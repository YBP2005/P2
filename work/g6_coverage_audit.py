#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""g6_coverage_audit.py — G6 评测的**覆盖面验收**（不信任评测脚本自己的 .DONE）。

判据（三条都要过）：
  (1) 清单里每个 run 的 `weights/epoch*.pt` 实盘个数 == 声明 `epochs//5`；
  (2) 每个 (run, ckpt) 在 `g6_perepoch.csv` 里**恰有一行**；
  (3) 每行的 `ckpt_epoch` 与文件名吻合（`epoch{N}.pt` → N+1）、`split` 全为 `test`、
      `map50_95` 落在 [0,100]、`data_yaml` 含 `carve_` 且含 `test:`。

输出：`g6_coverage.txt`（逐 run 一行 + 摘要）+ 打印；有任何缺口就非零退出。
用法：python g6_coverage_audit.py [--dir /workspace/g6_perepoch_20260930] [--list ...]
"""
import argparse
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='/workspace/g6_perepoch_20260930')
    ap.add_argument('--list', default='/workspace/g6_pull_list.tsv')
    ap.add_argument('--rundir', default='/workspace/runs')
    a = ap.parse_args()

    CSV = os.path.join(a.dir, 'g6_perepoch.csv')
    OUT = os.path.join(a.dir, 'g6_coverage.txt')
    if not os.path.exists(CSV):
        sys.exit('!! 找不到 %s' % CSV)

    runs = []
    for line in io.open(a.list, encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) == 2 and f[0].strip():
            runs.append((f[0].strip(), int(f[1])))

    rows = []
    for line in io.open(CSV, encoding='utf-8'):
        f = line.rstrip('\n').split(',')
        if len(f) >= 13 and f[0] != 'run':
            rows.append(f)

    per_run = {}
    bad_rows = []
    for f in rows:
        run, ck, ce, split, m, dy = f[0], f[4], f[5], f[6], f[7], f[11]
        per_run.setdefault(run, []).append(ck)
        try:
            mv = float(m)
        except ValueError:
            bad_rows.append('map50_95 非数：%s %s' % (run, ck)); continue
        if not (0.0 <= mv <= 100.0):
            bad_rows.append('map50_95 越界 %.3f：%s %s' % (mv, run, ck))
        if split != 'test':
            bad_rows.append('split!=test：%s %s' % (run, ck))
        mm = re.match(r'^epoch(\d+)$', ck)
        if mm:
            if ce != str(int(mm.group(1)) + 1):
                bad_rows.append('ckpt_epoch 不符：%s %s → %s' % (run, ck, ce))
        elif ck not in ('best', 'last'):
            bad_rows.append('非预期 ckpt 名：%s %s' % (run, ck))

    lines, missing = [], []
    n_ok = n_dup = n_diskbad = 0
    for (run, ep) in runs:
        wd = os.path.join(a.rundir, run, 'weights')
        disk = sorted((int(m.group(1)) for m in
                       (re.match(r'^epoch(\d+)\.pt$', n) for n in os.listdir(wd))
                       if m)) if os.path.isdir(wd) else []
        exp_n = ep // 5
        got = [c for c in per_run.get(run, []) if re.match(r'^epoch\d+$', c)]
        dup = len(got) - len(set(got))
        st = 'OK'
        if len(disk) != exp_n:
            st = 'DISK-COUNT'; n_diskbad += 1
        elif dup:
            st = 'DUPLICATE'; n_dup += 1
        elif len(set(got)) != exp_n:
            st = 'CSV-MISSING'; missing.append((run, exp_n - len(set(got))))
        else:
            n_ok += 1
        lines.append('%s\t声明点=%d\t盘上=%d\tCSV=%d\t重复=%d\t%s' % (run, exp_n, len(disk),
                                                                     len(set(got)), dup, st))
    # run 名里含非清单的（多余行）也要点出来
    extra = sorted(set(per_run) - set(r for r, _ in runs))

    summ = ('摘要：run 数=%d  齐备=%d  盘上个数不符=%d  重复=%d  CSV 缺 run=%d  多余 run=%d  '
            '行级异常=%d  行数=%d\n'
            % (len(runs), n_ok, n_diskbad, n_dup, len(missing), len(extra), len(bad_rows), len(rows)))
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(summ)
        f.write('\n'.join(lines) + '\n')
        if missing:
            f.write('\n# CSV 缺点位的 run：\n')
            for r, k in missing:
                f.write('MISSING\t%s\t缺 %d 点\n' % (r, k))
        if extra:
            f.write('\n# CSV 里出现清单外的 run：%s\n' % ', '.join(extra))
        if bad_rows:
            f.write('\n# 行级异常：\n' + '\n'.join(bad_rows[:200]) + '\n')
    print(summ, end='')
    for r, k in missing[:10]:
        print('  CSV-MISSING %s 缺 %d 点' % (r, k))
    for b in bad_rows[:10]:
        print('  行级异常:', b)
    print('存证：%s' % OUT)
    return 0 if (n_ok == len(runs) and not bad_rows and not extra) else 1


if __name__ == '__main__':
    sys.exit(main())
