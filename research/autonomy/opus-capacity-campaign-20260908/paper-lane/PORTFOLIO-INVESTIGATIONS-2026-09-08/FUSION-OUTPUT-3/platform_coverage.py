#!/usr/bin/env python3
"""Platform-readability determination for the FUSION-OUTPUT-2 pre-registered gene sets.

WHAT THIS DOES. FUSION-OUTPUT-2 froze six gene sets (contrast A and B at 1000/2000/5000 bp
promoter windows) and declared, as prerequisite S2, that each set must clear TWO floors on a
platform before it may be scored there: coverage >= 0.4 AND >= 4 readable genes. It recorded
GPL6244 coverage as 1 by construction and GPL3290 coverage as UNKNOWN OFFLINE. This script
resolves both from artifacts already in this checkout. No network. No expression value is read:
the only fields consumed are symbol keys, probe identifiers, and boolean readability flags.
No contrast is computed and no biological claim is made.

GPL6244 (GSE24369). Authoritative: the frozen source packet's own symbol -> probe map, the same
file `array_coverage.py` in that packet used. Membership in that map IS readability on GPL6244.

GPL3290 (GSE4303). NO platform table and NO EST-accession -> symbol bridge exists offline in this
checkout: the bridge is constructed at run time by `_gpl_symbols()` in
research/modalities/emc_atr_vulnerability.py, which fetches GEO acc.cgi / annot / SOFT over the
network. What DOES exist offline is per-symbol readability recorded by earlier committed runs of
that bridge. This script harvests every such record and grades each set as a BOUNDED interval:

  known_readable  - a committed run recorded this symbol as carrying a GPL3290 probe
  known_unreadable- a committed run recorded this symbol as NOT readable on GPL3290
  unknown         - no committed run touched this symbol; its status cannot be settled offline

  coverage_lower = known_readable / n          (every unknown assumed unreadable)
  coverage_upper = (n - known_unreadable) / n  (every unknown assumed readable)

Verdict per cell:
  PASSES BOTH FLOORS   coverage_lower >= 0.4 and known_readable >= 4
  FAILS COVERAGE       coverage_upper <  0.4
  FAILS GENE COUNT     (n - known_unreadable) < 4
  UNDETERMINABLE OFFLINE  otherwise (the interval straddles a floor)

A floor is never lowered here. An interval that straddles a floor is reported as undetermined,
not resolved in either direction.
"""
import hashlib
import math
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[5]
PREREG = HERE.parent / "FUSION-OUTPUT-2" / "fusion-program-testsets.json"
GPL6244_MAP = pathlib.Path(
    "/tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/"
    "nr4a3-program-source-2026-09-07/sources/GPL6244-gene-to-probes.json")
GPL3290_KEY = "GSE4303-GPL3290_series_matrix.txt.gz"
GPL6244_KEY = "GSE24369_series_matrix.txt.gz"

MIN_COVERAGE = 0.4
MIN_READABLE = 4

inputs = []


def load(path, note):
    p = pathlib.Path(path)
    if not p.exists():
        inputs.append({"path": str(p), "note": note, "exists": False})
        return None
    raw = p.read_bytes()
    inputs.append({"path": str(p), "note": note, "exists": True,
                   "bytes": len(raw),
                   "sha256": hashlib.sha256(raw).hexdigest()})
    return json.loads(raw.decode("utf-8"))


# ---------------------------------------------------------------- the frozen sets
sets_doc = load(PREREG, "FUSION-OUTPUT-2 frozen gene sets (the object under test)")
if sets_doc is None:
    sys.exit("missing pre-registered gene sets")
CELLS = {}
for window, wd in sets_doc["windows"].items():
    for contrast in ("A", "B"):
        CELLS[(window, contrast)] = list(wd[f"contrast_{contrast}_set"]["genes"])

# ---------------------------------------------------------------- GPL6244 truth
g6244 = load(GPL6244_MAP, "frozen source packet symbol->probe map for GPL6244 (authoritative)")
gpl6244_symbols = set(g6244) if g6244 else set()

# ---------------------------------------------------------------- GPL3290 evidence
readable = {}      # symbol -> list of provenance strings
unreadable = {}


def note_readable(sym, src):
    readable.setdefault(sym.upper(), []).append(src)


def note_unreadable(sym, src):
    unreadable.setdefault(sym.upper(), []).append(src)


panels = load(REPO / "research/modalities/emc-expression-panels.json",
              "committed run of the GPL3290 EST-accession bridge: per-gene readability flags, "
              "and the seeded background draw whose members are by definition probe-carrying")
if panels:
    for sym, per in panels.get("gene_reads", {}).items():
        rec = per.get(GPL3290_KEY)
        if isinstance(rec, dict) and "readable" in rec:
            (note_readable if rec["readable"] else note_unreadable)(
                sym, "emc-expression-panels.json#gene_reads")
    bg = panels.get("background_reads", {}).get(GPL3290_KEY, {})
    for sym in (bg.get("z") or {}):
        note_readable(sym, "emc-expression-panels.json#background_reads(seeded draw)")

fus = load(REPO / "research/modalities/nr4a3-fusion-targets.json",
           "committed run of the same bridge: per-gene readability for the fusion target panel")
if fus:
    for sym, per in (fus.get("gene_reads") or {}).items():
        rec = per.get(GPL3290_KEY)
        if isinstance(rec, dict) and "readable" in rec:
            (note_readable if rec["readable"] else note_unreadable)(
                sym, "nr4a3-fusion-targets.json#gene_reads")

census = load(REPO / "research/modalities/census-route-expression-grading.json",
              "committed run of the same bridge: per-route gene readability")
if census:
    for route, rd in (census.get("routes") or {}).items():
        for sym, per in (rd.get("genes") or {}).items():
            rec = per.get(GPL3290_KEY) if isinstance(per, dict) else None
            if isinstance(rec, dict) and "readable" in rec:
                (note_readable if rec["readable"] else note_unreadable)(
                    sym, f"census-route-expression-grading.json#routes/{route}")

# a symbol recorded both ways: keep the positive, flag it
conflicts = sorted(set(readable) & set(unreadable))
for s in conflicts:
    unreadable.pop(s, None)

frame_n = None
if panels:
    bg = panels.get("background_reads", {}).get(GPL3290_KEY, {})
    frame_n = bg.get("n_frame")
    drawn = bg.get("n_drawn")
else:
    drawn = None

# ---------------------------------------------------------------- grade
def grade(genes, universe_known_readable, universe_known_unreadable, exact):
    n = len(genes)
    up = [g for g in genes if g.upper() in universe_known_readable]
    un = [g for g in genes if g.upper() in universe_known_unreadable]
    unk = [g for g in genes if g.upper() not in universe_known_readable
           and g.upper() not in universe_known_unreadable]
    lo = len(up) / n
    hi = (n - len(un)) / n
    if exact:
        verdict = ("PASSES BOTH FLOORS" if (lo >= MIN_COVERAGE and len(up) >= MIN_READABLE)
                   else "FAILS COVERAGE" if lo < MIN_COVERAGE else "FAILS GENE COUNT")
    elif hi < MIN_COVERAGE:
        verdict = "FAILS COVERAGE"
    elif (n - len(un)) < MIN_READABLE:
        verdict = "FAILS GENE COUNT"
    elif lo >= MIN_COVERAGE and len(up) >= MIN_READABLE:
        verdict = "PASSES BOTH FLOORS"
    else:
        verdict = "UNDETERMINABLE OFFLINE"
    return {
        "n": n,
        "n_known_readable": len(up),
        "n_known_unreadable": len(un),
        "n_unknown_offline": len(unk),
        "coverage_lower_bound": round(lo, 4),
        "coverage_upper_bound": round(hi, 4),
        "coverage_exact": round(lo, 4) if exact else None,
        "readable_genes": sorted(up),
        "unreadable_genes": sorted(un),
        "unknown_genes": sorted(unk),
        "verdict": verdict,
        # The two floors are separable: the >=4-readable-gene floor can be SETTLED by positive
        # evidence alone (4 named readable genes clear it no matter what the unknowns are), while
        # the 0.4 coverage floor needs the denominator's unknowns resolved.
        "gene_count_floor_status": ("MET - settled by named readable genes" if len(up) >= MIN_READABLE
                                    else "FAILED - settled" if (n - len(un)) < MIN_READABLE
                                    else "UNSETTLED OFFLINE"),
        "coverage_floor_status": ("MET - settled" if lo >= MIN_COVERAGE
                                  else "FAILED - settled" if hi < MIN_COVERAGE
                                  else "UNSETTLED OFFLINE"),
    }


result = {
    "artifact": "platform-readability determination for the FUSION-OUTPUT-2 pre-registered sets",
    "status": "COVERAGE / FEASIBILITY ONLY - no expression value read, no contrast computed, "
              "no biological claim",
    "floors_applied_verbatim": {"min_coverage": MIN_COVERAGE,
                                "min_readable_genes": MIN_READABLE,
                                "source": "manuscript PUB-FUSION-OUTPUT Sec 2.3, restated in "
                                          "FUSION-OUTPUT-2 PRE-REGISTRATION.md Sec 3 and Sec 6.1; "
                                          "NOT modified here"},
    "inputs": inputs,
    "platforms": {},
}

result["platforms"]["GPL6244"] = {
    "series": "GSE24369",
    "determination_kind": "EXACT",
    "basis": "membership in the frozen source packet's own GPL6244 symbol->probe map "
             "(%d symbols); this is the universe the memberships were built on" % len(gpl6244_symbols),
    "n_symbols_in_map": len(gpl6244_symbols),
    "cells": {},
}
for (window, contrast), genes in sorted(CELLS.items()):
    result["platforms"]["GPL6244"]["cells"]["%s/%s" % (window, contrast)] = grade(
        genes, gpl6244_symbols, set(), exact=True)

result["platforms"]["GPL3290"] = {
    "series": "GSE4303",
    "determination_kind": "BOUNDED - no offline platform table or EST-accession bridge exists",
    "why_not_exact": "The GPL3290 probe->symbol bridge is built at run time by _gpl_symbols() in "
                     "research/modalities/emc_atr_vulnerability.py from GEO "
                     "(acc.cgi view=full, then the .annot.gz, then the family SOFT), plus an "
                     "accession->symbol resolution step. No copy of the GPL3290 platform table, "
                     "no accession->symbol dictionary and no list of the ~14,9xx bridged symbols "
                     "is committed anywhere in this checkout or in the frozen corpus. Only "
                     "per-symbol readability recorded by earlier committed runs survives offline.",
    "offline_evidence_scale": {
        "bridged_symbol_frame_size_recorded_by_the_committed_run": frame_n,
        "symbols_of_that_frame_named_in_the_committed_seeded_draw": drawn,
        "distinct_symbols_with_an_offline_readability_record": len(readable) + len(unreadable),
        "n_recorded_readable": len(readable),
        "n_recorded_unreadable": len(unreadable),
        "conflicting_records_resolved_as_readable": conflicts,
    },
    "cells": {},
}
for (window, contrast), genes in sorted(CELLS.items()):
    result["platforms"]["GPL3290"]["cells"]["%s/%s" % (window, contrast)] = grade(
        genes, set(readable), set(unreadable), exact=False)

result["provenance_of_each_gpl3290_call"] = {
    sym: sorted(set(src)) for sym, src in sorted(readable.items())
    if any(sym in [g.upper() for g in genes] for genes in CELLS.values())
}
result["provenance_of_each_gpl3290_negative"] = {
    sym: sorted(set(src)) for sym, src in sorted(unreadable.items())
    if any(sym in [g.upper() for g in genes] for genes in CELLS.values())
}

# ---------------------------------------------------------------- capture-recapture estimator
# THIS DOES NOT CHANGE ANY VERDICT ABOVE. It is a separate, clearly labelled statistical estimate.
#
# The committed run drew a SEEDED UNIFORM RANDOM sample of n_drawn symbols from the frame of
# n_frame symbols that carry a GPL3290 probe. For a gene that IS in the frame, the probability of
# appearing in that draw is p = n_drawn / n_frame. So for a set of n genes of which c*n are in the
# frame, the expected number appearing in the draw is c * n * p, and k / (n * p) estimates c.
# Assumptions, all of them load-bearing: (i) the draw is uniform over the frame and independent of
# any property of our genes; (ii) our genes were selected by promoter accessibility, not by array
# membership, so they are exchangeable with the frame with respect to the draw. Genes that carry a
# NON-random readability record (the biology-selected panels) are excluded from this estimator's
# numerator and denominator, because they were not sampled at random.
draw_syms = set()
panel_syms = set()
if panels:
    bg = panels.get("background_reads", {}).get(GPL3290_KEY, {})
    draw_syms = {s.upper() for s in (bg.get("z") or {})}
    panel_syms = {s.upper() for s in panels.get("gene_reads", {})}
if fus:
    panel_syms |= {s.upper() for s in (fus.get("gene_reads") or {})}
if census:
    for route, rd in (census.get("routes") or {}).items():
        panel_syms |= {s.upper() for s in (rd.get("genes") or {})}
panel_syms -= draw_syms

est = {
    "_what_this_is": "A STATISTICAL ESTIMATE, NOT A DETERMINATION. It does not open a floor, does "
                     "not change any verdict above, and cannot substitute for the platform table.",
    "p_detect_if_in_frame": None,
    "n_frame": frame_n,
    "n_drawn": drawn,
    "cells": {},
}
if frame_n and drawn:
    p = drawn / frame_n
    est["p_detect_if_in_frame"] = round(p, 5)
    for (window, contrast), genes in sorted(CELLS.items()):
        elig = [g for g in genes if g.upper() not in panel_syms]
        k = sum(1 for g in elig if g.upper() in draw_syms)
        n_e = len(elig)
        chat = (k / (n_e * p)) if n_e else None
        est["cells"]["%s/%s" % (window, contrast)] = {
            "n_eligible_for_the_estimator": n_e,
            "n_excluded_as_non_randomly_recorded": len(genes) - n_e,
            "k_in_the_seeded_draw": k,
            "point_estimate_of_frame_coverage": (round(min(chat, 1.0), 3)
                                                 if chat is not None else None),
            "point_estimate_uncapped": round(chat, 3) if chat is not None else None,
            "expected_k_if_coverage_were_the_0.4_floor": (round(0.4 * n_e * p, 2)
                                                          if n_e else None),
            "expected_k_if_coverage_were_1.0": round(n_e * p, 2) if n_e else None,
            # One-sided exact binomial tail against H0: frame coverage is exactly the 0.4 floor.
            # Under H0 each eligible gene appears in the draw with probability 0.4 * p, so
            # P(K >= k) is the evidence against "this set sits at the floor". This is a test of a
            # sampling hypothesis, NOT a coverage measurement, and it does not open the gate.
            "p_one_sided_against_H0_coverage_equals_0.4": (
                round(sum(math.comb(n_e, j) * (0.4 * p) ** j * (1 - 0.4 * p) ** (n_e - j)
                          for j in range(k, n_e + 1)), 5) if n_e else None),
        }
result["gpl3290_frame_coverage_estimate_from_the_seeded_random_draw"] = est

out = HERE / "platform-coverage.json"
out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")

for plat in ("GPL6244", "GPL3290"):
    print("== %s (%s) %s" % (plat, result["platforms"][plat]["series"],
                             result["platforms"][plat]["determination_kind"]))
    for cell, r in sorted(result["platforms"][plat]["cells"].items()):
        print("  %-12s n=%-3d readable>=%-3d cov[%.3f,%.3f]  %s"
              % (cell, r["n"], r["n_known_readable"], r["coverage_lower_bound"],
                 r["coverage_upper_bound"], r["verdict"]))
print("wrote", out)
