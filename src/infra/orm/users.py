from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.orm.common import Base, CreatedAtMixin, IntegerIdMixin

if TYPE_CHECKING:
    from infra.orm.likes import PostLikeOrm, CommentLikeOrm
    from infra.orm.messages import MessageOrm
    from infra.orm.posts import PostOrm
    from infra.orm.comments import CommentOrm
    from infra.orm.refresh_sessions import RefreshSessionOrm
    from infra.orm.media import MediaOrm


class UserOrm(IntegerIdMixin, CreatedAtMixin, Base):
    __tablename__ = 'users'

    posts: Mapped[list["PostOrm"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments: Mapped[list["CommentOrm"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    post_likes: Mapped[list["PostLikeOrm"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comment_likes: Mapped[list["CommentLikeOrm"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sent_messages: Mapped[list["MessageOrm"]] = relationship(
        back_populates="sender",
        foreign_keys="MessageOrm.sender_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    received_messages: Mapped[list["MessageOrm"]] = relationship(
        back_populates="recipient",
        foreign_keys="MessageOrm.recipient_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    refresh_sessions: Mapped[list["RefreshSessionOrm"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    avatar_media_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            'media.id',
            ondelete='SET NULL',
            use_alter=True,
            name="fk_users_avatar_media_id_media",
        ),
        nullable=True,
    )

    avatar: Mapped["MediaOrm | None"] = relationship(
        foreign_keys=[avatar_media_id],
    )

    uploaded_media: Mapped[list["MediaOrm"]] = relationship(
        foreign_keys="MediaOrm.owner_id",
    )

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))