# Configuration-level split aliasing in object-detection benchmarks: what the reported split is selected on, and how much of the selection survives an independent split


**Working title (v0.1). Target venue: Pattern Recognition (Elsevier).**

> **Provenance of this file.** The English submission form of the P2 manuscript, a faithful
> translation of the Chinese governing draft `评测有效性稿_正文_v0.1.md`
> (md5 `fe880ca0e3af77983382065db75255f3`, the state it was translated from, 2026-09-18; that draft is a live
> document, re-hashed whenever it changes — see `work/verify_text_hashes_20260917.py`); every number is unchanged and backed by the
> local artifacts listed in the Supplementary Material. Where the drafts disagree, the Chinese governs.
> Citation numbers refer to the References section of this manuscript, which is **ordered by first appearance**
> in the text (re-ordered once, on 2026-10-04, so that the numbering and the printed order agree). Every entry was verified against Crossref or DataCite DOI records
> or against the cited project's own page before it was added.
> The four citations unresolved in the first draft — [A] the CVPR 2026 geospatial leakage
> audit, [B] AI-TOD, [C] UAVDT, [D] D-Fire — are **now verified** as **[1] [2] [3] [4]**; two of
> the four titles and one venue had differed in an unverified citation.

---

## Abstract

Object-detection papers report a number from a split they call held out. We audit that premise, in three results.

**1. The convention is broken in our own corpora.** **6 of 14** corpora give the reported number no independent held-out split: the checkpoint was selected there, **even though** training and evaluation do not overlap. What is broken is **checkpoint selection**, not contamination — which turns an ethical question into a **measurement** one.

**2. The selection premium only partly survives.** The premium is positive in every escalated cell; the **paired Δgap** (arms' `val`-vs-`test` difference) changes sign by corpus, not the selection term — and **only gaps above the ≈0.5 pp A/A floor count** (**S23**). The **mean direction is metric-robust; one cell's significance and sign unanimity are not** (`smoke2sf`, p = 0.54). A **descriptive** 13-cell scan leaves **3** cells after BH, so the direction claim rests on the four escalated cells. **On a disjoint split, realization is partial**: the **claim-level interval includes zero**; arm-cell and run-weighted estimates are **descriptive** intervals only (Table 4). **At full budget, one corpus, one detector: 99 % — not robust to endpoint noise (§S30).** No power analysis was registered; nine `n` = 3 cells stay descriptive.

**3. The printed count rests on one rater.** The layer the literature reports prints **12 of 19** — **and its instrument reproduces only about a third of its own marks, a band of ±3–4 cells (S27)**; re-verifying every row and re-coding blind with **five** models recovers **19 of 30** corrected cells (§S12).
---

**Keywords:** evaluation validity; dataset splits; checkpoint selection; object detection; benchmark audit;
reproducibility

---

## 1. Introduction

A detection paper reports mAP50-95 on a split it calls held out, implying a number that estimates
performance on unseen data. The inference needs a premise the paper rarely states: the checkpoint was not
chosen on that same split. Binding `val:` and `test:` to one directory breaks it silently — the pipeline evaluates
there, keeps the best-scoring checkpoint and reports its score: a **maximum**, not a sample. Surveys of the detection literature [1] trace how that number became the
field's unit of comparison; this paper audits the reporting convention producing it.

That premise is audited in three places, in increasing distance from our own work: **our own corpora**,
where we count how many of our corpora alias the two keys (19 YAML files, counting by file); **19 public
benchmarks**, audited row by row for which split the reported number comes from; and **20 published
third-party training logs**, where we measure the premium directly, in data we did not produce.

Three further things we have not seen done here. We **measure the premium's fate** under a protocol separating
the selection set from the reported set (`best` and `last` checkpoints and both splits exist, so the
full 2 × 2 grid is computable): how much of the `val`-selected premium is realized on an independent
split — the measurement this paper contributes and §3.1 formalises. The protocol is the companion's and
is **cited, not restated**. And we **pre-register** a generalization hypothesis,
then report that it misses its criterion — a registration **also reported in the companion**.

### 1.1 Why the unit matters

Ask "how many of these benchmarks have a split problem?" and, unless a unit is declared, every answer is
defensible and they disagree by a factor of six: 2/19 (**structural**: one path bound to both keys),
10/19 (**`release` unit**: no independent held-out test), 13/19 (**`protocol` unit**: local independent testing gated), **12–14 of the 19** (**`reported` unit** — **12** the single rater's printed coding, **14** that rater's rows after a **non-blind recoding** moved two; **five blind coders agree at κ 0.824** and, once the record is re-verified first-hand, independently reach **19 of the 30** corrected cells, eleven unanimously (**S12**); the reported number's split is non-independent). The readings above are all defensible, and §6.1's four counting units (`release`, `protocol`, `yolo_dist`, `reported`) are the **columns** they come from — including `yolo_dist`, omitted above, at **4/19**. Declaring the unit is
therefore a methodological premise, not a caveat (§3, §6).

### 1.2 What we do not claim

We do not claim that aliasing is data contamination: the image-level intersection between the
training and held-out evaluation images is **zero** (SHWD [5] excepted, where `train` and `val` are one
directory). We do not claim a single bias direction: our paired analysis finds **two where it overstates, one where it understates above the design’s own measured floor, and one *at* that floor (Supplementary S23)**, and **nine cells are not testable at n = 3** (§5.1, §7.1; the escalation ledger is **Table S38b**, which records which cells moved to n = 10). Nor do we claim the
convention is framework-general (§6.5) or that the audited benchmarks are wrong: they report what their
configuration computes.

**Positioning (one sentence).** We claim neither to be first to audit split problems in detection benchmarks
nor to audit image-level leakage: both are taken. We occupy a different cell — **configuration-level
aliasing, a direction that varies by corpus, and the requirement that a count declare its unit.** Every number points to a local artifact; every claim narrowed after external checking is
recorded as narrowed (§5.4).

**Scope.** All quantitative claims about selection behaviour come from **YOLO-lineage pipelines**, the only
family among the six frameworks we checked (five pinned repositories plus the Ultralytics release) selecting the checkpoint by the validation metric by default
(§6.5) — stated at the claim, not only in a limitations section. **The registered multi-target replication is reported in the companion paper, and its first report, criterion and verdict stay there** (§9): this paper cites it for readability and **claims none of its results**.

---

## 2. Contributions and related work

**Where this paper sits.** Reporting practice has itself been audited: leakage and near-duplicate
contamination [3], [4], [6]; split naming and the choice of standard splits [7], [8]; experiment-
reporting standards [9]; checkpoint-selection criteria [10]; and budget-dependent rankings [2]. Each audits
**data, reporting, or selection**; **none audits a release’s configuration binding** — the object of §3–§6.

### 2.1 The closest work, and where this paper sits (detailed)

> The detailed comparison — the nine prior lines of work, what each measures, and the axis on which
> this paper differs — is **§S45 in the Supplementary material**; it is not printed here because
> the journal counts text inside the 20–35 page limit and the comparison is background, not a claim.
> **§2.2 (Contributions) and §2.3 (what we do not claim) are unaffected.**

### 2.2 Contributions

**What this paper reports first** (the boundary to the companion is in §2.3): the configuration-level audit
of the `val`/`test` convention and its selection premium (§4–5); and the **measured** realization of that
premium on a disjoint split with the reporting conventions it depends on (§8.6–8.7, §11, §3.1).

1. **We quantify the magnitude and direction of configuration-level aliasing.** The selection premium
   (best − last) is **positive in all four cells, the baseline arm gaining more** — **on an escalated four-cell base, not a sample** (**near-definitional; §5.1**; four paired 95 % CIs
   excluding zero, §5.1 Tier 1) — **consistent with the selection-bias literature** [11], not new in
   kind. **All four cells meet the stated-n criterion (n = 10–11)** and all four survive a Benjamini–Hochberg step over **these four** at q = 0.05 — **a data-selected set; the 13-cell BH is the multiplicity control (§5.2)** — the fourth, `dota15`, entered at n = 3
   and was escalated to n = 10 under a criterion fixed in advance (**Table S28's note**) — so the convention
   systematically shifts **arm-to-arm comparisons**; its direction
   varies by corpus: three-way paired differencing gives 2 cells where `val` understates, 2 where it
   overstates and 9 not testable at n = 3 — the **no-systematic-direction** [12] reports, measured here on
   detection corpora.
   **We do not claim a general understatement** (§5). It appears in third-party logs too (a searched 20-log sample; §5.5) — corroboration that the
component exists elsewhere, **not independent evidence** and not a field-level rate.
   *Note: **image-level** leakage magnitude is quantified by the two 2026 studies;
   **configuration-level** aliasing magnitude has not been measured before.*
2. **We measure how far the selection premium transfers.** The measurement is the contribution; its
   protocol is the companion's and is **cited, not restated** here (§8.1). On the
   five arm-cells measured here the `val`-selected premium is realized on the disjoint split at
   **23.3 %** with all five arm-cells at n = 10 — **a point estimate whose claim-level interval
   includes zero** ([−17.3 %, 53.2 %], P = 0.118; the six-cell pool's interval is [−4.9 %, +21.3 %]),
   and it is **not a constant**: the rate falls with the
   validation noise of the criterion used to select (§8.6–§8.7). The identity tying it to the
   winner's-curse share we **adopt** [13], not claim; the closest concurrent work [12, 15] reaches the same **direction** with a different quantity, and neither reports a **ratio of difference premiums** — `(T_best − T_final)/(V_max − V_final)`, on disjoint splits, in detection, on our own arm-cells, with measured `val` noise as moderator. A same-estimand ratio does exist elsewhere — in genomics, where it is written as a relative bias and measured at 10–60 % (**Supplementary S12** carries the full citation). The replicate axis is **data order** (§8.4) — the **seed-budget discipline
   reproduced inside this setting** rather than a new one.
3. **We disclose our own defects and the corrections** rather than removing them:
   our analysis' first version had non-reproducible items — pod-dependent scripts, a citation to a file
   not holding the quoted numbers, no written endpoint convention. §10, not deleted.

### 2.3 What we explicitly do **not** claim (shared tooling)

The companion and this paper share project-internal process protocols — a multi-model review checklist and a local/cloud scripting discipline — and neither claims originality for them: **Supplementary S6**, *Shared process protocols*.

---

## 3. Units: the methodological premise

"Have a split problem" is a property of a **(benchmark, counting unit)** pair, not of a benchmark. **[14] varies the definition on one file; we vary who controls the split and measure a different quantity: the share of `val`-selected premium that survives a disjoint split.** We use four units, defined by **who controls the split**:

- **`release`** — the split the benchmark's **own published release** ships: the `train:` / `val:` /
  `test:` entries and paths in the distributed archive. *Example*: an archive whose `data.yaml` binds
  `val:` and `test:` to the **same directory** records "yes" here (§4).
- **`protocol`** — the split the benchmark's **official protocol** tells you to use, which need not be
  the released one: a protocol may carve its own validation set out of the released training split.
  *Example*: an aliasing release whose documented protocol still requires a held-out test split records
  "no" here and "yes" above — the units answer different questions.
- **`yolo_dist`** — the split a **generic YOLO distribution package's** own configuration resolves to,
  i.e. what a practitioner taking the pipeline off the shelf gets. *Example*: a clean release whose
  community YAML points `val:` and `test:` at one directory records "yes" **only** here.
- **`reported`** — the split the number **the literature prints** came from (not the official leaderboard's
  own score), read from the release documentation and the dataset's own paper. *Example*: two papers on one benchmark can
  differ here while agreeing under all three units above — hence the headline count uses this unit (§6.1).

**A count is meaningless without its unit**: the same nineteen benchmarks answer differently under each
(Fig. 1).

**The proposition is not ours to claim.** That *the same data yield different defensible audit counts under different operational
definitions* is stated independently for molecular benchmark auditing, in a 2026 preprint whose abstract closes "different
defensible definitions return different answers from the same file" [14]. **The observation is the cited literature's; its
instantiation in detection evaluation, and the four named units, are ours** — the units named by *who controls the split*, the
19-row evidence table, and the premium on **five arm-cells**. It is orthogonal to [15], which separates leakage by **type**; the **single citation convention is `reported = 10–11 of the 16–17 decidable rows` (≈ **63–65 %**), i.e. **10–11 of 19 ≈ 53–58 %** of all nineteen**, with the printed-layer numbers (12–14/19) and the upper bound (≤14/19) scoped to their own columns**; we
separate the **counting subject**, so one type can still be counted under four units (§6.1).

> **Table S2** → Supplementary §S8.

**The `reported` unit is read from the release documentation and from the dataset's own paper**: we did not sample papers per benchmark, so no prevalence claim is made (§11). For each of 19 benchmarks we record all four units, an evidence class and a confidence level, and recompute every percentage from the row markers under a per-unit subtotal check **and one stated `n_a` rule** (**Supplementary S12**) — the full 19 × 4
table and the cross-check against the original audit are **Supplementary S1**, the derived counts §6.1 and its
table.

**The rule itself is not new.** The same toolchain's own course states it normatively — *"Test set is
touched once, at the end. Not for tuning."* and *"The splits must be independent on the dimension that
matters at deployment."* [16] — so what this paper adds is not the rule but the **audit and the count**
under it.

**The premise we rely on throughout:** a "yes" under any unit means *the reported number is not a sample from an independent split*. **What that does and does not license is stated where the counts are printed** (§6.1 and the note under its table).

### 3.1 Formalisation: what the four quantities are, and what they can and cannot identify

**Setup.** Training is a randomised map from (seed ω, recipe θ, checkpoint e) to weights, and evaluation a fixed functional on a labelled split; write V(e) and T(e) for a checkpoint’s `val` and `test` readings and ê for the `val` argmax. Sections 5–9 measure four quantities: the selection premium, Δgap, κ, the realization rate (**both sides at one checkpoint rule — Supplementary S11, S18**).

**Definition — the raw gap is not identifiable from the pair alone.** G = V(ê) − T(ê) = δ + o mixes a split-difficulty term with a selection-optimism term; the decomposition, **and the reading that a single-model endpoint pair is unable to separate its two terms, are [17]'s**, while its **strong form** — that *any* δ′ fits the observation equally well — is **stated here as a formalisation rather than attributed to that literature**. **The pairing assumption is what makes Δgap meaningful**, failing by construction under aliasing so that §9 cannot be read as a clean-protocol result; the identity holds value by value on all 13 scanned cells and both escalated cells at n = 10 (§5.6).

**Adopted identity, not a claim of this paper.** With V(e) = v(e) + ε_e and T(e) = v(e) + τ + η_e, **E[premium_test] = E[premium_val] − WC**, WC := E[ε_ê − ε_e_f] ≥ 0 — the argmax is over a **candidate set fixed in advance** and `e_f` is a **pre-specified member of it** (what the budget-fixed `last` gives) — so the realization rate is **1 − WC / E[premium_val] ≤ 1**, with equality only if selection is driven by signal alone [13] (**Supplementary S11** states which part of that the archive can and cannot settle) — the optimizer's curse in this paper's notation, the frame for §8.6–§8.7. **Two consequences are testable on the archive** — the per-run inequality, and monotonicity in the `val` noise (**Supplementary S11**). A third form, that the premium scales as σ√(2 ln E), was **tested and withdrawn** (**Supplementary S11**); contemporaneous work measures **≈5×** on the same σ√(2 ln K) bound [18].

**Corollary (the premium is mostly shape, and the peak is the worst place to stand).** `premium_r = shape(E) + ν_r` holds **exactly**, `shape(E)` being the mean curve's peak-to-final gap, so `shape` is a functional of the mean curve alone — **not** an independent check on σ — and `E[ν_r] ≥ 0`. On our 40-run four-budget series **the monotone criterion is met on the clean re-run** while the σ√(2 ln E) form is **outside** its pre-declared band, so that scaling **stays withdrawn**; the pre-declared shape control passes on the mean it specifies but fails per arm, and we report both readings — the with-early-stopping series carrying the pre-declared verdict — so **we do not claim an `E` effect**. The checkpoint rule is a **reporting rule** (the top-5 mean beats the argmax on the same 40 runs), with **three limits**: an empirical capture rate, a `val`-side cost the argmax does not carry, and a two-split, five-epoch-grid scope.

**What is ours, and what is not.** Of the statements that follow, the raw gap's definition [17], the impossibility result for endpoint-pair estimators [19] and the family-dependence procedure [20] are **machinery rather than results of ours**, and the identity is **adopted** from the selection-bias literature; **the corollary alone carries measurements of this paper**. Full statements and proofs are in **Supplementary S11**, and the detail displaced from here in **Supplementary S12**.

### 3.2 Six experiments, five judged criteria, on GPU machines, each with its criterion written down first

The propositions of §S11 are testable, so we ran them on rented GPUs with the **criterion fixed before the runs**; **Supplementary Table S37** gives, for each of the six experiments, the criterion it was judged against. Counts below are over **experiments**, not criteria.

**The two negative outcomes and the redone design are stated as such in Supplementary Table S37** (G1 is void; **two of the five judged experiments are negative — G1′ and G2**; the values behind every verdict are in **S31–S33**, the G1 family in **S12**; the reading below is stated more weakly in **Supplementary S11, section 13.3**).

**We then ran the clean test** of G3’s epoch-budget series with early stopping disabled, all four budgets present (**Supplementary S34b**); its relationship to the primary reading is stated above.

On the shared 5-epoch grid the `val` and `test` peaks agree in only **17.5 %** of runs, and conditioning on that single observable splits the 40 runs: where they agree the **median Δgap is lower** (mean **+0.13 pp**, median **−0.20 pp**, n = 7; **post-hoc**), where they differ it is **systematically not** (mean **+0.91 pp**, n = 33; permutation p = **0.009**, **post-hoc**; the median reading is **p = 0.0011**). **This is a partial predictor, not an explanation of the sign**; its limits — including the four of seven agreement runs whose gap is non-positive — and the per-run table and test are in **Supplementary S11**.

---

## 4. Finding 1: our own corpora

### 4.1 How common the aliasing is

In **our own packaged configurations** — the YAMLs we train from, a different object from a benchmark's own release — **6 of 14** give the reported number no independent held-out split: **AI-TOD, DOTA v1, DOTA v1.5 [21], Mendeley face-mask [22], SFCHD [23]** (five binding `val:` to `test:`) and **SHWD [5]** (which binds `train` to `val`; **S1** row 13). Of the remaining 8, **4** keep the keys genuinely distinct and **4** have no `test:` key at all — the three groups account for all 14, and this is **a count over the configurations we hold, not a prevalence, nor the benchmarks' own releases** (audited separately, §6.1). Counting by file, **19 YAML files** alias the two keys, in five locations; on the archived manifest subset the ratio is **8 of 28**. **These three bases answer three different questions** — configurations (6 of 14), the files inside them (19), the archived manifest's rows (8 of 28) — **not three estimates of one rate.**

**For the corpora whose `val` and `test` are the same directory this is not contamination**: their image-level intersection with training is **exactly zero**, so the aliasing changes not *what* was evaluated but *which checkpoint* was reported, turning "selection contamination" from an ethical question into a **measurement** question. **SHWD is the exception and is not folded into that statement**: with `train` and `val` on one directory, its training and evaluation images are the same files. **It still counts among the six, for the reason the list is about: its `val` is not an independent held-out split either.**

### 4.2 The failure is produced by a tool, not by carelessness

A PASCAL VOC [24]→YOLO conversion script wrote two keys from one `images_dir`, so `train == val` appears **because the generator could not produce distinct values** (§6.1 records the same for Mendeley face-mask [22]). §10's first recommendation: make "are `val` and `test` the same source?" a **pipeline-level hard check** — human YAML review will not catch it. 

---

## 5. Finding 2: the selection premium — magnitude, direction, and mechanism

**Evidence.** `eval_validity/selection_premium_local_20260916.txt`, reading **569 archived runs** from the local archive (the local version is the 2026-09-16 repair).

**Definition.** premium = **best-epoch − final-epoch** mAP50-95 **within a single run**. When `val == test`, "best" was selected on the reported split, while `last` and `last5` are endpoints **no selection rule can reach**. This is the checkpoint-selection term of the run-to-run variation studied in [25] (early stopping, data order) and [26] (benchmark variance across seeds). Being a maximum over a noisy curve, it also carries the upward bias of any selected extreme [13]: what those works average over as uncertainty, we measure as a reproducible component. **The two arms.** Every cell is a paired comparison in which the **baseline** arm follows the published convention and the **strategy** arm is the intervention under test — in the cells reported here, raising the peak learning rate from **0.001 to 0.005** with everything else held fixed (batch 32, imgsz 640, SGD; YOLOv12n with the shape-aware IoU). The two arms run the same code and the same data.

> **Table S3** → Supplementary §S8.

### 5.1 Direction: reported in two tiers, and the second tier's sign varies by corpus

The direction claim **must be reported in two tiers**: "the convention understates the effect" is
wrong, and external checking refuted it (§5.4, II). **Endpoint convention (frozen):** `best − last`
**within a single run**, both endpoints reported for every cell; §7.2–§7.3 quantify the other
convention.

**Tier 1: on the monitored split this positivity is near-definitional** (`best` is that curve's own argmax), so **the finding we report is the paired arm difference and its test side (§8.6)**: the selection premium is positive in all four cells, the baseline arm gaining more — consistent with the selection-bias literature, not new in kind. Pairing brings **no** variance benefit:
the paired t of 5.74 and the unpaired Welch t [27] of **5.68** agree — at ρ = 0, **standard arithmetic
rather than an empirical finding of ours** [26]. **Permutation checks** agree with the t-tests at each cell’s attainable floor (**Supplementary S12**).

**Meta-analyses of published results have long quantified this optimism**: development-set early stopping
is measured to *overestimate realistic model performance*, by as much as **18.0 %** accuracy [28]; and a
large Kaggle meta-analysis finds *little evidence of substantial overfitting* [29] — complementary rather
than contrary, since its mechanism is holdout **reuse** and ours needs none.

**Metric sensitivity.** On `metrics/mAP50(B)` the mean direction holds in all four cells, but
`smoke2sf` loses both its significance (**+0.063 pp**, p = 0.54) and its sign unanimity (**6+/5−**, not
11+/0−): **the mean direction is metric-robust, one cell's significance and sign unanimity are not**
(full mAP50 columns and both mAP75 columns — the mAP75 `val` side is a **5-epoch grid**, so a rate computed from it is **upward-biased** — **Supplementary S12**).

**Table 1.** Tier 1 — each arm's **peak−final gap** and the **paired difference** between arms, by cell; the gap is a within-run maximum (§5.1), so the finding is the paired difference. `n` counts paired units (**eleven**: ten `--shuffle-seed` runs plus one unseeded — Supplementary S12); at n = 10 the two headline cells read **+0.544** (`shwd2sf`) and **+0.397** (`smoke2sf`), both 10+/0−, and both differences hold at n = 10 (Supplementary S12). **A different run set from the transfer measurement in §8.6** — the two tables’ premiums are **different quantities, not two readings of one** (which run set each uses: **Supplementary S12**). Source: `verify_two_critiques_20260916.txt`; the `dota15` row's n = 10 escalation is in Table S28.

| Cell | n (paired units) | peak−final gap, base | peak−final gap, strat | **paired diff** | sd | t | p | perm. *p* (floor 2/2ⁿ) | 95 % CI |
|---|---|---|---|---|---|---|---|---|---|
| smoke2sf (strong) | 11 | +0.799 | +0.382 | **+0.416** | 0.240 | 5.74 | 1.9×10⁻⁴ | 0.00098 | [+0.255, +0.578] |
| shwd2sf (corroborating) | 11 | +1.038 | +0.512 | **+0.526** | 0.207 | 8.41 | 7.6×10⁻⁶ | 0.00098 | [+0.386, +0.665] |
| a2d15 (directional probe) | 10 | +0.534 | +0.262 | **+0.272** | 0.183 | 4.69 | 1.1×10⁻³ | 0.00391 | [+0.141, +0.403] |
| dota15 (within-domain) | 10 | +0.941 | +0.492 | **+0.449** | 0.196 | 7.23 | 4.9×10⁻⁵ | 0.00195 | [+0.309, +0.589] |

**Table 2.** Tier 2 — the paired difference Δgap by corpus. **Resolution limit (pre-registered A/A control):** two identically configured arms differing *only* in training file order give a spurious **Δgap ≈ 0.5 pp** (CI [+0.09, +0.84], **S23**), so equal split difficulty is an **assumption with a measured floor** and **gaps that small are not read as identified effects**. Δgap > 0 means `val` understates the strategy arm’s effect. **Δgap is the split-gap arm difference**, not the selection effect: it decomposes into a difficulty gap and a selection term, and **Δgap’s sign is not the selection term’s sign** (**Fig. S1**). the selection contribution is the **selection-action contrast** `Δprem_val − Δprem_test`. **`Reading` names Δgap’s sign, not the selection term’s** (`smoke2sf`: Δgap **+0.461**, selection **−0.580**). Sources: `xeval_analysis_20260916.txt` (the two `val`-understating cells) and `x1_tier*` / `teval.csv` (the two `val`-overstating cells).

| Corpus | n | Δgap (pp) | p | 95 % CI | Reading (**Δgap's sign**) |
|---|---|---|---|---|---|
| shwd2sf | 10 | **+0.779** | 0.0053 | [+0.297, +1.261] | `val` **understates** — **above the A/A floor** |
| smoke2sf | 10 | **+0.461** | 0.0263 | [+0.068, +0.855] | **at the A/A floor** (S23) — **not read as an identified effect** |
| p_aitovis | 10 | **−1.226** | 1.3×10⁻⁸ | [−1.370, −1.081] | `val` **overstates** |
| p_vistod15 | 10 | **−3.315** | 6.5×10⁻⁹ | [−3.676, −2.953] | `val` **overstates** |

> **The split of Δgap is recorded for two of the four cells**: difficulty **+0.759** / selection **+0.020** (`shwd2sf`), and difficulty **+1.041** / selection **−0.580** (`smoke2sf`) — in the second the selection term is **opposite in sign to Δgap**, so the sign does not carry it, and **both intervals include zero** (**Supplementary S9**, Fig. S1). The two `p_` cells' `prem_test` was **not recorded at that time**: their per-epoch `test` curves were evaluated on 2026-09-30, so nothing is imputed and the values are now recorded (**Supplementary S12**, Table S38).
>
> **The four rows below are an escalated base, not a sample**: the two `p_` cells reached n = 10 because their n = 3 Δgap had been flagged, so the 2/2 balance is a property of the escalation rule; the other nine cells are **descriptive** (**Supplementary S12**). This cell is also the one where **3 runs** changed training path silently under GPU memory pressure, and why we do not call it clean is in **§10, defect 10**.

*(Third §5 table, S5 → Supplementary §S8.)*

**Tier 2: on the same three-way corpora the paired difference Δgap varies in sign.** The raw
`M_val(ê) − M_test(ê)` is **not identifiable**; the paired difference removes the difficulty term **under the equal-difficulty assumption** (Table 2) —
**Δgap > 0 ⇒ `val` understates**. **Its effective base is four cells, not thirteen, and the floor is measured on one corpus pair — it is a reference point for that pair, not a universal threshold**, and an **escalated base** rather than a random sample, for the reason **Table 2's note** gives; **“2 understate / 2 overstate” is therefore a statement about these four cells, not a rate for the family**. **No prospective power analysis was registered**; the scan is in **Supplementary S12**. **Against the +0.47 pp floor** (§S23): `shwd2sf` **+0.779** is above it, `smoke2sf` **+0.461** is on it, and the two overstating cells (**−1.23**, **−3.32**) are an order of magnitude beyond it. **On the same rule the reading is one cell above the floor, one at it and two far below it** — so the direction claim rests on **one** understating cell that clears the floor, not two. **Scope of that floor:** §S23 measures the floor on the **selection term** `G = prem_val − prem_test`; Table 2’s `Δgap` adds the difficulty term, so applying the floor to `Δgap` is a **conservative analogy, not a strict null**.

**Both escalations met the criteria fixed in advance.** `dota15` **+0.449 pp** (**10+/0−**);
`p_aitovis` **−1.226 pp** and `p_vistod15` **−3.315 pp** (**0+/10−**), permutation p = **0.001953**,
the attainable floor at n = 10. (resolution limit: **Supplementary S23**; see **Table 2**’s caption.) **The `p_vistod15` runs flagged for memory pressure were re-run clean and reproduce to ≤0.15 pp, changing no reading (Supplementary S41).** The `best.pt` endpoint was identified, not assumed: on `test` it reproduces the archived `sio_b_results.csv` to **0.0046 pp**.

**The formal claim:** the convention systematically shifts **arm-to-arm comparisons** (Tier 1: four
cells, CIs excluding zero); **the direction of that shift varies by corpus** (Tier 2: **1 above the floor / 1 at it / 2 overstating**, Supplementary S23) — **neither "a general understatement" nor "no systematic direction"**.
BH at q = 0.05 **now leaves three cells significant** — `p_vistod15`, `p_aitovis`, `shwd2sf` [30], **reversing what we reported before the
escalation**. **The two families are not the same test**: the **13-cell scan is descriptive**, the **confirmatory family is the four escalated cells** (declared before their runs, §3.2) — the direction statement rests on those four.

**Scope (cross-framework boundary).** The convention this paper audits belongs to the **YOLO lineage —
Ultralytics YOLO [16] and YOLOX [31]**: at pinned commits, Detectron2 (`TEST.EVAL_PERIOD = 0`) [32],
MMDetection [33], DETR [34] and PaddleDetection [35] **report the final epoch instead** (§6.5) — that
pipeline family's convention, **not the field's**.

### 5.2 Two versions must be disclosed side by side

**Two archives, two versions of this table.** The main text uses the **local archive** (569 runs, n = 11); the pod root (347 runs, n = 10) is a **Supplementary S12** cross-check agreeing in sign and magnitude, not in value.

### 5.3 The dota15 cell: now reproducible, and one wording defect exposed
**This cell was not reproducible from the release as first written, and the repair exposed a wording defect** (both disclosed, §10 row 2). The repair, the value-by-value agreement and the defect are recorded in **Supplementary S12**.
### 5.4 Two external critiques, checked (one refuted, one judged non-identifiable)
**Supplementary S12** carries the two external critiques in full. **We used to write** that the gap was simply unidentifiable; the
external check **corrects this to** the paired-difference form, which cancels the difficulty term
under the pairing assumption stated in **§S11**. The argument and the recomputation are in
**Supplementary S12**.

### 5.5 The same component in third-party public logs
**The same quantity appears in other people's logs** — **a convenience sample with no sampling frame, not a field-level rate**: 20 logs from 6 sources found by repository **search**, median **+1.04 pp**, max **+5.65 pp**. **The sign is not the informative part**: the premium is a within-run maximum minus that run's own final epoch, so it is **non-negative by construction**, and the sample's content is its **magnitude**. The queries, the rest of the frame and the reason public logs **cannot establish aliasing** are in **Supplementary S12**.
**Five limitations**: ① the two cells escalated in §5.1 reach n = 10 with **local** runs and test-side
evaluations, and the remaining 9 cells' `test` side was closed on 2026-09-30 on one machine;
② `prem_test` is **best − last**, while the per-epoch `test` curve now exists for **all thirteen**
corpora (**Supplementary S12**, Table S38); ③ `last.pt`'s val recomputation differs from the final `results.csv`
row by ~0.02 pp; ④ this section does **not** touch §6's 19-benchmark census; ⑤ the aggregate is a **ratio of small means** — `prem_val` spans **+0.605 to +1.469 pp** across the five arm-cells (Table S20) — so a change of a few hundredths of a point in the numerator moves the rate by tens of points.

### 5.6 Why Δgap's sign varies by corpus: three of five candidate mechanisms are refuted by the data
**Three of five candidate mechanisms are refuted, and the mechanism itself is not identifiable** — the sign of Δgap is a sum of same-order terms, so no single mechanism can be read off it (§S11, Remark 3) — **but the paired quantity is, and is what we report.** The examination, the per-cell components and the exact identity are in **Supplementary S12** and Table S8–S10.

## 6. Finding 3: how general this is across public benchmarks

**Evidence**: `benchmark_split_audit.md`, a line-by-line audit of 19 benchmark rows, plus
`split_units_19rows_20260916.md` (recomputation script; no hard-coded percentages).

**The nineteen audited benchmarks**, each read from its own release or dataset paper: COCO [36], PASCAL VOC [24],
Objects365 [37], Open Images v7 [38], DOTA v1.0 and v2.0 [21], VisDrone-DET [39], AI-TOD [40], UAVDT [41], xView [42],
DIOR [43], NWPU VHR-10 [44], SHWD [5], SFCHD [23], MAFA [45], Mendeley face-mask [22], WIDER FACE [46], CrowdHuman [47]
and D-Fire [48] (**per-unit markings**: Supplementary S1) — **the configurations this archive could
read, not a sample of the field.** The question is **evaluation validity**: dataset-level bias auditing [49]
and classifier-accuracy estimation [50] ask whether a reported number measures what it is taken to
measure, but neither audits a release's configuration binding.

### 6.1 The result under four units (single-rater judgements)

![Fig. 1](figures/fig3_four_units.png)

**Fig. 1.** The four counting units on the same nineteen benchmarks — the **printed single-rater** counts (10/19 `release`, 13/19 `protocol`, 4/19 `yolo_dist`, 12/19 `reported`); the re-verified tallies are Table 3's second column.

**Table 3.** The four counting units, with denominators named (§3). **Co-headline (2026-10-10):** the same four units were re-coded blind by **five current-generation coders** (κ **0.824**; **Supplementary S12**), and re-verifying every row first-hand changed **30 cells** — so the table prints **both tallies**: the frozen single-rater counts, and beside them the same four units **re-tallied from the marking table after the 2026-10-09 first-party correction record**, under the **same per-column rule** (the value-to-count mapping is in **Supplementary S12**). Source: `split_units_19rows_20260916.md`. **Rows marked `n_a` enter the denominator, not the numerator**; **alternative readings of the same rows** are **12/19** for `release`, **12/15** the 19 less the four **undecidable** (`n_a` is two rows), and **13/19** for `reported` under the COCO-`val` reading. **The `clean` row is a reading**: the audit counted **5/19**, a later pass moved **two**, so this table reads **3/19**. **The `reported` row's two denominators**: `12–14 of the 19`, and `12/15 = 80 %` over the fifteen neither `n_a` nor undecidable (**4 rows are evidence-insufficient**). **Both ranges span two readings, not intervals**, on a **single rater's** judgement. **Independent re-coding reproduces it only at 31.4 % (Round 7, coder agreement κ 0.836) and 42.2 % (Round 8, κ 0.811) of the printed marks** (Supplementary S12). A **model-assisted, non-blind second coding** is **reliability evidence, not a replacement** (**Supplementary S12**).

| Unit | non-independent: printed (single rater) | non-independent: after first-party re-verification | of decidable rows: printed → re-verified | undecidable: printed → re-verified |
|---|---|---|---|---|
| **release** (the benchmark's own release) | **10/19 ≈ 53 %** | **14/19** | 10/19 → **14/19** | — |
| **protocol** (the official protocol) | **13/19 ≈ 68 %** | **14/19** | 13/19 → **14/19** | — |
| **yolo_dist** (the generic YOLO distribution package) | **4/19 ≈ 21 %** | **2/19** | 4/15 ≈ 27 % → **2/17 ≈ 12 %** | 4 → **2 rows** |
| **reported** (the layer actually reported) | **12–14 of the 19 ≈ 63–74 %** | **10–11 of the 19** | 12/15 = 80 % → **10/16–11/17 ≈ 63–65 %** | 4 → **2–3 rows** |

> **With `test_gated` excluded** (the table’s rule): release-layer **9/19 ≈ 47.4 %** vs **14/19** with them in.

**Naming note.** The fourth unit is named **`documented / locally scorable`**: it reads the **release documentation and each dataset’s own paper**, not a sample of papers that report on the benchmark. The rename, and the reason a literature measurement is not claimed, are in **§S39**.

> **What a count here is, and what a "yes" means.** Every row is a **single rater's judgement**
> (§6.1), so the counts are printed as counts — the percentages beside them are a reading aid, not a
> rate estimated from independent coding. A "yes" under any
> unit means the reported number is **not a sample from an independent split**; it does **not** mean
> the benchmark is broken or the experiment dishonest, and it does not license a generalization claim.
> **Primary reading (panel).** The **five-coder blind panel** leads: **19 of 30 corrected cells (63.3 %)**, eleven unanimously, **κ 0.836**. The **single-rater count is the frozen instrument of record**.

> **Frozen instrument.** These 19 rows were coded by **one rater** — 28 literal judgements (**§10**, defect 5). The five blind coders **independently reach 19 of 30 (63.3 %)** corrected cells, eleven unanimously, while **26 of 76** cells stay **undecidable**; **an independent blind panel reproduces only 31.4 % of the printed marks (42.2 % on the finer scale), so a 19-row count of 10–11 carries a band of roughly ±3–4 cells** — the *direction* of the majority survives on the decidable rows (10–11 of 16–17), **its size does not** (**Supplementary S27**); a **non-blind, model-assisted** pass agrees at κ **0.874** and **moves two rows** (**Supplementary S12**). `reported` means **the number the literature prints**: it is printed as a range, **12–14 of the 19 ≈ 63–74 %**, with the **80 %** column the lower end over the **12/15** decidable rows, and `n_a` rows counted in the **19** but not the numerator (**Supplementary S12**).

### 6.2 "Same directory" has four levels, and the audit reported only the narrowest
The levels, the rows each admits and the resulting shift are in **Supplementary S12**, Table S12.
### 6.3 We do **not** reproduce the original audit's two numbers, and we say why
one rests on the narrowest reading of "same directory", the other on a stale snapshot; both recomputations are in **Supplementary S12**, Table S13.
### 6.4 One judgment the evidence does not support (corrected)

**One classification correction is recorded in Supplementary S12** (D-Fire moves to the clean group).

### 6.5 Across frameworks: is the convention specific to YOLO?
**Among the six pinned default configurations we checked, only the two YOLO-lineage frameworks select on the reported split by default — Ultralytics YOLO and YOLOX (`trainer.py` tracks and saves the best); Detectron2, MMDetection, PaddleDetection and DETR do not** (Table S14). At pinned commits Detectron2 (`TEST.EVAL_PERIOD = 0`), MMDetection, DETR and PaddleDetection **report the final epoch instead** (file-by-file evidence, 25 configuration files: **S12**, Table S14; **a targeted sample at pinned commits, not a census**, so "the convention" means that family's, not the field's). A **cross-lineage realization test** — a Faster
R-CNN (ResNet-50 FPN) detector, a family that **reports the final epoch by default** — on VisDrone under the
same three-way split, at **six seeds**, is **positive in all six runs, with a 95 % interval excluding zero** (**68.2 %** realized; **+0.0809 pp**, 95 % CI **[26.9 %, 123.5 %]**) — **a sign-only claim**: the size is **below the endpoint’s own noise** (image-level SE ≈ **0.18 pp**, **S24**), so the printed magnitudes are **not interpreted as an effect size**.: the mechanism is **not confined to the YOLO lineage in this instance**. A **second detector family** (RetinaNet) keeps the **direction** on the second corpus but **not on VisDrone** (there the disjoint-split gain exceeds the selection gain, **Table S34e**) (**Supplementary S34e**). A second corpus, same protocol, same direction: **6/6** and **12/12** runs on `val`, **5/6** and **11/12** on `test`. This is **one detector, one protocol, two corpora, one setting** — **not a generalisation beyond the YOLO lineage** (**Supplementary S34c**). Its **68.2 %** is a rate over **six runs** on this probe's own split and is **not comparable** with §8.6's realization rate: different protocol, different denominator.
## 7. Finding 4: what "significant" means, and how the endpoint convention changes it

### 7.1 With n = 3 a permutation test **cannot** reject in principle

**A power note for the cells that remain at n = 3.** Recovering each Tier-2 cell's sd from its own printed 95 % CI gives **0.20–0.67 pp**; at n = 3 the required effect is **0.65–2.19 pp** at α = 0.05, two-sided — **at or above every Tier-1 effect here** (+0.27 to +0.53 pp) — and 0.2–0.7 pp at n = 10. The nine cells at n = 3 are therefore **not testable at this design**, and are reported descriptively only. **A prefix-n table (n = 3…10) and the derivation with the non-central-`t` factor (**`3.26·sd`**) are in S12**; the permutation floor **2/2ⁿ** binds at n = 3, not the *t* test.

**For a sign-flip permutation test on n pairs the smallest attainable two-sided p is 2/2ⁿ**: at
n = 3 that is **0.25**, so such a cell has **no resolution at this n**; **after §5.1's escalations no
headline cell (Tables 1–2) is n = 3** (**the derivation and each n's floor: Supplementary S12**).

### 7.2 The two clean-protocol cells clear significance by n = 6–8
> **Which quantity these p-values belong to.** The p-values quoted here are for **Table 2’s Δgap** (the arm difference of the val-vs-test gaps). **Table S42’s column is a different estimand** — `Δprem(seed) = prem(strategy) − prem(baseline)` — so its p-values are **not** expected to match these, and the S42 note says so. Both are printed with their n so a reader can check either.
**The weaker endpoint reaches *t*-significance at n = 6 on `shwd2sf` (p = 0.0164) and n = 7 on `smoke2sf` (p = 0.0400)**; the **exact permutation — floored at 2/2ⁿ (0.25 at n = 3) — follows **one step behind on `shwd2sf` and none on `smoke2sf`** (n = 8 on both `selected` readings; Table S42 gives every prefix n, both endpoints). The clean-protocol seed extension that reaches n = 10, and the per-cell numbers, are in **Supplementary S12** and Table S15.
> **First-report attribution (a convention we hold to).** Three things here belong to the companion
> paper and are cited, not claimed: the two Δ values (**+1.434 / +0.507 pp**), the three-way remediation
> protocol itself, and the pre-registered multi-target replication (§9). What this paper reports first is
> **the selection premium (§5), the 2 × 2 realization of that premium on a disjoint split (§8.6–8.7), and
> the formalisation of the realization rate (§3.1)**. The full statement — including how the companion is
> named to the editor while it carries no identifier — is in **Supplementary S12**.

### 7.3 A cross-archive endpoint conflict on the same run (investigated — and itself a disclosure)
**One run is recorded with two different endpoints in two archives** — which checkpoint is recorded was never specified: **Supplementary S12**, Table S16. Taking the final-epoch entry (67.12) gives Δ = **−1.490**, p = **0.0141**. The best-epoch entry (70.06) reads Δ = **−0.902**, p = **0.2931**, **but had been computed with the run's `last` reading**; corrected **2026-10-02** it becomes Δ = **−1.490**, p = **0.0141**, as released. So under the **`best`** convention of §5 this cell is **significant**, and nothing printed here moves.

## 8. Finding 5: how far the selection premium transfers to an independent split

### 8.1 The protocol is the companion's; the measurement under it is this paper's

The three-way remediation protocol is **defined and reported in the companion paper** — which first
reports that **the effect reproduces in direction while its magnitude falls** — so this section **cites
it** rather than presenting the replication. **In this paper's own terms it is three
things**: a `val` carved from the pool so that training never sees it; the target corpus's own held-out
`test`, with a filename-level check that its images do not intersect training; and an endpoint **defined in
writing before any run**. Its **FROZEN-HASH** stamp is stated in **§9**; the registration **text** itself is the
companion's and is **author-side**, so this paper carries the stamp and the readings (**Tables S24–S27**), not the
document. What this paper measures
**under** that protocol is the quantity §3.1 formalises: **how much of the `val`-selected premium survives
on a split no selection rule can touch**, and that measurement is this paper's.

### 8.2 The protocol's results on the companion's corpora: **transferred**

The protocol's results on the companion's corpora are the companion's first report. What this paper adds under the protocol is the measurement of §8.6–§8.7; the transfer (2026-09-21) is recorded in the module-transfer note of that date.

### 8.3 A direct measurement of data-order replication (not seed variance, and not the selection claim itself)
**A direct measurement of data-order replication — reproduced inside this setting**: adding replicates that permute the training file order lowers the mean by **9 %–29 %**, each figure taken **against that cell's own n = 6 mean** and not against the pooled
headline effect, the **replicate-budget discipline** measured rather than assumed ([51]'s setting, §8.4). **What these replicates are.** The per-run randomness is a **deterministic permutation of the training file order** (`--shuffle-seed`, the number in the run's name), **not** the framework's `seed` argument (**Supplementary S12**, section 9.3, with the two corpora whose replays are identical across `--seed` values). The quantity is therefore **data-order replication**, not seed variance: the 9 %–29 % bounds the **file-order** component of the reported mean, **not** the variance between independent training seeds. That best-of-K selection inflates a reported score is **not new** (§8.6 positions the closest concurrent work, a dose–response over 2,047 datasets), so **what is measured here is the magnitude under a protocol that selects cells for significance first and expands seeds afterwards** (design and recomputation check: **Supplementary S12**, Table S18). **The title is deliberately the weaker, sample-scoped claim**: with three initializations the interval is wide, and extending to five does not narrow it (the gain SD reaches the data-order component's order), so the components are **consistent with, not established by**, these initializations.
### 8.4 The three variance components: **the excluded one is the smaller in this sample — a sample-scoped ordering, not an established one**
**The three variance components, and the excluded one is the smaller in this sample**: the single-run data-order component is **0.515 pp**, against an initialization component of the same order — the **same ranking** as the shuffle-order result of [51] (**Supplementary S12**), so we **reproduce the ordering inside this setting** rather than discover it. What was held fixed, and why this is **sample-scoped** — at five initializations the gain SD moves **0.146 → 0.439 pp** and its interval **overlaps** the data-order magnitude, so the two are of the same order rather than one clearly smaller — is in **Supplementary S12** and Table S19.
### 8.5 Why "same-pipeline pairing" is a necessity, not a habit
**Pairing is not neutrality**: the paired design covers the **budget and data** axes only, and **not** the optimiser’s (why, and the counterexample: **Supplementary S12**).
### 8.6 The premium’s realization rate — **the claim-level interval includes zero**

![Fig. 2](figures/fig2_realization_rate.png)

**Fig. 2.** The `val`-selected premium against what it realizes on the disjoint `test` split, per arm-cell; the title's aggregate is the plotted pool's — **§8.6** names the pool Table 4 uses.

**Scope of the rate (§S20).** The rate is the realization of the `val`-selected premium on a disjoint split **for these five arm-cells, under the companion's protocol** — the wording, the non-pooling of the two batches and the scale dependence (the difference form is reported but **not** co-primary — a pp difference is not scale-free here) are stated in **§S20**.

**How much of the gain selected on `val` survives on `test`?**

**Table 4.** The premium selected on `val` versus what that same selection action realizes on the disjoint `test` split, per arm-cell (**six rows are printed; the pooled rate uses the five arm-cells whose `test` side reached n ≥ 5** — `aitod20` contributes its baseline row only) (**an unbalanced pool** — two corpora contribute both arms, `aitod20` only its baseline — so the arm-cell is the unit). Source files for every column: **Supplementary S12** (this revision's two batches included). **The §10 memory-pressure bound (defect 10) does not arise here**: its hits are in §3.1's clean batch and §5.1's `p_vistod15`.

| Cell | Arm | n | `prem_val` | **`prem_test`** | **realization rate** |
|---|---|---|---|---|---|
| shwd2sf | baseline | 10 | +1.469 | **+0.736** | **50 %** |
| shwd2sf | strategy | 10 | +0.865 | **+0.152** | **18 %** |
| smoke2sf | baseline | 10 | +0.691 | **+0.509** | **74 %** |
| smoke2sf | strategy | 10 | +0.605 | **−0.157** | **−26 %** |
| aitod20 | baseline | **10** | **+0.766** | **−0.218** | **−28 %** |
| aitod20 **†** | **strategy** | **10** | **+1.111** | **−0.543** | **−49 %** |

where `prem_val = V_max − V_final` (**selecting on val**) and
`prem_test = T_best − T_final` (**realized on test**).

**Aggregate** (runs weighted equally, n = 50): `prem_val` **+0.879 pp** → `prem_test` **+0.205 pp**. **At the claim level this is not significant**: the **claim-level interval** is the cell-level, five-cluster one, **[−17. **Both clusterings are printed** (**S22**): arm-cell **[−10.6 %, +55.8 %]**, target-corpus **[−47.9 %, +34.2 %]** — **both cover zero**.3 %, 53.2 %]**, **P(rate ≤ 0) = 0.118**, zero inside. Descriptively, arm-cell median **17.6 %** and run-weighted **23.3 %** (span **2/5** negative: Table 4). On a difference scale the eleven clusters give **−1.367 pp**, 95 % CI **[−1.59, −1.15]** (five-cell denominators **+0.605 to +1.469 pp**).

The monotonicity is a correlation, not a causal claim, and at the arm-cell unit the nine-cluster reading is ρ = **−0.433** (p = 0.244) — see **Fig. 3** and **Supplementary S12**: the n = 80 are the 81 runs with a measured
`test` side less the one whose `prem_val` is 0. It has a named precedent: [52] gives validation
overfitting (VO) its name and bounds the expected best observed loss by
E[min L] ≥ ν* − s_m√(2 log(Nq)), an optimism growing with the number of selection queries Nq.

The 806-row evaluation is archived (`xeval_perepoch_20260918/`, with a SHA-256 list).

![Fig. 3](figures/fig6_sigma_vs_rate.png)

**Fig. 3.** Realization rate against the noise scale σ̂ of the run's own `val` curve, over **80 runs** in three terciles of **27 / 27 / 26** (nine-cluster Spearman ρ = **−0.433**, p = 0.244; the run-level reading is −0.466); dashed: rate = 1, dotted: §8.6's pooled reading.

### 8.7 The per-epoch view: the realization rate is not a constant

![Fig. 4](figures/fig5_epoch_curve.png)

**Fig. 4.** **Left**: mean `val` and `test` trajectories over the 10 **data-order replicates**, both headline cells (baseline solid, strategy dashed). **Right**: per-(seed, epoch) `val` movement against what transfers to `test` — the ratio is not taken (its denominator can vanish); the fit through the origin is **κ = 0.708** (R² **0.937**, run-clustered 95 % CI **[0.671, 0.745]**; the title's **0.734** is the earlier five-epoch grid).

> **Tables S21–S23** → Supplementary §S8.

**One metric self-correction first.** Our first version used `r(e) = ΔT(e)/ΔV(e)`, which is
**pathological** at late epochs — `V(e) ≈ V(final)`, so the ratio's **denominator vanishes**; we
report only the non-dividing `ΔV(e)` and `ΔT(e)` below.

**Slope κ** (how much of the movement on `val` transfers to `test`). On the **complete curve** —
**n = 765 (replicate, epoch) points over the 41 runs** — **κ = 0.708, R² 0.937**, with a run-clustered
(sandwich) 95 % CI **[0.671, 0.745]**; the within-run estimator gives **0.698**. **Two controls (Table S43)**: a per-run κ distribution, and a free-intercept fit whose **intercept is indistinct from zero** — so the through-origin constraint is **supported, not assumed**. Across the curve `ΔV` reaches
**−8.1 pp** and about **71 %** transfers: **early-training progress is real progress.** §8.6's realized
share measures the **selection-relevant sliver** near the peak, where `ΔV` is of order **±0.2 pp** — so
**"most of the movement on `val` transfers" and "the little extra gained by selecting near the peak does
not" are both true**, and the premium is the residual of the transfer rate. **And κ is not constant
across arms either — in the direction the selection account predicts**: **baseline κ = 0.600**
([0.581, 0.619]) against **strategy κ = 0.767** ([0.735, 0.800]), difference
**+0.168, 95 % CI [+0.130, +0.203]**.

**A second result, and a self-correction the curve forces**: the sign-of-Δgap claim we wrote from four
sampled epochs is **too strong for one of the two cells** (on the complete curve `smoke2sf` starts
negative) and is **narrowed here**; per-checkpoint values: **Supplementary S11**.

**The limitations of this section are in Supplementary S12.**

### 8.8 Scale dependence: at full training budget the premium is realized in full

**§8.6's rate is a 20 %-train reading and does not carry to the regular scale.** We retrained the corpus
that supplies §8.6's largest cell at **full budget**: VisDrone with **5,971** training images (the
6,471-image public train split less the 500-image `val` carve), YOLOv12n **[53]**, 100 epochs, §5.1's two-arm
`lr0` contrast (**0.001** vs **0.005**), and **ten training file orders per arm (20 runs)**. Under the
§8.6 definitions the pooled realisation rate is **+99.2 %** (95 % interval **[+80.4 %, +122.0 %]**,
run-level bootstrap, 20,000 resamples), against the **pre-registered interval [−28 %, +74 %]**. **Read on run-to-run variation alone the interval clears the band’s upper edge (+76.9 %, barely); once the measured image-level endpoint noise is propagated (√2 × 0.18 pp per endpoint) the same interval is [+31.6 %, +225.0 %] and its lower bound falls *inside* the band — so the out-of-band reading is **not robust to measurement noise** and we do not rest a claim on it (Supplementary S30).** **What this arm changes is a bundle**: against §8.6 it changes the **corpus, the carve size and the budget at once**, so **+99.2 % is not attributable to budget alone** — and §8.9’s second full-budget corpus lands **inside** the band (**+1.44 %**, CI covering zero), which is why we do **not** read this as a budget effect. `prem_val` averages **+0.269 pp** against **+0.879 pp**
for §8.6's 20 %-train pool, while `prem_test` averages **+0.266 pp** — the premium is roughly **four
times smaller**, yet now realised almost exactly. That is what §3.1's decomposition anticipates: the
unrealised part is the winner's-curse term `WC` — whose concurrent check is **[54]** — which is what a larger `val` split should reduce, and
it agrees with Fig. 3's rate-versus-σ̂ correlation — more training data, a smoother `val` curve,
a smaller `WC`.

**The rate is arm-dependent, and one arm stays inside the band.** The baseline arm realises **+66.4 %**
(n = 10: `prem_val` **+0.256 pp**, range **+0.105 to +0.410**; `prem_test` **+0.170 pp**) and **remains
inside the pre-registered interval**; the strategy arm realises **+129.0 %** (n = 10: **+0.282 pp**,
**+0.075 to +0.412**; `prem_test` **+0.363 pp**). No run in either arm has a negative `prem_val` or
`prem_test` (**0/20** each). **What this does not do** is revise §8.6, which measures five arm-cells
under the companion's 20 %-train protocol and already states that the general reading — "the convention
realises about a quarter of the `val` premium" — would be false; what it adds is **scale**. We therefore
**weaken, rather than strengthen**, the recommendation §11 draws from §8.6 (§11 ②, §13). Two scopes
bound it: **one corpus**, and §5.1's `lr0` axis; a second corpus with a genuine disjoint `test`
(`mask_clean`, 919 images) is **registered as the replication**.

> **Per-run matrix, protocol, leakage self-check and the bootstrap** → **Supplementary §S13** (Tables S46–S47: the per-arm table is S46).


### 8.9 A second corpus at full budget: the premium and its realization are corpus properties
**The same full-budget protocol on a second corpus** (`mask_clean`: 5,220 train / 900 val / 919 test, `nc = 1`; 2 arms × ten file orders, 100 epochs, `test` side from a per-checkpoint sweep):

| Arm | n | `prem_val` | `prem_test` | realization |
|---|---:|---:|---:|---:|
| `base100` | 10 | +26.219 | **+1.755** | **+7.2 %** |
| `lr005_100ep` | 10 | +14.883 | **−1.165** | **−9.7 %** |

Pooled **+1.44 %**; run-level bootstrap 95 % CI **[−7.2 %, +4.1 %]** — **zero inside**; `prem_test > 0` in **12 of 20** runs. **Against §8.8** (full-budget VisDrone: premium +0.27 pp, realization **99 %**), the premium here is two orders of magnitude larger and **only a minority survives** — and the arms separate on the *realization* (+7.2 % vs −9.7 %) rather than on the premium alone. **Per-run detail: Supplementary S17.**


## 9. The registered multi-target replication: **reported in the companion paper**

**First report, criterion and verdict stay with the companion paper; nothing here is a claim of this paper.** To read its registered table: ① it is a **three-way split** (train / selection / report); ② it ran under the protocol then in force, where the **`val` side aliases the `test` half** — the one fact §7 takes; ③ its criterion was frozen **before any run existed** (FROZEN-HASH `6a7eee7b3e34b15ce5adcba14cf7ea36`) and its verdict entered is **"criterion not met"**, deliberately **not** "hypothesis refuted" — the companion reads the outcome as **"direction replicates, size does not"**. Record: **Supplementary S24–S27** (source of truth: the companion's archive).

## 10. Our own defects (disclosed, not hidden)

| # | Defect | Handling |
|---|---|---|
| 1 | The clean-protocol results document **cites a ledger file that does not exist in the sense claimed**: neither `_r10_final_stats.txt` nor the "real log" `_r10_stats_0403.txt` holds **any** headline number. | **Handled by rebuilding the numbers from the per-run artifacts**; the ledger's role is now documentary only, and every headline number in the pack traces to a released file (**§S6**; verbatim detail in **§S14.6**). |
| 2 | ~~the dota15 cell of `selection_premium.py` was not reproducible~~ → **fixed** (stale root directory; the matcher assumed a seed suffix the run names do not carry). | **Recomputed**; it now reproduces M3’s printed value (**§S6**). |
| 3 | **`sio_b_results.csv` has no written endpoint convention**: `t2_mask2mende_base100_s42n` is recorded as final (67.12) in one archive and best (70.06) in another. | **Stated in §7.3**, with its consequence for the conflicting-endpoint cells. |
| 4 | The two headline scripts **originally depended on a rented pod** (`import paramiko` plus a plaintext password) — a paper about evaluation validity whose own analysis is not reproducible from the archive. | **Repaired**: the pod is gone from the released paths, and the analyses run from the archive (**§S6**). |
| 5 | **One script recomputes the σ decomposition** from the archived per-run values, each asserted against the printed number, for the runs it can read. | **Disclosed**; the script and its inputs are released, and what it cannot reconstruct is named in §S14.5. |
| 6 | The local archive **has no copy of 6 of the 7 corpora**, and of the three-way carve it holds **only the manifest** (`split_defs_20260916/`), not the other carve directories | **Partially repaired**; the manifest ships and the carve directories are named (§S6). |
| 7 | The audit document has **internal inconsistencies** (nine items, found by our own census) | **Each adjudicated**: 3 misreadings, 4 real defects, 1 convention risk, 1 classification (§S12). |
| 8 | Our own corpora contain `val == test` | **That is this paper's argument**, not an embarrassment to be hidden |
| 9 | **Our first per-epoch report claimed curve-wide stability from a four-point sample**; the complete curve overturned it for one of the two cells (§8.7) | **Corrected in place, with the retraction recorded** (§8.7). |
| 10 | **Memory pressure silently changes the training path**: under GPU memory pressure Ultralytics switches implementation **without changing the recorded configuration**. | **Disclosed, not retracted**; the affected cells were re-run clean (six pairs twice each, `|clean2 − clean1| = 0.000` throughout) and the four affected `p_vistod15` runs reproduce to ≤ 0.15 pp — **Supplementary S41**; the bound this buys is stated there, verbatim with this row. |

---

## 11. Recommendations

**Four checks before reporting, each with the artifact that discharges it.** ① Are `val` and `test`
the same source? Make it a **hard pipeline check** on every dataset YAML (§4.2); the output is the
resolved paths. ② If you must select on the reported split, say so and report a selection-free endpoint — **the `final`-epoch endpoint, the only selection-free one this archive measures** —
alongside — the step **enlarges** the arm difference (§5.1). **The cost of not doing so is
scale-dependent**: at 20 % train the selection action realises about a quarter of the `val` premium
on a disjoint split, but **at full budget the answer is corpus-specific**: **+99.2 % on VisDrone (§8.8)** vs **+1.44 %, interval covering zero, on the second full-budget corpus (§8.9)** — the cost is **not monotone in scarcity**, and the recommendation is **scoped to where it was measured** — the practice is **most
damaging exactly where data is scarcest**. ③④ **Test conventions and counting units** (the two concrete asks): stated in **Supplementary S29**.

⑤ **A plateau is a post-hoc candidate, not a rule we validate.** Weight averaging is established [55];
   what is *measured here* takes the **mean of the ranked top-5 `val` epochs' readings** (a reading average, not a weight average), capturing **70 %** of the
   realizable gain against the argmax's **30 %**, at the cost of **0.73 pp** below the peak — a post-hoc
   reading of our own 40 runs, untested as an intervention **and not general across corpora — extending
   the same test to eight further arm-cells reverses it (Supplementary S11, Measurement 3)**.

---

## 12. Limitations

- **Four disclosed uncertainties bound every claim**: the 19-row audit is **single-rater**; the log sample is a **convenience sample** with no sampling frame; the GPU memory-pressure evidence is **one machine**; and §8.8's full-budget reading is **one corpus, one detector, on the same `lr0` axis as §5.1** — it does **not** re-open §8.6's pool and **no interval of §8.6 folds into it**.
- The audit reads **split definitions only** (YAML, README, paper text), **no datasets**; under the `reported` unit **4 rows are evidence-insufficient**; and counts carry **no sampling interval, deliberately** (the grading is in the count itself, Table 3 column 2).
- **The full nine-item limitations list is in Supplementary §S16.**

---

## 13. Conclusions

A count is meaningless until its **unit** is named: the same nineteen benchmarks answer differently under each declared unit (Fig. 1, Table 3; **the `n_a` applicability rule itself is stated in Supplementary S12**), and re-tallying them after the 2026-10-09 first-party correction record moves the **layer** units up and the **package and report** units down (**Table 3**, Supplementary S12) — the **majority** conclusion is unchanged (the weakest recomputed **majority** is still **10/19**). Three findings stand. **The most robust number is the transfer slope κ (§8.7): early `val` movement does transfer to `test`, and the premium is its residual.** The premium is positive in all four cells, the baseline gaining more, and the paired Δgap **varies in sign** by corpus — so "the convention understates the effect" is not claimed. On five arm-cells at n = 10 **under a 20 %-train protocol** it is realized on a disjoint split at **23.3 %** (claim-level **[−17.3 %, 53.2 %]**, P(rate ≤ 0) = **0.118**); **at full training budget on the same corpus the pooled rate rises to +99.2 % (95 % interval [+80.4 %, +122.0 %] on run-level variation alone; **+31.6 % to +225.0 % once endpoint noise is propagated**, so the out-of-band reading is **not robust**, §S30), and the run-only interval clears the band’s upper edge only by 2.9 pp.** The registered second-corpus reproduction (§8.9) lands *inside* that band (+1.44 %, interval covering zero), so the out-of-band result is **not** reproduced and we do **not** read the loss as a small-sample artefact. Intervals quoted here are run-level and are not compared with the cell-level ones (§8.9, Table S47).** Two things do **not** hold: the σ√(2 ln E) scaling was tested and **withdrawn**, and no power analysis was registered, so the nine `n = 3` cells stay descriptive. What we ask of a detection paper is narrow: **name the counting unit, freeze in writing which checkpoint is reported, and state the interval at the claim's level.** First report is the companion's (§7.2).

## Declarations

- **Data availability.** The **seven corpora are open**; the pack lacks their **images**, so retraining is not recomputable (§10 defect 6). §5.5’s **third-party logs are not redistributed** (hashes and pointers only), as **5 of their 6 sources state no licence**. Released per-run artifacts and scripts: `02_release_data/`.
- **Recomputability boundary.** Every reported number is recomputable from the released per-run artifacts **without retraining**, each with its script. **Three are not, and they are named**: the carve directories (images not in the pack), the conflicting-endpoint archives (§7.3), and the `aitod20` completion to n = 10. **This revision adds ten files and five scripts** to `02_release_data/`.
- **Competing interests.** None declared.
- **One quantity, two spellings (§S25).** The n = 10 floor is exactly 2/2¹⁰.
- **CRediT.** All CRediT roles: **the authors**; the named statement goes in the submission system.
- **Generative AI.** Five language models served as **blinded panel annotators** (§5.5) and for the multi-model cross-check; their returns are **data**, with prompts and matrices released. **No manuscript text was AI-generated.**
- **Reproducibility.** Every reported number points to a local artifact (paths are relative to the released `02_release_data/`); **289 audit anchors** guard the claims, and the audit plus six checkers ship with the archive: **one runs unaided for a holder of the archive, four are author-side gates, and one is partly runnable** (270 of 289 anchors checkable from the released copy alone).

## References

[1] Z. Zou, K. Chen, Z. Shi, Y. Guo, J. Ye. "Object Detection in 20 Years: A Survey." *Proceedings of the IEEE* 111(3):257-276 (2023). DOI 10.1109/JPROC.2023.3238524
[2] R. Guedes de Souza, A.R. Panisson. "Who Thinks Best Depends on How Long You Let Them: Budget-Dependent Rankings in LLM Evaluation." arXiv:2608.12150 (2026).
[3] S. Kapoor, A. Narayanan. "Leakage and the reproducibility crisis in machine-learning-based science." *Patterns* 4(9):100804 (2023). DOI 10.1016/j.patter.2023.100804
[4] B. Barz, J. Denzler. "Do We Train on Test Data? Purging CIFAR of Near-Duplicates." *Journal of Imaging* 6(6):41 (2020).
[5] Xu et al. "Detection of safety helmet wearing based on improved SSD." *Journal of Physics: Conference Series* (2019). Dataset: https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset
[6] Y.K. Adimoolam, C. Poullis, M. Averkiou. "Data Leakage Detection and De-duplication in Large Scale Geospatial Image Datasets." *CVPR* 2026 (Oral). https://openaccess.thecvf.com/content/CVPR2026/html/Adimoolam_Data_Leakage_Detection_and_De-duplication_in_Large_Scale_Geospatial_Image_CVPR_2026_paper.html
[7] K. Gorman, S. Bedrick. "We Need to Talk about Standard Splits." *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics* (ACL):2786–2791 (2019). DOI 10.18653/v1/P19-1267
[8] R. Reveles-Martínez, S. Burciaga-Sosa, J.M. Celaya-Padilla, S. Castro-Tapia, H. Luna-García, H. Morales-Magallanes, M.N. Regalado-Pérez, C. Landeros-Soriano, et al.. "Sequence-Aware Dataset Auditing for Leakage-Free Benchmarking of YOLO Detectors for Bottle Detection." *Technologies* 14(9):531 (2026).
[9] J. Dodge, S. Gururangan, D. Card, R. Schwartz, N.A. Smith. "Show Your Work: Improved Reporting of Experimental Results." *Proceedings of EMNLP-IJCNLP 2019*, pp. 2185–2194. https://aclanthology.org/D19-1224/
[10] A. Apicella, F. Isgrò, A. Pollastro, R. Prevete. "Don't stop me now: How Validation Criteria Affect Checkpoint Selection and Early Stopping." arXiv:2602.22107v2 (2026).
[11] G.C. Cawley, N.L.C. Talbot. "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation." *Journal of Machine Learning Research* 11(70):2079–2107 (2010).
[12] W. Ruangsang, P. Pramkeaw. "Cross-Dataset Evaluation of YOLOv8 for Unmanned Aerial Vehicle Fire and Smoke Detection: Benchmark Contamination, Zero-Shot Transfer, and Onboard Deployment on a Low-Cost Airframe." *Drones* 10(8):635 (2026).
[13] Smith JE, Winkler RL. The optimizer's curse: skepticism and postdecision surprise in decision analysis. *Management Science* **52**(3):311–322, 2006. doi:10.1287/mnsc.1050.0451.
[14] M. R. R. Roktim. "When Is a Molecule a Duplicate? Identity Policy Determines What a Benchmark Audit Finds." *ChemRxiv* preprint (2026). DOI 10.26434/chemrxiv.15009099/v1
[15] S. Roth. "Which Leakage Types Matter? A Quantitative Landscape Across 2,047 Benchmark Datasets." arXiv:2604.04199 (2026).
[16] G. Jocher, A. Chaurasia, J. Qiu. *Ultralytics YOLO* (v8.4.120) [computer software] (2023; pinned release 2026). https://github.com/ultralytics/ultralytics (accessed 2026-09-12); the same project's official course states the split-independence rule normatively: Ultralytics Academy, "Splits that Tell the Truth," https://academy.ultralytics.com/courses/computer-vision-foundations/splits-that-tell-the-truth (accessed 2026-09-26). [verified: software release tagged v8.4.120 as used in this study]
[17] B. Recht, R. Roelofs, L. Schmidt, V. Shankar. "Do ImageNet Classifiers Generalize to ImageNet?" *Proceedings of the 36th International Conference on Machine Learning*, PMLR **97**:5389–5400 (2019).
[18] G. Zhang, K. Zhao. "Winning by Peeking: Unenforced Budgets and Test-Set Selection Inflate Short-Budget AutoML Comparisons." arXiv:2608.07303 (2026).
[19] Taylor J, Tibshirani RJ. Statistical learning and selective inference. *Proceedings of the National Academy of Sciences* **112**(25):7629–7634, 2015. doi:10.1073/pnas.1507583112.
[20] Benjamini Y, Yekutieli D. False discovery rate–adjusted multiple confidence intervals for selected parameters. *Journal of the American Statistical Association* **100**(469):71–81, 2005. doi:10.1198/016214504000001907.
[21] G.-S. Xia, X. Bai, J. Ding, et al. "DOTA: a large-scale dataset for object detection in aerial images." *CVPR* 2018, pp. 3974-3983. DOI 10.1109/CVPR.2018.00418.
[22] Kaggle data record, "Face mask detection" (CC0; 853 images, 3 classes, PASCAL-VOC XML): https://www.kaggle.com/datasets/andrewmvd/face-mask-detection . No DataCite or Mendeley Data record carries this title (sweep, 2026-10-09).
[23] Fusheng Yu, Jiang Li, Xiaoping Wang, Shaojin Wu, Junjie Zhang, Zhigang Zeng. "Large, Complex, and Realistic Safety Clothing and Helmet Detection: Dataset and Method." arXiv:2306.02098 (2023); journal version in *IEEE Transactions on Instrumentation and Measurement* (2024) (SFCHD / SFCHD-SCALE)
[24] M. Everingham, L. Van Gool, C.K.I. Williams, J. Winn, A. Zisserman. "The Pascal Visual Object Classes (VOC) Challenge." *International Journal of Computer Vision* 88(2):303-338 (2009).
[25] J. Dodge, G. Ilharco, R. Schwartz, A. Farhadi, H. Hajishirzi, N. Smith. "Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping." arXiv:2002.06305 (2020)
[26] X. Bouthillier, P. Delaunay, M. Bronzi, A. Trofimov, B. Nichyporuk, J. Szeto, N. Sepah, E. Raff, et al. "Accounting for Variance in Machine Learning Benchmarks." arXiv:2103.03098 (2021)
[27] B.L. Welch. "The Generalization of 'Student's' Problem when Several Different Population Variances are Involved." *Biometrika* 34(1/2):28 (1947).
[28] K. Kann, K. Cho, S.R. Bowman. "Towards Realistic Practices In Low-Resource Natural Language Processing: The Development Set." *Proceedings of EMNLP-IJCNLP 2019*; arXiv:1909.01522 (2019).
[29] R. Roelofs, V. Shankar, B. Recht, S. Fridovich-Keil, M. Hardt, J. Miller, L. Schmidt. "A Meta-Analysis of Overfitting in Machine Learning." *Advances in Neural Information Processing Systems* **32**:9179-9189 (2019).
[30] Y. Benjamini, Y. Hochberg. "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." *Journal of the Royal Statistical Society Series B: Statistical Methodology* 57(1):289-300 (1995).
[31] *YOLOX* [computer software]. https://github.com/Megvii-BaseDetection/YOLOX (pinned at commit `6ddff4824372`, branch `main`, accessed 2026-09-16).
[32] *Detectron2* [computer software]. https://github.com/facebookresearch/detectron2 (pinned at commit `a2f4a8771ab7`, branch `main`, accessed 2026-09-16).
[33] *MMDetection* [computer software]. https://github.com/open-mmlab/mmdetection (pinned at commit `cfd5d3a985b0`, branch `main`, accessed 2026-09-16).
[34] *DETR* [computer software]. https://github.com/facebookresearch/detr (pinned at commit `29901c51d7fe`, branch `main`, accessed 2026-09-16).
[35] *PaddleDetection* [computer software]. https://github.com/PaddlePaddle/PaddleDetection (pinned at commit `b25522a0f4bd`, branch `release/2.9`, accessed 2026-09-16).
[36] Tsung-Yi Lin, Michael Maire, Serge Belongie, Lubomir Bourdev, Ross Girshick, James Hays, Pietro Perona, Deva Ramanan, C. Lawrence Zitnick, Piotr Dollár. "Microsoft COCO: Common Objects in Context." arXiv:1405.0312 (2014)
[37] S. Shao, Z. Li, T. Zhang, C. Peng, G. Yu, X. Zhang, J. Li, J. Sun. "Objects365: A Large-Scale, High-Quality Dataset for Object Detection." *2019 IEEE/CVF International Conference on Computer Vision (ICCV)* 8429-8438 (2019).
[38] A. Kuznetsova, H. Rom, N. Alldrin, J. Uijlings, I. Krasin, J. Pont-Tuset, S. Kamali, S. Popov, et al.. "The Open Images Dataset V4." *International Journal of Computer Vision* 128(7):1956-1981 (2020).
[39] P. Zhu, L. Wen, D. Du, et al. "Detection and tracking meet drones challenge." *IEEE TPAMI* 44(11):7380-7399 (2022). DOI 10.1109/TPAMI.2021.3119563. (VisDrone.)
[40] J. Wang, W. Yang, H. Guo, R. Zhang, G.S. Xia. "Tiny Object Detection in Aerial Images." *2020 25th International Conference on Pattern Recognition (ICPR)* 3791-3798 (2021). DOI 10.1109/icpr48806.2021.9413340
[41] D. Du, Y. Qi, H. Yu, Y. Yang, K. Duan, G. Li, W. Zhang, Q. Huang, et al.. "The Unmanned Aerial Vehicle Benchmark: Object Detection and Tracking." *Lecture Notes in Computer Science* 375-391 (2018). DOI 10.1007/978-3-030-01249-6_23
[42] Darius Lam, Richard Kuzma, Kevin McGee, Samuel Dooley, Michael Laielli, Matthew Klaric, Yaroslav Bulatov, Brendan McCord. "xView: Objects in Context in Overhead Imagery." arXiv:1802.07856 (2018)
[43] Ke Li, Gang Wan, Gong Cheng, Liqiu Meng, Junwei Han. "Object Detection in Optical Remote Sensing Images: A Survey and A New Benchmark." arXiv:1909.00133 (2019) (DIOR benchmark)
[44] G. Cheng, J. Han, P. Zhou, L. Guo. "Multi-class geospatial object detection and geographic image classification based on collection of part detectors." *ISPRS Journal of Photogrammetry and Remote Sensing* 98:119-132 (2014).
[45] S. Ge, J. Li, et al. "Detecting masked faces in the wild with LLE-CNNs." *CVPR* 2017, pp. 426-434. DOI 10.1109/CVPR.2017.53. (Cited only to delimit the MAFA packaging difference.)
[46] S. Yang, P. Luo, C.C. Loy, X. Tang. "WIDER FACE: A Face Detection Benchmark." *2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)* 5525-5533 (2016).
[47] Shuai Shao, Zijian Zhao, Boxun Li, Tete Xiao, Gang Yu, Xiangyu Zhang, Jian Sun. "CrowdHuman: A Benchmark for Detecting Human in a Crowd." arXiv:1805.00123 (2018)
[48] P.V.A.B. de Venâncio, A.C. Lisboa, A.V. Barbosa. "An automatic fire detection system based on deep convolutional neural networks for low-power, resource-constrained devices." *Neural Computing and Applications* 34(18):15349-15368 (2022). DOI 10.1007/s00521-022-07467-z
[49] L. Cascone, M. Nappi, C. Pero, X. Wang. "A framework for bias-aware dataset evaluation in soft facial attribute recognition." *Pattern Recognition* 172:112416 (2026). DOI 10.1016/j.patcog.2025.112416
[50] Y. Huang, Z. Zhang, Y. Huang, Q. Wu, H. Huang, Y. Zhong, L. Wang. "Customized meta-dataset for automatic classifier accuracy evaluation." *Pattern Recognition* 146:110026 (2024). DOI 10.1016/j.patcog.2023.110026
[51] J. Sweeney. "Optimizer Memory Makes Shuffle Order a First-Order Source of Fine-Tuning Noise." arXiv:2606.29554 (2026).
[52] E. Pintelas, I.E. Livieris. "GeNeX: Genetic Network eXperts framework for addressing Validation Overfitting." *IEEE Transactions on Neural Networks and Learning Systems* (2026); arXiv:2603.11056
[53] Y. Tian, Q. Ye, D. Doermann. "YOLOv12: attention-centric real-time object detectors." arXiv:2502.12524 (2025).
[54] H. Suo, H. Wang, Y. Li. "Checkpoint Selection and Evaluation in EEG Emotion Recognition." arXiv:2607.27655 (2026).
[55] N. Ajroldi, A. Orvieto, J. Geiping. "When, Where and Why to Average Weights?" arXiv:2502.06761 (2025).
