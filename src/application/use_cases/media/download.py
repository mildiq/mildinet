from dataclasses import dataclass
from collections.abc import AsyncIterator

from application.common.exceptions import MediaNotFoundError
from application.common.use_case import BaseUseCase
from application.interfaces.dm.media import IMediaDm
from application.interfaces.storage import IFileStorage


@dataclass(kw_only=True, frozen=True, slots=True)
class DownloadMediaCm:
    media_id: int


@dataclass(kw_only=True, frozen=True, slots=True)
class DownloadMediaRs:
    content: AsyncIterator[bytes]
    content_type: str
    filename: str
    size: int


@dataclass(kw_only=True, slots=True)
class DownloadMediaUc(
    BaseUseCase[DownloadMediaCm, DownloadMediaRs]
):
    _media: IMediaDm
    _storage: IFileStorage

    async def act(
        self,
        *,
        command: DownloadMediaCm,
    ) -> DownloadMediaRs:
        media = await self._media.get_by_id(
            media_id=command.media_id,
        )

        if media is None:
            raise MediaNotFoundError()

        content = self._storage.download(
            storage_key=media.storage_key,
        )

        return DownloadMediaRs(
            content=content,
            content_type=media.content_type,
            filename=media.original_filename,
            size=media.size,
        )