#!/usr/bin/env python3
"""Fail closed if Git's tree cannot be represented on a case-insensitive filesystem."""
import argparse
import subprocess
import sys
import unicodedata


def collisions(paths):
    groups = {}
    for path in paths:
        key = unicodedata.normalize('NFC', path).casefold()
        groups.setdefault(key, set()).add(path)
    return [tuple(sorted(group)) for group in groups.values() if len(group) > 1]


def tracked_paths(ref):
    output = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', ref])
    return [p.decode('utf-8', 'surrogateescape') for p in output.split(b'\0') if p]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ref', default='HEAD')
    args = parser.parse_args()
    try:
        found = collisions(tracked_paths(args.ref))
    except (subprocess.CalledProcessError, OSError, UnicodeError) as exc:
        print(f'CASEFOLD_AUDIT_ERROR: {exc}', file=sys.stderr)
        return 2
    for group in sorted(found):
        print('CASEFOLD_COLLISION: ' + ' | '.join(group))
    print(f'casefold_collision_groups={len(found)}')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
