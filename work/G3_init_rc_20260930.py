#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""G3_init_rc_20260930.py — 跨初始化的**兑现率**（补充材料 §S12 "no denominator" 台账第 ④ 条的闭合）。

台账第 ④ 条原文：*"Initialization is not an axis here — what varies across these replicates is the
training file order (`--shuffle-seed`) — so an across-initialization realization rate is not recorded
in this archive."* G3 把初始化从 3 个扩到 5 个（`r10_iv_src{1,2,3}` + `r16_iv_src{4,5}`，每个两臂），
每个 run 都有 `best.pt` 与 `last.pt` ⇒ 现在可以逐初始化给出 `prem_val`（val 侧）与 `prem_test`（test 侧）。

口径与正文一致：
  `prem_val`  = 逐 epoch val mAP50-95 的最大值 − 末轮值（各 run 自己的 `results.csv`）
  `prem_test` = `T_best − T_last`（两边都在同一留出 `test` split 上评；调用逐字照已登记口径）
本脚本**只评 `last.pt`**（`T_best` 已由训练脚本写进 `/workspace/sio_b_results.csv`），幂等：已评过的不重评。

用法： python G3_init_rc_20260930.py [--limit 0] [--out /workspace/G3_init_rc_20260930.txt]
"""
import argparse
import csv
import io
import os
import re
import statistics as st
import sys
import time
import traceback

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
RUNDIR = '/workspace/runs'
CELLS = [('r10_iv_src%d_%s_3way_s42n' % (k, a), k, a) for k in (1, 2, 3)
         for a in ('base100', 'lr005_100ep')] + \
        [('r16_iv_src%d_%s_3way_s42n' % (k, a), k, a) for k in (4, 5)
         for a in ('base100', 'lr005_100ep')]
ARCH_BEST = {  # 归档 09-15 备忘录里的端点（test mAP50-95，pp）：(k, arm) → 值
    (1, 'base100'): 43.630, (1, 'lr005_100ep'): 44.200,
    (2, 'base100'): 43.590, (2, 'lr005_100ep'): 43.870,
    (3, 'base100'): 43.250, (3, 'lr005_100ep'): 43.710,
}


def field(path, key):
    if not os.path.exists(path):
        return None
    for line in io.open(path, encoding='utf-8', errors='replace'):
        if line.startswith(key + ':'):
            return line.split(':', 1)[1].strip()
    return None


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


def ledger_map(path):
    d = {}
    for line in io.open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split(',')
        if len(f) >= 5 and f[0].startswith('r'):
            try:
                d[f[0]] = float(f[4]) * 100.0
            except ValueError:
                pass
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', default='/workspace/sio_b_results.csv')
    ap.add_argument('--cache', default='/workspace/G3_init_rc_last.csv')
    ap.add_argument('--out', default='/workspace/G3_init_rc_20260930.txt')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    L = ledger_map(a.ledger)

    done = {}
    if os.path.exists(a.cache):
        for line in io.open(a.cache, encoding='utf-8'):
            f = line.rstrip('\n').split(',')
            if len(f) == 2 and f[0] != 'run':
                try:
                    done[f[0]] = float(f[1])
                except ValueError:
                    pass
    todo = [(n, k, arm) for (n, k, arm) in CELLS if n not in done]
    print('待评 last.pt：%d / %d' % (len(todo), len(CELLS)), flush=True)

    if todo:
        from ultralytics import YOLO
        if not os.path.exists(a.cache):
            io.open(a.cache, 'w', encoding='utf-8', newline='\n').write('run,map50_95\n')
        n = 0
        for (name, k, arm) in todo:
            if a.limit and n >= a.limit:
                break
            rd = os.path.join(RUNDIR, name)
            dy = field(os.path.join(rd, 'args.yaml'), 'data')
            w = os.path.join(rd, 'weights', 'last.pt')
            if not os.path.exists(w) or not dy:
                print('SKIP %s（缺 last.pt 或 data）' % name, flush=True); continue
            t0 = time.time()
            try:
                m = YOLO(w)
                r = m.val(data=dy, split='test', batch=32, imgsz=640, device=0,
                          plots=False, verbose=False, save_json=False,
                          project='/workspace/G3_init_rc_tmp', name='_val', exist_ok=True)
                v = r.box.map * 100.0
                with io.open(a.cache, 'a', encoding='utf-8', newline='\n') as f:
                    f.write('%s,%.4f\n' % (name, v))
                done[name] = v; n += 1
                print('ok %-42s T_last=%.4f (%.1fs)' % (name, v, time.time() - t0), flush=True)
            except Exception:
                print('FAIL %s\n%s' % (name, traceback.format_exc()), flush=True)

    out = []
    def emit(s=''):
        out.append(s); print(s, flush=True)
    emit('=== 跨初始化的兑现率（G3：5 个初始化 × 2 臂）===')
    emit('台账 %s；T_last 缓存 %s' % (a.ledger, a.cache))
    emit('\ninit arm          prem_val  T_best   T_last   prem_test  rate     归档 T_best')
    per_init, allpv, allpt = {}, [], []
    for (name, k, arm) in CELLS:
        rd = os.path.join(RUNDIR, name)
        vc = val_curve(rd)
        tb = L.get(name)
        tl = done.get(name)
        if not vc or tb is None or tl is None:
            emit('src%-2d %-12s 读数不全（val=%d, T_best=%s, T_last=%s）'
                 % (k, arm, len(vc), tb, tl))
            continue
        v = dict(vc)
        pv = v[max(v, key=lambda e: v[e])] - v[vc[-1][0]]
        pt = tb - tl
        rate = pt / pv * 100 if pv else float('nan')
        ar = ARCH_BEST.get((k, arm))
        emit('src%-2d %-12s %+8.3f %8.3f %8.3f %+9.3f %7.1f%%   %s'
             % (k, arm, pv, tb, tl, pt, rate, ('%.3f' % ar) if ar else '—'))
        per_init.setdefault(k, []).append(rate); allpv.append(pv); allpt.append(pt)

    if allpv:
        rates = [r for v in per_init.values() for r in v]
        init_mean = [st.mean(v) for v in per_init.values()]
        emit('\n逐初始化（两臂平均）兑现率：%s'
             % ', '.join('src%d %.1f%%' % (k, st.mean(v)) for k, v in sorted(per_init.items())))
        emit('跨初始化：%d 个 arm-run 的兑现率 中位数 %.1f%% / 均值 %.1f%%；5 个初始化均值的 SD %.1f pp'
             % (len(rates), st.median(rates), st.mean(rates),
                st.stdev(init_mean) if len(init_mean) > 1 else float('nan')))
        emit('run 加权（Σprem_test / Σprem_val）= %.3f / %.3f = %.1f%%'
             % (sum(allpt), sum(allpv), sum(allpt) / sum(allpv) * 100))
        emit('符号：prem_test > 0 的 arm-run %d/%d；prem_val > 0 的 %d/%d'
             % (sum(1 for x in allpt if x > 0), len(allpt),
                sum(1 for x in allpv if x > 0), len(allpv)))
    # 归档三初始化的 T_best 复现核对
    bad = []
    for (k, arm), want in ARCH_BEST.items():
        nm = 'r10_iv_src%d_%s_3way_s42n' % (k, arm)
        got = L.get(nm)
        if got is None or abs(got - want) > 0.005:
            bad.append('%s got=%s want=%.3f' % (nm, got, want))
    emit('\n归档三次初始化 T_best 复现：%s' % ('PASS（≤0.005 pp）' if not bad else 'FAIL ' + '; '.join(bad)))
    io.open(a.out, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n存证：%s' % a.out)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
