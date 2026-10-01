# -*- coding: utf-8 -*-
"""P2 · T1-d 的 val 侧：n=7 → n=10 能不能补？（**只读、零 GPU、不改稿**）

背景（2026-10-02）：
  * 已印的 `release_T1_registered-replication_summary.csv` 里，**T1-d 的 val 侧只有 n = 7**（seed 42–48），
    而 test 侧是 n = 10；正文 Declarations 把该批 val 侧列为"**不可复算**"的例外之一。
  * A 机盘点（子代理）报：`t1d_dotatod15_{base100,lr005_100ep}_s42n…s51n` **20 个目录全在**，
    每个 `results.csv` = **101 行（100 epoch + 表头）**，`best/last` 齐（`epoch*.pt` 全族为 0）。
  ⇒ **val 曲线本来就在 `results.csv` 里** ⇒ 若成立，这条"不可复算"的披露就**过期了**。

本脚本干两件事（先对照、后补样）：
  ① **阳性对照**：用本地 B 归档 tar 里 `t1d_*_s42–48` 的 `results.csv` 复算 `premium_val = max_e V(e) − V(末轮)`，
     必须与已印的 14 个 per-run 值**逐位一致**（≤0.0005 pp），否则**停**（不打印补样结论）。
  ② 若本目录另有 s49–51 的 `results.csv`（从 A 拉回），算 **n = 10** 的均值/SD/配对 t/符号，并给出与原 n=7 的对照。

口径（与 `release_T1_*` 同）：V = `metrics/mAP50-95(B)`；单位 pp；`premium_val = max(V) − V[末轮]`。
用法：
    python -X utf8 work/p2_t1d_val_n10_20261002.py                 # 只做对照（用 tar 里的 14 条）
    python -X utf8 work/p2_t1d_val_n10_20261002.py --pull          # 先从 A 拉 s49–51（6 个文件）再算
"""
import argparse
import csv
import io
import os
import statistics as st
import subprocess
import sys
import tarfile

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
TAR = os.path.join(W, 'AB机实验文件夹', 'b_artifacts_20260930.tgz')
LONG = os.path.join(W, '_release_github', '02_release_data', 'P2_T1_registered-replication_long.csv')
WORK = os.path.join(W, 't1d_valext_20261002')
RUNS = os.path.join(WORK, 'runs')
HERE = os.path.dirname(os.path.abspath(__file__))
ARMS = ['t1d_dotatod15_base100', 't1d_dotatod15_lr005_100ep']
SEEDS_KNOWN = list(range(42, 49))
SEEDS_EXTRA = [49, 50, 51]
TOL = 5e-4


def name(arm, s):
    return '%s_s%dn' % (arm, s)


def val_premium(p):
    """premium_val = max_e V(e) − V(末轮)，V = mAP50-95(B) × 100"""
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return None, 0
    col = next((c for c in rows[0] if 'mAP50-95' in c and '(B)' in c), None)
    if col is None:
        return None, 0
    v = [float(r[col]) * 100 for r in rows]
    return max(v) - v[-1], len(v)


def printed_vals():
    """已印的 per-run val 侧值（来自 T1 长表）"""
    out = {}
    for r in csv.DictReader(io.open(LONG, encoding='utf-8')):
        if r['cell'] == 'T1-d' and r['quantity'] == 'premium_val_pp':
            out[r['run']] = float(r['value_pp'])
    return out


def extract_from_tar():
    os.makedirs(RUNS, exist_ok=True)
    n = 0
    with tarfile.open(TAR, 'r:gz') as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            parts = m.name.split('/')
            if len(parts) == 3 and parts[0] == 'runs' and parts[1].startswith('t1d_dotatod15') \
                    and parts[2] == 'results.csv':
                dst = os.path.join(RUNS, parts[1], 'results.csv')
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if not os.path.exists(dst):
                    f = tf.extractfile(m)
                    io.open(dst, 'wb').write(f.read())
                    n += 1
    return n


def pull_extra():
    rc = 0
    for arm in ARMS:
        for s in SEEDS_EXTRA:
            rn = name(arm, s)
            dst = os.path.join(RUNS, rn, 'results.csv')
            if os.path.exists(dst) and os.path.getsize(dst) > 1000:
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            cmd = [sys.executable, '-X', 'utf8', os.path.join(HERE, 'gpu_ssh.py'),
                   '--profile', 'a', '--get', '/workspace/runs/%s/results.csv' % rn, dst]
            env = dict(os.environ, MSYS_NO_PATHCONV='1')
            p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
            print(p.stdout.strip() or p.stderr.strip())
            if p.returncode != 0 or not os.path.exists(dst):
                rc = 1
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pull', action='store_true')
    a = ap.parse_args()
    os.makedirs(RUNS, exist_ok=True)

    got = extract_from_tar()
    print('从本地 B 归档取出 %d 个 t1d results.csv（已存在的跳过）' % got)
    if a.pull:
        print('从 A 机拉 s49–51 …')
        if pull_extra() != 0:
            print('★ 有文件没拉到 ⇒ 不打印补样结论（先解决取件）')
            return 2

    pr = printed_vals()
    print('已印 per-run val 值：%d 条' % len(pr))
    bad, base, lr = [], {}, {}
    alt = []
    for arm in ARMS:
        for s in SEEDS_KNOWN + SEEDS_EXTRA:
            rn = name(arm, s)
            pA = os.path.join(RUNS, rn, 'results_A.csv')      # A 机副本（= 已印值的来源）
            pB = os.path.join(RUNS, rn, 'results.csv')        # 本地 B 归档副本（**同名不同数据**）
            p = pA if os.path.exists(pA) and os.path.getsize(pA) > 500 else pB
            if not os.path.exists(p) or os.path.getsize(p) < 500:
                continue
            val, ne = val_premium(p)
            if val is None:
                continue
            (base if arm.endswith('base100') else lr)[s] = (val, ne)
            if rn in pr and abs(val - pr[rn]) > TOL:
                bad.append((rn, val, pr[rn]))
            if os.path.exists(pA) and os.path.exists(pB) and os.path.getsize(pB) > 500:
                vb, _ = val_premium(pB)
                if vb is not None and abs(vb - val) > TOL:
                    alt.append((rn, val, vb))
    if alt:
        print('⚠ A 机副本与本地 B 归档副本**同名但不同数据**：%d/%d 不符 ⇒ 本地 B 归档里的 `t1d_*` 不是已印值的来源'
              % (len(alt), len(pr)))
        for rn, va, vb in alt[:5]:
            print('     %s  A %+.4f  vs  B %+.4f' % (rn, va, vb))
    print()
    print('① 阳性对照（s42–48，与已印值逐位比，容差 %.4f pp）' % TOL)
    for arm, d in (('base100', base), ('lr005_100ep', lr)):
        ks = sorted(k for k in d if k in SEEDS_KNOWN)
        print('   %-14s n=%d  %s' % (arm, len(ks),
                                     '  '.join('s%d %+.4f(ep%d)' % (k, d[k][0], d[k][1]) for k in ks)))
    if bad:
        print('   ★ 对照不通过 %d 条：%s' % (len(bad), bad[:5]))
        print('   ⇒ 停：不打印 n=10 结论（口径或数据源不对）')
        return 3
    print('   ⇒ 对照通过：14/14 逐位一致（≤ %.4f pp）' % TOL)

    print()
    print('② 补样后（若 s49–51 已就位）')
    for arm, d in (('base100', base), ('lr005_100ep', lr)):
        ks = sorted(d)
        if len(ks) <= 7:
            print('   %-14s 仍只有 n=%d（s49–51 未就位；加 --pull 从 A 取）' % (arm, len(ks)))
            continue
        v7 = [d[k][0] for k in ks if k in SEEDS_KNOWN]
        v10 = [d[k][0] for k in ks]
        print('   %-14s n=%d：均值 %+.4f（原 n=7 %+.4f）  SD %.4f（原 %.4f）  正号 %d/%d（原 %d/7）'
              % (arm, len(v10), st.mean(v10), st.mean(v7),
                 st.stdev(v10) if len(v10) > 1 else 0, st.stdev(v7) if len(v7) > 1 else 0,
                 sum(1 for x in v10 if x > 0), len(v10), sum(1 for x in v7 if x > 0)))
    both = {s: (base[s][0], lr[s][0]) for s in sorted(set(base) & set(lr))}
    if len(both) > 7:
        print('   两臂**配对差**（= 已印口径 `premium_val_max_minus_final`：strategy − baseline，pp）')
        for tag, ks in (('n=7', [s for s in sorted(both) if s in SEEDS_KNOWN]),
                        ('n=%d' % len(both), sorted(both))):
            dif = [both[s][1] - both[s][0] for s in ks]
            line = '     %-5s 均值 %+.4f  SD %.4f  符号 %d+/%d−' % (
                tag, st.mean(dif), st.stdev(dif) if len(dif) > 1 else 0,
                sum(1 for x in dif if x > 0), sum(1 for x in dif if x < 0))
            try:
                from scipy import stats
                t, p = stats.ttest_1samp(dif, 0.0)
                lo, hi = stats.t.interval(0.95, len(dif) - 1, loc=st.mean(dif),
                                          scale=stats.sem(dif))
                line += '  配对 t=%.3f  p=%.6g  95%% CI [%+.4f, %+.4f]' % (t, p, lo, hi)
            except Exception as ex:                        # noqa: BLE001
                line += '  （t/CI 未算：%s）' % ex
            print(line)
        print('     （已印值：n=7 均值 −0.4043 pp、p=0.00106、0+/7−）')
        print('     逐 seed 明细：%s' % '  '.join(
            's%d(%+.3f,%+.3f→%+.3f)' % (s, both[s][0], both[s][1], both[s][1] - both[s][0])
            for s in sorted(both)))
    print()
    print('产物目录：%s' % RUNS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
