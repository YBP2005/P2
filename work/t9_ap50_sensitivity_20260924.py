# -*- coding: utf-8 -*-
"""T9：Tier-1 溢价的 **AP50 敏感性**——移植 `selection_premium_local.py`，同一代码路径两种指标。

纪律（本会话反复吃亏的那条）：**先要求 mAP50-95 把已发表值逐格复现到 ±0.001 pp**，
复现不上就**不出 AP50 数**（否则等于发布一个未经验证的管线产物）。
已发表值（`selection_premium_local_20260916.txt` / `verify_two_critiques_20260916.txt`）：
  smoke2sf   base +0.799  strat +0.382      配对差 +0.416
  shwd2sf    base +1.038  strat +0.512      配对差 +0.526
  a2d15      base +0.534  strat +0.262      配对差 +0.272
  dota15     base +0.868  strat +0.279      配对差 +0.589   （当时 n=3：43,44,unseeded）

移植要点：根沿用原脚本的三棵本地归档；匹配规则沿用"prefix + 可选 _s<N>n"（含 unseeded）；
`best = 逐 epoch 最大值`、`last = 末行`，×100 转 pp。仅把指标列从 mAP50-95 换成 mAP50 即得 AP50 版。
"""
import csv
import io
import os
import re
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
ROOTS = [r'D:\deepseek\4090Bruns\runs',
         r'D:\deepseek\analysis\A_results_20260914\runs',
         r'D:\deepseek\analysis\B_results_20260914\runs',
         r'D:\deepseek\analysis\A_results_20260915\workspace\runs',
         r'D:\deepseek\analysis\B_results_20260915\workspace\runs']
# r54x：表 1 的 dota15 已由 n=3 升级到 n=10，升级 run 不在上面五棵归档里。
# 但把这批并进来后，**整格 dota15 就不再等于 09-16 归档的 n=3 值**（那是另一批 run），
# 故不混算：主表仍用上面五棵（三格严格阳控），dota15 的升级集**单列**并报出与表 1 的残差。
ESC_ROOTS = [r'E:\workplace\pod_mirror_20260918\B_x8', r'E:\workplace\x8_dota15_20260918']
CELLS = {
    'smoke2sf': ('smoke2sf_base100', 'smoke2sf_lr005_100ep', 0.799, 0.382, 0.416),
    'shwd2sf': ('shwd2sf_base100', 'shwd2sf_lr005_100ep', 1.038, 0.512, 0.526),
    'a2d15': ('a2d15_base100', 'a2d15_lr005_100ep', 0.534, 0.262, 0.272),
    'dota15': ('dota15_base100', 'dota15_lr005_100ep', 0.868, 0.279, 0.589),
}


def find_runs():
    out = {}
    for root in ROOTS:
        if not os.path.isdir(root):
            print('   [缺根] %s' % root)
            continue
        for name in os.listdir(root):
            p = os.path.join(root, name, 'results.csv')
            if os.path.exists(p):
                out[name] = p
    return out


def series(path):
    rows = list(csv.DictReader(io.open(path, encoding='utf-8', errors='ignore')))
    def col(n):
        return np.array([float(r[n]) for r in rows]) if rows and n in rows[0] else None
    return col('metrics/mAP50-95(B)'), col('metrics/mAP50(B)')


def match(runs, pref):
    pat = re.compile(re.escape(pref) + r'(?:_s(\d+)n)?$')
    out = {}
    for name, path in runs.items():
        m = pat.match(name)
        if m:
            out[int(m.group(1)) if m.group(1) else 'unseeded'] = path
    return out


def premium_table(runs, idx):
    """idx=0 → mAP50-95，idx=1 → mAP50。返回 {cell: (n, {arm: mean_premium}, paired_diff)}"""
    res = {}
    for cell, (bp, sp, *_) in CELLS.items():
        b, s = match(runs, bp), match(runs, sp)
        seeds = sorted(set(b) & set(s), key=lambda x: (isinstance(x, str), x))
        if len(seeds) < 2:
            res[cell] = None
            continue
        per = {}
        for lab, m in (('base', b), ('strat', s)):
            vals = []
            for sd in seeds:
                a95, a50 = series(m[sd])
                arr = a95 if idx == 0 else a50
                vals.append((float(arr.max()) - float(arr[-1])) * 100)
            per[lab] = np.array(vals)
        res[cell] = (len(seeds), per['base'].mean(), per['strat'].mean(),
                     (per['base'] - per['strat']).mean(),
                     (per['base'] - per['strat']).std(ddof=1),
                     len(per['base']))
        res[cell] = dict(n=len(seeds), base=per['base'], strat=per['strat'])
    return res


runs = find_runs()
print('本地归档中带 results.csv 的 run 数：%d' % len(runs))
print()
t95 = premium_table(runs, 0)
t50 = premium_table(runs, 1)

print('=== 第一步：阳性对照（mAP50-95 必须复现已发表值）===')
ok_all = True
for cell, (bp, sp, pub_b, pub_s, pub_d) in CELLS.items():
    r = t95.get(cell)
    if not r:
        print('   %-9s **配对不足**' % cell)
        ok_all = False
        continue
    got_b, got_s = r['base'].mean(), r['strat'].mean()
    got_d = (r['base'] - r['strat']).mean()
    ok = (abs(got_b - pub_b) < 0.0015 and abs(got_s - pub_s) < 0.0015 and abs(got_d - pub_d) < 0.0015)
    ok_all &= ok
    print('   %-9s n=%-3d 已发表 base %+.3f/strat %+.3f/差 %+.3f → 复算 %+.3f/%+.3f/%+.3f  %s'
          % (cell, r['n'], pub_b, pub_s, pub_d, got_b, got_s, got_d, 'OK' if ok else '**不符**'))
print()
if not ok_all:
    sys.exit('!! 阳性对照未通过 —— 拒绝输出 AP50 结果（未经验证的管线不得发布数字）')
print('阳控通过 ⇒ 同一条代码路径换指标列，给出 AP50 敏感性：')
print()
print('%-9s %3s %12s %12s %12s %10s %8s' %
      ('cell', 'n', 'base AP50', 'strat AP50', '配对差 AP50', 't', 'p'))
rows_out = []
for cell in CELLS:
    r = t50.get(cell)
    if not r:
        continue
    b, s = r['base'], r['strat']
    d = b - s
    t, p = stats.ttest_rel(b, s)
    rows_out.append((cell, r['n'], b.mean(), s.mean(), d.mean(), t, p))
    print('%-9s %3d %+12.3f %+12.3f %+12.3f %10.2f %8.2g'
          % (cell, r['n'], b.mean(), s.mean(), d.mean(), t, p))
print()
print('=== 两指标并列（溢价均值，pp）===')
print('%-9s %22s %22s' % ('cell', 'mAP50-95 (base/strat)', 'AP50 (base/strat)'))
for cell in CELLS:
    a, b2 = t95.get(cell), t50.get(cell)
    if not (a and b2):
        continue
    print('%-9s %+10.3f / %+10.3f %12s %+10.3f / %+10.3f'
          % (cell, a['base'].mean(), a['strat'].mean(), '',
             b2['base'].mean(), b2['strat'].mean()))
print()
print('=== dota15 的升级集（n=10，含 E 盘升级 run）单独一节 ===')
print('   与表 1 已印值对照：base +0.941 / strat +0.492 / 差 +0.449（本节的集合与之**不完全相同**，故报残差）')
runs_esc = dict(runs)
for root in ESC_ROOTS:
    if os.path.isdir(root):
        for name in os.listdir(root):
            p = os.path.join(root, name, 'results.csv')
            if os.path.exists(p):
                runs_esc[name] = p
    else:
        print('   [缺根] %s' % root)
for idx, lab in ((0, 'mAP50-95'), (1, 'AP50')):
    t = premium_table(runs_esc, idx).get('dota15')
    if not t:
        print('   %s：配对不足' % lab)
        continue
    b, s = t['base'], t['strat']
    d = b - s
    tt, pp = stats.ttest_rel(b, s)
    print('   %-9s n=%d  base %+.3f / strat %+.3f / 差 %+.3f（t %.2f, p %.2g）'
          % (lab, t['n'], b.mean(), s.mean(), d.mean(), tt, pp))
