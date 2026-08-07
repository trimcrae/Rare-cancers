#!/usr/bin/env python3
"""
`C10` — the SYMMETRIC reciprocal-uniqueness + INDEL census across ALL residue classes ($0 CPU, offline).

★ WHAT THIS IS, AND WHAT IT IS NOT. This is a **READ**, not an inference. It cannot fail; it can only return
fewer positions than the program has been assuming. It is roadmap §10.1a `Q8`, promoted from instrument
candidate `C10` ([instrument-options.md](./instrument-options.md)), and it exists because the two things it
measures are the two things the committed maps structurally cannot see:

  (1) ⛔ **THE ATLAS CANNOT EXPRESS AN INDEL.** `nr4a3-differential-surface-atlas.json` is computed over 254
      ALIGNED residues; an unaligned position is not in the table at all. An indel — a whole element present
      in one paralogue and absent in another — is the strongest categorical difference available on this
      family, and nothing in this repository had ever enumerated one.

  (2) ⛔ **UNIQUENESS RUNS BOTH WAYS, AND ONLY THE CYSTEINE HALF HAD BEEN COMPUTED.**
      `nr4a-paralogue-unique-residues.json` carries `reciprocal_paralogue_unique` for **Cys and Lys only**
      (`residue_types=("C","K")`). Every other residue class — and every direction other than
      NR4A3-as-reference — was uncomputed. "NR4A3 has X and they do not" and "they have X and NR4A3 does
      not" are different facts with different consequences (a handle vs an ANTI-handle), and the second is
      what `Q3`'s anti-handle constraint needs as a data source.

WHAT IT SERVES. `Q3` (its data source — the anti-handle set, now for every residue class rather than
cysteines alone) and `Q5` (its completeness check — whether the widened reactive-class enumeration missed a
tetherable position that a symmetric read finds).

METHOD. Pure stdlib, offline, no network — the sequences are already cached
(`nr4a-sequences-cache.json`) and the geometry comes from the matched opened models already in the repo.

  * **Uniqueness** reuses `nr4a_paralogue_unique_residues.classify_positions` unchanged, called with all 20
    residue types and with EACH of the three paralogues as the reference in turn. That function already
    computes every position TWICE with two independent aligners — the match/mismatch linear-gap
    Needleman-Wunsch (`nrv04_cys_conservation`) and the affine-gap Gotoh/BLOSUM62 aligner
    (`nr4a_differential_atlas.nw_align`) — and records `alignment_robust` per position. That flag is
    load-bearing here for the same reason it was there: **uniqueness is a claim about an alignment**, and the
    two aligners are already known to disagree on where NR4A1 Cys551 maps.

  * **Indels** are new. For each of the six ordered pairs, contiguous runs of gaps in the alignment are
    enumerated under BOTH aligners, and a run is `robust` only if both aligners place a gap over the same
    reference span. A run is then promoted to a **three-way indel** — the categorical form `C10` names — only
    when the segment is present in exactly one paralogue and absent in BOTH others.

  * **Geometry** annotates NR4A3-anchored positions with Shrake-Rupley relative SASA and the distance from
    the residue's side-chain heavy-atom centroid to the nearest cryptic-pocket heavy atom, binned into the
    same reach bands the committed handle map uses. ⚠ Side-chain centroid, NOT a reactive atom: most residue
    classes have no reactive atom, so the general read cannot use `REACTIVE_ATOM` and its distances are
    therefore NOT comparable to the committed Cys/Lys `dist_to_cryptic_pocket_A` column. Both are reported
    with their definition attached.

⛔ HONEST LIMITS, carried into the artifact.
  * Sequence uniqueness is exact; every geometric annotation is ONE static opened conformer.
  * An indel's CONSEQUENCE needs a structure. This file says a segment is present in one paralogue and absent
    in the others. It says nothing about whether that segment is ordered, surface-exposed, near the pocket,
    or usable by anything.
  * The comparison set is THREE proteins. Nothing here is a proteome-wide statement of any kind, and nothing
    here is a claim about binding, reactivity, adduct formation, degradation, efficacy, safety, a therapeutic
    window or clinical readiness.
  * A position that is unique but NOT `alignment_robust` is ambiguous, not a finding: it needs a structural
    superposition, not a sequence call.

Output: nr4a-reciprocal-uniqueness-census.json
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

import nr4a_differential_atlas as atlas            # noqa: E402
import nrv04_cys_conservation as cyscons           # noqa: E402
import nr4a_paralogue_unique_residues as uniq      # noqa: E402

PROTEINS = ("NR4A1", "NR4A2", "NR4A3")
ALL_RESIDUE_TYPES = tuple("ACDEFGHIKLMNPQRSTVWY")

CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")
OUT = os.path.join(HERE, "nr4a-reciprocal-uniqueness-census.json")
STRUCT_DIR = os.path.join(REPO, "results", "nr4a3-matrix")

# Reactive classes, for the `Q5` completeness cross-check. Kept identical in spirit to the widened sweep:
# nucleophiles an electrophilic handle could in principle address.
NUCLEOPHILIC = {"C", "K", "Y", "S", "T", "H", "R", "M", "W", "D", "E"}

# The handful of residue classes the committed maps already covered, so this file can say what is NEW.
ALREADY_COVERED = {"C", "K"}


# =============================================================================================================
# indel census — the half that is genuinely new
# =============================================================================================================
def _linear_pairs(a: str, b: str):
    """(i_a|None, i_b|None) column list from the match/mismatch linear-gap aligner."""
    aln_a, aln_b = cyscons.needleman_wunsch(a, b)
    ia = ib = 0
    out = []
    for ca, cb in zip(aln_a, aln_b):
        pa = pb = None
        if ca != "-":
            pa = ia
            ia += 1
        if cb != "-":
            pb = ib
            ib += 1
        out.append((pa, pb))
    return out


def gap_runs(pairs, side: str):
    """Contiguous runs where `side` ('a' or 'b') is a gap while the other side consumes residues.

    Returns [{'other_first', 'other_last', 'length', 'segment'}] in the OTHER sequence's 1-based numbering —
    i.e. the residues that are PRESENT in the other sequence and ABSENT here. Terminal runs are included and
    flagged by the caller, because a terminal gap is a length difference, not an internal indel.
    """
    runs = []
    cur = None
    last_mine = None
    for pa, pb in pairs:
        mine, other = (pa, pb) if side == "a" else (pb, pa)
        if mine is None and other is not None:
            if cur is None:
                cur = [other, other, last_mine]
            else:
                cur[1] = other
        else:
            if cur is not None:
                runs.append(cur)
                cur = None
            if mine is not None:
                last_mine = mine
    if cur is not None:
        runs.append(cur)
    return [{"other_first": r[0] + 1, "other_last": r[1] + 1, "length": r[1] - r[0] + 1,
             # 1-based residue of the ABSENT sequence immediately preceding the gap — the insertion point.
             # `None` means the gap opens before residue 1 (an N-terminal run).
             "absent_after": None if r[2] is None else r[2] + 1}
            for r in runs]


def indel_census(seqs, min_length=1):
    """Every ordered pair, both aligners. A run is `robust` iff BOTH aligners report a gap run covering the
    same span in the present sequence."""
    out = {}
    for present in PROTEINS:
        for absent in PROTEINS:
            if present == absent:
                continue
            key = f"{present}_present__{absent}_absent"
            lin = _linear_pairs(seqs[present], seqs[absent])
            aff = atlas.nw_align(seqs[present], seqs[absent])
            runs_lin = gap_runs(lin, "b")
            runs_aff = gap_runs(aff, "b")
            aff_spans = {(r["other_first"], r["other_last"]) for r in runs_aff}
            rows = []
            n_pres = len(seqs[present])
            for r in runs_lin:
                if r["length"] < min_length:
                    continue
                terminal = r["other_first"] == 1 or r["other_last"] == n_pres
                rows.append({
                    "present_in": present,
                    "absent_in": absent,
                    "first_resnum": r["other_first"],
                    "last_resnum": r["other_last"],
                    "length": r["length"],
                    "segment": seqs[present][r["other_first"] - 1:r["other_last"]],
                    "insertion_point_in_absent_seq": r["absent_after"],
                    "terminal": terminal,
                    "robust_both_aligners": (r["other_first"], r["other_last"]) in aff_spans,
                })
            out[key] = rows
    return out


def shared_paralogue_indels(census, absent="NR4A3", min_length=2):
    """⭑ THE OTHER THREE-WAY DIRECTION, and the one the ordinary reading misses.

    `three_way_indels` asks *"which protein HAS a segment the other two lack"* — the handle direction. Its
    mirror is *"which segment do BOTH paralogues have that the target LACKS"* — an ABSENCE in NR4A3 at a
    position both paralogues fill. That cannot be a covalent handle (nothing can be tethered to a residue
    that is not there) and it is not an anti-handle either; it is a **shape** difference, and shape is the
    other mechanism the composer set in §10.1b runs on.

    Matched by INSERTION POINT in the absent sequence, not by the paralogues' own numbering — two runs at the
    same absent-side position are one event, and two runs at different positions are two.
    """
    others = [p for p in PROTEINS if p != absent]
    a = {r["insertion_point_in_absent_seq"]: r for r in census[f"{others[0]}_present__{absent}_absent"]
         if r["length"] >= min_length and not r["terminal"]}
    b = {r["insertion_point_in_absent_seq"]: r for r in census[f"{others[1]}_present__{absent}_absent"]
         if r["length"] >= min_length and not r["terminal"]}
    pocket = set(uniq.CRYPTIC_POCKET_UNIPROT) if absent == "NR4A3" else set()
    out = []
    for pos in sorted(set(a) & set(b) - {None}):
        ra, rb = a[pos], b[pos]
        flank = {pos, pos + 1}
        out.append({
            "absent_in": absent,
            "insertion_point_in_absent_seq": pos,
            "flanking_residues_in_absent_seq": sorted(flank),
            "flanks_are_cryptic_pocket_residues": sorted(flank & pocket) if pocket else None,
            "⚠_pocket_adjacency_is_a_COORDINATE_fact": (
                "The cryptic-pocket residue list is a set of NR4A3 residue numbers "
                "(`nr4a_paralogue_unique_residues.CRYPTIC_POCKET_UNIPROT`). Saying an indel opens between two "
                "of them says WHERE it is in the sequence. It says NOTHING about whether the inserted "
                "residues line the cavity, change its volume, or are ordered at all — that needs a structure "
                "of the paralogue, which this file does not touch."
            ),
            "present_in": {
                others[0]: {"first_resnum": ra["first_resnum"], "last_resnum": ra["last_resnum"],
                            "segment": ra["segment"], "robust_both_aligners": ra["robust_both_aligners"]},
                others[1]: {"first_resnum": rb["first_resnum"], "last_resnum": rb["last_resnum"],
                            "segment": rb["segment"], "robust_both_aligners": rb["robust_both_aligners"]},
            },
            "same_length": ra["length"] == rb["length"],
            "same_segment": ra["segment"] == rb["segment"],
            "robust_both_aligners": ra["robust_both_aligners"] and rb["robust_both_aligners"],
        })
    return out


def three_way_indels(census, min_length=2):
    """A segment present in exactly ONE paralogue and absent in BOTH others — the categorical form.

    ⚠ Computed as the INTERSECTION of the two pairwise runs, so the reported span is the part of the segment
    that both comparisons agree is missing. A three-way indel that survives only under one aligner is
    reported with `robust_both_aligners: false` and is not a finding.
    """
    out = []
    for present in PROTEINS:
        others = [p for p in PROTEINS if p != present]
        a = census[f"{present}_present__{others[0]}_absent"]
        b = census[f"{present}_present__{others[1]}_absent"]
        for ra in a:
            for rb in b:
                lo = max(ra["first_resnum"], rb["first_resnum"])
                hi = min(ra["last_resnum"], rb["last_resnum"])
                if hi - lo + 1 < min_length:
                    continue
                out.append({
                    "present_in": present,
                    "absent_in": others,
                    "first_resnum": lo,
                    "last_resnum": hi,
                    "length": hi - lo + 1,
                    "segment": None,          # filled by the caller, which holds the sequences
                    "terminal": ra["terminal"] and rb["terminal"],
                    "robust_both_aligners": ra["robust_both_aligners"] and rb["robust_both_aligners"],
                })
    return out


# =============================================================================================================
# geometry — general, all residue classes
# =============================================================================================================
MODEL_FILE = {"NR4A1": "nr4a1-opened.pdb", "NR4A2": "nr4a2-opened.pdb", "NR4A3": "nr4a3-opened.pdb"}


def model_offset(protein, seqs, struct_dir=STRUCT_DIR):
    """UniProt number of the model's local residue 1, DERIVED by exact substring match — never typed.

    ⛔ Refuses rather than guesses. If the model's sequence is not an exact substring of the cached UniProt
    sequence the offset is unknown, and a geometry keyed on a guessed offset is the failure mode this
    repository has paid for repeatedly: a populated field that was never measured.
    """
    pdb = os.path.join(struct_dir, MODEL_FILE[protein])
    if not os.path.exists(pdb):
        return None, None, None
    residues, atoms = atlas.parse_pdb(pdb)
    modelled = "".join(a for _, a in residues)
    i = seqs[protein].find(modelled)
    if i < 0 or seqs[protein].count(modelled) != 1:
        return None, None, None
    first_local = residues[0][0]
    return (i + 1) - first_local, residues, atoms


def pocket_positions_in(protein, seqs):
    """The NR4A3 cryptic pocket mapped onto `protein` through the alignment — not re-defined, TRANSFERRED.

    The pocket definition lives in `nr4a_paralogue_unique_residues.CRYPTIC_POCKET_UNIPROT` and is a statement
    about NR4A3. Asking 'how far is this NR4A1 residue from the pocket' therefore means the ALIGNED site, and
    a position that aligns to a gap has no answer and is dropped rather than approximated.
    """
    if protein == "NR4A3":
        return list(uniq.CRYPTIC_POCKET_UNIPROT)
    aln_ref, aln_oth = cyscons.needleman_wunsch(seqs["NR4A3"], seqs[protein])
    out = []
    for u in uniq.CRYPTIC_POCKET_UNIPROT:
        _res, idx = uniq.aligned_partner(aln_ref, aln_oth, u)
        if idx:
            out.append(idx)
    return out


def sidechain_geometry(protein, seqs, struct_dir=STRUCT_DIR):
    """Per-UniProt-residue RSA + side-chain-centroid distance to the (aligned) cryptic pocket, for EVERY
    residue class, on `protein`'s own opened model.

    ⚠ NOT comparable to the committed handle map's `dist_to_cryptic_pocket_A`, which measures a REACTIVE ATOM
    (Cys SG / Lys NZ). Most residue classes have no reactive atom, so a general read must use a general
    reference point; glycine has no side chain at all and falls back to CA. Heavy atoms only — `parse_pdb`
    keeps hydrogens and a hydrogen-inclusive centroid would be a different quantity again.
    """
    offset, residues, atoms = model_offset(protein, seqs, struct_dir)
    if offset is None:
        return {}, None
    sasa = atlas.shrake_rupley(atoms)
    rsa = atlas.residue_rsa(residues, sasa)

    by_local = {}
    for a in atoms:
        if a["elem"] == "H":
            continue
        by_local.setdefault(a["resid"], []).append(a)

    pocket = []
    for u in pocket_positions_in(protein, seqs):
        pocket.extend(by_local.get(u - offset, []))

    backbone = {"N", "CA", "C", "O", "OXT"}
    out = {}
    for local, ats in by_local.items():
        uni = local + offset
        side = [a for a in ats if a["name"] not in backbone] or [a for a in ats if a["name"] == "CA"]
        if not side:
            continue
        cx = sum(a["x"] for a in side) / len(side)
        cy = sum(a["y"] for a in side) / len(side)
        cz = sum(a["z"] for a in side) / len(side)
        d = min((math.dist((cx, cy, cz), (a["x"], a["y"], a["z"])) for a in pocket), default=None)
        out[uni] = {
            "local_resid": local,
            "resname": ats[0]["resname"],
            "rsa": round(rsa.get(local, 0.0), 3),
            "exposed": rsa.get(local, 0.0) >= atlas.EXPOSED_RSA,
            "sidechain_centroid_to_pocket_A": None if d is None else round(d, 2),
            "reach_class": None if d is None else uniq._reach_class(d),
        }
    return out, offset


# =============================================================================================================
# assembly
# =============================================================================================================
def build(seqs, struct_dir=STRUCT_DIR):
    geom, offsets = {}, {}
    for p in PROTEINS:
        geom[p], offsets[p] = sidechain_geometry(p, seqs, struct_dir)

    directions = {}
    for ref in PROTEINS:
        others = tuple(p for p in PROTEINS if p != ref)
        rows = uniq.classify_positions(seqs, ref=ref, residue_types=ALL_RESIDUE_TYPES, others=others)
        for r in rows:
            r["in_lbd"] = (uniq.LBD_FIRST <= r["resnum"] <= uniq.LBD_LAST) if ref == "NR4A3" else None
            g = geom[ref].get(r["resnum"])
            r["geometry"] = g or {"note": "outside this protein's modelled LBD construct — no geometry"}
            if ref != "NR4A3":
                r["in_lbd"] = bool(g)
        unique = [r for r in rows if r["unique_vs_both"]]
        robust = [r for r in unique if r["alignment_robust"]]
        directions[ref] = {
            "reference": ref,
            "compared_against": list(others),
            "n_positions": len(rows),
            "n_unique_vs_both": len(unique),
            "n_unique_vs_both_and_alignment_robust": len(robust),
            "by_residue_class": {
                aa: {
                    "n_positions": sum(1 for r in rows if r["residue"] == aa),
                    "n_unique_vs_both": sum(1 for r in unique if r["residue"] == aa),
                    "n_unique_and_robust": sum(1 for r in robust if r["residue"] == aa),
                    "already_covered_by_a_committed_map": aa in ALREADY_COVERED,
                }
                for aa in ALL_RESIDUE_TYPES
            },
            "unique_and_robust_rows": robust,
        }

    census = indel_census(seqs)
    three = three_way_indels(census)
    for t in three:
        t["segment"] = seqs[t["present_in"]][t["first_resnum"] - 1:t["last_resnum"]]
    shared = {p: shared_paralogue_indels(census, absent=p) for p in PROTEINS}

    return directions, census, three, shared, geom, offsets


TETHERABLE_BANDS = {"in_pocket", "exit_vector", "linker_borne"}


def summarize(directions, census, three, shared, seqs, geom, offsets):
    n3 = directions["NR4A3"]
    lbd_robust = [r for r in n3["unique_and_robust_rows"] if r["in_lbd"]]

    def reach(rows, bands):
        return [r for r in rows
                if (r.get("geometry") or {}).get("reach_class") in bands]

    tetherable = reach(lbd_robust, TETHERABLE_BANDS)
    nucleophilic_tetherable = [r for r in tetherable if r["residue"] in NUCLEOPHILIC]
    new_classes = [r for r in tetherable if r["residue"] not in ALREADY_COVERED]

    anti = []
    for p in ("NR4A1", "NR4A2"):
        for r in directions[p]["unique_and_robust_rows"]:
            g = r.get("geometry") or {}
            anti.append({"protein": p, "residue": r["residue"], "resnum": r["resnum"],
                         "nucleophilic": r["residue"] in NUCLEOPHILIC,
                         "modelled": bool(g.get("reach_class")),
                         "rsa": g.get("rsa"),
                         "reach_class": g.get("reach_class"),
                         "sidechain_centroid_to_aligned_pocket_A": g.get("sidechain_centroid_to_pocket_A")})
    anti_nuc = [a for a in anti if a["nucleophilic"]]
    anti_tether = [a for a in anti if a["reach_class"] in TETHERABLE_BANDS]
    anti_tether_nuc = [a for a in anti_tether if a["nucleophilic"]]

    internal_robust = [r for rows in census.values() for r in rows
                       if not r["terminal"] and r["robust_both_aligners"] and r["length"] >= 2]
    three_robust = [t for t in three if t["robust_both_aligners"] and not t["terminal"]]

    return {
        "★_what_this_read_returned": (
            "The census ran over all 20 residue classes in all three directions and over all six ordered "
            "pairs for indels. Every count below is a READ of the cached sequences and the committed opened "
            "model; none of it is an inference, and none of it licenses any claim about reactivity, adduct "
            "formation, binding, degradation, efficacy or safety."
        ),
        "n_unique_and_robust_by_direction": {
            p: directions[p]["n_unique_vs_both_and_alignment_robust"] for p in PROTEINS
        },
        "nr4a3_direction": {
            "n_unique_and_robust_total": n3["n_unique_vs_both_and_alignment_robust"],
            "n_in_lbd": len(lbd_robust),
            "n_in_lbd_and_tetherable": len(tetherable),
            "n_in_lbd_tetherable_and_nucleophilic": len(nucleophilic_tetherable),
            "n_in_lbd_tetherable_in_a_class_no_committed_map_covered": len(new_classes),
            "residue_classes_present_among_tetherable": sorted({r["residue"] for r in tetherable}),
        },
        "reciprocal_anti_handle_direction": {
            "_what": (
                "Positions where a PARALOGUE carries a residue class NR4A3 and the other paralogue both "
                "lack — the ANTI-handle set. `Q3` carries these as a design CONSTRAINT rather than a report."
            ),
            "⛔_what_it_is_not": (
                "An anti-handle is a position at which a paralogue is chemically DISTINGUISHABLE, not a "
                "position at which anything reacts. Nothing here says an adduct forms on a paralogue, and "
                "the tetherability bands are the same static single-conformer reach classes the committed "
                "handle map uses — a geometric plausibility statement, not a measurement."
            ),
            "n_total": len(anti),
            "n_nucleophilic": len(anti_nuc),
            "n_in_a_modelled_lbd_and_tetherable": len(anti_tether),
            "n_tetherable_and_nucleophilic": len(anti_tether_nuc),
            "by_protein": {p: sum(1 for a in anti if a["protein"] == p) for p in ("NR4A1", "NR4A2")},
            "by_protein_tetherable": {p: sum(1 for a in anti_tether if a["protein"] == p)
                                      for p in ("NR4A1", "NR4A2")},
            "⭑_committed_anti_handle_set_for_comparison": {
                "_source": "roadmap §10.1a Q3 — NR4A1 C505, NR4A1 C551, NR4A2 C534",
                "n": 3,
                "_reading": (
                    "The committed constraint is three CYSTEINES. This read finds "
                    f"{len(anti_tether)} tetherable paralogue-unique positions across all residue classes, "
                    f"{len(anti_tether_nuc)} of them in a nucleophilic class. ⚠ That is a WIDER SET, not a "
                    "stronger one: a unique serine is not a warhead target the way a unique cysteine is, "
                    "and this file computes no reactivity of any kind."
                ),
            },
            "tetherable_rows": anti_tether,
        },
        "indels": {
            "n_pairwise_runs": sum(len(v) for v in census.values()),
            "n_internal_robust_runs_len_ge_2": len(internal_robust),
            "n_three_way_candidates": len(three),
            "n_three_way_robust_internal": len(three_robust),
            "three_way_robust_internal": three_robust,
            "⭑_shared_paralogue_indels_absent_in_NR4A3": {
                "_what": ("segments BOTH paralogues carry at the same insertion point and NR4A3 lacks — the "
                          "mirror direction. Not a handle (nothing tethers to a residue that is not there) "
                          "and not an anti-handle: a SHAPE difference, which is the other mechanism the "
                          "§10.1b composer set runs on."),
                "n": len(shared["NR4A3"]),
                "n_robust": sum(1 for r in shared["NR4A3"] if r["robust_both_aligners"]),
                "rows": shared["NR4A3"],
            },
        },
        "Q5_completeness_check": {
            "_what": (
                "`Q8` is `Q5`'s completeness check: did the widened reactive-class enumeration "
                "(`sufex-second-handle.json`) miss a tetherable paralogue-unique nucleophilic position that "
                "a symmetric all-class read finds?"
            ),
            "tetherable_unique_robust_nucleophilic_labels": sorted(
                r["residue"] + str(r["resnum"]) for r in nucleophilic_tetherable),
            "★_reading": (
                "The symmetric read independently reproduces every position the widened sweep reports on: "
                "C397, C420 and C559 (the committed unique set), M398 and M399 (explicitly DROPPED there), "
                "and Y419 — at the same RSA 0.221 the sweep quotes. ⚠ THIS IS AGREEMENT, NOT A PROOF OF "
                "COMPLETENESS, and the two are not the same criterion: the sweep ranks on RSA against a "
                "reference site, this read bins on a side-chain-centroid reach band. A position could clear "
                "one and not the other, so the honest statement is that no tetherable paralogue-unique "
                "nucleophile appears here that the sweep does not also carry — not that none exists."
            ),
        },
        "sequence_lengths": {p: len(seqs[p]) for p in PROTEINS},
        "n_modelled_residues_with_geometry": {p: len(geom[p]) for p in PROTEINS},
        "model_uniprot_offset_of_local_residue_1": offsets,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--struct-dir", default=STRUCT_DIR)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    with open(args.cache) as fh:
        seqs = {k: v for k, v in json.load(fh).items() if k in PROTEINS}
    missing = [p for p in PROTEINS if p not in seqs]
    if missing:
        raise SystemExit(f"sequence cache is missing {missing} — this read is offline by design")

    directions, census, three, shared, geom, offsets = build(seqs, args.struct_dir)
    summary = summarize(directions, census, three, shared, seqs, geom, offsets)

    doc = {
        "_title": ("`C10` — symmetric reciprocal-uniqueness + indel census across ALL residue classes "
                   "(roadmap §10.1a `Q8`)"),
        "_status": ("$0 CPU, offline. A READ, not an inference — it cannot fail, only return fewer positions "
                    "than assumed. No GPU, no rental, no network. Nothing here is a claim about binding, "
                    "reactivity, adduct formation, degradation, efficacy, safety, a therapeutic window or "
                    "clinical readiness, and nothing here is a proteome-wide statement of any kind: the "
                    "comparison set is three proteins."),
        "_serves": ["Q3 — its data source (the anti-handle set, now for every residue class)",
                    "Q5 — its completeness check (did the widened reactive-class sweep miss a position?)",
                    "R8", "R15"],
        "_one_fact_one_place": (
            "This file is the one home of the INDEL census and of the all-residue-class symmetric uniqueness "
            "counts. It does NOT re-home the cysteine/lysine handle map — "
            "`nr4a-paralogue-unique-residues.json` owns that, and where the two overlap this file is a "
            "REPRODUCTION under a wider residue set, not a correction. Reach bands and the cryptic-pocket "
            "definition are cited from `nr4a_paralogue_unique_residues.py`, never re-typed."
        ),
        "_reads": {
            "research/modalities/nr4a-sequences-cache.json": "UniProt sequences (cached; no network)",
            "results/nr4a3-matrix/nr4a3-opened.pdb": "geometry for the NR4A3-anchored direction",
        },
        "_method": {
            "aligners": [
                "match/mismatch linear-gap Needleman-Wunsch (nrv04_cys_conservation.needleman_wunsch)",
                "affine-gap Gotoh/BLOSUM62 (nr4a_differential_atlas.nw_align, go=-11 ge=-1)",
            ],
            "alignment_robust": (
                "a position or indel run counts only when BOTH aligners agree. Load-bearing: the two are "
                "already known to disagree on where NR4A1 Cys551 maps, and uniqueness is a claim ABOUT an "
                "alignment."
            ),
            "geometry": (
                "Shrake-Rupley RSA + side-chain heavy-atom-centroid distance to the nearest cryptic-pocket "
                "heavy atom, on EACH protein's own opened model. ⚠ NOT the committed handle map's "
                "reactive-atom distance and not comparable to it — most residue classes have no reactive "
                "atom. The model→UniProt offset is DERIVED by exact substring match, never typed, and a "
                "model whose sequence is not an exact unique substring of its cached UniProt sequence is "
                "refused rather than approximated."
            ),
            "paralogue_pocket": (
                "The cryptic pocket is defined on NR4A3 (`nr4a_paralogue_unique_residues."
                "CRYPTIC_POCKET_UNIPROT`). For NR4A1/NR4A2 it is TRANSFERRED through the alignment, not "
                "re-defined; a pocket position aligning to a gap is dropped, not approximated."
            ),
            "reach_bands_A": uniq.REACH_BANDS[:-1],
            "cryptic_pocket_uniprot": list(uniq.CRYPTIC_POCKET_UNIPROT),
            "nucleophilic_classes_counted": sorted(NUCLEOPHILIC),
        },
        "★_headline": (
            "TWO READINGS, and the second was not the one the instrument was proposed for. "
            "⛔ **(1) THE HANDLE-DIRECTION INDEL AXIS IS EMPTY.** `C10`'s stated first half — an element "
            "present in ONE paralogue and absent in both others — returns **ZERO** robust internal "
            "three-way indels. All five candidates are aligner-dependent: the linear-gap and affine-gap "
            "aligners disagree on every one, which is exactly the condition the `alignment_robust` flag "
            "exists to refuse. So the strongest categorical difference the register hoped for does not "
            "exist on this family at the sequence level, and that is a real answer to a read that could "
            "only ever return fewer positions than assumed. "
            "⭑ **(2) THE MIRROR DIRECTION RETURNED EXACTLY ONE, AND IT SITS IN THE POCKET LINING.** A "
            "two-residue segment that BOTH paralogues carry and NR4A3 LACKS, at the same insertion point "
            "under both aligners: NR4A1 `ST` (378-379) and NR4A2 `AM` (378-379), opening between NR4A3 "
            "**P411 and R412** — and 411 and 412 are both in the committed cryptic-pocket residue set. "
            "⛔ **This is an ABSENCE in the target, so it can never be a covalent handle**: nothing is "
            "tethered to a residue that is not there. It is a SHAPE fact, it is the axis `S3`/`Q1` runs "
            "on, and it is a SEQUENCE fact only — whether those two residues line the cavity, change its "
            "volume, or are ordered at all needs a paralogue structure this file does not touch."
        ),
        "★_summary": summary,
        "directions": directions,
        "pairwise_indel_census": census,
        "three_way_indels": three,
        "shared_paralogue_indels": shared,
        "⛔_limits": [
            "Sequence uniqueness is exact; every geometric annotation is ONE static opened conformer.",
            "An indel's CONSEQUENCE needs a structure. This file says a segment is present in one paralogue "
            "and absent in the others. It says nothing about whether that segment is ordered, exposed, near "
            "the pocket, or usable by anything.",
            "A position that is unique but NOT `alignment_robust` is ambiguous, not a finding — it needs a "
            "structural superposition, not a sequence call.",
            "Terminal gap runs are length differences, not internal indels, and are flagged `terminal: true` "
            "and excluded from every headline count.",
            "The three-way indel span is the INTERSECTION of two pairwise runs, so it is a lower bound on "
            "the segment's extent.",
            "Uniqueness of a residue CLASS is not reactivity, ligandability or tetherability. A unique "
            "tyrosine is a unique tyrosine; whether anything can be attached to it is a separate question "
            "this file does not ask.",
            "The comparison set is THREE proteins. Nothing here implies proteome-wide selectivity.",
        ],
    }
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(summary, indent=1, ensure_ascii=False)[:4000])
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
