"""
文件路径: /backend/app/hr/api/routes.py
功能描述: HR 模块 API 路由定义
主要功能:
    - 汇聚 HR 健康检查、部门、员工、考勤、招聘接口
    - 保持原有外部路由路径稳定
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.hr.schemas.hr_in import AttendanceCreate, DepartmentCreate, EmployeeCreate, RecruitmentCreate
from app.hr.schemas.hr_out import AttendanceResponse, DepartmentResponse, EmployeeResponse, RecruitmentResponse
from app.hr.services.async_hr import hr_service
from app.user.schemas.user_out import UserResponse
from common.response import StandardResponse
from core.deps import get_db, require_permissions

router = APIRouter(prefix="/hr", tags=["HR"])
department_router = APIRouter(prefix="/departments", tags=["HR - Departments"])
employee_router = APIRouter(prefix="/employees", tags=["HR - Employees"])
attendance_router = APIRouter(prefix="/attendances", tags=["HR - Attendances"])
recruitment_router = APIRouter(prefix="/recruitments", tags=["HR - Recruitments"])


@router.get("/health")
async def hr_health():
    """HR 模块健康检查"""
    return {"status": "ok", "module": "hr"}


@department_router.get("", response_model=StandardResponse[List[DepartmentResponse]])
async def list_departments(
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """获取部门列表"""
    data = await hr_service.get_departments(db, page, page_size)
    return StandardResponse(data=data)


@department_router.post("", response_model=StandardResponse[DepartmentResponse])
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """创建部门"""
    result = await hr_service.create_department(db, data)
    return StandardResponse(data=result)


@employee_router.get("", response_model=StandardResponse[List[EmployeeResponse]])
async def list_employees(
    department_id: int = Query(None, alias="departmentId"),
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """获取员工列表"""
    data = await hr_service.get_employees(db, department_id, page, page_size)
    return StandardResponse(data=data)


@employee_router.post("", response_model=StandardResponse[EmployeeResponse])
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """创建员工"""
    result = await hr_service.create_employee(db, data)
    return StandardResponse(data=result)


@attendance_router.get("", response_model=StandardResponse[List[AttendanceResponse]])
async def list_attendances(
    employee_id: int = Query(None, alias="employeeId"),
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """获取考勤列表"""
    data = await hr_service.get_attendances(db, employee_id, page, page_size)
    return StandardResponse(data=data)


@attendance_router.get("/stats/summary", response_model=StandardResponse)
async def attendance_stats_summary(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """获取考勤统计摘要"""
    data = await hr_service.get_attendance_summary(db)
    return StandardResponse(data=data)


@attendance_router.post("", response_model=StandardResponse[AttendanceResponse])
async def create_attendance(
    data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """创建考勤记录"""
    result = await hr_service.create_attendance(db, data)
    return StandardResponse(data=result)


@recruitment_router.get("", response_model=StandardResponse[List[RecruitmentResponse]])
async def list_recruitments(
    status: str = None,
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """获取招聘列表"""
    data = await hr_service.get_recruitments(db, status, page, page_size)
    return StandardResponse(data=data)


@recruitment_router.get("/stats/overview", response_model=StandardResponse)
async def recruitment_stats_overview(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """获取招聘统计概览"""
    data = await hr_service.get_recruitment_overview(db)
    return StandardResponse(data=data)


@recruitment_router.post("", response_model=StandardResponse[RecruitmentResponse])
async def create_recruitment(
    data: RecruitmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("hr")),
):
    """创建招聘记录"""
    result = await hr_service.create_recruitment(db, data)
    return StandardResponse(data=result)
