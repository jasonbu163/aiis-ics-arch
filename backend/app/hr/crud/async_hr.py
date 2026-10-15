"""
文件路径: /backend/app/hr/crud/async_hr.py
功能描述: HR 模块异步 CRUD
主要功能:
    - 管理部门、员工、考勤、招聘数据库访问逻辑
    - 集中维护 HR SQL 查询
"""
from collections.abc import Sequence
from typing import Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.hr.models.hr import Attendance, Department, Employee, Recruitment
from common.data_keys import (
    normalize_attendance_status,
    normalize_recruitment_status,
    recruitment_status_storage_values,
)


class AsyncCRUDDepartment:
    """部门 SQL 执行层。"""

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Department]:
        result = await db.execute(select(Department).offset(skip).limit(limit))
        return result.scalars().all()

    async def count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Department.id)))
        return result.scalar() or 0

    async def create(self, db: AsyncSession, obj_in: dict) -> Department:
        db_obj = Department(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncCRUDEmployee:
    """员工 SQL 执行层。"""

    async def list(
        self, db: AsyncSession, department_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Sequence[Employee]:
        query = select(Employee)
        if department_id:
            query = query.where(Employee.department_id == department_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def count(self, db: AsyncSession, department_id: Optional[int] = None) -> int:
        query = select(func.count(Employee.id))
        if department_id:
            query = query.where(Employee.department_id == department_id)
        result = await db.execute(query)
        return result.scalar() or 0

    async def create(self, db: AsyncSession, obj_in: dict) -> Employee:
        db_obj = Employee(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncCRUDAttendance:
    """考勤 SQL 执行层。"""

    async def list(
        self, db: AsyncSession, employee_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Sequence[Attendance]:
        query = select(Attendance)
        if employee_id:
            query = query.where(Attendance.employee_id == employee_id)
        query = query.order_by(Attendance.date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_status_distribution(self, db: AsyncSession) -> Dict[str, int]:
        result = await db.execute(select(Attendance.status, func.count(Attendance.id)).group_by(Attendance.status))
        distribution: Dict[str, int] = {}
        for status, count in result.all():
            key = normalize_attendance_status(status) or status
            distribution[key] = distribution.get(key, 0) + count
        return distribution

    async def create(self, db: AsyncSession, obj_in: dict) -> Attendance:
        db_obj = Attendance(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncCRUDRecruitment:
    """招聘 SQL 执行层。"""

    async def list(
        self, db: AsyncSession, status: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> Sequence[Recruitment]:
        query = select(Recruitment)
        if status:
            query = query.where(Recruitment.status.in_(recruitment_status_storage_values(status)))
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_status_distribution(self, db: AsyncSession) -> Dict[str, int]:
        result = await db.execute(select(Recruitment.status, func.count(Recruitment.id)).group_by(Recruitment.status))
        distribution: Dict[str, int] = {}
        for status, count in result.all():
            key = normalize_recruitment_status(status) or status
            distribution[key] = distribution.get(key, 0) + count
        return distribution

    async def create(self, db: AsyncSession, obj_in: dict) -> Recruitment:
        db_obj = Recruitment(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


async_crud_department = AsyncCRUDDepartment()
async_crud_employee = AsyncCRUDEmployee()
async_crud_attendance = AsyncCRUDAttendance()
async_crud_recruitment = AsyncCRUDRecruitment()
