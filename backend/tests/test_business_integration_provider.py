"""完整八路provider机器合同、闭合引用与ASGI typed成功壳；无数据库/监听。"""
from copy import deepcopy
from decimal import Decimal
import importlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from httpx import ASGITransport,AsyncClient
from common.integration.canonical import canonical_bytes,integration_digests
from common.integration.envelope import source_time
from common.integration.receipt import receipt_response
from tests.test_business_integration_contract import example,REQUESTS,RESOURCES
from tests.test_business_integration_api import PATHS,OWNERS
from tests.test_business_integration_storage import manifest

pytestmark=pytest.mark.no_db


def provider():
    root=Path(os.environ.get('ARCH_BE005_REPOSITORY',Path(__file__).resolve().parents[2]))
    directory=root/'contracts/published/http-api/business-integration-v1'
    return json.loads((directory/'openapi.json').read_text()),json.loads((directory/'examples.json').read_text(),parse_float=Decimal)


def resolve(document,schema):
    if '$ref'in schema:return document['components']['schemas'][schema['$ref'].split('/')[-1]]
    return schema


def test_published_provider_is_closed_typed_numeric_and_examples():
    document,examples=provider()
    assert len(document['paths'])==len(examples['requests'])==8
    schemas=document['components']['schemas']
    def refs(node):
        if isinstance(node,dict):
            if '$ref'in node:assert node['$ref'].split('/')[-1]in schemas
            for value in node.values():refs(value)
        elif isinstance(node,list):
            for value in node:refs(value)
    refs(document)
    for index,entry in enumerate(examples['requests']):
        request=REQUESTS[index].model_validate(entry['body'])
        assert integration_digests(request,RESOURCES[index],101 if index in (4,5,6) else None)==(entry['requestDigest'],entry['businessDigest'])
        path='/api/v1/integration/'+PATHS[index].replace('101','{record_id}')
        operation=document['paths'][path]['post']
        assert not operation.get('security')
        response=resolve(document,operation['responses']['200']['content']['application/json']['schema'])
        assert set(response['required'])=={'code','message','data'} and response['additionalProperties']is False
        receipt=resolve(document,response['properties']['data'])
        assert set(receipt['required'])==set(receipt['properties']) and receipt['additionalProperties']is False
        assert receipt['properties']['recordId']['anyOf'][0]['type']=='integer'
        assert receipt['properties']['changedFields']['items']['enum']
        for status in ('403','409','413','415','422','503','500'):
            error=resolve(document,operation['responses'][status]['content']['application/json']['schema'])
            assert error['properties']['code']['const']==int(status)
            assert error['properties']['message']==error['properties']['errorCode'] or {k:v for k,v in error['properties']['message'].items() if k!='title'}=={k:v for k,v in error['properties']['errorCode'].items() if k!='title'}
            assert error['properties']['data']['type']=='null'
        assert ('404'in operation['responses'])==(index in (4,5,6))
        data_class=type(request.data);data_schema=schemas[data_class.__name__]
        for field,definition in data_class.model_fields.items():
            if definition.annotation in (Decimal,int):
                prop=data_schema['properties'][definition.alias]
                assert prop['type']in ('number','integer') and 'anyOf'not in prop and prop.get('default','missing')is not None
    assert 'oneOf'in schemas['ProductionObservationData']
    from hashlib import sha256
    for vector in examples['normalizationVectors']:
        assert sha256(vector['canonicalUtf8'].encode()).hexdigest()==vector['sha256']


@pytest.mark.parametrize('index',(0,1,2,7))
async def test_api_success_uses_owner_service_receipt_after_full_dependency_exit(index,monkeypatch):
    owner=OWNERS[index];api=importlib.import_module('app.'+owner+'.api.integration')
    dto=importlib.import_module('app.'+owner+'.schemas.integration')
    type_names=('TemperatureReceipt','DriveReceipt','ProductionParameterReceipt','ProductionObservationReceipt','ProcessTemperatureReceipt','ProcessTensionReceipt','ProcessSpeedReceipt','ProcessCurveReceipt')
    calls=[]
    async def service(db,request,*args):
        calls.append('service')
        a,b=integration_digests(request,RESOURCES[index],101 if index in (4,5,6) else None)
        return getattr(dto,type_names[index]).model_validate(dict(contractVersion='aiis.business-integration/v1',digestProfile='bi-json/v1',producerId=request.producer_id,eventId=request.event_id,resource=RESOURCES[index],equipmentId=request.data.equipment_id,mappingId=request.mapping_id,mappingRevision=request.mapping_revision,requestDigest=a,businessDigest=b,receiptId=501,recordId=101,performanceId=101 if index in (3,4,5,6) else None,affectedRecordIds=[101],sourceTime='2026-11-04T10:00:00.123+08:00',committedAt='2026-11-04T10:01:00.123+08:00',status='committed',confirmation='business_committed',applied=True,outcome='created',originalOutcome='created',changedFields=[],businessRetention='no_auto_ttl'))
    if owner=='performance':module=api.observation if index==3 else api.process;name='receive_observation'if index==3 else'receive_sample'
    else:module=api.service;name='receive_sample'
    monkeypatch.setattr(module,name,service)
    from core.registrar import create_app
    app=create_app(testing=True)
    app.dependency_overrides[api.get_integration_config]=lambda:SimpleNamespace(require_ready=lambda *args:manifest(owner))
    from database import get_db
    class Session:
        async def __aenter__(self):calls.append('session');return self
        async def __aexit__(self,*args):calls.append('session_exit')
    async def session():return Session()
    monkeypatch.setattr(api,"get_db_session",session)
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture')as client:
        response=await client.post('/api/v1/integration/'+PATHS[index],content=canonical_bytes(example(index)),headers={'content-type':'application/json'})
    assert response.status_code==200 and response.json()['data']['recordId']==101
    assert calls==['session','service','session_exit']
