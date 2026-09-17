from dataclasses import dataclass

from application.common.exceptions import CommentNotFoundError, CommentOwnershipError
from application.common.use_case import BaseUseCase
from application.dto.comments import Comment
from application.interfaces.dm.comments import ICommentDm
from application.interfaces.transaction import ITransactionManager


@dataclass(kw_only=True, frozen=True, slots=True)
class DeleteCommentCm:
    comment_id: int
    actor_id: int


@dataclass(kw_only=True, frozen=True, slots=True)
class DeleteCommentRs:
    deleted: bool


@dataclass(kw_only=True, slots=True)
class DeleteCommentUc(BaseUseCase[DeleteCommentCm, DeleteCommentRs]):
    """Delete an owned comment and its likes.

    Pipeline:
    1. Load the comment and verify ownership.
    2. Delete it through the data mapper.
    3. Commit and report success.

    Edge cases:
    - Missing comments and deletes by non-owners are distinct failures.
    """

    _comments: ICommentDm
    _transaction: ITransactionManager

    async def act(self, *, command: DeleteCommentCm) -> DeleteCommentRs:
        comment = await self._get_owned_comment(
            comment_id=command.comment_id,
            actor_id=command.actor_id,
        )

        await self._comments.delete(comment_id=comment.id)
        await self._transaction.commit()

        return DeleteCommentRs(deleted=True)

    async def _get_owned_comment(self, *, comment_id: int, actor_id: int) -> Comment:
        comment = await self._comments.get_by_id(comment_id=comment_id, for_update=True)
        if comment is None:
            raise CommentNotFoundError()
        if comment.author_id != actor_id:
            raise CommentOwnershipError(action="delete")

        return comment
