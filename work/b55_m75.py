# -*- coding: utf-8 -*-
"""B55 · mAP75 的 **test 半列**（评测级；val 半列要重训，不做）。

对 Table 4 的 50 个 run（40 既有 + aitod20 的 n=10 扩展）评 `best.pt` / `last.pt` 在**该 run 训练时
用的那份 3-way yaml 的 test 切分**上的 mAP50-95 / mAP50 / **mAP75**。

* 阳性控制：mAP50-95 必须复现论文 Table 4 的来源值（matrix.csv / x4fill / x4_teval）到 ≤0.005 pp
  —— 本脚本把 map50_95 一起落盘，供本地对账。
* 断点续跑：跳过 CSV 里已有的 (run, ckpt)。
* labels.cache：**写侧补键但不落盘**（同 B51 的 2026-09-27 修正），读侧保留。

用法（B 机）：python b55_m75.py --gpu 0 --shard 0 --nshards 2 --csv /tmp/b55_m75_s0.csv --runs b55_m75_runs.txt
"""
import argparse
import csv
import glob as _glob
import io
import os
import sys
import time

ROOT = '/workspace/runs'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpu', default='0')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshards', type=int, default=2)
    ap.add_argument('--csv', default='/tmp/b55_m75_s0.csv')
    ap.add_argument('--runs', default='/workspace/b55_m75_runs.txt')
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = a.gpu

    names = [l.strip() for l in io.open(a.runs, encoding='utf-8') if l.strip()]
    T = []
    for i, n in enumerate(names):
        if i % a.nshards != a.shard:
            continue
        d = os.path.join(ROOT, n)
        args = os.path.join(d, 'args.yaml')
        if not os.path.exists(args):
            print('MISS args.yaml %s' % n)
            continue
        yml = None
        for line in io.open(args, encoding='utf-8', errors='replace'):
            if line.startswith('data:'):
                yml = line.split(':', 1)[1].strip()
        for ck in ('best', 'last'):
            T.append(dict(run=n, ckpt=ck, w=os.path.join(d, 'weights', '%s.pt' % ck), yaml=yml))
    done = set()
    if os.path.exists(a.csv):
        for r in csv.DictReader(io.open(a.csv, encoding='utf-8', errors='replace')):
            if r.get('run'):
                done.add((r['run'], r['ckpt']))
    todo = [t for t in T if (t['run'], t['ckpt']) not in done]
    print('shard %d/%d：任务 %d，待跑 %d（%d 个 run）' % (a.shard, a.nshards, len(T), len(todo),
                                                        len({t['run'] for t in T})))
    if not todo:
        print('本片已完成')
        return 0

    from ultralytics import YOLO
    import ultralytics.data.dataset as _ds
    import ultralytics.data.utils as _du

    def _noop(*ar, **k):
        d = next((v for v in ar if isinstance(v, dict)), None)
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

    newf = not os.path.exists(a.csv)
    fh = io.open(a.csv, 'a', encoding='utf-8', newline='\n')
    wr = csv.writer(fh)
    if newf:
        wr.writerow(['run', 'ckpt', 'split', 'map50_95', 'map50', 'map75', 'yaml', 'secs'])
        fh.flush()
    io.open(a.csv + '.pid', 'w', encoding='utf-8').write('%d\n' % os.getpid())
    t0 = time.time()
    for i, t in enumerate(todo, 1):
        if not os.path.exists(t['w']) or not t['yaml']:
            print('[%d/%d] SKIP（缺权重或 yaml）%s %s' % (i, len(todo), t['run'], t['ckpt']))
            continue
        ts = time.time()
        try:
            m = YOLO(t['w'])
            r = m.val(data=t['yaml'], split='test', imgsz=640, batch=32, device=0, workers=a.workers,
                      project='/tmp/b55_m75_val', name='%s_%s' % (t['run'], t['ckpt']),
                      exist_ok=True, verbose=False, plots=False)
            mm, m50, m75 = r.box.map * 100, r.box.map50 * 100, r.box.map75 * 100
            del m
        except Exception as e:                      # 单个 run 失败不许拖垮整片
            print('[%d/%d] FAIL %s %s：%s: %s' % (i, len(todo), t['run'], t['ckpt'],
                                                  type(e).__name__, str(e)[:120]))
            wr.writerow([t['run'], t['ckpt'], 'test', 'FAIL', type(e).__name__, '', t['yaml'], '%.1f' % (time.time() - ts)])
            fh.flush()
            continue
        wr.writerow([t['run'], t['ckpt'], 'test', '%.4f' % mm, '%.4f' % m50, '%.4f' % m75,
                     t['yaml'], '%.1f' % (time.time() - ts)])
        fh.flush()
        print('[%d/%d] %-46s %-4s map50-95=%.4f map75=%.4f (%.0fs, 累计 %.1f min)'
              % (i, len(todo), t['run'], t['ckpt'], mm, m75, time.time() - ts, (time.time() - t0) / 60))
    fh.close()
    try:
        os.remove(a.csv + '.pid')
    except OSError:
        pass
    print('本片完成 %.1f min' % ((time.time() - t0) / 60))
    return 0


if __name__ == '__main__':
    sys.exit(main())
