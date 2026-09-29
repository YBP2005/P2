# -*- coding: utf-8 -*-
"""Second-coding agreement statistics for the 19 x 4 marking table (2026-09-27).

Read-only on the manuscript.  Parses the PRINTED coding from the published English
supplementary (the §S1 marking table inside its fenced block) and the SECOND coding from
work/second_coding_20260927.csv, then recomputes every statistic from those two sources:

  * Cohen's kappa on the decision scale (the printed counting distinctions) per unit and
    overall over the 76 judgments, with large-sample 95% intervals;
  * the same under two unknown-handling conventions: (A) unknown as a category,
    (B) cells where either coding is unknown dropped;
  * exact-mark agreement, and kappa on the literal marks;
  * the disagreement cells themselves.

No statistic is hard-coded; nothing is written except the report file.
"""
import collections
import csv
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
SUP = os.path.join(W, 'P2_Supplementary_English_v0.1.md')
CSV = os.path.join(W, 'work', 'second_coding_20260927.csv')
OUT = os.path.join(W, 'work', 'kappa_computed_20260927.txt')

UNITS = ['release', 'protocol', 'yolo_dist', 'reported']
ALIAS_EQUIV = {'alias', 'no_test', 'no_val', 'no_split', 'test_gated',
               'contradictory', 'no_yaml', 'train_val_alias'}


def base(mark):
    return mark.strip().strip('`').split('(')[0].strip()


def prov(mark):
    m = mark.strip().strip('`')
    return m[m.rfind('(') + 1:m.rfind(')')] if '(' in m else '?'


def category(mark):
    if mark in ALIAS_EQUIV:
        return 'non_ind'
    if mark in ('independent_test', 'clean'):
        return 'clean'
    if mark in ('no_test_key', 'unknown', 'n_a'):
        return mark
    raise ValueError('unmapped mark: %r' % mark)


def parse_printed():
    """The printed 19x4 marks from §S1's fenced marking table."""
    text = io.open(SUP, encoding='utf-8').read()
    fence = re.search(r'```text\n(.*?)\n```', text, re.S)
    assert fence, '§S1 fenced block not found'
    block = fence.group(1)
    start = block.index('## Marking table')
    rows = {}
    for line in block[start:].splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|', line)
        if not m:
            continue
        cells = [c.strip() for c in line.split('|')]
        # cells: '', '#', benchmark, release, protocol, yolo_dist, reported, ev, conf, ''
        n = int(cells[1])
        rows[n] = {'benchmark': cells[2],
                   'marks': {u: cells[3 + i] for i, u in enumerate(UNITS)}}
    assert len(rows) == 19, 'expected 19 printed rows, got %d' % len(rows)
    return rows


def parse_second():
    rows = {}
    with io.open(CSV, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            rows[int(r['row'])] = {'benchmark': r['benchmark'],
                                   'marks': {u: r[u].strip() for u in UNITS},
                                   'note': r['note']}
    assert len(rows) == 19, 'expected 19 second-coding rows, got %d' % len(rows)
    return rows


def kappa_cm(cm):
    """Cohen's kappa from a confusion matrix {coder1: {coder2: count}}; SE and 95% CI."""
    n = sum(cm[a][b] for a in cm for b in cm[a])
    p0 = sum(cm[a][a] for a in cm) / n
    me = {a: sum(cm[a].values()) for a in cm}
    mo = {b: sum(cm[a].get(b, 0) for a in cm) for b in {b for a in cm for b in cm[a]}}
    pe = sum(me[a] * mo.get(a, 0) for a in cm) / (n * n)
    if abs(1 - pe) < 1e-12:
        k = 1.0 if p0 == 1.0 else float('nan')
        se = 0.0
    else:
        k = (p0 - pe) / (1 - pe)
        se = (p0 * (1 - p0) / (n * (1 - pe) ** 2)) ** 0.5 if p0 < 1 else 0.0
    lo, hi = k - 1.959964 * se, k + 1.959964 * se
    return k, max(-1.0, lo), min(1.0, hi), p0, pe, n


def build_cm(pairs, scale):
    cats = sorted({c for p in pairs for c in p})
    cm = collections.defaultdict(lambda: collections.defaultdict(int))
    for a, b in pairs:
        cm[scale(a) if scale else a][scale(b) if scale else b] += 1
    return cm


def fmt(kci):
    k, lo, hi, p0, pe, n = kci
    if p0 == 1.0:
        return 'kappa = %.4f (95%% CI degenerate at 1.00; all %d cells agree)' % (k, n)
    return 'kappa = %.4f (95%% CI %.3f to %.3f)   p0 = %.4f, pe = %.4f, n = %d' % (k, lo, hi, p0, pe, n)


def main():
    printed, second = parse_printed(), parse_second()
    L = []

    def w(s=''):
        L.append(s)

    w('=' * 78)
    w('Second coding vs printed coding - agreement statistics (computed 2026-09-27)')
    w('printed source: P2_Supplementary_English_v0.1.md, §S1 fenced marking table')
    w('second source:  work/second_coding_20260927.csv')
    w('=' * 78)

    # ---- name check ---------------------------------------------------------------
    w('')
    w('[name check]')
    for n in sorted(printed):
        a, b = printed[n]['benchmark'], second[n]['benchmark']
        if a != b:
            w('  row %2d: printed %r vs second %r' % (n, a, b))
    w('  (only differing names listed; row numbers are the join key)')

    # ---- decision-scale kappa ------------------------------------------------------
    pairs_all = []
    w('')
    w('[decision-scale kappa, convention A: unknown kept as a category]')
    for u in UNITS:
        pairs = [(category(base(printed[n]['marks'][u])), category(second[n]['marks'][u]))
                 for n in sorted(printed)]
        pairs_all.extend(pairs)
        w('  %-9s %s' % (u, fmt(kappa_cm(build_cm(pairs, None)))))
    w('  %-9s %s' % ('OVERALL', fmt(kappa_cm(build_cm(pairs_all, None)))))

    # ---- convention B: drop cells where either coding is unknown -------------------
    w('')
    w('[decision-scale kappa, convention B: cells where EITHER coding is unknown dropped]')
    dropped = []
    for u in UNITS:
        keep = [n for n in sorted(printed)
                if base(printed[n]['marks'][u]) != 'unknown'
                and second[n]['marks'][u] != 'unknown']
        dropped_u = [n for n in sorted(printed) if n not in keep]
        dropped.append((u, dropped_u))
        pairs = [(category(base(printed[n]['marks'][u])), category(second[n]['marks'][u]))
                 for n in keep]
        w('  %-9s %s   (dropped rows: %s)' % (u, fmt(kappa_cm(build_cm(pairs, None))),
                                              dropped_u or 'none'))
    keep_cells = [(n, u) for n in sorted(printed) for u in UNITS
                  if base(printed[n]['marks'][u]) != 'unknown'
                  and second[n]['marks'][u] != 'unknown']
    pairs = [(category(base(printed[n]['marks'][u])), category(second[n]['marks'][u]))
             for n, u in keep_cells]
    w('  %-9s %s   (cell-wise: %d of 76 cells kept; dropped cells sit in rows %s)'
      % ('OVERALL', fmt(kappa_cm(build_cm(pairs, None))), len(keep_cells),
         sorted(set(n for _u, ns in dropped for n in ns))))

    # ---- exact-mark agreement and mark-level kappa ----------------------------------
    w('')
    w('[exact-mark agreement and mark-level kappa (literal marks)]')
    mpairs_all = []
    for u in UNITS:
        pairs = [(base(printed[n]['marks'][u]), second[n]['marks'][u]) for n in sorted(printed)]
        mpairs_all.extend(pairs)
        agree = sum(1 for a, b in pairs if a == b)
        w('  %-9s exact %2d/19 agree;  %s' % (u, agree, fmt(kappa_cm(build_cm(pairs, None)))))
    agree = sum(1 for a, b in mpairs_all if a == b)
    w('  %-9s exact %2d/76 agree;  %s' % ('OVERALL', agree, fmt(kappa_cm(build_cm(mpairs_all, None)))))

    # ---- disagreements --------------------------------------------------------------
    w('')
    w('[disagreement cells (literal marks differ)]')
    n_dis = 0
    for n in sorted(printed):
        for u in UNITS:
            pe_mark, ps_mark = printed[n]['marks'][u], second[n]['marks'][u]
            if base(pe_mark) != ps_mark:
                n_dis += 1
                w('  row %2d %-18s %-9s printed %-22s second %-18s  [%s -> %s]'
                  % (n, printed[n]['benchmark'], u, pe_mark, ps_mark,
                     category(base(pe_mark)), category(ps_mark)))
    w('  total: %d of 76 cells differ at mark level' % n_dis)

    # ---- per-unit confusion matrices on the decision scale (convention A) ------------
    w('')
    w('[decision-scale confusion matrices, convention A; rows=printed, cols=second]')
    for u in UNITS:
        pairs = [(category(base(printed[n]['marks'][u])), category(second[n]['marks'][u]))
                 for n in sorted(printed)]
        cm = build_cm(pairs, None)
        cats = sorted({c for p in pairs for c in p})
        w('  %-9s %s' % (u, '  '.join('%-11s' % c for c in cats)))
        for a in cats:
            w('    %-9s %s' % (a, '  '.join('%-11d' % cm[a].get(b, 0) for b in cats)))

    text = '\n'.join(L) + '\n'
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(text)
    print(text)
    print('[written] %s' % OUT)


if __name__ == '__main__':
    main()
