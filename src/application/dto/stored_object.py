from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True, slots=True)
class StoredObject:
    id: int
    storage_key: str
    checksum: str
    size: int
    content_type: str