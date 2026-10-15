"""能源价格输入校验与局部 JSON number 输出合同。"""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
import re
import math
from pydantic import ConfigDict, Field, field_serializer, field_validator, model_validator
from common.schema_base import ApiSchema


class PriceCreate(ApiSchema):
    model_config = ConfigDict(extra="forbid")
    observed_at: datetime | None = None
    electric_price: Decimal
    hydrogen_price: Decimal
    argon_price: Decimal
    electric_remark: str | None = Field(default=None, max_length=500)
    hydrogen_remark: str | None = Field(default=None, max_length=500)
    argon_remark: str | None = Field(default=None, max_length=500)
    remark: str | None = Field(default=None, max_length=2000)

    @field_validator("observed_at", mode="before")
    @classmethod
    def validate_observed_at(cls, value):
        if value is None:
            return None
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:\d{2})", value):
            raise ValueError("invalid_observed_at")
        try:
            instant = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
            canonical_hour_start(instant)
            return instant
        except (ValueError, OverflowError) as exc:
            raise ValueError("invalid_observed_at") from exc

    @model_validator(mode="before")
    @classmethod
    def reject_nonfinite_json_numbers(cls, values):
        # Python's JSON parser accepts non-standard NaN/Infinity. Keep validation
        # error inputs JSON-safe so FastAPI's existing 422 handler can serialize them.
        def safe_input(value):
            if isinstance(value, Decimal):
                return {"decimal": str(value)}
            if isinstance(value, float) and not math.isfinite(value):
                return {"nonfinite": str(value)}
            if isinstance(value, dict):
                return {key: safe_input(item) for key, item in value.items()}
            if isinstance(value, list):
                return [safe_input(item) for item in value]
            return value
        if isinstance(values, dict):
            # Preserve numeric lexemes as exact decimal strings only for price fields.
            # Other decimal-valued fields remain invalid and JSON-safe in 422 details.
            prices = {"electric_price", "hydrogen_price", "argon_price",
                      "electricPrice", "hydrogenPrice", "argonPrice"}
            values = {key: str(value) if key in prices and isinstance(value, Decimal) else value
                      for key, value in values.items()}
        return safe_input(values)

    @field_validator("electric_price", "hydrogen_price", "argon_price", mode="before")
    @classmethod
    def validate_price(cls, value):
        if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
            raise ValueError("invalid_price")
        if isinstance(value, str) and not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value):
            raise ValueError("invalid_price")
        try:
            number = Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError("invalid_price") from exc
        if not number.is_finite() or not 0 <= number <= Decimal("999999.9999"):
            raise ValueError("invalid_price")
        # Decimal tuple examination avoids context rounding, including long trailing zeros.
        digits = number.as_tuple().digits
        exponent = number.as_tuple().exponent
        trailing = 0
        for digit in reversed(digits):
            if digit != 0:
                break
            trailing += 1
        if number != 0 and exponent + trailing < -4:
            raise ValueError("invalid_price_precision")
        return number

    @field_validator("electric_remark", "hydrogen_remark", "argon_remark", "remark", mode="before")
    @classmethod
    def normalize_remark(cls, value):
        return None if value == "" else value


class PriceRecord(ApiSchema):
    id: int
    electric_price: Decimal
    hydrogen_price: Decimal
    argon_price: Decimal
    electric_remark: str | None
    hydrogen_remark: str | None
    argon_remark: str | None
    remark: str | None
    operator: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("electric_price", "hydrogen_price", "argon_price")
    def price_number(self, value: Decimal) -> float:
        return float(value)


class HourlyPriceRecord(PriceRecord):
    observed_at: datetime
    hour_start: datetime

    @field_serializer("observed_at", "hour_start", "created_at", "updated_at")
    def business_time(self, value: datetime) -> str:
        # MySQL DATETIME is deliberately stored as naive UTC in this module only.
        return value.replace(tzinfo=timezone.utc).astimezone(OUTPUT_ZONE).isoformat() if value.tzinfo is None else value.astimezone(OUTPUT_ZONE).isoformat()


class PricePage(ApiSchema):
    items: list[HourlyPriceRecord]
    total: int
    page: int
    page_size: int


BUSINESS_ZONE = ZoneInfo("Asia/Shanghai")
# Stable minute-offset ISO output remains browser parseable for historical LMT too.
OUTPUT_ZONE = timezone(timedelta(hours=8))


def parse_history_date(value: str) -> date:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("invalid_date")
    return date.fromisoformat(value)


def history_bounds(day: date):
    # Clamp only the unrepresentable edge of year 1; persisted times start at 1000.
    def utc_midnight(value):
        try:
            return datetime.combine(value, datetime.min.time(), BUSINESS_ZONE).astimezone(timezone.utc).replace(tzinfo=None)
        except OverflowError:
            return datetime.min
    start = utc_midnight(day)
    end = utc_midnight(day + timedelta(days=1)) if day < date.max else None
    return start, end


def canonical_hour_start(observed_at: datetime) -> datetime:
    """规范民用小时并校验事件/派生桶均可写入 MySQL DATETIME。"""
    instant = observed_at.astimezone(timezone.utc)
    hour_start = instant.astimezone(BUSINESS_ZONE).replace(
        minute=0, second=0, microsecond=0, fold=0,
    ).astimezone(timezone.utc)
    if instant.year < 1000 or hour_start.year < 1000:
        raise ValueError("unpersistable_observed_at")
    return hour_start
