# -*- coding: utf-8 -*-
"""B 机单机 clean 四预算串（E=50/100/200/400）与判据 C1–C3 复算。

口径严格照 `work/preregister_E_ext_20260919.py`：
  premium = max_e V(e) − V(末轮)，V = val 的 mAP50-95 ×100（逐 epoch 读 results.csv）
  C1：四预算均值单调不减，且每个 run 的 premium 对 ln E 回归 斜率>0 且 p<0.05
  C2：premium(400)/premium(100) ∈ [0.86, 1.43]
  C3：|mean(ê/E)(400) − mean(ê/E)(100)| ≤ 0.05
只读本地 CSV，不写任何文件。
"""
import csv
import io
import math
import os
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')

D = r'E:\workplace\g3cleanb_20260925'
# 预算 -> 本地文件名模板（全部来自 B 机 /workspace/runs/）
TPL = {
    50: 'g3cleanb_e50_%s_s%dn__results.csv',
    100: 'g3clean_e100_%s_s%dn__results.csv',
    200: 'g3clean_e200_%s_s%dn__results.csv',
    400: 'g3cleanb_e400_%s_s%dn__results.csv',
}
ARMS = ('base', 'lr005')
SEEDS = range(42, 47)


def load(path):
    if not os.path.exists(path):
        return None
    rows = list(csv.DictReader(io.open(path, encoding='utf-8', errors='replace')))
    if not rows:
        return None
    col = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if col is None:
        return None
    ep = [int(float(r['epoch'])) for r in rows]
    v = [float(r[col]) * 100.0 for r in rows]
    return ep, v


def stats(vals):
    m = st.mean(vals)
    sd = st.stdev(vals) if len(vals) > 1 else 0.0
    se = sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return m, sd, se


def t_p(two_tailed_t, df):
    from scipy import stats as ss
    return 2.0 * (1.0 - ss.t.cdf(abs(two_tailed_t), df))


per = {}          # (E, arm) -> list of premiums
shape = {}        # (E, arm) -> list of ê/E
detail = []
for E, tpl in TPL.items():
    for arm in ARMS:
        for sd in SEEDS:
            p = os.path.join(D, tpl % (arm, sd))
            r = load(p)
            if r is None:
                detail.append((E, arm, sd, None, None, None))
                continue
            ep, v = r
            pk = max(range(len(v)), key=lambda i: v[i])
            prem = v[pk] - v[-1]
            sh = float(ep[pk]) / float(E)
            per.setdefault((E, arm), []).append(prem)
            shape.setdefault((E, arm), []).append(sh)
            detail.append((E, arm, sd, prem, ep[pk], len(ep)))

print('=' * 104)
print('逐 run：premium = max V − V(末轮)（pp）；pk = 峰值轮；rows = results.csv 行数（<E 即早停）')
print('=' * 104)
print('%-5s %-7s %-5s %10s %6s %6s' % ('E', 'arm', 'seed', 'premium', 'pk', 'rows'))
for E, arm, sd, prem, pk, rows in detail:
    print('%-5d %-7s %-5d %10s %6s %6s'
          % (E, arm, sd, '—' if prem is None else '%+.4f' % prem,
             '—' if pk is None else pk, '—' if rows is None else rows))

print()
print('=' * 104)
print('每预算（臂内均值，再两臂等权）')
print('=' * 104)
series = {}
print('%-6s %-22s %-22s %-22s' % ('E', 'base mean (n)', 'lr005 mean (n)', '臂等权'))
for E in sorted(TPL):
    cell = {}
    for arm in ARMS:
        vs = per.get((E, arm), [])
        cell[arm] = stats(vs) if vs else None
    if all(cell[a] for a in ARMS):
        eq = (cell['base'][0] + cell['lr005'][0]) / 2.0
        series[E] = eq
        print('%-6d %-22s %-22s %+.4f'
              % (E, '%+.4f (n=%d)' % (cell['base'][0], len(per[(E, 'base')])),
                 '%+.4f (n=%d)' % (cell['lr005'][0], len(per[(E, 'lr005')])), eq))
    else:
        print('%-6d %-22s %-22s %s' % (E, '—', '—', '数据不全'))

print()
print('=' * 104)
print('判据')
print('=' * 104)
if len(series) == 4:
    ks = sorted(series)
    seq = [series[k] for k in ks]
    mono = all(seq[i] <= seq[i + 1] + 1e-12 for i in range(3))
    print('C1a 单调不减: %s   序列 %s' % (mono, ' / '.join('%+.4f' % x for x in seq)))

    xs, ys = [], []
    for (E, arm), vs in per.items():
        for v in vs:
            xs.append(math.log(E))
            ys.append(v)
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    dof = n - 2
    s2 = sum(r * r for r in resid) / dof
    se = math.sqrt(s2 / sxx)
    t = b / se
    p = t_p(t, dof)
    print('C1b 每 run premium ~ ln E: n=%d 斜率 %+.4f (se %.4f)  t=%.3f  p=%.4g  ⇒ %s'
          % (n, b, se, t, p, 'met' if (b > 0 and p < 0.05) else 'not met'))

    r_ = series[400] / series[100]
    print('C2  premium(400)/premium(100) = %+.4f / %+.4f = %.4f  预测 1.141  带 [0.86, 1.43] ⇒ %s'
          % (series[400], series[100], r_, '带内（该缩放复活，须重新审视撤回）' if 0.86 <= r_ <= 1.43 else '带外（形状读法成立）'))

    s400 = [st.mean(shape[(400, a)]) for a in ARMS if shape.get((400, a))]
    s100 = [st.mean(shape[(100, a)]) for a in ARMS if shape.get((100, a))]
    if s400 and s100:
        m4, m1 = st.mean(s400), st.mean(s100)
        d = abs(m4 - m1)
        print('C3  形状对照 ê/E: E=400 %.3f  E=100 %.3f  |Δ| = %.3f （阈值 0.05）⇒ %s'
              % (m4, m1, d, 'pass' if d <= 0.05 else 'FAIL（本轮比较被形状混淆）'))
else:
    print('四预算数据不全，判据待 E=400 跑完。')
