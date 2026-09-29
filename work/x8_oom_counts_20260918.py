# -*- coding: utf-8 -*-
"""r53 — the X8 OOM disclosure, computed from the LOCAL copy of the training log.

While X8 was sharing the GPU with the X3 sweep, ultralytics printed
    "CUDA OutOfMemoryError ... TaskAlignedAssigner ... using CPU"
i.e. it fell back to a CPU implementation of the assigner for that batch.  That is a memory
pressure artefact, not a semantic change -- but this paper's subject is exactly "which conditions
produced the number", so the count is reported per run instead of being left in a log file.

Input : E:\\workplace\\x8_dota15_20260918\\x8_dota15.log   (pulled from B, verbatim)
Output: E:\\workplace\\work\\x8_oom_counts_20260918.txt
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
LOG = os.path.join(W, 'x8_dota15_20260918', 'x8_dota15.log')
OUT = os.path.join(W, 'work', 'x8_oom_counts_20260918.txt')
L = []


def emit(s=''):
    L.append(s)
    print(s)


def main():
    txt = io.open(LOG, encoding='utf-8', errors='ignore').read()
    emit('=' * 88)
    emit('X8：训练日志里 CUDA OOM 回退（TaskAlignedAssigner → CPU）的逐 run 计数')
    emit('=' * 88)
    emit('源文件：%s（%d 字节，本地副本）' % (LOG, os.path.getsize(LOG)))
    emit()
    total = len(re.findall(r'OutOfMemoryError', txt))
    assigner = len(re.findall(r'TaskAlignedAssigner', txt))
    emit('  全日志 OutOfMemoryError 出现 %d 次；其中提到 TaskAlignedAssigner 的 %d 次'
         % (total, assigner))
    # split the log by run: the queue script delimits each run with
    #     "--- <ISO timestamp> train <run-name> ---"
    marks = [(m.start(), m.group(1))
             for m in re.finditer(r'--- \S+ train (\S+) ---', txt)]
    spans = []
    for i, (pos, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(txt)
        spans.append((name, txt[pos:end]))
    if not spans:
        sys.exit('!! 未能在日志里找到 run 分隔行，别猜 —— 先看清日志结构')
    per = {}
    for name, chunk in spans:
        per[name] = per.get(name, 0) + len(re.findall(r'OutOfMemoryError', chunk))
    emit('  日志里识别出 %d 个 run 段' % len(spans))
    emit()
    emit('  %-32s %s' % ('run', 'OOM 回退次数'))
    for name in sorted(per):
        if name.startswith('dota15'):
            emit('  %-32s %d' % (name, per[name]))
    base = [v for k, v in per.items() if k.startswith('dota15_base100')]
    strat = [v for k, v in per.items() if k.startswith('dota15_lr005')]
    emit()
    emit('  基准臂 %d 个 run，合计 %d 次；策略臂 %d 个 run，合计 %d 次'
         % (len(base), sum(base), len(strat), sum(strat)))
    emit('  出现过的 run 数：%d / %d'
         % (sum(1 for v in base + strat if v > 0), len(base) + len(strat)))
    emit()
    emit('  读法：这是**显存压力下的实现回退**（该 batch 的分配器改在 CPU 上跑），不是训练语义的')
    emit('  改变；但它意味着并行评测期间这台 GPU 上发生过显存竞争，故在正文/补充材料里按 run 报出，')
    emit('  并说明何时发生（X3 与本批并发的那几个 run）。')
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    emit()
    emit('已写 %s' % OUT)


main()
