# -*- coding: utf-8 -*-
"""Recompute every SHA-256 in MANIFEST_sha256.csv.  Prints one line per file and a verdict.

Usage:  python verify_release.py
"""
import csv
import hashlib
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.join(HERE, 'MANIFEST_sha256.csv')


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    bad, n = [], 0
    with io.open(MAN, encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            n += 1
            p = os.path.join(HERE, row['path'])
            if not os.path.exists(p):
                bad.append((row['path'], 'MISSING', row['sha256']))
                continue
            got = sha256(p)
            if got != row['sha256']:
                bad.append((row['path'], got, row['sha256']))
    print('files checked: %d' % n)
    for path, got, want in bad:
        print('  MISMATCH %s\n    got  %s\n    want %s' % (path, got, want))
    print('VERIFY: OK' if not bad else 'VERIFY: %d file(s) failed' % len(bad))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
