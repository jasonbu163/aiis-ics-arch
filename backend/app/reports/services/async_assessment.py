"""
文件路径: /backend/app/reports/services/async_assessment.py
功能描述: 评估管理异步服务
主要功能:
    - 编排评估列表、创建、更新和统计
    - 保持评估接口既有响应结构
"""
import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.crud.async_assessment import AssessmentCRUD
from app.reports.models.reports import Assessment


def serialize_assessment(assessment: Assessment) -> dict:
    return {
        "id": assessment.id,
        "employeeId": assessment.employee_id,
        "employeeName": assessment.employee_name,
        "assessmentType": assessment.assessment_type,
        "assessmentPeriod": assessment.assessment_period,
        "productionScore": float(assessment.production_score) if assessment.production_score else 0,
        "qualityScore": float(assessment.quality_score) if assessment.quality_score else 0,
        "efficiencyScore": float(assessment.efficiency_score) if assessment.efficiency_score else 0,
        "overallScore": float(assessment.overall_score) if assessment.overall_score else 0,
        "grade": assessment.grade,
        "comments": assessment.comments,
        "assessorId": assessment.assessor_id,
        "assessmentDate": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
    }


class AssessmentService:
    """评估管理业务编排层。"""

    @staticmethod
    def crud(db: AsyncSession) -> AssessmentCRUD:
        return AssessmentCRUD(db)

    async def list_assessments(
        self,
        db: AsyncSession,
        page: int,
        page_size: int,
        employee_name: Optional[str],
        assessment_type: Optional[str],
    ) -> dict:
        crud = self.crud(db)
        assessments = await crud.list_assessments(page, page_size, employee_name, assessment_type)
        total = await crud.count_all_assessments()

        return {
            "items": [serialize_assessment(assessment) for assessment in assessments],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def create_assessment(
        self,
        db: AsyncSession,
        employee_id: int,
        employee_name: str,
        assessment_type: str,
        assessment_period: str,
        production_score: float,
        quality_score: float,
        efficiency_score: float,
        overall_score: float,
        grade: str,
        assessment_date: str,
        comments: Optional[str],
        assessor_id: int,
    ) -> dict:
        assessment = Assessment(
            employee_id=employee_id,
            employee_name=employee_name,
            assessment_type=assessment_type,
            assessment_period=assessment_period,
            production_score=Decimal(str(production_score)),
            quality_score=Decimal(str(quality_score)),
            efficiency_score=Decimal(str(efficiency_score)),
            overall_score=Decimal(str(overall_score)),
            grade=grade,
            comments=comments,
            assessor_id=assessor_id,
            assessment_date=datetime.date.fromisoformat(assessment_date),
        )
        assessment = await self.crud(db).create_assessment(assessment)
        return serialize_assessment(assessment)

    async def update_assessment(
        self,
        db: AsyncSession,
        assessment_id: int,
        production_score: Optional[float],
        quality_score: Optional[float],
        efficiency_score: Optional[float],
        overall_score: Optional[float],
        grade: Optional[str],
        comments: Optional[str],
    ) -> dict | None:
        assessment = await self.crud(db).get_assessment(assessment_id)
        if not assessment:
            return None

        if production_score is not None:
            assessment.production_score = Decimal(str(production_score))
        if quality_score is not None:
            assessment.quality_score = Decimal(str(quality_score))
        if efficiency_score is not None:
            assessment.efficiency_score = Decimal(str(efficiency_score))
        if overall_score is not None:
            assessment.overall_score = Decimal(str(overall_score))
        if grade is not None:
            assessment.grade = grade
        if comments is not None:
            assessment.comments = comments

        assessment = await self.crud(db).save_assessment(assessment)
        return serialize_assessment(assessment)

    async def get_assessment_statistics(self, db: AsyncSession) -> dict:
        assessments = await self.crud(db).list_all_assessments()
        total = len(assessments)

        grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0}
        for assessment in assessments:
            if assessment.grade in grade_dist:
                grade_dist[assessment.grade] += 1

        scores = [float(assessment.overall_score) for assessment in assessments if assessment.overall_score]
        avg_score = sum(scores) / len(scores) if scores else 0

        type_dist = {}
        for assessment in assessments:
            assessment_type = assessment.assessment_type or "其他"
            type_dist[assessment_type] = type_dist.get(assessment_type, 0) + 1

        return {
            "total": total,
            "avgScore": round(avg_score, 2),
            "gradeDistribution": grade_dist,
            "typeDistribution": type_dist,
        }


assessment_service = AssessmentService()
