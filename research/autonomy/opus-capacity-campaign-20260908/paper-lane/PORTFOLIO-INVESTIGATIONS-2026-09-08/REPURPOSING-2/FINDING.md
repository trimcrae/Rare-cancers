---
id: DOC-PORTFOLIO-REPURPOSING2-FINDING
title: "REPURPOSING-2 — the tier question adjudicated, and the same class of miss found twice more"
level: L4
kind: finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# REPURPOSING-2 — follow-through on the two open items of PUB-REPURPOSING

Lane `REPURPOSING-2`, campaign OPUS-CAPACITY-CAMPAIGN-20260908, branch
`claude/confident-bardeen-ji76cd`. Paper: `research/manuscripts/repurposing/repurposing-hypotheses.md`.

⛔ **Nothing outside this directory was written.** No `git add`/`commit`/`push`, no
`scripts/preflight.sh`, no subagent, no repo copy, no shared-state edit, no tier change, no rule
change, no registry change, no reference added or removed. All proposals are **exact unapplied
diffs**. `git status` confirms the repurposing manuscript is unmodified.

## 1 · The two questions

1. **The tier question.** Reference [19] is a prospective phase II trial that enrolled EMC patients.
   Does it meet this paper's **own** T3 definition, and what does that do to the R2/V1 premise that
   nothing reaches T3?
2. **The same class of miss, elsewhere.** The falsifying cabozantinib fact was inside a paper the
   manuscript already cites, and a sibling lane had extracted it for a different question a day
   earlier without routing it. Sweep the manuscript's **own** cited references for other EMC
   patient-level facts its prose describes only at class or unselected-sarcoma level.

## 2 · Answers

### (1) The tier question — adjudicated as genuinely ambiguous, both readings stated

Full text with the definitions quoted: **`TIER-ADJUDICATION.md`**.

The definition is §2.2: *"**T3 denotes prospective or substantial clinical evidence in EMC**; T2, a
case-level signal in EMC or in a very close relative…"*. It is **ambiguous on precisely the point that
decides this case** — whether *prospective* attaches to the study **design** or requires an
**EMC-directed** study — and the committed manuscript supports each reading in a different place, so I
state both rather than pick one:

- **Reading A (literal, disjunctive): [19] meets T3.** A prospective trial, EMC patients enrolled, an
  EMC per-patient outcome reported. §2.2's own gloss — T3 marks *"what a prospective or substantial
  EMC clinical **result** would look like"* — points this way. Consequence: *"no candidate reaches
  T3"* and *"T3 is therefore defined but unoccupied"* become false in §2.2, §4, §5 **and in both the
  Figure 1 alt text and printed caption**.
- **Reading B (evidentiary-weight, EMC-directed): [19] fails T3 and lands squarely at T2.** An
  unplanned 3-patient stratum of a mixed-histology trial, with no EMC endpoint, no EMC analysis, no
  EMC safety denominator, is *"a case-level signal in EMC"* — the T2 wording, matched exactly. The
  strongest support is the manuscript's **own precedent in §4.1**, where it treats a sarcoma subgroup
  of a non-specific trial as settling *"the novelty claim"* and writes *"**It is not an efficacy
  result.**"* Its §1.1 exemplar of prospective EMC evidence is likewise an **EMC-only** cohort.

**Weighing, without deciding:** Reading B is the more consistent with the rest of the document and
needs the fewest changes; Reading A is the more natural reading of §2.2 taken alone, which is itself a
defect — if the coordinator adopts B, §2.2 should be tightened to say what §4.1 was already doing.

**What is untouched under both readings:** the imatinib T2 regrade stands (nothing found here bears on
it); the firewall rule is untouched and **is not triggered**, because admission needs T3 **and**
clinician review — T3 is necessary, never sufficient; the four-tier scale is untouched.

⛔ **The fence, restated because it governs the whole document:** a 3-patient subgroup of a trial that
**missed both primary endpoints** supports **no efficacy, safety or therapeutic-window claim at any
tier**. Tier placement here is evidence class, not whether the drug works. A T3 placement, if adopted,
would still assert nothing about cabozantinib working in EMC.

### (2) The sweep — the same shape found **twice more**, plus two smaller misses

Full table with citing sentences and verbatim cited facts: **`CITED-REFERENCE-SWEEP.md`**.

Seven cited references swept; five PMC full texts newly retrieved this session.

| | Hit | Changes a claim? |
|---|---|---|
| **H1** | **Pioglitazone has already been given to an EMC patient.** Reference **[5]** (Davis 2017, PMC5400622) — cited by the manuscript **only** for a genomics statement — reports: *"one patient with diabetes mellitus was treated with an antidiabetic agent, pioglitazone… had stable metastatic EMC for 13 months before unequivocal progression. The contribution of pioglitazone to disease control is unknown."* The manuscript grades the PPARγ row **"Novel (untried)"** in Table 1, novelty **"Yes"** in Table 2, and **"untried"** in Table 3. | **YES** — a second novelty falsification, of exactly the cabozantinib shape |
| **H2** | **The [6] *KIT* patient never received imatinib.** Reference **[6]** (Urbini 2018, PMC6073125) — cited **only** for the 1-of-20 prevalence — says: *"The EMC patient with a exon 11 mutation described here **never received imatinib**. Thus, the therapeutic role of this agent in this case is still to be defined. Interestingly the same patient had been **treated with sunitinib with a prolonged response**."* The manuscript calls it an *"imatinib-sensitive"* mutation. | **YES** — the source does not support the adjective; and an EMC sunitinib exposure sits unreflected |
| **H3** | **Sunitinib is attributed to [1], which does not appear to carry it.** Zero occurrences of "sunitinib" in [1]'s retrieved full text. ⚠ That extraction demonstrably drops tables, and [1] has an unretrievable clinical-trials table, so this is a **flag, not a refutation**. The claim is **true** and supported three times in the same reference list — by [4], [5] and [6]. | citation pointer only; **no diff proposed** |
| **H4** | **Reference [22] is now read at full text.** The manuscript says both proteasome trials are *"read here at abstract level only"* and that whether either enrolled an EMC patient *"remains unread"*. [22] (Boklan 2025, PMC12428389) is now read: 24 solid-tumour patients, 15 sarcomas (11 osteosarcoma, 1 synovial), **no EMC named anywhere**. ⚠ Its per-histology table is not in the retrievable text. | **YES** — a stated unknown is now partly resolved |
| **H5** | **[21] genuinely cannot be read.** Maki 2005 has **no PMCID**; MeSH stops at "Sarcoma". The manuscript's "unread" statement is **accurate and should be kept.** | no — confirms the paper |
| **H6** | Pazopanib denominator: the manuscript's *"4 of 22 evaluable"* is supported by **[4]**, not by the **[1]** it names ([1] says 23 mITT). | pointer only |

⛔ **No row above is an efficacy, safety or selectivity claim.** H1 in particular: n=1, incidental, no
response assessment, contribution unknown to the reporting authors, and the patient progressed. It
narrows **novelty**, nothing else.

**The routing lesson, made concrete.** Two of the four claim-changing hits came from references the
manuscript cites for a **non-treatment** fact (a genomics sentence, a prevalence fraction); the
cabozantinib miss came from one cited for a **class-level** fact. In every case the prose reads a
cited paper at one level of description and never asks what else that paper says about EMC patients.
No further literature search fixes this — **the papers were already in the reference list.**

## 3 · Artifact · validation · provenance · limitations · stop condition

**Artifacts.** `TIER-ADJUDICATION.md`; `CITED-REFERENCE-SWEEP.md`;
`PROPOSED-UNAPPLIED-cited-reference-sweep.diff` — an exact, unapplied unified diff against the
committed manuscript covering H1, H2 and H4 across §1.1, Table 1, Table 2, Table 3, §3.3 and §4.1. It
**adds no reference** ([5], [6], [21], [22] are all already cited), changes **no tier**, no rule, no
registry file, and touches nothing the tier adjudication is about. `checks/` holds one directory per
execution attempt with `command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`.

**Validation / baseline.** Baseline is the committed manuscript at
`3faeaa069cf8b6231273cf90bf62d30589152b14`. Every falsified sentence is quoted verbatim from it and
located by line. Every counter-fact is quoted verbatim from the cited paper's PMC full text. The diff
was built by an in-lane script carrying **seven exact-match assertions**; each anchor matched exactly
once, so no edit landed on a near-miss. `git status` shows the manuscript unmodified.

**Provenance.** PubMed / PubMed Central via the PubMed MCP server, 2026-09-09 00:05–00:13 UTC. New
full texts this session: PMC12504171 [1], PMC12398172 [4], PMC5400622 [5], PMC6073125 [6],
PMC9813045 [13], PMC12428389 [22]; metadata only for PMID 15739208 [21]. The [19] passages are
**reused verbatim** from PUB-REPURPOSING's `EVIDENCE-cabozantinib-emc.md` and were not re-fetched.
⛔ No direct HTTP fetch; the proxy-refused hosts were not touched.

**Limitations — the honest ones.**
- ⚠ **The PMC full-text extraction is lossy and this bounds two conclusions.** It drops **table
  contents** and italic-marked gene tokens. That is why H3 is a flag and not a refutation, and why H4
  is a reading of [22]'s narrative rather than of its diagnosis table. A reference could still hide an
  EMC patient inside a table this route will not return — which is exactly how the cabozantinib EMC
  count hid, in [19]'s Table 1.
- **The sweep is unfinished, not clear.** [2], [8], [9], [12] and [14] have no PMC full text reachable
  by this route or were not fetched; their EMC patient-level content is **unread, not absent**.
- The tier question is **not decided** here, deliberately. Both readings are live and the choice
  belongs to the paper's owner.
- H3 and H6 are left **without a proposed diff**: settling either requires reading a table this route
  cannot return, and guessing at a citation pointer would be worse than flagging it.
- I did not re-read [19] or [7]; [19] is taken as PUB-REPURPOSING quoted it, [7] as the manuscript
  characterises it.

**Stop condition.** Reached. Both assigned questions are answered — one adjudicated as ambiguous with
both readings and their consequences enumerated, one swept with four claim-changing hits and an exact
unapplied diff for three of them. Every remaining move (applying either diff, deciding the tier,
fixing the [1] citation pointer, finishing the unswept references) requires either shared-state
authority this lane does not have or a retrieval route that does not exist here.

## 4 · Next credible independent work

1. **Coordinator decision on the tier reading**, and on whether §2.2 is tightened to state the
   criterion §4.1 already applies. This is a *paper-owner* decision, not a literature question.
2. **Apply or reject the two unapplied diffs** — PUB-REPURPOSING's cabozantinib diff and this lane's
   sweep diff. They touch disjoint text and can be considered independently; the cabozantinib diff is
   **not blocked** on the tier decision, since its novelty corrections hold under both readings.
3. **Finish the sweep** for [2], [8], [9], [12], [14], and re-read [1]'s and [22]'s tables by a route
   that returns table contents.
4. **Build the cross-paper EMC-patient-exposure index.** Eight rows exist now
   (`CITED-REFERENCE-SWEEP.md` §2–3). One row per (agent, source, n, verbatim). This is the thing that
   would have caught cabozantinib, pioglitazone and the [6] characterisation on the same day.
5. **A bounded candidate-generation check**, separate from all of the above: the two best-performing
   targeted agents in the ex-vivo screen the carfilzomib candidate rests on — PU-H71 (HSP90) and
   HDM201 (MDM2/MDM4) — appear nowhere in the 14-candidate menu.
