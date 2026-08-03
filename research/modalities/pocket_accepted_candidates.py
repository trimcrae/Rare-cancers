#!/usr/bin/env python3
"""EVERY cavity that clears the frozen gate, per frame — not just the one the tie-break picked.

★★ WHY (2026-08-03, trimcrae: *"Why are we using that frame when we have tons of MD saying we can open a
cryptic pocket in NR4A3?"*).

The `R3` Gate-A audit found the generation receptor's mapped orthosteric site at druggability **0.259**,
below D* = 0.53 — and found that **two** of its 15 cavities clear the composite acceptance gate. The
better-matching one (pocket 1, 8/10 reference residues recovered) scores 0.259; the more druggable one
(pocket 2, 6/10) scores **0.667**. `pocket_tracking.match_pocket` orders accepted candidates by
frac_recovered → Jaccard → centroid → druggability, so pocket 1 wins and the frame FAILS.

That makes the verdict a **rule** question, and a rule question cannot be answered one frame at a time:
whichever cavity is "the site" in the generation frame, the SAME ordering decides it in all 300 committed
paralogue-ensemble frames, and therefore decides every detection fraction the selectivity premise rests
on. But the committed artifacts record only the WINNER per frame
(`paralogue-pocket-contrast.json → per_frame.pocket_number`), so the question could not be asked of them
at all — it needed another fpocket pass every time.

⛔ THIS MODULE DOES NOT CHOOSE, RANK, RE-TUNE OR PROPOSE A RULE, AND MUST NEVER BE MADE TO.
`pocket_tracking`'s thresholds were frozen 2026-07-11 and re-tuning them after seeing a verdict is the
outcome-selection defect the whole harmonized rerun exists to remove — doing it in a *helper* rather than
in the matcher would be the same defect with better manners. What this does is record, for every frame,
the FULL set of cavities the frozen gate accepted, with each one's gate arithmetic and druggability. Any
ordering question — the frozen one, or an alternative someone wants costed — is then arithmetic on a
committed artifact instead of a new fpocket run whose thresholds could drift.

Reuses `paralogue_pocket_contrast`'s frame walk, fpocket call and reference construction verbatim
(CLAUDE.md rule 1: one home). Only the recording differs: `match_pocket` returns the winner, this keeps
the accepted list.

Usage
    python pocket_accepted_candidates.py                    # all species/subsets (needs fpocket)
    python pocket_accepted_candidates.py --species NR4A3    # NR4A3 only
    python pocket_accepted_candidates.py --limit 2          # smoke: 2 frames per subset
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import paralogue_pocket_contrast as PPC   # noqa: E402  — the frame walk + fpocket + reference, one home
import pocket_tracking as pt              # noqa: E402  — THE detector; predicates used, never redefined

OUT = os.path.join(HERE, "pocket-accepted-candidates.json")


# ---------------------------------------------------------------------------------------------------------
# pure
# ---------------------------------------------------------------------------------------------------------
def frozen_winner(accepted):
    """The pocket the FROZEN rule selects among already-accepted candidates. PURE.

    ⚠ This is a RE-STATEMENT of `pocket_tracking.match_pocket`'s ordering for records that already carry
    their metrics, so a reader can verify the artifact against the committed per-frame winners without
    re-running fpocket. It is not an alternative rule and it is pinned by a test that requires it to agree
    with `match_pocket` on the same input. If they ever disagree, `match_pocket` is right and this is the
    bug."""
    if not accepted:
        return None
    return sorted(accepted, key=lambda r: (
        r["frac_recovered"], r["jaccard"],
        -(r["centroid_dist_ang"] if r["centroid_dist_ang"] is not None else 1e9),
        (r["druggability"] or 0.0),
    ), reverse=True)[0]


def most_druggable(accepted):
    """The most druggable ACCEPTED cavity. PURE, and reported for one reason only: it is what the frozen
    rule declines to pick, so the gap between the two is the size of the rule's consequence. ⛔ It is NOT
    a rule, and an artifact reader must never quote it as the site."""
    if not accepted:
        return None
    return sorted(accepted, key=lambda r: ((r["druggability"] or 0.0),
                                           r["frac_recovered"], r["jaccard"]), reverse=True)[0]


def summarise(frames, d_star=pt.D_STAR):
    """Per-ensemble counts under the FROZEN rule, plus the counts an ordering-by-druggability would give.
    PURE. Both are reported side by side because a rule's consequence is exactly the difference, and a
    consequence quoted alone is how a sensitivity becomes a recommendation."""
    out = {}
    for f in frames:
        key = (f["species"], f["ensemble"])
        row = out.setdefault(key, {"species": f["species"], "ensemble": f["ensemble"],
                                   "n_frames": 0, "n_matched": 0,
                                   "n_multi_accept": 0, "max_accepted": 0,
                                   "n_ge_dstar_frozen": 0, "n_ge_dstar_if_most_druggable": 0,
                                   "n_frames_where_the_two_rules_differ": 0})
        row["n_frames"] += 1
        acc = f["accepted"]
        row["max_accepted"] = max(row["max_accepted"], len(acc))
        if not acc:
            continue
        row["n_matched"] += 1
        if len(acc) > 1:
            row["n_multi_accept"] += 1
        fw, md = frozen_winner(acc), most_druggable(acc)
        if (fw["druggability"] or 0.0) >= d_star:
            row["n_ge_dstar_frozen"] += 1
        if (md["druggability"] or 0.0) >= d_star:
            row["n_ge_dstar_if_most_druggable"] += 1
        if fw["pocket"] != md["pocket"]:
            row["n_frames_where_the_two_rules_differ"] += 1
    return [out[k] for k in sorted(out)]


# ---------------------------------------------------------------------------------------------------------
# impure
# ---------------------------------------------------------------------------------------------------------
def accepted_for_frame(frame_pdb, species, seqs, ref, ref_pocket_local, workroot):
    """Every candidate cavity that clears the FROZEN composite gate, with its arithmetic. Raises on a
    frame it cannot read, so a refusal stays distinguishable from 'no cavity' (CLAUDE.md §4)."""
    model = PPC.B.load_paralogue(frame_pdb)
    offset, pocket_local, missing = PPC.PD.construct_frame(model, species, seqs, ref, ref_pocket_local)
    if not pocket_local:
        raise ValueError("homologous pocket mapped to 0 residues")
    ca = PPC.ca_by_resseq(frame_pdb)
    span = (min(pocket_local), max(pocket_local))
    reference = pt.orthosteric_reference(ca, lining_residues=sorted(pocket_local), span=span)
    cands = PPC.fpocket_candidates(frame_pdb, workroot)
    mp = pt.match_params()
    accepted = []
    for c in cands:
        m = pt.match_metrics(c["residues"], reference["lining_residues"])
        cen = pt.pocket_centroid(c["residues"], ca)
        cdist = None if cen is None else round(
            sum((a - b) ** 2 for a, b in zip(cen, reference["centroid"])) ** 0.5, 3)
        if pt.accept_candidate(m, cdist, mp["jaccard_min"], mp["frac_recovered_min"],
                               mp["centroid_max_ang"]):
            accepted.append({"pocket": c["pocket_number"], "druggability": c["druggability"],
                             "n_overlap": m["n_overlap"], "jaccard": round(m["jaccard"], 4),
                             "frac_recovered": round(m["frac_recovered"], 4),
                             "centroid_dist_ang": cdist,
                             "n_lining_residues": len(c["residues"])})
    accepted.sort(key=lambda r: -(r["druggability"] or 0.0))
    return accepted, {"n_candidates": len(cands), "n_lining_mapped": len(pocket_local),
                      "n_lining_unmapped": len(missing), "local_to_uniprot_offset": offset}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species", default=",".join(PPC.SPECIES))
    ap.add_argument("--limit", type=int, default=0, help="frames per subset (0 = all); smoke only")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    if not shutil.which("fpocket"):
        sys.exit("  ABORT: fpocket not on PATH — this artifact must never be synthesised from a summary")
    if pt.match_mode() != pt.HARMONIZED:
        sys.exit("  ABORT: POCKET_MATCH must be 'harmonized' (pocket_tracking.match_mode defaults LEGACY)")

    species = [s.strip().upper() for s in args.species.split(",") if s.strip()]
    ctx = reference_context()
    t0 = time.time()
    work = tempfile.mkdtemp(prefix="pac_")
    frames, refusals = [], []
    try:
        for sp in species:
            for sub in PPC.SUBSETS:
                paths = PPC.frame_paths(sp, sub)
                if args.limit:
                    paths = paths[:args.limit]
                for p in paths:
                    tag = f"{sp}/{sub}/{os.path.basename(os.path.dirname(p))}"
                    try:
                        acc, diag = accepted_for_frame(p, sp, *ctx, work)
                    except Exception as e:                                   # noqa: BLE001
                        refusals.append({"frame": tag, "reason": f"{type(e).__name__}: {e}"})
                        continue
                    frames.append({"frame": tag, "species": sp, "ensemble": sub,
                                   "accepted": acc, **diag})
                print(f"  {sp}/{sub}: {len(paths)} frames", flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    rec = {
        "_what": ("every cavity clearing the FROZEN harmonized acceptance gate, per committed ensemble "
                  "frame — so an ordering question is arithmetic on this file rather than a new fpocket "
                  "run whose thresholds could drift"),
        "_does_not_license": [
            "any change to pocket_tracking's thresholds or ordering — frozen 2026-07-11",
            "quoting `most_druggable` as 'the site'; the site is `frozen_winner`",
            "any statement about binding, affinity, degradation, efficacy or safety",
        ],
        "d_star": pt.D_STAR,
        "match_mode": pt.match_mode(),
        "match_params": pt.match_params(),
        "fpocket_version": pt.resolved_fpocket_version(),
        "n_frames": len(frames),
        "n_refusals": len(refusals),
        "refusals": refusals,
        "summary": summarise(frames),
        "per_frame": frames,
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(rec, fh, indent=2)
    for r in rec["summary"]:
        print(f"  {r['species']}/{r['ensemble']}: {r['n_matched']}/{r['n_frames']} matched, "
              f"{r['n_multi_accept']} multi-accept, >=D* frozen {r['n_ge_dstar_frozen']} vs "
              f"most-druggable {r['n_ge_dstar_if_most_druggable']} "
              f"({r['n_frames_where_the_two_rules_differ']} frames differ)", flush=True)
    print(f"[accepted-candidates] wrote {args.out} ({len(frames)} frames, {len(refusals)} refusals)")
    return 0


def reference_context():
    """(seqs, ref_model, ref_pocket_local) — byte-for-byte the three objects
    `paralogue_pocket_contrast.main()` builds before its frame loop, from the same three files.

    ⚠ Restated here rather than imported because that block lives INSIDE its `main()` and is not callable.
    `tests/test_pocket_accepted_candidates.py` pins the three source paths against that module's own
    constants, so a change there fails here loudly instead of silently defining a different site."""
    seqs = json.load(open(PPC.PD.SEQ_CACHE))
    ref = PPC.B.load_paralogue(PPC.PD.STATIC_MODEL["NR4A3"])
    u = json.load(open(PPC.PD.UNIQUE_JSON))
    ref_pocket_local = [x - PPC.B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]
    return (seqs, ref, ref_pocket_local)


if __name__ == "__main__":
    raise SystemExit(main())
