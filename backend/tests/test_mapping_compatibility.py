"""明确分域SQL及缺测SQL NULL，对照legacy默认；无真实连接。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.dialects import mysql
from sqlalchemy import null
from sqlalchemy.orm.persistence import _collect_insert_commands
from sqlalchemy.orm import attributes
from datetime import date
pytestmark=pytest.mark.no_db

def test_69_original_public_assignments_preserved_plus_three_empty_scopes():
    import hashlib
    from pathlib import Path
    import os
    archive=os.environ.get('ARCH_ACQ002_HISTORICAL_EXAMPLES')
    if not archive:
        pytest.skip('historical BE-006 examples are not supplied; current defaults are checked separately')
    root=Path(archive)
    expected={'.env.example': (8327, '8c7ded4ac77432248965640e1fe6dc1ca7256ad6c929682b00990d0c4cb6376b'), '.env.docker.dev.example': (8232, '4c8c796d67886968837619241a92b22247569693507dd7fd364107ea04739e9d'), '.env.docker.prod.example': (8311, 'ca162c464d944a44989869f4179ab054a129fd6637aeef2c6ca81df97ead118a')}
    scopes={"EQUIPMENT_MAPPING_INGEST_ID","PERFORMANCE_MAPPING_INGEST_ID","MONITOR_MAPPING_INGEST_ID"}
    for name,(length,digest) in expected.items():
        data=(root/name).read_bytes()
        assert hashlib.sha256(data[:length]).hexdigest()==digest
        assignments={line.split('=',1)[0]:line.split('=',1)[1] for line in data.decode().splitlines() if line and not line.startswith('#') and '=' in line}
        historical={key:value for key,value in assignments.items() if "_INTEGRATION_" not in key and not key.startswith("PLC_FACTS_")}
        assert len(historical)==72
        assert len(assignments)==91
        assert len(set(assignments)-set(historical))==19
        assert all(assignments[key]=='' for key in scopes)


def test_retired_equipment_and_monitor_mapping_settings_absent():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for name in ('.env.example','.env.docker.dev.example','.env.docker.prod.example'):
        assignments = dict(line.split('=',1) for line in (root/name).read_text().splitlines()
                           if line and not line.startswith('#') and '=' in line)
        assert 'EQUIPMENT_MAPPING_INGEST_ID' not in assignments
        assert 'MONITOR_MAPPING_INGEST_ID' not in assignments
