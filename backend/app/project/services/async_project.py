"""
文件路径: /backend/app/project/services/async_project.py
功能描述: 项目模块异步业务服务
主要功能:
    - 编排项目查询、创建与统计逻辑
    - 计算和更新项目进度
"""
from decimal import Decimal
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.project.crud.async_project import async_crud_project, async_crud_project_task
from app.project.schemas.project_in import ProjectCreate
from common.error_codes import ErrorCode
from common.exceptions import BusinessException


class ProjectService:
    """项目业务编排层。"""

    async def calculate_project_progress(self, db: AsyncSession, project_id: int) -> Decimal:
        total_tasks = await async_crud_project_task.count_total_by_project(db, project_id)
        if total_tasks == 0:
            return Decimal("0.00")

        completed_tasks = await async_crud_project_task.count_by_project_and_status(db, project_id, "completed")
        return (Decimal(completed_tasks) / Decimal(total_tasks) * 100).quantize(Decimal("0.00"))

    async def update_project_progress(self, db: AsyncSession, project_id: int) -> Decimal:
        progress = await self.calculate_project_progress(db, project_id)
        project = await async_crud_project.get_by_id(db, project_id)
        if project:
            project.progress = progress
            await db.flush()
        return progress

    async def get_projects(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        return await async_crud_project.get_all(db, skip, limit)

    async def get_project_detail(self, db: AsyncSession, project_id: int):
        project = await async_crud_project.get_by_id(db, project_id)
        if not project:
            raise BusinessException(ErrorCode.PROJECT_NOT_FOUND)
        return project

    async def create_project(self, db: AsyncSession, data: ProjectCreate):
        project = await async_crud_project.create(db, data.model_dump())
        await db.commit()
        return project

    async def get_project_stats_summary(self, db: AsyncSession) -> Dict[str, Any]:
        return await async_crud_project_task.get_global_stats(db)


project_service = ProjectService()
