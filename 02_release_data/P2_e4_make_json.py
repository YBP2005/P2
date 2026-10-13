#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""e4_make_json.py —— E4 第一步：为 §8.8 的 E1 run 产 **COCO 格式预测 JSON**（best/last 两端点）。

为什么：E4 要求"用放行的 COCO 格式 JSON 做图像级 bootstrap"，而当初的登记调用是 `save_json=False`，
所以包内**没有**这些 JSON ⇒ 本脚本按同一登记调用补产（只推理、不训练）。

输出：`/workspace/e4_json/<run>__<ckpt>.json`（Ultralytics `save_json=True` 的产出）

用法（多分片并发；评测类单进程利用率低）：
  python e4_make_json.py --gpu 0 --shard 0 --nshard 8
"""
import argparse
import csv
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
RUNDIR = '/workspace/runs'
OUTDIR = '/workspace/e4_json'
TMP = '/workspace/_e4_tmp'


def yaml_of(run):
    p = os.path.join(RUNDIR, run, 'args.yaml')
    if not os.path.isfile(p):
        return None
    for ln in io.open(p, encoding='utf-8', errors='ignore'):
        if ln.startswith('data:'):
            return ln.split(':', 1)[1].strip().strip("'\"")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpu', default='0')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshard', type=int, default=1)
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--imgsz', type=int, default=640)
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    runs = sorted(d for d in os.listdir(RUNDIR) if d.startswith('r18_e1full_y12n_'))
    jobs = [(r, k) for r in runs for k in ('best', 'last')]
    jobs = [j for i, j in enumerate(jobs) if i % a.nshard == a.shard]
    print('SHARD %s gpu=%s runs=%d 本片任务 %d' % (a.shard, a.gpu, len(runs), len(jobs)), flush=True)

    from ultralytics import YOLO
    for run, ck in jobs:
        outp = os.path.join(OUTDIR, '%s__%s.json' % (run, ck))
        if os.path.isfile(outp) and os.path.getsize(outp) > 1000:
            print('  skip %s %s' % (run, ck), flush=True)
            continue
        w = os.path.join(RUNDIR, run, 'weights', ck + '.pt')
        dy = yaml_of(run)
        if not os.path.isfile(w) or not dy or not os.path.isfile(dy):
            print('  ★ SKIP(缺件) %s %s w=%s dy=%s' % (run, ck, os.path.isfile(w), dy), flush=True)
            continue
        try:
            m = YOLO(w)
            m.val(data=dy, split='test', batch=a.batch, imgsz=a.imgsz, device=str(a.gpu),
                  plots=False, verbose=False, save_json=True, workers=a.workers,
                  project=TMP, name='v_%s_%s' % (run, ck), exist_ok=True)
            # Ultralytics 把 predictions.json 写在工作目录下，这里找出来搬到 OUTDIR
            # 分片并发 ⇒ 只认自己那一份：TMP/v_<run>_<ck>/predictions.json
            cand = os.path.join(TMP, 'v_%s_%s' % (run, ck), 'predictions.json')
            found = cand if (os.path.isfile(cand) and os.path.getsize(cand) > 1000) else None
            if found is None:
                for root, _dirs, files in os.walk(TMP):
                    for f in files:
                        if f == 'predictions.json':
                            p = os.path.join(root, f)
                            if ('v_%s_%s' % (run, ck)) in p and os.path.getsize(p) > 1000:
                                found = p
            if found:
                import shutil
                shutil.copy2(found, outp)
                print('  ok %s %s -> %s (%d B)' % (run, ck, os.path.basename(outp), os.path.getsize(outp)), flush=True)
            else:
                print('  ★ 未找到 predictions.json：%s %s' % (run, ck), flush=True)
        except Exception as e:
            print('  ★ FAIL %s %s : %s' % (run, ck, e), flush=True)
    print('SHARD %s 完成' % a.shard, flush=True)
    return 0


raise SystemExit(main())
