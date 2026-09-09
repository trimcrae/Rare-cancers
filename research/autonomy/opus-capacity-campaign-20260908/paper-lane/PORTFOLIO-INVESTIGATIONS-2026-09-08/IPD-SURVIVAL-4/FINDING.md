---
id: DOC-PORTFOLIO-INVESTIGATION-IPD-SURVIVAL-4-2026-09-09
title: "IPD-SURVIVAL-4 — the last unre-derivable clause closes: recording the text arm's page height takes proximity re-derivation to 11 of 15, and morioka2016 Fig. 1's `present` verdict is confirmed"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# IPD-SURVIVAL-4 — closing the gap IPD-SURVIVAL-3 could not close

⛔ **Instrument provenance, not survival analysis.** Nothing here is medical advice and nothing here
asserts efficacy, safety, selectivity, prognosis, therapeutic window or clinical readiness for any
therapy. No curve was digitised, no IPD was reconstructed, no cohort exists, and the closed KM/IPD
pilot was not reopened. Every quantity below is a property of a published figure's *geometry*, or of
a measurement record about one.

## 1 · The question

IPD-SURVIVAL-3's additive `y0`/`y1` change made the proximity clause
(`near_enough_to_tick_labels`, `MAX_RISK_GAP`) of `km_risk_row_detect.decide()` re-derivable for
**10 of 15** figures. Five stayed out of reach: four `undetermined` rows that return before any band
is recorded, **plus morioka2016 p4 — caption "Fig. 1 Kaplan-Meier plot of progression-free
survival", the TEXT arm — whose proximity denominator is `page.bbox[3]` and is recorded nowhere.**
So: **can `page.bbox[3]` be recorded the same additive way, and if it is, does morioka2016 Fig. 1's
recorded verdict survive being checked?** That figure is not a bystander: it is the **only `present`
verdict from the text arm** and the one figure in the whole census whose printed numbers-at-risk the
instrument actually recovered.

## 2 · Paper-level merit

A census is publishable only if a reader can re-run it *and* re-derive its rule. IPD-SURVIVAL-2 and
-3 removed most of the "trust the instrument here"; this lane removes the rest that geometry can
reach. The specific value is that the residue was not a negative sitting on an unverifiable clause —
it was the census's **one positive**. A reader could check every clause of every `absent` verdict and
still had to take on faith the clause under the row the paper cites as the single recovered
numbers-at-risk row. Patient relevance is indirect and is stated as such: it decides whether "this
literature does not print what reconstruction needs" is evidence or assertion. It is **not** a
survival result of any kind.

## 3 · The exact evidence gap, and what distinguishes it

Named inputs, all already local — **no PDF was fetched and no network call was made**: git object
`454df71144f677b1e84ed58f7a6c6951a4190f66` (`literature/km-figures-2026-08-25/`) on
`origin/literature-cache`, already extracted to the session scratchpad outside the repository;
`research/modalities/km_risk_row_detect.py` (the rule and its constants);
`research/modalities/km-risk-row-detection.json` (the committed measurement);
IPD-SURVIVAL-3's `preserve-mark-y0-y1.diff`.

* **IPD-SURVIVAL-2** re-derived 11 of 15 *verdicts* from preserved geometry and named the proximity
  clause as the residue.
* **IPD-SURVIVAL-3** closed the pixel half of that residue with `y0`/`y1` (10 of 15 figures
  proximity-re-derivable) and explicitly left the text arm open. **That result is not assumed here —
  §4.1 reproduces it from scratch and gets the same numbers.**
* What is new is the **text arm's denominator**, which no prior lane recorded and which no amount of
  `y0`/`y1` reaches.
* The blocked dependency (S6/S7: a real figure whose patient-level truth is also published,
  `EGRESS_BLOCKED`) is untouched, unretried and unsubstituted.

## 4 · Step taken, and results

### 4.1 IPD-SURVIVAL-3's result reproduces, digit for digit (`checks/01`–`checks/05`)

**Digests (`checks/01`, exit 0).** All five licensed PDFs in the local scratch cache hash to the
digests the committed census records, byte counts included — chiusole2020 `6f0b024ddaa9c657…` /
439160 B, martinbroto2020immunosarc1 `2869688dba542651…` / 529371 B, masunaga2025
`4ae16c8e3b901398…` / 1763019 B, morioka2016trabectedin `03574d05d823ecaa…` / 811863 B,
stacchiotti2013anthracycline `1df76e6b01167c77…` / 2609773 B. `ALL_MATCH True`.

**Unpatched baseline (`checks/02`, `checks/03`, exit 0).** The detector was copied to a scratch tree
**outside the repository** and run there; the repository's own file was never executed in a modified
state. Totals reproduced: **papers 5, figures 15, with_risk_row 2, without 9, undetermined 4.** With
the committed provenance string supplied on the command line, the baseline re-run is not merely
equal field by field — `diff -u` against the committed artifact is **empty** and the two files are
**byte-identical**, sha256 `b392b878bf4b5e698449d25bf4d8cc2a8632050c69af591c3f86861097c1a1af`,
50596 B. (IPD-SURVIVAL-3 reported a one-line diff only because it passed a shortened
`--page-raster-note`.)

**IPD-SURVIVAL-3's diff and its claim (`checks/04`, `checks/05`, exit 0).**
`preserve-mark-y0-y1.diff` applied cleanly to the scratch tree; the census re-ran with the same
totals. Running **IPD-SURVIVAL-3's own `rederive_proximity.py`** on **my** regenerated artifact:

> **n_figures 15 · n_proximity_rederivable 10 · n_all_flags_agree 10 · n_disagree 0 ·
> n_not_rederivable 5.**

The five blocked rows are exactly the ones it named: masunaga2025 p11, morioka2016 p1, p5, p8 (all
`undetermined`, no band geometry), **plus morioka2016 p4, arm `text`, verdict `present`, caption
"Fig. 1 Kaplan-Meier plot of progression-free survival", reason "the proximity denominator is
page.bbox[3], which the artifact does not record."** The re-derivation artifact my run produced is
**identical object-for-object** to the one IPD-SURVIVAL-3 committed
(`IS3_ARTIFACT_IDENTICAL_TO_MY_RERUN True`). **Everything in step 1 reproduces; nothing disagrees.**

### 4.2 The additive change (`record-text-arm-page-height.diff`)

The text-arm figure record now appends `"page_height_pt": round(page.bbox[3], 1)` — at the same 1 dp
as the neighbouring `tick_row_span_pt` — **after `**res`**, so it lands after every existing key of
the entry, including every key `decide()` contributes. No existing field is removed, renamed,
reordered or retyped; no threshold, tolerance, constant, matcher or clause is touched; **no clause
reads the new field**; the pixel arm is not touched at all. Twelve added lines, two of them code.

**Backward compatibility, proved the strong way (`checks/10b`, `checks/11b`, exit 0).** Strip the new
key from the regenerated document, re-serialise through the detector's own writer settings, hash:

| what was stripped | result |
|---|---|
| `page_height_pt` from the my-patch-only run | sha256 `b392b878bf4b…1c1a1af`, 50596 B — **byte-identical to the unpatched run, which is itself byte-identical to the committed artifact** |
| `page_height_pt` + `y0` + `y1` from the both-patches run (1 + 161 + 161 keys removed) | the same `b392b878bf4b…1c1a1af`, 50596 B — **byte-identical** |

Line level (`checks/13`, exit 0), committed vs both-patches regeneration: **161 `y0` + 161 `y1` +
1 `page_height_pt` inserted lines, 162 existing lines gaining only a trailing comma, 0 deletions,
0 value changes, 0 other insertions — `STRICTLY_ADDITIVE True`.** Totals, all 15 verdicts, the
`inputs` block and the whole synthetic `control` block compare identical (`checks/14`).

⚠ **A preserved failure that is also a correction to IPD-SURVIVAL-3.** My first two byte-identity
runs (`checks/10-…-FAILED-missing-trailing-newline`, `checks/11-…-FAILED-missing-trailing-newline`,
both exit 1) came out **one byte short**, because I had copied IPD-SURVIVAL-3's statement that "the
detector's own writer (`json.dump`, line 879) produces no trailing newline". It does:
`km_risk_row_detect.py:880` is `fh.write("\n")`. Consequence, measured in `checks/15`:
IPD-SURVIVAL-3's `km-risk-row-detection.REGENERATED.committed-provenance.json` is **60133 B, sha256
`93ee55f87563a1c6…`**, and my y0/y1-only regeneration is **60134 B, sha256 `acb4530d4024fa7f…`**,
with `mine[:-1] == IS3` exactly `True`. So **IPD-SURVIVAL-3's stated committed identity, and its ⚠
note about the writer, are both wrong by one trailing newline** — its post-processing step, not the
detector, dropped it. Nothing else in that lane is affected, and its `y0`/`y1` change itself is
sound. My regenerated artifact is written **by the detector itself with the committed provenance
string**, so it needs no post-processing and carries the newline.

### 4.3 Using it — morioka2016 Fig. 1's proximity clause re-derived (`checks/12`, exit 0)

`rederive_proximity_all_arms.py` re-applies the clause exactly as `decide()` states it —
`min(t.y0 for t in band) - max(t.y1 for t in bands[ref]) <= max_risk_gap` — for **both** arms, with
every constant parsed out of the source file and never retyped (`MAX_RISK_GAP` 0.25, `MIN_MARKS` 3,
`MIN_MATCHED_TICKS` 3, `MAX_MARK_WIDTH` 0.055), then re-derives the whole `present` conjunction.

> **11 of 15 figures are now proximity-re-derivable, and all 11 agree with the record on every
> candidate band — 0 proximity disagreements, 0 verdict disagreements.** The only rows left are the
> four `undetermined` ones that record no band at all.

**morioka2016 Fig. 1 — the verdict is CONFIRMED, not contradicted.** Page height 790.9 pt, so the
proximity ceiling is `0.25 × 790.9 = 197.72 pt`; the tick-label band (band 0) has bottom edge
`y1 = 664.2`. Every candidate band re-derives its recorded `near_enough_to_tick_labels` flag
identically:

| band | marks | matched ticks | median width frac | top `y0` | gap (pt) | gap / height | near enough | qualifies |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 1 | 0.1126 | 668.3 | 4.1 | 0.0052 | yes | no (marks, ticks, width) |
| 2 | 2 | 0 | 0.0379 | 678.5 | 14.3 | 0.0182 | yes | no (marks, ticks) |
| **3** | **9** | **8** | **0.0159** | **686.5** | **22.3** | **0.0282** | **yes** | **YES** |
| 4 | 9 | 8 | 0.0095 | 695.7 | 31.5 | 0.0398 | yes | yes (later; not selected) |
| 5 | 13 | 2 | 0.0560 | 708.7 | 44.5 | 0.0563 | yes | no (ticks, width) |
| 6 | 6 | 3 | 0.0718 | 717.1 | 52.9 | 0.0669 | yes | no (width) |

The re-derived `risk_row_band_index` is **3**, exactly the recorded value, and the re-derived verdict
is **`present`**, exactly the recorded verdict. Band 3 clears the proximity ceiling with a margin of
**175.43 pt** — it sits at 2.8 % of the page height below the tick labels against a 25 % ceiling, so
this verdict is nowhere near the boundary. Band 3's recorded text is
`["Trabectedin", "5", "5", "5", "3", "3", "1", "1", "1"]`, the row IPD-SURVIVAL-2 machine-matched to
the eye reading in `emc_ipd_survival.py`. **This is a confirmation, and confirmation was the expected
result; it is worth having precisely because the clause could not previously be checked at all.**

### 4.4 Are the two diffs independent, or must they be ordered? (`checks/07`, exit 0)

`git apply --check` tests each patch against the tree, not cumulatively, so it cannot answer this.
`checks/07` therefore performs a **real cumulative apply** on scratch copies of the pristine file, in
both orders:

* **A then B** (`preserve-mark-y0-y1.diff`, then mine): check1 rc 0, apply1 rc 0 → `48caaa6a035ba185…`;
  then, on the **already-patched** file, check2 rc 0, apply2 rc 0 → `b2c92e0fabf14d13…`; parses OK.
* **B then A**: check1 rc 0, apply1 rc 0 → `ff1de32644381c94…`; check2 rc 0, apply2 rc 0 →
  `b2c92e0fabf14d13…`; parses OK.
* `cmp` of the two results: **IDENTICAL.**

**The two patches are independent and commute — there is no ordering constraint.** They touch
`Token.as_dict` (line ~143) and the text-arm record append (line ~729), hunks far apart with no
shared context lines, and each still applies cleanly after the other. Either may be applied alone,
and either order gives the same file. They are also *semantically* independent: `y0`/`y1` makes the
pixel arm's clause checkable, `page_height_pt` makes the text arm's checkable; neither needs the
other. Applying **only** mine still yields a valid artifact (`checks/08`, exit 0, 50631 B), but
proximity re-derivation then covers **1** of 15 figures, not 11 — so the useful configuration is
both, and the 11/15 result requires both.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `record-text-arm-page-height.diff` (**UNAPPLIED**; `git apply --check --verbose`
  against a clean tree **exit 0**, `checks/06`); `km-risk-row-detection.REGENERATED.json` (both
  patches, written by the detector itself with the committed provenance string — no post-processing);
  `census-baseline-unpatched.json`; `proximity-clause-rederivation-both-arms.json`; scripts
  `verify_digests.py`, `strip_and_hash.py`, `rederive_proximity_all_arms.py`,
  `verify_additive_lines.py`; `checks/01`–`checks/15` including **three preserved failed attempts**
  (`02-…-FAILED-missing-sibling-module` exit 1, `10-…`/`11-…-FAILED-missing-trailing-newline` exit 1)
  and one preserved failed patch invocation (`04a-patch-p4-FAILED-wrong-strip`, exit 1). Every
  attempt has `command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`; none is omitted or
  rewritten. `checks/02`, `04`, `08`, `09` each retain the same benign pdf-parser warnings on stderr,
  identical between patched and unpatched runs.
* **Which committed artifact would be regenerated, and its identity.**
  **`research/modalities/km-risk-row-detection.json`** — and nothing else; the diff touches one
  source file and regenerates one data file. Committed today: sha256
  `b392b878bf4b5e698449d25bf4d8cc2a8632050c69af591c3f86861097c1a1af`, **50596 B**. With **both**
  diffs applied and the census regenerated from the same five digest-verified PDFs with the committed
  provenance string, the committed artifact's identity would become sha256
  `7b4731355faa820dbc5028fecdbf6c886f121639e90ba17b7c667233d1780a8c`, **60169 B** — 323 added lines,
  162 lines gaining a comma, **0 values changed**, totals and all 15 verdicts identical. With **only
  this lane's diff** applied it would become sha256
  `3bcec89ad303c027bfce1a161ede9fe4be2465ebc7b9b7756113021e3fe3565a`, **50631 B**. **The owner
  decides whether to apply. I did not — nothing was `git add`-ed, committed or pushed, and
  `scripts/preflight.sh` was not run.** The repository's `km_risk_row_detect.py` was edited in the
  working tree for the single purpose of producing the `git diff` header and then restored; it is
  back at sha256 `71ed29b707233bffb2736e89da5989e37e83758b2b81f3b6716fe9a2a80b3749` and
  `git diff --quiet` on it returns clean.
* **Validation / baseline.** The baseline is the committed artifact itself, and this lane's baseline
  re-run is byte-identical to it, so every downstream comparison is against the real committed bytes.
  Backward compatibility is proved by strip-and-re-serialise to **byte identity** (twice: my key
  alone, and my key together with IPD-SURVIVAL-3's), plus a line-level strict-superset test with zero
  violations. The rule was then re-derived with constants parsed from source. The synthetic control
  shipped inside the artifact re-ran in every execution and compared identical.
* **Provenance.** Repo `/home/user/Rare-cancers`, HEAD `673d33044…`, 2026-09-09 ~01:25–01:50 UTC,
  13 GiB free. Inputs from git object `454df7114…`, already in the local object store and already
  extracted to the session scratchpad by a prior lane; digests re-verified here before use. **No
  network call, no fetch, no GPU, no paid API, no subagent, no publication, no outreach, no git
  write, no `preflight.sh`, no edit outside this lane** (other than the transient, restored and
  verified working-tree edit described above). No licensed PDF entered the repository and none is
  retained in this lane.
* **Limitations.** ⛔ This measures **reporting practice and instrument checkability, not survival**.
  Re-derivation bounds *rule application*, not *perception*: a figure mis-segmented, mis-thresholded
  or never seen by the detector would re-derive just as cleanly, and the confirmation of morioka2016
  Fig. 1 says the rule was applied as written, **not** that the row was read correctly — that
  separate check is IPD-SURVIVAL-2's machine comparison against the eye reading. `page_height_pt` is
  recorded at 1 dp, so a re-derived text-arm gap carries ≤0.05 pt of rounding on the ceiling —
  immaterial against a 175.43 pt margin here, but a future figure could sit inside it. The four
  `undetermined` rows are still not re-derivable and are still unanswered questions, not negatives;
  no additive field reaches them, because they return before any band exists. The `marks` list is
  still capped at 16 per band (no band reaches it today; largest is 13) — a latent gap this change
  does not fix. The pixel arm's raster-crop path records `image_px` as the crop size, which this
  re-derivation takes on the code's word rather than re-measuring. The partition "which rows are the
  nine KM figures" is still human-supplied. Four chiusole2020 verdicts still rest on a page raster
  rather than the publisher's image. Nothing here cures the paper's other missing evidence, and the
  availability of these five PDFs says nothing about the sources that remain unreachable
  (seer270_2022, meisKindblom1999).
* **Stop condition (set before running, met).** Stop as soon as (i) IPD-SURVIVAL-3's 10/15, 0
  disagreements and the identity of the blocked figure either reproduce or do not — a failure to
  reproduce would have been the finding and would have stopped the lane at §4.1; (ii) the additive
  change is proved backward-compatible to byte identity or is not; (iii) morioka2016 Fig. 1's
  proximity clause is re-derived and its verdict reported confirmed or contradicted; and (iv) the
  ordering relationship between the two diffs is settled by a real cumulative apply. All met.
  Stopped: **no threshold, tolerance, matcher, floor or gate was touched**, no second census, no new
  source, no fourth proof of the same thing.

## 6 · Next credible independent work (not done here)

1. **Correct IPD-SURVIVAL-3's recorded artifact identity** for the y0/y1-only regeneration:
   `acb4530d4024fa7fd24adc14e0f1a1b2b391f9e8d857c9da6abe3bc0f2a6d916` / 60134 B, not
   `93ee55f8…` / 60133 B, and strike its ⚠ note about the writer omitting a trailing newline
   (`km_risk_row_detect.py:880` writes one). That is another lane's file; the parent records shared
   state, so it is reported, not edited.
2. **Raise or record the `[:16]` mark cap**, or record band-level `min_y0` / `max_y1` alongside the
   truncated list, so the clause stays re-derivable for a band wider than 16 marks. Latent, not
   current.
3. The four `undetermined` rows cannot be closed additively. Closing them means decoding what the
   pure-stdlib reader could not (chiusole2020's JPEGs, morioka2016's unreadable embeds) — a different
   and larger piece of work, and **`undetermined` remains the honest verdict until it is done**.
4. The correction IPD-SURVIVAL-2 flagged in `reports/W65-km-risk-row-instrument-audit.md`
   ("not runnable at this HEAD") is still uncorrected and is now falsified on a third HEAD
   (`673d33044…`). Owner's call; not edited here.
5. The genuinely blocked dependency is unchanged: a real figure whose patient-level truth is also
   published (S6/S7, `EGRESS_BLOCKED`). Nothing here substitutes for it or reopens a closed route.
