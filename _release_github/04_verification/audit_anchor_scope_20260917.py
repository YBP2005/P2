# -*- coding: utf-8 -*-
"""r48: audit the anchors themselves — the shared lessons library's 02 §1① failure mode.

Their finding: an anchor named "headroom sign law in conclusion" matched a sentence that
only exists in §1, so it never checked the conclusion at all; nine anchors named "abstract …"
were implemented as whole-document searches, two of which had long since stopped existing in
the abstract while still reporting PASS.

So: for every claim anchor whose description names a section (§N or §N.M), find where its
regex actually matches in the manuscript, and report any anchor whose match sits outside the
section it names.  Read-only; it changes no anchor and no text.

Conscious scope: anchors that are *meant* to be document-wide (coverage, reference count,
graphical-abstract size, the declared-count guard) name no section and are skipped.
"""
import ast
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
AUDIT = os.path.join(W, 'work', 'audit_anchors_fupaper.py')
ENG = os.path.join(W, 'P2_English_v0.1.md')


def anchors_from_source(path):
    """(code, description, pattern) for every string-literal tuple in CLAIMS."""
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == 'CLAIMS':
                for elt in getattr(node.value, 'elts', []):
                    parts = []
                    for e in getattr(elt, 'elts', []):
                        if isinstance(e, ast.Constant) and isinstance(e.value, str):
                            parts.append(e.value)
                        else:
                            parts.append(None)
                    if len(parts) >= 4 and parts[0] and parts[3]:
                        out.append((parts[0], parts[1] or '', parts[3]))
    return out


def sections(text):
    """Ordered list of (offset, id) for every heading."""
    out = []
    for m in re.finditer(r'(?m)^#{2,4}\s+(\d+(?:\.\d+)*)[.\s]', text):
        out.append((m.start(), m.group(1)))
    return out


def enclosing(secs, pos):
    best = None
    for off, sid in secs:
        if off <= pos:
            best = sid
        else:
            break
    return best


def main():
    eng = io.open(ENG, encoding='utf-8').read()
    secs = sections(eng)
    anchors = anchors_from_source(AUDIT)
    print('=' * 78)
    print('锚点自查（02 §1①）：凡描述里指名小节的锚点，它的正则实际在该小节内匹配吗？')
    print('=' * 78)
    print('  共解析到 %d 条 CLAIMS 锚点；正文小节 %d 个\n' % (len(anchors), len(secs)))
    named, ok, outside, unmatched = 0, 0, [], []
    for code, desc, pat in anchors:
        m = re.search(r'§\s?(\d+(?:\.\d+)*)', desc)
        if not m:
            continue
        named += 1
        want = m.group(1)
        try:
            hits = [x.start() for x in re.finditer(pat, eng, re.I)]
        except re.error as e:
            outside.append((code, desc, '正则无法编译：%s' % e, []))
            continue
        if not hits:
            unmatched.append((code, desc, pat))
            continue
        where = {enclosing(secs, h) for h in hits}
        if want in where or any(x == want for x in where):
            ok += 1
        else:
            outside.append((code, desc, want, sorted(x or '?' for x in where)))
    print('  描述里指名小节的锚点 %d 条：**在被指小节内命中 %d 条**' % (named, ok))
    if unmatched:
        print('\n  ✗ 一条都没命中（描述指名了小节，但正则在全篇找不到）：')
        for code, desc, pat in unmatched:
            print('      %-6s %s' % (code, desc[:66]))
            print('             pattern: %s' % pat[:90])
    if outside:
        print('\n  ⚠ 命中的位置不在被指小节内（02 §1① 的形态）：')
        for code, desc, want, where in outside:
            print('      %-6s 描述指 §%s，实际命中于 %s' % (code, want, where))
            print('             %s' % desc[:70])
    if not unmatched and not outside:
        print('\n  ⇒ 未发现"名字指 A、实际查 B"的锚点')
    print('\n  说明：本自查只覆盖描述里带 § 的锚点；文档级锚点（覆盖率、条数、图形摘要尺寸'
          '等）本来就不指名小节。')
    return 0 if (not unmatched and not outside) else 1


if __name__ == '__main__':
    sys.exit(main())
