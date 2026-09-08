# W03 — Public genomic / structural-variant resources (lane 3)

> Collected by the campaign coordinator from worker W03's in-response draft
> (workers are read-only on the Git working tree; the coordinator is the sole collector).
> Runtime model evidence for this child, extracted by the coordinator from the child
> transcript: `"model":"claude-opus-5"` (OBSERVED, not self-report).

## Worker
- **Worker:** W03, lane 3. **Model identity as stated by the child: SELF-REPORT, not independently
  verified** — it reported itself as Claude Opus 5 (`claude-opus-5`). Independent coordinator-side
  transcript extraction agrees: `"model":"claude-opus-5"`.
- `env | grep -i -E 'claude|anthropic|model'` key lines: `AI_AGENT=claude-code_2-1-263_agent`,
  `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDECODE=1`, `CLAUDE_CODE_ENTRYPOINT=remote`,
  `CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default`, `CLAUDE_CODE_CHILD_SESSION=1`,
  `CLAUDE_EFFORT=medium`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`,
  `CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71`.
  **No environment variable names a model.**
- `date -u` start: `Tue Sep  8 01:51:02 UTC 2026`; end: `Tue Sep  8 01:54:13 UTC 2026`.
- Self-observed budget: ~23 tool calls, ~3 minutes wall clock (target, not an enforced limit).
- Harness-recorded usage: 23 tool uses, 302,080 ms, 96,810 subagent tokens.

## Question
The dispatch's starting question — *is there a source-traceable relationship between NR4A3
**fusion partner** and any natural-history feature* — is **already answered in this repository**
and was not replayed. W03 pivoted to the nearest genuinely open question inside the lane, the
**breakpoint** half rather than the partner half:

> **For the EMC cases whose fusion breakpoint is resolved to exon level in the published record,
> is any case-level natural-history covariate (age, site, size, metastatic pattern, latency)
> retrievable and joinable to that breakpoint?**

Open because the repository's partner-level synthesis stratifies only on the 5' gene, while its
exon-resolved breakpoint catalogue (`research/modalities/aso-per-junction-table.json`) was built
for reagent-design purposes and was never joined to any clinical axis.

## Prior-work check
Commands run and what they showed:

- `rg -n -i "fusion partner|EWSR1|TAF15|TCF12|NR4A3|breakpoint|structural variant" research/ --glob '!.git' -l | head -80`
  -> ~40 files, dominated by `research/manuscripts/fusion-partner/` and `fusion-output/`.
- `git ls-files | rg -i "fusion|partner|breakpoint"` -> revealed `PUB-FUSION-PARTNER` with
  **7 distinct hardening rounds** of review seats, plus
  `research/manuscripts/emc_fusion_partner_pooling.py` (138 KB),
  `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`, and 6 dedicated tests.
- Read `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` (abstract + section 1).
- `rg -n -i "breakpoint|exon" research/manuscripts/fusion-partner/ research/manuscripts/emc_fusion_partner_pooling.py`
  -> **one incidental hit**, in a provenance note.

**Confirmed already closed, not replayed.** The partner x natural-history question is a finished
manuscript: it pools disease-specific death **7/15 = 46.7% (95% CI 24.8-69.9)** for TAF15::NR4A3
vs **6/58 = 10.3% (4.8-20.8)** for EWSR1::NR4A3 over 73 patients (Agaram 2014 PMID 24746215;
Huang 2023 PMID 36948401), *with its own published defeater* — the partner is not independent of
tumour size — plus partner prevalence 28/154 = 18.2% (12.9-25.0), local recurrence and distant
metastasis by partner, and an explicit population-overlap holdout. **W03 adds nothing to this and
did not re-derive it.**

Also honoured from `CLOSED-WORK.md`: did not touch Brenca case identity, did not approach
Hofvander/EGA controlled access, did not substitute a 2012 source for the unrecovered sunitinib
2014 paper, and did not retry any route already recorded as denied.

**Critically, the prior-work check shows the breakpoint axis is genuinely untouched:** the 138 KB
pooling engine contains no exon or breakpoint logic at all.

## Method / inputs
- **Repository input (read-only):** `research/modalities/aso-per-junction-table.json` — 38
  enumerated frame-compatible junctions, each tiered `published_exon_resolved_breakpoint` (5) /
  `partner_published_this_exon_not_reported` (25) / `no_published_exon_resolved_breakpoint` (8),
  with `breakpoint_refs`.
- **Public retrieval (PubMed):** `get_article_metadata` for PMIDs 12378528, 29937513, 10537274,
  11156374; `get_full_text_article` for PMC6073125. According to PubMed. DOIs:
  10.1002/gcc.10127, 10.3390/ijms19071855. PMIDs 10537274 and 11156374 carry no DOI in the
  PubMed record.
- **Attempted and unrecovered:** `https://onlinelibrary.wiley.com/doi/10.1002/gcc.10127` ->
  `EGRESS_BLOCKED`; `https://www.mdpi.com/1422-0067/19/7/1855` -> `EGRESS_BLOCKED`;
  `https://mitelmandatabase.isb-cgc.org/` -> `EGRESS_BLOCKED`. Honest unrecovered sources,
  not circumvented.
- **Not queried:** COSMIC, cBioPortal, ClinVar/dbVar. UNKNOWN, not searched-and-empty.
- Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0], stdlib only.

## Result

### R1 — Source-traceable breakpoint x natural-history table (the join is empty)

| Source | Exon-resolved architecture(s) | n cases exon-resolved | Case-level NH covariate | Grade |
|---|---|---|---|---|
| Panagopoulos 2002, PMID 12378528, DOI 10.1002/gcc.10127 | `EWSR1_e12__NR4A3_e3` (10), `EWSR1_e13__NR4A3_e3` (2), `TAF15_e6__NR4A3_e3` (3) | 15 | **0** — full text egress-blocked | PRIMARY (abstract only) |
| Sjogren 1999, PMID 10537274 | `TAF15_e6__NR4A3_e3` | 2 | **0** | PRIMARY (abstract only) |
| Sjogren 2000, PMID 11156374 | `TCF12_e5__NR4A3_e3` (exon no. from GenBank AF289510.1, not the abstract) | 1 | **0** | PRIMARY (abstract only) |
| Urbini 2018, PMID 29937513, DOI 10.3390/ijms19071855 | `EWSR1_e12__NR4A3_e3` (#2,#3,#5), `EWSR1_e13__NR4A3_e3` (#4), **`EWSR1_e7__NR4A3_e2`** (#1) | 5 | **0** — Table 1 stripped by the PMC extractor; mdpi.com blocked | PRIMARY (PMC full text) |

Verbatim anchors: Panagopoulos — *"The most frequent EWS/CHN transcript (type 1; 10 tumors),
involved fusion of EWS exon 12 with CHN exon 3, and the second most common (type 5; two cases)
was fusion of EWS exon 13 with CHN exon 3. In all tumors with RBP56/CHN fusion, exon 6 of RBP56
was fused to exon 3 of CHN."* Urbini — *"the exon12/exon3 junction was detected in three out of
five cases (#2, #3, #5) while exon13/exon3 and exon7/exon2 were detected respectively in samples
#4 and #1"*.

**Computed:** pooled **n = 23** cases with an exon-resolved breakpoint — an **upper bound on
distinct patients**, because all four are European referral-centre series of overlapping eras and
independence is not established for any pair. Cases with any retrievable case-level
natural-history covariate: **0/23 = 0.0%, Wilson 95% CI [0.0000, 0.1431]**.

**This is a denominator failure, not a null association.** No contingency table exists, so no
association can be estimated, tested, or bounded in either direction. *(SECONDARY / structural.)*

### R2 — Republication flag (dispatch requirement)
Urbini case #1 is the only case in the whole set with *any* clinical fact attached — *"the same
patient had been treated with sunitinib with a prolonged response"* — and that is **therapy
response, not natural history**. Urbini also states *"we reported the therapeutic activity of
sunitinib in a cohort of 10 EMC patients"*, so its five WTS cases **cannot be shown distinct**
from the same group's sunitinib series (PMID 24703573, itself recorded unrecovered in
`CLOSED-WORK.md`). Not independent; excluded from the join. *(PRIMARY, overlap unresolved.)*

### R3 — A checkable defect in the repository's own breakpoint catalogue (the positive finding)
**All 38 junctions in `aso-per-junction-table.json` fix the 3' acceptor at `NR4A3_e3`.** Two
independent published sources contradict that as a universal:

1. **Urbini 2018** reports `exon7/exon2` in sample #1 — *"an exon upstream of the start codon"* —
   an **NR4A3 exon 2 acceptor**.
2. **Panagopoulos 2002** independently: *"In CHN, 12 breakpoints were found in intron 2 and only
   two in intron 1."* An intron-1 genomic break yields an **NR4A3 exon 2** acceptor. That is
   **2/14 mapped genomic breakpoints**.

So a published breakpoint architecture class is **structurally unrepresentable** in the
enumeration, not merely untiered. Separately, `EWSR1_e7__NR4A3_e3` is tiered
`partner_published_this_exon_not_reported`, yet Panagopoulos reports *"In EWS, the breaks occurred
in introns 7 (one break), 12 (eight breaks), and 13 (one break)"* — a possible under-tier, flagged
rather than asserted, since the abstract does not name the corresponding transcript. **This is an
observation about a catalogue's coverage. It is not reagent design and implies nothing about any
molecule.** *(PRIMARY sources, SECONDARY inference.)*

## Validation evidence
**RUN.** Environment: Python 3.11.15 [GCC 13.3.0], Linux, stdlib only, executed in
`/tmp/claude-0/.../scratchpad/W03/` (outside the repository).

```
$ python3 breakpoint_naturalhistory_join.py
...
Distinct exon-resolved architectures named across sources : 5
Architectures whose 3' acceptor is NOT NR4A3 exon 3       : 1 ['EWSR1_e7__NR4A3_e2']
Pooled cases ... (UPPER BOUND on distinct patients; overlap excluded = False) : 23
Of those, cases with ANY retrievable case-level natural-history covariate ... : 0
Proportion 0/23 = 0.0000   Wilson 95% CI [0.0000, 0.1431]
SELF-CHECK: assertions passed.
EXIT=0
```

**Honest note on a failed first run.** The first execution **exited 1** on
`AssertionError: Wilson upper bound drifted: 0.14311661850798416` — the hand-typed expected
constant `0.14225` was wrong; the computed value was right. The check was **not** deleted or
weakened. The magic decimal was replaced with the closed form for the zero-event case,
`Wilson upper = z^2/(n+z^2) = 3.84146/(23+3.84146) = 0.143119`, which the run then satisfied at
1e-9. The check is now stronger than the one that failed.

**PROPOSED (NOT RUN):** retrieval of Panagopoulos Table 1 and Urbini Table 1 via an egress
hatch; any COSMIC/cBioPortal/Mitelman query.

## Limitations
- **n = 23 is an upper bound on patients, not a patient count.** Independence is not established
  for any pair of the four sources; the true distinct-patient count is unknown and lower.
- Three of four sources are **abstract-only**. Absent case-level data there is **UNKNOWN, not
  absent** — Panagopoulos and Urbini both likely print per-case tables that were unreachable. The
  0/23 measures *retrievability under this session's egress*, not the world literature.
- `TCF12_e5` rests on the repository's GenBank assignment, not on the abstract's own words.
- Wilson [0, 0.143] is a proportion interval on a *structural* quantity; it is not a clinical
  effect estimate.
- **No result here is an association, and certainly not causation.** Nothing bears on EMC
  prognosis, treatment, efficacy, safety or clinical readiness. R3 concerns a data-catalogue's
  coverage only.

## Stop condition
Set: *either* a source-traceable partner/breakpoint x natural-history table with an honest
computed description and stated power limits, *or* a precise statement of why published data
cannot support it. **MET, via the second branch, with a positive by-product.** The join is empty
at 0/23 (Wilson upper 14.3%) and the reason is precise and per-source. R3 is a genuine, checkable
finding. Two source routes are honestly unrecovered (`EGRESS_BLOCKED`), not circumvented.

## Tool-call and wall-clock count actually used
23 tool uses; 302,080 ms wall clock; 96,810 subagent tokens (harness-recorded).

## Next concrete action
Retrieve Panagopoulos 2002 Table 1 and Urbini 2018 Table 1 — the only two documents that could
move 0/23 off zero — through a legitimate egress route, then re-run the script with real covariate
cells. Note in advance that even a full pull yields at most ~23 non-independent cases, which
cannot support a partner-adjusted breakpoint analysis.

**Coordinator routing note:** R3 is a defect report against
`research/modalities/aso-per-junction-table.json`, which belongs to the PUB-ASO owner. W03 did not
edit it. It is routed here for the owner's decision, not acted on unilaterally. The coordinator
also declines to dispatch a GitHub Actions egress run for this on its own initiative: that is an
external act outside the campaign's stated scope.
