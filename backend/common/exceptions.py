"""
文件路径: /backend/common/exceptions.py
功能描述: 业务异常定义
主要功能:
    - 提供 BusinessException
    - 绑定业务错误码与响应 code/message
"""
from common.error_codes import ErrorCode


class BusinessException(Exception):
    """业务异常，交由全局异常处理器转换为统一响应。"""

    def __init__(self, error_code: ErrorCode, code: int = 400, message: str | None = None):
        self.error_code = error_code
        self.code = code
        self.message = message or error_code.value
        super().__init__(self.message)

