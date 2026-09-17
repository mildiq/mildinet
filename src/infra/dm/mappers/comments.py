from application.dto.comments import Comment
from infra.common.datetime import as_utc
from infra.orm.comments import CommentOrm


def map_comment(*, orm: CommentOrm, author_name: str, likes_count: int) -> Comment:
    return Comment(
        id=orm.id,
        post_id=orm.post_id,
        author_id=orm.author_id,
        author_name=author_name,
        content=orm.content,
        likes_count=likes_count,
        created_at=as_utc(value=orm.created_at),
    )
