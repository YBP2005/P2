#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""g6_prem_analyze.py — 把 G6 的逐 epoch `test` 曲线与归档 `val` 曲线合成读数（只算数，不出判词）。

口径**照正文既有定义**（`work/b55v_metric_compare_20260928.py` 声明、Table 4 / §8.6 同口径）：
    prem_val  = 逐 epoch val argmax − 末轮        （val mAP50-95 来自各 run 的 `results.csv`）
    prem_test = `best.pt` − `last.pt` 的 test 读数（本次新评的逐 checkpoint test 曲线里取 best/last）
    WC        = prem_val − prem_test

另外给出**同一 checkpoint 网格上的对照口径**（G6 的 5-epoch 网格），避免"全 argmax"与"网格"混用：
    prem_val_grid   = 网格上 val argmax − 末轮
    prem_test_grid  = 同一网格点的 test 值 − 末轮
    oracle_test_gain= 网格上 test 最大值 − 末轮（test 侧 oracle，描述性）

并做**独立复核**：若给了归档 `matrix.csv`（含既有 best/last test 读数），逐 run 比对本次重评的
best/last test 值 → 不一致就点名（这是"新评测与归档旧读数是否对得上"的硬证据，不是自证）。

用法： python g6_prem_analyze.py --dir /workspace/g6_perepoch_20260930 \
          --list /workspace/g6_pull_list.tsv --rundir /workspace/runs \
          [--matrix /workspace/matrix.csv] [--out /workspace/g6_prem_20260930]
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
ARMS = ('lr005_100ep', 'lr005_30ep', 'base100', 'base30', 'base', 'lr005')


def parse_name(run):
    m = re.match(r'^r\d+_(.+?)_s(\d+)n$', run)
    if m:
        mid, seed = m.group(1), int(m.group(2))
        mid = re.sub(r'_(3way|20p)$', '', mid)
        for arm in ARMS:
            if mid.endswith('_' + arm):
                return (mid[:-(len(arm) + 1)], arm, seed)
        return (mid, '', seed)
    # 2026-10-02 回退分支：§13.1 这批 run 名不带 `r\d+_` 前缀
    # （如 t1b_aitodtovis_base100_s42n / g3_e200_base_s42n / g3ext_e50_lr005_s42n）。
    # 切法与上面**同一套规则**；加 'base'/'lr005' 到 ARMS 只为认这两种后缀，
    # 因为排在 base100/base30/lr005_*ep 之后，对原有前缀分支的行为**无影响**。
    m = re.match(r'^(.+?)_s(\d+)n$', run)
    if not m:
        return ('', '', '')
    mid, seed = m.group(1), int(m.group(2))
    mid = re.sub(r'_(3way|20p)$', '', mid)
    for arm in ARMS:
        if mid.endswith('_' + arm):
            return (mid[:-(len(arm) + 1)], arm, seed)
    return (mid, '', seed)


def val_curve(rd):
    """→ (list of (epoch, mAP50-95) 按行序, 最后一轮的 epoch)"""
    p = os.path.join(rd, 'results.csv')
    if not os.path.exists(p):
        return [], 0
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return [], 0
    col = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if col is None:
        return [], 0
    out = []
    for i, r in enumerate(rows, start=1):
        try:
            out.append((i, float(r[col]) * 100.0))
        except (TypeError, ValueError):
            pass
    return out, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='/workspace/g6_perepoch_20260930')
    ap.add_argument('--list', default='/workspace/g6_pull_list.tsv')
    ap.add_argument('--rundir', default='/workspace/runs')
    ap.add_argument('--matrix', default='')
    ap.add_argument('--out', default='/workspace/g6_prem_20260930')
    a = ap.parse_args()

    runs = []
    for line in io.open(a.list, encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) == 2 and f[0].strip():
            runs.append(f[0].strip())

    # ---- 逐 checkpoint test 读数 ----
    t = defaultdict(dict)          # run -> {ckpt: map50_95}
    ep_of = defaultdict(dict)      # run -> {ckpt: ckpt_epoch}
    for r in csv.DictReader(io.open(os.path.join(a.dir, 'g6_perepoch.csv'), encoding='utf-8')):
        if r['split'] != 'test':
            continue
        t[r['run']][r['ckpt']] = float(r['map50_95'])
        if r['ckpt_epoch']:
            ep_of[r['run']][r['ckpt']] = int(r['ckpt_epoch'])

    rows = []
    for run in runs:
        cell, arm, seed = parse_name(run)
        vc, n_ep = val_curve(os.path.join(a.rundir, run))
        if not vc:
            rows.append(dict(run=run, cell=cell, arm=arm, seed=seed, note='NO-VAL-CSV'))
            continue
        v_final = vc[-1][1]
        v_max_ep, v_max = max(vc, key=lambda z: z[1])
        prem_val = v_max - v_final
        T = t.get(run, {})
        t_final = T.get('last')
        t_best = T.get('best')
        prem_test_bl = (t_best - t_final) if (t_best is not None and t_final is not None) else None
        # 网格口径：只取 epoch 检查点（epoch{N} → 训完 N+1 轮）
        grid = sorted(((ep_of[run][c], float(v)) for c, v in T.items()
                       if c.startswith('epoch') and c in ep_of[run]))
        vmap = dict(vc)
        grid_both = [(e, v, vmap[e]) for e, v in grid if e in vmap]
        pg = None
        if grid_both:
            e_star = max(grid_both, key=lambda z: (z[2], -z[0]))[0]
            v_star = vmap[e_star]
            t_star = dict(grid)[e_star]
            pg = dict(ep_star=e_star, prem_val_grid=v_star - v_final,
                      prem_test_grid=t_star - t_final if t_final is not None else None,
                      oracle_test_gain=(max(v for _, v in grid) - t_final)
                      if t_final is not None else None)
        # 归档 matrix 复核
        rows.append(dict(run=run, cell=cell, arm=arm, seed=seed, epochs=n_ep,
                         v_final=v_final, v_max=v_max, v_max_ep=v_max_ep, prem_val=prem_val,
                         t_final=t_final, t_best=t_best, prem_test_bl=prem_test_bl,
                         n_ckpt=len(T), prem_val_grid=(pg['prem_val_grid'] if pg else None),
                         prem_test_grid=(pg['prem_test_grid'] if pg else None),
                         oracle_test_gain=(pg['oracle_test_gain'] if pg else None)))

    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    flat = a.out + '_per_run.csv'
    cols = ['run', 'cell', 'arm', 'seed', 'epochs', 'n_ckpt', 'v_final', 'v_max', 'v_max_ep',
            'prem_val', 't_final', 't_best', 'prem_test_bl', 'prem_val_grid', 'prem_test_grid',
            'oracle_test_gain', 'note']
    with io.open(flat, 'w', encoding='utf-8', newline='\n') as f:
        f.write(','.join(cols) + '\n')
        for r in rows:
            f.write(','.join('' if r.get(c) is None else str(r.get(c)) for c in cols) + '\n')

    # ---- 归档 matrix 复核 ----
    diffs, matched = [], 0
    if a.matrix and os.path.exists(a.matrix):
        arch = defaultdict(dict)
        for r in csv.DictReader(io.open(a.matrix, encoding='utf-8', errors='replace')):
            if r.get('split') == 'test':
                arch[r['run']][r['ckpt']] = float(r['map50_95'])
        for r in rows:
            for ck, key in (('best', 't_best'), ('last', 't_final')):
                mine, theirs = r.get(key), arch.get(r['run'], {}).get(ck)
                if mine is None or theirs is None:
                    continue
                d = abs(mine - theirs)
                matched += 1
                if d > 0.005:
                    diffs.append('%s %s mine=%.4f archive=%.4f Δ=%.4f' % (r['run'], ck, mine, theirs, d))
    # ---- 逐格汇总 ----
    grp = defaultdict(list)
    for r in rows:
        if r.get('prem_val') is None:
            continue
        grp[(r['cell'], r['arm'])].append(r)
    agg = []
    for (cell, arm), rs in sorted(grp.items()):
        pv = [x['prem_val'] for x in rs]
        pb = [x['prem_test_bl'] for x in rs if x['prem_test_bl'] is not None]
        pc = [x['prem_test_grid'] for x in rs if x['prem_test_grid'] is not None]
        agg.append((cell, arm, len(rs), st.mean(pv), st.mean(pb) if pb else None,
                    st.mean(pc) if pc else None,
                    (st.mean(pb) / st.mean(pv)) if (pb and st.mean(pv)) else None))

    with io.open(a.out + '_by_cell.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.write('# G6 逐 epoch test 读数（口径：prem_val = val argmax − 末轮；'
                'prem_test = best.pt − last.pt 的 test；网格口径见列名）\n')
        f.write('# cell\tarm\tn\tprem_val\tprem_test(best−last)\tprem_test(网格)\t兑现率\n')
        for cell, arm, n, pv, pb, pc, rate in agg:
            f.write('%s\t%s\t%d\t%.4f\t%s\t%s\t%s\n'
                    % (cell, arm, n, pv,
                       ('%.4f' % pb) if pb is not None else '—',
                       ('%.4f' % pc) if pc is not None else '—',
                       ('%.1f%%' % (rate * 100)) if rate is not None else '—'))
        f.write('\n# 归档 matrix 复核：比对 %d 个 best/last test 值，超差(>0.005 pp) %d 个\n'
                % (matched, len(diffs)))
        for d in diffs[:50]:
            f.write('DIFF\t%s\n' % d)

    print('逐 run 读数 → %s' % flat)
    print('逐格汇总   → %s_by_cell.txt' % a.out)
    print('--- 逐格（cell · arm · n · prem_val · prem_test(best−last) · prem_test(网格) · 兑现率）---')
    for cell, arm, n, pv, pb, pc, rate in agg:
        print('  %-14s %-12s n=%-3d prem_val=%+.4f  prem_test=%s  grid=%s  rate=%s'
              % (cell, arm, n, pv,
                 ('%+.4f' % pb) if pb is not None else '   —   ',
                 ('%+.4f' % pc) if pc is not None else '   —   ',
                 ('%.1f%%' % (rate * 100)) if rate is not None else '—'))
    print('归档 matrix 复核：比对 %d 个值，超差 %d 个' % (matched, len(diffs)))
    for d in diffs[:10]:
        print('  DIFF', d)


if __name__ == '__main__':
    main()
