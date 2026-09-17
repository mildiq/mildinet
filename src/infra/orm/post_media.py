from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.orm.common import Base

if TYPE_CHECKING:
    from infra.orm.media import MediaOrm
    from infra.orm.posts import PostOrm


class PostMediaOrm(Base):
    __tablename__ = "post_media"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )

    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
        primary_key=True
    )

    position: Mapped[int] = mapped_column(default=0)

    post: Mapped["PostOrm"] = relationship(back_populates="media")

    media: Mapped["MediaOrm"] = relationship()