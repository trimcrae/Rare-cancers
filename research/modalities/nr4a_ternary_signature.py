#!/usr/bin/env python3
"""Does any NR4A3 ternary we hold present a paralogue-discriminating interface contact? ($0 CPU)

★★ THIS IS THE DELIVERABLE, AND IT IS GATED. A claim that one of this program's NR4A3 ternaries is selective
needs two things, and neither has ever been supplied:
  1. a readout shown to detect a paralogue difference **where the answer is known**, and
  2. an NR4A3 ternary that actually separates from NR4A1 and NR4A2 under it.

`selcal_interface_signature` supplies (1) or refuses to: it asks whether a static target<->E3 contact
descriptor recovers the published selectivity-inducing hydrogen bond of SMARCA2 Gln1469, on the deposited
crystals of both paralogues. **This module will not run unless that check RECOVERED**, because a descriptor
that cannot see a known paralogue difference cannot be used to assert an unknown one. The refusal is the
point, not an obstacle to route around.

⛔ AND THE HONEST PRIOR IS NEGATIVE. The paper's own §2.5/§2.7 already record that for a representative
`denovo_401` PROTAC the model predicts a ternary-like CRBN complex of **comparable confidence for all three
paralogues** (iptm 0.72/0.83/0.82) and that this "did not provide evidence for NR4A3-selective ternary geometry". So the expected outcome here is NO discriminating contact, and that result must be reported as
plainly as a positive one would be. If it lands that way, the answer to "is one of our NR4A3 ternaries
selective?" is **not yet, and here is precisely what is missing** — which is a finding, not a failure to
produce one.

⚠ A DISCRIMINATING CONTACT WOULD STILL NOT BE A DEMONSTRATION OF SELECTIVITY. It would be a structural
hypothesis with a validated detector behind it: this position, this residue difference, this contact. What it
licenses is a designed test — vary the linker and exit vector and ask whether the contact survives — not a
claim about degradation. The paper's language rules (`lint_claims.py` R1-R5) apply unchanged.

⚠ AND THE STRUCTURES MUST BE CREDIBLE. Every NR4A ternary this program holds came from the same co-folding
route whose output, on the one system with a crystal to check against, scores DockQ 0.023-0.046. That is
recorded beside any result here, because a discriminating contact read off an unreliable structure is a
hypothesis about the structure, not about the biology.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: The paralogue whose selectivity is being asked about, and the two it must separate from.
FOCUS = "NR4A3"
COMPARATORS = ("NR4A1", "NR4A2")


def descriptor_is_validated(path=None):
    """(True, detail) only if the descriptor recovered the PUBLISHED known answer. Otherwise (False, why)."""
    path = path or os.path.join(HERE, "selcal-interface-signature.json")
    if not os.path.exists(path):
        return False, ("%s absent — the descriptor has not been put to its known-answer test, and an "
                       "unvalidated detector may not be used to assert selectivity" % os.path.basename(path))
    try:
        d = json.load(open(path))
    except Exception as e:                                   # noqa: BLE001
        return False, "could not read %s: %s" % (os.path.basename(path), e)
    ka = d.get("known_answer") or {}
    if not ka.get("checked"):
        return False, "the known-answer check did not run: %s" % ka.get("why", "(no reason recorded)")
    if not ka.get("recovered"):
        return False, ("the descriptor did NOT recover the published SMARCA2 Gln1469 contact, so it is not "
                       "shown to detect a paralogue difference at all: %s" % ka.get("sentence", ""))
    return True, {"recovered_positions": ka.get("positions"), "n": ka.get("n_matching_positions")}


def signature_of(path, target_chain, e3_chains):
    """The target-side contact signature of one predicted ternary. Chains are given, never guessed here."""
    import selcal_cofold_validate as V
    import selcal_interface_signature as S
    atoms = V.parse_structure(path)
    seq, keys = V.chain_sequence(atoms, target_chain)
    if not seq:
        return {"path": os.path.basename(path), "error": "chain %s carries no polymer sequence" % target_chain}
    return {"path": os.path.basename(path), "target_sequence": seq, "target_sequence_len": len(seq),
            "residue_keys": [list(k) for k in keys],
            "roles": {"target": target_chain, "e3": list(e3_chains)},
            "contacts": S.residue_contacts(atoms, target_chain, set(e3_chains)),
            "contact_A": S.contact_a(), "polar_max_A": S.HBOND_MAX_A}


def discriminating_positions(focus_sig, comparator_sigs):
    """Aligned positions where the FOCUS paralogue makes a polar contact that EVERY comparator lacks.

    ⛔ EVERY comparator, not any: a contact present in NR4A3 and absent in NR4A2 but present in NR4A1 is not
    a discriminating contact for NR4A3, and reporting it as one is how a selectivity claim gets made out of a
    pairwise accident. The intersection is taken on the FOCUS side's own residue labels, so a position
    survives only if it discriminates against the whole comparator set."""
    import selcal_interface_signature as S
    per, sets = {}, []
    for name, sig in comparator_sigs.items():
        cmp_doc = S.compare(focus_sig, sig)
        per[name] = cmp_doc
        if cmp_doc.get("error"):
            return {"error": "comparison against %s failed: %s" % (name, cmp_doc["error"]), "pairwise": per}
        sets.append(set(cmp_doc.get("polar_only_in_a") or []))
    common = set.intersection(*sets) if sets else set()
    rows = []
    for name, cmp_doc in per.items():
        for r in cmp_doc.get("rows", []):
            if r["a"] in common:
                rows.append({"comparator": name, **{k: r[k] for k in
                                                    ("a", "b", "aa_a", "aa_b", "identical_residue",
                                                     "n_polar_a", "n_polar_b", "polar_detail_a")}})
    return {"discriminating": sorted(common), "n_discriminating": len(common),
            "detail": rows, "pairwise": {k: {"polar_only_in_focus": v.get("polar_only_in_a"),
                                             "sequence_identity": v.get("sequence_identity"),
                                             "n_aligned_interface_positions":
                                                 v.get("n_aligned_interface_positions")}
                                         for k, v in per.items()},
            "_rule": "a position must discriminate against EVERY comparator, not any one of them"}


def run(structures, target_chain, e3_chains, validated_path=None, provenance=None):
    """structures: {paralogue: path}. Returns the artifact document."""
    ok, why = descriptor_is_validated(validated_path)
    doc = {"_what": "does any NR4A3 ternary we hold present a contact that discriminates it from NR4A1 and "
                    "NR4A2 under a descriptor validated on a known answer?",
           "focus": FOCUS, "comparators": list(COMPARATORS),
           "descriptor_validated": bool(ok),
           "descriptor_validation": why if not ok else why,
           "structure_provenance": provenance or ("every NR4A ternary this program holds came from the same "
                                                  "co-folding route whose output, on the one system with a "
                                                  "crystal to check against, scores DockQ 0.023-0.046"),
           "structures": {k: os.path.basename(v) for k, v in sorted(structures.items())}}
    if not ok:
        doc["sentence"] = ("REFUSED — the descriptor has not passed its known-answer test, so no contact it "
                           "reports may be used to argue NR4A3 selectivity. %s" % why)
        return doc

    sigs = {}
    for name, path in structures.items():
        sigs[name] = signature_of(path, target_chain, e3_chains)
    doc["signatures"] = {k: {kk: vv for kk, vv in v.items() if kk != "contacts"} for k, v in sigs.items()}
    doc["n_interface_residues"] = {k: len(v.get("contacts") or {}) for k, v in sigs.items()}

    missing = [k for k in (FOCUS,) + COMPARATORS if k not in sigs or sigs[k].get("error")]
    if missing:
        doc["sentence"] = ("REFUSED — %s could not be read, and a comparison missing an arm is not a "
                           "comparison. Unread is not absent." % ", ".join(missing))
        return doc

    res = discriminating_positions(sigs[FOCUS], {k: sigs[k] for k in COMPARATORS})
    doc["result"] = res
    if res.get("error"):
        doc["sentence"] = "REFUSED — %s" % res["error"]
        return doc
    if res["n_discriminating"]:
        doc["sentence"] = (
            "%d position(s) where the %s ternary makes a polar contact to the E3 that BOTH %s ternaries lack: "
            "%s. ⛔ That is a structural HYPOTHESIS with a validated detector behind it — this position, this "
            "residue difference, this contact — and it licenses a designed test (vary linker and exit vector, "
            "ask whether the contact survives). It is not a demonstration of selectivity, and it is read off "
            "structures from a route that scores DockQ 0.023-0.046 where it can be checked."
            % (res["n_discriminating"], FOCUS, "/".join(COMPARATORS), ", ".join(res["discriminating"])))
    else:
        doc["sentence"] = (
            "NO position where the %s ternary makes a polar contact to the E3 that both %s ternaries lack. "
            "Under a descriptor that DID recover the published SMARCA2 Gln1469 contact, this NR4A3 ternary "
            "shows no paralogue-discriminating interface contact — so a selective-ternary claim cannot be "
            "justified from it. This agrees with the paper's own §2.5/§2.7 reading (comparable confidence "
            "across all three paralogues) and is reported as the finding it is."
            % (FOCUS, "/".join(COMPARATORS)))
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Paralogue-discriminating contacts in our NR4A ternaries ($0).")
    ap.add_argument("--root", required=True, help="directory holding one ternary structure per paralogue")
    ap.add_argument("--pattern", default="{p}*.cif", help="glob per paralogue; {p} is the paralogue name")
    ap.add_argument("--target-chain", required=True)
    ap.add_argument("--e3-chains", required=True, help="comma-separated")
    ap.add_argument("--validated", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a-ternary-signature.json"))
    args = ap.parse_args(argv)

    structures = {}
    for p in (FOCUS,) + COMPARATORS:
        hits = sorted(glob.glob(os.path.join(args.root, args.pattern.format(p=p.lower()))))
        if not hits:
            hits = sorted(glob.glob(os.path.join(args.root, args.pattern.format(p=p))))
        if hits:
            structures[p] = hits[0]
    doc = run(structures, args.target_chain, [c.strip() for c in args.e3_chains.split(",") if c.strip()],
              validated_path=args.validated)
    json.dump(doc, open(args.out, "w"), indent=1)
    print(doc["sentence"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
