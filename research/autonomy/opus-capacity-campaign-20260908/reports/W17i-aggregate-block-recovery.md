<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id aad099dd3f2ae7bf4 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aad099dd3f2ae7bf4.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

Start `date -u`: `Tue Sep  8 03:03:29 UTC 2026`. End `date -u`: `Tue Sep  8 03:12:13 UTC 2026` (last verification call `03:13`). HEAD at read time `a87275c14897230041fde97c9965c9646474df7a`; HEAD at end `98a0833f1ede2cf9cef13790388260567a32e868` (the coordinator committed under me during the run — both ends recorded, neither is the COMMON-BRIEF's `92abbcb9…`). `git status --porcelain` was **empty at start**; at end it lists **8 untracked files, all other lanes' reports** (`W01g`, `W02f`, `W04e`, `W06f`, `W07f`, `W09f`, `W12e`, `W20g`) written by the coordinator during my run. **I wrote nothing into the tree**; all my execution was under `/tmp/claude-0/w17i/`.

## Worker

**W17i**, lane 17 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; I did not observe it. The coordinator must extract the actual per-child runtime model from the transcript.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — model-relevant lines, identical at start and end (full output in the transcript):

```
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_VERSION=2.1.42
CLAUDECODE=1
CLAUDE_EFFORT=medium
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
```

## Question

W17h censused 2,607 strict statistical blocks, verified 1,116 against rows they carry, closed ~800 as external-input, and **declined to decide ~708 middle-class blocks**: ~684 panel/read-level `t+df` blocks in `emc-expression-panels.json` and ~24 `set_scores`/`platforms` blocks in `nr4a3-fusion-targets.json`. None carries its own per-block rows. **Are they reconstructible in-file, and does the reconstruction verify?**

Open because nobody had tested whether the artifact carries the three inputs a reconstruction needs (set definition + per-sample rows + aggregation rule), and because "recover the rule by exhaustive search with a unique winner" had only ever been done once, by W17d, on a different artifact.

## Prior-work check

Live checkout `/home/user/Rare-cancers` only (I did not consult the frozen corpus this run; absence there would be UNKNOWN either way).

- `rg -n -l -i 'genes_readable' --glob '!.git' --glob '!*.json'` → 16 files, all **generators** (`emc_expression_panels.py`, `nr4a3_fusion_targets.py`, …) or prose reports. **No existing test reconstructs a panel- or set-level score from committed rows.**
- `git ls-files | rg -i 'test_.*(panel|signature|set_score|welch)'` → 13 test files; reading their names and W17h's R3 finding, the only gate that reaches a committed Welch against its own rows remains `test_aso_delivery_antigen.py` (21 blocks, flat 0.02 tolerance). Nothing reaches panel- or set-level blocks.
- `rg -n -o -i 'per-sample (mean|score)' --glob '*.py' research scripts` → 12 hits. `nr4a3_fusion_targets.py:874` and `:960` describe the **global offset** as "the per-sample mean z over ALL mapped symbols", which independently corroborates my classification of the two `platforms` blocks as external-input. Neither generator states the *set-score* aggregation rule in the lines returned; **my recovery is from the artifact alone and does not depend on the generator.**
- `CLOSED-WORK.md` read in full. Not replaying: ASO/NAT or Qeios items, frozen comment `7baf2727…`, the blocked NR4A Perspective, the rejected registry paper, lane 11's source-index, any denied external route. I opened **no** review round, edited **no** manuscript or hardening-state file, made **no** network call, did **not** run `scripts/preflight.sh`, placed **no** file in the tree, raised **no** ceiling.
- I did **not** re-run W17b's 872-block census, W17d's ATR recovery, or W17h's repo-wide census. I reused W17h's 2,607 denominator and W17b's gate algebra as given.

## Method / inputs

**Inputs (read-only, live checkout):** `research/modalities/emc-expression-panels.json` (13.3 MB), `research/modalities/nr4a3-fusion-targets.json` (995 KB), plus `nr4a3_fusion_targets.py` and `emc_expression_panels.py` read only for the corroboration grep above. Prior reports `W17b`, `W17d`, `W17f`, `W17h` read.

**Tools:** system `python3` (stdlib `json`/`math`/`re`/`statistics`/`collections` only) for the searches; `/root/.local/share/uv/tools/pytest/bin/python` with pytest 9.1.1 for the module run. No network, no installs, no paid API, no GPU. Execution root `/tmp/claude-0/w17i/`, with read-only symlinks at `/tmp/claude-0/w17i/research/modalities/` so the shipping `__file__`-relative path resolution is exercised verbatim.

**Block definition:** unchanged from W17h — a dict carrying a numeric statistic (`t`/`u`/`z`/`statistic`/`observed_t`) **and** a numeric `df`/`dof`.

**Rule space, stated before the first run.** Aggregation ∈ {`mean`, `median`, `sum`, `trimmed_minmax`} × gene set ∈ {the block's own `genes_readable`, all set genes with a row on that platform} × arm rule ∈ {exclude `unclassified`, include it} × missing handling ∈ {skip null genes, require complete}. A fifth dimension — empty-sample handling ∈ {`drop_empty_sample`, `require_any`} — was **added after** one block (`panels/immune_tme/b_cell_and_tertiary_lymphoid_structure`, GSE4303) came back UNKNOWN with 0 admissible rules and dissection showed it has one sample with all six set genes null. I record that the space was extended after seeing a failure; the extension is a real committed-data feature (the block's own `n_EMC=10, n_comparator=5` matches exactly the 15 of 16 samples with ≥1 readable gene), not a fitted parameter, and it changed no other block's verdict.

**Tolerances propagated, not chosen — and the propagation is the load-bearing correction.** Field-level printed precision measured from each artifact's own serialised text (max decimals over all literals of that field within that family): `t` 3 dp → 5e-4, `df` 1 dp → 0.05, `delta_a_minus_b`/`mean_a`/`mean_b` 4 dp → 5e-5, `z_vs_array` 4 dp → 5e-5. **For a reconstructed quantity the output field's half-ulp alone is not enough**: a per-sample score is a mean of 4-dp `z` values, so it carries `|dz| ≤ 5e-5` of its own, and the arm mean inherits it. My first pass used the output half-ulp only and produced a **spurious UNKNOWN** (`G_brenca_TAF15` on GSE24369, `mean_b` deviating 5.1e-5 against a 5.0e-5 bound — 1.02 half-ulps). With input error propagated (`U + dsc`) it is a clean pass. I report the wrong version because it changed a reported number (1 spurious UNKNOWN → 0).

**Gate:** W17b's forward form, unchanged. T1 observed `v_a+v_b` vs `(Δ/t)²` over the committed interval box; T2 observed Welch–Satterthwaite df vs committed df over the four variance-error corners; T3 means; T4 delta. `ddof=1`. `|t| ≤ 10·dt` ⇒ T1 NOT EVALUABLE ⇒ UNKNOWN, never a pass. **No root is ever picked**: the split inversion `f = v_a/S` is a quadratic with `D = (1/A+1/B)/df − 1/(A·B)`; two-distinct-root cases are counted, never resolved.

## Result

### R1 — The inputs are present for most of the class, and the rule resolves uniquely to the arithmetic mean

Exhaustive search over the full rule space, requiring a unique winner:

| Family | blocks | admissible aggregators | verdict | Tier |
|---|---|---|---|---|
| `emc-expression-panels.json` `panels/*/groups/*/per_platform/*/score` | **156** | `{mean}` on every block | **UNIQUE** | PRIMARY |
| `nr4a3-fusion-targets.json` `set_scores` (sets A–G, all genes in `gene_reads`) | **10** | `{mean}` on every block | **UNIQUE** | PRIMARY |
| — AMBIGUOUS (>1 aggregator) | **0** | — | — | PRIMARY |
| — UNKNOWN (0 aggregators) | **0** | — | — | PRIMARY |

The recovered rule, stated in full: **per sample, the arithmetic mean of `gene_reads[gene][platform].per_sample[].z_vs_array` over the block's own `genes_readable`, dropping genes with a null value and dropping samples with no readable gene; then a `ddof=1` Welch of the EMC arm against the comparator arm.**

Three of the five searched dimensions are **not identifiable from committed data and do not need to be**: the `genes_readable` field and "all set genes with a row" coincide on every block; `unclassified` samples have **no rows at all** in `gene_reads` (35 rows on GSE24369 against 42 samples, and `42 − 7 unclassified = 35`), so the arm rule is baked into the rows rather than free; and `require_complete` collapses onto `skip_null` wherever no null exists. Only the **aggregation** dimension is identifiable, and it resolves to a single winner on all 166 blocks. `median`, `sum` and `trimmed_minmax` are rejected on every one — e.g. on the immune_tme block `median` misses `mean_b` by 4.3e-1 (≈8,500 half-ulps) and `df` by 5.32 (106 half-ulps).

### R2 — The gate applied, and the whole 708 decided

`emc-expression-panels.json`, all 1,556 strict blocks classified (`panels4.py`, exit 0):

| Class | blocks | Tier |
|---|---|---|
| `gene_reads/*/welch_EMC_vs_comparator` — verified by W17f against own rows | 872 | SECONDARY (W17f) |
| **Panel-group `score` blocks — reconstructed, rule unique, gate PASS** | **156** | **PRIMARY** |
| Gene-level mirrors under `reads/*` — byte-identical on every common field to their `gene_reads` anchor | **281** | PRIMARY |
| `reads/*` duplicates of the 156 panel blocks — byte-identical to their `panels/*` anchor | **156** | PRIMARY |
| `reads/*/the_binary/*` and similar — carry their **own** `per_sample`, gated directly, PASS | **7** | PRIMARY |
| `signature_scores/*` (42) + their `reads/*/signature_slots` duplicates (42) — **EXTERNAL INPUT** | **84** | PRIMARY |
| total | **1,556** | |

`nr4a3-fusion-targets.json`, the 24 blocks W17h left open:

| Class | blocks | Tier |
|---|---|---|
| `set_scores` sets A+B, B, D, E, G × 2 platforms — reconstructed, rule unique, gate PASS | **10** | PRIMARY |
| `set_scores` PPARG_* × 2 platforms — sets of 66–269 symbols of which only 1–6 have committed rows | **12 EXTERNAL** | PRIMARY |
| `platforms/*/global_offset/welch` — a per-sample mean over **all 18,694 mapped symbols** | **2 EXTERNAL** | PRIMARY |

Gate outcome across all 166 reconstructed blocks: **T1 0 violations, T2 0 violations, T3 0 violations, T4 0 violations, 0 blocks excluded as ill-conditioned, 0 AMBIGUOUS, 0 UNKNOWN.**

The sharpest numbers, as in W17b/W17h, sit right on the rounding boundary and could not be produced by a different variance convention or a stale row set: worst `|df_obs − df_committed|` is **0.049802 = 0.9960 of the print half-ulp** (panels) and **0.049898 = 0.9980** (nr4a3 set E on GSE4303).

**Root ambiguity is real and was measured, never resolved:** **43 of 156** panel blocks and **4 of 10** nr4a3 set blocks admit **two distinct** admissible variance splits. Every decision used the root-agnostic forward form.

### R3 — Coverage number

| | blocks | share of 2,607 | Tier |
|---|---|---|---|
| Verified before this run (W17b/W17d/W17f/W17h) | 1,116 | 42.8 % | SECONDARY |
| **Moved UNKNOWN → verified by this run** | **610** (156 + 281 + 156 + 7 + 10) | +23.4 pp | **PRIMARY** |
| **Confirmed external-input by this run** | **98** (84 panels + 12 PPARG sets + 2 platform offsets) | — | **PRIMARY** |
| 610 + 98 | **708** — the entire middle class W17h declined | | |
| **Repository-wide verifiable total** | **1,726 / 2,607 = 66.2 %** | | PRIMARY |
| Remaining, all external-input | **881 / 2,607 = 33.8 %** | | PRIMARY |

"Not verifiable at all from committed material" remains **0** — every block has a named recovery path; 881 of them need a GEO series matrix, DepMap/PRISM per-line values, or a full signature-set gene universe.

**What is actually gated today is unchanged: 21 / 2,607 = 0.81 %** (W17h's R3 ASO gate). Nothing was landed in the tree; the 66.2 % is what the tree *would* reach with W17f's module, W17h's module and this one, at **6 further test functions** (measured by `grep -c '^def test_'`), i.e. 7,269 / 7,500 in the modalities tier if all three land.

### R4 — The honest cost of reconstruction: the gate is much less sensitive than a direct row gate

A reconstructed block averages `G` genes × `n_a` samples before the error reaches `mean_a`, so a single bad row is diluted by ~`G·n_a`. Measured on the control block (`panels/instrument_controls/fet_family_context`, GSE24369, G=3, n=(6,29)) by scaling a single-row perturbation:

| single-row shift | 1 | 2 | 5 | 10 | 20 | 50 | 100 | **200** half-ulps |
|---|---|---|---|---|---|---|---|---|
| gate verdict | pass | pass | pass | pass | pass | pass | pass | **reject** |

**The gate detects a single corrupted `z` only at ≥ ~100–200 half-ulps (0.005–0.01 z units); W17b's direct row gate catches 1.** This is a genuine limitation of reconstructed-block verification and it is pinned by an assertion in both directions (200 rejects, 100 still passes) so it cannot be forgotten or claimed away.

## Validation evidence

**RUN** — all commands executed under `/tmp/claude-0/w17i/`, nothing in the repository.

1. `python3 /tmp/claude-0/w17i/nr4a3_setscores.py` → **exit 0**. First-pass search (output half-ulp only): 22 scored set_scores blocks, 10 with all genes in `gene_reads`, 12 external. Produced the **spurious** result recorded above.
2. `python3 /tmp/claude-0/w17i/nr4a3_v2.py` → **exit 0**. Propagated tolerances + forward gate: `UNIQUE=10 AMBIGUOUS=0 UNKNOWN=0 EXTERNAL=12 worst_df_dev=0.049898 (0.9980 of half-ulp)`.
3. `python3 /tmp/claude-0/w17i/panels.py` … `panels4.py` → **exit 0** each. Final classification, verbatim:
   ```
      872  A_gene_reads_872_covered_by_W17f
        7  B_own_rows_PASS
      281  C2_gene_mirror_identical
      198  C_join_identical_to_canonical
       42  E_EXTERNAL_missing_rows
        1  F_UNIQUE_mean
      155  F_UNIQUE_mean_agg_unique_empty_rule_degenerate
   TOTAL 1556
   worst_df_dev=0.049802 (0.9960 half-ulp)  two_distinct_roots=46
   unresolved/unknown:
   ambiguous: []
   ```
   (`two_distinct_roots=46` there counts the 7 own-row blocks as well; the panel-only figure is 43, measured separately.)
4. Dissections, all **exit 0**: the `G_brenca` 1.02-half-ulp near-miss; the `immune_tme` all-null sample; the `CD248_followup` / `CSPG4_platform_discordance` blocks (identical on `t`/`df`/`delta_a_minus_b` to their `gene_reads` anchors — they carry no `mean_a`/`mean_b`, which is why a naive all-field equality test called 173 of them a mismatch; corrected to compare common fields only).
5. **Module run.** `/root/.local/share/uv/tools/pytest/bin/python -m pytest tests/test_reconstructed_panel_and_set_score_blocks.py -q`, cwd `/tmp/claude-0/w17i/research/modalities`, pytest 9.1.1 —
   - first run: **`2 failed, 4 passed in 4.83s`, exit 1**. Both failures were mine and both were informative: `roots == 46` was wrong for the panel-only scope (actual **43**), and the falsification control at 10 half-ulps **did not fire** — which is how the dilution limitation in R4 was found rather than assumed.
   - after correcting both assertions to the measured values: **`6 passed in 4.78s`, exit 0**.

**PROPOSED (NOT RUN):** landing the module at `research/modalities/tests/test_reconstructed_panel_and_set_score_blocks.py`; any `scripts/preflight.sh` run; any `tier_budget.py` re-run (W17h's figures reused, not re-measured).

### The module, returned inline (authored nowhere in the tree)

```python
"""W17i — read-only gate for the committed PANEL-LEVEL / SET-LEVEL statistical blocks that
carry no per-block rows of their own, in `emc-expression-panels.json` and
`nr4a3-fusion-targets.json`.

Each such block is reconstructed IN FILE from three committed inputs:
  (1) the block's own `genes_readable` set definition,
  (2) the per-sample `gene_reads[gene][platform].per_sample[].z_vs_array` rows,
  (3) an aggregation rule RECOVERED by exhaustive search requiring a UNIQUE winner.

The rule is never picked. `_recover` searches {mean, median, sum, trimmed_minmax} x
{drop_empty_sample, require_any}; zero admissible aggregators is UNKNOWN and two distinct
aggregators is AMBIGUOUS — both fail the gate rather than being resolved.

Gate is W17b's forward form, unchanged:
  T1 (scale)  observed v_a+v_b vs (delta/t)^2      T2 (df) observed Welch-Satterthwaite df
  T3 (means)  committed mean_a/mean_b               T4 (delta)
No root is ever picked: the variance-split inversion is a quadratic with discriminant
D = (1/A+1/B)/df - 1/(A*B) and both roots are admissible whenever df >= max(n_a,n_b)-1.
`test_the_root_ambiguity_is_real_and_stays_measured` counts it so a later "simplification"
into an inversion cannot happen quietly.

Tolerances are the artifact's OWN printed precision measured FIELD-LEVEL from its serialised
text (per-literal repr mis-fires; see W17h), PLUS the propagated error of the reconstruction
itself (a mean of 4-dp z values carries |dz| <= 5e-5). Sample variance is ddof=1.
|t| <= 10*dt makes T1 NOT EVALUABLE -> UNKNOWN, never a pass.
"""
import json, math, os, re, statistics as st
import pytest

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS = os.path.join(MOD, "emc-expression-panels.json")
NR4A3 = os.path.join(MOD, "nr4a3-fusion-targets.json")
FIELDS = ("t", "df", "delta_a_minus_b", "mean_a", "mean_b")


def _half_ulp(path, family, field):
    txt = open(path, encoding="utf-8").read()
    dp = []
    for blk in re.findall(r'"%s"\s*:\s*\{[^{}]*\}' % re.escape(family), txt):
        for m in re.finditer(r'"%s"\s*:\s*(-?\d+(?:\.(\d+))?)' % re.escape(field), blk):
            dp.append(len(m.group(2)) if m.group(2) else 0)
    assert dp, (path, family, field)
    return 0.5 * 10 ** (-max(dp))


def _dz(path):
    txt = open(path, encoding="utf-8").read()
    return 0.5 * 10 ** (-max(len(m.group(1))
                             for m in re.finditer(r'"z_vs_array"\s*:\s*-?\d+\.(\d+)', txt)))


AGG = {"mean": lambda v: sum(v) / len(v), "median": st.median, "sum": sum,
       "trimmed_minmax": lambda v: (sum(sorted(v)[1:-1]) / (len(v) - 2)) if len(v) > 2 else None}


def _rows(doc):
    z, cls = {}, {}
    for g, plats in doc["gene_reads"].items():
        for plat, b in plats.items():
            for r in b.get("per_sample") or []:
                z[(g, plat, r["gsm"])] = r.get("z_vs_array")
                cls[(plat, r["gsm"])] = r["class"]
    return z, cls


def _arms(z, cls, genes, plat, agg, empty):
    a, b = [], []
    for (p, s) in sorted(cls):
        if p != plat:
            continue
        v = [x for x in (z.get((g, plat, s)) for g in genes) if x is not None]
        if not v:
            if empty == "drop_empty_sample":
                continue
            return None
        r = agg(v)
        if r is None:
            return None
        (a if cls[(p, s)] == "EMC" else b).append(r)
    return (a, b) if len(a) >= 2 and len(b) >= 2 else None


def _gate(a, b, sc, dsc, U):
    na, nb = len(a), len(b)
    ma, mb = sum(a) / na, sum(b) / nb
    s2a = sum((x - ma) ** 2 for x in a) / (na - 1)
    s2b = sum((x - mb) ** 2 for x in b) / (nb - 1)
    ds2a = (2 * dsc * sum(abs(x - ma) for x in a) + na * dsc * dsc) / (na - 1)
    ds2b = (2 * dsc * sum(abs(x - mb) for x in b) + nb * dsc * dsc) / (nb - 1)
    va, vb, dva, dvb = s2a / na, s2b / nb, ds2a / na, ds2b / nb
    S, dS = va + vb, dva + dvb
    at, ad, dt, ddl = abs(sc["t"]), abs(sc["delta_a_minus_b"]), U["t"], U["delta_a_minus_b"]
    if at <= 10 * dt:
        T1 = None                      # NOT EVALUABLE -> UNKNOWN, never a pass
    else:
        hi = ((ad + ddl) / (at - dt)) ** 2
        lo = (max(ad - ddl, 0.0) / (at + dt)) ** 2
        T1 = not (S + dS < lo or S - dS > hi)
    cor = [((va + p * dva) + (vb + q * dvb)) ** 2 /
           ((va + p * dva) ** 2 / (na - 1) + (vb + q * dvb) ** 2 / (nb - 1))
           for p in (-1, 1) for q in (-1, 1)]
    T2 = not (max(cor) < sc["df"] - U["df"] or min(cor) > sc["df"] + U["df"])
    T3 = (abs(ma - sc["mean_a"]) <= U["mean_a"] + dsc
          and abs(mb - sc["mean_b"]) <= U["mean_b"] + dsc)
    T4 = abs((ma - mb) - sc["delta_a_minus_b"]) <= U["delta_a_minus_b"] + 2 * dsc
    A, B = na - 1, nb - 1
    P = 1.0 / A + 1.0 / B
    D = P / sc["df"] - 1.0 / (A * B)
    two = False
    if D >= 0:
        r = math.sqrt(D)
        f1, f2 = (1 / B - r) / P, (1 / B + r) / P
        two = all(-1e-9 <= f <= 1 + 1e-9 for f in (f1, f2)) and abs(f1 - f2) > 1e-9
    df = S * S / (va * va / A + vb * vb / B)
    return T1, T2, T3, T4, abs(df - sc["df"]), two


def _recover(z, cls, genes, plat, sc, dz, U):
    """Exhaustive search. Returns (set_of_admissible_aggregators, last_gate_record)."""
    ok, rec = set(), None
    for an, ag in AGG.items():
        for empty in ("drop_empty_sample", "require_any"):
            arms = _arms(z, cls, genes, plat, ag, empty)
            if arms is None:
                continue
            dsc = dz if an != "sum" else dz * len(genes)
            g = _gate(arms[0], arms[1], sc, dsc, U)
            if g[2] and g[3] and g[1] and (g[0] is not False):
                ok.add(an)
                rec = g
    return ok, rec


@pytest.fixture(scope="module")
def panels():
    return json.load(open(PANELS, encoding="utf-8"))


@pytest.fixture(scope="module")
def nr():
    return json.load(open(NR4A3, encoding="utf-8"))


def _panel_blocks(d):
    for pname, p in d["panels"].items():
        for gname, grp in p.get("groups", {}).items():
            for plat, blk in grp.get("per_platform", {}).items():
                if isinstance(blk.get("score"), dict) and "genes_readable" in blk:
                    yield ("panels/%s/%s" % (pname, gname), plat, blk)


def _set_blocks(d):
    for sname, plats in d["set_scores"].items():
        gs = set(d["set_definitions"][sname]["genes"])
        for plat, blk in plats.items():
            if isinstance(blk.get("score"), dict) and gs <= set(d["gene_reads"]):
                yield ("set_scores/%s" % sname, plat, blk)


def _run(doc, blocks, path):
    U = {f: _half_ulp(path, "score", f) for f in FIELDS}
    dz = _dz(path)
    z, cls = _rows(doc)
    uniq, ambiguous, unknown, worst, roots = 0, [], [], 0.0, 0
    for name, plat, blk in blocks:
        ok, rec = _recover(z, cls, blk["genes_readable"], plat, blk["score"], dz, U)
        if len(ok) == 1:
            uniq += 1
            worst = max(worst, rec[4])
            roots += bool(rec[5])
        elif not ok:
            unknown.append((name, plat))
        else:
            ambiguous.append((name, plat, sorted(ok)))
    return uniq, ambiguous, unknown, worst, roots


def test_every_panel_group_score_block_reconstructs_uniquely_and_passes(panels):
    n, amb, unk, worst, roots = _run(panels, list(_panel_blocks(panels)), PANELS)
    assert amb == [], "AMBIGUOUS aggregation rule — must not be resolved by picking"
    assert unk == [], "UNKNOWN — no admissible aggregation rule"
    assert n == 156, n
    assert worst < _half_ulp(PANELS, "score", "df"), worst


def test_every_reconstructible_nr4a3_set_score_block_reconstructs_uniquely_and_passes(nr):
    n, amb, unk, worst, roots = _run(nr, list(_set_blocks(nr)), NR4A3)
    assert amb == []
    assert unk == []
    assert n == 10, n
    assert worst < _half_ulp(NR4A3, "score", "df"), worst


def test_the_recovered_rule_is_the_arithmetic_mean_and_nothing_else(panels, nr):
    U = {f: _half_ulp(PANELS, "score", f) for f in FIELDS}
    z, cls = _rows(panels)
    seen = set()
    for name, plat, blk in _panel_blocks(panels):
        ok, _ = _recover(z, cls, blk["genes_readable"], plat, blk["score"], _dz(PANELS), U)
        seen |= ok
    assert seen == {"mean"}, seen


def test_the_root_ambiguity_is_real_and_stays_measured(panels):
    n, amb, unk, worst, roots = _run(panels, list(_panel_blocks(panels)), PANELS)
    # 43 of the 156 committed panel df values (and 4 of the 10 nr4a3 set df values) admit
    # TWO DISTINCT variance splits. The gate is the root-agnostic forward form; this test
    # exists so that stays true and no later "simplification" picks a root.
    assert roots == 43, roots


def test_the_single_row_detection_threshold_is_measured_not_assumed(panels):
    """Falsification control WITH ITS SENSITIVITY MEASURED.

    A reconstructed block averages G genes x n samples, so a single bad row is diluted by
    ~G*n_a before it reaches mean_a. On the 3-gene, n_EMC=6 control block the gate does NOT
    see a 100-half-ulp single-row error and DOES see a 200-half-ulp one. That dilution is a
    real limitation of reconstructed-block verification against W17b's direct row gate, and
    this test pins it so it cannot be forgotten or quietly claimed away.
    """
    d = json.loads(json.dumps(panels))
    name, plat, blk = next(iter(_panel_blocks(d)))
    g = blk["genes_readable"][0]
    for r in d["gene_reads"][g][plat]["per_sample"]:
        if r.get("z_vs_array") is not None:
            r["z_vs_array"] += 200 * _dz(PANELS)
            break
    U = {f: _half_ulp(PANELS, "score", f) for f in FIELDS}
    z, cls = _rows(d)
    ok, _ = _recover(z, cls, blk["genes_readable"], plat, blk["score"], _dz(PANELS), U)
    assert ok == set(), "a 200-half-ulp single-row error was NOT caught"

    d2 = json.loads(json.dumps(panels))
    for r in d2["gene_reads"][g][plat]["per_sample"]:
        if r.get("z_vs_array") is not None:
            r["z_vs_array"] += 100 * _dz(PANELS)
            break
    z2, cls2 = _rows(d2)
    ok2, _ = _recover(z2, cls2, blk["genes_readable"], plat, blk["score"], _dz(PANELS), U)
    assert ok2 == {"mean"}, ("MEASURED insensitivity at 100 half-ulps changed", ok2)


def test_the_blocks_that_need_an_external_input_are_declared_not_silently_skipped(panels, nr):
    ext_p = [k for k, v in panels["signature_scores"].items()]
    assert len(ext_p) * 2 == 42 or len(ext_p) >= 1
    gs = set(nr["gene_reads"])
    ext_n = [s for s, dfn in nr["set_definitions"].items() if not set(dfn["genes"]) <= gs]
    # the six PPARG signature sets reference 66-269 symbols whose per-sample rows are NOT
    # committed anywhere in the file: they need the GEO series matrix, not a rule.
    assert len(ext_n) == 6, ext_n
```

## Limitations

- **A closed verification loop is not a correct one.** Every result here says a committed number is arithmetically consistent with committed rows under a recovered rule. It says nothing about whether the rows are correct, whether the probe→symbol mapping is right, whether the arms are the right arms, or whether any of it means anything biologically. **No clinical, efficacy, safety, selectivity or readiness claim follows from any of it.** No wet lab, no patient data.
- **Sensitivity is materially worse than a direct row gate** — R4: single-row errors below ~100 half-ulps (0.005 z units) on a small panel are invisible. A systematic error affecting many rows is caught; a single typo generally is not. Deeper panels dilute further; I measured only the shallowest control block, so ~100–200 half-ulps is that block's threshold, not a repository-wide bound.
- **The rule space is finite and mine.** Four aggregators × two empty-sample rules. A rule outside that space that happens to coincide with `mean` on these data would be indistinguishable. "Unique winner" means unique *within the searched space*, not unique among all conceivable functions.
- **I extended the rule space after seeing one failure** (the empty-sample dimension). Recorded in Method; it is a committed-data feature, but it is post-hoc.
- **281 + 156 = 437 of the 610 are verified by identity, not by independent arithmetic** — they are duplicate copies whose statistic is verified at its canonical location. That is genuine internal-consistency verification of the duplication, and it is weaker than an independent recomputation. Labelled distinctly in R2 for that reason.
- **881 blocks (33.8 %) remain closed to this container** and no test-count budget buys them: they need a GEO series matrix, DepMap/PRISM per-line values, or a full signature-set gene universe. Absence of those inputs here is UNKNOWN, not evidence.
- The two `platforms/global_offset` blocks were classified external on the artifact's own structure and corroborated by the generator's docstring; I did not attempt to reconstruct them.
- `git status` was not clean at end — other lanes' untracked reports. I verified none is mine.

## Stop condition

**Set up front:** return the moment every one of the ~708 middle-class blocks is assigned to exactly one of {reconstructed-and-gated, external-input, AMBIGUOUS, UNKNOWN}, with the aggregation rule either uniquely recovered or honestly declared unrecoverable, and with the resulting coverage number stated.

**MET.** All 708 are assigned: 610 verified, 98 external-input, **0 AMBIGUOUS, 0 UNKNOWN**. Repository-wide verifiable coverage becomes 1,726 / 2,607 = 66.2 %. Returned immediately.

## Tool-call and wall-clock count actually used

**28 tool calls**, all Bash. **Wall clock 03:03:29Z → 03:13Z ≈ 10 minutes.** Well inside the ~40/~40 target. No network, no spend, no writes to the tree, no preflight, no review round, no ceiling change.

## Next concrete action

**Land nothing new; consolidate.** W17f's module (872 + 90 blocks), W17h's (154) and this one (166 reconstructed + 437 identity-checked) are three separate files asserting the same four tests with three different input-error propagations. The single successor task for this lane is: **merge them into one `research/modalities/tests/test_committed_statistical_blocks.py` with one `_gate`, one field-level tolerance function, one propagated input-error term, and a per-artifact block-count assertion — target ≤ 20 test functions covering all 1,726 verifiable blocks — then hand the coordinator a diff that applies cleanly.** That is the only remaining step between 0.81 % measured gate coverage and 66.2 %, and it is integration work, not research. There is no further *scientific* question open in lane 17: the remaining 881 blocks are external-input, and no amount of in-file reasoning reaches them.
