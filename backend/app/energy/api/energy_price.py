"""能源价格三接口：精确 JSON 数字解析、认证与独立 read/manage 权限边界。"""
import json
from decimal import Decimal
from datetime import datetime, timezone
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.models.user import User
from app.energy.schemas.energy_price import PriceCreate, parse_history_date
from app.energy.services import async_energy_price as service
from common.response import ResponseModel
from core.deps import require_permissions
from database import get_db

class PriceJSONRequest(Request):
    """价格模块保留原始 JSON number 精度，避免 float 先行舍入。"""

    async def json(self):
        return json.loads(await self.body(), parse_float=Decimal)


class PriceRoute(APIRoute):
    """只替换本模块请求解析；校验与异常继续由 FastAPI 处理。"""

    def get_route_handler(self):
        handler = super().get_route_handler()

        async def exact_price_request(request: Request) -> Response:
            return await handler(PriceJSONRequest(request.scope, request.receive))

        return exact_price_request


router = APIRouter(
    prefix="/energy", tags=["Auxiliary - Energy Price"], route_class=PriceRoute,
)


@router.get("/current", response_model=ResponseModel)
async def current_price(
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permissions("energy-price-read")),
):
    return ResponseModel(data=await service.current_price(db, utc_now()))


@router.get("", response_model=ResponseModel)
async def price_history(
    request: Request,
    date: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="pageSize", ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permissions("energy-price-read")),
):
    day = None
    if "date" in request.query_params:
        try:
            if len(request.query_params.getlist("date")) != 1:
                raise ValueError("duplicate_date")
            day = parse_history_date(date)
        except ValueError:
            raise RequestValidationError([{"type": "value_error", "loc": ("query", "date"), "msg": "invalid_date", "input": date}])
    return ResponseModel(data=await service.price_history(db, page, page_size, day))


@router.post("", response_model=ResponseModel)
async def save_price(
    payload: PriceCreate,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permissions("energy-price-manage")),
):
    now = utc_now()
    observed_at = payload.observed_at if payload.observed_at is not None else now
    if observed_at > now:
        raise RequestValidationError([{"type": "value_error", "loc": ("body", "observedAt"), "msg": "future_observed_at", "input": observed_at.isoformat()}])
    return ResponseModel(data=await service.save_price(db, payload, actor.username, observed_at))


def utc_now():
    """每次请求由 API 捕获一次，便于固定钟验证。"""
    return datetime.now(timezone.utc)
