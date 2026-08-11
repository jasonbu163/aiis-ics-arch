"""
文件路径: /backend/tests/test_logging.py
功能描述: loguru 日志治理测试
主要功能:
    - 验证 API 与后台维护进程日志文件可创建
    - 验证 error-only 日志文件独立落盘
    - 验证日志文件为可解析 JSON Lines
    - 验证标准库 logging 会桥接到统一日志
    - 防止日志配置退化为仅 stdout 输出
"""
import json
import logging
from pathlib import Path

import pytest

from common import log as log_module
from common.log import log_event, log_projection_event, logger, setup_logger


pytestmark = pytest.mark.no_db


def flush_logger() -> None:
    """等待 loguru enqueue 日志写入完成。"""
    logger.complete()


def read_jsonl_records(path: Path) -> list[dict]:
    """读取 JSON Lines 日志并断言每行都可解析。"""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    return [json.loads(line) for line in lines]


def record_messages(records: list[dict]) -> list[str]:
    return [record["record"]["message"] for record in records]


def assert_process_logs(log_dir: Path, process_name: str, info_message: str, error_message: str) -> None:
    """断言指定进程日志和错误日志都已落盘。"""
    all_log = log_dir / f"{process_name}.log"
    error_log = log_dir / f"{process_name}-error.log"

    assert all_log.exists()
    assert error_log.exists()

    all_records = read_jsonl_records(all_log)
    error_records = read_jsonl_records(error_log)
    all_messages = record_messages(all_records)
    error_messages = record_messages(error_records)

    assert info_message in all_messages
    assert error_message in all_messages
    assert error_message in error_messages
    assert info_message not in error_messages
    assert all("time" in record["record"] for record in all_records)
    assert all("level" in record["record"] for record in all_records)
    assert all(record["record"]["extra"].get("process_name") == process_name for record in all_records)


def test_api_and_maintenance_log_files_are_created(tmp_path):
    """测试 API 与后台维护日志文件可创建且错误日志独立记录。"""
    api_info = "api info log persistence test"
    api_error = "api error log persistence test"
    maintenance_info = "maintenance info log persistence test"
    maintenance_error = "maintenance error log persistence test"

    try:
        setup_logger("api", log_dir=tmp_path, level="INFO", max_bytes=1024 * 1024, backup_count=1)
        logger.info(api_info)
        logger.error(api_error)
        flush_logger()
        assert_process_logs(tmp_path, "api", api_info, api_error)

        setup_logger("maintenance", log_dir=tmp_path, level="INFO", max_bytes=1024 * 1024, backup_count=1)
        logger.info(maintenance_info)
        logger.error(maintenance_error)
        flush_logger()
        assert_process_logs(tmp_path, "maintenance", maintenance_info, maintenance_error)
    finally:
        setup_logger("api")


def test_structured_event_and_standard_logging_are_jsonl(tmp_path):
    """测试结构化事件与标准库日志都会进入 JSON Lines。"""
    event = "backend_logging_jsonl_test"
    framework_message = "backend framework logging jsonl test"
    access_message = '127.0.0.1 - "GET /health HTTP/1.1" 200'

    try:
        setup_logger("api", log_dir=tmp_path, level="INFO", max_bytes=1024 * 1024, backup_count=1)

        log_event("INFO", event, result="success")
        logging.getLogger("uvicorn.error").info(framework_message)
        logging.getLogger("uvicorn.access").info(access_message)
        flush_logger()

        records = read_jsonl_records(tmp_path / "api.log")
        messages = record_messages(records)

        assert event in messages
        assert framework_message in messages
        assert access_message in messages
        assert any(record["record"]["extra"].get("event") == event for record in records)
    finally:
        setup_logger("api")


def test_projection_runner_channel_uses_separate_jsonl_file_sinks(tmp_path):
    """Runner records are isolated from API files while stdout remains shared."""
    api_info = "api channel info"
    api_error = "api channel error"
    runner_info = "projection runner channel info"
    runner_warning = "projection runner channel warning"
    runner_error = "projection runner channel error"

    try:
        setup_logger("api", log_dir=tmp_path, level="INFO", max_bytes=1024 * 1024, backup_count=1)
        logger.info(api_info)
        logger.error(api_error)
        log_projection_event("info", runner_info, batch_count=1)
        log_projection_event("warning", runner_warning, skipped_snapshot_count=1)
        log_projection_event("error", runner_error, error_code="test_error")
        flush_logger()

        api_records = read_jsonl_records(tmp_path / "api.log")
        api_error_records = read_jsonl_records(tmp_path / "api-error.log")
        runner_records = read_jsonl_records(tmp_path / "projection-runner.log")
        runner_error_records = read_jsonl_records(tmp_path / "projection-runner-error.log")

        assert {api_info, api_error}.issubset(record_messages(api_records))
        assert runner_info not in record_messages(api_records)
        assert runner_error not in record_messages(api_error_records)
        assert runner_info in record_messages(runner_records)
        assert runner_warning in record_messages(runner_records)
        assert runner_error in record_messages(runner_records)
        assert runner_error in record_messages(runner_error_records)
        assert all(
            record["record"]["extra"].get("channel") == "api"
            for record in api_records
        )
        assert all(
            record["record"]["extra"].get("channel") == "projection_runner"
            for record in runner_records
        )
        assert all(
            record["record"]["extra"].get("event") in {
                runner_info,
                runner_warning,
                runner_error,
            }
            for record in runner_records
        )
    finally:
        setup_logger("api")


def test_sqlalchemy_stays_warning_when_generic_logging_is_debug(tmp_path):
    """Generic DEBUG must not enable SQLAlchemy statement logging."""
    try:
        setup_logger("api", log_dir=tmp_path, level="DEBUG", max_bytes=1024 * 1024, backup_count=1)

        for logger_name in ("sqlalchemy", "sqlalchemy.engine", "sqlalchemy.pool"):
            assert logging.getLogger(logger_name).level == logging.WARNING
    finally:
        setup_logger("api")


def test_projection_runner_stdout_remains_jsonl_with_its_channel(tmp_path, capsys):
    """Channel filtering must not remove runner records from the shared stdout sink."""
    event = "projection_runner_stdout_jsonl_test"

    try:
        setup_logger("api", log_dir=tmp_path, level="INFO", max_bytes=1024 * 1024, backup_count=1)
        log_projection_event("info", event, tick_count=1)
        flush_logger()

        records = [
            json.loads(line)
            for line in capsys.readouterr().out.splitlines()
            if line.strip()
        ]
        runner_record = next(
            record for record in records if record["record"]["message"] == event
        )
        assert runner_record["record"]["extra"]["channel"] == "projection_runner"
    finally:
        with capsys.disabled():
            setup_logger("api")


def test_uvicorn_access_stdout_is_jsonl(tmp_path, capsys):
    """测试 Uvicorn access 输出不会绕过 JSON Lines sink。"""
    access_message = '127.0.0.1 - "GET /health HTTP/1.1" 200'

    try:
        setup_logger("api", log_dir=tmp_path, level="INFO", max_bytes=1024 * 1024, backup_count=1)
        logging.getLogger("uvicorn.access").info(access_message)
        flush_logger()

        lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
        assert lines
        records = [json.loads(line) for line in lines]
        assert access_message in record_messages(records)
    finally:
        with capsys.disabled():
            setup_logger("api")


def test_packaged_logging_avoids_multiprocessing_queue(monkeypatch):
    """冻结的单进程 package 不创建会在 SIGTERM 泄漏的日志 queue。"""
    monkeypatch.setattr(log_module.sys, "frozen", True, raising=False)
    assert log_module._should_enqueue_logs() is False

    monkeypatch.setattr(log_module.sys, "frozen", False, raising=False)
    assert log_module._should_enqueue_logs() is True
