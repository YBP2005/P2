# The blind-coding toolbox (round v4.5)

This directory releases the instrument and the returned matrices behind the article's Finding 3
(the 19-row x 4-unit marking table). It exists because the table is a **single-rater** product and the
natural objection is that its cells are not reproducible from the public record.

* `p2_coding_instrument_v46.md` - exactly what each coder received: a decision procedure plus, per row,
  an evidence card. It contains **no per-row mark, no confidence and no reference to the printed table**,
  with **one disclosed exception**: its *output-format* section illustrates the required format by filling
  in **row 1 (COCO)**. Those four illustrative values match **neither** the printed marking **nor** the
  re-verified one - printed `n_a` / `independent_test` / `clean` / `clean` against illustrative `gated` /
  `gated` / `gated` / `unknown` - and all five coders saw the same template, so the illustration was not a
  channel for the answer; a future round should nevertheless illustrate with an **abstract row** rather than
  a real one.
* `decision_procedure_v46.md` - the procedure alone (value sets, four decision trees, the explicit
  counting convention, and the three general rulings for multi-variant layers, gate-vs-absence, and the
  `contradictory` threshold).
* `evidence_cards_19rows.md` - the 19 cards alone (verbatim evidence with source, line number and pinned
  commit for the first-party re-verification of 2026-10-09).
* `returned_matrix_v45.json` - the five coders' returned judgement matrix.
* `coding_round_v45_summary.md` - the round summary: agreement among coders, the `blocked` cells, and the
  reproduction of the corrected cells.

**How to read it.** The five coders were blind to the printed marks and to each other. Agreement among
them is **Fleiss kappa 0.824**; re-verifying every row against first-party artifacts changed **30 cells**,
and the five independently reach the corrected value in **19 of those 30** (eleven unanimously). What the
five cannot recover is the printed mark, and the residual is a matter of counting convention and rule
wording rather than of evidence; both are stated in the Supplementary correction record.
