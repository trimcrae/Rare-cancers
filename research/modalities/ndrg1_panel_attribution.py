#!/usr/bin/env python3
"""IS NDRG1's ELEVATION IN EMC HYPOXIA-SHAPED OR PPARγ-SHAPED? (AUT-PROP-048, RT-SGK1)

★ WHAT THIS IS THE POSITIVE HALF OF. AUT-062 established what NDRG1's elevation is NOT: the
reading is transcript ABUNDANCE, and every published mechanism connecting SGK1 to NDRG1 is a
PHOSPHORYLATION of NDRG1 protein, so the number cannot be attributed to SGK1 activity. AUT-PD-099
then retracted the activity-shaped clause from RT-SGK1's grade. That left an open question rather
than a closed route: if not SGK-shaped, what shape IS it? This asks whether NDRG1's per-sample level
moves with hypoxia programmes or with PPARγ/adipogenic ones, in the two expression series this
repository already holds.

⛔⛔ TWO CONTROLS, AND WITHOUT EITHER OF THEM THE ANSWER IS MANUFACTURED.

  1. **LEAVE-ONE-OUT.** NDRG1 is itself a member of several published hypoxia sets — it is in the
     Buffa metagene, among others. Scoring a panel that contains NDRG1 and then correlating NDRG1
     against it is correlating a variable with itself, and it would return a large positive number
     for a set of any composition. Every panel score here EXCLUDES NDRG1, and `n_panel_members`
     reports the count after that exclusion.

  2. **A SIZE-MATCHED RANDOM NULL.** On a single-channel array every gene carries a shared
     array-level component, so "correlates with the mean of k other genes" is the NULL, not the
     finding. Each panel is compared against `N_DRAWS` random panels of the SAME SIZE drawn from the
     same readable pool. ⚠ This control is what changes the answer: in the smaller series a RANDOM
     panel already reaches rho ≈ +0.25 to +0.43, so a raw rho of +0.6 there means nothing at all.
     Reporting the raw correlations without it would have produced a two-series replication that the
     data does not support.

⚠ WHAT LIMITS THIS, STATED HERE RATHER THAN LEFT TO BE FOUND. `emc-expression-panels.json` carries
per-sample values for 479 genes, not for every member of every panel, so each panel score rests on
the SUBSET of its members that has one — 9 to 41 genes against published sets of 44 to 231. Every row
prints `n_panel_members / n_panel_readable` so the subset is visible on the face of the result. This
is a real narrowing and it is why the panels are treated as PROGRAMME PROXIES rather than as the
published signatures. Recomputing full per-sample scores needs the GEO series matrices, which is a
$0 CI dispatch and is NOT done here.

⛔ NOTHING HERE IS AN EFFICACY, SELECTIVITY, SAFETY, THERAPEUTIC-WINDOW OR CLINICAL-READINESS claim.
A correlation between a transcript and a programme proxy in archival tumour tissue is an association
in a small observational series. It is not a mechanism, not a dependency, and not a target rationale.

USAGE
    python3 research/modalities/ndrg1_panel_attribution.py            # regenerate the artifact
    python3 research/modalities/ndrg1_panel_attribution.py --check    # re-derive and compare
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "emc-expression-panels.json")
OUT = os.path.join(HERE, "ndrg1-panel-attribution.json")

#: The gene under test, and the one excluded from every panel it belongs to.
SUBJECT = "NDRG1"

#: ⛔ SEEDED, AND THE SEED IS PART OF THE ARTIFACT. `--check` re-derives and compares, so an
#: unseeded null would make every check fail for a reason that is not a defect.
SEED = 20260829
N_DRAWS = 2000

#: A panel needs enough per-sample members to be a programme proxy at all. Below this the score is
#: one or two genes wearing a signature's name. ⚠ A tuning constant, not a principled threshold —
#: it is pinned here in one place and the artifact records which panels it excluded and why.
MIN_MEMBERS = 5

#: A correlation needs samples. Both series clear this comfortably; it exists so a future series
#: with three arrays cannot produce a rho at all rather than producing a meaningless one.
MIN_SAMPLES = 6

#: ⚠ THE PANEL FAMILIES ARE SELECTED BY PREFIX FROM THE ARTIFACT, NOT LISTED HERE. Typing the names
#: would put a second copy of the signature roster in this file, and it would rot the first time a
#: panel is added upstream (CLAUDE.md §1). The prefixes are the contract.
HYPOXIA_PREFIX = "hypoxia_"
PPARG_PREFIX = "pparg_"
#: Scored with the PPARγ family because it is the same hypothesis — an adipogenic/lineage programme —
#: reached through a process term rather than a TF target set.
PPARG_EXTRA = ("adipogenesis_process_proxy",)


def _load():
    with open(PANELS, encoding="utf-8") as fh:
        return json.load(fh)


def family_of(panel: str) -> str | None:
    if panel.startswith(HYPOXIA_PREFIX):
        return "hypoxia"
    if panel.startswith(PPARG_PREFIX) or panel in PPARG_EXTRA:
        return "pparg"
    return None


def sample_z(gene_reads: dict, sym: str, matrix: str) -> dict | None:
    """`{gsm: z_vs_array}` for one gene on one matrix, or None if it is not readable there.

    ⚠ A per-sample row can carry a NULL z — the probe had no value on that array. An absent reading
    is not a zero reading (CLAUDE.md §4), so the sample is DROPPED for that gene rather than imputed.
    """
    v = (gene_reads.get(sym) or {}).get(matrix)
    if not v or not v.get("readable"):
        return None
    out = {r["gsm"]: r["z_vs_array"] for r in v.get("per_sample", [])
           if r.get("z_vs_array") is not None}
    return out or None


def spearman(x, y):
    """Rank correlation with mid-ranks for ties. Written out rather than imported: this module runs
    in CI with no scientific stack, and `dev-setup.sh` records what pulling one in has cost."""
    def rank(a):
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def panel_rho(members, subject_z, gsms, cache):
    """rho(subject, mean-z of `members`) across `gsms`, or None if too few samples score."""
    zs = {g: cache[g] for g in members if cache.get(g)}
    if not zs:
        return None, 0
    pairs = []
    for s in gsms:
        vals = [zs[g][s] for g in zs if s in zs[g]]
        if vals:
            pairs.append((subject_z[s], statistics.mean(vals)))
    if len(pairs) < MIN_SAMPLES:
        return None, len(pairs)
    return spearman([a for a, _ in pairs], [b for _, b in pairs]), len(pairs)


def build(n_draws: int = N_DRAWS) -> dict:
    src = _load()
    gene_reads, sig = src["gene_reads"], src["signature_scores"]
    matrices = sorted({m for v in gene_reads.values() for m in v})

    series = {}
    for matrix in matrices:
        cache = {g: sample_z(gene_reads, g, matrix) for g in gene_reads}
        subject_z = cache.get(SUBJECT)
        if not subject_z:
            series[matrix] = {"subject_readable": False,
                              "_means": f"{SUBJECT} has no probe on this platform. That is an "
                                        "instrument statement, never a biological negative."}
            continue
        gsms = sorted(subject_z)
        pool = sorted(g for g in gene_reads if g != SUBJECT and cache.get(g))
        rng = random.Random(SEED)
        nulls: dict[int, list] = {}
        rows = {}

        for panel in sorted(sig):
            fam = family_of(panel)
            if fam is None:
                continue
            s = sig[panel]
            if not s.get("resolved"):
                rows[panel] = {"family": fam, "scored": False,
                               "why": "the signature set was never RETRIEVED. That is a failure to "
                                      "fetch, which says nothing about the set's existence."}
                continue
            pp = (s.get("per_platform") or {}).get(matrix)
            if not pp:
                rows[panel] = {"family": fam, "scored": False,
                               "why": "the set was not scored on this platform"}
                continue
            readable = [g for g in (pp.get("genes_readable") or []) if g != SUBJECT]
            members = [g for g in readable if cache.get(g)]
            if len(members) < MIN_MEMBERS:
                rows[panel] = {"family": fam, "scored": False,
                               "n_panel_members": len(members),
                               "n_panel_readable": len(readable),
                               "why": f"fewer than {MIN_MEMBERS} members carry a per-sample value in "
                                      "the committed artifact, so a score would be a couple of genes "
                                      "wearing a signature's name"}
                continue

            rho, n_scored = panel_rho(members, subject_z, gsms, cache)
            if rho is None:
                rows[panel] = {"family": fam, "scored": False,
                               "why": f"only {n_scored} sample(s) scored, below MIN_SAMPLES"}
                continue

            k = len(members)
            if k not in nulls:
                draws = []
                for _ in range(n_draws):
                    r, _n = panel_rho(rng.sample(pool, k), subject_z, gsms, cache)
                    if r is not None:
                        draws.append(r)
                nulls[k] = sorted(draws)
            null = nulls[k]
            p_emp = (sum(1 for r in null if r >= rho) + 1) / (len(null) + 1)
            rows[panel] = {
                "family": fam,
                "scored": True,
                "n_panel_members": k,
                "n_panel_readable": len(readable),
                "n_samples_scored": n_scored,
                "rho": round(rho, 4),
                "null_median": round(statistics.median(null), 4),
                "null_p95": round(null[int(0.95 * len(null))], 4),
                "null_draws": len(null),
                "p_empirical": round(p_emp, 4),
                "above_null_p95": rho > null[int(0.95 * len(null))],
            }

        scored = {p: r for p, r in rows.items() if r.get("scored")}
        hyp = [r for p, r in scored.items() if r["family"] == "hypoxia"]
        ppg = [r for p, r in scored.items() if r["family"] == "pparg"]
        n_hyp_clear = sum(1 for r in hyp if r["above_null_p95"])
        n_ppg_clear = sum(1 for r in ppg if r["above_null_p95"])
        separates = bool(hyp) and n_hyp_clear == len(hyp) and n_ppg_clear == 0

        series[matrix] = {
            "subject_readable": True,
            "n_samples": len(gsms),
            "readable_pool": len(pool),
            "classes": {c: sum(1 for r in (gene_reads[SUBJECT][matrix]["per_sample"])
                               if r.get("class") == c)
                        for c in sorted({r.get("class")
                                         for r in gene_reads[SUBJECT][matrix]["per_sample"]})},
            "panels": rows,
            "n_hypoxia_scored": len(hyp), "n_hypoxia_above_null_p95": n_hyp_clear,
            "n_pparg_scored": len(ppg), "n_pparg_above_null_p95": n_ppg_clear,
            "null_median_range": [round(min(r["null_median"] for r in scored.values()), 4),
                                  round(max(r["null_median"] for r in scored.values()), 4)]
                                 if scored else None,
            "separates_hypoxia_from_pparg": separates,
            "_separates_means": "TRUE only when EVERY scored hypoxia panel exceeds its own "
                                "size-matched null p95 and NO PPARγ panel does. It is a joint "
                                "statement about both families, so one PPARγ panel clearing makes it "
                                "false however strong the hypoxia side is.",
        }

    usable = {m: s for m, s in series.items() if s.get("subject_readable")}
    separating = sorted(m for m, s in usable.items() if s["separates_hypoxia_from_pparg"])
    return {
        "_what": f"Does {SUBJECT}'s per-sample level in EMC-containing expression series track "
                 "HYPOXIA programme proxies or PPARγ/adipogenic ones? Every panel excludes "
                 f"{SUBJECT} itself and is graded against a size-matched random null.",
        "_route": "RT-SGK1", "_ledger_item": "AUT-PROP-048",
        "_language_discipline": "⛔ NOT an efficacy, selectivity, safety, therapeutic-window or "
                                "clinical-readiness claim. An association between a transcript and a "
                                "programme proxy in archival tissue is not a mechanism and not a "
                                "dependency.",
        "_the_two_controls": {
            "leave_one_out": f"{SUBJECT} is a member of several published hypoxia sets, so it is "
                             "removed from every panel before scoring. Without this the comparison "
                             "is a variable against itself.",
            "size_matched_null": f"{N_DRAWS} random panels of the same size from the same readable "
                                 "pool. Without this the array-level shared component reads as "
                                 "signal — and in the smaller series it fully accounts for a raw "
                                 "rho of +0.6.",
        },
        "_what_this_does_not_settle": (
            "Direction and mechanism. A transcript tracking a hypoxia proxy is consistent with "
            "HIF-driven abundance and equally consistent with both being downstream of something "
            "else in these tumours; nothing here separates them. It also does not settle the "
            "published signatures themselves — each panel is the SUBSET of its members carrying a "
            "per-sample value in the committed artifact, 9 to 41 genes against sets of 44 to 231."),
        "_inputs": {"panels": "research/modalities/emc-expression-panels.json",
                    "seed": SEED, "n_draws": N_DRAWS,
                    "min_panel_members": MIN_MEMBERS, "min_samples": MIN_SAMPLES},
        "series": series,
        "verdict": {
            "separating_series": separating,
            "n_series_usable": len(usable),
            "headline": (
                f"{len(separating)} of {len(usable)} series separate the two programmes."
                if usable else "no series carries a readable subject probe"),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare against the committed artifact")
    args = ap.parse_args(argv)
    doc = build()
    if args.check:
        if not os.path.exists(OUT):
            print(f"⛔ {os.path.basename(OUT)} does not exist — run this module without --check")
            return 1
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)
        if committed != doc:
            print(f"⛔ {os.path.basename(OUT)} does not re-derive from its generator. "
                  "Regenerate it and commit the result.")
            return 1
        print(f"OK {os.path.basename(OUT)} re-derives from this module")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    for matrix, s in doc["series"].items():
        if not s.get("subject_readable"):
            print(f"  {matrix:44s} subject not readable"); continue
        print(f"  {matrix:44s} n={s['n_samples']:3d}  "
              f"hypoxia {s['n_hypoxia_above_null_p95']}/{s['n_hypoxia_scored']} over null  "
              f"pparg {s['n_pparg_above_null_p95']}/{s['n_pparg_scored']} over null  "
              f"null median {s['null_median_range']}  separates={s['separates_hypoxia_from_pparg']}")
    print(f"  VERDICT {doc['verdict']['headline']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
