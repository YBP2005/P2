# -*- coding: utf-8 -*-
"""B55 · 把 **val 半列**（本次新评）与 **test 半列**（2026-09-27）按**同一对检查点**（best / last）配对。

问的是同一件事在两半上的读数：
  prem_X = mAP75(best) − mAP75(last)      X ∈ {val, test}
  ⇒ 「峰值到末点的落差」在 val 上有多大、在 test 上兑现了多少（ratio = prem_test / prem_val）。

输入（全部本地）：
  scratch/b55v_summary.csv                本次 val 半列逐 run 汇总（含 map75_best / map75_last / prem_val_*）
  scratch/b55_m75_s0.csv, b55_m75_s1.csv  2026-09-27 的 test 半列逐 (run, ckpt) 读数
输出：markdown 报告（stdout）。
"""
import csv
import io
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p, enc='utf-8-sig'):
    return list(csv.DictReader(io.open(p, encoding=enc, errors='replace')))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


val = {}
for r in rd(os.path.join(HERE, 'b55v_summary.csv')):
    if r.get('run'):
        val[r['run']] = r

test = {}
for fn in ('b55_m75_s0.csv', 'b55_m75_s1.csv'):
    p = os.path.join(HERE, fn)
    if os.path.exists(p):
        for r in rd(p):
            if r.get('ckpt') and r.get('map75') and not str(r['map75']).startswith('FAIL'):
                test.setdefault(r['run'], {})[r['ckpt']] = float(r['map75'])

FAM = [('shwd2sf', 'base100'), ('shwd2sf', 'lr005_100ep'),
       ('smoke2sf', 'base100'), ('smoke2sf', 'lr005_100ep')]

print('# B55 · val 半列 × test 半列（同检查点配对，mAP75）\n')
print('| 项 | 值 |')
print('|---|---|')
print('| val 半列覆盖 run | %d（四族各 10 种子）|' % len(val))
print('| test 半列覆盖 run | %d |' % len(test))
both = [r for r in val if r in test and 'best' in test[r] and 'last' in test[r]]
print('| 两半都有 best 与 last 的 run | **%d** |' % len(both))

rows = []
for rn in both:
    v, t = val[rn], test[rn]
    pv = f(v['prem_val_best_last'])
    pt = t['best'] - t['last']
    pg = f(v['prem_val_grid_75'])
    rows.append(dict(run=rn, cell=v['cell'], arm=v['arm'], seed=v['seed'],
                     val_best=f(v['map75_best']), val_last=f(v['map75_last']),
                     test_best=t['best'], test_last=t['last'],
                     prem_val=pv, prem_test=pt, prem_val_grid=pg,
                     ratio=(pt / pv) if (pv not in (None, 0) and abs(pv) > 0.05) else None))

print('\n## 1 逐族（mAP75，单位 pp）\n')
print('| cell | arm | n | val: best | val: last | **prem_val** | test: best | test: last | **prem_test** | ratio=test/val |')
print('|---|---|---|---|---|---|---|---|---|---|')
for cell, arm in FAM:
    ss = [r for r in rows if r['cell'] == cell and r['arm'] == arm]
    if not ss:
        continue
    rr = [r['ratio'] for r in ss if r['ratio'] is not None]

    def m(k):
        xs = [r[k] for r in ss if r[k] is not None]
        return st.mean(xs) if xs else float('nan')
    print('| %s | %s | %d | %.4f | %.4f | **%+.4f** | %.4f | %.4f | **%+.4f** | %s |' % (
        cell, arm, len(ss), m('val_best'), m('val_last'), m('prem_val'),
        m('test_best'), m('test_last'), m('prem_test'),
        ('%+.3f' % st.mean(rr)) if rr else 'n/a'))

allpv = [r['prem_val'] for r in rows if r['prem_val'] is not None]
allpt = [r['prem_test'] for r in rows if r['prem_test'] is not None]
allr = [r['ratio'] for r in rows if r['ratio'] is not None]
print('| **合计** | | %d | | | **%+.4f** | | | **%+.4f** | %s |' % (
    len(rows), st.mean(allpv), st.mean(allpt),
    ('%+.3f（中位 %+.3f，n=%d）' % (st.mean(allr), st.median(allr), len(allr))) if allr else 'n/a'))

pv_pos = sum(1 for r in rows if r['prem_val'] is not None and r['prem_val'] > 0)
pt_pos = sum(1 for r in rows if r['prem_test'] is not None and r['prem_test'] > 0)
c_pp = sum(1 for r in rows if r['prem_val'] is not None and r['prem_test'] is not None
           and r['prem_val'] > 0 and r['prem_test'] > 0)
c_pn = sum(1 for r in rows if r['prem_val'] is not None and r['prem_test'] is not None
           and r['prem_val'] > 0 and r['prem_test'] <= 0)
c_np = sum(1 for r in rows if r['prem_val'] is not None and r['prem_test'] is not None
           and r['prem_val'] <= 0 and r['prem_test'] > 0)
c_nn = sum(1 for r in rows if r['prem_val'] is not None and r['prem_test'] is not None
           and r['prem_val'] <= 0 and r['prem_test'] <= 0)

print('\n## 2 符号与兑现（n=%d）\n' % len(rows))
print('| 量 | 值 |')
print('|---|---|')
print('| prem_val > 0（val 上峰值确实高于末点） | %d/%d |' % (pv_pos, len(rows)))
print('| prem_test > 0（test 上兑现为正） | %d/%d |' % (pt_pos, len(rows)))
print('| 两半同为正 (val>0, test>0) | %d |' % c_pp)
print('| val>0 而 test≤0（未兑现） | %d |' % c_pn)
print('| val≤0 而 test>0 | %d |' % c_np)
print('| 两半同为非正 | %d |' % c_nn)
print('| prem_val 均值 / prem_test 均值 | %+.4f / %+.4f pp |' % (st.mean(allpv), st.mean(allpt)))
print('| 均值之比 prem_test均值 / prem_val均值 | %+.3f |' % (st.mean(allpt) / st.mean(allpv)))

print('\n## 3 逐 run（前 12 行示例，全量见 CS）\n')
print('| run | prem_val | prem_test | ratio |')
print('|---|---|---|---|')
for r in sorted(rows, key=lambda x: -(x['prem_test'] or 0))[:12]:
    print('| %s | %+.4f | %+.4f | %s |' % (r['run'], r['prem_val'], r['prem_test'],
                                           ('%+.3f' % r['ratio']) if r['ratio'] is not None else 'n/a'))

out = os.path.join(HERE, 'b55v_pair_rows.csv')
with io.open(out, 'w', encoding='utf-8', newline='\n') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print('\n逐 run 配对明细 → %s（%d 行）' % (os.path.basename(out), len(rows)))
