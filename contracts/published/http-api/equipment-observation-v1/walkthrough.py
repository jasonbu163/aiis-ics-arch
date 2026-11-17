#!/usr/bin/env python3
"""Run a synthetic task-000042 walkthrough against a provisioned loopback fixture."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True, help='Isolated loopback API, e.g. http://127.0.0.1:18395')
    parser.add_argument('--fixture-ack', required=True, help='Enter DISPOSABLE-OBS-FIXTURE for a dedicated disposable fixture')
    args = parser.parse_args()
    base = urlparse(args.base_url)
    if base.scheme != 'http' or base.hostname not in ('127.0.0.1', 'localhost', '::1') or base.path not in ('', '/'):
        parser.error('base URL must be an isolated loopback HTTP origin')
    if args.fixture_ack != 'DISPOSABLE-OBS-FIXTURE':
        parser.error('this fixed-identity writer requires a dedicated disposable fixture, not an existing dev database')
    required = ('OBS_DEMO_ADMIN_USER', 'OBS_DEMO_ADMIN_PASS', 'OBS_DEMO_EXTERNAL_TOKEN', 'OBS_DEMO_SMA_TOKEN')
    if any(not os.environ.get(key) for key in required):
        parser.error('provide the four OBS_DEMO_* environment variables documented in README')

    def call(method, path, token=None, body=None, query=None, acceptable=(200,)):
        url = args.base_url.rstrip('/') + '/api/v1' + path
        if query:
            url += '?' + urlencode(query)
        payload = None if body is None else json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        headers = {'Accept': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        if payload is not None:
            headers['Content-Type'] = 'application/json'
        try:
            with urlopen(Request(url, data=payload, method=method, headers=headers), timeout=15) as result:
                status, data = result.status, json.load(result)
        except HTTPError as error:
            status = error.code
            try:
                data = json.load(error)
            except (ValueError, UnicodeError):
                data = {}
        if status not in acceptable:
            raise RuntimeError(f'{method} {path}: HTTP {status}, errorCode={data.get("errorCode", "validation") if isinstance(data, dict) else "validation"}')
        return status, data

    _, login = call('POST', '/auth/login', body={'username': os.environ['OBS_DEMO_ADMIN_USER'],
                                                  'password': os.environ['OBS_DEMO_ADMIN_PASS']})
    admin = login['data']['accessToken']
    external = os.environ['OBS_DEMO_EXTERNAL_TOKEN']
    sma_token = os.environ['OBS_DEMO_SMA_TOKEN']
    keys = ('furnaceZone1Actual', 'furnaceZone1Set', 'furnaceHeatingReady')
    for key, zh, en, typ in zip(keys, ('实际温度', '设定温度', '加热就绪'),
                                ('Actual temperature', 'Set temperature', 'Heating ready'),
                                ('number', 'number', 'boolean')):
        metric = {'metricKey': key, 'sourceGroupKey': 'temperature', 'category': 'temperature',
                  'nameZh': zh, 'nameEn': en, 'valueType': typ,
                  'unit': '°C' if typ == 'number' else None, 'decimals': 1 if typ == 'number' else None}
        call('POST', '/equipment/metric-configs', admin, metric, acceptable=(200, 409))
    for target in ('latest', 'history'):
        for index, key in enumerate(keys if target == 'latest' else keys[:2], 1):
            binding = {'target': target, 'groupKey': 'temperature', 'slotNo': index if target == 'latest' else index + 6,
                       'metricKey': key, 'enabled': True}
            call('POST', '/equipment/metric-slot-bindings', admin, binding, acceptable=(200, 409))
    card = {'cardKey': 'zone1', 'pageKey': 'temperature', 'titleZh': '加热区 1', 'titleEn': 'Heating Zone 1',
            'enabled': True, 'sortOrder': 1, 'items': [{'metricKey': key, 'enabled': True} for key in keys[:2]]}
    curve = {'curveGroupKey': 'zone1', 'category': 'temperature', 'titleZh': '加热区 1', 'titleEn': 'Heating Zone 1',
             'enabled': True, 'sortOrder': 1, 'series': [{'metricKey': key, 'enabled': True} for key in keys[:2]]}
    call('POST', '/equipment/card-configs', admin, card, acceptable=(200, 409))
    call('POST', '/monitor/curve-configs', admin, curve, acceptable=(200, 409))

    run_id = str(time.time_ns() // 1000)
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)
    times = [(now - timedelta(seconds=11)).isoformat(), (now - timedelta(seconds=1)).isoformat()]
    sample_ids = [f'demo-external-{run_id}', f'demo-sma-{run_id}']
    points = ('point-active-task-no', 'point-zone1-temp-act', 'point-zone1-temp-set', 'point-zone1-ready')
    for index, stamp in enumerate(times):
        data = ('000042', 811.2 + index, 815.0, False)
        types = ('STRING[50]', 'REAL', 'REAL', 'BOOL')
        fact = {'contractVersion': 'plc-facts/v2', 'instanceId': 'daa-fixture', 'sampleId': sample_ids[index],
                'plcId': 'plc-01', 'dbNumber': 42, 'groupId': 'temperature', 'configRevision': 'r1',
                'sourceGeneration': 'generation-1', 'sourceSeq': str(int(run_id) + index),
                'points': [{'pointId': point, 'dataType': typ, 'value': value, 'quality': 'good', 'observedAt': stamp}
                           for point, typ, value in zip(points, types, data)]}
        call('POST', '/integration/plc-facts/samples', body=fact)

    query = {'equipmentId': 'line-01', 'groupKey': 'temperature', 'target': 'history'}
    for token in (external, sma_token):
        _, definitions = call('GET', '/integration/metric-definitions', token, query=query)
        assert {item['metricKey'] for item in definitions['data']['definitions']} >= set(keys[:2])
    ext = {'sourceRefs': [{'kind': 'external_event', 'sourceEventId': 'vendor-' + run_id}],
           'data': {'taskNo': '000042', 'sampledAt': times[0], 'values': {keys[0]: 811.2, keys[1]: 815.0}}}
    ext_history = {'sourceRefs': ext['sourceRefs'], 'data': dict(ext['data'], quality='good')}
    refs = [{'kind': 'plc_fact', 'instanceId': 'daa-fixture', 'plcId': 'plc-01',
             'sampleId': sample_ids[1], 'pointId': point} for point in points]
    sma = {'contractVersion': 'aiis.metric-ingest/v1', 'producerId': 'sma-line-01',
           'eventId': 'demo-latest-' + run_id, 'mappingId': 'sma-temperature', 'mappingRevision': 'r1',
           'sourceRefs': refs, 'data': {'equipmentId': 'line-01', 'groupKey': 'temperature', 'taskNo': '000042',
           'sampledAt': times[1], 'quality': 'good', 'values': {keys[0]: 812.2, keys[1]: 815.0, keys[2]: False}}}
    sma_history = dict(sma, eventId='demo-history-' + run_id,
                       data=dict(sma['data'], values={keys[0]: 812.2, keys[1]: 815.0}))
    receipts = []
    for token, body, path in ((external, ext, '/integration/equipment/latest-snapshots'),
                              (external, ext_history, '/integration/monitor/history-samples'),
                              (sma_token, sma, '/integration/equipment/latest-snapshots'),
                              (sma_token, sma_history, '/integration/monitor/history-samples')):
        _, result = call('POST', path, token, body)
        receipts.append(result['data'])
        assert result['data']['outcome'] == 'stored'
    _, replay = call('POST', '/integration/equipment/latest-snapshots', external, ext)
    assert replay['data'] == receipts[0]
    _, cards = call('GET', '/equipment/latest-cards', admin,
                    query={'equipmentId': 'line-01', 'pageKey': 'temperature'})
    assert cards['data']['taskNo'] == '000042'
    card_data = next(item for item in cards['data']['cards'] if item['cardKey'] == 'zone1')
    values = {item['metricKey']: item['value'] for item in card_data['items']}
    assert values[keys[0]] == 812.2 and values[keys[1]] == 815.0
    _, curves = call('GET', '/monitor/history-curves', admin,
                     query={'equipmentId': 'line-01', 'category': 'temperature', 'taskNo': '000042',
                            'from': (now - timedelta(minutes=1)).isoformat(), 'to': now.isoformat()})
    assert next(group for group in curves['data']['groups'] if group['curveGroupKey'] == 'zone1')['series']
    for receipt, path in ((receipts[2], '/equipment/admin/latest-snapshots/'),
                          (receipts[3], '/monitor/admin/history-samples/')):
        _, detail = call('GET', path + receipt['recordId'], admin)
        assert detail['data']['taskEvidence']['pointId'] == 'point-active-task-no'
    print(json.dumps({'result': 'pass', 'equipmentId': 'line-01', 'taskNo': '000042', 'card': 'zone1',
                      'actual': values[keys[0]], 'set': values[keys[1]],
                      'targets': [receipt['target'] for receipt in receipts],
                      'outcomes': [receipt['outcome'] for receipt in receipts],
                      'taskEvidence': 'verified', 'externalReplay': 'same receipt'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, RuntimeError, OSError) as exc:
        print('Walkthrough failed:', str(exc), file=sys.stderr)
        raise SystemExit(1)
