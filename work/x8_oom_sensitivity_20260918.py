# -*- coding: utf-8 -*-
"""r53 — does the X8 verdict depend on the runs that hit the CUDA-OOM fallback?

The X8 training log (local copy) records 92 "CUDA OutOfMemoryError in TaskAlignedAssigner, using
CPU" events.  They are not spread evenly: one strategy-arm run (`dota15_lr005_100ep_s51n`) carries
78 of them, and that run happens to be in the cell whose verdict the panel pre-declared a rule for.
So the honest move is to show the verdict surviving removal of the affected pairs, rather than to
mention the fallbacks in a footnote and move on.

Reported: the criterion on all 10 seeds, on each leave-one-pair-out subset (n = 9), and on the
8-seed subset that drops the two most-affected pairs (s51, s42).
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
D = os.path.join(W, 'x8_dota15_20260918', 'runs')
OOMS = os.path.join(W, 'work', 'x8_oom_counts_20260918.txt')
OUT = os.path.join(W, 'work', 'x8_oom_sensitivity_20260918.txt')
COL = 'metrics/mAP50-95(B)'
L = []


def emit(s=''):
    L.append(s)
    print(s)


def prem(name):
    p = os.path.join(D, name, 'results.csv')
    with io.open(p, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    v = [float(r[COL]) * 100 for r in rows
         if r.get(COL) and r.get(COL) not in ('', 'FAIL')]
    return max(v) - v[-1]


def summarize(d, label):
    d = np.asarray(d, float)
    n = len(d)
    m, sd = float(d.mean()), float(d.std(ddof=1))
    se = sd / np.sqrt(n)
    t = m / se
    p = float(2 * (1 - stats.t.cdf(abs(t), n - 1)))
    tc = float(stats.t.ppf(0.975, n - 1))
    lo, hi = m - tc * se, m + tc * se
    pos = int((d > 0).sum())
    ok = (m > 0) and (lo > 0) and (pos == n)
    emit('  %-34s n=%d  d̄=%+.3f  t=%.2f  p=%.4g  CI [%+.3f, %+.3f]  %d+/%d−  %s'
         % (label, n, m, t, p, lo, hi, pos, n - pos,
            '判据成立' if ok else ('**区间含 0**' if lo <= 0 else '**有反向种子**')))
    return m, lo, hi, pos, n


def main():
    oom_seed = collections.defaultdict(int)
    for line in io.open(OOMS, encoding='utf-8'):
        m = re.match(r'\s+(dota15_(?:base100|lr005_100ep)_s(\d+)n)\s+(\d+)\s*$', line)
        if m:
            oom_seed[int(m.group(2))] += int(m.group(3))
    emit('=' * 96)
    emit('X8：判据对"显存回退 run"的敏感性（先注册的判据必须经得起去掉受影响的配对）')
    emit('=' * 96)
    emit()
    emit('  日志里的 OOM 回退次数（按种子合并两臂）：%s'
         % ', '.join('s%d:%d' % (k, oom_seed[k]) for k in sorted(oom_seed)))
    emit()
    d, seeds = [], []
    for s in range(42, 52):
        pb = prem('dota15_base100_s%dn' % s)
        ps = prem('dota15_lr005_100ep_s%dn' % s)
        d.append(pb - ps)
        seeds.append(s)
    emit('  逐种子配对差：%s' % ' '.join('s%d:%+.3f' % (s, v) for s, v in zip(seeds, d)))
    emit()
    emit('(1) 全部 10 个种子')
    summarize(d, '全格')
    emit()
    emit('(2) 逐一去掉一对（n = 9）')
    lo_min, lo_max = 9, -9
    all_ok = True
    for i, s in enumerate(seeds):
        sub = [v for j, v in enumerate(d) if j != i]
        m, lo, hi, pos, n = summarize(sub, '去掉 s%d（OOM %d 次）' % (s, oom_seed.get(s, 0)))
        all_ok = all_ok and (lo > 0) and (pos == n)
        lo_min, lo_max = min(lo_min, lo), max(lo_max, lo)
    emit('    ⇒ 10 个留一子集的下界区间范围 [%+.3f, %+.3f]；%s'
         % (lo_min, lo_max, '每个子集都仍满足"正、全同号、区间不含 0"'
            if all_ok else '**有子集不满足**'))
    emit()
    emit('(3) 去掉 OOM 最多的两对（s51：78 次 + s42：7 次），n = 8')
    sub = [v for s, v in zip(seeds, d) if s not in (51, 42)]
    summarize(sub, '去掉 s51 与 s42')
    emit()
    emit('  读法：回退发生在**实现层**（该 batch 的分配器改在 CPU 上算），不改训练语义；')
    emit('  但它与并发评测造成的显存竞争同现，所以按上面的子集逐一复算判据，而不是只声明一句。')
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


main()
