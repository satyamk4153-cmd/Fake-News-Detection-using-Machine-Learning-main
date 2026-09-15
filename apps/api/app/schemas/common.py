"""Unified API response schemas for TruthLens."""

from typing import Generic, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[APIError] = None
    request_id: Optional[str] = None
    meta: Optional[PaginationMeta] = None
