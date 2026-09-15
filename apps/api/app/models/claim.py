"""Claim ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.db.base import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False)  # factual, numerical, attribution, causal, opinion, prediction
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    verification_priority: Mapped[str] = mapped_column(String(50), default="Medium")
    keywords_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    analysis = relationship("Analysis", back_populates="claims")
    evidence_items = relationship("EvidenceItem", back_populates="claim", cascade="all, delete-orphan")
