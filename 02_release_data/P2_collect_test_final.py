#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_test_final.py —— 对已归档 run 的 `last.pt` 跑一次 **test 侧** 评测，补 `T_final`。

为什么需要：`/workspace/train_obj.py` 末尾只对 `best.pt` 做一次 `val(split='test')`
（写进 `/workspace/sio_b_results.csv` = **T_best**），**没有 T_final**；
而 `prem_test = T_best − T_final` 需要两者。本脚本**纯推理、不训练**，
口径与训练脚本完全一致（`val(split='test', batch=32, imgsz=640, plots=False)`）。

用法（在节点上）：
  RUNDIR=/workspace/runs LIST=/root/todo_dev0.txt DEV=0 OUT=/root/t_final_dev0.csv \
    python collect_test_final.py
LIST 每行： <run_name>|<data.yaml>
输出列： run, ckpt, map50, map50_95, mp, mr, secs
"""
import csv
import os
import sys
import time

RUNDIR = os.environ.get('RUNDIR', '/workspace/runs')
LIST = os.environ.get('LIST', '/root/todo.txt')
DEV = int(os.environ.get('DEV', '0'))
OUT = os.environ.get('OUT', '/root/t_final.csv')
CKPT = os.environ.get('CKPT', 'last.pt')

from ultralytics import YOLO          # noqa: E402


def main():
    todo = []
    for ln in open(LIST):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        p = ln.split('|')
        if len(p) >= 2:
            todo.append((p[0], p[1]))
    print('本 lane 待评 %d 个 run（ckpt=%s, dev=%d, out=%s）' % (len(todo), CKPT, DEV, OUT), flush=True)

    new = not os.path.exists(OUT)
    f = open(OUT, 'a', newline='', encoding='utf-8')
    w = csv.writer(f)
    if new:
        w.writerow(['run', 'ckpt', 'map50', 'map50_95', 'mp', 'mr', 'secs'])
        f.flush()

    done = set()
    if not new:
        with open(OUT, encoding='utf-8') as g:
            for r in csv.DictReader(g):
                done.add(r['run'])
        print('已存在 %d 条，将跳过' % len(done), flush=True)

    for i, (run, data) in enumerate(todo, 1):
        if run in done:
            continue
        ck = os.path.join(RUNDIR, run, 'weights', CKPT)
        if not os.path.exists(ck):
            print('[%d/%d] %s 缺 %s，跳过' % (i, len(todo), run, CKPT), flush=True)
            continue
        t0 = time.time()
        try:
            m = YOLO(ck)
            r = m.val(data=data, split='test', batch=32, imgsz=640, device=DEV,
                      plots=False, save_json=False, verbose=False)
            w.writerow([run, CKPT, float(r.box.map50), float(r.box.map),
                        float(r.box.mp), float(r.box.mr), round(time.time() - t0, 1)])
            f.flush()
            print('[%d/%d] %s  test mAP50-95 = %.4f  (%.0fs)' %
                  (i, len(todo), run, float(r.box.map), time.time() - t0), flush=True)
        except Exception as e:
            print('[%d/%d] %s 失败：%r' % (i, len(todo), run, e), flush=True)
    f.close()
    print('LANE DONE (%d)' % len(todo), flush=True)


if __name__ == '__main__':
    main()
