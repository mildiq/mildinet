from dataclasses import dataclass
from collections import defaultdict

from sqlalchemy import Select, func, select

from application.dto.posts import Post
from application.dto.media import MediaPreview
from application.interfaces.dm.posts import IPostDm
from infra.common.transaction import TransactionManager
from infra.dm.exceptions import SerializationError
from infra.dm.mappers.posts import map_post
from infra.orm import StoredObjectOrm
from infra.orm.likes import PostLikeOrm
from infra.orm.posts import PostOrm
from infra.orm.users import UserOrm
from infra.orm.media import MediaOrm
from infra.orm.post_media import PostMediaOrm


def _post_query() -> Select[tuple[PostOrm, str, int]]:
    return (
        select(
            PostOrm,
            UserOrm.name,
            func.count(PostLikeOrm.user_id),
        )
        .join(UserOrm, UserOrm.id == PostOrm.author_id)
        .outerjoin(
            PostLikeOrm,
            PostLikeOrm.post_id == PostOrm.id
        )
        .group_by(
            PostOrm.id,
            UserOrm.name,
        )
    )


@dataclass(kw_only=True, slots=True)
class PostDm(IPostDm):
    _tm: TransactionManager

    async def get_by_id(
            self,
            *,
            post_id: int,
            for_update: bool = False,
    ) -> Post | None:
        if for_update:
            lock = (
                select(PostOrm.id)
                .where(PostOrm.id == post_id)
                .with_for_update()
            )

            if await self._tm.scalar(statement=lock) is None:
                return None

        row = (
            await self._tm.execute(
                statement=_post_query().where(
                    PostOrm.id == post_id
                ),
            )
        ).one_or_none()

        if row is None:
            return None

        orm, author_name, likes_count = row

        media_by_post = await self._load_media(
            post_ids=(post_id,),
        )

        return map_post(
            orm=orm,
            author_name=author_name,
            likes_count=likes_count,
            media=media_by_post.get(post_id, ()),
        )

    async def list(
            self,
            *,
            author_id: int | None = None,
            content_query: str | None = None,
            limit: int = 50,
            offset: int = 0,
    ) -> tuple[Post, ...]:
        query = _post_query()

        if author_id is not None:
            query = query.where(
                PostOrm.author_id == author_id
            )

        if content_query is not None:
            escaped = (
                content_query
                .replace("%", "\\%")
                .replace("_", "\\_")
            )

            query = query.where(
                PostOrm.content.ilike(
                    f"%{escaped}%",
                    escape="\\",
                )
            )

        query = (
            query
            .order_by(
                PostOrm.created_at.desc(),
                PostOrm.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        rows = (await self._tm.execute(statement=query)).all()

        if not rows:
            return ()

        post_ids = tuple(
            orm.id
            for orm, _, _ in rows
        )

        media_by_post = await self._load_media(
            post_ids=post_ids,
        )

        return tuple(
            map_post(
                orm=orm,
                author_name=author_name,
                likes_count=likes_count,
                media=media_by_post.get(orm.id, ()),
            )
            for orm, author_name, likes_count in rows
        )

    async def create(self, *, author_id: int, content: str) -> Post:
        orm = PostOrm(author_id=author_id, content=content)

        self._tm.add(instance=orm)
        await self._tm.flush(instances=[orm])

        return await self._reload(post_id=orm.id, operation="create")

    async def save(self, *, post: Post) -> Post:
        orm = await self._tm.get(entity=PostOrm, identifier=post.id)
        if orm is None:
            raise SerializationError(
                entity="post",
                identifier=post.id,
                operation="save",
            )

        orm.content = post.content
        await self._tm.flush(instances=[orm])

        return await self._reload(post_id=orm.id, operation="save")

    async def attach_media(
        self,
        *,
        post_id: int,
        media_ids: tuple[int, ...],
    ) -> None:
        attachments = [
            PostMediaOrm(
                post_id=post_id,
                media_id=media_id,
                position=index,
            )
            for index, media_id in enumerate(media_ids)
        ]

        for attachment in attachments:
            self._tm.add(instance=attachment)

        await self._tm.flush()

    async def delete(self, *, post_id: int) -> None:
        orm = await self._tm.get(entity=PostOrm, identifier=post_id)
        if orm is None:
            return

        await self._tm.delete(instance=orm)
        await self._tm.flush()

    async def _reload(self, *, post_id: int, operation: str) -> Post:
        post = await self.get_by_id(post_id=post_id)
        if post is not None:
            return post

        raise SerializationError(
            entity="post",
            identifier=post_id,
            operation=operation,
        )

    async def _load_media(
            self,
            *,
            post_ids: tuple[int, ...],
    ) -> dict[int, tuple[MediaPreview, ...]]:
        if not post_ids:
            return {}

        statement = (
            select(
                PostMediaOrm.post_id,
                MediaOrm.id,
                MediaOrm.media_type,
                StoredObjectOrm.storage_key,
                PostMediaOrm.position,
            )
            .join(
                MediaOrm,
                MediaOrm.id == PostMediaOrm.media_id,
            )
            .join(
                StoredObjectOrm,
                StoredObjectOrm.id == MediaOrm.stored_object_id,
            )
            .where(PostMediaOrm.post_id.in_(post_ids))
            .order_by(
                PostMediaOrm.post_id,
                PostMediaOrm.position,
            )
        )

        rows = (await self._tm.execute(statement=statement)).all()

        result: dict[int, list[MediaPreview]] = defaultdict(list)

        for (
                post_id,
                media_id,
                media_type,
                storage_key,
                position,
        ) in rows:
            result[post_id].append(
                MediaPreview(
                    id=media_id,
                    media_type=media_type,
                    storage_key=storage_key,
                )
            )

        return {
            post_id: tuple(items)
            for post_id, items in result.items()
        }