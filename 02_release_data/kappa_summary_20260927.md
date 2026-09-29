# Second-coding agreement summary — the 19 × 4 counting-unit marking table (2026-09-27)

**What this is.** A second coding pass re-coded all 19 rows × 4 units (`release` /
`protocol` / `yolo_dist` / `reported`) of the §S1 marking table under the published coding
rules, after first separating the rules from the printed conclusions into a standalone
manual (`coding_manual_19x4_20260927.md`). This file reports the agreement between the
second pass's marks (`second_coding_20260927.csv`) and the printed coding, with every
statistic recomputed mechanically from those two sources by `kappa_second_coding_20260927.py`
(full machine output: `kappa_computed_20260927.txt`). The printed coding in §S1 is **not
modified** by any of this; disagreements are recorded here, not edited into the table.

**Blinding status.** The pass is **non-blind**: §S1 and the upstream generator print the
rules and the printed marks together, so the second coder worked with the printed coding
visible. The agreement statistics below are a consistency check against a visible target,
not a blind inter-rater statistic. **The second pass is model-assisted, not a second human
rater**; it does not replace the single-rater disclosure printed with the table, and it
does not make the marking double-rated.

## 1. Agreement statistics

Decision scale = the printed counting distinctions: non-independent
(`alias`, `no_test`, `no_val`, `no_split`, `test_gated`, `contradictory`, `no_yaml`,
`train_val_alias`), clean (`independent_test`, `clean`), `no_test_key` (decidable
distribution-layer finding the printed yolo_dist count does not count as aliasing),
`unknown`, `n_a`. Cohen's κ; 95 % interval from the large-sample normal approximation,
upper bound clipped at 1.0.

| Unit | κ (conv. A: unknown as a category) | κ (conv. B: unknown cells dropped) |
|---|---|---|
| release | **0.716** (95 % CI 0.422–1.000) | 0.716 (n = 19; no unknowns) |
| protocol | **1.000** (all 19 cells agree; interval degenerate) | 1.000 (n = 19) |
| yolo_dist | **0.929** (95 % CI 0.792–1.000) | 1.000 (n = 15) |
| reported | **0.784** (95 % CI 0.501–1.000) | 1.000 (n = 15) |
| **Overall (76 judgments)** | **0.874** (95 % CI 0.778–0.971) | **0.922** (95 % CI 0.835–1.000; n = 68) |

Convention B drops the (row, unit) cells where **either** coding says `unknown` — 8 cells,
in rows 8, 9, 11, 12, 15, 16, 19. Exact-mark agreement (literal marks, the stricter
descriptive view): release 16/19, protocol 18/19, yolo_dist 17/19, reported 17/19 —
**68/76 (89.5 %)**; κ on the literal marks: 0.794 / 0.934 / 0.861 / 0.784, overall 0.879
(95 % CI 0.800–0.958).

Reading: overall agreement is high and the protocol layer agrees cell-for-cell, but the
intervals at n = 19 are wide, and two units (release 0.716, reported 0.784) sit in the
"substantial" rather than "almost perfect" band — the disagreement is concentrated exactly
where the manual is under-specified (below).

## 2. Disagreement list (8 of 76 cells at mark level)

1. **Row 1 COCO · release** — printed `n_a(A)`; second pass `independent_test`.
   Ground: the official release ships the test-dev partition with public annotations, so
   the unit definition yields a decidable mark. Class: **manual unclear** — no published
   material states when `n_a` applies at the release unit, so the printed mark is not
   derivable from the rules; the disagreement is definitional, not evidential.
2. **Row 2 PASCAL VOC · release** — printed `n_a(A)`; second pass `independent_test`.
   Same class and ground (test2007 partition shipped with labels).
3. **Row 18 CrowdHuman · release** — printed `test_gated(A)`; second pass
   `independent_test`. Class: **true disagreement**. The audit documents the same
   structure here as in row 17 (test images provided, ground truth withheld), which the
   printed table itself marks `independent_test` at release; under any fixed rule one of
   the two rows must move. The second pass assigns ground-truth withholding to the
   protocol unit, per the units' own division of labor.
4. **Row 18 CrowdHuman · protocol** — printed `alias(A)`; second pass `test_gated`.
   Class: **true disagreement**. The audit states verbatim that test annotations are never
   released and evaluation is server-only, which is the protocol unit's gating condition;
   the printed `alias` imports the authors' val-evaluation practice, which the reported
   unit already carries (and which row 17, same structure, is printed as `test_gated`).
   Both marks collapse to non-independent, so this cell does not move any printed count.
5. **Row 9 UAVDT · yolo_dist** — printed `unknown(A)`; second pass `no_test_key`.
   Class: **true disagreement**. The audit's §1 column-4 verdict for the row is explicit
   ("F-B … empty `test:`"), so "the audit takes no position" — the meaning of `unknown` —
   does not hold; §4's "unverified beyond these two" caveat limits generality but does not
   retract the verdict. The manual had to fix this precedence (§1 verdict over §4 caveat).
6. **Row 11 DIOR · reported** — printed `unknown(?)`; second pass `alias`. Class: **true
   disagreement**. The audit's §3b header ("`val` is the reported split because no `test`
   data exists") and its 14/19 roll-up both explicitly enumerate DIOR, so the audit does
   take a position; the row-level caveats (no primary per-split counts; HBB/OBB naming
   ambiguity) are real but the manual had to fix which statement wins. **Count-bearing**:
   this cell alone moves the printed reported-layer count (12/19 → 13/19).
7. **Row 16 Mendeley face-mask · reported** — printed `unknown(?)`; second pass `alias`.
   Class: **true disagreement**, same structure as row 11: the family is enumerated in
   §3b and in the 14/19 roll-up; the "treat it as a hypothesis" caveat concerns the
   benchmark's identity, and the audit still counts the row. **Count-bearing** (with row
   11: 12/19 → 14/19).
8. **Row 16 Mendeley face-mask · yolo_dist** — printed `alias(D)`; second pass
   `train_val_alias`. Class: **true disagreement at mark level** (both marks collapse to
   non-independent; no count moves). The verified generator writes `train == val` — the
   F-C shape, for which the mark vocabulary reserves `train_val_alias`; the printed
   `alias` follows the audit's own "F-A generated (`train == val`)" label, which conflates
   F-A (val == test) with F-C (train/val overlap).

## 3. Ambiguity register — where the published rules had to be supplemented

These are the points a **human** second rater would also have to resolve before any mark
could be mechanical; listing them is itself a reliability result:

1. **`n_a` has no stated applicability rule** at the release unit (rows 1–2 are the only
   uses). The manual fixes: the second pass does not emit it; the unit definition is
   applied literally.
2. **Ground-truth withholding is not assigned to a unit.** The release definition says
   "provide … test", the protocol definition adds "self-evaluated locally"; the manual
   fixes: partition at release, evaluability at protocol. The printed table itself is
   split on this (row 17 vs row 18 at release), which is what forces disagreement 3.
3. **Precedence is unstated twice**: §1 verdict vs §4 generality caveat (disagreement 5),
   and §3 enumerations vs row-level caveats (disagreements 6–7). The manual fixes both;
   the printed coding resolved the second the other way, and the audit's own text supports
   both resolutions.
4. **Version anchoring for multi-version rows is unstated** (e.g. a row whose v1 has no
   test and whose v2 adds a challenge-gated test): the manual fixes "code the audit's
   operative position for the row"; a latest-release anchoring would move one row's
   release/protocol marks (it does not appear in the disagreement list only because the
   audit's operative position is unambiguous there).
5. **The mark vocabulary is defined nowhere in §S1** — the marks' meanings live in the
   generator's header and the audit's failure-mode definitions. One printed mark
   (disagreement 8) follows the audit's own F-A/F-C conflation rather than the vocabulary.

## 4. What the disagreements imply for the printed counts (reliability bounds)

The printed coding is unchanged; the following bounds state how much the counts depend on
the two resolutions the second pass disputes:

- **Reported layer.** Printed: 12/19 = 63 % non-independent, 12/15 = 80 % of decidable
  rows, 4 unknown. Under the second pass's reading of rows 11 and 16 (the audit's own §3b
  enumeration): 14/19 = 74 %, 14/17 = 82 %, 2 unknown. Either way the qualitative
  conclusion (a majority of these benchmarks report a split that is not independent of
  checkpoint selection) is stable; the honest quoted form is the range **12–14 of 19
  (63–74 %)**, decidable rows **80–82 %**, until a human second rater adjudicates the two
  rows.
- **Release layer.** Printed 10/19 (52.6 %) vs second pass 9/19 (47.4 %); the difference
  is one row (18) plus the two `n_a` cells whose rule is unstated. The same
  majority-reading holds under both.
- **Protocol and yolo_dist layers** are unaffected: protocol agrees cell-for-cell;
  yolo_dist's one disagreement is an unknown-vs-decided cell whose decided value the
  printed count does not count as aliasing anyway.

Suggested wording where the article or supplement quotes the reported-layer counts:
*"12–14 of 19 benchmarks (63–74 %; 80–82 % of the decidable rows), where the range spans
the printed coding's two undecidable rows and the second coding's reading of the audit's
own enumeration; the printed coding is the conservative end."*

## 5. Provenance of this file

- Second coding: `second_coding_20260927.csv` (per-cell marks and per-row grounds).
- Rules: `coding_manual_19x4_20260927.md` (non-blind; interpretive rules listed in its §5).
- Statistics: `kappa_second_coding_20260927.py` → `kappa_computed_20260927.txt` (reads the
  printed table from the published supplementary and the CSV; nothing hand-copied).
- Evidence base: the archived configuration audit the `(A)`/`(D)`/`(?)` provenance refers
  to; the second pass codes what that document supports, not outside knowledge.
