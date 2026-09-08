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
DEPMAP = os.path.join(HERE, "depmap-sarcoma-dependency.json")
OUT = os.path.join(HERE, "census-route-expression-grading.json")

GPL6244 = "GSE24369_series_matrix.txt.gz"
GPL3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATFORMS = {GPL6244: "GPL6244 (6 EMC vs 29 comparator sarcomas)",
             GPL3290: "GPL3290 (10 EMC vs 6 comparator)"}


def load():
    with open(PANEL, encoding="utf-8") as fh:
        return json.load(fh)


def depmap():
    """The sarcoma-line dependency prior, keyed by gene.

    ⛔ IT CONTAINS NO EMC LINE. The one line on the curated record does not carry the fusion and has
    no CRISPR data, so every figure here is a TRANSFER from other sarcomas and inherits
    BLK-CLASS-INHERITANCE. The honest bound is not a small sample; it is no EMC observation at all.

    ⚠ AND A DEPENDENCY IS NOT A WINDOW. `frac_dependent` near 1.0 means the gene is required in
    almost every sarcoma line -- which is evidence AGAINST a therapeutic window, not for one, unless
    the class exploits a state the normal cell does not share.
    """
    with open(DEPMAP, encoding="utf-8") as fh:
        d = json.load(fh)
    out = {}
    for rows in d["genes_by_group"].values():
        for r in rows:
            out[r["gene"]] = {"sarcoma_mean_gene_effect": r.get("sarcoma_mean"),
                              "fraction_of_sarcoma_lines_dependent": r.get("sarcoma_frac_dependent")}
    return out


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
    dm = depmap()
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

    # ────────────────────────── RT-ALK-HIT ──────────────────────────
    # ⭐ THE ROUTE'S OWN FIRST STEP WAS "RE-READ THE COMMITTED SCREEN ARTIFACT FOR THE FULL HIT LIST",
    # and doing it changes what the lead is. The screen returned THREE hits, and TWO of them are the
    # same class as each other -- which is a within-screen class replication that the one-agent framing
    # ("an ALK/ROS1-class inhibitor was among the hits") could not show.
    routes["RT-ALK-HIT"] = {
        "selecting_feature": "whichever of the hit agent's targets EMC actually depends on",
        "direction_the_route_needed": "the agent's targets readable and high in EMC, with one "
                                      "separating from the others",
        "genes": {g: gene(p, g) for g in ("ALK", "ROS1", "EGFR", "HDAC1", "HDAC6", "HDAC9")},
        "panel_groups": {"brigatinib_targets":
                             group(p, "drug_screen_targets", "brigatinib_targets"),
                         "hdac_class_i_ii": group(p, "drug_screen_targets", "hdac_class_i_ii"),
                         "kinase_contrast": group(p, "drug_screen_targets", "kinase_contrast")},
        "observed": "⛔ THE EXPRESSION INSTRUMENT CANNOT ATTRIBUTE THIS HIT, AND THAT IS AN INSTRUMENT "
                    "STATEMENT AND NOT A NEGATIVE — BUT THE INSTRUMENT IS LESS BLIND THAN THIS BLOCK "
                    "SAID UNTIL 2026-08-29. ⛔ CORRECTED, AND THE OLD SENTENCE WAS CONTRADICTED BY "
                    "THE TABLE DIRECTLY ABOVE IT IN THIS SAME FILE: it read 'Both kinases the lead "
                    "names are NOT READABLE on EITHER platform — ALK and ROS1 have no probe on "
                    "GPL6244 or GPL3290'. The panel artifact that OWNS these reads says ALK is "
                    "readable on GPL6244 (one probe) and not on GPL3290, and ROS1 is readable on "
                    "BOTH. The brigatinib target group therefore reaches full coverage on GPL6244 "
                    "(3/3) and DOES emit a score there — LOWER in EMC than in comparator sarcomas; "
                    "it emits none on GPL3290 ONLY, where the single missing ALK probe takes "
                    "coverage to 2/3, below the panel's 3-gene floor. ⚠ The correction enlarges the "
                    "evidence base and improves nothing: on the platform where ALK is readable it "
                    "sits BELOW the array median in EMC and level with the comparators, so the route "
                    "moves from 'we cannot see it' to 'we can see it on one platform and it is "
                    "unremarkable there'. ⭐ The cause was that the sentence was hand-typed prose in "
                    "this module rather than derived from the per-gene reads it summarises, so "
                    "nothing could catch it drifting from them; it had already propagated by copy "
                    "into systems/graph/routes.json's grade and into the generated route view. "
                    "The HDAC group is underpowered, three of eight readable on each. "
                    "The other named target, EGFR, is LOWER in EMC on both "
                    "platforms. The generic kinase contrast is higher on both, which is exactly why it "
                    "was included: a kinase group reading up here is not specific to anything. "
                    "⭐ WHAT THE RE-READ DID SETTLE IS THE HIT LIST ITSELF. The screen's three "
                    "low-IC50 agents are brigatinib, panobinostat and romidepsin, and the repository's "
                    "own curated target records make the last two near-identical pan-HDAC agents. TWO "
                    "OF THREE HITS ARE ONE CLASS. ⚠ And that class is already ON the board and closed "
                    "on SELECTIVITY rather than on activity, so this replicates a known signal instead "
                    "of opening a new route. ⚠ The curated record for the third agent names ALK and "
                    "EGFR and does NOT name ROS1, although the lead that raised this route calls it "
                    "the ALK/ROS1 class.",
        "verdict": "UNATTRIBUTABLE BY EXPRESSION — and the re-read demotes the lead rather than "
                   "grading it, because the screen's dominant signal belongs to a class the board "
                   "already holds.",
        "what_this_does_not_settle": "⛔ ABUNDANCE NEVER ATTRIBUTES A SCREEN HIT EVEN WHERE THE READ "
                                     "SUCCEEDS. An IC50 reflects whichever target that line depends "
                                     "on, and a target at the array floor can be the one that matters. "
                                     "So this reading could only ever have ruled a target out — and "
                                     "on GPL6244, where all three named targets ARE readable, it did "
                                     "not rule any of them out either: the group's verdict there is a "
                                     "reason to de-prioritise, not a target-level exclusion, and it "
                                     "is a GROUP mean that no single target owns. ⚠ One "
                                     "cell line, monolayer, one library's concentrations; nothing here "
                                     "asserts activity, selectivity, safety, a therapeutic window or "
                                     "clinical readiness for any of the three agents in this disease.",
        "route_action": "demote and fold into the kinase paper as a corrected reading of a lead — the "
                        "attribution needs the model, not the arrays, and the screen's own weight sits "
                        "with a class the board has already assessed",
    }

    # ──────────────────────── RT-MATRIX-ADDRESS ────────────────────────
    # The route that reads the SAME panel as RT-MATRIX-SYNTHESIS and asks a different question of it:
    # not "is the tumour manufacturing its matrix" but "could it be making the oncofetal sulfation
    # pattern that a glycan-directed agent addresses". Its own `next.best_next_action` named this read
    # as its cheapest next observation, so grading it here is that step and not a new one.
    routes["RT-MATRIX-ADDRESS"] = {
        "selecting_feature": "the placental-type oncofetal chondroitin-sulfate pattern on EMC tissue",
        "direction_the_route_needed": "the 4-O-sulfotransferase arm that writes the pattern, and the "
                                      "sulfate-donor module that supplies every sulfation, HIGH in EMC",
        "genes": {g: gene(p, g) for g in ("CHST11", "CHST12", "CHST13", "CHST14")},
        "panel_groups": {"cs_sulfotransferases_4O":
                             group(p, "cs_gag_paps", "cs_sulfotransferases_4O"),
                         "paps_module": group(p, "cs_gag_paps", "paps_module"),
                         "cs_proteoglycan_core_proteins":
                             group(p, "cs_gag_paps", "cs_proteoglycan_core_proteins")},
        "observed": "⛔ NO SUPPORT ON EITHER HALF OF THE CAPACITY ARGUMENT. The 4-O arm — all four "
                    "genes readable on both platforms, so this is a taken reading and not a missing "
                    "one — is DISCORDANT: lower in EMC on one platform, higher on the other, and "
                    "significant on neither. The sulfate-DONOR module is LOWER in EMC on BOTH "
                    "platforms and is the only concordant signal in the panel, which is the same "
                    "observation that graded RT-MATRIX-SYNTHESIS against its premise. The core "
                    "proteins that would carry the chains are mildly higher on both and significant "
                    "on neither.",
        "verdict": "NOT SUPPORTED ON CAPACITY — AND THE ROUTE'S OWN QUESTION IS STILL UNREADABLE. "
                   "This grades the proxy the route nominated, not the route's premise.",
        "what_this_does_not_settle": "⛔ A SULFATION PATTERN HAS NO GENE, which is the panel's own "
                                     "standing caveat and is what makes this route's evidence "
                                     "asymmetric. Sulfotransferase transcript is a proxy for the "
                                     "CAPACITY to write a pattern and can never be a measurement of "
                                     "the pattern; an epitope written by a low-abundance enzyme on a "
                                     "long-lived glycan is entirely compatible with this reading. So "
                                     "an unfavourable capacity read WEAKENS the route and cannot "
                                     "close it — exactly the shape of RT-IMMUNOCYTOKINE, where the "
                                     "address is a splice variant a gene-level probe cannot see. "
                                     "⚠ It also says nothing about whether any glycan-directed agent "
                                     "binds, works or is safe in this disease.",
        "route_action": "keep, demoted: the $0 observation the route named has now been taken and "
                        "returns no support, so a stain is the only remaining instrument and the "
                        "route's readiness must stop claiming an unrun lookup",
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
        "sarcoma_dependency_prior": {g: dm.get(g) for g in ("PRMT5", "MAT2A", "MTAP")},
        "what_the_dependency_prior_adds_and_takes_away": (
            "⚠ IT TAKES SOMETHING AWAY AND THE PAPER MUST CARRY IT. Across the 91 screened sarcoma lines (of 176 sarcoma models) PRMT5 "
            "and MAT2A are dependencies in 94.5% and 96.7% -- close to pan-essential. That does NOT "
            "refute the hypothesis, because the therapeutic argument for this class is a "
            "DIFFERENTIAL between MTAP-deleted and MTAP-intact cells that a gene-effect score cannot "
            "express: an MTA-cooperative inhibitor exploits a metabolic state, not the raw "
            "dependency. But it does weaken any argument that resting on 'silencing PRMT5 impairs "
            "proliferation' is specific to a fusion sarcoma -- silencing it impairs proliferation "
            "nearly everywhere. MTAP itself is not a dependency (mean -0.075), exactly as expected "
            "for a biomarker rather than a target."),
        "route_action": "promote, with the near-pan-essentiality of the target carried as a stated "
                        "limit: the cheapest decisive next observation is a copy-number or "
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
        "sarcoma_dependency_prior": {g: dm.get(g) for g in ("CDK7", "CDK9", "CDK12", "CDK13")},
        "the_dependency_screen_ran_and_it_closed_the_window": (
            "⛔ THE DECISIVE OBSERVATION THIS ROW ASKED FOR ARRIVED THE SAME DAY, AND IT WENT "
            "AGAINST THE ROUTE. Across the 91 screened sarcoma lines (of 176 sarcoma models) CDK7 and CDK9 are dependencies in 100% of "
            "them, with mean gene effects of -1.85 and -1.46. That is the definition of pan-"
            "essential: the elevation seen in EMC buys no window, because every line needs these "
            "genes. The abundance result stands and is now known to be uninformative about the "
            "question, which is what this row warned it would be."),
        "route_action": "down-grade: supported on abundance, closed on the axis that matters",
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
        "sarcoma_dependency_prior": {g: dm.get(g) for g in ("MCL1", "BCL2L1", "BCL2")},
        "the_dependency_prior_says_the_opposite_of_the_abundance_read": (
            "⭐ THE MOST INFORMATIVE SINGLE RESULT OF THIS PASS, AND IT ARRIVED AFTER THE VERDICT "
            "ABOVE WAS WRITTEN. Across the 91 screened sarcoma lines (of 176 sarcoma models), MCL1 and BCL2L1 are dependencies in 83.5% "
            "and 75.8% of them -- and BCL2 in 2.2%. So in this tumour class the guardian holding the "
            "effectors is not BCL-2, which is precisely what the route hypothesised and precisely "
            "what would explain an EMC result where BCL-2 inhibition was inactive alone. The "
            "abundance read and the dependency prior disagree, and dependency is the axis the "
            "question is actually about. ⛔ NO EMC LINE IS IN THIS PANEL, so this is a class "
            "transfer and not an EMC finding."),
        "route_action": "the MCL-1-dominance form is AGAINST on abundance and FOR on the sarcoma "
                        "dependency prior; the two disagree and dependency is the relevant axis, so "
                        "the route is restored to open rather than down-graded",
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
        # ⚠ THE CONCLUSION WAS ALWAYS RIGHT AND THE REASON WAS NOT (corrected 2026-08-29,
        # AUT-PD-099; evidence research/literature/ndrg1-kinase-attribution-2026-08-28.json).
        # Superseded, retained: "NDRG1 is phosphorylated by several kinases, so a substrate
        # elevation is not attributable to SGK1". Kinase multiplicity is the reason a PHOSPHO
        # reading cannot be apportioned; this row reads TRANSCRIPT ABUNDANCE, which contains no
        # phosphorylation to apportion, so the old reason cited a division that is not in the
        # data. "Not attributable to SGK1" stands and is now carried by the type mismatch.
        "what_this_does_not_settle": "A transcript level is an ABUNDANCE measurement, and every "
                                     "published mechanism connecting SGK1 to NDRG1 is a "
                                     "PHOSPHORYLATION of NDRG1 protein — so this substrate "
                                     "elevation is not attributable to SGK1, and the "
                                     "kinase-multiplicity question does not apply to it, there "
                                     "being no phosphorylation in the reading to divide. A "
                                     "discordant kinase read across two platforms is exactly the "
                                     "case where a third series decides and nothing else does.",
        "route_action": "keep at concept; the corroboration this route was registered for did not arrive",
    }
    routes["RT-POLQ"] = {
        "selecting_feature": "an alt-EJ-high, HR-low repair state",
        "direction_the_route_needed": "alt-EJ up WITH homologous recombination down",
        "genes": {g: gene(p, g) for g in ("POLQ", "LIG3", "PARP1", "XRCC1", "RAD51", "BRCA1",
                                          "PRKDC")},
        "panel_groups": {"alt_ej_module": group(p, "ddr_mmej", "alt_ej_module"),
                         "homologous_recombination":
                             group(p, "ddr_mmej", "homologous_recombination"),
                         "nhej_contrast": group(p, "ddr_mmej", "nhej_contrast")},
        "observed": "⚠ ONE HALF IS PRESENT AND THE OTHER IS NOT — which is not what this grade first "
                    "said. The alt-EJ MODULE is HIGHER in EMC on BOTH platforms and concordantly so, "
                    "and every readable member of it is higher on both. ⛔ The homologous-recombination "
                    "arm is flat to mildly HIGHER rather than down, so the combination the class needs "
                    "— alt-EJ up WITH HR down — is not present. The NHEJ contrast is flat on both, "
                    "so the elevation is specific AGAINST NHEJ. ⚠ It is not shown to be specific "
                    "more broadly, and on GPL3290 it is not shown to be specific at all: the "
                    "homologous-recombination module rises MORE there than the alt-EJ module "
                    "(+0.2658 against +0.2578 SD), so the two move together on that platform and "
                    "only GPL6244 separates them (+0.087 against -0.0438). ⚠ Three of the "
                    "module's four members are single-strand-break and base-excision-repair "
                    "factors (LIG3, PARP1, XRCC1), and no contrast against that pathway was read. "
                    "⚠ The route's own primary gene is a weaker reading "
                    "than its module: it is readable on only ONE platform, is barely higher there, and "
                    "sits in the bottom quarter of that array's distribution — so the module carries "
                    "this observation and the single gene does not.",
        "verdict": "NOT SUPPORTED — the required COMBINATION is absent, because the "
                   "homologous-recombination half is not there. ⚠ Not because neither half is: the "
                   "alt-EJ half is present on both platforms.",
        "what_this_does_not_settle": "⛔ THE DEPENDENCY IS CREATED BY A REPAIR DEFECT, USUALLY A "
                                     "MUTATION, which this read cannot see at all — so the half that "
                                     "came back negative is the half this instrument is least able to "
                                     "measure, and an HR defect can be present with normal HR "
                                     "transcript. That makes this a weaker negative than the group "
                                     "scores alone suggest. It must also be read beside the WEAK grade "
                                     "the neighbouring ATR assessment already carries, since both rest "
                                     "on the same unproven replication-stress premise.",
        "route_action": "down-grade, but record the alt-EJ elevation rather than burying it — it is "
                        "the one half of this class's requirement that EMC does appear to meet",
        "⚠_correction_2026_08_09": "This grade first read 'POLQ is flat and sits low on its array' and "
                                   "concluded 'neither half of the required combination', and the "
                                   "route and census row inherited that. The alt-EJ MODULE is up on "
                                   "both platforms with every readable member higher on both; only the "
                                   "single primary gene is flat. The VERDICT is unchanged — the "
                                   "combination is still absent — but the reason given was wrong, and "
                                   "it was found by reading the panel again while drafting the paper "
                                   "that would have quoted it.",
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

    def gt(panel_name, group_name, plat):
        """A group's Welch t as the panel scored it. Same dot-free re-exposure, same reason."""
        return p["panels"][panel_name]["groups"][group_name]["per_platform"][plat]["score"]["t"]

    pin = {
        "mat2a_percentile_gpl6244": pct("MAT2A", GPL6244),
        "mat2a_percentile_gpl3290": pct("MAT2A", GPL3290),
        "prmt5_percentile_gpl6244": pct("PRMT5", GPL6244),
        "prmt5_percentile_gpl3290": pct("PRMT5", GPL3290),
        # ⭐ Added 2026-09-02 for research/manuscripts/dependency/emc-biomarker-selected-classes.md,
        # which quoted ten machine-written figures with no drift guard on any of them while its
        # sibling PRMT5 preprint was guarded above. Blind round on 20d33f347, finding S4.
        # ⚠ Two-platform pairs are pinned SEPARATELY: the linter passes a line if ANY number on it
        # matches, so pinning one member of a pair leaves the other free to drift on the same line.
        "biomarker_ass1_percentile_gpl6244": pct("ASS1", GPL6244),
        "biomarker_noxa_delta_gpl3290": gene(p, "PMAIP1")[GPL3290]["delta_emc_minus_comparator"],
        "biomarker_p53_output_t_gpl6244": gt("p53_mdm2_axis", "p53_transcriptional_output", GPL6244),
        "biomarker_p53_output_t_gpl3290": gt("p53_mdm2_axis", "p53_transcriptional_output", GPL3290),
        "biomarker_prc2_core_t_gpl6244": gt("chromatin_prc2_baf", "prc2_core", GPL6244),
        "biomarker_prc2_core_t_gpl3290": gt("chromatin_prc2_baf", "prc2_core", GPL3290),
        "biomarker_guardians_t_gpl6244": gt("apoptotic_dependency",
                                            "anti_apoptotic_the_druggable_ones", GPL6244),
        "biomarker_guardians_t_gpl3290": gt("apoptotic_dependency",
                                            "anti_apoptotic_the_druggable_ones", GPL3290),
        "biomarker_alt_ej_t_gpl6244": gt("ddr_mmej", "alt_ej_module", GPL6244),
        "biomarker_alt_ej_t_gpl3290": gt("ddr_mmej", "alt_ej_module", GPL3290),
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
