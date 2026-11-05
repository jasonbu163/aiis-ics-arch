# QA2 independent execution of inspected QA1 public-contract matrix; media/header assertions strengthened for current candidate.
from pathlib import Path
import subprocess,os,time,json,urllib.request,urllib.error,urllib.parse,socket,hashlib,decimal,stat,re
qa=Path(__file__).parent/'formal-probes-attempt2';qa.mkdir(mode=0o700,exist_ok=False);repo=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');api=repo/'backend-dotnet';run=Path((qa.parent/'b-run-root.path').read_text().strip());manifest=json.loads((run/'manifest.json').read_text());assert manifest['task']=='ARCH-BE-008' and manifest['root']==str(run) and manifest['database']=='arch_be008_plan'
tool=Path('/private/tmp/arch-be008-sdk-rfSK3RBg');sdk=str(tool/'sdk/dotnet');dll=api/'bin/Debug/net10.0/AIIS.Backend.Api.dll';processes=[];requests=[];groups={};summary={};failed=[]
jsonl=(qa/'formal-http-cases.jsonl').open('a');os.chmod(qa/'formal-http-cases.jsonl',0o600)
base={'coilNo':'QA2B-INPUT','grade':'G','spec':'S','weight':'1.2300','thickness':'0.123','width':'10.00'}
fields=['coilNo','grade','spec','weight','thickness','width','materialStatus','density','entryLength','uncoiler1Tension','exitTension','process1Tension','entryLoopTension','exitLoopTension','entryUnitTension','entryLoopUnitTension','processUnitTension','exitLoopUnitTension','exitUnitTension','priority','remark']
scales={p:(4 if p=='weight' or 'UnitTension' in p else 3 if p=='thickness' else 2) for p in fields if p not in ['coilNo','grade','spec','materialStatus','priority','remark']}
maxima={p:('99999999.9999' if s==4 else '9999999.999' if s==3 else '99999999.99') for p,s in scales.items()}
def sql(query):
 p=subprocess.run(['docker','exec','-i',manifest['container'],'mysql','--defaults-extra-file=/run/secrets/root_client','--default-character-set=utf8mb4','--batch','--skip-column-names',manifest['database']],input=query,capture_output=True,text=True)
 assert p.returncode==0,p.stderr
 return p.stdout

def snapshot(name):
 data=sql("SHOW CREATE TABLE plans; SELECT COUNT(*) FROM plans; SHOW TABLES;")
 (qa/(name+'.tsv')).write_text(data);return data

def rows_fingerprint():
 data=sql('SELECT * FROM plans ORDER BY id;');return hashlib.sha256(data.encode()).hexdigest(),len(data.splitlines())

def request(label,method,path,body=None,expected=200,error=None,content_type='application/json'):
 import http.client
 if isinstance(body,dict):raw=json.dumps(body,ensure_ascii=True,separators=(',',':')).encode()
 elif isinstance(body,str):raw=body.encode()
 else:raw=body
 headers={'Content-Type':content_type} if raw is not None and content_type is not None else {}
 start=time.time();started_ms=int(start*1000);connection=http.client.HTTPConnection('127.0.0.1',18108,timeout=10)
 try:
  connection.request(method,path,body=raw,headers=headers);r=connection.getresponse();payload=r.read();status=r.status;response_headers=dict(r.getheaders())
 finally:connection.close()
 try:parsed=json.loads(payload)
 except (json.JSONDecodeError,UnicodeDecodeError):parsed=None
 record={'case':label,'method':method,'path':path,'requestHeaders':headers,'responseHeaders':response_headers,'input':None if raw is None else raw.decode('utf-8','backslashreplace'),'expectedStatus':expected,'actualStatus':status,'body':parsed if parsed is not None else payload.decode('utf-8','backslashreplace'),'bodyBytes':len(payload),'requestId':response_headers.get('X-Request-Id'),'elapsedMs':round((time.time()-start)*1000,3)}
 jsonl.write(json.dumps(record,ensure_ascii=True)+'\n');jsonl.flush();requests.append(record)
 assert status==expected,(label,status,record['body'])
 if expected==200 and path.startswith('/api/'):
  assert set(parsed)=={'code','message','data','timestamp'} and parsed['code']==200 and parsed['message']=='success'
 if error:
  assert isinstance(parsed,dict),(label,'missing unified JSON error envelope',record)
  assert parsed['code']==expected and parsed['data'] is None and parsed['message']==parsed['errorCode']==error,(label,parsed)
  assert {'code','message','data','errorCode','timestamp'}<=set(parsed)
  assert isinstance(parsed['timestamp'],int) and started_ms<=parsed['timestamp']<=int(time.time()*1000)
  assert set(parsed)<= {'code','message','data','errorCode','timestamp','errors'}
  assert not parsed.get('errors') or all(set(item)=={'field','rule'} for item in parsed['errors'])
  assert response_headers.get('Content-Type','').startswith('application/json')
 elif expected in [404,405]: assert not parsed or not isinstance(parsed,dict) or not parsed.get('errorCode','').startswith('plan_')
 assert response_headers.get('X-Request-Id'),label
 return parsed

def invalid(label,body,error='plan_invalid_request',expected=422,content_type='application/json'):
 return request(label,'POST','/api/v1/plans',body,expected,error,content_type)

def start(tz,name):
 with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',18108))
 env=os.environ.copy();env.update({'BE008_TOOL_ROOT':str(tool),'BE008_DOTNET':sdk,'DOTNET_CLI_HOME':str(tool/'cli-home'),'NUGET_PACKAGES':str(tool/'nuget-packages'),'NUGET_HTTP_CACHE_PATH':str(tool/'nuget-http-cache'),'DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_CLI_TELEMETRY_OPTOUT':'1','TZ':tz,'Database__ConnectionString':(run/'app-connection').read_text(),'LoggingOptions__Directory':str(qa/(name+'-logs')),'Modules__Plan__Enabled':'true','ASPNETCORE_URLS':'http://127.0.0.1:18108'})
 stdout=(qa/(name+'.stdout.jsonl')).open('w');stderr=(qa/(name+'.stderr')).open('w');p=subprocess.Popen([sdk,str(dll)],cwd=api,env=env,stdout=stdout,stderr=stderr)
 rec={'name':name,'pid':p.pid,'TZ':tz,'argv':[sdk,str(dll)],'cwd':str(api),'stdout':stdout.name,'stderr':stderr.name,'logs':str(qa/(name+'-logs')),'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exitCode':None};processes.append(rec);(qa/'formal-processes.json').write_text(json.dumps(processes,indent=2)+'\n')
 for _ in range(100):
  if p.poll() is not None:raise AssertionError('owned_api_exited_before_health:'+str(p.returncode))
  try:
   with urllib.request.urlopen('http://127.0.0.1:18108/health',timeout=1) as r:
    if r.status==200:break
  except (urllib.error.URLError,TimeoutError):time.sleep(.1)
 else:raise AssertionError('health_timeout')
 return p,rec,stdout,stderr

def stop(state):
 p,rec,out,err=state
 if p.poll() is None:p.terminate()
 try:p.wait(timeout=20)
 except subprocess.TimeoutExpired:
  rec['forcedKill']=True;p.kill();p.wait(timeout=5)
 out.close();err.close();rec.update({'exitCode':p.returncode,'stoppedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
 try:os.kill(p.pid,0);rec['pidAbsent']=False
 except ProcessLookupError:rec['pidAbsent']=True
 with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',18108));rec['port18108Rebind']=True
 (qa/'formal-processes.json').write_text(json.dumps(processes,indent=2)+'\n');assert rec['exitCode']==0 and rec['pidAbsent'] and rec['port18108Rebind'] and not rec.get('forcedKill')

state=None
try:
 before=snapshot('formal-before-start');finger_before=rows_fingerprint();summary['beforeRows']=finger_before[1]
 state=start('America/New_York','formal-ny');assert snapshot('formal-after-start')==before;summary['startupNoDdlOrSeed']=True
 health=request('health-liveness','GET','/health');assert health=={'status':'alive'}
 openapi=request('raw-openapi','GET','/openapi/v1.json');(qa/'formal-openapi.json').write_text(json.dumps(openapi,indent=2)+'\n')
 paths=openapi['paths'];operations=[(p,v) for p,d in paths.items() for v in d if v in ['get','post','put','delete','patch','head','options']]
 assert {(p,v) for p,v in operations if p.startswith('/api/')}=={('/api/v1/plans','get'),('/api/v1/plans','post'),('/api/v1/plans/{id}','get')};assert all(p in ['/api/v1/plans','/api/v1/plans/{id}','/health'] for p in paths)
 assert not any('bearer' in s.lower() or 'jwt' in s.lower() for s in openapi.get('components',{}).get('securitySchemes',{}));summary['openApiOperations']=operations
 for key in list(base):
  data=base.copy();del data[key];invalid('missing-'+key,data)
 groups['missingRequired']=6
 for key in fields:
  if key=='remark':continue
  invalid('null-'+key,{**base,key:None})
 groups['nullNonRemark']=20
 for key in fields:
  invalid('wrong-object-'+key,{**base,key:{}})
  invalid('wrong-array-'+key,{**base,key:[]})
 groups['wrongObjectOrArray']=42
 for key in ['coilNo','grade','spec','materialStatus','remark']:
  for val in [1,True]:invalid('wrong-type-'+key+'-'+str(val),{**base,key:val})
 groups['wrongScalarType']=10
 for key in ['id','status','createdAt','updatedAt','coil_no','CoilNo','unknown']:
  invalid('unknown-'+key,{**base,key:'synthetic'})
 for key in ['coilNo','weight','remark']:
  raw=json.dumps(base,separators=(',',':'))[:-1]+(',"remark":"first"' if key=='remark' else '')+','+json.dumps(key)+':'+('null' if key=='remark' else '1' if key=='weight' else '"again"')+'}';invalid('duplicate-'+key,raw)
 for label,raw in [('array','[]'),('root-null','null'),('scalar','3'),('concatenated','{}{}'),('comments','{/*x*/}'),('trailing-comma','{"coilNo":"X",}')]:invalid('json-'+label,raw)
 for raw in [b'{"coilNo":"bad-\xff"}',json.dumps(base).replace('"G"','"\\ud800"'),json.dumps(base).replace('"G"','"\\udc00"')]:invalid('invalid-unicode-'+str(len(requests)),raw)
 for i,media in enumerate(['text/plain','application/octet-stream','application/x-www-form-urlencoded','application/merge-patch+json','application/problem+json','multipart/form-data; boundary=qa2',None]):
  invalid('media-'+str(i),base,expected=415,content_type=media)
 groups['shapeAndMedia']=26
 for key in scales:
  for val in [True,'','NaN','Infinity','-1','100000000','0.'+'0'*scales[key]+'1']:
   invalid('decimal-reject-'+key+'-'+str(val),{**base,key:val})
 groups['decimalAllFieldsRejected']=len(scales)*7
 for val in ['1.000000000000000000000000000000000000001','99999999.999900000000000000000000000000001','1,234','１','1 2','\u00a01\u00a0','1e+','1e999999999','1e-999999999']:
  invalid('decimal-raw-precision-'+str(len(requests)),{**base,'weight':val})
 for val in [0,-1,11,True,'5',5.0,1.5]:invalid('priority-reject-'+str(val),{**base,'priority':val})
 invalid('width-zero',{**base,'width':0})
 for key,maxlen in [('coilNo',50),('grade',20),('spec',50),('materialStatus',20),('remark',500)]:invalid('unicode-too-long-'+key,{**base,key:'🧪'*(maxlen+1)})
 for key in ['grade','spec']:invalid('empty-required-'+key,{**base,key:''})
 for coil in ['',' \t\u001c\u0085\u3000','A\tB','A\u0000B','A\u001fB','A\u007f']:invalid('coil-rule-'+str(len(requests)),{**base,'coilNo':coil},'plan_invalid_coil_no')
 assert rows_fingerprint()==finger_before;summary['rejectedRequestsNoDataMutation']=True;groups['rejectedHttpRequests']=len(requests)-2
 stamp_before=sql('SELECT CURRENT_TIMESTAMP;').strip();created=request('minimal-create','POST','/api/v1/plans',{**base,'coilNo':' \tQA2B-Raw-Case \r','remark':None})['data'];stamp_after=sql('SELECT CURRENT_TIMESTAMP;').strip()
 assert set(created)==set(fields)|{'id','status','createdAt','updatedAt'} and len(created)==25
 for key,scale in scales.items():assert isinstance(created[key],str) and re.fullmatch(r'-?\d+\.\d{'+str(scale)+'}',created[key]),key
 assert created['materialStatus']=='special' and created['priority']==5 and created['remark'] is None and created['status']=='planned';assert created['coilNo']==' \tQA2B-Raw-Case \r';assert created['createdAt']==created['updatedAt'];assert re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+08:00',created['createdAt'])
 local=created['createdAt'][:19].replace('T',' ');assert stamp_before<=local<=stamp_after
 assert request('minimal-detail','GET','/api/v1/plans/'+str(created['id']))['data']==created
 summary['minimalPlan']=created;summary['databaseClockBracket']=[stamp_before,stamp_after]
 full={**base,'coilNo':'QA2B-完整-🧪','grade':'🧪'*20,'spec':'🧪'*50,'materialStatus':'','priority':1,'remark':'🧪'*500,**{p:v+'0'*4 for p,v in maxima.items()}}
 fullout=request('all-fields-max-create','POST','/api/v1/plans',full)['data'];assert len(fullout)==25
 for key,maximum in maxima.items():assert fullout[key]==maximum
 for key in ['coilNo','grade','spec','materialStatus','priority','remark']:assert fullout[key]==full[key]
 assert request('all-fields-max-detail','GET','/api/v1/plans/'+str(fullout['id']))['data']==fullout
 d=request('decimal-grammar-create','POST','/api/v1/plans',{**base,'coilNo':'QA2B-GRAMMAR','grade':' ','spec':' ','weight':' +001.2300e+1 ','thickness':'\t.3000\r\n','width':'12.'})['data'];assert [d[x] for x in ['weight','thickness','width']]==['12.3000','0.300','12.00']
 numeric=json.dumps({**base,'coilNo':'QA2B-NUMBER'}).replace('"1.2300"','1e2');assert request('number-exponent','POST','/api/v1/plans',numeric)['data']['weight']=='100.0000'
 raw=request('raw-case-create','POST','/api/v1/plans',{**base,'coilNo':'  QA2B-AbC  '})['data']
 for coil in ['qa2b-abc',' QA2B-ABC ']:invalid('ascii-sequential-'+coil,{**base,'coilNo':coil},'plan_coil_already_exists',409)
 assert request('raw-case-retained','GET','/api/v1/plans/'+str(raw['id']))['data']==raw
 scalar=request('coil-fifty-scalars','POST','/api/v1/plans',{**base,'coilNo':'🧪'*50})['data'];assert scalar['coilNo']=='🧪'*50
 quote=request('quoted-coil-create','POST','/api/v1/plans',{**base,'coilNo':"QA2B-' OR 1=1; --"})['data'];assert quote['coilNo']=="QA2B-' OR 1=1; --"
 # Independent query checks use actual database facts, never application-derived expected totals.
 total=int(sql('SELECT COUNT(*) FROM plans;').strip());assert request('empty-filters-ignored','GET','/api/v1/plans?coilNo=&grade=&materialStatus=&status=')['data']['total']==total
 for field,value in [('grade','🧪'*20),('materialStatus','custom'),('status','planned')]:
  column={'grade':'grade','materialStatus':'material_status','status':'status'}[field];value_hex=value.encode().hex();expected=int(sql("SELECT COUNT(*) FROM plans WHERE `"+column+"`=CONVERT(0x"+value_hex+" USING utf8mb4);").strip());listed=request('filter-'+field,'GET','/api/v1/plans?'+urllib.parse.urlencode({field:value}))['data'];assert listed['total']==expected and all(item[field]==value for item in listed['items'])
 for field in ['coilNo','grade','materialStatus','status']:
  attack="' OR 1=1; DROP TABLE plans; --";assert request('sql-parameter-'+field,'GET','/api/v1/plans?'+urllib.parse.urlencode({field:attack}))['data']['total']==0
 page=request('page-one','GET','/api/v1/plans?coilNo=PAGE-&pageSize=2')['data'];page2=request('page-two','GET','/api/v1/plans?coilNo=PAGE-&pageSize=2&page=2')['data'];page3=request('page-three','GET','/api/v1/plans?coilNo=PAGE-&pageSize=2&page=3')['data'];expected_ids=list(map(int,sql("SELECT id FROM plans WHERE coil_no LIKE '%PAGE-%' ORDER BY created_at DESC,id DESC;").splitlines()));assert [item['id'] for p in [page,page2,page3] for item in p['items']]==expected_ids;assert page['total']==5 and page['totalPages']==3
 beyond=request('page-beyond','GET','/api/v1/plans?coilNo=PAGE-&page=2147483647&pageSize=1')['data'];assert beyond=={'items':[],'total':5,'page':2147483647,'pageSize':1,'totalPages':5}
 assert request('wildcards-preserved','GET','/api/v1/plans?coilNo=PAGE-_%')['data']['total']==5
 assert request('unknown-query-ignored','GET','/api/v1/plans?priority=1&sort=id%3Bdrop&unknown=1')['data']==request('default-list','GET','/api/v1/plans')['data']
 for path in ['/api/v1/plans/0','/api/v1/plans/-1','/api/v1/plans/1.1','/api/v1/plans/2147483648','/api/v1/plans/abc','/api/v1/plans?page=','/api/v1/plans?page=-1','/api/v1/plans?page=1.0','/api/v1/plans?page=2147483647&pageSize=100','/api/v1/plans?pageSize=0','/api/v1/plans?pageSize=101','/api/v1/plans?page=1&page=2']:
  request('query-id-invalid-'+str(len(requests)),'GET',path,expected=422,error='plan_invalid_request')
 request('missing-positive-id','GET','/api/v1/plans/2147483647',expected=404,error='plan_not_found')
 for method,path,status in [('PUT','/api/v1/plans/1',405),('DELETE','/api/v1/plans/1',405),('PATCH','/api/v1/plans/1',405),('GET','/api/v1/plans/xlsx/template',404),('POST','/api/v1/plans/xlsx/import',404),('POST','/api/v1/auth/login',404),('GET','/swagger',404),('GET','/openapi/no-document.json',404)]:request('unsupported-'+method+'-'+path,method,path,expected=status)
 summary['rowsAfterProbes']=int(sql('SELECT COUNT(*) FROM plans;').strip());summary['probeCount']=len(requests);summary['groups']=groups;summary['beforeRestartPlan']=created
 before_restart=snapshot('formal-before-restart');stop(state);state=None
 state=start('UTC','formal-utc');after_restart=snapshot('formal-after-restart');assert before_restart==after_restart;assert request('restart-detail','GET','/api/v1/plans/'+str(created['id']))['data']==created;assert request('restart-full-detail','GET','/api/v1/plans/'+str(fullout['id']))['data']==fullout;summary['restartNoDdlOrSeed']=True;summary['restartPlanUnchanged']=True
 summary['finalSelect']=sql('SELECT id,coil_no,weight,thickness,width,status,priority,created_at,updated_at FROM plans ORDER BY id;');(qa/'formal-select-readback.tsv').write_text(summary.pop('finalSelect'))
except Exception as ex:
 failed.append({'type':type(ex).__name__,'detail':str(ex)});summary['failure']=failed[-1];raise
finally:
 if state is not None:stop(state)
 jsonl.close();summary.update({'task':'ARCH-BE-008','revision':'r1','runId':manifest['runId'],'processes':processes,'totalRecordedHttpCases':len(requests),'failed':failed,'candidateSha256':json.loads((qa.parent/'candidate-independent.json').read_text())['candidateSha256'],'dllSha256':hashlib.sha256(dll.read_bytes()).hexdigest()});(qa/'formal-http-summary.json').write_text(json.dumps(summary,ensure_ascii=True,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ['runId','totalRecordedHttpCases','failed','dllSha256']}),flush=True)

if failed:raise SystemExit(1)
