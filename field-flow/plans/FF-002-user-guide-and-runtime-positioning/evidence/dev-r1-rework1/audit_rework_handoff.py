from pathlib import Path
import hashlib,json,subprocess,re,shutil
D=Path(__file__).parent;R=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');T=R/'field-flow/plans/FF-002-user-guide-and-runtime-positioning';E=T/'evidence/dev-r1-rework1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((E/'candidate-documents.json').read_text());assert all(sha(R/p)==h for p,h in m['files'].items());assert sha(T/'checklist.md')=='bb3d6eb203e21e6bbfa4081684b566fd723daa073f2d21c9fd1024786d1b976e'
for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(T/'tasks.md').read_text()):
 if '://' not in link:assert (T/link.split('#')[0]).exists(),link
p=subprocess.run(['git','diff','--check','--',*m['files'],'field-flow/plans/FF-002-user-guide-and-runtime-positioning/tasks.md'],cwd=R,capture_output=True,text=True);assert p.returncode==0;pout='exit=0\n'+p.stdout+p.stderr;(E/'diff-check.txt').write_text(pout)
shutil.copyfile(D/'audit_rework_handoff.py',E/'audit_rework_handoff.py')
ev={str(p.relative_to(T)):sha(p) for p in sorted(E.iterdir()) if p.is_file() and p.name not in ('evidence-manifest.json','handoff.json')};(E/'evidence-manifest.json').write_text(json.dumps({'files':ev},indent=2)+'\n')
h={'task':'FF-002','revision':'r1','rework':'1','status':'developer_handoff','working_tree':str(R),'head':m['head'],'spec_sha256':sha(T/'spec.md'),'qa1_checklist_sha256':sha(T/'checklist.md'),'tasks_sha256':sha(T/'tasks.md'),'candidate_documents_sha256':sha(E/'candidate-documents.json'),'evidence_manifest_sha256':sha(E/'evidence-manifest.json'),'changed_docs':m['changed_from_prior'],'protected_audit_sha256':sha(E/'protected-audit.json'),'two_shell_results_sha256':sha(E/'two-shell-results.json'),'resources_sha256':sha(E/'resources-final.json'),'prior_handoff_sha256':sha(T/'evidence/dev-r1/handoff.json'),'private_root':str(D),'next_gate':'new actual verification fork_turns=none; must independently close F-QA1-001 and complete full required product rehearsal; no verdict granted'}
(E/'handoff.json').write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(h,indent=2));print('handoff_sha256='+sha(E/'handoff.json'))
