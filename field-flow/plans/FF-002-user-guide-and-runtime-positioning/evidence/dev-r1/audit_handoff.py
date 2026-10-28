from pathlib import Path
import json,re,hashlib,subprocess,shutil
R=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');T=R/'field-flow/plans/FF-002-user-guide-and-runtime-positioning';E=T/'evidence/dev-r1';B=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((E/'candidate-documents.json').read_text());assert all(sha(R/p)==h for p,h in manifest['files'].items())
checks=json.loads((E/'document-checks.json').read_text());anchors=[];shell=[]
for name in manifest['files']:
 s=(R/name).read_text()
 for i,code in enumerate(re.findall(r'^```bash\n(.*?)^```',s,re.S|re.M)):
  p=subprocess.run(['bash','-n'],input=code,capture_output=True,text=True);shell.append({'file':name,'block':i,'exit':p.returncode,'stderr':p.stderr});assert p.returncode==0,(name,i,p.stderr)
 plain=re.sub(r'^```.*?^```','',s,flags=re.S|re.M)
 for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',plain):
  if '://' in link or '#' not in link:continue
  file,anchor=link.split('#',1);target=(R/name).parent/file
  text=target.read_text();ok=f'id="{anchor}"' in text
  if not ok:
   for heading in re.findall(r'^#+ (.*)',text,re.M):
    h=re.sub(r'[^\w\- ]','',heading).strip().lower().replace(' ','-')
    if h==anchor:ok=True
  anchors.append({'file':name,'target':link,'exists':ok});assert ok
# Validate tasks links separately.
s=(T/'tasks.md').read_text();bad=[]
for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s):
 if '://' not in link and not (T/link.split('#')[0]).exists():bad.append(link)
assert not bad
checks['explicit_anchors']=anchors;checks['bash_parse_only']=shell;checks['tasks_links_exist']=True
(E/'document-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
# Persist actual helper used for validation, not an invented run.
for p in [B/'finalize_evidence.py',B/'preserve_failures.py',B/'audit_handoff.py']:
 shutil.copyfile(p,E/p.name)
# Narrow doc diff; changes outside 16 docs belong to coordinator/pre-existing surfaces.
p=subprocess.run(['git','diff','--check','--',*manifest['files'],'field-flow/plans/FF-002-user-guide-and-runtime-positioning/tasks.md'],cwd=R,capture_output=True,text=True);assert p.returncode==0
(E/'diff-check.txt').write_text('exit='+str(p.returncode)+'\n'+p.stdout+p.stderr)
# A non-self-referential evidence digest; manifest itself is intentionally excluded.
evidence={str(p.relative_to(T)):sha(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name not in ('evidence-manifest.json','handoff.json')}
(E/'evidence-manifest.json').write_text(json.dumps({'files':evidence},indent=2)+'\n')
handoff={'task':'FF-002','revision':'r1','status':'developer_handoff','working_tree':str(R),'head':manifest['head'],'spec_sha256':sha(T/'spec.md'),'tasks_sha256':sha(T/'tasks.md'),'candidate_documents_sha256':sha(E/'candidate-documents.json'),'evidence_manifest_sha256':sha(E/'evidence-manifest.json'),'rehearsal_summary_sha256':sha(E/'rehearsal-summary.json'),'document_checks_sha256':sha(E/'document-checks.json'),'protected_audit_sha256':sha(E/'protected-audit.json'),'resources_sha256':sha(E/'resources-final.json'),'files':list(manifest['files']),'next_gate':'fresh-context verification fork_turns=none, then Human Owner final acceptance','private_root':str(B),'coordinator_root':'/private/tmp/ff-002-r1-coordinator-k8s3e9_q','limits':['macOS arm64 only','Linux untested','Windows Unix-source blockers','UTC calendar metadata remains','failed helper attempts retained','initial uv internal fixture parent PID not separately captured; no surviving task path process','no field/DS/Backend/hosting/long-soak/distribution acceptance']}
(E/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n');print(json.dumps(handoff,indent=2));print('handoff_sha256='+sha(E/'handoff.json'))
