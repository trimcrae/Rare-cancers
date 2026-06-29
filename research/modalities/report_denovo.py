#!/usr/bin/env python3
"""
Read the de-novo generation result from S3 and print the ranked candidates WITH SMILES — merged, if
present, with the dock-funnel selectivity cell and the MM-GBSA verdict so a candidate's structure,
chemistry, selectivity call, and energy-tier verdict are all in one table. Read-only; commits nothing.

Reads (best-effort, skips what's absent):
  s3://<bucket>/<denovo_prefix>/nr4a3-denovo.json       (generation: name, smiles, QED, SAscore, handle_contacts, denovo_promise)
  s3://<bucket>/<matrix_prefix>/nr4a3-matrix.json       (dock funnel: per-candidate selectivity cell)   [optional]
  s3://<bucket>/<mmgbsa_prefix>/nr4a3-mmgbsa.json        (MM-GBSA: per-candidate verdict)                [optional]
"""
import json
import os
import sys


def _get(s3, bucket, key):
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception as e:  # noqa: BLE001 — optional sources are allowed to be missing
        print(f"  (skip s3://{bucket}/{key}: {str(e)[:80]})", file=sys.stderr)
        return None


def _f(x, w=6, p=2):
    return f"{x:>{w}.{p}f}" if isinstance(x, (int, float)) else f"{'--':>{w}}"


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    denovo_prefix = os.environ.get("DENOVO_PREFIX", "nr4a3-denovo")
    matrix_prefix = os.environ.get("MATRIX_PREFIX", "nr4a3-denovo-matrix")
    mmgbsa_prefix = os.environ.get("MMGBSA_PREFIX", "nr4a3-denovo-mmgbsa")

    den = _get(s3, bucket, f"{denovo_prefix}/nr4a3-denovo.json")
    if not den:
        sys.exit(f"could not read s3://{bucket}/{denovo_prefix}/nr4a3-denovo.json")
    mtx = _get(s3, bucket, f"{matrix_prefix}/nr4a3-matrix.json") or {}
    mmg = _get(s3, bucket, f"{mmgbsa_prefix}/nr4a3-mmgbsa.json") or {}

    cell = {r.get("label"): r.get("cell") for r in mtx.get("candidates", [])}
    verdict = {r.get("label"): r.get("verdict") for r in mmg.get("candidates", [])}
    mm_margin = {r.get("label"): r.get("mm_min_margin") for r in mmg.get("candidates", [])}

    # Developability gate (red-team 2026-06-29): flag stability/reactivity liabilities the funnel's QED/SA
    # score missed (carbamic acids, peroxides, acetals, cyclopentadienes, ...). Guarded: only if RDKit is
    # present in the report env. The pure verdict reuses the profile's aromatic_rings + SAscore.
    try:
        import structural_alerts as _sa
        _rdkit_ok = True
    except Exception as _e:  # noqa
        print(f"  (structural_alerts unavailable: {str(_e)[:60]})", file=sys.stderr)
        _rdkit_ok = False

    def _dev(c):
        """Return (developable: bool|None, liabilities: list, reasons: list) for a candidate row."""
        if not _rdkit_ok or not c.get("smiles"):
            return None, [], []
        liab = _sa.liabilities_from_smiles(c["smiles"])
        v = _sa.developable_verdict(liab, c.get("aromatic_rings"), c.get("SAscore"))
        return v["developable"], liab, v["reasons"]
    # the leads list key differs between the saved JSON and the stdout summary — accept either
    leads_sel = (mmg.get("leads_confirmed_selective") or mmg.get("confirmed_selective") or [])

    print(f"\ncampaign: {den.get('campaign')}  n_samples_requested: {den.get('n_samples_requested')}  "
          f"num_nodes_list: {den.get('num_nodes_list')}")
    print(f"receptor: {den.get('receptor_source')}")
    print(f"summary: {json.dumps(den.get('summary', {}))}")
    if mmg.get("verdict_census"):
        print(f"mmgbsa verdict census: {json.dumps(mmg['verdict_census'])}  "
              f"confirmed_selective={leads_sel}")

    rows = [c for c in den.get("candidates", []) if c.get("smiles")]
    print(f"\n=== de-novo candidates with SMILES ({len(rows)}; ranked by denovo_promise) ===")
    hdr = (f"{'name':<11} {'prom':>5} {'QED':>4} {'SA':>4} {'MW':>5} {'hnd':>3} {'dev':>3} {'dockCell':<14} "
           f"{'mmMargin':>8} {'verdict':<22} SMILES")
    print(hdr); print("-" * len(hdr))
    for c in rows:
        nm = c.get("name")
        dev, _liab, _why = _dev(c)
        dflag = "--" if dev is None else ("OK" if dev else "X")
        print(f"{str(nm):<11} {_f(c.get('denovo_promise'),5)} {_f(c.get('QED'),4)} {_f(c.get('SAscore'),4,1)} "
              f"{_f(c.get('MW'),5,0)} {str(c.get('handle_contacts','')):>3} {dflag:>3} "
              f"{str(cell.get(nm,''))[:14]:<14} {_f(mm_margin.get(nm),8)} {str(verdict.get(nm,''))[:22]:<22} "
              f"{c.get('smiles')}")

    # Developability shortlist: clean (no liability, aromatic, SA<=4.5) candidates, NR4A3-favourable cells
    # first. This is the red-team's Tier-1 #1 deliverable — does a clean+selective candidate already exist
    # in the generated set, and which clean candidates should be advanced to a fresh dock+MM-GBSA?
    if _rdkit_ok:
        FAVOURABLE = {"NR4A3-only", "NR4A2+NR4A3", "NR4A1+NR4A3", "pan-NR4A"}
        clean = []
        for c in rows:
            dev, liab, _why = _dev(c)
            if dev:
                clean.append((c, cell.get(c.get("name")), verdict.get(c.get("name"))))
        print(f"\n=== DEVELOPABLE candidates ({len(clean)} of {len(rows)} clean: no liability + aromatic + "
              f"SA<=4.5) ===")
        # NR4A3-favourable-cell developables first (already scored), then the rest (to advance to docking)
        scored = [t for t in clean if t[1]]
        unscored = [t for t in clean if not t[1]]
        fav = [t for t in scored if t[1] in FAVOURABLE]
        print(f"  developable AND in an NR4A3-favourable docking cell ({len(fav)}): " +
              (", ".join(f"{c.get('name')}[{cl}/{vd}]" for c, cl, vd in fav) or "NONE"))
        print(f"  developable, other already-docked cells ({len(scored) - len(fav)}): " +
              (", ".join(f"{c.get('name')}[{cl}]" for c, cl, vd in scored if (c, cl, vd) not in fav) or "none"))
        print(f"  developable, NOT yet docked ({len(unscored)}; advance these to dock+MM-GBSA, "
              f"top by promise):")
        for c, _cl, _vd in unscored[:15]:
            print(f"    {c.get('name'):<11} prom={_f(c.get('denovo_promise'),5)} QED={c.get('QED')} "
                  f"SA={c.get('SAscore')} hnd={c.get('handle_contacts')} {c.get('smiles')}")

    # Spotlight the confirmed_selective leads (the publishable hits) with their full SMILES.
    if leads_sel:
        by_name = {c.get("name"): c for c in rows}
        print(f"\n=== confirmed_selective leads (MM-GBSA) ===")
        for nm in leads_sel:
            c = by_name.get(nm, {})
            print(f"  {nm}: SMILES={c.get('smiles')}  QED={c.get('QED')} SA={c.get('SAscore')} "
                  f"handles={c.get('handle_contacts')} dockCell={cell.get(nm)} mmMargin={mm_margin.get(nm)}")


if __name__ == "__main__":
    main()
