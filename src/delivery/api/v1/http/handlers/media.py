from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, File, UploadFile, status, Response
from fastapi.responses import StreamingResponse
from urllib.parse import quote

from application.use_cases.media import DownloadMediaUc, DownloadMediaCm, DeleteMediaUc, DeleteMediaCm
from application.use_cases.media.list import ListMediaUc, ListMediaCm
from application.use_cases.media.upload import UploadMediaCm, UploadMediaUc
from delivery.api.v1.http.dependencies.auth import CurrentUser
from delivery.api.v1.http.mappers.media import map_media_to_rp
from delivery.api.v1.http.schemas.errors import ErrorResponse
from delivery.api.v1.http.schemas.media import MediaRp


router = APIRouter(
    prefix="/api/v1/media",
    tags=["media"],
)


@router.post(
    "",
    response_model=MediaRp,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def media_upload(
    *,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    use_case: FromDishka[UploadMediaUc],
) -> MediaRp:
    data = await file.read()

    result = await use_case.act(
        command=UploadMediaCm(
            owner_id=current_user.id,
            filename=file.filename or "file",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )
    )

    return map_media_to_rp(media=result.media)


@router.get(
    "/{media_id}",
)
@inject
async def media_download(
    *,
    media_id: int,
    use_case: FromDishka[DownloadMediaUc],
) -> StreamingResponse:
    result = await use_case.act(
        command=DownloadMediaCm(
            media_id=media_id,
        )
    )

    filename = quote(result.filename)

    return StreamingResponse(
        result.content,
        media_type=result.content_type,
        headers={
            "Content-Disposition":  f"inline; filename*=UTF-8''{filename}",
        },
    )

@router.get(
    "",
    response_model=list[MediaRp],
)
@inject
async def media_list(
    *,
    current_user: CurrentUser,
    use_case: FromDishka[ListMediaUc],
) -> list[MediaRp]:
    result = await use_case.act(
        command=ListMediaCm(
            owner_id=current_user.id,
        ),
    )

    return [
        map_media_to_rp(media=media)
        for media in result.media
    ]

@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an owned media file.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "The authenticated user does not own this media.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Media was not found.",
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
async def delete_media(
    *,
    media_id: int,
    current_user: CurrentUser,
    use_case: FromDishka[DeleteMediaUc],
) -> Response:
    await use_case.act(
        command=DeleteMediaCm(
            media_id=media_id,
            actor_id=current_user.id,
        ),
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)