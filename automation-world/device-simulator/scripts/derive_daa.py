#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""固定DAA源码隔离暂存；不运行DAA、不覆盖正式DS，裸入口仅帮助。"""
import argparse
import hashlib
import json
import pathlib
import shutil


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive(project, root, role):
    project, root = project.resolve(), root.resolve()
    if root != pathlib.Path('/private/tmp/arch-aw-005-r5-exec'):
        raise RuntimeError('explicit approved run root required')
    repo = project.parents[1]
    record = json.loads((project / 'source-inputs.json').read_text())
    pins = record['daaDerivationPins']
    digest = hashlib.sha256(''.join(k + '\t' + pins[k] + '\n' for k in sorted(pins)).encode()).hexdigest()
    if len(pins) != 196 or digest != record['daaDerivationDigest']:
        raise RuntimeError('frozen DAA196 manifest mismatch')
    stage = root / 'stage' / role / 'daa-source'
    if stage.exists():
        raise RuntimeError('stage already exists; preserve prior bytes and inspect ownership')
    prefix = 'automation-world/data-acquisition-agent/'
    for relative, expected in pins.items():
        source = repo / relative
        if not relative.startswith(prefix) or source.is_symlink() or sha(source) != expected:
            raise RuntimeError('frozen source drift: ' + relative)
    stage.mkdir(parents=True)
    for relative, expected in pins.items():
        destination = stage / relative[len(prefix):]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / relative, destination)
        if sha(destination) != expected:
            raise RuntimeError('stage copy mismatch: ' + relative)
    result = {'taskId': 'ARCH-AW-005', 'revision': 'r5', 'role': role,
              'stage': str(stage), 'sourceCount': len(pins), 'digest': digest,
              'sourcePins': pins, 'formalProjectOverwritten': False,
              'daaRunOrBuild': False}
    (stage.parent / 'derivation.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=pathlib.Path)
    parser.add_argument('--run-root', type=pathlib.Path)
    parser.add_argument('--role', choices=['dev', 'qa'])
    args = parser.parse_args()
    if not all((args.project_root, args.run_root, args.role)):
        parser.print_help()
        return 0
    result = derive(args.project_root, args.run_root, args.role)
    print(json.dumps({k: v for k, v in result.items() if k != 'sourcePins'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
