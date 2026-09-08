# MEMO — R2: does one published case report meet the repurposing paper's own T3?

PROPOSED analysis. Nothing here is applied. This is **not** a recovered draft, and no external
canonical draft is assumed to exist. Baseline: `git HEAD cc23cd1dfe175aa0f82a3042fa11bfac0aa1f6f5`,
file `research/manuscripts/repurposing/repurposing-hypotheses.md` (711 lines).

## 1 · The test — the paper's own definitions, quoted (baseline §2.2, lines 211–213)

> "Each candidate is graded by the strength and proximity of its supporting evidence. T3 denotes
> prospective or substantial clinical evidence in EMC; T2, a case-level signal in EMC or in a very
> close relative; T1, a preclinical or in-vitro signal, or a strong analogy in a related
> fusion-driven sarcoma; T0, mechanistic rationale only. The tier states how speculative a
> hypothesis is, not the expected effect size."

## 2 · The evidence under imatinib's grade, quoted from the committed file

- §4, line 416: "Imatinib in the *KIT*-mutant subset is the only candidate at T3, resting on direct
  EMC clinical evidence: a *KIT* exon-11-mutant patient with 3 years of disease stabilisation [7]."
- Table 2, line 317: "Imatinib, *KIT*-mutant subset (KIT) | Clinical: one patient, 3 years of stable
  disease [7] | No, already reported"
- Reference [7], line 667: "Jennings B, et al. Sustained response to imatinib in patient with
  extraskeletal myxoid chondrosarcoma and novel KIT mutation. *BMJ Case Rep.* 2021.
  doi 10.1136/bcr-2021-242039. PMC8395296."
- The only other imatinib-adjacent EMC data cited (§1.1, lines 155–157) are *prevalence* figures for
  activating *KIT* mutations (1/20 [6]; 2/48, ~4% [2]) — biomarker frequency, not treatment
  evidence, and they cannot raise a treatment-evidence tier.

So the entire evidentiary basis of the grade is **one published single-patient case report**.

## 3 · Verdict — REGRADE TO T2 (on the grade question)

Applying the paper's own definitions to its own cited evidence:

1. **T3 requires "prospective or substantial clinical evidence in EMC."** A retrospective,
   single-patient case report is not prospective. One patient is not substantial by any reading that
   leaves the word work to do — the scale itself contrasts it with the class-level, multicentre
   phase-2 evidence the paper cites elsewhere (§1.1, pazopanib, NCT02066285). Neither disjunct of
   the T3 definition is satisfied.
2. **T2 is defined as "a case-level signal in EMC or in a very close relative."** The imatinib
   evidence is a case-level signal *in EMC* — the first disjunct, matched exactly and without
   analogy or stretching.
3. The T3 grade is therefore **inconsistent with the paper's own definition** of T3, and the
   evidence falls squarely inside T2. On the committed text this is decidable, and it decides
   against T3.

The plausible defence of T3 — that the four-valued scale means "clinical evidence *in an EMC
patient*" as its top rung, above "case-level in a close relative" — is **foreclosed by the committed
wording**, which places "a case-level signal *in EMC*" in T2 explicitly. The paper cannot both define
T2 that way and grade this evidence T3.

Note what this verdict is **not**: it says nothing about whether imatinib works in *KIT*-mutant EMC.
It is a statement about internal consistency between a grading scale and the evidence graded. No
efficacy, safety, selectivity or clinical-readiness claim is made or implied; there is no wet lab.

**Undecidable sub-question:** whether the scale should stay four-valued with T3 defined-but-empty
(Candidate A) or collapse to three values (Option B, as the 2026-08-10 response describes). The
evidence test settles the grade only. Arity is an editorial choice for the paper's owner, and is
listed UNRESOLVED.

## 4 · Dependent locations, with PROPOSED text

Complete map of every place in the committed file that the grade actually touches:

| # | Location (baseline line) | Carries a T-token? | Change entailed |
|---|---|---|---|
| 1 | §2.2 tier definitions, 211–213 | yes | A: add occupancy sentence. B: drop T3 from scale. |
| 2 | Abstract, 111–112 "tier from T0 to T3" | yes | A: none. B: "T0 to T2". |
| 3 | Abstract, 114 "single candidate with EMC clinical evidence" | no | none — statement remains true |
| 4 | Highlights, 129 | no | none |
| 5 | Table 1, 299–306 | **no** | none under A or B (see Option B fragment B5) |
| 6 | Table 2, 317 imatinib row | no | none — evidence is already stated as one patient |
| 7 | §4 Tranche 1, 415–417 "the only candidate at T3" | yes | **must change** — drafted |
| 8 | §5 first limitation, 522–523 "only imatinib reaching T3" | yes | **must change** — drafted |
| 9 | §5 ethics firewall, 575–578 "graded T0 to T2 out … at T3 may migrate" | yes | **collides with the registry — UNRESOLVED, not drafted as a recommendation** |
| 10 | Figure 1 caption, 275 "admitting only tier T3" | yes | same collision; also implicates the figure PNG asset |
| 11 | §2.6 firewall prose, 270–273 | no | none — states "direct EMC clinical evidence" without a tier token |
| 12 | §6 Critical view, 584–608 | **no** | none |
| 13 | §2.7 | — | **does not exist**; Methods run 2.1–2.6 |

Drafted text for 1, 7, 8 is in `CANDIDATE-A-T2-repurposing-hypotheses.md` / `CANDIDATE-A-T2.diff`.
Option B variants are in `OPTION-B-scale-collapse-fragments.md`.

## 5 · The registry-rule tension — stated precisely, LEFT UNRESOLVED

The firewall rule, as committed (§5, lines 575–578):

> "A firewall keeps hypotheses graded T0 to T2 out of all patient-facing material; only a candidate
> reaching direct EMC clinical evidence at T3 may migrate into the project's cited clinical
> registry, and then only after clinician review."

and Figure 1's caption (line 275): "A firewall governs what may reach patient-facing material,
admitting only tier T3 after clinician review."

Imatinib is **already in** that registry. `research/data/emc-clinical-registry.json` carries
"Imatinib (KIT inhibitor) — only for KIT-mutant EMC", status "Off-label; single published case
(biomarker-restricted)", citing the same case report; and the manuscript states this itself (§4,
lines 420–424): "It is not a hypothesis awaiting promotion into the project's cited clinical
registry: it is already listed there".

**The tension:** regrading imatinib to T2 makes the paper assert an admission rule that its own
registry entry violates — a T2 item sitting inside a registry the paper says admits only T3, and
inside material the same sentence says T2 items are kept out of. The contradiction is created by the
regrade; it is not created by, and does not by itself impeach, either the registry entry or the rule.

At least three shapes of resolution exist — **none is chosen here, and none is applied**:
(a) restate the rule by evidence *kind* ("direct EMC clinical evidence, after clinician review"), the
wording §2.6 already uses, so the rule stops depending on the tier token; (b) keep the tier-valued
rule and re-examine the registry entry against it; (c) distinguish the cited clinical registry from
"patient-facing material", which the committed sentence currently conflates. Choosing among these is
a scientific and clinical-governance judgement for the paper's owner, not a drafting fix, and it
interacts with a registry this lane must not touch. **Left unresolved by instruction and by merit.**

## 6 · UNRESOLVED list (explicit)

1. **Scale arity.** Four-valued with T3 defined-but-empty (A) vs three-valued (B). Not settled by the
   evidence; owner's editorial choice.
2. **The firewall rule.** See §5 above. Not drafted as a recommendation; not applied.
3. **Figure 1 asset.** The caption's "only tier T3" is mirrored in
   `research/figures/repurposing-fig1-design.png`, which this lane did not open and cannot
   regenerate. Whether the rendered figure carries the tier token is **unknown**, not zero.
4. **Which draft is canonical.** Unchanged from the blocker: the regrade must be applied, if at all,
   by the paper's owner as one coherent revision, not unilaterally.
5. **The response's §2.7 and Table 1 propagation targets** have no counterpart in the committed file.
   Recorded as an observation about the two texts; no history hunt was run and no external draft is
   posited.
6. **Reference-count mismatch** (response: 25; file: 22) — untouched. No reference was added.

## 7 · What this memo does not do

No shared file, registry, gate or patient-facing artifact was edited. No reference or citation added.
No git write. No network, no source retrieval — reference [7] was assessed **as the committed file
characterises it**, and this memo does not claim to have read the case report itself. No efficacy,
safety or clinical-readiness claim. Everything above is PROPOSED.
