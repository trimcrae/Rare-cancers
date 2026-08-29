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

#: ⛔⛔ WHICH MEMBERSHIP THE PANELS ARE SCORED OVER IS A PINNED CHOICE, NEVER A CONSEQUENCE OF
#: WHICH FILES A WORKFLOW HAPPENED TO PUSH (AUT-PD-167). Until 2026-08-29 this module widened its
#: entire scientific reading the moment `emc-expression-panels.json` grew a `signature_member_reads`
#: block — so a scheduled CI fetch (aa6d9d9a9) reversed a committed verdict with no commit, no gate
#: and no argument. The read is now a constant here and moving it is an edit somebody makes on
#: purpose and defends in a commit message.
#:
#: ⛔ NEITHER AVAILABLE READ IS SOUND, AND THEY FAIL IN OPPOSITE DIRECTIONS. Both were measured on
#: `origin/main` b24cb6e22; every figure lives on ledger row AUT-PD-167 and is not retyped here.
#:
#:   * `curated_only` (this pin) scores each published set over `curated ∩ published`. That subset is
#:     NOT a thin-but-fair sample of the panel: the 479-gene roster was curated for six targeted EMC
#:     reads that have nothing to do with this question, and in the LARGER series it picks, out of
#:     every hypoxia panel, members that track the subject far better than the panel itself does —
#:     while picking mid-pack members out of the PPARγ panels. ⛔ The size-matched null CANNOT absorb
#:     this: it draws random genes from a POOL, never random members from the PANEL, so a non-random
#:     choice of members passes straight through it. `within_panel_percentile` on every scored row
#:     measures it, and that field is the one home for the size of the effect.
#:   * `curated_plus_signature_members` (the wide read) scores each set over its full readable
#:     membership, which is the right membership — but the null's pool then becomes the union of the
#:     signature sets themselves, so a majority of it IS panel members and most of those are PPARγ
#:     members. A draw from that pool is a diluted mixture of the two hypotheses rather than a
#:     background, and the pool centroid's correlation with the subject moves from negative to
#:     positive. ⛔ That shift is a POOL effect and not a panel-size one: swept over k = 10…231 the
#:     null median is flat within each pool and differs between them at every k.
#:
#: ★ SO THE PIN IS NOT A VERDICT ON WHICH READ IS RIGHT — IT HOLDS THE PUBLISHED ONE STILL WHILE THE
#: MEASUREMENT THAT SETTLES IT IS TAKEN. That measurement is full membership scored against a null
#: drawn from a RANDOM SAMPLE OF THE ARRAY BACKGROUND, which neither read has and which is a $0 CI
#: read of the same two series matrices. It is ledger row AUT-PD-170.
MEMBERSHIP_SOURCE = "curated_only"

#: The reads this module knows how to take. `curated_plus_signature_members` is implemented and
#: reachable by changing the constant above; it is not dead code and it is not adopted.
MEMBERSHIP_SOURCES = ("curated_only", "curated_plus_signature_members")

#: Draws for the within-panel selection diagnostic. A quarter of `N_DRAWS`: it answers a percentile
#: rather than a p-value, and it runs once per scored panel on top of the null itself.
SELECTION_DRAWS = N_DRAWS // 4

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


def member_z(src: dict, matrix: str) -> dict:
    """`{gene: {gsm: z}}` from the panels artifact's compact `signature_member_reads`, or `{}`.

    ⛔ RETURNS `{}` WHENEVER `MEMBERSHIP_SOURCE` IS PINNED NARROW, EVEN THOUGH THE BLOCK IS PRESENT
    AND READABLE — and `panel_membership_source` in the artifact says so in those words, because a
    read declined on purpose and a read that could not be taken are different facts (CLAUDE.md §4).

    ⛔⛔ AN ABSENT BLOCK IS AN ABSENT READING, NOT A NARROW ONE BY CHOICE (AUT-PROP-051). Until a
    `panels` dispatch regenerates the artifact this returns `{}` and every score below is the OLD,
    NARROW read — a published set scored over `curated ∩ published`. That state is legible in the
    artifact's `panel_membership_source`, never silent: the two reads produce different numbers
    under the same field names, and a reader who cannot tell which one they hold has the worse of
    both.
    """
    return {} if MEMBERSHIP_SOURCE == "curated_only" else signature_member_z(src, matrix)


def signature_member_z(src: dict, matrix: str) -> dict:
    """The block itself, read WHATEVER the pin says. Used by the selection diagnostic, which has to
    enumerate each panel's full readable membership in order to report how the scored subset sits
    against it — a diagnostic that could only run under the read it is diagnosing would be useless."""
    blk = ((src.get("signature_member_reads") or {}).get(matrix) or {})
    gsms, z = blk.get("gsms") or [], blk.get("z") or {}
    if not gsms or not z:
        return {}
    return {g: {gsms[i]: v for i, v in enumerate(row) if v is not None and i < len(gsms)}
            for g, row in z.items()}


def within_panel_percentile(members, readable_full, subject_z, gsms, diag_cache, rng):
    """⛔⛔ THE CONTROL THE SIZE-MATCHED NULL CANNOT PROVIDE, AND THE ONE THAT DECIDES HOW MUCH THIS
    ARTIFACT'S VERDICT IS WORTH (AUT-PD-167).

    The null asks "would ANY k genes do this?" — it draws from a POOL. It therefore says nothing
    about whether THESE k members are a fair sample of the panel they are named after. This asks the
    other question: where does the scored subset's rho fall in the distribution of rho over k members
    drawn at random from the SAME panel's full readable membership?

    ⚠ A percentile near 50 means the subset is thin but fair. A percentile near 100 means the subset
    was selected — and a roster curated for other purposes can select without anybody intending it.
    Returns None when the full membership is no larger than the scored subset, because there is then
    no distribution to sit in.
    """
    full = [g for g in readable_full if diag_cache.get(g)]
    k = len(members)
    if len(full) <= k:
        return None
    rho, _n = panel_rho(members, subject_z, gsms, diag_cache)
    if rho is None:
        return None
    draws = []
    for _ in range(SELECTION_DRAWS):
        r, _x = panel_rho(rng.sample(full, k), subject_z, gsms, diag_cache)
        if r is not None:
            draws.append(r)
    if not draws:
        return None
    return {
        "n_panel_full": len(full),
        "rho_over_full_panel": round(panel_rho(full, subject_z, gsms, diag_cache)[0], 4),
        "percentile": round(100.0 * sum(1 for r in draws if r < rho) / len(draws), 1),
        "draws": len(draws),
        "_means": "where this row's scored subset falls among random subsets of the SAME size drawn "
                  "from this panel's own full readable membership. 50 = a fair thin sample; 100 = the "
                  "subset is the top of its own panel and the score is a selection effect.",
    }


def build(n_draws: int = N_DRAWS) -> dict:
    src = _load()
    gene_reads, sig = src["gene_reads"], src["signature_scores"]
    matrices = sorted({m for v in gene_reads.values() for m in v})

    wide_present = bool(src.get("signature_member_reads"))
    if MEMBERSHIP_SOURCE not in MEMBERSHIP_SOURCES:
        raise SystemExit(f"MEMBERSHIP_SOURCE={MEMBERSHIP_SOURCE!r} is not one of {MEMBERSHIP_SOURCES}")
    membership_source = {
        "pinned": MEMBERSHIP_SOURCE,
        "wide_block_present": wide_present,
        "source": ("gene_reads only" if MEMBERSHIP_SOURCE == "curated_only"
                   else "gene_reads + signature_member_reads"),
        "means": (
            "⛔ THE NARROW READ, PINNED ON PURPOSE AND NOT FOR WANT OF DATA (AUT-PD-167). Each "
            "published set is scored over `curated ∩ published`; how thin that is per panel is "
            "`n_panel_members / n_panel_readable` on each row. The wide block IS present in the "
            "panels artifact and is DECLINED here, "
            "which is a different fact from its being absent."
            if MEMBERSHIP_SOURCE == "curated_only" else
            "⭐ THE WIDE READ. Each published set is scored over every member the platform can "
            "read, and the size-matched null is drawn from that same widened pool."),
        "why_pinned": (
            "Neither available read is sound and they fail in OPPOSITE directions, so switching "
            "would substitute one confound for another while reversing a published verdict. The "
            "narrow read's members are a SELECTED subset of each panel (see `within_panel_percentile` "
            "on every row); the wide read's null pool is a majority of panel members, most of them "
            "PPARγ members, which makes it a diluted mixture of the two hypotheses rather than a "
            "background — the figures are on ledger row AUT-PD-167. The "
            "measurement that settles it — full membership against a null drawn from a random sample "
            "of the array background — is ledger row AUT-PD-170 and is a $0 CI read."),
        "not_comparable": "⚠ Numbers under the two sources are NOT comparable: the null's pool differs, "
                          "and the shift is a POOL effect rather than a panel-size one — swept over "
                          "k = 10…231 the null median is flat within each pool and differs between "
                          "them at every k (AUT-PD-167).",
    }

    series = {}
    for matrix in matrices:
        # ⭐ TWO SOURCES, `gene_reads` WINNING. Both carry the same within-array z for a gene that
        # is in both; gene_reads is preferred so a widened run cannot silently change a number that
        # was already published from the curated block.
        wide = member_z(src, matrix)
        cache = {g: sample_z(gene_reads, g, matrix) for g in gene_reads}
        for g, zs in wide.items():
            if not cache.get(g):
                cache[g] = zs
        # ⭐ THE DIAGNOSTIC'S CACHE IS ALWAYS WIDE, WHATEVER THE PIN. It never feeds a score, a null
        # or the verdict — only `within_panel_percentile`, which has to see the membership the pin
        # is declining in order to say what declining it costs.
        diag_cache = dict(cache)
        for g, zs in signature_member_z(src, matrix).items():
            if not diag_cache.get(g):
                diag_cache[g] = zs
        subject_z = cache.get(SUBJECT)
        if not subject_z:
            series[matrix] = {"subject_readable": False,
                              "_means": f"{SUBJECT} has no probe on this platform. That is an "
                                        "instrument statement, never a biological negative."}
            continue
        gsms = sorted(subject_z)
        # ⚠ THE NULL'S POOL GROWS WITH THE CACHE, AND THAT IS THE POINT RATHER THAN A SIDE EFFECT.
        # The size-matched null draws from whatever genes carry a per-sample value, so widening the
        # membership widens the null too — a random panel of k genes is drawn from a different,
        # larger pool. The verdict rests on the null, so it MUST be re-derived here and never
        # carried over from the narrow run.
        pool = sorted(g for g in cache if g != SUBJECT and cache.get(g))
        rng = random.Random(SEED)
        # ⛔ ITS OWN GENERATOR. Sharing `rng` would make every null downstream of the diagnostic
        # depend on how many panels happened to be diagnosed before it — the artifact would stop
        # re-deriving the moment a panel was added, for a reason that is not a defect.
        diag_rng = random.Random(SEED)
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
                "within_panel_percentile": within_panel_percentile(
                    members, readable, subject_z, gsms, diag_cache, diag_rng),
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
            "⛔⛔ FIRST AND LOUDEST: WHETHER THE SEPARATION BELOW IS THE BIOLOGY OR THE ROSTER "
            "(AUT-PD-167, measured 2026-08-29). Every panel here is scored over the members that "
            "happen to sit in a 479-gene roster curated for six unrelated targeted EMC reads, and "
            "`within_panel_percentile` on each row reports that this subset is NOT a fair thin "
            "sample of its panel in the larger series: there the curated subset of EVERY hypoxia "
            "panel lands in the upper tail of its own panel's distribution — read the six "
            "`within_panel_percentile` values below rather than a number retyped here — while the "
            "PPARγ subsets straddle the middle. ⛔ The "
            "size-matched null cannot absorb that, because it draws random genes from a POOL and "
            "never random members from the PANEL. Read `separating_series` as CONDITIONAL ON THIS "
            "ROSTER and not as a statement about the published signatures. "
            "⚠ The obvious repair — score the full membership, which this repository now holds — is "
            "NOT sound either: its null pool becomes the union of the signature sets, a majority of "
            "which IS panel members and most of those PPARγ members, so it is a diluted mixture of "
            "the two hypotheses rather than a background (AUT-PD-167). Both reads are confounded "
            "and they fail in opposite "
            "directions; the read that settles it is AUT-PD-170. "
            "Direction and mechanism are not settled either. A transcript tracking a hypoxia proxy "
            "is consistent with HIF-driven abundance and equally consistent with both being "
            "downstream of something else in these tumours; nothing here separates them. ⚠ HOW MUCH "
            "OF EACH SET WAS ACTUALLY SCORED IS `panel_membership_source` below and "
            "`n_panel_members / n_panel_readable` on every row."),
        "_inputs": {"panels": "research/modalities/emc-expression-panels.json",
                    "seed": SEED, "n_draws": N_DRAWS,
                    "min_panel_members": MIN_MEMBERS, "min_samples": MIN_SAMPLES},
        "panel_membership_source": membership_source,
        "series": series,
        "verdict": {
            "separating_series": separating,
            "n_series_usable": len(usable),
            "headline": (
                f"{len(separating)} of {len(usable)} series separate the two programmes, CONDITIONAL "
                "ON THE CURATED ROSTER — see `_what_this_does_not_settle` before quoting this."
                if usable else "no series carries a readable subject probe"),
            "_weight": "⛔ NOT a confirmed one-series finding. The subset each panel is scored over "
                       "is selected rather than thin-but-fair (`within_panel_percentile`), and the "
                       "wide alternative is confounded the other way. This artifact is the best "
                       "available read and it is not yet a result.",
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
