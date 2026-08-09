#!/usr/bin/env python3
"""What a symptom-directed intervention would be worth in EMC, and why that is a band.

THE ARITHMETIC. For each mechanism of death:

    survival gain  ~  attributable fraction of deaths
                      x  relative effect of the intervention
                      x  transferability

The first factor comes from the terminal-event corpus, the second from a published
trial, and the third is a judgement that is DECLARED rather than folded silently into
the product. Multiplying three uncertain numbers produces a fourth that looks precise,
so nothing here returns a point estimate: every row is a range with its three inputs
still attached and separately readable.

⛔ THE GUARD THAT MATTERS MOST IS NOT IN THE ARITHMETIC. Every effect size carries a
PMID, and this script REFUSES TO RUN if that PMID does not appear in the retrieved
Europe PMC probe artifact. That is not bureaucracy. CLAUDE.md section 7 records the
measured failure it exists to stop: an agent drafting a manuscript wrote a citation from
recollection, the PMID was present in no committed source anywhere in this repository,
and it PASSED `lint_claims` TWICE -- because claim strength and citation provenance are
orthogonal, and a properly hedged sentence resting on an invented identifier is a
perfect sentence to a linter that only reads hedging. A human-directed audit caught it.
Nothing automatic could have.

So the anchor here is mechanical: a fetch happened, the identifier came back in it, and
this script can see that. ⚠ AN ANCHORED PMID IS NOT THEREBY A VERIFIED CLAIM -- the
artifact is evidence that a paper was retrieved, never that it says what a row asserts.
This raises the floor. It is not a truth oracle.

Inputs:  research/manuscripts/emc-supportive-effect-inputs.json   (effect sizes + PMIDs)
         research/literature/emc-mortality-probe.json             (the retrieval, the anchor)
         research/manuscripts/emc-mortality-decomposition.json    (the ceiling)
         research/manuscripts/emc-terminal-events.json            (mechanism fractions, optional)
Output:  research/manuscripts/emc-supportive-effect-transfer.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
INPUTS = ROOT / "research/manuscripts/emc-supportive-effect-inputs.json"
PROBE = ROOT / "research/literature/emc-mortality-probe.json"
DECOMP = ROOT / "research/manuscripts/emc-mortality-decomposition.json"
EVENTS = ROOT / "research/manuscripts/emc-terminal-events.json"
OUT = ROOT / "research/manuscripts/emc-supportive-effect-transfer.json"

# How much of an effect measured elsewhere is carried across. Declared, never computed --
# there is no data that would let this be estimated for EMC, and a number produced by a
# formula would disguise a judgement as a measurement.
TRANSFER = {
    "direct":        (1.00, 1.00, "measured in this disease"),
    "close":         (0.50, 1.00, "measured in a population resembling this one in survival and burden"),
    "distant":       (0.20, 0.80, "measured in a population differing materially -- most often far shorter survival"),
    "speculative":   (0.00, 0.50, "no population resembling this one has been studied; the transfer is an assumption"),
    "unretrieved":   (0.00, 0.00, "no effect size has been retrieved; nothing is claimed"),
}


def anchored_pmids(probe: dict) -> set[str]:
    """Every PMID the retrieval actually returned, from either half of the artifact."""
    found: set[str] = set()
    for entry in (probe.get("queries") or {}).values():
        for hit in entry.get("hits") or []:
            if hit.get("pmid"):
                found.add(str(hit["pmid"]))
    for row in probe.get("oa_corpus") or []:
        if row.get("pmid"):
            found.add(str(row["pmid"]))
    for row in probe.get("terminal_events") or []:
        if row.get("pmid"):
            found.add(str(row["pmid"]))
    return found


def check_anchors(spec: dict, probe: dict) -> list[str]:
    """⛔ The gate. An effect size whose PMID never came back from a fetch does not run."""
    have = anchored_pmids(probe)
    problems = []
    for row in spec.get("interventions", []):
        if row.get("transferability") == "unretrieved":
            continue                      # claims nothing, so anchors nothing
        pmid = str(row.get("pmid") or "")
        if not re.fullmatch(r"\d{6,9}", pmid):
            problems.append(
                f"{row['id']}: no usable PMID ({pmid!r}). An effect size with no identifier "
                f"cannot be anchored and must be recorded as `unretrieved` instead.")
            continue
        if pmid not in have:
            problems.append(
                f"{row['id']}: PMID {pmid} does not appear anywhere in the retrieved probe "
                f"artifact. Either the retrieval did not return it -- in which case this row "
                f"is `unretrieved` -- or the identifier was written from recollection, which "
                f"is the failure this gate exists to stop.")
    return problems


def band(fraction: float, effect_lo: float, effect_hi: float, transfer: str) -> dict:
    t_lo, t_hi, t_note = TRANSFER[transfer]
    return {
        "attributable_fraction_of_deaths": round(fraction, 4),
        "relative_effect_range": [effect_lo, effect_hi],
        "transferability": transfer,
        "transferability_multiplier_range": [t_lo, t_hi],
        "transferability_note": t_note,
        "implied_share_of_deaths_averted_range": [
            round(fraction * effect_lo * t_lo, 4),
            round(fraction * effect_hi * t_hi, 4),
        ],
    }


def main() -> int:
    if not INPUTS.exists():
        print(f"no inputs at {INPUTS.relative_to(ROOT)} -- nothing to compute yet.", file=sys.stderr)
        print("This is the expected state until the retrieval has been READ. The inputs file "
              "is written by hand from retrieved hits, never from recollection.", file=sys.stderr)
        return 2
    if not PROBE.exists():
        print(f"no probe artifact at {PROBE.relative_to(ROOT)} -- the anchor check cannot run, "
              f"so nothing is computed.", file=sys.stderr)
        return 2

    spec = json.loads(INPUTS.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))

    problems = check_anchors(spec, probe)
    if problems:
        print("UNANCHORED EFFECT SIZES -- refusing to compute:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    decomp = json.loads(DECOMP.read_text(encoding="utf-8")) if DECOMP.exists() else {}
    events = json.loads(EVENTS.read_text(encoding="utf-8")) if EVENTS.exists() else {}
    fractions = (events.get("mechanism_fractions") or {}) if events else {}

    rows = []
    for row in spec.get("interventions", []):
        mech = row["mechanism"]
        frac = fractions.get(mech, {}).get("fraction_of_classified_deaths")
        if frac is None:
            rows.append({
                "id": row["id"], "intervention": row["intervention"], "mechanism": mech,
                "status": "MECHANISM_FRACTION_UNKNOWN",
                "why": ("the terminal-event corpus has not been classified for this mechanism, "
                        "so there is no attributable fraction to multiply and no band is stated"),
                "pmid": row.get("pmid"),
                "measured_in": row.get("measured_in"),
            })
            continue
        rows.append({
            "id": row["id"], "intervention": row["intervention"], "mechanism": mech,
            "status": "COMPUTED",
            "pmid": row.get("pmid"),
            "measured_in": row.get("measured_in"),
            "endpoint": row.get("endpoint"),
            "caveat": row.get("caveat"),
            **band(frac, row["relative_effect_lo"], row["relative_effect_hi"],
                   row["transferability"]),
        })

    within = (decomp.get("within_series") or [{}])[0]
    payload = {
        "_readme": (
            "What a symptom-directed intervention would be worth in EMC. Every row is a BAND "
            "with its three inputs separately readable, because a point estimate formed by "
            "multiplying three uncertain numbers hides all three. Every effect size is "
            "anchored to a PMID that appears in the committed retrieval artifact; the script "
            "refuses to run otherwise. An anchored identifier means a fetch returned it, NOT "
            "that the paper supports the row -- this raises the floor and is not a truth "
            "oracle. Nothing here asserts efficacy, safety, a therapeutic window or clinical "
            "readiness in EMC, and every effect was measured in some other disease."
        ),
        "generated_by": "research/manuscripts/emc_supportive_effect_transfer.py",
        "anchor_source": "research/literature/emc-mortality-probe.json",
        "anchored_pmids_available": len(anchored_pmids(probe)),
        "ceiling_context": {
            "antitumour_ceiling_pct_points_at_10y": within.get("antitumour_ceiling_pct_points"),
            "competing_share_of_deaths_pct_at_10y": within.get("competing_share_of_deaths_pct"),
            "source": "research/manuscripts/emc-mortality-decomposition.json (within-series)",
            "why_it_is_here": (
                "Any gain computed below has to be read against what the antitumour portfolio "
                "itself could achieve at best. A supportive intervention that looks small in "
                "isolation may not be small relative to a ceiling of this size."
            ),
        },
        "transferability_scale": {k: {"multiplier_range": [v[0], v[1]], "means": v[2]}
                                  for k, v in TRANSFER.items()},
        "interventions": rows,
        "limits": [
            "Every effect size was measured in a different disease, in populations with far shorter survival than EMC's. The transferability multiplier is a declared judgement, not a measurement, and it dominates every band here.",
            "An attributable fraction from a case-report corpus is a convenience sample: dramatic terminal events are over-represented and ordinary decline is under-reported.",
            "A share of deaths averted is not a gain in overall survival. Converting one to the other needs a time horizon and a competing-risks structure this analysis does not have.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(rows)} intervention(s), "
          f"{sum(1 for r in rows if r['status'] == 'COMPUTED')} computed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
