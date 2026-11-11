"""v2 有界到期清理，按批提交并保留逐点顺序水位。"""
import time

from sqlalchemy import text

from ..crud import sync_v2_maintenance as crud
from ..v2_domain import wire_time

MAX_ROWS_PER_TRANSACTION = 200
MAX_BYTES_PER_TRANSACTION = 2 * 1024 * 1024
MAX_ROWS_PER_TICK = 2000
MAX_BYTES_PER_TICK = 20 * 1024 * 1024
MAX_SECONDS_PER_TICK = 2


def configure_timeouts(db, deadline):
    """每次新事务先约束行锁、元数据锁及只读查询。"""
    for command in ('SET SESSION innodb_lock_wait_timeout = 1', 'SET SESSION lock_wait_timeout = 1',
                    'SET SESSION max_execution_time = 1000'):
        if time.monotonic() >= deadline:
            raise TimeoutError('cleanup budget exhausted before target verification')
        db.execute(text(command))


def run(db, target, apply):
    deadline = time.monotonic() + MAX_SECONDS_PER_TICK
    rows = 0
    byte_count = 0
    now = None
    if not apply:
        configure_timeouts(db, deadline)
        if time.monotonic() >= deadline:
            db.rollback()
            raise TimeoutError('cleanup budget exhausted before target verification')
        now = crud.target_now(db, target)
        selected = []
        for item in crud.candidates(db, now, MAX_ROWS_PER_TRANSACTION, False, deadline):
            if len(selected) == MAX_ROWS_PER_TRANSACTION or sum(row[3] for row in selected) + item[3] > MAX_BYTES_PER_TRANSACTION:
                break
            selected.append(item)
        db.rollback()
        rows, byte_count = len(selected), sum(item[3] for item in selected)
    while apply and rows < MAX_ROWS_PER_TICK and byte_count < MAX_BYTES_PER_TICK and time.monotonic() < deadline:
        try:
            configure_timeouts(db, deadline)
        except TimeoutError:
            db.rollback()
            if now is None:
                raise
            break
        if time.monotonic() >= deadline:
            db.rollback()
            if now is None:
                raise TimeoutError('cleanup budget exhausted before target verification')
            break
        now = crud.target_now(db, target)
        if time.monotonic() >= deadline:
            db.rollback()
            break
        candidates = crud.candidates(db, now, min(MAX_ROWS_PER_TRANSACTION, MAX_ROWS_PER_TICK - rows), True, deadline)
        batch_rows = 0
        batch_bytes = 0
        for candidate in candidates:
            size = candidate[3]
            if (batch_bytes + size > MAX_BYTES_PER_TRANSACTION or byte_count + batch_bytes + size > MAX_BYTES_PER_TICK
                    or time.monotonic() >= deadline):
                break
            batch_rows += crud.clear(db, candidate, now)
            batch_bytes += size
        db.commit()
        rows += batch_rows
        byte_count += batch_bytes
        if not candidates or not batch_rows:
            break
    db.rollback()
    if now is None:
        raise TimeoutError('cleanup budget exhausted before target verification')
    oldest = None
    oldest_known = False
    if time.monotonic() < deadline:
        try:
            configure_timeouts(db, deadline)
            oldest = crud.oldest(db, now, deadline)
            oldest_known = True
        except TimeoutError:
            db.rollback()
    completed = crud.database_time(db)
    db.rollback()
    return {'rows': rows, 'bytes': byte_count, 'oldestExpiredAt': wire_time(oldest) if oldest else None,
            'oldestKnown': oldest_known, 'completedAt': wire_time(completed)}
