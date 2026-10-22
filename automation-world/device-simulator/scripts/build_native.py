#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同产品Rust库的无端口B0构建/ABI/clock/预算记录；裸入口仅帮助。"""
import argparse
import difflib
import json
import pathlib
import re
import shutil
import subprocess
from collect_evidence import RUN_ROOT, digest
from run_validation import candidate, checked_inputs, environment, execute, listeners, new_run, source_inventory


def registry(lock):
    packages = {}
    for block in lock.read_text().split('[[package]]')[1:]:
        fields = dict(re.findall(r'^([a-z_]+) = "([^"]*)"$', block, re.M))
        if fields.get('source', '').startswith('registry+'):
            packages[(fields['name'], fields['version'])] = fields['checksum']
        elif fields.get('source'):
            raise RuntimeError('unapproved non-registry dependency')
    return packages


def audit_sources(project, root, role, run, inputs):
    bank = registry(project.parents[1] / 'automation-world/data-acquisition-agent/src-tauri/Cargo.lock')
    if len(bank) != 548:
        raise RuntimeError('frozen registry bank drift')
    locks = {}
    for name, path in [('runtime', project / 'runtime/Cargo.lock'), ('desktop', project / 'src-tauri/Cargo.lock'), ('managedS7', project / 'tests/compatibility/daa-client/Cargo.lock')]:
        actual = registry(path)
        if any(bank.get(key) != value for key, value in actual.items()):
            raise RuntimeError('dependency outside frozen bank: ' + name)
        locks[name] = {'sha256': digest(path), 'registryPackages': len(actual)}
    vendor = project / 'native/vendor/snap7-1.4.2'
    upstream = json.loads((vendor / 'upstream-manifest.json').read_text())['files']
    controlled = json.loads((vendor / 'controlled-manifest.json').read_text())['files']
    allowed = sorted('src/' + name for name in ['core/s7_server.h','core/s7_server.cpp','core/s7_isotcp.h','core/s7_isotcp.cpp','sys/snap_msgsock.h','sys/snap_msgsock.cpp','sys/snap_tcpsrvr.h','sys/snap_tcpsrvr.cpp'])
    if len(upstream) != 34 or set(controlled) != set(upstream):
        raise RuntimeError('native source membership drift')
    changed = []
    patch = b''
    for name in sorted(upstream):
        before, after = vendor / 'upstream' / name, vendor / 'controlled' / name
        if digest(before) != upstream[name] or digest(after) != controlled[name]:
            raise RuntimeError('native source manifest mismatch: ' + name)
        if before.read_bytes() != after.read_bytes():
            changed.append(name)
            patch += b''.join(difflib.diff_bytes(difflib.unified_diff, before.read_bytes().splitlines(keepends=True), after.read_bytes().splitlines(keepends=True), ('upstream/' + name).encode(), ('controlled/' + name).encode()))
    if changed != allowed:
        raise RuntimeError('native eight-file boundary mismatch')
    (run / 'vendor-computed-diff.patch').write_bytes(patch)
    archive = pathlib.Path('/private/tmp/arch-aw-005-r2-p0-_ap0y325/pm/downloads/snap7-full-1.4.2.7z')
    expected = '1f4270cde8684957770a10a1d311c226e670d9589c69841a9012e818f7b9f80e'
    if digest(archive) != expected:
        raise RuntimeError('native original archive drift')
    target = root / 'cache' / role / 'native/snap7-full-1.4.2.7z'
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(archive, target)
    if digest(target) != expected:
        raise RuntimeError('owned native archive copy mismatch')
    icons = {}
    for name in ['32x32.png','128x128.png','128x128@2x.png','icon.icns','icon.ico']:
        relative = 'automation-world/data-acquisition-agent/src-tauri/icons/' + name
        actual = digest(project / 'src-tauri/icons' / name)
        if actual != inputs['frozenMembers'][relative]:
            raise RuntimeError('frozen icon mismatch')
        icons[name] = actual
    return {'registryBankCount': len(bank), 'locks': locks, 'nativeMembers': 34, 'controlledChanged': changed,
            'threadFrameworkUnchanged': True, 'nativeArchive': {'path': str(target), 'sha256': expected},
            'computedPatchSha256': digest(run / 'vendor-computed-diff.patch'), 'storedPatchSha256': digest(vendor / 'native.patch'),
            'icons': icons, 'borrowBoundary': 'callbacks borrow Arc::as_ptr backing; packed tag ptr::read_unaligned; int return0/37 actual probe; no registered area image',
            'callChain': 'native existing request/item loop -> begin_pdu whole-PDU descriptor/reservation -> Rust owner::call/apply -> same image -> item int error -> original native response encoder; real pthread_join then release callback, Rust owner join at shutdown'}


def command(run, argv, project, env):
    result = execute(run, argv, project, env)
    if result.returncode:
        raise RuntimeError('build command failed: ' + ' '.join(argv) + '\n' + result.stderr[-3000:])
    return result


def build(project, root, role):
    inputs = checked_inputs(project)
    run = new_run(root, role)
    (run / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    source = source_inventory(project)
    source_sha = candidate(source)
    manifest = {'revision': 'r5', 'role': role, 'b0': 'open', 'source': source,
                'source_candidate_sha256': source_sha, 'sourceInputsSha256': inputs['sourceInputsSha256'],
                'binaries': {}, 'listenersStarted': False}
    try:
        for name in source:
            destination = run / 'source' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(project / name, destination)
        manifest['sourceAudit'] = audit_sources(project, root, role, run, inputs)
        if any(listeners(run).values()):
            raise RuntimeError('fixed port conflict before B0')
        env = environment(root, role, 'runtime')
        versions = [(['rustc', '--version'], 'rustc 1.89.0 '),
                    (['cargo', '--version'], 'cargo 1.89.0 '),
                    (['cmake', '--version'], 'cmake version 4.0.2'),
                    (['/usr/bin/clang++', '--version'], 'Apple clang version 17.0.0'),
                    (['/usr/bin/xcrun', '--show-sdk-version'], '26.1'),
                    (['/usr/bin/python3', '--version'], 'Python 3.9.6'),
                    (['node', '--version'], 'v22.19.0'),
                    (['pnpm', '--version'], '11.11.0')]
        for argv, expected in versions:
            actual = command(run, argv, project, env).stdout.strip()
            if not actual.startswith(expected):
                raise RuntimeError('frozen toolchain drift: ' + repr(argv) + ': ' + actual)
        command(run, ['/usr/bin/xcrun', '--show-sdk-path'], project, env)
        probe_env = dict(env)
        probe_env['DS_TEST_RUN_ROOT'] = str(root / 'profile' / role / 'normal' / run.name / 'log-probe')
        snapshot_probe = command(run, ['cargo','test','--offline','--locked','--manifest-path',str(project/'runtime/Cargo.toml'),'--features','native-s7,test-automation','--lib','logging::tests','--','--nocapture'], project, probe_env)
        measured = [json.loads(line) for line in snapshot_probe.stdout.splitlines() if line.startswith('{') and 'maximum_snapshot_probe' in line]
        if len(measured) != 1 or measured[0]['log']['observabilityDegraded'] or measured[0]['eventHeapUpper'] > 256*1024:
            raise RuntimeError('C16/H4 complete snapshot actual sink/heap probe failed')
        probe_root = pathlib.Path(measured[0]['root'])
        if not probe_root.is_relative_to(pathlib.Path(probe_env['DS_TEST_RUN_ROOT'])):
            raise RuntimeError('log probe escaped owned root')
        shutil.copytree(probe_root,run/'maximum-log-snapshot-probe')
        manifest['maximumLogSnapshotProbe'] = measured[0]
        queue_probe = [json.loads(line) for line in snapshot_probe.stdout.splitlines() if line.startswith('{') and 'file_queue_count_probe' in line]
        if len(queue_probe) != 1 or queue_probe[0]['lineLimit'] != 8192 or queue_probe[0]['actualDroppedLines'] != 1 or queue_probe[0]['queuedBytesAfter'] != 0:
            raise RuntimeError('actual bounded file queue saturation/drain proof failed')
        manifest['fileQueueCountProbe'] = queue_probe[0]
        burst_probe = [json.loads(line) for line in snapshot_probe.stdout.splitlines() if line.startswith('{') and 'file_burst_rate_probe' in line]
        if len(burst_probe) != 1 or burst_probe[0]['completedBothSinks'] != 6144 or burst_probe[0]['droppedLines'] or burst_probe[0]['queueBytesAfter']:
            raise RuntimeError('real file sink burst/sustained-rate proof failed')
        burst_root = pathlib.Path(burst_probe[0]['root'])
        if not burst_root.is_relative_to(pathlib.Path(probe_env['DS_TEST_RUN_ROOT'])):
            raise RuntimeError('burst probe escaped owned root')
        shutil.copytree(burst_root,run/'file-burst-rate-probe')
        manifest['fileBurstRateProbe'] = burst_probe[0]
        command(run, ['cargo', 'build', '--offline', '--locked', '--release', '--manifest-path', str(project / 'runtime/Cargo.toml'), '--features', 'native-s7,test-automation', '--bin', 'ds-test-host'], project, env)
        host = root / 'build' / role / 'runtime/release/ds-test-host'
        probe = command(run, [str(host), '--probe'], project, env)
        abi = json.loads(probe.stdout)
        if abi['clock']['count'] != 100 or abi['abi']['callback_zero'] != 0 or abi['abi']['callback_nonzero'] != 37:
            raise RuntimeError('actual ABI/int/100 clock probe failed')
        (run / 'abi-clock.json').write_text(json.dumps(abi, indent=2) + '\n')
        sdk = command(run, ['/usr/bin/xcrun', '--show-sdk-path'], project, env).stdout.strip()
        native = root / 'build' / role / 'native'
        command(run, ['cmake', '-S', str(project / 'tests/protocol'), '-B', str(native / 'reference-build'), '-G', 'Unix Makefiles', '-DCMAKE_MAKE_PROGRAM=/usr/bin/make', '-DCMAKE_CXX_COMPILER=/usr/bin/clang++', '-DCMAKE_OSX_ARCHITECTURES=arm64', '-DCMAKE_OSX_SYSROOT=' + sdk, '-DDS_NATIVE_OUTPUT_DIR=' + str(native)], project, env)
        command(run, ['cmake', '--build', str(native / 'reference-build'), '--parallel', '2'], project, env)
        daa_env = environment(root, role, 'daa')
        command(run, ['cargo', 'build', '--offline', '--locked', '--release', '--manifest-path', str(project / 'tests/compatibility/daa-client/Cargo.toml'), '--no-default-features', '--features', 'rust-snap7-driver'], project, daa_env)
        dep_info = root/'build'/role/'daa/release/ds-s7-daa-client.d'
        dependency_text = dep_info.read_text()
        required_daa = ['domain/local_configuration.rs','domain/local_sample.rs','domain/source_import.rs','domain/point_naming.rs','infrastructure/managed_s7.rs']
        if any('/data-acquisition-agent/src-tauri/src/'+name not in dependency_text for name in required_daa) or '/shared/tia-import-core/src/lib.rs' not in dependency_text:
            raise RuntimeError('actual compiled ManagedS7/core dependency closure missing')
        shutil.copyfile(dep_info,run/'managed-s7-actual-dep-info.d')
        features = command(run,['cargo','tree','--offline','--locked','--manifest-path',str(project/'tests/compatibility/daa-client/Cargo.toml'),'--no-default-features','--features','rust-snap7-driver','-e','features'],project,daa_env)
        (run/'managed-s7-feature-tree.txt').write_text(features.stdout)
        manifest['managedS7ActualClosure'] = {'depInfoSha256':digest(run/'managed-s7-actual-dep-info.d'),'driver':True,'localValidation':False,'requiredModules':required_daa,'core':'0.1.0 path byte-frozen'}
        profile = root / 'profile' / role / 'protocol' / run.name
        profile.mkdir(parents=True, exist_ok=False)
        test_manifest = {'taskId': 'ARCH-AW-005', 'revision': 'r5', 'role': role, 'runId': run.name,
                         'sourceCandidate': source_sha, 'ownedMarker': 'ARCH-AW-005-r5-owned',
                         'profileDir': str(profile), 'workspace': str(project / 'tests/fixtures/protocol-workspace.json'),
                         'allowedPorts': [30102, 30103, 30104], 'scenario': None}
        path = profile / 'manifest.json'
        path.write_text(json.dumps(test_manifest, indent=2) + '\n')
        # 同产品服务编译/保存/apply合成workspace；仅snapshot+quit，不执行start。
        with (run / 'stopped-stdout.txt').open('wb') as stdout, (run / 'stopped-stderr.txt').open('wb') as stderr:
            result = subprocess.run([str(host), '--ds-test-manifest', str(path)], input=b'snapshot A\nsnapshot B\nquit\n', stdout=stdout, stderr=stderr, env=env, cwd=project, timeout=15)
        (run / 'stopped-command.json').write_text(json.dumps({'argv': [str(host), '--ds-test-manifest', str(path)], 'stdin': 'snapshot A\nsnapshot B\nquit\n', 'exitCode': result.returncode}, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError('product workspace stopped compilation failed: ' + (run / 'stopped-stderr.txt').read_text())
        events = [json.loads(line) for line in (run / 'stopped-stdout.txt').read_text().splitlines()]
        if not any(e.get('event') == 'ready_stopped' for e in events) or not any(e.get('event') == 'process_close' and e.get('clean') for e in events) or any(e.get('event') == 'accepted' for e in events):
            raise RuntimeError('stopped host/real join proof missing')
        shutil.copyfile(profile / 'events.jsonl', run / 'events.jsonl')
        snapshots = [e for e in events if e.get('event') == 'control_result' and e.get('command') == 'snapshot']
        if len(snapshots) != 2 or any(s.get('running') or s.get('tcp') or s.get('h') or s.get('c') for s in snapshots):
            raise RuntimeError('B0 stopped baseline mismatch')
        manifest['stoppedSnapshots'] = snapshots
        budgets = [e for e in events if e.get('event') == 'baseline_budget']
        if len(budgets) != 1 or len(budgets[0]['instances']) != 2:
            raise RuntimeError('actual product budget inventory missing')
        for item in budgets[0]['instances']:
            if item['connectionBaseCharge'] > 65536 or item['nativeFixedCharge'] + 20 * item['connectionBaseCharge'] > 1048576 or sum(item['wholePduReservation'][key] for key in ['retainedS7Input','descriptors','typedStageTotal','extraPayloadCopiesTotal','worstResponseFrame']) != 2208:
                raise RuntimeError('measured native/descriptor/job reservation exceeds fixed budget')
        manifest['budgets'] = budgets[0]
        close = next(e for e in events if e.get('event') == 'process_close')
        if close['observability']['observabilityDegraded']:
            raise RuntimeError('B0 evidence degradation')
        manifest['logActualPeaks'] = close['observability']['peaks']
        manifest['logConservativeBudget'] = {'singleEventHeapUpper': 256*1024, 'pendingHeapUpper': 8*1024*1024,
            'historyHeapUpper': 8*1024*1024, 'drainedBatchHeapUpper': 8*1024*1024, 'fileWorkerQueueBytesUpper': 16*1024*1024,
            'serializationAndParsedEventTemporariesUpper': 4*1024*1024, 'activeFileWorkerMessageUpper': 256*1024,
            'fileWorkerQueueLineLimit':8192, 'channelMetadataAndMessageHeadersUpper':2*1024*1024,
            'sumBytesUpper': 46*1024*1024+256*1024, 'withinConfigurationSqlPreviewLogReservation': 288*1024*1024,
            'method': 'Value recursive heap upper includes map-node allowance; additional 2MiB covers 8192 channel Msg(Vec)/stamp slots, queue-control headers and unused pending/history/drain VecDeque/Vec slots (frozen tracing-appender/crossbeam source); actual peaks are counters/capacities, not allocator/full-lifetime RSS; 1Hz samples separate'}
        manifest['abiClockSha256'] = digest(run / 'abi-clock.json')
        paths = {'test_host': host, 'reference': native / 'ds-s7-reference',
                 'reference_native': native / 'libds_s7_reference.dylib',
                 'managed_s7': root / 'build' / role / 'daa/release/ds-s7-daa-client'}
        native_outputs = list((root / 'build' / role / 'runtime/release/build').glob('ds-runtime-*/out/native/libds_s7_native.dylib'))
        if len(native_outputs) != 1:
            raise RuntimeError('ambiguous runtime native output')
        paths['runtime_native'] = native_outputs[0]
        for name, path in paths.items():
            manifest['binaries'][name] = {'path': str(path.relative_to(root / 'build' / role)), 'sha256': digest(path)}
            for argv in [['/usr/bin/file', str(path)], ['/usr/bin/otool', '-L', str(path)], ['/usr/bin/nm', '-gU', str(path)]]:
                command(run, argv, project, env)
        if source_inventory(project) != source or checked_inputs(project) != inputs:
            raise RuntimeError('formal source/input drift during B0')
        manifest['portsAfter'] = listeners(run)
        if any(manifest['portsAfter'].values()):
            raise RuntimeError('unexpected listener at B0 end')
        manifest['b0'] = 'closed'
    except Exception as error:
        manifest['b0'] = 'blocked'
        manifest['error'] = str(error)
    (run / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if manifest['b0'] == 'closed':
        pointer = root / 'tmp' / role / 'latest-b0.json'
        pointer.write_text(json.dumps({'run': str(run), 'manifestSha256': digest(run / 'build-manifest.json'), 'sourceCandidate': source_sha}, indent=2) + '\n')
    print(json.dumps({'run': str(run), 'b0': manifest['b0'], 'sourceCandidate': source_sha, 'error': manifest.get('error')}))
    return 0 if manifest['b0'] == 'closed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=pathlib.Path)
    parser.add_argument('--run-root', type=pathlib.Path)
    parser.add_argument('--role', choices=['dev', 'qa'])
    args = parser.parse_args()
    if not all((args.project_root, args.run_root, args.role)):
        parser.print_help()
        return 0
    if args.run_root.resolve() != RUN_ROOT:
        raise RuntimeError('explicit approved run root required')
    return build(args.project_root.resolve(), args.run_root.resolve(), args.role)


if __name__ == '__main__':
    raise SystemExit(main())
