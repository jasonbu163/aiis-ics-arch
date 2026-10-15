"""已挂载业务入口401/403、disabled404与所有method/path guard所有权审计。"""
import inspect
from types import SimpleNamespace
import pytest
from httpx import ASGITransport, AsyncClient
from core.registrar import create_app
from core.deps import get_current_user
from database import get_db

pytestmark=pytest.mark.no_db
PATHS=('/dashboard/stats','/equipment/drive','/energy/current','/items','/performances','/plans','/project/list','/quality','/reports','/shift-rules','/monitor/temperature?date=2026-10-14')


@pytest.mark.asyncio
async def test_all_business_owners_require_auth_then_explicit_grants():
    app=create_app(testing=True)
    app.dependency_overrides[get_db]=lambda:None
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
        for path in PATHS:
            assert (await client.get('/api/v1'+path)).status_code==401,path
        app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role='operator',username='fixture')
        for path in PATHS:
            assert (await client.get('/api/v1'+path)).status_code==403,path
        assert (await client.get('/api/v1/hr/health')).status_code==404
        assert (await client.get('/api/v1/aiis-demo/ping')).status_code==404


def test_each_registered_business_method_has_declared_owner_guard():
    from app.module_registry import get_module_manifests
    manifests={m.name:m for m in get_module_manifests()}
    app=create_app(testing=True)
    for route in app.routes:
        endpoint=getattr(route,'endpoint',None)
        module=getattr(endpoint,'__module__','')
        parts=module.split('.')
        if len(parts)<3 or parts[0]!='app' or parts[1] not in manifests or parts[1] in {'system','schema_maintenance'}:continue
        owner=parts[1];keys=set()
        def visit(dep):
            call=dep.call
            for cell in getattr(call,'__closure__',()) or ():
                value=cell.cell_contents
                if isinstance(value,(tuple,list)) and all(isinstance(x,str) for x in value):keys.update(value)
            for child in dep.dependencies:visit(child)
        visit(route.dependant)
        assert keys and keys.issubset(manifests[owner].permissions),(route.path,owner,keys)
