# -*- coding: utf-8 -*-
"""r53 — X3 addendum, with the Δgap definition the manuscript actually prints.

WHY THIS EXISTS.  The first X3 pass (work/x3_perepoch_analysis_20260918.py) computed part (3)
from the κ regression's own variables ΔV(e) = V(e) − V(final) and ΔT(e) = T(e) − T(final).
At e = final those are identically zero, so that quantity is 0 at the last epoch **by
construction** and flips sign near the end for purely arithmetic reasons.  Read as "Δgap(e)"
it would have produced the wrong headline ("both cells flip ⇒ narrow the stability claim").

The quantity §5.1/§8.7 print is the **raw arm difference at a common evaluation point**:

    val_diff(e)  = mean_seeds[ V_base(e) ]  − mean_seeds[ V_strat(e) ]
    test_diff(e) = mean_seeds[ T_base(e) ]  − mean_seeds[ T_strat(e) ]
    Δgap(e)      = val_diff(e) − test_diff(e)          (§8.7's printed object)

which is what work/xeval_curve_analyze_20260916.py section (3) computed on four sampled epochs.
This script recomputes that object on **every** epoch (20 per run, 1 run has 6), so §8.7's
stability claim can be re-read on the full curve, and it re-derives the arm difference in κ with
the within-arm run-clustered inference that r50 introduced.

It also (a) re-checks the 175-point overlap of this sweep against the locally archived
xeval_20260916/curve.csv (free same-machine reproducibility evidence), and (b) dumps the mean
trajectories needed to replace the sampled-grid figure.

Inputs (all local):
  xeval_perepoch_20260918/matrix_perepoch.csv   the sweep (pulled, sha256-verified on the pod)
  xeval_20260916/curve.csv                      four-epoch test curve, already archived
  xeval_20260916/matrix.csv                     best/last × val/test, already archived
  xeval_20260916/runs/<run>_results.csv         the val curves
Output: work/x3b_perepoch_corrected_20260918.txt
"""
import collections
import csv
import io
import os
import re
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
D = os.path.join(W, 'xeval_perepoch_20260918')
OLD = os.path.join(W, 'xeval_20260916')
OUT = os.path.join(W, 'work', 'x3b_perepoch_corrected_20260918.txt')
TRJ = os.path.join(W, 'work', 'x3b_trajectories_20260918.csv')
HEAD = ('shwd2sf', 'smoke2sf')
L = []


def emit(s=''):
    L.append(s)
    print(s)


def cell_arm(run):
    a = 'strat' if 'lr005' in run else 'base'
    x = run.replace('_lr005_100ep', '').replace('_base100', '').replace('_base30', '')
    x = re.sub(r'_s\d+n$', '', x)
    return re.sub(r'^r10_', '', x).replace('_3way', ''), a


def seed_of(run):
    m = re.search(r'_s(\d+)n$', run)
    return int(m.group(1)) if m else 0


def load_perepoch():
    d = collections.defaultdict(dict)
    with io.open(os.path.join(D, 'matrix_perepoch.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                d[r['run']][int(r['epoch'])] = float(r['map50_95'])
            except (KeyError, ValueError):
                continue
    return d


def load_simple(path, key_epoch=True):
    d = collections.defaultdict(dict)
    with io.open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                if key_epoch:
                    d[r['run']][int(r['epoch'])] = float(r['map50_95'])
                else:
                    d[(r['run'], r['ckpt'], r['split'])] = float(r['map50_95'])
            except (KeyError, ValueError):
                continue
    return d


def load_val(run):
    p = os.path.join(OLD, 'runs', run + '_results.csv')
    if not os.path.exists(p):
        return {}
    with io.open(p, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        v = r.get('metrics/mAP50-95(B)')
        if r.get('epoch') and v not in (None, '', 'FAIL'):
            try:
                out[int(r['epoch'])] = float(v) * 100
            except ValueError:
                pass
    return out


def slope(x, y):
    return float((x * y).sum() / (x * x).sum())


def cluster_se(x, y, groups):
    k = slope(x, y)
    xx_inv = 1.0 / float((x * x).sum())
    u = y - k * x
    meat = 0.0
    for g in sorted(set(groups)):
        m = np.array([gg == g for gg in groups])
        s = float((x[m] * u[m]).sum())
        meat += s * s
    G = len(set(groups))
    return k, float(np.sqrt(xx_inv ** 2 * meat * (G / (G - 1.0)))), G


def boot_slope(x, y, groups, n=10000, seed=7):
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
    T = load_perepoch()
    runs = sorted(T)
    emit('=' * 96)
    emit('X3 补算：用**正文印的那个 Δgap 定义**在整条曲线上重算（修正首轮的归一化误用）')
    emit('=' * 96)
    emit()
    emit('输入的 run 数 %d，(run, epoch) 点 %d 个' % (len(runs), sum(len(v) for v in T.values())))

    # ---------- (A) overlap reproducibility vs the archived 4-epoch curve -----------------
    emit()
    emit('(A) 与已归档 xeval_20260916/curve.csv 的重叠点复核（同机、同协议、两次独立评测）')
    OLD_C = load_simple(os.path.join(OLD, 'curve.csv'))
    pairs = []
    for r in runs:
        for e, v in T[r].items():
            if e in OLD_C.get(r, {}):
                pairs.append((r, e, v, OLD_C[r][e]))
    if pairs:
        dif = np.array([abs(a[2] - a[3]) for a in pairs])
        emit('    重叠 (run, epoch) 点 %d 个；|差| 最大 %.4f pp，中位 %.4f pp，'
             '完全相同 %d/%d' % (len(pairs), dif.max(), float(np.median(dif)),
                                 int((dif == 0).sum()), len(pairs)))
        emit('    ⇒ %s' % ('两次评测在重叠点上一致（自由复现证据）' if dif.max() < 0.01
                           else '**有差异**：需要说明评测的非确定性来源'))
    else:
        emit('    !! 无重叠点 —— 检查旧归档是否同一批 run')

    # ---------- (B) Δgap(e) on every epoch ------------------------------------------------
    emit()
    emit('(B) 逐 epoch 的 Δgap(e)（原式：val 臂间差 − test 臂间差；未作末轮归一化）')
    by = collections.defaultdict(lambda: collections.defaultdict(dict))   # cell -> arm -> seed -> ep
    val = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in runs:
        c, a = cell_arm(r)
        by[c][a][seed_of(r)] = T[r]
        val[c][a][seed_of(r)] = load_val(r)
    summary = {}
    for c in sorted(by):
        base, strat = by[c].get('base', {}), by[c].get('strat', {})
        if not base or not strat:
            continue
        eps = sorted(set.intersection(*[set(v) for v in list(base.values()) + list(strat.values())])
                     if base and strat else set())
        if not eps:
            eps = sorted(set.union(*[set(v) for v in list(base.values()) + list(strat.values())]))
        rows = []
        for e in eps:
            vb = [base[s][e] for s in base if e in base[s]]
            vs = [strat[s][e] for s in strat if e in strat[s]]
            vdiff = float(np.mean(vb)) - float(np.mean(vs))
            # val side, same seeds / same epoch
            vvb = [val[c]['base'][s][e] for s in base if e in val[c]['base'].get(s, {})]
            vvs = [val[c]['strat'][s][e] for s in strat if e in val[c]['strat'].get(s, {})]
            if not vvb or not vvs:
                continue
            vdiff_v = float(np.mean(vvb)) - float(np.mean(vvs))
            rows.append((e, vdiff_v, vdiff, vdiff_v - vdiff))
        emit()
        emit('    【%s】%d 个 epoch' % (c, len(rows)))
        emit('      %5s %12s %12s %12s %6s' % ('epoch', 'val臂间差', 'test臂间差', 'Δgap(e)', '符号'))
        for e, vd, td, g in rows:
            emit('      %5d %+12.3f %+12.3f %+12.3f %6s' % (e, vd, td, g, '+' if g > 0 else '−'))
        gs = np.array([r[3] for r in rows])
        allpos, allneg = bool((gs > 0).all()), bool((gs < 0).all())
        emit('      ⇒ %s（正 %d / 负 %d；最小 %+.3f，最大 %+.3f）'
             % ('**每个 epoch 同号**' if (allpos or allneg) else '**有翻转**',
                int((gs > 0).sum()), int((gs < 0).sum()), gs.min(), gs.max()))
        summary[c] = rows

    # ---------- (C) the reported endpoints, so the curve can be tied to §5.1's table ------
    emit()
    emit('(C) 同一批 run 在**报告端点**上的 Δgap（= §5.1 Table 2 的构造），用于把曲线接回正文')
    MAT = load_simple(os.path.join(OLD, 'matrix.csv'), key_epoch=False)
    rpt = []
    for c in HEAD:
        for ck in ('best', 'last'):
            vals, tests = [], []
            for s in sorted(by[c].get('base', {})):
                rb = [r for r in runs if cell_arm(r) == (c, 'base') and seed_of(r) == s]
                rs = [r for r in runs if cell_arm(r) == (c, 'strat') and seed_of(r) == s]
                if not rb or not rs:
                    continue
                if (rb[0], ck, 'val') in MAT and (rb[0], ck, 'test') in MAT \
                   and (rs[0], ck, 'val') in MAT and (rs[0], ck, 'test') in MAT:
                    vals.append(MAT[(rb[0], ck, 'val')] - MAT[(rs[0], ck, 'val')])
                    tests.append(MAT[(rb[0], ck, 'test')] - MAT[(rs[0], ck, 'test')])
            if vals:
                emit('    %-10s ckpt=%-4s n=%d  val臂间差 %+.3f  test臂间差 %+.3f  Δgap %+.3f'
                     % (c, ck, len(vals), float(np.mean(vals)), float(np.mean(tests)),
                        float(np.mean(vals)) - float(np.mean(tests))))
                rpt.append((c, ck, float(np.mean(vals)) - float(np.mean(tests))))
    emit('    （正文 Table 2 印的是 shwd2sf +0.779 / smoke2sf +0.461）')

    # ---------- (D) full-curve κ and the arm difference ----------------------------------
    emit()
    emit('(D) 全曲线 κ 与**臂间差异**（用 r50 的同款推断：各臂内部重抽 run，不合并两臂）')
    DATA = []
    for (c, a) in sorted({cell_arm(r) for r in runs}):
        seeds = sorted({seed_of(r) for r in runs if cell_arm(r) == (c, a)})
        vf, tf = [], []
        for s in seeds:
            rl = [r for r in runs if cell_arm(r) == (c, a) and seed_of(r) == s]
            if not rl:
                continue
            vv = load_val(rl[0])
            if vv:
                vf.append(vv[max(vv)])
            if (rl[0], 'last', 'test') in MAT:
                tf.append(MAT[(rl[0], 'last', 'test')])
        if not vf or not tf:
            continue
        VF, TF = float(np.mean(vf)), float(np.mean(tf))
        for r in runs:
            if cell_arm(r) != (c, a):
                continue
            vv = load_val(r)
            for e, t in T[r].items():
                if e in vv:
                    DATA.append((c, a, seed_of(r), e, vv[e] - VF, t - TF, r))
    if not DATA:
        sys.exit('!! 没有可用的 (ΔV, ΔT) 数据点')
    x = np.array([d[4] for d in DATA]); y = np.array([d[5] for d in DATA])
    g = [d[6] for d in DATA]
    k, se, G = cluster_se(x, y, g)
    tc = float(stats.t.ppf(0.975, G - 1))
    kb = boot_slope(x, y, g)
    emit('    全体：n = %d 点，G = %d run；κ = %.3f（R² %.3f）' % (len(DATA), G, k,
        1 - float(((y - k * x) ** 2).sum()) / float((y * y).sum())))
    emit('          run 聚类 95 %% CI [%.3f, %.3f]（SE %.3f）；bootstrap [%.3f, %.3f]'
         % (k - tc * se, k + tc * se, se, float(np.percentile(kb, 2.5)),
            float(np.percentile(kb, 97.5))))
    emit('          §8.7 印的是五点抽样的 0.734，[0.683, 0.784]（r50 补算）')
    arm = {}
    for a in ('base', 'strat'):
        pts = [d for d in DATA if d[1] == a]
        xx = np.array([d[4] for d in pts]); yy = np.array([d[5] for d in pts])
        gg = [d[6] for d in pts]
        kk, sse, GG = cluster_se(xx, yy, gg)
        tcc = float(stats.t.ppf(0.975, GG - 1))
        arm[a] = (xx, yy, gg, boot_slope(xx, yy, gg))
        emit('    %-6s n=%-5d G=%-4d κ = %.3f  R² %.3f  聚类 95 %% CI [%.3f, %.3f]'
             % (a, len(pts), GG, kk, 1 - float(((yy - kk * xx) ** 2).sum()) / float((yy * yy).sum()),
                kk - tcc * sse, kk + tcc * sse))
    diffs = arm['strat'][3] - arm['base'][3]
    d0 = slope(arm['strat'][0], arm['strat'][1]) - slope(arm['base'][0], arm['base'][1])
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    emit('    臂间差异 κ_strat − κ_base = %+.3f，bootstrap 95 %% CI [%+.3f, %+.3f]，'
         '差 > 0 的比例 %.3f' % (d0, lo, hi, float((diffs > 0).mean())))
    emit('    ⇒ %s' % ('区间不含 0：全曲线上臂间差异仍在' if lo > 0
                       else '**区间含 0**：全曲线上臂间差异不再可区分'))
    emit('    五点抽样下同量是 +0.237 [0.145, 0.323]（r50）')

    # ---------- (E) trajectories for the figure ------------------------------------------
    emit()
    emit('(E) 轨迹数据（每格每臂：val 与 test 的种子均值，逐 epoch）→ %s' % TRJ)
    with io.open(TRJ, 'w', encoding='utf-8', newline='\n') as f:
        f.write('cell,arm,epoch,n_seeds,val_mean,test_mean\n')
        for c in sorted(by):
            for a in ('base', 'strat'):
                if a not in by[c]:
                    continue
                seeds = sorted(by[c][a])
                eps = sorted(set.intersection(*[set(by[c][a][s]) for s in seeds])) if seeds else []
                for e in eps:
                    tv = [by[c][a][s][e] for s in seeds]
                    vv = [val[c][a][s][e] for s in seeds if e in val[c][a].get(s, {})]
                    f.write('%s,%s,%d,%d,%.4f,%.4f\n'
                            % (c, a, e, len(tv),
                               float(np.mean(vv)) if vv else float('nan'), float(np.mean(tv))))
    emit('    已写（%s）' % TRJ)

    # ---------- (F) within-run κ on the full curve ---------------------------------------
    xd = np.zeros_like(x)
    yd = np.zeros_like(y)
    for gg in sorted(set(g)):
        m = np.array([z == gg for z in g])
        xd[m] = x[m] - x[m].mean()
        yd[m] = y[m] - y[m].mean()
    kw = slope(xd, yd)
    emit()
    emit('(F) 组内（within-run，各 run 内部去均值）的 κ —— 五点抽样下的同量是 0.774')
    emit('    全曲线 κ_within = %.3f（这一版把 run 间差异整体去掉，故与上面的 0.708 不是同一估计）'
         % kw)

    # ---------- (G) replacement contents of Tables S22 / S23 ------------------------------
    emit()
    emit('(G) 供补充材料重建的两张表的数据（S22 = 分组 κ/R²；S23 = 逐 epoch 的 Δgap 符号）')
    S22 = os.path.join(W, 'work', 'x3b_tableS22_20260918.csv')
    with io.open(S22, 'w', encoding='utf-8', newline='\n') as f:
        f.write('group,n_points,n_runs,kappa,R2,ci_lo,ci_hi\n')
        for lab, pts in (('all', DATA),
                         ('baseline arm', [d for d in DATA if d[1] == 'base']),
                         ('strategy arm', [d for d in DATA if d[1] == 'strat'])):
            xx = np.array([d[4] for d in pts]); yy = np.array([d[5] for d in pts])
            gg = [d[6] for d in pts]
            kk, sse, GG = cluster_se(xx, yy, gg)
            tcc = float(stats.t.ppf(0.975, GG - 1))
            r2 = 1 - float(((yy - kk * xx) ** 2).sum()) / float((yy * yy).sum())
            f.write('%s,%d,%d,%.4f,%.4f,%.4f,%.4f\n'
                    % (lab, len(pts), GG, kk, r2, kk - tcc * sse, kk + tcc * sse))
    emit('    S22 → %s' % S22)
    S23 = os.path.join(W, 'work', 'x3b_tableS23_20260918.csv')
    with io.open(S23, 'w', encoding='utf-8', newline='\n') as f:
        f.write('cell,epoch,val_arm_diff,test_arm_diff,dgap,sign\n')
        for c in sorted(summary):
            for e, vd, td, gp in summary[c]:
                f.write('%s,%d,%.4f,%.4f,%.4f,%s\n'
                        % (c, e, vd, td, gp, 'positive' if gp > 0 else 'negative'))
    emit('    S23 → %s（每格 %d/%d 个 epoch）'
         % (S23, len(summary.get('shwd2sf', [])), len(summary.get('smoke2sf', []))))

    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


if __name__ == '__main__':
    main()
