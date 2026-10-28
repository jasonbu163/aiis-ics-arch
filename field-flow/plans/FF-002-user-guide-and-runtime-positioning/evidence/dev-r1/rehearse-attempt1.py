import pathlib,subprocess,os,json,signal,time,socket,hashlib,shutil,sys
B=pathlib.Path(__file__).parent; REPO=pathlib.Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch')
E=REPO/'field-flow/plans/FF-002-user-guide-and-runtime-positioning/evidence/dev-r1'; E.mkdir(parents=True,exist_ok=True)
log=(E/'commands.jsonl').open('a'); results=[]
def record(row): log.write(json.dumps(row)+'\n');log.flush()
def run(args,cwd,tag):
 p=subprocess.run(args,cwd=cwd,env={**os.environ,'UV_CACHE_DIR':str(B/'uv-cache')},capture_output=True,text=True,timeout=180)
 (E/(tag+'.stdout.txt')).write_text(p.stdout);(E/(tag+'.stderr.txt')).write_text(p.stderr)
 record(dict(tag=tag,args=args,cwd=str(cwd),exit=p.returncode)); assert p.returncode==0,(tag,p.stderr)
 return p.stdout
ports=[31102,31103,31880,32102,32103,32880]
def release():
 out=[]
 for port in ports:
  s=socket.socket();s.bind(('127.0.0.1',port));s.close();out.append(port)
 return out

def gone(pid):
 try:os.kill(pid,0);return False
 except ProcessLookupError:return True

def scenario(lang,case,mode):
 rust=lang=='rust'; project=B/lang; scene=B/f'{lang}-{case}-{mode}';scene.mkdir();state=scene/'state';fixtureout=scene/'fixture'
 bin=str(B/'target-product/release/field-flow') if rust else str(project/'.venv/bin/field-flow')
 config=project/'config'/('loopback.yaml' if case=='demo01' else 'teaching01.yaml')
 instance=f'ff-{lang}-{case}'
 run([bin,'state','init','--synthetic','--mode',mode,'--state-dir',str(state),'--instance-id',instance],project,f'{lang}-{case}-{mode}-init')
 before=release();fargs=([str(B/'target-fixture/release/ff-fixture')] if rust else ['uv','run','--locked','--python','3.11','--no-python-downloads','python','-m','tests.fixtures'])+['--config',str(config),'--evidence-dir',str(fixtureout)]
 fo=(scene/'fixture.stdout').open('w');fe=(scene/'fixture.stderr').open('w')
 fixture=subprocess.Popen(fargs,cwd=project,stdin=subprocess.PIPE,stdout=fo,stderr=fe,env={**os.environ,'UV_CACHE_DIR':str(B/'uv-cache')},text=True)
 record(dict(tag=f'{lang}-{case}-{mode}-fixture',args=fargs,cwd=str(project),pid=fixture.pid))
 runtime=None
 try:
  # Read-only listener inspection, no request changes command timestamps or counts.
  deadline=time.monotonic()+5
  wanted=ports[:3] if rust else ports[3:]
  while time.monotonic()<deadline:
   assert fixture.poll() is None, (fixture.poll(),(scene/'fixture.stderr').read_text())
   report=subprocess.run(['lsof','-nP',*[f'-iTCP:{x}' for x in wanted],'-sTCP:LISTEN'],capture_output=True,text=True)
   if all(f':{x} ' in report.stdout for x in wanted): break
   time.sleep(.02)
  else:raise AssertionError('fixture not ready')
  (E/f'{lang}-{case}-{mode}-listeners.txt').write_text(report.stdout)
  args=[bin,'run','--config',str(config),'--state-dir',str(state)]+(['--execute'] if mode=='execute' else [])
  ro=(scene/'runtime.stdout.jsonl').open('w');re=(scene/'runtime.stderr').open('w')
  runtime=subprocess.Popen(args,cwd=project,stdout=ro,stderr=re)
  record(dict(tag=f'{lang}-{case}-{mode}-runtime',args=args,cwd=str(project),pid=runtime.pid))
  time.sleep(2)
  assert runtime.poll() is None,(runtime.poll(),(scene/'runtime.stderr').read_text())
  runtime.send_signal(signal.SIGINT);code=runtime.wait(timeout=20);ro.close();re.close()
  record(dict(tag=f'{lang}-{case}-{mode}-runtime-wait',pid=runtime.pid,exit=code,signal='SIGINT'))
  assert code==0,(code,(scene/'runtime.stderr').read_text())
  if rust: fixture.communicate('\n',timeout=10)
  else:fixture.send_signal(signal.SIGINT);fixture.wait(timeout=10)
  fo.close();fe.close();assert fixture.returncode==0,(fixture.returncode,(scene/'fixture.stderr').read_text())
  record(dict(tag=f'{lang}-{case}-{mode}-fixture-wait',pid=fixture.pid,exit=fixture.returncode,signal='ENTER' if rust else 'SIGINT'))
  inspect=json.loads(run([bin,'state','inspect','--state-dir',str(state)],project,f'{lang}-{case}-{mode}-inspect'))
  protocol=json.loads((fixtureout/('protocol.json' if rust else 'report.json')).read_text())
  records=[json.loads(x) for x in (scene/'runtime.stdout.jsonl').read_text().splitlines()]
  pids=[fixture.pid,runtime.pid]
  for row in records:
   ctx=json.loads(row['context']) if isinstance(row.get('context'),str) else row
   if isinstance(ctx.get('pid'),int):pids.append(ctx['pid'])
  if rust:pids.append(protocol['native_pid'])
  pids=sorted(set(pids));absent={str(pid):gone(pid) for pid in pids};assert all(absent.values()),absent
  after=release();assert inspect['counts']==({'simulated':1} if mode=='dry_run' else {'confirmed':1}),inspect
  assert protocol['writes']==(0 if mode=='dry_run' else 1),protocol
  # Verify source/current document copies later; only sanitized synthetic outputs are persisted.
  for src,name in [(scene/'runtime.stdout.jsonl','runtime.jsonl'),(scene/'runtime.stderr','runtime.stderr.txt'),(scene/'fixture.stdout','fixture.stdout.txt'),(scene/'fixture.stderr','fixture.stderr.txt')]:shutil.copyfile(src,E/f'{lang}-{case}-{mode}-{name}')
  (E/f'{lang}-{case}-{mode}-protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
  summary=dict(language=lang,case=case,mode=mode,scene=str(scene),fixture_exit=fixture.returncode,runtime_exit=code,inspect=inspect,protocol_counts={k:v for k,v in protocol.items() if k!='trace'},pids_absent=absent,ports_before=before,ports_after=after)
  results.append(summary);(E/'rehearsal-summary.json').write_text(json.dumps(results,indent=2)+'\n');print(lang,case,mode,'OK',flush=True)
 finally:
  if runtime is not None and runtime.poll() is None:
   runtime.send_signal(signal.SIGTERM);runtime.wait(timeout=20)
  if fixture.poll() is None:
   if rust:fixture.communicate('\n',timeout=10)
   else:fixture.send_signal(signal.SIGTERM);fixture.wait(timeout=10)

for lang in ('rust','python'):
 project=B/lang;empty=B/f'{lang}-empty';empty.mkdir(exist_ok=True)
 bin=str(B/'target-product/release/field-flow') if lang=='rust' else str(project/'.venv/bin/field-flow')
 for tag,args in [('bare',[]),('en',['--lang','en-US','--help']),('zh',['--lang','zh-CN','--help'])]:run([bin]+args,empty,f'{lang}-help-{tag}')
 assert not list(empty.iterdir())
 for mode in ('dry_run','execute'):scenario(lang,'demo01',mode)
# Apply tutorial only to private source copies.
for lang in ('rust','python'):
 project=B/lang; rust=lang=='rust'; dest=project/('src/app/teaching01.rs' if rust else 'src/field_flow/app/teaching01.py')
 dest.write_text((B/f'{lang}-teaching.txt').read_text())
 shutil.copyfile(B/f'{lang}-teaching.yaml',project/'config/teaching01.yaml')
 run([sys.executable,str(B/f'{lang}-wiring.py')],project,lang+'-wiring')
 if rust:
  run(['cargo','build','--locked','--release','--no-default-features','--bin','field-flow','--target-dir',str(B/'target-product')],project,'rust-teaching-build-product')
  run(['cargo','build','--locked','--release','--features','test-fixture','--bin','ff-fixture','--target-dir',str(B/'target-fixture')],project,'rust-teaching-build-fixture')
 else:
  run(['uv','run','--locked','--python','3.11','--no-python-downloads','python','-m','compileall','-q','src'],project,'python-teaching-compile')
  run(['uv','run','--locked','--python','3.11','--no-python-downloads','python','-c','from field_flow.config import load; from field_flow.app import teaching01; c=load("config/teaching01.yaml"); assert c.flows[0].kind == "teaching01"; assert callable(teaching01.once)'],project,'python-teaching-import-config')
 for mode in ('dry_run','execute'):scenario(lang,'teaching01',mode)
print('all eight scenes OK; all six fixed ports released',flush=True)
