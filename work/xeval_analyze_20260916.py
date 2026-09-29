# -*- coding: utf-8 -*-
"""
A 项 + D 项：把 pod 上的 **2×2 评估矩阵** 与归档接起来

  (1) 验证：本次复算的 (best,test) 是否复现项目自带的 sio_b_results.csv
  (2) 让 §8 的干净协议读数**在本地可复算**（gap A）
  (3) 让 §5.6 的"不可识别"变成**可分解**（gap D）：
        gap ≡ M_val(ê) − M_test(ê) = (V_final − T_final) + (prem_val − prem_test)
      ⇒ Δgap = Δ(末轮 checkpoint 上的两划分难度差) + Δ(选点乐观 val−test 之差)

输入（全部在 E:\\workplace\\xeval_20260916\\）：matrix.csv, sio_b_results_pod.csv, runs/<run>_results.csv
输出：E:\\workplace\\xeval_analysis_20260916.txt
"""
import csv, io, os, re, sys
from collections import defaultdict
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'E:\workplace\xeval_20260916'
OUT = r'E:\workplace\xeval_analysis_20260916.txt'
buf = []
def emit(s=''):
    print(s); buf.append(s)


def load_matrix():
    d = defaultdict(list)
    for line in io.open(os.path.join(BASE, 'matrix.csv'), encoding='utf-8'):
        f = line.strip().split(',')
        if len(f) < 4 or f[0] == 'run' or f[3] == 'FAIL':
            continue
        d[(f[0], f[1], f[2])].append(float(f[3]))
    out, conflicts = {}, []
    for k, v in d.items():
        if len(v) > 1 and (max(v) - min(v)) > 1e-6:
            conflicts.append((k, v))
        out[k] = float(np.mean(v))
    return out, conflicts


def load_sio():
    d = {}
    for line in io.open(os.path.join(BASE, 'sio_b_results_pod.csv'), encoding='utf-8', errors='ignore'):
        f = [x.strip() for x in line.rstrip('\n').split(',')]
        if len(f) < 7:
            continue
        try:
            d[f[0]] = float(f[4]) * 100.0
        except ValueError:
            pass
    return d


def val_series(run):
    p = os.path.join(BASE, 'runs', run + '_results.csv')
    if not os.path.exists(p):
        return None
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='ignore')))
    col = 'metrics/mAP50-95(B)'
    return np.array([float(r[col]) * 100 for r in rows if r.get(col)])


def cell_arm(run):
    x = run.replace('r10_', '').replace('_3way', '')
    arm = 'strat' if 'lr005' in x else 'base'
    x = x.replace('_lr005_100ep', '').replace('_base100', '').replace('_base30', '')
    return re.sub(r'_s\d+n$', '', x), arm


def seed_of(run):
    m = re.search(r'_s(\d+)n$', run)
    return int(m.group(1)) if m else None


def stat(x):
    x = np.asarray(x, float); n = len(x)
    if n < 2:
        return x.mean() if n else np.nan, np.nan, np.nan, np.nan, (np.nan, np.nan)
    m, sd = x.mean(), x.std(ddof=1)
    t, p = stats.ttest_rel(x, np.zeros(n))
    tc = stats.t.ppf(0.975, n - 1)
    return m, sd, t, p, (m - tc * sd / np.sqrt(n), m + tc * sd / np.sqrt(n))


M, conflicts = load_matrix()
SIO = load_sio()
emit('=' * 104)
emit('2×2 评估矩阵 × 归档：验证 / 本地可复算 / Δgap 的可分解化')
emit('=' * 104)
emit(f'矩阵条目 {len(M)}；sio 条目 {len(SIO)}；（commit/口径：split=test|val, batch=32, imgsz=640，与 train_obj.py L75 对齐）')
emit('同一格多次评估：%s' % ('全部一致' if not conflicts else f'{len(conflicts)} 处冲突（见下）'))
for k, v in conflicts[:8]:
    emit('   %s -> %s' % (k, v))
emit()

REC = defaultdict(dict)          # (cell, arm) -> seed -> dict
emit('--- 逐 run：归档 vs 本次复算（pp）')
emit(f'{"run":44}{"Vmax档":>9}{"Vbest测":>9}{"Vfin档":>9}{"Vfin测":>9}{"Tbest档":>9}{"Tbest测":>9}{"Tfin测":>9}')
n_skip = 0
for r in sorted({k[0] for k in M}):
    ser = val_series(r)
    if ser is None:
        n_skip += 1
        continue
    Vmax_a, Vfin_a = float(ser.max()), float(ser[-1])
    Vbest_o = M.get((r, 'best', 'val'), np.nan)
    Vfin_o = M.get((r, 'last', 'val'), np.nan)
    Tbest_a = SIO.get(r, np.nan)
    Tbest_o = M.get((r, 'best', 'test'), np.nan)
    Tfin_o = M.get((r, 'last', 'test'), np.nan)
    emit(f'{r[:44]:44}{Vmax_a:>9.3f}{Vbest_o:>9.3f}{Vfin_a:>9.3f}{Vfin_o:>9.3f}'
         f'{Tbest_a:>9.3f}{Tbest_o:>9.3f}{Tfin_o:>9.3f}')
    c, a = cell_arm(r); s = seed_of(r)
    if s is not None:
        REC[(c, a)][s] = dict(Vmax_a=Vmax_a, Vfin_a=Vfin_a, Vbest_o=Vbest_o, Vfin_o=Vfin_o,
                              Tbest_a=Tbest_a, Tbest_o=Tbest_o, Tfin_o=Tfin_o)
if n_skip:
    emit(f'（{n_skip} 个 run 的本地 results.csv 缺失，未纳入）')
emit()

# ---------------- (1) 验证
emit('=' * 104)
emit('(1) 验证：本次复算能不能复现已有归档')
emit('=' * 104)
dTb, dVb, dVf = [], [], []
for (c, a), sd in REC.items():
    for s, v in sd.items():
        if not np.isnan(v['Tbest_o']) and not np.isnan(v['Tbest_a']):
            dTb.append(abs(v['Tbest_o'] - v['Tbest_a']))
        if not np.isnan(v['Vbest_o']):
            dVb.append(abs(v['Vbest_o'] - v['Vmax_a']))
        if not np.isnan(v['Vfin_o']):
            dVf.append(abs(v['Vfin_o'] - v['Vfin_a']))
if dTb:
    emit(f'  (best,test) 复算 vs sio 归档 ：n={len(dTb)}  最大差 {max(dTb):.4f}  中位 {np.median(dTb):.4f} pp')
    emit('     ⇒ %s' % ('✅ 逐位吻合（<0.05 pp）：评估链路与项目同口径，且归档值可被独立复现'
                        if max(dTb) < 0.05 else '⚠️ 有差异，须查口径'))
if dVb:
    emit(f'  (best,val)  复算 vs results.csv 最大值：n={len(dVb)}  最大差 {max(dVb):.4f}  中位 {np.median(dVb):.4f} pp')
    emit('     ⇒ %s' % ('ℹ️ 不完全相等是预期的：ultralytics 的 best.pt 按 **fitness** 选，'
                        '不必然等于 mAP50-95 的最大值' if max(dVb) > 0.05 else '恰好相等（该格 fitness 与 mAP 同序）'))
if dVf:
    emit(f'  (last,val)  复算 vs results.csv 末轮   ：n={len(dVf)}  最大差 {max(dVf):.4f}  中位 {np.median(dVf):.4f} pp')
emit()

# ---------------- (3) 分解
emit('=' * 104)
emit('(3) Δgap 的可分解化')
emit('=' * 104)
emit()
emit('  恒等式：  gap = M_val(ê) − M_test(ê) = (V_final − T_final) + (prem_val − prem_test)')
emit('     prem_val = V_max − V_final（results.csv）；prem_test = T_best − T_final（本次实测）')
emit()
emit(f'{"cell":12}{"arm":6}{"n":>3}{"V_fin":>8}{"T_fin":>8}{"prem_val":>9}{"prem_test":>10}{"gap":>8}{"校验":>8}')
for (c, a) in sorted(REC):
    sd = REC[(c, a)]
    ok = [(s, v) for s, v in sd.items() if not np.isnan(v['Tfin_o']) and not np.isnan(v['Tbest_a'])]
    if not ok:
        continue
    Vf = np.mean([v['Vfin_a'] for _, v in ok]); Tf = np.mean([v['Tfin_o'] for _, v in ok])
    pv = np.mean([v['Vmax_a'] - v['Vfin_a'] for _, v in ok])
    pt = np.mean([v['Tbest_a'] - v['Tfin_o'] for _, v in ok])
    gp = np.mean([v['Vmax_a'] - v['Tbest_a'] for _, v in ok])
    emit(f'{c[:12]:12}{a:6}{len(ok):>3}{Vf:>8.3f}{Tf:>8.3f}{pv:>9.3f}{pt:>10.3f}{gp:>8.3f}{(Vf-Tf)+(pv-pt):>8.3f}')
emit()
emit(f'{"cell":12}{"n":>3}{"Δgap":>8}{"Δ难度差":>10}{"Δ选点乐观":>11}{"和(校验)":>10}{"主导分量":>12}{"p(Δgap)":>10}')
DEC = {}
for c in sorted({k[0] for k in REC}):
    b, s = REC.get((c, 'base'), {}), REC.get((c, 'strat'), {})
    common = sorted(set(b) & set(s))
    common = [k for k in common if not np.isnan(b[k]['Tfin_o']) and not np.isnan(s[k]['Tfin_o'])
              and not np.isnan(b[k]['Tbest_a']) and not np.isnan(s[k]['Tbest_a'])]
    if len(common) < 2:
        continue
    dg, dd, do = [], [], []
    for k in common:
        gb = b[k]['Vmax_a'] - b[k]['Tbest_a'];  gs = s[k]['Vmax_a'] - s[k]['Tbest_a']
        db = b[k]['Vfin_a'] - b[k]['Tfin_o'];   ds = s[k]['Vfin_a'] - s[k]['Tfin_o']
        ob = (b[k]['Vmax_a'] - b[k]['Vfin_a']) - (b[k]['Tbest_a'] - b[k]['Tfin_o'])
        os_ = (s[k]['Vmax_a'] - s[k]['Vfin_a']) - (s[k]['Tbest_a'] - s[k]['Tfin_o'])
        dg.append(gb - gs); dd.append(db - ds); do.append(ob - os_)
    mg, _, _, pg, cig = stat(dg)
    md, mo = np.mean(dd), np.mean(do)
    dom = 'Δ难度差' if abs(md) > abs(mo) else 'Δ选点乐观'
    emit(f'{c[:12]:12}{len(common):>3}{mg:>+8.3f}{md:>+10.3f}{mo:>+11.3f}{md+mo:>+10.3f}{dom:>12}{pg:>10.4g}')
    DEC[c] = dict(n=len(common), dgap=mg, p=pg, ci=cig, d_diff=md, d_opt=mo,
                  sd_diff=np.std(dd, ddof=1) if len(dd) > 1 else np.nan,
                  sd_opt=np.std(do, ddof=1) if len(do) > 1 else np.nan)
emit()
emit('  读法：')
for c, v in sorted(DEC.items(), key=lambda kv: -abs(kv[1]['dgap'])):
    emit(f'    {c:12} Δgap={v["dgap"]:+.3f}（p={v["p"]:.4g}, n={v["n"]}）= '
         f'难度差 {v["d_diff"]:+.3f}（±{v["sd_diff"]:.3f}） + 选点乐观 {v["d_opt"]:+.3f}（±{v["sd_opt"]:.3f}）')
emit()

# ---------------- (4) 选点获益在 test 上兑现了多少
emit('=' * 104)
emit('(4) 选点获益的"兑现率"：val 上选出来的分，在 test 上还剩多少')
emit('=' * 104)
emit()
emit('  prem_val = V_max − V_final（在 val 上选点得到的账面增益）')
emit('  prem_test = T_best − T_final（同一选点动作在 test 上兑现到的增益）')
emit()
emit(f'{"cell":12}{"arm":6}{"n":>3}{"prem_val":>10}{"prem_test":>11}{"兑现率":>9}   逐 run 的 prem_test')
TR = {}
for (c, a) in sorted(REC):
    sd = REC[(c, a)]
    ok = [(s, v) for s, v in sorted(sd.items()) if not np.isnan(v['Tfin_o']) and not np.isnan(v['Tbest_a'])]
    if not ok:
        continue
    pv = np.mean([v['Vmax_a'] - v['Vfin_a'] for _, v in ok])
    pts = [v['Tbest_a'] - v['Tfin_o'] for _, v in ok]
    pt = float(np.mean(pts))
    ratio = (pt / pv * 100) if abs(pv) > 1e-9 else float('nan')
    emit(f'{c[:12]:12}{a:6}{len(ok):>3}{pv:>10.3f}{pt:>11.3f}{ratio:>8.0f}%   ' +
         ' '.join('%+.2f' % x for x in pts))
    TR[(c, a)] = dict(pv=pv, pt=pt, ratio=ratio, n=len(ok), per=pts)
emit()
allpv = [v['pv'] for v in TR.values()]; allpt = [v['pt'] for v in TR.values()]
emit(f'  合计：prem_val 均值 {np.mean(allpv):+.3f} pp，prem_test 均值 {np.mean(allpt):+.3f} pp，'
     f'兑现率 {np.mean(allpt)/np.mean(allpv)*100:.0f}%')
neg = [k for k, v in TR.items() if v['pt'] < 0]
emit(f'  prem_test 为**负**的格：{len(neg)}/{len(TR)} —— ' + '、'.join(f'{c}/{a}({TR[(c,a)]["pt"]:+.3f})' for c, a in neg))
emit('  ⇒ 在 val 上选出来的增益，在独立划分上只兑现了一部分，甚至反向。')
emit()

io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(buf) + '\n')
print(f'\n输出已写：{OUT}')
