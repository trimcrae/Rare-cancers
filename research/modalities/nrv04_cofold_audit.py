#!/usr/bin/env python3
"""
NR-V04 co-fold E3 PROVENANCE AUDIT — which protein is actually in each co-folded assembly?

WHY THIS EXISTS. The retrospective's chain-split check (nrv04_vast_launch.retro_stage_test, 2026-07-24) measured
a per-chain residue census of the assembled complexes and found four chains: A=254, E=213, F=255, G=112. Chain A
is the NR4A LBD (the frozen construct is the C-terminal 254 residues), E is VHL (213 aa), G is Elongin C
(112 aa) — but **F is 255 residues, and Elongin B is 118**. The suspected cause is the accession error already
on record in e3-provenance-correction.json: `ELONGIN_B` was `P62258` (14-3-3 protein epsilon, YWHAE) until
2026-07-17, and nrv04_ternary.py builds its co-fold YAML by fetching that constant's sequence directly. That
record scoped the physical impact to valB (which resolves chains from RCSB, so it was genuinely unaffected) and
parked the NR-V04 co-folds as "a separate, parked workstream" — the follow-up never happened.

This module produces the observation that DISCRIMINATES rather than another plausible story:
  1. the real lengths of P62258 and Q15370, fetched from UniProt (a runner, not the sandbox — the egress proxy
     403s UniProt);
  2. the S3 LastModified of each co-fold prefix, so a co-fold built before the 2026-07-17 correction is
     distinguished from one built after;
  3. a chain-length census of one real CIF from EACH co-fold prefix, so the audit covers the RETROSPECTIVE's
     inputs (nrv04-descriptive-v3) AND the COMPLETED feasibility panel's inputs (nrv04-covalent-cofold).

Item 3 is the one that matters most: the feasibility panel is finished and its result is the recorded GO for
this rung. If its co-folds carry the same substitution, that verdict rests on an assembly containing the wrong
protein, and it has to be said plainly.

Pure stdlib + boto3. Runs on a CI runner (free, open internet).
"""
from __future__ import annotations

import json
import os
import urllib.request

UNIPROT_FASTA = "https://rest.uniprot.org/uniprotkb/{acc}.fasta"

# The accessions in play. Names are what UniProt should return; the audit VERIFIES them rather than asserting.
ACCESSIONS = {
    "P62258": "expected: 14-3-3 protein epsilon (YWHAE) — the ERRONEOUS ElonginB value used before 2026-07-17",
    "Q15370": "expected: Elongin B (ELOB) — the corrected value",
    "Q15369": "expected: Elongin C (ELOC)",
    "P40337": "expected: VHL",
}

COFOLD_PREFIXES = {
    "nrv04-descriptive-v3": "the RETROSPECTIVE's inputs (nr4a1/nr4a2/nr4a3 + neg controls)",
    "nrv04-covalent-cofold": "the COMPLETED covalent feasibility panel's inputs",
    "nrv04-shakeout": "the earlier shakeout run",
}


def fetch_lengths(accessions=tuple(ACCESSIONS)):
    """Sequence length + description per accession, straight from UniProt."""
    out = {}
    for acc in accessions:
        req = urllib.request.Request(UNIPROT_FASTA.format(acc=acc), headers={"User-Agent": "rare-cancers-ci"})
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
        lines = txt.strip().splitlines()
        header = lines[0] if lines else ""
        seq = "".join(l.strip() for l in lines[1:])
        out[acc] = {"length": len(seq), "header": header, "note": ACCESSIONS.get(acc, "")}
    return out


def chain_census_from_cif(cif_path):
    """Per-chain polymer residue counts from a co-fold CIF, in file order (gemmi)."""
    import gemmi
    st = gemmi.read_structure(cif_path)
    st.setup_entities()
    out = []
    for chain in st[0]:
        n = sum(1 for res in chain
                if (lambda i: bool(i) and (i.is_amino_acid() or i.is_nucleic_acid()))(
                    gemmi.find_tabulated_residue(res.name)))
        if n:
            out.append({"chain": chain.name, "residues": n})
    return out


def _s3_first_cif(s3, bucket, prefix):
    """(key, LastModified) of the first *_model_0.cif under a prefix — None if the prefix has none."""
    tok, best = None, None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if o["Key"].endswith("_model_0.cif") and (best is None or o["Key"] < best[0]):
                best = (o["Key"], o["LastModified"])
        if not r.get("IsTruncated"):
            return best
        tok = r["NextContinuationToken"]


def audit(bucket, prefixes=tuple(COFOLD_PREFIXES)):
    import boto3
    s3 = boto3.client("s3")
    lengths = fetch_lengths()
    by_len = {}
    for acc, d in lengths.items():
        by_len.setdefault(d["length"], []).append(acc)

    findings = []
    for prefix in prefixes:
        hit = _s3_first_cif(s3, bucket, prefix.rstrip("/") + "/")
        if not hit:
            findings.append({"prefix": prefix, "status": "no co-fold CIF found"})
            continue
        key, modified = hit
        local = "/tmp/audit_%s.cif" % prefix.replace("/", "_")
        s3.download_file(bucket, key, local)
        census = chain_census_from_cif(local)
        # match each chain length back to an accession where it is unambiguous
        annotated = []
        for c in census:
            match = by_len.get(c["residues"], [])
            annotated.append({**c, "matches_accession": match,
                              "identified_as": (lengths[match[0]]["header"].split("OS=")[0].strip()
                                                if len(match) == 1 else None)})
        has_wrong = any("P62258" in (c["matches_accession"] or []) for c in annotated)
        has_right = any("Q15370" in (c["matches_accession"] or []) for c in annotated)
        findings.append({
            "prefix": prefix, "purpose": COFOLD_PREFIXES.get(prefix, ""), "example_key": key,
            "s3_last_modified": modified.isoformat() if hasattr(modified, "isoformat") else str(modified),
            "chains": annotated,
            "contains_P62258_length_chain": has_wrong,
            "contains_Q15370_length_chain": has_right,
            "verdict": ("AFFECTED — a chain matches the erroneous P62258 (14-3-3 epsilon) length and none "
                        "matches Elongin B" if has_wrong and not has_right else
                        "clean — an Elongin B-length chain is present" if has_right else
                        "inconclusive — no chain matches either accession length"),
        })

    out = {"bucket": bucket, "uniprot_lengths": lengths,
           "elongin_b_correction_record": "e3-provenance-correction.json (corrected 2026-07-17)",
           "findings": findings,
           "why": "the retrospective's chain-split check measured a 255-residue chain where Elongin B (118) "
                  "should be; this audit identifies it from primary sequence lengths rather than inference"}
    json.dump(out, open("nrv04-cofold-e3-audit.json", "w"), indent=2)
    print(json.dumps(out, indent=2, default=str), flush=True)
    return out


def completed_panel_chain_split(bucket, prefix="nrv04-covalent-results"):
    """SECOND, independent question: did the COMPLETED feasibility panel measure the interface it meant to?

    nrv04_covalent_md._topology_indices splits E3 from target POSITIONALLY — `target = the LAST sorted protein
    chain`. The co-folds are chain A = NR4A LBD, E = VHL, F = ElonginB, G = ElonginC, so sorted-last is G,
    ElonginC. The same driver ALSO resolves the reactive cysteine by GEOMETRY (nearest Sγ to the warhead), and
    records that chain in each leg's `meta.reactive_cys`. The reactive Cys is on the NR4A1 LBD by construction.

    So a completed leg whose recorded reactive-Cys chain is NOT the chain the positional rule would have picked
    is direct, artifact-based proof — from the panel's own committed output — that the interface readouts were
    computed against the wrong chain pair. No re-run, no inference."""
    import boto3
    s3 = boto3.client("s3")
    tok, keys = None, []
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix.rstrip("/") + "/"}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", []) if o["Key"].rsplit("/", 1)[-1].startswith("leg_")]
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    legs = []
    for k in sorted(keys):
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception as e:  # noqa: BLE001
            legs.append({"key": k, "error": str(e)}); continue
        meta = d.get("meta") or {}
        rc = meta.get("reactive_cys") or {}
        legs.append({"key": k, "leg_id": d.get("leg_id"), "seed": d.get("seed"),
                     "reactive_cys_chain": rc.get("chain"), "reactive_cys_resid": rc.get("resid"),
                     "sg_electrophile_dist_A": rc.get("sg_electrophile_dist_A"),
                     "R1_stable": (d.get("R1_interface") or {}).get("stable"),
                     "R1_plateau_A": (d.get("R1_interface") or {}).get("plateau_A"),
                     "R2_recruited": (d.get("R2_recruitment") or {}).get("recruited"),
                     "R3_min_A": (d.get("R3_lys") or {}).get("min_A")})
    chains = sorted({l.get("reactive_cys_chain") for l in legs if l.get("reactive_cys_chain")})
    return {"prefix": prefix, "n_legs": len(legs), "reactive_cys_chains_seen": chains, "legs": legs,
            "how_to_read": "the reactive Cys sits on the NR4A1 LBD. If that chain is not the last chain in "
                           "sorted order, the positional target rule selected a different chain and the R1-R3 "
                           "readouts describe a different interface than intended."}


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Audit which E3 proteins are actually in the NR-V04 co-folds.")
    ap.add_argument("--completed-panel", action="store_true",
                    help="also audit the completed feasibility panel's leg JSONs for the chain-split question")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--prefixes", default=",".join(COFOLD_PREFIXES))
    args = ap.parse_args(argv)
    if not args.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")
    audit(args.bucket, tuple(p for p in args.prefixes.split(",") if p))
    if args.completed_panel:
        res = completed_panel_chain_split(args.bucket)
        json.dump(res, open("nrv04-completed-panel-chain-split.json", "w"), indent=2)
        print(json.dumps(res, indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
