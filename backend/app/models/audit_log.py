"""Audit log model for compliance tracking."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """Immutable audit log for compliance.

    Schema follows: Who, Did What, To What, When, Context

    This table should be append-only in production.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # WHO
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    actor_type: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False,
    )
    actor_ip: Mapped[str | None] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )

    # DID WHAT
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    action_detail: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # TO WHAT
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # CONTEXT
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # WHEN
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # CHANGE DETAILS
    old_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    new_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # RESULT
    success: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # CLASSIFICATION
    data_classification: Mapped[str] = mapped_column(
        String(20),
        default="internal",
        nullable=False,
    )

    __table_args__ = (
        Index("ix_audit_tenant_timestamp", "tenant_id", "timestamp"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_actor_action", "actor_id", "action"),
    )
