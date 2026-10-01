# -*- coding: utf-8 -*-
"""r51 — experiment X10 from the blind-review synthesis: the alias-bias audit of the registered
replication, on the val side.

Four of §9's five cells use a dataset config whose `val:` and `test:` point at the same
directory, so for those cells the metric watched during training **is** the reported metric
and the run's own log measures the selection premium directly:

        p(run) = max_e mAP50-95(e) − mAP50-95(final epoch)

The registered verdicts are paired across seeds, so the corresponding alias-bias term is the
paired difference

        d(seed) = p_baseline(seed) − p_strategy(seed),        Δ ≈ Δ_reported + d̄

i.e. how much of a cell's published Δ is the *differential* selection opportunity of the two
arms rather than the learning-rate change (GLM's formulation in the synthesis).  T1-b is
excluded by construction — its YAML separates the two keys, so its training-time metric is a
different quantity from the reported one, and a val-side term cannot bound a two-term bias
(the extract's own correction M1).

The same pass also recomputes the run arithmetic, because §9 states "70 runs were frozen …
plus a control of 10 further runs … making 80", and the run directories are the primary record.

Reads only (both trees); writes work/x10_alias_audit_20260918.txt.
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
ROOTS = [
    r'D:\deepseek\analysis\A_results_20260914\runs',
    r'D:\deepseek\analysis\A_results_20260915\workspace\runs',
    r'D:\deepseek\analysis\A_results_20260916_t1d',
    r'D:\deepseek\analysis\B_results_20260914\runs',
    r'D:\deepseek\analysis\B_results_20260915\workspace\runs',
]
OUT = r'E:\workplace\work\x10_alias_audit_20260918.txt'
COL = 'metrics/mAP50-95(B)'
CELLS = [
    ('T1-a dota15\u2192aitod', 't1a_d15toaitod', 'same directory'),
    ('T1-b aitod\u2192visdrone', 't1b_aitodtovis', 'separated'),
    ('T1-c visdrone\u2192dota15', 't1c_vistod15', 'same directory'),
    ('saturated control (mask\u2192mendeley)', 't2_mask2mende', 'same directory'),
    ('appended control C (dota\u2192dota15)', 't1d_dotatod15', 'same directory (per \u00a79)'),
]
L = []


def emit(s=''):
    L.append(s)
    print(s)


def collect():
    runs = {}
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for d in os.listdir(root):
            p = os.path.join(root, d, 'results.csv')
            if os.path.isfile(p) and d not in runs:      # first root wins; copies are identical
                runs[d] = p
    return runs


def curve(path):
    rows = list(csv.DictReader(io.open(path, encoding='utf-8', errors='ignore')))
    vals = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
            if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    return vals


def main():
    runs = collect()
    emit('=' * 100)
    emit('X10：注册复现的别名偏差审计（val 侧）+ 运行数复算')
    emit('=' * 100)
    emit('run 目录（去重后，跨 %d 个根）共 %d 个' % (len(ROOTS), len(runs)))
    emit()
    emit('(1) 运行数复算（正文 §9 称"冻结 70 + 追加 10 = 80"）')
    emit('   %-34s %6s %6s %6s %s' % ('格', 'arm', 'seeds', 'runs', 'seeds 明细'))
    total_runs = 0
    per_cell = {}
    for label, prefix, aliasing in CELLS:
        arms = defaultdict(dict)
        for name, path in runs.items():
            if not name.startswith(prefix + '_'):
                continue
            rest = name[len(prefix) + 1:]
            m = re.match(r'(.+)_s(\d+)n$', rest)
            if not m:
                continue
            arm, seed = m.group(1), int(m.group(2))
            arms[arm][seed] = path
        per_cell[label] = arms
        for arm in sorted(arms):
            seeds = sorted(arms[arm])
            total_runs += len(seeds)
            emit('   %-34s %6s %6d %6d %s' % (label, arm, len(seeds), len(seeds),
                                              '%d–%d' % (seeds[0], seeds[-1]) if seeds else ''))
    emit('   ── 合计 %d 个 run' % total_runs)
    emit()

    emit('(2) 每格的 val 侧选择溢价 p = max_e − final（%）与臂间配对差 d̄')
    emit('   %-34s %5s %8s %8s %9s %-22s %s'
         % ('格', 'n_seed', 'p_base', 'p_strat', 'd̄ (pp)', '95 % CI (bootstrap)', 'val/test'))
    results = {}
    for label, prefix, aliasing in CELLS:
        arms = per_cell[label]
        base = arms.get('base100', {})
        strat = arms.get('lr005_100ep', {})
        common = sorted(set(base) & set(strat))
        pb, ps, d = [], [], []
        for s in common:
            cb, cs = curve(base[s]), curve(strat[s])
            if len(cb) < 3 or len(cs) < 3:
                continue
            vb = [v for _, v in cb]; vs = [v for _, v in cs]
            p_b = max(vb) - vb[-1]
            p_s = max(vs) - vs[-1]
            pb.append(p_b); ps.append(p_s); d.append(p_b - p_s)
        if not d:
            emit('   %-34s %5d  （无成对数据）' % (label, 0))
            continue
        d = np.array(d)
        rng = np.random.default_rng(3)
        bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(10000)])
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        results[label] = (len(d), float(np.mean(pb)), float(np.mean(ps)), float(d.mean()),
                          lo, hi, float((bs > 0).mean()), aliasing)
        emit('   %-34s %5d %8.3f %8.3f %9.3f [%+.3f, %+.3f]  %s'
             % (label, len(d), np.mean(pb), np.mean(ps), d.mean(), lo, hi, aliasing))
    emit()
    emit('(3) 读法（GLM 的表述：Δ ≈ Δ_reported + d̄）')
    PUB = {'T1-a dota15\u2192aitod': 0.147, 'T1-b aitod\u2192visdrone': 0.168,
           'T1-c visdrone\u2192dota15': 3.727,
           'saturated control (mask\u2192mendeley)': -1.490,
           'appended control C (dota\u2192dota15)': 0.727}
    for label, (n, mb, ms, dm, lo, hi, frac, alias) in results.items():
        pub = PUB.get(label)
        if pub is None:
            continue
        if 'separated' in alias:
            emit('   %-34s 公开 Δ = %+.3f ｜ **不适用**：该格 val/test 分离，训练期看到的量'
                 % (label, pub))
            emit('   %-34s 与上报量不是同一个，val 侧项无法界定两项偏差（提取件 M1 的更正）'
                 % '')
            continue
        emit('   %-34s 公开 Δ = %+.3f ｜ d̄ = %+.3f %s ｜ Δ + d̄ = %+.3f'
             % (label, pub, dm, '（区间不含 0）' if lo > 0 or hi < 0 else '（区间含 0）',
                pub + dm))
    emit()
    emit('(4) 判据（面板给的）')
    emit('   若某格因修正跨过冻结判据边界 ⇒ 影响 §9 的头条结论；若所有 |d̄| 都很小 ⇒ §9 的裁定稳健。')
    for label, (n, mb, ms, dm, lo, hi, frac, alias) in results.items():
        if 'separated' in alias:
            continue
        emit('   %-34s |d̄| = %.3f pp %s' % (label, abs(dm),
                                            '（< 0.1 pp：对判据无实质影响）' if abs(dm) < 0.1
                                            else '（≥ 0.1 pp：需与判据边界比对）'))
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


if __name__ == '__main__':
    main()
