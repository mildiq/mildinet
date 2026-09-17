from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from delivery.api.v1.http.schemas.media import MediaPreviewRp


class CreatePostRq(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(default='', max_length=5000)
    media_ids: list[int] = Field(default_factory=list)


class UpdatePostRq(CreatePostRq):
    pass


class PostRp(BaseModel):
    id: int
    author_id: int
    author_name: str
    content: str
    likes_count: int
    created_at: datetime
    media: list[MediaPreviewRp]

class PostListRp(BaseModel):
    items: list[PostRp]


class ToggleLikeRp(BaseModel):
    liked: bool
    likes_count: int
