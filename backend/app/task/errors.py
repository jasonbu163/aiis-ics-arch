"""任务 HTTP 合同错误，由 task 模块独占命名空间。"""
from enum import StrEnum


class TaskErrorCode(StrEnum):
    UNAUTHENTICATED = 'task.unauthenticated'
    FORBIDDEN = 'task.forbidden'
    NOT_FOUND = 'task.not_found'
    STATE_CONFLICT = 'task.state_conflict'
    FIELD_VERSION_CONFLICT = 'task.field_version_conflict'
    CONFIG_REVISION_CONFLICT = 'task.config_revision_conflict'
    OBSERVATION_CONFLICT = 'task.observation_conflict'
    DISPATCH_CONFLICT = 'task.dispatch_conflict'
    ACTION_REQUEST_CONFLICT = 'task.action_request_conflict'
    PLAN_SUPPLEMENT_REQUIRED = 'task.plan_supplement_required'
    INVALID_REQUEST = 'task.invalid_request'
    UNAVAILABLE = 'task.unavailable'
    COMMIT_UNKNOWN = 'task.commit_unknown'


class TaskError(Exception):
    def __init__(self, key: TaskErrorCode, status: int):
        self.key = key
        self.status = status
        super().__init__(key.value)
