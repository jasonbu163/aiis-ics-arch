#!/usr/bin/env bash
# ARCH-BE-008 明确子命令与 run manifest；裸入口仅帮助，无默认输入/资源副作用。
set -euo pipefail
if [[ $# == 0 || ${1:-} == --help ]]; then
  cat <<'HELP'
Usage: run-mysql-tests.sh prepare|test|cleanup --run-root /private/tmp/arch-be008-run-<nonce>
prepare: requires a new, empty, user-owned 0700 directory. Creates only the approved resources.
test: requires matching manifest/resource labels, BE008_TOOL_ROOT and BE008_DOTNET.
cleanup: coordinator only, after evidence persistence and explicit resource ownership review.
Uses fixed project/container/network/volume, loopback:13388, database arch_be008_plan.
HELP
  exit 0
fi
if [[ $# != 3 || $2 != --run-root ]]; then echo 'invalid_arguments' >&2; exit 2; fi
BE008_SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
export BE008_SCRIPT_DIR
exec python3 - "$1" "$3" <<'PY'
import os,sys,json,secrets,subprocess,socket,time,pathlib,stat,hashlib
command=sys.argv[1]; root=pathlib.Path(sys.argv[2]); api=pathlib.Path(os.environ['BE008_SCRIPT_DIR']).parents[1]
project='aiis-arch-be008'; container='aiis-arch-be008-mysql'; network='aiis-arch-be008-net'; volume='aiis-arch-be008-mysql-data'; database='arch_be008_plan'
if command not in ('prepare','test','cleanup'):sys.exit('unknown_subcommand')
if root.is_symlink() or root.parent != pathlib.Path('/private/tmp') or not root.name.startswith('arch-be008-run-') or not root.is_dir() or root.stat().st_uid!=os.getuid() or stat.S_IMODE(root.stat().st_mode)!=0o700:sys.exit('unsafe_run_root')
def run(args,stdin=None,check=True):
 p=subprocess.run(args,input=stdin,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if check and p.returncode:sys.exit('command_failed:'+args[0]+':'+str(p.returncode))
 return p

def save(name,value):
 p=root/name
 with open(p,'x') as f:os.chmod(p,0o600);f.write(value)
def inspect(kind,name):
 p=run(['docker',kind,'inspect',name],check=False)
 if p.returncode:return None
 return json.loads(p.stdout)[0]
def labels(obj,kind):return obj.get('Config',{}).get('Labels',{}) if kind=='container' else obj.get('Labels',{})
def verify(manifest):
 if manifest.get('task')!='ARCH-BE-008' or manifest.get('project')!=project or manifest.get('database')!=database or manifest.get('host')!='127.0.0.1' or manifest.get('port')!=13388 or manifest.get('root')!=str(root):sys.exit('manifest_target_mismatch')
 for kind,name in [('container',container),('network',network),('volume',volume)]:
  obj=inspect(kind,name)
  if not obj or labels(obj,kind).get('task')!='ARCH-BE-008' or labels(obj,kind).get('runId')!=manifest['runId']:sys.exit('resource_ownership_mismatch')
 obj=inspect('container',container)
 ports=obj.get('HostConfig',{}).get('PortBindings',{}).get('3306/tcp',[])
 if ports != [{'HostIp':'127.0.0.1','HostPort':'13388'}] or obj.get('Config',{}).get('Image')!='mysql:8.4.6':sys.exit('resource_target_mismatch')
 if manifest.get('containerId') and obj['Id']!=manifest['containerId']:sys.exit('container_identity_changed')
 return obj

def sql(text,db=True):
 return run(['docker','exec','-i',container,'mysql','--defaults-extra-file=/run/secrets/root_client','--batch','--skip-column-names']+([database] if db else []),text).stdout

def compose(action,extra=[]):
 return run(['docker','compose','--env-file',str(root/'compose.env'),'-p',project,'-f',str(api/'tests/infra/mysql.compose.yml'),action]+extra)
if command=='prepare':
 if any(root.iterdir()):sys.exit('run_root_not_empty')
 for kind,name in [('container',container),('network',network),('volume',volume)]:
  if inspect(kind,name):sys.exit('existing_named_resource_refused:'+name)
 for port in (13388,18108):
  with socket.socket() as s:
   try:s.bind(('127.0.0.1',port))
   except OSError:sys.exit('port_in_use:'+str(port))
 runid=secrets.token_hex(12); rootpwd=secrets.token_hex(32); apppwd=secrets.token_hex(32); fixturepwd=secrets.token_hex(32)
 save('root-password',rootpwd);save('root-client.cnf','[client]\nuser=root\npassword='+rootpwd+'\n')
 save('app-password',apppwd);save('fixture-password',fixturepwd)
 save('compose.env','BE008_RUN_ROOT='+str(root)+'\nBE008_RUN_ID='+runid+'\n')
 manifest={'task':'ARCH-BE-008','runId':runid,'root':str(root),'project':project,'container':container,'network':network,'volume':volume,'database':database,'host':'127.0.0.1','port':13388,'image':'mysql:8.4.6','state':'preparing'}
 save('manifest.json',json.dumps(manifest,indent=2)+'\n')
 pull=compose('pull'); print('docker_pull_exit=0',flush=True)
 compose('config',['--quiet']); compose('up',['-d']); print('docker_up_exit=0',flush=True)
 obj=verify(manifest)
 for _ in range(90):
  p=run(['docker','exec',container,'mysql','--defaults-extra-file=/run/secrets/root_client','-Nse','SELECT 1'],check=False)
  if p.returncode==0:break
  time.sleep(1)
 else:sys.exit('mysql_not_ready')
 version=sql('SELECT VERSION();').strip()
 if not version.startswith('8.4.6'):sys.exit('mysql_version_mismatch')
 if sql('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE();').strip()!='0':sys.exit('schema_not_empty')
 if sql('SELECT @@global.time_zone,@@session.time_zone,TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP,CURRENT_TIMESTAMP);').strip()!='+08:00\t+08:00\t28800':sys.exit('database_timezone_mismatch')
 sql((api/'tests/infra/plans.sql').read_text())
 sql("CREATE USER 'arch_be008_app'@'%' IDENTIFIED BY '"+apppwd+"'; GRANT INSERT, SELECT ON arch_be008_plan.* TO 'arch_be008_app'@'%'; CREATE USER 'arch_be008_fixture'@'%' IDENTIFIED BY '"+fixturepwd+"'; GRANT ALL PRIVILEGES ON arch_be008_plan.* TO 'arch_be008_fixture'@'%';")
 base='Server=127.0.0.1;Port=13388;Database=arch_be008_plan;Connection Timeout=5;Default Command Timeout=5;SslMode=Preferred;'
 save('app-connection',base+'User ID=arch_be008_app;Password='+apppwd)
 save('fixture-connection',base+'User ID=arch_be008_fixture;Password='+fixturepwd)
 image=inspect('image','mysql:8.4.6')
 manifest.update({'state':'prepared','containerId':obj['Id'],'serverVersion':version,'imageDigest':image['RepoDigests'],'imageArchitecture':image['Architecture']})
 (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 summary={'task':manifest['task'],'runId':runid,'target':'127.0.0.1:13388/arch_be008_plan','version':version,'digest':image['RepoDigests'],'architecture':image['Architecture'],'schema':sql('SHOW CREATE TABLE plans;'),'tables':sql('SHOW TABLES;'),'appGrants':sql("SHOW GRANTS FOR 'arch_be008_app'@'%';")}
 save('prepare-evidence.json',json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ('schema','appGrants')}))
else:
 manifest=json.loads((root/'manifest.json').read_text());verify(manifest)
 if command=='test':
  tool=pathlib.Path(os.environ.get('BE008_TOOL_ROOT',''));dotnet=pathlib.Path(os.environ.get('BE008_DOTNET',''))
  if tool.parent!=pathlib.Path('/private/tmp') or not tool.name.startswith('arch-be008-sdk-') or dotnet!=tool/'sdk/dotnet':sys.exit('private_sdk_required')
  env=os.environ.copy();env.update({'BE008_RUN_ROOT':str(root),'DOTNET_CLI_HOME':str(tool/'cli-home'),'NUGET_PACKAGES':str(tool/'nuget-packages'),'NUGET_HTTP_CACHE_PATH':str(tool/'nuget-http-cache'),'DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_CLI_TELEMETRY_OPTOUT':'1'})
  result=subprocess.run([str(dotnet),'test','tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj','--no-restore','--filter','TestCategory=MySQL','--logger','trx;LogFileName=mysql-'+str(time.time_ns())+'.trx','--results-directory',str(root/'results')],cwd=api,env=env)
  verify(manifest);readback=sql('SELECT id,coil_no,weight,thickness,width,status,priority,created_at,updated_at FROM plans ORDER BY id;')
  (root/'select-readback.tsv').write_text(readback);os.chmod(root/'select-readback.tsv',0o600)
  print('mysql_test_exit='+str(result.returncode));sys.exit(result.returncode)
 else:
  if os.environ.get('BE008_COORDINATOR_CLEANUP_CONFIRMED')!=manifest['runId']:sys.exit('coordinator_review_required')
  compose('down',['--volumes']);
  for kind,name in [('container',container),('network',network),('volume',volume)]:
   if inspect(kind,name):sys.exit('cleanup_resource_remains')
  manifest['state']='resources_removed';(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('owned_resources_removed')
PY
