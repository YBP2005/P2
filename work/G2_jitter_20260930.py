#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""G2_jitter.py — 把「洁净重跑 vs 归档」的差拆成**训练抖动**与**可能的 reroute 效应**。

口径（预注册 G2 段说"否则报告新界"，本脚本给出报告新界所需的两个量）：
  * **抖动标尺**：同一 (arm, seed) 的两次洁净重跑之差 `|clean2 − clean1|`（同机、同日、同配方）
    —— 这是"同配置再跑一次"的不可复现性，**任何小于它的归档差都不能归因于 reroute**；
  * **待判差**：归档（含静默改路的读数）与 clean1 之差 `|archive − clean1|`。
  再报两者在同一 (arm, seed) 上的对比，以及 val 侧逐 epoch 的最大差（后者含训练轨迹整体漂移，只作参考）。

数据来源（都在 A 机）：台账 `/workspace/sio_b_results.csv`（`map` 列 = test mAP50-95，分数→pp）
+ 各 run 自己的 `results.csv`（val 逐 epoch）。

用法： python G2_jitter.py [--cell p_vistod15] [--out /workspace/G2_jitter_20260930.txt]
"""
import argparse
import csv
import io
import os
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def ledger(path):
    d = {}
    for line in io.open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split(',')
        if len(f) >= 5 and f[0].startswith('r'):
            try:
                d[f[0]] = float(f[4]) * 100.0
            except ValueError:
                pass
    return d


def val_curve(rd):
    p = os.path.join(rd, 'results.csv')
    if not os.path.exists(p):
        return {}
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return {}
    col = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if col is None:
        return {}
    out = {}
    for i, r in enumerate(rows, start=1):
        try:
            out[i] = float(r[col]) * 100.0
        except (TypeError, ValueError):
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cell', default='p_vistod15')
    ap.add_argument('--ledger', default='/workspace/sio_b_results.csv')
    ap.add_argument('--rundir', default='/workspace/runs')
    ap.add_argument('--out', default='/workspace/G2_jitter_20260930.txt')
    a = ap.parse_args()
    L = ledger(a.ledger)
    out = []
    def emit(s=''):
        out.append(s); print(s, flush=True)

    emit('=== G2：训练抖动 vs 归档差（cell=%s）===' % a.cell)
    emit('台账 %s' % a.ledger)
    emit('\narm          seed  归档T   clean1T  clean2T  |归档−clean1|  |clean2−clean1|  val逐epoch最大差(归档vs clean1)')
    jit, arc, vmax = [], [], []
    for arm in ('base100', 'lr005_100ep'):
        for s in (42, 43):
            arch = L.get('r10_%s_%s_3way_s%dn' % (a.cell, arm, s))
            c1 = L.get('r16_g2_clean_%s_%s_3way_s%dn' % (a.cell, arm, s))
            c2 = L.get('r16_g2_clean2_%s_%s_3way_s%dn' % (a.cell, arm, s))
            v_arch = val_curve(os.path.join(a.rundir, 'r10_%s_%s_3way_s%dn' % (a.cell, arm, s)))
            v_c1 = val_curve(os.path.join(a.rundir, 'r16_g2_clean_%s_%s_3way_s%dn' % (a.cell, arm, s)))
            common = sorted(set(v_arch) & set(v_c1))
            dm = max((abs(v_arch[e] - v_c1[e]) for e in common), default=float('nan'))
            da = abs(arch - c1) if (arch is not None and c1 is not None) else float('nan')
            dj = abs(c2 - c1) if (c2 is not None and c1 is not None) else float('nan')
            if da == da:
                arc.append(da)
            if dj == dj:
                jit.append(dj)
                vmax.append(dm)
            emit('%-12s %-5d %s %s %s  %13s  %14s  %s'
                 % (arm, s,
                    ('%.3f' % arch) if arch is not None else '—',
                    ('%.3f' % c1) if c1 is not None else '—',
                    ('%.3f' % c2) if c2 is not None else '—',
                    ('%.3f' % da) if da == da else '—',
                    ('%.3f' % dj) if dj == dj else '—',
                    ('%.3f' % dm) if dm == dm else '—'))

    if jit and arc:
        emit('\n--- 汇总（test 端点，pp）---')
        emit('训练抖动 |clean2 − clean1|：n=%d，均值 %.3f，最大 %.3f' % (len(jit), st.mean(jit), max(jit)))
        emit('待判差 |归档 − clean1|  ：n=%d，均值 %.3f，最大 %.3f' % (len(arc), st.mean(arc), max(arc)))
        emit('val 逐 epoch 最大差（归档 vs clean1）：均值 %.3f，最大 %.3f（含轨迹漂移，只作参考）'
             % (st.mean(vmax), max(vmax)))
        # 按每对 (arm, seed) 判定：待判差是否超过抖动
        emit('\n--- 逐对判定 ---')
        worse = 0
        for arm in ('base100', 'lr005_100ep'):
            for s in (42, 43):
                arch = L.get('r10_%s_%s_3way_s%dn' % (a.cell, arm, s))
                c1 = L.get('r16_g2_clean_%s_%s_3way_s%dn' % (a.cell, arm, s))
                c2 = L.get('r16_g2_clean2_%s_%s_3way_s%dn' % (a.cell, arm, s))
                if None in (arch, c1, c2):
                    continue
                da, dj = abs(arch - c1), abs(c2 - c1)
                verdict = ('归档差 ≤ 抖动 ⇒ 与 reroute **不可分辨**' if da <= dj
                           else '归档差 > 抖动 ⇒ 该对**超出**抖动标尺')
                if da > dj:
                    worse += 1
                emit('  %-12s s%-3d 归档差 %.3f vs 抖动 %.3f  ⇒ %s' % (arm, s, da, dj, verdict))
        emit('\n结论（描述性）：%d/4 对的归档差超过同配置抖动；'
             '若 0/4 超过，则 defect 10 的"≤0.05 pp 界"应改报为**按本批抖动量级的界**（均值 %.3f / 最大 %.3f pp），'
             '而不是继续沿用那个旧界。' % (worse, st.mean(jit), max(jit)))
    else:
        emit('\n（读数不全：clean2 还没跑完或台账缺行）')
    io.open(a.out, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n存证：%s' % a.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
