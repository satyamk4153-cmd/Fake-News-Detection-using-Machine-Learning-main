"""Health and Readiness endpoints."""

from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import APIResponse
from apps.api.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", response_model=APIResponse[dict])
async def liveness():
    """Liveness probe: verifies process is running."""
    return APIResponse(data={
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@router.get("/ready", response_model=APIResponse[dict])
async def readiness(session: AsyncSession = Depends(get_db)):
    """Readiness probe: verifies database, models, and file system are accessible."""
    checks = {}

    # 1. Database check
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # 2. ML Artifacts check
    model_dir = Path(settings.MODEL_DIR)
    if (model_dir / "ensemble_meta.joblib").exists():
        checks["ml_models"] = "ok"
    else:
        checks["ml_models"] = "missing_artifacts"

    is_ready = checks.get("database") == "ok" and checks.get("ml_models") == "ok"

    return APIResponse(
        success=is_ready,
        data={
            "status": "ready" if is_ready else "degraded",
            "checks": checks,
            "active_model_version": settings.ACTIVE_MODEL_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
