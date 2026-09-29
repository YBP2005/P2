# -*- coding: utf-8 -*-
"""selection_premium.py — is the headline gain a checkpoint-selection artefact?

Context (verified on the live pods, 2026-09-14): every dataset yaml used by this project points
`val` and `test` at the SAME directory, so the reported endpoint is the *best-validation* checkpoint
evaluated on its own validation split.  The reported per-run number is therefore a maximum over
epochs.  Two questions follow, and both are answerable from the released `results.csv` files with no
GPU:

  1. How large is the selection premium (best-epoch minus final-epoch metric) per run?
  2. Does the headline paired contrast survive when the endpoint is *not* selected on the reported
     split — i.e. at the final epoch, or averaged over a trailing window?

If the contrast survives, the leak inflates levels but not the arm difference, and the paper can say
so with numbers instead of asserting it.  If it does not survive, the headline is a selection effect
and must be reported as such.

Reads: analysis/A_results_20260914/runs/*/results.csv, analysis/B_results_20260914/runs/*/results.csv
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
         r'D:\deepseek\analysis\B_results_20260914\runs']

CELLS = {
    'smoke2sf (strong cell)': ('smoke2sf_base100', 'smoke2sf_lr005_100ep'),
    'shwd2sf (corroborating)': ('shwd2sf_base100', 'shwd2sf_lr005_100ep'),
    'a2d15 (directional probe)': ('a2d15_base100', 'a2d15_lr005_100ep'),
    'dota15 within-domain 100ep': ('dota15_base100', 'dota15_lr005_100ep'),
}


def find_runs():
    out = {}
    for root in ROOTS:
        if not os.path.isdir(root):
            print('missing root: %s' % root)
            continue
        for name in os.listdir(root):
            p = os.path.join(root, name, 'results.csv')
            if os.path.exists(p):
                out[name] = p
    return out


def series(path):
    """per-epoch (mAP50-95, mAP50) from a released results.csv"""
    with io.open(path, encoding='utf-8', errors='ignore') as fh:
        rows = [r for r in csv.DictReader(fh)]
    def col(*names):
        for n in names:
            if rows and n in rows[0]:
                return np.array([float(r[n]) for r in rows])
        return None
    m95 = col('metrics/mAP50-95(B)', 'metrics/mAP50-95(B)'.strip())
    m50 = col('metrics/mAP50(B)')
    return m95, m50


def main():
    runs = find_runs()
    print('released runs with results.csv: %d' % len(runs))
    print()
    print('%-30s %6s %6s %6s %6s %6s' % ('cell / arm', 'n_seed', 'best', 'last', 'last5', 'premium'))
    summary = {}
    for cell, (base_pref, strat_pref) in CELLS.items():
        rows = {}
        for pref in (base_pref, strat_pref):
            hits = {k: v for k, v in runs.items() if k.startswith(pref + '_s')}
            rows[pref] = hits
        seeds = sorted({int(re.search(r'_s(\d+)n', k).group(1))
                        for k in list(rows[base_pref]) + list(rows[strat_pref])
                        if re.search(r'_s(\d+)n', k)})
        if not seeds:
            print('%-30s  no runs found' % cell)
            continue
        per = {}
        for label, pref in (('base', base_pref), ('strat', strat_pref)):
            vals = {'best': [], 'last': [], 'last5': []}
            kept = []
            for s in seeds:
                key = '%s_s%dn' % (pref, s)
                if key not in runs:
                    continue
                m95, _ = series(runs[key])
                if m95 is None or len(m95) == 0:
                    continue
                vals['best'].append(float(m95.max()))
                vals['last'].append(float(m95[-1]))
                vals['last5'].append(float(m95[-5:].mean()))
                kept.append(s)
            per[label] = {k: np.array(v) * 100 for k, v in vals.items()}
            per[label + '_seeds'] = kept
        n = min(len(per['base']['best']), len(per['strat']['best']))
        print('%-30s' % cell)
        for label in ('base', 'strat'):
            v = per[label]
            d = v['best'] - v['last']
            print('   %-26s %6d %6.3f %6.3f %6.3f %+6.3f'
                  % (label, len(v['best']), v['best'].mean(), v['last'].mean(),
                     v['last5'].mean(), d.mean()))
        if n >= 2:
            res = {}
            for k in ('best', 'last', 'last5'):
                b = per['base'][k][:n]
                s = per['strat'][k][:n]
                diff = s - b
                t, p = stats.ttest_rel(s, b)
                res[k] = (diff.mean(), diff.std(ddof=1), t, p)
            summary[cell] = (n, res)
            print('   paired contrast (n=%d):' % n)
            for k in ('best', 'last', 'last5'):
                m, sd, t, p = res[k]
                print('      %-6s delta %+6.3f pp  sd %5.3f  paired t %6.2f  p %.4g' % (k, m, sd, t, p))
        print()

    print('=' * 78)
    print('interpretation key:')
    print('  premium = best-epoch minus final-epoch metric within a run (the selection premium)')
    print('  "best" = the reported convention (val==test, so this is selected on the reported split)')
    print('  "last"/"last5" = endpoints no selection can touch')
    print('=' * 78)


if __name__ == '__main__':
    main()
