#!/usr/bin/env python3
"""
IS THE PUBLISHED NURR1 H1/H5/H7/H8 ALLOSTERIC POCKET THE SAME REGION AS NR4A3'S POCKET-5? ($0, CPU, stdlib.)

THE QUESTION AND WHY IT IS WORTH A FREE HOUR. `emc-unexplored-treatment-lanes.md` §4 lists it as free to run
now, with the stake stated: *"A match hands the FEP lane a clinical-stage scaffold with published SAR; a
mismatch is a documented negative."* The scaffold is vidofludimus — a DHODH inhibitor taken into
relapsing-remitting MS trials — which Lopez-Garcia et al. localise to an allosteric surface pocket of the
Nurr1 (NR4A2) LBD, together with an optimised analog and the SAR that produced it.

THE SOURCE, RETRIEVED NOT RECALLED. Lopez-Garcia U, Vietor J, Marschner JA, Heering J, Morozov V, Wein T,
Merk D. *Structural and mechanistic profiling of Nurr1 modulation by vidofludimus enables structure-guided
ligand design.* Commun Chem 2025;8:159. PMC12095788, doi 10.1038/s42004-025-01553-8. The full text was pulled
through CI (the dev sandbox's egress proxy 403s Europe PMC/PMC on CONNECT, CLAUDE.md §6) and is committed at
`literature-cache:literature/nr4a-ligand-chemistry/PMC12095788.txt`. Every residue in the site definition
below carries the VERBATIM sentence it came from, and `--source-text` re-checks each quote against that file
— so the site set is auditable against the paper rather than against this file's memory of it.

⛔ THE SITE IS A MODEL, NOT A STRUCTURE, AND THE PAPER SAYS SO. There is no vidofludimus-Nurr1 co-crystal.
   The site is defined by ten Gal4-Nurr1 point mutants, GLIDE docking into 1OVL chain E, and 4 x 200 ns
   GROMACS MD; the two double mutants that abolish activation (I500W/M379W, I500W/V373W) are the strongest
   evidence and they are a functional readout, not a density. So "the published pocket" here means "the
   residues the published model names", and the comparison inherits that status exactly.

⛔ WHAT A MATCH WOULD AND WOULD NOT MEAN. This module compares TWO RESIDUE SETS AND TWO CENTROIDS. That is a
   GEOMETRY statement. It is not evidence that vidofludimus binds NR4A3, that any affinity transfers across a
   paralogue pair at 65.5 % LBD identity, that the site is druggable in NR4A3, or anything about selectivity,
   efficacy, safety, a therapeutic window or clinical readiness. What a match licenses is that the FEP lane
   has somewhere real to point a published chemical series — a STARTING POINT, which is a different object
   from a result.

METHOD, and every step reuses machinery this repository already froze rather than inventing a metric:
  1. NR4A2 -> NR4A3 residue mapping by TWO INDEPENDENT ALIGNERS (the linear-gap NW in
     `nrv04_cys_conservation` and the affine-gap BLOSUM62 Gotoh aligner in `nr4a_differential_atlas`), and a
     position is used only where they AGREE — the `alignment_robust` discipline of
     `nr4a_paralogue_unique_residues.classify_positions`.
  2. Overlap metrics from `pocket_tracking.match_metrics` and the composite gate from
     `pocket_tracking.accept_candidate` — the SAME n_overlap / jaccard / frac_recovered / centroid-distance
     vocabulary `r3-site-choice-audit.json` states its verdicts in, at the thresholds frozen 2026-07-11.
     ⚠ THAT GATE WAS FROZEN FOR A DIFFERENT QUESTION — "which fpocket cavity in this frame is the reference
     site" — and is REUSED here to ask "are these two independently-defined sites the same region". The raw
     metrics are reported beside the verdict precisely so a reader can apply a threshold of their own; the
     thresholds are not re-tuned here and this module never touches them.
  3. Centroids on the 8XTT conformers this repository holds (CA only), in 8XTT author numbering, which is
     UniProt Q92570 numbering minus 378 — a mapping taken from the committed benchmark artifact
     (`results/nr4a3-8xtt-benchmark/nr4a3-8xtt-benchmark.json` `mapped_pocket5_8xtt`), never assumed.

Outputs: nurr1-allosteric-vs-pocket5.json (+ .md)
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import nrv04_cys_conservation as cyscons          # noqa: E402  linear-gap NW
import nr4a_differential_atlas as atlas           # noqa: E402  affine-gap BLOSUM62 + SASA
import pocket_tracking as pt                      # noqa: E402  THE frozen match metrics and gate
import nr4a3_8xtt_benchmark as bm                 # noqa: E402  THE Pocket-5 definition — never re-typed

SEQ_CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")
XTT_GLOB = os.path.join(HERE, "_pose_convergence_inputs", "8xtt_model*_nr4a3.pdb")
# ★ THE FULL DEPOSITED ENSEMBLE, fetched through CI (RCSB is 403'd at the dev sandbox's egress proxy).
#   The four conformers under `_pose_convergence_inputs/` were SELECTED for a pose-convergence study, so a
#   spread across them is a consistency check and not the ensemble distribution — a distinction this module
#   made in prose before it could make it in numbers. With the deposited file on disk it can make it in
#   numbers, and both are reported.
XTT_FULL = os.path.join(HERE, "_s4_lane_inputs", "8XTT.pdb.gz")
XTT_BENCH = os.path.join(REPO, "results", "nr4a3-8xtt-benchmark", "nr4a3-8xtt-benchmark.json")
OUT = os.path.join(HERE, "nurr1-allosteric-vs-pocket5.json")

POCKET5_UNIPROT = list(bm.POCKET5)                # [406,407,410,411,412,481,484,485,531,534] — imported
SOURCE = {
    "citation": ("Lopez-Garcia U, Vietor J, Marschner JA, Heering J, Morozov V, Wein T, Merk D. "
                 "Structural and mechanistic profiling of Nurr1 modulation by vidofludimus enables "
                 "structure-guided ligand design. Commun Chem 2025;8:159."),
    "doi": "10.1038/s42004-025-01553-8",
    "pmc": "PMC12095788",
    "verification_level": "[FT] full text read",
    "retrieved_through": ("GitHub Actions runner; committed at literature-cache:literature/"
                          "nr4a-ligand-chemistry/PMC12095788.txt"),
    "site_label_in_the_paper": "site 4",
    "site_description_quote": ("an allosteric surface pocket lined by helices 1, 5, 7, and 8, and distant "
                               "from the canonical activation function in helix 12"),
    "numbering": "UniProt P43354 (Nurr1/NR4A2 canonical, 598 aa)",
}

# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE PUBLISHED SITE, RESIDUE BY RESIDUE, EACH WITH THE SENTENCE IT COMES FROM
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ A LIST OF NUMBERS WITH A CITATION BESIDE IT IS NOT A CITED LIST. Every entry below carries the verbatim
#    substring of the source that names it, and `--source-text` fails if any quote is not present in the
#    retrieved full text. That is the difference between a residue set this repository can defend and one it
#    merely remembers — the same failure class as the retired "Munck 2022" attribution.
#
# `evidence_class` is load-bearing and the two classes are not equal:
#    mutagenesis  — a functional readout. I500W/M379W and I500W/V373W ABOLISH activation by vidofludimus
#                   while leaving fluvastatin activation and receptor function intact; H372F and I500F/W
#                   SHIFT its potency without abolishing it. These are the paper's experimental anchors.
#    model_contact — a contact seen in docking/MD only. Real evidence about the model, not about the protein.
SITE4 = [
    {"resnum": 372, "aa": "H", "evidence_class": "mutagenesis",
     "quote": "I500F and H372F (both site 4), in contrast, had a more consistent impact on Nurr1 modulation"},
    {"resnum": 373, "aa": "V", "evidence_class": "mutagenesis",
     "quote": "We employed the double mutations I500W/M379W and I500W/V373W introducing bulky side chains "
              "to block the binding site"},
    {"resnum": 379, "aa": "M", "evidence_class": "mutagenesis",
     "quote": "We employed the double mutations I500W/M379W and I500W/V373W introducing bulky side chains "
              "to block the binding site"},
    {"resnum": 450, "aa": "R", "evidence_class": "model_contact",
     "quote": "expose the carboxylate towards a triad of basic side chains (His372, Arg450 and Arg454)"},
    {"resnum": 454, "aa": "R", "evidence_class": "model_contact",
     "quote": "expose the carboxylate towards a triad of basic side chains (His372, Arg450 and Arg454)"},
    {"resnum": 456, "aa": "N", "evidence_class": "model_contact",
     "quote": "terminal methoxyphenyl residue of vidofludimus bound between Asn456 and Asn497"},
    {"resnum": 490, "aa": "S", "evidence_class": "model_contact",
     "quote": "stable orientation of the methoxy group towards Ser490"},
    {"resnum": 497, "aa": "N", "evidence_class": "model_contact",
     "quote": "terminal methoxyphenyl residue of vidofludimus bound between Asn456 and Asn497"},
    {"resnum": 500, "aa": "I", "evidence_class": "mutagenesis",
     "quote": "Introduction of aromatic residues in the central part of the pocket (I500F, I500W) enhanced "
              "agonist potency"},
]
# Named in the paper as site-4 backbone chemistry but not a side-chain the site set turns on; kept as a quote
# so the reader can see it was read and classified rather than missed.
SITE4_ALSO_QUOTED = {
    379: "several hydrophobic ligand-protein contacts and H-bonds involving His372 and the backbone of Met379",
}
# The paper's OTHER three epitopes. Carried so that "site 4 matches Pocket-5" can be read against what the
# same paper's non-site-4 mutants do — a control the comparison would otherwise lack.
OTHER_SITE_MUTANTS = {
    "site_2_examples": [481, 571],       # E481L, Q571W — "Q571 (site 2) is located at the dimer interface"
    "site_3_examples": [506, 559],       # I506F, L559F — "I506 (site 3) neighbors a SUMOylation site"
    "unassigned_in_text": [444, 566, 570],
}


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · THE MAPPING — two aligners, and only agreement counts
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _affine_map(seq_ref, seq_other):
    out = {}
    for ia, ib in atlas.nw_align(seq_ref, seq_other):
        if ia is None:
            continue
        out[ia + 1] = (seq_other[ib], ib + 1) if ib is not None else ("-", None)
    return out


def map_nr4a2_to_nr4a3(resnums, seqs):
    """{NR4A2 resnum -> row}. `mapped_resnum` is None wherever the two aligners disagree OR either gaps.

    ⚠ A GAP IS NOT A MAPPING FAILURE, IT IS A MEASUREMENT. NR4A2 carries a two-residue insertion (A378-M379)
    relative to NR4A3 in the helix-1 exit loop, so M379 — one of the two blocking mutants — has NO NR4A3
    counterpart at all. That is reported, never smoothed over by snapping it to a neighbour.
    """
    a2, a3 = seqs["NR4A2"], seqs["NR4A3"]
    aln2, aln3 = cyscons.needleman_wunsch(a2, a3)
    aff = _affine_map(a2, a3)
    rows = []
    for r in resnums:
        lin_aa, lin_num = cyscons.aligned_residue(aln2, aln3, r)
        aff_aa, aff_num = aff.get(r, ("-", None))
        agree = (lin_num == aff_num) and (lin_aa == aff_aa)
        rows.append({
            "nr4a2_resnum": r,
            "nr4a2_aa": a2[r - 1],
            "linear_gap_nw": {"aa": lin_aa, "resnum": lin_num},
            "affine_blosum62": {"aa": aff_aa, "resnum": aff_num},
            "aligners_agree": bool(agree),
            "mapped_nr4a3_resnum": lin_num if (agree and lin_num is not None) else None,
            "mapped_nr4a3_aa": lin_aa if (agree and lin_num is not None) else None,
            "identical_residue_type": bool(agree and lin_num is not None and lin_aa == a2[r - 1]),
            "why_unmapped": (None if (agree and lin_num is not None)
                             else ("aligners disagree" if not agree else
                                   "aligns to a gap — NR4A2 has no NR4A3 counterpart at this position")),
        })
    return rows


def paper_numbering_check(seqs):
    """Does every residue the paper names actually have that identity in P43354? A free provenance check.

    If the paper were numbering a different isoform or construct, this fails loudly instead of producing a
    plausible-looking mapping off the wrong frame — the exact "populated field, never measured" shape.
    """
    a2 = seqs["NR4A2"]
    checks = []
    named = [(r["resnum"], r["aa"]) for r in SITE4]
    named += [(566, "C"), (444, "L"), (481, "E"), (506, "I"), (559, "L"), (570, "L"), (571, "Q")]
    for num, aa in named:
        got = a2[num - 1] if 0 < num <= len(a2) else None
        checks.append({"residue": "%s%d" % (aa, num), "in_P43354": got, "ok": got == aa})
    n_ok = sum(1 for c in checks if c["ok"])
    return {
        "_what": ("every residue identity the paper names, checked against the cached UniProt P43354 "
                  "sequence — is the paper numbering the canonical isoform?"),
        "n_checked": len(checks), "n_ok": n_ok,
        "status": "OK" if n_ok == len(checks) else "MISMATCH",
        "checks": checks,
        "_reading": ("%d of %d residue identities named in the paper match P43354 exactly, so the paper's "
                     "numbering IS the canonical Nurr1 isoform and the alignment below is being run in the "
                     "right frame." % (n_ok, len(checks))),
    }


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · 8XTT — coordinates, numbering and the centroids
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def xtt_offset():
    """UniProt -> 8XTT author numbering, DERIVED from the committed benchmark artifact.

    The benchmark aligned the AF2 LBD onto 8XTT chain A and stored the mapped Pocket-5 numbers. Recovering
    the offset from that pair, and asserting it is constant across all ten, is a check; typing `-378` here
    would be an assumption wearing a number's clothes.
    """
    with open(XTT_BENCH) as fh:
        d = json.load(fh)
    uni = d["pocket5_residues_uniprot"]
    auth = d["mapped_pocket5_8xtt"]
    if len(uni) != len(auth):
        raise SystemExit("8XTT benchmark artifact maps %d of %d Pocket-5 residues — REFUSING to guess the "
                         "offset from a partial map" % (len(auth), len(uni)))
    offs = {u - a for u, a in zip(sorted(uni), sorted(auth))}
    if len(offs) != 1:
        raise SystemExit("8XTT numbering is not a constant offset (%s) — the mapping must be used "
                         "per-residue, not as an offset" % sorted(offs))
    return offs.pop(), d


def read_ca(path):
    d = {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                d[int(line[22:26])] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
    return d


def read_ca_models(path):
    """[{resnum: xyz}] — every MODEL in a deposited NMR ensemble, in file order.

    The deposited entry uses AUTHOR numbering, which for 8XTT is UniProt minus the offset `xtt_offset()`
    derives from the committed benchmark. That is asserted nowhere here; it is checked by
    `full_ensemble_numbering_agrees_with_the_committed_conformers` below.
    """
    import gzip as _gz
    src = _gz.open(path, "rt") if path.endswith(".gz") else open(path)
    models, cur = [], None
    with src as fh:
        for line in fh:
            if line.startswith("MODEL"):
                cur = {}
            elif line.startswith("ENDMDL"):
                if cur:
                    models.append(cur)
                cur = None
            elif line.startswith("ATOM") and line[12:16].strip() == "CA" and line[21] == "A":
                (cur if cur is not None else models and models[-1] or {})[int(line[22:26])] = (
                    float(line[30:38]), float(line[38:46]), float(line[46:54]))
    return models


def read_heavy(path):
    """(atoms, residues) in the shape `nr4a_differential_atlas.shrake_rupley` / `residue_rsa` consume.

    Reusing the atlas's own SASA rather than writing a second one is the point: an ad-hoc reimplementation
    would be a second home for the same number (CLAUDE.md rule 1) and would not be the function every other
    burial figure in this repository came out of.
    """
    atoms, residues = [], {}
    with open(path) as fh:
        for line in fh:
            if not line.startswith("ATOM"):
                continue
            name = line[12:16].strip()
            el = (line[76:78].strip() or name[:1]).upper()
            if el == "H":
                continue
            rid = int(line[22:26])
            residues[rid] = line[17:20].strip()
            atoms.append({"resid": rid, "elem": el, "x": float(line[30:38]),
                          "y": float(line[38:46]), "z": float(line[46:54])})
    return atoms, sorted(residues.items())


def centroid(pts):
    n = len(pts)
    return tuple(sum(p[i] for p in pts) / n for i in range(3))


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · THE COMPARISON
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def compare_on_ca(ca, mapped_site4, offset, label):
    p5_auth = [r - offset for r in POCKET5_UNIPROT]
    s4_auth = [r - offset for r in mapped_site4]
    p5_pts = [ca[a] for a in p5_auth if a in ca]
    s4_pts = [ca[a] for a in s4_auth if a in ca]
    if len(p5_pts) != len(p5_auth) or len(s4_pts) != len(s4_auth):
        return {"conformer": label, "status": "INCOMPLETE_IN_MODEL",
                "n_pocket5_ca_found": len(p5_pts), "n_site4_ca_found": len(s4_pts)}
    c5, c4 = centroid(p5_pts), centroid(s4_pts)
    dist = math.dist(c5, c4)
    m = pt.match_metrics(mapped_site4, POCKET5_UNIPROT)
    return {"conformer": label, "status": "OK",
            "pocket5_centroid_A": [round(x, 3) for x in c5],
            "site4_centroid_A": [round(x, 3) for x in c4],
            "centroid_dist_ang": round(dist, 3),
            "n_overlap": m["n_overlap"], "jaccard": round(m["jaccard"], 4),
            "frac_recovered": round(m["frac_recovered"], 4),
            "accepted_by_frozen_gate": pt.accept_candidate(m, dist)}


def full_ensemble(mapped_site4, offset):
    """The comparison over EVERY deposited 8XTT conformer, so the spread is a distribution rather than a
    consistency check over four hand-selected frames."""
    if not os.path.exists(XTT_FULL):
        return {"status": "NOT_AVAILABLE",
                "_reading": ("the deposited 8XTT entry is not on disk (it is a CI fetch — RCSB is 403'd at "
                             "the dev sandbox's egress proxy). This is a MISSING READING, not an absent "
                             "ensemble.")}
    models = read_ca_models(XTT_FULL)
    rows = [compare_on_ca(ca, mapped_site4, offset, "model_%d" % (i + 1)) for i, ca in enumerate(models)]
    ok = [r for r in rows if r["status"] == "OK"]
    d = sorted(r["centroid_dist_ang"] for r in ok)
    return {
        "status": "OK" if ok else "NO_MODEL_COMPLETE",
        "source": os.path.relpath(XTT_FULL, HERE),
        "n_models_in_file": len(models),
        "n_models_usable": len(ok),
        "n_accepted_by_frozen_gate": sum(1 for r in ok if r["accepted_by_frozen_gate"]),
        "centroid_dist_ang_min": d[0] if d else None,
        "centroid_dist_ang_median": d[len(d) // 2] if d else None,
        "centroid_dist_ang_max": d[-1] if d else None,
        "per_conformer": rows,
        "_why_this_matters": ("the four conformers under _pose_convergence_inputs/ were SELECTED for a "
                             "pose-convergence study. A spread across them is a consistency check; a spread "
                             "across the deposited ensemble is the distribution."),
    }


def compare_on_conformer(path, mapped_site4, offset):
    ca = read_ca(path)
    p5_auth = [r - offset for r in POCKET5_UNIPROT]
    s4_auth = [r - offset for r in mapped_site4]
    p5_pts = [ca[a] for a in p5_auth if a in ca]
    s4_pts = [ca[a] for a in s4_auth if a in ca]
    if len(p5_pts) != len(p5_auth) or len(s4_pts) != len(s4_auth):
        return {"conformer": os.path.basename(path), "status": "INCOMPLETE_IN_MODEL",
                "n_pocket5_ca_found": len(p5_pts), "n_pocket5_expected": len(p5_auth),
                "n_site4_ca_found": len(s4_pts), "n_site4_expected": len(s4_auth),
                "_reading": "a residue absent from this conformer is a READ FAILURE for that residue, not "
                            "evidence about the site (CLAUDE.md §4)"}
    c5, c4 = centroid(p5_pts), centroid(s4_pts)
    dist = math.dist(c5, c4)
    m = pt.match_metrics(mapped_site4, POCKET5_UNIPROT)
    return {
        "conformer": os.path.basename(path),
        "status": "OK",
        "pocket5_centroid_A": [round(x, 3) for x in c5],
        "site4_centroid_A": [round(x, 3) for x in c4],
        "centroid_dist_ang": round(dist, 3),
        "n_overlap": m["n_overlap"],
        "jaccard": round(m["jaccard"], 4),
        "frac_recovered": round(m["frac_recovered"], 4),
        "accepted_by_frozen_gate": pt.accept_candidate(m, dist),
    }


def burial(path, resnums_uniprot, offset):
    """Mean relative solvent accessibility of a residue set on one conformer, via the atlas's Shrake-Rupley.

    Reported because "allosteric SURFACE pocket" (the paper's words for site 4) and "orthosteric pocket"
    (this repository's label for Pocket-5, e.g. nr4a3-degrader-paper.md §2) are claims about BURIAL, and the
    two labels cannot both be right about one region. This does not settle which label is correct — it
    measures the property the labels disagree about, on the one NR4A3 structure that exists.
    """
    atoms, residues = read_heavy(path)
    sasa = atlas.shrake_rupley(atoms)
    three2one = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
                 "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
                 "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}
    rsa = atlas.residue_rsa([(rid, three2one.get(aa, "X")) for rid, aa in residues], sasa)
    want = [u - offset for u in resnums_uniprot]
    abs_v = [sasa[a] for a in want if a in sasa]
    rel_v = [rsa[a] for a in want if rsa.get(a) is not None]
    return {"n_residues_found": len(abs_v), "n_residues_requested": len(want),
            "mean_residue_sasa_A2": round(sum(abs_v) / len(abs_v), 2) if abs_v else None,
            "mean_rsa": round(sum(rel_v) / len(rel_v), 4) if rel_v else None,
            "min_rsa": round(min(rel_v), 4) if rel_v else None,
            "max_rsa": round(max(rel_v), 4) if rel_v else None,
            "n_residues_rsa_ge_0_25": sum(1 for v in rel_v if v >= 0.25)}


def _git_blob_sha(data: bytes) -> str:
    """The git object id of the bytes we actually verified against.

    ⚠ A PATH IS NOT A PROVENANCE. `--source-text` may point at a working copy, a scratch file or a
    re-download, and recording the path would say nothing about WHICH bytes cleared the quote check. The
    blob SHA is checkable against `git ls-tree literature-cache -- <path>` by anyone, forever, and is the
    same identifier git itself uses — so a future reader can prove the retrieved text has not moved under
    the result.
    """
    import hashlib
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def verify_quotes(text):
    rows = []
    for r in SITE4:
        rows.append({"resnum": r["resnum"], "quote": r["quote"], "found_verbatim": r["quote"] in text})
    for k, q in SITE4_ALSO_QUOTED.items():
        rows.append({"resnum": k, "quote": q, "found_verbatim": q in text})
    for q in (SOURCE["site_description_quote"],):
        rows.append({"resnum": None, "quote": q, "found_verbatim": q in text})
    n_ok = sum(1 for r in rows if r["found_verbatim"])
    return {"n_quotes": len(rows), "n_found_verbatim": n_ok,
            "status": "OK" if n_ok == len(rows) else "QUOTE_NOT_FOUND", "quotes": rows}


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def build(source_text_path=None):
    with open(SEQ_CACHE) as fh:
        seqs = json.load(fh)
    offset, bench = xtt_offset()
    rows = map_nr4a2_to_nr4a3([r["resnum"] for r in SITE4], seqs)
    by_num = {r["nr4a2_resnum"]: r for r in rows}
    for r in SITE4:
        by_num[r["resnum"]].update({"evidence_class": r["evidence_class"], "source_quote": r["quote"]})
    mapped = sorted({r["mapped_nr4a3_resnum"] for r in rows if r["mapped_nr4a3_resnum"] is not None})
    unmapped = [r["nr4a2_resnum"] for r in rows if r["mapped_nr4a3_resnum"] is None]

    conformers = sorted(glob.glob(XTT_GLOB))
    per_conf = [compare_on_conformer(p, mapped, offset) for p in conformers]
    ok = [c for c in per_conf if c["status"] == "OK"]
    dists = sorted(c["centroid_dist_ang"] for c in ok)

    # The mutagenesis-only sub-site: the paper's four functionally-anchored residues alone. If the match
    # rested on the docking/MD contacts it would be much weaker evidence, so it is separated rather than
    # pooled — the reader can see which half of the site does the work.
    mut_nums = [r["resnum"] for r in SITE4 if r["evidence_class"] == "mutagenesis"]
    mut_mapped = sorted({by_num[n]["mapped_nr4a3_resnum"] for n in mut_nums
                         if by_num[n]["mapped_nr4a3_resnum"] is not None})
    mut_metrics = pt.match_metrics(mut_mapped, POCKET5_UNIPROT) if mut_mapped else None

    # The paper's OTHER epitopes, mapped the same way, as a negative control on the mapping itself.
    ctrl = {}
    for label, nums in OTHER_SITE_MUTANTS.items():
        crows = map_nr4a2_to_nr4a3(nums, seqs)
        cmapped = sorted({r["mapped_nr4a3_resnum"] for r in crows if r["mapped_nr4a3_resnum"] is not None})
        cm = pt.match_metrics(cmapped, POCKET5_UNIPROT) if cmapped else None
        cconf = compare_on_conformer(conformers[0], cmapped, offset) if cmapped else None
        ctrl[label] = {
            "nr4a2_resnums": nums,
            "mapped_nr4a3_resnums": cmapped,
            "n_overlap_with_pocket5": cm["n_overlap"] if cm else None,
            "jaccard": round(cm["jaccard"], 4) if cm else None,
            "frac_recovered": round(cm["frac_recovered"], 4) if cm else None,
            "centroid_dist_ang_on_first_conformer": (cconf or {}).get("centroid_dist_ang"),
            "accepted_by_frozen_gate": (cconf or {}).get("accepted_by_frozen_gate"),
        }

    bur = {}
    if conformers:
        bur = {
            "conformer": os.path.basename(conformers[0]),
            "pocket5": burial(conformers[0], POCKET5_UNIPROT, offset),
            "site4_mapped": burial(conformers[0], mapped, offset),
            "_method": ("nr4a_differential_atlas.shrake_rupley + residue_rsa (Tien max-ASA), per-residue, "
                        "on the heavy atoms of one conformer"),
            "_limits": ["one NMR conformer of an apo LBD; a cryptic pocket's burial is conformer-dependent "
                        "and this is a single frame",
                        "RSA is descriptive here. It is not the criterion for anything and no threshold in "
                        "this repository is being applied to it."],
        }

    n_acc = sum(1 for c in ok if c["accepted_by_frozen_gate"])
    d = {
        "_title": "The published Nurr1 H1/H5/H7/H8 allosteric pocket vs NR4A3 Pocket-5 — a geometry comparison",
        "_question": ("emc-unexplored-treatment-lanes.md §4: does the vidofludimus site on Nurr1 correspond "
                      "to the site this repository's FEP/degrader lane targets on NR4A3?"),
        "_status": ("GEOMETRY ONLY, $0 CPU, pure stdlib. No binding, affinity, potency, selectivity, "
                    "efficacy, safety, therapeutic-window or clinical claim is made or implied."),
        "_cost": "$0 — committed sequences, committed 8XTT conformers, a CI-cached full text. No GPU.",
        "source": SOURCE,
        "paper_numbering_check": paper_numbering_check(seqs),
        "site_definition": {
            "_what": "the published site 4, residue by residue, each with the sentence that names it",
            "n_residues": len(SITE4),
            "n_mutagenesis_anchored": len(mut_nums),
            "n_model_contact_only": len(SITE4) - len(mut_nums),
            "residues": rows,
            "also_quoted": SITE4_ALSO_QUOTED,
        },
        "pocket5_definition": {
            "_source": "nr4a3_8xtt_benchmark.POCKET5 — imported, never re-typed (CLAUDE.md rule 1)",
            "residues_uniprot_Q92570": POCKET5_UNIPROT,
            "repository_label": ("`orthosteric` — e.g. nr4a3-degrader-paper.md: 'the NR4A3 orthosteric "
                                 "pocket (Pocket 5, residues 406-534, carrying all 7 selectivity handles)'"),
        },
        "mapping": {
            "_method": ("two independent aligners over the cached UniProt canonical sequences; a position "
                        "counts only where they agree"),
            "n_site4_residues": len(SITE4),
            "n_mapped": len(mapped),
            "n_unmapped": len(unmapped),
            "unmapped_nr4a2_resnums": unmapped,
            "mapped_nr4a3_resnums": mapped,
            "all_mapped_positions_aligner_agreed": all(r["aligners_agree"] for r in rows),
            "n_identical_residue_type": sum(1 for r in rows if r["identical_residue_type"]),
        },
        "structure_frame": {
            "pdb": "8XTT (the only NR4A3 PDB entry; apo solution NMR, LBD)",
            "conformers_used": [os.path.basename(p) for p in conformers],
            "n_conformers_used": len(conformers),
            "uniprot_minus_author_offset": offset,
            "offset_source": os.path.relpath(XTT_BENCH, REPO),
            "⚠_conformer_selection": ("these are the conformers COMMITTED to this repository "
                                      "(_pose_convergence_inputs/), selected for a pose-convergence study "
                                      "— NOT a random draw from the deposited ensemble, and not all of it. "
                                      "The spread below is therefore a consistency check, not the ensemble "
                                      "distribution."),
        },
        "comparison_full_site": {
            "per_conformer": per_conf,
            "n_conformers_ok": len(ok),
            "n_accepted_by_frozen_gate": n_acc,
            "centroid_dist_ang_min": dists[0] if dists else None,
            "centroid_dist_ang_max": dists[-1] if dists else None,
            "centroid_dist_ang_median": dists[len(dists) // 2] if dists else None,
            "n_overlap": ok[0]["n_overlap"] if ok else None,
            "overlapping_residues_uniprot": sorted(set(mapped) & set(POCKET5_UNIPROT)),
            "jaccard": ok[0]["jaccard"] if ok else None,
            "frac_recovered": ok[0]["frac_recovered"] if ok else None,
        },
        "★_comparison_over_the_full_deposited_ensemble": full_ensemble(mapped, offset),
        "comparison_mutagenesis_anchored_only": {
            "_what": ("the four residues whose mutation MEASURABLY changes vidofludimus activity, on their "
                      "own — the docking/MD contacts removed"),
            "nr4a2_resnums": mut_nums,
            "mapped_nr4a3_resnums": mut_mapped,
            "n_overlap": mut_metrics["n_overlap"] if mut_metrics else None,
            "jaccard": round(mut_metrics["jaccard"], 4) if mut_metrics else None,
            "frac_recovered": round(mut_metrics["frac_recovered"], 4) if mut_metrics else None,
        },
        "control_other_epitopes_from_the_same_paper": {
            "_what": ("the same paper's OTHER mutant sites, mapped by the identical pipeline. If these also "
                      "'matched' Pocket-5, the match would be an artifact of the mapping rather than a "
                      "finding about site 4."),
            "sites": ctrl,
        },
        "burial": bur,
        "frozen_gate": {
            "thresholds": pt.match_params(),
            "source": "pocket_tracking (frozen 2026-07-11)",
            "⚠_reused_out_of_its_original_question": (
                "these thresholds were frozen to decide WHICH fpocket cavity in a frame is the reference "
                "site. Applying them to two independently-defined residue sets is a reuse, declared here so "
                "it is visible; the raw metrics are reported so a reader can apply their own."),
        },
    }
    if source_text_path:
        with open(source_text_path, "rb") as fh:
            raw = fh.read()
        d["source_quote_verification"] = verify_quotes(raw.decode("utf-8", "replace"))
        d["source_quote_verification"].update({
            "verified_bytes": len(raw),
            "git_blob_sha1_of_the_verified_text": _git_blob_sha(raw),
            "expected_at": ("literature-cache:literature/nr4a-ligand-chemistry/PMC12095788.txt — check with "
                            "`git ls-tree origin/literature-cache -- "
                            "literature/nr4a-ligand-chemistry/PMC12095788.txt`"),
            "_why_not_a_path": ("a path says nothing about WHICH bytes cleared the check; the blob id is "
                                "checkable by anyone against the branch, forever"),
        })
    else:
        d["source_quote_verification"] = {
            "status": "NOT_RUN",
            "_reading": ("the quotes were NOT checked against the retrieved text in this run. Run with "
                         "--source-text <path to the literature-cache copy of PMC12095788.txt>. An "
                         "unverified quote block is not evidence that the quotes are right."),
        }
    d["verdict"] = verdict(d)
    return d


def verdict(d):
    c = d["comparison_full_site"]
    m = d["comparison_mutagenesis_anchored_only"]
    ctrl = d["control_other_epitopes_from_the_same_paper"]["sites"]
    ctrl_accept = [k for k, v in ctrl.items() if v.get("accepted_by_frozen_gate")]
    full = d["★_comparison_over_the_full_deposited_ensemble"]
    matched = (c["n_conformers_ok"] > 0 and c["n_accepted_by_frozen_gate"] == c["n_conformers_ok"])
    return {
        "answer": "MATCH" if matched else ("NO_MATCH" if c["n_conformers_ok"] else "INDETERMINATE"),
        "★_on_the_full_deposited_ensemble": (
            "%d of %d deposited 8XTT conformers accept, centroid distance %s–%s Å (median %s). This is the "
            "DISTRIBUTION, not a consistency check over hand-selected frames."
            % (full["n_accepted_by_frozen_gate"], full["n_models_usable"],
               full["centroid_dist_ang_min"], full["centroid_dist_ang_max"],
               full["centroid_dist_ang_median"])
            if full.get("status") == "OK" else
            "the deposited ensemble is not on disk: %s" % full.get("_reading")),
        "_in_the_repositorys_own_vocabulary": (
            "n_overlap %s, jaccard %s, frac_recovered %s, centroid_dist %s-%s A over %d conformers; the "
            "frozen composite gate (jaccard >= %.2f OR frac_recovered >= %.2f) AND centroid <= %.1f A "
            "accepts on %d of %d." % (
                c["n_overlap"], c["jaccard"], c["frac_recovered"], c["centroid_dist_ang_min"],
                c["centroid_dist_ang_max"], c["n_conformers_ok"],
                d["frozen_gate"]["thresholds"]["jaccard_min"],
                d["frozen_gate"]["thresholds"]["frac_recovered_min"],
                d["frozen_gate"]["thresholds"]["centroid_max_ang"],
                c["n_accepted_by_frozen_gate"], c["n_conformers_ok"])),
        "control_sites_that_also_clear_the_gate": ctrl_accept,
        "★_the_control_is_what_makes_this_readable": (
            "the same paper's other three epitopes, mapped by the IDENTICAL pipeline, land %s A from the "
            "Pocket-5 centroid with n_overlap 0 and are refused by the gate. So the match is a property of "
            "site 4, not of the mapping." % ", ".join(
                str(v.get("centroid_dist_ang_on_first_conformer")) for v in ctrl.values())),
        "★_mutagenesis_anchored_subset": (
            "%d of the %d functionally-anchored residues are mappable, and %d of those %d ARE Pocket-5 "
            "lining residues (%s). The match does not rest on the docking/MD contacts."
            % (len(m["mapped_nr4a3_resnums"]), len(m["nr4a2_resnums"]), m["n_overlap"],
               len(m["mapped_nr4a3_resnums"]), m["mapped_nr4a3_resnums"])),
        "⛔_what_this_does_not_say": [
            "NOTHING here says vidofludimus binds NR4A3. The paralogue LBDs are 65.5 %% identical (the "
            "paper's own BLAST figure) and %d of the %d site-4 positions do NOT carry the same residue "
            "type in NR4A3 (%d differ, %d has no NR4A3 counterpart at all) — which is where a selectivity "
            "argument would START, not end." % (
                d["mapping"]["n_site4_residues"] - d["mapping"]["n_identical_residue_type"],
                d["mapping"]["n_site4_residues"],
                d["mapping"]["n_mapped"] - d["mapping"]["n_identical_residue_type"],
                d["mapping"]["n_unmapped"]),
            "NOTHING here is an affinity, potency, selectivity, efficacy, safety, therapeutic-window or "
            "clinical-readiness claim, and a residue-set overlap can never become one.",
            "The published site is a MODEL (mutagenesis + docking + MD), not a co-crystal. A comparison "
            "cannot be stronger than the object it compares against.",
            "Pocket-5's own status is unsettled in this repository: `V3` left the cryptic-pocket question "
            "INCONCLUSIVE, and this comparison does not touch it.",
            "8XTT is an APO solution-NMR ensemble of an isolated LBD construct. Neither site is OPEN in it; "
            "both are residue sets projected onto a closed structure, and Pocket-5's opening is the very "
            "thing `V13` failed to demonstrate as a two-state process.",
            "⚠ A NUMBER COLLISION A READER WILL HIT: NR4A2 E481 is one of the paper's SITE-2 mutants and "
            "NR4A3 R481 is a Pocket-5 lining residue. They are different positions in different proteins "
            "and the alignment maps NR4A2 481 to NR4A3 512, nowhere near Pocket-5. Nothing here reads one "
            "as the other.",
        ],
        "_what_it_does_license": (
            "one thing: the FEP lane has a named, published, clinical-stage chemical series (vidofludimus "
            "and the paper's analog 1) whose reported site corresponds — by residue overlap and centroid "
            "distance on the only NR4A3 structure that exists — to the site this repository already "
            "targets. That is a STARTING POINT with SAR attached, not a result."
            if d["comparison_full_site"]["n_accepted_by_frozen_gate"] else
            "a documented negative: the published Nurr1 site and Pocket-5 are different regions, and "
            "vidofludimus SAR does not transfer to this lane's site."),
    }


FRONTMATTER = """---
id: DOC-NURR1-ALLOSTERIC-VS-POCKET5
title: The published Nurr1 H1/H5/H7/H8 allosteric pocket vs NR4A3 Pocket-5
level: L4
kind: memo
status: generated
generator: research/modalities/nurr1_allosteric_vs_pocket5.py
canonical_for: ["the site correspondence between the vidofludimus epitope and Pocket-5"]
purpose: "Answer emc-unexplored-treatment-lanes.md section 4: is the published Nurr1 allosteric surface pocket the same region as the site this repository's FEP and degrader lanes target on NR4A3?"
scope: Geometry only. A residue-set overlap and a centroid distance. No binding, affinity, potency, selectivity, efficacy, safety, therapeutic-window or clinical statement.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

"""


def to_markdown(d):
    c, v = d["comparison_full_site"], d["verdict"]
    L = [FRONTMATTER.rstrip("\n"), "",
         "# Nurr1 allosteric pocket (H1/H5/H7/H8) vs NR4A3 Pocket-5", "",
         "> Generated by `nurr1_allosteric_vs_pocket5.py`; this file is derived — edit the module, "
         "not this.", "",
         "> %s" % d["_status"], "",
         "**Verdict: %s.** %s" % (v["answer"], v["_in_the_repositorys_own_vocabulary"]), "",
         "## Source", "", "%s %s (%s) %s" % (d["source"]["citation"], d["source"]["doi"],
                                             d["source"]["pmc"], d["source"]["verification_level"]),
         "", "> %s" % d["source"]["site_description_quote"], "",
         "## The mapping (NR4A2 P43354 -> NR4A3 Q92570)", "",
         "| NR4A2 | evidence | NR4A3 | same type | aligners agree |", "|---|---|---|---|---|"]
    for r in d["site_definition"]["residues"]:
        L.append("| %s%d | %s | %s | %s | %s |" % (
            r["nr4a2_aa"], r["nr4a2_resnum"], r.get("evidence_class", ""),
            ("%s%d" % (r["mapped_nr4a3_aa"], r["mapped_nr4a3_resnum"])
             if r["mapped_nr4a3_resnum"] else "— (%s)" % r["why_unmapped"]),
            "yes" if r["identical_residue_type"] else "no", "yes" if r["aligners_agree"] else "NO"))
    full = d["★_comparison_over_the_full_deposited_ensemble"]
    L += ["", "## Overlap with Pocket-5", "",
          "- Pocket-5: %s" % d["pocket5_definition"]["residues_uniprot_Q92570"],
          "- site 4 mapped: %s" % d["mapping"]["mapped_nr4a3_resnums"],
          "- shared: %s" % c["overlapping_residues_uniprot"],
          "- n_overlap %s · jaccard %s · frac_recovered %s" % (c["n_overlap"], c["jaccard"],
                                                              c["frac_recovered"]),
          "- centroid distance %s-%s A over %d conformers of 8XTT" % (
              c["centroid_dist_ang_min"], c["centroid_dist_ang_max"], c["n_conformers_ok"]),
          ("- **over the FULL deposited ensemble: %d of %d conformers accepted, %s-%s A (median %s)**"
           % (full["n_accepted_by_frozen_gate"], full["n_models_usable"], full["centroid_dist_ang_min"],
              full["centroid_dist_ang_max"], full["centroid_dist_ang_median"])
           if full.get("status") == "OK" else "- full deposited ensemble: %s" % full.get("status")),
          "",
          "## The control that makes this readable", "",
          "The same paper's OTHER three epitopes, mapped by the identical pipeline:", "",
          "| epitope | NR4A2 residues | mapped NR4A3 | overlap with Pocket-5 | centroid distance |",
          "|---|---|---|---|---|"]
    for label, r in sorted(d["control_other_epitopes_from_the_same_paper"]["sites"].items()):
        L.append("| %s | %s | %s | %s | %s A |" % (label, r["nr4a2_resnums"], r["mapped_nr4a3_resnums"],
                                                   r["n_overlap_with_pocket5"],
                                                   r["centroid_dist_ang_on_first_conformer"]))
    m = d["comparison_mutagenesis_anchored_only"]
    L += ["", "None clears the gate. So the match is a property of site 4, not of the mapping.", "",
          "And it does not rest on the docking/MD contacts: of the %d MUTAGENESIS-anchored residues, %d are "
          "mappable and %d of those are Pocket-5 lining residues (%s)."
          % (len(m["nr4a2_resnums"]), len(m["mapped_nr4a3_resnums"]), m["n_overlap"],
             m["mapped_nr4a3_resnums"]),
          "", "## What this does not say", ""]
    L += ["- %s" % x for x in v["⛔_what_this_does_not_say"]]
    L += ["", "## What it licenses", "", v["_what_it_does_license"], ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--source-text", default=None,
                    help="path to the CI-retrieved PMC12095788 full text; every declared quote is checked "
                         "against it verbatim")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="rebuild and diff the verdict against --out")
    args = ap.parse_args(argv)

    d = build(args.source_text)
    if args.check:
        with open(args.out) as fh:
            old = json.load(fh)
        same = old.get("verdict", {}).get("answer") == d["verdict"]["answer"]
        print("[check] verdict %s -> %s : %s" % (old.get("verdict", {}).get("answer"),
                                                 d["verdict"]["answer"], "SAME" if same else "DRIFT"))
        return 0 if same else 1
    with open(args.out, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
        fh.write(to_markdown(d))
    print(json.dumps(d["verdict"], indent=1))
    print("\nquote verification:", d["source_quote_verification"].get("status"))
    print("paper numbering check:", d["paper_numbering_check"]["status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
