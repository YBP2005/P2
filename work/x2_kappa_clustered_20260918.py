# -*- coding: utf-8 -*-
"""r50 — experiment X2 from the blind-review synthesis: re-analyse κ with clustered inference.

The panel's request (ranked #7 of the improvement suggestions, and X2 in the experiment list,
"affordable without new training: Yes"): the paper reports a through-origin slope κ = 0.734
(R² = 0.902, n = 161 (seed, epoch) points) as *the* transfer rate, from 41 runs whose 5 epochs
per run are not independent observations.  Three reviewers asked for a run-clustered or
mixed-effects fit with an interval, and stated the decision rule explicitly:

    CI comfortably excluding 0.5 and 1.0      -> §8.7 stands as written
    a wide CI (their example: [0.2, 1.2])     -> present κ as an estimate, not "κ = 0.734"

This script
  1. REPRODUCES the published number from the same two local inputs, so the re-analysis is on
     the same quantity rather than a lookalike;
  2. adds a run-clustered sandwich SE, a run-level bootstrap CI, and a within-run
     (random-intercept-style) slope;
  3. reports the arm- and cell-level fits with their cluster counts;
  4. states the verdict against the panel's rule.

Inputs (all local): xeval_20260916/{curve.csv, matrix.csv, runs/*_results.csv}
Output: work/xeval_kappa_clustered_20260918.txt  (also echoed to stdout)
"""
import csv
import io
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
D = os.path.join(W, 'xeval_20260916')
OUT = os.path.join(W, 'work', 'xeval_kappa_clustered_20260918.txt')
EPS = [0, 20, 40, 60, 80]
LINES = []


def emit(s=''):
    LINES.append(s)
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


def through_origin(x, y):
    denom = float((x * x).sum())
    k = float((x * y).sum() / denom)
    ss_tot = float((y * y).sum())
    r2 = 1 - float(((y - k * x) ** 2).sum()) / ss_tot if ss_tot > 0 else float('nan')
    return k, r2


def cluster_robust_ci(x, y, groups, alpha=0.05):
    """Sandwich SE for a through-origin slope, clustered on `groups`."""
    n = len(x)
    xx_inv = 1.0 / float((x * x).sum())
    k = xx_inv * float((x * y).sum())
    u = y - k * x
    meat = 0.0
    uniq = sorted(set(groups))
    for g in uniq:
        m = np.array([gg == g for gg in groups])
        sg = float((x[m] * u[m]).sum())
        meat += sg * sg
    G = len(uniq)
    if G < 2:
        return k, float('nan'), (float('nan'), float('nan'))
    # finite-sample correction: G/(G-1) * (n-1)/(n-p), p = 1
    corr = (G / (G - 1.0)) * ((n - 1.0) / (n - 1.0))
    var = xx_inv * xx_inv * meat * corr
    se = float(np.sqrt(var))
    # t critical with G-1 df
    from scipy import stats
    tcrit = float(stats.t.ppf(1 - alpha / 2, G - 1))
    return k, se, (k - tcrit * se, k + tcrit * se)


def cluster_bootstrap_ci(x, y, groups, n_boot=10000, seed=42):
    rng = np.random.default_rng(seed)
    uniq = sorted(set(groups))
    by = {g: np.array([gg == g for gg in groups]) for g in uniq}
    ks = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.choice(len(uniq), size=len(uniq), replace=True)
        xs, ys = [], []
        for i in pick:
            m = by[uniq[i]]
            xs.append(x[m])
            ys.append(y[m])
        X = np.concatenate(xs)
        Y = np.concatenate(ys)
        ks[b] = float((X * Y).sum() / (X * X).sum())
    return float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5)), float(ks.std())


def within_run_slope(x, y, groups):
    """Fixed-effects (random-intercept-style) estimator: demean within run, fit through origin."""
    xd = np.zeros_like(x)
    yd = np.zeros_like(y)
    for g in sorted(set(groups)):
        m = np.array([gg == g for gg in groups])
        xd[m] = x[m] - x[m].mean()
        yd[m] = y[m] - y[m].mean()
    return through_origin(xd, yd)


def main():
    CURVE, MAT = load_curve(), load_matrix()
    V, T = defaultdict(dict), defaultdict(dict)
    runs = sorted(CURVE)
    missing_val = []
    for r in runs:
        v = load_val(r)
        if v is None:
            missing_val.append(r)
            continue
        V[r] = v
        T[r] = CURVE[r]
    emit('=' * 96)
    emit('X2：κ 的聚类推断（复现 + 区间）')
    emit('=' * 96)
    emit('curve.csv：%d 个 run、%d 个 (run, epoch) test 点；runs/*_results.csv：%d 份（缺 %d）'
         % (len(CURVE), sum(len(v) for v in CURVE.values()), len(V), len(missing_val)))
    if missing_val:
        emit('  缺 val 结果文件的 run：%s' % missing_val[:5])

    DATA = []
    for (c, a) in sorted({cell_arm(r) for r in runs}):
        seeds = sorted({seed_of(r) for r in runs if cell_arm(r) == (c, a)})
        vf, tf = [], []
        for s in seeds:
            rl = [r for r in runs if cell_arm(r) == (c, a) and seed_of(r) == s]
            if not rl:
                continue
            vv = V.get(rl[0], {})
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
            for e in EPS:
                if e in V.get(r0, {}) and e in T.get(r0, {}):
                    DATA.append((c, a, s, e, V[r0][e] - VF, T[r0][e] - TF, r0))
    emit()
    emit('数据点：%d 个 (cell, arm, seed, epoch)；独立 run 数（聚类数）G = %d'
         % (len(DATA), len({d[6] for d in DATA})))
    x = np.array([d[4] for d in DATA])
    y = np.array([d[5] for d in DATA])
    groups = [d[6] for d in DATA]
    k, r2 = through_origin(x, y)
    emit()
    emit('(1) 复现论文里的数：κ = %.3f，R² = %.3f，n = %d  →  论文写 0.734 / 0.902 / 161  ⇒ %s'
         % (k, r2, len(DATA),
            '复现一致' if (abs(k - 0.734) < 0.002 and abs(r2 - 0.902) < 0.002
                          and len(DATA) == 161) else '**不一致，先查清**'))
    _, se, (lo_t, hi_t) = cluster_robust_ci(x, y, groups)
    lo_b, hi_b, sd_b = cluster_bootstrap_ci(x, y, groups)
    kw, r2w = within_run_slope(x, y, groups)
    emit()
    emit('(2) 三种口径的区间')
    emit('   %-34s %8s %10s %s' % ('口径', 'κ', 'SE', '95 % CI'))
    emit('   %-34s %8.3f %10s %s' % ('过原点 OLS（论文所用）', k, '—', '—'))
    emit('   %-34s %8.3f %10.3f [%.3f, %.3f]（聚类稳健，G-1=%d df）'
         % ('run 聚类稳健三明治 SE', k, se, lo_t, hi_t, len(set(groups)) - 1))
    emit('   %-34s %8.3f %10.3f [%.3f, %.3f]（run 级自助 10,000 次）'
         % ('run 级 bootstrap', k, sd_b, lo_b, hi_b))
    emit('   %-34s %8.3f %10s R² = %.3f（剔除 run 均值，等价随机截距）'
         % ('组内（within-run）估计', kw, '—', r2w))
    emit()
    emit('(3) 分组复核（每组的聚类数）')
    emit('   %-22s %5s %5s %9s %9s' % ('组', 'n', 'G', 'κ', 'R²'))
    for label, sel in (('全部（4 个臂格）', lambda d: True),
                       ('仅 base 臂', lambda d: d[1] == 'base'),
                       ('仅 strat 臂', lambda d: d[1] == 'strat')):
        pts = [d for d in DATA if sel(d)]
        if len(pts) < 3:
            continue
        xx = np.array([d[4] for d in pts]); yy = np.array([d[5] for d in pts])
        kk, rr = through_origin(xx, yy)
        emit('   %-22s %5d %5d %9.3f %9.3f' % (label, len(pts), len({d[6] for d in pts}), kk, rr))
    for (c, a) in sorted({(d[0], d[1]) for d in DATA}):
        pts = [d for d in DATA if d[0] == c and d[1] == a]
        if len(pts) < 3:
            continue
        xx = np.array([d[4] for d in pts]); yy = np.array([d[5] for d in pts])
        kk, rr = through_origin(xx, yy)
        emit('   %-22s %5d %5d %9.3f %9.3f' % ('%s/%s' % (c[:16], a), len(pts),
                                               len({d[6] for d in pts}), kk, rr))
    emit()
    emit('(4) 按面板给的判据下结论')
    excl = (lo_t > 0.5 and hi_t < 1.0) or (lo_b > 0.5 and hi_b < 1.0)
    wide = (hi_t - lo_t) > 0.5
    if excl and not wide:
        emit('   CI 完全落在 (0.5, 1.0) 内且不宽 ⇒ §8.7 可以照原样保留，并补上区间。')
    elif wide:
        emit('   CI 很宽（宽度 %.3f > 0.5）⇒ 按面板的要求，κ 应作为**估计**呈现，'
             '不能写成 "κ = 0.734" 这样不带不确定性的断言。' % (hi_t - lo_t))
    else:
        emit('   CI 未完全落在 (0.5, 1.0) 内 ⇒ 措辞需相应收窄。')
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(LINES) + '\n')
    emit()
    emit('已写 %s' % OUT)


if __name__ == '__main__':
    main()
