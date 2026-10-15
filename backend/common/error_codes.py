"""
文件路径: /backend/common/error_codes.py
功能描述: 稳定业务错误码定义
主要功能:
    - 集中定义业务错误码
    - 为前端 i18n 和逻辑判断提供稳定 key
"""
from enum import StrEnum


class ErrorCode(StrEnum):
    USER_NOT_FOUND = "user_not_found"
    USERNAME_ALREADY_EXISTS = "username_already_exists"
    INVALID_PASSWORD_POLICY = "invalid_password_policy"
    OLD_PASSWORD_REQUIRED = "old_password_required"
    OLD_PASSWORD_INCORRECT = "old_password_incorrect"
    CANNOT_CREATE_ADMIN = "cannot_create_admin"
    CANNOT_MANAGE_USER_ROLE = "cannot_manage_user_role"
    CANNOT_DISABLE_ADMIN = "cannot_disable_admin"
    CANNOT_DELETE_ADMIN = "cannot_delete_admin"
    CANNOT_DELETE_SELF = "cannot_delete_self"
    CANNOT_OPERATE_SELF = "cannot_operate_self"
    TARGET_USER_NOT_MANAGEABLE = "target_user_not_manageable"
    PROJECTION_MAPPING_HANDLER_NOT_FOUND = "projection_mapping_handler_not_found"
    PROJECTION_MAPPING_HANDLER_PROVENANCE_NOT_ALLOWED = "projection_mapping_handler_provenance_not_allowed"
    PROJECTION_MAPPING_SET_NOT_FOUND = "projection_mapping_set_not_found"
    PROJECTION_MAPPING_SET_ALREADY_EXISTS = "projection_mapping_set_already_exists"
    PROJECTION_MAPPING_REVISION_NOT_FOUND = "projection_mapping_revision_not_found"
    PROJECTION_MAPPING_REVISION_IMMUTABLE = "projection_mapping_revision_immutable"
    PROJECTION_MAPPING_INVALID_TRANSITION = "projection_mapping_invalid_transition"
    PROJECTION_MAPPING_VALIDATION_FAILED = "projection_mapping_validation_failed"

    # 本批旧源码兼容错误；未来模块自有命名空间StrEnum。
    PERFORMANCE_INVALID_TIME_RANGE = 'performance_invalid_time_range'
    PLAN_COIL_ALREADY_EXISTS = 'plan_coil_already_exists'
    PLAN_COIL_CONFLICT = 'plan_coil_conflict'
    PLAN_INVALID_COIL_NO = 'plan_invalid_coil_no'
    PLAN_INVALID_STATE = 'plan_invalid_state'
    PLAN_LINK_CANDIDATE_CONFLICT = 'plan_link_candidate_conflict'
    PLAN_NOT_FOUND = 'plan_not_found'
    PLAN_PERFORMANCE_ALREADY_LINKED = 'plan_performance_already_linked'
    PLAN_PERFORMANCE_NOT_FOUND = 'plan_performance_not_found'
    PLAN_PERFORMANCE_NOT_UNPLANNED = 'plan_performance_not_unplanned'
    PLAN_XLSX_UNSUPPORTED_CONFLICT_STRATEGY = 'plan_xlsx_unsupported_conflict_strategy'
    PLAN_XLSX_VALIDATION_FAILED = 'plan_xlsx_validation_failed'
    PROJECT_NOT_FOUND = 'project_not_found'
    QUALITY_DEFECT_NOT_FOUND = 'quality_defect_not_found'
    QUALITY_INSPECTION_NOT_FOUND = 'quality_inspection_not_found'
