> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check complete: retained set independently rebuilt and reconciled exactly to W10's 5,882; both older-era queries covered end-to-end (286/286 and 98/98); the one candidate outcome cohort confirmed absent by independent PMID, DOI and author greps; tree unmodified; 27 GiB free.

---

# W10b — Saturation of the *older* EMC literature, and whether any unretained old paper carries an outcome cohort

## Worker

- Worker **W10b**, refill for Lane 10 (older-era half of the EMC clinical-evidence sweep).
- **Model identity: SELF-REPORT, not independently verified.** I report myself as Claude Opus 5 (`claude-opus-5`). I cannot observe the served model; the coordinator must extract the actual runtime model from the transcript.
- `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — **no environment variable names a model.** Identity-bearing lines, identical at start and end of run:

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

- `date -u` at start: `Tue Sep  8 02:02:32 UTC 2026`. At end: `Tue Sep  8 02:06:26 UTC 2026`.
- **Write isolation honoured.** I wrote nothing under `/home/user/Rare-cancers`. All execution was in `/tmp/claude-0/w10b/`. `git status --porcelain` at end shows only the pre-existing untracked `?? research/autonomy/opus-capacity-campaign-20260908/` — no file authored by me. No git write operation of any kind. Nothing downloaded; `df -h /` went 28 GiB → 27 GiB free (unrelated container churn, not my doing), well above the 10 GiB floor.

## Question

**Across the older EMC literature (publication date ≤ 2015) — the half the recency-sorted W10 sweep never reached — is the repository's bibliography as saturated as it is for recent work, and does any unretained older paper carry an EMC clinical outcomes cohort?**

Open because W10's own Limitation states it: its 84 records were drawn `sort=pub_date` from 601 available, so its 77.4% retention figure describes only recent literature. EMC's substantive outcome series are old, so the older literature is precisely where an unretained outcome cohort would sit. W10 could not answer this and said so.

**Both halves of the question are now answered, and they answer differently.** No — the older literature is *not* as saturated. And yes — **exactly one** unretained older paper carries a genuine EMC clinical outcomes cohort with survival data.

## Prior-work check

Commands run and what they showed:

1. Read `COMMON-BRIEF.md`, `CLOSED-WORK.md` and `reports/W10-new-clinical-evidence.md` in full before any other action.
2. Retained-set rebuild (W10's corrected command, verbatim as dispatched) — see Validation. My count and the reconciliation of it against W10's 5,882 are in R0.
3. Landmark-author retention probe: `rg -l -i "<author>" --glob '!.git' research/ systems/ archive/ | wc -l` → `Meis-Kindblom` 35 files, `Drilon` 46, `Antonescu` 24, `Stacchiotti` 105, `Ogura` 7, `Kawaguchi` 5, `Oliveira` 3. The landmark old-series authors are heavily represented in the corpus.
4. Novelty confirmation for my single positive hit: `rg -c -i "11493979"` → **no hits**; `rg -l -i "106689690000800209"` (its DOI) → **no hits**; `rg -l -i "oshiro"` → one file only, `research/modalities/geo-gse28866-brunner-series.json`, which is an unrelated GEO series record, not this paper. The hit is genuinely unretained under PMID *and* DOI *and* author.

**Closed items I confirm I am not replaying.** I made **no** request of any kind against Sunitinib 2014 (`24703573`), Wagner 2020 (`32856598`), CTARC 2022 (`35144048`), Trabectedin/RT 2018 (`10.4172/clinical-practice.1000433`), the pazopanib primary, or the anthracycline paper (`24345066`). `24703573` and `24345066` appear in my query-A result lists purely as PubMed record IDs and are both **RETAINED**; I fetched no metadata, no full text and no supplement for them, and I draw no inference beyond retained strength for any of them. I performed **no 2012 sunitinib substitution.** I did **not** retry W10's `EGRESS_BLOCKED` supplementary-data route — I issued no `curl`, no `WebFetch`, and no network request outside the PubMed MCP server. I did not touch the restricted NR4A Perspective, the registry ICD-O paper, or any lane-11 source-index material.

## Method / inputs

- Corpus: `/home/user/Rare-cancers` at frozen HEAD `92abbcb905cacf07f14b238db50d1b98f6590374` (verified by `git rev-parse HEAD`).
- Tools: ripgrep + GNU coreutils (`comm`, `sort`, `tr`, `grep`) under Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k`; PubMed MCP server (`search_articles`, `get_article_metadata`).
- **According to PubMed**, two older-era queries, both bounded in the query string (see the defect note below):
  - **Query A (broad):** `extraskeletal myxoid chondrosarcoma AND ("1950"[Date - Publication] : "2015"[Date - Publication])`, `sort=pub_date`. `total_count = 286`. Paginated `retstart` 0/100/200 → **286 of 286 retrieved (100%)**.
  - **Query B (outcome language):** `extraskeletal myxoid chondrosarcoma AND (survival OR outcome OR cohort OR series OR follow-up OR prognosis) AND ("1950"[Date - Publication] : "2015"[Date - Publication])`, `sort=pub_date`. `total_count = 98`. Single page → **98 of 98 retrieved (100%)**, `has_more: false`.
  - Query B is a strict subset of Query A: union = **286 unique PMIDs**.
- **Tool defect found and worked around (report this to the coordinator).** The MCP `date_to` parameter is **silently ignored**. My first call passed `date_to=2015` and PubMed returned 2026 records (`42660639`) with `total_count=469` — identical to W10's unfiltered total. The filter only takes effect when the range is written into the query string as `("1950"[Date - Publication] : "2015"[Date - Publication])`, which the returned `query_translation` then confirms as `AND 1950/01/01:2015/12/31[Date - Publication]`. **Any worker who trusted `date_to`/`date_from` got an unfiltered result set.** W10's Query A used `date_from=2022` and reported `total_count` 469 — the same unfiltered number — so W10's own date bound was probably also inert, and its 84 records should be read as "84 arbitrary records sorted by date", not "84 records from 2022 onward".

## Result

### R0 — Retained-set rebuild and exact reconciliation to 5,882 (PRIMARY)

| Variant of the retained-set build | Count |
|---|---|
| Dispatched command, verbatim, whole tree | **5,898** |
| Dispatched command, excluding the untracked campaign directory | **5,881** |
| Dispatched command + `--no-filename`, excluding campaign directory | **5,867** |
| W10's reported figure | 5,882 |

`PRIMARY`. **My number does not match 5,882, and the discrepancy is fully explained rather than waved off.**

Two independent defects sit in the dispatched pipeline, and I am reporting both:

1. **`rg -o` prefixes every match with its file path**, and `grep -oE '[0-9]{7,8}'` then harvests digits out of the *path* as if they were PMIDs. 14 of the 5,881 are path artefacts, not PMIDs: `00387752 1121610 20260905 2401803 31357997 3217966 32224299 34940552 3715775 47303771 47966625 48774033 5059912 7111761`. Adding `--no-filename` removes them → 5,867.
2. **Scope creep from the campaign directory itself.** The untracked `research/autonomy/opus-capacity-campaign-20260908/` now holds other workers' reports, injecting 17 further entries including the obvious junk `20260908`, `99900001`–`99900004` (placeholder IDs from another worker's report).

**Reconciliation with W10 is exact.** W10 ran the command when the campaign directory contained only the brief and `CLOSED-WORK.md`. All four PMIDs in those two files (`24345066 24703573 32856598 35144048`) are already retained elsewhere and add nothing — but the directory *path* `opus-capacity-campaign-20260908` contributes the artefact `20260908`. **5,881 real repository PMIDs + 1 path artefact = 5,882.** W10's number is reproduced precisely, and it contains one non-PMID.

For the classification below I deliberately use the **permissive** repo-only set (**5,881**, path-inclusive). A permissive retained set can only ever *understate* novelty, so every NEW call below is conservative.

### R1 — Older-era retention, against the recent-era baseline (PRIMARY)

| Era | Sweep | Records classified | RETAINED | NEW | Retention |
|---|---|---|---|---|---|
| Recent (W10, `sort=pub_date`, unbounded) | 84 of 601 | 84 | 65 | 19 | **77.4%** |
| **Older (≤2015, this worker)** | **286 of 286** | **286** | **112** | **174** | **39.2%** |

`PRIMARY` — exact set membership, not an estimate. Uncertainty: retention is measured **by PMID only**, so a source retained under DOI/PMCID without a PMID is misclassified NEW; 39.2% is therefore a **lower bound** on true older-era retention. The same bias applies to W10's 77.4%, so the *direction* of the comparison is robust even though both absolute numbers are floors.

**The bibliography is markedly less saturated for older work — roughly half the retention rate.** W10's saturation finding does not generalise backwards, and the premise behind this dispatch was correct.

### R2 — Coverage actually achieved (PRIMARY)

| Denominator | Covered | Fraction |
|---|---|---|
| Older-era broad query (≤2015) | 286 / 286 | **100%** |
| Older-era outcome-language query (≤2015) | 98 / 98 | **100%** |
| Older-era NEW items given individual metadata triage | 49 / 174 | **28.2%** |
| Whole EMC PubMed record set (`total_count` 469, broad query, unbounded) | 286 / 469 | 61.0% |

`PRIMARY`. The older era is swept **exhaustively at the record level**. The triage denominator is the honest limit: I retrieved metadata for the **49 NEW items that carry outcome language** (NEW ∩ Query B), and **125 NEW items with no outcome language were not individually triaged** — they are `UNKNOWN`, not "confirmed non-cohort". See Limitations for how much risk that leaves.

### R3 — The 49 outcome-language NEW items: cohort or case report? (SECONDARY, PubMed metadata)

**According to PubMed.** All 49 were retrieved and classified. **48 of 49 are case reports, differential-diagnosis/immunohistochemistry papers, reviews, or studies where EMC appears only as a comparator.** One is a genuine EMC outcomes cohort.

**The single positive — `PMID 11493979`, an EMC clinical outcomes cohort, unretained:**

| Field | Value |
|---|---|
| Citation | Oshiro Y, Shiratsuchi H, Tamiya S, Oda Y, Toyoshima S, Tsuneyoshi M. "Extraskeletal Myxoid Chondrosarcoma with Rhabdoid Features, with Special Reference to Its Aggressive Behavior." *Int J Surg Pathol* 2000;8(2):145–152 |
| DOI | [10.1177/106689690000800209](https://doi.org/10.1177/106689690000800209) |
| Cohort n | **36 EMC cases reviewed**; **26 with follow-up information** |
| Survival | **5-year survival 73%; 10-year survival 63%** |
| Subgroup result | 3/36 had rhabdoid features; those cases had significantly poorer prognosis, **p = 0.0271** |
| Retained? | **No** — absent by PMID, by DOI, and by author (R4) |

`SECONDARY` (abstract-level; I did not obtain the full text). This is a real EMC survival series with a stated n, a follow-up denominator, and 5- and 10-year survival figures.

**Two borderline items, correctly classified as NOT outcome cohorts:**

| PMID | Item | Why not a cohort |
|---|---|---|
| [10721413](https://doi.org/10.1097/00125480-200007020-00001) | Oliveira & Nascimento, *Adv Anat Pathol* 2000 — "Phenotypic plasticity and prognostic factors in EMC" | `article_types: ["Journal Article","Review"]`. A **review** summarising prognostic factors (older age, larger size, proximal location, metastasis as adverse predictors); it reports no n and no survival estimates of its own. Companion commentary to the Oliveira primary series, not the series. |
| [6402851](https://doi.org/10.1007/BF00666219) | Dardick 1983, *Virchows Arch A* — 12 chordoid sarcomas | A histological/ultrastructural characterisation series. n=12 but **no follow-up and no survival data**. Diagnostic, not outcome. |

**Representative sample of the 48 negatives** (all `Case Reports`, `Letter`, `Review`, or diagnostic studies; full list in Validation):

| PMID | Year | What it is | Cohort? |
|---|---|---|---|
| [10450885](https://doi.org/10.1007/s002560050531) | 1999 | Single-patient EMC of the knee, 64-month course | No — case report |
| [10748851](https://doi.org/10.1017/s0022215100145074) | 1999 | EMC of the external auditory meatus, 1 patient | No |
| [11259746](https://pubmed.ncbi.nlm.nih.gov/11259746/) | 2001 | EMC heart metastasis, 1 patient | No |
| [12754636](https://doi.org/10.1177/106689690301100215) | 2003 | Poorly differentiated EMC, 1 patient | No |
| [12820050](https://doi.org/10.1007/s007010300006) | 2003 | `article_types: ["Comment","Letter"]` on EMC prognosis | No |
| [17437101](https://doi.org/10.1007/s00256-007-0303-9) | 2007 | 4 patients, skeletal recurrence imaging | No — imaging series, no survival stats |
| [19542871](https://doi.org/10.1097/PAS.0b013e3181a8ffbe) | 2009 | 12 **urothelial** carcinomas mimicking EMC | No — EMC is a morphological comparator only |
| [2090579](https://pubmed.ncbi.nlm.nih.gov/2090579/) | 1990 | 3 EMC cases, Kidwai Institute | No — n=3, narrative follow-up, no survival estimate |
| [23599152](https://doi.org/10.1038/modpathol.2013.65) | 2013 | NY-ESO-1 IHC across 138 myxoid neoplasms (12 EMC) | No — diagnostic marker study |
| [24713246](https://pubmed.ncbi.nlm.nih.gov/24713246/) | 2014 | 5 EMC cases, clinicopathologic + IHC | No — no survival analysis |
| [25031013](https://doi.org/10.1007/s00428-014-1627-1) | 2014 | CD99/NKX2.2 for Ewing sarcoma; EMC a comparator | No |
| [7606973](https://doi.org/10.1378/chest.108.1.281) | 1995 | Interferon alfa-2b response, **1 patient** | No — single-patient response report |

`SECONDARY`. Note that `7606973` is a therapy-response report — but n=1, so it establishes nothing and is not a cohort.

### R4 — Landmark old-series retention probe (PRIMARY)

To test whether the low 39.2% older-era retention hides a gap in the *important* old literature specifically, I resolved every ≤2015 EMC paper by the four landmark-series author names and checked each against the retained set.

**According to PubMed**, `extraskeletal myxoid chondrosarcoma AND (Meis-Kindblom JM[Author] OR Oliveira AM[Author] OR Antonescu CR[Author] OR Drilon AD[Author]) AND ("1950":"2015"[Date - Publication])` → `total_count = 15`, all 15 retrieved.

| Result | PMIDs |
|---|---|
| **RETAINED (13/15)** | 24746215, 18951519, 12748252, 12598313, 11737310, 11156374, 11153986, 10955458, 10366145, 9844602, 9781944, 7635565, 7726361 |
| NEW (2/15) | 10721413 (review — R3), [14657948](https://doi.org/10.1038/modpathol.3800036) |

`14657948` = Aigner, Oliveira & Nascimento, *Mod Pathol* 2004, "Extraskeletal myxoid chondrosarcomas do not show a chondrocytic phenotype" — matrix-protein immunohistochemistry on 14 specimens. **No survival data. Not an outcome cohort.**

`PRIMARY`. **86.7% retention among landmark-author old papers, versus 39.2% across the older era as a whole.** The corpus has systematically retained the old literature that matters and systematically skipped the old case-report tail. The 39.2% is real but is concentrated in low-value material.

I did **not** assert any landmark PMID from memory. My first attempt guessed four PMIDs, all four failed the retained-set check, and rather than report them I discarded them and resolved the set through PubMed. Recalled identifiers are exactly the class of thing this repository forbids inventing.

### R5 — Verdict

**Is the older bibliography as saturated as the recent one?** **No.** 39.2% vs 77.4% by PMID. But the shortfall is in the case-report tail, not the evidence base: landmark-author old papers are 86.7% retained.

**Does any unretained older paper carry an EMC clinical outcomes cohort?** **Yes — exactly one, and only one, in the 49 items triaged.** Oshiro 2000 ([10.1177/106689690000800209](https://doi.org/10.1177/106689690000800209)), n=36 EMC / 26 with follow-up, 5-year survival 73%, 10-year 63%. Every other outcome-language NEW item in the older era is a case report, a diagnostic/IHC study, a review, or a paper in which EMC appears only as a differential-diagnosis comparator.

This is a **finding, not a null**: the dispatch's premise — that an unretained outcome cohort would be found in the old literature rather than the new — is confirmed, and the specific paper is named.

## Validation evidence

**RUN.** All in `/tmp/claude-0/w10b/`, container `container_0166QEHnXrRA8nCR59c9UG4k`, Linux 6.18.44-fc-v24, ripgrep + GNU coreutils, `bash`.

| # | Command | Exit | Verbatim key output |
|---|---|---|---|
| 1 | `git rev-parse HEAD` | 0 | `92abbcb905cacf07f14b238db50d1b98f6590374` |
| 2 | `rg -o -i --glob '!.git' -e '"pmid"…' -e 'PMID[: ]*…' -e 'pubmed…' research/ archive/ systems/ \| grep -oE '[0-9]{7,8}' \| sort -u \| wc -l` | 0 | `5898` |
| 3 | same, `--glob '!research/autonomy/opus-capacity-campaign-20260908/**'` | 0 | `5881` |
| 4 | same + `--no-filename` | 0 | `5867` |
| 5 | `comm -23 retained_excl.txt retained_clean.txt` | 0 | 14 path artefacts, listed in R0 |
| 6 | `comm -23 retained.txt retained_excl.txt` | 0 | `20260908 … 99900001 99900002 99900003 99900004` (17 campaign-dir entries) |
| 7 | `comm -12 union.txt retained_excl.txt \| wc -l` | 0 | `112` (RETAINED) |
| 8 | `comm -23 union.txt retained_excl.txt \| wc -l` | 0 | `174` (NEW) |
| 9 | `comm -12 new_hits.txt qB_s.txt \| wc -l` | 0 | `49` (NEW ∩ outcome language) |
| 10 | `comm -23 new_hits.txt qB_s.txt \| wc -l` | 0 | `125` (NEW, no outcome language — untriaged) |
| 11 | `rg -c -i "11493979" --glob '!.git' .` | 1 (no match) | *(empty)* |
| 12 | `rg -l -i "106689690000800209" --glob '!.git' .` | 1 (no match) | *(empty)* |
| 13 | `rg -l -i "oshiro" --glob '!.git' .` | 0 | `./research/modalities/geo-gse28866-brunner-series.json` (unrelated) |
| 14 | `git status --porcelain` | 0 | `?? research/autonomy/opus-capacity-campaign-20260908/` — **no file authored by me** |
| 15 | `df -h /` | 0 | `/dev/vda 252G 11G 27G 29% /` — ≥10 GiB floor held |

Set-arithmetic reproduction (the exact script run, so the coordinator can re-derive every count):

```bash
cd /tmp/claude-0/w10b
# retained set (dispatched command, repo-only, permissive/path-inclusive)
cd /home/user/Rare-cancers && rg -o -i --glob '!.git' \
  --glob '!research/autonomy/opus-capacity-campaign-20260908/**' \
  -e '"pmid"[[:space:]]*:[[:space:]]*"?[0-9]{7,8}' \
  -e 'PMID[: ]*[0-9]{7,8}' \
  -e 'pubmed[a-z./]*/[0-9]{7,8}' \
  research/ archive/ systems/ \
  | grep -oE '[0-9]{7,8}' | sort -u > /tmp/claude-0/w10b/retained_excl.txt
# sweep sets (qA.txt / qB.txt written from the PubMed pmids arrays)
cd /tmp/claude-0/w10b
tr ' ' '\n' < qA.txt | grep -E '^[0-9]+$' | sort -u > qA_s.txt   # 286
tr ' ' '\n' < qB.txt | grep -E '^[0-9]+$' | sort -u > qB_s.txt   # 98
cat qA_s.txt qB_s.txt | sort -u > union.txt                      # 286
comm -12 union.txt retained_excl.txt > retained_hits.txt         # 112
comm -23 union.txt retained_excl.txt > new_hits.txt              # 174
comm -12 new_hits.txt qB_s.txt      > new_outcome.txt            # 49  <- triaged
comm -23 new_hits.txt qB_s.txt      | wc -l                      # 125 <- UNKNOWN
```

**The 49 triaged outcome-language NEW PMIDs, in full** (all metadata retrieved; classifications in R3):
`10450885 10591950 10721413 10748851 10834009 11257623 11259746 11406651 11493979 11504379 11757867 12754636 12820050 12866586 12909830 12940774 16816935 17437101 18070452 18235511 18568733 19542871 20496272 2090579 21547635 21651669 21753718 22426765 22438126 22499307 2256420 22743288 22804337 22843913 23599152 24008882 24293381 24713246 24818862 25031013 25533917 25550031 25619049 26504046 273676 6402851 7606973 7924809 8249186`

MCP calls: `search_articles` ×5 (one of which exposed the `date_to` defect), `get_article_metadata` ×5. All returned successfully; `get_article_metadata` silently truncates a request to **20 articles** (a 25-PMID request returned `count: 20`), which I detected and compensated for by re-batching — no PMID was dropped.

**PROPOSED (NOT RUN):** retrieving the Oshiro 2000 full text to extract the per-patient rows behind the 73%/63% survival figures. Not attempted — it needs a publisher route, and W10's identical route is recorded as `EGRESS_BLOCKED` at this container's proxy. I did not replay it.

## Limitations

- **125 of 174 older-era NEW items were never individually triaged.** They are the NEW items carrying *none* of `survival|outcome|cohort|series|follow-up|prognosis` in PubMed-indexed text. This is a real denominator gap and it is `UNKNOWN`, not zero. The residual risk is low but non-zero: PubMed's translation of "series" and "follow-up" is broad, and an EMC survival series that used none of those six words anywhere in title, abstract or MeSH would be unusual. I did not verify that no such paper exists.
- **Retention measured by PMID only.** A source retained under DOI or PMCID with no PMID is counted NEW. 39.2% is a floor, and the true older-era retention is higher by an unmeasured amount. For the single positive hit I closed this gap specifically, by DOI and author grep (R4/Validation #11–13); I did not close it for the other 173.
- **The Oshiro 2000 finding is abstract-level (`SECONDARY`).** I did not read the full text. The n=36 / n=26-with-follow-up / 73% / 63% / p=0.0271 figures are quoted from the PubMed abstract as the authors state them. I have not verified the follow-up denominator, the censoring, the survival method, or whether "survival" means overall or disease-specific. **Nothing here may be entered into the clinical registry or any pinned quantity on this evidence alone.**
- **This is a retrieval census, not evidence.** No survival, response, fusion or outcome number in this report is new EMC evidence. Nothing establishes efficacy, safety, selectivity or clinical readiness for any therapy. There is no wet lab and no new patient data; finding a paper is not acquiring a cohort.
- **The dispatched retained-set command is defective in two ways** (R0) and its output should not be quoted as a PMID count without the `--no-filename` fix and a campaign-directory exclusion. I reproduced W10's 5,882 exactly, including its one non-PMID.
- **The MCP `date_to`/`date_from` parameters do not filter.** Any prior worker's date-bounded sweep in this campaign may silently be unbounded. This affects W10's stated Query A/B bounds.
- Two PMIDs W10 recorded as returning no record (`26389342`, `26389361`) appear in my Query A result list but carry no outcome language, so they fall in my untriaged 125. Still `UNKNOWN`.
- I did not attempt, and this report does not touch, any supplementary-file route, any denied route, or any of the six closed sources named in R3 of `CLOSED-WORK.md`.

## Stop condition

Set: *a bounded older-era RETAINED/NEW classification with the covered fraction stated, and an explicit verdict on whether any unretained older paper carries an EMC outcomes cohort.*

**Met, and stronger than bounded.** The older era was swept **exhaustively** — 286/286 and 98/98, not a sample — so the RETAINED/NEW classification (112/174) has no sampling gap at the record level. The covered fraction is stated at every level in R2, including the honest 49/174 triage fraction. The verdict is explicit and is **positive, not a saturation null**: the older bibliography is roughly half as saturated as the recent one (39.2% vs 77.4%), and one unretained older paper — Oshiro 2000, [10.1177/106689690000800209](https://doi.org/10.1177/106689690000800209) — does carry an EMC clinical outcomes cohort with n and survival data.

## Tool-call and wall-clock count actually used

**21 tool calls**; **3 min 54 s** wall clock (`02:02:32Z` → `02:06:26Z`). Well within the ~40-call / ~40-minute target.

## Next concrete action

**One task, for a worker with a network escape hatch (Actions runner):** retrieve the full text of **Oshiro 2000, `PMID 11493979`, [10.1177/106689690000800209](https://doi.org/10.1177/106689690000800209)**, *Int J Surg Pathol* 8(2):145–152, and determine (a) whether the 26 follow-up cases are reported as a per-patient table or only as aggregate 73%/63% survival, (b) whether overall or disease-specific survival is meant, and (c) whether the series overlaps the already-retained Japanese EMC series from the same Kyushu group — an overlap check is mandatory before this n is treated as independent patients, per the standing rule that arrays or specimens do not imply new patients. **Gate it honestly: if the paper reports only aggregate percentages with no risk table and no per-patient rows, it is not IPD-admissible, and this lane closes on a named-but-unusable source.** Note the route is not on any denied list, but it is a 2000 subscription journal, so a publisher 403 there would be an honest unrecovered source, not a hurdle to route around.

---

result: The older EMC literature (≤2015) is NOT as saturated as the recent — 39.2% retained (112/286, exhaustive sweep) vs W10's 77.4% recent — and exactly one unretained older paper carries a real EMC clinical outcomes cohort: Oshiro 2000 (PMID 11493979, DOI 10.1177/106689690000800209), n=36 EMC / 26 with follow-up, 5-yr survival 73%, 10-yr 63%, absent from the repo by PMID, DOI and author; W10's 5,882 retained-PMID figure reproduced exactly and shown to contain one path artefact, and the PubMed MCP `date_to` parameter found to silently not filter.
