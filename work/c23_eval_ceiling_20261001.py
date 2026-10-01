# -*- coding: utf-8 -*-
"""C23 的本地小实验：定位评测器自检上限 0.990099 的**真实截断点**（不训练、不需要模型）。

做法：用 pycocotools 直接把 **ground truth 当作 detections**（score = 1.0）评测，看
`COCOeval.eval['precision']` 在 101 个 recall 阈值上的分布 —— 若"全 1"，均值应为 1.0；
实测上限 100/101 = 0.990099 必然意味着**某一个 recall 点上精度为 0**，本脚本把它是哪一个打印出来。

三种输入：① 单图单类单框 maxDets=1000；② 同图 maxDets=100；③ 拥挤图（1 类 150 框）maxDets=100。
用法： python -X utf8 work/c23_eval_ceiling_20261001.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

OUT = r'E:\workplace\G4b_20260930'
os.makedirs(OUT, exist_ok=True)


def mk_gt(n_boxes, W=200, H=200):
    im = dict(id=1, width=W, height=H, file_name='synthetic.png')
    anns = []
    for i in range(n_boxes):
        col, row = i % 15, i // 15
        x, y = 5 + col * 12, 5 + row * 12
        anns.append(dict(id=i + 1, image_id=1, category_id=1, iscrowd=0,
                         bbox=[x, y, 10, 10], area=100))
    return dict(images=[im], annotations=anns, categories=[dict(id=1, name='obj')])


def run(n_boxes, max_dets, tag):
    gt = mk_gt(n_boxes)
    p = os.path.join(OUT, '_c23_gt_%s.json' % tag)
    io.open(p, 'w', encoding='utf-8').write(json.dumps(gt))
    coco = COCO(p)
    dets = [dict(image_id=a['image_id'], category_id=a['category_id'],
                 bbox=a['bbox'], score=1.0) for a in gt['annotations']]
    dp = os.path.join(OUT, '_c23_dt_%s.json' % tag)
    io.open(dp, 'w', encoding='utf-8').write(json.dumps(dets))
    dt = coco.loadRes(dp)
    ev = COCOeval(coco, dt, 'bbox')
    ev.params.maxDets = [1, 10, 100] if max_dets == 100 else [1, 10, 100, 1000]
    ev.evaluate()
    ev.accumulate()
    ev.summarize()
    prec = ev.eval['precision']          # [T, R, K, A, M]
    m = ev.params.maxDets.index(max_dets)
    p50 = prec[0, :, 0, 0, m]            # IoU .50, class 1, area all, 该 maxDets
    nz = int((p50 > 0).sum())
    bad = [i for i, v in enumerate(p50) if v <= 0]
    print('【%s】maxDets=%d｜mAP@[.5:.95]=%.6f｜IoU.50 的 101 个 recall 点上非零 %d 个'
          % (tag, max_dets, ev.stats[0], nz))
    print('   精度为 0 的 recall 下标：%s（recThr 步长 0.01）' % (bad[:6] or '无'))
    if len(bad):
        print('   首个 0 出现在 recall=%.2f ⇒ 均值 = %d/101 = %.6f'
              % (ev.params.recThrs[bad[0]], 101 - len(bad), (101 - len(bad)) / 101.0))
    print('   末 5 个 recall 点的精度：%s' % np.round(p50[-5:], 4).tolist())
    return ev.stats[0]


def main():
    print('=' * 78)
    a = run(1, 1000, 'one_box_maxDets1000')
    b = run(1, 100, 'one_box_maxDets100')
    c = run(150, 100, 'crowded150_maxDets100')
    io.open(os.path.join(OUT, 'c23_eval_ceiling_20261001.txt'), 'w', encoding='utf-8', newline='\n').write(
        'C23 评测器上限定位（本地 pycocotools，gt = predictions，score = 1.0）\n'
        '① 单图单类单框 maxDets=1000：mAP=%.6f\n'
        '② 同图 maxDets=100：mAP=%.6f\n'
        '③ 拥挤图（1 类 150 框）maxDets=100：mAP=%.6f\n' % (a, b, c))
    print('已写 %s' % os.path.join(OUT, 'c23_eval_ceiling_20261001.txt'))
    return 0


sys.exit(main())
