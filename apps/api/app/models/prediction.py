"""Prediction ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.db.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    model_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("model_versions.id"), nullable=True)
    
    label: Mapped[str] = mapped_column(String(100), nullable=False)  # LIKELY CREDIBLE, UNCERTAIN, LIKELY MISLEADING
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    calibrated_probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(50), nullable=False)  # High, Medium, Low
    model_agreement: Mapped[str] = mapped_column(String(50), nullable=False)   # High, Medium, Low
    agreement_score: Mapped[float] = mapped_column(Float, default=1.0)
    ood_score: Mapped[float] = mapped_column(Float, default=0.0)
    model_scores_json: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    limitations: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    analysis = relationship("Analysis", back_populates="prediction")
    model_version = relationship("ModelVersion", back_populates="predictions")
