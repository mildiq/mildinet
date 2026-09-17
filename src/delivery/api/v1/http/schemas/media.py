from datetime import datetime

from pydantic import BaseModel

from application.common.media import MediaType


class MediaRp(BaseModel):
    id: int
    media_type: MediaType
    content_type: str
    original_filename: str
    size: int
    created_at: datetime

class MediaPreviewRp(BaseModel):
    id: int
    media_type: MediaType
    url: str