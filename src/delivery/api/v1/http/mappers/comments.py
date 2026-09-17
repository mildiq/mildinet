from application.dto.comments import Comment
from delivery.api.v1.http.schemas.comments import CommentListRp, CommentRp


def map_comment_to_rp(*, comment: Comment) -> CommentRp:
    return CommentRp(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_name=comment.author_name,
        content=comment.content,
        likes_count=comment.likes_count,
        created_at=comment.created_at,
    )


def map_comments_to_rp(*, comments: tuple[Comment, ...]) -> CommentListRp:
    return CommentListRp(items=[map_comment_to_rp(comment=comment) for comment in comments])
