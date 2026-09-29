# -*- coding: utf-8 -*-
"""pvalue_table_local.py — the three-convention p-value table, computed from LOCAL archives only.

Port of `work/pvalue_table.py` (2026-09-15), which reached the two pods over SSH (`import paramiko`, plaintext
root passwords) to `grep "^r10_" /workspace/sio_b_results.csv`. That dependency is what makes the table
irreproducible from the release — for a paper whose subject is evaluation validity, its own headline statistics
must be recomputable by a reader.

What changed: only the input path. The cells, the statistics and the output layout are the original ones, so the
numbers can be compared cell by cell against `analysis/r10_pvalue_table_20260915.md`. Collisions between the
three local copies of the summary csv are reported rather than silently resolved.

Writes: analysis/r10_pvalue_table_20260916_local.md
"""
import csv
import io
import itertools
import math
import os
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
D = r'D:\deepseek\analysis'
SOURCES = [os.path.join(D, 'A_results_20260915', 'workspace', 'sio_b_results.csv'),
           os.path.join(D, 'B_results_20260915', 'workspace', 'sio_b_results.csv')]
OUT = os.path.join(D, 'r10_pvalue_table_20260916_local.md')

CELLS = [
    ('smoke→SFCHD（干净协议）', 'r10_smoke2sf_base100_3way_', 'r10_smoke2sf_lr005_100ep_3way_'),
    ('SHWD→SFCHD（干净协议）', 'r10_shwd2sf_base100_3way_', 'r10_shwd2sf_lr005_100ep_3way_'),
    ('dota15→dota15 30ep', 'r10_d15d15_base30_3way_', 'r10_d15d15_lr005_30ep_3way_'),
    ('mask→mask 30ep', 'r10_mask20_base30_3way_', 'r10_mask20_lr005_30ep_3way_'),
    ('mendeley→mendeley 30ep', 'r10_mende20_base30_3way_', 'r10_mende20_lr005_30ep_3way_'),
    ('aitod→aitod 30ep', 'r10_aitod20_base30_3way_', 'r10_aitod20_lr005_30ep_3way_'),
    ('firesmoke→firesmoke 30ep', 'r10_fire_base30_3way_', 'r10_fire_lr005_30ep_3way_'),
    ('visdrone→visdrone 30ep', 'r10_vis_base30_3way_', 'r10_vis_lr005_30ep_3way_'),
    ('dota→dota 30ep', 'r10_dota_base30_3way_', 'r10_dota_lr005_30ep_3way_'),
    ('剂量 2.5×（SHWD→SFCHD）', 'r10_shwd2sf_base100_3way_', 'r10_sf_dose2p5x_100ep_'),
    ('剂量 5×（SHWD→SFCHD）', 'r10_shwd2sf_base100_3way_', 'r10_sf_dose5x_100ep_'),
    ('剂量 10×（SHWD→SFCHD）', 'r10_shwd2sf_base100_3way_', 'r10_sf_dose10x_100ep_'),
    ('剂量 20×（SHWD→SFCHD）', 'r10_shwd2sf_base100_3way_', 'r10_sf_dose20x_100ep_'),
    ('复制对 dota15→aitod', 'r10_p_d15toai_base100_3way_', 'r10_p_d15toai_lr005_100ep_3way_'),
    ('复制对 aitod→visdrone', 'r10_p_aitovis_base100_3way_', 'r10_p_aitovis_lr005_100ep_3way_'),
    ('复制对 visdrone→dota15', 'r10_p_vistod15_base100_3way_', 'r10_p_vistod15_lr005_100ep_3way_'),
    ('复制对 mask→mendeley', 'r10_p_masktomende_base100_3way_', 'r10_p_masktomende_lr005_100ep_3way_'),
    ('损失先验 sns（MAFA→mendeley）', 'r10_prior_base100_3way_', 'r10_prior_sns100_3way_'),
    ('损失先验 css（MAFA→mendeley）', 'r10_prior_base100_3way_', 'r10_prior_css100_3way_'),
    ('损失先验 pws（MAFA→mendeley）', 'r10_prior_base100_3way_', 'r10_prior_pws100_3way_'),
]


def perm_paired(d):
    n = len(d)
    obs = abs(d.mean())
    hit = tot = 0
    for signs in itertools.product([-1, 1], repeat=n):
        tot += 1
        if abs((np.array(signs) * d).mean()) >= obs - 1e-12:
            hit += 1
    return hit / tot, 2.0 / (2 ** n)


def perm_unpaired(a, b):
    n = len(a)
    pool = np.concatenate([a, b])
    obs = abs(a.mean() - b.mean())
    combos = list(itertools.combinations(range(2 * n), n))
    hit = sum(1 for c in combos
              if abs(pool[list(c)].mean() - pool[[i for i in range(2 * n) if i not in c]].mean()) >= obs - 1e-12)
    return hit / len(combos), 2.0 / math.comb(2 * n, n)


# ---- local input, with collisions reported ------------------------------------------------------
rec, origin, collisions = {}, {}, []
for path in SOURCES:
    if not os.path.exists(path):
        print('MISSING input: %s' % path)
        continue
    for row in csv.reader(io.open(path, encoding='utf-8', errors='ignore')):
        if len(row) < 7 or not row[0]:
            continue
        try:
            v = float(row[4]) * 100.0
        except ValueError:
            continue
        if row[0] in rec and rec[row[0]] != v:
            collisions.append((row[0], rec[row[0]], v, origin[row[0]], os.path.basename(os.path.dirname(path))))
        if row[0] not in rec:
            origin[row[0]] = os.path.basename(os.path.dirname(path))
        rec[row[0]] = v
print('runs read from local archives: %d' % len(rec))
print('cross-archive value collisions: %d' % len(collisions))
for c in collisions[:8]:
    print('   %s: %.3f (%s) vs %.3f (%s)' % (c[0], c[1], c[3], c[2], c[4]))

rows = []
for label, pb, ps in CELLS:
    seeds = {}
    for n, v in rec.items():
        for kind, pre in (('base', pb), ('strat', ps)):
            if n.startswith(pre):
                s = n.rsplit('_s', 1)[-1].replace('n', '')
                if s.isdigit():
                    seeds.setdefault(int(s), {})[kind] = v
    ok = sorted(s for s, d in seeds.items() if 'base' in d and 'strat' in d)
    if len(ok) < 2:
        rows.append((label, len(ok), None))
        continue
    b = np.array([seeds[s]['base'] for s in ok])
    st = np.array([seeds[s]['strat'] for s in ok])
    d = st - b
    t, pt = stats.ttest_rel(st, b)
    tw, pw = stats.ttest_ind(st, b, equal_var=False)
    pp, pmin = perm_paired(d)
    pu, pumin = perm_unpaired(st, b)
    rows.append((label, len(ok), dict(delta=d.mean(), sd=d.std(ddof=1), t=t, pt=pt, pw=pw, pp=pp,
                                      pmin=pmin, pu=pu, pumin=pumin, seeds=ok, per=list(d))))

lines = ['# 干净协议逐格 p 值表（本地归档版，2026-09-16）', '',
         '**与 `r10_pvalue_table_20260915.md` 的关系**：格、统计量与输出格式完全沿用原脚本 `work/pvalue_table.py`；',
         '唯一改动是输入——不再 SSH 到租用 pod，改读本地归档的两份 `sio_b_results.csv`。',
         '因此两表可**逐格比对**，数字应完全一致。', '',
         '输入：`%s`' % '`、`'.join(SOURCES), '',
         '| 格 | n | Δ | paired t p | **配对置换 p（下界）** | 两样本置换 p（下界） | Welch p | 逐种子 Δ |',
         '|---|---|---|---|---|---|---|---|']
for label, n, r in rows:
    if r is None:
        lines.append('| %s | %d | — | 种子不足 | | | | |' % (label, n))
        continue
    lines.append('| %s | %d | %+.3f | %.4g | **%.4g**（%.4g） | %.4g（%.4g） | %.4g | %s |'
                 % (label, n, r['delta'], r['pt'], r['pp'], r['pmin'], r['pu'], r['pumin'], r['pw'],
                    ' '.join('%+.2f' % x for x in r['per'])))
lines += ['', '跨归档同名校验：%d 处冲突（若有，见本次运行 stdout）。' % len(collisions), '']
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('wrote %s' % OUT)
for label, n, r in rows:
    if r:
        print('%-26s n=%2d Δ=%+.3f p_t=%.4g p_perm=%.4g' % (label[:26], n, r['delta'], r['pt'], r['pp']))
