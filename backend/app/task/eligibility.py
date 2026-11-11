"""默认关闭的任务集成资格与按版本冻结的目标映射。"""
from functools import lru_cache
import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import resolve_env_file
from app.task.domain import identifier, FIELD_NAME
from app.task.errors import TaskError, TaskErrorCode


class TaskSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=resolve_env_file(), extra='ignore')
    TASK_INTEGRATION_ENABLED: bool = False
    TASK_INTEGRATION_PROFILE_FILE: str = ''


def parse_profile(document):
    if not isinstance(document, dict) or set(document) != {'targets'} or not isinstance(document['targets'], dict):
        raise ValueError('invalid task profile')
    for target, item in document['targets'].items():
        identifier(target)
        if not isinstance(item, dict) or set(item) != {'mes', 'executors', 'versions'}:
            raise ValueError('invalid task target')
        for category in ('mes', 'executors'):
            entries = item[category]
            if not isinstance(entries, list) or len(entries) != len(set(entries)):
                raise ValueError('invalid task producers')
            for producer in entries:
                identifier(producer)
        if not isinstance(item['versions'], dict):
            raise ValueError('invalid task versions')
        for version, mapping in item['versions'].items():
            if not isinstance(version, str) or not version.isascii() or not version.isdigit() or int(version) < 1 or str(int(version)) != version:
                raise ValueError('invalid task version')
            if not isinstance(mapping, dict) or set(mapping) != {'dispatch', 'automatic', 'plcSeqMax'}:
                raise ValueError('invalid task mapping')
            if type(mapping['plcSeqMax']) is not int or not 0 <= mapping['plcSeqMax'] <= 9007199254740991:
                raise ValueError('invalid PLC sequence bound')
            fields, automatic = mapping['dispatch'], mapping['automatic']
            if not isinstance(fields, list) or len(fields) != len(set(fields)) or any(not isinstance(f, str) or not FIELD_NAME.fullmatch(f) for f in fields):
                raise ValueError('invalid dispatch mapping')
            if not isinstance(automatic, dict) or set(automatic) != {'producerId', 'recordSource'}:
                raise ValueError('invalid automatic stream')
            identifier(automatic['producerId'])
            if automatic['recordSource'] not in ('sma', 'ca_ff'):
                raise ValueError('invalid automatic source')
    return document


@lru_cache(maxsize=1)
def get_project_profile():
    try:
        config = TaskSettings()
        if not config.TASK_INTEGRATION_PROFILE_FILE:
            raise ValueError('closed')
        path = Path(config.TASK_INTEGRATION_PROFILE_FILE).resolve(strict=True)
        root = Path(__file__).resolve().parents[3]
        if path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError('invalid profile path')
        return parse_profile(json.loads(path.read_text(encoding='utf-8')))
    except (ValueError, TypeError, OSError, UnicodeError, TaskError):
        raise TaskError(TaskErrorCode.FORBIDDEN, 403) from None


def get_profile():
    if not TaskSettings().TASK_INTEGRATION_ENABLED:
        raise TaskError(TaskErrorCode.FORBIDDEN, 403)
    return get_project_profile()


def target_mapping(target, version):
    try:
        return get_project_profile()['targets'][identifier(target)]['versions'][str(version)]
    except (KeyError, TypeError):
        raise TaskError(TaskErrorCode.FORBIDDEN, 403) from None


def admit(target, producer, category, version=None):
    target, producer = identifier(target), identifier(producer)
    try:
        item = get_profile()['targets'][target]
        if category == 'automatic':
            allowed = target_mapping(target, version)['automatic']['producerId'] == producer
        elif category == 'read':
            allowed = producer in item['mes'] or producer in item['executors'] or any(v['automatic']['producerId'] == producer for v in item['versions'].values())
        else:
            allowed = producer in item[category]
        if not allowed:
            raise KeyError('producer')
        return item
    except (KeyError, TypeError):
        raise TaskError(TaskErrorCode.FORBIDDEN, 403) from None


def admit_read_target(target):
    try:
        get_profile()['targets'][identifier(target)]
    except (KeyError, TypeError):
        raise TaskError(TaskErrorCode.FORBIDDEN, 403) from None
