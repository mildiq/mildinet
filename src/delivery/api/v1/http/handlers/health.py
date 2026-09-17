from fastapi import APIRouter, status

from delivery.api.v1.http.schemas.errors import ErrorResponse

router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get(
    "/health",
    description="Check whether the API is running",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal Server Error.",
        },
    },
)
async def health() -> dict[str, str]:
    return {"status": "ok"}