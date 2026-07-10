"""
Harmonized, score-INDEPENDENT orthosteric-pocket tracking for the NR4A3 cryptic-pocket work.

WHY THIS EXISTS (reviewer P0). The earlier pipeline conflated two things that must be separate:
  (a) DEFINING which cavity is the orthosteric "Pocket 5" — the site IDENTITY, and
  (b) SCORING that cavity's druggability with fpocket.
It used fpocket's own druggability score to pick the site (`select_druggable_lbd_pocket` = the
HIGHEST-druggability LBD cavity sharing >=1 residue with the LBD window), then tracked it across
frames/conformers/proteins by "maximal residue-set overlap requiring >=1 shared residue," and DROPPED
frames where no cavity was matched. That makes the site definition circular with the quantity under
test and lets a 1-residue-overlap decoy count as "the pocket."

THIS MODULE fixes that with three prespecified, score-independent pieces (all PURE + unit-tested):

  1. orthosteric_reference(): the site is a FIXED, prespecified structural residue set (the known
     Pocket-5 lining set 406,407,410,411,412,481,484,485,531,534, plus the 406-534 span), mapped to
     the target structure's numbering by the CALLER (BLOSUM62 alignment for 8XTT author numbering,
     residue_map for renumbered MD topologies). fpocket never chooses the site — it only scores it.

  2. match_pocket(): a candidate fpocket cavity is accepted as "the orthosteric site in this frame"
     ONLY if it clears a COMPOSITE gate that is prespecified and NOT tuned to preserve any result:
         (residue Jaccard >= JACCARD_MIN  OR  fraction-of-reference-recovered >= FRAC_RECOVERED_MIN)
         AND centroid within CENTROID_MAX_ANG of the mapped reference-site centroid.
     A 1-residue-overlap decoy fails both the Jaccard and the recovery branch and is rejected.

  3. detection_report() / sensitivity(): report BOTH denominators (detection fraction, fraction >= D*
     among DETECTED frames, and fraction >= D* among ALL propagated frames), and how the headline
     fraction moves as the match thresholds vary over a prespecified grid.

UNITS. All coordinates are ANGSTROM (fpocket / PDB native). mdtraj `save_pdb` writes PDB in Angstrom
regardless of its internal nm, so a centroid computed from a saved frame PDB is also Angstrom. The
centroid threshold is therefore in Angstrom (CENTROID_MAX_ANG). This deliberately avoids the nm/Angstrom
mix that has already bitten this repo (see residue_map.py). 8.0 A ~= 0.8 nm.

Everything here is dependency-free and takes plain data, so tests/test_pocket_tracking.py exercises it
without fpocket, numpy, biopython, or any structure.
"""
import math
import re
import subprocess

# --------------------------------------------------------------------------------------------------
# The FIXED orthosteric reference (single source of truth; matches nr4a3_8xtt_benchmark constants).
# Canonical UniProt Q92570 numbering — the CALLER maps these onto the target structure's numbering.
# --------------------------------------------------------------------------------------------------
POCKET5_LINING = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]  # 10 prespecified lining residues
POCKET5_SPAN = (406, 534)                                            # MD/release lining span

# --------------------------------------------------------------------------------------------------
# PRESPECIFIED default acceptance thresholds. These are principled, NOT tuned to preserve the ~20-24%
# result — the sensitivity() grid is what reports how the headline moves, so these must stand on their
# own reasoning:
#   FRAC_RECOVERED_MIN = 0.30  a matched cavity must recover >= 3 of the 10 reference lining residues.
#                              (The workhorse branch: fpocket cavities line ~15-30 residues, far more
#                              than the 10-residue reference, so a co-located cavity naturally has LOW
#                              Jaccard even when it clearly IS the site — hence the OR with recovery.)
#   JACCARD_MIN        = 0.25  a residue-set Jaccard of at least 0.25 also accepts (the size-matched
#                              branch), so a compact cavity that overlaps the reference tightly passes
#                              even if it recovers <3 named residues.
#   CENTROID_MAX_ANG   = 8.0   the cavity centroid must sit within 8 A (~0.8 nm, roughly one pocket
#                              radius) of the reference-site centroid — a cavity centered a full
#                              pocket-width away is a DIFFERENT site regardless of residue overlap.
# A 1-residue-overlap decoy: recovery = 0.1 (< 0.30) and Jaccard ~ 1/large (< 0.25) -> REJECTED.
# --------------------------------------------------------------------------------------------------
JACCARD_MIN = 0.25
FRAC_RECOVERED_MIN = 0.30
CENTROID_MAX_ANG = 8.0

# Calibrated drug-bound band lower edge (nr4a3-calibration); the headline D* for detection reports.
D_STAR = 0.53

# The pinned fpocket build (see sagemaker_src/entry_*.py). Recorded into every harmonized output so all
# ensembles are scored by ONE homogeneous fpocket. conda-forge serves up to 4.2.3 (latest, verified).
FPOCKET_VERSION = "4.2.3"

# Env flag names.
MATCH_MODE_ENV = "POCKET_MATCH"          # "harmonized" | "legacy" (default)
HARMONIZED = "harmonized"
LEGACY = "legacy"


# ==================================================================================================
# 1. The fixed reference site (score-independent).
# ==================================================================================================

def _centroid(coords):
    n = len(coords)
    if n == 0:
        raise ValueError("centroid of empty coordinate list")
    sx = sum(c[0] for c in coords)
    sy = sum(c[1] for c in coords)
    sz = sum(c[2] for c in coords)
    return (sx / n, sy / n, sz / n)


def orthosteric_reference(ca_by_resnum, lining_residues=POCKET5_LINING, span=POCKET5_SPAN):
    """The FIXED orthosteric reference site for one structure, defined WITHOUT fpocket.

    `ca_by_resnum`: {residue_number: (x,y,z)} CA coords in the STRUCTURE'S OWN numbering (Angstrom).
        The caller must have already mapped the canonical Pocket-5 residue numbers onto this numbering
        (BLOSUM62 alignment for 8XTT; residue_map for renumbered MD topologies) and pass the MAPPED
        `lining_residues` / `span` in that same numbering.
    `lining_residues`: the prespecified lining set (mapped numbering).
    `span`: (first, last) inclusive lining span (mapped numbering) for MD/release overlap.

    Returns {"lining_residues": [...present...], "span_residues": [...present...],
             "centroid": (x,y,z), "n_lining_present": int, "n_lining_expected": int}.
    Raises if none of the lining residues is present (a numbering catastrophe — fail loud)."""
    present = [r for r in lining_residues if r in ca_by_resnum]
    if not present:
        raise ValueError(
            f"none of the {len(lining_residues)} reference lining residues is present in the "
            "structure — check the numbering map before defining the reference site")
    centroid = _centroid([ca_by_resnum[r] for r in present])
    lo, hi = span
    span_present = [r for r in range(lo, hi + 1) if r in ca_by_resnum]
    return {
        "lining_residues": sorted(present),
        "span_residues": sorted(span_present),
        "centroid": centroid,
        "n_lining_present": len(present),
        "n_lining_expected": len(lining_residues),
    }


def pocket_centroid(residues, ca_by_resnum):
    """Centroid (Angstrom) of a candidate cavity's lining residues, from the SAME CA coord source used
    for the reference — apples-to-apples. Returns None if no lining residue has a CA coord."""
    coords = [ca_by_resnum[r] for r in residues if r in ca_by_resnum]
    if not coords:
        return None
    return _centroid(coords)


# ==================================================================================================
# 2. The composite acceptance gate (score-independent site identity).
# ==================================================================================================

def _dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def match_metrics(candidate_residues, reference_lining):
    """Residue-overlap metrics of one candidate cavity vs the fixed reference lining set. Pure.
    Returns {"n_overlap", "jaccard", "frac_recovered"}."""
    cand = set(candidate_residues)
    ref = set(reference_lining)
    if not ref:
        raise ValueError("reference lining set is empty")
    inter = cand & ref
    union = cand | ref
    return {
        "n_overlap": len(inter),
        "jaccard": (len(inter) / len(union)) if union else 0.0,
        "frac_recovered": len(inter) / len(ref),
    }


def accept_candidate(metrics, centroid_dist, jaccard_min=JACCARD_MIN,
                     frac_recovered_min=FRAC_RECOVERED_MIN, centroid_max_ang=CENTROID_MAX_ANG):
    """The prespecified composite gate for ONE candidate. Pure boolean.

    accept = (jaccard >= jaccard_min OR frac_recovered >= frac_recovered_min)
             AND centroid_dist <= centroid_max_ang

    `centroid_dist` may be None (no CA coords to place the candidate) — treated as FAILING the centroid
    clause (we refuse to accept a cavity we cannot geometrically localize)."""
    residue_ok = (metrics["jaccard"] >= jaccard_min) or (metrics["frac_recovered"] >= frac_recovered_min)
    centroid_ok = (centroid_dist is not None) and (centroid_dist <= centroid_max_ang)
    return bool(residue_ok and centroid_ok)


def match_pocket(candidate_pockets, reference, jaccard_min=JACCARD_MIN,
                 frac_recovered_min=FRAC_RECOVERED_MIN, centroid_max_ang=CENTROID_MAX_ANG,
                 ca_by_resnum=None):
    """Return the candidate cavity that IS the orthosteric site in this frame (or None), by the
    composite gate — INDEPENDENT of fpocket druggability.

    `candidate_pockets`: list of dicts, each with "residues" (list[int], structure numbering) and
        either a precomputed "centroid" (x,y,z Angstrom) OR enough for `ca_by_resnum` to place it.
    `reference`: an orthosteric_reference() dict (its "lining_residues" and "centroid" are used).
    `ca_by_resnum`: optional {resnum:(x,y,z)}; if a candidate lacks a "centroid" it is computed from
        the candidate's lining residues via this map.

    Among ALL candidates that clear the gate, pick the best: highest frac_recovered, then highest
    Jaccard, then nearest centroid, then highest druggability (only as a final deterministic tiebreak,
    never as an acceptance criterion). Returns the chosen pocket dict AUGMENTED with a "_match" block,
    or None if no candidate clears the gate."""
    ref_lining = reference["lining_residues"]
    ref_centroid = reference["centroid"]
    accepted = []
    for p in candidate_pockets:
        m = match_metrics(p.get("residues", []), ref_lining)
        cen = p.get("centroid")
        if cen is None and ca_by_resnum is not None:
            cen = pocket_centroid(p.get("residues", []), ca_by_resnum)
        cdist = _dist(cen, ref_centroid) if cen is not None else None
        if accept_candidate(m, cdist, jaccard_min, frac_recovered_min, centroid_max_ang):
            info = dict(p)
            info["_match"] = {"n_overlap": m["n_overlap"], "jaccard": round(m["jaccard"], 4),
                              "frac_recovered": round(m["frac_recovered"], 4),
                              "centroid_dist_ang": None if cdist is None else round(cdist, 3)}
            accepted.append((m, cdist, info))
    if not accepted:
        return None
    accepted.sort(key=lambda t: (
        t[0]["frac_recovered"],
        t[0]["jaccard"],
        -(t[1] if t[1] is not None else 1e9),        # nearer centroid first
        (t[2].get("druggability") or 0.0),           # final deterministic tiebreak only
    ), reverse=True)
    return accepted[0][2]


# ==================================================================================================
# 3. Both-denominator detection reporting + threshold sensitivity.
# ==================================================================================================

def detection_report(detected_scores, d_star=D_STAR, n_propagated=None):
    """Both-denominator report for one ensemble.

    `detected_scores`: druggability values for the frames/conformers where a matched orthosteric
        cavity WAS detected (float list; exclude un-matched frames — they are NOT in this list).
    `n_propagated`: TOTAL frames/conformers propagated into the analysis (the honest "all" denominator,
        including frames where no cavity matched or fpocket found nothing). Defaults to
        len(detected_scores) (i.e. assume every propagated frame was detected) — callers should pass
        the real total so the detection fraction is meaningful.

    Returns detection fraction P(matched pocket detected), fraction >= D* among DETECTED frames, and
    fraction >= D* among ALL propagated frames — all three, with counts."""
    scores = [float(s) for s in detected_scores if s is not None]
    n_detected = len(scores)
    if n_propagated is None:
        n_propagated = n_detected
    if n_propagated < n_detected:
        raise ValueError(f"n_propagated ({n_propagated}) < n_detected ({n_detected})")
    n_ge = sum(1 for s in scores if s >= d_star)
    return {
        "d_star": d_star,
        "n_propagated": n_propagated,
        "n_detected": n_detected,
        "n_ge_dstar": n_ge,
        "detection_fraction": (n_detected / n_propagated) if n_propagated else None,
        "frac_ge_among_detected": (n_ge / n_detected) if n_detected else None,
        "frac_ge_among_propagated": (n_ge / n_propagated) if n_propagated else None,
    }


def default_threshold_grid():
    """A small PRESPECIFIED grid around the defaults for the sensitivity analysis. Varies each axis
    while holding the others at the default, plus a stricter and a looser corner — enough to show the
    headline is not knife-edged on the exact thresholds, without fishing."""
    grid = []
    for fr in (0.20, 0.30, 0.40, 0.50):
        grid.append({"jaccard_min": JACCARD_MIN, "frac_recovered_min": fr,
                     "centroid_max_ang": CENTROID_MAX_ANG})
    for jc in (0.15, 0.25, 0.35):
        grid.append({"jaccard_min": jc, "frac_recovered_min": FRAC_RECOVERED_MIN,
                     "centroid_max_ang": CENTROID_MAX_ANG})
    for cm in (6.0, 8.0, 10.0):
        grid.append({"jaccard_min": JACCARD_MIN, "frac_recovered_min": FRAC_RECOVERED_MIN,
                     "centroid_max_ang": cm})
    # dedupe (the default point recurs) while preserving order
    seen, out = set(), []
    for g in grid:
        key = (g["jaccard_min"], g["frac_recovered_min"], g["centroid_max_ang"])
        if key not in seen:
            seen.add(key)
            out.append(g)
    return out


def sensitivity(frames, threshold_grid=None, d_star=D_STAR):
    """Headline fraction >= D* vs the match thresholds, recomputing the MATCH at each grid point.

    `frames`: list of per-frame records, each a dict with:
        "candidates": [candidate pocket dicts as for match_pocket() — each with "residues",
                       "druggability", and "centroid"],
        "reference":  an orthosteric_reference() dict for that frame.
      (Each frame carries its OWN reference because different conformers/structures map the fixed
       residue set to different coordinates.) `n_propagated` = len(frames).
    `threshold_grid`: list of {jaccard_min, frac_recovered_min, centroid_max_ang}; defaults to
        default_threshold_grid().

    Returns a list (one row per grid point) of {thresholds, + detection_report fields}, so the caller
    can tabulate how detection fraction and both >= D* fractions move with the thresholds."""
    if threshold_grid is None:
        threshold_grid = default_threshold_grid()
    n_prop = len(frames)
    rows = []
    for g in threshold_grid:
        detected = []
        for fr in frames:
            hit = match_pocket(fr["candidates"], fr["reference"],
                               jaccard_min=g["jaccard_min"],
                               frac_recovered_min=g["frac_recovered_min"],
                               centroid_max_ang=g["centroid_max_ang"])
            if hit is not None and hit.get("druggability") is not None:
                detected.append(hit["druggability"])
        rep = detection_report(detected, d_star=d_star, n_propagated=n_prop)
        rows.append({"thresholds": dict(g), **rep})
    return rows


# ==================================================================================================
# Consolidation of per-ensemble detection reports into one table (pure; for the re-run driver).
# ==================================================================================================

def consolidated_table(ensembles):
    """Fold a list of per-ensemble detection dicts into one consolidated table + rows.

    `ensembles`: list of {"ensemble": name, "detection": detection_report(...)}. Returns
    {"columns": [...], "rows": [...]} with per-ensemble: total frames, matched detected, detection
    fraction, >=D* among detected, >=D* among all propagated."""
    columns = ["ensemble", "n_propagated", "n_detected", "detection_fraction",
               "n_ge_dstar", "frac_ge_among_detected", "frac_ge_among_propagated", "d_star"]
    rows = []
    for e in ensembles:
        d = e.get("detection", {})
        rows.append({
            "ensemble": e.get("ensemble"),
            "n_propagated": d.get("n_propagated"),
            "n_detected": d.get("n_detected"),
            "detection_fraction": d.get("detection_fraction"),
            "n_ge_dstar": d.get("n_ge_dstar"),
            "frac_ge_among_detected": d.get("frac_ge_among_detected"),
            "frac_ge_among_propagated": d.get("frac_ge_among_propagated"),
            "d_star": d.get("d_star"),
        })
    return {"columns": columns, "rows": rows}


# ==================================================================================================
# fpocket version recording (impure wrapper + pure parser).
# ==================================================================================================

def parse_fpocket_version(text):
    """Extract an fpocket version like '4.2.3' from CLI banner text. None if not found. Pure."""
    # tolerate junk between the word 'fpocket' and the version token, e.g. '(fpocket) v4.1'
    m = re.search(r"fpocket[^\d\n]{0,12}?(\d+\.\d+(?:\.\d+)*)", text or "", re.IGNORECASE)
    return m.group(1) if m else None


def resolved_fpocket_version():
    """Best-effort runtime fpocket version string. Tries the CLI banner; falls back to the pinned
    FPOCKET_VERSION constant (the conda spec pins it, so pinned == resolved by construction). Never
    raises — returns a string."""
    for args in (["fpocket", "--version"], ["fpocket", "-h"], ["fpocket"]):
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=30)
            v = parse_fpocket_version((r.stdout or "") + "\n" + (r.stderr or ""))
            if v:
                return v
        except Exception:  # noqa: BLE001 — best-effort; fall through to the pin
            continue
    return FPOCKET_VERSION


def match_mode(env=None):
    """The active match mode from the environment (default LEGACY for backward compatibility)."""
    import os
    val = (env or os.environ).get(MATCH_MODE_ENV, LEGACY).strip().lower()
    return HARMONIZED if val == HARMONIZED else LEGACY


def match_params():
    """The active harmonized match parameters (env-overridable, else the prespecified defaults)."""
    import os
    def _f(name, default):
        try:
            return float(os.environ.get(name, default))
        except (TypeError, ValueError):
            return default
    return {
        "jaccard_min": _f("POCKET_JACCARD_MIN", JACCARD_MIN),
        "frac_recovered_min": _f("POCKET_FRAC_RECOVERED_MIN", FRAC_RECOVERED_MIN),
        "centroid_max_ang": _f("POCKET_CENTROID_MAX_ANG", CENTROID_MAX_ANG),
    }
