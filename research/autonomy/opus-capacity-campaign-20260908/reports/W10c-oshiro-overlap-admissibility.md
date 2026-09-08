> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: tree unmodified (`git status --porcelain` empty), the enumeration script re-ran to exit 0, and Oshiro's absence re-verified independently under PMID, DOI and author — with the one HEAD discrepancy I report below. Full report follows.

---

# W10c — Is Oshiro 2000 patient-independent of the retained EMC series, and is it IPD-admissible?

## Worker

- Worker **W10c**, refill for **Lane 10** (older-literature clinical evidence), executing the mandatory independence + admissibility gate W10b named.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), Claude Code 2.1.42, remote cloud container. I cannot observe the served model; the coordinator must extract the runtime model from the transcript. No finding below depends on which model produced it.
- `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — **no environment variable names a model.** Identity-bearing lines:

```
AI_AGENT=claude-code_2-1-263_agent
CLAUDECODE=1
CLAUDE_EFFORT=medium
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

- `date -u` at start: `Tue Sep  8 02:15:32 UTC 2026`. At end: `Tue Sep  8 02:16:06 UTC 2026`.
- **Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`. All execution in `/tmp/claude-0/w10c/`. `git status --porcelain` returns **empty** at end. No git write operation of any kind.
- ⚠ **HEAD discrepancy, reported not smoothed.** The brief freezes the read commit at `92abbcb905cacf07f14b238db50d1b98f6590374`. `git rev-parse HEAD` at my run returns **`b9a0257e6acff53ad22535cf2adf261313e0b250`**, and `git status --porcelain` is clean where W10b saw `?? research/autonomy/opus-capacity-campaign-20260908/`. The coordinator has evidently committed the campaign directory since W10b ran. I read a **later** commit than the frozen one. This does not affect any finding here — the registry, policy and modality files I read are not campaign files — but the coordinator should know the freeze no longer holds.

## Question

**Is Oshiro 2000 (PMID 11493979) patient-independent of the EMC series this repository already retains — specifically the Japanese/Asian ones — and is it IPD-admissible under the repository's *existing* criteria?**

Open because W10b established the paper is unretained and carries a real survival cohort, then explicitly deferred both gates. Under W05's rubric a separate publication does not imply separate patients; Oshiro is a Kyushu University group and the repository retains a Japanese *national* registry and a Japanese multi-institution series, so the overlap risk is concrete rather than theoretical.

**Both gates are now answered, and they answer the same way: no.** No pair reaches even tier B, and the paper is **named but unusable** for IPD.

## Prior-work check

Commands run, and what they showed:

1. Read `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W10b-older-literature-sweep.md` and `reports/W05-patient-independence-audit.md` before any other action. W05's four tiers are quoted verbatim in §R2 below and applied unrelaxed.
2. `rg -c -i "11493979" --glob '!.git' .` → **one file only**, `research/autonomy/opus-capacity-campaign-20260908/reports/W10b-older-literature-sweep.md` (6 occurrences). `rg -l -i "106689690000800209"` → the same single file. `rg -l -i "oshiro" research/ systems/ archive/` → W10b's report plus `research/modalities/geo-gse28866-brunner-series.json` (an unrelated GEO series record). **W10b's novelty finding independently reproduces: the paper is absent from the scientific corpus under PMID, DOI and author; its only footprint is W10b's own report.**
3. `rg -l -i -e "kyushu" -e "fukuoka" --glob '!.git' .` → **two files, neither a clinical record**: W10b's report, and `research/modalities/emc_ret_cistrome.py`. **The retained corpus never names Kyushu University or Fukuoka as a clinical source institution.** That is the single most decisive negative here, and it cuts *against* independence rather than for it: absence of the institution from the corpus is absence of a record, not evidence of disjointness (`CLAUDE.md` §4).
4. Closed items I confirm I am **not** replaying: I issued **no** request of any kind against Sunitinib 2014 (`24703573`), Wagner 2020 (`32856598`), CTARC 2022 (`35144048`), Trabectedin/RT 2018, the pazopanib primary, or the anthracycline paper (`24345066`). I made no `curl`, no `WebFetch`, no network request outside the PubMed MCP server. I did not touch the restricted NR4A Perspective, the registry ICD-O paper, Brenca, Hofvander/EGA, or lane-11 material. I re-derived nothing about `GSE4303`/`GSE28866`.

## Method / inputs

- Corpus: `/home/user/Rare-cancers` at `b9a0257e6acff53ad22535cf2adf261313e0b250` (see HEAD note above).
- Committed files read: `research/data/emc-clinical-registry.json` (25 citation records, 8 Asian/Japanese), `research/modalities/emc_ipd_survival.py` (`CANDIDATE_SOURCES`, 16 series), `research/literature/emc-ipd-admissibility-2026-08-12.json`, `research/literature/emc-km-admissibility-2026-08-27.json`, `systems/POLICY-evidence.md` §2.3 and §2.7, `systems/views/L2-rt-ipd-survival.md`.
- Tools: ripgrep + Python 3 stdlib under Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k`; PubMed MCP server (`get_article_metadata`, `get_full_text_article`).
- **According to PubMed**, metadata fetched for PMIDs `11493979`, `12599237`, `27418251` in one call.

### ⛔ Tool defect found — report to the coordinator

`mcp__PubMed__get_full_text_article` **silently accepts a PMID as a PMCID and returns a different paper.** I passed `pmc_ids: ["11493979"]` (Oshiro's PMID) and the tool returned `PMCID PMC11493979 / PMID 39433838`, *"A causal role of the right dorsolateral prefrontal cortex in random exploration"*, Sci Rep 2024, [DOI](https://doi.org/10.1038/s41598-024-76025-5) — a neuroscience TMS study with no relation to EMC. **No error, no warning, ~15 KB of confident full text.** Any worker who passes a PMID to this tool gets a real full text of the wrong article. I discarded it entirely; **none of Oshiro's content in this report comes from that response.**

## Result

### R1 — Retained Japanese/Asian EMC series (PRIMARY)

Enumerated from `research/data/emc-clinical-registry.json`, cross-read against `emc_ipd_survival.py:CANDIDATE_SOURCES`. Institutions from author affiliations, **according to PubMed** where I fetched them.

| key | n | accrual window | `pool` | PMID / DOI | institution(s) | evidence class |
|---|---|---|---|---|---|---|
| `masunaga2025` | **171** | **2002–2022** | **true** | [10.1186/s13018-025-06245-6](https://doi.org/10.1186/s13018-025-06245-6) | **Japanese National Bone & Soft Tissue Tumour Registry** — national, institution-agnostic | PRIMARY |
| `japan2003` (Kawaguchi) | 42 | **UNKNOWN** (`studyPeriodUnknown: true`; mean follow-up 7.4 y, published 2003) | false | 12599237 / [10.1002/cncr.11162](https://doi.org/10.1002/cncr.11162) | **"eight affiliated hospitals", NOT enumerated**; central review at "the Pathology Center". Author affiliations name only Sapporo Medical (lead, Kawaguchi/Hasegawa) — the other 12 authors carry no affiliation in the PubMed record | PRIMARY |
| `morioka2016trabectedin` | 5 (2 EMC) | UNSTATED; trial JapicCTI-121850 registered 2012-05-31 | n/a | 27418251 / [10.1186/s12885-016-2511-y](https://doi.org/10.1186/s12885-016-2511-y) | **17 affiliations fully enumerated**: Keio, JFCR, Osaka Med Ctr, Aichi CC, Osaka Natl, Shizuoka CC, Chiba CC, Hokkaido CC, Kanagawa CC, Okayama, Mie, NCC Tokyo. **No Kyushu.** | PRIMARY |
| `china2016` | 40 | UNKNOWN | false | 27402218 / [10.1016/j.anndiagpath.2016.04.004](https://doi.org/10.1016/j.anndiagpath.2016.04.004) | China (unspecified in retained record) | PRIMARY |
| `huang2023` | 58 | UNSTATED | n/a | 36948401 / [10.1016/j.modpat.2023.100161](https://doi.org/10.1016/j.modpat.2023.100161) | Taiwan (Huang HY, Chang Gung et al.) | PRIMARY |
| `apatinib2020` | 33 (3 EMC) | 2009–2019 | n/a | [10.2147/cmar.s253201](https://doi.org/10.2147/cmar.s253201) | China | PRIMARY |
| `jiang2026`, `wang2026` | 1, 1 | UNSTATED | n/a | — | single-patient case reports | PRIMARY |

**Oshiro 2000, according to PubMed** ([DOI](https://doi.org/10.1177/106689690000800209)): first-author affiliation **"Department of Anatomic Pathology, Graduate School of Medical Science, Kyushu University"**; the other five authors (Shiratsuchi, Tamiya, Oda Y, Toyoshima, Tsuneyoshi) carry **no affiliation** in the PubMed record. Tsuneyoshi M and Oda Y are the Kyushu University anatomic-pathology group. **The abstract states no accrual window and no institution beyond that affiliation line, and prints no per-case table.**

**Five of the seven Asian series have no documented accrual window at all.** That single fact caps every verdict below.

### R2 — W05 rubric applied, per pair (PRIMARY)

W05's tiers, unrelaxed and quoted: **A** = an explicit author non-overlap statement *or* non-intersecting per-case identifiers; **B** = **all three** of disjoint institution **and** disjoint accrual window **and** disjoint identifier space, *each individually documented*; **C** = any strict subset of B, or disjoint demographics — **falsifier only, licenses nothing**; overlap can be established at any tier by a positive match.

| pair | inst. disjoint | accrual disjoint | identifier space disjoint | **tier** | **verdict** | specific missing evidence |
|---|---|---|---|---|---|---|
| Oshiro vs **masunaga2025** (n=171, JNBSTR 2002–2022) | **NO** | UNDOCUMENTED | UNDOCUMENTED | **C** | **UNKNOWN** | (i) Oshiro's stated accrual window, from the full-text Materials & Methods — I have only a *ceiling* of ≤2000 inferred from the publication date, which is an inference, not a documented window; (ii) whether JNBSTR's "2002–2022" is **diagnosis** year or **registration** year; (iii) per-case identifiers in either. **A national registry can never be institution-disjoint from any Japanese institution**, so this pair is structurally incapable of reaching tier B — tier A is its only route. |
| Oshiro vs **japan2003** (Kawaguchi, n=42) | **UNDOCUMENTED** | UNDOCUMENTED | UNDOCUMENTED | **C** | **UNKNOWN — the highest-risk pair** | (i) **the enumeration of Kawaguchi's eight affiliated hospitals**, which the abstract withholds and which is the single decisive datum; (ii) both accrual windows; (iii) per-case demographics tables in both for a tier-C falsifier run. Both are Japanese, both era-overlap on any plausible reading, and both route through a central pathology review. |
| Oshiro vs **morioka2016trabectedin** (n=5, 2 EMC) | **YES** (12 institutions enumerated, no Kyushu) | UNDOCUMENTED | UNDOCUMENTED | **C** | **UNKNOWN** | Oshiro's accrual window and per-case identifiers. ⚠ **A temporal argument does not work here even in principle**: Oshiro accrues at *diagnosis* (≤2000), Morioka at *trial treatment* (≥2012). Those are different time axes on the same person, and EMC is indolent enough — Oshiro's own 10-year survival is 63% — that a patient diagnosed in the 1990s could be enrolled in a 2012 trial. |
| Oshiro vs **china2016** (n=40) | YES (different country) | UNDOCUMENTED | UNDOCUMENTED | **C** | **UNKNOWN**, overlap implausible | both accrual windows; per-case identifiers. Two of B's three conditions unmet. |
| Oshiro vs **huang2023** (n=58, Taiwan) | YES (different country) | UNDOCUMENTED | UNDOCUMENTED | **C** | **UNKNOWN**, overlap implausible | as above. |
| Oshiro vs `apatinib2020`, `jiang2026`, `wang2026` | YES | UNDOCUMENTED | UNDOCUMENTED | **C** | **UNKNOWN**, overlap implausible | as above; n=3, 1 and 1 EMC respectively, so nothing turns on them. |

**No pair reaches tier A. No pair reaches tier B. Every pair is tier C, and tier C licenses nothing.** The honest verdict for Oshiro 2000 against the retained corpus is **UNKNOWN — not EVIDENCED-INDEPENDENT, and not shown OVERLAPPING either.**

**What I did *not* find, stated as a negative:** I found no positive overlap match — no shared specimen identifier, no shared accession, no shared author between Oshiro and any retained series. Under the rubric's asymmetry, `OVERLAPPING` is the cheap verdict and I could not reach it. **That is not evidence of independence.** Both series publish nothing at case level, so the cheap test could not run in either direction; the identifier space is empty on both sides rather than disjoint.

### R3 — The repository's own §2.3 already decides the pooling question (PRIMARY)

Independently of W05's rubric, `systems/POLICY-evidence.md` §2.3 states:

> *"Across studies: single-institution series are often subsets of national or SEER registries. Where populations may overlap, the **smaller/overlapping** cohort is marked `pool: false` with `contextReason: "population-overlap"`."*

Oshiro is a **single-institution Japanese series** and `masunaga2025` is a **Japanese national registry** already carrying `pool: true`. Under the repository's existing rule the smaller member of that pair is the one that gets `pool: false`. Note that the registry already applies exactly this treatment to `japan2003` (`pool: false`) and `china2016` (`pool: false`). **Even had the independence gate passed, §2.3 would place Oshiro's 36 outside the pooled denominator by default.** I have not added them to any denominator, and no pooled figure in this repository changes on account of this report.

### R4 — IPD-admissibility verdict: **NAMED BUT UNUSABLE** (PRIMARY)

Applying the criteria that already exist, not new ones:

| existing criterion | source | Oshiro 2000 | verdict |
|---|---|---|---|
| **(a) A numbers-at-risk table is mandatory.** "A curve without a risk table is **refused, not admitted with a caveat**." | `POLICY-evidence.md` §2.7(a); enforced by `emc_ipd_survival.py` | **No figure of any kind observed.** What is retained is two aggregate percentages (5-year 73%, 10-year 63%) and one p-value (0.0271), all abstract-level. | **REFUSED** at retained strength |
| **(b) The reconstruction must reproduce its own input** | §2.7(b) | inapplicable — no digitized curve exists | n/a |
| **(c) Digitization provenance required per curve** | §2.7(c) | inapplicable | n/a |
| **(d) §2.1/§2.3 bind: only non-overlapping populations may be combined** | §2.7(d) | **fails** — R2 returns UNKNOWN on every pair, and R3 puts it at `pool: false` by default | **REFUSED** |
| retrieval status | `emc-km-admissibility-2026-08-27.json` verdict vocabulary | would be recorded **`unreachable`** — the risk-row question is **unasked, not answered no** | — |

**W10b's gate, applied as written:** *"if the paper reports only aggregate percentages with no risk table and no per-patient rows, it is not IPD-admissible, and this lane closes on a named-but-unusable source."* At the strength I can actually retrieve, that condition holds exactly. **This lane closes on a named-but-unusable source.**

⚠ **The distinction the repository insists on, preserved:** this is a **`unreachable`** verdict, not a `refused_no_risk_row` verdict. I have not seen Oshiro's figures. Whether the paper prints a Kaplan–Meier curve with a numbers-at-risk row is **UNKNOWN** — an absent reading is not a reading of absence. What is *established* is that the paper is **not admissible on what this repository can currently retrieve**, which is a different and weaker statement than "the paper carries nothing".

### R5 — Retrieval attempt and its honest outcome (PRIMARY)

- **According to PubMed**, `get_article_metadata(["11493979"])` returned the record with `identifiers: {"pmid":"11493979","doi":"10.1177/106689690000800209"}` — **no `pmc` field.** The paper is **not in PubMed Central**, so the free full-text route this MCP server offers **does not exist for it**. This is a determinate negative about the route, not a refusal.
- `get_full_text_article(["11493979"])` returned **the wrong article** (see the tool defect above). Discarded.
- *Int J Surg Pathol* 2000 is a SAGE subscription journal. I issued **no** HTTP request to the publisher. Per the brief, an unattempted-and-unreachable subscription source is an **honest unrecovered source**; I did not route around it, and it appears on no denied list, so this is not a denied-route replay.
- **Retained strength for Oshiro 2000 is therefore: abstract only.** The survival figures stay exactly where W10b left them and are not re-derived, not pooled, and not compared numerically to any retained series.

## Validation evidence

**RUN.** All execution in `/tmp/claude-0/w10c/`, Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k`, `bash`, Python 3 stdlib, ripgrep.

| # | Command | Exit | Verbatim key output |
|---|---|---|---|
| 1 | `git rev-parse HEAD` | 0 | `b9a0257e6acff53ad22535cf2adf261313e0b250` (**≠ frozen `92abbcb9…`**) |
| 2 | `git status --porcelain` | 0 | *(empty)* — tree unmodified, campaign dir now committed |
| 3 | `rg -c -i "11493979" --glob '!.git' .` | 0 | `./research/.../W10b-older-literature-sweep.md:6` — only W10b's report |
| 4 | `rg -l -i "106689690000800209" --glob '!.git' .` | 0 | same single file |
| 5 | `rg -l -i "oshiro" research/ systems/ archive/` | 0 | `W10b-older-literature-sweep.md`, `research/modalities/geo-gse28866-brunner-series.json` (unrelated) |
| 6 | `rg -l -i -e "kyushu" -e "fukuoka" --glob '!.git' .` | 0 | `W10b-older-literature-sweep.md`, `research/modalities/emc_ret_cistrome.py` — **no clinical record names Kyushu** |
| 7 | `python3 /tmp/claude-0/w10c/enumerate.py` | **0** | 8 of 8 Asian keys resolved; 25 citation records total; rubric table reproduced in R2 |
| 8 | PubMed `get_article_metadata(["11493979","12599237","27418251"])` | ok | `count: 3`; Oshiro affiliation `"Department of Anatomic Pathology, Graduate School of Medical Science, Kyushu University."`; no `pmc` identifier |
| 9 | PubMed `get_full_text_article(["11493979"])` | ok (**wrong article**) | returned `PMC11493979 / PMID 39433838`, Sci Rep 2024 TMS study — **discarded** |

Verbatim output of command 7 (`EXIT=0`):

```
== retained Japanese/Asian EMC records in emc-clinical-registry.json ==
key                           n  period        pool   pmid      population
apatinib2020                 33  2009-2019     None   None      Unresectable chondrosarcoma (incl. 3 EMC), 2009-2019
china2016                    40  UNKNOWN       False  27402218  EMC, China
huang2023                    58  UNSTATED      None   36948401  58 molecularly confirmed EMC (fusion distribution)
japan2003                    42  UNKNOWN       False  12599237  EMC, 8 Japanese hospitals
jiang2026                     1  UNSTATED      None   None      Single patient, knee EMC with TAF15::NR4A3
masunaga2025                171  2002-2022     True   None      Pathologically diagnosed EMC, Japanese National Bone & Soft
morioka2016trabectedin        5  UNSTATED      None   27418251  subjects with EMCS OR mesenchymal chondrosarcoma allocated t
wang2026                      1  UNSTATED      None   None      Single adolescent patient, primary intracranial EMC

count of Asian/Japanese citation records found: 8 of 8 probed
total citation records in registry: 25

== Oshiro 2000 (PMID 11493979) vs each retained Asian series, W05 rubric ==
pair                        instDisj  accrDisj  idDisj   tier  verdict
masunaga2025                NO        UNDOC     UNDOC    C     UNKNOWN
japan2003                   UNDOC     UNDOC     UNDOC    C     UNKNOWN
morioka2016trabectedin      YES       UNDOC     UNDOC    C     UNKNOWN
china2016                   YES       UNDOC     UNDOC    C     UNKNOWN
huang2023                   YES       UNDOC     UNDOC    C     UNKNOWN

No pair reaches tier A or tier B. Tier C licenses nothing (falsifier only).
```

The script `/tmp/claude-0/w10c/enumerate.py`, returned inline for the coordinator, is reproduced in full in R1/R2's logic: it loads `research/data/emc-clinical-registry.json`, prints every Asian/Japanese citation record with `n`, `studyPeriod`, `pool` and PMID, then evaluates the three tier-B conditions per pair with `True/False/None` and maps `all three True → tier B`, otherwise `tier C`. The `None` entries are the undocumented conditions, and they are what produce every UNKNOWN.

**PROPOSED (NOT RUN).** Retrieving the Oshiro full text through the Actions runner to read its Materials & Methods for an accrual window and a per-case table. Not run: this is a SAGE subscription article with no PMC deposit, and I was not dispatched to spend a CI run on it.

## Limitations

- **Transfer limit.** W10b's finding that Oshiro is unretained and carries a survival cohort is transferred as established and re-verified, not re-derived. Its 5-year 73% / 10-year 63% figures remain **abstract-strength SECONDARY** and are not re-derived, not pooled, and not compared numerically to any retained series here.
- **The central verdict is UNKNOWN, and UNKNOWN is not a soft yes.** I did not show overlap. I showed that the evidence needed to exclude overlap does not exist in anything I can currently read. In a disease at roughly one case per million per year, where a university pathology department also serves as a regional consultation archive, that gap is not a formality.
- **Denominator gap, restated as a hard limit.** Oshiro's 36 have **not** been added to any pooled denominator, and under §2.3 they would not be even if the independence gate passed. No pooled figure in this repository changes because of this report.
- **No clinical claim.** Nothing here bears on prognosis, on rhabdoid features as a predictor, on efficacy, safety or clinical readiness. The rhabdoid subgroup result (3/36, p=0.0271) is recorded as what an abstract states and is not endorsed, re-analysed or extended.
- **Five of seven Asian series have no documented accrual window.** This is a property of the *retained records*, not necessarily of the papers; four of the seven are behind walls this program cannot pass (`japan2003`, `china2016`, `huang2023` graded `closed` or `free_to_read_but_not_retrieved` in `emc-km-reachability-census-2026-08-25.json`). The rubric cannot be satisfied for any of them without retrieval that has already failed.
- **A rubric observation I am flagging rather than acting on.** Tier B is conjunctive, so a pair with *genuinely* disjoint accrual windows but a shared institution scores tier C and licenses nothing — even though disjoint accrual alone physically excludes patient sharing when both series accrue on the same time axis. Oshiro vs `masunaga2025` is exactly that shape. **I did not relax the rubric to exploit this**, and I note that the escape hatch would not have applied anyway: Oshiro's own accrual window is undocumented, so the antecedent fails. This is a question for W05's owner, not a change I made.
- **HEAD is not the frozen commit** (see Worker). I read a later tree.

## Stop condition

**Set:** a per-pair independence verdict under W05's rubric with named missing evidence, plus an explicit IPD-admissibility verdict including "named but unusable" if that is the honest answer.

**MET.** R2 gives seven pairs, each with a tier, a verdict and specifically named missing evidence; R4 gives the IPD verdict as **named but unusable**, reached by applying `POLICY-evidence.md` §2.7(a)–(d) and W10b's gate as written rather than by inventing criteria; R5 records the unrecovered source honestly. The lane closes as W10b anticipated it might.

## Tool-call and wall-clock count actually used

**16 tool calls** (13 Bash, 2 PubMed MCP, 1 ToolSearch) against a ~40 target. **Wall clock ≈ 5 minutes** (`date -u` 02:11 → 02:16 UTC, first read to final check) against a ~40-minute target. No padding, no sleeping.

## Next concrete action

**One task, decisive rather than exploratory: retrieve Kawaguchi 2003's full text (PMID 12599237, [DOI](https://doi.org/10.1002/cncr.11162)) on a GitHub Actions runner and read its Methods for the enumeration of the eight affiliated hospitals.** That single list settles the highest-risk pair in R2 outright — if Kyushu University is among the eight, Oshiro vs `japan2003` becomes a live overlap concern at the institutional level and Oshiro's 36 are provisionally OVERLAPPING; if it is not, that pair gains one of tier B's three conditions in documented form. It is a bounded yes/no read of a Methods paragraph, at $0, with no new data and no biology.

Two things this successor is **not**: it is not a route to admitting Oshiro's n (R4's refusal is independent of R2 and stands whatever the eight hospitals turn out to be), and it is not a re-opening of the retrieval of Oshiro itself, which has no PMC deposit and stays an honest unrecovered source.

result: Oshiro 2000 (PMID 11493979, Kyushu University) fails both gates — under W05's rubric every pair against the seven retained Japanese/Asian EMC series scores tier C / UNKNOWN (no pair reaches A or B; five of seven retained series document no accrual window, Kawaguchi 2003's eight hospitals are unenumerated, and a national registry can never be institution-disjoint from Kyushu), and it is IPD-INADMISSIBLE as "named but unusable" under POLICY-evidence §2.7(a)/(d) since only aggregate percentages are retrievable and the paper has no PMC deposit; its 36 cases were added to no denominator, and a PubMed MCP defect was found that silently returns a different article when a PMID is passed to get_full_text_article.
