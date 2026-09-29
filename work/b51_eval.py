#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B51 · test-carve 大小敏感性 —— 装置（在 B 机上运行）

设计（**只用 Ultralytics 自己的度量**，使 100% 情形逐位复现稿内印值）：
  * 对每个 test split，按 RNG seed 42 生成 **10 次不放回抽样**，比例 25% / 50%；
    100% 即全集（唯一，确定性）。
  * 每个子集写成一个 **图片路径清单 .txt**，并据原 yaml 生成一份把 `test:` 指向该清单的 yaml。
  * 评测时 Ultralytics 按 `/images/`→`/labels/` 规则配对标签，故清单里用**绝对路径**即可。

子命令：
  prep                          生成清单与 yaml（幂等）
  list                          打印将要评测的任务数
  eval --gpu N --shard i --nshards k [--limit M] [--csv path]
                                对第 i/k 片任务跑评测，逐条追加写 CSV
"""
import argparse
import csv
import io
import json
import os
import random
import sys
import time

ROOT = '/root/b51'
SIZES = [25, 50]
DRAWS = 10
SEED = 42
SPLITS = {
    'sfchd': dict(images='/workspace/datasets/split_5_5/test/images',
                  src_yaml='/workspace/datasets/split_5_5/sfchd20_3way.yaml'),
    'aitod': dict(images='/root/datasets/AI-TOD_yolo/images/val',
                  src_yaml='/root/datasets/AI-TOD_yolo/aitod20_3way.yaml'),
}

# 50 个 run（Table 4 的五格），权重路径按来源分派
RUNS = []
for s in range(42, 52):
    RUNS.append(('shwd2sf', 'base', 'r10_shwd2sf_base100_3way_s%dn' % s,
                 '/workspace/runs/r10_shwd2sf_base100_3way_s%dn/weights/%%s.pt' % s, 'sfchd'))
    RUNS.append(('shwd2sf', 'strat', 'r10_shwd2sf_lr005_100ep_3way_s%dn' % s,
                 '/workspace/runs/r10_shwd2sf_lr005_100ep_3way_s%dn/weights/%%s.pt' % s, 'sfchd'))
    RUNS.append(('smoke2sf', 'base', 'r10_smoke2sf_base100_3way_s%dn' % s,
                 '/workspace/runs/r10_smoke2sf_base100_3way_s%dn/weights/%%s.pt' % s, 'sfchd'))
    RUNS.append(('smoke2sf', 'strat', 'r10_smoke2sf_lr005_100ep_3way_s%dn' % s,
                 '/workspace/runs/r10_smoke2sf_lr005_100ep_3way_s%dn/weights/%%s.pt' % s, 'sfchd'))
for s in range(42, 52):
    # aitod20：s42-s45 在原 run 目录；s46-s51 由 aitodfill_a 从 A 机补回
    if s <= 45:
        tpl = '/workspace/runs/r10_aitod20_base30_3way_s%dn/weights/%%s.pt' % s
    else:
        tpl = '/root/aitodfill_a/weights/r10_aitod20_base30_3way_s%dn__%%s.pt' % s
    RUNS.append(('aitod20', 'base', 'r10_aitod20_base30_3way_s%dn' % s, tpl, 'aitod'))


def read_names(src_yaml):
    """读源 yaml 的 path/nc/names/train（train 必填，否则 Ultralytics 拒收）。"""
    d = {}
    for line in io.open(src_yaml, encoding='utf-8'):
        s = line.strip()
        for k in ('path', 'nc', 'names', 'train', 'val', 'test'):
            if s.startswith(k + ':'):
                d[k] = s.split(':', 1)[1].strip()
    path = d.get('path', '')

    def resolve(v):
        if not v or v.startswith('/'):
            return v
        return os.path.join(path, v)
    d['train_abs'] = resolve(d.get('train', ''))
    return d


def prep():
    os.makedirs(os.path.join(ROOT, 'subsets'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'yamls'), exist_ok=True)
    index = {}
    for split, cfg in SPLITS.items():
        files = sorted(f for f in os.listdir(cfg['images'])
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')))
        abs_paths = [os.path.join(cfg['images'], f) for f in files]
        meta = read_names(cfg['src_yaml'])
        path, nc, names = meta.get('path', ''), meta.get('nc', ''), meta.get('names', '')
        train_abs = meta['train_abs']
        # 100%：全集
        specs = [(100, 0, abs_paths)]
        rng = random.Random(SEED)
        for pct in SIZES:
            k = int(round(len(abs_paths) * pct / 100.0))
            for d in range(DRAWS):
                specs.append((pct, d, sorted(rng.sample(abs_paths, k))))
        for pct, d, sel in specs:
            tag = '%s_%03d_d%02d' % (split, pct, d)
            lst = os.path.join(ROOT, 'subsets', tag + '.txt')
            io.open(lst, 'w', encoding='utf-8', newline='\n').write('\n'.join(sel) + '\n')
            y = os.path.join(ROOT, 'yamls', tag + '.yaml')
            io.open(y, 'w', encoding='utf-8', newline='\n').write(
                'path: %s\ntrain: %s\nval: %s\ntest: %s\nnc: %s\nnames: %s\n'
                % (path, train_abs, lst, lst, nc, names))
            index[tag] = dict(split=split, pct=pct, draw=d, n=len(sel), list=lst, yaml=y)
    io.open(os.path.join(ROOT, 'subset_index.json'), 'w', encoding='utf-8').write(
        json.dumps(index, ensure_ascii=False, indent=1))
    print('prep 完成：%d 个（split × 比例 × 抽样）组合' % len(index))
    for split in SPLITS:
        ks = [v for v in index.values() if v['split'] == split]
        print('  %-6s 组合 %d，全集 %d 图；25%%=%d 图，50%%=%d 图'
              % (split, len(ks), [v['n'] for v in ks if v['pct'] == 100][0],
                 [v['n'] for v in ks if v['pct'] == 25][0],
                 [v['n'] for v in ks if v['pct'] == 50][0]))


def tasks():
    idx = json.load(io.open(os.path.join(ROOT, 'subset_index.json'), encoding='utf-8'))
    out = []
    for cell, arm, run, tpl, split in RUNS:
        for ck in ('best', 'last'):
            for tag, meta in sorted(idx.items()):
                if meta['split'] == split:
                    out.append(dict(cell=cell, arm=arm, run=run, ckpt=ck,
                                    w=tpl % ck, tag=tag, pct=meta['pct'], draw=meta['draw'],
                                    yaml=meta['yaml'], n=meta['n']))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['prep', 'list', 'eval', 'migrate'])
    ap.add_argument('--gpu', default='0', help="'0'/'1' 或 'auto'（= shard %% 2）")
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshards', type=int, default=1)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=8, help='dataloader workers（多进程并发时要调小）')
    ap.add_argument('--csv', default=os.path.join(ROOT, 'b51_results.csv'))
    ap.add_argument('--prefix', default='/tmp/b51_s', help='migrate：目标 CSV 前缀')
    ap.add_argument('--from', dest='srcs', action='append', default=[],
                    help='migrate：源 CSV（可多次）')
    a = ap.parse_args()
    if a.cmd == 'prep':
        return prep()

    # ---- migrate：把旧 CSV 的行按**新的** nshards 重新分派到 <prefix><shard>.csv
    #      （任务的全局序号由同一个 tasks() 决定，故分派与 eval 的分片规则**同源**）
    if a.cmd == 'migrate':
        T = tasks()
        idx = {(t['run'], t['ckpt'], str(t['pct']), str(t['draw'])): i for i, t in enumerate(T)}
        out, unknown = {}, 0
        for src in a.srcs:
            if not os.path.exists(src):
                continue
            for r in csv.DictReader(io.open(src, encoding='utf-8', errors='replace')):
                k = (r['run'], r['ckpt'], r['pct'], r['draw'])
                i = idx.get(k)
                if i is None:
                    unknown += 1
                    continue
                out.setdefault(i % a.nshards, []).append(r)
        for s, rows in sorted(out.items()):
            p = '%s%d.csv' % (a.prefix, s)
            fh = io.open(p, 'w', encoding='utf-8', newline='\n')
            wr = csv.writer(fh)
            wr.writerow(['cell', 'arm', 'run', 'ckpt', 'pct', 'draw', 'n', 'map50_95', 'map50', 'secs'])
            for r in rows:
                wr.writerow([r['cell'], r['arm'], r['run'], r['ckpt'], r['pct'], r['draw'],
                             r['n'], r['map50_95'], r['map50'], r['secs']])
            fh.close()
            print('  %s : %d 行' % (p, len(rows)))
        print('migrate 完成：分派 %d 行，未匹配 %d 行' % (sum(len(v) for v in out.values()), unknown))
        return 0

    T = tasks()
    mine = [t for i, t in enumerate(T) if i % a.nshards == a.shard]
    if a.gpu == 'auto':
        a.gpu = str(a.shard % 2)
    if a.limit:
        mine = mine[:a.limit]
    # ---- resume：跳过 CSV 里已有的 (run, ckpt, pct, draw)，使重启幂等（本片曾因 cache 竞态死过一次）
    done = set()
    if os.path.exists(a.csv):
        for r in csv.DictReader(io.open(a.csv, encoding='utf-8', errors='replace')):
            if r.get('run') and r.get('ckpt'):
                done.add((r['run'], r['ckpt'], r['pct'], r['draw']))
    todo = [t for t in mine if (t['run'], t['ckpt'], str(t['pct']), str(t['draw'])) not in done]
    if a.cmd == 'list':
        print('总任务 %d；本片 %d；已完成 %d；**待跑 %d**'
              % (len(T), len(mine), len(mine) - len(todo), len(todo)))
        return 0
    os.environ['CUDA_VISIBLE_DEVICES'] = a.gpu
    from ultralytics import YOLO
    # ---- 关掉 Ultralytics 的 labels.cache（**必须**，见下）----------------------------------
    # 实测：`cache=False` 只关"图像入内存"，**不关 labels.cache**。而
    #   ① `save_dataset_cache_file` 是 **先 unlink 再写**；② `_load_or_scan_cache` 的 except
    #      只捕 FileNotFoundError/AssertionError/AttributeError/ModuleNotFoundError，**不捕 EOFError**。
    #   ⇒ 多进程读同一个 labels.cache 时，读到半截文件就 **EOFError 崩掉**（本项目实测 err=38、
    #      8 片全线崩、看护陷入"起了就死"的循环）。
    #   处置：把写缓存函数 patch 成 no-op（于是永远不回写、永远走扫描）；并把已有 cache 删掉。
    import glob as _glob
    import ultralytics.data.dataset as _ds
    import ultralytics.data.utils as _du
    def _noop(*a, **k):
        # 2026-09-27 修正（真因，不是竞态）：本版 Ultralytics 的 save_dataset_cache_file
        # **会在字典里注入 `version` / `hash`**（`get_labels` 末尾 `[cache.pop(k) for k in
        # ("hash","version","msgs")]` 依赖它们）。把写侧做成纯 no-op ⇒ 一旦走"扫描分支"
        # （无 cache 文件时必然走），末尾 pop 立刻 `KeyError: 'version'`，8 片起了就死。
        # 昨天能出 1,263 行，只是因为当时目录里**还留着**可读的 cache 文件、一直走读分支。
        # 处置：仍然不落盘，但**该补的键照补**（值无关：校验只在读分支发生）。
        d = next((v for v in a if isinstance(v, dict)), None)
        if d is None:
            d = next((v for v in k.values() if isinstance(v, dict)), None)
        if isinstance(d, dict):
            d.setdefault('hash', 'cache-disabled')
            d.setdefault('version', 'cache-disabled')
            d.setdefault('msgs', [])
        return None
    _du.save_dataset_cache_file = _noop
    if hasattr(_ds, 'save_dataset_cache_file'):
        _ds.save_dataset_cache_file = _noop
    print('  [patch] labels.cache 写入已禁用（但读仍可用：既有 cache 是有效的就照读）')
    header = ['cell', 'arm', 'run', 'ckpt', 'pct', 'draw', 'n', 'map50_95', 'map50', 'secs']
    newf = not os.path.exists(a.csv)
    fh = io.open(a.csv, 'a', encoding='utf-8', newline='\n')
    wr = csv.writer(fh)
    if newf:
        wr.writerow(header)
        fh.flush()
    print('shard %d/%d：%d 个任务（待跑 %d），GPU=%s，CSV=%s'
          % (a.shard, a.nshards, len(mine), len(todo), a.gpu, a.csv))
    # ---- PID 文件：让看护用 `kill -0` 判存活，而不是靠正则匹配命令行
    #      （教训：pgrep 模式写错会导致看护以为"全死了"而反复重复起进程）
    pidf = a.csv + '.pid'
    io.open(pidf, 'w', encoding='utf-8').write('%d\n' % os.getpid())
    cache, t_start = {}, time.time()
    for i, t in enumerate(todo, 1):
        key = t['w']
        t0 = time.time()
        # 2026-09-27：**单任务失败不许拖垮整片**。实测：撞上缺权重的 run（如
        # r10_aitod20_base30_3way_s43n 的 best.pt 不存在）时 `YOLO()` 抛 FileNotFoundError，
        # 整片死 → 看护重启 → 又撞同一个任务 ⇒ 无限重启、行长不动（卡在 ~2,004/2,100）。
        # 处置：捕获并把失败行落盘，续跑按 (run,ckpt,pct,draw) 跳过，于是**不再撞**。
        try:
            if key not in cache:
                cache = {key: YOLO(t['w'])}      # 同类只留一个模型在显存里
            m = cache[key]
            r = m.val(data=t['yaml'], split='test', imgsz=640, batch=32, device=0,
                      project=os.path.join(ROOT, 'val_runs'),
                      name='%s__%s__%s' % (t['tag'], t['run'], t['ckpt']), exist_ok=True,
                      verbose=False, plots=False, cache=False, workers=a.workers)
            secs = time.time() - t0
            cells = ['%.4f' % (r.box.map * 100), '%.4f' % (r.box.map50 * 100), '%.1f' % secs]
            err = ''
        except Exception as e:
            cache = {}
            secs = time.time() - t0
            bad = 'FAIL:' + type(e).__name__
            cells = [bad, bad, '%.1f' % secs]
            err = '  <<< %s' % str(e).replace('\n', ' ')[:110]
            print('[%d/%d] FAIL %s %s：%s: %s' % (i, len(mine), t['run'], t['ckpt'],
                                                  type(e).__name__, str(e)[:120]))
        wr.writerow([t['cell'], t['arm'], t['run'], t['ckpt'], t['pct'], t['draw'], t['n']] + cells)
        fh.flush()
        if not err:
            print('[%d/%d] %-9s %-5s %-34s %-4s pct=%-3d d=%02d n=%-5d map=%.4f (%.0fs, 累计 %.0f min)'
                  % (i, len(mine), t['cell'], t['arm'], t['run'], t['ckpt'], t['pct'], t['draw'],
                     t['n'], float(cells[0]), secs, (time.time() - t_start) / 60))
    fh.close()
    try:
        os.remove(pidf)
    except OSError:
        pass
    if not todo:
        io.open(a.csv + '.done', 'w', encoding='utf-8').write('done %s\n' % time.strftime('%FT%T'))
        print('本片无待跑任务 → 写完成标记 %s.done' % a.csv)
    print('本片完成，用时 %.1f min' % ((time.time() - t_start) / 60))
    return 0


if __name__ == '__main__':
    sys.exit(main())
