from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.orm.common import Base, CreatedAtMixin, IntegerIdMixin
from infra.orm.comments import CommentOrm

if TYPE_CHECKING:
    from infra.orm.likes import PostLikeOrm
    from infra.orm.users import UserOrm
    from infra.orm.post_media import PostMediaOrm


class PostOrm(IntegerIdMixin, CreatedAtMixin, Base):
    __tablename__ = "posts"
    _created_at_index = True

    author: Mapped["UserOrm"] = relationship(back_populates="posts")
    post_likes: Mapped[list["PostLikeOrm"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    content: Mapped[str] = mapped_column(
        String(5000),
        nullable=False,
        server_default="",
    )

    comments: Mapped[list["CommentOrm"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,

    )

    media: Mapped[list["PostMediaOrm"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )