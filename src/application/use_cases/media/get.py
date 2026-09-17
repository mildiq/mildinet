from dataclasses import dataclass

from application.common.exceptions import MediaNotFoundError
from application.common.use_case import BaseUseCase
from application.dto.media import Media
from application.interfaces.dm.media import IMediaDm


@dataclass(kw_only=True, frozen=True, slots=True)
class GetMediaCm:
    media_id: int


@dataclass(kw_only=True, frozen=True, slots=True)
class GetMediaRs:
    media: Media


@dataclass(kw_only=True, slots=True)
class GetMediaUc(BaseUseCase[GetMediaCm, GetMediaRs]):
    _media: IMediaDm

    async def act(self, *, command: GetMediaCm) -> GetMediaRs:
        media = await self._media.get_by_id(
            media_id=command.media_id,
        )

        if media is None:
            raise MediaNotFoundError()

        return GetMediaRs(media=media)