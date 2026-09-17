from application.dto.media import Media
from infra.orm.media import MediaOrm


def map_media(*, orm: MediaOrm) -> Media:
    return Media(
        id=orm.id,
        owner_id=orm.owner_id,
        storage_key=orm.stored_object.storage_key,
        original_filename=orm.original_filename,
        content_type=orm.stored_object.content_type,
        media_type=orm.media_type,
        size=orm.stored_object.size,
        checksum=orm.stored_object.checksum,
        created_at=orm.created_at,
    )