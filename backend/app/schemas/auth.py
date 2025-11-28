"""Authentication schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    """Login response with tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""

    sub: str  # user_id
    email: str
    tenant_id: str
    roles: list[str] = []
    type: str  # "access" or "refresh"
    exp: datetime
    iat: Optional[datetime] = None
