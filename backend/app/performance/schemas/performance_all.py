"""
文件路径: /backend/app/performance/schemas/performance_all.py
功能描述: 生产实绩数据验证模型定义
主要功能:
    - 定义实绩创建、更新、响应的数据结构
    - 过程数据模型（温度、张力、速度）
    - 下推记录模型
    - 分卷数据模型
"""
from pydantic import Field, ConfigDict
from typing import Optional, List
# from datetime import datetime
import datetime
from decimal import Decimal
from common.schema_base import ApiSchema


class PerformanceBase(ApiSchema):
    plan_id: int
    coil_no: str
    parent_coil_no: Optional[str] = None
    grade: str
    spec: Optional[str] = None
    weight: Decimal
    production_date: datetime.date


class PerformanceCreate(PerformanceBase):
    total_length: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    density: Optional[Decimal] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    output_quantity: Optional[Decimal] = Decimal("0")
    qualified_quantity: Optional[Decimal] = Decimal("0")
    efficiency_rate: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    is_split: Optional[bool] = False
    remark: Optional[str] = None


class PerformanceUpdate(ApiSchema):
    total_length: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    density: Optional[Decimal] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    output_quantity: Optional[Decimal] = None
    qualified_quantity: Optional[Decimal] = None
    efficiency_rate: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    is_split: Optional[bool] = None
    remark: Optional[str] = None
    spec: Optional[str] = None
    grade: Optional[str] = None
    weight: Optional[Decimal] = None


class PerformanceResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    plan_id: Optional[int] = None
    coil_no: str
    parent_coil_no: Optional[str] = None
    grade: Optional[str] = None
    spec: Optional[str] = None
    weight: Optional[Decimal] = None
    total_length: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    density: Optional[Decimal] = None
    production_date: datetime.date
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    output_quantity: Decimal
    qualified_quantity: Decimal
    efficiency_rate: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    collected_weight: Optional[Decimal] = None
    manual_override_weight: Optional[Decimal] = None
    effective_weight: Optional[Decimal] = None
    effective_weight_source: Optional[str] = None
    manual_override_by_id: Optional[int] = None
    manual_override_at: Optional[datetime.datetime] = None
    manual_override_reason: Optional[str] = None
    total_duration_seconds: Optional[int] = None
    total_duration_source: Optional[str] = None
    is_split: bool = False
    remark: Optional[str] = None
    device_id: Optional[int] = None
    observation_status: Optional[str] = None
    record_source: Optional[str] = None
    first_observed_at: Optional[datetime.datetime] = None
    last_observed_at: Optional[datetime.datetime] = None
    first_raw_snapshot_id: Optional[int] = None
    last_raw_snapshot_id: Optional[int] = None
    plc_key: Optional[str] = None
    db_number: Optional[int] = None
    group_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class ProcessTemperatureBase(ApiSchema):
    zone: str
    set_temp: Optional[Decimal] = None
    max_temp: Optional[Decimal] = None
    min_temp: Optional[Decimal] = None
    avg_temp: Optional[Decimal] = None
    duration: Optional[int] = None


class ProcessTemperatureCreate(ProcessTemperatureBase):
    performance_id: int


class ProcessTemperatureResponse(ProcessTemperatureBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    performance_id: int
    record_time: datetime.datetime
    created_at: datetime.datetime


class ProcessTensionBase(ApiSchema):
    zone: str
    set_tension: Optional[Decimal] = None
    avg_tension: Optional[Decimal] = None
    max_tension: Optional[Decimal] = None
    min_tension: Optional[Decimal] = None


class ProcessTensionCreate(ProcessTensionBase):
    performance_id: int


class ProcessTensionResponse(ProcessTensionBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    performance_id: int
    record_time: datetime.datetime
    created_at: datetime.datetime


class ProcessSpeedBase(ApiSchema):
    zone: str
    set_speed: Optional[Decimal] = None
    avg_speed: Optional[Decimal] = None
    max_speed: Optional[Decimal] = None


class ProcessSpeedCreate(ProcessSpeedBase):
    performance_id: int


class ProcessSpeedResponse(ProcessSpeedBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    performance_id: int
    record_time: datetime.datetime
    created_at: datetime.datetime


class PushDownRecordBase(ApiSchema):
    push_down_type: str
    target_system: Optional[str] = None


class PushDownRecordCreate(PushDownRecordBase):
    performance_id: int
    operator_id: Optional[int] = None


class PushDownRecordResponse(PushDownRecordBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    performance_id: int
    status: str
    message: Optional[str] = None
    operator_id: Optional[int] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None


class ProcessDataResponse(ApiSchema):
    temperature: List[ProcessTemperatureResponse] = []
    tension: List[ProcessTensionResponse] = []
    speed: List[ProcessSpeedResponse] = []


class SplitBase(ApiSchema):
    performance_id: int
    split_no: str
    weight: Decimal
    spec: str


class SplitCreate(SplitBase):
    pass


class SplitUpdate(ApiSchema):
    split_no: Optional[str] = None
    weight: Optional[Decimal] = None
    spec: Optional[str] = None


class SplitResponse(SplitBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    created_at: datetime.datetime
