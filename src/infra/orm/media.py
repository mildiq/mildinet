from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM

from application.common.media import MediaType
from infra.orm.common import Base, CreatedAtMixin, IntegerIdMixin


if TYPE_CHECKING:
    from infra.orm.stored_objects import StoredObjectOrm

media_type_enum = ENUM(
    MediaType,
    name='mediatype',
    create_type=True,
)

class MediaOrm(IntegerIdMixin, Base, CreatedAtMixin):
    __tablename__ = 'media'

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)

    stored_object_id: Mapped[int] = mapped_column(ForeignKey('stored_objects.id', ondelete='RESTRICT'), index=False)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)

    media_type: Mapped[MediaType] = mapped_column(media_type_enum, nullable=False)

    stored_object: Mapped["StoredObjectOrm"] = relationship()