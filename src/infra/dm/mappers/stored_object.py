from application.dto.stored_object import StoredObject
from infra.orm.stored_objects import StoredObjectOrm


def map_stored_object(*, orm: StoredObjectOrm) -> StoredObject:
    return StoredObject(
        id=orm.id,
        storage_key=orm.storage_key,
        checksum=orm.checksum,
        size=orm.size,
        content_type=orm.content_type,
    )