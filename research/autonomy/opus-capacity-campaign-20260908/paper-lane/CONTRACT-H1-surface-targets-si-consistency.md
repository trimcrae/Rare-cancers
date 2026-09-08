# H1 — paper-level contract, recorded BEFORE launch

`date -u` **Tue Sep  8 09:20:40 UTC 2026**. HEAD **e4916072d312f569049b469de72d5622ce5fddc8**. Same session, sole parent/launcher, `claude-opus-5` medium, existing
saved first-party subscription, no overage, no credits, no paid fallback, deadline
2026-09-09T02:37:19Z. Disk 20 GiB free (floor 10 GiB).

## Selected paper

`research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` — the supplementary file of
`PUB-SURFACE-TARGETS`, drafted and unpublished. The main text was corrected at `d2ea5a7e` (G1).

## The exact issue — parent-verified, and it corrects G1

G1 disclosed the GPL3290 processing confound in the main text and changed its CSPG4 passage from
"Two candidate explanations are live and neither is settled here" to "**Three** candidate explanations
… **none** is settled". G1 left the SI's parallel passage untouched, reporting that SI line 353
"refers to the *platform-disagreement* section, not the CSPG4 discordance".

**That reading is wrong, and I verified it at the HEAD above.** The SI passage reads:

> "Two explanations for the platform disagreement are live and neither is settled. The GPL3290
> comparator arm is 6 samples with an unusually high CSPG4 mean, and dermatofibrosarcoma protuberans
> is a dermal fibroblastic tumour while CSPG4 is a well-known melanocytic and pericytic antigen…
> The sequencing row rests on one peak and 4 libraries…"

Those are **the same two explanations**, about **the same CSPG4 discordance**, in the same order as
the main text's pre-G1 wording. It is a parallel statement of one argument, not a different one.

**Measured consequences:**
- The SI says **two** live explanations where the main text now says **three**.
- `grep -c 'CRH|UHR'` over the SI → **0**. The confound is disclosed in the main text and **nowhere**
  in the supplement.
- The main text now states at line 496 that every GPL3290 contrast "rests on a partly mismatched
  comparison that this study neither reprocessed nor excluded" — which the SI's own account of the
  same contrast does not carry.

⭐ **So the paper's supplement now contradicts its main text on a disclosed confound.** A reader of the
supplement alone gets the uncorrected two-explanation account.

## Finite acceptance

1. Bring the SI passage into agreement with the corrected main text: **three** live explanations, none
   settled, with the processing mismatch stated as the third — **in place**, not as an end-note.
2. **Quote the annotations from the committed artifact** `research/modalities/emc-expression-panels.json`
   (CRH/mRNA for the ten EMC and three DFSP arrays; UHR/total-RNA for the three GIST arrays). Infer
   no annotation. Cross-reference the main text's Methods rather than restating it at length.
3. **⛔ NO RECOMPUTATION and NO NEW NUMBER.** The sensitivity analysis (recomputing GPL3290 contrasts
   against the three DFSP arrays alone) stays **out of scope and undone**; say so if the SI needs it
   said. Run, edit or invoke no analysis module.
4. **No overclaim.** The mismatch does not show any reported contrast is wrong. Both existing SI
   explanations survive **verbatim**; only the counting words and the added third clause change.
5. **⛔ Do not edit the main manuscript.** It is settled at `d2ea5a7e`. Edits are confined to
   `emc-surface-target-landscape-si.md`. If you find a main-text problem, **report it, do not fix it**.
6. Linters run and reported honestly with exit codes. ⛔ **A tripped gate is a finding to report —
   never a reason to weaken, relax, reorder or edit a gate.** Two pre-existing failures are **not
   yours**: `lint_citations` exit 1 repo-wide, and `lint_consistency` exit 1 on the separately owned
   MTAP/PRMT5 `2.102` blocker. Establish baselines and attribute honestly.
   ⚠ The main text sits at **4,994 of 5,000 words** — 6 words of headroom. Do not spend it; the SI is
   a separate file and is not what the main cap measures, so keep every word of this edit in the SI.

## Restrictions

**No network call.** All inputs are committed. **No git write whatsoever** — no commit, add, stash,
checkout or restore; read-only git only, and baselines by `cp` of your own copy or
`git show HEAD:<path>`, never by stashing the shared tree. No graph edit, no PR, no publication, no
`scripts/preflight.sh`. There is no wet lab: no EMC efficacy, safety, selectivity or
clinical-readiness claim. Invent no fact, source, patient datum or result. If a request is refused by
content policy, stop that branch, record the refusal verbatim, never route around it.

## Retention — CLAUDE.md §8 applies

Under `/tmp/claude-0/h1-retained/`: pre-edit SI (copied before the first edit), post-edit SI, unified
diff, every linter's stdout **and** stderr with exit code echoed. **Delete nothing.** The parent
preserves the original child JSONL and parses the served model from it. Nothing is re-run to recreate
evidence.

## Stop conditions

Stop if the SI passage is already consistent on reading; if the artifact lacks the quoted annotations;
if consistency cannot be reached without deleting a hedge; if any step would need a network call, a
recomputation or a guard change; or at ~40 tool calls / ~40 minutes.
