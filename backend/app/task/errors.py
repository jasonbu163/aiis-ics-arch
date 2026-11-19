"""任务 HTTP 合同错误，由 task 模块独占命名空间。"""
from enum import StrEnum


class TaskErrorCode(StrEnum):
    UNAUTHENTICATED = 'task.unauthenticated'
    FORBIDDEN = 'task.forbidden'
    NOT_FOUND = 'task.not_found'
    TARGET_CONFLICT = 'task.target_conflict'
    FIELD_IN_USE = 'task.field_in_use'
    ENDPOINT_RETIRED = 'task.endpoint_retired'
    CONFIG_REVISION_CONFLICT = 'task.config_revision_conflict'
    INVALID_REQUEST = 'task.invalid_request'
    UNAVAILABLE = 'task.unavailable'
    COMMIT_UNKNOWN = 'task.commit_unknown'


class TaskError(Exception):
    def __init__(self, key: TaskErrorCode, status: int, *, field: str | None = None, reason: str | None = None):
        self.key = key
        self.status = status
        self.details = {}
        if field is not None:
            self.details['field'] = field
        if reason is not None:
            self.details['reason'] = reason
        super().__init__(key.value)
