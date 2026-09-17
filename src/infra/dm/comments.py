from dataclasses import dataclass

from sqlalchemy import Select, func, select

from application.dto.comments import Comment
from application.interfaces.dm.comments import ICommentDm
from infra.common.transaction import TransactionManager
from infra.dm.exceptions import SerializationError
from infra.dm.mappers.comments import map_comment
from infra.orm.likes import CommentLikeOrm
from infra.orm.comments import CommentOrm
from infra.orm.users import UserOrm


def _comment_query() -> Select[tuple[CommentOrm, str, int]]:
    return (
        select(CommentOrm, UserOrm.name, func.count(CommentLikeOrm.user_id))
        .join(UserOrm, UserOrm.id == CommentOrm.author_id)
        .outerjoin(CommentLikeOrm, CommentLikeOrm.comment_id == CommentOrm.id)
        .group_by(CommentOrm.id, UserOrm.name)
    )


@dataclass(kw_only=True, slots=True)
class CommentDm(ICommentDm):
    _tm: TransactionManager

    async def get_by_id(
        self,
        *,
        comment_id: int,
        for_update: bool = False,
    ) -> Comment | None:
        if for_update:
            lock = select(CommentOrm.id).where(CommentOrm.id == comment_id).with_for_update()
            if await self._tm.scalar(statement=lock) is None:
                return None

        row = (
            await self._tm.execute(
                statement=_comment_query().where(CommentOrm.id == comment_id),
            )
        ).one_or_none()
        if row is None:
            return None

        return map_comment(
            orm=row[0],
            author_name=row[1],
            likes_count=row[2],
        )

    async def list(
        self,
        *,
        post_id: int,
        limit: int = 3,
        offset: int = 0,
    ) -> tuple[Comment, ...]:
        query = _comment_query()
        if post_id is not None:
            query = query.where(CommentOrm.post_id == post_id)
        # if content_query is not None:
        #     escaped = content_query.replace("%", "\\%").replace("_", "\\_")
        #     query = query.where(CommentOrm.content.ilike(f"%{escaped}%", escape="\\"))

        rows = (
            await self._tm.execute(
                statement=query.order_by(CommentOrm.created_at.asc(), CommentOrm.id.asc())
                .limit(limit)
                .offset(offset),
            )
        ).all()
        return tuple(
            map_comment(
                orm=orm,
                author_name=author_name,
                likes_count=likes_count,
            )
            for orm, author_name, likes_count in rows
        )

    async def create(self, *, post_id: int, author_id: int, content: str) -> Comment:
        orm = CommentOrm(post_id=post_id, author_id=author_id, content=content)

        self._tm.add(instance=orm)
        await self._tm.flush(instances=[orm])

        return await self._reload(comment_id=orm.id, operation="create")

    async def save(self, *, comment: Comment) -> Comment:
        orm = await self._tm.get(entity=CommentOrm, identifier=comment.id)
        if orm is None:
            raise SerializationError(
                entity="comment",
                identifier=comment.id,
                operation="save",
            )

        orm.content = comment.content
        await self._tm.flush(instances=[orm])

        return await self._reload(comment_id=orm.id, operation="save")

    async def delete(self, *, comment_id: int) -> None:
        orm = await self._tm.get(entity=CommentOrm, identifier=comment_id)
        if orm is None:
            return

        await self._tm.delete(instance=orm)
        await self._tm.flush()

    async def _reload(self, *, comment_id: int, operation: str) -> Comment:
        comment = await self.get_by_id(comment_id=comment_id)
        if comment is not None:
            return comment

        raise SerializationError(
            entity="comment",
            identifier=comment_id,
            operation=operation,
        )
