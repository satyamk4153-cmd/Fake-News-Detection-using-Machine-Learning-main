"""Analysis and Credibility router."""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import APIResponse, PaginationMeta
from apps.api.app.schemas.analysis import (
    AnalysisCreateRequest,
    URLAnalysisRequest,
    AnalysisResponse,
    AnalysisListItem,
    FeedbackCreateRequest,
)
from apps.api.app.services.analysis_service import AnalysisService
from apps.api.app.services.auth_service import get_current_user_optional, get_current_user
from apps.api.app.core.ssrf import fetch_url_safely, extract_article_from_html
from apps.api.app.core.rate_limiter import rate_limit_dependency
from apps.api.app.models.audit_and_feedback import Feedback

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("", response_model=APIResponse[AnalysisResponse], dependencies=[Depends(rate_limit_dependency(max_requests=30))])
async def analyze_text(
    request: AnalysisCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    """Analyze news headline or full article text for credibility and linguistic signals."""
    user_id = current_user.id if current_user else None
    result = await AnalysisService.create_analysis(session, request, user_id=user_id)
    return APIResponse(data=result)


@router.post("/url", response_model=APIResponse[AnalysisResponse], dependencies=[Depends(rate_limit_dependency(max_requests=15))])
async def analyze_url(
    request: URLAnalysisRequest,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    """Fetch article content safely from URL (with SSRF protection) and execute credibility analysis."""
    final_url, _, html_text = await fetch_url_safely(request.url)
    title, body_text = extract_article_from_html(html_text)

    analysis_req = AnalysisCreateRequest(
        text=body_text,
        headline=title,
        input_type="url"
    )
    user_id = current_user.id if current_user else None
    result = await AnalysisService.create_analysis(
        session,
        analysis_req,
        user_id=user_id,
        source_url=final_url
    )
    return APIResponse(data=result)


@router.get("/{analysis_id}", response_model=APIResponse[AnalysisResponse])
async def get_analysis(
    analysis_id: str,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    """Retrieve detailed analysis result by ID."""
    user_id = current_user.id if current_user else None
    is_admin = (current_user.role == "ADMIN") if current_user else False
    result = await AnalysisService.get_analysis_by_id(
        session,
        analysis_id,
        requesting_user_id=user_id,
        is_admin=is_admin
    )
    return APIResponse(data=result)


@router.delete("/{analysis_id}", response_model=APIResponse[dict])
async def delete_analysis(
    analysis_id: str,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Delete an analysis record. Only the owner or an admin can delete it."""
    is_admin = (current_user.role == "ADMIN")
    await AnalysisService.delete_analysis(session, analysis_id, current_user.id, is_admin=is_admin)
    return APIResponse(data={"message": "Analysis successfully deleted."})


@router.get("", response_model=APIResponse[List[AnalysisListItem]])
async def list_analyses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    assessment: Optional[str] = Query(None),
    input_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    """List historical analysis records with optional filtering by assessment and input type."""
    user_id = current_user.id if current_user else None
    is_admin = (current_user.role == "ADMIN") if current_user else False
    import math
    items, total = await AnalysisService.list_analyses(
        session,
        user_id=user_id,
        assessment_filter=assessment,
        input_type_filter=input_type,
        search_query=search,
        page=page,
        page_size=page_size,
        is_admin=is_admin
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages
    )
    return APIResponse(data=items, meta=meta)


@router.post("/{analysis_id}/feedback", response_model=APIResponse[dict])
async def submit_feedback(
    analysis_id: str,
    feedback: FeedbackCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    """Submit user feedback regarding the accuracy or clarity of an assessment."""
    user_id = current_user.id if current_user else None
    fb = Feedback(
        analysis_id=analysis_id,
        user_id=user_id,
        is_useful=feedback.is_useful,
        feedback_category=feedback.feedback_category,
        comment=feedback.comment
    )
    session.add(fb)
    await session.commit()
    return APIResponse(data={"message": "Feedback submitted successfully. Thank you for helping improve model monitoring."})
