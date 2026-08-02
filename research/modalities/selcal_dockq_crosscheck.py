#!/usr/bin/env python3
"""SECOND INSTRUMENT on the selcal co-fold-vs-crystal finding — canonical DockQ, run as a separate program.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ WHY A SECOND INSTRUMENT, AND WHY IT IS NOT A FUNCTION INSIDE THE FIRST ONE
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
`selcal_cofold_validate` measured all 12 co-folds at 17.8-21.2 Å from the deposited ternaries with fnat 0.000.
That is a strong claim, and it comes from an instrument that had **three** defects before they were caught,
every one of which returned a plausible number rather than an error:

  1. the deposited PROTAC shares an auth chain id with a protein chain, so the ligand was being counted as an
     interface residue (9DTX: 43 of 47 native contacts `unmappable`, arithmetically impossible for genuine
     protein-protein contacts — which is what exposed it);
  2. 9DTY holds ~10 copies at identity 1.000, so roles resolved by file order and could have built a chimeric
     reference across copies;
  3. contact-grouping cannot separate copies that touch in a lattice — it merged 39 of 40 chains into one.

Three silent defects in one instrument is the argument for not trusting its fourth answer either. So the check
is a **separate program running a separate implementation**: the canonical DockQ (Basu & Wallner), installed
from PyPI, sharing no code with `selcal_cofold_validate` — not its parser, not its chain mapper, not its
interface selector, not its superposition. If both say the co-folds do not reproduce the crystals, that is two
instruments; if they disagree, the first one is wrong and that must surface BEFORE anyone writes the number
down.

⚠ DEVIATION FROM THE PLAN, AND IT IS AN IMPROVEMENT: the plan named `DockQ/dockq_util.cal_dockq` from the
pinned DeepTernary clone. The PyPI `DockQ` is the same authors' reference implementation, needs none of the
clone's torch/dgl/mmengine stack, and is independent of the vendoring as well as of my code. Strictly more
independent and strictly cheaper, so it is what runs.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
⛔ WHAT MAY AND MAY NOT BE COMPARED — TWO RMSDs WITH THE SAME NAME ARE NOT THE SAME QUANTITY
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
  * **fnat is directly comparable.** Both compute the fraction of the native's inter-chain residue-residue
    contacts that the model reproduces, both at a **5.0 Å** heavy-atom cutoff. Same definition, same cutoff —
    so this is the sharp, definitionally-matched test, and it is the one the agreement verdict turns on.
  * **The two interface RMSDs are NOT comparable as numbers.** `selcal_cofold_validate` superposes on the
    WHOLE E3 Cα set (matching E1, deliberately, so its number can be read against E1's plateaux); DockQ's
    `iRMS` superposes on the interface residues alone. Different superposition, different quantity. They are
    reported side by side as CORROBORATION OF DIRECTION only — "both large" or "both small" — and this module
    never subtracts one from the other or calls their difference a discrepancy. Treating two same-named
    quantities as one number is the one-fact-one-place bug wearing a lab coat.
  * DockQ's own quality classes (Incorrect < 0.23 ≤ Acceptable < 0.49 ≤ Medium < 0.80 ≤ High) are the
    field's, not this program's, and are reported as DockQ emits them.

⛔ SCOPE. This grades INPUTS. It re-scores no leg, moves no threshold, amends no preregistration and emits no
tier. `selcal-verdict.json` remains the one home of the verdict, and the first instrument's artifact
(`selcal-cofold-vs-crystal.json`) is NOT overwritten — two instruments, two records, both readable.

Pure stdlib + a subprocess call to the DockQ CLI.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST_INSTRUMENT_JSON = os.path.join(HERE, "selcal-cofold-vs-crystal.json")
OUT_JSON = os.path.join(HERE, "selcal-cofold-dockq.json")

#: fnat is the definitionally-matched comparison. Both instruments use a 5.0 Å heavy-atom contact cutoff, so
#: this tolerance is about numerical/implementation noise, NOT about reconciling two different definitions.
FNAT_AGREEMENT_TOL = 0.10

#: Above this, both instruments are saying "the model does not reproduce the native interface". It is a
#: READING THRESHOLD for the agreement sentence, not a gate on anything, and no result is graded against it.
FAR_IRMSD_A = 5.0


def dockq_version():
    """The exact implementation being used, recorded rather than assumed."""
    try:
        import importlib.metadata as md
        return md.version("DockQ")
    except Exception:                                       # noqa: BLE001
        try:
            out = subprocess.run(["DockQ", "--help"], capture_output=True, text=True, timeout=60)
            return "unknown (CLI present, rc=%d)" % out.returncode
        except Exception as e:                              # noqa: BLE001
            return "UNAVAILABLE: %s" % e


def run_dockq(model_path, native_path, mapping=None, timeout=1800):
    """Run the DockQ CLI on one pair. Returns (parsed json | None, error | None).

    A failure is returned as an error string, never as a zero. An instrument that could not run must not
    render as an instrument that measured badly — the same rule the first instrument applies to a co-fold it
    could not read."""
    if not os.path.exists(model_path):
        return None, "model not found: %s" % model_path
    if not os.path.exists(native_path):
        return None, "native not found: %s" % native_path
    out_json = model_path + ".dockq.json"
    cmd = ["DockQ", model_path, native_path, "--json", out_json]
    if mapping:
        cmd += ["--mapping", mapping]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "DockQ timed out after %ds" % timeout
    except FileNotFoundError:
        return None, "the DockQ CLI is not installed on this runner"
    if not os.path.exists(out_json):
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return None, "DockQ wrote no json (rc=%d): %s" % (proc.returncode, " | ".join(tail[-4:]) or "no output")
    try:
        with open(out_json) as fh:
            return json.load(fh), None
    except Exception as e:                                  # noqa: BLE001
        return None, "DockQ json unreadable: %s" % e


def mapping_from_first_instrument(record):
    """`--mapping MODELCHAINS:NATIVECHAINS` built from the FIRST instrument's derived chain map.

    Supplying it deliberately, rather than letting DockQ align independently, is what makes this an
    apples-to-apples check: both instruments then score the SAME copy of a multi-copy asymmetric unit against
    the SAME role assignment. DockQ would otherwise be free to pick a different one of 9DTY's ~10 copies, and
    a disagreement would then be ambiguous between 'the measurement differs' and 'they scored different
    copies' — which is not a question worth manufacturing."""
    matched = ((record.get("chain_map") or {}).get("matched")) or {}
    if not matched:
        return None, "the first instrument recorded no chain map for this co-fold"
    model_chains = sorted(matched)
    native_chains = [matched[c]["native_chain"] for c in model_chains]
    if any(len(c) != 1 for c in model_chains + native_chains):
        return None, ("a chain id is not a single character (%s -> %s); DockQ's --mapping cannot express it"
                      % (model_chains, native_chains))
    return "%s:%s" % ("".join(model_chains), "".join(native_chains)), None


def best_interface(dockq_doc):
    """The scored interface with the highest DockQ, plus how many were scored.

    DockQ reports one entry per interface in the mapping. The target-E3 interface is the one this program is
    about, but naming it by chain letters would hard-code a convention; taking the BEST is conservative in the
    direction that matters — if even the best-reproduced interface is far from the native, no interface is
    close, and the conclusion cannot be an artifact of having looked at the wrong pair."""
    per = dockq_doc.get("best_result") or dockq_doc.get("interfaces") or {}
    if isinstance(per, dict) and per:
        items = []
        for name, v in per.items():
            if isinstance(v, dict) and "DockQ" in v:
                items.append((name, v))
        if items:
            name, v = max(items, key=lambda t: t[1].get("DockQ") or 0.0)
            return {"interface": name, "DockQ": v.get("DockQ"), "fnat": v.get("fnat"),
                    # DockQ 2.x spells these `iRMSD`/`LRMSD`; the older spelling is accepted too so a version
                    # bump degrades to a missing value rather than to a silent None that reads as zero.
                    "iRMS": _first(v, "iRMSD", "iRMS"), "LRMS": _first(v, "LRMSD", "LRMS"),
                    "nat_correct": v.get("nat_correct"), "nat_total": v.get("nat_total"),
                    "clashes": v.get("clashes"),
                    "n_interfaces_scored": len(items)}
    if "DockQ" in dockq_doc:                                # --short / single-interface shape
        return {"interface": "(single)", "DockQ": dockq_doc.get("DockQ"), "fnat": dockq_doc.get("fnat"),
                "iRMS": _first(dockq_doc, "iRMSD", "iRMS"), "LRMS": _first(dockq_doc, "LRMSD", "LRMS"),
                "n_interfaces_scored": 1}
    return None


def _first(d, *keys):
    for k in keys:
        if d.get(k) is not None:
            return d[k]
    return None


def quality_class(dockq):
    """DockQ's own CAPRI-style classes. The field's thresholds, not this program's."""
    if dockq is None:
        return None
    if dockq < 0.23:
        return "Incorrect"
    if dockq < 0.49:
        return "Acceptable"
    if dockq < 0.80:
        return "Medium"
    return "High"


def compare(first_record, dockq_best):
    """Do the two instruments tell the same story? Reported whichever way it lands.

    ⚠ Only `fnat` is compared as a NUMBER — same definition, same 5.0 Å cutoff in both. The two interface
    RMSDs are different quantities (whole-E3 superposition vs interface-only) and are carried side by side as
    direction only. Nothing here subtracts them."""
    mine_fnat = ((first_record.get("fnat") or {}).get("fnat"))
    mine_irmsd = first_record.get("interface_rmsd_to_crystal_A")
    if dockq_best is None:
        return {"agree": None, "why": "DockQ produced no scored interface — nothing to compare, and an "
                                      "instrument that did not run is not an instrument that disagreed"}
    their_fnat = dockq_best.get("fnat")
    their_irms = dockq_best.get("iRMS")
    out = {
        "fnat_first_instrument": mine_fnat,
        "fnat_dockq": their_fnat,
        "fnat_is_directly_comparable": "both compute the fraction of native inter-chain residue-residue "
                                       "contacts recovered, both at a 5.0 A heavy-atom cutoff",
        "interface_rmsd_first_instrument_A": mine_irmsd,
        "iRMS_dockq_A": their_irms,
        "rmsds_are_NOT_directly_comparable": "the first instrument superposes on the WHOLE E3 Ca set (matching "
                                             "E1, so its number reads against E1's plateaux); DockQ's iRMS "
                                             "superposes on interface residues alone. Different quantity, "
                                             "same name. Carried side by side as DIRECTION only; their "
                                             "difference is not a discrepancy and is never computed here.",
        "DockQ": dockq_best.get("DockQ"),
        "dockq_quality_class": quality_class(dockq_best.get("DockQ")),
    }
    if mine_fnat is None or their_fnat is None:
        out["agree"] = None
        out["why"] = "one instrument reported no fnat"
        return out
    out["fnat_abs_difference"] = round(abs(mine_fnat - their_fnat), 4)
    fnat_agrees = out["fnat_abs_difference"] <= FNAT_AGREEMENT_TOL
    both_far = (mine_irmsd is not None and their_irms is not None
                and mine_irmsd > FAR_IRMSD_A and their_irms > FAR_IRMSD_A)
    out["agree"] = bool(fnat_agrees)
    out["direction_corroborated"] = bool(both_far)
    out["why"] = ("fnat agrees within %.2f (|%.3f - %.3f| = %.3f)" % (FNAT_AGREEMENT_TOL, mine_fnat,
                                                                     their_fnat, out["fnat_abs_difference"])
                  if fnat_agrees else
                  "⛔ fnat DISAGREES beyond %.2f (|%.3f - %.3f| = %.3f) — the first instrument's number must "
                  "not be cited until this is root-caused" % (FNAT_AGREEMENT_TOL, mine_fnat, their_fnat,
                                                              out["fnat_abs_difference"]))
    return out


def crosscheck(cofold_root, native_dir, first_json=FIRST_INSTRUMENT_JSON, model_glob="*.cif"):
    """Run DockQ over every co-fold the first instrument graded, and compare."""
    import glob
    with open(first_json) as fh:
        first = json.load(fh)

    out = {
        "_what": "SECOND INSTRUMENT on selcal-cofold-vs-crystal.json — canonical DockQ (PyPI), a separate "
                 "program sharing no code with the first instrument.",
        "_why": "The first instrument had three defects that each returned a plausible number rather than an "
                "error before they were caught. Three silent defects is the argument for not trusting its "
                "fourth answer either.",
        "_licenses": "NOTHING about SMARCA2/4, NR4A3, degradation, efficacy or selectivity. It grades inputs. "
                     "It re-scores no leg, moves no threshold and emits no tier; selcal-verdict.json remains "
                     "the one home of the verdict, and selcal-cofold-vs-crystal.json is NOT overwritten.",
        "_only_fnat_is_compared_as_a_number": "same definition and same 5.0 A cutoff in both. The two "
                                              "interface RMSDs are different quantities with the same name "
                                              "and are reported side by side as direction only.",
        "dockq_version": dockq_version(),
        "first_instrument": os.path.basename(first_json),
        "records": [], "n_compared": 0, "n_agree": 0, "n_disagree": 0, "n_dockq_failed": 0,
    }

    for rec in first.get("records", []):
        if not rec.get("graded"):
            continue                                        # nothing to cross-check against
        system = rec.get("cofold_system")
        seed = rec.get("seed")
        pdb_id = (rec.get("native_pdb_id") or "").upper()
        sdir = os.path.join(cofold_root, str(system), "seed_%s" % seed)
        models = sorted(glob.glob(os.path.join(sdir, model_glob))) or \
            sorted(glob.glob(os.path.join(sdir, "**", model_glob), recursive=True))
        native_path = os.path.join(native_dir, "%s.cif" % pdb_id)
        row = {"arm_id": rec.get("arm_id"), "cofold_system": system, "seed": seed, "native_pdb_id": pdb_id}
        if not models:
            row.update({"dockq": None, "error": "no model under %s — unread, not disagreeing" % sdir})
            out["records"].append(row); out["n_dockq_failed"] += 1
            continue
        mapping, map_err = mapping_from_first_instrument(rec)
        row["mapping"] = mapping
        row["mapping_error"] = map_err
        doc, err = run_dockq(models[0], native_path, mapping=mapping)
        if err:
            row.update({"dockq": None, "error": err})
            out["records"].append(row); out["n_dockq_failed"] += 1
            continue
        best = best_interface(doc)
        row["dockq"] = best
        row["comparison"] = compare(rec, best)
        out["records"].append(row)
        out["n_compared"] += 1
        if row["comparison"].get("agree") is True:
            out["n_agree"] += 1
        elif row["comparison"].get("agree") is False:
            out["n_disagree"] += 1

    out["verdict"] = _overall(out)
    return out


def _overall(doc):
    """One plain sentence about whether the two instruments tell the same story."""
    n, a, d, f = doc["n_compared"], doc["n_agree"], doc["n_disagree"], doc["n_dockq_failed"]
    if n == 0:
        return {"instruments_agree": None,
                "sentence": "DockQ scored nothing (%d failures) — no cross-check was obtained. An instrument "
                            "that did not run is not an instrument that agreed." % f}
    if d == 0:
        dqs = [r["dockq"]["DockQ"] for r in doc["records"] if r.get("dockq") and r["dockq"].get("DockQ") is not None]
        return {"instruments_agree": True,
                "sentence": "Two independent instruments agree on all %d graded co-folds: DockQ %s, quality "
                            "class %s. The finding that the co-folds do not reproduce the deposited ternaries "
                            "is corroborated." % (n,
                                                  ("%.3f-%.3f" % (min(dqs), max(dqs))) if dqs else "n/a",
                                                  quality_class(max(dqs)) if dqs else "n/a"),
                "n_dockq_failed": f}
    return {"instruments_agree": False,
            "sentence": "⛔ THE TWO INSTRUMENTS DISAGREE on %d of %d co-folds. The first instrument's numbers "
                        "must not be cited until this is root-caused — a disagreement is a defect in one of "
                        "them, not a range to average." % (d, n),
            "n_dockq_failed": f}


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="DockQ cross-check of the selcal co-fold finding ($0 CPU).")
    ap.add_argument("--cofold-root", required=True)
    ap.add_argument("--native-dir", default=None)
    ap.add_argument("--first", default=FIRST_INSTRUMENT_JSON)
    ap.add_argument("--model-glob", default="*.cif")
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args(argv)
    native_dir = args.native_dir or os.path.join(args.cofold_root, "_native")

    res = crosscheck(args.cofold_root, native_dir, first_json=args.first, model_glob=args.model_glob)
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("[selcal-dockq] wrote %s" % args.out, flush=True)
    for r in res["records"]:
        if r.get("dockq"):
            c = r["comparison"]
            print("  %-16s seed %-2s DockQ=%.4f (%s)  fnat: mine=%s dockq=%s  iRMS=%.2f A  agree=%s"
                  % (r["arm_id"], r["seed"], r["dockq"]["DockQ"] or 0.0,
                     quality_class(r["dockq"]["DockQ"]), c.get("fnat_first_instrument"),
                     c.get("fnat_dockq"), r["dockq"].get("iRMS") or float("nan"), c.get("agree")), flush=True)
        else:
            print("  %-16s seed %-2s DockQ FAILED — %s" % (r["arm_id"], r["seed"], r.get("error")), flush=True)
    print("\n[selcal-dockq] %s" % res["verdict"]["sentence"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
