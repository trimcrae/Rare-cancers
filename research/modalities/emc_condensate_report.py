#!/usr/bin/env python3
"""Render the CALVADOS single-chain arm's findings note FROM its artifacts.

⛔ WHY A GENERATOR RATHER THAN A WRITTEN NOTE. Every number in the note is a number that already
exists in a committed artifact, and CLAUDE.md rule 1 says a total is derived and never typed. A
hand-written results note drifts from the artifact it describes the moment either moves, and nothing
catches it. `--check` fails the build when the committed note stops matching what the artifacts say.

⭐ AND THE INTERPRETATION IS GENERATED TOO, WHICH IS THE POINT. The prose block for each verdict and
each negative is fixed HERE, keyed off the scorer's output, so the note cannot say something the data
did not produce. It is the prespecification's §7 rendered as text rather than re-argued after the
fact.

Usage:  emc_condensate_report.py            # write the note
        emc_condensate_report.py --check    # fail if the committed note is stale
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT = os.path.join(HERE, "emc-condensate-calvados.json")
ELIGIBILITY = os.path.join(HERE, "emc-condensate-window-eligibility.json")
MANIFEST = os.path.join(HERE, "emc-condensate-constructs.json")
COMPOSITION = os.path.join(HERE, "emc-condensate-composition.json")
OUT = os.path.join(HERE, "emc-condensate-calvados-findings.md")

PRESPEC = "emc-condensate-calvados-prespecification.md"

VERDICT_PROSE = {
    "INCOMPLETE": (
        "**INCOMPLETE — the run set does not match the frozen manifest, so no verdict about any "
        "partner is emitted.** This is not a negative result and must never be read as one. An "
        "absent reading is not a reading of absence; the missing runs are named below and the arm "
        "is finished when they land."),
    "INSTRUMENT_FAILED": (
        "**INSTRUMENT_FAILED — a control or a provenance check did not hold, so every ν is "
        "withheld.** This is not a negative result. The prespecification separates the two by "
        "construction precisely so a broken instrument cannot be published as a finding about the "
        "disease. The failing conditions are named below."),
    "SEPARATION_OBSERVED": (
        "**SEPARATION_OBSERVED — at least one prespecified pair separates under rule D1.** What "
        "that means is bounded by §9 of the prespecification and repeated below: ν is a "
        "single-chain conformational observable, and a difference in ν between two retained "
        "partner segments is a difference in ν between two retained partner segments."),
    "NO_SEPARATION": (
        "**NO_SEPARATION — no prespecified pair separates under rule D1.** ⭐ This is a RESULT, not "
        "a failure. It says the model does not distinguish the reported partners' retained segments "
        "on this axis, which contradicts the differential prediction the route memo was about to "
        "build on."),
}

NEGATIVE_PROSE = {
    "NEGATIVE_COMPOSITION_ONLY": (
        "**N1 · composition-only.** Neither scrambled parent's ν moved from its parent by the "
        "separation threshold. Composition-preserving shuffles change the *order* of the sequence "
        "and nothing else, so the simulation is resolving nothing beyond amino-acid composition — "
        "and composition counting is already the manuscript's existing evidence. ⚠ Read with the "
        "verdict above: if partners also separate, that separation is real but is a composition "
        "effect, and CALVADOS has added a more expensive route to a number the paper already had."),
    "NEGATIVE_NO_STRATIFICATION": (
        "**N2 · no partner stratification.** No length-matched FET-vs-TCF12 pair separates. The "
        "differential prediction across the chimeras is not supported on this axis."),
    "NEGATIVE_WILDTYPE_NOT_SEPARATED": (
        "**N3 · the wild-type control does not separate.** NR4A3's own disordered AF1 is "
        "indistinguishable from the EWSR1 low-complexity window on this readout. The manuscript's "
        "central fusion-versus-wild-type asymmetry survives at the composition level and fails at "
        "the phase-behaviour level, and the manuscript has to say so."),
    "NEGATIVE_FET_NOT_SPECIAL": (
        "**N4 · FET identity carries no signal here.** None of the three length-matched pairs "
        "separates, so the clinical reading — that a TCF12-partnered patient is different on this "
        "axis — is unsupported by this instrument."),
}


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def _fmt(x, n=4):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.{n}f}"
    return str(x)


def render():
    res = _load(RESULT)
    elig = _load(ELIGIBILITY)
    man = _load(MANIFEST)
    if res is None or man is None:
        raise SystemExit("missing artifacts; run the lane first")

    roles = {c["id"]: c for c in man["constructs"]}
    L = []
    A = L.append

    A("---")
    A("id: DOC-EMC-CONDENSATE-CALVADOS-FINDINGS")
    A('title: "CALVADOS single-chain arm — what the run measured"')
    A("level: L4")
    A("kind: generated")
    A("status: generated")
    A("generator: research/modalities/emc_condensate_report.py")
    A("canonical_for: [emc-condensate-calvados-result]")
    A("purpose: >")
    A("  The measured result of the frozen CALVADOS single-chain arm, rendered from its artifacts so")
    A("  that no number here is typed.")
    A("scope: >")
    A("  The CALVADOS 2 single-chain arm only. No slab phase-coexistence run and no multi-domain run")
    A("  is reported, because neither was performed.")
    A("audience: [maintainers, external reviewers, autonomous research agents]")
    A("date: 2026-08-24")
    A("last_verified: 2026-08-24")
    A("---")
    A("# CALVADOS single-chain arm — what the run measured")
    A("")
    A(f"> ⚙ **GENERATED FILE — do not hand-edit.** Rendered by `emc_condensate_report.py` from")
    A(f"> [`emc-condensate-calvados.json`](./emc-condensate-calvados.json) and")
    A(f"> [`emc-condensate-window-eligibility.json`](./emc-condensate-window-eligibility.json).")
    A(f"> Every rule applied here was frozen in [`{PRESPEC}`](./{PRESPEC}) **before any simulation**;")
    A("> the prose for each verdict and each negative is fixed in the generator, so this note cannot")
    A("> say something the run did not produce.")
    A("")
    A("## 1 · Verdict")
    A("")
    A(VERDICT_PROSE.get(res.get("verdict"), f"**{res.get('verdict')}**"))
    A("")
    if res.get("reasons"):
        A("Conditions that fired:")
        A("")
        for r in res["reasons"][:20]:
            A(f"- {r}")
        if len(res["reasons"]) > 20:
            A(f"- …and {len(res['reasons']) - 20} more, in the artifact.")
        A("")
    for neg in res.get("negatives", []):
        A(NEGATIVE_PROSE.get(neg, f"**{neg}**"))
        A("")

    A("## 2 · What was run")
    A("")
    A(f"- Constructs in the frozen manifest: **{man['n_constructs']}**; runs: **{man['n_runs']}**; "
      f"analyses reduced: **{res.get('n_runs_reduced', 0)}**.")
    p = man["protocol"]
    A(f"- Protocol: CALVADOS 2, {p['temperature_K']} K, {p['ionic_strength_M']} M ionic strength, "
      f"pH {p['pH']}, {p['timestep_fs']} fs timestep, {p['n_frames']} frames × "
      f"{p['steps_per_frame']} steps, first {p['discard_frames']} discarded, "
      f"{p['box_nm']:.0f} nm box, {p['platform']} platform.")
    A(f"- Pooled replicate SD of ν: **{_fmt(res.get('pooled_replicate_sd_nu'))}**; "
      f"separation threshold (3 SD): **{_fmt(res.get('separation_threshold_nu'))}**.")
    A("")

    if elig:
        A("### 2.1 · Window eligibility (AlphaFold pLDDT, fetched before any simulation)")
        A("")
        A(f"Entry criterion, fixed before the fetch: at least "
          f"{elig['_fraction_required']:.0%} of window residues below pLDDT "
          f"{elig['_cutoff']:.0f}.")
        A("")
        A("| construct | window | residues read | mean pLDDT | fraction < 50 | eligible |")
        A("|---|---|---:|---:|---:|---|")
        for cid, w in elig["windows"].items():
            if not w.get("read"):
                A(f"| `{cid}` | — | — | — | — | not read |")
                continue
            A(f"| `{cid}` | {w['window']} | {w['n_residues_read']} | {w['mean_plddt']} | "
              f"{w['frac_below_50']} | {_fmt(w['eligible_for_calvados2_single_chain'])} |")
        A("")
        A(f"All primary windows eligible: **{_fmt(elig.get('all_primary_windows_eligible'))}**.")
        A("")

    means = res.get("construct_means") or {}
    if means:
        A("## 3 · Measured ν per construct")
        A("")
        A("| construct | role | window | N | n | ν mean | ν SD | ν min | ν max |")
        A("|---|---|---|---:|---:|---:|---:|---:|---:|")
        for cid in [c["id"] for c in man["constructs"] if c["id"] in means]:
            m = means[cid]
            c = roles[cid]
            A(f"| `{cid}` | {c['role']} | {c['window']} | {c['length']} | {m['n']} | "
              f"{_fmt(m['nu_mean'])} | {_fmt(m['nu_sd'])} | {_fmt(m['nu_min'])} | "
              f"{_fmt(m['nu_max'])} |")
        A("")

    pairs = res.get("pairs") or {}
    if pairs:
        A("## 4 · Prespecified comparisons")
        A("")
        A("`D1` is the frozen rule: |Δν̄| ≥ 3 pooled replicate SDs **and** disjoint replicate ranges. "
          "`p` is an exact two-sided permutation test; Holm is applied across the primary family only.")
        A("")
        A("| pair | family | Δν̄ | separated (D1) | p | arrangements | powered | Holm |")
        A("|---|---|---:|---|---:|---:|---|---|")
        for key in sorted(pairs, key=lambda k: (pairs[k]["family"] != "primary", k)):
            r = pairs[key]
            perm = r["permutation"]
            A(f"| `{key}` | {r['family']} | {_fmt(r['delta_nu_mean'])} | "
              f"{_fmt(r['separated_D1'])} | {_fmt(perm['p'])} | {perm['n_arrangements']} | "
              f"{_fmt(perm['powered'])} | "
              f"{_fmt(r.get('holm_reject_at_0.05')) if 'holm_reject_at_0.05' in r else '—'} |")
        A("")

    comp = res.get("composition_only_test") or {}
    if comp:
        A("## 5 · The composition-only null")
        A("")
        A("Each parent against the mean of its three composition-preserving scrambles. A shuffle "
          "changes sequence *order* and preserves composition exactly, so a parent that does not "
          "move from its scrambles is a parent whose ν carries no information beyond composition.")
        A("")
        A("| parent | Δν̄ vs scramble mean | exceeds the 3-SD threshold |")
        A("|---|---:|---|")
        for k, v in comp.items():
            A(f"| `{k}` | {_fmt(v['delta_nu_vs_scramble_mean'])} | "
              f"{_fmt(v['exceeds_threshold'])} |")
        A("")

    comp_tbl = _load(COMPOSITION)
    if comp_tbl:
        A("### 5.1 · The composition baseline these ν have to beat")
        A("")
        A("The manuscript's own sequence-derived descriptors "
          "(`fusion_idr_features.features`, imported rather than copied), computed on **exactly the "
          "windows simulated here** — the manuscript's own table uses different ones, and "
          "characterises TAF15 1–205 while the only reported TAF15::NR4A3 coding junction retains "
          "1–161.")
        A("")
        A("| construct | N | SYGQ | aromatic (FYW) | FCR | NCPR | entropy (bits) | SCD |")
        A("|---|---:|---:|---:|---:|---:|---:|---:|")
        for cid, v in comp_tbl["rows"].items():
            A(f"| `{cid}` | {v['length']} | {v['frac_SYGQ']} | {v['frac_aromatic_FYW']} | "
              f"{v['frac_charged_FCR']} | {v['net_charge_per_residue_NCPR']} | "
              f"{v['shannon_entropy_bits']} | {v['SCD']} |")
        A("")
        A("⚠ **Read the scramble rows, because they bound what N1 can prove.** A "
          "composition-preserving shuffle leaves **every composition descriptor byte-identical** to "
          "its parent and moves only **SCD**, which is order-dependent. Both facts are asserted by "
          "the guard suite rather than eyeballed here. So a scramble-sensitive ν shows the "
          "simulation exceeds *composition* — it does **not** by itself show it exceeds the "
          "manuscript's full descriptor set, because SCD is in that set and the scramble does not "
          "hold it fixed. That is a limit of the prespecified null, stated rather than glossed.")
        A("")

    conv = res.get("convergence")
    if conv:
        A("## 6 · Convergence")
        A("")
        A(f"ν on the second half of each trajectory against ν on the whole post-equilibration "
          f"trajectory. Largest drift **{_fmt(conv['max_half_vs_full_delta'])}**; "
          f"**{conv['n_exceeding_pooled_sd']} of {conv['n_runs_with_a_delta']}** runs drift by more "
          f"than the pooled replicate SD "
          f"({conv['fraction_exceeding_pooled_sd']:.0%}). Converged by the frozen rule: "
          f"**{_fmt(conv['converged'])}**.")
        if not conv["converged"]:
            A("")
            A("⚠ **Every ν above is therefore labelled PROVISIONAL** — reported, never withheld, "
              "per Amendment 1.")
        A("")

    flags = res.get("outside_expected_range") or {}
    if flags:
        A("### 6.1 · Values outside the expected range")
        A("")
        A("Reported rather than withheld, per Amendment 1: the polymer globule limit is ν = 1/3 and "
          "a finite compact chain can fit below it, so *compact* and *broken* are different tests.")
        A("")
        A("| construct | ν mean | expected range | largest half-vs-full drift |")
        A("|---|---:|---|---:|")
        for k, v in flags.items():
            A(f"| `{k}` | {_fmt(v['nu_mean'])} | {v['expected_range']} | "
              f"{_fmt(v['nu_half_vs_full_delta_max'])} |")
        A("")

    A("## 7 · Claim ceiling")
    A("")
    A(res.get("claim_ceiling",
              "ν is a single-chain conformational observable. No efficacy, no selectivity in a "
              "patient, no safety, no therapeutic window, no clinical readiness."))
    A("")
    A("## 8 · What was not run")
    A("")
    A("- **The slab phase-coexistence arm** — multi-chain direct coexistence, the arm that would "
      "make *phase behaviour* a measurement rather than the model's premise. It needs a GPU, it is "
      "a real-dollar spend, and nothing here authorises it.")
    A("- **The multi-domain (CALVADOS 3) reading** of the full type-1 retained segment "
      "(EWSR1 1–431, which runs into the folded RRM at 361–442) and of the full-length chimeras.")
    A("- **Mpipi**, the other member of the model family.")
    A("")
    return "\n".join(L) + "\n"


def main():
    text = render()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print(f"{OUT} does not exist")
            return 1
        current = open(OUT).read()
        if current != text:
            print(f"{OUT} is STALE — rerun 'python3 {os.path.basename(__file__)}' and commit")
            return 1
        print("findings note is current")
        return 0
    with open(OUT, "w") as fh:
        fh.write(text)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
