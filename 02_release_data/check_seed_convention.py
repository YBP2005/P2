# -*- coding: utf-8 -*-
"""r52 — the seed convention, checked on data that is already local.

The recon found that on the pod every dota15 run's `args.yaml` says `seed: 42` — including the
runs named `_s43n` / `_s44n` — because the per-run randomness is installed by the project's own
`--shuffle-seed` (which matches the directory name), while ultralytics' `seed` stays at its
default.  That is worth checking for the REGISTERED replication too: §9's claim is "ten-seed
paired testing" over seeds 42-51, and a reader who opens one run's args.yaml will see `seed: 42`
in all ten.  If the seeds are realized through the shuffle, the paper should say so — the panel
already flagged seed identity as a defect class (§10 row 2).

This script reads the registered runs' args.yaml and results.csv from the local archive and asks:
  1. does `seed:` differ between runs named for different seeds?
  2. do the results.csv differ (i.e. is the seed actually doing something)?
  3. is there a recorded shuffle seed, and where?

Read-only.
"""
import hashlib
import io
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ROOTS = [
    r'D:\deepseek\analysis\A_results_20260914\runs',
    r'D:\deepseek\analysis\B_results_20260914\runs',
    r'D:\deepseek\analysis\A_results_20260916_t1d',
]
CELLS = ['t1a_d15toaitod', 't1b_aitodtovis', 't1c_vistod15', 't2_mask2mende', 't1d_dotatod15']

print('=' * 90)
print('注册复现的种子记录方式（本地归档）')
print('=' * 90)
for root in ROOTS:
    if not os.path.isdir(root):
        continue
    runs = sorted(d for d in os.listdir(root) if re.match(r'^t1[a-d]_|^t2_', d))
    if not runs:
        continue
    print('\n--- %s（%d 个 run）---' % (root, len(runs)))
    by_cell = defaultdict(list)
    for r in runs:
        m = re.match(r'^(t\w+?_(?:d15toaitod|aitodtovis|vistod15|mask2mende|dotatod15))_(.+)_s(\d+)n$', r)
        by_cell[m.group(1) if m else r].append(r)
    for cell, rr in sorted(by_cell.items()):
        seeds, agreed, disagreed = set(), [], []
        for r in rr:
            p = os.path.join(root, r, 'args.yaml')
            seed = None
            if os.path.exists(p):
                for line in io.open(p, encoding='utf-8', errors='ignore'):
                    if line.startswith('seed:'):
                        seed = line.split(':', 1)[1].strip()
                        break
            seeds.add(seed)
            rc = os.path.join(root, r, 'results.csv')
            h = (hashlib.md5(io.open(rc, 'rb').read()).hexdigest()[:8]
                 if os.path.exists(rc) else 'no-csv')
            (agreed if seed == str(int(re.search(r'_s(\d+)n$', r).group(1))) else disagreed).append(
                (r, seed, h))
        print('  %-22s %2d 个 run：args.yaml 里的 seed 取值 = %s' % (cell, len(rr), sorted(seeds)))
        print('     %d 个与目录名一致 / %d 个不一致' % (len(agreed), len(disagreed)))
        if disagreed:
            for r, seed, h in disagreed[:3]:
                print('       %s  args seed=%s  results.md5=%s' % (r[:46], seed, h))
        # are the CSVs distinct across seeds?
        hs = [h for _, _, h in (agreed + disagreed) if h != 'no-csv']
        print('     results.csv 去重后 %d / %d 个不同 ⇒ 种子确实在起作用：%s'
              % (len(set(hs)), len(hs), '是' if len(set(hs)) == len(hs) else '**有重复，需查**'))
print()
print('结论用于正文：若 args.yaml 的 seed 恒为默认值，则应写明"种子是通过数据顺序打乱'
      '（--shuffle-seed，与目录名一致）实现的，框架的 seed 参数保持默认"。')
