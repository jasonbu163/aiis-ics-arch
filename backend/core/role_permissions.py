"""
文件路径: /backend/core/role_permissions.py
功能描述: 纯角色授权解析、原始等级校验与模块权限过滤
主要功能:
    - 严格检查两项 JSON 数组和退役配置
    - 汇总普通模块与显式安全边界的权限 owner
    - 返回应用专属的只读授权策略，不依赖 FastAPI 或数据库
"""
import json
from types import MappingProxyType


SUPERVISOR_VARIABLE = "SUPERVISOR_API_PERMISSIONS_JSON"
OPERATOR_VARIABLE = "OPERATOR_API_PERMISSIONS_JSON"


def parse_permission_array(raw: str, variable: str) -> frozenset[str]:
    """解析稳定 key，精确匹配且不把配置全文带入异常。"""
    try:
        values = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        raise ValueError(f"{variable}: invalid JSON; expected an array of strings") from None
    if not isinstance(values, list):
        raise ValueError(f"{variable}: expected an array of strings")
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{variable}[{index}]: expected a non-blank string")
    return frozenset(values)


def build_role_api_permissions(
    supervisor_raw, operator_raw, manifests, *, legacy_present=False, warn,
):
    """先校验原始子集，再按所有 owner 状态过滤；诊断由组合根注入。"""
    if legacy_present:
        raise ValueError(
            "ROLE_API_PERMISSIONS_JSON is retired; remove it and migrate to "
            f"{SUPERVISOR_VARIABLE} and {OPERATOR_VARIABLE}"
        )
    supervisor = parse_permission_array(supervisor_raw, SUPERVISOR_VARIABLE)
    operator = parse_permission_array(operator_raw, OPERATOR_VARIABLE)
    missing = operator - supervisor
    if missing:
        raise ValueError(
            f"{OPERATOR_VARIABLE}: permissions {sorted(missing)!r} "
            f"are absent from {SUPERVISOR_VARIABLE}"
        )

    owners = {
        "system": [("user", True)],
        "control-agent-read": [("control_agent", True)],
        "control-agent": [("control_agent", True)],
    }
    for manifest in manifests:
        for permission in manifest.permissions:
            owners.setdefault(permission, []).append((manifest.name, manifest.enabled))

    effective = {}
    for role, variable, configured in (
        ("supervisor", SUPERVISOR_VARIABLE, supervisor),
        ("operator", OPERATOR_VARIABLE, operator),
    ):
        granted = set()
        for permission in sorted(configured):
            declarations = owners.get(permission, [])
            if any(enabled for _, enabled in declarations):
                granted.add(permission)
            else:
                warn(
                    variable=variable,
                    permission=permission,
                    reason="disabled_module" if declarations else "unknown_permission",
                    modules=sorted({name for name, _ in declarations}),
                )
        effective[role] = frozenset(granted)
    return MappingProxyType(effective)
