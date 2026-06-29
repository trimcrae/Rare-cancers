"""
Pure selection/ranking logic for the de-novo NR4A3 warhead campaign — no deps (TESTING.md #3), so
the screen job (nr4a3_denovo.py, run on a free GitHub CPU runner) executes only unit-tested logic.

The de-novo driver generates molecules against the opened NR4A3 pocket (DiffSBDD), then runs a cheap
CPU cascade — novelty (ECFP Tanimoto vs known NR4A actives) -> developability
(warhead_chem_profile.profile) -> docking into the three state-matched opened pockets
(selectivity_fingerprint.classify) -> PROTAC-handle check. This module owns the THRESHOLDING and
RANKING of that cascade: it takes already-computed numbers (the RDKit/smina work lives in the driver)
and decides, per molecule, whether it passes the screen and how the shortlist is ordered.

Two verdict levels (kept separate on purpose):
  - `passes_screen`  : docking-NR4A3-selective AND developable AND novel AND has a PROTAC handle.
                       These are the molecules worth the one cheap MM-GBSA confirmation run.
  - `is_candidate`   : passes_screen AND the later MM-GBSA verdict is `confirmed_selective`.
                       This is the publishable designed candidate (= the deliverable).

Everything here is a triage/design prior, NOT affinity and NOT a validated warhead — docking dG is a
screening prior, MM-GBSA is direction-only, and the pocket is biased-MD-opened. The terminal blockers
(synthesise; prove binding/degradation; prove EMC fusion-addiction via dTAG) stay wet-lab.
"""

import selectivity_fingerprint as sf   # pure, no deps — reuse classify()/margins/cell logic

# --- Novelty -----------------------------------------------------------------------------------
# A generated molecule must be meaningfully NEW, not a re-draw of a known NR4A tool compound. We
# gate on the maximum ECFP4 Tanimoto similarity to the known-actives set (computed in the driver).
NOVELTY_TANIMOTO_MAX = 0.40            # > 0.40 to any known active => "not novel", reject

# --- Developability gate (PROTAC-aware) --------------------------------------------------------
# The warhead is only HALF of the final degrader, so we allow a modest MW and tolerate beyond-Ro5,
# but reject hard-to-make (SAscore) and pan-assay-interference (PAINS) scaffolds outright.
QED_MIN = 0.30
SASCORE_MAX = 4.5                      # >4.5 ~ celastrol-hard; reject as a starting warhead
PAINS_MAX = 0                          # any PAINS alert => reject
BRENK_MAX = 2                          # a couple of BRENK alerts tolerated; more => reject
WARHEAD_MW_MAX = 600.0                 # warhead only; the linker+E3 add ~400-500 more


def is_novel(max_tanimoto_to_known, thresh=NOVELTY_TANIMOTO_MAX):
    """True if the molecule is dissimilar enough from every known NR4A active to count as novel.
    `max_tanimoto_to_known` is the max ECFP Tanimoto to the known set (None if it could not be
    computed -> conservatively treated as NOT novel)."""
    return max_tanimoto_to_known is not None and max_tanimoto_to_known <= thresh


def has_protac_handle(profile):
    """True if the molecule carries at least one amine/phenol/carboxylic-acid a linker can conjugate
    to (from warhead_chem_profile.profile's `protac_handles`)."""
    return (profile or {}).get("protac_handles", {}).get("total", 0) > 0


def is_developable(profile, qed_min=QED_MIN, sascore_max=SASCORE_MAX,
                   pains_max=PAINS_MAX, brenk_max=BRENK_MAX, mw_max=WARHEAD_MW_MAX):
    """Pure developability gate over a warhead_chem_profile.profile() dict.

    Returns (developable: bool, reasons: list[str]) — `reasons` lists every failed criterion, so a
    pass is an empty list. An unparseable/missing profile fails with a single reason."""
    if not profile or "error" in profile:
        return False, ["unprofilable"]
    reasons = []
    qed = profile.get("QED")
    sa = profile.get("SAscore")
    mw = profile.get("MW")
    if qed is None or qed < qed_min:
        reasons.append(f"QED<{qed_min}")
    if sa is None or sa > sascore_max:
        reasons.append(f"SAscore>{sascore_max}")
    if len(profile.get("PAINS_alerts", [])) > pains_max:
        reasons.append("PAINS")
    if profile.get("BRENK_alert_count", 0) > brenk_max:
        reasons.append(f"BRENK>{brenk_max}")
    if mw is None or mw > mw_max:
        reasons.append(f"MW>{mw_max}")
    if not has_protac_handle(profile):
        reasons.append("no_PROTAC_handle")
    return (len(reasons) == 0), reasons


def build_row(gen, dg3, dg1, dg2, profile, max_tanimoto,
              handle_contacts=0, conserved_contacts=0):
    """Fuse one generated molecule's cascade results into a single classified row.

    `gen` is the generation record (label/smiles/campaign/...); dg3/dg1/dg2 are the opened-pocket
    docking dG (None = failed dock); `profile` is warhead_chem_profile.profile(); `max_tanimoto` is
    the novelty number. Returns a dict carrying the selectivity fingerprint plus novelty/
    developability verdicts and `passes_screen`."""
    fp = sf.classify(dg3, dg1, dg2)
    developable, dreasons = is_developable(profile)
    novel = is_novel(max_tanimoto)
    row = dict(fp)
    row.update({
        "label": gen.get("label"),
        "smiles": gen.get("smiles"),
        "campaign": gen.get("campaign"),
        "handle_contacts": handle_contacts,
        "conserved_contacts": conserved_contacts,
        "max_tanimoto_to_known": max_tanimoto,
        "novel": novel,
        "developable": developable,
        "develop_fail": dreasons,
        "QED": (profile or {}).get("QED"),
        "SAscore": (profile or {}).get("SAscore"),
        "protac_handles": (profile or {}).get("protac_handles", {}).get("total", 0),
    })
    # Screen pass depends on the campaign's selectivity target.
    if gen.get("campaign") == "pan":
        sel_ok = fp["pan_nr4a"]
    else:                                      # default = the NR4A3-selective lead campaign
        sel_ok = fp["nr4a3_selective"]
    row["passes_screen"] = bool(sel_ok and developable and novel
                                and has_protac_handle(profile))
    return row


def is_candidate(row, mmgbsa_verdict=None):
    """The publishable verdict: a screened molecule whose later MM-GBSA verdict CONFIRMS selectivity.
    `mmgbsa_verdict` is the string from mmgbsa_select (e.g. 'confirmed_selective'); None until that
    run exists, so this is False during the CPU-only screen."""
    return bool(row.get("passes_screen") and mmgbsa_verdict == "confirmed_selective")


def _rank_key(r):
    # selective leads first, then by combined NR4A3 margin, then NR4A3 potency, then handle engagement
    return (not r.get("passes_screen"),
            -((r.get("margin_vs_NR4A1") or -99) + (r.get("margin_vs_NR4A2") or -99)),
            (r["dG"]["NR4A3"] if r.get("dG", {}).get("NR4A3") is not None else 0),
            -r.get("handle_contacts", 0))


def rank(rows):
    """Return the rows sorted into a screen ranking (screen-passers first, then by margin/potency)."""
    return sorted(rows, key=_rank_key)


def summarize(rows):
    """Census + the actionable shortlists from a set of built rows."""
    ranked = rank(rows)
    census = {}
    for r in ranked:
        census[r["cell"]] = census.get(r["cell"], 0) + 1
    return {
        "n_generated": len(ranked),
        "cell_census": census,
        "n_novel": sum(1 for r in ranked if r.get("novel")),
        "n_developable": sum(1 for r in ranked if r.get("developable")),
        "screen_passers": [r for r in ranked if r.get("passes_screen")],
        "selective_passers": [r for r in ranked
                              if r.get("passes_screen") and r.get("campaign") != "pan"],
        "pan_passers": [r for r in ranked
                        if r.get("passes_screen") and r.get("campaign") == "pan"],
    }
