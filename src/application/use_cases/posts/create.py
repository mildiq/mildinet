from dataclasses import dataclass, field

from application.common.exceptions import MediaNotFoundError, MediaOwnershipError, EmptyPostError
from application.common.use_case import BaseUseCase
from application.dto.posts import Post
from application.interfaces.dm.media import IMediaDm
from application.interfaces.dm.posts import IPostDm
from application.interfaces.transaction import ITransactionManager
from infra.dm.exceptions import SerializationError


@dataclass(kw_only=True, frozen=True, slots=True)
class CreatePostCm:
    author_id: int
    content: str
    media_ids: tuple[int, ...] = field(default_factory=tuple)


@dataclass(kw_only=True, frozen=True, slots=True)
class CreatePostRs:
    post: Post


@dataclass(kw_only=True, slots=True)
class CreatePostUc(BaseUseCase[CreatePostCm, CreatePostRs]):
    """Create a post owned by the authenticated user.

    Pipeline:
    1. Normalize content.
    2. Persist the post.
    3. Commit and return it.

    Edge cases:
    - Transport validation guarantees non-empty bounded content.
    """

    _posts: IPostDm
    _media: IMediaDm
    _transaction: ITransactionManager

    async def act(self, *, command: CreatePostCm) -> CreatePostRs:
        # Normalize and persist content under the authenticated author.

        if not command.content.strip() and not command.media_ids:
            raise EmptyPostError()

        await self._check_media(
            media_ids=command.media_ids,
            user_id=command.author_id,
        )

        post = await self._posts.create(
            author_id=command.author_id,
            content=command.content.strip(),
        )

        post_id = post.id

        await self._posts.attach_media(
            post_id=post.id,
            media_ids=command.media_ids,
        )

        post = await self._posts.get_by_id(
            post_id=post_id,
        )

        if post is None:
            raise SerializationError(
                entity="post",
                identifier=post_id,
                operation="create",
            )

        # Return the post only after it becomes durable.
        await self._transaction.commit()
        return CreatePostRs(post=post)


    async def _check_media(
        self,
        *,
        media_ids: tuple[int, ...],
        user_id: int
    ) -> None:
        if not media_ids:
            return

        media = await self._media.list(media_ids=media_ids)

        media_by_id = {item.id: item for item in media}

        for media_id in media_ids:
            item = media_by_id.get(media_id)

            if item is None:
                raise MediaNotFoundError()

            if item.owner_id != user_id:
                raise MediaOwnershipError()
