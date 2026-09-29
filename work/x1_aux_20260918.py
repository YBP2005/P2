# -*- coding: utf-8 -*-
"""r53 — the X1 auxiliary quantities, so the tables that quote these two cells can be updated
from data instead of by hand.

For each escalated cell (p_aitovis, p_vistod15) at n = 10, using
    val curve      x1_tier2_20260918/runs/<run>/results.csv          (Vmax, Vfin)
    test of best/last  x1_tier2_20260918/teval.csv                    (Tbest, Tlast)
computes:
  (1) the realization rate (§8.6's object): prem_val = Vmax − Vfin, prem_test = Tbest − Tlast,
      per arm, run-weighted mean and arm-cell-equal mean;
  (2) the exact three-component decomposition of Δgap (§5.6, supplementary Table S10):
      Δgap = (final-epoch val arm diff) + Δ(selection optimism) − (test arm diff);
  (3) the mechanism checks that §5.6's Table S9 rests on, re-verified on the n = 10 vintage:
      M1 (multiplicative gain ⇒ Δgap same sign as the raw baseline gap) and
      M4 (a cell whose strategy is better on test cannot have Δgap < 0).
"""
import csv
import io
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
RUNS = os.path.join(W, 'x1_tier2_20260918', 'runs')
TEVAL = os.path.join(W, 'x1_tier2_20260918', 'teval.csv')
OUT = os.path.join(W, 'work', 'x1_aux_20260918.txt')
CELLS = ('p_aitovis', 'p_vistod15')
SEEDS = list(range(42, 52))
L = []


def emit(s=''):
    L.append(s)
    print(s)


def vcurve(run):
    with io.open(os.path.join(RUNS, run, 'results.csv'), encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    col = 'metrics/mAP50-95(B)'
    return [float(r[col]) * 100 for r in rows if r.get(col) and r.get(col) not in ('', 'FAIL')]


def rn(cell, arm, s):
    return 'r10_%s_%s_3way_s%dn' % (cell, 'lr005_100ep' if arm == 'strat' else 'base100', s)


def main():
    T = {}
    with io.open(TEVAL, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            T[(r['run'], r['ckpt'])] = float(r['map50_95'])
    emit('=' * 92)
    emit('X1 附随量：兑现率、Δgap 三分量分解、§5.6 机制判定的 n = 10 复核')
    emit('=' * 92)
    emit()
    emit('(1) §8.6 的兑现率（prem_val = Vmax − Vfin；prem_test = Tbest − Tlast），两格 × 两臂，n = 10')
    emit('    %-12s %-6s %10s %10s %10s %10s %9s'
         % ('cell', 'arm', 'prem_val', 'prem_test', 'Vfin', 'Vmax', '兑现率'))
    allpv, allpt = [], []
    for c in CELLS:
        for arm in ('base', 'strat'):
            pv, pt = [], []
            for s in SEEDS:
                v = vcurve(rn(c, arm, s))
                pv.append(max(v) - v[-1])
                pt.append(T[(rn(c, arm, s), 'best')] - T[(rn(c, arm, s), 'last')])
            pv, pt = np.array(pv), np.array(pt)
            allpv.append(pv.mean()); allpt.append(pt.mean())
            emit('    %-12s %-6s %10.3f %10.3f %10.3f %10.3f %8.1f %%'
                 % (c, arm, pv.mean(), pt.mean(),
                    float(np.mean([vcurve(rn(c, arm, s))[-1] for s in SEEDS])),
                    float(np.mean([max(vcurve(rn(c, arm, s))) for s in SEEDS])),
                    100 * pt.mean() / pv.mean()))
    emit()
    emit('    run 加权（把两格两臂共 40 个 run 一起平均）：prem_val %.3f / prem_test %.3f ⇒ %.1f %%'
         % (np.mean(allpv), np.mean(allpt), 100 * np.mean(allpt) / np.mean(allpv)))
    emit('    臂格等权（论文声明口径）：prem_val %.3f / prem_test %.3f ⇒ %.1f %%'
         % (np.mean(allpv), np.mean(allpt), 100 * np.mean(allpt) / np.mean(allpv)))
    emit('    （论文 §8.6 在 41 个 run 上印的是 19 %%；这两格是**新加的两格**，用同一套定义算）')

    emit()
    emit('(2) Δgap 的三分量分解（恒等式：Δgap = 末轮 val 臂间差 + Δ选点乐观 − 末轮 test 臂间差）')
    emit('    依据 archive 的口径：难度差那项用的是 **last.pt 的 test**（不是 best.pt 的）：')
    emit('      Δgap = [(Vfin_b − Tlast_b) − (Vfin_s − Tlast_s)] + [(prem_val − prem_test)_b − (…)_s]')
    emit('    %-12s %9s %11s %9s %9s %9s' % ('cell', 'Δgap', '末轮val差', 'Δprem', '−test差', '校验'))
    for c in CELLS:
        dgap, dd, do_, dt = [], [], [], []
        for s in SEEDS:
            vb, vs = vcurve(rn(c, 'base', s)), vcurve(rn(c, 'strat', s))
            tbest_b, tbest_s = T[(rn(c, 'base', s), 'best')], T[(rn(c, 'strat', s), 'best')]
            tlast_b, tlast_s = T[(rn(c, 'base', s), 'last')], T[(rn(c, 'strat', s), 'last')]
            dgap.append((max(vb) - tbest_b) - (max(vs) - tbest_s))
            # (i) final-epoch val arm difference  (ii) Δ selection optimism  (iii) − final test arm difference
            dd.append(vb[-1] - vs[-1])
            do_.append(((max(vb) - vb[-1]) - (tbest_b - tlast_b))
                       - ((max(vs) - vs[-1]) - (tbest_s - tlast_s)))
            dt.append(-(tlast_b - tlast_s))
        m = lambda a: float(np.mean(a))
        emit('    %-12s %+9.3f %+11.3f %+9.3f %+9.3f %+9.3f'
             % (c, m(dgap), m(dd), m(do_), m(dt), m(dd) + m(do_) + m(dt)))
        emit('      （三分量形式 末轮val差 + Δprem − 末轮test差 = %+.3f）'
             % (m(dd) + m(do_) + m(dt)))
    emit('    ⇒ "校验"列必须等于 Δgap（恒等式），否则分解写错。')

    emit()
    emit('(3) §5.6 表 S9 的两条机制判定，在 n = 10 上复核')
    for c in CELLS:
        gb, dgap, test_diff = [], [], []
        for s in SEEDS:
            vb, vs = vcurve(rn(c, 'base', s)), vcurve(rn(c, 'strat', s))
            tb, ts = T[(rn(c, 'base', s), 'best')], T[(rn(c, 'strat', s), 'best')]
            gb.append(max(vb) - tb)
            dgap.append((max(vb) - tb) - (max(vs) - ts))
            test_diff.append(tb - ts)
        mg, md, mtd = float(np.mean(gb)), float(np.mean(dgap)), float(np.mean(test_diff))
        emit('    %-12s 基线 raw gap %+.3f；Δgap %+.3f ⇒ M1（同号？）：%s'
             % (c, mg, md, '同号 → M1 不成立' if mg * md > 0 else '异号 → 仍是 M1 的反例'))
        emit('    %-12s test 臂间差 %+.3f ⇒ %s' % ('', mtd,
             '策略在 test 上更好而 Δgap 为负 → 仍是 M4 的反例'
             if (mtd < 0 and md < 0) else '不再是 M4 的反例' if md > 0 else '策略在 test 上并不更好'))
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


main()
