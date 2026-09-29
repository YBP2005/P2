# -*- coding: utf-8 -*-
"""同一样本上的**阈值对照**：把 mAP50-95 与 mAP75 的兑现率限制在**同一批 40 个 run**上比。

口径两边都照正文 Table 4（`work/item2_final_v2_20260925.py` 判定过的口径）：
    prem_val  = 逐 epoch argmax − 末轮（mAP50-95 来自各 run `results.csv`；
                mAP75 用本次 2026-09-28 重评的 **best.pt − last.pt**，因为归档里没有 mAP75 的逐 epoch 读数）
    prem_test = best.pt − last.pt 的 **test** 读数（mAP50-95 来自 matrix/x4fill/x4；mAP75 来自 09-27 的 test 半列）
本脚本只做"同一批 run 上的阈值对照"，不改任何印刷值。
"""
import csv
import glob
import io
import os
import re
import statistics as st
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
REL = r'E:\workplace\_release_github\02_release_data'
XEV = r'E:\workplace\xeval_20260916'
AIN = r'E:\workplace\aitod20_n10_20260924'
X4F = r'E:\workplace\x4fill_20260925\x4fill_20260925.csv'
HERE = r'E:\Edu_workplace\scratch'
rd = lambda p: list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))

FAM = [('shwd2sf', 'base'), ('shwd2sf', 'strat'), ('smoke2sf', 'base'), ('smoke2sf', 'strat')]
MINE = [('shwd2sf', 'base', 'r10_shwd2sf_base100_3way_s%dn'), ('shwd2sf', 'strat', 'r10_shwd2sf_lr005_100ep_3way_s%dn'),
        ('smoke2sf', 'base', 'r10_smoke2sf_base100_3way_s%dn'), ('smoke2sf', 'strat', 'r10_smoke2sf_lr005_100ep_3way_s%dn')]
RUNS = [(c, a, t % s) for c, a, t in MINE for s in range(42, 52)]
print('本批 40 run：%d' % len(RUNS))

# ---- mAP50-95 侧 ----
val95 = {}
for f in glob.glob(os.path.join(XEV, 'runs', '*results.csv')):
    nm = os.path.basename(f).replace('_results.csv', '')
    rows = rd(f)
    if not rows:
        continue
    c = next((x for x in rows[0] if 'mAP50-95' in x and '(B)' in x), None)
    if c is None:
        continue
    v = [float(x[c]) * 100 for x in rows]
    val95[nm] = max(v) - v[-1]
t95 = {}
for r in rd(os.path.join(REL, 'matrix.csv')):
    if r['split'] == 'test':
        t95.setdefault(r['run'], {})[r['ckpt']] = float(r['map50_95'])
for f in (os.path.join(AIN, 'x4_teval.csv'), X4F):
    if os.path.exists(f):
        for r in rd(f):
            if r['split'] == 'test':
                t95.setdefault(r['run'], {})[r['ckpt']] = float(r['map50_95'])
test95 = {n: v['best'] - v['last'] for n, v in t95.items() if 'best' in v and 'last' in v}

# ---- mAP75 侧（本次 val 半列 + 09-27 test 半列）----
v75, t75 = {}, {}
for r in rd(os.path.join(HERE, 'b55v_summary.csv')):
    if r.get('run') and r['prem_val_best_last']:
        v75[r['run']] = float(r['prem_val_best_last'])
for fn in ('b55_m75_s0.csv', 'b55_m75_s1.csv'):
    for r in rd(os.path.join(HERE, fn)):
        if r.get('ckpt') and r.get('map75') and not str(r['map75']).startswith('FAIL'):
            t75.setdefault(r['run'], {})[r['ckpt']] = float(r['map75'])
test75 = {n: v['best'] - v['last'] for n, v in t75.items() if 'best' in v and 'last' in v}

print('mAP50-95：val %d 个 run，test %d 个；mAP75：val %d，test %d'
      % (len(val95), len(test95), len(v75), len(test75)))

print('\n## 同一批 40 run 上的逐格兑现率（%%）\n')
print('| cell | arm | n | mAP50-95 prem_val | mAP50-95 prem_test | **rate95** | mAP75 prem_val | mAP75 prem_test | **rate75** |')
print('|---|---|---|---|---|---|---|---|---|')
r95, r75 = [], []
for c, a in FAM:
    ss = [rn for cc, aa, rn in RUNS if cc == c and aa == a]
    ok95 = [(val95[rn], test95[rn]) for rn in ss if rn in val95 and rn in test95]
    ok75 = [(v75[rn], test75[rn]) for rn in ss if rn in v75 and rn in test75]
    mv95, mt95 = st.mean(x[0] for x in ok95), st.mean(x[1] for x in ok95)
    mv75, mt75 = st.mean(x[0] for x in ok75), st.mean(x[1] for x in ok75)
    a95, a75 = 100 * mt95 / mv95, 100 * mt75 / mv75
    r95.append(a95); r75.append(a75)
    print('| %s | %s | %d/%d | %+.4f | %+.4f | **%+.1f** | %+.4f | %+.4f | **%+.1f** |'
          % (c, a, len(ok95), len(ok75), mv95, mt95, a95, mv75, mt75, a75))

V95 = st.mean([val95[rn] for _, _, rn in RUNS if rn in val95])
T95 = st.mean([test95[rn] for _, _, rn in RUNS if rn in test95])
V75 = st.mean([v75[rn] for _, _, rn in RUNS if rn in v75])
T75 = st.mean([test75[rn] for _, _, rn in RUNS if rn in test75])
print('\n| 口径 | mAP50-95 | mAP75 |')
print('|---|---|---|')
print('| 臂格中位（4 格） | %+.1f %% | %+.1f %% |' % (st.median(r95), st.median(r75)))
print('| 臂格等权（4 格均值） | %+.1f %% | %+.1f %% |' % (st.mean(r95), st.mean(r75)))
print('| run 加权（同一批 40 run） | %+.1f %% | %+.1f %% |' % (100 * T95 / V95, 100 * T75 / V75))
print('| 负的臂格数 | %d/4 | %d/4 |' % (sum(1 for x in r95 if x < 0), sum(1 for x in r75 if x < 0)))
print('\n（读法）两列的 run 集合**完全相同**（四族 × 10 种子）；差异只在阈值与 val 侧构造：'
      'mAP50-95 的 prem_val 是逐 epoch argmax（全曲线），mAP75 的 prem_val 是 best−last（归档无逐 epoch mAP75）。')
