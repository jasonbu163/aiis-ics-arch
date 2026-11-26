"""动态项目及精确小时价格的请求与响应合同。"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, field_serializer, field_validator, model_validator

from app.energy.schemas.energy_price import (
    OUTPUT_ZONE, PriceInput, exact_price, json_safe_validation_input,
)
from common.schema_base import ApiSchema


ItemKey = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]
ItemText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]
SortOrder = Annotated[int, Field(strict=True, ge=-(2**53 - 1), le=2**53 - 1)]


class PricingItemPatch(ApiSchema):
    model_config = ConfigDict(extra="forbid")
    name_zh: ItemText | None = None
    name_en: ItemText | None = None
    unit: ItemText | None = None
    sort_order: SortOrder | None = None
    enabled: bool | None = Field(default=None, strict=True)

    @field_validator("name_zh", "name_en", mode="before")
    @classmethod
    def optional_name(cls, value):
        return None if isinstance(value, str) and not value.strip() else value

    @model_validator(mode="before")
    @classmethod
    def json_safe(cls, values):
        return json_safe_validation_input(values)


class PricingItemCreate(PricingItemPatch):
    item_key: ItemKey
    unit: ItemText
    sort_order: SortOrder = 0
    enabled: bool = Field(default=True, strict=True)

    @model_validator(mode="after")
    def has_name(self):
        if self.name_zh is None and self.name_en is None:
            raise ValueError("pricing_name_required")
        return self


class PriceValueIn(ApiSchema):
    model_config = ConfigDict(extra="forbid")
    price: Decimal
    remark: str | None = Field(default=None, max_length=500)

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, value):
        return exact_price(value)

    @field_validator("remark", mode="before")
    @classmethod
    def normalize_remark(cls, value):
        return None if value == "" else value


class PricingHourWrite(PriceInput):
    items: dict[ItemKey, PriceValueIn] = Field(min_length=1)
    remark: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def json_safe(cls, values):
        if isinstance(values, dict) and isinstance(values.get("items"), dict):
            items = {}
            for key, item in values["items"].items():
                key = key.strip()
                if key in items:
                    raise ValueError("duplicate_pricing_item")
                if isinstance(item, dict) and isinstance(item.get("price"), Decimal):
                    item = {**item, "price": str(item["price"])}
                items[key] = item
            values = {**values, "items": items}
        return json_safe_validation_input(values)

    @field_validator("remark", mode="before")
    @classmethod
    def normalize_remark(cls, value):
        return None if value == "" else value


class PricingItem(ApiSchema):
    item_key: str
    name_zh: str | None
    name_en: str | None
    unit: str
    sort_order: int
    enabled: bool


class PriceValue(ApiSchema):
    price: Decimal | None = None
    remark: str | None = None
    observed_at: datetime | None = None
    updated_at: datetime | None = None
    operator: str | None = None

    @field_serializer("price")
    def price_number(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None

    @field_serializer("observed_at", "updated_at")
    def business_time(self, value: datetime | None) -> str | None:
        return value.replace(tzinfo=OUTPUT_ZONE).isoformat() if value is not None else None


class CurrentPrice(PriceValue):
    item_key: str
    name_zh: str | None
    name_en: str | None
    unit: str


class PricingHour(ApiSchema):
    hour_start: datetime
    remark: str | None
    values: dict[str, PriceValue]

    @field_serializer("hour_start")
    def business_time(self, value: datetime) -> str:
        return value.replace(tzinfo=OUTPUT_ZONE).isoformat()


class PricingPage(ApiSchema):
    columns: list[PricingItem]
    items: list[PricingHour]
    total: int
    page: int
    page_size: int
