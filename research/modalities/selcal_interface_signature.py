#!/usr/bin/env python3
"""Does a STRUCTURE-ONLY readout separate the two paralogues, where the answer is known? ($0 CPU)

★★ WHY THIS IS THE SHORTEST ROUTE TO A JUSTIFIED SELECTIVITY CLAIM.
Every paralogue-selectivity statement in this program is an unvalidated prediction because no readout has
ever been shown to detect a paralogue difference where the answer is known. The endpoint the program uses
(E1, an interface-RMSD plateau under MD) has been tried and returned a NULL that later proved
uninterpretable. **But the published mechanism for this very pair is not a dynamical quantity at all.**
Kofink et al. 2022 (Nat Commun, PMC9551036), verbatim from `selcal_panel.REFERENCE`:

    "Represented are the key PPIs between VCB and SMARCA2BD/SMARCA4BD, highlighting the
     selectivity-inducing hydrogen bonding between Gln1469 of SMARCA2BD and VCB"

A hydrogen bond between two named partners is **visible in a deposited structure**. So the question "can a
readout of this program's kind see the paralogue difference?" can be asked of a static interface descriptor,
on the two crystals, for nothing — and it is a genuine known-answer test, because the expected answer was
published before this program existed and is not derived from anything here.

⛔ WHAT A PASS DOES AND DOES NOT LICENSE.
  · **PASS** — the descriptor recovers the published contact on the SMARCA2 arm and its absence on SMARCA4.
    That validates a STRUCTURAL selectivity readout against a known answer, and it is the first such control
    this program has. It says a paralogue-discriminating contact is *detectable from a ternary structure*.
  · ⛔ It does **not** validate E1, which is a different quantity, and it does **not** make any NR4A3
    prediction correct. Applying it to an NR4A3 ternary requires that ternary to be credible, which is a
    separate and currently failing question (`selcal-cofold-decompose.json`).
  · ⛔ And it is **one contact in one pair**. A descriptor that recovers one published H-bond has been shown
    to work once; that is the beginning of a validated readout, not the end of one.

⚠ NO HYDROGENS. Deposited X-ray structures at this resolution do not place them, so a "hydrogen bond" here
is the standard heavy-atom proxy — an N/O donor-acceptor pair within `HBOND_MAX_A` — and is labelled
`polar_contact` throughout rather than `hydrogen_bond`, so no reader can take geometry that was not measured.

⛔ Re-scores no leg, moves no verdict, amends no preregistration.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: Heavy-atom N/O separation counted as a polar contact. 3.5 A is the conventional donor-acceptor ceiling for
#: a hydrogen bond inferred without hydrogens; it is the field's number, not one chosen here, and it is stated
#: as a PROXY everywhere it is used.
HBOND_MAX_A = 3.5

#: Any-atom separation counted as an interface contact, imported so it means what it means everywhere else.
def contact_a():
    import selcal_cofold_validate as V
    return V.FNAT_CONTACT_A


#: Protein backbone atom names. Everything else on a residue is side chain.
BACKBONE = {"N", "CA", "C", "O", "OXT"}


def _polar(atom):
    return (atom.element or atom.name[:1]).upper() in ("N", "O")


def _sidechain(name):
    return name.strip().upper() not in BACKBONE


def residue_contacts(atoms, target_chain, e3_chains, cutoff=None, polar_cutoff=HBOND_MAX_A):
    """Per-target-residue contact record against the E3 chains. Pure geometry, no interpretation."""
    import numpy as np
    cutoff = contact_a() if cutoff is None else cutoff
    tgt = [a for a in atoms if a.chain == target_chain and not a.hetatm and a.is_heavy]
    e3 = [a for a in atoms if a.chain in e3_chains and not a.hetatm and a.is_heavy]
    if not tgt or not e3:
        return {}
    E = np.array([[a.x, a.y, a.z] for a in e3], dtype=float)
    e3_polar = np.array([_polar(a) for a in e3], dtype=bool)

    by_res = {}
    for a in tgt:
        by_res.setdefault((a.resseq, a.icode, a.resname), []).append(a)

    out = {}
    for (resseq, icode, resname), ats in sorted(by_res.items()):
        A = np.array([[x.x, x.y, x.z] for x in ats], dtype=float)
        d = np.sqrt(((A[:, None, :] - E[None, :, :]) ** 2).sum(axis=2))
        if d.min() > cutoff:
            continue
        rec = {"resname": resname, "resseq": resseq, "icode": icode,
               "min_dist_A": round(float(d.min()), 2),
               "n_contacts": int((d <= cutoff).sum()), "polar_contacts": []}
        a_polar = np.array([_polar(x) for x in ats], dtype=bool)
        mask = np.outer(a_polar, e3_polar) & (d <= polar_cutoff)
        for i, j in zip(*np.nonzero(mask)):
            rec["polar_contacts"].append({
                "target_atom": ats[i].name, "e3_chain": e3[j].chain,
                "e3_resname": e3[j].resname, "e3_resseq": e3[j].resseq, "e3_atom": e3[j].name,
                "distance_A": round(float(d[i, j]), 2),
                "target_sidechain": _sidechain(ats[i].name),
                "_proxy": "N/O heavy-atom pair within %.1f A; no hydrogens are placed in these deposits"
                          % polar_cutoff})
        rec["n_polar_contacts"] = len(rec["polar_contacts"])
        rec["n_sidechain_polar_contacts"] = sum(1 for c in rec["polar_contacts"] if c["target_sidechain"])
        out["%s%d%s" % (resname, resseq, icode.strip())] = rec
    return out


def signature(cif_path, pdb_id):
    """The target-side interface signature of ONE deposit, on the copy the committed map names."""
    import selcal_cofold_validate as V
    import valb_frame_transfer_check as F
    roles, rerr = F.roles_from_selcal_artifact(pdb_id)
    if rerr:
        return {"pdb": pdb_id, "error": "roles unresolved: %s" % rerr}
    atoms = V.parse_structure(cif_path)
    seq, keys = V.chain_sequence(atoms, roles["target"])
    return {"pdb": pdb_id, "roles": {"target": roles["target"], "e3": roles["e3"]},
            "target_sequence_len": len(seq), "target_sequence": seq,
            "residue_keys": [list(k) for k in keys],
            "contacts": residue_contacts(atoms, roles["target"], set(roles["e3"])),
            "contact_A": contact_a(), "polar_max_A": HBOND_MAX_A}


def align_positions(sig_a, sig_b):
    """[(index_a, index_b)] aligned columns of the two target sequences, by the repo's own aligner."""
    import selcal_cofold_validate as V
    ident, pairs = V.align_identity(sig_a["target_sequence"], sig_b["target_sequence"])
    return ident, pairs


def compare(sig_a, sig_b):
    """Where do the two paralogues' interfaces differ, position by aligned position?

    ⛔ ALIGNED BY SEQUENCE, NEVER BY RESIDUE NUMBER. SMARCA2 and SMARCA4 bromodomains are ~80 % identical but
    are numbered in their own full-length proteins, so equal numbers are different residues and the two
    numbering schemes are ~140 apart. Comparing by number would produce a table that looks like a result."""
    if sig_a.get("error") or sig_b.get("error"):
        return {"error": sig_a.get("error") or sig_b.get("error")}
    ident, pairs = align_positions(sig_a, sig_b)
    keys_a = [tuple(k) for k in sig_a["residue_keys"]]
    keys_b = [tuple(k) for k in sig_b["residue_keys"]]
    ca, cb = sig_a["contacts"], sig_b["contacts"]

    def _label(keys, seqidx, contacts):
        if seqidx >= len(keys):
            return None, None
        _, resseq, icode = keys[seqidx]
        for k, v in contacts.items():
            if v["resseq"] == resseq and (v["icode"] or "").strip() == (icode or "").strip():
                return k, v
        return None, None

    rows = []
    for ia, ib in pairs:
        ka, va = _label(keys_a, ia, ca)
        kb, vb = _label(keys_b, ib, cb)
        aa_a = sig_a["target_sequence"][ia]
        aa_b = sig_b["target_sequence"][ib]
        pa = va["n_polar_contacts"] if va else 0
        pb = vb["n_polar_contacts"] if vb else 0
        # ⛔ SIDE CHAIN vs BACKBONE IS THE DISTINCTION THAT MATTERS, and ignoring it cost a real recovery.
        # The published claim is a hydrogen bond from the SIDE CHAIN of a glutamine. At the aligned position
        # SMARCA4 carries a LEUCINE, which cannot make that bond — but its BACKBONE amide does contact the
        # E3, and counting that as "SMARCA4 also makes a polar contact here" hid the substitution behind an
        # interaction of a different kind (measured, CI run 30757920977: GLN98 OE1->ARG12.NH2 2.88 A vs
        # LEU1545 N->ASP92.OD1 2.93 A).
        sa = va.get("n_sidechain_polar_contacts", 0) if va else 0
        sb = vb.get("n_sidechain_polar_contacts", 0) if vb else 0
        if not va and not vb:
            continue
        rows.append({"a": ka, "b": kb, "aa_a": aa_a, "aa_b": aa_b, "identical_residue": aa_a == aa_b,
                     "n_contacts_a": va["n_contacts"] if va else 0,
                     "n_contacts_b": vb["n_contacts"] if vb else 0,
                     "n_polar_a": pa, "n_polar_b": pb,
                     "n_sidechain_polar_a": sa, "n_sidechain_polar_b": sb,
                     "polar_only_in_a": bool(pa and not pb), "polar_only_in_b": bool(pb and not pa),
                     "sidechain_polar_only_in_a": bool(sa and not sb),
                     "sidechain_polar_only_in_b": bool(sb and not sa),
                     "polar_detail_a": (va or {}).get("polar_contacts", []),
                     "polar_detail_b": (vb or {}).get("polar_contacts", [])})
    return {"sequence_identity": round(ident, 4), "n_aligned_interface_positions": len(rows),
            "rows": rows,
            "polar_only_in_a": [r["a"] for r in rows if r["polar_only_in_a"]],
            "polar_only_in_b": [r["b"] for r in rows if r["polar_only_in_b"]],
            "sidechain_polar_only_in_a": [r["a"] for r in rows if r["sidechain_polar_only_in_a"]],
            "sidechain_polar_only_in_b": [r["b"] for r in rows if r["sidechain_polar_only_in_b"]],
            "_aligned_by": "sequence, never residue number — the two paralogues are numbered in their own "
                           "full-length proteins and equal numbers are different residues"}


def known_answer_check(cmp_doc, expected_residue_letter="Q"):
    """Does the descriptor recover the PUBLISHED selectivity contact? A known-answer test, scored honestly.

    The published claim is a selectivity-inducing hydrogen bond from **Gln1469 of SMARCA2BD** to VCB. What is
    checkable without trusting author numbering: at least one aligned interface position where the SMARCA2
    residue is a GLUTAMINE, makes a SIDE-CHAIN polar contact to the E3, and the aligned SMARCA4 residue makes
    no side-chain polar contact of its own.

    ⛔ SIDE CHAIN, NOT ANY POLAR CONTACT — the first version tested "any", and it missed the real recovery.
    SMARCA4 carries a LEUCINE at the aligned position, which cannot make the published bond, but its BACKBONE
    amide does touch the E3; counting that hid the substitution behind an interaction of a different kind.

    ⚠ The residue NUMBER is reported when it is present, but the check does not depend on it — a deposit is
    free to number its construct however it likes, and a check that hinged on 1469 would fail for a reason
    that has nothing to do with the mechanism."""
    if cmp_doc.get("error"):
        return {"checked": False, "why": cmp_doc["error"]}
    hits = [r for r in cmp_doc.get("rows", [])
            if r.get("sidechain_polar_only_in_a") and r["aa_a"] == expected_residue_letter]
    doc = {"checked": True,
           "expected": "a %s on the SMARCA2 arm making a polar contact to VCB that the aligned SMARCA4 "
                       "residue does not make (Kofink et al. 2022, PMC9551036)" % expected_residue_letter,
           "n_matching_positions": len(hits),
           "positions": [{"smarca2": r["a"], "smarca4": r["b"], "smarca4_residue": r["aa_b"],
                          "polar_contacts": r["polar_detail_a"]} for r in hits],
           "recovered": bool(hits)}
    if hits:
        doc["sentence"] = (
            "KNOWN-ANSWER RECOVERED: the interface descriptor finds %d position(s) where a glutamine on the "
            "SMARCA2 arm makes a SIDE-CHAIN polar contact to VCB and the aligned SMARCA4 residue makes none "
            "(%s). The "
            "published selectivity-inducing contact is visible to a static, MD-free readout — so a "
            "paralogue-discriminating contact IS detectable from a ternary structure. ⛔ It validates THIS "
            "descriptor on ONE contact in ONE pair; it does not validate E1, and it makes no NR4A3 "
            "prediction correct."
            % (len(hits), ", ".join("%s vs %s" % (h["smarca2"], h["smarca4"]) for h in doc["positions"])))
    else:
        doc["sentence"] = (
            "KNOWN ANSWER NOT RECOVERED: no aligned position has a glutamine making a polar contact on the "
            "SMARCA2 arm and not on SMARCA4. Either the descriptor cannot see the published contact or the "
            "copy compared does not contain it — and until that is resolved this descriptor may NOT be used "
            "to argue selectivity anywhere, including for NR4A3.")
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Structure-only paralogue interface signature ($0 CPU).")
    ap.add_argument("--native-dir", default="/tmp/selcal_cofolds/_native")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-interface-signature.json"))
    args = ap.parse_args(argv)

    import selcal_panel as P
    dep = dict(P.REFERENCE["deposited_ternaries"])

    def _path(pid):
        p = os.path.join(args.native_dir, "%s.cif" % pid)
        return p if os.path.exists(p) else os.path.join(args.native_dir, "%s.pdb" % pid)

    sigs = {}
    for gene, pid in dep.items():
        p = _path(pid)
        sigs[gene] = ({"pdb": pid, "error": "%s not read on this runner — UNREAD, not empty" % pid}
                      if not os.path.exists(p) else signature(p, pid))

    doc = {"_what": "static, MD-free target<->VCB interface signature of the two deposited ternaries, and "
                    "whether it recovers the published selectivity-inducing contact",
           "_reference": P.REFERENCE.get("pair_mechanism_quote"),
           "_reference_source": P.REFERENCE.get("pair_mechanism_source"),
           "polar_contact_is_a_proxy": "N/O heavy-atom pair within %.1f A; deposited X-ray structures at "
                                       "this resolution place no hydrogens" % HBOND_MAX_A,
           "signatures": sigs}
    cmp_doc = compare(sigs.get("SMARCA2", {}), sigs.get("SMARCA4", {}))
    doc["comparison"] = cmp_doc
    doc["known_answer"] = known_answer_check(cmp_doc)
    doc["sentence"] = doc["known_answer"].get("sentence")
    json.dump(doc, open(args.out, "w"), indent=1)

    for gene, s in sigs.items():
        if s.get("error"):
            print("  %-9s %s" % (gene, s["error"]), flush=True)
        else:
            print("  %-9s %s  target chain %s, %d interface residue(s)"
                  % (gene, s["pdb"], s["roles"]["target"], len(s["contacts"])), flush=True)
    if not cmp_doc.get("error"):
        print("  aligned interface positions: %d (sequence identity %.3f)"
              % (cmp_doc["n_aligned_interface_positions"], cmp_doc["sequence_identity"]), flush=True)
        print("  polar only on SMARCA2: %s" % (cmp_doc["polar_only_in_a"] or "none"), flush=True)
        print("  polar only on SMARCA4: %s" % (cmp_doc["polar_only_in_b"] or "none"), flush=True)
    print(doc["sentence"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
