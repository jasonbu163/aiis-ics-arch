#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按持久r4原件闭集逐文件计划/退役；只有当前产品全验证通过才允许执行。"""
import argparse
import json
import pathlib
from collect_evidence import ARCHIVE, RUN_ROOT, digest
from run_validation import candidate, source_inventory

OLD_RUNTIME = ['src/bin/ds-g0-server.rs', 'src/bin/ds-g0-abi-probe.rs', 'src/commands/mod.rs', 'src/commands/stdio.rs', 'src/config/g0_profile.rs']


def plan(project, extra):
    archive = ARCHIVE / 'r4-stop-snapshot'
    original = json.loads((archive / 'inventory.json').read_text())['files']
    archive_paths = {name: archive / name for name in original}
    if extra is not None:
        from verify_evidence import verify_archive
        verify_archive(extra)
        reference = json.loads((extra / 'original-member-reference.json').read_text())
        for relative, expected in reference['members'].items():
            name = 'sources/automation-world/device-simulator/' + relative
            original[name] = expected
            archive_paths[name] = extra / expected['archiveMember']
    rows = []
    for member, expected in sorted(original.items()):
        prefix = 'sources/automation-world/device-simulator/'
        if not member.startswith(prefix):
            continue
        relative = member[len(prefix):]
        if not (relative.startswith('g0/') or relative in ['runtime/' + p for p in OLD_RUNTIME]):
            continue
        preserved = archive_paths[member]
        current = project / relative
        if digest(preserved) != expected['sha256'] or preserved.stat().st_size != expected['bytes']:
            raise RuntimeError('persistent original mismatch: ' + member)
        if not current.is_file() or current.is_symlink() or digest(current) != expected['sha256']:
            raise RuntimeError('old source drift/absent: ' + relative)
        if relative.startswith('g0/vendor/'):
            migrated = 'native/vendor/snap7-1.4.2'
        elif relative.startswith('g0/client/'):
            migrated = 'tests/protocol'
        elif 'daa' in relative:
            migrated = 'tests/compatibility/daa-client'
        elif 'fixture' in relative:
            migrated = 'tests/fixtures/protocol-workspace.json'
        elif relative.startswith('runtime/') or 'abi' in relative:
            migrated = 'runtime/src/bin/ds-test-host.rs + runtime/tests/ffi_contract.rs'
        else:
            migrated = 'scripts + README/BUILD bilingual product entries'
        rows.append({'path': relative, 'action': 'retire_after_validation', 'migration': migrated,
                     'archiveMember': str(preserved), 'sha256': expected['sha256'], 'bytes': expected['bytes']})
    actual = {str(p.relative_to(project)) for p in (project / 'g0').rglob('*') if p.is_file()}
    if actual != {row['path'] for row in rows if row['path'].startswith('g0/')}:
        raise RuntimeError('old G0 membership differs from original closed set')
    return {'taskId': 'ARCH-AW-005', 'revision': 'r5', 'sourceCandidateBefore': candidate(source_inventory(project)),
            'persistentOriginalInventorySha256': digest(archive / 'inventory.json'), 'rows': rows,
            'kept': ['runtime unique owner/image/queues/FFI/clock/logging/resource implementation', 'all historical plans/P4 and A4/A5 raw'],
            'notDeleted': ['cache/build/profile/system WebKit data/foreign resources'], 'executed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path)
    parser.add_argument('--validation-run', type=pathlib.Path)
    parser.add_argument('--extra-originals', type=pathlib.Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.project_root or not args.output:
        parser.print_help()
        return 0
    project, output = args.project_root.resolve(), args.output.resolve()
    if project != pathlib.Path(__file__).resolve().parents[1] or not output.is_relative_to(RUN_ROOT / 'tmp/dev'):
        raise RuntimeError('explicit owned project/output required')
    record = plan(project, args.extra_originals.resolve() if args.extra_originals else None)
    if args.execute:
        validation = args.validation_run.resolve() if args.validation_run else None
        if validation is None or validation.parent != RUN_ROOT / 'runs' or not validation.name.startswith('dev-'):
            raise RuntimeError('explicit DEV completed product validation required')
        status = json.loads((validation / 'status.json').read_text())
        if status.get('suite') != 'all' or status.get('result') != 'pass' or status.get('sourceCandidate') != record['sourceCandidateBefore']:
            raise RuntimeError('current product normal/core/native/protocol full validation not passed')
        from verify_evidence import verify_archive
        verify_archive(ARCHIVE / ('dev-run-' + validation.name.split('-')[1]))
        # Exact files only. Empty-directory removal never follows links or deletes non-enumerated contents.
        for row in record['rows']:
            (project / row['path']).unlink()
        directories = sorted({p.parent for row in record['rows'] for p in [(project / row['path'])]} | {p for p in (project / 'g0').rglob('*') if p.is_dir()}, key=lambda p: len(p.parts), reverse=True)
        for directory in directories:
            if directory.is_symlink():
                raise RuntimeError('unexpected symlink during empty-directory cleanup')
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
        if (project / 'g0').exists() and not any((project / 'g0').iterdir()):
            (project / 'g0').rmdir()
        record.update(executed=True, validationRun=str(validation), sourceCandidateAfter=candidate(source_inventory(project)))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'plan': str(output), 'members': len(record['rows']), 'executed': record['executed']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
