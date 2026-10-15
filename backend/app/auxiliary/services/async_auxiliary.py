"""
文件路径: /backend/app/auxiliary/services/async_auxiliary.py
功能描述: 辅助管理异步业务服务
主要功能:
    - 编排班组管理业务
    - 编排班次管理业务
    - 编排停机记录业务
    - 编排排班规则业务
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.auxiliary.crud.async_auxiliary import AuxiliaryCRUD
from app.auxiliary.schemas.auxiliary_in import (
    ShiftCreate,
    ShiftRuleUpdate,
    ShiftTeamCreate,
    ShiftTeamUpdate,
    ShiftUpdate,
    StopRecordCreate,
    StopRecordUpdate,
)
from common.data_keys import normalize_downtime_reason
from common.exceptions import BusinessException
from app.auxiliary.error_codes import AuxiliaryErrorCode
from sqlalchemy.exc import IntegrityError


class AuxiliaryService:
    """辅助管理业务编排层。"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.crud = AuxiliaryCRUD(db)

    async def list_shift_teams(self, page: int, page_size: int):
        return await self.crud.list_shift_teams(page=page, page_size=page_size)

    async def get_shift_team(self, id: int):
        return await self.crud.get_shift_team(id)

    async def create_shift_team(self, data: ShiftTeamCreate):
        try:
            result = await self.crud.create_shift_team(data.model_dump())
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def update_shift_team(self, id: int, data: ShiftTeamUpdate):
        try:
            result = await self.crud.update_shift_team(id, data.model_dump(exclude_unset=True))
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def delete_shift_team(self, id: int) -> bool:
        try:
            result = await self.crud.delete_shift_team(id)
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def list_shifts(self, page: int, page_size: int, team_id: int | None, start_date=None, end_date=None):
        items, total = await self.crud.list_shifts(
            page=page,
            page_size=page_size,
            team_id=team_id,
            start_date=start_date,
            end_date=end_date,
        )
        return items, total

    async def get_shift(self, id: int):
        return await self.crud.get_shift(id)

    async def create_shift(self, data: ShiftCreate):
        try:
            result = await self.crud.create_shift(data.model_dump())
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def update_shift(self, id: int, data: ShiftUpdate):
        try:
            result = await self.crud.update_shift(id, data.model_dump(exclude_unset=True))
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def delete_shift(self, id: int) -> bool:
        try:
            result = await self.crud.delete_shift(id)
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def get_shift_rule(self):
        return await self.crud.get_active_shift_rule()

    async def update_shift_rule(self, id: int, data: ShiftRuleUpdate):
        try:
            result = await self.crud.update_shift_rule(id, data.model_dump(exclude_unset=True))
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def list_stop_records(
        self,
        page: int,
        page_size: int,
        status: str | None,
        shift: str | None = None,
        start_time=None,
        end_time=None,
        stop_type: str | None = None,
    ):
        return await self.crud.list_stop_records(
            page=page,
            page_size=page_size,
            status=status,
            shift=shift,
            start_time=start_time,
            end_time=end_time,
            stop_type=normalize_downtime_reason(stop_type),
        )

    async def get_stop_record(self, id: int):
        return await self.crud.get_stop_record(id)

    async def create_stop_record(self, data: StopRecordCreate):
        payload = data.model_dump()
        payload["stop_type"] = normalize_downtime_reason(payload.get("stop_type"))
        try:
            result = await self.crud.create_stop_record(payload)
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def update_stop_record(self, id: int, data: StopRecordUpdate):
        payload = data.model_dump(exclude_unset=True)
        if "stop_type" in payload:
            payload["stop_type"] = normalize_downtime_reason(payload["stop_type"])
        try:
            result = await self.crud.update_stop_record(id, payload)
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def delete_stop_record(self, id: int) -> bool:
        try:
            result = await self.crud.delete_stop_record(id)
            await self.db.commit()
            return result
        except IntegrityError as exc:
            await self.db.rollback()
            raise BusinessException(AuxiliaryErrorCode.CONFLICT) from exc
        except Exception:
            await self.db.rollback()
            raise
