"""ARCH-OBS-003 使用明确专用 MySQL 实例，从真实旧接口写入并验证迁移后的重放。"""
import asyncio
from copy import deepcopy
from datetime import datetime, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from secrets import token_urlsafe
import shutil
import subprocess
import sys
import time
from uuid import UUID, uuid4

import pytest

ENV = ("OBS003_TEST_PORT", "OBS003_TEST_SERVER_UUID", "OBS003_TEST_PASSWORD", "OBS003_TEST_ACK",
       "OBS003_TEST_OLD_BACKEND")
if not all(key in os.environ for key in ENV):
    pytest.skip("ARCH-OBS-003 requires a dedicated MySQL 8.4 target and c9 source", allow_module_level=True)

import httpx
import pymysql

PORT, SERVER, PASSWORD, CONFIRM, OLD_PATH = (os.environ[key] for key in ENV)
if (not PORT.isdecimal() or not 20000 <= int(PORT) <= 65535 or str(UUID(SERVER)) != SERVER
        or CONFIRM != f"ARCH-OBS-003-r2:127.0.0.1:{PORT}:{SERVER}"):
    raise RuntimeError("isolated MySQL identity not explicitly confirmed")

ROOT = Path(__file__).resolve().parents[1]
OLD_ROOT = Path(OLD_PATH).resolve()
OLD = "c9e1a3b5d720"
ACQ = "da6c32f8a701"
NEW = "d8f2a4c6b915"
WRITES = {
    "latest": "/integration/equipment/latest-snapshots",
    "history": "/integration/monitor/history-samples",
    "energy": "/integration/energy/samples",
}
RENAMES = {
    "equipment_status_main": "equipment_main",
    "process_monitor_main": "monitor_main",
    "equipment_metric_configs": "observation_metric_configs",
    "equipment_metric_groups": "observation_metric_groups",
    "equipment_metric_slot_bindings": "observation_metric_slot_bindings",
}
OLD_RECEIPTS = "metric_ingest_receipts"
OBS_RECEIPTS = "observation_ingest_receipts"
ENERGY_RECEIPTS = "energy_ingest_receipts"


def sql(schema, statement, parameters=None):
    if schema is not None and not re.fullmatch(r"obs003_[0-9a-f]{16}", schema):
        raise RuntimeError("schema is not a generated OBS test fixture")
    with pymysql.connect(host="127.0.0.1", port=int(PORT), user="root", password=PASSWORD,
                         database=schema, autocommit=True, connect_timeout=5) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT @@server_uuid, VERSION(), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())")
        server, version, offset = cursor.fetchone()
        if server != SERVER or not version.startswith("8.4.") or offset != 28800:
            raise RuntimeError("isolated database identity mismatch")
        cursor.execute(statement, parameters)
        return cursor.fetchall()


def fixture_env(schema):
    env = dict(os.environ)
    env.update(APP_NAME="OBS003 fixture", APP_VERSION="1.0.0", DEBUG="False", TESTING="True",
               PRIMARY_DATABASE="mysql", MYSQL_ENABLED="True", MYSQL_HOST="127.0.0.1",
               MYSQL_PORT=PORT, MYSQL_USER="root", MYSQL_PASSWORD=PASSWORD, MYSQL_DATABASE="unused",
               TEST_MYSQL_DATABASE=schema, MYSQL_ROOT_USER="root", MYSQL_ROOT_PASSWORD=PASSWORD,
               JWT_SECRET_KEY="0" * 64, JWT_ALGORITHM="HS256", ACCESS_TOKEN_EXPIRE_MINUTES="5",
               REFRESH_TOKEN_EXPIRE_DAYS="1", API_V1_PREFIX="/api/v1", BACKEND_MOCK_ENABLED="False",
               ADMIN_BOOTSTRAP_ENABLED="False", PYTHONDONTWRITEBYTECODE="1")
    for prefix in ("ACQ_RETIREMENT", "ACQ_FACTS", "ACQ_REGISTRY", "OBS_RETIREMENT", "ACQ_CONSUMPTION", "OBS_RECEIPT"):
        env[f"{prefix}_EXPECTED_SCHEMA"] = schema
        env[f"{prefix}_EXPECTED_SERVER_UUID"] = SERVER
    env.update(ACQ_FACTS_OPERATION_ID="arch-obs003", ACQ_REGISTRY_R3_EMPTY_CONFIRMED="1",
               TASK_CUTOVER_SCHEMA=schema, TASK_CUTOVER_SERVER_UUID=SERVER, TASK_CUTOVER_OPERATION_ID="arch-obs003",
               TASK_R2_SCHEMA=schema, TASK_R2_SERVER_UUID=SERVER, TASK_R2_OPERATION_ID="arch-obs003-r2",
               TASK_R2_HISTORY_TIME_VERIFIED="Asia/Shanghai", OBS_RETIREMENT_WINDOW_CONFIRMED=f"{schema}:{SERVER}",
               ACQ_CONSUMPTION_WINDOW_CONFIRMED=f"{schema}:{SERVER}", OBS_RECEIPT_WINDOW_CONFIRMED=f"{schema}:{SERVER}")
    return env


def migrate(schema, revision, *, wrong_target=False, interrupt_at=None, account=None):
    env = fixture_env(schema)
    env["PYTHONPATH"] = str(ROOT)
    if account:
        env["MYSQL_USER"], env["MYSQL_PASSWORD"] = account
    if wrong_target:
        env["OBS_RECEIPT_EXPECTED_SERVER_UUID"] = str(uuid4())
    command = [sys.executable, "-m", "alembic", "-x", "obs_r10_writers_quiesced=yes", "upgrade", revision]
    if interrupt_at:
        command = [sys.executable, str(Path(__file__).resolve()), "interrupt", interrupt_at]
    return subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)


@pytest.fixture
def schema():
    name = f"obs003_{uuid4().hex[:16]}"
    sql(None, f"CREATE DATABASE `{name}` DEFAULT CHARACTER SET utf8mb4")
    try:
        yield name
    finally:
        # 仅回收该次测试刚创建的独占随机库。DDL 结果先断言再清理。
        sql(name, f"DROP DATABASE `{name}`")


def assert_success(result):
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def table_set(schema):
    return {row[0] for row in sql(schema, "SHOW TABLES")}


def row_snapshot(schema, tables):
    return {table: sorted(sql(schema, f"SELECT * FROM `{table}`"), key=repr) for table in tables}


def table_ddl_snapshot(schema, tables):
    return {table: sql(schema, f"SHOW CREATE TABLE `{table}`")[0][1] for table in tables}


def collation_snapshot(schema, tables):
    rows = sql(schema, """
        SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES
         WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME
    """)
    columns = sql(schema, """
        SELECT TABLE_NAME, COLUMN_NAME, COLLATION_NAME FROM information_schema.COLUMNS
         WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)
    return {table: (collation, [(name, rule) for owner, name, rule in columns if owner == table])
            for table, collation in rows if table in tables}


def run_http(schema, step, fixture):
    checkout = OLD_ROOT if step == "before" else ROOT
    if not (checkout / "app/equipment_observation/profile.py").is_file() or checkout == OLD_ROOT == ROOT:
        raise RuntimeError("provide a separate unmodified c9 backend source")
    env = fixture_env(schema)
    env["PYTHONPATH"] = str(checkout)
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), step, str(fixture)],
                          cwd=checkout, env=env, capture_output=True, text=True, timeout=90)


def test_empty_chain_and_preflight_refusals(schema):
    assert_success(migrate(schema, ACQ))
    before_tables = table_set(schema)
    before = row_snapshot(schema, (OLD_RECEIPTS, *RENAMES))
    result = migrate(schema, NEW, wrong_target=True)
    assert result.returncode != 0 and "mismatch" in result.stderr
    assert table_set(schema) == before_tables
    sql(schema, "CREATE TABLE equipment_main (id INT PRIMARY KEY)")
    result = migrate(schema, NEW)
    assert result.returncode != 0 and "occupied destination" in result.stderr
    sql(schema, "DROP TABLE equipment_main")
    sql(schema, f"INSERT INTO {OLD_RECEIPTS}(target,producer_id,event_id,request_digest,outcome) "
                "VALUES ('unknown','obs-test','unknown',REPEAT('x',32),'stored')")
    result = migrate(schema, NEW)
    assert result.returncode != 0 and "unknown observation receipt target" in result.stderr
    sql(schema, f"DELETE FROM {OLD_RECEIPTS} WHERE target='unknown' AND event_id='unknown'")
    assert table_set(schema) == before_tables
    assert row_snapshot(schema, (OLD_RECEIPTS, *RENAMES)) == before
    sql(schema, "CREATE TABLE observation_unexpected_reference (id BIGINT UNSIGNED PRIMARY KEY, "
                "FOREIGN KEY (id) REFERENCES metric_ingest_receipts(id))")
    result = migrate(schema, NEW)
    assert result.returncode and "unexpected foreign key" in result.stderr
    sql(schema, "DROP TABLE observation_unexpected_reference")
    sql(schema, "CREATE VIEW obs_dependency AS SELECT id FROM metric_ingest_receipts")
    result = migrate(schema, NEW)
    assert result.returncode and "object may depend" in result.stderr
    sql(schema, "DROP VIEW obs_dependency")
    user = f"limited_{uuid4().hex[:8]}"
    password = token_urlsafe(18)
    sql(schema, f"CREATE USER `{user}`@'%%' IDENTIFIED BY %s", (password,))
    try:
        sql(schema, f"GRANT ALL PRIVILEGES ON `{schema}`.* TO `{user}`@'%'")
        result = migrate(schema, NEW, account=(user, password))
        assert result.returncode and "requires global database object visibility" in result.stderr
    finally:
        sql(schema, f"DROP USER `{user}`@'%'")
    assert row_snapshot(schema, (OLD_RECEIPTS, *RENAMES)) == before
    sql(schema, f"ALTER DATABASE `{schema}` COLLATE utf8mb4_0900_as_cs")
    result = migrate(schema, NEW)
    assert result.returncode and "unsupported observation predecessor default collation" in result.stderr
    assert table_set(schema) == before_tables
    sql(schema, f"ALTER DATABASE `{schema}` COLLATE utf8mb4_0900_ai_ci")

    assert_success(migrate(schema, NEW))
    assert sql(schema, "SELECT version_num FROM alembic_version") == ((NEW,),)


def test_predecessor_guard_rejects_changed_check_and_collation(schema, tmp_path):
    assert_success(migrate(schema, OLD))
    assert_success(run_http(schema, "before", tmp_path / "http-state.json"))
    assert_success(migrate(schema, ACQ))
    before = table_set(schema)

    def assert_refused(reason):
        dirty_ddl = table_ddl_snapshot(schema, before)
        before_data = row_snapshot(schema, before)
        refused = migrate(schema, NEW)
        assert refused.returncode != 0 and reason in refused.stderr
        assert table_set(schema) == before
        assert table_ddl_snapshot(schema, before) == dirty_ddl
        assert row_snapshot(schema, before) == before_data
        assert sql(schema, "SELECT version_num FROM alembic_version") == ((ACQ,),)
    sql(schema, """
        ALTER TABLE equipment_metric_configs DROP CHECK ck_obs_r10_metric_type,
          ADD CONSTRAINT ck_obs_r10_metric_type CHECK (char_length(value_type) > 0)
    """)
    assert_refused("unexpected check constraints in equipment_metric_configs")
    sql(schema, """
        ALTER TABLE equipment_metric_configs DROP CHECK ck_obs_r10_metric_type,
          ADD CONSTRAINT ck_obs_r10_metric_type CHECK (value_type IN ('number','boolean','string'))
    """)
    sql(schema, """
        ALTER TABLE metric_ingest_receipts
          MODIFY target VARCHAR(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL
    """)
    assert_refused("unexpected receipt column definition: target")
    sql(schema, """
        ALTER TABLE metric_ingest_receipts
          MODIFY target VARCHAR(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL
    """)
    assert_success(migrate(schema, NEW))
    assert sql(schema, "SELECT version_num FROM alembic_version") == ((NEW,),)


def test_receipt_predecessor_and_copy_reject_extra_layout(schema, tmp_path):
    assert_success(migrate(schema, OLD))
    assert_success(run_http(schema, "before", tmp_path / "http-state.json"))
    assert_success(migrate(schema, ACQ))
    before = table_set(schema)
    clean_data = row_snapshot(schema, before)
    clean_ddl = table_ddl_snapshot(schema, before)
    index = "uq_obs_receipt_event"
    for change, reason, restore in (
        (
            "ADD CONSTRAINT ck_unexpected_receipt_limit CHECK (char_length(event_id) < 100)",
            "unexpected check constraints in metric_ingest_receipts",
            "DROP CHECK ck_unexpected_receipt_limit",
        ),
        (f"ALTER INDEX {index} INVISIBLE", "unexpected index definitions in metric_ingest_receipts",
         f"ALTER INDEX {index} VISIBLE"),
        (
            f"DROP INDEX {index}, ADD UNIQUE INDEX {index} (target DESC,producer_id,event_id)",
            "unexpected index definitions in metric_ingest_receipts",
            f"DROP INDEX {index}, ADD UNIQUE INDEX {index} (target,producer_id,event_id)",
        ),
        ("ALTER COLUMN outcome SET INVISIBLE", "unexpected receipt column definition: outcome",
         "ALTER COLUMN outcome SET VISIBLE"),
    ):
        sql(schema, f"ALTER TABLE {OLD_RECEIPTS} {change}")
        dirty_data = row_snapshot(schema, before)
        dirty_ddl = table_ddl_snapshot(schema, before)
        refused = migrate(schema, NEW)
        assert refused.returncode != 0 and reason in refused.stderr
        assert table_set(schema) == before
        assert row_snapshot(schema, before) == dirty_data
        assert table_ddl_snapshot(schema, before) == dirty_ddl
        sql(schema, f"ALTER TABLE {OLD_RECEIPTS} {restore}")
    assert table_ddl_snapshot(schema, before) == clean_ddl
    assert row_snapshot(schema, before) == clean_data

    refused = migrate(schema, NEW, interrupt_at="copied-check")
    assert refused.returncode != 0 and "unexpected check constraints in energy_ingest_receipts" in refused.stderr
    assert table_set(schema) == before | {ENERGY_RECEIPTS}
    assert sql(schema, f"SELECT COUNT(*) FROM {ENERGY_RECEIPTS}") == ((0,),)
    assert table_ddl_snapshot(schema, before) == clean_ddl
    assert row_snapshot(schema, before) == clean_data
    # 独占夹具中仅删除上面受控注入、未用且已检查为空的副本；正式恢复仍用备份。
    sql(schema, f"DROP TABLE {ENERGY_RECEIPTS}")

    assert_success(migrate(schema, NEW))
    assert sql(schema, "SELECT version_num FROM alembic_version") == ((NEW,),)
    assert_success(run_http(schema, "after", tmp_path / "http-state.json"))


def test_competing_writer_stays_locked_until_cutover(schema, tmp_path):
    assert_success(migrate(schema, ACQ))
    marker = tmp_path / "table-lock-acquired"
    release = tmp_path / "allow-migration"
    env = {**fixture_env(schema), "PYTHONPATH": str(ROOT),
           "OBS003_TEST_MARKER": str(marker), "OBS003_TEST_RELEASE": str(release)}
    command = [sys.executable, str(Path(__file__).resolve()), "interrupt", "lock"]
    running = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 15
        while not marker.exists() and running.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert marker.exists()
        with pymysql.connect(host="127.0.0.1", port=int(PORT), user="root", password=PASSWORD,
                             database=schema, autocommit=True, connect_timeout=5) as contender, contender.cursor() as cursor:
            cursor.execute("SELECT @@server_uuid, DATABASE()")
            assert cursor.fetchone() == (SERVER, schema)
            cursor.execute("SET SESSION lock_wait_timeout=1")
            for receipts in (OLD_RECEIPTS, ENERGY_RECEIPTS):
                with pytest.raises(pymysql.err.OperationalError, match="Lock wait timeout"):
                    cursor.execute(f"INSERT INTO `{receipts}` (target,producer_id,event_id,request_digest,outcome) "
                                   "VALUES ('energy','fixture','should-be-blocked',REPEAT('x',32),'pending')")
    finally:
        release.touch()
        stdout, stderr = running.communicate(timeout=40)
    assert running.returncode == 0, stdout + stderr
    for receipts in (OBS_RECEIPTS, ENERGY_RECEIPTS):
        assert sql(schema, f"SELECT COUNT(*) FROM `{receipts}`") == ((0,),)


def dump_or_restore(schema, utility, data=None):
    command = shutil.which(utility)
    if command is None:
        pytest.fail(f"isolated interrupted-migration recovery requires {utility}")
    sql(schema, "SELECT DATABASE()")
    options = [command, "--host=127.0.0.1", f"--port={PORT}", "--user=root"]
    if utility == "mysqldump":
        options.extend(("--single-transaction", "--triggers", "--set-gtid-purged=OFF", "--no-tablespaces"))
    result = subprocess.run([*options, schema], input=data, capture_output=True,
                            env={**os.environ, "MYSQL_PWD": PASSWORD}, timeout=60)
    assert result.returncode == 0, result.stderr.decode()
    return result.stdout


def triggers(schema):
    return sql(schema, """
        SELECT TRIGGER_NAME, ACTION_TIMING, EVENT_MANIPULATION, ACTION_STATEMENT
          FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE() ORDER BY TRIGGER_NAME
    """)


def test_interrupted_stages_restore_and_replay(schema, tmp_path):
    assert_success(migrate(schema, OLD))
    assert_success(run_http(schema, "before", tmp_path / "http-state.json"))
    assert_success(migrate(schema, ACQ))
    initial_tables = table_set(schema)
    initial = row_snapshot(schema, initial_tables)
    initial_triggers = triggers(schema)
    backup = dump_or_restore(schema, "mysqldump")
    for stage in ("copy", "foreign-key", "rename", "remove-source", "version"):
        interrupted = migrate(schema, NEW, interrupt_at=stage)
        assert interrupted.returncode and f"OBS003 interrupt after {stage}" in interrupted.stderr
        assert sql(schema, "SELECT version_num FROM alembic_version") == ((ACQ,),)
        assert ENERGY_RECEIPTS in table_set(schema)
        assert ("equipment_main" in table_set(schema)) == (stage in {"rename", "remove-source", "version"})
        energy_parent = sql(schema, """
            SELECT REFERENCED_TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE
             WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='energy_consumption_main'
               AND COLUMN_NAME='ingest_receipt_id'
        """)
        assert energy_parent == (((OLD_RECEIPTS if stage == "copy" else ENERGY_RECEIPTS),),)
        assert sql(schema, f"SELECT COUNT(*) FROM {ENERGY_RECEIPTS}") == (
            (0 if stage == "copy" else len([row for row in initial[OLD_RECEIPTS] if row[1] == "energy"]),),
        )
        rerun = migrate(schema, NEW)
        assert rerun.returncode and "partial OBS receipt separation" in rerun.stderr
        assert triggers(schema) == initial_triggers
        # 仅在已核对 UUID 的独占测试库执行备份恢复。实际库切换另行授权。
        sql(schema, f"DROP DATABASE `{schema}`")
        sql(None, f"CREATE DATABASE `{schema}` DEFAULT CHARACTER SET utf8mb4")
        dump_or_restore(schema, "mysql", backup)
        assert table_set(schema) == initial_tables
        assert row_snapshot(schema, initial_tables) == initial
        assert triggers(schema) == initial_triggers

    assert_success(migrate(schema, NEW))
    assert_success(run_http(schema, "after", tmp_path / "http-state.json"))


def seed_legacy_acquisition(schema):
    sql(schema, """
        INSERT INTO plc_source_registry (plc_id,instance_id,source_generation,source_type,
            retired_generations,registration_revision)
        VALUES ('obs-src','obs-instance','g1','daa',JSON_ARRAY(),UUID())
    """)
    sql(schema, """
        INSERT INTO plc_facts_history (instance_id,sample_id,plc_id,db_number,source_generation,source_seq,
            points_json,content_hash,sampled_at,stored_at,expires_at,source_type)
        VALUES ('obs-instance','obs-fact','obs-src',21,'g1',1,
            JSON_ARRAY(JSON_OBJECT('pointId','zero','dataType','INT','value',0,'quality','good')),
            UNHEX(REPEAT('42',32)),NOW(6),NOW(6),NOW(6)+INTERVAL 1 DAY,'daa')
    """)
    sql(schema, """
        INSERT INTO plc_facts_latest (plc_id,db_number,point_id,data_type,value_json,quality,observed_at,expires_at,
            instance_id,source_generation,source_seq,sample_id)
        VALUES ('obs-src',21,'zero','INT',CAST('0' AS JSON),'good',NOW(6),NOW(6)+INTERVAL 1 DAY,
            'obs-instance','g1',1,'obs-fact')
    """)
    sql(schema, """
        INSERT INTO energy_price_hours (electric_price,hydrogen_price,argon_price,operator,observed_at,hour_start)
        VALUES (0.55,1.25,2.9,'fixture', '2026-01-01 00:01:00', '2026-01-01 00:00:00')
    """)


def seed_acquisition_runtime_state(schema):
    consumer, delivery, operation = str(uuid4()), str(uuid4()), str(uuid4())
    sql(schema, """
        INSERT INTO acq_consumers VALUES
        (%s,'obs-src',21,'retained',NOW(6),1,0,0,NULL,NULL,'obs-dest',21,'obs-dest-instance',
         'g1','running',NULL,0,NULL,NULL)
    """, (consumer,))
    sql(schema, """
        INSERT INTO acq_consumer_deliveries VALUES
        (%s,%s,1,'config-v1',UNHEX(REPEAT('10',32)),'serializer.v1',UNHEX(REPEAT('20',32)),NOW(6),NULL)
    """, (consumer, delivery))
    sql(schema, """
        INSERT INTO acq_consumer_operations VALUES
        (%s,%s,UNHEX(REPEAT('30',32)),JSON_OBJECT('eventSeq','1'))
    """, (consumer, operation))


@pytest.mark.parametrize("collation", ("utf8mb4_0900_ai_ci", "utf8mb4_unicode_ci"))
def test_populated_c9_acq_and_observation_chain(schema, tmp_path, collation):
    # 测试夹具自己的随机库在创建任何前驱表前配置默认规则。
    sql(schema, f"ALTER DATABASE `{schema}` CHARACTER SET utf8mb4 COLLATE {collation}")
    assert_success(migrate(schema, OLD))
    seed_legacy_acquisition(schema)
    state = tmp_path / "http-state.json"
    assert_success(run_http(schema, "before", state))
    old_tables = table_set(schema)
    before_c9 = row_snapshot(schema, old_tables - {"alembic_version"})
    assert_success(migrate(schema, ACQ))
    assert row_snapshot(schema, before_c9) == before_c9
    assert sql(schema, "SELECT event_seq,sample_id FROM acq_consumption_events") == ((1, b"obs-fact"),)
    seed_acquisition_runtime_state(schema)
    old_triggers = triggers(schema)
    before_tables = table_set(schema)
    sql(schema, f"UPDATE {OLD_RECEIPTS} SET target='energy' WHERE event_id='replace'")
    refusal = migrate(schema, NEW)
    assert refusal.returncode and "invalid latest sample owner" in refusal.stderr
    assert table_set(schema) == before_tables
    sql(schema, f"UPDATE {OLD_RECEIPTS} SET target='latest' WHERE event_id='replace'")
    history_id, = sql(schema, f"SELECT result_record_id FROM {OLD_RECEIPTS} WHERE target='history' AND event_id='shared'")[0]
    sql(schema, f"UPDATE {OLD_RECEIPTS} SET result_record_id=999999 WHERE target='history' AND event_id='shared'")
    refusal = migrate(schema, NEW)
    assert refusal.returncode and "invalid history sample owner" in refusal.stderr
    assert table_set(schema) == before_tables
    sql(schema, f"UPDATE {OLD_RECEIPTS} SET result_record_id=%s WHERE target='history' AND event_id='shared'", (history_id,))
    preserved = before_tables - set(RENAMES) - {OLD_RECEIPTS, "alembic_version"}
    before = row_snapshot(schema, (*preserved, *RENAMES, OLD_RECEIPTS))
    before_collation = collation_snapshot(schema, (*RENAMES, OLD_RECEIPTS, "energy_consumption_main"))
    assert all(table_rule == collation for table_rule, _ in before_collation.values())
    assert dict(before_collation[OLD_RECEIPTS][1])["target"] == collation
    sql(schema, f"ALTER TABLE {OLD_RECEIPTS} AUTO_INCREMENT=1000")
    assert_success(migrate(schema, NEW))
    assert sql(schema, "SELECT version_num FROM alembic_version") == ((NEW,),)
    assert table_set(schema) == (before_tables - set(RENAMES) - {OLD_RECEIPTS}
                                 | set(RENAMES.values()) | {OBS_RECEIPTS, ENERGY_RECEIPTS})
    assert row_snapshot(schema, preserved) == {name: before[name] for name in preserved}
    assert len(old_triggers) == 3 and triggers(schema) == old_triggers
    assert collation_snapshot(schema, (*RENAMES.values(), OBS_RECEIPTS, ENERGY_RECEIPTS, "energy_consumption_main")) == {
        **{destination: before_collation[source] for source, destination in RENAMES.items()},
        OBS_RECEIPTS: before_collation[OLD_RECEIPTS], ENERGY_RECEIPTS: before_collation[OLD_RECEIPTS],
        "energy_consumption_main": before_collation["energy_consumption_main"],
    }
    assert row_snapshot(schema, RENAMES.values()) == {dest: before[src] for src, dest in RENAMES.items()}
    assert row_snapshot(schema, (OBS_RECEIPTS, ENERGY_RECEIPTS)) == {
        dest: [row for row in before[OLD_RECEIPTS] if row[1] in targets]
        for dest, targets in ((OBS_RECEIPTS, {"latest", "history"}), (ENERGY_RECEIPTS, {"energy"}))
    }
    assert sql(schema, """
        SELECT TABLE_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
          FROM information_schema.KEY_COLUMN_USAGE
         WHERE TABLE_SCHEMA=DATABASE() AND COLUMN_NAME='ingest_receipt_id' ORDER BY TABLE_NAME
    """) == (("energy_consumption_main", ENERGY_RECEIPTS, "id"), ("equipment_main", OBS_RECEIPTS, "id"),
             ("monitor_main", OBS_RECEIPTS, "id"))
    assert_success(run_http(schema, "after", state))
    assert sql(schema, f"SELECT MIN(id) FROM {OBS_RECEIPTS} WHERE event_id='new'") == ((1000,),)
    assert sql(schema, f"SELECT MIN(id) FROM {ENERGY_RECEIPTS} WHERE event_id='new'") == ((1000,),)
    assert sql(schema, f"SELECT COUNT(*) FROM {OBS_RECEIPTS} WHERE event_id='parallel'") == ((1,),)
    assert sql(schema, f"SELECT COUNT(*) FROM {ENERGY_RECEIPTS} WHERE event_id='parallel'") == ((1,),)


async def http_run(step, state):
    from app.user.models.user import User
    from app.equipment_observation.profile import get_profile
    from core.registrar import create_app
    from core.security import hash_password
    from database import async_engine, async_session_maker
    from sqlalchemy import text

    path = state.with_name("profile.json")
    os.environ.update(OBSERVATION_ENABLED="true", OBSERVATION_PROFILE_FILE=str(path))
    revision = OLD if step == "before" else NEW
    async with async_session_maker() as session:
        current = (await session.execute(text(
            "SELECT DATABASE(), @@server_uuid, (SELECT version_num FROM alembic_version), CURRENT_TIMESTAMP(6)"
        ))).one()
        name, server, found_revision, now = current
        assert (name, server, found_revision) == (os.environ["TEST_MYSQL_DATABASE"], SERVER, revision)
        if step == "before":
            password = token_urlsafe(18)
            session.add(User(username="obs-admin", name="OBS Admin", role="admin",
                             password=hash_password(password), is_active=True))
            await session.commit()
            evidence = {"password": password, "posts": [], "reads": []}
        else:
            evidence = json.loads(state.read_text())
    device, meter, group = "line-obs003", "meter-obs003", "process"
    producers = []
    keys = {"obs-writer": "obs-writer-isolated-token", "obs-second": "obs-second-isolated-token"}
    for producer, token in keys.items():
        producers.append({
            "producerId": producer, "kind": "external", "enabled": True,
            "tokenSha256": sha256(token.encode()).hexdigest(),
            "grants": [{"equipmentId": device, "groupKey": group, "metricKeys": ["temperature", "speed"],
                        "target": target} for target in ("latest", "history")],
            "energyGrants": [{"meterId": meter, "groupKey": "electricity", "metricKeys": ["energy"]}],
        })
    profile = {
        "target": {"schema": name, "serverUuid": server, "schemaRevision": revision},
        "devices": [{"equipmentId": device, "nameZh": "测试", "nameEn": "Fixture",
                     "staleAfterSeconds": 3600, "futureToleranceSeconds": 30}],
        "readScopes": {"admin": [device]}, "meters": [{"meterId": meter, "nameZh": "表计", "nameEn": "Meter"}],
        "meterReadScopes": {"admin": [meter]}, "producers": producers, "groupSettings": [], "historyRules": [],
    }
    path.write_text(json.dumps(profile))
    path.chmod(0o600)
    properties = {"nameZh": "合成指标", "nameEn": "Synthetic", "enabled": True}
    previous_time = now - timedelta(minutes=5)
    def stamp(value):
        return value.isoformat(timespec="microseconds") + "+08:00"

    def payload(event, moment=previous_time, reading=0):
        return {"eventId": event, "data": {"equipmentId": device, "taskNo": "000042",
                "observedAt": stamp(moment), "quality": "good", "groups": {group: {"temperature": reading, "speed": 0}}}}

    def meter_payload(event, moment=previous_time):
        return {"eventId": event, "data": {"meterId": meter, "groupKey": "electricity", "quality": "good",
                "observedAt": stamp(moment), "intervalStartAt": stamp(moment - timedelta(seconds=60)),
                "intervalEndAt": stamp(moment), "values": {"energy": 3}}}

    app = create_app(testing=True)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture/api/v1") as client:
        async def send(method, route, status=200, **kwargs):
            reply = await client.request(method, route, **kwargs)
            assert reply.status_code == status, (route, status, reply.status_code, reply.text)
            return reply.json().get("data")

        auth = await send("POST", "/auth/login", json={"username": "obs-admin", "password": evidence["password"]})
        client.headers["Authorization"] = f"Bearer {auth.get('accessToken') or auth['access_token']}"

        async def post(target, body, producer="obs-writer", code=200):
            headers = {"Authorization": "Bearer " + keys[producer]}
            return await send("POST", WRITES[target], code, headers=headers, json=body)

        async def record(target, body, outcome="stored", producer="obs-writer"):
            reply = await post(target, body, producer)
            assert reply["outcome"] == outcome
            evidence["posts"].append([target, body, producer, reply])
            return reply

        async def concurrent(target, body):
            headers = {"Authorization": "Bearer " + keys["obs-writer"]}
            responses = await asyncio.gather(*(client.post(WRITES[target], json=body, headers=headers) for _ in range(2)))
            assert any(reply.status_code == 200 for reply in responses)
            accepted = await post(target, body)
            for reply in responses:
                if reply.status_code == 503:
                    # InnoDB may choose one concurrent transaction as a deadlock victim.
                    assert reply.json()["errorCode"] == "equipment_observation.not_ready"
                else:
                    assert reply.status_code == 200 and reply.json()["data"] == accepted
            return accepted

        if step == "before":
            await send("POST", "/equipment/metric-groups", json={
                **properties, "groupKey": group, "category": "temperature", "sortOrder": 0})
            for number, (key, unit) in enumerate((("temperature", "°C"), ("speed", "m/s")), 1):
                await send("POST", "/equipment/metric-configs", json={
                    "metricKey": key, "sourceGroupKey": group, "nameZh": "合成", "nameEn": key,
                    "category": "temperature", "valueType": "number", "unit": unit})
                await send("POST", "/equipment/metric-slot-bindings", json={
                    "target": "latest", "groupKey": group, "slotNo": number, "metricKey": key, "enabled": True})
            await record("history", payload("no-history"), "no_history_metrics")
            for number, key in enumerate(("temperature", "speed"), 1):
                await send("POST", "/equipment/metric-slot-bindings", json={
                    "target": "history", "groupKey": group, "slotNo": number, "metricKey": key, "enabled": True})
            await send("POST", "/equipment/card-configs", json={
                "cardKey": "fixture", "pageKey": "temperature", "titleZh": "测试", "titleEn": "Fixture",
                "enabled": True, "sortOrder": 0, "items": [{"metricKey": "temperature", "enabled": True}]})
            await send("POST", "/monitor/curve-configs", json={
                "curveGroupKey": "fixture", "category": "temperature", "titleZh": "测试", "titleEn": "Fixture",
                "enabled": True, "sortOrder": 0, "series": [{"metricKey": "temperature", "enabled": True}]})
            await send("POST", "/energy/metric-configs", json={
                **properties, "meterId": meter, "groupKey": "electricity", "metricKey": "energy", "slotNo": 1,
                "valueType": "number", "quantityKey": "energy", "measurementMode": "interval", "unit": "kWh",
                "rules": {"continuityConfirmed": True, "maxGapSeconds": 3600}})
            latest_sample = await record("latest", payload("shared"))
            history_sample = await record("history", payload("shared"))
            await record("energy", meter_payload("shared"))
            await record("latest", payload("equal"), "already_stored")
            await record("latest", payload("stale", previous_time - timedelta(seconds=1)), "stale")
            await record("latest", {**payload("replace", previous_time + timedelta(seconds=1), 9),
                                   "mappingId": "mapping", "mappingRevision": "1",
                                   "sourceRefs": [{"kind": "synthetic", "payload": {"value": 0}}]},
                         producer="obs-second")
            old_parallel = meter_payload("parallel-old")
            accepted = await concurrent("energy", old_parallel)
            evidence["posts"].append(["energy", old_parallel, "obs-writer", accepted])
            for route, params in (
                ("/equipment/observation-options", {}),
                ("/monitor/observation-options", {}),
                ("/equipment/sampled-tasks", {"equipmentId": device}),
                ("/equipment/metric-groups", {}),
                ("/equipment/metric-configs", {}),
                ("/equipment/metric-slot-bindings", {"target": "latest", "groupKey": group}),
                ("/equipment/metric-slot-bindings", {"target": "history", "groupKey": group}),
                ("/equipment/observation-list-columns", {"target": "latest"}),
                ("/equipment/observation-list-columns", {"target": "history"}),
                ("/equipment/card-configs", {"pageKey": "temperature"}),
                ("/monitor/curve-configs", {"category": "temperature"}),
                ("/equipment/admin/latest-snapshots", {"equipmentId": device}),
                ("/monitor/admin/history-samples", {"equipmentId": device}),
                (f"/equipment/admin/latest-snapshots/{latest_sample['recordId']}", {}),
                (f"/monitor/admin/history-samples/{history_sample['recordId']}", {}),
                ("/energy/consumption/options", {}),
                ("/energy/consumption/definitions", {"meterId": meter}),
                ("/energy/metric-configs", {"meterId": meter, "groupKey": "electricity"}),
                ("/energy/admin/consumption-samples", {"meterId": meter, "groupKey": "electricity"}),
                ("/energy/current", {}),
                ("/equipment/latest-cards", {"equipmentId": device, "pageKey": "temperature"}),
                ("/monitor/history-samples", {"equipmentId": device, "taskNo": "000042"}),
                ("/monitor/history-curves", {"equipmentId": device, "category": "temperature",
                                            "from": stamp(previous_time - timedelta(minutes=1)), "to": stamp(now)}),
                ("/energy/consumption/summary", {"meterId": meter, "groupKey": "electricity", "metricKey": "energy",
                                                 "from": stamp(previous_time - timedelta(minutes=1)), "to": stamp(now)}),
                ("/energy/consumption/samples", {"meterId": meter, "groupKey": "electricity"}),
            ):
                evidence["reads"].append([route, params, await send("GET", route, params=params)])
            machine = {"Authorization": "Bearer " + keys["obs-writer"]}
            evidence["machine_reads"] = [
                [route, params, await send("GET", route, params=params, headers=machine)]
                for route, params in (
                    ("/integration/metric-definitions", {"equipmentId": device}),
                    ("/integration/energy/metric-definitions", {"meterId": meter, "groupKey": "electricity"}),
                )
            ]
            state.write_text(json.dumps(evidence))
            state.chmod(0o600)
        else:
            for target, body, producer, reply in evidence["posts"]:
                assert await post(target, body, producer) == reply
                changed = deepcopy(body)
                changed["data"]["observedAt"] = stamp(now - timedelta(seconds=1))
                await post(target, changed, producer, code=409)
                await send("POST", WRITES[target], 401, json=body, headers={"Authorization": "Bearer invalid"})
                scope = "energyGrants" if target == "energy" else "grants"
                writer = get_profile()["producers"][producer]
                grants = writer[scope]
                writer[scope] = []
                try:
                    await post(target, changed, producer, code=403)
                finally:
                    writer[scope] = grants
            for route, params, expected in evidence["reads"]:
                assert await send("GET", route, params=params) == expected, route
            machine = {"Authorization": "Bearer " + keys["obs-writer"]}
            for route, params, expected in evidence["machine_reads"]:
                assert await send("GET", route, params=params, headers=machine) == expected, route
            for target in WRITES:
                body = meter_payload("new", now) if target == "energy" else payload("new", now, 2)
                assert (await post(target, body))["outcome"] == "stored"
            for target in ("history", "energy"):
                body = meter_payload("parallel", now) if target == "energy" else payload("parallel", now)
                assert (await concurrent(target, body))["outcome"] == "stored"

            from sqlalchemy.ext.asyncio import AsyncSession
            original_commit = AsyncSession.commit
            for target, committed in (("history", False), ("energy", True)):
                event = "commit-lost" if committed else "commit-rolled-back"
                body = meter_payload(event, now) if target == "energy" else payload(event, now)

                async def interrupt_commit(session):
                    AsyncSession.commit = original_commit
                    if committed:
                        await original_commit(session)
                    raise OSError("synthetic commit fault")

                AsyncSession.commit = interrupt_commit
                try:
                    await post(target, body, code=503)
                finally:
                    AsyncSession.commit = original_commit
                async with async_session_maker() as session:
                    table = ENERGY_RECEIPTS if target == "energy" else OBS_RECEIPTS
                    count = (await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE event_id=:id"),
                                                   {"id": event})).scalar_one()
                    assert count == int(committed)
                reply = await post(target, body)
                assert reply["outcome"] == "stored" and await post(target, body) == reply
    await async_engine.dispose()


def interrupt_migration(stage):
    from alembic.config import main
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    statements = {
        "copy": "INSERT INTO `energy_ingest_receipts`",
        "copied-check": "CREATE TABLE `energy_ingest_receipts` LIKE",
        "foreign-key": "ALTER TABLE `energy_consumption_main` DROP FOREIGN KEY",
        "rename": "RENAME TABLE `equipment_status_main`",
        "remove-source": "DELETE FROM `observation_ingest_receipts` WHERE",
        "version": "UPDATE alembic_version SET",
        "lock": "LOCK TABLES",
    }

    def fail(conn, cursor, statement, parameters, execution, many):
        if not statement.strip().startswith(statements[stage]) or (stage == "version" and NEW not in statement):
            return
        if stage == "copied-check":
            sql(os.environ["TEST_MYSQL_DATABASE"], f"ALTER TABLE {ENERGY_RECEIPTS} "
                "ADD CONSTRAINT ck_unexpected_receipt_limit CHECK (char_length(event_id) < 100)")
        elif stage == "lock":
            Path(os.environ["OBS003_TEST_MARKER"]).touch()
            release = Path(os.environ["OBS003_TEST_RELEASE"])
            deadline = time.monotonic() + 25
            while not release.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            assert release.exists(), "competing writer fixture did not release migration"
        else:
            raise RuntimeError(f"OBS003 interrupt after {stage}")

    # SQLAlchemy callback after each completed server statement, ahead of the next stage.
    event.listen(Engine, "after_cursor_execute", fail)
    main(argv=["-x", "obs_r10_writers_quiesced=yes", "upgrade", NEW])


if __name__ == "__main__":
    if sys.argv[1] == "interrupt":
        interrupt_migration(sys.argv[2])
    else:
        asyncio.run(http_run(sys.argv[1], Path(sys.argv[2])))
