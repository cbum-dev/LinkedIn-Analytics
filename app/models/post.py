from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Enum as PgEnum, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PostStatus(str, Enum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"


class ReactionType(str, Enum):
    like = "like"
    praise = "praise"
    empathy = "empathy"
    interest = "interest"
    appreciation = "appreciation"


class Post(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    content: Mapped[str] = mapped_column(String(280), nullable=False)
    status: Mapped[PostStatus] = mapped_column(PgEnum(PostStatus, name="post_status"), default=PostStatus.draft, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    scheduled_second: Mapped[int | None] = mapped_column(Integer)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="posts")
    reactions = relationship("Reaction", back_populates="post", cascade="all,delete")

    __table_args__ = (
        Index("ix_post_owner_status_time", "owner_id", "status", "scheduled_at"),
        Index("ix_post_scheduled_status", "scheduled_at", "status"),
        Index("ix_post_created_at", "created_at"),
    )


class Reaction(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[ReactionType] = mapped_column(PgEnum(ReactionType, name="reaction_type"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    post = relationship("Post", back_populates="reactions")

    __table_args__ = (
        Index("ix_reaction_post_type", "post_id", "type"),
        Index("ix_reaction_created_at", "created_at"),
    )
