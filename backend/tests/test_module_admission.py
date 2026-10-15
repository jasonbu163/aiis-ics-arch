"""C0→C2冻结、消费者E接入正负矩阵及r3 Model分类；全程禁止连接DB。"""
import hashlib
import json
from pathlib import Path
import shutil

import pytest
from tests.module_admission_fixtures import generate_core_profile, add_probe, run_python, CORE_TABLES

pytestmark = pytest.mark.no_db
COMPOSE = '''from app.module_preflight import check_source
check_source(".")
from app.module_registry import import_model_packages
import_model_packages()
from core.registrar import create_app
app = create_app(testing=True)
from sqlalchemy.orm import configure_mappers
configure_mappers()
from app.user.models.token_blacklist import TokenBlacklist
from database import Base
print("TABLES=" + __import__('json').dumps(sorted(Base.metadata.tables)))
'''


@pytest.fixture(scope="module")
def frozen_core(tmp_path_factory):
    core = generate_core_profile(tmp_path_factory.mktemp("admission") / "C2")
    result = run_python(core, COMPOSE + f'assert set(Base.metadata.tables) == {CORE_TABLES!r}')
    assert result.returncode == 0, result.stdout + result.stderr
    result = run_python(core, 'import pytest\nraise SystemExit(pytest.main(["--noconftest", "-q", "-m", "no_db", "tests"]))')
    assert result.returncode == 0, result.stdout + result.stderr
    return core


def consumer(tmp_path, frozen_core, summary=True):
    profile = tmp_path / "E"
    shutil.copytree(frozen_core, profile)
    add_probe(profile)
    if summary:
        add_probe(profile, summary=True)
    return profile


def rewrite(profile, name, old, new):
    file = profile / name
    text = file.read_text()
    assert old in text, (name, old)
    file.write_text(text.replace(old, new))


def assert_rejected(profile, stage):
    result = run_python(profile, COMPOSE)
    assert result.returncode != 0, result.stdout
    assert stage in result.stderr, result.stderr
    assert '"location"' in result.stderr or '"stage"' in result.stderr


@pytest.mark.parametrize("summary", [False, True])
def test_c2_frozen_core_accepts_independent_and_combined_modules(tmp_path, frozen_core, summary):
    profile = consumer(tmp_path, frozen_core, summary)
    before = json.loads((profile / "core-files.json").read_text())
    result = run_python(profile, COMPOSE + f'assert len(Base.metadata.tables) == {16 if summary else 15}')
    assert result.returncode == 0, result.stdout + result.stderr
    for name, record in before.items():
        assert hashlib.sha256((profile / name).read_bytes()).hexdigest() == record["sha256"], name
    assert not (profile / "common/data_keys.py").exists()
    assert set(json.loads((profile / "profile.json").read_text())["tables"]) == CORE_TABLES


@pytest.mark.parametrize("file,old,new,stage", [
    ("app/admission_summary/manifest.py", 'requires=("admission_probe",)', 'requires=("missing",)', "dependency"),
    ("app/admission_probe/manifest.py", 'enabled=True', 'enabled=False', "dependency"),
    ("app/admission_summary/manifest.py", 'requires=("admission_probe",)', 'requires=("admission_summary",)', "dependency-name"),
    ("app/admission_summary/manifest.py", 'requires=("admission_probe",)', 'requires=("admission_probe", "admission_probe")', "manifest-duplicate"),
    ("app/admission_probe/manifest.py", 'requires=()', 'requires=("admission_summary",)', "runtime-cycle"),
    ("app/admission_probe/manifest.py", 'aiis.backend-module/v1', 'aiis.backend-module/v2', "contract"),
    ("app/admission_summary/manifest.py", 'requires=("admission_probe",)', 'requires=()', "undeclared-dependency"),
    ("app/admission_summary/manifest.py", 'model_requires=("admission_probe",)', 'model_requires=()', "undeclared-dependency"),
    ("app/admission_probe/manifest.py", '"app.admission_probe.models:Item", ', '', "private-import"),
    ("app/admission_summary/models/item.py", 'from app.admission_probe.models import', 'from app.admission_probe.models.item import', "private-import"),
    ("app/admission_probe/models/item.py", 'admission_probe_items', 'users', '"stage": "table"'),
    ("app/admission_summary/manifest.py", '"admission_summary-read"', '"admission_probe-read"', '"stage": "permissions"'),
    ("app/admission_summary/error_codes.py", 'admission_summary.invalid_value', 'admission_probe.invalid_value', "error-namespace"),
    ("app/admission_probe/manifest.py", '"app.admission_probe.domain:ACTIVE"', '"app.admission_probe.domain:MISSING"', '"stage": "export"'),
    ("app/admission_probe/api/routes.py", 'from database import get_db', 'from database import sync_engine', "private-core-import"),
    ("app/admission_probe/domain.py", 'ACTIVE = "active"', 'from settings import settings\nACTIVE = settings.MYSQL_PASSWORD', "private-setting"),
    ("app/admission_probe/domain.py", 'ACTIVE = "active"', 'from importlib import import_module as load\nACTIVE = load("app.user")', "unsupported-dynamic-import"),
])
def test_each_invalid_source_change_is_located(tmp_path, frozen_core, file, old, new, stage):
    profile = consumer(tmp_path, frozen_core)
    rewrite(profile, file, old, new)
    assert_rejected(profile, stage)


def test_no_manifest_dependency_is_blocked(tmp_path, frozen_core):
    profile = consumer(tmp_path, frozen_core)
    (profile / "app/admission_probe/manifest.py").unlink()
    assert_rejected(profile, "dependency")


@pytest.mark.parametrize("path", ["/{id}", "/openapi.json"])
def test_final_route_conflicts_fail_before_ready(tmp_path, frozen_core, path):
    profile = consumer(tmp_path, frozen_core, False)
    file = profile / "app/admission_probe/api/routes.py"
    with file.open("a") as stream:
        if path == "/{id}":
            stream.write('\n@router.get("/{id}")\ndef first(id): return id\n@router.get("/{item_id}")\ndef second(item_id): return item_id\n')
        else:
            # prefix使普通模块碰显式user/API路径。
            stream.write('\n@router.get("/current")\ndef current(): return 1\n@router.get("/current")\ndef duplicate(): return 2\n')
    assert_rejected(profile, "http-route")


@pytest.mark.parametrize("location", ["models/consumer.py", "crud/consumer.py", "services/consumer.py"])
def test_public_model_classification_is_independent_of_consumer_file(tmp_path, frozen_core, location):
    profile = consumer(tmp_path, frozen_core, False)
    package = profile / "app/model_consumer"
    package.mkdir(); (package / "__init__.py").write_text('')
    (package / "models").mkdir(); (package / "models/__init__.py").write_text('')
    file = package / location; file.parent.mkdir(exist_ok=True)
    file.write_text('from app.admission_probe.models import Item\n')
    (package / "manifest.py").write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="model_consumer", models_package="app.model_consumer.models", model_requires=("admission_probe",))\n')
    rewrite(profile, "app/admission_probe/manifest.py", "enabled=True", "enabled=False")
    result = run_python(profile, COMPOSE)
    assert result.returncode == 0, result.stderr
    rewrite(profile, "app/model_consumer/manifest.py", 'model_requires=("admission_probe",)', 'model_requires=()')
    assert_rejected(profile, "undeclared-dependency")


def test_disabled_consumer_api_keeps_metadata_and_reexport_same_class(tmp_path, frozen_core):
    profile = consumer(tmp_path, frozen_core)
    rewrite(profile, "app/admission_summary/manifest.py", "enabled=True", "enabled=False")
    result = run_python(profile, COMPOSE + '\nassert len(Base.metadata.tables)==16\nfrom app.admission_probe.models import Item\nfrom app.admission_probe.models.item import Item as Original\nassert Item is Original\nassert not any("admission-summary" in route.path for route in app.routes)')
    assert result.returncode == 0, result.stderr


def test_system_public_model_dependency_has_no_hidden_core_exception(tmp_path, frozen_core):
    profile = consumer(tmp_path, frozen_core, False)
    rewrite(profile, "app/system/manifest.py", 'model_requires=("monitor",)', 'model_requires=()')
    assert_rejected(profile, "undeclared-dependency")


def test_disabled_service_export_does_not_eagerly_import_missing_runtime(tmp_path, frozen_core):
    profile = consumer(tmp_path, frozen_core, False)
    package = profile / 'app/inactive_consumer'
    package.mkdir(); (package/'__init__.py').write_text('')
    (package/'models').mkdir(); (package/'models/__init__.py').write_text('')
    (package/'services').mkdir(); (package/'services/__init__.py').write_text('')
    (package/'services/async_service.py').write_text('from app.not_installed.services import execute\ndef public_service(): return execute()\n')
    (package/'manifest.py').write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="inactive_consumer",enabled=False,models_package="app.inactive_consumer.models",requires=("not_installed",),exports=("app.inactive_consumer.services.async_service:public_service",))\n')
    result = run_python(profile, COMPOSE + '\nimport sys\nassert "app.inactive_consumer.services.async_service" not in sys.modules')
    assert result.returncode == 0, result.stderr
    rewrite(profile,'app/inactive_consumer/manifest.py','enabled=False','enabled=True')
    assert_rejected(profile,'dependency')


@pytest.mark.parametrize("provider_present", [False, True])
@pytest.mark.parametrize("entry", ["services/runtime.py", "services/__init__.py", "api/__init__.py"])
def test_disabled_consumer_error_from_inactive_runtime_provider_is_not_imported(tmp_path, frozen_core, provider_present, entry):
    profile = consumer(tmp_path, frozen_core, False)
    if provider_present:
        provider = profile / "app/runtime_provider"
        provider.mkdir(); (provider / "__init__.py").write_text("")
        (provider / "models").mkdir(); (provider / "models/__init__.py").write_text("")
        (provider / "error_codes.py").write_text('from enum import StrEnum\nfrom not_installed_runtime import connect\nclass Failure(StrEnum):\n    INVALID="runtime_provider.invalid"\n')
        (provider / "manifest.py").write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="runtime_provider",enabled=False,models_package="app.runtime_provider.models",exports=("app.runtime_provider.error_codes:Failure",),error_codes=("runtime_provider.invalid",))\n')
    package = profile / "app/inactive_error"
    package.mkdir(); (package / "__init__.py").write_text("")
    for name in ("api", "models", "schemas", "crud", "services", "mocks", "seeds"):
        (package / name).mkdir(); (package / name / "__init__.py").write_text("")
    module = "app.inactive_error." + entry.removesuffix(".py").replace("/", ".").removesuffix(".__init__")
    (package / "manifest.py").write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="inactive_error",enabled=False,requires=("runtime_provider",),models_package="app.inactive_error.models",exports=("' + module + ':execute",))\n')
    service = package / entry
    service.write_text('from app.runtime_provider.error_codes import Failure\nfrom common.exceptions import BusinessException\ndef execute():\n    raise BusinessException(Failure.INVALID)\n')
    result = run_python(profile, COMPOSE + f'''
import sys
assert {module!r} not in sys.modules
assert "app.runtime_provider.error_codes" not in sys.modules
assert len(Base.metadata.tables)==15
''')
    assert result.returncode == 0, result.stdout + result.stderr
    # metadata依赖始终有效，不随runtime inactive被忽略。
    rewrite(profile, "app/inactive_error/manifest.py", 'requires=("runtime_provider",)', 'requires=("runtime_provider",),model_requires=("not_installed",)')
    assert_rejected(profile, "dependency")
    rewrite(profile, "app/inactive_error/manifest.py", ',model_requires=("not_installed",)', "")
    # 能定位的本地错误仍须静态声明/namespace合法；disabled不是错误合同豁免。
    service.write_text('from enum import StrEnum\nfrom common.exceptions import BusinessException\nclass Failure(StrEnum):\n    INVALID="user_not_found"\ndef execute():\n    raise BusinessException(Failure.INVALID)\n')
    assert_rejected(profile, "error-namespace")
    service.write_text('from app.runtime_provider.error_codes import Failure\nfrom common.exceptions import BusinessException\ndef execute():\n    raise BusinessException(Failure.INVALID)\n')
    rewrite(profile, "app/inactive_error/manifest.py", "enabled=False", "enabled=True")
    assert_rejected(profile, "dependency")


@pytest.mark.parametrize("entry", ["__init__.py", "models/runtime.py"])
def test_disabled_entry_and_metadata_error_sources_are_still_strict(tmp_path, frozen_core, entry):
    profile = consumer(tmp_path, frozen_core, False)
    package = profile / "app/inactive_error"
    package.mkdir(); (package / "__init__.py").write_text("")
    (package / "models").mkdir(); (package / "models/__init__.py").write_text("")
    (package / "manifest.py").write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="inactive_error",enabled=False,requires=("not_installed",),models_package="app.inactive_error.models")\n')
    (package / entry).write_text('from app.not_installed.error_codes import Failure\nfrom common.exceptions import BusinessException\ndef execute():\n    raise BusinessException(Failure.INVALID)\n')
    assert_rejected(profile, "error-source")


@pytest.mark.parametrize("value,stage", [
    ("user_not_found", "error-namespace"),
    ("other.invalid_value", "error-namespace"),
    ("admission_probe.invalid_value", "error-declaration"),
])
def test_used_error_str_enum_cannot_hide_behind_class_name_or_empty_claim(tmp_path, frozen_core, value, stage):
    # QA F-001原输入：Failure不是Error类名，manifest空声明，真实Service仍使用该StrEnum。
    profile = consumer(tmp_path, frozen_core, False)
    rewrite(profile, "app/admission_probe/error_codes.py", "class ErrorCode", "class Failure")
    rewrite(profile, "app/admission_probe/error_codes.py", "admission_probe.invalid_value", value)
    rewrite(profile, "app/admission_probe/services/async_item.py", "import ErrorCode", "import Failure")
    rewrite(profile, "app/admission_probe/services/async_item.py", "ErrorCode.INVALID_VALUE", "Failure.INVALID_VALUE")
    rewrite(profile, "app/admission_probe/manifest.py", 'error_codes=("admission_probe.invalid_value",)', "error_codes=()")
    assert_rejected(profile, stage)


@pytest.mark.parametrize("style", ["alias-keyword", "qualified-module", "thin-reexport", "typed-factory", "generic-factory", "untyped-factory", "local-member", "subclass-base", "package-module", "relative-module", "explicit-module", "relative-explicit-module"])
def test_error_enum_aliases_and_domain_str_enum_use_actual_semantics(tmp_path, frozen_core, style):
    profile = consumer(tmp_path, frozen_core, False)
    (profile / "app/admission_probe/error_codes.py").write_text('from enum import StrEnum as TextEnum\nclass Failure(TextEnum):\n    INVALID_VALUE="admission_probe.invalid_value"\nclass ErrorStatus(TextEnum):\n    ACTIVE="active"\n')
    service = profile / "app/admission_probe/services/async_item.py"
    content = service.read_text().replace("from common.exceptions import BusinessException", "from common.exceptions import BusinessException as Fault").replace("raise BusinessException(ErrorCode.INVALID_VALUE)", "raise Fault(error_code=Failure.INVALID_VALUE)")
    if style == "alias-keyword":
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", "from app.admission_probe.error_codes import Failure as Outcome").replace("Failure.INVALID_VALUE", "Outcome.INVALID_VALUE")
    elif style == "qualified-module":
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", "import app.admission_probe.error_codes").replace("Failure.INVALID_VALUE", "app.admission_probe.error_codes.Failure.INVALID_VALUE")
    elif style in {"package-module", "relative-module", "explicit-module", "relative-explicit-module"}:
        if "explicit" in style:
            # __init__显式绑定优先于同名error_codes子模块；转发仍是同一原StrEnum。
            (profile / "app/admission_probe/forwarded.py").write_text("from .error_codes import Failure\n")
            (profile / "app/admission_probe/__init__.py").write_text("from . import forwarded as error_codes\n")
        imported = "from .. import error_codes as errors" if style.startswith("relative") else "from app.admission_probe import error_codes as errors"
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", imported).replace("Failure.INVALID_VALUE", "errors.Failure.INVALID_VALUE")
    elif style == "subclass-base":
        errors = profile / "app/admission_probe/error_codes.py"
        errors.write_text(errors.read_text().replace("class Failure(TextEnum):", "class Codes(TextEnum):\n    pass\nclass Failure(Codes):"))
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", "from app.admission_probe.error_codes import Failure")
    elif style in {"typed-factory", "generic-factory", "untyped-factory"}:
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", "from app.admission_probe.error_codes import Failure")
        annotation = {"typed-factory": ": Failure", "generic-factory": ": StrEnum", "untyped-factory": ""}[style]
        content += f'\nfrom enum import StrEnum\ndef fail(code{annotation}):\n    return Fault(error_code=code)\n'
        content = content.replace("raise Fault(error_code=Failure.INVALID_VALUE)", "raise fail(Failure.INVALID_VALUE)")
    elif style == "local-member":
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", "from app.admission_probe.error_codes import Failure")
        content = content.replace("raise Fault(error_code=Failure.INVALID_VALUE)", "code = Failure.INVALID_VALUE\n        raise Fault(error_code=code)")
    else:
        (profile / "app/admission_probe/services/__init__.py").write_text("from app.admission_probe.error_codes import Failure as PublicFailure\n")
        content = content.replace("from app.admission_probe.error_codes import ErrorCode", "from app.admission_probe.services import PublicFailure as Failure")
    service.write_text(content)
    result = run_python(profile, COMPOSE + '''
import asyncio
from httpx import ASGITransport, AsyncClient
from database import get_db
from core.deps import get_current_user
from types import SimpleNamespace
app.dependency_overrides[get_db]=lambda:None
app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role="admin",username="fixture")
async def request():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://fixture") as client:
        response=await client.post("/api/v1/admission-probe/items",json={"itemLabel":" "})
        assert response.status_code==200
        assert response.json()["errorCode"]=="admission_probe.invalid_value"
asyncio.run(request())
''')
    assert result.returncode == 0, result.stdout + result.stderr
    # 同一别名路径改成Core冲突且撤声明仍必须拒绝，不可仅正例支持别名。
    rewrite(profile, "app/admission_probe/error_codes.py", "admission_probe.invalid_value", "user_not_found")
    rewrite(profile, "app/admission_probe/manifest.py", 'error_codes=("admission_probe.invalid_value",)', "error_codes=()")
    assert_rejected(profile, "error-namespace")


@pytest.mark.parametrize("annotation", ["StrEnum", "str"])
def test_generic_factory_actual_arguments_still_check_error_owner(tmp_path, frozen_core, annotation):
    profile = consumer(tmp_path, frozen_core, False)
    service = profile / "app/admission_probe/services/async_item.py"
    content = service.read_text().replace("raise BusinessException(ErrorCode.INVALID_VALUE)", "raise fail(ErrorCode.INVALID_VALUE)")
    content += f'\nfrom enum import StrEnum\ndef fail(code: {annotation}):\n    return BusinessException(code)\n'
    service.write_text(content)
    rewrite(profile, "app/admission_probe/error_codes.py", "admission_probe.invalid_value", "user_not_found")
    rewrite(profile, "app/admission_probe/manifest.py", 'error_codes=("admission_probe.invalid_value",)', "error_codes=()")
    assert_rejected(profile, "error-namespace")


def test_factory_with_unresolved_runtime_error_argument_is_located(tmp_path, frozen_core):
    profile = consumer(tmp_path, frozen_core, False)
    service = profile / "app/admission_probe/services/async_item.py"
    content = service.read_text().replace("raise BusinessException(ErrorCode.INVALID_VALUE)", "raise fail(data.item_label)")
    content += '\ndef fail(code):\n    return BusinessException(code)\n'
    service.write_text(content)
    assert_rejected(profile, "error-source")


@pytest.mark.parametrize("kind", ["model", "dto", "function"])
def test_explicit_package_binding_beats_same_named_submodule_and_keeps_category(tmp_path, frozen_core, kind):
    profile = consumer(tmp_path, frozen_core, False)
    provider = profile / "app/admission_probe"
    declaration = {"model": "from .models import Item as Public", "dto": "from .schemas import ItemDTO as Public", "function": "from .domain import valid_label as Public"}[kind]
    (provider / "__init__.py").write_text(declaration + "\n")
    (provider / "Public.py").write_text('SHADOW="a child module must not replace an explicit binding"\n')
    rewrite(profile, "app/admission_probe/manifest.py", 'exports=("app.admission_probe.models:Item",', 'exports=("app.admission_probe:Public", "app.admission_probe.models:Item",')
    package = profile / "app/admission_binding"
    package.mkdir(); (package / "__init__.py").write_text("")
    for name in ("api", "models", "schemas", "crud", "services", "mocks", "seeds"):
        (package / name).mkdir(); (package / name / "__init__.py").write_text("")
    dependency = 'model_requires=("admission_probe",)' if kind == "model" else 'requires=("admission_probe",)'
    (package / "manifest.py").write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="admission_binding",models_package="app.admission_binding.models",' + dependency + ')\n')
    (package / "services/reference.py").write_text("from app.admission_probe import Public as Bound\n")
    if kind == "model":
        rewrite(profile, "app/admission_probe/manifest.py", "enabled=True", "enabled=False")
    result = run_python(profile, COMPOSE + f'''
from pathlib import Path
from app.module_preflight import _is_model_symbol
from app.module_registry import get_module_manifests
from app.admission_probe import Public
from app.admission_binding.services.reference import Bound
assert Bound is Public
provider=next(m for m in get_module_manifests() if m.name=="admission_probe")
assert _is_model_symbol(Path('.').resolve(), "app.admission_probe:Public", provider) is {kind == "model"!r}
assert Public.__module__ == {dict(model="app.admission_probe.models.item", dto="app.admission_probe.schemas.item", function="app.admission_probe.domain")[kind]!r}
''')
    assert result.returncode == 0, result.stdout + result.stderr
    rewrite(profile, "app/admission_binding/manifest.py", dependency, "")
    assert_rejected(profile, "undeclared-dependency")


@pytest.mark.parametrize("target", ["app.admission_probe.models.item.Item", "admission_probe.models.item.Item"])
@pytest.mark.parametrize("reverse_scan", [False, True])
def test_qualified_relationship_preserves_same_named_model_owner(tmp_path, frozen_core, target, reverse_scan):
    # QA F-002：两个owner均有Item，引用必须跟随原定义，不能要求无引用的summary依赖。
    profile = consumer(tmp_path, frozen_core)
    package = profile / "app/admission_ref"
    package.mkdir(); (package / "__init__.py").write_text("")
    for name in ("api", "models", "schemas", "crud", "services", "mocks", "seeds"):
        (package / name).mkdir(); (package / name / "__init__.py").write_text("")
    (package / "manifest.py").write_text('from app.module_registry import ModuleManifest\nmanifest=ModuleManifest(name="admission_ref",core_contract="aiis.backend-module/v1",models_package="app.admission_ref.models",model_requires=("admission_probe",),exports=("app.admission_ref.models:Ref",))\n')
    (package / "models/__init__.py").write_text("from .ref import Ref\n")
    (package / "models/ref.py").write_text(f'''from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
class Ref(Base):
    __tablename__="admission_refs"
    id: Mapped[int]=mapped_column(primary_key=True)
    probe_id: Mapped[int]=mapped_column(ForeignKey("admission_probe_items.id"))
    probe: Mapped["{target}"]=relationship("{target}")
''')
    provider = "admission_probe"
    if reverse_scan:
        # provider从summary之前移至之后；业务源码重命名，冻结Core不变。
        provider = "admission_zprobe"
        for module in (profile / "app").glob("admission_*"):
            for file in module.rglob("*.py"):
                file.write_text(file.read_text().replace("admission_probe", provider))
        (profile / "app/admission_probe").rename(profile / "app" / provider)
        target = target.replace("admission_probe", provider)
    code = COMPOSE + '''
from app.admission_ref.models import Ref
from app.admission_probe.models import Item as Probe
from app.admission_probe.models.item import Item as Original
from sqlalchemy import select
assert Ref.probe.property.mapper.class_ is Probe is Original
assert "JOIN admission_probe_items" in str(select(Ref).join(Ref.probe))
assert len(Base.metadata.tables)==17
'''
    result = run_python(profile, code.replace("admission_probe", provider))
    assert result.returncode == 0, result.stdout + result.stderr
    rewrite(profile, "app/admission_ref/manifest.py", f'model_requires=("{provider}",)', "model_requires=()")
    assert_rejected(profile, "undeclared-model-dependency")
    rewrite(profile, "app/admission_ref/manifest.py", "model_requires=()", f'model_requires=("{provider}",)')
    rewrite(profile, "app/admission_ref/models/ref.py", target, "Item")
    assert_rejected(profile, "model-target")


def test_new_module_cannot_import_private_user_crud(tmp_path, frozen_core):
    profile = consumer(tmp_path, frozen_core, False)
    rewrite(profile,'app/admission_probe/domain.py','ACTIVE = "active"','from app.user.crud.async_user import UserCRUD\nACTIVE = "active"')
    assert_rejected(profile,'private-core-import')


def test_e_public_asgi_camelcase_module_error_grants_and_transaction(tmp_path, frozen_core):
    profile=consumer(tmp_path,frozen_core,False)
    code=COMPOSE+'''
import asyncio, json
from types import SimpleNamespace
from httpx import ASGITransport, AsyncClient
from core.deps import get_current_user
from core.role_permissions import build_role_api_permissions
from app.module_registry import get_module_manifests
from database import get_db
from app.admission_probe.services import async_item as service
from app.admission_probe.schemas import ItemCreate
class MemorySession:
    def __init__(self): self.rows=[]; self.pending=None; self.commits=0; self.rollbacks=0; self.fail=False
    def add(self,item): item.id=len(self.rows)+1; self.pending=item
    async def flush(self):
        if self.fail: raise ValueError('synthetic_flush_failure')
    async def refresh(self,item): pass
    async def commit(self): self.rows.append(self.pending); self.commits+=1
    async def rollback(self): self.pending=None; self.rollbacks+=1
    async def execute(self,statement): return SimpleNamespace(scalars=lambda:SimpleNamespace(all=lambda:list(self.rows)))
db=MemorySession()
app.dependency_overrides[get_db]=lambda:db
app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role='admin',username='fixture')
async def scenario():
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
        saved=await client.post('/api/v1/admission-probe/items',json={'itemLabel':'fixture'})
        assert saved.status_code==200 and saved.json()['data']=={'id':1,'itemLabel':'fixture'}
        listed=await client.get('/api/v1/admission-probe/items')
        assert listed.json()['data']==[{'id':1,'itemLabel':'fixture'}]
        failed=await client.post('/api/v1/admission-probe/items',json={'itemLabel':' '})
        assert failed.status_code==200 and failed.json()['code']==400 and failed.json()['data'] is None
        assert failed.json()['errorCode']=='admission_probe.invalid_value'
        assert db.commits==1
        app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role='supervisor',username='fixture')
        for grants in ([],['unknown']):
            app.state.role_api_permissions=build_role_api_permissions(json.dumps(grants),'[]',get_module_manifests(),warn=lambda **kw:None)
            assert (await client.get('/api/v1/admission-probe/items')).status_code==403
        app.state.role_api_permissions=build_role_api_permissions('["admission_probe-read"]','[]',get_module_manifests(),warn=lambda **kw:None)
        assert (await client.get('/api/v1/admission-probe/items')).status_code==200
        assert (await client.post('/api/v1/admission-probe/items',json={'itemLabel':'denied'})).status_code==403
    db.fail=True
    try: await service.create_item(db,ItemCreate(item_label='rollback'))
    except ValueError: pass
    else: raise AssertionError('failure expected')
    assert db.rollbacks==1 and db.commits==1
asyncio.run(scenario())
'''
    result=run_python(profile,code)
    assert result.returncode==0,result.stdout+result.stderr


def test_e_valid_bidirectional_metadata_relationship_cycle(tmp_path,frozen_core):
    profile=consumer(tmp_path,frozen_core)
    rewrite(profile,'app/admission_probe/models/item.py','class Item(Base):','class ProbeItem(Base):')
    rewrite(profile,'app/admission_probe/models/item.py','from sqlalchemy.orm import Mapped, mapped_column','from sqlalchemy.orm import Mapped, mapped_column, relationship')
    with (profile/'app/admission_probe/models/item.py').open('a') as stream:
        stream.write('    notes: Mapped[list["SummaryItem"]] = relationship("SummaryItem", back_populates="probe")\n')
    rewrite(profile,'app/admission_probe/models/__init__.py','from .item import Item','from .item import ProbeItem as Item')
    rewrite(profile,'app/admission_probe/manifest.py','model_requires=()','model_requires=("admission_summary",)')
    rewrite(profile,'app/admission_summary/models/item.py','class Item(Base):','class SummaryItem(Base):')
    rewrite(profile,'app/admission_summary/models/item.py','from sqlalchemy.orm import Mapped, mapped_column','from sqlalchemy.orm import Mapped, mapped_column, relationship')
    with (profile/'app/admission_summary/models/item.py').open('a') as stream:
        stream.write('    probe: Mapped["ProbeItem"] = relationship("ProbeItem", back_populates="notes")\n')
    rewrite(profile,'app/admission_summary/models/__init__.py','from .item import Item','from .item import SummaryItem as Item')
    result=run_python(profile,COMPOSE+'\nassert len(Base.metadata.tables)==16')
    assert result.returncode==0,result.stdout+result.stderr


def test_bare_preflight_help_does_not_import_configuration(tmp_path,frozen_core):
    result=run_python(frozen_core,'from app.module_preflight import main\nimport sys\nassert main([])==0\nassert "settings" not in sys.modules\nassert "database" not in sys.modules')
    assert result.returncode==0,result.stdout+result.stderr
    assert '--check-only' in result.stdout


def test_explicit_user_route_collision_is_blocked(tmp_path,frozen_core):
    profile=consumer(tmp_path,frozen_core,False)
    rewrite(profile,'app/admission_probe/api/routes.py','prefix="/admission-probe"','prefix=""')
    with (profile/'app/admission_probe/api/routes.py').open('a') as stream:
        stream.write('\n@router.post("/auth/login")\ndef collide(): return None\n')
    assert_rejected(profile,'http-route')


def test_extend_existing_table_cannot_hide_core_collision(tmp_path,frozen_core):
    profile=consumer(tmp_path,frozen_core,False)
    with (profile/'app/admission_probe/models/item.py').open('a') as stream:
        stream.write('\nfrom sqlalchemy import Table\nshadow = Table("users", Base.metadata, extend_existing=True)\n')
    assert_rejected(profile,'"stage": "table"')
