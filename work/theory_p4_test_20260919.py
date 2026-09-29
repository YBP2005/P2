# -*- coding: utf-8 -*-
"""r54 — the theory's experimental outlet: test Proposition 4's quantitative prediction.

Proposition 4 (P2_理论补强_v0.1.md §2) says the selection premium is not merely *measured* but
**predictable**:

    E[premium_val] = E[max_e V(e) - V(E)]  with  V(e) = v(e) + eps_e
    => WC := E[eps_selected - eps_final] >= 0   and   realization rate = 1 - WC/E[premium_val]

Two testable consequences, both computable from the local archive (no GPU):

  P4-a  if the selection is a maximum over E noisy evaluations, WC ~ sigma* sqrt(2 ln E)
        (extreme-value scale) => the premium should grow ~linearly in the val-curve noise sigma,
        with slope of order sqrt(2 ln E).  We estimate sigma as the residual sd of the val curve
        around a centred 5-point moving average, and regress the premium on it.
  P4-b  the realization rate (= realised premium / selected premium) should *increase* with the
        val signal-to-noise near the peak.  We bin runs by sigma and compare.

Direction matters more than the exact slope: the extreme-value approximation ignores the strong
serial correlation between neighbouring epochs, so sqrt(2 ln E) is an **upper** scale, not a point
prediction, and the output says so.
"""
import csv
import glob
import io
import os
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
COL = 'metrics/mAP50-95(B)'
OUT = os.path.join(W, 'work', 'theory_p4_test_20260919.txt')
L = []


def emit(s=''):
    L.append(s)
    print(s)


def curve(path):
    with io.open(path, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    v = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
         if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    v.sort()
    return np.array([x for _, x in v], float)


def sigma_hat(v):
    """Noise scale of a smooth curve: residual sd around a centred 5-point moving average."""
    if len(v) < 7:
        return np.nan
    k = 5
    trend = np.convolve(v, np.ones(k) / k, mode='valid')
    res = v[k // 2:len(v) - k // 2] - trend
    return float(res.std(ddof=1))


def collect():
    """(label, val curve, test-of-best, test-of-last) for every run whose curves are local."""
    rows = []
    # 1. the 41 three-way runs (val curves + the 2x2 matrix)
    mat = {}
    with io.open(os.path.join(W, 'xeval_20260916', 'matrix.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            mat[(r['run'], r['ckpt'], r['split'])] = float(r['map50_95'])
    for p in glob.glob(os.path.join(W, 'xeval_20260916', 'runs', '*_results.csv')):
        run = os.path.basename(p)[:-len('_results.csv')]
        rows.append((run, curve(p), mat.get((run, 'best', 'test')), mat.get((run, 'last', 'test'))))
    # 2. the 40 escalated Tier-2 runs (val curves + our own test sweep)
    T = {}
    with io.open(os.path.join(W, 'x1_tier2_20260918', 'teval.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            T[(r['run'], r['ckpt'])] = float(r['map50_95'])
    for d in sorted(glob.glob(os.path.join(W, 'x1_tier2_20260918', 'runs', '*'))):
        run = os.path.basename(d)
        p = os.path.join(d, 'results.csv')
        if os.path.exists(p):
            rows.append((run, curve(p), T.get((run, 'best')), T.get((run, 'last'))))
    # 3. the 20 X8 runs (same-directory YAML, so no separate test side)
    for d in sorted(glob.glob(os.path.join(W, 'x8_dota15_20260918', 'runs', '*'))):
        run = os.path.basename(d)
        p = os.path.join(d, 'results.csv')
        if os.path.exists(p):
            rows.append((run, curve(p), None, None))
    return [r for r in rows if r[1].size >= 20]


def main():
    rows = collect()
    emit('=' * 96)
    emit('命题 4 的实验出口：溢价是否可被"val 曲线噪声 × 极值尺度"预测')
    emit('=' * 96)
    emit()
    emit('  参与回归的 run：%d 个（三分划 41 + 升格 40 + 同域 20）' % len(rows))
    S, P, PT, E = [], [], [], []
    for run, v, tb, tl in rows:
        s = sigma_hat(v)
        prem = float(v.max() - v[-1])
        S.append(s); P.append(prem); E.append(v.size)
        PT.append(float(tb - tl) if (tb is not None and tl is not None) else np.nan)
    S, P, PT, E = map(np.array, (S, P, PT, E))
    ok = ~np.isnan(S)
    emit('  σ̂（val 曲线残差 sd，pp）：中位 %.3f，四分位 [%.3f, %.3f]'
         % (np.median(S[ok]), np.percentile(S[ok], 25), np.percentile(S[ok], 75)))
    emit('  溢价 premium_val（pp）：中位 %.3f，四分位 [%.3f, %.3f]'
         % (np.median(P[ok]), np.percentile(P[ok], 25), np.percentile(P[ok], 75)))

    # ---- P4-a: slope of premium on sigma -------------------------------------------------
    emit()
    emit('(P4-a) premium_val ~ a + b·σ̂  （预言：b > 0，且量级为 √(2 ln E) 的上界）')
    x, y = S[ok], P[ok]
    b, a, r, p, se = stats.linregress(x, y)
    n = len(x)
    tc = stats.t.ppf(0.975, n - 2)
    emit('    n = %d  斜率 b = %.3f ± %.3f（95%% CI [%.3f, %.3f]）  截距 a = %.3f  r = %.3f  p = %.3g'
         % (n, b, tc * se, b - tc * se, b + tc * se, a, r, p))
    Ev = int(np.median(E))
    pred = np.sqrt(2 * np.log(Ev))
    emit('    评测点数 E 中位 = %d ⇒ 极值尺度 √(2 ln E) = %.2f（**上界**：相邻 epoch 高度相关，'
         '有效独立次数远小于 E）' % (Ev, pred))
    emit('    ⇒ %s' % ('斜率显著为正，方向与命题 4 的预言一致；量级 %.2f 对 上界 %.2f'
                       % (b, pred) if (p < 0.05 and b > 0) else
                       '**方向不符或未达显著，命题 4 的这一形式需要改写**'))
    emit('    相关比 b/σ̄ 的另一种读法：溢价中位 %.3f 对应 σ̂ 中位 %.3f（倍数 %.2f）'
         % (np.median(P[ok]), np.median(S[ok]), np.median(P[ok]) / np.median(S[ok])))

    # ---- P4-b: realization rate vs sigma --------------------------------------------------
    emit()
    emit('(P4-b) 兑现率是否随 σ̂ 增大而**上升**（命题 4：兑现率 = 1 − WC/premium，WC 随噪声增大）')
    m = ~np.isnan(S) & ~np.isnan(PT)
    xs, pv, pt = S[m], P[m], PT[m]
    emit('    有 test 侧读数的 run：%d 个' % m.sum())
    q = np.quantile(xs, [0, 1 / 3, 2 / 3, 1])
    emit('    %-14s %5s %10s %10s %10s' % ('σ̂ 分位', 'n', 'prem_val', 'prem_test', '兑现率'))
    for i in range(3):
        lo, hi = q[i], q[i + 1] + (1e-9 if i == 2 else 0)
        sel = (xs >= lo) & (xs <= hi)
        if sel.sum() < 3:
            continue
        emit('    %-14s %5d %10.3f %10.3f %9.1f %%'
             % ('%.3f–%.3f' % (lo, hi), sel.sum(), pv[sel].mean(), pt[sel].mean(),
                100 * pt[sel].mean() / pv[sel].mean()))
    # per-run ratio: guard against premium_val == 0 (division by zero produced a NaN and a
    # misleading verdict in the first run of this script); the rank correlation is the right
    # statistic here because the ratio is heavy-tailed.
    good = pv > 1e-9
    ratio = np.full_like(pv, np.nan)
    ratio[good] = pt[good] / pv[good]
    rs, ps = stats.spearmanr(xs[good], ratio[good])
    emit('    逐 run 的（prem_test/prem_val）与 σ̂：Spearman ρ = %+.3f，p = %.3g（n = %d）'
         % (rs, ps, good.sum()))
    emit('    ⇒ %s' % ('**σ̂ 越大、兑现率越低**——与命题 4 的推论（兑现率 = 1 − WC/premium，WC 随噪声增大）'
                       '**方向一致**' if rs < 0 else '与命题 4 的推论方向相反'))
    emit('    说明：前一轮脚本在这里除了零（有 run 的 prem_val = 0），报出 NaN 并误判为"方向相反"，已修。')

    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


main()
