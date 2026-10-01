# Second coding of the 19 x 4 marking table — artefacts

This directory holds everything behind the supplementary's section *"An independent second coding of the
19-row marking table"*, so that the agreement statistics there can be recomputed rather than trusted.

## The instruments (the rules a coder received)

| file | what it is |
|---|---|
| `coding_manual_19x4_20260927.md` | the coding manual: rules only, no marks. Written for the **non-blind, model-assisted** pass. |
| `taska_19x4_v1.md` | the **blind** task sheet, first version: 19 rows x 4 units, `yes`/`no`/`unknown`, evidence pointers only. |
| `taskb_19x4_v2.md` | the blind task sheet, second version (2026-09-29): a five-way scale (`independent` / `alias` / `absent` / `gated` / `unknown`), the `reported` frame stated as *the number the literature prints*, and three worked examples on invented benchmarks. **Prepared after the eight-coder round diagnosed the v1 frame problem; not yet run.** |
| `blank_table_v1.md` | the optional blank answer table handed out with `taska`. |

## The returns (verbatim, one file per coder)

`G8_coding_<identifier>_20260929.md` — eight language models (three of them from vendors already used in the first two rounds, five from vendors not used there), each
coding the same 19 x 4 = 76 cells blind, in a fresh session, under the **clarified** rules, answering **in
chat** (the coordinator transcribed each answer verbatim, so no coder could see another's output or any
file). Each file carries the coder's own blind-status declaration (network use: no; other coders' material
read: no) and its ambiguity report.

## The earlier passes

| file | what it is |
|---|---|
| `second_coding_20260927.csv` | the **non-blind, model-assisted** pass of 2026-09-27, in the table's own 12-mark vocabulary, with a per-row note. |
| `kappa_computed_20260927.txt` | that pass's agreement statistics against the printed coding. |

## The new analysis

| file | what it is |
|---|---|
| `kappa_g8_primary_20261001.txt` | the **primary** mapping of the eight-coder round (v1 returns): per-coder kappa against the printed coding (overall and per unit), the 28 pairwise values, Fleiss' kappa, the confusion tables and the headline recomputation. **This is the vintage the supplement's printed range 0.105-0.325 (median 0.308) comes from.** |
| `kappa_g8_20260929.txt` | **the `--sens` sensitivity variant of the same round** (its own first line says so: the two genuinely ambiguous vocabulary items read as `unknown`): same statistics, range 0.063-0.278, median 0.260. It is **not** the vintage the supplement prints; both are shipped so the choice can be checked. |
| `kappa_g8_20260929.py` | the script that produced both reports (also runs a `--sens` variant that re-reads the two genuinely ambiguous vocabulary items the other way, and `probe_g8_matrix_20260929.py` prints the per-row matrix). |
| `g8_primary_run_20261001.py` | re-runs that script on the v1 returns for the **primary** mapping and re-runs the `--sens` variant, checking it against the shipped sensitivity file. |

**The mapping used, stated because it is a convention:** the printed 12-mark vocabulary was collapsed to
the coders' three-way scale per unit — `independent_test, clean -> yes`; `alias, train_val_alias -> no`;
`n_a, no_test, no_val, no_split, no_yaml, contradictory, unknown -> unknown`; with `test_gated` read as
`yes` on the `release` column and `no` on `protocol` (the `--sens` variant reads those two as `unknown`).
The result is robust to that choice: the mean moves by about 0.05 and nothing qualitative changes.
