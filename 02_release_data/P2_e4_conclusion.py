#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""e4_conclusion.py —— 读 /workspace/e4_se.csv，出 E4 的判据结论。

判据（评审原文）：
  * 逐端点 **SE ≥ 0.15 pp** ⇒ S34 的 prem_val = +0.0809 pp 与 Table S46 的 +0.075 pp **落在评测噪声内**
    ⇒ §6.5 的量级句改为**只讲符号**（评审明确说这算**对论文有利**）；
  * **SE ≤ 0.05 pp** ⇒ 包内数字维持现状。
另报 prem_test 的诱导 SE（= sqrt(SE_best² + SE_last²)）与兑现率的诱导 SE。
"""
import csv, io, math, os, statistics as st, sys
sys.stdout.reconfigure(encoding='utf-8')
F = '/workspace/e4_se.csv'
rows = list(csv.DictReader(io.open(F, encoding='utf-8'))) if os.path.isfile(F) else []
print('端点数 =', len(rows))
se = [float(r['se']) for r in rows]
if se:
    print('逐端点 SE：中位 %.4f pp · 均值 %.4f · 范围 [%.4f, %.4f] pp' % (st.median(se), st.mean(se), min(se), max(se)))
by = {}
for r in rows:
    by.setdefault(r['run'], {})[r['ckpt']] = float(r['se'])
pt = [math.sqrt(v['best']**2 + v['last']**2) for v in by.values() if 'best' in v and 'last' in v]
if pt:
    print('prem_test 的诱导 SE（n=%d）：中位 %.4f pp · 范围 [%.4f, %.4f]' % (len(pt), st.median(pt), min(pt), max(pt)))
m = st.median(se) if se else float('nan')
print()
print('判据对照：')
print('  ≥ 0.15 pp ？ %s' % (m >= 0.15))
print('  ≤ 0.05 pp ？ %s' % (m <= 0.05))
if m >= 0.15:
    print('  ⇒ 结论：**端点噪声 ≥ 0.15 pp ⇒ S34/S46 的量级句应改为只讲符号**（对论文有利）。')
elif m <= 0.05:
    print('  ⇒ 结论：**噪声 ≤ 0.05 pp ⇒ 包内数字维持现状**。')
else:
    print('  ⇒ 结论：落在两者之间（0.05–0.15 pp）⇒ 量级句可保留，但应写明端点 SE 的量级。')
