---
id: DOC-PORTFOLIO-INVESTIGATION-STRATEGY-ARCH-3-20260909
title: "Portfolio investigation — STRATEGY-ARCH-3: the depth result reproduces, one label flip reverses it at n=4, and the missing eligibility text was in the checkout all along"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: STRATEGY-ARCH-3
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
endpoint: PUB-STRATEGY-ARCH
---

# STRATEGY-ARCH-3 — from a finding to something the paper can act on

⛔ Not medical advice, not a trial-matching service. Everything below is a statement about
registry text on the retrieval dates recorded in the cited deposits. No patient, referral,
enrolment, treatment or outcome is involved, and **nothing here says any trial is or is not
reachable by any real patient**. No efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim is made or implied, and none could be made from this kind of evidence.
**The cost of a false hit remains UNKNOWN, not zero**; the prior lane's no-go on it stands
unweakened.

## 1 · The question

STRATEGY-ARCH-2 measured that giving a string screen the posted eligibility criterion **lowers**
precision, and concluded that the manuscript's §6.2 ("registries could index eligibility text")
and §6.3 ("read criteria rather than match strings") are in measurable tension. That result rests
on n = 4.

**Question.** Does that table reproduce from the committed deposit under independent code; **how
many ground-truth label flips would reverse the direction of the precision loss**; does the
eligibility text the prior lane declared unavailable exist anywhere in this checkout; and can the
tension be stated in the manuscript's own voice without recommending either remedy?

## 2 · Paper-level merit

A methodological recommendation that a tool-builder will implement should not rest on an
unstated-fragility n = 4, and a paper should not carry an evidence limit that is false. Both are
patient-relevant in the ordinary way this endpoint is: the recommendations tell people how to
build the thing a patient searches with. Establishing the fragility number, and correcting a
wrong "the text does not exist" limit, is the difference between a finding and something the
paper owner can act on. It needs no bench and is falsifiable from committed data.

## 3 · The evidence gap this closes

STRATEGY-ARCH-2 stated its own limitation as: *"the four FET-deposit records flagged
`eligibility_text_retrieved: true` store a boolean and an assessment, not the text, so they cannot
be scored at depth B or C"*, and its stop condition made enlarging the set conditional on a
CI-routed `clinicaltrials.gov` fetch. It also gave no fragility analysis. Nothing was fetched
here; **that limitation was tested against the checkout rather than accepted.**

## 4 · Step 1 — re-derivation (done first)

`depth_fragility_and_extension.py` rebuilds the nine-row ablation from
`research/literature/emc-trial-reachability-adjudication-2026-08-09.json` with its own scoring
code — it imports neither `screen_depth_ablation.py` nor `keyword_screen_benchmark.py` — and
compares every cell against `STRATEGY-ARCH-2/screen-depth-ablation.json`.

**All nine rows, all seven fields each, reproduce exactly. MISMATCHES: 0**
(`checks/01-rederive-fragility-extend/`, exit 0). Histology A undefined / B 0.0000 / C 0.0000;
molecular 0.6667 → 0.6667 → 0.5000; union 0.6667 → 0.5000 → 0.3333. Ground-truth labels are
re-checked against the deposit's own verdict wording at run time; the script exits 2 on mismatch.

## 5 · Step 2 — fragility: **the n = 4 union result is one flip from reversing**

Every subset of ground-truth label flips was enumerated and the table re-scored.

| lexicon | direction as published (A → B) | minimum flips to remove it | which |
|---|---|---|---|
| union | 0.6667 → 0.5000 (loss) | **1** | **NCT07188532** → A 0.6667, B **0.7500**: loss **REVERSED** |
| molecular | 0.6667 → 0.6667 (no loss) | 1 | any single record; equality survives as equality |
| histology | undefined → 0.0000 | 1 | any single record leaves A undefined; no A/B comparison exists |

**This must be reported as such.** The published union precision loss — the plain refutation
STRATEGY-ARCH-2 rested on — is reversed by flipping **one** label, and the label that does it is
**NCT07188532**, the very record the whole finding turns on. At n = 4 the result is maximally
fragile in the direction that matters.

The histology row is a different kind of claim and does not carry this exposure: at depth A the
screen never fires, so there is no precision to lose. What is measured there is that the screen's
**only hit at any depth is a refusal** — a single-record statement, not a rate.

## 6 · Step 3 — the eligibility text **does** exist in this checkout

STRATEGY-ARCH-2's limitation is **wrong, and this lane corrects it.** The fetched
ClinicalTrials.gov payloads are committed to the git ref **`origin/literature-cache`**, already in
this clone (`git ls-tree -r origin/literature-cache`, exit 0, 72 207 paths; **no network**,
nothing re-probed). `eligibilityModule.eligibilityCriteria` was read from the per-record payload
for **7 of the 8** benchmark records:

| NCT | payload path in `origin/literature-cache` | criteria chars | orphaned `>` |
|---|---|---|---|
| NCT06571734 | `literature/ct-confirm-four-candidates-2026-08-09/ct_nct06571734_zanzalintinib.txt` | 14080 | 9 |
| NCT04151342 | `literature/ct-confirm-four-candidates-2026-08-09/ct_nct04151342_carma.txt` | 826 | 0 |
| NCT06094101 | `literature/ct-confirm-four-candidates-2026-08-09/ct_nct06094101_pervision.txt` | 5664 | 5 |
| NCT07188532 | `literature/ct-confirm-four-candidates-2026-08-09/ct_nct07188532_adaptive_rt.txt` | 1807 | 1 |
| NCT05918640 | `literature/ct-reverify-c3b-2026-08-07/ct_nct05918640_lurbi_fet.txt` | 5090 | 3 |
| NCT05275426 | `literature/ct-reverify-c3b-2026-08-07/ct_nct05275426_ly2880070.txt` | 4120 | 1 |
| NCT07328425 | `literature/ct-reverify-c3b-2026-08-07/ct_nct07328425_dsrct.txt` | 3470 | 0 |
| **NCT07695311** | **none — no per-record payload in the ref** | — | — |

**That single absence is the decisive remaining limit**, and it is one record, not four.

### Enlarged table — n = 7, full posted criteria (not one quoted sentence)

| lexicon | depth | n | TP | FP | TN | FN | precision | recall |
|---|---|---|---|---|---|---|---|---|
| histology | A index only | 7 | 0 | 0 | 3 | 4 | undefined (never fires) | 0.0000 |
| histology | B index + criteria | 7 | 0 | **1** | 2 | 4 | **0.0000** | 0.0000 |
| histology | C criteria only | 7 | 0 | 1 | 2 | 4 | 0.0000 | 0.0000 |
| molecular | A index only | 7 | 3 | 1 | 2 | 1 | **0.7500** | 0.7500 |
| molecular | B index + criteria | 7 | 4 | 2 | 1 | 0 | **0.6667** | **1.0000** |
| molecular | C criteria only | 7 | 3 | 2 | 1 | 1 | 0.6000 | 0.7500 |
| union | A index only | 7 | 3 | 1 | 2 | 1 | **0.7500** | 0.7500 |
| union | B index + criteria | 7 | 4 | 3 | 0 | 0 | **0.5714** | 1.0000 |
| union | C criteria only | 7 | 3 | 3 | 0 | 1 | 0.5000 | 0.7500 |

Four things follow, and two of them cut against the prior lane's framing:

1. **The direction survives and widens its base.** Depth B precision falls for both defined
   lexicons — molecular 0.7500 → 0.6667, union 0.7500 → 0.5714 — where at n = 4 the molecular
   lexicon was flat. The stated criterion is refuted on the enlarged set too.
2. **Fragility improves but is still small: minimum 2 flips** for the union at n = 7 (1 for
   molecular; histology has no defined A). Two flips out of seven labels is not a comfortable
   margin, and it is reported rather than managed.
3. **The histology finding is unchanged and is the robust one.** Over seven records the
   histology-name screen still never fires on the index, and across the full posted criteria it
   fires exactly once, on the refusal NCT07188532 — precision 0.0000 at both denominators.
4. **Depth B buys recall while it costs precision** (molecular 0.7500 → **1.0000**). This is a
   genuine correction to a one-sided reading: reading criteria recovers an admitting record the
   index misses, and adds false positives at the same time. It is a trade, not a pure loss, and
   the proposed manuscript wording says so rather than reporting only the harm.

## 7 · Step 4 — the unapplied diff

`UNAPPLIED-emc-trial-reachability-section6-tension.diff` — one hunk against
`research/manuscripts/care-delivery/emc-trial-reachability.md`, inserting a dated correction after
§6 item 3. It **states the tension and recommends neither remedy** ("This paper does not resolve
which recommendation should give way"), names both denominators, names the one-flip fragility at
n = 4 and the two-flip figure at n = 7, and **preserves the superseded §6.2 wording verbatim
inside the dated correction** ("Item 2 above read, in full: …") rather than deleting it.

* `git apply --check` → **exit 0** (`checks/02-git-apply-check/`).
* **Real cumulative apply**, because `git apply --check` is not cumulative: a scratch git repo
  holding the committed manuscript, STRATEGY-ARCH-2's §4 diff applied **first** (exit 0), then
  this lane's §6 diff (exit 0, hunk #1 at offset +13); both hunks verified present in the
  resulting file (`arch2_hunk=1`, `arch3_hunk=1`), `CUMULATIVE_EXIT=0`
  (`checks/04-cumulative-apply-scratch-rerun/`, exit 0).
* **Neither diff was applied.** The working tree's manuscript is unmodified —
  `git status --porcelain` on it is empty after every check. No `git add`, commit, push or
  preflight was run.

## 8 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `depth-fragility-and-extension.json` — the re-derived nine rows with a per-cell
  comparison against the prior JSON, the full flip enumeration for all three lexicons, the payload
  search result per record, and the enlarged nine-row table with its own fragility. Generated by
  `depth_fragility_and_extension.py`. Plus the unapplied diff.
* **Validation / baseline.** The baseline is STRATEGY-ARCH-2's own published table, compared cell
  by cell by independent code; a non-reproducing cell would have stopped the script (`return 3`)
  before anything was built on it. Ground truth is re-validated against the deposits' own verdict
  wording at run time.
* **Provenance.** `research/literature/emc-trial-reachability-adjudication-2026-08-09.json`,
  `research/literature/fet-fusion-trial-eligibility-2026-08-07.json`,
  `STRATEGY-ARCH-2/screen-depth-ablation.json`, `PUB-STRATEGY-ARCH/keyword-screen-benchmark.json`,
  and payloads read from the local git ref `origin/literature-cache`. **Nothing was fetched, no
  network egress was attempted, no registry was re-probed, no refusal was encountered, reworded,
  model-switched or proxied around.** The recorded clinicaltrials.gov closure was not re-tested.
  Every write is inside this lane directory.
* **Limitations — stated, not managed.**
  * **n = 7, and the union direction is 2 label flips from disappearing; at n = 4 it is 1.**
    Neither set is a sample of the registry and no interval is quoted.
  * **Transport damage is present in the payloads.** `scripts/lit_fetch_urls.py` `strip_html()`
    deleted spans from `<` to the next `>` in free-text criteria; the criteria used here carry
    0–9 orphaned `>` each (per-record counts above). Deleted text can only **remove** matchable
    string, so on a refusing record it can only remove false positives: the histology false
    positive on NCT07188532 is robust to it, and the depth-B precision losses are, if anything,
    understated. This direction is asserted from the defect's mechanism, not measured.
  * **NCT07695311 has no per-record payload in the ref** and is excluded from the enlarged table,
    so the enlarged set is 7 of the 8 benchmark records.
  * The lexicons are the prior lanes' a-priori lists, unchanged; a different lexicon re-scores
    everything, which is why per-record hits are published.
  * A registry record is not a protocol; "admits"/"refuses" is a reading of posted criteria on a
    retrieval date, never a trial team's decision, and never a statement about a real patient.
* **Stop condition.** Stop. The three questions are answered decisively: the table reproduces
  (0 mismatches), the n = 4 headline is one flip from reversing, and the text exists for 7 of 8.
  The only way past 7 is a payload for NCT07695311, which this sandbox cannot fetch — and **do
  not** manufacture one by paraphrasing an assessment. The diff is the paper owner's decision;
  this lane owns none of those files and applied nothing.

## 9 · Checks

| dir | what | exit |
|---|---|---|
| `checks/01-rederive-fragility-extend/` | re-derivation, fragility, payload search, enlarged table | 0 |
| `checks/02-git-apply-check/` | `git apply --check` on this lane's diff | 0 |
| `checks/03-cumulative-apply-scratch/` | first cumulative-apply attempt; **exit code UNRECORDED** — my wrapper's `exit` inside `{ }` killed the shell before it was written. Preserved unaltered with `NOTE.txt`; **not** back-filled from stdout | UNRECORDED |
| `checks/04-cumulative-apply-scratch-rerun/` | same run without the `exit`; both diffs applied in order on a scratch copy | 0 |

## 10 · Resource problem encountered, reported not worked around

While writing this file the container root filesystem reached **100 % (1.4 MB free)** and a write
failed with ENOSPC. **No campaign task evidence directory was touched.** The only files deleted
were four scratch copies this lane itself created minutes earlier under the session scratchpad
(`cumul/`, `cumul2/`, `work/`, `orig.md`, `new.md` — ~570 KB total), whose entire content is
reproduced in `checks/03-…`, `checks/04-…` and the diff. The shared scratchpad still holds ~4.4 GB
belonging to other work (`s4` 1.2 G, `headtree` 783 M, `pert` 729 M, `head-clone` 729 M, `head`
665 M, `ctg-cache-216bd1b5` 151 M); **none of it was inspected for deletion or deleted**, and the
disk floor is reported here as an open resource problem for the coordinator rather than resolved
by freeing someone else's space.
