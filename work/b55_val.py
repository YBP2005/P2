# -*- coding: utf-8 -*-
"""B55 · mAP75 的 **val 半列**（评测级，用**在册的逐 epoch 检查点**，不重训）。

对 Table 4 的四族（`r10_shwd2sf`/`r10_smoke2sf` × `base100`/`lr005_100ep`，各 10 种子）：
  · 把 `weights/epoch*.pt` 的**每一个**（实测 `epoch0,5,…,95` 的 5 轮网格）在该 run 自己的
    **val** 切分上重评，记 mAP50-95 / mAP50 / **mAP75**；
  · 同时把 `results.csv` 里**同 epoch** 的 `metrics/mAP50-95(B)` 一起落盘 ⇒ 阳性控制（训练时读数 vs 现在重评）；
  · `last.pt` 也评一次（epoch 取 results.csv 末行），用于"网格末点 vs 真末点"的对齐说明。

**口径必须随数一起报**：这是 **5 轮网格** 的 val 曲线，不是逐 epoch argmax ⇒
`prem_val(grid) ≤ prem_val(true)`，用它算兑现率会偏高。本脚本把两者都算出来供量化。

**实测（2026-09-28，B 机）**：40 个 run 共用同一个 val 目录 `carve_sfchd20/images`（1000 图 / 1386 实例）；
无 cache 时首次 `cache_labels` 扫描 ≈190 s，命中 cache 后单次 val ≈8 s ⇒ 840 个任务的成本
≈(190 s 一次) + 840×8 s/8 片 ≈ 20 min。cache 存在时一律不重写（8 片并发写同一文件会损坏）。

用法（B 机）：python b55_val.py --gpu 0 --shard 0 --nshards 2 --csv /tmp/b55_val_s0.csv
"""
import argparse
import csv
import glob as _glob
import io
import os
import re
import sys
import time

ROOT = '/workspace/runs'
SEEDS = list(range(42, 52))
FAM = [('shwd2sf', 'base100', 'r10_shwd2sf_base100_3way_s%dn'),
       ('shwd2sf', 'lr005_100ep', 'r10_shwd2sf_lr005_100ep_3way_s%dn'),
       ('smoke2sf', 'base100', 'r10_smoke2sf_base100_3way_s%dn'),
       ('smoke2sf', 'lr005_100ep', 'r10_smoke2sf_lr005_100ep_3way_s%dn')]


def val_curve(d):
    """results.csv → {检查点编号: mAP50-95×100}。

    ⚠ `results.csv` 的 `epoch` 列是 **1-based**，而权重文件名 `epoch{N}.pt` 是 0-based
    ⇒ 第 N 个检查点对应 results.csv 的 **N+1** 行。故这里把下标减 1 落到检查点编号上
    （实测判据：重评值 vs 曲线[e+1] 中位 |Δ| 0.0161 pp，vs 曲线[e] 0.6462 pp）。
    """
    p = os.path.join(d, 'results.csv')
    if not os.path.exists(p):
        return {}, None
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return {}, None
    vcol = next((c for c in rows[0] if c.strip() == 'metrics/mAP50-95(B)'), None)
    out = {}
    for r in rows:
        try:
            out[int(float(r['epoch'])) - 1] = float(r[vcol]) * 100
        except (TypeError, ValueError):
            pass
    return out, (max(out) if out else None)


_NVAL = {}


def wpath(p, ckroot):
    """检查点镜像重定向；镜像里没有该文件就回退原路径（保证不会因缺件而漏评）。"""
    if not ckroot:
        return p
    q = p.replace('/workspace/runs/', ckroot.rstrip('/') + '/', 1)
    return q if os.path.exists(q) else p


def n_val_images(yml):
    """该 data yaml 的 val 目录图片数（并缓存），用于审计列 n_img。"""
    if not yml:
        return ''
    if yml in _NVAL:
        return _NVAL[yml]
    n = ''
    try:
        import yaml as _y
        dd = _y.safe_load(io.open(yml, encoding='utf-8', errors='replace'))
        vd = os.path.join(dd.get('path', '') or '', dd.get('val', '') or '')
        if vd and os.path.isdir(vd):
            n = len(_glob.glob(os.path.join(vd, '*')))
    except Exception:
        n = ''
    _NVAL[yml] = n
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpu', default='0')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshards', type=int, default=2)
    ap.add_argument('--csv', default='/tmp/b55_val_s0.csv')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--tags', default='grid,last',
                    help='要评的检查点类别：grid（epoch*.pt 网格）/ last / best，逗号分隔')
    ap.add_argument('--yaml', default='',
                    help='覆盖各 run args.yaml 的 data:（用于 /dev/shm 的 RAM 镜像；图/标签字节相同）')
    ap.add_argument('--ckroot', default='',
                    help='检查点镜像根（如 /dev/shm/b55v/ck）：把 /workspace/runs/<run>/weights/x.pt '
                         '换成 <ckroot>/<run>/weights/x.pt；镜像里没有则回退原路径')
    a = ap.parse_args()
    tags = [x.strip() for x in a.tags.split(',') if x.strip()]
    os.environ['CUDA_VISIBLE_DEVICES'] = a.gpu

    T = []
    for cell, arm, tpl in FAM:
        for s in SEEDS:
            run = tpl % s
            d = os.path.join(ROOT, run)
            yml = None
            args = os.path.join(d, 'args.yaml')
            if os.path.exists(args):
                for line in io.open(args, encoding='utf-8', errors='replace'):
                    if line.startswith('data:'):
                        yml = line.split(':', 1)[1].strip()
            curve, last_ep = val_curve(d)
            if a.yaml:
                yml = a.yaml          # RAM 镜像覆盖
            nval = n_val_images(yml)
            cks = []
            for p in _glob.glob(os.path.join(d, 'weights', 'epoch*.pt')):
                m = re.search(r'epoch(\d+)\.pt$', p)
                if m:
                    cks.append((int(m.group(1)), p))
            cks.sort()
            for ep, p in cks:
                if 'grid' not in tags:
                    continue
                T.append(dict(cell=cell, arm=arm, seed=s, run=run, epoch=ep, w=wpath(p, a.ckroot),
                              yaml=yml, curve=curve, last_ep=last_ep, tag='grid', nval=nval))
            lp = os.path.join(d, 'weights', 'last.pt')
            if 'last' in tags and os.path.exists(lp):
                T.append(dict(cell=cell, arm=arm, seed=s, run=run, epoch=last_ep,
                              w=wpath(lp, a.ckroot),
                              yaml=yml, curve=curve, last_ep=last_ep, tag='last', nval=nval))
            bp = os.path.join(d, 'weights', 'best.pt')
            if 'best' in tags and os.path.exists(bp):
                # best.pt 的 epoch 不在 results.csv 里 ⇒ epoch 列写 'best'，
                # 其真实 epoch 由控制脚本用「重评 mAP50-95 与全曲线最近邻」反查。
                T.append(dict(cell=cell, arm=arm, seed=s, run=run, epoch='best',
                              w=wpath(bp, a.ckroot),
                              yaml=yml, curve=curve, last_ep=last_ep, tag='best', nval=nval))
    mine = [t for i, t in enumerate(T) if i % a.nshards == a.shard]
    done = set()
    if os.path.exists(a.csv):
        for r in csv.DictReader(io.open(a.csv, encoding='utf-8', errors='replace')):
            # FAIL 行不算完成 ⇒ 下次续跑会重试（否则一次偶发失败会被永久跳过）
            if r.get('run') and r.get('epoch') and not str(r.get('map50_95', '')).startswith('FAIL'):
                done.add((r['run'], r['epoch'], r['tag']))
    todo = [t for t in mine if (t['run'], str(t['epoch']), t['tag']) not in done]
    print('shard %d/%d：本片任务 %d，待跑 %d（全量任务 %d）' % (a.shard, a.nshards, len(mine), len(todo), len(T)))
    if not todo:
        io.open(a.csv + '.done', 'w', encoding='utf-8').write('done\n')
        print('本片已完成 → 写 %s.done' % a.csv)
        return 0

    from ultralytics import YOLO
    import ultralytics.data.dataset as _ds
    import ultralytics.data.utils as _du

    # 缓存策略（2026-09-28 实测修正）：本批 40 个 run **共用同一个 val 目录**
    # （/workspace/datasets/split_5_5/carve_sfchd20，1000 图）。首次无 cache 时 ultralytics 要
    # cache_labels 扫描 ≈190 s，之后命中 cache 只要 ≈8 s。故：
    #   · cache 已存在 ⇒ 一律不重写（8 片并发写同一个 cache 文件会互相损坏）；
    #   · cache 不存在 ⇒ 放行原生写入，让扫描成本只付一次。
    # 注意 no-op 分支仍要补 hash/version/msgs 键（B51 的 KeyError: 'version' 教训）。
    _orig_save = _du.save_dataset_cache_file

    def _guarded(*ar, **k):
        p = next((v for v in ar if isinstance(v, str) and v.endswith('.cache')), None)
        if p is None:
            p = next((v for v in k.values() if isinstance(v, str) and v.endswith('.cache')), None)
        if p and os.path.exists(p):
            d = next((v for v in ar if isinstance(v, dict)), None)
            if d is None:
                d = next((v for v in k.values() if isinstance(v, dict)), None)
            if isinstance(d, dict):
                d.setdefault('hash', 'cache-disabled')
                d.setdefault('version', 'cache-disabled')
                d.setdefault('msgs', [])
            return None
        return _orig_save(*ar, **k)

    _du.save_dataset_cache_file = _guarded
    if hasattr(_ds, 'save_dataset_cache_file'):
        _ds.save_dataset_cache_file = _guarded

    newf = not os.path.exists(a.csv)
    # 并发保护：同一片不允许两个进程同时写（重启重叠会造成重复行）
    _pf = a.csv + '.pid'
    if os.path.exists(_pf):
        try:
            _old = int(io.open(_pf, encoding='utf-8').read().strip())
        except ValueError:
            _old = -1
        if _old > 0 and os.path.exists('/proc/%d' % _old):
            print('本片已有存活进程 pid=%d ⇒ 退出（避免重复写行）' % _old)
            return 1
    fh = io.open(a.csv, 'a', encoding='utf-8', newline='\n')
    wr = csv.writer(fh)
    if newf:
        wr.writerow(['run', 'cell', 'arm', 'seed', 'epoch', 'tag', 'split', 'map50_95', 'map50',
                     'map75', 'rec_5095_same', 'rec_5095_next', 'n_img', 'secs'])
        fh.flush()
    io.open(a.csv + '.pid', 'w', encoding='utf-8').write('%d\n' % os.getpid())
    t_start = time.time()
    for i, t in enumerate(todo, 1):
        t0 = time.time()
        if not t['yaml'] or not os.path.exists(t['yaml']):
            print('[%d/%d] SKIP（yaml 不在）%s e%s  yaml=%s' % (i, len(todo), t['run'], t['epoch'], t['yaml']))
            wr.writerow([t['run'], t['cell'], t['arm'], t['seed'], t['epoch'], t['tag'], 'val',
                         'FAIL:no_yaml', 'FAIL:no_yaml', 'FAIL:no_yaml', '', '', '', '%.1f' % (time.time() - t0)])
            fh.flush()
            continue
        try:
            m = YOLO(t['w'])
            r = m.val(data=t['yaml'], split='val', imgsz=640, batch=32, device=0, workers=a.workers,
                      project='/tmp/b55_val_runs', name='%s_e%s_%s' % (t['run'], t['epoch'], t['tag']),
                      exist_ok=True, verbose=False, plots=False)
            v95, v50, v75 = r.box.map * 100, r.box.map50 * 100, r.box.map75 * 100
            n_img = t['nval']
            del m
        except Exception as e:
            bad = 'FAIL:' + type(e).__name__
            wr.writerow([t['run'], t['cell'], t['arm'], t['seed'], t['epoch'], t['tag'], 'val',
                         bad, bad, bad, '', '', '', '%.1f' % (time.time() - t0)])
            fh.flush()
            print('[%d/%d] FAIL %s e%s：%s' % (i, len(todo), t['run'], t['epoch'], str(e)[:100]))
            continue
        cur = t['curve'].get(t['epoch'], '')
        nxt = t['curve'].get(t['epoch'] + 1, '') if isinstance(t['epoch'], int) else ''
        wr.writerow([t['run'], t['cell'], t['arm'], t['seed'], t['epoch'], t['tag'], 'val',
                     '%.4f' % v95, '%.4f' % v50, '%.4f' % v75,
                     ('%.4f' % cur) if cur != '' else '', ('%.4f' % nxt) if nxt != '' else '',
                     n_img, '%.1f' % (time.time() - t0)])
        fh.flush()
        print('[%d/%d] %-38s e%-3s %-4s map50-95=%.4f map75=%.4f rec=%.4f (%.0fs, 累计 %.0f min)'
              % (i, len(todo), t['run'], t['epoch'], t['tag'], v95, v75,
                 cur if cur != '' else float('nan'), time.time() - t0, (time.time() - t_start) / 60))
    fh.close()
    try:
        os.remove(a.csv + '.pid')
    except OSError:
        pass
    io.open(a.csv + '.done', 'w', encoding='utf-8').write('done\n')
    print('本片完成 %.1f min' % ((time.time() - t_start) / 60))
    return 0


if __name__ == '__main__':
    sys.exit(main())
