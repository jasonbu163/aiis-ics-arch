"""
文件路径: /backend/app/monitor/manifest.py
功能描述: Monitor 模块注册元数据
主要功能:
    - 声明监控数据 API 路由入口
    - 声明监控数据模型包入口
    - 支持后端模块 registry 统一加载
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    name="monitor",
    enabled=True,
    order=35,
    routers=("app.monitor.api.routes:router",),
    models_package="app.monitor.models",
    permissions=("monitor",),
)
