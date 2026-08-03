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
import re
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


def resname_by_resseq(pdb_path):
    """{resSeq: 3-letter resName} from the frame PDB. PURE-ish (one file read, no fpocket).

    ⚠ ADDED 2026-08-03 and it is not cosmetic. The Gate-A verdict turns on WHICH of two accepted cavities
    is 'the site', and that question cannot be adjudicated from a druggability float — it needs the
    residues. Without names, `pocket 2` is an integer; with them it is either the same cavity fpocket
    segmented differently or a different site, and only the second reading would make the frozen rule's
    preference for pocket 1 look wrong."""
    names = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM") or line[12:16].strip() != "CA":
                continue
            if line[16] not in (" ", "A"):
                continue
            try:
                names[int(line[22:26])] = line[17:20].strip()
            except ValueError:
                continue
    return names


def parse_pocket_volumes(info_text):
    """{pocket_number: volume_A3} from an fpocket `<stem>_info.txt`. PURE.

    `fpocket_lib.parse_info` is the ONE home of that file's druggability and alpha-sphere parsing and is
    NOT modified here (other lanes read it). Volume is parsed separately because 'is pocket 2 a real
    second cavity or a sliver' is a size question and alpha-sphere count alone under-determines it.

    ⚠ THE LABEL MUST BE EXACTLY `Volume`. fpocket's info.txt carries BOTH `Volume :` (Å³, hundreds) and
    `Volume Score :` (a 0-10 descriptor). A substring test on "Volume" silently returns the SCORE — which
    is how a first pass of this function reported the two cavities at "4.909" and "4.833 Å³", numbers that
    are physically impossible for a cavity and would have been quoted as volumes."""
    vols, pid = {}, None
    for line in (info_text or "").splitlines():
        m = re.match(r"\s*Pocket\s+(\d+)\s*:", line)
        if m:
            pid = int(m.group(1))
            continue
        m = re.match(r"\s*Volume\s*:\s*(-?[0-9]*\.?[0-9]+)", line)
        if pid is not None and m:
            vols[pid] = float(m.group(1))
    return vols


def label_residues(resseqs, resnames, lbd_first=LBD_FIRST):
    """['LEU406', ...] in UniProt numbering for a structure numbered from 1 at `lbd_first`. PURE.

    The offset is DERIVED from the same `lbd_first` the mapping used, never typed: resSeq 1 <-> 373."""
    out = []
    for r in sorted(resseqs):
        out.append(f"{resnames.get(r, 'UNK')}{r + lbd_first - 1}")
    return out


def site_choice_contrast(pockets, ref_lining, centroids):
    """DESCRIPTIVE contrast between the cavities the frozen gate ACCEPTED. PURE.

    ⚠ THIS DOES NOT AND MUST NOT FEED THE MATCHER. `pocket_tracking`'s thresholds were frozen 2026-07-11
    and re-tuning them after seeing a verdict is the outcome-selection defect this whole audit is about.
    What this returns is a DESCRIPTION of the two accepted cavities so a reader can see what each one IS,
    and it deliberately reports the raw set arithmetic rather than a verdict.

    `pockets`: [{"pocket": int, "residues": [int], "druggability": float}] — the ACCEPTED ones only.
    `ref_lining`: the mapped reference lining set (structure numbering).
    `centroids`: {pocket: (x,y,z)}.

    `relationship` is a descriptive label under thresholds stated inline, not a gate:
      SAME_CAVITY_RESEGMENTED  pairwise residue Jaccard >= 0.5 (the two cavities are mostly one set)
      OVERLAPPING_SUBPOCKETS   they share at least one residue but Jaccard < 0.5
      DISJOINT_CAVITIES        they share no lining residue at all
    """
    out = {"n_accepted": len(pockets), "pairs": []}
    for i in range(len(pockets)):
        for j in range(i + 1, len(pockets)):
            a, b = pockets[i], pockets[j]
            sa, sb = set(a["residues"]), set(b["residues"])
            inter, union = sa & sb, sa | sb
            jac = (len(inter) / len(union)) if union else 0.0
            ca_, cb_ = centroids.get(a["pocket"]), centroids.get(b["pocket"])
            sep = None
            if ca_ is not None and cb_ is not None:
                sep = round(sum((x - y) ** 2 for x, y in zip(ca_, cb_)) ** 0.5, 3)
            if not inter:
                rel = "DISJOINT_CAVITIES"
            elif jac >= 0.5:
                rel = "SAME_CAVITY_RESEGMENTED"
            else:
                rel = "OVERLAPPING_SUBPOCKETS"
            ref = set(ref_lining)
            out["pairs"].append({
                "pockets": [a["pocket"], b["pocket"]],
                "n_residues": [len(sa), len(sb)],
                "n_shared": len(inter),
                "pairwise_jaccard": round(jac, 4),
                "centroid_separation_ang": sep,
                "shared_residues": sorted(inter),
                "only_in_first": sorted(sa - sb),
                "only_in_second": sorted(sb - sa),
                "reference_lining_in_first_only": sorted((sa & ref) - sb),
                "reference_lining_in_second_only": sorted((sb & ref) - sa),
                "reference_lining_in_both": sorted(inter & ref),
                "relationship": rel,
            })
    return out


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
    resnames = resname_by_resseq(local)
    try:
        with open(os.path.join(workdir, stem + "_out", stem + "_info.txt")) as fh:
            volumes = parse_pocket_volumes(fh.read())
    except OSError:
        volumes = {}
    resseqs = sorted(ca)
    lining, span, numbering = map_lining(resseqs)
    ref = pt.orthosteric_reference(ca, lining_residues=lining,
                                   span=(min(span), max(span)) if span else (0, 0))
    cands = [{"pocket": int(num), "residues": sorted(int(r) for r in resids),
              "druggability": info[num]["druggability"]}
             for num, resids in resids_by_num.items()]
    mp = pt.match_params()
    hit = pt.match_pocket(cands, ref, ca_by_resnum=ca, **mp)

    # ⚠ EVERY CANDIDATE'S GATE ARITHMETIC, NOT JUST THE WINNER'S. Without this the artifact cannot
    # distinguish two readings that call for different responses: (a) the legacy classifier picked a
    # cavity that is NOT the mapped orthosteric site, versus (b) two cavities both ARE the site and the
    # composite rule prefers the less druggable one. `match_pocket` returns only the winner, so the
    # per-candidate table is recomputed here from the same pure predicates it uses.
    per_candidate = []
    for c in cands:
        m = pt.match_metrics(c["residues"], ref["lining_residues"])
        cen = pt.pocket_centroid(c["residues"], ca)
        cdist = None if cen is None else round(
            sum((a - b) ** 2 for a, b in zip(cen, ref["centroid"])) ** 0.5, 3)
        per_candidate.append({
            "pocket": c["pocket"], "druggability": c["druggability"],
            "n_overlap": m["n_overlap"], "jaccard": round(m["jaccard"], 4),
            "frac_recovered": round(m["frac_recovered"], 4), "centroid_dist_ang": cdist,
            "accepted_by_gate": bool(pt.accept_candidate(m, cdist, mp["jaccard_min"],
                                                         mp["frac_recovered_min"],
                                                         mp["centroid_max_ang"])),
        })
    per_candidate.sort(key=lambda r: -(r["druggability"] or 0.0))

    # ⚠ WHAT EACH CAVITY ACTUALLY IS. The verdict turns on which of two ACCEPTED cavities the frozen
    # rule calls 'the site', and that is unanswerable from the gate arithmetic alone — two cavities can
    # both clear it while being one re-segmented pocket or two genuinely different sites, and only the
    # second reading would put the rule in question. So the residues, their identities, their volumes
    # and the accepted-pair set arithmetic are recorded. NONE of it touches the matcher.
    by_num = {c["pocket"]: c for c in cands}
    centroids = {c["pocket"]: pt.pocket_centroid(c["residues"], ca) for c in cands}
    accepted_nums = [r["pocket"] for r in per_candidate if r["accepted_by_gate"]]
    accepted = [by_num[n] for n in accepted_nums]
    ref_lining = ref["lining_residues"]
    pocket_identity = {}
    for c in cands:
        shared = sorted(set(c["residues"]) & set(ref_lining))
        cen = centroids.get(c["pocket"])
        pocket_identity[str(c["pocket"])] = {
            "druggability": c["druggability"],
            "alpha_spheres": (info.get(c["pocket"]) or {}).get("alpha_spheres"),
            "volume_a3": volumes.get(c["pocket"]),
            "n_lining_residues": len(c["residues"]),
            "lining_resseqs": c["residues"],
            "lining_uniprot_labels": label_residues(c["residues"], resnames),
            "reference_lining_shared": shared,
            "reference_lining_shared_labels": label_residues(shared, resnames),
            "centroid": None if cen is None else [round(v, 3) for v in cen],
        }

    verdict = classify_score(hit is not None, None if hit is None else hit.get("druggability"))
    return {
        "site_choice_contrast": site_choice_contrast(accepted, ref_lining, centroids),
        "pocket_identity": pocket_identity,
        "reference_lining_labels": label_residues(ref_lining, resnames),
        "reference_centroid": [round(v, 3) for v in ref["centroid"]],
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
        "per_candidate_gate": per_candidate,
        "n_accepted_by_gate": sum(1 for r in per_candidate if r["accepted_by_gate"]),
        "most_druggable_cavity_anywhere": (per_candidate[0] if per_candidate else None),
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
