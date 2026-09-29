# -*- coding: utf-8 -*-
"""G8 v2（5 值刻度）汇总与一致性分析，并与 v1（3 值刻度）对照。

v2 刻度：`independent` / `alias` / `absent` / `gated` / `unknown`。
已印 12 个标记 → v2 五值：**全定义域、逐类对应**（故 κ 与已印表直接可比）：
    independent_test, clean → independent
    alias, train_val_alias  → alias
    n_a, no_test, no_val, no_split, no_yaml → absent
    test_gated              → gated
    contradictory, unknown  → unknown
v1 的 8 份原文已随复现包留档（`_release_github/04_verification/second_coding/G8_coding_*.md`），
本脚本同时解析它们，做 v1→v2 的**同批编码者配对对照**。

用法：python -X utf8 work/kappa_g8v2_20260929.py
"""
import collections
import hashlib
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
SUP = os.path.join(W, 'P2_Supplementary_English_v0.1.md')
RET = os.path.join(W, '盲审归档', '编码_G8_20260929', 'returns')
V1DIR = os.path.join(W, '_release_github', '04_verification', 'second_coding')
OUT = os.path.join(W, 'work', 'kappa_g8v2_20260929.txt')
UNITS = ['release', 'protocol', 'yolo_dist', 'reported']
V2 = ['independent', 'alias', 'absent', 'gated', 'unknown']
V2MAP = {'independent_test': 'independent', 'clean': 'independent',
         'alias': 'alias', 'train_val_alias': 'alias',
         'n_a': 'absent', 'no_test': 'absent', 'no_val': 'absent',
         'no_split': 'absent', 'no_yaml': 'absent', 'no_test_key': 'absent',
         'test_gated': 'gated', 'contradictory': 'unknown', 'unknown': 'unknown'}
BUFS = []


def w(s=''):
    BUFS.append(s)
    print(s)


def base(m):
    return m.strip().strip('`').split('(')[0].strip()


def parse_printed():
    t = io.open(SUP, encoding='utf-8').read()
    block = re.search(r'```text\n(.*?)\n```', t, re.S).group(1)
    start = block.index('## Marking table')
    rows, bench = {}, {}
    for line in block[start:].splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|', line)
        if not m:
            continue
        c = [x.strip() for x in line.split('|')]
        n = int(c[1])
        rows[n] = {u: base(c[3 + i]) for i, u in enumerate(UNITS)}
        bench[n] = c[2]
    assert len(rows) == 19
    return rows, bench


ROW_RE = re.compile(r'(?m)^\s*ROW\s+(\d+)\s*\|(.*)$')


def parse_coder(path, scale):
    t = io.open(path, encoding='utf-8').read()
    rows = {}
    for m in ROW_RE.finditer(t):
        rest = m.group(2)
        d = {}
        for u in UNITS:
            mm = re.search(r'%s\s*=\s*\**\s*([A-Za-z_]+)' % u, rest)
            d[u] = mm.group(1).lower() if mm else 'MISSING'
        rows[int(m.group(1))] = d
    return rows


def kappa_cm(cm):
    n = sum(cm[a][b] for a in cm for b in cm[a])
    p0 = sum(cm[a][a] for a in cm) / n
    me = {a: sum(cm[a].values()) for a in cm}
    mo = {b: sum(cm[a].get(b, 0) for a in cm) for b in {b for a in cm for b in cm[a]}}
    pe = sum(me[a] * mo.get(a, 0) for a in cm) / (n * n)
    if abs(1 - pe) < 1e-12:
        k, se = (1.0 if p0 == 1.0 else float('nan')), 0.0
    else:
        k = (p0 - pe) / (1 - pe)
        se = (p0 * (1 - p0) / (n * (1 - pe) ** 2)) ** 0.5 if p0 < 1 else 0.0
    return k, max(-1.0, k - 1.959964 * se), min(1.0, k + 1.959964 * se), p0, pe, n


def cm_of(pairs):
    cm = collections.defaultdict(lambda: collections.defaultdict(int))
    for a, b in pairs:
        cm[a][b] += 1
    return cm


def fleiss(items, cats):
    N, k = len(items), len(items[0])
    pj, P = collections.Counter(), []
    for it in items:
        c = collections.Counter(it)
        P.append((sum(v * v for v in c.values()) - k) / (k * (k - 1)))
        pj.update(it)
    Pbar = sum(P) / N
    pe = sum((pj[c] / (N * k)) ** 2 for c in cats)
    return (Pbar - pe) / (1 - pe), Pbar, pe


def fmt(kci):
    k, lo, hi, p0, pe, n = kci
    if p0 == 1.0:
        return 'κ=%.3f (CI 退化于 1.00，%d 格全一致)' % (k, n)
    return 'κ=%.3f (95%% CI %.3f–%.3f)  p0=%.3f pe=%.3f n=%d' % (k, lo, hi, p0, pe, n)


def main():
    printed_raw, bench = parse_printed()
    printed = {n: {u: V2MAP[printed_raw[n][u]] for u in UNITS} for n in printed_raw}

    v2f = sorted(f for f in os.listdir(RET) if f.endswith('_v2_20260929.md'))
    coders = {}
    for f in v2f:
        name = f[len('G8_coding_'):-len('_v2_20260929.md')]
        rows = parse_coder(os.path.join(RET, f), V2)
        miss = [n for n in range(1, 20) if n not in rows]
        bad = [(n, u, rows[n][u]) for n in rows for u in UNITS if rows[n][u] not in V2]
        if miss or bad:
            w('⚠ %s：缺行 %s；取值越界 %s' % (name, miss, bad))
        coders[name] = rows
    v1 = {}
    if os.path.isdir(V1DIR):
        for f in sorted(os.listdir(V1DIR)):
            if not f.startswith('G8_coding_') or not f.endswith('_20260929.md'):
                continue
            name = f[len('G8_coding_'):-len('_20260929.md')]
            v1[name] = parse_coder(os.path.join(V1DIR, f), ['yes', 'no', 'unknown'])

    w('=' * 110)
    w('G8 v2（5 值刻度：independent / alias / absent / gated / unknown）· 一致性分析')
    w('=' * 110)
    w('编码者 %d 位：%s' % (len(coders), '、'.join(coders)))
    w('已印 12 标记 → 五值：**全定义域逐类对应**（见脚本头）⇒ 与已印表直接可比。')
    w('')
    w('【已印标记折成五值后的分布】')
    for u in UNITS:
        c = collections.Counter(printed[n][u] for n in range(1, 20))
        w('  %-9s ' % u + ' · '.join('%s %d' % (k, c[k]) for k in V2 if c[k]))

    w('')
    w('【逐位编码者 vs 已印标记（Cohen\'s κ）】')
    w('%-24s %-34s %s' % ('编码者', 'overall（76 格）', '逐单元（release/protocol/yolo_dist/reported）'))
    per = {}
    for name in coders:
        kc = kappa_cm(cm_of([(printed[n][u], coders[name][n][u]) for n in range(1, 20) for u in UNITS]))
        pu = []
        for u in UNITS:
            pu.append(kappa_cm(cm_of([(printed[n][u], coders[name][n][u]) for n in range(1, 20)]))[0])
        per[name] = kc[0]
        w('%-24s %-34s %s' % (name, fmt(kc), ' / '.join('%.3f' % x for x in pu)))
    ks = sorted(v for v in per.values() if v == v)
    w('  ⇒ overall κ：中位 %.3f，范围 %.3f–%.3f（n = %d 位）'
      % (ks[len(ks) // 2], ks[0], ks[-1], len(ks)))

    w('')
    w('【两两（v2，8 位，overall 76 格）】')
    names = list(coders)
    pk = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pk.append(kappa_cm(cm_of([(coders[names[i]][n][u], coders[names[j]][n][u])
                                      for n in range(1, 20) for u in UNITS]))[0])
    pk.sort()
    w('  %d 对：中位 %.3f，范围 %.3f–%.3f' % (len(pk), pk[len(pk) // 2], pk[0], pk[-1]))
    w('  明细：' + '  '.join('%.2f' % x for x in pk))

    w('')
    w('【Fleiss\' κ（v2，8 位）】')
    for label, its in [('overall', [[coders[c][n][u] for c in names] for n in range(1, 20) for u in UNITS])] + \
                      [(u, [[coders[c][n][u] for c in names] for n in range(1, 20)]) for u in UNITS]:
        if label != 'overall':
            its = [[coders[c][n][label] for c in names] for n in range(1, 20)]
        kf, pb, pe = fleiss(its, V2)
        w('  %-9s κ=%.3f  P̄=%.3f  Pe=%.3f' % (label, kf, pb, pe))

    w('')
    w('【混淆（已印 → 8 位作答合计）】')
    for u in UNITS:
        w('  %s：' % u)
        for cat in V2:
            rows_here = [n for n in range(1, 20) if printed[n][u] == cat]
            if not rows_here:
                continue
            cnt = collections.Counter(coders[c][n][u] for n in rows_here for c in names)
            w('     已印=%-12s（%2d 行）→ ' % (cat, len(rows_here))
              + ' · '.join('%s %d' % (k, cnt[k]) for k in V2 if cnt[k]))

    w('')
    w('【headline：每位数出的 `reported = alias`（= 非独立）行数】')
    pr = sum(1 for n in range(1, 20) if printed[n]['reported'] == 'alias')
    w('  已印：%d/19' % pr)
    cnts = {c: sum(1 for n in range(1, 20) if coders[c][n]['reported'] == 'alias') for c in names}
    w('  ' + '  '.join('%s %d' % (c, cnts[c]) for c in names))
    v = sorted(cnts.values())
    w('  ⇒ 编码者区间 %d–%d（中位 %d）；已印 %d %s'
      % (v[0], v[-1], v[len(v) // 2], pr, '落在区间内' if v[0] <= pr <= v[-1] else '**落在区间外**'))

    if v1:
        w('')
        w('【v1 → v2 配对（同一位编码者，overall 76 格；两轮刻度不同，v1 按其三值口径重算仅作参考）】')
        common = [c for c in names if c in v1]
        w('  v1 里同名可比 %d 位：%s' % (len(common), '、'.join(common)))
        for c in common:
            a = sum(1 for n in range(1, 20) for u in UNITS if v1[c][n][u] == 'yes')
            b = sum(1 for n in range(1, 20) for u in UNITS if coders[c][n][u] == 'independent')
            w('     %-24s v1 答 yes %2d 格 → v2 答 independent %2d 格' % (c, a, b))

    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(BUFS) + '\n')
    print('\n报告 → %s' % OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
