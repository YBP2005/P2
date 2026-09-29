# -*- coding: utf-8 -*-
"""在**单机 clean 批**上重算命题 6 的形状/噪声分解（口径与 work/prop6_shape_noise_20260920.py 完全一致），
并作为释放件 `release_shape-noise-by-budget.csv` 的**唯一生成器**。

**选取规则（同时写进释放件的 source_run 列与补充材料该表下的表注）**
- 机器：**只在 B 机一台**上跑（消除跨机混来源）；
- 批次：clean 批（`G3CLEAN_NOSTOP=1`，**早停关闭**）；
- 每个预算只用**跑满 epoch 1..E** 的 run（序列长度必须 == E，末轮 epoch == E）；
- 两臂 base / lr005，各 5 个种子（42–46）⇒ 每臂 n = 5（跑满的话），合并行按两臂等权。

口径（照 prop6）：
  premium_r = max_e V_r(e) − V_r(E)；m(e) = 均值曲线；shape(E) = max_e m(e) − m(E)；ν_r = premium_r − shape(E)
  arm 合并：premium 均 = 两臂均值再平均；shape 同；shape 占比 = shape / premium 均。
  `nu_mean_pp` = 该臂内 ν_r 的均值 = 该臂 premium 均 − shape(E)。

用法：
  python work/prop6_clean_b_20260925.py            # dry-run：重算 + 打印释放件全文，**不写盘**
  python work/prop6_clean_b_20260925.py --apply    # 写报告 .txt 与释放件 CSV（写前备份）

纯本地只读（CSV 已在 g3cleanb_20260925/），**不 ssh**。报告与释放件共用同一套取数/计算函数，
释放件里的每个数字都来自 `summarize()`/`combine()` 的返回值，**没有手抄**。
"""
import csv
import hashlib
import io
import os
import shutil
import sys

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
D = r'E:\workplace\g3cleanb_20260925'
OUT = r'E:\workplace\work\prop6_clean_b_20260925.txt'
REL = r'E:\workplace\实验内容共享\P2\02_论文释放件\release_shape-noise-by-budget.csv'
BAK = REL + '.bak_before_s11shape_20260925'
APPLY = '--apply' in sys.argv
COL = 'metrics/mAP50-95(B)'
TPL = {
    50: 'g3cleanb_e50_%s_s%dn__results.csv',
    100: 'g3clean_e100_%s_s%dn__results.csv',
    200: 'g3clean_e200_%s_s%dn__results.csv',
    400: 'g3cleanb_e400_%s_s%dn__results.csv',
}
ARMS = ('base', 'lr005')
SEEDS = range(42, 47)
RULE = ('single machine B; clean batch G3CLEAN_NOSTOP=1 (early stopping disabled); only runs that '
        'completed epochs 1..E; arms base+lr005 x seeds 42-46 => n=5 per arm')
SRC_RUN = D + ' | ' + RULE
HEADER = ['budget_epochs', 'arm', 'n', 'premium_mean_pp', 'shape_pp', 'shape_share_pct',
          'sd_nu_pp', 'nu_mean_pp', 'source_run']
# 两臂合并值（取自本脚本自己在单机 clean 批上的重算；此处作为**断言**，不是数字来源）
EXPECT_COMB = {
    50: (0.4439, 0.3161, 71.2, 0.1349, 0.1278),
    100: (0.6824, 0.6176, 90.5, 0.1604, 0.0648),
    200: (0.9712, 0.8517, 87.7, 0.1235, 0.1195),
    400: (1.2717, 1.1142, 87.6, 0.0836, 0.1575),
}
L = []


def emit(s=''):
    L.append(s)
    print(s)


def curve(p):
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8', errors='replace') as f:
        rows = list(csv.DictReader(f))
    v = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
         if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    v.sort()
    return v


def load_runs():
    """Return (runs, skipped): runs[(E, arm)] = [(seed, curve array)], one entry per FULL run."""
    runs, skipped = {}, []
    for E, tpl in TPL.items():
        for arm in ARMS:
            for sd in SEEDS:
                p = os.path.join(D, tpl % (arm, sd))
                v = curve(p)
                if not v:
                    skipped.append('%s（无 CSV）' % os.path.basename(p))
                    continue
                if v[-1][0] != E or len(v) != E:
                    skipped.append('%s（末轮 %d / 长度 %d，非跑满）'
                                   % (os.path.basename(p), v[-1][0], len(v)))
                    continue
                runs.setdefault((E, arm), []).append((sd, np.array([x for _, x in v])))
    return runs, skipped


def summarize(runs):
    """Per-arm decomposition: rows[(E, arm)] -> dict (premium mean, shape, sd(nu), n, mean(nu))."""
    rows = {}
    for (E, arm) in sorted(runs):
        V = np.vstack([v for _, v in sorted(runs[(E, arm)])])
        prem = V.max(axis=1) - V[:, -1]
        m = V.mean(axis=0)
        shape = m.max() - m[-1]
        nu = prem - shape
        rows[(E, arm)] = dict(prem=prem.mean(), shape=shape, sdnu=nu.std(ddof=1),
                              sdp=prem.std(ddof=1), n=len(V), V=V, numu=nu.mean())
    return rows


def combine(rows):
    """Two arms equal-weight: comb[E] = (premium, shape, sd(nu), mean(nu), n)."""
    comb = {}
    for E in sorted({k[0] for k in rows}):
        aa = [rows[(E, a)] for a in ARMS if (E, a) in rows]
        if not aa:
            continue
        p = float(np.mean([a['prem'] for a in aa]))
        s = float(np.mean([a['shape'] for a in aa]))
        sd = float(np.mean([a['sdnu'] for a in aa]))
        mu = float(np.mean([a['numu'] for a in aa]))
        nmin = min(a['n'] for a in aa)
        comb[E] = (p, s, sd, mu, nmin)
    return comb


def release_text(rows):
    """The release CSV's full text, built ONLY from summarize()'s output."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\r\n')     # the previous file used CRLF
    w.writerow(HEADER)
    data = []
    for (E, arm) in sorted(rows):
        r = rows[(E, arm)]
        prem, shape = r['prem'], r['shape']
        share = 100.0 * shape / prem if prem else 0.0
        row = [E, arm, r['n'], '%.4f' % prem, '%.4f' % shape, '%.1f' % share,
               '%.4f' % r['sdnu'], '%.4f' % r['numu'], SRC_RUN]
        data.append(row)
        w.writerow(row)
    return buf.getvalue(), data


def check_release(data, comb):
    """Every assertion the release file must satisfy, on the values actually written."""
    bad = []
    if len(data) != 8:
        bad.append('行数 %d != 8' % len(data))
    pairs = {(r[0], r[1]) for r in data}
    if pairs != {(E, a) for E in TPL for a in ARMS}:
        bad.append('臂-预算格子不是 4×2：%s' % sorted(map(str, pairs)))
    for r in data:
        E, arm, n, prem, shape, share = r[0], r[1], r[2], float(r[3]), float(r[4]), float(r[5])
        if n != 5:
            bad.append('E=%d %s: n=%d != 5' % (E, arm, n))
        if abs(share - 100.0 * shape / prem) > 0.05:
            bad.append('E=%d %s: 占比 %.1f vs 100*shape/premium %.4f'
                       % (E, arm, share, 100.0 * shape / prem))
        if abs(float(r[7]) - (prem - shape)) > 5e-5:
            bad.append('E=%d %s: nu_mean %.4f != premium-shape %.4f' % (E, arm, float(r[7]), prem - shape))
        if r[8] != SRC_RUN or 'n=5 per arm' not in r[8]:
            bad.append('E=%d %s: source_run 未写明单机 clean 批与 n' % (E, arm))
    # combined rows: the numbers that the supplementary table prints
    for E, (ep, es, esh, esd, emu) in sorted(EXPECT_COMB.items()):
        p, s, sd, mu, _n = comb[E]
        sh = 100.0 * s / p
        for got, want, what in ((p, ep, 'premium'), (s, es, 'shape'), (sd, esd, 'sd(nu)'),
                                (mu, emu, 'mean(nu)')):
            if abs(round(got, 4) - want) > 5e-5:
                bad.append('E=%d 合并 %s: %.4f != %.4f' % (E, what, got, want))
        if abs(round(sh, 1) - esh) > 0.05:
            bad.append('E=%d 合并占比: %.1f != %.1f' % (E, sh, esh))
    if abs(round(100.0 * comb[400][1] / comb[400][0], 1) - 87.6) > 0.1:
        bad.append('E=400 合并占比 != 87.6 (±0.1)')
    return bad


def main():
    emit('=' * 100)
    emit('命题 6 实测（**单机 clean 批**）：premium_r = shape(E) + ν_r')
    emit('选取规则：B 机单机 / clean 批(早停关闭) / 只用跑满 epoch 1..E 的 run / 两臂 base, lr005 / 种子 42–46')
    emit('=' * 100)
    emit(' %-5s %-6s %3s %12s %10s %11s %9s %11s' %
         ('E', 'arm', 'n', 'premium 均', 'shape', 'shape 占比', 'sd(ν)', 'sd(premium)'))

    runs, skipped = load_runs()
    for s in skipped:
        emit('  跳过：%s' % s)
    rows = summarize(runs)
    for (E, arm) in sorted(rows):
        r = rows[(E, arm)]
        emit(' %-5d %-6s %3d %+12.4f %10.4f %10.1f%% %9.4f %11.4f'
             % (E, arm, r['n'], r['prem'], r['shape'],
                100.0 * r['shape'] / r['prem'] if r['prem'] else 0, r['sdnu'], r['sdp']))

    emit('')
    emit('--- 两臂合并（先臂内均值，再两臂等权）---')
    emit(' %-5s %3s %13s %10s %10s %10s %11s' % ('E', 'n', 'premium 均', 'shape', 'shape 占比', 'sd(ν)', 'ν 均值'))
    comb = combine(rows)
    for E in sorted(comb):
        p, s, sd, mu, nmin = comb[E]
        emit(' %-5d %3d %+13.4f %10.4f %9.1f%% %10.4f %+11.4f'
             % (E, nmin, p, s, 100.0 * s / p if p else 0, sd, mu))

    emit('')
    emit('--- 判据 ---')
    Es = sorted(comb)
    if len(Es) >= 2:
        a, b = Es[0], Es[-1]
        emit('  E = %d → %d：shape ×%.3f，premium ×%.3f，sd(ν) ×%.3f；σ√(2 ln E) 型预测 ×%.3f'
             % (a, b, comb[b][1] / comb[a][1], comb[b][0] / comb[a][0],
                comb[b][2] / comb[a][2], np.sqrt(np.log(b) / np.log(a))))
        emit('  ① premium 的增幅 %.3f× vs shape 的增幅 %.3f×（比值 %.3f）'
             % (comb[b][0] / comb[a][0], comb[b][1] / comb[a][1],
                (comb[b][0] / comb[a][0]) / (comb[b][1] / comb[a][1])))
        emit('  ② ν 均值 %s 0 ⇒ %s' % ('≥' if comb[b][3] >= 0 else '<',
                                     '噪声项只占很小一块' if comb[b][3] >= 0 else '噪声项为负'))

    emit('')
    emit('--- 释放件（本脚本是它的唯一生成器）---')
    rel_txt, data = release_text(rows)
    checks = check_release(data, comb)
    for line in rel_txt.replace('\r\n', '\n').rstrip('\n').split('\n'):
        emit('  ' + line)
    emit('  断言：%s' % ('全部通过' if not checks else '**失败** %s' % checks))
    if checks:
        sys.exit('!! 释放件不满足断言，拒绝写盘：%s' % checks)

    n_rows = len(data)
    emit('  行数（不含表头）= %d；每臂 n = %s；E=400 合并占比 = %.1f %%'
         % (n_rows, sorted({r[2] for r in data}), 100.0 * comb[400][1] / comb[400][0]))

    if not APPLY:
        print()
        print('[dry-run] 未写盘。加 --apply 才写 %s 与 %s'
              % (os.path.basename(OUT), os.path.basename(REL)))
        return 0

    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('\n已写：%s' % OUT)
    if not os.path.exists(BAK):
        shutil.copy2(REL, BAK)
        print('  备份 %s' % os.path.basename(BAK))
    io.open(REL, 'w', encoding='utf-8', newline='').write(rel_txt)
    b = io.open(REL, 'rb').read()
    print('已写：%s（%d B，%d 行，md5 %s）'
          % (REL, len(b), b.count(b'\r\n'), hashlib.md5(b).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
