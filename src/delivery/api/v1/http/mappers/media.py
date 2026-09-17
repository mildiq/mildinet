from application.dto.media import Media, MediaPreview
from delivery.api.v1.http.schemas.media import MediaRp, MediaPreviewRp


def map_media_to_rp(*, media: Media) -> MediaRp:
    return MediaRp(
        id=media.id,
        media_type=media.media_type,
        content_type=media.content_type,
        original_filename=media.original_filename,
        size=media.size,
        created_at=media.created_at,
    )

def map_media_preview_to_rp(*, media: MediaPreview) -> MediaPreviewRp:
    return MediaPreviewRp(
        id=media.id,
        media_type=media.media_type,
        url=f"/api/v1/media/{media.id}",
    )