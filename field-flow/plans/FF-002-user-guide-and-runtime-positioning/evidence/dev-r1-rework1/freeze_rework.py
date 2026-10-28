from pathlib import Path
import json,hashlib,shutil,re,subprocess,difflib,os
D=Path(__file__).parent;R=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');T=R/'field-flow/plans/FF-002-user-guide-and-runtime-positioning';E=T/'evidence/dev-r1-rework1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=json.loads((E/'start-audit.json').read_text());old=json.loads((T/'evidence/dev-r1/candidate-documents.json').read_text());files=list(old['files']);changed=[p for p in files if sha(R/p)!=start['prior16'][p]]
expected={f'field-flow/field-flow-{lang}/USER_GUIDE{sf}' for lang in ('rust','python') for sf in ('.md','.zh-CN.md')};assert set(changed)==expected
patch=''
for p in changed:patch+=''.join(difflib.unified_diff((D/'before'/p).read_text().splitlines(True),(R/p).read_text().splitlines(True),fromfile='before/'+p,tofile='after/'+p))
(E/'four-guide-diff.patch').write_text(patch)
checks=[]
for lang in ('rust','python'):
 a=(R/f'field-flow/field-flow-{lang}/USER_GUIDE.md').read_text();b=(R/f'field-flow/field-flow-{lang}/USER_GUIDE.zh-CN.md').read_text();blocks=lambda x:re.findall(r'^```([^\n]*)\n(.*?)^```',x,re.M|re.S);assert blocks(a)==blocks(b)
 assert a.count('Switch back to the same Terminal B')==2;assert a.count('immediately record FF_FIXTURE_EXIT in A as in section3')==2
 assert b.count('切回第3节一直保留的终端B')==2;assert b.count('再切回保留本轮FF_PID的B')==2
 checks.append({'language':lang,'bilingual_code_blocks_byte_equal':True,'block_count':len(blocks(a)),'section3_B_ownership_labels':2,'section7_B_reuse_labels':2})
for p in files:
 text=(R/p).read_text();assert all(x==x.rstrip() for x in text.splitlines())
 for code in re.findall(r'^```bash\n(.*?)^```',text,re.M|re.S):
  proc=subprocess.run(['bash','-n'],input=code,text=True,capture_output=True);assert proc.returncode==0,(p,proc.stderr)
 plain=re.sub(r'^```.*?^```','',text,flags=re.M|re.S)
 for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',plain):
  if '://' in link:continue
  target=link.split('#')[0]
  if target:assert ((R/p).parent/target).exists(),(p,link)
checks={'pair_checks':checks,'all_16_local_link_paths_exist':True,'all_16_bash_parse_only':True,'no_trailing_whitespace':True,'changed_docs':changed,'other12_unchanged':True}
(E/'document-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
base=json.loads(Path('/private/tmp/ff-002-r1-coordinator-k8s3e9_q/baseline.json').read_text());protected={p:sha(R/p) for p in base['protected_ff_sha256']};assert protected==base['protected_ff_sha256']
old_ev=json.loads((T/'evidence/dev-r1/evidence-manifest.json').read_text())['files'];assert all(sha(T/p)==h for p,h in old_ev.items());assert sha(T/'checklist.md')==start['qa1_checklist_sha256'];assert sha(E/'tasks-before-rework1.md')==start['prior_tasks_sha256']
(E/'protected-audit.json').write_text(json.dumps({'protected581_equal':True,'protected_count':len(protected),'qa1_checklist_sha256':sha(T/'checklist.md'),'qa1_unchanged':True,'prior_dev_evidence_files_checked':len(old_ev),'prior_dev_evidence_all_equal':True,'prior_candidate_manifest_sha256':sha(T/'evidence/dev-r1/candidate-documents.json'),'old_handoff_sha256':sha(T/'evidence/dev-r1/handoff.json'),'spec_sha256':sha(T/'spec.md')},indent=2)+'\n')
manifest={}
for p in files:
 dest=D/'candidate-documents'/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/p,dest);assert sha(dest)==sha(R/p);manifest[p]=sha(R/p)
(E/'candidate-documents.json').write_text(json.dumps({'task':'FF-002','revision':'r1','development_rework':'1','working_tree':str(R),'head':old['head'],'files':manifest,'changed_from_prior':changed,'copy_root':str(D/'candidate-documents'),'all_copy_hashes_equal':True,'prior_candidate_sha256':sha(T/'evidence/dev-r1/candidate-documents.json')},indent=2)+'\n')
ports=[31102,31103,31880,32102,32103,32880];ls=subprocess.run(['/usr/sbin/lsof','-nP',*[f'-iTCP:{x}' for x in ports],'-sTCP:LISTEN'],capture_output=True);assert ls.returncode==1 and not ls.stdout and not ls.stderr
rows=json.loads((E/'two-shell-results.json').read_text());pids=[x['terminalB']['retained_FF_PID'] for x in rows];absent={}
for pid in pids:
 p=subprocess.run(['/bin/ps','-p',str(pid),'-o','pid=,stat=,command='],capture_output=True);assert p.returncode==1 and not p.stdout and not p.stderr;absent[str(pid)]=True
(E/'resources-final.json').write_text(json.dumps({'private_root':str(D),'helper_pids_absent':absent,'shell_processes_waited':8,'lsof_args':['/usr/sbin/lsof','-nP',*[f'-iTCP:{x}' for x in ports],'-sTCP:LISTEN'],'lsof_exit':ls.returncode,'lsof_stdout_hex':ls.stdout.hex(),'lsof_stderr_hex':ls.stderr.hex(),'no_product_processes_started':True,'no_ports_bound':True,'no_new_state_or_environments':True,'preserve_until':'fresh QA and Human Owner final acceptance, followed by coordinator ownership/handles/dependencies audit','older_roots_read_only':['/private/tmp/ff-002-r1-qa-E8j08DYR','/private/tmp/ff-002-r1-dev-vncfzod3','/private/tmp/ff-002-r1-coordinator-k8s3e9_q']},indent=2)+'\n')
for p in [D/'fix_guides.py',D/'check_two_shells.py',D/'freeze_rework.py']:shutil.copyfile(p,E/p.name)
print(json.dumps({'candidate_sha256':sha(E/'candidate-documents.json'),'checks_sha256':sha(E/'document-checks.json'),'protected_sha256':sha(E/'protected-audit.json'),'four_changed':len(changed),'protected':len(protected),'shell_cases':len(rows)}))
