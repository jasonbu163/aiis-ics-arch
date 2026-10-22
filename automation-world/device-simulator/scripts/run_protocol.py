#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DS产品runtime原19case编排；只用owned子进程、合成输入和三固定loopback端点。"""
import argparse
import array
import fcntl
import struct
import termios
import concurrent.futures
import ctypes
import resource
import hashlib
import json
import os
import pathlib
import queue
import random
import socket
import statistics
import subprocess
import threading
import time
import sys
sys.dont_write_bytecode = True
from run_validation import checked_inputs, source_inventory, candidate, environment, new_run, listeners
from collect_evidence import seal
OUTPUT_LOCK=threading.Lock()
CASES=['W%02d'%i for i in range(1,10)]+['C%02d'%i for i in range(1,7)]+['D01','D02','X01','X02']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(value,why):
    if not value: raise AssertionError(why)
def emit(path,value):
    with path.open('a') as f: f.write(json.dumps(value,separators=(',',':'))+'\n')
class ProcessSampler:
    """只读1Hz libproc采样：DS进程、独立clients与Python采集器分别标记。"""
    class TaskInfo(ctypes.Structure):
        _fields_=[(k,ctypes.c_uint64) for k in ['virtual','rss','user','system','threads_user','threads_system']]+[(k,ctypes.c_int32) for k in ['policy','faults','pageins','cow','messages_sent','messages_received','mach_calls','unix_calls','csw','threads','running','priority']]
    class Timebase(ctypes.Structure):
        _fields_=[('numer',ctypes.c_uint32),('denom',ctypes.c_uint32)]
    class Timespec(ctypes.Structure):
        _fields_=[('sec',ctypes.c_long),('nsec',ctypes.c_long)]
    def __init__(self,run):
        self.run=run;self.processes={};self.lock=threading.Lock();self.stop=threading.Event();self.errors=[]
        self.lib=ctypes.CDLL('/usr/lib/libproc.dylib',use_errno=True)
        self.lib.proc_pidinfo.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_uint64,ctypes.c_void_p,ctypes.c_int];self.lib.proc_pidinfo.restype=ctypes.c_int
        self.system=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
        self.system.clock_gettime.argtypes=[ctypes.c_int,ctypes.POINTER(self.Timespec)];self.system.clock_gettime.restype=ctypes.c_int
        self.system.mach_timebase_info.argtypes=[ctypes.POINTER(self.Timebase)];self.system.mach_timebase_info.restype=ctypes.c_int
        self.base=self.Timebase();require(self.system.mach_timebase_info(ctypes.byref(self.base))==0 and self.base.denom>0,'libproc CPU timebase')
        self.thread=threading.Thread(target=self.read,daemon=True)
        self.processes[os.getpid()]=('observer_sampler',None)
        own=self.sample(os.getpid(),'observer_sampler');usage=resource.getrusage(resource.RUSAGE_SELF)
        require(abs(own['cpu_seconds']-usage.ru_utime-usage.ru_stime)<.05,'libproc CPU ticks conversion')
        emit(run/'resources.jsonl',dict(own,event='observer_resource_calibration',rusage_cpu_seconds=usage.ru_utime+usage.ru_stime,task_info_bytes=ctypes.sizeof(self.TaskInfo)))
        self.thread.start()
    def sample(self,pid,role):
        value=self.TaskInfo();n=self.lib.proc_pidinfo(pid,4,0,ctypes.byref(value),ctypes.sizeof(value))
        if n!=ctypes.sizeof(value):raise OSError(ctypes.get_errno(),'proc_pidinfo TASKINFO '+str(pid))
        capacity=self.lib.proc_pidinfo(pid,1,0,None,0);require(0<=capacity<=1048576,'observer FD sample bound')
        data=ctypes.create_string_buffer(max(1,capacity));fd_bytes=self.lib.proc_pidinfo(pid,1,0,data,capacity)
        if fd_bytes<0:raise OSError(ctypes.get_errno(),'proc_pidinfo LISTFDS '+str(pid))
        clock=self.Timespec();require(self.system.clock_gettime(6,ctypes.byref(clock))==0,'observer CLOCK_MONOTONIC')
        return {'event':'external_resource_sample','pid':pid,'process_role':role,'clock_id':'darwin-clock-monotonic-ns','monotonic_ns':clock.sec*1000000000+clock.nsec,'cpu_raw_ticks':value.user+value.system,'cpu_timebase_numer':self.base.numer,'cpu_timebase_denom':self.base.denom,'cpu_seconds':(value.user+value.system)*self.base.numer/self.base.denom/1e9,'rss':value.rss,'threads':value.threads,'fd':fd_bytes//8,'mach_ports':None,'mach_ports_scope':'cross-process Mach task rights are not requested; DS/reference self-samples retain their own Mach counts','in_ds_tree':role in ['server','desktop'],'threshold_source':'DS self resources event; external client/sampler metrics separately reported','source':'SDK proc_taskinfo96B/PROC_PIDTASKINFO4; PROC_PIDLISTFDS1 actual returned8B records'}
    def register(self,process,role):
        with self.lock:self.processes[process.pid]=(role,process)
        emit(self.run/'resources.jsonl',self.sample(process.pid,role))
    def read(self):
        while not self.stop.wait(1):
            with self.lock:items=list(self.processes.items())
            for pid,(role,process) in items:
                if process and process.poll() is not None:continue
                try:emit(self.run/'resources.jsonl',self.sample(pid,role))
                except Exception as error:
                    observed=time.monotonic_ns()
                    if process is not None and isinstance(error,OSError) and error.errno==3:
                        # libproc can stop exposing TASKINFO before waitpid reports a zombie.
                        # Keep the actual ESRCH and bounded exit confirmation; a live-process failure remains an error.
                        try:
                            exit_code=process.wait(timeout=.1)
                        except subprocess.TimeoutExpired:
                            pass
                        else:
                            emit(self.run/'resources.jsonl',{'event':'resource_sample_exit_race','pid':pid,'process_role':role,'error':str(error),'observed_python_ns':observed,'exit_confirmed_python_ns':time.monotonic_ns(),'confirmation_limit_ns':100000000,'exit_code':exit_code,'sample_result':None})
                            continue
                    if process and process.poll() is not None:
                        emit(self.run/'resources.jsonl',{'event':'resource_sample_after_exit','pid':pid,'process_role':role,'error':str(error),'exit_code':process.returncode,'sample_result':None})
                        continue
                    value={'event':'resource_sample_error','pid':pid,'process_role':role,'error':str(error)};self.errors.append(value);emit(self.run/'resources.jsonl',value)
    def close(self):
        self.stop.set();self.thread.join(timeout=2)
        return not self.thread.is_alive() and not self.errors

class FileMirror:
    """产品四文件有界轮转的独立只读tail；逐行保存真实file通道，不拿stdout补造。"""
    def __init__(self,path,target,process):
        self.path,self.target,self.process=path,target,process;self.errors=[];self.rotations=0
        self.thread=threading.Thread(target=self.read,daemon=True);self.thread.start()
    def read(self):
        source=None;inode=None;pending=b'';missing_since=None
        try:
            with self.target.open('wb') as target:
                while True:
                    if source is None:
                        try:source=self.path.open('rb');inode=os.fstat(source.fileno()).st_ino
                        except FileNotFoundError:
                            if self.process.poll() is not None:raise RuntimeError('file sink never created')
                            time.sleep(.002);continue
                    chunk=source.read(65536)
                    if chunk:
                        pending+=chunk
                        end=pending.rfind(b'\n')
                        if end>=0:target.write(pending[:end+1]);pending=pending[end+1:]
                        continue
                    try:
                        current=self.path.stat().st_ino
                        missing_since=None
                    except FileNotFoundError:
                        if missing_since is None:missing_since=time.monotonic()
                        if self.process.poll() is not None or time.monotonic()-missing_since>.5:
                            raise RuntimeError('file sink missing beyond bounded rotation gap')
                        time.sleep(.002);continue
                    if current!=inode:
                        if pending:raise RuntimeError('file rotation split final JSON line')
                        source.close();source=None;self.rotations+=1;continue
                    if self.process.poll() is not None:
                        if pending:raise RuntimeError('partial final file line')
                        break
                    time.sleep(.002)
        except Exception as error:self.errors.append(str(error))
        finally:
            if source:source.close()
    def close(self):
        self.thread.join(timeout=5)
        emit(self.target.parent/'results.jsonl',{'event':'file_mirror','rotations':self.rotations,'errors':self.errors,'joined':not self.thread.is_alive()})
        return not self.thread.is_alive() and not self.errors

class Rpc:
    def __init__(self,argv,run,name,sampler=None,aliases=None):
        self.run,self.name=run,name;self.aliases=aliases or {}
        self.err=(run/'stderr.txt').open('a')
        output=(run/'stdout.txt').open('ab',buffering=0) if name=='server' else subprocess.PIPE
        self.p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=output,stderr=self.err,text=True,bufsize=1,env={k:v for k,v in os.environ.items() if k in ['PATH','LANG','LC_ALL','TMPDIR','CARGO_HOME','CARGO_TARGET_DIR','DS_TEST_RUN_ROOT']})
        if name=='server':output.close()
        if sampler:sampler.register(self.p,name)
        self.events=[];self.invalid_json=0;self.q=queue.Queue();self.lock=threading.Lock()
        emit(run/'processes.jsonl',{'event':'spawn','name':name,'pid':self.p.pid,'argv':argv,'binary_sha256':sha(pathlib.Path(argv[0])),'at':time.monotonic()})
        self.reader=threading.Thread(target=self.read,daemon=True);self.reader.start()
    def server_lines(self):
        # 子进程直接写owned普通raw文件；tail只接受完整行，进程退出后排空到EOF。
        with (self.run/'stdout.txt').open('r') as source:
            pending=''
            while True:
                part=source.readline()
                if part:
                    pending+=part
                    if pending.endswith('\n'):
                        yield pending;pending=''
                elif self.p.poll() is not None:
                    if pending:
                        self.invalid_json+=1
                        emit(self.run/'results.jsonl',{'event':'partial_final_stdout','process':self.name,'line':pending})
                    break
                else:time.sleep(.001)
    def read(self):
        output=(self.run/'stdout.txt').open('a',buffering=65536) if self.name=='reference' else None
        try:
            for line in self.server_lines() if self.name=='server' else self.p.stdout:
                if output:
                    raw=json.dumps({'process':self.name,'pid':self.p.pid,'line':line})+'\n'
                    with OUTPUT_LOCK:output.write(raw)
                try:value=json.loads(line)
                except ValueError:
                    self.invalid_json+=1;emit(self.run/'results.jsonl',{'event':'invalid_json','process':self.name,'line':line});continue
                # 同一raw中reference的原stdout包络不属于Rust事件，不重复消费。
                if self.name=='server' and value.get('process') in ['reference','managed_s7'] and 'line' in value:continue
                if self.name=='server' and value.get('instance') in self.aliases:value['instance_id']=value['instance'];value['instance']=self.aliases[value['instance']]
                value['event_index']=len(self.events)
                if self.name=='server' and 'monotonic_ns' in value:value['at']=value['monotonic_ns']/1e9
                self.events.append(value)
                if self.name=='reference':
                    emit(self.run/'wire.jsonl',dict(value,client_pid=self.p.pid));self.q.put(value)
                elif value.get('event')=='control_result':self.q.put(value)
                elif value.get('event')=='resources':emit(self.run/'resources.jsonl',value)
        finally:
            if output:
                with OUTPUT_LOCK:output.close()
    def call(self,line,timeout=8):
        with self.lock:
            started=time.monotonic();self.p.stdin.write(line+'\n');self.p.stdin.flush()
            value=self.q.get(timeout=timeout)
            emit(self.run/'commands.jsonl',{'event':'stdin_command','pid':self.p.pid,'process':self.name,'input':line,'start':started,'end':time.monotonic(),'result_ticket':value.get('ticket'),'result_ok':value.get('ok')})
            return value
    def wait_event(self,event,predicate=lambda x:True,timeout=5):
        start=time.monotonic()
        while time.monotonic()-start<timeout:
            for value in reversed(self.events):
                if value.get('event')==event and predicate(value): return value
            if self.p.poll() is not None: raise RuntimeError('process exited before '+event)
            time.sleep(.005)
        raise TimeoutError(event)
    def close(self):
        if self.p.poll() is None:
            try:
                if self.name=='server': self.p.stdin.write('quit\n');self.p.stdin.flush()
                self.p.stdin.close();self.p.wait(timeout=6)
            except (BrokenPipeError,subprocess.TimeoutExpired):
                self.p.terminate()
                try:self.p.wait(timeout=5)
                except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
        self.reader.join(timeout=5);self.err.close()
        if self.reader.is_alive():self.invalid_json+=1;emit(self.run/'results.jsonl',{'event':'stdout_drain_timeout','process':self.name})
        emit(self.run/'processes.jsonl',{'event':'exit','name':self.name,'pid':self.p.pid,'exit_code':self.p.returncode,'at':time.monotonic()})
        return self.p.returncode
class Suite:
    def __init__(self,source,root,role,case,b0_run=None):
        self.source,self.root,self.role,self.case=source,root,role,case
        self.run=new_run(root,role);self.clients=[];self.server=None;self.sampler=None;self.mirror=None;self.b0_run=b0_run
    def setup(self):
        inputs=checked_inputs(self.source)
        b0=self.b0_run
        if b0 is None:b0=pathlib.Path(json.loads((self.root/'tmp'/self.role/'latest-b0.json').read_text())['run'])
        require(b0.resolve().parent==(self.root/'runs').resolve() and b0.name.startswith(self.role+'-'),'foreign B0 run')
        build=json.loads((b0/'build-manifest.json').read_text())
        require(build['b0']=='closed' and build['role']==self.role,'role B0 not closed')
        actual_source=source_inventory(self.source)
        require(build['source']==actual_source and build['source_candidate_sha256']==candidate(actual_source),'formal source content drift')
        require(build['sourceInputsSha256']==inputs['sourceInputsSha256'],'fixed input manifest drift')
        for name,record in build['binaries'].items():require(sha(self.root/'build'/self.role/record['path'])==record['sha256'],'role binary drift '+name)
        (self.run/'source-manifest.json').write_text(json.dumps(actual_source,indent=2)+'\n')
        (self.run/'build-manifest.json').write_text(json.dumps(build,indent=2)+'\n')
        (self.run/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
        (self.run/'native.patch').write_bytes((self.source/'native/vendor/snap7-1.4.2/native.patch').read_bytes())
        self.profile=self.root/'profile'/self.role/'protocol'/self.run.name;self.profile.mkdir(parents=True,exist_ok=False)
        fixture=self.source/'tests/fixtures'/getattr(self,'workspace_name','protocol-workspace.json')
        self.aliases={i['id']:i['name'] for i in json.loads(fixture.read_text())['instances']}
        manifest={'taskId':'ARCH-AW-005','revision':'r5','role':self.role,'runId':self.run.name,'sourceCandidate':build['source_candidate_sha256'],'ownedMarker':'ARCH-AW-005-r5-owned','profileDir':str(self.profile),'workspace':str(fixture),'allowedPorts':[30102,30103,30104],'scenario':None}
        path=self.profile/'manifest.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
        (self.run/'fixture-manifest.json').write_text(json.dumps({'workspace':str(fixture),'sha256':sha(fixture),'manifestSha256':sha(path)},indent=2)+'\n')
        self.sampler=ProcessSampler(self.run)
        self.native=self.root/'build'/self.role/'native'
        self.server=Rpc([str(self.root/'build'/self.role/build['binaries']['test_host']['path']),'--ds-test-manifest',str(path)],self.run,'server',self.sampler,self.aliases)
        self.mirror=FileMirror(self.profile/'events.jsonl',self.run/'events.jsonl',self.server.p)
        self.server.wait_event('ready_stopped',timeout=15)
        calibration=[]
        for k in range(20):
            before=time.monotonic_ns();r=self.ctrl('ping A calibration-%d'%k);after=time.monotonic_ns();native=r['clock_ns'];calibration.append({'python_before_ns':before,'rust_ns':native,'python_after_ns':after,'offset_low_ns':native-after,'offset_high_ns':native-before})
        (self.run/'clock-calibration.json').write_text(json.dumps({'clock_id':'darwin-clock-monotonic-ns','python_origin':'independent','samples':calibration,'offset_intersection_ns':[max(x['offset_low_ns'] for x in calibration),min(x['offset_high_ns'] for x in calibration)]},indent=2)+'\n')
        time.sleep(1.1)
        self.b0=self.server.events[-1]
    def wait_native(self,target):
        while self.ctrl('ping A wait')['clock_ns']<target:time.sleep(.01)
    def start(self):
        for instance in ['A','B']:require(self.ctrl('start '+instance)['ok'],'start failed '+instance)
    def ctrl(self,text): return self.server.call(text)
    def client(self,instance='A',slot=None,connect=True):
        c=Rpc([str(self.native/'ds-s7-reference'),'--run-root',str(self.run)],self.run,'reference',self.sampler);self.clients.append(c)
        if connect:
            result=c.call('0 connect %d %d'%(30102 if instance=='A' else 30103,slot or (1 if instance=='A' else 2)))
            require(result['ok'],'reference connect failed')
            accepted=self.server.wait_event('accepted',lambda e:e.get('instance')==instance and e.get('peer_port')==result['local_port'])
            c.connection_id=accepted['connection']
            self.server.wait_event('established',lambda e:e.get('instance')==instance and e.get('connection')==c.connection_id)
        return c
    def snap(self,step,instance='A'):
        s=self.ctrl('snapshot '+instance);data=bytes.fromhex(s['image'])+bytes.fromhex(s['marker'])
        images=self.run/'images';images.mkdir(exist_ok=True)
        p=images/('%s-%s-%s-%s.bin'%(self.case,step,instance,s['epoch']));p.write_bytes(data)
        s['sha256']=hashlib.sha256(data).hexdigest();s['db_sha256']={'41':hashlib.sha256(data[:1024]).hexdigest(),'57':hashlib.sha256(data[1024:]).hexdigest()};s['step']=step
        emit(self.run/'results.jsonl',{'event':'snapshot','case':self.case,**s});return s
    def read(self,c,start,size,db=41):return c.call('0 read %d %d %d'%(db,start,size))
    def write(self,c,start,data,db=41):return c.call('0 write %d %d %s'%(db,start,data.hex()))
    def denied(self,c,start,data,step,db=41):
        before=self.snap(step+'-before');r=self.write(c,start,data,db);after=self.snap(step+'-after')
        require(r['codes'] and all(x!=255 for x in r['codes']),'missing real item error '+step)
        require(before['sha256']==after['sha256'] and before['seq']==after['seq'] and before['points']==after['points'],'rejected mutation '+step)
    def silent(self):
        require(self.ctrl('pause A')['ok'],'pause')
        time.sleep(.02)
    def point_seq(self,s,byte,bit=0):return next(p['last_seq'] for p in s['points'] if p['bit_address']==byte*8+bit)
    def w01(self):
        c=self.client();self.silent();before=self.snap('before')
        data=bytes.fromhex('01020304fffffffe');r=self.write(c,512,data);after=self.snap('after')
        require(r['codes']==[255] and after['seq']==before['seq']+1,'single write/seq')
        require(self.read(c,512,8)['payload']==data.hex(),'raw readback')
        require(self.read(c,0,64,57)['payload'][:16]=='4453473041303031','marker A')
        native=c.call('0 native 30102');require(native['ok'] and native['rx'][:16]=='4453473041303031','upstream native C client')
    def w02(self):
        c=self.client();self.silent()
        for i,(start,data,db) in enumerate([(48,b'\0'*4,41),(400,b'\0'*4,41),(100,b'\0',41),(0,b'\0',57),(0,b'\0',99)]):self.denied(c,start,data,str(i),db)
        self.ctrl('overlay A 1');self.denied(c,56,b'\0'*4,'unconfirmed');self.ctrl('overlay A 0')
    def w03(self):
        a=self.client();b=self.client();self.silent()
        require(a.call('0 bit 41 0 01')['codes']==[255],'bit0')
        require(int(self.read(a,0,1)['payload'],16)&3==3,'neighbor rule bit')
        self.denied(a,0,b'\3','whole-byte')
        for k in range(100):
            require(self.write(a,1,b'\0')['codes']==[255],'zero byte1')
            barrier=threading.Barrier(2)
            def bit(c,n):barrier.wait();return c.call('0 bit 41 %d 01'%n)
            with concurrent.futures.ThreadPoolExecutor(2) as pool:
                f=pool.submit(bit,a,8);g=pool.submit(bit,b,9)
                require(f.result()['codes']==[255] and g.result()['codes']==[255],'race item')
            require(self.read(a,1,1)['payload']=='03','lost bit update')
        require(self.write(a,1,b'\xff')['codes']==[255],'all-client byte')
    def w04(self):
        c=self.client();self.silent()
        for i,(start,data) in enumerate([(2,b'\1'),(4,b'\0'*2),(638,b'\0'*4),(1023,b'\0'*2),(4,bytes.fromhex('7fc00000')),(4,bytes.fromhex('7f800000'))]):self.denied(c,start,data,str(i))
        require(self.write(c,2,bytes.fromhex('fffe'))['codes']==[255],'signed INT')
        require(self.write(c,4,bytes.fromhex('3fc00000'))['codes']==[255],'finite REAL')
        template=bytes.fromhex(self.write(c,512,b'\0'*8)['tx'])
        vectors=[]
        zero=bytearray(template);zero[23:25]=b'\0\0';vectors.append(zero)
        overflow=bytearray(template);overflow[23:25]=b'\xff\xff';vectors.append(overflow)
        short=bytearray(template[:-1]);short[2:4]=len(short).to_bytes(2,'big');short[15:17]=(11).to_bytes(2,'big');vectors.append(short)
        unit=bytearray(template);unit[32]=3;vectors.append(unit)
        fractional=bytearray(template);fractional[33:35]=(65).to_bytes(2,"big");vectors.append(fractional)
        vectors.append(bytes.fromhex('0300020102f080')+b'\0'*506)
        read_template=bytes.fromhex(self.read(c,0,154)['tx']);item=read_template[19:31]
        too_large_response=bytearray(read_template[:17])+bytes([4,3])+item*3
        too_large_response[13:15]=(38).to_bytes(2,'big');too_large_response[2:4]=len(too_large_response).to_bytes(2,'big')
        vectors.append(too_large_response)  # response=495 frame bytes, S7 PDU=488 exceeds negotiated480
        for i,data in enumerate(vectors):
            c=self.client();before=self.snap('raw%d-before'%i);r=c.call('0 raw '+bytes(data).hex());after=self.snap('raw%d-after'%i)
            require(not r['rx'] or not r['codes'] or all(x!=255 for x in r['codes']),'malformed succeeded')
            require(before['sha256']==after['sha256'] and before['seq']==after['seq'],'malformed mutation')
    def w05(self):
        c=self.client();self.silent()
        for start,n in [(64,8),(128,254)]:
            data=bytes([n,3])+b'ABC'+b'\0'*(n-3)
            require(self.write(c,start,data)['codes']==[255] and self.read(c,start,n+2)['payload']==data.hex(),'STRING legal')
            vectors=[bytes([n-1])+data[1:],bytes([n,n+1])+data[2:],data[:2]+b'\x80'+data[3:],data[:2],data[:-1]]
            for i,v in enumerate(vectors):self.denied(c,start,v,'%d-%d'%(n,i))
    def w06(self):
        c=self.client();self.silent();before=self.snap('before')
        r=c.call('0 multi 41 512 0102030405060708 41 400 00000000 41 64 08034142430000000000')
        after=self.snap('after');require(len(r['codes'])==3 and r['codes'][0]==255 and r['codes'][1]!=255 and r['codes'][2]==255,'real mixed item results')
        require(after['seq']==before['seq']+2,'multi-item commits')
    def w07(self):
        c=self.client();self.silent();s=self.snap('initial');epoch,rev=s['epoch'],s['revision']
        def source(src,start,data,cas=0,e=None,r=None):return self.ctrl('write A %d %d -1 %s %d %d %d'%(src,start,data.hex(),epoch if e is None else e,rev if r is None else r,cas))
        require(source(2,48,b'\0\0\0\5')['ok'],'UI owner')
        require(not source(2,48,b'\0'*4,0)['ok'],'UI stale CAS')
        require(not source(2,56,b'\0'*4)['ok'],'UI ownership')
        require(not source(3,56,b'\0'*4)['ok'],'maintenance default off')
        require(not source(1,400,b'\0'*4)['ok'],'paused rule')
        self.ctrl('resume A');require(source(1,400,b'\0\0\0\7')['ok'],'rule legal source');require(not source(1,56,b'\0'*4)['ok'],'rule/hold')
        require(not source(1,400,b'\0'*4,e=epoch-1)['ok'],'old epoch')
        for src in [4,5]:require(not source(src,2,b'\0'*2)['ok'],'init/reset running')
        require(self.ctrl('stop A')['ok'],'stop for maintenance')
        require(source(4,2,b'\0'*2)['ok'],'stopped initialize source')
        require(not source(5,2,b'\0'*2)['ok'],'raw per-point reset forbidden')
        require(self.ctrl('reset A')['ok'],'whole-image stopped reset source');epoch=self.snap('reset-source')['epoch']
        require(self.ctrl('maintenance A 1')['ok'],'enable stopped maintenance')
        maintenance_snapshot=self.snap('maintenance-config');rev=maintenance_snapshot['revision'];epoch=maintenance_snapshot['epoch'];require(self.ctrl('start A')['ok'],'restart');self.silent()
        s=self.snap('before-maint');cas=self.point_seq(s,56)
        require(source(3,56,b'\0\0\0\7',cas)['ok'],'maintenance legal')
        require(not source(3,56,b'\0\0\0\8',cas)['ok'],'maintenance CAS stale')
        require(not source(3,424,b'\0'*4)['ok'],'maintenance paused rule forbidden')
        c=self.client();self.denied(c,400,b'\0'*4,'client-rule');require(self.write(c,56,b'\0\0\0\11')['codes']==[255],'client overwrites maintenance')
        self.ctrl('stop A');self.ctrl('start A');self.silent();c=self.client();require(self.read(c,56,4)['payload']=='00000009','stop/start preserve')
        self.ctrl('stop A');require(self.ctrl('reset A')['ok'],'explicit reset');s=self.snap('reset');require(s['epoch']==epoch+1 and bytes.fromhex(s['image'])[56:60]==b'\0'*4,'reset initializes')
    def w08(self):
        self.silent();before=self.snap('before');clock_before={'wall':time.time(),'monotonic':time.monotonic()}
        for fn in [0x28,0x29,0x1a,0x1b,0x1d,0x1e,0x00,0x7f]:
            c=self.client();raw=bytes.fromhex('0300001302f08032010000000100020000')+bytes([fn,0]);r=c.call('0 raw '+raw.hex());require(not r['rx'] or all(x!=255 for x in r['codes']),'system request accepted')
        c=self.client();r=c.call('0 raw 0300001f02f080320100000001000e00000401120a10020001000083000000');require(not r['codes'] or r['codes']!=[255],'nonDB')
        after=self.snap('after');clock_after={'wall':time.time(),'monotonic':time.monotonic()};emit(self.run/'results.jsonl',{'event':'host_clock_observation','before':clock_before,'after':clock_after});require(before['sha256']==after['sha256'] and before['seq']==after['seq'] and after['running'],'system side effect')
    def w09(self):
        self.silent()
        for phase,action,commits in [(1,'close',0),(2,'stop',1),(3,'close',1),(1,'timeout',0)]:
            c=self.client();cid=c.connection_id;before=self.snap('%d-%s-before'%(phase,action));self.ctrl('barrier A '+str(phase))
            with concurrent.futures.ThreadPoolExecutor(1) as pool:
                f=pool.submit(self.write,c,512,b'\0\0\0\1\0\0\0\2');self.server.wait_event('barrier',lambda e:e.get('connection')==cid and e.get('phase')==phase)
                if action=='close':self.ctrl('close A '+str(cid))
                elif action=='stop':self.ctrl('stop A')
                else:time.sleep(2.15)
                result=f.result();emit(self.run/'results.jsonl',{'event':'ack_observation','phase':phase,'action':action,'result':result,'meaning':'unknown if committed and response absent; never auto-retried'})
            self.ctrl('release A');after=self.snap('%d-%s-after'%(phase,action));require(after['seq']==before['seq']+commits,'barrier commit count')
            if not commits:require(before['sha256']==after['sha256'],'precommit canceled mutation')
            if action=='stop':self.ctrl('start A');self.silent()
    def profile_round(self,c,slot,round):
        resource=c.call('0 resources');emit(self.run/'resources.jsonl',dict(resource,process='reference',at=time.monotonic()))
        r=self.read(c,0,64,57);data=round.to_bytes(4,'big')+slot.to_bytes(4,'big');w=self.write(c,512+slot*8,data)
        require(r['codes']==[255] and r['payload'][:16]=='4453473041303031' and w['codes']==[255],'profile offered request failed')
        return [r['ms'],w['ms']]
    def c01(self):
        clients=[self.client() for _ in range(16)];latencies=[[] for _ in clients]
        start=time.monotonic();measurement=None
        for round in range(330):
            if round==30:
                measurement=self.ctrl('measurement_begin A C01');begin_ns=measurement['begin_ns'];end_ns=begin_ns+300_000_000_000
                self.wait_native(begin_ns);start=time.monotonic()-30
            with concurrent.futures.ThreadPoolExecutor(16) as pool:
                futures=[pool.submit(self.profile_round,c,i,round) for i,c in enumerate(clients)]
                for i,f in enumerate(futures):
                    value=f.result()
                    if round>=30:latencies[i]+=value
            time.sleep(max(0,start+round+1-time.monotonic()))
        self.wait_native(end_ns);self.ctrl('measurement_end A C01')
        time.sleep(1.05)
        stats=[]
        for i,values in enumerate(latencies):
            ordered=sorted(values);s={'connection':i,'offered':600,'completed':len(values),'p50':ordered[299],'p95':ordered[569],'p99':ordered[593],'max':max(values)};stats.append(s);require(len(values)==600 and s['p95']<=100 and s['p99']<=250,'per-connection latency')
        emit(self.run/'results.jsonl',{'event':'C01_metrics','requests':sum(len(x) for x in latencies),'payload_bytes':345600,'connections':stats,'measurement_start_ns':begin_ns,'measurement_end_ns':end_ns,'logical_phase':'C01','duration_ns':end_ns-begin_ns})
        samples=[x for x in self.server.events if x.get('event')=='resources' and begin_ns<=x['monotonic_ns']<=end_ns]
        require(len(samples)>=298,'resource sample gap')
        require(max(x['rss'] for x in samples)<=512*1024*1024 and samples[-1]['rss']-samples[0]['rss']<=16*1024*1024,'RSS threshold')
        require(max(x['threads'] for x in samples)<=64 and max(x['fd']+x['mach_ports'] for x in samples)<=1024,'thread/handles')
        require((samples[-1]['cpu_seconds']-samples[0]['cpu_seconds'])/(samples[-1]['at']-samples[0]['at'])<=1,'CPU one-core budget')
        rules=[x for x in self.server.events if x.get('event')=='rule_cycle' and x.get('instance')=='A' and begin_ns<=x['monotonic_ns']<end_ns]
        require(sum(x['due'] for x in rules)==24000 and sum(x['missed'] for x in rules)<=240,'rule due/missed')
        waits=[e['wait_ms'] for e in self.server.events if e.get('event')=='dispatch' and begin_ns<=e['monotonic_ns']<=end_ns]
        require(sorted(waits)[int(len(waits)*.99)-1]<=100,'queue p99')
        self.c02(clients)
        emit(self.run/'results.jsonl',{'case':'C02','status':'pass','scope':'same sixteen C01 sessions remain active for extra-connection rejection and replacement'})
    def c02(self,clients=None):
        clients=clients or [self.client() for _ in range(16)]
        for k in range(20):
            for i,c in enumerate(clients):self.profile_round(c,i,k)
            extra=self.client(connect=False);require(not extra.call('0 connect 30102 1')['ok'],'17th accepted');extra.close();time.sleep(.1)
        clients[0].call('0 close');time.sleep(.1);replacement=self.client();self.profile_round(replacement,0,99)
        sid=[x['connection'] for x in self.server.events if x.get('event')=='accepted' and x.get('instance')=='A'][-1]
        self.ctrl('close A '+str(sid));self.ctrl('close A '+str(sid));time.sleep(.1)
        require(self.ctrl('snapshot A')['c']==15,'duplicate close count')
    def c03(self):
        clients=[self.client() for _ in range(16)]
        for trial in range(3):
            pending=[];accepted=time.monotonic()
            for _ in range(4):pending.append(socket.create_connection(('127.0.0.1',30102),timeout=1))
            time.sleep(.1);hs=self.ctrl('snapshot A');require(hs['h']==4,'H4');handshakes=[c for c in hs['connections'] if c['phase']=='handshaking']
            for _ in range(20):
                try:s=socket.create_connection(('127.0.0.1',30102),timeout=.05);s.close()
                except (OSError,socket.timeout):pass
            for c in clients:self.read(c,0,64,57)
            time.sleep(max(0,accepted+5.5-time.monotonic()));require(self.ctrl('snapshot A')['h']==0,'handshake absolute cleanup')
            for c in handshakes:
                joins=[e for e in self.server.events if e.get('event')=='pthread_join_return_release' and e.get('instance')=='A' and e.get('connection')==c['connection']]
                require(joins and joins[0]['at']-c['accepted_ns']/1e9<=5.5,'handshake measured deadline')
            for s in pending:s.close()
        for trial in range(3):
            s=socket.create_connection(('127.0.0.1',30102),timeout=1);s.settimeout(.5);start=time.monotonic();peer_port=s.getsockname()[1];event_mark=len(self.server.events);accepted_event=self.server.wait_event('accepted',lambda e:e.get('instance')=='A' and e.get('peer_port')==peer_port);start=time.monotonic();event_mark=len(self.server.events)
            for byte in b'\3\0\0\x16\x11\xe0':
                try:s.send(bytes([byte]))
                except OSError:break
                time.sleep(.5)
            time.sleep(max(0,start+2.5-time.monotonic()));s.close();require(self.ctrl('snapshot A')['h']==0,'partial frame absolute cleanup');joins=[e for e in self.server.events if e.get('event')=='pthread_join_return_release' and e.get('instance')=='A' and e.get('connection')==accepted_event['connection']];first=[e for e in self.server.events[event_mark:] if e.get('event')=='io' and e.get('instance')=='A' and e.get('connection')==accepted_event['connection'] and e.get('op')==0];require(joins and first and joins[0]['monotonic_ns']-first[0]['started_ns']<=2_500_000_000,'partial first-byte measured deadline')
        time.sleep(30);require(self.read(clients[0],0,64,57)['codes']==[255],'idle session wrongly removed')
    def c04(self):
        self.silent();c=self.client();template=bytes.fromhex(self.write(c,512,b'\0'*8)['tx']);before=self.snap('inflight-before')
        result=c.call('0 raw '+(template+template).hex());after=self.snap('inflight-after');require(not result['rx'] and before['sha256']==after['sha256'] and before['seq']==after['seq'],'inflight admission before item0')
        for name,limits in [('connection',(1,1048576,4194304)),('instance',(65536,1,4194304)),('global',(65536,1048576,1))]:
            c=self.client();self.ctrl('budget A '+' '.join(map(str,limits)));before=self.snap(name+'-before');r=self.write(c,512,b'\1'*8);after=self.snap(name+'-after');require(not r['rx'] and before['sha256']==after['sha256'] and before['seq']==after['seq'],'whole reservation '+name);self.ctrl('budget A 65536 1048576 4194304');c=self.client();require(self.write(c,512,b'\0'*8)['codes']==[255],'reservation restoration')
        # A raw slow peer remains a client, never a protocol server. C++ supplies the exact raw read vector.
        c=self.client();valid=bytes.fromhex(self.read(c,128,256)['tx']);c.call('0 close')
        slow=socket.socket();slow.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192);slow.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,8192);slow.settimeout(1);slow.setsockopt(socket.IPPROTO_TCP,0x08,1);slow.setsockopt(socket.IPPROTO_TCP,socket.TCP_MAXSEG,256);buffers={'rcvbuf':slow.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF),'sndbuf':slow.getsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF)};require(max(buffers.values())<=16384,'slow peer buffer bound');slow.connect(('127.0.0.1',30102))
        # Darwin loopback connect覆盖pre-connect buffer；连接完成后重新设置并逐阶段读回。
        slow.setsockopt(socket.IPPROTO_TCP,socket.TCP_MAXSEG,256)
        slow.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192);slow.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,8192)
        def peer_state(phase,sent):
            pending=array.array('i',[0]);fcntl.ioctl(slow.fileno(),termios.FIONREAD,pending,True)
            info=slow.getsockopt(socket.IPPROTO_TCP,0x106,104) # SDK TCP_CONNECTION_INFO
            state={'event':'slow_peer_socket_state','phase':phase,'sent':sent,'observer_monotonic':time.monotonic(),'rcvbuf':slow.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF),'sndbuf':slow.getsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF),'unread_bytes':pending[0],'tcp_info_raw':info.hex(),'tcp_noopt_requested':True,'tcp_noopt_readback':slow.getsockopt(socket.IPPROTO_TCP,0x08),'tcp_info_rcv_wscale':info[2],'tcp_info_options':struct.unpack_from('=I',info,4)[0],'tcp_maxseg_requested':256,'tcp_info_maxseg':struct.unpack_from('=I',info,16)[0],'tcp_info_rcv_wnd':struct.unpack_from('=I',info,36)[0],'tcp_info_snd_sbbytes':struct.unpack_from('=I',info,32)[0]}
            emit(self.run/'results.jsonl',state);require(max(state['rcvbuf'],state['sndbuf'])<=16384,'slow peer actual post-connect buffer bound');require(state['tcp_noopt_readback'] and state['tcp_info_rcv_wscale']==0 and state['tcp_info_rcv_wnd']<=65535,'slow peer bounded advertised window');return state
        peer_state('connected_before_protocol',0)
        # Handshake uses the same frozen finite client vectors, then does not consume read responses.
        slow.sendall(bytes.fromhex('0300001611e00000000100c0010ac1020100c2020101'));head=slow.recv(4);n=int.from_bytes(head[2:4],'big');body=b''
        while len(body)<n-4:body+=slow.recv(n-4-len(body))
        slow.sendall(bytes.fromhex('0300001902f08032010000000100080000f0000001000101e0'));head=slow.recv(4);n=int.from_bytes(head[2:4],'big');body=b''
        while len(body)<n-4:body+=slow.recv(n-4-len(body))
        peer_state('handshake_complete',0)
        require(self.ctrl('resume A')['ok'],'resume rules for slow peer isolation');healthy=self.client()
        begin=time.monotonic();event_mark=len(self.server.events);sent=0
        for index in range(600):
            time.sleep(max(0,begin+index*.05-time.monotonic()))
            if time.monotonic()-begin>=30:break
            try:slow.sendall(valid);sent+=1
            except OSError as error:
                emit(self.run/'results.jsonl',{'event':'slow_peer_send_stopped','sent':sent,'elapsed':time.monotonic()-begin,'error':str(error)});break
            if index%20==0:
                peer_state('no_response_consumption',sent)
                result=self.read(healthy,0,64,57);require(result['codes']==[255],'other connection stalled behind slow peer')
                emit(self.run/'results.jsonl',{'event':'slow_peer_other_connection','sent':sent,'connection':healthy.connection_id,'response':result})
        emit(self.run/'results.jsonl',{'event':'slow_peer_offered','sent':sent,'offered_target':600,'period_seconds':.05,'max_window_seconds':30,'elapsed':time.monotonic()-begin,'received_by_application_after_handshake':0})
        time.sleep(2.6);peer_state('before_close',sent);slow.close()
        blocked=[e for e in self.server.events[event_mark:] if e.get('event')=='io' and e.get('instance')=='A' and e.get('op')==3]
        require(blocked,'no actual send block observed; send deadline unproved')
        for e in blocked:
            closes=[x for x in self.server.events if x.get('event')=='pthread_join_return_release' and x.get('connection')==e['connection'] and x['at']>=e['at']]
            require(closes and closes[0]['monotonic_ns']-e['started_ns']<=2_500_000_000,'send absolute deadline')
            joined=closes[0]['monotonic_ns']
            require(any(x.get('event')=='io' and x.get('instance')=='A' and x.get('connection')==healthy.connection_id and x.get('op')==2 and e['monotonic_ns']<=x['monotonic_ns']<=joined for x in self.server.events),'no other-connection response during actual send block')
            require(any(x.get('event')=='rule_cycle' and x.get('instance')=='A' and e['monotonic_ns']<=x['monotonic_ns']<=joined for x in self.server.events),'rules stalled during actual send block')
        emit(self.run/'results.jsonl',{'event':'slow_peer','sent':sent,'buffers_actual':buffers,'blocked':len(blocked)})
    def c05(self):
        self.ctrl('stop A');self.ctrl('maintenance A 1');self.ctrl('start A')
        flood=self.client();a=self.client();b=self.client();idle=[self.client() for _ in range(13)]
        start=time.monotonic();errors=[];low_latencies={'A':[],'B':[]};counts={'F_completed':0,'F_rejected':0,'A':0,'B':0,'UI':0}
        # 4x64B reads occupy one PDU; clone a native client-generated one-item descriptor as finite test data.
        template=bytes.fromhex(self.read(flood,512,64)['tx'])
        # Correct base raw S7 parameter offsets explicitly; C++ independently decodes all item results.
        item=template[19:31];pdu=bytearray(template[:17])+bytes([4,4])+item*4;pdu[13:15]=(50).to_bytes(2,'big');pdu[2:4]=len(pdu).to_bytes(2,'big')
        def high():
            for i in range(1200):
                r=flood.call('0 raw '+pdu.hex());counts['F_completed' if r['codes']==[255]*4 else 'F_rejected']+=1;time.sleep(max(0,start+(i+1)*.05-time.monotonic()))
        def low(c,key,slot):
            for i in range(60):low_latencies[key].extend(self.profile_round(c,slot,i));counts[key]+=2;time.sleep(max(0,start+i+1-time.monotonic()))
        def ui():
            for i in range(60):
                s=self.ctrl('snapshot A');cas=self.point_seq(s,56);r=self.ctrl('write A 3 56 -1 %s %d %d %d'%((i+1).to_bytes(4,'big').hex(),s['epoch'],s['revision'],cas));require(r['ok'],'UI maintenance starved');counts['UI']+=1;time.sleep(max(0,start+i+1-time.monotonic()))
        with concurrent.futures.ThreadPoolExecutor(4) as pool:
            futures=[pool.submit(high),pool.submit(low,a,'A',0),pool.submit(low,b,'B',1),pool.submit(ui)]
            for f in futures:f.result()
        require(counts['A']==120 and counts['B']==120 and counts['UI']==60,'offered low/UI completion')
        require(counts['F_completed']>0,'flood all rejected')
        for key,values in low_latencies.items():
            require(len(values)==120 and sorted(values)[118]<=250,'C05 low p99 '+key)
        emit(self.run/'results.jsonl',{'event':'C05_low_latency','values_ms':low_latencies})
        emit(self.run/'results.jsonl',{'event':'C05_metrics','counts':counts,'start':start,'end':time.monotonic()})
        fault_clients=[flood,a,b]+idle
        for trial in range(3):
            if trial:
                for c in fault_clients:require(c.call('0 connect 30102 1')['ok'],'fault reconnect')
            self.silent();self.ctrl('budget A 32768 400000 800000');self.ctrl('barrier A 1');before=self.snap('backlog%d-before'%trial);t=time.monotonic();event_mark=len(self.server.events)
            with concurrent.futures.ThreadPoolExecutor(16) as pool:
                futures=[pool.submit(self.write,c,512+i*8,b'\0'*8) for i,c in enumerate(fault_clients)]
                self.server.wait_event('barrier',lambda e:e.get('event_index',-1)>=event_mark);time.sleep(.05);backlog=self.snap('backlog%d-admitted'%trial);require(backlog['protocol_waiting']>=1,'no actual admitted backlog')
                t=time.monotonic();require(self.ctrl('stop A')['ok'] and time.monotonic()-t<=5,'fault stop')
                for f in futures:f.result()
            after=self.snap('backlog%d-after'%trial);require(before['sha256']==after['sha256'] and before['seq']==after['seq'],'queued stop committed')
            self.ctrl('release A');self.ctrl('budget A 65536 1048576 4194304');self.ctrl('start A');time.sleep(5);require(self.ctrl('snapshot A')['reserved_bytes']==0,'recovery queue')
    def c06(self):
        clients=[self.client() for _ in range(16)];rng=random.Random(5003)
        for round in range(10):
            delays=[rng.uniform(.1,1) for _ in clients]
            def reconnect(i):
                clients[i].call('0 '+['close','half','error'][(round+i)%3]);time.sleep(delays[i]);require(clients[i].call('0 connect 30102 1')['ok'],'reconnect');self.profile_round(clients[i],i,round)
            with concurrent.futures.ThreadPoolExecutor(16) as pool:list(pool.map(reconnect,range(16)))
        self.ctrl('stop A');self.ctrl('stop B');time.sleep(10)
        stamp=self.ctrl('ping A stopped-baseline')['clock_ns'];baseline=self.server.wait_event('resources',lambda e:e.get('monotonic_ns',0)>=stamp);samples=[]
        for cycle in range(20):
            require(self.ctrl('start A')['ok'],'cycle start')
            for i,c in enumerate(clients):require(c.call('0 connect 30102 1')['ok'],'cycle connect');self.profile_round(c,i,cycle)
            t=time.monotonic();require(self.ctrl('stop A')['ok'] and time.monotonic()-t<=2,'normal stop deadline');time.sleep(10)
            s=self.ctrl('snapshot A');require(s['c']==s['h']==s['tcp']==s['reserved_bytes']==0,'stopped transport resources')
            sample=[e for e in self.server.events if e.get('event')=='resources'][-1];samples.append(sample)
            require(sample['threads']==baseline['threads'] and sample['fd']==baseline['fd'] and sample['mach_ports']<=baseline['mach_ports']+1,'thread/handle baseline')
            require(sample['rss']<=baseline['rss']+16*1024*1024,'stopped RSS')
            emit(self.run/'results.jsonl',{'event':'cycle','cycle':cycle,'snapshot':s,'resource':sample,'baseline':baseline})
        values=[x['rss'] for x in samples];require(statistics.median(values[-5:])-statistics.median(values[:5])<=8*1024*1024,'RSS median growth')
        groups=[statistics.median(values[i:i+5]) for i in range(0,20,5)];require(not(all(groups[i]<groups[i+1] for i in range(3)) and groups[-1]-groups[0]>8*1024*1024),'four-group RSS growth')
        for _ in range(3):require(self.ctrl('reset A')['ok'],'reset stopped')
    def managed_client(self,argv,timeout):
        p=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={k:v for k,v in os.environ.items() if k in ['PATH','LANG','LC_ALL','TMPDIR','CARGO_HOME','CARGO_TARGET_DIR','DS_TEST_RUN_ROOT']})
        self.sampler.register(p,'managed_s7')
        emit(self.run/'processes.jsonl',{'event':'spawn','name':'managed_s7','pid':p.pid,'argv':argv,'binary_sha256':sha(pathlib.Path(argv[0]))})
        timed_out=False
        try:out,err=p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.terminate()
            try:out,err=p.communicate(timeout=5)
            except subprocess.TimeoutExpired:p.kill();out,err=p.communicate()
            timed_out=True
        finally:emit(self.run/'processes.jsonl',{'event':'exit','name':'managed_s7','pid':p.pid,'exit_code':p.returncode})
        with OUTPUT_LOCK:
            with (self.run/'stdout.txt').open('a') as raw:
                for line in out.splitlines(True):raw.write(json.dumps({'process':'managed_s7','pid':p.pid,'line':line})+'\n')
        with (self.run/'stderr.txt').open('a') as raw:raw.write(err)
        if timed_out:raise RuntimeError('owned ManagedS7 timeout; interrupted experiment')
        return subprocess.CompletedProcess(argv,p.returncode,out,err)
    def d01(self):
        ref=self.client();require(self.write(ref,512,b'\1\2\3\4\5\6\7\10')['codes']==[255],'change hold before DAA')
        binary=self.root/'build'/self.role/'daa/release/ds-s7-daa-client';start=time.monotonic()
        p=self.managed_client([str(binary),'--run-root',str(self.run)],70)
        records=[json.loads(line) for line in p.stdout.splitlines()];require(p.returncode==0,'real DAA process failed')
        for r in records:emit(self.run/'results.jsonl',r)
        read_records=[r for r in records if r.get('event')=='read_complete']
        require(len(read_records)==240,'DAA offered reads')
        for r in read_records:
            if r['db']==57:require(bytes(r['bytes'][:8])==(b'DSG0A001' if r['instance']==0 else b'DSG0B001'),'DAA marker')
            elif r['instance']==0:require(bytes(r['bytes'])==b'\1\2\3\4\5\6\7\10','DAA changed hold')
        emit(self.run/'commands.jsonl',{'argv':[str(binary),'--run-root',str(self.run)],'exit_code':p.returncode,'duration':time.monotonic()-start,'binary_sha256':sha(binary)})
    def d02(self):
        binary=self.root/'build'/self.role/'daa/release/ds-s7-daa-client';argv=[str(binary),'--run-root',str(self.run),'--case','D02']
        p=self.managed_client(argv,30)
        emit(self.run/'commands.jsonl',{'argv':argv,'exit_code':p.returncode,'binary_sha256':sha(binary)})
        records=[json.loads(line) for line in p.stdout.splitlines()]
        for r in records:emit(self.run/'results.jsonl',r)
        require(p.returncode==0 and len(records)==12 and all(r['rejected'] for r in records),'real ManagedS7 negative connections')
        for port,slot in [(30102,2),(30103,1),(30104,1)]:
            for _ in range(3):c=self.client(connect=False);require(not c.call('0 connect %d %d'%(port,slot))['ok'],'wrong endpoint identity accepted')
        require(self.ctrl('stop A')['ok'],'stop A before conflict')
        stopped=self.ctrl('snapshot A');require(stopped['c']==stopped['h']==stopped['tcp']==0 and not stopped['running'],'A not actually stopped before conflict')
        argv=['/usr/sbin/lsof','-nP','-iTCP:30102','-sTCP:LISTEN'];os_state=subprocess.run(argv,capture_output=True,text=True,timeout=3)
        emit(self.run/'commands.jsonl',{'argv':argv,'exit_code':os_state.returncode,'stdout':os_state.stdout,'stderr':os_state.stderr})
        require(os_state.returncode==1 and not os_state.stdout and not os_state.stderr,'residual/foreign LISTEN before owned conflict; never killed or replaced')
        argv=['/usr/sbin/netstat','-anv','-p','tcp'];state=subprocess.run(argv,capture_output=True,text=True,timeout=3)
        emit(self.run/'commands.jsonl',{'argv':argv,'exit_code':state.returncode,'stdout_fixed_endpoint_only':'\n'.join(line for line in state.stdout.splitlines() if '127.0.0.1.30102 ' in line),'stderr':state.stderr,'read_scope':'OS metadata filtered to approved endpoint; other records not retained'})
        owned=socket.socket();owned.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        require(owned.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT)==0,'conflict fixture must not share live port')
        owned.bind(('127.0.0.1',30102));owned.listen(1)
        emit(self.run/'results.jsonl',{'event':'owned_conflict_listener','observer_pid':os.getpid(),'port':30102,'reuseaddr':owned.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR),'reuseport':owned.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT),'scope':'sequential TIME_WAIT rebind only; no concurrent listener sharing'})
        try:
            for _ in range(2):require(not self.ctrl('start A')['ok'],'duplicate listener started')
            c=self.client('B');require(self.read(c,0,64,57)['payload'][:16]=='4453473042303031','B affected by A conflict')
        finally:owned.close()
        self.ctrl('stop A');require(self.ctrl('start A')['ok'],'A recovery after conflict')
    def x01(self):
        a=self.client();b=self.client('B');self.silent();cid=a.connection_id
        stop=threading.Event();reads=[]
        def continuous_b():
            for index in range(300):
                if stop.is_set():return
                result=self.read(b,0,64,57)
                require(result['codes']==[255] and result['payload'][:16]=='4453473042303031','B disrupted during A barriers/stop')
                reads.append(result)
                emit(self.run/'results.jsonl',{'event':'X01_B_continuous_read','index':index,'connection':b.connection_id,'client_pid':b.p.pid,'response':result})
                if stop.wait(.1):return
            raise AssertionError('bounded B observer expired before A scenario ended')
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            future=pool.submit(continuous_b)
            try:
                self.ctrl('close A '+str(cid));self.w09()
                self.ctrl('stop A');self.ctrl('start A');c=self.client();require(self.read(c,0,64,57)['payload'][:16]=='4453473041303031','rebind')
            finally:stop.set();future.result()
        require(len(reads)>=2,'B continuous read evidence missing')
        emit(self.run/'results.jsonl',{'event':'X01_B_progress','read_count':len(reads),'cadence_seconds':.1,'max_reads':300,'connection':b.connection_id,'client_pid':b.p.pid})
    def x02(self):
        return {'status':'not_applicable','reason':'Single Rust process with in-process native protocol, A/B unique Rust owners, no sidecar/child model. Native hard crash can affect both; common stop/cleanup remains tested elsewhere.'}
    def finish(self):
        for c in self.clients:c.close()
        clean=True
        for instance in ['A','B'] if self.server else []:
            try:clean=self.ctrl('stop '+instance)['ok'] and clean
            except Exception:clean=False
        code=self.server.close() if self.server else 0
        mirror_complete=self.mirror.close() if self.mirror else self.server is None
        sampler_complete=self.sampler.close() if self.sampler else True
        listeners=[]
        for port in [30102,30103,30104]:
            s=socket.socket();s.settimeout(.15)
            try:rc=s.connect_ex(('127.0.0.1',port))
            finally:s.close()
            if rc==0:listeners.append(port)
        raw_events=[];evidence_error=None
        try:raw_events=[json.loads(line) for line in (self.run/'events.jsonl').read_text().splitlines()] if self.server else []
        except Exception as e:evidence_error=str(e)
        degraded=[e for e in raw_events if e.get('event') in ['evidence_lost','observability_degraded']]
        evidence_complete=(not evidence_error and not degraded and mirror_complete and all(c.invalid_json==0 for c in self.clients) and (self.server is None or (len(raw_events)==len(self.server.events) and self.server.invalid_json==0)))
        cleanup={'clean':clean and code==0 and not listeners,'server_exit':code,'listeners':listeners,'owned_only':True,'evidence_complete':evidence_complete and sampler_complete,'sampler_complete':sampler_complete,'stdout_server_events':len(self.server.events) if self.server else 0,'file_server_events':len(raw_events),'evidence_error':evidence_error,'degraded':degraded}
        cleanup['file_mirror_complete']=mirror_complete
        for path in self.profile.glob('device-simulator-v1/config.sqlite') if hasattr(self,'profile') else []:
            import shutil
            shutil.copyfile(path,self.run/'configuration-after.sqlite')
        (self.run/'cleanup.json').write_text(json.dumps(cleanup,indent=2)+'\n');return cleanup

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=pathlib.Path);p.add_argument('--run-root',type=pathlib.Path);p.add_argument('--role',choices=['dev','qa']);p.add_argument('--case',choices=CASES);p.add_argument('--b0-run',type=pathlib.Path)
    a=p.parse_args()
    if not all((a.project_root,a.run_root,a.role,a.case)):p.print_help();return 0
    require(a.run_root.resolve()==pathlib.Path('/private/tmp/arch-aw-005-r5-exec'),'explicit approved run root')
    checked_inputs(a.project_root.resolve())
    suite=Suite(a.project_root.resolve(),a.run_root.resolve(),a.role,a.case,a.b0_run)
    result={'case':a.case,'status':'blocked','reason':'setup not completed'};started=time.monotonic()
    try:
        require(not any(listeners(suite.run,(30102,30103,30104)).values()),'fixed port conflict; no foreign process killed')
        suite.setup();suite.start();extra=getattr(suite,a.case.lower())()
        result={'case':a.case,'status':'pass','duration':time.monotonic()-started,**(extra or {})}
    except Exception as e:result={'case':a.case,'status':'fail' if suite.server else 'blocked','error':type(e).__name__+': '+str(e),'duration':time.monotonic()-started}
    finally:
        cleanup=suite.finish()
        if not cleanup['clean']:result['status']='fail';result['cleanup_failed']=True
        elif not cleanup['evidence_complete']:result['status']='blocked';result['evidence_incomplete']=True
        emit(suite.run/'results.jsonl',result);(suite.run/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
        emit(suite.run/'commands.jsonl',{'argv':list(os.sys.argv),'exit_code':0 if result['status'] in ['pass','not_applicable'] else 1,'start':started,'end':time.monotonic()})
        result['run']=str(suite.run)
    print(json.dumps(result));return 0 if result['status'] in ['pass','not_applicable'] else 1
if __name__=='__main__':raise SystemExit(main())
