#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""e4_bootstrap.py —— E4 第二步：**图像级 bootstrap**（逐端点）求 mAP50-95 的 SE。

做法（自包含，不依赖 Ultralytics 的中间件）：
  1. 从 run 的 `args.yaml` 的 data yaml 取 `test` 目录，把 YOLO 标签转成 **COCO GT**；
  2. 读第一步产出的 `predictions.json`（COCO 检测格式）；
  3. 每次抽样**图像 id（有放回）**，用 pycocotools 在被抽子集上重算 mAP50-95；
  4. 重复 N 次 ⇒ 端点 SE = 抽样分布的标准差。

输出（追加写，可断点续跑）：
  `/workspace/e4_se.csv`  run,ckpt,N,map50_95_mean,se,note

用法（多分片并发）：
  python e4_bootstrap.py --gpu 0 --shard 0 --nshard 8 --draws 200
"""
import argparse
import csv
import io
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
RUNDIR = '/workspace/runs'
JSONDIR = '/workspace/e4_json'
OUT = '/workspace/e4_se.csv'


def yaml_of(run):
    p = os.path.join(RUNDIR, run, 'args.yaml')
    for ln in io.open(p, encoding='utf-8', errors='ignore'):
        if ln.startswith('data:'):
            return ln.split(':', 1)[1].strip().strip("'\"")
    return None


def test_dir_of(run):
    import yaml
    y = yaml_of(run)
    if not y or not os.path.isfile(y):
        return None
    d = yaml.safe_load(io.open(y, encoding='utf-8'))
    root = d.get('path', '')
    t = d.get('test', '')
    p = t if os.path.isabs(t) else os.path.join(root, t)
    return p if os.path.isdir(p) else None


def build_gt(run, imgdir, names):
    """YOLO 标签 → COCO GT（只做一次，缓存到 /tmp）。"""
    cache = '/tmp/e4_gt_%s.json' % run
    if os.path.isfile(cache):
        return json.load(io.open(cache, encoding='utf-8'))
    labdir = imgdir.replace('/images', '/labels')
    if not os.path.isdir(labdir):
        labdir = os.path.join(os.path.dirname(imgdir), 'labels')
    imgs, anns, aid = [], [], 1
    for fn in sorted(os.listdir(imgdir)):
        if not fn.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            continue
        stem = os.path.splitext(fn)[0]
        # 只用文件名登记（predictions.json 也是按文件名匹配 ⇒ 一致）
        iid = len(imgs) + 1
        imgs.append({'id': iid, 'file_name': fn, 'width': 0, 'height': 0})
        lf = os.path.join(labdir, stem + '.txt')
        if not os.path.isfile(lf):
            continue
        for ln in io.open(lf, encoding='utf-8', errors='ignore'):
            p = ln.split()
            if len(p) < 5:
                continue
            c = int(float(p[0]))
            x, y, w, h = (float(v) for v in p[1:5])
            # 归一化 cx,cy,w,h → 绝对 xywh（用图像尺寸；尺寸缺失时按 1:1 归一化坐标保留）
            W = H = None
            try:
                from PIL import Image
                W, H = Image.open(os.path.join(imgdir, fn)).size
            except Exception:
                W = H = 1000
            anns.append({'id': aid, 'image_id': iid, 'category_id': c + 1,
                         'bbox': [(x - w / 2) * W, (y - h / 2) * H, w * W, h * H],
                         'area': w * W * h * H, 'iscrowd': 0})
            aid += 1
    gt = {'images': imgs, 'annotations': anns,
          'categories': [{'id': i + 1, 'name': n} for i, n in enumerate(names)]}
    json.dump(gt, io.open(cache, 'w', encoding='utf-8'))
    return gt


def eval_subset(gt, preds, ids):
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    keep = set(ids)
    g = {'images': [im for im in gt['images'] if im['id'] in keep],
         'annotations': [a for a in gt['annotations'] if a['image_id'] in keep],
         'categories': gt['categories']}
    c = COCO()
    c.dataset = g
    c.createIndex()
    p = [d for d in preds if d['image_id'] in keep]
    if not p:
        return 0.0
    dt = c.loadRes(p)
    e = COCOeval(c, dt, 'bbox')
    e.evaluate(); e.accumulate(); e.summarize()
    return float(e.stats[0]) * 100.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshard', type=int, default=1)
    ap.add_argument('--draws', type=int, default=25)
    ap.add_argument('--sub', type=int, default=400, help='每次抽样的图像数（不足则取全量）')
    ap.add_argument('--seed', type=int, default=20261012)
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(JSONDIR) if f.endswith('.json')) if os.path.isdir(JSONDIR) else []
    jobs = [f for i, f in enumerate(files) if i % a.nshard == a.shard]
    done = set()
    if os.path.isfile(OUT):
        for r in csv.DictReader(io.open(OUT, encoding='utf-8', errors='ignore')):
            done.add((r['run'], r['ckpt']))
    print('SHARD %s 文件 %d · 本片 %d（已完成 %d）' % (a.shard, len(files), len(jobs), len(done)), flush=True)

    for f in jobs:
        run, ck = f[:-5].rsplit('__', 1)
        if (run, ck) in done:
            print('  skip %s %s' % (run, ck), flush=True)
            continue
        imgdir = test_dir_of(run)
        if not imgdir:
            print('  ★ SKIP(无 test 目录) %s' % run, flush=True)
            continue
        names = []
        try:
            import yaml
            d = yaml.safe_load(io.open(yaml_of(run), encoding='utf-8'))
            nm = d.get('names') or {}
            names = [nm[k] for k in sorted(nm)] if isinstance(nm, dict) else list(nm)
        except Exception:
            names = []
        gt = build_gt(run, imgdir, names or ['obj'])
        preds = json.load(io.open(os.path.join(JSONDIR, f), encoding='utf-8'))
        # predictions.json 的 image_id 是 Ultralytics 的编号 ⇒ 用 file_name 重映射到我们的 id
        byname = {im['file_name']: im['id'] for im in gt['images']}
        # Ultralytics 在 predictions.json 里只写 image_id（其内部编号）与 category_id/bbox/score；
        # 若带 file_name 就直接映射，否则按类别无关的顺序假设与 GT 的排序一致（本项目的 test 目录按名排序）
        if preds and 'file_name' in preds[0]:
            for d0 in preds:
                d0['image_id'] = byname.get(os.path.basename(d0['file_name']), d0['image_id'])
        else:
            order = [im['id'] for im in gt['images']]
            ids = sorted({d0['image_id'] for d0 in preds})
            mp = {u: order[i] for i, u in enumerate(ids) if i < len(order)}
            for d0 in preds:
                d0['image_id'] = mp.get(d0['image_id'], d0['image_id'])
        all_ids = [im['id'] for im in gt['images']]
        sub_n = min(a.sub, len(all_ids))
        random.seed(a.seed)
        vals = []
        for _ in range(a.draws):
            ids = [random.choice(all_ids) for _ in range(sub_n)]
            vals.append(eval_subset(gt, preds, ids))
        import statistics as st
        m = st.mean(vals); se_sub = st.pstdev(vals)
        # 折算到全量 test 集：SE_full = SE_sub × sqrt(sub_n / N)
        se = se_sub * (float(sub_n) / len(all_ids)) ** 0.5
        new = not os.path.isfile(OUT)
        with io.open(OUT, 'a', encoding='utf-8', newline='\n') as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(['run', 'ckpt', 'draws', 'map50_95_mean', 'se', 'note'])
            w.writerow([run, ck, a.draws, '%.4f' % m, '%.4f' % se,
                        'image-level bootstrap, sub=%d of %d, rescaled' % (sub_n, len(all_ids))])
        print('  ok %s %s  mAP50-95=%.3f  SE(full, rescaled)=%.4f pp  (sub SE=%.4f, sub=%d)'
              % (run, ck, m, se, se_sub, sub_n), flush=True)
    print('SHARD %s 完成' % a.shard, flush=True)
    return 0


raise SystemExit(main())
