# Reproduction package — configuration-level split aliasing in object-detection benchmarks

This package carries the artifacts the manuscript points at, so that every number it states can be
checked rather than taken on trust. It accompanies the manuscript and its Supplementary Material.

## Version and snapshot

This snapshot carries the submission text of **2026-10-01** (editing rounds r134-r176 of the authors' own log: the eighth review round's remediations, the presentation pass, and the method-detail relocation). The manuscript copies under `01_paper/` are **byte-identical** to the submitted files: `P2_English_v0.1.md` md5 `a54be2d92872d67ceefa761a3d389b79`, `P2_English_submission_blind_v1.md` md5 `6086322fb5ab6193771a5b5288dadc5f`, `P2_Supplementary_English_v0.1.md` md5 `45d6555597b7eae8f32d11e50e533245`. The Data availability statement in the article names this repository with the access date **2026-09-29** (the deposit date; the text was refreshed on 2026-10-01; the released-data correction of 2026-10-02 is recorded below), and the commit hash is the one this file is served from.

## Licence

See `LICENSE` in the repository root. The authors' own material is CC BY 4.0; the third-party datasets and training logs are **not** redistributed and are **not** covered by that licence.

## Which of the six checkers run from this package (measured, 2026-10-01)

The article names six checkers. Every entry point was run from an unpacked copy of this tree with `P2_ROOT` pointed at the copy and `P2_NO_AUTHOR_FALLBACK=1` (so the authors' working tree cannot quietly supply what the package lacks); the results are in the authors' log, round r169.

| checker | runs from this package alone | what it additionally needs |
|---|---|---|
| `work/verify_pulled.py` | **yes** -- no arguments: 85 records, 0 mismatches | -- |
| `04_verification/audit_anchors_fupaper.py` | **partly: 13 of its 18 inputs, i.e. 270 of the 289 anchors**, measured with `P2_NO_AUTHOR_FALLBACK=1` on a machine without the authors' `D:\` drive; it reports the root it used, the inputs it resolved and the ones it could not, and exits 3 under that flag instead of printing a PASS. The 19 anchors it cannot check there -- X05-X07, X09, X15-X17, X19-X28, X37, X41 -- read four working-tree documents plus one `D:\` file | those four documents (the audit correction and adjudication record, the two-critiques check, the internal track/gap record and the reference list) and the author-machine file `split_audit_integration_20260915.md`; `figures/FIGURES.md` and `verify_two_critiques_20260916.txt` **are** shipped, as are the graphical abstract, the submission front matter and the forms record |
| `04_verification/verify_pr_forms_20260917.py` | no -- **author-side generator** | the archived publisher-guideline evidence on the authors' `D:\` drive; it writes the forms-verification record into the working tree |
| `work/check_crosscite.py` | no -- **author-side gate** | the companion paper's governing drafts and the working-tree Chinese draft; two of its items cannot be satisfied here |
| `04_verification/verify_submission_pack_20260917.py` | no -- **author-side gate** | the submission front matter, the reference list and the forms record; run here it stops with a readable "missing author-side input" message and exit code 2 |
| `work/gap_mechanism_20260916.py` | no -- **author-side gate** | the working-tree run archives; its artefact, `02_release_data/gap_mechanism_20260916.txt`, is shipped and byte-checkable |

Two claims made in an earlier version of this file were **wrong and are withdrawn**: that `audit_anchors_fupaper.py` "runs from this package alone and passes" (it passed on the authors' machine because the working tree was present) and that "no checker hardcodes an author-machine path" (the anchor checker did; it now resolves `P2_ROOT` -> package root -> authors' tree, and the author-side generators point at the working tree by design, as the table says).


## One released-data correction (2026-10-02)

One row of the released registered-replication summary had been computed with the wrong endpoint. In `02_release_data/release_T2_saturated-control_summary.csv` the saturated control's `test_best_epoch` row carried one run's **`last`** reading in place of its **`best`** reading (`t2_mask2mende_base100_s42n`: `67.1200`, against `67.1183` for that run's `last` and `70.0603` for its `best`); that run's `source_test` also came from a different machine from the rest of its family. The row is corrected here, and in `P2_T1_registered-replication_long.csv`, to `-1.4901` pp (sd `0.8002`, paired t `-4.164`, p `0.0141`, signs `0+/5-` over the five runs in the row), which is what the row reads once every run contributes the quantity its column names. **The article's own printed figure for this control does not change**, because what it quotes is the `last`-epoch row, which was already correct; but note that the **corrected** `best`-epoch row is **significant** (p `0.0141`), so under the article's frozen `best` convention this control is significant — the article's §7.3 and Table S16 now state that, and its Table S25 is endpoint-independent. A systematic check of every released per-run `test` value against fresh re-evaluations found this to be the **only** row that mixed the two quantities; seven further rows (`t1d_dotatod15_*`) differ from the fresh re-evaluation by `0.012`-`0.164` pp in the direction of `best`, i.e. within the cross-machine band the submission measured, and are **not** corrected. The archives the re-evaluations were read from are named in that file's own `source_run` field, and the corrected row's per-run long form is in `P2_T1_registered-replication_long.csv`.


## Layout

| Directory | What is in it |
|---|---|
| `01_paper/` | the article (working and anonymised forms, Markdown and PDF), the Supplementary Material in English (authoritative artefact) and its Chinese source record, and the governing Chinese draft |
| `02_release_data/` | the released readings the article cites: the 806-checkpoint per-epoch sweep, the 90-run registered replication in long form, the 2×2 evaluation matrix × archive, the 569-run selection-premium reading, and the verdict files of §13.1 (G1 is void in the article; G1′, G1″, G2, G3, G4) |
| `03_framework_audit/` | the pinned-commit cross-framework configuration census (hashes of the official configuration files) and the curve analysis |
| `04_verification/` | the checkers. `audit_anchors_fupaper.py` is the 289-anchor audit; `remeasure_official_20260920.py` reproduces the page count **together with its positive control**; `prelaunch_cite_guard_20260920.py` checks that every named entity carries a citation where it first appears; `round_stages_20260917.json` records, per round, which numeric changes each editing pass made. |

## How to check the claims

1. **Integrity first.** Run `python verify_release.py` — it recomputes every SHA-256 in
   `MANIFEST_sha256.csv` and prints a table. A mismatch means the copy you have is not the copy the
   authors released.
2. **Reference numbers.** The article numbers its citations in order of first appearance, as the
   venue requires. `04_verification/prelaunch_cite_guard_20260920.py` re-checks that every named
   dataset, framework and model carries a citation at first mention, and that the reference list and
   the in-text citations are mutually complete.
3. **Anchors.** `04_verification/audit_anchors_fupaper.py` re-checks the 289 load-bearing claims
   against the article; the sweep prints every suite's own verdict.
4. **Page limit.** `04_verification/remeasure_official_20260920.py` builds the article in the venue's
   own geometry (single column, Times New Roman 10 pt, 1.5 line spacing, margins 4.3/4.8/4.3/4.8 cm)
   and measures it with Word's pagination engine. It injects a **600-word control paragraph** and
   refuses to write its record unless the page count responds — a measurement that cannot move is not
   a measurement, and this article sits exactly on the 35-page limit.

## What is deliberately not here

* **Third-party training logs.** The public-log sample of §5.5 is described by source pointer; its own hash list is
  **author-side** and is named as such in the supplement: those logs are other people's data, five of their sources state no licence, and this
  package does not redistribute them.
* **Training run archives.** The raw per-run archives (tens of GB, plus a large run tarball) are not
  included; the released CSVs and the per-epoch matrix in `02_release_data/` carry the numbers the
  article reports, and the per-run `results.csv` files they were derived from are identified by pointer
  in the Supplementary Material.
* **Internal project records** (working logs, hand-over notes, review correspondence): not paper
  material.

## Note on the two forms of the article

`P2_English_v0.1.md` is the working form; it carries audit provenance (file names, hashes, the draft
history), which the project keeps on purpose. `P2_English_submission_blind_v1.md` is the anonymised
form built from it, with that provenance removed and no personal data in the document properties.
The two differ only in that provenance and in nothing that carries a result.

## Licence and reuse

The article, its Supplementary Material and the authors' own data files in `02_release_data/` are
released for verification of the published claims. Third-party configuration files referenced in
`03_framework_audit/` remain under their own upstream licences; their pinned commits are recorded so
that the same files can be obtained from their own repositories.

## The headline realization rate: recompute inputs (C01)

`work/item2_final_v2_20260925.py` reproduces Table 4's realization rate. Its inputs are shipped here under `02_release_data/`: `xeval_20260916/` (per-run `*_results.csv` with the epoch curves), `aitod20_n10_20260924/` (that cell's `x4_teval.csv`) and `x4fill_20260925/` — the three inputs an earlier release did not carry, which is what the review round flagged. The script resolves its paths from the package root, so it can be run from an unpacked copy.
