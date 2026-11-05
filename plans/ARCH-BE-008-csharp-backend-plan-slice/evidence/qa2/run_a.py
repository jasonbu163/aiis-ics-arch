import pathlib,os,subprocess,json,time,hashlib
q=pathlib.Path(__file__).parent
api=pathlib.Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet')
tool=pathlib.Path('/private/tmp/arch-be008-sdk-rfSK3RBg');dotnet=str(tool/'sdk/dotnet')
env=os.environ.copy();env.update({'BE008_TOOL_ROOT':str(tool),'BE008_DOTNET':dotnet,'DOTNET_CLI_HOME':str(tool/'cli-home'),'NUGET_PACKAGES':str(tool/'nuget-packages'),'NUGET_HTTP_CACHE_PATH':str(tool/'nuget-http-cache'),'DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_CLI_TELEMETRY_OPTOUT':'1','TZ':'UTC'})
commands=[('dotnet-info',[dotnet,'--info']),('restore-api',[dotnet,'restore','AIIS.Backend.Api.csproj','--configfile','NuGet.Config','--locked-mode']),('restore-tests',[dotnet,'restore','tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj','--configfile','NuGet.Config','--locked-mode']),('build',[dotnet,'build','AIIS.Backend.Api.csproj','--no-restore']),('msbuild-items',[dotnet,'msbuild','AIIS.Backend.Api.csproj','-getItem:Compile,Content,None','-nologo']),('a',[dotnet,'test','tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj','--no-restore','--filter','TestCategory!=MySQL','--logger','trx;LogFileName=qa2-a.trx','--results-directory',str(q/'results-a')])]
results=[]
for name,argv in commands:
 start=time.time();p=subprocess.run(argv,cwd=api,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(q/(name+'.stdout')).write_text(p.stdout);(q/(name+'.stderr')).write_text(p.stderr);item={'name':name,'argv':argv,'cwd':str(api),'exitCode':p.returncode,'elapsedSeconds':time.time()-start};results.append(item);(q/'a-commands.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(item),flush=True)
 if p.returncode:raise SystemExit(p.returncode)
items=json.loads((q/'msbuild-items.stdout').read_text())['Items'];assert all(not x['Identity'].replace('\\','/').startswith('tests/') for v in items.values() for x in v)
print('A_COMMANDS_AND_ITEMS_PASS',flush=True)
