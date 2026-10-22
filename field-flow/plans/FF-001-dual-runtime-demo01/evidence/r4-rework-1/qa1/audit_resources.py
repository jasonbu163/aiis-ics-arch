from pathlib import Path
import hashlib,json,os,re,socket,subprocess,time
q=Path(__file__).parent
pids=set();roots={str(q)};reports={};visited=set()
def collect(value,key=''):
    if isinstance(value,dict):
        for k,v in value.items():collect(v,k)
    elif isinstance(value,list):
        for v in value:collect(v,key)
    elif isinstance(value,int) and (key=='pid' or key.endswith('_pid')) and value>1:pids.add(value)
    elif isinstance(value,str):
        if key=='run_id' and re.fullmatch(r'\d{13}-\d+-\d+',value):pids.add(int(value.split('-')[1]))
        if value.startswith('/private/tmp/ff-001-'):
            p=Path(value)
            roots.add('/private/tmp/'+p.parts[3])
            if p.is_file() and p.suffix=='.json' and str(p) not in visited:
                visited.add(str(p))
                try:
                    data=json.loads(p.read_text());reports[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();collect(data)
                except Exception:pass
for path in q.glob('*.json'):
    if path.name in ('baseline.json','inputs.json','protocol-output-index.json','python-report-summary.json'):continue
    try:collect(json.loads(path.read_text()))
    except Exception:pass
for path in q.glob('*.txt'):
    for line in path.read_text(errors='replace').splitlines():
        n=line.find('{')
        if n>=0:
            try:collect(json.loads(line[n:]))
            except Exception:pass
        for value in re.findall(r'/private/tmp/ff-001-[^\s"\'\),;]+',line):
            path=Path(value)
            if path.exists():roots.add('/private/tmp/'+path.parts[3])
results=[]
for pid in sorted(pids):
    try:os.kill(pid,0);state='still_present'
    except ProcessLookupError:state='absent'
    except PermissionError:state='permission_denied'
    results.append({'pid':pid,'state':state})
ports=[]
for port in [31102,31103,31880,32102,32103,32880]:
    argv=['lsof','-nP',f'-iTCP:{port}','-sTCP:LISTEN'];r=subprocess.run(argv,capture_output=True,text=True)
    s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:s.bind(('127.0.0.1',port));rebound=True
    except OSError as e:rebound=str(e)
    finally:s.close()
    ports.append({'port':port,'argv':argv,'lsof_exit':r.returncode,'output':r.stdout+r.stderr,'rebound':rebound})
out={'checked_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'recorded_pids':results,'ports':ports,'retained_roots':sorted(roots),'json_reports_sha256':reports,'retention':'QA owned sources/envs/state/logs/reports retained for Development rework and Owner; no directory cleanup performed','scope':'PID inventory uses only own command outputs and their report references; no process-name termination or unknown-owner cleanup'}
(q/'resources.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'pid_count':len(pids),'not_absent':[r for r in results if r['state']!='absent'],'ports':ports,'retained_roots':len(roots),'reports':len(reports)},indent=2))
