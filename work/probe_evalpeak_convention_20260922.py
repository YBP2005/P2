# -*- coding: utf-8 -*-
"""查清释放件 `e_val_peak` 的口径：为什么与"val 曲线直接 argmax"只有 8/40 相符。

线索：释放件的峰位常**晚于**直接 argmax（s42：65 vs 58），且落在 5 的倍数上（55/65/70/75/80/85/90）
⇒ 假设 H：`e_val_peak` 是**取窗口中位数/滚动均值后的峰位**（作者自己声明过 window-based median）。

逐条检验各候选口径，报各自命中率：
  H0 直接 argmax（无窗）
  H1 滚动中位数窗 w∈{3,5,7,9} 后 argmax
  H2 滚动均值窗 w∈{3,5,7,9} 后 argmax
  H3 取"首个达到峰值 99% 的 epoch"
  H4 取"最后达到峰值 99% 的 epoch"
并检查命中时是否**同轮**（精确相等）还是仅**邻近**（±5 内）。
"""
import csv
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
RUNS = r'E:\workplace\xeval_20260916\runs'
REL = r'E:\workplace\实验内容共享\P2\02_论文释放件\release_selection-transfer_perseed.csv'

val = {}
for f in sorted(os.listdir(RUNS)):
    if f.endswith('_results.csv'):
        run = f[:-len('_results.csv')]
        val[run] = {int(r['epoch']): float(r['metrics/mAP50-95(B)'])
                    for r in csv.DictReader(io.open(os.path.join(RUNS, f), encoding='utf-8-sig'))}

rows = [r for r in csv.DictReader(io.open(REL, encoding='utf-8-sig')) if r['run'] in val]
print('  可比 run：%d' % len(rows))


def roll(v, w, how):
    ep = sorted(v)
    out = {}
    for i, e in enumerate(ep):
        lo = max(0, i - w // 2)
        hi = min(len(ep), i + w // 2 + 1)
        win = [v[x] for x in ep[lo:hi]]
        out[e] = (sum(win) / len(win)) if how == 'mean' else sorted(win)[len(win) // 2]
    return out


def peak(d):
    # 并列时取**最早**（与常见实现一致）；另报取最晚的结果
    m = max(d.values())
    return min([e for e in d if d[e] == m])


CAND = [('H0 argmax(无窗)', lambda v: v)]
for w in (3, 5, 7, 9):
    CAND.append(('H1 滚动中位数 w=%d' % w, lambda v, w=w: roll(v, w, 'median')))
    CAND.append(('H2 滚动均值   w=%d' % w, lambda v, w=w: roll(v, w, 'mean')))
CAND.append(('H3 首个达峰 99%', lambda v: {e: x for e, x in v.items()
                                      if x >= max(v.values()) * 0.99}))

print()
print('   %-24s %8s %10s %10s' % ('口径', '精确命中', '±5 命中', '±10 命中'))
best = None
for tag, fn in CAND:
    ex = near5 = near10 = 0
    for r in rows:
        v = val[r['run']]
        try:
            got = peak(fn(v))
        except Exception:
            continue
        want = int(r['e_val_peak'])
        if got == want:
            ex += 1
        if abs(got - want) <= 5:
            near5 += 1
        if abs(got - want) <= 10:
            near10 += 1
    print('   %-24s %5d/%-3d %5d/%-4d %5d/%-4d' % (tag, ex, len(rows), near5, len(rows), near10, len(rows)))
    if best is None or ex > best[1]:
        best = (tag, ex)

print()
print('  ⇒ 最佳口径：%s（精确命中 %d/%d）' % (best[0], best[1], len(rows)))
print()

# 释放件峰位的取值分布（看是否落在 5 的倍数上 ⇒ 指向"只在抽查网格上取峰"）
peaks = sorted(int(r['e_val_peak']) for r in rows)
from collections import Counter
print('  释放件 e_val_peak 取值分布（前 20）：')
for e, c in sorted(Counter(peaks).items())[:20]:
    print('     %3d  ×%d   %s' % (e, c, '（5 的倍数）' if e % 5 == 0 else ''))
print('  为 5 的倍数者：%d/%d' % (sum(1 for p in peaks if p % 5 == 0), len(peaks)))
print()

# 关键交叉检验：把 test 侧抽查网格当作"公共网格"，在**该网格上**取 val 峰
import csv as _csv
MAT = r'E:\workplace\xeval_perepoch_20260918\matrix_perepoch.csv'
grid = {}
for r in _csv.DictReader(io.open(MAT, encoding='utf-8-sig')):
    grid.setdefault(r['run'], set()).add(int(r['epoch']))
print('  ===== 假设 H5：在 test 抽查的**同一 epoch 网格**上取 val 峰 =====')
ex = near5 = 0
details = []
for r in rows:
    run = r['run']
    g = grid.get(run)
    if not g:
        continue
    v = val[run]
    sub = {e: v[e] for e in sorted(g) if e in v}
    if not sub:
        continue
    got = peak(sub)
    want = int(r['e_val_peak'])
    details.append((run, want, got, abs(got - want)))
    if got == want:
        ex += 1
    if abs(got - want) <= 5:
        near5 += 1
print('   精确命中 %d/%d；±5 命中 %d/%d' % (ex, len(details), near5, len(details)))
for d in details[:8]:
    print('     %-38s 释放件 %3d  网格 argmax %3d  差 %d' % d)
