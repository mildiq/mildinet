from collections.abc import Sequence
from typing import Protocol

from application.dto.media import Media
from application.common.media import MediaType


class IMediaDm(Protocol):
    async def create(
        self,
        *,
        owner_id: int,
        stored_object_id: int,
        original_filename: str,
        media_type: MediaType,
    ) -> Media: ...

    async def list(
        self,
        *,
        owner_id: int | None = None,
        media_ids: Sequence[int] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Media, ...]: ...

    async def list_by_owner(
        self,
        *,
        owner_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Media, ...]: ...

    async def get_by_id(
        self,
        *,
        media_id: int,
        for_update: bool = False,
    ) -> Media | None: ...

    async def count_by_stored_object(
        self,
        *,
        stored_object_id: int,
    ) -> int:
        ...

    async def delete(
        self,
        *,
        media_id: int,
    ) -> None: ...
