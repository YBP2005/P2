#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""G3_sigma_n5_20260930.py — σ 三分量的「初始化分量」从 n = 3 扩到 n = 5 的复算（只算数，不出最终判词）。

输入：
  A 机 `/workspace/sio_b_results.csv`（`train_obj.py` 的台账，列 `name,loss,epochs,map50,map,mp,mr`，
  其中 `map` 是 **test** 的 mAP50-95，分数形式）。stage-2 的行：
      r10_iv_src{1,2,3}_{base100,lr005_100ep}_3way_s42n        （归档三次初始化）
      r16_iv_src{4,5}_{base100,lr005_100ep}_3way_s42n          （本轮新增两次）
口径照 2026-09-15 那次（`r10_initvar_and_seedext_20260915.md` §2）：
  每个初始化 k 给两个端点：`base`（base100 的 test 值）与 `lr0.005`；
  增益 gain_k = lr0.005 − base；初始化分量 = gain 的 SD（端点 SD 另报）。

先**复现归档三次**（base 43.630 / 43.590 / 43.250，gain +0.570 / +0.280 / +0.460，SD 0.146、端点 SD 0.209）
——对不上就非零退出，绝不静默继续；再给 n = 5 的读数与 bootstrap CI。
用法： python G3_sigma_n5_20260930.py [--ledger /workspace/sio_b_results.csv] [--out /workspace/G3_initvar_20260930.txt]
"""
import argparse
import io
import os
import random
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ARCH_BASE = {1: 43.630, 2: 43.590, 3: 43.250}
ARCH_GAIN = {1: 0.570, 2: 0.280, 3: 0.460}
ARCH_SD_GAIN, ARCH_SD_BASE = 0.146, 0.209
TOL = 0.005


def read_ledger(path):
    d = {}
    for line in io.open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split(',')
        if len(f) >= 5 and f[0].startswith('r'):
            try:
                d[f[0]] = float(f[4]) * 100.0        # map = test mAP50-95（分数→pp）
            except ValueError:
                pass
    return d


def boot_sd(vals, n=20000, seed=20260930):
    rnd = random.Random(seed)
    k = len(vals)
    if k < 2:
        return (float('nan'), float('nan'))
    sds = []
    for _ in range(n):
        s = [vals[rnd.randrange(k)] for _ in range(k)]
        try:
            sds.append(st.stdev(s))
        except Exception:
            pass
    sds.sort()
    return (sds[int(0.025 * len(sds))], sds[int(0.975 * len(sds))])


def chi2_sd_interval(sd, df):
    """正态样本 SD 的精确区间（卡方）：[sd*sqrt(df/chi2_{0.975}), sd*sqrt(df/chi2_{0.025})]"""
    try:
        from scipy.stats import chi2
    except Exception:
        return (float('nan'), float('nan'))
    lo = sd * (df / chi2.ppf(0.975, df)) ** 0.5
    hi = sd * (df / chi2.ppf(0.025, df)) ** 0.5
    return (lo, hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', default='/workspace/sio_b_results.csv')
    ap.add_argument('--out', default='/workspace/G3_initvar_20260930.txt')
    a = ap.parse_args()
    L = read_ledger(a.ledger)

    def get(k, arm):
        pre = 'r10_iv_src%d' % k if k <= 3 else 'r16_iv_src%d' % k
        if arm == 'base':
            return L.get('%s_base100_3way_s42n' % pre)
        return L.get('%s_lr005_100ep_3way_s42n' % pre)

    out = []
    def emit(s=''):
        out.append(s); print(s, flush=True)

    emit('=== G3：初始化分量 n = 3 → n = 5 复算（口径照 2026-09-15）===')
    emit('%d 行台账：%s' % (len(L), a.ledger))
    base, gain, missing = {}, {}, []
    for k in range(1, 6):
        b, s = get(k, 'base'), get(k, 'str')
        if b is None or s is None:
            missing.append(k)
            continue
        base[k] = b; gain[k] = s - b
    emit('\n逐初始化（test mAP50-95，pp）：')
    emit('  init   base     lr0.005  gain   归档 base/gain')
    for k in sorted(base):
        ar = ('%.3f / %+.3f' % (ARCH_BASE[k], ARCH_GAIN[k])) if k <= 3 else '—'
        emit('  src%-3d %8.3f %8.3f %+7.3f   %s' % (k, base[k], base[k] + gain[k], gain[k], ar))
    if missing:
        emit('\n⚠ 缺读数：src%s —— 下面的 n 只按已到位的算' % missing)

    # ---- 复现归档三次 ----
    fails = []
    for k in (1, 2, 3):
        if k not in base:
            fails.append('src%d 无读数（无法复现归档）' % k); continue
        if abs(base[k] - ARCH_BASE[k]) > TOL:
            fails.append('src%d base %.3f vs 归档 %.3f' % (k, base[k], ARCH_BASE[k]))
        if abs(gain[k] - ARCH_GAIN[k]) > TOL:
            fails.append('src%d gain %+.3f vs 归档 %+.3f' % (k, gain[k], ARCH_GAIN[k]))
    emit('\n[1] 复现归档三次：%s' % ('PASS（全部 ≤ %.3f pp）' % TOL if not fails else 'FAIL ' + '; '.join(fails)))

    ks3 = [k for k in (1, 2, 3) if k in base]
    ks5 = sorted(base)
    for tag, ks in (('n = 3（归档）', ks3), ('n = %d（本轮）' % len(ks5), ks5)):
        if len(ks) < 2:
            continue
        g = [gain[k] for k in ks]; b = [base[k] for k in ks]
        sdg, sdb = st.stdev(g), st.stdev(b)
        lo, hi = boot_sd(g)
        c_lo, c_hi = chi2_sd_interval(sdg, len(ks) - 1)
        emit('\n[2] %s' % tag)
        emit('    gain: 均值 %+.3f  极差 %.3f  SD %.3f   （bootstrap 95%% CI [%.3f, %.3f]；卡方 %.3f→[%.3f, %.3f]）'
             % (st.mean(g), max(g) - min(g), sdg, lo, hi, sdg, c_lo, c_hi))
        emit('    base 端点 SD %.3f（%.3f–%.3f）' % (sdb, min(b), max(b)))

    emit('\n[3] 与另两个分量的排序（§8.4 的对照值）')
    emit('    数据顺序（同单元 shwd2sf）：n=10 SD 0.488 pp；n=9 0.515 pp')
    emit('    增广 RNG：策略臂 0.246 / 基线臂 0.190 pp')
    if len(ks5) >= 2:
        g = [gain[k] for k in ks5]
        lo, hi = boot_sd(g)
        emit('    本轮初始化：gain SD %.3f pp（CI 上界 %.3f）  ⇒ %s'
             % (st.stdev(g), hi,
                'CI 上界 < 数据顺序点估计 0.488 ⇒ 按预注册规则**可收紧措辞**'
                if hi < 0.488 else '**CI 上界越过 0.488** ⇒ 按预注册规则保持 "consistent with, not established"'))

    txt = '\n'.join(out) + '\n'
    io.open(a.out, 'w', encoding='utf-8', newline='\n').write(txt)
    print('\n存证：%s' % a.out)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
