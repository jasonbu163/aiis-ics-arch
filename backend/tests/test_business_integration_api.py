"""A0 八路拒绝、旧认证、模块关闭及依赖退出的真实 ASGI 内存测试。"""
from copy import deepcopy
from dataclasses import replace
import importlib
import json

import pytest
from fastapi import APIRouter, Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from common.integration.canonical import canonical_bytes
from common.integration.receipt import IntegrationReceipt, receipt_response
from starlette.responses import Response
from tests.test_business_integration_contract import example, REQUESTS, RESOURCES

pytestmark = pytest.mark.no_db
PATHS = ("equipment/temperature-samples", "equipment/drive-samples", "equipment/production-parameter-samples",
         "performances/production-observations", "performances/101/process-temperature-samples",
         "performances/101/process-tension-samples", "performances/101/process-speed-samples", "monitor/process-curve-samples")
OWNERS = ("equipment",) * 3 + ("performance",) * 4 + ("monitor",)


@pytest.mark.parametrize('index', (3,4,5,6))
async def test_retired_performance_integration_never_executes_old_handler(index):
    from core.registrar import create_app
    app = create_app(testing=True)
    path = '/api/v1/integration/' + PATHS[index]
    assert path not in app.openapi()['paths']
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        response = await client.post(path, json=example(index))
    assert response.status_code in (404, 405)
