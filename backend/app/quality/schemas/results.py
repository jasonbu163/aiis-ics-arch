"""质量结果、字段配置、分页与错误信封的 API 类型。"""
from datetime import datetime
from decimal import Decimal
import re
from time import time
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictBool, StrictInt, StrictStr, WithJsonSchema, field_validator, model_validator

from common.integration.envelope import BUSINESS_TIMEZONE
from app.quality.domain import QualityErrorCode, normalize_task_no

TaskNo = Annotated[str, BeforeValidator(normalize_task_no)]
TargetKey = Annotated[str, Field(min_length=1, max_length=64, pattern=r'^[A-Za-z0-9._-]+$')]
FieldKey = Annotated[str, Field(min_length=1, max_length=64, pattern=r'^[a-z][A-Za-z0-9_]*$')]
Value = StrictStr | StrictBool | StrictInt | Annotated[float, Field(strict=True, allow_inf_nan=False)] | None
InputValue = StrictStr | StrictBool | StrictInt | Annotated[Decimal, Field(strict=True), WithJsonSchema({'type': 'number'})] | None
T = TypeVar('T')


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Envelope(Contract, Generic[T]):
    code: int = 200
    message: str = 'success'
    data: T
    timestamp: int = Field(default_factory=lambda: int(time() * 1000))


class ErrorEnvelope(Contract):
    code: int
    message: str
    data: None = None
    errorCode: QualityErrorCode
    details: dict[str, str]
    timestamp: int = Field(default_factory=lambda: int(time() * 1000))


class Labels(Contract):
    zh: str = Field(alias='zh-CN', min_length=1, max_length=128)
    en: str = Field(alias='en-US', min_length=1, max_length=128)


class FieldDefinition(Contract):
    name: FieldKey
    labels: Labels
    type: Literal['string', 'number', 'boolean', 'link']
    unit: str | None = Field(default=None, max_length=64)
    enabled: StrictBool = True
    visible: StrictBool = True
    editable: StrictBool = False
    isNullable: StrictBool = True
    order: StrictInt = Field(default=0, ge=0, le=65535)
    linkText: str | None = Field(default=None, max_length=128)

    @field_validator('unit', 'linkText')
    @classmethod
    def optional_text(cls, value):
        if value is not None:
            value.encode('utf-8')
            return value.strip() or None
        return value

    @field_validator('labels')
    @classmethod
    def validate_labels(cls, labels):
        for name in (labels.zh, labels.en):
            name.encode('utf-8')
            if not name.strip():
                raise ValueError('labels cannot be blank')
        return labels

    @model_validator(mode='after')
    def links_only(self):
        if self.type != 'link' and self.linkText is not None:
            raise ValueError('linkText requires a link field')
        return self


class ConfigSnapshot(Contract):
    revision: StrictInt = Field(ge=1, le=2**53 - 1)
    definitions: list[FieldDefinition] = Field(max_length=100)


class Upsert(Contract):
    taskNo: TaskNo
    items: dict[FieldKey, InputValue] = Field(default_factory=dict, max_length=100)


class IntegrationUpsert(Upsert):
    targetKey: TargetKey | None = None


class Result(Contract):
    id: str
    taskNo: TaskNo
    targetKey: TargetKey | None
    items: dict[str, Value]
    createdAt: str
    updatedAt: str


class SaveResult(Contract):
    outcome: Literal['created', 'updated', 'unchanged']
    quality: Result


class CreatedResult(SaveResult):
    outcome: Literal['created']


class Page(Contract):
    items: list[Result]
    total: int
    page: int
    pageSize: int
    totalPages: int


class ReadPage(Page):
    fields: list[FieldDefinition]


class QueryFilters(Contract):
    taskNo: TaskNo | None = None
    targetKey: TargetKey | None = None
    createdFrom: datetime | None = None
    createdTo: datetime | None = None
    page: int = Field(default=1, ge=1, le=2**31 - 1)
    pageSize: int = Field(default=20, ge=1, le=100)

    @field_validator('createdFrom', 'createdTo', mode='before')
    @classmethod
    def local_time(cls, value):
        if value is None:
            return value
        if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:[0-5]\d)', value, re.ASCII
        ):
            raise ValueError('timestamp with an explicit offset required')
        try:
            converted = datetime.fromisoformat(value).astimezone(BUSINESS_TIMEZONE)
            if converted.year < 1000:
                raise ValueError
        except (ValueError, OverflowError):
            raise ValueError('invalid timestamp') from None
        return converted

    @model_validator(mode='after')
    def check_range(self):
        if self.createdFrom and self.createdTo and self.createdFrom >= self.createdTo:
            raise ValueError('createdFrom must precede createdTo')
        return self
