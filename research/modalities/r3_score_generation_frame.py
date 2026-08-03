#!/usr/bin/env python3
"""R3, part 2 — SCORE the generation receptor under the HARMONIZED, score-independent site definition.

`r3_generation_frame_audit.py` names the frame and, on the committed manifest, returns
`FRAME_NAMED_UNSCORED`: the generation receptor is `nr4a3-release-druggable.pdb` = release replica 0,
frame 95 (Rg 0.7367 nm), and its recorded druggability **0.667** carries NO `pocket_match` block at all
(the manifest is dated 2026-06-29, before the harmonized tracker was frozen on 2026-07-11), so it is a
pre-harmonized number. A pre-harmonized score cannot discharge a harmonized gate. This module is the named
unblocker: score that ONE structure, under `POCKET_MATCH=harmonized` and the pinned fpocket build, with
exactly the code path `nr4a3_mdpocket.druggability_timeseries` uses for every release frame.

⚠ WHY NOT REUSE `nr4a3_fpocket_enumerate.py`. That script is the `af2_static` path: it is hardcoded to
`AF-Q92570.pdb` and its docstring states *"The AF2 model uses UniProt numbering, so resSeq == residue."*
The generation receptor is a trajectory frame re-extracted by `nr4a3_release_druggable.py` and is
renumbered — its manifest row records `resseq_range: [1, 254]` against an LBD trimmed contiguously from
373. Running the AF2 path over it would look up UniProt 406–534 in a structure numbered 1–254 and find
nothing, i.e. it would report "no matched orthosteric cavity" for a numbering reason and that would be
indistinguishable from a real D* failure. The mapping is therefore DERIVED by `residue_map.
resolve_positions` — the same call `nr4a3_release_druggable.py` made — and the derived label is reported,
never assumed.

⚠ AND THIS IS A SEPARATE FINDING WORTH KEEPING VISIBLE: `af2_static` in the committed harmonized table is
the raw AFDB model `AF-Q92570.pdb`, fetched at runtime by `sagemaker_src/entry_pocket_reharmonize.py`. It
is NOT an MD frame and NOT the generation receptor. Any reading that treats its `n_ge_dstar: 0` of 1 as
"the design frame fails D*" is scoring a different structure.

Pure decision logic (`map_lining`, `classify_score`) is unit-testable; `main()` is the I/O wrapper the CI
job runs inside the fpocket environment.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pocket_tracking as pt
import residue_map as rm

LBD_FIRST = 373
POCKET5_LINING = pt.POCKET5_LINING            # 406,407,410,411,412,481,484,485,531,534 (UniProt)
POCKET_FIRST, POCKET_LAST = pt.POCKET5_SPAN   # 406..534 (UniProt)
D_STAR = pt.D_STAR


def ca_by_resseq(pdb_path):
    """{resSeq: (x,y,z)} CA coords from the frame PDB — the SAME coordinates fpocket reads, so candidate
    and reference centroids are apples-to-apples. First altloc only. Mirrors
    `nr4a3_mdpocket._ca_by_resseq_from_pdb` deliberately: a second, subtly different reader is how two
    'identical' pipelines stop agreeing."""
    ca = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM") or line[12:16].strip() != "CA":
                continue
            if line[16] not in (" ", "A"):
                continue
            try:
                ca[int(line[22:26])] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            except ValueError:
                continue
    return ca


def map_lining(resseqs, lbd_first=LBD_FIRST):
    """(lining_resseqs, span_resseqs, numbering_label) in the STRUCTURE'S numbering. PURE.

    `resseqs`: the structure's protein residue numbers in chain order.
    Returns the mapped fixed 10-residue lining set and the mapped 406..534 span, plus the label
    `residue_map.resolve_positions` produced ('resSeq-preserved' or 'renumbered-from-373') so a reader
    can tell which branch fired instead of trusting an offset.
    """
    lpos, numbering = rm.resolve_positions(resseqs, POCKET5_LINING, lbd_first)
    spos, _ = rm.resolve_positions(resseqs, range(POCKET_FIRST, POCKET_LAST + 1), lbd_first)
    lining = sorted({resseqs[i] for i in lpos})
    span = sorted({resseqs[i] for i in spos})
    return lining, span, numbering


def classify_score(matched, druggability, d_star=D_STAR):
    """The Gate-A verdict for one structure. PURE.

    Three outcomes, deliberately distinct: no matched cavity is NOT the same as a matched cavity below
    D*, and both are different from a pass. The paper's sentence — *"if the generation frame does not
    qualify, the generation receptor ... is affected"* — attaches to the first two.
    """
    if not matched:
        return {"verdict": "GATE_A_FAIL_NO_MATCH", "druggability": None, "d_star": d_star,
                "reason": ("under the harmonized composite gate (Jaccard / fraction-recovered / centroid) "
                           "no fpocket cavity in the generation receptor IS the mapped orthosteric site — "
                           "it is not the same site, before druggability is read at all"),
                "reaches": "the generation receptor itself, not merely a reported frame-fraction"}
    if float(druggability) >= d_star:
        return {"verdict": "GATE_A_PASS", "druggability": float(druggability), "d_star": d_star,
                "reason": (f"the mapped orthosteric site is detected in the generation receptor and its "
                           f"harmonized druggability {druggability} >= D* {d_star}")}
    return {"verdict": "GATE_A_FAIL_BELOW_DSTAR", "druggability": float(druggability), "d_star": d_star,
            "reason": (f"the mapped orthosteric site is detected but its harmonized druggability "
                       f"{druggability} < D* {d_star}"),
            "reaches": "the generation receptor itself, not merely a reported frame-fraction"}


# ---- I/O wrapper -----------------------------------------------------------------------------------

def score_pdb(pdb_path, workdir):
    """Run fpocket on one structure and apply the harmonized matcher. Returns the full record."""
    import nr4a3_structure as ns
    stem = "frame"
    local = os.path.join(workdir, stem + ".pdb")
    shutil.copy(pdb_path, local)
    subprocess.run(["fpocket", "-f", local], check=True, capture_output=True, text=True, timeout=600)
    resids_by_num, info = ns.pocket_residues_by_number(os.path.join(workdir, stem + "_out"), stem)

    ca = ca_by_resseq(local)
    resseqs = sorted(ca)
    lining, span, numbering = map_lining(resseqs)
    ref = pt.orthosteric_reference(ca, lining_residues=lining,
                                   span=(min(span), max(span)) if span else (0, 0))
    cands = [{"pocket": int(num), "residues": sorted(int(r) for r in resids),
              "druggability": info[num]["druggability"]}
             for num, resids in resids_by_num.items()]
    hit = pt.match_pocket(cands, ref, ca_by_resnum=ca, **pt.match_params())
    verdict = classify_score(hit is not None, None if hit is None else hit.get("druggability"))
    return {
        "structure": os.path.basename(pdb_path),
        "numbering": numbering,
        "n_protein_residues": len(resseqs),
        "mapped_lining_resseqs": lining,
        "mapped_span_resseqs": [min(span), max(span)] if span else None,
        "fpocket_version": pt.resolved_fpocket_version(),
        "match_mode": pt.match_mode(),
        "match_params": pt.match_params(),
        "n_candidate_pockets": len(cands),
        "all_pocket_druggability": {str(c["pocket"]): c["druggability"] for c in cands},
        "matched_pocket": None if hit is None else {"pocket": hit.get("pocket"),
                                                    "druggability": hit.get("druggability"),
                                                    "_match": hit.get("_match")},
        "verdict": verdict,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    here = os.path.dirname(os.path.abspath(__file__))
    pdb = None
    out_path = os.path.join(here, "r3-generation-frame-harmonized.json")
    for i, a in enumerate(argv):
        if a == "--pdb" and i + 1 < len(argv):
            pdb = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out_path = argv[i + 1]
    if not pdb or not os.path.exists(pdb):
        sys.exit(f"  ABORT: --pdb <path> required and must exist (got {pdb!r})")
    if not shutil.which("fpocket"):
        sys.exit("  ABORT: fpocket not on PATH — the harmonized score must not be faked from the manifest")
    if pt.match_mode() != pt.HARMONIZED:
        sys.exit("  ABORT: POCKET_MATCH must be 'harmonized'; a legacy score cannot discharge this gate")

    work = tempfile.mkdtemp(prefix="r3fp_")
    rec = score_pdb(pdb, work)
    rec["_what"] = ("R3 Gate A — the EXACT generation receptor (nr4a3-release-druggable.pdb = release "
                    "rep 0 frame 95) scored under the harmonized, score-independent orthosteric-site "
                    "definition with the pinned fpocket build")
    rec["_gate"] = ("nr4a3-degrader-paper.md 'Dependency audit — still open'; "
                    "nr4a3-ensemble-redesign-brief.md Gate A")
    rec["_prior_manifest_score"] = {"value": 0.667, "mode": "pre-harmonized (no pocket_match block)",
                                    "source": "s3 nr4a3-release-druggable/nr4a3-release-druggable.json, "
                                              "written 2026-06-29, before the harmonized tracker froze"}
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=2)
    print(json.dumps(rec["verdict"], indent=2))
    print(f"[r3-score] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
