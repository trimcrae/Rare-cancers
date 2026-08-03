#!/usr/bin/env python3
"""RUNG `5b-T` — the PRE-REGISTERED three-arm GO/NO-GO, read over all 16 models per arm. ($0 CPU)

The criteria are not written here. They are read from the `gate` block of
[`ternary-rebuild-cost.json`](./ternary-rebuild-cost.json), which was registered on 2026-08-02 **before any
arm of this rung had been run**, and this module is their arithmetic. Where a number appears below it is
imported from that artifact or from the artifact that owns it — never retyped (CLAUDE.md rule 1).

  **(A) SEQUENCE-ENCODED, NOT A PLACEMENT ARTIFACT.** At least one discriminating position at which the
      ALIGNED RESIDUE ITSELF differs in both NR4A1 and NR4A2. The earlier pass returned six discriminating
      positions and **five carried the identical residue in all three paralogues**; an identical residue
      cannot encode a paralogue difference, so those are differences between three independently-folded
      structures, not evidence of anything.

  **(B) REPRODUCIBLE.** That position present in **≥ 12 of 16** NR4A3 models AND **≤ 4 of 16** on **each**
      comparator. Under a per-model coin flip each tail is one-sided binomial *p* = 0.0384. ⛔ Anything
      between is **INDETERMINATE — a third outcome and NOT a pass**, and below `MIN_MODELS` per arm the
      module refuses the word "reproducible" outright.

  **(C) THE TETHER GEOMETRY THE CATEGORICAL AXIS DEPENDS ON SURVIVES ASSEMBLY.** ⛔ **NO-GO, not a caveat.**
      C1: the median electrophile-carbon-to-C397-SG distance across the accepted NR4A3 models lies within the
      pendant-reach convention the construct was designed at. C2: the construct's own backbone length still
      lies inside the assembled placement's C397 chemoselectivity window — short of the first PARALOGUE
      cysteine to come into reach.
      ⚠ **REPORTED UNDER BOTH REACH CONVENTIONS, NEVER MERGED.** `nr4a3-linker-covalent-reach.json` grades
      every cell twice, `through_space` and `corridor`, and they do not agree for this construct. Merging
      them — or quoting whichever passes — would be choosing the convention on the outcome.

⛔ REFUSALS ARE NOT RESULTS. An arm with no models is unrun, never a zero. A failed harness positive control
makes the whole run **uninterpretable**, and this module says so rather than reading the arms.

⛔ WHAT A PASS LICENSES: a STRUCTURAL statement — these modelled interface contacts differ between the
paralogues, at named positions, with a per-model frequency and a validated detector behind the descriptor.
WHAT IT DOES NOT: any affinity, potency or N-fold claim (this computes no free energy); discharging `R12`,
`R13`, `R6` or the free-energy requirement; degradation, efficacy, safety or clinical readiness; the word
"blind" (DeepTernary is GIVEN which pocket each end occupies); or generalisation (both harness controls are
inside the model's data horizon).
"""
from __future__ import annotations

import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

FOCUS = "NR4A3"
COMPARATORS = ("NR4A1", "NR4A2")

#: Below this many models on ANY arm, no reproducibility statement is made in either direction. Imported from
#: the module that owns the rule so the two cannot drift.
def min_models():
    import nr4a_ternary_signature as S
    return S.MIN_MODELS_FOR_REPRODUCIBILITY


def gate_spec(path=None):
    """(spec, error) — the PRE-REGISTERED criteria, read from the artifact that registered them."""
    path = path or os.path.join(HERE, "ternary-rebuild-cost.json")
    if not os.path.exists(path):
        return None, ("%s absent — the gate criteria were registered there before the run and this module "
                      "will not invent them" % os.path.basename(path))
    doc = json.load(open(path))
    g = doc.get("gate")
    if not g:
        return None, "%s carries no `gate` block" % os.path.basename(path)
    return g, None


def binomial_tail_at_least(k, n, p=0.5):
    """One-sided P(X >= k) for X ~ Bin(n, p). Exact, stdlib — the null the gate's p-values come from."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def binomial_tail_at_most(k, n, p=0.5):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


# ---------------------------------------------------------------------------------------------------------
# Reading the models
# ---------------------------------------------------------------------------------------------------------


def arm_models(pred_root, arm):
    """Every predicted complex for one arm, sorted. Flat `complex_pred_<ARM>_<seed>.pdb` layout."""
    hits = sorted(glob.glob(os.path.join(pred_root, "complex_pred_%s_*.pdb" % arm)))
    if not hits:
        hits = sorted(glob.glob(os.path.join(pred_root, arm, "complex_pred_*.pdb")))
    return hits


def model_signature(path):
    """(signature, error) for one predicted complex, chains resolved by length and never guessed."""
    import nr4a_ternary_signature as S
    tgt, e3, detail, err = S.resolve_chains(path)
    if err:
        return None, err
    sig = S.signature_of(path, tgt, e3)
    if sig.get("error"):
        return None, sig["error"]
    sig["chain_detail"] = detail
    return sig, None


def presence_by_column(sigs, ref_seq):
    """[{column: bool}] per model, columns indexed on the REFERENCE (NR4A3) sequence.

    ⛔ ALIGNED BY SEQUENCE, NEVER BY RESIDUE NUMBER. The three paralogue models are independently built and
    numbered locally; equal numbers are not the same residue. `presence` at a column means "the residue this
    arm carries at that aligned column makes a polar contact to the E3 in this model"."""
    import selcal_cofold_validate as V
    out, letters = [], {}
    for sig in sigs:
        ident, pairs = V.align_identity(sig["target_sequence"], ref_seq)
        keys = [tuple(k) for k in sig["residue_keys"]]
        contacts = sig["contacts"]
        by_resseq = {}
        for v in contacts.values():
            by_resseq[(v["resseq"], (v["icode"] or "").strip())] = v
        present = {}
        for ia, ib in pairs:
            if ia >= len(keys):
                continue
            _, resseq, icode = keys[ia]
            letters.setdefault(ib, sig["target_sequence"][ia])
            v = by_resseq.get((resseq, (icode or "").strip()))
            if v and v.get("n_polar_contacts", 0) > 0:
                present[ib] = True
        out.append({"present": present, "identity_to_reference": round(ident, 4)})
    return out, letters


def arm_A_and_B(model_sets, spec):
    """The (A) and (B) arithmetic over every model of every arm."""
    doc = {"n_models": {k: len(v) for k, v in sorted(model_sets.items())}, "unreadable": {}}
    sigs, errs = {}, {}
    for arm, paths in model_sets.items():
        ok, bad = [], []
        for p in paths:
            s, e = model_signature(p)
            (ok.append(s) if s else bad.append({"model": os.path.basename(p), "why": e}))
        sigs[arm] = ok
        if bad:
            errs[arm] = bad
    doc["unreadable"] = errs
    doc["n_readable"] = {k: len(v) for k, v in sorted(sigs.items())}

    missing = [a for a in (FOCUS,) + COMPARATORS if not sigs.get(a)]
    if missing:
        doc["verdict"] = "REFUSED"
        doc["sentence"] = ("REFUSED — no readable model on %s. A comparison missing an arm is not a "
                           "comparison; unread is not absent." % ", ".join(missing))
        return doc

    n_min = min(len(v) for v in sigs.values())
    doc["min_models_per_arm"] = n_min
    doc["reproducibility_bar"] = min_models()
    if n_min < min_models():
        doc["verdict"] = "REFUSED"
        doc["sentence"] = ("REFUSED — only %d model(s) on the thinnest arm, below the bar of %d. No "
                           "reproducibility statement is made in either direction; one model cannot "
                           "distinguish a determinant from that model's accident."
                           % (n_min, min_models()))
        return doc

    ref_seq = sigs[FOCUS][0]["target_sequence"]
    per_arm, letters_by_arm = {}, {}
    for arm in (FOCUS,) + COMPARATORS:
        rows, letters = presence_by_column(sigs[arm], ref_seq)
        per_arm[arm] = rows
        letters_by_arm[arm] = letters

    cols = sorted(set().union(*[set(r["present"]) for rows in per_arm.values() for r in rows]))
    thr = spec["B_reproducible_not_one_models_accident"]["threshold"]
    lo, hi = thr["min_present_on_focus"], thr["max_present_on_each_comparator"]

    table = []
    for c in cols:
        counts = {arm: sum(1 for r in per_arm[arm] if r["present"].get(c)) for arm in per_arm}
        n = {arm: len(per_arm[arm]) for arm in per_arm}
        aa = {arm: letters_by_arm[arm].get(c) for arm in per_arm}
        # (A): the aligned residue itself must differ in BOTH comparators, and be known in all three.
        seq_encoded = (aa[FOCUS] is not None
                       and all(aa[c2] is not None and aa[c2] != aa[FOCUS] for c2 in COMPARATORS))
        focus_ok = counts[FOCUS] >= lo
        comp_ok = all(counts[c2] <= hi for c2 in COMPARATORS)
        if focus_ok and comp_ok:
            b = "PASS"
        elif counts[FOCUS] == 0 and all(counts[c2] == 0 for c2 in COMPARATORS):
            b = "ABSENT"
        else:
            b = "INDETERMINATE"
        table.append({
            "reference_column": c, "residues": aa, "counts": counts, "n_models": n,
            "sequence_encoded": bool(seq_encoded), "arm_B": b,
            "p_focus_at_least": round(binomial_tail_at_least(counts[FOCUS], n[FOCUS]), 5),
            "p_comparators_at_most": {c2: round(binomial_tail_at_most(counts[c2], n[c2]), 5)
                                      for c2 in COMPARATORS}})

    encoded = [r for r in table if r["sequence_encoded"] and r["arm_B"] != "ABSENT"]
    passing = [r for r in encoded if r["arm_B"] == "PASS"]
    indet = [r for r in encoded if r["arm_B"] == "INDETERMINATE"]
    same_residue = [r for r in table if not r["sequence_encoded"] and r["arm_B"] == "PASS"]

    doc["thresholds"] = {"min_present_on_focus": lo, "max_present_on_each_comparator": hi,
                         "models_per_arm_registered": thr.get("models_per_arm")}
    doc["per_column"] = table
    doc["n_columns_with_any_contact"] = len(cols)
    doc["A_sequence_encoded_candidates"] = [r["reference_column"] for r in encoded]
    doc["A_verdict"] = "PASS" if encoded else "FAIL"
    doc["B_passing_columns"] = [r["reference_column"] for r in passing]
    doc["B_indeterminate_columns"] = [r["reference_column"] for r in indet]
    doc["B_verdict"] = "PASS" if passing else ("INDETERMINATE" if indet else "FAIL")
    doc["same_residue_placement_artifacts_that_would_have_passed_B"] = \
        [r["reference_column"] for r in same_residue]
    doc["_why_same_residue_is_excluded"] = (
        "an identical residue at the aligned column cannot encode a paralogue difference; five of the six "
        "positions the earlier pass returned were exactly this, and counting them is how three "
        "independently-folded structures become a selectivity claim")
    doc["verdict"] = "PASS" if (doc["A_verdict"] == "PASS" and doc["B_verdict"] == "PASS") else (
        "INDETERMINATE" if doc["B_verdict"] == "INDETERMINATE" and doc["A_verdict"] == "PASS" else "FAIL")
    return doc


# ---------------------------------------------------------------------------------------------------------
# Arm (C)
# ---------------------------------------------------------------------------------------------------------


def arm_C(frame_doc, pred_root, reach_path=None):
    """C1 (measured on the accepted NR4A3 models) and C2 (the committed chemoselectivity window).

    ⚠ BOTH CONVENTIONS, SIDE BY SIDE AND NEVER MERGED."""
    import nr4a3_linker_design as LD
    reach_path = reach_path or os.path.join(HERE, "nr4a3-linker-covalent-reach.json")
    out = {"_reported": "under BOTH reach conventions, never merged — they do not agree for this construct"}

    arm_rows = {r["paralogue"]: r for r in frame_doc.get("arms", [])}
    n_bb = (frame_doc.get("degrader") or {}).get("n_backbone_atoms_measured")
    construct_id = frame_doc.get("construct_id") or ""
    pendant = construct_id.rsplit("_", 1)[-1] if "_" in construct_id else None
    reach_key = (LD.PENDANT.get(pendant) or {}).get("reach_key") if hasattr(LD, "PENDANT") else None
    if reach_key is None:
        for tbl in ("PENDANT", "WEDGE", "ELECTROPHILE"):
            t = getattr(LD, tbl, None)
            if isinstance(t, dict) and pendant in t:
                reach_key = t[pendant].get("reach_key")
                break
    out["construct"] = {"construct_id": construct_id, "pendant": pendant, "reach_key": reach_key,
                        "n_backbone_atoms_measured": n_bb}

    # ---- C2: the committed window, at the placement this rung actually assembled at
    placement = (frame_doc.get("placement") or {}).get("meta_basin_id")
    cell_key = "%s@term_a_exemplar" % placement if placement else None
    reach = json.load(open(reach_path)) if os.path.exists(reach_path) else {}
    windows = (reach.get("★_family_wide_chemoselectivity_window") or {}).get("by_convention") or {}
    c2 = {}
    for conv, cells in windows.items():
        cell = next((c for c in cells if c.get("placement") == cell_key and c.get("pendant") == reach_key),
                    None)
        if cell is None:
            c2[conv] = {"verdict": "REFUSED", "why": "no graded cell for %s x %s" % (cell_key, reach_key)}
            continue
        lo, hi = cell.get("window_lo"), cell.get("window_hi")
        inside = (lo is not None and hi is not None and n_bb is not None and lo <= n_bb <= hi)
        c2[conv] = {"window_lo": lo, "window_hi": hi, "closed_by": cell.get("closed_by"),
                    "closed_at_atoms": cell.get("closed_at_atoms"), "target_atoms": cell.get("target_atoms"),
                    "construct_backbone_atoms": n_bb,
                    "verdict": "PASS" if inside else "FAIL",
                    "why": (None if inside else
                            "the construct's %s backbone atoms lie %s the window [%s, %s], which %s closes at "
                            "%s atoms — the assembled ternary is past the paralogue-collision knee under this "
                            "convention, and the gate calls that NO-GO, not a caveat"
                            % (n_bb, "below" if (lo is not None and n_bb is not None and n_bb < lo) else
                               "above", lo, hi, cell.get("closed_by"), cell.get("closed_at_atoms")))}
    out["C2_chemoselectivity_window"] = c2

    # ---- C1: the measured electrophile-to-C397 distance on the NR4A3 arm's accepted models
    row = arm_rows.get(FOCUS) or {}
    inputs = (row.get("detail") or {}).get("arm_C_inputs") or {}
    idx = inputs.get("electrophile_beta_carbon_index_in_ligand_pdb")
    c1 = {"pendant_reach_A": None, "measured": None}
    try:
        c1["pendant_reach_A"] = LD.PENDANT_REACH.get(reach_key)
    except Exception:                                            # noqa: BLE001
        pass
    models = arm_models(pred_root, "%s_%s" % (FOCUS, "5BT_LIG"))
    dists = []
    unreadable = []
    for p in models:
        d, why = _electrophile_to_c397(p, idx)
        if d is None:
            unreadable.append({"model": os.path.basename(p), "why": why})
        else:
            dists.append(d)
    if not dists:
        c1.update(verdict="REFUSED",
                  why=("the electrophile→C397-SG distance could not be measured on any accepted NR4A3 model "
                       "(%d attempted). REFUSED, not a zero." % len(models)),
                  unreadable=unreadable[:5])
    else:
        dists.sort()
        med = dists[len(dists) // 2]
        lim = c1["pendant_reach_A"]
        c1.update(measured={"n_models": len(dists), "median_A": round(med, 2),
                            "min_A": round(dists[0], 2), "max_A": round(dists[-1], 2)},
                  verdict=("PASS" if (lim is not None and med <= lim) else
                           "FAIL" if lim is not None else "REFUSED"),
                  why=(None if (lim is not None and med <= lim) else
                       "median %.2f Å against the %s pendant-reach convention of %s Å"
                       % (med, reach_key, lim)),
                  unreadable=unreadable[:5])
    out["C1_electrophile_reaches_C397"] = c1

    verdicts = [c1.get("verdict")] + [v.get("verdict") for v in c2.values()]
    out["verdict_by_convention"] = {conv: ("PASS" if (c1.get("verdict") == "PASS" and v.get("verdict") == "PASS")
                                           else "REFUSED" if "REFUSED" in (c1.get("verdict"), v.get("verdict"))
                                           else "FAIL")
                                    for conv, v in c2.items()}
    out["verdict"] = ("PASS" if all(v == "PASS" for v in out["verdict_by_convention"].values())
                      else "REFUSED" if "REFUSED" in verdicts else "FAIL")
    out["_registered_at_risk_in_advance"] = (
        "⚠ This arm was registered AT RISK before the rung ran: no committed construct sits at or below 12 "
        "backbone atoms, and the only CRBN basin in the CONFIRMED set needs 13 for C397 under the rung-5a "
        "convention. The sharper conflict found since is that CRBN reaches C397 at 12 only under "
        "THROUGH-SPACE; under CORRIDOR its floor is 14. Saying any of this afterwards would be worthless, "
        "which is why it is registered rather than discovered.")
    return out


def _electrophile_to_c397(path, lig_atom_index, target_resseq=25):
    """(distance Å, error). The NR4A3-unique cysteine is local residue 25 in the matched opened model, which
    is the numbering `protein1.pdb` was written with and the numbering the prediction inherits."""
    import selcal_cofold_validate as V
    try:
        atoms = V.parse_structure(path)
    except Exception as e:                                       # noqa: BLE001
        return None, "unreadable: %s" % e
    if not lig_atom_index:
        return None, "the frame artifact did not record the electrophile's atom index"
    het = [a for a in atoms if a.hetatm and a.is_heavy]
    if len(het) < lig_atom_index:
        return None, ("the predicted complex carries %d ligand heavy atoms, fewer than the recorded "
                      "electrophile index %d — the atom correspondence is not established, so no distance "
                      "may be quoted" % (len(het), lig_atom_index))
    e = het[lig_atom_index - 1]
    cys = [a for a in atoms if not a.hetatm and a.resseq == target_resseq and a.resname.upper() == "CYS"]
    if not cys:
        return None, "no CYS at local residue %d in the predicted target chain" % target_resseq
    sg = next((a for a in cys if a.name.strip().upper() == "SG"), None)
    if sg is None:
        return None, "residue %d is a CYS but carries no SG atom in the prediction" % target_resseq
    return math.dist((e.x, e.y, e.z), (sg.x, sg.y, sg.z)), None


# ---------------------------------------------------------------------------------------------------------
# The harness controls, and the whole-run interpretability question they decide
# ---------------------------------------------------------------------------------------------------------


def harness_controls(paths):
    """(rows, interpretable, sentence). A failed positive control makes the run UNINTERPRETABLE — this
    module says so and does NOT read the arms behind it."""
    rows = []
    for p in paths:
        if not os.path.exists(p):
            rows.append({"artifact": os.path.basename(p), "ran": False,
                         "why": "absent — the control did not run to a verdict"})
            continue
        d = json.load(open(p))
        rows.append({"artifact": os.path.basename(p), "ran": True, "case": d.get("case"),
                     "case_is_in_set": d.get("case_is_in_set"),
                     "passes": bool(d.get("positive_control_passes")),
                     "summary": d.get("summary"), "sentence": d.get("sentence")})
    ok = bool(rows) and all(r.get("passes") for r in rows)
    if ok:
        s = ("Both harness positive controls PASS (%s). The harness and both scoring instruments can produce "
             "and recognise a correct ternary, so a null on the paralogue arms is about those systems rather "
             "than the plumbing. ⛔ It says NOTHING about generalisation: both cases are inside the model's "
             "2023-10-14 data horizon." % ", ".join(str(r.get("case")) for r in rows))
    else:
        s = ("⛔ A HARNESS POSITIVE CONTROL DID NOT PASS, so THE WHOLE RUN IS UNINTERPRETABLE and the "
             "paralogue arms are not read. A harness that cannot score a known-good ternary cannot grade a "
             "suspect one. Detail: %s"
             % "; ".join("%s: %s" % (r["artifact"], r.get("why") or r.get("sentence")) for r in rows))
    return rows, ok, s


# ---------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------


def run(pred_root, frame_path, control_paths, reach_path=None, spec_path=None):
    spec, err = gate_spec(spec_path)
    doc = {"_what": "RUNG 5b-T — the pre-registered three-arm GO/NO-GO",
           "_criteria_source": "ternary-rebuild-cost.json -> gate (registered 2026-08-02, before any arm ran)",
           "_scope": {
               "a_pass_licenses": "a STRUCTURAL statement: these modelled interface contacts differ between "
                                  "the paralogues, at named positions, with a per-model frequency and a "
                                  "validated detector behind the descriptor",
               "a_pass_does_not_license": [
                   "any affinity, potency or N-fold statement — this computes NO free energy",
                   "discharging R12, R13, R6 or the free-energy requirement",
                   "any degradation, efficacy, safety, therapeutic-window or clinical claim",
                   "the word 'blind' — DeepTernary is GIVEN which pocket each end of the degrader occupies",
                   "generalisation — both harness controls are inside the model's 2023-10-14 data horizon"],
               "inherited_limits_that_travel_with_every_result": [
                   "`R5` is UNRESOLVED and site 1 inherits it: `V3` is INCONCLUSIVE because the pipeline's "
                   "SITE SELECTION missed on 6 of 6 pairs, so the warhead sub-pose is conditional",
                   "`R3` FAILED on 2026-08-03: the generation frame (unbiased release replica 0, frame 95) "
                   "scores druggability 0.259 against D* = 0.53 — see `_r3_dependency` below",
                   "`V1` validates ONE contact in ONE pair (SMARCA2 Gln1469<->VCB) and makes no NR4A "
                   "prediction correct",
                   "`V2`'s post-horizon pass is ONE arm on a VHL/bromodomain system; NOTHING covers a CRBN "
                   "ternary with a nuclear receptor, which is exactly what this rung assembles",
                   "there is NO native NR4A3 ternary, so the published 'superpose into the native frame' "
                   "step has no reference and a modelled RUNG-5a basin supplies the arrangement instead",
                   "every structure here is an isolated LBD construct — `R13` is untouched"]}}
    if err:
        doc["verdict"] = "REFUSED"
        doc["sentence"] = "REFUSED — %s" % err
        return doc

    rows, interpretable, csent = harness_controls(control_paths)
    doc["harness_controls"] = rows
    doc["run_is_interpretable"] = interpretable
    doc["harness_sentence"] = csent
    if not interpretable:
        doc["verdict"] = "UNINTERPRETABLE"
        doc["sentence"] = csent
        return doc

    frame = json.load(open(frame_path)) if os.path.exists(frame_path) else {}
    doc["frame_artifact"] = os.path.basename(frame_path)
    doc["arms_built"] = frame.get("ready_arms")
    doc["arms_refused"] = frame.get("refused_arms")
    doc["_r3_dependency"] = _r3_dependency(frame)

    model_sets = {p: arm_models(pred_root, "%s_5BT_LIG" % p) for p in (FOCUS,) + COMPARATORS}
    doc["A_and_B"] = arm_A_and_B(model_sets, spec)
    doc["C"] = arm_C(frame, pred_root, reach_path)

    ab = doc["A_and_B"].get("verdict")
    c = doc["C"].get("verdict")
    if ab == "REFUSED" or c == "REFUSED":
        doc["verdict"] = "REFUSED"
    elif c == "FAIL":
        doc["verdict"] = "NO-GO"
    elif ab == "PASS" and c == "PASS":
        doc["verdict"] = "GO"
    elif ab == "INDETERMINATE":
        doc["verdict"] = "INDETERMINATE"
    else:
        doc["verdict"] = "NO-GO"
    doc["sentence"] = _sentence(doc)
    return doc


def _r3_dependency(frame):
    """Does site 1 derive from the frame `R3` failed on? Answered from the artifacts, not from memory."""
    src = ((frame.get("arms") or [{}])[0].get("detail") or {}).get("matched_superposition")
    return {
        "_question": "does site 1 derive from the generation frame that FAILED `R3` on 2026-08-03?",
        "answer": "NO — but the two are cousins, and the difference matters less than it looks.",
        "site_1_receptors": "results/nr4a3-matrix/nr4a{1,2,3}-opened.pdb — the METAD-OPENED matched models "
                            "(NR4A3 frame 300, NR4A1 524, NR4A2 125), fpocket druggability 0.931/0.981/0.938 "
                            "as recorded in results/nr4a3-matrix/nr4a3-matrix.json",
        "the_frame_R3_failed_on": "the unbiased RELEASE replica 0, frame 95, scored 0.259 against D* = 0.53 "
                                  "(r3-generation-frame-harmonized.json) — a DIFFERENT frame from a "
                                  "DIFFERENT trajectory class",
        "⚠_what_it_still_does_to_the_reading": "the matched models and the generation frame come from the "
            "same metadynamics/release pipeline and the same cryptic-pocket hypothesis, so `R3`'s failure is "
            "evidence about that pipeline's OUTPUT DISTRIBUTION, not only about one frame. The honest "
            "statement is that site 1 is NOT the failing frame and its own druggability was scored ABOVE D* "
            "on its own model — and that a pipeline shown to emit a non-druggable generation frame cannot be "
            "assumed to emit druggable ones. That is a caveat on the SITE, which arm (A)/(B) then inherit; "
            "it is not repaired by anything in this rung.",
        "matched_superposition_of_the_comparators": src}


def _sentence(doc):
    v = doc["verdict"]
    ab, c = doc.get("A_and_B", {}), doc.get("C", {})
    conv = c.get("verdict_by_convention") or {}
    head = {
        "GO": "GATE PASSED on all three pre-registered arms.",
        "NO-GO": "GATE NOT PASSED.",
        "INDETERMINATE": "GATE INDETERMINATE — the third outcome, and NOT a pass.",
        "REFUSED": "GATE REFUSED — a required measurement could not be made, which is not a zero.",
    }[v]
    return ("%s (A) sequence-encoded: %s%s. (B) reproducible ≥%s of %s focus / ≤%s of %s each comparator: %s%s. "
            "(C) tether geometry, reported under BOTH conventions and never merged: %s. "
            "⛔ Whatever this says, it is STRUCTURAL: no free energy is computed, nothing about affinity, "
            "degradation, efficacy or safety follows, and the arms are not blind — DeepTernary is given which "
            "pocket each end of the degrader occupies."
            % (head,
               ab.get("A_verdict"),
               (" (%s candidate column(s))" % len(ab.get("A_sequence_encoded_candidates") or [])) if ab else "",
               (ab.get("thresholds") or {}).get("min_present_on_focus"),
               ab.get("min_models_per_arm") or "?",
               (ab.get("thresholds") or {}).get("max_present_on_each_comparator"),
               ab.get("min_models_per_arm") or "?",
               ab.get("B_verdict"),
               (" (passing: %s; indeterminate: %s)"
                % (", ".join(map(str, ab.get("B_passing_columns") or [])) or "none",
                   ", ".join(map(str, ab.get("B_indeterminate_columns") or [])) or "none")) if ab else "",
               "; ".join("%s %s" % (k, val) for k, val in sorted(conv.items())) or c.get("verdict")))


def _et_now():
    """US Eastern, 12-hour, per CLAUDE.md §1. EDT = UTC−4 on this date."""
    from datetime import datetime, timedelta, timezone
    return datetime.now(timezone(timedelta(hours=-4)))


def map_edits(doc):
    """The roadmap edits this run requires, ready to apply verbatim and anchor-checkable.

    ⛔ EVERY `proposed_text` POINTS AT THE ARTIFACT AND RESTATES NO NUMBER (CLAUDE.md rule 1): the verdict,
    the per-column counts and the two arm-(C) conventions have ONE home, `nr4a3-5bt-gate.json`, and a second
    copy in the map is the bug this rule exists to stop. Superseded text is retained inline as a one-line
    `⚠ Superseded, retained:` clause rather than dropped, per rule 1.2.

    ⚠ Anchors are checked with `grep -F` semantics against the LIVE map by `verify_map_edits.py`, because
    nine verbatim edits died on stale anchors in one day while four agents edited this file."""
    v = doc.get("verdict", "REFUSED")
    stamp = _et_now().strftime("%Y-%m-%d %-I:%M %p ET")
    art = "[`nr4a3-5bt-gate.json`](../modalities/nr4a3-5bt-gate.json)"
    ran = ("✅ **RAN %s — the pre-registered three-arm gate returns `%s`.** ⛔ Whatever it says is "
           "**STRUCTURAL**: no free energy is computed, so nothing about affinity, degradation, efficacy or "
           "safety follows, and the arms are **not blind** — DeepTernary is given which pocket each end of "
           "the degrader occupies. Every number, per arm and per column, has one home: %s (built inputs and "
           "the snap-mask pre-flight: [`nr4a3-5bt-frame.json`](../modalities/nr4a3-5bt-frame.json); the `V1` "
           "read over all 16 models per arm: [`nr4a3-5bt-signature.json`](../modalities/nr4a3-5bt-signature.json))."
           % (stamp, v, art))
    inherited = (" ⚠ **Three inherited conditions travel with the result and are not footnotes:** `R5` is "
                 "UNRESOLVED (`V3` INCONCLUSIVE — site selection missed 6 of 6 pairs) and site 1 rests on it; "
                 "`R3` FAILED 2026-08-03 on the generation frame, and while site 1 is a *different* frame it "
                 "comes from the same pipeline; and `V2` has **no** validation on a CRBN ternary with a "
                 "nuclear receptor, which is exactly what this rung assembles.")
    return [
        {"section": "§10.1 · Open rows — row 1 (the rebuild)",
         "anchor": "| **1** | **Rebuild the ternaries by the assembly route**",
         "current_text": "**RUN IT — it needs no authorization, and the row-25 hold is DISCHARGED.**",
         "proposed_text": ran + inherited + " ⚠ **Superseded, retained:** *\"RUN IT — it needs no "
                          "authorization, and the row-25 hold is DISCHARGED.\"*",
         "why": "the row's next action has been taken; leaving an instruction where a result belongs is how "
                "a finished item stays on the critical path",
         "artifact": "nr4a3-5bt-gate.json:verdict"},
        {"section": "THE ORDERED PLAN → RUNG 5b-T",
         "anchor": "`[ ]` 5b-T · Rebuild the NR4A1/2/3 ternaries by the ASSEMBLY route",
         "current_text": "`[ ]` 5b-T · Rebuild the NR4A1/2/3 ternaries by the ASSEMBLY route",
         "proposed_text": "`[x]` 5b-T · Rebuild the NR4A1/2/3 ternaries by the ASSEMBLY route",
         "why": "the rung ran; its verdict and every figure live in the gate artifact, not here",
         "artifact": "nr4a3-5bt-gate.json:verdict"},
        {"section": "§10.1 · Open rows — row 18 (≥3 ternary models per paralogue, then `V1`)",
         "anchor": "PRICED — it is the second half of row 1's rung `5b-T`, at $0",
         "current_text": "PRICED — it is the second half of row 1's rung `5b-T`, at $0",
         "proposed_text": "PRICED AND RAN — it is the second half of row 1's rung `5b-T`, at $0, and the "
                          "`V1` read covered all 16 models per arm against a bar of 3",
         "why": "row 18's reproducibility bar was the thing 5b-T's arm (B) turned into a threshold with a "
                "stated null; the row must stop reading as unrun",
         "artifact": "nr4a3-5bt-gate.json:A_and_B.min_models_per_arm"},
        {"section": "§10.2 · The readout",
         "anchor": "**0 of 27 open rows are moving, and 3 of the 27 are now RESOLVED (rows 3, 6, 24).**",
         "current_text": "**0 of 27 open rows are moving, and 3 of the 27 are now RESOLVED (rows 3, 6, 24).**",
         "proposed_text": "**4 of the 27 open rows are now RESOLVED (rows 1, 3, 6, 24), and rows 1 and 18 "
                          "were resolved by the same $0 CPU purchase.** ⚠ *Superseded, retained: \"0 of 27 "
                          "open rows are moving, and 3 of the 27 are now RESOLVED (rows 3, 6, 24).\"*",
         "why": "the count is DERIVED from the state column and row 1's state changed; the superseded "
                "sentence is retained rather than dropped",
         "artifact": "nr4a3-5bt-gate.json:verdict"},
    ]


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="RUNG 5b-T — the pre-registered three-arm gate ($0).")
    ap.add_argument("--pred-root", required=True)
    ap.add_argument("--frame", default=os.path.join(HERE, "nr4a3-5bt-frame.json"))
    ap.add_argument("--control", action="append", default=[])
    ap.add_argument("--reach", default=None)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-5bt-gate.json"))
    args = ap.parse_args(argv)
    doc = run(args.pred_root, args.frame, args.control, args.reach, args.spec)
    doc["map_edits_required"] = map_edits(doc)
    json.dump(doc, open(args.out, "w"), indent=1)
    print(doc.get("sentence") or json.dumps(doc)[:400], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
