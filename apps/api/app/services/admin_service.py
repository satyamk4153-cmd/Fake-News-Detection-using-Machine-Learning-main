"""Admin Analytics, Model Registry Lifecycle, and Telemetry Service."""

import json
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.user import User
from apps.api.app.models.analysis import Analysis
from apps.api.app.models.prediction import Prediction
from apps.api.app.models.audit_and_feedback import Feedback, AuditLog
from apps.api.app.models.model_version import ModelVersion
from apps.api.app.schemas.admin import AnalyticsOverview, AuditLogItem, SystemHealthResponse
from apps.api.app.core.config import settings
from apps.api.app.core.exceptions import NotFoundError, ValidationError


class AdminService:

    @staticmethod
    async def get_analytics(session: AsyncSession) -> AnalyticsOverview:
        # Total counts
        total_analyses = (await session.execute(select(func.count(Analysis.id)))).scalar() or 0
        total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
        total_feedbacks = (await session.execute(select(func.count(Feedback.id)))).scalar() or 0

        # Assessment distribution
        stmt_dist = select(Prediction.label, func.count(Prediction.id)).group_by(Prediction.label)
        dist_rows = (await session.execute(stmt_dist)).all()
        assessment_dist = {label: count for label, count in dist_rows}

        # Average confidence
        avg_conf_stmt = select(func.avg(Prediction.confidence))
        avg_confidence = (await session.execute(avg_conf_stmt)).scalar() or 0.0

        # Uncertain rate
        uncertain_count = assessment_dist.get("UNCERTAIN / NEEDS VERIFICATION", 0) + assessment_dist.get("UNCERTAIN", 0)
        uncertain_rate = (uncertain_count / total_analyses * 100) if total_analyses > 0 else 0.0

        # Failure rate
        failed_count_stmt = select(func.count(Analysis.id)).where(Analysis.status == "FAILED")
        failed_count = (await session.execute(failed_count_stmt)).scalar() or 0
        failure_rate = (failed_count / total_analyses * 100) if total_analyses > 0 else 0.0

        # Input type distribution
        stmt_types = select(Analysis.input_type, func.count(Analysis.id)).group_by(Analysis.input_type)
        type_rows = (await session.execute(stmt_types)).all()
        by_type = {t: count for t, count in type_rows}

        # Dynamic inference latency calculation across completed analyses
        stmt_latency = (
            select(Analysis.created_at, Analysis.completed_at)
            .where(Analysis.status == "COMPLETED")
            .order_by(desc(Analysis.created_at))
            .limit(100)
        )
        latency_rows = (await session.execute(stmt_latency)).all()
        latencies = []
        for row in latency_rows:
            if row[0] and row[1]:
                delta = (row[1] - row[0]).total_seconds() * 1000.0
                if delta >= 0:
                    latencies.append(delta)
        
        avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 0.0

        return AnalyticsOverview(
            total_analyses=total_analyses,
            total_users=total_users,
            total_feedbacks=total_feedbacks,
            assessment_distribution=assessment_dist,
            average_confidence=round(float(avg_confidence), 2),
            uncertain_rate=round(float(uncertain_rate), 2),
            failure_rate=round(float(failure_rate), 2),
            average_inference_latency_ms=avg_latency,
            analyses_by_input_type=by_type
        )

    @staticmethod
    async def get_audit_logs(session: AsyncSession, limit: int = 50) -> List[AuditLogItem]:
        stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
        logs = (await session.execute(stmt)).scalars().all()
        
        items = []
        for log in logs:
            try:
                details = json.loads(log.details_json)
            except Exception:
                details = {}
            items.append(AuditLogItem(
                id=log.id,
                actor_id=log.actor_id,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                details=details,
                created_at=log.created_at
            ))
        return items

    @staticmethod
    async def get_registered_models(session: AsyncSession) -> List[Dict[str, Any]]:
        """List registered models and sync real evaluation report metrics."""
        report_file = Path(settings.MODEL_DIR) / "evaluation_report.json"
        eval_metrics = {}
        if report_file.exists():
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    eval_metrics = json.load(f)
            except Exception:
                pass

        # Load database models or populate defaults from verified training run
        stmt = select(ModelVersion).order_by(desc(ModelVersion.created_at))
        models = (await session.execute(stmt)).scalars().all()

        if not models and eval_metrics:
            # Seed initial model versions from verified training evaluation
            for key, ev in eval_metrics.items():
                status = "PRODUCTION" if key == "ensemble" else "EVALUATED"
                mv = ModelVersion(
                    version_tag=ev["model_version"],
                    model_type=ev["model_name"],
                    metrics_json=json.dumps(ev),
                    artifact_path=f"ml/artifacts/{key}.joblib",
                    status=status
                )
                session.add(mv)
            await session.commit()
            models = (await session.execute(stmt)).scalars().all()

        results = []
        for m in models:
            metrics = json.loads(m.metrics_json) if m.metrics_json else None
            results.append({
                "id": m.id,
                "version_tag": m.version_tag,
                "model_type": m.model_type,
                "status": m.status,
                "metrics": metrics,
                "created_at": m.created_at
            })
        return results

    @staticmethod
    async def promote_model(session: AsyncSession, model_id: str, new_status: str, admin_user_id: str) -> Dict[str, Any]:
        """Update model status (e.g. STAGING -> PRODUCTION or rollback)."""
        valid_statuses = {"TRAINED", "EVALUATED", "STAGING", "PRODUCTION", "RETIRED"}
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status '{new_status}'. Allowed: {valid_statuses}")

        stmt = select(ModelVersion).where(ModelVersion.id == model_id)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError("ModelVersion", model_id)

        old_status = model.status
        model.status = new_status

        # If promoting to production, retire any other production ensemble
        if new_status == "PRODUCTION":
            stmt_others = select(ModelVersion).where(ModelVersion.id != model_id, ModelVersion.status == "PRODUCTION")
            others = (await session.execute(stmt_others)).scalars().all()
            for other in others:
                other.status = "RETIRED"

        audit = AuditLog(
            actor_id=admin_user_id,
            action="MODEL_STATUS_CHANGE",
            target_type="model_version",
            target_id=model_id,
            details_json=json.dumps({"from": old_status, "to": new_status, "version": model.version_tag})
        )
        session.add(audit)
        await session.commit()

        return {
            "model_id": model.id,
            "version_tag": model.version_tag,
            "status": model.status,
            "previous_status": old_status
        }
