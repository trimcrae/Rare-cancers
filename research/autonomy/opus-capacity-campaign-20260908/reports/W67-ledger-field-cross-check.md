<!-- collected 2026-09-08T05:00:19Z by campaign coordinator; agent id a3d963174d9a513ae; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a3d963174d9a513ae.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; report follows.

## Worker

**W67**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: W55's named successor — cross-checking the five in-principle-decidable content fields of the citation-provenance ledger against committed fetch products.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the four long proxy lines and `JAVA_TOOL_OPTIONS` marked elided for length; nothing else removed):

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
no_proxy=… [elided]  NO_PROXY=… [elided]  GLOBAL_AGENT_NO_PROXY=… [elided]
npm_config_noproxy=… [elided]  JAVA_TOOL_OPTIONS=… [elided, proxy/truststore]
```

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:51:13 UTC 2026` | `Tue Sep  8 04:56:22 UTC 2026` |
| `git rev-parse HEAD` | `56f355f65b7b3e47aeb434ac02edf4cf049f40f3` | `129a4e2a1c39352a7a697c42445bb27fc50f9b0c` |
| `git status --porcelain` | 0 lines | 0 lines |

**HEAD advanced under me** (coordinator collection, per COMMON-BRIEF §1). Both commits touch only the campaign directory; every file I measured is outside it. **Write isolation honoured**: zero writes under `/home/user/Rare-cancers`, zero git write operations, no edit of any manuscript, ledger, graph file, view or report, no repair/patch/gate/test authored, no guard weakened. All execution under `/tmp/claude-0/w67/`, now deleted. **No network of any kind**: 0 links opened, 0 identifiers resolved against any service, 0 MCP calls, 0 paid API, 0 GPU. `scripts/preflight.sh` not run. `atr_hrd_sarcoma_series.py` never invoked. No `research/` module was executed at all. No content-policy refusal occurred. W25 not read, not referenced.

## Question

Of the 93 `verified` rows in `research/manuscripts/citation-provenance-ledger.json`, W55 graded five keys **decidable in principle from committed bytes**: `verified_title` (90), `verified_year` (79), `verified_journal` (11), `verified_pmid` (11), `verified_pmcid` (11). **Do those values agree with the committed fetch products that already carry the same identifiers?** Per row and per field: AGREES / DISAGREES / NOT-CARRIED, from committed bytes only.

Open because W55 measured only *presence* of the 11 `verified_pmid` strings somewhere in the tree — explicitly "not a cross-check" (W55 Limitation 3) — and graded the truth of all five fields UNKNOWN.

## Prior-work check

Read in full, in order: `COMMON-BRIEF.md` (478 lines, both "Known, measured" sections and the two 04:50Z results), `CORPUS-CONTEXT.md` (82), `CLOSED-WORK.md` (70), `reports/W55-provenance-ledger-decidability.md` (272), `reports/W43-unread-act-assertion-fields.md` (307, env dump skipped). W55's key matrix and W43's 34-field census are taken as **given**; I did not re-census the ledger's key space.

Commands run for prior art:

```
$ grep -rn -E "verified_title|verified_journal|verified_pmcid" --include='*.py' --include='*.mjs' \
       --include='*.sh' --include='*.yml' --include='*.yaml' . | grep -v '/\.git/' | wc -l
0
$ git ls-files | grep -iE 'cross.?check|ledger.?verif'
research/modalities/emc-gse4303-crosscheck.json          research/modalities/emc_gse4303_crosscheck.py
research/modalities/nr4a3-bioemu-crosscheck-findings.md  research/modalities/nr4a3-bioemu-crosscheck.json
research/modalities/selcal_dockq_crosscheck.py           research/modalities/vast-bid-ondemand-crosscheck.json
research/modalities/tests/test_bioemu_crosscheck.py      research/modalities/tests/test_selcal_dockq_crosscheck.py
```

None of the eight cross-check artifacts concerns the citation ledger (GSE4303 expression, BioEmu conformers, DockQ, Vast pricing). **No existing instrument compares these five fields to anything.** `CLOSED-WORK.md` closes nothing in this lane. Per the brief, sibling reports are premises, not repository evidence.

## Method and inputs

**Two tiers, deliberately separated, because they answer different questions.**

**Tier 1 — CO-LOCATED comparison (primary).** For each of the 93 `verified` rows I collected every JSON object anywhere in the tracked tree that carries the row's own identifier (`id`, case-folded) **or** its ledger key (`key`, case-folded — needed because two fetch-product records link back by `ledger_key`). Within those objects only, I read every key matching `title` / `year|pubdate|published` / `journal|venue|container` / `pmid` / `pmcid` and compared the normalised value to the ledger's. Normalisation: NFKD, unicode hyphen variants folded to ASCII `-`, HTML tags stripped, lowercased, non-alphanumerics collapsed for title/journal; first 4-digit year extracted; digit-run extracted for PMID/PMCID. Keys matching `manuscript_title|paper_title|section|figure|report_title` were excluded from the title comparison.

Corpus: `git ls-files '*.json'` = **4,517 files**, minus the ledger itself and the campaign directory. **4,516 parsed; 1 failed** (see Result R.5). Identifier index: 256,036 distinct normalised string/large-int values.

**Tier 2 — WIDE value-presence (secondary, and admissible only for distinctive strings).** For every Tier-1 NOT-CARRIED case, `git grep -n -F <value>` over all tracked bytes, ledger and campaign directory excluded. ⚠ **This tier is inadmissible for `verified_year` and for generic `verified_journal` values** — `git grep -F 1973` returns 2,791 hits, `2026` returns 94,437, `Nature` returns 423, none of which is about the cited work. That is the same vacuous-frame failure COMMON-BRIEF records for the `superseded[]` transplant screen ("for an alternative that is a bare numeric literal, the frame degenerates to 'any number'"), and I record those Tier-2 results as **VACUOUS, not as agreement**.

**Positive control (the km precedent's requirement).** `research/modalities/emc_ipd_survival.py:220-228` states the standard this work is held to: *"an eye reading recorded in a JSON field is unfalsifiable: nothing in the repository could disagree with it … `research/modalities/km_risk_row_detect.py` measures the band structure … THE TWO READINGS AGREE ON ALL NINE KAPLAN-MEIER FIGURES, which is what makes the negative worth something — and the instrument is shown capable of the other answer, because it fires on both figures that DO print a risk row."* Accordingly I ran the comparison twice more against **mutated scratch copies** of the ledger (never the tracked file) to demonstrate it can return DISAGREES.

Files read: `research/manuscripts/citation-provenance-ledger.json`, `research/manuscripts/citation-retraction-sweep.json`, `research/manuscripts/degrader/lit-targets-degrader-citations.json`, `research/manuscripts/aso/lit-targets-aso-instruments.json`, `research/modalities/emc_ipd_survival.py:218-232`, `research/modalities/e3-provenance-correction.json:18-26`. Tools: system `python3` (stdlib only), `git`, `grep`. Four scratch scripts under `/tmp/claude-0/w67/`, deleted.

## Result

### R.0 Headline `PRIMARY`

Across all 93 `verified` rows and the five decidable fields — **202 field instances present**, of which **4 carry an explicit `null`**:

| field | present | AGREES | **DISAGREES** | NOT-CARRIED | NULL-VALUE | field ABSENT on row |
|---|---:|---:|---:|---:|---:|---:|
| `verified_title` | 90 | **77** | **0** | 13 | 0 | 3 |
| `verified_year` | 79 | **75** | **0** | 4 | 0 | 14 |
| `verified_journal` | 11 | **2** | **0** | 9 | 0 | 82 |
| `verified_pmid` | 11 | **3** | **0** | 8 | 0 | 82 |
| `verified_pmcid` | 11 | **0** | **0** | 7 | **4** | 82 |
| **TOTAL** | **202** | **157** | **0** | **41** | **4** | 195 |

**Zero disagreements.** 157 of 202 (77.7%) of the decidable field instances are independently corroborated by a second committed artifact; 41 (20.3%) are carried by no other tracked file; 4 are `null` in the ledger itself and so carry no assertion to check.

⚠ **This does not verify any citation.** It measures agreement between two committed files that were, for 58 of the 77 title agreements, written from the *same* fetch run (see R.4). Corroboration by a copy of the same source is weaker than independent confirmation, and none of it says a link was opened, a paper exists, or a claim is supported. Per the dispatch, a disagreement here would have been a **discrepancy between two committed files, never evidence about which is right** — and there were none to report.

### R.1 Per-row table `PRIMARY`

Code per row, in field order **title · year · journal · pmid · pmcid**. `A` = AGREES, `D` = DISAGREES, `N` = NOT-CARRIED, `0` = ledger value is `null`, `-` = field absent on that row. The last column is the file supplying the corroboration (title's supporting file, or year's where title is absent).

```
AA---  DOI:10.1002/gcc.22976                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1002/gcc.23144                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1002/jcc.10128                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1002/jcc.20035                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1007/s10822-014-9747-x         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1016/0022-2836(73              research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1016/S1093-3263(98             research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1016/j.cpc.2013.09.018         research/manuscripts/degrader/lit-targets-degrader-citations.json
N-NN0  DOI:10.1016/j.jclinepi.2017.08.010    —
N-NNN  DOI:10.1016/j.patter.2023.100858      —
AA---  DOI:10.1016/j.str.2018.10.002         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/acs.jcim.4c01227          research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/acs.jctc.5c00064          research/manuscripts/aso/lit-targets-aso-degrader-refile.json
AA---  DOI:10.1021/acs.jctc.5c00736          research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/acs.jctc.6c00135          research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/acs.jmedchem.0c00894      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/acs.jmedchem.3c01467      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/acs.jmedchem.5c00459      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/bi00027a007               research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/ci300604z                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/ct060037v                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1021/jp0217839                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/nature14610                research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/nm.4306                   research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/nm1579                    research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/s41467-023-36699-3        research/manuscripts/degrader/lit-targets-degrader-citations.json
N-NNN  DOI:10.1038/s41467-023-37139-y        —
N-NNN  DOI:10.1038/s41467-024-55655-3        —
AA---  DOI:10.1038/s41556-022-01060-1        research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/s41586-019-0985-x         research/literature/fusion-consensus-probe.json
AA---  DOI:10.1038/s41586-021-03819-2        research/manuscripts/degrader/lit-targets-degrader-citations.json
N-NNN  DOI:10.1038/s41586-025-09992-y        —
N-NNN  DOI:10.1038/s41586-026-10644-y        —
N-NNN  DOI:10.1038/s41586-026-10652-y        —
AA---  DOI:10.1038/s41589-018-0055-y         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/s41592-019-0506-8         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1038/s43588-024-00737-x        research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1056/NEJMoa2505725             research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1063/1.2978177                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1063/1.445869                  research/manuscripts/degrader/lit-targets-degrader-citations.json
NN---  DOI:10.1073/pnas.2509698123           —
A-AA0  DOI:10.1089/nat.2024.0072             research/manuscripts/aso/lit-targets-aso-instruments.json
AA---  DOI:10.1093/bioinformatics/btp163     research/manuscripts/degrader/lit-targets-degrader-citations.json
N-NNN  DOI:10.1093/jamia/ocaa163             —
AA---  DOI:10.1093/nar/gkac1052              research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1093/nar/gky1075               research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1101/2025.06.14.659707         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1111/bjh.12708                 research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1126/science.1244851           research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1126/science.1244917           research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1158/1541-7786.mcr-20-0707     research/manuscripts/degrader/lit-targets-degrader-citations.json
-----  DOI:10.1158/2326-6066.CIR-19-0464     — (no decidable field on this row)
AA---  DOI:10.1186/1471-2105-10-168          research/manuscripts/degrader/lit-targets-degrader-citations.json
NN---  DOI:10.1186/s13045-026-01824-4        —
AA---  DOI:10.1364/JOSAA.4.000629            research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1371/journal.pcbi.1005659      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.1371/journal.pone.0135246      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.2210/pdb8XTT/pdb               research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.3390/cancers12092433           research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  DOI:10.3390/cancers15133373           research/manuscripts/degrader/lit-targets-degrader-citations.json
NN---  NCT:NCT06789198                       —
NN---  NCT:NCT07648069                       —
AA---  PMCID:PMC10101761                     research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC10340722                     research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC10683012                     research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC11659159                     research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC12262699                     research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC4535767                      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC5253712                      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC5863701                      research/literature/rt-lung-mets-probe.json
AA---  PMCID:PMC6926456                      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMCID:PMC7864866                      research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:20016108                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:24292623                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:24292625                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:24328678                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:24746215                         research/literature/emc-mortality-probe.json
AA---  PMID:26131937                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:28009512                         research/manuscripts/degrader/lit-targets-degrader-citations.json
N-NA0  PMID:28912002                         —
-----  PMID:31871119                         — (no decidable field on this row)
AA---  PMID:33289551                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:34124809                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:35482177                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:36658219                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:37444483                         research/manuscripts/degrader/lit-targets-degrader-citations.json
A-AA0  PMID:39912803                         research/manuscripts/aso/aso-design-only-census.json
AA---  PMID:40454645                         research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:40646688                         research/manuscripts/citation-article-types.json
AA---  PMID:41712689                         research/manuscripts/degrader/lit-targets-degrader-citations.json
-----  PMID:8634690                          — (no decidable field on this row)
AA---  PMID:9520484                          research/manuscripts/degrader/lit-targets-degrader-citations.json
AA---  PMID:9608532                          research/manuscripts/degrader/lit-targets-degrader-citations.json
```

93 rows listed. **`D` appears zero times.**

### R.2 The 41 NOT-CARRIED instances, and why `PRIMARY`

**Thirteen `verified_title` NOT-CARRIED**, in three groups:

* **Nine rows whose title exists nowhere else in the tree at all** (Tier-2 `git grep -F` = **0 hits**, and title strings are distinctive enough for that tier to be admissible): `DOI:10.1016/j.jclinepi.2017.08.010`, `…j.patter.2023.100858`, `…s41467-023-37139-y`, `…s41467-024-55655-3`, `…s41586-025-09992-y`, `…s41586-026-10644-y`, `…s41586-026-10652-y`, `…10.1093/jamia/ocaa163`, `PMID:28912002`. All eight distinct works are cited from a **single** markdown file, `research/method-watch-autonomy-prior-art-2.md`, which carries no fetch product. **NOT-CARRIED, repository-wide.**
* **Two more with 0 Tier-2 hits**: `DOI:10.1073/pnas.2509698123`, `DOI:10.1186/s13045-026-01824-4`.
* **Two NCT rows**, `NCT:NCT06789198` (ledger `:1595`-region) and `NCT:NCT07648069` (`:1612`): 0 Tier-2 hits. Both declare their own weakness in `verified_source`: `"ClinicalTrials.gov (search snippet only, not a direct fetch)"`, and `NCT07648069`'s `verified_title` is literally `"Tumor Neoantigen Vaccine ... (full title unconfirmed pending direct fetch)"` — a self-disclosed incompleteness, exactly the honest shape W43 records for registry `reviewedBy`.

**Four `verified_year` NOT-CARRIED** — the same two PNAS/BMC rows and the two NCT rows. Tier-2 is **VACUOUS** here (`2026` → 94,437 hits) and I claim nothing from it.

**Nine `verified_journal` NOT-CARRIED** and **eight `verified_pmid` NOT-CARRIED** — all from the same `method-watch-autonomy-prior-art-2.md` group. Tier-2 for journal is VACUOUS (`Nature` → 423 hits, `Nat Commun` → 122, none about these works); two rows (`J Clin Epidemiol`, `J Am Med Inform Assoc`) give 2 and 0 hits respectively and neither is a bibliographic record of the cited work.

**Seven `verified_pmcid` NOT-CARRIED, zero AGREES** — `PMC10682748`, `PMC10015005`, `PMC11833048`, `PMC12872444`, `PMC13345910`, `PMC13346116`, `PMC7727361` each return **0** Tier-2 hits. `verified_pmcid` is the one field of the five with **no corroboration anywhere in the tree** and therefore no exercised path at all.

### R.3 Correction to the field counts, and a sharpening of W55's PMID result `PRIMARY`

* ⚠ **`verified_pmcid` is 11 keys but only 7 assertions.** Four rows carry `verified_pmcid: null` — `DOI:10.1016/j.jclinepi.2017.08.010` (ledger `:1057`-region), `DOI:10.1089/nat.2024.0072` (`:1005`), `PMID:28912002`, `PMID:39912803` (`:2603`). A `null` is not a content claim; the decidable denominator for that field is **7, not 11**. `verified_title` (90), `verified_year` (79), `verified_journal` (11) and `verified_pmid` (11) carry no nulls.
* ⚠ **W55's "all 11 `verified_pmid` values appear in `citation-retraction-sweep.json`" is true but is a weaker statement than it reads.** Measured: only **3 of 11** appear in an object that also carries the ledger row's own identifier. The other 8 appear in `citation-retraction-sweep.json` as **standalone swept identifiers** — e.g. `research/manuscripts/citation-retraction-sweep.json:737-738`, `"PMID:28912002": { "pmid": "28912002", "status": "clean", "via": "PubMed esearch [uid], 2026-09-01" }`. That record contains **no DOI, no title, no year**. It confirms the PMID string was swept; it cannot corroborate the ledger's assertion that *this DOI is that PMID*. The DOI↔PMID linkage for those 8 rows is asserted by the ledger and by nothing else. This is a refinement of W55, not a contradiction — W55 said explicitly it was measuring presence, not cross-checking.
* **Three `verified` rows carry none of the five fields**: `DOI:10.1158/2326-6066.CIR-19-0464`, `PMID:31871119`, `PMID:8634690`. Nothing about them is decidable from committed bytes; they remain UNKNOWN, exactly as W43 and W55 leave them.
* **Two ledger `id`s are truncated at an unescaped `(`**: `"id": "10.1016/0022-2836(73"` (`citation-provenance-ledger.json:117`) and `"id": "10.1016/S1093-3263(98"`. The fetch product carries the full DOIs — `research/manuscripts/degrader/lit-targets-degrader-citations.json:78` `"anchor_token": "10.1016/0022-2836(73)90011-9"` — **and links back by the truncated form** at `:81` `"ledger_key": "DOI:10.1016/0022-2836(73"`. So the truncation is consistently propagated rather than an unnoticed corruption, and both rows AGREE on title and year once the `ledger_key` join is used. **Reported as a shape observation; I propose no change.** An identifier-level cross-check that joins on `id` alone would silently mark these two NOT-CARRIED — my first pass did exactly that (title AGREES 75 → 77 after adding the key join), which is worth knowing for anyone re-running this.

### R.4 What the corroboration actually rests on `PRIMARY`

Supporting files behind the 157 agreements, counted at the first supporting hit per row/field:

| n (title) | n (year) | file |
|---:|---:|---|
| 58 | 57 | `research/manuscripts/degrader/lit-targets-degrader-citations.json` |
| 5 | 6 | `research/manuscripts/aso/fusion-junction-aso-references.json` |
| 3 | 3 | `research/literature/emc-mortality-probe.json` |
| 3 | 3 | `research/literature/fusion-consensus-probe.json` |
| 2 | 2 | `research/manuscripts/aso/lit-targets-aso-degrader-refile.json` |
| 1 | 1 | `research/literature/rt-lung-mets-probe.json` |
| 1 | 1 | `research/manuscripts/citation-article-types.json` |
| 1 | 1 | `research/manuscripts/aso/lit-targets-aso-instruments.json` (also 1 journal, 1 pmid) |
| 1 | — | `research/manuscripts/aso/aso-design-only-census.json` (also 1 journal, 1 pmid) |
| — | — | `research/manuscripts/citation-retraction-sweep.json` (1 pmid) |

⛔ **75% of all title agreement comes from one file, and that file is the ledger's own cited source.** `citation-provenance-ledger.json:27` records `"verified_by": "fetch-literature.yml targets_json -> Crossref (runs 31270123183 and 31270300182); record in lit-targets-degrader-citations.json"` — the ledger names `lit-targets-degrader-citations.json` as where the record lives. So for 58 rows, "the ledger agrees with the fetch product" means **the ledger agrees with the artifact it says it was copied from**. That is a *transcription* check, not an independent one: it can catch a copying error, a stale hand edit, or a row invented without a fetch, and it caught none. It cannot catch an error present in the fetch product itself. The remaining **19** title agreements come from **seven other artifacts** written by different routes, and those are genuinely independent corroborations.

### R.5 One incidental measured defect, reported and not repaired `PRIMARY`

`research/modalities/e3-provenance-correction.json` is **tracked, named `.json`, and is not valid JSON**: `json.load` fails with `Expecting ',' delimiter: line 22 column 22`. Lines 21-26 use Python-style implicit adjacent-string concatenation inside a value:

```
research/modalities/e3-provenance-correction.json:21:  "physical_impact": "NONE on the valB benchmark. The valB ternary/binary staging resolves E3 chains from RCSB "
research/modalities/e3-provenance-correction.json:22:                     "8G1Q via ternary_pdb_stage.role_to_chains -> UNIPROT_ROLE, which already mapped Elongin B "
```

It is 1 of 4,517 tracked JSON files and it carries none of the ledger's identifiers, so it does not affect any number above. **I authored no repair and propose none** — it is outside my lane and belongs to whoever owns that artifact.

### R.6 Verdict

**AGREES 157 / DISAGREES 0 / NOT-CARRIED 41 / NULL 4, over 202 field instances on 93 rows.** W43's and W55's undecidable class shrinks by 157 instances: those are now *measured* against committed bytes rather than merely asserted. The residual 41 + 4 + 195-absent remain undecidable from committed bytes and are **UNKNOWN — not confirmed, not refuted, and certainly not false.**

## Validation evidence

**RUN.** Environment `/home/user/Rare-cancers`, HEAD `56f355f6…` → `129a4e2a…` (coordinator commits, campaign directory only), `git status --porcelain` **0 lines at both ends**. System `python3` stdlib only, `git`, `grep`. Scratch `/tmp/claude-0/w67/`, deleted. **No repository module was executed**, so no write path needed clearing; **no test suite was run and no pass/fail is asserted anywhere in this report.**

Index build (verbatim stderr):

```
candidate json files 4517
parsed 4516 failed 1
FAILPARSE ('research/modalities/e3-provenance-correction.json', "Expecting ',' delimiter: line 22 column 22 (char 984)")
index keys 256036
```

Comparison over the **live, unmodified** ledger (verbatim stdout):

```
{
 "verified_title":   {"AGREES": 77, "NOT-CARRIED": 13, "ABSENT": 3},
 "verified_year":    {"AGREES": 75, "ABSENT": 14, "NOT-CARRIED": 4},
 "verified_journal": {"ABSENT": 82, "NOT-CARRIED": 9, "AGREES": 2},
 "verified_pmid":    {"ABSENT": 82, "NOT-CARRIED": 8, "AGREES": 3},
 "verified_pmcid":   {"ABSENT": 82, "NULL-VALUE": 4, "NOT-CARRIED": 7}
}
--- DISAGREES detail ---
                       <- empty: zero disagreements
```

**POSITIVE CONTROL — the instrument is shown capable of the other answer** (mutations applied to scratch copies `/tmp/claude-0/w67/mutated.json` and `mut2.json`; **the tracked ledger was never modified**, `git status --porcelain` = 0 throughout):

```
$ python3 cmp2.py /tmp/claude-0/w67/mutated.json          # title -> a false string, year -> 1899
 "verified_title": {"DISAGREES": 1, "AGREES": 76, ...}
 "verified_year":  {"AGREES": 74, "DISAGREES": 1, ...}
--- DISAGREES detail ---
DOI:10.1002/gcc.22976 verified_title LEDGER= 'A completely different paper about nothing'
   OTHER research/manuscripts/degrader/lit-targets-degrader-citations.json returned_title
         'SMARCA2‐NR4A3 is a novel fusion gene of extraskeletal myxoid chondrosarcoma identified by RNA next‐generation sequencing'
DOI:10.1002/gcc.23144 verified_year LEDGER= 1899
   OTHER research/manuscripts/degrader/lit-targets-degrader-citations.json returned_year 2023
   OTHER research/literature/fusion-consensus-probe.json year '2023'

$ python3 cmp2.py /tmp/claude-0/w67/mut2.json             # pmid -> 99999999, journal -> a false name
 "verified_journal": {..., "DISAGREES": 1, "AGREES": 1}
 "verified_pmid":    {..., "DISAGREES": 1, "AGREES": 2}
--- DISAGREES detail ---
DOI:10.1089/nat.2024.0072 verified_journal LEDGER= 'Journal of Nonexistence'
   OTHER research/manuscripts/aso/lit-targets-aso-instruments.json journal 'Nucleic Acid Ther'
DOI:10.1089/nat.2024.0072 verified_pmid LEDGER= '99999999'
   OTHER research/manuscripts/aso/lit-targets-aso-instruments.json pmid '39912803'
```

The control fires for **4 of the 5 fields** (title, year, journal, pmid). ⛔ **No positive control is available for `verified_pmcid`**: with 0 AGREES there is no corroborating value anywhere to disagree with, so that field's comparison path is **unexercised** and its 0/0/7 line rests on absence alone. Anchors: `research/manuscripts/aso/lit-targets-aso-instruments.json:86` `"pmid": "39912803"`, `:90` `"journal": "Nucleic Acid Ther"`; ledger `:2603` `"key": "PMID:39912803"`, `:1005` `"key": "DOI:10.1089/nat.2024.0072"`.

Precedent quoted from source, `research/modalities/emc_ipd_survival.py:220-226`:

```
# ⭐ AND ON 2026-08-27 EVERY ONE OF THOSE READINGS WAS RE-TAKEN BY AN INSTRUMENT, because an eye
# reading recorded in a JSON field is unfalsifiable: nothing in the repository could disagree with
# it. `research/modalities/km_risk_row_detect.py` measures the band structure beneath each figure's
# axis and answers present / absent / undetermined; ...
# ⛔ THE TWO READINGS AGREE ON ALL NINE KAPLAN-MEIER FIGURES, which is what makes the negative worth
# something -- and the instrument is shown capable of the other answer, because it fires on both
# figures that DO print a risk row.
```

End state:

```
$ rm -rf /tmp/claude-0/w67 && ls /tmp/claude-0/w67
ls: cannot access '/tmp/claude-0/w67': No such file or directory
$ date -u ; git rev-parse HEAD ; git status --porcelain | wc -l
Tue Sep  8 04:56:22 UTC 2026
129a4e2a1c39352a7a697c42445bb27fc50f9b0c
0
```

**PROPOSED (NOT RUN).** None. I authored no test, patch, gate, guard or validator and propose none. The comparison scripts were scratch measurement code, run only under `/tmp/claude-0/w67/`, and are deleted; **I am not proposing them as a new instrument** — the dispatch instructed citing the `km_risk_row_detect.py` precedent instead of proposing one, and I have.

## Limitations

1. **Agreement is not verification.** Two committed files agreeing says nothing about whether the cited work exists, whether a link was ever opened, or whether the citation supports the claim it is attached to. `verified_by` / `verified_on` / `verified_source` (90 each) remain **UNREAD-AND-UNDECIDABLE**, exactly as W43 and W55 graded them; I did not touch that class.
2. **75% of the title corroboration is a transcription check, not an independent one** (R.4). The ledger names `lit-targets-degrader-citations.json` as its own record. Only 19 of 77 title agreements come from an artifact the ledger does not cite as its source.
3. **`verified_pmcid` has no exercised path.** 0 AGREES, so no positive control exists for it; its result is "nothing in the tree carries these seven values", which is UNKNOWN about their correctness.
4. **Tier-2 (`git grep -F`) is vacuous for years and generic journal names** and I have claimed nothing from it there. Where I report "0 hits repository-wide", the value is distinctive (a full title, a PMCID, a PMID) and the claim is bounded to tracked bytes at this HEAD.
5. **The comparison is JSON-only on the corroborating side.** A title or year stated in a Markdown bibliography, a YAML workflow or a CSV is outside Tier 1 by construction. `research/method-watch-autonomy-prior-art-2.md` is precisely such a file and is the sole home of 8 of the NOT-CARRIED rows — their identifiers appear there in prose, not as a bibliographic record. NOT-CARRIED means *no structured record co-carries the value*, not that the work is uncited.
6. **Key-matching is by regex on field names.** A corroborating record using an unusual key (`heading`, `pub`, `src_year`) would be missed; a `NOT-CARRIED` is therefore UNKNOWN rather than proven absence. The mutation control shows the matcher works where it does match; it cannot bound what it never looked at.
7. **HEAD moved under me** (`56f355f6` → `129a4e2a`); both commits are campaign-directory-only collections and every measured file is outside it.
8. **No clinical claim.** This is repository wiring and bibliographic bookkeeping. Nothing here says any treatment works, is safe, selective or ready for a patient; no cited paper's content is restated as a finding; there is no wet lab and no EMC efficacy, safety, selectivity or clinical-readiness statement.
9. **No repair.** I edited nothing, applied nothing, weakened no guard, and reordered no check. The truncated DOIs (R.3), the null `verified_pmcid`s (R.3) and the malformed `e3-provenance-correction.json` (R.5) are reported as measurements for their owners, not as work I did or propose to do.

## Stop condition

**Set up front:** cross-check all five decidable fields for all 93 `verified` rows against committed fetch products; classify every field instance AGREES / DISAGREES / NOT-CARRIED; give the three counts per field and the total; demonstrate the comparison can return DISAGREES; open no link, fetch nothing, repair nothing, write nothing into the repository; then return.

**MET.** 93 rows × 5 fields resolved (202 present instances, 195 field-absent), counts reported per field and in total, zero disagreements found, positive control fires for 4 of 5 fields and is honestly reported as unavailable for the fifth. Returning at ~5 minutes rather than padding.

## Tool-call and wall-clock count actually used

**19 tool calls** (all Bash; 2 the mandated start/end state records, 1 the scratch deletion). **0** network calls, **0** retrieval calls, **0** MCP calls, **0** links opened, **0** identifiers resolved against any service, **0** repository-module invocations, **0** test runs, **0** repository writes, **0** git write operations, **0** refusals. Wall clock **04:51:13Z → 04:56:22Z = 5 min 09 s** of measured tool time plus report drafting — well inside the ~40 call / ~40 minute target.

## Next concrete action

**The honest successor is a decision, not another worker.** The measurement this lane was built to produce is done: 157 of 202 decidable field instances agree, none disagree, and the residual 45 are enumerated by row above. Re-running any variant of this comparison would be the "repeatedly rewrite a correct paper" failure `CLAUDE.md` §5 names.

The one open item that is *not* a re-measurement, and that I deliberately did not do because it is outside a read-only lane: **the eight works cited only from `research/method-watch-autonomy-prior-art-2.md` are the ledger's entire uncorroborated surface** — 9 of 13 NOT-CARRIED titles, 9 of 9 journals, 8 of 8 PMIDs and 6 of 7 PMCIDs come from that single file, which has no fetch product anywhere in the tree while every other `verified` cluster has one. Whether that file's citations should acquire a fetch product is a **retrieval decision with an owner and a cost**, requires network the campaign forbids, and is therefore a question for the manuscript owner, not a task for a worker. I state it and stop.

I propose this and nothing else. **I have written nothing into the repository, edited no ledger, artifact, manuscript, graph, view or report, authored no repair, gate or test, and weakened no guard.**
