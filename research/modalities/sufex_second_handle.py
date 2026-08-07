#!/usr/bin/env python3
"""Y419 AS A SECOND COVALENT HANDLE — the ruling on which ruler is reported, the residues explicitly
dropped, the literature state of SuFEx tyrosine chemistry, and the chemoselectivity consequence it drags in.

WHY THIS FILE EXISTS
--------------------
[`path-family-synthesis.md`](../manuscripts/path-family-synthesis.md) §2 Tier-1 row 6 records a finding and
then a MANDATE, and only the finding had landed. The finding: sweeping 11 reactive classes instead of the
committed two finds paralogue-unique, alignment-robust LBD positions well beyond C397, and one of them —
**Y419**, a tyrosine addressable by SuFEx chemistry, one residue from C420 — ranks ABOVE NR4A1 Cys551, the
NR4A family's one literature-anchored covalent site, on the accessibility observable. The mandate:

    "Take the threshold-free rank as the roadmap mandates and stop quoting both rulers as equals."

Everywhere the finding is written down today, BOTH rulers are quoted as equals and the reader is told
*"neither reading is chosen here"* — `selectivity-mechanism-options.md` M2, and roadmap §8 Route B. That is
not a neutral presentation. `V17`'s exposure cutoff is **KNOWN-DEFECTIVE** by the roadmap's own instrument
table: it FAILS its own positive control (NR4A1 Cys551, RSA 0.165 against a 0.25 cutoff, 0 of 25 frames), and
the roadmap's ruling is that what survives is a threshold-free **RANK**. Reporting a discredited criterion
beside the ruler that replaced it, as co-equal readings, lets a reader pick the discredited one.

WHAT THIS FILE DOES
-------------------
  1. RULES on the ruler, in one place, so the mandate has a home:  `the_reported_ruler`.
  2. DROPS M398/M399 by name and by number rather than silently: `explicitly_dropped`.
  3. RECORDS the literature state of SuFEx tyrosine-targeting chemistry with an explicit VERIFICATION
     LEVEL per citation — because the row's own falsifier is that "chemistry credibility is a literature
     label, not a computed quantity":  `literature_record`.
  4. MEASURES the thing the falsifier's second clause asserts — that "every added handle re-opens the
     chemoselectivity-window question `S1` already answers uncomfortably". `S1`'s window is computed over
     CYSTEINES ONLY. A SuFEx warhead does not see a cysteine-only competitor set. This file counts the
     competitor population a SuFEx warhead actually faces, on the same committed models, and reports it
     beside the cysteine population the existing window was computed over:  `sufex_competitor_census`.
  5. EMITS the roadmap edits this requires — DESCRIBED, NEVER APPLIED (`map_edits_required`), anchors
     resolved against the live map at generation time by `map_edits.py`.

⛔ SCOPE AND WHAT THIS IS NOT
----------------------------
$0 — pure-stdlib CPU over committed structures and committed artifacts. No GPU, no rental.

This is a **REAGENT-LEVEL** statement and nothing more. It says a residue is unique to NR4A3 among its two
paralogues, is within linker reach on one static opened conformer, and belongs to a residue class for which
published covalent chemistry exists. It says NOTHING about whether an adduct forms, about binding affinity,
degradation, efficacy, a therapeutic window, safety, clinical readiness, or selectivity beyond the
two-paralogue comparison set. No phenol pKa, nucleophilicity, adduct stability or electrophile promiscuity is
modelled anywhere in this repository.

★ ONE FACT, ONE PLACE (CLAUDE.md rule 1). Y419's RSA, its rank, the reference site's RSA, the class counts
and M398/M399's values are CITATIONS out of
[`selectivity-mechanism-options.json`](selectivity-mechanism-options.json) → `measurements.M2`, which owns
them; each carries `_from`. The competitor census in §4 is a NEW fact and this file is its one home.

Usage
    python3 research/modalities/sufex_second_handle.py            # write the JSON
    python3 research/modalities/sufex_second_handle.py --check    # regenerate and diff, exit 1 on drift
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

STRUCT = os.path.join(REPO, "results", "nr4a3-matrix")
SELMECH = os.path.join(HERE, "selectivity-mechanism-options.json")
REACH = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")
OUT = os.path.join(HERE, "sufex-second-handle.json")

# ⛔ NOT EDITED BY THIS FILE. Roadmap edits are DESCRIBED in `map_edits_required` and applied by a human.
LOCKED = ("research/manuscripts/nr4a3-program-map.md", "research/manuscripts/path-family-synthesis.md",
          "STRATEGY.md", "CLAUDE.md", "systems/graph/", "systems/views/")

# The residue classes a SuFEx warhead is documented to label, with the reactive atom used for the distance.
# ⚠ THIS SET IS THE POINT OF §4. It is NOT this file's opinion: it is read off the literature record below
# (`literature_record`), where each entry names which residues that source reports. Cys is listed separately
# because the EXISTING window was computed over cysteines alone.
SUFEX_REACTIVE_ATOM = {"TYR": "OH", "LYS": "NZ", "HIS": "NE2", "SER": "OG", "THR": "OG1"}
CYS_REACTIVE_ATOM = {"CYS": "SG"}

# The cryptic-pocket definition, in NR4A3 UniProt numbering. CITATION, not a second home:
# nr4a_paralogue_unique_residues.CRYPTIC_POCKET_UNIPROT. Imported rather than typed at runtime; the literal
# is here only so a reader can see it, and `_assert_pocket_matches_owner` fails the run if they diverge.
CRYPTIC_POCKET_UNIPROT_MIRROR = (406, 407, 410, 411, 412, 481, 484, 485, 531, 534)

# The paralogue superposition's own reliability bar. `superpose_paralogue` returns a per-residue post-fit
# deviation; a residue far outside the structured core has an UNRELIABLE position in the NR4A3 frame, so its
# distance is reported but excluded from the headline count. 2.0 A is the function's own floor for the
# outlier cut (`cut = max(2.0, 2.0 * core_rmsd)`), used here for the same reason.
CORE_DEVIATION_MAX_A = 2.0


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _et(utc: dt.datetime) -> str:
    """CLAUDE.md rule 1: US Eastern, 12-hour, never UTC and never 24-hour. EDT = UTC-4."""
    e = utc - dt.timedelta(hours=4)
    s = e.strftime("%Y-%m-%d %I:%M %p ET")
    return s.replace(" 0", " ", 1) if e.strftime("%I").startswith("0") else s


def _r(x, n=3):
    return None if x is None else round(x, n)


# ==========================================================================================================
# (1) THE RULING — one ruler is reported, the other is registered as superseded
# ==========================================================================================================
def the_reported_ruler(m2):
    """The mandate from path-family-synthesis §2 row 6, executed. PURE — reads M2, decides nothing new
    about the numbers, and states which of the two readings is THE reading."""
    rank_block = m2["read_against_the_V17_positive_control_instead_of_the_cutoff"]
    ranked = rank_block["rank_of_every_tetherable_unique_handle_by_rsa"]
    order = [s.split("=")[0] for s in ranked]
    ref_rsa = rank_block["reference_rsa"]

    def rsa_of(label):
        for s in ranked:
            if s.split("=")[0] == label:
                return float(s.split("=")[1])
        return None

    y_rsa = rsa_of("Y419")
    return {
        "_mandate": ("path-family-synthesis.md §2 Tier-1 row 6: 'Take the threshold-free rank as the roadmap "
                     "mandates and stop quoting both rulers as equals.'"),
        "THE_RULER": "the threshold-free RANK against NR4A1 Cys551",
        "_why_this_one": (
            "Not a preference. The roadmap's instrument table marks the alternative KNOWN-DEFECTIVE: `V17`'s "
            "EXPOSED_RSA = 0.25 cutoff FAILS its own positive control — NR4A1 Cys551, the NR4A family's one "
            "covalent site with literature support, reads RSA 0.165 on the state-matched opened model and 0 "
            "of 25 metadynamics frames — and the roadmap's own ruling is that what survives is a "
            "threshold-free RANK. A criterion with a demonstrated false negative on the only positive "
            "control the family has cannot be reported as co-equal with the ruler that replaced it."),
        "_what_changes_in_practice": (
            "Nothing about the numbers; everything about the sentence. Both readings stay computed and both "
            "stay in the artifact. What ends is the framing 'both readings are given, neither is chosen "
            "here' — the rank reading is THE reading, and the cutoff reading is carried as a SUPERSEDED "
            "cross-check, named as such, so it stays quotable as history and not as an alternative."),
        "reference_site": rank_block["reference_site"],
        "reference_rsa": ref_rsa,
        "_from_reference": "selectivity-mechanism-options.json -> measurements.M2."
                           "read_against_the_V17_positive_control_instead_of_the_cutoff.reference_rsa",
        "Y419": {
            "rsa": y_rsa,
            "rank_among_tetherable_unique_handles": (order.index("Y419") + 1) if "Y419" in order else None,
            "n_tetherable_unique_handles_ranked": len(order),
            "clears_the_reference": (y_rsa is not None and ref_rsa is not None and y_rsa >= ref_rsa),
            "margin_over_reference_rsa": _r((y_rsa - ref_rsa) if (y_rsa and ref_rsa) else None),
            "clears_the_V17_cutoff": False,
            "_from": "selectivity-mechanism-options.json -> measurements.M2 (rank list + lbd_unique_handles)",
        },
        "under_the_superseded_cutoff": {
            "chemically_credible_set": m2["chemically_credible_handles_under_the_V17_cutoff"],
            "_reading": ("NO new handle clears the cutoff at all — the set collapses to exactly the "
                         "cysteines and lysines already committed. This is retained as a SUPERSEDED "
                         "cross-check, not as a co-equal reading. Registering it is the point: a sweep that "
                         "reports only what survives is a sweep nobody can grade."),
            "_from": "selectivity-mechanism-options.json -> measurements.M2."
                     "chemically_credible_handles_under_the_V17_cutoff",
        },
        "NEW_handles_the_ruling_admits": rank_block["NEW_handles_this_reading_admits_that_the_cutoff_does_not"],
    }


# ==========================================================================================================
# (2) WHAT IS DROPPED — by name and by number
# ==========================================================================================================
def explicitly_dropped(m2):
    """M398/M399 named, valued and refused. A sweep that reports only survivors cannot be graded."""
    rank_block = m2["read_against_the_V17_positive_control_instead_of_the_cutoff"]
    ranked = rank_block["rank_of_every_tetherable_unique_handle_by_rsa"]
    order = [s.split("=")[0] for s in ranked]
    ref = rank_block["reference_rsa"]
    by_label = {h["class"] + str(h["uniprot"]): h for h in m2["lbd_unique_handles"]}
    out = []
    for lab in ("M398", "M399"):
        h = by_label.get(lab)
        if not h:
            out.append({"label": lab, "status": "NOT_IN_ARTIFACT",
                        "⚠": "This handle is not in the committed M2 handle list — the drop cannot be "
                             "targeted and this entry is a visible refusal, not a silent omission."})
            continue
        out.append({
            "label": lab, "class": h["class"], "residue_class": "Met thioether",
            "chemistry": "oxaziridine (redox-activated)", "chemistry_credibility_label": h["chemistry_credibility"],
            "rsa": h["rsa"], "reference_rsa": ref,
            "rank_among_tetherable_unique_handles": (order.index(lab) + 1) if lab in order else None,
            "n_tetherable_unique_handles_ranked": len(order),
            "clears_the_reference": h["rsa"] >= ref,
            "clears_the_V17_cutoff": bool(h["exposed_by_V17_cutoff"]),
            "reach_class": h["reach_class"], "dist_to_cryptic_pocket_A": h["dist_to_cryptic_pocket_A"],
            "VERDICT": "DROPPED — below the reference site on the ruler that binds, and below the cutoff on "
                       "the superseded one. It fails on BOTH readings, so no choice of ruler rescues it.",
            "_from": "selectivity-mechanism-options.json -> measurements.M2.lbd_unique_handles",
        })
    return {
        "_why_named": ("Naming a dropped candidate is the difference between an enumeration and an "
                       "advertisement. M398/M399 are the two handles this sweep found and refused."),
        "dropped": out,
        "not_carried_forward": [d["label"] for d in out],
    }


# ==========================================================================================================
# (3) THE LITERATURE RECORD — with a verification level on every entry
# ==========================================================================================================
def literature_record():
    """★ THE ROW'S OWN FALSIFIER, addressed with real sources and an HONEST verification level.

    ⛔ EVERY PUBLISHER, PMC, EUROPE PMC AND CROSSREF HOST RETURNED 403 AT THE EGRESS PATH IN THIS SESSION
    (measured 2026-08-06: `curl` to europepmc.org and api.crossref.org failed CONNECT with 403; WebFetch on
    pubmed.ncbi.nlm.nih.gov, nature.com, pmc.ncbi.nlm.nih.gov, europepmc.org, pubs.rsc.org and biorxiv.org
    all returned HTTP 403). The repository's Europe PMC workflow was unavailable to this session. So NO
    full text and NO publisher abstract was retrieved. What WAS obtained is a web-search result listing:
    title, host, and the DOI or PMID carried inside the returned URL, plus the search engine's own summary.

    That is recorded honestly per entry as `verification`, and it is the reason no entry here asserts a
    page range, an author list or a quantity that was not visible in the returned listing. ⛔ A citation
    whose identifier this session could not see is not written down at all.
    """
    ent = [
        {
            "key": "chen_2016_jacs",
            "title": "Arylfluorosulfates Inactivate Intracellular Lipid Binding Protein(s) through "
                     "Chemoselective SuFEx Reaction with a Binding Site Tyr Residue",
            "venue": "Journal of the American Chemical Society",
            "doi": "10.1021/jacs.6b02960",
            "pmid": "27191344",
            "url": "https://pubs.acs.org/doi/10.1021/jacs.6b02960",
            "what_it_establishes": "Aryl fluorosulfates engage a BINDING-SITE tyrosine in a protein "
                                   "chemoselectively via SuFEx. This is the anchor precedent for "
                                   "tyrosine-directed SuFEx on a folded protein.",
            "what_it_does_NOT_establish": "It is a binding-site tyrosine inside a ligand pocket of an "
                                          "intracellular lipid binding protein. It says nothing about a "
                                          "surface/exit-vector tyrosine reached by a linker.",
            "verification": "TITLE + VENUE + DOI + PMID read off returned search-result URLs. Full text and "
                            "publisher abstract NOT retrieved (403 at every fetch path tried this session).",
        },
        {
            "key": "hahm_2020_natchembiol",
            "title": "Global targeting of functional tyrosines using sulfur-triazole exchange chemistry",
            "venue": "Nature Chemical Biology",
            "doi": "10.1038/s41589-019-0404-5",
            "pmid": "31768034",
            "url": "https://www.nature.com/articles/s41589-019-0404-5",
            "what_it_establishes": "Sulfonyl-triazole (SuTEx) probes profile tyrosine sites at proteome "
                                   "scale in lysates and live cells, and tuning the leaving group improves "
                                   "chemoselectivity for tyrosine over other nucleophilic amino acids.",
            "what_it_does_NOT_establish": "⛔ It is the source of the honest ceiling, not of a licence. The "
                                          "selectivity it reports is a FOLD ENRICHMENT for tyrosine over "
                                          "other nucleophiles, not exclusivity — i.e. the warhead labels "
                                          "other residue classes too, which is exactly what §4 counts.",
            "verification": "TITLE + VENUE + DOI + PMID read off returned search-result URLs; the search "
                            "listing's own summary quoted the fold-selectivity and site-count claims. Full "
                            "text NOT retrieved (403). ⚠ The specific figures are therefore NOT re-homed "
                            "here as numbers — only the direction of the claim is used.",
        },
        {
            "key": "martin_gago_olsen_2019_angew",
            "title": "Arylfluorosulfate-Based Electrophiles for Covalent Protein Labeling: A New Addition "
                     "to the Arsenal",
            "venue": "Angewandte Chemie International Edition",
            "doi": "10.1002/anie.201806037",
            "pmid": "30024079",
            "url": "https://onlinelibrary.wiley.com/doi/full/10.1002/anie.201806037",
            "what_it_establishes": "★ THE DECISIVE ONE FOR THIS LEAD. A review framing arylfluorosulfates "
                                   "as LATENT electrophiles that react on ACTIVATION in particular binding "
                                   "sites — the returned listing states the reaction requires a "
                                   "ligand-binding motif giving sufficient residence time AND a "
                                   "surrounding environment (basic residues) that lowers the pKa of the "
                                   "targeted nucleophile. It also states the residues addressed are "
                                   "context-specific Tyr and Lys, and also Ser.",
            "what_it_does_NOT_establish": "It does not describe a general-purpose tyrosine warhead that "
                                          "works on any exposed tyrosine. The opposite: context is the "
                                          "mechanism.",
            "verification": "TITLE + VENUE + DOI + PMID read off returned search-result URLs. Full text NOT "
                            "retrieved (403 on both Wiley and the PMC mirror).",
        },
        {
            "key": "wang_2018_jacs_fsy",
            "title": "Genetically Encoding Fluorosulfate-l-tyrosine To React with Lysine, Histidine, and "
                     "Tyrosine via SuFEx in Proteins in Vivo",
            "venue": "Journal of the American Chemical Society",
            "doi": "10.1021/jacs.8b01087",
            "pmid": None,
            "url": "https://pubs.acs.org/doi/10.1021/jacs.8b01087",
            "what_it_establishes": "⛔ The cross-reactivity fact, in the title itself: a SuFEx aryl "
                                   "fluorosulfate reacts with proximal LYSINE, HISTIDINE and TYROSINE. The "
                                   "warhead's residue set is not {Tyr}.",
            "what_it_does_NOT_establish": "It is a genetically encoded unnatural amino acid on a protein, "
                                          "not a small-molecule probe; the proximity regime differs. The "
                                          "residue promiscuity is the transferable part.",
            "verification": "TITLE + VENUE + DOI read off returned search-result URLs. Full text NOT "
                            "retrieved (403). PMID not seen in any returned URL, so none is recorded.",
        },
        {
            "key": "vhl_sulfonyl_fluoride_protacs_2024_jmedchem",
            "title": "Structure-Guided Design and Optimization of Covalent VHL-Targeted Sulfonyl Fluoride "
                     "PROTACs",
            "venue": "Journal of Medicinal Chemistry",
            "doi": None,
            "pmid": None,
            "url": "https://pubs.acs.org/jmcmar/article/67/6/4641/171752/Structure-Guided-Design-and-Optimization-of",
            "what_it_establishes": "A SuFEx-class warhead HAS been carried inside a bifunctional degrader "
                                   "and driven degradation — so the construct class is not hypothetical.",
            "what_it_does_NOT_establish": "⛔ THE COVALENT BOND IS ON THE E3 SIDE, NOT THE TARGET SIDE. The "
                                          "returned listing states the sulfonyl fluoride covalently binds "
                                          "VHL Ser110; the degrader's TARGET engagement (BRD4, AR) is "
                                          "non-covalent. This is NOT precedent for a linker-borne SuFEx "
                                          "warhead engaging a target-side tyrosine, which is what Route B "
                                          "would need.",
            "verification": "TITLE + VENUE + volume/issue/page visible in the returned URL path "
                            "(67/6/4641). DOI and PMID not seen in any returned URL, so none is recorded. "
                            "Full text NOT retrieved (403 on the publisher page and on the bioRxiv "
                            "preprint PDF).",
        },
        {
            "key": "sufex_protac_p300_cbp_2025",
            "title": "Construction of PROTAC molecules by the SuFEx reaction for inducing p300/CBP protein "
                     "degradation",
            "venue": "Bioorganic & Medicinal Chemistry (ScienceDirect listing)",
            "doi": None,
            "pmid": "40267748",
            "url": "https://pubmed.ncbi.nlm.nih.gov/40267748/",
            "what_it_establishes": "SuFEx used to BUILD degrader libraries.",
            "what_it_does_NOT_establish": "⚠ Here SuFEx is a LINKER-CONSTRUCTION click reaction, not a "
                                          "protein-engaging warhead. Counting it as precedent for covalent "
                                          "target engagement would be a category error, and it is recorded "
                                          "here so nobody makes it.",
            "verification": "TITLE + PMID read off the returned search-result URL; venue inferred from the "
                            "ScienceDirect listing and marked as such. Full text NOT retrieved (403).",
        },
    ]
    return {
        "_question": "Is 'SuFEx tyrosine' a real chemistry, and how routine is it?",
        "_egress_state": (
            "MEASURED 2026-08-06 in this session: europepmc.org and api.crossref.org failed CONNECT with "
            "403 at the proxy; WebFetch returned HTTP 403 for pubmed.ncbi.nlm.nih.gov, nature.com, "
            "pmc.ncbi.nlm.nih.gov, europepmc.org, pubs.rsc.org and biorxiv.org. The repository's Europe PMC "
            "workflow was owned by another session and not used. Every entry below therefore carries a "
            "verification level, and none carries a figure that was not visible in a returned listing."),
        "entries": ent,
        "★_verdict": (
            "SuFEx tyrosine-targeting chemistry is REAL and PUBLISHED — the row's label 'precedented' "
            "SURVIVES contact with the literature and is not an overstatement. It is also NOT routine, and "
            "the specific way it is non-routine matters more than the label: the precedent set is "
            "BINDING-SITE tyrosines whose local environment lowers the phenol pKa and whose ligand gives "
            "the warhead residence time. Y419 is not that object. It is an EXIT-VECTOR residue at "
            "%s A from the cryptic pocket, at RSA %s on one static opened conformer, with no pKa, no "
            "measured microenvironment and no ligand residence time modelled anywhere in this repository. "
            "So the chemistry does not kill the lead — but it does not transfer to this site for free "
            "either, and the gap between 'this residue class is addressable' and 'this residue is "
            "addressable' is the whole of the remaining risk."),
        "★_what_would_settle_it": (
            "A bench experiment, and nothing in silico. No pKa predictor validated on ligand-directed SuFEx "
            "reactivity exists in this program, and building one is not a $0 job. The honest in-silico "
            "ceiling for Y419 is exactly where C397's is: a REACH-and-UNIQUENESS statement."),
    }


# ==========================================================================================================
# (4) THE CHEMOSELECTIVITY CONSEQUENCE — measured, not asserted
# ==========================================================================================================
def _assert_pocket_matches_owner(pocket):
    if tuple(pocket) != CRYPTIC_POCKET_UNIPROT_MIRROR:
        raise SystemExit(
            "⛔ CRYPTIC POCKET DEFINITION DRIFTED. nr4a_paralogue_unique_residues.CRYPTIC_POCKET_UNIPROT = "
            f"{tuple(pocket)} but this file mirrors {CRYPTIC_POCKET_UNIPROT_MIRROR}. The owner wins — fix "
            "the mirror. Refusing to emit a census against a pocket the owner does not define.")


def sufex_competitor_census(y419_dist_A):
    """★ NEW FACT, and this file is its one home.

    THE QUESTION. `S1`'s chemoselectivity window is THE decision quantity for the cysteine handle: the
    interval of linker backbone-atom counts over which the electrophile reaches C397 and reaches NO OTHER
    CYSTEINE in NR4A3, NR4A1 or NR4A2. It is closed by a PARALOGUE cysteine in 30 of 30 graded cells under
    each convention (`categorical-axis-audit.json` -> window_verdict). That window is computed over
    CYSTEINE SG ATOMS ALONE — `nr4a3_linker_covalent_reach.cysteines_in` reads `SG` and nothing else.

    A SuFEx warhead does not see a cysteine-only competitor set. The literature record above reports Tyr,
    Lys, His and Ser labelling for this warhead class. So the existing window CANNOT be inherited by Y419,
    and the honest statement of the consequence needs the size of the competitor population the SuFEx
    warhead would actually face. That is what this counts.

    ⛔ WHAT THIS IS AND IS NOT. This is a DISTANCE-ORDERED CENSUS over the same three committed opened
    models, using the same cryptic-pocket reference and the same minimum-heavy-atom-distance metric that
    `M2` used for `dist_to_cryptic_pocket_A`. It is NOT the backbone-atom window: it does not run the E3
    placement/pendant enumeration, so it cannot say at which linker length a competitor arrives. It is a
    LOWER-BOUND DIAGNOSTIC on the size of the problem — a count of how many reactive competitors sit at or
    inside the target's own distance shell. A census that says the competitor population is N times larger
    does not prove the window is narrower; it proves the window was never computed for this warhead and
    that computing it is not optional.

    ⚠ PARALOGUE POSITIONS ARE ONLY AS GOOD AS THE SUPERPOSITION. `superpose_paralogue` returns a per-residue
    post-fit deviation; residues outside the structured core have unreliable positions in the NR4A3 frame.
    They are counted separately (`n_excluded_unreliable`) and kept out of the headline rather than dropped.
    """
    import nr4a3_basin_search as B
    import nr4a_paralogue_unique_residues as U
    _assert_pocket_matches_owner(U.CRYPTIC_POCKET_UNIPROT)

    ref = B.load_paralogue(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    fits = {"NR4A3": ref}
    for sp in ("NR4A1", "NR4A2"):
        mob = B.load_paralogue(os.path.join(STRUCT, f"{sp.lower()}-opened.pdb"))
        fits[sp] = B.superpose_paralogue(mob, ref)

    # The distance reference: every heavy atom of the NR4A3 cryptic-pocket residues, in NR4A3's own frame.
    pocket_atoms = []
    for uni in U.CRYPTIC_POCKET_UNIPROT:
        pocket_atoms.extend(ref["atoms_by_res"].get(uni - U.LOCAL_OFFSET, []))
    pocket_pts = [(a["x"], a["y"], a["z"]) for a in pocket_atoms]
    pocket_res = {uni - U.LOCAL_OFFSET for uni in U.CRYPTIC_POCKET_UNIPROT}

    def scan(atom_map):
        rows = []
        for sp, model in fits.items():
            dev = model.get("deviation_by_res") or {}
            for rid, alist in model["atoms_by_res"].items():
                if not alist:
                    continue
                resname = alist[0]["resname"]
                want = atom_map.get(resname)
                if not want:
                    continue
                hit = next((a for a in alist if a["name"] == want), None)
                if hit is None:
                    continue
                p = (hit["x"], hit["y"], hit["z"])
                # ⚠ self-exclusion, same rule M2 used: a pocket-LINING residue is ~0 A from "the pocket" by
                # construction. Its own atoms come out before the minimum is taken.
                pts = pocket_pts if not (sp == "NR4A3" and rid in pocket_res) else [
                    (a["x"], a["y"], a["z"]) for a in pocket_atoms if a["resid"] != rid]
                if not pts:
                    continue
                d = min(math.dist(p, q) for q in pts)
                reliable = True if sp == "NR4A3" else (dev.get(rid) is not None
                                                       and dev[rid] <= CORE_DEVIATION_MAX_A)
                rows.append({"protein": sp, "local_resid": rid, "resname": resname,
                             "reactive_atom": want, "dist_to_cryptic_pocket_A": _r(d, 2),
                             "post_fit_deviation_A": _r(dev.get(rid), 2) if sp != "NR4A3" else 0.0,
                             "position_reliable_in_nr4a3_frame": bool(reliable),
                             "uniprot_if_nr4a3": (rid + U.LOCAL_OFFSET) if sp == "NR4A3" else None})
        return sorted(rows, key=lambda r: r["dist_to_cryptic_pocket_A"])

    def summarise(rows, label):
        rel = [r for r in rows if r["position_reliable_in_nr4a3_frame"]]
        inside = [r for r in rel if r["dist_to_cryptic_pocket_A"] <= y419_dist_A]
        per_prot, per_res = {}, {}
        for r in inside:
            per_prot[r["protein"]] = per_prot.get(r["protein"], 0) + 1
            per_res[r["resname"]] = per_res.get(r["resname"], 0) + 1
        return {
            "warhead_class": label,
            "residue_types_counted": sorted({r["resname"] for r in rows}),
            "n_reactive_atoms_all_three_models": len(rows),
            "n_excluded_unreliable": len(rows) - len(rel),
            "n_reliable": len(rel),
            "n_at_or_inside_Y419_distance_shell": len(inside),
            "by_protein_inside_shell": dict(sorted(per_prot.items())),
            "by_residue_type_inside_shell": dict(sorted(per_res.items())),
            "nearest_10_inside_shell": inside[:10],
        }

    sufex_rows = scan(SUFEX_REACTIVE_ATOM)
    cys_rows = scan(CYS_REACTIVE_ATOM)
    # ⚠ SENSITIVITY, because the widest residue set is the one a reader will challenge. Ser and Thr are
    # counted in the headline and that is deliberate: a COMPETITOR is a residue the warhead can label, not a
    # residue anyone would design against. `M2` grades Ser "not a handle outside catalytic serines" — a
    # statement about DESIGN INTENT — while the literature record here reports a sulfonyl fluoride PROTAC
    # whose covalent bond is on VHL **Ser110**, i.e. a serine labelled in practice. Both are true and they
    # are not the same question. The narrow set (Tyr/Lys/His only) is reported beside the headline so the
    # conclusion can be read either way.
    narrow_rows = scan({k: v for k, v in SUFEX_REACTIVE_ATOM.items() if k in ("TYR", "LYS", "HIS")})
    s = summarise(sufex_rows, "SuFEx (aryl fluorosulfate / sulfonyl fluoride / sulfonyl triazole)")
    c = summarise(cys_rows, "cysteine-directed (acrylamide / chloroacetamide) — what S1's window WAS "
                            "computed over")
    nar = summarise(narrow_rows, "SuFEx, NARROW residue set (Tyr/Lys/His only) — the sensitivity check")
    ratio = (s["n_at_or_inside_Y419_distance_shell"] / c["n_at_or_inside_Y419_distance_shell"]) \
        if c["n_at_or_inside_Y419_distance_shell"] else None
    ratio_narrow = (nar["n_at_or_inside_Y419_distance_shell"] / c["n_at_or_inside_Y419_distance_shell"]) \
        if c["n_at_or_inside_Y419_distance_shell"] else None
    return {
        "_what_this_measures": (
            "How many reactive competitors each warhead class faces at or inside the target's own distance "
            "shell from the cryptic pocket, on the same three committed opened models `M2` used."),
        "_what_this_is_NOT": (
            "⛔ NOT the chemoselectivity window. The window is an interval in linker BACKBONE-ATOM counts "
            "from an E3 anchor and requires the placement/pendant enumeration in "
            "`nr4a3_linker_covalent_reach.py`, which has never been run for a non-cysteine warhead. This is "
            "a lower-bound diagnostic on the SIZE of that unrun problem."),
        "_shell_definition_A": y419_dist_A,
        "_shell_is": "Y419's own dist_to_cryptic_pocket_A, cited from selectivity-mechanism-options.json -> "
                     "measurements.M2.lbd_unique_handles",
        "_reliability_rule": (f"Paralogue residues with post-fit deviation > {CORE_DEVIATION_MAX_A} A after "
                              "`superpose_paralogue` are counted as unreliable and excluded from the "
                              "headline, never silently dropped."),
        "superposition": {sp: fits[sp]["superposition"] for sp in ("NR4A1", "NR4A2")},
        "sufex_warhead": s,
        "cysteine_warhead": c,
        "sufex_warhead_narrow_set_sensitivity": nar,
        "_why_ser_and_thr_are_in_the_headline_set": (
            "A COMPETITOR is a residue the warhead can label, not a residue anyone would design against. "
            "`M2` grades Ser 'not a handle outside catalytic serines' — a statement about DESIGN INTENT — "
            "while `literature_record.vhl_sulfonyl_fluoride_protacs_2024_jmedchem` reports a sulfonyl "
            "fluoride PROTAC whose covalent bond is on VHL **Ser110**, a serine labelled in practice. Both "
            "are true and they are not the same question. The narrow set is reported beside the headline so "
            "the conclusion can be read either way — and it does not change the direction."),
        "competitor_population_ratio_sufex_over_cysteine": _r(ratio, 2),
        "competitor_population_ratio_narrow_set_over_cysteine": _r(ratio_narrow, 2),
        "★_finding": (
            "Inside Y419's own distance shell the SuFEx warhead faces "
            f"{s['n_at_or_inside_Y419_distance_shell']} reactive competitors across the three models, "
            f"against {c['n_at_or_inside_Y419_distance_shell']} for the cysteine warhead whose window `S1` "
            f"actually computed — a factor of {_r(ratio, 2)}, and {_r(ratio_narrow, 2)} even on the narrow "
            f"Tyr/Lys/His set ({nar['n_at_or_inside_Y419_distance_shell']} competitors), so the direction "
            "does not depend on counting Ser/Thr. `S1`'s window is closed by a PARALOGUE "
            "cysteine in 30 of 30 graded cells under each convention with the SMALLER of these two "
            "populations. ⛔ Therefore the existing window may not be inherited by Y419 in either "
            "direction: it cannot be quoted as reassurance, and it cannot be quoted as a refutation. It "
            "has not been computed for this warhead."),
        "_S1_window_citations": {
            "closed_by_a_paralogue_cysteine": "30 of 30 graded cells, each convention — "
                                              "categorical-axis-audit.json -> window_verdict."
                                              "★_the_correct_sentence",
            "through_space_majority_closer": "NR4A1 C505 in 24 of 30 cells — a position NR4A3 SHARES "
                                             "(C536), so no reciprocal-uniqueness reading applies to it",
            "corridor_majority_closer": "NR4A2 C534 in 23 of 30 cells — a position NR4A3 LACKS (S565)",
            "competitor_set_is_cysteine_only": "nr4a3_linker_covalent_reach.cysteines_in reads atom 'SG' "
                                               "and no other reactive atom",
        },
        "rows_sufex": sufex_rows,
        "rows_cysteine": cys_rows,
    }


# ==========================================================================================================
# (5) ROADMAP EDITS — DESCRIBED, NEVER APPLIED
# ==========================================================================================================
def build_map_edits(ruling, dropped, census, lit):
    """Same anchor discipline as `paralogue_pocket_contrast.build_map_edits`: every `current_text` is READ
    out of the live map, so an entry that cannot be targeted says so instead of being silently wrong."""
    import map_edits as ME
    text = ME.load_map()
    art = "research/modalities/sufex-second-handle.json"
    y = ruling["Y419"]
    ratio = census["competitor_population_ratio_sufex_over_cysteine"]
    n_s = census["sufex_warhead"]["n_at_or_inside_Y419_distance_shell"]
    n_c = census["cysteine_warhead"]["n_at_or_inside_Y419_distance_shell"]

    entries = [
        ME.edit(
            text, "§8 Route B — the heading clause",
            "BUT ONLY ON THE RULER THIS PAGE PERMITS, AND BOTH READINGS",
            "The clause says the axis is wider 'BUT ONLY ON THE RULER THIS PAGE PERMITS', which reads as a "
            "concession — as though the permitted ruler were the weaker of two. It is the only one this "
            "page permits BECAUSE the other is KNOWN-DEFECTIVE in its own instrument table. Stating that "
            "positively is the difference between a hedge and a ruling.",
            art,
            ME.replace_in_line(
                "BUT ONLY ON THE RULER THIS PAGE PERMITS, AND BOTH READINGS",
                "ON THE RULER THIS PAGE MANDATES, WHICH IS THE ONLY ONE IT PERMITS — AND BOTH READINGS")),
        ME.edit(
            text, "§8 Route B — 'neither reading is chosen here'",
            "The sweep cuts both ways and neither reading is chosen here",
            "⛔ THE MANDATE VIOLATION, in one sentence. path-family-synthesis.md §2 Tier-1 row 6 says "
            "'take the threshold-free rank as the roadmap mandates and STOP QUOTING BOTH RULERS AS EQUALS'. "
            "'Neither reading is chosen here' is precisely quoting them as equals, and it lets a reader "
            "pick the criterion this page's own instrument table marks KNOWN-DEFECTIVE. A superseded "
            "reading is registered, never offered.",
            art,
            ME.replace_in_line(
                "**The sweep cuts both ways and neither reading is chosen here:**",
                "**The sweep cuts both ways — and the reading that BINDS is the threshold-free RANK, per "
                "[`path-family-synthesis.md`](path-family-synthesis.md) §2 row 6. The cutoff reading is "
                "registered as SUPERSEDED, not offered as an alternative** "
                "([`sufex-second-handle.json`](../modalities/sufex-second-handle.json) "
                "`the_reported_ruler`):")),
        ME.edit(
            text, "§8 Route B — the superseded cutoff bullet",
            "the cysteines and lysines already committed.",
            "The bullet is correct and must stay — registering what the discredited ruler said is how a "
            "reader grades the sweep. What it lacks is the label that stops it being read as a live "
            "alternative.",
            art,
            ME.append_to_line(
                " ⚠ **SUPERSEDED AS A RULER, RETAINED AS A CROSS-CHECK** — `V17` fails its own positive "
                "control ([§3.1 row `V17`](#31--the-instrument-table)), so this reading records what a "
                "criterion with a demonstrated false negative returns; it does not compete with the rank.")),
        ME.edit(
            text, "§8 Route B — Y419 bullet",
            "literature-anchored covalent site and the very false negative that discredited the cutoff.",
            "The bullet states the rank result without the rank position or the numbers behind it, and "
            "without the two limits that decide how much it is worth: the chemistry precedent is for "
            "BINDING-SITE tyrosines and Y419 is an exit-vector residue, and the chemoselectivity window has "
            "never been computed for a non-cysteine warhead.",
            art,
            ME.append_to_line(
                f" It ranks **{y['rank_among_tetherable_unique_handles']} of "
                f"{y['n_tetherable_unique_handles_ranked']}** tetherable unique handles at RSA "
                f"**{y['rsa']}**, against the reference site's **{ruling['reference_rsa']}**. ⛔ **Two "
                "limits travel with it and neither is optional.** **(a)** The SuFEx tyrosine precedent is "
                "for **binding-site** tyrosines whose local environment lowers the phenol pKa and whose "
                "ligand supplies residence time; Y419 is an **exit-vector** residue and no pKa, "
                "microenvironment or residence time is modelled anywhere here. **(b)** ⛔ **`S1`'s "
                "chemoselectivity window may not be inherited** — it is computed over **cysteines only**, "
                f"and inside Y419's own distance shell a SuFEx warhead faces **{n_s}** reactive "
                f"competitors against the cysteine warhead's **{n_c}** (**{ratio}×**). "
                "[`sufex-second-handle.json`](../modalities/sufex-second-handle.json) owns those counts. "
                "**This is a REAGENT-level statement**: a second candidate handle, not a second engagement "
                "claim, and it does **not** unblock `R5`")),
        ME.edit(
            text, "§8 Route B — the M398/M399 drop",
            "point: a sweep that only reports what survives is a sweep nobody can grade.",
            "The drop is stated without its numbers, so a reader cannot check it. Rule 1: point at the "
            "artifact that owns them.",
            art,
            ME.append_to_line(
                " The numbers: RSA **%s** / **%s** against the reference site's **%s**, ranks **%s** and **%s** of "
                "**%s** — [`sufex-second-handle.json`](../modalities/sufex-second-handle.json) "
                "`explicitly_dropped`." % (
                    dropped["dropped"][0].get("rsa"), dropped["dropped"][1].get("rsa"),
                    ruling["reference_rsa"],
                    dropped["dropped"][0].get("rank_among_tetherable_unique_handles"),
                    dropped["dropped"][1].get("rank_among_tetherable_unique_handles"),
                    y["n_tetherable_unique_handles_ranked"]))),
        ME.edit(
            text, "§10.1 open rows — new row 30, appended after row 29",
            # ⚠ ANCHORED ON THE LAST TABLE ROW, NOT ON THE HEADING. The §10.1 heading is followed by a prose
            # paragraph before the table header, so appending a `|`-row under the heading would land outside
            # the table and render as broken markdown.
            "| **29** | **The categorical axis's cross-system decoy null (`IC-2`)**",
            "The second-handle question is on no ranked row. It is the difference between Route B having a "
            "single point of failure that is a FACT ABOUT THE PROTEIN and one that was an artefact of "
            "sweeping two residue classes — and the one thing that would settle how much Y419 is worth is a "
            "$0 CPU job (the non-cysteine chemoselectivity window) that has never been run.",
            art,
            ME.append_after_line(
                "| **30** | **The non-cysteine chemoselectivity window — run the reach enumeration for a "
                "SuFEx warhead at Y419** | `R8` `R15` (Route B's single-point-of-failure hedge) | ○ **not "
                "started** | — ($0) | **$0** — CPU/CI | ⛔ **The window that decides the cysteine handle has "
                "never been computed for any other warhead.** `nr4a3_linker_covalent_reach.cysteines_in` "
                "reads atom `SG` and nothing else, so `S1`'s *closed by a paralogue cysteine in 30 of 30 "
                "graded cells* is a statement about a **cysteine-only** competitor set. Inside Y419's own "
                f"distance shell a SuFEx warhead faces **{n_s}** reactive competitors (Tyr/Lys/His/Ser/Thr, "
                f"all three models) against the cysteine warhead's **{n_c}** — **{ratio}×** the population, "
                "on the SMALLER of which the existing window already closes "
                "([`sufex-second-handle.json`](../modalities/sufex-second-handle.json)). ★ **What it "
                "settles:** whether Y419 is a usable second handle or a handle whose window is shut before "
                "it opens — i.e. whether Route B's single point of failure is a fact about the protein or a "
                "gap in the enumeration. ⛔ **What it does NOT settle:** the chemistry. SuFEx tyrosine "
                "precedent is for **binding-site** tyrosines with a pKa-perturbing environment and ligand "
                "residence time; Y419 is an **exit-vector** residue, and closing that gap needs a bench "
                "([`sufex-second-handle.json`](../modalities/sufex-second-handle.json) `literature_record`) |")),
    ]
    return {
        "_contract": ("DESCRIBED, NEVER APPLIED. Every `current_text` is a byte-exact substring of "
                      "nr4a3-program-map.md as it stood at generation time; verify with `grep -F`. An "
                      "anchor that could not be resolved carries status ANCHOR_NOT_FOUND / "
                      "ANCHOR_NOT_UNIQUE and NO proposed_text — a visible refusal, not a mis-targeted edit."),
        "_locked_files_this_generator_must_not_touch": list(LOCKED),
        "entries": entries,
        "verification": ME.verify(entries, text),
    }


# ==========================================================================================================
def build():
    sel = _load(SELMECH)
    m2 = sel["measurements"]["M2"]
    by_label = {h["class"] + str(h["uniprot"]): h for h in m2["lbd_unique_handles"]}
    y419 = by_label.get("Y419")
    if y419 is None:
        raise SystemExit("⛔ Y419 is not in the committed M2 handle list. Refusing to emit a finding about "
                         "a handle the artifact does not contain.")

    ruling = the_reported_ruler(m2)
    dropped = explicitly_dropped(m2)
    lit = literature_record()
    census = sufex_competitor_census(y419["dist_to_cryptic_pocket_A"])
    lit["★_verdict"] = lit["★_verdict"] % (y419["dist_to_cryptic_pocket_A"], y419["rsa"])

    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    return {
        "_title": "Y419 as a second covalent handle — the ruler ruling, the drops, the chemistry and the "
                  "chemoselectivity consequence",
        "_status": "$0 CPU. Reagent-level enumeration finding. No GPU, no rental, no claim about binding, "
                   "reactivity, degradation, efficacy, safety, a therapeutic window or clinical readiness, "
                   "and no selectivity claim beyond the two-paralogue comparison set.",
        "_serves": ["path-family-synthesis.md §2 Tier-1 row 6 (the mandate)",
                    "roadmap §8 Route B", "roadmap §10.1"],
        "_one_fact_one_place": (
            "M2's numbers are CITATIONS carrying `_from`; selectivity-mechanism-options.json owns them. The "
            "competitor census in `sufex_competitor_census` is a NEW fact and this file is its one home. "
            "`S1`'s window figures are citations to categorical-axis-audit.json."),
        "_reads": {
            "research/modalities/selectivity-mechanism-options.json": "M2 — the 11-class sweep, the rank, "
                                                                      "the handles and their RSA",
            "results/nr4a3-matrix/nr4a3-opened.pdb": "the NR4A3 opened LBD model — distance reference",
            "results/nr4a3-matrix/nr4a1-opened.pdb": "superposed into the NR4A3 frame",
            "results/nr4a3-matrix/nr4a2-opened.pdb": "superposed into the NR4A3 frame",
            "research/modalities/categorical-axis-audit.json": "S1's window verdict (cited, not re-homed)",
        },
        "_generated": {"utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "et": _et(now),
                       "generator": "research/modalities/sufex_second_handle.py"},
        "the_reported_ruler": ruling,
        "explicitly_dropped": dropped,
        "literature_record": lit,
        "sufex_competitor_census": census,
        "★_headline": (
            "Route B's single point of failure is NOT purely a fact about the protein — the enumeration was "
            "narrower than the mechanism. Sweeping 11 reactive classes puts Y419, a paralogue-unique "
            f"tyrosine at RSA {y419['rsa']} and {y419['dist_to_cryptic_pocket_A']} A from the cryptic "
            f"pocket, at rank {ruling['Y419']['rank_among_tetherable_unique_handles']} of "
            f"{ruling['Y419']['n_tetherable_unique_handles_ranked']} tetherable unique handles — ABOVE the "
            "NR4A family's one literature-anchored covalent site on the ruler this program mandates. "
            "⛔ AND IT IS A CANDIDATE, NOT REDUNDANCY. Three things stand between it and a second handle, "
            "all named: the SuFEx precedent is for BINDING-SITE tyrosines and Y419 is an exit-vector "
            "residue; the chemoselectivity window has never been computed for a non-cysteine warhead and "
            "the competitor population is "
            f"{census['competitor_population_ratio_sufex_over_cysteine']}x larger inside Y419's own shell; "
            "and Route B remains blocked upstream on `R5`, which a second handle does not touch."),
        "⛔_limits": [
            "REAGENT-LEVEL ONLY. Nothing here says an adduct forms. No phenol pKa, nucleophilicity, adduct "
            "stability or electrophile promiscuity is modelled anywhere in this repository.",
            "Sequence uniqueness is exact; every geometric annotation is ONE static opened conformer, and "
            "the paralogue geometry additionally inherits the superposition's core/outlier split.",
            "The competitor census is a distance-ordered LOWER-BOUND DIAGNOSTIC, not the backbone-atom "
            "window. It cannot say at which linker length a competitor arrives.",
            "Chemistry credibility remains a LITERATURE LABEL. No citation in `literature_record` was read "
            "in full text — every publisher, PMC, Europe PMC and Crossref host returned 403 in this "
            "session, and each entry records that.",
            "A second handle does not unblock Route B. `R5` — the site/pose question `V3` returned "
            "INCONCLUSIVE on — is upstream of every anchor here, Y419's included.",
            "The comparison set is TWO paralogues. Nothing here is a proteome-wide statement of any kind.",
        ],
        "map_edits_required": build_map_edits(ruling, dropped, census, lit),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="regenerate and diff against the committed artifact; exit 1 on drift")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    res = build()
    if a.check:
        if not os.path.exists(a.out):
            print("⛔ no committed artifact at %s" % a.out)
            return 1
        old = _load(a.out)
        old.pop("_generated", None)
        new = json.loads(json.dumps(res))
        new.pop("_generated", None)
        if old != new:
            print("⛔ DRIFT — regenerated output differs from the committed artifact")
            return 1
        print("✅ no drift")
        return 0
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print("[sufex] wrote %s" % a.out)
    c = res["sufex_competitor_census"]
    print("[sufex] Y419 rank %s/%s, RSA %s vs reference %s" % (
        res["the_reported_ruler"]["Y419"]["rank_among_tetherable_unique_handles"],
        res["the_reported_ruler"]["Y419"]["n_tetherable_unique_handles_ranked"],
        res["the_reported_ruler"]["Y419"]["rsa"], res["the_reported_ruler"]["reference_rsa"]))
    print("[sufex] competitors inside Y419 shell: SuFEx %s vs cysteine %s (%sx)" % (
        c["sufex_warhead"]["n_at_or_inside_Y419_distance_shell"],
        c["cysteine_warhead"]["n_at_or_inside_Y419_distance_shell"],
        c["competitor_population_ratio_sufex_over_cysteine"]))
    print("[sufex] map edits: %s" % res["map_edits_required"]["verification"]["status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
