"""能源动态单价 API，沿用价格权限并独立校验项目配置管理员。"""
from typing import Annotated, Generic, TypeVar

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_serializer
from sqlalchemy.ext.asyncio import AsyncSession

from app.energy.api import energy_price
from app.energy.schemas.energy_pricing import (
    CurrentPrice, ItemKey, PricingHour, PricingHourWrite, PricingItem,
    PricingItemCreate, PricingItemPatch, PricingPage,
)
from app.energy.services import async_energy_pricing as service
from app.user.models.user import User
from common.exceptions import BusinessException
from common.response import ResponseModel
from core.deps import get_current_active_admin, require_permissions
from database import get_db


T = TypeVar("T")


class PricingResponse(ResponseModel, Generic[T]):
    data: T

    @field_serializer("data")
    def serialize_data(self, data):
        # 只转换模型字段别名，值对象中的业务键保持原样（如 water_feed）。
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json", by_alias=True)
        return [item.model_dump(mode="json", by_alias=True) for item in data]


class PricingRoute(energy_price.PriceRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def handle(request):
            try:
                return await handler(request)
            except BusinessException as exc:
                return JSONResponse(status_code=exc.code, content={
                    "code": exc.code, "message": exc.message, "data": None, "errorCode": exc.error_code.value,
                })
        return handle


router = APIRouter(
    prefix="/energy/pricing", tags=["Energy"], route_class=PricingRoute,
    responses={401: {"description": "Authentication required"}, 403: {"description": "Permission denied"}},
)
PriceReader = Annotated[User, Depends(require_permissions("energy-price-read"))]
PriceWriter = Annotated[User, Depends(require_permissions("energy-price-manage"))]
Admin = Annotated[User, Depends(get_current_active_admin)]
DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/items", response_model=PricingResponse[list[PricingItem]])
async def items(db: DB, actor: PriceReader):
    return PricingResponse[list[PricingItem]](data=await service.list_items(db))


@router.post("/items", response_model=PricingResponse[PricingItem],
             responses={409: {"description": "Pricing item key already exists"}})
async def create_item(payload: PricingItemCreate, db: DB, actor: PriceWriter, admin: Admin):
    return PricingResponse[PricingItem](data=await service.save_item(db, payload, actor.username))


@router.patch("/items/{itemKey:path}", response_model=PricingResponse[PricingItem])
async def update_item(request: Request, itemKey: ItemKey, payload: PricingItemPatch, db: DB, actor: PriceWriter, admin: Admin):
    # Browser URL parsing normalizes bare dot segments, even when singly escaped.
    raw_key = request.scope.get("raw_path", b"").rsplit(b"/", 1)[-1]
    if raw_key in {b"%252e", b"%252e%252e"}:
        itemKey = "." * (len(raw_key) // 5)
    return PricingResponse[PricingItem](data=await service.save_item(db, payload, actor.username, itemKey))


@router.get("/current", response_model=PricingResponse[list[CurrentPrice]])
async def current(db: DB, actor: PriceReader):
    return PricingResponse[list[CurrentPrice]](data=await service.current_prices(db, energy_price.utc_now()))


@router.get("/hours", response_model=PricingResponse[PricingPage])
async def hours(
    request: Request, db: DB, actor: PriceReader, date: str | None = None,
    page: int = Query(1, ge=1), page_size: int = Query(24, alias="pageSize", ge=1, le=100),
):
    day = energy_price.history_day(request, date)
    return PricingResponse[PricingPage](data=await service.price_history(db, page, page_size, day))


@router.post("/hours", response_model=PricingResponse[PricingHour])
async def save_hour(payload: PricingHourWrite, db: DB, actor: PriceWriter):
    observed = energy_price.observed_time(payload.observed_at, energy_price.utc_now())
    return PricingResponse[PricingHour](data=await service.save_hour(db, payload, actor.username, observed))
