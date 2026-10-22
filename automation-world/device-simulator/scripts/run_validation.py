#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r5正式角色验证编排；显式输入、隔离cache/profile，裸入口只显示帮助。"""
import argparse
import datetime
import ctypes
import json
import os
import pathlib
import signal
import sqlite3
import subprocess
import time
import uuid
from collect_evidence import RUN_ROOT, digest

SPEC_SHA = '67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419'
PORTS = (30102, 30103, 30104, 15194, 14194)


def new_run(root, role):
    numbers = [int(path.name.split('-')[1]) for path in (root / 'runs').glob(role + '-[0-9][0-9][0-9][0-9]')]
    run = root / 'runs' / ('%s-%04d' % (role, max(numbers, default=0) + 1))
    run.mkdir(parents=True, exist_ok=False)
    return run


def source_inventory(project):
    result = {}
    excluded = {'node_modules', 'target', 'dist', 'gen', '__pycache__', '.git', 'g0'}
    for directory, dirs, files in os.walk(project):
        dirs[:] = [name for name in dirs if name not in excluded]
        for name in sorted(files):
            path = pathlib.Path(directory) / name
            if name.endswith('.md') or name == 'source-inputs.json':
                continue
            if path.is_symlink():
                raise RuntimeError('formal source symlink: ' + str(path))
            result[str(path.relative_to(project))] = digest(path)
    return dict(sorted(result.items()))


def candidate(source):
    import hashlib
    return hashlib.sha256(''.join(name + '\t' + source[name] + '\n' for name in sorted(source)).encode()).hexdigest()


def checked_inputs(project):
    repo = project.parents[1]
    spec = repo / 'plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md'
    if digest(spec) != SPEC_SHA:
        raise RuntimeError('approved spec drift')
    source = json.loads((project / 'source-inputs.json').read_text())
    checked = {}
    for group in ('daaDerivationPins', 'r4FrozenInputs'):
        for relative, expected in source[group].items():
            path = repo / relative
            if path.is_symlink() or digest(path) != expected:
                raise RuntimeError('frozen input drift: ' + relative)
            checked[relative] = expected
    return {'specSha256': SPEC_SHA, 'sourceInputsSha256': digest(project / 'source-inputs.json'),
            'frozenMembers': checked}


def environment(root, role, surface):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('DS_G0_', 'DS_TEST_'))}
    tool = '/Users/jason/.rustup/toolchains/stable-aarch64-apple-darwin/bin'
    env.update(CARGO_HOME=str(root / 'cache' / role / 'cargo-home'),
               CARGO_TARGET_DIR=str(root / 'build' / role / surface),
               TMPDIR=str(root / 'tmp' / role), RUSTC=tool + '/rustc', RUSTDOC=tool + '/rustdoc',
               CARGO_NET_OFFLINE='true', CARGO_BUILD_JOBS='2',
               pnpm_config_store_dir=str(root / 'cache' / role / 'pnpm-store'),
               pnpm_config_offline='true', pnpm_config_manage_package_manager_versions='false',
               pnpm_config_update_notifier='false', pnpm_config_verify_deps_before_run='error',
               pnpm_config_enable_global_virtual_store='false',
               PATH=tool + ':/Users/jason/.nvm/versions/node/v22.19.0/bin:/Users/jason/Library/pnpm/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin')
    return env


def execute(run, argv, cwd=None, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    with (run / 'commands.jsonl').open('a') as out:
        out.write(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              'argv': argv, 'cwd': str(cwd), 'exitCode': result.returncode,
                              'stdout': result.stdout, 'stderr': result.stderr}) + '\n')
    return result


def listeners(run, ports=PORTS):
    result = {}
    for port in ports:
        check = execute(run, ['/usr/sbin/lsof', '-nP', '-iTCP:' + str(port), '-sTCP:LISTEN'])
        if check.returncode not in (0, 1):
            raise RuntimeError('listener inspection failed: ' + check.stderr)
        result[str(port)] = check.stdout
    return result


def descendants(run, pid):
    found = []
    pending = [pid]
    while pending:
        parent = pending.pop()
        result = execute(run, ['/usr/bin/pgrep', '-P', str(parent)])
        if result.returncode not in (0, 1):
            raise RuntimeError('owned descendant inspection failed')
        children = [int(value) for value in result.stdout.split()]
        found.extend(children)
        pending.extend(children)
    return found


def records(path):
    if not path.exists():
        return []
    lines = path.read_text(errors='replace').splitlines()
    result = []
    for line in lines:
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # 未完成的最后一行只在下一次poll读取，不用于pass。
    return result


def normal_dev(project, root, role, run):
    descendants(run, os.getpid())  # 权限缺口在启动任何子进程前明确失败。
    before = listeners(run)
    if any(before.values()):
        raise RuntimeError('fixed port conflict; no process was killed')
    profile = root / 'profile' / role / 'normal' / run.name
    profile.mkdir(parents=True, exist_ok=False)
    env = environment(root, role, 'desktop')
    env['DS_PROFILE_DIR'] = str(profile)
    argv = ['pnpm', 'tauri', 'dev']
    seen = set()
    status = {'suite': 'ordinary-pnpm-tauri-dev', 'argv': argv, 'profile': str(profile),
              'normalWindowCloseProof': False, 'portsBefore': before, 'result': 'running'}
    (run / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
    with (run / 'stdout.txt').open('wb') as stdout, (run / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(argv, cwd=project, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        status['launcherPid'] = process.pid
        (run / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
        deadline = time.monotonic() + 900
        try:
            while time.monotonic() < deadline:
                seen.update(descendants(run, process.pid))
                events = records(profile / 'events.jsonl')
                responses = {event.get('command') for event in events if event.get('phase') == 'response' and event.get('result') == 'ok'}
                # 各IPC的实际字段采用真实事件命令名，不从“窗口已启动”推定成功。
                commands = {event.get('command', event.get('name')) for event in events if event.get('phase') == 'response'}
                status['observedCommands'] = sorted(str(value) for value in commands)
                ready = any(event.get('event') == 'profile_open' for event in events)
                if ready and {'ds_get_bootstrap', 'ds_get_configuration', 'ds_get_runtime_snapshot'} <= responses:
                    status['result'] = 'pass'
                    break
                if process.poll() is not None:
                    raise RuntimeError('ordinary dev exited before real bootstrap/configuration/snapshot IPC')
                time.sleep(1)
            else:
                raise RuntimeError('ordinary dev bootstrap deadline exceeded')
            try:
                seen.update(descendants(run, process.pid))
            except RuntimeError as error:
                status['processInspectionError'] = str(error)
                status['result'] = 'fail'
            for pid in sorted(seen):
                execute(run, ['/bin/ps', '-p', str(pid), '-o', 'pid=,ppid=,command='])
            events = records(profile / 'events.jsonl')
            opened = next(event for event in events if event.get('event') == 'profile_open')
            store = uuid.UUID(opened['webviewStoreId'])
            if store.int == 0:
                raise RuntimeError('default WebKit store is forbidden for owned smoke')
            status['webviewStoreId'] = str(store)
            status['realIpcEvents'] = [event for event in events if event.get('phase') == 'response']
            db = profile / 'device-simulator-v1/config.sqlite'
            connection = sqlite3.connect('file:' + str(db) + '?mode=ro', uri=True)
            status['sqlite'] = {'applicationId': connection.execute('PRAGMA application_id').fetchone()[0],
                                'userVersion': connection.execute('PRAGMA user_version').fetchone()[0],
                                'tables': connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()}
            connection.close()
            if status['sqlite']['applicationId'] != 0x44535631 or status['sqlite']['userVersion'] != 1:
                raise RuntimeError('normal DS SQLite identity mismatch')
            status['portsDuring'] = listeners(run)
            if any(status['portsDuring'][str(port)] for port in (30102, 30103, 30104)):
                raise RuntimeError('empty normal profile started S7 unexpectedly')
            binary = root / 'build' / role / 'desktop/debug/aiis-device-simulator'
            status['binary'] = {'path': str(binary), 'sha256': digest(binary)}
            execute(run, ['/usr/bin/otool', '-L', str(binary)])
            execute(run, ['/usr/sbin/lsof', '-nP', '-p', ','.join(map(str, sorted(seen))), '-F', 'pn'])
        except BaseException as error:
            status['result'] = 'fail'
            status['error'] = str(error)
        finally:
            # 普通dev watcher的实验收尾；绝不记为正常Window.close或N场景通过。
            try:
                seen.update(descendants(run, process.pid))
            except RuntimeError as error:
                status['processInspectionError'] = str(error)
                status['result'] = 'fail'
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=5)
            status['launcherExitCode'] = process.returncode
            status['ownedPids'] = sorted(seen)
            status['portsAfter'] = listeners(run)
            status['cleanupMethod'] = 'owned watcher process group SIGINT; not normal window close'
            status['remainingPids'] = []
            for pid in sorted(seen | {process.pid}):
                check = execute(run, ['/bin/ps', '-p', str(pid), '-o', 'pid=,ppid=,command='])
                if check.returncode == 0 and check.stdout.strip():
                    status['remainingPids'].append({'pid': pid, 'observed': check.stdout})
            if status['remainingPids'] or any(status['portsAfter'].values()):
                status['result'] = 'fail'
                status['cleanupIncomplete'] = True
            (run / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps(status))
    return 0 if status['result'] == 'pass' else 1


def core(project, root, role, run):
    env = environment(root, role, 'runtime')
    env['DS_TEST_RUN_ROOT'] = str(root / 'profile' / role / 'normal' / run.name)
    results = []
    for argv in [['cargo', 'fmt', '--manifest-path', str(project / 'runtime/Cargo.toml'), '--check'],
                 ['cargo', 'test', '--offline', '--locked', '--manifest-path', str(project / 'runtime/Cargo.toml'), '--features', 'native-s7,test-automation', '--lib', '--tests']]:
        result = execute(run, argv, project, env)
        results.append({'argv': argv, 'exitCode': result.returncode})
        if result.returncode:
            break
    if results and all(r['exitCode'] == 0 for r in results):
        try: profile_lock_processes(project, root, role, run, env)
        except Exception as error: results.append({'phase':'real_cross_process_profile_lock','exitCode':1,'error':str(error)})
    status = {'suite': 'core', 'commands': results, 'result': 'pass' if all(r['exitCode'] == 0 for r in results) else 'fail', 'networkListenersStarted': False}
    (run / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps(status))
    return 0 if status['result'] == 'pass' else 1


class Timespec(ctypes.Structure):
    _fields_ = [('seconds', ctypes.c_long), ('nanoseconds', ctypes.c_long)]


def monotonic_ns():
    library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    library.clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(Timespec)]
    value = Timespec()
    if library.clock_gettime(6, ctypes.byref(value)):
        raise OSError(ctypes.get_errno(), 'CLOCK_MONOTONIC6')
    return value.seconds * 1000000000 + value.nanoseconds


def webkit_metadata(run, store_id, identity):
    # 仅已知应用/进程名下的本profile UUID；不枚举其它应用或读取偏好内容。
    result = []
    for name in [identity, 'aiis-device-simulator']:
        path = pathlib.Path('/Users/jason/Library/WebKit') / name / 'WebsiteDataStore' / store_id.lower()
        row = {'path': str(path), 'exists': path.exists(), 'metadataOnly': True}
        if path.exists():
            stat = path.stat()
            row.update(uid=stat.st_uid, birthtime=stat.st_birthtime, mtimeNs=stat.st_mtime_ns)
            execute(run, ['/usr/sbin/lsof', '-nP', '+D', str(path)])
        result.append(row)
    return result


class WebKitStoreResources:
    """实际POSIX descendants与精确owned store关联；逐PID去重，未知费用不记零。"""
    def __init__(self, run, sampler, desktop_process):
        self.run, self.sampler = run, sampler
        self.desktop_process, self.desktop_pid = desktop_process, desktop_process.pid
        self.store_id = None
        self.next = 0
        self.pids = {}
        self.errors = []
        self.paths = []
        self.webview_probes = []
        self.terminal_observations = []
        self.exited_pids = set()
        self.after_close_checks = []

    def observe(self, events, phase='running', force=False, child_pids=()):
        opened = next((e for e in events if e.get('event') == 'profile_open'), None)
        if opened is None:
            return
        if self.store_id is None:
            self.store_id = str(uuid.UUID(opened['webviewStoreId']))
            self.paths = [pathlib.Path('/Users/jason/Library/WebKit') / name / 'WebsiteDataStore' / self.store_id
                          for name in ['com.aiis.aw.devicesimulator.validation', 'aiis-device-simulator']]
        now = time.monotonic()
        if not force and now < self.next:
            return
        self.next = now + 1
        actual_children = set(child_pids) - {self.desktop_pid}
        store_pids = set()
        # Only fixed PID observations from this actual owned WKWebView; no process-name scan.
        probe_pids = set()
        probes = [event for event in events if event.get('event') == 'native_webview_processes']
        if probes:
            probe = probes[-1]
            if not self.webview_probes or self.webview_probes[-1].get('monotonic_ns') != probe.get('monotonic_ns'):
                self.webview_probes.append(probe)
            if phase == 'running':
                for key in ['webProcessId', 'gpuProcessId']:
                    pid = probe.get(key)
                    if isinstance(pid, int) and 0 < pid < 2147483647:
                        probe_pids.add(pid)
        for path in self.paths:
            if not path.exists():
                continue
            argv = ['/usr/sbin/lsof', '-nP', '-Fpcn', '+D', str(path)]
            try:
                result = subprocess.run(argv, capture_output=True, text=True, timeout=.75)
                record = {'event': 'owned_webkit_store_handles', 'phase': phase, 'clockNs': monotonic_ns(),
                          'storeId': self.store_id, 'path': str(path), 'argv': argv, 'exitCode': result.returncode,
                          'stdout': result.stdout, 'stderr': result.stderr, 'readScope': 'exact owned store directory metadata only'}
                store_pids.update(int(line[1:]) for line in result.stdout.splitlines()
                                  if line.startswith('p') and line[1:].isdigit())
                if result.returncode not in (0, 1) or result.stderr:
                    self.errors.append(record)
            except subprocess.TimeoutExpired as error:
                record = {'event': 'owned_webkit_store_lookup_timeout', 'phase': phase, 'clockNs': monotonic_ns(),
                          'path': str(path), 'argv': argv, 'timeoutSeconds': .75, 'stdout': str(error.stdout), 'stderr': str(error.stderr)}
                self.errors.append(record)
            with (self.run / 'webkit-resource-association.jsonl').open('a') as output:
                output.write(json.dumps(record) + '\n')
        # 同一观察周期只对union中的PID采一次；不能把child与XPC两张表的费用相加。
        for pid in sorted((actual_children | store_pids | probe_pids) - {self.desktop_pid} - self.exited_pids):
            origins = (['actual_posix_descendant'] if pid in actual_children else []) + (['owned_store_open_file'] if pid in store_pids else []) + (['current_wkwebview_fixed_pid_getter'] if pid in probe_pids else [])
            stamp = monotonic_ns()
            if pid not in self.pids:
                if len(self.pids) >= 64:
                    self.errors.append({'event': 'association_pid_cap', 'pid': pid})
                    continue
                argv = ['/bin/ps', '-p', str(pid), '-o', 'pid=,ppid=,lstart=,comm=']
                try:
                    ps = subprocess.run(argv, capture_output=True, text=True, timeout=.5)
                    self.pids[pid] = {'pid': pid, 'firstClockNs': stamp, 'psArgv': argv, 'psExit': ps.returncode,
                                      'ps': ps.stdout, 'origins': {}, 'resourceSamples': 0, 'unavailableSamples': 0, 'killAuthorized': False}
                except subprocess.TimeoutExpired:
                    self.errors.append({'event': 'associated_pid_metadata_timeout', 'pid': pid, 'timeoutSeconds': .5})
                    continue
            item = self.pids[pid]
            item['lastAssociatedClockNs'] = stamp
            for origin in origins:
                if origin not in item['origins']:
                    item['origins'][origin] = {'firstClockNs': stamp, 'lastClockNs': stamp}
                item['origins'][origin]['lastClockNs'] = stamp
            role = 'desktop_posix_child' if pid in actual_children else ('webkit_view_pid' if pid in probe_pids else 'webkit_store_handle')
            try:
                sample = self.sampler.sample(pid, role)
                sample.update(event='attributed_native_tree_resource_sample', phase=phase, storeId=self.store_id,
                              attributionOrigins=origins, in_ds_tree=pid in actual_children,
                              resourceScope='GUI tree separately reported; shared store XPC may not be exclusively owned; no headless C01 threshold assigned',
                              deduplication='one sample per PID in this 1Hz union observation')
                item['resourceSamples'] += 1
                item['lastSampleClockNs'] = sample['monotonic_ns']
                with (self.run / 'webkit-resources.jsonl').open('a') as output:
                    output.write(json.dumps(sample) + '\n')
            except OSError as error:
                item['unavailableSamples'] += 1
                record = {'event': 'native_tree_pid_sample_unavailable', 'phase': phase, 'clockNs': monotonic_ns(),
                          'pid': pid, 'origins': origins, 'error': str(error), 'sample': None, 'cost': None}
                # A genuine process can exit between the view getter/lsof and libproc.
                # Only an exact, bounded OS observation may classify this as ended;
                # permission failures, live PID failures or missing proof stay errors.
                ended = False
                lifecycle = [e for e in records(self.run / 'stdout.txt') if e.get('pid') == self.desktop_pid]
                confirmed = [e['monotonic_ns'] for e in lifecycle if e.get('event') == 'desktop_close_confirmed']
                exits = [e['monotonic_ns'] for e in lifecycle if e.get('event') == 'desktop_exit']
                normal_exit_trace = bool(confirmed and exits and max(confirmed) <= max(exits) <= record['clockNs'])
                record['normalCloseExitTrace'] = normal_exit_trace
                if error.errno == 3 and normal_exit_trace:
                    # Never accept a missing component while its host is still operating.
                    try:
                        host_code = self.desktop_process.wait(timeout=.1)
                        record.update(hostExitCode=host_code, hostExitConfirmedNs=monotonic_ns(),
                                      closeConfirmedNs=max(confirmed), desktopExitEventNs=max(exits))
                    except subprocess.TimeoutExpired:
                        host_code = None
                        record['hostExitCheckTimeoutSeconds'] = .1
                    if host_code == 0:
                        argv = ['/bin/ps', '-p', str(pid), '-o', 'pid=,ppid=,lstart=,comm=']
                        try:
                            check = subprocess.run(argv, capture_output=True, text=True, timeout=.1)
                            record.update(exitCheckArgv=argv, exitCheckCode=check.returncode,
                                          exitCheckStdout=check.stdout, exitCheckStderr=check.stderr,
                                          exitCheckClockNs=monotonic_ns())
                            ended = check.returncode == 1 and not check.stdout.strip() and not check.stderr.strip()
                        except subprocess.TimeoutExpired:
                            record['exitCheckTimeoutSeconds'] = .1
                if ended:
                    record['disposition'] = 'confirmed_absent_after_actual_association; terminal unavailable sample, not zero cost'
                    self.exited_pids.add(pid)
                    item['confirmedAbsentClockNs'] = record['exitCheckClockNs']
                    self.terminal_observations.append(record)
                else:
                    self.errors.append(record)
                with (self.run / 'webkit-resource-association.jsonl').open('a') as output:
                    output.write(json.dumps(record) + '\n')

        if phase == 'after_normal_or_failed_close':
            for pid in sorted(self.pids):
                argv = ['/bin/ps', '-p', str(pid), '-o', 'pid=,ppid=,lstart=,comm=']
                try:
                    check = subprocess.run(argv, capture_output=True, text=True, timeout=.1)
                    self.after_close_checks.append({'pid': pid, 'clockNs': monotonic_ns(), 'argv': argv,
                                                    'exitCode': check.returncode, 'stdout': check.stdout,
                                                    'stderr': check.stderr, 'killAuthorized': False,
                                                    'scope': 'exact previously attributed XPC/child PID; shared system service lifetime is not treated as an owned orphan'})
                except subprocess.TimeoutExpired:
                    self.after_close_checks.append({'pid': pid, 'clockNs': monotonic_ns(), 'timeoutSeconds': .1, 'state': 'unknown', 'killAuthorized': False})

    def summary(self):
        observed = [item for item in self.pids.values() if item['resourceSamples'] > 0]
        names = '\n'.join(item['ps'] for item in observed)
        unknown = [name for name in ['WebContent', 'Networking', 'GPU'] if 'WebKit.' + name not in names]
        return {'method': '1Hz actual POSIX descendants, exact current-profile store handles and fixed current WKWebView PID getters; targeted PID metadata/libproc',
                'webviewProcessProbeObservations': self.webview_probes,
                'webviewGetterPids': sorted(pid for pid, item in self.pids.items() if 'current_wkwebview_fixed_pid_getter' in item['origins']),
                'storeId': self.store_id, 'paths': [str(p) for p in self.paths], 'associatedPids': list(self.pids.values()),
                'posixChildPids': sorted(pid for pid, item in self.pids.items() if 'actual_posix_descendant' in item['origins']),
                'storeHandlePids': sorted(pid for pid, item in self.pids.items() if 'owned_store_open_file' in item['origins']),
                'deduplicatedResourcePidSet': sorted(self.pids), 'deduplication': 'union by PID and actual sample time; child/store origins do not add duplicate cost',
                'errors': self.errors, 'afterClosePidChecks': self.after_close_checks, 'terminalUnavailableObservations': self.terminal_observations, 'unattributedPotentialComponents': unknown,
                'completeExpectedComponentAttribution': not unknown and not self.errors, 'unattributedCost': None,
                'limitation': 'A service without a POSIX-descendant, exact-owned-store open-file or current WKWebView PID getter association is not attributed. Missing/short-lived samples remain null, not zero; sampled peaks are not lifetime maxima. No XPC process is killed or claimed as an orphan.'}


def native_cycle(project, root, role, binary, profile, scenario, build):
    from run_protocol import ProcessSampler, Rpc
    import shutil
    run = new_run(root, role)
    before = listeners(run)
    if any(before.values()):
        raise RuntimeError('native cycle fixed port conflict')
    manifest_dir = root / 'profile' / role / 'native' / run.name
    manifest_dir.mkdir(parents=True, exist_ok=False)
    manifest = {'taskId': 'ARCH-AW-005', 'revision': 'r5', 'role': role, 'runId': run.name,
                'sourceCandidate': build['source_candidate_sha256'], 'ownedMarker': 'ARCH-AW-005-r5-owned',
                'profileDir': str(profile), 'workspace': None, 'allowedPorts': [30102,30103,30104], 'scenario': scenario}
    manifest_path = manifest_dir / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    shutil.copyfile(manifest_path, run / 'manifest.json')
    env = environment(root, role, 'desktop/validation')
    env['DS_TEST_RUN_ROOT'] = str(root)
    status = {'scenario': scenario, 'run': str(run), 'binarySha256': digest(binary), 'sourceCandidate': build['source_candidate_sha256'],
              'profile': str(profile), 'result': 'running', 'portsBefore': before, 'clockId': 'darwin-clock-monotonic-ns',
              'pythonClockCall': 'libSystem.clock_gettime(clock_id=6), not Python3.9 monotonic absolute origin'}
    client = None
    sql_blocker = None
    sql_block_done = False
    sampler = ProcessSampler(run)
    with (run / 'stdout.txt').open('wb') as stdout, (run / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen([str(binary), '--ds-test-manifest', str(manifest_path)], cwd=project, env=env, stdout=stdout, stderr=stderr)
        status['pid'] = process.pid
        sampler.register(process, 'desktop')
        webkit = WebKitStoreResources(run,sampler,process)
        children = set()
        deadline = time.monotonic() + 250
        try:
            while time.monotonic() < deadline:
                events = records(run / 'stdout.txt')
                current_children = set(descendants(run, process.pid))
                children.update(current_children)
                webkit.observe(events, child_pids=current_children)
                if any(e.get('event') in ('native_driver_eval_failed', 'native_driver_timeout') or e.get('event') == 'native_dom_step' and e.get('status') == 'fail' for e in events):
                    raise RuntimeError('real native DOM driver failed')
                if not sql_block_done and sql_blocker is None and any(e.get('event') == 'native_dom_step' and e.get('step') == 'snapshot_stale_ready' for e in events):
                    sql_blocker = sqlite3.connect(str(profile / 'device-simulator-v1/config.sqlite'), timeout=1)
                    sql_blocker.execute('BEGIN EXCLUSIVE')
                    (run / 'sql-lock-observation.jsonl').open('a').write(json.dumps({'event':'owned_sql_exclusive_begin','clockNs':monotonic_ns(),'path':str(profile / 'device-simulator-v1/config.sqlite')}) + '\n')
                if sql_blocker is not None and any(e.get('event') == 'native_dom_step' and e.get('step') == 'snapshot_stale_observed' for e in events):
                    sql_blocker.rollback();sql_blocker.close();sql_blocker = None;sql_block_done = True
                    (run / 'sql-lock-observation.jsonl').open('a').write(json.dumps({'event':'owned_sql_exclusive_release','clockNs':monotonic_ns()}) + '\n')
                if client is None and any(e.get('event') == 'native_dom_step' and e.get('step') == 'listener_started' for e in events):
                    client = Rpc([str(root / 'build' / role / build['binaries']['reference']['path']), '--run-root', str(run)], run, 'reference', sampler)
                    connected = client.call('0 connect 30102 1')
                    if not connected['ok']:
                        raise RuntimeError('native independent S7 client failed')
                    readback = client.call('0 read 71 0 4')
                    if readback['codes'] != [255]:
                        raise RuntimeError('native real configured DB71 read failed')
                if process.poll() is not None:
                    status['waitObservedNs'] = monotonic_ns()
                    break
                time.sleep(.02)
            else:
                raise RuntimeError('native cycle absolute deadline exceeded')
            events = records(run / 'stdout.txt')
            dom = [e for e in events if e.get('event') == 'native_dom_step']
            opened = next(e for e in events if e.get('event') == 'profile_open')
            status['webviewStoreId'] = opened['webviewStoreId']
            status['webviewMetadata'] = webkit_metadata(run, opened['webviewStoreId'], 'com.aiis.aw.devicesimulator.validation')
            if not any(row['exists'] for row in status['webviewMetadata']):
                raise RuntimeError('actual owned WK store path not observed')
            for event in ['native_abi_validated','desktop_window_close_requested','desktop_close_confirmed','desktop_exit_requested','desktop_shutdown_joined','desktop_exit']:
                if not any(e.get('event') == event for e in events):
                    raise RuntimeError('normal lifecycle evidence missing: ' + event)
            confirmed = max(e['monotonic_ns'] for e in events if e.get('event') == 'desktop_close_confirmed')
            status['normalCloseUpperNs'] = status['waitObservedNs'] - confirmed
            if process.returncode != 0 or not 0 <= status['normalCloseUpperNs'] <= 5000000000 or not dom or dom[-1].get('step') != 'close_ready':
                raise RuntimeError('normal close/DOM sequence threshold failed')
            status['steps'] = dom
            status['result'] = 'pass'
        except Exception as error:
            status.update(result='fail', error=str(error))
        finally:
            if sql_blocker is not None:
                sql_blocker.rollback();sql_blocker.close()
            if process.poll() is None:
                # 只用于失败实验收尾，绝不计正常窗口退出。
                status['interruptedExperiment'] = True
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=5)
            if client is not None:
                client.close()
            webkit.observe(records(run/'stdout.txt'),phase='after_normal_or_failed_close',force=True)
            status['webviewResourceCoverage']=webkit.summary()
            status['samplerComplete'] = sampler.close()
            status['exitCode'] = process.returncode
            status['ownedChildren'] = sorted(children)
            status['portsAfter'] = listeners(run)
            status['remainingPids'] = []
            for pid in sorted(children | {process.pid}):
                result = execute(run, ['/bin/ps','-p',str(pid),'-o','pid=,ppid=,command='])
                if result.returncode == 0 and result.stdout.strip():
                    status['remainingPids'].append({'pid': pid, 'observed': result.stdout})
            if status['remainingPids'] or any(status['portsAfter'].values()) or not status['samplerComplete']:
                status['result'] = 'fail'
                status['cleanupIncomplete'] = True
            db = profile / 'device-simulator-v1/config.sqlite'
            if db.exists():
                shutil.copyfile(db, run / 'configuration-after.sqlite')
                status['configurationSha256'] = digest(db)
                probe = sqlite3.connect(str(db), timeout=1)
                probe.execute('BEGIN EXCLUSIVE');probe.rollback();probe.close()
                status['sqliteClosedReadableExclusive'] = True
            (run / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps({key: status.get(key) for key in ['scenario','run','pid','result','error','normalCloseUpperNs','remainingPids']}), flush=True)
    return status


def native(project, root, role, run):
    import build_native
    status = {'suite': 'native', 'result': 'running', 'cycles': []}
    try:
        # 普通产品与自动化build是各自独立的真实产物，不复用旧target或binary。
        product_env = environment(root, role, 'desktop/product')
        result = execute(run, ['pnpm','tauri','build','--no-bundle','--features','native-s7'], project, product_env)
        if result.returncode:
            raise RuntimeError('normal no-bundle product build failed')
        product_binary = root / 'build' / role / 'desktop/product/release/aiis-device-simulator'
        status['productBinary'] = {'path': str(product_binary), 'sha256': digest(product_binary)}
        rejected = execute(run, [str(product_binary), '--ds-test-manifest', '/not-an-owned-manifest'], project, product_env)
        if rejected.returncode != 2:
            raise RuntimeError('normal product accepted test argument')
        config = root / 'profile' / role / 'tauri.test.json'
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps({'identifier':'com.aiis.aw.devicesimulator.validation','build':{'frontendDist':str(root/'build'/role/'frontend')}}, indent=2) + '\n')
        env = environment(root, role, 'desktop/validation')
        env['DS_FRONTEND_OUT_DIR'] = str(root / 'build' / role / 'frontend')
        result = execute(run, ['pnpm','exec','tauri','build','--no-bundle','--features','native-s7,test-automation','--config',str(config)], project, env)
        if result.returncode:
            raise RuntimeError('non-default native test build failed')
        binary = root / 'build' / role / 'desktop/validation/release/aiis-device-simulator'
        status['testBinary'] = {'path': str(binary), 'sha256': digest(binary)}
        for path in [product_binary,binary]:
            execute(run,['/usr/bin/file',str(path)])
            execute(run,['/usr/bin/otool','-L',str(path)])
            execute(run,['/usr/bin/otool','-X','-s','__TEXT','__info_plist',str(path)])
        if build_native.build(project,root,role):
            raise RuntimeError('current product B0 is not closed; no listener permitted')
        b0 = json.loads((root/'tmp'/role/'latest-b0.json').read_text())
        build = json.loads((pathlib.Path(b0['run'])/'build-manifest.json').read_text())
        status['b0Run'] = b0['run']
        profile = root/'profile'/role/'native'/('workspace-'+run.name)
        for scenario in ['N1','N2','N3']:
            cycle = native_cycle(project,root,role,binary,profile,scenario,build)
            status['cycles'].append(cycle)
            if cycle['result'] != 'pass':
                raise RuntimeError('actual '+scenario+' failed; later scenes not run')
        status['result'] = 'pass'
    except Exception as error:
        status.update(result='fail',error=str(error))
    (run/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps({'suite':'native','run':str(run),'result':status['result'],'error':status.get('error')}),flush=True)
    return 0 if status['result']=='pass' else 1


def product_protocol(project, root, role, parent_run):
    """K07真实通用DB/两端口；使用同一产品App与正式独立reference，无固定41/57。"""
    import concurrent.futures
    import struct
    import threading
    from run_protocol import Suite, require, emit
    suite = Suite(project, root, role, 'K07')
    suite.workspace_name = 'product-workspace.json'
    result = {'case': 'K07', 'status': 'blocked'}
    try:
        require(not any(listeners(suite.run, (30102, 30103, 30104)).values()), 'fixed port conflict')
        suite.setup(); suite.start()
        a, b = suite.client('A'), suite.client('B')
        reads = []
        stop = threading.Event()
        def observe_b():
            for index in range(200):
                if stop.is_set(): return
                response = suite.read(b, 0, 4, 94)
                require(response['codes'] == [255] and response['payload'] == '0000001d', 'B changed during A lifecycle')
                reads.append(response)
                emit(suite.run / 'results.jsonl', {'event': 'K07_B_read', 'index': index, 'response': response})
                if stop.wait(.1): return
            raise AssertionError('K07 B observer deadline')
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            future = pool.submit(observe_b)
            try:
                for db, value in [(71, bytes.fromhex('01020304')), (88, struct.pack('>f', 2.5)), (109, bytes.fromhex('08034142430000000000'))]:
                    require(suite.write(a, 0, value, db)['codes'] == [255], 'generic DB write ' + str(db))
                    require(suite.read(a, 0, len(value), db)['payload'] == value.hex(), 'generic DB readback ' + str(db))
                require(suite.ctrl('stop A')['ok'] and suite.ctrl('reset A')['ok'], 'A reset stopped')
                require(suite.ctrl('start A')['ok'], 'A start after reset')
                a = suite.client('A')
                require(suite.read(a, 0, 4, 71)['payload'] == '00000011', 'A reset initial17')
                require(suite.write(a, 0, bytes.fromhex('00000034'), 71)['codes'] == [255], 'A hold52')
                before = suite.ctrl('snapshot A')
                require(suite.ctrl('stop A')['ok'] and suite.ctrl('reconfigure A')['ok'], 'real save/apply A while B active')
                after = suite.ctrl('snapshot A')
                require(after['epoch'] == before['epoch'] + 1, 'A apply new epoch')
                require(suite.ctrl('start A')['ok'], 'A restart after apply')
                a = suite.client('A')
                require(suite.read(a, 0, 4, 71)['payload'] == '00000034', 'compatible hold52 preserved by A apply')
                time.sleep(.3)
            finally:
                stop.set(); future.result()
        require(len(reads) >= 2, 'B continuous progress missing')
        result = {'case': 'K07', 'status': 'pass', 'A_dbs': [71, 88, 109], 'B_dbs': [94, 130], 'B_reads': len(reads), 'B_cadence_seconds': .1}
    except Exception as error:
        result.update(status='fail' if suite.server else 'blocked', error=str(error))
    finally:
        cleanup = suite.finish()
        if not cleanup['clean']: result.update(status='fail', cleanupFailed=True)
        elif not cleanup['evidence_complete']: result.update(status='blocked', evidenceIncomplete=True)
        (suite.run / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
        (parent_run / 'product-protocol.json').write_text(json.dumps({'run': str(suite.run), **result}, indent=2) + '\n')
        from collect_evidence import seal
        seal(suite.run)
    print(json.dumps({'run': str(suite.run), **result}), flush=True)
    return result['status'] == 'pass'


def protocol(project, root, role, run):
    """原19项保持次数/阈值；每轮独立product profile/reset，失败停止不伪造剩余通过。"""
    result = {'suite': 'protocol', 'caseRuns': [], 'result': 'running'}
    try:
        if not product_protocol(project, root, role, run):
            raise RuntimeError('actual generic K07 protocol failed')
        cases = ['W%02d' % n for n in range(1, 10) for _ in range(3)]
        cases += ['C01', 'C03', 'C04', 'C05', 'C06', 'D01', 'D02'] + ['X01'] * 3 + ['X02']
        # C02 is executed with the same 16 live C01 sessions, not restarted as a separate empty-case proof.
        for case in cases:
            command = ['/usr/bin/python3', '-B', str(project / 'scripts/run_protocol.py'), '--project-root', str(project), '--run-root', str(root), '--role', role, '--case', case]
            completed = execute(run, command, project, environment(root, role, 'runtime'))
            lines = [line for line in completed.stdout.splitlines() if line.startswith('{')]
            record = json.loads(lines[-1]) if lines else {'case': case, 'status': 'blocked', 'error': 'missing actual case receipt'}
            result['caseRuns'].append(record)
            if record.get('run'):
                from collect_evidence import seal
                record['archive'] = seal(pathlib.Path(record['run']))
            print(json.dumps(record), flush=True)
            if completed.returncode or record.get('status') not in ('pass', 'not_applicable'):
                raise RuntimeError('actual original case failed: ' + case)
        result['result'] = 'pass'
    except Exception as error:
        result.update(result='fail', error=str(error))
    (run / 'status.json').write_text(json.dumps(result, indent=2) + '\n')
    return 0 if result['result'] == 'pass' else 1


def profile_lock_processes(project, root, role, run, env):
    """K02真实两进程争同profile；无需listener，失败进程不接管、不修改原配置。"""
    from run_protocol import ProcessSampler, require
    build = execute(run, ['cargo','build','--offline','--locked','--manifest-path',str(project/'runtime/Cargo.toml'),'--features','native-s7,test-automation','--bin','ds-test-host'],project,env)
    if build.returncode: raise RuntimeError('profile lock host build failed')
    host = root/'build'/role/'runtime/debug/ds-test-host'
    profile = root/'profile'/role/'normal'/run.name/'cross-process-lock'
    profile.mkdir(parents=True,exist_ok=False)
    manifest = {'taskId':'ARCH-AW-005','revision':'r5','role':role,'runId':run.name,'sourceCandidate':candidate(source_inventory(project)),'ownedMarker':'ARCH-AW-005-r5-owned','profileDir':str(profile),'workspace':None,'allowedPorts':[30102,30103,30104],'scenario':None}
    path=profile/'manifest.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
    status={'hostSha256':digest(host),'manifest':manifest,'portsBefore':listeners(run)}
    with (run/'lock-owner-stdout.jsonl').open('wb') as out, (run/'lock-owner-stderr.txt').open('wb') as err:
        first=subprocess.Popen([str(host),'--ds-test-manifest',str(path)],env=env,cwd=project,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True)
        status['ownerPid']=first.pid
        try:
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                if any(e.get('event')=='ready_stopped' for e in records(run/'lock-owner-stdout.jsonl')):break
                if first.poll() is not None:raise RuntimeError('first profile owner exited before ready')
                time.sleep(.02)
            else:raise RuntimeError('first profile owner not ready')
            database=profile/'device-simulator-v1/config.sqlite';before=digest(database)
            second=execute(run,[str(host),'--ds-test-manifest',str(path)],project,env)
            require(second.returncode==1 and 'profile_in_use' in second.stderr,'second process unexpectedly took profile')
            require(digest(database)==before,'rejected second process changed configuration bytes')
            first.stdin.write('quit\n');first.stdin.flush();first.stdin.close();first.wait(timeout=5)
            require(first.returncode==0,'profile owner normal shutdown failed')
            probe=sqlite3.connect(str(database),timeout=1);probe.execute('BEGIN EXCLUSIVE');probe.rollback();probe.close()
            status.update(result='pass',ownerExit=first.returncode,databaseSha256=before,secondExit=second.returncode,portsAfter=listeners(run))
            require(not any(status['portsAfter'].values()),'profile lock experiment left listener')
        finally:
            if first.poll() is None:
                status['interruptedExperiment']=True;first.terminate()
                try:first.wait(timeout=5)
                except subprocess.TimeoutExpired:first.kill();first.wait(timeout=5)
            (run/'profile-lock-processes.json').write_text(json.dumps(status,indent=2)+'\n')
    return status


def completed_phase(project, root, role, phase):
    phase_run=new_run(root,role)
    code={'build':normal_dev,'core':core,'native':native,'protocol':protocol}[phase](project,root,role,phase_run)
    from collect_evidence import seal, ARCHIVE
    from verify_evidence import verify_archive
    # Nested B0/native/case runs are independently immutable raw sets.
    for child in sorted((root/'runs').glob(role+'-[0-9][0-9][0-9][0-9]')):
        if int(child.name.split('-')[1]) < int(phase_run.name.split('-')[1]):continue
        archive=ARCHIVE/(role+'-run-'+child.name.split('-')[1])
        if archive.exists():verify_archive(archive)
        else:seal(child)
    return {'phase':phase,'run':str(phase_run),'exitCode':code,'result':'pass' if code==0 else 'fail'}


def all_validation(project,root,role,run):
    status={'suite':'all','sourceCandidate':candidate(source_inventory(project)),'phases':[],'result':'running'}
    for phase in ['build','core','native','protocol']:
        result=completed_phase(project,root,role,phase)
        status['phases'].append(result)
        if result['exitCode']:
            status['result']='fail';break
    else:status['result']='pass'
    if status['sourceCandidate']!=candidate(source_inventory(project)):
        status.update(result='fail',error='formal source changed during complete validation')
    (run/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    from collect_evidence import seal
    seal(run)
    print(json.dumps(status),flush=True)
    return 0 if status['result']=='pass' else 1


def cleanup_check(project,root,role,run):
    status={'suite':'cleanup-check','ports':listeners(run),'sourceCandidate':candidate(source_inventory(project))}
    obsolete=[project/'g0']+[project/'runtime'/p for p in ['src/bin/ds-g0-server.rs','src/bin/ds-g0-abi-probe.rs','src/commands/mod.rs','src/commands/stdio.rs','src/config/g0_profile.rs']]
    status['obsoletePresent']=[str(p) for p in obsolete if p.exists()]
    status['result']='pass' if not status['obsoletePresent'] and not any(status['ports'].values()) else 'fail'
    (run/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status))
    return 0 if status['result']=='pass' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=pathlib.Path)
    parser.add_argument('--run-root', type=pathlib.Path)
    parser.add_argument('--role', choices=['dev', 'qa'])
    parser.add_argument('--suite', choices=['all', 'build', 'core', 'protocol', 'native', 'cleanup-check'])
    args = parser.parse_args()
    if not all((args.project_root, args.run_root, args.role, args.suite)):
        parser.print_help()
        return 0
    project, root = args.project_root.resolve(), args.run_root.resolve()
    if root != RUN_ROOT or project != pathlib.Path(__file__).resolve().parents[1]:
        raise RuntimeError('explicit approved project/run root required')
    inputs = checked_inputs(project)
    run = new_run(root, args.role)
    (run / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    source = source_inventory(project)
    (run/'source-manifest.json').write_text(json.dumps(source,indent=2)+'\n')
    for name in source:
        import shutil
        target = run/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/name,target)
    if args.suite == 'all':
        return all_validation(project,root,args.role,run)
    if args.suite == 'cleanup-check':
        return cleanup_check(project,root,args.role,run)
    if args.suite == 'build':
        return normal_dev(project, root, args.role, run)
    if args.suite == 'core':
        return core(project,root,args.role,run)
    if args.suite == 'native':
        return native(project,root,args.role,run)
    if args.suite == 'protocol':
        return protocol(project,root,args.role,run)
    raise RuntimeError('suite not implemented yet; no pass or side effects were inferred')


if __name__ == '__main__':
    raise SystemExit(main())
