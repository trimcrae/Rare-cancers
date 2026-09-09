---
id: DOC-PORTFOLIO-INVESTIGATION-CLOSED-ROUTES-2
title: "CLOSED-ROUTES-2 — nine retrieval closures this campaign evidenced, and the nine the standing negative record does not carry"
level: L4
kind: coverage-reconciliation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# CLOSED-ROUTES-2 — reconciling the standing negative record against what this campaign actually closed

⛔ **This lane catalogues closures. It does not test, probe, retry or reopen any of them.** No
network request of any kind was issued from this lane, to any host, closed or open. Every closure
below is established by the evidence its lane retained at the time — a recorded `curl` exit code, a
recorded empty body, a recorded absent artifact — never by a fresh refusal of my own. Routes
**B1/B2** (Ensembl FASTA), **B4** (surfaceome), **B8** (HLA-C) and **B9** (PMID 22592656) stay
closed; naming one in a catalogue is not relabelling it, and nothing here is a plan or an invitation
to retry it.

## 1 · The question

`research/manuscripts/methods-record/closed-routes-negative-record.md` is this repository's standing
record of closed routes and has never had a lane. OPUS-CAPACITY-CAMPAIGN-20260908 produced a large
amount of newly evidenced route-closure fact that currently exists only inside individual lane
directories. **Which of those closures does the standing record already carry, and which are
uncatalogued?**

## 2 · Merit

Negative retrieval fact is the most easily lost evidence in this repository and the most expensive
to re-establish, because re-establishing it means re-attempting a route that is refused — precisely
the act the fences forbid. A closure that lives only in one lane's `checks/` directory will be
re-attempted by the next worker who needs the same input, and each re-attempt is a fence violation
waiting to happen. Consolidating them into the standing record is what makes "do not retry this"
enforceable by reading rather than by memory. It is patient-relevant only indirectly, through the
results these closures bound: what the trial-eligibility screen may claim, what the vital-tissue
liability verdict actually screened, what fraction of the population an HLA-C-restricted epitope
would serve.

## 3 · The evidence gap, named exactly

The record's declared scope is **the seven therapeutic routes filed against `PUB-CLOSED-ROUTES`** —
`RT-EWSR1-PROTEIN`, `RT-FET-LC-LIGAND`, `RT-DBD`, `RT-RXR`, `RT-SYNPROMOTER`, `RT-HDAC-BET`,
`RT-6MP` — closed on argument over facts already on record. Its §9 ("What is missing") lists what
the *taxonomy* does not yet settle. **It contains no retrieval or data-access closure at all.** The
gap is therefore not "the record is out of date on the seven"; it is that a second, distinct class
of closure — a source that returns nothing, a body that arrives stripped, an artifact built at run
time from a network source and so absent from this checkout — has accumulated across nine lanes with
no home in the record.

## 4 · The step taken

I enumerated every closure the named lanes evidenced, attached each to its lane's **own** evidence
path, scanned the standing record for each route's identifying tokens, and generated (never
hand-wrote) an unapplied diff adding only the rows the record does not carry.

### Result

**Nine routes catalogued. Zero are in the record. All nine are uncatalogued.**

| route | lane | in record |
|---|---|---|
| `CR-GPL3290-ACCESSION-BRIDGE` — the EST-accession→symbol bridge is built at run time from GEO and is not in this checkout, so GPL3290 readability can only be bounded | FUSION-OUTPUT-3 | **no** |
| `CR-HPA-RNATSS-EMPTY` — `rnatss` is already in the producer's query string and comes back empty, so `vital_tissue: []` on all 45 rows: the 21-tissue vital screen has never had an input | SURFACE-2 | **no** |
| `CR-CLINICALTRIALS-GOV-EGRESS` — CONNECT tunnel failed, response 403; `curl` exit **56** | STRATEGY-ARCH-2 | **no** |
| `CR-NO-LOCAL-TRANSCRIPTOME` — no local cache and no local transcriptome anywhere in the checkout; the reference half of a k ≥ 6 re-run is route B1/B2 and stays closed | MATRIX-ADDRESS-3 | **no** |
| `CR-FOUR-REFERENCES-NO-PMC` — references [2], [8], [9], [14] have no PubMed Central record at all, agreed by two independent retrieval modes | REPURPOSING-3 | **no** |
| `CR-PMC10054153-EMPTY-BODY` — a PMC record that returns an empty `full_text` reproducibly under both accepted id forms | REPURPOSING-3 | **no** |
| `CR-MORIOKA-TABLES-DROPPED` — PMC4946242 returns abstract and narrative only; all tables, figures and legends stripped | CARE-DELIVERY-3 | **no** |
| `CR-HLA-C-NO-FREQUENCY-B8` — the committed AFND snapshot carries loci A and B only and route B8 is closed, so the HLA-C population share is UNKNOWN and stays UNKNOWN | HLA-COVERAGE-2 | **no** |
| `CR-Q92570-3-SEQUENCE-ABSENT` — the NR4A3 isoform-3 sequence is not in this checkout, so the peptide offset is carried rather than re-verified; TrEMBL sits outside both novelty strata | NEOANTIGEN-4 | **no** |

The zero is the finding. It is also the reason the diff files the rows under a **new** heading
(§9A) rather than into §4's table of seven: these are not therapeutic-route closures and must not be
read as though they were. That is a scope extension to a live manuscript, so the diff is
**UNAPPLIED** and the decision is the parent's, not this lane's.

**Artifact.**
* `closed-route-coverage.json` — the coverage table: route · closure statement · closure class ·
  evidencing lane · evidence locator(s) · per-token record-scan hits · `in_record` yes/no, plus the
  record's sha256 at the moment of use.
* `UNAPPLIED-closed-routes-additions.diff` — adds only the uncatalogued rows, each carrying its
  lane's own evidence path.
* `build_coverage.py`, `generate_diff.py` — the generators.
* `checks/01`–`06`, one directory per attempt, with `command.txt`, `stdout.txt`, `stderr.txt` and
  the real `exit_code.txt`.

**Validation.** `git apply --check` on the generated diff: **exit 0**, no output
(`checks/05-git-apply-check/`). The diff was produced by `difflib.unified_diff` against the file
bytes as read at generation time — **generated, never hand-written**, which is the specific failure
HLA-COVERAGE-2 hit at exit 128. Two independent fences are enforced in code and would refuse rather
than emit: a row with no evidence locator exits `3`, and a locator that does not exist on disk exits
`4`. The insertion anchor (`## 10 · References`) is asserted to match **exactly once**; any other
count exits `6`/`7`. The record's sha256 at generation is
`e091b1cdf0b660b3ba947680b99a923c27f53565a6e4137d888bde6a6dbcf920`, matching the value the proposal
pinned, and it is byte-identical after the run (`checks/06`) — the diff is genuinely unapplied.

**A preserved failed attempt.** `checks/02-build-coverage` ran to exit 0 but reported
`CR-NO-LOCAL-TRANSCRIPTOME` as **in-record** on a false positive: the bare token `B1` matched inside
the record's own sha256 digest (`e091**b1**cd…`). The scan now requires alphanumeric boundaries and
uses the longer forms `route B1` / `B1/B2`. Both runs are retained; `checks/02` is the wrong answer
and is kept as such. The corrected run is `checks/03`.

**Provenance.** Repo `/home/user/Rare-cancers`, shared checkout read concurrently — no copy, no
worktree. Inputs: the standing record, and the `FINDING.md` plus `checks/` of FUSION-OUTPUT-3,
SURFACE-2, STRATEGY-ARCH-2, REPURPOSING-3, CARE-DELIVERY-3, HLA-COVERAGE-2, MATRIX-ADDRESS-3 and
NEOANTIGEN-4, all read-only. The `clinicaltrials.gov` refusal is quoted from
`PUB-STRATEGY-ARCH/checks/01-connectivity-probe/` — the probe another lane ran and recorded, read
here as a file. **No network egress from this lane.** No `git add`, `commit`, `push`, `preflight`,
subagent, GPU, paid API, publication or outreach. Writes confined to
`…/PORTFOLIO-INVESTIGATIONS-2026-09-08/CLOSED-ROUTES-2/`.

**Limitations.**
1. **`in_record` is a token scan, not a semantic reading.** It answers "does this document mention
   this route at all", which for a document that mentions none of them is decisive in the negative
   direction and would be weaker in the positive one. A future row that scans `yes` needs a human
   read before it is trusted.
2. **The nine are the closures the eight named lanes evidenced**, not every closure this campaign
   produced. Rows the lanes did not evidence with their own path were not added — that is the
   proposal's rule and it was enforced by refusal, not by judgement. B4 (surfaceome) and B9 (PMID
   22592656) are standing closures with no evidence path inside these eight lanes, so they are
   **absent from the table by that rule**, not by a finding that they are catalogued.
3. **The diff extends a live manuscript's declared scope** from seven therapeutic routes to seven
   therapeutic routes plus a retrieval appendix. That is an editorial call this lane is not
   authorised to make, which is why it is unapplied.
4. **A catalogue entry changes nothing about a closure's status.** No route is reopened, downgraded,
   relabelled or made retryable by appearing here.

**Stop condition.** Reached. The coverage table and the diff exist and the diff checks clean. This
lane stops. It does not apply the diff, does not enlarge the row set by attempting any route, and
does not re-probe anything.
