# -*- coding: utf-8 -*-
"""verify_two_critiques_20260916.py — 核对两条最锐利的审稿意见。

背景：6 模型咨询中，两条批评决定头条结论能否按现措辞写：
  (I) deepseek-flash：SHWD 格的"溢价差" 0.526 pp ≈ 该格数据顺序 SD 0.515 pp（同量级）
      → 但臂间比较是同种子配对，相关量是配对差的 SD。本脚本算它 + CI。
  (II) gpt-5.6-sol：`best-val − final-val` 由构造天然非负，不等于"对未见数据的乐观偏差"。
      正确估计量是 M_val(ê) − M_test(ê)（ê = argmax val）。三分划 run 里 val/test 分离，可算。

数据（均已交叉核对）：
  * results.csv        逐 epoch，metrics/mAP50-95(B) 是 **carved val**（三分划）或 val（val==test 时）
  * sio_b_results.csv  无表头；列 = [run, tag, epoch, mAP50, mAP50-95, P, R]；值是**被选中 checkpoint** 的指标；
                       对三分划 run 是 **test split**，对 val==test run 是 val
新文件；不改动 analysis/ 下任何既有文件。输出 analysis/eval_validity/verify_two_critiques_20260916.txt
"""
import csv, io, os, re, sys
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

ROOTS = [r'D:\deepseek\4090Bruns\runs',
         r'D:\deepseek\analysis\A_results_20260914\runs',
         r'D:\deepseek\analysis\B_results_20260914\runs',
         r'D:\deepseek\analysis\A_results_20260915\workspace\runs',
         r'D:\deepseek\analysis\B_results_20260915\workspace\runs']
SIO = {'A': r'D:\deepseek\analysis\A_results_20260915\workspace\sio_b_results.csv',
       'B': r'D:\deepseek\analysis\B_results_20260915\workspace\sio_b_results.csv'}
OUT = r'D:\deepseek\analysis\eval_validity\verify_two_critiques_20260916.txt'

CELLS = {
    'smoke2sf (strong)':      ('smoke2sf_base100',  'smoke2sf_lr005_100ep'),
    'shwd2sf (corroborating)': ('shwd2sf_base100',  'shwd2sf_lr005_100ep'),
    'a2d15 (directional probe)': ('a2d15_base100',  'a2d15_lr005_100ep'),
    'dota15 within-domain':   ('dota15_base100',    'dota15_lr005_100ep'),
}

buf = []
def emit(s=''):
    print(s)
    buf.append(s)


# ---------- 载入 ----------
def index_runs():
    out = {}
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for n in os.listdir(root):
            p = os.path.join(root, n, 'results.csv')
            if os.path.exists(p):
                out[n] = p
    return out


def val_series(path):
    rows = list(csv.DictReader(io.open(path, encoding='utf-8', errors='ignore')))
    col = 'metrics/mAP50-95(B)'
    return np.array([float(r[col]) for r in rows if r.get(col)])


def load_sio():
    d = {}
    for arch, p in SIO.items():
        if not os.path.exists(p):
            continue
        for line in io.open(p, encoding='utf-8', errors='ignore'):
            f = [x.strip() for x in line.rstrip('\n').split(',')]
            if len(f) < 7:
                continue
            try:
                m50, m95, pr, rc = (float(f[3]), float(f[4]), float(f[5]), float(f[6]))
            except ValueError:
                continue
            d.setdefault(f[0], {})[arch] = dict(m50=m50, m95=m95, p=pr, r=rc)
    return d


def match(runs, pref):
    """返回 seed -> results.csv 路径。runs 是 name -> 路径。"""
    pat = re.compile(re.escape(pref) + r'(?:_s(\d+)n)?$')
    out = {}
    for name, path in runs.items():
        m = pat.match(name)
        if m:
            out[int(m.group(1)) if m.group(1) else 'unseeded'] = path
    return out


def ci95(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return np.nan, np.nan, np.nan, np.nan, np.nan
    m, sd = x.mean(), x.std(ddof=1)
    se = sd / np.sqrt(n)
    t, p = stats.ttest_rel(x, np.zeros(n))          # H0: 配对差 = 0
    tc = stats.t.ppf(0.975, n - 1)
    return m, sd, t, p, (m - tc * se, m + tc * se)


runs = index_runs()
sio = load_sio()
emit('=' * 80)
emit('核对两条审稿意见')
emit('=' * 80)
emit(f'local runs with results.csv: {len(runs)}    sio entries: {len(sio)}')
emit()

# ================= (I) 溢价差的配对检验 =================
emit('#' * 80)
emit('# (I) deepseek-flash："溢价差 ≈ 噪声量级"是否成立')
emit('#' * 80)
emit('溢价(seed) = best-epoch − final-epoch（同一 run 内，mAP50-95，pp）')
emit('检验的是【配对差】d(seed) = 溢价_base(seed) − 溢价_strat(seed)，n = 配对种子数')
emit()
partA = {}
for cell, (bp, sp) in CELLS.items():
    base, strat = match(runs, bp), match(runs, sp)
    seeds = sorted(set(base) & set(strat), key=lambda s: (isinstance(s, str), s))
    emit(f'--- {cell}:  配对种子 {len(seeds)}   {seeds}')
    if len(seeds) < 2:
        emit('    不足以做配对检验'); emit(); continue
    pb, ps = [], []
    for s in seeds:
        sb, ss = val_series(base[s]), val_series(strat[s])
        pb.append((sb.max() - sb[-1]) * 100)
        ps.append((ss.max() - ss[-1]) * 100)
    pb, ps = np.array(pb), np.array(ps)
    d = pb - ps
    emit(f'    溢价_base 均值 {pb.mean():+.3f} pp (sd {pb.std(ddof=1):.3f})，'
         f'溢价_strat 均值 {ps.mean():+.3f} pp (sd {ps.std(ddof=1):.3f})')
    emit(f'    未配对差     {pb.mean()-ps.mean():+.3f} pp   <-- 此前正文只报了这个')
    m, sd, t, p, ci = ci95(d)
    emit(f'    【配对差】   {m:+.3f} pp  sd {sd:.3f}  paired t {t:.2f}  p {p:.4g}  '
         f'95%CI [{ci[0]:+.3f}, {ci[1]:+.3f}]')
    # 同一格的数据顺序 SD（即"噪声量级"的参照）
    sb_all = np.concatenate([val_series(base[s]) for s in seeds])
    emit(f'    对照：本格跨种子的 best-epoch 端点 SD '
         f'{np.std([val_series(base[s]).max()*100 for s in seeds], ddof=1):.3f} pp（基线臂）')
    partA[cell] = (len(seeds), m, sd, t, p, ci)
    emit()

# ================= (II) M_val(ê) − M_test(ê) =================
emit('#' * 80)
emit('# (II) gpt："正确的是 M_val(ê) − M_test(ê)"——用三分划 run 直接算')
emit('#' * 80)
emit('M_val(ê) = results.csv 里 carved-val 的逐 epoch 最大值（即选点依据）')
emit('M_test(ê) = sio_b_results.csv 的 mAP50-95（test split，被选中 checkpoint 上评估）')
emit()

r3 = {}
for root in ROOTS:
    if not os.path.isdir(root):
        continue
    arch = 'A' if 'A_results' in root else ('B' if 'B_results' in root else '?')
    for n in os.listdir(root):
        if '3way' in n and 'OOMKILLED' not in n and 'PARTIAL' not in n:
            r3[n] = (os.path.join(root, n, 'results.csv'), arch)

emit(f'三分划 run（可用）: {len(r3)}')
rows = []
for n, (p, arch) in sorted(r3.items()):
    if not os.path.exists(p):
        continue
    s = val_series(p)
    if len(s) < 2:
        continue
    e = int(np.argmax(s))
    mv = s[e] * 100
    ent = sio.get(n)
    if not ent:
        rows.append((n, arch, mv, None, None, e + 1))
        continue
    rec = ent.get(arch) or list(ent.values())[0]
    mt = rec['m95'] * 100
    rows.append((n, arch, mv, mt, mv - mt, e + 1))

got = [r for r in rows if r[3] is not None]
miss = [r for r in rows if r[3] is None]
emit(f'  能配上 test 的 {len(got)} 个；配不上的 {len(miss)} 个' + (f'（例：{[m[0] for m in miss[:3]]}）' if miss else ''))
emit()

def cell_of(name):
    x = name.replace('r10_', '')
    x = re.sub(r'_3way_s\d+n$', '', x)
    x = re.sub(r'_s\d+n$', '', x)
    arm = 'strat' if ('lr005' in x or 'lr005' in name) else 'base'
    x = x.replace('_lr005_100ep', '').replace('_lr005_30ep', '').replace('_base100', '').replace('_base30', '')
    return x, arm

groups = {}
for n, arch, mv, mt, gap, e in got:
    k = cell_of(n)
    groups.setdefault(k, []).append((n, mv, mt, gap, e, arch))

emit('--- 逐格：M_val(ê) 与 M_test(ê)（pp）')
emit(f'{"cell":28} {"arm":6} {"n":>3} {"M_val(ê)":>9} {"M_test(ê)":>10} {"gap":>8} {"gap SD":>7}')
pairdata = {}
for k in sorted(groups):
    vals = groups[k]
    mv = np.array([v[1] for v in vals]); mt = np.array([v[2] for v in vals]); gp = np.array([v[3] for v in vals])
    emit(f'{k[0][:28]:28} {k[1]:6} {len(vals):>3} {mv.mean():>9.3f} {mt.mean():>10.3f} '
         f'{gp.mean():>+8.3f} {(gp.std(ddof=1) if len(gp)>1 else float("nan")):>7.3f}')
    pairdata[k] = {v[0]: v[3] for v in vals}
emit()

emit('--- 配对：同格同种子的 gap 在两臂间的差（正 = 基线臂 gap 更大）')
emit(f'{"cell":28} {"n":>3} {"Δgap":>8} {"sd":>7} {"t":>7} {"p":>9}   95%CI')
for cell in sorted(set(k[0] for k in pairdata)):
    b = {n: g for (c, a), d in pairdata.items() if c == cell and a == 'base' for n, g in d.items()}
    s = {n: g for (c, a), d in pairdata.items() if c == cell and a == 'strat' for n, g in d.items()}
    keys = [k for k in b if k in s]
    # 按种子配对
    def seed(n):
        m = re.search(r'_s(\d+)n$', n)
        return int(m.group(1)) if m else None
    bs = {seed(k): v for k, v in b.items() if seed(k)}
    ss = {seed(k): v for k, v in s.items() if seed(k)}
    common = sorted(set(bs) & set(ss))
    if len(common) < 2:
        continue
    d = np.array([bs[x] - ss[x] for x in common])
    m, sd, t, p, ci = ci95(d)
    emit(f'{cell[:28]:28} {len(common):>3} {m:>+8.3f} {sd:>7.3f} {t:>7.2f} {p:>9.4g}   '
         f'[{ci[0]:+.3f}, {ci[1]:+.3f}]')
emit()

# ================= 汇总判断 =================
emit('#' * 80)
emit('# 结论汇总（脚本判读，供人工复核）')
emit('#' * 80)
emit()
emit('(I) 溢价差的配对检验：')
for cell, (n, m, sd, t, p, ci) in partA.items():
    verdict = '不显著（CI 含 0）' if (ci[0] < 0 < ci[1]) else '显著（CI 不含 0）'
    emit(f'   {cell[:34]:34} 配对差 {m:+.3f} pp  n={n}  CI [{ci[0]:+.3f}, {ci[1]:+.3f}]  -> {verdict}')
emit()
emit('(II) M_val(ê) − M_test(ê)：上面逐格表；注意该 gap 同时含【两集难度差】与【选择乐观】两个分量，')
emit('     仅凭它不能把两者分开——要分开需要非选中 epoch 上的 test 指标，归档里没有逐 epoch test。')
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(buf) + '\n')
print(f'\nwrote {OUT}')
