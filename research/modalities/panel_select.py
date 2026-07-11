#!/usr/bin/env python3
"""
Resolve the FROZEN conformer-panel selection RULES (nr4a3-conformer-panel.json) to concrete frame lists,
deterministically, from the harmonized per-frame druggability.

The panel manifest freezes the panel as *rules* (top-N druggable release frames = design, the druggable
8XTT NMR models = validation, occluded/AF2/metad = stress, ...), NOT hand-picked indices — so it can't be
gamed by shuffling a failed conformer into the design set, and it reproduces from whatever per-frame
druggability the harmonized tracker produced. This module is that resolver: pure logic over frame records,
so the panel-docking pipeline (and its tests) can select frames without any structure/docking/S3 stack.

A frame record = {"ensemble", "frame_id", "druggability"(float), "detected"(bool)}. `resolve_panel` returns
{design, validation, stress, nr4a1_antitarget, nr4a2_antitarget} each = ordered list of frame records, plus
a `_provenance` describing the rule applied and the counts (so a run logs exactly what it selected).

Dependency-free; unit-tested in tests/test_panel_select.py.
"""

D_STAR = 0.53
AF2_ENSEMBLES = ("af2_static", "af2_opened", "af2")   # the circular denovo_401 design frame(s)


def _druggable(rec, d_star=D_STAR):
    return bool(rec.get("detected", True)) and rec.get("druggability") is not None \
        and float(rec["druggability"]) >= d_star


def _by_drug_desc(recs):
    """Stable sort by druggability descending, then frame_id ascending (deterministic ties)."""
    return sorted(recs, key=lambda r: (-(float(r.get("druggability") or -1.0)), str(r.get("frame_id"))))


def _from(frames, *ensembles):
    ens = set(ensembles)
    return [r for r in frames if r.get("ensemble") in ens]


def resolve_panel(frames, d_star=D_STAR, n_design=3, n_validation_release=3):
    """Resolve the NR4A3 design/validation/stress + matched anti-target panels from `frames`.

    frames: list of per-frame druggability records across all ensembles (release_rep*, 8xtt*, *metad, af2*).
      Recognised ensembles: 'release_rep0/1/2' or 'release*' (unbiased release); '8xtt*' (the 20-model NMR
      ensemble); 'nr4a3_metad'/'metad*'; 'nr4a1_metad'; 'nr4a2_metad'; an AF2 ensemble (see AF2_ENSEMBLES).
    Returns {design, validation, stress, nr4a1_antitarget, nr4a2_antitarget, _provenance}. Pure.

    Rules (mirror nr4a3-conformer-panel.json):
      design      = top-`n_design` druggable UNBIASED-RELEASE frames (>= d_star), EXCLUDING any AF2 frame.
      validation  = ALL druggable 8XTT frames (>= d_star) + the next druggable release frames not in design
                    (up to `n_validation_release`).  (held out — never seen by generation/early scoring)
      stress      = 8XTT frames that are detected-but-below-d_star OR not detected (occluded) + every AF2
                    frame + the single most-druggable NR4A3-metad frame (promiscuous discriminator).
      nr4a1/2 anti-target = every nr4a1_metad / nr4a2_metad frame provided (matched opened paralogue states).
    """
    release = _from(frames, "release_rep0", "release_rep1", "release_rep2") \
        or [r for r in frames if str(r.get("ensemble", "")).startswith("release")]
    xtt = [r for r in frames if str(r.get("ensemble", "")).startswith("8xtt")]
    af2 = [r for r in frames if r.get("ensemble") in AF2_ENSEMBLES]
    nr3_metad = _from(frames, "nr4a3_metad") or [r for r in frames if r.get("ensemble") == "metad_frames"] \
        or [r for r in frames if str(r.get("ensemble", "")) in ("metad", "metad_frames")]
    nr1_metad = _from(frames, "nr4a1_metad")
    nr2_metad = _from(frames, "nr4a2_metad")

    # design: top-N druggable release frames, no AF2
    release_drug = _by_drug_desc([r for r in release if _druggable(r, d_star)])
    design = release_drug[:n_design]
    design_ids = {(r["ensemble"], r["frame_id"]) for r in design}

    # validation: druggable 8XTT + next druggable release (not already design)
    xtt_drug = _by_drug_desc([r for r in xtt if _druggable(r, d_star)])
    release_val = [r for r in release_drug if (r["ensemble"], r["frame_id"]) not in design_ids][:n_validation_release]
    validation = xtt_drug + release_val

    # stress: occluded 8XTT (detected-below-D* or not-detected) + AF2 + top metad
    xtt_occluded = _by_drug_desc([r for r in xtt if not _druggable(r, d_star)])
    metad_top = _by_drug_desc(nr3_metad)[:1]
    stress = xtt_occluded + list(af2) + metad_top

    prov = {
        "d_star": d_star,
        "counts": {"design": len(design), "validation": len(validation), "stress": len(stress),
                   "nr4a1_antitarget": len(nr1_metad), "nr4a2_antitarget": len(nr2_metad)},
        "rule": {
            "design": "top-%d druggable unbiased-release frames (>= %.2f), AF2 excluded" % (n_design, d_star),
            "validation": "druggable 8XTT (>= %.2f) + next %d druggable release not in design" % (d_star, n_validation_release),
            "stress": "occluded 8XTT (detected<D* or undetected) + AF2 frame(s) + top-1 NR4A3-metad",
            "anti_target": "all provided nr4a1_metad / nr4a2_metad frames",
        },
        "warnings": [],
    }
    if not design:
        prov["warnings"].append("NO druggable release frame -> design set EMPTY (panel cannot rank)")
    if not xtt_drug:
        prov["warnings"].append("NO druggable 8XTT frame -> validation lacks the held-out experimental test")
    if not (nr1_metad and nr2_metad):
        prov["warnings"].append("missing an anti-target metad ensemble (NR4A1 and/or NR4A2)")

    return {"design": design, "validation": validation, "stress": stress,
            "nr4a1_antitarget": nr1_metad, "nr4a2_antitarget": nr2_metad, "_provenance": prov}
