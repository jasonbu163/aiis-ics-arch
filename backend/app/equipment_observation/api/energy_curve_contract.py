"""能耗曲线组的严格请求、返回及 OpenAPI 错误声明。"""
from typing import Annotated, Literal

from pydantic import Field

from ..schemas import Input, Key, Order


CurveTitle = Annotated[str, Field(max_length=128)]


class EnergyCurveSeries(Input):
    metric_key: Key
    enabled: bool
    line_style: Literal["solid", "dashed"]


class EnergyCurveCreate(Input):
    curve_group_key: Key
    title_zh: CurveTitle = ""
    title_en: CurveTitle = ""
    meter_id: Key
    group_key: Key
    sort_order: Order
    enabled: bool
    series: list[EnergyCurveSeries]


class EnergyCurveData(EnergyCurveCreate):
    title_zh: CurveTitle
    title_en: CurveTitle


class EnergyCurvePatch(Input):
    title_zh: CurveTitle = Field(default_factory=str)
    title_en: CurveTitle = Field(default_factory=str)
    meter_id: Key = Field(default_factory=str)
    group_key: Key = Field(default_factory=str)
    sort_order: Order = 0
    enabled: bool = True
    series: list[EnergyCurveSeries] = Field(default_factory=list)


class EnergyCurveResponse(Input):
    code: int
    message: str
    data: EnergyCurveData


class EnergyCurveListResponse(Input):
    code: int
    message: str
    data: list[EnergyCurveData]


class EnergyCurveError(Input):
    code: int
    message: str
    data: None
    error_code: str


CURVE_ERRORS = {
    401: {"description": "Missing or invalid user Bearer", "model": EnergyCurveError},
    403: {"description": "Permission or meter access denied", "model": EnergyCurveError},
    422: {"description": "Invalid fields, metric references or curve units", "model": EnergyCurveError},
    503: {"description": "Energy data unavailable or commit result unknown", "model": EnergyCurveError},
}
