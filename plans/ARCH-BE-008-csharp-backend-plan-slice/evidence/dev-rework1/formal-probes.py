# ARCH-BE-008 r1 rework1: explicit owned fixture and real DLL HTTP regression evidence.
import pathlib,json,subprocess,os,time,socket,http.client,hashlib,sys,re
run=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);api=pathlib.Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet');tool=pathlib.Path('/private/tmp/arch-be008-sdk-rfSK3RBg')
manifest=json.loads((run/'manifest.json').read_text());obj=json.loads(subprocess.check_output(['docker','container','inspect','aiis-arch-be008-mysql']))[0]
assert manifest['task']=='ARCH-BE-008' and obj['Config']['Labels']['task']=='ARCH-BE-008' and obj['Config']['Labels']['runId']==manifest['runId'] and obj['Id']==manifest['containerId']
def query(sql):
 return subprocess.run(['docker','exec','-i','aiis-arch-be008-mysql','mysql','--defaults-extra-file=/run/secrets/root_client','--default-character-set=utf8mb4','--batch','--skip-column-names','arch_be008_plan'],input=sql,text=True,capture_output=True,check=True).stdout

def fingerprint():return hashlib.sha256(query('SELECT * FROM plans ORDER BY id;').encode()).hexdigest()
def bind():
 with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',18108))
records=[];media_ids=[]
def request(method,path,payload=None,media=None,expect=200,key=None):
 body=None if payload is None else (json.dumps(payload,ensure_ascii=False).encode() if not isinstance(payload,str) else payload.encode())
 headers={} if media is None else {'Content-Type':media};started=int(time.time()*1000)
 connection=http.client.HTTPConnection('127.0.0.1',18108,timeout=10)
 try:
  connection.request(method,path,body=body,headers=headers);response=connection.getresponse();raw=response.read().decode();response_headers=dict(response.getheaders());status=response.status
 finally:connection.close()
 parsed=json.loads(raw) if raw else None
 record={'request':{'method':method,'path':path,'headers':headers,'body':None if body is None else body.decode()},'response':{'status':status,'headers':response_headers,'bodyBytes':len(raw.encode()),'bodyUtf8':raw}};records.append(record)
 with open(out/'formal-http-cases.jsonl','a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
 assert status==expect,(method,path,media,status,raw)
 if key:
  assert parsed and parsed['code']==expect and parsed['message']==key and parsed['errorCode']==key and parsed['data'] is None
  assert started<=parsed['timestamp']<=int(time.time()*1000) and response_headers.get('Content-Type','').startswith('application/json') and response_headers.get('X-Request-Id')
 elif expect in (404,405):assert not parsed or not str(parsed.get('errorCode','')).startswith('plan_')
 return parsed,response_headers

def schema():return re.sub(r'AUTO_INCREMENT=[0-9]+','AUTO_INCREMENT=<counter>',query('SHOW CREATE TABLE plans;'))
summaries=[];original=None;schema_before=schema();initial_count=int(query('SELECT COUNT(*) FROM plans;'))
for phase,tz in [('first','America/New_York'),('second','UTC')]:
 bind();env=os.environ.copy();env.update({'Database__ConnectionString':(run/'app-connection').read_text(),'LoggingOptions__Directory':str(out/'formal-logs'),'TZ':tz,'DOTNET_CLI_HOME':str(tool/'cli-home'),'NUGET_PACKAGES':str(tool/'nuget-packages'),'NUGET_HTTP_CACHE_PATH':str(tool/'nuget-http-cache'),'DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_CLI_TELEMETRY_OPTOUT':'1'})
 output=open(out/('formal-'+phase+'-stdout.jsonl'),'w');process=subprocess.Popen([str(tool/'sdk/dotnet'),'bin/Debug/net10.0/AIIS.Backend.Api.dll'],cwd=api,env=env,stdout=output,stderr=subprocess.STDOUT);(out/('formal-'+phase+'.pid')).write_text(str(process.pid)+'\n')
 try:
  for attempt in range(60):
   try:
    connection=http.client.HTTPConnection('127.0.0.1',18108,timeout=1)
    try:connection.request('GET','/health');r=connection.getresponse();assert r.status==200;r.read();break
    finally:connection.close()
   except OSError:assert process.poll() is None;time.sleep(.1)
  else:raise RuntimeError('owned_api_not_ready')
  assert int(query('SELECT COUNT(*) FROM plans;'))==initial_count+(0 if phase=='first' else 1)
  if phase=='first':
   before=fingerprint();denied={'coilNo':'RW1-MEDIA-ONLY','grade':'G','spec':'S','weight':'1.2300','thickness':'0.123','width':'10.00'}
   for media in ['text/plain','application/octet-stream','application/x-www-form-urlencoded','application/merge-patch+json','application/problem+json','multipart/form-data; boundary=rw1',None]:
    _,h=request('POST','/api/v1/plans',denied,media,415,'plan_invalid_request');media_ids.append(h['X-Request-Id'])
   request('POST','/api/v1/plans','{}','application/json',422,'plan_invalid_request')
   invalid=dict(denied);invalid['coilNo']=' \t ';request('POST','/api/v1/plans',invalid,'application/json',422,'plan_invalid_coil_no')
   request('GET','/api/v1/plans?page=0',expect=422,key='plan_invalid_request')
   request('GET','/api/v1/plans/2147483647',expect=404,key='plan_not_found')
   request('POST','/unknown',denied,'text/plain',404)
   request('DELETE','/api/v1/plans/1',denied,'text/plain',405)
   request('PUT','/api/v1/plans/1',denied,'application/json',405)
   assert fingerprint()==before,'rejected inputs modified rows'
   assert schema()==schema_before
   payload=dict(denied);payload['coilNo']='RW1-FORMAL-RESTART';result,headers=request('POST','/api/v1/plans',payload,'application/json; charset=utf-8',200);original=result['data'];assert len(original)==25 and original['createdAt']==original['updatedAt'] and original['createdAt'].endswith('+08:00')
   request('POST','/api/v1/plans',payload,'application/json',409,'plan_coil_already_exists')
   (out/'create-response.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  result,_=request('GET','/api/v1/plans/'+str(original['id']));assert result['data']==original
  assert int(query('SELECT COUNT(*) FROM plans;'))==initial_count+1 and schema()==schema_before
  assert query('SHOW TABLES;').strip()=='plans'
  summaries.append({'phase':phase,'pid':process.pid,'processTZ':tz,'planId':original['id'],'createdAt':original['createdAt'],'updatedAt':original['updatedAt'],'rows':initial_count+1,'createGetRestartSame25Fields':True,'schemaOnlyPlansUnchanged':True})
 finally:
  if process.poll() is None:process.terminate()
  code=process.wait(timeout=15);output.close();(out/('formal-'+phase+'.exit')).write_text(str(code)+'\n');assert code==0
  try:os.kill(process.pid,0)
  except ProcessLookupError:pass
  else:raise AssertionError('owned_pid_remaining')
 bind()

logs=[]
for path in list((out/'formal-logs').glob('*.jsonl'))+list(out.glob('formal-*-stdout.jsonl')):
 for line in path.read_text().splitlines():
  if line:logs.append(json.loads(line))
for requestid in media_ids:assert any(row.get('requestId')==requestid and row.get('event')=='plan_request_failed' and row.get('errorCode')=='plan_invalid_request' for row in logs),requestid
for name in ['root-password','app-password','fixture-password','app-connection','fixture-connection']:
 secret=(run/name).read_text();assert all(secret not in json.dumps(row,ensure_ascii=False) for row in logs+records)
summary={'task':'ARCH-BE-008','revision':'r1','finding':'F-QA1-001','httpCases':len(records),'nonJsonMediaCases':len(media_ids),'each415FullEnvelopeAndStableErrorLog':True,'nonJsonRequestIds':media_ids,'rejectedRowsFingerprintUnchanged':True,'422404405Preserved':True,'rowsBeforeFirstStartup':initial_count,'processes':summaries,'apiExitCodes':[0,0],'pidsAbsent':True,'port18108RebindWithReuseAddr':True,'parsedLogLines':len(logs),'secretScan':'no_matches'}
(out/'formal-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'formal-select-readback.tsv').write_text(query('SELECT id,coil_no,CAST(weight AS CHAR),CAST(thickness AS CHAR),CAST(width AS CHAR),status,priority,created_at,updated_at FROM plans ORDER BY id;'))
print(json.dumps(summary))
