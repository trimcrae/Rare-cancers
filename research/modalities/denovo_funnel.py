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

N_ENGAGEABLE_HANDLES = 5     # L406, T410, I484, I531, L534 (the pocket-facing divergent handles)


def score_molecule(profile, handle_contacts, n_handles=N_ENGAGEABLE_HANDLES):
    """Composite triage score for one generated molecule.

    profile: the RDKit profile dict (QED, SAscore, PAINS_alerts, BRENK_alert_count, protac_handles, ...),
             or a dict containing {"error": ...} for an invalid/unparseable generation.
    handle_contacts: # of engageable handle residues the generated pose contacts (0..n_handles).
    Returns a float (higher = more promising), or None if the molecule is invalid.

    Mirrors warhead_chem_profile.promise (QED - 0.1*SA - 0.15*PAINS - 0.05*BRENK +/- PROTAC handle) and
    adds a handle-engagement term (+0.2 * fraction of engageable handles contacted) — the selectivity-lever
    contact is the whole point of conditioning generation on the divergent handles.
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
    return round(qed - 0.1 * sa - 0.15 * pains - 0.05 * brenk + handle_term + 0.2 * frac, 3)


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
    return {
        "n_generated": n,
        "n_valid": nv,
        "frac_valid": round(nv / n, 3) if n else None,
        "n_unique_smiles": len(smis),
        "frac_druglike_qed_ge_0.5": frac(lambda r: (r.get("QED") or 0) >= 0.5),
        "frac_synthesizable_sa_le_4.5": frac(lambda r: (r.get("SAscore") or 99) <= 4.5),
        "frac_pains_free": frac(lambda r: len(r.get("PAINS_alerts") or []) == 0),
        "frac_contacts_ge_3_handles": frac(lambda r: r.get("handle_contacts", 0) >= 3),
        "frac_contacts_ge_4_handles": frac(lambda r: r.get("handle_contacts", 0) >= 4),
        "max_handle_contacts": max(contacts) if contacts else None,
        "mean_handle_contacts": round(sum(contacts) / len(contacts), 2) if contacts else None,
        "mean_SAscore": round(sum(sas) / len(sas), 2) if sas else None,
        "mean_QED": round(sum(qeds) / len(qeds), 3) if qeds else None,
        "n_engageable_handles": n_handles,
    }
