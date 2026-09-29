# -*- coding: utf-8 -*-
"""G8 诊断：逐行矩阵（已印 vs 8 位编码者），按单元打印，看分歧是"逐行系统性"还是"随机噪声"。

用法：python -X utf8 work/probe_g8_matrix_20260929.py
"""
import collections
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(r'E:\workplace', 'work'))
W = r'E:\workplace'
RET = os.path.join(W, '盲审归档', '编码_G8_20260929', 'returns')
UNITS = ['release', 'protocol', 'yolo_dist', 'reported']

import importlib.util
spec = importlib.util.spec_from_file_location('kg', os.path.join(W, 'work', 'kappa_g8_20260929.py'))
# 不用 exec 整个脚本（它会打印），直接把需要的函数复制过来
base = lambda m: m.strip().strip('`').split('(')[0].strip()
MAP = {'release': {'independent_test': 'yes', 'test_gated': 'yes', 'alias': 'no', 'train_val_alias': 'no'},
       'protocol': {'independent_test': 'yes', 'test_gated': 'no', 'alias': 'no', 'train_val_alias': 'no'},
       'yolo_dist': {'clean': 'yes', 'alias': 'no', 'train_val_alias': 'no'},
       'reported': {'clean': 'yes', 'independent_test': 'yes', 'alias': 'no', 'train_val_alias': 'no',
                    'contradictory': 'no'}}
ROW_RE = re.compile(r'(?m)^\s*ROW\s+(\d+)\s*\|(.*)$')

sup = io.open(os.path.join(W, 'P2_Supplementary_English_v0.1.md'), encoding='utf-8').read()
block = re.search(r'```text\n(.*?)\n```', sup, re.S).group(1)
start = block.index('## Marking table')
printed_raw, bench = {}, {}
for line in block[start:].splitlines():
    m = re.match(r'^\|\s*(\d+)\s*\|', line)
    if not m:
        continue
    c = [x.strip() for x in line.split('|')]
    printed_raw[int(c[1])] = {u: base(c[3 + i]) for i, u in enumerate(UNITS)}
    bench[int(c[1])] = c[2]

coders = {}
for f in sorted(os.listdir(RET)):
    if not f.startswith('G8_coding_') or not f.endswith('.md'):
        continue
    name = f[len('G8_coding_'):-len('_20260929.md')]
    t = io.open(os.path.join(RET, f), encoding='utf-8').read()
    rows = {}
    for m in ROW_RE.finditer(t):
        rest = m.group(2)
        rows[int(m.group(1))] = {u: (re.search(r'%s\s*=\s*\**\s*(yes|no|unknown)' % u, rest, re.I).group(1).lower()
                                     if re.search(r'%s\s*=\s*\**\s*(yes|no|unknown)' % u, rest, re.I) else '?')
                                  for u in UNITS}
    coders[name] = rows
names = list(coders)
short = {n: n[:10] for n in names}

for u in UNITS:
    print('=' * 108)
    print('单元 %s   （已印标记折成 yes/no/unknown 后，逐行对比）' % u)
    print('=' * 108)
    print('%-3s %-22s %-18s %s' % ('#', 'benchmark', 'printed', ' | '.join('%s' % short[n] for n in names)))
    agree = collections.Counter()
    for n in range(1, 20):
        p = MAP[u].get(printed_raw[n][u], 'unknown')
        cells = [coders[c][n][u] for c in names]
        agree[p] += sum(1 for x in cells if x == p)
        print('%-3d %-22s %-8s(%s) %s' % (n, bench[n][:22], p, printed_raw[n][u][:12],
                                          '   '.join('%-3s' % x[:3] for x in cells)))
    print('  ⇒ 与已印一致格数 %d/152' % sum(agree.values()))
