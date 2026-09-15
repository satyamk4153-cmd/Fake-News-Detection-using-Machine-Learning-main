"""Model Registry Pydantic schemas."""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class ModelVersionResponse(BaseModel):
    id: str
    version_tag: str
    model_type: str
    metrics: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime


class ModelComparisonItem(BaseModel):
    model_name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    macro_f1: float
    brier_score: float
    expected_calibration_error: float
    confusion_matrix: list
