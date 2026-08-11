"""
文件路径: /backend/common/log.py
功能描述: 后端统一日志管理
主要功能:
    - 导出全局 loguru logger
    - 为 API、迁移与维护进程注册独立日志文件
    - 同时保留 stdout 与 error-only 日志文件
    - 将标准库 logging 桥接到 JSON Lines 输出
"""
import logging
import os
import sys
from pathlib import Path

from loguru import logger

from settings import settings


LOG_FORMAT = "{message}"
PROJECTION_RUNNER_LOG_CHANNEL = "projection_runner"


def _should_enqueue_logs() -> bool:
    """Use multiprocessing queues except in the forced single-process package."""
    return not getattr(sys, "frozen", False)


class InterceptHandler(logging.Handler):
    """Route standard-library logging records into loguru sinks."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _configure_standard_logging(level: str) -> None:
    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=level, force=True)

    sqlalchemy_level = "WARNING"
    framework_logger_levels = {
        "uvicorn": level,
        "uvicorn.error": level,
        "uvicorn.access": level,
        "sqlalchemy": sqlalchemy_level,
        "sqlalchemy.engine": sqlalchemy_level,
        "sqlalchemy.pool": sqlalchemy_level,
    }

    for logger_name, logger_level in framework_logger_levels.items():
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [intercept_handler]
        std_logger.propagate = False
        std_logger.setLevel(logger_level)


def log_event(level: str, event: str, **fields: object) -> None:
    """Emit a structured backend event through the shared JSONL logger."""
    logger.bind(event=event, **fields).log(level.upper(), event)


def log_projection_event(level: str, event: str, **fields: object) -> None:
    """Emit a runner event through the shared logger's dedicated channel."""
    logger.bind(
        channel=PROJECTION_RUNNER_LOG_CHANNEL,
        event=event,
        **fields,
    ).log(level.upper(), event)


def _is_projection_runner_record(record: dict[str, object]) -> bool:
    extra = record["extra"]
    return extra.get("channel") == PROJECTION_RUNNER_LOG_CHANNEL


def _is_default_record(record: dict[str, object]) -> bool:
    return not _is_projection_runner_record(record)


def setup_logger(
    process_name: str = "api",
    *,
    log_dir: str | os.PathLike[str] | None = None,
    level: str | None = None,
    max_bytes: int | None = None,
    backup_count: int | None = None,
) -> None:
    """注册当前进程日志输出。"""
    log_level = (level or settings.LOG_LEVEL).upper()
    log_path = Path(log_dir or settings.LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)

    max_file_bytes = max_bytes or settings.LOG_MAX_BYTES
    file_backup_count = backup_count or settings.LOG_BACKUP_COUNT
    enqueue_logs = _should_enqueue_logs()

    logger.remove()
    logger.configure(extra={"process_name": process_name, "channel": process_name})
    logger.add(
        sys.stdout,
        level=log_level,
        format=LOG_FORMAT,
        serialize=True,
        enqueue=enqueue_logs,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        log_path / f"{process_name}.log",
        level=log_level,
        format=LOG_FORMAT,
        serialize=True,
        rotation=max_file_bytes,
        retention=file_backup_count,
        encoding="utf-8",
        enqueue=enqueue_logs,
        backtrace=False,
        diagnose=False,
        filter=_is_default_record,
    )
    logger.add(
        log_path / f"{process_name}-error.log",
        level="ERROR",
        format=LOG_FORMAT,
        serialize=True,
        rotation=max_file_bytes,
        retention=file_backup_count,
        encoding="utf-8",
        enqueue=enqueue_logs,
        backtrace=True,
        diagnose=False,
        filter=_is_default_record,
    )
    logger.add(
        log_path / "projection-runner.log",
        level=log_level,
        format=LOG_FORMAT,
        serialize=True,
        rotation=max_file_bytes,
        retention=file_backup_count,
        encoding="utf-8",
        enqueue=enqueue_logs,
        backtrace=False,
        diagnose=False,
        filter=_is_projection_runner_record,
    )
    logger.add(
        log_path / "projection-runner-error.log",
        level="ERROR",
        format=LOG_FORMAT,
        serialize=True,
        rotation=max_file_bytes,
        retention=file_backup_count,
        encoding="utf-8",
        enqueue=enqueue_logs,
        backtrace=True,
        diagnose=False,
        filter=_is_projection_runner_record,
    )
    _configure_standard_logging(log_level)
