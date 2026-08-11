"""
File Path: /backend/app/system/crud/async_projection_mapping.py
Description: Async persistence access for Projection mapping revisions.
Main Features:
    - Loads mapping sets and revisions with explicit eager relationships
    - Provides deterministic row locks for lifecycle mutations
    - Keeps transaction commit and rollback in the application Service layer
"""
from collections.abc import Iterable

from sqlalchemy import delete, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.monitor.models.monitor import PlcDbBlockRawSnapshot
from app.system.models.projection_mapping import (
    ProjectionMappingAuditEvent,
    ProjectionMappingBinding,
    ProjectionMappingRevision,
    ProjectionMappingSet,
)


class AsyncProjectionMappingCRUD:
    """SQL-only access methods for Projection mapping control-plane rows."""

    async def list_sets(self, db: AsyncSession) -> list[ProjectionMappingSet]:
        result = await db.execute(
            select(ProjectionMappingSet)
            .options(selectinload(ProjectionMappingSet.active_published_revision))
            .order_by(ProjectionMappingSet.id)
        )
        return list(result.scalars().all())

    async def get_set(
        self,
        db: AsyncSession,
        mapping_set_id: int,
        *,
        for_update: bool = False,
        include_revisions: bool = False,
    ) -> ProjectionMappingSet | None:
        statement = select(ProjectionMappingSet).where(ProjectionMappingSet.id == mapping_set_id)
        if include_revisions:
            statement = statement.options(
                selectinload(ProjectionMappingSet.active_published_revision).selectinload(
                    ProjectionMappingRevision.bindings
                ),
                selectinload(ProjectionMappingSet.revisions).selectinload(
                    ProjectionMappingRevision.bindings
                ),
            )
        elif not for_update:
            statement = statement.options(selectinload(ProjectionMappingSet.active_published_revision))
        if for_update:
            statement = statement.with_for_update()
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_set_by_identity(
        self,
        db: AsyncSession,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
        handler_key: str,
    ) -> ProjectionMappingSet | None:
        result = await db.execute(
            select(ProjectionMappingSet).where(
                ProjectionMappingSet.plc_key == plc_key,
                ProjectionMappingSet.db_number == db_number,
                ProjectionMappingSet.group_name == group_name,
                ProjectionMappingSet.handler_key == handler_key,
            )
        )
        return result.scalar_one_or_none()

    async def get_revision(
        self,
        db: AsyncSession,
        revision_id: int,
        *,
        for_update: bool = False,
    ) -> ProjectionMappingRevision | None:
        statement = (
            select(ProjectionMappingRevision)
            .where(ProjectionMappingRevision.id == revision_id)
            .options(selectinload(ProjectionMappingRevision.bindings))
        )
        if for_update:
            statement = statement.with_for_update()
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_next_revision_no(self, db: AsyncSession, mapping_set_id: int) -> int:
        result = await db.execute(
            select(func.max(ProjectionMappingRevision.revision_no)).where(
                ProjectionMappingRevision.mapping_set_id == mapping_set_id
            )
        )
        return int(result.scalar_one_or_none() or 0) + 1

    async def replace_bindings(
        self,
        db: AsyncSession,
        revision: ProjectionMappingRevision,
        bindings: Iterable[ProjectionMappingBinding],
    ) -> None:
        await db.execute(
            delete(ProjectionMappingBinding).where(
                ProjectionMappingBinding.revision_id == revision.id
            )
        )
        for binding in bindings:
            db.add(binding)
        await db.flush()
        db.expire(revision, ["bindings"])

    async def get_raw_device_identity(
        self,
        db: AsyncSession,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
    ) -> tuple[int, list[int]]:
        filters = (
            PlcDbBlockRawSnapshot.plc_key == plc_key,
            PlcDbBlockRawSnapshot.db_number == db_number,
            PlcDbBlockRawSnapshot.group_name == group_name,
        )
        count_result = await db.execute(
            select(func.count()).select_from(PlcDbBlockRawSnapshot).where(*filters)
        )
        device_result = await db.execute(
            select(distinct(PlcDbBlockRawSnapshot.device_id))
            .where(*filters)
            .order_by(PlcDbBlockRawSnapshot.device_id)
        )
        return int(count_result.scalar_one() or 0), list(device_result.scalars().all())

    async def add(self, db: AsyncSession, row: object) -> None:
        db.add(row)
        await db.flush()

    async def add_audit_event(
        self,
        db: AsyncSession,
        event: ProjectionMappingAuditEvent,
    ) -> None:
        db.add(event)
        await db.flush()


projection_mapping_crud = AsyncProjectionMappingCRUD()
