---
id: DOC-PORTFOLIO-INVESTIGATION-IPD-SURVIVAL-2-2026-09-09
title: "IPD-SURVIVAL-2 — the reporting census PUB-IPD-SURVIVAL rests on is repeatable at this HEAD, and it reproduces byte for byte"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# IPD-SURVIVAL-2 — the census was believed unrepeatable here. It is not, and it reproduces exactly.

⛔ Nothing here is medical advice, and nothing here asserts efficacy, safety, selectivity,
therapeutic window or clinical readiness for any therapy. Nothing here creates a patient, a cohort
or a day of follow-up. There is no wet lab. Every quantity is either a property of an already
published figure or a property of a measurement record about one.

## 1 · The question

`PUB-IPD-SURVIVAL`'s headline claim is a **negative about reporting practice**: of the reachable
extraskeletal myxoid chondrosarcoma series, the two largest print **seven Kaplan–Meier curves
between them and no numbers-at-risk row**, so those curves cannot be reconstructed at all. Every one
of those verdicts comes from **one execution** of `research/modalities/km_risk_row_detect.py` on
PDFs that are deliberately **not committed** (licence). The repository's own instrument audit
(`reports/W65-km-risk-row-instrument-audit.md`) closed by naming this as the artifact's only
untested clause and grading the real-figure arm **"not runnable at this HEAD"**, because
`origin/literature-cache` was measured absent from the checkout. So: **is that census repeatable in
this checkout, and if it is, does it reproduce?**

## 2 · Paper-level merit

The paper's contribution is now a methods-and-census negative, and a census is only worth
publishing if a reader can check it. Right now the census's five input digests point at files no
reader of this repository can reach, and the recorded position is that they are unreachable here
too. Either answer is publishable and they are opposite: if the inputs are genuinely gone, the paper
must say its central measurement is unrepeatable and carries a provenance record that cannot be
falsified; if the inputs are present, the measurement becomes an ordinary reproducible result and
the paper can say so with a command. That question is patient-relevant only indirectly — it decides
whether the field-level statement "this literature does not print what reconstruction needs" is
evidence or assertion — but it is exactly the kind of claim that gets reused by anyone digitizing a
rare-disease figure, so it must be checkable.

## 3 · The exact evidence gap, and how it differs from prior work

Named inputs: `research/modalities/km-risk-row-detection.json` (the committed measurement — 5
papers, 15 figures, 2 `present` / 9 `absent` / 4 `undetermined`, with per-figure band geometry),
`research/modalities/km_risk_row_detect.py` (the rule and its constants),
`research/modalities/emc_ipd_survival.py` (the eye reading of the one recovered risk row),
`research/modalities/km-figure-readings.json` (the single real curve reading), git object
`454df7114…` on `origin/literature-cache`.

* **W65** cross-tabulated the recorded verdicts against the recorded human reading and reproduced
  the **synthetic** control (8/8). It did not, and said it could not, re-run the **real-figure**
  arm. Its stated successor was exactly this question.
* **First-round `PUB-IPD-SURVIVAL`** worked one layer down — decision-level uncertainty on the one
  digitized curve — and left the census layer untouched. **Its numbers are not assumed here; they
  are re-derived below.**
* **S6/S7** looked outward for an external figure–truth pair (0 matched, one candidate
  `EGRESS_BLOCKED`). Not retried, not proxied, not substituted. This lane needs no retrieval: the
  inputs were already inside the repository's object store.
* `research/autonomy/portfolio-2026-09-05/recommendation.md` reconciled: its IPD prospect is no
  longer "digitize the curves" — that was attempted and produced the negative census plus one curve
  — so the open work is the census's own checkability, which no later result closed.

## 4 · Step taken, and results

### 4.0 Re-derivation of the first round's numbers (prerequisite, `checks/01`)

`rederive_first_round.py` recomputes every load-bearing number the first-round lane reported. The
Guyot inversion is the artifact under test so it is imported, but the **product-limit estimate, the
median, S(6) and the predicted numbers-at-risk are recomputed by a local estimator** that does not
call `kaplan_meier`, `survival_at` or `_median_survival`.

**ALL REPORTED NUMBERS REPRODUCE — zero mismatches.** Anchored branch n=11, 9 events, 2 censored,
deviation 0.0454, median 7.984996, S(6) 0.511364 (local estimator agrees with the module to 6 dp);
printed branch n=10, 9 events, 1 censored, deviation 0.0903, median 4.987643, inadmissible. E2
hold-outs t=4 → 7 vs 7, t=6 → 5 vs 4, t=8 → 1 vs 2, t=10 → 0 vs 0, deviations 0.0454 / 0.0454 /
0.0324 / 0.0454, median 7.984996 in all four. E1 over the same 123 offsets: anchored median
{7.984996}, (events, censored) {(8,3), (9,2), (10,1)}, smallest inadmissible positive offset 0.005,
printed branch never admissible, its minimum deviation 0.0604. Building on the first round is
therefore justified.

### 4.1 Is the census re-derivable from what the artifact preserved? (`checks/02`, `checks/06`)

`census_rederive.py` re-applies the decision rule — constants parsed **out of the source**, not
retyped — to the band geometry the artifact preserved, and recomputes, per band, the median mark
width fraction, the tick-alignment count, the tick-label reference band and the final verdict.

* **11 of 15 figures preserve enough geometry to re-derive. All 11 verdicts re-derive identically**,
  including both `present` verdicts and every `absent` one, with matching `risk_row_band_index`,
  `tick_label_band_index` and figure-level `matched_ticks`.
* The remaining **4 are `undetermined` rows that return before any band is recorded** (undecodable
  embedded encoding, too few tokens). They are not re-derivable and are reported as such — not as
  agreement.
* The constants the artifact advertises match the constants the code holds exactly (no drift).
* Three differences appeared, all in `median_mark_width_frac` on one figure, all of magnitude
  **0.0001**. `checks/06` shows they are **recorded-precision rounding** — the artifact stores that
  fraction to 4 dp and the text arm's width scale to 1 dp — and that **no clause outcome flips**
  under either value. No verdict depends on them.
* The one printed risk row whose **values** the instrument recovered (morioka2016 Fig. 1, text arm)
  is **identical, machine-compared, to the eye reading** transcribed in `emc_ipd_survival.py`:
  `[[0,5],[3,5],[6,5],[9,3],[12,3],[15,1],[18,1],[21,1]]`.

### 4.2 Do the recorded inputs resolve here? (`checks/03`) — **the recorded position is wrong**

`git cat-file -t 454df71144f677b1e84ed58f7a6c6951a4190f66` → `commit`, exit 0.
`git rev-parse --verify origin/literature-cache` → `216bd1b5fb…`, exit 0.
`git ls-tree -r 454df7114 -- literature/km-figures-2026-08-25/` lists **all five PDFs and every page
raster**, with byte sizes equal to the recorded `pdf_bytes`.

Extracted from the object store to scratch (outside the repository; no licensed file was written
into the repository) and hashed:

| source | recorded `pdf_sha256` | measured sha256 | match |
|---|---|---|---|
| chiusole2020 | `6f0b024ddaa9c65700ea46f2c89c3120f8ecb1c10ef3a6ee820dc91dc7e0a788` | identical | ✔ |
| martinbroto2020immunosarc1 | `2869688dba5426516415a388457213e6c6fa87f46a58ee3cb7b432fe0635f40f` | identical | ✔ |
| masunaga2025 | `4ae16c8e3b901398a2c881007d64d74ce94176f997f2b3d069ac17c2de00461a` | identical | ✔ |
| morioka2016trabectedin | `03574d05d823ecaa4a460f772fb1fd8eec1028fd74da7a180ab2431b8402f292` | identical | ✔ |
| stacchiotti2013anthracycline | `1df76e6b01167c7737a34bd4ab93659b3d2a7b38797fad4783667e24f7ab774a` | identical | ✔ |

**5 / 5 digests match.** The provenance record is **ENFORCED at this HEAD**, not undecidable. W65's
"not runnable at this HEAD", and the W40 measurement it rests on ("`origin/literature-cache` has
never existed in this checkout"), are **refuted as of 2026-09-09T00:47Z on HEAD `04a4e0ef…`**. I did
not fetch: no network call was made, and the ref was already present locally.

### 4.3 Re-execution of the census on its original inputs (`checks/04`, `checks/05`) — **exact**

`km_risk_row_detect.py --pdf-dir <scratch> --page-png-dir <scratch>`, output written **into this
lane directory only**, exit 0. Reproduced totals: **papers 5, figures 15, with_risk_row 2, without
9, undetermined 4** — identical to the committed totals.

`compare_reproduced.py` then walks the two documents field by field over `sources`, `_totals`,
`control` and `method` (excluding only the provenance strings passed on the command line):

> **0 field differences. 0 verdict differences.** Every figure, every band, every mark centroid and
> width, every `matched_ticks`, every `label_phrase_found`, and the whole synthetic control block
> are identical to the committed measurement.

**Consequence for the paper.** The seven Kaplan–Meier curves the headline negative is built on —
masunaga2025 Figs. 1–3 and chiusole2020 Figs. 1–4 — are `absent` in the committed record, `absent`
on re-derivation from preserved geometry, and `absent` on full re-execution from the original PDFs
whose digests match. The census is a reproducible measurement, and the paper can print the command.

### 4.4 How close is any negative to flipping? (in `census-verdict-rederivation.json`)

For the seven headline KM figures, the nearest non-qualifying band fails **three clauses at once**
(chiusole: 1 mark, 1 matched, median width 0.15–0.16 against a 0.055 ceiling — an axis title;
masunaga: 2 marks, 0 matched, width 0.20–0.22). None is near the boundary. The single near-miss in
the whole artifact is **martinbroto2020 p6 — the swimmer plot, which is not a KM figure and is
excluded from the nine** — where a band of 5 narrow marks with 3 matched ticks fails **only** the
proximity clause. That clause is the one I could not re-derive, because the artifact preserves each
mark's `cy` but not its `y0`/`y1`.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `census-reproduced-2026-09-09.json` (full re-executed census),
  `census-reproduction-diff.json` (field-by-field comparison, 0 differences),
  `census-verdict-rederivation.json` (per-figure rule re-derivation and flip margins),
  `rederivation-first-round.json` (first-round numbers re-derived, 0 mismatches),
  `rounding-stability.json`; scripts `census_rederive.py`, `compare_reproduced.py`,
  `rederive_first_round.py`, `rounding_stability.py`; `checks/01`–`checks/06`, each with
  `command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`. **All six attempts exited 0; no
  attempt failed and none is omitted.** `checks/04/stderr.txt` retains four benign pdf-parser
  warnings from the re-execution.
* **Validation / baseline.** The baseline is the committed artifact itself, at two independent
  levels: rule application re-derived from preserved intermediates, and the whole measurement
  re-executed from digest-verified original inputs. The synthetic control shipped inside the
  artifact re-ran as part of the re-execution and compared identical. The first-round lane's numbers
  were reproduced before anything was built on them.
* **Provenance.** Repo HEAD `04a4e0ef3078fca4259109ed376efdc60bca3aaa`, 2026-09-09 00:47–00:52 UTC,
  13 GiB free. Inputs: git object `454df71144f677b1e84ed58f7a6c6951a4190f66`
  (`literature/km-figures-2026-08-25/`) on `origin/literature-cache`, already in the local object
  store. PDFs extracted to a scratch directory outside the repository and deleted after the run; no
  licensed file was written into the repository and none is retained here. No network call, no
  fetch, no GPU, no paid API, no subagent, no git write, no `preflight.sh`, no edit outside this
  directory.
* **Limitations.** ⛔ This measures **reporting practice and measurement reproducibility, not
  survival**. Reproducing a census does not make its verdicts true: re-execution bounds
  determinism and transcription, and the geometry re-derivation bounds rule application — **neither
  bounds perception**. A figure mis-segmented, mis-thresholded or never seen by the detector would
  reproduce just as exactly. The four `undetermined` rows remain unanswered questions, not
  negatives. The proximity clause of the rule is **not** re-derivable from the artifact, because
  per-mark `y0`/`y1` are not preserved; for the seven headline figures this is immaterial (each
  fails three other clauses), but for the swimmer-plot row the `absent` verdict rests on it alone.
  The partition "which rows are the nine KM figures" is still human-supplied. Four chiusole2020
  verdicts still rest on a page raster rather than the publisher's image. Nothing here is a
  statement about any patient, any therapy, or any survival estimate; the reproduced census cures
  none of the paper's other missing evidence; and the availability of these five PDFs in the object
  store says nothing about the sources that remain unreachable (seer270_2022, meisKindblom1999).
* **Stop condition (met, and set before running).** Stop as soon as (i) the first round's reported
  numbers are independently re-derived or a mismatch is found, (ii) the recorded verdicts are
  re-derived from preserved geometry or shown not re-derivable, and (iii) the input digests are
  resolved to ENFORCED or UNDECIDABLE — with, if and only if they resolve, one re-execution and one
  field comparison. All met. Stopped; nothing padded, no second census, no new source.

## 6 · Next credible independent work (not done here)

1. **A correction, for the owner, not applied by me.** `reports/W65-km-risk-row-instrument-audit.md`
   records the real-figure arm as "not runnable at this HEAD" and cites W40 for
   `origin/literature-cache` never having existed in this checkout. That is measurably false today.
   I did not edit it: it is another lane's report and the parent alone records shared state. **No
   tracked non-campaign file needs to change for this lane's result to stand**, which is why this
   lane emits no unapplied diff.
2. **Preserve `y0`/`y1` per mark in `km_risk_row_detect.py`'s `Token.as_dict`.** It is additive, it
   weakens no clause, and it would make the proximity clause — currently the sole support of one
   `absent` verdict — re-derivable like every other clause. It regenerates the committed artifact,
   so it is the owner's call, not a worker's.
3. The genuinely blocked dependency is unchanged and untouched: a real figure whose patient-level
   truth is also published (S6/S7, `EGRESS_BLOCKED`). Nothing here substitutes for it, and nothing
   here reopens a closed route.
