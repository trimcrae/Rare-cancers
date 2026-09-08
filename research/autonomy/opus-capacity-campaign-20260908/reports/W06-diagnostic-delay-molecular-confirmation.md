> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Sanity check: exit 0, and the two reconstructed sums verify against their sources (Agaram 16+7+1+2 = 26; Taiwan 46+9+2+1 = 58). Repo tree confirmed free of my writes. Full report below.

---

## Worker

- **Worker ID:** W06 — Lane 6 (EMC diagnostic delay, referral pathway, molecular confirmation)
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. I did not observe the served model and do not assert it as fact; the coordinator should extract the actual runtime model from the transcript.
- **Write-isolation correction complied with.** Before the correction I had created `research/autonomy/opus-capacity-campaign-20260908/code/W06/emc_molecular_confirmation.py` inside the repo. I copied it to `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/`, then `rm -rf`'d the repo directory. Verified: `find research/autonomy/opus-capacity-campaign-20260908 -name '*W06*' -o -name 'W06'` returned nothing. `git status --porcelain` shows only `?? research/autonomy/opus-capacity-campaign-20260908/` — the coordinator's own untracked campaign directory, not my file. I wrote nothing else in the tree and ran no git write operation.
- **`date -u` at start:** not captured — I began before the corrected brief required it. Honest gap; not reconstructed. **`date -u` at re-run start:** `Tue Sep  8 01:54:30 UTC 2026`. **`date -u` at end:** `Tue Sep  8 01:54:31 UTC 2026` (the analysis itself runs in under a second).
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** — literal output (abridged only by removing the long `no_proxy`/`JAVA_TOOL_OPTIONS` lines, which contain no model information; all model-relevant lines retained verbatim):

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

**No environment variable in this container names a model.** That is itself the finding on model evidence: my identity claim rests solely on my system prompt.

---

## Question

**What fraction of published EMC cases had their diagnosis confirmed molecularly (NR4A3 rearrangement by FISH / RT-PCR / sequencing) versus morphology alone, how has that changed by publication era, and what is the actual reporting denominator in each source?**

It is open because the repository has never assembled this table. It has extracted molecular-confirmation facts *per paper* where a specific downstream analysis needed one (partner pooling, ASO coverage, systemic-therapy pooling), but never asked the cross-series question of *how much of the published EMC record is molecularly confirmed at all*. That matters because every survival and treatment estimate in this program is pooled over series whose diagnostic standards differ, and a morphology-only series can contain misclassified myxoid tumours.

---

## Prior-work check

Commands actually run, in `/home/user/Rare-cancers`:

1. `rg -n -i "molecular confirm|FISH|RT-PCR|NR4A3 rearrang|diagnostic delay|referral|misdiagn" research/ --glob '!.git' | head -80`
2. `ls research/manuscripts/care-delivery/`
3. `git ls-files | rg -i "care-delivery|diagnos|confirm" | head -40`
4. `sed -n '420,530p;820,870p' research/manuscripts/aso_coverage_ladder.py`
5. `sed -n '230,270p;540,620p' research/manuscripts/emc_systemic_therapy_pooling.py`
6. A Python dump of every `label/design/population/year/pmid/doi/n` field in `research/manuscripts/emc_fusion_partner_pooling.py`

**What exists already, and what I am therefore not duplicating.** The repository holds a large amount of per-paper confirmation detail scattered across three analysis scripts: `emc_fusion_partner_pooling.py` (per-series `design`/`design_tier` strings such as "58 FISH-confirmed EMC", "central pathology review + molecular confirmation"), `aso_coverage_ladder.py` (the Okamoto 2001 15/18 quote, and a fully worked argument that Okamoto's denominator is *defined by its own assay's positivity*), and `emc_systemic_therapy_pooling.py` (Drilon, anthracycline and pazopanib design tiers). `research/manuscripts/mtap-prmt5/…-decline-review-biology-2026-08-10.md` and `repurposing/pparg-direction-emc.md` both flag "molecularly-unconfirmed cohort" as a weakness of specific analyses. `research/manuscripts/care-delivery/` contains eight files, none of which is about molecular confirmation — the closest, `emc-icdo-9231-classification.md`, sits under a **user-rejected** paper.

**What does not exist:** any cross-series table of `n_confirmed / n_total`, any era stratification, and — the substantive point — any statement that several of the largest series report **no numerator at all**. This lane's question is genuinely open, and the framing my analysis needed (that "molecularly confirmed" is two different estimands depending on cohort assembly) is a generalisation of the §2.1(3) "structural 100%" argument already made in `aso_coverage_ladder.py` for a single series.

**Closed items confirmed and not replayed.** I opened no route to Wagner 2020 (32856598), CTARC 2022, Sunitinib 2014 (24703573), the Pazopanib primary, or Trabectedin/RT 2018. None of them is in my table. Sunitinib 2014 and pazopanib appear in the repository dumps I read, but I drew no confirmation numerator from either and made no inference beyond what is retained. I did not re-open GSE4303/GSE28866 or the SRA deposit. I did not touch the restricted NR4A Perspective review. **No content-policy refusal occurred in this run.** Two PubMed tool results carried a mandatory-attribution notice, which I comply with below rather than route around.

---

## Method / inputs

**Retrieval.** PubMed MCP tools only (`search_articles`, `get_article_metadata`, `get_full_text_article`). No WebSearch was needed; no paywalled route was attempted, so no 403 was incurred.

- `get_article_metadata` on `["18951519","11679947","24746215","36948401","36563884","32572850","32612944","12598313","12378528","29937513"]`
- `search_articles`: `extraskeletal myxoid chondrosarcoma[Title] AND (cases[Title] OR analysis[Title] OR study[Title])` → 41 hits, 40 returned
- `get_article_metadata` on `["10366145","9781944","8539235","1451062","10955458","10895826","24944710","30353688","27819877"]`
- `get_full_text_article` on `["PMC2779719"]` (Drilon 2008, open access) — the single most load-bearing retrieval in this report

**Attribution (required by the PubMed tool's terms).** All article facts below were retrieved from **PubMed**. DOI links: Drilon 2008 [DOI](https://doi.org/10.1002/cncr.23978); Okamoto 2001 [DOI](https://doi.org/10.1053/hupa.2001.28226); Agaram 2014 [DOI](https://doi.org/10.1016/j.humpath.2014.01.007); Kao 2023 (Taiwan) [DOI](https://doi.org/10.1016/j.modpat.2023.100161); Michal 2023 (Czech) [DOI](https://doi.org/10.1016/j.humpath.2022.12.005); Stacchiotti/ISG 2021 [DOI](https://doi.org/10.1245/s10434-020-08737-7); Chiusole 2020 [DOI](https://doi.org/10.3389/fonc.2020.00828); Sjögren 2003 [DOI](https://doi.org/10.1016/S0002-9440(10)63875-8); Panagopoulos 2002 [DOI](https://doi.org/10.1002/gcc.10127); Meis-Kindblom 1999 [DOI](https://doi.org/10.1097/00000478-199906000-00002); Antonescu 1998 [DOI](https://doi.org/10.1002/\(sici\)1097-0142\(19981015\)83:8%3C1504::aid-cncr5%3E3.0.co;2-b); Oliveira 2000 [DOI](https://doi.org/10.1038/modpathol.3880161); Saleh 1992 [DOI](https://doi.org/10.1002/1097-0142\(19921215\)70:12%3C2827::aid-cncr2820701217%3E3.0.co;2-v); Santos 2018 [DOI](https://doi.org/10.1002/dc.24028); Sciot 1995 (PMID 8539235, no DOI in the PubMed record).

**Computation.** One stdlib-only Python 3.11.15 script, authored by me and returned inline below. Clopper-Pearson exact binomial intervals via a bisection on the regularised incomplete beta function (continued-fraction `betainc`); two-sided Fisher exact by the point-probability method. No numpy/scipy, so nothing to install and nothing to pin beyond the interpreter.

**The design decision that makes the table honest.** Every row carries an `assembly` field with three values, and the analysis refuses to pool across them:

- `morphology_then_ancillary` — the cohort was assembled on morphology/expert review, and molecular testing was applied afterwards. **Only these rows estimate anything.**
- `molecular_inclusion` — molecular positivity *is* the entry criterion. The proportion is 100% by construction and is not a measurement. This generalises the §2.1(3) argument already in `aso_coverage_ladder.py`.
- `unstated` — no numerator in the retrieved text. **UNKNOWN, never imputed to zero.**

---

## Result

### Table 1 — molecular-confirmation denominators, one row per retrievable EMC series

Uncertainty is a two-sided 95% Clopper-Pearson exact binomial interval on the stated `k/n`; it quantifies sampling only, not misclassification and not selection into publication. All quotes are verbatim from the PubMed abstract unless marked otherwise.

| Series | PMID | Year | n total | n confirmed | Proportion [95% exact CI] | Assembly | Grade |
|---|---|---|---|---|---|---|---|
| Saleh | 1451062 | 1992 | 10 | — | UNKNOWN (no numerator) | unstated | **UNKNOWN** |
| Sciot | 8539235 | 1995 | 3 | 3 | 1.000 [0.292, 1.000] | ancillary | **PRIMARY** |
| Antonescu | 9781944 | 1998 | 20 | 7 | 0.350 [0.154, 0.592] | ancillary | **PRIMARY** |
| Meis-Kindblom | 10366145 | 1999 | 117 | — | UNKNOWN (no numerator) | unstated | **UNKNOWN** |
| Oliveira | 10955458 | 2000 | 23 | — | UNKNOWN (no numerator) | unstated | **UNKNOWN** |
| Okamoto | 11679947 | 2001 | 18 | 15 | 0.833 [0.586, 0.964] | ancillary | **PRIMARY** |
| Panagopoulos | 12378528 | 2002 | 18 | 18 | 1.000 [0.815, 1.000] | molecular-inclusion | **PRIMARY (structural)** |
| Sjögren | 12598313 | 2003 | 10 | 10 | 1.000 [0.692, 1.000] | molecular-inclusion | **PRIMARY (structural)** |
| **Drilon** | **18951519** | **2008** | **86** | **—** | **UNKNOWN (no numerator)** | **unstated** | **UNKNOWN** |
| Agaram | 24746215 | 2014 | 26 | 26 | 1.000 [0.868, 1.000] | ancillary | **PRIMARY** |
| Santos | 30353688 | 2018 | 11 | — | UNKNOWN (no numerator) | unstated | **UNKNOWN** |
| Chiusole | 32612944 | 2020 | 59 | 23 | 0.390 [0.265, 0.526] | ancillary | **PRIMARY** |
| Stacchiotti/ISG | 32572850 | 2021 | 67 | 67 | 1.000 [0.946, 1.000] | molecular-inclusion | **PRIMARY (structural)** |
| Michal (Czech) | 36563884 | 2023 | 17 | 12 | 0.706 [0.440, 0.897] | ancillary | **PRIMARY** |
| Kao (Taiwan) | 36948401 | 2023 | 58 | 58 | 1.000 [0.938, 1.000] | molecular-inclusion | **PRIMARY (structural)** |

**247 of 543 patients (45.5%) across these fifteen series sit in a source that states no molecular-confirmation numerator at all.**

### The load-bearing quotes

**Drilon 2008 is the decisive one, and it required the full text.** The abstract says nothing about how diagnoses were confirmed. `PMC2779719`, Materials and Methods, Patient Selection, verbatim:

> "Patients with a definite diagnosis of EMC by expert pathologic review of the primary tumor were included in the study. **In situations in which a clear diagnosis was not established on pathology, confirmation was made by reverse-transcriptase polymerase chain reaction (RT-PCR) or fluorescence in situ hybridization (FISH) analysis for the translocation t(9;22).**"

Molecular testing was applied **only to the residue that morphology could not settle**, and **the size of that residue is stated nowhere in the paper**. This is the largest EMC treatment series the program pools over, and its confirmation numerator is unrecoverable from the published text. A second, smaller discrepancy in the same paper: the abstract says **87** patients, Methods and Results both say **86**. I report both and impute neither.

Other quotes as transcribed into the script:

- **Antonescu 1998** — "Molecular analysis for the EWS-CHN fusion RNA resulting from the t(9;22) was performed in 15 cases (9 EMC and 6 SMC) and was detected in **7 of 9 EMC cases** and 0 of 6 SMC cases." Cohort n=20 EMC; assay attempted in 9. So 7/20 on the cohort denominator, 7/9 on the tested denominator — the two differ by a factor of two and the paper reports the latter.
- **Okamoto 2001** — "EWS-CHN or TAF2N-CHN fusion gene transcripts characteristic of EMCS could be detected in **15 (83%) of the 18 cases**." Attempted in all 18. Carries the known caveat already in `aso_coverage_ladder.py`: a type-panel RT-PCR on paraffin cannot report a junction it has no primer for, so its 3 negatives are assay-scope negatives.
- **Agaram 2014** — "26 consecutive EMCs… EWSR1-NR4A3 in 16 (62%), TAF15-NR4A3 in 7 (27%), TCF12-NR4A3 in 1 (4%). Two cases showed only NR4A3 gene rearrangements." 16+7+1+2 = 26/26, arithmetic verified.
- **Chiusole 2020** — "59 patients were identified… **We performed molecular analysis in 23 cases**, all carried a EWSR1-NR4A3." A 2020 two-institution series over 1980–2018 with 39% molecular coverage.
- **Michal 2023** — "**Molecular testing was successfully performed in 12/17 cases.**"
- **Stacchiotti/ISG 2021** — "Diagnosis was centrally reviewed according to WHO 2013. **Only patients with NR4A3 rearrangement were included.**" Structural 100%.
- **Kao 2023** — "fluorescence in situ hybridization was performed **to confirm 58 EMCs**." 46+9+2+1 = 58, arithmetic verified. Structural 100%.
- **Meis-Kindblom 1999**, n=117, the largest EMC series ever published — the retrieved abstract reports clinical, morphologic and immunohistochemical features and **no molecular or cytogenetic numerator**. I record UNKNOWN, not zero. Its full text is not open access and I did not attempt a paywalled route.
- **Santos 2018** — "NR4A3 gene rearrangements were found **in all cases tested**." No denominator for "tested". UNKNOWN.

### Table 2 — era analysis (all rows computed, all **PRIMARY** arithmetic on **PRIMARY** inputs)

Primary analysis, `morphology_then_ancillary` rows only, crude denominator-weighted pool:

| Era | k/n | Proportion [95% exact CI] | Series |
|---|---|---|---|
| 1992–2009 | 25/41 | 0.610 [0.445, 0.758] | Sciot, Antonescu, Okamoto |
| 2010–2026 | 61/102 | 0.598 [0.496, 0.694] | Agaram, Chiusole, Michal |

Fisher exact two-sided **p = 1.0000** — post-hoc, descriptive, no claim rests on it.

**Sensitivity A — what a naive reader gets by pooling everything with a numerator**, i.e. letting the molecular-inclusion series in: 1992–2009 = 53/69 = 0.768 [0.651, 0.861]; 2010–2026 = 186/227 = 0.819 [0.763, 0.867]. This manufactures a modest upward "era trend" **entirely out of the inclusion criteria of four series**, not out of any change in practice. It is the wrong analysis and is reported so it can be seen to be wrong.

**Sensitivity B — bounds when the unstated-numerator patients are admitted to the denominator** (true numerator anywhere in [0, n]):

| Era | Unstated-numerator patients | Full denominator | Proportion bounded in |
|---|---|---|---|
| 1992–2009 | 236 | 277 | **[0.090, 0.942]** |
| 2010–2026 | 11 | 113 | [0.540, 0.637] |

### The answer to the lane question

**An era trend in molecular confirmation is NOT estimable from the retrievable published record, and the reason is a denominator gap rather than a sample-size problem.** Early-era ignorance width **0.852** versus late-era **0.097**. In 1992–2009 the patients whose confirmation status is unreported (236, dominated by Meis-Kindblom's 117 and Drilon's 86) outnumber the patients with a reported numerator (41) by nearly six to one, so the bounding interval spans almost the whole unit interval and **covers both directions of trend simultaneously**. The point estimates that *are* computable (0.610 vs 0.598, p = 1.0) show no trend, but they rest on 41 early-era patients drawn from three small series and cannot carry the question either.

The practically useful finding for this program is narrower and firmer: **the two largest series in the EMC outcome literature — Meis-Kindblom 1999 (n=117) and Drilon 2008 (n=86/87) — supply no molecular-confirmation numerator**, and Drilon's own Methods establish that its molecular testing was *selectively* applied to morphologically ambiguous cases only. Any pooled survival or treatment estimate that draws on Drilon inherits an unquantified misclassification exposure, and that exposure cannot be bounded from the paper. That is a real, checkable constraint on the program's existing pooled analyses.

---

## Validation evidence

**RUN.**

- Working directory: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad` (outside the repository, per the corrected brief)
- Command: `date -u && python3 -VV && uname -srm && python3 emc_molecular_confirmation.py; echo "EXIT=$?"`
- Environment: `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, `Linux 6.18.44-fc-v24 x86_64`, stdlib only (`math`, `itertools`), no third-party imports, no network
- **Exit code: `EXIT=0`**
- Timestamps: `Tue Sep  8 01:54:30 UTC 2026` → `Tue Sep  8 01:54:31 UTC 2026`
- Verbatim key output (the full stdout is reproduced in Tables 1 and 2 above; the verdict block as printed):

```
rows by assembly: ancillary=6  molecular-inclusion=4  unstated-numerator=5
patients with NO reported confirmation numerator: 247 of 543 across all listed series
  1992-2009: 25/41 = 0.610  [0.445, 0.758]
  2010-2026: 61/102 = 0.598  [0.496, 0.694]
  Fisher exact two-sided p = 1.0000  (POST-HOC, DESCRIPTIVE; no claim rests on it)
  early-era ignorance width = 0.852; late-era ignorance width = 0.097
```

**Independent sanity checks I performed on the result** (not just "it ran"): the two reconstructed totals verify against their own sources — Agaram 16+7+1+2 = 26 = stated n; Kao 46+9+2+1 = 58 = stated n. The degenerate Clopper-Pearson endpoints behave correctly (`k=n` gives an upper limit of exactly 1.000; the n=3 row gives the correct wide lower limit 0.292). The two era denominators sum to the six ancillary rows' totals (41 + 102 = 143 = 3+20+18+26+59+17).

**Earlier RUN, superseded but disclosed:** the identical script was first executed from inside the repository at `research/autonomy/.../code/W06/`, also exit 0, with byte-identical output. That copy has been deleted per the coordinator's correction; the `/tmp` run above is the authoritative one.

**PROPOSED (NOT RUN).** A `tests/` file with unit tests pinning `clopper_pearson` against published reference intervals and `fisher_exact_two_sided` against a known 2×2 — I verified the degenerate cases by inspection of the output but wrote no test file, and I do not claim the numerics are unit-tested. Retrieval of Meis-Kindblom 1999 full text (not open access; no route attempted). Retrieval of Oliveira 2000 and Saleh 1992 full texts (same). Extension of the table to case reports and to the SEER-based series (Kemmerer 2018, PMID 27819877), which have no per-case molecular data by construction.

---

## Limitations

- **Published series are a biased sample of all EMC, in a direction that is not correctable here.** A centre publishes a series because it has an unusual cohort, a new assay, or a referral concentration. Confirmation rates in published series say little about confirmation rates in the population of diagnosed EMC, and nothing at all about undiagnosed or misdiagnosed myxoid tumours — which is the population the misclassification worry is actually about.
- **The numerator means different things in different rows even within `morphology_then_ancillary`.** Sciot 1995 is a karyotype call on t(9;22) predating the NR4A3 fusion assays; Okamoto 2001 is a fixed-type RT-PCR panel on paraffin that demonstrably drops rearranged tumours; Agaram 2014 and Kao 2023 are break-apart FISH, which names no partner. Pooling them into one "confirmed" count is a coarsening I did deliberately and flag here; a finer analysis would stratify by assay, and the counts are too small to support it.
- **The two-era cut at 2010 is my choice and was made before seeing the stratified numbers**, but it is not preregistered and no one else has adjudicated it. The Fisher p is post-hoc and descriptive.
- **Clopper-Pearson intervals quantify sampling only.** They do not cover misclassification, selective reporting, or the possibility that a paper's stated numerator is itself wrong.
- **This cannot claim that morphology-only series contain misclassified tumours.** It establishes that the published record does not let you *check* whether they do, for 45.5% of the patients in it. That is weaker and is stated as weaker.
- **Nothing here is clinical evidence.** No efficacy, safety, selectivity or readiness claim follows. There is no wet lab and no new patient data — every number is transcribed from a published sentence or computed from those transcriptions.
- **Three paywalled full texts (Meis-Kindblom, Oliveira, Saleh) are honest UNKNOWNs, not absences.** Their numerators may exist in text I did not retrieve. If Meis-Kindblom's 117 turn out to carry a stated numerator, the early-era bound tightens substantially and the era question may become estimable.
- **The `assembly` classification is my judgement call per row**, made from the quoted sentence. Another reader could reasonably classify Panagopoulos 2002 as ancillary rather than molecular-inclusion. I put every quote in the script so that judgement is auditable rather than buried.
- The diagnostic-delay and referral-pathway halves of Lane 6 are untouched. I pursued only the molecular-confirmation question, which was the dispatch's concrete starting question.

---

## Stop condition

**Set:** a source-traceable molecular-confirmation denominator table across retrievable EMC series, with an honest assessment of whether an era trend is estimable, or a precise statement of why the denominators do not support it.

**MET — in the second form.** The table exists (15 series, 543 patients, every row carrying its own source sentence), and the era trend is **not estimable**, with the reason quantified rather than asserted: 236 of 277 early-era patients sit in sources with no stated numerator, bounding the early-era proportion in [0.090, 0.942].

---

## Tool-call and wall-clock count actually used

**Tool calls: 17** (2 brief reads, 3 prior-work searches, 4 PubMed calls, 1 result-parse, 1 script write+run, 4 correction-compliance and re-run calls, 2 verification calls). **Wall clock: roughly 20 minutes**, including the mid-run write-isolation correction. Both inside the ~40/~40 target.

---

## Next concrete action

**One successor task, and it is cheap and decisive.** Retrieve the Methods section of **Meis-Kindblom 1999 (PMID 10366145, Am J Surg Pathol 23(6):636-50)** and determine whether it states a molecular or cytogenetic confirmation numerator for its 117 cases. That single paper carries 117 of the 236 unresolved early-era patients — 43% of the entire ignorance mass — and it is the only unretrieved source that could by itself move the era question from "not estimable" to "estimable". It is not open access, so this needs a legitimate route (the CI escape hatch's networked runner, or an institutional route the coordinator holds); **it must not be attempted by replaying a route already recorded as denied.** If that route does not exist, the honest terminal state for this sub-question is the bound reported here, and the lane should pivot to the untouched diagnostic-delay/referral half rather than iterate on confirmation.

Secondary, and doable with no new access: propagate this finding into the program's pooled analyses as a named exposure — `emc_systemic_therapy_pooling.py` pools Drilon's 21 chemotherapy patients under a `design_tier` that does not record that Drilon's molecular confirmation was selectively applied with an unstated denominator. That is a one-field correction to an existing row, owned by whoever owns that file, not by me.

---

### Code, for the coordinator to write to disk

Intended path: `research/autonomy/opus-capacity-campaign-20260908/code/W06/emc_molecular_confirmation.py`. This is the exact file that produced the output above (exit 0). It has no third-party dependencies.

```python
#!/usr/bin/env python3
"""W06 - EMC molecular-confirmation denominator table and era analysis.

Every row's (n_total, n_confirmed) is transcribed from a source sentence quoted in
SERIES[*]['quote']. Rows whose numerator is not stated carry n_confirmed = None and are
NEVER imputed. Exact (Clopper-Pearson) binomial intervals, stdlib only.

Estimand warning, enforced structurally by the 'assembly' field:
  'morphology_then_ancillary' -- cohort assembled on morphology/expert review; molecular
      testing applied afterwards. Only these rows estimate "what fraction of a
      morphology-defined EMC cohort is molecularly confirmed".
  'molecular_inclusion' -- molecular positivity IS the inclusion criterion. Its proportion
      is 100% BY CONSTRUCTION and is not an estimate of anything.
  'unstated' -- no numerator in the retrieved text. UNKNOWN.
"""
import math

# --- exact binomial (Clopper-Pearson) via the beta quantile, computed by bisection on the
# regularised incomplete beta function built from a continued fraction. stdlib only.


def _betacf(a, b, x, itmax=300, eps=3e-14):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-300:
        d = 1e-300
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-300:
            d = 1e-300
        c = 1.0 + aa / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-300:
            d = 1e-300
        c = 1.0 + aa / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta + b * math.log1p(-x) + a * math.log(x)) * _betacf(b, a, 1.0 - x) / b


def _beta_quantile(p, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided 100(1-alpha)% interval for a binomial proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else _beta_quantile(alpha / 2.0, k, n - k + 1)
    hi = 1.0 if k == n else _beta_quantile(1.0 - alpha / 2.0, k + 1, n - k)
    return (lo, hi)


def fisher_exact_two_sided(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]] (point-probability method)."""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def hyp(x):
        return math.exp(
            math.lgamma(r1 + 1) + math.lgamma(n - r1 + 1) + math.lgamma(c1 + 1)
            + math.lgamma(n - c1 + 1) - math.lgamma(n + 1) - math.lgamma(x + 1)
            - math.lgamma(r1 - x + 1) - math.lgamma(c1 - x + 1)
            - math.lgamma(n - r1 - c1 + x + 1))

    obs = hyp(a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    return min(1.0, sum(hyp(x) for x in range(lo, hi + 1) if hyp(x) <= obs * (1 + 1e-9)))


# ------------------------------------------------------------------ the table
SERIES = [
    dict(key="saleh1992", pmid="1451062", year=1992, n_total=10, n_confirmed=None,
         method="none reported (light microscopy)", assembly="unstated",
         quote="'All cases had typical histologic features.' No molecular or cytogenetic "
               "assay is reported in the abstract. Predates the EWS/CHN cloning."),
    dict(key="sciot1995", pmid="8539235", year=1995, n_total=3, n_confirmed=3,
         method="karyotype (t(9;22)(q22-31;q11-12)); NOT an NR4A3 fusion assay",
         assembly="morphology_then_ancillary",
         quote="'Three cases of extraskeletal myxoid chondrosarcoma with typical histologic and "
               "ultrastructural features were investigated cytogenetically. All three cases showed "
               "a reciprocal chromosome translocation characterized as t(9;22)(q22-31)(q11-12)'"),
    dict(key="antonescu1998", pmid="9781944", year=1998, n_total=20, n_confirmed=7,
         method="RT-PCR for EWS-CHN, attempted in 9 of 20",
         assembly="morphology_then_ancillary",
         quote="'Molecular analysis for the EWS-CHN fusion RNA resulting from the t(9;22) was "
               "performed in 15 cases (9 EMC and 6 SMC) and was detected in 7 of 9 EMC cases and "
               "0 of 6 SMC cases.'"),
    dict(key="meiskindblom1999", pmid="10366145", year=1999, n_total=117, n_confirmed=None,
         method="none stated in the retrieved abstract (clinical/morphologic/IHC)",
         assembly="unstated",
         quote="'The clinical, morphologic, and immunohistochemical features of 117 previously "
               "unreported cases were studied and statistically analyzed.' No molecular or "
               "cytogenetic numerator appears in the retrieved abstract."),
    dict(key="oliveira2000", pmid="10955458", year=2000, n_total=23, n_confirmed=None,
         method="none stated in the retrieved abstract (IHC, Ki-67, ploidy)",
         assembly="unstated",
         quote="'Twenty-three cases ... were studied for clinicopathologic features, "
               "immunohistochemical profile, Ki-67 activity, and ploidy status'. No fusion assay "
               "numerator appears in the retrieved abstract."),
    dict(key="okamoto2001", pmid="11679947", year=2001, n_total=18, n_confirmed=15,
         method="RT-PCR on paraffin-embedded tissue, type-1/type-2/TAF2N panel, attempted in 18/18",
         assembly="morphology_then_ancillary",
         quote="'EWS-CHN or TAF2N-CHN fusion gene transcripts characteristic of EMCS could be "
               "detected in 15 (83%) of the 18 cases'"),
    dict(key="panagopoulos2002", pmid="12378528", year=2002, n_total=18, n_confirmed=18,
         method="cytogenetics + RT-PCR + genomic PCR/sequencing",
         assembly="molecular_inclusion",
         quote="'Fifteen cases had an EWS/CHN fusion transcript and three had an RBP56/CHN "
               "transcript.' The series is defined by its molecular characterisation."),
    dict(key="sjogren2003", pmid="12598313", year=2003, n_total=10, n_confirmed=10,
         method="SKY/FISH + RT-PCR", assembly="molecular_inclusion",
         quote="'All tumors contained translocation-generated or cryptic gene fusions, including "
               "EWS-TEC (five cases...), TAF2N-TEC (four cases), and TCF12-TEC (one case).'"),
    dict(key="drilon2008", pmid="18951519", year=2008, n_total=86, n_confirmed=None,
         method="RT-PCR or FISH, applied only where morphology was not decisive; count not reported",
         assembly="unstated",
         quote="'Patients with a definite diagnosis of EMC by expert pathologic review of the "
               "primary tumor were included in the study. In situations in which a clear diagnosis "
               "was not established on pathology, confirmation was made by reverse-transcriptase "
               "polymerase chain reaction (RT-PCR) or fluorescence in situ hybridization (FISH) "
               "analysis for the translocation t(9;22).' (PMC2779719 Materials and Methods.) "
               "The number so tested is NOT stated anywhere in the full text."),
    dict(key="agaram2014", pmid="24746215", year=2014, n_total=26, n_confirmed=26,
         method="FISH (NR4A3 and partner break-apart), all 26 consecutive cases",
         assembly="morphology_then_ancillary",
         quote="'We investigated 26 consecutive EMCs ... Fluorescence in situ hybridization "
               "analysis showed EWSR1-NR4A3 gene fusion in 16 cases (62%), TAF15-NR4A3 gene fusion "
               "in 7 cases (27%), and TCF12-NR4A3 gene fusion in 1 case (4%). Two cases showed "
               "only NR4A3 gene rearrangements.' 16+7+1+2 = 26."),
    dict(key="santos2018", pmid="30353688", year=2018, n_total=11, n_confirmed=None,
         method="FISH on 3 FNA specimens; histological specimens 'all cases tested', number unstated",
         assembly="unstated",
         quote="'Fluorescence in situ hybridization technique performed in three FNA specimens "
               "showed EWSR1 gene rearrangements in all... Histological specimens showed typical "
               "features of EMC and NR4A3 gene rearrangements were found in all cases tested.' "
               "'all cases tested' has no stated denominator."),
    dict(key="chiusole2020", pmid="32612944", year=2020, n_total=59, n_confirmed=23,
         method="molecular analysis (EWSR1-NR4A3), performed in 23 of 59",
         assembly="morphology_then_ancillary",
         quote="'59 patients were identified... We performed molecular analysis in 23 cases, all "
               "carried a EWSR1-NR4A3.'"),
    dict(key="isg2021", pmid="32572850", year=2021, n_total=67, n_confirmed=67,
         method="NR4A3 rearrangement required for entry", assembly="molecular_inclusion",
         quote="'Diagnosis was centrally reviewed according to WHO 2013. Only patients with NR4A3 "
               "rearrangement were included.'"),
    dict(key="czech2023", pmid="36563884", year=2023, n_total=17, n_confirmed=12,
         method="molecular testing (fusion partner assignment), successful in 12 of 17",
         assembly="morphology_then_ancillary",
         quote="'Molecular testing was successfully performed in 12/17 cases.'"),
    dict(key="taiwan2023", pmid="36948401", year=2023, n_total=58, n_confirmed=58,
         method="FISH used to confirm the cohort; RNA exome sequencing in 3",
         assembly="molecular_inclusion",
         quote="'Alongside RES-analyzed cases, fluorescence in situ hybridization was performed to "
               "confirm 58 EMCs'. FISH confirmation defines the 58."),
]

ERA_CUT = 2010


def era(y):
    return "1992-2009" if y < ERA_CUT else "2010-2026"


def main():
    print("=" * 100)
    print("W06 EMC MOLECULAR-CONFIRMATION DENOMINATOR TABLE")
    print("=" * 100)
    hdr = f"{'series':<18}{'PMID':<10}{'yr':<6}{'n':>5}{'conf':>7}  {'prop [95% exact CI]':<26}{'assembly'}"
    print(hdr)
    print("-" * 100)
    for s in SERIES:
        if s["n_confirmed"] is None:
            cell = "UNKNOWN (no numerator)"
        else:
            k, n = s["n_confirmed"], s["n_total"]
            lo, hi = clopper_pearson(k, n)
            cell = f"{k/n:.3f} [{lo:.3f}, {hi:.3f}]"
        conf = "UNK" if s["n_confirmed"] is None else s["n_confirmed"]
        print(f"{s['key']:<18}{s['pmid']:<10}{s['year']:<6}{s['n_total']:>5}{str(conf):>7}  "
              f"{cell:<26}{s['assembly']}")
    print("-" * 100)

    anc = [s for s in SERIES if s["assembly"] == "morphology_then_ancillary"]
    unk = [s for s in SERIES if s["assembly"] == "unstated"]
    inc = [s for s in SERIES if s["assembly"] == "molecular_inclusion"]
    print(f"\nrows by assembly: ancillary={len(anc)}  molecular-inclusion={len(inc)}  "
          f"unstated-numerator={len(unk)}")
    print(f"patients with NO reported confirmation numerator: {sum(s['n_total'] for s in unk)} "
          f"of {sum(s['n_total'] for s in SERIES)} across all listed series")

    print("\n--- PRIMARY ANALYSIS: only 'morphology_then_ancillary' rows (the only rows whose")
    print("    proportion estimates anything). Crude pooled proportion, descriptive. ---")
    strata = {}
    for s in anc:
        e = era(s["year"])
        k, n = strata.get(e, (0, 0))
        strata[e] = (k + s["n_confirmed"], n + s["n_total"])
    for e in sorted(strata):
        k, n = strata[e]
        lo, hi = clopper_pearson(k, n)
        print(f"  {e}: {k}/{n} = {k/n:.3f}  [{lo:.3f}, {hi:.3f}]  "
              f"(series: {[s['key'] for s in anc if era(s['year']) == e]})")
    if len(strata) == 2:
        (k1, n1), (k2, n2) = strata["1992-2009"], strata["2010-2026"]
        p = fisher_exact_two_sided(k1, n1 - k1, k2, n2 - k2)
        print(f"  Fisher exact two-sided p = {p:.4f}  (POST-HOC, DESCRIPTIVE; no claim rests on it)")

    print("\n--- SENSITIVITY A: add the molecular-inclusion rows (structural 100%). This is the")
    print("    number a naive reader would compute, and it is inflated BY CONSTRUCTION. ---")
    strata_a = {}
    for s in anc + inc:
        e = era(s["year"])
        k, n = strata_a.get(e, (0, 0))
        strata_a[e] = (k + s["n_confirmed"], n + s["n_total"])
    for e in sorted(strata_a):
        k, n = strata_a[e]
        lo, hi = clopper_pearson(k, n)
        print(f"  {e}: {k}/{n} = {k/n:.3f}  [{lo:.3f}, {hi:.3f}]")

    print("\n--- SENSITIVITY B: bounds on the unstated-numerator rows. Their true numerator is")
    print("    anywhere in [0, n_total], so the era estimate is only bounded, not estimated. ---")
    for e in ("1992-2009", "2010-2026"):
        k0, n0 = strata.get(e, (0, 0))
        nu = sum(s["n_total"] for s in unk if era(s["year"]) == e)
        if nu == 0:
            print(f"  {e}: no unstated-numerator patients; estimate unaffected.")
            continue
        lo_p, hi_p = k0 / (n0 + nu), (k0 + nu) / (n0 + nu)
        print(f"  {e}: {nu} patients with unstated numerator -> proportion bounded in "
              f"[{lo_p:.3f}, {hi_p:.3f}] on the full denominator {n0 + nu}")

    print("\n--- ERA-TREND VERDICT ---")
    e1w = sum(s["n_total"] for s in unk if era(s["year"]) == "1992-2009")
    e2w = sum(s["n_total"] for s in unk if era(s["year"]) == "2010-2026")
    width1 = ((strata["1992-2009"][0] + e1w) / (strata["1992-2009"][1] + e1w)
              - strata["1992-2009"][0] / (strata["1992-2009"][1] + e1w))
    width2 = ((strata["2010-2026"][0] + e2w) / (strata["2010-2026"][1] + e2w)
              - strata["2010-2026"][0] / (strata["2010-2026"][1] + e2w))
    print(f"  early-era ignorance width = {width1:.3f}; late-era ignorance width = {width2:.3f}")
    print("  An era trend is NOT estimable from the published record: in the early era the")
    print("  unstated-numerator mass ({} patients, incl. n=117 and n=86) exceeds the entire".format(e1w))
    print("  reported-numerator mass, so the bounding interval spans nearly [0,1] and covers")
    print("  BOTH directions of trend. Published series are additionally a biased sample of all")
    print("  EMC: series get published because a centre has an unusual cohort or a new assay.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

*(One cosmetic difference from the executed file: the executed copy carried an unused `from itertools import product` import and a redundant `None`-guard on `width1`, both removed above. The numeric path is byte-identical.)*

result: W06 built a 15-series, 543-patient EMC molecular-confirmation denominator table from primary sources (PubMed, script exit 0) showing an era trend is NOT estimable — 247/543 patients (45.5%) sit in series reporting no confirmation numerator at all, including the two largest (Meis-Kindblom n=117; Drilon n=86, whose full text confirms molecular testing was applied only to morphologically ambiguous cases with the count never stated) — bounding the 1992-2009 proportion at only [0.090, 0.942]; report and code returned inline per the coordinator's write-isolation correction, and my in-repo file was deleted.
