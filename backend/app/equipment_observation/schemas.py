"""管理 API 与写入正文的严格输入模型。"""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Input(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False,
                              extra="forbid", strict=True)


Key = Annotated[str, Field(min_length=1, max_length=64)]
Title = Annotated[str, Field(min_length=1, max_length=128)]
Category = Annotated[str, Field(min_length=1, max_length=32)]
Order = Annotated[int, Field(ge=-(2**63), le=2**63 - 1)]


class Metric(Input):
    metric_key: Key
    source_group_key: Key
    category: Category
    name_zh: Title
    name_en: Title
    value_type: Literal["number", "boolean", "string"]
    unit: Annotated[str, Field(max_length=24)] | None = None
    decimals: Annotated[int, Field(ge=0, le=12)] | None = None


class Group(Input):
    group_key: Key
    category: Literal["production", "cleaning", "temperature", "drive"]
    name_zh: Title
    name_en: Title
    enabled: bool
    sort_order: Order


class GroupPatch(Input):
    category: Literal["production", "cleaning", "temperature", "drive"] | None = None
    name_zh: Title | None = None
    name_en: Title | None = None
    enabled: bool | None = None
    sort_order: Order | None = None


class EnergyMetric(Input):
    meter_id: Key
    group_key: Key
    metric_key: Key
    slot_no: Annotated[int, Field(ge=1, le=100)]
    name_zh: Title
    name_en: Title
    value_type: Literal["number"]
    quantity_key: Key
    measurement_mode: Literal["cumulative", "interval", "instantaneous"]
    unit: Annotated[str, Field(max_length=24)] | None = None
    decimals: Annotated[int, Field(ge=0, le=12)] | None = None
    enabled: bool
    list_visible: bool = False
    list_order: Annotated[int, Field(ge=0, le=2**31 - 1)] | None = None
    rules: dict = Field(default_factory=dict)


class EnergyMetricPatch(Input):
    slot_no: Annotated[int, Field(ge=1, le=100)] | None = None
    name_zh: Title | None = None
    name_en: Title | None = None
    value_type: Literal["number"] | None = None
    quantity_key: Key | None = None
    measurement_mode: Literal["cumulative", "interval", "instantaneous"] | None = None
    unit: Annotated[str, Field(max_length=24)] | None = None
    decimals: Annotated[int, Field(ge=0, le=12)] | None = None
    enabled: bool | None = None
    list_visible: bool | None = None
    list_order: Annotated[int, Field(ge=0, le=2**31 - 1)] | None = None
    rules: dict | None = None


class MetricPatch(Input):
    name_zh: Title | None = None
    name_en: Title | None = None
    unit: Annotated[str, Field(max_length=24)] | None = None
    decimals: Annotated[int, Field(ge=0, le=12)] | None = None
    value_type: Literal["number", "boolean", "string"] | None = None


class Slot(Input):
    target: Literal["latest", "history"]
    group_key: Key
    slot_no: Annotated[int, Field(ge=1, le=100)]
    metric_key: Key
    enabled: bool


class SlotPatch(Input):
    enabled: bool | None = None
    list_visible: bool | None = None
    list_order: Annotated[int, Field(ge=0, le=2**31 - 1)] | None = None


class DisplayItem(Input):
    metric_key: Key
    enabled: bool


class CurveSeries(DisplayItem):
    line_style: Literal["solid", "dashed"] = "solid"


class Card(Input):
    card_key: Key
    page_key: Literal["production", "cleaning", "temperature", "drive"]
    title_zh: Title
    title_en: Title
    enabled: bool
    sort_order: Order
    items: list[DisplayItem]


class Curve(Input):
    curve_group_key: Key
    category: Literal["temperature", "drive", "cleaning"]
    title_zh: Title
    title_en: Title
    enabled: bool
    sort_order: Order
    series: list[CurveSeries]


class Remark(Input):
    remark: str | None = None


class HistoryReview(Input):
    remark: str | None = None
    review_mark: Literal["abnormal", "reviewed"] | None = None


class CardPatch(Input):
    page_key: Literal["production", "cleaning", "temperature", "drive"] | None = None
    title_zh: Title | None = None
    title_en: Title | None = None
    enabled: bool | None = None
    sort_order: Order | None = None
    items: list[DisplayItem] | None = None


class CurvePatch(Input):
    category: Literal["temperature", "drive", "cleaning"] | None = None
    title_zh: Title | None = None
    title_en: Title | None = None
    enabled: bool | None = None
    sort_order: Order | None = None
    series: list[CurveSeries] | None = None
