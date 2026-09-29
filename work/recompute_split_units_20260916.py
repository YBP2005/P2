#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""副论文前置件：19 行 × 5 列单位标记表 + 重算。

目的
----
审计文档（benchmark_split_audit.md）混用了四个计数单位而未声明，导致 (d)(g)(h) 三处不一致。
本脚本把 19 个基准行**逐行**标记为三种单位下的判决，使所有头条百分比**可由标记机械重算**。

三种单位（论文中必须写明用哪一条）
--------------------------------
  release   基准自身发布物层：官方发布的分划产物/脚本是否提供独立留出 test
  protocol  官方协议层：官方 README/论文/网站声明的划分，且该 test 是否本地可自评
  reported  实际报告层：文献里报告的数字来自哪个划分、该划分是否独立于选点

判决取值
--------
  independent_test / clean / alias / no_test / no_val / no_split / test_gated /
  contradictory / no_yaml / train_val_alias / n_a / unknown

证据来源标记（每格后缀）
------------------------
  (A) 审计文档明文
  (D) 由审计文档陈述的事实推导（推导规则写在 note）
  (?) 审计文档未表态

纪律
----
 * 本脚本是新文件，不覆盖 analysis/ 下任何既有文件。
 * 行数据放在脚本内（与 _ev_final_audit.py 的惯例一致）。
 * 所有计数都由行数据算出，脚本内不出现硬编码的百分比。
 * 已按 (h-1) 裁定更正 D-Fire / FireSmoke 族：见 ROWS[18] 的 note 与 CORRECTIONS。
"""

import io, os, collections, sys
sys.stdout.reconfigure(encoding='utf-8')

OUTDIR = r'D:\deepseek\analysis\eval_validity'
OUT_TXT = os.path.join(OUTDIR, 'split_units_recompute_20260916.txt')
OUT_MD = os.path.join(OUTDIR, 'split_units_19rows_20260916.md')

# 每行：name, release, protocol, yolo_dist, reported, ev(证据类别), conf(A自评), note
# 括号内 (A)/(D)/(?) 为证源标记，见文件头。
ROWS = [
 dict(n='COCO', release='n_a(A)', protocol='independent_test(A)', yolo='clean(A)',
      reported='clean(A)', ev='官方计数 + mirror yaml', conf='high',
      note='官方不发 yaml。审计注记：训练于 train2017、早停于 test-dev 已属 "mild F-A-adjacent"，但仍计入干净。'),
 dict(n='PASCAL VOC', release='n_a(A)', protocol='test_gated(A)', yolo='alias(A)',
      reported='alias(A)', ev='mirror VOC.yaml（两键逐行引用）', conf='high',
      note='审计称 "the cleanest val == test instance in the whole audit"。VOC2012 test 标注从未发布。'),
 dict(n='Objects365', release='no_test(A)', protocol='no_test(A)', yolo='no_test_key(A)',
      reported='alias(D)', ev='mirror yaml + Ultralytics docs', conf='high',
      note='推导：审计引官方以 mAP^val 报告 → 报的是 val。v1 无 test；v2 才有 challenge test。'),
 dict(n='Open Images v7', release='independent_test(A)', protocol='independent_test(A)',
      yolo='no_test_key(A)', reported='alias(D)', ev='官方 facts page + mirror yaml', conf='high',
      note='推导：官方三划分全标注，但 YOLO 配置丢弃 test、报 val。'),
 dict(n='DOTA v1.0', release='independent_test(A)', protocol='independent_test(A)',
      yolo='clean(A)', reported='clean(A)', ev='官方下载页 + mirror DOTAv1.yaml', conf='high',
      note='Ultralytics 1411/458/937 是官方 train+val 的重划；test 是已标注数据的留出切片，非官方 test server。'),
 dict(n='DOTA v2.0', release='independent_test(A)', protocol='test_gated(A)',
      yolo='clean(A)', reported='alias(D)', ev='官方/mirror 文档', conf='high',
      note='推导：官方 test 标注 server-only → 本地不可自评 → 报的是 val。审计把它计入干净组，本表据"实际报告层"改判并留痕。'),
 dict(n='VisDrone-DET', release='independent_test(A)', protocol='independent_test(A)',
      yolo='clean(A)', reported='clean(A)', ev='mirror + converter', conf='high',
      note='审计备注：论文报告的 test 数是 test-dev 上的；test-challenge 被排除。'),
 dict(n='AI-TOD', release='contradictory(A)', protocol='contradictory(A)', yolo='unknown(A)',
      reported='unknown(?)', ev='官方 README（含两条互相矛盾的发布声明）', conf='low',
      note='审计自陈 "cannot determine from this README alone whether a third party can evaluate locally on AI-TOD-v2 test"。审计仍将其计入干净组——(d) 缺陷所在。'),
 dict(n='UAVDT', release='no_val(A)', protocol='no_val(A)', yolo='unknown(A)',
      reported='alias(A)', ev='官方论文 + 两个 mirror（审计称 unverified beyond these two）', conf='medium',
      note='官方只有 train/test（30/70 序列）。常用副本的 "128 images" 注释系从 coco128 复制。'),
 dict(n='xView', release='no_test(A)', protocol='no_test(A)', yolo='no_test_key(A)',
      reported='alias(A)', ev='mirror xView.yaml', conf='low',
      note='审计明示 "Treat 847/282 as config-asserted, not independently confirmed"；Ultralytics 用 847 的随机 90/10 autosplit 取代官方划分。'),
 dict(n='DIOR', release='independent_test(A)', protocol='independent_test(A)',
      yolo='no_test_key(A)', reported='unknown(?)', ev='官方描述（无计数）+ mirror DIOR-R yaml', conf='low',
      note='审计称无一次源给出官方逐划分计数；且 "DIOR" 在野外混指 HBB DIOR 与 OBB DIOR-R。'),
 dict(n='NWPU VHR-10', release='no_split(A)', protocol='no_split(A)', yolo='unknown(A)',
      reported='alias(A)', ev='官方 TorchGeo（split 指 positive/negative）', conf='high',
      note='数据集完全不发划分，任何 val==test 是第三方选择。审计要求正文写明"责任在 baseline 而非基准作者"。'),
 dict(n='SHWD', release='no_yaml(A)', protocol='no_val(A)', yolo='train_val_alias(A)',
      reported='alias(A)', ev='官方 README + mirror Reflective_vests.yaml', conf='medium',
      note='官方只有 trainval/test，无 val；官方训练脚本把 test 叫 "val"。审计自陈无法声称该镜像对 SHWD 用户有代表性。'),
 dict(n='SFCHD', release='alias(A)', protocol='no_val(A)', yolo='alias(A)',
      reported='alias(A)', ev='官方一方发布物（机器比对 _ev_sfchd_check2.py）', conf='highest',
      note='test.txt 6 行、val.txt 2475 行，test ⊆ val 且 val.txt[:6] == test.txt。审计称 "the strongest single finding"。'),
 dict(n='MAFA', release='no_val(A)', protocol='no_val(A)', yolo='unknown(?)',
      reported='alias(A)', ev='官方 CVPR PDF（pypdf 抽取）', conf='high',
      note='全文 "validation" 出现 0 次。另附一条引用更正：arXiv 1804.04017 不是 MAFA。'),
 dict(n='Mendeley face-mask', release='no_split(A)', protocol='no_split(A)',
      yolo='alias(D)', reported='unknown(?)', ev='官方数据记录 + mirror generator', conf='lowest',
      note='推导：VOC→YOLO 生成器从同一 images_dir 写 train 与 val，且不发 test 键。审计自评 "treat it as a hypothesis"。'),
 dict(n='WIDER FACE', release='independent_test(A)', protocol='test_gated(A)',
      yolo='no_test_key(A)', reported='alias(A)', ev='官方站点（GT 不发布逐字核实）+ mirror', conf='high',
      note='mirror 的 16551/4952 注释系 VOC 计数；其 val 是否为官方 val 未核实。'),
 dict(n='CrowdHuman', release='test_gated(A)', protocol='alias(A)', yolo='no_test_key(A)',
      reported='alias(A)', ev='官方论文 + mirror', conf='high',
      note='作者自己的 baseline 即为 F-B："the results are evaluated in the validation subset"。计数为二次源。'),
 dict(n='D-Fire (FireSmoke)', release='independent_test(A)', protocol='independent_test(A)',
      yolo='clean(A)', reported='unknown(?)', ev='官方 README', conf='medium',
      note='【已按 (h-1) 裁定更正】官方发布物为三个预分文件夹（train/val/test），无 yaml。'
           '审计原将 FireSmoke 族行判 "mixed" 并把 D-Fire 计入 alias 组，其唯一依据 Reflective_vests.yaml '
           '在审计 A:52 明写 "built on SHWD" → 证据不支持，族行判决应为 "D-Fire 族副本 3 distinct / 0 aliasing"。'),
]

# 已施加的更正（供输出披露）
CORRECTIONS = [
 ('(h-1)', 'D-Fire / FireSmoke 族',
  '族行 "mixed" 判据取自一条 SHWD 血统的 config（A:59 引 Reflective_vests.yaml；A:52 注明其基于 SHWD）。'
  '属 FireSmoke/D-Fire 的三个副本全部 distinct。据 3a 明文采用的"发布物层"单位，D-Fire 归干净组。'),
 ('(d-1)', 'AI-TOD / DOTA 不对称',
  '审计对含 trainval 的 AI-TOD 标 F-C，对同样含 trainval 的 DOTA v1/v2 未标。'
  '本表统一采用"发布物/协议层"单位：trainval 属用户协议注意事项，不作判决依据；两处均不改判，但 AI-TOD 因 v2 发布声明自相矛盾而为 contradictory。'),
]

# 注意：ROWS 里的键是 'yolo'；显示名写作 yolo_dist 以对应审计表的第 4 列。
# （首版误将键名写成 'yolo_dist' 导致 KeyError，已修；留此注释备查。）
UNITS = [
 ('release', '基准自身发布物层'),
 ('protocol', '官方协议层'),
 ('yolo', '通用 YOLO 分发包层（yolo_dist）'),
 ('reported', '实际报告层'),
]

ALIAS_EQUIV = {'alias', 'no_test', 'no_val', 'no_split', 'test_gated',
               'contradictory', 'no_yaml', 'train_val_alias'}


def base(v):
    return v.split('(')[0].strip()


def prov(v):
    return v[v.rfind('(') + 1:v.rfind(')')] if '(' in v else '?'


def main():
    N = len(ROWS)
    lines = []
    def w(s=''):
        lines.append(s)

    w('=' * 78)
    w('19 行 × 5 列单位标记表 —— 重算输出')
    w('生成：recompute_split_units_20260916.py（新文件；未改动 analysis/ 下任何既有文件）')
    w('=' * 78)
    w()
    w('【三种单位的定义】')
    w('  release   基准自身发布物层：官方分划产物/脚本是否提供独立留出 test')
    w('  protocol  官方协议层：官方 README/论文/网站声明的划分，且该 test 是否本地可自评')
    w('  reported  实际报告层：文献报告的数字来自哪个划分、该划分是否独立于选点')
    w('  （另有 yolo_dist = 通用 YOLO 分发包层，即审计 §1 表第 4 列所测的那一列）')
    w()
    w('【已施加的更正】')
    for code, what, why in CORRECTIONS:
        w(f'  {code}  {what}')
        w(f'      {why}')
    w()

    # ---------- 表 ----------
    w('【19 × 5 标记表】')
    hdr = f'{"#":>2}  {"benchmark":<20} {"release":<22} {"protocol":<24} {"yolo_dist":<18} {"reported":<22}'
    w(hdr)
    w('-' * len(hdr))
    for i, r in enumerate(ROWS, 1):
        w(f'{i:>2}  {r["n"][:20]:<20} {r["release"]:<22} {r["protocol"]:<24} '
          f'{r["yolo"]:<18} {r["reported"]:<22}')
    w()

    # ---------- 计数 ----------
    counts = {}
    for key, label in UNITS:
        c = collections.Counter(base(r[key]) for r in ROWS)
        counts[key] = c
        alias = sum(v for k, v in c.items() if k in ALIAS_EQUIV)
        unknown = c.get('unknown', 0)
        determinate = N - unknown
        w(f'--- 单位「{key}」({label})')
        for k, v in sorted(c.items(), key=lambda kv: -kv[1]):
            mark = ' ←alias/非独立' if k in ALIAS_EQUIV else ''
            w(f'      {v:>2}  {k}{mark}')
        w(f'      小计校验：{sum(c.values())} / {N} 行')
        w(f'      **alias/非独立 = {alias}/{N} = {100.0*alias/N:.1f}%**'
          f'（可判定行中 {alias}/{determinate} = {100.0*alias/determinate:.1f}%）'
          + (f'；unknown {unknown} 行' if unknown else ''))
        w()

    # ---------- 与审计已发表数字交叉核对 ----------
    w('【与审计文档已发表数字的交叉核对】')
    # 审计 3a 的单位是"通用分发包 config 里两键同路径"，故只取 yolo=alias 且证源为 (A) 的行；
    # Mendeley 的 alias 是 VOC→YOLO 生成器写出来的（不同单位），单列。
    l1_A = [r['n'] for r in ROWS if base(r['yolo']) == 'alias' and prov(r['yolo']) == 'A']
    l1_D = [r['n'] for r in ROWS if base(r['yolo']) == 'alias' and prov(r['yolo']) == 'D']
    a_2_19 = len(l1_A)
    a_14 = sum(v for k, v in counts['reported'].items() if k in ALIAS_EQUIV)
    a_clean_reported = counts['reported'].get('clean', 0)
    w(f'  审计 3a 字面 val == test (2/19)：本表「分发包 config 两键同路径」(A 证源) 得 {a_2_19}/{N}'
      f' — {", ".join(l1_A)} → ' + ('**复现 ✓**' if a_2_19 == 2 else '不一致 ✗'))
    if l1_D:
        w(f'     （另 {len(l1_D)} 行走 alias 由**生成器**造成，非分发包 config，不计入 3a 口径：'
          f'{", ".join(l1_D)}）')
    w(f'  审计 14/19（reported 层）：本表 reported=alias/非独立 得 {a_14}/{N}'
      f' → 与 14 的差 = {a_14 - 14:+d}（(h-1) 移除 D-Fire；DOTA v2 与 DIOR/Mendeley 的证源差异见各行 note）')
    w(f'  审计 5/19 clean（reported 层）：本表 reported=clean 得 {a_clean_reported}/{N}'
      f' → 与 5 的差 = {a_clean_reported - 5:+d}')
    w()
    w('  ⚠ 审计的 12/19 是"移出 WIDER FACE + CrowdHuman"两行手调所得，'
      '不是把某一单位一致施加于 19 行的结果；本表用一致规则重算，故数值不必相同。')
    w()

    # ---------- 决策所需 ----------
    w('【供正文采用的一组自洽数】')
    w(f'  · 字面 val == test（通用分发包 config，A 证源）：**{a_2_19}/19 = {100.0*a_2_19/N:.0f}%**'
      f' — {", ".join(l1_A)}')
    if l1_D:
        w(f'  · 另有生成器制造的 train/val 同源：**{len(l1_D)}/19**（{", ".join(l1_D)}），'
          f'口径不同，须单独表述')
    p_alias = sum(v for k, v in counts['protocol'].items() if k in ALIAS_EQUIV)
    w(f'  · 官方协议层非独立（test_gated/no_test/no_val/no_split/contradictory/alias）：'
      f'**{p_alias}/19 = {100.0*p_alias/N:.0f}%**')
    w(f'  · 实际报告层非独立：**{a_14}/19 = {100.0*a_14/N:.0f}%**'
      f'（unknown {counts["reported"].get("unknown",0)} 行）')
    w(f'  · 实际报告层干净：**{a_clean_reported}/19 = {100.0*a_clean_reported/N:.0f}%**')
    w(f'  · 求和校验：{a_14} + {a_clean_reported} + {counts["reported"].get("unknown",0)} = '
      f'{a_14 + a_clean_reported + counts["reported"].get("unknown",0)} （应为 {N}）')
    w()

    # ---------- “same directory” 四层级 ----------
    w('【"same directory" 的四层级（解 (g0)，审计只报了最窄一层）】')
    lv1 = [r['n'] for r in ROWS if base(r['yolo']) == 'alias' and prov(r['yolo']) == 'A']
    lv2 = [r['n'] for r in ROWS if base(r['yolo']) == 'train_val_alias']
    lv3 = [r['n'] for r in ROWS if base(r['reported']) == 'alias'
           and base(r['yolo']) not in ('alias', 'train_val_alias')]
    w(f'  L1 通用分发包字面 val==test：{len(lv1)} 行 — {", ".join(lv1)}')
    w(f'  L2 分发包 train==val（F-C）：{len(lv2)} 行 — {", ".join(lv2)}')
    w(f'  L3 分发包干净但报告层非独立：{len(lv3)} 行 — {", ".join(lv3)}')
    w(f'  L4 其余：{N - len(lv1) - len(lv2) - len(lv3)} 行')
    w()

    # ---------- 汇总表 ----------
    w('【每行证据类别与置信度（沿用审计自评）】')
    for i, r in enumerate(ROWS, 1):
        w(f'  {i:>2}. {r["n"]:<20} conf={r["conf"]:<8} ev={r["ev"]}')
    w()
    w('【逐行推导/更正说明】')
    for i, r in enumerate(ROWS, 1):
        w(f'  {i:>2}. {r["n"]}: {r["note"]}')
    w()
    w('END')

    text = '\n'.join(lines)
    io.open(OUT_TXT, 'w', encoding='utf-8', newline='\n').write(text + '\n')
    print(text)

    # ---------- 渲染 Markdown ----------
    md = []
    md.append('# 19 行 × 5 列单位标记表（副论文前置件）')
    md.append('')
    md.append('> 由 `analysis\\work\\recompute_split_units_20260916.py` 生成；'
              '所有百分比由本表标记机械重算，无硬编码。')
    md.append('> 建立 2026-09-16。已施加 (h-1) 裁定（D-Fire 归干净）。')
    md.append('')
    md.append('## 三种单位（正文须写明用哪一条）')
    md.append('')
    md.append('| 单位 | 定义 |')
    md.append('|---|---|')
    md.append('| **release** | 基准自身发布物层：官方分划产物/脚本是否提供独立留出 test |')
    md.append('| **protocol** | 官方协议层：官方声明的划分，且该 test 是否本地可自评 |')
    md.append('| **yolo_dist** | 通用 YOLO 分发包层（＝审计 §1 表第 4 列所测的那一列） |')
    md.append('| **reported** | 实际报告层：文献报告的数字来自哪个划分、是否独立于选点 |')
    md.append('')
    md.append('证据标记：(A) 审计明文｜(D) 由审计事实推导｜(?) 审计未表态')
    md.append('')
    md.append('## 标记表')
    md.append('')
    md.append('| # | benchmark | release | protocol | yolo_dist | reported | 证据类别 | 置信度 |')
    md.append('|---|---|---|---|---|---|---|---|')
    for i, r in enumerate(ROWS, 1):
        md.append(f'| {i} | {r["n"]} | `{r["release"]}` | `{r["protocol"]}` | '
                  f'`{r["yolo"]}` | `{r["reported"]}` | {r["ev"]} | {r["conf"]} |')
    md.append('')
    md.append('## 重算结果')
    md.append('')
    md.append('| 单位 | alias/非独立 | 可判定行中 | unknown |')
    md.append('|---|---|---|---|')
    for key, label in UNITS:
        c = counts[key]
        alias = sum(v for k, v in c.items() if k in ALIAS_EQUIV)
        unk = c.get('unknown', 0)
        md.append(f'| {key}（{label}） | **{alias}/{N} = {100.0*alias/N:.1f}%** | '
                  f'{alias}/{N-unk} = {100.0*alias/(N-unk):.1f}% | {unk} |')
    md.append('')
    md.append('## 与审计已发表数字的交叉核对')
    md.append('')
    md.append(f'- 审计 3a「字面 `val == test` **2/19**」→ 本表「分发包 config 两键同路径」(A 证源) 得 **{a_2_19}/19**，'
              + ('**复现 ✓**' if a_2_19 == 2 else '不一致 ✗'))
    if l1_D:
        md.append(f'  - 另 {len(l1_D)} 行 alias 由**生成器**造成（{", ".join(l1_D)}），非分发包 config，不计入 3a 口径')
    md.append(f'- 审计「**14/19**」→ 本表 `reported` 得 **{a_14}/19**（差 {a_14-14:+d}）')
    md.append(f'- 审计「**5/19** clean」→ 本表 `reported=clean` 得 **{a_clean_reported}/19**（差 {a_clean_reported-5:+d}）')
    md.append(f'- 审计「12/19」为两行手调所得，**非**一致单位重算；本表按一致规则重算，数值不必相同')
    md.append('')
    md.append('## 供正文采用的一组自洽数')
    md.append('')
    md.append(f'- 字面 `val == test`（通用分发包 config，A 证源）：**{a_2_19}/19 = {100.0*a_2_19/N:.0f}%** — {", ".join(l1_A)}')
    if l1_D:
        md.append(f'- 生成器制造的 train/val 同源：**{len(l1_D)}/19**（{", ".join(l1_D)}），**口径不同，须单独表述**')
    p_alias = sum(v for k, v in counts['protocol'].items() if k in ALIAS_EQUIV)
    md.append(f'- 官方协议层非独立：**{p_alias}/19 = {100.0*p_alias/N:.0f}%**')
    md.append(f'- 实际报告层非独立：**{a_14}/19 = {100.0*a_14/N:.0f}%**（unknown {counts["reported"].get("unknown",0)} 行）')
    md.append(f'- 实际报告层干净：**{a_clean_reported}/19 = {100.0*a_clean_reported/N:.0f}%**')
    md.append('')
    md.append('## "same directory" 的四层级（解 (g0)）')
    md.append('')
    md.append(f'- **L1** 通用分发包字面 `val==test`：{len(lv1)} 行 — {", ".join(lv1)}')
    md.append(f'- **L2** 分发包 `train==val`（F-C）：{len(lv2)} 行 — {", ".join(lv2)}')
    md.append(f'- **L3** 分发包干净但报告层非独立：{len(lv3)} 行 — {", ".join(lv3)}')
    md.append(f'- **L4** 其余：{N-len(lv1)-len(lv2)-len(lv3)} 行')
    md.append('')
    md.append('## 已施加的更正')
    md.append('')
    for code, what, why in CORRECTIONS:
        md.append(f'- **{code} {what}**：{why}')
    md.append('')
    io.open(OUT_MD, 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
    print()
    print(f'[written] {OUT_TXT}')
    print(f'[written] {OUT_MD}')


if __name__ == '__main__':
    main()
