"""
文件路径: /backend/app/hr/models/__init__.py
功能描述: HR 模块数据库模型导出
主要功能:
    - 导出部门、员工、考勤、招聘和应聘者模型
"""
from app.hr.models.hr import Applicant, Attendance, Department, Employee, Recruitment

__all__ = ["Department", "Employee", "Attendance", "Recruitment", "Applicant"]
