#!/usr/bin/env python3
"""Human-readable summary of `nr4a-paralogue-dynamics.json` — the tables the verdict is read from.

A 20 MB JSON is not a result anyone can check. This prints the three things that decide the lane, in the form
they belong in the manuscript: the per-species cysteine reach distributions, the matched-construct collision
probability at each linker length, and the E2~Ub transfer-zone lysine comparison. Pure stdlib, no side effects.
"""
from __future__ import annotations

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "nr4a-paralogue-dynamics.json")


def fmt_q(q, k="median"):
    if not q:
        return "  -  "
    return f"{q.get(k):.3f}" if isinstance(q.get(k), (int, float)) else "  -  "


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default=DEFAULT)
    a = ap.parse_args(argv)
    d = json.load(open(a.json))

    print("=" * 108)
    print("LANE 13 — does the CATEGORICAL case survive paralogue dynamics?")
    print("=" * 108)

    cv = d.get("coverage_validation")
    if cv:
        print(f"\n[check] analytic transfer-zone coverage vs the committed Monte-Carlo sampler: "
              f"max |diff| {cv['max_abs_diff']}  ({'PASS' if cv['passes'] else 'FAIL'})")

    print("\n--- A1  E3-INDEPENDENT REACH ENVELOPE (each species in its own frame, its own homologous pocket)")
    print("     'gate' = fraction of conformers in which the cysteine is reachable at <= 12 linker atoms\n")
    ta = (d.get("term_a") or {}).get("by_species") or {}
    hdr = f"{'species':7s} {'ensemble':22s} {'Cys':7s} {'aligned':9s} {'shared?':8s} " \
          f"{'RSA med':8s} {'gate':6s} {'95% CI':16s} {'Lmin med':9s} {'n':4s}"
    print(hdr)
    print("-" * len(hdr))
    for sp in ("NR4A3", "NR4A1", "NR4A2"):
        blk = ta.get(sp) or {}
        for ens_name in ("static_opened_model", "pooled_unbiased", "metad"):
            summ = None
            if ens_name == "pooled_unbiased":
                summ = ((blk.get("pooled_unbiased") or {}).get("summary"))
                n_lab = f"pooled_unbiased({(blk.get('pooled_unbiased') or {}).get('n_frames', 0)})"
            else:
                e = (blk.get("ensembles") or {}).get(ens_name)
                if e:
                    summ = e["summary"]
                    n_lab = f"{ens_name}({e['n_frames']}){'*biased' if e.get('biased') else ''}"
            if not summ:
                continue
            for lab, v in sorted(summ.items()):
                ci = v.get("frac_frames_open_at_or_below_gate_wilson95")
                gate_frac = v.get("frac_frames_open_at_or_below_gate")
                gate_txt = f"{gate_frac:.3f}" if gate_frac is not None else "  -  "
                shared = "shared" if v.get("nr4a3_has_cys_here") else "NR4A3-lacks"
                print(f"{sp:7s} {n_lab:22s} {lab:7s} {str(v.get('nr4a3_aligned')):9s} {shared:8s} "
                      f"{fmt_q(v.get('rsa')):8s} {gate_txt:6s} {str(ci):16s} "
                      f"{fmt_q(v.get('shortest_linker_atoms')):9s} {v.get('n_frames', 0):4d}")
            print()

    print("\n--- A2  MATCHED-CONSTRUCT COLLISION (same placement, same anchors, same length budget)")
    vd = d.get("categorical_verdict") or {}
    for scope, row in (vd.get("by_scope") or {}).items():
        print(f"\n  scope = {scope}   frames {row.get('n_frames')}   placements {row.get('n_placements')}")
        if row.get("VERDICT_NOT_EVALUABLE"):
            print(f"    !! NOT EVALUABLE: {row['VERDICT_NOT_EVALUABLE']}")
            continue
        print(f"    {'L':>3s}  {'P(NR4A3 uniq)':>14s}  {'P(collide|NR4A3)':>17s}  "
              f"{'P(collide|NR4A3) exp':>21s}  {'P(anyCys) A3/A1/A2':>26s}")
        for n, c in sorted((row.get("by_linker_atoms") or {}).items(), key=lambda kv: int(kv[0])):
            trio = "/".join(f"{c.get(f'mean_P_any_cysteine_{s}', 0):.4f}" for s in ("NR4A3", "NR4A1", "NR4A2"))
            print(f"    {n:>3}  {c.get('mean_P_nr4a3_unique', 0):>14.6f}  "
                  f"{str(c.get('P_paralogue_also_labelled_given_nr4a3')):>17s}  "
                  f"{str(c.get('P_paralogue_also_labelled_given_nr4a3_EXPOSED')):>21s}  {trio:>26s}")

    print("\n\n--- B  E2~Ub TRANSFER-ZONE LYSINE COVERAGE (one matched placement set)")
    tb = (d.get("term_b") or {})
    print(f"    transfer geometry: {tb.get('transfer_geometry')}")
    print(f"    placements: {(tb.get('placements') or {}).get('n_total')}\n")
    print(f"    {'species':7s} {'ensemble':24s} {'P(any lys)':>12s} {'P(any exposed)':>15s} "
          f"{'core RMSD':>10s} {'pocket offset':>14s}")
    for sp in ("NR4A3", "NR4A1", "NR4A2"):
        blk = (tb.get("by_species") or {}).get(sp) or {}
        for ens_name, e in (blk.get("ensembles") or {}).items():
            print(f"    {sp:7s} {ens_name + ('*' if e.get('biased') else ''):24s} "
                  f"{fmt_q(e.get('P_zone_covers_any_lysine')):>12s} "
                  f"{fmt_q(e.get('P_zone_covers_any_EXPOSED_lysine')):>15s} "
                  f"{fmt_q(e.get('superposition_core_rmsd_A')):>10s} "
                  f"{fmt_q(e.get('homologous_pocket_centroid_offset_A')):>14s}")
        p = blk.get("pooled_unbiased")
        if p:
            print(f"    {sp:7s} {'POOLED UNBIASED':24s} "
                  f"{fmt_q(p.get('P_zone_covers_any_lysine')):>12s} "
                  f"{fmt_q(p.get('P_zone_covers_any_EXPOSED_lysine')):>15s}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
