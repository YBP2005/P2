# -*- coding: utf-8 -*-
"""r48: the paired guards the shared lessons library recommends (02 §5, §6).

02 §5 lists guards that should exist in pairs.  Three were missing here and are built now:

  * **named artifacts must resolve.**  The Declarations promise that "six checkers (`a`, `b`,
    …) can be run by the authors, and by any holder of the archive" — a claim about *files*.
    Every backticked filename in the submission artifacts is resolved against the two trees
    that make up this project's material (the workspace and the read-only archive), with
    declared-external classes for things that are legitimately neither.
  * **placeholders must not reach a submission.**  TODO/TBD/`__X__`/"to be completed" fail on
    the submission forms; the working article may carry the declared CRediT placeholder.
  * **retired claims must not come back.**  §5.4 retracted a sentence, the audit's 14/19 was
    replaced, two anchor counts were wrong, a page figure was an error.  Each carries its
    reason and its scope (the supplement legitimately *quotes* 14/19 while recording the
    correction — scoping a guard is part of writing it).

02 §6 adds "a label is itself a claim": when a sentence states a count about our own content
(six checkers, 23 remaining tables, five figures), the count is recomputed here.

NOTE ON SCOPING — the first version of this file reported 81 failures, of which 80 were its
own over-claiming (third-party framework files, Kaggle log names, archive-relative paths, a
glob pattern, the two ledger files whose ABSENCE is the disclosed defect, and the
`__unstated__`/`___base___` naming conventions inside extracted file names).  That is the
library's 02 §1① failure mode, and it is why each declared class below carries its reason.
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
W2 = r'D:\deepseek'                     # read-only sibling tree (the archive)
ART = os.path.join(W, 'P2_English_v0.1.md')
BLIND = os.path.join(W, 'P2_English_submission_blind_v1.md')
SUP = os.path.join(W, 'P2_Supplementary_English_v0.1.md')

# ---------------------------------------------------------------------------------------
# Classes of named file that legitimately resolve elsewhere, or do not need to resolve.
# Each is a pattern + a reason; nothing is excused without one.
# ---------------------------------------------------------------------------------------
EXTERNAL_CLASSES = [
    (r'^-', 'third-party training logs (Kaggle/GitHub): the Declarations state they are NOT '
            'redistributed — hashes and source pointers only'),
    (r'^[a-z0-9_.-]+__.*\.csv$', 'third-party log inside a corpus directory (our naming)'),
    (r'^(tools/|datasets/|annotations/)', 'file inside a third-party framework or dataset'),
    (r'^(trainer\.py|runtime\.yml|results\.csv|best\.pt|last\.pt|coco\.py)$',
     'file created by the training framework at run time, not ours to archive'),
    (r'^image_info_test2017\.json$', 'COCO metadata file, not redistributed'),
    (r'\*', 'a glob pattern, not a filename'),
    (r'^_r10_(final_stats|stats_0403)\.txt$',
     'the ledger files whose ABSENCE is the disclosed defect (§10 row 1)'),
    (r'^PROVENANCE\.md$|^build_provenance\.py$',
     'archived in the sibling tree (eval_validity/published_logs, analysis/work)'),
    (r'^python\s', 'a command line, not a filename'),
    (r'_20p(_3way)?\.yaml$',
     'dataset configs archived under eval_validity/yamls/, named after their origin path'),
    (r'^(eval_validity|analysis|work|xframe|_xframe)/', 'archive-relative path'),
    (r'^[a-z0-9_]+\.(json|yaml|yml)$', 'a file inside the corpora, not a standalone artifact'),
]

# Statements that must not reappear, with the artifact(s) they apply to and the reason.
RETIRED = [
    (r'(?<![\d.,])14/19(?![\d.,])', ('art', 'blind'),
     '旧计数（审计口径）已被机械重算取代；正文只许用 12/19 与 13/19。'
     '**补充材料例外**：它在更正记录里必须引用这个旧值才能说明改了什么'),
    (r'(?<![\d.,])227(?![\d.,])', ('art', 'blind', 'sup'),
     '补充材料曾把锚点数写成 227；现行数字由 X82 守卫'),
    (r'(?<![\d.,])481(?![\d.,])', ('art', 'blind', 'sup'),
     '伴生论文曾把我们的锚点数写成 481（跨文件写死数字的实例）'),
    (r'34\.7', ('art', 'blind', 'sup'),
     '页数曾报 34.7（用了别人的词密度）；现行口径是实测页数'),
    (r'understates rather than manufactures', ('art', 'blind', 'sup'),
     '§5.4 撤回的旧措辞（方向并非单一）'),
    (r'S1–S5', ('art', 'blind', 'sup'), '补充材料旧的节范围（现为 S1–S9）'),
]


def declared_external(name):
    base = os.path.basename(name.replace('\\', '/'))
    for pat, why in EXTERNAL_CLASSES:
        if re.search(pat, name) or re.search(pat, base):
            return why
    return None


def find_anywhere(base):
    for root in (W, W2):
        if not os.path.isdir(root):
            continue
        for _dirpath, _dirs, files in os.walk(root):
            if base in files:
                return True
    return False


def flatten(text):
    """Collapse markdown line wrapping so a pattern can span a wrapped line."""
    return re.sub(r'\s+', ' ', text)


def main():
    art = io.open(ART, encoding='utf-8').read()
    blind = io.open(BLIND, encoding='utf-8').read()
    sup = io.open(SUP, encoding='utf-8').read()
    texts = {'art': art, 'blind': blind, 'sup': sup}
    fails, notes = [], []
    print('=' * 78)
    print('配对守卫（02 §5/§6）：点名文件 / 占位符 / 退役主张 / 标签自称的数')
    print('=' * 78)

    # ---- 1. named files resolve ----------------------------------------------------
    print('\n[1] 文中点名的文件是否可解析（两棵树：工作区 + 只读归档）')
    named = set()
    for t in texts.values():
        for m in re.finditer(r'`([^`\n]+)`', t):
            s = m.group(1).strip()
            if re.search(r'\.(py|md|txt|csv|json|ya?ml|pt|png|html)$', s):
                named.add(s)
    missing, excused = [], 0
    for n in sorted(named):
        if find_anywhere(os.path.basename(n.replace('\\', '/'))):
            continue
        why = declared_external(n)
        if why:
            excused += 1
            continue
        missing.append(n)
    print('   点名 %d 个；可解析或已声明 %d 个；**未解析且未声明 %d 个**'
          % (len(named), len(named) - len(missing), len(missing)))
    for n in missing:
        print('      FAIL 无法解析：%s' % n)
        fails.append('unresolved file %s' % n)
    notes.append('%d 个走"已声明外部/不需解析"的类别（第三方日志、框架文件、归档相对路径、glob）' % excused)

    # ---- 2. placeholders -----------------------------------------------------------
    # Fenced blocks are stripped first: they contain verbatim third-party source, where a
    # token such as `os.path.realpath(__file__)` is code, not an unfilled placeholder.  The
    # first version of this check flagged exactly that.
    print('\n[2] 占位符（独立 __WORD__ 形式；先剔除围栏代码块——那里是逐字证据，不是占位）')
    PH = r'(?<![A-Za-z0-9_])__[A-Za-z][A-Za-z0-9_]*__(?![A-Za-z0-9_])|\bTODO\b|\bTBD\b|\bFIXME\b|to be completed|\u5f85\u8865|\bXXX\b'

    def prose_only(t):
        return re.sub(r'(?s)```.*?```', ' ', t)

    for label, key, allow in (('匿名投稿形态', 'blind', False), ('英文补充材料', 'sup', False),
                              ('工作形态', 'art', True)):
        body = prose_only(texts[key])
        hits = [(body[:m.start()].count('\n') + 1, m.group(0))
                for m in re.finditer(PH, body, re.I)]
        if hits and allow:
            print('   ok   %s：%d 处占位符，**已声明**为 CRediT 待作者名单（且不进投稿件）'
                  % (label, len(hits)))
        elif hits:
            for ln, what in hits[:5]:
                print('      FAIL %s 第 %d 行：%r' % (label, ln, what))
                fails.append('%s placeholder %s' % (label, what))
        else:
            print('   ok   %s：无占位符' % label)

    # ---- 3. retired claims ---------------------------------------------------------
    print('\n[3] 退役主张（按件限定作用域）')
    for pat, scope, why in RETIRED:
        bad = [lab for lab in scope if re.search(pat, texts[lab])]
        if bad:
            for lab in bad:
                print('      FAIL %-6s 仍出现 /%s/' % (lab, pat))
            fails.append('retired %s in %s' % (pat, bad))
        else:
            print('   ok   /%s/ 在 %s 中已消失 —— %s' % (pat, '/'.join(scope), why[:44]))

    # ---- 4. label counts (recomputed) ----------------------------------------------
    print('\n[4] 标签自称的数量（重算比对；先合并折行）')
    fa, fb, fs = flatten(art), flatten(blind), flatten(sup)

    m = re.search(r'(\w+) checkers \(([^)]*)\)', fb)
    if not m:
        fails.append('找不到 "N checkers (...)" 句')
        print('      FAIL 找不到 checkers 句')
    else:
        w2n = {'six': 6, 'seven': 7, 'eight': 8}
        stated = w2n.get(m.group(1), None) or (int(m.group(1)) if m.group(1).isdigit() else None)
        listed = re.findall(r'`([^`]+)`', m.group(2))
        ok = stated == len(listed)
        print('   %-4s checkers 句：声明 %s、实列 %d %s'
              % ('ok' if ok else 'FAIL', stated, len(listed),
                 '' if ok else '(不自洽)'))
        if not ok:
            fails.append('checkers count %s vs %d' % (stated, len(listed)))
        for name in listed:
            if not find_anywhere(os.path.basename(name)) and not declared_external(name):
                print('      FAIL checkers 句点名但不存在的文件：%s' % name)
                fails.append('checker file missing: %s' % name)

    # The article states "**Four evidence tables are printed here as well**" and "all five
    # figures" — those are the counts it actually claims, so those are the ones recomputed.
    # (An earlier version of this check looked for a "23 remaining moved tables" sentence that
    # the inventory does not contain: it had been replaced during the r46 rewrite.  Checking
    # for a sentence that is not there is not a guard, it is a false alarm.)
    #
    # r54v: the inventory was compressed for the page limit and the sentence now reads
    # "Four tables are printed **here** too, because each carries a headline number to check".
    # The check follows the claim, not one particular wording: the number-word prefix and the
    # word "printed" are what carry the claim (how many tables the article says it prints).
    # 2026-09-26（B3）：这句声明随清单一节**搬进了补充材料**，措辞也由 `printed **here**`
    #   改为 `printed **in the article**`（"here" 在补充材料里指代会反）⇒ 改在 `sup` 上找。
    #   ⚠ 用未折行的 `sup`，不能用 `fs`（flatten 过的，行内措辞仍可匹配但保持一致性）。
    #   **被比对的"实际有几张表"仍在正文**（`fa` 的表题）—— 那半没搬。
    m = re.search(r'(Four|Three|Five) (?:evidence )?tables are (?:also )?printed '
                  r'\*\*in the article\*\*(?: as well| too)?', sup)
    if not m:
        fails.append('找不到"Four evidence tables are printed"句')
        print('      FAIL 找不到"printed in the article"的表数声明（补充材料前置）')
    else:
        stated = {'Three': 3, 'Four': 4, 'Five': 5}[m.group(1)]
        captions = {int(x) for x in re.findall(r'\*\*Table (\d+)\.\*\*', fa)}
        listed = set()
        for mm in re.finditer(r'\| \*\*Tables? (S[\dS\u2013\-,\s]+?)\*\* \|', fa):
            for part in re.split(r',', mm.group(1)):
                part = part.strip()
                rng = re.match(r'S(\d+)\s*[\u2013-]\s*S(\d+)$', part)
                if rng:
                    listed.update(range(int(rng.group(1)), int(rng.group(2)) + 1))
                elif re.match(r'^S\d+$', part):
                    listed.add(int(part[1:]))
        ok = stated == len(captions)
        print('   %-4s 正文印出的表数：声明 %d、实际图题 %d 个 %s'
              % ('ok' if ok else 'FAIL', stated, len(captions), sorted(captions)))
        if not ok:
            fails.append('article table count %d vs captions %d' % (stated, len(captions)))
        total_moved = len(listed) + len(captions)
        print('       附表：清单列出的"仍在补充材料" %d 张 + 正文印出 %d 张 = %d 张'
              % (len(listed), len(captions), total_moved))

    # 2026-09-26（A10 随搬图一并改；用户裁定"守卫按同一逻辑改"）：原判据靠正文里一句
    #   "all N figures" 的声明。搬图后该句已改为 "four of the six figures are printed here"
    #   ⇒ 改为**两段各自数一遍再互相交叉**：正文**内嵌** Fig. 1–4、清单列出补充材料余下的
    #   Fig. S1–S2、§S9 图题实有 == 清单所列。三者任一不符即 FAIL（保护未减，对象换了）。
    emb = {int(x) for x in re.findall(r'!\[Fig\. (\d+)\]', fa)}
    # r73（B3）：清单一节已移入补充材料 ⇒ `listed` 从**补充材料**读。
    #   ⚠ 必须用未折行的 `sup`，不能用 `fs`（`fs` 是 flatten() 折行后的，行锚匹配不上）。
    listed = {int(x) for x in re.findall(r'\*\*Fig\. S(\d+)\*\* \|', sup)}
    in_sup = {int(x) for x in re.findall(r'\*\*Fig\. S(\d+)\.\*\*', fs)}
    ok = (emb == {1, 2, 3, 4}) and (in_sup == {1, 2}) and (listed == in_sup)
    print('   %-4s 图：正文内嵌 %s、清单列出补充材料 %s、§S9 图题实有 %s'
          % ('ok' if ok else 'FAIL', sorted(emb), sorted(listed), sorted(in_sup)))
    if not ok:
        fails.append('figures: art-embedded %s vs inventory %s vs sup %s'
                     % (sorted(emb), sorted(listed), sorted(in_sup)))

    # 2026-09-26（r70，A9）：**表级一致性检查**。A9 的残余不是"矛盾没闭合"（S20 已改成 n = 10），
    #   而是**没有一条机器检查**把"正文 Table 4 与补充材料 Table S20 的同一格"锁在一起 ——
    #   上一轮 D1 之所以能悄悄留着旧值，就是因为它不检查这个。
    #   §S4 那个逐字嵌入件里的 `aitod20 base 1 … −0.377` **是有意保留的旧快照**（已在 S20 下加注），
    #   故本条**只比 Table 4 vs Table S20**，不比 §S4。
    def _cells(txt, cell, arm):
        """把 `| cell | arm | ... |` 那一行的**全部单元格**取出来（去 `**` 与首尾空白）。"""
        for m in re.finditer(r'(?m)^\|\s*%s\s*\|\s*%s\s*\|([^\n]*)$' % (cell, arm), txt):
            return [c.replace('**', '').strip()
                    for c in (m.group(0).strip().strip('|').split('|'))]
        return None
    # ★ 用 `art`/`sup`（**未折行**原文），不能用 `fa`/`fs` —— 那两个是 flatten() 折行合并后的文本，
    #   行锚 `^\|…$` 在它们上面永远匹配不上（第一版就是这么假红的）。
    a4, s20 = _cells(art, 'aitod20', 'baseline'), _cells(sup, 'aitod20', 'baseline')
    ok_tab = (a4 is not None) and (a4 == s20)
    print('   %-4s 表级一致：正文 Table 4 `aitod20`=%s / 补充 Table S20=%s'
          % ('ok' if ok_tab else 'FAIL', a4, s20))
    if not ok_tab:
        fails.append('table-level: Table 4 aitod20 %s vs Table S20 %s' % (a4, s20))
    # ★ 阴性对照：把正文那一行换成**上一轮的旧值**，检查器必须报不一致。
    #   没有这一步，"表级一致"就只是印出来的两个字，不是检查。
    if a4 is not None:
        doctored = art.replace(''.join(['| aitod20 | baseline | **10** | **+0.766** | **−0.218** |']),
                              '| aitod20 | baseline | **1** | **+0.786** | **−0.377** |', 1)
        ctl = _cells(doctored, 'aitod20', 'baseline')
        ctl_ok = (ctl is not None) and (ctl != s20)
        print('   %-4s 阴性对照：把正文该行换成旧值后，检查器报不一致 = %s'
              % ('ok' if ctl_ok else 'FAIL', ctl_ok))
        if not ctl_ok:
            fails.append('table-level check has no negative control (it cannot fail)')

    print()
    for n in notes:
        print('   注：%s' % n)
    print('失败 %d 项' % len(fails))
    print('ALL PASS' if not fails else 'FAILED: ' + '; '.join(fails[:6]))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
