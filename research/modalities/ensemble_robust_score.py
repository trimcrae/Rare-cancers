#!/usr/bin/env python3
"""
ENSEMBLE-ROBUST candidate scoring for the NR4A3 selective-degrader redesign (branch:
claude/nr4a3-ensemble-redesign).

WHY THIS EXISTS. Every NR4A3-selective candidate so far (denovo_401 and the lo_m0_NCCO lead-opt series)
was nominated by a score in ONE receptor frame. Two results say that is not enough:
  * the metad-frame decoy null (2026-07-01): denovo_401 clears the release-frame null but NOT the
    metad-opened-frame null — its specificity is receptor-frame-dependent;
  * the 8XTT provenance recalc (2026-07-10): swapping the opened NR4A3 conformer (AF2-opened vs an
    8XTT-derived druggable NMR frame) moves the absolute ABFE by ~4.7 kcal/mol — MORE than the whole
    selectivity margin. i.e. the CONFORMER effect can exceed the RECEPTOR (paralogue) effect.
A single-frame "best score" therefore cannot distinguish a genuinely NR4A3-selective binder from a
molecule overfit to one pocket geometry. This module implements the redesign's core shift: rank on
WORST-CASE robustness across a prespecified conformer panel, not best score in one frame. It is the
pure, score-model-agnostic decision layer; it consumes whatever per-(receptor, conformer) endpoint
numbers the docking / MM-GBSA / ABFE tiers produce and never runs physics itself.

THE OBJECTIVE (trimcrae, 2026-07-11). For a candidate scored across a conformer panel:

    S  =  min_c M_{3,c}   -   lambda * SD_c(M_{3,c})   -   gamma * max_{p in {1,2}, c} B_{p,c}

  * M_{3,c}  = NR4A3 binding favourability in conformer c   (higher = tighter; = -dG_bind).
  * SD_c(.)  = spread of the NR4A3 favourability across the panel  (the "conformer sensitivity" penalty).
  * B_{p,c}  = paralogue (NR4A1/NR4A2) binding favourability in conformer c (higher = worse leakage).
  * lambda, gamma >= 0 weight sensitivity and paralogue leakage. Defaults lambda=gamma=1.0 (the values in
    the design memo); chemical-liability terms are applied UPSTREAM as a hard developability gate
    (structural_alerts.py), not folded into S, so S stays an energetic quantity.

The move from "best score" to "worst-case robustness": min over conformers (not max/mean), an explicit
variance penalty, and a paralogue term that takes the WORST (max) leakage over every tested paralogue
conformer -- so a candidate cannot hide a paralogue counterexample in an untested pocket state.

THE CENTRAL CRITERION.  |receptor effect|  >  |conformer effect|.  A credible selective candidate's
NR4A3-vs-paralogue preference must exceed its frame-to-frame wobble; if the conformer effect dominates,
the "selectivity" is a geometry artefact (exactly the denovo_401 provenance situation). See
receptor_vs_conformer().

THE PANEL (design / validation / stress).  The panel is split so generalisation is TESTED, not assumed:
  * design      conformers -> used to generate / early-score candidates;
  * validation  conformers -> held-out, never seen by the generator or early scoring (the real test);
  * stress      conformers -> a minimally-open / occluded frame + the original AF2-opened design frame
                 (scoring a 401-derived scaffold there is a circularity probe, not a pass/fail).
A candidate that wins only on the design conformers is another overfit molecule; one that keeps its
NR4A3 preference on HELD-OUT experimental conformers is the compelling result. See panel_split_report().

SIGN CONVENTION.  Everything here is FAVOURABILITY (higher = more favourable binding = -dG), matching
nr4a3_8xtt_conformer_scoring.favourability / mmgbsa_energy. Callers pass dG and use favourabilities_from_dG,
or pass favourabilities directly. None means "not scored in this conformer" and is skipped (never coerced
to 0) so a docking failure cannot masquerade as weak binding.

PURITY.  Dependency-free (plain dicts/lists, hand-rolled mean/SD -- no numpy), so
tests/test_ensemble_robust_score.py exercises every path without any structure, docking, or scoring stack.
"""

# NR4A3 is the on-target receptor key; NR4A1/NR4A2 are the paralogue anti-targets.
TARGET = "3"
PARALOGUES = ("1", "2")

# Objective weights (design memo defaults). lambda penalises conformer sensitivity; gamma penalises the
# worst paralogue leakage. Both are configurable per call; these are only the defaults.
LAMBDA = 1.0
GAMMA = 1.0

# EXTENDED objective (S_ext) weights. The redesign plan asks for the fuller ranking objective
#   S_ext = min_c M_{3,c} - lambda*SD - gamma*max B - gamma_c*C - eta*L
# adding an explicit anti-target-COUNTEREXAMPLE term C (# panel conformers where a paralogue is CLEARLY
# favoured) and a chemical-LIABILITY term L (structural-alert count). These are kept in a SEPARATE
# S_ext, never folded into S, so the base S stays a pure energetic quantity (design note above) while the
# ranking can optionally penalise molecules that fail in some frames or carry developability liabilities.
GAMMA_C = 1.0                 # per strong anti-target counterexample (favourability units)
ETA = 0.5                     # per chemical-liability alert (favourability units)
# A "strong" counterexample = a conformer whose selectivity margin is at least this far BELOW zero (a
# paralogue clearly beats NR4A3 there, not just a near-tie). Distinguishes a real reversal from noise.
COUNTEREXAMPLE_THRESHOLD = 1.0

# A panel needs at least this many scored NR4A3 conformers before its SD (conformer sensitivity) is
# meaningful. With 1 conformer SD is trivially 0 and would make a single-frame candidate look robust.
MIN_CONFORMERS_FOR_SD = 2


# ---------------------------------------------------------------------------
# small pure numerics (no numpy)
# ---------------------------------------------------------------------------
def favourability(dG):
    """-dG (higher = tighter binding). None -> None (unscored stays unscored)."""
    return None if dG is None else -float(dG)


def favourabilities_from_dG(dG_by_conformer):
    """{conformer -> dG|None} -> {conformer -> favourability|None}. Pure."""
    return {c: favourability(v) for c, v in (dG_by_conformer or {}).items()}


def _clean(values):
    """Drop None; return list of floats."""
    return [float(v) for v in values if v is not None]


def _mean(values):
    xs = _clean(values)
    return sum(xs) / len(xs) if xs else None


def _population_sd(values):
    """POPULATION SD (ddof=0) across the panel. The conformer panel is the whole population we score over
    (a fixed, prespecified set), not a sample of a larger one, so ddof=0 is the honest spread. Defined for
    n>=1 (n==1 -> 0.0). Callers gate on MIN_CONFORMERS_FOR_SD before trusting a 0.0. None if no data."""
    xs = _clean(values)
    if not xs:
        return None
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5


# ---------------------------------------------------------------------------
# per-candidate ensemble-robust score S
# ---------------------------------------------------------------------------
def per_conformer_margins(scores, paralogues=PARALOGUES, target=TARGET):
    """Per-conformer selectivity margin  M_{3,c} - max_p B_{p,c}  over the conformers where NR4A3 AND at
    least one paralogue are both scored.

    `scores`: {receptor_key -> {conformer_id -> favourability|None}} with keys target + paralogues.
    Returns {conformer_id -> margin} (favourability units; > 0 = NR4A3-favoured in that conformer). A
    conformer missing the NR4A3 score, or every paralogue score, is omitted. Pure."""
    tgt = scores.get(target, {}) or {}
    out = {}
    for c, m3 in tgt.items():
        if m3 is None:
            continue
        para_here = [scores.get(p, {}).get(c) for p in paralogues]
        para_here = [x for x in para_here if x is not None]
        if not para_here:
            continue
        out[c] = float(m3) - max(para_here)          # worst (max-favourable) paralogue in this conformer
    return out


def counterexample_report(margins, threshold=COUNTEREXAMPLE_THRESHOLD):
    """Summarise where a candidate's per-conformer selectivity margin turns AGAINST NR4A3.

    `margins`: {conformer_id -> margin} (favourability units; >0 = NR4A3-favoured), e.g. from
    per_conformer_margins(). Returns:
      n_sign_reversals       : # conformers with margin < 0            (any reversal, incl. near-ties),
      n_counterexamples      : # conformers with margin <= -threshold  (STRONG paralogue counterexamples),
      counterexample_conformers : sorted ids of the strong counterexamples,
      worst_counterexample   : the most-negative margin (None if no margins),
      worst_counterexample_at: the conformer achieving it.
    Pure; threshold >= 0."""
    items = [(c, m) for c, m in (margins or {}).items() if m is not None]
    n_rev = sum(1 for _, m in items if m < 0)
    cx = sorted(c for c, m in items if m <= -abs(threshold))
    worst = min(items, key=lambda cm: cm[1]) if items else None
    return {"n_sign_reversals": n_rev, "n_counterexamples": len(cx),
            "counterexample_conformers": cx,
            "worst_counterexample": (worst[1] if worst else None),
            "worst_counterexample_at": (worst[0] if worst else None)}


def robust_score(scores, lam=LAMBDA, gamma=GAMMA, paralogues=PARALOGUES, target=TARGET,
                 gamma_c=GAMMA_C, eta=ETA, liabilities=None,
                 counterexample_threshold=COUNTEREXAMPLE_THRESHOLD):
    """The ensemble-robust score S for ONE candidate over ONE conformer panel.

    Returns a dict:
      worst_nr4a3        : min_c M_{3,c}                       (worst-case NR4A3 favourability),
      mean_nr4a3         : mean_c M_{3,c},
      sensitivity        : SD_c(M_{3,c})                       (population SD; the conformer-wobble penalty),
      sensitivity_assessable : n_nr4a3 >= MIN_CONFORMERS_FOR_SD (else SD is not trustworthy),
      worst_paralogue    : max_{p,c} B_{p,c}                   (worst paralogue leakage anywhere in panel),
      worst_paralogue_at : (receptor_key, conformer_id) achieving it,
      per_conformer_margin : {c -> M_{3,c} - max_p B_{p,c}},
      min_margin         : min_c margin                        (worst-case selectivity margin, the rank key),
      mean_margin        : mean_c margin,
      n_nr4a3            : # conformers with an NR4A3 score,
      n_margin           : # conformers with a computable margin,
      n_sign_reversals   : # conformers where the margin turns against NR4A3 (margin < 0),
      n_counterexamples  : # STRONG anti-target counterexamples (margin <= -counterexample_threshold),
      counterexample_conformers : sorted ids of those strong counterexamples,
      liabilities        : the chemical-liability count passed in (echoed; None if not supplied),
      S                  : min_c M_{3,c} - lam*SD - gamma*worst_paralogue     (PURE ENERGETIC core, unchanged),
      S_ext              : S - gamma_c*n_counterexamples - eta*(liabilities or 0)  (full ranking objective),
      lam, gamma, gamma_c, eta, counterexample_threshold : echoed weights.
    Missing numbers propagate as None (never 0). S_ext is None whenever S is None. Pure.

    S stays a pure energetic quantity; the counterexample (C) and liability (L) penalties live only in
    S_ext (redesign plan). Pass `liabilities` = structural_alerts count (int) to activate the L term."""
    tgt_vals = list((scores.get(target, {}) or {}).values())
    worst_nr4a3 = min(_clean(tgt_vals)) if _clean(tgt_vals) else None
    mean_nr4a3 = _mean(tgt_vals)
    sd = _population_sd(tgt_vals)
    n_nr4a3 = len(_clean(tgt_vals))

    worst_paralogue = None
    worst_at = None
    for p in paralogues:
        for c, v in (scores.get(p, {}) or {}).items():
            if v is None:
                continue
            if worst_paralogue is None or v > worst_paralogue:
                worst_paralogue = float(v)
                worst_at = (p, c)

    margins = per_conformer_margins(scores, paralogues, target)
    min_margin = min(margins.values()) if margins else None
    mean_margin = _mean(list(margins.values()))
    cx = counterexample_report(margins, counterexample_threshold)

    S = None
    if worst_nr4a3 is not None and sd is not None and worst_paralogue is not None:
        S = worst_nr4a3 - lam * sd - gamma * worst_paralogue
    liab = None if liabilities is None else int(liabilities)
    S_ext = None if S is None else S - gamma_c * cx["n_counterexamples"] - eta * (liab or 0)

    return {
        "worst_nr4a3": worst_nr4a3, "mean_nr4a3": mean_nr4a3,
        "sensitivity": sd, "sensitivity_assessable": n_nr4a3 >= MIN_CONFORMERS_FOR_SD,
        "worst_paralogue": worst_paralogue, "worst_paralogue_at": worst_at,
        "per_conformer_margin": margins, "min_margin": min_margin, "mean_margin": mean_margin,
        "n_nr4a3": n_nr4a3, "n_margin": len(margins),
        "n_sign_reversals": cx["n_sign_reversals"], "n_counterexamples": cx["n_counterexamples"],
        "counterexample_conformers": cx["counterexample_conformers"],
        "worst_counterexample": cx["worst_counterexample"],
        "liabilities": liab,
        "S": S, "S_ext": S_ext,
        "lam": lam, "gamma": gamma, "gamma_c": gamma_c, "eta": eta,
        "counterexample_threshold": counterexample_threshold,
    }


# ---------------------------------------------------------------------------
# the central criterion: |receptor effect| > |conformer effect|
# ---------------------------------------------------------------------------
def receptor_vs_conformer(scores, paralogues=PARALOGUES, target=TARGET):
    """Is the NR4A3-vs-paralogue (receptor) effect bigger than the frame-to-frame (conformer) effect?

    receptor_effect = mean_c M_{3,c} - max_p mean_c B_{p,c}   (how much NR4A3 is preferred on average),
    conformer_effect = SD_c(M_{3,c})                          (how much NR4A3 favourability wobbles),
    criterion_met   = |receptor_effect| > |conformer_effect|.

    Returns those three plus `assessable` (needs >=MIN_CONFORMERS_FOR_SD NR4A3 conformers and >=1 paralogue
    mean). If the conformer effect dominates, the apparent selectivity is a geometry artefact -- the
    denovo_401 provenance failure mode -- and criterion_met is False. Pure."""
    tgt_mean = _mean(list((scores.get(target, {}) or {}).values()))
    para_means = [_mean(list((scores.get(p, {}) or {}).values())) for p in paralogues]
    para_means = [m for m in para_means if m is not None]
    conformer_effect = _population_sd(list((scores.get(target, {}) or {}).values()))
    n_nr4a3 = len(_clean(list((scores.get(target, {}) or {}).values())))

    receptor_effect = None
    if tgt_mean is not None and para_means:
        receptor_effect = tgt_mean - max(para_means)     # worst paralogue on average

    assessable = (n_nr4a3 >= MIN_CONFORMERS_FOR_SD) and bool(para_means)
    criterion_met = None
    if receptor_effect is not None and conformer_effect is not None and assessable:
        criterion_met = abs(receptor_effect) > abs(conformer_effect)

    return {"receptor_effect": receptor_effect, "conformer_effect": conformer_effect,
            "criterion_met": criterion_met, "assessable": assessable, "n_nr4a3": n_nr4a3}


# ---------------------------------------------------------------------------
# design / validation / stress panel split
# ---------------------------------------------------------------------------
def _subset(scores, conformer_ids, target=TARGET, paralogues=PARALOGUES):
    """Restrict `scores` to a set of conformer ids (across target + paralogues). Pure."""
    keep = set(conformer_ids)
    out = {}
    for rk in (target, *paralogues):
        row = scores.get(rk, {}) or {}
        out[rk] = {c: v for c, v in row.items() if c in keep}
    return out


def panel_split_report(scores, roles, lam=LAMBDA, gamma=GAMMA,
                       paralogues=PARALOGUES, target=TARGET):
    """Score a candidate SEPARATELY on the design / validation / stress conformer subsets, and judge
    generalisation.

    `roles`: {"design": [conformer_id,...], "validation": [...], "stress": [...]} (any subset may be
    empty/absent). Returns:
      by_role            : {role -> robust_score(subset)},
      full               : robust_score over ALL panel conformers,
      favoured_all_design    : NR4A3-favoured (margin > 0) in EVERY design conformer,
      favoured_all_validation: NR4A3-favoured in EVERY held-out validation conformer  (the key test),
      generalises        : favoured_all_design AND favoured_all_validation AND validation is non-empty,
      stress_survives    : NR4A3 preference not REVERSED (margin > 0) in every scored stress conformer
                           (None if no stress conformer scored),
      rationale          : plain-English, honestly scoped.
    "Favoured in every conformer of a role" uses the per-conformer margins that are computable in that
    role (conformers lacking a score are not counted for/against). Pure."""
    roles = roles or {}
    by_role = {}
    favoured = {}
    for role in ("design", "validation", "stress"):
        ids = roles.get(role) or []
        sub = _subset(scores, ids, target, paralogues)
        rs = robust_score(sub, lam, gamma, paralogues, target)
        by_role[role] = rs
        margins = rs["per_conformer_margin"]
        favoured[role] = (len(margins) > 0 and all(m > 0 for m in margins.values()))

    all_ids = [c for ids in roles.values() for c in (ids or [])]
    full = robust_score(_subset(scores, all_ids, target, paralogues), lam, gamma, paralogues, target)

    has_validation = bool(by_role["validation"]["per_conformer_margin"])
    generalises = bool(favoured["design"] and favoured["validation"] and has_validation)

    stress_margins = by_role["stress"]["per_conformer_margin"]
    stress_survives = all(m > 0 for m in stress_margins.values()) if stress_margins else None

    if generalises:
        rationale = ("NR4A3-favoured in every design AND every held-out validation conformer -> the "
                     "preference generalises across experimental geometry (not a design-frame overfit)")
    elif favoured["design"] and not has_validation:
        rationale = "favoured on the design conformers but NO validation conformer was scored -> untested"
    elif favoured["design"] and not favoured["validation"]:
        rationale = ("favoured on the design conformers but NOT on all held-out validation conformers -> "
                     "design-frame overfit (the failure mode this panel is built to catch)")
    else:
        rationale = "not NR4A3-favoured across the design conformers"

    return {"by_role": by_role, "full": full,
            "favoured_all_design": favoured["design"],
            "favoured_all_validation": favoured["validation"],
            "generalises": generalises,
            "stress_survives": stress_survives,
            "rationale": rationale}


# ---------------------------------------------------------------------------
# benchmark comparison (must beat denovo_401 on a MATCHED multi-conformer panel)
# ---------------------------------------------------------------------------
def beats_benchmark(candidate_scores, benchmark_scores, lam=LAMBDA, gamma=GAMMA,
                    paralogues=PARALOGUES, target=TARGET, margin_eps=0.0):
    """Does a candidate beat the benchmark (denovo_401) on WORST-CASE robustness over the SAME conformer
    panel? A better single-frame score is explicitly NOT enough (redesign rule).

    Compares S and min_margin (worst-case selectivity margin). Returns:
      candidate / benchmark : the two robust_score dicts,
      dS                    : S_cand - S_bench   (None if either S is None),
      d_min_margin          : min_margin_cand - min_margin_bench,
      beats_S               : dS > margin_eps,
      beats_min_margin      : d_min_margin > margin_eps,
      beats                 : beats_S AND beats_min_margin  (must win on BOTH worst-case axes),
      rationale.
    Callers should pass the candidate and benchmark scored on the identical conformer set. Pure."""
    cand = robust_score(candidate_scores, lam, gamma, paralogues, target)
    bench = robust_score(benchmark_scores, lam, gamma, paralogues, target)

    dS = None if (cand["S"] is None or bench["S"] is None) else cand["S"] - bench["S"]
    dmm = (None if (cand["min_margin"] is None or bench["min_margin"] is None)
           else cand["min_margin"] - bench["min_margin"])
    beats_S = None if dS is None else dS > margin_eps
    beats_mm = None if dmm is None else dmm > margin_eps
    beats = bool(beats_S) and bool(beats_mm) if (beats_S is not None and beats_mm is not None) else None

    if beats:
        rationale = "beats the benchmark on BOTH worst-case S and worst-case selectivity margin"
    elif beats is False:
        rationale = "does not beat the benchmark on both worst-case axes (a single-frame win does not count)"
    else:
        rationale = "incomparable: S or min_margin undefined for candidate or benchmark on this panel"

    return {"candidate": cand, "benchmark": bench, "dS": dS, "d_min_margin": dmm,
            "beats_S": beats_S, "beats_min_margin": beats_mm, "beats": beats, "rationale": rationale}


# ---------------------------------------------------------------------------
# combined advancement verdict (the redesign's go/no-go for a NEW candidate)
# ---------------------------------------------------------------------------
def advancement_verdict(scores, roles, benchmark_scores=None,
                        protonation_robust=None, stereo_robust=None,
                        abfe_direction_consistent=None,
                        clears_generation_matched_null=None,
                        lam=LAMBDA, gamma=GAMMA, paralogues=PARALOGUES, target=TARGET):
    """Combine every prespecified advancement criterion for a NEW ensemble-designed candidate into one
    go/no-go, honestly reporting which criteria are unmet vs simply not-yet-assessed.

    Energetic criteria computed here from `scores` + `roles`:
      C1 favoured_all_design      : NR4A3-favoured in every prespecified design conformer,
      C2 generalises              : retains preference in every held-out validation conformer,
      C3 worst_case_selective     : min_margin > 0 (NR4A3-favoured in the WORST panel conformer),
      C4 receptor_gt_conformer    : |receptor effect| > |conformer effect|,
      C5 stress_survives          : preference not reversed in the stress conformers (None if unscored),
      C6 beats_benchmark          : beats denovo_401 on the matched panel (only if benchmark_scores given).
    External criteria passed in as tri-state flags (True/False/None=not-yet-assessed):
      C7 clears_generation_matched_null (generation_matched_null.py),
      C8 protonation_robust       (fep_species-style microstate check),
      C9 stereo_robust            (stereoisomer check),
      C10 abfe_direction_consistent (repaired ABFE gives same preference direction on >=2 NR4A3 conformers).

    Returns {criteria: {name: True|False|None}, unmet: [...], pending: [...], advance: bool|None,
    split, receptor_conformer, benchmark, rationale}. advance = True iff every ASSESSED criterion passes
    AND none is unknown; False if any assessed criterion fails; None if some are still pending and none
    has failed. Pure -- it decides, it does not run anything."""
    split = panel_split_report(scores, roles, lam, gamma, paralogues, target)
    rc = receptor_vs_conformer(scores, paralogues, target)
    full = split["full"]
    bench = (beats_benchmark(scores, benchmark_scores, lam, gamma, paralogues, target)
             if benchmark_scores is not None else None)

    crit = {
        "C1_favoured_all_design": split["favoured_all_design"] if split["by_role"]["design"]["per_conformer_margin"] else None,
        "C2_generalises": split["generalises"] if split["by_role"]["validation"]["per_conformer_margin"] else None,
        "C3_worst_case_selective": (None if full["min_margin"] is None else full["min_margin"] > 0),
        "C4_receptor_gt_conformer": rc["criterion_met"],
        "C5_stress_survives": split["stress_survives"],
        "C6_beats_benchmark": (bench["beats"] if bench is not None else None),
        "C7_clears_generation_matched_null": clears_generation_matched_null,
        "C8_protonation_robust": protonation_robust,
        "C9_stereo_robust": stereo_robust,
        "C10_abfe_direction_consistent": abfe_direction_consistent,
    }

    unmet = [k for k, v in crit.items() if v is False]
    pending = [k for k, v in crit.items() if v is None]
    if unmet:
        advance = False
        rationale = "HOLD -- failed: " + ", ".join(unmet)
    elif pending:
        advance = None
        rationale = "not yet advanceable -- pending: " + ", ".join(pending)
    else:
        advance = True
        rationale = "ADVANCE -- every prespecified criterion assessed and passed"

    return {"criteria": crit, "unmet": unmet, "pending": pending, "advance": advance,
            "split": split, "receptor_conformer": rc, "benchmark": bench, "rationale": rationale}


# ---------------------------------------------------------------------------
# ranking a field of candidates
# ---------------------------------------------------------------------------
def rank_candidates(candidates, lam=LAMBDA, gamma=GAMMA, paralogues=PARALOGUES, target=TARGET,
                    key="S", gamma_c=GAMMA_C, eta=ETA, liabilities_by_name=None,
                    counterexample_threshold=COUNTEREXAMPLE_THRESHOLD):
    """Rank a field of candidates by worst-case robustness.

    `candidates`: {name -> scores-dict}. `key`: "S" (default), "S_ext" (adds counterexample+liability
    penalties) or "min_margin". `liabilities_by_name`: optional {name -> structural-alert count} feeding
    the S_ext liability term (missing -> None -> no L penalty). Candidates whose key is None (incomputable
    on their panel) sort LAST, in stable name order. Returns a list of {name, rank, S, S_ext, min_margin,
    worst_nr4a3, sensitivity, worst_paralogue, n_counterexamples, n_sign_reversals}, best first. Pure."""
    liabilities_by_name = liabilities_by_name or {}
    rows = []
    for name, sc in (candidates or {}).items():
        rs = robust_score(sc, lam, gamma, paralogues, target, gamma_c, eta,
                          liabilities_by_name.get(name), counterexample_threshold)
        rows.append({"name": name, "S": rs["S"], "S_ext": rs["S_ext"], "min_margin": rs["min_margin"],
                     "worst_nr4a3": rs["worst_nr4a3"], "sensitivity": rs["sensitivity"],
                     "worst_paralogue": rs["worst_paralogue"],
                     "n_counterexamples": rs["n_counterexamples"],
                     "n_sign_reversals": rs["n_sign_reversals"]})
    rows.sort(key=lambda r: (r[key] is None, -(r[key] if r[key] is not None else 0.0), r["name"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows
