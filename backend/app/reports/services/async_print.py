"""
文件路径: /backend/app/reports/services/async_print.py
功能描述: 打印标签异步服务
主要功能:
    - 编排打印列表和打印数据查询
    - 创建打印提交记录
"""
import datetime
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.crud.async_print import PrintCRUD
from app.reports.models.reports import PrintRecord


def serialize_print_performance(performance) -> dict:
    return {
        "id": performance.id,
        "coilNo": performance.coil_no,
        "grade": performance.grade,
        "spec": performance.spec,
        "weight": float(performance.weight) if performance.weight else 0,
        "totalLength": float(performance.total_length) if performance.total_length else 0,
        "outerDiameter": float(performance.diameter) if performance.diameter else 0,
        "productionDate": performance.production_date.isoformat() if performance.production_date else None,
        "endTime": performance.end_time.isoformat() if performance.end_time else None,
    }


class PrintService:
    """打印标签业务编排层。"""

    @staticmethod
    def crud(db: AsyncSession) -> PrintCRUD:
        return PrintCRUD(db)

    async def list_print_items(self, db: AsyncSession, page: int, page_size: int) -> dict:
        crud = self.crud(db)
        performances = await crud.list_performances(page, page_size)
        total = await crud.count_performances()

        return {
            "items": [serialize_print_performance(performance) for performance in performances],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_print_data(self, db: AsyncSession, performance_id: int, operator_name: str) -> dict | None:
        performance = await self.crud(db).get_performance(performance_id)
        if not performance:
            return None

        thickness = None
        width = None
        if performance.spec:
            try:
                parts = re.split(r"[×*xX]", performance.spec)
                if len(parts) >= 2:
                    thickness = float(parts[0])
                    width = float(parts[1])
            except (ValueError, IndexError):
                pass

        return {
            "coilNo": performance.coil_no,
            "grade": performance.grade,
            "spec": performance.spec,
            "weight": float(performance.weight) if performance.weight else 0,
            "totalLength": float(performance.total_length) if performance.total_length else 0,
            "outerDiameter": float(performance.diameter) if performance.diameter else 0,
            "thickness": thickness,
            "width": width,
            "operator": operator_name,
            "shift": "dayShift",
            "entryTension": 15.5,
            "entryLoopTension": 12.0,
            "furnaceTension": 10.0,
            "exitLoopTension": 12.0,
            "exitTension": 15.5,
            "entrySpeed": 25.0,
            "furnaceSpeed": 20.0,
            "exitSpeed": 25.0,
            "furnaceTemp": "900-920",
            "residenceTime": 180,
            "dewPoint": -45,
            "oxygenContent": "≤10ppm",
        }

    async def submit_print(self, db: AsyncSession, performance_ids: list[int], operator_id: int) -> int:
        records = [
            PrintRecord(
                performance_id=performance_id,
                print_type="label",
                print_status="completed",
                print_time=datetime.datetime.now(),
                operator_id=operator_id,
            )
            for performance_id in performance_ids
        ]
        await self.crud(db).create_print_records(records)
        return len(records)


print_service = PrintService()
