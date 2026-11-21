"""采集消费者请求及状态响应的版本化字段。"""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .v2 import Identifier, ResponseModel, SampleDetail

UuidText = Annotated[str, Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')]
HashText = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
SequenceText = Annotated[str, Field(pattern=r'^[1-9][0-9]{0,18}$')]
DbNumber = Annotated[int, Field(ge=1, le=65535)]
Permission = Literal['create', 'read', 'run', 'lease', 'pending', 'ack', 'target']


class ConsumptionIn(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, alias_generator=to_camel)


class TargetIn(ConsumptionIn):
    kind: Literal['plc-facts-v2']
    instance_id: Identifier
    plc_id: Identifier
    db_number: DbNumber
    source_generation: Identifier


class DeliveryTargetIn(TargetIn):
    sample_id: UuidText
    source_seq: SequenceText


class CreateConsumerIn(ConsumptionIn):
    plc_id: Identifier
    db_number: DbNumber
    start_mode: Literal['now', 'retained']
    target: TargetIn


class RunStateIn(ConsumptionIn):
    operation_id: UuidText
    desired_state: Literal['running', 'paused']


class LeaseIn(ConsumptionIn):
    operation_id: UuidText
    worker_id: Identifier
    action: Literal['acquire', 'renew', 'release']


class PendingIn(ConsumptionIn):
    event_seq: SequenceText
    config_version: Identifier
    config_hash: HashText
    serializer_version: Identifier
    body_sha256: HashText
    target: DeliveryTargetIn


class AckIn(ConsumptionIn):
    operation_id: UuidText
    http_status: Literal[200]
    code: Literal[200]
    contract_version: Literal['plc-facts/v2']
    instance_id: Identifier
    sample_id: UuidText
    status: Literal['committed']
    outcome: Literal['created', 'duplicate']


class FailureOut(ResponseModel):
    code: int
    message: str
    data: dict[str, str] | None = None
    error_code: str


class ExcludedOut(ResponseModel):
    count: str
    first_event_seq: str | None
    last_event_seq: str | None


class ConsumerCreatedOut(ResponseModel):
    consumer_id: UuidText
    start_at: str
    start_seq: str
    last_confirmed_seq: str
    excluded_history: ExcludedOut
    desired_state: Literal['paused']


class TargetOut(ResponseModel):
    kind: Literal['plc-facts-v2']
    instance_id: str
    plc_id: str
    db_number: DbNumber
    source_generation: str


class DeliveryTargetOut(TargetOut):
    sample_id: UuidText
    source_seq: SequenceText


class PendingOut(ResponseModel):
    delivery_id: UuidText
    event_seq: SequenceText
    config_version: str
    config_hash: HashText
    serializer_version: str
    body_sha256: HashText
    target: DeliveryTargetOut


class LeaseOut(ResponseModel):
    lease_id: UuidText
    lease_generation: SequenceText
    expires_at: str
    renew_after_at: str


class RunStateOut(ResponseModel):
    desired_state: Literal['running', 'paused']


class ConsumerStatusOut(RunStateOut):
    consumer_id: UuidText
    plc_id: str
    db_number: DbNumber
    start_mode: Literal['now', 'retained']
    start_at: str
    start_seq: str
    last_confirmed_seq: str
    excluded_history: ExcludedOut
    target: TargetOut
    lease: LeaseOut | None
    pending: PendingOut | None
    status: Literal['idle', 'pending', 'confirmed', 'blocked']


class ReadyOut(ResponseModel):
    status: Literal['ready']
    event_seq: SequenceText
    delivery_id: UuidText
    target: DeliveryTargetOut
    sample: SampleDetail


class EmptyOut(ResponseModel):
    status: Literal['empty']


class ConfirmedOut(ResponseModel):
    status: Literal['confirmed']
    delivery_id: UuidText
    last_confirmed_seq: SequenceText
    confirmed_at: str
