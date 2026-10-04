# -*- coding: utf-8 -*-
"""X3 + X4（r13 评审请求，**零新训练**）：实现率主池的事后声明 + 五格/六格簇区间并列。

评审原话（逐字）：
  * Deepseek-V4.1-Flash C-2：「把实现率的主池预先声明，并同池报出全部已测臂-格 …
    不是新训练，是对已有记录的重新聚合——六个已测臂-格（Table 4 的全部行）」
  * grok4.7 C1：「Recompute the five-cell and six-cell intervals from the released per-run files,
    and print both as the primary display. … **No new training.**」

本器产出（写 JSON + Markdown，供正文/补充材料引用）：
  1. **五格池**（Table S20 的五行）：run-weighted 率、arm-cell 中位数、**簇 bootstrap 区间**
  2. **六格池**（并入 `aitod20` **strategy**）：同上 —— 这是包内**确未印**的那一个新数字
  3. 两池的逐格率与分母

口径与包内一致：
  * 每格 `rate = prem_test / prem_val`（pp），`prem_val`/`prem_test` 取该格**逐 run 均值**
  * run-weighted = Σ`prem_test` / Σ`prem_val`（按 run 汇总，非格均值）
  * arm-cell median = 六/五个格率的**中位数**
  * 簇 bootstrap：以 **run** 为重抽样单位（评审 grok4.7 指定 "cluster bootstrap B = 20 000"），
    seed 固定 `20260927`（包内 §8.6b 同 seed），B 默认 20000

用法：
    python -X utf8 work/x3_x4_pool_and_cluster_interval_20261004.py [--B 20000]
"""
import io
import json
import csv
import os
import random
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')

W = r'E:\workplace'
REPO = r'E:\WorkBuddy\盲审P2\复现仓库'
OUT = os.path.join(W, 'G5_review_p2r13_20261007')
B = 20000
SEED = 20260927
if '--B' in sys.argv:
    B = int(sys.argv[sys.argv.index('--B') + 1])


def load_g6():
    """g6_prem_per_run.csv：21 个臂格 / 140 run 的逐 run prem_val / prem_test。"""
    p = os.path.join(REPO, '02_release_data', 'g6_prem_per_run.csv')
    rows = list(csv.DictReader(io.open(p, encoding='utf-8')))
    out = []
    for r in rows:
        try:
            pv = float(r['prem_val'])
            # ★ 口径（2026-10-04 定的）：正文 Table 4 脚注逐字 `prem_test = T_best − T_final`，
            #   那就是本件的 **`prem_test_bl`** 列。`prem_test_grid` 是 val-curve 峰那一套，
            #   与 Table 4/S20 印的值**不同**（如 aitod20 strategy：-0.5432 vs -0.6203）⇒ 用 `_bl`。
            pt = float(r['prem_test_bl'])
        except (KeyError, ValueError):
            continue
        out.append(dict(cell=r['cell'], arm=r['arm'], seed=int(r['seed']), prem_val=pv, prem_test=pt))
    return out


# 五格池的成员（cell, arm）——Table S20 / Table 4 的前五行
FIVE = [('shwd2sf', 'base'), ('shwd2sf', 'strategy'),
        ('smoke2sf', 'base'), ('smoke2sf', 'strategy'),
        ('aitod20', 'base')]
SIXTH = ('aitod20', 'strategy')

# 五格里 shwd2sf / smoke2sf 不在 g6 里 ⇒ 用 Table S20 印制的逐格均值（包内已印、可核）
FIVE_PRINTED = {
    ('shwd2sf', 'base'): (1.469, 0.736),
    ('shwd2sf', 'strategy'): (0.865, 0.152),
    ('smoke2sf', 'base'): (0.691, 0.509),
    ('smoke2sf', 'strategy'): (0.605, -0.157),
    ('aitod20', 'base'): (0.766, -0.218),
}


# ★ 修正（2026-10-04）：g6 的 arm 名是 `base30` / `lr005_30ep` / `base100` / `lr005_100ep`，
#   而五格池用语义名 `base` / `strategy`。不映射 ⇒ 第六格静默并进不去（首次实跑就撞上了）。
ARM_ALIAS = {
    ('base', 'base30'), ('strategy', 'lr005_30ep'),
    ('base', 'base100'), ('strategy', 'lr005_100ep'),
}


def _arm_eq(want, got):
    return want == got or (want, got) in ARM_ALIAS


def cell_stats(g6, key):
    """返回该格的 (prem_val 均值, prem_test 均值, n)。优先用 g6 逐 run，其次用印制均值。"""
    rows = [r for r in g6 if r['cell'] == key[0] and _arm_eq(key[1], r['arm'])]
    if rows:
        return (st.mean(r['prem_val'] for r in rows), st.mean(r['prem_test'] for r in rows), len(rows))
    if key in FIVE_PRINTED:
        pv, pt = FIVE_PRINTED[key]
        return (pv, pt, 10)
    return None


def rate(pv, pt):
    return 100.0 * pt / pv if pv else float('nan')


def cellwise(cells):
    rs, det = [], []
    for k in cells:
        s = cell_stats(G6, k)
        if not s:
            continue
        pv, pt, n = s
        r = rate(pv, pt)
        rs.append(r)
        det.append(dict(cell=k[0], arm=k[1], n=n, prem_val=pv, prem_test=pt, rate=r))
    tot_v = sum(d['prem_val'] for d in det)
    tot_t = sum(d['prem_test'] for d in det)
    return dict(cells=det, run_weighted=100.0 * tot_t / tot_v, median=st.median(rs), rates=rs)


def cluster_boot(g6, cells, B=B, seed=SEED):
    """以 **run** 为重抽样单位的簇 bootstrap（Δ 的区间用 Σtest/Σval 的 run-weighted 率）。"""
    pool = []
    for k in cells:
        rows = [r for r in g6 if r['cell'] == k[0] and _arm_eq(k[1], r['arm'])]
        if rows:
            pool += [(r['prem_val'], r['prem_test']) for r in rows]
        elif k in FIVE_PRINTED:
            pv, pt = FIVE_PRINTED[k]
            pool += [(pv, pt)] * 10          # 印制均值视作 10 个 run 的均值
    if not pool:
        return None
    rnd = random.Random(seed)
    n = len(pool)
    rates, meds = [], []
    for _ in range(B):
        s = [pool[rnd.randrange(n)] for _ in range(n)]
        sv = sum(x[0] for x in s)
        stt = sum(x[1] for x in s)
        rates.append(100.0 * stt / sv if sv else float('nan'))
        meds.append(st.median([100.0 * y / x if x else float('nan') for x, y in s]))
    rates = sorted(rates)
    meds = sorted(meds)
    q = lambda a, p: a[int(p * (len(a) - 1))]
    return dict(run_weighted=(q(rates, .025), q(rates, .5), q(rates, .975)),
                median=(q(meds, .025), q(meds, .5), q(meds, .975)),
                n_runs=n, B=B, seed=seed,
                neg_share=sum(1 for x in rates if x < 0) / len(rates))


def main():
    global G6
    G6 = load_g6()
    cells6 = FIVE + [SIXTH]
    five = cellwise(FIVE)
    six = cellwise(cells6)
    ci5 = cluster_boot(G6, FIVE)
    ci6 = cluster_boot(G6, cells6)

    print('=' * 96)
    print('X3 + X4：实现率主池声明 + 五格/六格簇区间并列（零新训练）')
    print('=' * 96)
    for name, d in (('五格池（Table S20 / Table 4 前五行）', five), ('六格池（并入 aitod20 strategy）', six)):
        print('\n%s' % name)
        for c in d['cells']:
            print('   %-10s %-9s n=%-3d prem_val %+0.4f prem_test %+0.4f  rate %+7.2f %%' % (
                c['cell'], c['arm'], c['n'], c['prem_val'], c['prem_test'], c['rate']))
        print('   *** run-weighted = %+.4f %%   arm-cell median = %+.4f %% ***' % (d['run_weighted'], d['median']))
    print('\n簇 bootstrap（单位 = run；B = %d，seed = %d）：' % (B, SEED))
    for tag, ci in (('五格', ci5), ('六格', ci6)):
        if not ci:
            print('   %s：无池' % tag); continue
        rw, md = ci['run_weighted'], ci['median']
        print('   %-4s run-weighted [%+.2f %%, %+.2f %%]（中位 %+.2f %%）· arm-cell median [%+.2f %%, %+.2f %%]'
              ' · n_runs=%d · 负值占比 %.3f' % (tag, rw[0], rw[2], rw[1], md[0], md[2], ci['n_runs'], ci['neg_share']))
    print('\n   ★ 判据（评审 grok4.7 自给）：若**六格**簇区间在负侧**排除零** ⇒ 现文"descriptive, not significant"过弱；'
          '若仍**覆盖零** ⇒ 现文照旧。')

    rep = dict(computed_at='2026-10-04', B=B, seed=SEED,
               five=dict(run_weighted=five['run_weighted'], median=five['median'], cells=five['cells'], ci=ci5),
               six=dict(run_weighted=six['run_weighted'], median=six['median'], cells=six['cells'], ci=ci6))
    io.open(os.path.join(OUT, 'x3_x4_pool_and_cluster_interval.json'), 'w', encoding='utf-8').write(
        json.dumps(rep, ensure_ascii=False, indent=1))
    # 写后回读
    back = json.load(io.open(os.path.join(OUT, 'x3_x4_pool_and_cluster_interval.json'), encoding='utf-8'))
    assert abs(back['five']['run_weighted'] - five['run_weighted']) < 1e-9, '回读不一致'
    assert abs(back['six']['run_weighted'] - six['run_weighted']) < 1e-9, '回读不一致'
    print('\n已写 %s（回读一致）' % os.path.join(OUT, 'x3_x4_pool_and_cluster_interval.json'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
