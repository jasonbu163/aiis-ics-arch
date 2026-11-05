import os,json,pathlib,subprocess,socket,tempfile,time,sys
q=pathlib.Path(__file__).parent;api=pathlib.Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet');records=[]
def command(name,args,env=None):
 started=time.time();p=subprocess.run(args,cwd=api,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(q/(name+'.stdout')).write_text(p.stdout);(q/(name+'.stderr')).write_text(p.stderr);records.append({'name':name,'argv':args,'cwd':str(api),'exitCode':p.returncode,'elapsedSeconds':time.time()-started});(q/'b-commands.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records[-1]),flush=True);return p
p=command('docker-version',['docker','version','--format','{{json .Server}}']);assert p.returncode==0
preflight={'resources':{}}
for kind,name in [('container','aiis-arch-be008-mysql'),('network','aiis-arch-be008-net'),('volume','aiis-arch-be008-mysql-data')]:
 p=command('preflight-'+kind,['docker',kind,'inspect','--format','{{.Name}}',name]);assert p.returncode!=0 and 'no such' in p.stderr.lower(),name;preflight['resources'][name]='absent'
for port in [13388,18108]:
 with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',port));preflight[str(port)]='actual_rebind_pass'
(q/'b-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
run=pathlib.Path(tempfile.mkdtemp(prefix='arch-be008-run-',dir='/private/tmp'));os.chmod(run,0o700);(q/'b-run-root.path').write_text(str(run)+'\n')
p=command('b-prepare',['tests/scripts/run-mysql-tests.sh','prepare','--run-root',str(run)]);assert p.returncode==0
print('B_PREPARED='+str(run),flush=True)
