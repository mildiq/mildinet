from dataclasses import dataclass
from typing import Protocol
from collections.abc import AsyncIterator


@dataclass(frozen=True, slots=True)
class StoredFile:
    storage_key: str
    content_type: str
    size: int


class IFileStorage(Protocol):
    async def upload(
        self,
        *,
        data: bytes,
        content_type: str,
        extension: str,
    ) -> StoredFile: ...

    async def download(
        self,
        *,
        storage_key: str,
    ) -> AsyncIterator[bytes]: ...

    async def delete(
        self,
        *,
        storage_key: str,
    ) -> None: ...