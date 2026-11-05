"""严格查询合同：未知、重复和互斥参数均失败。"""
from typing import Literal
from pydantic import Field, model_validator
from .source import StrictSchema, Id, Time

class LatestQuery(StrictSchema):
    plc_id: Id
    db_number: int|None=Field(default=None,ge=1,le=65535)
    group_id: Id|None=None
    point_id: Id|None=None
    limit: int=Field(default=100,ge=1,le=500)
    page_cursor: str|None=None

class HistoryQuery(LatestQuery):
    mode: Literal['changes','range']
    instance_id: Id|None=None
    source_generation: Id|None=None
    start: Literal['earliest','tail']|None=None
    cursor: str|None=None
    from_: Time|None=Field(default=None,alias='from')
    to: Time|None=None
    view: Literal['projection','original']='projection'

    @model_validator(mode='after')
    def modes(self):
        if self.mode=='changes':
            if self.from_ or self.to or self.page_cursor or self.view=='original' or bool(self.start)==bool(self.cursor): raise ValueError('changes parameters')
        else:
            if self.start or self.cursor or not self.from_ or not self.to or self.from_>=self.to: raise ValueError('range parameters')
            if self.view=='original' and (self.point_id or self.group_id): raise ValueError('original filters')
        return self
