"""五revision recorder和MySQL离线签名，保护旧58及旧四迁移字节。"""
import hashlib
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable, CreateIndex
from database import Base
from tests.test_business_module_migration import load
from tests.test_core_migration_baseline import MigrationRecorder, _table_signature, VERSIONS_DIR

pytestmark=pytest.mark.no_db
OLD_SHA = {'20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py': '7efeba1aef3270a1f7c51b6b7bbbf2af670e49ac2ffdca342e978a03ce573d1a', '20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py': 'f038e80badccf322292a9b4dca5bf2bb563bb5c15388f4745bc36fd02ca478f2', '20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py': '806b008ebc4d232326db9967132a5bdb5d507518dca96017592ed80e00d056eb', '20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py': '0950882badedd3abea8c61c2f7ed09c6176f8a0ee3edd5e5cf3b601766188914'}
NEW_TABLES={"equipment_temperature_samples","equipment_temperature_sample_receipts"}


def test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types():
    for name,digest in OLD_SHA.items():assert hashlib.sha256((VERSIONS_DIR/name).read_bytes()).hexdigest()==digest
    recorder=MigrationRecorder()
    migrations=[load(p) for p in sorted(VERSIONS_DIR.glob("*.py"))]
    assert [m.revision for m in migrations]==["d4e6f8a0b2c4","a6c8e0f2b4d6","b8d0f2a4c6e8","d2f4a6b8c0e2","e4f6a8b0c2d4"]
    for m in migrations[:-1]:m.op=recorder;m.upgrade()
    assert len(recorder.metadata.tables)==58
    before={name:_table_signature(t) for name,t in recorder.metadata.tables.items()}
    last=migrations[-1];last.op=recorder;last.upgrade()
    assert len(recorder.metadata.tables)==60
    for name,t in recorder.metadata.tables.items():
        assert _table_signature(t)==_table_signature(Base.metadata.tables[name]),name
        str(CreateTable(t).compile(dialect=mysql.dialect()))
        for index in t.indexes:str(CreateIndex(index).compile(dialect=mysql.dialect()))
    for name in NEW_TABLES:
        table=recorder.metadata.tables[name]
        assert table.c.sampled_at.type.dialect_impl(mysql.dialect()).fsp==3
        assert table.c.equipment_id.type.dialect_impl(mysql.dialect()).collation=="utf8mb4_bin"
        assert "UTC_TIMESTAMP(3)" in str(table.c.created_at.server_default.arg)
    sample=recorder.metadata.tables["equipment_temperature_samples"]
    for key in [f"zone{z}_{k}" for z in range(1,6) for k in ("set","act")]:
        assert sample.c[key].type.precision==30 and sample.c[key].type.scale==10
        assert sample.c[key].default is None and sample.c[key].server_default is None
    assert "actor_user_id" not in sample.c
    last.downgrade()
    assert len(recorder.metadata.tables)==58
    assert {name:_table_signature(t) for name,t in recorder.metadata.tables.items()}==before
    assert recorder.operations[-2:]==[("drop_table","equipment_temperature_sample_receipts"),("drop_table","equipment_temperature_samples")]


def test_single_explicit_head_and_no_data_migration():
    graph=ScriptDirectory.from_config(Config("alembic.ini"))
    assert graph.get_heads()==["e4f6a8b0c2d4"] and graph.get_bases()==["d4e6f8a0b2c4"]
    assert graph.get_revision("e4f6a8b0c2d4").down_revision=="d2f4a6b8c0e2"
    source=(VERSIONS_DIR/"20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py").read_text()
    for word in ("create_all", "stamp(", "bulk_insert", "execute(", "INSERT INTO"):
        assert word not in source


def test_prepared_mysql_comparison_preserves_literal_grouping_and_type_boundaries():
    import ast,re
    root=VERSIONS_DIR.parents[1]
    source=ast.parse((root/"tests_mysql/test_equipment_temperature.py").read_text())
    methods={node.name:node for node in ast.walk(source) if isinstance(node,ast.FunctionDef) and node.name in {"expression","normalized"}}
    namespace={"re":re}
    for node in methods.values():
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),"mysql-comparison","exec"),namespace)
    expression=namespace["expression"];normalized=namespace["normalized"]
    for a,b in [("quality = 'Good'","quality = 'good'"),("x='A B'","x='AB'"),("(a=1 OR b=2) AND c=3","a=1 OR (b=2 AND c=3)"),("NOT (a=1 AND b=2)","NOT a=1 AND b=2"),("x='(A)'","x='A'"),(None,"NULL"),("0","1"),("x y","xy"),("x@1","x1")]:
        assert expression(a)!=expression(b),(a,b)
    for a,b in [("((quality = 'good'))","`quality` = _utf8mb4'good'"),("current_timestamp()","now()"),("(UTC_TIMESTAMP(3))","utc_timestamp(3)")]:
        assert expression(a)==expression(b),(a,b)
    for a,b in [("DECIMAL(30,10)","DECIMAL(30,9)"),("DECIMAL(30,10)","DECIMAL(29,10)"),("INT UNSIGNED","INT"),("DATETIME(3)","DATETIME"),("VARCHAR(128)","VARCHAR(127)")]:
        assert normalized(a)!=normalized(b)
    assert normalized("VARCHAR(128) CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN")==normalized("VARCHAR(128) COLLATE UTF8MB4_BIN")
    for a,b in [("VARCHAR(128) CHARACTER SET LATIN1 COLLATE UTF8MB4_BIN","VARCHAR(128) COLLATE UTF8MB4_BIN"),
                ("VARCHAR(128) CHARACTER SET UTF8MB3 COLLATE UTF8MB4_BIN","VARCHAR(128) COLLATE UTF8MB4_BIN"),
                ("VARCHAR(128) CHARACTER SET UTF8MB4 COLLATE UTF8MB4_0900_AI_CI","VARCHAR(128) COLLATE UTF8MB4_BIN"),
                ("VARCHAR(128) CHARACTER SET UTF8MB4","VARCHAR(128)"),
                ("VARCHAR(127) CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN","VARCHAR(128) COLLATE UTF8MB4_BIN")]:
        assert normalized(a)!=normalized(b),(a,b)
