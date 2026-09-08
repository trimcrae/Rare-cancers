# E1 — paper-level contract, recorded BEFORE launch

`date -u` **Tue Sep 8 08:18 UTC 2026**. Same session, sole parent, `claude-opus-5` medium, saved subscription,
no overage, deadline 2026-09-09T02:37:19Z. Disk 20 GiB free (floor 10 GiB).

## Correction accepted first

**"Already drafted" was an invented exclusion.** A1 and A2 both used it as a hard gate and I propagated it into
my own adjudications. Drafted ≠ published, complete, scientifically closed or automatically publishable. The
next-paper scope **includes existing drafted-but-unpublished manuscripts**, and a wholly new question is not
required. D1–D3 do **not** advance the mortality-mechanisms draft, which expressly excludes host-factor
arithmetic — so that draft is not the target here.

## Selected paper

- **Title / path:** *Repurposing hypotheses* — `research/manuscripts/repurposing/repurposing-hypotheses.md`
  (7,854 words), endpoint `PUB-REPURPOSING`, state `drafted`, unpublished.
- **Prior review already on file:** `repurposing-hypotheses-peer-review-2026-08-10.md`,
  `repurposing-hypotheses-review-response-2026-08-10.md`, `repurposing-hypotheses-review.md`, and the paper's
  own §6 correction log.

## The exact unfinished substantive issue — parent-verified, not inherited

§4.1 states that after both pre-specified in-silico rationales returned negative, the proteasome candidate
**"survives on a published ex-vivo observation alone"**, and §3/§5 carry carfilzomib as **"untried"** with
"preclinical replication, then a combination arm" as its next step.

**Measured by me in the committed tree:** `research/literature/carfilzomib-class-clinical-2026-08-28.json`
holds **PMID 15739208 — Maki et al., "A multicenter Phase II study of bortezomib in recurrent or metastatic
sarcomas", *Cancer* 2005** (DOI 10.1002/cncr.20968), plus **PMID 40941020 — a 2025 Phase I of carfilzomib with
cyclophosphamide and etoposide in relapsed/refractory leukaemia and solid tumours**. **`grep` of the manuscript
returns 0 occurrences of `15739208`, `Maki` or `MAKI`.**

⭐ **So a repurposing menu presents a proteasome-inhibitor candidate as untried and ex-vivo-only, while a
Phase II of that class in the parent histology has existed since 2005 and is cited nowhere in the paper.**
That is a completeness defect in a claim the paper actually makes — exactly the class its own peer review flags
("in an ultra-rare tumour, evidence strength and novelty are structurally anti-correlated"), and it is the
strongest concrete, input-backed manuscript issue available from existing evidence.

## Contribution of the step

The paper becomes honest about its own novelty axis for this candidate: class-level clinical experience in
sarcoma is disclosed where the paper claims untried status and ex-vivo-only survival. **This is claim
hardening, not a new result.** No new scientific claim is created.

## Named-hold non-overlap — checked, not assumed

Not C1 (closed; no regeneration, variant, guard bypass or row withdrawal). Not the mortality-mechanisms draft.
Not W25 / GSE243553 / primary-article / Results / novelty — the blocked writer is **not** woken, retried or
rerouted. Not the NR4A Perspective or the P6 successor. Not the frozen submitted comment, ASO or RNA assets.
Not the parked synthetic figure-validation family, S1/S3, or P1–P6 dispositions. No S7 NCBI or D2 DOI egress
bypass; **no network of any kind** — the two records are already committed. `15739208`, `40941020` appear on no
denied list.

## Finite acceptance

1. The class evidence is disclosed in the paper **where the affected claims live** (§4.1, and the §3/§5 rows
   asserting untried status), **by replacement, not appending** — the hardening convention on file.
2. **Abstract-level only, and labelled as such:** the artifact states no full text was retrieved — PMID
   15739208 has no PMCID and PMC12428389 was not fetched. Enrolment denominators and per-histology outcomes are
   **UNKNOWN and stay UNKNOWN**.
3. **No overclaim in either direction.** A 2005 Phase II of **bortezomib** is a different agent, era and
   regimen; it is **not** evidence that carfilzomib fails, and equally the paper may no longer imply the class
   is clinically untried in sarcoma.
4. The paper's word count stays within its venue cap, and **no hedge is deleted to make room**.
5. Applicable manuscript linters are run and reported honestly. ⛔ **If adding a citation trips a gate, that is
   a finding to report — never a reason to weaken, relax or edit the gate.**

## Stop conditions

Stop if the §4.1 premise does not hold on reading; if the correction cannot be made within the word cap without
deleting a hedge; if any change would require a network call, a new source, or a guard change; or at ~40 tool
calls / ~40 minutes. Edits are confined to
`research/manuscripts/repurposing/repurposing-hypotheses.md`. **No PR, no publication, no graph edit, no
`candidates.json` change, no other manuscript.** The parent integrates and commits.
