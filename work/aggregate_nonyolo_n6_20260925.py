# -*- coding: utf-8 -*-
"""第 4 项汇总：把 5 个新 seed 与原有 n=1 的 run 合成 n = 6，给出带区间的跨架构兑现率。

估计量口径（明确区分，避免"比的均值 vs 比值的均值"混淆——本项目 §8.6 踩过这个坑）：
  · **比的均值**（与 §8.6 头条同族）：Σprem_test / Σprem_val
  · **比值的均值**：逐 run 算 rate 再平均（另一估计量，单列）
  两者都给，并给 run 级 bootstrap 95% 区间。
输入：settle_s43..47.json（新）与 nonyolo_realization.json（原有 n=1）。
"""
import glob
import io
import json
import os
import random
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')
D = r'E:\workplace\nonyolo_settle_20260925'
NEW = sorted(glob.glob(os.path.join(D, 'settle_s*.json')))
ORIG = os.path.join(D, 'nonyolo_realization.json')
MD = ('100', '300', '1000')
PRIMARY = '300'


def load_runs():
    runs = []
    for p in NEW:
        o = json.load(io.open(p, encoding='utf-8'))
        pm = o['per_maxdets']
        runs.append({'name': 'seed%s' % o['seed'], 'src': os.path.basename(p),
                     'prem_val': {m: pm[m]['prem_val'] for m in MD},
                     'prem_test': {m: pm[m]['prem_test'] for m in MD},
                     'rate': {m: pm[m]['rate_pct'] for m in MD}})
    if os.path.exists(ORIG):
        o = json.load(io.open(ORIG, encoding='utf-8'))
        s = o['summary']
        runs.append({'name': 'orig(n=1)', 'src': os.path.basename(ORIG),
                     'prem_val': {m: s['maxdets_%s' % m]['prem_val'] for m in MD if 'maxdets_%s' % m in s},
                     'prem_test': {m: s['maxdets_%s' % m]['prem_test'] for m in MD if 'maxdets_%s' % m in s},
                     'rate': {m: s['maxdets_%s' % m]['realization_rate_pct'] for m in MD
                              if 'maxdets_%s' % m in s}})
    return runs


def boot_mean(vals, n=10000, seed=42):
    rng = random.Random(seed)
    ms = sorted(sum(rng.choice(vals) for _ in vals) / len(vals) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def boot_ratio(pv, pt, n=10000, seed=7):
    rng = random.Random(seed)
    idx = range(len(pv))
    out = []
    for _ in range(n):
        pick = [rng.choice(list(idx)) for _ in idx]
        sv = sum(pv[i] for i in pick)
        stt = sum(pt[i] for i in pick)
        out.append(100 * stt / sv if sv else float('nan'))
    out = [x for x in out if x == x]
    out.sort()
    return out[int(0.025 * len(out))], out[int(0.975 * len(out)) - 1]


runs = load_runs()
print('=== 参与汇总的 run（n = %d）===' % len(runs))
print('%-12s %10s %10s %9s   %s' % ('run', 'prem_val', 'prem_test', 'rate%', '来源'))
for r in runs:
    print('%-12s %+10.4f %+10.4f %9s   %s'
          % (r['name'], r['prem_val'][PRIMARY], r['prem_test'][PRIMARY],
             r['rate'][PRIMARY], r['src']))

out = {'n': len(runs), 'primary_maxdets': PRIMARY, 'per_maxdets': {}}
for m in MD:
    pv = [r['prem_val'][m] for r in runs if m in r['prem_val']]
    pt = [r['prem_test'][m] for r in runs if m in r['prem_test']]
    rt = [r['rate'][m] for r in runs if m in r['rate'] and r['rate'][m] is not None]
    if not pv:
        continue
    ratio = 100 * sum(pt) / sum(pv) if sum(pv) else float('nan')
    lo_r, hi_r = boot_ratio(pv, pt)
    lo_m, hi_m = boot_mean(rt) if len(rt) > 1 else (float('nan'), float('nan'))
    out['per_maxdets'][m] = {
        'n': len(pv),
        'prem_val_mean': round(st.mean(pv), 4), 'prem_val_sd': round(st.stdev(pv), 4) if len(pv) > 1 else None,
        'prem_test_mean': round(st.mean(pt), 4), 'prem_test_sd': round(st.stdev(pt), 4) if len(pt) > 1 else None,
        'rate_ratio_of_means_pct': round(ratio, 2), 'rate_ratio_ci': [round(lo_r, 2), round(hi_r, 2)],
        'rate_mean_of_ratios_pct': round(st.mean(rt), 2) if rt else None,
        'rate_mean_ci': [round(lo_m, 2), round(hi_m, 2)] if rt else None,
        'signs': {'prem_val_pos': sum(1 for x in pv if x > 0), 'prem_test_pos': sum(1 for x in pt if x > 0),
                  'rate_pos': sum(1 for x in rt if x > 0), 'rate_neg': sum(1 for x in rt if x < 0)},
    }
    o = out['per_maxdets'][m]
    star = ' ←主口径' if m == PRIMARY else ''
    print()
    print('--- maxdets=%s（n=%d）%s ---' % (m, o['n'], star))
    print('   prem_val  均值 %+8.4f（sd %.4f）   prem_test 均值 %+8.4f（sd %.4f）'
          % (o['prem_val_mean'], o['prem_val_sd'] or 0, o['prem_test_mean'], o['prem_test_sd'] or 0))
    print('   兑现率【比的均值】%.2f %%    bootstrap 95%% CI [%.2f, %.2f]'
          % (o['rate_ratio_of_means_pct'], o['rate_ratio_ci'][0], o['rate_ratio_ci'][1]))
    print('   兑现率【比值的均值】%s %%    bootstrap 95%% CI [%s, %s]'
          % (o['rate_mean_of_ratios_pct'], o['rate_mean_ci'][0], o['rate_mean_ci'][1]))
    print('   同号计数：prem_val>0 %d/%d；prem_test>0 %d/%d；rate>0 %d，rate<0 %d'
          % (o['signs']['prem_val_pos'], o['n'], o['signs']['prem_test_pos'], o['n'],
             o['signs']['rate_pos'], o['signs']['rate_neg']))

p = os.path.join(D, 'nonyolo_n6_aggregate.json')
json.dump(out, io.open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print()
print('已写 %s' % p)
