from typing import Protocol

from application.dto.stored_object import StoredObject


class IStoredObjectDm(Protocol):
    async def get_by_checksum(
        self,
        *,
        checksum: str
    ) -> StoredObject | None:
        ...

    async def create(
        self,
        *,
        storage_key: str,
        checksum: str,
        size: int,
        content_type: str,
    ) -> StoredObject:
        ...

    async def delete(
        self,
        *,
        stored_object_id: int,
    ) -> None:
        ...
