"""Admin and Observability Pydantic schemas."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


class SystemHealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    ml_models: str
    active_model_version: str
    environment: str
    timestamp: datetime


class AnalyticsOverview(BaseModel):
    total_analyses: int
    total_users: int
    total_feedbacks: int
    assessment_distribution: Dict[str, int]
    average_confidence: float
    uncertain_rate: float
    failure_rate: float
    average_inference_latency_ms: float
    analyses_by_input_type: Dict[str, int]


class AuditLogItem(BaseModel):
    id: str
    actor_id: Optional[str]
    action: str
    target_type: str
    target_id: str
    details: Dict[str, Any]
    created_at: datetime
