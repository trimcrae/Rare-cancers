> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W21b** — corpus-differential lane, second pass, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable observed names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at **start**: `Tue Sep  8 02:46:53 UTC 2026`
`date -u` at **end**: `Tue Sep  8 02:51:07 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim; the same command at end returned the same set):

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

**Actual HEAD read:** `git rev-parse HEAD` → `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` at start **and** at end (stable across my run — unlike W21's, which moved). This is neither the brief's declared freeze `92abbcb…` nor W21's `47aac85f…`/`7d081218…`.

`git status --porcelain` → **empty (0 lines) at start and at end.** I wrote nothing into `/home/user/Rare-cancers`. All execution and all scratch files under `/tmp/claude-0/w21b/`. No git write operation. No network. No paid API, no GPU, no MCP call.

---

## Question

**Do the 36 campaign reports collected after W21 ran carry any novelty or absence claim that the frozen corpus contradicts?**

Open because W21's differential covered the 48 reports present at `47aac85f…`; the collected set has since grown to 85, and none of the 37 additions has been tested against the corpus — with one exception I found and credit below (W15e tested its own claim against the corpus and is right).

---

## Prior-work check

Commands run (all read-only, exit 0):

```
$ ls research/autonomy/opus-capacity-campaign-20260908/reports | wc -l          → 85
$ git ls-tree --name-only 47aac85f874a57a6f981c3432abcf16980968aec .../reports/ → 48
$ comm -13 w21-covered.txt now.txt | wc -l                                      → 37
```

**W21's 48 covered reports** (verbatim, from `git ls-tree` at W21's own start HEAD `47aac85f…`):
`W01`, `W01b`, `W01c`, `W01d`, `W02`, `W02b`, `W02c`, `W03`, `W03b`, `W04`, `W04b`, `W04c`, `W05`, `W05b`, `W05c`, `W06`, `W06b`, `W06c`, `W07`, `W07b`, `W08`, `W08b`, `W08c`, `W09`, `W09b`, `W10`, `W10b`, `W10c`, `W11`, `W11b`, `W12`, `W13`, `W13b`, `W14`, `W15`, `W15b`, `W15c`, `W16`, `W16b`, `W17`, `W17b`, `W17c`, `W19`, `W19b`, `W19c`, `W20`, `W20b`, `W20c` (full filenames as listed in `reports/`).

**New since W21 — 37 files**, of which I audited **36** (I exclude `W21-corpus-differential-audit.md` itself as the prior work I am extending, not an object of audit):
`W01e`, `W02d`, `W03c`, `W03d`, `W05d`, `W06d`, `W07c`, `W07d`, `W08d`, `W08e`, `W09c`, `W09d`, `W10d`, `W10e`, `W11c`, `W11d`, `W12b`, `W12c`, `W13c`, `W13d`, `W13e`, `W14b`, `W14c`, `W15d`, `W15e`, `W16c`, `W17d`, `W17e`, `W17f`, `W17g`, `W18`, `W19d`, `W20d`, `W20e`, `W22`, `W23` (+ `W21` excluded).

**I re-audited none of W21's 48.** W21's verdicts (2 CONTRADICTED — W01, W12; 8 CORROBORATED; 1 UNKNOWN-resolved — W08; 1 live-tree contradiction — W13) stand unchanged and I did not retest them.

`CLOSED-WORK.md` read in full. Not replayed, re-reviewed or relabelled: the blocked NR4A Perspective refusal (not approached under any label); the user-rejected registry ICD-O paper; Davis/Hofvander/promoter-transfer/inverse-bounds closures; every unrecovered source (I fetched nothing); the lane-11 source-index bundle (I tested absence claims only, proposed no source-index change). Per my binding instruction the Brenca accessions `PRJNA692081` / `SRP301712` are **already recovered → DUPLICATE, never novelty**; I report them only as a scope check on W01e and draw no cohort, patient or independence conclusion.

---

## Method / inputs

- **Live checkout** `/home/user/Rare-cancers` at `3f5fc95d…`, read-only (`git ls-files`, `git ls-tree`, `grep`, `sed`).
- **Frozen corpus** `/tmp/claude-0/frozen-corpus/extracted/` — read **in place**, not copied, not overlaid; `corpus/` (5,996 files) and `metadata/tracked-file-map.txt`.
- **Scratch** `/tmp/claude-0/w21b/` — six path lists (`corpus-files.txt` 5,996; `live-files.txt` 7,692; `corpus-only.txt` 2,201; `w21-covered.txt` 48; `new-reports.txt` 37; `claims.txt` 69).
- **Claim pool:** one regex sweep over the 36 new reports → **69 candidate lines in 26 files**; 10 reports carried no matching line.
- No network, no retrieval, no external source.

---

## Result

### R0 — A standing fact in my own dispatch is wrong, and I must say so before anything else (`PRIMARY`)

My dispatch states that `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` "is absent from both this checkout and the frozen corpus". **The checkout half is true; the corpus half is false.** The directory is present in the frozen corpus as **13 corpus-only files**:

```
$ grep "nr4a3-patient-junction-source-2026-09-07" corpus-files.txt        → 13 files
research/autonomy/nr4a3-patient-junction-source-2026-09-07/README.md
  ├ brenca-origin-gate.csv, compare_published_calls.py, coordinator-verification.json
  ├ delite-model-metadata.csv, published-call-comparison.json, recover.py, retrieval.json
  └ sources/{brenca-article.xml, brenca-ena-runs.tsv, brenca-project.xml,
             delite-article.xml, urbini-article.xml}
$ grep -c "nr4a3-patient-junction" corpus-only.txt                        → 13  (none in live tree)
$ ls research/autonomy | grep -i junction                                 → (no output, exit 1)
```

W21's R6 already recorded corpus Brenca material under this exact path. W21 was right; the "absent from the corpus" wording is not.

### R1 — Verdict table, 36 new reports (`PRIMARY` unless marked)

| # | Report `file:line` | Claim (quoted, abridged) | Verdict |
|---|---|---|---|
| N1 | `W23-cross-output-synthesis-packet.md:223` | *"`research/autonomy/nr4a3-patient-junction-source-2026-09-07/` does not exist at the pinned tip `d3e9c4d8…`, and it is **not** in the 5,996-file frozen corpus."* | **CONTRADICTED** — the second half is false; 13 corpus-only files (R0) |
| N2 | `W01e-deposit-classification-rederivation.md:148` | *"The only EGA accession anywhere in the tree is `EGAS00001002795`."* | **CONTRADICTED** — six distinct EGAS accessions exist; four in the **live tree**, two more **corpus-only** (see R2) |
| N3 | `W01e:82` | *"`research/autonomy/nr4a3-patient-junction-source-2026-09-07/` **does not exist at this HEAD** (`ls research/autonomy` confirms)"* and the accessions *"appear **only** in `WAVE-LOG.md:82-84`"* | **STANDING** — correctly scoped to "this HEAD"; I reproduced the live-tree absence exactly. The corpus holds the directory and the accessions, so the sentence must not be re-quoted as a repository-wide absence |
| N4 | `W13c-remaining-cohort-units.md:139,387` | *"The primary, **identified here for the first time** as Giner 2022, [DOI 10.1007/s00428-022-03453-x]"* | **CONTRADICTED, and NOT by the corpus** — the full citation is in the **live tree** at two paths (see R3). The corpus corroborates the falsity and adds the citing chain, but adds no corpus-only counterexample |
| N5 | `W07c-toxicity-fulltext-resolution.md:108,240` | *"No Table 3 counts, no body-text toxicity paragraph, and no apatinib toxicity section exist anywhere in the tree."* | **CORROBORATED** — 44 corpus files mention apatinib; the 16 corpus-only ones are ClinicalTrials.gov registration records (BIOVAS, `emc-pharmacology-identity-2026-09-06`) stating a **safety objective**, holding **no reported toxicity counts and no results section** |
| N6 | `W10d-kawaguchi-hospital-enumeration.md:82` | *"No committed file anywhere enumerates them [the eight affiliated hospitals]."* | **CORROBORATED** — `grep -rlI -i "eight affiliated\|8 affiliated"` over the corpus → exactly one file, `research/literature/rt-lung-mets-probe.json`, which is the live abstract W10d already cites; zero corpus-only enumerations |
| N7 | `W11c-source-index-divergence-adjudication.md:104` | *"`possible_same_deposit`, `PROVENANCE_UNVERIFIED`, `title_candidates` → **no hits anywhere in the tree**."* | **CORROBORATED** — 0 corpus files for each of the three tokens |
| N8 | `W11c:187-188`; `W11d:264,295`; `W23:314,357` | `scripts/source_reuse_index.py`, its test, and all five pytest configs absent | **CORROBORATED** — consistent with W21's C5 (no source-index file, no `__init__.py` in the corpus). Not re-derived beyond confirming no corpus-only source-index file exists |
| N9 | `W15d:214,218`; `W15e:176,340` | *"a `denominator_unit` field does not exist in any committed file"*; *"scanning all four files for any key matching `/unit/i` … returns NONE"* | **CORROBORATED, and W15e tested this itself** — `grep -rl "denominator_unit" corpus/` → **0**. W15e:83 records that same corpus command in its own report; credit is W15e's, not mine |
| N10 | `W15e:83` | *"Three hits [for `denominator_unit`], all inside `W15d`"* — with `denominator_means` separately reported as committed in 16 files | **CORROBORATED** — 11 corpus files carry `denominator_means`, all also-live, consistent with W15e's own count; 0 carry `denominator_unit` |
| N11 | `W16c-bishop2019-admissibility-package.md:217` | *"The registry carries **no institution roster for `ussc2022`**."* | **CORROBORATED** — **zero corpus-only** files mention `ussc2022`; all 14 corpus hits are also-live files W16c read. The corpus supplies no roster |
| N12 | `W16c:172` | *"no committed test pins 94, 259, 88, 326, 36.3 or 27.0"* (eligibility-filtered) | **CORROBORATED** — every corpus test matching those integers is an unrelated modality test (`test_fusion_cofold.py`, `test_pocket_*`, `test_r3_*`); none is corpus-only, none is eligibility-related |
| N13 | `W17e-pub-atr-figure-anchoring.md:192` | *"`emc_model_identity_check` does not exist anywhere in `emc-atr-vulnerability.json` … it lives in `research/modalities/atr-hrd-sarcoma-series.json`"* | **CORROBORATED** — 12 corpus files carry the token; `atr-hrd-sarcoma-series.json` is among them, `emc-atr-vulnerability.json` is not |
| N14 | `W23:195` | *"no `.bed` is tracked anywhere"*; *"every `jaccard` hit in the tree is unrelated"*; *"No pairwise comparison between GSE243553 peaksets exists anywhere in the repository."* | **CORROBORATED, with one addition W23 could not have enumerated** — 0 `.bed` files in the corpus and 0 in `tracked-file-map.txt`; the corpus adds **six corpus-only `jaccard` files**, of which `research/autonomy/nr4a3-program-tissue-2026-09-07/` is a further **gene-set** Jaccard (`analyze.py:192` computes program-membership set overlap), not a peakset comparison. The claim survives; its enumeration of "unrelated jaccard hits" is now incomplete by one cluster |
| N15 | `W08e-adjudication-sensitivity.md:119,285`; `W13e:90`; `W10e:43,218` | *"`W08d-*.md` does not exist on disk at HEAD `47aac85` … and [not in] the frozen corpus"*; *"`W13d-*.md` … no hits anywhere on the filesystem, including the frozen corpus"*; *"`W10d-*.md` does not exist on disk"* | **CORROBORATED at the time; now superseded by collection** — `grep -rlI "W08d" corpus/` → 0; `"W13d"` → 0. All three reports **now exist** in `reports/` at `3f5fc95d…`. Their SECONDARY/TRANSFERRED markings were correct when written and remain the right label for what those workers actually read |
| N16 | `W08d:273`; `W16c:221`; `W20e:218`; `W03c:75` | route-exhaustion and NOT-RUN statements (*"not reachable by any permitted route", not "does not exist"*) | **STANDING — correctly scoped, nothing to test.** These are the model of how to phrase an absence |
| N17 | `W12b:68`; `W15d:65`; `W19d:69`; `W20d:259`; `W14c:409`; `W16c:124,265`; `W13c:6` | write-isolation statements (`git status --porcelain` clean of the worker's own paths) | **NOT TESTABLE against the corpus** — session facts, no finding made |
| N18 | `W07d:79,94`; `W07c:298`; `W23:80`; `W09d:205`; `W11c:84,296`; `W11d:179,317`; `W14b:511`; `W15d:367,377` | lane-scoped or proposal-scoped statements (*"never been tested"*, *"tests that do not exist"*, *"never been audited by this lane"*) | **NOT TESTABLE / STANDING** — each is scoped to a lane, a proposal, or an unwritten test, and a repository corpus cannot refute it |

**Totals over 36 new reports: 3 CONTRADICTED (N1, N2, N4 — of which N4 is a live-tree contradiction, not a corpus one), 11 CORROBORATED, and the remainder STANDING or NOT TESTABLE.**

### R2 — Corpus and live evidence for N2, quoted (`PRIMARY`)

```
$ cd /tmp/claude-0/frozen-corpus/extracted/corpus && grep -rhoI -E "EGAS[0-9]{8,12}" . | sort | uniq -c | sort -rn
      6 EGAS00001002795     3 EGAS00001002920     3 EGAS00001000855
      3 EGAS00001000839     1 EGAS50000000393     1 EGAS00001001178     1 EGAS00001000978
```

Live-tree carriers (present in `/home/user/Rare-cancers` at `3f5fc95d…`, so W01e's own grep did not match its stated scope):
`research/modalities/atr-hrd-sarcoma-series-inputs.json` → `EGAS00001000839`, `EGAS00001000855`, `EGAS00001001178`; `research/modalities/emc-atr-vulnerability.json` → `EGAS00001000978`.

Corpus-only carriers (genuinely new to W01e), quoted verbatim with path:

> `research/autonomy/zullow-emc-source-2026-09-06/README.md:78-79` — *"Its data availability identifies GSE108028 for cell lines and deidentified NCI synovial-sarcoma RNA, and EGA **EGAS00001002920** for patient-associated MD Anderson synovial and epithelioid sarcoma samples."*

> `research/autonomy/next-paper-2026-09-07/native-cell-source-gate.json` — `"name": "Seitz2026" … "ega_metadata": "https://metadata.ega-archive.org/studies/EGAS50000000393/datasets" … "finding": "89 native specimens/62 patients; no EMC-specific identity recovered."`

**Correct restatement (for the coordinator to append, not a rewrite of W01e):**

> **Correction to `W01e-deposit-classification-rederivation.md` (D4, L148).** The sentence *"The only EGA accession anywhere in the tree is `EGAS00001002795`"* is wrong on both halves of its scope. Four further EGA accessions (`EGAS00001000839`, `EGAS00001000855`, `EGAS00001001178`, `EGAS00001000978`) are in the **live checkout** at `research/modalities/atr-hrd-sarcoma-series-inputs.json` and `emc-atr-vulnerability.json`, so the grep as reported did not match its stated scope; two more (`EGAS00001002920`, `EGAS50000000393`) are **corpus-only**. **D4's substantive finding is unaffected and stands**: neither corpus-only accession is an EMC anchor — `EGAS00001002920` is McBride 2018 synovial/epithelioid sarcoma, and `EGAS50000000393` is Seitz2026 with *"no EMC-specific identity recovered"*. The wording should be narrowed to "no EGA accession in this repository is an EMC-linked deposit", which is what D4 actually established.

> **Correction to `W23-cross-output-synthesis-packet.md` (L223).** *"it is **not** in the 5,996-file frozen corpus"* is false. `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` is present as **13 corpus-only files**, including `README.md`, `retrieval.json`, `published-call-comparison.json` and `sources/{brenca,delite,urbini}-article.xml`. Its README states verbatim: *"The proposed original patient-read study did not pass its access and specimen-identity gate. No raw reads were downloaded or aligned."* and *"The [2021 correction] points to PRJNA692081 / SRP301712. The preserved ENA report has 23 paired libraries, 46 FASTQs and 46,317,317,021 compressed bytes. **This is an access observation, not 23 patients.**"* The correct restatement is: *"absent from the pinned tip `d3e9c4d8…`, but present in the frozen corpus, where I have now read it."* **This does not upgrade W23's item to PRIMARY on its own merits** — the accessions are already recovered and are **DUPLICATE, not novelty**; the directory's own README forbids reading 23 libraries as 23 patients; and no cohort, independence or patient claim follows.

### R3 — Evidence for N4, and why I refuse to credit the corpus with it (`PRIMARY`)

W13c:139 claims Giner is *"identified here for the first time"*. The **live checkout** already carries the full citation, twice:

> `research/manuscripts/endpoint/meta-analysis.md:255` — *"12. Giner F, et al. Extraskeletal myxoid chondrosarcoma: p53 and Ki-67 offer prognostic value for clinical outcome — an immunohistochemical and molecular analysis of **31 cases**. *Virchows Arch.* **2023**. doi:10.1007/s00428-022-03453-x; PMID 36376703."*

> `research/manuscripts/repurposing/repurposing-hypotheses.md:597` — *"8. Giner F, López-Guerrero JA, Machado I, … Llombart-Bosch A. … analysis of **31 cases**. *Virchows Arch.* **2023;482(2):407-417.** doi 10.1007/s00428-022-03453-x. PMID 36376703."*

The corpus corroborates and supplies the citation chain — the PeerJ source article's reference list is **corpus-only**, at `research/autonomy/peerj21497-source-2026-09-06/article.xml`, `ref-18`:

> *`<label>Giner et al. (2023)</label> … <year iso-8601-date="2023">2023</year><article-title>Extraskeletal myxoid chondrosarcoma: p53 and Ki-67 offer prognostic value for clinical outcome—an immunohistochemical and molecular analysis of 31 cases</article-title><source>Virchows Archiv</source><volume>482</volume><fpage>407</fpage><lpage>417</lpage><pub-id pub-id-type="doi">10.1007/s00428-022-03453-x</pub-id><pub-id pub-id-type="pmid">36376703</pub-id>`*

**Correct restatement:**

> **Correction to `W13c-remaining-cohort-units.md` (row `[7]`, L139, repeated in the artifact string at L387) — source-flagged.** *"identified here for the first time"* must be withdrawn: the same work, with the same DOI, PMID and the same *"analysis of 31 cases"* title, is committed in the live checkout at `research/manuscripts/endpoint/meta-analysis.md:255` and `research/manuscripts/repurposing/repurposing-hypotheses.md:597`. **This correction is live-tree-derived, not corpus-derived** — no corpus-only file was needed to falsify it, exactly as W21 flagged for W13. Two secondary points: the year should read **2023** (Virchows Arch 482(2):407-417), not 2022 — `2022` is the DOI suffix from online-first; and W13c's premise that the bibliographic route was closed is narrower than it looks, because the PeerJ article's **full reference list is present in the corpus** at `research/autonomy/peerj21497-source-2026-09-06/article.xml`. **W13c's substantive verdict is untouched**: both the citing sentence and the primary say *"cases"*, not *"patients"*, so row `[7]`'s unit remains **UNKNOWN** and no cohort-unit conclusion changes.

### R4 — What the corpus does not change

Of 69 candidate lines across 36 new reports, the corpus contradicts **one** (N1), contradicts **one** jointly with the live tree (N2), surfaces **one** pre-existing live-tree error it did not itself find (N4), and corroborates **eleven** clusters. The pattern W21 identified holds exactly: **every claim scoped to "this HEAD", "this checkout", "at the freeze point", "by any permitted route", or "by this lane" survived; the three that broke were written as claims about the world** ("anywhere in the tree", "not in the frozen corpus", "for the first time"). W15e is the only new report that pre-emptively tested itself against the corpus, and it was right to.

---

## Validation evidence

All `RUN`, all read-only, all outside the repository except read-only `git`/`grep`/`sed` against it. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Claude Code 2.1.42, Python 3 (used only to slice two XML/JSON files for quoting). No network.

```
$ git rev-parse HEAD                                  → 3f5fc95d806765b8fddf4fbe1dc288c85869fa2d  (start and end, exit 0)
$ git status --porcelain | wc -l                       → 0  (start and end, exit 0)
$ ls .../reports | wc -l                               → 85                                        exit 0
$ git ls-tree --name-only 47aac85f… .../reports/ | wc -l → 48                                       exit 0
$ comm -13 w21-covered.txt now.txt | wc -l             → 37                                        exit 0
$ (cd corpus && find . -type f | sed 's|^\./||' | sort) | wc -l   → 5996                            exit 0
$ (git ls-files | sort) | wc -l                        → 7692                                       exit 0
$ comm -23 corpus-files.txt live-files.txt | wc -l     → 2201   (corpus-only)                        exit 0
$ grep -n -i -E "no prior work|does not exist|anywhere in the (tree|repo)|no committed|…" <36 reports> | wc -l  → 69   exit 0
```

Corpus searches (all `exit 0`; a zero-hit `grep -rl` returns 1 and is reported as 0 files):

```
$ grep "nr4a3-patient-junction-source-2026-09-07" corpus-files.txt | wc -l   → 13
$ grep -c "nr4a3-patient-junction" corpus-only.txt                            → 13
$ ls research/autonomy | grep -i junction                                     → (no output, exit 1)
$ grep -rlI "possible_same_deposit" corpus/ | wc -l                           → 0
$ grep -rlI "PROVENANCE_UNVERIFIED" corpus/ | wc -l                           → 0
$ grep -rlI "title_candidates" corpus/ | wc -l                                → 0
$ grep -rlI "denominator_unit" corpus/ | wc -l                                → 0
$ grep -rlI "denominator_means" corpus/ | wc -l                               → 11   (all also-live)
$ grep -rlI "W08d" corpus/ | wc -l                                            → 0
$ grep -rlI "W13d" corpus/ | wc -l                                            → 0
$ grep -ci '\.bed$' corpus-files.txt                                          → 0
$ grep -ci '\.bed'  metadata/tracked-file-map.txt                             → 0
$ grep -rlI -i "eight affiliated\|8 affiliated" corpus/                       → research/literature/rt-lung-mets-probe.json  (1, also-live)
$ grep -rlI "ussc2022" corpus/ | (filter to corpus-only)                      → 0 corpus-only
$ grep -rlI -i "apatinib" corpus/ | wc -l                                     → 44   (16 corpus-only, all trial registrations)
$ grep -rlI "emc_model_identity_check" corpus/ | wc -l                        → 12   (atr-hrd-sarcoma-series.json yes; emc-atr-vulnerability.json no)
$ grep -rhoI -E "EGAS[0-9]{8,12}" corpus/ | sort | uniq -c                    → 7 distinct, counts in R2
$ grep -rhoE "EGAS[0-9]{8,12}" research/ systems/ scripts/ | sort -u          → 6 distinct in the live tree
```

**`PROPOSED (NOT RUN)`:** nothing. I ran no test I did not execute, authored no acceptance criterion, and ran no repository gate (`scripts/preflight.sh` not authorised by my dispatch and nothing in the tree was changed).

---

## False-positive discipline (explicitly, as required)

A string match is not a refutation. Of my hits:

**Read and verified by opening the file** (these carry the CONTRADICTED and the load-bearing CORROBORATED verdicts): `nr4a3-patient-junction-source-2026-09-07/README.md` (first 30 lines) and `retrieval.json` (first 25); `peerj21497-source-2026-09-06/article.xml` `ref-18` extracted in full plus the "31 cases" context window; live `meta-analysis.md:255` and `repurposing-hypotheses.md:597` read as complete lines; `zullow-emc-source-2026-09-06/README.md` lines 74-82 with the EGAS context; `next-paper-2026-09-07/native-cell-source-gate.json` EGAS window; `nr4a3-program-tissue-2026-09-07/README.md` (40 lines) and `analyze.py:189-198`; six corpus-only apatinib files inspected via 200-character context windows around each `apatinib` hit.

**Counted but NOT read** — these support only "no corpus-only counterexample exists", never a positive claim about content: the remaining 38 of 44 apatinib files; all 34 `GSE243553` files; all 14 `ussc2022` files; all 14 `Giner` files beyond the four quoted; the 11 `denominator_means` files; the 12 `emc_model_identity_check` files; 80 of the 86 `jaccard` files; the modality test files matched on the bare integers `259`/`326` (I read only their filenames and judged them unrelated on that basis — a weaker check than reading, and I flag it as such). Where I read only a filename, my verdict is "no corpus-only file of this kind", not "no such content anywhere".

**One hit I explicitly declined to promote:** the 16 corpus-only apatinib trial registrations mention safety objectives. That is not a toxicity section and does not refute W07c; calling it one would have been the false positive this section exists to prevent.

---

## Limitations

- **Scope is the 36 new reports only.** W21's 48 are untouched by design; I did not re-verify a single one of W21's verdicts, so if W21 erred, that error is not corrected here.
- **Claim extraction is regex-seeded and non-exhaustive** — 69 candidate lines from ~26 of 36 files; 10 new reports produced no matching line, which means my patterns found nothing there, **not** that they contain no absence claim.
- **Absence from the snapshot is not repository-wide absence.** Every CORROBORATED verdict means only *"also absent from this selected snapshot of 5,996 files"*. Quoting `snapshot-provenance.json`: *"Absence is not evidence of repository-wide absence, source novelty or access permission."*
- **The corpus is not a Git checkout and I verified no checksum myself** — I relied entirely on the coordinator's verification recorded in `CORPUS-CONTEXT.md`. Base `93b75888…` was not tested for local presence in this run.
- **Corpus-only files are prior *repository work*, not new *source material*** — `"no_new_source_material": true`, `"no_source_fetch": true`, `"no_scientific_acceptance": true`.
- **N4 is not a corpus finding** and must not be recorded as one; N2 is half live-tree and half corpus and I separated the two halves rather than crediting the corpus with both.
- **No clinical claim.** This is a provenance audit. Nothing here bears on EMC biology, NR4A3 fusion behaviour, degrader efficacy, safety, selectivity, therapeutic window or clinical readiness, and no result admits any cohort, patient or independence claim. The Brenca accessions remain **DUPLICATE**; the junction-source directory's contents are now **PRIMARY only for the two files I actually read**, and SECONDARY where I did not.
- **No content-policy refusal occurred in this run.** Nothing here reviews, recreates, reroutes or reframes the blocked NR4A Perspective.

---

## Stop condition

Set up front: *both report sets stated by filename; every explicit novelty/absence claim in the new reports extracted with `file:line` and tested by literal corpus search; verbatim corpus evidence plus a correct restatement drafted for each CONTRADICTED claim; false-positive discipline stated.*

**MET.** 48 covered / 37 new stated by filename (36 audited, W21 itself excluded and why). 69 claim lines extracted, classified into 18 clusters: **3 CONTRADICTED** (N1 corpus-derived, N2 mixed, N4 live-tree-derived and flagged as such), **11 CORROBORATED**, the rest STANDING or NOT TESTABLE. Three corrections drafted verbatim for the coordinator to append. One dispatch-supplied "standing fact" found to be false and reported (R0). Returning now.

---

## Tool-call and wall-clock count actually used

**16 tool calls**, all `Bash`. **Wall clock 4 min 14 s measured** (`02:46:53Z` → `02:51:07Z`), plus context reading before the first timestamp. Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**Append the three drafted corrections (W01e D4, W13c row `[7]`, W23 L223) and fix the campaign's own standing-fact text about the frozen corpus**, which currently asserts that `nr4a3-patient-junction-source-2026-09-07/` is absent from the corpus when 13 corpus-only files are present. That text is being handed to workers in dispatch prompts, so the error propagates: W23:223 already repeated it. The correction needs no retrieval, no network and no new analysis — only a coordinator write, since every worker is read-only.

**Explicitly not a successor, and I recommend against it:** re-auditing W21's 48, and treating the newly-readable junction-source directory as a scientific opening. The first is a repeat; the second is barred — the accessions are already recovered (DUPLICATE), the directory's own README records that its access-and-identity gate was **not passed**, and reading 23 ENA libraries as 23 patients is the exact inference it forbids.
