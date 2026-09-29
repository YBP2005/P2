# Coding manual for the 19 × 4 counting-unit marking table (second coding pass, 2026-09-27)

**Purpose.** This manual states the rules under which a second coding pass re-coded the
19-row × 4-unit marking table printed in Supplementary §S1 (`release` / `protocol` /
`yolo_dist` / `reported`). It contains **rules only** — no per-row coding conclusions, and
no copy of the printed marks. The second pass's own per-cell marks are archived separately
(`second_coding_20260927.csv`), and the agreement statistics against the printed coding are
recomputed mechanically by `kappa_second_coding_20260927.py`.

**Blinding status (stated up front, because it bounds what the agreement numbers mean).**
The pass is **non-blind**. §S1 prints the coding rules and the printed coding in one place,
and the upstream generator carries both as well, so the second coder could not avoid seeing
the printed marks. The manual separates rules from printed conclusions, but no blinding was
possible, and the agreement statistics must be read as a consistency check, not as a blind
inter-rater statistic.

## 1. Sources the second coder works from

1. **Unit definitions** — as published in §S1 ("The three units", quoting the four rows
   release / protocol / yolo_dist / reported) and in the header of
   `recompute_split_units_20260916.py`.
2. **Mark vocabulary** — the twelve marks the printed table instantiates:
   `independent_test`, `clean`, `alias`, `no_test`, `no_val`, `no_split`, `test_gated`,
   `contradictory`, `no_yaml`, `train_val_alias`, `n_a`, `unknown`. §S1 itself does not
   define them; their meanings are fixed here from the audit's own failure-mode definitions
   (F-A `val == test`, F-B no usable `test:`, F-C `train`/`val` overlap) and from the
   generator's collapse set (`ALIAS_EQUIV`), which §S1's printed counts disclose.
3. **Evidence base** — the configuration audit document as archived
   (`benchmark_split_audit.md`): this is what the `(A)` explicit / `(D)` derived / `(?)`
   no-position provenance system refers to. **The pass codes what that document supports,
   not the coder's outside knowledge of the benchmarks**: where the audit is silent, the
   honest mark is `unknown`, not an inference from unpublished sources.
4. **Published corrections** — the two rulings §S1 states as already applied: (h-1)
   (D-Fire/FireSmoke family judged on D-Fire's own release, not on a SHWD-lineage config)
   and (d-1) (`trainval` is a user-protocol caveat, never grounds for a verdict; AI-TOD is
   `contradictory` because its v2 release statements contradict each other). Where a
   correction supersedes audit text, the correction governs.

## 2. Decision rules per unit

### 2.1 release — "the benchmark's own release layer: whether the official split
artifacts/scripts provide an independent held-out test"

Operational rule: look at what the official release **ships** (split folders, split files,
split scripts), and mark the structural finding:

- `independent_test` — the release ships a held-out test partition distinct from
  train/val. The *evaluability* of that test (ground truth released or withheld) is **not
  weighed here**; the unit split assigns it to `protocol` (below).
- `alias` — the release's own split artifacts bind `val` and `test` together (e.g. a
  shipped `test` list contained in the shipped `val` list).
- `no_val` — the release ships train + test but no val partition.
- `no_test` — the release ships no test partition at all.
- `no_split` — the release ships no split structure.
- `no_yaml` — the release ships split folders but **no machine-readable split
  configuration** (the artifact-level finding); the structural absence of a val is then
  `protocol`'s finding. (Interpretive rule fixed by this manual: for folder-only releases,
  the release mark records the missing configuration, because "artifacts/scripts" is the
  release unit's own object.)
- `contradictory` — the release's own statements about what is released contradict each
  other.
- `n_a` — **no applicability rule is derivable from the published materials.** §S1 and the
  generator nowhere state when the release layer is "not applicable". The second coder
  therefore does not emit `n_a`; where the printed table uses it, the second pass records
  the mark the unit definition yields. This is registered as a manual gap, not resolved by
  invention.

### 2.2 protocol — "the split declared by the official source, and whether that test can
be self-evaluated locally"

Operational rule, applied to the audit's explicit statements:

- `independent_test` — the official source declares a held-out test distinct from
  train/val, and nothing in the evidence base gates it (no statement that ground truth is
  withheld or evaluation is server-only).
- `test_gated` — the evidence base **explicitly** documents that the declared test cannot
  be self-evaluated locally (ground truth withheld / server-only evaluation). A vague or
  oblique indication is not enough; the pass requires an explicit gating statement. Where
  the evidence base affirmatively describes the split structure but is silent on
  evaluability, the mark is `independent_test`, not `unknown` (the silence rule; stated
  here because the published definitions do not fix it).
- `no_test` — the declared protocol provides no locally evaluable test (no test split, or
  a test that exists only inside a challenge/evaluation server with no local evaluation
  path).
- `no_val` — the declared protocol is train/test only.
- `no_split` — no split is declared at all.
- `contradictory` — the official statements about the test's availability contradict each
  other.
- The authors' own *evaluation practice* (which split their published numbers come from)
  belongs to the `reported` unit, not to `protocol`; `protocol` records what is declared
  and whether that declared test is locally evaluable.

### 2.3 yolo_dist — "the generic YOLO distribution-package layer (the audit's §1 column 4)"

Operational rule: take the audit's column-4 verdict for the row and map it onto the mark
vocabulary:

- F-A (`val:` and `test:` the same path) → `alias`; a generator/config that writes
  `train == val` (F-C shape) → `train_val_alias` (the vocabulary reserves `alias` for
  val/test binding; the audit's own labelling of one generator case as "F-A generated" is a
  known conflation, and the mark definitions govern).
- F-B (no usable `test:` key in the distribution config) → `no_test_key`.
- Distinct train/val/test in the distribution config → `clean`.
- No distribution config found by the audit (and the audit explicitly does not claim
  absence) → `unknown`.

Precedence rule fixed by this manual: where the audit's §1 row states a verdict and its §4
records a residual caveat about generality ("unverified beyond these N mirrors"), the §1
verdict governs the mark; the caveat does not convert a stated verdict into `unknown`,
because `unknown` means "the audit takes no position".

### 2.4 reported — "which split the numbers reported in the literature come from, and
whether they are independent of checkpoint selection"

Operational rule, in order:

1. Apply the definition to **explicit audit statements about reporting practice** (which
   split the literature reports; whether it coincides with the selection split).
2. Where the audit's only position is its §3 **enumeration** (the failure-mode lists and
   the roll-up), the enumeration governs: a row listed in a non-independent group is
   `alias`; a row in the clean group is `clean`.
3. `unknown` only where the audit takes **no position anywhere** — including after the
   published corrections are applied (a correction can retract an enumeration's basis, as
   (h-1) does for one family row).
4. The reported layer keeps the printed vocabulary: `clean` / `alias` / `unknown`.

## 3. Cross-cutting rules

- **Multi-version rows** are coded at the audit's operative position for the row (the
  version whose facts the audit's verdicts rest on), with the version question registered
  as an open ambiguity, since the published rules do not state an anchoring convention.
- **`unknown` is a legal mark.** It is emitted whenever the evidence base takes no
  position; guessing is prohibited (a κ computed on guessed marks measures the guess, not
  the manual).
- **Counts the printed table publishes** map marks to decisions as follows:
  non-independent = {`alias`, `no_test`, `no_val`, `no_split`, `test_gated`,
  `contradictory`, `no_yaml`, `train_val_alias`}; clean = {`independent_test`, `clean`};
  `no_test_key` is a decidable distribution-layer finding that the printed yolo_dist count
  deliberately does not count as aliasing; `unknown` is excluded from "decidable rows";
  `n_a` stays in the denominator but in neither count.

## 4. Agreement analysis plan (fixed before comparing)

- **Decision scale** (the printed counting distinctions, one common scale over all four
  units): {non-independent, clean, no_test_key, unknown, n_a}.
- **Primary statistics**: Cohen's κ per unit and overall over all 76 judgments, each with a
  95 % interval from the large-sample normal approximation
  (SE = sqrt(p₀(1−p₀)) / ((1−pₑ)·√n)), the upper bound clipped at 1.0; where all cells
  agree the interval is degenerate and is reported as such.
- **Two conventions for `unknown`**, both reported: (A) unknown as a category of the
  confusion matrix; (B) cells where **either** coding says `unknown` are dropped.
  `n_a` is kept as a category under both conventions.
- **Secondary statistics**: exact-mark agreement (literal marks), and κ on the literal
  marks per unit, as a stricter descriptive complement.
- All statistics are recomputed by `kappa_second_coding_20260927.py`, which reads the
  printed table from the published supplementary file and the second pass's marks from
  `second_coding_20260927.csv`; no statistic is hand-copied into the results files without
  that recomputation.

## 5. Known limits of this manual

The published materials underdetermine four things; each is fixed here by an explicit
interpretive rule so the coding is reproducible, and each is also reported as an ambiguity
finding in the results summary: (i) the applicability conditions of `n_a` (no rule
derivable — the pass does not emit it); (ii) the treatment of ground-truth withholding at
the release unit (assigned to protocol, per the units' division of labor); (iii) precedence
between a §1 verdict and a §4 generality caveat, and between the §3 enumerations and
row-level caveats; (iv) version anchoring for multi-version rows. A human second rater
working from §S1 alone would have to fix the same four points before any mark could be
mechanical; listing them is part of the reliability result, not a defect of one pass.
