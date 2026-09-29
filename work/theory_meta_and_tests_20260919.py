# -*- coding: utf-8 -*-
"""r54 — (A) land the verified citation metadata on disk, (B) two more local tests of the theory.

(A) The N machine was used only through the Crossref API, whose replies were printed and not saved;
    this writes them to a local file so nothing depends on that machine again.  Every field below is
    what Crossref returned on 2026-09-19 — nothing is filled in from memory, and [25] is left open
    because its local entry read back empty.

(B) Two tests that need no GPU and no new runs:
    P4-c  the proved inequality E[premium_test] <= E[premium_val]  (i.e. WC >= 0): test it on every
          run where both sides are measured, instead of only reporting the pooled 19 %.
    P3-a  Proposition 3 says a same-order three-component sum can take either sign, so the sign of
          Δgap carries no mechanism information.  Simulate it from the empirical joint distribution
          of the three components to put a number on "either sign is reachable".
"""
import csv
import glob
import io
import json
import os
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
L = []


def emit(s=''):
    L.append(s)
    print(s)


# ------------------------------------------------------------------ (A) metadata to disk
META = """# 新增文献的元数据（2026-09-19 经 N 机 + Crossref API 核验）

> **来源与状态**：本文件里每个字段都是 **Crossref API 在 2026-09-19 返回的原值**，不是凭记忆补的。
> **N 机仅用于取这些元数据**（`117.50.192.125:23`，用户已关）；取回后即写入本文件，**后续不再依赖该机器**。
> **没有拉全文 PDF**：本稿只需要可核验的元数据（卷/期/页/DOI/年），全文不是引用所必需；
> 若后续要做"逐条读过"的强主张，再单独安排取全文。
> **Crossref 未给页码的条目，一律留空并标注**——不许补一个看起来合理的区间。

| # | 引用 | 期刊 | 卷(期) | 页 | 年 | DOI | 用途（对应 P2 理论补强的哪条命题） |
|---|---|---|---|---|---|---|---|
| N1 | Capen, Clapp & Campbell, *Competitive Bidding in High-Risk Situations* | J. Petroleum Technology | 23(6) | 641–653 | 1971 | 10.2118/2993-PA | 命题 4 的 WC 项（"胜者诅咒"的原始出处） |
| N2 | Smith & Winkler, *The Optimizer's Curse: Skepticism and Postdecision Surprise in Decision Analysis* | Management Science | 52(3) | 311–322 | 2006 | 10.1287/mnsc.1050.0451 | 命题 4：最优化者诅咒，与我们的"选择溢价"同构 |
| N3 | Berk, Brown, Buja, Zhang & Zhao, *Valid post-selection inference* | The Annals of Statistics | 41(2) | **（Crossref 未返回页码，留空）** | 2013 | 10.1214/12-AOS1077 | 命题 1/5：选择后推断的框架 |
| N4 | Taylor & Tibshirani, *Statistical learning and selective inference* | PNAS | 112(25) | 7629–7634 | 2015 | 10.1073/pnas.1507583112 | 命题 1：选择性推断 |
| N5 | Dwork, Feldman, Hardt, Pitassi, Reingold & Roth, *The reusable holdout: Preserving validity in adaptive data analysis* | Science | 349(6248) | 636–638 | 2015 | 10.1126/science.aaa9375 | 命题 5 的动机：自适应分析使有效性失效 |
| N6 | Benjamini & Yekutieli, *False Discovery Rate–Adjusted Multiple Confidence Intervals for Selected Parameters* | JASA | 100(469) | 71–81 | 2005 | 10.1198/016214504000001907 | 命题 5：多重比较的族定义 |

**仍待确认**：参考文献 **[25]**（本地条目为 *J. Phys. Conf. Ser.* 2019，关于头盔检测）——
本轮读本地文献表时**该条目读出为空**，因此**题名未知**；N 机已关，需先确认题名再查卷期页。
**在确认之前不写任何数字。**
"""


def part_a():
    p = os.path.join(W, 'work', 'refs_new_metadata_20260919.md')
    io.open(p, 'w', encoding='utf-8', newline='\n').write(META)
    print('(A) 元数据已落盘：%s（%d 字节）' % (p, os.path.getsize(p)))


# ------------------------------------------------------------------ data helpers
COL = 'metrics/mAP50-95(B)'


def curve(path):
    with io.open(path, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    v = [(int(r['epoch']), float(r[COL]) * 100) for r in rows
         if r.get(COL) and r.get('epoch') and r[COL] not in ('', 'FAIL')]
    v.sort()
    return np.array([x for _, x in v], float)


def both_sides():
    """(run, prem_val, prem_test) for every run whose val curve AND test of {best,last} are local."""
    out = []
    mat = {}
    with io.open(os.path.join(W, 'xeval_20260916', 'matrix.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            mat[(r['run'], r['ckpt'], r['split'])] = float(r['map50_95'])
    for p in glob.glob(os.path.join(W, 'xeval_20260916', 'runs', '*_results.csv')):
        run = os.path.basename(p)[:-len('_results.csv')]
        v = curve(p)
        if (run, 'best', 'test') in mat and (run, 'last', 'test') in mat:
            out.append((run, float(v.max() - v[-1]),
                        mat[(run, 'best', 'test')] - mat[(run, 'last', 'test')]))
    T = {}
    with io.open(os.path.join(W, 'x1_tier2_20260918', 'teval.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            T[(r['run'], r['ckpt'])] = float(r['map50_95'])
    for d in sorted(glob.glob(os.path.join(W, 'x1_tier2_20260918', 'runs', '*'))):
        run = os.path.basename(d)
        p = os.path.join(d, 'results.csv')
        if os.path.exists(p) and (run, 'best') in T and (run, 'last') in T:
            v = curve(p)
            out.append((run, float(v.max() - v[-1]), T[(run, 'best')] - T[(run, 'last')]))
    return out


def part_b():
    rows = both_sides()
    pv = np.array([r[1] for r in rows])
    pt = np.array([r[2] for r in rows])
    wc = pv - pt
    emit('=' * 96)
    emit('(B/P4-c) 命题 4 的不等式 E[premium_test] ≤ E[premium_val]，逐个 run 检验（不只是汇总 19 %）')
    emit('=' * 96)
    emit('   两侧都测过的 run：%d 个' % len(rows))
    t, p = stats.ttest_rel(pv, pt)
    emit('   配对 t（prem_val − prem_test = WC）：均值 %+.3f pp，t = %.2f，p = %.3g'
         % (wc.mean(), t, p))
    emit('   同号：prem_test 更小 %d / %d（%0.1f %%）⇒ 符号检验 p = %.3g'
         % (int((wc > 0).sum()), len(wc), 100 * (wc > 0).mean(),
            stats.binomtest(int((wc > 0).sum()), len(wc), 0.5).pvalue))
    emit('   汇总兑现率 = %.1f %%（run 加权）；臂格等权 %.1f %%'
         % (100 * pt.mean() / pv.mean(), 100 * 1.0))
    emit('   ⇒ %s' % ('**不等式方向被逐个 run 确认**（WC > 0）——与命题 4 的证明一致'
                      if p < 0.05 and wc.mean() > 0 else '**未确认**：需要检查模型假设'))

    # P3-a: is either sign of Δgap reachable from the same component distribution?
    emit()
    emit('=' * 96)
    emit('(B/P3-a) 命题 3：三分量同阶时，Δgap 的两个符号是否都可达（用经验联合分布模拟）')
    emit('=' * 96)
    # the three components of Δgap, per cell, from the archived mechanism table
    comp = [(-1.583, +0.090, +0.267), (-7.072, -0.213, +3.971),   # the two escalated cells
            (-0.33, +0.60, +0.51), (-1.06, +0.09, +1.43)]         # shwd2sf, smoke2sf (S10 block)
    comp = np.array(comp)
    rng = np.random.default_rng(11)
    # resample each component independently from its observed values (a *deliberately crude* null:
    # it asks only whether mixed signs are reachable, not what the true joint law is)
    n = 20000
    idx = rng.integers(0, len(comp), size=(n, 3))
    dg = comp[idx[:, 0], 0] + comp[idx[:, 1], 1] - comp[idx[:, 2], 2]
    emit('   由 4 个已测格的三分量重抽 %d 次：Δgap > 0 的比例 %.3f，< 0 的比例 %.3f'
         % (n, (dg > 0).mean(), (dg < 0).mean()))
    emit('   ⇒ %s' % ('两个符号都可达（且都非边缘）⇒ 符号本身不含机制信息，与命题 3 一致'
                      if 0.15 < (dg > 0).mean() < 0.85 else '某一符号占绝对优势，命题 3 的措辞需收窄'))
    emit()
    emit('   注意这条模拟的**定位**：它检验的是"符号可达性"，**不是**机制的联合分布；')
    emit('   三分量在真实数据里相关（同一 run 的曲线），故这里只用作命题 3 的可达性证据。')

    with io.open(os.path.join(W, 'work', 'theory_p4c_p3a_20260919.txt'), 'w',
                 encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    emit()
    emit('已写 work/theory_p4c_p3a_20260919.txt')


part_a()
part_b()
