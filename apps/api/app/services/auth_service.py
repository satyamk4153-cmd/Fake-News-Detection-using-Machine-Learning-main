"""Authentication and User Management Service."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from apps.api.app.models.user import User
from apps.api.app.models.audit_and_feedback import AuditLog
from apps.api.app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from apps.api.app.core.exceptions import AuthenticationError, AuthorizationError, ValidationError
from apps.api.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from apps.api.app.db.session import get_db

security_bearer = HTTPBearer(auto_error=False)


class AuthService:

    @staticmethod
    async def register(session: AsyncSession, request: RegisterRequest) -> TokenResponse:
        # Check if email exists
        stmt = select(User).where(User.email == request.email.lower())
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValidationError(f"User with email '{request.email}' already exists.")

        # If it's the first registered user, make them ADMIN for bootstrapping ease
        count_stmt = select(User)
        all_users = await session.execute(count_stmt)
        is_first = len(all_users.scalars().all()) == 0
        role = "ADMIN" if is_first else "USER"

        import uuid
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=request.email.lower(),
            password_hash=hash_password(request.password),
            role=role,
            is_active=True
        )
        session.add(user)
        
        # Audit log
        audit = AuditLog(
            actor_id=user_id,
            action="REGISTER",
            target_type="user",
            target_id=user_id,
            details_json=f'{{"email": "{user.email}", "role": "{role}"}}'
        )
        session.add(audit)
        await session.commit()
        await session.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        return TokenResponse(access_token=token, expires_in=86400)

    @staticmethod
    async def login(session: AsyncSession, request: LoginRequest) -> TokenResponse:
        stmt = select(User).where(User.email == request.email.lower())
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(request.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("This account has been deactivated.")

        audit = AuditLog(
            actor_id=user.id,
            action="LOGIN",
            target_type="user",
            target_id=user.id,
            details_json=f'{{"email": "{user.email}"}}'
        )
        session.add(audit)
        await session.commit()

        token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        return TokenResponse(access_token=token, expires_in=86400)

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Extract current authenticated user if token present, else None."""
    if not auth or not auth.credentials:
        return None
    try:
        payload = decode_access_token(auth.credentials)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await AuthService.get_user_by_id(session, user_id)
    except Exception:
        return None


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Enforce that request is made by an authenticated user."""
    if not user:
        raise AuthenticationError("Authentication required to perform this action.")
    return user


async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    """Enforce that request is made by an ADMIN."""
    if user.role != "ADMIN":
        raise AuthorizationError("Administrative privileges are required.")
    return user
