from pathlib import Path
import json,os,subprocess,shutil,hashlib,re,socket,platform
B=Path(__file__).parent;R=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');E=R/'field-flow/plans/FF-002-user-guide-and-runtime-positioning/evidence/dev-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Recover completed Python dry scene after helper-only TIME_WAIT bind assertion.
summary=[x for x in json.loads((E/'rehearsal-summary.json').read_text()) if not (x['language']=='python' and x['case']=='demo01' and x['mode']=='dry_run')];scene=B/'python-demo01-dry_run-retry1'
protocol=json.loads((scene/'fixture/report.json').read_text());bin=B/'python/.venv/bin/field-flow'
pr=subprocess.run([str(bin),'state','inspect','--state-dir',str(scene/'state')],capture_output=True,text=True);assert pr.returncode==0;inspect=json.loads(pr.stdout);assert inspect['counts']=={'simulated':1}
commands=[json.loads(x) for x in (E/'commands.jsonl').read_text().splitlines()]
pids=[x['pid'] for x in commands if x['tag'] in ('python-demo01-dry_run-fixture','python-demo01-dry_run-runtime')]+[protocol['server_pid']]
rows=[json.loads(x) for x in (scene/'runtime.stdout.jsonl').read_text().splitlines()];pids += [x['pid'] for x in rows if isinstance(x.get('pid'),int)]
absent={}
for pid in sorted(set(pids)):
 try:os.kill(pid,0);absent[str(pid)]=False
 except ProcessLookupError:absent[str(pid)]=True
assert all(absent.values());assert protocol['writes']==0 and protocol['server_exit']==0
for src,name in [(scene/'runtime.stdout.jsonl','runtime.jsonl'),(scene/'runtime.stderr','runtime.stderr.txt'),(scene/'fixture.stdout','fixture.stdout.txt'),(scene/'fixture.stderr','fixture.stderr.txt')]:shutil.copyfile(src,E/f'python-demo01-dry_run-{name}')
(E/'python-demo01-dry_run-protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
summary.append(dict(language='python',case='demo01',mode='dry_run',scene=str(scene),fixture_exit=0,runtime_exit=0,inspect=inspect,protocol_counts={k:v for k,v in protocol.items() if k!='trace'},pids_absent=absent,helper_failure='Completed normal scene; initial no-reuse bind probe hit TIME_WAIT, recovered using no-listener + reuse-aware bind without rerunning runtime'))
(E/'rehearsal-summary.json').write_text(json.dumps(summary,indent=2)+'\n');assert len(summary)==8
# Freeze source and ownership audit based on coordinator baseline.
base=json.loads(Path('/private/tmp/ff-002-r1-coordinator-k8s3e9_q/baseline.json').read_text());protected=base['protected_ff_sha256']
changes=[k for k,v in protected.items() if sha(R/k)!=v];assert not changes,changes
(E/'protected-audit.json').write_text(json.dumps({'baseline':'/private/tmp/ff-002-r1-coordinator-k8s3e9_q/baseline.json','checked':len(protected),'changed':changes,'spec_sha256':sha(R/'field-flow/plans/FF-002-user-guide-and-runtime-positioning/spec.md')},indent=2)+'\n')
files=base['development_docs'];assert len(files)==16
# Real document copy and hash equality proof for this final candidate.
manifest={}
for rel in files:
 src=R/rel;dst=B/'candidate-documents'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(src)==sha(dst);manifest[rel]=sha(src)
(E/'candidate-documents.json').write_text(json.dumps({'task':'FF-002','revision':'r1','working_tree':str(R),'head':base['head'],'files':manifest,'copy_root':str(B/'candidate-documents'),'all_copy_hashes_equal':True},indent=2)+'\n')
# Bilingual code blocks/structure and scoped local links.
validation=[];fail=[]
for en in files:
 if not en.endswith('.md') or en.endswith('.zh-CN.md') or 'CODE_INDEX' in en:continue
 zh=en[:-3]+'.zh-CN.md'
 if zh not in files:continue
 x=(R/en).read_text();y=(R/zh).read_text();blocks=lambda t:re.findall(r'^```([^\n]*)\n(.*?)^```',t,re.S|re.M)
 bx=blocks(x);by=blocks(y);same=bx==by
 # README pairs do not have code; all code/commands/YAML/source are byte-equivalent.
 validation.append({'pair':[en,zh],'code_blocks':len(bx),'code_blocks_byte_equal':same,'section_counts':[len(re.findall(r'^#{1,3} ',x,re.M)),len(re.findall(r'^#{1,3} ',y,re.M))]})
 if not same:fail.append(en+' code-block divergence')
for rel in files:
 text=(R/rel).read_text();assert not any(line.rstrip()!=line for line in text.splitlines()),rel
 text=re.sub(r'^```.*?^```','',text,flags=re.M|re.S)
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  if '://' in target:continue
  part=target.split('#')[0]
  if part and not ((R/rel).parent/part).exists():fail.append(rel+': '+target)
(E/'document-checks.json').write_text(json.dumps({'pairs':validation,'local_links':'checked existing paths','whitespace':'no trailing whitespace','failures':fail},indent=2)+'\n');assert not fail,fail
# Persist actual build/preparation/failure outputs and private helpers, not SQLite/config secrets.
for name in ['rust-product-build.log','rust-fixture-build.log','python-sync.log','python-sync-cache.log','python-sync-offline.log','python-sync-network.log','rehearsal-harness.stdout','rehearsal-harness.stderr','rehearsal-harness-retry1.stdout','rehearsal-harness-retry1.stderr','rehearsal-harness-retry2.stdout','rehearsal-harness-retry2.stderr','rehearse.py','rehearse-attempt1.py','rehearse-attempt2.py','rust-wiring.py','python-wiring.py']:
 shutil.copyfile(B/name,E/name)
(E/'sources.json').write_text(json.dumps({'official_urls':['https://doc.rust-lang.org/cargo/commands/cargo-build.html','https://doc.rust-lang.org/rustc/platform-support.html'],'rust_snap7_version':'1.142.2','cargo_checksum':'8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243','native_build_source':'/Users/jason/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rust-snap7-1.142.2/build.rs','native_build_sha256':sha(Path('/Users/jason/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rust-snap7-1.142.2/build.rs'))},indent=2)+'\n')
# Final exact PID and six-port release proof.
allpids={pid for row in summary for pid in row['pids_absent']};absent={}
for pid in allpids:
 try:os.kill(int(pid),0);absent[pid]=False
 except ProcessLookupError:absent[pid]=True
assert all(absent.values());ports=[31102,31103,31880,32102,32103,32880]
p=subprocess.run(['lsof','-nP',*[f'-iTCP:{x}' for x in ports],'-sTCP:LISTEN'],capture_output=True,text=True);assert p.returncode==1 and not p.stdout
for port in ports:
 sock=socket.socket();sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);sock.bind(('127.0.0.1',port));sock.close()
(E/'resources-final.json').write_text(json.dumps({'pids_absent':absent,'six_ports_rebound':ports,'lsof_exit':p.returncode,'lsof_stdout':p.stdout,'reuseaddr_matches_python_fixture':True,'private_root':str(B),'preserve_until':'fresh QA and Human Owner final acceptance; coordinator must review ownership/handles/dependencies before cleanup','coordinator_root':'/private/tmp/ff-002-r1-coordinator-k8s3e9_q'},indent=2)+'\n')
print(json.dumps({'scenes':len(summary),'protected':len(protected),'docs':len(files),'pids':len(absent),'candidate_sha':sha(E/'candidate-documents.json'),'checks':sha(E/'document-checks.json')}))
