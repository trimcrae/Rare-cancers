# RUNG 5a(c) — E3 recruiter staging and the downselect to ≤2

**Lane doc, 2026-07-25.** Companion to the machine-readable
[`e3-recruiter-staging.json`](e3-recruiter-staging.json) and its generated table
[`e3-recruiter-staging.md`](e3-recruiter-staging.md). Engine:
[`e3_recruiter_staging.py`](e3_recruiter_staging.py); tests:
[`tests/test_e3_recruiter_staging.py`](tests/test_e3_recruiter_staging.py). Cost: **$0** (CPU/CI only).

> **Honest scope.** This is *design prep*, not a validated result. Ligandability computed from one deposited
> holo structure is a **hypothesis for testing**: it says a published ligand occupies a pocket with a
> solvent-directed exit vector, and nothing more. Advancing a recruiter means "carried into a computational
> search", never "suitable for use". No claim of efficacy, safety, therapeutic window, or clinical readiness
> is made or implied.

---

## 1 · What this stage is for, and the one constraint that shapes it

[nr4a3-program-map.md](../manuscripts/nr4a3-program-map.md) → *The prospective stage*, item **(c) E3 breadth, free at the search stage*:

> widen beyond VHL/CRBN to the ligandable set with public ligand-bound structures (cIAP1/BIRC2, DCAF1,
> DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2). Since basin search is CPU this costs ~nothing and multiplies
> the chance that *some* E3 surface complements NR4A3's differential surface. **Downselect to ≤2 recruiters
> before any GPU leg, and log what was dropped** — a silent top-N reads as "we covered everything".

Two things follow, and they pull in opposite directions. Widening is free at CPU; a wide set multiplied by
GPU legs is not. So the cap is not an aesthetic preference — it is the thing that keeps the RUNG 5 ladder
priced. And the logged dropped set is not an appendix: without it, "we searched ten and advanced two" is
indistinguishable from "we searched two".

**The constraint that decides *how* the cut is made.** Availability was already answered, for $0, and it does
**not** discriminate: all eight widened arms are broadly expressed and record-complete on the Human Protein
Atlas (`nr4a3_e3_expression.py` → [`nr4a-e3-expression.json`](nr4a-e3-expression.json), CI run 30125742542),
exactly as the original VHL/CRBN check found. STRATEGY is explicit that **no recruiter may be dropped with
"not expressed" as the reason**, and that the cut must be made on **ligandability + interface geometry**.

That is asserted here structurally, not promised in prose: every dropped row carries
`availability_was_not_a_factor: true`, the JSON carries an `availability_assertion` block, and a unit test
(`test_availability_is_never_a_drop_reason`) fails the build if a drop reason so much as contains the string
"express".

## 2 · What was computed, and why each number is the one that matters

Everything is fetched or computed; nothing is recalled. Gene symbols resolve through UniProt's own search
with a reviewed / human / exact-gene-name guard that **refuses** rather than substitutes a plausible-looking
accession — the same fail-closed pattern the HPA resolver uses, and for the same reason: a wrong accession
would silently stage a different protein and nothing downstream would notice.

| quantity | how | why it is the deciding number |
|---|---|---|
| **staged structure** | RCSB search on the accession, restricted to entries carrying ≥1 non-polymer entity, sorted by resolution; RCSB data API for method, chains, ligand CCD, primary citation | a recruiter with no public ligand-bound structure cannot be staged for linker design at all — the handle would have to be invented, which is a far weaker claim |
| **ligand burial** | Shrake–Rupley SASA of the ligand free vs in the deposited complex | a linker exerts force on the handle; a ligand lying on a surface at <50 % burial has no pocket holding it |
| **site enclosure** | fraction of 256 rays from the ligand centroid meeting protein within 12 Å | separates a cavity from a groove from a flat epitope |
| **cavity volume** | LIGSITE protein–solvent–protein scan (Hendlich 1997), ligand-proximal, MINPSP 5/7 | pocket size, on a literature algorithm rather than a bespoke score |
| **fpocket druggability** | fpocket on the deposited chains with the ligand removed; the ligand attributed to a pocket by alpha-sphere proximity, the file→pocket mapping derived from alpha-sphere fingerprints (never the filename index) | the same field-standard number this program already uses for the NR4A3 cryptic pocket, so the two are comparable |
| **★ exit vector** | the ligand heavy atom with the largest SASA in complex is the anchor; 512 Fibonacci rays from it; a ray ends where a 1.7 Å linker heavy atom would clash with a protein vdW sphere; the direction is the **solid-angle centroid of the near-maximal rays** | this is the direction a linker must leave from. Taking the centroid rather than `argmax` matters: a wide mouth ties dozens of rays at the cap, and `argmax` would then return whichever the iteration order reached first — a coordinate artifact, not geometry |
| **★ open solid-angle fraction (15 Å)** | fraction of all 512 rays with ≥15 Å unobstructed reach from the anchor | **the number the orientation-basin search consumes**: the geometric size of the orientation space a tethered target can occupy, before any energetics |
| **linker-bearing analogue** | answered *structurally* from deposited entries — tier 3 a ≥500 Da ligand that is **verified from the coordinates** to contact both the recruiter and a non-arm partner chain; tier 2 a ≥500 Da ligand with the recruiter alone; tier 1 only sub-500 Da ligands; tier 0 none | a solved structure with a linker already leaving this exit vector is the only *direct* evidence in the whole panel that the vector tolerates a linker |

**The burial routine is checked against an independent implementation, not assumed.** `sasa_per_atom` computes
per-atom Shrake–Rupley with an occluders-only `subset` (the ligand's area inside the full complex, without
paying for the other ~5,000 protein atoms). Summed per residue on the repo's AF2 NR4A3 model it reproduces
`nr4a_differential_atlas.shrake_rupley` — written independently, for a different purpose — to **0.0 Å² on
every one of 626 residues**, total 59,736.4 Å² either way. The optimisation changes cost, not the number.

### Four frame decisions that change the answer

None of these is a detail; each was forced by something the first run actually returned.

1. **The geometry frame is a partner-free structure wherever one exists.** Run 30167890490 staged VHL on
   **7Z76** (VHL·ELOB·ELOC + SMARCA2) and CRBN on **8RQC** (CRBN + IKZF1) — both ternary. In that frame the
   bound partner sits in the orientation space being measured, so "this recruiter has a solved ternary" was
   being scored as "this recruiter has nowhere for a target to go". Those runs' openness numbers (VHL 0.164,
   CRBN 0.236) are artifacts and are not quoted anywhere as results.
2. **The occluder set is the recruiter plus its own CRL arm**, with arm membership read from the single
   existing definition of those arms in `nr4a3_e3_expression.py` rather than re-listed. A neosubstrate,
   PROTAC target or crystallisation partner is removed. Where **no** partner-free structure exists, the
   recruiter still stages, flagged, with the honest caveat that its site may be partly formed *by* the
   removed partner.
3. **Coordinates come from biological assembly 1, not the asymmetric unit.** FEM1B **9PW8** has chains A and
   B, *both* FEM1B, and returned an exit clearance of 0.0 — a ligand walled in by a crystallographic
   neighbour that is not there in solution. Failing a recruiter at G3 for a packing artifact is precisely
   the silent error the dropped-set log exists to prevent.
4. **Tier 3 is verified, not asserted.** Entry-level co-presence of a second protein is not bridging. Since
   `linker_analogue_tier` is the top lexicographic key, an unverified tier 3 could have decided the whole
   result on its own, so the coordinates are re-read and the tier is demoted when the ligand does not
   actually contact both proteins.

**Interface geometry, honestly bounded.** The open solid-angle fraction is interface geometry *at the
attachment point* — how much orientation space exists. Whether any orientation in that space is
thermodynamically favourable, and whether it discriminates NR4A3 from NR4A1/2, is the orientation-basin
search's question, not this module's. This stage hands over a receptor, an attachment point, and the size of
the space; it does not pre-judge what is in it.

## 3 · The rule, preregistered

The rule was committed **before** the CI fetch that produced the data (commit on
`claude/max-effort-2dq11l-e3`, "RUNG 5a: E3 recruiter staging + ligandability downselect — schema, engine,
preregistered rule"), so it cannot have been fitted to the answer.

**Gates — all must pass to be eligible.**

1. **G1 · a public ligand-bound structure.** ≥1 deposited entry with the recruiter and a non-solvent,
   non-cryoprotectant ligand of ≥10 heavy atoms, at ≤3.0 Å (diffraction/EM) or by solution NMR.
2. **G2 · the ligand is pocket-bound.** Buried fraction of the primary ligand's SASA ≥ 0.50.
3. **G3 · a linker can leave.** Exit clearance ≥ 8.0 Å **and** 30° cone openness ≥ 0.30. (8 Å is the shortest
   reach of any linker the RUNG 5b virtual library will enumerate; a cone open in <30 % of nearby directions
   is a channel, not an exit.)

**Ranking — Pareto, not a scalar.** Validation requirement 5 forbids a tunable scalar, so eligible recruiters
are ranked by the **nondominated front** over three axes — `linker_analogue_tier`, `exit_quality`
(min(clearance, 20) × cone openness), and `orientation_openness` — followed by a **fixed lexicographic
tiebreak** `(analogue tier, orientation openness, exit quality, −resolution)` to reach the cap of 2. A unit
test asserts the rule contains no weight.

**Backfill.** If the front collapses to a single recruiter, the second slot is filled by the best
gate-passing recruiter outside the front, and labelled as backfilled. Carrying one E3 forward would leave the
E3 an **uncontrolled variable** in every downstream basin comparison — there would be no E3-choice
sensitivity check at all. The cap is ≤2, not ==1.

## 4 · Result

**Advanced: CRBN and VHL.** Source: GitHub Actions run **30169233382** (job 89707362939), 2,919 fetched URLs.
The full per-recruiter table lives in the generated [`e3-recruiter-staging.md`](e3-recruiter-staging.md) and
is not restated here.

| | CRBN | VHL |
|---|---|---|
| structure | **9CUO**, 1.60 Å, X-ray | **9GIO**, 1.486 Å, X-ray |
| chains | A–F = cereblon (assembly frame A–C) | A = Elongin-B, B = Elongin-C, C = VHL |
| ligand | **A1A0J**, 259.3 Da, 19 heavy atoms | **3JF** (VH032-class), 472.6 Da, 33 heavy atoms |
| citation | Jal. *J. Med. Chem.* 2024, `10.1021/acs.jmedchem.4c01305`, PMID 39151120 | *ACS Med. Chem. Lett.* 2025, `10.1021/acsmedchemlett.4c00582`, PMID 40236540 |
| construct | 113 aa (thalidomide-binding domain), 0.256 of full length | 160 aa, 0.751 of full length |
| buried fraction | 0.634 | 0.665 |
| exit clearance / cone | 25.0 Å (cap) / 1.00 | 25.0 Å (cap) / 1.00 |
| **open solid angle (≥15 Å)** | **0.549** | **0.516** |
| analogue tier | 3, bridging **verified** on 8RQC | 3, bridging **verified** on 7Z76 |
| status | sole Pareto-front member | **backfilled** for E3-choice sensitivity |

**CRBN is the only Pareto-front member.** VHL advances as the backfill, not as a co-winner: it is dominated
by CRBN (equal analogue tier, equal saturated exit quality, marginally lower open solid angle) and is carried
so that the E3 is a controlled variable in every downstream basin comparison rather than a confound. That
distinction is in the JSON (`backfilled_for_e3_choice_sensitivity`) and in `load_advanced()`'s `caveats`, and
it should survive into anything the basin search reports.

**Read the CRBN-over-VHL margin as a tie, not a finding.** The two differ by 0.033 in open solid angle on a
single deposited conformer each, with no error model on that quantity. Nothing here says CRBN is the better
recruiter for NR4A3 — only that both clear every gate comfortably and neither can be excluded at this stage.

### Three checks that changed the answer, each on real data

- **The bridging check demoted DCAF15.** Its tier-3 label rested on entry-level co-presence in **8ROY**; the
  coordinates show the ligand contacting DCAF15 (87 contacts) and **not** the partner (0). Tier 2, logged.
  Every other tier-3 claim survived verification: VHL on 7Z76, CRBN on 8RQC, BIRC2 on 6W7O, DCAF1 on 9NSN,
  DCAF16 on 8G46.
- **The exit-vector fix rescued FEM1B from a false drop.** It had been failing G3 at clearance 0.0; it now
  reads 25.0 Å with a 0.543 cone and passes. It is still dropped — on the Pareto front, at tier 1 and an open
  solid angle of 0.045 — but for the right reason.
- **The frame fix reversed the whole result.** Before staging preferred partner-free biological assemblies,
  the advanced pair was BIRC2 + MDM2, because VHL and CRBN were being measured inside ternary complexes whose
  bound partner occupied the orientation space. Those numbers are retracted, not merely superseded.

## 5 · The dropped set

Eight recruiters dropped, every one with its reason recorded in
`downselect.dropped[]` and none of them for availability. Two failed a gate; six were Pareto-dominated.

**Failed a gate — a structural fact about the recruiter, not a ranking:**

- **RNF114** — **G1**. No deposited structure of the protein at all (RCSB returns nothing for Q9Y508). This is
  the strongest form of the drop: not "un-liganded", but structurally unknown. The module distinguishes those
  two cases precisely because they mean different things about ligandability.
- **DCAF16** — **G2**, buried fraction **0.344** against the 0.50 threshold. Measured on 8G46 with BRD4
  removed from the occluder set, its ligand YK3 is not held in a DCAF16 pocket; it lies at an interface that
  the partner helps form. That is what a molecular-glue site looks like when you take the partner away, and
  it is the single most informative drop in the panel: **DCAF16's site is not a handle pocket to hang a
  linker on.** Note its open solid angle is the highest in the panel (0.736) — openness without a pocket.

**Pareto-dominated — passed every gate, lost on ligandability + interface geometry:**

| recruiter | tier | exit quality | open solid angle | why it lost |
|---|---|---|---|---|
| BIRC2 | 3 | 20.0 | 0.510 | matched CRBN on tier and exit quality, marginally lower openness — the closest call in the panel |
| MDM2 | 2 | 20.0 | 0.514 | openness comparable to CRBN, but no solved bivalent complex |
| DCAF15 | 2 | 20.0 | 0.217 | tier demoted by the bridging check; low openness |
| DCAF1 | 3 | 16.6 | 0.180 | only gate-passer with a non-saturated cone (0.829); low openness |
| KEAP1 | 2 | 20.0 | 0.147 | lowest openness of the tier-2 group |
| FEM1B | 1 | 10.9 | 0.045 | no published linker-bearing form, and the tightest exit in the panel |

**BIRC2 is the drop most worth revisiting.** It is tier 3 with verified bridging (6W7O), the best resolution
in the panel (1.249 Å), and an open solid angle within 0.04 of CRBN's. It lost a near-tie on one axis measured
from one conformer. If the basin search finds CRBN and VHL geometrically unpromising against NR4A3, BIRC2 is
the first recruiter to bring back — and it costs $0 to do so, because everything needed is already staged in
the JSON.

## 6 · What this does and does not hand to the basin search

**Hands over.** For each advanced recruiter: a named deposited structure and the biological assembly it was
read from, the chains that are the recruiter and the chains that are its own CRL arm, the linker attachment
point `anchor_xyz` in that structure's own frame, the outward unit `exit_direction`, how far a linker reaches
along it, and `open_solid_angle_fraction_15A` — the size of the orientation space available to a tethered
target before any energetics. The consumer API is `e3_recruiter_staging.load_advanced()`, which also returns a
`caveats` list that must be carried into any downstream report.

**Does not hand over.** Whether any orientation in that space is thermodynamically favourable; whether it
discriminates NR4A3 from NR4A1/2; whether a linker of the required length is synthetically reachable; whether
the recruiter's own pharmacology is tolerable. Those are the basin search's, RUNG 5b's, and a literature
assessment's questions respectively. Nothing here is a selectivity claim.

## 7 · Proposed nr4a3-program-map.md deltas

*This lane does not edit nr4a3-program-map.md. The exact edits requested are listed here for whoever owns that file.*

See the lane's final report for the verbatim quote/replacement pairs; in substance:

1. **§"The prospective stage" → item (c)** should record that the widening and the mandatory downselect are
   **done**, name the advanced pair and the artifact, and state the finding that changes how (c) reads: the
   binding constraint on E3 breadth is **structural stageability**, not availability. HPA says all eight
   widened arms are available; the PDB says the panel is materially smaller than eight.
2. **RUNG 5 → 5a** should mark the recruiter-staging half complete with its artifact paths and cost ($0), so
   the remaining 5a work is unambiguously the orientation-basin search itself.

## 8 · Limits

- One deposited conformer, one ligand copy, no protein flexibility, no linker sampling, no explicit solvent.
  The exit vector **bounds where a linker could leave**; it does not show that any particular linker does.
- The linker-bearing-analogue tier is structural evidence from deposited entries, **not a literature
  review**, so it under-counts recruiters whose linker-bearing chemistry is published without a crystal
  structure. A tier-1 recruiter is "no solved linker-bearing structure", not "no linker chemistry exists".
- fpocket druggability is a pocket-shape score computed on the apo-ised deposited chains. It is not a
  measured affinity and carries the same caveats as every use of it in this program.
- Everything here is conditional on the deposited structure being a reasonable model of the recruiter as it
  exists in the ternary complex. Substrate receptors are conformationally active; a recruiter whose pocket
  is only ordered in the presence of its published ligand is being read at its most favourable.
- Availability is recorded and then deliberately **excluded** from the rule (§1). That is a decision, not an
  oversight: the HPA panel is uniformly positive, so including it would add no discrimination while giving
  the appearance of a filter that did work it did not do.
- **★ The rule is blind to recruiter-intrinsic pharmacology, and that is a real omission.** Several
  ligandable E3s are ligandable *precisely because* their handle is a well-developed inhibitor of the E3's
  own function — a nutlin-class MDM2 handle also inhibits MDM2; a KEAP1 handle perturbs the KEAP1–NRF2 axis.
  A recruiter can therefore win on ligandability and interface geometry while carrying an on-target
  liability this stage cannot see. Any recruiter advanced here must have that liability assessed from the
  literature **before** it is committed to. It is an input to the next gate, not a footnote.
- **Arm membership is only as complete as the availability module's component lists.** `nr4a3_e3_expression.py`
  defines each arm as substrate receptor + adaptor(s) + cullin + RBX1, which omits accessory subunits such as
  **DDA1** in CRL4. Any chain not on that list is treated as a partner and removed from the occluder set, so a
  structure containing a genuine accessory subunit is measured slightly **over-open**. The error runs in the
  conservative direction — it cannot falsely seal a site — and every removed chain is recorded in
  `ligandability.occluder_set.partner_entity_chains_excluded`, so it is auditable per recruiter rather than
  hidden.
- The exit-vector quality axis **saturates**: clearance is capped at 20 Å and most gate-passing recruiters
  reach a 30° cone openness of 1.0, so `exit_quality` mostly restates G3 rather than discriminating. The
  discrimination in practice comes from the analogue tier and the open solid angle. This is reported, **not
  retuned** — amending a preregistered rule after seeing the result is exactly the move nr4a3-program-map.md forbids
  without a dated, reviewed defect-fix.
