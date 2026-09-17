from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.orm.common import Base, CreatedAtMixin, IntegerIdMixin

if TYPE_CHECKING:
    from infra.orm.likes import CommentLikeOrm
    from infra.orm.users import UserOrm
    from infra.orm.posts import PostOrm

class CommentOrm(IntegerIdMixin, CreatedAtMixin, Base):
    __tablename__ = "comments"
    _created_at_index = True
    __table_args__ = (
        CheckConstraint("length(content) BETWEEN 1 AND 1000", name="content_len"),
    )
    post: Mapped["PostOrm"] = relationship(back_populates="comments")

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
    index=True,
    )

    author: Mapped["UserOrm"] = relationship(back_populates="comments")

    comment_likes: Mapped[list["CommentLikeOrm"]] = relationship(
        back_populates="comment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    content: Mapped[str] = mapped_column(String(1000))
