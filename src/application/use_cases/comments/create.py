from dataclasses import dataclass

from application.common.use_case import BaseUseCase
from application.dto.comments import Comment
from application.interfaces.dm.comments import ICommentDm
from application.interfaces.transaction import ITransactionManager


@dataclass(kw_only=True, frozen=True, slots=True)
class CreateCommentCm:
    post_id: int
    author_id: int
    content: str


@dataclass(kw_only=True, frozen=True, slots=True)
class CreateCommentRs:
    comment: Comment


@dataclass(kw_only=True, slots=True)
class CreateCommentUc(BaseUseCase[CreateCommentCm, CreateCommentRs]):
    """Create a comment owned by the authenticated user.

    Pipeline:
    1. Normalize content.
    2. Persist the comment.
    3. Commit and return it.

    Edge cases:
    - Transport validation guarantees non-empty bounded content.
    """

    _comments: ICommentDm
    _transaction: ITransactionManager

    async def act(self, *, command: CreateCommentCm) -> CreateCommentRs:
        # Normalize and persist content under the authenticated author.
        comment = await self._comments.create(
            post_id=command.post_id,
            author_id=command.author_id,
            content=command.content.strip(),
        )

        # Return the comment only after it becomes durable.
        await self._transaction.commit()
        return CreateCommentRs(comment=comment)
