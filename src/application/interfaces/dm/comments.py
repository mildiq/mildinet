from typing import Protocol

from application.dto.comments import Comment


class ICommentDm(Protocol):
    async def get_by_id(
        self,
        *,
        comment_id: int,
        for_update: bool = False,
    ) -> Comment | None: ...

    async def list(
        self,
        *,
        post_id: int,
        limit: int = 3,
        offset: int = 0,
    ) -> tuple[Comment, ...]: ...

    async def create(self, *, post_id: int, author_id: int, content: str) -> Comment: ...

    async def save(self, *, comment: Comment) -> Comment: ...

    async def delete(self, *, comment_id: int) -> None: ...