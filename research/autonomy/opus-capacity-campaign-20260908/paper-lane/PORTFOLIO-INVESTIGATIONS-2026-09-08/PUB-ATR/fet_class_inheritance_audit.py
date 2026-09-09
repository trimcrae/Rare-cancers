#!/usr/bin/env python3
"""Boundary audit of the FET->ATM->ATR class-inheritance premise used by PUB-ATR.

TWO OFFLINE QUESTIONS, both answered from artifacts already in this repo:

 Q1  ASSAY-LEVEL AUDIT.  The assessment states the mechanism was measured on FOUR fusions
     across four diseases (EWSR1::FLI1, EWSR1::ATF1, EWSR1::WT1, FUS::CHOP).  Which ASSAY
     was each of those four actually run in, in the cached full text of the source
     (PMC10187251, held verbatim in atr-hrd-sarcoma-series-inputs.json)?  The structural
     precondition census speaks ONLY to the DSB-recruitment / RG-dependence arm, so the
     relevant count is how many of the four appear in THAT arm.

 Q2  FAMILY GEOMETRY.  The census's zero-RG criterion and its 299-residue RGG-free ceiling
     are EWSR1 numbers.  EMC's minority partners are TAF15 and FUS.  Recompute, from the
     cached sequences, the retained-RG fraction each FET protein would show at the SAME
     retained N-terminal lengths the census uses for EWSR1, and the longest zero-RG
     N-terminus each admits.

Writes nothing outside this lane directory.  No network.  No new sequence, no new
breakpoint, no citation is introduced here: every input is read from a committed file.
"""
import json, re, sys, os
from collections import OrderedDict

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research/modalities")

def load(p):
    with open(os.path.join(MOD, p)) as f:
        return json.load(f)

# ---------------------------------------------------------------- Q1
FUSIONS = OrderedDict([
    ("EWSR1::FLI1",  r"EWSR1[-– ]?FLI1?\b"),
    ("EWSR1::ATF1",  r"EWSR1[-– ]?ATF1\b"),
    ("EWSR1::WT1",   r"EWSR1[-– ]?WT1\b"),
    ("FUS::CHOP",    r"(FUS[-– ]?CHOP|FUS[-– ]?DDIT3)\b"),
])
# assay classes, in the words the source itself uses
ARMS = OrderedDict([
    ("dsb_recruitment", r"(laser|micro-?irradiat|recruit)"),
    ("rg_rgg_dependence", r"(RGG|RG[- ]?mutant|ΔRGG)"),
    ("atm_signalling", r"(ATM)"),
    ("atri_drug_sensitivity", r"(IC50|sensitiv|elimusertib|ceralasertib|berzosertib)"),
    ("cell_line_panel_membership", r"(panel|cell line)"),
])

def q1():
    xml = load("atr-hrd-sarcoma-series-inputs.json")["mechanism_fulltext_xml"]
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
    # sentence split; crude but the quotes are printed verbatim for checking
    sents = re.split(r"(?<=\.)\s+", txt)
    out = OrderedDict()
    for name, pat in FUSIONS.items():
        rx = re.compile(pat)
        hits = [s for s in sents if rx.search(s)]
        rec = OrderedDict()
        rec["mentions_in_cached_fulltext"] = len(hits)
        arms = OrderedDict()
        for arm, apat in ARMS.items():
            arx = re.compile(apat, re.I)
            co = [s for s in hits if arx.search(s)]
            arms[arm] = OrderedDict([
                ("n_sentences", len(co)),
                ("example_quote", co[0].strip()[:400] if co else None),
            ])
        rec["arms"] = arms
        rec["appears_in_dsb_recruitment_arm"] = arms["dsb_recruitment"]["n_sentences"] > 0
        rec["fet_protein"] = "FUS" if name.startswith("FUS") else "EWSR1"
        out[name] = rec
    return out

# ---------------------------------------------------------------- Q2
def rg_positions(seq):
    """1-based positions of every RG dipeptide (R at i, G at i+1)."""
    return [i + 1 for i in range(len(seq) - 1) if seq[i] == "R" and seq[i + 1] == "G"]

def q2():
    seqs = load("fet-sequences-cache.json")
    census = load("emc-fet-idr-census.json")
    # retained-length landmarks the census actually uses, each already sourced there
    LANDMARKS = OrderedDict([
        (161, "TAF15 e6 cut (TAF15::NR4A3, the one pinned non-EWSR1 EMC junction)"),
        (264, "EWSR1 e7 cut - Ewing type 1 measured half; EMC type 2 is byte-identical to it"),
        (324, "EWSR1 e8 cut - EWSR1::ATF1, a MEASURED fusion, retains 7/30 RG here"),
        (431, "EWSR1 e12 cut - EMC type 1, the commonest EMC fusion"),
        (472, "EWSR1 e13 cut - EMC type 5"),
    ])
    out = OrderedDict()
    for fet in ("EWSR1", "TAF15", "FUS"):
        s = seqs[fet]
        rg = rg_positions(s)
        rec = OrderedDict()
        rec["length"] = len(s)
        rec["n_RG_dipeptides_total"] = len(rg)
        rec["first_RG_at"] = rg[0]
        rec["longest_zero_RG_N_terminus"] = rg[0] - 1
        rec["census_wildtype_first_RG_at"] = census["wild_type_annotation"][fet]["first_RG_dipeptide_at"]
        rec["agrees_with_census_annotation"] = (rg[0] == census["wild_type_annotation"][fet]["first_RG_dipeptide_at"])
        at = OrderedDict()
        for cut, why in LANDMARKS.items():
            if cut > len(s):
                at[str(cut)] = {"_note": "cut exceeds this protein's length", "why_this_cut": why}
                continue
            n = sum(1 for p in rg if p <= cut)
            at[str(cut)] = OrderedDict([
                ("why_this_cut", why),
                ("rg_retained", n),
                ("fraction_of_wildtype_RG_retained", round(n / len(rg), 3)),
                ("meets_strict_zero_RG_criterion", n == 0),
            ])
        rec["at_census_landmark_cuts"] = at
        out[fet] = rec
    return out

def main():
    a1, a2 = q1(), q2()
    measured_recruit = [k for k, v in a1.items() if v["appears_in_dsb_recruitment_arm"]]
    panel_only = [k for k, v in a1.items() if not v["appears_in_dsb_recruitment_arm"]]
    nonews = [k for k in measured_recruit if a1[k]["fet_protein"] != "EWSR1"]
    res = OrderedDict()
    res["_what"] = ("Boundary audit of the class-inheritance premise behind PUB-ATR. Reads only "
                    "committed artifacts; introduces no new sequence, breakpoint or citation.")
    res["_inputs"] = ["research/modalities/atr-hrd-sarcoma-series-inputs.json (mechanism_fulltext_xml, PMC10187251)",
                      "research/modalities/fet-sequences-cache.json",
                      "research/modalities/emc-fet-idr-census.json"]
    res["q1_assay_level_audit"] = a1
    res["q1_summary"] = OrderedDict([
        ("fusions_in_dsb_recruitment_arm", measured_recruit),
        ("n_in_dsb_recruitment_arm", len(measured_recruit)),
        ("non_EWSR1_fusions_in_dsb_recruitment_arm", nonews),
        ("n_non_EWSR1_in_dsb_recruitment_arm", len(nonews)),
        ("fusions_appearing_only_outside_the_recruitment_arm", panel_only),
        ("_reading", "The DSB-recruitment / RG-dependence arm is the ONLY arm the structural "
                     "precondition census speaks to. In the cached full text every fusion in that "
                     "arm is an EWSR1 fusion; the one non-EWSR1 member of the four (FUS::CHOP) "
                     "appears once, as a cell line in the ATR-inhibitor sensitivity panel."),
    ])
    res["q2_family_geometry"] = a2
    res["_limits"] = [
        "Q1 audits the CACHED main text of PMC10187251 only. Supplementary notes, figures and tables "
        "are not in this repo's cache, so 'does not appear in the recruitment arm here' bounds the "
        "cached record, not the source's entire body of work.",
        "Q2 is a sequence geometry. It says where RG dipeptides sit, not what any fusion does.",
        "No efficacy, potency, dose, safety or therapeutic-window statement follows from either half.",
    ]
    json.dump(res, sys.stdout, indent=1)
    print()

if __name__ == "__main__":
    main()
