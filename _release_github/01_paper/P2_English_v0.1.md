# Configuration-level split aliasing in object-detection benchmarks: how the reported split is selected on, how far the selection transfers, and what a three-way protocol reveals

**Working title (v0.1). Target venue: Pattern Recognition (Elsevier).**

> **Provenance of this file.** The English submission form of the P2 manuscript, a faithful
> translation of the Chinese governing draft `评测有效性稿_正文_v0.1.md`
> (md5 `fe880ca0e3af77983382065db75255f3`, the state it was translated from, 2026-09-18; that draft is a live
> document, re-hashed whenever it changes — see `work/verify_text_hashes_20260917.py`); every number is unchanged and backed by the
> local artifacts listed in the Supplementary Material. Where the drafts disagree, the Chinese governs.
> Citation numbers refer to `P2_参考文献_v0.1.md` (**40 entries, all verified**), seven added
> in r39 ([34]–[40]) for the venue's 35–45 reference band, all verified against Crossref or DataCite
> DOI records; this form cites **every** entry, including the benchmarks and frameworks that the
> governing Chinese draft names without numbers. The four citations unresolved in the first
> draft — [A] the CVPR 2026 geospatial leakage audit, [B] AI-TOD, [C] UAVDT,
> [D] D-Fire — are **now verified** as **[30] [31] [32] [33]**; two of the four titles and
> one venue had differed in an unverified citation (see that file, §4).

---

## Abstract

Object-detection papers report a number from a split they call held out. We audit the configuration
behind that premise: **6 of 14** YOLO configurations we produced bind `val:` and `test:` to one
directory, so the reported checkpoint was selected on the reported split. Training and evaluation do
not overlap at the image level — the intersection is exactly zero — so this is not contamination but **checkpoint
selection**, positive in all four cells measured on 569 runs (all four now powered; §5.1), the baseline
arm gaining more. Its
direction is **not single-valued**: in 19 public benchmarks the reported number comes from a
non-independent split in **12/19** (§6.1, single-rater: a second reading), yet four all-correct answers exist by counting unit. A three-way split
remediation reproduces the headline effect (smoke→SFCHD **+1.434 pp**, 10/10 seeds positive) while adding
seeds lowers the mean by **9 %–29 %**, a direct measure of seed inflation.

**Keywords:** evaluation validity; dataset splits; checkpoint selection; object detection; benchmark audit;
reproducibility

---

## 1. Introduction

A detection paper reports mAP50-95 on a split it calls held out, implying a number that estimates
performance on unseen data. The inference needs a premise the paper rarely states: the checkpoint was not
chosen on that same split. Binding `val:` and `test:` to one directory breaks it silently — the pipeline evaluates
there, keeps the best-scoring checkpoint and reports its score: a **maximum**, not a sample. Surveys of the detection literature [36] trace how that number became the
field's unit of comparison; this paper audits the reporting convention producing it.

That premise is audited in three places, in increasing distance from our own work: **our own corpora**,
where we count how many of the YOLO configurations we produced alias the two keys; **19 public
benchmarks**, audited row by row for which split the reported number comes from; and **20 published
third-party training logs**, where we measure the premium directly, in data we did not produce.

Three further things we have not seen done here. We **remediate** with a three-way split separating the
selection set from the reported set, plus a recomputable protocol, reporting the consequences, not only the
fix. We **measure the premium's fate**: `best` and `last` checkpoints and both splits exist, so the full
2 × 2 grid is computable: how much of the val-selected premium is realized on an independent split? And we **pre-register** a generalization hypothesis, then report that it misses its criterion.

### 1.1 Why the unit matters

Ask "how many of these benchmarks have a split problem?" and, unless a unit is declared, every answer is
defensible and they disagree by a factor of six: 2/19 (the release artifact binds both keys to one path),
10/19 (no independent held-out test is provided), 13/19 (the official protocol does not let you evaluate an
independent test locally), 12/19 (the reported number comes from a non-independent split). We therefore
treat "declare the unit" as a contribution, not a caveat (§3, §6).

### 1.2 What we do not claim

We do not claim that aliasing is data contamination: the image-level intersection between the
training images and the held-out evaluation images is **zero**. We do not claim a single bias direction: our paired analysis finds **two corpora
where `val` understates the effect and two where it overstates it**, nine cells not significant (§5.1). We
do not claim the convention is framework-general (§6.5), nor that the benchmarks we audit are wrong: they
report what their configuration computes.

**Positioning (one sentence).** We claim neither to be first to audit split problems in detection benchmarks
nor to audit image-level leakage: both are taken. We occupy a different cell — **configuration-level
aliasing, a direction that varies by corpus, and the requirement that a count declare its unit.** Every number points to a local artifact; every claim narrowed after external checking is
recorded as narrowed (§5.4).

**Scope.** All quantitative claims about selection behaviour come from **YOLO-lineage pipelines**, the only
family among the five frameworks we checked selecting the checkpoint by the validation metric by default
(§6.5) — stated at the claim, not only in a limitations section.

---

## 2. Contributions and related work

### 2.1 The closest work, and where this paper sits

The table was verified against the **full texts** of both 2026 studies (PDFs archived; extraction script
retained).

> **Table S1** → Supplementary §S8.

None of these works is wrong — **they audit images, we audit configurations.** Image-level duplication
inflates the metric (both 2026 studies measure that); configuration-level aliasing shifts the **comparison
between arms**, whose direction we measure as **not single-valued**.

They instantiate the taxonomy of [34] and [35]: leakage is the mismatch between the data used to choose a
model and the data used to score it, duplication one such mismatch [3].
Binding `val:` and `test:` to one directory creates the same mismatch **without duplicating an image**, so
de-duplication cannot find it — why the two literatures have not met.

**Why this is a selection question, not only a leakage question.** The bias we measure is
the one the model-selection literature has described for decades: **choosing a model by its
score on a validation set makes the reported score optimistic** [41], [42], and the classical
remedy is to *nest* the selection inside the evaluation rather than to de-duplicate the data.
In detection benchmarks that remedy is unavailable in practice **until the configuration is
read**: the selection step is implicit — the training script writes `best.pt` by fitness and
the paper reports that checkpoint — so a reader who trusts the split names sees a held-out
evaluation where the pipeline in fact performed a **maximum**. The two literatures that do
confront benchmark erosion — reused test sets [43], standard splits [44] — therefore
describe a bias that this configuration reaches without any data being reused or mis-split.
We take [41], [42] as the general statement and report the detection-specific instantiation:
**the selection premium (best − last), and how much of it transfers to a disjoint split**
(§5, §8).

**The sharpest contrast** is the two closest works: *Technologies* 2026 [1], which audits a detection pipeline at the **image** level, and *Drones* 2026 [2], which: it too reports a val-vs-test gap, but concludes "no
systematic direction", treating split agreement as evidence that model selection has not overfit
validation. We measure a **different quantity**, in two tiers: (i) the selection premium (best −
last) is positive in all four cells, the baseline arm gaining more (four paired CIs excluding zero);
(ii) the paired Δgap on three-way corpora **varies in sign** (2 cells where `val` understates, 2 where it
overstates, 9 not significant). We therefore do **not** write "understated" unqualified, and state the difference from [2]: [2] reports a
raw val-minus-test gap, mixing two splits' difficulty, **not identifiable**, whereas our **paired
difference** cancels difficulty and still shows a residual shift. [30] is supporting, not competing: cited only as evidence that the genre has a
venue, not as a comparable quantity.

### 2.2 Contributions

1. **We quantify the magnitude and direction of configuration-level aliasing.** The selection premium
   (best − last) is **positive in all four cells**, **the baseline arm gaining more** (four paired 95 %
   CIs excluding zero, §5.1 Tier 1). **All four cells are powered (n = 10–11)** — the fourth,
   `dota15`, entered at n = 3 and was escalated to n = 10 under a criterion fixed in advance by the shared review protocol (Supplementary S6) before
   the runs existed; it is met (§5.1) ⇒ the convention systematically shifts **arm-to-arm comparisons**; yet
   the shift's **sign varies by corpus** (three-way paired differencing: 2 cells where `val` understates, 2 where it overstates, 9
   not significant — and the four crossing cells are now **all at n = 10**, the two overstating ones only after the escalation in §5.1).
   **We do not claim a general understatement** (§5). It appears in third-party logs too (20 logs / 6 sources, median +1.04 pp, max +5.65 pp,
18/20 positive; §5.5) — a sample, not a field-level rate.
   *Note: **image-level** leakage magnitude is quantified by the two 2026 studies;
   **configuration-level** aliasing magnitude has not been measured before.*
2. **We show that "how many benchmarks have a problem" needs a declared unit**, and give a recomputable
   table in four units with per-row evidence classes (§3, §6): four defensible answers.
3. **We give a remediation protocol and report its consequences.** Under a three-way split the effect
   reproduces (n = 10), while adding seeds lowers the mean by 9 %–29 % (§8) — a direct measurement of
   selection inflation; the premium's realization becomes measurable (**19 %**, §8.6).
4. **We disclose our own defects** rather than removing them: our analysis' first version had
   non-reproducible items — scripts depending on a rented pod, a citation to a file not containing the
   quoted numbers, no written endpoint convention. §10, not deleted.

### 2.3 What we explicitly do **not** claim (shared tooling)

This paper and the budgeted fine-tuning study it re-measures — the companion paper — share **process
protocols**: a multi-model review checklist and a local/cloud workflow discipline (scripted remote
execution, all-or-nothing patching, audit anchors, a local artifact pointer behind every number). **Both are project-internal protocols, not publications, and not a
methodological contribution of this paper.** By agreement, neither paper may present them as its own
methodology. This paper displays only their **outputs**: the six self-reported defects in §10 and the
artifact pointer behind every number. So does the **audit-anchor system** (a mechanically checked set of anchors that must all
pass on every rebuild of this manuscript): shared tooling, no contribution claimed. Whether those documents appear in a
submission is a joint decision of the two papers; this paper asserts only that the same protocols were
used, and originality is not claimed. Corresponding statements appear in the companion.

---

## 3. Units: the methodological premise

"Have a split problem" is a property of a **(benchmark, counting unit)** pair, not of a benchmark. We use four units, defined by **who controls the split**:

> **Table S2** → Supplementary §S8.


**The `reported` unit is read from the release documentation and from the dataset's own paper**: we did not sample papers per benchmark and make no claim about how often the community reports a given split; a stated-frame literature sample is future work (§12). For each of 19 benchmarks we record all four units, an evidence class and a confidence level, and recompute every percentage from the row markers under a per-unit subtotal check. The full 19 × 4 table, the subtotal checks and the cross-check against the original audit are **Supplementary S1**; the derived counts are in §6.1.

**The premise we rely on throughout:** a "yes" under any unit means *the reported number is not a sample from an independent split*. It does **not** mean the benchmark is broken or the experiment dishonest; the number does not license a generalization claim.

---

## 4. Finding 1: our own corpora

### 4.1 How common the aliasing is

In **our own** experimental corpora, **6 of 14** bind `val:` and `test:` to the same directory. Counting by file, not by corpus, the whole-tree scan covers **19 YAML files**; on our own manifest the ratio is **8 of 28**. One case is maximal: for **SHWD all three keys** [25] (`train:`, `val:`, `test:`) **point to a single directory**.

**This is not contamination.** The image-level intersection is **exactly zero**: training and evaluation images do not overlap. It changes not *what* was evaluated but *which checkpoint* was reported, turning "selection contamination" from an ethical question into a **measurement** question.

### 4.2 The failure is produced by a tool, not by carelessness

A PASCAL VOC [13]→YOLO conversion script wrote two keys from one `images_dir`, so `train == val` appears **because the generator could not produce distinct values** (§6.1 records the same for Mendeley face-mask [27]). §11's first recommendation: make "are `val` and `test` the same source?" a **pipeline-level hard check** — human YAML review will not catch it. Two upstream projects have had to repair exactly this class of defect in their own splits — one by pointing the training evaluation at the real `test` split (rf-detr [4]), the other after three test drives were found inside `train` (ultralytics issue #25650 [5]).

---

## 5. Finding 2: the selection premium — magnitude, direction, and mechanism

**Evidence.** `eval_validity/selection_premium_local_20260916.txt`, reading **569 published runs** from the local archive (the local version is the 2026-09-16 repair).

**Definition.** premium = **best-epoch − final-epoch** mAP50-95 **within a single run**. When `val == test`, "best" was selected on the reported split, while `last` and `last5` are endpoints **no selection rule can reach**. This is the checkpoint-selection term of the run-to-run variation studied in [37] (early stopping, data order) and [38] (benchmark variance across seeds): what those works average over as uncertainty, we measure as a reproducible component.

> **Table S3** → Supplementary §S8.


### 5.1 Direction: reported in two tiers, and the second tier's sign varies by corpus

The direction claim **must be reported in two tiers**: collapsing them into "the convention understates the effect" is wrong — external checking refuted it (§5.4, II).

**Tier 1: the selection premium is positive in all four cells, and the baseline arm gains more.** The tested quantity is the paired difference d(seed) = premium_baseline(seed) − premium_strategy(seed), within cell and seed:

**Table 1.** Tier 1 — the selection premium per arm and the paired difference between arms, by cell. Source: `verify_two_critiques_20260916.txt`.

| Cell | n | premium baseline | premium strategy | **paired diff** | sd | t | p | 95 % CI |
|---|---|---|---|---|---|---|---|---|
| smoke2sf (strong) | 11 | +0.799 | +0.382 | **+0.416** | 0.240 | 5.74 | 1.9×10⁻⁴ | [+0.255, +0.578] |
| shwd2sf (corroborating) | 11 | +1.038 | +0.512 | **+0.526** | 0.207 | 8.41 | 7.6×10⁻⁶ | [+0.386, +0.665] |
| a2d15 (directional probe) | 10 | +0.534 | +0.262 | **+0.272** | 0.183 | 4.69 | 1.1×10⁻³ | [+0.141, +0.403] |
| dota15 (within-domain) | 10 | +0.941 | +0.492 | **+0.449** | 0.196 | 7.23 | 4.9×10⁻⁵ | [+0.309, +0.589] |

**Table 2.** Tier 2 — the paired difference Δgap by corpus, with the reading it supports. Δgap > 0 means `val` understates the strategy arm’s effect. Source: `xeval_analysis_20260916.txt`.

| Corpus | n | Δgap (pp) | p | 95 % CI | Reading |
|---|---|---|---|---|---|
| shwd2sf | 10 | **+0.779** | 0.0053 | [+0.297, +1.261] | `val` **understates** |
| smoke2sf | 10 | **+0.461** | 0.0263 | [+0.068, +0.855] | `val` **understates** |
| p_aitovis | 10 | **−1.226** | 1.3×10⁻⁸ | [−1.370, −1.081] | `val` **overstates** |
| p_vistod15 | 10 | **−3.315** | 6.5×10⁻⁹ | [−3.676, −2.953] | `val` **overstates** |
| other 9 cells | 3–10 | −2.46 to +13.66 | ≥ 0.054 | all include 0 | **not significant** |

*(The third §5 evidence table, S5, is in Supplementary §S8.)*

**The four paired differences are +0.416 / +0.526 / +0.272 / +0.449 pp** (Table 1, in cell
order) — **all four cells powered at n = 10–11, and all four 95 % CIs excluding zero** (p from
7.6×10⁻⁶ to 1.1×10⁻³). `dota15` entered this table at n = 3, where §7.1 permits only "significant
under the paired t-test; the non-parametric test is unavailable at this n", and that three-run cell
included two runs without a seed identity (§5.3, §10). Both are now history rather than a caveat:
the escalation below supplies ten seeded runs and a permutation-valid p. The right scale is the SE of the difference (**0.058–0.120 pp**): **each arm is a mean over
10–11 seeds**. Runs are **independently randomized**, so pairing brings
**no** variance benefit: the paired t of 5.74 and the unpaired (Welch) t [29] of **5.68** agree — **the conclusion does not depend on pairing**. (The critic's 0.515 pp is the **single-run**
data-order component of §8.4; see §5.4 (I).) Endpoints no selection rule can reach make the paired contrast **larger**:


Paired t-tests are all p ≤ 1.4×10⁻⁹ (n = 10–11). **Tier 1 may be stated as directional**: the baseline arm
benefits more from selecting on the reported split.

**The n = 3 cell was escalated, and the criterion fixed for it in advance was met.** Tier 1's
fourth cell, `dota15`, entered this table at n = 3 with a parametric p = 0.039, below the resolution
of any sign-flip test there (§7.1); the pre-declared consequence was that a ten-seed paired difference
failing to be positive with ≥ 8/10 same-sign and a CI excluding zero would remove the cell from the
four-cell headline. Ten seeds (42–51) give **+0.449 pp**, t = 7.23, **p = 4.9×10⁻⁵**,
95 % CI **[+0.309, +0.589]**, **10+/0−** — **the criterion is met as stated**, so the cell is read as
powered rather than directional. Its mean is **24 % below** the n = 3 value (+0.589 → +0.449), a
fourth instance of §8.4's seed inflation inside the published 9 %–29 % band. Per-seed values, the
recipe-identity check across the cell's twenty `args.yaml`, and the GPU-memory sensitivity run are in
**Supplementary S28**.

**Tier 2: on the same three-way corpora, the paired difference Δgap varies in sign.** The raw quantity
`M_val(ê) − M_test(ê)` is **not identifiable**: it ranges from **−33.0 to +21.2 pp**, and with
**no per-epoch test evaluation** the components cannot be separated. What remains is the **paired
difference**, each arm's gap subtracted within seed, which cancels the difficulty term:

> Δgap = (arm difference on val) − (arm difference on test); **Δgap > 0 means `val` understates the strategy arm's effect**

The four cells crossing the line: **+0.779 pp** (shwd2sf) and **+0.461 pp** (smoke2sf) — `val`
**understates**; **−1.226 pp** (`p_aitovis`) and **−3.315 pp** (`p_vistod15`) — it **overstates**.
**All four are now powered and none is n = 3**: the two overstating cells were escalated from n = 3
to n = 10 under criteria fixed in advance, and both met them (reported immediately below).
Four of 13 cells cross the uncorrected line at
p < 0.05; three marginal cells (`aitod20` +1.481,
p = 0.054; `fire` +13.658, p = 0.061; `mende20` +2.472, p = 0.099) **do not cross the line and we make no claim about them**. **These 13 cell tests are reported
uncorrected, as a descriptive scan. Across the 13, a Benjamini–Hochberg correction at q = 0.05
**now leaves three cells significant** — `p_vistod15` (6.5×10⁻⁹) and `p_aitovis` (1.3×10⁻⁸) far
below their lines, and `shwd2sf` (0.0053 against a line of 0.0115), because the two very small
p-values at the front of the ordering lift the lines behind them; `smoke2sf` (0.0263 against
0.0154) does not survive. **This reverses what we reported before the escalation**, when the
smallest p (0.0053) lay above the first line (0.00385) and nothing survived — the change comes from
measuring two cells at n = 10 instead of n = 3, not from choosing a different test. So the Tier 2
sign pattern now also carries three cells that survive the paper's own family correction; §9 applies
BH within its own family of three registered pairs, where the count is stated separately.** **Proposition 5 of §13 gives the formal reason this count depends on the declared family.**


**The two overstating cells were escalated too, and both met their pre-declared criteria.** The
plan fixed before the runs (40 runs, seeds 42–51 × 2 arms × 2 cells; paired *and* sign-flip tests;
`{best, last} × {val, test}`; a prespecified correction) named the strong branch of its outcome rule:
*"both remaining negative and significant with permutation p ≤ 0.002"*. At n = 10: `p_aitovis`
**−1.226 pp** (95 % CI [−1.370, −1.081], t = −19.17, p = 1.3×10⁻⁸, **0+/10−**, permutation
p = **0.001953**) and `p_vistod15` **−3.315 pp** ([−3.676, −2.953], t = −20.76, p = 6.5×10⁻⁹,
**0+/10−**, permutation p = **0.001953** — 2/2¹⁰, the attainable floor at n = 10). **Both conditions
are met**, including **Holm across the two targets**, so **the abstract stays as written and its weak
form is strengthened**: "`val` understates in two cells and overstates in two" no longer rests on two
n = 3 rows. The endpoint the comparison rests on was identified rather than assumed — our
re-evaluation of `best.pt` on `test` reproduces the archived `sio_b_results.csv` to 0.0046 pp — and
the per-seed values, the endpoint check and the auxiliary quantities are in **Supplementary S29**.

**The sharpest single fact**: in the shwd2sf cell the arms differ
on **val** by 60.669 − 60.397 = **+0.272 pp** (baseline better) and on **test** by 43.559 − 44.066 =
**−0.507 pp** (baseline worse). **The sign reverses**, so reading only `val` inverts the arm ordering.

**The paper's formal claim is therefore:** the convention systematically shifts **arm-to-arm comparisons**
(Tier 1: four cells, same sign, CIs excluding zero); **the direction of that shift varies by corpus**
(Tier 2: 2 understate / 2 overstate / 9 not significant) — **neither "a general understatement" nor
"no systematic direction".**

**Scope (cross-framework boundary).** The convention this paper audits belongs to the **YOLO lineage — Ultralytics YOLO [12] and YOLOX [8]** — whose configuration points `val:` at the split it selects on. We checked five mainstream frameworks at pinned commits: **only that lineage does this by default** — Detectron2 (`TEST.EVAL_PERIOD = 0`) [7], MMDetection [6], DETR [10] and PaddleDetection [9] **report the final epoch instead** (§6.5). **"The convention" here
therefore means that pipeline family's convention, not the field's.**

**Feasible cross-validation.** M_test(ê) arm differences from `sio_b_results.csv` — smoke2sf
**+1.434**, shwd2sf **+0.507** — match the published clean-protocol readings of §8.2 **at the printed precision**:
independent evidence that two machines and protocols agree.

### 5.2 Two versions must be disclosed side by side

The same script on the **pod root** (347 runs, n = 10) gives a smoke2sf premium of **+0.786 / +0.390**;
on the **local archive** (569 runs, n = 11) **+0.799 / +0.382** — agreeing in sign and magnitude,
not value. **The main text uses the local version**; the pod version is recorded as a cross-check.

### 5.3 The dota15 cell: now reproducible, and one wording defect exposed
**This cell was not reproducible from the release as first written, and the repair exposed a wording defect** (both disclosed, §10 row 2). The repair, the value-by-value agreement and the defect are recorded in **Supplementary S12**.
### 5.4 Two external critiques, checked (one refuted, one judged non-identifiable)
**Two external critiques were checked: one refuted, one judged non-identifiable.** The refuted one compared the premium difference against a single-run component (0.515 pp) rather than the standard error of a difference of arm means; the other asked for the raw `M_val − M_test`, whose difficulty term cannot be separated from selection optimism. **We used to write** that the gap was simply unidentifiable in this archive; the external check **corrects this to** the paired-difference form, which cancels the difficulty term under the pairing assumption stated in §13. Details and the recomputation are in **Supplementary S12**.
### 5.5 The same component in third-party public logs (independent evidence)
**The same quantity appears in other people's logs**: 20 logs from 6 sources, median **+1.04 pp**, max **+5.65 pp**, 18/20 positive — a sample, not a field-level rate. **The sampling frame**: logs found by repository **search** (Kaggle and public repositories), with the exact queries in **Supplementary S12**; it is a sample, and public logs **cannot establish aliasing** at the configuration level. The rest of the frame and what the sample cannot support are in **Supplementary S12**.
### 5.6 Why Δgap's sign varies by corpus: three of five candidate mechanisms are refuted by the data
**Three of five candidate mechanisms are refuted and the mechanism itself is not identifiable**: the sign of Δgap is a sum of same-order terms, so no single mechanism can be read off it (§13, Proposition 3). **The paired quantity is nonetheless identifiable and is what we report; the raw `M_val − M_test` is not identifiable at all.** The candidate-by-candidate examination, the per-cell components and the exact identity are in **Supplementary S12** and Table S8–

S10.
## 6. Finding 3: how general this is across public benchmarks

**Evidence**: `benchmark_split_audit.md`, a line-by-line audit of 19 benchmark rows, plus
`split_units_19rows_20260916.md` (recomputation script; no hard-coded percentages).

The 19 audited benchmarks, with the release or dataset paper read for each: COCO [18], PASCAL VOC [13], Objects365 [14],
Open Images v7 [15], DOTA v1.0 and v2.0 [22], VisDrone-DET [23], AI-TOD [31], UAVDT [32], xView [19],
DIOR [21], NWPU VHR-10 [16], SHWD [25], SFCHD [26], MAFA [24], Mendeley face-mask [27], WIDER FACE [17],
CrowdHuman [20], D-Fire [33]. The question is **evaluation validity**. Dataset-level bias auditing [39]
and classifier-accuracy estimation [40] are neighbours: both ask whether a reported number measures what it
is taken to measure, but neither audits a release's configuration binding.

### 6.1 The result under four units (single-rater judgements)

**Table 3.** The four counting units over the 19 audited benchmarks. **A count is meaningless without its unit** (§3). Source: `split_units_19rows_20260916.md`.

| Unit | non-independent | of decidable rows | undecidable |
|---|---|---|---|
| **release** (the benchmark's own release) | **10/19 ≈ 53 %** | 10/19 | — |
| **protocol** (the official protocol) | **13/19 ≈ 68 %** | 13/19 | — |
| **yolo_dist** (the generic YOLO distribution package) | **4/19 ≈ 21 %** | **4/15 ≈ 27 %** | 4 rows |
| **reported** (the layer actually reported) | **12/19 ≈ 63 %** | **12/15 = 80 %** | 4 rows |
| ↳ of which **literal two-key same path** (= the 2/19 the original audit reported) | **2/19 ≈ 11 %** | 2/19 | — |
| **reported − clean** | **3/19 ≈ 16 %** | 3/15 | 4 rows |


**These 19 rows were coded by one rater** (§10 defect 5 records that the audit is hand-written, with
28 literal judgements and no second rater), so every count below is a single-rater count.

**Which number the `reported` unit judges.** For one row the answer depends on which reported
number is meant: COCO. Community tables report the **server-scored `test-dev`** value, which no
local run can be selected on, and we count that as independent; a paper's own ablations report its
**`val`** value, which is also the selection split. On the first reading `reported` is **12/19** and
**3/19** are clean; on the second, **13/19** and **2/19**. No other row is affected. This article
prints the first reading in the abstract and states both here.

**Subtotal checks**: reported **12 + 3 + 4 = 19**; `yolo_dist` **4 + 5 clean + 6 with no `test:` key +
4 undecidable = 19**; `release` 10 + 9 = 19; `protocol` 13 + 6 = 19.

**Correction to the first version of this table.** It **put 2/19 under
`yolo_dist`**, contradicting the recomputation: `yolo_dist` is **4/19** (PASCAL VOC and SFCHD's **literal
two-key** alias, SHWD's `train == val`, Mendeley's generator-produced alias), while **2/19 is only a subset
of it** — the A-evidence, literal `val == test` rows the audit reported. The table makes **a unit a whole column**, ordered as §3's four definitions.

**Algorithm self-check**: on the **literal two-key subset** the table **reproduces the audit's 2/19**
(PASCAL VOC, SFCHD), so the difference comes from **the unit**, not from a transcription
error; the whole `yolo_dist` column is **4/19**.

**One row belongs to a different unit.** Mendeley face-mask's `train == val` comes from a **generator**
(a VOC→YOLO conversion script writing two keys from one `images_dir`), not a distribution package, so it is
not counted in the 2/19 and must be described separately.

**A number we deliberately do not use.** The audit's "63–79 %" upper bound (15/19) has **no
enumeration**; we do not cite it.

### 6.2 "Same directory" has four levels, and the audit reported only the narrowest
**"Same directory" has four levels, and the original audit reported only the narrowest.** The levels, the rows each admits, and the resulting shift in the headline number are in **Supplementary S12** and Table S12.
### 6.3 We do **not** reproduce the original audit's two numbers, and we say why
**We do not reproduce the original audit's two numbers, and we say why**: one rests on the narrowest reading of "same directory", the other on a stale snapshot. The recomputation and the reason for each difference are in **Supplementary S12** and Table S13.
### 6.4 One judgment the evidence does not support (corrected)

The audit classified the FireSmoke mirror family row as "mixed" solely from a config with
`train == val`, but **another line of the same document records that this config is based on SHWD**. All
three FireSmoke/D-Fire copies have **three separated keys**, so D-Fire moves to the clean group.

### 6.5 Across frameworks: is the convention specific to YOLO?
**Only the YOLO lineage does this by default.** At pinned commits, Detectron2 (`TEST.EVAL_PERIOD = 0`), MMDetection, DETR and PaddleDetection **report the final epoch instead**; the file-by-file evidence (23 official configuration files) is in **Supplementary S12** and Table S14. **This is a targeted sample at pinned commits, not a census** of the five frameworks, and "the convention" therefore means that pipeline family's convention, not the field's.
## 7. Finding 4: what "significant" means, and how the endpoint convention changes it

### 7.1 With n = 3 a permutation test **cannot** reject in principle

**For a sign-flip permutation test on n pairs, the smallest attainable two-sided p is 2/2ⁿ** — for n = 3,
**0.25**. Every n = 3 cell still in our tables has a permutation p of 0.25: **not** "not significant"
but "no resolution at this n". **After the two escalations reported in §5.1, no cell of the headline
tables (Tables 1–2) is n = 3 any more**; the n = 3 cells that remain are the nine non-crossing rows
of the 13-cell scan in Supplementary Table S8.

**Consequence.** An n = 3 cell may only read "**significant under the paired t-test; the non-parametric
test is unavailable at this n**", **not** a bare "p = 0.025" — one reviewer question, "which test is
that?", exposes the difference.

The attainable floors are: n = 3 → **0.25**; n = 6 → **0.031**; n = 7 → **0.0156**; n = 10 → **0.0020**.

### 7.2 Both conventions become significant only at n ≥ 6
**Both conventions become significant only at n ≥ 6** — below that a permutation test has no resolution (§7.1). The clean-protocol seed extension that reaches n = 10, and the per-cell numbers, are in **Supplementary S12** and Table S15.
> **First-report attribution (a convention we hold to).** The two Δ values here (**+1.434 / +0.507 pp**)
> are the **primary readings of the companion paper**, our budgeted fine-tuning study: this paper cites
> them, marks them as such, and does **not** claim them as first reports. What this paper reports first is
> the three-way protocol, the selection premium (§5), and its consequences (§8.3). The full statement —
> including how the companion is named to the editor while it carries no identifier — is in
> **Supplementary S12**.

### 7.3 A cross-archive endpoint conflict on the same run (investigated — and itself a disclosure)
**One run is recorded with two different endpoints in two archives** — "final" (67.12) in one and "best" (70.06) in the other — i.e. **which checkpoint is recorded was never specified**; §10 discloses it and the two readings' consequences (significant versus not) are worked out in **Supplementary S12** and Table 

S16.
## 8. Finding 5: a remediation protocol and its consequences

### 8.1 The protocol
**The protocol**: three-way corpora, YOLOv12n [11] + shapeiou, a 20 %-budget fine-tune at 100 epochs, seeds 42–51. The steps, the carve construction, the run inventory and the disjointness audit are in **Supplementary S12**.
### 8.2 Results: the effect reproduces, but the magnitude falls

> **Table S17** → Supplementary §S8.


**Both readings must be stated**: the effect **reproduces** under a protocol separating selection from
reporting, and the magnitude is not comparable with the old protocol (different unit). All
reported metrics come from the **test** split (`sio_b_results.csv`), **not** the per-epoch `results.csv`
values — a different quantity; our first version **took the wrong column** and the fix is on the record.

> **A defect in the document that reports these numbers.** The clean-protocol results document **cites a
> ledger file that is not merely misnamed**: neither `_r10_final_stats.txt` nor the file later identified as
> the "real log" (`_r10_stats_0403.txt`) contains **any** of that document's headline values (6 probes each,
> 0/6 hits) ⇒ **these numbers have no surviving stdout ledger.** We **do not** point at a replacement file
> (renaming would only manufacture a new false citation). Where this paper cites those numbers it says so;
> the p-values can be recomputed from `pvalue_table_local.py`.

**Recomputation status (updated 2026-09-16).** These readings were originally **not locally recomputable**:
the local archive lacks 6 of 7 corpora, which the script that *constructs* the three-way split needs
(defect 5 in §10). We therefore ran a **2 × 2 evaluation** on a GPU machine — 41 three-way runs ×
{`best`, `last`} × {`val`, `test`}, **164 evaluations, 0 failures** — and pulled back the per-epoch curves,
`sio_b_results.csv` and the matrix: **84 files with a SHA-256 list** (`xeval_20260916/`).
**This section's readings and §5.6's decomposition are therefore locally recomputable**; **retraining is
not**, needing the corpora. The batch also reproduces the archived `best × test` values to within
**0.0047 pp** (median 0.0021 pp) across all 41 runs.
### 8.3 A direct measurement of selection inflation
**A direct measurement of seed inflation**: adding seeds lowers the mean by **9 %–29 %** of the headline effect; the estimand is the change in the mean, not a single-run quantity. The design, the per-cell changes and the check against recomputed means are in **Supplementary S12** and Table S18. **The section title is deliberately the weaker, sample-scoped claim** ("the excluded one is the smaller in this sample"), since with three initializations the interval is wide: the components are **consistent with, not established by**, these three initializations.
### 8.4 The three variance components: the excluded one is the smaller in this sample
**The three variance components, and the excluded one is the smaller in this sample**: the single-run data-order component is **0.515 pp**, against initialization and seed components of the same order. What was held fixed, and why this is a sample statement rather than a general one, is in **Supplementary S12** and Table S19.
### 8.5 Why "same-pipeline pairing" is a necessity, not a habit
**Same-pipeline pairing is a necessity, not a habit**: mixing two pipelines' `val`/`test` conventions would confound the split convention with the framework. The reasoning and the counterexample are in **Supplementary S12**.
### 8.6 The premium's realization rate: **19 %**

**Measured on the GPU machine for this revision** (script `work/rcmd/xeval_3way.py`;
artifacts `xeval_20260916/matrix.csv`, per-run archives).

Separating the two raises a question unaskable
before: **how much of the gain selected on `val` survives on `test`?**

**Method**: the **2 × 2 evaluation** described above, with `split=test`, `batch=32`,
`imgsz=640`, `plots=False`.

**Table 4.** The premium selected on `val` versus what that same selection action realizes on the disjoint `test` split, per arm-cell. Source: `xeval_20260916/matrix.csv`.

| Cell | Arm | n | `prem_val` | **`prem_test`** | **realization rate** |
|---|---|---|---|---|---|
| shwd2sf | baseline | 10 | +1.469 | **+0.735** | **50 %** |
| shwd2sf | strategy | 10 | +0.865 | **+0.151** | **18 %** |
| smoke2sf | baseline | 10 | +0.691 | **+0.507** | **73 %** |
| smoke2sf | strategy | 10 | +0.605 | **−0.158** | **−26 %** |
| aitod20 | baseline | 1 | +0.786 | **−0.377** | −48 % |

**Two more cells, measured the same way — and they land at the other end.** The escalation in §5.1
adds four arm-cells to this measurement: realization rates **82 % / 104 %** (`p_aitovis`, baseline /
strategy) and **56 % / 29 %** (`p_vistod15`), pooled **55 %** against the **19 %** above. We do
**not** re-average that headline — it is defined over §8.6's own four arm-cells and Table 4 stays as
printed — but the contrast supports this section's own conclusion (§8.7): **the realization rate is
not a constant across corpora**, so "19 %" is a property of *those* cells rather than of the
convention. (In `p_aitovis`'s strategy arm the realized premium slightly exceeds the selected one,
104 %, i.e. within noise on quantities of ~0.27 pp.) Source: `work/x1_aux_20260918.py`.
**A theory-driven check on this very quantity.** §13 derives the realization rate as
**1 − WC / premium**, where WC is the winner's-curse part of the selected gain — the piece that came
from the `val` split's own noise rather than from real progress. Two consequences are testable on the
archive, and both hold. ① The inequality is **per run**, not just on average: over the 81 runs whose
two sides are both measured, WC = `prem_val` − `prem_test` averages **+0.463 pp** (t = 8.34,
p = 1.8×10⁻¹²) and the realized premium is smaller in **68 of 81** runs. ② The rate should **fall as
the `val` curve gets noisier**: sorting those runs by the noise scale σ̂ of their own `val` curve
gives terciles of **65.6 % / 49.8 % / 13.8 %**, Spearman **ρ = −0.466** (p = 1.3×10⁻⁵, n = 80).
**This section's 19 % and §8.7's per-cell variation are therefore the same statement at different
noise levels**, which is why we do not present 19 % as a constant of the convention. What does **not**
hold is the stronger form we first wrote down — that the premium itself scales with the noise as
σ√(2 ln E): the regression slope is 0.026 ± 0.222 (p = 0.82, n = 101), because the premium's *level*
is set by the shape of the `val` curve (how far the peak sits before the final epoch). §13 records
that withdrawal. Scripts: `work/theory_p4_test_20260919.py`, `work/theory_meta_and_tests_20260919.py`.



where `prem_val = V_max − V_final` (**selecting on val**, the book value) and
`prem_test = T_best − T_final` (**realized on test**).

**Aggregate: `prem_val` mean +0.883 pp → `prem_test` mean +0.172 pp — a realization rate of 19 %**
**(a run-level bootstrap puts the run-weighted figure at 32.7 %, 95 % CI [17.2 %, 47.9 %], P(rate ≤ 0) = 0.000, so the interval excludes no-realization; script `work/x2b_kappa_arms_20260918.py`).**
**The weighting is declared here**: the ratio of **unweighted arm-cell
means**, each of the five arm-cells counting once, the single-run `aitod20` cell carrying **20 %**
of the weight; two other defensible weightings give **32.3 %** (by runs, n = 41) and **34.0 %**
(the four n = 10 arm-cells only), and that most of the premium selected on `val`
is **not** realized on an independent split holds under all three. In
**two of the five arm-cells the realized premium is negative**: the selection action
does not merely fail to pay off, it **costs**.

(`best.pt × val` versus the per-epoch maximum in
`results.csv` differs by up to 0.083 pp, since `best.pt` is selected by **fitness**, not necessarily by
mAP50-95 — itself a convention.)

**Four limitations**: ① the two cells escalated in §5.1 (`p_aitovis`, `p_vistod15`) now also reach
n = 10 and their runs and test-side evaluations are **local** (`x1_tier2_20260918/`), but the
remaining 9 cells' runs are **not local**; ② `prem_test` uses only **best and last**, not a
per-epoch curve;
③ `last.pt`'s val recomputation differs from the final `results.csv` row by ~0.02 pp; ④ this section
does **not** touch the 19-benchmark census of §6.

### 8.7 The per-epoch view: the realization rate is not a constant

The runs of §8.6 **retain intermediate checkpoints** (`save_period=5`: `epoch0,5,…,95`, **20 files**; **3,854**
`epoch*.pt`). Our first version sampled every fourth checkpoint (**41 runs × {0, 20, 40, 60, 80} = 202 evaluations, 0 failures**); the shared protocol (Supplementary S6) asks for the whole curve, so we then evaluated **all 806 retained checkpoints of the same 41 runs on the disjoint `test` split, 0 failures**. **The 202 shared (run, epoch) points agree to 0.0000 pp** — the same checkpoints evaluated twice, independently, on one machine and protocol: a free reproducibility check of the endpoint rule itself.

**One metric self-correction first.** Our first version used `r(e) = ΔT(e)/ΔV(e)`, producing values such as
**−860 % and +1031 %**: at late epochs `V(e) ≈ V(final)`, so the **denominator vanishes** —
**an ill-conditioned metric, not a finding.** We report only the non-dividing quantities
`ΔV(e) = V(e) − V(final)`, `ΔT(e) = T(e) − T(final)`, summarized by the slope κ of ΔT on ΔV
**through the origin**.

> **Tables S21–S23** → Supplementary §S8.


**Slope κ** (how much of the movement on `val` transfers to `test`). On the **complete curve** —
**n = 765 (seed, epoch) points over the 41 runs** — **κ = 0.708, R² 0.937**, with a run-clustered
95 % CI **[0.671, 0.745]** (sandwich SE 0.018, matched by a run-level bootstrap [0.672, 0.744]);
the within-run estimator, which removes run-level differences entirely, gives **0.698**. The
five-epoch sample gave **0.734** (not the independent unit — the epochs within a run are not), so
**the completed sweep moves the estimate by −0.026 with overlapping intervals: the conclusion is
unchanged, and we now quote the complete-curve value as primary.** The interval sits well inside
(0.5, 1.0), so the transfer rate is an estimate with a known width rather than a bare point value. Scripts:
`work/x2_kappa_clustered_20260918.py` (reproduces the published 0.734 / 0.902 / n = 161 exactly
before adding the interval) and `work/x3b_perepoch_corrected_20260918.py` (complete curve). **The key point: κ is not a constant, and §8.6's 19 % does not contradict 0.734 — the two cover different
regions of the curve** (§13 puts both in one model: the realization rate is 1 − WC/premium).

- Across the curve (especially early) the movement is large — `ΔV` reaches **−8.1 pp** — and about **73 %**
  transfers to `test`: **early-training progress is real progress.** §8.6's 19 % measures the
  **selection-relevant sliver** near the peak, where `ΔV` is of order **±0.2 pp** and `ΔT` is
  **directionless noise** (negative for the smoke2sf strategy arm).
- **Both are therefore true**: "most of the movement on `val` transfers"
  (κ = 0.734) **and** "the little extra gained by selecting near the peak does not" (19 %) — the
  **selection premium is the residual of the transfer rate**.
- **And κ is not constant across arms either — in the direction the selection account predicts.**
  On the complete curve, **baseline κ = 0.600** (95 % CI [0.581, 0.619], R² 0.946) and
  **strategy κ = 0.767** ([0.735, 0.800], R² 0.951); resampling runs *within* each arm (never pooling
  the two sets) puts the difference at **+0.168, 95 % CI [+0.130, +0.203]** (the five-epoch sample:
  0.532 / 0.769 and **+0.237, [0.145, 0.323]**). **The arm that gains more from selecting on `val`
  (§5 Tier 1: the baseline arm) is the arm whose movement transfers less to `test`** — what a
  selection account requires, and an independent corroboration on data that already existed.
  **The completed curve narrows the arm difference by a third but keeps its sign and its interval
  away from zero**: smaller than the sampled grid suggested, not larger.

**A second result — and a self-correction the complete curve forces.** With four sampled epochs we
wrote that **"the sign of Δgap does not flip anywhere on the curve"**, and read it as non-*p*-value
support for §5.1 Tier 2. **On the complete curve that sentence is too strong for one of the two
cells, and we narrow it:** from epoch 20 onward Δgap is positive at every checkpoint in both cells,
and in `smoke2sf` it is negative over the first three — the grid's apparent uniformity was partly an
artefact of where it sampled. The per-checkpoint values, the epochs that flip, and the check that
reproduces the published values to the printed digit are in **Supplementary S11**.

**Three limitations**: ① only the two headline cells reach n = 10; `aitod20` has a single run (30 epochs
only, so it contributes 6 checkpoints where the others contribute 20 — hence 806, not 820); ② **closed: every retained checkpoint is now evaluated**, and the *stability* reading is narrower
than the sampled grid suggested, as stated above; ③ κ is relative to each run's own final epoch and is **not** causal.
The complete 806-row evaluation is archived locally as `xeval_perepoch_20260918/matrix_perepoch.csv`
with a SHA-256 list, verified against the pod copy after transfer.

---

## 9. Finding 6: the registered replication — hypothesis stated, criterion not met

**What was registered** (frozen 2026-09-13 01:37:27 UTC, **zero runs existing at freeze
time**, FROZEN-HASH md5 `6a7eee7b3e34b15ce5adcba14cf7ea36`). **H1**: on **three unsaturated target
domains** (100-epoch baseline mAP50-95 < 0.30), raising the peak learning rate from **0.001 to
0.005** during a 20 %-budget fine-tune (YOLOv12n [11] + shapeiou) yields a **positive** gain
resolvable by **ten-seed paired testing**. **"Replication succeeded"** required **≥ 2/3 pairs**
satisfying {gain ≥ **+0.30 pp**, paired p < **0.01**, **≥ 8 of 10 seeds** same direction} and
surviving **BH (q = 0.05)**; **otherwise report it as not replicated** [28]. **H2** (moderator): on
a **saturated** domain the same strategy's gain should be **≈ 0**. The **ring** design over
three aerial corpora makes source and target roles differ in every pair; **70 runs** were frozen (three
pairs × 2 arms × 10 seeds = 60, plus a saturated control of 2 × 5 = 10), and the near-matched
**control C** was appended by amendment and later extended to ten seeds — **2 × 10 = 20 further
runs** — for **90 runs in total** (70 registered + 20 appended); the count is taken from the run
directories themselves, ten seeds per arm in every cell except the saturated control, which has five.


**How the ten seeds are realized** (stated because the run metadata is misleading): the seed is
carried by the **shuffle order of the training files**, not by the framework's `seed` argument, so
every run's `args.yaml` records the framework default **`seed: 42`** — expected, and **not** a sign
that the seeds coincide. What is verified: the per-seed `results.csv` are **distinct in every cell**
(20/20 runs in each registered pair, 10/10 in the saturated control, 20/20 for the appended
control), re-running one shuffle seed reproduces its run, and the same holds for the cells escalated
in §5.1. The mechanism, the framework version and the args.yaml detail are in **Supplementary S12**
(script `work/check_seed_convention_20260918.py`).

**Result, at n = 10 per pair.** **T1-a** (dota15→aitod) **+0.147 pp** (CI [−0.036, +0.330], t = 1.816,
p = 0.1027, **6+/4−**) — **fails**. **T1-b** (aitod→visdrone) **+0.168 pp** (CI [+0.083,
+0.253], t = 4.455, p = 0.0016, **10+/0−**, permutation p = **0.001953**, the n = 10 floor) —
passes direction and significance, **fails the +0.30 pp magnitude criterion**. **T1-c**
(visdrone→dota15) **+3.727 pp** (CI [+3.534, +3.920], t = 43.774, p = 8.5×10⁻¹², **10+/0−**,
permutation p = **0.001953**) — **the only pair passing all three parts**. **Significant after BH
(q = 0.05, m = 3): 2/3** (2.5×10⁻¹¹ and 0.0024 survive; T1-a's 0.1027 does not).
**Passing the full registered criterion is a different count: 1/3**, because T1-b fails the
magnitude part while passing significance. **→ H1: not replicated** (1/3 by the unit criterion, 2/3
after BH). We write "**criterion not met**", **not "hypothesis refuted"**: T1-b is 10/10 in the same
direction with its permutation p already at the attainable floor, yet its magnitude falls short —
**direction stable, magnitude insufficient**, and that tension is itself the result.

**The saturated control** falls into **none of the frozen document's literal cases** (the registration
requires recording such a case for human adjudication; we mark it a deviation): not "≈ 0 and
non-significant" and not a positive gain, but **significantly negative** (−1.490 pp, p = 0.0141).

**The appended control C** (dota → dota15, class sets differing by one container-crane class)
asks whether the gain depends on a label-space change: at n = 10, **+0.727 pp** (CI [+0.640,
+0.814], t = 18.854, p = 1.53×10⁻⁸, **10+/0−**). Its three-seed predecessor was +0.707 (p = 0.0157),
**short of the threshold** — at n = 3 the permutation floor is **0.25**, so it cannot reject there in
principle; only ten seeds turn it into a verdict. Its YAML shares a directory between `val`
and `test` and uses the project's reporting convention, the best endpoint — §10.

**How much of these Δs is the alias itself — val side.** In the four cells whose config points
`val:` and `test:` at one directory, the metric watched during training **is** the reported
metric, so each run's own log measures the selection premium directly:
`p = max_e mAP50-95(e) − mAP50-95(final epoch)`. Paired across seeds within a cell,
`d̄ = mean[p_baseline − p_strategy]` is the part of that cell's Δ that is **differential
selection opportunity** rather than the intervention, so `Δ ≈ Δ_reported + d̄`.
The per-cell values of that term, with their intervals, are in **Supplementary S12** (audit script `work/x10_alias_audit_20260918.py`). In the same terms: T1-a **+0.198 pp**, T1-c **+3.941 pp**, control C **+1.133 pp**; T1-b is excluded by construction, since its YAML separates
the two keys, so its training-time metric is not the reported one and a val-side term cannot
bound a two-term bias. **No verdict changes; one magnitude does**, and we state the smaller
number rather than leave the more striking one standing.

### 9.4 What this section has to do with the paper's subject

**Four of the experiment's five cells rest on the `val`/`test` coincidence identified in §4** (three
registered pairs, the registered saturated control, the cell appended by amendment), so
**this verdict cannot be presented as a clean-protocol result**: it was obtained **under the protocol
in force at registration time**, and §8's remediation ran on a **different batch of runs**. **One coincidence, stated without inferring
causation**: the only cell with a separated split (T1-b) is the one whose magnitude falls short
(+0.168 < +0.30, despite 10/10 in the same direction), while the passing cell (T1-c) and the
significantly negative saturated control **are both on same-directory YAMLs**; with five
cells we **infer no mechanism**, yet it is an instance of "the reported split is not independent"
**landing on a concrete conclusion**. The registration and the later clean-protocol rerun
(`r10_p_*`, 3 seeds) **agree in sign everywhere** (+3.61/+3.75/+3.38 versus
+3.74/+3.60/+3.80 on the largest cell) but are **not the same batch and must not be pooled
or averaged**; the frozen registration, per-pair tables, outcome-blind displacement measure
(including the published MAFA→mask = 7.1894) and verdict scripts are in
**Supplementary S24–S27**.

## 10. Our own defects (disclosed, not hidden)

| # | Defect | Handling |
|---|---|---|
| 1 | The clean-protocol results document **cites a ledger file that does not exist in the sense claimed, and the problem is worse than a wrong filename**: neither the cited `_r10_final_stats.txt` nor the file later identified as the "real log" (`_r10_stats_0403.txt`) contains **any** of that document's headline values (6 probes each, **0/6 hits**) ⇒ **these numbers have no surviving stdout ledger** | **We do not point at a replacement file** (renaming would only manufacture a new false citation). Text citing those numbers notes **"no stdout ledger"**; the p-values can be recomputed from the local `pvalue_table_local.py` |
| 2 | ~~the dota15 cell of `selection_premium.py` was not reproducible~~ → **fixed** (the root directory was a stale snapshot, and the matcher used `prefix + '_s'` while the actual run names carry no seed suffix); after the fix it **reproduces M3's +1.12/+0.95/+0.93 value by value** | Stated in §5.3; **and it exposed a new disclosure**: M3 wrote "3 seeds" while only **2** runs carry a seed identity |
| 3 | **`sio_b_results.csv` has no written endpoint convention** — `t2_mask2mende_base100_s42n` is recorded as final (67.12) in one archive and best (70.06) in another, i.e. "which checkpoint is recorded" was never specified | Stated in §7.3 with the consequences of each reading (significant versus not) |
| 4 | The two headline scripts **originally depended on a rented pod** (`import paramiko` plus a plaintext password) — a paper about evaluation validity whose own analysis is not reproducible from the release | **Fixed**: `selection_premium_local_20260916.txt` and `r10_pvalue_table_20260916_local.md` now **read the local archive**; the main text uses the local versions and lists the pod versions as cross-checks |
| 5 | **No script computes the σ decomposition** (the three components come from three unrelated scripts); **no frozen effect-size rule file**; **no script generates `benchmark_split_audit.md`** (hand-written, 28 judgments as literals) | Each is labelled "manual / not archived", or a script is added |
| 6 | The local archive **has no copy of the three-way carve directories**, and no copy of 6 of the 7 corpora | **Partially repaired (2026-09-16, GPU run)**: the per-epoch curves of the 41 three-way runs, `sio_b_results.csv`, and the **2 × 2 evaluation matrix** (164 evaluations) are now local with a SHA-256 list (`xeval_20260916/`), so **§8's readings and §5.6's decomposition are locally recomputable**; **what remains non-recomputable is retraining**, which needs the corpora themselves |
| 7 | The audit document has **internal inconsistencies** (nine items, found by our own census of it) | Each adjudicated in `审计文档更正与裁定_20260916.md`: **3 turned out to be misreadings by the inventory, 4 are real defects, 1 is a convention risk** |
| 8 | Our own corpora contain `val == test` | **That is this paper's argument**, not an embarrassment to be hidden |
| 9 | **Our first per-epoch report claimed curve-wide stability from a four-point sample**, and reading the complete curve overturned it for one of the two cells (§8.7) | **Corrected in place, with the retracted sentence quoted**: the complete sweep shows `smoke2sf`'s Δgap negative at epochs 5/10/15 and positive from epoch 20 on, so the claim is **narrowed** rather than deleted, and the sampled grid's apparent uniformity is named as partly an artefact of where it sampled |

*(The Chinese draft numbers these rows 1–3, 3, 4–7 with a duplicate "3"; renumbered here without
changing content.)*

---

## 11. Recommendations

1. **Check the three keys before reporting**: do `val` and `test` point to the same directory or file list?
   **At the tool level**, make "are `val` and `test` the same source?" a **hard pipeline check** —
   §4.2: a tool produces this failure, a tool can block it.
2. **If you must select on the reported split**: say so ("the reported value is a **selected**
   value") and **report a selection-free endpoint alongside it** (the final epoch, or the mean of the last
   few). §5.1 shows this step **enlarges** the arm difference.
3. **Report the test convention**: below n = 6 a permutation test has no resolution; at n = 3 significance
   comes from the paired t-test alone.
4. **Declare the unit**: any "how many benchmarks have a problem" number must state whether it is
   release / protocol / yolo_dist / reported.
5. **Select a plateau, not the single peak**, when you must select on the reported split: on 40 paired
   runs the `val` argmax captured **30 %** of the realizable gain and the best five `val` epochs captured
   **70 %** — at the cost of reporting a number **0.73 pp** below the peak, which is exactly the part of
   that peak that belongs to the split rather than to the model.

---

## 12. Limitations

- The audit reads **split definitions** (YAML, README, paper text), **no datasets downloaded**.
- For several benchmarks the "generic YOLO copy" is a **per-project** config, not a canonical artifact.
- Under the `reported` unit, **4 rows (AI-TOD, DIOR, Mendeley, D-Fire) are evidence-insufficient**; we do
  not guess.
- Two evidentiary differences (pod versus local) are listed side by side, neither hidden.
- The census is a **literature/release survey**, weaker evidence than the **self-measurement** on our own
  corpora (§3).
- The selection-premium decomposition (§5.6) covers **2 of 13 cells**; the other cells' runs are not on the
  machine used — a scope we state rather than extrapolate.

---

## References

[1] R. Reveles-Martínez, S. Burciaga-Sosa, J.M. Celaya-Padilla, S. Castro-Tapia, H. Luna-García, H. Morales-Magallanes, M.N. Regalado-Pérez, C. Landeros-Soriano, et al.. "Sequence-Aware Dataset Auditing for Leakage-Free Benchmarking of YOLO Detectors for Bottle Detection." *Technologies* 14(9):531 (2026).

[2] W. Ruangsang, P. Pramkeaw. "Cross-Dataset Evaluation of YOLOv8 for Unmanned Aerial Vehicle Fire and Smoke Detection: Benchmark Contamination, Zero-Shot Transfer, and Onboard Deployment on a Low-Cost Airframe." *Drones* 10(8):635 (2026).

[3] B. Barz, J. Denzler. "Do We Train on Test Data? Purging CIFAR of Near-Duplicates." *Journal of Imaging* 6(6):41 (2020).

[4] roboflow/rf-detr. pull request #1329: "fix(training): evaluate the real test split for YOLO datasets" (2026). https://github.com/roboflow/rf-detr/pull/1329

[5] ultralytics/ultralytics. issue #25650: "Fix the KITTI Eigen test split: 3 test drives were in train" (2026). https://github.com/ultralytics/ultralytics/pull/25650

[6] *MMDetection* [computer software]. https://github.com/open-mmlab/mmdetection (pinned at commit `cfd5d3a985b0`, branch `main`, accessed 2026-09-16).

[7] *Detectron2* [computer software]. https://github.com/facebookresearch/detectron2 (pinned at commit `a2f4a8771ab7`, branch `main`, accessed 2026-09-16).

[8] *YOLOX* [computer software]. https://github.com/Megvii-BaseDetection/YOLOX (pinned at commit `6ddff4824372`, branch `main`, accessed 2026-09-16).

[9] *PaddleDetection* [computer software]. https://github.com/PaddlePaddle/PaddleDetection (pinned at commit `b25522a0f4bd`, branch `release/2.9`, accessed 2026-09-16).

[10] *DETR* [computer software]. https://github.com/facebookresearch/detr (pinned at commit `29901c51d7fe`, branch `main`, accessed 2026-09-16).

[11] Y. Tian, Q. Ye, D. Doermann. "YOLOv12: attention-centric real-time object detectors." arXiv:2502.12524 (2025).

[12] G. Jocher, A. Chaurasia, J. Qiu. *Ultralytics YOLO* (v8.4.120) [computer software] (2023). https://github.com/ultralytics/ultralytics (accessed 2026-09-12). [verified: software release tagged v8.4.120 as used in this study]

[13] M. Everingham, L. Van Gool, C.K.I. Williams, J. Winn, A. Zisserman. "The Pascal Visual Object Classes (VOC) Challenge." *International Journal of Computer Vision* 88(2):303-338 (2009).

[14] S. Shao, Z. Li, T. Zhang, C. Peng, G. Yu, X. Zhang, J. Li, J. Sun. "Objects365: A Large-Scale, High-Quality Dataset for Object Detection." *2019 IEEE/CVF International Conference on Computer Vision (ICCV)* 8429-8438 (2019).

[15] A. Kuznetsova, H. Rom, N. Alldrin, J. Uijlings, I. Krasin, J. Pont-Tuset, S. Kamali, S. Popov, et al.. "The Open Images Dataset V4." *International Journal of Computer Vision* 128(7):1956-1981 (2020).

[16] G. Cheng, J. Han, P. Zhou, L. Guo. "Multi-class geospatial object detection and geographic image classification based on collection of part detectors." *ISPRS Journal of Photogrammetry and Remote Sensing* 98:119-132 (2014).

[17] S. Yang, P. Luo, C.C. Loy, X. Tang. "WIDER FACE: A Face Detection Benchmark." *2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)* 5525-5533 (2016).

[18] Tsung-Yi Lin, Michael Maire, Serge Belongie, Lubomir Bourdev, Ross Girshick, James Hays, Pietro Perona, Deva Ramanan, C. Lawrence Zitnick, Piotr Dollár. "Microsoft COCO: Common Objects in Context." arXiv:1405.0312 (2014). DOI 10.48550/arXiv.1405.0312

[19] Darius Lam, Richard Kuzma, Kevin McGee, Samuel Dooley, Michael Laielli, Matthew Klaric, Yaroslav Bulatov, Brendan McCord. "xView: Objects in Context in Overhead Imagery." arXiv:1802.07856 (2018). DOI 10.48550/arXiv.1802.07856

[20] Shuai Shao, Zijian Zhao, Boxun Li, Tete Xiao, Gang Yu, Xiangyu Zhang, Jian Sun. "CrowdHuman: A Benchmark for Detecting Human in a Crowd." arXiv:1805.00123 (2018). DOI 10.48550/arXiv.1805.00123

[21] Ke Li, Gang Wan, Gong Cheng, Liqiu Meng, Junwei Han. "Object Detection in Optical Remote Sensing Images: A Survey and A New Benchmark." arXiv:1909.00133 (2019). DOI 10.48550/arXiv.1909.00133 (DIOR benchmark)

[22] G.-S. Xia, X. Bai, J. Ding, et al. "DOTA: a large-scale dataset for object detection in aerial images." *CVPR* 2018, pp. 3974-3983. DOI 10.1109/CVPR.2018.00418.

[23] P. Zhu, L. Wen, D. Du, et al. "Detection and tracking meet drones challenge." *IEEE TPAMI* 44(11):7380-7399 (2022). DOI 10.1109/TPAMI.2021.3119563. (VisDrone.)

[24] S. Ge, J. Li, et al. "Detecting masked faces in the wild with LLE-CNNs." *CVPR* 2017, pp. 426-434. DOI 10.1109/CVPR.2017.53. (Cited only to delimit the MAFA packaging difference.)

[25] Xu et al. "Detection of safety helmet wearing based on improved SSD." *Journal of Physics: Conference Series* (2019). Dataset: https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset

[26] Fusheng Yu, Jiang Li, Xiaoping Wang, Shaojin Wu, Junjie Zhang, Zhigang Zeng. "Large, Complex, and Realistic Safety Clothing and Helmet Detection: Dataset and Method." arXiv:2306.02098 (2023); journal version in *IEEE Transactions on Instrumentation and Measurement* (2024). DOI 10.48550/arXiv.2306.02098 (SFCHD / SFCHD-SCALE)

[27] Mendeley Data records, "Face Mask Detection" (data records, no venue). Widely used 853-image PASCAL-VOC variant: https://www.kaggle.com/datasets/andrewmvd/face-mask-detection

[28] Y. Benjamini, Y. Hochberg. "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." *Journal of the Royal Statistical Society Series B: Statistical Methodology* 57(1):289-300 (1995).

[29] B.L. Welch. "The Generalization of `Student's' Problem when Several Different Population Variances are Involved." *Biometrika* 34(1/2):28 (1947).

[30] Y.K. Adimoolam, C. Poullis, M. Averkiou. "Data Leakage Detection and De-duplication in Large Scale Geospatial Image Datasets." *CVPR* 2026 (Oral). https://openaccess.thecvf.com/content/CVPR2026/html/Adimoolam_Data_Leakage_Detection_and_De-duplication_in_Large_Scale_Geospatial_Image_CVPR_2026_paper.html

[31] J. Wang, W. Yang, H. Guo, R. Zhang, G.S. Xia. "Tiny Object Detection in Aerial Images." *2020 25th International Conference on Pattern Recognition (ICPR)* 3791-3798 (2021). DOI 10.1109/icpr48806.2021.9413340

[32] D. Du, Y. Qi, H. Yu, Y. Yang, K. Duan, G. Li, W. Zhang, Q. Huang, et al.. "The Unmanned Aerial Vehicle Benchmark: Object Detection and Tracking." *Lecture Notes in Computer Science* 375-391 (2018). DOI 10.1007/978-3-030-01249-6_23

[33] P.V.A.B. de Venâncio, A.C. Lisboa, A.V. Barbosa. "An automatic fire detection system based on deep convolutional neural networks for low-power, resource-constrained devices." *Neural Computing and Applications* 34(18):15349-15368 (2022). DOI 10.1007/s00521-022-07467-z

[34] S. Kapoor, A. Narayanan. "Leakage and the reproducibility crisis in machine-learning-based science." *Patterns* 4(9):100804 (2023). DOI 10.1016/j.patter.2023.100804

[35] S. Kaufman, S. Rosset, C. Perlich, O. Stitelman. "Leakage in data mining." *ACM Transactions on Knowledge Discovery from Data* 6(4):1-21 (2012). DOI 10.1145/2382577.2382579

[36] Z. Zou, K. Chen, Z. Shi, Y. Guo, J. Ye. "Object Detection in 20 Years: A Survey." *Proceedings of the IEEE* 111(3):257-276 (2023). DOI 10.1109/JPROC.2023.3238524

[37] J. Dodge, G. Ilharco, R. Schwartz, A. Farhadi, H. Hajishirzi, N. Smith. "Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping." arXiv:2002.06305 (2020). DOI 10.48550/arXiv.2002.06305

[38] X. Bouthillier, P. Delaunay, M. Bronzi, A. Trofimov, B. Nichyporuk, J. Szeto, N. Sepah, E. Raff, et al. "Accounting for Variance in Machine Learning Benchmarks." arXiv:2103.03098 (2021). DOI 10.48550/arXiv.2103.03098

[39] L. Cascone, M. Nappi, C. Pero, X. Wang. "A framework for bias-aware dataset evaluation in soft facial attribute recognition." *Pattern Recognition* 172:112416 (2026). DOI 10.1016/j.patcog.2025.112416

[40] Y. Huang, Z. Zhang, Y. Huang, Q. Wu, H. Huang, Y. Zhong, L. Wang. "Customized meta-dataset for automatic classifier accuracy evaluation." *Pattern Recognition* 146:110026 (2024). DOI 10.1016/j.patcog.2023.110026

[41] G.C. Cawley, N.L.C. Talbot. "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation." *Journal of Machine Learning Research* 11(70):2079–2107 (2010).

[42] S. Varma, R. Simon. "Bias in error estimation when using cross-validation for model selection." *BMC Bioinformatics* 7:91 (2006). DOI 10.1186/1471-2105-7-91

[43] B. Recht, R. Roelofs, L. Schmidt, V. Shankar. "Do ImageNet Classifiers Generalize to ImageNet?" *Proceedings of the 36th International Conference on Machine Learning* (ICML), PMLR 97:5389–5400 (2019).

[44] K. Gorman, S. Bedrick. "We Need to Talk about Standard Splits." *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics* (ACL):2786–2791 (2019). DOI 10.18653/v1/P19-1267

## Figure and table inventory

**Where the evidence lives.** This article keeps its **claims, argument, four headline tables and its
disclosure**; the remaining tables and all six figures are in the Supplementary Material, reproduced
**unchanged**, every number here still backed by an artifact pointer. Four tables are printed **here**
too, because each carries a headline number to check:

| In this article | §S8 counterpart | What it settles |
|---|---|---|
| **Table 1** | Table S4 | **Tier 1** — the premium per arm and the paired arm difference, with t, p and 95 % CI |
| **Table 2** | Table S6 | **Tier 2** — the paired difference Δgap by corpus, with the reading it supports |
| **Table 3** | Table S11 | the four counting units over the 19 audited benchmarks |
| **Table 4** | Table S20 | the premium selected on `val` versus what that same selection realizes on the disjoint `test` split |

**The rest are in §S8 and §S9**, keyed to their main-text sections: **Table S1** (§2.1); **Tables
S2–S3, S5, S7–S10** (§3, §5, §5.1, §5.5, §5.6); **Tables S12–S19** (§6.1–§6.5, §7.2, §7.3);
**Tables S21–S27** (§8.7, §9); the six figures:

| Figure | Main-text section |
|---|---|
| **Fig. S1** | §5.6 |
| **Fig. S2** | §8.6 |
| **Fig. S3** | §6.1 |
| **Fig. S4** | §5.5 |
| **Fig. S5** | §8.7 |
| **Fig. S6** | §13 |

§10's defect table is **kept in this article**, deliberately: disclosure belongs in the article. The
Supplementary's own §0 lists how it is generated and verified, and its §S6 records the **shared process
protocols** — the same set of protocols is used by this paper and its companion study — with their file
hashes. Disclosure-type content — first-report attribution, methodological premises, gaps — stays **in the
article**, per the venue's page convention.

---

## 13. Formalisation: what the four quantities are, and what they can and cannot identify

Sections 5–9 measure four quantities — the selection premium, the paired difference Δgap, the
transfer slope κ, and the realization rate. This section puts them in **one model** and states what
each can and cannot identify. Proofs are in **Supplementary S11**; every proposition is anchored to
numbers already measured in this paper.

**Setup.** Training is a randomised map (seed ω, recipe θ, checkpoint e) ↦ weights; evaluation is a
fixed functional M_S(W) on a labelled split S; write V(e) = M_{S_val}(W(e)) and T(e) = M_{S_test}(W(e)),
with ê = argmax_e V(e) and e_f the final checkpoint.

**Proposition 1 (the raw gap is not identifiable).** V(ê) − T(ê) = [V(e_f) − T(e_f)] +
[(V(ê) − V(e_f)) − (T(ê) − T(e_f))], i.e. **G = δ + o** with δ a split-difficulty term and o a
selection-optimism term. For any δ′ the pair (δ′, G − δ′) fits the observation equally well, so no
endpoint-pair estimator separates them [47, 48]. **The pairing assumption is what makes Δgap meaningful**:
with matched seeds and one split pair, E[δ_base − δ_strat] = 0, and only then does the arm difference
identify the difference in selection optimism. Under an aliasing configuration that assumption
*fails by construction* — the two arms' δ are two maxima on the same split — which is why §9 cannot
be read as a clean-protocol result.

**Proposition 2 (exact three-component identity).** Differencing Proposition 1 across arms gives
**Δgap = Δδ_f + Δprem_val − Δprem_test**: the final-epoch arm difference on `val`, plus the two arms'
selection gains, minus their final-epoch arm difference on `test`. This is an identity, not a fit, and
it holds value by value on all 13 scanned cells and on both escalated cells at n = 10 (§5.6).

**Proposition 3 (the sign of Δgap does not identify a mechanism).** Three measured facts carry this:
the components are of the same order (medians **1.07 / 0.54 / 0.93 pp**), so which one dominates
differs by corpus; **both signs occur** in the scanned cells (per-cell table: Table 2, Supplementary S6); every candidate mechanism we could
state is refuted by a
**sign mismatch** (M1/M2/M4/M5, Table S9). **What we do not claim** is that the sign is *fragile*: a perturbation analysis (numbers in **Supplementary S11**) leaves it stable under a ±10 % change of a single arm-difference term, so the honest statement is "the dominant term varies by corpus and the sign is a sum of same-order terms", not "the sign is noise".

**Proposition 4 (the realization rate is one minus the winner's-curse share).** With V(e) = v(e) + ε_e
and T(e) = v(e) + τ + η_e, **E[premium_test] = E[premium_val] − WC** where **WC := E[ε_ê − ε_e_f] ≥ 0**,
so the realization rate is **1 − WC / E[premium_val] ≤ 1**, with equality only if selection is driven
by signal alone [45, 46]. The inequality needs only that ê is chosen on `val` (which is the convention under
audit); the identity additionally needs the `test` noise not to enter the selection. **Two consequences, both tested on the archive** — the per-run inequality and the monotonicity in the `val` noise; per-run values, terciles and rank correlation: **Supplementary S11**. This is why §8.6's 19 % and §8.7's per-cell variation are the
same statement at different noise levels, not a contradiction. A third form — that the premium scales as σ√(2 ln E) — was **tested and withdrawn**; the regression and its diagnostic are in **Supplementary S11**.

**Proposition 5 (Benjamini–Hochberg depends on the declared family).** The step-up thresholds are
i/m·q, so adding hypotheses with smaller p-values **raises** the thresholds behind them and the
rejection count is not monotone in the family. We are ourselves an instance: escalating two cells to
n = 10 changed the 13-cell count from **0 to 3** surviving cells (§5.1) [49, 50]. Declaring the counting unit
and the comparison family is therefore not a stylistic preference but a condition for the number to
mean anything.
**Corollary (the premium is mostly shape, and the peak is the worst place to stand).** With the
notation of Proposition 4, `premium_r = shape(E) + ν_r` holds **exactly**, where `shape(E)` is the gap
between the mean curve's peak and its final epoch. Measured over 40 runs at E = 50/100/200/400, `shape` is
**71 %/91 %/88 %/9 %** of the premium. The four-budget series is **not monotone**: the premium peaks at E = 200
(+0.971 pp) and **falls** at E = 400 (+0.907 pp), so the pre-declared monotone-rise criterion is **not
met**; and premium(400)/premium(100) = **1.329** lies **inside** the pre-declared band [0.86, 1.43]
around the σ√(2 ln E) prediction 1.141, so that scaling is **not rejected** — reading the level as
shape-driven rather than jitter-driven is therefore a *candidate*, not a result. **The four early-stopped runs decide the outcome** — one restriction (dropping them) flips both
criteria — and the clean test, the same budgets with early stopping disabled, was not run; we report
the pre-declared verdict as **not met / scaling not rejected**, with this dependence stated rather
than resolved. The per-budget detail is in **Supplementary S11**. Two consequences follow. (i) A low realization rate is expected: most of the `val` premium is
the split's own shape, not transferable gain. (ii) The `val` **argmax is a poor checkpoint to carry
over**, and the reason is stated as a candidate rather than a claim: the measured test for it is in
**Supplementary S11**. On 40 paired runs (selection on `val`, readout on a
disjoint split) the argmax captured **30 %** of the realizable gain and the two peaks agreed in only
**17.5 %** of runs, whereas **averaging the best five `val` epochs captured 70 %**. Derivations and
the full tables are in **Supplementary S11**.



### 13.1 Five tests on GPU machines, each with its criterion written down first

The propositions above are testable, so we ran them on rented GPUs with the **criterion fixed before the
runs**. Two of the five outcomes are negative and one design had to be redone — reported as they came out.


The six experiments, their **pre-declared criteria** and how each came out are tabulated in
**Supplementary S31–S33**: G1 **void** (the two splits differ by 14.7 pp in difficulty on the same
checkpoints, so its −0.582 pp mixes the effect with a level effect); G1″ **met**; G1′ **not met**
(WC = **−0.069 pp**, t = −0.23, p = 0.83, n = 10 — no inflation detectable); G2 **direction met,
magnitude not met**; G3 **met**; G4 **met** (WC = **+5.21 pp**, CI [+4.82, +5.66], 20/20 runs
positive). Where the outcome is negative it is reported as negative.

The four criteria that were met and the two that were not carry one message together: **the selection
bias moves with the absolute amount of selection noise and with the number of selection opportunities,
but not with whether the two splits are the same file.** Two consequences do not follow from the numbers
alone: the configuration-level fact of §4 stands — the reported number *is* the selected number — while
the stronger reading, that aliasing *adds* a measurable amount on top of it, does not. Proposition 4's WC
is best read as the winner's-curse share of the selected gain, a quantity set by the noise. The
per-comparison reasoning and the sources are in **Supplementary S31–S33**.

---

## Declarations

- **Data availability.** All quantitative claims are backed by local artifacts listed in the Supplementary
  Material; the third-party training logs are **not redistributed** (hashes and source pointers only), and
  5 of their sources state no licence.
- **Competing interests.** None declared.
- **One quantity, two spellings.** The n = 10 attainable floor is **exactly 2/2¹⁰ = 0.001953**; the
  tables use the exact value while the abstract writes **0.0020** in the same place. Both denote the
  same floor, so any mechanical consistency check must compare **numerically** (|Δ| < 5×10⁻⁵) rather
  than as strings.
- **CRediT author statement.** *[To be completed with the final author list, using the 14 Elsevier
  roles: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation,
  Resources, Data curation, Writing – original draft, Writing – review & editing, Visualization,
  Supervision, Project administration, Funding acquisition.]*
- **Reproducibility.** Every number in this paper carries a pointer to a local artifact; 291 audit anchors
  mechanically guard the claims, and six checkers (`audit_anchors_fupaper.py`, `check_crosscite.py`,
  `verify_pulled.py`, `gap_mechanism_20260916.py`, `verify_pr_forms_20260917.py`,
  `verify_submission_pack_20260917.py`) can be run by the authors, and by any holder of the archive, against the archived artifacts.
  The archive itself is not yet deposited; until it is, these checkers are evidence about these
  results rather than an object a reader can obtain.
