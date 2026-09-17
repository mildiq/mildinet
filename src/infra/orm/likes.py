from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.orm.common import Base, CreatedAtMixin

if TYPE_CHECKING:
    from infra.orm.posts import PostOrm
    from infra.orm.comments import CommentOrm
    from infra.orm.users import UserOrm


class PostLikeOrm(CreatedAtMixin, Base):
    __tablename__ = "post_likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["UserOrm"] = relationship(back_populates="post_likes")
    post: Mapped["PostOrm"] = relationship(back_populates="post_likes")


class CommentLikeOrm(CreatedAtMixin, Base):
    __tablename__ = "comments_likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["UserOrm"] = relationship(back_populates="comment_likes")
    comment: Mapped["CommentOrm"] = relationship(back_populates="comment_likes")

