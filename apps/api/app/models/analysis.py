"""Analysis ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.db.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    input_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "article", "headline", "url"
    source_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", index=True, nullable=False)  # COMPLETED, FAILED, PROCESSING
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="analyses")
    prediction = relationship("Prediction", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="analysis", cascade="all, delete-orphan")
    explanation = relationship("Explanation", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="analysis", cascade="all, delete-orphan")
