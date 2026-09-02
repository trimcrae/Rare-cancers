---
id: DOC-REPURPOSING-HYPOTHESES-REVIEW-RESPONSE
title: "Response to the simulated peer review of repurposing-hypotheses.md"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Record what the repurposing review changed in response to each point of the simulated internal review, and why each declined point was declined.
scope: One manuscript's revision. It reports no new experiment and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Response to the simulated peer review of repurposing-hypotheses.md

> **THIS RESPONDS TO A SIMULATED INTERNAL REVIEW WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S OWN
> REQUEST ([`repurposing-hypotheses-peer-review-2026-08-10.md`](./repurposing-hypotheses-peer-review-2026-08-10.md)).
> It is not correspondence with *Critical Reviews in Oncology/Hematology*, not a reply to a decision
> letter, and no editor or external reviewer has seen this manuscript. Nothing here should be
> represented, quoted or forwarded as journal correspondence.**

Revised files: [`repurposing-hypotheses.md`](./repurposing-hypotheses.md),
[`repurposing-hypotheses-cover-letter.md`](./repurposing-hypotheses-cover-letter.md),
[`figures/repurposing_design_figure.py`](../figures/repurposing_design_figure.py) and its rendered
PNG/PDF, [`../hypotheses/txgnn_predict.py`](../../hypotheses/txgnn_predict.py),
[`../hypotheses/build-candidates.mjs`](../../hypotheses/build-candidates.mjs) and the regenerated
`candidates.json`, [`../hypotheses/txgnn-emc-findings.md`](../../hypotheses/txgnn-emc-findings.md),
[`../hypotheses/METHODOLOGY.md`](../../hypotheses/METHODOLOGY.md),
[`submission_metrics.py`](../submission_metrics.py), `systems/graph/publications.json` and its
generated views, and `emc-systems-map.json`. New files:
[`../hypotheses/txgnn_exact_match_reanalysis.py`](../../hypotheses/txgnn_exact_match_reanalysis.py) and
its output `txgnn-exact-match-reanalysis.json`, and
[`tests/test_txgnn_exact_match.py`](../tests/test_txgnn_exact_match.py).

**Tally: 21 of the 30 revision items applied in full; the other 9 applied in part, each with a
named component declined and reasoned. None declined outright.** Section numbers below are those of
the REVISED manuscript, which was restructured (item 12), so they do not match the numbers in the
review. The nine partial items are 4, 7, 16, 20, 21, 24, 25, 26 and 28; in every case the declined
component needs either a network retrieval, a re-run of the model, or a fact no committed artifact
carries.

Measured after revision by `submission_metrics.py`: **6,384 words of main text** against a believed
8,000-word limit, **242-word abstract** against 250, **five display items** (one figure, four
tables) against six, and **25 references**.

---

## The revision list, item by item

### 1. Regrade imatinib from T3 (major 1) — APPLIED, taking the first of the two offered options

Imatinib is regraded **T2**. A single published case report is a case-level EMC signal, which is T2
under the scale the manuscript states one paragraph earlier; the alternative — an explicit rule
admitting a biomarker-matched single case with a durable response to T3 — would define the top tier
by whatever the one available candidate happens to have, and §3.1 now says so in one sentence rather
than leaving the choice implicit. Propagated to the Table 1 row label ("Clinical, EMC case"), the
abstract, §2.2, §5 Tranche 1, §6 and the firewall statement in §2.7 and §6. §2.2 states that the
scale as applied is three-valued and that nothing reaches T3. Applied to the data as well:
`build-candidates.mjs` and the regenerated `candidates.json` now carry
`evidenceTier: "T2-emc-case-signal"`, which also clears the `validate-research.mjs` warning that had
flagged the candidate as eligible to graduate.

**One thing the review did not catch, and it is the more serious half.** The manuscript said imatinib
"is the only candidate flagged as eligible to graduate into the cited clinical registry, pending
clinician review". It is **already in that registry**:
`research/data/emc-clinical-registry.json` → `emergingTreatments` lists "Imatinib (KIT inhibitor) —
only for KIT-mutant EMC", biomarker-restricted, attributed to the case report, and labelled "based
on a single case". So the sentence was false in fact, not merely inflated by a tier. §5 Tranche 1
now states that imatinib is not a hypothesis awaiting promotion, and why. The underlying tension —
the project's rule admits only T3 to the registry, and a T2 agent is in it — is recorded at its home
in `METHODOLOGY.md` §5 rather than resolved unilaterally here, because relaxing a patient-facing
firewall is a decision for a clinician review, not for a manuscript revision.

### 2. Replace the "three independent generation methods" framing (major 2) — APPLIED

The reviewer is right and the measured split is the better paper. The title, abstract, Highlight 1,
§1.2, §2.3, §6 and the cover letter now carry **12 from curation, 2 from the enumeration, 0 from the
model**. The nine enumerated genes are named in §2.3, with the finding that they reach **three of the
eight axes** and that the enumeration contributed nothing outside the kinase and nuclear-receptor
axes.

New title: *"Repurposing in an ultra-rare sarcoma: evidence and novelty are anti-correlated in
extraskeletal myxoid chondrosarcoma, and two computational routes added no candidate."*

**Adjudicated against the reviewer on one number.** The review says two of seven axes plus KIT. The
axis list itself was the defect: seven axes were named and two candidates were then filed under
ad-hoc labels outside them, "(KIT)" and "(kinome screen hit)" (the reviewer's minor 3). Receptor
tyrosine kinase drivers is a real, documented EMC vulnerability axis and is now the eighth; brigatinib
carries no axis, because its mechanism in EMC is undefined and that is the honest value. So the
coverage statement is **three of eight**, not two of seven. The axis is now a field of
`candidates.json` rather than a claim living only in prose, which is minor 3's substance.

### 3. Re-derive the model percentiles by exact matching (major 3) — APPLIED, but as a correction rather than a regeneration

The defect is real, worse than the review states, and is now fixed in code, corrected in prose,
registered in the appendix and held by test.

`txgnn_predict.relevant_ranks` matched a query to the ranking with
`next((i, d) for i, d in enumerate(ranked, 1) if q in d["drug"].lower())` over a list sorted by
**descending** score, so it returned the highest-scoring compound whose name *contained* the query.
Verified in the committed artifacts' own `matched` fields: `doxorubicin` → **13-deoxydoxorubicin**
(EMC and soft-tissue sarcoma) and **Zoptarelin doxorubicin** (chondrosarcoma), `apatinib` →
**Lapatinib**, `ifosfamide` → **Palifosfamide**.

**Why this is a correction and not a regeneration, which is the substantive judgement in this
response.** Re-deriving the true ranks needs the model re-run: only the top 100 drugs (EMC node) and
top 15 (each comparison node) of the 7,957-drug ranking were ever committed, `txgnn-cache` does not
exist on the remote, and no full ranking is anywhere in the repository or its history. So the honest
output is the exactly-matched subset plus three explicit unknowns, not three plausible numbers.
Concretely:

- **28 of 33 queried agents matched exactly**, and Table 2 reports medians over those with
  interquartile ranges: **20.9 (18.2 to 24.0)** at the EMC node, **17.6 (12.8 to 25.0)** at
  chondrosarcoma, **17.0 (15.0 to 18.9)** at soft-tissue sarcoma.
- The **best exactly matched agent at every node is masitinib** (52.4 / 69.9 / 61.2), not
  doxorubicin. Doxorubicin has been removed from all three "best-ranked" cells and is not replaced
  by the compound the matcher returned.
- **The true ranks of doxorubicin, apatinib and ifosfamide are reported as unknown** pending a re-run,
  in the manuscript, in `txgnn-emc-findings.md` and in the new re-analysis artifact, which stores
  `"true_rank_of_the_query": null` for each.
- Two queries (`fruquintinib`, `anlotinib`) are **absent from the graph** and are excluded rather
  than ranked low; §2.3 states this and the Table 2 caption gives the 28-of-33 denominator.
- The reason the published medians were **upper bounds** is now stated with its mechanism: an agent's
  own name contains its own query string, so the substring match returns a compound scoring at least
  as high as the agent.

Code: `name_matches_query()` matches the INN root exactly and admits only salt and hydrate forms;
`relevant_ranks` records `match: "exact"` or `match: "absent_from_vocabulary"`. The re-analysis is
`txgnn_exact_match_reanalysis.py`, whose `--check` fails if the committed artifact drifts from a
fresh derivation. `tests/test_txgnn_exact_match.py` asserts the four collisions that actually
happened, the salt-form cases, and that the agent wins over a higher-scoring lookalike.
`txgnn-emc-findings.md` carries the correction banner and its table now reports the three as unknown.

**Two further defects found while fixing this, neither in the review.** The median was
`sorted(present)[len(present) // 2]`, the upper-middle order statistic rather than a median (fixed).
And the claim that the comparators reproduced "the same implausible top hits" is only partly true:
the same compound ranks first at all three nodes and **5 of each top 15 are shared**, but the EMC
node's metabolic and lysosomal-storage character does not carry over to chondrosarcoma. §3.3 now
states what is shared and what is not.

### 4. The sparsity stress test (major 4) — APPLIED as the weakened conclusion; the graph-side measurement DECLINED as unavailable

The conclusion is weakened to what the data support: the low ranking of clinically active agents is
reproduced at two commoner sarcoma nodes, so it is **not unique to the EMC node**, and the cause is
**not settled** by the test. The sentence "the divergence is therefore not attributable to the
sparsity of EMC specifically" is gone from the manuscript and from `txgnn-emc-findings.md`, and is
registered in Appendix A.

The graph-side measurement is declined because it is not available at $0. Node degree and indication
count are properties of PrimeKG, which is not committed here; the deposited outputs carry only
ranked drug lists. Obtaining them means downloading the knowledge graph and re-running, which is the
same dependency as item 3. Rather than assert the comparators are data-rich, §2.3 and §3.3 state
that they are commoner **in the population**, that nothing in the run measures the graph-side
quantity, and that the held-out complex-disease split prevents any node from serving as a clean
data-rich control. Dispersion is reported (IQR, Table 2). The grouped-node and approximately-2023
vintage facts are in §2.3.

### 5. The GSE4303 module claim (major 5) — APPLIED, without upgrading it

"On the 16-tumour platform (GSE4303) every module was null" is deleted. §3.2 gives all six module
values on both platforms, names **bounce-back and integrated stress at t = +3.56** as the largest
module value on either platform, and states that the pre-specified rule does not read it. §2.5 states
that four of the six scored modules enter the decision rule and two were pre-declared context.

**Reported, not upgraded, and for a reason recorded before the data were seen.** The artifact's own
pre-stated expectation says the NFE2L1 bounce-back that limits proteasome inhibitors is
post-translational and therefore invisible to an array, so a module of transcripts is a weak proxy
for the mechanism it names. §3.2 carries that qualification alongside the value. The reviewer is
right that reporting a signal on the lead's own resistance axis as an absence was the wrong error to
make; treating it as support would be the opposite one.

### 6. WHO placement, "parent histology", and the comparator description (major 6) — APPLIED

§1.1 states EMC's WHO placement among malignant mesenchymal neoplasms of uncertain differentiation,
attributed to reference 13, whose abstract is held verbatim in the repository and states it.
"Parent histology" is gone from the manuscript. §1.2 states that because EMC is not a chondrosarcoma,
prior art in the cartilaginous tumours bounds nothing about EMC, and no novelty claim is qualified by
it. §3.3 describes chondrosarcoma and soft-tissue sarcoma as commoner comparator disease nodes
selected on node availability, notes that a genuinely close comparator would be another FET-fusion
sarcoma, and says none was available. The same correction is applied to `txgnn_predict.py`'s comment
and to `txgnn-emc-findings.md`, both of which called them "data-rich relatives".

### 7. The Chow 2007 target list (major 7) — APPLIED by reduction; retrieval DECLINED

Reduced to **methylthioadenosine phosphorylase**, the only item the committed prior-art record
supports, and the HDAC novelty qualification that rested on the untraceable part of the list is
removed from Table 3 and Table 4. Retrieval is declined for this revision: the dev sandbox proxy
blocks Europe PMC, a CI dispatch would introduce a new external dependency into a revision that is
otherwise entirely re-analysis of committed material, and the manuscript is not weakened by the
reduction, since the sentence was bounding a novelty claim that is now unqualified and correct. The
same record's observation that the abstract describes EMC as a distinct fusion-defined entity is used in
§1.2, which is a use the committed record does support.

### 8. The anti-angiogenic class claim (major 8) — APPLIED in full

§1.1 now cites the primaries, using only identifiers, titles and author strings present in
`emc-fusion-partner-pooling.json` and the registry's citation map. The pazopanib phase 2 (reference
5) is reported as the primary reports it: 26 entered, 23 met the modified intention-to-treat
eligibility criteria, 22 were evaluable, **four (18%, 95% CI 1 to 36)** had a RECIST objective
response. The sunitinib series (reference 6) is reported as **6 partial responses, 2 stable, 2
progressive among 10 patients**. The 2025 review is kept for the synthesis it is. The 19-month median
progression-free survival is **labelled as a reading of the review** rather than of the primary,
which is what `emc-systemic-therapy-pooling.json` shows it to be. The abstract no longer carries a
bare 18%.

### 9. The prior-art screen (major 9) — APPLIED, as prose rather than a supplementary table

§2.4 is new and reports the screen as a Review should within the constraints of what was recorded:
database and date, that the screen served four separate publication endpoints across five query
buckets, the per-bucket record counts (1 / 0 / 3 / 0 / 1), that the 322 records and 238 full texts
are totals across all five, that **the repurposing bucket returned zero records** so nothing was
screened by hand for this question, that **no query strings are recorded** so the search is not
reproducible from the artifact, and that **no positive control was included** so the queries'
sensitivity is unknown. The enumeration's exclusion list is given with its size and composition: ten
first-token roots, six of them drug names and four not, with exactly two of the 106 enumerated drugs
classified as known-active in EMC. §6's sixth limitation is kept and strengthened to say the novelty
claim for each of the fourteen candidates rests on a search whose recall has not been demonstrated.

The exact query strings are not supplied because they exist nowhere in the repository. Reconstructing
them from the returned records would be a guess presented as a method. A supplementary table was not
added because it would have made a sixth display item out of five numbers.

### 10. The immune axis and the sunitinib-plus-nivolumab cohort (major 10) — APPLIED

The cohort is cited (reference 17, from the registry's verified citation record) in Table 3, §4.4 and
§7: 24 accrued, 23 evaluable, 16 progression-free at 6 months, 2 partial responses, 12-month overall
survival 90%, a conference abstract with no full paper indexed. The "no EMC data" grade is restricted
to the **vaccine component**, and §4.4 states that the checkpoint axis is not untried. The registry's
own recorded caveat — that the abstract states its primary endpoint as both 77% and 16/23, and that
its best-response counts sum to 22 rather than 23 — is carried into §4.4 and §7, because a cohort
cited as the field's evidence ceiling should be quoted with the reason it is a weak ceiling.

### 11. The four passages a clinician could act on (major 11) — APPLIED in full

- **"no biomarker required" is deleted.** The PPARγ row's next experiment is now to resolve the sign
  of the axis in an EMC model before any agent is considered.
- **"oral and globally available" is deleted** from the lead description.
- **"expanded-access or n-of-1 study" is gone** from Tranche 1, replaced by a statement of what
  evidence would be needed before any clinical step could be contemplated, with the
  sarcoma-specialist and ethics requirement adjacent rather than two sections away.
- **The combination entries are reworded** as "the combinations reported in the source screen", in
  Table 3 and Table 4.

The column heading is now "The next experiment", and every cell in it names a preclinical or
study-design step. The section closes with a sentence stating that nothing in Table 4 is a proposal
to give an agent to a patient.

### 12. Restructure so the negatives lead (major 12) — APPLIED, including the title

Adjudicated and agreed. The menu dates as the drug landscape moves; the structural result and the two
negatives do not. New structure: **§3 "What the three approaches returned"** holds the
evidence-versus-novelty analysis (§3.1), the two failed proteasome rationales (§3.2) and the graph
model with its stress test (§3.3), all at the same level. The menu is **§4**, supporting §3 rather
than fronting the paper. The abstract's second half is the three findings. The title follows.
Appendix A registers the previous ordering.

### 13. Rewrite the Critical View outward (major 13, minor 15) — APPLIED

§7 is rewritten to the six items requested: the field's evidence ceiling (two prospective EMC cohorts,
22 and 23 evaluable patients, one of them a conference abstract whose counts do not reconcile;
everything else retrospective, single cases or ex-vivo work in one or two models); untested
cross-model reproducibility, with the specific statement that no hit from either patient-derived model
system has been tested in the other; the unknown denominator of unpublished negative off-label
experience and what it bounds; the pace of graph-model adoption in rare disease against its
validation, with the concrete test this paper's result suggests; what would change our reading of each
lead; and the infrastructure argument, which is expanded into its own §5.1 with three named components
rather than three sentences and one citation.

"A set of five rather than of fourteen" is corrected to **three of fourteen**, and Table 4's caption no
longer claims that all its rows carry functional data: it states that three of the five do and names
the evidence type of each row.

### 14. Apply the registered corrections to the deposited dataset (major 14, minor 3) — APPLIED

All three, in `build-candidates.mjs`, with `candidates.json` regenerated from it: the unsupported
`~5%` figure is gone from `landscapeNote` and from the imatinib `keyRisks`; "CD117/KIT is expressed in
roughly half of cases" is replaced by the verified range with its correct attribution. Each carries a
one-line superseded note in the field itself, so the dataset registers the correction rather than
silently losing it. An `axis` field is added to every candidate, with the vocabulary and the
seven-to-eight change recorded in a new `axes` block.

**A fourth correction the review did not list, found by the same check.** `candidates.json` still
carried "Carfilzomib sensitivity identified and validated across **two** patient-derived EMC ex vivo
models" — the exact claim Appendix A has registered as superseded since 2026-08-06. It is corrected in
the generator and the dataset. The reviewer's point generalises: a correction registered in an
appendix but not applied to the deposited data is not a correction, and this was the case that had
been missed.

### 15. Separate any *KIT* mutation from an imatinib-sensitive-class mutation (major 15) — APPLIED

§1.1 states the exon-11 in-frame deletion in 1 of 20 EMCs, identifying exon-11 as the
imatinib-sensitive class in gastrointestinal stromal tumour, and separately the p.E554K mutation in 2
of 48, with the statement that no source consulted here characterises that variant as
imatinib-sensitive. The combined "approximately 4%" is gone from §1.1, §4 and the cover letter, and
§6's fourth limitation states that the addressable minority is smaller and less certain than the sum.
The same separation is applied to the imatinib entry in `candidates.json`.

### 16. The enumeration filter (major 16) — APPLIED; the optional filter change DECLINED

§2.3 describes the filter as implemented: **approval status alone**, with interaction types recorded
and never filtered on. It reports 106 approved drugs, 10 already catalogued, 2 known-active, **94
newly surfaced**, and names nine of the 94 that a mechanism filter would have removed. **Rabeprazole
is corrected to a proton pump inhibitor**, with the five VEGFR-family and PDGFR-family edges that
surfaced it named as database artifacts.

Implementing an interaction-type filter and regenerating is declined. It requires a live DGIdb query,
which would replace a dataset with a recorded retrieval date of 2026-06-20 by one retrieved during a
revision, and every number in §2.3 and §4.1 would then describe a different query than the one the
paper reports. The precision problem is real and is now visible in the text, which is the outcome the
reviewer wanted; changing the method mid-revision is not.

### 17. Restrict the convergence claim (major 17) — APPLIED

§2.3 restricts the convergence claim to the angiogenesis and *KIT* clusters and names the spurious
edges: **carfilzomib via *KDR*, venetoclax via *KIT*, palbociclib via *RET* and *MET***. One further
example is added from the same check: **entrectinib matched through kinase edges rather than through
*NTRK*, which is not in the target list at all** — so the enumeration could not have reproduced that
catalogue entry through its actual mechanism. §6's second limitation states that the coverage bias the
enumeration was introduced to mitigate is mitigated on two axes and nowhere else.

### 18. Name the comparator arms and GSE4303's instrument limits (minor 7, minor 8) — APPLIED

§2.5 names both comparator arms with their counts (GSE24369: 17 low-grade fibromyxoid sarcoma, 6
desmoid fibromatosis, 6 fibrosarcoma; GSE4303: 3 dermatofibrosarcoma protuberans, 3 gastrointestinal
stromal tumours), states that low-grade fibromyxoid sarcoma is itself FET-rearranged so a shared
fusion-driven programme would be subtracted out, and describes GSE4303 as a two-colour log-ratio
array with about 63% probe-to-symbol mapping and 1,662 of 1,973 requested genes measurable — a weak
instrument on which a null is close to uninformative.

### 19. No EMC cell line in DepMap (minor 9) — APPLIED

Stated twice, in §2.5 and again in §3.2 where the dependency numbers are given, with the artifact's
own framing that the read is a prior transferred from other sarcomas rather than EMC data.

### 20. Qualify the zaltoprofen rows; retrieve the Higuchi full text (minor 11, minor 12) — APPLIED in part; retrieval DECLINED

The qualification is now in the tables themselves rather than only in the prose section: Table 3's
zaltoprofen row and Table 4's PPARγ row both carry the unresolved direction and the H-EMC-SS identity
problem in the cell a reader would quote. To be explicit about what that second qualifier is, since
this file names the model: the identity of H-EMC-SS (ACH-001519) is DISPUTED — Cellosaurus records a
curated caution that it does not harbour the EWSR1 fusion that defines the disease — so nothing here
reads it as EMC evidence, and it is named only as a reason a row was weakened. The retrieval is declined for the same reason as item 7,
and the manuscript takes the reviewer's stated alternative: §6's fifth limitation says plainly that
the strength of the only in-vivo signal in the menu **cannot currently be stated**, because the paper
is not open access and its full text was not retrieved for this work. §7 repeats it as one of the
three gaps bounding the paper.

### 21. The VEGFR list and regional approval (minor 13, minor 14) — APPLIED in part; naming regions DECLINED

The list is reconciled to **nine agents** in Table 3 and in Tranche 2, matching the deposited dataset;
fruquintinib is restored rather than silently excluded. Naming which agents are approved in which
regions is declined: no committed artifact carries per-region regulatory status, and writing it from
recollection is the failure mode this repository's citation rules exist to prevent. What the
manuscript says instead is checkable and is the fact a trialist needs — DGIdb's `approved` flag is a
single global property that does not resolve jurisdiction, so regional status differs across the class
and must be established from regulatory sources before any design.

### 22. Table caption and `evidenceStrength` (minor 4, minor 5) — APPLIED

Table 3 now has **14 rows for 14 candidates**: the anthracycline-combination entry is given its own
row rather than folded into the carfilzomib row, which is also what the dataset does. §2.2 states that
Table 3 is ordered by the strength of EMC-specific evidence and names the ordinal `evidenceStrength`
field that records it in the dataset.

### 23. DGIdb query date and version (minor 6) — APPLIED

§2.3 gives the query date (20 June 2026), the interface (the GraphQL API at dgidb.org), the number of
genes queried (nine, named), and states that the artifact records no database release version. The
last is a limitation of the record rather than an omission from the prose, and saying so is more
useful than leaving a version unstated.

### 24. Reference completion and expansion (minor 18, minor 19) — APPLIED in part; the 45-to-70 target DECLINED

The completion note is removed from the body of the manuscript and its content moved into the
editorial comment, which is stripped at submission; it is editor-facing and states that the reference
list is not submission-ready, which is a repository fact rather than a claim a published paper should
carry. Five references are added, every one traceable to a committed retrieval record: the pazopanib
phase 2 with its erratum, the sunitinib series, the IMMUNOSARC II EMC cohort abstract, the
anthracycline-based chemotherapy series and the two-institution retrospective series. Reference 7
gains its PMID. Twenty becomes twenty-five.

Expanding to 45 to 70 is declined, and the reason is not effort. Every identifier, title and author
string in this repository's manuscripts must trace to a committed retrieval record; a citation written
from a model's recollection is what produced a fabricated PMID here on 2026-08-07, and the gate that
now catches it (`lint_citations.py`) exists because nothing else did. Adding twenty-five references to
reach a target would mean either fetching and verifying twenty-five papers, which is a separate piece
of work with a network dependency, or writing them from memory, which is prohibited. Where the review
identifies a genuinely under-referenced argument, the manuscript answers it with evidence rather than
with a citation: §2.3's account of target-to-drug false positives is demonstrated on this paper's own
four measured examples, which is stronger than citing a methodological review; §5.1 is expanded with
three named components; and §3.4's immune candidate now rests on an EMC cohort rather than on a
melanoma trial alone.

### 25. A commit hash or archived snapshot (minor 17) — APPLIED in part

§8 states that every artifact carries the date it was generated and that a versioned archive of the
repository state will be deposited with a citable identifier at submission. A commit hash cannot be
embedded in the commit that contains it, and a hash of an earlier commit would point at a state that
is not the one being described, so the specific mechanism the reviewer asks for is deferred to the
deposit step rather than faked here.

### 26. Remove Appendix A and the HTML comment from the submission (minor 20, minor 22) — APPLIED in part

Both are marked as stripped at submission, in the first line of the editorial comment and in a banner
on Appendix A, and the editorial comment now names both as the two things removed. Neither is deleted
from the repository copy, because this repository keeps **one file per deliverable**: a parallel
condensed draft has drifted out of sync and self-contradicted here before, and the fix for that was a
standing rule against maintaining two versions of a manuscript. The correction register is also
required by the project's own rules and is genuinely valuable; the reviewer says as much.

Confirming the journal's actual limits from its author guidelines is declined as not achievable: those
pages return HTTP 403 both from this sandbox and from a GitHub Actions runner, which is recorded with
the HTTP statuses in `venue-fee-routes-2026-08-10.json`. The editorial comment states that the limits
remain search-derived, and `submission_metrics.py` records the same in its output.

### 27. Cut the structure-narrating sentences (minor 21) — APPLIED

All five named sentences are gone: "Table 1 shows the structure at a glance", "which Table 3
isolates", "The presentation in section 3 does not use that composite, for the reason given there",
"That short list is the practical output of the exercise", and "That is why approved agents hitting
PPARγ … dominate the upper rows of Table 2". The rewrite was checked with `lint_style.py`, which
enforces journal register on this file and reports it clean at 0.1 bold runs and 1.8 em-dashes per
1000 words.

### 28. Replace the Highlights; re-check the abstract (minor 1, minor 2) — APPLIED, except one part declined

The five Highlights are replaced with the set the review proposes: the anti-correlation and the empty
cell; that the one clinically evidenced candidate is the only one already reported; the two failed
pre-specified rationales; the graph model's bottom-quintile placement of the two most active agents;
and the fourteen candidates across eight axes with explicit tiers. Four negatives and one positive.
All five are within 85 characters. The abstract is 242 words against the 250-word limit, re-measured
after every other change.

**Declined:** deleting "No efficacy is claimed for any agent named here" from the abstract. The
abstract is the part of this paper that will be read alone, indexed alone and quoted alone, by
readers including patients and their families searching the disease name. In a paper that names
fourteen real, mostly approved drugs, nine words carrying the disclaimer into the only section most
readers will see is a better use of the space than a fifth finding. It duplicates the scope box by
design.

### 29. Figure 1 (minor 23) — APPLIED

The generator and the rendered PNG and PDF are updated. The caption and figure title are reconciled
with the revised framing: "the generation design and the firewall", not "the three-method design".
The dashed convention is now explained in a legend line ("Dashed outline and arrow: a path that ran
and contributed no candidate"). The divergence label is repositioned onto its arrow. Two additions
beyond the request, both following from item 2: the arrows from curation and enumeration are labelled
**12 of 14** and **2 of 14**, so the figure shows the split the paper is now about; and the catalogue
node reads "tiers T0–T2" rather than "T0–T3", following item 1. The firewall's outgoing label was
overlapping both boxes it sat between and is lifted clear.

### 30. The cover letter (minor 26, minor 28) — APPLIED

The title is updated; the "three independent methods" claim is replaced by the measured split in its
own paragraph; the "*KIT*-mutant minority of roughly four per cent" is replaced by the separated
claims and a statement that the size of the minority is itself uncertain; the proteasome sentence
gains the clause item 5 requires, noting the context module reported alongside the two negatives; and
the code defect and its correction are disclosed. The clinical-review request is made specific, naming
the tier assignments, the size of the addressable *KIT*-mutant population, and every entry in Table
4's next-experiment column.

---

## Minor points needing no change

**Minor 10** (the DepMap numbers check out) and **minor 27** (the two-part AI disclosure is correctly
separated and worded) reported no defect and none was introduced. **Minor 16**'s substantive half is
handled under item 4; the parenthetical about the held-out split is now its own sentence in §3.3.
**Minor 24** and **minor 25** are measurements rather than requests, and both are re-measured above.

## Findings from this revision that the review did not raise

1. **The registry already lists imatinib**, so the manuscript's "eligible to graduate" sentence was
   false in fact and not merely inflated by a tier grade (item 1).
2. **`candidates.json` still carried the superseded two-model carfilzomib reading**, which Appendix A
   had registered as corrected on 2026-08-06 — the same class of defect as major 14, in a row the
   review's audit did not reach (item 14).
3. **`submission_metrics.py` counted one display item where a reviewer counted five.** Its table
   pattern required a `**bold**` caption, and this manuscript italicises them, so the gate whose job
   is to catch a display-item breach was reading four tables as zero. Fixed to accept both emphasis
   forms; no other manuscript's count changes.
4. **The median in `txgnn_predict.py` was the upper-middle order statistic**, not a median (item 3).
5. **"The same implausible top hits" was only partly true** across the three disease nodes (item 3).
6. **The seven-axis list did not cover two of the fourteen candidates**, which had been filed under
   ad-hoc labels outside it (item 2).

## Checks run after revision

`lint_consistency.py`, `lint_style.py` and `lint_claims.py` exit 0 across the repository;
`submission_metrics.py` reports this manuscript within every limit; `pytest
research/manuscripts/tests/test_txgnn_exact_match.py` passes 12 tests;
`txgnn_exact_match_reanalysis.py --check` and `validate-research.mjs` pass. `systems_check.py
--check` is at 0 ERROR after the generated views were rewritten with `--write-views` rather than
hand-edited. `lint_citations.py` reported 0 ERROR immediately after this revision; every one of the
33 errors it reports at the time of writing is attributed to
`research/manuscripts/nr4a3-fusion-transcriptional-output.md`, which gained unanchored DOIs from a
concurrent session, and none to any file touched here.

⚠ **`emc_systems_map_check.py --check` still reports two errors, and neither is from this revision.**
Both are `[O3]` on `research/manuscripts/emc-surface-target-landscape.md`, whose registered
correction marker `Amendment 1` is no longer in the file — so the registry says a disputed cell-line
identity is disclosed there and the file does not disclose it. That manuscript was being revised by
another session in the same working tree while this one was; the fix belongs to whoever is editing
it, and editing it from here would collide with them. It is flagged rather than left for a commit to
turn `main` red, because O3 is a medical-integrity gate, not a formatting one. This manuscript's own
O3 obligation for the same object is satisfied: it is registered `survives_relabelled` with the
marker `PPARγ DIRECTION — UNRESOLVED (2026-08-06)`, which Appendix A carries.
