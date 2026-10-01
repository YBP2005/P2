# -*- coding: utf-8 -*-
"""G8（多模型盲式第二编码）汇总与一致性分析。

输入：
  · 已印标记：补充材料 §S1 的 fenced marking table（12 个标记词表）
  · 8 份新编码：`盲审归档\\编码_G8_20260929\\returns\\G8_coding_*_20260929.md` 的 19 行 `ROW …`
输出：`work/kappa_g8_20260929.txt`（逐单元 + overall；Cohen's κ（对已印标记）、两两、Fleiss' κ）

**预先写死的映射**（把已印的 12 个标记按**任务书第 2 节逐单元的定义**折成 yes/no/unknown；
`test_gated` 在 release 一列按"澄清规则 1"记为结构上存在独立 test ⇒ yes；在 protocol 一列记为 no）：
    release : independent_test→yes ; alias/train_val_alias→no ; test_gated→yes ; 其余→unknown
    protocol: independent_test→yes ; test_gated→no ; alias/train_val_alias→no ; 其余→unknown
    yolo_dist: clean→yes ; alias/train_val_alias→no ; 其余→unknown
    reported: clean/independent_test→yes ; alias/train_val_alias/contradictory→no ; 其余→unknown
另有 `--sens` 变体：把唯一两处可争的（release:test_gated、protocol:alias）改记为 unknown，看 κ 会不会动。

用法：python -X utf8 work/kappa_g8_20260929.py [--sens]
"""
import collections
import io
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')

# ── r163（D32）：路径改为**包根解析 + 环境变量覆盖**，好让这份脚本从发布包里也能跑 ─────────────
#   `P2_ROOT` > 本脚本上一级 > 上两级 > 作者树（带 `01_paper/` 的才算包根）。
#   三个输入输出各有专用环境变量（`G8_SUP` / `G8_RET` / `G8_OUT`），由
#   `g8_primary_run_20261001.py` 用来在 v1 回执上重跑 primary 与 --sens。
HERE = os.path.dirname(os.path.abspath(__file__))


def _root():
    for c in (os.environ.get('P2_ROOT'), os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE)),
              r'E:\workplace'):
        if c and os.path.isdir(os.path.join(c, '01_paper')):
            return c
    return r'E:\workplace'


W = _root()


def _pick(*rels):
    for rel in rels:                      # 包内布局优先：与本脚本同目录
        p = os.path.join(HERE, rel)
        if os.path.exists(p):
            return p
    for rel in rels:                      # 否则按作者树布局
        p = os.path.join(W, rel)
        if os.path.exists(p):
            return p
    return os.path.join(W, rels[-1])


SUP = os.environ.get('G8_SUP') or _pick(
    os.path.join('01_paper', 'P2_Supplementary_English_v0.1.md'),
    'P2_Supplementary_English_v0.1.md')


def _ret_dir():
    """第 3 轮（v1 三值刻度）的 8 份回执。包内布局里它们以 `v1_` 前缀平铺，作者树里在 `returns_v1/`。
    **排除 `_v2_`**：那是第 4 轮修好仪器后的五值刻度，用本脚本的映射读它会读错。"""
    for d in (os.path.join(HERE, 'returns_v1'), HERE, os.path.join(HERE, 'returns'),
              os.path.join(W, '盲审归档', '编码_G8_20260929', 'returns_v1'),
              os.path.join(W, '盲审归档', '编码_G8_20260929', 'returns')):
        if not os.path.isdir(d):
            continue
        fs = sorted(f for f in os.listdir(d)
                    if 'G8_coding_' in f and f.endswith('_20260929.md') and '_v2_' not in f)
        if fs:
            return d, fs
    sys.exit('!! 找不到第 3 轮（v1）回执目录：试过 returns_v1 / 本目录 / returns（作者树同）')


RET, RET_FILES = (os.environ.get('G8_RET'), None) if os.environ.get('G8_RET') else _ret_dir()
UNITS = ['release', 'protocol', 'yolo_dist', 'reported']
SCALE = ['yes', 'no', 'unknown']
SENS = '--sens' in sys.argv
# r163：默认输出名按变体区分（历史件 `kappa_g8_20260929.txt` 就是 `--sens` 那份，别再被默认跑覆盖）
OUT = os.environ.get('G8_OUT') or (
    os.path.join(HERE, 'kappa_g8_20260929.txt' if SENS else 'kappa_g8_primary_20261001.txt')
    if os.path.basename(HERE) == 'work'
    else os.path.join(tempfile.gettempdir(),
                      'kappa_g8_%s.txt' % ('sens' if SENS else 'primary')))

MAP = {
    'release': {'independent_test': 'yes', 'test_gated': 'yes',
                'alias': 'no', 'train_val_alias': 'no'},
    'protocol': {'independent_test': 'yes', 'test_gated': 'no',
                 'alias': 'no', 'train_val_alias': 'no'},
    'yolo_dist': {'clean': 'yes', 'alias': 'no', 'train_val_alias': 'no'},
    'reported': {'clean': 'yes', 'independent_test': 'yes',
                 'alias': 'no', 'train_val_alias': 'no', 'contradictory': 'no'},
}
SENS_OVERRIDE = {('release', 'test_gated'): 'unknown', ('protocol', 'alias'): 'unknown',
                 ('protocol', 'train_val_alias'): 'unknown'}
BUFS = []


def w(s=''):
    BUFS.append(s)
    print(s)


def base(mark):
    return mark.strip().strip('`').split('(')[0].strip()


def parse_printed():
    text = io.open(SUP, encoding='utf-8').read()
    fence = re.search(r'```text\n(.*?)\n```', text, re.S)
    block = fence.group(1)
    start = block.index('## Marking table')
    rows = {}
    for line in block[start:].splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|', line)
        if not m:
            continue
        cells = [c.strip() for c in line.split('|')]
        rows[int(cells[1])] = {u: base(cells[3 + i]) for i, u in enumerate(UNITS)}
    assert len(rows) == 19, len(rows)
    return rows


def printed_scale(rows):
    out = {}
    for n, r in rows.items():
        d = {}
        for u in UNITS:
            mk = r[u]
            if SENS and (u, mk) in SENS_OVERRIDE:
                d[u] = SENS_OVERRIDE[(u, mk)]
            else:
                d[u] = MAP[u].get(mk, 'unknown')
        out[n] = d
    return out


ROW_RE = re.compile(r'(?m)^\s*ROW\s+(\d+)\s*\|(.*)$')


def parse_coder(path):
    t = io.open(path, encoding='utf-8').read()
    rows = {}
    for m in ROW_RE.finditer(t):
        n = int(m.group(1))
        rest = m.group(2)
        d = {}
        for u in UNITS:
            mm = re.search(r'%s\s*=\s*\**\s*(yes|no|unknown|YES|NO|UNKNOWN)' % u, rest)
            d[u] = mm.group(1).lower() if mm else 'MISSING'
        rows[n] = d
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


def fleiss(items, cats):
    """items: list of lists of labels（每 item 的 k 个评分）。返回 (kappa, p_bar, p_e)。"""
    N = len(items)
    k = len(items[0])
    pj = collections.Counter()
    P = []
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
        return 'κ=%.3f (CI 退化于 1.00，全部 %d 格一致)' % (k, n)
    return 'κ=%.3f (95%% CI %.3f–%.3f)  p0=%.3f pe=%.3f n=%d' % (k, lo, hi, p0, pe, n)


def main():
    printed_raw = parse_printed()
    printed = printed_scale(printed_raw)
    files = RET_FILES if RET_FILES else sorted(
        f for f in os.listdir(RET)
        if 'G8_coding_' in f and f.endswith('_20260929.md') and '_v2_' not in f)
    coders = {}
    for f in files:
        base = f[len('v1_'):] if f.startswith('v1_') else f    # 包内 v1 回执带 `v1_` 前缀
        name = base[len('G8_coding_'):-len('_20260929.md')]
        rows = parse_coder(os.path.join(RET, f))
        miss = [n for n in range(1, 20) if n not in rows]
        bad = [(n, u) for n, d in rows.items() for u in UNITS if d[u] == 'MISSING']
        if miss or bad:
            w('⚠ %s：缺行 %s；解析不到的单元 %s' % (name, miss, bad))
        coders[name] = rows

    w('=' * 108)
    w('G8 多模型盲式第二编码 · 一致性分析%s' % ('（敏感性变体：release:test_gated / protocol:alias → unknown）' if SENS else ''))
    w('=' * 108)
    w('编码者 %d 位：%s' % (len(coders), '、'.join(coders)))
    w('比较基数：已印标记 19 行 × 4 单元 = 76 格；映射见脚本头（预先写死）。')
    w('')
    w('【已印标记折成 yes/no/unknown 后的分布】')
    for u in UNITS:
        c = collections.Counter(printed[n][u] for n in range(1, 20))
        w('  %-9s yes %2d / no %2d / unknown %2d' % (u, c['yes'], c['no'], c['unknown']))

    w('')
    w('【逐位编码者对已印标记的一致性（Cohen\'s κ）】')
    w('%-24s %-28s %s' % ('编码者', 'overall（76 格）', '逐单元 κ（release/protocol/yolo_dist/reported）'))
    per = {}
    for name in coders:
        pairs_all = [(printed[n][u], coders[name][n][u]) for n in range(1, 20) for u in UNITS]
        cm = collections.defaultdict(lambda: collections.defaultdict(int))
        for a, b in pairs_all:
            cm[a][b] += 1
        kc = kappa_cm(cm)
        per_u = []
        for u in UNITS:
            cmu = collections.defaultdict(lambda: collections.defaultdict(int))
            for n in range(1, 20):
                cmu[printed[n][u]][coders[name][n][u]] += 1
            per_u.append(kappa_cm(cmu)[0])
        per[name] = kc[0]
        w('%-24s %-28s %s' % (name, fmt(kc), ' / '.join('%.3f' % x for x in per_u)))
    ks = [v for v in per.values() if v == v]
    w('  ⇒ overall κ：中位 %.3f，范围 %.3f–%.3f（n = %d 位）'
      % (sorted(ks)[len(ks) // 2], min(ks), max(ks), len(ks)))

    w('')
    w('【两两一致性（新编码者之间，overall 76 格）】')
    names = list(coders)
    pks = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            cm = collections.defaultdict(lambda: collections.defaultdict(int))
            for n in range(1, 20):
                for u in UNITS:
                    cm[coders[names[i]][n][u]][coders[names[j]][n][u]] += 1
            kk = kappa_cm(cm)[0]
            pks.append(kk)
    w('  %d 对：中位 %.3f，范围 %.3f–%.3f' % (len(pks), sorted(pks)[len(pks) // 2], min(pks), max(pks)))
    w('  明细：' + '  '.join('%.2f' % x for x in sorted(pks)))

    w('')
    w('【Fleiss\' κ（8 位编码者同时评；逐单元 + overall）】')
    for label, items in [('overall', [[coders[c][n][u] for c in names] for n in range(1, 20) for u in UNITS])] + \
                        [(u, [[coders[c][n][u] for c in names] for n in range(1, 20)]) for u in UNITS]:
        if label != 'overall':
            items = [[coders[c][n][u] for c in names] for n in range(1, 20)]
            u = label
        kf, pb, pe = fleiss(items, SCALE)
        w('  %-9s κ=%.3f  P̄=%.3f  Pe=%.3f  (n_items=%d, raters=%d)' % (label, kf, pb, pe, len(items), len(names)))

    w('')
    w('【与已印标记的混淆：每一列（已印）→ 编码者们都答了什么（8 位合计，76 格按单元拆）】')
    for u in UNITS:
        w('  %s：' % u)
        for cat in SCALE:
            rows_here = [n for n in range(1, 20) if printed[n][u] == cat]
            if not rows_here:
                continue
            cnt = collections.Counter(coders[c][n][u] for n in rows_here for c in names)
            w('     已印=%-8s（%2d 行 ×%d 位）→ yes %3d / no %3d / unknown %3d'
              % (cat, len(rows_here), len(names), cnt['yes'], cnt['no'], cnt['unknown']))

    w('')
    w('【headline 重算：每位编码者会数出多少个"reported 非独立"（= reported=no 的行数）】')
    w('  已印标记给出的数：%d/19' % sum(1 for n in range(1, 20) if printed[n]['reported'] == 'no'))
    cnts = {}
    for c in names:
        cnts[c] = sum(1 for n in range(1, 20) if coders[c][n]['reported'] == 'no')
    w('  ' + '  '.join('%s %d' % (c, cnts[c]) for c in names))
    v = sorted(cnts.values())
    w('  ⇒ 编码者区间 %d–%d（中位 %d）；已印数 %d %s'
      % (v[0], v[-1], v[len(v) // 2],
         sum(1 for n in range(1, 20) if printed[n]['reported'] == 'no'),
         '落在区间内' if v[0] <= sum(1 for n in range(1, 20) if printed[n]['reported'] == 'no') <= v[-1] else '**落在区间外**'))

    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(BUFS) + '\n')
    print('\n报告 → %s' % OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
