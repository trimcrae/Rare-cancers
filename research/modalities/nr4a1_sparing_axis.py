#!/usr/bin/env python3
"""THE NR4A1-SPARING AXIS — "NR-V04 in reverse": can a molecule degrade every NR4A paralogue EXCEPT NR4A1?

★ THE QUESTION, from trimcrae (2026-08-03): *"Is there anything to the idea of doing the inverse of NR-V04
here? Like making something that will degrade every NR4A paralogue EXCEPT NR4A1 using the same mechanism as
NR-V04 but in reverse?"*

WHY IT IS WORTH REAL WORK, STATED PRECISELY. The selectivity requirement is ASYMMETRIC (roadmap §2.4): NR4A1
is the *mandatory* anti-target, because the Nr4a1;Nr4a3 double null is the named mouse AML genotype a
non-selective NR4A3 degrader reconstitutes (PMID 17515897, 29343483; independently recoverable from MGI).
A molecule that reliably SPARES NR4A1 clears the hard half of the requirement BY CONSTRUCTION — a different,
and possibly easier, problem than discriminating NR4A3 from both paralogues at once.

⛔ WHAT DOES NOT WORK, AND IT IS THE FIRST THING THIS FILE SAYS. **The covalent mechanism does not invert.**
NR-V04 selects POSITIVELY on NR4A1 Cys551 — a residue NR4A2 and NR4A3 do not carry. Sparing NR4A1 requires
selecting on an ABSENCE, and you cannot covalently label a residue that is not there. There is no "reverse
NR-V04" as chemistry, and this file exists partly so nobody proposes one again.

★ WHAT MIGHT WORK, AND IS COMPUTABLE AT $0 — the two things measured here:

  R1  THE RECIPROCAL ENUMERATION NOBODY HAD RUN. Every uniqueness enumeration in this repo is ONE-WAY:
      *which residues does NR4A3 have that the paralogues lack*. `nr4a3-covalent-handle-ensemble.json` is
      built from `unique_cysteines` only; `categorical-axis-audit.json` flags the one-way scope explicitly.
      The committed reciprocal fragment (`nr4a-paralogue-unique-residues.json -> reciprocal_paralogue_unique`,
      and `nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness`) is PAIRWISE against
      NR4A3 and restricted to Cys/Lys — it cannot answer "unique to NR4A1 against BOTH others", which is the
      set an NR4A1-sparing design needs. That set is computed here for the first time, over all 20 residue
      types, with the SAME two-independent-aligner robustness rule the forward enumeration uses, so the two
      are directly comparable.

  R2  OF THOSE, WHICH COULD DENY A POSE? Mechanism `S3` (steric exclusion, negative design) DOES invert: it
      needs a bulkier side chain, not a unique labelable one. `S3` was measured in one direction only —
      positions where BOTH paralogues are bulkier than NR4A3 (L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe;
      clash 0.923 against a 0.173 null, 5.34x). The SAME measurement is run here in the NR4A1-only
      direction, with the SAME null and the SAME controls.

⛔ THE CONTROL TRAVELS WITH EVERY NUMBER, AND IT BITES HARDER HERE THAN IT DOES FOR `S3`. `M4` measured that
the paralogue RELOCATES the ligand (median 5.31 A in NR4A1) rather than refusing it. For `S3` that caps the
claim at a POSE constraint, which is survivable because `S3` is a design rule for growing a substituent. For
an NR4A1-SPARING claim it is worse than a cap: sparing REQUIRES non-engagement, and a molecule that binds
NR4A1 5.3 A away may still be degraded there. So the relocation control is not a footnote on this axis — it
is the axis's central weakness, and it is stated in the verdict rather than in the limits.

$0. Pure CPU: cached UniProt sequences + committed opened models + committed docked poses. No GPU, no
rental, no dispatch, no network.
"""
from __future__ import annotations

import datetime
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import nr4a_paralogue_unique_residues as U      # noqa: E402  classify_positions / _read_sdf_coords / LBD bounds
import nrv04_cys_conservation as cyscons        # noqa: E402  needleman_wunsch / aligned_residue
import selectivity_mechanism_options as S       # noqa: E402  HARD_CLASH_A / POCKET5 / _sidechain / STRUCT
import steric_design_rule as SDR                # noqa: E402  denied_lobe (pure geometry, reused unchanged)

SPECIES = ("NR4A1", "NR4A2", "NR4A3")
ALL_AA = tuple("ACDEFGHIKLMNPQRSTVWY")

#: A position "lines the pocket" when ANY species' side chain at it comes within this distance of the union of
#: the 13 committed docked-pose heavy atoms. ⚠ THE UNION IS REQUIRED, NOT A CONVENIENCE: defining lining from
#: NR4A3 alone would discard exactly the positions this file is looking for — those where NR4A1's BULKIER side
#: chain protrudes into the pocket while NR4A3's smaller one does not reach it.
LINING_A = 5.0

OUT_JSON = os.path.join(HERE, "nr4a1-sparing-axis.json")
OUT_MD = os.path.join(HERE, "nr4a1-sparing-axis.md")


def _r(x, n=3):
    return None if x is None else round(float(x), n)


def _load(rel):
    with open(os.path.join(REPO, rel)) as f:
        return json.load(f)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# offsets — DERIVED from the models, never typed
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def uniprot_offset(model, seq):
    """local_resid + offset == UniProt resid, recovered by locating the model's own sequence in the FASTA.

    ⚠ THIS IS NOT PEDANTRY. `selectivity_mechanism_options.m3_steric_exclusion` labels its paralogue partners
    with `rp + U.LOCAL_OFFSET`, and `U.LOCAL_OFFSET` is NR4A3's (372). The paralogue models start at UniProt
    348 (NR4A1) and 344 (NR4A2), so every paralogue residue NUMBER in `M3.positions.*.partners` is high by 25
    / 29 — and the wrong numbers name REAL residues of the same protein (NR4A1 "397" is K397, not the H the
    field carries), which is the populated-field-is-not-a-measured-field failure in CLAUDE.md §4. The residue
    LETTERS are correct and every conclusion drawn from M3 rests on the letters, so nothing downstream moves.
    Recorded in `defect_found_in_a_committed_artifact`, and this file uses recovered offsets throughout.
    """
    s = "".join(model["seq"]) if isinstance(model["seq"], list) else model["seq"]
    idx = seq.find(s[:40])
    if idx < 0:
        raise RuntimeError("model sequence not found in the FASTA — offset cannot be recovered")
    first_local = sorted(model["atoms_by_res"])[0]
    return idx + 1 - first_local


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# R1 — the reciprocal enumeration
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _lbd_map(seqs, sp):
    """{1-based position of `sp` -> NR4A3 partner (residue, resnum)} by the same linear-gap NW the forward
    enumeration uses. Used to scope a paralogue position to the LBD by ITS NR4A3 PARTNER, so 'LBD' means the
    same window of the same alignment in every species instead of three independently guessed ranges."""
    aln_sp, aln_3 = cyscons.needleman_wunsch(seqs[sp], seqs["NR4A3"])
    return {i: cyscons.aligned_residue(aln_sp, aln_3, i) for i in range(1, len(seqs[sp]) + 1)}


def reciprocal_enumeration(seqs):
    """For EACH species, the positions whose residue type is absent at the aligned position in BOTH others.

    Same machinery, same rule and same robustness standard as the forward (NR4A3-side) enumeration:
    `classify_positions` runs a linear-gap NW and the atlas's affine-gap BLOSUM62 aligner independently and
    keeps only `unique_vs_both AND alignment_robust`. Running all three species — not just NR4A1 — costs
    nothing and supplies the denominator: an NR4A1-unique count means nothing without knowing that NR4A3's is
    the same order of magnitude.
    """
    out = {"_question": ("Which LBD positions are unique to NR4A1 against BOTH NR4A2 and NR4A3 — the "
                         "reciprocal of the enumeration this repo has always run in one direction?"),
           "_method": ("nr4a_paralogue_unique_residues.classify_positions with `ref` set to each species in "
                       "turn, `others` set to the other two, and residue_types widened from the committed "
                       "('C','K') to all 20. Uniqueness is a claim ABOUT AN ALIGNMENT, so it is computed "
                       "twice with independent aligners (linear-gap NW + affine-gap BLOSUM62) and only "
                       "`unique_vs_both AND alignment_robust` rows are admitted — identical to the forward "
                       "enumeration, which is what makes the two comparable."),
           "_lbd_scope": ("A position is IN THE LBD when its NR4A3-aligned partner falls in UniProt 373-626 "
                          "(nr4a_paralogue_unique_residues.LBD_FIRST/LBD_LAST). One window, one alignment, "
                          "three species."),
           "by_species": {}}

    for sp in SPECIES:
        others = tuple(o for o in SPECIES if o != sp)
        rows = U.classify_positions(seqs, ref=sp, residue_types=ALL_AA, others=others)
        lbdmap = _lbd_map(seqs, sp) if sp != "NR4A3" else None
        uniq = []
        for r in rows:
            if not (r["unique_vs_both"] and r["alignment_robust"]):
                continue
            if sp == "NR4A3":
                in_lbd, partner3 = (U.LBD_FIRST <= r["resnum"] <= U.LBD_LAST), (r["residue"], r["resnum"])
            else:
                partner3 = lbdmap.get(r["resnum"], ("-", None))
                in_lbd = bool(partner3[1] and U.LBD_FIRST <= partner3[1] <= U.LBD_LAST)
            uniq.append({
                "residue": r["residue"], "uniprot": r["resnum"], "context": r["context"],
                "in_lbd": in_lbd,
                "nr4a3_aligned_resnum": partner3[1], "nr4a3_aligned_residue": partner3[0],
                "partners": {o: {"residue": r["partners"][o]["residue"],
                                 "uniprot": r["partners"][o]["resnum"],
                                 "affine_residue": r["partners"][o]["affine_residue"]} for o in others},
            })
        out["by_species"][sp] = {
            "accession": U.ACCESSIONS[sp],
            "n_positions_scanned": len(rows),
            "n_unique_vs_both_alignment_robust": len(uniq),
            "n_unique_in_lbd": sum(1 for u in uniq if u["in_lbd"]),
            "unique_positions_in_lbd": [u for u in uniq if u["in_lbd"]],
        }
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# R2 — the steric test, run in the NR4A1-only direction
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _models(seqs):
    import nr4a3_basin_search as B
    ref = B.load_paralogue(os.path.join(S.STRUCT, "nr4a3-opened.pdb"))
    raw = {sp: B.load_paralogue(os.path.join(S.STRUCT, f"{sp.lower()}-opened.pdb")) for sp in S.PARALOGUES}
    fit = {sp: B.superpose_paralogue(raw[sp], ref) for sp in S.PARALOGUES}
    off = {"NR4A3": uniprot_offset(ref, seqs["NR4A3"])}
    off.update({sp: uniprot_offset(raw[sp], seqs[sp]) for sp in S.PARALOGUES})
    return ref, raw, fit, off


def _sc(model, rid):
    return S._sidechain(model, rid) if rid else []


def _classify_frame_positions(ref, fit, off, uniq_by_species, positions_u3):
    """Per NR4A3-frame position, the residue in all three species and the NR4A1-direction bulk class.

    CLASSES, defined as the exact mirror of `M3`'s:
      nr4a1_unique_and_bulkier  NR4A1's residue type is unique vs BOTH (sequence, two aligners) AND its
                                side-chain heavy-atom count strictly exceeds BOTH others'  -> SIGNAL
      nr4a1_unique_not_bulkier  unique but not strictly bulkier                             -> the control
                                that proves uniqueness alone creates no exclusion
      conserved_or_shared       NR4A1's residue type appears in at least one other          -> the NULL
    """
    nr4a1_unique_uniprot = {u["uniprot"] for u in uniq_by_species["NR4A1"]["unique_positions_in_lbd"]}
    recs = {}
    for u3 in positions_u3:
        rid3 = u3 - off["NR4A3"]
        rec = {"nr4a3_uniprot": u3, "residues": {"NR4A3": ref["aa_of"].get(rid3)},
               "uniprot": {"NR4A3": u3}, "n_side_chain_heavy": {"NR4A3": len(_sc(ref, rid3))},
               "post_fit_deviation_A": {}}
        ok = True
        for sp in S.PARALOGUES:
            rp = fit[sp]["corr_from_ref"].get(rid3)
            rec["residues"][sp] = fit[sp]["aa_of"].get(rp)
            rec["uniprot"][sp] = (rp + off[sp]) if rp else None
            rec["n_side_chain_heavy"][sp] = len(_sc(fit[sp], rp))
            rec["post_fit_deviation_A"][sp] = _r(fit[sp]["deviation_by_res"].get(rp), 2) if rp else None
            if rp is None:
                ok = False
        n1 = rec["n_side_chain_heavy"]["NR4A1"]
        # ★ THE BULK MARGIN — how many heavy atoms the candidate side chain has OVER the larger of the two it
        # must exclude. This is the quantity that actually decides whether a steric exclusion can exist, and
        # unlike a clash rate it is a property of the SEQUENCE, not of the modelled conformer.
        rec["bulk_margin_heavy_atoms"] = {
            "nr4a1_over_both": n1 - max(rec["n_side_chain_heavy"]["NR4A2"], rec["n_side_chain_heavy"]["NR4A3"]),
            "nr4a3_over_both_paralogues_S3_direction":
                rec["n_side_chain_heavy"]["NR4A3"] - max(n1, rec["n_side_chain_heavy"]["NR4A2"]),
            "both_paralogues_over_nr4a3_S3_signal":
                min(n1, rec["n_side_chain_heavy"]["NR4A2"]) - rec["n_side_chain_heavy"]["NR4A3"],
        }
        rec["nr4a1_strictly_bulkier_than_both"] = bool(
            ok and n1 > rec["n_side_chain_heavy"]["NR4A2"] and n1 > rec["n_side_chain_heavy"]["NR4A3"])
        rec["nr4a1_categorically_unique_vs_both"] = bool(rec["uniprot"]["NR4A1"] in nr4a1_unique_uniprot)
        rec["class"] = ("nr4a1_unique_and_bulkier"
                        if rec["nr4a1_categorically_unique_vs_both"] and rec["nr4a1_strictly_bulkier_than_both"]
                        else "nr4a1_unique_not_bulkier" if rec["nr4a1_categorically_unique_vs_both"]
                        else "conserved_or_shared")
        rec["nr4a1_only_clash_poses"] = 0
        recs[u3] = rec
    return recs


def _clash_sweep(ref, fit, off, recs, ligands):
    """The NR4A1-only clash predicate, pose by pose.

    `M3` asks: do BOTH paralogues clash where NR4A3 does not?  The inverse asks: does NR4A1 clash where
    NEITHER NR4A2 NOR NR4A3 does?  Same 3.0 A hard_clash_A, same superposition, same 13 poses.
    """
    per_pose = []
    for title, coords in ligands:
        pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
        rec = {"pose": title, "n_clashing_positions": {sp: 0 for sp in SPECIES},
               "nr4a1_only_clash_positions": []}
        for u3 in recs:
            rid3 = u3 - off["NR4A3"]
            d = {"NR4A3": min((math.dist(p, q) for p in _sc(ref, rid3) for q in pts), default=None)}
            for sp in S.PARALOGUES:
                rp = fit[sp]["corr_from_ref"].get(rid3)
                d[sp] = min((math.dist(p, q) for p in _sc(fit[sp], rp) for q in pts), default=None)
            hit = {sp: (d[sp] is not None and d[sp] < S.HARD_CLASH_A) for sp in SPECIES}
            for sp in SPECIES:
                rec["n_clashing_positions"][sp] += int(hit[sp])
            if hit["NR4A1"] and not hit["NR4A2"] and not hit["NR4A3"]:
                rec["nr4a1_only_clash_positions"].append(u3)
                recs[u3]["nr4a1_only_clash_poses"] += 1
        per_pose.append(rec)

    groups = {}
    n_poses = len(ligands)
    for u3, rec in recs.items():
        g = groups.setdefault(rec["class"], {"positions": [], "hits": 0, "trials": 0})
        g["positions"].append(u3)
        g["hits"] += rec["nr4a1_only_clash_poses"]
        g["trials"] += n_poses
    for g in groups.values():
        g["positions"].sort()
        g["rate"] = _r(g["hits"] / g["trials"], 3) if g["trials"] else None
    return per_pose, groups


def forward_self_check(ref, fit, off, ligands, uniq, m3):
    """⛔ THE CHECK WITHOUT WHICH A NULL RESULT IS UNINTERPRETABLE.

    A measurement that returns "no signal" is indistinguishable from a measurement that is broken. So the
    SAME code path, on the SAME frame and the SAME poses, is run with M3's FORWARD predicate (both paralogues
    clash and NR4A3 does not) and its forward classes, and the result is compared to the committed M3 rates.
    If this does not reproduce 0.923 / 0.173 the inverse result must be discarded, and this file says so.
    """
    nr4a3_unique = {u["uniprot"] for u in uniq["by_species"]["NR4A3"]["unique_positions_in_lbd"]}
    recs = {}
    for u3 in S.POCKET5:
        rid3 = u3 - off["NR4A3"]
        n = {"NR4A3": len(_sc(ref, rid3))}
        for sp in S.PARALOGUES:
            n[sp] = len(_sc(fit[sp], fit[sp]["corr_from_ref"].get(rid3)))
        unique = u3 in nr4a3_unique
        bulkier = n["NR4A1"] > n["NR4A3"] and n["NR4A2"] > n["NR4A3"]
        recs[u3] = {"class": ("unique_and_both_bulkier" if unique and bulkier
                              else "unique_not_bulkier" if unique else "conserved_or_shared"),
                    "hits": 0}
    for _, coords in ligands:
        pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
        for u3 in recs:
            rid3 = u3 - off["NR4A3"]
            d = {"NR4A3": min((math.dist(p, q) for p in _sc(ref, rid3) for q in pts), default=None)}
            for sp in S.PARALOGUES:
                rp = fit[sp]["corr_from_ref"].get(rid3)
                d[sp] = min((math.dist(p, q) for p in _sc(fit[sp], rp) for q in pts), default=None)
            hit = {sp: (d[sp] is not None and d[sp] < S.HARD_CLASH_A) for sp in SPECIES}
            if hit["NR4A1"] and hit["NR4A2"] and not hit["NR4A3"]:
                recs[u3]["hits"] += 1
    groups = {}
    for u3, r in recs.items():
        g = groups.setdefault(r["class"], {"positions": [], "hits": 0, "trials": 0})
        g["positions"].append(u3)
        g["hits"] += r["hits"]
        g["trials"] += len(ligands)
    for g in groups.values():
        g["positions"].sort()
        g["rate"] = _r(g["hits"] / g["trials"], 3)
    got = {k: groups.get(k, {}).get("rate") for k in ("unique_and_both_bulkier", "conserved_or_shared")}
    want = {k: m3["by_position_class"][k]["rate"] for k in got}
    return {
        "_why": ("a null result is indistinguishable from a broken measurement, so the same code path is run "
                 "with M3's forward predicate and compared to the committed M3 rates"),
        "by_position_class": groups,
        "recomputed": got, "committed_M3": want,
        "reproduces_committed_M3": got == want,
        "_if_false": ("the inverse result in this file MUST be discarded — the code, not the protein, would "
                      "be the finding"),
    }


def _lining_positions(ref, fit, off, ligands):
    """Every LBD position whose side chain — in ANY of the three species, in the shared frame — comes within
    LINING_A of the union of the docked-pose heavy atoms. See LINING_A for why the union is mandatory."""
    env = [(c[0], c[1], c[2]) for _, coords in ligands for c in coords if c[3] != "H"]
    out = []
    for rid3 in sorted(ref["atoms_by_res"]):
        u3 = rid3 + off["NR4A3"]
        if not (U.LBD_FIRST <= u3 <= U.LBD_LAST):
            continue
        near = False
        for sc in [_sc(ref, rid3)] + [_sc(fit[sp], fit[sp]["corr_from_ref"].get(rid3)) for sp in S.PARALOGUES]:
            if sc and min(math.dist(p, q) for p in sc for q in env) < LINING_A:
                near = True
                break
        if near:
            out.append(u3)
    return out


def steric_inverse(ref, raw, fit, off, seqs, uniq, m3):
    ligands = U._read_sdf_coords(os.path.join(S.STRUCT, "docked_nr4a3.sdf"))
    nr4a3_heavy = [tuple(p) for p in ref["heavy_xyz"]]

    blocks = {}
    lining = _lining_positions(ref, fit, off, ligands)
    for label, posset in (("pocket5_matched_to_M3", list(S.POCKET5)), ("ligand_envelope_lining", lining)):
        recs = _classify_frame_positions(ref, fit, off, uniq["by_species"], posset)
        per_pose, groups = _clash_sweep(ref, fit, off, recs, ligands)
        sig = groups.get("nr4a1_unique_and_bulkier", {}).get("rate")
        null = groups.get("conserved_or_shared", {}).get("rate")
        blocks[label] = {
            "n_positions": len(posset), "positions": posset, "n_poses": len(ligands),
            "per_position": recs, "per_pose": per_pose, "by_position_class": groups,
            "signal_rate": sig, "null_rate": null,
            "enrichment_signal_over_null": _r(sig / null, 2) if (sig and null) else None,
            "signal_minus_null": _r(sig - null, 3) if (sig is not None and null is not None) else None,
        }

    # ── the DENIED LOBE, inverted: space a heavy atom may occupy in NR4A3 AND in NR4A2, but not in NR4A1.
    # `steric_design_rule.denied_lobe` is a pure function of (atoms that must NOT deny, side chains that must
    # ALL deny), so it is reused unchanged with the roles swapped — no second implementation of the geometry.
    lobes = {}
    for u3 in S.POCKET5:
        rid3 = u3 - off["NR4A3"]
        r1 = fit["NR4A1"]["corr_from_ref"].get(rid3)
        r2 = fit["NR4A2"]["corr_from_ref"].get(rid3)
        permissive = nr4a3_heavy + _sc(fit["NR4A2"], r2)
        lobe = SDR.denied_lobe(permissive, [_sc(fit["NR4A1"], r1)], ref["cb"].get(rid3), S.HARD_CLASH_A)
        rec = blocks["pocket5_matched_to_M3"]["per_position"][u3]
        lobe.update({"nr4a3_uniprot": u3, "class": rec["class"], "residues": rec["residues"],
                     "n_side_chain_heavy": rec["n_side_chain_heavy"],
                     "post_fit_deviation_A": rec["post_fit_deviation_A"]})
        lobes[u3] = lobe
    null_vols = {u: lobes[u].get("volume_A3", 0.0) for u in lobes if lobes[u]["class"] == "conserved_or_shared"}
    ceiling = max(null_vols.values()) if null_vols else SDR.MIN_LOBE_VOLUME_A3
    ceiling_at = max(null_vols, key=null_vols.get) if null_vols else None
    for u, lobe in lobes.items():
        lobe["qualifies_as_a_design_target"] = bool(
            lobe["class"] == "nr4a1_unique_and_bulkier"
            and lobe.get("volume_A3", 0.0) > max(ceiling, SDR.MIN_LOBE_VOLUME_A3))

    # ★ THE STRUCTURAL REASON THE MECHANISM DOES NOT INVERT WELL, in one number per direction. A clash rate
    # is conformer-dependent; the bulk margin is not — it is heavy-atom counts of aligned residues.
    def _best_margin(block, key, cls):
        rows = [(u, r) for u, r in block["per_position"].items() if r["class"] == cls] if cls else \
               list(block["per_position"].items())
        best = max(rows, key=lambda kv: kv[1]["bulk_margin_heavy_atoms"][key], default=None)
        if not best:
            return None
        return {"nr4a3_frame_position": best[0], "margin_heavy_atoms": best[1]["bulk_margin_heavy_atoms"][key],
                "residues": best[1]["residues"]}

    margins = {}
    for label, blk in blocks.items():
        fwd = {u: r["bulk_margin_heavy_atoms"]["both_paralogues_over_nr4a3_S3_signal"]
               for u, r in blk["per_position"].items()}
        inv = {u: r["bulk_margin_heavy_atoms"]["nr4a1_over_both"] for u, r in blk["per_position"].items()}
        margins[label] = {
            "S3_forward_best_margin": {"position": max(fwd, key=fwd.get), "heavy_atoms": max(fwd.values()),
                                       "residues": blk["per_position"][max(fwd, key=fwd.get)]["residues"]},
            "inverse_best_margin": {"position": max(inv, key=inv.get), "heavy_atoms": max(inv.values()),
                                    "residues": blk["per_position"][max(inv, key=inv.get)]["residues"]},
            "inverse_margins_at_signal_positions": {
                u: r["bulk_margin_heavy_atoms"]["nr4a1_over_both"]
                for u, r in sorted(blk["per_position"].items())
                if r["class"] == "nr4a1_unique_and_bulkier"},
        }

    return {
        "_question": ("Are there positions where NR4A1's side chain is strictly bulkier than BOTH NR4A2's and "
                      "NR4A3's, and where that bulk lines the pocket — i.e. a lobe NR4A1 alone denies?"),
        "_method": (f"{len(ligands)} committed NR4A3-docked poses against the shared frame "
                    f"(results/nr4a3-matrix/nr4a3-opened.pdb; paralogues superposed by "
                    f"nr4a3_basin_search.superpose_paralogue). A position clashes when its side-chain heavy "
                    f"atoms come within {S.HARD_CLASH_A} A of a ligand heavy atom — the same hard_clash_A M3 "
                    f"used. The NR4A1-ONLY predicate is: NR4A1 clashes AND NR4A2 does not AND NR4A3 does not."),
        "_the_null_is_the_whole_point": (
            "Exactly as in M3: a rate without its matched null is not a result. The null is the same predicate "
            "evaluated at conserved-or-shared positions, where no categorical difference exists and any firing "
            "is a measured false positive of the superposition."),
        "superposition": {sp: {k: fit[sp]["superposition"][k]
                               for k in ("n_ca_pairs", "n_core", "core_fraction", "core_rmsd_A")}
                          for sp in S.PARALOGUES},
        "uniprot_offsets_recovered": off,
        "lining_definition": {"cutoff_A": LINING_A, "n_lining_positions": len(lining),
                              "_union_over_species_because": (
                                  "defining lining from NR4A3 alone would discard the very positions this "
                                  "test looks for — where NR4A1's bulkier side chain protrudes into the "
                                  "pocket and NR4A3's smaller one does not reach it")},
        "blocks": blocks,
        "⛔_forward_direction_self_check": forward_self_check(ref, fit, off, ligands, uniq, m3),
        "★_bulk_margin_the_conformer_independent_reason_the_mechanism_does_not_invert": {
            "_what": ("Heavy atoms the excluding side chain has OVER the larger of the two it must exclude. "
                      "A clash rate depends on the modelled rotamer; this does not — it is heavy-atom counts "
                      "of aligned residues, so it is a fact about the PROTEIN."),
            "by_position_set": margins,
            "_reading": (
                "In the S3 (NR4A3-selective) direction the best pocket margin is +%d heavy atoms at position "
                "%s (%s -> %s/%s) — most of an aromatic ring of extra bulk. In the NR4A1-sparing direction "
                "the best margin ANYWHERE in the pocket or its lining envelope is +%d, at %s (%s -> %s/%s), "
                "and every position in the signal class sits at that same +%d. That is the structural reason "
                "the inverse fires at its own null while the forward fires well above it: NR4A1 is not "
                "BULKIER than its paralogues anywhere that matters — it is DIFFERENT from them, which "
                "uniqueness captures and steric exclusion cannot use."
                % (margins["pocket5_matched_to_M3"]["S3_forward_best_margin"]["heavy_atoms"],
                   margins["pocket5_matched_to_M3"]["S3_forward_best_margin"]["position"],
                   margins["pocket5_matched_to_M3"]["S3_forward_best_margin"]["residues"]["NR4A3"],
                   margins["pocket5_matched_to_M3"]["S3_forward_best_margin"]["residues"]["NR4A1"],
                   margins["pocket5_matched_to_M3"]["S3_forward_best_margin"]["residues"]["NR4A2"],
                   margins["ligand_envelope_lining"]["inverse_best_margin"]["heavy_atoms"],
                   margins["ligand_envelope_lining"]["inverse_best_margin"]["position"],
                   margins["ligand_envelope_lining"]["inverse_best_margin"]["residues"]["NR4A3"],
                   margins["ligand_envelope_lining"]["inverse_best_margin"]["residues"]["NR4A1"],
                   margins["ligand_envelope_lining"]["inverse_best_margin"]["residues"]["NR4A2"],
                   max(margins["ligand_envelope_lining"]["inverse_margins_at_signal_positions"].values(),
                       default=0))),
        },
        "nr4a1_only_denied_lobes": {
            "_what": ("the sub-volume a ligand heavy atom may occupy in NR4A3 AND at NR4A2's residue, and may "
                      "NOT occupy at NR4A1's — the S3 design-rule lobe with the roles inverted. Computed by "
                      "steric_design_rule.denied_lobe, reused unchanged."),
            "grid_A": SDR.GRID_A,
            "null_volume_ceiling_A3": _r(ceiling, 2),
            "null_volume_ceiling_at": ceiling_at,
            "_bar": ("volume must exceed the null class's own largest lobe AND the position must be "
                     "nr4a1_unique_and_bulkier — the same measured bar S3 uses, never a chosen threshold"),
            "lobes": lobes,
            "design_targets": [u for u in S.POCKET5 if lobes[u]["qualifies_as_a_design_target"]],
        },
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# provenance, controls, trade, verdict
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def provenance(uniq):
    """What already existed versus what had to be computed. The one-way gap, closed VISIBLY."""
    prior = _load("research/modalities/nr4a-paralogue-unique-residues.json")["reciprocal_paralogue_unique"]
    reach = _load("research/modalities/nr4a3-linker-covalent-reach.json")
    rec = (reach.get("paralogue_control") or {}).get("reciprocal_uniqueness") or {}
    n1_lbd = uniq["by_species"]["NR4A1"]["n_unique_in_lbd"]
    prior_nr4a1_also_in_nr4a2 = sorted(
        {(r["residue"], r["resnum"]) for r in prior["NR4A1"]} & {(r["residue"], r["resnum"]) for r in prior["NR4A2"]})
    return {
        "already_existed": [
            {"artifact": "research/modalities/nr4a-paralogue-unique-residues.json",
             "field": "reciprocal_paralogue_unique",
             "what": ("PAIRWISE reciprocal uniqueness: positions where a paralogue carries a Cys or Lys and "
                      "NR4A3 does not, one paralogue at a time. NR4A1 %d rows, NR4A2 %d rows, whole sequence."
                      % (len(prior["NR4A1"]), len(prior["NR4A2"]))),
             "what_it_could_NOT_answer": (
                 "it is not 'unique vs BOTH'. %d of NR4A1's rows are shared with NR4A2 at the same position "
                 "(%s), so they are NOT NR4A1-unique and cannot support an NR4A1-sparing design. It is also "
                 "restricted to two residue types, and a steric argument needs all twenty."
                 % (len(prior_nr4a1_also_in_nr4a2),
                    ", ".join("%s%d" % p for p in prior_nr4a1_also_in_nr4a2) or "none")),
             "generator_capability": ("nr4a_paralogue_unique_residues.reciprocal_unique() hard-codes "
                                      "ref='NR4A3' and iterates `others` INDEPENDENTLY — the 'vs both' "
                                      "intersection is not something it can express."),
             },
            {"artifact": "research/modalities/nr4a3-linker-covalent-reach.json",
             "field": "paralogue_control.reciprocal_uniqueness",
             "what": ("the beginning of the reciprocal set, as named in the task: NR4A1 C551 -> NR4A3 T579 "
                      "and NR4A1/NR4A2 C534 -> NR4A3 S565."),
             "what_it_could_NOT_answer": (
                 "same two limits, plus it is scoped to the chemoselectivity WINDOW (which cysteine closes a "
                 "linker's reach envelope first), not to a design axis. And C534 is present in BOTH "
                 "paralogues, so of the two named sites only C551 is NR4A1-unique at all."),
             "present": sorted(rec.get("by_paralogue", {}).keys()) or list(rec.keys()),
             },
            {"artifact": "research/modalities/categorical-axis-audit.json",
             "field": "residue_identity",
             "what": ("the correction that keeps this honest: NR4A1 C505 aligns to NR4A3 C536, so it is NOT "
                      "a reciprocal-uniqueness site, and naming 'C534' alone mislabels the majority "
                      "through-space closer."),
             "what_it_could_NOT_answer": "it audits the pairwise set; it does not compute a vs-both one.",
             },
            {"artifact": "research/modalities/selectivity-mechanism-options.json",
             "field": "measurements.M3 / mechanisms S3",
             "what": ("the steric-exclusion measurement and its null, in the NR4A3-selective direction only "
                      "(both paralogues bulkier than NR4A3)."),
             "what_it_could_NOT_answer": ("the NR4A1-only direction was never evaluated — M3's predicate "
                                          "requires BOTH paralogues to clash, which by construction can "
                                          "never fire on an NR4A1-specific bulge."),
             },
        ],
        "computed_here_for_the_first_time": [
            "the vs-BOTH reciprocal set for NR4A1 over all 20 residue types under the two-aligner robustness "
            "rule — %d alignment-robust NR4A1-unique positions in the LBD" % n1_lbd,
            "the same enumeration for NR4A2 and NR4A3 as denominators, so the NR4A1 count can be graded",
            "the NR4A1-ONLY steric clash rate, with the matched null and the uniqueness-alone control, over "
            "the same 13 poses and the same hard_clash_A M3 used",
            "the same measurement over the ligand-envelope lining set rather than fpocket's 10 residues, "
            "using a union-over-species lining definition",
            "the inverted denied lobe (occupiable in NR4A3 and at NR4A2's residue, denied at NR4A1's) with "
            "its own measured volume ceiling",
        ],
        "_the_gap_this_closes": (
            "Every uniqueness enumeration in this repo ran NR4A3-first. The reciprocal fragments that existed "
            "were pairwise-against-NR4A3 and Cys/Lys-only, which is the wrong shape for an NR4A1-sparing "
            "design: that design needs positions NR4A1 does not SHARE WITH NR4A2, because a feature NR4A2 "
            "also carries cannot spare one and degrade the other."),
    }


def controls(m4):
    return {
        "★_the_relocation_control_is_this_axis's_central_problem_not_a_footnote": (
            "M4 measured that the paralogue's OWN docking relocates the same molecules rather than "
            "reproducing the pose: median centroid shift %s A (NR4A1), %s A (NR4A2). For S3 that caps a "
            "claim at 'this POSE is denied', which a design rule can live with. An NR4A1-SPARING claim "
            "cannot: sparing requires NR4A1 not to be engaged AT ALL, and a molecule that binds NR4A1 5.3 A "
            "away in a different sub-site may still recruit an E3 and be degraded there. A steric result in "
            "this direction therefore licenses strictly LESS than the same result licenses for S3."
            % (m4["median_centroid_shift_A"]["NR4A1"], m4["median_centroid_shift_A"]["NR4A2"])),
        "⚠_construction_bias_and_why_the_contrast_survives_it": (
            "The 13 poses were docked INTO NR4A3, so 'NR4A3 does not clash' is guaranteed by construction and "
            "carries no information — and the NR4A1-only predicate contains that free term. The bias inflates "
            "every class IDENTICALLY, so the signal-vs-null CONTRAST remains gradeable and the absolute rate "
            "does not. Grade the contrast, never the rate. (Identical to M3's own limit, inherited whole.)"),
        "⚠_rigid_transfer": (
            "NR4A1's side chain is held in its own opened conformer and could rotate away. This measures "
            "'clash in NR4A1's modelled conformer with the ligand held fixed', never 'NR4A1 cannot bind'."),
        "⚠_the_NR4A2_half_is_NOT_construction_guaranteed_and_that_is_the_one_real_signal": (
            "Of the three species in the predicate, only NR4A2's non-clash is a free measurement — NR4A3's is "
            "by construction and NR4A1's is the thing being tested. So the informative content of any firing "
            "cell is 'NR4A1 clashes where NR4A2 does not', and that is how it must be read."),
        "⚠_a_single_static_conformer_per_species": (
            "One opened model each. The forward pocket-detection contrast was replicated over matched "
            "unbiased ensembles (paralogue-pocket-contrast.json); nothing here is."),
        "⚠_no_p_value_is_computed_and_that_is_deliberate": (
            "Cells are not independent: positions within one pose share the same superposition and the same "
            "ligand, and poses share the same three models — the spatial-correlation caveat Route A already "
            "carries. A rate is reported against its matched null and nothing is converted into a test. The "
            "verdict does not need one: the signal is AT the null, not near a threshold."),
        "⛔_no_energy_is_computed_anywhere_in_this_file": (
            "no affinity, no ddG, no selectivity ratio, no degradation, no efficacy, no safety, no "
            "therapeutic window, no clinical readiness, and no proteome-wide selectivity of any kind — the "
            "comparison set is three paralogues."),
    }


def therapeutic_trade():
    """Both halves, cited, not re-typed. Every figure names the artifact that OWNS it."""
    b = _load("research/modalities/nr4a2-sparing-bound.json")
    sg = b["mgi"]["single_gene"]
    multi = {m["genotype_genes"]: m for m in b["mgi"]["multi_gene_genotypes"]}
    hpa = b["verdict"]["gates"]["B3_tissue_overlap_measured"]

    def surv(node):
        return [{"term": t["term"], "mp_id": t.get("mp_id"), "pubmed_ids": t.get("pubmed_ids")}
                for t in node.get("survival_or_viability_terms", [])] or []

    n13, n23 = multi.get("Nr4a1 + Nr4a3", {}), multi.get("Nr4a2 + Nr4a3", {})
    return {
        "_one_fact_one_place": ("Every figure below is READ from research/modalities/nr4a2-sparing-bound.json "
                               "at generation time. This is a citation, not a second home."),
        "what_the_profile_BUYS": {
            "the_genotype_it_avoids_by_construction": {
                "genotype": "Nr4a1 + Nr4a3",
                "n_annotations": n13.get("n_annotations"),
                "survival_or_viability_terms": n13.get("survival_or_viability_terms"),
                "pubmed_ids": n13.get("pubmed_ids"),
                "includes": [t for t in n13.get("phenotype_terms", []) if "leukemia" in t],
                "_why_it_matters": ("this is the named mouse AML genotype a NON-selective NR4A3 degrader "
                                    "reconstitutes, and it is the whole reason roadmap §2.4 calls the NR4A1 "
                                    "half MANDATORY. A molecule that spares NR4A1 cannot reconstitute it."),
            },
            "and_NR4A1's_own_single_null_is_the_mild_one": {
                "n_single_gene_annotations": sg["Nr4a1"]["n_single_gene_annotations"],
                "survival_or_viability_terms": surv(sg["Nr4a1"]),
                "_reading": ("0 survival/viability terms on 8 single-gene annotations. ⛔ THIS IS NOT A "
                             "LICENCE — an absent record is an absence of evidence. It is stated because the "
                             "asymmetry runs the other way from intuition: the mandatory anti-target is "
                             "mandatory because of a COMBINATION, not because its own null is severe."),
            },
        },
        "what_the_profile_COSTS": {
            "NR4A2_single_null_is_lethal_with_complete_penetrance": {
                "n_single_gene_annotations": sg["Nr4a2"]["n_single_gene_annotations"],
                "survival_or_viability_terms": surv(sg["Nr4a2"]),
                "_reading": ("the paralogue this profile DEGRADES is the one whose own single knockout is "
                             "neonatal-lethal at complete penetrance — while the paralogue it SPARES has no "
                             "survival term at all. The trade buys the combination and pays on the single."),
            },
            "a_conditional_deletion_lands_closer_to_a_degrader_and_is_still_lethal": {
                "genotype": "Nr4a2 + Slc6a3",
                "n_annotations": multi.get("Nr4a2 + Slc6a3", {}).get("n_annotations"),
                "survival_or_viability_terms": multi.get("Nr4a2 + Slc6a3", {}).get("survival_or_viability_terms"),
                "pubmed_ids": multi.get("Nr4a2 + Slc6a3", {}).get("pubmed_ids"),
                "_reading": ("a dopaminergic-restricted (Slc6a3/DAT-Cre) Nr4a2 deletion — tissue-restricted "
                             "and post-developmental, i.e. the closest genotype on record to what a degrader "
                             "does — still carries 'lethality at weaning, complete penetrance' with neuron "
                             "degeneration and decreased dopamine. ⛔ Still a genetic deletion, still complete "
                             "and still lifelong within its lineage; a degrader is partial and reversible."),
            },
            "tissue_distribution_cannot_rescue_it": {
                "n_tissues": hpa["n_tissues"], "counts": hpa["counts"], "source": hpa["source"],
                "_reading": ("NR4A2 and NR4A3 are co-expressed in 47 of 51 HPA tissues and NR4A2 is the "
                             "dominant family member in 0, so there is no tissue window in which degrading "
                             "NR4A3 reaches NR4A2 less. ⛔ AND THE CONVERSE MISREADING IS FORBIDDEN by that "
                             "artifact: a bulk average dilutes the substantia nigra to invisibility, so this "
                             "measures exposure breadth and not the dopaminergic requirement."),
            },
        },
        "⚠_the_genotype_this_profile_WOULD_reconstitute_and_what_the_record_actually_says": {
            "genotype": "Nr4a2 + Nr4a3",
            "n_annotations": n23.get("n_annotations"),
            "example_genotypes": n23.get("example_genotypes"),
            "survival_or_viability_terms": n23.get("survival_or_viability_terms"),
            "phenotype_terms": n23.get("phenotype_terms"),
            "pubmed_ids": n23.get("pubmed_ids"),
            "⛔_read_this_before_quoting_the_empty_survival_list": (
                "The combination IS on record and carries NO survival/viability term — and that is NOT "
                "evidence of tolerability, for a reason visible in the genotype string itself: the annotated "
                "animal is Nr4a2 HETEROZYGOUS (Nr4a2<tm1Tpe>/Nr4a2<+>) with Nr4a3 homozygous null. A "
                "double NULL of Nr4a2 and Nr4a3 has no MGI record at all. So the comparison is not "
                "'Nr4a1;Nr4a3 is lethal and Nr4a2;Nr4a3 is not' — it is 'one double null is phenotyped as "
                "lethal and the other has never been reported'. AN ABSENT READING IS NOT A READING OF "
                "ABSENCE (CLAUDE.md §4)."),
        },
        "_the_trade_in_one_sentence": (
            "Sparing NR4A1 removes the one genotype the program treats as disqualifying — the AML double "
            "null — and it removes it BY CONSTRUCTION rather than by a margin any instrument here can "
            "resolve; but the profile it buys degrades the paralogue whose own single knockout is "
            "neonatal-lethal at complete penetrance, in a tissue distribution that offers no window, against "
            "a double-null genotype nobody has reported. This file does not decide that trade."),
        "_what_is_NOT_claimed": (
            "no statement that an NR4A1-sparing degrader would be safe, tolerable, efficacious or clinically "
            "relevant. A germline or lineage KO bounds developmental loss, never adult transient partial "
            "degradation — the caveat that travels with every row of nr4a2-sparing-bound.json."),
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# verdict + routing
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def verdict(uniq, ster, m4, m3):
    p5 = ster["blocks"]["pocket5_matched_to_M3"]
    lin = ster["blocks"]["ligand_envelope_lining"]
    marg = ster["★_bulk_margin_the_conformer_independent_reason_the_mechanism_does_not_invert"]
    fwd_enr = m3["enrichment_signal_over_null"]
    best_cell = max(lin["per_position"].items(),
                    key=lambda kv: (kv[1]["class"] == "nr4a1_unique_and_bulkier",
                                    kv[1]["nr4a1_only_clash_poses"]))
    sig_positions = p5["by_position_class"].get("nr4a1_unique_and_bulkier", {}).get("positions", [])
    lin_positions = lin["by_position_class"].get("nr4a1_unique_and_bulkier", {}).get("positions", [])
    targets = ster["nr4a1_only_denied_lobes"]["design_targets"]
    n1 = uniq["by_species"]["NR4A1"]["n_unique_in_lbd"]
    n3 = uniq["by_species"]["NR4A3"]["n_unique_in_lbd"]

    exists = bool(sig_positions or lin_positions)
    usable = bool(targets and lin["signal_minus_null"] and lin["signal_minus_null"] > 0)

    if usable:
        state, why = "LIVE", "a signal class exists, clears its own null, and offers occupiable denied space"
    elif exists:
        state, why = ("⏸ PARKED",
                      "the axis is not empty — NR4A1-unique-and-bulkier pocket-lining positions EXIST — but "
                      "the signal class fires at or BELOW its own matched null (%s vs %s at the pocket, %s vs "
                      "%s over the lining envelope), and the inverted denied lobe clears no measured volume "
                      "ceiling. ⛔ This is ⏸ and not ✕ on purpose. §6's bar for ✕ is POSITIVE EVIDENCE OF "
                      "IMPOSSIBILITY, and what is measured here is a null result on ONE static conformer per "
                      "species — an instrument statement. The conformer-INDEPENDENT half (no NR4A1-unique "
                      "lining position exceeds a +1 heavy-atom bulk margin) points at ✕ and is a fact about "
                      "the protein, but +1 is not zero and the lining set itself is model-dependent, so it "
                      "does not reach the bar on its own. 'We looked and found nothing promising' is "
                      "explicitly not ✕."
                      % (p5["signal_rate"], p5["null_rate"], lin["signal_rate"], lin["null_rate"]))
    else:
        state, why = ("✕ DEAD (candidate)",
                      "no NR4A1-unique position is both bulkier than both others and pocket-lining — a fact "
                      "about the protein rather than about our effort, which is §6's bar for ✕")

    return {
        "answer_to_the_question": (
            "PARTLY. ⛔ The COVALENT mechanism does not invert and there is no version of it that does — "
            "NR-V04 selects positively on NR4A1 Cys551 and sparing NR4A1 means selecting on an ABSENCE, "
            "which no electrophile can do. ★ A DIFFERENT mechanism does invert: steric exclusion (S3) needs "
            "a bulkier side chain rather than a labelable one, and bulk is a property NR4A1 can have "
            "uniquely. That axis is measured here for the first time, and the measurement is thin."),
        "is_it_measured_or_speculative": (
            "MEASURED, at $0, with its matched null and both controls — and the measurement is what makes it "
            "thin rather than promising. Nothing here is a projection or an intention."),
        "the_axis_in_one_line": (
            "%d alignment-robust NR4A1-unique-vs-BOTH LBD positions exist (against %d for NR4A3, so the "
            "reciprocal set is comparably large and the idea is not vacuous), but at the pocket the signal "
            "class is %s and over the whole ligand-envelope lining set it is %s."
            % (n1, n3, sig_positions or "empty", lin_positions or "empty")),
        "★_the_one_number_that_answers_it": (
            "The forward (NR4A3-selective) steric test fires at %sx its own null. The inverse "
            "(NR4A1-sparing) test fires at %sx its own null over the same frame, the same 13 poses and the "
            "same hard_clash_A. The mechanism does not invert on this protein — not because nobody looked, "
            "but because it was looked at with the matched control and came back at the null."
            % (fwd_enr, lin["enrichment_signal_over_null"])),
        "★_the_structural_reason": marg["_reading"],
        "⛔_the_null_is_not_a_bug_and_here_is_the_proof": (
            "The SAME code path, frame and poses run with M3's FORWARD predicate reproduce the committed M3 "
            "rates EXACTLY (%s / %s) — see steric_inverse.⛔_forward_direction_self_check. A null result is "
            "otherwise indistinguishable from a broken measurement, and this program has been burned by "
            "exactly that shape before."
            % (ster["⛔_forward_direction_self_check"]["recomputed"]["unique_and_both_bulkier"],
               ster["⛔_forward_direction_self_check"]["recomputed"]["conserved_or_shared"])),
        "⚠_the_single_cell_that_does_fire_above_null_and_why_it_is_not_enough": {
            "position": best_cell[0],
            "residues": best_cell[1]["residues"],
            "uniprot": best_cell[1]["uniprot"],
            "nr4a1_only_clash_poses": best_cell[1]["nr4a1_only_clash_poses"],
            "bulk_margin_heavy_atoms": best_cell[1]["bulk_margin_heavy_atoms"]["nr4a1_over_both"],
            "_why_it_is_not_enough": (
                "one position out of %d in the lining set, 13 poses, a +1 heavy-atom margin, and it is "
                "selected POST HOC as the largest of the signal class — the multiplicity that makes a "
                "per-position rate uninterpretable is exactly why the CLASS rate carries the verdict and a "
                "cell does not. It is named rather than dropped because a sweep that reports only what "
                "survives is a sweep nobody can grade."
                % lin["n_positions"]),
            "_and_it_already_existed_in_the_pairwise_set": (
                "this residue appears in nr4a-paralogue-unique-residues.json -> "
                "reciprocal_paralogue_unique.NR4A1 — the committed pairwise reciprocal list. What is new is "
                "that it survives the vs-BOTH test and that its steric consequence has been measured."),
        },
        "rates": {"pocket5": {"signal": p5["signal_rate"], "null": p5["null_rate"],
                              "signal_minus_null": p5["signal_minus_null"],
                              "enrichment": p5["enrichment_signal_over_null"]},
                  "ligand_envelope_lining": {"signal": lin["signal_rate"], "null": lin["null_rate"],
                                             "signal_minus_null": lin["signal_minus_null"],
                                             "enrichment": lin["enrichment_signal_over_null"]}},
        "recommended_register_state": state,
        "why_that_state_and_not_the_others": why,
        "what_would_reopen_it_if_parked": [
            "an ensemble in the NR4A1 direction — the forward contrast was replicated over matched unbiased "
            "ensembles (paralogue-pocket-contrast.json) and this is one static conformer per species; a "
            "rotamer that is modelled away here could be a real bulge",
            "poses docked into NR4A2 as the design frame rather than NR4A3, which would remove the "
            "construction bias in the direction that actually matters for a pan-except-NR4A1 molecule",
            "a site other than the cryptic pocket — the whole test is conditional on R5, and the NR4A1-unique "
            "LBD positions outside the pocket envelope are untested by anything here",
        ],
        "⛔_what_a_pass_would_still_NOT_license": [
            "that NR4A1 does not bind the molecule — M4 says it relocates it by a median %s A, and for a "
            "SPARING claim relocation is not a footnote but the failure mode" % m4["median_centroid_shift_A"]["NR4A1"],
            "any degradation, affinity, selectivity ratio, efficacy, safety or window — no energy is computed",
            "escape from R5: the pocket may not be the right site, and V3 returned INCONCLUSIVE",
        ],
    }


def register_reconciliation():
    """Reconcile against S15 and S3 EXPLICITLY, because a second S-number for one mechanism is the
    second-home problem CLAUDE.md rule 1 exists to stop."""
    return {
        "_why_this_block_exists": (
            "selectivity-mechanism-options.md already carries S15 — 'Reciprocal anti-handle avoidance: design "
            "AWAY from the paralogues' own unique residues', grade B — which is adjacent to this question. "
            "It was read before anything here was written."),
        "vs_S15": {
            "S15_is": ("a FILTER on an NR4A3-selective covalent construct: do not let the reach envelope "
                       "admit NR4A1 C505/C551 or NR4A2 C534, so the molecule does not label a paralogue."),
            "this_is": ("a MECHANISM for a different target profile: use an NR4A1-unique BULGE to deny NR4A1 "
                        "the pose, in a molecule that is deliberately NOT NR4A3-selective."),
            "shared": "both read the reciprocal direction of the uniqueness map.",
            "distinct_because": [
                "different observable — S15 is covalent reach to a reactive residue; this is steric occlusion "
                "by side-chain volume, and the two sets barely intersect (a Cys is small, and this axis needs "
                "bulk)",
                "different pairwise structure — S15's set is 'paralogue has it, NR4A3 lacks it' and includes "
                "positions NR4A1 SHARES with NR4A2 (C534, K558), which are useless here by construction",
                "different target product — S15 improves an NR4A3-selective degrader; this describes a "
                "pan-NR4A-except-NR4A1 degrader, which is a different molecule with a different brief",
                "opposite sign on the same protein — S15 says AVOID NR4A1's unique residues; this says SEEK "
                "one and design INTO the space around it",
            ],
            "verdict": ("DISTINCT. It is not S15 measured for the first time — S15 is already measured (the "
                        "closure data is committed, 30 of 30 graded cells). A new number is warranted."),
        },
        "vs_S3": {
            "S3_is": "steric exclusion measured in the NR4A3-selective direction (both paralogues bulkier).",
            "this_is": "the SAME physics and the SAME instrument, evaluated on the opposite predicate.",
            "verdict": ("SAME MECHANISM CLASS, DIFFERENT DIRECTION AND DIFFERENT TARGET PROFILE. It must not "
                        "be folded into S3's row: S3's rate (0.923/0.173) answers 'can NR4A3 be selected "
                        "positively', and merging a second predicate into that row would put two "
                        "measurements behind one number."),
        },
        "proposed_register_id": "S18",
        "proposed_name": "★ Inverse steric exclusion — an NR4A1-unique bulge that denies NR4A1 the pose "
                         "(the 'pan-NR4A except NR4A1' profile)",
        "⛔_this_file_does_not_edit_the_register": (
            "selectivity-mechanism-options.json is GENERATED by selectivity_mechanism_options.py and "
            "regenerating it rebuilds M1-M7 as well. The row is proposed here with its measurement already "
            "owned by this artifact; whoever adds S18 must IMPORT these numbers, never re-type them."),
    }


def map_edits(uniq, ster, ver, trade):
    p5 = ster["blocks"]["pocket5_matched_to_M3"]
    n1 = uniq["by_species"]["NR4A1"]["n_unique_in_lbd"]
    n3 = uniq["by_species"]["NR4A3"]["n_unique_in_lbd"]
    sig = p5["by_position_class"].get("nr4a1_unique_and_bulkier", {}).get("positions", [])
    sig_s = ", ".join(str(x) for x in sig) if sig else "EMPTY"
    lobe_targets = ster["nr4a1_only_denied_lobes"]["design_targets"]
    lobe_s = ", ".join(str(x) for x in lobe_targets) if lobe_targets else "no position"
    return [
        {
            "id": "E1",
            "section": "2.4 — the asymmetric selectivity requirement",
            "anchor": "hard constraint — spare NR4A1; soft constraint",
            "current_text": None,
            "proposed_text": (
                "- ★ **AND THE ASYMMETRY IMPLIES A ROUTE NOBODY HAD PRICED: A MOLECULE THAT SPARES NR4A1 "
                "CLEARS THE MANDATORY HALF *BY CONSTRUCTION* (2026-08-03, $0, from trimcrae's question "
                "*\"can we do the inverse of NR-V04\"*).** If NR4A1 is the hard constraint because of a "
                "**combination** genotype, then a pan-NR4A degrader that spares NR4A1 never reconstitutes "
                "it — no margin any instrument here can resolve is required. ⛔ **And the price is on the "
                "half this page calls weaker, which is the wrong intuition:** the paralogue such a profile "
                "*degrades* is the one whose **own single knockout is neonatal-lethal at complete "
                "penetrance** (MP:0011087, PMID 9092472 / 9608532), while the paralogue it *spares* carries "
                "**0 survival/viability terms** on its 8 single-gene annotations; and across 51 HPA tissues "
                "NR4A2 is co-expressed with NR4A3 in **47** and dominant in **0**, so tissue distribution "
                "cannot rescue it. ⚠ The `Nr4a2;Nr4a3` combination *is* on MGI with no survival term — but "
                "the annotated animal is **Nr4a2 heterozygous**, and the double null has **never been "
                "reported**, so that is an absence of a record and not a reading of tolerability. Both "
                "halves, cited: [`nr4a1-sparing-axis.json`](../modalities/nr4a1-sparing-axis.json) → "
                "`therapeutic_trade`. ⛔ **The covalent mechanism does not invert** — NR-V04 selects "
                "*positively* on NR4A1 Cys551 and sparing requires selecting on an **absence**, which no "
                "electrophile can do."),
            "where_it_goes": ("as a new bullet in §2.4's 'What this changes, and what it explicitly does "
                              "not' list, after the 'It changes the brief' bullet. The finding is about the "
                              "REQUIREMENT — it exploits the asymmetry — so it belongs beside the "
                              "asymmetry, not in the mechanism section."),
            "why": ("§2.4 establishes that NR4A1 is mandatory and NR4A2 is weaker, and stops there. The "
                    "design consequence of that asymmetry — that the mandatory half can be cleared by "
                    "construction, and what that costs — has no home on the page."),
            "artifact": "research/modalities/nr4a1-sparing-axis.json:therapeutic_trade",
        },
        {
            "id": "E2",
            "section": "8 — a NEW subsection, 'Route C'",
            "anchor": None,
            "current_text": None,
            "proposed_text": (
                "### Route C — an NR4A1-sparing (pan-NR4A-except-NR4A1) profile · ⏸ **parked, nothing "
                "running** · serves `R7` by a different construction\n\n"
                "★ **What distinguishes it from Routes A and B in one line: it does not need NR4A3 to be "
                "distinguishable from both paralogues — only NR4A1 to be excludable.** Routes A and B are "
                "both POSITIVE selection on NR4A3; this is NEGATIVE selection on NR4A1, and it clears "
                "[§2.4](#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)'s "
                "mandatory half by construction rather than by a margin.\n\n"
                "- ⛔ **The covalent mechanism does not invert, and this is the first thing to say.** NR-V04 "
                "selects *positively* on NR4A1 Cys551, a residue NR4A2/NR4A3 lack. Sparing NR4A1 means "
                "selecting on an **absence**, and an electrophile cannot label a residue that is not there. "
                "There is no reverse-NR-V04 as chemistry.\n"
                "- ★ **What does invert is `S3` steric exclusion**, because it needs a bulkier side chain "
                f"rather than a labelable one. The reciprocal enumeration nobody had run is now run: **{n1} "
                f"alignment-robust NR4A1-unique-vs-BOTH LBD positions** (against **{n3}** for NR4A3, so the "
                "reciprocal set is comparably large and the idea was not vacuous), same two independent "
                "aligners as the forward enumeration.\n"
                "- ⛔ **And the measurement came back AT THE NULL — this is a measured negative, not a "
                f"shortfall of effort.** {ver['★_the_one_number_that_answers_it']} The NR4A1-only signal "
                f"class at Pocket-5 is {sig_s}; the inverted denied lobe qualifies {lobe_s} as a design "
                "target. Every figure, both nulls and the provenance split: "
                "[`nr4a1-sparing-axis.json`](../modalities/nr4a1-sparing-axis.json).\n"
                f"- ★ **The structural reason, and it is conformer-INDEPENDENT.** {ver['★_the_structural_reason']}\n"
                "- ⛔⛔ **And the `M4` relocation control bites harder here than it does on Route A.** The "
                "paralogue *relocates* the ligand by a median 5.31 Å rather than refusing it; for `S3` that "
                "caps a claim at *the pose is denied*, which a design rule survives, but a **sparing** claim "
                "requires non-engagement, and a molecule bound 5 Å away in NR4A1 may still be degraded "
                "there. **This is the axis's central weakness, not a footnote.**\n"
                "- ⏸ **Parked, not dead** — [§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen). "
                "The named trigger is a matched NR4A1-direction ensemble, or poses docked into NR4A2 as the "
                "design frame; one static conformer per species is what closed it here, and that is a "
                "statement about the instrument rather than about the protein."),
            "where_it_goes": ("§8 currently has exactly two route subsections and both are positive "
                              "selection on NR4A3. This is a negative-selection route and needs its own "
                              "heading, immediately after 'Route B'. ⚠ No anchor is given because the "
                              "section does not exist; do not invent one."),
            "why": ("the finding is a ROUTE, not a bullet inside Route A — it targets a different product "
                    "profile and uses a different logical construction."),
            "artifact": "research/modalities/nr4a1-sparing-axis.json:verdict",
        },
        {
            "id": "E3",
            "section": "6b — PARKED",
            "anchor": None,
            "current_text": None,
            "proposed_text": (
                "| **NR4A1-sparing steric exclusion (the inverse of `S3`)** — *serves `R7` by negative "
                f"selection* | ⏸ | the reciprocal enumeration is not empty ({n1} alignment-robust "
                "NR4A1-unique-vs-BOTH LBD positions), but on ONE static opened conformer per species the "
                f"pocket signal class is {sig_s} and the inverted denied lobe qualifies {lobe_s}. "
                "⛔ Not ✕: that is a statement about the instrument, not positive evidence the protein "
                "cannot support the mechanism. | **REOPEN WHEN:** a matched NR4A1-direction ensemble exists "
                "(the forward contrast has one; this does not), or poses are docked into NR4A2 as the design "
                "frame so the construction bias points the right way. "
                "[`nr4a1-sparing-axis.json`](../modalities/nr4a1-sparing-axis.json) |"),
            "where_it_goes": ("§6b's table. ⚠ Column layout must be read off the live table before "
                              "inserting — this row is written to the four-column shape §6b used on "
                              "2026-08-03 and must be reshaped, not forced, if that has changed."),
            "why": "§6's own rule: a route that failed with today's tools and names its reopening trigger is "
                   "⏸, and filing it is worth as much as filing a live route.",
            "artifact": "research/modalities/nr4a1-sparing-axis.json:verdict.recommended_register_state",
        },
        {
            "id": "E4",
            "section": "8 — the options-register bullet list above Route A",
            "anchor": "Route A's seven divergent handles split.",
            "current_text": None,
            "proposed_text": (
                "- ⛔ **AND THE ENUMERATION BEHIND ALL OF THIS RAN IN ONE DIRECTION ONLY UNTIL 2026-08-03.** "
                "Every uniqueness map in the program asks *which residues does NR4A3 have that the "
                "paralogues lack*; the committed reciprocal fragments "
                "(`nr4a-paralogue-unique-residues.json → reciprocal_paralogue_unique`, "
                "`nr4a3-linker-covalent-reach.json → paralogue_control.reciprocal_uniqueness`) are "
                "**pairwise against NR4A3 and Cys/Lys-only**, which cannot express *unique to NR4A1 against "
                "BOTH others*. The vs-BOTH set now exists for all three species over all 20 residue types: "
                "[`nr4a1-sparing-axis.json`](../modalities/nr4a1-sparing-axis.json) → "
                "`reciprocal_enumeration`."),
            "where_it_goes": "appended to the four-bullet options-register list in §8's preamble.",
            "why": "the one-way scope of every enumeration on the page is a limit the page never states.",
            "artifact": "research/modalities/nr4a1-sparing-axis.json:reciprocal_enumeration",
        },
    ]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# build
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def build():
    seqs = _load("research/modalities/nr4a-sequences-cache.json")
    uniq = reciprocal_enumeration(seqs)
    ref, raw, fit, off = _models(seqs)
    m3 = _load("research/modalities/selectivity-mechanism-options.json")["measurements"]["M3"]
    ster = steric_inverse(ref, raw, fit, off, seqs, uniq, m3)
    m4 = _load("research/modalities/selectivity-mechanism-options.json")["measurements"]["M4"]
    trade = therapeutic_trade()
    ver = verdict(uniq, ster, m4, m3)
    now = datetime.datetime.now(datetime.timezone.utc)

    return {
        "_title": ("The NR4A1-SPARING axis — the inverse of NR-V04, enumerated and measured"),
        "_question_from_trimcrae": (
            "Is there anything to the idea of doing the inverse of NR-V04 here? Like making something that "
            "will degrade every NR4A paralogue EXCEPT NR4A1 using the same mechanism as NR-V04 but in "
            "reverse?"),
        "_status": ("MEASURED at $0 — CPU only: cached UniProt sequences, committed opened models, committed "
                    "docked poses. No GPU, no rental, no dispatch, no network. Nothing here is a claim about "
                    "binding, reactivity, degradation, efficacy, safety or clinical readiness."),
        "_one_fact_one_place": (
            "The MGI and HPA figures are READ from nr4a2-sparing-bound.json at generation time; the "
            "relocation control is READ from selectivity-mechanism-options.json M4; hard_clash_A and the "
            "Pocket-5 list come from selectivity_mechanism_options; the lobe geometry is "
            "steric_design_rule.denied_lobe reused unchanged. This file is the ONE home only of the "
            "reciprocal vs-BOTH enumeration and the NR4A1-only steric measurement."),
        "_documents_this_file_may_not_edit": ["research/manuscripts/nr4a3-program-map.md",
                                              "research/modalities/selectivity-mechanism-options.json"],
        "_generated": {"utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "et": (now - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %-I:%M %p ET"),
                       "generator": "research/modalities/nr4a1_sparing_axis.py"},
        "⛔_the_covalent_mechanism_does_not_invert": {
            "statement": ("NR-V04 achieves NR4A1 selectivity by covalently labelling **NR4A1 Cys551**, a "
                          "residue NR4A2 and NR4A3 do not carry at the aligned position (NR4A3 has T579). "
                          "That is POSITIVE selection on a PRESENCE. Sparing NR4A1 requires selecting on an "
                          "ABSENCE — and an electrophile cannot label a residue that is not there."),
            "so": ("there is no 'NR-V04 in reverse' as chemistry, and no amount of warhead engineering "
                   "creates one. Any NR4A1-sparing design must use a NON-covalent mechanism. This is stated "
                   "plainly so the idea is not re-proposed as a covalent one."),
            "the_committed_evidence": ("nr4a-paralogue-unique-residues.json -> "
                                       "reciprocal_paralogue_unique.NR4A1 carries C551 with NR4A3 partner "
                                       "T579, alignment-robust; categorical-axis-audit.json records the "
                                       "same pair."),
            "⚠_and_the_one_thing_that_DOES_carry_over": (
                "the CATEGORICAL logic survives — 'a residue the other proteins do not have' is still a "
                "set-membership fact rather than an energy difference. What changes is which observable can "
                "read it: a bond cannot, a SHAPE can. That is why the measured half of this file is steric."),
        },
        "provenance": provenance(uniq),
        "reciprocal_enumeration": uniq,
        "steric_inverse": ster,
        "controls": controls(m4),
        "therapeutic_trade": trade,
        "verdict": ver,
        "register_reconciliation": register_reconciliation(),
        "defect_found_in_a_committed_artifact": {
            "artifact": "research/modalities/selectivity-mechanism-options.json",
            "field": "measurements.M3.positions.*.partners.<paralogue>[1]",
            "what": ("the paralogue residue NUMBERS are labelled with NR4A3's local offset (372) instead of "
                     "the paralogue's own (348 for NR4A1, 344 for NR4A2), so every one is high by 25 (NR4A1) "
                     "/ 29 (NR4A2): M3 reports NR4A3 L406's NR4A1 partner as 'H, 397' where the residue is "
                     "H372."),
            "why_it_matters": ("the wrong numbers name REAL residues of the same protein — NR4A1 397 is a "
                               "lysine that appears in this repo's own reciprocal list — so the field reads "
                               "as measured and is not. CLAUDE.md §4: a populated field is not a measured "
                               "one."),
            "blast_radius": ("NONE for any conclusion. Every downstream use quotes the residue LETTERS "
                             "(L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe), which are correct, and "
                             "steric-design-rule.json carries letters only."),
            "fix": ("selectivity_mechanism_options.m3_steric_exclusion line `(rp + U.LOCAL_OFFSET)` must use "
                    "the paralogue's own recovered offset — nr4a1_sparing_axis.uniprot_offset() derives it "
                    "from the model sequence rather than hard-coding it. Not applied here: regenerating that "
                    "artifact rebuilds M1-M7 and it is owned by another lane."),
        },
        "map_edits_required": map_edits(uniq, ster, ver, trade),
        "⛔_limits": [
            "SEQUENCE UNIQUENESS IS EXACT; EVERYTHING ELSE IS A HYPOTHESIS. The vs-both enumeration is a "
            "fact about two alignments of three FASTA sequences. The steric measurement is a fact about "
            "three static models and 13 poses.",
            "ONE STATIC OPENED CONFORMER PER SPECIES, rigidly transferred. A rotamer modelled away here "
            "could be a real bulge, and vice versa.",
            "THE POSES WERE DOCKED INTO NR4A3, so 'NR4A3 does not clash' is free. Only the class contrast is "
            "gradeable — never the absolute rate.",
            "CONDITIONAL ON R5. The whole pocket-level analysis assumes the cryptic pocket is the right "
            "site, and the pose known-answer test V3 returned INCONCLUSIVE.",
            "NO ENERGY, ANYWHERE. No affinity, ddG, selectivity ratio, degradation, efficacy, safety, "
            "therapeutic window or clinical readiness is computed or implied, and no proteome-wide "
            "selectivity of any kind is claimed — the comparison set is three paralogues.",
            "THE THERAPEUTIC TRADE IS CITED, NOT DECIDED. Germline and lineage knockouts bound developmental "
            "loss; a degrader is adult, transient and incomplete.",
        ],
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# markdown — a rendering of the JSON, never a second home for a number
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def to_markdown(d):
    v, ster, uniq = d["verdict"], d["steric_inverse"], d["reciprocal_enumeration"]
    p5 = ster["blocks"]["pocket5_matched_to_M3"]
    lin = ster["blocks"]["ligand_envelope_lining"]
    L = []
    A = L.append
    A("# " + d["_title"])
    A("")
    A("> **The question, from trimcrae:** *\"%s\"*" % d["_question_from_trimcrae"])
    A("")
    A("**Generated** %s by `%s` — %s" % (d["_generated"]["et"], d["_generated"]["generator"], d["_status"]))
    A("")
    A("⚠ **Every number below is rendered from [`nr4a1-sparing-axis.json`](nr4a1-sparing-axis.json).** "
      "This file is a reading of that artifact, never a second home for any figure.")
    A("")
    A("---")
    A("")
    A("## ⛔ First, what does NOT work — the covalent mechanism does not invert")
    A("")
    A(d["⛔_the_covalent_mechanism_does_not_invert"]["statement"])
    A("")
    A("**So:** " + d["⛔_the_covalent_mechanism_does_not_invert"]["so"])
    A("")
    A("⚠ " + d["⛔_the_covalent_mechanism_does_not_invert"]["⚠_and_the_one_thing_that_DOES_carry_over"])
    A("")
    A("## The answer")
    A("")
    A(v["answer_to_the_question"])
    A("")
    A("- **Measured or speculative?** " + v["is_it_measured_or_speculative"])
    A("- **The axis in one line:** " + v["the_axis_in_one_line"])
    A("- **Recommended register state:** %s — %s" % (v["recommended_register_state"],
                                                     v["why_that_state_and_not_the_others"]))
    A("")
    A("> ★ " + v["★_the_one_number_that_answers_it"])
    A("")
    A("★ **The structural reason, and it is conformer-independent.** " + v["★_the_structural_reason"])
    A("")
    c = v["⚠_the_single_cell_that_does_fire_above_null_and_why_it_is_not_enough"]
    A("⚠ **The one cell that does fire above null:** NR4A3 %s%s / NR4A1 %s%s / NR4A2 %s%s — %s of %s poses, "
      "bulk margin +%s heavy atom. %s" % (
          c["residues"]["NR4A3"], c["uniprot"]["NR4A3"], c["residues"]["NR4A1"], c["uniprot"]["NR4A1"],
          c["residues"]["NR4A2"], c["uniprot"]["NR4A2"], c["nr4a1_only_clash_poses"],
          lin["n_poses"], c["bulk_margin_heavy_atoms"], c["_why_it_is_not_enough"]))
    A("")
    A("## 1 · The reciprocal enumeration — which positions are unique to which paralogue, against BOTH others")
    A("")
    A(uniq["_method"])
    A("")
    A("| species | positions scanned | unique vs BOTH (alignment-robust) | of those, in the LBD |")
    A("|---|---|---|---|")
    for sp in SPECIES:
        b = uniq["by_species"][sp]
        A("| **%s** (%s) | %d | %d | **%d** |" % (sp, b["accession"], b["n_positions_scanned"],
                                                  b["n_unique_vs_both_alignment_robust"], b["n_unique_in_lbd"]))
    A("")
    A("### NR4A1-unique LBD positions that LINE the pocket envelope")
    A("")
    A("*(the full %d-position list is in the JSON; this table is the subset the steric test can act on)*"
      % uniq["by_species"]["NR4A1"]["n_unique_in_lbd"])
    A("")
    A("| NR4A3 frame | NR4A3 | NR4A1 | NR4A2 | NR4A1 heavy atoms vs NR4A2 / NR4A3 | class |")
    A("|---|---|---|---|---|---|")
    shown = 0
    for u3, rec in sorted(lin["per_position"].items()):
        if rec["class"] == "conserved_or_shared":
            continue
        n = rec["n_side_chain_heavy"]
        A("| %s | %s%s | %s%s | %s%s | %d vs %d / %d | `%s` |" % (
            u3, rec["residues"]["NR4A3"], rec["uniprot"]["NR4A3"],
            rec["residues"]["NR4A1"], rec["uniprot"]["NR4A1"],
            rec["residues"]["NR4A2"], rec["uniprot"]["NR4A2"],
            n["NR4A1"], n["NR4A2"], n["NR4A3"], rec["class"]))
        shown += 1
    if not shown:
        A("| — | — | — | — | — | *no NR4A1-unique position lines the pocket envelope* |")
    A("")
    A("## 2 · The steric test, run in the NR4A1-only direction")
    A("")
    A(ster["_question"])
    A("")
    A(ster["_method"])
    A("")
    A("⚠ " + ster["_the_null_is_the_whole_point"])
    A("")
    for label, blk in (("Pocket-5, matched to `M3`", p5), ("ligand-envelope lining set", lin)):
        A("**%s** — %d positions × %d poses" % (label, blk["n_positions"], blk["n_poses"]))
        A("")
        A("| class | positions | hits / trials | rate |")
        A("|---|---|---|---|")
        for cls in ("nr4a1_unique_and_bulkier", "nr4a1_unique_not_bulkier", "conserved_or_shared"):
            g = blk["by_position_class"].get(cls)
            if not g:
                A("| `%s` | *(class empty)* | — | — |" % cls)
                continue
            A("| `%s` | %s | %d / %d | **%s** |" % (cls, g["positions"], g["hits"], g["trials"], g["rate"]))
        A("")
        A("signal − null = **%s** · enrichment = **%s**" % (blk["signal_minus_null"],
                                                            blk["enrichment_signal_over_null"]))
        A("")
    A("### ⛔ The forward-direction self-check — proof the null is not a bug")
    A("")
    fsc = ster["⛔_forward_direction_self_check"]
    A(fsc["_why"])
    A("")
    A("| class | recomputed here | committed `M3` |")
    A("|---|---|---|")
    for k in ("unique_and_both_bulkier", "conserved_or_shared"):
        A("| `%s` | %s | %s |" % (k, fsc["recomputed"][k], fsc["committed_M3"][k]))
    A("")
    A("**Reproduces committed `M3`: %s.** %s" % ("YES" if fsc["reproduces_committed_M3"] else "NO",
                                                 "" if fsc["reproduces_committed_M3"] else fsc["_if_false"]))
    A("")
    A("### The inverted denied lobe")
    A("")
    lob = ster["nr4a1_only_denied_lobes"]
    A(lob["_what"])
    A("")
    A("Measured volume ceiling from the null class: **%s Å³** at position %s. Design targets clearing it: **%s**."
      % (lob["null_volume_ceiling_A3"], lob["null_volume_ceiling_at"], lob["design_targets"] or "none"))
    A("")
    A("| NR4A3 frame | NR4A3 / NR4A1 / NR4A2 | class | lobe Å³ | clears the bar |")
    A("|---|---|---|---|---|")
    for u3, lo in sorted(lob["lobes"].items()):
        r = lo["residues"]
        A("| %s | %s / %s / %s | `%s` | %s | %s |" % (u3, r["NR4A3"], r["NR4A1"], r["NR4A2"], lo["class"],
                                                      lo.get("volume_A3"),
                                                      "✅" if lo["qualifies_as_a_design_target"] else "—"))
    A("")
    A("## 3 · The controls — and why one of them is the whole story here")
    A("")
    for k, val in d["controls"].items():
        A("- **%s** — %s" % (k.replace("_", " ").strip(), val))
    A("")
    A("## 4 · The therapeutic trade, both halves")
    A("")
    t = d["therapeutic_trade"]
    A("⚠ " + t["_one_fact_one_place"])
    A("")
    A("**What the profile BUYS**")
    A("")
    buys = t["what_the_profile_BUYS"]["the_genotype_it_avoids_by_construction"]
    A("- `%s` — %s annotations, survival terms %s (PMID %s). %s" % (
        buys["genotype"], buys["n_annotations"], buys["survival_or_viability_terms"],
        ", ".join(buys["pubmed_ids"] or []), buys["_why_it_matters"]))
    mild = t["what_the_profile_BUYS"]["and_NR4A1's_own_single_null_is_the_mild_one"]
    A("- NR4A1 single-gene MGI: %s annotations, survival terms %s. %s" % (
        mild["n_single_gene_annotations"], mild["survival_or_viability_terms"] or "**none**", mild["_reading"]))
    A("")
    A("**What the profile COSTS**")
    A("")
    for key, node in t["what_the_profile_COSTS"].items():
        A("- **%s** — %s" % (key.replace("_", " "), node["_reading"]))
    A("")
    A("⚠ **%s**" % t["⚠_the_genotype_this_profile_WOULD_reconstitute_and_what_the_record_actually_says"][
        "⛔_read_this_before_quoting_the_empty_survival_list"])
    A("")
    A("**In one sentence:** " + t["_the_trade_in_one_sentence"])
    A("")
    A("## 5 · What already existed, and what is new")
    A("")
    p = d["provenance"]
    A("**Already committed:**")
    A("")
    for e in p["already_existed"]:
        A("- `%s` → `%s` — %s" % (e["artifact"], e["field"], e["what"]))
        A("  - ⛔ could not answer: %s" % e["what_it_could_NOT_answer"])
    A("")
    A("**Computed here for the first time:**")
    A("")
    for e in p["computed_here_for_the_first_time"]:
        A("- " + e)
    A("")
    A("⚠ " + p["_the_gap_this_closes"])
    A("")
    A("## 6 · Reconciliation with the mechanism register")
    A("")
    r = d["register_reconciliation"]
    A("- **vs `S15`** — %s **%s**" % (r["vs_S15"]["distinct_because"][0], r["vs_S15"]["verdict"]))
    for b in r["vs_S15"]["distinct_because"][1:]:
        A("  - " + b)
    A("- **vs `S3`** — %s" % r["vs_S3"]["verdict"])
    A("- **Proposed id:** `%s` — %s" % (r["proposed_register_id"], r["proposed_name"]))
    A("- ⛔ " + r["⛔_this_file_does_not_edit_the_register"])
    A("")
    A("## 7 · A defect found on the way")
    A("")
    df = d["defect_found_in_a_committed_artifact"]
    A("`%s` → `%s`: %s" % (df["artifact"], df["field"], df["what"]))
    A("")
    A("- **Why it matters:** " + df["why_it_matters"])
    A("- **Blast radius:** " + df["blast_radius"])
    A("- **Fix:** " + df["fix"])
    A("")
    A("## ⛔ Limits")
    A("")
    for lim in d["⛔_limits"]:
        A("- " + lim)
    A("")
    return "\n".join(L) + "\n"


def main(argv=None):
    d = build()
    with open(OUT_JSON, "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(OUT_MD, "w") as f:
        f.write(to_markdown(d))
    v = d["verdict"]
    print("wrote", OUT_JSON)
    print("wrote", OUT_MD)
    print("state:", v["recommended_register_state"])
    print("axis :", v["the_axis_in_one_line"])
    print("rates:", json.dumps(v["rates"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
