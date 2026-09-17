from dataclasses import dataclass

from application.common.exceptions import CommentNotFoundError
from application.common.use_case import BaseUseCase
from application.dto.comments import Comment
from application.interfaces.dm.likes import ICommentLikeDm
from application.interfaces.dm.comments import ICommentDm
from application.interfaces.transaction import ITransactionManager


@dataclass(kw_only=True, frozen=True, slots=True)
class ToggleCommentLikeCm:
    comment_id: int
    user_id: int


@dataclass(kw_only=True, frozen=True, slots=True)
class ToggleCommentLikeRs:
    liked: bool
    likes_count: int


@dataclass(kw_only=True, slots=True)
class ToggleCommentLikeUc(BaseUseCase[ToggleCommentLikeCm, ToggleCommentLikeRs]):
    """Toggle a unique like without a denormalized counter.

    Pipeline:
    1. Verify the comment exists and load the caller's like.
    2. Create or delete the unique like row.
    3. Commit, derive the new count, and return state.
    """

    _comments: ICommentDm
    _likes: ICommentLikeDm
    _transaction: ITransactionManager

    async def act(self, *, command: ToggleCommentLikeCm) -> ToggleCommentLikeRs:
        liked = await self._toggle(
            user_id=command.user_id,
            comment_id=command.comment_id,
        )

        await self._transaction.commit()

        comment = await self._require_comment(comment_id=command.comment_id)

        return ToggleCommentLikeRs(liked=liked, likes_count=comment.likes_count)

    async def _toggle(self, *, user_id: int, comment_id: int) -> bool:
        if not await self._likes.lock_comment(comment_id=comment_id):
            raise CommentNotFoundError()

        was_liked = await self._likes.exists(user_id=user_id, comment_id=comment_id)

        if was_liked:
            await self._likes.delete(user_id=user_id, comment_id=comment_id)
        else:
            await self._likes.create(user_id=user_id, comment_id=comment_id)

        return not was_liked

    async def _require_comment(self, *, comment_id: int) -> Comment:
        comment = await self._comments.get_by_id(comment_id=comment_id)
        if comment is None:
            raise CommentNotFoundError()

        return comment
