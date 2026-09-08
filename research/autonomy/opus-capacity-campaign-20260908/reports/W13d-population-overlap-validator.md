> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W13d** — lane 13 refill (provenance / identity contract in committed data).

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the runtime model from the child transcript. I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 02:27:03 UTC 2026`. `date -u` at end: `Tue Sep  8 02:29:55 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start run; the four long proxy-host lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy` and `JAVA_TOOL_OPTIONS` are elided by me at the end run and are unchanged between the two — nothing else altered):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`.** This is NOT the commit named as frozen in `COMMON-BRIEF.md` (`92abbcb905cacf07f14b238db50d1b98f6590374`); the checkout has advanced. `git status --porcelain` shows the working tree modification is confined to `WAVE-LOG.md` plus untracked campaign reports; the three files I read as evidence (`research/data/emc-clinical-registry.json`, `systems/POLICY-evidence.md`, `research/modalities/emc-site-curation.json`) are clean at that HEAD (`git status --porcelain <those three> | wc -l` → `0`), so my quotes are committed content. I wrote nothing into the tree.

## Question

Findings A5 and A6 of `W13-provenance-identity-contract.md`: four registry rows assert a population overlap and name no counterpart, and `populationKey` is absent on 9 of 14 cohorts — a silent exemption from the double-counting guard rather than a declared one. **Are these two properties checkable by a validator over committed data, what does such a validator report today, does `systems/POLICY-evidence.md` already require either property, and which pooled figures in the repository currently sum across a cohort that declares an unnamed overlap?**

It is open because W13 asserted A5/A6 inside a 12-finding inventory whose validator bundles them with ten other checks; neither finding had been separated, re-verified at a later HEAD, tested against the governing policy for whether it is a *violation* or a *proposal*, or costed in terms of which downstream figures it actually touches.

**I make no determination about what any cohort `n` counts.** That is W13c's live question (A1/A2, the `nUnit` question); every `n` below is transcribed as committed, with no unit reading attached.

## Prior-work check

Commands run and what they showed:

- `grep -n "A5\|A6\|A3\|populationKey\|contextReason\|overlap" reports/W13-provenance-identity-contract.md` — confirms W13 lines 124 (A5), 125 (A6), and its proposed schema fields `population_key` / `overlaps_population_key` (lines 309–316) and checks `C5-OVERLAP-UNNAMED` / `C6-POPULATION-KEY-MISSING` (lines 407–416). W13's validator is a 12-check bundle; it was not re-run here, and I wrote an independent two-check implementation rather than re-executing W13's.
- `rg -n "overlapsPopulationKey|populationKeyUnknown|overlapsSourceId|populationKeyNotApplicable" --glob '!.git' .` — **exactly one hit, and it is inside W13's own untracked report** (`W13-provenance-identity-contract.md:413`). No such field exists anywhere in committed data. So no counterpart-naming or absence-declaration mechanism is in the repository today; both are genuinely new fields.
- `grep -rn "populationKey" --include=*.py --include=*.json --include=*.md -l .` → 7 files: the registry, `POLICY-evidence.md`, `emc_fusion_partner_pooling.py`, `emc-fusion-partner-pooling.json`, and three campaign reports (W13, W13b, W15c).
- `git ls-files | rg -i "validate-registry|overlap"` — the tracked `overlap` files are all GSE243553/ABFE artifacts, unrelated.
- `grep -rln "emc-clinical-registry" --include=*.py --include=*.mjs --include=*.js .` → 17 consumers, enumerated for the blast-radius pass.

Closed items I confirmed I am not replaying: the registry ICD-O paper (user-rejected), PUB-EMC-CLASSIFICATION, any Brenca route, and patient/case/specimen identity (CLOSED-unresolved — I did not attempt to identify any patient, and the `registry.patients` rows are out of scope here). W13c's cohort-unit question is untouched.

## Method / inputs

| Input | Path | Role |
|---|---|---|
| Clinical registry | `/home/user/Rare-cancers/research/data/emc-clinical-registry.json` | the committed data under test; `registry.cohorts` (14 rows), `registry.citations` (25), `treatments.systemicEvidence` (10) |
| Governing policy | `/home/user/Rare-cancers/systems/POLICY-evidence.md` (386 lines) | read §2.1–§2.4 and §5 to settle the compliance-vs-proposal question |
| Existing guard | `/home/user/Rare-cancers/scripts/validate-registry.mjs` | baseline; line 113 is the exemption A6 names |
| Pooling consumers | `research/meta/meta-analysis.mjs`, `research/modalities/emc_site_curation.py`, `research/modalities/emc_locoregional_eligibility.py`, `research/modalities/emc_ipd_survival.py`, `research/manuscripts/emc_systemic_therapy_pooling.py` | blast-radius search |
| Pooled artifact | `research/modalities/emc-site-curation.json` | the one artifact with real exposure |
| My validator | `/tmp/claude-0/w13d/check_overlap_contract.py` (authored here, outside the tree; source inline below) | the two checks |
| Negative-control fixture | `/tmp/claude-0/w13d/fixture-negative-control.json` | throwaway `/tmp` copy with the two fields synthetically populated, to prove the checks can pass. **Never written to the repository, and its synthetic values are not proposals for any row.** |

Tools: Python 3.11.15, Node v22.22.2. No network. Read-only on the tree.

## Result

### R1 — A5 re-verified at HEAD `b9a0257`: four cohort rows, verbatim

All four are `pool: false`. Quoted exactly as committed (`registry.cohorts`, indices as in the file):

| Idx | `label` | `sourceId` | `n` | `contextReason` (verbatim) | `populationKey` | Grade |
|---|---|---|---|---|---|---|
| 5 | `Localised, single-institution series` | `bishop2019` | 41 | `"population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)"` | absent | PRIMARY |
| 6 | `Localised, US SEER population` | `remiszewski2025` | 156 | `"population-overlap; percentage-only"` | absent | PRIMARY |
| 9 | `SEER overall-survival series` | `seer270_2022` | 270 | `"population-overlap; percentage-only"` | absent | PRIMARY |
| 11 | `Single-institution series (U Michigan)` | `uMich2023` | 44 | `"population-overlap"` | absent | PRIMARY |

`n` is transcribed only; **no unit determination is made or implied** (W13c owns that).

**A5 is confirmed, and it extends further than W13 recorded.** A fifth row outside `registry.cohorts` has the identical defect: `treatments.systemicEvidence[7]`, agent `"Trabectedin (second EMC-specific series)"`, `sourceId: "palmerini2022trobsultrarare"`, `n: 3`, `pool: false`, `contextReason: "population-overlap"` — a structured field that names no counterpart. Its `result` free-text *does* narrate a suspected counterpart at length (`chiusole2020`, TrObs vs Istituto Oncologico Veneto, shared author A. Brunello) and ends `"Neither paper says whether any patient appears in the other"`. That narration is unreachable prose: the machine-readable counterpart field is empty, so a checker sees the same UNKNOWN as for cohorts 5/6/9/11. Grade: PRIMARY. This row was not in W13's A5 (W13 scoped A5 to `cohorts[]`), so the count is **5 declared overlaps with no resolvable counterpart, not 4**.

Only four `populationKey` values are declared anywhere in the file: `masunaga2025-jpreg` (shared by cohorts 0 and 1 as strata), `meisKindblom1999`, `ussc2022`, `chiusole2020`. **A counterpart named for any of the five rows would therefore have to resolve against a namespace of four keys, none of which is a SEER, US-Sarcoma-Collaborative-membership, or TrObs population.** The counterpart is UNKNOWN in committed data; I do not infer one from size, country or date, and W13c's live question means I would not infer one anyway.

### R2 — A6 re-verified: exactly which 9 cohorts lack `populationKey`

Present on 5: indices 0, 1 (`masunaga2025-jpreg`), 2 (`meisKindblom1999`), 3 (`ussc2022`), 4 (`chiusole2020`) — i.e. precisely the five `pool: true` rows.

Absent on 9 — indices 5, 6, 7, 8, 9, 10, 11, 12, 13:

| Idx | `label` | `sourceId` | `n` | `contextReason` | Grade |
|---|---|---|---|---|---|
| 5 | Localised, single-institution series | `bishop2019` | 41 | population-overlap (…) | PRIMARY |
| 6 | Localised, US SEER population | `remiszewski2025` | 156 | population-overlap; percentage-only | PRIMARY |
| 7 | Local recurrence by surgical margin | `remiszewski2025` | 31 | percentage-only | PRIMARY |
| 8 | Advanced disease on pazopanib | `remiszewski2025` | 26 | different-endpoint | PRIMARY |
| 9 | SEER overall-survival series | `seer270_2022` | 270 | population-overlap; percentage-only | PRIMARY |
| 10 | Two-referral-center long-term series (Drilon) | `drilon2008` | 87 | percentage-only | PRIMARY |
| 11 | Single-institution series (U Michigan) | `uMich2023` | 44 | population-overlap | PRIMARY |
| 12 | Japanese multi-institutional series | `japan2003` | 42 | different-endpoint | PRIMARY |
| 13 | Chinese series | `china2016` | 40 | percentage-only | PRIMARY |

The absence is perfectly correlated with `pool: false`, which is why it never surfaces: `scripts/validate-registry.mjs:113` reads

```js
if (c.pool !== false && c.populationKey) {
```

Both conjuncts fail for all nine. A6 stands exactly as W13 stated it: the omission is a **silent exemption**, not a flagged gap. Note the structural consequence — cohorts 6, 7 and 8 all draw on `sourceId: "remiszewski2025"`, so if any of them were ever flipped to `pool: true` there is today no key by which the guard could tell whether they are disjoint strata of one population. That is latent, not active.

### R3 — the policy question: PROPOSED NEW REQUIREMENT, not a compliance gap

I read `systems/POLICY-evidence.md` before forming a view. The two governing passages, verbatim:

§2.3, on `populationKey`:
> **Within a study:** use **mutually exclusive strata** only. Never pool a whole-cohort row *and* its sub-strata. Strata of one study share a `populationKey` and declare a distinct `stratum`; the validator flags two pooled cohorts that share both.

§2.3, on overlap:
> **Across studies:** single-institution series are often subsets of national or SEER registries. Where populations may overlap, the **smaller/overlapping** cohort is marked `pool: false` with `contextReason: "population-overlap"`. Distinct populations (e.g. a Japanese registry and a US single institution) may be pooled.

§5 checklist:
> - [ ] Overlapping / percentage-only / different-endpoint series set `pool:false` + `contextReason`.

**Ruling, and it goes against my checks:**

- **Check (i), counterpart naming: NOT REQUIRED BY POLICY.** §2.3 requires an overlapping row to be marked `pool: false` with `contextReason: "population-overlap"`, and nothing more. It never asks who the counterpart is. All five rows in R1 carry exactly what §2.3 and the §5 checklist demand. **They are compliant.** Requiring a resolvable counterpart is a **PROPOSED NEW REQUIREMENT**, and I label it as such. It is not a violation and must not be reported as one.
- **Check (ii), `populationKey` present-or-declared: NOT REQUIRED BY POLICY.** §2.3 scopes `populationKey` to *strata of one study* and to *pooled* cohorts ("the validator flags two pooled cohorts that share both"). It imposes no obligation on a `pool: false` row. The five pooled rows all carry one; the nine unpooled rows are outside the requirement. `validate-registry.mjs:113` implements §2.3 faithfully. **Also compliant, also a PROPOSED NEW REQUIREMENT.**

So both W13 findings are real and correctly described as *unguarded invariants*, but neither is a policy breach. The honest framing is: **A5 and A6 identify two properties the policy does not currently require, whose absence means the double-counting rule is enforced only inside the pool and is unfalsifiable outside it.** Whether to require them is a change to `POLICY-evidence.md` — the registry owner's decision, not a worker's, and explicitly not mine to make (I may not author my own acceptance criterion).

### R4 — blast radius: one artifact, two figures

I checked every consumer of the registry that computes a sum.

| Consumer | Treatment of the overlap-declaring rows | Exposure |
|---|---|---|
| `research/meta/meta-analysis.mjs:32` — `data.registry.cohorts.filter((c) => c.pool !== false)` | excludes all four cohort rows | **NONE** |
| `research/modalities/emc_locoregional_eligibility.py:148-159` — `if not c.get("pool"): skipped.append(...)`, reason recorded | excludes all four | **NONE** |
| `research/modalities/emc_ipd_survival.py` | carries a free-text `overlap_risk` on `seer270_2022` (`"⚠ US institutions overlap drilon2008 and uMich2023"`) and emits `⛔_this_is_not_a_pool` | **NONE** (nothing is summed) |
| `research/manuscripts/emc_systemic_therapy_pooling.py` | hard-codes its own rows, does not read `registry.cohorts`; its one overlap hazard (`population_overlap_warning`, A3) **names both counterparts** — the Italian anthracycline and sunitinib series — and keeps them in pools A2/A3 that are "reported separately and never summed" | **NONE** — this is the counterpart-naming discipline the proposed check would formalise, already practised, in prose |
| **`research/modalities/emc_site_curation.py` → `research/modalities/emc-site-curation.json`** | **deliberately overrides `pool: false` and pools `bishop2019` (cohorts[5]) with `chiusole2020` and `masunaga2025`** | **THE ONLY EXPOSURE** |

The two exposed figures, transcribed from `emc-site-curation.json` → `pooled_extremity_fraction`, **not recomputed and not corrected**:

| Figure | events/denom | percent | Wilson 95% CI | Contains | Grade |
|---|---|---|---|---|---|
| `extremity_strict` | 194 / 271 | 71.6% | 65.9 – 76.6 | chiusole2020, masunaga2025, **bishop2019 (n=41)** | PRIMARY (as committed) |
| `extremity_inclusive` | 229 / 271 | 84.5% | 79.7 – 88.3 | same three series | PRIMARY (as committed) |

A superseded pair is retained in the same file (70.4% strict / 85.7% inclusive over 230 patients, the two-series pool before `bishop2019` was added on 2026-08-27), so the exposure is dated and its before/after is on the record.

**This is not a concealed defect — the file argues its own case, verbatim:**
> The clinical registry marks bishop2019 `pool: false` with `contextReason: population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`. That exclusion bites only where an overlap PARTNER is inside the same pool, and neither SEER nor the US Sarcoma Collaborative contributes a site distribution to this one. ⛔ Pool membership is decided per pool, not once per source. The registry's recurrence and metastasis pools do contain ussc2022, so its flag stands unchanged there.

That reasoning is sound on its face and is exactly the argument W16b independently reached from the other side. **But it is the precise place where the missing counterpart field costs something.** The argument's soundness is entirely conditional on the counterpart set being `{SEER, US Sarcoma Collaborative}` — and that set is read out of a free-text `contextReason` whose own wording is a hedge (`"likely within"`). The registry does not assert who the counterpart is; it asserts that one is suspected. So the site pool's justification rests on a reading of prose that the registry itself does not commit to, and no check anywhere can verify that the counterpart named in the justification is the counterpart the registry meant. If the true counterpart were instead a series that *does* contribute a site distribution, the argument would fail silently and `71.6% / 84.5%` would be pooling some patients twice. **I cannot resolve that: the counterpart is UNKNOWN in committed data and I will not infer it.**

**Routing, not repair:** this belongs to whoever owns `systems/POLICY-evidence.md` and the registry. It is the same rule-ownership question W16b handed over from the opposite direction (W16b wanted to *admit* `bishop2019` to a non-pooling bound; `emc_site_curation.py` already *admits* it to a real pool). Two independent workers have now hit the identical clause. One decision — does `pool: false` for overlap travel with the source or attach per-pool, and must the counterpart be named — settles both.

## Validation evidence

**RUN — check 1 of 3: baseline, the existing guard is green.**
```
$ cd /home/user/Rare-cancers && node scripts/validate-registry.mjs
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
VALIDATE_REGISTRY_EXIT=0
```
Node v22.22.2. **Exit 0, zero warnings** — this is A6's point made empirically: nine cohorts sit outside the double-counting guard and the run reads clean.

**RUN — check 2 of 3: my two-check validator against committed data.**
```
$ cd /home/user/Rare-cancers && python3 /tmp/claude-0/w13d/check_overlap_contract.py research/data/emc-clinical-registry.json
```
Verbatim output (headers and per-check counts; the nine C-PK detail lines carry an identical `->` explanation and are elided here as `[…8 further rows, indices 6,7,8,9,10,11,12,13…]`):
```
registry            : research/data/emc-clinical-registry.json
cohorts             : 14
rows w/ contextReason: 10   of which declare overlap: 5
declared populationKeys: ['chiusole2020', 'masunaga2025-jpreg', 'meisKindblom1999', 'ussc2022']

[C-OV] overlap declared, counterpart resolvable: 5 finding(s)
   .registry.cohorts[5]  'Localised, single-institution series'
      -> declares contextReason='population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)' and names no counterpart in any resolvable field; the counterpart is UNKNOWN
   .registry.cohorts[6]  'Localised, US SEER population'
      -> declares contextReason='population-overlap; percentage-only' and names no counterpart in any resolvable field; the counterpart is UNKNOWN
   .registry.cohorts[9]  'SEER overall-survival series'
      -> declares contextReason='population-overlap; percentage-only' and names no counterpart in any resolvable field; the counterpart is UNKNOWN
   .registry.cohorts[11]  'Single-institution series (U Michigan)'
      -> declares contextReason='population-overlap' and names no counterpart in any resolvable field; the counterpart is UNKNOWN
   .treatments.systemicEvidence[7]  'Trabectedin (second EMC-specific series)'
      -> declares contextReason='population-overlap' and names no counterpart in any resolvable field; the counterpart is UNKNOWN

[C-PK] populationKey present or its absence declared: 9 finding(s)
   .registry.cohorts[5]  'Localised, single-institution series'
      -> populationKey is absent and its absence is not declared; validate-registry.mjs:113 guards overlap only `if (c.pool !== false && c.populationKey)`, so the omission is a SILENT EXEMPTION from the double-counting guard rather than a flagged gap
   [ …8 further rows, indices 6,7,8,9,10,11,12,13… ]

TOTAL FINDINGS: 14
EXIT=1
```
**Per-check counts: C-OV 5, C-PK 9, total 14, exit code 1.** Python 3.11.15.

**RUN — check 3 of 3: negative control, the checks can pass.** A throwaway `/tmp` fixture with both fields synthetically populated (never written to the repository; the synthetic values are placeholders, **not** proposed values for any row):
```
$ python3 /tmp/claude-0/w13d/check_overlap_contract.py /tmp/claude-0/w13d/fixture-negative-control.json
[C-OV] overlap declared, counterpart resolvable: 0 finding(s)

[C-PK] populationKey present or its absence declared: 0 finding(s)

TOTAL FINDINGS: 0
EXIT=0
```
**Exit 0.** The checks are falsifiable in both directions rather than unconditionally red.

**Read-only confirmed:** `git status --porcelain research/data/emc-clinical-registry.json systems/POLICY-evidence.md research/modalities/emc-site-curation.json | wc -l` → `0`. No git write operation of any kind was run.

**Validator source (authored in this run, returned inline per the brief; lives at `/tmp/claude-0/w13d/check_overlap_contract.py`, NOT in the tree):**

```python
#!/usr/bin/env python3
"""W13d read-only validator over committed data. Two checks, no writes, no repair.

C-OV  a row that DECLARES a population overlap must NAME its counterpart by a
      resolvable key (overlapsPopulationKey -> a declared cohort populationKey,
      or overlapsSourceId -> a registry.citations key).
C-PK  a cohort's populationKey is either PRESENT, or its absence is EXPLICITLY
      DECLARED (populationKeyUnknown / populationKeyNotApplicable, with a reason).
      Merely missing is neither.

Exit 0 = both checks clean. Exit 1 = at least one finding. Exit 2 = input error.
This validator NEVER authors a populationKey, never infers a counterpart, and
never touches a denominator.
"""
import json, sys

REG = sys.argv[1] if len(sys.argv) > 1 else "research/data/emc-clinical-registry.json"
try:
    D = json.load(open(REG))
except Exception as e:                                    # pragma: no cover
    print(f"INPUT-ERROR {REG}: {e}"); sys.exit(2)

reg = D.get("registry", {})
cohorts = reg.get("cohorts", [])
citations = reg.get("citations", {})
declared_popkeys = {c["populationKey"] for c in cohorts if c.get("populationKey")}

# every row anywhere in the file that carries a contextReason
rows = []
def walk(o, p=""):
    if isinstance(o, dict):
        if isinstance(o.get("contextReason"), str):
            rows.append((p, o))
        for k, v in o.items(): walk(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, f"{p}[{i}]")
walk(D)

findings = {"C-OV": [], "C-PK": []}
def lbl(r): return r.get("label") or r.get("agent") or "<unlabelled>"

# ---- C-OV -----------------------------------------------------------------
ov_rows = 0
for path, r in rows:
    if "overlap" not in r["contextReason"].lower():
        continue
    ov_rows += 1
    ck = r.get("overlapsPopulationKey"); cs = r.get("overlapsSourceId")
    if ck and ck in declared_popkeys:   continue
    if cs and cs in citations:          continue
    if ck or cs:
        findings["C-OV"].append((path, lbl(r), f"counterpart {ck or cs!r} does not resolve"))
    else:
        findings["C-OV"].append((path, lbl(r),
            f"declares contextReason={r['contextReason']!r} and names no counterpart "
            "in any resolvable field; the counterpart is UNKNOWN"))

# ---- C-PK -----------------------------------------------------------------
for i, c in enumerate(cohorts):
    if c.get("populationKey"): continue
    if c.get("populationKeyUnknown") or c.get("populationKeyNotApplicable"): continue
    findings["C-PK"].append((f".registry.cohorts[{i}]", lbl(c),
        "populationKey is absent and its absence is not declared; validate-registry.mjs:113 "
        "guards overlap only `if (c.pool !== false && c.populationKey)`, so the omission is a "
        "SILENT EXEMPTION from the double-counting guard rather than a flagged gap"))

print(f"registry            : {REG}")
print(f"cohorts             : {len(cohorts)}")
print(f"rows w/ contextReason: {len(rows)}   of which declare overlap: {ov_rows}")
print(f"declared populationKeys: {sorted(declared_popkeys)}")
print()
for cid, title in (("C-OV", "overlap declared, counterpart resolvable"),
                   ("C-PK", "populationKey present or its absence declared")):
    f = findings[cid]
    print(f"[{cid}] {title}: {len(f)} finding(s)")
    for path, l, why in f:
        print(f"   {path}  {l!r}\n      -> {why}")
    print()
total = sum(len(v) for v in findings.values())
print(f"TOTAL FINDINGS: {total}")
sys.exit(1 if total else 0)
```

**PROPOSED (NOT RUN):** integrating either check into `scripts/validate-registry.mjs` or any preflight tier. Not run, not attempted, and not appropriate until the policy question in R3 is decided by the registry owner — a check that fires 14 times against fully policy-compliant data would be a false alarm, not a guard.

## Limitations

- **Both checks are PROPOSED REQUIREMENTS, not compliance tests.** Exit 1 above means "14 rows lack a property `POLICY-evidence.md` does not ask for", not "14 violations". Any reader who quotes the exit code without R3 will misreport compliant data as defective.
- **No counterpart is resolved, and none can be from committed data.** For all five rows the counterpart is UNKNOWN. I did not infer one from cohort size, country, date, author or institution, and the `treatments.systemicEvidence[7]` prose narration of a suspected TrObs/Chiusole overlap is retained as the source's own hedged statement (`"Neither paper says whether any patient appears in the other"`), not converted into an answer.
- **No unit determination.** Every `n` is transcribed. W13c owns what a cohort `n` counts; nothing here depends on that answer and nothing here pre-empts it.
- **No pooled figure recomputed, corrected, or endorsed.** `71.6%` and `84.5%` are transcribed from `emc-site-curation.json` as committed. I did not assess whether they are right, and I added no case to any denominator.
- **This is bookkeeping, not science.** No clinical claim, no rate, no pooled estimate, no statement about EMC biology, prognosis or treatment follows from anything above.
- **Blast radius is bounded by my search, not proven exhaustive.** I traced the 17 code consumers of the registry and inspected the five that sum. A pooled figure that transcribes a registry number by hand into prose, rather than reading the JSON, would not appear in that trace. Absence of a further hit is UNKNOWN, not zero.
- **HEAD drift:** the brief's frozen commit is not this checkout's HEAD. My quotes are from `b9a0257`, verified clean for the three evidence files.
- **Model identity is self-report.** Not independently verified.

## Stop condition

**MET, all four clauses.** (i) A5 and A6 re-verified at HEAD `b9a0257` with verbatim `contextReason` quotes for four cohort rows plus a fifth previously-unrecorded row, and the nine `populationKey`-absent cohorts enumerated by index, label and source. (ii) A validator built under `/tmp` and executed with a real command, exit code 1 and per-check counts C-OV 5 / C-PK 9, plus a negative control at exit 0 and the existing guard's baseline at exit 0. (iii) The policy question answered from `POLICY-evidence.md` §2.3 and §5 with verbatim quotes: **neither property is required, so both are PROPOSED NEW REQUIREMENTS and neither finding is a violation.** (iv) Blast radius named: exactly one artifact and two figures (`emc-site-curation.json` → `pooled_extremity_fraction.extremity_strict` 194/271 = 71.6% [65.9–76.6] and `.extremity_inclusive` 229/271 = 84.5% [79.7–88.3]), routed to the registry/policy owner and neither recomputed nor corrected.

## Tool-call and wall-clock count actually used

**13 tool calls** (all Bash), **wall clock 02:27:03Z → 02:29:55Z = 2 min 52 s.** Well inside the ~40-call / ~40-minute target. No network, no spend, no git write, no repository write.

## Next concrete action

**One decision, not a computation, and it now has two independent petitioners.** Put a single question to the owner of `systems/POLICY-evidence.md`: *when a row is marked `pool: false` for population overlap, must it name its counterpart, and does that exclusion travel with the source or attach per-pool?* The package is complete and needs no further work: §2.3 as written requires neither naming nor a per-pool rule; `emc_site_curation.py` already pools `bishop2019` on a per-pool reading whose validity depends on a counterpart set read out of a hedged free-text string; W16b independently hit the same clause from the non-pooling side and handed it over unresolved; and the two figures at stake are transcribed above. If the answer is "counterpart must be named", the C-OV check is the enforcement and five rows need a counterpart supplied **by someone who can read the sources** — not inferred, and not by me. If the answer is "per-pool, no naming required", then `emc-site-curation.json`'s rationale should be promoted from a free-text note into the policy, C-OV is withdrawn, and A5 closes as a non-defect. Either way `populationKey` (C-PK/A6) is the cheaper half and can be settled independently: requiring `populationKeyUnknown: true` with a reason on the nine unpooled rows converts a silent exemption into a declared one without touching a single number.
