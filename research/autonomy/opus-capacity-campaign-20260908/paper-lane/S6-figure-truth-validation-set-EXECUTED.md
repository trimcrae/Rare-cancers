<!-- collected 2026-09-08T06:38:14Z by campaign coordinator; agent id aadf26ebcbd3d3230; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aadf26ebcbd3d3230.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met (acceptance: durable, verified candidate list with per-candidate verdicts).

## Worker

**S6**, paper lane, OPUS-CAPACITY-CAMPAIGN-20260908 — focused public-source recovery.

**Model — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42, remote cloud. I did not observe the served model. Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` is in the first tool call of this run and is byte-identical to the block reproduced in `reports/W07g-cohort-composition-dependencies.md` except for nothing — same container, same session.

- `date -u` start `Tue Sep  8 06:31:03 UTC 2026` · end `Tue Sep  8 06:36:56 UTC 2026`
- `git rev-parse HEAD` start `061afc559af80234f80681f09caafb251a34411d` · end `c31052098e46320a8d7761233ce3908e02bb00f8` (advanced under me by the coordinator, not by me)
- `git status --porcelain` start: empty · end: empty
- `df -h /` start `252G / 18G used / 20G avail / 47%` · end identical. ≥10 GiB free honoured at both ends.
- Repository writes: **none**. No git operation, no manuscript or shared-graph edit. `scripts/preflight.sh` not run; `atr_hrd_sarcoma_series.py` never invoked.

## Question

Which published series print **both** a survival figure **and** the per-patient data behind it, so a digitization method could be tested against real ground truth — EMC first, then rare sarcoma more broadly?

## Coordinator narrowing — applied before any verdict was finalised

All three points are recorded verbatim in `candidates.json → _coordinator_narrowing_applied` and govern this report:

1. **Withdrawn:** that one pair would validate or refute the synthetic line. A pair tests a method **on that pair only** — one figure, one cohort, one endpoint, one journal's rendering. Transfer beyond pairs actually tested is UNKNOWN.
2. **Withdrawn:** that an empty class is a decisive, publishable-grade negative. What follows is a **bounded source/reachability result**. It is not paper merit, not a manuscript admission — and finding pairs would not have admitted a paper either.
3. **MATCHED vs ADJACENT** is applied to every row, with the weaker reading as default. Both dispatch fragments were **tested** against it; **neither passes**.

## Prior-work check

Read `DECISION-synthetic-line-and-S6.md`, `CLOSED-WORK.md` in full, `CORPUS-CONTEXT.md`, `P1-PUB-IPD-SURVIVAL-paper-step.md` (fragment provenance), `W07g` (method + failure modes), and the committed artifact `research/modalities/emc-ipd-survival.json` at live HEAD. The two fragments trace to `emc-ipd-survival.json → printed_patient_level_data` and `→ candidate_sources[].figure_finding`, not to my own retrieval; I re-derived nothing and re-ran nothing.

## Method and queries run

Retrieval **only** through the admitted PubMed MCP tools. Seven searches, two ID conversions, two metadata batches, three full-text retrievals. All queries with result counts, including the failures, are in `queries.json`.

According to PubMed, the three articles whose narrative text I retrieved are [10.1186/s12885-016-2511-y](https://doi.org/10.1186/s12885-016-2511-y), [10.1177/20363613221079754](https://doi.org/10.1177/20363613221079754) and [10.1186/s12885-018-4934-0](https://doi.org/10.1186/s12885-018-4934-0).

**The governing method fact:** `get_full_text_article` returns narrative text only. On all three retrievals it stripped table contents, figure images, and even the table/figure *numbers* — inline citations render as bare `()` or `"presented in Table."`. The two halves of a figure–truth pair live exactly in the stripped material. **No verdict below rests on direct inspection of a table or a figure.**

## Candidates and verdicts

| Source | IDs | Figure | Ground truth | Both halves at $0 | Verdict |
|---|---|---|---|---|---|
| Morioka 2016 trabectedin sub-analysis (dispatch fragment 1) | PMID 27418251 · PMC4946242 · [DOI](https://doi.org/10.1186/s12885-016-2511-y) | Fig. 1 KM of PFS, **two arms** (trabectedin 5, BSC 3), numbers-at-risk row printed for both (repo artifact, not re-measured) | Table 2 per-subject efficacy; **confirmed at 2 subjects** (repo transcription); rest of trabectedin arm asserted by repo record, BSC arm UNKNOWN | Open access → yes for a browser; **no** through this route | **ADJACENT** — partial-cohort truth against a mixed-arm curve |
| Fice 2022 EMC case series | PMID 35251555 · PMC8891938 · [DOI](https://doi.org/10.1177/20363613221079754) | KM OS + DSS stated in Methods; figure existence not confirmed | "Additional treatment characteristics can be seen for each patient in [table]"; whether time+status are printed per patient unresolved | Open access → yes for a browser; **no** through this route | **UNKNOWN** |
| ImmunoSarc swimmer plot (dispatch fragment 2) | PMC7674086 (repo record only) | **Zero KM curves** (`km_figures = 0`) | Fig. 3 swimmer plot = the truth itself | truth yes, figure absent | **NOT A PAIR** |
| Giani 2023 DSRCT | PMID 36951537 · PMC10225189 · [DOI](https://doi.org/10.1002/cam4.5829) | KM EFS/OS over 38 | per-patient times for 5 long-term survivors only | UNKNOWN (full text NOT RUN) | **ADJACENT** |
| Shiba 2018 EHE | PMID 30340559 · PMC6194639 · [DOI](https://doi.org/10.1186/s12885-018-4934-0) | 3 KM figures | none — every cited table is an aggregate summary | figure yes, truth absent | **NOT A PAIR** |

**Result: 0 MATCHED pairs established, 1 UNKNOWN, 2 ADJACENT, 2 NOT A PAIR.** Both fragments the campaign had already stumbled on fail the MATCHED test.

## Rejects and why

Full disposition of all 43 identifiers seen is in `screened-identifiers.json`. Principal rejects: PMID 26823892 (urothelial carcinoma, EMC only as histologic mimic — off-topic); PMID 27832806 (single case report); PMID 37987424 (ASPS imaging study, no survival figure indicated); PMID 30340559 (aggregate tables). PMIDs 36825763 (EMC n=44) and 35962783 (EMC n=60) are shape-plausible candidates with **no PMCID** — their access is **UNKNOWN, not absent**.

## Blocked or unreachable, with the exact dependency

1. **Neither half of any pair is renderable through the admitted route.** Exact dependency: one rendering of the PMC HTML or PDF tables and figures for a named candidate. Not attempted — no admitted route.
2. **PubMed cannot search this class at all.** `sarcoma AND swimmer plot AND (...)` → **0 records**, while the campaign *holds* a retained sarcoma swimmer plot. PubMed indexes title/abstract/MeSH, not figure captions or table contents. Candidates can only be screened one article at a time.
3. Two queries failed as queries: `open access[filter]` voided its query (0 records, no term expansion at all); a quoted-phrase query was auto-mapped into `patients[MeSH]` and returned 737 unrelated records. Neither is evidence about the class.
4. 19 of 41 screened PMIDs have no PMCID → access UNKNOWN. 13 PMC-available candidates were **NOT RUN**.
5. **PMID 32856598 (Wagner)** surfaced inside one result list. Denied list — dropped on sight, not retrieved, no substitute route sought. No other denied or held item was touched.

## Durable artifacts written and verified

`/tmp/claude-0/s6-retained/` — verified by `sha256sum -c SHA256SUMS`, **all 5 OK**, printed above. Nothing deleted; the directory is intact for the parent collector.

```
6117cbce5172c04c5fdd2a76d545c014990a31eecdbc38f4a3470855850f2cad  candidates.json
4d7a51fc02b5e38d1dd2002b8aabdfc6bfb2ef91188ced773087c9a1aa098cbd  queries.json
e5d5e49ca8a40d602a9cefc3167e59be951e9aa3680a354417f0b56da4d44afa  screened-identifiers.json
1a950f8b5da4c8c2b0b5c7f9448fd684100f34df3830f1b77cd2c051d95517a5  failures-and-refusals.md
97b5bcd581cb437dded439cd453a1259861d523d2d77e5d7f3da4240728ce494  run-log.json
```

No bytes are missing. `candidates.json` was regraded in place after the coordinator's message; the superseded v1 grading is described in `_coordinator_narrowing_applied` rather than retained as a separate file — that is the one thing not byte-preserved, and it is labelled as such.

## What this does and does not support

**Supports:** within this scope, on this date, through this one route, **no MATCHED figure–truth pair was established**. It supports one structural observation, recorded as OBSERVED, NOT PROVEN: per-patient rows appeared only in very small reports (a 5–8 subject trial sub-analysis; a 15-patient case series), while 38–60-patient series printed aggregate tables — so the pair and the figure worth digitizing pull in opposite directions.

**Does not support:** that the class is empty in the literature; that any digitization result is validated or refuted; any paper, any manuscript admission, any reporting recommendation. Source availability is not paper admission — in either direction. **No clinical claim of any kind** about any disease, therapy, prognosis or readiness follows from anything here. There is no wet lab. No reconstruction, digitization, inversion, pooling or patient-level dataset was performed or produced.

## Validation evidence

`sha256sum -c` on all five artifacts (all OK, output printed); `json.load` parse check on all three JSON files; start/end `date -u`, HEAD, `git status --porcelain`, `df -h /` recorded and reproduced. The MCP-route stripping behaviour was observed independently on three separate articles, not inferred from one.

## Limitations

Every verdict is an inference from narrative prose and from the repository's own committed artifacts, **never** from inspecting a table or a figure. The Morioka risk-row and per-subject facts are the repository's committed measurements, graded as such and not re-measured under me. 13 PMC-available candidates and 19 no-PMCID candidates were not screened. Two of seven queries failed as queries. The disease scope was EMC plus four adjacent ultra-rare sarcoma histologies, English-language PubMed only.

## Stop condition

Acceptance: durably written, hash-verified candidate list with per-candidate MATCHED/ADJACENT/UNKNOWN verdicts, plus a bounded, explicitly scoped result. Reached at ~6 minutes and 26 tool calls, well inside the ~40/~40 ceiling.

## Tool-call and wall-clock count actually used

**26 tool calls · 5 minutes 53 seconds wall clock** (06:31:03 → 06:36:56 UTC).

## Next concrete action

For the parent collector: copy, verify against `SHA256SUMS`, and commit `/tmp/claude-0/s6-retained/`. The single decisive open question is `fice2022emc` (PMC8891938) — it collapses to MATCHED or NOT A PAIR on **one look** at whether that article prints a survival figure and whether its per-patient table carries follow-up time and vital status. That look requires a table/figure rendering route this worker was not granted; it is a decision for the coordinator, not an action I should take by routing around the route I was given.
