"""
文件路径: /backend/app/hr/services/async_hr.py
功能描述: HR 模块异步业务服务
主要功能:
    - 编排部门、员工、考勤、招聘业务流程
    - 提供考勤和招聘统计摘要
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.hr.crud.async_hr import (
    async_crud_attendance,
    async_crud_department,
    async_crud_employee,
    async_crud_recruitment,
)
from app.hr.schemas.hr_in import AttendanceCreate, DepartmentCreate, EmployeeCreate, RecruitmentCreate
from common.data_keys import (
    normalize_attendance_status,
    normalize_department_status,
    normalize_employee_status,
    normalize_recruitment_status,
)


class HRService:
    """HR 业务编排层。"""

    async def get_departments(self, db: AsyncSession, page: int = 1, page_size: int = 20):
        skip = (page - 1) * page_size
        return await async_crud_department.list(db, skip=skip, limit=page_size)

    async def create_department(self, db: AsyncSession, data: DepartmentCreate):
        payload = data.model_dump()
        payload["status"] = normalize_department_status(payload.get("status"))
        department = await async_crud_department.create(db, payload)
        await db.commit()
        return department

    async def get_employees(
        self, db: AsyncSession, department_id: Optional[int] = None, page: int = 1, page_size: int = 20
    ):
        skip = (page - 1) * page_size
        return await async_crud_employee.list(db, department_id=department_id, skip=skip, limit=page_size)

    async def create_employee(self, db: AsyncSession, data: EmployeeCreate):
        payload = data.model_dump()
        payload["status"] = normalize_employee_status(payload.get("status"))
        employee = await async_crud_employee.create(db, payload)
        await db.commit()
        return employee

    async def get_attendances(
        self, db: AsyncSession, employee_id: Optional[int] = None, page: int = 1, page_size: int = 20
    ):
        skip = (page - 1) * page_size
        return await async_crud_attendance.list(db, employee_id=employee_id, skip=skip, limit=page_size)

    async def create_attendance(self, db: AsyncSession, data: AttendanceCreate):
        payload = data.model_dump()
        payload["status"] = normalize_attendance_status(payload.get("status"))
        attendance = await async_crud_attendance.create(db, payload)
        await db.commit()
        return attendance

    async def get_attendance_summary(self, db: AsyncSession):
        distribution = await async_crud_attendance.get_status_distribution(db)
        total_employees = await async_crud_employee.count(db)

        return {
            "totalEmployees": total_employees,
            "presenceRate": (distribution.get("present", 0) / total_employees * 100) if total_employees > 0 else 0,
            "statusDistribution": distribution,
        }

    async def get_recruitments(
        self, db: AsyncSession, status: Optional[str] = None, page: int = 1, page_size: int = 20
    ):
        skip = (page - 1) * page_size
        return await async_crud_recruitment.list(db, status=status, skip=skip, limit=page_size)

    async def create_recruitment(self, db: AsyncSession, data: RecruitmentCreate):
        payload = data.model_dump()
        payload["status"] = normalize_recruitment_status(payload.get("status"))
        recruitment = await async_crud_recruitment.create(db, payload)
        await db.commit()
        return recruitment

    async def get_recruitment_overview(self, db: AsyncSession):
        distribution = await async_crud_recruitment.get_status_distribution(db)
        return {
            "totalApplications": sum(distribution.values()),
            "statusSummary": distribution,
        }


hr_service = HRService()
