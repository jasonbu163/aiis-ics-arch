"""辅助模块稳定错误；不扩展全局枚举。"""
from enum import StrEnum
class AuxiliaryErrorCode(StrEnum):
    NOT_FOUND = "auxiliary.not_found"
    CONFLICT = "auxiliary.conflict"
