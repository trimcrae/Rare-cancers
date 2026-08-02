#!/usr/bin/env python3
"""
NR4A3 PARALOGUE-UNIQUE REACTIVE-RESIDUE map — the *categorical* selectivity axes ($0 CPU/CI).

WHY. The degrader plan's prospective stage currently seeks selectivity on ONE axis: a favourable-vs-frustrated
induced target-E3 interface, i.e. a ~1 kcal/mol thermodynamic margin resolved by methods whose own accuracy is
~1-1.7 kcal/mol. That axis has no validated prospective predictor (nr4a3-program-map.md thesis). This module maps the two
axes on which NR4A1/NR4A2 are not merely *disfavoured* but *structurally incapable*:

  AXIS 1 - a paralogue-unique NUCLEOPHILE. If NR4A3 carries a solvent-exposed cysteine at a position where both
    paralogues carry a non-nucleophile, an electrophilic handle placed on the degrader (pocket-proximal or on the
    linker) can form a covalent/reversible-covalent adduct on NR4A3 and CANNOT on NR4A1/2. This is exactly the
    mechanism that the repo has ALREADY verified for the reciprocal case: nrv04_cys_conservation.py showed the
    celastrol-reactive Cys551 is UNIQUE to NR4A1 (NR4A2 -> Y, NR4A3 -> T), i.e. the field's one demonstrated
    NR4A-family-selective degrader (NR-V04) most plausibly owes its selectivity to a paralogue-unique cysteine.
    That result is currently filed only as a CONFOUND; it is equally a PRECEDENT, available in reciprocal form.

  AXIS 2 - a paralogue-unique UBIQUITINATION SITE. Ubiquitin transfer needs a lysine inside the E2~Ub transfer
    zone. A lysine present in NR4A3 and absent at the aligned position in both paralogues is a site the paralogues
    cannot use at all, however well their ternary complex forms. Steering the transfer zone onto a UNIQUE lysine
    (and off the conserved ones) is a geometric constraint, not a free-energy contest.

WHAT. Pure stdlib. Two halves, both cheap:
  * SEQUENCE (needs internet -> run on a GitHub Actions runner; the dev sandbox's egress proxy 403s UniProt):
    fetch NR4A1/2/3 (+ EWSR1 for fusion context), Needleman-Wunsch align with NR4A3 as reference, and classify
    every NR4A3 Cys/Lys as unique-vs-both / unique-vs-one / conserved. Reciprocal direction reported too.
  * GEOMETRY (offline; uses the matched opened models already in the repo): relative SASA of each handle plus the
    distance from its reactive atom (Cys SG / Lys NZ) to the cryptic pocket and to the docked ligand poses, so a
    handle is labelled by whether a warhead, a short exit-vector arm, or a linker-borne group could reach it.

HONEST LIMITS (carried into the output). Sequence uniqueness is exact; everything downstream of it is a
hypothesis. Reachability uses ONE static opened conformer and a centroid/heavy-atom distance, not a docked
electrophile trajectory - it says "a group tethered this far from the pocket could plausibly reach", not "this
adduct forms". Intrinsic cysteine reactivity (pKa, local electrostatics, accessibility to a soft electrophile) is
NOT computed here. No claim of efficacy, safety, or degradation is made or implied.

Outputs: nr4a-paralogue-unique-residues.json (+ .md)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import nr4a_differential_atlas as atlas          # noqa: E402  (parse_pdb / shrake_rupley / residue_rsa)
import nrv04_cys_conservation as cyscons         # noqa: E402  (needleman_wunsch / fetch_fasta / _context)

ACCESSIONS = {"NR4A1": "P22736", "NR4A2": "P43354", "NR4A3": "Q92570", "EWSR1": "Q01844"}
PARALOGUES = ("NR4A1", "NR4A2")

# NR4A3 LBD == UniProt 373-626 == local residue 1..254 in results/nr4a3-matrix/nr4a3-opened.pdb.
LBD_FIRST, LBD_LAST = 373, 626
LOCAL_OFFSET = LBD_FIRST - 1                      # local_resid = uniprot_resid - 372

# The druggable cryptic pocket (fpocket pocket 5, druggability 0.495; research/modalities/nr4a-selectivity.json).
CRYPTIC_POCKET_UNIPROT = (406, 407, 410, 411, 412, 481, 484, 485, 531, 534)

# Reactive-atom name per residue type (the atom an electrophile / an E2~Ub thioester must reach).
REACTIVE_ATOM = {"CYS": "SG", "LYS": "NZ"}

# Documented in-frame EWSR1::NR4A3 breakpoints already used elsewhere in the repo (fusion_breakpoints.py,
# fusion-neoantigen-predictions.json "EWSR1_kept_residues: 1-264"). Scenarios, not a single asserted breakpoint.
EWSR1_KEPT_SCENARIOS = {"exon7_like_1_264": 264, "modelled_keep_200": 200, "exon12_like_1_349": 349}

# Reach classes for a handle's reactive atom measured from the cryptic pocket (see HONEST LIMITS).
#   in_pocket      - a warhead substituent could bear the electrophile directly
#   exit_vector    - a short rigid arm off the exit vector could reach
#   linker_borne   - within the span a PROTAC linker already crosses; the electrophile rides the linker
#   distal         - beyond a plausible tether from this pocket; usable only as an E3-interface contact
REACH_BANDS = ((8.0, "in_pocket"), (12.0, "exit_vector"), (22.0, "linker_borne"), (float("inf"), "distal"))


# =============================================================================================================
# sequence layer
# =============================================================================================================
def fetch_sequences(accessions=None, cache=None):
    """UniProt FASTA for each accession. If `cache` exists it is used instead (offline/test path); if the fetch
    succeeds and `cache` is given the sequences are written there."""
    accessions = accessions or ACCESSIONS
    if cache and os.path.exists(cache):
        with open(cache) as f:
            seqs = json.load(f)
        missing = [n for n in accessions if n not in seqs]
        if not missing:
            return seqs, "cache:" + os.path.basename(cache)
    seqs = {name: cyscons.fetch_fasta(acc) for name, acc in accessions.items()}
    if cache:
        with open(cache, "w") as f:
            json.dump(seqs, f)
    return seqs, "UniProt FASTA (rest.uniprot.org)"


def aligned_partner(aln_ref, aln_other, ref_resnum):
    """Residue (and 1-based index in `other`) opposite 1-based `ref_resnum` of the reference. '-' == gap."""
    return cyscons.aligned_residue(aln_ref, aln_other, ref_resnum)


def _affine_partner_map(seq_ref, seq_other):
    """{1-based ref position -> (partner residue, 1-based partner position or None)} using the atlas's AFFINE-gap
    BLOSUM62 aligner. A SECOND, independent alignment of the same pair — see `classify_positions`."""
    out = {}
    for ia, ib in atlas.nw_align(seq_ref, seq_other):
        if ia is None:
            continue
        out[ia + 1] = (seq_other[ib], ib + 1) if ib is not None else ("-", None)
    return out


def classify_positions(seqs, ref="NR4A3", residue_types=("C", "K"), others=PARALOGUES):
    """For every position of `ref` whose residue is in `residue_types`, report the aligned residue in each of
    `others` and whether the reference residue type is UNIQUE (absent in that partner at the aligned position).

    ALIGNMENT ROBUSTNESS (deliberate, and load-bearing). Uniqueness is a claim ABOUT AN ALIGNMENT, so it is
    computed TWICE with independent aligners — the simple match/mismatch linear-gap NW already used for the
    NR-V04 Cys551 leg, and the atlas's affine-gap (Gotoh) BLOSUM62 aligner — and each row records whether the two
    AGREE. Only `unique_vs_both AND alignment_robust` may be used as a design premise; a disagreement means the
    local alignment is ambiguous and the position needs a structural superposition, not a sequence call. (This
    matters here: the two aligners already disagree on which NR4A3 position the NR4A1 celastrol Cys551 maps to.)

    Returns a list of dicts, one per reference position, ordered by residue number. Pure function of the
    sequences — unit-testable with synthetic input, no network."""
    ref_seq = seqs[ref]
    alns = {o: cyscons.needleman_wunsch(ref_seq, seqs[o]) for o in others}
    affine = {o: _affine_partner_map(ref_seq, seqs[o]) for o in others}
    rows = []
    for i, aa in enumerate(ref_seq, start=1):
        if aa not in residue_types:
            continue
        row = {"residue": aa, "resnum": i, "context": cyscons._context(ref_seq, i), "partners": {}}
        agree = True
        for o in others:
            aln_ref, aln_oth = alns[o]
            res, idx = aligned_partner(aln_ref, aln_oth, i)
            res2, idx2 = affine[o].get(i, ("-", None))
            same1, same2 = res == aa, res2 == aa
            if same1 != same2:
                agree = False
            row["partners"][o] = {
                "residue": res, "resnum": idx,
                "same_type": same1,
                "affine_residue": res2, "affine_resnum": idx2, "affine_same_type": same2,
                "aligners_agree": same1 == same2,
                "context": cyscons._context(seqs[o], idx) if idx else "(aligned to a gap)",
            }
        row["unique_vs_both"] = not any(p["same_type"] for p in row["partners"].values())
        row["unique_vs_both_affine"] = not any(p["affine_same_type"] for p in row["partners"].values())
        row["alignment_robust"] = agree
        row["unique_vs"] = sorted(o for o, p in row["partners"].items() if not p["same_type"])
        row["in_lbd"] = LBD_FIRST <= i <= LBD_LAST
        rows.append(row)
    return rows


def reciprocal_unique(seqs, residue_types=("C", "K"), ref="NR4A3", others=PARALOGUES):
    """The other direction: positions where a PARALOGUE carries the reactive residue and NR4A3 does not. These
    are anti-handles - sites where a paralogue is chemically addressable and NR4A3 is not (the NR-V04 / NR4A1
    Cys551 situation), and therefore also the sites a *counter-screen* must cover."""
    out = {}
    for o in others:
        aln_o, aln_ref = cyscons.needleman_wunsch(seqs[o], seqs[ref])
        rows = []
        for i, aa in enumerate(seqs[o], start=1):
            if aa not in residue_types:
                continue
            res, idx = aligned_partner(aln_o, aln_ref, i)
            if res != aa:
                rows.append({"residue": aa, "resnum": i, "context": cyscons._context(seqs[o], i),
                             "nr4a3_residue": res, "nr4a3_resnum": idx})
        out[o] = rows
    return out


def fusion_lysine_scenarios(ewsr1_seq, scenarios=None):
    """Lysines contributed by the EWSR1 moiety of EWSR1::NR4A3 under documented breakpoint scenarios. These are
    sites present on the FUSION and absent from NR4A1/NR4A2 entirely (different protein) AND from the NR4A3
    LBD construct - the strongest categorical ubiquitination handle available, and the one the LBD-only atlas
    structurally cannot see. Scenario-based: the breakpoint is a modelling choice, not an assertion."""
    scenarios = scenarios or EWSR1_KEPT_SCENARIOS
    out = {}
    for label, keep in scenarios.items():
        seg = ewsr1_seq[:keep]
        out[label] = {"ewsr1_residues_kept": keep,
                      "n_lysines": seg.count("K"),
                      "lysine_positions": [i for i, a in enumerate(seg, start=1) if a == "K"]}
    return out


# =============================================================================================================
# geometry layer (offline; matched opened models already in the repo)
# =============================================================================================================
def _reach_class(d):
    for cut, label in REACH_BANDS:
        if d < cut:
            return label
    return "distal"


def _read_sdf_coords(path):
    """Minimal multi-record V2000 SDF reader -> [(title, [(x,y,z,element), ...]), ...]. No RDKit needed."""
    mols, lines, i = [], open(path).read().splitlines(), 0
    while i + 3 < len(lines):
        title = lines[i].strip()
        try:
            n_atoms = int(lines[i + 3][0:3])
        except (ValueError, IndexError):
            break
        coords = []
        for j in range(i + 4, min(i + 4 + n_atoms, len(lines))):
            L = lines[j]
            try:
                coords.append((float(L[0:10]), float(L[10:20]), float(L[20:30]), L[31:34].strip()))
            except ValueError:
                break
        mols.append((title, coords))
        k = i
        while k < len(lines) and lines[k].strip() != "$$$$":
            k += 1
        i = k + 1
    return mols


def geometry_annotations(struct_dir, docked_sdf=None):
    """Per-UniProt-residue geometry for the NR4A3 opened model: relative SASA, plus the distance from the
    residue's reactive atom to (a) the nearest cryptic-pocket heavy atom, (b) the nearest docked-ligand heavy
    atom. Returns {uniprot_resid: {...}}; residues outside the model simply do not appear."""
    pdb = os.path.join(struct_dir, "nr4a3-opened.pdb")
    residues, atoms = atlas.parse_pdb(pdb)
    sasa = atlas.shrake_rupley(atoms)
    rsa = atlas.residue_rsa(residues, sasa)

    by_local = {}
    for a in atoms:
        by_local.setdefault(a["resid"], []).append(a)

    pocket_atoms = []
    for u in CRYPTIC_POCKET_UNIPROT:
        pocket_atoms.extend(by_local.get(u - LOCAL_OFFSET, []))

    ligands = _read_sdf_coords(docked_sdf) if docked_sdf and os.path.exists(docked_sdf) else []

    out = {}
    for local, ats in by_local.items():
        uni = local + LOCAL_OFFSET
        resname = ats[0]["resname"]
        want = REACTIVE_ATOM.get(resname)
        if want is None:
            continue
        rx = [a for a in ats if a["name"] == want]
        if not rx:
            continue
        p = (rx[0]["x"], rx[0]["y"], rx[0]["z"])
        d_pocket = min((math.dist(p, (a["x"], a["y"], a["z"])) for a in pocket_atoms), default=None)
        d_lig, lig_name = None, None
        for title, coords in ligands:
            d = min((math.dist(p, (c[0], c[1], c[2])) for c in coords), default=None)
            if d is not None and (d_lig is None or d < d_lig):
                d_lig, lig_name = d, title
        out[uni] = {
            "local_resid": local, "resname": resname, "reactive_atom": want,
            "rsa": round(rsa.get(local, 0.0), 3),
            "exposed": rsa.get(local, 0.0) >= atlas.EXPOSED_RSA,
            "dist_to_cryptic_pocket_A": None if d_pocket is None else round(d_pocket, 2),
            "dist_to_nearest_docked_ligand_A": None if d_lig is None else round(d_lig, 2),
            "nearest_docked_ligand": lig_name,
            "reach_class": None if d_pocket is None else _reach_class(d_pocket),
        }
    return out


# =============================================================================================================
# assembly
# =============================================================================================================
def build(seqs, struct_dir, docked_sdf=None):
    cys = classify_positions(seqs, residue_types=("C",))
    lys = classify_positions(seqs, residue_types=("K",))
    geom = geometry_annotations(struct_dir, docked_sdf) if os.path.isdir(struct_dir) else {}

    def _join(rows):
        for r in rows:
            g = geom.get(r["resnum"])
            r["geometry"] = g if g else {"note": "outside the modelled LBD construct (373-626) — no geometry"}
        return rows

    cys, lys = _join(cys), _join(lys)
    # DESIGN-GRADE uniqueness requires BOTH aligners to agree (see classify_positions); the non-robust ones are
    # kept in the full lists but never enter a gate or a design premise.
    uniq_cys = [r for r in cys if r["unique_vs_both"] and r["alignment_robust"]]
    uniq_lys = [r for r in lys if r["unique_vs_both"] and r["alignment_robust"]]
    ambiguous = [r["residue"] + str(r["resnum"]) for r in cys + lys if not r["alignment_robust"]]

    def _exposed_unique(rows):
        return [r for r in rows if r["geometry"].get("exposed")]

    return {
        "_title": "NR4A3 paralogue-unique reactive residues — the categorical selectivity axes",
        "_why": ("A residue type present in NR4A3 and absent at the aligned position in BOTH paralogues is a "
                 "selectivity mechanism that does not depend on winning a ~1 kcal/mol free-energy contest: "
                 "cysteines gate covalent capture, lysines gate ubiquitin transfer."),
        "_method": ("UniProt FASTA + Needleman-Wunsch global alignment (NR4A3 as reference) for uniqueness; "
                    "Shrake-Rupley RSA + reactive-atom distances on the matched opened LBD model for "
                    "reachability. Pure stdlib."),
        "_limits": [
            "Sequence uniqueness is exact; everything downstream (reachability, adduct formation, transfer "
            "competence) is a HYPOTHESIS generated for testing, not a result.",
            "Reachability uses ONE static opened conformer and a heavy-atom distance to the cryptic pocket — "
            "not a docked electrophile or a linker conformer search.",
            "Intrinsic cysteine reactivity (pKa, local electrostatics, hard/soft preference) is NOT computed.",
            "Lysine uniqueness does not by itself establish ubiquitination competence — that is a geometry "
            "question for the ternary/CRL stage.",
            "No efficacy, safety, therapeutic-window or clinical claim is made or implied.",
        ],
        "accessions": ACCESSIONS,
        "sequence_lengths": {k: len(v) for k, v in seqs.items()},
        "cryptic_pocket_uniprot": list(CRYPTIC_POCKET_UNIPROT),
        "reach_bands_A": {label: cut for cut, label in REACH_BANDS if cut != float("inf")},
        "nr4a3_cysteines": cys,
        "nr4a3_lysines": lys,
        "nr4a3_unique_cysteines": uniq_cys,
        "nr4a3_unique_lysines": uniq_lys,
        "reciprocal_paralogue_unique": reciprocal_unique(seqs),
        "fusion_context_ewsr1_lysines": fusion_lysine_scenarios(seqs["EWSR1"]) if "EWSR1" in seqs else {},
        "summary": {
            "n_nr4a3_cysteines": len(cys),
            "n_unique_cysteines_vs_both": len(uniq_cys),
            "n_unique_cysteines_exposed": len(_exposed_unique(uniq_cys)),
            "n_nr4a3_lysines": len(lys),
            "n_unique_lysines_vs_both": len(uniq_lys),
            "n_unique_lysines_exposed": len(_exposed_unique(uniq_lys)),
            "alignment_ambiguous_positions": ambiguous,
            "uniqueness_rule": "unique_vs_both AND alignment_robust (both aligners agree)",
        },
        "gate": _gate(uniq_cys, uniq_lys, _exposed_unique),
    }


def _gate(uniq_cys, uniq_lys, exposed_fn):
    """The cheap categorical-axis GO/NO-GO. Deliberately weaker than a claim: it asks only whether the axes
    EXIST to be designed against, which is what decides where the next $0 of search effort goes."""
    ec, el = exposed_fn(uniq_cys), exposed_fn(uniq_lys)
    reachable = [r for r in ec if r["geometry"].get("reach_class") in ("in_pocket", "exit_vector", "linker_borne")]
    axis1 = bool(reachable)
    axis2 = bool(el)
    if axis1 and axis2:
        verdict = ("GO on BOTH categorical axes — at least one exposed NR4A3-unique cysteine is within tether "
                   "range of the warhead pocket (covalent-capture axis) AND at least one exposed NR4A3-unique "
                   "lysine exists (ubiquitination-site axis). Search these BEFORE, not after, the ~1 kcal/mol "
                   "interface-thermodynamics axis.")
    elif axis1 or axis2:
        verdict = ("PARTIAL — only one categorical axis is available; it still outranks the interface-"
                   "thermodynamics axis on expected information per dollar, but the plan must not claim two.")
    else:
        verdict = ("NO categorical axis — selectivity must come from the induced-interface thermodynamics "
                   "alone, which is the hardest and least-validated route. Say so explicitly in the paper.")
    return {
        "question": ("Does NR4A3 present a reactive residue that BOTH paralogues structurally lack, positioned "
                     "so a degrader could exploit it?"),
        "covalent_axis_available": axis1,
        "unique_lysine_axis_available": axis2,
        "tether_reachable_unique_cysteines": [r["resnum"] for r in reachable],
        "exposed_unique_lysines": [r["resnum"] for r in el],
        "verdict": verdict,
    }


def to_markdown(d):
    L = [f"# {d['_title']}", "", d["_why"], "", f"*Method:* {d['_method']}", ""]
    s = d["summary"]
    L += ["## Summary", "",
          f"- NR4A3 cysteines: **{s['n_nr4a3_cysteines']}**, of which **{s['n_unique_cysteines_vs_both']}** are "
          f"absent in BOTH paralogues ({s['n_unique_cysteines_exposed']} solvent-exposed).",
          f"- NR4A3 lysines: **{s['n_nr4a3_lysines']}**, of which **{s['n_unique_lysines_vs_both']}** are absent "
          f"in BOTH paralogues ({s['n_unique_lysines_exposed']} solvent-exposed).", ""]

    def _table(rows, title):
        out = [f"## {title}", "",
               "| NR4A3 | NR4A1 | NR4A2 | RSA | d(pocket) Å | d(nearest docked lig) Å | reach |",
               "|---|---|---|---|---|---|---|"]
        for r in rows:
            g = r["geometry"]
            p1, p2 = r["partners"]["NR4A1"], r["partners"]["NR4A2"]
            out.append("| {}{} | {}{} | {}{} | {} | {} | {} | {} |".format(
                r["residue"], r["resnum"], p1["residue"], p1["resnum"] or "-",
                p2["residue"], p2["resnum"] or "-",
                g.get("rsa", "—"), g.get("dist_to_cryptic_pocket_A", "—"),
                g.get("dist_to_nearest_docked_ligand_A", "—"), g.get("reach_class", "—")))
        return out + [""]

    L += _table(d["nr4a3_unique_cysteines"], "Axis 1 — NR4A3-unique cysteines (covalent-capture handles)")
    L += _table(d["nr4a3_unique_lysines"], "Axis 2 — NR4A3-unique lysines (ubiquitination-site handles)")

    rec = d.get("reciprocal_paralogue_unique", {})
    if rec:
        L += ["## Reciprocal — reactive residues a paralogue has and NR4A3 lacks", "",
              "(These are the anti-handles: sites where a paralogue is addressable and NR4A3 is not. "
              "NR4A1 Cys551 — the celastrol/NR-V04 site — is the precedent this whole map mirrors.)", ""]
        for o, rows in rec.items():
            cys_rows = [r for r in rows if r["residue"] == "C"]
            L.append(f"- **{o}**: {len(cys_rows)} unique cysteines "
                     f"({', '.join('C%d' % r['resnum'] for r in cys_rows[:12])}"
                     f"{' …' if len(cys_rows) > 12 else ''})")
        L.append("")

    fus = d.get("fusion_context_ewsr1_lysines", {})
    if fus:
        L += ["## Fusion context — lysines the EWSR1 moiety contributes", "",
              "Present on EWSR1::NR4A3, absent from NR4A1/NR4A2 entirely and from the NR4A3 LBD construct. "
              "Breakpoint scenarios, not an asserted breakpoint.", "",
              "| scenario | EWSR1 residues kept | lysines |", "|---|---|---|"]
        for k, v in fus.items():
            L.append(f"| {k} | 1–{v['ewsr1_residues_kept']} | **{v['n_lysines']}** |")
        L.append("")

    g = d["gate"]
    L += ["## Gate", "", f"**{g['verdict']}**", "", "## Honest limits", ""]
    L += [f"- {x}" for x in d["_limits"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--struct-dir", default=os.path.join(REPO, "results", "nr4a3-matrix"))
    ap.add_argument("--docked-sdf", default=os.path.join(REPO, "results", "nr4a3-matrix", "docked_nr4a3.sdf"))
    ap.add_argument("--seq-cache", default=os.path.join(HERE, "nr4a-sequences-cache.json"),
                    help="reuse/write fetched UniProt sequences here (lets the analysis re-run offline)")
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a-paralogue-unique-residues.json"))
    args = ap.parse_args(argv)

    seqs, source = fetch_sequences(cache=args.seq_cache)
    print(f"[seq] source = {source}; lengths = " + ", ".join(f"{k}:{len(v)}" for k, v in seqs.items()), flush=True)
    data = build(seqs, args.struct_dir, args.docked_sdf)
    data["_source"] = source
    with open(args.out, "w") as f:
        json.dump(data, f, indent=1)
    md = os.path.splitext(args.out)[0] + ".md"
    with open(md, "w") as f:
        f.write(to_markdown(data))
    print(json.dumps(data["summary"], indent=1), flush=True)
    print(data["gate"]["verdict"], flush=True)
    print(f"[out] {os.path.relpath(args.out, REPO)} + {os.path.relpath(md, REPO)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
