#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ctrldrift_check.py — **环境漂移对照**：把一条"今天重跑的归档配置"与它当年的归档读数比对。

为什么需要：G2 显示 `p_vistod15` 的归档读数与今天的洁净重跑差到 **0.150 pp**（端点），而**同配置两次
独立重跑逐位相同（抖动 0.000 pp）**、`args.yaml` 逐字段相同。⇒ 这个差要么是 defect 10 的 reroute，
要么是**环境漂移**（torch/cuDNN/ultralytics 构建或数据文件在这半个月变了）。
本脚本比对一条**当年确定无显存压力**的归档配置（初始化实验的 stage-2：`src1_base100`）与今天重跑的同一配置：
  * 若两者几乎无差 ⇒ 环境稳定 ⇒ `p_vistod15` 的差可**归因于 reroute**；
  * 若也差 ~0.1–0.2 pp ⇒ 那是**环境漂移**，不能归给 reroute。

口径：test 端点为各 run 台账里的 `map`（mAP50-95，分数→pp）；另报 val 逐 epoch 同轮最大差（含轨迹漂移）。

用法： python ctrldrift_check.py [--old r10_iv_src1_base100_3way_s42n] [--new r16_ctrl_envdrift_src1_base100_3way_s42n]
"""
import argparse
import csv
import io
import os
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
    ap.add_argument('--ledger', default='/workspace/sio_b_results.csv')
    ap.add_argument('--rundir', default='/workspace/runs')
    ap.add_argument('--old', default='r10_iv_src1_base100_3way_s42n')
    ap.add_argument('--new', default='r16_ctrl_envdrift_src1_base100_3way_s42n')
    ap.add_argument('--out', default='/workspace/ctrldrift_20260930.txt')
    a = ap.parse_args()
    L = ledger(a.ledger)
    old, new = L.get(a.old), L.get(a.new)
    vo, vn = val_curve(os.path.join(a.rundir, a.old)), val_curve(os.path.join(a.rundir, a.new))
    common = sorted(set(vo) & set(vn))
    dmax = max((abs(vo[e] - vn[e]) for e in common), default=float('nan'))
    lines = []
    lines.append('=== 环境漂移对照（同一个归档配置，09-15 vs 今天）===')
    lines.append('归档 run：%s  T=%.3f' % (a.old, old if old is not None else float('nan')))
    lines.append('今日 run：%s  T=%.3f' % (a.new, new if new is not None else float('nan')))
    if old is not None and new is not None:
        lines.append('**端点差 |今日 − 归档| = %.3f pp**' % abs(new - old))
    lines.append('val 逐 epoch 同轮最大差 = %.3f pp（n=%d 个可比 epoch）' % (dmax, len(common)))
    lines.append('')
    lines.append('判读：')
    if old is not None and new is not None:
        d = abs(new - old)
        if d <= 0.02:
            lines.append('  ⇒ 该对照几乎无差 ⇒ **环境稳定**，`p_vistod15` 的 0.150 pp 差可归因于 defect 10 的 reroute。')
        elif d >= 0.10:
            lines.append('  ⇒ 该对照本身就差 %.3f pp ⇒ **存在环境漂移**，不能把 `p_vistod15` 的差归给 reroute；'
                         'defect 10 的界应写成"含环境漂移与 reroute 的上界"。' % d)
        else:
            lines.append('  ⇒ 对照差 %.3f pp（介于两者之间）⇒ 归因不确定，如实写成"不能区分 reroute 与环境漂移"。' % d)
    else:
        lines.append('  ⇒ 读数缺失（run 未完成或台账无行）。')
    txt = '\n'.join(lines) + '\n'
    io.open(a.out, 'w', encoding='utf-8', newline='\n').write(txt)
    print(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main())
