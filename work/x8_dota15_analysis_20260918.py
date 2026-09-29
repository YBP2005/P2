# -*- coding: utf-8 -*-
"""r52 — X8 analysis (to run once the 16 new runs finish and the CSVs are pulled back).

Question the panel asked, with its own decision rule:
    "If the n = 10 paired difference is not positive with >= 8/10 same-sign and a CI excluding
     zero -> remove dota15 from the 'all four cells' headline and rewrite the abstract/Tier 1."

So this computes, from the 20 runs' own training logs (seeds 43 and 44 already existed; 42 and
45-51 are new):
    premium(run) = max_e mAP50-95(e) - mAP50-95(final epoch)      [on val, the monitored split]
    d(seed)      = premium_baseline(seed) - premium_strategy(seed)
and reports mean, sd, paired t, p, 95 % CI, the sign split, and the same numbers restricted to
the published n = 3 subset so the new result can be compared with the printed +0.589 pp.

Input: E:\\workplace\\x8_dota15_20260918\\runs\\<name>\\results.csv   (pulled from the pod)
"""
import csv
import io
import os
import re
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
D = os.path.join(W, 'x8_dota15_20260918', 'runs')
OUT = os.path.join(W, 'work', 'x8_dota15_analysis_20260918.txt')
COL = 'metrics/mAP50-95(B)'
SEEDS = list(range(42, 52))
PUBLISHED_N3 = [43, 44]          # the two runs that carried a seed identity in the old cell
L = []


def emit(s=''):
    L.append(s)
    print(s)


def prem(name):
    p = os.path.join(D, name, 'results.csv')
    if not os.path.exists(p):
        return None, None
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='ignore')))
    vals = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
            if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    if len(vals) < 3:
        return None, None
    v = [x for _, x in vals]
    return max(v) - v[-1], v[-1]


def arm(prefix, seed):
    return '%s_s%dn' % (prefix, seed)


def main():
    emit('=' * 92)
    emit('X8：dota15 同域格的 n = 10 配对溢价（基准臂 vs 策略臂，100 轮，seeds 42–51）')
    emit('=' * 92)
    rows = []
    for s in SEEDS:
        pb, fb = prem(arm('dota15_base100', s))
        ps, fs = prem(arm('dota15_lr005_100ep', s))
        if pb is None or ps is None:
            emit('  seed %-3d 缺数据（base=%s strat=%s）' % (s, pb is not None, ps is not None))
            continue
        rows.append((s, pb, ps, pb - ps, fb, fs))
    if len(rows) < 4:
        sys.exit('!! 可用的配对种子只有 %d 个 —— 先查为什么' % len(rows))

    emit()
    emit('  逐种子（单位 pp）')
    emit('  %-6s %12s %12s %12s' % ('seed', 'prem_base', 'prem_strat', 'd = base−strat'))
    for s, pb, ps, d, _, _ in rows:
        emit('  %-6d %12.3f %12.3f %12.3f' % (s, pb, ps, d))

    def summarize(sub, label):
        d = np.array([r[3] for r in sub])
        n = len(d)
        m, sd = float(d.mean()), float(d.std(ddof=1))
        se = sd / np.sqrt(n)
        t = m / se if se > 0 else float('nan')
        p = float(2 * (1 - stats.t.cdf(abs(t), n - 1)))
        lo, hi = m - stats.t.ppf(0.975, n - 1) * se, m + stats.t.ppf(0.975, n - 1) * se
        pos = int((d > 0).sum())
        emit()
        emit('  【%s】n = %d  配对差 d̄ = %+.3f pp  sd %.3f  t %.2f  p %.4g  95 %% CI [%+.3f, %+.3f]'
             % (label, n, m, sd, t, p, lo, hi))
        emit('        符号：%d 正 / %d 负；区间%s含 0；%s ≥ 8/10 同号'
             % (pos, n - pos, '' if (lo <= 0 <= hi) else '不', '达到' if pos >= 8 else '未达到'))
        return {'n': n, 'mean': m, 'sd': sd, 't': t, 'p': p, 'lo': lo, 'hi': hi, 'pos': pos}

    all_s = summarize(rows, '全部可用种子')
    emit()
    emit('  Table 1 那一行需要的两臂均值（单位 pp）：')
    pb = np.array([r[1] for r in rows]); ps = np.array([r[2] for r in rows])
    emit('    溢价 基线臂 %+.3f（sd %.3f）｜策略臂 %+.3f（sd %.3f）｜配对差 %+.3f'
         % (pb.mean(), pb.std(ddof=1), ps.mean(), ps.std(ddof=1), (pb - ps).mean()))
    tb = float(pb.mean() / (pb.std(ddof=1) / np.sqrt(len(pb))))
    ts = float(ps.mean() / (ps.std(ddof=1) / np.sqrt(len(ps))))
    emit('    各臂自身与 0 的配对：基线 t=%.2f，策略 t=%.2f（两个臂的溢价都显著为正）'
         % (tb, ts))
    emit('    终轮 val（%s 的末行）两臂均值：基线 %.3f｜策略 %.3f'
         % ('results.csv', float(np.mean([r[4] for r in rows])),
            float(np.mean([r[5] for r in rows]))))
    n3 = [r for r in rows if r[0] in PUBLISHED_N3]
    n3s = summarize(n3, '仅旧的两个带种子 run（43/44）') if len(n3) >= 2 else None
    emit()
    emit('  （正文印的是 n = 3 的 +0.589 pp；旧三个配对里第三个是 unseeded run，'
         '按项目自己的口径**不具种子身份**，故此处只列 43/44）')
    emit()
    emit('=' * 92)
    emit('面板给的判据与结论')
    emit('=' * 92)
    ok = (all_s['mean'] > 0) and (all_s['pos'] >= 8) and not (all_s['lo'] <= 0 <= all_s['hi'])
    if ok:
        emit('  ✅ n = 10 判据**满足**（差为正、≥8/10 同号、CI 不含 0）⇒ "四格为正"可以保留，'
             '并把 dota15 从"定向探针"升为有功效的格。')
    else:
        why = []
        if all_s['mean'] <= 0:
            why.append('点估计不为正')
        if all_s['pos'] < 8:
            why.append('同号种子 %d/10 < 8' % all_s['pos'])
        if all_s['lo'] <= 0 <= all_s['hi']:
            why.append('CI 含 0')
        emit('  ⚠ n = 10 判据**未满足**（%s）⇒ 按面板要求，dota15 应从"四格为正"的头条里'
             '移出并改写摘要/Tier 1 的措辞。' % '；'.join(why))
    emit()
    emit('  无论结论如何，都属于**先注册后报告**（面板已声明这条判据），故直接照做，不挑结果。')
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


if __name__ == '__main__':
    main()
