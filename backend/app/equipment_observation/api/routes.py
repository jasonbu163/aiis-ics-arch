"""指标发现、双路写入、配置和查询 HTTP 入口。"""
import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, Path, Query, Request, Security
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.guard import EvidenceUnavailable, current_clock, verify_energy_target
from common.log import log_event
from common.integration.http import IntegrationPayloadError, strict_json
from core.deps import get_current_active_admin, require_permissions
from database import get_db
from ..domain import ObservationError, identifier, reject, response
from ..models import CardConfig, CurveGroup, EnergyMetric, MetricConfig, MetricGroup, SlotBinding
from ..machine_openapi import request_body
from ..profile import allowed_meter, authenticate, get_profile, permitted_energy, require_energy_target
from ..schemas import (Card, CardPatch, Curve, CurvePatch, EnergyMetric as EnergyMetricInput,
                       EnergyMetricPatch, Group, GroupPatch, HistoryReview, Metric, MetricPatch, Remark, Slot, SlotPatch)
from ..services import (async_energy_curve_groups, configuration, energy_meters, energy_public_reads, energy_reads, energy_registered_ingest, energy_write_sources,
                        ingest_v2, reads, registered_ingest, write_sources)
from .energy_curve_contract import (CURVE_ERRORS, EnergyCurveCreate, EnergyCurveError, EnergyCurveListResponse,
                                    EnergyCurvePatch, EnergyCurveResponse)
from .energy_meter_contract import (CreateEnergyMeter, EnergyMeterError, EnergyMeterListResponse,
                                    EnergyMeterResponse, METER_CHANGE_ERRORS, METER_READ_ERRORS, PatchEnergyMeter)
from .energy_public_read_contract import ENERGY_HISTORY_READ, LATEST_ENERGY_READ
from .write_source_contract import CreateWriteSource, ENERGY_WRITE_REQUEST, PatchWriteSource, WRITE_REQUEST


class ObservationRoute(APIRoute):
    def __init__(self, path, **kwargs):
        if path.startswith(("/energy/", "/integration/energy/")):
            kwargs["tags"] = ["Energy"]
        super().__init__(path, **kwargs)

    def get_route_handler(self):
        handler = super().get_route_handler()
        path = self.path
        is_energy = "/energy/" in path
        async def protected(request):
            public_energy_read = request.method == "GET" and path.endswith(
                ("/integration/energy/latest", "/integration/energy/samples")
            )
            curve_route = is_energy and "/curve-configs" in path
            stable_validation = (public_energy_read or curve_route
                                 or path.endswith(("/integration/observations", "/integration/observations/latest"))
                                 or path.endswith("/integration/energy/registered-samples")
                                 or path.endswith("/energy/meters")
                                 or "/equipment/write-sources" in path or "/energy/write-sources" in path)
            try:
                if request.method == "POST" and path.endswith((
                    "/integration/equipment/latest-snapshots", "/integration/monitor/history-samples", "/integration/energy/samples"
                )):
                    profile = energy_profile() if is_energy else get_profile()
                    producer = authenticate(profile, request.headers.get("authorization"))
                    request.state.observation_identity = (profile, producer)
                    await strict_body(request)
                try:
                    return await handler(request)
                except HTTPException as exc:
                    if not curve_route or exc.status_code not in (401, 403):
                        raise
                    reject("unauthenticated" if exc.status_code == 401 else "forbidden", exc.status_code)
                except RequestValidationError:
                    if not stable_validation:
                        raise
                    reject()
                except DBAPIError:
                    reject("not_ready", 503)
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
    profile = energy_profile() if "/energy/" in request.scope["route"].path else get_profile()
    header = f"{credentials.scheme} {credentials.credentials}" if credentials else ""
    return profile, authenticate(profile, header)


def energy_profile():
    return require_energy_target(get_profile())


def admin_scope(_user):
    # Global configuration needs admin, while record queries separately filter devices.
    return get_profile()


def language(request):
    return "en-US" if request.headers.get("accept-language", "").lower().startswith("en") else "zh-CN"


async def strict_body(request, *, decimal_only=False):
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise ObservationError(415, "media_type")
    if decimal_only:
        parameters = request.headers.get("content-type", "").split(";")[1:]
        if (request.headers.get("content-encoding", "identity").strip().lower() != "identity"
                or any(key.strip().lower() == "charset" and value.strip().strip('"').lower() != "utf-8"
                       for key, _, value in (parameter.partition("=") for parameter in parameters))):
            reject("media_type", 415)
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
        if decimal_only:
            return request._obs_decimal
        document = json.loads(body.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid)
        request._json = document
        return document
    except IntegrationPayloadError as exc:
        if decimal_only:
            reject()
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
    await write_sources.check_profile(db, profile)
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
    await verify_energy_target(db, profile["target"])
    rows = (await db.execute(select(EnergyMetric).where(EnergyMetric.meter_id == meter_id,
        EnergyMetric.group_key == group_key, EnergyMetric.enabled.is_(True)).order_by(EnergyMetric.slot_no))).scalars().all()
    return response({"meterId": meter_id, "groupKey": group_key, "definitions": [
        {"metricKey": row.metric_key, "valueType": row.value_type, "measurementMode": row.measurement_mode,
         "quantityKey": row.quantity_key, "unit": row.unit} for row in rows if row.metric_key in allowed]})


@router.post("/integration/energy/samples", openapi_extra=request_body("energy"))
async def write_energy(request: Request, payload: dict, identity=Depends(machine), db: AsyncSession = Depends(get_db)):
    profile, producer = identity
    return response(await ingest_v2.energy(db, profile, producer, request._obs_decimal))


@router.get("/integration/energy/latest", responses=LATEST_ENERGY_READ, openapi_extra={"security": []},
            summary="Public — Get latest energy samples")
async def public_energy_latest(meter: str | None = Query(None, alias="meterId", min_length=1, max_length=64),
                               group: str | None = Query(None, alias="groupKey", min_length=1, max_length=64),
                               db: AsyncSession = Depends(get_db)):
    return response(await energy_public_reads.latest(db, energy_profile(), meter, group))


@router.get("/integration/energy/samples", responses=ENERGY_HISTORY_READ, openapi_extra={"security": []},
            summary="Public — Get historical energy samples")
async def public_energy_history(meter: str = Query(alias="meterId", min_length=1, max_length=64),
                                group: str | None = Query(None, alias="groupKey", min_length=1, max_length=64),
                                start: str = Query(alias="from"), end: str = Query(alias="to"),
                                page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                                db: AsyncSession = Depends(get_db)):
    return response(await energy_public_reads.history(db, energy_profile(), meter, group, start, end, page, size))


@router.post("/integration/observations", openapi_extra=WRITE_REQUEST)
async def write_observation(request: Request, db: AsyncSession = Depends(get_db)):
    document = await strict_body(request, decimal_only=True)
    result = await registered_ingest.submit(db, get_profile(), document)
    try:
        log_event("INFO", "observation.registered_ingest", target=result["target"],
                  source_key=result["sourceKey"], outcome=result["outcome"])
    except Exception:
        pass
    return response(result)


@router.get("/integration/observations/latest")
async def read_observation(source_key: str = Query(alias="sourceKey"), target: Literal["latest", "history"] = Query(),
                           task: str | None = Query(None, alias="taskNo"), db: AsyncSession = Depends(get_db)):
    return response(await reads.public_latest(db, get_profile(), source_key, target, task))


@router.get("/equipment/write-sources")
async def list_write_sources(user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response(await write_sources.list_sources(db, admin_scope(user)))


@router.post("/equipment/write-sources")
async def add_write_source(item: CreateWriteSource, user=Depends(get_current_active_admin),
                           db: AsyncSession = Depends(get_db)):
    return response(await write_sources.create(db, admin_scope(user), item.source_key, item.name, item.enabled))


def _source_path_key(key):
    # 浏览器会消去点路径段；只恢复这两个已知的、双层百分号编码段。
    return {"%2E": ".", "%2E%2E": ".."}.get(key, key)


@router.patch("/equipment/write-sources/{sourceKey}")
async def patch_write_source(source_key: Annotated[str, Path(alias="sourceKey")], item: PatchWriteSource, user=Depends(get_current_active_admin),
                             db: AsyncSession = Depends(get_db)):
    changes = item.model_dump(exclude_unset=True)
    if not changes or ("enabled" in changes and changes["enabled"] is None):
        reject()
    return response(await write_sources.change(db, admin_scope(user), _source_path_key(source_key), changes))


@router.delete("/equipment/write-sources/{sourceKey}")
async def delete_write_source(source_key: Annotated[str, Path(alias="sourceKey")], user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response(await write_sources.change(db, admin_scope(user), _source_path_key(source_key), {}, delete=True))


@router.get("/equipment/observation-options")
async def equipment_options(include_deleted: bool = Query(False, alias="includeDeleted"), user=Depends(equipment_reader),
                            db: AsyncSession = Depends(get_db)):
    return response(await reads.options(db, get_profile(), user, include_deleted))


@router.get("/monitor/observation-options")
async def monitor_options(include_deleted: bool = Query(False, alias="includeDeleted"), user=Depends(monitor_reader),
                          db: AsyncSession = Depends(get_db)):
    return response(await reads.options(db, get_profile(), user, include_deleted))


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
    admin_scope(user)
    rows = (await db.execute(select(MetricGroup).order_by(MetricGroup.sort_order, MetricGroup.group_key))).scalars().all()
    return response([configuration.group_data(row) for row in rows])


@router.post("/equipment/metric-groups")
async def add_metric_group(item: Group, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.save_group(db, item))


@router.patch("/equipment/metric-groups/{key}")
async def patch_metric_group(key: str, item: GroupPatch, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.save_group(db, item, key))


@router.post("/integration/energy/registered-samples", openapi_extra=ENERGY_WRITE_REQUEST,
             summary="Public — Write registered energy samples")
async def write_registered_energy(request: Request, db: AsyncSession = Depends(get_db)):
    document = await strict_body(request, decimal_only=True)
    result = await energy_registered_ingest.submit(db, energy_profile(), document)
    try:
        log_event("INFO", "energy.registered_ingest", source_key=result["sourceKey"],
                  outcome=result["outcome"], sample_count=len(result["records"]))
    except Exception:
        pass
    return response(result)


@router.get("/energy/write-sources", summary="Management — List energy write sources")
async def list_energy_write_sources(user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    await verify_energy_target(db, energy_profile()["target"])
    return response(await energy_write_sources.list_sources(db))


@router.post("/energy/write-sources", summary="Management — Add energy write source")
async def add_energy_write_source(item: CreateWriteSource, user=Depends(get_current_active_admin),
                                  db: AsyncSession = Depends(get_db)):
    await verify_energy_target(db, energy_profile()["target"])
    return response(await energy_write_sources.create(db, item.source_key, item.name, item.enabled))


@router.patch("/energy/write-sources/{sourceKey}", summary="Management — Update energy write source")
async def patch_energy_write_source(source_key: Annotated[str, Path(alias="sourceKey")], item: PatchWriteSource,
                                    user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    changes = item.model_dump(exclude_unset=True)
    if not changes or ("enabled" in changes and changes["enabled"] is None):
        reject()
    await verify_energy_target(db, energy_profile()["target"])
    return response(await energy_write_sources.change(db, _source_path_key(source_key), changes))


@router.delete("/energy/write-sources/{sourceKey}", summary="Management — Delete energy write source")
async def delete_energy_write_source(source_key: Annotated[str, Path(alias="sourceKey")],
                                     user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    await verify_energy_target(db, energy_profile()["target"])
    return response(await energy_write_sources.change(db, _source_path_key(source_key), {}, delete=True))


@router.get("/energy/meters", summary="Management — List energy meters",
            response_model=EnergyMeterListResponse, responses=METER_READ_ERRORS)
async def list_energy_meters(user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = energy_profile()
    await verify_energy_target(db, profile["target"])
    meters = await energy_meters.catalog(db, profile)
    return response([meters[key] for key in sorted(meters)])


@router.post("/energy/meters", summary="Management — Add energy meter",
             response_model=EnergyMeterResponse, responses={**METER_CHANGE_ERRORS,
                 409: {"description": "Duplicate meter ID", "model": EnergyMeterError}})
async def add_energy_meter(item: CreateEnergyMeter, user=Depends(get_current_active_admin),
                           db: AsyncSession = Depends(get_db)):
    profile = energy_profile()
    await verify_energy_target(db, profile["target"])
    return response(await energy_meters.create(db, profile, item.meter_id, item.model_dump(exclude={"meter_id"})))


@router.patch("/energy/meters", summary="Management — Update energy meter",
              response_model=EnergyMeterResponse, responses={**METER_CHANGE_ERRORS,
                  404: {"description": "Meter not found", "model": EnergyMeterError}})
async def patch_energy_meter(item: PatchEnergyMeter, user=Depends(get_current_active_admin),
                             db: AsyncSession = Depends(get_db)):
    profile = energy_profile()
    await verify_energy_target(db, profile["target"])
    changes = item.model_dump(exclude={"meter_id"}, exclude_unset=True)
    return response(await energy_meters.change(db, profile, item.meter_id, changes))


@router.get("/energy/curve-configs", summary="Management — List energy curve groups",
            response_model=EnergyCurveListResponse, responses=CURVE_ERRORS)
async def list_energy_curve_groups(meter_id: str | None = Query(None, alias="meterId"),
                                   user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response(await async_energy_curve_groups.list_groups(
        db, energy_profile(), user, meter_id, enabled_only=False))


@router.post("/energy/curve-configs", summary="Management — Add energy curve group",
             response_model=EnergyCurveResponse, responses={**CURVE_ERRORS,
                 409: {"description": "Duplicate curve group key", "model": EnergyCurveError}})
async def add_energy_curve_group(item: EnergyCurveCreate, user=Depends(get_current_active_admin),
                                 db: AsyncSession = Depends(get_db)):
    return response(await async_energy_curve_groups.create(db, energy_profile(), user, item))


@router.patch("/energy/curve-configs/{curveGroupKey:path}", summary="Management — Update energy curve group",
              response_model=EnergyCurveResponse, responses={**CURVE_ERRORS,
                  404: {"description": "Curve group not found", "model": EnergyCurveError}})
async def patch_energy_curve_group(request: Request, curve_group_key: Annotated[str, Path(alias="curveGroupKey")],
                                   item: EnergyCurvePatch, user=Depends(get_current_active_admin),
                                   db: AsyncSession = Depends(get_db)):
    # 保护浏览器会规范化的两个点段，其他路径参数继续使用框架解码后的值。
    dots = {"%2e": ".", "%2e%2e": ".."}.get(curve_group_key)
    if dots and request.scope.get("raw_path", b"").endswith(dots.replace(".", "%252e").encode()):
        curve_group_key = dots
    return response(await async_energy_curve_groups.patch(db, energy_profile(), user, curve_group_key, item))


@router.get("/energy/consumption/curve-configs", summary="List enabled energy curve groups",
            response_model=EnergyCurveListResponse, responses=CURVE_ERRORS)
async def energy_consumption_curve_groups(meter_id: str | None = Query(None, alias="meterId"),
                                          user=Depends(energy_reader), db: AsyncSession = Depends(get_db)):
    return response(await async_energy_curve_groups.list_groups(
        db, energy_profile(), user, meter_id, enabled_only=True))


@router.get("/energy/consumption/options")
async def energy_options(user=Depends(energy_reader), db: AsyncSession = Depends(get_db)):
    profile = await energy_meters.effective_profile(db, energy_profile())
    return response([profile["meters"][key] for key in sorted(profile["meterReadScopes"].get(user.role, []))])


@router.get("/energy/consumption/definitions")
async def energy_read_definitions(meter_id: str = Query(alias="meterId"), user=Depends(energy_reader),
                                  db: AsyncSession = Depends(get_db)):
    profile = await energy_meters.effective_profile(db, energy_profile())
    allowed_meter(profile, user, meter_id)
    rows = (await db.execute(select(EnergyMetric).where(EnergyMetric.meter_id == meter_id)
                             .order_by(EnergyMetric.group_key, EnergyMetric.slot_no))).scalars().all()
    return response([configuration.energy_metric_data(row) for row in rows])


@router.get("/energy/metric-configs", summary="Management — List energy metric configurations")
async def energy_configs(meter_id: str | None = Query(None, alias="meterId"),
                         group_key: str | None = Query(None, alias="groupKey"),
                         user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = await energy_meters.effective_profile(db, energy_profile())
    if meter_id is not None:
        allowed_meter(profile, user, meter_id)
        meter_ids = (meter_id,)
    else:
        meter_ids = profile["meterReadScopes"].get(user.role, ())
    return response(await configuration.energy_metric_configs(db, meter_ids, group_key))


@router.post("/energy/metric-configs", summary="Management — Add energy metric configuration")
async def add_energy_config(item: EnergyMetricInput, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = await energy_meters.effective_profile(db, energy_profile())
    allowed_meter(profile, user, item.meter_id)
    return response(await configuration.save_energy_metric(db, item))


@router.patch("/energy/metric-configs/{meter_id}/{group_key}/{metric_key}",
              summary="Management — Update energy metric configuration")
async def patch_energy_config(meter_id: str, group_key: str, metric_key: str, item: EnergyMetricPatch,
                              user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    profile = await energy_meters.effective_profile(db, energy_profile())
    allowed_meter(profile, user, meter_id)
    return response(await configuration.save_energy_metric(db, item, (meter_id, group_key, metric_key)))


@router.get("/energy/consumption/samples")
async def energy_samples(meter_id: str = Query(alias="meterId"), group_key: str | None = Query(None, alias="groupKey"),
                         start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to"),
                         page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                         user=Depends(energy_reader), db: AsyncSession = Depends(get_db)):
    return response(await energy_reads.samples(db, energy_profile(), user, meter_id, group_key, start, end, page, size))


@router.get("/energy/consumption/summary")
async def energy_summary(meter_id: str = Query(alias="meterId"), group_key: str = Query(alias="groupKey"),
                         metric_key: str = Query(alias="metricKey"), start: str = Query(alias="from"),
                         end: str = Query(alias="to"), user=Depends(energy_reader), db: AsyncSession = Depends(get_db)):
    return response(await energy_reads.summary(db, energy_profile(), user, meter_id, group_key, metric_key, start, end))


@router.get("/energy/admin/consumption-samples", summary="Management — List energy consumption samples")
async def energy_admin_samples(meter_id: str = Query(alias="meterId"), group_key: str | None = Query(None, alias="groupKey"),
                         start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to"),
                         page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100, alias="pageSize"),
                         user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    return response(await energy_reads.samples(db, energy_profile(), user, meter_id, group_key, start, end, page, size))


@router.patch("/energy/admin/consumption-samples/{identity}", summary="Management — Update energy sample review")
async def patch_energy_sample(identity: int, item: HistoryReview, user=Depends(get_current_active_admin),
                              db: AsyncSession = Depends(get_db)):
    row = await energy_reads.detail(db, energy_profile(), user, identity)
    changes = item.model_dump(exclude_unset=True)
    if any(getattr(row, key) != value for key, value in changes.items()):
        for key, value in changes.items():
            setattr(row, key, value)
        row.updated_at = await current_clock(db)
    await db.commit()
    await db.refresh(row)
    return response(await energy_reads.sample_data(db, row))


@router.get("/equipment/metric-configs")
async def metric_configs(user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.metrics(db))


@router.post("/equipment/metric-configs")
async def add_metric(item: Metric, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.create_metric(db, item))


@router.patch("/equipment/metric-configs/{metric_key}")
async def patch_metric(metric_key: str, item: MetricPatch, user=Depends(get_current_active_admin),
                       db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.update_metric(db, metric_key, item))


@router.get("/equipment/metric-slot-bindings")
async def list_bindings(target: str | None = None, group_key: str | None = Query(None, alias="groupKey"),
                        user=Depends(get_current_active_admin),
                        db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.bindings(db, target, group_key))


@router.post("/equipment/metric-slot-bindings")
async def add_binding(item: Slot, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.create_binding(db, item))


@router.patch("/equipment/metric-slot-bindings/{target}/{group_key}/{slot_no}")
async def patch_binding(target: str, group_key: str, slot_no: int, item: SlotPatch,
                        user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.update_binding(db, target, group_key, slot_no, item))


@router.get("/equipment/observation-list-columns")
async def observation_list_columns(target: Literal["latest", "history"], user=Depends(get_current_active_admin),
                                   db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.list_columns(db, target))


@router.get("/equipment/card-configs")
async def list_cards(page_key: str | None = Query(None, alias="pageKey"), user=Depends(get_current_active_admin),
                     db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    query = select(CardConfig).order_by(CardConfig.sort_order, CardConfig.card_key)
    if page_key:
        query = query.where(CardConfig.page_key == page_key)
    return response([configuration.card_data(row) for row in (await db.execute(query)).scalars()])


def display_fields(item, collection):
    data = item.model_dump(exclude_unset=True)
    if any(value is None for value in data.values()):
        reject()
    if collection in data:
        data[collection] = [entry.model_dump(by_alias=True, exclude_unset=True) for entry in getattr(item, collection)]
    return data


@router.post("/equipment/card-configs")
async def add_card(item: Card, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.save_display(db, CardConfig, item.card_key, display_fields(item, "items")))


@router.patch("/equipment/card-configs/{key}")
async def patch_card(key: str, item: CardPatch, user=Depends(get_current_active_admin),
                     db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.save_display(db, CardConfig, key, display_fields(item, "items"), existing=True))


@router.get("/monitor/curve-configs")
async def list_curves(category: str | None = None, user=Depends(get_current_active_admin),
                      db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    query = select(CurveGroup).order_by(CurveGroup.sort_order, CurveGroup.curve_group_key)
    if category:
        query = query.where(CurveGroup.category == category)
    return response([configuration.curve_data(row) for row in (await db.execute(query)).scalars()])


@router.post("/monitor/curve-configs")
async def add_curve(item: Curve, user=Depends(get_current_active_admin), db: AsyncSession = Depends(get_db)):
    admin_scope(user)
    return response(await configuration.save_display(db, CurveGroup, item.curve_group_key, display_fields(item, "series")))


@router.patch("/monitor/curve-configs/{key}")
async def patch_curve(key: str, item: CurvePatch, user=Depends(get_current_active_admin),
                      db: AsyncSession = Depends(get_db)):
    admin_scope(user)
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


@router.get("/monitor/history-default-context")
async def history_default_context(category: Literal["temperature", "drive", "cleaning"],
                                  equipment_id: str | None = Query(None, alias="equipmentId", min_length=1),
                                  task: str | None = Query(None, alias="taskNo"),
                                  user=Depends(monitor_reader), db: AsyncSession = Depends(get_db)):
    return response(await reads.history_default_context(db, get_profile(), user, category, equipment_id, task))


@router.get("/monitor/history-curves")
async def history_curves(request: Request, equipment_id: str = Query(alias="equipmentId"),
                         category: str = Query(), start: str = Query(alias="from"), end: str = Query(alias="to"),
                         task: str | None = Query(None, alias="taskNo"), user=Depends(monitor_reader),
                         db: AsyncSession = Depends(get_db)):
    return response(await reads.curves(db, get_profile(), user, equipment_id, category, task, start, end, language(request)))


async def admin_list(target, equipment_id, group_key, task, start, end, page, size, user, db):
    profile = admin_scope(user)
    return response(await reads.samples(db, profile, user, target,
        dict(equipment=equipment_id, group=group_key, task=task, start=start, end=end), page, size, admin=True))


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


async def save_observation_edits(db, row, item):
    changes = {name: value for name, value in item.model_dump(exclude_unset=True).items()
               if getattr(row, name) != value}
    if changes:
        row.updated_at = await current_clock(db)
        for name, value in changes.items():
            setattr(row, name, value)
    await db.commit()


@router.patch("/equipment/admin/latest-snapshots/{record_id}")
async def edit_latest(record_id: int, item: Remark, user=Depends(get_current_active_admin),
                      db: AsyncSession = Depends(get_db)):
    row, _ = await reads.detail(db, get_profile(), user, "latest", record_id)
    await save_observation_edits(db, row, item)
    return response((await reads.detail(db, get_profile(), user, "latest", record_id))[1])


@router.patch("/monitor/admin/history-samples/{record_id}")
async def edit_history(record_id: int, item: HistoryReview, user=Depends(get_current_active_admin),
                       db: AsyncSession = Depends(get_db)):
    row, _ = await reads.detail(db, get_profile(), user, "history", record_id)
    await save_observation_edits(db, row, item)
    return response((await reads.detail(db, get_profile(), user, "history", record_id))[1])
