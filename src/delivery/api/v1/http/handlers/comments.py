from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query, Response, status

from application.use_cases.comments import (
    CreateCommentCm,
    CreateCommentUc,
    DeleteCommentCm,
    DeleteCommentUc,
    ListCommentsCm,
    ListCommentsUc,
    ToggleCommentLikeCm,
    ToggleCommentLikeUc,
    UpdateCommentCm,
    UpdateCommentUc,
)
from delivery.api.v1.http.dependencies import CurrentUser
from delivery.api.v1.http.mappers.comments import map_comment_to_rp, map_comments_to_rp
from delivery.api.v1.http.schemas.errors import ErrorResponse
from delivery.api.v1.http.schemas.comments import (
    CreateCommentRq,
    CommentListRp,
    CommentRp,
    ToggleLikeRp,
    UpdateCommentRq,
)

router = APIRouter(prefix="/api/v1/comments", tags=["comments"])


@router.put(
    "/{comment_id}",
    response_model=CommentRp,
    description="Replace the content of an owned comment.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Only the post author can edit the comment.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Comment was not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Path or request data is invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
@inject
async def update_comment(
    *,
    comment_id: int,
    request: UpdateCommentRq,
    current_user: CurrentUser,
    use_case: FromDishka[UpdateCommentUc],
) -> CommentRp:
    result = await use_case.act(
        command=UpdateCommentCm(
            comment_id=comment_id,
            actor_id=current_user.id,
            content=request.content,
        ),
    )

    return map_comment_to_rp(comment=result.comment)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an owned post.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Only the post author can delete the post.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Post was not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Path parameter is invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
@inject
async def delete_comment(
    *,
    comment_id: int,
    current_user: CurrentUser,
    use_case: FromDishka[DeleteCommentUc],
) -> Response:
    await use_case.act(
        command=DeleteCommentCm(comment_id=comment_id, actor_id=current_user.id),
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{comment_id}/likes/toggle",
    response_model=ToggleLikeRp,
    description="Add or remove the authenticated user's like on a comment.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Comment was not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Path parameter is invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
@inject
async def toggle_comment_like(
    *,
    comment_id: int,
    current_user: CurrentUser,
    use_case: FromDishka[ToggleCommentLikeUc],
) -> ToggleLikeRp:
    result = await use_case.act(
        command=ToggleCommentLikeCm(comment_id=comment_id, user_id=current_user.id),
    )

    return ToggleLikeRp(liked=result.liked, likes_count=result.likes_count)
