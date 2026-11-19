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
        request = REQUESTS[index].model_validate(entry['body']) if index in REQUESTS else None
        if request is not None:
            assert integration_digests(request, RESOURCES[index], 101 if index in (4, 5, 6) else None) == (entry['requestDigest'], entry['businessDigest'])
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
        if request is None:
            continue
        data_class=type(request.data);data_schema=schemas[data_class.__name__]
        for field,definition in data_class.model_fields.items():
            if definition.annotation in (Decimal,int):
                prop=data_schema['properties'][definition.alias]
                assert prop['type']in ('number','integer') and 'anyOf'not in prop and prop.get('default','missing')is not None
    assert 'oneOf'in schemas['ProductionObservationData']
    from hashlib import sha256
    for vector in examples['normalizationVectors']:
        assert sha256(vector['canonicalUtf8'].encode()).hexdigest()==vector['sha256']
