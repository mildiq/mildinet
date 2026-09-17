from dataclasses import dataclass

from application.common.use_case import BaseUseCase
from application.dto.media import Media
from application.interfaces.dm.media import IMediaDm


@dataclass(kw_only=True, frozen=True, slots=True)
class ListMediaCm:
    owner_id: int
    limit: int = 50
    offset: int = 0


@dataclass(kw_only=True, frozen=True, slots=True)
class ListMediaRs:
    media: tuple[Media, ...]


@dataclass(kw_only=True, slots=True)
class ListMediaUc(BaseUseCase[ListMediaCm, ListMediaRs]):
    """List media files owned by the current user."""

    _media: IMediaDm

    async def act(self, *, command: ListMediaCm) -> ListMediaRs:
        media = await self._media.list_by_owner(
            owner_id=command.owner_id,
            limit=min(max(command.limit, 1), 100),
            offset=max(command.offset, 0),
        )

        return ListMediaRs(media=media)