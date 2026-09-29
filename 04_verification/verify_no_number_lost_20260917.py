# -*- coding: utf-8 -*-
"""r46/r54i: the guard the per-part multiset check cannot provide -- "no number leaves the paper".

Why this exists: compressing, de-duplicating and restructuring legitimately move numbers between
parts and between the article and its supplement, so the per-part multiset invariant registers
every such move as a "loss" that must be declared.  Declaring them by hand is fine, but a script
that auto-computes the declarations turns the guard into a rubber stamp -- and the r46 trim did in
fact delete one of the two statements of the archive-reproduction figure (0.0047 pp), which the
per-part check flagged and an auto-refresh would have silently blessed.

The property that matters is not "the multiset is identical" but "**every number the paper
asserted at the start is still asserted somewhere in the paper (article ∪ supplementary)**", or,
if it is not, that a per-token reason names what superseded it.

r54i, and this is the point of the 28 entries: the two Tier-2 cells `p_aitovis` and `p_vistod15`
were **pre-declared** to escalate from n = 3 to n = 10, and the same happened to `dota15` and to
the per-epoch limitation.  When the escalation ran, the n = 3 numbers left the paper *by design*
and were replaced by the n = 10 ones.  Those numbers are therefore NOT hand-waved away here: each
token gets its own entry, generated from the table below, naming the cell, the quantity, the
artifact that holds it, and the value that replaced it.  Every stated replacement is then
**checked against the text on disk** (`REPLACEMENTS_MUST_BE_PRESENT`), so a declaration cannot
claim a supersession that did not happen, and `evidence` files are required to exist.
Also: the index in `vanished_evidence_r54i.json` is regenerated on every run from the measurement,
so it cannot silently describe an older revision of the paper.

Read-only.
"""
import collections
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
BASE = os.path.join(W, 'P2_English_v0.1.md.bak_before_r39_20260917')   # before the r41-r46 work
ART = os.path.join(W, 'P2_English_submission_blind_v1.md')
SUP = os.path.join(W, 'P2_Supplementary_English_v0.1.md')
INDEX = os.path.join(W, 'work', 'vanished_evidence_r54i.json')

# ---------------------------------------------------------------------------------------
# r54i: the vanishing tokens, one entry per token, grouped by the escalation that replaced
# them.  Fields: token -> (vintage, quantity, where it is evidenced, what replaced it in the
# paper, the value(s) that must therefore be present in the paper today).
# The three groups are the n = 3 vintages that the pre-declared escalations superseded.
# ---------------------------------------------------------------------------------------
SUPERSEDED_BY_ESCALATION = {
    'p_aitovis (Δgap = −1.114 at n = 3)': {
        'cell': '`p_aitovis`', 'n_old': 3, 'n_new': 10,
        'evidence': ['核对_两条审稿意见_20260916.md', 'work/x1_gap_analysis_20260918.txt',
                     'x1_tier2_20260918/teval.csv'],
        'replaced_by': 'Δgap −1.226 (95 % CI [−1.370, −1.081], p = 1.3×10⁻⁸)',
        'after': '−1.226',
        'tokens': {
            '0.0173': 'the n = 3 paired-t p of the headline cell (printed as 0.0173 in §5.1 Tier 2)',
            '0.476': 'the upper end of its n = 3 95 % CI [−1.752, −0.476]',
            '1.752': 'the lower end of that n = 3 95 % CI',
            '1.11': 'the same cell\'s n = 3 Δgap as printed in the mechanism table '
                    '(`gap_mechanism_20260916.txt`: "p_aitovis Δgap = −1.11", the 2-dp rounding '
                    'of −1.114; the −1.114 spelling of the same number is declared separately)',
            '10.08': 'M_test baseline arm at n = 3',
            '10.41': 'M_test strategy arm at n = 3',
            '11.23': 'M_val baseline arm at n = 3',
            '12.67': 'M_val strategy arm at n = 3',
        },
        'after_also': ['10.21', '10.40', '11.24', '12.66'],
    },
    'p_vistod15 (Δgap = −3.580 at n = 3)': {
        'cell': '`p_vistod15`', 'n_old': 3, 'n_new': 10,
        'evidence': ['核对_两条审稿意见_20260916.md', 'work/x1_gap_analysis_20260918.txt',
                     'gap_mechanism_20260916.txt'],
        'replaced_by': 'Δgap −3.315 (95 % CI [−3.676, −2.953], p = 6.5×10⁻⁹)',
        'after': '−3.315',
        'tokens': {
            '0.0182': 'the n = 3 paired-t p of the second headline cell',
            '5.686': 'the lower end of its n = 3 95 % CI [−5.686, −1.474]',
            '1.474': 'the upper end of that n = 3 95 % CI',
            '16.72': 'M_val baseline arm at n = 3',
            '24.02': 'M_val strategy arm at n = 3',
            '11.52': 'M_test baseline arm at n = 3',
            '15.24': 'M_test strategy arm at n = 3',
            # the same cell's n = 3 three-component decomposition (gap_mechanism_20260916.txt)
            '3.58': 'its n = 3 Δgap as printed in the decomposition table (rounded)',
            '7.52': 'its n = 3 final-epoch val difference',
            '3.71': 'its n = 3 `−test diff` component',
        },
        'after_also': ['16.96', '23.93', '11.63', '15.26', '−7.072', '−0.213', '+3.971'],
    },
    'dota15 (within-domain probe, Δgap = +0.589 at n = 3)': {        'cell': '`dota15`', 'n_old': 3, 'n_new': 10,
        'evidence': ['核对_两条审稿意见_20260916.md', 'work/x1_gap_analysis_20260918.txt',
                     'work/write_x3x8_into_paper_20260918.py'],
        'replaced_by': 'Δgap +0.449 (95 % CI [+0.309, +0.589], p = 4.9×10⁻⁵, 10+/0−)',
        'after': '+0.449',
        'tokens': {
            '0.868': 'M_val strategy arm at n = 3 (the cell entered at n = 3, not 10)',
            '0.279': 'M_val baseline arm at n = 3',
            '0.208': 'its n = 3 paired-t p',
            '0.073': 'the lower end of its n = 3 95 % CI [+0.073, +1.105]',
            '1.105': 'the upper end of that n = 3 95 % CI',
            '4.91': 'the n = 3 statistic printed in the same table row (§5.1 Tier 2)',  # page 4.91? no: the t/r
        },
        'after_also': ['+0.941', '+0.492', '0.196', '7.23', '+0.309', '+0.589'],
    },
    'the per-arm transfer-fit quality (§8.3), superseded by the complete-curve refit': {
        'cell': 'the per-arm κ fit (§8.3; 81 baseline runs / 80 strategy runs on the sampled grid)',
        'n_old': None, 'n_new': None,
        'evidence': ['work/r33_epoch_curve_paper_20260916.py', 'work/r33f_finalize_20260916.py',
                     '变更日志.md'],
        'replaced_by': ('the same two R² on the complete curve (806 evaluations): '
                        'baseline κ = 0.600 with R² 0.946 and strategy κ = 0.767 with '
                        'R² 0.951 (article §8.5)'),
        'after': '0.946',
        'tokens': {
            '0.743': 'the per-arm R² of the baseline arm κ on the sampled grid (202 evaluations)',
            '0.933': 'the per-arm R² of the strategy arm κ on the same grid',
        },
        'after_also': ['0.951'],
    },
    'the per-epoch limitation (§8), superseded by the complete-curve re-evaluation': {
        'cell': 'the 41 three-way runs', 'n_old': None, 'n_new': None,
        'evidence': ['work/x3b_perepoch_corrected_20260918.py',
                     'xeval_perepoch_20260918/matrix_perepoch.csv'],
        'replaced_by': ('the limitation was removed because the complete curve was evaluated: '
                        '806 evaluations, 0 failures (article §8.7)'),
        'after': '806',
        'tokens': {
            '205': 'the "202 rather than 205 evaluations" count in the sampled-grid limitation',
            '4.6': 'the "a full sweep is about 4.6 h and was not run" half of the same limitation',
        },
        'after_also': ['202'],
    },
}


def build_declarations():
    """One DECLARED_ABSENT entry per token, generated from the table above (not hand-typed)."""
    decl, index = {}, {}
    for group, meta in SUPERSEDED_BY_ESCALATION.items():
        for tok, what in meta['tokens'].items():
            vintage = ('n = %d' % meta['n_old']) if meta['n_old'] else 'the sampled-grid vintage'
            decl[tok] = ('r54i · %s: %s — vintage %s, %s. Held in: %s. Replaced in the paper by: '
                         '%s%s. (Vacated by a pre-declared escalation, so nothing is hidden: the '
                         'supersession is disclosed in the article.)'
                         % (vintage, what, vintage, group, ' / '.join(meta['evidence']),
                            meta['replaced_by'],
                            ('' if not meta['after_also'] else
                             '；同批 n = 10 数字 %s' % ', '.join(meta['after_also']))))
            index[tok] = {'group': group, 'quantity': what, 'vintage': vintage,
                          'n_old': meta['n_old'], 'n_new': meta['n_new'],
                          'replaced_by': meta['replaced_by'],
                          'evidence': meta['evidence'],
                          'also_present_n_new': meta['after_also']}
    return decl, index


# r54i: every replacement this guard claims must be FOUND in the article/supplement text.
# Format: token -> list of strings that must occur in article ∪ supplement.
REPLACEMENTS_MUST_BE_PRESENT = {
    '0.0173': ['1.3×10⁻⁸', '0.001953'],
    '0.0182': ['6.5×10⁻⁹', '0.001953'],
    '1.752': ['1.226'],
    '1.11': ['1.226'],
    '0.476': ['1.226'],
    '10.08': ['10.21'],
    '10.41': ['10.40'],
    '11.23': ['11.24'],
    '12.67': ['12.66'],
    '5.686': ['3.315'],
    '1.474': ['3.315'],
    '16.72': ['16.96'],
    '24.02': ['23.93'],
    '11.52': ['11.63'],
    '15.24': ['15.26'],
    '3.58': ['3.315'],
    '7.52': ['7.072'],
    '3.71': ['3.971'],
    '0.743': ['0.946'],
    '0.933': ['0.951'],
    '0.868': ['0.941'],
    '0.279': ['0.492'],
    '0.208': ['0.196'],
    '0.073': ['0.309'],
    '1.105': ['0.589'],
    '4.91': ['7.23', '0.449'],
    '205': ['806'],
    '4.6': ['806'],
}

# Numbers of the pre-r41 manuscript that left for other reasons, judged one by one.  These are
# not part of the escalation and their absence is independent of r54i.
DECLARED_ABSENT_OTHER = {
    '052': "fragment of the governing Chinese draft's md5 `8de3dd059a0665aa052b6e79b94afca7`, "
           'removed with the provenance block (internal metadata, never part of the paper)',
    '059': 'same md5 fragment',
    '0665': 'same md5 fragment',
    '20260913': 'the frozen pre-registration date; now written ISO-style as `2026-09-13`, so the '
                'fact survives and only the notation changed',
    '9.1': 'the `§9.1` sub-heading number, removed when §9 was compressed (its content is in the '
           'same section, and the supplementary carries the full protocol)',
    '9.2': 'r121 · the stale provenance pointers in Tables S24/S25 (`moved from *9.2 Result: the '
           'criterion is not met*`): §9 has had no sub-sections since it was compressed, so the '
           'pointers now read `§9` and the tables themselves are unchanged.  Same family as 9.1/9.4.',
}


# ★ 2026-09-21：**随模块移交给 P1** 的数字。
#   用户裁定把 §9（登记多目标复制）与 §8.1–8.2（三方协议定义 + 其在 P1 语料上的结果）
#   整体交给 P1（见 `实验内容共享\P2→P1_模块移交_登记复制与三方协议_20260921.md`）。
#   这些数字因此从 P2 正文消失，但**没有丢** —— 它们随件到了一个具名文件。
#   ⇒ 判据不是"我说移交了"，而是**逐个断言能在那个具名文件里命中**（见 declarations 里的检查）。
TRANSFERRED_LEDGER = os.path.join(W, '实验内容共享', 'P2→P1_逐值移交清单_20260921.md')

DECLARED_ABSENT_TRANSFERRED = {
    '0.0024': 'registration replication: T1-c\'s BH-surviving q (q = 0.05, m = 3) — module transferred',
    '0.0157': 'registration replication: p of control C\'s three-seed predecessor (+0.707) — module transferred',
    '0.707': 'registration replication: control C\'s three-seed predecessor Δ — module transferred',
    '3.38': 'remediation: one of the three r10_p_* clean-protocol readings that agree in sign — module transferred',
    '3.60': 'remediation: same set (largest cell) — module transferred',
    '3.61': 'remediation: same set — module transferred',
    '3.74': 'remediation: same set (largest cell) — module transferred',
    '3.75': 'remediation: same set — module transferred',
    '3.80': 'remediation: same set (largest cell) — module transferred',
    '7.1894': 'the published MAFA→mask displacement value, reproduced value-by-value in the transferred module — module transferred',
    '8.2': "the `§8.2` sub-heading number; that sub-section (protocol + its results on the companion's corpora) is transferred, and the protocol is now cited as §8.1",
    '9.4': "the `§9.4` sub-heading number; that sub-section went with the registration module",
}


def tokens(s):
    """Numeric tokens, with list markers and ordinary formatting excluded."""
    s = re.sub(r'(?m)^\s*\d+[.)]\s+', '', s)
    s = re.sub(r'(?m)(\s)\d+[.)]\s+', r'\1', s)
    return collections.Counter(re.findall(r'\d+(?:[.,]\d+)*', s))


def main():
    for p in (BASE, ART, SUP):
        if not os.path.exists(p):
            sys.exit('!! 缺文件 %s' % p)
    base = io.open(BASE, encoding='utf-8').read()
    art = io.open(ART, encoding='utf-8').read()
    sup = io.open(SUP, encoding='utf-8').read()

    gen, index = build_declarations()
    DECLARED_ABSENT = dict(DECLARED_ABSENT_OTHER)
    DECLARED_ABSENT.update(gen)
    DECLARED_ABSENT.update(DECLARED_ABSENT_TRANSFERRED)

    # ★ 断言：每个"已随模块移交"的数字**必须真的**能在逐值清单里命中。
    #   否则声明就成了空话 —— 这条检查把"我声称移交了"变成"文件里查得到"。
    if os.path.exists(TRANSFERRED_LEDGER):
        ledger = open(TRANSFERRED_LEDGER, encoding='utf-8').read()
        ledger_missing = [k for k in DECLARED_ABSENT_TRANSFERRED
                          if not re.search(r'(?<![\d.])' + re.escape(k) + r'(?![\d])', ledger)]
    else:
        ledger_missing = ['<ledger file missing: %s>' % TRANSFERRED_LEDGER]
    if ledger_missing:
        print('!! 声明"已随模块移交"但逐值清单里查不到：%s' % ledger_missing)
        print('   ⇒ 不会把"移交"当作已证的落点。')
        for k in ledger_missing:
            DECLARED_ABSENT.pop(k, None)

    tb, ta, ts = tokens(base), tokens(art), tokens(sup)
    now = ta + ts
    absent = set(tb) - set(now)
    undeclared = sorted(a for a in absent if a not in DECLARED_ABSENT)
    declared_hit = sorted(a for a in absent if a in DECLARED_ABSENT)
    reduced = {k: tb[k] - now.get(k, 0) for k in tb if now.get(k, 0) and now[k] < tb[k]}
    gained = now - tb

    print('=' * 76)
    print('论文整体（正文 ∪ 补充材料）的数字留存检查')
    print('=' * 76)
    print('  基线：%s（r41 结构改动之前）' % os.path.basename(BASE))
    print('  现值：匿名投稿正文 + 英文补充材料')
    print('  基线数字令牌 %d 种 / %d 个；现值 %d 种 / %d 个'
          % (len(tb), sum(tb.values()), len(now), sum(now.values())))
    print()

    # --- the declarations must be evidence-backed, not merely asserted -------------------
    whole = art + '\n' + sup
    unsupported, missing_evidence = [], []
    for tok, needles in REPLACEMENTS_MUST_BE_PRESENT.items():
        if tok not in gen:
            unsupported.append('%s（声明里没有这个令牌）' % tok)
            continue
        for nd in needles:
            if nd not in whole:
                unsupported.append('%s 的替代值 %r 在论文里找不到' % (tok, nd))
    for group, meta in SUPERSEDED_BY_ESCALATION.items():
        for ev in meta['evidence']:
            if not os.path.exists(os.path.join(W, ev.replace('/', os.sep))):
                missing_evidence.append('%s → %s' % (group, ev))
    print('  声明的替代值复核：%d 条替代都必须真的出现在论文里 —— %s'
          % (len(REPLACEMENTS_MUST_BE_PRESENT),
             'ok' if not unsupported else 'FAIL %s' % unsupported))
    print('  声明引用的证据件必须在盘上：%s'
          % ('ok' if not missing_evidence else 'FAIL %s' % missing_evidence))
    print()

    if declared_hit:
        print('  已声明且逐条判定的消失（%d 种）：' % len(declared_hit))
        for k in declared_hit:
            print('     %-12s %s' % (k, DECLARED_ABSENT[k]))
        print()

    io.open(INDEX, 'w', encoding='utf-8', newline='\n').write(
        json.dumps({'generated_by': 'work/verify_no_number_lost_20260917.py',
                    'round': 'r54i', 'generated_from': [os.path.basename(BASE),
                                                        os.path.basename(ART),
                                                        os.path.basename(SUP)],
                    'absent_tokens': declared_hit, 'index': index},
                   ensure_ascii=False, indent=1) + '\n')
    print('  已重新生成逐条索引 %s（%d 条）' % (os.path.basename(INDEX), len(index)))
    print()

    if unsupported or missing_evidence:
        print('  !! 声明本身不成立：替代值或证据件对不上。')
        if unsupported:
            print('     %s' % unsupported)
        if missing_evidence:
            print('     %s' % missing_evidence)
        return 1
    if undeclared:
        print('  !! 有数字在整篇论文里**完全消失且未声明**（%d 种）：' % len(undeclared))
        for k in undeclared:
            print('     %-14s 基线 %d 次 → 现值 0 次' % (k, tb[k]))
        print()
        print('  ⇒ 必须解释并补回，或在 DECLARED_ABSENT 里逐条写明理由（附替代值）。')
        return 1
    if absent:
        print('  ok  基线里出现过的每一个数字，除上述已逐条判定者外，都仍出现 ≥1 次')
    else:
        print('  ok  基线里出现过的每一个数字，在正文或补充材料里都仍然出现 ≥1 次')
    if reduced:
        print('  说明：%d 种数字的出现次数**减少**（去重/压缩），这是允许的：' % len(reduced))
        for k in sorted(reduced)[:12]:
            print('     %-14s %d → %d 次' % (k, tb[k], now[k]))
        if len(reduced) > 12:
            print('     … 另有 %d 种' % (len(reduced) - 12))
    print('  %d 个新令牌是 r41–r54 的修正与新实验引入的（两种读法的计数、加权口径、单评者标签、'
          'n = 10 升级与 S31–S33 结果表等）' % len(gained))
    print()
    print('失败 0 项')
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
