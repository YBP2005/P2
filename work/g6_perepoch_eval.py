#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""g6_perepoch_eval.py — G6：把各 arm-cell 的 `epoch*.pt` 逐点评 `split="test"`，
形成"逐 epoch 测试曲线"，供 `prem_test` / WC 使用（只评不训）。

**为什么需要**：稿件 §S12 自己写着 `prem_test`（进而 WC）只在 5 个 arm-cell 上有记录，
`aitod20` strategy 臂与另外十格"没有逐 epoch test 曲线，`prem_test` 无法形成"。

评估调用**逐字照**已登记的两个脚本（本组读数已复现到四位小数）：
    work/x4_teval.py               （best/last）
    /tmp/p4_perepoch_teval.py      （逐 epoch）
        m = YOLO(w)
        r = m.val(data=dy, split='test', batch=32, imgsz=640, device=GPU,
                  plots=False, verbose=False, save_json=False,
                  project=DIR, name='_val_tmp', exist_ok=True)
**不 import modules/losses**。

ckpt ↔ 训练轮次（p4 冻结本 §1.6a 实测）：`epoch{N}.pt` = 训完 **N+1** 轮；
`last.pt` = 训完 `epochs_done` 轮；`best.pt` = 未知（留空）。

纪律：
  * data yaml 从**该 run 自己的 args.yaml** 读，不硬编码（跨族通用）；
  * 断言 yaml **内容**含 `carve_`（三方）且含 `test:`（真有 held-out），否则记 problem 不评；
  * `epoch*.pt` 个数与清单声明的 `epochs//5` 不符 → 记 problem，**仍评已存在的点**（缺口在清单里点名）；
  * 增量写、可断点续跑（已登记的 `(run, ckpt)` 直接跳过）；
  * 两卡分片：`--shard i --nshard 2` 按 plan 下标取模，两卡负载基本均等。

用法：
    python g6_perepoch_eval.py --gpu 0 --shard 0 --nshard 2 --plan-only     # 先只看计划
    python g6_perepoch_eval.py --gpu 0 --shard 0 --nshard 2                 # 卡0
    python g6_perepoch_eval.py --gpu 1 --shard 1 --nshard 2                 # 卡1
"""
import argparse
import hashlib
import io
import os
import re
import sys
import time
import traceback

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RUNDIR = '/workspace/runs'
HDR = 'run,cell,arm,seed,ckpt,ckpt_epoch,split,map50_95,map50,mp,mr,data_yaml,secs\n'
ARMS = ('lr005_100ep', 'lr005_30ep', 'base100', 'base30')


def field(path, key):
    if not os.path.exists(path):
        return None
    for line in io.open(path, encoding='utf-8', errors='replace'):
        if line.startswith(key + ':'):
            return line.split(':', 1)[1].strip()
    return None


def epochs_done(rd):
    p = os.path.join(rd, 'results.csv')
    if not os.path.exists(p):
        return 0
    with io.open(p, encoding='utf-8', errors='replace') as fh:
        return max(0, sum(1 for _ in fh) - 1)


def ckpt_epoch(name, done):
    """epoch{N}.pt → N+1；last → done；best → None（未知）"""
    if name == 'last':
        return done
    if name == 'best':
        return None
    m = re.match(r'^epoch(\d+)$', name)
    return int(m.group(1)) + 1 if m else None


def parse_name(run):
    """r10_p_aitovis_base100_3way_s42n → ('p_aitovis', 'base100', 42)"""
    m = re.match(r'^r\d+_(.+?)_s(\d+)n$', run)
    if not m:
        return ('', '', '')
    mid, seed = m.group(1), int(m.group(2))
    mid = re.sub(r'_(3way|20p|dota15|visdrone)$', '', mid)
    for arm in ARMS:
        if mid.endswith('_' + arm):
            return (mid[:-(len(arm) + 1)], arm, seed)
    return (mid, '', seed)


def read_list(path):
    out = []
    for line in io.open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        f = line.split('\t')
        out.append((f[0].strip(), int(f[1]) if len(f) > 1 and f[1].strip() else 0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', default='/workspace/g6_pull_list.tsv')
    ap.add_argument('--gpu', default='0')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshard', type=int, default=1)
    ap.add_argument('--dir', default='/workspace/g6_perepoch_20260930')
    ap.add_argument('--rundir', default=RUNDIR)
    ap.add_argument('--yaml', default='', help='覆盖 args.yaml 的 data 字段（跨机等价 yaml）')
    ap.add_argument('--limit', type=int, default=0, help='本次最多评多少次（0=不限）')
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--workers', type=int, default=8, help='val 的 dataloader worker 数（多片并发时按核数摊）')
    ap.add_argument('--plan-only', action='store_true', help='只做体检并打印计划，不评')
    a = ap.parse_args()

    os.makedirs(a.dir, exist_ok=True)
    shard = 'g%s_of%d' % (a.shard, a.nshard)
    OUT = os.path.join(a.dir, 'g6_perepoch.csv')
    if not os.path.exists(OUT):
        io.open(OUT, 'w', encoding='utf-8', newline='\n').write(HDR)

    done = set()
    for line in io.open(OUT, encoding='utf-8'):
        f = line.rstrip('\n').split(',')
        if len(f) >= 6 and f[0] != 'run':
            done.add((f[0], f[4]))

    runs = read_list(a.list)
    if not runs:
        print('EMPTY list: ' + a.list, flush=True)
        return 2

    # ---------- 体检：整表体检（两卡都看全量，便于对齐），再按分片取自己的 ----------
    plan_all, problems = [], []
    per_run = {}
    for (run, exp_ep) in runs:
        rd = os.path.join(a.rundir, run)
        if not os.path.isdir(rd):
            problems.append('MISSING run dir ' + run)
            per_run[run] = 0
            continue
        dy = a.yaml or field(os.path.join(rd, 'args.yaml'), 'data')
        if not dy or not os.path.exists(dy):
            problems.append('yaml absent for %s (%s)' % (run, dy))
            per_run[run] = 0
            continue
        body = io.open(dy, encoding='utf-8', errors='replace').read()
        if 'carve_' not in body:
            problems.append('NOT three-way yaml for %s: %s' % (run, dy))
            continue
        if 'test:' not in body:
            problems.append('no test split in %s (%s)' % (dy, run))
            continue
        done_n = epochs_done(rd)
        cell, arm, seed = parse_name(run)
        wd = os.path.join(rd, 'weights')
        names = [n[:-3] for n in os.listdir(wd) if n.endswith('.pt')] if os.path.isdir(wd) else []
        names = [n for n in names
                 if n == 'best' or n == 'last' or re.match(r'^epoch\d+$', n)]
        names.sort(key=lambda n: (ckpt_epoch(n, done_n) is None, ckpt_epoch(n, done_n) or 0))
        per_run[run] = len([n for n in names if re.match(r'^epoch\d+$', n)])
        exp_ck = exp_ep // 5
        if per_run[run] != exp_ck:
            problems.append('epoch*.pt count %d != %d (epochs=%d) for %s'
                            % (per_run[run], exp_ck, exp_ep, run))
        if done_n != exp_ep:
            problems.append('results.csv rows %d != declared %d for %s' % (done_n, exp_ep, run))
        for ck in names:
            plan_all.append((run, cell, arm, seed, ck, dy, done_n))

    plan = [p for i, p in enumerate(plan_all) if i % a.nshard == a.shard]
    todo = [p for p in plan if (p[0], p[4]) not in done]

    io.open(os.path.join(a.dir, 'g6_%s.preflight.txt' % shard), 'w',
            encoding='utf-8', newline='\n').write(
        'shard=%s runs=%d plan_all=%d plan_shard=%d todo=%d problems=%d\n%s\n'
        % (shard, len(runs), len(plan_all), len(plan), len(todo), len(problems),
           '\n'.join(problems)))
    print('SHARD %s runs=%d plan_all=%d plan_shard=%d todo=%d problems=%d'
          % (shard, len(runs), len(plan_all), len(plan), len(todo), len(problems)), flush=True)
    for p in problems[:30]:
        print('  problem:', p, flush=True)
    if problems:
        print('  ... problems total=%d 详见 %s' % (len(problems),
              os.path.join(a.dir, 'g6_%s.preflight.txt' % shard)), flush=True)
    if a.plan_only:
        print('PLAN-ONLY 结束', flush=True)
        return 0

    from ultralytics import YOLO
    if not todo:
        print('NOTHING TODO (本分片全部已评)', flush=True)

    ok = fail = 0
    t_start = time.time()
    for (run, cell, arm, seed, ck, dy, done_n) in todo:
        if a.limit and (ok + fail) >= a.limit:
            print('LIMIT reached', flush=True)
            break
        w = os.path.join(a.rundir, run, 'weights', ck + '.pt')
        t0 = time.time()
        try:
            m = YOLO(w)
            r = m.val(data=dy, split='test', batch=a.batch, imgsz=640, device=a.gpu,
                      workers=a.workers, plots=False, verbose=False, save_json=False,
                      project=a.dir, name='_val_tmp_' + shard, exist_ok=True)
            b = r.box
            ce = ckpt_epoch(ck, done_n)
            with io.open(OUT, 'a', encoding='utf-8', newline='\n') as fh:
                fh.write('%s,%s,%s,%s,%s,%s,test,%.4f,%.4f,%.4f,%.4f,%s,%.1f\n' % (
                    run, cell, arm, seed, ck, ('' if ce is None else ce),
                    b.map * 100, b.map50 * 100, b.mp * 100, b.mr * 100, dy,
                    time.time() - t0))
            ok += 1
            print('ok %-40s %-8s ep=%-4s map50_95=%.4f (%.1fs) [%d/%d]'
                  % (run, ck, ('' if ce is None else ce), b.map * 100,
                     time.time() - t0, ok + fail, len(todo)), flush=True)
        except Exception:
            fail += 1
            print('FAIL %s %s\n%s' % (run, ck, traceback.format_exc()), flush=True)

    h = hashlib.sha256(io.open(OUT, 'rb').read()).hexdigest()
    io.open(os.path.join(a.dir, 'g6_%s.SHA256' % shard), 'w', encoding='utf-8',
            newline='\n').write('%s  g6_perepoch.csv\n' % h)
    rows = sum(1 for _ in io.open(OUT, encoding='utf-8')) - 1
    # ★ 纪律：只有"把计划的 todo 全部走完"才写 .DONE；
    #   被 --limit 截断时只写 .PARTIAL，避免下游把半截分片当成完成（2026-09-28 教训）。
    truncated = bool(a.limit and (ok + fail) < len(todo))
    stamp = ('ok=%d fail=%d rows=%d todo=%d sha256=%s wall=%.0fs at=%s\n' % (
        ok, fail, rows, len(todo), h, time.time() - t_start,
        time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime())))
    if truncated:
        io.open(os.path.join(a.dir, 'g6_%s.PARTIAL' % shard), 'w', encoding='utf-8',
                newline='\n').write('TRUNCATED-BY-LIMIT\n' + stamp)
        print('SHARD %s PARTIAL(limit) ok=%d fail=%d rows=%d' % (shard, ok, fail, rows), flush=True)
    else:
        io.open(os.path.join(a.dir, 'g6_%s.DONE' % shard), 'w', encoding='utf-8',
                newline='\n').write(stamp)
        print('SHARD %s DONE ok=%d fail=%d rows=%d sha=%s wall=%.0fs'
              % (shard, ok, fail, rows, h, time.time() - t_start), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
