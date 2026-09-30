#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""g2_screen_20260930.py — G2 洁净重跑的**日志指纹筛查 + 与归档读数比对**。

判据（方案里已预注册）：洁净重跑与含静默改路的归档读数之差 **≤ 0.05 pp**；
否则报告新界并取代该格。本脚本只出数、出筛查结论，不写稿。

筛查（defect 10 的三种指纹，见补充材料 §10 defect 10）：
  ① 训练日志出现 `CUDA out of memory` / `Reducing to batch` ⇒ case (a) 配置级改路；
  ② 出现 `TaskAlignedAssigner` 且伴随 `using CPU` / `OutOfMemoryError` ⇒ case (b) 同 batch 改路；
  ③ 迭代进度分母在中途变化（32 → 16 的痕迹）⇒ 单 run 内 batch 不恒定。
比对：逐 (arm, seed) 打印归档 vs 洁净重跑的 `val` 末轮值与逐 epoch argmax 值（mAP50-95，pp）。

用法： python g2_screen_20260930.py --cell p_vistod15 [--rundir /workspace/runs]
"""
import argparse
import csv
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def val_curve(rd):
    p = os.path.join(rd, 'results.csv')
    if not os.path.exists(p):
        return []
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return []
    col = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if col is None:
        return []
    out = []
    for i, r in enumerate(rows, start=1):
        try:
            out.append((i, float(r[col]) * 100.0))
        except (TypeError, ValueError):
            pass
    return out


def screen(logpath, ref_dens=(5, 9, 15)):
    """→ (结论字符串, 命中的指纹列表, 观察到的迭代分母集合)

    ★ 2026-09-30 修正：旧版把"分母集合大小 ≤ 1"当作 CLEAN，结果把**合法**的三个分母
    （epoch 进度 / train 迭代 / val 迭代 = 5/9/15）判成 DIRTY —— 与"FAIL 0 被当成失败"同型的自伤。
    现在的判据是：**与已知良好分母集比对**（中途换批会引入 16/18/81 这类新分母 ⇒ 集合会变），
    并保留"OOM 字符串"这条硬指纹。
    """
    if not os.path.exists(logpath):
        return ('LOG-ABSENT', [], set())
    txt = io.open(logpath, encoding='utf-8', errors='replace').read()
    hits = []
    if re.search(r'CUDA out of memory', txt):
        hits.append('case-a:CUDA-out-of-memory')
    if re.search(r'Reducing to batch', txt):
        hits.append('case-a:Reducing-to-batch')
    if re.search(r'TaskAlignedAssigner', txt) and re.search(r'using CPU|OutOfMemoryError', txt):
        hits.append('case-b:TaskAlignedAssigner-on-CPU')
    dens = set()
    for m in re.finditer(r'(?<![\d/])(\d{1,3})/(\d{1,4})(?![\d/])', txt):
        num, den = int(m.group(1)), int(m.group(2))
        if den <= 200 and num <= den and den != 100:
            dens.add(den)
    unexpected = sorted(d for d in dens if d not in ref_dens)
    if unexpected:
        hits.append('denominator-set-unexpected:%s' % unexpected)
    verdict = 'CLEAN' if not hits else 'DIRTY'
    return (verdict, hits, dens)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cell', default='p_vistod15')
    ap.add_argument('--rundir', default='/workspace/runs')
    a = ap.parse_args()

    print('=== G2 洁净重跑筛查（cell=%s）===' % a.cell)
    worst = 0.0
    rows = []
    for arm, lr in (('base100', 0.001), ('lr005_100ep', 0.005)):
        for s in (42, 43):
            old = 'r10_%s_%s_3way_s%dn' % (a.cell, arm, s)
            new = 'r16_g2_clean_%s_%s_3way_s%dn' % (a.cell, arm, s)
            log = '/workspace/r16_g2_%s.log' % new
            verd, hits, dens = screen(log)
            vo, vn = val_curve(os.path.join(a.rundir, old)), val_curve(os.path.join(a.rundir, new))
            if not vo or not vn:
                print('  %-10s s%-3d 读数缺失（归档 %d 点 / 洁净 %d 点）' % (arm, s, len(vo), len(vn)))
                continue
            do = dict(vo); dn = dict(vn)
            same = sorted(set(do) & set(dn))
            dmax = max(abs(do[e] - dn[e]) for e in same)
            dstat = (do[max(do, key=lambda e: do[e])]
                     - dn[max(dn, key=lambda e: dn[e])])
            ok = dmax <= 0.05
            worst = max(worst, dmax)
            rows.append((arm, s, verd, dmax, ok))
            print('  %-10s s%-3d 筛查=%-5s 指纹=%-28s 分母=%s' %
                  (arm, s, verd, (','.join(hits) if hits else '无'), (sorted(dens) or '—')))
            print('             逐 epoch val 同轮最大差 = %.4f pp（%s）  逐-split 峰值差 = %+.4f pp'
                  % (dmax, '≤0.05 界内' if ok else '**超界**', dstat))
    print('--- 汇总：最大逐 epoch 差 %.4f pp；判定 %s ---'
          % (worst, '全部在 0.05 pp 界内' if worst <= 0.05 else '**有超界，需报新界**'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
