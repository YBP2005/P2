# -*- coding: utf-8 -*-
"""只读：§6.1 的**合理窗口**版判据（替代上一版"首句必须带引用"的过严探针）。

判据：实体在**正文**（排除表格行、排除 References 节、排除图片题注）首次出现处，其
**所在段落**或**前后各两句**之内必须出现 `[n]`。
理由：引用常写在同段后句或紧邻句（例如 §4.1 先描述现象、后句给编号），
把窗口收成"首句"会制造假缺陷（27 号文 §5：判据与对象不匹配）。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
raw = io.open(W + r'\P2_English_v0.1.md', encoding='utf-8').read()
body, _, refs = raw.partition('\n## References')

# 正文（去表格行）用于"是否在正文点名"
prose = '\n'.join(ln for ln in body.split('\n') if not ln.strip().startswith('|'))

MUST = ['VisDrone', 'AI-TOD', 'DOTA', 'COCO', 'Mendeley', 'SHWD', 'SFCHD', 'VOC',
        'YOLOv12', 'YOLOv8', 'YOLOv5', 'Faster R-CNN', 'RetinaNet', 'Detectron2',
        'MMDetection', 'DETR', 'PaddleDetection', 'P2PNet', 'CSRNet', 'DM-Count',
        'BBBC005', 'MAFA', 'Qwen', 'InternVL', 'AWQ', 'YOLOX']
CITE = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')


def windows(text):
    """按句切分，返回句列表（折行已压平）。"""
    flat = re.sub(r'\s+', ' ', text)
    return re.split(r'(?<=[.!?]) ', flat)


sents = windows(prose)
print('=' * 100)
print('§6.1 合理窗口判据（同段或 ±2 句内须有 [n]）')
print('=' * 100)
bad = []
for e in MUST:
    idx = [i for i, s in enumerate(sents) if re.search(re.escape(e), s)]
    if not idx:
        # 正文未点名（可能只在参考文献标题里）⇒ 不是"该引未引"
        in_refs = e in refs
        print('  %-14s 正文未点名%s' % (e, '（仅出现在参考文献里 ⇒ 不算缺陷）' if in_refs else ''))
        continue
    i = idx[0]
    win = ' '.join(sents[max(0, i - 2):i + 3])
    if CITE.search(win):
        print('  ok   %-14s 首次出现句 ±2 句内有引用 %s'
              % (e, CITE.search(win).group(0)))
    else:
        bad.append((e, i, sents[i]))
        print('  !!   %-14s 首次出现处 ±2 句内无引用：%s' % (e, sents[i][:110]))

print()
print('=' * 100)
print('§6.3 参考文献完备性（含表格内的引用）')
print('=' * 100)
cited_all = set()
for m in CITE.finditer(body):
    for n in re.findall(r'\d+', m.group(1)):
        cited_all.add(int(n))
listed = [int(x) for x in re.findall(r'(?m)^\s*\[(\d+)\] ', refs)]
uncited = sorted(set(listed) - cited_all)
unlisted = sorted(cited_all - set(listed))
print('  条目 %d｜正文（含表格）引用到 %d' % (len(listed), len(cited_all)))
print('  **列出但全文从未引用**：%s' % (uncited or '无'))
print('  **引用了但列表里没有**：%s' % (unlisted or '无'))
print()
print('⇒ 真实待修项：%d 个实体 + %d 条文献' % (len(bad), len(uncited)))
