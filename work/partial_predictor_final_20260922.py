# -*- coding: utf-8 -*-
"""甲档 B（定稿版）：在**正确口径**（共用 5-epoch 网格）上检验 Δgap 符号的部分预测器。

★ 口径更正（本脚本建立的）：
  释放件 `e_val_peak` **不是** 100-epoch 全曲线 argmax（那只 8/40 相符），
  而是**在 test 抽查共用的 epoch 网格上**取 val 峰 ⇒ 与 e_test_peak **同网格可比**（40/40 相符）。
  这一点很关键：**同网格是"峰位是否同轮"(same_epoch) 这个量有意义的前提**。

本脚本：
  ① 打印实际 epoch 网格（确认 5 的倍数）；
  ② 复算 same_epoch 与 e_val_peak / e_test_peak（口径自证）；
  ③ 报 same_epoch 对 gap 符号的判别力（置换检验）；
  ④ 把预测器写成**可用规则**：它的输入只需 val 与 test 各一条 5-epoch 网格曲线。
"""
import csv
import io
import os
import random
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
RUNS = r'E:\workplace\xeval_20260916\runs'
MAT = r'E:\workplace\xeval_perepoch_20260918\matrix_perepoch.csv'
REL = r'E:\workplace\实验内容共享\P2\02_论文释放件\release_selection-transfer_perseed.csv'
random.seed(42)

# ---------- ① 网格 ----------
grid = {}
tcurve = {}
for r in csv.DictReader(io.open(MAT, encoding='utf-8-sig')):
    if r['split'] != 'test':
        continue
    grid.setdefault(r['run'], set()).add(int(r['epoch']))
    tcurve.setdefault(r['run'], {})[int(r['epoch'])] = float(r['map50_95'])
sigs = Counter(tuple(sorted(v)) for v in grid.values())
print('  ===== ① test 抽查的 epoch 网格 =====')
for sig, c in sigs.most_common():
    print('   %-38s ×%d run' % (str(sig), c))
main_grid = sigs.most_common(1)[0][0]
print('   主网格：%s（%d 点）' % (str(main_grid), len(main_grid)))
print('   全部为 5 的倍数：%s' % all(e % 5 == 0 for e in main_grid))
print()

# ---------- val 曲线 ----------
val = {}
for f in sorted(os.listdir(RUNS)):
    if f.endswith('_results.csv'):
        val[f[:-len('_results.csv')]] = {
            int(r['epoch']): float(r['metrics/mAP50-95(B)'])
            for r in csv.DictReader(io.open(os.path.join(RUNS, f), encoding='utf-8-sig'))}
print('  val 曲线 %d run' % len(val))
print()

# ---------- ② 口径自证 ----------
rows = [r for r in csv.DictReader(io.open(REL, encoding='utf-8-sig')) if r['run'] in val]
okv = okt = 0
recs = []
for r in rows:
    run = r['run']
    g = sorted(grid.get(run, []))
    sub = {e: val[run][e] for e in g if e in val[run]}
    if not sub:
        continue
    vpk = max(sub, key=lambda e: sub[e])
    tpk = max(tcurve[run], key=lambda e: tcurve[run][e]) if tcurve.get(run) else None
    wantv, wantt = int(r['e_val_peak']), int(r['e_test_peak'])
    okv += (vpk == wantv)
    okt += (tpk == wantt)
    recs.append(dict(run=run, arm=r['arm'],
                     pv=float(r['prem_val_pp']), po=float(r['prem_test_oracle_pp']),
                     ps=float(r['prem_test_selected_pp']),
                     vpk=vpk, tpk=tpk, wantv=wantv, wantt=wantt,
                     same_file=r['same_epoch'].strip().lower() == 'true',
                     same_calc=(vpk == tpk),
                     same_grid=sub, tgrid={e: tcurve[run][e] for e in g if e in tcurve.get(run, {})}))
print('  ===== ② 口径自证（共用网格上取峰） =====')
print('   e_val_peak  一致 %d/%d' % (okv, len(recs)))
print('   e_test_peak 一致 %d/%d' % (okt, len(recs)))
same_agree = sum(1 for x in recs if x['same_file'] == x['same_calc'])
print('   same_epoch 与自算（峰位同轮）一致 %d/%d' % (same_agree, len(recs)))
print()

# ---------- ③ 判别力 ----------
for x in recs:
    x['gap'] = x['pv'] - x['ps']
gaps = [x['gap'] for x in recs]
npos = sum(1 for g in gaps if g > 0)
print('  ===== ③ gap = prem_val − prem_test_selected =====')
print('   n=%d 均值 %.4f pp；正值（val 侧高估）%d，非正 %d' % (
    len(gaps), sum(gaps) / len(gaps), npos, len(gaps) - npos))
same = [x['gap'] for x in recs if x['same_calc']]
diff = [x['gap'] for x in recs if not x['same_calc']]
print()
print('   峰位**同轮** n=%d：gap 均值 %+.4f pp 中位 %+.4f 为负者 %d' % (
    len(same), sum(same) / len(same) if same else 0, sorted(same)[len(same) // 2] if same else 0,
    sum(1 for g in same if g <= 0)))
print('   峰位**异轮** n=%d：gap 均值 %+.4f pp 中位 %+.4f 为负者 %d' % (
    len(diff), sum(diff) / len(diff) if diff else 0, sorted(diff)[len(diff) // 2] if diff else 0,
    sum(1 for g in diff if g <= 0)))
obs = abs(sum(same) / len(same) - sum(diff) / len(diff))
allg = gaps[:]
k = len(same)
cnt = 0
for _ in range(20000):
    random.shuffle(allg)
    if abs(sum(allg[:k]) / k - sum(allg[k:]) / (len(allg) - k)) >= obs:
        cnt += 1
print('   均值差 |%.4f| pp；置换 p = %.4f（20000 次）' % (obs, cnt / 20000))
print()

# 符号判别力
lab = [x['gap'] > 0 for x in recs]
feat = [1 if x['same_calc'] else 0 for x in recs]


def auc(v, l):
    P = [a for a, b in zip(v, l) if b]
    N = [a for a, b in zip(v, l) if not b]
    if not P or not N:
        return None
    c = sum(1 for a in P for b in N if a > b) + .5 * sum(1 for a in P for b in N if a == b)
    return c / (len(P) * len(N))


a = auc(feat, lab)
print('   "峰位同轮"对 gap>0 的 AUC = %s' % ('%.4f（同轮⇒更可能不为正）' % a if a else 'n/a'))
null = []
l2 = lab[:]
for _ in range(20000):
    random.shuffle(l2)
    z = auc(feat, l2)
    if z is not None:
        null.append(z)
null.sort()
p = sum(1 for z in null if abs(z - .5) >= abs(a - .5)) / len(null)
print('   置换 p = %.4f  ⇒ %s' % (p, '**有判别力**' if p < 0.05 else '未检出'))
print()

# ---------- ④ 可用规则 ----------
print('  ===== ④ 可用规则（输入：val 与 test 各一条 5-epoch 网格曲线） =====')
print('   R: 在**共用的 5-epoch 网格**上分别取 val 峰与 test 峰：')
print('      峰位同轮 ⇒ val 侧 premium 基本兑现（本批 n=%d，gap 均值 %+.4f pp）' % (len(same), sum(same) / len(same)))
print('      峰位异轮 ⇒ val 侧 premium **系统性不兑现**（本批 n=%d，gap 均值 %+.4f pp，置换 p=%.4f）'
      % (len(diff), sum(diff) / len(diff), cnt / 20000))
print('   这是**部分预测器**：只覆盖"峰位是否同轮"这一可观测条件，不解释 sign 的全部变异。')
print()
print('   ★ 本批局限（必须一起写进稿子，否则是过度声称）：')
print('     · n=40（同轮仅 %d）；' % len(same))
print('     · 响应是"兑现差额"，不是"符号"本身 —— 符号在被预测组内仍有个别反例；')
print('     · 同一网格依赖性：结论只在 5-epoch 抽查网格上成立，未在更细网格复核。')
