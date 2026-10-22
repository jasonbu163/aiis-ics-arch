"""QA-only subprocess ledger; source code is never changed."""
from pathlib import Path
import hashlib, json, os, signal, subprocess, sys, time
Q=Path(__file__).parent
ROOT=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch')
mode=sys.argv[1]
is_copy=mode.endswith('copy')
lang=mode.split('-')[0]
project='field-flow-'+lang
cwd=Q/'isolated'/lang/'project' if is_copy else ROOT/'field-flow'/project
env=os.environ.copy()
for key in ('PYTHONPATH','VIRTUAL_ENV','CONDA_PREFIX'):
    env.pop(key,None)
env.update(UV_CACHE_DIR=str(Q/'uv-cache'),PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(Q/(mode+'-pycache')),CARGO_TARGET_DIR=str(Q/(mode+'-target')))
if lang=='python':env['UV_PROJECT_ENVIRONMENT']=str(Q/(mode+'-venv'))
uv=['uv','run','--offline','--locked','--python','3.11','--no-python-downloads']
if lang=='python':
    checks=[('lock',['uv','lock','--check','--offline','--python','3.11','--no-python-downloads'],60),('sync',['uv','sync','--offline','--locked','--python','3.11','--no-python-downloads'],120),('build',['uv','build','--offline','--python','3.11','--no-python-downloads','--out-dir',str(Q/(mode+'-dist'))],120),('compile',uv+['python','-m','compileall','-q','src','tests'],60),('unit',uv+['pytest','-p','no:cacheprovider','-q','tests/unit','-s'],60),('gate',uv+['pytest','-p','no:cacheprovider','-q','tests/test_matched_ack_gate.py','-s'],120),('protocol',uv+['pytest','-p','no:cacheprovider','-q','tests/test_local_protocol.py','-s'],180),('bare',uv+['field-flow'],30),('cli',uv+['python','-m','tests.fixtures.cli_smoke'],90),('provenance',uv+['python','-c','import sys,field_flow,tests.fixtures,sqlite3,snap7; import importlib.metadata as m,json; print(json.dumps(dict(executable=sys.executable,source=field_flow.__file__,fixture=tests.fixtures.__file__,python=sys.version,sqlite=sqlite3.sqlite_version,snap7=m.version("python-snap7"))))'],30)]
else:
    checks=[('fmt',['cargo','fmt','--check'],60),('check',['cargo','check','--locked','--offline','--all-targets','--features','test-fixture'],600),('build',['cargo','build','--locked','--offline','--bins','--features','test-fixture'],600),('unit',['cargo','test','--locked','--offline','--test','s7_int_pdu','--','--test-threads=1','--nocapture'],120),('gate',['cargo','test','--locked','--offline','--features','test-fixture','--test','local_protocol','matched_ack_preflight','--','--test-threads=1','--nocapture'],120),('protocol',['cargo','test','--locked','--offline','--features','test-fixture','--','--test-threads=1','--nocapture'],240),('bare',['cargo','run','--locked','--offline','--bin','field-flow','--'],30)]
if len(sys.argv)>2: checks=[x for x in checks if x[0] in sys.argv[2].split(',')]
records=[]
for label,argv,timeout in checks:
    path=Q/(mode+'-'+label+'.txt'); start=time.monotonic()
    with path.open('w') as out:
        p=subprocess.Popen(argv,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=p.wait(timeout=timeout); timed_out=False
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(p.pid,signal.SIGTERM)
            try:code=p.wait(timeout=1)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);code=p.wait(timeout=2)
    record=dict(label=label,argv=argv,cwd=str(cwd),env={k:env[k] for k in ('UV_CACHE_DIR','UV_PROJECT_ENVIRONMENT','PYTHONPYCACHEPREFIX','CARGO_TARGET_DIR') if k in env},pid=p.pid,exit_code=code,timed_out=timed_out,duration_seconds=time.monotonic()-start,output=str(path),output_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    records.append(record);(Q/(mode+'-commands.json')).write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(record),flush=True)
    if code!=0:
        print(path.read_text()[-10000:],flush=True)
        sys.exit(1)
