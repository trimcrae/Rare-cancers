> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Line numbers and blob SHAs confirmed stable. Report follows.

---

## Worker

- **Worker ID:** W04d — lane 4 refill, OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt, under Claude Code 2.1.42. I did not observe the served model. No environment variable in this container names a model — the coordinator must extract the actual runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 02:54:28 UTC 2026` · **at end:** `Tue Sep  8 02:58:25 UTC 2026`
- **`git rev-parse HEAD` at start:** `4d950cf036294627b7ae67dfb306cc1875d702ac` · **at end:** `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`. HEAD moved under me mid-run (coordinator collecting other workers). **Both** differ from the `92abbcb905cacf07f14b238db50d1b98f6590374` named as frozen in `COMMON-BRIEF.md`. I re-verified my citations against the end HEAD: `git diff --stat 4d950cf ce743d6` over both W04 report files returns **empty**, and the blobs are `b5f31fc…` (W04b) and `0c51a15…` (W04c). Every `file:line` below is valid at both HEADs.
- **`git status --porcelain` at start:** empty. **At end:** empty. `find … -name '*w04d*'` in the tree returns nothing. All execution in `/tmp/claude-0/w04d/` (one file, `recompute.py`). No git write operation of any kind.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** — literal output, abridged only by dropping the five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`), which match solely because they enumerate `api.anthropic.com` and carry no model identity:

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

**No clinical claim is made anywhere in this report.** Every duration below is a description of what a paper reported. Nothing here is a statement about prognosis, about harm from delay, or about what care should look like, and no recommendation is stated or implied.

---

## Question

**Is lane 4's duration set stable, and what is the true support for its headline interval?**

Open because both W04b and W04c rest on a paper set assembled by one PubMed search whose completeness was never tested — the identical weakness W07d found and quantified in lane 7, where a nine-paper set proved to be a 26-paper union once vocabulary was widened.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers`:

1. `git ls-files research/autonomy/opus-capacity-campaign-20260908/ | wc -l` → **99 tracked**. The campaign directory is now committed, so W04b and W04c *are* repository assertions, not loose drafts. (W04b itself recorded it as untracked — that has changed since.)
2. `git ls-files | grep -i w04` → exactly three files: `W04-pathology-imaging-resources.md`, `W04b-diagnostic-delay-interval.md`, `W04c-fulltext-duration-harvest.md`.
3. `grep -rn -E "median (of )?(6|9)(\.0)? ?(mo|month)" --include='*.md' --include='*.json' --include='*.py' .` (`.git` excluded) → hits **only** in W04b and W04c, plus one irrelevant brain-metastasis abstract in `research/literature/rt-lung-mets-probe.json:3227`.
4. `grep -rn -E "2[–-]360|2[–-]36 " --include='*.md' --include='*.json' .` → hits only in W04b and W04c.
5. `grep -rn -i "symptom duration\|duration of symptom\|symptom-to-diagnosis\|diagnostic delay" … | grep -v 'opus-capacity-campaign'` → **zero hits**. No file outside the campaign directory asserts anything about the EMC diagnostic interval.
6. `grep -n -i "lane 4\|duration\|delay\|w04" WAVE-LOG.md` → **zero hits**. The coordinator's wave log carries no lane-4 paraphrase at all, so there is no third assertion site to diverge.
7. `grep -n -i "lane 4\|w04\|duration\|delay" AGENT-ROLES.md MANIFEST.md` → `AGENT-ROLES.md:21` assigns lane 4 to "Digital pathology / imaging resource + licence analyst"; `:23` assigns diagnostic delay to **lane 6**.

**Closed items confirmed not replayed.** I opened no route to Wagner 2020, CTARC 2022, Sunitinib 2014, the Pazopanib primary, or Trabectedin/RT 2018. I touched no denied route, no publisher route, no paywall, GSE4303/GSE28866, the NR4A Perspective, the ICD-O paper, or the clinical registry. I did **not** re-run W04c's generator — I reused its committed output tables as an input, as instructed. I did not enter lane 6's molecular-confirmation question. **No content-policy refusal occurred in this run.**

---

## Method / inputs

**Committed inputs (read, not re-derived):** `research/autonomy/opus-capacity-campaign-20260908/reports/W04b-diagnostic-delay-interval.md` (blob `b5f31fc…`) and `…/W04c-fulltext-duration-harvest.md` (blob `0c51a15…`), plus `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `W04-pathology-imaging-resources.md`, `W06-diagnostic-delay-molecular-confirmation.md`, `AGENT-ROLES.md`, `MANIFEST.md`, `WAVE-LOG.md`. I read the **live cloud checkout**, not the frozen corpus at `/tmp/claude-0/frozen-corpus/`.

**Retrieval — PubMed MCP only** (`search_articles`, `convert_article_ids`, `get_article_metadata`, `get_full_text_article`). No WebSearch, no publisher route, no paywall attempt. **Identifier guard applied as mandated:** `convert_article_ids` was run on all 34 candidate PMIDs *before* any of them was described; **34/34 `requested-id` fields echoed back exactly, zero mismatches, nothing discarded.**

**Attribution (required by the PubMed tool's terms).** According to PubMed and PubMed Central, all article facts below were retrieved from PubMed. DOI links for every source I assert a fact about: PMID 19890812 [DOI](https://doi.org/10.1055/s-0028-1098788); PMID 41635359 [DOI](https://doi.org/10.7759/cureus.100687); PMID 35494187 [DOI](https://doi.org/10.5114/jcb.2022.115161); PMID 7270148 [DOI](https://doi.org/10.1111/j.1440-1827.1981.tb01387.x); PMID 6402851 [DOI](https://doi.org/10.1007/BF00666219); PMID 151975 [DOI](https://doi.org/10.1007/BF00432640); PMID 30386446 [DOI](https://doi.org/10.1016/j.radcr.2018.09.027); PMID 23189013 [DOI](https://doi.org/10.4103/0976-3147.102641); PMID 39941809 [DOI](https://doi.org/10.3390/cancers17030442); PMID 7456313 [DOI](https://doi.org/10.1007/BF00430704); PMID 9149016 [DOI](https://doi.org/10.1002/(sici)1097-0142(19970515)79:10%3C1903::aid-cncr10%3E3.0.co;2-z); PMID 1440978 [DOI](https://doi.org/10.3109/01913129209061549); PMID 8734708 [DOI](https://doi.org/10.1016/s1079-2104(96)80053-9); PMID 7571087 [DOI](https://doi.org/10.3109/01913129509064233); PMID 129278 [DOI](https://doi.org/10.1002/1097-0142(197601)37:1%3C300::aid-cncr2820370140%3E3.0.co;2-#); PMID 10410173, 8154989, 2111968 [DOI](https://doi.org/10.1097/00000421-199006000-00006), 2974598, 2464825, 3337620, 3786159, 4001032 [DOI](https://doi.org/10.1016/S0344-0338(85)80196-5), 6478143 [DOI](https://doi.org/10.1259/0007-1285-57-681-836), 6524124, 6477167, 6476662, 7079855, 6281155 [DOI](https://doi.org/10.1111/j.1365-2559.1982.tb02713.x), 7196282 [DOI](https://doi.org/10.1002/1097-0142(19810601)47:11%3C2611::aid-cncr2820471116%3E3.0.co;2-0), 7213084, 6243509 [DOI](https://doi.org/10.1002/1097-0142(19800201)45:3%3C520::aid-cncr2820450318%3E3.0.co;2-6), 707436 [DOI](https://doi.org/10.1093/ajcp/70.4.700), 1234779, 4702680 [DOI](https://doi.org/10.1093/ajcp/59.5.623) (those without a link have no DOI in the PubMed record).

**Computation.** One stdlib-only Python 3.11.15 script (`/tmp/claude-0/w04d/recompute.py`, returned inline in Validation evidence), run outside the repository. Medians and ranges only — I deliberately compute no confidence interval on a set whose members have mixed anchors.

---

## Result

### Finding 1 — the headline claim, verbatim, and the divergence

Lane 4's headline quantitative claim is asserted in **two committed places with different numbers and different n**, and neither is marked as superseding the other:

| Assertion site (`file:line`) | Verbatim | n | Median | Range |
|---|---|---|---|---|
| `reports/W04b-diagnostic-delay-interval.md:178` | `\| Stated durations only \| 8 \| **6.0 mo** \| 2–36 \| 2, 5, 6, 6, 6, 12, 12, 36 \|` | 8 | **6.0 mo** | 2–36 mo |
| `reports/W04b-diagnostic-delay-interval.md:179` | `\| + 1 derived from dates \| 9 \| **6.0 mo** \| 2–36 \| 2, 5, 6, 6, 6, 6, 12, 12, 36 \|` | 9 | 6.0 mo | 2–36 mo |
| `reports/W04c-fulltext-duration-harvest.md:184` | `\| Stated durations only \| **10** \| **9.0 mo** \| 2–360 \| 2, 5, 6, 6, 6, 12, 12, 36, **72**, **360** \|` | 10 | **9.0 mo** | 2–360 mo |
| `reports/W04c-fulltext-duration-harvest.md:185` | `\| + 1 derived from dates \| 11 \| 6.0 mo \| 2–360 \| 2, 5, 6, 6, 6, 6, 12, 12, 36, 72, 360 \|` | 11 | 6.0 mo | 2–360 mo |

Restated in prose at `W04b:191` (*"Nine values, median 6 months, range 2–36"*), `W04b:466`, `W04b:482`, `W04c:189` (*"The median of 9 months cannot be read as a median diagnostic delay for EMC"*) and `W04c:574`.

**The divergence, graded PRIMARY (a repository-state reading):**

1. **Two live medians.** The repository simultaneously asserts 6.0 mo (W04b) and 9.0 mo (W04c) for "the" stated-duration set. W04c is the later and larger measurement and explains the move at `W04c:187–189`, but W04b's tables are not annotated as superseded, so a reader arriving at W04b:178 gets 6.0 mo / 2–36 with no pointer forward. This is the exact pattern `CLAUDE.md §1` forbids — retired instructions sitting beside current ones.
2. **A within-file scope slip in W04b.** `W04b:191` says *"**Nine** values, median **6** months"*. Nine values is the `+derived` row; the stated-only row is eight. Both happen to have median 6.0, so the number is not wrong — but the sentence attaches the n of one estimand to the label of another, and it is this sentence, not the table, that the summary line at `W04b:482` propagates.
3. **A non-monotone median that looks like an error and is not.** W04c reports n=10 → 9.0 mo but n=11 → 6.0 mo: adding a value *lowers* the median. I verified this is correct parity arithmetic, not a defect (n=10 median = mean of the 5th and 6th = (6+12)/2 = 9.0; n=11 median = the 6th = 6). It is nonetheless a fragility signal, exploited by Finding 4.
4. **Lane mislabelling.** `AGENT-ROLES.md:23` assigns diagnostic delay to **lane 6**, and `W04b` opens by declaring itself *"reassigned from Lane 4 (closed) to the untouched diagnostic-delay half of Lane 6."* The work is filed under W04b/W04c but is, by the campaign's own roles table, lane-6 work. The dispatch calling it "lane 4's duration set" is following the filename, not the roles table.
5. **No third assertion site.** `WAVE-LOG.md` contains zero lane-4/duration text, and no file outside the campaign directory mentions the EMC diagnostic interval at all. So the divergence is confined to these two files — it has not leaked into `pinned-figures.json`, the manuscripts, or the registry.

### Finding 2 — the papers supplying a duration, with anchors, unharmonised

Transcribed from `W04b:161–172` (Table 2) and `W04c:143–153` (Table 2). **I have not re-derived these values; they are W04c's harvest reused as an input, per the dispatch.**

| PMID | Value | Unit | Statistic | **Anchor (start → end)** | Grade |
|---|---|---|---|---|---|
| 30985717 | 36 | months | single case | mass noticed → presentation (*"3-year history of a slowly growing painless left leg mass"*) | PRIMARY |
| 29657686 | 12 | months | single case | **symptom** onset → presentation (*"nasal obstruction and occasional epistaxis of one-year duration"*) | PRIMARY |
| 26125202 | 12 | months | single case | mass noticed → presentation (*"a growth underneath the sole … for 1 year"*) | PRIMARY |
| 28638563 | 6 | months | single case | mass noticed → presentation (*"mass … of 6 months duration"*) | PRIMARY |
| 38440485 | 6 | months | single case | **symptom** onset → presentation (*"difficulty in chewing food for a duration of 6 months"*) | PRIMARY |
| 27591381 | 6 | months | single case | **symptom** onset → presentation (*"intermittent hemoptysis for the last 6 months"*) | PRIMARY |
| 30325000 | 5 | months | single case | **symptom** onset → presentation (*"accusing pelvic pain for 5 months"*) | PRIMARY |
| 11917595 | 2 | months | single case | mass noticed → presentation (*"a hard lump in the breast of two months' duration"*) | PRIMARY |
| 40831041 | 72 | months | single case | mass noticed → presentation (*"first palpating a peanut-sized subcutaneous mass … 6 years earlier"*) | PRIMARY |
| 35494187 | 360 | months | single case | mass discovered → **diagnosis** (*"discovered 30 years ago"* … *"In 2015 … she was diagnosed with EMC"*) | PRIMARY |
| 21941486 | ~6 | months | single case, **DERIVED** | **first presentation → pathological diagnosis** (April 2009 presentation, October 2009 biopsy) | SECONDARY (derived) |
| 24713246 | 3–12 | months | **range over n=5, no median, denominator UNSTATED** | onset → (unstated) | PRIMARY — **excluded from the distribution by W04b, correctly** |
| 28360467 | — | — | qualitative only (*"from several months"*) | mass → presentation | PRIMARY (qualitative), not poolable |

**The mixture, stated rather than harmonised (this is the answer to part 2):**

- **Three distinct anchor pairs are pooled in the committed n=10 set.** Five values are *mass-noticed → presentation*; four are *symptom onset → presentation*; **one (35494187, the 360-month extreme) is *discovery → diagnosis***, which includes the post-presentation workup interval that the other nine exclude. These are not the same quantity. The largest single value in the set is the one measured over the longest anchor span.
- **The n=11 `+derived` set pools a fourth, orthogonal anchor.** Mitchell (21941486) is *first presentation → pathological diagnosis* — it starts where the other ten **end**. Pooling it into a symptom-duration distribution adds a value from the complementary segment of the pathway. W04b and W04c both correctly grade it DERIVED and both present the n=11 row as secondary, but the row still appears as a median and range of the same column, and `W04b:191`/`W04b:482` quote the n=9 pooled figure in prose.
- **"Mass noticed" and "symptom onset" are themselves different anchors.** A painless lump the patient happens to notice and a symptom that drives consultation are different starting events; the committed set treats them as one.
- **Statistic types are, to W04c's credit, not mixed.** All eleven pooled values are single cases. Xu 2014's n=5 range is correctly kept out. That half of the pooling discipline holds.

**So: yes, the committed figure pools across incompatible anchors.** The n=10 headline mixes three anchor pairs; the n=11 variant mixes four.

### Finding 3 — set stability under vocabulary widening

**Axis declared in advance: vocabulary.** Chosen because lane 4's founding query (`W04b`, Method) was `extraskeletal myxoid chondrosarcoma[Title] AND (case report[Publication Type] OR case[Title])` — restricted to the **exact phrase in the title**. EMC carries a documented historical synonym, *chordoid sarcoma* (Stewart, 1948; the entity was renamed), plus a hyphenated spelling *extra-skeletal*. A title-phrase search cannot return any of these, so vocabulary is where a real gap must be if one exists. It is a fair test because it changes only the surface string, not the inclusion criteria, and it mirrors W07d's lane-7 method, making the two lanes comparable. Citation-graph widening was rejected as unfair here: lane 4's set is dominated by case reports, which cite thin and idiosyncratically.

Two searches, run before any classification:

- `"chordoid sarcoma"[All Fields]` → **31** PMIDs (total_count 31, complete).
- `("extra-skeletal myxoid chondrosarcoma" OR "extraskeletal myxoid chondro-sarcoma" OR "myxoid chondrosarcoma of soft tissue" OR "chordoid sarcoma") AND (duration OR history OR noticed OR swelling)` → **4** PMIDs. *PubMed's `query_translation` silently dropped two of my four phrases* (`"extraskeletal myxoid chondro-sarcoma"`, `"myxoid chondrosarcoma of soft tissue"` do not appear in the translation) — recorded because it means this arm tested fewer variants than I asked for.

**Union = 34 PMIDs. Zero of the 34 appear anywhere in W04b's or W04c's tables.** The addition is therefore 34 papers on top of lane 4's ~34-paper set (26 case reports + 8 series) — a set roughly doubled, the same order of instability W07d found in lane 7 (9 → 26).

**Crucially, the addition is *not* a clean superset, and this is a difference from lane 7.** "Chordoid sarcoma" in 1973–1990 was also applied to entities now split off from EMC. Screening all 34 abstracts:

| Class | n | Examples |
|---|---|---|
| **Admissible EMC, new usable duration** | **2** | 19890812, 41635359 |
| Admissible EMC series, **abstract-silent** on duration | 2 | 7270148 (n=14 clinicopathologic series), 6402851 (n=12 series) |
| Admissible EMC/synonym, abstract-silent, no PMCID → full text UNRECOVERED | 12 | 7079855, 7213084, 6477167, 6524124, 6476662, 129278, 707436, 1234779, 2111968, 2974598, 3786159, 4702680 |
| **Not admissible** — different entity (parachordoma, skeletal myxoid chondrosarcoma, chondroid lipoma, synovial/brown-fat reclassification, nosology-only, chordoma) | 17 | 30386446, 23189013, 10410173, 9149016, 8734708, 7571087, 8154989, 1440978, 3337620, 4001032, 6478143, 6281155, 7196282, 6243509, 7456313, 2464825, 39941809 |
| **Borderline** — duration present but entity and derivation both uncertain | 1 | 151975 |

**Count of new usable duration values: 2** (plus 1 borderline, reported separately and **not** pooled).

| PMID | Value | Anchor | Why lane 4 missed it | Verbatim | Grade |
|---|---|---|---|---|---|
| **19890812** (Mroczkowski 2009, *Zentralbl Chir*, German) | **18 mo** | **"delay in diagnostics"** — an explicit *delay to diagnosis*, not a symptom duration | title/abstract use the **hyphenated** *"extra-skeletal myxoid chondrosarcoma"* | *"After a **delay in diagnostics for 1.5 years**, an MRI scan taken in a 42-year-old male patient with progressive swelling of the left calf showed a soft-tissue tumour…"* | **PRIMARY** |
| **41635359** (Cureus 2026, PMC12863220) | **1 mo** | mass noticed → presentation | hyphenated *"Extra-skeletal"* in the title | *"The palpable non-tender abdominal mass had been present for **one month**. The patient reported **five to six months** of significant fatigue."* (EMC FISH-confirmed, NR4A3/EWSR1) | **PRIMARY** |
| 151975 (Tanaka 1978) | ~120 mo, **DERIVED** | onset (age ~37) → radical resection (age 47); diagnosis date never stated | "chordoid sarcoma" | *"a history of over 30 years after onset at around 37 years of age"*; radical resection at 47 | **SECONDARY / UNKNOWN entity** — authors themselves offer *"chondroid chordoma"* as an alternative label. **Excluded.** |

**Two consequences beyond the count.**

- **The new 1-month value is below the committed minimum of 2**, so the widening extends the range at *both* ends, not only the tail W04c identified.
- **19890812 bears directly on W04c's most quotable negative.** `W04c:196–207` concludes *"no source quantifies a system-side diagnostic delay … Zero of four retrievable EMC misdiagnosis narratives states the time the misreading cost."* Here is an EMC paper whose abstract states *"a delay in diagnostics for 1.5 years"* in so many words. Whether that delay was system-side or patient-side **is not resolved by the abstract**, and I did not obtain the full text (no PMCID; German-language journal) — so I record it as **UNKNOWN as to attribution, but PRIMARY as to existence**. W04c's verdict was scoped to "four retrievable misdiagnosis narratives" and is not false within its own denominator; but as a general claim that the literature contains no quantified diagnostic delay, it does not survive vocabulary widening.
- **The series-level negative gets *stronger*.** 7270148 (Tsuneyoshi 1981, 14 EMC cases) and 6402851 (Dardick 1983, 12 chordoid sarcomas) are clinicopathologic series lane 4's eight-series set never enumerated, and **both are abstract-silent on symptom duration.** W04b's *"0 of 8 series"* becomes **0 of 10** at abstract level, over 331 + 26 = **357** pooled patients. Inter-series patient overlap is **UNKNOWN** — W04b did not audit it and neither did I.

### Finding 4 — the true support set, and the recomputation

**True support set of the committed n=10 headline: ten single-patient case reports, listed above** — PMIDs 11917595 (2), 30325000 (5), 28638563 (6), 38440485 (6), 27591381 (6), 29657686 (12), 26125202 (12), 30985717 (36), 40831041 (72), 35494187 (360). **No series contributes a single value.** Nine of the ten values come from a one-sentence clause in an abstract or a case-presentation paragraph; the tenth (35494187) is the 360-month extreme carrying one third of the set's entire span.

**Committed alongside recomputed — never in place of:**

| Set | n | Median | Range | Status |
|---|---|---|---|---|
| **COMMITTED** `W04b:178` | 8 | **6.0 mo** | 2–36 | reproduced exactly from the committed table |
| **COMMITTED** `W04c:184` ← the headline | 10 | **9.0 mo** | 2–360 | reproduced exactly from the committed table |
| **COMMITTED** `W04c:185` | 11 | 6.0 mo | 2–360 | reproduced exactly from the committed table |
| **W04d, + 41635359 only** (same anchor family, no anchor mixing added) | **11** | **6.0 mo** | **1–360** | **DISAGREES with the committed 9.0** |
| W04d, + 41635359 + 19890812 (**pools a delay anchor**) | 12 | 9.0 mo | 1–360 | agrees numerically, but only by pooling an incompatible anchor |
| 19890812 on its own anchor | 1 | 18.0 mo | — | the only explicitly-labelled *delay* value in the corpus |

**The disagreement is the finding, and it is sharp.** Adding **one** vocabulary-widened paper — a molecularly confirmed EMC case report, admissible by every criterion lane 4 itself used, missed solely because its title hyphenates *extra-skeletal* — moves the headline median from **9.0 months to 6.0 months**, a 33% shift. The committed 9.0 is a parity artefact of an even-n set straddling the 6/12 gap, exactly the fragility Finding 1 flagged. The median is not stable to a single admissible addition.

**What *is* reproduced successfully, and it is worth stating:** every committed arithmetic result I checked is correct as arithmetic. W04c's n=10 → 9.0 and n=11 → 6.0 are right; W04b's n=8 and n=9 both give 6.0; the parity behaviour is real, not a bug. **The defect is not in the computation — it is that a median over ten anchor-mixed single cases was reported as a headline at all.** W04b and W04c both say so themselves, repeatedly and in bold (`W04b:181`, `W04c:189`: *"cannot be read as a median diagnostic delay for EMC"*). My result is that they understated it: the figure is not merely unrepresentative of patients, it is **unstable to the search string that produced it**.

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24, `/home/user/Rare-cancers` (read-only to me), execution in `/tmp/claude-0/w04d/`, Python 3.11.15, Claude Code 2.1.42.

Recomputation script (authored by me; returned inline, **not** written into the tree):

```python
#!/usr/bin/env python3
import statistics as s
def d(name, v):
    v=sorted(v); print(f"{name:52s} n={len(v):3d} median={s.median(v):7.1f} mo  range={min(v)}-{max(v)} mo")
    print(f"{'':52s} values={v}")

committed_c     = [2,5,6,6,6,12,12,36,72,360]      # W04c:184, stated-only
committed_c_der = [2,5,6,6,6,6,12,12,36,72,360]    # W04c:185, +derived
committed_b     = [2,5,6,6,6,12,12,36]             # W04b:178
print("== COMMITTED (reproduced from the report tables, not recomputed from sources) ==")
d("W04b Table 4 stated-only", committed_b)
d("W04c Table 4 stated-only  <-- HEADLINE", committed_c)
d("W04c Table 4 +derived", committed_c_der)
print("\n== W04d, vocabulary-widened ==")
d("+41635359 only (same anchor: mass-noticed)", committed_c+[1])
d("+41635359 +19890812 (POOLS a delay anchor)", committed_c+[1,18])
d("19890812 alone, its own anchor", [18])
```

`python3 /tmp/claude-0/w04d/recompute.py` — verbatim output, **exit code 0**:

```
== COMMITTED (reproduced from the report tables, not recomputed from sources) ==
W04b Table 4 stated-only                             n=  8 median=    6.0 mo  range=2-36 mo
                                                     values=[2, 5, 6, 6, 6, 12, 12, 36]
W04c Table 4 stated-only  <-- HEADLINE               n= 10 median=    9.0 mo  range=2-360 mo
                                                     values=[2, 5, 6, 6, 6, 12, 12, 36, 72, 360]
W04c Table 4 +derived                                n= 11 median=    6.0 mo  range=2-360 mo
                                                     values=[2, 5, 6, 6, 6, 6, 12, 12, 36, 72, 360]

== W04d, vocabulary-widened ==
+41635359 only (same anchor: mass-noticed)           n= 11 median=    6.0 mo  range=1-360 mo
                                                     values=[1, 2, 5, 6, 6, 6, 12, 12, 36, 72, 360]
+41635359 +19890812 (POOLS a delay anchor)           n= 12 median=    9.0 mo  range=1-360 mo
                                                     values=[1, 2, 5, 6, 6, 6, 12, 12, 18, 36, 72, 360]
19890812 alone, its own anchor                       n=  1 median=   18.0 mo  range=18-18 mo
                                                     values=[18]
exit=0
```

**Identifier guard, RUN.** `convert_article_ids(ids=[34 PMIDs], id_type="pmid")` → `"status":"ok"`, 34 records, every `requested-id` matching its `pmid` field. Zero mismatches, nothing discarded. Only 4 of 34 carry a PMCID: PMC6205874, PMC3505352, PMC12863220, PMC11816224.

**Anchor test on the 360-month extreme, RUN.** `get_full_text_article(["PMC9044308"])` (PMID 35494187 — already recovered by W04c, so not a new route). The full text gives: *"An **87-year-old** woman presented with a slow-growing tumor of the right ankle joint **discovered 30 years ago**. … **In 2015**, the patient's ankle joint tumor underwent necrosis with infection, and she was **diagnosed with EMC**."* The phrase *"ago"* is ambiguous between the 2015 presentation and the 2022 publication (which would give ~276 months, not 360). **The age arithmetic resolves it in favour of the committed value**: the abstract states she was 87 at the amputation, which the text places three months after the 2015 diagnosis, so "30 years ago" anchors at 2015 → 1985 → 360 months. **The committed 360 is not overturned.** Residual ambiguity is recorded, not suppressed.

**PROPOSED (NOT RUN).** Full texts of the 12 admissible abstract-silent additions with no PMCID; the full text of 19890812 (which would resolve whether its 1.5-year delay is system- or patient-side); a citation-graph widening arm; any re-derivation of W04c's harvest from sources.

---

## Limitations

- **I reused W04c's harvest as an input and did not re-verify its ten values against their sources.** If a value in `W04c:184` is mis-transcribed, my recomputation inherits the error. My recomputation tests *stability*, not *correctness of transcription*.
- **The widening is one axis and one vocabulary.** It says nothing about citation-graph or MeSH-based completeness, and PubMed silently dropped two of my four phrase variants, so even the vocabulary arm is incomplete. The true addition set is a **lower bound**: 34 is what these two strings found.
- **30 of 34 additions have no PMCID.** Their full texts are UNRECOVERED → **UNKNOWN, never negative, never imputed**. My "2 new usable values" is therefore a **lower bound on the widened set's yield**, exactly as W04c's 11/26 was a lower bound on the original set's.
- **Admissibility of the older "chordoid sarcoma" literature is a genuine scientific judgement I made from abstracts alone**, and I made it conservatively — 17 papers excluded, 1 borderline excluded. A different adjudicator with full texts could admit some of the 17 and shift the count. This is a weaker evidentiary basis than lane 7's widening, where the entity was not in nosological flux.
- **I computed no confidence interval on the widened distribution, deliberately.** A CI over anchor-mixed values would imply a sampling model that does not exist here.
- **Inter-series patient overlap is unaudited** in both the committed 331 and my 357.
- **This cannot claim anything clinical.** It is a description of what papers reported and of how stable a repository figure is under a search-string change. It says nothing about prognosis, about whether any delay harmed any patient, or about what care should look like. W04b's and W04c's central negative — that the published EMC record does not support a symptom-duration or diagnostic-delay distribution — is **strengthened, not weakened**, by everything above.
- The frozen commit named in `COMMON-BRIEF.md` (`92abbcb…`) was not this checkout's HEAD at any point in my run.

---

## Stop condition

**Set up front:** return as soon as (a) the headline claim is located verbatim with `file:line` and any divergence characterised, (b) the duration-supplying papers are enumerated with anchor and statistic type, (c) one declared widening axis is executed with its additions enumerated and its count of new usable values determined, and (d) the headline is recomputed and shown beside the committed figure.

**MET, all four parts.** (a) two divergent assertion sites plus a scope slip and a lane mislabel; (b) 13 rows with three-to-four mixed anchors identified; (c) vocabulary axis, 34 additions, **2 new usable values**, 1 borderline excluded; (d) recomputed — 6.0 mo vs the committed 9.0 mo, disagreement, with the arithmetic reproduced exit 0.

---

## Tool-call and wall-clock count actually used

**18 tool calls** (9 Bash, 1 ToolSearch, 2 PubMed `search_articles`, 1 `convert_article_ids`, 2 `get_article_metadata`, 2 `get_full_text_article`, plus this accounting within the final Bash), against a ~40-call target. **Wall clock 02:54:28Z → 02:58:25Z ≈ 4 minutes**, against a ~40-minute target. Returned on stop-condition satisfaction, not padded.

---

## Next concrete action

**One successor, finite and in-lane: resolve PMID 19890812's full text to determine whether its stated 1.5-year "delay in diagnostics" is system-side or patient-side.** It is the single highest-value unresolved item in this lane: it is the only explicitly-labelled *diagnostic delay* quantity in the retrievable EMC corpus, it bears directly on the one W04c verdict this run challenged (`W04c:196–207`), and its attribution is the difference between "the literature quantifies a system-side delay once" and "it does not". It has **no PMCID**, so the successor's first task is to establish whether any permitted route exists at all — and if none does, to record it as UNRECOVERED/UNKNOWN and stop, rather than reroute. **It must not open any route recorded as denied in `CLOSED-WORK.md`.**

Secondary, cheaper, and available from committed evidence alone: **the coordinator should reconcile `W04b:178–179`/`:191`/`:482` against `W04c:184–185`** so the repository stops asserting two medians for one set — per `CLAUDE.md §1`, by correcting the current prose and marking W04b's table superseded, not by deleting W04b's record.
