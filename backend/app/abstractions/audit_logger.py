"""AuditLogger abstraction for compliance logging.

Provides structured audit logging following the schema:
Who, Did What, To What, When, Context
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_optional_request_context
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Standard audit actions."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    EXPORT = "export"
    IMPORT = "import"
    GRANT_ACCESS = "grant_access"
    REVOKE_ACCESS = "revoke_access"


class DataClassification(str, Enum):
    """Data classification levels per spec."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AuditEntry(BaseModel):
    """Audit log entry.

    Schema: Who, Did What, To What, When, Context
    """

    # WHO
    actor_id: str
    actor_type: str = "user"
    actor_ip: Optional[str] = None

    # DID WHAT
    action: AuditAction
    action_detail: Optional[str] = None

    # TO WHAT
    resource_type: str
    resource_id: str

    # CONTEXT
    tenant_id: str
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: Optional[str] = None

    # WHEN
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # CHANGE DETAILS
    old_values: Optional[dict[str, Any]] = None
    new_values: Optional[dict[str, Any]] = None

    # RESULT
    success: bool = True
    error_message: Optional[str] = None

    # CLASSIFICATION
    data_classification: DataClassification = DataClassification.INTERNAL

    @classmethod
    def from_context(
        cls,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        **kwargs,
    ) -> "AuditEntry":
        """Create an audit entry from current request context.

        Automatically populates actor, tenant, and request info from context.
        """
        ctx = get_optional_request_context()

        if ctx:
            return cls(
                actor_id=ctx.user_id or "anonymous",
                actor_ip=ctx.client_ip,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                tenant_id=ctx.tenant_id,
                request_id=ctx.request_id,
                session_id=ctx.session_id,
                **kwargs,
            )
        else:
            # No context - require explicit values
            return cls(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                **kwargs,
            )


class AuditLogger(ABC):
    """Abstract base class for audit logging.

    Audit logs must be:
    - Immutable (append-only)
    - Tamper-evident (signed/hashed in production)
    - Retained per compliance requirements
    """

    @abstractmethod
    async def log(self, entry: AuditEntry) -> str:
        """Log an audit entry.

        Args:
            entry: Audit entry to log

        Returns:
            Audit log ID

        Note:
            This should never fail silently - audit failures should be escalated.
        """
        pass

    @abstractmethod
    async def query(
        self,
        tenant_id: str,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """Query audit logs with filters.

        Args:
            tenant_id: Required tenant filter
            actor_id: Optional actor filter
            resource_type: Optional resource type filter
            resource_id: Optional resource ID filter
            action: Optional action filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum results to return
            offset: Results offset for pagination

        Returns:
            List of matching audit entries
        """
        pass


class DatabaseAuditLogger(AuditLogger):
    """AuditLogger implementation using PostgreSQL."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def log(self, entry: AuditEntry) -> str:
        """Log an audit entry to the database."""
        audit_log = AuditLog(
            actor_id=UUID(entry.actor_id) if entry.actor_id != "anonymous" else uuid4(),
            actor_type=entry.actor_type,
            actor_ip=entry.actor_ip,
            action=entry.action.value,
            action_detail=entry.action_detail,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            tenant_id=UUID(entry.tenant_id),
            request_id=UUID(entry.request_id),
            session_id=UUID(entry.session_id) if entry.session_id else None,
            timestamp=entry.timestamp,
            old_values=entry.old_values,
            new_values=entry.new_values,
            success=entry.success,
            error_message=entry.error_message,
            data_classification=entry.data_classification.value,
        )

        self._session.add(audit_log)
        await self._session.flush()

        logger.info(
            "Audit logged",
            extra={
                "audit_id": str(audit_log.id),
                "action": entry.action.value,
                "resource_type": entry.resource_type,
                "resource_id": entry.resource_id,
            },
        )

        return str(audit_log.id)

    async def query(
        self,
        tenant_id: str,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """Query audit logs from database."""
        stmt = select(AuditLog).where(AuditLog.tenant_id == UUID(tenant_id))

        if actor_id:
            stmt = stmt.where(AuditLog.actor_id == UUID(actor_id))
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
        if resource_id:
            stmt = stmt.where(AuditLog.resource_id == resource_id)
        if action:
            stmt = stmt.where(AuditLog.action == action.value)
        if start_time:
            stmt = stmt.where(AuditLog.timestamp >= start_time)
        if end_time:
            stmt = stmt.where(AuditLog.timestamp <= end_time)

        stmt = stmt.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        logs = result.scalars().all()

        return [
            AuditEntry(
                actor_id=str(log.actor_id),
                actor_type=log.actor_type,
                actor_ip=log.actor_ip,
                action=AuditAction(log.action),
                action_detail=log.action_detail,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                tenant_id=str(log.tenant_id),
                request_id=str(log.request_id),
                session_id=str(log.session_id) if log.session_id else None,
                timestamp=log.timestamp,
                old_values=log.old_values,
                new_values=log.new_values,
                success=log.success,
                error_message=log.error_message,
                data_classification=DataClassification(log.data_classification),
            )
            for log in logs
        ]


class LoggingAuditLogger(AuditLogger):
    """AuditLogger implementation that writes to structured logs.

    Useful for development or when database isn't available.
    """

    async def log(self, entry: AuditEntry) -> str:
        """Log an audit entry to the logging system."""
        log_id = str(uuid4())

        logger.info(
            "AUDIT",
            extra={
                "audit_id": log_id,
                "actor_id": entry.actor_id,
                "actor_type": entry.actor_type,
                "action": entry.action.value,
                "resource_type": entry.resource_type,
                "resource_id": entry.resource_id,
                "tenant_id": entry.tenant_id,
                "request_id": entry.request_id,
                "success": entry.success,
                "data_classification": entry.data_classification.value,
            },
        )

        return log_id

    async def query(
        self,
        tenant_id: str,
        **kwargs,
    ) -> list[AuditEntry]:
        """Query not supported for logging-only implementation."""
        logger.warning("Audit query not supported for LoggingAuditLogger")
        return []
