# F1 — collection and adjudication, with a parent language qualification

Collected 2026-09-08 ~08:58 UTC. F1 is terminal (UI: Completed, 3m32s, 16 tool uses). No restart, no
review cycle, no new child, no lookup, no retention re-run. Contract and worker history preserved.

## Child identity — parsed from the transcript, not the receipt

| item | measured |
|---|---|
| child | `ac729a1950a540205` |
| original JSONL | `F1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-ac729a1950a540205.jsonl`, **165,513 bytes**, `cmp`-identical at copy |
| model strings | **33 × `claude-opus-5`, 0 others** |
| span | **08:50:03.764Z → 08:53:36.173Z** (~3 m 32 s) |
| tool pairs | **16 `tool_use` / 16 `tool_result`** — matches the UI's 16 |

Bounds ~40 calls / ~40 min: **16 / ~3.5 min, well within.**

## ⚠ Parent language qualification — recorded separately, and the contract was wrong first

**The error is mine, in `CONTRACT-F1-…md`, not F1's.** That contract said the record "**answers**"
the caveat and that the existence of a peer-reviewed version "**is established**". Both overstate.
The record's `_answer` field is **its own label**, not independent confirmation, and three mutually
agreeing search-index queries are **not** publisher verification and are **not** verification that
peer review occurred. F1 followed the contract faithfully and inherited the overstatement into the
manuscript ("That a peer-reviewed version exists is what has been established").

**The correct level, now applied:** the retained search-index results **identify an apparent
published counterpart**. Existence is **indicated, not confirmed** — and it is qualified **together
with** the bibliographic metadata, not separately from it. Publisher record, and cross-version
identity and content, are **UNCONFIRMED at the level actually observed**.

Five parent replacements applied to `emc-mtap-prmt5-hypothesis.md` (diff
`parent-qualification.diff`, 52 lines), in F1's own three passages:

- §4.4 → "Search-index results retained on 2026-08-10 identify an apparent peer-reviewed counterpart
  … That identification is search-index-level and is not independent publisher verification …
  So the existence of a published counterpart is indicated rather than confirmed, on the same footing
  as the bibliographic detail given in reference 2, and agreement between repeated index queries is
  not verification of the publisher's own record, nor of the peer-review process itself. Both the
  existence and the detail must be confirmed against the publisher record before submission. … the
  apparent published version was neither read here nor matched against the preprint, so whether it is
  the same work in content, and whether those findings survive peer review unchanged, are both
  unconfirmed."
- Reference 2 → "Search-index results identify an apparent peer-reviewed counterpart:" and "its
  existence, together with its title, authors, volume, issue, article number, DOI and PMCID, is
  indicated by a search index rather than confirmed … whether that record is the same work in content
  was not checked."
- Reference-completion note → "An apparent peer-reviewed counterpart is indicated by search-index
  results retained on 2026-08-10 … the counterpart's existence and its metadata alike are indicated
  rather than confirmed."

`grep` for the superseded unqualified forms ("is what has been established", "was subsequently
published") returns **0**. **No new search, retrieval, denied-route retry, review or retention cycle
was run** — this is wording over the already-retained record.

## Contract terms, adjudicated

1. **In-place replacement, no end-note — MET.** Three passages corrected where the caveat lives.
2. **Verification level carried — MET, only after the parent qualification above.** As F1 delivered
   it, the level was carried for the *metadata* but the *existence* was stated as established. That
   split is exactly what the qualification closes.
3. **Attributions unmoved — MET.** Preprint-read findings stay attributed to the preprint (2 explicit
   statements), and the text now adds that the apparent published version was never matched against
   the preprint.
4. **No overclaim; transfer hedges intact — MET.** 3 grep hits for the no-shared-DNA-binding-domain
   and no-EMC-observation hedges; "argued rather than assumed"; "neither is an observation in EMC".
   Nothing about the counterpart is used to strengthen the EWSR1::ATF1 → EWSR1::NR4A3 transfer.
5. **Reference 2 and the completion note updated consistently — MET.**
6. **Word cap and hedges — MET.** Main 5,276 → 5,588 w; `GCC-Research-Article` records
   `limits.main_words = null` and abstract cap 250 with the abstract unchanged at 249;
   `submission_metrics` exit 0, `0 limit(s) exceeded`. No hedge cut.
7. **Linters honest — MET, with one gate finding.** See below.
8. **No network, no git write — MET.** F1 obtained its `lint_citations` baseline by `cp` and verified
   restoration with `cmp`; it performed no git write at all. It left
   `research/manuscripts/submission-metrics.json` modified as a `submission_metrics.py` side effect
   and reported that rather than reverting it, exactly as instructed.

## Linter outcomes (post parent qualification)

| linter | exit | note |
|---|---|---|
| `lint_style` | **0** | see the self-inflicted trip below |
| `lint_claims` | 0 | |
| `lint_submission_residue` | 0 | |
| `lint_asymmetry` | 0 | |
| `submission_metrics` | 0 | 0 limits exceeded |
| `lint_consistency` | **1** | ⛔ genuine finding, unfixed — see below |
| `lint_citations` | 1 pre-edit **and** post-edit | pre-existing repo-wide failure; F1's cp-based baseline shows the same exit, the only delta being two *advisory* NOT-SWEPT lines |

**⛔ `lint_consistency` gate finding, reported not fixed.**
`emc-mtap-prmt5-hypothesis.md:673: ERROR [S-card_ratio_4090_over_3090_2_10] superseded value '2.102'
stated without marking it superseded.` The string `2.102` is a **substring of the DOI**
`10.1016/j.jbc.2022.102434` (…202**2.102**434). It is a naive-substring false positive against an
unrelated GPU-benchmark value. The DOI is correct and cannot be reworded, and marking it "superseded"
would be a false statement. **No gate was weakened, relaxed, reordered or edited, and the ledger was
not touched.** This is a live blocker on the manuscript's commit gate and needs a parent decision
(a digit-boundary/token exclusion in the rule, which is a gate change outside both F1's scope and
this continuation's) — recorded, not acted on.

**One self-inflicted trip, fixed in my own prose.** My first qualification pass introduced
`**not**` and `**indicated rather than confirmed**`, which tripped `lint_style`
`bold-midsentence` ×2 (exit 1). I removed the bold — the words carry the emphasis — and `lint_style`
returned to **exit 0**. The gate was correct and was not touched.

## Out-of-scope finding F1 raised, routed not acted on

Appendix A's corrections register attributes "a peer-reviewed fusion-dependent PRMT5 requirement in a
second EWSR1-fusion sarcoma **[2]**" — but that is the Ewing result, reference **[3]**; [2] is the
non-peer-reviewed preprint. F1 flagged rather than edited it, correctly: it sits outside the
contract's named passages and inside a preserved register. Recorded for a separate decision.

## Standing

**This is not publication acceptance.** The apparent published counterpart remains unconfirmed at
publisher level, the `lint_consistency` blocker is open, and the register mis-citation is unresolved.
Baseline for this collection was taken read-only (`git show HEAD:…` `cmp`-identical to F1's
`BEFORE.md`); no stash and no shared-tree checkout was used while other work was present.
