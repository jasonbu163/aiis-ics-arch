"""辅助非价格路由聚合。"""
from fastapi import APIRouter
from .auxiliary import shift_team_router, shift_router, shift_rule_router, stop_record_router
router = APIRouter()
for child in (shift_team_router, shift_router, shift_rule_router, stop_record_router):
    router.include_router(child)
