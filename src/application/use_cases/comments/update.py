from dataclasses import dataclass, replace

from application.common.exceptions import CommentNotFoundError, CommentOwnershipError
from application.common.use_case import BaseUseCase
from application.dto.comments import Comment
from application.interfaces.dm.comments import ICommentDm
from application.interfaces.transaction import ITransactionManager


@dataclass(kw_only=True, frozen=True, slots=True)
class UpdateCommentCm:
    comment_id: int
    actor_id: int
    content: str


@dataclass(kw_only=True, frozen=True, slots=True)
class UpdateCommentRs:
    comment: Comment


@dataclass(kw_only=True, slots=True)
class UpdateCommentUc(BaseUseCase[UpdateCommentCm, UpdateCommentRs]):
    """Edit an owned comment.

    Pipeline:
    1. Load the comment and verify ownership.
    2. Persist normalized replacement content.
    3. Commit and return the updated comment.

    Edge cases:
    - Missing comments and edits by non-owners are distinct failures.
    """

    _comments: ICommentDm
    _transaction: ITransactionManager

    async def act(self, *, command: UpdateCommentCm) -> UpdateCommentRs:
        comment = await self._get_owned_comment(
            comment_id=command.comment_id,
            actor_id=command.actor_id,
        )

        updated = await self._comments.save(
            comment=replace(comment, content=command.content.strip()),
        )
        await self._transaction.commit()

        return UpdateCommentRs(comment=updated)

    async def _get_owned_comment(self, *, comment_id: int, actor_id: int) -> Comment:
        comment = await self._comments.get_by_id(comment_id=comment_id, for_update=True)
        if comment is None:
            raise CommentNotFoundError()
        if comment.author_id != actor_id:
            raise CommentOwnershipError(action="edit")

        return comment
