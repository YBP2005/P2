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
    m = re.search(r'(Four|Three|Five) (?:evidence )?tables are (?:also )?printed \*\*here\*\*'
                  r'(?: as well| too)?', fa)
    if not m:
        fails.append('找不到"Four evidence tables are printed"句')
        print('      FAIL 找不到"printed here as well"的表数声明')
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

    m = re.search(r'all (five|four|six) figures', fa)
    if m:
        stated = {'four': 4, 'five': 5, 'six': 6}[m.group(1)]
        in_art = {int(x) for x in re.findall(r'Fig\. S(\d+)', fa)}
        in_sup = {int(x) for x in re.findall(r'\*\*Fig\. S(\d+)\.\*\*', fs)}
        ok = (stated == len(in_sup)) and (in_art == in_sup)
        print('   %-4s 图数：声明 %d、正文列出 %s、补充材料 §S9 实有 %s'
              % ('ok' if ok else 'FAIL', stated, sorted(in_art), sorted(in_sup)))
        if not ok:
            fails.append('figure count %d vs art %s vs sup %s' % (stated, sorted(in_art),
                                                                  sorted(in_sup)))
    else:
        fails.append('找不到图数声明')
        print('      FAIL 找不到"all five figures"句')

    print()
    for n in notes:
        print('   注：%s' % n)
    print('失败 %d 项' % len(fails))
    print('ALL PASS' if not fails else 'FAILED: ' + '; '.join(fails[:6]))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
