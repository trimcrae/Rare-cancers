# G1 — paper-level contract, recorded BEFORE launch

`date -u` **Tue Sep  8 09:07:01 UTC 2026**. HEAD **9197478061f9757e63463732b61e9497867a1b2c**. Same session, sole parent/launcher, `claude-opus-5` medium, existing
saved first-party subscription, no overage, no credits, no paid fallback, deadline
2026-09-09T02:37:19Z. Disk 20 GiB free (floor 10 GiB).

## Selected paper

`research/manuscripts/surface-targets/emc-surface-target-landscape.md` — endpoint
`PUB-SURFACE-TARGETS`, state `drafted`, **unpublished**. `submission_metrics.py`: BJC-Article,
main **4,755 w of 5,000**, abstract **194 w of 200**, 6 display items of 8, 18 refs of 80.
Reviews on file: `…-peer-review-2026-08-10.md`, `…-review-response-2026-08-10.md`.
Not a held or frozen lane: not W25/GSE243553, not NR4A Perspective or P6, not the ASO/RNA frozen
assets, not the repurposing paper (E1, closed), not MTAP/PRMT5 (F1, closed with blockers).

## The exact unfinished substantive issue — parent-verified in the committed tree

The 2026-08-10 peer review raises as a **major point**:

> "**Half the GPL3290 comparator arm was not processed like the EMC arm, and the confound is not
> disclosed.** … the ten EMC arrays and the three dermatofibrosarcoma protuberans arrays were
> hybridised against a 'CRH' reference and are mRNA, while the three gastrointestinal stromal tumour
> arrays are total RNA against a 'UHR' reference. … It affects all 78 GPL3290 gene contrasts, the
> +0.599 route-panel score that disagrees with GPL6244, and the CSPG4 discordance for which the paper
> offers two explanations and not this one."

The review response says this was **applied**: "Methods now disclose the mismatch in its own
paragraph, Table 2 carries it … as the third live explanation for the CSPG4 platform disagreement in
Results and Note N3."

**Measured by me at the HEAD above:**
- `grep -i 'CRH|UHR|reference channel|total RNA'` over `emc-surface-target-landscape.md` → **no
  CRH, no UHR, no total-RNA disclosure anywhere**; the only near hit is a generic "relative to the
  reference pool" line.
- Same grep over `emc-surface-target-landscape-si.md` → **absent there too**. `Note N3` occurs in
  **no** manuscript file; only the response names it.
- The Results passage still reads "**Two explanations are live** and neither is settled here" for the
  CSPG4 discordance — the third explanation the response claims was added is **not in the paper**.
- The underlying evidence **is committed**: `research/modalities/emc-expression-panels.json` carries
  the verbatim deposit annotations — **28 CRH**, **8 UHR**, 33 mRNA, e.g.
  `"STT3126-DFSP | CRH | STT3126-DFSP mRNA"` and `"STT2001c-GIST-Total RNA-WT | UHR | …"`.

⭐ **So an undisclosed platform confound that the paper's own review called a major point, and that
the paper's own response records as fixed, is absent from the committed manuscript and its SI, while
the verbatim annotations proving it sit in a committed artifact.** This is the same
committed-text-versus-response-record divergence found for the repurposing draft, but here it is a
**substantive scientific omission**, not a version-labelling question.

## Contribution of the step

A reader learns that half the six-array GPL3290 comparator arm differs from the EMC arm in **both**
reference pool and RNA input, and that this is a live, unexcluded explanation for the CSPG4
discordance. **This is disclosure of a limitation from committed data — claim weakening, not a new
result.** No new scientific claim is created and no conclusion is strengthened.

## Finite acceptance

1. Disclose the mismatch in **Methods**, in **Limitations**, and as a **third live explanation** for
   the CSPG4 discordance in Results — **in place, where those claims live**, not as an end-note.
   The "Two explanations are live" sentence must be corrected to match.
2. **Quote the deposit annotations from the committed artifact.** Every CRH/UHR/RNA-input statement
   must be traceable to `emc-expression-panels.json`. Do not infer an annotation that is not there.
3. **State the scope of what is affected as the review states it** — all 78 GPL3290 gene contrasts and
   the +0.599 route-panel score — **only if you verify those two figures in the committed text or
   artifacts**. If you cannot verify a figure, say so and omit it rather than repeating it.
4. **⛔ Do NOT recompute anything.** The review's suggested sensitivity analysis (recomputing GPL3290
   contrasts against the three DFSP arrays alone) is **explicitly OUT OF SCOPE** here. This contract
   is disclosure only. Do not run, edit or invoke any analysis module.
5. **No overclaim.** The confound does not establish that any reported contrast is wrong; it
   establishes that a mismatch exists and is not excluded. Existing hedges — that only the
   between-group contrast is interpretable on a two-colour platform, and the two already-stated CSPG4
   explanations — **survive intact**.
6. Word count stays within **5,000 main / 200 abstract**; at 4,755 there is ~245 words of headroom.
   **No hedge deleted to make room.**
7. Linters run and reported honestly with exit codes. ⛔ **If this trips a gate, that is a finding to
   report — never a reason to weaken, relax, reorder or edit a gate.** Note `lint_citations` fails
   repo-wide at exit 1 for unrelated reasons, and `lint_consistency` currently exits 1 on the
   **MTAP/PRMT5** DOI substring — a **separately owned, unresolved blocker**. Neither is G1's to fix;
   establish baselines and attribute honestly.

## Restrictions

**No network call of any kind** — every input is committed. No retry of any blocked route. **No git
write operation whatsoever** — no commit, add, stash, checkout or restore; read-only git
(`show`/`log`/`status`/`diff`) only. Take any baseline by `cp` of your own saved copy or by
`git show HEAD:<path>`, **never** by stashing the shared tree, which may carry other work. Edits
confined to `emc-surface-target-landscape.md` and, only if a Methods/SI split requires it,
`emc-surface-target-landscape-si.md`. No other manuscript, no graph edit, no `candidates.json`, no
PR, no publication, no `scripts/preflight.sh`. There is no wet lab: no EMC efficacy, safety,
selectivity or clinical-readiness claim. Invent no fact, source, patient datum or result. If a request
is refused by content policy, stop that branch, record the refusal verbatim, never route around it.

## Stop conditions

Stop if the confound is already disclosed on reading; if the artifact does not carry the annotations
quoted above; if disclosure cannot be made within the word caps without deleting a hedge; if any step
would need a network call, a recomputation, or a guard change; or at ~40 tool calls / ~40 minutes.

## Retention

Before any cleanup, under `/tmp/claude-0/g1-retained/`: pre-edit manuscript (copied before the first
edit), post-edit manuscript, unified diff, and every linter's stdout **and** stderr with its exit code
echoed. The parent preserves the original child JSONL and tool bodies with hashes and parses the
served model from that JSONL. **Nothing is re-run to recreate evidence.**
