# -*- coding: utf-8 -*-
"""X6（r13 评审请求，**零新训练**）：臂间 κ 的**配对**重算。

评审原话（Space-Bunny R2，逐字）：
  「**臂间 κ 的配对重算**：按种子配对求 κ_base(e) − κ_strat(e)，再对种子求均值与 CI」；
  自标「0 新训练、0 新评测」，并称「**这是本清单里最便宜的一个统计收益**」。

数据（全部已放行、零新训练）：
  * `val` 侧逐 epoch：`xeval_20260916/runs/<run>_results.csv` 的 `metrics/mAP50-95(B)`（41 run）
  * `test` 侧逐 epoch：`02_release_data/xeval_perepoch_20260918/matrix_perepoch.csv`（806 行 / 41 run）
  * 配对方式：**同语料、同 seed、异臂**（`within a batch the two arms share their seeds`，包内 §8.6b 逐字）

口径（与包内 §8.7 一致）：
  * `ΔV(e) = V_strategy(e) − V_base(e)`、`ΔT(e) = T_strategy(e) − T_base(e)`，**逐 epoch 配对**
  * κ（through-origin）= `Σ ΔV·ΔT / Σ ΔV²`（包 L804 逐字 `the through-origin slope κ of ΔT on ΔV`）
  * **对照**：带截距的 `κ_free` 与截距本身（评审 Deepseek-V4-Pro F-6 要求"报带截距的对照"）
  * 逐对 κ 汇总：对 **seed** 求均值与 95 % CI（run-clustered 不适用时用 seed 级 t）

用法：python -X utf8 work/x6_arm_paired_kappa_20261004.py
"""
import csv
import io
import json
import math
import os
import re
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')

W = r'E:\workplace'
REPO = r'E:\WorkBuddy\盲审P2\复现仓库'
OUT = r'E:\workplace\G5_review_p2r13_20261007'
VALDIR = os.path.join(W, 'xeval_20260916', 'runs')
TST = os.path.join(REPO, '02_release_data', 'xeval_perepoch_20260918', 'matrix_perepoch.csv')


def load_val():
    """逐 run 的 {epoch: mAP50-95}（val 侧）。"""
    out = {}
    for fn in os.listdir(VALDIR):
        if not fn.endswith('_results.csv'):
            continue
        run = fn[:-len('_results.csv')]
        d = {}
        with io.open(os.path.join(VALDIR, fn), encoding='utf-8') as fh:
            for r in csv.DictReader(fh):
                try:
                    d[int(r['epoch'])] = float(r['metrics/mAP50-95(B)'])
                except (KeyError, ValueError):
                    pass
        if d:
            out[run] = d
    return out


def load_test():
    out = {}
    with io.open(TST, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r.get('split') != 'test':
                continue
            try:
                out.setdefault(r['run'], {})[int(r['epoch'])] = float(r['map50_95'])
            except (KeyError, ValueError):
                pass
    return out


def fit(dv, dt, intercept=False):
    """through-origin 或带截距的最小二乘。返回 (κ, intercept, R²)。"""
    n = len(dv)
    if n < 2 or all(abs(x) < 1e-12 for x in dv):
        return None
    if not intercept:
        k = sum(x * y for x, y in zip(dv, dt)) / sum(x * x for x in dv)
        a = 0.0
    else:
        mx, my = st.mean(dv), st.mean(dt)
        num = sum((x - mx) * (y - my) for x, y in zip(dv, dt))
        den = sum((x - mx) ** 2 for x in dv)
        if abs(den) < 1e-12:
            return None
        k = num / den
        a = my - k * mx
    ss_res = sum((y - (a + k * x)) ** 2 for x, y in zip(dv, dt))
    ss_tot = sum((y - st.mean(dt)) ** 2 for y in dt)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return k, a, r2


def main():
    V = load_val()
    T = load_test()
    print('=' * 100)
    print('X6：臂间 κ 的配对重算（**零新训练**；val 逐 epoch 来自 results.csv，test 逐 epoch 来自 matrix_perepoch.csv）')
    print('=' * 100)
    print('val 侧 run = %d；test 侧 run = %d' % (len(V), len(T)))

    # ★ 口径修正（2026-10-04）：包 L807/L1007 逐字规定
    #   `ΔV(e) = V(e) − V(final)`、`ΔT(e) = T(e) − T(final)` —— **run 内、逐 epoch、相对该 run 的 final**，
    #   不是臂间配对（我第一版按"strategy − base 同 epoch"算，得 κ≈55，比印的 0.708 大 77 倍 ⇒ 定义错）。
    #   印的口径：n = 765 (seed, epoch) 点、41 run、池化 through-origin slope = 0.708、R² 0.937。
    per_run = []
    for run in sorted(V):
        if run not in T:
            continue
        common = sorted(set(V[run]) & set(T[run]))
        if len(common) < 3:
            continue
        ef = max(common)                      # final epoch
        vf, tf = V[run][ef], T[run][ef]
        dv = [V[run][e] - vf for e in common]
        dt = [T[run][e] - tf for e in common]
        # final 点使 ΔV=ΔT=0 ⇒ 过原点拟合的自然成分（不额外加权）
        f0 = fit(dv, dt, intercept=False)
        f1 = fit(dv, dt, intercept=True)
        if not f0:
            continue
        m = re.match(r'r10_(\w+?)_(base\d+|lr005_\d+ep)_3way_s(\d+)n$', run)
        per_run.append(dict(run=run, cell=(m.group(1) if m else run.rsplit('_s',1)[0]),
                            seed=(int(m.group(3)) if m else None), n_epochs=len(common),
                            kappa=f0[0], r2=f0[2],
                            kappa_free=(f1[0] if f1 else None),
                            intercept=(f1[1] if f1 else None), r2_free=(f1[2] if f1 else None),
                            dv_min=min(dv), dv_max=max(dv), dt_min=min(dt), dt_max=max(dt)))

    print()
    print('逐 run（%d 个）：' % len(per_run))
    print('  %-40s %-10s %-5s %-7s %9s %7s' % ('run', 'cell', 'seed', 'epochs', 'kappa', 'R²'))
    for p_ in per_run:
        print('  %-40s %-10s %-5s %-7d %+9.4f %7.4f' % (p_['run'][:40], p_['cell'], p_['seed'], p_['n_epochs'], p_['kappa'], p_['r2']))

    # 池化：全部 (run, epoch) 观测放在一起
    allv, allt = [], []
    for p_ in per_run:
        run = p_['run']; common = sorted(set(V[run]) & set(T[run])); ef = max(common)
        allv += [V[run][e] - V[run][ef] for e in common]
        allt += [T[run][e] - T[run][ef] for e in common]
    pool = fit(allv, allt, intercept=False)
    poolf = fit(allv, allt, intercept=True)
    # 逐 run κ 的汇总（评审要的"按种子配对求 κ … 再对种子求均值与 CI"）
    ks = [p_['kappa'] for p_ in per_run]
    kf = [p_['kappa_free'] for p_ in per_run if p_['kappa_free'] is not None]
    it = [p_['intercept'] for p_ in per_run if p_['intercept'] is not None]
    # 取 shwd2sf / smoke2sf 两组的"臂配对"版本：同 seed 的 base 与 lr005 各一个 run，取两 run 的 κ 之差
    byseed = {}
    for p_ in per_run:
        m = re.match(r'r10_(\w+?)_(base\d+|lr005_\d+ep)_3way_s(\d+)n$', p_['run'])
        if m:
            byseed.setdefault((m.group(1), int(m.group(3))), {})['base' if m.group(2).startswith('base') else 'strategy'] = p_['kappa']
    paired = [(k, v['strategy'] - v['base']) for k, v in sorted(byseed.items()) if 'base' in v and 'strategy' in v]
    ks = [p_['kappa'] for p_ in per_run]
    kf = [p_['kappa_free'] for p_ in per_run if p_['kappa_free'] is not None]
    it = [p_['intercept'] for p_ in per_run if p_['intercept'] is not None]
    m = st.mean(ks); sd = st.stdev(ks) if len(ks) > 1 else 0.0
    se = sd / math.sqrt(len(ks)) if ks else float('nan')
    print('\n汇总（对 seed 配对，n = %d）：' % len(ks))
    print('  κ（through-origin）逐对均值 = **%+.4f**（SD %.4f，SE %.4f）· 95 %% CI [%+.4f, %+.4f]'
          % (m, sd, se, m - 1.96 * se, m + 1.96 * se))
    if kf:
        print('  κ_free（带截距）逐对均值 = %+.4f；intercept 逐对均值 = %+.4f（SD %.4f）'
              % (st.mean(kf), st.mean(it), st.stdev(it) if len(it) > 1 else 0))
    print('\n池化（全部 %d 个 (epoch, 对) 观测放在一起）：' % len(allv))
    print('  κ（through-origin）= %+.4f  R² = %.4f' % (pool[0], pool[2]))
    print('  对照 κ_free = %+.4f、intercept = %+.4f  R² = %.4f' % (poolf[0], poolf[1], poolf[2]))
    print('  ★ 包内印的 κ = **0.708**（run-clustered CI [0.671, 0.745]）⇒ 与池化值对照。')

    rep = dict(per_run=per_run, n_runs=len(ks), paired_kappa_diff=[list(x) for x in paired],
               kappa_mean=m, kappa_sd=sd, kappa_ci=[m - 1.96 * se, m + 1.96 * se],
               kappa_free_mean=(st.mean(kf) if kf else None),
               intercept_mean=(st.mean(it) if it else None),
               pooled=dict(kappa=pool[0], r2=pool[2], n_obs=len(allv)),
               pooled_free=dict(kappa=poolf[0], intercept=poolf[1], r2=poolf[2]),
               printed_kappa=0.708)
    p = os.path.join(OUT, 'x6_arm_paired_kappa.json')
    io.open(p, 'w', encoding='utf-8').write(json.dumps(rep, ensure_ascii=False, indent=1))
    back = json.load(io.open(p, encoding='utf-8'))
    assert back['n_runs'] == len(ks), '回读不一致'
    print('\n已写 %s（回读一致）' % p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
