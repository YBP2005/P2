#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""analyze_c2_aa_control.py —— **C2（A/A 空干预对照）的判据分析**（跑完后在本地/任一有台账的机器上运行）。

口径（照 §5.1 Tier-2 / 补充材料对 Δgap 的定义）：
  * 每个 run 的 **val 端**：`prem_val = max_e V(e) − V(final)`（mAP50-95，pp；取自该 run 自己的 `results.csv`）；
  * 每个 run 的 **test 端**：`prem_test = T(best.pt) − T(last.pt)`（取自逐检查点 test 扫或台账的 best/last 读数）；
  * **配对差**：同一 `--shuffle-seed` 下，`Δval = prem_val(strategy) − prem_val(baseline)`，
               `Δtest = prem_test(strategy) − prem_test(baseline)`，**`Δgap = Δval − Δtest`**（正 = val 低估策略臂）。
  * C2 的两臂**配置相同**（`lr0` 都 0.001），只差**数据序**（臂 A：42–51；臂 B：62–71）⇒ 期望 `Δgap ≈ 0`。

判据（跑前写定，评审原文）：
  * `Δgap_A/A` 的 **95 % CI 覆盖 0** ⇒ 表 2 获得一个**真正的空对照**；
  * 若 **CI 不含 0** 或 **|均值| > ~0.2 pp**（观测升级效应的一半）⇒ §5.1 Tier-2 的"相等难度"假设须**显式修订**。

用法：
  python analyze_c2_aa_control.py --runs /workspace/runs --tag r21_c2aa_sfchd \
      [--matrix /workspace/g6_perepoch_20260930/g6_perepoch.csv] [--ledger /workspace/sio_b_results.csv]
"""
import argparse
import csv
import io
import math
import os
import re
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')


def prem_val(run_dir):
    f = os.path.join(run_dir, 'results.csv')
    if not os.path.isfile(f):
        return None
    seq = []
    for r in csv.DictReader(io.open(f, encoding='utf-8', errors='ignore')):
        if r.get('epoch') in (None, ''):
            continue
        try:
            seq.append((float(r['epoch']), float(r['metrics/mAP50-95(B)']) * 100.0))
        except Exception:
            pass
    if not seq:
        return None
    return max(v for _, v in seq) - seq[-1][1]


def test_endpoints(name, matrix, ledger, tecsv=''):
    # ① 优先：本次专为 C2 跑的 best/last test 评测（同单位 mAP50-95）
    if tecsv and os.path.isfile(tecsv):
        got = {}
        for r in csv.DictReader(io.open(tecsv, encoding='utf-8', errors='ignore')):
            if r.get('run') == name:
                got[r.get('ckpt')] = float(r['map50_95'])
        if 'best' in got and 'last' in got:
            return got['best'], got['last']
    return _te_fallback(name, matrix, ledger)


def _te_fallback(name, matrix, ledger):
    """返回 (T_best, T_last)；优先逐检查点矩阵，退化到台账。"""
    if matrix and os.path.isfile(matrix):
        got = {}
        for r in csv.DictReader(io.open(matrix, encoding='utf-8', errors='ignore')):
            if r.get('run') == name and r.get('split', 'test') == 'test':
                got[r.get('ckpt')] = float(r['map50_95'])
        if 'best' in got and 'last' in got:
            return got['best'], got['last']
    if ledger and os.path.isfile(ledger):
        for ln in csv.reader(io.open(ledger, encoding='utf-8', errors='ignore')):
            if ln and ln[0] == name and len(ln) >= 7:
                try:
                    return float(ln[5]) * 100.0, float(ln[6]) * 100.0
                except Exception:
                    pass
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default='/workspace/runs')
    ap.add_argument('--tag', default='r21_c2aa_sfchd')
    ap.add_argument('--matrix', default='')
    ap.add_argument('--ledger', default='/workspace/sio_b_results.csv')
    ap.add_argument('--tecsv', default='/workspace/r21_c2aa_testeval.csv',
                    help='本次 C2 专跑的 best/last test 评测 CSV（同单位优先）')
    a = ap.parse_args()

    rows = []
    for arm, rng in (('A', range(42, 52)), ('B', range(62, 72))):
        for s in rng:
            name = '%s_%s_s%dn' % (a.tag, arm, s)
            d = os.path.join(a.runs, name)
            if not os.path.isdir(d):
                continue
            pv = prem_val(d)
            tb, tl = test_endpoints(name, a.matrix, a.ledger, a.tecsv)
            if pv is None or tb is None:
                print('  [缺数据] %s' % name)
                continue
            rows.append((arm, s, pv, tb - tl))
    print('配对样本：A 臂 %d 个 · B 臂 %d 个' % (sum(1 for r in rows if r[0] == 'A'), sum(1 for r in rows if r[0] == 'B')))
    if not rows:
        print('  无可用 run（检查 --runs/--tag）')
        return 1
    # C2 的两臂按设计使用**不相交**的数据序 ⇒ **两样本**比较（不是配对）：
    #   每个 run 的原始 gap  G = prem_val − prem_test（§5.1 的 G = V(ê) − T(ê)）；
    #   Δgap_A/A = mean(G | 臂 A) − mean(G | 臂 B)，CI 用 Welch t 与 run 级 bootstrap 两法各出一版。
    import random
    GA = [r[2] - r[3] for r in rows if r[0] == 'A']
    GB = [r[2] - r[3] for r in rows if r[0] == 'B']
    print()
    print('  臂 A（序 42–51）: n=%d · G 均值 %+0.3f pp · SD %0.3f' % (len(GA), st.mean(GA), st.pstdev(GA) if len(GA) > 1 else 0))
    print('  臂 B（序 62–71）: n=%d · G 均值 %+0.3f pp · SD %0.3f' % (len(GB), st.mean(GB), st.pstdev(GB) if len(GB) > 1 else 0))
    mA, mB = st.mean(GA), st.mean(GB)
    sA = st.variance(GA) if len(GA) > 1 else 0.0
    sB = st.variance(GB) if len(GB) > 1 else 0.0
    se = math.sqrt(sA / len(GA) + sB / len(GB)) if (len(GA) > 1 and len(GB) > 1) else float('nan')
    diff = mA - mB
    lo, hi = (diff - 1.96 * se, diff + 1.96 * se)
    random.seed(20261012)
    bs = []
    for _ in range(20000):
        a = [random.choice(GA) for _ in GA]
        b = [random.choice(GB) for _ in GB]
        bs.append(st.mean(a) - st.mean(b))
    bs.sort()
    blo, bhi = bs[int(.025 * len(bs))], bs[int(.975 * len(bs))]
    print()
    print('  Δgap_A/A（臂 A − 臂 B）= %+0.3f pp · Welch 95 %% CI [%+0.3f, %+0.3f] · bootstrap(B=20,000) 95 %% CI [%+0.3f, %+0.3f]'
          % (diff, lo, hi, blo, bhi))
    g = [diff]
    m, sd, n = diff, se, len(GA) + len(GB)
    print()
    print('  Δgap_A/A：均值 %+0.3f pp · SD %0.3f · n=%d · 95 %% CI [%+0.3f, %+0.3f]' % (m, sd, n, lo, hi))
    covers = (lo <= 0 <= hi) if n > 1 else None
    print('  判据：CI 覆盖 0 = %s · |均值| > 0.2 pp = %s' % (covers, abs(m) > 0.2))
    print()
    if covers and abs(m) <= 0.2:
        print('  ⇒ 结论：**表 2 获得一个真正的空对照**（无需修订 §5.1 Tier-2 的假设）。')
    else:
        print('  ⇒ 结论：**§5.1 Tier-2 的"相等难度"假设须显式修订**，表 2 全部读法加约定项。')
    return 0


raise SystemExit(main())
