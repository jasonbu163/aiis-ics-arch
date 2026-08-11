"""
文件路径: /backend/app/router.py
功能描述: 主路由汇聚模块，注册所有子路由
主要功能:
    - 汇聚所有业务模块路由
    - 统一路由前缀和标签配置
"""
from fastapi import APIRouter

from app.user.api.routes import auth_router, users_router
from app.control_agent.api.routes import router as control_agent_router
from app.module_registry import include_module_routers

router = APIRouter()

# 认证与用户管理是安全边界入口，故意显式挂载，避免被普通业务模块 registry 隐式化。
router.include_router(auth_router)
router.include_router(users_router)

# control_agent 是现场 runtime / 授权边界，故意显式挂载，便于后续审查暴露面。
router.include_router(control_agent_router)

include_module_routers(router)
