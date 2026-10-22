"""显式schema、实例锁、单SQLite/audit owner线程；父进程拥有执行事实。"""
from __future__ import annotations
import asyncio
from concurrent.futures import Future
from dataclasses import asdict
import fcntl
import json
import os
from pathlib import Path
import queue
import shutil
import sqlite3
import threading
import time
from field_flow.domain import Failure, Resource, canonical, digest, identity, require, valid_id
from field_flow.infrastructure.audit import Audit

STAMP = "strftime('%Y-%m-%dT%H:%M:%fZ','now')"
SCHEMA = f"""
PRAGMA page_size=4096; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL;
PRAGMA foreign_keys=ON; PRAGMA max_page_count=16384;
CREATE TABLE store_meta(schema_version INTEGER NOT NULL,implementation TEXT NOT NULL,mode TEXT NOT NULL CHECK(mode IN ('dry_run','execute')),instance_id TEXT NOT NULL,store_uuid TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT({STAMP}));
CREATE TABLE commands(source_id TEXT NOT NULL,command_id TEXT NOT NULL,flow_id TEXT NOT NULL,target_key TEXT NOT NULL,config_identity_hash TEXT NOT NULL,payload_hash TEXT NOT NULL,value_i16 INTEGER NOT NULL CHECK(value_i16 BETWEEN -32768 AND 32767),issued_at_ms INTEGER NOT NULL,expires_at_ms INTEGER NOT NULL,state TEXT NOT NULL CHECK(state IN ('pending','in_flight','confirmed','unknown','expired','canceled','simulated')),dispatch_count INTEGER NOT NULL CHECK(dispatch_count IN (0,1)),run_id TEXT NOT NULL,request_id TEXT,last_error_key TEXT,ack_kind TEXT,created_at TEXT NOT NULL DEFAULT({STAMP}),updated_at TEXT NOT NULL DEFAULT({STAMP}),PRIMARY KEY(source_id,command_id));
CREATE TABLE command_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,source_id TEXT NOT NULL,command_id TEXT NOT NULL,run_id TEXT NOT NULL,request_id TEXT,from_state TEXT,to_state TEXT NOT NULL,reason_key TEXT NOT NULL,summary TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT({STAMP}),FOREIGN KEY(source_id,command_id) REFERENCES commands(source_id,command_id));
CREATE TRIGGER immutable_intent BEFORE UPDATE OF source_id,command_id,flow_id,target_key,config_identity_hash,payload_hash,value_i16,issued_at_ms,expires_at_ms ON commands BEGIN SELECT RAISE(ABORT,'immutable_intent'); END;
CREATE TRIGGER preserve_commands BEFORE DELETE ON commands BEGIN SELECT RAISE(ABORT,'preserve_commands'); END;
CREATE TRIGGER events_update BEFORE UPDATE ON command_events BEGIN SELECT RAISE(ABORT,'append_only'); END;
CREATE TRIGGER events_delete BEFORE DELETE ON command_events BEGIN SELECT RAISE(ABORT,'append_only'); END;
"""


def init(directory, mode, instance):
    require(mode in ("dry_run", "execute") and valid_id(instance), "state_arguments")
    directory = Path(directory)
    try:
        directory.mkdir(mode=0o700)  # exist_ok=False; symlinks/existing data never overwritten.
        (directory / "instance.lock").touch(mode=0o600, exist_ok=False)
        with sqlite3.connect(directory / "state.sqlite") as db:
            db.executescript(SCHEMA)
            db.execute("INSERT INTO store_meta(schema_version,implementation,mode,instance_id,store_uuid) VALUES(1,'python',?,?,?)", (mode, instance, identity()))
    except OSError:
        raise Failure("state_exists_or_parent_missing") from None


def inspect(directory, tables=False):
    try:
        db = sqlite3.connect((Path(directory) / "state.sqlite").absolute().as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            result = {"meta": dict(db.execute("SELECT * FROM store_meta").fetchone()),
                      "counts": dict(db.execute("SELECT state,count(*) FROM commands GROUP BY state"))}
            if tables:
                result["tables"] = {name: [dict(r) for r in db.execute(f"SELECT * FROM {name}")]
                                    for name in ("store_meta", "commands", "command_events")}
            return result
        finally:
            db.close()
    except (sqlite3.Error, OSError, TypeError):
        raise Failure("state_read") from None


class State:
    def __init__(self, directory, mode, instance):
        self.directory, self.mode, self.instance = Path(directory), mode, instance
        self.run_id, self.healthy, self.finalized = identity(), True, False
        self.jobs, self.gates = queue.Queue(16), []
        self.command_limit, self.event_limit, self.fail_t3 = 10000, 90000, False
        self.lock_fd, self.audit, self.db = None, None, None
        self.ready = Future()
        self.thread = threading.Thread(target=self._loop, name="ff-sqlite-audit-owner")
        self.thread.start()

    @classmethod
    async def open(cls, directory, mode, instance):
        state = cls(directory, mode, instance)
        try:
            await asyncio.wait_for(asyncio.wrap_future(state.ready), 1.5)
            return state
        except BaseException:
            state.healthy = False
            end = time.monotonic()+1
            while state.thread.is_alive() and time.monotonic() < end:
                await asyncio.sleep(.001)
            if not state.thread.is_alive():
                state.thread.join()
            raise

    def _bad(self):
        self.healthy = False
        for gate in self.gates:
            gate.close()

    def _loop(self):
        try:
            require(not self.directory.is_symlink(), "state_symlink")
            self.lock_fd = os.open(self.directory / "instance.lock", os.O_RDWR | os.O_NOFOLLOW)
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Failure("state_locked") from None
            self.db = sqlite3.connect((self.directory / "state.sqlite").absolute().as_uri() + "?mode=rw", uri=True, timeout=.5)
            self.db.row_factory = sqlite3.Row
            meta = list(self.db.execute("SELECT schema_version,implementation,mode,instance_id FROM store_meta"))
            require(len(meta) == 1 and tuple(meta[0]) == (1, "python", self.mode, self.instance), "state_identity")
            self.db.executescript("PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; PRAGMA max_page_count=16384; PRAGMA busy_timeout=500;")
            self.audit = Audit(self.directory, self.run_id, self.instance)
            for row in list(self.db.execute("SELECT source_id,command_id FROM commands WHERE state='in_flight'")):
                self._transition(tuple(row), "unknown", "recovered_in_flight")
            self.audit.emit("process_start", result="ok")
            self.ready.set_result(None)
            while True:
                item = self.jobs.get()
                if item is None:
                    break
                fn, future, end = item
                try:
                    require(time.monotonic() < end, "state_deadline")
                    self.db.set_progress_handler(lambda: int(time.monotonic() >= end), 100)
                    value = fn()
                    if not future.cancelled():
                        future.set_result(value)
                except BaseException as exc:
                    if not isinstance(exc, Failure):
                        exc = Failure("state_io")
                    if str(exc) not in ("identity_conflict", "target_unknown", "capacity_paused", "state_transition"):
                        self._bad()
                    if not future.cancelled():
                        future.set_exception(exc)
                finally:
                    self.db.set_progress_handler(None, 0)
        except BaseException as exc:
            self._bad()
            if not self.ready.done():
                self.ready.set_exception(exc if isinstance(exc, Failure) else Failure("state_io"))
        finally:
            if self.db is not None:
                self.db.close()
            if self.audit is not None:
                self.audit.close()
            if self.lock_fd is not None:
                os.close(self.lock_fd)  # inherited lock share survives parent failure; no explicit LOCK_UN.
                self.lock_fd = None

    async def call(self, fn):
        future = Future()
        try:
            self.jobs.put_nowait((fn, future, time.monotonic() + 1))
            return await asyncio.wait_for(asyncio.wrap_future(future), 1.5)
        except (queue.Full, asyncio.TimeoutError):
            self._bad()
            raise Failure("state_deadline") from None

    async def event(self, event, **fields):
        return await self.call(lambda: self.audit.emit(event, **fields))

    def _capacity(self, new):
        command_count = self.db.execute("SELECT count(*) FROM commands").fetchone()[0]
        event_count = self.db.execute("SELECT count(*) FROM command_events").fetchone()[0]
        size = (self.directory / "state.sqlite").stat().st_size
        journal = self.directory / "state.sqlite-journal"
        require(not (new and command_count >= self.command_limit) and event_count < self.event_limit and
                size < 48 * 1024**2 and size + (journal.stat().st_size if journal.exists() else 0) < 128 * 1024**2 and
                shutil.disk_usage(self.directory).free >= 256 * 1024**2, "capacity_paused")

    def _unblocked(self, target):
        for row in self.db.execute("SELECT target_key FROM commands WHERE state='unknown'"):
            require(not target.overlaps(Resource(**json.loads(row[0]))), "target_unknown")

    async def admit(self, intent):
        def job():
            old = self.db.execute("SELECT payload_hash,state FROM commands WHERE source_id=? AND command_id=?", (intent.source_id, intent.command_id)).fetchone()
            h = digest(asdict(intent))
            if old:
                if old[0] != h:
                    self.audit.emit("identity_conflict", flow_id=intent.flow_id, command_id=intent.command_id, error_key="identity_conflict")
                    raise Failure("identity_conflict")
                return old[1]
            require(self.healthy, "audit_unhealthy")
            self._capacity(True); self._unblocked(intent.target)
            state = "pending" if self.mode == "execute" else "simulated"
            with self.db:
                self.db.execute("INSERT INTO commands(source_id,command_id,flow_id,target_key,config_identity_hash,payload_hash,value_i16,issued_at_ms,expires_at_ms,state,dispatch_count,run_id) VALUES(?,?,?,?,?,?,?,?,?,?,0,?)", (intent.source_id, intent.command_id, intent.flow_id, canonical(asdict(intent.target)), intent.config_identity_hash, h, intent.value, intent.issued_at_ms, intent.expires_at_ms, state, self.run_id))
                self._event_row((intent.source_id, intent.command_id), None, state, "intent", None, h)
            self.audit.emit("intent", flow_id=intent.flow_id, command_id=intent.command_id, new=state, state=state, result="durable")
            return state
        return await self.call(job)

    def _event_row(self, key, old, new, reason, request, summary="{}"):
        self.db.execute("INSERT INTO command_events(source_id,command_id,run_id,request_id,from_state,to_state,reason_key,summary) VALUES(?,?,?,?,?,?,?,?)", (*key, self.run_id, request, old, new, reason, summary))

    def _transition(self, key, new, reason, request=None):
        old, count, saved_request = self.db.execute("SELECT state,dispatch_count,request_id FROM commands WHERE source_id=? AND command_id=?", key).fetchone()
        request = request or saved_request
        require((old == "pending" and new in ("in_flight", "expired", "canceled") and count == 0) or
                (old == "in_flight" and new in ("confirmed", "unknown", "expired", "canceled") and count == 1), "state_transition")
        require(not (new == "confirmed" and self.fail_t3), "state_io")
        with self.db:
            n = self.db.execute(f"UPDATE commands SET state=?,dispatch_count=?,request_id=coalesce(?,request_id),last_error_key=?,ack_kind=?,updated_at={STAMP} WHERE source_id=? AND command_id=? AND state=?", (new, 1 if new == "in_flight" else count, request, reason if new == "unknown" else None, "s7_protocol" if new == "confirmed" else None, *key, old)).rowcount
            require(n == 1, "state_cas")
            self._event_row(key, old, new, reason, request)
        self.audit.emit("ack" if new == "confirmed" else new, command_id=key[1], request_id=request or "", old=old, new=new, state=new, result=reason)

    async def dispatch(self, intent, request):
        def job():
            require(self.healthy, "audit_unhealthy")
            self._capacity(False); self._unblocked(intent.target)
            self._transition((intent.source_id, intent.command_id), "in_flight", "dispatch_permit", request)
        return await self.call(job)

    async def finish(self, intent, new, reason):
        return await self.call(lambda: self._transition((intent.source_id, intent.command_id), new, reason))

    async def status(self, intent):
        return await self.call(lambda: self.db.execute("SELECT state FROM commands WHERE source_id=? AND command_id=?", (intent.source_id, intent.command_id)).fetchone()[0])

    async def snapshot(self):
        def job():
            counts = dict(self.db.execute("SELECT state,count(*) FROM commands GROUP BY state"))
            try:
                self._capacity(True); capacity = True
            except Failure:
                capacity = False
            return {"commands": counts, "log_writable": not self.audit.failed, "capacity": capacity}
        return await self.call(job)

    async def test_fault(self, kind):
        def job():
            if kind == "t3":
                self.fail_t3 = True
            else:
                self.audit.failed = True
                self.audit.emit("test_fault")
        return await self.call(job)

    async def close(self, deadline):
        self.jobs.put_nowait(None)
        while self.thread.is_alive() and time.monotonic() < deadline:
            await asyncio.sleep(.005)
        require(not self.thread.is_alive(), "state_join_incomplete")
        self.thread.join()
