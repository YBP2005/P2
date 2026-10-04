# -*- coding: utf-8 -*-
"""Proposition 6 (shape v. noise in the selection premium) -- empirical decomposition.

Fix v2: results.csv holds E data rows (epochs 1..E) plus a header, so completeness is decided by the
last EPOCH NUMBER, not by the row count.  Also pulls fresh CSVs first: the local copy of the running
E=400 run was stale (9 rows).

    premium_r = max_e V_r(e) - V_r(E) = shape(E) + nu_r     (exact, by construction)
    m(e)      = mean over runs of V_r(e);  shape(E) = max_e m(e) - m(E)
"""
import csv
import io
import os
import re
import sys

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
OUT = os.path.join(W, 'work', 'prop6_shape_noise_20260920.txt')
L = []


def emit(s=''):
    L.append(s)
    print(s)


def pull():
    d = os.path.join(W, 'g3ext_runs')
    os.makedirs(d, exist_ok=True)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    _h, _p, _u, _pw = _cluster_creds('cpod-1uearmsfxbj2.podtcp.compshare.cn', 25046)
    c.connect(_h, port=_p, username=_u, password=_pw, timeout=40)
    sftp = c.open_sftp()
    runs = [l.strip().split('/')[-1] for l in
            c.exec_command('ls -d /workspace/runs/g3ext_*')[1].read().decode().splitlines()]
    n = 0
    for r in runs:
        os.makedirs(os.path.join(d, r), exist_ok=True)
        try:
            sftp.get('/workspace/runs/%s/results.csv' % r, os.path.join(d, r, 'results.csv'))
            n += 1
        except Exception:
            pass
    c.close()
    print('  已刷新 %d 个 run 的 results.csv' % n)


def curve(d, run):
    p = os.path.join(d, run, 'results.csv')
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    v = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
         if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    v.sort()
    return v


def main():
    print('=== 先拉最新 CSV ===')
    pull()
    runs = {}
    for d in (os.path.join(W, 'g3ext_runs'), os.path.join(W, 'g3_epochs_runs')):
        if not os.path.isdir(d):
            continue
        for run in sorted(os.listdir(d)):
            m = re.match(r'^g3(?:ext)?_e(\d+)_(base|lr005)_s(\d+)n$', run)
            if not m:
                continue
            v = curve(d, run)
            if not v:
                continue
            E = int(m.group(1))
            if v[-1][0] != E:
                emit('  排除未跑完：%s（到最后 epoch %d / %d）' % (run, v[-1][0], E))
                continue
            seq = np.array([x for _, x in v])
            if len(seq) != E:
                emit('  排除：%s 的 epoch 序列长度 %d ≠ %d' % (run, len(seq), E))
                continue
            runs.setdefault((E, m.group(2)), []).append((int(m.group(3)), seq))

    emit('')
    emit('=' * 98)
    emit('命题 6 实测：premium_r = shape(E) + ν_r（按臂分组，shape 取自该臂的均值曲线；epoch 1..E）')
    emit('=' * 98)
    emit(' %-5s %-6s %3s %11s %10s %10s %9s %10s' %
         ('E', 'arm', 'n', 'premium 均', 'shape', 'shape 占比', 'sd(ν)', 'sd(premium)'))
    rows = {}
    for (E, arm) in sorted(runs):
        arrs = sorted(runs[(E, arm)])
        V = np.vstack([v for _, v in arrs])
        prem = V.max(axis=1) - V[:, -1]
        m = V.mean(axis=0)
        shape = m.max() - m[-1]
        nu = prem - shape
        rows[(E, arm)] = dict(prem=prem.mean(), shape=shape, sdnu=nu.std(ddof=1),
                              sdp=prem.std(ddof=1), n=len(V), V=V)
        emit(' %-5d %-6s %3d %+11.3f %10.3f %9.1f%% %9.3f %10.3f'
             % (E, arm, len(V), prem.mean(), shape,
                100.0 * shape / prem.mean() if prem.mean() else 0, nu.std(ddof=1), prem.std(ddof=1)))

    emit('')
    emit('--- 两臂合并 ---')
    emit(' %-5s %12s %10s %10s %10s %12s' % ('E', 'premium 均', 'shape', 'shape 占比', 'sd(ν)', 'ν 均值'))
    comb = {}
    for E in sorted({k[0] for k in rows}):
        aa = [rows[(E, a)] for a in ('base', 'lr005') if (E, a) in rows]
        p = np.mean([a['prem'] for a in aa])
        s = np.mean([a['shape'] for a in aa])
        sd = np.mean([a['sdnu'] for a in aa])
        mu = np.mean([np.mean(a['V'].max(axis=1) - a['V'][:, -1] - a['shape']) for a in aa])
        comb[E] = (p, s, sd, mu)
        emit(' %-5d %+12.3f %10.3f %9.1f%% %10.3f %+12.3f' % (E, p, s, 100.0 * s / p if p else 0, sd, mu))

    emit('')
    emit('--- 判据 ---')
    Es = sorted(comb)
    if len(Es) >= 2:
        a, b = Es[0], Es[-1]
        emit('  E = %d → %d：shape ×%.3f，premium ×%.3f，sd(ν) ×%.3f；σ√(2 ln E) 型预测 ×%.3f'
             % (a, b, comb[b][1] / comb[a][1] if comb[a][1] else float('nan'),
                comb[b][0] / comb[a][0] if comb[a][0] else float('nan'),
                comb[b][2] / comb[a][2] if comb[a][2] else float('nan'),
                np.sqrt(np.log(b) / np.log(a))))
        emit('  ① 若 premium 的增幅 ≈ shape 的增幅（且远大于 sd(ν) 的增幅）⇒ 水平由形状决定；')
        emit('  ② ν 的均值 %s 0 ⇒ 噪声项在溢价里只占很小一块。'
             % ('≥' if comb[b][3] >= 0 else '<'))
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('\n已写：%s' % OUT)


if __name__ == '__main__':
    main()
