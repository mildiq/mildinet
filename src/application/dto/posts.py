from dataclasses import dataclass, field
from datetime import datetime

from application.dto.media import MediaPreview


@dataclass
class Post:
    id: int
    author_id: int
    author_name: str
    content: str
    likes_count: int
    created_at: datetime
    media: tuple[MediaPreview, ...] = field(default_factory=tuple)