"""登记管理、旧身份碰撞保护与读取选项投影。"""
from contextlib import suppress
import hashlib
import re

from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from ..domain import ObservationError, reject, wire_time
from ..models import HistorySample, LatestSnapshot, Receipt, WriteSource
from ..profile import WRITE_SOURCES_REVISION
from .guard import current_clock, probe_target

_SOURCE_KEY = re.compile(r"[A-Za-z0-9_.-]{1,64}")
_STORAGE_ID = re.compile(r"obsreg_[0-9a-f]{57}")


def source_key(value):
    if not isinstance(value, str) or not _SOURCE_KEY.fullmatch(value):
        reject()
    return value


def storage_identity(key):
    return "obsreg_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:57]


def registry_available(profile):
    return profile.get("target", {}).get("schemaRevision") == WRITE_SOURCES_REVISION


def profile_identities(profile):
    return {key for kind in ("devices", "producers") for key in profile.get(kind, {}) if _STORAGE_ID.fullmatch(key)}


async def check_profile(db, profile, *, writing_as=()):
    if not registry_available(profile):
        return
    identities = profile_identities(profile)
    active = identities.intersection(writing_as)
    if active:
        isolation = (await db.execute(text("SELECT @@transaction_isolation"))).scalar_one()
        if isolation not in ("REPEATABLE-READ", "SERIALIZABLE"):
            reject("not_ready", 503)
        # 锁住参与旧写入的精确映射或其唯一索引间隙，避免并发登记先于旧写入提交。
        for identity in sorted(active):
            query = select(WriteSource.source_key).where(WriteSource.storage_identity == identity)
            if (await db.execute(query.with_for_update(read=True))).first():
                reject("configuration_conflict", 503)
    if identities - active:
        query = select(WriteSource.source_key).where(WriteSource.storage_identity.in_(identities - active)).limit(1)
        if (await db.execute(query)).first():
            reject("configuration_conflict", 503)


async def source_row(db, key, *, lock=False):
    query = select(WriteSource).where(WriteSource.source_key == key)
    if lock:
        query = query.with_for_update()
    return (await db.execute(query)).scalar_one_or_none()


async def visible_sources(db, profile, *, include_deleted=False):
    if not registry_available(profile):
        return []
    query = select(WriteSource).order_by(WriteSource.source_key)
    if not include_deleted:
        query = query.where(WriteSource.deleted_at.is_(None))
    return list((await db.execute(query)).scalars())


def data(row):
    return {"sourceKey": row.source_key, "name": row.name, "enabled": row.enabled,
            "createdAt": wire_time(row.created_at), "updatedAt": wire_time(row.updated_at)}


def source_projection(row):
    return {"sourceKey": row.source_key, "sourceName": row.name, "sourceDeleted": row.deleted_at is not None}


async def list_sources(db, profile):
    await probe_target(db, profile["target"])
    await check_profile(db, profile)
    return [data(row) for row in await visible_sources(db, profile)]


async def commit(db):
    try:
        await db.commit()
    except Exception:
        with suppress(Exception):
            await db.rollback()
        reject("commit_unknown", 503)


async def create(db, profile, key, name, enabled):
    key = source_key(key)
    identity = storage_identity(key)
    now = await probe_target(db, profile["target"])
    await check_profile(db, profile)
    if identity in profile_identities(profile):
        reject("configuration_conflict", 409)
    row = WriteSource(source_key=key, storage_identity=identity, name=name, enabled=enabled,
                      created_at=now, updated_at=now)
    db.add(row)
    try:
        # 先保留唯一索引项，再用当前读排除已提交的旧身份。
        await db.flush()
        for model, column in ((LatestSnapshot, LatestSnapshot.equipment_id),
                              (HistorySample, HistorySample.equipment_id), (Receipt, Receipt.producer_id)):
            query = select(model.id).where(column == identity)
            if model is Receipt:
                query = query.where(Receipt.target.in_(("latest", "history")))
            if (await db.execute(query.limit(1).with_for_update(read=True))).first():
                reject("configuration_conflict", 409)
    except IntegrityError:
        # 路由会把业务异常变成响应，不能依赖请求依赖看到异常并回滚。
        await db.rollback()
        reject("configuration_conflict", 409)
    except (ObservationError, DBAPIError):
        await db.rollback()
        raise
    result = data(row)
    await commit(db)
    return result


async def change(db, profile, key, changes, *, delete=False):
    await probe_target(db, profile["target"])
    await check_profile(db, profile)
    row = await source_row(db, source_key(key), lock=True)
    if row is None or row.deleted_at is not None:
        reject("not_found", 404)
    if not delete:
        changes = {field: value for field, value in changes.items() if getattr(row, field) != value}
        if not changes:
            result = data(row)
            await db.rollback()
            return result
    now = await current_clock(db)
    if delete:
        row.deleted_at, row.enabled = now, False
        result = {"sourceKey": key, "deleted": True}
    else:
        for field, value in changes.items():
            setattr(row, field, value)
        result = None
    row.updated_at = now
    if not delete:
        result = data(row)
    try:
        await db.flush()
    except DBAPIError:
        await db.rollback()
        raise
    await commit(db)
    return result
