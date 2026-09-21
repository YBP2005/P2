# -*- coding: utf-8 -*-
"""r42: verify the prose compression against what must survive, not against phrasing.

First version counted the literal phrase "we do not" and flagged a drop -- but the
sentence had been rewritten as "We claim neither to be first to audit ... : both are
taken", which preserves the claim. A string check was measuring spelling, not content.
(This is the project's oldest lesson: compare the quantity, not the string.)

So the check is now: a list of **required claims and disclosures**, each written as a
rephrase-tolerant pattern, every one of which must survive somewhere in the compressed
manuscript. Plus the mechanical invariants that are genuinely mechanical: numeric
tokens, citations, headings, pointer lines, table rows, References list.

Read-only.
"""
import collections
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = r'E:\workplace\work'
TAG = '.bak_before_r42_compress_20260917'
# ---------------------------------------------------------------------------------------
# Declared intentional changes, in three rounds. ANY change not listed here still fails.
#
# r45  the two panel-driven fixes: the §9.2 BH count (1/3 -> 2/3) and the §8.6 weighting
#      declaration (19 %/32.3 %/34.0 %), plus the stale anchor counts (220/227/247 -> one 247).
# r46A the mechanical hard defects H5, H7, H9, H15, H16, H18, H21, H22, H23.
# r46B H6 (COCO option C: the second reading of one row), H8 (70 -> 80 runs), H14 (single-rater
#      label), H19 (the §8.3 estimand renamed to seed inflation).
# r46C H9b, H10, H11, H12, H13, H17 (documentation and consistency).
# r46S the structural step: §9 compressed to its findings/numbers/disclosures (dropping its three
#      sub-headings), and four evidence tables restored into the article as Table 1-4 -- which
#      removes three pointer lines and adds table rows. Measured effect: page-neutral (38 -> 38),
#      so the point of the step is M12 (headline numbers checkable in the article), not the cap.
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# DEPRECATED — kept for history, no longer read by this script.
# The five tables below (POST_COMPRESSION_EDITS / _XREF / _HEADINGS / DECLARED_POINTERS /
# DECLARED_TABLE_ROWS) were the hand-maintained declaration of changes. They were replaced
# by the verified round chain (see KNOWN_ROUNDS / chain_declaration below), which composes
# the same information from the per-round snapshots and re-verifies it against disk. Do not
# add entries here: a change that is not in the chain will fail this check, which is the
# point. Left in place only so the history of what was declared when remains readable.
# ---------------------------------------------------------------------------------------
POST_COMPRESSION_EDITS = {
    1: {'loss': {'220': 1}, 'gain': {'3': 1, '7.1': 2, '6.1': 1, '10': 1, '1': 1, '11': 1, '15': 1}},
    2: {'loss': {'8': 1, '6': 1, '4': 1, '5.74': 1, '1.9': 1, '8.41': 1, '7.6': 1, '4.69': 1, '1.1': 1, '4.91': 1, '0.039': 1, '33.0': 1, '21.2': 1, '0.507': 1}, 'gain': {'2': 3, '12': 1, '1': 2, '11': 1, '20260916': 2, '95': 2, '5': 1, '3': 2, '0.799': 1, '0.382': 1, '0.416': 1, '0.240': 1, '0.255': 1, '0.578': 1, '1.038': 1, '0.512': 1, '0.526': 1, '0.207': 1, '0.386': 1, '0.665': 1, '15': 2, '0.534': 1, '0.262': 1, '0.183': 1, '0.141': 1, '0.403': 1, '0.868': 1, '0.279': 1, '0.589': 1, '0.208': 1, '0.073': 1, '1.105': 1, '0': 2, '0.779': 1, '0.0053': 1, '0.461': 1, '1.114': 1, '1.752': 1, '0.476': 1, '3.580': 1, '5.686': 1, '1.474': 1, '2.46': 1, '13.66': 1, '0.054': 1, '7.1': 2, '5.3': 1, '13': 1, '0.05': 2, '0.00385': 1, '9.2': 1, '2.2': 1, '5.5': 1}},
    3: {'loss': {'8': 1, '5': 1, '0.0020': 2, '0.001953': 1}, 'gain': {'3': 5, '19': 16, '20260916': 1, '13': 3, '15': 3, '21': 1, '10': 1, '16': 1, '27': 1, '6.1': 1, '53': 1, '68': 1, '4': 5, '12': 2, '63': 1, '80': 1, '2': 2, '28': 1}},
    4: {'loss': {'8': 4, '0': 2, '41': 3, '164': 1, '84': 1, '256': 1, '20260916': 1, '0.0047': 1, '0.0021': 1, '19': 1, '95': 1, '20260913': 1, '15': 1, '9.1': 1, '1': 5, '100': 1, '0.30': 3, '0.01': 1, '9.2': 1, '25': 1, '0.168': 1, '9.3': 1, '2502.12524': 1}, 'gain': {'5': 1, '10': 4, '6': 1, '2': 2, '9': 1, '18': 1, '4': 1, '1.469': 1, '0.735': 1, '0.865': 1, '0.151': 1, '0.691': 1, '0.507': 1, '73': 1, '0.605': 1, '0.158': 1, '20': 1, '0.786': 1, '0.377': 1, '48': 1, '32.3': 1, '34.0': 1, '60': 1, '80': 1, '1.490': 1, '0.0141': 1, '0.0020': 1}},
}

POST_COMPRESSION_XREF = {
    1: {'new': {'§7.1': 2, '§6.1': 1}, 'lost': {}},
    2: {'new': {'§12': 1, '§5': 1, '§7.1': 2, '§5.3': 1, '§10': 1, '§9.2': 1, '§2.2': 1, '§5.5': 1}, 'lost': {}},
    3: {'new': {'§3': 1, '§10': 1, '§6.1': 1}, 'lost': {}},
    4: {'new': {}, 'lost': {}},
}

POST_COMPRESSION_HEADINGS = {
    1: {'new': [], 'lost': []},
    2: {'new': [], 'lost': []},
    3: {'new': ['### 6.1 The result under four units (single-rater judgements)'], 'lost': ['### 6.1 The result under four units']},
    4: {'new': ['### 8.3 A direct measurement of selection inflation', '### 8.4 The three variance components: the excluded one is the smaller in this sample', "### 8.6 The premium's realization rate: **19 %**", "### 9.4 What this section has to do with the paper's subject"], 'lost': ['### 8.3 ⭐ A direct measurement of selection inflation', '### 8.4 The three variance components: the excluded one is not the dominant one', "### 8.6 ⭐ The premium's realization rate: **19 %**", '### 9.1 What was registered', '### 9.2 Result: the **criterion is not met** (the third row is the one that passes)', '### 9.3 The near-matched control C: the gain does **not** depend on a label-space change', "### 9.4 ⭐ What this section has to do with the paper's subject"]},
}

# The pointer lines and table rows the article is expected to carry now (the structural step
# legitimately changed both: three pointers became tables, and Table 4 added rows to part 4).
DECLARED_POINTERS = {
    1: ['> **Table S1** → Supplementary §S8.'],
    2: ['> **Table S2** → Supplementary §S8.', '> **Table S3** → Supplementary §S8.', '> **Table S7** → Supplementary §S8.', '> **Tables S8–S10** → Supplementary §S8.'],
    3: ['> **Table S12** → Supplementary §S8.', '> **Table S13** → Supplementary §S8.', '> **Table S14** → Supplementary §S8.', '> **Table S15** → Supplementary §S8.', '> **Table S16** → Supplementary §S8.'],
    4: ['> **Table S17** → Supplementary §S8.', '> **Table S18** → Supplementary §S8.', '> **Table S19** → Supplementary §S8.', '> **Tables S21–S23** → Supplementary §S8.'],
}

DECLARED_TABLE_ROWS = {1: 0, 2: 13, 3: 8, 4: 29}

# The assembled manuscript this suite's substance check runs on.
COMBINED = r'E:\workplace\P2_English_v0.1.md'

# ---------------------------------------------------------------------------------------
# Claims and disclosures that must survive the compression somewhere in the assembled
# manuscript, each written as a rephrase-tolerant pattern.  The point is that compression
# may rewrite a sentence but may not silently drop an obligation: the finding itself, the
# superseded-count warning, the first-report disclaimer, the negative registered result,
# the weighting disclosure and the artifact-pointer promise.
#
# Deliberately NOT a transcription of the current wording: each pattern names the concept
# and tolerates rephrasing, so a rewrite passes and a deletion fails.  If a pattern ever
# stops matching, the right response is to find out what happened to the claim, not to
# loosen the pattern.
# ---------------------------------------------------------------------------------------
REQUIRED = [
    ('val/test 两键同路径（finding 本体）', r'val\s*(?:==|=|与)\s*test|two keys[^.\n]{0,60}same path|alias'),
    ('选择溢价 = best − final 的定义', r'selection premium'),
    ('四种计数单位', r'four (?:counting )?units|four units'),
    ('旧计数已被更正、不得再引（本文自己的更正声明）', r'Correction to the first version|contradicting the recomputation'),
    ('不主张首先报告（归因声明）', r'neither[^.\n]{0,40}first|not (?:the )?first to'),
    ('付费差额 Δgap', r'\\?Delta\s*gap|Δgap'),
    ('实现率', r'realization rate'),
    ('注册复现的判据未达成（负结果）', r'(?:criterion|predictions?)[^.\n]{0,60}not met|not met by'),
    ('单评者标注（口径声明）', r'single[- ]rater'),
    ('COCO 两种读法并存（option C）', r'both readings|two readings|states both'),
    # r51: this entry used to require the panel's provisional arithmetic ("making 80 as
    # reported").  The run directories are the primary record and they show ten seeds per arm
    # in the appended control — 20 runs, total 90 — so the check now requires the corrected
    # fact, and the label records where the number comes from.
    ('运行数以 run 目录为准：90 = 70 登记 + 20 追加', r'90 runs in total'),
    # r53: this entry used to require "no cell significant", which was the CORRECT statement until
    # the two Tier-2 cells were escalated to n = 10.  Their p-values then moved to the front of the
    # BH ordering and lifted the lines behind them, so the count REVERSED to three.  The old claim
    # is now false; the check requires the new one **including the statement that it is a reversal**
    # (a silent swap is exactly the kind of edit this file exists to catch).
    ('多重比较后 3 格存活，并写明这是对旧计数的反转',
     r'now leaves three cells significant|This reverses what we reported'),
    ('n = 3 置换检验无分辨力的方法学规则仍在位',
     r'smallest attainable two-sided p'),
    ('X1 两格升到 n = 10、置换 p 达下界且判据满足',
     r'permutation p = \*\*0\.001953\*\*'),
    ('X8 dota15 升到 n = 10、面板预先声明的判据满足',
     r'\+0\.449 pp'),
    ('§8.7 的稳定性主张被收窄（自我更正，不是悄悄保留）',
     r'too strong for one of the two'),
    ('归档端点被重测锁定为 best.pt×test（0.0046 pp）',
     r'0\.0046 pp'),
    ('完整逐 epoch 全扫：806 次评测、202 点逐点重合',
     r'806 retained checkpoints'),
    ('本文自身的缺陷一节', r'Our own defects'),
    ('格等权（n=1 格占 20%）的口径声明', r'cell[- ]equal|equal[- ]weight|19\.4|32\.3'),
    ('近似匹配对照 C', r'control C'),
    ('每个数字带本地指针', r'local pointer|artifact pointer|points? to (?:a|the) (?:local|artifact)'),
    ('两篇共用同一套过程规程（不主张原创）', r'same set of[^.\n]{0,40}protocols|shared[^.\n]{0,30}protocols'),
]


def nums(s):
    """Numeric tokens, EXCLUDING markdown ordered-list markers.

    Converting a numbered list into prose (which the compression legitimately does)
    removes the ordinals 1..n. Those are formatting, not content -- counting them would
    report a formatting choice as a lost number, the same class of false positive as the
    docx image-alt-text case. The substance of a converted list is checked by the
    REQUIRED-claims list below instead.
    """
    s = re.sub(r'(?m)^\s*\d+[.)]\s+', '', s)
    s = re.sub(r'(?m)(\s)\d+[.)]\s+', r'\1', s)
    return collections.Counter(re.findall(r'\d+(?:[.,]\d+)*', s))


def cites(s):
    return collections.Counter(re.findall(r'\[\d+\]', s))


def heads(s):
    return re.findall(r'(?m)^#{1,6} .*$', s)


def pointers(s):
    return sorted(re.findall(r'(?m)^> \*\*Tables? S[\dS–]+\*\* → Supplementary §S8\.$', s))


# ---------------------------------------------------------------------------------------
# The declared changes are no longer hand-maintained dicts.  They are composed from the
# per-round snapshots that the rounds left on disk (work/round_stages_20260917.json, built
# by work/gen_round_stages_20260917.py), and every claim in that record is re-verified
# against the files NOW: each stage's endpoint md5 must match, and each stage's measured
# delta must equal the recorded one.  The chain must start at the pre-compression baseline
# and end at the current file, so any later edit to a part file breaks this check until the
# round that made it is named below.  An unbacked edit therefore cannot pass, and a declared
# change is always attributable to a named round instead of to a blob.
#
# History: the previous version kept one hand-written dict per part, and it twice went
# stale in a way that would have excused an undeclared numeric change (the r45 anchor-count
# fix, then the r46 structural step): the auto-refresh that "fixed" it the first time simply
# recorded whatever it found, which is a rubber stamp, not a check.
# ---------------------------------------------------------------------------------------
STAGES_JSON = os.path.join(WORK, 'round_stages_20260917.json')
KNOWN_ROUNDS = {
    'r39': 'reference list and provenance pass',
    'r39b': 'second reference/provenance pass',
    'r41_move': 'evidence tables and figures moved to the Supplementary',
    'r41_pointers': 'pointer lines added for each moved table',
    'r41_pointers2': 'pointer-line wording settled',
    'r42_compress': 'pre-compression baseline of this check',
    'r43_finaltrim': 'final trim before the page measurement',
    'r45_anchorcount': 'stale anchor counts collapsed to one (220/227/247 -> 247)',
    'r45_referents': 'dangling referents repaired',
    'r45_scope': 'scope labels for the reported counts',
    'r45_reviewfix': '§9.2 BH count and §8.6 weighting declaration',
    'r45_driveletters': 'drive letters written as words',
    'r46_batchA': 'mechanical hard defects H5/H7/H9/H15/H16/H18/H21/H22/H23',
    'r46_batchA2': 'hard defects continued',
    'r46_batchB': 'H6 (COCO option C), H8 (70 -> 80 runs), H14, H19',
    'r46_batchC': 'H9b, H10, H11, H12, H13, H17',
    'r46_batchC2': 'consistency follow-ups',
    'r46_H6': 'H6 COCO second reading',
    'r46_H20': 'H20 n-split statement',
    'r46_H20b': 'H20 follow-up',
    'r46_H23': 'H23 referent',
    'r46_sec9': 'structural step: §9 compressed, four tables restored to the article',
    'r46_restore': 'structural step: tables and pointer lines restored/removed',
    'r46_restore2': 'structural step: final state of that round',
    'inv': 'figure/table inventory corrected (Tables 1-4 back in the article)',
    'inv2': 'figure/table inventory corrected again: wrong descriptions, and the two numbering axes kept apart',
    'r48_count': 'declared anchor count synced with the real one (247 -> 280), with a new guard X82',
    'r48_xref': 'three dangling section pointers repaired (§9.2 x2, §1.4 to an unsubmitted record)',
    'r48_provhash': 'the provenance block re-states the governing draft hash with the date it was taken',
    'r50_kappa': 'X2 re-analysis written in: κ with a run-clustered interval, the arm split, the realization interval',
    'r50_anchorcount': 'declared anchor count re-synced (280 -> 282) after adding X83/X84',
    'r51_x10': 'X10 alias-bias audit written in (val side) + the run count corrected to 90',
    'r51_anchorcount': 'declared anchor count re-synced (282 -> 284) after adding X85/X86',
    'r51_provhash': 'the governing draft hash re-synced after the X10 edit',
    'r51_rank8': 'rank 8: selection-bias related work + four verified references (40 -> 44)',
    'r51_refcount': 'reference-count guards moved 40 -> 44 (X43 range, compression check)',
    'r51_provhash2': 'governing-draft hash re-synced after the rank-8 edit',
    'r53_resync': 'r53: X8/X1/X3 results written in (two escalations to n = 10, the complete per-epoch sweep, the seed-convention disclosure); the four article parts re-synced from the assembled file so assemble_en reproduces it',
    # ---- r54v: B (de-duplication) -------------------------------------------------------
    # Three rounds, named so the chain stays attributable.  The reader of the compression
    # check can see exactly what each did to the numeric multiset:
    'dedupB': 'r54v: B de-duplication stage 1+2 (five spans: the per-run WC/tercile numbers of §13 Prop 4 -> pointer to Supplementary S11, the withdrawn σ√(2 ln E) regression -> S11, the "ten positive three negative" recount, the perturbation percentages -> S11, and the per-cell alias audit numbers of §9 -> S12). Removed spans, no claim deleted; E4\'s conclusion sentence kept verbatim.',
    'e5numfix': 'r54v: the three derived totals the §9 alias-audit move had dropped (T1-a +0.198 / T1-c +3.941 / control C +1.133 pp) written back into the article sentence, because "every number carries a pointer" and none of the three existed anywhere else',
    'splicefix': 'r54v: repair of the splice artifact the §9 edit left behind ("**+1.133 pp**.: its YAML separates" -> "**+1.133 pp**; T1-b is excluded by construction, since its YAML separates")',
    'seedcut': 'r54v/P2-2 first cut: the §9 seed-convention paragraph keeps its disclosure and verdict in the article (metadata misleading, seed: 42 is the framework default and does NOT mean the seeds coincide, per-cell results distinct 20/20 / 10/10 / 20/20, re-run reproduces) while the implementation mechanism (--shuffle-seed, ultralytics 8.4.120 not reading args.seed, the identical epoch-by-epoch replays, the args.yaml detail) moves to Supplementary S12 §9.3; 182 -> 110 words',
    'current': 'the live part file',
    # ---- r54v second half: press the article into the venue's own page limit -----------------
    'invcmpct': 'r54v: figure/table inventory compressed for the page limit (390 -> 165 words): the "how the Supplementary is organised" paragraph dropped as index-type text, the moved-table/figure list folded from a 13-row table into prose plus a six-row figure table; every guard payload kept (the four Table N -> S4/S6/S11/S20 mapping rows, Fig. S1-S5, Supplementary S24-S27, the defect-table-stays disclosure)',
    'rowrestore': 'r54v: the four mapping rows restored as table rows after the first attempt had flattened them into prose and the write-after assertion caught the loss',
    'page35': 'r54v: §13.1\'s six-experiment criteria/outcome table moved to Supplementary S31-S33 with one summary sentence in the article (268 -> 94 words); verdicts, the 14.7 pp difficulty gap, G1\' WC -0.069 pp and G4 WC +5.21 pp kept in the article',
    'syntaxfix': 'r54v: syntax repair of two seams the de-duplication left ("Supplementary S11**.\'s 19 %" -> "S11**. This is why §8.6\'s 19 %"; "S11**.–Hochberg" -> the full Proposition 5 heading)',
    'syntaxfix2': 'r54v: syntax repair of two more seams (Proposition 3 lost the subject "every candidate mechanism"; Proposition 4\'s perturbation sentence lost its connective)',
    'guardfix2': 'r54v: guard payloads restored — the figure list back into a table (X39/X71 need `**Fig. S5** | §8.7`) and the Table 4 row back to its full wording (X80)',
    'finalfix': 'r54v: last two seams — the stray punctuation the figure table left ("| §13 |. §10\'s") and the load-bearing claim that both papers share the same process protocols, which the inventory compression had dropped from the article',
    '131cut': 'r54v: §13.1\'s interpretive summary 189 -> 115 words — the per-comparison reasoning and the source list move to Supplementary S31–S33, the aggregate verdict stays in the article',
    'prose': 'r54v: prose-only compression with a numeric-conservation assertion (§8.7 back-reference and meta-sentences, §9 saturated-control parenthesis, §9.4 meta-sentence) — 5 blocks, no digit moved',
    'tablenums': 'r54v: §8.7 numbers already carried by Tables S21–S23 restated as pointers (κ estimate accounting, the per-checkpoint sign values, the closed five-epoch limitation)',
    'blocks': 'r54v: two whole blocks moved to Supplementary S11 keeping their verdicts — §8.7\'s per-checkpoint sign detail (202 -> 117 words) and §13\'s four-budget detail (109 -> 56), which is what brings the article inside the venue\'s 35-page limit under the official geometry',
    'addcites2': 'r54w: first-mention citations added after the pre-launch check found 5 entities named without one at first use — SHWD [25], Mendeley face-mask [27], PASCAL VOC [13] (§4.2 wrote "VOC" unnumbered; [13] is the VOC challenge reference, [15] is Open Images), YOLOv12n [11]; all four reuse existing numbers, so no reference was added and the list is unchanged',
}


def load_chain():
    with io.open(STAGES_JSON, encoding='utf-8') as fh:
        return json.load(fh)


def chain_declaration(part, current_text, chain):
    """Compose the declared changes for one part and re-verify the record against disk.

    Returns (decl, problems).  decl carries num/xref/heading/pointer/row deltas composed
    over the stages from the pre-compression baseline onward.
    """
    problems = []
    rec = chain['parts'].get(str(part))
    if rec is None:
        return None, ['no chain record for this part']
    stages = rec['stages']

    def content(fname, expected_md5):
        if fname == 'en_part%d.md' % part:
            txt = current_text
        else:
            fp = os.path.join(WORK, fname)
            if not os.path.exists(fp):
                problems.append('snapshot missing on disk: %s' % fname)
                return None
            txt = io.open(fp, encoding='utf-8').read()
        if hashlib.md5(txt.encode('utf-8')).hexdigest() != expected_md5:
            problems.append('snapshot changed since the record was made: %s' % fname)
            return None
        return txt

    start = None
    for k, st in enumerate(stages):
        if st['produced_by'] not in KNOWN_ROUNDS:
            problems.append('unnamed round in the chain: %r' % st['produced_by'])
        if st['from'].endswith(TAG):
            start = k
    if start is None:
        problems.append('chain does not reach the pre-compression baseline')
        return None, problems

    decl = {'num_loss': collections.Counter(), 'num_gain': collections.Counter(),
            'xref_new': collections.Counter(), 'xref_lost': collections.Counter(),
            'head_new': [], 'head_lost': [], 'ptr_new': [], 'ptr_lost': [],
            'rows_delta': 0, 'rounds': []}

    net_num = collections.Counter()      # + means the token was ADDED
    net_xref = collections.Counter()
    net_head = collections.Counter()
    net_ptr = collections.Counter()
    rows_delta = 0

    for st in stages[start:]:
        a = content(st['from'], st['from_md5'])
        b = content(st['to'], st['to_md5'])
        if a is None or b is None:
            continue
        # re-measure this stage and require the record to match
        if dict(nums(a) - nums(b)) != st['num_loss'] or dict(nums(b) - nums(a)) != st['num_gain']:
            problems.append('stage %s: recorded numeric delta does not match disk' % st['produced_by'])
        xb, xa = collections.Counter(re.findall(r'§\s?\d+(?:\.\d+)?', a)), \
            collections.Counter(re.findall(r'§\s?\d+(?:\.\d+)?', b))
        if dict(xa - xb) != st['xref_new'] or dict(xb - xa) != st['xref_lost']:
            problems.append('stage %s: recorded §-xref delta does not match disk' % st['produced_by'])
        # Compose the NET effect, because consecutive rounds cancel: a later round can
        # restore a number an earlier one removed, and summing gross losses and gains
        # separately would then claim a change that the text does not have.
        # NOTE: Counter's +, - and -= operators DROP non-positive results (they are
        # "positive multiset" operations), which silently erases every loss. update() is
        # the signed accumulation, so it is used here instead.
        net_num.update(st['num_gain'])
        net_num.update({k: -v for k, v in st['num_loss'].items()})
        net_xref.update(st['xref_new'])
        net_xref.update({k: -v for k, v in st['xref_lost'].items()})
        net_head.update(st['head_new'])
        net_head.update({k: -v for k, v in collections.Counter(st['head_lost']).items()})
        net_ptr.update(st['ptr_new'])
        net_ptr.update({k: -v for k, v in collections.Counter(st['ptr_lost']).items()})
        rows_delta += st['rows_to'] - st['rows_from']
        decl['rounds'].append(st['produced_by'])

    def split_net(net):
        """Counter of net changes -> (new, lost) where lost is positive-counted."""
        new = collections.Counter({k: v for k, v in net.items() if v > 0})
        lost = collections.Counter({k: -v for k, v in net.items() if v < 0})
        return new, lost

    decl['num_gain'], decl['num_loss'] = split_net(net_num)
    decl['xref_new'], decl['xref_lost'] = split_net(net_xref)
    decl['head_new'], decl['head_lost'] = split_net(net_head)
    decl['ptr_new'], decl['ptr_lost'] = split_net(net_ptr)
    decl['rows_delta'] = rows_delta

    tail = content(stages[-1]['to'], stages[-1]['to_md5'])
    if tail is None:
        problems.append('the chain does not end at the current file')
    elif tail != current_text:
        problems.append('the record ends at a state that is not the current file')
    return decl, problems


def main():
    fails = []
    print('=' * 76)
    print('压缩保真校验 v2（对照 %s）' % TAG)
    print('=' * 76)
    tot_before = tot_after = 0
    for i in (1, 2, 3, 4):
        p = os.path.join(WORK, 'en_part%d.md' % i)
        b = p + TAG
        name = 'en_part%d.md' % i
        print('\n--- %s' % name)
        if not os.path.exists(b):
            print('   FAIL 找不到备份')
            fails.append(name + ':nobackup')
            continue
        before = io.open(b, encoding='utf-8').read()
        after = io.open(p, encoding='utf-8').read()
        wb, wa = len(before.split()), len(after.split())
        tot_before += wb
        tot_after += wa

        checks = []
        chain = load_chain()
        comp, problems = chain_declaration(i, after, chain)
        if comp is None:
            for pr in problems:
                print('   FAIL %s' % pr)
                fails.append('%s:chain' % name)
            continue
        for pr in problems:
            print('   FAIL %s' % pr)
            fails.append('%s:chain' % name)
        checks.append(('轮次链（每段可指到轮次）', not problems,
                       '%d 段：%s' % (len(comp['rounds']), ' → '.join(comp['rounds'][:3]) + ' …')
                       if not problems else '见上'))
        nb, na = nums(before), nums(after)
        decl = {'loss': dict(comp['num_loss']), 'gain': dict(comp['num_gain'])}
        loss = collections.Counter(nb - na)
        gain = collections.Counter(na - nb)
        exp_loss = collections.Counter(decl['loss'])
        exp_gain = collections.Counter(decl['gain'])
        ok = (loss == exp_loss) and (gain == exp_gain)
        checks.append(('数字令牌（含已声明的评审修正）', ok,
                       '一致（%d 种）' % len(nb) if ok and not loss else
                       ('已声明：−%s +%s' % (dict(loss), dict(gain)) if ok else
                        '未声明变动！−%s +%s（声明为 −%s +%s）'
                        % (dict(loss), dict(gain), dict(exp_loss), dict(exp_gain)))))
        cb, ca = cites(before), cites(after)
        # r51: this used to demand an identical citation multiset.  The guard's purpose is that
        # compression must not *lose* a citation (a claim left without its source) — and r51
        # legitimately ADDS citations, because the panel asked for a selection-bias related-work
        # paragraph and four verified references went with it.  So: nothing may be lost; growth
        # is reported rather than forbidden.
        lost_c, new_c = cb - ca, ca - cb
        checks.append(('引用 [n]（丢失为 FAIL，新增只报告）', not lost_c,
                       '一致（%d 处）' % sum(cb.values()) if not lost_c and not new_c
                       else ('无丢失；新增 %s（%d 处）' % (dict(new_c), sum(new_c.values()))
                             if not lost_c
                             else '丢失 %s / 新增 %s' % (dict(lost_c), dict(new_c)))))
        hb, ha = heads(before), heads(after)
        # The strict "same headings" check is superseded by the declared-diff heading check
        # further down: batch A legitimately renamed four headings (removing the ⭐ markers and
        # making §8.4 descriptive), which changes the strings but not the structure. Keeping the
        # old check would force us to choose between honest typography and a green audit.
        # Cross-references: a compressor that invents a § reference creates a wrong
        # pointer (this happened once: a §2.1 that should have been §5.1 Tier 2), and one
        # that drops a § reference loses navigability. Neither is detectable by a numbers
        # check, so it is checked explicitly.
        xb = collections.Counter(re.findall(r'§\s?\d+(?:\.\d+)?', before))
        xa = collections.Counter(re.findall(r'§\s?\d+(?:\.\d+)?', after))
        declx = {'new': dict(comp['xref_new']), 'lost': dict(comp['xref_lost'])}
        new_x = collections.Counter(xa - xb)
        lost_x = collections.Counter(xb - xa)
        ok = (new_x == collections.Counter(declx['new'])
              and lost_x == collections.Counter(declx['lost']))
        checks.append(('§ 交叉引用（含已声明的修正）', ok,
                       '无新增' if ok and not new_x else
                       ('已声明 新增%s 丢失%s' % (dict(new_x), dict(lost_x)) if ok else
                        '未声明变动！新增%s 丢失%s（声明 新增%s 丢失%s）'
                        % (dict(new_x), dict(lost_x), declx['new'], declx['lost']))))

        hb2 = collections.Counter(heads(before))
        ha2 = collections.Counter(heads(after))
        declh = {'new': comp['head_new'], 'lost': comp['head_lost']}
        ok = (ha2 - hb2 == collections.Counter(declh['new'])
              and hb2 - ha2 == collections.Counter(declh['lost']))
        checks.append(('标题（含已声明的改名）', ok,
                       '%d 条' % len(hb2) if ok and not declh['new'] else
                       ('已声明改名 %d 条' % len(declh['new']) if ok else '未声明的标题变动！')))
        pb, pa = pointers(before), pointers(after)
        exp_p = sorted(comp['ptr_new']), sorted(comp['ptr_lost'])
        got_new = [x for x in pa if x not in pb]
        got_lost = [x for x in pb if x not in pa]
        ok = sorted(got_new) == exp_p[0] and sorted(got_lost) == exp_p[1]
        checks.append(('指针行（含已声明的增删）', ok,
                       '%d 条在场' % len(pa) if ok and not got_new and not got_lost else
                       ('已声明 +%d −%d' % (len(got_new), len(got_lost)) if ok
                        else '未声明变动！+%s −%s' % (got_new[:2], got_lost[:2]))))
        drop = 100.0 * (wb - wa) / wb if wb else 0
        # Informational, not a pass/fail: the compression itself succeeded, and the blind-review
        # fixes legitimately ADD words (scope labels, the n-split, the multiplicity position, the
        # §8.3 estimand). The page budget is measured directly instead
        # (work/measure_pages_final_20260917.py), which is the quantity that actually matters.
        checks.append(('词数（参考；评审修正会加词）', True,
                       '%d → %d（%+.1f%%）' % (wb, wa, -drop)))
        if i == 4:
            rb = len([l for l in before.split('\n') if l.strip().startswith('|')])
            ra = len([l for l in after.split('\n') if l.strip().startswith('|')])
            exp_rows = rb + comp['rows_delta']
            checks.append(('表行数（缺陷表 + 清单，含已声明增删）', ra == exp_rows,
                           '%d → %d' % (rb, ra) if ra == exp_rows
                           else '%d → %d（链声明 %d）' % (rb, ra, exp_rows)))
            checks.append(('References 条目 = 44',
                           len(re.findall(r'(?m)^\[\d+\] ', after)) == 44,
                           str(len(re.findall(r'(?m)^\[\d+\] ', after)))))
        for label, ok, detail in checks:
            print('   %-24s %-4s %s' % (label, 'ok' if ok else 'FAIL', detail))
            if not ok:
                fails.append('%s:%s' % (name, label))

    # ---- the substance check, on the assembled manuscript
    print('\n--- 必须存活的声明与披露（在拼装后的正文上检查）')
    if not os.path.exists(COMBINED):
        print('   FAIL 找不到 %s' % COMBINED)
        fails.append('combined:missing')
    else:
        doc = io.open(COMBINED, encoding='utf-8').read()
        for label, pat in REQUIRED:
            ok = bool(re.search(pat, doc, re.I))
            print('   %-4s %s' % ('ok' if ok else 'FAIL', label))
            if not ok:
                fails.append('claim:%s' % label)

    print()
    print('=' * 76)
    print('总词数 %d → %d（−%d，−%.1f%%）' % (tot_before, tot_after, tot_before - tot_after,
                                              100.0 * (tot_before - tot_after) / tot_before))
    print('失败 %d 项' % len(fails))
    print('ALL PASS' if not fails else 'FAILED: ' + '; '.join(fails))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
