#!/usr/bin/env python3
"""Build the drug-repurposing candidate set for the NR4A3 cryptic-pocket screen.

Turns the **Broad Drug Repurposing Hub** (Corsello et al., Nat Med 2017; non-commercial research use) into a
candidate JSON in the SAME shape the de-novo dock funnel consumes (nr4a3_matrix.py candidate mode via
--candidate-json): {"candidates": [{"name", "smiles", "denovo_promise", "drug", "phase", "moa", "target"}]}.

Pipeline: parse the samples file (name+SMILES) -> desalt to the largest organic fragment -> drug-like filter
(valid RDKit, allowed elements, MW window, not grossly non-drug-like) -> dedupe by canonical SMILES -> annotate
clinical phase / MOA / target from the drugs file -> flag any KNOWN NR4A/Nur77 modulators already present as
positive controls (SMILES sourced from the Hub, never fabricated here).

MEDICAL-INTEGRITY NOTE: every SMILES comes from the Broad Hub export; this script does not invent structures.
The Hub is a curated public repurposing library. Downstream docking scores are HYPOTHESES, not affinities.

Run locally (needs network + rdkit); commit the emitted JSON so the SageMaker dock job reads it from the git
clone (the job itself does no download). Source files (SHA-pinned by date in the URL):
  repurposing_samples_20200324.txt  repurposing_drugs_20200324.txt
"""
import json
import os
import re
import sys

SAMPLES = os.environ.get("SAMPLES_TXT", "repurposing_samples.txt")
DRUGS = os.environ.get("DRUGS_TXT", "repurposing_drugs.txt")
OUT = os.environ.get("OUT_JSON", "nr4a3-repurpose-candidates.json")

ALLOWED = set("H B C N O F Si P S Cl Br I".split())
MW_MIN, MW_MAX = 150.0, 600.0          # cryptic Pocket-5 is small (401 MW ~334, lo_m0_NCCO ~361); allow to 600
MAX_HEAVY = 60

# Known NR4A / Nur77 (NR4A1) / NURR1 (NR4A2) / NOR-1 (NR4A3) modulators reported in the literature. We only
# FLAG these as positive controls when the SAME name is present in the Hub (so the SMILES is the Hub's, curated)
# — we do not inject SMILES. Names are matched case-insensitively against pert_iname.
NR4A_CONTROL_NAMES = {
    "celastrol", "cytosporone-b", "cytosporone b", "csn-b",
    "3,3'-diindolylmethane", "diindolylmethane", "dim",
    "6-mercaptopurine", "mercaptopurine", "6-mp",
    "prostaglandin-a2", "prostaglandin a2", "pga2",
    "tretinoin", "isotretinoin",      # retinoids reported to act on Nur77/RXR-Nur77 heterodimers
    "thpn", "z-ligustilide",
}


def _drugs_ann(path):
    ann = {}
    if not os.path.exists(path):
        return ann
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("!") or line.startswith("pert_iname\t"):
                continue
            c = [x.strip().strip('"').strip() for x in line.rstrip("\n").split("\t")]
            if len(c) >= 4 and c[0]:
                ann[c[0].lower()] = {"phase": c[1], "moa": c[2], "target": c[3]}
    return ann


def _largest_fragment(mol, Chem):
    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=False)
    if not frags:
        return mol
    return max(frags, key=lambda m: m.GetNumHeavyAtoms())


def main():
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")

    ann = _drugs_ann(DRUGS)
    seen_key = set()
    seen_name = set()
    cands = []
    n_rows = n_bad = n_filtered = 0

    with open(SAMPLES, encoding="utf-8", errors="replace") as fh:
        header = None
        for line in fh:
            if line.startswith("!"):
                continue
            cols = line.rstrip("\n").split("\t")
            if header is None:
                header = cols
                idx = {h: i for i, h in enumerate(header)}
                continue
            n_rows += 1
            try:
                name = cols[idx["pert_iname"]].strip().strip('"').strip()
                smi = cols[idx["smiles"]].strip().strip('"').strip()
            except (KeyError, IndexError):
                n_bad += 1
                continue
            if not smi or not name or name.lower() in seen_name:
                continue
            m = Chem.MolFromSmiles(smi)
            if m is None:
                n_bad += 1
                continue
            m = _largest_fragment(m, Chem)
            try:
                Chem.SanitizeMol(m)
            except Exception:  # noqa: BLE001
                n_bad += 1
                continue
            syms = {a.GetSymbol() for a in m.GetAtoms()}
            if not syms.issubset(ALLOWED):
                n_filtered += 1
                continue
            if m.GetNumHeavyAtoms() > MAX_HEAVY:
                n_filtered += 1
                continue
            mw = Descriptors.MolWt(m)
            if not (MW_MIN <= mw <= MW_MAX):
                n_filtered += 1
                continue
            can = Chem.MolToSmiles(m)
            key = Chem.MolToInchiKey(m) if hasattr(Chem, "MolToInchiKey") else can
            if key in seen_key:
                continue
            seen_key.add(key)
            seen_name.add(name.lower())
            a = ann.get(name.lower(), {})
            is_ctrl = name.lower() in NR4A_CONTROL_NAMES
            cands.append({
                "name": f"rep{len(cands):05d}",
                "smiles": can,
                "denovo_promise": 1.0,       # equal rank; the funnel docks up to TOP_N in list order
                "drug": name,
                "phase": a.get("phase", ""),
                "moa": a.get("moa", ""),
                "target": a.get("target", ""),
                **({"control": "NR4A_modulator"} if is_ctrl else {}),
            })

    n_ctrl = sum(1 for c in cands if c.get("control"))
    out = {
        "_note": "Drug-repurposing candidate set for the NR4A3 cryptic Pocket-5 selectivity screen. SMILES from "
                 "the Broad Drug Repurposing Hub (Corsello et al., Nat Med 2017; non-commercial research use), "
                 "desalted + drug-like filtered + deduped. Docking scores are HYPOTHESES, not affinities.",
        "campaign": "repurpose-cryptic-pocket",
        "source": "Broad Drug Repurposing Hub (repurposing_samples/drugs_20200324)",
        "filters": {"mw": [MW_MIN, MW_MAX], "allowed_elements": sorted(ALLOWED), "max_heavy": MAX_HEAVY,
                    "desalt": "largest organic fragment", "dedupe": "InChIKey"},
        "n_candidates": len(cands),
        "n_controls": n_ctrl,
        "candidates": cands,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"rows={n_rows} bad={n_bad} filtered={n_filtered} -> kept={len(cands)} (controls={n_ctrl})")
    print(f"controls: {[c['drug'] for c in cands if c.get('control')]}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
