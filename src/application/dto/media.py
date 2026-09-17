from dataclasses import dataclass
from datetime import datetime
from application.common.media import MediaType


@dataclass(kw_only=True, frozen=True, slots=True)
class Media:
    id: int
    owner_id: int
    storage_key: str
    original_filename: str
    content_type: str
    media_type: MediaType
    size: int
    checksum: str
    created_at: datetime



@dataclass(frozen=True, slots=True)
class MediaPreview:
    id: int
    media_type: MediaType
    storage_key: str