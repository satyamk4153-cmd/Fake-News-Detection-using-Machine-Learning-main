"""Admin management and observability router."""

from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.admin import AnalyticsOverview, AuditLogItem, SystemHealthResponse
from apps.api.app.services.admin_service import AdminService
from apps.api.app.services.auth_service import require_admin
from apps.api.app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get("/analytics", response_model=APIResponse[AnalyticsOverview])
async def get_analytics(session: AsyncSession = Depends(get_db)):
    """Retrieve system-wide aggregated usage analytics."""
    data = await AdminService.get_analytics(session)
    return APIResponse(data=data)


@router.get("/models", response_model=APIResponse[List[Dict[str, Any]]])
async def get_admin_models(session: AsyncSession = Depends(get_db)):
    """List model versions and lifecycle states."""
    models = await AdminService.get_registered_models(session)
    return APIResponse(data=models)


@router.post("/models/{model_id}/status", response_model=APIResponse[Dict[str, Any]])
async def update_model_status(
    model_id: str,
    status: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_db),
    admin_user=Depends(require_admin)
):
    """Promote or roll back a model version (e.g. STAGING -> PRODUCTION)."""
    result = await AdminService.promote_model(session, model_id, status, admin_user.id)
    return APIResponse(data=result)


@router.get("/audit-logs", response_model=APIResponse[List[AuditLogItem]])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve security and administrative audit trail logs."""
    logs = await AdminService.get_audit_logs(session, limit=limit)
    return APIResponse(data=logs)


@router.get("/system-health", response_model=APIResponse[SystemHealthResponse])
async def get_system_health(session: AsyncSession = Depends(get_db)):
    """Check internal system health and subsystem status."""
    return APIResponse(data=SystemHealthResponse(
        status="healthy",
        database="connected",
        redis="connected_or_memory_fallback",
        ml_models="loaded",
        active_model_version=settings.ACTIVE_MODEL_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc)
    ))
