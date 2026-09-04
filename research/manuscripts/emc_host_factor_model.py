#!/usr/bin/env python3
"""What treating a common, independently treatable condition would be worth in EMC.

THE IDEA (trimcrae, 2026-08-09). If being obese raises the chance of dying after an EMC
diagnosis, then a GLP-1 receptor agonist is a de-facto EMC survival drug for the obese
patient -- no EMC biology required, no molecule to discover, and the drug already exists.
The same shape applies to smoking, hypertension, diabetes and deconditioning.

⛔ THE MODEL'S WHOLE STRUCTURE IS ONE DISTINCTION, BECAUSE COLLAPSING IT IS HOW THIS
ARGUMENT GOES WRONG. Mortality after an EMC diagnosis has two compartments and a host
factor acts on them through completely different evidence:

  COMPARTMENT A -- death caused by EMC (~60% of deaths within a decade).
    Does obesity make the SARCOMA kill you sooner? There is no EMC evidence and the
    sarcoma evidence is thin and confounded. Default here is UNKNOWN, and the model
    refuses to invent it.

  COMPARTMENT B -- death from everything else (~40% of deaths within a decade, computed
    in emc-mortality-decomposition.json).
    Does obesity make an ordinary death sooner? Yes, and the evidence is enormous --
    because in this compartment an EMC patient IS an ordinary person of that age and sex.
    THE DEATHS ARE NOT CANCER DEATHS, so general-population evidence transfers with the
    weakest assumption anywhere in this repository.

⭐ THAT ASYMMETRY IS THE FINDING, AND IT INVERTS THIS PROGRAMME'S USUAL PROBLEM. Every
antitumour route here is blocked on EMC-specific evidence that cannot be obtained without
a wet lab or a clinic. Compartment B needs no EMC-specific evidence at all -- it needs
population evidence that already exists in abundance, and its transfer assumption is
"EMC patients die of heart disease at roughly the rate their age and sex predict", which
is far weaker than "a ligand designed against a cryptic pocket will be paralogue-selective".

⚠ AND THE HONEST CONSEQUENCE CUTS THE CLAIM DOWN. Acting only on compartment B, a host
factor can only ever move the ~40% of deaths that are not EMC deaths. The headline is
therefore never "this cures EMC" -- it is "this is worth a defined and modest number of
percentage points, to a defined subgroup, at a cost of zero new science". The model
reports that number with its assumptions attached rather than a slogan.

⛔ NO EFFECT SIZE IS HARDCODED HERE. Every one is read from an inputs file whose entries
must carry a PMID that appears in a committed retrieval artifact, exactly as in
emc_supportive_effect_transfer.py, and for the reason recorded in CLAUDE.md section 7:
an invented PMID passed lint_claims twice, because claim strength and citation provenance
are orthogonal.

Inputs:  research/manuscripts/emc-host-factor-inputs.json
         research/literature/emc-host-factor-probe.json    (the anchor)
         research/manuscripts/emc-mortality-decomposition.json
Output:  research/manuscripts/emc-host-factor-model.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
INPUTS = ROOT / "research/manuscripts/emc-host-factor-inputs.json"
PROBE = ROOT / "research/literature/emc-host-factor-probe.json"
DECOMP = ROOT / "research/manuscripts/emc-mortality-decomposition.json"
OUT = ROOT / "research/manuscripts/emc-host-factor-model.json"


# ---------------------------------------------------------------------------
# The bias registry -- retrieved, not remembered, and attached to every row
# ---------------------------------------------------------------------------
# ⛔ Each of these has a documented capacity to reverse the sign of a host-factor
# estimate. A row that does not declare which apply has not been analysed.
BIASES = {
    "reverse_causation": (
        "The disease causes the exposure rather than the reverse. Cancer causes weight "
        "loss, so low body mass looks lethal and high body mass looks protective. An "
        "analysis blind to this recommends weight GAIN to cancer patients."),
    "obesity_paradox": (
        "The specific, named form of the above in oncology, where measured associations "
        "between adiposity and survival run opposite to the causal effect."),
    "collider_bias": (
        "Conditioning on having the disease distorts associations among its causes, so a "
        "risk factor for incidence can appear protective for survival without any "
        "biological effect at all."),
    "immortal_time": (
        "A drug taken by people who survived long enough to take it manufactures a "
        "survival benefit out of the study design."),
    "healthy_user": (
        "People who take preventive medication and adhere to it differ systematically "
        "from those who do not, in ways that predict survival independently."),
    "confounding_by_indication": (
        "The condition prompting treatment is itself prognostic."),
    "competing_risks_misestimation": (
        "Using an estimator that censors other-cause deaths overstates the cause-specific "
        "incidence, which is precisely the two-compartment structure at issue here."),
    "transportability": (
        "The effect was measured in a population that differs from this one in ways that "
        "modify the effect, not merely in ways that shift the baseline."),
}

# How far an effect measured elsewhere carries into each compartment. Declared, never
# computed. ⚠ THE ASYMMETRY IS DELIBERATE AND IS THE MODEL'S CENTRAL CLAIM: the same
# study supports a compartment-B statement far better than a compartment-A one.
COMPARTMENT_TRANSFER = {
    "B": (0.60, 1.00,
          "Competing (non-EMC) death. The outcome is an ordinary death in an ordinary "
          "person, so a general-population effect applies with the weakest assumption in "
          "this repository. Not 1.0, because an EMC cohort is selected for having reached "
          "and survived a sarcoma diagnosis and is therefore fitter than the population "
          "the effect was measured in."),
    "A": (0.00, 0.30,
          "EMC-specific death. No EMC evidence exists and sarcoma evidence is thin and "
          "confounded, so the lower bound is ZERO -- no effect -- and stays zero unless a "
          "row supplies direct evidence and says so."),
}


def anchored_pmids(probe: dict) -> set[str]:
    found: set[str] = set()
    for entry in (probe.get("queries") or {}).values():
        for hit in entry.get("hits") or []:
            if hit.get("pmid"):
                found.add(str(hit["pmid"]))
    return found


def check_anchors(spec: dict, probe: dict) -> list[str]:
    have = anchored_pmids(probe)
    problems = []
    for row in spec.get("factors", []):
        for ev in row.get("evidence", []):
            if ev.get("status") == "unretrieved":
                continue
            pmid = str(ev.get("pmid") or "")
            if not re.fullmatch(r"\d{6,9}", pmid):
                problems.append(f"{row['id']}: unusable PMID {pmid!r}; record it as unretrieved instead")
            elif pmid not in have:
                problems.append(
                    f"{row['id']}: PMID {pmid} is in no retrieved artifact. Either the search "
                    f"did not return it, or it was written from recollection.")
    return problems


def model_factor(row: dict, competing_share: float) -> dict:
    """One host factor, both compartments, as a band."""
    prev = row["prevalence_in_cohort"]
    out = {
        "id": row["id"],
        "factor": row["factor"],
        "intervention": row["intervention"],
        "prevalence_in_cohort": prev,
        "prevalence_basis": row["prevalence_basis"],
        "biases_that_apply": [
            {"bias": b, "why_it_matters": BIASES[b]} for b in row.get("biases", []) if b in BIASES
        ],
        "compartments": {},
    }
    if row.get("endpoint_caveat"):
        out["endpoint_caveat"] = row["endpoint_caveat"]
    if not row.get("biases"):
        out["bias_declaration_missing"] = (
            "No biases declared. That is not a clean bill of health -- it means this row has "
            "not been analysed, and its numbers should not be quoted.")

    for comp, share in (("A", 1.0 - competing_share), ("B", competing_share)):
        ev = next((e for e in row.get("evidence", []) if e.get("compartment") == comp), None)
        t_lo, t_hi, t_note = COMPARTMENT_TRANSFER[comp]
        if ev is None or ev.get("status") == "unretrieved":
            out["compartments"][comp] = {
                "share_of_all_deaths": round(share, 4),
                "status": "NO_EVIDENCE",
                "relative_risk_reduction_range": [0.0, 0.0],
                "transfer_note": t_note,
                "reading": (
                    "Nothing is claimed for this compartment. For compartment A that is the "
                    "expected and honest state: no EMC-specific evidence exists."),
            }
            continue
        if ev.get("status") == "association_only":
            # ⛔ AN ASSOCIATION IS NOT AN INTERVENTION EFFECT. A hazard ratio for HAVING the
            # factor says nothing about what REMOVING it would do -- the bias registry above
            # lists five ways the two differ in sign. It is recorded so the reader can see the
            # sarcoma-specific evidence exists, and it is modelled at ZERO so that nothing
            # downstream can quote it as a benefit.
            out["compartments"][comp] = {
                "share_of_all_deaths": round(share, 4),
                "status": "ASSOCIATION_ONLY",
                "pmid": ev["pmid"],
                "measured_in": ev.get("measured_in"),
                "endpoint": ev.get("endpoint"),
                "association_hazard_ratio_range": [ev["hazard_ratio_lo"], ev["hazard_ratio_hi"]],
                "relative_risk_reduction_range": [0.0, 0.0],
                "transfer_note": t_note,
                "exposed_patient_share_of_deaths_averted_range": [0.0, 0.0],
                "cohort_share_of_deaths_averted_range": [0.0, 0.0],
                "reading": (
                    "An association between carrying the factor and dying is recorded here, and "
                    "NOTHING is claimed from it: the estimate is not an intervention effect, and "
                    "reverse causation alone can produce it with the sign intact."),
            }
            continue
        rrr_lo, rrr_hi = ev["relative_risk_reduction_lo"], ev["relative_risk_reduction_hi"]
        out["compartments"][comp] = {
            "share_of_all_deaths": round(share, 4),
            "status": "MODELLED",
            "pmid": ev["pmid"],
            "measured_in": ev.get("measured_in"),
            "endpoint": ev.get("endpoint"),
            "relative_risk_reduction_range": [rrr_lo, rrr_hi],
            "transfer_multiplier_range": [t_lo, t_hi],
            "transfer_note": t_note,
            # For a patient who HAS the factor: the share of their total mortality removed.
            "exposed_patient_share_of_deaths_averted_range": [
                round(share * rrr_lo * t_lo, 4),
                round(share * rrr_hi * t_hi, 4),
            ],
            # Across the whole cohort, only the exposed fraction can benefit.
            "cohort_share_of_deaths_averted_range": [
                round(prev * share * rrr_lo * t_lo, 4),
                round(prev * share * rrr_hi * t_hi, 4),
            ],
        }
    return out


def main() -> int:
    if not INPUTS.exists():
        print(f"no inputs at {INPUTS.relative_to(ROOT)} -- nothing to model yet.", file=sys.stderr)
        print("Expected until the host-factor retrieval has been READ. Effect sizes are "
              "entered by hand from retrieved hits, never from recollection.", file=sys.stderr)
        return 2
    if not PROBE.exists():
        print(f"no probe artifact at {PROBE.relative_to(ROOT)} -- the anchor check cannot run.",
              file=sys.stderr)
        return 2

    spec = json.loads(INPUTS.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))

    problems = check_anchors(spec, probe)
    if problems:
        print("UNANCHORED EVIDENCE -- refusing to model:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    decomp = json.loads(DECOMP.read_text(encoding="utf-8"))
    within = (decomp.get("within_series") or [{}])[0]
    competing_share = (within.get("competing_share_of_deaths_pct") or 0.0) / 100.0

    rows = [model_factor(r, competing_share) for r in spec.get("factors", [])]

    payload = {
        "_readme": (
            "What treating a common, independently treatable condition would be worth to a "
            "patient with EMC. TWO COMPARTMENTS, NEVER ONE NUMBER. Compartment B is death "
            "from causes other than EMC, where the patient is an ordinary person and "
            "general-population evidence transfers with a weak assumption. Compartment A is "
            "death caused by EMC, where no EMC evidence exists and the default is that "
            "NOTHING is claimed. Every effect size is anchored to a PMID present in the "
            "committed retrieval artifact; an anchored identifier means a fetch returned it, "
            "not that the paper supports the row. Nothing here asserts efficacy, safety, a "
            "therapeutic window or clinical readiness in EMC, and nothing here is advice for "
            "any individual."
        ),
        "generated_by": "research/manuscripts/emc_host_factor_model.py",
        "competing_share_of_deaths_used": competing_share,
        "competing_share_source": (
            "research/manuscripts/emc-mortality-decomposition.json, within-series "
            "(Meis-Kindblom 1999) -- the only pairing measured on the same patients."
        ),
        "why_two_compartments": (
            "A host factor acts on EMC deaths and on ordinary deaths through completely "
            "different evidence, and the second is far better supported. Reporting one blended "
            "number would let the strength of the compartment-B evidence silently license a "
            "compartment-A claim that nothing supports."
        ),
        "the_honest_ceiling": (
            "Acting on compartment B alone, a host-factor intervention can only ever touch the "
            "share of deaths that are not EMC deaths. It is not a cancer treatment and must "
            "never be presented as one. What makes it worth registering is that it requires no "
            "new science, no wet lab and no collaborator -- which is not true of any other "
            "route in this portfolio."
        ),
        "bias_registry": BIASES,
        "compartment_transfer_scale": {
            k: {"multiplier_range": [v[0], v[1]], "means": v[2]}
            for k, v in COMPARTMENT_TRANSFER.items()
        },
        "factors": rows,
        "factors_not_entered": spec.get("not_entered", []),
        "limits": [
            "Prevalence of every host factor in an EMC cohort is UNKNOWN -- no EMC series records one -- so every prevalence here is imported from a general population and is an assumption, not a measurement.",
            "A share of deaths averted is not a gain in life expectancy; converting the two needs a time horizon and a competing-risks structure this model does not have.",
            "Every compartment-A entry that is not NO_EVIDENCE should be treated as the weakest part of this analysis, because the sarcoma literature behind it is small and confounded.",
            "This model cannot detect the biases in its own inputs. The bias registry names what threatens each estimate; it does not correct for any of them.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(rows)} factor(s), "
          f"competing share {competing_share:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
