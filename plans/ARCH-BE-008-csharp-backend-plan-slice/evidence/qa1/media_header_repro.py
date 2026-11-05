from pathlib import Path
import subprocess,os,json,urllib.request,urllib.error,time,socket
qa=Path(__file__).parent;run=Path('/private/tmp/arch-be008-run-eihb7rry');api=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet');tool=Path('/private/tmp/arch-be008-sdk-rfSK3RBg');sdk=str(tool/'sdk/dotnet')
def sql(q):
 p=subprocess.run(['docker','exec','-i','aiis-arch-be008-mysql','mysql','--defaults-extra-file=/run/secrets/root_client','--batch','--skip-column-names','arch_be008_plan'],input=q,capture_output=True,text=True);assert p.returncode==0;return p.stdout
with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',18108))
env=os.environ.copy();env.update({'DOTNET_CLI_HOME':str(tool/'cli-home'),'NUGET_PACKAGES':str(tool/'nuget-packages'),'NUGET_HTTP_CACHE_PATH':str(tool/'nuget-http-cache'),'DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_CLI_TELEMETRY_OPTOUT':'1','TZ':'UTC','Database__ConnectionString':(run/'app-connection').read_text(),'LoggingOptions__Directory':str(qa/'media-repro-logs'),'Modules__Plan__Enabled':'true','ASPNETCORE_URLS':'http://127.0.0.1:18108'})
args=[sdk,str(api/'bin/Debug/net10.0/AIIS.Backend.Api.dll')];out=(qa/'media-repro.stdout.jsonl').open('w');err=(qa/'media-repro.stderr').open('w');before=sql('SELECT COUNT(*) FROM plans; SHOW CREATE TABLE plans; SHOW TABLES;');p=subprocess.Popen(args,cwd=api,env=env,stdout=out,stderr=err);result={'task':'ARCH-BE-008','revision':'r1','finding':'F-QA1-001','pid':p.pid,'TZ':'UTC','argv':args,'cases':[]};request_body=b'{"coilNo":"QA1-MEDIA-ONLY","grade":"G","spec":"S","weight":"1.2300","thickness":"0.123","width":"10.00"}'
try:
 for _ in range(100):
  try:
   with urllib.request.urlopen('http://127.0.0.1:18108/health',timeout=1) as r:assert r.status==200
   break
  except urllib.error.URLError:
   assert p.poll() is None;time.sleep(.1)
 else:raise AssertionError('owned_api_not_ready')
 for media in ['text/plain','application/octet-stream','application/x-www-form-urlencoded','application/merge-patch+json']:
  req=urllib.request.Request('http://127.0.0.1:18108/api/v1/plans',data=request_body,headers={'Content-Type':media},method='POST')
  try:r=urllib.request.urlopen(req,timeout=10)
  except urllib.error.HTTPError as ex:r=ex
  with r:
   data=r.read();result['cases'].append({'request':{'method':'POST','path':'/api/v1/plans','headers':{'Content-Type':media},'body':request_body.decode()},'response':{'status':r.status,'headers':dict(r.headers),'bodyBytes':len(data),'bodyUtf8':data.decode()}})
  assert result['cases'][-1]['response']['status']==415
 result['schemaAndRowsUnchanged']=sql('SELECT COUNT(*) FROM plans; SHOW CREATE TABLE plans; SHOW TABLES;')==before
 assert result['schemaAndRowsUnchanged']
finally:
 if p.poll() is None:p.terminate()
 p.wait(timeout=20);out.close();err.close();result['exitCode']=p.returncode
 try:os.kill(p.pid,0);result['pidAbsent']=False
 except ProcessLookupError:result['pidAbsent']=True
 with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',18108));result['port18108Rebind']=True
 (qa/'F-QA1-001-headers-repro.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pid':p.pid,'exitCode':p.returncode,'cases':[{ 'media':x['request']['headers']['Content-Type'],'status':x['response']['status'],'bodyBytes':x['response']['bodyBytes']} for x in result['cases']],'pidAbsent':result['pidAbsent'],'port18108Rebind':result['port18108Rebind']},indent=2),flush=True)
