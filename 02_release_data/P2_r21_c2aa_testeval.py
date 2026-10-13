#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""testeval_c2_aa_control.py —— 对 C2 的 20 个 run 各评 **best.pt 与 last.pt** 在 `split='test'` 上。

为什么：C2 的 `prem_test` 需要与 val 端**同单位**（mAP50-95）的 test 读数，而 C2 的 run 没有逐检查点 test 扫。
本脚本只评不训；逐 run 从**该 run 自己的 `args.yaml`** 读 data yaml（不硬编码）；增量写、可断点续跑。

输出：`/workspace/r21_c2aa_testeval.csv`
      `run,ckpt,split,map50_95,map50,mp,mr,data_yaml`

用法（多分片并发以占满卡；本项目实测单进程评测利用率只有 0–20 %）：
  python testeval_c2_aa_control.py --gpu 0 --shard 0 --nshard 8
"""
import argparse
import csv
import io
import os
import sys
import traceback

sys.stdout.reconfigure(encoding='utf-8')

TAG = 'r21_c2aa_sfchd'
OUT = '/workspace/r21_c2aa_testeval.csv'
RUNDIR = '/workspace/runs'
TMP = '/workspace/_c2_testeval_tmp'


def load_done():
    done = set()
    if os.path.isfile(OUT):
        for r in csv.DictReader(io.open(OUT, encoding='utf-8', errors='ignore')):
            done.add((r['run'], r['ckpt']))
    return done


def yaml_of(run):
    """从该 run 自己的 args.yaml 读 data（跨机通用，不硬编码）。"""
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

    jobs = []
    for arm, rng in (('A', range(42, 52)), ('B', range(62, 72))):
        for s in rng:
            run = '%s_%s_s%dn' % (TAG, arm, s)
            for ck in ('best', 'last'):
                jobs.append((run, ck))
    jobs = [j for i, j in enumerate(jobs) if i % a.nshard == a.shard]
    done = load_done()
    print('SHARD %s gpu=%s 计划 %d 项（已完成 %d）' % (a.shard, a.gpu, len(jobs), len(done)), flush=True)

    from ultralytics import YOLO
    os.makedirs(TMP, exist_ok=True)
    for run, ck in jobs:
        if (run, ck) in done:
            print('  skip %s %s' % (run, ck), flush=True)
            continue
        w = os.path.join(RUNDIR, run, 'weights', ck + '.pt')
        dy = yaml_of(run)
        if not os.path.isfile(w) or not dy or not os.path.isfile(dy):
            print('  ★ SKIP(缺件) %s %s  w=%s dy=%s' % (run, ck, os.path.isfile(w), dy), flush=True)
            continue
        try:
            m = YOLO(w)
            r = m.val(data=dy, split='test', batch=a.batch, imgsz=a.imgsz, device=str(a.gpu),
                      plots=False, verbose=False, save_json=False, workers=a.workers,
                      project=TMP, name='v', exist_ok=True)
            row = [run, ck, 'test', '%.4f' % (float(r.box.map) * 100.0), '%.4f' % (float(r.box.map50) * 100.0),
                   '%.4f' % (float(getattr(r.box, 'mp', 0.0)) * 100.0), '%.4f' % (float(getattr(r.box, 'mr', 0.0)) * 100.0), dy]
            new = not os.path.isfile(OUT)
            with io.open(OUT, 'a', encoding='utf-8', newline='\n') as fh:
                wr = csv.writer(fh)
                if new:
                    wr.writerow(['run', 'ckpt', 'split', 'map50_95', 'map50', 'mp', 'mr', 'data_yaml'])
                wr.writerow(row)
            print('  ok %s %s  mAP50-95=%.4f' % (run, ck, float(r.box.map) * 100.0), flush=True)
        except Exception as e:
            print('  ★ FAIL %s %s : %s' % (run, ck, e), flush=True)
            traceback.print_exc()
    print('SHARD %s 完成' % a.shard, flush=True)
    return 0


raise SystemExit(main())
