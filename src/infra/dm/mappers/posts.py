from application.dto.media import MediaPreview
from application.dto.posts import Post
from infra.orm.posts import PostOrm


def map_post(
        *,
        orm: PostOrm,
        author_name: str,
        likes_count: int,
        media: tuple[MediaPreview, ...] = (),
) -> Post:
    return Post(
        id=orm.id,
        author_id=orm.author_id,
        author_name=author_name,
        content=orm.content,
        created_at=orm.created_at,
        likes_count=likes_count,
        media=media,
    )