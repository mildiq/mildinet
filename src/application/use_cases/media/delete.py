from dataclasses import dataclass

from application.common.exceptions import MediaNotFoundError, MediaOwnershipError, StoredObjectNotFoundError
from application.common.use_case import BaseUseCase
from application.dto.media import Media
from application.interfaces.dm.media import IMediaDm
from application.interfaces.dm.stored_object import IStoredObjectDm
from application.interfaces.storage import IFileStorage
from application.interfaces.transaction import ITransactionManager


@dataclass(kw_only=True, frozen=True, slots=True)
class DeleteMediaCm:
    media_id: int
    actor_id: int


@dataclass(kw_only=True, frozen=True, slots=True)
class DeleteMediaRs:
    deleted: bool


@dataclass(kw_only=True, slots=True)
class DeleteMediaUc(BaseUseCase[DeleteMediaCm, DeleteMediaRs]):
    _media: IMediaDm
    _stored_object: IStoredObjectDm
    _storage: IFileStorage
    _transaction: ITransactionManager

    async def act(self, *, command: DeleteMediaCm) -> DeleteMediaRs:
        media = await self._get_owned_media(
            media_id=command.media_id,
            actor_id=command.actor_id,
        )

        stored_object = await self._stored_object.get_by_checksum(
            checksum=media.checksum,
        )

        if stored_object is None:
            raise StoredObjectNotFoundError()

        references_count = await self._media.count_by_stored_object(
            stored_object_id=stored_object.id,
        )

        await self._media.delete(
            media_id=media.id,
        )

        if references_count == 1:
            await self._storage.delete(
                storage_key=stored_object.storage_key,
            )

            await self._stored_object.delete(
                stored_object_id=stored_object.id,
            )

        await self._transaction.commit()

        return DeleteMediaRs(deleted=True)

    async def _get_owned_media(
        self,
        *,
        media_id: int,
        actor_id: int,
    ) -> Media:
        media = await self._media.get_by_id(
            media_id=media_id,
            for_update=True,
        )

        if media is None:
            raise MediaNotFoundError()

        if media.owner_id != actor_id:
            raise MediaOwnershipError()

        return media