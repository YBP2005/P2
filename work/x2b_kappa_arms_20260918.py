# -*- coding: utf-8 -*-
"""r50 — follow-ups the first clustered fit made visible.

The X2 re-analysis reproduced κ = 0.734 (n = 161, R² = 0.902) exactly and gave a narrow
run-clustered interval [0.683, 0.784].  It also showed something the paper does not state:
the slope differs sharply between the two arms (base ≈ 0.53, strategy ≈ 0.77).  That is not a
claim to write down on the strength of two point estimates, so this script:

  1. computes each arm's κ with a run-clustered interval and a run-level bootstrap interval;
  2. tests the difference by resampling runs WITHIN each arm (the honest null: the two arms
     are different sets of runs, so the runs cannot be pooled);
  3. does the same for the §8.6 realization rate (the panel's rank-9 request: "add a
     bootstrap/seed-level interval"), for the declared unweighted arm-cell mean and for the
     run-weighted alternative.

Reads only local files; writes work/xeval_kappa_arms_20260918.txt.
"""
import csv
import io
import os
import re
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
D = os.path.join(W, 'xeval_20260916')
OUT = os.path.join(W, 'work', 'xeval_kappa_arms_20260918.txt')
EPS = [0, 20, 40, 60, 80]
L = []


def emit(s=''):
    L.append(s)
    print(s)


def cell_arm(run):
    x = run
    arm = 'strat' if 'lr005' in x else 'base'
    x = x.replace('_lr005_100ep', '').replace('_base100', '').replace('_base30', '')
    return re.sub(r'_s\d+n$', '', x), arm


def seed_of(run):
    m = re.search(r'_s(\d+)n$', run)
    return int(m.group(1)) if m else 0


def load_curve():
    d = defaultdict(dict)
    for line in io.open(os.path.join(D, 'curve.csv'), encoding='utf-8'):
        f = line.strip().split(',')
        if len(f) < 3 or f[0] == 'run' or f[2] == 'FAIL':
            continue
        d[f[0]][int(f[1])] = float(f[2])
    return d


def load_matrix():
    d = {}
    for line in io.open(os.path.join(D, 'matrix.csv'), encoding='utf-8'):
        f = line.strip().split(',')
        if len(f) < 4 or f[0] == 'run' or f[3] == 'FAIL':
            continue
        d[(f[0], f[1], f[2])] = float(f[3])
    return d


def load_val(run):
    p = os.path.join(D, 'runs', run + '_results.csv')
    if not os.path.exists(p):
        return None
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='ignore')))
    col = 'metrics/mAP50-95(B)'
    return {int(r['epoch']): float(r[col]) * 100 for r in rows if r.get(col) and r.get('epoch')}


def slope(x, y):
    return float((x * y).sum() / (x * x).sum())


def boot_ci(x, y, groups, n=10000, seed=7):
    rng = np.random.default_rng(seed)
    uniq = sorted(set(groups))
    by = {g: np.array([gg == g for gg in groups]) for g in uniq}
    ks = np.empty(n)
    for b in range(n):
        pick = rng.choice(len(uniq), size=len(uniq), replace=True)
        X = np.concatenate([x[by[uniq[i]]] for i in pick])
        Y = np.concatenate([y[by[uniq[i]]] for i in pick])
        ks[b] = slope(X, Y)
    return ks


def main():
    CURVE, MAT = load_curve(), load_matrix()
    runs = sorted(CURVE)
    DATA = []
    for (c, a) in sorted({cell_arm(r) for r in runs}):
        seeds = sorted({seed_of(r) for r in runs if cell_arm(r) == (c, a)})
        vf, tf = [], []
        for s in seeds:
            rl = [r for r in runs if cell_arm(r) == (c, a) and seed_of(r) == s]
            if not rl:
                continue
            vv = load_val(rl[0]) or {}
            if vv:
                vf.append(vv[max(vv)])
            if (rl[0], 'last', 'test') in MAT:
                tf.append(MAT[(rl[0], 'last', 'test')])
        if not vf or not tf:
            continue
        VF, TF = float(np.mean(vf)), float(np.mean(tf))
        for s in seeds:
            rl = [r for r in runs if cell_arm(r) == (c, a) and seed_of(r) == s]
            if not rl:
                continue
            r0 = rl[0]
            vv = load_val(r0) or {}
            for e in EPS:
                if e in vv and e in CURVE.get(r0, {}):
                    DATA.append((c, a, s, e, vv[e] - VF, CURVE[r0][e] - TF, r0))

    emit('=' * 96)
    emit('κ 的臂间差异（X2 顺带发现）+ §8.6 兑现率的自助区间')
    emit('=' * 96)
    emit()
    emit('(1) 分臂的 κ 与区间（cluster = run）')
    emit('   %-8s %5s %5s %9s   %-20s %-20s' % ('臂', 'n', 'G', 'κ', '聚类稳健 95 % CI',
                                                'bootstrap 95 % CI'))
    arm_boot, arm_data = {}, {}
    all_dat = defaultdict(list)
    for a in ('base', 'strat'):
        pts = [d for d in DATA if d[1] == a]
        x = np.array([d[4] for d in pts]); y = np.array([d[5] for d in pts])
        g = [d[6] for d in pts]
        k = slope(x, y)
        xx_inv = 1.0 / float((x * x).sum())
        u = y - k * x
        meat = 0.0
        for gg in sorted(set(g)):
            m = np.array([z == gg for z in g])
            s = float((x[m] * u[m]).sum())
            meat += s * s
        G = len(set(g))
        se = float(np.sqrt(xx_inv ** 2 * meat * (G / (G - 1.0))))
        tc = float(stats.t.ppf(0.975, G - 1))
        ks = boot_ci(x, y, g)
        arm_boot[a] = ks
        arm_data[a] = (x, y, g)
        emit('   %-8s %5d %5d %9.3f   [%.3f, %.3f]%s[%.3f, %.3f]'
             % (a, len(pts), G, k, k - tc * se, k + tc * se, ' ' * 8,
                float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5))))

    emit()
    emit('(2) 臂间差异 κ_strat − κ_base（在**各臂内部**重抽 run，不合并两臂）')
    d0 = slope(*arm_data['strat'][:2]) - slope(*arm_data['base'][:2])
    diffs = arm_boot['strat'] - arm_boot['base']
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    pexcl = float((diffs > 0).mean())
    emit('   点估计差 = %.3f（strat %.3f − base %.3f）' % (d0, slope(*arm_data['strat'][:2]),
                                                          slope(*arm_data['base'][:2])))
    emit('   bootstrap 95 %% CI = [%.3f, %.3f]；差 > 0 的比例 %.3f' % (lo, hi, pexcl))
    emit('   ⇒ %s' % ('区间不含 0：臂间差异在本数据上可区分' if lo > 0
                      else '区间含 0：**不能**据此声明臂间差异'))

    emit()
    emit('(3) §8.6 兑现率的自助区间（按 run 重抽）')
    rows = []
    for (r, ckpt, split), v in MAT.items():
        rows.append((r, ckpt, split, v))
    per = defaultdict(dict)
    for r, ckpt, split, v in rows:
        per[r][(ckpt, split)] = v
    prem = {}
    for r, d in per.items():
        if ('best', 'val') in d and ('last', 'val') in d and ('best', 'test') in d \
                and ('last', 'test') in d:
            prem[r] = (d[('best', 'val')] - d[('last', 'val')],
                       d[('best', 'test')] - d[('last', 'test')])
    emit('   有完整 best/last × val/test 的 run：%d' % len(prem))
    pv = np.array([p[0] for p in prem.values()])
    pt = np.array([p[1] for p in prem.values()])
    emit('   run 加权：prem_val 均值 %.3f pp，prem_test 均值 %.3f pp ⇒ 兑现率 %.1f %%'
         % (pv.mean(), pt.mean(), 100 * pt.mean() / pv.mean()))
    rng = np.random.default_rng(11)
    n = len(pv)
    rs = np.array([100 * pt[i].mean() / pv[i].mean()
                   for i in (rng.integers(0, n, n) for _ in range(10000))])
    emit('   run 级 bootstrap 95 %% CI = [%.1f %%, %.1f %%]（中位 %.1f %%）；'
         'P(兑现率 ≤ 0) = %.3f' % (float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5)),
                                   float(np.median(rs)), float((rs <= 0).mean())))
    # unweighted arm-cell mean (the paper's declared weighting)
    cells = defaultdict(list)
    for r, (a, b) in prem.items():
        cells[cell_arm(r)].append((a, b))
    mv = np.mean([np.mean([x for x, _ in v]) for v in cells.values()])
    mt = np.mean([np.mean([y for _, y in v]) for v in cells.values()])
    emit('   臂格等权（论文声明口径）：prem_val %.3f / prem_test %.3f ⇒ 兑现率 %.1f %%'
         % (mv, mt, 100 * mt / mv))
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


if __name__ == '__main__':
    main()
