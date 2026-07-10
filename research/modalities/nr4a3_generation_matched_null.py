#!/usr/bin/env python3
"""
GENERATION-MATCHED DECOY NULL driver — the winner's-curse / generative-confound control for the de-novo
NR4A3 funnel (JCIM review Major Comment 12/13; review-response §1).

WHY. ``denovo_401`` was DiffSBDD-generated conditioned on the NR4A3 release-frame pocket AND selected
best-of-N, whereas the decoy null it beats was NOT generated for any pocket. This driver runs the IDENTICAL
generate -> developability-filter -> dock -> multi-snapshot MM-GBSA -> best-of-N funnel on CONTROL OBJECTIVES
and asks: how often does the whole procedure MANUFACTURE a "confirmed-selective, above-null survivor" on a
null objective? If the real campaign's survival is within the manufactured rate, the confound is not
excluded; if it exceeds it, denovo_401's survival is not a generic funnel artifact.

This is an ORCHESTRATION + REDUCE driver — it does NOT dispatch or fabricate any compute. It (1) preps the
control inputs the dispatched jobs consume (a scrambled-objective candidate JSON for control b; a control
receptor manifest for control c), and (2) reduces the finished real + control MM-GBSA outputs into
``nr4a3-generation-matched-null.json``. All counting/thresholding/stats live in the pure, unit-tested
``generation_matched_null`` module.

CONTROLS (cheapest-yet-meaningful, maximal machinery reuse):
  (b) SCRAMBLED-OBJECTIVE on the real NR4A3 release frame — REUSE the real generations (no new g5 gen),
      permute ``denovo_promise`` so the best-of-N advanced to docking is decoupled from the divergent-handle
      objective (real pocket, null objective). Isolates the winner's-curse in the SELECTION step.
  (c) PARALOGUE-POCKET generation — a FRESH DiffSBDD generation into the NR4A1 (or NR4A2) metad-opened
      pocket, then the identical funnel; any NR4A3-selective survivor is a manufactured false positive
      (the molecules were designed for a different pocket). A real generation into a real non-target pocket.
  (a) property-matched decoy pocket — SUPPORTED via the same control-pocket path (build_control_receptor_
      manifest on any matched pocket PDB); left optional because the repo has no matched-pocket builder yet.

MODES (env MODE): ``prep-scramble`` | ``prep-manifest`` | ``reduce`` (default). See the functions below.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generation_matched_null as gmn          # noqa: E402
import selectivity_calibration as sc           # noqa: E402

OUT = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _bool(env, default=False):
    v = os.environ.get(env)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# MODE prep-scramble — build the scrambled-objective candidate JSON (control b).
# ---------------------------------------------------------------------------
def prep_scramble():
    """Read the REAL nr4a3-denovo.json (env DENOVO_JSON), permute the promise (seed SCRAMBLE_SEED), and
    write a scrambled nr4a3-denovo.json to OUTPUT_DIR. The dispatcher then runs gpu-denovo-dock-aws.yml with
    denovo_prefix pointing at this control prefix -> the funnel docks a top-N chosen by a NULL objective."""
    src = os.environ.get("DENOVO_JSON")
    if not src or not os.path.exists(src):
        sys.exit(f"prep-scramble: set DENOVO_JSON to the real nr4a3-denovo.json (got {src!r})")
    seed = int(os.environ.get("SCRAMBLE_SEED", "0"))
    denovo = _load(src)
    scrambled = gmn.scrambled_denovo_json(denovo, seed=seed)
    dest = os.path.join(OUT, "nr4a3-denovo.json")
    os.makedirs(OUT, exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(scrambled, fh, indent=2)
    n_valid = sum(1 for c in scrambled["candidates"] if c.get("denovo_promise") is not None)
    print(f"prep-scramble: wrote {dest} (seed={seed}, {n_valid} valid generations re-ranked by null "
          f"objective)", flush=True)


# ---------------------------------------------------------------------------
# MODE prep-manifest — build the control-pocket receptor manifest (control c / a).
# ---------------------------------------------------------------------------
def prep_manifest():
    """Write the DiffSBDD receptor manifest that points the identical generation job at a CONTROL pocket.
    Env: CONTROL_PDB (basename of the receptor PDB, e.g. nr4a1-opened.pdb), CONTROL_BOX_RES (comma resSeqs
    to box on — the paralogue CV residues / matched-pocket lining), CONTROL_TARGET (label, e.g. NR4A1),
    CONTROL_SOURCE (provenance string). The PDB itself is placed alongside by the dispatcher."""
    pdb = os.environ.get("CONTROL_PDB")
    if not pdb:
        sys.exit("prep-manifest: set CONTROL_PDB (basename of the control receptor PDB)")
    box = [int(x) for x in os.environ.get("CONTROL_BOX_RES", "").split(",") if x.strip()]
    if not box:
        sys.exit("prep-manifest: set CONTROL_BOX_RES (comma-separated pocket-lining resSeqs)")
    target = os.environ.get("CONTROL_TARGET", "control")
    source = os.environ.get("CONTROL_SOURCE", "control-pocket-generation")
    man = gmn.build_control_receptor_manifest(pdb, box, target, source)
    dest = os.path.join(OUT, "nr4a3-release-druggable.json")   # name the gen job expects
    os.makedirs(OUT, exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(man, fh, indent=2)
    print(f"prep-manifest: wrote {dest} -> DiffSBDD target {pdb} boxed on {len(box)} residues "
          f"(target={target})", flush=True)


# ---------------------------------------------------------------------------
# MODE reduce — compute the survivor reports + comparison JSON.
# ---------------------------------------------------------------------------
def _decoy_margins():
    """The decoy null the survivor bar is calibrated against. DECOY_MMGBSA (path) => a FRAME-MATCHED decoy
    null (the non-NR4A decoy set pushed through the same NR4A3/NR4A1/NR4A2 MM-GBSA frames — preferred, the
    manuscript stresses frame-dependence). Else the committed single-snapshot constant."""
    p = os.environ.get("DECOY_MMGBSA")
    if p and os.path.exists(p):
        margins = gmn.decoy_margins_from_mmgbsa(_load(p))
        if margins:
            return margins, f"frame-matched decoy MM-GBSA ({len(margins)} decoys, {os.path.basename(p)})"
    return list(sc.DECOY_2026_06_30), f"committed constant DECOY_2026_06_30 ({len(sc.DECOY_2026_06_30)})"


def _parse_named(env):
    """'name:path,name2:path2' -> [(name, path)] (path may itself be absent -> skipped by the caller)."""
    out = []
    for tok in os.environ.get(env, "").split(","):
        tok = tok.strip()
        if not tok:
            continue
        if ":" not in tok:
            sys.exit(f"{env}: expected name:path entries, got {tok!r}")
        name, path = tok.split(":", 1)
        out.append((name.strip(), path.strip()))
    return out


def _parse_counts(env):
    out = {}
    for tok in os.environ.get(env, "").split(","):
        tok = tok.strip()
        if tok and ":" in tok:
            name, cnt = tok.split(":", 1)
            out[name.strip()] = int(cnt.strip())
    return out


def reduce_():
    """Reduce the real + control MM-GBSA outputs into nr4a3-generation-matched-null.json."""
    q = float(os.environ.get("NULL_Q", "95"))
    band = float(os.environ.get("BAND", "1.0"))
    subtract_sd = _bool("SUBTRACT_SD", default=False)     # set for the multi-snapshot bar (margin-SD > null)
    decoy_margins, decoy_src = _decoy_margins()

    real_path = os.environ.get("REAL_MMGBSA")
    if not real_path or not os.path.exists(real_path):
        sys.exit(f"reduce: set REAL_MMGBSA to the real campaign nr4a3-mmgbsa.json (got {real_path!r})")
    counts = _parse_counts("NGEN")                          # name->generation-pool size (denominators)
    real_ngen = int(os.environ["REAL_NGEN"]) if os.environ.get("REAL_NGEN") else counts.get("real")
    real = _load(real_path)
    real_report = gmn.survivor_report(real.get("candidates", []), decoy_margins, n_generated=real_ngen,
                                      q=q, band=band, subtract_sd=subtract_sd)
    # denovo_401 is the sole robust real lead the manuscript advances; allow an explicit override so the
    # comparison uses the true harvested-survivor count rather than whatever the rescore file happens to hold.
    real_survivors = int(os.environ["REAL_SURVIVORS"]) if os.environ.get("REAL_SURVIVORS") else None

    controls = []
    for name, path in _parse_named("CONTROL_MMGBSA"):
        if not os.path.exists(path):
            print(f"  WARN: control {name}: {path} missing — skipped", file=sys.stderr)
            continue
        rep = gmn.survivor_report(_load(path).get("candidates", []), decoy_margins,
                                  n_generated=counts.get(name), q=q, band=band, subtract_sd=subtract_sd)
        rep["control"] = name
        controls.append(rep)

    res = {
        "_note": ("Generation-matched decoy null: the identical de-novo funnel run on CONTROL objectives, "
                  "to measure how often the whole generate->filter->dock->MM-GBSA->best-of-N procedure "
                  "manufactures a confirmed-selective, above-null survivor. Screening-null statistic."),
        "params": {"null_q": q, "band": band, "subtract_sd": subtract_sd, "decoy_null": decoy_src,
                   "n_decoys": len(decoy_margins),
                   "decoy_threshold": gmn.sc.decoy_threshold(decoy_margins, q)},
        "real_campaign": {**real_report, "campaign": "nr4a3-release (denovo_401)",
                          "survivors_reported": real_survivors},
        "controls": controls,
    }
    if controls:
        res["comparison"] = gmn.compare_campaigns(real_report, controls, real_survivors=real_survivors)
    else:
        res["comparison"] = {"verdict": "no control MM-GBSA outputs supplied yet — dispatch the controls, "
                                        "then re-run reduce"}
    dest = os.path.join(OUT, "nr4a3-generation-matched-null.json")
    os.makedirs(OUT, exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps({"real": {k: real_report[k] for k in ("n_generated", "n_survivors", "survivors")},
                      "controls": [{k: c.get(k) for k in ("control", "n_generated", "n_survivors",
                                                          "best_margin", "manufactured")} for c in controls],
                      "comparison": res["comparison"]}, indent=2), flush=True)
    print(f"reduce: wrote {dest}", flush=True)


def main():
    mode = os.environ.get("MODE", "reduce").strip()
    if mode == "prep-scramble":
        prep_scramble()
    elif mode == "prep-manifest":
        prep_manifest()
    elif mode == "reduce":
        reduce_()
    else:
        sys.exit(f"unknown MODE={mode!r} (prep-scramble | prep-manifest | reduce)")


if __name__ == "__main__":
    main()
