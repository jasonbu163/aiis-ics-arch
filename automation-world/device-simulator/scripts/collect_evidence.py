#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将明确的r5角色run原件持久封存并二次核SHA；裸入口只显示帮助。"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil

RUN_ROOT = pathlib.Path('/private/tmp/arch-aw-005-r5-exec')
ARCHIVE = pathlib.Path('/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(run):
    run = run.resolve()
    if run.parent != RUN_ROOT / 'runs' or not re.fullmatch(r'(dev|qa)-\d{4}', run.name):
        raise RuntimeError('only an explicit approved role run may be sealed')
    role, number = run.name.split('-')
    destination = ARCHIVE / (role + '-run-' + number)
    if destination.exists():
        raise RuntimeError('archive already exists; sealed evidence is immutable')
    members = {}
    for path in sorted(run.rglob('*')):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise RuntimeError('non-regular raw member: ' + str(path))
        if path.is_file():
            members[str(path.relative_to(run))] = {'sha256': digest(path), 'bytes': path.stat().st_size}
    if not members:
        raise RuntimeError('empty run is not evidence')
    destination.mkdir(parents=True)
    for name, expected in members.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / name, target)
        if digest(target) != expected['sha256']:
            raise RuntimeError('archive copy mismatch: ' + name)
    inventory = {'taskId': 'ARCH-AW-005', 'revision': 'r5', 'role': role,
                 'sourceRun': str(run), 'archive': str(destination), 'members': members}
    (destination / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    # 独立第二遍从持久目录重读，不把临时hash当持久化证明。
    for name, expected in members.items():
        if digest(destination / name) != expected['sha256'] or digest(run / name) != expected['sha256']:
            raise RuntimeError('post-copy source/archive drift: ' + name)
    return {'archive': str(destination), 'members': len(members),
            'inventorySha256': digest(destination / 'inventory.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=pathlib.Path)
    args = parser.parse_args()
    if args.run is None:
        parser.print_help()
        return 0
    print(json.dumps(seal(args.run)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
