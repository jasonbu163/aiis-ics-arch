"""PLC 事实 v2 严格请求 Schema；字段名与跨运行时合同一致。"""
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


Identifier = Annotated[str, Field(min_length=1, max_length=128, json_schema_extra={'x-utf8-max-bytes': 128})]
ObservedTime = Annotated[str, Field(pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?\+08:00$')]
DataType = Annotated[str, Field(pattern=r'^(?:BOOL|BYTE|USINT|INT|UINT|WORD|DINT|UDINT|DWORD|REAL|CHAR|STRING\[(?:[1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-4])\])$')]


class PointV2In(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)

    point_id: Identifier
    name: str = Field(default='', max_length=100, json_schema_extra={'x-utf8-max-bytes': 100})
    data_type: DataType
    value: Any
    quality: Literal['good', 'bad']
    observed_at: ObservedTime
    reason: str | None = Field(default=None, max_length=128, json_schema_extra={'x-utf8-max-bytes': 128})


class SampleV2In(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)

    contract_version: Literal['plc-facts/v2']
    instance_id: Identifier
    sample_id: Identifier
    plc_id: Identifier
    db_number: int = Field(ge=1, le=65535)
    group_id: Identifier | None = None
    config_revision: Identifier | None = None
    source_generation: Identifier
    source_seq: str = Field(pattern=r'^[1-9][0-9]*$', max_length=19)
    points: list[PointV2In] = Field(min_length=1, max_length=512)


class ReceiptData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    contract_version: Literal['plc-facts/v2']
    instance_id: str
    sample_id: str
    status: Literal['committed']
    outcome: Literal['created', 'duplicate']


class ReceiptOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: ReceiptData


class FailureOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    code: int
    message: str
    data: None = None
    error_code: str


class ResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OptionItem(ResponseModel):
    plc_id: str
    db_numbers: list[int]


class LatestItem(ResponseModel):
    point_id: str
    name: str
    data_type: str
    value: Any
    quality: Literal['good', 'bad']
    reason: str | None
    observed_at: str
    instance_id: str
    source_generation: str
    source_seq: str
    sample_id: str
    source_type: Literal['daa', 'external']


class LatestBrowseItem(LatestItem):
    plc_id: str
    db_number: int


class SampleSummary(ResponseModel):
    id: str
    instance_id: str
    sample_id: str
    plc_id: str
    db_number: int
    group_id: str | None
    config_revision: str | None
    source_type: Literal['daa', 'external'] | None
    source_generation: str
    source_seq: str
    sampled_at: str
    stored_at: str
    point_count: int


class SampleDetail(SampleSummary):
    points: list[PointV2In]


class OptionsData(ResponseModel):
    items: list[OptionItem]


class LatestData(ResponseModel):
    items: list[LatestItem]


class HistoryData(ResponseModel):
    items: list[SampleSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class LatestBrowseData(ResponseModel):
    items: list[LatestBrowseItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class OptionsOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: OptionsData


class LatestOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: LatestData


class LatestBrowseOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: LatestBrowseData


class HistoryOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: HistoryData


class DetailOut(BaseModel):
    code: Literal[200] = 200
    message: Literal['success'] = 'success'
    data: SampleDetail
