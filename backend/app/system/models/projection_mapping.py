"""
File Path: /backend/app/system/models/projection_mapping.py
Description: Database models for published Projection mapping revisions.
Main Features:
    - Stores one PLC/DB-group/handler mapping-set identity
    - Versions immutable validated and published point-to-input bindings
    - Records lifecycle audit events without persisting executable behavior
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProjectionMappingSet(Base):
    """Stable identity for one handler bound to one PLC DB group."""

    __tablename__ = "projection_mapping_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plc_key: Mapped[str] = mapped_column(String(80), nullable=False)
    db_number: Mapped[int] = mapped_column(Integer, nullable=False)
    group_name: Mapped[str] = mapped_column(String(120), nullable=False)
    handler_key: Mapped[str] = mapped_column(String(160), nullable=False)
    active_published_revision_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "projection_mapping_revisions.id",
            name="fk_projection_mapping_set_active_revision",
            ondelete="SET NULL",
            use_alter=True,
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    revisions: Mapped[list["ProjectionMappingRevision"]] = relationship(
        "ProjectionMappingRevision",
        foreign_keys="ProjectionMappingRevision.mapping_set_id",
        back_populates="mapping_set",
        cascade="all, delete-orphan",
    )
    active_published_revision: Mapped["ProjectionMappingRevision | None"] = relationship(
        "ProjectionMappingRevision",
        foreign_keys=[active_published_revision_id],
        post_update=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "plc_key",
            "db_number",
            "group_name",
            "handler_key",
            name="uq_projection_mapping_set_identity",
        ),
    )


class ProjectionMappingRevision(Base):
    """A versioned binding set; only draft revisions may be edited."""

    __tablename__ = "projection_mapping_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mapping_set_id: Mapped[int] = mapped_column(
        ForeignKey("projection_mapping_sets.id", name="fk_projection_mapping_revision_set", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision_no: Mapped[int] = mapped_column(Integer, nullable=False)
    handler_version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_report: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_projection_mapping_revision_created_by", ondelete="SET NULL"),
        nullable=True,
    )
    validated_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_projection_mapping_revision_validated_by", ondelete="SET NULL"),
        nullable=True,
    )
    published_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_projection_mapping_revision_published_by", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    mapping_set: Mapped[ProjectionMappingSet] = relationship(
        "ProjectionMappingSet",
        foreign_keys=[mapping_set_id],
        back_populates="revisions",
    )
    bindings: Mapped[list["ProjectionMappingBinding"]] = relationship(
        "ProjectionMappingBinding",
        back_populates="revision",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'validated', 'published', 'retired')",
            name="ck_projection_mapping_revision_status",
        ),
        UniqueConstraint(
            "mapping_set_id",
            "revision_no",
            name="uq_projection_mapping_revision_number",
        ),
    )


class ProjectionMappingBinding(Base):
    """One full PLC point identity bound to one declared handler input."""

    __tablename__ = "projection_mapping_bindings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    revision_id: Mapped[int] = mapped_column(
        ForeignKey("projection_mapping_revisions.id", name="fk_projection_mapping_binding_revision", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plc_key: Mapped[str] = mapped_column(String(80), nullable=False)
    db_number: Mapped[int] = mapped_column(Integer, nullable=False)
    group_name: Mapped[str] = mapped_column(String(120), nullable=False)
    point_name: Mapped[str] = mapped_column(String(180), nullable=False)
    input_key: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    revision: Mapped[ProjectionMappingRevision] = relationship(
        "ProjectionMappingRevision",
        back_populates="bindings",
    )

    __table_args__ = (
        UniqueConstraint(
            "revision_id",
            "input_key",
            name="uq_projection_mapping_binding_input",
        ),
        UniqueConstraint(
            "revision_id",
            "plc_key",
            "db_number",
            "group_name",
            "point_name",
            name="uq_projection_mapping_binding_point",
        ),
    )


class ProjectionMappingAuditEvent(Base):
    """Append-only lifecycle evidence for mapping revision actions."""

    __tablename__ = "projection_mapping_audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mapping_set_id: Mapped[int] = mapped_column(
        ForeignKey("projection_mapping_sets.id", name="fk_projection_mapping_audit_set", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision_id: Mapped[int | None] = mapped_column(
        ForeignKey("projection_mapping_revisions.id", name="fk_projection_mapping_audit_revision", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_projection_mapping_audit_actor", ondelete="SET NULL"),
        nullable=True,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ProjectionRuntimeCursor(Base):
    """One durable raw-fact cursor for a stable Projection mapping set."""

    __tablename__ = "projection_runtime_cursors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mapping_set_id: Mapped[int] = mapped_column(
        ForeignKey("projection_mapping_sets.id", name="fk_projection_runtime_cursor_set", ondelete="CASCADE"),
        nullable=False,
    )
    last_raw_snapshot_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_signature: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("mapping_set_id", name="uq_projection_runtime_cursor_set"),
    )


class ProjectionRuntimeAuditEvent(Base):
    """Append-only batch evidence for the headless Projection runtime."""

    __tablename__ = "projection_runtime_audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mapping_set_id: Mapped[int] = mapped_column(
        ForeignKey("projection_mapping_sets.id", name="fk_projection_runtime_audit_set", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision_id: Mapped[int | None] = mapped_column(
        ForeignKey("projection_mapping_revisions.id", name="fk_projection_runtime_audit_revision", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    first_raw_snapshot_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_raw_snapshot_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processed_snapshot_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_quality: Mapped[str | None] = mapped_column(String(30), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('processed', 'skipped', 'contract_rejected', 'failed')",
            name="ck_projection_runtime_audit_event_type",
        ),
        Index(
            "ix_projection_runtime_audit_set_raw",
            "mapping_set_id",
            "last_raw_snapshot_id",
        ),
    )
