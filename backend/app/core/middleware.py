"""FastAPI middleware for security and request context."""

import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.core.context import RequestContext, set_request_context

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Establishes request context for tenant isolation and audit logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Extract tenant from header (in production, validate against JWT)
        tenant_id = request.headers.get("X-Tenant-ID", "default")

        # Extract client info
        client_ip = None
        if request.client:
            client_ip = request.client.host

        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Create context
        ctx = RequestContext(
            request_id=request_id,
            tenant_id=tenant_id,
            client_ip=client_ip,
            user_agent=request.headers.get("User-Agent"),
        )

        # Set context for this request
        set_request_context(ctx)

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs request/response for debugging and audit."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
            },
        )

        response = await call_next(request)

        # Log response
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limits request body size to prevent DoS attacks."""

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("Content-Length")

        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return Response(
                content="Request body too large",
                status_code=413,
                media_type="text/plain",
            )

        return await call_next(request)


def configure_middleware(app: FastAPI) -> None:
    """Configure all middleware in correct order.

    Order matters: First added = outermost = runs first on request.
    """
    settings = get_settings()

    # 1. CORS (must handle preflight before other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 2. Request size limit
    app.add_middleware(RequestSizeLimitMiddleware)

    # 3. Request logging
    if settings.debug:
        app.add_middleware(RequestLoggingMiddleware)

    # 4. Request context (should be inner to have full context)
    app.add_middleware(RequestContextMiddleware)
