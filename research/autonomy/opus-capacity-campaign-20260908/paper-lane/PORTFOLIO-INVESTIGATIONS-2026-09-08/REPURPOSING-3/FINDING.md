---
id: DOC-PORTFOLIO-REPURPOSING3-FINDING
title: "REPURPOSING-3 — the five unread cited references finished, and a harder limitation than the one recorded"
level: L4
kind: finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# REPURPOSING-3 — finishing the cited-reference sweep on [2], [8], [9], [12], [14]

Lane `REPURPOSING-3`, campaign OPUS-CAPACITY-CAMPAIGN-20260908, branch
`claude/confident-bardeen-ji76cd`. Paper: `research/manuscripts/repurposing/repurposing-hypotheses.md`,
committed at `b729216089989343bc8eb5d538bb815ab9e413a0`.

⛔ **Nothing outside this directory was written.** No `git add` / `commit` / `push`, no
`scripts/preflight.sh`, no subagent, no repo copy, no shared-state edit. **No tier, no rule, no
registry, no reference list was changed by this lane** — every proposal is an exact **unapplied**
diff. `git status` on `research/manuscripts/repurposing/` is clean. No direct HTTP fetch was made;
the proxy-refused hosts were not touched. PubMed MCP only.

## 1 · The question

The two prior lanes closed with five cited references **unread, not clear**: [2], [8], [9], [12],
[14]. Read each for **what it contains** — any EMC patient-level fact, enrolment, treatment given,
response, outcome — not for what it was cited for; get at table content where possible; and say for
each whether it changes a manuscript claim, and which sentence.

## 2 · The load-bearing answer first: the limitation is worse than recorded, in a specific way

The prior lanes recorded that the PMC full-text extraction **drops table contents**. For these five
that framing is too optimistic, and the correction matters because it changes what an absence claim
here can mean.

Two independent retrieval modes were run before any reading (checks `01` and `04`): the identifier
converter, and the PubMed-to-PMC link database. **They agree.**

* **[2], [8], [9] and [14] have no PubMed Central record at all.** Not a lossy extraction — **no
  retrievable body of any kind**. No Methods, no Results, no Discussion, no tables, no figures, no
  supplementary material.
* **[12] has a PMC record (`PMC10054153`) that returns an empty `full_text` string**, reproducibly,
  under both accepted id forms (checks `02`, `03`). Abstract only.

So all five were read at **abstract level**, plus keywords, MeSH and article types. Alternatives
were tried before concluding: the second retrieval mode above, the bare-numeric id form, and, for
[12], a PubMed search of the drug against the disease (check `06`) which found the one adjacent
human record described below. **There is no further route to these five that this session is
permitted to take.** Every absence stated in this lane is bounded to "not in the abstract" and is
written that way in the per-reference table.

**This is the honest form of the failure mode the task named.** An EMC patient-level fact sitting in
[8]'s 31-case clinicopathological table, or in [14]'s donor-patient record, **would not have been
seen here**. Recording that is the finding; claiming those references are clear would be the miss.

Per-reference detail, with sections-read and retrieval-completeness columns and verbatim quotations:
**`FIVE-REFERENCE-TABLE.md`**.

## 3 · Does it change a manuscript claim, and which sentence

| | Reference | Changes a claim? | The sentence |
|---|---|---|---|
| **E1** | **[2]** | **YES — an EMC treatment-outcome fact the manuscript never mentions.** Across **58 EMCs**, *"the administration of chemotherapy portended shorter univariate disease-specific survival"*, and it did **not** remain prognostically independent. The manuscript cites [2] only for a fusion-variant fact, a *KIT* fraction, a CD117 percentage and pan-Trk expression. | §1.1, the sentence ending *"…against a low objective response rate for anthracycline-based chemotherapy [1]. Those trial figures are taken from the 2025 comprehensive review… retrieved for this manuscript."* — a cited series independently bears on the same claim and is not used. Diff adds it **with the confounding by indication stated**, as a further absence of established systemic benefit and **explicitly not as evidence of harm**. |
| **E2** | **[2] + [8]** | **YES — two figures presented as one range are measured to different thresholds.** [2]'s 52.6% counts *"moderate-to-strong immunoreactivities"* among 48 assessed cases; [8]'s 84% counts *"IHC positivity (**focal or diffuse**)"* among 31. | §1.1: *"CD117/KIT protein… is detectable by immunohistochemistry in a substantial but variable proportion of cases, approximately 53% in one series and approximately 84% of 31 cases in another [2,8]."* Diff keeps both numbers and adds the threshold each was measured to. |
| **E3** | **[8]** | **YES — the same threshold omission, on the CDK4 figure that carries a candidate row.** [8] reports CDK4 100% under *"IHC positivity (focal or diffuse)"*. | §3.1 Table 2, the CDK4/6 row: *"CDK4 positive in 100% of a 31-case series…"*; and the §4 tranche table: *"CDK4 positive in 100% of a 31-case series with CDKN2A/CDKN2B loss [8,5]…"*. Both get the threshold. The candidate's standing is unchanged — it remains expression-and-genomic, not functional. |
| **E4/E5** | **[12]** | **YES, on the recorded reason only.** The manuscript twice says the zaltoprofen paper *"is not open access and its full text has not been retrieved here"*. A **PMC record does exist**, `PMC10054153`; it returns an abstract and an empty body. | §3.3: *"That paper is not open access and its full text has not been retrieved here, so whether the mouse experiment used the same line is unknown…"*, and the matching Appendix A row. ✅ **The substantive claim is confirmed correct and stays**: the abstract names **H-EMC-SS for the in-vitro work only** and calls the animal work *"a mouse model of extraskeletal myxoid chondrosarcoma"* **without naming a line**. The manuscript's refusal to state it in either direction is right. |
| **E6** | all five | **YES — provenance.** The editor-facing reference-completion note records which references are abstract-level (15, 21, 22) and omits these five. | The note's sentence beginning *"References 21 and 22 were retrieved from PubMed on 2026-08-28 and are likewise abstract-level only…"*. Diff records the five, with the reason for each and the date. |
| **Z1–Z4** | **[12]'s programme** | **YES — a parent-histology novelty bound, and it needs a new reference.** | See §4. Separate diff. |
| — | **[9]** | **NO.** The manuscript's §1.2 list — *"histone deacetylase, PDGFR, MMP-1, oestrogen signalling, VEGF-A and methylthioadenosine phosphorylase"* — matches [9]'s validated-target sentence **exactly, all six**. ⚠ One observation without a diff: [9] also says *"Bisphosphonates may also possess important antitumoral effects"*, a seventh class absent from both the manuscript's bounding list and its 14-candidate menu. The manuscript's clause is scoped to targets *"described as validated by translational research"*, and bisphosphonates sit in a separate, weaker sentence, so the sentence as written is **accurate** and no diff is proposed. |
| — | **[14]** | **NO.** The abstract confirms the manuscript verbatim: *"identified three candidates, brigatinib, panobinostat, and romidepsin"* from a 221-drug screen in a patient-derived EMC line. §3.1 Table 2 and the §4 tranche row already carry all three. The donor patient's treatment history is not in the abstract. |
| — | **[2], again** | **Corroboration, not a new diff.** REPURPOSING-2's H2 removed *"imatinib-sensitive"* as an adjective on the *KIT* mutation, on the strength of [6]. [2] **independently supports that**: it reports *"KIT p. E554K mutation was detected in 2/48 cases"* and concludes *"pathogenic KIT mutation rarely occurred"* — and **the word imatinib does not appear in its abstract at all.** Neither cited series characterises the mutation as imatinib-sensitive. |

⛔ **No row above is an efficacy, safety, selectivity or therapeutic-window claim.** E1 in particular
is a univariate association in an observational series, confounded by indication, with no regimen
named and no response assessment; the diff says so in the manuscript text itself.

## 4 · The one item that would add a reference — flagged, not taken

Reading [12] for what it **contains** rather than for what it was cited for raises a question [12]
cannot answer: has zaltoprofen ever been given to a human with this tumour? PubMed holds two records
for this drug in this disease. The other is by the **same group**, is **not cited**, and is an
article of type *Case Reports*:

> Higuchi T et al., *Cancer Med.* 2018;7(5):1944-1954. PMID 29573200, PMC5943440.
> *"we showed a case of a patient with **cervical chondrosarcoma (grade 2)**, who was treated with
> zaltoprofen and has been free from disease progression for more than 2 years."*

⛔ **That patient did not have EMC.** This **does not** falsify "untried in EMC" and is **not** a
third instance of the cabozantinib/pioglitazone shape. It bounds novelty at **parent-histology**
level only — precisely the qualification the manuscript already writes for itself elsewhere
(*"Untried in EMC; the class is not untried in sarcoma"*) and via [9] for histone deacetylase. Under
the paper's own convention the PPARγ row should carry the same qualification.

Because acting on it **adds reference [23]**, which this lane has no authority to do, it is a
**separate, clearly-named unapplied diff** for the paper's owner to accept or reject:
`PROPOSED-UNAPPLIED-zaltoprofen-parent-histology-ADDS-REFERENCE.diff`. No efficacy conclusion is
drawn from an uncontrolled n=1 report in either histology, and the diff text says so.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifacts.**
* `FIVE-REFERENCE-TABLE.md` — the per-reference table, with **sections actually read** and
  **retrieval completeness** columns, verbatim quotations, and an explicit "what is NOT reported in
  what was read" column per row.
* `PROPOSED-UNAPPLIED-five-unread-references.diff` — E1–E6. **Adds no reference**, changes no tier,
  no rule, no registry, no acceptance criterion.
* `PROPOSED-UNAPPLIED-zaltoprofen-parent-histology-ADDS-REFERENCE.diff` — Z1–Z4. **Adds reference
  [23]**; named so it cannot be applied unnoticed.
* `PROPOSED-UNAPPLIED-rebased-onto-REPURPOSING-2.diff` — both of the above, rebased. See the
  interaction result below.
* `checks/` — one directory per execution attempt, with `command.txt`, `stdout.txt`, `stderr.txt`,
  `exit_code.txt`, including the two retrieval attempts that returned an empty body.

**Validation.** Both diffs were built by in-lane scripts (`checks/07`, `checks/09`) carrying
**exactly-once anchor assertions** — 7 edits in the first, 4 in the second — with the script exiting
`3` if any anchor matched other than once, so no edit could land on a near-miss. All 11 matched
exactly once against the committed manuscript, and all 11 again against the REPURPOSING-2-applied
text. `patch --dry-run` on a scratch **copy** confirms each diff applies cleanly to its stated
baseline (`checks/08`, exit 0 for both; `checks/09`, exit 0 for the rebased diff). The manuscript
itself was never written to.

**⚠ Interaction result, reported because it is a real negative (`checks/08`).** **These diffs do not
apply after REPURPOSING-2's sweep diff.** With REPURPOSING-2 applied first: the five-reference diff
loses 1 of 6 hunks (E2, at line 163) and lands another with `fuzz 1`; the zaltoprofen diff loses
**3 of 4** hunks. The conflicts are **textual, not substantive** — REPURPOSING-2 rewrote the
surrounding §1.1 prose, split the Table 2 zaltoprofen row in two, and appended its own §3.3
paragraph. `PROPOSED-UNAPPLIED-rebased-onto-REPURPOSING-2.diff` is the resolved form, and its Z3
cell **merges** REPURPOSING-2's pioglitazone wording rather than overwriting it. **Ordering matters:
apply REPURPOSING-2's diff, then the rebased diff. Do not apply the two committed-baseline diffs
after it.**

**Provenance.** PubMed / PubMed Central via the PubMed MCP server, 2026-09-09 (checks `01`–`06`).
According to PubMed. New this session: metadata for PMIDs 36948401 [2], 36376703 [8], 17545802 [9],
40580361 [14] and 29573200 (adjacent, uncited); full-text attempts on `PMC10054153` [12] in two id
forms, both returning an empty body; and two independent PMC-availability checks across all five.
DOIs: [2] [10.1016/j.modpat.2023.100161](https://doi.org/10.1016/j.modpat.2023.100161);
[8] [10.1007/s00428-022-03453-x](https://doi.org/10.1007/s00428-022-03453-x);
[9] [10.1097/CCO.0b013e32812143d9](https://doi.org/10.1097/CCO.0b013e32812143d9);
[12] [10.1080/15384101.2023.2166195](https://doi.org/10.1080/15384101.2023.2166195);
[14] [10.1007/s13577-025-01250-7](https://doi.org/10.1007/s13577-025-01250-7);
adjacent [10.1002/cam4.1438](https://doi.org/10.1002/cam4.1438).
⛔ No direct HTTP fetch. No previously denied source was reopened.

**Limitations — the honest ones.**
* **The sweep is now *complete as to what is reachable*, and still not complete as to what exists.**
  All five were read at abstract level only, four of them because **no PMC record exists** and one
  because its record returns an empty body. An EMC patient-level fact inside [8]'s 31-case table,
  [2]'s per-case listing, or [14]'s donor-patient record **would not have been seen**. Every "no"
  above is "not in the abstract", never "not in the paper".
* The [9] bisphosphonate observation is left **without a diff** deliberately: the manuscript's clause
  is scoped in a way that makes the omission defensible, and forcing a change there would be worse
  than flagging it.
* The zaltoprofen chondrosarcoma case is **n=1, uncontrolled, inside a laboratory paper, and in the
  wrong histology.** It carries a novelty bound and nothing else.
* This lane did **not** re-read [1], [4], [5], [6], [7], [13], [19], [21] or [22]; it takes the two
  prior lanes' readings of those as they recorded them, and did not revisit the tier question.

**Stop condition. Reached.** All five assigned references are retrieved to the limit of the
permitted route, read for content rather than for citation purpose, and answered individually with
sections named. Every remaining move needs either shared-state authority this lane does not have
(applying a diff, adding reference [23]) or a retrieval route that does not exist here (a publisher
full text for four papers with no PMC record).

## 6 · Next credible independent work

1. **Coordinator: decide the apply order.** Three unapplied diffs now target this one manuscript and
   they are **not independently applicable** (§5). The rebased diff exists precisely so this does not
   have to be rediscovered by a patch failure.
2. **Accept or reject reference [23]** and the parent-histology bound on the PPARγ row.
3. **The four references with no PMC record are a standing hole, not a closed question.** If a
   publisher-side route is ever authorised, [8]'s 31-case clinicopathological table and [14]'s
   donor-patient record are the two highest-value unread objects in this reference list — both are
   EMC case series with follow-up, and both are exactly the shape that hid three EMC patients in
   [19].
4. **Build the cross-paper EMC-patient-exposure index** that REPURPOSING-2 proposed, and add a
   **retrieval-completeness column** to it. Two of this lane's rows ([8], [14]) would enter it as
   *unknown*, not as *none* — which is the distinction the index exists to preserve.
