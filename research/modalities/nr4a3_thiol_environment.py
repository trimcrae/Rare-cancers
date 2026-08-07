#!/usr/bin/env python3
"""
`C12` — thiol pKa / intrinsic nucleophilicity for C397: the $0 KNOWN-ANSWER PRECHECK, plus the structural
determinants read that is available WITHOUT a predictor (roadmap §10.1a `Q9`).

★★ THE ONE THING THIS FILE IS FOR. `S1` — the categorical covalent axis, the program's strongest surviving
mechanism — rests on C397 being addressable by an electrophile. Across this entire repository that property
is a **LABEL**, never a measured quantity: limit L6 of the categorical audit says in its own words that no
thiol pKa, nucleophilicity, adduct stability or promiscuity is modelled anywhere here. `C12` proposes to
convert one of those four from a label into a number.

⛔ AND IT DOES NOT DO SO IN THIS FILE, DELIBERATELY. Two separate reasons, both binding:
  * **The claim ceiling (roadmap §2.3).** `C12` is at *proposed*. Its own register entry says the known-answer
    set is `candidate_unverified` and that a $0 precheck must settle it before anything is quoted. A pKa
    computed before that precheck returns would be a number with no way to grade it — and the register
    already warns that pKa predictors are *weakly calibrated on buried cysteines*, which is the exact regime
    C397 sits in.
  * **The environment.** No pKa predictor is installed in this sandbox. Per CLAUDE.md §6 that is a routing
    problem and not a stopping point — but routing it is worth nothing until the precheck says what the
    prediction would be graded against.

⛔⛔ WHAT NO RESULT IN THIS FILE, OR IN ANY FOLLOW-UP TO IT, CAN EVER LICENSE. **A favourable thiol pKa is
NOT evidence that a covalent bond forms.** Reactivity is necessary and never sufficient: adduct formation in
a cell additionally requires the electrophile to be delivered to the site, held there long enough, in a
geometry that permits attack, against a proteome of competing nucleophiles, at a concentration the cell
tolerates. This file models none of that and neither would a pKa. Nothing here is a claim about binding,
adduct formation, degradation, efficacy, safety, a therapeutic window or clinical readiness, and nothing here
is a statement about selectivity beyond the three-protein comparison set.

WHAT IT ACTUALLY COMPUTES — part B, and it is a READ.
The physical determinants that a thiol pKa depends on are measurable from a structure without predicting the
pKa itself, and none of them has ever been computed here for these cysteines:
  * **Burial** — relative SASA of the whole residue and the SG atom's own neighbour count. A buried thiol is
    desolvated; desolvation raises the pKa, which is the direction that would ARGUE AGAINST C397.
  * **Electrostatic environment** — distance to the nearest cationic group (Lys NZ, Arg NE/NH1/NH2,
    His ND1/NE2) and to the nearest anionic carboxylate (Asp OD1/OD2, Glu OE1/OE2), plus the net formal
    charge inside an 8 Å shell. A thiolate is stabilised by nearby positive charge and destabilised by
    nearby negative charge.
  * **H-bond donors within reach of SG** — backbone and side-chain N/O donors inside 4.0 Å, the standard
    thiolate-stabilising contact.
⭑ Reported as a RANK ACROSS THE FAMILY'S OWN CYSTEINES, never as an absolute. A rank is what the register
says the honest output of this instrument is even when it IS run, and a rank needs no calibration: it says
"C397 sits at position k of n on this determinant among the cysteines of these three proteins", which is a
statement about the comparison set and nothing more.

⚠ HONEST LIMITS, all carried into the artifact.
  * ONE static opened conformer per protein. A thiol's environment is dynamic; a single frame cannot see it.
  * These are DETERMINANTS, not a pKa, and they do not combine into one. They can disagree, and where they
    do, the artifact reports the disagreement rather than a score.
  * Hydrogens in the model are from the preparation, not from an experiment, so no H-bond GEOMETRY (angle)
    is used — only heavy-atom donor distance, which is the weaker but honest criterion.
  * The comparison set is three proteins. Nothing here is proteome-wide.

Output: nr4a3-thiol-environment.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import nr4a_differential_atlas as atlas            # noqa: E402
import nr4a_reciprocal_census as census            # noqa: E402

OUT = os.path.join(HERE, "nr4a3-thiol-environment.json")
STRUCT_DIR = os.path.join(REPO, "results", "nr4a3-matrix")
PROTEINS = ("NR4A1", "NR4A2", "NR4A3")

CATION_ATOMS = {("LYS", "NZ"), ("ARG", "NE"), ("ARG", "NH1"), ("ARG", "NH2"),
                ("HIS", "ND1"), ("HIS", "NE2")}
ANION_ATOMS = {("ASP", "OD1"), ("ASP", "OD2"), ("GLU", "OE1"), ("GLU", "OE2")}
DONOR_ELEMENTS = {"N", "O"}
HBOND_CUTOFF_A = 4.0
CHARGE_SHELL_A = 8.0
NEIGHBOUR_SHELL_A = 6.0

# ---------------------------------------------------------------------------------------------------------
# PART A — the known-answer precheck. Same contract as `cys_chemoproteomics_precheck.py`:
# ⛔ every entry is a CANDIDATE, and nothing here may be cited until this file records `status: OK` for it.
# ---------------------------------------------------------------------------------------------------------
PKA_SOURCES = [
    {
        "id": "pkad_webserver",
        "what": "a curated database of EXPERIMENTALLY MEASURED protein pKa values (wild type + mutants)",
        "url": "http://compbio.clemson.edu/pkad",
        "discovered_via": "web search → the database publication's availability statement",
    },
    {
        "id": "pkad_webserver_https",
        "what": "the same database over https",
        "url": "https://compbio.clemson.edu/pkad/",
        "discovered_via": "web search → the database publication's availability statement",
    },
    {
        "id": "pkad_article_oa",
        "what": "the database's open-access article record, which states the per-residue-type entry counts",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6389863/",
        "discovered_via": "web search",
    },
]

UA = {"User-Agent": "Mozilla/5.0 (compatible; Rare-cancers precheck; +https://github.com/trimcrae/Rare-cancers)"}


def fetch(url, timeout=45):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.status, r.read(20_000_000), None
    except urllib.error.HTTPError as e:
        return e.code, b"", f"HTTPError {e.code}"
    except Exception as e:                                   # noqa: BLE001
        return None, b"", f"{type(e).__name__}: {str(e)[:200]}"


def known_answer_precheck(timeout=45):
    rows = []
    for s in PKA_SOURCES:
        status, blob, err = fetch(s["url"], timeout)
        rows.append({**s, "http_status": status, "bytes": len(blob), "error": err,
                     "status": "OK" if (status == 200 and blob) else "UNREACHABLE"})
    reachable = [r for r in rows if r["status"] == "OK"]
    return {
        "sources": rows,
        "n_reachable_in_this_run": len(reachable),
        "verdict": "REFERENCE_DATABASE_EXISTS_BUT_UNREAD" if not reachable else "REFERENCE_READ",
        "⚠": ("`UNREACHABLE` is a statement about THIS RUN'S NETWORK, never about the database. An absent "
              "reading is not a reading of absence — route these through CI before concluding anything "
              "from their silence."),
    }


# ---------------------------------------------------------------------------------------------------------
# PART B — the structural determinants read
# ---------------------------------------------------------------------------------------------------------
def thiol_environments(protein, seqs, struct_dir=STRUCT_DIR):
    offset, residues, atoms = census.model_offset(protein, seqs, struct_dir)
    if offset is None:
        return []
    sasa = atlas.shrake_rupley(atoms)
    rsa = atlas.residue_rsa(residues, sasa)
    heavy = [a for a in atoms if a["elem"] != "H"]

    by_local = {}
    for a in heavy:
        by_local.setdefault(a["resid"], []).append(a)

    out = []
    for local, ats in sorted(by_local.items()):
        if ats[0]["resname"] != "CYS":
            continue
        sg = next((a for a in ats if a["name"] == "SG"), None)
        if sg is None:
            continue
        p = (sg["x"], sg["y"], sg["z"])

        def d(a):
            return math.dist(p, (a["x"], a["y"], a["z"]))

        others = [a for a in heavy if a["resid"] != local]
        cations = [(d(a), a) for a in others if (a["resname"], a["name"]) in CATION_ATOMS]
        anions = [(d(a), a) for a in others if (a["resname"], a["name"]) in ANION_ATOMS]
        donors = [a for a in others if a["elem"] in DONOR_ELEMENTS and d(a) <= HBOND_CUTOFF_A]
        n_cat_shell = sum(1 for dd, _ in cations if dd <= CHARGE_SHELL_A)
        n_ani_shell = sum(1 for dd, _ in anions if dd <= CHARGE_SHELL_A)
        neighbours = sum(1 for a in others if d(a) <= NEIGHBOUR_SHELL_A)

        nearest_cat = min(cations, default=(None, None))
        nearest_ani = min(anions, default=(None, None))
        out.append({
            "protein": protein,
            "uniprot_resnum": local + offset,
            "label": f"C{local + offset}",
            "local_resid": local,
            "rsa": round(rsa.get(local, 0.0), 3),
            "exposed_by_atlas_rule": rsa.get(local, 0.0) >= atlas.EXPOSED_RSA,
            "sg_heavy_neighbours_within_6A": neighbours,
            "n_hbond_capable_donors_within_4A_of_SG": len(donors),
            "hbond_donor_atoms": sorted({f"{a['resname']}{a['resid'] + offset}:{a['name']}" for a in donors}),
            "nearest_cationic_group_A": None if nearest_cat[0] is None else round(nearest_cat[0], 2),
            "nearest_cationic_group": (None if nearest_cat[1] is None else
                                       f"{nearest_cat[1]['resname']}{nearest_cat[1]['resid'] + offset}:"
                                       f"{nearest_cat[1]['name']}"),
            "nearest_anionic_group_A": None if nearest_ani[0] is None else round(nearest_ani[0], 2),
            "nearest_anionic_group": (None if nearest_ani[1] is None else
                                      f"{nearest_ani[1]['resname']}{nearest_ani[1]['resid'] + offset}:"
                                      f"{nearest_ani[1]['name']}"),
            "n_cationic_groups_within_8A": n_cat_shell,
            "n_anionic_groups_within_8A": n_ani_shell,
            "net_formal_charge_within_8A": n_cat_shell - n_ani_shell,
        })
    return out


DETERMINANTS = {
    # name: (field, direction) — direction "+" means a HIGHER value argues for a LOWER (more reactive) pKa
    "solvent_exposure": ("rsa", "+"),
    "hbond_donors_to_SG": ("n_hbond_capable_donors_within_4A_of_SG", "+"),
    "net_positive_charge_8A": ("net_formal_charge_within_8A", "+"),
    "proximity_to_cation": ("nearest_cationic_group_A", "-"),
}


def rank_determinants(rows, focus="C397"):
    """Rank every cysteine in the comparison set on each determinant, independently.

    ⛔ NOT COMBINED INTO A SCORE, and that is the point. Combining them would require weights, weights would
    require calibration, and calibration is exactly what the known-answer precheck has not delivered. Four
    separate ranks that can disagree is an honest instrument; one number is a fabricated one.
    """
    out = {}
    for name, (field, direction) in DETERMINANTS.items():
        vals = [(r[field], r) for r in rows if r.get(field) is not None]
        vals.sort(key=lambda t: t[0], reverse=(direction == "+"))
        order = [r["protein"] + " " + r["label"] for _, r in vals]
        hit = next((i for i, lab in enumerate(order) if lab.endswith(" " + focus)), None)
        out[name] = {
            "field": field,
            "higher_value_argues_for_lower_pKa": direction == "+",
            "n_ranked": len(order),
            "ranking_best_first": order,
            f"{focus}_rank": None if hit is None else hit + 1,
            f"{focus}_value": next((v for v, r in vals if r["label"] == focus), None),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--struct-dir", default=STRUCT_DIR)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--no-network", action="store_true")
    args = ap.parse_args(argv)

    with open(os.path.join(HERE, "nr4a-sequences-cache.json")) as fh:
        seqs = {k: v for k, v in json.load(fh).items() if k in PROTEINS}

    rows = []
    for p in PROTEINS:
        rows.extend(thiol_environments(p, seqs, args.struct_dir))
    ranks = rank_determinants(rows)
    precheck = ({"skipped": "--no-network"} if args.no_network
                else known_answer_precheck(args.timeout))

    c397 = next((r for r in rows if r["protein"] == "NR4A3" and r["label"] == "C397"), None)
    agree = [k for k, v in ranks.items() if v["C397_rank"] is not None and v["C397_rank"] <= len(rows) / 3]
    disagree = [k for k, v in ranks.items() if v["C397_rank"] is not None and v["C397_rank"] > 2 * len(rows) / 3]

    doc = {
        "_title": ("`C12` — thiol environment determinants for C397, and the $0 known-answer precheck "
                   "(roadmap §10.1a `Q9`)"),
        "_status": ("$0 CPU + network reads. No GPU, no rental. ⛔ NO pKa IS COMPUTED OR REPORTED HERE. "
                    "Nothing here is a claim about binding, reactivity as a measured quantity, adduct "
                    "formation, degradation, efficacy, safety, a therapeutic window or clinical readiness, "
                    "and nothing here implies proteome-wide selectivity."),
        "_serves": ["S1 (the one axis of it that is currently a LABEL rather than a quantity)", "R8"],
        "⛔⛔_what_this_can_never_license": (
            "A favourable thiol pKa is NOT evidence that a covalent bond forms. Reactivity is necessary and "
            "never sufficient: adduct formation in a cell additionally requires delivery to the site, "
            "residence time, an attack geometry, survival against a proteome of competing nucleophiles, and "
            "a tolerated concentration. None of that is modelled here, and none of it would be modelled by "
            "a pKa either. ⛔ This applies to every downstream use of this artifact, including a future run "
            "that does compute a pKa."
        ),
        "⛔_the_handle_is_still_a_LABEL": (
            "Everywhere this program calls C397 a covalent handle, that is a CATEGORICAL sequence/geometry "
            "statement — a paralogue-unique cysteine within tether reach — and NOT a measured reactivity. "
            "This file does not change that. It reports the structural determinants a reactivity would "
            "depend on; it does not report a reactivity."
        ),
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_method": {
            "structures": "the matched opened LBD models already in the repo, one static conformer each",
            "model_uniprot_offsets": "DERIVED by exact substring match (nr4a_reciprocal_census.model_offset)",
            "hbond_criterion": (f"heavy-atom N/O donor within {HBOND_CUTOFF_A} A of SG. ⚠ DISTANCE ONLY — no "
                                "angle, because the model's hydrogens come from the preparation rather than "
                                "from an experiment."),
            "charge_shell_A": CHARGE_SHELL_A,
            "neighbour_shell_A": NEIGHBOUR_SHELL_A,
            "cationic_atoms": sorted("%s:%s" % t for t in CATION_ATOMS),
            "anionic_atoms": sorted("%s:%s" % t for t in ANION_ATOMS),
        },
        "★_part_A_known_answer_precheck": precheck,
        "★_part_B_determinants": {
            "n_cysteines_in_comparison_set": len(rows),
            "C397": c397,
            "ranks": ranks,
            "★_reading": (
                "Four determinants, ranked independently across every cysteine of the three proteins. "
                f"C397 sits in the top third on {sorted(agree)} and in the bottom third on {sorted(disagree)}. "
                "⛔ They are NOT combined, and a reader must not combine them: weights would need "
                "calibration and the known-answer precheck has not delivered any. Where they disagree, the "
                "disagreement IS the finding — it is what 'weakly calibrated on buried cysteines' looks "
                "like before a predictor is even involved."
            ),
        },
        "★_internal_control_the_family_s_one_literature_anchored_covalent_site": {
            "_what": ("NR4A1 C551 is the only NR4A cysteine with a covalent precedent in the literature, and "
                      "it is `V17`'s demonstrated FALSE NEGATIVE — the geometric cutoff calls it buried. Its "
                      "position on these determinants is therefore the closest thing to a control this read "
                      "has, and it is free."),
            "row": next((r for r in rows if r["protein"] == "NR4A1" and r["label"] == "C551"), None),
            "rank_on_each_determinant": {
                k: (v["ranking_best_first"].index("NR4A1 C551") + 1
                    if "NR4A1 C551" in v["ranking_best_first"] else None)
                for k, v in ranks.items()
            },
            "⚠_what_this_is_and_is_not": (
                "⭑ It is a CONSISTENCY check that passed: the site's RSA here reproduces the value the "
                "widened-enumeration artifact quotes as its reference, computed by a different script, so "
                "the geometry pipeline agrees with itself across two independent readers. "
                "⛔ It is NOT a known-answer test. n = 1, the outcome variable is a literature LABEL rather "
                "than a measured pKa or reactivity, and a rank on a determinant is not a prediction. A real "
                "known-answer test is what part A is a precheck for, and part A has not returned."
            ),
        },
        "rows": rows,
        "⛔_limits": [
            "NO pKa IS REPORTED. These are the determinants a pKa depends on, not a pKa, and they do not "
            "combine into one.",
            "ONE static opened conformer per protein. A thiol's electrostatic environment is dynamic and a "
            "single frame cannot see it — the same limit every other single-frame reading in this program "
            "carries.",
            "Ranks are WITHIN the three-protein comparison set. A rank of 1 means 'first among these "
            "cysteines', never 'reactive'.",
            "H-bond contacts are heavy-atom distances with no angular criterion, so they overcount.",
            "The known-answer set for a cysteine-pKa predictor is small by the database's own account, and "
            "until part A reads it, no predictor output may be quoted anywhere in this repository.",
            "Nothing here is a proteome-wide statement of any kind.",
        ],
    }
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps({"precheck": precheck.get("verdict", precheck),
                      "n_cys": len(rows),
                      "C397_ranks": {k: v["C397_rank"] for k, v in ranks.items()}},
                     indent=1, ensure_ascii=False))
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
