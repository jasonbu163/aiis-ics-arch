from pathlib import Path
import subprocess,os,re,json,time,shutil,hashlib
D=Path(__file__).parent;R=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');T=R/'field-flow/plans/FF-002-user-guide-and-runtime-positioning';E=T/'evidence/dev-r1-rework1'
env={k:v for k,v in os.environ.items() if k not in ('FF_PID','FF_PROJECT','FF_LESSON','FF_BIN','FF_FIXTURE_EXIT')};rows=[]
for lang in ('rust','python'):
 text=(R/f'field-flow/field-flow-{lang}/USER_GUIDE.md').read_text();blocks=re.findall(r'^```bash\n(.*?)^```',text,re.M|re.S)
 a_code=next(x for x in blocks if x.startswith('FF_FIXTURE_EXIT=$?'))
 for mode in ('dry','execute'):
  case=D/f'{lang}-{mode}';case.mkdir();lesson=case/'lesson';scene=lesson/f'{mode}-lesson';(scene/'fixture').mkdir(parents=True)
  src=T/f'evidence/dev-r1/{lang}-demo01-{"dry_run" if mode=="dry" else "execute"}'
  report='protocol.json' if lang=='rust' else 'report.json'
  shutil.copyfile(Path(str(src)+'-protocol.json'),scene/'fixture'/report);shutil.copyfile(Path(str(src)+'-runtime.stderr.txt'),scene/'stderr.txt')
  b_check=next(x for x in blocks if x.startswith(f'cat "$FF_LESSON/{mode}-lesson/fixture/'))
  # B persists between run/wait and post-A inspection; A is an independently created shell.
  b_pre='''read -r FF_PROJECT
read -r FF_LESSON
cd "$FF_PROJECT"
sleep 0 &
FF_PID=$!
wait "$FF_PID"
FF_EXIT=$?
printf "B runtime PID=%s exit=%s\\n" "$FF_PID" "$FF_EXIT"
printf "B ready\\n"
read -r FF_CHECK_READY
'''
  b_tail='''
FF_PS_EXIT=$?
printf "B ps exit=%s\\n" "$FF_PS_EXIT"
[[ "$FF_PID" == <1-> && "$FF_PS_EXIT" == 1 ]] || exit 10
[[ ! -v FF_FIXTURE_EXIT ]] || exit 11
printf "B fixture variable remains unset\\n"
'''
  (case/'terminal-B-script.zsh').write_text(b_pre+b_check+b_tail)
  out=(case/'B.stdout').open('wb');err=(case/'B.stderr').open('wb')
  b=subprocess.Popen(['/bin/zsh','-f'],stdin=subprocess.PIPE,stdout=out,stderr=err,cwd=D,env=env,text=True)
  # Supply only explicit path input; no process variables shared with A.
  b.stdin.write('read -r FF_PROJECT\n'+str(R)+ '\nread -r FF_LESSON\n'+str(lesson)+'\n'+b_pre[b_pre.index('cd "$FF_PROJECT"'):]);b.stdin.flush()
  end=time.monotonic()+3
  while 'B ready' not in (case/'B.stdout').read_text():
   assert b.poll() is None;assert time.monotonic()<end;time.sleep(.01)
  a_script='''[[ ! -v FF_PID ]] || exit 12
sleep 0
'''+a_code+'''\n[[ "$FF_FIXTURE_EXIT" == 0 && ! -v FF_PID ]] || exit 13
printf "A runtime variable remains unset\\n"
'''
  (case/'terminal-A-script.zsh').write_text(a_script)
  a=subprocess.run(['/bin/zsh','-f','-c',a_script],cwd=R,env=env,capture_output=True)
  (case/'A.stdout').write_bytes(a.stdout);(case/'A.stderr').write_bytes(a.stderr);assert a.returncode==0,(a.returncode,a.stderr)
  b.stdin.write('continue\n'+b_check+b_tail);b.stdin.close();b.wait(timeout=5);out.close();err.close()
  stdout=(case/'B.stdout').read_text();stderr=(case/'B.stderr').read_bytes();assert b.returncode==0,(b.returncode,stderr,stdout);assert stderr==b'',stderr
  pid=int(re.search(r'B runtime PID=(\d+)',stdout).group(1));assert f'checking runtime PID={pid}' in stdout
  ps=subprocess.run(['/bin/ps','-p',str(pid),'-o','pid=,stat=,command='],capture_output=True);assert ps.returncode==1 and not ps.stdout and not ps.stderr
  row={'language':lang,'mode':mode,'terminalA':{'argv':['/bin/zsh','-f','-c',a_script],'cwd':str(R),'exit':a.returncode,'stdout':a.stdout.decode(),'stderr_hex':a.stderr.hex(),'FF_PID':'unset'},'terminalB':{'argv':['/bin/zsh','-f'],'cwd_at_check':str(R),'script':b_pre+b_check+b_tail,'path_inputs':[str(R),str(lesson)],'exit':b.returncode,'stdout':stdout,'stderr_hex':stderr.hex(),'retained_FF_PID':pid,'FF_FIXTURE_EXIT':'unset'},'pid_recheck':{'pid':pid,'exit':ps.returncode,'stdout_hex':ps.stdout.hex(),'stderr_hex':ps.stderr.hex()},'scope':'short-lived sleep0 helper only, not a product/fixture run; copied DEV real report is input for literal cat checks'}
  rows.append(row);(E/'two-shell-results.json').write_text(json.dumps(rows,indent=2)+'\n')
  for name in ['terminal-A-script.zsh','terminal-B-script.zsh','A.stdout','A.stderr','B.stdout','B.stderr']:shutil.copyfile(case/name,E/(f'{lang}-{mode}-'+name))
print(json.dumps({'cases':len(rows),'independent_shells':8,'all_exit0':all(x['terminalA']['exit']==x['terminalB']['exit']==0 for x in rows),'four_helper_PIDs_absent':True,'no_product_services_started':True}))
