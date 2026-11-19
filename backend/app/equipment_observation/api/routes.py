"""指标发现、双路写入、配置和查询 HTTP 入口。"""
import json
from typing import Literal

from fastapi import APIRouter, Depends, Header, Query, Request, Security
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.guard import EvidenceUnavailable, probe_target
from common.log import log_event
from common.integration.http import IntegrationPayloadError, strict_json
from core.deps import get_current_active_admin, require_permissions
from database import get_db
from ..domain import ObservationError, identifier, reject, response
from ..models import CardConfig, CurveGroup, EnergyMetric, MetricConfig, MetricGroup, SlotBinding
from ..machine_openapi import request_body
from ..profile import allowed_meter, authenticate, get_profile, permitted_energy
from ..schemas import (Card, CardPatch, Curve, CurvePatch, EnergyMetric as EnergyMetricInput,
                       EnergyMetricPatch, Group, GroupPatch, HistoryReview, Metric, MetricPatch, Remark, Slot, SlotPatch)
from ..services import configuration, energy_reads, ingest_v2, reads


class ObservationRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        async def protected(request):
            try:
                if request.method == "POST" and request.url.path.endswith((
                    "/integration/equipment/latest-snapshots", "/integration/monitor/history-samples", "/integration/energy/samples"
                )):
                    profile = get_profile()
                    producer = authenticate(profile, request.headers.get("authorization"))
                    request.state.observation_identity = (profile, producer)
                    await strict_body(request)
                return await handler(request)
            except EvidenceUnavailable:
                return JSONResponse(status_code=503, content={"code": 503, "message": "equipment_observation.not_ready",
                                    "data": None, "errorCode": "equipment_observation.not_ready"})
            except ObservationError as exc:
                code = f"equipment_observation.{exc.reason}"
                try:
                    log_event("WARNING", "observation.request_rejected", status=exc.status,
                              reason=exc.reason, method=request.method)
                except Exception:
                    pass
                return JSONResponse(status_code=exc.status, content={"code": exc.status, "message": code,
                                    "data": None, "errorCode": code},
                                    headers={"WWW-Authenticate": "Bearer"} if exc.status == 401 else None)
        return protected


router = APIRouter(route_class=ObservationRoute, tags=["Equipment observation"])
machine_bearer = HTTPBearer(auto_error=False, scheme_name="ObservationMachineBearer")
equipment_reader = require_permissions("equipment-observation-read")
monitor_reader = require_permissions("monitor-observation-read")
energy_reader = require_permissions("energy-consumption-read")


def machine(request: Request, credentials: HTTPAuthorizationCredentials | None = Security(machine_bearer)):
    existing = getattr(request.state, "observation_identity", None)
    if existing is not None:
        return existing
    profile = get_profile()
    header = f"{credentials.scheme} {credentials.credentials}" if credentials else ""
    return profile, authenticate(profile, header)


def admin_scope(_user):
    # Global configuration needs admin, while record queries separately filter devices.
    return get_profile()


def language(request):
    return "en-US" if request.headers.get("accept-language", "").lower().startswith("en") else "zh-CN"


async def strict_body(request):
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise ObservationError(415, "media_type")
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > 65536:
            raise ObservationError(413, "payload_too_large")
        body.extend(chunk)
    request._body = bytes(body)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    def invalid(_value):
        raise ValueError("invalid number")
    try:
        request._obs_decimal = strict_json(bytes(body))
        document = json.loads(body.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid)
        request._json = document
        return document
    except IntegrationPayloadError as exc:
        raise ObservationError(exc.status, exc.suffix) from None
    except (ValueError, UnicodeError, RecursionError):
        reject()


@router.get("/integration/metric-definitions")
async def definitions(equipment_id: str = Query(alias="equipmentId"), identity=Depends(machine),
                      db: AsyncSession = Depends(get_db)):
    profile, producer = identity
    identifier(equipment_id)
    if equipment_id not in profile["devices"]:
        reject("forbidden", 403)
    scopes = {(g["groupKey"], g["target"]): set(g["metricKeys"]) for g in producer["grants"]
              if g["equipmentId"] == equipment_id}
    if not scopes:
        reject("forbidden", 403)
    await probe_target(db, profile["target"])
    groups = (await db.execute(select(MetricGroup).order_by(MetricGroup.sort_order, MetricGroup.group_key))).scalars().all()
    metrics = (await db.execute(select(MetricConfig).order_by(MetricConfig.metric_key))).scalars().all()
    slots = (await db.execute(select(SlotBinding))).scalars().all()
    enabled = {(s.target, s.group_key, s.metric_key): s.enabled for s in slots}
    output = []
    for group in groups:
        if not any(g == group.group_key for g, _ in scopes):
            continue
        entries = []
        for metric in metrics:
            if metric.source_group_key != group.group_key:
                continue
            latest = metric.metric_key in scopes.get((group.group_key, "latest"), set())
            history = metric.metric_key in scopes.get((group.group_key, "history"), set())
            if not latest and not history:
                continue
            entries.append({"metricKey": metric.metric_key, "valueType": metric.value_type, "unit": metric.unit,
                            "latestEnabled": latest and enabled.get(("latest", group.group_key, metric.metric_key), False),
                            "historyEnabled": history and enabled.get(("history", group.group_key, metric.metric_key), False)})
        output.append({"groupKey": group.group_key, "metrics": entries})
    return response({"equipmentId": equipment_id, "groups": output})


async def submit(target, request, identity, db):
    profile, producer = identity
    result = await ingest_v2.device(db, profile, producer, target, request._json, request._obs_decimal)
    try:
        log_event("INFO", "observation.ingest", target=target, producer_id=producer["producerId"],
                  outcome=result["outcome"])
    except Exception:
        pass
    return response(result)


@router.post("/integration/equipment/latest-snapshots", openapi_extra=request_body("latest"))
async def write_latest(request: Request, payload: dict, identity=Depends(machine), db: AsyncSession = Depends(get_db)):
    return await submit("latest", request, identity, db)


@router.post("/integration/monitor/history-samples", openapi_extra=request_body("history"))
async def write_history(request: Request, payload: dict, identity=Depends(machine), db: AsyncSession = Depends(get_db)):
    return await submit("history", request, identity, db)


@router.get("/integration/energy/metric-definitions")
async def energy_definitions(meter_id: str = Query(alias="meterId"), group_key: str = Query(alias="groupKey"),
                             identity=Depends(machine), db: AsyncSession = Depends(get_db)):
    profile, producer = identity
    allowed = permitted_energy(producer, meter_id, group_key)
    await probe_target(db, profile["target"])
    rows = (await db.execute(select(EnergyMetric).where(EnergyMetric.meter_id == meter_id,
        EnergyMetric.group_key == group_key, EnergyMetric.enabled.is_(True)).order_by(EnergyMetric.slot_no))).scalars().all()
    return response({"meterId": meter_id, "groupKey": group_key, "definitions": [
        {"metricKey": row.metric_key, "valueType": row.value_type, "measurementMode": row.measurement_mode,
         "quantityKey": row.quantity_key, "unit": row.unit} for row in rows if row.metric_key in allowed]})


@router.post("/integration/energy/samples", openapi_extra=request_body("energy"))
async def write_energy(request: Request, payload: dict, identity=Depends(machine), db: AsyncSession = Depends(get_db)):
    profile, producer = identity
    return response(await ingest_v2.energy(db, profile, producer, request._obs_decimal))


@router.get("/equipment/observation-options")
async def equipment_options(user=Depends(equipment_reader)):
    return response(await reads.options(get_profile(), user))


@router.get("/monitor/observation-options")
async def monitor_options(user=Depends(monitor_reader)):
    return response(await reads.options(get_profile(), user))


@router.get("/equipment/latest-cards")
async def latest_cards(request: Request, equipment_id: str = Query(alias="equipmentId"),
                       page_key: str = Query(alias="pageKey"), task: str | None = Query(None, alias="taskNo"), user=Depends(equipment_reader),
                       db: AsyncSession = Depends(get_db)):
    return response(await reads.latest_cards(db, get_profile(), user, equipment_id, page_key, language(request), task))


@router.get("/equipment/sampled-tasks")
async def sampled_tasks(equipment_id: str = Query(alias="equipmentId"), user=Depends(equipment_reader), db: AsyncSession = Depends(get_db)):
    return response(await reads.task_candidates(db, get_profile(), user, equipment_id))


@router.get("/equipment/metric-groups")
async def metric_groups(user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    rows = (await db.execute(select(MetricGroup).order_by(MetricGroup.sort_order, MetricGroup.group_key))).scalars().all()
    return response([configuration.group_data(row) for row in rows])


@router.post("/equipment/metric-groups")
async def add_metric_group(item: Group, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    await probe_target(db, admin_scope(user)["target"])
    return response(await configuration.save_group(db, item))


@router.patch("/equipment/metric-groups/{key}")
async def patch_metric_group(key: str, item: GroupPatch, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    await probe_target(db, admin_scope(user)["target"])
    return response(await configuration.save_group(db, item, key))


@router.get("/energy/consumption/options")
async def energy_options(user=Depends(energy_reader)):
    profile = get_profile()
    return response([profile["meters"][key] for key in sorted(profile["meterReadScopes"].get(user.role, []))])


@router.get("/energy/consumption/definitions")
async def energy_read_definitions(meter_id: str = Query(alias="meterId"), user=Depends(energy_reader),
                                  db: AsyncSession = Depends(get_db)):
    profile = get_profile()
    allowed_meter(profile, user, meter_id)
    await probe_target(db, profile["target"])
    rows = (await db.execute(select(EnergyMetric).where(EnergyMetric.meter_id == meter_id)
                             .order_by(EnergyMetric.group_key, EnergyMetric.slot_no))).scalars().all()
    return response([configuration.energy_metric_data(row) for row in rows])


@router.get("/energy/metric-configs")
async def energy_configs(meter_id: str = Query(alias="meterId"), group_key: str | None = Query(None, alias="groupKey"),
                         user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = get_profile()
    allowed_meter(profile, user, meter_id)
    await probe_target(db, profile["target"])
    query = select(EnergyMetric).where(EnergyMetric.meter_id == meter_id)
    if group_key:
        query = query.where(EnergyMetric.group_key == group_key)
    rows = (await db.execute(query.order_by(EnergyMetric.group_key, EnergyMetric.slot_no))).scalars().all()
    return response([configuration.energy_metric_data(row) for row in rows])


@router.post("/energy/metric-configs")
async def add_energy_config(item: EnergyMetricInput, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = get_profile()
    allowed_meter(profile, user, item.meter_id)
    await probe_target(db, profile["target"])
    return response(await configuration.save_energy_metric(db, item))


@router.patch("/energy/metric-configs/{meter_id}/{group_key}/{metric_key}")
async def patch_energy_config(meter_id: str, group_key: str, metric_key: str, item: EnergyMetricPatch,
                              user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = get_profile()
    allowed_meter(profile, user, meter_id)
    await probe_target(db, profile["target"])
    return response(await configuration.save_energy_metric(db, item, (meter_id, group_key, metric_key)))


@router.get("/energy/consumption/samples")
async def energy_samples(meter_id: str = Query(alias="meterId"), group_key: str | None = Query(None, alias="groupKey"),
                         start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to"),
                         page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                         user=Depends(energy_reader), db: AsyncSession = Depends(get_db)):
    return response(await energy_reads.samples(db, get_profile(), user, meter_id, group_key, start, end, page, size))


@router.get("/energy/consumption/summary")
async def energy_summary(meter_id: str = Query(alias="meterId"), group_key: str = Query(alias="groupKey"),
                         metric_key: str = Query(alias="metricKey"), start: str = Query(alias="from"),
                         end: str = Query(alias="to"), user=Depends(energy_reader), db: AsyncSession = Depends(get_db)):
    return response(await energy_reads.summary(db, get_profile(), user, meter_id, group_key, metric_key, start, end))


@router.get("/energy/admin/consumption-samples")
async def energy_admin_samples(meter_id: str = Query(alias="meterId"), group_key: str | None = Query(None, alias="groupKey"),
                         start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to"),
                         page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                         user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response(await energy_reads.samples(db, get_profile(), user, meter_id, group_key, start, end, page, size))


@router.patch("/energy/admin/consumption-samples/{identity}")
async def patch_energy_sample(identity: int, item: HistoryReview, user=Depends(get_current_active_admin),
                              db: AsyncSession = Depends(get_db)):
    row = await energy_reads.detail(db, get_profile(), user, identity)
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    await db.commit()
    await db.refresh(row)
    return response(await energy_reads.sample_data(db, row))


@router.get("/equipment/metric-configs")
async def metric_configs(user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.metrics(db))


@router.post("/equipment/metric-configs")
async def add_metric(item: Metric, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.create_metric(db, item))


@router.patch("/equipment/metric-configs/{metric_key}")
async def patch_metric(metric_key: str, item: MetricPatch, user=Depends(get_current_active_admin),
                       db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.update_metric(db, metric_key, item))


@router.get("/equipment/metric-slot-bindings")
async def list_bindings(target: str, group_key: str = Query(alias="groupKey"), user=Depends(get_current_active_admin),
                        db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.bindings(db, target, group_key))


@router.post("/equipment/metric-slot-bindings")
async def add_binding(item: Slot, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.create_binding(db, item))


@router.patch("/equipment/metric-slot-bindings/{target}/{group_key}/{slot_no}")
async def patch_binding(target: str, group_key: str, slot_no: int, item: SlotPatch,
                        user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.update_binding(db, target, group_key, slot_no, item))


@router.get("/equipment/observation-list-columns")
async def observation_list_columns(target: Literal["latest", "history"], user=Depends(get_current_active_admin),
                                   db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.list_columns(db, target))


@router.get("/equipment/card-configs")
async def list_cards(page_key: str | None = Query(None, alias="pageKey"), user=Depends(get_current_active_admin),
                     db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    query = select(CardConfig).order_by(CardConfig.sort_order, CardConfig.card_key)
    if page_key:
        query = query.where(CardConfig.page_key == page_key)
    return response([configuration.card_data(row) for row in (await db.execute(query)).scalars()])


def display_fields(item, collection):
    data = item.model_dump(exclude_unset=True)
    if any(value is None for value in data.values()):
        reject()
    if collection in data:
        data[collection] = [entry.model_dump(by_alias=True) for entry in getattr(item, collection)]
    return data


@router.post("/equipment/card-configs")
async def add_card(item: Card, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.save_display(db, CardConfig, item.card_key, display_fields(item, "items")))


@router.patch("/equipment/card-configs/{key}")
async def patch_card(key: str, item: CardPatch, user=Depends(get_current_active_admin),
                     db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.save_display(db, CardConfig, key, display_fields(item, "items"), existing=True))


@router.get("/monitor/curve-configs")
async def list_curves(category: str | None = None, user=Depends(get_current_active_admin),
                      db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    query = select(CurveGroup).order_by(CurveGroup.sort_order, CurveGroup.curve_group_key)
    if category:
        query = query.where(CurveGroup.category == category)
    return response([configuration.curve_data(row) for row in (await db.execute(query)).scalars()])


@router.post("/monitor/curve-configs")
async def add_curve(item: Curve, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.save_display(db, CurveGroup, item.curve_group_key, display_fields(item, "series")))


@router.patch("/monitor/curve-configs/{key}")
async def patch_curve(key: str, item: CurvePatch, user=Depends(get_current_active_admin),
                      db: AsyncSession = Depends(get_db)):
    profile = admin_scope(user)
    await probe_target(db, profile["target"])
    return response(await configuration.save_display(db, CurveGroup, key, display_fields(item, "series"), existing=True))


@router.get("/monitor/history-samples")
async def history_samples(equipment_id: str | None = Query(None, alias="equipmentId"),
                          group_key: str | None = Query(None, alias="groupKey"), task: str | None = Query(None, alias="taskNo"),
                          start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to"),
                          category: str | None = None, metric_key: str | None = Query(None, alias="metricKey"),
                          page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                          user=Depends(monitor_reader), db: AsyncSession = Depends(get_db)):
    filters = dict(equipment=equipment_id, group=group_key, task=task, start=start, end=end,
                   category=category, metric_key=metric_key)
    return response(await reads.samples(db, get_profile(), user, "history", filters, page, size))


@router.get("/monitor/history-curves")
async def history_curves(request: Request, equipment_id: str = Query(alias="equipmentId"),
                         category: str = Query(), start: str = Query(alias="from"), end: str = Query(alias="to"),
                         task: str | None = Query(None, alias="taskNo"), user=Depends(monitor_reader),
                         db: AsyncSession = Depends(get_db)):
    return response(await reads.curves(db, get_profile(), user, equipment_id, category, task, start, end, language(request)))


async def admin_list(target, equipment_id, group_key, task, start, end, page, size, user, db):
    profile = admin_scope(user)
    return response(await reads.samples(db, profile, user, target,
        dict(equipment=equipment_id, group=group_key, task=task, start=start, end=end), page, size))


@router.get("/equipment/admin/latest-snapshots")
async def latest_list(equipment_id: str | None = Query(None, alias="equipmentId"),
                      group_key: str | None = Query(None, alias="groupKey"), task: str | None = Query(None, alias="taskNo"),
                      page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                      user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return await admin_list("latest", equipment_id, group_key, task, None, None, page, size, user, db)


@router.get("/monitor/admin/history-samples")
async def history_list(equipment_id: str | None = Query(None, alias="equipmentId"),
                       group_key: str | None = Query(None, alias="groupKey"), task: str | None = Query(None, alias="taskNo"),
                       start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to"),
                       page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                       user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return await admin_list("history", equipment_id, group_key, task, start, end, page, size, user, db)


@router.get("/equipment/admin/latest-snapshots/{record_id}")
async def latest_detail(record_id: int, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response((await reads.detail(db, get_profile(), user, "latest", record_id))[1])


@router.get("/monitor/admin/history-samples/{record_id}")
async def history_detail(record_id: int, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response((await reads.detail(db, get_profile(), user, "history", record_id))[1])


@router.patch("/equipment/admin/latest-snapshots/{record_id}")
async def edit_latest(record_id: int, item: Remark, user=Depends(get_current_active_admin),
                      db: AsyncSession = Depends(get_db)):
    row, _ = await reads.detail(db, get_profile(), user, "latest", record_id)
    for name, value in item.model_dump(exclude_unset=True).items():
        setattr(row, name, value)
    await db.commit()
    await db.refresh(row)
    return response(await reads.sample_data(db, row, "latest", details=True))


@router.patch("/monitor/admin/history-samples/{record_id}")
async def edit_history(record_id: int, item: HistoryReview, user=Depends(get_current_active_admin),
                       db: AsyncSession = Depends(get_db)):
    row, _ = await reads.detail(db, get_profile(), user, "history", record_id)
    for name, value in item.model_dump(exclude_unset=True).items():
        setattr(row, name, value)
    await db.commit()
    await db.refresh(row)
    return response(await reads.sample_data(db, row, "history", details=True))
