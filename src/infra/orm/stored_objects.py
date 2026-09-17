from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from infra.orm import IntegerIdMixin
from infra.orm.common import Base


class StoredObjectOrm(IntegerIdMixin, Base):
    __tablename__ = "stored_objects"

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    size: Mapped[int] = mapped_column(nullable=False)

    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )