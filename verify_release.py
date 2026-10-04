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
    # ★ 反方向检查（2026-10-04 增加）：**盘上文件 → 清单**。
    #   原先只做"清单 → 文件"（缺件 / 哈希不符），因此**多了文件而清单没登记**时它照样是绿的。
    #   本轮实测正是这种情况的后果之一：`02_release_data/t1d_valext_20261002/` 在盘上有 41 件
    #   而清单没有，评审在 GitHub 上看不到该目录，也无法判断"它该不该在"。
    #   规范：盘上每个常规文件都必须有清单条目；**有意不入册的**在 EXEMPT 里逐条写明理由。
    EXEMPT = {
        'MANIFEST_sha256.csv': 'the manifest itself',
        '.gitattributes': 'git plumbing, not a released artefact',
        '01_paper/P2_English_submission_blind_v1.pdf': 'submitted PDF; its Word source is registered',
        '01_paper/P2_Supplementary_English_v0.1.pdf': 'PDF as built; its Markdown source is registered',
        '02_release_data/g6_coverage.txt': 'derived coverage note; its generator is registered',
        'work/build_provenance.py': 'helper script, source-side only',
        'work/gap_mechanism_20260916.txt': 'working note, source-side only',
    }
    listed = set()
    with io.open(MAN, encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            listed.add(row['path'].replace('\\', '/'))
    unlisted = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), HERE).replace(os.sep, '/')
            if rel in listed or rel in EXEMPT:
                continue
            unlisted.append(rel)
    print('unlisted files on disk: %d (declared exemptions: %d)' % (len(unlisted), len(EXEMPT)))
    for rel in sorted(unlisted)[:20]:
        print('  UNLISTED %s' % rel)
    if unlisted:
        bad.append(('<unlisted>', '%d file(s)' % len(unlisted), 'a manifest entry or a declared exemption'))

    print('VERIFY: OK' if not bad else 'VERIFY: %d file(s) failed' % len(bad))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
