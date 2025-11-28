"""Request context for tenant isolation and audit logging."""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass
class RequestContext:
    """Holds request-scoped context for tenant isolation and audit.

    Uses contextvars for async-safe storage across the request lifecycle.
    """

    request_id: str
    tenant_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_roles: list[str] = field(default_factory=list)
    session_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.user_roles

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.has_role("admin")


# Context variable for request-scoped data
_request_context: ContextVar[Optional[RequestContext]] = ContextVar(
    "request_context",
    default=None,
)


def set_request_context(ctx: RequestContext) -> None:
    """Set the current request context."""
    _request_context.set(ctx)


def get_request_context() -> RequestContext:
    """Get current request context.

    Raises:
        RuntimeError: If not in request scope.
    """
    ctx = _request_context.get()
    if ctx is None:
        raise RuntimeError("No request context available - are you in a request?")
    return ctx


def get_optional_request_context() -> Optional[RequestContext]:
    """Get current request context or None if not in request scope."""
    return _request_context.get()


def get_tenant_id() -> str:
    """Convenience function to get current tenant ID."""
    return get_request_context().tenant_id


def get_user_id() -> Optional[str]:
    """Convenience function to get current user ID."""
    ctx = get_optional_request_context()
    return ctx.user_id if ctx else None


def get_request_id() -> str:
    """Convenience function to get current request ID."""
    return get_request_context().request_id
