from dataclasses import dataclass

from sqlalchemy import select

from application.dto.stored_object import StoredObject
from application.interfaces.dm.stored_object import IStoredObjectDm
from infra.common.transaction import TransactionManager
from infra.dm.mappers.stored_object import map_stored_object
from infra.orm import StoredObjectOrm

@dataclass(kw_only=True, slots=True)
class StoredObjectDm(IStoredObjectDm):
    _tm: TransactionManager


    async def get_by_checksum(
        self,
        *,
        checksum: str,
    ) -> StoredObject | None:
        query = select(StoredObjectOrm).where(
            StoredObjectOrm.checksum == checksum,
        )

        result = await self._tm.execute(
            statement=query,
        )
        orm = result.scalar_one_or_none()

        return None if orm is None else map_stored_object(orm=orm)

    async def create(
        self,
        *,
        storage_key: str,
        checksum: str,
        size: int,
        content_type: str,
    ) -> StoredObject:
        orm = StoredObjectOrm(
            storage_key=storage_key,
            checksum=checksum,
            size=size,
            content_type=content_type,
        )

        self._tm.add(instance=orm)
        await self._tm.flush(instances=[orm])
        await self._tm.refresh(instance=orm)

        return map_stored_object(orm=orm)

    async def delete(
            self,
            *,
            stored_object_id: int,
    ) -> None:
        orm = await self._tm.get(
            entity=StoredObject,
            identifier=stored_object_id,
        )

        if orm is None:
            return

        await self._tm.delete(instance=orm)
        await self._tm.flush()