"""B阶段F专用MySQL入口；显式空库/旧head升级/失败与回退副本，绝不使用共享建库fixture。"""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone
import importlib.util
import os
from pathlib import Path
import subprocess
import sys


def test_explicit_mysql_f_reintegration(monkeypatch):
    helper_path = Path(__file__).with_name("test_module_admission.py")
    spec = importlib.util.spec_from_file_location("be005_mysql_admission", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    scenario = os.environ["ARCH_BE005_MYSQL_SCENARIO"]
    assert scenario in {"f_empty", "f_upgrade", "f_rehearsal"}
    target = helper.DisposableTarget(scenario)
    try:
        from app.module_registry import import_model_packages
        from database import Base
        from sqlalchemy.orm import Session
        from tests.module_admission_fixtures import CORE_TABLES
        import_model_packages()
        protected = CORE_TABLES | {"energy_prices", "energy_price_hours"}
        if scenario != "f_empty":
            target.migrate("b8d0f2a4c6e8")
            # 旧16表中的公开合成用户/两代价格，其他Core表保持空且逐表checksum。
            from app.user.models.user import User
            from app.energy.models.energy_price import EnergyPrice
            from app.energy.models.energy_price_hour import EnergyPriceHour
            with Session(target.engine) as session:
                session.add(User(id=1, username="disposable", password="synthetic-not-a-login-hash", name="Fixture", role="admin", is_active=True))
                session.add(EnergyPrice(electric_price=1, hydrogen_price=2, argon_price=3, operator="legacy", remark="keep-legacy"))
                session.add(EnergyPriceHour(electric_price=4, hydrogen_price=5, argon_price=6, operator="legacy", remark="keep-hour", observed_at=datetime(2020, 1, 1), hour_start=datetime(2020, 1, 1)))
                session.commit()
            before = target.checksum(protected)
            if scenario == "f_rehearsal":
                # 仅在生成的可丢弃源码副本加失败revision；不改仓库/已发布migration。
                failure = target.root / "alembic/versions/be005_failure_probe.py"
                assert not failure.exists()
                failure.write_text('from alembic import op\nimport sqlalchemy as sa\nrevision="be005_failure"\ndown_revision="b8d0f2a4c6e8"\ndef upgrade():\n    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True))\ndef downgrade():\n    pass\n')
                try:
                    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "be005_failure"], cwd=target.root, capture_output=True, text=True)
                    assert result.returncode != 0, "Intentional duplicate-table migration must fail"
                    with target.engine.connect() as connection:
                        assert connection.exec_driver_sql("SELECT version_num FROM alembic_version").scalar_one() == "b8d0f2a4c6e8"
                    assert target.checksum(protected) == before
                finally:
                    failure.unlink()
            target.migrate("head")
            assert target.checksum(protected) == before
        else:
            target.migrate("head")
            before = target.checksum(protected)
            from app.user.models.user import User
            with Session(target.engine) as session:
                session.add(User(id=1, username="disposable", password="synthetic-not-a-login-hash", name="Fixture", role="admin", is_active=True))
                session.commit()
        target.assert_schema()
        assert len(Base.metadata.tables) == 58  # 专用F fixture，非通用生产接入上限。
        if scenario == "f_rehearsal":
            target.migrate("b8d0f2a4c6e8", "downgrade")
            from sqlalchemy import inspect
            assert set(inspect(target.engine).get_table_names()) == protected | {"alembic_version"}
            assert target.checksum(protected) == before
            target.migrate("head")
            target.assert_schema()
            assert target.checksum(protected) == before
            return

        async def run():
            from httpx import ASGITransport, AsyncClient
            from sqlalchemy import select
            from app.auxiliary.models.auxiliary import ShiftRule, ShiftTeam
            from app.auxiliary.services.async_auxiliary import AuxiliaryService
            from app.auxiliary.schemas.auxiliary_in import ShiftTeamCreate
            from app.equipment.models.equipment import EquipmentDrive
            from app.monitor.models.business_history import HistoryProcessCurve, HistoryEnergyConsumption
            from app.energy.models.energy_price_hour import EnergyPriceHour
            app, engine, sessions = target.api()
            async def request(client, method, path, **kwargs):
                response = await client.request(method, "/api/v1" + path, **kwargs)
                assert response.status_code == 200, (method, path, response.status_code, response.text)
                body = response.json()
                if "code" in body:
                    assert body["code"] == 200, (path, body)
                return body.get("data", body)
            try:
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://disposable") as client:
                    assert (await client.get("/api/v1/hr/health")).status_code == 404
                    assert await request(client, "GET", "/shift-rules") is None
                    assert (await request(client, "GET", "/shifts"))["total"] == 0
                    team = await request(client, "POST", "/shift-teams", json={"teamName": "B-synthetic"})
                    assert (await request(client, "GET", f'/shift-teams/{team["id"]}'))["teamName"] == "B-synthetic"
                    shift = await request(client, "POST", "/shifts", json={"teamId": team["id"], "date": date.today().isoformat()})
                    assert (await request(client, "GET", f'/shifts/{shift["id"]}'))["teamId"] == team["id"]
                    now = datetime.now().replace(microsecond=0)
                    stop = await request(client, "POST", "/stop-records", json={"startTime": (now-timedelta(minutes=30)).isoformat(), "endTime": now.isoformat(), "duration": 30, "reason": "synthetic", "status": "active"})
                    assert (await request(client, "GET", f'/stop-records/{stop["id"]}'))["duration"] == 30
                    async with sessions() as session:
                        rule = ShiftRule(name="B-explicit", cycle_name="B-cycle")
                        session.add(rule)
                        await session.commit()
                        rule_id = rule.id
                    await request(client, "PUT", f"/shift-rules/{rule_id}", json={"cycleName": "B-updated"})
                    assert (await request(client, "GET", "/shift-rules"))["cycleName"] == "B-updated"
                    project = await request(client, "POST", "/project/create", json={"name": "B-project"})
                    assert (await request(client, "GET", f'/project/{project["id"]}'))["name"] == "B-project"
                    maintenance = await request(client, "POST", "/items", json={"name": "B-maintenance", "code": "B001"})
                    assert (await request(client, "GET", f'/items/{maintenance["id"]}'))["code"] == "B001"
                    coil = "B-SYNTHETIC"
                    plan = await request(client, "POST", "/plans", json={"coilNo": coil, "grade": "Q235", "spec": "1*1000", "weight": 10, "thickness": 1, "width": 1000})
                    assert (await request(client, "GET", f'/plans/{plan["id"]}'))["coilNo"] == coil
                    performance = await request(client, "POST", "/performances", json={"planId": plan["id"], "coilNo": coil, "grade": "Q235", "weight": 10, "productionDate": date.today().isoformat(), "startTime": (now-timedelta(hours=1)).isoformat(), "endTime": now.isoformat(), "outputQuantity": 10, "qualifiedQuantity": 9, "qualityScore": 90, "efficiencyRate": 80})
                    assert (await request(client, "GET", f'/performances/{performance["id"]}'))["planId"] == plan["id"]
                    quality = await request(client, "POST", "/quality", json={"coilNo": coil, "grade": "Q235", "judgment": "qualified", "defects": [{"defectType": "synthetic"}]})
                    assert (await request(client, "GET", f'/quality/{quality["id"]}'))["coilNo"] == coil
                    report = await request(client, "POST", "/reports/generate", params={"report_type": "daily", "report_date": date.today().isoformat()})
                    assert (await request(client, "GET", f'/reports/{report["id"]}'))["total_coils"] >= 1
                    efficiency = await request(client, "GET", "/statistics/efficiency", params={"startDate": date.today().isoformat(), "endDate": date.today().isoformat()})
                    assert efficiency["summary"]["downtime"] >= 0.5
                    assert coil in str(await request(client, "GET", "/dashboard/recent-plans"))
                    async with sessions() as session:
                        session.add(EquipmentDrive(tv=1234, timestamp=now))
                        session.add(HistoryProcessCurve(device_id=1, coil_number=coil, z1_temp_act=789, created_at=now))
                        session.add(HistoryEnergyConsumption(device_id=1, coil_number=coil, elect_consum=12, n2_total=34, created_at=now))
                        await session.commit()
                    assert (await request(client, "GET", "/equipment/drive"))["process_params"]["tv"] == 1234
                    assert (await request(client, "GET", "/monitor/temperature", params={"date": date.today().isoformat()}))["latest"]["z1TempAct"] == 789
                    assert (await request(client, "GET", "/monitor/energy"))["todayTotal"]["elect"] == 12
                    price = {"electricPrice": 1.2345, "hydrogenPrice": 2, "argonPrice": 3}
                    saved = await request(client, "POST", "/energy", json=price)
                    assert (await request(client, "GET", "/energy/current"))["id"] == saved["id"]
                    assert any(row["id"] == saved["id"] for row in (await request(client, "GET", "/energy"))["items"])
                    groups = [{"electricPrice": 10, "hydrogenPrice": 20, "argonPrice": 30, "remark": "A"}, {"electricPrice": 40, "hydrogenPrice": 50, "argonPrice": 60, "remark": "B"}]
                    await asyncio.gather(*(request(client, "POST", "/energy", json={**group, "observedAt": saved["observedAt"]}) for group in groups))
                    current = await request(client, "GET", "/energy/current")
                    assert any(all(current[key] == group[key] for key in group) for group in groups)
                    async with sessions() as session:
                        rows = (await session.execute(select(EnergyPriceHour).where(EnergyPriceHour.hour_start == datetime.fromisoformat(current["hourStart"]).astimezone(timezone.utc).replace(tzinfo=None)))).scalars().all()
                        assert len(rows) == 1
                    duplicate = await client.post("/api/v1/shift-teams", json={"teamName": "B-synthetic"})
                    assert duplicate.json()["errorCode"] == "auxiliary.conflict"
                    async with sessions() as session:
                        service = AuxiliaryService(session)
                        try:
                            await service.create_shift_team(ShiftTeamCreate(team_name="B-synthetic"))
                        except Exception as error:
                            from common.exceptions import BusinessException
                            assert isinstance(error, BusinessException)
                            assert not session.in_transaction()
                        else:
                            raise AssertionError("Unique violation must rollback")
                        assert (await session.execute(select(ShiftTeam))).scalars().all()
                    # 仅测试副本中的HR manifest对象启用；源文件开关不变。
                    from dataclasses import replace
                    import app.hr.manifest as hr_manifest
                    monkeypatch.setattr(hr_manifest, "manifest", replace(hr_manifest.manifest, enabled=True))
                    hr_app, hr_engine, _ = target.api()
                    try:
                        async with AsyncClient(transport=ASGITransport(app=hr_app), base_url="http://disposable") as hr_client:
                            department = await request(hr_client, "POST", "/departments", json={"name": "B-department"})
                            assert department["name"] == "B-department"
                            assert "B-department" in str(await request(hr_client, "GET", "/departments"))
                    finally:
                        await hr_engine.dispose()
            finally:
                await engine.dispose()
        asyncio.run(run())
        # API写入前旧价格合成记录的原值仍应保留；禁止把正常同小时覆盖当历史迁移丢失。
        if scenario == "f_upgrade":
            with target.engine.connect() as connection:
                assert connection.exec_driver_sql("SELECT remark FROM energy_prices WHERE operator='legacy'").scalar_one() == "keep-legacy"
                assert connection.exec_driver_sql("SELECT remark FROM energy_price_hours WHERE operator='legacy'").scalar_one() == "keep-hour"
    finally:
        target.engine.dispose()
