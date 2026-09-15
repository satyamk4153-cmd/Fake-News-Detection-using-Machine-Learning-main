"""Analysis and Credibility Assessment Orchestration Service."""

import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.app.models.analysis import Analysis
from apps.api.app.models.prediction import Prediction
from apps.api.app.models.claim import Claim
from apps.api.app.models.evidence import EvidenceItem
from apps.api.app.models.audit_and_feedback import Explanation, Feedback, AuditLog
from apps.api.app.models.model_version import ModelVersion
from apps.api.app.core.config import settings
from apps.api.app.core.exceptions import (
    NotFoundError,
    AuthorizationError,
    ValidationError,
    ModelInferenceError,
    InsufficientInputError,
    UnsupportedLanguageError,
)
from apps.api.app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisResponse,
    PredictionDetail,
    ClaimItem,
    EvidenceItemSchema,
    ExplanationDetail,
    HighlightSpanSchema,
    AnalysisListItem,
)
from apps.api.app.services.evidence_service import EvidenceService
from ml.models.ensemble import TruthLensEnsemble
from ml.explainability.claim_extractor import ClaimExtractor
from ml.explainability.highlighter import TextHighlighter
from ml.preprocessing.language_detector import detect_language

# Global cached ensemble instance
_global_ensemble: Optional[TruthLensEnsemble] = None


def get_loaded_ensemble() -> TruthLensEnsemble:
    """Retrieve or initialize the active production ensemble model."""
    global _global_ensemble
    if _global_ensemble is None:
        model_path = Path(settings.MODEL_DIR)
        if not (model_path / "ensemble_meta.joblib").exists():
            raise ModelInferenceError(
                f"Model artifacts not found at {model_path}. Please execute `python -m ml.training.train` first."
            )
        _global_ensemble = TruthLensEnsemble(version=settings.ACTIVE_MODEL_VERSION)
        _global_ensemble.load(model_path)
    return _global_ensemble


class AnalysisService:

    @staticmethod
    async def create_analysis(
        session: AsyncSession,
        request: AnalysisCreateRequest,
        user_id: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> AnalysisResponse:
        start_time = datetime.now(timezone.utc)
        clean_text = request.text.strip()
        headline = (request.headline or "").strip()
        combined_text = f"{headline} {clean_text}".strip()

        # 1. Validation checks
        if len(clean_text) < settings.MIN_HEADLINE_LENGTH:
            raise InsufficientInputError("The submitted text is too short to produce a reliable assessment.")

        lang_res = detect_language(combined_text)
        if not lang_res["supported"]:
            raise UnsupportedLanguageError(lang_res["message"])

        # Compute deterministic hash
        input_hash = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()
        derived_title = headline if headline else (clean_text[:80] + "..." if len(clean_text) > 80 else clean_text)

        # 2. Run Ensemble Inference
        ensemble = get_loaded_ensemble()
        try:
            assessment_result = ensemble.assess(
                text=clean_text,
                headline=headline,
                threshold_low=settings.UNCERTAINTY_THRESHOLD_LOW,
                threshold_high=settings.UNCERTAINTY_THRESHOLD_HIGH
            )
        except Exception as e:
            raise ModelInferenceError(f"Inference error: {str(e)}")

        # 3. Claims Extraction
        claim_extractor = ClaimExtractor()
        extracted_claims = claim_extractor.extract_claims(combined_text, max_claims=5)

        # 4. Text Highlighting
        highlighter = TextHighlighter()
        highlighted_spans = highlighter.generate_highlights(combined_text)

        completion_time = datetime.now(timezone.utc)
        now = completion_time

        # 5. Persist Analysis Record
        analysis = Analysis(
            user_id=user_id,
            input_type=request.input_type,
            source_url=source_url,
            title=derived_title,
            input_hash=input_hash,
            language="en",
            status="COMPLETED",
            created_at=start_time,
            completed_at=completion_time
        )
        session.add(analysis)
        await session.flush()  # populate analysis.id

        # 6. Persist Prediction Record
        prediction = Prediction(
            analysis_id=analysis.id,
            label=assessment_result["label"],
            raw_score=assessment_result["raw_score"],
            calibrated_probability=assessment_result["calibrated_probability"],
            confidence=assessment_result["confidence"],
            confidence_level=assessment_result["confidence_level"],
            model_agreement=assessment_result["model_agreement"],
            agreement_score=assessment_result["agreement_score"],
            ood_score=assessment_result["ood_score"],
            model_scores_json=json.dumps(assessment_result["model_scores"]),
            summary=assessment_result["summary"],
            limitations=assessment_result["limitations"],
            created_at=now
        )
        session.add(prediction)

        # 7. Persist Claims
        db_claims: List[Claim] = []
        for c in extracted_claims:
            db_claim = Claim(
                analysis_id=analysis.id,
                text=c.text,
                sentence_index=c.sentence_index,
                claim_type=c.claim_type,
                confidence=c.confidence,
                verification_priority=c.verification_priority,
                keywords_json=json.dumps(c.keywords),
                created_at=now
            )
            session.add(db_claim)
            db_claims.append(db_claim)
        await session.flush()

        # 8. Retrieve & Persist Evidence
        evidence_items = await EvidenceService.retrieve_evidence_for_claims(db_claims)
        for ev in evidence_items:
            session.add(ev)

        # 9. Persist Explanation
        explanation = Explanation(
            analysis_id=analysis.id,
            supporting_signals_json=json.dumps(assessment_result["supporting_signals"]),
            counter_signals_json=json.dumps(assessment_result["counter_signals"]),
            structural_deviations_json=json.dumps(assessment_result["structural_deviations"]),
            highlighted_spans_json=json.dumps([s.to_dict() for s in highlighted_spans]),
            created_at=now
        )
        session.add(explanation)

        # 10. Audit log
        audit = AuditLog(
            actor_id=user_id,
            action="ANALYZE",
            target_type="analysis",
            target_id=analysis.id,
            details_json=json.dumps({
                "assessment": assessment_result["assessment"],
                "calibrated_probability": assessment_result["calibrated_probability"],
                "input_type": request.input_type
            })
        )
        session.add(audit)

        await session.commit()
        return await AnalysisService.get_analysis_by_id(session, analysis.id)

    @staticmethod
    async def get_analysis_by_id(
        session: AsyncSession,
        analysis_id: str,
        requesting_user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> AnalysisResponse:
        stmt = (
            select(Analysis)
            .where(Analysis.id == analysis_id)
            .options(
                selectinload(Analysis.prediction),
                selectinload(Analysis.claims).selectinload(Claim.evidence_items),
                selectinload(Analysis.explanation)
            )
        )
        result = await session.execute(stmt)
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise NotFoundError("Analysis", analysis_id)

        # Ownership check: if analysis is owned by a user, only that user or an admin can access it
        if analysis.user_id and requesting_user_id and analysis.user_id != requesting_user_id and not is_admin:
            raise AuthorizationError("You do not have permission to view this analysis.")

        pred_detail = None
        if analysis.prediction:
            p = analysis.prediction
            pred_detail = PredictionDetail(
                label=p.label,
                raw_score=p.raw_score,
                calibrated_probability=p.calibrated_probability,
                confidence=p.confidence,
                confidence_level=p.confidence_level,
                model_agreement=p.model_agreement,
                agreement_score=p.agreement_score,
                ood_score=p.ood_score,
                model_scores=json.loads(p.model_scores_json),
                summary=p.summary,
                limitations=p.limitations
            )

        claim_items: List[ClaimItem] = []
        evidence_items: List[EvidenceItemSchema] = []
        for c in analysis.claims:
            claim_items.append(ClaimItem(
                claim_id=c.id,
                text=c.text,
                sentence_index=c.sentence_index,
                claim_type=c.claim_type,
                confidence=c.confidence,
                verification_priority=c.verification_priority,
                keywords=json.loads(c.keywords_json)
            ))
            for ev in c.evidence_items:
                evidence_items.append(EvidenceItemSchema(
                    source_name=ev.source_name,
                    url=ev.url,
                    title=ev.title,
                    publisher=ev.publisher,
                    retrieved_at=ev.retrieved_at,
                    relevance_score=ev.relevance_score,
                    evidence_type=ev.evidence_type,
                    summary=ev.summary
                ))

        expl_detail = None
        if analysis.explanation:
            e = analysis.explanation
            spans = [HighlightSpanSchema(**s) for s in json.loads(e.highlighted_spans_json)]
            expl_detail = ExplanationDetail(
                supporting_signals=json.loads(e.supporting_signals_json),
                counter_signals=json.loads(e.counter_signals_json),
                structural_deviations=json.loads(e.structural_deviations_json),
                highlighted_spans=spans
            )

        return AnalysisResponse(
            id=analysis.id,
            title=analysis.title,
            input_type=analysis.input_type,
            source_url=analysis.source_url,
            language=analysis.language,
            status=analysis.status,
            created_at=analysis.created_at,
            prediction=pred_detail,
            claims=claim_items,
            evidence=evidence_items,
            explanation=expl_detail
        )

    @staticmethod
    async def delete_analysis(
        session: AsyncSession,
        analysis_id: str,
        user_id: str,
        is_admin: bool = False
    ) -> bool:
        stmt = select(Analysis).where(Analysis.id == analysis_id)
        result = await session.execute(stmt)
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise NotFoundError("Analysis", analysis_id)

        if analysis.user_id != user_id and not is_admin:
            raise AuthorizationError("You do not have permission to delete this analysis.")

        await session.delete(analysis)
        audit = AuditLog(
            actor_id=user_id,
            action="DELETE_ANALYSIS",
            target_type="analysis",
            target_id=analysis_id,
            details_json="{}"
        )
        session.add(audit)
        await session.commit()
        return True

    @staticmethod
    async def list_analyses(
        session: AsyncSession,
        user_id: Optional[str] = None,
        assessment_filter: Optional[str] = None,
        input_type_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        is_admin: bool = False
    ) -> Tuple[List[AnalysisListItem], int]:
        stmt = (
            select(Analysis)
            .outerjoin(Prediction, Analysis.id == Prediction.analysis_id)
            .options(selectinload(Analysis.prediction))
        )

        # Non-admins can only list their own analyses, or public/anonymous analyses if unauthenticated
        if not is_admin:
            if user_id:
                stmt = stmt.where(Analysis.user_id == user_id)
            else:
                stmt = stmt.where(Analysis.user_id.is_(None))
        elif user_id:
            stmt = stmt.where(Analysis.user_id == user_id)

        if assessment_filter:
            stmt = stmt.where(Prediction.label.ilike(f"%{assessment_filter}%"))
        if input_type_filter:
            stmt = stmt.where(Analysis.input_type == input_type_filter)
        if search_query:
            stmt = stmt.where(Analysis.title.ilike(f"%{search_query}%"))

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await session.execute(count_stmt)).scalar() or 0

        # Paginated results
        stmt = stmt.order_by(desc(Analysis.created_at)).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        analyses = result.scalars().all()

        items = []
        for a in analyses:
            p_label = a.prediction.label if a.prediction else None
            p_conf = a.prediction.confidence if a.prediction else None
            p_prob = a.prediction.calibrated_probability if a.prediction else None
            items.append(AnalysisListItem(
                id=a.id,
                title=a.title,
                input_type=a.input_type,
                source_url=a.source_url,
                status=a.status,
                created_at=a.created_at,
                label=p_label,
                confidence=p_conf,
                calibrated_probability=p_prob
            ))

        return items, total_count
