# Paper-level decision on the synthetic instrument line, and the next step — recorded 2026-09-08 06:29:42 UTC (`date -u`)

## What the synthetic line actually contributes, and what it cannot

**The durable methods contribution is a negative about a quality metric, and S5 hardened it.** Across
**four structurally distinct censoring shapes**, `assess_quality`'s admissibility check passed **189 of 200**
reconstructions under the unchanged 0.05 floor while individual cells lost up to **51 of 53** censorings
(maxdev 0.0225) and **41 of 41** (maxdev 0.0142). The metric compares the reconstruction against the
*digitized* curve, so an error that moves the input moves both sides together. That is reusable, it is
measured on 200 reconstructions with raw bytes retained, and it does not depend on which of S4's two effects
generalises.

**S5 resolved the merit question that was open after S4, and the answer reduces the line's value.** S4's
density finding is **not** a property of the instrument: its exact-arm form fails in 3 of 4 shapes, its
read-arm form in 1 of 4, and `line_width_4` — a *degraded* render — largely abolished it. S4's extent finding
persists in direction 4 of 4 but its endpoint and magnitude are cohort properties. So the headline that looked
paper-shaped after S4 is, after S5, **a cohort-and-render artifact**, and the surviving contribution is the
metric-blindness result above.

## ⛔ DECISION: **NO-GO on further synthetic sweeps.** The child's named successor is NOT executed.

S5 proposed varying `render_km`'s figure `width` to separate digitized-point count from row count. It is
runnable, cheap and deterministic — **and runnability is not a reason to run it.** The decision against it:

1. It refines the **mechanism of an effect S5 has already shown does not generalise**. Explaining a
   cohort-and-render artifact more precisely does not make it a finding.
2. It cannot touch the **material merit limit**, which is transfer. Every result in this line is synthetic, and
   as the appended disposition on S5's report now records, **synthetic ease establishes no bound on real-figure
   error in either direction.** A methods paper about reconstructing *published* figures cannot rest on an
   instrument validated only against inputs it generated itself.
3. Continuing would be the "endless sequence of synthetic sweeps" the standing instruction forbids, and each
   further sweep would inherit the same transfer gap.

**Exact reopening input, so this is a blocker with a condition rather than an abandonment:** a **real published
survival figure whose patient-level ground truth is also published** — a paper printing both a Kaplan-Meier
curve and the per-patient data behind it (a per-subject table, a swimmer plot, or supplementary IPD). One such
pair converts every synthetic result above into a validated or refuted claim about real figures. Absent that,
the synthetic line stays a description of its own instrument, and **no reporting requirement, no journal
recommendation and no clinical claim follows from any of it.** Nothing here is a manuscript admission.

## Next step, selected and executed in the same cycle: **S6 — assemble the validation set**

The reopening input is itself a bounded, independently useful public-source question, so the next step is to
**go get it** rather than to park the line.

**Question.** Which published series — in extraskeletal myxoid chondrosarcoma first, then rare sarcoma more
broadly — print **both** a survival figure **and** the patient-level data behind it, such that a digitization
method can be validated against real ground truth rather than against synthetic inputs?

**Why it is distinct, and not a closed route.** This is **not** the closed IPD paper, **not** an
inverse-baseline application, **not** the long-term-recurrence gate, **not** an RT/IPD synthesis, and **not**
a pooled dataset — no reconstruction is performed and no patient-level data is pooled or produced. It is the
assembly of a **method-validation corpus**: figure–truth pairs. The campaign has already stumbled on two
fragments of exactly this shape (a per-subject table in one trial report; a swimmer plot in another), which is
evidence the class exists and has never been enumerated.

**Scientific purpose.** It is the one input that could make the whole digitization line say something about
real figures — and if the class turns out to be empty or unreachable at $0, that is itself the decisive,
publishable-grade negative about what this literature permits, and it closes the line honestly.

**Acceptance.** A list of candidate figure–truth pairs with identifier, access state, what the figure shows,
what form the ground truth takes, and whether both are reachable at $0 — or a documented finding that the
class is empty/unreachable within the searched scope, with the scope stated.

**Stop.** When the search scope is exhausted or ~40 tool calls / ~40 minutes, whichever first.

**Bounds and prohibitions.** Retrieval only through the already-admitted PubMed MCP route. **No reconstruction,
no digitization, no pooling, no patient-level dataset.** The `CLOSED-WORK.md` denied list (Pazopanib,
Sunitinib 2014, Wagner, CTARC, Trabectedin/RT), GSE4303/GSE28866, PMID 22592656 and any held continuation are
excluded; a non-open-access source is **UNKNOWN**, not absent. No clinical claim, no manuscript, no
publication. W25 / primary-article / Results / novelty, the NR4A/P6 successor exclusion, the S1/S3 stops, the
P1–P3 closures and the P4–P6 intake limits all stay exact.

**Ownership.** Campaign record owned by the one parent collector; no manuscript or shared-graph write. Durable
artifacts to `/tmp/claude-0/s6-retained/`, verified before any cleanup, parent copies and commits.

---

# ⛔ NARROWING APPENDED 2026-09-08 06:34 UTC — two claims above were too strong

**The decision text above is preserved unchanged.** The NO-GO on further synthetic sweeps and the correction
that synthetic ease establishes no real-figure error bound both stand. Two claims in the S6 section are
narrowed here.

## 1. A matched pair tests the method on THAT pair — it does not validate the line

The text above says one figure–truth pair *"converts every synthetic result above into a validated or refuted
claim about real figures."* ⛔ **That is too strong and is withdrawn.** A single matched pair supports a test of
the method **on that pair only** — one figure, one cohort, one endpoint, one journal's rendering. It cannot
validate or refute *every* synthetic finding, and it establishes no general claim about real figures. Whether
any result transfers beyond the pairs actually tested remains **UNKNOWN**, and the number of pairs needed for
any broader statement is itself unestablished.

## 2. A null result is a bounded source/reachability finding — not automatic paper merit

The text above calls an empty class *"the decisive, publishable-grade negative that closes the line honestly."*
⛔ **Also withdrawn.** Failing to find or reach such a pair is a **bounded statement about what was searched and
what was reachable**, nothing more. It is **not** automatically publishable-grade, **not** paper merit, and
**not** a manuscript admission. Symmetrically: **source availability is not paper admission either** — finding
pairs admits no paper. Any paper-level consequence would need its own separate decision on its own evidence.

## 3. Matched cohort/endpoint versus merely adjacent — the distinction is load-bearing

A **matched** pair means the per-patient data covers **the same cohort and the same endpoint** as the survival
figure, so it can serve as ground truth for that figure. An **adjacent** fragment — a per-subject table for a
different subset, a swimmer plot of a different endpoint or a differently-defined population, patient-level
data for some arms of a mixed cohort — **does not supply ground truth for that figure** and must not be graded
as though it did. The two fragments this campaign already stumbled on are **candidates to be tested against this
definition, not established pairs**, and either may fail it. Verdicts must state matched-versus-adjacent
explicitly and default to the weaker reading when the source does not settle it.

## 4. Closures are unaffected by any of this

Every named closed and held source stays excluded — **including if it turns out to be one of the fragments that
motivated this candidate**. These narrowings must not be used to broaden scope, revisit a closed route, or
justify a retry. The `CLOSED-WORK.md` denied list, GSE4303/GSE28866, PMID 22592656, W25 / GSE243553 /
primary-article / Results / novelty, the NR4A Perspective, the S1/S3 stops, the P1–P3 closures and the P4–P6
limits all stand exactly as recorded.

The running S6 contract otherwise continues unchanged: source identification only, no digitization,
reconstruction, pooling or clinical dataset; retention and access-state recording as already permitted; no new
manuscript or publication action; no controller, session, deadline or billing change.

---

# S6 RESULT AND PAPER-LEVEL DISPOSITION — appended 2026-09-08 06:40 UTC

## Collection and verification

Child `aadf26ebcbd3d3230`, model verified from transcript as exactly `claude-opus-5`, ran 06:31:03 → 06:36:56
UTC (5 min 53 s, 26 tool calls). Repository writes by the child: **none**; `git status --porcelain` empty at its
start and end; 20 GiB free both ends. Durable directory `/tmp/claude-0/s6-retained/` verified by the parent
re-running `sha256sum -c SHA256SUMS` — **5 of 5 OK** — then copied into `paper-lane/S6-executed-artifacts/` and
**re-verified in place, 5 of 5 OK**: `candidates.json` `6117cbce…`, `queries.json` `4d7a51fc…`,
`screened-identifiers.json` `e5d5e49c…`, `failures-and-refusals.md` `1a950f8b…`, `run-log.json` `97b5bcd5…`.
The retained directory is **not deleted**.

⚠ **One byte-preservation gap, labelled as the child labelled it:** `candidates.json` was **regraded in place**
after the narrowing arrived, so the superseded v1 grading exists only as a description inside
`_coordinator_narrowing_applied`, not as retained bytes. That is the single non-preserved item in this run and
it is recorded rather than smoothed over.

## Result: **0 MATCHED pairs established** — 1 UNKNOWN, 2 ADJACENT, 2 NOT A PAIR

⭐ **Both fragments that motivated this candidate were tested against the matched/adjacent definition and both
fail it.** The trabectedin sub-analysis is **ADJACENT** — partial-cohort per-subject truth against a
**mixed-arm** curve. The swimmer plot is **NOT A PAIR** — that report prints **zero** KM curves, so there is a
truth with no figure. The narrowing was applied before any verdict was finalised, exactly as intended, and it
changed the answer.

## Three findings about the search route itself, all measured

1. ⛔ **The admitted route cannot see either half of a pair.** `get_full_text_article` returns narrative text
   only — it strips table contents, figure images, and even the table and figure *numbers* (inline citations
   render as bare `()` or `"presented in Table."`). Observed independently on three separate articles.
   **No verdict rests on direct inspection of any table or figure.**
2. ⛔ **PubMed cannot search this class at all.** `sarcoma AND swimmer plot AND (…)` returns **0 records** while
   this campaign *holds* a retained sarcoma swimmer plot — the index covers title/abstract/MeSH, not figure
   captions or table contents. The class is only screenable one article at a time.
3. Two of seven queries failed **as queries** (an `open access[filter]` that voided its own query; a quoted
   phrase auto-mapped into `patients[MeSH]`, 737 unrelated records). Neither is evidence about the class.

**Closure discipline held under pressure:** PMID 32856598 (Wagner) surfaced inside a result list and was
**dropped on sight** — not retrieved, no substitute route sought.

## Paper-level disposition

**The synthetic instrument line remains BLOCKED, and its reopening input is not in hand.** S6 was the attempt
to fetch that input and it returned zero matched pairs, so nothing changes for the synthetic work: no
digitization result is validated or refuted, and no reporting requirement, journal recommendation or clinical
claim follows from any of it.

**This is a bounded source/reachability result and nothing more**, per the narrowing above: it does **not**
establish that the class is empty in the literature, it is **not** paper merit, and it is **not** a manuscript
admission — and finding pairs would not have admitted a paper either. 13 PMC-available candidates and 19
no-PMCID candidates were **NOT RUN**; scope was EMC plus four adjacent ultra-rare sarcoma histologies,
English-language PubMed only, on this date.

**Exact dependency for the one decisive open candidate:** `fice2022emc` (PMID 35251555 / PMC8891938) collapses
to MATCHED or NOT A PAIR on **one look** at whether it prints a survival figure and whether its per-patient
table carries follow-up time and vital status. That look needs a **table/figure rendering route** — PMC HTML or
PDF — which this campaign has not been granted. The child correctly refused to route around the route it was
given. Until such a route exists, that candidate stays **UNKNOWN**.

⭐ **One structural observation worth carrying, recorded as OBSERVED, NOT PROVEN:** per-patient rows appeared
only in very small reports (a 5–8 subject trial sub-analysis, a 15-patient case series), while the 38–60-patient
series printed aggregate tables. **The pair and the figure worth digitizing pull in opposite directions** — the
studies large enough to have a curve worth reconstructing are the ones that stop printing per-patient data.
If that holds beyond this scope, it is a reason the class may be structurally thin rather than merely unsearched.

## No further dispatch on this line

No worker is dispatched to continue it. The decisive candidate needs a capability this campaign does not have;
the remaining unscreened candidates would be more of the same one-at-a-time screening against a route that
cannot see tables or figures; and manufacturing another sweep or another census to fill a slot is precisely
what the standing instruction forbids. **Recorded as blocked with its exact reopening input, not abandoned and
not padded.**

All holds and closures stand exactly: S1/S3 stops, P1–P3 closures, P4–P6 limits, the NR4A/P6 successor
exclusion, and the W25 / primary-article / Results / novelty safety hold. No manuscript, publication, clinical
claim, controller, session, deadline or billing change arises from any of this.

---

# S6 EVIDENCE RETENTION + SCOPE CORRECTIONS — appended 2026-09-08 06:44 UTC

Mechanical retention from the **existing child transcript only**. No new source lookup, no query re-run, no
analysis, no regenerated grading. S6's branch stays finished.

## 1. Original PubMed tool-response bodies retained — 14 of 14

Extracted **unchanged** from the child transcript's `tool_result` blocks (not rewritten, not summarised) into
`paper-lane/S6-executed-artifacts/original-tool-responses/`, each paired with its tool name and verbatim input
in `INDEX.json`, hashed in `SHA256SUMS-original-responses.txt`:

| response | tool | bytes | sha256 (head) |
|---|---|---:|---|
| `01-get_full_text_article-PMC4946242.txt` | `mcp__PubMed__get_full_text_article` | 19,107 | `71e5542cf78c2630` |
| `07-get_full_text_article-PMC8891938.txt` | same | 20,609 | `a13897e56f21d273` |
| `14-get_full_text_article-PMC6194639.txt` | same | 17,074 | `29044957099606df` |
| 7 × `search_articles` | `mcp__PubMed__search_articles` | 648–2,089 | `78fced2d…`, `a91e4dca…`, `4c6a0464…`, `52dc1b15…`, `19ed73df…`, `76aab4f7…`, `e7c93280…` |
| 2 × `convert_article_ids` | `mcp__PubMed__convert_article_ids` | 1,786 / 1,794 | `41df5a14…`, `5edd3c2b…` |
| 2 × `get_article_metadata` | `mcp__PubMed__get_article_metadata` | 46,490 / 21,201 | `93f83217…`, `9b382f41…` |

The three narrative full-text bodies are now reviewable in the original, so any reader can check the child's
curated quotations against them — **and can confirm directly that they contain no table contents and no figure
images**, which is the basis for the standing rule that **no verdict here is a table- or figure-based verdict**.

## 2. ⭐ The superseded `candidates.json` v1 bytes ARE recoverable, and are retained

The earlier "v1 not byte-preserved" gap is **closed**. The v1 write survives as the heredoc body of the
original Bash `tool_use` input in the child transcript, recovered without re-running anything and retained at
`paper-lane/S6-executed-artifacts/candidates.v1-ORIGINAL-BYTES.json` — **10,668 bytes, sha256
`7b18d2a900e95e41316dc163de73b9e3af084e6e2f9ef5fd48919f24ab92cf07`**, parses as valid JSON, carries
`_written_utc: "2026-09-08T06:5xZ (see run-log.json for exact date -u)"` and **lacks**
`_coordinator_narrowing_applied` — confirming it is the pre-narrowing grading. **v2 (`6117cbce…`) is unchanged**
and both are now retained side by side.

## 3. Scope correction — the query evidence is about THESE queries, not about PubMed

⛔ My earlier line *"PubMed cannot search this class at all"* is **too strong and is withdrawn.** What the
records support: **these seven queries, returning these fields, did not surface the class**, and the one
directly diagnostic observation is that `sarcoma AND swimmer plot AND (…)` returned **0 records** while the
campaign holds a retained sarcoma swimmer plot — evidence that **the fields these queries searched** do not
index figure captions or table contents. That is a limitation of the queries and the returned fields, **not a
proof about PubMed's capabilities in general**, and other query formulations or indexes are **UNKNOWN**, not
excluded.

## 4. Count reconciliation, from existing records only — and it does not fully reconcile

`queries.json → not_run` and `failures-and-refusals.md` list **15** PMC identifiers; `screened-identifiers.json
→ screening_totals.pmc_available_but_not_screened` and my own earlier disposition say **13**. Reading the
per-item dispositions already in `screened-identifiers.json`, the 15-item list is **heterogeneous** and at least
five of its members are not "available but unscreened":

- `PMC10225189` — *"CANDIDATE — graded ADJACENT in candidates.json; full text NOT RUN"* (a graded candidate);
- `PMC10660714` — **REJECT**, ASPS imaging-features study, subject is imaging;
- `PMC5105269` — **REJECT**, single case report, one patient cannot carry a curve;
- `PMC4713678` — **REJECT**, urothelial carcinoma, EMC only as a histologic mimic — off-topic;
- `PMC5574947` — *"NOT RUN **as a pair candidate**"*, a screening judgement rather than an unexamined item.

⚠ **Those categories account for the direction of the discrepancy but not for its exact size:** 15 minus the
one graded and the three rejects is 11, and minus the pair-candidate judgement is 10 — **neither equals 13**.
So `pmc_available_but_not_screened: 13` is **not reproducible from the per-item dispositions**, and my earlier
disposition repeated the 13 uncritically. Recorded as an **unreconciled internal inconsistency in the child's
own records**. **No extra source search was run to resolve it**, and none should be.

## 5. Timestamps — use the run-log, not the placeholder

Authoritative: `run-log.json` / the child's own `date -u`, **06:31:03 → 06:36:56 UTC**. `candidates.json`
carries the literal placeholder `"2026-09-08T06:5xZ"` in `_written_utc` (in both v1 and v2) and it **must not be
quoted as a time**; the file itself points to the run-log for the exact reading.

## 6. Unchanged

`candidates.json` v2, `queries.json`, `screened-identifiers.json`, `failures-and-refusals.md`, `run-log.json`
and the child's report are **untouched**; the durable source directory `/tmp/claude-0/s6-retained/` is **not
deleted**; the child-transcript model evidence (observed set exactly `claude-opus-5`) is retained in
`S6-MODEL-START-RECEIPT.md`. No verdict was changed by this retention pass.
