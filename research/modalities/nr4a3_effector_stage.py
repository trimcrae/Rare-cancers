#!/usr/bin/env python3
"""
TRANSCRIPTIONAL-EFFECTOR ARM STAGING for the TCIP reach enumeration — the one input `nr4a3_tcip_reach.py`
does not have, staged the same way the E3 arms were: discovery by UniProt accession, never by a remembered
PDB ID.

WHY THIS EXISTS. `nr4a3_tcip_reach.py` consumes two points per cell: `a` (the warhead exit-vector anchor on
the NR4A3 side) and `b` (the second terminus's ligand exit atom). `b` is not typeable — it comes out of
`nr4a3_basin_search.sample_placements`, which needs a staged RIGID BODY: a registry record carrying
`receptor_pdb` coordinates on disk and a `ligand.exit_atom_xyz`. Counted by that module's own
`effector_arm_census`, this repository staged FOUR such bodies (vhl 5T35, crbn 6BOY, birc2 4HY4, mdm2 6Q9L)
and every one of them is an E3 ubiquitin-ligase recruiter. The two used at effector size (birc2, mdm2) are
SIZE-AND-SHAPE PROXIES and the route memo forbids naming an effector on their basis. So every TCIP statement
the repository can make today is about a size class. This script stages the missing kind of body.

WHICH EFFECTOR, AND ON WHAT EVIDENCE. Read out of the route's own motivating paper rather than recalled:
Bond, Golden, DiGiovanni et al., "Rewiring the fusion oncoprotein EWSR1::FLI1 in Ewing sarcoma with bivalent
small molecules", J Am Chem Soc 2025;147(49):44739-44758, doi 10.1021/jacs.5c05634 (PMC12851799; the CI-fetched
full text is committed on the `literature-cache` branch at
`literature/emc-post-degrader-options/tcip_ewsfli1_jacs_pmc.txt`). Its abstract states the molecule
"recruits FKBP12(F36V)-tagged EWSR1::FLI1 to DNA sites bound by the transcriptional regulator BCL6", and its
results section states EB-TCIP is "BAK-04-212, a bivalent molecule comprised of OAP and BI3812" — BI3812
being a BCL6 ligand. The recruited transcriptional machinery in the prior art is therefore **BCL6**, a
BTB/POZ zinc-finger transcriptional REPRESSOR, engaged through its BTB-domain lateral groove. That paper also
states the reason it was chosen, which is exactly this script's hard constraint: "known chemical matter,
validated exit vector, and assay availability".

⚠ THE HARD CONSTRAINT IS THE LIGAND, NOT THE PROTEIN. A second terminus with no small-molecule handle cannot
supply `b` at all, however interesting the protein is. That is what rules out most transcriptional effectors
(and it is why `nr4a3_tcip_reach.effector_arm_census`'s guess that "the TCIP literature's effector handle is a
bromodomain-class ligand" is corrected here against the source: for EB-TCIP it is a BCL6 BTB ligand).

⛔ AND THE BTB DOMAIN IS WHY THIS IS NOT `nr4a3_e3_stage.py` WITH A DIFFERENT ACCESSION. That script's
`select_assembly_copy` takes ONE chain per protein — correct for VHL/CRBN/BIRC2/MDM2, where the ligand site
sits inside a single chain. The BCL6 BTB lateral groove is formed BETWEEN the two protomers of an obligate
homodimer, so a one-chain body would be half a binding site: the excluded volume would be understated and the
derived exit vector could point into the protomer that was dropped, and every distance downstream would still
look reasonable. That is the silent-success class this repository keeps being bitten by, so the body here is
DERIVED FROM THE LIGAND'S OWN CONTACTS (which chains does the chosen ligand actually touch?) and the choice is
reported per chain rather than assumed.

NETWORK. RCSB is 403'd at CONNECT by the dev sandbox's egress proxy, so this runs on a GitHub Actions runner
(CLAUDE.md §6). Pure stdlib urllib — no pip.

WHAT THIS IS NOT. Staging a body is not evidence that anything binds it, that a bivalent molecule engaging it
would form, that transcription would change, or that any of this is selective, efficacious or clinically
relevant. It is an excluded volume and one atom's coordinates.

Usage
    python nr4a3_effector_stage.py --plan                  # offline: print exactly what would be queried
    python nr4a3_effector_stage.py --arms bcl6             # CI: discover, verify, download, stage, write
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                      # noqa: E402
import nr4a3_e3_stage as E3                 # noqa: E402  — HTTP, PDB parsing and the exit-vector derivation

STAGE_DIR = os.path.join(REPO, "results", "nr4a3-effector-arms")
REGISTRY = os.path.join(HERE, "nr4a3-effector-arm-registry.json")

# The ligand-contact test that defines the body. Same 4.5 A cutoff `nr4a3_e3_stage.pick_ligand` already uses
# for "is this ligand bound to the recruiter", reused rather than re-picked so the two staging paths agree.
LIGAND_CONTACT_A = 4.5
MIN_LIGAND_ATOMS_PER_CHAIN = 3               # below this a "contact" is one atom brushing a side chain
INTERFACE_CONTACT_A = 6.0                    # chain-chain contact, as in nr4a3_e3_stage._chains_touch
MIN_INTERFACE_RESIDUES = 30                  # a real domain-swap/dimer interface, not crystal packing
AMBIGUOUS_INTERFACE_RATIO = 1.20             # two partner candidates this close = refuse, do not guess

# Effector specs. `accession` IDENTIFIES the protein; it is not a structure claim. `max_body_chains` is the
# stoichiometry of the LIGAND-BINDING UNIT and is checked against the coordinates, never trusted.
EFFECTORS = {
    "bcl6": {
        "effector": "BCL6",
        "accession": "P41182",
        "partner_class": "transcriptional effector",
        "effector_role": "transcriptional repressor (BTB/POZ zinc-finger); the BTB domain is the "
                         "corepressor-recruiting module and carries the ligandable lateral groove",
        "chemical_handle": "BTB lateral-groove ligands of the BI-3802 / BI-3812 series",
        "max_body_chains": 2,
        "why_this_stoichiometry": "the BTB lateral groove is formed between two protomers, so the "
                                  "ligand-binding unit is a dimer; ASSERTED HERE, MEASURED BELOW as the "
                                  "number of chains the chosen ligand actually contacts",
        "evidence": {
            "doi": "10.1021/jacs.5c05634",
            "pmc": "PMC12851799",
            "quote_recruits": "recruits FKBP12(F36V)-tagged EWSR1::FLI1 to DNA sites bound by the "
                              "transcriptional regulator BCL6",
            "quote_ligand": "BAK-04-212, a bivalent molecule comprised of OAP and BI3812",
            "quote_why_chosen": "known chemical matter, validated exit vector, and assay availability",
            "cached_fulltext": "literature-cache:literature/emc-post-degrader-options/"
                               "tcip_ewsfli1_jacs_pmc.txt",
            "⚠_citation_gate": "EV-EB-TCIP-2025 has NOT cleared this repository's `verify-refs` gate. It is "
                               "cited here as the reason an effector was CHOSEN — a staging decision — and "
                               "supplies no number to any result.",
        },
    },
    # A second transcriptional-machinery body, staged for the same reason the size comparison needed two
    # bodies per class: one arm cannot tell an effector result from that arm's own shape. BRD4's first
    # bromodomain is the recruited transcriptional co-activator in the TCIP series this route descends from,
    # and JQ1-class chemical matter is the most thoroughly solved small-molecule handle in the whole field.
    "brd4_bd1": {
        "effector": "BRD4",
        "accession": "O60885",
        "partner_class": "transcriptional effector",
        "effector_role": "BET-family transcriptional co-activator / acetyl-lysine reader; bromodomain 1 is "
                         "the ligandable module",
        "chemical_handle": "acetyl-lysine-competitive bromodomain ligands of the JQ1 / I-BET series",
        "max_body_chains": 1,
        "why_this_stoichiometry": "a bromodomain's acetyl-lysine pocket sits inside a single chain",
        "evidence": {
            "role_in_the_TCIP_series": "BRD4 is the transcriptional co-activator half of the original TCIP "
                                       "bivalent series that EB-TCIP descends from",
            "⚠": "staged as a SECOND transcriptional-effector body so a single body's shape cannot be "
                 "mistaken for an effector-class result. No claim is made that BRD4 is the right effector "
                 "for NR4A3.",
        },
    },
}


# ---------------------------------------------------------------------------------------------------------
# Body selection — derived from the ligand's own contacts
# ---------------------------------------------------------------------------------------------------------
def _chain_atoms(prot, chain):
    return [a["xyz"] for a in prot if a["chain"] == chain]


def ligand_chain_contacts(prot, chains, lig_atoms, cutoff=LIGAND_CONTACT_A):
    """For each candidate chain, how many ligand heavy atoms lie within `cutoff` of it. Exact distances."""
    out = {}
    for c in sorted(chains):
        pts = _chain_atoms(prot, c)
        if not pts:
            continue
        n = sum(1 for a in lig_atoms if E3._min_dist_exact(a["xyz"], pts) <= cutoff)
        if n:
            out[c] = n
    return out


def interface_residues(prot, c1, c2, cutoff=INTERFACE_CONTACT_A):
    """Number of residues of `c1` with any heavy atom within `cutoff` of `c2`. A size, not a boolean, because
    the decision below has to DISCRIMINATE a biological dimer from crystal packing rather than just detect
    touching."""
    a2 = _chain_atoms(prot, c2)
    if not a2:
        return 0
    f = G.SquaredDistanceField(a2, cell=1.5, clamp=8.0)
    hit = set()
    for a in prot:
        if a["chain"] != c1:
            continue
        if f.min_dist(a["xyz"]) <= cutoff:
            hit.add((a["resid"], a["icode"]))
    return len(hit)


def select_ligand_body(prot, accession_chains, lig, max_chains):
    """The rigid body = the chains the CHOSEN LIGAND actually touches, completed to the declared
    stoichiometry only through a measured, unambiguous interface.

    Returns (chains, info). `info` always carries the per-chain evidence, whether or not it succeeded, so a
    refusal can be read as easily as an acceptance.
    """
    lig_atoms = [{"xyz": tuple(a["xyz"])} for a in lig["atoms"]]
    contacts = ligand_chain_contacts(prot, accession_chains, lig_atoms)
    touching = sorted((c for c, n in contacts.items() if n >= MIN_LIGAND_ATOMS_PER_CHAIN),
                      key=lambda c: -contacts[c])
    info = {"ligand_atom_contacts_per_chain": contacts,
            "chains_the_ligand_touches": touching,
            "declared_max_body_chains": max_chains}
    if not touching:
        info["ok"] = False
        info["reason"] = "the chosen ligand touches no chain of this accession"
        return None, info

    if len(touching) >= max_chains:
        sel = touching[:max_chains]
        info.update({"ok": True, "selection_rule": "chains the ligand itself contacts",
                     "n_chains_the_ligand_spans": len(touching), "selected": sel,
                     "completed_through_interface": False})
        return sel, info

    # The ligand touches fewer chains than the declared ligand-binding unit. Complete it ONLY through a
    # measured interface, and refuse if two candidates are too close to call.
    sel = list(touching)
    partners = []
    for c in sorted(set(accession_chains) - set(sel)):
        n = max(interface_residues(prot, c, s) for s in sel)
        partners.append({"chain": c, "interface_residues": n})
    partners.sort(key=lambda p: -p["interface_residues"])
    info["candidate_partner_chains"] = partners
    while len(sel) < max_chains and partners:
        top = partners[0]
        if top["interface_residues"] < MIN_INTERFACE_RESIDUES:
            info["ok"] = False
            info["reason"] = ("no partner chain forms an interface of >= %d residues with the "
                              "ligand-contacting chain(s); best is %s at %d"
                              % (MIN_INTERFACE_RESIDUES, top["chain"], top["interface_residues"]))
            return None, info
        if len(partners) > 1 and partners[1]["interface_residues"] > 0 and (
                top["interface_residues"] / partners[1]["interface_residues"] < AMBIGUOUS_INTERFACE_RATIO):
            info["ok"] = False
            info["reason"] = ("partner chain is AMBIGUOUS: %s (%d residues) vs %s (%d) are within %.2fx, so "
                              "the biological unit cannot be told from crystal packing — refused rather than "
                              "guessed" % (top["chain"], top["interface_residues"], partners[1]["chain"],
                                           partners[1]["interface_residues"], AMBIGUOUS_INTERFACE_RATIO))
            return None, info
        sel.append(top["chain"])
        partners = partners[1:]
    if len(sel) < max_chains:
        info["ok"] = False
        info["reason"] = "not enough chains of this accession to build the declared ligand-binding unit"
        return None, info
    info.update({"ok": True,
                 "selection_rule": "ligand-contacting chain(s), completed through a measured interface",
                 "n_chains_the_ligand_spans": len(touching), "selected": sel,
                 "completed_through_interface": True})
    return sel, info


# ---------------------------------------------------------------------------------------------------------
# Candidate ranking — stated, recorded, and never a silent first-hit
# ---------------------------------------------------------------------------------------------------------
def rank_key(cand, spec):
    """Stated preference order over entries that passed EVERY hard check.

    1. the ligand spans the declared ligand-binding unit (for BCL6: a groove ligand that touches both
       protomers is the one the chemical series actually occupies);
    2. more ligand heavy atoms — a fragment has an exit vector too, but a lead-like ligand's is the one a
       linker would be grown from;
    3. better resolution.
    """
    spans = 1 if cand["body"]["n_chains_the_ligand_spans"] >= spec["max_body_chains"] else 0
    res = cand["entry"]["resolution_A"]
    return (-spans, -cand["ligand"]["n_heavy"], res if res is not None else 99.0)


def stage_effector(arm_id, spec, out_dir, log, max_candidates=25, keep=8):
    rec = {"arm_id": arm_id, "recruiter": spec["effector"], "crl": None,
           "partner_class": spec["partner_class"], "effector_role": spec["effector_role"],
           "chemical_handle": spec["chemical_handle"], "evidence_for_choosing_this_effector": spec["evidence"],
           "status": "pending", "provenance": {}, "rejected": [], "ring": None, "intact_assembly": None,
           "_not_an_E3": "This arm is NOT a ubiquitin-ligase recruiter. It carries no RING, no cullin and no "
                         "transfer anchor, and nothing about ubiquitin transfer may be read off it. "
                         "`nr4a3_tcip_reach` measures that the acceptance test ignores those fields."}

    ids = E3.search_entries([spec["accession"]], rows=max_candidates)
    log(f"[effstage] {arm_id}: RCSB returned {len(ids)} entries for accession {spec['accession']} "
        f"(best resolution first): {ids[:12]}")
    rec["provenance"]["discovery"] = {
        "method": "RCSB search by UniProt accession; NO PDB ID is supplied by this script",
        "accession": spec["accession"],
        "n_entries_returned": len(ids),
        "entries_returned": ids,
    }

    passed = []
    for pdb in ids:
        try:
            comp = E3.entry_composition(pdb)
        except Exception as e:                                          # noqa: BLE001
            rec["rejected"].append({"pdb": pdb, "reason": f"metadata fetch failed: {e}"})
            continue
        chains = set(comp["chains_by_accession"].get(spec["accession"], []))
        if not chains:
            rec["rejected"].append({"pdb": pdb, "reason": "re-verification failed: the downloaded metadata "
                                                          "does not carry the required accession"})
            continue
        try:
            text = E3._get(E3.FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
        except E3.NotAvailable as e:
            rec["rejected"].append({"pdb": pdb, "reason": str(e)})
            continue
        except Exception as e:                                          # noqa: BLE001
            rec["rejected"].append({"pdb": pdb, "reason": f"coordinate fetch failed: {e}"})
            continue
        prot, het = E3.parse_pdb_text(text)
        present = {a["chain"] for a in prot}
        chains = {c for c in chains if c in present}
        if not chains:
            rec["rejected"].append({"pdb": pdb, "reason": "no annotated chain of this accession is present "
                                                          "in the deposited PDB-format coordinates"})
            continue
        # First pass: the ligand, chosen against ALL chains of this accession, with recruiter contact
        # required exactly as the E3 path requires it.
        lig = E3.pick_ligand(prot, het, chains, chains)
        if lig is None:
            rec["rejected"].append({"pdb": pdb, "reason": "no bound ligand >= %d heavy atoms in contact "
                                                          "(<= 4.5 A) with this protein itself"
                                                          % E3.MIN_LIGAND_HEAVY})
            continue
        body, binfo = select_ligand_body(prot, chains, lig, spec["max_body_chains"])
        if body is None:
            rec["rejected"].append({"pdb": pdb, "reason": "body selection: " + binfo["reason"],
                                    "body_evidence": binfo})
            continue
        # Second pass: re-derive the exit vector against the SELECTED body only. The first pass used every
        # annotated chain, which for a multi-copy asymmetric unit is not the body we keep — and the exit
        # atom is defined as the ligand atom furthest from the body, so it must be measured on the body that
        # is actually written out.
        lig2 = E3.pick_ligand(prot, het, set(body), set(body))
        if lig2 is None:
            rec["rejected"].append({"pdb": pdb, "reason": "the ligand does not survive re-derivation against "
                                                          "the selected body chains"})
            continue
        passed.append({"pdb_id": pdb, "entry": comp, "ligand": lig2, "body": binfo,
                       "body_chains": sorted(body), "text": text, "prot": prot})
        log(f"[effstage] {arm_id}: PASSED {pdb} ({comp['resolution_A']} A) body {sorted(body)} "
            f"ligand {lig2['het_code']} n_heavy={lig2['n_heavy']} spans "
            f"{binfo['n_chains_the_ligand_spans']} chain(s) exit atom {lig2['exit_atom_name']} "
            f"exposure {lig2['exit_atom_dist_to_receptor_A']} A")
        if len(passed) >= keep:
            break

    rec["candidates_considered"] = [
        {"pdb_id": c["pdb_id"], "resolution_A": c["entry"]["resolution_A"], "title": c["entry"]["title"],
         "method": c["entry"]["method"], "body_chains": c["body_chains"],
         "n_chains_the_ligand_spans": c["body"]["n_chains_the_ligand_spans"],
         "ligand_het": c["ligand"]["het_code"], "ligand_n_heavy": c["ligand"]["n_heavy"],
         "exit_atom": c["ligand"]["exit_atom_name"],
         "exit_atom_exposure_A": c["ligand"]["exit_atom_dist_to_receptor_A"]}
        for c in sorted(passed, key=lambda c: rank_key(c, spec))]
    if not passed:
        rec["status"] = "FAILED_no_verified_ligand_bound_entry"
        return rec

    best = sorted(passed, key=lambda c: rank_key(c, spec))[0]
    body_chains = set(best["body_chains"])
    body_atoms = [a for a in best["prot"] if a["chain"] in body_chains]
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{arm_id}-receptor.pdb")
    with open(path, "w") as fh:
        fh.write("REMARK   1 STAGED BY nr4a3_effector_stage.py FROM RCSB %s CHAINS %s\n"
                 % (best["pdb_id"], "".join(sorted(body_chains))))
        fh.write("REMARK   2 TRANSCRIPTIONAL EFFECTOR (%s) - NOT AN E3 UBIQUITIN-LIGASE RECRUITER\n"
                 % spec["effector"])
        for i, a in enumerate(body_atoms, 1):
            fh.write("ATOM  %5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (i, a["name"][:4], a["resname"], a["chain"], a["resid"],
                        a["xyz"][0], a["xyz"][1], a["xyz"][2], a["elem"][:2]))
    rec["receptor_pdb"] = os.path.relpath(path, REPO)
    rec["ligand"] = best["ligand"]
    rec["assembly_copy"] = {"selected_chains": sorted(body_chains), "selection": best["body"]}
    rec["provenance"]["receptor_entry"] = best["entry"]
    rec["n_residues_written"] = len({(a["chain"], a["resid"], a["icode"]) for a in body_atoms})
    rec["n_atoms_written"] = len(body_atoms)
    rec["status"] = "OK"
    log(f"[effstage] {arm_id}: CHOSE {best['pdb_id']} -> {rec['receptor_pdb']} "
        f"({rec['n_residues_written']} residues, {rec['n_atoms_written']} atoms); "
        f"exit atom {best['ligand']['exit_atom_name']} at {best['ligand']['exit_atom_xyz']}")
    return rec


def self_check(rec, log):
    """Re-read what was written and confirm it is loadable as a rigid body by the consumer that will use it.

    ⚠ A POPULATED FIELD IS NOT A MEASURED ONE (CLAUDE.md §4). `status: OK` and a filled `exit_atom_xyz` are
    exactly what a defaulted record would also look like, so the check that matters is the one only a real
    staging can pass: the coordinate file parses, the exit atom LANDS ON a heavy atom of the deposited ligand,
    and `nr4a3_basin_search.load_arm_from_registry` turns the pair into a body without touching the network.
    """
    import nr4a3_basin_search as BS                                     # noqa: PLC0415
    out = {"arm_id": rec["arm_id"]}
    try:
        arm = BS.load_arm_from_registry(rec)
    except Exception as e:                                              # noqa: BLE001
        out.update({"ok": False, "reason": f"{type(e).__name__}: {e}"})
        log(f"[effstage] {rec['arm_id']}: SELF-CHECK FAILED — {out['reason']}")
        return out
    exit_xyz = tuple(rec["ligand"]["exit_atom_xyz"])
    d_lig = min(G.dist(exit_xyz, tuple(a["xyz"])) for a in rec["ligand"]["atoms"])
    near_ca = min(G.dist(exit_xyz, p) for p in arm["ca"])
    out.update({
        "ok": True,
        "n_residues_loaded": arm["n_ca"],
        "chains_loaded": arm["chains"],
        "exit_atom_is_a_deposited_ligand_atom": d_lig == 0.0,
        "exit_atom_to_nearest_ligand_atom_A": round(d_lig, 3),
        "exit_atom_to_nearest_body_CA_A": round(near_ca, 2),
        "ring_is_absent": arm["ring"] is None,
        "transfer_anchor_is_absent": arm["tanchor"] is None,
        "_reading": "the staged record loads as a rigid body through the SAME consumer the reach enumeration "
                    "uses, and its anchor is an atom of the deposited ligand rather than a typed number",
    })
    log(f"[effstage] {rec['arm_id']}: self-check OK — {arm['n_ca']} residues, chains {arm['chains']}, "
        f"exit atom sits {out['exit_atom_to_nearest_ligand_atom_A']} A from the nearest deposited ligand "
        f"atom and {out['exit_atom_to_nearest_body_CA_A']} A from the nearest body CA")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--arms", default="bcl6", help="comma-separated ids from EFFECTORS")
    ap.add_argument("--out-dir", default=STAGE_DIR)
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--plan", action="store_true", help="offline: print the queries, touch no network")
    args = ap.parse_args(argv)

    ids = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in ids if a not in EFFECTORS]
    if unknown:
        raise SystemExit(f"unknown effector arm(s): {unknown}; known: {sorted(EFFECTORS)}")

    if args.plan:
        print("[effstage] OFFLINE PLAN — no network touched")
        for a in ids:
            s = EFFECTORS[a]
            print(f"  arm {a}: {s['effector']} — {s['effector_role']}")
            print(f"    query          : UniProt accession {s['accession']} (no PDB ID is supplied)")
            print(f"    chemical handle: {s['chemical_handle']}")
            print(f"    ligand-binding unit: {s['max_body_chains']} chain(s) — {s['why_this_stoichiometry']}")
            print(f"    evidence       : {json.dumps(s['evidence'])[:300]}")
        return 0

    os.makedirs(args.out_dir, exist_ok=True)
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    arms = {}
    for a in ids:
        try:
            arms[a] = stage_effector(a, EFFECTORS[a], args.out_dir, log)
        except Exception as e:                                          # noqa: BLE001
            import traceback
            log(f"[effstage] arm {a} FAILED: {type(e).__name__}: {e}")
            log(traceback.format_exc())
            arms[a] = {"arm_id": a, "status": f"FAILED_{type(e).__name__}", "error": str(e)}
        if arms[a].get("status") == "OK":
            arms[a]["self_check"] = self_check(arms[a], log)
            if not arms[a]["self_check"]["ok"]:
                arms[a]["status"] = "FAILED_self_check"

    out = {
        "_title": "Transcriptional-effector second-terminus arm registry for the TCIP reach enumeration",
        "_question": "does this repository hold a staged rigid body for a NAMED transcriptional effector, so "
                     "the reach enumeration can speak about an effector rather than a size class?",
        "_method": "RCSB discovery by UniProt accession (never by a remembered PDB ID), composition "
                   "re-verified against the same accession after download, the rigid body DERIVED from the "
                   "chains the chosen ligand actually contacts, and the exit vector derived by "
                   "nr4a3_e3_stage.pick_ligand against that body.",
        "_limits": [
            "One deposited conformer per effector. No ensemble, no dynamics, no induced fit.",
            "The body is the LIGAND-BINDING UNIT, not the full-length protein: a BTB domain is not BCL6 and "
            "a bromodomain is not BRD4. Everything outside the deposited construct is absent from the "
            "excluded volume, so the admitted space is an UPPER bound on what the full protein would allow.",
            "Nothing here is evidence that any of these effectors binds NR4A3, is recruited by any molecule, "
            "is retained on chromatin, or changes transcription. It is input staging: an excluded volume and "
            "one atom's coordinates.",
            "The citation that motivates the CHOICE of effector (10.1021/jacs.5c05634) has not cleared this "
            "repository's `verify-refs` gate. It supplies no number to any result — only the reason a "
            "protein was chosen.",
        ],
        "staged_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "arms": arms,
        "log": lines,
    }
    with open(args.registry, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[effstage] wrote {os.path.relpath(args.registry, REPO)}")
    for a, r in arms.items():
        print(f"[effstage] {a}: {r['status']}")
    return 0 if all(r.get("status") == "OK" for r in arms.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
