---
id: DOC-PORTFOLIO-INVESTIGATION-IPD-SURVIVAL-3-2026-09-09
title: "IPD-SURVIVAL-3 — the census reproduces again independently, and the one clause that was not re-derivable now is: the swimmer plot stays `absent`"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# IPD-SURVIVAL-3 — closing the last unre-derivable clause of the KM reporting census

⛔ This is **instrument provenance**, not survival analysis. Nothing here is medical advice and
nothing here asserts efficacy, safety, selectivity, prognosis, therapeutic window or clinical
readiness for any therapy. No curve was digitised, no IPD was reconstructed, no cohort exists, and
the closed KM/IPD pilot was not reopened. Every quantity below is a property of a published figure's
*geometry* or of a measurement record about one.

## 1 · The question

`PUB-IPD-SURVIVAL`'s headline negative — that the reachable extraskeletal myxoid chondrosarcoma
series print seven Kaplan–Meier curves with **no numbers-at-risk row**, so those curves cannot be
reconstructed — rests entirely on one committed measurement,
`research/modalities/km-risk-row-detection.json`. IPD-SURVIVAL-2 showed that measurement reproduces
exactly but found **one clause of the decision rule that a reader cannot check**: the proximity
clause (`near_enough_to_tick_labels`, `MAX_RISK_GAP`) needs each mark's `y0`/`y1`, and
`Token.as_dict` preserved only the centre `cy`. That clause is the **sole** support of the `absent`
verdict on martinbroto2020's swimmer plot. So: **does the census still reproduce under independent
re-execution, and if the missing geometry is preserved, does that verdict survive being checked?**

## 2 · Paper-level merit

A census is publishable only if a reader can re-run it *and* re-derive its rule. The reproduction
half was settled by IPD-SURVIVAL-2; this lane settles the derivation half. The value is not another
"it reproduces" — it is removing the one place where the paper would have had to say *trust the
instrument here*. That matters beyond this paper: anyone digitising a rare-disease figure inherits
this rule, and a rule with an uncheckable clause is an assertion. Patient relevance is indirect and
should be stated as such: it decides whether "this literature does not print what reconstruction
needs" is evidence or assertion. It is **not** a survival result of any kind.

## 3 · The exact evidence gap, and what distinguishes it

Named inputs, all already local — **no PDF was fetched, no network call was made**:
git object `454df71144f677b1e84ed58f7a6c6951a4190f66` (`literature/km-figures-2026-08-25/`) on
`origin/literature-cache`; `research/modalities/km_risk_row_detect.py` (the rule and its constants);
`research/modalities/km-risk-row-detection.json` (the committed measurement).

* **IPD-SURVIVAL-2** re-executed the census and re-derived 11 of 15 verdicts from preserved
  geometry. It closed by naming the proximity clause as the residue and proposing the additive fix.
  **Its central claim is not assumed here — it is re-derived from scratch in §4.1 with a comparator
  written independently of its `compare_reproduced.py`.**
* **W65** graded the real-figure arm "not runnable at this HEAD". That remains refuted; this lane
  refutes it a second time on a *different* HEAD (`90de330b…`, not `04a4e0ef…`).
* The blocked dependency (S6/S7: a real figure whose patient-level truth is also published,
  `EGRESS_BLOCKED`) is untouched, unretried and unsubstituted.

## 4 · Step taken, and results

### 4.1 Independent re-derivation of IPD-SURVIVAL-2's central claim (`checks/01`–`checks/04`)

**Digests (`checks/01`, exit 0).** The five PDFs were extracted from the git object to a scratch
directory **outside the repository** (`git archive … | tar -x`, tar exit 0 via `${PIPESTATUS}`) and
hashed independently. **5 / 5 `pdf_sha256` match, and all five `pdf_bytes` match**: chiusole2020
`6f0b024d…a788` / 439160 B, martinbroto2020immunosarc1 `2869688d…5f40f` / 529371 B, masunaga2025
`4ae16c8e…0461a` / 1763019 B, morioka2016trabectedin `03574d05…2292` / 811863 B,
stacchiotti2013anthracycline `1df76e6b…774a` / 2609773 B. `ALL_MATCH True`.
(`checks/01-digest-verify-FAILED-keyerror` preserves the first attempt, which used key `id` instead
of `source_id` and exited 1.)

**Re-execution (`checks/02`, exit 0).** `km_risk_row_detect.py` run on those inputs, unpatched,
output written into this lane only. Reproduced totals: **papers 5, figures 15, with_risk_row 2,
without 9, undetermined 4** — identical, digit for digit, to the committed `_totals`.

**Comparison (`checks/03`, `checks/04`, exit 0).** `deep_compare.py` — written here, not reused —
walks both documents recursively and is sensitive to missing keys, extra keys, **key order**, list
length, list order, type and value. Result: **0 field differences, 0 verdict differences, 15 of 15
figures compared.** The only difference anywhere is `$.inputs.page_rasters`, a provenance string
supplied on the command line. In fact a plain `diff -u` of the committed file against the unpatched
re-run is **one line long** (`checks/11`). (`checks/03` used a verdict key of `page`+`arm`, which is
not unique in chiusole2020 and compared 13 keys rather than 15; `checks/04` is the corrected rerun.
The field walk was unaffected either way. Both are preserved.)

**Nothing disagrees. IPD-SURVIVAL-2's central claim is confirmed independently**, and building on it
is justified.

### 4.2 The additive change (`preserve-mark-y0-y1.diff`)

`Token.as_dict` now appends `y0` and `y1`, rounded to 1 dp exactly as `cx`/`cy`/`w` already are,
**after** every existing key. No existing field is removed, renamed, reordered or retyped; no
threshold, tolerance, constant or clause is touched; **no clause reads the new fields**. Nine added
lines, one of them code.

**Backward compatibility, proved three ways, all on the same inputs:**

| proof | check | result |
|---|---|---|
| recursive field comparison vs the committed artifact, `y0`/`y1` the only permitted new keys | `checks/07`, exit 0 | **0 field differences, 0 verdict differences**, 15/15 figures, 322 additive keys seen |
| strip `y0`/`y1` from the regenerated document, re-serialise, hash | `checks/08`, exit 0 | **byte-identical** to the unpatched re-run — both `3bceb5d9…6dc24`, 50519 B |
| line-level superset test against the committed file | `checks/12`, exit 0 | 322 inserted `y0`/`y1` lines (= 2 × 161 mark records, synthetic control included), 161 existing lines gaining only a trailing comma, **0 deletions, 0 value changes, 0 other insertions** — `STRICTLY_ADDITIVE True` |

`cy` remains the midpoint the new fields imply to within 0.1 px across all 161 marks — that 0.1 px
is the arithmetic of rounding both endpoints to the record's existing 1 dp, not drift.
(`checks/08b…FAILED-tolerance` preserves a first run that used a 0.05 tolerance and exited 1; its
finding was the tolerance, not the data. `checks/12b…FAILED-opcode-handling` preserves a first
line-level run that mishandled unequal-length `difflib` replace opcodes and exited 1.)

`git apply --check --verbose` on the diff against a clean tree: **exit 0** (`checks/06`). The patch
was applied to the **working tree only**, and the file was restored from a byte-identical scratch
backup (`sha256 71ed29b7…3749`); `git diff --quiet -- research/modalities/km_risk_row_detect.py`
returns clean. **Nothing was `git add`-ed, committed or pushed, and `scripts/preflight.sh` was not
run.**

### 4.3 Using it — the proximity clause re-derived (`checks/09`, exit 0)

`rederive_proximity.py` re-applies the clause exactly as `decide()` states it —
`min(t.y0 for t in band) - max(t.y1 for t in bands[ref]) <= MAX_RISK_GAP * <figure height>` — with
**every constant parsed out of the source file, never retyped** (`MAX_RISK_GAP` 0.25, `MIN_MARKS` 3,
`MIN_MATCHED_TICKS` 3, `MAX_MARK_WIDTH` 0.055), and then re-derives the whole `present` conjunction.

> **10 of 15 figures are now proximity-re-derivable, and all 10 agree with the record on every
> candidate band — 0 disagreements.** Both re-derived figure verdicts match the record
> (stacchiotti2013 `present` at band 3; nine `absent`). No band's `marks` list was truncated by the
> `[:16]` cap anywhere in the artifact (largest band = 13 marks), so no re-derivation used a partial
> band.

**The martinbroto2020 swimmer plot (p6, Fig. 3, `absent`) — the verdict that rested on this clause
alone — is now independently re-derivable, and it does NOT change.** Figure height 649 px, so the
proximity ceiling is `0.25 × 649 = 162.25 px`; the tick-label band's bottom edge is `y1 = 228`. The
near-miss band 11 (5 narrow marks, 3 matched ticks, median width 0.0086 — the three clauses it
*passes*) has top edge `y0 = 607`, a gap of **379 px = 0.584 of the figure height, missing the
0.25 ceiling by 216.75 px**. It is not close to the boundary; it is more than twice over it. The
`absent` verdict stands, and it now stands on a clause a reader can check. **This is a non-change,
and it is the expected and useful result.**

The 5 not re-derivable: 4 `undetermined` rows that return before any band is recorded (unchanged
from IPD-SURVIVAL-2), **plus one this lane newly identifies** — morioka2016 Fig. 1, the **text
arm**, whose proximity denominator is `page.bbox[3]` and is *not* recorded in the artifact. Adding
`y0`/`y1` does not reach it. That is reported as not re-derivable, **not** as agreement; it is the
next additive step, and it is not taken here.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `preserve-mark-y0-y1.diff` (**unapplied**, `git apply --check` exit 0);
  `km-risk-row-detection.REGENERATED.json` and
  `km-risk-row-detection.REGENERATED.committed-provenance.json` (the same document with the
  committed `inputs.page_rasters` string restored — the file the owner would actually commit);
  `census-baseline-unpatched.json`; `diff-baseline-vs-committed.json`,
  `diff-regenerated-vs-committed.json`, `proximity-clause-rederivation.json`; scripts
  `deep_compare.py`, `strip_and_hash.py`, `rederive_proximity.py`, `verify_additive_lines.py`;
  `checks/01`–`checks/12` plus two preserved failed attempts, each with `command.txt`,
  `stdout.txt`, `stderr.txt`, `exit_code.txt`. **Twelve attempts exited 0, three exited 1; none is
  omitted or rewritten.** `checks/02` and `checks/05` each retain the same four benign pdf-parser
  warnings on stderr ("Cannot set non-stroke color: 2 components specified"), identical between the
  unpatched and patched runs.
* **Which committed artifact would be regenerated, and its identity.**
  **`research/modalities/km-risk-row-detection.json`** — and nothing else; the diff touches one
  source file and regenerates one data file. Committed today: sha256
  `b392b878bf4b5e698449d25bf4d8cc2a8632050c69af591c3f86861097c1a1af`, 50596 B. After the change,
  regenerated from the same five digest-verified PDFs with the committed provenance string: sha256
  `93ee55f87563a1c60867490052565a54c683b72adaf00b1f1b27040584af169a`, 60133 B — 322 added lines,
  161 lines gaining a comma, **0 values changed**, totals and all 15 verdicts identical.
  ⚠ The regenerated file has no trailing newline; the detector's own writer (`json.dump`, line 879)
  produces none either, so the owner should regenerate through the script rather than copy this file
  if the committed file's trailing byte matters. **The owner decides whether to apply. I did not.**
* **Validation / baseline.** The baseline is the committed artifact itself, compared four ways:
  recursive field walk (0 differences), one-line textual diff of the unpatched re-run, byte-identical
  strip-and-hash, and a line-level strict-superset test. Independently, the rule was re-derived from
  preserved geometry with constants parsed from source. The synthetic control shipped inside the
  artifact re-ran as part of both executions and compared identical.
* **Provenance.** Repo `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`, HEAD
  `90de330ba28dfe098159c4860a00fe03709dc3ea`, 2026-09-09 ~00:52–01:12 UTC, 13 GiB free. Inputs from
  git object `454df7114…` already in the local object store. **No network call, no fetch, no GPU, no
  paid API, no subagent, no publication, no outreach, no git write, no `preflight.sh`.** The five
  licensed PDFs were extracted to the session scratchpad **outside the repository**; none entered
  the repository and none is retained in this lane. They remain in the scratchpad, uncommitted.
* **Limitations.** ⛔ This measures **reporting practice and instrument checkability, not survival**.
  Re-derivation bounds *rule application*, not *perception*: a figure mis-segmented or never seen by
  the detector would re-derive just as cleanly. `y0`/`y1` are recorded at 1 dp, so a re-derived gap
  carries ≤0.1 px of rounding — immaterial against margins of 6.75–216.75 px here, but a future
  figure could sit inside it. The `marks` list is still capped at 16 per band; no band reaches that
  today, but a wider band would make its own proximity clause un-re-derivable again, and this change
  does not fix that. The text arm's proximity denominator is still unrecorded (§4.3). The four
  `undetermined` rows remain unanswered questions, not negatives. The partition "which rows are the
  nine KM figures" is still human-supplied. Four chiusole2020 verdicts still rest on a page raster
  rather than the publisher's image. Nothing here cures the paper's other missing evidence, and the
  availability of these five PDFs says nothing about the sources that remain unreachable
  (seer270_2022, meisKindblom1999).
* **Stop condition (set before running, met).** Stop as soon as (i) the totals and the field
  comparison either reproduce or disagree — a disagreement would have been the finding and would
  have stopped the lane at §4.1; (ii) the additive change is proved backward-compatible or is not;
  and (iii) the proximity clause is re-derived for every figure whose geometry supports it, with the
  martinbroto verdict reported changed or unchanged. All met. Stopped: no threshold touched, no
  second census, no new source, no third proof of the same thing.

## 6 · Next credible independent work (not done here)

1. **Record the text arm's proximity denominator** (`page.bbox[3]`, or the resolved
   `max_risk_gap` in px) in the figure entry. It is the same shape of additive change and would take
   proximity re-derivation from 10/15 to 11/15 — every figure that has band geometry at all.
2. **Raise or record the `[:16]` mark cap**, or record band-level `min_y0` / `max_y1` alongside the
   truncated list, so the clause stays re-derivable for a band wider than 16 marks. No such band
   exists today; this is a latent gap, not a current one.
3. The correction IPD-SURVIVAL-2 flagged in `reports/W65-km-risk-row-instrument-audit.md`
   ("not runnable at this HEAD") is still uncorrected and is now falsified on a second HEAD. Owner's
   call; not edited here.
4. The genuinely blocked dependency is unchanged: a real figure whose patient-level truth is also
   published (S6/S7, `EGRESS_BLOCKED`). Nothing here substitutes for it or reopens a closed route.
