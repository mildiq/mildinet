from dataclasses import dataclass
import hashlib
from pathlib import Path

from application.common.exceptions import MediaTooLargeError, UnsupportedMediaTypeError
from application.common.media import MediaType
from application.common.use_case import BaseUseCase
from application.interfaces.dm.media import IMediaDm
from application.interfaces.dm.stored_object import IStoredObjectDm
from application.interfaces.storage import IFileStorage
from application.interfaces.transaction import ITransactionManager
from bootstrap.settings import Settings
from application.dto.media import Media


@dataclass(kw_only=True, frozen=True, slots=True)
class UploadMediaCm:
    owner_id: int
    filename: str
    content_type: str
    data: bytes

@dataclass(kw_only=True, frozen=True, slots=True)
class UploadMediaRs:
    media: Media


@dataclass(kw_only=True, slots=True)
class UploadMediaUc(BaseUseCase[UploadMediaCm, UploadMediaRs]):
    _storage: IFileStorage
    _media: IMediaDm
    _transaction: ITransactionManager
    _settings: Settings
    _stored_object: IStoredObjectDm

    async def act(self, *, command: UploadMediaCm) -> UploadMediaRs:
        media_type = self._media_type(command.content_type)

        self._validate_size(media_type, len(command.data))

        checksum = hashlib.sha256(command.data).hexdigest()

        extension = Path(command.filename).suffix.lstrip(".")

        stored_object = await self._stored_object.get_by_checksum(
            checksum=checksum,
        )

        if stored_object is None:
            stored = await self._storage.upload(
                data=command.data,
                content_type=command.content_type,
                extension=extension,
            )

            stored_object = await self._stored_object.create(
                storage_key=stored.storage_key,
                checksum=checksum,
                size=stored.size,
                content_type=stored.content_type,
            )

        media = await self._media.create(
            owner_id=command.owner_id,
            stored_object_id=stored_object.id,
            original_filename=command.filename,
            media_type=media_type,
        )

        await self._transaction.commit()

        return UploadMediaRs(media=media)

    def _media_type(self, content_type: str) -> MediaType:
        if content_type.startswith("image/"):
            return MediaType.IMAGE

        if content_type.startswith("video/"):
            return MediaType.VIDEO

        if content_type.startswith("audio/"):
            return MediaType.AUDIO

        if content_type.startswith("document/"):
            return MediaType.DOCUMENT

        raise UnsupportedMediaTypeError()

    def _validate_size(self, media_type: MediaType, size: int) -> None:
        limits = {
            MediaType.IMAGE: self._settings.max_image_size_mb,
            MediaType.VIDEO: self._settings.max_video_size_mb,
            MediaType.AUDIO: self._settings.max_audio_size_mb,
            MediaType.DOCUMENT: self._settings.max_document_size_mb,
        }

        if size > limits[media_type] * 1024 * 1024:
            raise MediaTooLargeError()

