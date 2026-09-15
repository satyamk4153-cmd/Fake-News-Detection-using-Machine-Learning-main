"""Authentication router."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from apps.api.app.services.auth_service import AuthService, get_current_user
from apps.api.app.core.rate_limiter import rate_limit_dependency

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[TokenResponse], dependencies=[Depends(rate_limit_dependency(max_requests=10))])
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    token = await AuthService.register(session, request)
    return APIResponse(data=token)


@router.post("/login", response_model=APIResponse[TokenResponse], dependencies=[Depends(rate_limit_dependency(max_requests=20))])
async def login(request: LoginRequest, session: AsyncSession = Depends(get_db)):
    """Authenticate existing user credentials."""
    token = await AuthService.login(session, request)
    return APIResponse(data=token)


@router.post("/logout", response_model=APIResponse[dict])
async def logout(current_user=Depends(get_current_user)):
    """Log out of the current session."""
    return APIResponse(data={"message": "Successfully logged out."})


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(current_user=Depends(get_current_user)):
    """Retrieve current authenticated user profile."""
    return APIResponse(data=UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    ))
