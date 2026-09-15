"""TruthLens FastAPI Application Entrypoint."""

import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from apps.api.app.core.config import settings
from apps.api.app.core.exceptions import TruthLensException
from apps.api.app.db.session import init_db
from apps.api.app.api.v1.auth import router as auth_router
from apps.api.app.api.v1.analysis import router as analysis_router
from apps.api.app.api.v1.models import router as models_router
from apps.api.app.api.v1.claims import router_claims, router_evidence
from apps.api.app.api.v1.admin import router as admin_router
from apps.api.app.api.v1.health import router as health_router

# Configure structured logging with safe fallback for third-party libraries
class SafeRequestIdFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "system"
        return super().format(record)


_log_handler = logging.StreamHandler()
_log_handler.setFormatter(SafeRequestIdFormatter("%(asctime)s [%(levelname)s] [req_id=%(request_id)s] %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_log_handler])
logger = logging.getLogger("truthlens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing TruthLens Database tables...", extra={"request_id": "startup"})
    await init_db()
    logger.info("TruthLens API ready for requests.", extra={"request_id": "startup"})
    yield
    # Shutdown
    logger.info("TruthLens API shutting down cleanly.", extra={"request_id": "shutdown"})


app = FastAPI(
    title="TruthLens API",
    description=(
        "Production-grade credibility assessment platform for analyzing potentially "
        "misleading news content through calibrated machine learning, feature explainability, "
        "and claim attribution."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


# Global Exception Handlers
@app.exception_handler(TruthLensException)
async def truthlens_exception_handler(request: Request, exc: TruthLensException):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"Domain Exception: {exc.code} - {exc.message}", extra={"request_id": req_id})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            },
            "request_id": req_id
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", "unknown")
    details = [{"field": ".".join(map(str, err["loc"])), "issue": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Input validation failed. Please check submitted fields.",
                "details": {"validation_errors": details}
            },
            "request_id": req_id
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True, extra={"request_id": req_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong while analyzing the article. Your input was not lost. Please try again."
            },
            "request_id": req_id
        }
    )


# Include API v1 Routers
api_v1_prefix = settings.API_V1_PREFIX
app.include_router(health_router, prefix=api_v1_prefix)
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(analysis_router, prefix=api_v1_prefix)
app.include_router(models_router, prefix=api_v1_prefix)
app.include_router(router_claims, prefix=api_v1_prefix)
app.include_router(router_evidence, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)


@app.get("/")
async def root():
    return {
        "service": "TruthLens API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health/ready"
    }
