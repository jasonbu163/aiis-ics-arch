"""
文件路径: /backend/app/hr/models/hr.py
功能描述: 人力资源数据模型定义
主要功能:
    - 定义部门、员工、考勤、招聘、应聘者表结构
    - 使用 SQLAlchemy 2.0 现代风格
"""
import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, IntPk, Timestamp, UpdatedAt


class Department(Base):
    """部门模型"""

    __tablename__ = "departments"

    id: Mapped[IntPk] = mapped_column()
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department")
    parent: Mapped[Optional["Department"]] = relationship("Department", remote_side=[id], back_populates="children")
    children: Mapped[List["Department"]] = relationship("Department", back_populates="parent")


class Employee(Base):
    """员工模型"""

    __tablename__ = "employees"

    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    join_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    attendances: Mapped[List["Attendance"]] = relationship("Attendance", back_populates="employee")


class Attendance(Base):
    """考勤模型"""

    __tablename__ = "attendances"

    id: Mapped[IntPk]
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    check_in: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    check_out: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    work_hours: Mapped[Optional[int]] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="normal")
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[Timestamp]

    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendances")


class Recruitment(Base):
    """招聘模型"""

    __tablename__ = "recruitments"

    id: Mapped[IntPk]
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    count: Mapped[int] = mapped_column(default=1)
    applicants: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="open")
    publish_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    requirements: Mapped[Optional[str]] = mapped_column(String(1000))
    salary_range: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    applicants_list: Mapped[List["Applicant"]] = relationship("Applicant", back_populates="recruitment")


class Applicant(Base):
    """应聘者模型"""

    __tablename__ = "applicants"

    id: Mapped[IntPk]
    recruitment_id: Mapped[int] = mapped_column(ForeignKey("recruitments.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    education: Mapped[Optional[str]] = mapped_column(String(50))
    experience: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    apply_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[Timestamp]

    recruitment: Mapped["Recruitment"] = relationship("Recruitment", back_populates="applicants_list")
