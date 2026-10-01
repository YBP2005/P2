# -*- coding: utf-8 -*-
"""第 2 项定稿计算（与论文 Table 4 **同口径**）。

口径（由 `verify_table4_convention_20260925.py` 复现判定，最大偏差 0.0004）：
    prem_val  = 逐 epoch argmax − 末轮（V = val mAP50-95 × 100，来自各 run 的 results.csv）
    prem_test = best.pt − last.pt 的 test 读数
40 个既有 run 的曲线在 xeval_20260916/runs/；aitod20 的 10 个在 aitod20_n10_20260924/。
"""
import csv
import glob
import io
import os
import random
import re
import statistics as st
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
import os as _os
_ROOT = _os.environ.get('P2_ROOT') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
REL = _os.path.join(_ROOT, '02_release_data')
XEV = _os.path.join(REL, 'xeval_20260916')
AIN = _os.path.join(REL, 'aitod20_n10_20260924')
X4F = _os.path.join(REL, 'x4fill_20260925', 'x4fill_20260925.csv')
NBOOT = 20000

rd = lambda p: list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))

# ---- prem_test：matrix（40 既有 + s42）→ x4fill(B) → x4(A) ----
Mt = {}
for r in rd(os.path.join(REL, 'matrix.csv')):
    Mt.setdefault(r['run'], {})[(r['ckpt'], r['split'])] = float(r['map50_95'])
test_prem = {}
for n, d in Mt.items():
    if ('best', 'test') in d and ('last', 'test') in d:
        test_prem[n] = d[('best', 'test')] - d[('last', 'test')]
for r in rd(os.path.join(AIN, 'x4_teval.csv')):
    if r['split'] == 'test':
        test_prem.setdefault(r['run'], {})
for f in (X4F,):
    for r in rd(f):
        if r['split'] == 'test':
            test_prem.setdefault(r['run'], {})
tb, tl = {}, {}
for r in rd(os.path.join(AIN, 'x4_teval.csv')):
    if r['split'] == 'test':
        tb.setdefault(r['run'], {})[r['ckpt']] = float(r['map50_95'])
for r in rd(X4F):
    if r['split'] == 'test':
        tb.setdefault(r['run'], {})[r['ckpt']] = float(r['map50_95'])
for n, v in tb.items():
    if 'best' in v and 'last' in v:
        test_prem[n] = v['best'] - v['last']

# ---- prem_val：逐 epoch argmax − 末轮 ----
val_prem, ep_of = {}, {}
files = glob.glob(os.path.join(XEV, 'runs', '*results.csv')) + \
    glob.glob(os.path.join(AIN, '*__results.csv'))
for f in files:
    name = os.path.basename(f).replace('__results.csv', '').replace('_results.csv', '')
    rows = rd(f)
    if not rows:
        continue
    c95 = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if c95 is None:
        continue
    c = [float(x[c95]) * 100 for x in rows]
    i = max(range(len(c)), key=lambda k: c[k])
    val_prem[name] = c[i] - c[-1]
    ep_of[name] = (i + 1, len(c))

print('prem_val 曲线 run 数：%d；prem_test run 数：%d' % (len(val_prem), len(test_prem)))


def cell_of(n):
    arm = 'strat' if 'lr005' in n else 'base'
    x = n.replace('_lr005_100ep', '').replace('_base100', '').replace('_base30', '')
    x = x.replace('r10_', '').replace('_3way', '')
    return re.sub(r'_s\d+n$', '', x), arm


def build(names):
    c = defaultdict(list)
    for n in names:
        if n in val_prem and n in test_prem:
            c[cell_of(n)].append((val_prem[n], test_prem[n]))
    return c


def est(c, kind='rw', big=False):
    sel = {k: v for k, v in c.items() if (len(v) >= 5 or not big)}
    if not sel:
        return float('nan')
    if kind == 'eq':
        return 100 * st.mean(st.mean(x[1] for x in v) for v in sel.values()) / \
            st.mean(st.mean(x[0] for x in v) for v in sel.values())
    return 100 * st.mean(x[1] for v in sel.values() for x in v) / \
        st.mean(x[0] for v in sel.values() for x in v)


TBL = {('shwd2sf', 'base'): (1.469, 0.735, 50), ('shwd2sf', 'strat'): (0.865, 0.151, 18),
       ('smoke2sf', 'base'): (0.691, 0.507, 73), ('smoke2sf', 'strat'): (0.605, -0.158, -26),
       ('aitod20', 'base'): (0.786, -0.377, -48)}

base41 = [n for n in val_prem if not n.startswith('r10_aitod20')] + ['r10_aitod20_base30_3way_s42n']
ext50 = [n for n in val_prem if not n.startswith('r10_aitod20')] + \
    [n for n in val_prem if n.startswith('r10_aitod20')]

print()
print('=== ① 复现 Table 4（41 run 口径；应逐行对上印刷值）===')
c41 = build(base41)
print('  %-12s %-6s %3s  %-9s %-9s %-9s  %-22s' % ('cell', 'arm', 'n', 'prem_val', 'prem_test', 'rate', 'Table 4 印'))
okmax = 0.0
for k in sorted(c41):
    v = c41[k]
    mv, mt = st.mean(x[0] for x in v), st.mean(x[1] for x in v)
    t = TBL[k]
    okmax = max(okmax, abs(mv - t[0]), abs(mt - t[1]))
    print('  %-12s %-6s %3d  %+9.4f %+9.4f %+8.1f %%   %+.3f/%+.3f/%+d %%'
          % (k[0], k[1], len(v), mv, mt, 100 * mt / mv, t[0], t[1], t[2]))
print('  ⇒ 与印刷值的最大偏差 = %.4f pp' % okmax)

print()
print('=== ② 兑现率 ===')
print('  41 run（现状，aitod n=1）：① 臂格等权 %.2f %%   ② run 加权 %.2f %%'
      % (est(c41, 'eq'), est(c41, 'rw')))
c50 = build(ext50)
print('  50 run（扩展，每格 n=10）：① %.2f %%   ② %.2f %%   ③ 只取 n≥5 格 %.2f %%'
      % (est(c50, 'eq'), est(c50, 'rw'), est(c50, 'rw', big=True)))

print()
print('=== ③ 逐格（50 run，供新的 Table 4）===')
print('  %-12s %-6s %3s  %-9s %-9s %-8s' % ('cell', 'arm', 'n', 'prem_val', 'prem_test', 'rate'))
for k in sorted(c50):
    v = c50[k]
    mv, mt = st.mean(x[0] for x in v), st.mean(x[1] for x in v)
    print('  %-12s %-6s %3d  %+9.4f %+9.4f %+7.1f %%' % (k[0], k[1], len(v), mv, mt, 100 * mt / mv))

print()
print('=== ④ aitod20 格逐 seed（口径：argmax val / best-last test）===')
for s in range(42, 52):
    n = 'r10_aitod20_base30_3way_s%dn' % s
    i, T = ep_of[n]
    print('  s%-3d prem_val %+.4f (argmax@ep%d/%d)  prem_test %+.4f' % (s, val_prem[n], i, T, test_prem[n]))
av = [val_prem['r10_aitod20_base30_3way_s%dn' % s] for s in range(42, 52)]
at = [test_prem['r10_aitod20_base30_3way_s%dn' % s] for s in range(42, 52)]
print('  mean prem_val %+.4f (sd %.4f, 正 %d/10)  mean prem_test %+.4f (sd %.4f, 负 %d/10)  rate %+.1f %%'
      % (st.mean(av), st.stdev(av), sum(1 for x in av if x > 0),
         st.mean(at), st.stdev(at), sum(1 for x in at if x < 0), 100 * st.mean(at) / st.mean(av)))

print()
print('=== ⑤ 41 run 的两个既有数字（应对上论文现印）===')
V41 = st.mean(x[0] for v in c41.values() for x in v)
T41 = st.mean(x[1] for v in c41.values() for x in v)
print('  prem_val mean %+.4f  prem_test mean %+.4f  rate %.2f %%   （论文印 +0.896 / +0.293 / 32.7 %%）'
      % (V41, T41, 100 * T41 / V41))
V50 = st.mean(x[0] for v in c50.values() for x in v)
T50 = st.mean(x[1] for v in c50.values() for x in v)
print('  50 run：prem_val mean %+.4f  prem_test mean %+.4f' % (V50, T50))

rng = random.Random(20260925)
print()
print('=== ⑥ 自助 95 %% 区间（B=%d）===' % NBOOT)
for kind, lab in (('rw', '② run 加权（run 级重抽）'), ('eq', '① 臂格等权（cell 级重抽，5 簇）')):
    for c, tag in ((c41, '41 run'), (c50, '50 run')):
        keys = list(c)
        boots = []
        for _ in range(NBOOT):
            if kind == 'rw':
                pool = [x for v in c.values() for x in v]
                s = [rng.choice(pool) for _ in pool]
                boots.append(100 * st.mean(x[1] for x in s) / st.mean(x[0] for x in s))
            else:
                vs, ts = [], []
                for k in [rng.choice(keys) for _ in keys]:
                    v = c[k]
                    s = [rng.choice(v) for _ in v]
                    vs.append(st.mean(x[0] for x in s))
                    ts.append(st.mean(x[1] for x in s))
                boots.append(100 * st.mean(ts) / st.mean(vs))
        boots.sort()
        print('  %-26s %-7s %6.2f %%  CI95 [%6.2f, %6.2f]  P(≤0)=%.3f'
              % (lab, tag, est(c, kind), boots[int(.025 * NBOOT)], boots[int(.975 * NBOOT)],
                 sum(1 for b in boots if b <= 0) / NBOOT))
