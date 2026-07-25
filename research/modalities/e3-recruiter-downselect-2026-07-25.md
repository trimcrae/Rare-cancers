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

[STRATEGY.md](../../STRATEGY.md) → *The prospective stage*, item **(c) E3 breadth, free at the search stage*:

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

*(filled from the CI run — see §5 for the dropped set)*

## 5 · The dropped set

*(filled from the CI run)*

## 6 · Limits

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
  retuned** — amending a preregistered rule after seeing the result is exactly the move STRATEGY.md forbids
  without a dated, reviewed defect-fix.
