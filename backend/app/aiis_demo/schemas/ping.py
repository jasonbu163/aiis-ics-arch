"""
文件路径: /backend/app/aiis_demo/schemas/ping.py
功能描述: AIIS Demo ping 响应 Schema
主要功能:
    - 定义静态参考模块健康 payload
    - 复用统一 ApiSchema 的命名与属性配置
"""
from common.schema_base import ApiSchema


class PingResponse(ApiSchema):
    """Static health payload for the reference module."""

    module: str
    status: str
    reference: bool
