"""可重建的C0→C2/E/F公开fixture；不复制env、连接DB或执行迁移。"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

C0 = "363b297bffe65e020108f5504766b4fb1ec3b381"
CORE_PATCH = ("app/module_registry.py", "app/module_contract.py", "app/module_preflight.py",
              "common/exceptions.py", "core/registrar.py", "app/system/manifest.py",
              "app/system/crud/async_projection_mapping.py")
CORE_PACKAGES = ("user", "system", "control_agent", "schema_maintenance", "monitor", "aiis_demo")
CORE_TABLES = {"users", "token_blacklist", "sys_dicts", "sys_dict_items", "projection_mapping_sets",
               "projection_mapping_revisions", "projection_mapping_bindings", "projection_mapping_audit_events",
               "projection_runtime_cursors", "projection_runtime_audit_events", "control_agent_gate_tokens",
               "monitor_collector_states", "plc_db_block_raw_snapshots", "plc_db_block_latest_snapshots"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def public_environment():
    """公开占位参数；禁writer/mock/bootstrap；无秘密，无env文件。"""
    return dict(APP_NAME="Admission fixture", APP_VERSION="1.0.0", DEBUG="False", TESTING="True",
                MYSQL_HOST="127.0.0.1", MYSQL_PORT="1", MYSQL_USER="fixture", MYSQL_PASSWORD="fixture",
                MYSQL_DATABASE="fixture_primary", TEST_MYSQL_DATABASE="fixture_test", MYSQL_ROOT_USER="fixture",
                MYSQL_ROOT_PASSWORD="fixture", JWT_SECRET_KEY="public-fixture-secret-32-characters", JWT_ALGORITHM="HS256",
                ACCESS_TOKEN_EXPIRE_MINUTES="30", REFRESH_TOKEN_EXPIRE_DAYS="7", API_V1_PREFIX="/api/v1",
                BACKEND_MOCK_ENABLED="False", PROJECTION_RUNNER_ENABLED="False", ADMIN_BOOTSTRAP_ENABLED="False",
                SUPERVISOR_BOOTSTRAP_ENABLED="False", OPERATOR_BOOTSTRAP_ENABLED="False",
                SUPERVISOR_API_PERMISSIONS_JSON="[]", OPERATOR_API_PERMISSIONS_JSON="[]",
                LOG_DIR="logs", PRIMARY_DATABASE="mysql", MYSQL_ENABLED="True")


def generate_core_profile(destination, source_root=None):
    source_root = Path(source_root or Path(__file__).resolve().parents[1])
    repository = Path(os.environ.get("ARCH_BE005_REPOSITORY", source_root.parent))
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", C0, "backend"], cwd=repository, text=True).splitlines()
    records = {}
    patches = []
    for path in paths:
        rel = path.removeprefix("backend/")
        parts = Path(rel).parts
        allowed = (parts[0] in {"common", "core", "database", "projection", "alembic"}
                   or (parts[0] == "app" and (len(parts) == 2 or parts[1] in CORE_PACKAGES))
                   or rel == "config/plc_snapshot_policy.yaml"
                   or rel in {"main.py", "run.py", "settings.py", "pyproject.toml", "uv.lock", "alembic.ini", "README.md"})
        if not allowed or Path(rel).name.startswith(".env"):
            continue
        if parts[0] == "alembic" and "versions" in parts and "d4e6f8a0b2c4" not in rel:
            continue
        data = subprocess.check_output(["git", "show", C0 + ":" + path], cwd=repository)
        output = destination / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        records[rel] = dict(source="C0", sha256=sha256(data))
    for rel in CORE_PATCH:
        data = (source_root / rel).read_bytes()
        previous_path = destination / rel
        previous = previous_path.read_bytes() if previous_path.exists() else b""
        patch = "".join(difflib.unified_diff(previous.decode().splitlines(True), data.decode().splitlines(True), fromfile="a/"+rel, tofile="b/"+rel))
        patches.append(patch)
        output = destination / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        records[rel] = dict(source="approved Core patch", sha256=sha256(data), patch_sha256=sha256(patch.encode()))
    # R3 monitor只叠加C0事实manifest合同字段，不复制F业务路由/权限/模型。
    rel = "app/monitor/manifest.py"
    output = destination / rel
    c0_data = output.read_bytes()
    overlay = c0_data.decode().replace('    name="monitor",', '    name="monitor",\n    core_contract="aiis.backend-module/v1",\n    requires=(),\n    model_requires=(),\n    exports=("app.monitor.models:PlcDbBlockRawSnapshot",),\n    error_codes=(),')
    output.write_text(overlay)
    patch = "".join(difflib.unified_diff(c0_data.decode().splitlines(True), overlay.splitlines(True), fromfile="a/"+rel, tofile="b/"+rel))
    patches.append(patch)
    (destination / "core-patch.diff").write_text("".join(patches))
    records[rel] = dict(source="C0 + r3 monitor manifest overlay", c0_sha256=sha256(c0_data),
                        sha256=sha256(output.read_bytes()), patch_sha256=sha256(patch.encode()))
    for test_name in ("test_module_structure.py", "test_celery_retirement.py", "test_core_migration_baseline.py", "test_openapi_router_tags.py"):
        rel = "tests/" + test_name
        data = subprocess.check_output(["git", "show", C0 + ":backend/" + rel], cwd=repository)
        output = destination / rel
        output.parent.mkdir(exist_ok=True)
        output.write_bytes(data)
    (destination / "tests/__init__.py").write_text('"""C0原断言；隔离Core清理验证。"""\n')
    (destination / "core-files.json").write_text(json.dumps(records, indent=2, sort_keys=True))
    (destination / "profile.json").write_text(json.dumps(dict(profile="C2", c0=C0, core_patch=(*CORE_PATCH,"app/monitor/manifest.py"), core_patch_sha256=sha256("".join(patches).encode()), tables=sorted(CORE_TABLES)), indent=2))
    assert not (destination / "common/data_keys.py").exists()
    return destination


def generate_full_profile(destination, source_root=None):
    source_root = Path(source_root or Path(__file__).resolve().parents[1])
    destination = Path(destination)
    def ignore(directory, names):
        return [name for name in names if (name.startswith(".env") and not name.endswith(".example")) or name in {".venv", "node_modules", ".pnpm-store", "__pycache__", ".pytest_cache", "logs", "data", "dist", "build"}]
    shutil.copytree(source_root, destination, ignore=ignore)
    frontend = source_root.parent / "frontend-js"
    if frontend.is_dir() and not (destination.parent / "frontend-js").exists():
        shutil.copytree(frontend, destination.parent / "frontend-js", ignore=ignore)
    (destination / "profile.json").write_text(json.dumps(dict(profile="F", c0=C0, expected_table_count=58), indent=2))
    return destination


def run_python(profile, code, *, source_root=None):
    """复用项目已锁定环境；子进程cwd及PYTHONPATH只指公开fixture，拒绝DB连接。"""
    source_root = Path(source_root or Path(__file__).resolve().parents[1])
    environment = {key: value for key, value in os.environ.items()
                   if key in {"PATH", "HOME", "LANG", "TMPDIR", "SYSTEMROOT"}}
    environment.update(public_environment())
    environment["PYTHONPATH"] = str(profile)
    environment["UV_PROJECT_ENVIRONMENT"] = os.environ.get("UV_PROJECT_ENVIRONMENT", str(source_root / ".venv"))
    environment["ARCH_BE005_REPOSITORY"] = os.environ.get("ARCH_BE005_REPOSITORY", str(source_root.parent))
    environment["UV_CACHE_DIR"] = "/private/tmp/arch-be-005-r2-development/uv-cache"
    environment["PYTHONPYCACHEPREFIX"] = "/private/tmp/arch-be-005-r2-development/pycache"
    guard = """
import sqlalchemy.engine.base, sqlalchemy.ext.asyncio.engine
from unittest.mock import patch

def denied(*args, **kwargs):
    raise AssertionError('A profile prohibits all database connections')
with patch.object(sqlalchemy.engine.base.Engine, 'connect', denied), patch.object(sqlalchemy.engine.base.Engine, 'raw_connection', denied), patch.object(sqlalchemy.ext.asyncio.engine.AsyncEngine, 'connect', denied):
"""
    guarded = guard + "\n".join("    " + line for line in code.splitlines())
    return subprocess.run(["uv", "run", "--frozen", "--no-sync", "python", "-c", guarded], cwd=profile,
                          env=environment, capture_output=True, text=True)


def add_probe(profile, *, summary=False):
    """从aiis_demo七包骨架派生合成模块；内容完全固定并输出每文件指纹。"""
    profile = Path(profile)
    name = "admission_summary" if summary else "admission_probe"
    path = profile / "app" / name
    shutil.copytree(profile / "app/aiis_demo", path)
    for file in path.rglob("*.py"):
        file.unlink()
    files = {"__init__.py": '"""合成接入模块；无运行副作用。"""\n'}
    for package in ("api", "models", "schemas", "crud", "services", "mocks", "seeds"):
        files[package + "/__init__.py"] = '"""合成接入package。"""\n'
    files["error_codes.py"] = f'from enum import StrEnum\nclass ErrorCode(StrEnum):\n    INVALID_VALUE = "{name}.invalid_value"\n'
    files["domain.py"] = 'ACTIVE = "active"\ndef valid_label(value):\n    return bool(value.strip())\n'
    dependency = 'requires=("admission_probe",), model_requires=("admission_probe",),' if summary else 'requires=(), model_requires=(),'
    files["manifest.py"] = f'''from app.module_registry import ModuleManifest
manifest = ModuleManifest(name="{name}", enabled=True, order=100, core_contract="aiis.backend-module/v1",
    routers=("app.{name}.api.routes:router",), models_package="app.{name}.models",
    permissions=("{name}-read", "{name}-manage"), {dependency}
    exports=("app.{name}.models:Item", "app.{name}.schemas:ItemDTO", "app.{name}.domain:ACTIVE"),
    error_codes=("{name}.invalid_value",))
'''
    table = "admission_summary_notes" if summary else "admission_probe_items"
    fk = '\n    probe_id: Mapped[int] = mapped_column(ForeignKey("admission_probe_items.id"))' if summary else ''
    model_import = 'from app.admission_probe.models import Item as ProbeItem\n' if summary else ''
    files["models/item.py"] = f'''from database import Base
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
{model_import}class Item(Base):
    __tablename__ = "{table}"
    id: Mapped[int] = mapped_column(primary_key=True)
    item_label: Mapped[str] = mapped_column(String(80), unique=True){fk}
'''
    files["models/__init__.py"] = 'from .item import Item\n'
    dto_import = 'from app.admission_probe.schemas import ItemDTO as ProbeDTO\nfrom app.admission_probe.domain import ACTIVE\n' if summary else ''
    dto_fk = '\n    probe_id: int' if summary else ''
    files["schemas/item.py"] = f'''from common.schema_base import ApiSchema
{dto_import}class ItemCreate(ApiSchema):
    item_label: str{dto_fk}
class ItemDTO(ItemCreate):
    id: int
'''
    if summary:
        files["schemas/item.py"] = files["schemas/item.py"].replace("class ItemDTO(ItemCreate):\n    id: int", "class ItemDTO(ProbeDTO):\n    probe_id: int\n    probe_state: str = ACTIVE")
    files["schemas/__init__.py"] = 'from .item import ItemDTO, ItemCreate\n'
    files["crud/async_item.py"] = f'''from sqlalchemy import select
from app.{name}.models import Item
async def list_items(db):
    return (await db.execute(select(Item).order_by(Item.id))).scalars().all()
async def create_item(db, data):
    item = Item(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item
'''
    files["services/async_item.py"] = f'''from app.{name}.crud import async_item as crud
from app.{name}.domain import valid_label
from app.{name}.error_codes import ErrorCode
from common.exceptions import BusinessException
async def list_items(db):
    return await crud.list_items(db)
async def create_item(db, data):
    if not valid_label(data.item_label):
        raise BusinessException(ErrorCode.INVALID_VALUE)
    try:
        item = await crud.create_item(db, data)
        await db.commit()
        return item
    except Exception:
        await db.rollback()
        raise
'''
    prefix = name.replace('_', '-')
    files["api/routes.py"] = f'''from fastapi import APIRouter, Depends
from database import get_db
from common.response import SuccessResponse
from core.deps import require_permissions
from app.{name}.schemas import ItemCreate, ItemDTO
from app.{name}.services import async_item as service
router = APIRouter(prefix="/{prefix}")
@router.get("/items", dependencies=[Depends(require_permissions("{name}-read"))])
async def list_items(db=Depends(get_db)):
    return SuccessResponse(data=[ItemDTO.model_validate(x) for x in await service.list_items(db)])
@router.post("/items", dependencies=[Depends(require_permissions("{name}-manage"))])
async def create_item(data: ItemCreate, db=Depends(get_db)):
    return SuccessResponse(data=ItemDTO.model_validate(await service.create_item(db, data)))
'''
    for rel, content in files.items():
        file = path / rel; file.parent.mkdir(parents=True, exist_ok=True); file.write_text(content)
    revision = "e2a4c6e8b0d2" if summary else "e1a3c5e7b9d1"
    previous = "e1a3c5e7b9d1" if summary else "d4e6f8a0b2c4"
    extra = ', sa.Column("probe_id", sa.Integer(), sa.ForeignKey("admission_probe_items.id"), nullable=False)' if summary else ''
    migration = f'''"""合成消费者显式增量；仅fixture，不发布或在线执行。"""
from alembic import op
import sqlalchemy as sa
revision = "{revision}"
down_revision = "{previous}"
def upgrade():
    op.create_table("{table}", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("item_label", sa.String(80), nullable=False, unique=True){extra})
def downgrade():
    op.drop_table("{table}")
'''
    migration_path = profile / "alembic/versions" / (revision + "_" + name + ".py")
    migration_path.write_text(migration)
    fingerprints = {str(file.relative_to(profile)): sha256(file.read_bytes()) for file in sorted(path.rglob("*.py"))}
    fingerprints[str(migration_path.relative_to(profile))] = sha256(migration.encode())
    (profile / (name + "-files.json")).write_text(json.dumps(fingerprints, indent=2, sort_keys=True))
    metadata = json.loads((profile / "profile.json").read_text())
    metadata["profile"] = "E"
    metadata.setdefault("consumers", []).append(name)
    metadata["expected_table_count"] = len(CORE_TABLES) + len(metadata["consumers"])
    (profile / "profile.json").write_text(json.dumps(metadata, indent=2, sort_keys=True))
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("C2", "E", "F"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if not args.profile or not args.output:
        parser.print_help(); return
    if args.profile == "F":
        generate_full_profile(args.output)
    else:
        generate_core_profile(args.output)
        if args.profile == "E":
            add_probe(args.output)
            if args.summary:
                add_probe(args.output, summary=True)


if __name__ == "__main__":
    main()
