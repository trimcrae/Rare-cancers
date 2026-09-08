> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W21** — cross-cutting corpus-vs-completed-reports provenance audit lane, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable observed in this session names a served model; the coordinator must extract the actual per-child runtime model from the transcript. Do not treat this line as observed fact.

`date -u` at **start**: `Tue Sep  8 02:31:35 UTC 2026`
`date -u` at **end**: `Tue Sep  8 02:35:37 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (full, verbatim):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=<same no_proxy list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags>
NO_PROXY=<same no_proxy list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same no_proxy list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

At end the same command returned the same set (I filtered to seven lines for brevity; nothing changed).

**Actual HEAD read — and it moved under me, which matters.**

| Point | HEAD |
|---|---|
| Live checkout HEAD at my start, and the HEAD my file differential is keyed to | `47aac85f874a57a6f981c3432abcf16980968aec` |
| Live checkout HEAD at my end (coordinator committed during my run) | `7d081218f107363573573e6d102e4334567adf77` |
| Commit `COMMON-BRIEF.md` declares as the campaign freeze point | `92abbcb905cacf07f14b238db50d1b98f6590374` — present in the object store, **not** HEAD at any point I observed |
| Corpus snapshot base | `93b75888e31976195145e2404373b2d7a512f6d1` — **not in the local object store**; `git cat-file -t` exit 128 |

`git status --porcelain | wc -l` → `0` at end. I wrote nothing into the tree. All execution was under `/tmp/claude-0/w21/`.

---

## Question

**Which of this campaign's 48 completed reports made a novelty, absence, or "no prior work" claim that the frozen corpus now contradicts, corroborates, or leaves standing?**

It is open because the corpus arrived after every report in `reports/` was written, and `CORPUS-CONTEXT.md` §"How workers must use it" item 1 says explicitly that "not found locally" is now a much weaker claim than it was — but no worker has yet re-tested a single completed claim against it.

---

## Prior-work check

- `ls /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/` — no existing corpus-differential or claim-audit artifact; the only report that audits absence claims is `W09b-absence-claim-audit.md`, which ran a **regex gate over repository prose at the live checkout**, not a corpus differential. W09b's own §L206 already recorded the W07→W07b contradiction; I do not re-report that as mine, I report it as W09b's and W07b's.
- `grep -n -i -E "no prior|does not exist|no output|not found|first time|no existing|never been|..." reports/*.md` → **168 matching lines across 48 reports**. This is the claim pool.
- `CLOSED-WORK.md` read in full. Items I confirm I am **not** replaying, re-reviewing, or relabelling: the blocked NR4A Perspective refusal (not approached under any label — the corpus does not authorize it and I did not read `research/manuscripts/nr4a-reagents/` for content); PUB-EMC-CLASSIFICATION / the user-rejected registry ICD-O paper (untouched); the Brenca case-identity gate (see Result R6 — I treat the corpus Brenca material as **DUPLICATE**, report no accession, and draw no cohort, independence or patient conclusion from it); Davis, Hofvander, promoter transfer, inverse bounds; every unrecovered source (Pazopanib, anthracycline, sunitinib, trabectedin/RT, Wagner, CTARC — I fetched nothing, no network was used); the lane-11 source-index bundle (Lane 11 is sole owner; I only *tested* W11's absence claim against the corpus and made no source-index change or proposal).
- Historical worker-status wording inside `metadata/closed-source-and-ownership-map.md` is **not** current live ownership and I did not read it as such.

---

## Method / inputs

- **Live checkout:** `/home/user/Rare-cancers` at `47aac85f…` (differential), read-only; `git ls-files`, `git show`, `git cat-file`, `rg`. No git write operation of any kind.
- **Frozen corpus:** `/tmp/claude-0/frozen-corpus/extracted/` — read in place, **not copied, not overlaid**. Read `README.md`, `metadata/snapshot-provenance.json`, `metadata/tracked-file-map.txt`, and content under `corpus/`.
- **Scratch:** `/tmp/claude-0/w21/` (six sorted path lists). Nothing executed inside the repository.
- **Reports audited:** all 48 files in `research/autonomy/opus-capacity-campaign-20260908/reports/` (20,500 lines).
- **No network.** No paid API, no GPU, no external retrieval, no publication.

---

## Result

### R1 — Three-way file differential (`PRIMARY`)

Keyed to live HEAD `47aac85f…`; corpus base `93b75888…`; map = `metadata/tracked-file-map.txt` (10,566 entries).

| Category | Count | Evidence |
|---|---:|---|
| Corpus total selected files | **5,996** | `find corpus -type f \| wc -l` — matches the manifest |
| Live tracked files at `47aac85f…` | **7,655** | `git ls-files \| wc -l` |
| **(a) present in `corpus/` AND in the live checkout** | **3,795** | `comm -12` |
| **(b) present in `corpus/` but NOT in the live checkout** | **2,201** | `comm -23` |
| **(c) named in `tracked-file-map.txt` but present in NEITHER** | **765** | `comm -23 <(comm -23 map corpus) live` |
| (memo) named in the map, absent from `corpus/`, but present live | 3,805 | 4,570 map-not-in-corpus minus the 765 |

**Characterisation of (b) — 2,201 corpus-only files.** Overwhelmingly working evidence directories that the live tree no longer tracks: `research/autonomy/` 2,080, `research/release-candidates/` 84, `research/manuscripts/` 23, `research/modalities/` 6, `scripts/` 5, `systems/views/` 2, `research/literature/` 1. Largest single clusters: `ipd-empirical-information-2026-09-06` (282), `peerj-validation-audit-2026-09-07` (127), `ipd-prefix-propagation-2026-09-07` (105), `ipd-published-baselines-2026-09-06` (98), `atlas-hofvander-validation-2026-09-06` (93), `ipd-information-ablation-2026-09-07` (91), `PUB-SURFACE-TARGETS` (84). By type it is source and record material, not binaries: 1,573 `.json`, 232 `.py`, 156 `.md`, 118 `.txt`, 52 `.xml`, 27 `.tsv`, 26 `.csv`, 10 `.R`, 4 `.jsonl`, 3 `.ps1`. **This is the category that can contradict a report.**

**Characterisation of (c) — 765 files: UNKNOWN, not absent.** I repeat the provenance file verbatim: `"absent_files": "Unknown/unprovided in this selected snapshot. Absence is not evidence of repository-wide absence, source novelty or access permission."` and `"A listing does not prove local availability, inspection, or inclusion."` (c) is dominated by exactly the types a *source*-file selection filter would exclude: 371 `.log`, 127 `.gz`, 44 `.zip`, 44 `.png`, 39 `.html`, 29 `.pdf`, 20 `.response`, 13 `.xlsx`, 13 `.Rd`, 6 `.xls`, 5 `.patch`, 4 `.rda`, 4 `.jpg`, 4 `.gb`, 3 `.npz`. Named examples include `research/manuscripts/external-validation/emc-external-validation-comment.tex` and its `.pdf`/`.zip`, the surface-tissue-RNA figure PDFs/PNGs/SVGs, and `research/manuscripts/nr4a-reagents/nr4a-reagents-emc-perspective-preprint.pdf`. **I inspected none of these, I do not know their contents, and their absence from `corpus/` establishes nothing about them.** Note in particular that the NR4A Perspective preprint falls in (c): it is UNKNOWN and it remains closed regardless.

### R2 — Per-report claim classification

Only claims about **repository content** are testable against the corpus. Claims about the external literature (W07/W07b's toxicity denominator, W04b/W04c's duration harvest, W10c's PubMed route) are **NOT TESTABLE** here and I make no finding on them.

| # | Report | Claim (abridged, quoted) | Verdict |
|---|---|---|---|
| C1 | `W01-expression-multiomics-resources.md:59,136,234,242` | *"Zero `E-MTAB-`, zero `EGAS`, zero `phs` accessions anywhere in the tree — i.e. ArrayExpress/BioStudies, EGA and dbGaP have never been searched or recorded."* | **CONTRADICTED** `PRIMARY` |
| C2 | `W12-windows-portability-defects.md:432` | *"The retained evidence this lane was built around does not exist. The Windows path-separator failure logs are not in the tree — only a prose summary and post-repair PASS logs."* | **CONTRADICTED** `PRIMARY` |
| C3 | `W08-disease-course-surveillance-question.md:123,133` | *"`research/autonomy/clinical-methods-checkpoints-2026-09-07` does not exist in this checkout … Per the brief that is UNKNOWN, not proof of absence."* | **UNKNOWN RESOLVED — claim was correctly hedged and stands; corpus supplies the directory.** Not a contradiction. `PRIMARY` |
| C4 | `W13-provenance-identity-contract.md:92` | *"No committed file anywhere carries `n_patients`, `n_specimens`, or a `namespace` declaration."* | **CONTRADICTED, but not by the corpus.** See R3. `PRIMARY` |
| C5 | `W11-source-index-integration-contract.md:92`; `W11b:90` | *"No source-index file is tracked at the freeze point"*; *"no basename collision"*; *"No `__init__.py` anywhere"* | **CORROBORATED** — `find corpus -iname '*source*index*' -o -iname '*source_reuse*'` → no output; `find corpus -name '__init__.py' \| wc -l` → `0` `PRIMARY` |
| C6 | `W04-pathology-imaging-resources.md:101,95-100` | *"no prior work exists in this lane"*; *"`rg -i "TCIA"` returned no hit anywhere; `rg -i "whole.slide\|WSI"` returned no hit anywhere."* | **CORROBORATED** — the one corpus `TCIA` hit is a **false positive inside a protein sequence** (`…NLTLVNVTSEDNGFTLTCIAENVVGMSNASVALTVYYPPRV…`, `nr4a3-program-source-2026-09-07/sources/supp-table1.csv`); all five `WSI`/whole-slide hits are inside fetched journal article text, none an image resource, dataset accession or licence record `PRIMARY` |
| C7 | `W02-singlecell-spatial-microenvironment.md:55` | *"no tracked file records a systematic search for whether [a compartment-resolved EMC measurement] exists."* | **CORROBORATED, with a near-miss noted.** No corpus-only file is a single-cell/spatial **dataset search record**. The nearest thing, `research/autonomy/ngo-emc-source-2026-09-06/result.md` (category b), is a *source-availability* memo for an external mesenchymal RNA panel and states outright: *"The source describes study scRNA-seq and spatial data as EpS. They must not be recast as EMC measurements."* It does not answer W02's question and does not contradict the claim, but a future W02-lane worker should read it. `PRIMARY` |
| C8 | `W06-diagnostic-delay-molecular-confirmation.md:94` | *"What does not exist: any cross-series table of `n_confirmed / n_total`, any era stratification…"* | **CORROBORATED for the cross-series table.** The corpus-only `clinical-methods-checkpoints-2026-09-07/` holds **single-series** primary records (e.g. `paioli-primary-record.json`, "67 localized, surgically treated, molecularly confirmed cases", Italian Sarcoma Group) — a per-series record, not the cross-series table W06 said is missing. `PRIMARY` |
| C9 | `W06b:79` / `W06c:72` | *"no committed analysis in the repository sweeps a contamination parameter"* | **CORROBORATED** — every corpus-only `contamination`/misclassification hit is inside fetched article text (`ctsd2026`, `Zurich2023-fulltext.xml`, `ngo-emc-source article.xml`) or a reader case record, none a committed sweep. `PRIMARY` |
| C10 | `W05:81` / `W13b:74` | *"no file in the tree contains such an [patient-level independence] audit"*; *"no committed file states the unit of any cohort `n`"* | **CORROBORATED** — the corpus-only hits (`atlas-independent-normal-feasibility.*`, `atlas-contribution-audit-2026-09-06.json`) concern *normal-tissue* comparator independence and contribution accounting, not patient-level cohort non-overlap; the single `unit`-shaped corpus-only hit is `atlas-hofvander-validation-2026-09-06/replication-manifest.json`, a replication manifest, not a cohort-unit declaration. `PRIMARY` |
| C11 | `W04b:93` | *"the repository holds zero content on the EMC diagnostic interval"* | **CORROBORATED** — zero corpus-only files match `diagnostic (interval\|delay)\|symptom.to.diagnosis\|time to diagnosis`. `PRIMARY` |
| C12 | Any claim whose relevant path falls in category (c) — 765 files, including the external-validation `.tex`/`.pdf`/`.zip` set, the surface-target figure binaries, and the PUB-SURFACE-TARGETS build/verification logs | — | **UNDETERMINED.** These paths are listed in the map and supplied in neither the corpus nor the live checkout. Nothing about them is established either way. `UNKNOWN` |

### R3 — The one classification that needs a caveat, stated plainly (`PRIMARY`)

W13's C4 claim is **false**, but the corpus is not what falsifies it and I will not credit the corpus with it. All 18 corpus files carrying a whole-word `n_patients` are in category **(a)** — zero are corpus-only. The claim was already falsifiable at W13's own declared freeze point: `git show 92abbcb905cacf07f14b238db50d1b98f6590374:research/modalities/emc_ipd_survival.py | grep -c "n_patients"` → `1`. The corpus **corroborates the falsity** and adds nothing new. Per this lane's binding constraint ("a locally absent prior report is not source novelty," and its converse), this is a live-tree finding, not a corpus discovery, and I flag it as such so no one records it as corpus-derived. It is nonetheless a real defect in a completed report and is drafted below.

### R4 — What the corpus does NOT change

Of 168 candidate absence/novelty lines across 48 reports, the corpus contradicts **two** (C1, C2), corroborates **eight** clusters (C5–C11 plus W11b), resolves **one** correctly-hedged UNKNOWN (C3), surfaces **one** pre-existing live-tree error it did not itself find (C4), and leaves everything touching category (c) **UNDETERMINED**. The great majority of this campaign's absence claims are unchanged. Notably, every claim whose scope was written as *"in this checkout"* or *"at the freeze point"* survives intact; the two that broke were written as claims about the world (*"anywhere in the tree"*, *"does not exist"*).

### R5 — Focused corrections for the CONTRADICTED claims

Per `CORPUS-CONTEXT.md` item 4 these are **focused corrections to be appended**, not a new review round. Completed outputs are preserved; W01 and W12 are not reopened.

> **Correction to `W01-expression-multiomics-resources.md` (claim at L59, restated at L136, L234, L242).**
> W01's Prior-work check states *"Zero `E-MTAB-`, zero `EGAS`, zero `phs` accessions anywhere in the tree — i.e. ArrayExpress/BioStudies, EGA and dbGaP have never been searched or recorded."* The frozen corpus contradicts this: 31 files carry such accessions, 20 of them absent from the live checkout, including a complete ArrayExpress retrieval set at `research/autonomy/tempo-prostate-source-2026-09-06/` (`E-MTAB-12593.idf.txt`, `E-MTAB-12593-retrieval.json`, `E-MTAB-12593-files-retrieval.json`) — an ArrayExpress query that was in fact run and recorded. The "never been searched" inference must be withdrawn; the underlying route-bounded negative (four archive endpoints returned proxy 403 **this session**) is unaffected and stands. Note separately that the accession count was also non-zero at W01's own declared freeze point (`git show 92abbcb…:research/modalities/emc-atr-vulnerability.json` contains `E-MTAB-783`, `E-MTAB-3610`, `EGAS00001000978`), so the grep as reported did not match its stated scope.

> **Correction to `W12-windows-portability-defects.md` (Limitations, L432).**
> W12 states *"The retained evidence this lane was built around does not exist. The Windows path-separator failure logs are not in the tree."* True of W12's checkout, but the frozen corpus holds that evidence at snapshot base `93b75888…`: `research/autonomy/peerj-validation-audit-2026-09-07/validation/windows-platform-outcome.json` records a real Windows full-mode run at 97 failed / 8,303 passed / 51 skipped with a `representative_diagnosis` naming *"separator-specific scanner comparison"* among four actual platform errors, and `validation/full-windows-manuscripts-partial.txt` is the raw pytest failure log for that run (alongside `full-windows-platform-stop.json`). All three are category (b) — corpus-only. The sentence should be narrowed to "not in this checkout"; W12's own empirically measured Linux findings are untouched and remain the report's result.

> **Correction to `W13-provenance-identity-contract.md` (Prior-work check, L92) — source-flagged.**
> W13 states *"No committed file anywhere carries `n_patients`, `n_specimens`, or a `namespace` declaration."* Eighteen files carry a whole-word `n_patients`, including `research/manuscripts/aso_coverage_ladder.py`, `research/manuscripts/emc_terminal_events.py` and `research/modalities/emc_ipd_survival.py`. **This correction is not corpus-derived** — all 18 are present in the live checkout and the claim was already false at W13's declared freeze point (`git show 92abbcb…:research/modalities/emc_ipd_survival.py | grep -c "n_patients"` → `1`). The corpus adds no corpus-only counterexample. W13's substantive gap finding (no *declared cohort-unit namespace*) may well survive; only the categorical "no committed file anywhere" wording is wrong.

### R6 — Brenca material in the corpus: DUPLICATE, not a discovery (`SECONDARY`)

`grep -rlI -i "brenca" corpus/` returns files under `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` (including `sources/brenca-article.xml`) and four `review-seats/` citation records. Per this lane's binding constraint I record this as **DUPLICATE**: it is not a discovery, I report **no accession**, and it supports **no cohort, independence or patient claim**. It changes nothing in `W01b-brenca-accession-recovery.md` or `W01d-urbini-brenca-nesting.md`, whose closures stand, and the Brenca case-identity gate stays closed. I did not open the article file.

---

## Validation evidence

All `RUN`, all read-only, all outside the repository except read-only `git`/`rg` against it.

**Environment:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Claude Code 2.1.42, no network used.

```
$ cd /home/user/Rare-cancers && git rev-parse HEAD
47aac85f874a57a6f981c3432abcf16980968aec                                   # exit 0 (start)
7d081218f107363573573e6d102e4334567adf77                                   # exit 0 (end; coordinator committed mid-run)
$ git status --porcelain | wc -l
0                                                                          # exit 0 — I wrote nothing
$ git cat-file -t 93b75888e31976195145e2404373b2d7a512f6d1
fatal: git cat-file: could not get object info                             # exit 128 — corpus base NOT verifiable locally
$ git cat-file -t 92abbcb905cacf07f14b238db50d1b98f6590374
commit                                                                     # exit 0
```

```
$ (cd /tmp/claude-0/frozen-corpus/extracted/corpus && find . -type f | sed 's|^\./||' | sort) > corpus-files.txt
$ awk -F'\t' '{print $2}' .../metadata/tracked-file-map.txt | sort -u > map-files.txt
$ (cd /home/user/Rare-cancers && git ls-files | sort) > live-files.txt
$ wc -l corpus-files.txt map-files.txt live-files.txt
   5996 corpus-files.txt
  10566 map-files.txt
   7655 live-files.txt
$ comm -12 corpus-files.txt live-files.txt | wc -l          # (a)
3795
$ comm -23 corpus-files.txt live-files.txt | wc -l          # (b)
2201
$ comm -23 <(comm -23 map-files.txt corpus-files.txt) live-files.txt | wc -l   # (c)
765
```
exit 0 throughout.

```
$ cd .../corpus && grep -rhoI -E "E-MTAB-[0-9]{3,5}|EGAS[0-9]{8,12}|phs[0-9]{6}" . | sort | uniq -c | sort -rn | head
     46 E-MTAB-12593
     16 phs003305
     11 E-MTAB-9875
      6 EGAS00001002795
      4 E-MTAB-15661
      4 E-MTAB-13948
      3 EGAS00001002920
      3 EGAS00001000855
      3 EGAS00001000839
      2 phs000720
$ grep -rlI -E "E-MTAB-...|EGAS...|phs..." . | wc -l   →  31
$ comm -12 acc-files.txt b-corpus-not-live.txt | wc -l →  20        # corpus-only, i.e. new
$ git show 92abbcb...:research/modalities/emc-atr-vulnerability.json | grep -oE "EGAS[0-9]{8,12}|E-MTAB-[0-9]{3,5}"
E-MTAB-783
E-MTAB-3610
EGAS00001000978                                                            # exit 0
```

```
$ head -c 700 .../corpus/research/autonomy/peerj-validation-audit-2026-09-07/validation/windows-platform-outcome.json
{
  "utc": "2026-09-07T22:47:28.943372+00:00",
  "candidate": "9759f8dc48cb959d5c141e9b3af2ccbb26c3ceb2",
  "scope": "Full-mode Windows run stopped after actual97failed8303passed51skipped modality result, ...",
  "full_pass": false,
  "representative_diagnosis": "Four actual platform errors: Unix strftime flags, separator-specific
                               scanner comparison, signal.alarm absent, direct shell-script
                               CreateProcess invalid binary. This sample does not diagnose all97.",
  ...
}                                                                          # exit 0
$ head -8 .../validation/full-windows-manuscripts-platform... (full-windows-manuscripts-partial.txt)
bringing up nodes...
........................................................................ [  3%]
......F..................................................F.............. [ 21%]
.................................................................F..F... [ 47%]                     # exit 0
```

```
$ cd .../corpus && find . -iname '*source*index*' -o -iname '*source_reuse*'
                                                    (no output)           # exit 0 — C5 corroborated
$ find . -name '__init__.py' | wc -l
0                                                                          # exit 0
$ ls -d .../corpus/research/autonomy/clinical-methods-checkpoints-2026-09-07
research/autonomy/clinical-methods-checkpoints-2026-09-07                  # exit 0 — C3 resolved
$ grep -o -i ".\{40\}tcia.\{40\}" .../nr4a3-program-source-2026-09-07/sources/supp-table1.csv
WIVTGLQSINTHQTNLNWTNVHAINLTLVNVTSEDNGFTLTCIAENVVGMSNASVALTVYYPPRVVSLEEPELRLEHCIEFVVR
                                                # exit 0 — protein sequence; C6 stands
```

**`PROPOSED (NOT RUN)`:** nothing. I proposed and ran no test I did not execute, and I authored no acceptance criterion.

---

## Limitations

- **The differential is keyed to live HEAD `47aac85f…`, which moved to `7d081218…` during my run.** Category counts (a)/(b)/(c) are exact for `47aac85f…` and approximate for any later HEAD. The campaign brief's declared freeze commit `92abbcb…` is a third, different commit; I used it only for the two targeted `git show` checks, which are exact.
- **I cannot verify the corpus against Git.** Base `93b75888…` is not in the local object store and there is no network. I rely entirely on the coordinator's recorded hash verification in `CORPUS-CONTEXT.md`; I re-verified no checksum myself.
- **Category (c) is UNKNOWN, not absent** — repeating the provenance file: *"Absence is not evidence of repository-wide absence, source novelty or access permission."* My reading that (c) looks like a binary/log/archive selection filter is an **inference from file extensions**, not a statement from the provenance file, and it does not upgrade any (c) path from UNKNOWN.
- **Absence from this snapshot is not repository-wide absence, source novelty, or access permission.** Every CORROBORATED verdict above means only "also absent from this selected snapshot," never "does not exist."
- **A locally absent prior report is not source novelty**, and conversely the corpus-only files I found are prior *repository work*, not new *source material* — the provenance file records `"no_new_source_material": true`, `"no_source_fetch": true`, `"no_scientific_acceptance": true`.
- **Claim extraction is regex-seeded and non-exhaustive.** 168 candidate lines over 20,500; a novelty claim phrased outside my pattern set would be missed. My verdicts cover 12 claim clusters, not all 168 lines.
- **Literature-absence claims are NOT TESTABLE against a repository corpus** and I made no finding on them. W07's already-refuted toxicity claim is W07b's finding and W09b's report; it is not mine and is not corpus-derived.
- **No clinical claim.** This is a provenance audit. Nothing here bears on EMC biology, NR4A3 fusion behaviour, degrader efficacy, safety, selectivity, therapeutic window, or clinical readiness, and no result here admits any cohort, patient, or independence claim.
- **Closures untouched.** Nothing here reviews, recreates, reroutes or reframes the blocked NR4A Perspective; nothing reopens PUB-EMC-CLASSIFICATION; the Brenca material is DUPLICATE. No content-policy refusal was encountered in this run.

---

## Stop condition

Set: *three-way differential with counts, per-report claim classification, and a focused correction drafted for every CONTRADICTED claim.*

**MET.** (a)=3,795 / (b)=2,201 / (c)=765 reported and characterised, with (c) explicitly labelled UNKNOWN. Twelve claim clusters across 48 reports classified: **2 CONTRADICTED by the corpus** (W01, W12), **8 CORROBORATED**, **1 correctly-hedged UNKNOWN resolved** (W08), **1 contradicted by the live tree rather than the corpus and flagged as such** (W13), and everything touching category (c) **UNDETERMINED**. Focused corrections drafted for all three defective claims. Returning now.

---

## Tool-call and wall-clock count actually used

**23 tool calls**, all `Bash`. **Wall clock 4 min 02 s measured** (`02:31:35Z` → `02:35:37Z`), plus context reading before the first timestamp. Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**One successor, bounded and cheap: apply the two corpus-derived focused corrections (W01, W12) and the one source-flagged correction (W13) as appended blocks, then re-run this differential against the coordinator's current HEAD.** The corrections are drafted verbatim above and need no retrieval, no network and no new analysis — only a coordinator write, since every worker is read-only. The re-run matters because HEAD moved during my four minutes (`47aac85f…` → `7d081218…`), so category (a)/(b) membership is already slightly stale; the same six `comm` commands regenerate it in seconds.

**Explicitly not a successor, and I recommend against it:** promoting any category-(c) path to a finding, and re-testing the literature-absence claims — the first is barred by the provenance file, the second needs retrieval this sandbox does not have.
