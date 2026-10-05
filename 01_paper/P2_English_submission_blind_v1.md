# Configuration-level split aliasing in object-detection benchmarks: what the reported split is selected on, and how much of the selection survives an independent split


---

## Abstract

Object-detection papers report a number from a split they call held out. We audit that premise, with three results.

**1. The convention is broken in our own corpora.** **6 of 14** corpora we hold give the reported number no independent held-out split: the checkpoint was selected there.
Training and evaluation do not overlap: **checkpoint selection**, not contamination.

**2. The direction varies by corpus.** The premium is **positive in all four cells** with the baseline arm gaining more (§5.1; **near-definitional**), the **paired Δgap** changing sign by corpus (**not the selection term's sign**); a declared, **descriptive** 13-cell family leaves **3** after BH; in **12–14 of 19** benchmarks it comes from a non-independent split — **inter-coding uncertainty, not a CI** (κ **0.11–0.44**), over **configurations the archive could read, not a sample** (§6.1). **Changing the metric keeps the mean direction; one cell loses
significance and sign unanimity** (`smoke2sf` **+0.063 pp**, p = 0.54, **6+/5−**).

**3. Partial realization on a disjoint split.** Separating the selection set from the reported set, the
premium is realized only in part: the **claim-level interval includes zero** ([−17.3 %, 53.2 %], P = 0.118), so it is a **descriptive five-cell statement**, not a significant one; arm-cell median **17.6 %** (span **−28.5 % to +73.7 %**, **2/5 negative**),
run-weighted **23.3 %** (mAP50 **31.5 %**, **1/5** negative), run-level [8.4 %, 37.4 %] (P = 0.002), leave-one-out **9.77 %–34.16 %**.
Data-order replication lowers the mean **9 %–29 %** (§8); no power analysis was pre-registered, so the
nine `n = 3` cells stay descriptive.

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
10/19 (**`release` unit**: no independent held-out test), 13/19 (**`protocol` unit**: local independent testing gated), **12–14 of the 19** (**`reported` unit** — the range's **two ends are not the same instrument**: **12** is the single rater's printed coding, **14** the same rater's rows after a **model-assisted, non-blind recoding** moved two of them; per-coder κ **0.11–0.44**, weakest here, not blind humans; the reported number's split is non-independent). These are defensible answers, not the four counting units (§6.1: 10/19, 13/19, 4/19, 12/19). Declaring the unit is
therefore a methodological premise, not a caveat (§3, §6).

### 1.2 What we do not claim

We do not claim that aliasing is data contamination: the image-level intersection between the
training and held-out evaluation images is **zero** (SHWD excepted, where `train` and `val` are one
directory). We do not claim a single bias direction: our paired analysis finds **two corpora where `val`
understates and two where it overstates**, and **nine cells are not testable at n = 3** (§5.1, §7.1). Nor do we claim the
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

### 2.1 The closest work, and where this paper sits

> **Table S1** → Supplementary §S8 — verified against both 2026 studies' **full texts**, with the PDFs and extraction script archived.

None of these works is wrong — **they audit data (image identity, or the splitting unit), we audit configurations** (which path each key points to). Configuration-level aliasing shifts the
**comparison between arms**, and its direction is **not single-valued** — a **weaker** statement
than [2], whose rankings reverse across budgets on **all** of its benchmarks. Here **2 of 13
cells are underestimated on `val`, 2 overestimated and **9 are not testable at n = 3****, so no more than that is
claimed. They instantiate the taxonomy of [3], of which duplication is one mismatch [4]; binding `val:`
and `test:` to one directory creates the same mismatch **without duplicating an image**, so
de-duplication cannot find it.

**Non-collision, checked by literal search**: three exact queries return **0** hits and the channel is **metadata-only** — which establishes that these strings are unused, **not that the idea is new** (**Supplementary S12**).

**Why this is a selection question, not only a leakage question.** The bias we measure is the one the
model-selection literature has described for decades: **choosing a model by its score on a validation set
makes the reported score optimistic** [5], as does the **choice of validation criterion** — accuracy-based
early stopping being the worst rule tested [6] — and the classical remedy is to *nest* the selection
inside the evaluation, not to de-duplicate the data. In detection the selection step is implicit:
the training script writes `best.pt` by fitness and the paper reports that checkpoint, often from a single
run [7]. A reader trusting the split names therefore sees a held-out evaluation where the pipeline
performed a **maximum** — the bias the benchmark-erosion literature [8] describes, reached here with no
data reused or mis-split. We take [5] as the general statement and report the detection-specific
instantiation: **the selection premium (best − last), and how much of it transfers to a disjoint split**
(§5, §8).

**The sharpest contrast** is the two closest works: *Technologies* 2026 [9], which audits a detection
pipeline's **splitting unit** (frame versus sequence), and *Drones* 2026 [10], whose six configurations differ between `val`
and `test` by **between −0.41 and +0.49** mAP@0.5, "with no systematic direction". We measure a **different
quantity**: on three-way corpora we **measure the paired difference's sign**. We therefore do **not**
write "understated" unqualified, and state the difference from [10]: [10] **names the mechanism** — "the validation split is what early stopping and checkpoint selection saw" — but reports a raw val-minus-test
gap, mixing two splits' difficulty, **not identifiable**, whereas our **paired difference** cancels
difficulty and still shows a residual shift. Reference [11] is not competing: cited only
as evidence that the genre has a venue.

**That separation is the paper's own contribution.** The literature above measures how much of the choice
survives as a level [12]; it does not predict that in these curves the premium is **dominated by the peak's
position, not by run noise** (§8.6). Its remedies are therefore not interchangeable with ours, and **a
`val`-side difference stays uninterpretable as a generalisation difference even after selection is removed**.

### 2.2 Contributions

**What this paper reports first** (the boundary to the companion is in §2.3): the configuration-level audit
of the `val`/`test` convention and its selection premium (§4–5); and the **measured** realization of that
premium on a disjoint split with the reporting conventions it depends on (§8.6–8.7, §11, §3.1).

1. **We quantify the magnitude and direction of configuration-level aliasing.** The selection premium
   (best − last) is **positive in all four cells, the baseline arm gaining more** (**near-definitional; §5.1**; four paired 95 % CIs
   excluding zero, §5.1 Tier 1) — **consistent with the selection-bias literature** [5], not new in
   kind. **All four cells meet the stated-n criterion (n = 10–11)** and all four survive a Benjamini–Hochberg step over **these four** at q = 0.05 — the fourth, `dota15`, entered at n = 3
   and was escalated to n = 10 under a criterion fixed in advance (**Table S28's note**) — so the convention
   systematically shifts **arm-to-arm comparisons**; its direction
   varies by corpus: three-way paired differencing gives 2 cells where `val` understates, 2 where it
   overstates and 9 not testable at n = 3 — the **no-systematic-direction** [10] reports, measured here on
   detection corpora.
   **We do not claim a general understatement** (§5). It appears in third-party logs too (a searched 20-log sample; §5.5) — corroboration that the
component exists elsewhere, **not independent evidence** and not a field-level rate.
   *Note: **image-level** leakage magnitude is quantified by the two 2026 studies;
   **configuration-level** aliasing magnitude has not been measured before.*
2. **We measure how far the selection premium transfers.** The measurement is the contribution; the
   protocol that makes it readable is the companion's and is **cited, not restated** here (§8.1). On the
   five arm-cells measured here the `val`-selected premium is realized on the disjoint split at
   **23.3 %** with all five arm-cells at n = 10, and it is **not a constant**: the rate falls with the
   validation noise of the criterion used to select (§8.6–§8.7). The identity tying it to the
   winner's-curse share we **adopt** [13], not claim; the closest concurrent work [12, 14] reaches the same **direction** with a different quantity, and neither reports a **ratio of difference premiums** — `(T_best − T_final)/(V_max − V_final)`, on disjoint splits, in detection, on our own arm-cells, with measured `val` noise as moderator. A same-estimand ratio does exist elsewhere — in genomics, where it is written as a relative bias and measured at 10–60 % (**Supplementary S12** carries the full citation). The replicate axis is **data order** (§8.4) — the **seed-budget discipline
   reproduced inside this setting** rather than a new one.
3. **We disclose our own defects, and the corrections that followed** rather than removing them:
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

**The proposition is not ours to claim.** That *the same data yield different defensible audit counts under
different operational definitions* has been stated independently, for molecular benchmark auditing, in a 2026
preprint whose abstract closes "different defensible definitions return different answers from the same
file" [15]. **The observation is the cited literature's; the instantiation, and the four named units, are ours.** Our contribution is therefore **not the observation but its instantiation in detection
evaluation**: naming the four units by *who controls the split*, and backing them with the 19-row, four-unit
evidence table, and the premium on **five arm-cells**. The decomposition is orthogonal to [15], which separates leakage by **type**; we
separate the **counting subject**, so one leakage type can still be counted under four units (§6.1).

> **Table S2** → Supplementary §S8.

**The `reported` unit is read from the release documentation and from the dataset's own paper**: we did not sample papers per benchmark and make no claim about prevalence; a stated-frame sample is future work (§11). For each of 19 benchmarks we record all four units, an evidence class and a confidence level, and recompute every percentage from the row markers under a per-unit subtotal check **and one stated `n_a` rule** (**Supplementary S12**) — the full 19 × 4
table and the cross-check against the original audit are **Supplementary S1**, the derived counts §6.1 and its
table.

**The rule itself is not new.** The same toolchain's own course states it normatively — *"Test set is
touched once, at the end. Not for tuning."* and *"The splits must be independent on the dimension that
matters at deployment."* [16] — so what this paper adds is not the rule but the **audit and the count**
under it.

**The premise we rely on throughout:** a "yes" under any unit means *the reported number is not a sample from an independent split*. **What that does and does not license is stated where the counts are printed** (§6.1 and the note under its table).

### 3.1 Formalisation: what the four quantities are, and what they can and cannot identify

**Setup.** Training is a randomised map from (seed ω, recipe θ, checkpoint e) to weights, and evaluation a fixed functional on a labelled split; write V(e) and T(e) for a checkpoint’s `val` and `test` readings and ê for the `val` argmax. Sections 5–9 measure four quantities: the selection premium, Δgap, κ, the realization rate (**notation and formal statements: Supplementary S11**).

**Definition — the raw gap is not identifiable from the pair alone.** G = V(ê) − T(ê) = δ + o mixes a split-difficulty term with a selection-optimism term; the decomposition, **and the reading that a single-model endpoint pair is unable to separate its two terms, are [17]'s**, while its **strong form** — that *any* δ′ fits the observation equally well — is **stated here as a formalisation rather than attributed to that literature**. **The pairing assumption is what makes Δgap meaningful**, failing by construction under aliasing so that §9 cannot be read as a clean-protocol result; the identity holds value by value on all 13 scanned cells and both escalated cells at n = 10 (§5.6).

**Adopted identity, not a claim of this paper.** With V(e) = v(e) + ε_e and T(e) = v(e) + τ + η_e, **E[premium_test] = E[premium_val] − WC**, WC := E[ε_ê − ε_e_f] ≥ 0, so the realization rate is **1 − WC / E[premium_val] ≤ 1**, with equality only if selection is driven by signal alone [13] (**Supplementary S11** states which part of that the archive can and cannot settle) — the optimizer's curse in this paper's notation, the frame for §8.6–§8.7. **Two consequences are testable on the archive** — the per-run inequality, and monotonicity in the `val` noise (**Supplementary S11**). A third form, that the premium scales as σ√(2 ln E), was **tested and withdrawn** (**Supplementary S11**); contemporaneous work measures **≈5×** on the same σ√(2 ln K) bound [18].

**Corollary (the premium is mostly shape, and the peak is the worst place to stand).** `premium_r = shape(E) + ν_r` holds **exactly**, `shape(E)` being the mean curve's peak-to-final gap, so `shape` is a functional of the mean curve alone — **not** an independent check on σ — and `E[ν_r] ≥ 0`. On our 40-run four-budget series **the monotone criterion is met on the clean re-run** while the σ√(2 ln E) form is **outside** its pre-declared band, so that scaling **stays withdrawn**; the pre-declared shape control passes on the mean it specifies but fails per arm, and we report both readings — the with-early-stopping series carrying the pre-declared verdict — so **we do not claim an `E` effect**. The checkpoint rule is a **reporting rule** (the top-5 mean beats the argmax on the same 40 runs), with **three limits**: an empirical capture rate, a `val`-side cost the argmax does not carry, and a two-split, five-epoch-grid scope.

**What is ours, and what is not.** Of the statements that follow, the raw gap's definition [17], the impossibility result for endpoint-pair estimators [19] and the family-dependence procedure [20] are **machinery rather than results of ours**, and the identity is **adopted** from the selection-bias literature; **the corollary alone carries measurements of this paper**. Full statements and proofs are in **Supplementary S11**, and the detail displaced from here in **Supplementary S12**.

### 3.2 Six experiments, five judged criteria, on GPU machines, each with its criterion written down first

The propositions of §S11 are testable, so we ran them on rented GPUs with the **criterion fixed before the runs**; **Supplementary Table S37** gives, for each of the six experiments, the criterion it was judged against. Counts below are over **experiments**, not criteria.

**The two negative outcomes and the redone design are stated as such in Supplementary Table S37** (G1 is void; **two of the five judged experiments are negative — G1′ and G2**; the values behind every verdict are in **S31–S33**, the G1 family in **S12**; the reading below is stated more weakly in **Supplementary S11, section 13.3**).

**We then ran the clean test** of G3's epoch-budget series on **one machine with early stopping disabled**, all four budgets present: C1 is **met**, C2 falls **outside** its band, and C3 **passes** on the mean ê/E it specifies but not per arm — see §3.1 and **Table S34b**; **the pre-declared verdict stays with the with-early-stopping series**. The judged criteria carry one message: **the selection bias moves with the absolute amount of selection noise and with the number of selection opportunities, but not with whether the two splits are the same file.** Two consequences do not follow: §4's configuration-level fact stands, while the stronger reading — that aliasing *adds* a measurable amount on top — does not.

On the shared 5-epoch grid the `val` and `test` peaks agree in only **17.5 %** of runs, and conditioning on that single observable splits the 40 runs: where they agree the **median Δgap is lower** (mean **+0.13 pp**, median **−0.20 pp**, n = 7; **post-hoc**), where they differ it is **systematically not** (mean **+0.91 pp**, n = 33; permutation p = **0.009**, **post-hoc**; the median reading is **p = 0.0011**). **This is a partial predictor, not an explanation of the sign**; its limits — including the four of seven agreement runs whose gap is non-positive — and the per-run table and test are in **Supplementary S11**.

---

## 4. Finding 1: our own corpora

### 4.1 How common the aliasing is

In **our own packaged configurations** — the YAMLs we train from, a different object from a benchmark's own release — **6 of 14** give the reported number no independent held-out split: **AI-TOD, DOTA v1, DOTA v1.5, Mendeley face-mask, SFCHD** (five binding `val:` to `test:`) and **SHWD** (which binds `train` to `val`; **S1** row 13). Of the remaining 8, **4** keep the keys genuinely distinct and **4** have no `test:` key at all — the three groups account for all 14, and this is **a count over the configurations we hold, not a prevalence, nor the benchmarks' own releases** (audited separately, §6.1). Counting by file, **19 YAML files** alias the two keys, in five locations; on the archived manifest subset the ratio is **8 of 28**.

**For the corpora whose `val` and `test` are the same directory this is not contamination**: their image-level intersection with training is **exactly zero**, so the aliasing changes not *what* was evaluated but *which checkpoint* was reported, turning "selection contamination" from an ethical question into a **measurement** question. **SHWD is the exception and is not folded into that statement**: with `train` and `val` on one directory, its training and evaluation images are the same files. **It still counts among the six, for the reason the list is about: its `val` is not an independent held-out split either.**

### 4.2 The failure is produced by a tool, not by carelessness

A PASCAL VOC [21]→YOLO conversion script wrote two keys from one `images_dir`, so `train == val` appears **because the generator could not produce distinct values** (§6.1 records the same for Mendeley face-mask [22]). §10's first recommendation: make "are `val` and `test` the same source?" a **pipeline-level hard check** — human YAML review will not catch it. 

---

## 5. Finding 2: the selection premium — magnitude, direction, and mechanism

**Evidence.** `eval_validity/selection_premium_local_20260916.txt`, reading **569 archived runs** from the local archive (the local version is the 2026-09-16 repair).

**Definition.** premium = **best-epoch − final-epoch** mAP50-95 **within a single run**. When `val == test`, "best" was selected on the reported split, while `last` and `last5` are endpoints **no selection rule can reach**. This is the checkpoint-selection term of the run-to-run variation studied in [23] (early stopping, data order) and [24] (benchmark variance across seeds). Being a maximum over a noisy curve, it also carries the upward bias of any selected extreme [13]: what those works average over as uncertainty, we measure as a reproducible component. **The two arms.** Every cell is a paired comparison in which the **baseline** arm follows the published convention and the **strategy** arm is the intervention under test — in the cells reported here, raising the peak learning rate from **0.001 to 0.005** with everything else held fixed (batch 32, imgsz 640, SGD; YOLOv12n with the shape-aware IoU). The two arms run the same code and the same data.

> **Table S3** → Supplementary §S8.

### 5.1 Direction: reported in two tiers, and the second tier's sign varies by corpus

The direction claim **must be reported in two tiers**: "the convention understates the effect" is
wrong, and external checking refuted it (§5.4, II). **Endpoint convention (frozen):** `best − last`
**within a single run**, both endpoints reported for every cell; §7.2–§7.3 quantify the other
convention.

**Tier 1: the selection premium is positive in all four cells and the baseline arm gains more**,
consistent with the selection-bias literature, not new in kind; **on the monitored split that positivity is near-definitional** (`best` is that curve's own argmax), and **the finding we report is the paired arm difference and its test side (§8.6)**. Pairing brings **no** variance benefit:
the paired t of 5.74 and the unpaired Welch t [25] of **5.68** agree — at ρ = 0, **standard arithmetic
rather than an empirical finding of ours** [24]. **Permutation checks** agree with the t-tests at each cell’s attainable floor (**Supplementary S12**).

**Meta-analyses of published results have long quantified this optimism**: development-set early stopping
is measured to *overestimate realistic model performance*, by as much as **18.0 %** accuracy [26]; and a
large Kaggle meta-analysis finds *little evidence of substantial overfitting* [27] — complementary rather
than contrary, since its mechanism is holdout **reuse** and ours needs none.

**Metric sensitivity.** On `metrics/mAP50(B)` the mean direction holds in all four cells, but
`smoke2sf` loses both its significance (**+0.063 pp**, p = 0.54) and its sign unanimity (**6+/5−**, not
11+/0−): **the mean direction is metric-robust, one cell's significance and sign unanimity are not**
(full mAP50 columns and both mAP75 columns — the mAP75 `val` side is a **5-epoch grid**, so a rate computed from it is **upward-biased** — **Supplementary S12**).

**Table 1.** Tier 1 — each arm's **peak−final gap** and the **paired difference** between arms, by cell; the gap is a within-run maximum (§5.1), so the finding is the paired difference. `n` counts paired units (ten seeded, one unseeded — Supplementary S12); both differences hold at n = 10. **A different run set from the transfer measurement in §8.6**: these are the 569-run local archive under the published (aliased) protocol, while that measurement’s premiums come from the clean three-way runs — the two tables’ premiums are different quantities, not two readings of one. Source: `verify_two_critiques_20260916.txt`; the `dota15` row's n = 10 escalation is in Table S28.

| Cell | n (paired units) | peak−final gap, base | peak−final gap, strat | **paired diff** | sd | t | p | perm. *p* (floor 2/2ⁿ) | 95 % CI |
|---|---|---|---|---|---|---|---|---|---|
| smoke2sf (strong) | 11 | +0.799 | +0.382 | **+0.416** | 0.240 | 5.74 | 1.9×10⁻⁴ | 0.00098 | [+0.255, +0.578] |
| shwd2sf (corroborating) | 11 | +1.038 | +0.512 | **+0.526** | 0.207 | 8.41 | 7.6×10⁻⁶ | 0.00098 | [+0.386, +0.665] |
| a2d15 (directional probe) | 10 | +0.534 | +0.262 | **+0.272** | 0.183 | 4.69 | 1.1×10⁻³ | 0.00391 | [+0.141, +0.403] |
| dota15 (within-domain) | 10 | +0.941 | +0.492 | **+0.449** | 0.196 | 7.23 | 4.9×10⁻⁵ | 0.00195 | [+0.309, +0.589] |

**Table 2.** Tier 2 — the paired difference Δgap by corpus. Δgap > 0 means `val` understates the strategy arm’s effect. **Δgap is the split-gap arm difference** — a split-dependent arm contrast, not an isolated selection effect: it decomposes into a difficulty gap and a selection term, and **Δgap’s sign is not the selection term’s sign** — on the two headline cells the difficulty term dominates while the selection term is small or opposite-signed (**Fig. S1**). Equal split difficulty across arms is an **assumption we state**, not demonstrated here; the selection contribution proper is the **selection-action contrast** `Δprem_val − Δprem_test`. Sources: `xeval_analysis_20260916.txt` (the two `val`-understating cells) and `x1_tier*` / `teval.csv` (the two `val`-overstating cells).

| Corpus | n | Δgap (pp) | p | 95 % CI | Reading |
|---|---|---|---|---|---|
| shwd2sf | 10 | **+0.779** | 0.0053 | [+0.297, +1.261] | `val` **understates** |
| smoke2sf | 10 | **+0.461** | 0.0263 | [+0.068, +0.855] | `val` **understates** |
| p_aitovis | 10 | **−1.226** | 1.3×10⁻⁸ | [−1.370, −1.081] | `val` **overstates** |
| p_vistod15 | 10 | **−3.315** | 6.5×10⁻⁹ | [−3.676, −2.953] | `val` **overstates** |

> **The split of Δgap is recorded for two of the four cells**: difficulty **+0.759** / selection **+0.020** (`shwd2sf`), and difficulty **+1.041** / selection **−0.580** (`smoke2sf`) — in the second the selection term is **opposite in sign to Δgap**, so the sign does not carry it, and **both intervals include zero** (**Supplementary S9**, Fig. S1). The two `p_` cells' `prem_test` was **not recorded at that time**: their per-epoch `test` curves were evaluated on 2026-09-30, so nothing is imputed and the values are now recorded (**Supplementary S12**, Table S38).
>
> **The four rows below are an escalated base, not a sample**: the two `p_` cells reached n = 10 because their n = 3 Δgap had been flagged, so the 2/2 balance is a property of the escalation rule; the other nine cells are **descriptive** (**Supplementary S12**). This cell is also the one where **3 runs** changed training path silently under GPU memory pressure, and why we do not call it clean is in **§10, defect 10**.

*(Third §5 table, S5 → Supplementary §S8.)*

**Tier 2: on the same three-way corpora the paired difference Δgap varies in sign.** The raw
`M_val(ê) − M_test(ê)` is **not identifiable**; the paired difference removes the difficulty term **under the equal-difficulty assumption** (Table 2) —
**Δgap > 0 ⇒ `val` understates**. **Its effective base is four cells, not thirteen**, and an **escalated base** rather than a random sample, for the reason **Table 2's note** gives; **“2 understate / 2 overstate” is therefore a statement about these four cells, not a rate for the family**. **No prospective power analysis was registered**; the scan is in **Supplementary S12**.

**Both escalations met the criteria fixed in advance.** `dota15` **+0.449 pp** (**10+/0−**);
`p_aitovis` **−1.226 pp** and `p_vistod15` **−3.315 pp** (**0+/10−**), permutation p = **0.001953**,
the attainable floor at n = 10. The `best.pt` endpoint was identified, not assumed: on `test` it
reproduces the archived `sio_b_results.csv` to **0.0046 pp**.

**The formal claim:** the convention systematically shifts **arm-to-arm comparisons** (Tier 1: four
cells, CIs excluding zero); **the direction of that shift varies by corpus** (Tier 2: 2 understate /
2 overstate on the four-cell base) — **neither "a general understatement" nor "no systematic direction"**.
BH at q = 0.05 **now leaves three cells significant** — `p_vistod15`, `p_aitovis`, `shwd2sf` [28], **reversing what we reported before the
escalation**. **The two families are not the same test**: the **13-cell scan is descriptive**, the **confirmatory family is the four escalated cells** (declared before their runs, §3.2) — the direction statement rests on those four.

**Scope (cross-framework boundary).** The convention this paper audits belongs to the **YOLO lineage —
Ultralytics YOLO [16] and YOLOX [29]**: at pinned commits, Detectron2 (`TEST.EVAL_PERIOD = 0`) [30],
MMDetection [31], DETR [32] and PaddleDetection [33] **report the final epoch instead** (§6.5) — that
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
**The same quantity appears in other people's logs** — **a convenience sample with no sampling frame, not a field-level rate**: 20 logs from 6 sources found by repository **search**, median **+1.04 pp**, max **+5.65 pp**, 18/20 positive. The queries, the rest of the frame and the reason public logs **cannot establish aliasing** are in **Supplementary S12**.
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

**The nineteen audited benchmarks** — each read from its own release or dataset paper — are COCO [34], PASCAL VOC [21],
Objects365 [35], Open Images v7 [36], DOTA v1.0 and v2.0 [37], VisDrone-DET [38], AI-TOD [39], UAVDT [40], xView [41],
DIOR [42], NWPU VHR-10 [43], SHWD [44], SFCHD [45], MAFA [46], Mendeley face-mask [22], WIDER FACE [47], CrowdHuman [48]
and D-Fire [49]; their per-unit markings are in **Supplementary S1**. **They are the configurations this archive could
read, not a sample of the field.** The question is **evaluation validity**: dataset-level bias auditing [50]
and classifier-accuracy estimation [51] ask whether a reported number measures what it is taken to
measure, but neither audits a release's configuration binding.

### 6.1 The result under four units (single-rater judgements)

![Fig. 1](figures/fig3_four_units.png)

**Table 3.** The four counting units, with denominators named (§3). Source: `split_units_19rows_20260916.md`. **Rows marked `n_a` enter the denominator, not the numerator**; **alternative readings of the same rows** are **12/19** for `release`, **12/15** the 19 less the four **undecidable** (`n_a` is two rows), and **13/19** for `reported` under the COCO-`val` reading. **The `clean` row is a reading, not a subtraction**: the audit counted **5/19**, the non-blind second pass moved **two**, so this table reads **3/19**. **The `reported` row's two denominators**: `12–14 of the 19` over all nineteen, `12/15 = 80 %` over the fifteen that are neither `n_a` nor undecidable (**4 rows
(AI-TOD, DIOR, Mendeley, D-Fire) are evidence-insufficient**). **The range spans two readings, not an interval**, on a **single rater's** judgement (per-coder κ **0.11–0.44**, the weakest unit in the three-valued round). A **model-assisted, non-blind second coding** is **reliability evidence, not a replacement** (**Supplementary S12**).

| Unit | non-independent | of decidable rows | undecidable |
|---|---|---|---|
| **release** (the benchmark's own release) | **10/19 ≈ 53 %** | 10/19 | — |
| **protocol** (the official protocol) | **13/19 ≈ 68 %** | 13/19 | — |
| **yolo_dist** (the generic YOLO distribution package) | **4/19 ≈ 21 %** | **4/15 ≈ 27 %** | 4 rows |
| **reported** (the layer actually reported) | **12–14 of the 19 ≈ 63–74 %** | **12/15 = 80 %** | 4 rows |
| ↳ of which **literal two-key same path** (= the 2/19 the original audit reported) | **2/19 ≈ 11 %** | 2/19 | — |
| ↳ of which `reported` is **`clean`** (independent) | **3/19 ≈ 16 %** | 3/15 | 4 rows |

> **What a count here is, and what a "yes" means.** Every row is a **single rater's judgement**
> (§6.1), so the counts are printed as counts — the percentages beside them are a reading aid, not a
> rate estimated from independent coding. A "yes" under any
> unit means the reported number is **not a sample from an independent split**; it does **not** mean
> the benchmark is broken or the experiment dishonest, and it does not license a generalization claim.
**These 19 rows were coded by one rater** — 28 literal judgements (**§10**, defect 5) — with **eleven blind language-model coders** (**3**, then **8**) **across four rounds** as its only cross-check; a **non-blind, model-assisted** pass agrees at κ **0.874** (**Supplementary S12**) and **moves two rows**. `reported` means **the number the literature prints**: it is printed as a range, **12–14 of the 19 ≈ 63–74 %**, with the **80 %** column the lower end over the **12/15** decidable rows, and `n_a` rows counted in the **19** but not the numerator (**Supplementary S12**).

**Five clauses move to Supplementary S12** (the self-check's column and subtotal equalities to
**S1**): the COCO row's judged number, the `yolo_dist` first-version correction (**4/19**), the
literal-two-key self-check (**2/19**), Mendeley face-mask's **generator** provenance, and the audit's
unused "63–79 %" bound.

### 6.2 "Same directory" has four levels, and the audit reported only the narrowest
The levels, the rows each admits and the resulting shift are in **Supplementary S12**, Table S12.
### 6.3 We do **not** reproduce the original audit's two numbers, and we say why
one rests on the narrowest reading of "same directory", the other on a stale snapshot; both recomputations are in **Supplementary S12**, Table S13.
### 6.4 One judgment the evidence does not support (corrected)

**One classification correction is recorded in Supplementary S12** (D-Fire moves to the clean group).

### 6.5 Across frameworks: is the convention specific to YOLO?
**Among the pinned default configurations we checked, only the YOLO lineage does this by default.** At pinned commits Detectron2 (`TEST.EVAL_PERIOD = 0`), MMDetection, DETR and PaddleDetection **report the final epoch instead** (file-by-file evidence, 25 configuration files: **S12**, Table S14; **a targeted sample at pinned commits, not a census**, so "the convention" means that family's, not the field's). A **cross-lineage realization test** — a Faster
R-CNN (ResNet-50 FPN) detector, a family that **reports the final epoch by default** — on VisDrone under the
same three-way split, at **six seeds**, is **positive in all six runs, with a 95 % interval excluding zero** (**68.2 %** realized; **+0.0809 pp** mean `prem_val`, 95 % CI **[26.9 %, 123.5 %]**)
(values, interval and per-run table: **Supplementary S34**): the mechanism is **not confined to the YOLO lineage in this instance**. A second corpus, same protocol, same direction: **6/6** and **12/12** runs. This is **one detector, one protocol, two corpora, one setting** — **not a generalisation beyond the YOLO lineage** (**Supplementary S34c**).
## 7. Finding 4: what "significant" means, and how the endpoint convention changes it

### 7.1 With n = 3 a permutation test **cannot** reject in principle

**A power note for the cells that remain at n = 3.** Recovering each Tier-2 cell's sd from its own printed 95 % CI gives **0.20–0.67 pp**; at n = 3 the required effect is **0.65–2.19 pp** at α = 0.05, two-sided — **at or above every Tier-1 effect here** (+0.27 to +0.53 pp) — and 0.2–0.7 pp at n = 10. The nine cells at n = 3 are therefore **not testable at this design**, and are reported descriptively only. **A prefix-n table (n = 3…10) and the derivation with the non-central-`t` factor (**`3.26·sd`**) are in S12**; the permutation floor **2/2ⁿ** binds at n = 3, not the *t* test.

**For a sign-flip permutation test on n pairs the smallest attainable two-sided p is 2/2ⁿ**: at
n = 3 that is **0.25**, so such a cell has **no resolution at this n**; **after §5.1's escalations no
headline cell (Tables 1–2) is n = 3** (**the derivation and each n's floor: Supplementary S12**).

### 7.2 The two clean-protocol cells clear significance by n = 6–8
**The weaker endpoint reaches *t*-significance at n = 6 on `shwd2sf` (p = 0.0164) and n = 7 on `smoke2sf` (p = 0.0400)**; the **exact permutation — floored at 2/2ⁿ (0.25 at n = 3) — follows one to two steps behind** (n = 8 on both `selected` readings; Table S42 gives every prefix n, both endpoints). The clean-protocol seed extension that reaches n = 10, and the per-cell numbers, are in **Supplementary S12** and Table S15.
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
writing before any run**. The registration text and its **FROZEN-HASH** stamp are in **§9** and in the author-side
registration record; **Tables S24–S27** carry the registered cells' readings. What this paper measures
**under** that protocol is the quantity §3.1 formalises: **how much of the `val`-selected premium survives
on a split no selection rule can touch**, and that measurement is this paper's.

### 8.2 The protocol's results on the companion's corpora: **transferred**

The protocol's results on the companion's corpora are the companion's first report. What this paper adds under the protocol is the measurement of §8.6–§8.7; the transfer (2026-09-21) is recorded in the module-transfer note of that date.

### 8.3 A direct measurement of selection inflation
**A direct measurement of data-order replication — reproduced inside this setting**: adding replicates that permute the training file order lowers the mean by **9 %–29 %**, each figure taken **against that cell's own n = 6 mean** and not against the pooled
headline effect, the **seed-budget discipline** measured rather than assumed ([52]'s setting, §8.4). **What these replicates are, and what the bound is a bound on.** The per-run randomness the ten runs install is a **deterministic permutation of the training file order** (`--shuffle-seed`, the number in the run's own name), **not** the framework's `seed` argument (**Supplementary S12**, section 9.3, with the two corpora whose replays are identical across `--seed` values). The quantity is therefore **data-order replication**, not seed variance: the 9 %–29 % it bounds is the **file-order** component of the reported mean, and is **not** an estimate of the variance between independent training seeds. That best-of-K selection inflates a reported score is **not new** — §8.6 positions the closest concurrent work, which measures the **dose–response** over 2,047 datasets — so **what is measured here is the magnitude under a protocol that selects cells for significance first and expands seeds afterwards**; design and the check against recomputed means: **Supplementary S12**, Table S18. **The title is deliberately the weaker, sample-scoped claim**: with three initializations the interval is wide, and extending to five does not narrow it (the gain SD reaches the data-order component's order), so the components are **consistent with, not established by**, these initializations.
### 8.4 The three variance components: **the excluded one is the smaller in this sample — a sample-scoped ordering, not an established one**
**The three variance components, and the excluded one is the smaller in this sample**: the single-run data-order component is **0.515 pp**, against initialization and seed components of the same order — the **same ranking** as the shuffle-order result of [52] (**Supplementary S12**), so we **reproduce the ordering inside this setting** rather than discover it. What was held fixed, and why this is **sample-scoped** — at five initializations the gain SD moves **0.146 → 0.439 pp** and its interval **overlaps** the data-order magnitude, so the two are of the same order rather than one clearly smaller — is in **Supplementary S12** and Table S19.
### 8.5 Why "same-pipeline pairing" is a necessity, not a habit
**Pairing is not neutrality**: the paired design covers the **budget and data** axes only, and **not** the optimiser’s (why, and the counterexample: **Supplementary S12**).
### 8.6 The premium's realization rate: **not significant at claim level** (the claim-level interval includes zero); arm-cell median **17.6 %** (five arm-cells, n = 10; run-weighted **23.3 %**)

![Fig. 2](figures/fig2_realization_rate.png)

**What this section claims, and what it does not.** The rate below is the realization of the
`val`-selected premium on a disjoint split **for the five arm-cells measured here, under the
companion's protocol** — **not a constant of the convention**. The escalated cells reach a **pooled
55 %**, but the two batches are **not pooled** (different runs, different protocol, §8.1). "The
convention realizes about a quarter of the `val` premium" would be false; "in these five cells, about
a quarter survives" is what we measured.

**How much of the gain selected on `val` survives on `test`?**

**Table 4.** The premium selected on `val` versus what that same selection action realizes on the disjoint `test` split, per arm-cell (**an unbalanced pool** — two corpora contribute both arms, `aitod20` only its baseline — so the arm-cell is the unit). Source: the **per-epoch `val` curves** (`results.csv`, for `prem_val`), `xeval_20260916/matrix.csv`, and this
revision's two batches (`x4_teval.csv` on A, `x4fill_20260925.csv` on B, for `prem_test`). **The §10 memory-pressure bound (defect 10) does not arise here**: its hits are in §3.1's clean batch and §5.1's `p_vistod15`.

| Cell | Arm | n | `prem_val` | **`prem_test`** | **realization rate** |
|---|---|---|---|---|---|
| shwd2sf | baseline | 10 | +1.469 | **+0.736** | **50 %** |
| shwd2sf | strategy | 10 | +0.865 | **+0.152** | **18 %** |
| smoke2sf | baseline | 10 | +0.691 | **+0.509** | **74 %** |
| smoke2sf | strategy | 10 | +0.605 | **−0.157** | **−26 %** |
| aitod20 | baseline | **10** | **+0.766** | **−0.218** | **−28 %** |
| aitod20 | **strategy** | **10** | **+1.111** | **−0.543** | **−49 %** |

> The `aitod20` **strategy** row is in the data but outside the five-cell pool; **that pool is defined mechanically in Table S20's note** (every arm-cell whose `test` side had reached n = 10 at the 2026-09-25 freeze — 50 runs), which is why **this table prints six cells and Table S20 the five of the pool**. **The exclusion was decided after the readings were in, not by a pre-registered rule** (the only pre-registered criterion is the companion's, §9).

where `prem_val = V_max − V_final` (**selecting on val**) and
`prem_test = T_best − T_final` (**realized on test**).

**The three bases**: run-level `[8.4 %, 37.4 %]`, `P = 0.002`; five-cell `[−17.3 %, 53.2 %]`, `P = 0.118` (claim-level, **zero inside**); eleven-cluster `[19.3 %, 60.4 %]`, `P = 0.000`.

**Aggregate** (runs weighted equally, n = 50): `prem_val` **+0.879 pp** → `prem_test` **+0.205 pp**. **At the claim level this is not significant**: the **claim-level interval** is the cell-level, five-cluster one, **[−17.3 %, 53.2 %]**, **P(rate ≤ 0) = 0.118**, zero inside. Descriptively, arm-cell median **17.6 %** and run-weighted **23.3 %** (`item2_final_v2_20260925.py`; the span, **2/5** negative, is in Table 4). On a difference scale the eleven clusters give **−1.367 pp**, 95 % CI **[−1.59, −1.15]** (five-cell denominators span **+0.605 to +1.469 pp**). Re-aggregated: run-weighted **36.9 %**, arm-cell-equal **39.3 %**, 95 % CI **[19.3 %, 60.4 %]** — the interval's sign depends on the base, and **completing the cell, not the weighting, is what moves it**: at n = 10 the three weightings agree, so **the fragile axis is pool composition**. **Leave-one-out 9.77 % to 34.16 %.** In two arm-cells the selection action **costs** rather than failing to pay off (`smoke2sf` strategy, `aitod20` baseline); the escalated cells reach **82 % / 104 %** and **56 % / 29 %**, pooled **55 %** (§5.1). The closest concurrent work, the winner's-curse check, the withdrawn σ√(2 ln E) form and each cell's corpus pair: **Supplementary S12**.

(the `best.pt`-versus-argmax residual, our withdrawn attribution and why the remainder is **unidentified**: **Supplementary S12**.)

The monotonicity is a correlation, not a causal claim, and at the arm-cell unit the nine-cluster reading is ρ = **−0.433** (p = 0.244) — see **Fig. 3** and **Supplementary S12**: the n = 80 are the 81 runs with a measured
`test` side less the one whose `prem_val` is 0. It has a named precedent: [53] gives validation
overfitting (VO) its name and bounds the expected best observed loss by
E[min L] ≥ ν* − s_m√(2 log(Nq)), an optimism growing with the number of selection queries Nq.

**Recomputation status.** The readings were originally **not locally recomputable** (the archive lacks 6 of 7 corpora; **§10, defect 5**); a GPU **2 × 2 evaluation** on **41** three-way runs of **YOLOv12n [54]** × {`best`, `last`} × {`val`, `test`} makes them so, **retraining not**, reproducing the archived `best × test` values to within **0.0047 pp** (median **0.0021 pp**) — the endpoint rule's positive control (**Supplementary S12**).

**Three limitations**: ① in the **41-run epoch sweep** only the two headline cells reach n = 10; `aitod20` contributes one run of 30 epochs and 6 checkpoints where others contribute **20** (hence 806, not 820), its Table 4 arm-cell a separate n = 10 batch; ② **closed: every retained checkpoint is now evaluated**, the *stability* reading is narrower than the grid; ③ κ is relative to each run's own final epoch, not causal. The 806-row evaluation is archived (`xeval_perepoch_20260918/`, with a SHA-256 list).

![Fig. 3](figures/fig6_sigma_vs_rate.png)


**Pool composition — and why the claim does not turn on it.** Table 4 prints **six** measured arm-cells; adding the sixth (`aitod20` **strategy**) moves the run-weighted rate **23.3 % → 8.7 %** and the median **+17.6 % → −4.2 %**. That is a large move, so this is the one place where a post-hoc pool decision could have mattered — **and it does not**. The exclusion was **decided after the readings were in, not by a pre-registered rule**, but **every claim we make is interval-level and both pools give the same verdict**: five-cell **[−17.3 %, 53.2 %]** (P = 0.118) and six-cell **[−4.9 %, +21.3 %]** **both cover zero**, so **no reported conclusion depends on which cells are in the pool** — what moves is the point estimate, not the reading. Five cells are primary because they are the ones the mechanical rule admits (n = 10 on both sides at the freeze, Table S20's note); six is the sensitivity; **both intervals are printed**.

### 8.7 The per-epoch view: the realization rate is not a constant

![Fig. 4](figures/fig5_epoch_curve.png)

**One metric self-correction first.** Our first version used `r(e) = ΔT(e)/ΔV(e)`, producing values such as **−860 % and +1031 %**: at late epochs `V(e) ≈ V(final)`, the **denominator vanishing** — **an ill-conditioned metric, not a finding.** We report only the non-dividing `ΔV(e) = V(e) − V(final)` and `ΔT(e) = T(e) − T(final)`, summarized by the through-origin slope κ of ΔT on ΔV.

> **Tables S21–S23** → Supplementary §S8.

**Slope κ** (how much of the movement on `val` transfers to `test`). On the **complete curve** —
**n = 765 (seed, epoch) points over the 41 runs** — **κ = 0.708, R² 0.937**, with a run-clustered
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

---

## 9. The registered multi-target replication: **reported in the companion paper**

**First report, criterion and verdict stay with the companion paper; nothing here is a claim of this paper.** To read its registered table: ① it is a **three-way split** (train / selection / report); ② it ran under the protocol then in force, where the **`val` side aliases the `test` half** — the one fact §7 takes; ③ its criterion was frozen **before any run existed** (FROZEN-HASH `6a7eee7b3e34b15ce5adcba14cf7ea36`) and its verdict entered is **"criterion not met"**, deliberately **not** "hypothesis refuted" — the companion reads the outcome as **"direction replicates, size does not"**. Record: **Supplementary S24–S27** (source of truth: the companion's archive).

## 10. Our own defects (disclosed, not hidden)

| # | Defect | Handling |
|---|---|---|
| 1 | The clean-protocol results document **cites a ledger file that does not exist in the sense claimed**: neither `_r10_final_stats.txt` nor the "real log" `_r10_stats_0403.txt` holds **any** headline value (6 probes each, **0/6 hits**) ⇒ **no surviving stdout ledger** | **We do not point at a replacement file** (renaming would manufacture a new false citation); the text says **"no stdout ledger"**, and the p-values are recomputable from `pvalue_table_local.py`. Detail: §S12 |
| 2 | ~~the dota15 cell of `selection_premium.py` was not reproducible~~ → **fixed** (stale root directory; the matcher assumed a seed suffix the run names do not carry); it now **reproduces M3's +1.12/+0.95/+0.93 value by value** | Stated in §5.3; the "3 seeds" note was **retracted on 2026-09-21** — the third run's seed is s42, the campaign's fixed shuffle seed. Detail: §S12 |
| 3 | **`sio_b_results.csv` has no written endpoint convention**: `t2_mask2mende_base100_s42n` is recorded as final (67.12) in one archive and best (70.06) in another | Stated in §7.3, with the consequence of each reading (significant versus not) |
| 4 | The two headline scripts **originally depended on a rented pod** (`import paramiko` plus a plaintext password) — a paper about evaluation validity whose own analysis is not reproducible from the release | **Fixed**: both now **read the local archive**; the main text uses the local versions and lists the pod versions as cross-checks |
| 5 | **One script now recomputes the σ decomposition** — the data-order and initialization components from the archived per-run values, each asserted against the printed number — but it can only **cite** the augmentation component, whose record holds an SD and no per-run values; **no frozen effect-size rule file**; **no script generates `benchmark_split_audit.md`** (hand-written, 28 judgments as literals, though its counts are recomputed) | The first is closed by script, with its one cited (not recomputed) component named; the other two stay labelled "manual / not archived" |
| 6 | The local archive **has no copy of 6 of the 7 corpora**, and of the three-way carve it holds **only the manifest** (`split_defs_20260916/`), not the other carve directories | **Partially repaired (2026-09-16, GPU run)**: the 41 runs' per-epoch curves, `sio_b_results.csv` and the **2 × 2 evaluation matrix** (164 evaluations) are now local; **retraining remains non-recomputable** |
| 7 | The audit document has **internal inconsistencies** (nine items, found by our own census) | Each adjudicated: **3 misreadings by the inventory, 4 real defects, 1 convention risk, 1 classification correction (§6.4)** |
| 8 | Our own corpora contain `val == test` | **That is this paper's argument**, not an embarrassment to be hidden |
| 9 | **Our first per-epoch report claimed curve-wide stability from a four-point sample**; the complete curve overturned it for one of the two cells (§8.7) | **Corrected in place, with the retracted sentence quoted**: the claim is **narrowed**, not deleted, and the grid's apparent uniformity is named as partly an artefact of where it sampled. Detail: §S12 |
| 10 | **Memory pressure silently changes the training path**: under GPU memory pressure Ultralytics switches implementation **without changing the recorded configuration** — a batch reduction, or a fallback of label assignment to CPU that can fork the trajectory — and case (a) is **invisible in the standard artifacts**. | **Disclosed, not retracted; we do not call the affected batches “clean”.** Configuration-level hits: **2** places, **4** runs. **A reproducibility residual, not an event size**: same-config repeats are **bit-identical** (**0.000 pp**, four pairs, same machine and day), while the quantity a bound would be about — archived run against clean re-run — is **0.000 / 0.020 / 0.150 / 0.000 pp** (**Table S41**), so **≤0.05 pp** holds only inside the clean E = 50 batch and is **not extrapolated**; without a no-event control the event effect is **unidentified** (such a control is itself **not reproducible across dates**, **0.440 pp**), and elsewhere it sits inside the zero-event-control spread. The one clear case is ΔVmax **+0.769 pp**. Event counts, per-run consequences and the log fingerprints are in **Supplementary S12 (defect 10)**. |

---

## 11. Recommendations

**Four checks before reporting, each with the artifact that discharges it.** ① Are `val` and `test`
the same source? Make it a **hard pipeline check** on every dataset YAML (§4.2); the output is the
resolved paths. ② If you must select on the reported split, say so and report a selection-free endpoint
alongside — the step **enlarges** the arm difference (§5.1). ③ State the test convention: below n = 6 a
permutation test has no resolution; print the `2/2ⁿ` floor beside every p. ④ Declare the counting unit
behind every count, as Table 3's header does.

⑤ **A plateau is a post-hoc candidate, not a rule we validate.** Weight averaging is established [55];
   what is *measured here* takes the **mean of the ranked top-5 `val` epochs' readings** (a reading average, not a weight average), capturing **70 %** of the
   realizable gain against the argmax's **30 %**, at the cost of **0.73 pp** below the peak — a post-hoc
   reading of our own 40 runs, untested as an intervention. The per-rule table and the
   candidate mechanism are in **Supplementary S11**, Measurement 3.

---

## 12. Limitations

- The audit reads **split definitions** (YAML, README, paper text), **no datasets downloaded**.
- For several benchmarks the "generic YOLO copy" is **per-project**, not canonical.
- Under the `reported` unit, **4 rows (AI-TOD, DIOR, Mendeley, D-Fire) are evidence-insufficient**; we do
  not guess. Counts are **row-equal over the 19**, and the grading enters the **error bar, not the
  count** (**Table 3's second column**).
- Two evidentiary differences (pod versus local) are listed side by side.
- The census is a **literature/release survey**, weaker than our **self-measurement** (§3).
- The **difficulty/selection decomposition** (§5.6) covers **2 of the 13 cells** (the headline two); the **identity** behind it is checked on **all 13** (`work/gap_mechanism_20260916.txt`) — what is scoped is the decomposition, not the identity.
- The intervention axis the headline comparisons use is **`lr0` (`0.001 → 0.005`)**; two further orthogonal axes were run, one reproducing, as on `lr0`, the **corpus-dependent character** of the shift (**Supplementary S8**, **Table S40b**); the cross-lineage probe is
   **one detector, two corpora, and incomparable magnitudes**.
- **Four disclosed uncertainties** bound our claims: the 19-row audit is **single-rater**; the log sample is a **convenience sample**; the GPU memory-pressure effect is **bounded, not estimated** (**≤0.05 pp** where same-config pairs can be compared, fresh replicates being bit-identical; cross-date comparisons carry a **0.440 pp** drift); and the §8.3 replicates vary the **training file order**, not independent seeds. **And, not as an uncertainty**: **no interval here folds into §8.6's rate**. **Supplementary S12**.

---

## 13. Conclusions

A count is meaningless until its **unit** is named: the same nineteen benchmarks answer differently under each declared unit (Fig. 1, Table 3) — **10/19** under `release`, **13/19** under `protocol`, **4/19** under `yolo_dist`, and **12–14 of the 19** under `reported` (whose COCO-`val` reading is **13/19**). Three findings stand. **The most robust number here is the transfer slope κ (§8.7): early `val` movement does transfer to `test`, and the premium is only its residual.** The premium is positive in all four cells, the baseline arm gaining more, and the paired Δgap **varies in sign** by corpus — so "the convention understates the effect" is not claimed. On five arm-cells at n = 10 it is realized on a disjoint split at **23.3 %**, interval containing zero. Two things do **not** hold: the σ√(2 ln E) scaling was tested and **withdrawn**, and no prospective power analysis was registered, so the nine `n = 3` cells stay descriptive. What we ask of a detection paper is narrow: **name the counting unit, freeze in writing which checkpoint is the reported number, and state the interval at the level of the claim.** First report is the companion's (§7.2).

## Declarations

- **Data availability.** Claims are backed by the artifacts in the Supplementary Material; the third-party training logs are **not redistributed** (hashes and source pointers only) and 5 of their sources state no licence. The reproduction package itself — data files, per-epoch matrix, verdict files, checkers, with their SHA-256 list in `MANIFEST_sha256.csv` — is deposited and openly available at **https://github.com/YBP2005/P2.git** (accessed 2026-09-29).
- **Recomputability boundary.** Every reported number is recomputable from the released per-run artifacts **without
  retraining**, each with its script; **three are not, and they are named**: the unredistributable corpora
  (§10 defect 6), the conflicting-endpoint archives (§7.3), and the `aitod20` completion to n = 10.
- **Competing interests.** None declared.
- **One quantity, two spellings.** The n = 10 attainable floor is **exactly 2/2¹⁰ = 0.001953**; the tables
  use the exact value, the abstract writes **0.002**. Same floor, spelling only.
- **Reproducibility.** Every number carries a pointer to a local artifact; **289 audit anchors** mechanically
  guard the claims, and six checkers
  (`audit_anchors_fupaper.py`, `check_crosscite.py`, `verify_pulled.py`, `gap_mechanism_20260916.py`,
  `verify_pr_forms_20260917.py`, `verify_submission_pack_20260917.py`) ship with the archive: **one is
  runnable by a holder of the archive unaided, the anchor audit checks 270 of its 289 anchors there, and
  four are author-side gates** (**the package README says which**). The archive is the one deposited above (**Data availability**).

## References

> **Note on preprint citations.** Seventeen of the 55 entries give an arXiv edition. **Three** of them also name a
> peer-reviewed venue (Dodge et al., EMNLP-IJCNLP 2019; Yu et al., IEEE TIM 2024; Pintelas & Livieris,
> IEEE TNNLS 2026). **The other fourteen have no peer-reviewed version**, and they are not one kind of
> thing: four are cited at a benchmark's or dataset's canonical release (COCO; xView; DIOR; CrowdHuman),
> two are methodological (Smith & Winkler; Roth), and the **remaining eight** are the closest concurrent
> and tooling works — **Guedes de Souza & Panisson; Apicella et al.; Suo et al.; Zhang & Zhao;
> Bouthillier et al.; Sweeney; Tian et al.; Ajroldi et al.**, of which **two are from 2025 and six from
> 2026**. All of the fourteen are cited **for positioning only**
> on them, every number being measured on our own corpora or on the third-party logs of §5.5.

[1] Z. Zou, K. Chen, Z. Shi, Y. Guo, J. Ye. "Object Detection in 20 Years: A Survey." *Proceedings of the IEEE* 111(3):257-276 (2023). DOI 10.1109/JPROC.2023.3238524
[2] R. Guedes de Souza, A.R. Panisson. "Who Thinks Best Depends on How Long You Let Them: Budget-Dependent Rankings in LLM Evaluation." arXiv:2608.12150 (2026).
[3] S. Kapoor, A. Narayanan. "Leakage and the reproducibility crisis in machine-learning-based science." *Patterns* 4(9):100804 (2023). DOI 10.1016/j.patter.2023.100804
[4] B. Barz, J. Denzler. "Do We Train on Test Data? Purging CIFAR of Near-Duplicates." *Journal of Imaging* 6(6):41 (2020).
[5] G.C. Cawley, N.L.C. Talbot. "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation." *Journal of Machine Learning Research* 11(70):2079–2107 (2010).
[6] A. Apicella, F. Isgrò, A. Pollastro, R. Prevete. "Don't stop me now: How Validation Criteria Affect Checkpoint Selection and Early Stopping." arXiv:2602.22107v2 (2026).
[7] J. Dodge, S. Gururangan, D. Card, R. Schwartz, N.A. Smith. "Show Your Work: Improved Reporting of Experimental Results." *Proceedings of EMNLP-IJCNLP 2019*, pp. 2185–2194. https://aclanthology.org/D19-1224/
[8] K. Gorman, S. Bedrick. "We Need to Talk about Standard Splits." *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics* (ACL):2786–2791 (2019). DOI 10.18653/v1/P19-1267
[9] R. Reveles-Martínez, S. Burciaga-Sosa, J.M. Celaya-Padilla, S. Castro-Tapia, H. Luna-García, H. Morales-Magallanes, M.N. Regalado-Pérez, C. Landeros-Soriano, et al.. "Sequence-Aware Dataset Auditing for Leakage-Free Benchmarking of YOLO Detectors for Bottle Detection." *Technologies* 14(9):531 (2026).
[10] W. Ruangsang, P. Pramkeaw. "Cross-Dataset Evaluation of YOLOv8 for Unmanned Aerial Vehicle Fire and Smoke Detection: Benchmark Contamination, Zero-Shot Transfer, and Onboard Deployment on a Low-Cost Airframe." *Drones* 10(8):635 (2026).
[11] Y.K. Adimoolam, C. Poullis, M. Averkiou. "Data Leakage Detection and De-duplication in Large Scale Geospatial Image Datasets." *CVPR* 2026 (Oral). https://openaccess.thecvf.com/content/CVPR2026/html/Adimoolam_Data_Leakage_Detection_and_De-duplication_in_Large_Scale_Geospatial_Image_CVPR_2026_paper.html
[12] H. Suo, H. Wang, Y. Li. "Checkpoint Selection and Evaluation in EEG Emotion Recognition." arXiv:2607.27655 (2026).
[13] Smith JE, Winkler RL. The optimizer's curse: skepticism and postdecision surprise in decision analysis. *Management Science* **52**(3):311–322, 2006. doi:10.1287/mnsc.1050.0451.
[14] M. R. R. Roktim. "When Is a Molecule a Duplicate? Identity Policy Determines What a Benchmark Audit Finds." *ChemRxiv* preprint (2026). DOI 10.26434/chemrxiv.15009099/v1
[15] S. Roth. "Which Leakage Types Matter? A Quantitative Landscape Across 2,047 Benchmark Datasets." arXiv:2604.04199 (2026).
[16] G. Jocher, A. Chaurasia, J. Qiu. *Ultralytics YOLO* (v8.4.120) [computer software] (2023; pinned release 2026). https://github.com/ultralytics/ultralytics (accessed 2026-09-12); the same project's official course states the split-independence rule normatively: Ultralytics Academy, "Splits that Tell the Truth," https://academy.ultralytics.com/courses/computer-vision-foundations/splits-that-tell-the-truth (accessed 2026-09-26). [verified: software release tagged v8.4.120 as used in this study]
[17] B. Recht, R. Roelofs, L. Schmidt, V. Shankar. "Do ImageNet Classifiers Generalize to ImageNet?" *Proceedings of the 36th International Conference on Machine Learning*, PMLR **97**:5389–5400 (2019).
[18] G. Zhang, K. Zhao. "Winning by Peeking: Unenforced Budgets and Test-Set Selection Inflate Short-Budget AutoML Comparisons." arXiv:2608.07303 (2026).
[19] Taylor J, Tibshirani RJ. Statistical learning and selective inference. *Proceedings of the National Academy of Sciences* **112**(25):7629–7634, 2015. doi:10.1073/pnas.1507583112.
[20] Benjamini Y, Yekutieli D. False discovery rate–adjusted multiple confidence intervals for selected parameters. *Journal of the American Statistical Association* **100**(469):71–81, 2005. doi:10.1198/016214504000001907.
[21] M. Everingham, L. Van Gool, C.K.I. Williams, J. Winn, A. Zisserman. "The Pascal Visual Object Classes (VOC) Challenge." *International Journal of Computer Vision* 88(2):303-338 (2009).
[22] Mendeley Data records, "Face Mask Detection" (data records, no venue). Widely used 853-image PASCAL-VOC variant: https://www.kaggle.com/datasets/andrewmvd/face-mask-detection
[23] J. Dodge, G. Ilharco, R. Schwartz, A. Farhadi, H. Hajishirzi, N. Smith. "Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping." arXiv:2002.06305 (2020). DOI 10.48550/arXiv.2002.06305
[24] X. Bouthillier, P. Delaunay, M. Bronzi, A. Trofimov, B. Nichyporuk, J. Szeto, N. Sepah, E. Raff, et al. "Accounting for Variance in Machine Learning Benchmarks." arXiv:2103.03098 (2021). DOI 10.48550/arXiv.2103.03098
[25] B.L. Welch. "The Generalization of 'Student's' Problem when Several Different Population Variances are Involved." *Biometrika* 34(1/2):28 (1947).
[26] K. Kann, K. Cho, S.R. Bowman. "Towards Realistic Practices In Low-Resource Natural Language Processing: The Development Set." *Proceedings of EMNLP-IJCNLP 2019*; arXiv:1909.01522 (2019).
[27] R. Roelofs, V. Shankar, B. Recht, S. Fridovich-Keil, M. Hardt, J. Miller, L. Schmidt. "A Meta-Analysis of Overfitting in Machine Learning." *Advances in Neural Information Processing Systems* **32**:9179-9189 (2019).
[28] Y. Benjamini, Y. Hochberg. "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." *Journal of the Royal Statistical Society Series B: Statistical Methodology* 57(1):289-300 (1995).
[29] *YOLOX* [computer software]. https://github.com/Megvii-BaseDetection/YOLOX (pinned at commit `6ddff4824372`, branch `main`, accessed 2026-09-16).
[30] *Detectron2* [computer software]. https://github.com/facebookresearch/detectron2 (pinned at commit `a2f4a8771ab7`, branch `main`, accessed 2026-09-16).
[31] *MMDetection* [computer software]. https://github.com/open-mmlab/mmdetection (pinned at commit `cfd5d3a985b0`, branch `main`, accessed 2026-09-16).
[32] *DETR* [computer software]. https://github.com/facebookresearch/detr (pinned at commit `29901c51d7fe`, branch `main`, accessed 2026-09-16).
[33] *PaddleDetection* [computer software]. https://github.com/PaddlePaddle/PaddleDetection (pinned at commit `b25522a0f4bd`, branch `release/2.9`, accessed 2026-09-16).
[34] Tsung-Yi Lin, Michael Maire, Serge Belongie, Lubomir Bourdev, Ross Girshick, James Hays, Pietro Perona, Deva Ramanan, C. Lawrence Zitnick, Piotr Dollár. "Microsoft COCO: Common Objects in Context." arXiv:1405.0312 (2014). DOI 10.48550/arXiv.1405.0312
[35] S. Shao, Z. Li, T. Zhang, C. Peng, G. Yu, X. Zhang, J. Li, J. Sun. "Objects365: A Large-Scale, High-Quality Dataset for Object Detection." *2019 IEEE/CVF International Conference on Computer Vision (ICCV)* 8429-8438 (2019).
[36] A. Kuznetsova, H. Rom, N. Alldrin, J. Uijlings, I. Krasin, J. Pont-Tuset, S. Kamali, S. Popov, et al.. "The Open Images Dataset V4." *International Journal of Computer Vision* 128(7):1956-1981 (2020).
[37] G.-S. Xia, X. Bai, J. Ding, et al. "DOTA: a large-scale dataset for object detection in aerial images." *CVPR* 2018, pp. 3974-3983. DOI 10.1109/CVPR.2018.00418.
[38] P. Zhu, L. Wen, D. Du, et al. "Detection and tracking meet drones challenge." *IEEE TPAMI* 44(11):7380-7399 (2022). DOI 10.1109/TPAMI.2021.3119563. (VisDrone.)
[39] J. Wang, W. Yang, H. Guo, R. Zhang, G.S. Xia. "Tiny Object Detection in Aerial Images." *2020 25th International Conference on Pattern Recognition (ICPR)* 3791-3798 (2021). DOI 10.1109/icpr48806.2021.9413340
[40] D. Du, Y. Qi, H. Yu, Y. Yang, K. Duan, G. Li, W. Zhang, Q. Huang, et al.. "The Unmanned Aerial Vehicle Benchmark: Object Detection and Tracking." *Lecture Notes in Computer Science* 375-391 (2018). DOI 10.1007/978-3-030-01249-6_23
[41] Darius Lam, Richard Kuzma, Kevin McGee, Samuel Dooley, Michael Laielli, Matthew Klaric, Yaroslav Bulatov, Brendan McCord. "xView: Objects in Context in Overhead Imagery." arXiv:1802.07856 (2018). DOI 10.48550/arXiv.1802.07856
[42] Ke Li, Gang Wan, Gong Cheng, Liqiu Meng, Junwei Han. "Object Detection in Optical Remote Sensing Images: A Survey and A New Benchmark." arXiv:1909.00133 (2019). DOI 10.48550/arXiv.1909.00133 (DIOR benchmark)
[43] G. Cheng, J. Han, P. Zhou, L. Guo. "Multi-class geospatial object detection and geographic image classification based on collection of part detectors." *ISPRS Journal of Photogrammetry and Remote Sensing* 98:119-132 (2014).
[44] Xu et al. "Detection of safety helmet wearing based on improved SSD." *Journal of Physics: Conference Series* (2019). Dataset: https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset
[45] Fusheng Yu, Jiang Li, Xiaoping Wang, Shaojin Wu, Junjie Zhang, Zhigang Zeng. "Large, Complex, and Realistic Safety Clothing and Helmet Detection: Dataset and Method." arXiv:2306.02098 (2023); journal version in *IEEE Transactions on Instrumentation and Measurement* (2024). DOI 10.48550/arXiv.2306.02098 (SFCHD / SFCHD-SCALE)
[46] S. Ge, J. Li, et al. "Detecting masked faces in the wild with LLE-CNNs." *CVPR* 2017, pp. 426-434. DOI 10.1109/CVPR.2017.53. (Cited only to delimit the MAFA packaging difference.)
[47] S. Yang, P. Luo, C.C. Loy, X. Tang. "WIDER FACE: A Face Detection Benchmark." *2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)* 5525-5533 (2016).
[48] Shuai Shao, Zijian Zhao, Boxun Li, Tete Xiao, Gang Yu, Xiangyu Zhang, Jian Sun. "CrowdHuman: A Benchmark for Detecting Human in a Crowd." arXiv:1805.00123 (2018). DOI 10.48550/arXiv.1805.00123
[49] P.V.A.B. de Venâncio, A.C. Lisboa, A.V. Barbosa. "An automatic fire detection system based on deep convolutional neural networks for low-power, resource-constrained devices." *Neural Computing and Applications* 34(18):15349-15368 (2022). DOI 10.1007/s00521-022-07467-z
[50] L. Cascone, M. Nappi, C. Pero, X. Wang. "A framework for bias-aware dataset evaluation in soft facial attribute recognition." *Pattern Recognition* 172:112416 (2026). DOI 10.1016/j.patcog.2025.112416
[51] Y. Huang, Z. Zhang, Y. Huang, Q. Wu, H. Huang, Y. Zhong, L. Wang. "Customized meta-dataset for automatic classifier accuracy evaluation." *Pattern Recognition* 146:110026 (2024). DOI 10.1016/j.patcog.2023.110026
[52] J. Sweeney. "Optimizer Memory Makes Shuffle Order a First-Order Source of Fine-Tuning Noise." arXiv:2606.29554 (2026).
[53] E. Pintelas, I.E. Livieris. "GeNeX: Genetic Network eXperts framework for addressing Validation Overfitting." *IEEE Transactions on Neural Networks and Learning Systems* (2026); arXiv:2603.11056. DOI 10.48550/arXiv.2603.11056
[54] Y. Tian, Q. Ye, D. Doermann. "YOLOv12: attention-centric real-time object detectors." arXiv:2502.12524 (2025).
[55] N. Ajroldi, A. Orvieto, J. Geiping. "When, Where and Why to Average Weights?" arXiv:2502.06761 (2025).
