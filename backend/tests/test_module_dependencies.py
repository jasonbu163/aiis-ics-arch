"""纯声明依赖负矩阵：runtime DAG与disabled metadata闭包分别验证。"""
from dataclasses import replace

import pytest
from app.module_preflight import ModulePreflightError, validate_manifests
from app.module_registry import ModuleManifest

pytestmark = pytest.mark.no_db


def module(name, **kwargs):
    return ModuleManifest(name=name, core_contract="aiis.backend-module/v1", models_package=f"app.{name}.models", **kwargs)


@pytest.mark.parametrize("change,stage", [
    ({"requires": ("missing",)}, "dependency"),
    ({"requires": ("consumer",)}, "dependency-name"),
    ({"requires": ("provider", "provider")}, "manifest-duplicate"),
    ({"requires": ("user",)}, "dependency-name"),
    ({"model_requires": ("missing",)}, "dependency"),
    ({"core_contract": "aiis.backend-module/v2"}, "contract"),
])
def test_invalid_dependency_declarations(change, stage):
    consumer = replace(module("consumer"), **change)
    with pytest.raises(ModulePreflightError, match=stage):
        validate_manifests([module("provider"), consumer])


def test_enabled_consumer_cannot_depend_on_disabled_provider():
    with pytest.raises(ModulePreflightError, match="consumer -> provider"):
        validate_manifests([module("provider", enabled=False), module("consumer", requires=("provider",))])


def test_runtime_cycle_reports_complete_chain():
    with pytest.raises(ModulePreflightError, match="alpha -> beta -> alpha"):
        validate_manifests([module("alpha", requires=("beta",)), module("beta", requires=("alpha",))])


def test_disabled_runtime_inactive_but_models_still_require_provider():
    validate_manifests([module("provider", enabled=False), module("consumer", enabled=False,
                       requires=("not_installed",), model_requires=("provider",))])
    with pytest.raises(ModulePreflightError, match="dependency"):
        validate_manifests([module("consumer", enabled=False, model_requires=("provider",))])


def test_metadata_cycles_are_legal_and_order_is_unchanged():
    manifests = [module("alpha", order=90, model_requires=("beta",)), module("beta", order=10, model_requires=("alpha",))]
    validate_manifests(manifests)
    assert [x.name for x in manifests] == ["alpha", "beta"]
