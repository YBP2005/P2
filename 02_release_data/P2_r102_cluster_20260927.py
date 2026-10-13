# -*- coding: utf-8 -*-
"""r102 / change ④ (#19) — re-run the two Proposition-4 tests with CLUSTERED inference.

WHY THIS SCRIPT EXISTS
----------------------
The same submission already reports the kappa (kappa = 0.708) fit with run-clustered
(sandwich) inference, because the epochs inside a run are not independent observations
(Supplementary Table S22, note "Uncertainty").  Two other tests of the same
formalisation — the two Proposition-4 tests printed in Supplementary S11 and again in
Table S20's note and in S12 §8.6 — were reported with ordinary run-level standard
errors, i.e. **without** clustering:

  ① "inequality per run (WC > 0)":  WC = prem_val - prem_test, mean +0.463 pp,
     t = 8.34, p = 1.8e-12, sign 68/81        (work/theory_meta_and_tests_20260919.py)
  ② "rate vs val noise (terciles)": Spearman rho = -0.466, p = 1.3e-5, n = 80
                                              (work/theory_p4_test_20260919.py)

The 81 runs behind both tests are **not independent draws**: they are 9 arm-cells
(corpus x arm), each contributing 1 or 10 runs produced by one pipeline on one split
pair.  The article's own claim unit is the arm-cell ("the claim is about five
arm-cells", §8.6).  This script re-derives ① and ② from the archive and adds the
clustered reading (cluster = arm-cell) next to the published unclustered one.

READ-ONLY.  It reads the archive and prints; it writes nothing, and it does not touch
the manuscript or the supplementary.

Archive inputs (all local, all pre-existing):
  E:\\workplace\\xeval_20260916\\runs\\*_results.csv        (41 runs, per-epoch val curve)
  E:\\workplace\\xeval_20260916\\matrix.csv                 (run, ckpt, split) -> test
  E:\\workplace\\x1_tier2_20260918\\runs\\*\\results.csv    (40 runs, per-epoch val curve)
  E:\\workplace\\x1_tier2_20260918\\teval.csv               (run, ckpt) -> test

Usage:  python -X utf8 work/r102_cluster_20260927.py
"""
import csv
import glob
import io
import os
import re
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

W = r'E:\workplace'
COL = 'metrics/mAP50-95(B)'
B = 20000                      # cluster-bootstrap replicates (spec asks for >= 10,000)
SEED = 20260927
OUT = []                       # collected lines, printed at the end (no file is written)


def emit(s=''):
    OUT.append(s)
    print(s)


# ----------------------------------------------------------------- data loading
def curve(path):
    """Per-epoch val curve (pp), in epoch order."""
    with io.open(path, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    v = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
         if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    v.sort()
    return np.array([x for _, x in v], float)


def sigma_hat(v):
    """Reproduce work/theory_p4_test_20260919.py exactly: residual sd around a
    centred 5-point moving average."""
    if len(v) < 7:
        return np.nan
    k = 5
    trend = np.convolve(v, np.ones(k) / k, mode='valid')
    res = v[k // 2:len(v) - k // 2] - trend
    return float(res.std(ddof=1))


def cluster_of(run):
    """arm-cell = (corpus, arm).  The run names carry the prefix r10_ and one of the
    two suffixes '_3way_sNNn' or '_3way'; both are stripped so that the 41 three-way
    runs and the 40 escalated runs land in the same scheme."""
    r = run
    if r.startswith('r10_'):
        r = r[4:]
    r = re.sub(r'_3way_s\d+n$', '', r)
    r = re.sub(r'_3way$', '', r)
    r = re.sub(r'_s\d+n$', '', r)
    return r


def collect():
    """(run, prem_val, prem_test, sigma_hat) for every run with both sides measured.

    Exactly the runs that theory_meta_and_tests_20260919.py / theory_p4_test_20260919.py
    use for these two tests: 41 three-way runs + 40 escalated Tier-2 runs = 81."""
    rows = []

    mat = {}
    with io.open(os.path.join(W, 'xeval_20260916', 'matrix.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            mat[(r['run'], r['ckpt'], r['split'])] = float(r['map50_95'])
    for p in sorted(glob.glob(os.path.join(W, 'xeval_20260916', 'runs', '*_results.csv'))):
        run = os.path.basename(p)[:-len('_results.csv')]
        if (run, 'best', 'test') not in mat or (run, 'last', 'test') not in mat:
            continue
        v = curve(p)
        rows.append((run,
                     float(v.max() - v[-1]),
                     mat[(run, 'best', 'test')] - mat[(run, 'last', 'test')],
                     sigma_hat(v)))

    T = {}
    with io.open(os.path.join(W, 'x1_tier2_20260918', 'teval.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            T[(r['run'], r['ckpt'])] = float(r['map50_95'])
    for d in sorted(glob.glob(os.path.join(W, 'x1_tier2_20260918', 'runs', '*'))):
        run = os.path.basename(d)
        p = os.path.join(d, 'results.csv')
        if not os.path.exists(p) or (run, 'best') not in T or (run, 'last') not in T:
            continue
        v = curve(p)
        rows.append((run,
                     float(v.max() - v[-1]),
                     T[(run, 'best')] - T[(run, 'last')],
                     sigma_hat(v)))
    return rows


# --------------------------------------------------------- clustered estimators
def cluster_sandwich(x, g):
    """CR1 cluster-robust SE of the mean of x with clusters g.

    Var = (1/n^2) * sum_g ( sum_{i in g} (x_i - xbar) )^2 , finite-sample factor
    G/(G-1) * (n-1)/(n-1) is not applied beyond CR1's usual G/(G-1)."""
    x = np.asarray(x, float)
    n = len(x)
    xbar = x.mean()
    u = x - xbar
    keys = list(dict.fromkeys(g))
    G = len(keys)
    s = 0.0
    for k in keys:
        s += u[np.array([gi == k for gi in g])].sum() ** 2
    var = s / (n ** 2) * (G / (G - 1.0))
    return float(np.sqrt(var)), G


def cluster_bootstrap(x, g, stat, B=B, rng=None):
    """Bootstrap by resampling CLUSTERS with replacement; `stat` maps an index array
    to a scalar."""
    rng = rng or np.random.default_rng(SEED)
    x = np.asarray(x, float)
    keys = list(dict.fromkeys(g))
    idx_by_key = {k: np.array([i for i, gi in enumerate(g) if gi == k]) for k in keys}
    out = np.empty(B, float)
    G = len(keys)
    for b in range(B):
        pick = rng.integers(0, G, size=G)
        idx = np.concatenate([idx_by_key[keys[p]] for p in pick])
        out[b] = stat(x[idx], idx)
    return out


def boot_p(draws, null=0.0):
    """Two-sided percentile bootstrap p against `null`."""
    lo = float((draws <= null).mean())
    hi = float((draws >= null).mean())
    return max(2 * min(lo, hi), 1.0 / len(draws))


def fmt_p(p):
    if p == 0:
        return '<%.1e' % (1.0 / B)
    if p < 1e-3:
        return '%.2e' % p
    return '%.4f' % p


# ------------------------------------------------------------------- main body
def main():
    rows = collect()
    runs = [r[0] for r in rows]
    pv = np.array([r[1] for r in rows])
    pt = np.array([r[2] for r in rows])
    sg = np.array([r[3] for r in rows])
    wc = pv - pt
    cl = [cluster_of(r) for r in runs]
    keys = list(dict.fromkeys(cl))
    n = len(rows)

    emit('=' * 92)
    emit('r102 / #19 — the two Proposition-4 tests, re-derived with arm-cell clustering')
    emit('=' * 92)
    emit()
    emit('Archive read (read-only):')
    emit('  %s' % os.path.join(W, 'xeval_20260916'))
    emit('  %s' % os.path.join(W, 'x1_tier2_20260918'))
    emit()
    emit('Units: %d runs in %d arm-cell clusters (the resampling unit)' % (n, len(keys)))
    for k in keys:
        m = np.array([c == k for c in cl])
        emit('  %-28s runs %2d   prem_val mean %+.3f   prem_test mean %+.3f'
             % (k, m.sum(), pv[m].mean(), pt[m].mean()))

    # ---------------------------------------------------------------- test 1
    emit()
    emit('=' * 92)
    emit('TEST 1 — Proposition 4, inequality per run:  WC = prem_val - prem_test > 0')
    emit('=' * 92)
    emit()
    emit('[published, unclustered]  n = %d runs treated as independent' % n)
    t0, p0 = stats.ttest_rel(pv, pt)
    se0 = wc.std(ddof=1) / np.sqrt(n)
    tc0 = stats.t.ppf(0.975, n - 1)
    emit('  mean WC = %+.4f pp   sd %.4f   SE %.4f   t = %.2f   p = %s   (t df = %d)'
         % (wc.mean(), wc.std(ddof=1), se0, t0, fmt_p(p0), n - 1))
    emit('  95%% CI [%+.4f, %+.4f]   sign  prem_test smaller in %d/%d   sign-test p = %s'
         % (wc.mean() - tc0 * se0, wc.mean() + tc0 * se0,
            int((wc > 0).sum()), n,
            fmt_p(stats.binomtest(int((wc > 0).sum()), n, 0.5).pvalue)))

    emit()
    emit('[clustered]  cluster = arm-cell, G = %d' % len(keys))
    se_c, G = cluster_sandwich(wc, cl)
    t_c = wc.mean() / se_c
    p_c = 2 * stats.t.sf(abs(t_c), G - 1)
    tc_c = stats.t.ppf(0.975, G - 1)
    emit('  (a) cluster-robust (CR1 sandwich) SE = %.4f  ->  t = %.2f, p = %s  (t df = G-1 = %d)'
         % (se_c, t_c, fmt_p(p_c), G - 1))
    emit('      95%% CI [%+.4f, %+.4f]   (point estimate unchanged: %+.4f pp)'
         % (wc.mean() - tc_c * se_c, wc.mean() + tc_c * se_c, wc.mean()))

    rng = np.random.default_rng(SEED)
    draws = cluster_bootstrap(wc, cl, lambda x, i: x.mean(), rng=rng)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    emit('  (b) cluster bootstrap (B = %d, clusters resampled with replacement)' % B)
    emit('      95%% percentile CI [%+.4f, %+.4f]   bootstrap p = %s'
         % (lo, hi, fmt_p(boot_p(draws))))
    emit('      bootstrap sd of the mean = %.4f' % draws.std(ddof=1))

    cell_mean = np.array([wc[np.array([c == k for c in cl])].mean() for k in keys])
    cell_n = np.array([int(np.sum([c == k for c in cl])) for k in keys])
    emit('  (c) cluster-level reading (each arm-cell one observation, G = %d)' % G)
    emit('      cell means: %s' % ', '.join('%s %+.3f (n=%d)' % (k, v, m)
                                            for k, v, m in zip(keys, cell_mean, cell_n)))
    tc_l = stats.t.ppf(0.975, G - 1)
    se_l = cell_mean.std(ddof=1) / np.sqrt(G)
    t_l, p_l = stats.ttest_1samp(cell_mean, 0.0)
    emit('      equal-weight mean %+.4f pp, sd %.4f, SE %.4f, t = %.2f, p = %s, 95%% CI [%+.4f, %+.4f]'
         % (cell_mean.mean(), cell_mean.std(ddof=1), se_l, t_l, fmt_p(p_l),
            cell_mean.mean() - tc_l * se_l, cell_mean.mean() + tc_l * se_l))
    emit('      sign at cluster level: WC > 0 in %d/%d arm-cells   sign-test p = %s'
         % (int((cell_mean > 0).sum()), G,
            fmt_p(stats.binomtest(int((cell_mean > 0).sum()), G, 0.5).pvalue)))
    emit('      run-weighted vs arm-cell-equal differ because one arm-cell '
         '(aitod20 base30) contributes only 1 of the %d runs.' % n)

    # ---------------------------------------------------------------- test 2
    emit()
    emit('=' * 92)
    emit('TEST 2 — Proposition 4, corollary: realization rate falls as val noise sigma-hat rises')
    emit('=' * 92)
    emit()
    good = pv > 1e-9                     # the original script drops prem_val == 0
    ratio = np.full(n, np.nan)
    ratio[good] = pt[good] / pv[good]
    xs, rs_ = sg[good], ratio[good]
    cl2 = [c for c, g in zip(cl, good) if g]
    emit('[published, unclustered]  n = %d runs (1 run with prem_val = 0 dropped)' % good.sum())
    rho0, p0b = stats.spearmanr(xs, rs_)
    emit('  Spearman rho = %+.4f, p = %s, n = %d' % (rho0, fmt_p(p0b), good.sum()))
    # the published terciles are computed on all 81 runs with a test reading (the
    # NaN-mask of the original), NOT on the 80-run `good` subset, and each bin's rate
    # is a RATIO OF MEANS (`pt[sel].mean() / pv[sel].mean()`).
    q = np.quantile(sg, [0, 1 / 3, 2 / 3, 1])
    terc = []
    for i in range(3):
        lo_, hi_ = q[i], q[i + 1] + (1e-9 if i == 2 else 0)
        sel = (sg >= lo_) & (sg <= hi_)
        terc.append(100 * pt[sel].mean() / pv[sel].mean())
    emit('  terciles of the per-run rate over the %d runs with a test reading '
         '(ratio of means per bin, as published): %.1f %% / %.1f %% / %.1f %%'
         % (n, terc[0], terc[1], terc[2]))

    keys2 = list(dict.fromkeys(cl2))
    emit()
    emit('[clustered]  cluster = arm-cell, G = %d' % len(keys2))

    def rho_stat(x, i):
        # i indexes into the (x, ratio) arrays jointly; x is the resampled sigma-hat
        return stats.spearmanr(x, ratio[good][i])[0]

    rng2 = np.random.default_rng(SEED + 1)
    draws2 = cluster_bootstrap(xs, cl2, rho_stat, rng=rng2)
    lo2, hi2 = np.percentile(draws2, [2.5, 97.5])
    emit('  (a) cluster bootstrap over arm-cells (B = %d, n = %d runs per replicate)'
         % (B, good.sum()))
    emit('      95%% percentile CI [%+.4f, %+.4f]   bootstrap p = %s'
         % (lo2, hi2, fmt_p(boot_p(draws2))))
    emit('      bootstrap sd of rho = %.4f   (point estimate unchanged: %+.4f)'
         % (draws2.std(ddof=1), rho0))

    cell_sig = np.array([xs[np.array([c == k for c in cl2])].mean() for k in keys2])
    cell_rate = np.array([ratio[good][np.array([c == k for c in cl2])].mean() for k in keys2])
    cell_pv = np.array([pv[good][np.array([c == k for c in cl2])].mean() for k in keys2])
    cell_pt = np.array([pt[good][np.array([c == k for c in cl2])].mean() for k in keys2])
    rho_c, p_c2 = stats.spearmanr(cell_sig, cell_rate)
    emit('  (b) cluster-level reading (each arm-cell one observation, G = %d)' % len(keys2))
    for k, s_, r_, a_, b_ in zip(keys2, cell_sig, cell_rate, cell_pv, cell_pt):
        emit('      %-28s sigma-hat %5.3f   rate %7.1f %%   (prem_val %+.3f, prem_test %+.3f)'
             % (k, s_, 100 * r_, a_, b_))
    emit('      Spearman rho across the %d arm-cells = %+.4f, p = %s'
         % (len(keys2), rho_c, fmt_p(p_c2)))
    emit('      NOTE: G = %d is below the n the article itself asks for elsewhere'
         % len(keys2))

    # ------------------------------------------------- one-sentence draft
    emit()
    emit('=' * 92)
    emit('DRAFT SENTENCE for Supplementary S12 (one sentence, with the script name)')
    emit('=' * 92)
    emit()
    emit('  "The two Proposition-4 tests of S11 are re-read with the arm-cell as the')
    emit('   resampling unit, as the kappa fit of Table S22 already is (%d runs in %d arm-cells):'
         % (n, len(keys)))
    emit('   WC = %+.3f pp, cluster-robust 95 %% CI [%+.3f, %+.3f], p = %s'
         % (wc.mean(), wc.mean() - tc_c * se_c, wc.mean() + tc_c * se_c, fmt_p(p_c)))
    emit('   (CR1 sandwich on %d clusters; a cluster bootstrap gives [%+.3f, %+.3f]);'
         % (len(keys), lo, hi))
    emit('   the noise-rate Spearman rho = %+.3f, cluster-bootstrap 95 %% CI [%+.3f, %+.3f],'
         % (rho0, lo2, hi2))
    emit('   p = %s (work/r102_cluster_20260927.py)."'
         % fmt_p(boot_p(draws2)))
    emit()
    emit('=' * 92)
    return 0


if __name__ == '__main__':
    sys.exit(main())
