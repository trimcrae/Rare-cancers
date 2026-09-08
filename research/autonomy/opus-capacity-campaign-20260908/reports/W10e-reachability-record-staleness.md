> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Start `date -u`: `Tue Sep  8 02:32:30 UTC 2026`. End `date -u`: `Tue Sep  8 02:34:38 UTC 2026`.

---

## Worker

- **W10e**, lane 10 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Read-only on the Git tree; nothing written into `/home/user/Rare-cancers`. Scratch under `/tmp/claude-0/w10e/` only.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model; the coordinator must extract the served model from the transcript.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — identity-bearing lines, identical at start and end (full start-of-run output was captured in tool call 1; the tail below is the filtered identity subset re-run at end, exit 0):

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

- **Actual HEAD read — and it moved under me.** `git rev-parse HEAD` at start: `47aac85f874a57a6f981c3432abcf16980968aec`. At end: `7d081218f107363573573e6d102e4334567adf77`. This is **not** the `92abbcb905cacf07f14b238db50d1b98f6590374` named in COMMON-BRIEF §1; the coordinator is committing to the shared checkout during the campaign. `git status --porcelain` was empty (0 lines) at both start and end, so I introduced no modification. Every literature artifact I read has mtime `Sep 4 12:16` and its last touching commit is `14a3f172d6b494d872f6d2678c7d0caa7ef26ccc` (2026-09-04), so the content I audited is stable across that HEAD move.
- I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/`; the question is entirely about live-checkout artifacts and the live checkout is authoritative for them.

## Question

**How much of this repository's EMC literature reachability record is stale, and where does it disagree with itself?** Specifically: a per-source route-outcome inventory over `emc-km-reachability-census-2026-08-25.json`, `emc-km-admissibility-2026-08-27.json` and siblings; every place a retrieval outcome and an OA/licence flag disagree; and every route recorded denied in one of {census/admissibility, `CLOSED-WORK.md`} but absent from the other.

It is open because W10d closed the *retrieval* axis for this lane (Kawaguchi 2003 has no PMC deposit; its publisher route is already recorded denied at HTTP 403) and concluded the lane had no successor on that axis. The audit axis needs no retrieval at all and had not been done.

**I issued no publisher request, no retrieval, and no network call of any kind — not even PubMed MCP.** No route recorded denied was replayed. No case was added to any denominator and no source's verdict was changed; §2.7 of `systems/POLICY-evidence.md` was read before any admissibility statement, and every admissibility verdict below is quoted from the artifact, not re-derived.

## Prior-work check

- `ls /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports | grep -i w10` → `W10-new-clinical-evidence.md`, `W10b-older-literature-sweep.md`, `W10c-oshiro-overlap-admissibility.md`. **`W10d-*.md` does not exist on disk** (exit 0, no match). W10d's findings reached me only through the dispatch prompt; I treated its two conclusions (no PMC deposit for Kawaguchi; publisher route already recorded denied 403) as transferred fact and did not re-verify them by retrieval.
- Read W10b in full (51 KB, persisted) and W10c. Read `CLOSED-WORK.md` and `CORPUS-CONTEXT.md` in full.
- `git ls-files | grep -iE 'reachab|admissib'` → 11 paths; the EMC-literature siblings are exactly `emc-ipd-admissibility-2026-08-12.json`, `emc-km-admissibility-2026-08-27.json`, `emc-km-reachability-census-2026-08-25.json`, `emc-trial-reachability-adjudication-2026-08-09.json`, plus the generators `scripts/emc_km_admissibility.py` and `scripts/emc_km_reachability_census.py`. I also read `emc-km-figure-retrieval-2026-08-25.json` (not matched by that pattern but a route-outcome record). `emc-trial-reachability-adjudication-2026-08-09.json` is a ClinicalTrials.gov registry adjudication, not a literature-route record — it recorded 4/4 HTTP 200 and is out of scope here.
- Confirmed I am not replaying: PUB-EMC-CLASSIFICATION (user-rejected), any Brenca route, Kawaguchi, Oshiro, the NR4A Perspective refusal.

## Method / inputs

Read-only `python3`/`grep`/`sed` over the live checkout:

- `research/literature/emc-km-reachability-census-2026-08-25.json` (16 series, 4 rounds)
- `research/literature/emc-km-admissibility-2026-08-27.json` (16 series, round `km-figures-round5-2026-08-27`)
- `research/literature/emc-km-figure-retrieval-2026-08-25.json` (7 targets)
- `research/literature/emc-ipd-admissibility-2026-08-12.json` (7 papers + `step_1b` route probe)
- `scripts/emc_km_reachability_census.py` lines 74–100 (verdict derivation)
- `systems/POLICY-evidence.md` §2.7 (read before any admissibility statement)
- `research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md`

## Result

### 1. Per-source route-outcome inventory — all 16 series

Both artifacts cover the **same 16 source_ids**. Verdict vocabularies differ between them (see §1b). "Date" is **inferred from the round slug / filename**: **no per-route timestamp exists anywhere in these artifacts** — this is itself a record defect (Limitations).

| # | source_id | ids | census verdict | admissibility verdict | route(s) attempted → HTTP (bytes, content-type) | attempt date | tier |
|---|---|---|---|---|---|---|---|
| 1 | `stacchiotti2013anthracycline` | PMID 24345066 / PMC3879193 | retrieved | **admitted** | `europepmc_pdf_render` → **200** (2,609,773, application/pdf) | 2026-08-25 | PRIMARY |
| 2 | `morioka2016trabectedin` | PMID 27418251 / PMC4946242 | retrieved | **admitted** | `europepmc_pdf_render` → **200** (811,863, pdf) | 2026-08-25 | PRIMARY |
| 3 | `masunaga2025` | PMC12398172 | retrieved | refused_no_risk_row | `europepmc_pdf_render` → **200** (1,763,019, pdf) | 2026-08-25 | PRIMARY |
| 4 | `chiusole2020` | PMID 32612944 / PMC7308468 | retrieved | refused_no_risk_row | `europepmc_pdf_render` → **200** (439,160, pdf) | 2026-08-25 | PRIMARY |
| 5 | `martinbroto2020immunosarc1` | PMID 33203665 / PMC7674086 | retrieved | refused_no_risk_row | `europepmc_pdf_render` → **200** (529,371, pdf) | 2026-08-25 | PRIMARY |
| 6 | `drilon2008` | PMID 18951519 / PMC2779719 / 10.1002/cncr.23978 | unresolved | unreachable | `europepmc_pdf_render` → **500** (57, json); `pmc_direct_pdf` → **200** (1,817, **text/html**); `pmc_legacy_pdf` → **200** (1,817, text/html); `caller_pdf_url` (Wiley) → **403** (2,000, text/html) | 500 at 2026-08-25; all four at 2026-08-27. Earlier: **404** on Europe PMC fullTextXML at 2026-08-12 (chars=196) | PRIMARY |
| 7 | `bishop2019` | PMID 31436747 / PMC7771031 / 10.1097/coc.0000000000000590 | unresolved | unreachable | `europepmc_pdf_render` → **500** (57, json); `pmc_direct_pdf` → **200** (1,817, text/html); `pmc_legacy_pdf` → **200** (1,816, text/html); `caller_pdf_url` → **200** (**168,147**, text/html) | as above; **404** at 2026-08-12 | PRIMARY |
| 8 | `japan2003` (= Kawaguchi 2003) | PMID 12599237 / 10.1002/cncr.11162 | free_to_read_but_not_retrieved | unreachable | `caller_pdf_url` (Wiley pdfdirect) → **403** (2,000, text/html); browser retry → **403** (5,808, text/html) | 2026-08-25 (r3, r4-browser); 2026-08-27 (r5) | PRIMARY |
| 9 | `huang2023` | PMID 36948401 / 10.1016/j.modpat.2023.100161 | free_to_read_but_not_retrieved | unreachable | `caller_pdf_url` (modernpathology.org) → **403** (2,000); browser retry → **403** (5,799) | same | PRIMARY |
| 10 | `seer270_2022` (= CTARC 2022) | PMID 35144048 / 10.1016/j.ctarc.2022.100530 | free_to_read_but_not_retrieved | unreachable | `caller_pdf_url` (ScienceDirect) → **403** (2,000); browser retry → **403** (831,865, text/html) | same | PRIMARY |
| 11 | `china2016` | PMID 27402218 / 10.1016/j.anndiagpath.2016.04.004 | closed | unreachable | **`routes: []` — no HTTP attempt recorded in either artifact** | n/a | UNKNOWN |
| 12 | `meisKindblom1999` | PMID 10366145 / 10.1097/00000478-199906000-00002 | closed | unreachable | **`routes: []`** | n/a | UNKNOWN |
| 13 | `stacchiotti2014sunitinib` | PMID 24703573 / 10.1016/j.ejca.2014.03.013 | closed | unreachable | **`routes: []`** | n/a | UNKNOWN |
| 14 | `stacchiotti2019pazopanib` | PMID 31331701 / 10.1016/S1470-2045(19)30319-5 | closed | unreachable | **`routes: []`** | n/a | UNKNOWN |
| 15 | `uMich2023` | PMID 36825763 / 10.1097/coc.0000000000000988 | closed | unreachable | **`routes: []`** | n/a | UNKNOWN |
| 16 | `ussc2022` | PMID 35962783 / 10.1002/jso.27062 | closed | unreachable | **`routes: []`** | n/a | UNKNOWN |

Tallies reconcile: census `{retrieved 5, unresolved 2, free_to_read_but_not_retrieved 3, closed 6}` = 16; admissibility `{admitted 2, refused_no_risk_row 3, unreachable 11}` = 16. The 5 retrieved split cleanly into 2 admitted + 3 refused. **No arithmetic disagreement between the two artifacts.**

**Staleness, measured.** Every recorded route outcome dates to 2026-08-12, 2026-08-25 or 2026-08-27 — **12 to 27 days before today (2026-09-08)**. No artifact in this family carries an outcome newer than 2026-08-27. But the dominant staleness fact is not age: **6 of 16 sources (37.5%) carry a denial-shaped verdict with zero recorded HTTP attempts at any date.** Those are not stale, they are *unattempted*, and the record does not distinguish the two states in its verdict vocabulary.

### 1b. Verdict-vocabulary disagreement between the two artifacts (label-level, not substantive)

The same source carries different verdict words in the two files: `closed`/`unresolved`/`free_to_read_but_not_retrieved` (census) all collapse to `unreachable` (admissibility). The admissibility `why` string is identical for all 11 — *"no free route returned the article today, so its figures have not been LOOKED at: the risk-row question is unasked, not answered no"* — which is honest, but it **erases the census's own three-way distinction between a source that was refused 403, a source that returned 500, and a source that was never requested at all.** A reader of the admissibility file alone cannot tell #11–#16 (never attempted) from #8–#10 (attempted and refused).

### 2. Internal disagreements: OA/licence flag versus recorded retrieval outcome

**An OA flag is a claim by a metadata aggregator (Unpaywall / OpenAlex / DOAJ), not an access grant.** It describes what an indexer believes about a licence; it confers no permission and predicts nothing about whether a request will be served. **None of the rows below is licence to retry any route, and I recommend no retry.** W10d surfaced one such case; the record contains **five**, plus two deeper structural contradictions.

| source_id | aggregator OA claim | OA location(s) the aggregator names | Recorded outcome on that same URL | Disagreement |
|---|---|---|---|---|
| `japan2003` (Kawaguchi 2003) | Unpaywall `is_oa: true`, `oa_status: "bronze"`, 1 location; OpenAlex `license: null` | `https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/cncr.11162` (publisher, publishedVersion) | **403**, then browser **403** | **The W10d case.** The single claimed OA location is the exact URL that 403s. |
| `huang2023` | Unpaywall `is_oa: true`, `bronze`, 1 location; OpenAlex `license: null` | `http://www.modernpathology.org/article/S0893395223000662/pdf` (publisher, publishedVersion) | **403**, then browser **403** | Identical shape to Kawaguchi. Not previously named. |
| `seer270_2022` | Unpaywall `is_oa: true`, **`gold`**, `cc-by-nc-nd`, 2 locations; OpenAlex names `cc-by-nc-nd` (ScienceDirect) and **`cc-by-sa`** (DOAJ) | (a) ScienceDirect `.../S2468294222000211/pdf`; (b) `https://doaj.org/article/90d8691f…` (repository, **submittedVersion**) | (a) **403**, browser **403** (831,865-byte HTML error body). (b) **no route outcome recorded at all** | A *gold*, explicitly-licensed article that is not served. Also two aggregators assert **different licences for the same article** (`cc-by-nc-nd` vs `cc-by-sa`) — an internal licence disagreement in its own right, and material because the census separately notes the CC BY-NC-ND licence rule blocks committing this one anyway. |
| `drilon2008` | Unpaywall `is_oa: true`, `bronze`, 2 locations | (a) Wiley `pdfdirect/10.1002/cncr.23978`; (b) **PMC 2779719** (repository, submittedVersion, NIH) | (a) **403**. (b) `europepmc_pdf_render` **500**; `pmc_direct_pdf` **200 / 1,817 bytes / text/html**; `pmc_legacy_pdf` **200 / 1,817 / text/html** | Kawaguchi's shape *plus* a claimed **PMC** OA location that the record elsewhere calls not-open-access (see below). |
| `bishop2019` | Unpaywall `is_oa: true`, **`green`**, 1 location | **PMC 7771031 only** (repository, submittedVersion, NIH) | `europepmc_pdf_render` **500**; `pmc_direct_pdf` **200 / 1,817 / text/html**; `pmc_legacy_pdf` **200 / 1,816 / text/html**; `caller_pdf_url` **200 / 168,147 / text/html** | **The sharpest disagreement in the record.** "Green OA" means *deposited in a repository*; the sole named repository is the one every route to it failed on. And the `caller_pdf_url` row is a **200 with a 168 KB body** sitting under a verdict that reads *"no free route returned the article today."* |

**Two structural contradictions behind those rows**

**(A) The `idIsNotOpenAccess` claim is not corroborated by the file that is supposed to corroborate it.** `emc-ipd-admissibility-2026-08-12.json` states as a "definitively closed" finding: *"drilon2008 (PMC2779719) and bishop2019 (PMC7771031) both return error code 'idIsNotOpenAccess' from the OA service … these papers are not open access, and no open route will reach them."* But `emc-km-figure-retrieval-2026-08-25.json` records the PMC OA service (`oa.fcgi`) result for **all seven** of its targets, and every one is identical: `http: 404, error_code: null, license: null` — **including the five papers that were successfully retrieved as PDFs in the same run.** So in the 2026-08-25 record the `oa.fcgi` signal is **non-discriminating** and does not distinguish a reachable paper from an unreachable one. The 2026-08-25 file nonetheless writes that the 500s are *"consistent with the 2026-08-12 finding that the OA service reports them as not open access"* — an inference its own adjacent field does not support. Separately, the same two papers' Europe PMC status **changed from 404 (2026-08-12) to 500 (2026-08-25, 2026-08-27)**, so the word "definitively" rests on a status code that has already moved once.

**(B) A recorded HTTP 200 in this family does not mean the article was obtained.** This is a *consistency* worth stating because it constrains how row `bishop2019` must be read. The 2026-08-12 `step_1b` probe records `pmc.ncbi.nlm.nih.gov/…/bin/<figure>.jpg` returning *"HTTP 200 but content-type text/html — a reCAPTCHA interstitial"*, and explicitly credits the content-type guard for keeping the refusal legible. The 1,817-byte `text/html` 200s for drilon2008/bishop2019 have exactly that shape. **I am not re-adjudicating bishop2019's 200/168,147-byte response and it does not change any verdict** — I am recording that the artifact stores a bare status code with no classification field distinguishing "served the article" from "served a wall at 200", and that this is why a 200 and an `unreachable` verdict can coexist without either being a lie.

**(C) The census derives "closed" from an aggregator flag alone.** `scripts/emc_km_reachability_census.py` lines 81–95, verbatim:

```python
    # the verdict per source is the BEST outcome any round reached
    for sid, row in by_source.items():
        got = [r for r in row["rounds"] if r["route_used"]]
        oa = [r for r in row["rounds"] if r["unpaywall_is_oa"] is True]
        closed = [r for r in row["rounds"] if r["unpaywall_is_oa"] is False]
        if got:
            row["verdict"] = "retrieved"
        elif oa:
            row["verdict"] = "free_to_read_but_not_retrieved"
            row["⚠"] = ("Unpaywall grades it open access and every route this program tried was "
                        "refused by the publisher. That is a retrieval problem, not a licence one.")
        elif closed:
            row["verdict"] = "closed"
        else:
            row["verdict"] = "unresolved"
```

The record is **asymmetric about the aggregator**: when Unpaywall says *open*, the census correctly refuses to believe it and files the source as `free_to_read_but_not_retrieved` with an explicit warning. When Unpaywall says *closed*, the census believes it outright and stops — assigning `closed` to sources #11–#16 **with no request ever issued**. The same epistemic caution is applied in one direction and not the other. Stating this is not a recommendation to attempt those six: an aggregator's "closed" is weak evidence, but weak evidence of denial is not evidence of permission, and the correct label for those six is **UNKNOWN**, which is how I have marked them above.

### 3. Routes recorded in one place and not the other (census/admissibility ↔ `CLOSED-WORK.md`)

**Named in `CLOSED-WORK.md` as denied/unrecovered, but the route is ABSENT from the census and admissibility artifacts:**

1. **Sunitinib 2014 — `stacchiotti2014sunitinib`, PMID 24703573, DOI 10.1016/j.ejca.2014.03.013. The most dangerous gap.** `CLOSED-WORK.md` states *"unrecovered; three ordinary institutional 403 routes exhausted."* Both artifacts record **`routes: []`** for this source. **Three denied 403 routes exist in the campaign record and appear nowhere in the machine-readable reachability record.** A worker reading only the census sees a source that has never been requested.
2. **Wagner 2020 — PMID 32856598, DOI 10.1158/1055-9965.EPI-20-0447.** `CLOSED-WORK.md`: methods unresolved, ordinary route historically `EGRESS_BLOCKED`. `grep 32856598 research/literature/emc-km-*.json research/literature/emc-ipd-*.json` → **no match.** The source is not a census candidate at all, so its blocked route is recorded only in prose.
3. **Trabectedin/RT 2018 — DOI 10.4172/clinical-practice.1000433.** `CLOSED-WORK.md`: known-unverified PDF, historical `EGRESS_BLOCKED` (explicitly *not* a publisher-authentication denial). `grep` → **no match** in either artifact.
4. **Pazopanib supporting records — EudraCT `2013-005456-15` and the unread mortality erratum.** `grep 2013-005456-15` → **no match.** `stacchiotti2019pazopanib` is in the census but as a `routes: []` / flag-only `closed`; the EudraCT and erratum routes named in `CLOSED-WORK.md` have no representation.

**Recorded denied in the census/admissibility artifacts, but ABSENT from `CLOSED-WORK.md`:**

5. **`drilon2008`** (PMID 18951519 / PMC2779719) — a 500, two 200-HTML stubs and a Wiley 403. Not named anywhere in `CLOSED-WORK.md`.
6. **`bishop2019`** (PMID 31436747 / PMC7771031) — a 500, two 200-HTML stubs and a 200-HTML `caller_pdf_url`. Not named.
7. **`japan2003` / Kawaguchi 2003** (PMID 12599237) — Wiley 403 + browser 403. **Not named in `CLOSED-WORK.md`**, which is precisely why W10c/W10d had to rediscover it as an open question. This is the bookkeeping gap that already cost this lane a worker-cycle.
8. **`huang2023`** (PMID 36948401) — modernpathology.org 403 + browser 403. Not named.
9. **`china2016`, `meisKindblom1999`, `uMich2023`, `ussc2022`** — flag-only `closed`, no attempt, no mention in `CLOSED-WORK.md`. Absent from both in the sense that matters: neither document records a route for them.

**Agreeing in both (the clean match):** `seer270_2022` = CTARC 2022, PMID 35144048. `CLOSED-WORK.md`: *"abstract retained; latest publisher 403, methods unrecovered."* Census/admissibility: `caller_pdf_url` 403, browser 403. **Consistent.** This is the only source of the 16 whose denial is correctly recorded in both places.

**One framing tension, flagged not resolved:** `CLOSED-WORK.md` lists the **anthracycline** paper (`PMC3879193` / PMID 24345066) under *"Unrecovered / partially retained sources — retained only median 4 cycles…"*, while both artifacts record it as **retrieved at HTTP 200 (2.6 MB PDF)** and the admissibility file **admits** it under §2.7(a) with a digitized numbers-at-risk row. These are probably compatible — `CLOSED-WORK.md` is constraining which *quantities* were extracted (chemotherapy cycles), not asserting the PDF was never obtained — but a reader scanning the "unrecovered" heading would draw the wrong conclusion about retrieval state. I make no change to either record.

### Answer to the headline question

The record is **not** internally consistent apart from the one W10d found. It contains **five** OA-flag-versus-outcome disagreements (not one), **two** structural contradictions about the PMC OA service and about what an HTTP 200 means, an **asymmetric treatment of the aggregator** that assigns denial verdicts to 6/16 sources on no attempt at all, and **nine** routes recorded in exactly one of the two bookkeeping locations. Nothing here changes any source's verdict, and nothing here licenses a retry.

## Validation evidence

All **RUN**, all read-only, all in the live checkout. Nothing `PROPOSED (NOT RUN)`; nothing skipped.

- Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Claude Code 2.1.42, `python3` (stdlib `json` only), GNU coreutils/grep/sed. No network egress attempted at any point.
- `date -u` start `Tue Sep  8 02:32:30 UTC 2026`, end `Tue Sep  8 02:34:38 UTC 2026`, both exit 0.
- `git rev-parse HEAD` → `47aac85f874a57a6f981c3432abcf16980968aec` (start) / `7d081218f107363573573e6d102e4334567adf77` (end); `git status --porcelain | wc -l` → `0` at both, exit 0.
- `ls .../reports | grep -i w10` → three files, **no `W10d-*`**, exit 0.
- `git ls-files | grep -iE 'reachab|admissib'` → 11 paths (listed in Prior-work check), exit 0.
- `grep -l` for `32856598`, `10.4172/clinical-practice.1000433`, `2013-005456-15` across `research/literature/emc-km-*.json research/literature/emc-ipd-*.json` → **no match** for all three; `24703573`, `31331701`, `35144048` → matched **only** `emc-km-admissibility-2026-08-27.json`. Verbatim:

```
== 32856598
  (absent from emc-km-*/emc-ipd-* artifacts)
== 10.4172/clinical-practice.1000433
  (absent from emc-km-*/emc-ipd-* artifacts)
== 24703573
research/literature/emc-km-admissibility-2026-08-27.json
== 31331701
research/literature/emc-km-admissibility-2026-08-27.json
== 35144048
research/literature/emc-km-admissibility-2026-08-27.json
== 2013-005456-15
  (absent from emc-km-*/emc-ipd-* artifacts)
```

- Key verbatim output supporting the `oa.fcgi` contradiction (from `emc-km-figure-retrieval-2026-08-25.json`, one line per target, all seven identical in the fields that matter):

```
### masunaga2025 PMC12398172 route_used= europepmc_pdf_render
  oa_service: {"lookup_url": "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC12398172", "http": 404, ..., "error_code": null, "license": null}
### drilon2008 PMC2779719 route_used= None
  oa_service: {"lookup_url": "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC2779719", "http": 404, ..., "error_code": null, "license": null}
### bishop2019 PMC7771031 route_used= None
  oa_service: {"lookup_url": "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC7771031", "http": 404, ..., "error_code": null, "license": null}
```

- Verbatim `bishop2019` retrieval block from `emc-km-admissibility-2026-08-27.json` (the 200-under-`unreachable` row):

```
"routes": [
 {"route": "europepmc_pdf_render", "http": 500, "bytes": 57, "content_type": "application/json;charset=UTF-8", "browser_http": 500},
 {"route": "pmc_direct_pdf",       "http": 200, "bytes": 1817, "content_type": "text/html; charset=utf-8", "browser_http": 200},
 {"route": "pmc_legacy_pdf",       "http": 200, "bytes": 1816, "content_type": "text/html; charset=utf-8", "browser_http": 200},
 {"route": "caller_pdf_url",       "http": 200, "bytes": 168147, "content_type": "text/html; charset=utf-8", "browser_http": 200}],
"unpaywall": {"is_oa": true, "oa_status": "green", "n_oa_locations": 1}
```

- `scripts/emc_km_reachability_census.py` lines 74–100 quoted verbatim in Result §2(C), exit 0.
- `systems/POLICY-evidence.md` §2.7 read in full (lines 242–275) before any admissibility statement; §2.7(a) mandates the numbers-at-risk table and refuses a curve without one *"not admitted with a caveat"*. I applied no §2.7 test and changed no §2.7 outcome.

## Limitations

- **This is an audit of a record, not a re-adjudication.** Every verdict, every UNKNOWN and every unrecovered-source status stands exactly as I found it. I added nothing to any denominator. The 2 admitted / 3 refused / 11 unreachable split is unchanged.
- **No per-route timestamp exists.** Every date in the inventory is inferred from a round slug or a filename. If a round's slug date differs from its actual execution date, my dates are wrong by that amount. This is a genuine defect in the artifacts, and it means "staleness" cannot be measured to better than round granularity.
- **A bare HTTP status is all the record stores.** There is no field saying whether a 200 delivered the article or a wall. I therefore cannot tell from the record whether `bishop2019`'s 168 KB `text/html` 200 is a landing page, a paywall, or something else — and I did not fetch it to find out. It stays UNKNOWN.
- **"Absent from `CLOSED-WORK.md`" is a statement about that one file at this HEAD**, not about the whole repository. Some of these routes may be recorded in cycle outcomes, receipts, the literature-cache branch (which the census itself flags as *"a working cache rather than repository state"*), or the frozen corpus. Absence here is a bookkeeping observation, **not proof the route is undocumented anywhere.**
- **I did not read the frozen corpus**, so a locally-absent prior record of these routes remains UNKNOWN in exactly the sense `CORPUS-CONTEXT.md` warns about.
- **HEAD moved during the run** (`47aac85f` → `7d081218`). The four artifacts I audited were last touched at `14a3f172` (2026-09-04) and are unaffected, but a coordinator commit landing after my reads could in principle alter them.
- **No clinical claim of any kind.** Reachability is a statement about this program's $0 routes on specific dates. It says nothing about what any paper prints, about any patient, or about efficacy, safety or selectivity. The three retrieval-side disagreements above are metadata disagreements, not scientific ones.
- **W10d's report file does not exist on disk**, so its findings are transferred through the dispatch prompt only and I could not verify its method.

## Stop condition

Set: (i) a per-source route-outcome inventory, (ii) a table of internal OA-versus-outcome disagreements, (iii) a named list of routes recorded in one place and not the other. **All three MET.** All 16 sources inventoried with route, status, bytes, content-type and inferred date; five OA-versus-outcome disagreements tabulated plus three structural contradictions; nine one-sided route records named across both directions. Returning now.

## Tool-call and wall-clock count actually used

**20 tool calls** (all `Bash`; no MCP, no network, no `Read`/`Write`/`Edit` on the tree). **Wall clock 02:32:30Z → 02:34:38Z**, a measured span of **2 min 08 s** of tool time within the turn. Well inside the ~40-call / ~40-minute target.

## Next concrete action

**One specific successor, and it is a coordinator-owned bookkeeping repair, not research:** add the four `CLOSED-WORK.md`-only routes (Sunitinib 2014's three institutional 403s; Wagner 2020's `EGRESS_BLOCKED`; Trabectedin/RT 2018's `EGRESS_BLOCKED`; the pazopanib EudraCT/erratum) into the machine-readable reachability record as explicit denied-route entries with their dates, and add the five artifact-only denials (`drilon2008`, `bishop2019`, `japan2003`, `huang2023`, and the four flag-only `closed` sources) to `CLOSED-WORK.md`. Concretely this needs two schema fields the artifacts currently lack: a **`attempted: false`** marker so a flag-derived `closed` can never again be mistaken for an exhausted route, and a **per-route timestamp**. This is a **write** to shared coordination state and to `research/literature/`, so it is **not mine to make** — W10e is read-only, and I am handing it to the coordinator as a diagnosis with a named smallest repair.

**For lane 10 itself: no viable successor**, and this audit confirms rather than reopens W10d's conclusion. The retrieval axis is terminal on permitted routes; the audit axis is now complete; and the one thing this audit surfaced that *looks* like an opening — five sources with `is_oa: true` sitting on denied routes, and six sources never requested — is explicitly **not** one. An aggregator's OA flag is not an access grant, an aggregator's "closed" is not a completed attempt, and neither is a reason to issue a request. Any decision to pursue `drilon2008`, `bishop2019` or the six unattempted sources through a subscription or interlibrary route is trimcrae's, exactly as the 2026-08-12 record already says.
