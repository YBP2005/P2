# -*- coding: utf-8 -*-
"""B51 收口汇总：逐片 CSV → 去重 → 覆盖率 + FAIL 归因 + 子采样敏感性网格。

任务键 = (cell, arm, run, ckpt, pct, draw)。B51 的测量是：同一个 run 的同一 ckpt，在**不同大小的
test-carve 子采样**（pct = 抽多少比例、draw = 第几次抽样、n = 子采样图数）上重评，
看"test 侧读数（以及 best−last 的溢价）"对 carve 大小有多敏感。
"""
import collections
import csv
import glob
import io
import os
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda p: list(csv.DictReader(io.open(p, encoding='utf-8-sig', errors='replace')))

rows = []
for f in sorted(glob.glob(os.path.join(HERE, 'b51_s*.csv'))):
    rows += rd(f)
print('原始行 %d（来自 %d 个 CSV）' % (len(rows), len(glob.glob(os.path.join(HERE, 'b51_s*.csv')))))

key = lambda r: (r['cell'], r['arm'], r['run'], r['ckpt'], r['pct'], r['draw'])
seen, uniq = set(), []
for r in rows:
    k = key(r)
    if k in seen:
        continue
    seen.add(k)
    uniq.append(r)
ok = [r for r in uniq if not r['map50_95'].startswith('FAIL')]
bad = [r for r in uniq if r['map50_95'].startswith('FAIL')]
print('去重后 %d 条：成功 **%d** / FAIL **%d**（合计 %d = 计划任务数）' % (len(uniq), len(ok), len(bad), len(uniq)))

print('\n=== FAIL 归因（权重不在 B 上的 run）===')
c = collections.Counter((r['run'], r['map50_95']) for r in bad)
for (run, why), n in c.most_common(12):
    print('  %-46s %-24s x%d' % (run, why, n))
print('  受影响 run 数 = %d' % len({r['run'] for r in bad}))

print('\n=== 覆盖的 run / cell ===')
print('  成功覆盖 run 数 = %d；cell 分布 = %s'
      % (len({r['run'] for r in ok}), dict(collections.Counter(r['cell'] for r in ok))))

print('\n=== 子采样网格（pct × draw）===')
g = collections.defaultdict(list)
for r in ok:
    g[(r['pct'], r['draw'])].append(r)
print('  网格点数 = %d；pct 取值 = %s' % (len(g), sorted({r['pct'] for r in ok}, key=int)))
print('  %-5s %-5s %-7s %-8s %s' % ('pct', 'draw', 'n图', 'n行', 'mean mAP50-95'))
for k in sorted(g, key=lambda t: (int(t[0]), int(t[1])))[:14]:
    v = [float(r['map50_95']) for r in g[k]]
    print('  %-5s %-5s %-7s %-8d %.4f' % (k[0], k[1], g[k][0]['n'], len(v), st.mean(v)))
print('  …（共 %d 个网格点）' % len(g))

# ---- best − last 的溢价：同一 (run, pct, draw) 上配对 ----
pair = collections.defaultdict(dict)
for r in ok:
    pair[(r['run'], r['pct'], r['draw'])][r['ckpt']] = float(r['map50_95'])
full = {}
for k, d in pair.items():
    if 'best' in d and 'last' in d:
        full.setdefault(k[1:], []).append(d['best'] - d['last'])
print('\n=== best − last 溢价（按 carve 大小聚合；与全测试集读数的比较留给正文口径）===')
for pct in sorted({k[0] for k in full}, key=int):
    v = [x for k in full if k[0] == pct for x in full[k]]
    print('  pct=%-4s 配对数 %-4d 均值 %+0.4f pp  中位 %+0.4f  sd %.4f  正 %d/%d'
          % (pct, len(v), st.mean(v), st.median(v), st.stdev(v) if len(v) > 1 else 0,
             sum(1 for x in v if x > 0), len(v)))
out = os.path.join(HERE, 'b51_summary.txt')
io.open(out, 'w', encoding='utf-8', newline='\n').write(
    'uniq=%d ok=%d fail=%d runs_ok=%d grid=%d\n'
    % (len(uniq), len(ok), len(bad), len({r['run'] for r in ok}), len(g)))
print('\n摘要 → %s' % out)
