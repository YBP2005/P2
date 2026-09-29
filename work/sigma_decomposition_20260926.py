# -*- coding: utf-8 -*-
"""σ 三分量的**单一复算脚本**（B14：把 §10 缺陷 5 自认"没有脚本"的那个洞填上）。

## 它算什么
论文 §8.4 / Table S19 报的三个方差分量，逐个从**档案里的逐值记录**重算，并**断言**与印出的数一致：

| 分量 | 输入（档案逐值） | 脚本重算 | 论文印的 |
|---|---|---|---|
| 数据顺序（第二分量） | 10 个逐种子增益 × 2 单元 | SD(n=9, ddof=1)=smoke **0.403** / SHWD **0.515**；SD(n=10)=**0.383** / **0.488**；均值 n=9 **1.420**/**0.492** | Table S19 与 §1.0/§1.0b 同值 |
| 初始化（第一分量） | 3 个初始化的 base 端点与增益 | 增益 SD **0.146**、均值 **0.437**、极差 **0.290**、端点 SD **0.209** | Table S19 同值 |
| 增广 RNG | **记录里只有 SD，没有逐值** | **不重算** —— 只核对该 SD 在档案里被记录过 | 0.246（策略臂）/ 0.190（基线臂） |

**为什么第三项不重算**：档案（`r10_pvalue_table_20260915.md` 的功效段）只记了该对照的 **SD = 0.246 pp**，
**没有逐值**。本脚本**不做"把常数打印出来假装算过"的事**（本库 `22` §6.2 记过这个陷阱）——
它对第三项做的是**引用核对**，并在输出里明确标成 `cited, not recomputed`。

## 输入在哪，找不到会怎样
逐值记录在档案件 `r10_initvar_and_seedext_20260915.md`（P2 语料侧的收官读数件）。
**脚本只读它、不写任何东西**；**找不到就非零退出并说明**，绝不静默跳过（静默跳过正是"看起来在算"的来源）。

用法：python work/sigma_decomposition_20260926.py [--record <路径>]
"""
import io
import os
import re
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')
DEFAULT_RECORD = r'D:\deepseek\analysis\r10_initvar_and_seedext_20260915.md'
AUGREC = r'D:\deepseek\analysis\r10_pvalue_table_20260915.md'

# 论文印出的值（Table S19 / §8.4）——脚本要**证明**它们能从逐值重算出来
EXPECT = {
    'order_sd9_smoke': 0.403, 'order_sd9_shwd': 0.515,
    'order_sd10_smoke': 0.383, 'order_sd10_shwd': 0.488,
    'order_mean9_smoke': 1.420, 'order_mean9_shwd': 0.492,
    'aug_strategy_sd': 0.246, 'aug_baseline_sd': 0.190,
    'init_gain_sd': 0.146, 'init_gain_mean': 0.437, 'init_gain_range': 0.290,
    'init_endpoint_sd': 0.209,
}
TOL = 5e-4   # 论文印到三位小数


def read_record(path):
    if not os.path.exists(path):
        sys.exit('!! 找不到逐值记录件：%s\n   本脚本只读档案、不写盘；找不到就退出，不静默跳过。' % path)
    return io.open(path, encoding='utf-8').read()


def parse_seed_gains(txt):
    """从记录件里取两条『逐种子增益』行。"""
    out = {}
    for key, pat in (('smoke', r'^-\s*smoke：(.*)$'), ('shwd', r'^-\s*SHWD：(.*)$')):
        m = re.search(pat, txt, re.M)
        assert m, '记录件里找不到 %s 的逐种子增益行' % key
        out[key] = [float(x.replace('\u2212', '-'))
                    for x in re.findall(r'[+\u2212-]?\d+\.\d+', m.group(1))]
        assert len(out[key]) == 10, '%s 的逐种子增益应为 10 个，实得 %d' % (key, len(out[key]))
    return out


def parse_init_table(txt):
    """从记录件里取三个初始化的『基线 / 增益』。"""
    rows = re.findall(r'^\|\s*src(\d)\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|\s*\*\*([+\u2212-][\d.]+) pp\*\*\s*\|',
                      txt, re.M)
    assert len(rows) == 3, '初始化表应有 3 行，实得 %d' % len(rows)
    base = [float(r[1]) for r in rows]
    gain = [float(r[3].replace('\u2212', '-')) for r in rows]
    return base, gain


def main():
    rec_path = DEFAULT_RECORD
    if '--record' in sys.argv:
        rec_path = sys.argv[sys.argv.index('--record') + 1]
    txt = read_record(rec_path)
    print('=== σ 三分量复算（单一脚本）===')
    print('  逐值记录件：%s（%d 字符）' % (rec_path, len(txt)))
    fails = []

    def check(tag, got, want):
        ok = abs(got - want) <= TOL
        print('   %-4s %-30s 重算 %.3f / 论文 %.3f' % ('ok' if ok else 'FAIL', tag, got, want))
        if not ok:
            fails.append('%s: recomputed %.4f vs printed %.3f' % (tag, got, want))

    # ── 第二分量：数据顺序（唯一有逐值的一项）──────────────────────────────────
    g = parse_seed_gains(txt)
    for key, k9, k10, m9 in (('smoke', 'order_sd9_smoke', 'order_sd10_smoke', 'order_mean9_smoke'),
                             ('shwd', 'order_sd9_shwd', 'order_sd10_shwd', 'order_mean9_shwd')):
        v = g[key]
        check('%s 数据顺序 SD(n=9)' % key, st.stdev(v[:9]), EXPECT[k9])
        check('%s 数据顺序 SD(n=10)' % key, st.stdev(v), EXPECT[k10])
        check('%s 数据顺序 均值(n=9)' % key, st.mean(v[:9]), EXPECT[m9])
    print('   （ddof=1；n=9 取前九个种子 42–50，n=10 取 42–51 —— 与记录件的 1.0 / 1.0b 两表同口径）')

    # ── 第一分量：初始化 ──────────────────────────────────────────────────────
    base, gain = parse_init_table(txt)
    check('初始化 增益 SD', st.stdev(gain), EXPECT['init_gain_sd'])
    check('初始化 增益 均值', st.mean(gain), EXPECT['init_gain_mean'])
    check('初始化 增益 极差', max(gain) - min(gain), EXPECT['init_gain_range'])
    check('初始化 端点 SD', st.stdev(base), EXPECT['init_endpoint_sd'])

    # ── 第三分量：增广 RNG —— 只核对"被记录过"，不假装重算 ────────────────────────
    if os.path.exists(AUGREC):
        a = io.open(AUGREC, encoding='utf-8').read()
        hit = ('%.3f' % EXPECT['aug_strategy_sd']) in a
        print('   %-4s %-30s 记录件里记着 SD=%.3f：%s'
              % ('ok' if hit else 'FAIL', '增广 RNG（cited, not recomputed）',
                 EXPECT['aug_strategy_sd'], hit))
        if not hit:
            fails.append('augmentation SD not recorded in %s' % AUGREC)
    else:
        print('   --   增广 RNG：引用件不在本机（%s）⇒ 本项只标 cited，不重算' % AUGREC)
    print('   ⚠ 增广 RNG 一项**未被本脚本重算**：档案只记了 SD、没有逐值。'
          '基线臂 0.190 pp 同属该记录件的引用，不作为本脚本的重算结果。')

    print()
    if fails:
        sys.exit('!! σ 三分量复算失败 %d 项：\n   - %s' % (len(fails), '\n   - '.join(fails)))
    print('结论：两个分量（数据顺序、初始化）由本脚本**从逐值重算**并与论文印出的数逐项一致；'
          '第三项（增广 RNG）在档案里只有 SD，本脚本只做引用核对。')


if __name__ == '__main__':
    main()
