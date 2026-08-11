"""Core latest snapshot tests with project-neutral payloads."""

from datetime import datetime

from app.monitor.models.monitor import PlcDbBlockLatestSnapshot
from app.monitor.services.async_realtime import get_realtime_latest_data


async def test_realtime_latest_returns_snapshot_facts_in_stable_order(db_session):
    collected_at = datetime(2026, 8, 9, 8, 1, 0)
    db_session.add_all(
        [
            PlcDbBlockLatestSnapshot(
                plc_key="example-plc",
                device_id=7,
                db_number=2,
                group_name="second",
                contract_version="example",
                collected_at=collected_at,
                driver="mock",
                quality="good",
                decoded_payload={"beta": 2},
            ),
            PlcDbBlockLatestSnapshot(
                plc_key="example-plc",
                device_id=7,
                db_number=1,
                group_name="first",
                contract_version="example",
                collected_at=collected_at,
                driver="mock",
                quality="good",
                decoded_payload={"alpha": 1},
            ),
        ]
    )
    await db_session.commit()

    latest = await get_realtime_latest_data(db_session, device_id=7)

    assert latest["deviceId"] == 7
    assert latest["hasSnapshot"] is True
    assert latest["stale"] is False
    assert [row["groupName"] for row in latest["snapshots"]] == ["first", "second"]
    assert latest["snapshots"][0]["decodedPayload"] == {"alpha": 1}


async def test_realtime_latest_is_stale_for_mixed_contracts(db_session):
    collected_at = datetime(2099, 8, 9, 8, 1, 0)
    db_session.add_all(
        [
            PlcDbBlockLatestSnapshot(
                plc_key="example-plc",
                device_id=8,
                db_number=1,
                group_name="first",
                contract_version="v1",
                collected_at=collected_at,
                driver="mock",
                quality="good",
                decoded_payload={"value": 1},
            ),
            PlcDbBlockLatestSnapshot(
                plc_key="example-plc",
                device_id=8,
                db_number=2,
                group_name="second",
                contract_version="v2",
                collected_at=collected_at,
                driver="mock",
                quality="good",
                decoded_payload={"value": 2},
            ),
        ]
    )
    await db_session.commit()

    latest = await get_realtime_latest_data(db_session, device_id=8)
    assert latest["stale"] is True
