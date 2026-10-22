#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读核对角色B0/正式来源/持久raw；裸入口仅帮助，不修改公开索引。"""
import argparse
import json
import pathlib
from collect_evidence import ARCHIVE as ARCHIVE_ROOT, RUN_ROOT, digest
from run_validation import candidate, checked_inputs, source_inventory


def verify_archive(path):
    path = path.resolve()
    if path.parent != ARCHIVE_ROOT or not path.name.startswith(('dev-run-', 'qa-run-')):
        raise RuntimeError('explicit owned sealed archive required')
    inventory = json.loads((path / 'inventory.json').read_text())
    members = inventory['members']
    actual = {str(p.relative_to(path)) for p in path.rglob('*') if p.is_file() and p != path / 'inventory.json'}
    if actual != set(members):
        raise RuntimeError('sealed raw membership drift')
    for name, expected in members.items():
        member = path / name
        if member.is_symlink() or member.stat().st_size != expected['bytes'] or digest(member) != expected['sha256']:
            raise RuntimeError('sealed raw byte drift: ' + name)
    return {'archive': str(path), 'members': len(members), 'inventorySha256': digest(path / 'inventory.json')}


def verify_b0(project, run, role):
    if run.resolve().parent != RUN_ROOT / 'runs' or not run.name.startswith(role + '-'):
        raise RuntimeError('explicit same-role B0 required')
    build = json.loads((run / 'build-manifest.json').read_text())
    inputs = checked_inputs(project)
    source = source_inventory(project)
    if build['b0'] != 'closed' or build['role'] != role or build['source'] != source or build['source_candidate_sha256'] != candidate(source):
        raise RuntimeError('closed B0/source mismatch')
    if build['sourceInputsSha256'] != inputs['sourceInputsSha256']:
        raise RuntimeError('B0 frozen-input mismatch')
    for name, item in build['binaries'].items():
        if digest(RUN_ROOT / 'build' / role / item['path']) != item['sha256']:
            raise RuntimeError('B0 binary drift: ' + name)
    return {'b0': 'closed', 'run': str(run), 'sourceCandidate': build['source_candidate_sha256'], 'binaries': build['binaries']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=pathlib.Path)
    parser.add_argument('--project-root', type=pathlib.Path)
    parser.add_argument('--b0-run', type=pathlib.Path)
    parser.add_argument('--role', choices=['dev', 'qa'])
    args = parser.parse_args()
    result = {}
    if args.archive:
        result['archive'] = verify_archive(args.archive)
    if args.b0_run:
        if args.project_root is None or args.role is None or args.project_root.resolve() != pathlib.Path(__file__).resolve().parents[1]:
            raise RuntimeError('explicit formal project and role required')
        result['build'] = verify_b0(args.project_root.resolve(), args.b0_run.resolve(), args.role)
    if not result:
        parser.print_help()
        return 0
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
