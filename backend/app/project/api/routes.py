"""
文件路径: /backend/app/project/api/routes.py
功能描述: 项目模块 API 路由定义
主要功能:
    - 提供项目列表、详情、创建接口
    - 提供项目概览统计接口
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.project.schemas.project_in import ProjectCreate
from app.project.schemas.project_out import ProjectDetailOut, ProjectOut
from app.project.services.async_project import project_service
from common.response import StandardResponse
from core.deps import get_db, require_permissions

router = APIRouter(
    prefix="/project",
    tags=["Project"],
    dependencies=[Depends(require_permissions("project"))],
)


@router.get("/list", response_model=StandardResponse[List[ProjectOut]])
async def list_projects_api(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """获取项目列表"""
    data = await project_service.get_projects(db, skip, limit)
    return StandardResponse(data=data)


@router.get("/{project_id}", response_model=StandardResponse[ProjectDetailOut])
async def get_project_detail_api(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取项目详情"""
    data = await project_service.get_project_detail(db, project_id)
    return StandardResponse(data=data)


@router.post("/create", response_model=StandardResponse[ProjectOut])
async def create_project_api(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新项目"""
    result = await project_service.create_project(db, data)
    return StandardResponse(data=result)


@router.get("/stats/overview", response_model=StandardResponse)
async def project_stats_overview_api(
    db: AsyncSession = Depends(get_db),
):
    """项目概览统计"""
    data = await project_service.get_project_stats_summary(db)
    return StandardResponse(data=data)
