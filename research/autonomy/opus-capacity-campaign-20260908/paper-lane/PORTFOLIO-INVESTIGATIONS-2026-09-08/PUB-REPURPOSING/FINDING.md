---
id: DOC-PORTFOLIO-PUBREPURPOSING-FINDING
title: "PUB-REPURPOSING investigation — falsifying the novelty claim, agent by agent"
level: L4
kind: finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-REPURPOSING — falsification study, 2026-09-08/09

Lane: `PUB-REPURPOSING`, paper `research/manuscripts/repurposing/repurposing-hypotheses.md`.
Nothing outside this directory was written. No git write, no preflight, no subagent, no repo copy.

## 1 · The question

**Does the manuscript's load-bearing novelty claim — that each of its 14 candidates is "not yet
reported in EMC" — survive a per-agent, EMC-scoped literature search, when the earlier screens
matched only the generic *EMC × repurposing* pairing?**

## 2 · Paper-level merit

The novelty claim is in the title, the abstract, Table 1's whole structure, Table 2's third column
and the tranche ordering of §5. If any candidate has already been given to EMC patients, the paper
mis-states the state of the field for a rare disease in which a clinician reading it would be looking
for exactly that. The paper itself asks for this check: §2.2 says the status of any individual agent
"is time-sensitive and should be re-checked with a dated, documented database search at the point of
submission", and §6 says the screens were framed around EMC pairings and declines to claim the other
axes are free of the class-level gap that was already found once. The evidence is public, attainable,
and each row is decidable.

## 3 · The exact evidence gap, and how it differs from completed or held work

What existed before this lane:

- `research/literature/emc-prior-art-2026-08-09.json` — Europe PMC, 322 records, screened by hand for
  the *EMC × repurposing* pairing. `"repurposing": 0`. Title/abstract only.
- `research/literature/carfilzomib-class-clinical-2026-08-28.json` — the **only** per-axis search of
  the drug class in the parent histology. Its own note: *"The query the EMC-scoped screens never ran:
  the drug CLASS in the PARENT HISTOLOGY."* It found a 21-year-old miss, and that miss is what §4.1
  now discloses. It was run for the proteasome axis and no other.
- `research/literature/emc-clinical-sweep-targets.json` — disease-scoped sweeps (EMC × treatment,
  × TKI, × chemo …), never agent-scoped for the 14 named candidates.

**No per-agent EMC-scoped search of the 14 candidate rows had been run.** That is the gap, and it is
different in kind from every held item on this paper: the E1 class-evidence, N1 residue, O1 registry,
R2 tier and V1 disclosure work were all about **internal consistency between the manuscript, the
review response and the registry**. None of them tested the manuscript against the literature.

⭐ The gap turned out to be even narrower than expected: the falsifying evidence is **inside a paper
the manuscript already cites** (reference [19]), and its EMC content had already been extracted on
2026-09-08 by a **sibling lane working on a different paper** —
`reports/W07c-toxicity-fulltext-resolution.md` recorded n(EMC)=3 and "1 EMC" among the responders
while answering a toxicity-denominator question. It was never routed to PUB-REPURPOSING;
`CROSS-PAPER-ADVANCE-2026-09-08.md` contains **0** mentions of cabozantinib.

## 4 · The bounded step taken, and its result

Four EMC-scoped PubMed queries covering every agent in Table 2, metadata for all 12 non-trivial hits,
and one full text. **Thirteen of fourteen rows survive. One is falsified.**

**Cabozantinib is not an untested class extension in EMC.** According to PubMed, the phase II trial
cited by this manuscript as [19] (PMID 34716194, PMC8776602,
[DOI](https://doi.org/10.1158/1078-0432.CCR-21-2480)) enrolled **three patients with EMC** among 54
evaluable, reports **one confirmed partial response in an EMC patient** after ten cycles, and calls
that the **longest response on the trial** (still on study at 99 cycles). The manuscript instead
describes [19] as showing *"activity of the class in unselected soft-tissue sarcoma"* and grades the
whole VEGFR row as *"untested extensions"*, novelty *"Partly"*.

Three manuscript statements are therefore false as written:

1. Table 2, VEGFR row: *"these specific agents are untested extensions"*.
2. Abstract: *"The single candidate with EMC clinical evidence, imatinib …, is also the only one
   already reported"*.
3. Table 1: the "Clinical, EMC patient" row containing imatinib alone, with the VEGFR class placed
   one row lower at "Clinical, class level".

⛔ No efficacy, safety or therapeutic-window claim is made or implied here. A three-patient subgroup
of a mixed-histology trial that **missed both of its primary endpoints**, and whose adverse events are
reported only against all 54 patients, is a report that the agent was given in EMC — nothing more.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `EVIDENCE-cabozantinib-emc.md` (the 14-row check table plus the verbatim full-text
passages) and `PROPOSED-UNAPPLIED-repurposing-cabozantinib.diff` — an **exact, unapplied** unified
diff against the committed manuscript correcting the abstract, Table 1, Table 2, §5 Tranche 2 and the
§6 limitation. It **adds no reference** ([19] is already cited), changes no tier, no rule and no
registry file.

**Validation / baseline.** The baseline is the committed manuscript at the current checkout. Every
falsified sentence is quoted verbatim from it and located by line. The counter-evidence is quoted
verbatim from the PMC full text, and the two independent numbers (n(EMC)=3; one EMC responder) agree
with what the sibling W07c lane extracted from the same article on 2026-09-08 by a separate route.

**Provenance.** PubMed / PubMed Central via the PubMed MCP server, 2026-09-08 23:59Z-2026-09-09 00:05Z.
Queries, returned PMID sets, the 49.6 KB metadata result and the repo greps are in `checks/`, one
directory per attempt, with `command.txt`, `stdout.txt`, `stderr.txt` and `exit_code.txt`. All seven
attempts exited 0; there were no failures to preserve.

**Limitations.**
- A title/abstract-scoped search proves only that nothing is *indexed* on a pairing. The thirteen
  surviving rows are **"nothing indexed"**, not "nobody has done it" — a subgroup buried in a
  supplementary table stays invisible, which is how cabozantinib itself survived four earlier screens.
- Only PubMed was queried. Europe PMC, trial registries, congress abstracts and non-indexed venues
  were not, and no full text was read for the thirteen surviving rows.
- The proposed diff **splits the single VEGFR candidate row into two**, so Table 2 gains a row while
  the candidate count stays 14 agents-plus-classes. Whether "14 candidates" should be restated is an
  **editorial decision for the coordinator**, not made here.
- ⚠ **Unadjudicated consequence, flagged not resolved.** The paper defines T3 as *"prospective or
  substantial clinical evidence in EMC"*. A prospective multi-site phase II trial that enrolled EMC
  patients is prospective EMC clinical evidence for cabozantinib. That bears directly on the R2/V1
  proposal to regrade imatinib to T2 on the ground that nothing reaches T3. **I did not change any
  tier, the scale, the firewall rule or the registry, and I take no position on the regrade.** It is
  an input the tier decision did not have.
- I did not re-read reference [7] or [1]; imatinib's row is characterised as the manuscript
  characterises it.

**Stop condition.** Reached: the question was answered decisively for all fourteen rows, the artifact
and the unapplied diff exist, and the remaining moves (applying the diff, restating the candidate
count, re-opening the tier decision) all require shared-state authority this lane does not have.

## 6 · Next credible independent work

1. Coordinator decision on the unapplied diff, and on whether the tier decision reopens with the
   cabozantinib input.
2. The same per-agent search extended to Europe PMC and the trial registries, which reach the
   non-PubMed-indexed literature this check cannot see.
3. A standing routing rule: W07c held the falsifying fact for a day inside another paper's lane. A
   cross-paper index of *EMC patient-level agent exposures* would have surfaced it immediately.
