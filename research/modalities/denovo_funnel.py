#!/usr/bin/env python3
"""Pure ranking/aggregation for de-novo generated NR4A3 warhead candidates (Step 2 funnel, eyeball tier).

WHY. DiffSBDD generates 3D molecules inside the Step-0 druggable pocket. Before spending dock+MM-GBSA on
any of them, we triage the raw generations on cheap, pose-aware criteria: is it a valid, drug-like,
synthesizable, non-PAINS molecule that actually contacts the divergent selectivity handles in the generated
pose? This module is the pure scoring/ranking/summary behind that triage — no RDKit/IO/structure dependency
so it is unit-tested directly (TESTING.md #3). The driver (nr4a3_denovo.py) supplies the per-molecule
RDKit profile + handle-contact count computed from the generated pose.

These are SCREENING PRIORS for which generations to advance, NOT affinity or a validated lead.
"""

import structural_alerts as _sa

N_ENGAGEABLE_HANDLES = 5     # L406, T410, I484, I531, L534 (the pocket-facing divergent handles)

# Hard demotion for a non-developable molecule (structural-alert liability, no aromatic ring, or SA>4.5).
# Large enough to sink any artifact below every clean candidate, but finite so the ranking still ORDERS the
# artifacts (we want to SEE them, not silently drop them — the de-novo MM-GBSA artifacts were the whole point).
DEVELOPABILITY_PENALTY = 1.0


def developability(profile, max_sa=_sa.MAX_SASCORE):
    """Developability verdict for one generated molecule from its RDKit profile. Reads the profile's
    'structural_liabilities' (list, computed by the driver via structural_alerts.find_liabilities),
    'aromatic_rings', and 'SAscore'. Returns {"developable": bool, "reasons": [..]}; an invalid profile is
    not developable."""
    if not profile or "error" in profile:
        return {"developable": False, "reasons": ["invalid"]}
    return _sa.developable_verdict(profile.get("structural_liabilities") or [],
                                   profile.get("aromatic_rings"), profile.get("SAscore"), max_sa=max_sa)


def score_molecule(profile, handle_contacts, n_handles=N_ENGAGEABLE_HANDLES, min_mw=250.0):
    """Composite triage score for one generated molecule.

    profile: the RDKit profile dict (MW, QED, SAscore, PAINS_alerts, BRENK_alert_count, protac_handles, ...),
             or a dict containing {"error": ...} for an invalid/unparseable generation.
    handle_contacts: # of engageable handle residues the generated pose contacts (0..n_handles).
    min_mw: below this molecular weight a SIZE PENALTY applies (the pilot showed unconstrained generation
            top-ranks trivially-small fragments — benzoic acid etc. — that ace QED/SAscore but are not
            warheads). Penalty = 0.002 * (min_mw - MW) Da, so MW 122 (benzoic acid) loses ~0.26 while a
            ~350 Da lead loses 0. MW missing -> no penalty (don't punish an un-profiled molecule).
    Returns a float (higher = more promising), or None if the molecule is invalid.

    Mirrors warhead_chem_profile.promise (QED - 0.1*SA - 0.15*PAINS - 0.05*BRENK +/- PROTAC handle), adds a
    handle-engagement term (+0.2 * fraction of engageable handles contacted — the selectivity-lever contact
    is the point of conditioning on the divergent handles), and the lead-size floor.
    """
    if not profile or "error" in profile:
        return None
    qed = profile.get("QED") or 0.0
    sa = profile.get("SAscore")
    sa = 6.0 if sa is None else sa
    pains = len(profile.get("PAINS_alerts") or [])
    brenk = profile.get("BRENK_alert_count") or 0
    handle_term = 0.1 if (profile.get("protac_handles") or {}).get("total", 0) > 0 else -0.2
    frac = (handle_contacts or 0) / float(n_handles) if n_handles else 0.0
    mw = profile.get("MW")
    size_penalty = 0.0 if (mw is None or mw >= min_mw) else round(0.002 * (min_mw - mw), 4)
    # Developability gate: a structural-alert liability / non-aromatic / SA>4.5 molecule is hard-demoted, so
    # the unstable-but-high-scoring artifacts (denovo_15 carbamic acid, denovo_94 peroxide) can no longer
    # float to the top of the funnel. The clean candidates win.
    dev_penalty = 0.0 if developability(profile)["developable"] else DEVELOPABILITY_PENALTY
    return round(qed - 0.1 * sa - 0.15 * pains - 0.05 * brenk + handle_term + 0.2 * frac
                 - size_penalty - dev_penalty, 3)


def rank(rows):
    """Sort molecule rows by denovo_promise desc (invalids, promise=None, sort last). Stable on ties via
    the row's existing order. Returns a new list; each row must already carry 'denovo_promise'."""
    return sorted(rows, key=lambda r: (r.get("denovo_promise") is not None,
                                       r.get("denovo_promise") or 0.0), reverse=True)


def summarize(rows, n_handles=N_ENGAGEABLE_HANDLES):
    """Aggregate stats over generated molecule rows for the pilot eyeball: validity, drug-likeness,
    synthesizability, cleanliness, handle engagement, and chemotype diversity (unique canonical SMILES)."""
    valid = [r for r in rows if r.get("denovo_promise") is not None and "error" not in r]
    n = len(rows)
    nv = len(valid)

    def frac(pred, pool=valid):
        return round(sum(1 for r in pool if pred(r)) / len(pool), 3) if pool else None

    smis = {r.get("smiles") for r in valid if r.get("smiles")}
    contacts = [r.get("handle_contacts", 0) for r in valid]
    sas = [r["SAscore"] for r in valid if r.get("SAscore") is not None]
    qeds = [r["QED"] for r in valid if r.get("QED") is not None]
    mws = [r["MW"] for r in valid if r.get("MW") is not None]
    return {
        "n_generated": n,
        "n_valid": nv,
        "frac_valid": round(nv / n, 3) if n else None,
        "n_unique_smiles": len(smis),
        "frac_druglike_qed_ge_0.5": frac(lambda r: (r.get("QED") or 0) >= 0.5),
        "frac_synthesizable_sa_le_4.5": frac(lambda r: (r.get("SAscore") or 99) <= 4.5),
        "frac_pains_free": frac(lambda r: len(r.get("PAINS_alerts") or []) == 0),
        "frac_developable": frac(lambda r: developability(r)["developable"]),
        "n_developable": sum(1 for r in valid if developability(r)["developable"]),
        "frac_lead_size_mw_250_500": frac(lambda r: 250 <= (r.get("MW") or 0) <= 500),
        "frac_contacts_ge_3_handles": frac(lambda r: r.get("handle_contacts", 0) >= 3),
        "frac_contacts_ge_4_handles": frac(lambda r: r.get("handle_contacts", 0) >= 4),
        "max_handle_contacts": max(contacts) if contacts else None,
        "mean_handle_contacts": round(sum(contacts) / len(contacts), 2) if contacts else None,
        "mean_SAscore": round(sum(sas) / len(sas), 2) if sas else None,
        "mean_QED": round(sum(qeds) / len(qeds), 3) if qeds else None,
        "mean_MW": round(sum(mws) / len(mws), 1) if mws else None,
        "n_engageable_handles": n_handles,
    }
