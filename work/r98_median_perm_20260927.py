# -*- coding: utf-8 -*-
"""#33 read-only recomputation: peak-agreement predictor -- mean-driven diagnostic
plus a median-difference permutation test.  Nothing is written; no paper file is touched.

Archive inputs:
  workplace/xeval_20260916/runs/*_results.csv                     (val curves)
  workplace/xeval_perepoch_20260918/matrix_perepoch.csv           (test spot-check grid)
  workplace/实验内容共享/P2/02_论文释放件/release_selection-transfer_perseed.csv
"""
import csv, io, os, random, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
RUNS = 'E:/workplace/xeval_20260916/runs'
MAT = 'E:/workplace/xeval_perepoch_20260918/matrix_perepoch.csv'
REL = 'E:/workplace/实验内容共享/P2/02_论文释放件/release_selection-transfer_perseed.csv'
SEED = 42

grid, tcurve = {}, {}
for r in csv.DictReader(io.open(MAT, encoding='utf-8-sig')):
    if r['split'] != 'test':
        continue
    grid.setdefault(r['run'], set()).add(int(r['epoch']))
    tcurve.setdefault(r['run'], {})[int(r['epoch'])] = float(r['map50_95'])
sigs = Counter(tuple(sorted(v)) for v in grid.values())
main_grid = sigs.most_common(1)[0][0]
print('test spot-check grid: %d points, %s'
      % (len(main_grid), 'all multiples of 5' if all(e % 5 == 0 for e in main_grid) else 'NOT all multiples of 5'))

val = {}
for f in sorted(os.listdir(RUNS)):
    if f.endswith('_results.csv'):
        val[f[:-len('_results.csv')]] = {int(r['epoch']): float(r['metrics/mAP50-95(B)'])
                                         for r in csv.DictReader(io.open(os.path.join(RUNS, f), encoding='utf-8-sig'))}

rows = [r for r in csv.DictReader(io.open(REL, encoding='utf-8-sig')) if r['run'] in val]
recs, okv, okt = [], 0, 0
for r in rows:
    run = r['run']
    g = sorted(grid.get(run, []))
    sub = {e: val[run][e] for e in g if e in val[run]}
    if not sub:
        continue
    vpk = max(sub, key=lambda e: sub[e])
    tpk = max(tcurve[run], key=lambda e: tcurve[run][e]) if tcurve.get(run) else None
    okv += (vpk == int(r['e_val_peak']))
    okt += (tpk == int(r['e_test_peak']))
    recs.append(dict(run=run, arm=r['arm'], pv=float(r['prem_val_pp']),
                     ps=float(r['prem_test_selected_pp']),
                     same_file=r['same_epoch'].strip().lower() == 'true', same_calc=(vpk == tpk)))
print('convention self-check: e_val_peak %d/%d, e_test_peak %d/%d, same_epoch %d/%d'
      % (okv, len(recs), okt, len(recs),
         sum(1 for x in recs if x['same_file'] == x['same_calc']), len(recs)))
for x in recs:
    x['gap'] = x['pv'] - x['ps']
same = [x['gap'] for x in recs if x['same_calc']]
diff = [x['gap'] for x in recs if not x['same_calc']]


def med(v):
    s = sorted(v)
    return s[len(s) // 2]


print('\n=== reproducing the group statistics printed in S11 13.3 / S12 ===')
print(' agree  n=%d  mean %+.4f  median %+.4f  non-positive %d'
      % (len(same), sum(same) / len(same), med(same), sum(1 for g in same if g <= 0)))
print(' differ n=%d  mean %+.4f  median %+.4f  non-positive %d'
      % (len(diff), sum(diff) / len(diff), med(diff), sum(1 for g in diff if g <= 0)))
print(' all 40 runs  min %+.4f  max %+.4f' % (min(same + diff), max(same + diff)))
top = max(same)
toprun = [x['run'] for x in recs if x['same_calc'] and x['gap'] == top][0]
print(' agree-group max %+.4f (run %s); without it agree mean %+.4f, median %+.4f'
      % (top, toprun, (sum(same) - top) / (len(same) - 1), med(sorted(same)[:-1])))
print(' agree-group non-positive: %d/%d' % (sum(1 for g in same if g <= 0), len(same)))

allg = same + diff
k = len(same)
obs_m = abs(med(allg[:k]) - med(allg[k:]))
obs_mean = abs(sum(same) / k - sum(diff) / len(diff))


def run(n_iter=20000, seed=SEED):
    rnd = random.Random(seed)
    cm = cmean = 0
    for _ in range(n_iter):
        rnd.shuffle(allg)
        if abs(med(allg[:k]) - med(allg[k:])) >= obs_m - 1e-12:
            cm += 1
        if abs(sum(allg[:k]) / k - sum(allg[k:]) / (len(allg) - k)) >= obs_mean - 1e-12:
            cmean += 1
    return cm / n_iter, cmean / n_iter


pm, pmn = run()
print('\n=== permutation test (20000 draws, seed 42, relabelling the 40 gaps) ===')
print(' observed |median_agree - median_differ| = |%+.4f - %+.4f| = %.4f' % (med(same), med(diff), obs_m))
print('   -> median-difference permutation p = %.4f' % pm)
print(' observed |mean_agree - mean_differ|     = |%+.4f - %+.4f| = %.4f' % (sum(same) / k, sum(diff) / len(diff), obs_mean))
print('   -> mean-difference permutation p     = %.4f   (the supplement prints 0.0091)' % pmn)
pm2, _ = run(20000, seed=7)
pm3, _ = run(20000, seed=2026)


def med_lo(v):
    s = sorted(v)
    return (s[(len(s) - 1) // 2] + s[len(s) // 2]) / 2


obs_m2 = abs(med_lo(same) - med_lo(diff))
rnd = random.Random(SEED)
c2 = 0
for _ in range(20000):
    rnd.shuffle(allg)
    if abs(med_lo(allg[:k]) - med_lo(allg[k:])) >= obs_m2 - 1e-12:
        c2 += 1
print(' robustness: seed 7 p=%.4f; seed 2026 p=%.4f; lower-median definition obs=%.4f p=%.4f'
      % (pm2, pm3, obs_m2, c2 / 20000))

print('\n=== leave-the-one-big-run-out sensitivity ===')
s2 = [x['gap'] for x in recs if x['same_calc'] and x['run'] != toprun]
d2 = [x['gap'] for x in recs if not x['same_calc']]
rnd = random.Random(SEED)
c = 0
o = abs(med(s2) - med(d2))
for _ in range(20000):
    rnd.shuffle(allg)
    if abs(med(allg[:k - 1]) - med(allg[k - 1:])) >= o - 1e-12:
        c += 1
print(' drop %s: agree mean %+.4f, median %+.4f (was +0.1305 / -0.2019); median-diff p = %.4f'
      % (toprun, sum(s2) / len(s2), med(s2), c / 20000))
print('\n=== why the mean is a poor summary here ===')
print(' agree group: %d of %d runs are non-positive; the single run %s contributes %+.4f pp to a group sum of %+.4f pp'
      % (sum(1 for g in same if g <= 0), len(same), toprun, top, sum(same)))
