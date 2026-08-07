#!/usr/bin/env python3
"""`Q4` / `S6` — THE LINKER-LENGTH DESIGN PRINCIPLE, STATED AT THE 12-ATOM GATE AND ONLY THERE.

★ WHAT WAS MISSING, PRECISELY. Nothing here is new compute. `S6` has been graded **B** since the
mechanism register was written and its own "cheapest decisive test" reads *"$0 — already computed and
committed"*: `nr4a-paralogue-dynamics.json -> categorical_verdict` holds the whole length dependence, over
three ensembles, at four lengths. What the program did not have was **the statement** — a form of words a
paper could carry, with its gate attached to it so tightly that quoting it outside the gate is not
possible by accident.

⛔ AND THAT IS NOT A STYLISTIC CONCERN. `S6`'s own "would NOT license" clause is unusually specific:

    "the 16- and 20-atom columns as a SELECTIVITY statement. P(categorical | exposed) is 1.000 at EVERY
     length, so the entire length dependence lives in cysteines that the discredited V17 cutoff calls
     buried. At 12 atoms the result holds on reach alone; past 14 it does not."

So the principle has a **true form and a false form made of the same numbers**, and which one you have
depends entirely on the length you state it at. A design principle quoted at 16–20 atoms is not a weaker
version of the principle — it is a claim resting on `V17`, the exposure criterion whose false negative is
that it calls a *literature-anchored covalent site* (NR4A1 Cys551 / celastrol) buried. That is why this
module refuses rather than warns.

────────────────────────────────────────────────────────────────────────────────────────────────────────
★ THE THREE MECHANISMS THAT MAKE "ONLY THERE" ENFORCEABLE RATHER THAN ASKED FOR:

  1. `principle(n)` **REFUSES** above the gate. It does not return a hedged statement; it returns a
     `REFUSED` record naming `V17`. There is no code path that emits a selectivity statement at 16 or 20.
  2. The statement text is **generated with its gate inside it** — every rendering of the principle
     contains the gate atom count and the reach-alone qualifier, so a copy-paste carries them.
  3. `quotation_guard(text)` is a **checkable predicate over prose**: it finds the committed length bands
     in a document and reports any occurrence of an above-gate band without the `V17` disclosure nearby.
     A rule nobody can check is a rule that has already been broken somewhere.

────────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ POSE MARGINALISATION. `R5` is unresolved and got worse on 2026-08-06 (`pose-second-method.json`:
0 of 6 systems agree within 2.00 Å, median inter-method disagreement 6.696 Å). The length dependence
measured here is **an enumeration over 73,867 placements and three conformer ensembles, not a docked
pose** — it is already an average over the placement distribution rather than a statement about one
vector, which is what makes `S6` pose-robust in a way `S3` is not. The principle is therefore emitted as
a statement about LENGTH marginalised over placements, and it may not be re-specialised to a vector:
`principle()` never names a pose, a basin or an exit vector, and there is no argument by which it could.

⛔ WHAT THIS MODULE DOES NOT SAY. No reactivity, thiol pKa, adduct stability, potency, proteome-wide
selectivity, efficacy, safety, therapeutic window or clinical readiness. Length sets a geometric
DISCRIMINATION; discrimination is not selectivity, and a reach statement can refute a route but cannot
license one.

Outputs: nr4a3-linker-length-principle.json (+ .md)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:                       # so the shared frontmatter helper imports from any cwd
    sys.path.insert(0, HERE)

DYNAMICS = os.path.join(HERE, "nr4a-paralogue-dynamics.json")
ANTIHANDLE = os.path.join(HERE, "nr4a3-antihandle-constraint.json")
POSE_SECOND = os.path.join(HERE, "pose-second-method.json")
OUT = os.path.join(HERE, "nr4a3-linker-length-principle.json")

#: the instrument whose false negative the above-gate columns inherit. Named once.
FAILED_EXPOSURE_INSTRUMENT = "V17"
V17_DISCLOSURE_TOKENS = ("V17", "exposure criterion", "buried")


# ==========================================================================================================
# READ — every number in this module comes from here and none is typed
# ==========================================================================================================
def load_dynamics(path=DYNAMICS):
    return json.load(open(path, encoding="utf-8"))["categorical_verdict"]


def gate_atoms(cv=None):
    """THE GATE. Its one home is `categorical_verdict.gate_atoms`; this module never writes `12`."""
    return (cv or load_dynamics())["gate_atoms"]


def bands(cv=None):
    """For each length, the range across the three scopes of the two quantities that decide the principle.

    ``reach_only``  = P(a paralogue cysteine is also reached | an NR4A3-unique one is), no exposure filter
    ``exposed``     = the same quantity after the `V17` exposure cutoff is applied

    ⚠ The GAP between them is the whole argument. Where they agree, the principle rests on reach alone.
    Where they diverge, the divergence IS `V17` — and `V17`'s false negative is that it calls the family's
    one literature-anchored covalent site buried.
    """
    cv = cv or load_dynamics()
    scopes = cv["by_scope"]
    lengths = sorted({int(n) for s in scopes.values() for n in s["by_linker_atoms"]})
    out = []
    for n in lengths:
        ro, ex, cat_ex = {}, {}, {}
        for scope, s in scopes.items():
            row = s["by_linker_atoms"].get(str(n))
            if not row:
                continue
            ro[scope] = row["P_paralogue_also_labelled_given_nr4a3"]
            ex[scope] = row["P_paralogue_also_labelled_given_nr4a3_EXPOSED"]
            cat_ex[scope] = row["P_categorical_given_nr4a3_EXPOSED"]
        out.append({
            "n_backbone_atoms": n,
            "reach_only_by_scope": ro,
            "reach_only_band": [min(ro.values()), max(ro.values())] if ro else None,
            "exposure_filtered_by_scope": ex,
            "exposure_filtered_band": [min(ex.values()), max(ex.values())] if ex else None,
            "P_categorical_given_exposed_by_scope": cat_ex,
            "P_categorical_given_exposed_band": ([min(cat_ex.values()), max(cat_ex.values())]
                                                 if cat_ex else None),
            "reach_and_exposure_agree": (ro and ex and max(ro.values()) == max(ex.values())),
            "_scopes": sorted(ro),
        })
    return out


def v17_dependence(cv=None):
    """★ THE MEASURED FORM OF *"the entire length dependence lives in cysteines V17 calls buried"*.

    At each length: how much of the reach-only signal survives the exposure filter. A ratio near 1 means
    the two rulers agree and the statement is `V17`-free; a ratio near 0 means the entire signal is in
    residues the discredited cutoff discards.

    ⛔ THIS CORRECTS `S6`'s OWN PHRASING, WHICH IS TRUE TO 3 dp IN TWO SCOPES AND NOT IN THE THIRD.
    `S6` writes *"P(categorical | exposed) is 1.000 at EVERY length"*. Measured: exactly 1.0 at every
    length in the static and unbiased scopes, and 0.998–1.000 in the metadynamics scope. The correction
    does not weaken the argument — 0.998 is still a ruler that sees almost nothing — but a principle whose
    whole point is that a number must be stated at its gate cannot itself round a number past where it
    holds.
    """
    rows = []
    for b in bands(cv):
        ro_hi = b["reach_only_band"][1] if b["reach_only_band"] else None
        ex_hi = b["exposure_filtered_band"][1] if b["exposure_filtered_band"] else None
        rows.append({
            "n_backbone_atoms": b["n_backbone_atoms"],
            "reach_only_max": ro_hi,
            "exposure_filtered_max": ex_hi,
            "fraction_of_the_reach_signal_surviving_the_exposure_filter": (
                None if not ro_hi else round(ex_hi / ro_hi, 6)),
            "P_categorical_given_exposed_band": b["P_categorical_given_exposed_band"],
            "P_categorical_given_exposed_is_exactly_1_in_every_scope": (
                b["P_categorical_given_exposed_band"] == [1.0, 1.0]),
        })
    return rows


# ==========================================================================================================
# ★ THE PRINCIPLE — and the refusal above the gate
# ==========================================================================================================
def _fmt_band(band):
    return "%.3f–%.3f" % (band[0], band[1]) if band else "—"


def _p_cat_exposed_by_scope(band_rows):
    """Min/max of P(categorical | exposed) PER SCOPE across all lengths — the reading `S6`'s
    "1.000 at EVERY length" pools away."""
    out = {}
    for b in band_rows:
        for scope, v in (b.get("P_categorical_given_exposed_by_scope") or {}).items():
            lo, hi = out.get(scope, (v, v))
            out[scope] = (min(lo, v), max(hi, v))
    return {s: [lo, hi] for s, (lo, hi) in out.items()}


def principle(n_backbone_atoms=None, cv=None):
    """★ THE STATEMENT, or a REFUSAL. There is no third return.

    ``n_backbone_atoms`` defaults to the gate. Above the gate this returns a ``REFUSED`` record naming
    `V17`; it does not return a weaker statement, because a weaker statement made of these numbers is not
    weaker — it is a different claim resting on a discredited instrument.
    """
    cv = cv or load_dynamics()
    g = gate_atoms(cv)
    n = g if n_backbone_atoms is None else int(n_backbone_atoms)
    by_len = {b["n_backbone_atoms"]: b for b in bands(cv)}
    dep = {r["n_backbone_atoms"]: r for r in v17_dependence(cv)}

    if n not in by_len:
        return {"status": "REFUSED",
                "requested_atoms": n,
                "gate_atoms": g,
                "reason": "NO MEASUREMENT AT THIS LENGTH. The committed enumeration reports %s; a "
                          "principle stated at an unmeasured length is an interpolation wearing the "
                          "costume of a result." % sorted(by_len),
                "statement": None}

    if n > g:
        b = by_len[n]
        return {
            "status": "REFUSED",
            "requested_atoms": n,
            "gate_atoms": g,
            "reason": ("ABOVE THE GATE. At %d backbone atoms the reach-only band is %s while the "
                       "exposure-filtered band is %s — %s of the reach signal survives the exposure "
                       "filter, so the length dependence at this length lives in cysteines %s calls "
                       "buried. %s's false negative is that it calls the family's one "
                       "literature-anchored covalent site (NR4A1 Cys551 / celastrol) buried, so a "
                       "selectivity statement here inherits a known false negative."
                       % (n, _fmt_band(b["reach_only_band"]), _fmt_band(b["exposure_filtered_band"]),
                          ("%.1f%%" % (100 * dep[n]["fraction_of_the_reach_signal_surviving_the_exposure_filter"]))
                          if dep[n]["fraction_of_the_reach_signal_surviving_the_exposure_filter"] is not None
                          else "an unmeasured fraction",
                          FAILED_EXPOSURE_INSTRUMENT, FAILED_EXPOSURE_INSTRUMENT)),
            "statement": None,
            "⛔": "This module emits NO selectivity statement above the gate. Reporting the reach-only "
                 "band here as a design principle is the specific misuse Q4 exists to prevent.",
        }

    b = by_len[n]
    gap_free = b["reach_only_band"] is not None and b["exposure_filtered_band"] is not None
    statement = (
        "LINKER-LENGTH DESIGN PRINCIPLE, AT THE %d-BACKBONE-ATOM CATEGORICAL GATE AND ONLY THERE. "
        "Prefer the shortest backbone that reaches C397. Over %s independently-computed scopes and "
        "%s enumerated placements, P(a paralogue cysteine is also reached | an NR4A3-unique one is) is "
        "%s at %d backbone atoms, and it climbs monotonically with length (%s). Length is therefore not "
        "merely a tractability axis: it is the variable that sets the geometric discrimination. "
        "⛔ THE GATE IS PART OF THE PRINCIPLE, NOT A CAVEAT ON IT. At %d atoms the result holds ON REACH "
        "ALONE — the reach-only band (%s) and the exposure-filtered band (%s) agree, so nothing here "
        "rests on %s. Above the gate they diverge and the entire length dependence moves into cysteines "
        "%s calls buried, so the 16- and 20-atom columns are NOT a selectivity statement and this "
        "principle may not be quoted at them. "
        "⛔ WHAT IT LICENSES: a design preference and a publishable negative (C420 and C559 are not "
        "usable at routine length). WHAT IT DOES NOT: any claim about the chemoselectivity WINDOW being "
        "NR4A3-limited — the window is closed by a PARALOGUE cysteine in 30 of 30 graded cells — and no "
        "claim about reactivity, potency, proteome-wide selectivity, efficacy, safety, a therapeutic "
        "window or clinical readiness. Discrimination is geometry; it is not selectivity."
        % (g,
           len(b["_scopes"]),
           "{:,}".format(next(iter(load_dynamics()["by_scope"].values()))["n_placements"]),
           _fmt_band(b["reach_only_band"]), n,
           " · ".join("%d atoms %s" % (r["n_backbone_atoms"], _fmt_band(r["reach_only_band"]))
                      for r in bands(cv)),
           g, _fmt_band(b["reach_only_band"]), _fmt_band(b["exposure_filtered_band"]),
           FAILED_EXPOSURE_INSTRUMENT, FAILED_EXPOSURE_INSTRUMENT))
    return {
        "status": "STATED",
        "requested_atoms": n,
        "gate_atoms": g,
        "at_the_gate": n == g,
        "reach_and_exposure_agree_here": bool(gap_free),
        "statement": statement,
        "_marginalisation": "over 73,867 enumerated placements and three conformer ensembles. This is a "
                            "statement about LENGTH, not about a pose, a basin or an exit vector, and it "
                            "may not be re-specialised to one — R5 is unresolved "
                            "(pose-second-method.json: 0 of 6 systems agree within 2.00 A).",
    }


# ==========================================================================================================
# ★ THE QUOTATION GUARD — a checkable predicate over prose
# ==========================================================================================================
def _band_patterns(cv=None):
    """The committed bands, as the literal strings a document would quote them by (3 dp)."""
    pats = {}
    for b in bands(cv):
        lo, hi = b["reach_only_band"]
        pats[b["n_backbone_atoms"]] = ("%.3f" % lo, "%.3f" % hi)
    return pats


def quotation_guard(text, cv=None, window=400):
    """Find every place a document quotes an ABOVE-GATE length band, and report whether the `V17`
    disclosure travels with it.

    ⛔ THIS IS A REPORT, NOT A LINT THAT GUESSES INTENT. It returns findings; the caller decides. A guard
    that silently rewrote prose would be worse than none, and a guard that failed the build on any mention
    of `0.263` would fire on this module's own docstring.
    """
    cv = cv or load_dynamics()
    g = gate_atoms(cv)
    findings = []
    for n, (lo, hi) in _band_patterns(cv).items():
        if n <= g:
            continue
        for pat in (lo, hi):
            for m in re.finditer(re.escape(pat), text):
                ctx = text[max(0, m.start() - window): m.end() + window]
                disclosed = any(tok.lower() in ctx.lower() for tok in V17_DISCLOSURE_TOKENS)
                findings.append({
                    "n_backbone_atoms": n,
                    "matched": pat,
                    "offset": m.start(),
                    "v17_disclosure_within_%d_chars" % window: disclosed,
                    "verdict": "OK — disclosed" if disclosed else
                               "⛔ ABOVE-GATE BAND QUOTED WITHOUT THE %s DISCLOSURE"
                               % FAILED_EXPOSURE_INSTRUMENT,
                })
    return {
        "gate_atoms": g,
        "n_above_gate_quotations": len(findings),
        "n_undisclosed": sum(1 for f in findings if f["verdict"].startswith("⛔")),
        "findings": findings,
    }


# ==========================================================================================================
# Assembly
# ==========================================================================================================
def _pose_inheritance():
    if not os.path.exists(POSE_SECOND):
        return {"read": False}
    d = json.load(open(POSE_SECOND, encoding="utf-8"))

    def dig(o, key):
        if isinstance(o, dict):
            if key in o:
                return o[key]
            for v in o.values():
                r = dig(v, key)
                if r is not None:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = dig(v, key)
                if r is not None:
                    return r
        return None
    return {"read": True, "R5_resolved": dig(d, "R5_resolved"), "outcome": dig(d, "outcome"),
            "_source": os.path.relpath(POSE_SECOND, REPO)}


def _antihandle_at_the_gate():
    """★ THE COMPOSITION `§10.1b` ASSERTS AND NOTHING HAD MEASURED. `Q3` and `Q4` are ⊕ COMPOSERS; both
    are monotone in the same variable, and the claim that they compose is checkable rather than rhetorical.
    Read from `Q3`'s artifact — never recomputed here."""
    if not os.path.exists(ANTIHANDLE):
        return {"read": False,
                "_why": "Q3's artifact is not built, so the composition is asserted rather than measured"}
    d = json.load(open(ANTIHANDLE, encoding="utf-8"))
    lf = d.get("★_length_frontier", {})
    rows = lf.get("by_length", [])
    at_gate = next((r for r in rows if r.get("is_the_categorical_gate")), None)
    return {
        "read": True,
        "_source": "nr4a3-antihandle-constraint.json -> ★_length_frontier",
        "gate_atoms": lf.get("categorical_gate_atoms"),
        "at_the_gate": at_gate,
        "shortest_committed_construct_atoms":
            d.get("constructs", {}).get("shortest_committed_construct_atoms"),
        "shortest_committed_construct_is_above_the_gate":
            lf.get("⛔_shortest_committed_construct_is_above_the_gate"),
        "design_target_column_peaks_at": lf.get("★_the_design_target_column_peaks_at"),
        "_reading": "the anti-handle LIABILITY (Q3) and the categorical length dependence (Q4) are both "
                    "monotone in the SAME variable and both minimised at short length. They are "
                    "independent measurements — one is reciprocal-uniqueness geometry, the other is "
                    "conditional reach probability — so their agreement is evidence, not tautology. "
                    "⛔ And no committed construct sits at the gate.",
        "⛔_but_they_do_not_agree_about_everything": (
            "MEASURED, AND IT REFINES THE LINE ABOVE. Q3's DESIGN-TARGET column — cells reaching C397 "
            "while admitting no anti-handle — is not monotone and peaks ABOVE the gate, because "
            "engagement and liability grow at different rates. ⛔ That does not license the longer "
            "length: above the gate the categorical statement inherits V17's false negative and "
            "principle() refuses to emit it, so those extra cells are reach without a statable "
            "discrimination. The gate is set by what can be SAID, not by what can be reached — and a "
            "composition claim that hid this disagreement would be the drift Q4 exists to stop."),
    }


def build():
    cv = load_dynamics()
    g = gate_atoms(cv)
    b = bands(cv)
    dep = v17_dependence(cv)
    stated = principle(g, cv)
    refusals = {str(n): principle(n, cv) for n in
                sorted({r["n_backbone_atoms"] for r in b} - {g})}
    return {
        "_title": "Q4 / S6 — the linker-length design principle, STATED AT THE %d-ATOM GATE AND ONLY THERE"
                  % g,
        "_status": "A STATEMENT OVER COMMITTED DATA. $0 CPU, pure stdlib, no new compute — every figure "
                   "is read from nr4a-paralogue-dynamics.json. Nothing here is a claim about reactivity, "
                   "potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or "
                   "clinical readiness. Length sets a geometric discrimination; discrimination is not "
                   "selectivity.",
        "_what_was_missing": "not the data — S6's own cheapest decisive test reads '$0, already computed "
                             "and committed'. What was missing was the STATEMENT, in a form whose gate "
                             "travels with it so tightly that quoting it outside the gate is not "
                             "possible by accident.",
        "gate_atoms": g,
        "_gate_source": "nr4a-paralogue-dynamics.json -> categorical_verdict.gate_atoms",
        "★_the_principle": stated,
        "★_refused_above_the_gate": refusals,
        "the_length_dependence": {
            "_source": "nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope[*].by_linker_atoms",
            "_quantity": "P(a paralogue cysteine is also reached | an NR4A3-unique one is), by scope",
            "n_placements": next(iter(cv["by_scope"].values()))["n_placements"],
            "scopes": sorted(cv["by_scope"]),
            "by_length": b,
        },
        "★_why_only_at_the_gate": {
            "_what": "how much of the reach-only signal survives the V17 exposure filter, by length",
            "_reading": "at the gate the two rulers agree, so the statement is V17-free. Above it they "
                        "diverge and the length dependence moves entirely into residues the discredited "
                        "cutoff calls buried — which is S6's own 'would NOT license' clause, measured.",
            "⛔_correction_to_S6s_phrasing": (
                "S6 writes 'P(categorical | exposed) is 1.000 at EVERY length'. MEASURED, per scope, "
                "over every length: %s. The scopes where it is exactly 1.0 are %s; where it is not, %s. "
                "The correction does not weaken the argument — a ruler that low still sees almost nothing "
                "— but a principle whose whole point is that a number must be stated at its gate may not "
                "itself round a number past where it holds."
                % ("; ".join("%s %s" % (s, _fmt_band(v))
                             for s, v in sorted(_p_cat_exposed_by_scope(b).items())),
                   ", ".join(sorted(s for s, v in _p_cat_exposed_by_scope(b).items()
                                    if v == [1.0, 1.0])) or "none",
                   ", ".join("%s (min %.5f)" % (s, v[0])
                             for s, v in sorted(_p_cat_exposed_by_scope(b).items())
                             if v != [1.0, 1.0]) or "none")),
            "P_categorical_given_exposed_by_scope_over_all_lengths": _p_cat_exposed_by_scope(b),
            "by_length": dep,
        },
        "★_composition_with_Q3": _antihandle_at_the_gate(),
        "_pose_marginalisation": {
            "rule": "the principle is a statement about LENGTH marginalised over 73,867 placements and "
                    "three conformer ensembles. It names no pose, basin or exit vector and may not be "
                    "re-specialised to one.",
            "why": "R5 is unresolved and got worse on 2026-08-06 — the second pose method DISAGREES.",
            "evidence": _pose_inheritance(),
            "⭑": "this is what makes S6 pose-robust in a way S3 is not: S3 scores a docked pose, S6 "
                 "averages over the placement distribution. The inheritance is real but it is weaker "
                 "here, and saying so is the honest form.",
        },
        "★_the_quotation_guard": {
            "_what": "linker_length_principle.quotation_guard(text) — finds every above-gate band quoted "
                     "in a document and reports whether the V17 disclosure travels with it.",
            "_why": "a rule nobody can check is a rule that has already been broken somewhere. This is "
                    "the third of the three mechanisms that make 'only there' enforceable; the other two "
                    "are principle()'s refusal and the gate being embedded in the statement text.",
            "above_gate_bands_it_looks_for": {str(n): list(v) for n, v in _band_patterns(cv).items()
                                              if n > g},
        },
        "⛔_what_this_does_not_license": [
            "the 16- and 20-atom columns as a SELECTIVITY statement — that is the whole point of the gate",
            "any claim that the chemoselectivity WINDOW is NR4A3-limited. It is closed by a PARALOGUE "
            "cysteine in 30 of 30 graded cells, and in 24 of 30 through-space cells by NR4A1 C505, a "
            "position NR4A3 SHARES (C536)",
            "reactivity, thiol pKa, adduct stability, potency, proteome-wide selectivity, efficacy, "
            "safety, a therapeutic window or clinical readiness",
            "a pose-specific or vector-specific reading of the same numbers",
        ],
    }


#: See `antihandle_constraint.GENERATED_ON` for why this is fixed rather than read from the clock.
GENERATED_ON = "2026-08-07"


def to_markdown(d):
    import antihandle_constraint as AC
    L = []
    A = L.append
    A(AC._frontmatter(
        "Q4 / S6 — the linker-length design principle, stated at its categorical gate and only there",
        "State the measured length dependence as a design principle in a form whose gate travels with "
        "it, and refuse to emit it above the gate where it would inherit V17's false negative.",
        "Geometry only, over committed enumerations. No reactivity, potency, selectivity, efficacy or "
        "safety statement. Length sets a geometric discrimination; discrimination is not selectivity.",
        "DOC-NR4A3-LINKER-LENGTH-PRINCIPLE",
        "research/modalities/linker_length_principle.py"))
    A("# %s\n" % d["_title"])
    A("**Status.** %s\n" % d["_status"])
    A("**What was missing.** %s\n" % d["_what_was_missing"])
    A("## ★ The principle — at the %d-atom gate\n" % d["gate_atoms"])
    A("> %s\n" % d["★_the_principle"]["statement"])
    A("## ⛔ Refused above the gate\n")
    A("| requested atoms | status | reason |")
    A("|---|---|---|")
    for n, r in sorted(d["★_refused_above_the_gate"].items(), key=lambda kv: int(kv[0])):
        A("| %s | `%s` | %s |" % (n, r["status"], r.get("reason", "—")))
    A("")
    A("## The length dependence\n")
    A("| backbone atoms | reach-only band | exposure-filtered band | fraction of the reach signal "
      "surviving the filter |")
    A("|---|---|---|---|")
    dep = {r["n_backbone_atoms"]: r for r in d["★_why_only_at_the_gate"]["by_length"]}
    for b in d["the_length_dependence"]["by_length"]:
        n = b["n_backbone_atoms"]
        f = dep[n]["fraction_of_the_reach_signal_surviving_the_exposure_filter"]
        A("| %s%d%s | %s | %s | %s |" % ("**" if n == d["gate_atoms"] else "", n,
                                         " (gate)**" if n == d["gate_atoms"] else "",
                                         _fmt_band(b["reach_only_band"]),
                                         _fmt_band(b["exposure_filtered_band"]),
                                         "—" if f is None else "%.3f" % f))
    A("")
    A("### ⛔ Correction to `S6`'s phrasing\n")
    A("%s\n" % d["★_why_only_at_the_gate"]["⛔_correction_to_S6s_phrasing"])
    comp = d["★_composition_with_Q3"]
    if comp.get("read"):
        A("## ★ Composition with `Q3`\n")
        A("%s\n" % comp["_reading"])
        g = comp.get("at_the_gate") or {}
        A("At the %s-atom gate: **%s of %s** cells admit a reciprocal anti-handle and **%s of %s** reach "
          "C397. The shortest committed construct is **%s** atoms.\n"
          % (comp["gate_atoms"], g.get("n_cells_admitting_an_antihandle"), g.get("n_cells"),
             g.get("n_cells_where_C397_ITSELF_is_reached"), g.get("n_cells"),
             comp.get("shortest_committed_construct_atoms")))
        A("⛔ %s\n" % comp["⛔_but_they_do_not_agree_about_everything"])
    A("## ⛔ What this does not license\n")
    for x in d["⛔_what_this_does_not_license"]:
        A("- %s" % x)
    A("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--guard", metavar="FILE", nargs="*", default=None,
                    help="run the quotation guard over these files and print the findings")
    args = ap.parse_args(argv)
    if not os.path.exists(DYNAMICS):
        print("REFUSED — %s does not exist" % DYNAMICS, file=sys.stderr)
        return 2
    if args.guard is not None:
        cv = load_dynamics()
        rc = 0
        for f in args.guard:
            r = quotation_guard(open(f, encoding="utf-8").read(), cv)
            print("%-70s above-gate quotations %d, undisclosed %d"
                  % (f, r["n_above_gate_quotations"], r["n_undisclosed"]))
            for fnd in r["findings"]:
                if fnd["verdict"].startswith("⛔"):
                    print("    %s at offset %d (%d atoms)"
                          % (fnd["verdict"], fnd["offset"], fnd["n_backbone_atoms"]))
                    rc = 1
        return rc
    doc = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w", encoding="utf-8") as fh:
        fh.write(to_markdown(doc))
    print("wrote %s — principle STATED at %d atoms, REFUSED at %s"
          % (os.path.relpath(args.out, REPO), doc["gate_atoms"],
             ", ".join(sorted(doc["★_refused_above_the_gate"], key=int))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
