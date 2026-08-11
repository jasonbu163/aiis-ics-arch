"""
文件路径: /backend/app/aiis_demo/manifest.py
功能描述: AIIS Demo 模块注册元数据
主要功能:
    - 声明默认关闭的参考路由、模型包和权限元数据
    - 保持 manifest 导入无数据库与运行时副作用
"""
from app.module_registry import ModuleManifest


manifest = ModuleManifest(
    name="aiis_demo",
    enabled=False,
    order=900,
    routers=("app.aiis_demo.api.routes:router",),
    models_package="app.aiis_demo.models",
    permissions=("aiis_demo",),
)
