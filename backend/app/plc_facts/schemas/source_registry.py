"""管理员 PLC 来源登记请求与响应合同。"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from pydantic.alias_generators import to_camel

from ..v2_domain import V2Error, identifier


class RegistrationIn(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)
    source_type: Literal['daa', 'external']
    instance_id: str
    plc_id: str
    source_generation: str

    @field_validator('instance_id', 'plc_id', 'source_generation')
    @classmethod
    def valid_identifier(cls, value):
        try:
            return identifier(value)
        except V2Error:
            raise ValueError('invalid identifier') from None


class SourceOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    source_type: Literal['daa', 'external']
    instance_id: str
    plc_id: str
    source_generation: str
    registration_revision: str
    created_at: str
    updated_at: str


class PageData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    items: list[SourceOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class PageOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: PageData


class RegistrationData(BaseModel):
    outcome: Literal['created', 'updated', 'replaced', 'unchanged', 'deleted']
    source: SourceOut


class RegistrationOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: RegistrationData


class FailureOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    code: int
    message: str
    data: None = None
    error_code: str


class ExpectedSource(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)
    instance_id: str
    source_generation: str
    registration_revision: str

    @field_validator('instance_id', 'source_generation', 'registration_revision')
    @classmethod
    def valid_identifier(cls, value):
        try:
            return identifier(value)
        except V2Error:
            raise ValueError('invalid identifier') from None


class ReplacementSource(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)
    source_type: Literal['daa', 'external']
    instance_id: str
    source_generation: str

    @field_validator('instance_id', 'source_generation')
    @classmethod
    def valid_identifier(cls, value):
        try:
            return identifier(value)
        except V2Error:
            raise ValueError('invalid identifier') from None


class UpdateIn(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)
    action: Literal['edit', 'takeover', 'delete']
    plc_id: str
    expected: ExpectedSource
    source_type: Literal['daa', 'external'] | None = None
    replacement: ReplacementSource | None = None
    confirm_takeover: bool | None = None
    confirm_delete: bool | None = None

    @field_validator('plc_id')
    @classmethod
    def valid_identifier(cls, value):
        try:
            return identifier(value)
        except V2Error:
            raise ValueError('invalid identifier') from None

    @model_validator(mode='after')
    def validate_action(self):
        if self.action == 'takeover':
            if (self.replacement is None or self.confirm_takeover is not True
                    or self.source_type is not None or self.confirm_delete is not None):
                raise ValueError('confirmed replacement required')
        elif self.action == 'edit':
            if (self.source_type is None or self.replacement is not None
                    or self.confirm_takeover is not None or self.confirm_delete is not None):
                raise ValueError('source type required for edit')
        elif (self.confirm_delete is not True or self.source_type is not None
              or self.replacement is not None or self.confirm_takeover is not None):
            raise ValueError('confirmed deletion required')
        return self
