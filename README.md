# Reproduction package — configuration-level split aliasing in object-detection benchmarks

This package carries the artifacts the manuscript points at, so that every number it states can be
checked rather than taken on trust. It accompanies the manuscript and its Supplementary Material.

## Version and snapshot

This snapshot carries the submission text of **2026-09-29** (editing rounds r121 and r122 of the authors' own log). The manuscript copies under `01_paper/` are **byte-identical** to the submitted files: `P2_English_v0.1.md` md5 `e9b5d65392bec46fa9cfa215161cf927`, `P2_English_submission_blind_v1.md` md5 `15d7e31f7adad2cef6885066285b6623`, `P2_Supplementary_English_v0.1.md` md5 `95c768b45c16b7c4e5dcc0148ecce6e9`. The Data availability statement in the article names this repository with the access date **2026-09-29**, the date of the commit that carries this snapshot; the commit hash is the one this file is served from.

## Licence

See `LICENSE` in the repository root. The authors' own material is CC BY 4.0; the third-party datasets and training logs are **not** redistributed and are **not** covered by that licence.

## What is deliberately not here

* the third-party training logs (hashes and source pointers only);
* the original training-run archives (tens of gigabytes) and `x1.log`;
* six of the seven detection corpora -- the archive that produced the paper does not hold them;
* anything the article itself marks as `local`: those are named in the text with the word local and are reproduced from the author-side tree rather than from this package.

## Layout

| Directory | What is in it |
|---|---|
| `01_paper/` | the article (working and anonymised forms, Markdown and PDF), the Supplementary Material in English (authoritative artefact) and its Chinese source record, and the governing Chinese draft |
| `02_release_data/` | the released readings the article cites: the 806-checkpoint per-epoch sweep, the 90-run registered replication in long form, the 2×2 evaluation matrix × archive, the 569-run selection-premium reading, and the verdict files of §13.1 (G1, G1′, G1″, G2, G3, G4) |
| `03_framework_audit/` | the pinned-commit cross-framework configuration census (hashes of the official configuration files) and the curve analysis |
| `04_verification/` | the checkers. `run_sweep_20260919.py` runs the whole suite; `audit_anchors_fupaper.py` is the 289-anchor audit; `remeasure_official_20260920.py` reproduces the page count **together with its positive control**; `prelaunch_cite_guard_20260920.py` checks that every named entity carries a citation where it first appears; `round_stages_20260917.json` records, per round, which numeric changes each editing pass made. |

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

* **Third-party training logs.** The public-log sample of §5.5 is described by source pointer and
  hash only: those logs are other people's data, five of their sources state no licence, and this
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
