from pathlib import Path
import json,os,shutil,socket,subprocess
B=Path(__file__).parent;E=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/plans/FF-002-user-guide-and-runtime-positioning/evidence/dev-r1')
scene=B/'python-demo01-dry_run';protocol=json.loads((scene/'fixture/report.json').read_text());rows=[json.loads(x) for x in (scene/'runtime.stdout.jsonl').read_text().splitlines()]
pids={protocol['server_pid']}|{x['pid'] for x in rows if isinstance(x.get('pid'),int)};absent={}
for pid in pids:
 try:os.kill(pid,0);absent[str(pid)]=False
 except ProcessLookupError:absent[str(pid)]=True
assert all(absent.values())
for path in ['runtime.stdout.jsonl','runtime.stderr','fixture.stdout','fixture.stderr','fixture/report.json']:
 shutil.copyfile(scene/path,E/('attempt1-python-dry-'+Path(path).name))
ps=subprocess.run(['ps','-axo','pid=,ppid=,command='],capture_output=True,text=True);assert ps.returncode==0
survivors=[x for x in ps.stdout.splitlines() if str(B) in x and not any(tag in x for tag in ['preserve_failures.py','/bin/zsh -c','python3 -'])]
assert not survivors,survivors
failure={'initial_private_cache_sync':{'exit':1,'reason':'DNS unavailable for frozen dependency URLs','retained':'python-sync.log'},'normal_cache_write_attempt':{'exit':2,'reason':'sandbox denied normal cache .git write','retained':'python-sync-cache.log'},'copied_cache_offline_sync':{'exit':1,'reason':'locked pytest wheel absent','retained':'python-sync-offline.log'},'network_sync':{'exit':0,'reason':'auto-reviewed locked dependency preparation, no interpreter/target install','retained':'python-sync-network.log'},'attempt1':{'reason':'helper sent SIGINT to uv wrapper, wait10 timed out; finally sent SIGTERM and wait succeeded. Runtime exited0, simulated1, fixture report writes0/server_exit0; task process/listener scan clean. Unknown internal uv child PID was not captured before exit; later successful documented direct interpreter route records fixture/server/driver/runtime PIDs.','original_scene':str(scene),'extra_known_pids_absent':absent},'attempt2':{'reason':'normal scene completed but helper no-reuse bind hit TCP TIME_WAIT. lsof had no listeners; corrected probe to SO_REUSEADDR matching Python fixture and rechecked existing state without rerunning this scene.','scene':str(B/'python-demo01-dry_run-retry1')},'task_path_process_scan':{'exit':ps.returncode,'survivors':survivors},'documentation_corrections':['Python fixture server is a spawn child with owned server threads','Python manual TTL30s versus Rust60s; input max age10s unchanged','Python Sample has no pid member','Exact .venv/bin/python fixture signal target, no uv wrapper in scripted stop','Actual otool list includes Security/CoreFoundation/libc++/libiconv/libSystem','Removed unsupported uv python find --python option during source/CLI help check','Added explicit private tutorial source copy, environment/build/init/run steps','No formal source/config/locale/manifest/lock edits']}
(E/'failures-and-corrections.json').write_text(json.dumps(failure,indent=2)+'\n')
print('original known failure PIDs absent; no task-path processes')
