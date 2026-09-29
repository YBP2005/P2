# -*- coding: utf-8 -*-
"""selection_premium_local.py — the selection-premium table, computed from LOCAL archives only.

Port of `work/selection_premium.py` (2026-09-14). Two defects are fixed by the port itself, and both are recorded
rather than silently patched:

  1. its roots are three older trees, so the run inventory it sees is a snapshot; this port also reads the two
     pulled 20260915 archives.
  2. its fourth cell ("dota15 within-domain 100ep") matched nothing and printed "no runs found". The runs exist
     but two of them carry no seed suffix (`dota15_base100`, `dota15_lr005_100ep`), so the cell's matcher —
     `prefix + '_s'` — never saw them. This port matches the optional seed suffix as well, keys the unseeded run
     by its directory name, and marks it in the output, because "three seeds" for that cell is really two seeded
     runs plus one whose seed identity is not recorded in its name.

Statistics and the three endpoints (best = the reported convention under val == test; last and last5 = endpoints
selection cannot touch) are unchanged, so the three cells that the original did produce must reproduce exactly.

Writes: analysis/eval_validity/selection_premium_local_20260916.txt
"""
import csv
import io
import os
import re
import sys

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
ROOTS = [r'D:\deepseek\4090Bruns\runs',
         r'D:\deepseek\analysis\A_results_20260914\runs',
         r'D:\deepseek\analysis\B_results_20260914\runs',
         r'D:\deepseek\analysis\A_results_20260915\workspace\runs',
         r'D:\deepseek\analysis\B_results_20260915\workspace\runs']
OUT = r'D:\deepseek\analysis\eval_validity\selection_premium_local_20260916.txt'

CELLS = {
    'smoke2sf (strong cell)': ('smoke2sf_base100', 'smoke2sf_lr005_100ep'),
    'shwd2sf (corroborating)': ('shwd2sf_base100', 'shwd2sf_lr005_100ep'),
    'a2d15 (directional probe)': ('a2d15_base100', 'a2d15_lr005_100ep'),
    'dota15 within-domain 100ep': ('dota15_base100', 'dota15_lr005_100ep'),
}


def find_runs():
    out, dupes = {}, []
    for root in ROOTS:
        if not os.path.isdir(root):
            print('missing root: %s' % root)
            continue
        for name in os.listdir(root):
            p = os.path.join(root, name, 'results.csv')
            if os.path.exists(p):
                if name in out:
                    dupes.append(name)
                out[name] = p
    return out, dupes


def series(path):
    rows = list(csv.DictReader(io.open(path, encoding='utf-8', errors='ignore')))
    def col(*names):
        for n in names:
            if rows and n in rows[0]:
                return np.array([float(r[n]) for r in rows])
        return None
    return col('metrics/mAP50-95(B)'), col('metrics/mAP50(B)')


def match(runs, pref):
    """pref, or pref with a seed suffix. Keyed by seed number, or by 'unseeded' for a run whose name carries
    no seed — the cell's third reading comes from exactly such a run, and keying it per arm would stop the two
    arms from pairing at all."""
    pat = re.compile(re.escape(pref) + r'(?:_s(\d+)n)?$')
    out = {}
    for name, path in runs.items():
        m = pat.match(name)
        if m:
            out[int(m.group(1)) if m.group(1) else 'unseeded'] = path
    return out


buf = []
def emit(s=''):
    print(s)
    buf.append(s)


runs, dupes = find_runs()
emit('released runs with results.csv (local archives): %d' % len(runs))
if dupes:
    emit('run names present in more than one root: %d  eg %s' % (len(dupes), sorted(dupes)[:4]))
emit()
emit('%-30s %-26s %8s %8s %8s %8s' % ('cell / arm', 'seed', 'best', 'last', 'last5', 'premium'))
summary = {}
for cell, (base_pref, strat_pref) in CELLS.items():
    base = match(runs, base_pref)
    strat = match(runs, strat_pref)
    seeds = sorted(set(base) & set(strat), key=lambda s: (isinstance(s, str), s))
    emit('%-30s matched base=%d strat=%d paired=%d' % (cell, len(base), len(strat), len(seeds)))
    if len(seeds) < 2:
        emit('   no usable pairs')
        emit()
        continue
    per = {}
    for label, m in (('base', base), ('strat', strat)):
        vals = {'best': [], 'last': [], 'last5': []}
        for s in seeds:
            m95, _ = series(m[s])
            vals['best'].append(float(m95.max()))
            vals['last'].append(float(m95[-1]))
            vals['last5'].append(float(m95[-5:].mean()))
        per[label] = {k: np.array(v) * 100 for k, v in vals.items()}
    n = len(seeds)
    for label in ('base', 'strat'):
        v = per[label]
        d = v['best'] - v['last']
        emit('   %-26s %-26s %8.3f %8.3f %8.3f %+8.3f'
             % (label, ','.join(str(s) for s in seeds)[:26], v['best'].mean(), v['last'].mean(),
                v['last5'].mean(), d.mean()))
    res = {}
    for k in ('best', 'last', 'last5'):
        b, s = per['base'][k], per['strat'][k]
        t, p = stats.ttest_rel(s, b)
        res[k] = ((s - b).mean(), (s - b).std(ddof=1), t, p)
    summary[cell] = (n, res)
    emit('   paired contrast (n=%d):' % n)
    for k in ('best', 'last', 'last5'):
        m, sd, t, p = res[k]
        emit('      %-6s delta %+6.3f pp  sd %5.3f  paired t %6.2f  p %.4g' % (k, m, sd, t, p))
    emit()

emit('=' * 78)
emit('premium = best-epoch minus final-epoch mAP50-95 within a run.')
emit('With val == test in the corpus yamls, "best" is selected on the reported split; "last"/"last5" are not.')
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(buf) + '\n')
print('\nwrote %s' % OUT)
