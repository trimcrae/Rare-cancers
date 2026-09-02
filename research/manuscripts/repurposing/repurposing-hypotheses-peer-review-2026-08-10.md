---
id: DOC-REPURPOSING-HYPOTHESES-PEER-REVIEW
title: "Simulated peer review — repurposing-hypotheses.md (Critical Reviews in Oncology/Hematology)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A simulated journal peer review of the repurposing review, and the revision list it generates.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Simulated peer review — repurposing-hypotheses.md

> **THIS IS A SIMULATED INTERNAL REVIEW WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S OWN REQUEST.
> It is not correspondence from *Critical Reviews in Oncology/Hematology*, not a decision letter,
> and no editor or external reviewer has seen this manuscript. The journal name appears only to fix
> the standard being applied. Nothing here should be represented, quoted or forwarded as a journal
> review.**

Manuscript: `research/manuscripts/repurposing-hypotheses.md` (dated 2026-08-09).
Also read: the cover letter, `figures/repurposing-fig1-design.png`, and — as background, not as
submitted material — `fact-check-log.md` and `repurposing-hypotheses-review.md`.

Reviewer standpoint: medical oncology with a sarcoma practice, plus working familiarity with
drug-repurposing methodology, target-to-drug enumeration and knowledge-graph link prediction.

Because the underlying data and code are open, I checked the load-bearing numbers against the
artifacts rather than taking them on trust. That is where most of the points below come from, and
several of them are things no ordinary reviewer could have found. I want to say at the outset that
the practice of committing the artifacts alongside the prose is the reason this review can be
useful, and that most manuscripts I review would not survive the same treatment as well as this one
does.

---

## Recommendation

**Major revision.**

This is a careful, unusually self-critical manuscript on a disease that badly needs one, and its
central observation — that in an ultra-rare tumour, evidence strength and novelty are structurally
anti-correlated, so the only candidate with clinical evidence is the only one already tried — is a
real and transferable point that I have not seen made this cleanly elsewhere. I want it published.
But three things must change before it can be. First, several load-bearing statements do not match
the artifacts they cite: the model's best-ranked agent is not doxorubicin in any of the three rows
of Table 4, one of the two pre-specified proteostasis platforms is reported as uniformly null when
its largest module reading sits on the proteasome-resistance axis, and the sole T3 candidate is
graded a tier above what the manuscript's own tier definitions allow. Second, the "three
independent generation methods" framing in the title, abstract and Highlights is not what the data
show: one method produced twelve of the fourteen candidates, the second contributed to two of them
on the kinase axis alone, and the third contributed none — which is a more interesting finding than
the one being claimed, and should be stated. Third, the paper names real approved drugs and, in two
places, edges from hypothesis into something a clinician could act on. None of these requires new
data. All are fixable by re-analysis of what is already committed, by restructuring, and by
weakening language to what the evidence supports.

---

## MAJOR POINTS

**1. Section 2.2, Table 1, Table 2, Section 4 (Tranche 1), Section 5. The one T3 grade contradicts
the paper's own tier definitions, and T3 is also the firewall threshold.**

Section 2.2 defines the scale: "T3 denotes prospective or substantial clinical evidence in EMC; T2,
a case-level signal in EMC or in a very close relative." Table 2 then records imatinib's EMC
evidence as "Clinical: one patient, 3 years of stable disease [7]", and Section 4 calls it "the only
candidate at T3". A single published case report is the textbook instance of T2 under the definition
given one paragraph earlier. `research/hypotheses/candidates.json` records the same tension in its
own fields: `evidenceTier: "T3-emc-clinical-evidence"` sits beside `keyRisks: "Single case; ..."`.

This is not a bookkeeping quibble, for two reasons. It is the single grade on which the paper's
headline structural claim rests — remove it and the "clinical, EMC patient" row of Table 1 is empty
and the anti-correlation becomes a much starker statement about a disease with no clinical
repurposing evidence at all. And Section 5 makes T3 the bright line the firewall enforces: "only a
candidate reaching direct EMC clinical evidence at T3 may migrate into the project's cited clinical
registry." A tier inflated by one step is therefore also a candidate promoted across the one barrier
the paper builds to protect patients.

*What would resolve it.* Either regrade imatinib as T2 and rewrite the Table 1 row, the Tranche 1
paragraph and the abstract accordingly — which strengthens rather than weakens the paper's thesis —
or add an explicit, defended tier rule stating that a molecularly characterised, biomarker-matched
single case with a durable response counts as T3, and say plainly in Section 2.2 that T3 in this
paper can rest on n = 1. I would take the first option. Note also that no candidate in the whole
menu is graded T2, so the scale as used is really three-valued; say so.

**2. Title, Abstract, Highlight 1, Section 2.3, Section 6. "Three independent generation methods" is
not what the artifacts show, and the true picture is a better finding.**

I checked which candidates the enumeration actually contributed to.
`research/hypotheses/candidates.json` carries `enumeratedAgents` and `enumerationProvenance` on
exactly two of the fourteen entries: the imatinib entry (seven alternative KIT inhibitors) and the
VEGFR-TKI entry (nine agents). The other twelve carry neither field and are pure single-rater
curation. The graph model, by the paper's own account, promoted nothing. So the generation split is
12 / 2 / 0, not three parallel methods.

The coverage limit is structural, not incidental. `research/hypotheses/targets.json` contains nine
genes: KIT, KDR, FLT1, FLT4, PDGFRA, PDGFRB, RET, MET and PPARG. Of the seven vulnerability axes
named in Section 2.1, the enumeration had a target on two — angiogenesis and PPARγ/nuclear receptor
— plus KIT. It had no target at all for the fusion and transcriptional programme, epigenetic
dependencies, the cell cycle, apoptosis and proteostasis, or the immune microenvironment. Five of
seven axes were therefore never enumerated, and the abstract's "Curation and enumeration converged
on 14 candidates across seven vulnerability axes" and Highlight 1's "Three independent methods
yielded 14 existing-drug candidates across seven axes" both overstate what happened. Highlight 1
also contradicts Highlight 5 in the same list.

*What would resolve it.* Rewrite the design as what it is: one primary generation method
(literature-driven curation), one partial systematic cross-check confined to the kinase and
nuclear-receptor axes, and one independent model run that returned nothing usable. State the nine
genes and the two-of-seven axis coverage in Section 2.3, and state that the enumeration's yield of
new candidates outside the kinase axis was zero. This is a more honest and more interesting claim
than triangulation, and it sets up the negative findings the paper should be leading with (point 12).

**3. Section 5 and Table 4. The "best-ranked of our agents" is not doxorubicin in any of the three
rows, and every percentile in the table is an upper bound.**

`txgnn_predict.relevant_ranks` matches a query to a model output by substring against a
descending-sorted list: `next((i, d) for i, d in enumerate(ranked, 1) if q in d["drug"].lower())`.
It therefore returns the *highest-scoring* compound whose name contains the query string. The
committed artifacts record the consequences explicitly, in the `matched` field:

- EMC row: `doxorubicin` matched **13-deoxydoxorubicin** (74.7th percentile).
- Chondrosarcoma row: `doxorubicin` matched **zoptarelin doxorubicin** (80.0th percentile) — a
  different investigational conjugate again.
- Soft-tissue sarcoma row: `doxorubicin` matched **13-deoxydoxorubicin** (71.5th percentile).

All three "doxorubicin" cells in Table 4 name a compound the model did not rank. Two further
mismatches sit inside the medians: `apatinib` matched **lapatinib**, and `ifosfamide` matched
**palifosfamide**. The lapatinib collision is notable because the repository's other enumeration
script guards against precisely it — `enumerate-drugs.mjs`'s self-test asserts that "Lapatinib must
NOT match apatinib" — so the fix is known in one place and absent in the other. Two further queries
(`fruquintinib`, `anlotinib`) matched nothing at all and silently drop out of the denominator.

Because the matcher takes the best substring hit rather than the exact agent, all three medians
(21.0, 17.7, 17.4) are upper bounds on the model's true ranking of the named agents, not point
estimates. The same error is propagated in `research/hypotheses/txgnn-emc-findings.md`, which lists
"doxorubicin 2017 / 74.7 — our only above-median lead".

*What would resolve it.* Re-derive Table 4 from exact name matching against the model's drug
vocabulary, report the number of queried agents that had no exact match, and state in the caption
that agents absent from the 2023 graph are excluded rather than ranked low. This is a $0 re-analysis
of a committed artifact. If exact matching is not feasible for some agents, report the matched
compound name in the table rather than the query.

**4. Section 5, Table 4. The stress test does not test the hypothesis it is said to refute.**

The argument is: if EMC's sparsity in the knowledge graph caused the low ranks, then commoner
relatives should rank the same agents higher; they did not; therefore sparsity is not the cause.
That inference requires the comparators to be denser in the graph. What is offered instead is that
they are commoner *in the population*. Population incidence and knowledge-graph node degree are
different quantities, and neither the manuscript nor `txgnn-relatives-comparison.json` reports a
single edge count, node degree or number of known indications for any of the three disease nodes.
The script's own comment calls them "data-rich relatives" without measuring it.

The manuscript then states the caveat that voids its own conclusion, in the same sentence: the
released checkpoint is "the held-out complex-disease split, which, being the held-out
complex-disease split, also prevents any of the three diseases from serving as a clean data-rich
control". If none of the three is a clean control, the comparison cannot discriminate the two
explanations, and "The divergence is therefore not attributable to the sparsity of EMC specifically"
is not supported by it. The differences involved (21.0 versus 17.7 versus 17.4) are small, computed
over 31 matched agents, and reported with no dispersion.

*What would resolve it.* Either report the graph-side quantity that makes the comparators
comparators — node degree and indication count for the three disease nodes, both readable from the
committed graph at $0 — or weaken the conclusion to what the data support: the low ranking of
clinically active agents is reproduced for two commoner sarcoma nodes, so it is not a property
unique to the EMC node, and the causal question is not settled by this test. Report the medians with
a range or interquartile spread. Also state in Section 2.3 that EMC is a *grouped* node in the graph
and that the graph vintage is approximately 2023, so two of the queried agents are absent from it
entirely; both facts are in `txgnn-emc-findings.md` and neither reaches the manuscript.

**5. Section 4.1 and Section 2.4. "On the 16-tumour platform (GSE4303) every module was null" is
contradicted by the artifact, and the module that moved is the one that matters most for this lead.**

`research/modalities/emc-proteostasis-read.json` records, for GSE4303: proteasome 20S core t = 0.574,
19S regulatory t = −0.965, secretory/matrix-load proxy t = −0.807, unfolded protein response
t = −0.894, degradative alternatives t = 1.878, and **bounce-back and integrated stress t = 3.560**.
Against the pre-specified |t| ≥ 2 threshold, one of the six modules moved, and it moved further than
any module on either platform. The eight most extreme genes on that array are a coherent integrated
stress signature.

I looked at why the artifact's own verdict string nonetheless reads "NULL", and the answer is
defensible: `emc_proteostasis_read._verdict` is pre-specified to read only the LOAD and MACHINERY
modules, with bounce-back and degradative alternatives declared CONTEXT and excluded from the rule.
The verdict is correct for the contrast it grades. The manuscript's sentence is not: "every module
was null" is a claim about all six, and it is false of the data. Section 2.4 compounds it by telling
the reader that six modules were scored without saying that only four enter the decision.

The direction of the error is toward understating a positive, which is the safer direction, but it
is not harmless here. `emc_proteostasis_read.py`'s own header identifies NFE2L1 bounce-back as "the
mechanism that actually limits proteasome inhibitors". A paper whose distinguishing virtue is the
honest reporting of its own negatives has, in the one place it matters, reported a signal on its
lead's resistance axis as an absence.

*What would resolve it.* In Section 2.4, state that the pre-specified rule grades the load-versus-
machinery contrast and that two further modules were scored as context. In Section 4.1, replace
"every module was null" with the module table or with an accurate sentence: the load and machinery
modules did not move on either platform, and the bounce-back and integrated-stress module moved on
GSE4303 (t = +3.56), which the pre-specified rule does not read and which is reported here because
it bears on the same lead. Do not upgrade it into support; report it.

**6. Section 1.2, Section 5, Table 4. EMC is not a chondrosarcoma, so "the parent histology" and
"two commoner relatives" are both wrong, and two arguments inherit the error.**

The WHO classification places extraskeletal myxoid chondrosarcoma among tumours of uncertain
differentiation; the name is a historical morphological misnomer, the tumour has no cartilaginous
matrix, and it is genetically unrelated to conventional chondrosarcoma. This is not a matter of
taste for a sarcoma readership — it is the first thing a sarcoma pathologist or medical oncologist
will react to, and this repository already holds the sentence: the Bangerter abstract cached in
`research/modalities/emc-line-data-probe.json` opens "a malignant mesenchymal neoplasm of uncertain
differentiation as classified by the WHO Classification of Tumours 2020".

Two arguments rest on the error. Section 1.2 uses a 2007 chondrosarcoma review to bound the novelty
of the HDAC and VEGF entries "with respect to the parent histology" — but chondrosarcoma is not
EMC's parent histology, so prior art in chondrosarcoma bounds nothing about EMC and the sentence
either needs a different justification or should go. And Table 4's stress test selects
"chondrosarcoma (disease)" as a close relative of EMC on what appears to be a name match; a
genuinely close relative would be another FET-fusion sarcoma.

*What would resolve it.* State EMC's WHO placement once in Section 1.1. Replace "parent histology"
throughout with an accurate description of what reference 9 is (a review of a differently classified
tumour group that shares the historical name), or delete the novelty-bounding sentence. In Section 5
and Table 4, describe chondrosarcoma and soft-tissue sarcoma as commoner comparator disease nodes
rather than as EMC's relatives, and note that the choice was made on graph-node availability.

**7. Section 1.2 and reference 9. Five of the six targets attributed to reference 9 cannot be traced
to any committed source, and one of them is load-bearing.**

Section 1.2 states that the 2007 review "listed histone deacetylase, PDGFR, MMP-1, oestrogen
signalling, VEGF-A and methylthioadenosine phosphorylase among targets it described as validated by
translational research". The only committed record of that paper,
`research/literature/emc-prior-art-2026-08-09.json`, records one target: it "names
METHYLTHIOADENOSINE PHOSPHORYLASE among targets 'validated' by translational research in
chondrosarcoma". I searched the repository for the abstract text; it is not held anywhere. The
manuscript's own editorial comment concedes the list comes "from the abstract it summarises, not
from a full text read here", and that abstract is not in evidence.

The histone-deacetylase item is not decorative: it is used again in Table 2 ("Histone deacetylase is
named in the parent histology [9]") and in Table 3 to qualify the novelty of the HDAC lead. So a
novelty qualification on one of the paper's five leads rests on an untraceable attribution.

*What would resolve it.* Retrieve the abstract through the existing literature-fetch workflow and
quote what it actually says, or reduce the sentence to the single target the committed record
supports and drop the HDAC novelty qualification with it. Do not reconstruct the list from memory.

**8. Section 1.1, Abstract, Section 3.1. The anti-angiogenic class claim — adjudication of the
authors' own flagged open item.**

The authors flag this themselves and did not fix it: the ORR of 18% and median PFS of 19 months for
pazopanib, and the "most consistently active class" statement, are cited to the 2025 review rather
than to the primary reports. My ruling, as a reviewer, is that **this must be fixed before
acceptance, and it is not a matter of citation style.**

Citing a review for background orientation is entirely normal in a Review article. What is not
normal is citing a review for the specific numerical results of a specific named trial that the
manuscript's own abstract advances as its clinical premise. Reference 1 becomes, in this manuscript,
the sole support for: which class is most active in EMC, the response rate, the progression-free
survival, and by implication the trial's design and denominator. That is a primary-data claim, and
in this journal it will be read as one. It also propagates a second-hand reading: the repository's
own pooling record notes that the 19-month median PFS is itself "read from the Remiszewski 2025
review's account of the same trial", so the manuscript is at two removes from the measurement.

The authors' stated reason for not fixing it — the manuscript's editorial comment says two candidate
primaries were surfaced by CI search "and are not cited here because no committed artifact carries
their titles or author lists" — is a good rule, correctly applied to the wrong papers. **The
canonical primaries for this exact claim are already in this repository, with full bibliographic
records, verified retrieval notes and dates.** `research/manuscripts/emc-fusion-partner-pooling.json`
carries, under `citations`:

- the pazopanib phase 2 (Stacchiotti and colleagues, *Lancet Oncology* 2019, volume 20, pages
  1252–1262, NCT02066285), with design, dates, population, an erratum record, an `accessed` date of
  2026-08-07 and a verification note quoting the primary verbatim: 26 entered, 23 in the modified
  intention-to-treat set, 22 evaluable, "four (18% [95% CI 1–36]) had a RECIST objective response";
- the sunitinib series (Stacchiotti and colleagues, *European Journal of Cancer* 2014, volume 50,
  pages 1657–1664), 10 patients, 6 partial responses;
- the two-patient sunitinib report (Stacchiotti and colleagues, *Clinical Sarcoma Research* 2012),
  open access, full text held;
- the EMC state-of-the-art review (Stacchiotti and colleagues, *Cancers* 2020), open access.

So the fix costs nothing and requires no new retrieval. Cite the pazopanib trial and the sunitinib
series directly for the class claim, keep reference 1 for the synthesis it is, and — this is the part
that matters more than the citation — **report the numbers as the primary reports them**: four of 22
evaluable patients, 18%, 95% CI 1 to 36. An 18% point estimate quoted bare, from a single-arm phase 2
of 22 evaluable patients, with an interval that includes 1%, is the strongest claim in the abstract
and is currently presented as though it were a settled property of the class. If the 19-month median
PFS cannot be sourced to the primary, either cite it to the review explicitly as a secondary reading
or drop it. Given that this project's own `emc-systemic-therapy-pooling.json` documents five
widely-quoted EMC time-to-event figures that describe a different population or quantity than they
are quoted for, the manuscript should be the most careful paper in this literature on exactly this
point, not the least.

**9. Section 2.1, Section 5 (sixth limitation). The "not yet reported in EMC" evidence is materially
weaker than the Methods describe, and the counts quoted belong to a different question.**

Section 2.1 states: "A dedicated prior-art screen of Europe PMC, run on 9 August 2026, retrieved 322
records and 238 full texts and was screened by hand; it returned no indexed EMC-specific
drug-repurposing report." Checking `research/literature/emc-prior-art-2026-08-09.json`:

- The screen was not dedicated to this question. Its own header describes it as a "prior-art screen
  for the four publication endpoints scoring 12.5+", and it carries five query buckets.
- The 322 records and 238 full texts are the totals across all five buckets. The `repurposing` bucket
  returned **zero** records. There were no repurposing records to screen by hand.
- No query strings are recorded anywhere in the artifact, so the search is not reproducible.
- The artifact states that no positive control was used: `_no_positive_control_and_why` records that
  `expect_pmids` "was left EMPTY deliberately". A search that returns zero with no positive control
  cannot be distinguished from a search that did not work.

Separately, the enumeration arm's operational definition of "not reported in EMC" is narrower than
the prose implies. `enumerate-drugs.mjs` builds its exclusion list from the project's own clinical
registry by taking the first alphabetic token of each agent name, which yields roughly ten name
roots; the committed gap analysis classifies exactly two drugs as known-active in EMC. So for that
arm, "untried" means "absent from a ten-entry internal list", not "absent from the literature".

*What would resolve it.* Report the search as a Review should: database, exact query strings, date
run, records returned per query, and screening procedure, in a short Methods paragraph or a
supplementary table. State that the repurposing query returned zero records and that no positive
control was run, so the query's sensitivity is unknown. State the enumeration's exclusion list
explicitly, with its size and source. Then keep the sixth limitation, which is well written, and
strengthen it to say that the novelty claim for each of the fourteen candidates rests on a search
whose recall has not been demonstrated.

**10. Table 2, Section 3.4, Section 5. The immune axis is graded "no EMC data" when this project's
own registry records a prospective EMC cohort of a checkpoint inhibitor.**

Table 2 grades the mRNA-vaccine-plus-checkpoint candidate as "Mechanistic: cold-microenvironment
hypothesis, no EMC data", and Section 3.4 presents it as analogy-only. But
`research/data/emc-clinical-registry.json` records, under `treatments.systemicEvidence`, a
prospective phase 2 EMC cohort of sunitinib plus nivolumab: 23 evaluable, 16 progression-free at 6
months, two partial responses, 12-month overall survival 90%, reported as a conference abstract with
no full paper indexed. The same file's `emergingTreatments` block lists "Immune checkpoint
inhibitors (e.g. nivolumab), alone or with a TKI".

"No EMC data" for a checkpoint-inhibitor-containing candidate is therefore not accurate against the
project's own data, and the omission cuts against the paper. That cohort is the single most relevant
piece of EMC evidence for this candidate, it is a modest signal at best, and saying so would make the
grading more credible, not less.

*What would resolve it.* Cite the cohort, restate the candidate as the vaccine component specifically
(which genuinely has no EMC data) rather than the axis, and note in Section 5 that a PD-1 inhibitor
with a VEGFR TKI has been studied prospectively in EMC with a conference-abstract-level result. If
the abstract cannot be cited to a retrievable record, say that.

**11. Section 3.2 (Table 3), Section 4 (Tranche 1), Section 4.2. Four passages a clinician could read
as a treatment suggestion, in a manuscript whose scope statement disclaims making one.**

The scope box states that the review "makes no treatment recommendation, including a negative one".
I do not think that survives contact with these sentences:

- Table 3, PPARγ row, "A realistic test": *"investigator-initiated window study or n-of-1; **no
  biomarker required**"*. This is the single most concerning phrase in the manuscript. It proposes
  giving a named, globally available oral drug to unselected EMC patients, on an axis whose direction
  of effect Section 3.3 says is unresolved and whose only functional support comes from a cell line
  of contested identity. "No biomarker required" removes the only selection gate, and a clinician
  scanning tables will read it as "any EMC patient".
- Table 3, same row: *"oral and globally available"* as a qualifying property. Availability is a
  feasibility statement in a research context and an access hint in a clinical one.
- Section 4, Tranche 1: *"The realistic route is molecular pre-screening by sequencing for KIT
  mutations, followed by an expanded-access or n-of-1 study in the small mutation-defined minority
  who qualify."* Expanded access is a route to treating a patient. Recommending it, for an approved
  drug, in a named molecular subgroup, on the strength of one case report, is a treatment
  recommendation in substance whatever the scope box says.
- Table 2 and Section 4: naming *"carfilzomib, with doxorubicin or venetoclax"* as a unit reads as a
  regimen rather than as a hypothesis, particularly in a table a reader will screenshot.

*What would resolve it.* Rewrite the "A realistic test" column so that every entry names a
preclinical or trial-design step rather than an administration route, and delete "no biomarker
required" outright — on an axis of unresolved sign, the absence of a biomarker is a reason for
caution, not a convenience. Replace "expanded-access or n-of-1 study" with a statement about what
evidence would be needed before any clinical step could be contemplated, and keep the existing
sarcoma-specialist-review requirement adjacent to it rather than two sections away. Remove
availability and tolerability adjectives from the lead descriptions in Table 3; they belong in the
dataset, where they already are. Reword combination entries as "the combinations reported in the
source screen" rather than as drug pairings.

**12. Overall shape; Abstract, Section 3, Section 6. The negative findings are the contribution, and
the paper is organised as though they were caveats.**

The manuscript's own honest summary is that the only candidate with EMC clinical evidence is the only
one already tried, that both in-silico rationales advanced for the most striking lead failed, and
that the graph foundation model diverged from everything and promoted nothing. Those three results
are what a reader will remember and are what makes this worth publishing. They currently appear as
the third and fifth items of the Limitations section, as a subsection of the prioritisation section,
and as one line of the abstract, while the front of the paper is a menu of fourteen agents.

Is this a useful review or a null result dressed as a menu? It is a useful review with its
contribution buried. The menu, taken alone, is fourteen mechanistically plausible agents of which
twelve have no EMC-specific functional data and none has clinical data — which is a modest
contribution, and one whose shelf life is short because the drug landscape moves. The structural
result, the failed rationales and the model's failure are durable, and two of them are genuine
negative results of a kind this literature almost never publishes. A reader deciding whether to
spend a year on EMC repurposing is better served by "here is what three approaches to this problem
returned, and two of them returned nothing" than by a ranked list.

*What would resolve it.* Restructure so the negatives lead. Concretely: move the evidence-versus-
novelty analysis and its empty cell to the front of Section 3 with the fourteen-candidate table as
its support rather than its subject; promote the proteasome section and the graph-model section from
Section 4.1 and Limitations into a numbered results section of their own, at the same level as the
menu; and rewrite the abstract so its second half is the three findings rather than one line about
them. The title should follow: "a graded candidate menu from three independent generation methods"
promises the thing that did not happen, and something closer to what the paper actually establishes —
that in an ultra-rare sarcoma the untried candidates are exactly the ones without evidence, and that
two independent computational approaches to fixing that returned nothing — would be a truer and more
citable title.

**13. Section 6. The mandatory Critical View section exists but is inward-facing and thin.**

It is present, correctly placed at the end, and runs about 285 words. Three of its four paragraphs
restate the paper's own contributions ("The output is a graded menu…", "The structural result is the
part most likely to survive…", "A graph foundation model was run…"). Only the last paragraph is
critical, and it is critical of this work rather than of the field. For this journal the Critical
View is expected to be an appraisal of the state of the evidence, not a summary.

*What belongs in it.* (a) The evidence ceiling of the field: the only prospective trial in this
disease is a single-arm phase 2 with 22 evaluable patients and a response-rate interval spanning 1 to
36 per cent, and everything else is retrospective series, single cases, or ex-vivo work in one or two
patient-derived models. (b) That reproducibility across EMC models is untested — two independent
screens exist and have not been run against each other, so the field cannot currently say whether a
screen hit in one model replicates in another. (c) That the denominator of tried-and-failed agents in
EMC is unknown, because negative off-label experience in ultra-rare disease is almost never
published, which bounds every "not yet reported" claim in this paper and in any successor. (d) That
graph-model repurposing is being adopted in rare disease faster than it is being validated in it, and
that this paper's result — a released checkpoint ranking the two most clinically active agents in the
disease in its bottom quintile — is a data point that should temper that adoption. (e) What would
change the authors' minds about any lead on the menu. (f) One paragraph on the infrastructure
argument from Section 4.2, which is currently the weakest-supported part of the paper and is the part
a rare-disease readership can actually act on.

Also, an internal inconsistency to fix while rewriting: Section 6 says the high-return set is "five
rather than of fourteen", but Table 3's caption restricts it to candidates "backed by EMC-specific
functional data rather than by mechanism alone", and two of its five rows fail that test by their own
text — the CDK4/6 row says its evidence "is expression and genomic rather than functional", and the
BET/CDK7-9 row says "mechanism and analogy only, with no EMC functional data". The set that satisfies
the caption is three.

**14. Section 7 and the deposited dataset. Three values the manuscript's Appendix A registers as
corrected are still live in the file readers are pointed to.**

Section 7 directs readers to `research/hypotheses/candidates.json` as the accompanying dataset, and
Section 2.2 says the per-criterion scores, rationale, risks and citations for every candidate live
there. That file still carries:

- `landscapeNote`: "the KIT mutation is a rare (~5%) exception" — the figure Appendix A registers as
  removed because "No source carried the ~5% figure";
- the imatinib entry's `keyRisks`: "only ~5% carry an actionable KIT mutation" — the same figure
  again;
- the imatinib entry's `emcVulnerability.claim`: "CD117/KIT is expressed in roughly half of cases",
  attributed to `kitMutation2018` (reference 6) — the cherry-picked single figure that Appendix A
  registers as replaced by a verified range.

All three also persist in the generator, `build-candidates.mjs`, so regenerating the dataset
reproduces them. A correction that is registered in the manuscript's appendix but not applied to the
deposited data is not a correction; the reader who downloads the dataset gets the withdrawn values.

*What would resolve it.* Apply the three corrections to `build-candidates.mjs`, regenerate
`candidates.json`, and confirm the appendix rows match the file. While there, add the axis assignment
as a field: the manuscript claims seven vulnerability axes and the dataset carries no axis field at
all, so the axis mapping exists only in prose and cannot be checked (see minor point 3).

**15. Section 1.1, Section 3.1, cover letter. The 4% figure counts a mutation the record does not
characterise as imatinib-sensitive.**

Section 1.1 states that "An imatinib-sensitive activating KIT mutation is rare, reported in 1 of 20
EMCs in one series [6] and in 2 of 48, approximately 4%, in another [2]". The committed record
describes these differently: the first is an exon-11 in-frame deletion, which is the imatinib-
sensitive class; the second is recorded in `candidates.json` as "a KIT p.E554K mutation in 2/48 EMC",
with no statement anywhere in the artifacts that it is imatinib-sensitive or exon-11. The fact-check
log verifies the fractions, not the sensitivity classification.

The 4% figure is then load-bearing: Section 3.1 uses it to size the only clinically evidenced
candidate's addressable population, and the cover letter repeats it as "the KIT-mutant minority of
roughly four per cent".

*What would resolve it.* Separate the two claims. State the frequency of any KIT mutation with the
fractions as reported, and state separately, and only where the source supports it, which of those
mutations fall in the imatinib-sensitive class. If the second series' variant is not characterised as
imatinib-sensitive in its source, the sentence cannot describe it as one, and the addressable
minority is smaller and less certain than 4%.

**16. Section 2.3. The Methods misdescribe the enumeration filter, and one triaged-out example is
mis-identified.**

Section 2.3 says "approved drugs with an inhibitor interaction were retained". `enumerate-drugs.mjs`
applies exactly one filter — `if (!it.drug?.approved) continue;` — and records `interactionTypes`
without ever filtering on them. That is why `target-drug-matrix.json`'s 94 newly surfaced drugs
include aspirin, dexamethasone, letrozole, cytarabine, leucovorin, estradiol valerate, apigenin,
gentian violet and a proton-pump inhibitor. The stated filter would have removed most of these; the
implemented one did not.

Relatedly, the manuscript describes the triaged-out implausible hits as "a protein-protein-interaction
modulator and a thrombopoietin agonist". The thrombopoietin agonist is romiplostim, correctly. The
other is rabeprazole, which `candidates.json` records as "a PPI — biologically implausible DGIdb
artifact", where PPI means proton pump inhibitor. The abbreviation has been expanded the wrong way in
the manuscript, turning a common gastric acid suppressant into a drug class it does not belong to.

*What would resolve it.* Describe the filter as implemented (approved status only), report that 94
drugs were surfaced and how many were triaged and on what basis, and correct rabeprazole to a
proton-pump inhibitor. If an interaction-type filter is wanted, apply it in the code and regenerate;
that is a $0 change and would materially improve the enumeration's precision.

**17. Section 2.3, Section 6. The "convergence" of curation and enumeration runs partly through
biologically implausible graph edges.**

The enumeration's `gapAnalysis.inCatalog` — the set the manuscript treats as independent
corroboration of the hand-built catalogue — includes carfilzomib matched via a KDR edge, venetoclax
via a KIT edge, and palbociclib via RET and MET edges. None of those is the drug's actual target, and
none is why the curator selected it. So three of the ten "already in catalogue" agreements are
coincidences of database noise rather than convergent inference, which weakens the claim in Section
2.3 that the enumeration "independently reproduced" the curated cluster and "mitigates single-rater
coverage bias".

*What would resolve it.* Restrict the convergence claim to the angiogenesis and KIT clusters, where
the target edges are real, and state explicitly which catalogue entries the enumeration reproduced
through their actual mechanism. A one-sentence caveat that database target annotations include
spurious edges, with these three as the examples, would be more convincing than the current framing
and costs the paper nothing.

---

## MINOR POINTS

1. **Abstract.** 240 words by a plain count against a 250-word limit. There is no headroom for the
   changes above; budget for it. The last sentence, "No efficacy is claimed for any agent named
   here", is unusual in an abstract and duplicates the scope box; the space is better spent on the
   findings.

2. **Highlights.** All five are within the 85-character limit and are well written. Highlight 1 is
   wrong (point 2) and Highlight 3 depends on the disputed T3 grade (point 1). My suggested five:
   the structural anti-correlation and the empty cell; that the only clinically evidenced candidate
   is the only one already tried; that two pre-specified in-silico rationales for the proteasome
   lead both failed; that a released graph foundation model ranked the two most clinically active
   agents in the disease in its bottom quintile; and that fourteen candidates were catalogued across
   seven axes with explicit evidence tiers. That is four negatives and one positive, which matches
   the paper.

3. **Section 2.1 and Table 2.** The seven vulnerability axes are named in prose only.
   `candidates.json` carries no axis field, and Table 2's parenthetical axis labels include at least
   two — "(KIT)" and "(kinome screen hit)" — that are not among the seven. Add the axis as a dataset
   field and make the table labels match the seven.

4. **Table 2 caption.** Captioned "The 14 candidates" but contains 13 rows; the anthracycline-
   combination candidate is a separate entry in Table 1 and in the dataset but is folded into the
   carfilzomib row here. Reconcile, or caption it accurately.

5. **Section 2.2.** `evidenceStrength` (a 1 to 5 field in the dataset) is used to order Table 2 but is
   never defined in the manuscript. Either define it or say that ordering is by evidence type.

6. **Section 2.3.** No date is given for the DGIdb query. The artifact records 2026-06-20, roughly
   seven weeks before the manuscript date, and the paper elsewhere insists that agent status is
   time-sensitive. Give the query date, the database version and the number of genes queried.

7. **Section 2.4.** The comparator arms are not described. On GSE24369 the comparators are
   low-grade fibromyxoid sarcoma, desmoid fibromatosis and fibrosarcoma — and the artifact notes the
   LGFMS arm is itself FET-rearranged, so a shared fusion-driven programme would be subtracted out.
   On GSE4303 the comparators are three dermatofibrosarcoma protuberans and three gastrointestinal
   stromal tumours. Both facts change how a null should be read and belong in the Methods.

8. **Section 2.4 and Section 4.1.** GSE4303 is a two-colour cDNA array reporting log-ratios against a
   reference pool, with about 63% probe-to-symbol mapping and 1,662 of 1,973 requested genes
   measurable, contrasting 10 against 6. A null on that instrument is close to uninformative and
   should be described as a weak instrument rather than as a second independent confirmation.

9. **Section 2.4 and Section 4.1.** The manuscript never states that no EMC cell line exists in the
   DepMap dataset. The artifact says so explicitly and calls itself "a PRIOR from related sarcomas,
   NOT EMC data". A reader will otherwise assume EMC lines are among the 91. Add one sentence.

10. **Section 4.1.** The DepMap numbers all check out against the artifact: PSMB1, PSMC1, PSMD1 and
    VCP at 100%, PSMB5 at 97.8%, selectivity −0.103 to +0.169, SQSTM1 at 0% and NFE2L1 at 7.7%. No
    change needed; recorded here so the authors know it was checked.

11. **Section 3.3.** This is the best-argued section of the paper and should be cited as the model for
    the rest. One fix: it correctly says the direction is unresolved and that the in-vitro work used
    a line whose EMC identity is unsupported, but Table 1 still files zaltoprofen under "In vivo,
    animal EMC model" and Table 3 still leads with it. Tables are what get quoted. Qualify the row
    labels themselves, e.g. "in vivo, animal model; line identity of the in-vitro half unsupported,
    xenograft line unread".

12. **Section 3.3 and Section 5.** Whether the mouse experiment used the same cell line is recorded as
    unread because the paper is paywalled. This is a $0 retrieval through the workflow the project
    already runs for full texts. Either retrieve it and state the answer, or state plainly in
    Section 5 that the strength of the only in-vivo signal in the menu cannot currently be
    established. Do not leave it implicit.

13. **Section 3.1, Table 2, Section 4.** The VEGFR list is eight agents in the manuscript and nine in
    the dataset; fruquintinib appears in `candidates.json` and in the enumeration output but not in
    the paper, with no stated reason. Either restore it with its regional approval caveat or record
    the exclusion.

14. **Section 4, Tranche 2.** "Regional approval status varies by agent and would need checking
    before any such design" is the right instinct but too vague to act on. Name which agents in the
    list are approved in which of the major regions, or state that the list mixes globally and
    regionally approved agents and identify the latter.

15. **Section 4.2.** The shared-infrastructure paragraph is three sentences and one citation for what
    is, in practice, the paper's only actionable recommendation. Expand it or fold it into the
    Critical View.

16. **Section 5, third limitation.** "ranking the most clinically active agents in EMC, pazopanib and
    sunitinib, in the bottom quartile" checks out (19.3rd and 19.8th percentiles). The parenthetical
    about the held-out split is doing too much work in one sentence and should be its own sentence,
    for the reason in major point 4.

17. **Section 7.** Good practice, and better than most submissions. Add the commit hash or a DOI-
    minted archive of the repository state the manuscript was written against; file paths alone do
    not fix a version, and several of the files cited here have changed since the values in the
    manuscript were taken from them.

18. **Section 9, reference completion note.** The note is admirably candid, but it also states that
    eight of twenty references still lack volume and page detail and one is a database. That is an
    editor-facing problem: the reference list is not submission-ready as it stands, and the note
    itself must not survive into the submitted manuscript.

19. **References, adequacy.** Twenty references is thin for a Review in this journal, and the
    thinness is concentrated where it matters. Under-referenced sections, in order of severity:
    Section 1.1 (the entire clinical background of the disease rests on references 1, 2, 4, 5 and
    the three KIT papers, with no primary trial citation — see major point 8); Section 4.2 (one
    citation, to a registry, for the whole infrastructure argument); Section 3.4 (the immune
    candidate is supported by one melanoma trial and one nanoparticle review with nothing from the
    sarcoma immunotherapy literature); Section 2.3 (the enumeration method cites the database but no
    methodological literature on target-to-drug inference or its known false-positive behaviour);
    and Section 5's third limitation (the graph-model divergence is a claim about a class of methods
    and cites only the model's own paper — no independent evaluation of knowledge-graph repurposing
    in rare disease, and no comparator method). I would expect 45 to 70 references for a Review of
    this scope in this journal.

20. **Appendix A.** This does not belong in a journal submission. It is a change log of a document
    that has never been published, so none of its rows corrects anything a reader could have seen; it
    contains internal repository history ("The document's own status as an 'earlier treatment-track
    draft…'"), a retracted identifier for a reference that is now correct, and a warning glyph and
    mid-sentence bolding that are out of register for a journal. Keep it in the repository, where it
    is genuinely valuable, and remove it from the submission. If any of it must survive, the only
    rows that bear on a reader are the Bangerter single-model correction and the refuted sparsity
    explanation, and both are already stated in the main text.

21. **Register.** The style is clean and journal-appropriate almost throughout, which is not something
    I often say. The surviving tics, all outside the linted body: the warning glyph and the four
    mid-sentence bold spans in Appendix A; and, in the main text, a habit of narrating the paper's
    own structure — "Table 1 shows the structure at a glance", "which Table 3 isolates", "The
    presentation in section 3 does not use that composite, for the reason given there", "That short
    list is the practical output of the exercise", "That is why approved agents hitting PPARγ …
    dominate the upper rows of Table 2". Each of these tells the reader what the paper is doing
    instead of doing it. Cut them.

22. **Editorial comment block.** The HTML comment at the top of the file ships with the manuscript in
    a markdown submission and must be deleted before submission. It also concedes something an editor
    would want to know: the word, abstract and display-item limits the manuscript is built to are
    search-derived rather than read from the journal's author guidelines, because those pages returned
    HTTP 403. My editorial checks below take those limits at face value; confirm them independently.

23. **Figure 1.** Legible, greyscale-safe as claimed, and it makes the paper's point better than the
    prose does — the graph model sits outside the design as a disconnected dashed pair, which is
    exactly what it turned out to be. Three fixes: the caption calls it "The three-method design"
    while the figure shows two methods feeding the catalogue and one contributing nothing, so either
    the caption or the framing should change (see major point 2); the dashed convention is never
    explained, so add "dashed = ran but contributed no candidate" to the legend; and the label
    "diverged; reported as a limitation, no hit promoted" floats above the arrow it belongs to.

24. **Display items.** One figure and four tables, five items against a stated limit of six. Fine, and
    there is room for the one item I would add: a supplementary table of the search strategy for
    major point 9.

25. **Word count.** Roughly 4,200 words from the abstract through Section 6 excluding table rows, or
    about 5,400 including references, against a stated 8,000-word limit. There is ample room for the
    additional referencing in minor point 19 and for the Critical View expansion in major point 13.

26. **Cover letter.** Well judged, correctly emphasises the negatives, and the fit argument ("the fit
    with the journal is the register rather than the disease") is a good one. Two changes follow from
    the review: it repeats the 4% figure (major point 15) and it describes the work as using "three
    independent methods" (major point 2). Also, the sentence "the two in-silico rationales advanced
    here for the highest-profile lead … were both pre-specified, both run, and both returned negative"
    will need to survive the correction in major point 5, which it can, with one added clause.

27. **Sections 8 and 9, AI disclosure.** The two-part disclosure — research-process use in Section 2.5,
    manuscript-preparation use in Section 8 — is correctly separated and correctly worded, and the
    statement that every step is a committed script with a committed output is true and unusually
    verifiable. No change. I note it because it is the part of the manuscript most likely to draw an
    editorial query, and it will hold up.

28. **Single-authorship and clinical review.** The manuscript and cover letter both state that no
    sarcoma clinician has reviewed the candidates. That is honest and I would not require a
    co-author, but for this journal I would require the recommendation to be more specific: name what
    a clinician review would have to cover (the tier assignments, the addressable population for the
    KIT subset, and the four passages in major point 11) rather than recommending review in general.

---

## Revision list

Work top to bottom. Every item is doable with what is already committed; none requires new
experimental data.

1. `repurposing-hypotheses.md`, Section 2.2 and Table 1, Table 2, Section 4 Tranche 1, Section 5 and
   Abstract — regrade imatinib from T3 to T2, or state and defend an explicit rule under which a
   biomarker-matched single case counts as T3. Propagate to the Table 1 row label, the Tranche 1
   paragraph, the abstract sentence and the firewall statement. State that no candidate is graded T2
   as the scale is currently applied. (Major 1)
2. `repurposing-hypotheses.md`, title, Abstract, Highlight 1, Section 2.3, Section 6 — replace the
   "three independent generation methods" framing with the measured split: 12 candidates from
   curation, 2 from the enumeration, 0 from the model. State the nine enumerated genes and that five
   of the seven axes had no enumeration target. (Major 2)
3. `repurposing-hypotheses.md`, Table 4 and Section 5 — re-derive the model percentiles by exact name
   matching. Remove "doxorubicin" from all three "best-ranked" cells or replace it with the compound
   the artifact actually matched. Report how many queried agents had no exact match, and state that
   agents absent from the graph are excluded rather than ranked. Fix the same error in
   `research/hypotheses/txgnn-emc-findings.md`. (Major 3)
4. `repurposing-hypotheses.md`, Section 5 and Table 4 — either add the graph-side measure that makes
   the two comparators comparators (node degree and indication count, readable at $0), or weaken the
   conclusion to "the low ranking is reproduced at two commoner sarcoma nodes, so it is not unique to
   the EMC node; the cause is not settled by this test". Add the grouped-node and 2023-vintage facts
   to Section 2.3. Report dispersion alongside the three medians. (Major 4)
5. `repurposing-hypotheses.md`, Section 4.1 — delete "on the 16-tumour platform (GSE4303) every module
   was null" and replace it with the six module values, naming the bounce-back and integrated-stress
   module at t = +3.56 and stating that the pre-specified rule does not read it. In Section 2.4, state
   that four of the six scored modules enter the decision rule and two are context. (Major 5)
6. `repurposing-hypotheses.md`, Section 1.1, Section 1.2, Section 5, Table 4 — add EMC's WHO placement
   among tumours of uncertain differentiation; remove "parent histology" throughout; redescribe
   chondrosarcoma and soft-tissue sarcoma as comparator disease nodes rather than as relatives.
   (Major 6)
7. `repurposing-hypotheses.md`, Section 1.2 and reference 9 — reduce the target list attributed to
   reference 9 to methylthioadenosine phosphorylase, the only item any committed record supports, and
   remove the consequent HDAC novelty qualification from Table 2 and Table 3; or retrieve the abstract
   through the existing literature-fetch workflow and quote it. (Major 7)
8. `repurposing-hypotheses.md`, Section 1.1, Abstract, Section 3.1, reference list — cite the pazopanib
   phase 2 (Stacchiotti and colleagues, *Lancet Oncology* 2019, NCT02066285) and the sunitinib series
   (Stacchiotti and colleagues, *European Journal of Cancer* 2014) directly for the class claim, using
   the full records already held in `research/manuscripts/emc-fusion-partner-pooling.json`. Report the
   response rate as 4 of 22 evaluable, 18%, 95% CI 1 to 36. Either source the 19-month median PFS to
   the primary or label it as a reading of the review. (Major 8)
9. `repurposing-hypotheses.md`, Section 2.1 and Section 5 sixth limitation — add a Methods paragraph
   or supplementary table giving the exact queries, database, date and per-query record counts; state
   that the repurposing query returned zero records and that no positive control was used; state the
   enumeration's exclusion list, its size and its source. Correct the sentence that attributes 322
   records and 238 full texts to this question. (Major 9)
10. `repurposing-hypotheses.md`, Table 2, Section 3.4, Section 5 — cite the prospective sunitinib-plus-
    nivolumab EMC cohort recorded in `research/data/emc-clinical-registry.json`, restrict the "no EMC
    data" grade to the vaccine component, and note the checkpoint axis is not untried. (Major 10)
11. `repurposing-hypotheses.md`, Table 3 and Section 4 Tranche 1 — delete "no biomarker required";
    remove "oral and globally available"; replace "expanded-access or n-of-1 study" with a statement of
    what evidence would be needed first; rewrite the "A realistic test" column so no cell names a route
    to administering a drug; reword combination entries as reported source findings. (Major 11)
12. `repurposing-hypotheses.md`, Abstract, Section 3, new results section, title — restructure so the
    three negative findings lead: promote the evidence-versus-novelty analysis to the front of
    Section 3, give the failed proteasome rationales and the model divergence their own numbered
    results section, rewrite the second half of the abstract around them, and retitle. (Major 12)
13. `repurposing-hypotheses.md`, Section 6 — rewrite the Critical View outward: the field's evidence
    ceiling, untested cross-model reproducibility of screen hits, the unknown denominator of
    unpublished negative off-label experience, the pace of graph-model adoption in rare disease
    against its validation, what would change the authors' minds, and the infrastructure argument.
    Correct "a set of five rather than of fourteen" to three, or relax Table 3's caption. (Major 13,
    Minor 15)
14. `research/hypotheses/build-candidates.mjs` and `candidates.json` — remove the unsupported ~5% KIT
    figure from `landscapeNote` and from the imatinib `keyRisks`; replace "CD117/KIT is expressed in
    roughly half of cases" with the verified range and correct its attribution; regenerate the dataset
    and confirm it matches Appendix A. Add an `axis` field to every candidate. (Major 14, Minor 3)
15. `repurposing-hypotheses.md`, Section 1.1, Section 3.1 and the cover letter — separate "any KIT
    mutation" from "imatinib-sensitive-class KIT mutation"; do not describe the second series' variant
    as imatinib-sensitive unless a source says so; restate the addressable minority accordingly.
    (Major 15)
16. `repurposing-hypotheses.md`, Section 2.3 — describe the enumeration filter as implemented
    (approved status only); report the 94 surfaced drugs and how they were triaged; correct
    "protein-protein-interaction modulator" to "proton pump inhibitor". Optionally implement the
    interaction-type filter in `enumerate-drugs.mjs` and regenerate. (Major 16)
17. `repurposing-hypotheses.md`, Section 2.3 and Section 6 — restrict the convergence claim to the
    angiogenesis and KIT clusters and name carfilzomib via KDR, venetoclax via KIT and palbociclib via
    RET/MET as examples of spurious database edges. (Major 17)
18. `repurposing-hypotheses.md`, Section 2.4 — name the comparator arms on both platforms, note that
    the GSE24369 comparator arm includes a FET-rearranged sarcoma, and describe GSE4303's instrument
    limits (two-colour log-ratio, ~63% probe mapping, 10 versus 6). (Minor 7, Minor 8)
19. `repurposing-hypotheses.md`, Section 2.4 and Section 4.1 — state that no EMC cell line exists in
    the DepMap dataset and that the dependency read is a prior from other sarcomas. (Minor 9)
20. `repurposing-hypotheses.md`, Table 1 and Table 3 — qualify the zaltoprofen row labels in the tables
    themselves, not only in Section 3.3. Retrieve the Higuchi full text through the existing workflow
    to settle the xenograft line, or state in Section 5 that the strength of the only in-vivo signal
    cannot currently be established. (Minor 11, Minor 12)
21. `repurposing-hypotheses.md`, Table 2 and Section 4 Tranche 2 — reconcile the eight- versus
    nine-agent VEGFR list, restore or record the exclusion of fruquintinib, and name which agents are
    approved in which regions. (Minor 13, Minor 14)
22. `repurposing-hypotheses.md`, Table 2 caption and Section 2.2 — reconcile "the 14 candidates" with
    13 rows; define or drop `evidenceStrength`. (Minor 4, Minor 5)
23. `repurposing-hypotheses.md`, Section 2.3 — give the DGIdb query date and database version.
    (Minor 6)
24. `repurposing-hypotheses.md`, Section 9 — complete all references to journal style, add the eight
    incomplete records, and delete the reference completion note from the submitted version. Expand
    the reference list toward 45 to 70, prioritising Section 1.1, Section 2.3, Section 3.4, Section 4.2
    and the third limitation of Section 5. (Minor 18, Minor 19)
25. `repurposing-hypotheses.md`, Section 7 — add a commit hash or an archived, versioned snapshot of
    the repository state the manuscript was written against. (Minor 17)
26. `repurposing-hypotheses.md` — remove Appendix A and the leading HTML editorial comment from the
    submission version; keep both in the repository copy. Confirm the journal's actual word, abstract
    and display-item limits from its author guidelines rather than from a search-derived summary.
    (Minor 20, Minor 22)
27. `repurposing-hypotheses.md`, main text — cut the structure-narrating sentences listed in minor
    point 21. (Minor 21)
28. `repurposing-hypotheses.md`, Highlights — replace the five with the set proposed in minor point 2
    after the substantive changes land. Re-check the abstract against the 250-word limit last, since
    items 1, 8 and 12 all add to it. (Minor 1, Minor 2)
29. `figures/repurposing_design_figure.py` and Figure 1 caption — add the dashed-line convention to the
    legend, reposition the divergence label onto its arrow, and reconcile the caption with the revised
    framing of the third method. (Minor 23)
30. `repurposing-hypotheses-cover-letter.md` — propagate the corrections from items 2, 5 and 15, and
    make the clinical-review request specific to the tier assignments, the KIT subset denominator and
    the four passages in major point 11. (Minor 26, Minor 28)
