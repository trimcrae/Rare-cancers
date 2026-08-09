#!/usr/bin/env python3
"""Grade the modality-census routes whose selecting feature is READABLE in data already on disk. ($0, stdlib)

⭐ WHY THIS EXISTS. The 2026-08-09 modality census registered 24 new routes, each carrying a "cheapest
next observation". For six of them that observation turned out not to need running at all: the genes
were already read and committed in `emc-expression-panels.json`, and nobody had ever graded them
AGAINST THESE ROUTES because the routes did not exist when the panel was built. This module closes
that gap and does nothing else -- it reads one committed artifact and emits a verdict per route.

⛔ IT COMPUTES NOTHING NEW. Every number it reports is lifted from the panel artifact, which owns it.
That is deliberate: re-deriving a z-score here would create a second home for a figure the panel
already owns (rule 1), and the whole finding of this pass is that the reading existed and the GRADE
did not.

⚠ WHAT A TRANSCRIPT READ CANNOT DO, stated once and inherited by every verdict below. These are two
small archival array series (6 EMC vs 29 comparator sarcomas on GPL6244; 10 vs 6 on GPL3290). A
transcript level is not a protein level, is not an activity, and is not a copy number. Every verdict
here is a reason to prioritise or de-prioritise a route, never a statement about what any agent does
in a patient. Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "emc-expression-panels.json")
OUT = os.path.join(HERE, "census-route-expression-grading.json")

GPL6244 = "GSE24369_series_matrix.txt.gz"
GPL3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATFORMS = {GPL6244: "GPL6244 (6 EMC vs 29 comparator sarcomas)",
             GPL3290: "GPL3290 (10 EMC vs 6 comparator)"}


def load():
    with open(PANEL, encoding="utf-8") as fh:
        return json.load(fh)


def gene(panel, symbol):
    """EMC-minus-comparator mean z per platform, plus EMC's own array percentile.

    Returns `readable: False` where no probe maps -- and that is NOT a statement that the gene is
    unexpressed, which is the panel artifact's own governing rule and the one most easily lost when
    a second module summarises it.
    """
    out = {}
    src = panel["gene_reads"].get(symbol)
    if src is None:
        return {p: {"readable": False, "why": "symbol absent from the panel's gene_reads"}
                for p in PLATFORMS}
    for p in PLATFORMS:
        v = src.get(p)
        if not v or not v.get("readable"):
            out[p] = {"readable": False,
                      "why": "no probe on this platform maps to the symbol; NOT a reading of absence"}
            continue
        out[p] = {"readable": True,
                  "emc_mean_z": v["EMC"]["mean_z"],
                  "emc_array_percentile": v["EMC"]["mean_array_percentile"],
                  "comparator_mean_z": v["comparator"]["mean_z"],
                  "delta_emc_minus_comparator": round(
                      v["EMC"]["mean_z"] - v["comparator"]["mean_z"], 4)}
    return out


def group(panel, panel_name, group_name):
    """A scored group verdict as the panel emitted it, verbatim."""
    g = panel["panels"][panel_name]["groups"][group_name]["per_platform"]
    return {p: {"verdict": g[p]["verdict"], "score": g[p].get("score")} for p in PLATFORMS if p in g}


def concordance(per_platform, key="delta_emc_minus_comparator"):
    """Do the two platforms agree on SIGN? The only cross-platform claim this data supports.

    ⚠ Magnitudes are not comparable across these two series -- different platforms, different
    comparator arms, different n. Sign agreement is a real observation; a pooled effect size would be
    an invented one.
    """
    signs = [v[key] > 0 for v in per_platform.values() if v.get("readable") and key in v]
    if len(signs) < 2:
        return "not_assessable_one_platform_or_fewer"
    return "concordant" if len(set(signs)) == 1 else "discordant"


def build():
    p = load()
    routes = {}

    # ─────────────────────────── RT-ARGININE ───────────────────────────
    ass1 = gene(p, "ASS1")
    routes["RT-ARGININE"] = {
        "selecting_feature": "ASS1 silencing — the biomarker arginine-deprivation agents are given on",
        "direction_the_route_needed": "ASS1 LOW in EMC",
        "genes": {"ASS1": ass1, "ASL": gene(p, "ASL"), "ARG2": gene(p, "ARG2")},
        "concordance_of_the_primary_gene": concordance(ass1),
        "observed": "ASS1 is HIGHER in EMC than in comparator sarcomas on BOTH platforms, and on "
                    "GPL6244 it sits at the 92nd percentile of that array's own probe distribution.",
        "verdict": "AGAINST — the selecting feature is absent at transcript level on both platforms.",
        "what_this_does_not_settle": "ASS1 loss in the arginine-deprivation literature is an IHC "
                                     "call, and a transcript is not a protein. This de-prioritises "
                                     "the route; it does not prove the class could not act.",
        "route_action": "down-grade: the premise as stated is not supported",
    }

    # ───────────────────────────── RT-RET ─────────────────────────────
    ret = gene(p, "RET")
    routes["RT-RET"] = {
        "selecting_feature": "RET expressed AND activated — the historical claim the lane rests on",
        "direction_the_route_needed": "RET present, with an engageable activation route",
        "genes": {g: gene(p, g) for g in ("RET", "GDNF", "GFRA1", "ARTN", "NRTN")},
        "concordance_of_the_primary_gene": concordance(ret),
        "panel_groups": {"gdnf_family_ligands": group(p, "ret_axis", "gdnf_family_ligands"),
                         "gfra_co_receptors": group(p, "ret_axis", "gfra_co_receptors")},
        "observed": "RET itself is HIGHER in EMC on both platforms — the lane's own premise holds at "
                    "the receptor. ⛔ But the module that ACTIVATES it does not: the GFRα "
                    "co-receptors are LOWER in EMC on both platforms and strongly so, and the "
                    "GDNF-family ligands are LOWER on both. Canonical RET signalling needs a ligand "
                    "and a GFRα co-receptor; EMC has the receptor and, relative to comparator "
                    "sarcomas, less of both of the things that switch it on.",
        "verdict": "SPLIT — receptor supported, ligand-dependent activation route weakened.",
        "what_this_does_not_settle": "Ligand-independent activation exists in tumours carrying a RET "
                                     "rearrangement, and none is reported in this disease either "
                                     "way. Co-receptor transcript in bulk tumour also cannot exclude "
                                     "a paracrine supply from stroma or nerve. This narrows the "
                                     "mechanism the lane should claim; it does not close it.",
        "route_action": "keep, with the co-receptor reading carried as a stated caveat",
    }

    # ────────────────────── RT-HYPOXIA-PRODRUG ──────────────────────
    routes["RT-HYPOXIA-PRODRUG"] = {
        "selecting_feature": "a hypoxic fraction large enough to activate a prodrug",
        "direction_the_route_needed": "hypoxia signature HIGH in EMC",
        "genes": {g: gene(p, g) for g in ("CA9", "SLC2A1", "VEGFA", "LDHA", "ADM")},
        "panel_groups": {"hypoxia_canonical_hif_targets_curated":
                         group(p, "hypoxia", "hypoxia_canonical_hif_targets_curated")},
        "observed": "A curated canonical HIF-target metagene scores HIGHER in EMC than in comparator "
                    "sarcomas on BOTH platforms, with 15/15 and 14/15 genes readable.",
        # ⛔ THIS VERDICT WAS WRONG AND IS CORRECTED IN PLACE. It read SUPPORTED, from the raw
        # contrast, because this module consulted the panel artifact and NOT emc-hypoxia-confounds.json,
        # which audits that exact read against a genome-wide size-matched null the signature fails on
        # GPL6244. An audit that reaches some consumers of a shared reading and not others is this
        # repository's most-repeated failure, and here the grader WAS the consumer it did not reach.
        "verdict": "⛔ WITHDRAWN — first graded SUPPORTED from the raw contrast; the confound audit "
                   "restricts the signature to one of the two platforms and the memo that owns it "
                   "declines to license this class from the signal at all.",
        "what_this_does_not_settle": "A hypoxia metagene is a transcriptional shadow of hypoxia, not "
                                     "an oxygen measurement, and 'higher than other sarcomas' is not "
                                     "'hypoxic enough to reduce a prodrug'. The class also carries a "
                                     "negative randomised soft-tissue-sarcoma record that any "
                                     "assessment must lead with. ⛔ AND THE DECISIVE OMISSION, which "
                                     "is why this row is withdrawn: emc-hypoxia-reading.md §5 owns "
                                     "the audit of this exact reading and rules that the signal is a "
                                     "reason to ask a question rather than to revisit this class.",
        "route_action": "withdrawn; the owning memo's ruling stands and this grader defers to it",
    }

    # ────────────────────── RT-MATRIX-SYNTHESIS ──────────────────────
    routes["RT-MATRIX-SYNTHESIS"] = {
        "selecting_feature": "the tumour actively manufacturing its sulfated chondroitin-sulfate matrix",
        "direction_the_route_needed": "CS biosynthetic and sulfation machinery HIGH in EMC",
        "genes": {g: gene(p, g) for g in ("CHST11", "CHST14", "PAPSS1", "PAPSS2", "XYLT1")},
        "panel_groups": {"paps_module": group(p, "cs_gag_paps", "paps_module"),
                         "cs_backbone_polymerisation":
                             group(p, "cs_gag_paps", "cs_backbone_polymerisation"),
                         "cs_sulfotransferases_4O":
                             group(p, "cs_gag_paps", "cs_sulfotransferases_4O")},
        "observed": "⛔ The sulfate-DONOR module is LOWER in EMC than in comparator sarcomas on BOTH "
                    "platforms, driven by PAPSS2. The backbone-polymerisation and 4-O-sulfotransferase "
                    "groups DISAGREE between platforms, so neither supports a call.",
        "verdict": "AGAINST AS STATED — the naive form of the premise, that a matrix-defining tumour "
                   "must be running its biosynthetic machinery hotter than its neighbours, is not "
                   "what the data shows.",
        "what_this_does_not_settle": "The comparator arm is itself matrix-rich sarcoma, so this is a "
                                     "relative statement and not an absolute one; and bulk transcript "
                                     "of a biosynthetic enzyme need not track accumulated matrix mass "
                                     "in a tumour whose product is long-lived. The route needs "
                                     "reformulating rather than deleting.",
        "route_action": "re-scope: the premise must be restated in a form this reading does not "
                        "already contradict",
    }

    # ─────────────────────── RT-IMMUNOCYTOKINE ───────────────────────
    fn1 = gene(p, "FN1")
    routes["RT-IMMUNOCYTOKINE"] = {
        "selecting_feature": "a matrix epitope present in EMC stroma and restricted enough to address",
        "direction_the_route_needed": "the epitope's parent genes present, ideally enriched",
        "genes": {"FN1": fn1, "TNC": gene(p, "TNC"), "FAP": gene(p, "FAP")},
        "observed": "The parent genes are abundantly expressed in ABSOLUTE terms — FN1 sits at the "
                    "94th percentile of its array on GPL6244 — but they are NOT enriched relative to "
                    "comparator sarcomas: FN1 is flat on one platform, and TNC and FAP are LOWER in "
                    "EMC on both.",
        "verdict": "PRESENT, NOT SELECTIVE — and the question that actually decides this route is "
                   "unreadable here.",
        "what_this_does_not_settle": "⛔ THE ADDRESS IS A SPLICE VARIANT, AND A GENE-LEVEL PROBE "
                                     "CANNOT SEE ONE. The clinical immunocytokines target an "
                                     "oncofetal fibronectin/tenascin isoform, not total FN1 or TNC, "
                                     "and its abundance is not deducible from the parent gene. So "
                                     "this reading bounds the parent genes and leaves the route's own "
                                     "premise untested.",
        "route_action": "keep; the isoform question is now the route's stated first requirement",
    }

    # ───────────────────────────── RT-NR2F1 ─────────────────────────────
    nr2f1 = gene(p, "NR2F1")
    routes["RT-NR2F1"] = {
        "selecting_feature": "expression of the dormancy receptor in EMC",
        "direction_the_route_needed": "the receptor readable and present",
        "genes": {"NR2F1": nr2f1},
        "panel_groups": {"dormancy_associated_context_curated":
                         group(p, "nr2f1_dormancy", "dormancy_associated_context_curated")},
        "observed": "NR2F1 is NOT READABLE on either platform — no probe maps to it. ⚠ That is an "
                    "instrument limit and not a reading of absence. Separately, a curated "
                    "dormancy-associated context set is HIGHER in EMC on BOTH platforms.",
        "verdict": "UNREAD — the route's precondition cannot be answered from these two series at all, "
                   "while the surrounding programme it belongs to is elevated on both.",
        "what_this_does_not_settle": "Everything about the receptor itself. An unreadable gene is the "
                                     "one case where this pass returns no information, and recording "
                                     "that as a negative would be the exact failure the source "
                                     "artifact's governing rule forbids.",
        "route_action": "keep; the next observation must come from a platform that carries the probe",
    }


    # ═══════════ reads 9–16, graded 2026-08-09 after the CI panel extension ═══════════
    # ⚠ EVERY ROW BELOW IS AN ABUNDANCE READING AND THE QUESTION IS USUALLY DEPENDENCY. A tumour can
    # be exquisitely dependent on a module it expresses at ordinary levels, so a flat read excludes
    # little and an elevated one establishes nothing on its own. What these are good for is RANKING
    # which hypothesis to spend the next observation on.
    routes["RT-MTAP-PRMT5"] = {
        "selecting_feature": "MTAP locus deletion — the copy state that selects the PRMT5/MAT2A axis",
        "direction_the_route_needed": "MTAP down, at the floor, with CDKN2A",
        "genes": {g: gene(p, g) for g in ("MTAP", "CDKN2A", "CDKN2B", "PRMT5", "MAT2A")},
        "panel_groups": {"the_locus": group(p, "mtap_prmt5", "the_locus"),
                         "prmt5_methylosome": group(p, "mtap_prmt5", "prmt5_methylosome"),
                         "methionine_salvage_context": group(p, "mtap_prmt5",
                                                             "methionine_salvage_context")},
        "observed": "⭐ The three-gene MTAP/CDKN2A/CDKN2B locus is LOWER in EMC on the platform where "
                    "it is powered, and not marginally. The PRMT5 methylosome is HIGHER in EMC on "
                    "BOTH platforms, and MAT2A sits at the 99th and 84th percentile of its array. "
                    "That is the shape an MTAP-deleted, methylosome-dependent state makes on an "
                    "expression platform.",
        "verdict": "SUPPORTED, WITH THE LOCUS READ POWERED ON ONE PLATFORM ONLY.",
        "what_this_does_not_settle": "⛔ A TRANSCRIPT IS NOT A COPY NUMBER, and this is the case where "
                                     "that matters most: the class is selected by homozygous deletion, "
                                     "which reads as a floor-level transcript but is not the same "
                                     "measurement. The locus group is UNDERPOWERED on GPL3290 (2 of 3 "
                                     "genes readable), so the strong result rests on six tumours on "
                                     "one array. And an elevated methylosome is not a dependency on it.",
        "route_action": "promote: the cheapest decisive next observation is a copy-number or "
                        "methylation read of the locus, not another expression series",
    }
    routes["RT-TXN-CDK"] = {
        "selecting_feature": "elevated transcriptional CDK machinery in a transactivating-fusion tumour",
        "direction_the_route_needed": "transcriptional CDK modules up",
        "genes": {g: gene(p, g) for g in ("CDK7", "CDK9", "CDK12", "CDK13", "MYC")},
        "panel_groups": {"cdk7_initiation_module": group(p, "transcriptional_cdk",
                                                         "cdk7_initiation_module"),
                         "cdk9_elongation_module": group(p, "transcriptional_cdk",
                                                         "cdk9_elongation_module"),
                         "transcriptional_output_context": group(p, "transcriptional_cdk",
                                                                 "transcriptional_output_context")},
        "observed": "The CDK7 initiation module is HIGHER in EMC on BOTH platforms, and so is the "
                    "general transcriptional-output group, both with the largest t-statistics in this "
                    "pass. The CDK9 elongation module is higher on both but weakly. MYC is up on both.",
        "verdict": "SUPPORTED — the most concordant elevation in the census, on both platforms.",
        "what_this_does_not_settle": "⛔ THIS IS THE ROW WHERE ABUNDANCE IS FURTHEST FROM THE QUESTION. "
                                     "Every cell transcribes; elevated transcriptional machinery in a "
                                     "transcriptionally driven tumour is close to a tautology, and it "
                                     "says nothing about a WINDOW against normal tissue, which is the "
                                     "whole objection to this class. A general-transcription elevation "
                                     "is also exactly what higher cellularity or proliferation would "
                                     "produce.",
        "route_action": "keep; the decisive observation is a dependency screen, not another abundance read",
    }
    routes["RT-CHAPERONE"] = {
        "selecting_feature": "a standing proteostatic load imposed by a chimeric protein",
        "direction_the_route_needed": "chaperone machine up",
        "genes": {g: gene(p, g) for g in ("HSP90AA1", "HSP90AB1", "CDC37", "HSPA8")},
        "panel_groups": {"hsp90_machine": group(p, "chaperone_dependency", "hsp90_machine"),
                         "co_chaperones": group(p, "chaperone_dependency", "co_chaperones"),
                         "hsp70_arm_and_stress_response": group(p, "chaperone_dependency",
                                                                "hsp70_arm_and_stress_response")},
        "observed": "The HSP90 machine is HIGHER in EMC on BOTH platforms and the co-chaperones follow "
                    "it. ⚠ The HSP70 arm and heat-shock response go the OTHER way on both, which is "
                    "not what a general stress response looks like.",
        "verdict": "PARTLY SUPPORTED — the HSP90 arm only, and the stress-response arm contradicts it.",
        "what_this_does_not_settle": "An elevated chaperone machine is not evidence that the fusion is "
                                     "its client, which is the route's actual premise and a "
                                     "co-immunoprecipitation question. The split between the HSP90 and "
                                     "HSP70 arms is interesting and unexplained, and this data cannot "
                                     "explain it.",
        "route_action": "keep; the premise needs a client experiment, not more abundance",
    }
    routes["RT-APOPTOSIS-DEP"] = {
        "selecting_feature": "an anti-apoptotic guardian other than BCL-2 holding the threshold",
        "direction_the_route_needed": "a non-BCL2 guardian dominant in EMC",
        "genes": {g: gene(p, g) for g in ("MCL1", "BCL2L1", "BCL2", "BAX", "PMAIP1")},
        "panel_groups": {"anti_apoptotic_the_druggable_ones":
                         group(p, "apoptotic_dependency", "anti_apoptotic_the_druggable_ones"),
                         "bh3_only_sensitisers": group(p, "apoptotic_dependency",
                                                       "bh3_only_sensitisers")},
        "observed": "⛔ All five druggable guardians together are LOWER in EMC than in comparator "
                    "sarcomas on BOTH platforms, MCL1 and BCL2L1 individually included. NOXA, the "
                    "BH3-only protein that specifically neutralises MCL-1, is UP on both.",
        "verdict": "AGAINST AT THE ABUNDANCE LEVEL — no guardian is dominant, and the one that is up "
                   "is a sensitiser rather than a guardian.",
        "what_this_does_not_settle": "⛔ AND HERE THE GAP IS THE WHOLE POINT: apoptotic dependency is "
                                     "which protein HOLDS the effectors, which BH3 profiling measures "
                                     "and abundance cannot. Low guardian transcript with high NOXA is "
                                     "compatible with a primed state, which would make the "
                                     "combination-only result that raised this hypothesis MORE "
                                     "interesting rather than less. This read de-prioritises the "
                                     "specific MCL-1 claim, not the underlying observation.",
        "route_action": "down-grade the MCL-1-dominance form; the priming reading survives and is "
                        "untestable from expression",
    }
    routes["RT-MDM2"] = {
        "selecting_feature": "an intact, transcriptionally live p53 axis",
        "direction_the_route_needed": "p53 target output present",
        "genes": {g: gene(p, g) for g in ("TP53", "MDM2", "MDM4", "CDKN1A", "ZMAT3")},
        "panel_groups": {"the_axis": group(p, "p53_mdm2_axis", "the_axis"),
                         "p53_transcriptional_output": group(p, "p53_mdm2_axis",
                                                             "p53_transcriptional_output")},
        "observed": "The p53 transcriptional output group is LOWER in EMC on BOTH platforms, and the "
                    "axis genes themselves are flat. The output the class needs to be live is not "
                    "elevated.",
        "verdict": "NOT SUPPORTED — the axis reads quiet rather than intact-and-live.",
        "what_this_does_not_settle": "A quiet p53 output is not the same as a defective axis: an "
                                     "unstressed tumour has little p53 output by construction, and "
                                     "these are archival resections rather than treated tissue. This "
                                     "cannot establish that TP53 is mutant, and it does not.",
        "route_action": "down-grade; the selection argument was the whole route and it is not supported",
    }
    routes["RT-EZH2"] = {
        "selecting_feature": "a PRC2 or SWI/SNF chromatin state of the kind that selects the approved agent",
        "direction_the_route_needed": "PRC2 up, or a SWI/SNF subunit at the floor",
        "genes": {g: gene(p, g) for g in ("EZH2", "EED", "SUZ12", "SMARCB1", "BRD9")},
        "observed": "EZH2 is mildly higher on both platforms and the rest of PRC2 is flat; no SWI/SNF "
                    "tumour-suppressor subunit reads anywhere near a floor.",
        "verdict": "NOT SUPPORTED — neither selecting shape is present.",
        "what_this_does_not_settle": "The approved agent is selected by protein LOSS, frequently "
                                     "post-transcriptional, so a normal transcript does not exclude "
                                     "it. This is a weak negative and is reported as one.",
        "route_action": "down-grade",
    }
    routes["RT-SGK1"] = {
        "selecting_feature": "SGK1 elevated, corroborating a two-decade-old antibody series",
        "direction_the_route_needed": "SGK1 up",
        "genes": {g: gene(p, g) for g in ("SGK1", "NDRG1", "SGK3")},
        "observed": "⚠ SGK1 itself is DISCORDANT — lower on one platform, higher on the other. Its "
                    "canonical substrate NDRG1 is higher on both, at the 98th percentile on one.",
        "verdict": "DISCORDANT ON THE KINASE, CONCORDANT ON ITS SUBSTRATE.",
        "what_this_does_not_settle": "NDRG1 is phosphorylated by several kinases, so a substrate "
                                     "elevation is not attributable to SGK1, and a discordant kinase "
                                     "read across two platforms is exactly the case where a third "
                                     "series decides and nothing else does.",
        "route_action": "keep at concept; the corroboration this route was registered for did not arrive",
    }
    routes["RT-POLQ"] = {
        "selecting_feature": "an alt-EJ-high, HR-low repair state",
        "direction_the_route_needed": "alt-EJ up WITH homologous recombination down",
        "genes": {g: gene(p, g) for g in ("POLQ", "LIG3", "RAD51", "BRCA1", "PRKDC")},
        "observed": "POLQ is flat and sits low on its array; the homologous-recombination genes are "
                    "flat to mildly higher rather than down. The combination the class needs — one up "
                    "AND the other down — is not present.",
        "verdict": "NOT SUPPORTED — neither half of the required combination.",
        "what_this_does_not_settle": "The dependency is created by a repair DEFECT, usually a mutation, "
                                     "which this read cannot see at all. It must also be read beside "
                                     "the WEAK grade the neighbouring ATR assessment already carries.",
        "route_action": "down-grade",
    }

    # ⭐ A FLAT, DOT-FREE BLOCK EXISTS PURELY SO THE PREPRINT'S FIGURES CAN BE PINNED. The consistency
    # linter addresses artifact values by a dot-separated path, and this panel's platform keys are
    # FILENAMES containing dots ("GSE24369_series_matrix.txt.gz"), so no path can reach them. Rather
    # than loosen the linter, the figures the paper actually quotes are re-exposed here under flat
    # names. ⛔ They are lifted from the panel and computed nowhere -- this is an index into the one
    # home, not a second one.
    # ⚠ ROUNDED TO THE INTEGER PERCENTILE, because that is the form the prose quotes ("the 99th
    # percentile"). A pin whose format does not match how the sentence is written cannot fire on a
    # real drift -- it fires on the formatting instead, and gets switched off.
    def pct(sym, plat):
        return round(gene(p, sym)[plat]["emc_array_percentile"] * 100)

    pin = {
        "mat2a_percentile_gpl6244": pct("MAT2A", GPL6244),
        "mat2a_percentile_gpl3290": pct("MAT2A", GPL3290),
        "prmt5_percentile_gpl6244": pct("PRMT5", GPL6244),
        "prmt5_percentile_gpl3290": pct("PRMT5", GPL3290),
    }

    return {
        "pinned_figures_quoted_by_the_preprint": pin,
        "_a_grader_must_read_the_audit_not_only_the_reading": (
            "⛔ ADDED AFTER THIS FILE GOT IT WRONG. emc-expression-panels.json holds READINGS; "
            "emc-hypoxia-confounds.json holds the AUDIT of one of them. Grading from the first "
            "without the second produced a SUPPORTED verdict on a signature its own genome-wide null "
            "restricts to one of the two platforms. An audit that reaches some consumers of a shared "
            "reading and not others is this repository's most-repeated failure, and here the grader "
            "WAS the consumer it did not reach. Any future grader over this panel must check whether "
            "a confound audit exists for the read it is using."),
        "_what": "Verdicts for the modality-census routes whose selecting feature was ALREADY readable "
                 "in emc-expression-panels.json. One reading per route, graded against the route's own "
                 "stated premise.",
        "_why": "The census registered these routes on 2026-08-09 with a 'cheapest next observation'. "
                "For six of them the observation was already committed and had never been graded "
                "against them, because the routes did not exist when the panel was built.",
        "_this_artifact_computes_nothing_new": "Every figure is lifted from emc-expression-panels.json, "
                                               "which owns it. Re-deriving one here would make a "
                                               "second home for it.",
        "_language_discipline": "Nothing here asserts efficacy, safety, a therapeutic window or "
                                "clinical readiness for any agent or class. A transcript level is not "
                                "a protein level, an activity or a copy number.",
        "_the_comparison_being_made": "EMC tumour tissue against comparator sarcomas on the same "
                                      "array, expressed as a mean z difference. Magnitudes are NOT "
                                      "comparable across the two platforms; only sign agreement is.",
        "source_artifact": "research/modalities/emc-expression-panels.json",
        "platforms": PLATFORMS,
        "routes": routes,
        "summary": {
            "supported": [k for k, v in routes.items() if v["verdict"].startswith("SUPPORTED")],
            "against": [k for k, v in routes.items() if v["verdict"].startswith("AGAINST")],
            "withdrawn": [k for k, v in routes.items() if v["verdict"].startswith("⛔ WITHDRAWN")],
            "split_or_unread": [k for k, v in routes.items()
                                if not v["verdict"].startswith(("SUPPORTED", "AGAINST",
                                                                "⛔ WITHDRAWN"))],
        },
    }


def main():
    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    for rid, r in doc["routes"].items():
        print(f"  {rid:<22} {r['verdict'][:78]}")


if __name__ == "__main__":
    main()
