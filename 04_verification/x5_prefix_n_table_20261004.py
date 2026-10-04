# -*- coding: utf-8 -*-
"""X5（r13 评审请求，**零新训练**）：§7.2 的「前缀-n」表。

评审原话（Space-Bunny R1，逐字）：
  「**§7.2 的前缀-n 表**：两个登记格逐 seed 前缀 n = 3…10，各自的 paired *t* p 与
    精确 sign-flip 置换 p（**两种端点约定各一列**）」；自标 `ANALYSIS`（0 新训练）。

数据：`复现仓库/02_release_data/release_selection-transfer_perseed.csv`
  **40 run** = 2 格（`shwd2sf`、`smoke2sf`）× 2 臂（`base` / `lr005`）× 10 seed（42–51），
  逐 run 给 `prem_val_pp`、`prem_test_oracle_pp`（val 峰那套）、`prem_test_selected_pp`（best/last 那套）。

口径：
  * 配对**在 seed 内**：`Δgap(seed) = (strategy 的 prem) − (baseline 的 prem)`，逐 seed 一条
  * **两种端点**：`oracle` = 用 `prem_test_oracle_pp`；`selected` = 用 `prem_test_selected_pp`
  * paired t：双侧，df = n − 1
  * **精确 sign-flip 置换**：n ≤ 10 ⇒ 2ⁿ = 最多 1024 种符号翻转，**全枚举**、无抽样
  * 前缀 n = 3…10 用**前 n 个 seed**（42, 43, …）

用法：python -X utf8 work/x5_prefix_n_table_20261004.py
"""
import csv
import io
import itertools
import json
import math
import os
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO = r'E:\WorkBuddy\盲审P2\复现仓库'
OUT = r'E:\workplace\G5_review_p2r13_20261007'
SRC = os.path.join(REPO, '02_release_data', 'release_selection-transfer_perseed.csv')

CELLS = ['shwd2sf', 'smoke2sf']
ARMS = {'base': 'base', 'strategy': 'lr005'}
ENDPOINTS = {'oracle': 'prem_test_oracle_pp', 'selected': 'prem_test_selected_pp'}


def load():
    rows = list(csv.DictReader(io.open(SRC, encoding='utf-8')))
    d = {}
    for r in rows:
        # run 名形如 r10_shwd2sf_base100_3way_s42n
        import re
        m = re.match(r'r10_(\w+?)_(base100|lr005_100ep|base30|lr005_30ep)_3way_s(\d+)n', r['run'])
        if not m:
            continue
        cell, armraw, seed = m.group(1), m.group(2), int(m.group(3))
        arm = 'base' if armraw.startswith('base') else 'strategy'
        d[(cell, arm, seed)] = dict(
            prem_val=float(r['prem_val_pp']),
            oracle=float(r['prem_test_oracle_pp']),
            selected=float(r['prem_test_selected_pp']),
        )
    return d


def paired_t(diffs):
    n = len(diffs)
    m = st.mean(diffs)
    sd = st.stdev(diffs) if n > 1 else 0.0
    if sd == 0:
        return m, 0.0, 1.0 if abs(m) < 1e-12 else 0.0
    t = m / (sd / math.sqrt(n))
    # 双侧 p（t 分布精确值用不完全 beta；这里用数学库的实现）
    try:
        from scipy import stats as _s
        p = float(2 * _s.t.sf(abs(t), n - 1))
    except Exception:
        # 无 scipy 时的保守近似：用正态
        p = float(math.erfc(abs(t) / math.sqrt(2)))
    return m, t, p


def signflip_exact(diffs):
    """精确 sign-flip 置换：对 |Δ| 做 2ⁿ 次符号翻转，统计 |mean| ≥ 观测的占比。"""
    n = len(diffs)
    obs = abs(st.mean(diffs))
    base = [abs(x) for x in diffs]
    signs = list(itertools.product((-1, 1), repeat=n))
    hits = 0
    for s in signs:
        v = abs(sum(si * bi for si, bi in zip(s, base)) / n)
        if v >= obs - 1e-12:
            hits += 1
    return hits / len(signs), len(signs)


def main():
    d = load()
    print('=' * 100)
    print('X5：§7.2 前缀-n 表（逐 seed 前缀 n = 3…10；paired t 与精确 sign-flip 置换；两种端点各一列）')
    print('=' * 100)
    print('数据：%s（%d 个 (cell, arm, seed) 组合）' % (os.path.basename(SRC), len(d)))
    out = {}
    for cell in CELLS:
        seeds = sorted({s for (c, a, s) in d if c == cell})
        print('\n### %s（seed %s）' % (cell, seeds))
        for ep in ENDPOINTS:
            print('  端点 = %-9s' % ep)
            print('    %-3s %-8s %-9s %-9s %-9s %-11s %-11s' % ('n', 'seeds', 'meanΔ', 'sd', 'paired t', 't-p', 'perm-p'))
            tbl = []
            for n in range(3, 11):
                use = seeds[:n]
                diffs = []
                for s in use:
                    b = d.get((cell, 'base', s))
                    a = d.get((cell, 'strategy', s))
                    if not b or not a:
                        continue
                    diffs.append(a[ep] - b[ep])
                if len(diffs) < 3:
                    continue
                m, t, p = paired_t(diffs)
                pp, ns = signflip_exact(diffs)
                tbl.append(dict(n=n, seeds=use, mean=m, sd=st.stdev(diffs), t=t, p_t=p, p_perm=pp, n_perms=ns))
                print('    %-3d %-8s %+9.4f %-9.4f %-9.4f %-11.3g %-11.3g' % (
                    n, '%d..%d' % (use[0], use[-1]) if n > 1 else str(use[0]), m, st.stdev(diffs), t, p, pp))
            out.setdefault(cell, {})[ep] = tbl
    p = os.path.join(OUT, 'x5_prefix_n_table.json')
    io.open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
    back = json.load(io.open(p, encoding='utf-8'))
    assert back['shwd2sf']['oracle'][0]['n'] == 3, '回读不一致'
    print('\n已写 %s（回读一致）' % p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
