from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateCommentRq(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(min_length=1, max_length=1000)


class UpdateCommentRq(CreateCommentRq):
    pass


class CommentRp(BaseModel):
    id: int
    post_id: int
    author_id: int
    author_name: str
    content: str
    likes_count: int
    created_at: datetime


class CommentListRp(BaseModel):
    items: list[CommentRp]


class ToggleLikeRp(BaseModel):
    liked: bool
    likes_count: int