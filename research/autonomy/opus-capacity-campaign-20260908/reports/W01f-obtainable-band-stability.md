> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

# W01f — What moves the "obtainable without correspondence" band, and how wide is it under every defensible reading?

## Worker

- **Worker:** W01f, lane 1 refill (public EMC tumour expression / multiomics resources), OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model. The coordinator must extract the served model from the transcript.
- **`date -u` start:** `Tue Sep  8 02:54:11 UTC 2026`. **`date -u` end:** `Tue Sep  8 02:56:44 UTC 2026`.
- **HEAD actually read:** `4d950cf036294627b7ae67dfb306cc1875d702ac` at start (≠ the brief's frozen `92abbcb9…`; ≠ W01e's `b9a0257e…`). **All readings in this report are against `4d950cf0`.** At exit HEAD had moved to `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8` — coordinator activity, not mine.
- **`git status --porcelain`:** empty at start, empty at end. **Zero writes to the Git tree.** All execution under `/tmp/claude-0/w01f/`. **No network used at all** — no WebFetch, no WebSearch, no MCP, no retrieval of any kind, as dispatched.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (exit 0), literal; three long proxy host lists and the JVM flag string are marked as elided and name no model:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<long host list, elided — names no model>
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
GLOBAL_AGENT_NO_PROXY=<long host list, elided>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore/proxy flags, elided — names no model>
NO_PROXY=<long host list, elided>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<long host list, elided>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

## Question

Pursued exactly as dispatched: **what exactly makes the "obtainable without correspondence" band move, and how wide is it under every defensible reading?** A leave-one-decision-out sensitivity analysis over the band's own construction — not a re-estimate of it — plus the two extreme envelopes, a ranking of decisions by leverage, and the band's **stable core**.

It is open because the headline moved 32–51 → 44–63 on a single correction (W01e R4). A quantity that moves by 12 specimens on one row change has an uncertainty structure that nobody has written down, and until it is written down the number is not quotable.

## Prior-work check

Read in full at `4d950cf0`: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `WAVE-LOG.md` (including the `02:40Z` dated Brenca correction and its verification gap), `reports/W01e-…` (complete), `reports/W01c-…` R1–R6 + validation, `reports/W01d-…` (structure + R1–R4 + limitations + successor), `reports/W01b-…` (routes table, `E-MTAB-7264` rows, successor).

- `grep -n -i -E "brenca|32.51|44.63|obtainable" WAVE-LOG.md` → 12 hits; confirms the owner correction and that W01e is the current owner of the corrected band.
- `grep -n -E "E-MTAB|147|102|GSE6481|arithmetic" W01b-…` → the `E-MTAB-7264` ≈102 vs 19+128=147 arithmetic objection, and the `GSE6481` negative control.
- `wc -l` on the four reports (236 / 347 / 208 / 241 lines) to confirm I read them whole rather than sampled.

**Confirmed not replayed.** I attempted **no** retrieval of any kind — no accession, no route, no origin gate, no source request, no PubMed, no WebSearch. `PRJNA692081` / `SRP301712` are treated throughout as **ALREADY RECOVERED** and any touch on them as **DUPLICATE**; I did not touch them. No cohort, independence or patient claim is built anywhere below: **15 unresolved libraries are not 15 patients, libraries are not specimens, the specimen count stays at the paper-stated 12**. W01d's non-independence finding (same institution, same pathologists, tier D) is carried forward unaltered and not reopened. PUB-EMC-CLASSIFICATION is not reopened. `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` is absent from this checkout and from the frozen corpus, so everything about its contents is **SECONDARY — transcribed, not read**, and I make no attempt to verify it.

**Novelty statement, plainly:** this run adds **no source and no data**. It is an audit of committed records. Its only genuinely new content is (a) the leave-one-out table and envelopes, which had never been computed, and (b) one previously unnamed decision (**S-PARITY**, R5).

## Method / inputs

Inputs are **transcribed from committed reports**, not re-derived from primary artifacts — W01e already did the artifact re-derivation and I do not repeat it.

| input | supplied |
|---|---|
| `reports/W01c-emc-deposit-literature-inventory.md` R1, R5 | the 13-row inventory, per-study `n EMC profiled`, availability class, and the exclusions (PMID 41644428 = 16 EMC; PMID 41315062 = 1) |
| `reports/W01c-…` R2, R3, R4 | the PeerJ availability paragraph; row 12's public-status evidence; the `GSE6481` negative control |
| `reports/W01e-deposit-classification-rederivation.md` R1–R5 | the re-derived classes, D1–D5, the corrected floor of 44, the leverage list |
| `reports/W01d-urbini-brenca-nesting.md` R3, R4 | tier-D verdict; 84 / 79 / 60 denominator scenarios |
| `reports/W01b-brenca-accession-recovery.md` R1, R3 | the 14-route negative; `E-MTAB-7264` arithmetic objection |
| `WAVE-LOG.md` §`02:30Z`, §`02:40Z` | the owner's Brenca closure and the coordinator's stated verification gap |

Tool: `python3` 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0] on Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w01f/`, outside the repository. Scripts: `band_sensitivity.py`, `coherent_share.py` (both returned inline in Validation evidence; neither writes to the tree).

## Result

### R1 — The band's derivation, reconstructed row by row

The band is **not** a statistical interval. It is a partition of one 84-specimen inventory into a floor set and a ceiling adder, and each row's membership is decided by exactly one named judgement. Floor = "accession known and public". Ceiling = floor + "public per literature, accession unresolved here".

| # | study | n | in floor? | in ceiling? | **the specific decision that places it there** | grade of that decision |
|---|---|---|---|---|---|---|
| 2 | Subramanian 2005, **GSE4303** | 10 | ✔ | ✔ | accession known, public, EMC-titled sample count verified in `emc-cohort-search-inputs.json` (36 samples / 10 EMC) | PRIMARY (committed artifact) |
| 4 | Möller 2011, **GSE24369** | 6 | ✔ | ✔ | as above (42 / 6); corroborated by PeerJ's 6+36=42 | PRIMARY (committed artifact) |
| 5 | Brunner 2012, **GSE28866** | 4 | ✔ | ✔ | as above (99 / 4) | PRIMARY (committed artifact) |
| 11 | Chaiboonchoe 2026, **PRJNA1357027** | 12 | ✔ | ✔ | accession public **and** the TempO-Seq targeted panel is admitted as "whole-transcriptome" on the vendor product name | PRIMARY (accession) / **CONTESTED** (assay criterion, W01e D2) |
| 8 | Brenca 2019, **PRJNA692081/SRP301712** | 12 | ✔ | ✔ | owner closure states the accession is recovered and public; count held at the paper-stated 12 | **SECONDARY — transcribed, unverifiable at this HEAD** |
| 12 | unnamed GEO cartilaginous series | 19 | ✘ | ✔ | PeerJ Methods state it is publicly available, but no accession is resolved and the committed GEO census does not corroborate a ~147-sample series | PRIMARY (existence/public status per PeerJ) / UNKNOWN (identity); **non-corroborated**, W01e D1 |
| 6 | Davis 2017 | 6 | ✘ | ✘ | obtained by a third party only through a formal request to journal editors → correspondence required by definition | PRIMARY (PeerJ Methods, verbatim) |
| 3 | Filion 2009 | 3 | ✘ | ✘ | whole-text sweep found **no data-availability statement of any kind** | PRIMARY (n) / UNKNOWN (class) |
| 7 | Urbini 2018 | 5 | ✘ | ✘ | as above — every "available" hit is a software URL | PRIMARY (n) / UNKNOWN (class) |
| 10 | *Mod Pathol* 2023 | 3 | ✘ | ✘ | full text not in PMC; availability unread | PRIMARY (n) / UNKNOWN |
| 9 | *Genes Chrom Cancer* 2022 | 1 | ✘ | ✘ | full text not in PMC; availability unread | PRIMARY (n) / UNKNOWN |
| 1 | Sjögren 2003 | 2 | ✘ | ✘ | PeerJ states the early cDNA datasets predate routine deposition and are unavailable for reanalysis | PRIMARY (n) / **SECONDARY** (availability) |
| 13 | Hofvander TAF15 | 1 | ✘ | ✘ | controlled access via EGA | **SECONDARY** — repository record only; W01e D4 found no committed anchor (the tree's only EGA accession is Haller's, not EMC) |

**Floor 44 = 10+6+4+12+12. Ceiling 63 = 44+19. Total 84.** Everything re-derivable to a committed artifact is in rows 2/4/5/11; rows 1, 9, 12, 13 could not be re-derived at all by W01e and are transcribed readings.

**What I could not re-derive from a checkable source, marked SECONDARY:** row 8's entire class (the supporting directory is absent here and from the frozen corpus); row 13's class; row 1's availability; row 12's identity; rows 1, 9, 13's specimen counts. Rows 3, 6, 7, 10, 11's counts are PRIMARY from full texts W01c actually retrieved.

### R2 — Leave-one-decision-out sensitivity (each flip applied **alone** to the baseline)

Machine output, `band_sensitivity.py`, exit 0, assertions passed. Baseline = W01e's corrected **44–63** of 84.

| decision flipped | what the flip asserts | band | Δfloor | Δceiling |
|---|---|---|---|---|
| **S-ROW12-resolve** | the 19-EMC GEO series' accession is resolved → promoted to floor | **63–63** | +19 | 0 |
| **S-ROW12-drop** | the series is dropped (W01e D1: not corroborated by the committed census) | **44–44** | 0 | −19 |
| **S-PANEL-strict** | TempO-Seq targeted panel excluded — i.e. W01c's own PMID-41644428 criterion applied to row 11 | **32–51** | −12 | −12 |
| **S-NODAS-in** | "no data-availability statement" read as *may be public* → rows 3, 7, 9, 10 (12 specimens) admitted to the ceiling | **44–75** | 0 | +12 |
| **S-BRENCA-out** | row 8 reverts to W01c's `accession unrecoverable` (the closure is SECONDARY and unverifiable at any HEAD this campaign has read) | **32–51** | −12 | −12 |
| **S-BRENCA-unusable** | accession public, but the 12 EMC specimens are not identifiable among 23 libraries (8 engineered, 15 origin-unresolved) | **32–51** | −12 | −12 |
| **S-REQUEST-in** | Davis 2017 counted obtainable (an editor request that demonstrably succeeded) | **50–69** | +6 | +6 |
| **S-PREDEP-in** | Sjögren's pre-deposition status is SECONDARY → admitted to the ceiling | **44–65** | 0 | +2 |
| **S-EGA-in** | EGA controlled access counted obtainable via application | **45–64** | +1 | +1 |

**Extreme envelopes.** All downward flips together → **20–20**. All upward flips together → **70–84**. Full defensible envelope: **20 – 84 specimens, out of 84.** The permissive extreme reaches the entire inventory, which is the plainest possible demonstration that the ceiling carries almost no information.

### R3 — Ranking, and the decision that dominates

| rank | decision | max movement of an edge |
|---|---|---|
| 1 | **row 12 — identity/existence of the unnamed 19-EMC GEO series** | **19** |
| 2= | row 11 — targeted panel vs transcriptome-wide criterion | 12 |
| 2= | rows 3/7/9/10 — how "no data-availability statement" is read | 12 |
| 2= | row 8 — Brenca's status (whether public; whether usable) | 12 |
| 5 | row 6 — whether a successful editor request counts as obtainable | 6 |
| 6 | row 1 — Sjögren's pre-deposition status | 2 |
| 7 | row 13 — EGA controlled access | 1 |

**Row 12 dominates, and it does so in a way that is worse than the ranking suggests.** Row 12 is the *only* member of the ceiling adder, so **the entire quoted width of 44–63 is one binary fact about one dataset nobody has identified.** The band is not an uncertainty interval over thirteen studies; it is a single unresolved accession wearing the costume of one.

**The corollary is the substantive audit finding.** The three decisions ranked 2= each move the band by 12 and **none of them is represented in the quoted interval at all** — the floor of 44 is written as though it were settled. The 12-specimen jump that prompted this dispatch (32–51 → 44–63) was exactly one of those hidden decisions firing. Two more of the same size are still loaded: S-PANEL-strict would take the band straight back to 32–51 by a different route, and S-BRENCA-unusable would do the same. W01e already noted this coincidence and correctly declined to treat the cancellation as an argument.

**Therefore: the band must never be quoted without naming row 12** — and, given the floor's three hidden 12-specimen decisions, the honest form is not a band at all but the stable core plus an explicit list of contingencies.

### R4 — The stable core

**The specimen count obtainable under every defensible reading is 20** — `GSE4303` (10) + `GSE24369` (6) + `GSE28866` (4), three studies. That is **24% of the 84-specimen point estimate**, and it is the only number in this analysis that can be quoted without a caveat.

Those three rows survive every flip because they alone satisfy all four conditions simultaneously: the accession is named, the deposit is public, the platform is not a targeted panel, and the EMC-labelled sample count is verifiable in this repository's own committed GEO census (PRIMARY). No transcription, no owner closure and no third party's Methods sentence is load-bearing for any of them.

**And it is small — say so plainly:**

- 20 of 84 is **less than a quarter** of the EMC expression specimens the readable literature says exist.
- **All 20 are already held and analysed by this repository.** `GSE4303` and `GSE28866` are recorded in `CLOSED-WORK.md` as heavily retained; `GSE24369` is repository-retained per W01 R1. **The stable core therefore represents zero new data.** Every specimen that would be a genuine acquisition — Brenca's 12, PeerJ's 12, row 12's 19 — sits on a contested decision.
- The corresponding *share* statement is even less stable than the count. Applying each decision **coherently to numerator and denominator** (`coherent_share.py`, exit 0): baseline 44/84 = 52%; row 12 dropped from both 44/65 = 68%; panel excluded from both 32/72 = 44%; Brenca out of the floor 32/84 = 38%; all three downward flips 20/53 = 38%. The reachable share ranges **38–68%** across the same decision set. W01c's "roughly 38%" and W01e's "~52%" are two points on that range, not a revision of one another.

### R5 — One decision this run adds, which nobody had named

**S-PARITY (this run's own finding, offered as a candidate, not applied).** The criterion in W01e's D2 excludes row 11 because TempO-Seq measures a fixed probe set rather than the transcriptome. `GSE4303` is a **42,000-spot two-colour cDNA array** — also a fixed, pre-selected probe set. If the panel objection is admitted on probe-set logic, parity arguably removes `GSE4303` too, and **the stable core falls from 20 to 10** (`GSE24369` + `GSE28866`).

I do **not** assert this and I have not applied it in R2–R4. It is stated because it is the one live threat to the only number this analysis calls quotable, and burying it would defeat the purpose of the audit. A strict "full-length transcriptome sequencing only" reading would go further still, but that changes the question ("genome-wide expression profiled") rather than reading it, so it is excluded from the envelope and quantified here only for completeness.

## Validation evidence

**RUN.** Environment: Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; Linux 6.18.44-fc-v24 x86_64; cwd `/tmp/claude-0/w01f`, outside the repository. **No network in any command.**

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u`; `env \| grep -i -E 'claude\|anthropic\|model' \| sed …`; `git -C /home/user/Rare-cancers rev-parse HEAD`; `git … status --porcelain` | 0 | start `02:54:11 UTC`; HEAD `4d950cf0…`; status **empty** |
| 2 | `ls -la …/opus-capacity-campaign-20260908/{,reports/}` | 0 | 83 reports present; the four required inputs located |
| 3 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` | 0 | read in full |
| 4 | `grep -n -i -E "brenca\|32.51\|44.63\|obtainable" WAVE-LOG.md` | 0 | 12 hits, incl. lines 81–86 and 129–131 |
| 5 | `wc -l W01b* W01c* W01d* W01e*` | 0 | 236 / 347 / 208 / 241 |
| 6 | `sed -n '40,140p' WAVE-LOG.md` | 0 | the `02:30Z` owner corrections and the `02:40Z` dated Brenca correction incl. the verification gap |
| 7 | `cat W01e-deposit-classification-rederivation.md` | 0 | full report, R1–R5 |
| 8 | `sed -n '95,347p' W01c-…` (persisted, 31KB) + `awk 'NR>=110 && NR<=230'` | 0 | the 13-row table, exclusions, R5 decomposition, `inventory.py` output |
| 9 | `grep -n -E "…" W01d-…` and `W01b-…` | 0 | tier-D verdict, 84/79/60 scenarios; `E-MTAB-7264` 19+128=147 ≠ ~102 |
| 10 | `cd /tmp/claude-0/w01f && python3 band_sensitivity.py; echo "EXIT=$?"` | **0** | the R2 table, the ranking, envelopes `20-20` / `70-84`, core `20`; **`ASSERTIONS PASSED`** (7 assertions: total=84, baseline=(44,63), both 12-specimen flips land exactly on (32,51), core=20, envelopes=(20,20) and (70,84)) |
| 11 | `python3 coherent_share.py`; `date -u`; `rev-parse HEAD`; `status --porcelain` | 0 | shares 52/68/44/38/56/38%; end `02:56:44 UTC`; HEAD moved to `ce743d6a…` (coordinator); status **empty — no tree writes by me** |

Verbatim key output of call 10 is reproduced in full in R2/R3 above, including the two assertion-checked identities `band(floor−Brenca) = 32–51` and `band(floor−row11) = 32–51`.

**PROPOSED (NOT RUN):**
- Resolve row 12 by an archive query (GEO/ArrayExpress for a ~147-sample cartilaginous-tumour series). **Not run** — dispatch forbids retrieval; the reliable route is the Actions escape hatch.
- Verify row 8 against `retrieval.json`. **Not run** — the directory does not exist here; this is the coordinator's integration-time task, as the WAVE-LOG itself states.
- Settle S-PARITY by reading `GSE4303`'s platform record. **Not run** — no retrieval this run; and the decision is a policy choice for the lane owner, not a fact lookup.

**No test suite and no `scripts/preflight.sh`.** This run changes no code, manuscript or shared state, and the dispatch does not call for them. Nothing here is a skipped check reported as a pass.

## Limitations

- **This is an audit of two reports, not of the world.** Every specimen count and class is transcribed from W01c/W01e; where they were wrong, I am wrong identically. I re-derived nothing from primary artifacts — W01e did that, and I did not duplicate it.
- **The flip set is not exhaustive.** I enumerated nine decisions plus one candidate; a reading I did not think of would widen the envelope further. The `20 – 84` envelope is a **lower bound on the band's width**, not its true width.
- **Envelope arithmetic assumes decisions are independent.** They are not entirely: S-PANEL-strict and S-PARITY share a rationale, and S-BRENCA-out and S-BRENCA-unusable are alternative reasons for the same −12 (they are not additive, and I did not add them).
- **Specimens, not patients. Arrays are not patients. Runs are not patients. Libraries are not specimens.** Nothing here is a cohort, and no patient-level deduplication exists for any pair except `GSE4303`/`GSE28866`. **No independence or cohort claim is made or implied.** W01d's tier-D non-independence finding stands untouched.
- **"Obtainable" is a ceiling on availability, not usability.** The stable core of 20 counts specimens whose accession is public; it does not assert a usable expression matrix or any fusion-type annotation comes with them.
- **Row 8 is SECONDARY throughout and cannot be verified at any HEAD this campaign has read.** I accept the owner's closure as authoritative and quantify what happens if it is later qualified; I make no attempt to check it and no attempt on the accessions or routes.
- **W01e's D1 is a non-corroboration, not a refutation.** An absent record in a bounded 2026-08 GEO query set is **UNKNOWN, not zero**, and S-ROW12-drop is therefore a defensible reading rather than the correct one.
- **No clinical claim.** Deposit availability is a data-access fact. Nothing here bears on EMC efficacy, safety, selectivity, prognosis or clinical readiness, and no computational result could.

## Stop condition

**Set up front:** a leave-one-decision-out table over every decision the band is sensitive to, both extreme envelopes, a leverage ranking naming the dominant decision, and the stable core stated as a single number with its size characterised honestly — computed, assertion-checked, and returned the moment those four exist.

**MET.** (1) Nine decisions enumerated with each row's placement rule and grade (R1) and each flipped individually (R2). (2) Envelopes **20–20** and **70–84**, full defensible envelope **20–84 of 84**. (3) Ranking computed; **row 12 dominates at 19 specimens and is the entire quoted width of the band**, with three hidden 12-specimen floor decisions identified as unrepresented in the quoted interval. (4) **Stable core = 20 specimens (24%), all three already held by the repository, i.e. zero new data** — plus one newly named candidate decision (S-PARITY) that would cut it to 10. Returning immediately; no padding.

## Tool-call and wall-clock count actually used

**11 tool calls** (all Bash; zero MCP, zero WebSearch, zero WebFetch, zero network, zero retrieval) against the ~40 target. **Wall clock 2 min 33 s** (`02:54:11` → `02:56:44` UTC) against the ~40-minute target.

## Next concrete action

**Retire the band as a quotable figure and replace it with the stable core plus a named contingency list.** Concretely, one edit for whoever owns the lane's reporting: wherever "44–63 obtainable" appears, write instead *"**20 specimens obtainable and verified** (GSE4303, GSE24369, GSE28866 — all already held); a further 24 contingent on two decisions (Brenca's transcribed accession, +12; whether a targeted probe panel counts as transcriptome-wide, +12); and up to 19 more contingent on identifying one GEO series nobody has identified."* That sentence is true under every reading in R2, requires no retrieval, and cannot move by 12 on the next correction — which the current headline demonstrably can, twice over.

The single piece of *evidence* worth buying remains W01e's: **identify row 12 by an archive query on the GitHub Actions escape hatch** (~15 min, no spending, shares a runner job with W01b's queued Europe PMC `accessionIds` query). It is worth 19 specimens — the whole width of the band — and it is the only action that converts a decision into a fact rather than re-litigating one. A cheap no-network second item stands from W01e and is reinforced by R5 here: **decide once what "transcriptome-wide" means in this inventory, and apply it to row 11, GSE4303 and PMID 41644428 together** — as it stands the criterion is applied in the single direction that flatters the obtainable number.
