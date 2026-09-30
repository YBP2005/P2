#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""g6_repro_vs_printed.py — 用 G6 的新读数**逐格复现稿件已印的数**（这是对整条流水线的硬校验）。

靶子：`gap_mechanism_20260916.txt` 的表（§5.6 / §S12 L2130 就是照它印的），逐格给
    n, Mval_b, Mval_s, Mtest_b, Mtest_s, prem_b, prem_s
其中 `Mtest_*` 是**归档 sio_b_results.csv 里的 test 读数**（被选中 checkpoint 上的 test 评测）。

核对三项（同格、同臂、同种子集）：
  ① 归档 `results.csv` 的逐 epoch val 最大值均值  ⇄ 印出的 `Mval_*`
  ② 由 ① 算出的 `prem_val = V_max − V_final` 均值 ⇄ 印出的 `prem_*`
  ③ 本次新评的 `best.pt` test 读数均值          ⇄ 印出的 `Mtest_*`
种子集：印出 n = 10 的格取 s42–51；n = 3 的格取 s42–44（与原记录"两臂种子交集"一致）。

三者都对上 ⇒ 新评测与归档口径一致，`prem_test = T(best) − T(last)` 才可信。
用法： python g6_repro_vs_printed.py --printed /workspace/gap_mechanism_archive.txt
"""
import argparse
import csv
import io
import os
import re
import statistics as st
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ARMS = ('lr005_100ep', 'lr005_30ep', 'base100', 'base30')


def arm_tokens(cell):
    """按格的 epochs 猜臂名（30 ep 的格用 base30/lr005_30ep）"""
    a = '30' if cell in ('aitod20', 'd15d15', 'dota', 'fire', 'mask20', 'mende20', 'vis') else '100'
    return ('base' + a, 'lr005_' + a + 'ep' if a == '30' else 'lr005_100ep')


def val_curve(rd):
    p = os.path.join(rd, 'results.csv')
    if not os.path.exists(p):
        return []
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return []
    col = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if col is None:
        return []
    out = []
    for i, r in enumerate(rows, start=1):
        try:
            out.append((i, float(r[col]) * 100.0))
        except (TypeError, ValueError):
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='/workspace/g6_perepoch_20260930')
    ap.add_argument('--rundir', default='/workspace/runs')
    ap.add_argument('--printed', default='/workspace/gap_mechanism_archive.txt')
    a = ap.parse_args()

    # ---- 解析印出的表 ----
    printed = {}
    txt = io.open(a.printed, encoding='utf-8', errors='replace').read()
    for line in txt.splitlines():
        f = line.split()
        if len(f) == 13 and re.match(r'^\d+$', f[1]):
            cell = f[0]
            printed[cell] = dict(n=int(f[1]), mv_b=float(f[2]), mv_s=float(f[3]),
                                 mt_b=float(f[4]), mt_s=float(f[5]),
                                 prem_b=float(f[10]), prem_s=float(f[11]))
    print('印出的格数 = %d：%s' % (len(printed), ', '.join(sorted(printed))))

    # ---- 本次 test 读数 ----
    T = defaultdict(dict)
    for r in csv.DictReader(io.open(os.path.join(a.dir, 'g6_perepoch.csv'), encoding='utf-8')):
        if r['split'] == 'test':
            T[r['run']][r['ckpt']] = float(r['map50_95'])

    rows, worst = [], {'Mval': 0.0, 'prem_val': 0.0, 'Mtest_best': 0.0}
    for cell in sorted(printed):
        p = printed[cell]
        seeds = range(42, 52) if p['n'] == 10 else range(42, 45)
        base, strat = arm_tokens(cell)
        for arm, key_mv, key_pm, key_mt in ((base, 'mv_b', 'prem_b', 'mt_b'),
                                            (strat, 'mv_s', 'prem_s', 'mt_s')):
            mvs, prems, tbests, tlasts = [], [], [], []
            for s in seeds:
                run = 'r10_%s_%s_3way_s%dn' % (cell, arm, s)
                vc = val_curve(os.path.join(a.rundir, run))
                if vc:
                    v = dict(vc)
                    vmax_ep = max(v, key=lambda e: v[e])
                    mvs.append(v[vmax_ep]); prems.append(v[vmax_ep] - v[vc[-1][0]])
                t = T.get(run, {})
                if 'best' in t:
                    tbests.append(t['best'])
                if 'last' in t:
                    tlasts.append(t['last'])
            if not mvs:
                print('  %-14s %-12s 无 val 读数（跳过）' % (cell, arm))
                continue
            d_mv = st.mean(mvs) - p[key_mv]
            d_pm = st.mean(prems) - p[key_pm]
            d_mt = (st.mean(tbests) - p[key_mt]) if tbests else float('nan')
            worst['Mval'] = max(worst['Mval'], abs(d_mv))
            worst['prem_val'] = max(worst['prem_val'], abs(d_pm))
            if tbests:
                worst['Mtest_best'] = max(worst['Mtest_best'], abs(d_mt))
            rows.append((cell, arm, len(mvs), p[key_mv], st.mean(mvs), d_mv,
                         p[key_pm], st.mean(prems), d_pm,
                         p[key_mt], (st.mean(tbests) if tbests else None), d_mt,
                         st.mean(tbests) - st.mean(tlasts) if (tbests and tlasts) else None))

    print('\ncell           arm           n  Mval(印/我/Δ)              prem_val(印/我/Δ)          '
          'Mtest(best 印/我/Δ)      prem_test(Tbest−Tlast)')
    for (cell, arm, n, pmv, mmv, dmv, ppm, mpm, dpm, pmt, mmt, dmt, pt) in rows:
        print('%-14s %-12s %2d  %7.2f %7.2f %+6.2f   %7.2f %7.2f %+6.2f   %s   %s'
              % (cell, arm, n, pmv, mmv, dmv, ppm, mpm, dpm,
                 ('%7.2f %7.2f %+6.2f' % (pmt, mmt, dmt)) if mmt is not None else '   —（无 best 读数）  ',
                 ('%+.3f' % pt) if pt is not None else '—'))
    print('\n最大绝对偏差：Mval %.4f pp ｜ prem_val %.4f pp ｜ Mtest(best) %.4f pp'
          % (worst['Mval'], worst['prem_val'], worst['Mtest_best']))
    ok = max(worst.values()) <= 0.05
    print('判定：%s（阈值 0.05 pp）' % ('复现通过' if ok else '**有超差，需查口径**'))
    out = '/workspace/g6_repro_vs_printed.txt'
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('cell\tarm\tn\tMval_printed\tMval_mine\tMval_delta\t'
                'prem_printed\tprem_mine\tprem_delta\tMtest_printed\tMtest_mine\tMtest_delta\t'
                'prem_test_Tbest_minus_Tlast\n')
        for r in rows:
            f.write('\t'.join('' if x is None else str(x) for x in r) + '\n')
        f.write('\nmax_abs: Mval=%.4f prem_val=%.4f Mtest=%.4f verdict=%s\n'
                % (worst['Mval'], worst['prem_val'], worst['Mtest_best'],
                   'PASS' if ok else 'FAIL'))
    print('存证：%s' % out)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
