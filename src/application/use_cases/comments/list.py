from dataclasses import dataclass

from application.common.use_case import BaseUseCase
from application.dto.comments import Comment
from application.interfaces.dm.comments import ICommentDm


@dataclass(kw_only=True, frozen=True, slots=True)
class ListCommentsCm:
    post_id: int
    limit: int = 50
    offset: int = 0


@dataclass(kw_only=True, frozen=True, slots=True)
class ListCommentsRs:
    comments: tuple[Comment, ...]


@dataclass(kw_only=True, slots=True)
class ListCommentsUc(BaseUseCase[ListCommentsCm, ListCommentsRs]):
    """List of the comments.

    Pipeline:
    1. ---.
    2. ---.
    3. Return comments or an empty result.
    """

    _comments: ICommentDm

    async def act(self, *, command: ListCommentsCm) -> ListCommentsRs:
        # Keep pagination bounded before delegating the read projection.
        comments = await self._comments.list(
            post_id=command.post_id,
            limit=min(max(command.limit, 1), 100),
            offset=max(command.offset, 0),
        )
        return ListCommentsRs(comments=comments)
