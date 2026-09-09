#!/usr/bin/env python3
"""PARKED-MODALITIES-1 — build the parked-modality reason ledger from committed graph bytes.

Read-only outside this lane. stdlib only. No network, no GPU, no paid API.
Every verdict cell is derived from a named committed file; nothing is asserted from memory.
"""
import json, hashlib, os, sys

ROOT = "/home/user/Rare-cancers"
OUT = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "PUB-PARKED-MODALITIES"


def load(rel):
    p = os.path.join(ROOT, rel)
    b = open(p, "rb").read()
    return json.loads(b), hashlib.sha256(b).hexdigest()


routes, h_routes = load("systems/graph/routes.json")
pubs, h_pubs = load("systems/graph/publications.json")
techs, h_techs = load("systems/graph/technologies.json")
insts, h_insts = load("systems/graph/instruments.json")
blocks, h_blocks = load("systems/graph/blockers.json")
decoy, h_decoy = load("research/modalities/selcal-dockq-decoy-scale.json")
census, h_census = load("research/modalities/instrument-census.json")

byid = lambda seq: {x["id"]: x for x in seq}
T, I, B = byid(techs), byid(insts), byid(blocks)

parked = [r for r in routes
          if isinstance(r.get("publication"), dict)
          and r["publication"].get("endpoint") == ENDPOINT]
parked.sort(key=lambda r: r["id"])

# ---------------------------------------------------------------- re-derivation 1
# instrument-census.json (V12 row) asserts: "DockQ 0.023-0.046 ~= true structure moved 32 A".
# Re-derive that 32 A from the decoy ladder it summarises, before any verdict leans on it.
lo, hi = decoy["cofold_DockQ_range"]
ladder = [(p["requested_rmsd_A"], p["DockQ"]["median"], p["DockQ"]["max"]) for p in decoy["points"]]
matching = [d for d, med, mx in ladder if med <= hi]
rederived = min(matching) if matching else None
bracket_lo = max([d for d, med, mx in ladder if med > hi], default=None)
recheck = {
    "asserted_in": "research/modalities/instrument-census.json ('DockQ 0.023-0.046 = true structure moved 32 A')",
    "asserted_displacement_A": decoy["displacement_matching_cofolds_A"],
    "cofold_DockQ_range": [lo, hi],
    "ladder_requested_rmsd_A_vs_median_DockQ": [[d, med] for d, med, mx in ladder],
    "rederived_first_rung_with_median_at_or_below_best_cofold_A": rederived,
    "reproduces": rederived == decoy["displacement_matching_cofolds_A"],
    "limitation": (
        "The ladder is a doubling series (0/0.5/1/2/4/8/16/32 A). The rung at %s A has median DockQ "
        "%s > best co-fold %s, so the displacement that actually matches the co-folds lies in the "
        "OPEN INTERVAL (%s, %s] A. '32 A' is the coarsest matching RUNG, not an estimated displacement, "
        "and no interpolation or uncertainty is published for it."
        % (bracket_lo,
           [med for d, med, mx in ladder if d == bracket_lo][0],
           hi, bracket_lo, rederived)
    ),
    "not_established": (
        "Nothing here is an efficacy, safety, selectivity, therapeutic-window or clinical-readiness "
        "statement. It is one instrument's failure to rebuild one deposited ternary from sequence + ligand."
    ),
}

# ---------------------------------------------------------------- scope test
# A parking reason is OVER-SCOPED when the route asserts a GLOBAL absence while the record that
# OWNS the capability records something weaker. Test that mechanically where an owner exists.
GLOBAL_ABSENCE_MARKERS = [
    "nobody has", "the field has not", "no design method", "nothing to report until",
    "the field has largely moved on", "no modern", "has not solved", "does not exist",
]

def route_prose(r):
    parts = []
    for k in ("closure_note", "rationale", "purpose"):
        if isinstance(r.get(k), str):
            parts.append((k, r[k]))
    rd = r.get("readiness", {})
    for k in ("why_not_higher",):
        if isinstance(rd.get(k), str):
            parts.append(("readiness." + k, rd[k]))
    for i, u in enumerate(r.get("remaining_unknowns", []) or []):
        parts.append(("remaining_unknowns[%d]" % i, u))
    for i, m in enumerate((rd.get("missing") or [])):
        parts.append(("readiness.missing[%d]" % i, m))
    g = r.get("grade")
    if isinstance(g, dict) and isinstance(g.get("value"), str):
        parts.append(("grade.value", g["value"]))
    return parts

def owning_tech_states(r):
    out = {}
    for t in techs:
        if r["id"] in (t.get("unblocks", {}) or {}).get("routes", []):
            out[t["id"]] = {
                "current_state": t.get("current_state"),
                "confidence": t.get("confidence"),
                "evidence": t.get("evidence"),
                "ungraded_pending_signals": sum(
                    1 for s in (t.get("pending_signals") or []) if s.get("graded") is False),
                "newest_ungraded_signal_seen_on": max(
                    [s.get("seen_on") for s in (t.get("pending_signals") or [])
                     if s.get("graded") is False] or [None]),
            }
    return out

rows = []
for r in parked:
    prose = route_prose(r)
    flagged = [{"field": k, "text": v,
                "marker": [m for m in GLOBAL_ABSENCE_MARKERS if m in v.lower()]}
               for k, v in prose if any(m in v.lower() for m in GLOBAL_ABSENCE_MARKERS)]
    blockers = {b: {"kind": B[b].get("kind"),
                    "has_evidence_field": "evidence" in B[b],
                    "owner": B[b].get("owner")} for b in r.get("blockers_inherited", []) if b in B}
    rows.append({
        "route": r["id"],
        "display_name": r.get("display_name"),
        "state": r.get("state", {}).get("status"),
        "state_last_verified": r.get("state", {}).get("last_verified"),
        "route_artifacts": r.get("artifacts"),
        "route_evidence": r.get("evidence"),
        "instruments": r.get("instruments"),
        "blockers_inherited": blockers,
        "owning_technology_records": owning_tech_states(r),
        "global_absence_phrasing_found": flagged,
    })

endpoint = [p for p in pubs if p["id"] == ENDPOINT][0]

manifest = {
    "_what": ("Derived inputs for the PARKED-MODALITIES-1 reason ledger. Machine-derived fields only; "
              "the human verdicts live in parked-modality-reason-ledger.json beside this."),
    "generated": "2026-09-09",
    "lane": "PARKED-MODALITIES-1",
    "campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
    "input_sha256": {
        "systems/graph/routes.json": h_routes,
        "systems/graph/publications.json": h_pubs,
        "systems/graph/technologies.json": h_techs,
        "systems/graph/instruments.json": h_insts,
        "systems/graph/blockers.json": h_blocks,
        "research/modalities/selcal-dockq-decoy-scale.json": h_decoy,
        "research/modalities/instrument-census.json": h_census,
    },
    "endpoint": {
        "id": endpoint["id"],
        "state": endpoint.get("state"),
        "document_file": (endpoint.get("document") or {}).get("file"),
        "why_not_written": endpoint.get("why_not_written"),
        "outcome_potential_why": endpoint.get("outcome_potential_why"),
        "blocked_by": endpoint.get("blocked_by"),
    },
    "n_parked_routes": len(parked),
    "number_recheck_v12_32A": recheck,
    "routes": rows,
}
json.dump(manifest, open(os.path.join(OUT, "parked-modality-derived-inputs.json"), "w"), indent=2)

print("parked routes reached from %s : %d" % (ENDPOINT, len(parked)))
for r in rows:
    print("  %-18s status=%-7s artifacts=%s evidence=%s  global-absence-phrases=%d"
          % (r["route"], r["state"], r["route_artifacts"], r["route_evidence"],
             len(r["global_absence_phrasing_found"])))
    for t, s in r["owning_technology_records"].items():
        print("      owner %-24s current_state=%-18s confidence=%-8s ungraded_signals=%d (newest %s)"
              % (t, s["current_state"], s["confidence"], s["ungraded_pending_signals"],
                 s["newest_ungraded_signal_seen_on"]))
print()
print("V12 32 A recheck: asserted=%s  rederived=%s  reproduces=%s"
      % (recheck["asserted_displacement_A"], recheck["rederived_first_rung_with_median_at_or_below_best_cofold_A"],
         recheck["reproduces"]))
print("bracket: " + recheck["limitation"])
