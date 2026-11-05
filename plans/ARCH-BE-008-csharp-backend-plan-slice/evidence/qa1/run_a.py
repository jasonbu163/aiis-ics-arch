from pathlib import Path
import os,json,subprocess,time,hashlib
qa=Path(__file__).parent
repo=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch')
api=repo/'backend-dotnet';tool=Path('/private/tmp/arch-be008-sdk-rfSK3RBg');sdk=str(tool/'sdk/dotnet')
env=os.environ.copy();env.update({'BE008_TOOL_ROOT':str(tool),'BE008_DOTNET':sdk,'DOTNET_CLI_HOME':str(tool/'cli-home'),'NUGET_PACKAGES':str(tool/'nuget-packages'),'NUGET_HTTP_CACHE_PATH':str(tool/'nuget-http-cache'),'DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_CLI_TELEMETRY_OPTOUT':'1','TZ':'UTC'})
(qa/'a-temp-roots-before.json').write_text(json.dumps(sorted(str(x) for x in Path('/private/tmp').glob('arch-be008-*'))))
commands=[('sdk-info',[sdk,'--info']),('restore-api',[sdk,'restore','AIIS.Backend.Api.csproj','--configfile','NuGet.Config','--locked-mode']),('restore-tests',[sdk,'restore','tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj','--configfile','NuGet.Config','--locked-mode']),('build',[sdk,'build','AIIS.Backend.Api.csproj','--no-restore']),('api-items',[sdk,'msbuild','AIIS.Backend.Api.csproj','-getItem:Compile,Content,None','-nologo']),('a-tests',[sdk,'test','tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj','--no-restore','--filter','TestCategory!=MySQL','--logger','trx;LogFileName=qa1-a.trx','--results-directory',str(qa/'results-a')])]
results=[]
for name,args in commands:
 started=time.time()
 with (qa/(name+'.stdout')).open('w') as out,(qa/(name+'.stderr')).open('w') as err:
  result=subprocess.run(args,cwd=api,env=env,stdout=out,stderr=err)
 results.append({'name':name,'cwd':str(api),'argv':args,'exitCode':result.returncode,'elapsedSeconds':round(time.time()-started,3),'stdout':name+'.stdout','stderr':name+'.stderr'})
 (qa/'a-commands.json').write_text(json.dumps(results,indent=2)+'\n')
 print(name+': exit='+str(result.returncode),flush=True)
 if result.returncode:break
(qa/'a-temp-roots-after.json').write_text(json.dumps(sorted(str(x) for x in Path('/private/tmp').glob('arch-be008-*'))))
if all(x['exitCode']==0 for x in results) and len(results)==len(commands):
 items=json.loads((qa/'api-items.stdout').read_text())['Items']
 assert not any(x.get('Identity','').replace('\\','/').startswith('tests/') for key in ['Compile','Content','None'] for x in items.get(key,[]))
 print('API Compile/Content/None: no tests paths',flush=True)
else:raise SystemExit(1)
