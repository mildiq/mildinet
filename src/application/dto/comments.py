from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True, frozen=True, slots=True)
class Comment:
    id: int
    post_id: int
    author_id: int
    author_name: str
    content: str
    likes_count: int
    created_at: datetime