# -*- coding: utf-8 -*-
"""B55 mAP75 测试半列：先做**阳性控制**（mAP50-95 必须复现稿内来源值），再给 prem_test 的 mAP75 列。

阳性控制的对照源（与论文 Table 4/其它表同源）：
  · `_release_github/02_release_data/matrix.csv`（列：run, ckpt, split, map50_95）
  · `x4fill_20260925/x4fill_20260925.csv` 与 `aitod20_n10_20260924/x4_teval.csv`
判据：|Δ| ≤ 0.005 pp（与稿内"best × test 复现归档到 0.0046 pp"同档）。
"""
import csv
import io
import os
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda p: list(csv.DictReader(io.open(p, encoding='utf-8-sig', errors='replace')))

mine = {}
for f in ('b55_m75_s0.csv', 'b55_m75_s1.csv'):
    p = os.path.join(HERE, f)
    if not os.path.exists(p):
        continue
    for r in rd(p):
        if r['ckpt'] and r['map50_95'] and not r['map50_95'].startswith('FAIL'):
            mine[(r['run'], r['ckpt'])] = (float(r['map50_95']), float(r['map50']), float(r['map75']))
print('本次评测成功读数：%d 个 (run, ckpt)' % len(mine))

ref = {}
for r in rd(os.path.join(W, '_release_github', '02_release_data', 'matrix.csv')):
    if r.get('split') == 'test':
        ref[(r['run'], r['ckpt'])] = float(r['map50_95'])
for f in (os.path.join(W, 'x4fill_20260925', 'x4fill_20260925.csv'),
          os.path.join(W, 'aitod20_n10_20260924', 'x4_teval.csv')):
    if os.path.exists(f):
        for r in rd(f):
            if r.get('split') == 'test':
                ref.setdefault((r['run'], r['ckpt']), float(r['map50_95']))

common = sorted(set(mine) & set(ref))
print('可对照的 (run, ckpt)：%d' % len(common))
if common:
    d = [mine[k][0] - ref[k] for k in common]
    ad = [abs(x) for x in d]
    print('  Δ(mAP50-95)：max %.4f pp，中位 %.4f pp，|Δ|>0.005 的 %d 个'
          % (max(ad), st.median(ad), sum(1 for x in ad if x > 0.005)))
    worst = sorted(common, key=lambda k: -abs(mine[k][0] - ref[k]))[:5]
    for k in worst:
        print('    %-46s %-4s 本机 %.4f  归档 %.4f  Δ%+.4f'
              % (k[0], k[1], mine[k][0], ref[k], mine[k][0] - ref[k]))
    print('  阳性控制：%s' % ('PASS' if max(ad) <= 0.005 else '*** FAIL ***'))

# ---- prem_test 在 mAP75 / mAP50-95 / mAP50 三个阈值上的臂格值 ----
print('\n=== prem_test = best − last（五格 + 其余在册 run）===')
cells = {}
for (run, ck) in mine:
    cells.setdefault(run, {})[ck] = mine[(run, ck)]
rows = []
for run, d in sorted(cells.items()):
    if 'best' in d and 'last' in d:
        rows.append((run, d['best'][0] - d['last'][0], d['best'][2] - d['last'][2],
                     d['best'][1] - d['last'][1]))
print('  run 数 = %d' % len(rows))
for tag, idx in (('mAP50-95', 1), ('mAP75', 2), ('mAP50', 3)):
    v = [r[idx] for r in rows]
    print('  %-9s 均值 %+0.4f pp  正 %d/%d  负 %d/%d'
          % (tag, st.mean(v), sum(1 for x in v if x > 0), len(v), sum(1 for x in v if x < 0), len(v)))
print('\n=== 按 run 名分组（同一格的同名型号）===')
grp = {}
for run, a, b, c in rows:                      # a=mAP50-95 b=mAP75 c=mAP50
    key = run.split('_3way')[0]
    grp.setdefault(key, []).append((a, b, c))
for k in sorted(grp):
    g = grp[k]
    print('  %-40s n=%2d  mAP50-95 %+0.4f   mAP75 %+0.4f (正 %d/%d)   mAP50 %+0.4f'
          % (k, len(g), st.mean(x[0] for x in g), st.mean(x[1] for x in g),
             sum(1 for x in g if x[1] > 0), len(g), st.mean(x[2] for x in g)))

out = os.path.join(HERE, 'b55_m75_summary.txt')
d = [mine[k][0] - ref[k] for k in common]
io.open(out, 'w', encoding='utf-8', newline='\n').write(
    'evaluated=%d common=%d maxabs=%.4f\n' % (len(mine), len(common),
                                              max(abs(x) for x in d) if common else -1))
print('\n摘要 → %s' % out)
