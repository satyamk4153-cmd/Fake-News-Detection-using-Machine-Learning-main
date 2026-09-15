"""EvidenceItem ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.db.base import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), index=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    publisher: Mapped[str] = mapped_column(String(255), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    relevance_score: Mapped[float] = mapped_column(Float, default=0.85)
    evidence_type: Mapped[str] = mapped_column(String(50), default="contextual")  # supporting, contradicting, contextual, unclear
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    claim = relationship("Claim", back_populates="evidence_items")
