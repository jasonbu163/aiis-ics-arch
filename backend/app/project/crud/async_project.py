"""
文件路径: /backend/app/project/crud/async_project.py
功能描述: 项目模块异步 CRUD
主要功能:
    - 查询和创建项目、任务、里程碑
    - 提供项目统计查询
"""
from collections.abc import Sequence
from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.project.models.project import Project, ProjectMilestone, ProjectTask


class AsyncCRUDProject:
    """项目 SQL 执行层。"""

    async def get_by_id(self, db: AsyncSession, project_id: int) -> Optional[Project]:
        result = await db.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.tasks), selectinload(Project.milestones))
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Project]:
        result = await db.execute(select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc()))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> Project:
        db_obj = Project(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncCRUDProjectTask:
    """项目任务 SQL 执行层。"""

    async def get_by_project(self, db: AsyncSession, project_id: int) -> Sequence[ProjectTask]:
        result = await db.execute(select(ProjectTask).where(ProjectTask.project_id == project_id))
        return result.scalars().all()

    async def count_by_project_and_status(self, db: AsyncSession, project_id: int, status: str) -> int:
        result = await db.execute(
            select(func.count(ProjectTask.id)).where(ProjectTask.project_id == project_id, ProjectTask.status == status)
        )
        return result.scalar() or 0

    async def count_total_by_project(self, db: AsyncSession, project_id: int) -> int:
        result = await db.execute(select(func.count(ProjectTask.id)).where(ProjectTask.project_id == project_id))
        return result.scalar() or 0

    async def get_global_stats(self, db: AsyncSession) -> Dict[str, Any]:
        project_result = await db.execute(select(Project.status, func.count(Project.id)).group_by(Project.status))
        status_stats = {status: count for status, count in project_result.all()}

        avg_result = await db.execute(select(func.avg(Project.progress)))
        avg_progress = avg_result.scalar() or 0

        return {
            "total": sum(status_stats.values()),
            "active": status_stats.get("active", 0),
            "completed": status_stats.get("completed", 0),
            "avgProgress": float(avg_progress),
        }

    async def create(self, db: AsyncSession, obj_in: dict) -> ProjectTask:
        db_obj = ProjectTask(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncCRUDProjectMilestone:
    """项目里程碑 SQL 执行层。"""

    async def get_by_project(self, db: AsyncSession, project_id: int) -> Sequence[ProjectMilestone]:
        result = await db.execute(select(ProjectMilestone).where(ProjectMilestone.project_id == project_id))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> ProjectMilestone:
        db_obj = ProjectMilestone(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


async_crud_project = AsyncCRUDProject()
async_crud_project_task = AsyncCRUDProjectTask()
async_crud_project_milestone = AsyncCRUDProjectMilestone()
