# Red-team of the EMC surface-target preprint — findings + resolutions

> **Role:** adversarial review log for [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md),
> run 2026-07-03 as two independent reviewers (a methods/scientific-integrity lens and a
> sarcoma/immuno-oncology domain lens), plus the discovery that reframed the paper. This file records the
> substantive findings and exactly how each was resolved (in the code, the data, or the manuscript), so a
> reader can audit the corrections. The review was harsh and the paper changed materially as a result — that
> is the intent.

## The reframing discovery (supersedes several findings)
Both reviewers attacked the surrogate on the premise that **EMC has no cell line in DepMap** (a project-wide
assumption). Re-examining the pipeline output falsified that premise: the single DepMap line matched by the
"myxoid" filter is **ACH-001519 = HEMCSS = the H-EMC-SS line**, DepMap OncotreeSubtype *"Extraskeletal Myxoid
Chondrosarcoma"* — a classic, real EMC cell line. So DepMap contains **one EMC line (n=1)**, and its surface
transcriptome is *real EMC data*, not a surrogate. This (a) resolves the "myxoid = myxoid liposarcoma"
critique (the line is EMC), and (b) upgrades the paper from purely-surrogate to *one real EMC line + a
translocation-sarcoma surrogate class*. n=1 gives no statistics, and H-EMC-SS authentication/fusion status is
flagged `[to verify]`, but this is the most EMC-specific in-silico signal available and is now reported
directly (`emc_line_top_surface` in `emc-surfaceome-scan.json`).

## Methods / integrity findings

**M1 (HIGH) — HPA "Tissue enhanced" mis-read as RESTRICTED.** In HPA's taxonomy "tissue *enhanced*" = detected
in essentially all tissues but elevated ≥4× in some (broad-with-a-peak), the near-opposite of restricted. The
classifier lumped "enhanced" with "enriched"/"group enriched" into RESTRICTED, so the top priors inherited a
"restricted" verdict from a keyword denoting breadth. **Fix:** `classify()` now separates "enhanced"
(→`ENHANCED_BROAD`) from "enriched/group enriched" (→`RESTRICTED` only if no vital/immune hit). Re-ran; the
"restricted" set collapsed accordingly — the honest result.

**M2 (HIGH) — controls validated the wrong branch.** DLL3/GPC3 (positive controls) are "tissue *enriched*",
so they only exercised the enriched→RESTRICTED path, never the (wrong) enhanced→RESTRICTED path. **Fix:** added
a **hard control, CD3E**, which is a "tissue enhanced"/immune antigen that must NOT come out restricted; the
classifier now flags it `VITAL_OR_IMMUNE_LIABILITY`. Controls now test the branch the priors use.

**M3 (HIGH) — NCAM1 given a ★ "selective" without a value.** **Fix:** the scan now reports NCAM1's
`enrichment_vs_rest` (+1.74) with a BH-significant MWU p; NCAM1 is selective, but its normal-tissue window
(NK/neural) is the disqualifier (see D2), so its priority is set by the window, not the missing number.

**M7 (MED/HIGH) — prose "ranks above B7-H3" contradicts the sort key** (`score()` sorts by
`class_frac_expressed` first, so B7-H3 at 98% sits at the top). **Fix:** added a proper **Mann-Whitney
selectivity test (BH-corrected)**; the paper now says B7-H3 is *not significantly selective* (p=0.98, q=1.0)
rather than "ranks below", and reports the significance-ranked selective set (CDH11/KIT/FGFR1/NCAM1/GPC2/…).

**M8 (MED/HIGH) — the "myxoid" surrogate line undisclosed.** Superseded by the reframing discovery: the line
is now named (ACH-001519 / H-EMC-SS) and identified as real EMC, with n=1 stated.

**M10/M11 (MED) — "each stage self-validates" overstated / scan self-validation tautological.** **Fix:** the
manuscript now says only two of four stages carry controls, and describes the surfaceome housekeeping check as
a minimal sanity check (ACTB/GAPDH are excluded by construction), not pipeline validation.

**M13 (MED) — ²²⁵Ac crossfire "~mm" is wrong.** α (²²⁵Ac) range ≈ 50–80 µm (a few cell diameters); only β
(¹⁷⁷Lu) is ~2 mm. **Fix:** corrected per-emitter ranges in the text.

**M14 (MED) — "unbiased" vs a curated seed union + undisclosed UniProt provenance.** **Fix:** the paper now
reports the UniProt provenance (status, `n_from_uniprot` vs seed) and softens "unbiased" to acknowledge the
always-unioned actionable seed.

**M16/M17 (LOW/MED) — HPA cancer-specificity column empty; EGFR/KIT dropped.** **Fix:** dropped the empty
cancer column, added HPA **blood-cell** specificity instead (which catches CD56/CD3); reported that EGFR is
*not* selective in the class (−2.21, ns) and KIT *is* (+2.46), integrating the only real-EMC-mentioned markers.

**M18–M24 (LOW) — "seven-platform" GSE4303 (confirmed: 7 matrix files), incidence cited-and-to-verify,
"quiet genome" citation, "solved"→"clinically validated", Table ordering, 2,820 vs scanned count, ifinatamab
in a to-verify cell.** All corrected in the manuscript text.

## Domain / clinical findings

**D1 (HIGH) — CDH11 misclassified; a pan-fibroblast/synovial/bone antigen, hazardous for CAR/TCE.** CDH11 is
on normal fibroblasts, synovium and bone body-wide (an RA/fibrosis target). **Fix:** with the corrected
classifier CDH11 is `ENHANCED_BROAD` (not restricted); the paper now names its normal-mesenchyme liability and
does not present it as a CAR/TCE prior. Its high cross-cancer enrichment (+3.18) is reframed as a
mesenchymal-vs-epithelial artifact (D6).

**D2 (HIGH) — CD56/NCAM1 on NK cells/brain/muscle, with a failed ADC precedent.** **Fix:** the classifier now
flags NCAM1 `VITAL_OR_IMMUNE_LIABILITY` via HPA blood-cell specificity (NK); the paper cites the discontinued
CD56 ADC **lorvotuzumab mertansine (IMGN901)** (efficacy failure + toxicity) and the CAR fratricide risk, and
removes CD56 from the top priors.

**D4 (HIGH) — surface modalities "shed" the delivery gate is overstated for EMC's myxoid matrix.** **Fix:**
added an EMC-specific penetration section — the abundant myxoid/chondroid ECM is a diffusion/binding-site
barrier to antibody, cell and radioligand delivery, and adult sarcoma has a poor CAR/TCE record — and reframed
the thesis as *orthogonal, differently-gated*, not "more tractable".

**D5 (HIGH) — RLT crossfire "tolerates a broad antigen" is backwards.** Crossfire mitigates heterogeneous
*tumour* uptake; for a broad *normal* antigen it widens the toxic field. **Fix:** corrected the mechanism; the
B7-H3/RLT rescue is dropped and replaced with the dosimetry/tumour-to-normal-ratio requirement.

**D6 (HIGH) — "selectivity = enrichment vs other cancers" inflates mesenchymal antigens.** The DepMap panel is
epithelial-dominated, so any mesenchymal marker scores "selective" while being ubiquitous in normal mesenchyme.
**Fix:** demoted cross-cancer enrichment to a "distinguishable-from-epithelial-tumours" descriptor; the
**normal-tissue window is now the primary axis**, and it is what disqualifies CDH11/CD56 despite their high
cross-cancer enrichment.

**D7 (HIGH/MED) — missing SSTR2/GD2 and the EMC neuroendocrine/IHC literature.** **Fix:** added **SSTR2** (a
cell-surface target of the *approved* NE radioligand ¹⁷⁷Lu-DOTATATE) and **GD2** as candidate hypotheses
grounded in EMC's neuroendocrine differentiation (INSM1, synaptophysin/NSE — real markers, cited), and added
SSTR2/B4GALNT1(GD2 synthase) to the window scan.

**D8 (MED) — B7-H3 demotion is an mRNA-vs-protein artifact.** B7-H3 protein is often tumour-restricted despite
broad mRNA (the basis of its clinical traction). **Fix:** the paper now states the mRNA-protein discordance
and bases the B7-H3 caution on the *selectivity* statistic (ns) and the mRNA-protein caveat, not a claim of
tumour-restricted protein.

**D9 (MED) — fusion-exclusivity loss under-weighed; no EMC-specific antigen rationale.** **Fix:** stated
plainly that these are lineage/generic antigens with no EWSR1::NR4A3 linkage, and weighed the loss of the ASO's
fusion-exclusivity as a first-order cost of the surface axis.

**D10 (MED) — false decimal precision in the ranking.** **Fix:** results presented as coarse tiers, with the
surface-protein-density requirement foregrounded.

**D13 (MED/LOW) — the data request reads as presumptuous.** **Fix:** the outreach and §6 reframed as a genuine
collaboration (we run their data, contribute analysis, defer authorship norms to them); dropped "the models
are the missing half".

**D14/D16 (LOW) — FAP window / FGFR1 dependency overstated.** **Fix:** FAP normal-fibroblast expression + FAPI
toxicity noted (and FAP is ns-selective here anyway); the FGFR1 "adjunct" suggestion removed absent an EMC
FGFR-dependency rationale, and its signal noted to rest on the single EMC line.

## Round 2 (on the revised paper) — findings + resolutions
A fresh adversarial pass on the rewrite confirmed the core content is internally consistent with the committed
data and that round-1 fixes landed, and raised: **(blocking)** the window table listed MCAM as BROAD while the
stated rule implied RESTRICTED — resolved by stating the *"detected in all" distribution* override and the
blood *enriched*-vs-*enhanced* threshold in §2.3 (MCAM is "group enriched" but detected in all tissues); and
the surfaceome counts didn't sum — resolved by stating the union explicitly (2,820 ∪ 47 seed, 41 overlapping,
= 2,826). **(medium, soft-promotion of SSTR2/GD2)** the abstract said "documented" neuroendocrine (softened to
"reported, pending citation"); SSTR2/GD2 were framed as "forward leads" and "dosimetry is the gate" — both
reworded to gate explicitly on *unmeasured EMC expression* so the honest "no clean target" thesis is not
undercut; APP was double-used as ubiquitous and neural (dropped from the neural list); CD59/LAMP1 were cited as
top-list examples but absent from Table 1 (replaced with ALCAM); the abstract's B7-H3 figure was the
uncorrected p=0.98 (changed to BH q=1.0 for consistency). **(minor)** selectivity-table ordering; H-EMC-SS
"real EMC" vs "[to verify]" tone reconciled (noted ECACC-catalogued). All applied.

## Net
The two passes plus the H-EMC-SS discovery turned an over-optimistic "top surface targets for EMC" draft into
an honest, self-critical analysis whose main results are: (1) one real EMC line's surface profile (n=1);
(2) a rigorously-tested selectivity ranking in which **B7-H3 is not selective**; (3) a hard normal-tissue
window under which **most candidates are liabilities**, so the analysis mainly refines priorities and flags
dangers rather than declaring winners; and (4) a grounded SSTR2/DOTATATE neuroendocrine hypothesis the first
draft missed. The decisive validation remains the patient-derived EMC lines' surface data.
