"""Claims and Evidence routers."""

import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.analysis import ClaimItem, EvidenceItemSchema
from apps.api.app.models.claim import Claim
from apps.api.app.models.evidence import EvidenceItem
from apps.api.app.core.exceptions import NotFoundError

router_claims = APIRouter(tags=["Claims"])
router_evidence = APIRouter(tags=["Evidence"])


@router_claims.get("/analysis/{analysis_id}/claims", response_model=APIResponse[List[ClaimItem]])
async def get_analysis_claims(analysis_id: str, session: AsyncSession = Depends(get_db)):
    """Retrieve all structured claims extracted from a specific analysis."""
    stmt = select(Claim).where(Claim.analysis_id == analysis_id).order_by(Claim.sentence_index)
    claims = (await session.execute(stmt)).scalars().all()
    items = [
        ClaimItem(
            claim_id=c.id,
            text=c.text,
            sentence_index=c.sentence_index,
            claim_type=c.claim_type,
            confidence=c.confidence,
            verification_priority=c.verification_priority,
            keywords=json.loads(c.keywords_json)
        )
        for c in claims
    ]
    return APIResponse(data=items)


@router_evidence.get("/claims/{claim_id}/evidence", response_model=APIResponse[List[EvidenceItemSchema]])
async def get_claim_evidence(claim_id: str, session: AsyncSession = Depends(get_db)):
    """Retrieve attributed evidence references associated with a specific claim."""
    stmt = select(EvidenceItem).where(EvidenceItem.claim_id == claim_id)
    evidence_items = (await session.execute(stmt)).scalars().all()
    items = [
        EvidenceItemSchema(
            source_name=ev.source_name,
            url=ev.url,
            title=ev.title,
            publisher=ev.publisher,
            retrieved_at=ev.retrieved_at,
            relevance_score=ev.relevance_score,
            evidence_type=ev.evidence_type,
            summary=ev.summary
        )
        for ev in evidence_items
    ]
    return APIResponse(data=items)
