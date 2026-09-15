"""Model Version and Registry ORM models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.db.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_tag: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    metrics_json: Mapped[str] = mapped_column(Text, nullable=True)
    artifact_path: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="TRAINED", nullable=False)  # TRAINED, EVALUATED, STAGING, PRODUCTION, RETIRED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    predictions = relationship("Prediction", back_populates="model_version")
