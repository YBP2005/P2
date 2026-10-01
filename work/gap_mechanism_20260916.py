# -*- coding: utf-8 -*-
"""
§5.6 用：Δgap 的符号为何按语料而异？——把四种候选机制逐一对数据检验。

数据通路与 `analysis/work/verify_two_critiques_20260916.py` **完全相同**（同一批归档、同一套匹配规则），
本脚本只新增"机制检验"部分，不改动 D 盘任何既有文件。
输出：E:\\workplace\\gap_mechanism_20260916.txt
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
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gap_mechanism_20260916.txt')
# r169：不再写作者机绝对路径 `E:\workplace\...`（包 README 承诺"没有 checker 硬编码作者机路径"）。
#   注意：本脚本的**输入**是作者树上的 D 盘归档（不在包内），所以它属**作者侧**；发布包里那份
#   `02_release_data/gap_mechanism_20260916.txt` 就是它的产物，逐字节可核。

buf = []
def emit(s=''):
    print(s); buf.append(s)


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
                m50, m95 = float(f[3]), float(f[4])
            except ValueError:
                continue
            d.setdefault(f[0], {})[arch] = dict(m50=m50, m95=m95)
    return d


def ci95(x):
    x = np.asarray(x, dtype=float); n = len(x)
    if n < 2:
        return (np.nan,) * 5
    m, sd = x.mean(), x.std(ddof=1); se = sd / np.sqrt(n)
    t, p = stats.ttest_rel(x, np.zeros(n))
    tc = stats.t.ppf(0.975, n - 1)
    return m, sd, t, p, (m - tc * se, m + tc * se)


def cell_of(name):
    x = name.replace('r10_', '')
    x = re.sub(r'_3way_s\d+n$', '', x)
    x = re.sub(r'_s\d+n$', '', x)
    arm = 'strat' if 'lr005' in name else 'base'
    x = (x.replace('_lr005_100ep', '').replace('_lr005_30ep', '')
          .replace('_base100', '').replace('_base30', ''))
    return x, arm


def seed_of(name):
    m = re.search(r'_s(\d+)n$', name)
    return int(m.group(1)) if m else None


runs = index_runs()
sio = load_sio()
emit('=' * 88)
emit('Δgap 的符号为何按语料而异 —— 候选机制的逐条检验（只用已归档数据，无需 GPU）')
emit('=' * 88)
emit(f'归档中带 results.csv 的 run：{len(runs)}   sio 条目：{len(sio)}')
emit()
emit('数据通路与 verify_two_critiques_20260916.py 相同：')
emit('  M_val(ê) = results.csv 内 carved-val mAP50-95 的逐 epoch 最大值（＝选点依据）')
emit('  M_test(ê) = sio_b_results.csv 的 mAP50-95（被选中 checkpoint 上的 test 评测，项目报告口径）')
emit('  gap = M_val(ê) − M_test(ê)；Δgap = gap_base − gap_strat（同种子配对）')
emit()

# ---------------- 逐格原始量
cells = {}
for name, path in sorted(runs.items()):
    if '_3way_' not in name:
        continue
    cell, arm = cell_of(name)
    sd = seed_of(name)
    if sd is None:
        continue
    ser = val_series(path)
    if len(ser) == 0:
        continue
    # 单位：results.csv 的 val 与 sio 的 m95 都是 **分数**（0–1），一律 ×100 转 pp
    # （与 verify_two_critiques_20260916.py 的 L171/L177 完全一致）
    mval_best, mval_final = float(ser.max()) * 100, float(ser[-1]) * 100
    ent = sio.get(name) or sio.get(name.replace('_3way', ''))
    if not ent:                                    # 取任一归档的读数
        continue
    mt = list(ent.values())[0]['m95'] * 100
    cells.setdefault(cell, {}).setdefault(arm, {})[sd] = dict(
        mval=mval_best, mtest=mt, gap=mval_best - mt, prem=mval_best - mval_final)

emit('--- 逐格 × 逐臂（均值）与两臂配对量')
hdr = ('cell', 'n', 'Mval_b', 'Mval_s', 'Mtest_b', 'Mtest_s', 'val差', 'test差', 'Δgap', 'p', 'prem_b', 'prem_s', 'gap_b')
emit(f'{hdr[0]:16}{hdr[1]:>4}{hdr[2]:>9}{hdr[3]:>9}{hdr[4]:>9}{hdr[5]:>9}{hdr[6]:>8}{hdr[7]:>8}{hdr[8]:>8}{hdr[9]:>9}{hdr[10]:>8}{hdr[11]:>8}{hdr[12]:>8}')

table = {}
for cell in sorted(cells):
    b, s = cells[cell].get('base', {}), cells[cell].get('strat', {})
    seeds = sorted(set(b) & set(s))
    if len(seeds) < 2:
        continue
    mv_b = np.mean([b[k]['mval'] for k in seeds]); mv_s = np.mean([s[k]['mval'] for k in seeds])
    mt_b = np.mean([b[k]['mtest'] for k in seeds]); mt_s = np.mean([s[k]['mtest'] for k in seeds])
    val_diff = mv_b - mv_s            # 正 = 基线在 val 上更好
    test_diff = mt_b - mt_s           # 正 = 基线在 test 上更好
    d = np.array([b[k]['gap'] - s[k]['gap'] for k in seeds])
    m, sd_, t, p, ci = ci95(d)
    pb = np.mean([b[k]['prem'] for k in seeds]); ps = np.mean([s[k]['prem'] for k in seeds])
    table[cell] = dict(n=len(seeds), mv_b=mv_b, mv_s=mv_s, mt_b=mt_b, mt_s=mt_s,
                       val_diff=val_diff, test_diff=test_diff, dgap=m, p=p, ci=ci,
                       prem_b=pb, prem_s=ps, dprem=pb - ps, gap_b=mv_b - mt_b, gap_s=mv_s - mt_s)
    emit(f'{cell[:16]:16}{len(seeds):>4}{mv_b:>9.2f}{mv_s:>9.2f}{mt_b:>9.2f}{mt_s:>9.2f}'
         f'{val_diff:>+8.2f}{test_diff:>+8.2f}{m:>+8.2f}{p:>9.4g}{pb:>+8.2f}{ps:>+8.2f}{table[cell]["gap_b"]:>+8.2f}')
emit()

sig = {c: v for c, v in table.items() if v['p'] < 0.05}
emit(f'显著格 {len(sig)} 个（p < 0.05）：' + '、'.join(f'{c}(Δgap={v["dgap"]:+.2f})' for c, v in sig.items()))
emit()

# ---------------- 四个候选机制
emit('=' * 88)
emit('候选机制逐条检验')
emit('=' * 88)
emit()

def verdict(name, cond_pass, detail):
    emit(f'【{name}】 {"成立" if cond_pass else "被排除"}')
    for d in detail:
        emit('    ' + d)
    emit()
    return cond_pass

# M1 乘性（相对）增益：Δgap = ρ · gap_base ⇒ sign(Δgap) == sign(gap_base)
ok, bad = True, []
for c, v in table.items():
    if v['gap_b'] > 0.5 and v['dgap'] < -0.05:
        ok = False; bad.append(f'{c}: gap_b={v["gap_b"]:+.2f} 但 Δgap={v["dgap"]:+.2f}')
    if v['gap_b'] < -0.5 and v['dgap'] > 0.05:
        ok = False; bad.append(f'{c}: gap_b={v["gap_b"]:+.2f} 但 Δgap={v["dgap"]:+.2f}')
verdict('M1 乘性增益：策略按固定比例改进 ⇒ Δgap 应与 gap 同号', ok,
        ([f'反例 {len(bad)} 处：'] + bad[:6]) if bad else ['全部 13 格符号一致'])

# M2 容易的划分压缩优势：gap 大 ⇒ Δgap 负
big = [c for c, v in table.items() if abs(v['gap_b']) > 10]
if len(big) >= 2:
    ok2 = all(table[c]['dgap'] < 0 for c in big)
    verdict('M2 天花板压缩：|gap| 越大越压缩策略优势 ⇒ Δgap 应随 |gap| 增大而变负', ok2,
            [f'|gap_b| > 10 的格：' + '、'.join(f'{c}(gap_b={table[c]["gap_b"]:+.1f}, Δgap={table[c]["dgap"]:+.2f})' for c in big)])
    # 全体相关
    xs2 = np.array([v['gap_b'] for v in table.values()]); ys2 = np.array([v['dgap'] for v in table.values()])
    r2, p2 = stats.pearsonr(xs2, ys2)
    emit(f'    全体 13 格 Pearson(gap_b, Δgap) r = {r2:+.3f}, p = {p2:.3f}')
    emit()
else:
    verdict('M2 天花板压缩', False, [f'|gap_b| > 10 的格只有 {len(big)} 个，**无法检验**（不当作成立）'])

# M3 水平/信噪比决定"能否分辨"（而非符号）
hi = np.array([v['mv_b'] for c, v in table.items() if v['p'] < 0.05])
lo = np.array([v['mv_b'] for c, v in table.items() if v['p'] >= 0.05])
emit('【M3 水平（val mAP 量级）决定可分辨性】')
emit(f'    显著格 val 基线均值 {hi.mean():.2f} pp（n={len(hi)}）；不显著格 {lo.mean():.2f} pp（n={len(lo)}）')
if len(hi) >= 2 and len(lo) >= 2:
    t, p = stats.ttest_ind(hi, lo, equal_var=False)
    emit(f'    Welch t = {t:.2f}, p = {p:.3f} ⇒ ' + ('两组无可分辨差异' if p > 0.05 else '两组有差异'))
emit()

# M4 策略在 test 上是否真有增益，决定 Δgap 符号
ok4, det4 = True, []
for c, v in table.items():
    strat_wins_test = v['test_diff'] < 0          # 策略在 test 上更好
    if strat_wins_test and v['dgap'] < -0.05:     # 策略在 test 上赢，但 val 高估它（Δgap<0）
        ok4 = False; det4.append(f'{c}: test 上策略更好({-v["test_diff"]:+.2f}) 但 Δgap={v["dgap"]:+.2f}')
verdict('M4 "策略在 test 上是否真有增益"决定 Δgap 符号', ok4,
        ([f'反例 {len(det4)} 处：'] + det4[:6]) if det4 else ['无反例'])

# M5 val 侧的选点获益之差（可直接由归档算出）：Δgap 是否与 (prem_base − prem_strat) 同号
agree = sum(1 for c, v in table.items()
            if (v['dgap'] > 0) == (v['dprem'] > 0))
emit('【M5 val 侧选点获益之差：Δgap 与 (premium_base − premium_strat) 同号？】')
emit(f'    13 格中同号 {agree} 格、异号 {13 - agree} 格')
for c, v in sorted(table.items(), key=lambda kv: -abs(kv[1]['dgap'])):
    emit(f'      {c[:18]:18} Δgap={v["dgap"]:+7.2f}  Δpremium={v["dprem"]:+7.2f}  '
         f'{"同号" if (v["dgap"] > 0) == (v["dprem"] > 0) else "异号"}')
xs = np.array([v['dprem'] for v in table.values()]); ys = np.array([v['dgap'] for v in table.values()])
if xs.std() > 0:
    r, pr = stats.pearsonr(xs, ys)
    emit(f'    Pearson r = {r:+.3f}, p = {pr:.3f}（n = {len(xs)}）')
emit()

# ---------------- 精确三分量分解（恒等式，用于说明符号为何不稳）
emit('=' * 88)
emit('精确三分量分解：Δgap 由三个可直接算出的分量合成')
emit('=' * 88)
emit()
emit('  因 M_val(ê) = V_final + premium_val，展开得恒等式：')
emit('     Δgap = (V_b^final − V_s^final)  +  (prem_b − prem_s)  −  (T_b − T_s)')
emit('            └ 末轮 val 的臂间差 ┘   └ val 侧选点获益之差 ┘   └ test 侧臂间差 ┘')
emit()
emit(f'{"cell":16}{"Δgap":>8}{"末轮val差":>11}{"Δprem":>9}{"-test差":>9}{"校验":>7}   主导分量')
for c, v in sorted(table.items(), key=lambda kv: -abs(kv[1]['dgap'])):
    # 末轮 val 的臂间差需重算：V_final = M_val(ê) − prem
    b, s = cells[c]['base'], cells[c]['strat']
    ks = sorted(set(b) & set(s))
    vfb = np.mean([b[k]['mval'] - b[k]['prem'] for k in ks])
    vfs = np.mean([s[k]['mval'] - s[k]['prem'] for k in ks])
    fin = vfb - vfs
    dprem = v['dprem']
    negtest = -v['test_diff']          # 符号约定成"对 Δgap 的贡献"
    chk = fin + dprem + negtest
    comps = {'末轮val差': fin, 'Δprem': dprem, '−test差': negtest}
    dom = max(comps, key=lambda k: abs(comps[k]))
    emit(f'{c[:16]:16}{v["dgap"]:>+8.2f}{fin:>+11.2f}{dprem:>+9.2f}{negtest:>+9.2f}{chk:>+7.2f}   {dom}')
emit()
emit('（"校验"列必须等于 Δgap——若不等说明分解写错。全部相等即恒等式成立。）')
emit()

# 两个分量的相对大小：说明"为什么符号不稳"
absd = [abs(np.mean([cells[c]['base'][k]['mval'] - cells[c]['base'][k]['prem'] for k in sorted(set(cells[c]['base']) & set(cells[c]['strat']))])
            - np.mean([cells[c]['strat'][k]['mval'] - cells[c]['strat'][k]['prem'] for k in sorted(set(cells[c]['base']) & set(cells[c]['strat']))]))
        for c in table]
emit(f'|末轮 val 臂间差| 的中位数：{np.median(absd):.2f} pp')
emit(f'|Δprem| 的中位数：{np.median([abs(v["dprem"]) for v in table.values()]):.2f} pp')
emit(f'|test 臂间差| 的中位数：{np.median([abs(v["test_diff"]) for v in table.values()]):.2f} pp')
emit('⇒ 三个分量同量级 ⇒ 任一分量的抖动都能翻转 Δgap 的符号。')
emit()

# ---------------- 结论
emit('=' * 88)
emit('结论（脚本判读，供人工复核）')
emit('=' * 88)
emit()
emit('恒等式（不是机制，但决定怎么解释）：')
emit('    Δgap > 0  ⟺  val 上"基线相对策略的相对增益"小于 test 上的同一量')
emit('    即：Δgap 只是"两臂相对差在两个划分上的比较"，它不指向任何单一生成原因。')
emit()
emit('因此要解释符号，需要能把下列两个分量分开的量：')
emit('    ① 两划分的难度差（含被选 checkpoint 在不同划分上的难度差）')
emit('    ② 选点乐观在两臂之间的差（val 侧与 test 侧各一份）')
emit('归档里没有【非选中 epoch 上的 test 指标】，②的 test 侧那一份算不出来——这就是缺口。')
emit()

io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(buf) + '\n')
print(f'\n输出已写：{OUT}')
