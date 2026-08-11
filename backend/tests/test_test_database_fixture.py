"""Destructive test-database fixture safety checks."""

import pytest

from tests.conftest import ensure_test_database
from settings import settings


@pytest.mark.no_db
def test_destructive_test_cleanup_rejects_primary_database(monkeypatch):
    monkeypatch.setattr(settings, "TEST_MYSQL_DATABASE", settings.MYSQL_DATABASE)

    with pytest.raises(RuntimeError, match="must differ from MYSQL_DATABASE"):
        ensure_test_database()
