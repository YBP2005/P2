# -*- coding: utf-8 -*-
"""G1′ verdict: the corrected aliasing test, judged by the criterion fixed before the runs.

Design recap (plan §8): train with `val = C2` (the selection split) and `test = C3`, where C3 is a
disjoint, **level-matched** split (measured difference −0.122 pp on the same checkpoints).  Then, for
the same run and the same checkpoints, read the premium twice:
    prem_C2 = M_C2(best) − M_C2(last)     <- selection side: the checkpoint was chosen on C2's noise
    prem_C3 = M_C3(best) − M_C3(last)     <- independent side, same difficulty
Pre-declared criterion:
    **WC = prem_C2 − prem_C3 > 0** (paired t, p < 0.05, and >= 8/10 runs of the same sign per arm)
    => the aliased reading inflates the reported gain.  Otherwise we report that the inflation is NOT
    detectable even on a level-matched pair, and say which assumption of Proposition 4 that touches.
Cross-check: prem_C2 must agree with the training-time val premium from results.csv (same split).
"""
import csv
import io
import os
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
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
COL = 'metrics/mAP50-95(B)'
_h, _p, _u, _pw = _cluster_creds('cpod-1u20pv1vhj4v.podtcp.compshare.cn', 24581)
A = dict(h=_h, p=_p, pw=_pw)
OUT = os.path.join(W, 'work', 'g1p_verdict_20260919.txt')
L = []


def emit(s=''):
    L.append(s)
    print(s)


c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(A['h'], port=A['p'], username='root', password=A['pw'], timeout=45, banner_timeout=45)
sftp = c.open_sftp()


def sh(cmd, t=300):
    _i, o, e = c.exec_command(cmd, timeout=t)
    return (o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')).strip()


print('=== marker 与产物 ===')
print(' g1p.DONE : %s' % sh('cat /workspace/g1p_20260919/g1p.DONE 2>/dev/null').replace('\n', ' | '))
print(' ABORT    : %s' % (sh('cat /workspace/g1p_20260919/g1p.ABORT 2>/dev/null') or '(无)'))
print(' 读数行数 : %s' % sh('wc -l < /workspace/g1p_20260919/g1p_readout.csv'))
print(' run 数   : %s' % sh('ls -d /workspace/runs/g1p_*_s*n | wc -l'))
print(' 日志尾   : %s' % sh('tail -n 3 /workspace/g1p_20260919/g1p.log').replace('\n', ' | ')[:200])

D = os.path.join(W, 'g1p_20260919')
RUNS = os.path.join(W, 'g1p_runs')
os.makedirs(D, exist_ok=True)
os.makedirs(RUNS, exist_ok=True)
for fn in ('g1p_readout.csv', 'g1p.SHA256', 'g1p.DONE'):
    try:
        sftp.get('/workspace/g1p_20260919/' + fn, os.path.join(D, fn))
    except Exception as ex:
        print(' 缺 %s：%r' % (fn, ex))
for name in sh('ls -d /workspace/runs/g1p_*_s*n | xargs -n1 basename').split():
    os.makedirs(os.path.join(RUNS, name), exist_ok=True)
    for fn in ('results.csv', 'args.yaml'):
        try:
            sftp.get('/workspace/runs/%s/%s' % (name, fn), os.path.join(RUNS, name, fn))
        except Exception:
            pass
c.close()

r = {}
with io.open(os.path.join(D, 'g1p_readout.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        r.setdefault(row['run'], {})[(row['ckpt'], row['side'])] = float(row['map50_95'])


def valprem(name):
    p = os.path.join(RUNS, name, 'results.csv')
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    v = [float(x[COL]) * 100 for x in rows if x.get(COL) and x.get(COL) not in ('', 'FAIL')]
    return max(v) - v[-1] if v else None


emit()
emit('=' * 96)
emit('G1′ · 层匹配对上的别名校准（val = C2 选点 / test = C3 独立读出，C2–C3 层差 −0.122 pp）')
emit('=' * 96)
emit()
emit('  %-32s %9s %9s %9s %9s %9s' % ('run', 'prem_C2', 'prem_C3', 'WC', '训练期val溢价', '一致性'))
d = []
for name in sorted(r):
    g = r[name]
    if ('best', 'C2_selection') not in g or ('last', 'C2_selection') not in g:
        continue
    p2 = g[('best', 'C2_selection')] - g[('last', 'C2_selection')]
    p3 = g[('best', 'C3_independent')] - g[('last', 'C3_independent')]
    tv = valprem(name)
    ok = 'ok' if (tv is not None and abs(p2 - tv) < 0.05) else ('差 %.3f' % (p2 - tv) if tv else '—')
    d.append((name, p2, p3, p2 - p3))
    emit('  %-32s %9.3f %9.3f %9.3f %9s %9s' % (name[:32], p2, p3, p2 - p3,
                                                ('%.3f' % tv) if tv is not None else '—', ok))

wc = np.array([x[3] for x in d])
emit()
emit('  (1) 主判据：WC = prem_C2 − prem_C3 > 0（配对 t，p < 0.05）')
t, p = stats.ttest_1samp(wc, 0.0)
tc = stats.t.ppf(0.975, len(wc) - 1)
emit('      n=%d  WC 均值 %+.3f pp，sd %.3f，配对 t=%.2f，**p=%.4g**，95%% CI [%+.3f, %+.3f]'
     % (len(wc), wc.mean(), wc.std(ddof=1), t, p,
        wc.mean() - tc * wc.std(ddof=1) / np.sqrt(len(wc)),
        wc.mean() + tc * wc.std(ddof=1) / np.sqrt(len(wc))))
emit('      ⇒ 主判据 %s' % ('**成立**：层匹配对上也测到别名抬高' if (wc.mean() > 0 and p < 0.05)
                          else '**不成立**：在层匹配对上也测不到抬高'))
emit()
emit('  (2) 按臂的符号计数（判据要求每臂 ≥ 8/10 同号；本实验每臂 n=5）')
for arm, pat in (('baseline', 'base100'), ('strategy', 'lr005')):
    sub = [x[3] for x in d if pat in x[0]]
    pos = sum(1 for v in sub if v > 0)
    emit('      %-9s n=%d  WC 均值 %+.3f，%d 正 / %d 负' % (arm, len(sub), float(np.mean(sub)),
                                                         pos, len(sub) - pos))
emit()
emit('  (3) 与 G1（旧设计）对照')
emit('      G1 旧设计：别名侧 +0.692、不相交侧 +1.274 ⇒ Δ = −0.582 pp（但两划分难度差 14.7 pp，混淆）')
emit('      本设计：C2/C3 层差仅 −0.122 pp ⇒ Δ 不再混入难度差，可作结论')
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
emit()
emit('已写 %s' % OUT)
