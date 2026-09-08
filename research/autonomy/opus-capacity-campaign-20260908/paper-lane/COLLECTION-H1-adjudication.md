# H1 — collection and adjudication against `CONTRACT-H1-surface-targets-si-consistency.md`

Collected 2026-09-08 09:24–09:27 UTC from the retained originals. No re-run, no restart, no re-audit.

## Child identity — from the transcript

| item | measured |
|---|---|
| child | `a44b7543b77ae627f` |
| original JSONL | `H1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a44b7543b77ae627f.jsonl`, **173,674 B**, sha256 `4eaa83d27d56736498d69fca83aed3f230c2dcebdcdc58fc380ee24affccfe43`, `cmp`-identical at copy |
| model strings | **37 × `claude-opus-5`, 0 others** |
| tool pairs | **18 / 18** |
| span | 09:21:05Z → 09:23:55Z (~2 m 50 s) |

⚠ **Third consecutive undercount.** H1 self-reported "14 tool calls"; the transcript holds **18**
(E1: 18/37, G1: 13/21). The transcript is authoritative. Bounds ~40/~40 met.

## Verification

| copy | sha256 |
|---|---|
| `git show HEAD:…-si.md` (read-only baseline) | `f3658018…1f23` |
| retained `BEFORE.md` | `f3658018…1f23` — identical |
| working tree | `55ab4f1a…f0a1` |
| retained `AFTER.md` | `55ab4f1a…f0a1` — identical |

## Acceptance, adjudicated

1. **SI reconciled with the main text — MET.** Line 353 now reads "**Three** explanations for the
   platform disagreement are live and **none** is settled", matching the main text's three-explanation
   account. Corrected in place, no end-note.
2. **Annotations quoted from the committed artifact — MET.** `grep -c 'CRH|UHR'` over the SI: **0
   before → 3 after**. H1 confirmed the 13/3 split (ten EMC + three DFSP on CRH/mRNA; three GIST on
   UHR/total-RNA) directly in `emc-expression-panels.json`, and cross-referenced the main text's
   Methods rather than restating them at length.
3. **No recomputation, no new number — MET.** No analysis module run, and the SI now says the undone
   work plainly: "No reprocessing was performed and no sensitivity analysis recomputing the GPL3290
   contrasts against the three dermatofibrosarcoma protuberans arrays alone was run, here or elsewhere
   in this study, so the mismatch is disclosed rather than excluded."
4. **No overclaim; both original explanations verbatim — MET, parent-checked independently.** I ran a
   whitespace-normalised substring test for each original explanation against `BEFORE.md` and the
   committed file: comparator-arm **True/True**, sequencing-row **True/True**. The six apparent
   deletions in the diff are the **re-wrapped paragraph**, not content removal. The new clause states
   the mismatch "does not show the reported contrast to be wrong."
5. **Main text untouched — MET.** `git diff --stat` for `emc-surface-target-landscape.md` returns
   **0 lines**. The 6-word cap headroom was not spent; main text remains **4,994 / 5,000**. The SI is
   a separate file and is not what the main cap measures.
6. **Linters honest — MET.** `submission_metrics`, `lint_style`, `lint_claims`,
   `lint_submission_residue`, `lint_asymmetry` all **exit 0**. `lint_consistency` **exit 1** and
   `lint_citations` **exit 1** are pre-existing: the consistency stdout is **byte-identical** to H1's
   own cp-based pre-edit baseline (`cmp` clean), its sole ERROR being the separately owned MTAP/PRMT5
   `2.102` blocker. No gate weakened, relaxed, reordered or edited.
7. **No network, no git write, nothing deleted — MET.** H1 used read-only git only and, per
   CLAUDE.md §8, deleted nothing including its own scratch. `submission_metrics.py` rewrote
   `submission-metrics.json` with identical content, so it does not appear in `git status`.

## What this closes, and what it does not

**Closes:** the contradiction between the supplement and the corrected main text. A reader of the
supplement alone no longer gets the uncorrected two-explanation account.

**Does not close — and is now stated in both files:** the sensitivity analysis recomputing GPL3290
contrasts against the three DFSP arrays alone is **undone**. It remains a genuine, separately ownable
next step. **This is not publication acceptance**; the main text also sits 6 words under its cap.

## Retention status — no cleanup performed

`/tmp/claude-0/h1-retained/` **is intact and has NOT been deleted.** Under CLAUDE.md §8 it stays until
a directory-specific receipt verifies it. The in-repo copy is `H1-executed-artifacts/` with its own
manifest. The eleven older sets and this one are all preserved; 20 GiB free, floor 10 GiB.
