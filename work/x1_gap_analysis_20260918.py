# -*- coding: utf-8 -*-
"""r53 — trace the two published Tier-2 Δgap values (−1.114 p_aitovis / −3.580 p_vistod15, n = 3)
to their sources, then evaluate the same object at n = 10.

PUBLISHED CONSTRUCTION (work/gap_mechanism_20260916.py, which produced the Tier-2 table):
    M_val(ê)  = max of the run's own val curve in results.csv                (pp)
    M_test(ê) = sio_b_results.csv field index 4 × 100                       (pp)
                — fields are (name, loss, epochs, mAP50, mAP50-95, P, R),
                  so field 4 is mAP50-95; the source is the M3 archive of the machine the
                  run was trained on: p_* runs are on A, so D:\\deepseek\\analysis\\
                  A_results_20260915\\workspace\\sio_b_results.csv
    Δgap      = mean_seed[ (M_val − M_test)_base − (M_val − M_test)_strat ]

Part 1 reproduces the two published values from those two sources — if it does not reproduce
them, the rest of this file is not comparable and must not be used.

Part 2 (only if the test-side sweep has landed) reports the same cell at n = 10 under
(a) the published construction where possible and (b) a **uniformly specified** endpoint:
our own evaluation of best.pt on the disjoint `test` split for all ten seeds
(`x1_tier2_20260918/teval.csv`).  The endpoint convention of the archive file was never
specified (manuscript §7.3, disclosed defect 3), so the n = 3 subset is computed under both
sources and the difference is printed rather than smoothed over.
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
RUNS = os.path.join(W, 'x1_tier2_20260918', 'runs')
TEVAL = os.path.join(W, 'x1_tier2_20260918', 'teval.csv')
SIO_A = r'D:\deepseek\analysis\A_results_20260915\workspace\sio_b_results.csv'
OUT = os.path.join(W, 'work', 'x1_gap_analysis_20260918.txt')
CELLS = ('p_aitovis', 'p_vistod15')
SEEDS = list(range(42, 52))
N3 = [42, 43, 44]
L = []


def emit(s=''):
    L.append(s)
    print(s)


def val_curve(run):
    p = os.path.join(RUNS, run, 'results.csv')
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    col = 'metrics/mAP50-95(B)'
    v = [float(r[col]) * 100 for r in rows if r.get(col) and r.get(col) not in ('', 'FAIL')]
    return v or None


def run_name(cell, arm, seed):
    a = 'lr005_100ep' if arm == 'strat' else 'base100'
    return 'r10_%s_%s_3way_s%dn' % (cell, a, seed)


def load_sio():
    d = {}
    if not os.path.exists(SIO_A):
        return d
    for line in io.open(SIO_A, encoding='utf-8', errors='ignore'):
        f = [x.strip() for x in line.rstrip('\n').split(',')]
        if len(f) < 7:
            continue
        try:
            d[f[0]] = float(f[4]) * 100.0
        except ValueError:
            pass
    return d


def load_teval():
    d = {}
    if not os.path.exists(TEVAL):
        return d
    with io.open(TEVAL, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                d[(r['run'], r['ckpt'])] = float(r['map50_95'])
            except (KeyError, ValueError):
                continue
    return d


def stats_block(d, label, emit_all=True):
    d = np.asarray(d, float)
    n = len(d)
    m, sd = float(d.mean()), float(d.std(ddof=1))
    se = sd / np.sqrt(n)
    t = m / se if se else float('nan')
    p = float(2 * (1 - stats.t.cdf(abs(t), n - 1)))
    tc = float(stats.t.ppf(0.975, n - 1))
    lo, hi = m - tc * se, m + tc * se
    pos = int((d > 0).sum())
    # exact sign-flip permutation over all 2^n sign patterns
    signs = np.array([[1 if (k >> i) & 1 else -1 for i in range(n)] for k in range(2 ** n)])
    perm = (np.abs((signs * d).mean(axis=1)) >= abs(m) - 1e-12).mean()
    floor = 2.0 / (2 ** n)
    if emit_all:
        emit('    n=%d  Δgap=%+.3f  sd %.3f  t=%.3f  p_t=%.4g  95%%CI [%+.3f, %+.3f]  '
             '%d+/%d−' % (n, m, sd, t, p, lo, hi, pos, n - pos))
        emit('           符号翻转置换 p=%.6f（n=%d 的可达下界 %.6f）；与 0 配对：'
             '全同号=%s' % (perm, n, floor, pos in (0, n)))
    return dict(n=n, mean=m, sd=sd, t=t, p=p, lo=lo, hi=hi, pos=pos, perm=perm, floor=floor, d=d)


def main():
    sio = load_sio()
    teval = load_teval()
    emit('=' * 98)
    emit('X1：两个 Tier-2 格的 Δgap —— 先把 n = 3 的已发表值追到源，再算 n = 10')
    emit('=' * 98)
    emit()
    emit('(1) n = 3 的已发表值能否从"本机 results.csv + A 档 sio_b_results.csv"复现')
    emit('    源：%s（存在=%s，p_* 条目=%d）'
         % (SIO_A, os.path.exists(SIO_A), sum(1 for k in sio if k.startswith('r10_p_'))))
    pub = {}
    for cell in CELLS:
        mv = collections.defaultdict(list)
        mt = collections.defaultdict(list)
        for s in N3:
            for arm in ('base', 'strat'):
                rn = run_name(cell, arm, s)
                vc = val_curve(rn)
                if vc is None:
                    emit('    !! 缺本地 results.csv：%s' % rn)
                    continue
                mv[arm].append(max(vc))
                mt[arm].append(sio.get(rn, float('nan')))
        mvb, mvs = float(np.mean(mv['base'])), float(np.mean(mv['strat']))
        mtb, mts = float(np.mean(mt['base'])), float(np.mean(mt['strat']))
        d = [(mv['base'][i] - mt['base'][i]) - (mv['strat'][i] - mt['strat'][i])
             for i in range(len(mv['base']))]
        pub[cell] = float(np.mean(d))
        emit()
        emit('    【%s】M_val 基线/策略 = %.2f / %.2f；M_test 基线/策略 = %.2f / %.2f'
             % (cell, mvb, mvs, mtb, mts))
        emit('        逐种子 Δgap = %s' % ' '.join('%+0.3f' % x for x in d))
        st = stats_block(d, cell)
        emit('        ⇒ n = 3 的 Δgap = %+.3f' % st['mean'])
    emit()
    emit('    正文印的是 −1.114（p_aitovis）与 −3.580（p_vistod15）。')
    for cell in CELLS:
        emit('    %-11s 复现 %+0.3f ⇒ %s' % (cell, pub[cell],
             '一致' if abs(pub[cell] - (-1.114 if cell == 'p_aitovis' else -3.580)) < 0.002
             else '**不一致：不许拿它当基线**'))

    # ---------------- part 2 -------------------------------------------------------------
    emit()
    emit('=' * 98)
    if not teval:
        emit('(2) 测试侧评测尚未到位（%s 不存在）—— 本文件到此为止。' % TEVAL)
        io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
        emit()
        emit('已写 %s' % OUT)
        return
    emit('(2) n = 10：同一批 run 的 Δgap（seeds 42–51），三种端点口径并列')
    emit('=' * 98)
    emit()
    emit('    (2.0) 先确认端点口径：本机重评 best.pt×test 是否等于 A 档 sio 的四个数')
    arch = {}
    for line in io.open(SIO_A, encoding='utf-8', errors='ignore'):
        f = [x.strip() for x in line.rstrip('\n').split(',')]
        if len(f) >= 7:
            try:
                arch[f[0]] = (float(f[3]) * 100, float(f[4]) * 100, float(f[5]) * 100,
                              float(f[6]) * 100)
            except ValueError:
                pass
    p = os.path.join(RUNS)
    dif = []
    n_cmp = 0
    for cell in CELLS:
        for s in N3:
            for arm in ('base', 'strat'):
                rn = run_name(cell, arm, s)
                if rn not in arch:
                    continue
                a = arch[rn]
                t = teval.get((rn, 'best'))
                if t is None:
                    continue
                n_cmp += 1
                dif.append(abs(a[1] - t))
    if dif:
        emit('        可比 run 数 %d；|本机 best.pt×test − 档 sio 的 mAP50-95| 最大 %.4f pp，'
             '中位 %.4f pp' % (n_cmp, max(dif), float(np.median(dif))))
        emit('        ⇒ %s'
             % ('两者一致 ⇒ 档 sio 记录的**就是 best.pt 在 test 上的评测**，'
                '于是 n = 3 与 n = 10 是同一端点口径，可以直接比'
                if max(dif) < 0.01 else
                '**有差异**：说明端点不是 best.pt×test，必须查清后再比，不许直接对接'))
    else:
        emit('        !! 没有可比 run —— 先查为什么')
    rows = {}
    for cell in CELLS:
        rows[cell] = {}
        for s in SEEDS:
            e = {}
            for arm in ('base', 'strat'):
                rn = run_name(cell, arm, s)
                vc = val_curve(rn)
                e[arm] = dict(
                    vmax=max(vc) if vc else float('nan'),
                    vfin=vc[-1] if vc else float('nan'),
                    tbest=teval.get((rn, 'best'), float('nan')),
                    tlast=teval.get((rn, 'last'), float('nan')),
                    sio=sio.get(rn, float('nan')))
            rows[cell][s] = e
        emit()
        emit('    【%s】逐种子（pp）' % cell)
        emit('      %-5s %14s %14s %14s %14s' % ('seed', 'val_max_b/s', 'test_best_b/s',
                                                 'test_last_b/s', 'sio_b/s'))
        for s in SEEDS:
            e = rows[cell][s]
            emit('      %-5d %6.2f/%6.2f %6.2f/%6.2f %6.2f/%6.2f %6.2f/%6.2f'
                 % (s, e['base']['vmax'], e['strat']['vmax'],
                    e['base']['tbest'], e['strat']['tbest'],
                    e['base']['tlast'], e['strat']['tlast'],
                    e['base']['sio'], e['strat']['sio']))
    variants = collections.defaultdict(dict)
    for cell in CELLS:
        for name, key in (('① Vmax(val) − best.pt(test)', 'tbest'),
                          ('② Vmax(val) − last.pt(test)', 'tlast'),
                          ('③ Vmax(val) − 档 sio（仅 42–44 有）', 'sio'),
                          ('④ best.pt(val侧最大) − best.pt(test)', None)):
            d, dd = [], []
            for s in SEEDS:
                e = rows[cell][s]
                if key is not None:
                    if np.isnan(e['base'][key]) or np.isnan(e['strat'][key]):
                        continue
                    d.append((e['base']['vmax'] - e['base'][key])
                             - (e['strat']['vmax'] - e['strat'][key]))
                else:
                    pass
            if len(d) >= 3:
                variants[cell][name] = stats_block(d, name, emit_all=False)
    emit()
    emit('    三种口径的 n = 10 结果：')
    for name in ('① Vmax(val) − best.pt(test)', '② Vmax(val) − last.pt(test)'):
        emit()
        emit('    %s' % name)
        for cell in CELLS:
            v = variants[cell].get(name)
            if not v:
                emit('      %-11s 数据不足' % cell)
                continue
            emit('      %-11s Δgap=%+.3f  t=%.3f  p_t=%.4g  CI [%+.3f, %+.3f]  %d+/%d−  '
                 '置换 p=%.6f' % (cell, v['mean'], v['t'], v['p'], v['lo'], v['hi'],
                                  v['pos'], v['n'] - v['pos'], v['perm']))
    emit()
    emit('    同一口径下限制到旧的三个种子（42–44），以便与已发表的 n = 3 直接比：')
    for cell in CELLS:
        for name, key in (('①best', 'tbest'), ('②last', 'tlast'), ('③sio', 'sio')):
            d = []
            for s in N3:
                e = rows[cell][s]
                if np.isnan(e['base'][key]) or np.isnan(e['strat'][key]):
                    continue
                d.append((e['base']['vmax'] - e['base'][key])
                         - (e['strat']['vmax'] - e['strat'][key]))
            if len(d) == 3:
                emit('      %-11s %s源 n=3：Δgap=%+.3f（逐种子 %s）'
                     % (cell, name, float(np.mean(d)), ' '.join('%+0.2f' % x for x in d)))
    emit()
    emit('    注：n = 10 的"报告端点"口径用 ①（best.pt 的 test 实测），因为它是**唯一**在全部')
    emit('        十个种子上都口径明确、同机同协议测出的端点；archive sio 只覆盖 42–44，且其')
    emit('        端点约定从未被写清（§7.3 已披露的缺陷 3）。三者的差值已在上表列出。')
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


main()
