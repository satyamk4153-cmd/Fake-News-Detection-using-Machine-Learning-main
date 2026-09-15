"""Custom domain exceptions for TruthLens."""

from typing import Optional, Dict, Any


class TruthLensException(Exception):
    """Base exception for all domain errors in TruthLens."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ValidationError(TruthLensException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, details=details)


class AuthenticationError(TruthLensException):
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, code="AUTHENTICATION_FAILED", status_code=401)


class AuthorizationError(TruthLensException):
    def __init__(self, message: str = "Insufficient permissions to access this resource"):
        super().__init__(message, code="FORBIDDEN", status_code=403)


class NotFoundError(TruthLensException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(f"{resource} with identifier '{identifier}' was not found.", code="NOT_FOUND", status_code=404)


class RateLimitError(TruthLensException):
    def __init__(self, message: str = "Too many requests. Please try again shortly."):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", status_code=429)


class URLFetchError(TruthLensException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="URL_FETCH_FAILED", status_code=400, details=details)


class ArticleExtractionError(TruthLensException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ARTICLE_EXTRACTION_FAILED", status_code=422, details=details)


class ModelInferenceError(TruthLensException):
    def __init__(self, message: str):
        super().__init__(message, code="MODEL_INFERENCE_FAILED", status_code=503)


class UnsupportedLanguageError(TruthLensException):
    def __init__(self, message: str = "English analysis is currently supported."):
        super().__init__(message, code="UNSUPPORTED_LANGUAGE", status_code=400)


class InsufficientInputError(TruthLensException):
    def __init__(self, message: str = "More text is required for a reliable assessment."):
        super().__init__(message, code="INSUFFICIENT_INPUT", status_code=400)
