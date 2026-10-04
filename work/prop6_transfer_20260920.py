# -*- coding: utf-8 -*-
"""Does the val-side selection premium transfer?  A decisive, GPU-free check of theory §9.4.

Data: 41 runs that already have per-epoch TEST readouts (`xeval_perepoch_20260918/matrix_perepoch.csv`,
epochs 0,5,…,95) whose per-epoch VAL curves come from the runs' own results.csv on the pod.

Everything is measured on the SAME 5-epoch grid so the two sides are comparable:
    prem_val(O)   = max_grid val − val(95)                     oracle peak on val
    prem_test(O)  = max_grid test − test(95)                   oracle peak on test (upper bound)
    prem_test(sel)= test(ê_val) − test(95)                     what selecting on val actually delivers
Then: how much of the *val* premium survives the transfer, and is the loss explained by the val peak
landing at a different epoch than the test peak?
"""
import csv
import io
import os
import re
import sys
from collections import defaultdict

# ★ r205 发布卫生修正：**不得在发布件里写明文口令**。
#   本脚本原先把集群口令硬编码在 `password=` 里；改为从环境变量读取（不存在时给出可执行的报错，
#   而不是回落到硬编码值）。变量：`P2_GPU_HOST` / `P2_GPU_PORT` / `P2_GPU_USER` / `P2_GPU_PASSWORD`。
import os as _os


def _cluster_creds(default_host, default_port):
    pw = _os.environ.get('P2_GPU_PASSWORD')
    if not pw:
        raise SystemExit('!! 需要口令：请设环境变量 P2_GPU_PASSWORD（发布件不再内置凭据）。')
    return (_os.environ.get('P2_GPU_HOST', default_host),
            int(_os.environ.get('P2_GPU_PORT', default_port)),
            _os.environ.get('P2_GPU_USER', 'root'), pw)
import numpy as np
import paramiko

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
COL = 'metrics/mAP50-95(B)'
LOCAL = os.path.join(W, 'r10_runs')
OUT = os.path.join(W, 'work', 'prop6_transfer_20260920.txt')
L = []


def emit(s=''):
    L.append(s)
    print(s)


def pull(names):
    os.makedirs(LOCAL, exist_ok=True)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    _h, _p, _u, _pw = _cluster_creds('cpod-1uearmsfxbj2.podtcp.compshare.cn', 25046)
    c.connect(_h, port=_p, username=_u, password=_pw, timeout=40)
    sftp = c.open_sftp()
    got = 0
    for r in names:
        d = os.path.join(LOCAL, r)
        os.makedirs(d, exist_ok=True)
        try:
            sftp.get('/workspace/runs/%s/results.csv' % r, os.path.join(d, 'results.csv'))
            got += 1
        except Exception:
            pass
    c.close()
    print('  拉回 %d / %d 个 run 的 results.csv' % (got, len(names)))


def val_curve(run):
    p = os.path.join(LOCAL, run, 'results.csv')
    if not os.path.exists(p):
        return {}
    with io.open(p, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    return {int(r['epoch']): float(r[COL]) * 100 for r in rows
            if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')}


def main():
    P = os.path.join(W, 'xeval_perepoch_20260918', 'matrix_perepoch.csv')
    rows = list(csv.DictReader(io.open(P, encoding='utf-8', errors='ignore')))
    test = defaultdict(dict)
    for r in rows:
        if r['split'] == 'test':
            test[r['run']][int(r['epoch'])] = float(r['map50_95'])
    names = sorted(test)
    print('=== 拉 val 曲线 ===')
    pull(names)

    rec = []
    for run in names:
        tv, vv = test[run], val_curve(run)
        grid = sorted(set(tv) & set(vv))
        if len(grid) < 8:
            continue
        v = np.array([vv[e] for e in grid])
        t = np.array([tv[e] for e in grid])
        iv, it = int(np.argmax(v)), int(np.argmax(t))
        rec.append(dict(run=run, n=len(grid), grid=grid,
                        prem_val=v.max() - v[-1], prem_test_oracle=t.max() - t[-1],
                        prem_test_sel=t[iv] - t[-1],
                        e_val=grid[iv], e_test=grid[it],
                        v=v, t=t, arm=('lr005' if '_lr005_' in run else 'base')))

    emit('')
    emit('=' * 104)
    emit('val 侧选点能否转移到不相交读点？（同一 5 轮网格上的配对比较，n = %d 个 run）' % len(rec))
    emit('=' * 104)
    emit(' %-40s %4s %10s %12s %12s %8s %8s' %
         ('run', 'n', 'prem_val', 'test 神谕', 'test 实得', 'ê_val', 'ê_test'))
    for r in rec:
        emit(' %-40s %4d %+10.3f %+12.3f %+12.3f %8d %8d'
             % (r['run'][:40], r['n'], r['prem_val'], r['prem_test_oracle'], r['prem_test_sel'],
                r['e_val'], r['e_test']))

    pv = np.array([r['prem_val'] for r in rec])
    po = np.array([r['prem_test_oracle'] for r in rec])
    ps = np.array([r['prem_test_sel'] for r in rec])
    same = np.mean([r['e_val'] == r['e_test'] for r in rec])
    emit('')
    emit('--- 汇总（%d 个 run）---' % len(rec))
    emit('  premium(val) 均值            %+8.3f pp' % pv.mean())
    emit('  premium(test, 神谕上界) 均值  %+8.3f pp  ⇒ 占 val 的 %.1f%%' % (po.mean(), 100 * po.mean() / pv.mean()))
    emit('  premium(test, 用 val 选点) 均值 %+8.3f pp  ⇒ 占 val 的 %.1f%%' % (ps.mean(), 100 * ps.mean() / pv.mean()))
    emit('  val 峰与 test 峰落在同一 epoch 的比例：%.1f%%' % (100 * same))
    d = np.array([abs(r['e_val'] - r['e_test']) for r in rec])
    emit('  |ê_val − ê_test| 中位数 %d 轮（网格步长 5 轮）' % int(np.median(d)))
    emit('  val 侧选点保住了多少"神谕可得的 test 溢价"：%.1f%%'
         % (100 * ps.mean() / po.mean() if po.mean() else float('nan')))

    emit('')
    emit('--- 形状项在两边的占比（同网格）---')
    for side, key in (('val', 'v'), ('test', 't')):
        M = np.vstack([r[key] for r in rec])
        m = M.mean(axis=0)
        prem = (M.max(axis=1) - M[:, -1]).mean()
        shape = m.max() - m[-1]
        emit('  %-5s premium 均 %+7.3f，shape %7.3f ⇒ 占比 %5.1f%%'
             % (side, prem, shape, 100 * shape / prem if prem else 0))

    emit('')
    emit('--- 读法 ---')
    emit('  ① 若"用 val 选点"远小于"神谕上界"，说明损失来自**峰位置不一致**，而不是 test 侧没有收益；')
    emit('  ② 若两侧 shape 都占大头，则 19%% 兑现率的成因是"形状是划分自身的属性"，')
    emit('     而非"选点无效"——这正是理论 §9.3 第 2 条的机制，现在有配对数据支撑。')
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('\n已写：%s' % OUT)


if __name__ == '__main__':
    main()
