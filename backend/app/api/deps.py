"""FastAPI dependencies for injection."""

from typing import Annotated, Optional
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.context import RequestContext, get_request_context, set_request_context
from app.core.security import verify_access_token
from app.db.session import get_db
from app.models.user import User

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Optional[User]:
    """Get current user from JWT token if provided.

    Returns None if no token or invalid token.
    """
    if not credentials:
        return None

    try:
        payload = verify_access_token(credentials.credentials)

        user_id = UUID(payload["sub"])
        stmt = select(User).where(User.id == user_id, User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update request context with user info
            ctx = get_request_context()
            ctx.user_id = str(user.id)
            ctx.user_email = user.email
            ctx.user_roles = user.roles or []
            ctx.tenant_id = str(user.tenant_id)
            set_request_context(ctx)

        return user

    except (jwt.InvalidTokenError, ValueError, KeyError):
        return None


async def get_current_user(
    user: Annotated[Optional[User], Depends(get_current_user_optional)],
) -> User:
    """Get current authenticated user.

    Raises HTTPException if not authenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user.

    Raises HTTPException if user is inactive.
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return user


async def require_admin(
    user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require admin role.

    Raises HTTPException if user is not admin.
    """
    if not user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_admin)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
DB = Annotated[AsyncSession, Depends(get_db)]
