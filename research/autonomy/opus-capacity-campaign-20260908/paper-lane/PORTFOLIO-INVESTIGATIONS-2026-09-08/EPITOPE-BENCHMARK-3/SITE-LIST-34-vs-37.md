---
id: DOC-EPITOPE-BENCHMARK-3-SITE-LIST
title: "Every site quoting 34 or 37 for the Wilson sensitivity-0.9 requirement"
level: L4
kind: site-census
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Site census — the Wilson n-required value at sensitivity 0.9

Repository `/home/user/Rare-cancers`, searched 2026-09-09 with `grep -rn --exclude-dir=.git` on
three independent patterns: the literal ladder `93 */ *78 */ *60`, the JSON key form
`"0\.9" *: *(34|37)`, and `wilson`. Only sites quoting **this** quantity are listed; incidental
occurrences of the integers 34 and 37 elsewhere in the repository (e.g. the 34-allele screen in
`pinned-figures.json`) are **not** this quantity and are excluded, with the exclusions named below.

## A · Sites quoting **37** (the value the diff supersedes)

| # | file | line | form | status after the diff |
|---|---|---|---|---|
| A1 | `.../EPITOPE-BENCHMARK/validated-epitope-counts.json` | 524 | `"0.9": 37` | **changed to 34** by the diff (derived artifact) |
| A2 | `.../EPITOPE-BENCHMARK/check_consistency.py` | 14 | `{"0.5":93,"0.7":78,"0.8":60,"0.9":37}` — **the pin** | **changed to 34** by the diff |
| A3 | `.../EPITOPE-BENCHMARK/check_consistency.py` | 28 | printed banner `Wilson 93/78/60/37` | **changed to 93/78/60/34** by the diff |
| A4 | `.../EPITOPE-BENCHMARK/FINDING.md` | 115 | prose "at sensitivity 0.9 it returns **37**" | **rewritten**, superseded value preserved with its origin |
| A5 | `.../EPITOPE-BENCHMARK/FINDING.md` | 123 | table row `\| 0.9 \| 37 \| **15** \| 22 \|` | **changed to `\| 0.9 \| 34 \| **15** \| 19 \|`** |
| A6 | `.../EPITOPE-BENCHMARK/FINDING.md` | 179 | prose "differs only at sensitivity 0.9 (37 vs 34)" | **rewritten**, arbitration recorded |
| A7 | `.../EPITOPE-BENCHMARK/PARENT-ADJUDICATION-34-vs-37.md` | 25–28, title | the arbitration itself | **NOT changed** — this is the record that supersedes 37; editing it would erase the history |
| A8 | `.../EPITOPE-BENCHMARK/checks/06-consistency-assertions/stdout.txt` | 2 | `Wilson 93/78/60/37` | **NOT changed** — retained execution evidence of a real past run; a check log is never retrofitted |
| A9 | `.../EPITOPE-BENCHMARK-2/checks/05-check-consistency-unmodified/stdout.txt` | 2 | `Wilson 93/78/60/37` | **NOT changed** — same reason, and another lane's evidence |
| A10 | `.../EPITOPE-BENCHMARK-2/FINDING.md` | 130 | quotes that run's banner | **NOT changed** — another lane's finding, and a true quotation of what that run printed |
| A11 | `.../EPITOPE-BENCHMARK-2/FINDING.md` | 159 | "pins `\"0.9\":37`, which the parent arbitration superseded" | **NOT changed** — already correct; it is the referral that opened this lane |

## B · Sites quoting **34** (already correct; the diff does not touch them)

| # | file | line | form |
|---|---|---|---|
| B1 | `.../VACCINE-PATH-2/FINDING.md` | 82 | `93 / 78 / 60 / **34**` with all three conventions tabulated |
| B2 | `.../VACCINE-PATH-2/b1-exemplar-admissibility.json` | 136, 142 | `"0.9": 34` (twice: two convention blocks) |
| B3 | `.../VACCINE-PATH-2/b1_exemplar_admissibility.py` | 154 | `wilson_reproduction_note` string |
| B4 | `.../VACCINE-PATH-2/checks/05-b1-exemplar-admissibility-corrected/stdout.txt` | 136, 142, 151 | that run's output |
| B5 | `.../EPITOPE-BENCHMARK/PARENT-ADJUDICATION-34-vs-37.md` | 25–28 | the arbitration table, `0.9 → 34` |

## C · Sites checked and found **NOT** to carry this quantity

| where | result |
|---|---|
| `research/manuscripts/pinned-figures.json` | **no entry** for the Wilson sensitivity ladder. The `34` at lines 1960/1970/1971 is the **34-allele screen** panel size — a different quantity. The `37.7`/`242.20` hits are gate timings and mass values. **This quantity is unpinned in `pinned-figures.json`.** |
| `research/manuscripts/neoantigen/emc-vaccine-development-path.md` (PUB-VACCINE-PATH) | **the ladder is not printed in the manuscript.** Its Wilson intervals were **withdrawn** (see lines 417 and 1564: *"Earlier versions printed Wilson 95% …"*, and the pooling objection). So no manuscript sentence quotes 34 **or** 37, and the diff changes nothing a reader of the paper sees. |
| `systems/graph/*.json`, `systems/views/` | no occurrence of this ladder. |
| any other manuscript under `research/manuscripts/` | no occurrence of `93 / 78 / 60`. |

## D · Consequence for the diff's blast radius

Every site the diff changes is inside **EPITOPE-BENCHMARK**. No other lane, no manuscript, no graph
entry, no `pinned-figures.json` entry and no generated view quotes this quantity at 37. The four
retained execution logs (A8, A9) and the arbitration record (A7) deliberately keep the old value,
because they are records of what actually ran and what was actually decided.
