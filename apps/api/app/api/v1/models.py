"""Model Registry and Performance Metrics router."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import APIResponse
from apps.api.app.services.admin_service import AdminService

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=APIResponse[List[Dict[str, Any]]])
async def list_models(session: AsyncSession = Depends(get_db)):
    """List all registered models, their active statuses, and real evaluation metrics."""
    models = await AdminService.get_registered_models(session)
    return APIResponse(data=models)
