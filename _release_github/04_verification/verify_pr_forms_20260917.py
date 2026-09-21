# -*- coding: utf-8 -*-
"""
从 **D 侧已存档的官方/转载证据**里抽取 PR 的形式要求（不再重新抓取；官方页全通道 403）。
产出 `E:\\workplace\\PR形式要求_核实_20260917.md`：每一条都注明**取自哪个存档文件 + 原文片段 + 文件哈希**。
抽不到的写"未取到"，不推断。
"""
import hashlib, io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
EV = r'D:\deepseek\analysis\pr_guideline_evidence'
OUT = r'E:\workplace\PR形式要求_核实_20260917.md'


def load(name):
    p = os.path.join(EV, name)
    if not os.path.exists(p):
        return None, None, None
    b = io.open(p, 'rb').read()
    return b.decode('utf-8', 'replace'), hashlib.sha256(b).hexdigest()[:16], len(b)


rep = ['# PR（Pattern Recognition）形式要求 —— 核实报告（2026-09-17）', '']
rep.append('> **为什么做**：这是 P2 §13.3 缺口表里**唯一还标"未核"**的一项。')
rep.append('> **方法**：**官方 Guide for Authors 页全通道 403**（D 侧 2026-09-16 已逐通道留证：'
           '`PR页数限制_附录是否计入_核实_20260916.md` §1）。')
rep.append('> 故本报告**复用 D 侧已存档的转载原文**（逐字转载页），**不重新抓取**、不做推断。')
rep.append('> **纪律**：每条都注明**取自哪个存档文件 + 原文片段 + 该文件哈希**；抽不到就写"未取到"。')
rep.append('')

# 存档清单与来源
prov, ph, pn = load('PROVENANCE.json')
if prov:
    rep.append('## 0. D 侧存档的来源说明（`pr_guideline_evidence/PROVENANCE.json`）')
    rep.append('')
    rep.append('```json')
    rep.append(prov.strip()[:1800])
    rep.append('```')
    rep.append('')
    rep.append('（该文件 sha256[:16] = `%s`，%d B）' % (ph, pn))
    rep.append('')

SRC = 'probe_http___apps_lib_whu_edu_cn_ensci_show_tg.txt'
txt, h, n = load(SRC)
if txt is None:
    sys.exit('!! 缺转载原文存档 %s' % SRC)
flat = re.sub(r'\s+', ' ', txt)
rep.append('## 1. 逐条抽取（**转载原文**：`%s`，sha256[:16] = `%s`，%d B）' % (SRC, h, n))
rep.append('')

ITEMS = {
    'Highlights（是否要求 / 数量 / 字数）': [r'Highlights?[^.]{0,200}', r'3 to 5[^.]{0,120}', r'85 characters[^.]{0,80}'],
    'Graphical abstract': [r'[Gg]raphical abstract[^.]{0,200}'],
    '摘要长度': [r'[Aa]bstract[^.]{0,40}(maximum|max\.?)[^.]{0,120}', r'[Aa]bstract[^.]{0,60}\d+\s*words[^.]{0,60}'],
    '关键词数量': [r'[Kk]eywords?[^.]{0,160}'],
    'CRediT 作者贡献': [r'CRediT[^.]{0,240}'],
    'Declaration of interest / 竞争利益': [r'[Dd]eclaration of [Ii]nterest[^.]{0,240}', r'competing interest[^.]{0,200}'],
    'Data availability（数据可得性声明）': [r'[Dd]ata availability[^.]{0,240}', r'research data[^.]{0,180}'],
    '页数 / 版面（单栏、双倍行距、编号页）': [r'single column[^.]{0,160}', r'double[- ]spac\w+[^.]{0,160}', r'numbered pages[^.]{0,160}'],
    'Cover letter': [r'[Cc]over letter[^.]{0,180}'],
    'Artwork / 图件规格（dpi 等）': [r'\bdpi\b[^.]{0,160}', r'[Aa]rtwork[^.]{0,180}'],
    'AI 使用声明': [r'(?i)\bAI\b[^.]{0,40}(declar|disclos)[^.]{0,160}'],
}
hit_n = 0
for label, pats in ITEMS.items():
    got = []
    for p in pats:
        m = re.search(p, flat)
        if m:
            s = m.group(0).strip()
            if s not in got:
                got.append(s)
    rep.append('### %s' % label)
    rep.append('')
    if got:
        hit_n += 1
        for g in got[:3]:
            rep.append('> %s' % g[:400])
    else:
        rep.append('**未取到**（转载原文中未匹配到；不推断）')
    rep.append('')

rep.append('## 2. 来源更正记录：`whu` 转载存档不是 PR 的指南（r39 更正，本节是它的归属）')
rep.append('')
rep.append('> **本节为什么必须由本脚本一起写出**：本脚本是 '
           '`E:\\workplace\\PR形式要求_核实_20260917.md` 的**唯一写入者**。'
           'r39 曾把下面这条更正**手工补进该文件**（v0.2 §1 首段），但本脚本每次运行都会把文件重写成'
           '上面的 v0.1 抽取，于是**更正被覆盖掉**，`work/verify_submission_pack_20260917.py` 的'
           '第 8 组（"形式要求核实件的来源更正必须留痕"）每次都判 FAIL。'
           'r54i 起把这条更正**并入生成逻辑**，让它不可能再被自己的重写冲掉（记录本身不是重写的产物，'
           '是必须随重写一起保留下来的结论）。')
rep.append('')
rep.append('**核实结论**：§1 所用的转载原文 `%s`（sha256[:16] `%s`，%d B）是 '
           '**THE VETERINARY JOURNAL（ISSN 1090-0233）** 的投稿指南，**不是 PR 的指南**。'
           % (SRC, h, n))
rep.append('')
rep.append('**证据**（`work/probe_pr_whu_journal_20260917.py`，只读）：该存档全文 '
           '`Pattern Recognition` 出现 **0 次**、`0031-3203` **0 次**；页眉为 '
           '**VETERINARY JOURNAL / 1090-0233**；联系邮箱 `healthpermissions@elsevier.com`；'
           '体例为 `Introduction, Materials and methods, Results, Discussion, Conclusions`。')
rep.append('')
rep.append('⇒ **§1 里由该存档抽出的四条要求作废，不得用于 PR 投稿**（200 词摘要、五个关键词、'
           '单倍行距例外、dpi 300/500/1000）。它们**不属于 PR**，正文与投稿前件**不得**按这四条'
           '执行；上面 §1 的抽取保留原样是为了留痕，不代表它们成立。')
rep.append('')
rep.append('**错因如实写下**：当初只核了"是不是 Elsevier 的指南"，**没核"是不是 PR 的指南"**——'
           '是核实的漏项，不是来源的问题；该存档对其他用途仍有效。')
rep.append('')

rep.append('## 3. 小结与对 P2 的动作')
rep.append('')
rep.append('| 项 | 状态 | P2 的动作 |')
rep.append('|---|---|---|')
rep.append('| 页数口径（20–35 编号页；附录是否计入） | **已核实到实践层面**（D 侧四项证据；官方无明文） | §13.3 已按此改写 |')
rep.append('| 其余形式件（按上表逐条） | 见上表 | 按抽到的条款补齐；**未抽到的仍标"未核"，不编** |')
rep.append('')
rep.append('*本报告由 P2 侧生成（`work/verify_pr_forms_20260917.py`），2026-09-17。*'
           '**官方页全通道 403 这一事实本身也已记录**，故凡引用都指向转载存档，不做官方归属声明。')

io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
b = io.open(OUT, 'rb').read()
print('报告已写：%s' % OUT)
print('md5 %s size %d' % (hashlib.md5(b).hexdigest(), len(b)))
print('抽到内容的类别：%d / %d' % (hit_n, len(ITEMS)))
for label, pats in ITEMS.items():
    ok = any(re.search(p, flat) for p in pats)
    print('   %-42s %s' % (label, '有' if ok else '未取到'))
# r54i: this suite both generates the report and checks that the r39 source correction survived
# into it.  The verdict line is about THAT check (a stated obligation), not about how many
# clauses were extracted -- "未取到" is a legitimate outcome and is printed above, not hidden.
# r54i: the correction record moved into this generator's own output (section 2), so it is
# checked HERE, at the producer, as well as in work/verify_submission_pack_20260917.py.
# r54m: the audit anchor X46 requires a specific obligation, not just the word '作废'.
# Checking the full phrase here means the generator itself can no longer drop it.
lost = [s for s in ('VETERINARY JOURNAL', '作废', '作废，不得用于 PR 投稿')
        if s not in io.open(OUT, encoding='utf-8').read()]
print('来源更正留痕（VETERINARY JOURNAL / 作废 / 作废，不得用于 PR 投稿）：%s'
      % ('ok' if not lost else 'FAIL %s' % lost))
print('失败 %d 项' % len(lost))
print('ALL PASS' if not lost else 'FAILED: 来源更正未写入 %s' % lost)
sys.exit(0 if not lost else 1)
