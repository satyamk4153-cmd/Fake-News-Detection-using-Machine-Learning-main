"""Analysis and Prediction Pydantic schemas."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class AnalysisCreateRequest(BaseModel):
    text: str = Field(..., min_length=15, max_length=50000, description="Article or statement text to analyze")
    headline: Optional[str] = Field(default="", max_length=500, description="Optional headline")
    input_type: str = Field(default="article", pattern="^(article|headline)$")


class URLAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2000, description="Web address of the news article to analyze")


class PredictionDetail(BaseModel):
    label: str
    raw_score: float
    calibrated_probability: float
    confidence: float
    confidence_level: str
    model_agreement: str
    agreement_score: float
    ood_score: float
    model_scores: Dict[str, float]
    summary: str
    limitations: str


class ClaimItem(BaseModel):
    claim_id: str
    text: str
    sentence_index: int
    claim_type: str
    confidence: float
    verification_priority: str
    keywords: List[str]


class EvidenceItemSchema(BaseModel):
    source_name: str
    url: Optional[str] = None
    title: str
    publisher: Optional[str] = None
    retrieved_at: datetime
    relevance_score: float
    evidence_type: str
    summary: str


class HighlightSpanSchema(BaseModel):
    text: str
    start_char: int
    end_char: int
    influence_level: str
    direction: str
    weight: float
    explanation: str


class ExplanationDetail(BaseModel):
    supporting_signals: List[Any]
    counter_signals: List[Any]
    structural_deviations: List[Any]
    highlighted_spans: List[HighlightSpanSchema]


class AnalysisResponse(BaseModel):
    id: str
    title: str
    input_type: str
    source_url: Optional[str] = None
    language: str
    status: str
    created_at: datetime
    prediction: Optional[PredictionDetail] = None
    claims: List[ClaimItem] = Field(default_factory=list)
    evidence: List[EvidenceItemSchema] = Field(default_factory=list)
    explanation: Optional[ExplanationDetail] = None


class AnalysisListItem(BaseModel):
    id: str
    title: str
    input_type: str
    source_url: Optional[str] = None
    status: str
    created_at: datetime
    label: Optional[str] = None
    confidence: Optional[float] = None
    calibrated_probability: Optional[float] = None


class FeedbackCreateRequest(BaseModel):
    is_useful: bool
    feedback_category: Optional[str] = Field(default=None, pattern="^(prediction_wrong|explanation_unclear|source_issue|other)$")
    comment: Optional[str] = Field(default=None, max_length=1000)
