# -*- coding: utf-8 -*-
"""r45: recompute the Tier-2 multiplicity issue before believing the reviewer.

The blind reviewer (glm53flash) claims that none of the 13 Tier-2 cell p-values survives
Benjamini-Hochberg at q = 0.05. The project's own rule is that any statistic taken from
someone else is recomputed before it is written down, so this reads the 13 p-values straight
out of the supplementary's Table S8 and runs BH on them, printing every intermediate step.

Read-only.
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SUP = r'E:\workplace\P2_Supplementary_English_v0.1.md'

SUPERS = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
          '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-'}


def parse_p(s):
    """Parse '0.0173' or '1.3×10⁻⁸' (the notation the table uses for small p).

    r53 note: this function exists because the first version of this script called float() on the
    cell and SKIPPED the row when that failed -- so when two rows were later written in exponent
    notation, BH was recomputed over 11 of 13 cells and still printed a confident "none survives".
    An unparsable p is now a hard error, never a silent skip.
    """
    s = s.strip().replace('~', '').replace('<', '').replace('*', '')
    if '×10' in s:
        mant, _, exp = s.partition('×10')
        exp = ''.join(SUPERS.get(c, c) for c in exp)
        return float(mant) * (10.0 ** int(exp))
    return float(s)


def main():
    t = io.open(SUP, encoding='utf-8').read().split('\n')
    # Table S8 = the 13-cell Δgap table: | corpus | n | M_val b/s | M_test b/s | Δgap | p |
    start = None
    for i, l in enumerate(t):
        if l.startswith('### Table S8 '):
            start = i
            break
    if start is None:
        sys.exit('!! 找不到 Table S8')

    rows = []
    for l in t[start:start + 20]:
        if not l.strip().startswith('|'):
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if len(cells) < 6 or cells[0].startswith('---') or cells[0] == 'Cell':
            continue
        try:
            p = parse_p(cells[5])
        except ValueError:
            sys.exit('!! Table S8 row %r has an unparsable p value %r -- refusing to recompute '
                     'over a silently reduced table' % (cells[0], cells[5]))
        rows.append((cells[0], cells[1], p))
    if len(rows) != 13:
        sys.exit('!! Table S8 应有 13 个 Δgap 单元格，读到 %d 个 —— 表被改过或解析出错，'
                 '在弄清之前不许拿这个 BH 结果' % len(rows))

    print('=' * 74)
    print('Table S8 的 %d 个 Δgap 单元格（p 值取自表内，原样）' % len(rows))
    print('=' * 74)
    for name, n, p in rows:
        print('  %-16s n=%-3s p=%s' % (name, n, p))

    m = len(rows)
    ordered = sorted(rows, key=lambda r: r[2])
    print('\nBH(q=0.05) 复算：m = %d，临界线 i/m*q' % m)
    print('  %-16s %-10s %-10s %-12s %s' % ('cell', 'p', 'rank i', 'i/m*q', 'p <= line ?'))
    survives = []
    for i, (name, n, p) in enumerate(ordered, 1):
        line = i / m * 0.05
        ok = p <= line
        if ok:
            survives.append(name)
        print('  %-16s %-10s %-10d %-12.5f %s' % (name, p, i, line, 'YES' if ok else 'no'))
    print('\n存活：%s' % (survives or 'none'))
    print('未校正下 p<0.05 的：%s' % [n for n, _, p in rows if p < 0.05])
    print()
    print('结论：%s' % ('复算证实审稿人 —— 13 格在 BH(q=0.05) 下无一存活'
                       if not survives else '有格子存活，审稿人说法不成立：%s' % survives))


if __name__ == '__main__':
    main()
