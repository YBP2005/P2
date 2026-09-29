# -*- coding: utf-8 -*-
"""
C 项分析：从取回的官方配置/脚本里**机械抽取**"划分与选点"的原始证据行。
不写结论，只输出带行号的证据；判定由人工（写在 §6.4 的表里）。
输出：E:\\workplace\\xframe_evidence_20260916.txt
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'E:\workplace\_xframe'
OUT = r'E:\workplace\xframe_evidence_20260916.txt'

# (框架, 文件, [要抓的正则])
TARGETS = [
    ('MMDetection', 'mmdetection/configs___base___datasets__coco_detection.py',
     [r'ann_file', r'data_prefix', r'data_root', r"type='", r'metainfo']),
    ('MMDetection', 'mmdetection/configs___base___default_runtime.py',
     [r'val_interval', r'val_evaluator', r'test_evaluator', r'val_cfg', r'test_cfg', r'save_best']),
    ('MMDetection', 'mmdetection/configs__faster_rcnn__faster-rcnn_r50_fpn_1x_coco.py',
     [r'.']),
    ('MMDetection', 'mmdetection/tools__train.py',
     [r'save_best', r'val_interval', r'val_evaluator', r'val_loop', r'val_dataloader']),
    ('Detectron2', 'detectron2/configs__COCO-Detection__faster_rcnn_R_50_FPN_1x.yaml',
     [r'.']),
    ('Detectron2', 'detectron2/configs__Base-RCNN-FPN.yaml',
     [r'DATASETS', r'TRAIN', r'TEST', r'EVAL_PERIOD', r'IMS_PER_BATCH']),
    ('Detectron2', 'detectron2/tools__train_net.py',
     [r'EVAL_PERIOD', r'best', r'checkpointer', r'eval_period', r'DATASETS.TEST']),
    ('Detectron2', 'detectron2/detectron2__data__datasets__builtin.py',
     [r'coco_2017_train', r'coco_2017_val', r'coco_2017_test', r'val2017', r'test2017',
      r'instances_val2017', r'annotations']),
    ('Detectron2', 'detectron2/detectron2__config__defaults.py',
     [r'EVAL_PERIOD', r'DATASETS\.TEST']),
    ('YOLOX', 'yolox/exps__default__yolox_s.py',
     [r'val_ann', r'data_dir', r'exp', r'num_classes']),
    ('YOLOX', 'yolox/yolox__data__datasets__coco.py',
     [r'val_ann', r'val2017', r'train2017', r'instances_val', r'self\.val_dataset', r'ann_file']),
    ('YOLOX', 'yolox/tools__train.py',
     [r'best_ap', r'self\.best', r'eval', r'val_loader', r'save_checkpoint', r'ap50_95']),
    ('YOLOX', 'yolox/tools__eval.py',
     [r'val_ann', r'val2017', r'instances_val', r'exp\.eval', r'--test']),
    ('PaddleDetection', 'paddledetection/configs__yolov3__yolov3_darknet53_270e_coco.yml',
     [r'.']),
    ('PaddleDetection', 'paddledetection/tools__train.py',
     [r'EvalDataset', r'save_best', r'val', r'best']),
    ('DETR', 'detr/main.py',
     [r'--eval', r'eval', r'val', r'best']),
    ('DETR', 'detr/datasets__coco.py',
     [r'val2017', r'train2017', r'split', r'PATHS']),
    ('DETR', 'detr/engine.py',
     [r'evaluate', r'val', r'best', r'checkpoint']),
]

buf = []
def emit(s=''):
    print(s); buf.append(s)

emit('=' * 100)
emit('C 项：跨框架"划分与选点"证据抽取（机械抽取，带行号；判定不在此文件）')
emit('=' * 100)
emit()
pin = io.open(os.path.join(BASE, 'PINNED_COMMITS.txt'), encoding='utf-8').read().strip().split('\n')
for l in pin:
    emit('  ' + l)
emit()

missing = []
for fw, rel, pats in TARGETS:
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        missing.append(rel); continue
    txt = io.open(p, encoding='utf-8', errors='replace').read().split('\n')
    emit('-' * 100)
    emit(f'### {fw} :: {rel}   （{len(txt)} 行）')
    hits = 0
    for i, line in enumerate(txt, 1):
        s = line.rstrip()
        if not s.strip() or s.strip().startswith('#'):
            continue
        if any(re.search(pat, s) for pat in pats):
            emit(f'  {i:>4}: {s[:150]}')
            hits += 1
    if hits == 0:
        emit('  （无命中）')
    emit()

emit('=' * 100)
emit('缺失文件：' + (', '.join(missing) if missing else '无'))
emit()
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(buf) + '\n')
print(f'\n输出已写：{OUT}')
