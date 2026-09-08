<!-- collected 2026-09-08T03:52:11Z by campaign coordinator; agent id ad20361f9450a60c6; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad20361f9450a60c6.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

# W02j — Does the W02i arm-to-arm rule fire on the two marker sets W02d retired? (specificity control on the rule itself)

## Worker

- **Worker ID:** W02j (lane 2 refill), OPUS-CAPACITY-CAMPAIGN-20260908. W02i's named successor.
- **Lane:** Lane 2 — EMC microenvironment. Specificity/discriminant-validity control on W02i's frozen arm-to-arm rule.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote container. **This is a self-report and must not be treated as observed fact.** No served-model environment variable exists (`ANTHROPIC_MODEL` unset; the only Anthropic variable is `ANTHROPIC_BASE_URL`). The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git working tree, honoured. All execution under `/tmp/claude-0/w02j/`, **deleted before returning** (`rm -rf`; `ls` exits 2, `No such file or directory`). **Nothing written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git write operation of any kind.** `scripts/preflight.sh` not run. No network call, no paid API, no GPU. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` was read only (one `rg`), never written or copied.

**`date -u` start:** `Tue Sep  8 03:42:02 UTC 2026` — **end:** `Tue Sep  8 03:46:47 UTC 2026`
**`git rev-parse HEAD` start:** `5ae0fa04ff9516ac8f820381079d644a094f4a77` — **end:** `606d79f96526b651f3b825190d721f6b302c032e` (**moved under me, as the brief warns**).
**Verified rather than assumed:** `git diff --name-only 5ae0fa04 606d79f9 | grep -v opus-capacity-campaign-20260908 | wc -l` → **0**. Every one of the 9 changed files is inside this campaign directory (`COMMON-BRIEF.md` plus 8 collected sibling reports). **Nothing I measured changed.**
**`git status --porcelain` start / end:** empty / empty (literal `STATUS:[]` both times).
**Panel cache sha256 start / at runtime (in-script) / end:** `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` — **all three identical.**

**`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (four long proxy/no-proxy lines that merely contain `api.anthropic.com` in a host list are named here and elided in this rendering — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`):

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

**Dispatch correction acknowledged:** the stray `EOF_MARKER_REPLACED_BELOW` line was ignored; the coordinator's standing constraint block was read and obeyed, and `COMMON-BRIEF.md` (post-03:36Z correction), `CORPUS-CONTEXT.md` and `CLOSED-WORK.md` were read in full **before the run**. Nothing in the "Known, measured, and NOT worth rediscovering" section touches this question; the `preflight` systems-step note is noted and irrelevant (I ran no preflight and changed no file). **W25 not read, not referenced.**

---

## Question

W02i's rule produced one surviving lane-2 claim — **fibro/ECM `R_gene` = U (UNUSUAL)**, EMC 2.0460 below all three comparator arms and below all 12376 exhaustive LGFMS six-specimen subsamples — and W02i itself named its single successor as the only remaining test that could **falsify** rather than decorate it:

**Run the identical six-row arm-to-arm rule on the two marker sets W02d RETIRED — immune (k=12) and tumour (k=9) — as a specificity control on the rule itself.**

It is open because the surviving `U` currently has **no discriminant validity**: nobody has shown the rule *fails to fire* on a curated gene set that carries no lane claim. The immune set is the ideal control precisely because W02d recorded that it is genuinely **structured** (it beats its size-matched random 12-gene null at P = 0.0114) while carrying **no excess between-specimen variance** (EMC/LGFMS ratio 1.00×, retired as W02d's explicit negative control). The tumour set was retired because its 2.23× ratio rests on one specimen (GSM600938).

---

## Prior-work check

| # | command | what it showed |
|---|---|---|
| 1 | `rg -n -i "specificity control\|discriminant valid\|retired marker set\|immune.*k=12" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` | Every hit is the **NR4A3 degrader decoy specificity control** (`nr4a3-degrader-paper.md`, `map-audit-manuscript.md`, `nr4a3_8xtt_decoy_null.py`, `emc_atr_vulnerability.py`) — a molecular-docking control, unrelated to expression marker sets. **No expression-panel specificity control exists in the tracked corpus.** |
| 2 | `rg -n -i "R_gene\|mean pairwise r\|arm-to-arm" --glob '!.git' --glob '!…campaign…/**'` | Zero hits for `R_gene`, `arm-to-arm`, or mean pairwise `r`. All hits are `per_gene` substring collisions in the fusion-output and MTAP/PRMT5 manuscripts. **The statistic does not exist outside this campaign.** |
| 3 | `rg -n -i "R_gene\|arm-to-arm" /tmp/claude-0/frozen-corpus/extracted/corpus/` | Same result in the verified frozen corpus (all hits are `per_gene`/`test_the_census_view` collisions). Confirms this is not locally-absent-but-known prior art. |
| 4 | `git ls-files \| rg -i "w02\|expression-panel"` | Nine lane-2 campaign reports; W02i is the latest and names this successor. |
| 5 | read `W02i-comparator-arm-decomposition.md` **in full**, including its frozen docstring and full inline script | Loader, three statistic functions, arm dictionary and C(17,6) enumeration reused **verbatim**. |
| 6 | `grep -n -i -E "retire\|immune\|tumour" W02d-compartment-variance-battery.md` | Established why both sets are retired and — critically — that the immune set is structured (random-null P = 0.0114) but flat between specimens (1.00×). This is what makes it the right control. |
| 7 | read `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` in full | I touched none of: the clinical registry, PUB-ASO/Qeios frozen deliverables, the NR4A Perspective refusal, Brenca, Hofvander, the paired-Davis negative, the registry-classification paper, or any unrecovered pazopanib/sunitinib/trabectedin/Wagner/CTARC source. **No network call. No expression matrix fetched. No denied route probed, replayed or routed around.** GSE24369 rediscovery is not new data and I claim none. |

Per the brief, sibling campaign reports are not repository evidence; W02i is my *input*, not my prior art. This exact test is unrun.

---

## Method and inputs

**SUBSTRATE LIMIT, stated up front and not as a gap to close.** Sole input: the committed panel cache `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json` (`generated_utc 2026-08-29T12:51:32+00:00`, sha256 `123bd05a…f336bd9`). It is **not an expression matrix**. The GSE24369 series matrix is not committed and fetching it is **DENIED**; no attempt, probe or workaround was made. Field used: `gene_reads[SYM]["GSE24369_series_matrix.txt.gz"].per_sample[].array_percentile` — a **within-array rank**, not an abundance.

- **Platform:** GPL6244 (`GSE24369`), **464 genes complete-case × 35 samples**, classes `{EMC 6, LGFMS 17, desmoid_fibromatosis 6, fibrosarcoma 6}`, asserted in-script.
- **Marker sets under test:** immune (declared k=12) and tumour (declared k=9), verbatim from W02d via W02i's `MARK` dict. **Both realised at full k — zero genes dropped**, printed by the run.
- **Statistics:** `r_gene`, `r_var`, `mean_pair_r` function bodies **copied byte-for-byte from W02i's returned script**, as is the loader.
- **Subsampling:** EMC / desmoid / fibrosarcoma at n=6 are point values; LGFMS (n=17) enumerated **exhaustively**, all **C(17,6) = 12376** subsamples (asserted), therefore **seed-free**. Full-arm n=17 printed for context only, entering no rule.
- **Tools:** Python 3.11.15, numpy 2.4.6, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02j`. No scipy, no network, no paid API, no GPU.

### Pre-declaration integrity

The complete pre-declaration is the script's module docstring, **written in full before the first execution**; there was exactly one execution.

| moment | sha256 of `/tmp/claude-0/w02j/w02j.py` |
|---|---|
| **before run** (`sha256sum`) | `997944cef4d3dbdda7d031b9176b0674d39d84943e0aa9a021bfb3560226c57b` |
| **at runtime** (script hashing itself) | `997944cef4d3dbdda7d031b9176b0674d39d84943e0aa9a021bfb3560226c57b` |
| **after run** (`sha256sum`) | `997944cef4d3dbdda7d031b9176b0674d39d84943e0aa9a021bfb3560226c57b` |

**All three identical. The result is not VOID.**

**Tail of interest — decided and justified in advance, with W02i's error explicitly named so it was not repeated.** Quoted from the docstring: *"The tail for a SPECIFICITY CONTROL is not a free choice: it must be the tail in which the claim being controlled fired… `R_gene`: LOWER tail. The fibro/ECM U fired BELOW… A retired set firing BELOW is the artefact signature. An upward departure on a retired set is NOT the thing being controlled and will be reported descriptively only. `R_var`: LOWER… `mean_r`: UPPER tail. This is a genuine PROSPECTIVE directional prediction, not a repair of W02i's error applied to W02i's own data. W02i OBSERVED EMC to have the highest mean_r of four arms on BOTH surviving axes. These two marker sets are NEW to that comparison, so predicting the same direction for them in advance is a real prediction that can fail."* A two-tailed column `p_two = min(1, 2·min(p_lo,p_hi))` was **also pre-declared** and printed for all six rows, so no direction error could void the run; the directional rule remains primary.

**What would show the fibro/ECM U is an artefact, quoted:** *"ARTEFACT: EITHER retired set returns U on R_gene (primary directional rule, lower tail)… I PRE-COMMIT to headlining that outcome as a further weakening of the lane's one surviving claim, written as a weakening and not as a nuance. DISCRIMINANT: BOTH retired sets return N on R_gene… AMBIGUOUS: anything else."*

**My expectation, quoted:** *"I expect ARTEFACT or AMBIGUOUS, and I lean ARTEFACT… Elevated internal correlation across two unrelated gene sets in the same arm is more parsimoniously an arm-level property… I expect at least one retired set to return U or P-with-BELOW on R_gene, and I expect both retired sets to put EMC top-of-four on mean_r."*

**Two pre-declared secondary diagnostics** (declared in the docstring before the run, beyond W02i's six rows, because the falsification statement names two alternatives — "a property of the rule" and "a property of the EMC arm's global rank structure" — that the six primary rows cannot separate): **D1**, the same three statistics on all 464 complete-case genes as one set; **D2**, a random-panel calibration of the E1 limb (universe = 464 minus the 41 marker genes = 423, the W02g-style exclusion; 400 panels per k ∈ {14,12,9}, seed 20260908, LGFMS point value approximated by a fixed seeded 250-combination subset — **the approximation applies only to D1/D2, never to the six exhaustive primary rows**).

---

## Result

**Headline: the artefact reading is NOT supported — neither retired set reproduces the fibro/ECM signature — but the pre-declared calibration shows that half of the rule is worthless, and my own leading expectation was wrong.**

### R1 — Control: W02i's algebra AND its full rule reproduced before any retired-set number — `PRIMARY`

| axis | k | `R_gene` | taken | `R_var` | taken | `mean_r` | taken | all match |
|---|---|---|---|---|---|---|---|---|
| fibro/ECM | 14 | 2.0460 | 2.0460 | 3.0441 | 3.0441 | 0.5168 | 0.5168 | **True** |
| endothelial | 6 | 1.1729 | 1.1729 | 1.3934 | 1.3934 | 0.8124 | 0.8124 | **True** |

Beyond the six EMC values, the **entire rule pipeline** was re-run on W02i's two surviving sets and checked against its printed verdict rows:

```
fibroECM     R_gene  reproduced=True | mine EMC 2.0460 LGFMSmed 4.3448 des 5.3457 fib 5.1089 p_lo 0.00008 rank 1 U
endothelial  R_gene  reproduced=True | mine EMC 1.1729 LGFMSmed 1.2528 des 1.4393 fib 1.1724 p_lo 0.20296 rank 2 N
CONTROL OVERALL LIKE-FOR-LIKE = True
```

This is like-for-like. (Note, `[POST-HOC]` and scoring nothing: under *my* pre-declared upper tail for `mean_r`, W02i's two `P` rows would have been `U` — fibro/ECM `p_hi` 0.00052, endothelial `p_hi` 0.01147. I am **not** re-scoring W02i; its rows stand as `P` with post-hoc directions, exactly as it reported them.)

### R2 — Arm table, immune axis (k=12, retired; W02d's negative control) — `SECONDARY`

| stat | EMC (n=6) | desmoid | fibrosarcoma | LGFMS full (n=17)\* | LGFMS-sub p05 | p50 | p95 | min | max |
|---|---|---|---|---|---|---|---|---|---|
| `R_gene` | **2.8457** | 1.6106 | 1.3983 | 1.4438 | 1.4161 | 1.5454 | 1.9578 | 1.3405 | 10.2421 |
| `R_var` | **3.6767** | 1.8715 | 1.7367 | 1.8727 | 1.6411 | 2.0917 | 2.4595 | 1.3092 | 2.9332 |
| `mean_r` | **0.2289** | 0.3272 | 0.5444 | 0.4581 | 0.2078 | 0.4613 | 0.6501 | −0.0646 | 0.7372 |

\* n=17, context only, enters no rule.

### R3 — Arm table, tumour axis (k=9, retired) — `SECONDARY`

| stat | EMC (n=6) | desmoid | fibrosarcoma | LGFMS full (n=17)\* | LGFMS-sub p05 | p50 | p95 | min | max |
|---|---|---|---|---|---|---|---|---|---|
| `R_gene` | 2.9005 | 4.2347 | 2.1405 | 2.7574 | 2.4638 | 4.6292 | 9.7390 | 1.1929 | 51.2844 |
| `R_var` | 1.9282 | 2.5228 | 1.8463 | 1.8001 | 1.6616 | 2.2552 | 2.9268 | 1.2203 | 4.1400 |
| `mean_r` | **0.0777** | −0.0233 | 0.0215 | −0.0673 | −0.1046 | −0.0581 | 0.0090 | −0.1243 | 0.0823 |

### R4 — Primary verdict table, verbatim from the run — `PRIMARY` (a computation actually executed)

```
set       stat          EMC  LGFMSmed   desmoid fibrosarc    side     E1 p_declared     p_two     E2  E2two  rank  outcome
immune    R_gene     2.8457    1.5454    1.6106    1.3983   ABOVE   True   0.99911   0.00194  False   True     4  P (PARTIAL)
immune    R_var      3.6767    2.0917    1.8715    1.7367   ABOVE   True   1.00000   0.00016  False   True     4  P (PARTIAL)
immune    mean_r     0.2289    0.4613    0.3272    0.5444   BELOW   True   0.92922   0.14171  False  False     1  P (PARTIAL)
tumour    R_gene     2.9005    4.6292    4.2347    2.1405  INSIDE  False   0.10649   0.21298  False  False     2  N (NOT UNUSUAL)
tumour    R_var      1.9282    2.2552    2.5228    1.8463  INSIDE  False   0.14834   0.29668  False  False     2  N (NOT UNUSUAL)
tumour    mean_r     0.0777   -0.0581   -0.0233    0.0215   ABOVE   True   0.00024   0.00048   True   True     4  U (UNUSUAL)

=== FALSIFICATION CALL (pre-declared three-way, R_gene limb, primary directional rule) ===
R_gene outcomes: {'immune': 'P', 'tumour': 'N'} sides: {'immune': 'ABOVE', 'tumour': 'INSIDE'}
CALL: AMBIGUOUS — neither pre-declared condition met.

=== SECONDARY CALL (mean_r, upper tail, pre-declared prospective direction) ===
mean_r EMC rank of 4 per retired set: {'immune': 1, 'tumour': 4}
CALL: EMC is NOT uniformly top-of-four on mean_r for the retired sets; the global-arm explanation is not supported.
```

### R5 — D1, all 464 complete-case genes as one set — `SECONDARY`, descriptive, pre-declared

```
stat       EMC(n=6)    desmoid  fibrosarc LGFMSfull* |    LG p05    LG p50    LG p95
R_gene      11.2313    81.4459    11.5896     8.0485 |    9.8747   13.6531   27.1744   -> P (BELOW, p_lo 0.29880)
R_var        4.4998     5.1727     3.8147     4.6525 |    5.2376    5.9793    6.9743   -> P (INSIDE, p_lo 0.00398)
mean_r       0.0304     0.0060     0.0347     0.0198 |    0.0078    0.0183    0.0331   -> N (INSIDE, rank 3/4)
```

As declared in advance, D1's `R_gene` is numerically unstable at k=464 and the informative quantity is `mean_r`.

### R6 — D2, random-panel calibration of the E1 limb — `SECONDARY`, pre-declared, and the most consequential row here

Universe = 464 complete-case genes minus the 41 marker genes present = **423** (matching W02g's universe size). 400 panels per k, seed 20260908.

| k | panels | E1 fires BELOW on `R_gene` | E1 fires ABOVE on `R_gene` | E1 fires ABOVE on `mean_r` | E1 fires BELOW on `mean_r` |
|---|---|---|---|---|---|
| 14 | 400 | **0.2950** | 0.2275 | 0.3725 | 0.2300 |
| 12 | 400 | **0.3025** | 0.2225 | 0.3250 | 0.2275 |
| 9 | 400 | **0.2675** | 0.2650 | 0.3575 | 0.2100 |

**Pre-declared reading, fired:** *"if E1BELOW_Rgene for k=14 exceeds 0.05, the E1 limb is NOT evidence-grade for the fibro/ECM claim."* Observed **0.2950 → NOT EVIDENCE-GRADE.**

### R7 — What this says, limb by limb

**(a) The pre-declared ARTEFACT condition did NOT fire, and this is the answer to the question I was sent to ask.** Neither retired set reproduces the fibro/ECM signature. The tumour set returns **N** on `R_gene` (INSIDE the comparator range, `p_lo` = 0.107, rank 2/4). The immune set departs **in the opposite direction** — `R_gene` 2.8457 **ABOVE** all three comparators, rank 4/4 — and my docstring stated in advance that *"an upward departure on a retired set is NOT the thing being controlled."* So on the letter of the frozen rule the call is **AMBIGUOUS** (DISCRIMINANT required N on both), but on the substance **no retired set fires the BELOW-and-outside signature that the fibro/ECM `U` is made of.** The lane's surviving claim is **not shown to be an artefact of the rule by this control**, and it gains partial — not full — discriminant validity.

**(b) I was wrong about the global-arm explanation, and the data refute it cleanly.** I expected EMC to be top-of-four on `mean_r` for both retired sets, on the reasoning that six EMC arrays are globally more alike. **The immune set puts EMC LAST of four** (`mean_r` 0.2289 vs 0.3272 / 0.4378-equivalent 0.5444 / 0.4613; rank **1/4**), and **D1 puts EMC third of four** on the all-464-gene `mean_r` (0.0304, INSIDE, **N**). **There is no global elevation of within-arm gene-gene rank correlation in EMC.** The parsimonious artefact explanation I leaned on is **not supported**, and I am reporting my expectation as failed rather than quietly dropping it. Whatever produces the fibro/ECM `mean_r` 0.5168 is gene-set-dependent, not arm-wide.

**(c) The rule DOES fire `U` on a retired set — on the `mean_r` limb.** Tumour `mean_r` = 0.0777 vs comparators −0.0581 / −0.0233 / 0.0215, `p_hi` = 0.00024, rank 4/4 → **U (UNUSUAL)** under my pre-declared upper tail. This is a real specificity failure, and it must be stated: **the `mean_r` limb of this rule fires `U` for a gene set W02d retired.** Two things bound how much it costs. First, `mean_r` carries no surviving lane-2 claim (W02i's two `mean_r` rows are `P` with post-hoc directions). Second, and more damning for the statistic than for the lane, **the effect size is trivial in absolute terms** — a `U` was achieved at `mean_r` = 0.078, i.e. "very slightly positive where the comparators are very slightly negative." A verdict machine that returns UNUSUAL at that magnitude is measuring the comparators' tightness, not the EMC set's structure.

**(d) The `E1` limb of the rule is quantitatively worthless, and this is now measured rather than argued.** 29.5% of random 423-universe 14-gene panels place EMC below all three comparator points on `R_gene`. That is essentially the 25% exchangeable prior for "EMC is the minimum of four values" — **`E1` is a rank-1-of-4 test wearing an interval's clothes.** W02i already declared `E3` descriptive because a four-arm rank cannot reach α = 0.05; **D2 shows `E1` is the same test and inherits the same ceiling**, which W02i's `U`/`N`/`P` scheme did not acknowledge. Consequently **the whole of the fibro/ECM `U` rests on the `E2` limb alone** (`p_lo` = 0.00008 against the 12376 exhaustive LGFMS subsamples) — and `E2` resamples *one* arm, so it measures within-LGFMS specimen sampling, **not** between-disease variability. W02i stated that limitation in prose; this run converts it from a caveat into the entire load-bearing structure of the claim.

**Net effect on the lane.** The surviving fibro/ECM `U` **survives this falsification attempt** — no retired set reproduces its signature, and the global-arm alternative is refuted by D1 and by the immune `mean_r` rank. But it is now known to rest on a single limb whose companion limb has a **~30% false-fire rate**, and the rule as a whole is known to return `U` on a retired set in the `mean_r` limb. The claim is narrower and better characterised; it is not stronger.

---

## Validation evidence

**RUN.**

| # | command | exit | verbatim key output |
|---|---|---|---|
| 1 | `python3 -c "import numpy,sys;print(...)"` | 0 | `numpy 2.4.6 python 3.11.15` |
| 2 | `sha256sum /tmp/claude-0/w02j/w02j.py` (before run) | 0 | `997944cef4d3dbdda7d031b9176b0674d39d84943e0aa9a021bfb3560226c57b` |
| 3 | `cd /tmp/claude-0/w02j && time python3 w02j.py > out.txt 2>&1` | **0** (`EXIT=0`) | `real 0m38.916s`; full output reproduced as R1–R6 |
| 4 | `sha256sum /tmp/claude-0/w02j/w02j.py` (after run) | 0 | `997944ce…0226c57b` — **identical to #2 and to the script's runtime self-hash** |
| 5 | `sha256sum research/modalities/emc-expression-panels.json` (start, in-script, end) | 0 | `123bd05a…f336bd9` all three times |
| 6 | `git rev-parse HEAD` (start / end) | 0 | `5ae0fa04…` / `606d79f9…` — **moved**; see #7 |
| 7 | `git diff --name-only 5ae0fa04 606d79f9 \| grep -v opus-capacity-campaign-20260908 \| wc -l` | 0 | **`0`** — all 9 changed files are inside this campaign directory; nothing I measured changed |
| 8 | `git status --porcelain` (start / end) | 0 | empty / empty |
| 9 | in-script assertions | — | `X.shape[0] == 464`; arm sizes 6/17/6/6; `len(combos) == 12376`; realised k 12/6/14/9 with `dropped=none` for all four sets — all passed (failure would have been a non-zero exit) |
| 10 | control reproduction check | — | `CONTROL OVERALL LIKE-FOR-LIKE = True` |
| 11 | `rm -rf /tmp/claude-0/w02j && ls -d /tmp/claude-0/w02j` | 2 | `ls: cannot access '/tmp/claude-0/w02j': No such file or directory` — scratch deleted |
| 12 | `df -h /` | 0 | `/dev/vda 252G 20G 18G 54% /` |

**PROPOSED (NOT RUN):** the E2-limb calibration named under *Next concrete action*; any joint arm-varying **and** gene-varying null; any GPL3290 cross-check (comparator arms there are n=3 and cross-platform pooling is forbidden); anything on the GSE24369 series matrix (uncommitted, egress **DENIED**). None executed, none claimed. `scripts/preflight.sh` not run (brief and dispatch forbid it); no repository test tier invoked, because I changed no repository file. **No content-policy refusal was encountered in this unit.**

**Script, returned inline (not written into the tree).** The complete file whose sha256 is `997944cef4d3dbdda7d031b9176b0674d39d84943e0aa9a021bfb3560226c57b` was `/tmp/claude-0/w02j/w02j.py`, since deleted. Its module docstring is the frozen pre-declaration; here it is in full, with the body.

```python
"""
W02j — OPUS-CAPACITY-CAMPAIGN-20260908, lane 2 refill.  W02i's NAMED SUCCESSOR.

COMPLETE PRE-DECLARATION.  Written in full BEFORE the first execution.  The file is sha256'd
before the run, hashes itself at runtime, and is sha256'd again after.  If any of the three
differ the result is VOID and I will say so.  Exactly one execution is intended.

============================================================================================
QUESTION
============================================================================================
W02i ran a frozen six-row arm-to-arm rule (2 surviving marker sets x 3 statistics) and got a
SPLIT result:
  * endothelial R_gene -> N (NOT UNUSUAL); EMC rank 2 of 4, p_lo = 0.203.  W02g's endothelial
    flatness finding was therefore WITHDRAWN as not EMC-specific.
  * fibro/ECM R_gene   -> U (UNUSUAL); EMC 2.0460 below all three comparator points and below
    all but zero of the 12376 exhaustive LGFMS six-specimen subsamples (p_lo = 0.00008).
    W02i itself labelled this a CONFIRMATION UNDER A FROZEN RULE of something W02f had already
    printed post-hoc, not a discovery.
  * both mean_r rows -> P, because W02i declared the LOWER tail and the departure was UPWARD
    (EMC highest mean_r of four arms on BOTH axes).  Those upper-tail p-values are POST-HOC in
    direction and claim no significance.

The fibro/ECM U is the lane's ONE surviving claim.  It currently lacks DISCRIMINANT VALIDITY:
nobody has shown that the rule does NOT fire for gene sets that carry no claim at all.  W02i
named exactly one successor and called it the only remaining test that could FALSIFY rather
than decorate:

  RUN THE IDENTICAL SIX-ROW ARM-TO-ARM RULE ON THE TWO MARKER SETS W02d RETIRED — immune (k=12)
  and tumour (k=9) — AS A SPECIFICITY CONTROL ON THE RULE ITSELF.

Why these two sets are the right control and not an arbitrary pair.  W02d ran a four-part
artifact battery and retired BOTH: tumour (k=9) DOES NOT SURVIVE (its elevated EMC/LGFMS
variance ratio 2.23x rests on one specimen, GSM600938); immune (k=12) DOES NOT SURVIVE and was
run by W02d explicitly as a NEGATIVE CONTROL (EMC/LGFMS ratio 1.00x; a six-specimen LGFMS
resample matched or exceeded EMC's immune SD 46% of the time).  Neither carries any surviving
lane-2 claim.  Crucially, W02d ALSO recorded that the immune set beats its size-matched random
12-gene null (P = 0.0114) — i.e. it is a genuinely STRUCTURED curated set, not noise.  So it is
the ideal control for a rule whose whole content is about the internal structure of a curated
marker set: if the W02i rule fires U on a set that is structured but carries no claim, the rule
is measuring "curated set on this platform in this arm", not "fibro/ECM in EMC".

============================================================================================
INPUT — SUBSTRATE LIMIT, stated as a limit and not as a gap to close
============================================================================================
Sole input: the committed panel cache
  /home/user/Rare-cancers/research/modalities/emc-expression-panels.json
  expected sha256 123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9
This is NOT an expression matrix.  The GSE24369 series matrix is not committed and fetching it
is DENIED; no attempt, probe or workaround is made anywhere in this unit.  No network, no paid
API, no GPU, no wet lab, no new deposit.
Field used: gene_reads[SYM][GSE24369_series_matrix.txt.gz].per_sample[].array_percentile — a
WITHIN-ARRAY RANK, not an abundance.  Six arrays are not six patients.  Anything found here is
an ASSOCIATION at most: no mechanism, no clinical claim.

============================================================================================
STATISTICS — reused VERBATIM from W02i (which reused W02f/W02g/W02h) so this is like-for-like
============================================================================================
For a marker set of k genes scored on the n specimens of one arm, s = mean over genes:
  R_gene = k * sum_i f_i^2 ,  f_i = Cov(g_i, s) / (k * Var(s))        (even = 1.0)
  R_var  = k * sum_i (v_i / sum_j v_j)^2 ,  v_i = Var(g_i)            (even = 1.0)
  mean_r = mean of the k(k-1)/2 off-diagonal Pearson correlations among the k genes
The three function bodies are copied unchanged from W02i's returned script.  The loader
(complete-case genes on GPL6244, 464 genes x 35 samples) is copied unchanged.

============================================================================================
ARMS AND SUBSAMPLING SCHEME — identical to W02i
============================================================================================
  EMC                     n = 6   point value (the arm under test)
  desmoid_fibromatosis    n = 6   point value
  fibrosarcoma            n = 6   point value
  LGFMS                   n = 17  EXHAUSTIVE enumeration of all C(17,6) = 12376 six-specimen
                                  subsamples.  Exhaustive => SEED-FREE, not Monte-Carlo.
                                  The full-arm n=17 value is printed for CONTEXT ONLY and enters
                                  no rule (these statistics are n-dependent).
The n-matched LGFMS POINT VALUE used in every primary rule is the MEDIAN of its 12376 subsamples.
Comparator point set P = { median(LGFMS subsamples), desmoid, fibrosarcoma } — three arms.
ONLY THREE COMPARATOR ARMS EXIST on this platform.  That is a hard power ceiling: a four-arm
rank can never reach alpha = 0.05, so any rank statistic here is DESCRIPTIVE ONLY and is
labelled as such wherever it appears.

MARKER SETS UNDER TEST (verbatim from W02d via W02i's MARK dict, not re-invented):
  immune (k=12): PTPRC CD2 CD3D CD3E CD8A CD68 CD163 CSF1R ITGAM HLA-DRA MS4A1 GZMB
  tumour (k=9) : NR4A3 PPARG RET INSM1 SYP CHGA ENO2 KIT CD24
If any listed gene is absent from the 464-gene complete-case matrix it is DROPPED, the dropped
list and the realised k are PRINTED, and the realised k is what is reported — I will not pretend
to a k I do not have.  If a set's realised k < 5 its rows are reported UNCOMPUTABLE and not
scored.

============================================================================================
DECISION RULES, TAIL OF INTEREST, THRESHOLDS — frozen
============================================================================================
For EACH set (immune, tumour) and EACH statistic (R_gene, R_var, mean_r):

  E1 RANGE      : fires iff EMC's value lies OUTSIDE the closed interval [min P, max P].
                  Side (BELOW / INSIDE / ABOVE) is recorded.
  E2 LGFMS TAIL : p_lo = (#{subsample <= EMC} + 1) / (12376 + 1)
                  p_hi = (#{subsample >= EMC} + 1) / (12376 + 1)
                  Both tails ALWAYS printed.  E2 fires iff the PRE-DECLARED tail p <= ALPHA=0.05.
  E3 RANK       : EMC's rank among the four n=6-comparable arm point values.  DESCRIPTIVE ONLY,
                  can never reach 0.05 with four arms, never cited as significance.
  VERDICT: U iff E1 AND E2 ; N iff NEITHER ; P iff exactly one.

TAIL OF INTEREST — DECIDED AND JUSTIFIED IN ADVANCE.  W02i got this wrong (it declared LOWER for
mean_r and the departure was UPWARD, costing it two scoreable rows).  I am not repeating that,
and I am not hiding behind two-tailed for everything either.  The tail for a SPECIFICITY CONTROL
is not a free choice: it must be the tail in which the claim being controlled fired, because the
control asks "does the rule fire the SAME WAY on a set with no claim?".  Therefore:

  R_gene : LOWER tail.  The fibro/ECM U fired BELOW (EMC 2.0460 under every comparator).  A
           retired set firing BELOW is the artefact signature.  An upward departure on a retired
           set is NOT the thing being controlled and will be reported descriptively only.
  R_var  : LOWER tail.  Same reasoning; W02i's fibro/ECM R_var row was P with p_lo = 0.00097,
           i.e. its only firing limb was also the lower one.
  mean_r : UPPER tail.  This is a genuine PROSPECTIVE directional prediction, not a repair of
           W02i's error applied to W02i's own data.  W02i OBSERVED EMC to have the highest
           mean_r of four arms on BOTH surviving axes.  These two marker sets are NEW to that
           comparison, so predicting the same direction for them in advance is a real prediction
           that can fail.  I declare UPPER and I will accept a null if EMC's mean_r is not high.

  SECONDARY, ALSO PRE-DECLARED so that no direction error can void this run: a two-tailed column
  p_two = min(1, 2*min(p_lo, p_hi)) with E2two at alpha = 0.05, printed for all six rows.  The
  PRIMARY verdict is the directional one above; the two-tailed column is reported alongside and
  never substituted for it after the fact.

No multiplicity correction is applied to the six primary rows.  Declared here, not repaired later.

============================================================================================
EXPLICITLY: WHAT RESULT WOULD SHOW THE FIBRO/ECM U IS AN ARTEFACT OF THE RULE
============================================================================================
  ARTEFACT      : EITHER retired set returns U on R_gene (primary directional rule, lower tail).
                  Then the rule fires BELOW-and-outside for a gene set carrying no lane claim,
                  and "EMC's fibro/ECM markers are unusually flat" is not a fibro/ECM fact but a
                  property of the rule and/or of the EMC arm's global rank structure.  I
                  PRE-COMMIT to headlining that outcome as a further weakening of the lane's one
                  surviving claim, written as a weakening and not as a nuance.
  DISCRIMINANT  : BOTH retired sets return N on R_gene.  The rule then demonstrably does not
                  fire on structured-but-unclaimed sets, and the fibro/ECM U gains the
                  discriminant validity it currently lacks.  This does NOT make it a discovery
                  (it remains W02f's post-hoc observation re-tested under a frozen rule) and does
                  NOT make it biological.
  AMBIGUOUS     : anything else (P on either set, or one N and one P).  Reported as ambiguous,
                  with both halves stated and neither promoted.
The same three-way call is made separately and secondarily for mean_r (upper tail): if both
retired sets ALSO put EMC top-of-four on mean_r, elevated internal correlation in the EMC arm is
a GLOBAL property of that arm, not a property of the fibro/ECM or endothelial gene sets.

============================================================================================
PRE-DECLARED DIAGNOSTICS (SECONDARY; beyond W02i's six rows; declared here BEFORE the run)
============================================================================================
These exist because the falsification statement above names two alternatives — "a property of
the rule" and "a property of the EMC arm's global rank structure" — and the six primary rows
alone cannot separate them.  Both are descriptive; neither can promote or rescue a primary row.

  D1  ALL-GENE ARM PROFILE.  The same three statistics on ALL 464 complete-case genes as one
      "set", arm to arm.  If EMC has the highest all-gene mean_r of the four arms, then every
      gene set scored on EMC will tend to look internally correlated and the marker-set framing
      adds nothing.  DECLARED IN ADVANCE: with k=464 the mean-of-all-genes score s is close to
      the array-wide percentile mean, so Var(s) may be near zero and D1's R_gene may be numerically
      unstable and huge; it is printed with that warning and the INFORMATIVE D1 quantity is
      mean_r.  For cost, D1's LGFMS point value uses the SUB250 subset defined below, not all
      12376; this is an approximation of a median and is labelled as one.

  D2  RANDOM-PANEL CALIBRATION OF THE E1 LIMB — the false-fire rate of the rule itself.
      Universe: the 464 complete-case genes MINUS all 41 genes named in the four marker sets
      (immune 12 + endothelial 6 + fibroECM 14 + tumour 9), i.e. the same style of exclusion
      W02g used to get its 423-gene universe.  The realised universe size is printed.
      For each k in {14, 12, 9}: draw NPANEL = 400 random k-gene panels, seed 20260908 (numpy
      default_rng), and for each panel evaluate E1 exactly as the primary rule does, except that
      the LGFMS point value is the median over SUB250 = a fixed seeded 250-combination subset of
      the 12376 (seed 20260908), because 400 x 12376 exhaustive evaluations is not affordable
      here.  This approximation applies ONLY to D2 and D1, never to the six primary rows, which
      remain exhaustive.
      Report, per k: the fraction of random panels for which E1 fires BELOW on R_gene, and the
      fraction for which E1 fires ABOVE on mean_r.
      PRE-DECLARED READING: if more than 0.05 of random k=14 panels fire E1-BELOW on R_gene, the
      E1 limb of the rule is not evidence-grade for the fibro/ECM claim and I will say so
      plainly.  D2 constrains E1 only; it says nothing about the E2 limb.

============================================================================================
CONTROL ROW REQUIRED BY DISPATCH — reproduce W02i's algebra BEFORE anything else
============================================================================================
Step 1 of the run, before any retired-set number is computed, reproduces W02i's R1 EMC control
values AND re-runs W02i's full six-row rule on its two surviving sets, so that not only the
loader but the ENTIRE RULE PIPELINE is shown to be the same object:
  TAKEN R_gene fibroECM 2.0460 / endothelial 1.1729   (W02f/W02g)
  TAKEN R_var  fibroECM 3.0441 / endothelial 1.3934   (W02h)
  TAKEN mean_r fibroECM 0.5168 / endothelial 0.8124   (W02h)
  TAKEN W02i verdict row: fibroECM R_gene p_lo 0.00008 rank 1 U ; endothelial R_gene p_lo 0.20296
  rank 2 N ; and the comparator points fibroECM R_gene LGFMSmed 4.3448 desmoid 5.3457
  fibrosarcoma 5.1089.
Every one of these is asserted-by-printing with a match flag at 4 dp (tolerance 5e-5 for the
statistics, 5e-5 for p-values).  If the control row does not reproduce, the run is reported as
NOT LIKE-FOR-LIKE and no retired-set conclusion is drawn.

============================================================================================
MY EXPECTATION, DECLARED IN WRITING IN ADVANCE so neither outcome can be staged as a surprise
============================================================================================
I expect ARTEFACT or AMBIGUOUS, and I lean ARTEFACT.  Reasoning, stated now so it cannot be
retrofitted: W02i found EMC top-of-four on mean_r for BOTH surviving axes, one of which (endothelial)
returned N on R_gene.  Elevated internal correlation across two unrelated gene sets in the same
arm is more parsimoniously an arm-level property — six EMC arrays being globally more alike in
their within-array rank profiles — than two independent gene-set facts.  If that is what is
happening, it should show up on the retired sets too, and a high, evenly-shared correlation
drives f_i toward equality and R_gene DOWN, which is exactly the E1-BELOW signature.  So I
expect at least one retired set to return U or P-with-BELOW on R_gene, and I expect both retired
sets to put EMC top-of-four on mean_r.
Against my own lean: W02d found the tumour set's EMC behaviour rests on a single specimen and
found the immune set flat (ratio 1.00x), so these sets may simply be too structureless in EMC to
move R_gene at all, in which case N on both is a real possibility and I will report it as the
DISCRIMINANT outcome without hedging it.
I have no stake in either result.  I will report whichever prints.

============================================================================================
STOP CONDITION
============================================================================================
Stop the moment the control row, the 2 x 3 primary verdict table, D1 and D2 have printed on a
single execution with matching before / at-runtime / after script sha256 and matching source
sha256.  No further statistic is added, no threshold is moved, no tail is re-chosen, no post-hoc
test is run.  Any observation made after seeing the numbers is labelled [POST-HOC] and scores
nothing.
"""
import hashlib, json, itertools
import numpy as np

SRC = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT = "GSE24369_series_matrix.txt.gz"
ALPHA = 0.05
SEED = 20260908
NPANEL = 400
NSUB = 250

MARK = {
 "immune": ["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"],
 "endothelial": ["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"],
 "fibroECM": ["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1","PDGFRA","PDGFRB","ACTA2","COL11A1"],
 "tumour": ["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"],
}
TAKEN_RGENE = {"fibroECM": 2.0460, "endothelial": 1.1729}
TAKEN_RVAR  = {"fibroECM": 3.0441, "endothelial": 1.3934}
TAKEN_MEANR = {"fibroECM": 0.5168, "endothelial": 0.8124}
# W02i's printed verdict rows for its two surviving axes (R_gene limb), reproduced as control
TAKEN_W02I = {
  ("fibroECM","R_gene"):    dict(emc=2.0460, lg=4.3448, des=5.3457, fib=5.1089, p_lo=0.00008, rank=1, out="U"),
  ("endothelial","R_gene"): dict(emc=1.1729, lg=1.2528, des=1.4393, fib=1.1724, p_lo=0.20296, rank=2, out="N"),
}
# PRE-DECLARED tail of interest, per statistic
TAIL = {"R_gene": "lo", "R_var": "lo", "mean_r": "hi"}

print("SELF sha256 (as read at runtime) =", hashlib.sha256(open(__file__,'rb').read()).hexdigest())
print("SOURCE sha256 =", hashlib.sha256(open(SRC,'rb').read()).hexdigest())
d = json.load(open(SRC))
print("SOURCE generated_utc =", d.get("generated_utc"))

# ---- loader: complete-case genes on GPL6244 (copied unchanged from W02i) ----
gr = d["gene_reads"]
gsms, klass, rows, names = None, None, [], []
for g in sorted(gr):
    p = gr[g].get(PLAT)
    if not p or not p.get("per_sample"): continue
    ps = p["per_sample"]
    if any(r.get("array_percentile") is None for r in ps): continue
    ids = [r["gsm"] for r in ps]
    if gsms is None:
        gsms = ids; klass = [r["class"] for r in ps]
    if ids != gsms: continue
    names.append(g); rows.append([r["array_percentile"] for r in ps])
X = np.asarray(rows, float)
assert X.shape[0] == 464, X.shape
cnt = {c: klass.count(c) for c in sorted(set(klass))}
print("PLATFORM %s | complete-case %d genes x %d samples | %s" % (PLAT, X.shape[0], X.shape[1], cnt))
idx = {g:i for i,g in enumerate(names)}
ARMS = {c: np.array([i for i,k in enumerate(klass) if k == c]) for c in sorted(set(klass))}
assert len(ARMS["EMC"]) == 6 and len(ARMS["LGFMS"]) == 17
assert len(ARMS["desmoid_fibromatosis"]) == 6 and len(ARMS["fibrosarcoma"]) == 6

# ---- statistics (copied unchanged from W02i) ----
def r_gene(M):
    k, n = M.shape
    s = M.mean(0)
    vs = s.var(ddof=1)
    if vs <= 0: return None
    Mc = M - M.mean(1, keepdims=True)
    sc = s - s.mean()
    C = (Mc * sc).sum(1) / (n - 1) / k
    f = C / vs
    return k * float((f**2).sum())

def r_var(M):
    k = M.shape[0]
    v = M.var(1, ddof=1)
    t = v.sum()
    if t <= 0: return None
    return k * float(((v/t)**2).sum())

def mean_pair_r(M):
    k = M.shape[0]
    sd = M.std(1, ddof=1)
    if np.any(sd <= 0): return None
    R = np.corrcoef(M)
    iu = np.triu_indices(k, 1)
    return float(R[iu].mean())

STATS = [("R_gene", r_gene), ("R_var", r_var), ("mean_r", mean_pair_r)]

# ---- realised marker sets ----
REAL = {}
for ax, gl in MARK.items():
    have = [g for g in gl if g in idx]
    miss = [g for g in gl if g not in idx]
    REAL[ax] = have
    print("SET %-12s declared k=%2d realised k=%2d  dropped=%s" % (ax, len(gl), len(have), miss if miss else "none"))

combos = list(itertools.combinations(range(17), 6))
assert len(combos) == 12376
print("\nLGFMS exhaustive six-specimen subsamples enumerated: %d (expected C(17,6)=12376)" % len(combos))

def arm_row(G, nm, fn, sub_vals):
    emc = fn(G[:, ARMS["EMC"]]); des = fn(G[:, ARMS["desmoid_fibromatosis"]])
    fib = fn(G[:, ARMS["fibrosarcoma"]]); lgf = fn(G[:, ARMS["LGFMS"]])
    a = sub_vals[~np.isnan(sub_vals)]
    lg_pt = float(np.median(a)); P = [lg_pt, des, fib]; lo, hi = min(P), max(P)
    e1 = not (lo <= emc <= hi)
    side = "BELOW" if emc < lo else ("ABOVE" if emc > hi else "INSIDE")
    n = len(a)
    p_lo = (int((a <= emc).sum()) + 1) / (n + 1)
    p_hi = (int((a >= emc).sum()) + 1) / (n + 1)
    p_two = min(1.0, 2*min(p_lo, p_hi))
    pdecl = p_lo if TAIL[nm] == "lo" else p_hi
    e2 = pdecl <= ALPHA
    e2t = p_two <= ALPHA
    pts = sorted([("EMC",emc),("LGFMSmed",lg_pt),("desmoid",des),("fibrosarcoma",fib)], key=lambda t:t[1])
    rank = [t[0] for t in pts].index("EMC") + 1
    out = "U (UNUSUAL)" if (e1 and e2) else ("N (NOT UNUSUAL)" if (not e1 and not e2) else "P (PARTIAL)")
    return dict(emc=emc, des=des, fib=fib, lgf=lgf, a=a, lg_pt=lg_pt, lo=lo, hi=hi, e1=e1, side=side,
                p_lo=p_lo, p_hi=p_hi, p_two=p_two, pdecl=pdecl, e2=e2, e2t=e2t, rank=rank, out=out)

def run_axis(ax, genelist, sub_combos, label):
    G = X[[idx[g] for g in genelist]]
    k = G.shape[0]
    L = G[:, ARMS["LGFMS"]]
    sub = {nm: [] for nm,_ in STATS}
    for c in sub_combos:
        Mc = L[:, list(c)]
        for nm, fn in STATS:
            v = fn(Mc); sub[nm].append(np.nan if v is None else v)
    sub = {nm: np.asarray(v, float) for nm, v in sub.items()}
    print("\n================ %s %s (k=%d, LGFMS draws=%d) ================" % (label, ax, k, len(sub_combos)))
    print("%-8s %10s %10s %10s %10s | %9s %9s %9s %9s %9s" %
          ("stat","EMC(n=6)","desmoid","fibrosarc","LGFMSfull*","LG p05","LG p50","LG p95","LG min","LG max"))
    res = {}
    for nm, fn in STATS:
        r = arm_row(G, nm, fn, sub[nm]); res[nm] = r; a = r["a"]
        print("%-8s %10.4f %10.4f %10.4f %10.4f | %9.4f %9.4f %9.4f %9.4f %9.4f" %
              (nm, r["emc"], r["des"], r["fib"], r["lgf"], np.percentile(a,5), np.percentile(a,50),
               np.percentile(a,95), a.min(), a.max()))
    print("* LGFMSfull is n=17, CONTEXT ONLY, enters no rule.")
    for nm,_ in STATS:
        r = res[nm]
        print("  %-7s EMC=%9.4f | P=[%.4f, %.4f] -> %s ; E1=%s | p_lo=%.5f p_hi=%.5f (declared %s tail p=%.5f) -> E2=%s"
              " | p_two=%.5f E2two=%s | E3 rank %d/4 [DESCRIPTIVE ONLY] -> %s"
              % (nm, r["emc"], r["lo"], r["hi"], r["side"], r["e1"], r["p_lo"], r["p_hi"],
                 TAIL[nm].upper(), r["pdecl"], r["e2"], r["p_two"], r["e2t"], r["rank"], r["out"]))
    return res

# ============ STEP 1: CONTROL — reproduce W02i before anything else ============
print("\n############ STEP 1 — CONTROL: reproduce W02i's algebra and rule (BEFORE any retired-set number) ############")
ok = True
for ax in ["fibroECM","endothelial"]:
    M = X[[idx[g] for g in REAL[ax]]][:, ARMS["EMC"]]
    rc, rv, mr = r_gene(M), r_var(M), mean_pair_r(M)
    m1 = abs(rc-TAKEN_RGENE[ax])<5e-5; m2 = abs(rv-TAKEN_RVAR[ax])<5e-5; m3 = abs(mr-TAKEN_MEANR[ax])<5e-5
    ok = ok and m1 and m2 and m3
    print("%-12s k=%2d : R_gene %.4f vs TAKEN %.4f match=%s | R_var %.4f vs %.4f match=%s | mean_r %.4f vs %.4f match=%s"
          % (ax, M.shape[0], rc, TAKEN_RGENE[ax], m1, rv, TAKEN_RVAR[ax], m2, mr, TAKEN_MEANR[ax], m3))
ctl = {}
for ax in ["fibroECM","endothelial"]:
    ctl[ax] = run_axis(ax, REAL[ax], combos, "CONTROL (W02i surviving set)")
print("\n--- CONTROL check against W02i's printed verdict rows (R_gene limb) ---")
for (ax,nm), t in TAKEN_W02I.items():
    r = ctl[ax][nm]
    chk = (abs(r["emc"]-t["emc"])<5e-5 and abs(r["lg_pt"]-t["lg"])<5e-5 and abs(r["des"]-t["des"])<5e-5
           and abs(r["fib"]-t["fib"])<5e-5 and abs(r["p_lo"]-t["p_lo"])<5e-5 and r["rank"]==t["rank"]
           and r["out"].startswith(t["out"]))
    ok = ok and chk
    print("%-12s %-7s reproduced=%s | mine EMC %.4f LGFMSmed %.4f des %.4f fib %.4f p_lo %.5f rank %d %s"
          " || W02i EMC %.4f LGFMSmed %.4f des %.4f fib %.4f p_lo %.5f rank %d %s"
          % (ax, nm, chk, r["emc"], r["lg_pt"], r["des"], r["fib"], r["p_lo"], r["rank"], r["out"],
             t["emc"], t["lg"], t["des"], t["fib"], t["p_lo"], t["rank"], t["out"]))
print("CONTROL OVERALL LIKE-FOR-LIKE =", ok)
if not ok:
    print("!! CONTROL FAILED: this run is NOT like-for-like with W02i and no retired-set conclusion may be drawn.")

# ============ STEP 2: PRIMARY — the six-row rule on the two RETIRED sets ============
print("\n############ STEP 2 — PRIMARY: identical six-row rule on the two RETIRED sets ############")
prim = {}
for ax in ["immune","tumour"]:
    if len(REAL[ax]) < 5:
        print("SET %s realised k=%d < 5 -> UNCOMPUTABLE, not scored." % (ax, len(REAL[ax]))); continue
    prim[ax] = run_axis(ax, REAL[ax], combos, "RETIRED (specificity control)")

print("\n=== PRIMARY VERDICT TABLE (2 retired sets x 3 statistics) ===")
print("%-9s %-7s %9s %9s %9s %9s %7s %6s %9s %9s %6s %6s %5s  %s" %
      ("set","stat","EMC","LGFMSmed","desmoid","fibrosarc","side","E1","p_declared","p_two","E2","E2two","rank","outcome"))
for ax in prim:
    for nm,_ in STATS:
        r = prim[ax][nm]
        print("%-9s %-7s %9.4f %9.4f %9.4f %9.4f %7s %6s %9.5f %9.5f %6s %6s %5d  %s" %
              (ax,nm,r["emc"],r["lg_pt"],r["des"],r["fib"],r["side"],r["e1"],r["pdecl"],r["p_two"],
               r["e2"],r["e2t"],r["rank"],r["out"]))

print("\n=== FALSIFICATION CALL (pre-declared three-way, R_gene limb, primary directional rule) ===")
og = {ax: prim[ax]["R_gene"]["out"][0] for ax in prim}
sides = {ax: prim[ax]["R_gene"]["side"] for ax in prim}
if any(v == "U" for v in og.values()):
    call = "ARTEFACT — a retired set returns U on R_gene; the rule fires for a gene set carrying no lane claim."
elif all(v == "N" for v in og.values()):
    call = "DISCRIMINANT — both retired sets return N on R_gene; the rule does not fire on structured-but-unclaimed sets."
else:
    call = "AMBIGUOUS — neither pre-declared condition met."
print("R_gene outcomes:", og, "sides:", sides)
print("CALL:", call)
mr_top = {ax: prim[ax]["mean_r"]["rank"] for ax in prim}
print("\n=== SECONDARY CALL (mean_r, upper tail, pre-declared prospective direction) ===")
print("mean_r EMC rank of 4 per retired set:", mr_top,
      "| outcomes:", {ax: prim[ax]["mean_r"]["out"] for ax in prim})
if all(v == 4 for v in mr_top.values()):
    print("CALL: EMC is top-of-four on mean_r for the retired sets TOO -> elevated internal correlation is a")
    print("      GLOBAL property of the EMC arm on this platform, not a property of the fibro/ECM or endothelial sets.")
else:
    print("CALL: EMC is NOT uniformly top-of-four on mean_r for the retired sets; the global-arm explanation is not supported.")

# ============ STEP 3: D1 — all-gene arm profile (SECONDARY, descriptive) ============
rng = np.random.default_rng(SEED)
sub_idx = rng.choice(len(combos), size=NSUB, replace=False)
SUB250 = [combos[i] for i in sub_idx]
print("\n############ STEP 3 — D1 (SECONDARY, DESCRIPTIVE): all %d complete-case genes as one set ############" % X.shape[0])
print("D1 uses SUB250 (%d of 12376 combos, seed %d) for the LGFMS point value: an APPROXIMATE median." % (NSUB, SEED))
print("WARNING declared in advance: with k=464, Var(mean-of-all-genes) may be near zero and D1's R_gene may be")
print("numerically unstable/huge. The informative D1 quantity is mean_r.")
d1 = run_axis("ALLGENES", names, SUB250, "D1 (descriptive)")

# ============ STEP 4: D2 — random-panel calibration of the E1 limb ============
excluded = set(g for gl in MARK.values() for g in gl if g in idx)
UNIV = [g for g in names if g not in excluded]
print("\n############ STEP 4 — D2 (SECONDARY): random-panel calibration of the E1 limb ############")
print("Universe = %d complete-case genes minus %d marker genes present = %d genes (W02g-style exclusion)."
      % (X.shape[0], len(excluded), len(UNIV)))
print("NPANEL=%d per k, seed=%d, LGFMS point value = median over SUB250 (approximation, D2 only)." % (NPANEL, SEED))
uidx = np.array([idx[g] for g in UNIV])
rng2 = np.random.default_rng(SEED)
print("%3s %8s %10s %10s %10s %10s" % ("k","panels","E1BELOW_Rgene","E1ABOVE_Rgene","E1ABOVE_mean_r","E1BELOW_mean_r"))
d2 = {}
for k in (14, 12, 9):
    nb = na = mb = ma = 0; used = 0
    for _ in range(NPANEL):
        sel = rng2.choice(uidx, size=k, replace=False)
        G = X[sel]
        L = G[:, ARMS["LGFMS"]]
        vals = {"R_gene": [], "mean_r": []}
        bad = False
        for c in SUB250:
            Mc = L[:, list(c)]
            v1 = r_gene(Mc); v2 = mean_pair_r(Mc)
            vals["R_gene"].append(np.nan if v1 is None else v1)
            vals["mean_r"].append(np.nan if v2 is None else v2)
        for nm, fn in (("R_gene", r_gene), ("mean_r", mean_pair_r)):
            emc = fn(G[:, ARMS["EMC"]]); des = fn(G[:, ARMS["desmoid_fibromatosis"]]); fib = fn(G[:, ARMS["fibrosarcoma"]])
            if emc is None or des is None or fib is None: bad = True; break
            a = np.asarray(vals[nm], float); a = a[~np.isnan(a)]
            P = [float(np.median(a)), des, fib]; lo, hi = min(P), max(P)
            if nm == "R_gene":
                nb += (emc < lo); na += (emc > hi)
            else:
                mb += (emc < lo); ma += (emc > hi)
        if not bad: used += 1
    d2[k] = (used, nb, na, mb, ma)
    print("%3d %8d %10.4f %10.4f %10.4f %10.4f" % (k, used, nb/used, na/used, ma/used, mb/used))
print("\nPRE-DECLARED READING: if E1BELOW_Rgene for k=14 exceeds 0.05, the E1 limb is NOT evidence-grade")
print("for the fibro/ECM claim. Observed k=14 E1BELOW_Rgene = %.4f -> %s"
      % (d2[14][1]/d2[14][0], "NOT EVIDENCE-GRADE" if d2[14][1]/d2[14][0] > 0.05 else "within the declared bound"))
print("D2 constrains the E1 limb only; it says nothing about the E2 limb.")

print("""
============================================================================================
No biological, mechanistic or clinical claim follows from any outcome above.  array_percentile
is a within-array rank; six arrays are not six patients; only three comparator arms exist and a
four-arm rank can never reach alpha=0.05, so every rank statistic here is DESCRIPTIVE ONLY.
This is an ASSOCIATION at most.
============================================================================================""")
```

---

## Limitations

1. **SUBSTRATE LIMIT, restated as a limit.** The only input is a committed panel cache of 464 genes' `array_percentile` values on GPL6244. It is not an expression matrix; the matrix is not committed and fetching it is denied. Everything here is a statistic of a rank table.
2. **`array_percentile` is a within-array rank.** Correlations and variances on ranks are not correlations of abundance. No absolute expression statement is possible.
3. **Six arrays are not six patients.** EMC n=6, desmoid n=6, fibrosarcoma n=6. Nothing here is patient-level or clinical, and no mechanism follows. **Association at most.** No EMC efficacy, safety, selectivity or clinical-readiness claim is made or implied.
4. **Only three comparator arms exist and they are fixed by the deposit.** The arm-to-arm "spread" is three numbers. `E3` and — as D2 now shows — `E1` are both effectively four-arm rank tests and can never reach α = 0.05. `E2`'s apparent precision (12376 exhaustive subsamples) comes from resampling **one** arm: it measures within-LGFMS specimen sampling, **not** between-disease variability, and must not be read as if there were 12376 arms.
5. **The comparator arms are other sarcomas, several fibroblastic.** "Outside the comparator spread" means "unlike these three fibroblastic sarcoma arms", never "abnormal", "high" or "low" in any absolute sense.
6. **The AMBIGUOUS call is a real outcome of my own rule, not a hedge.** DISCRIMINANT required `N` on both; immune returned `P` because `E1` fired **upward**. My docstring pre-declared that an upward departure on a retired set is not the artefact signature, so the substantive reading in R7(a) is pre-declared, not post-hoc — but the formal call remains AMBIGUOUS and I have not relabelled it.
7. **The rule fires `U` on a retired set (tumour `mean_r`).** That is a genuine specificity failure of the `mean_r` limb, reported rather than minimised, and it was achieved at `mean_r` = 0.078, a trivial absolute magnitude.
8. **D1 and D2 use a 250-of-12376 seeded subset** for the LGFMS point value, an explicitly declared approximation. It applies to D1/D2 only; the six primary rows are exhaustive. D2's fractions carry Monte-Carlo error of roughly ±0.023 at 400 panels — far smaller than the gap between 0.295 and the 0.05 bound, so the conclusion is not sensitive to it.
9. **D1's `R_gene` at k=464 is numerically unstable**, as declared in advance; only D1's `mean_r` is read.
10. **No multiplicity correction** on the six primary rows, nor on the control's six re-run rows. Declared in advance, not repaired afterwards.
11. **W02c's caution stands:** the fibrosarcoma arm correlates with panel brightness at r = +0.845 on the endothelial axis and is a weak comparator generally. It sets the `E1` interval edge in several rows here.
12. **No repository file changed**, so no repository test tier applies. No preflight, no gate, no publication path, no graph or view touched. HEAD moved during the run and I verified rather than assumed that nothing outside the campaign directory changed.

---

## Stop condition

**Declared in the frozen docstring before the run:** *"Stop the moment the control row, the 2 x 3 primary verdict table, D1 and D2 have printed on a single execution with matching before / at-runtime / after script sha256 and matching source sha256. No further statistic is added, no threshold is moved, no tail is re-chosen, no post-hoc test is run."*

**MET.** All four blocks printed on the single execution (exit 0, 38.9 s); all three script hashes are `997944ce…0226c57b`; all three source hashes are `123bd05a…f336bd9`. No statistic was added, no threshold moved, no tail re-chosen after seeing a number. The one observation made after the numbers — that under *my* tail W02i's `mean_r` rows would have scored `U` — is labelled `[POST-HOC]` and scores nothing. Scratch deleted; returning immediately.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 17** (target ~40).
- **Wall clock: ~5 minutes of execution**, `date -u` 03:42:02Z → 03:46:47Z (target ~40 minutes), plus report composition. Script runtime 38.9 s.
- Under target because W02i's loader, statistics and enumeration were reusable verbatim and the question was sharply specified. I did not pad.

---

## Next concrete action

**W02i judged that lane 2 would be out of questions after this run. I disagree, narrowly and specifically, and my own result is the reason.** D2 measured the `E1` limb's false-fire rate at **0.295** and thereby moved the *entire* weight of the lane's one surviving claim onto the `E2` limb — which has **never been calibrated**. That makes one precise, falsifiable, no-new-data test available:

**Run the E2-limb calibration.** For each of N random k=14 panels drawn from the same 423-gene non-marker universe, compute EMC's `R_gene` and the **exhaustive** 12376 LGFMS six-specimen subsample distribution, and record the fraction of panels with `p_lo ≤ 0.05`. Pre-declare the reading before running: **if that fraction materially exceeds 0.05, the fibro/ECM `U` is dead** — the `E2` limb would then be firing at a rate incompatible with its nominal α, most plausibly because EMC's six arrays differ systematically from LGFMS six-array subsamples in a way that is gene-set-independent, and the lane's last claim goes with it. If the fraction is at or below 0.05, the `U` is calibrated and the lane has said everything this substrate can support. Cost: N × 12376 evaluations of a 14×6 statistic — roughly 150 s at N = 400 in the same pure-numpy form, well inside one worker's budget, seed-free on the LGFMS side and seeded only in the panel draw. It requires no new data, no network, no denied route.

**After that test, and only after it, I agree lane 2 is finished on this substrate.** Every further variant — more arms, transcriptome-wide universes, abundance instead of within-array rank, single-cell or spatial deconvolution (the lane's original subject) — needs the uncommitted GSE24369 expression matrix or a new deposit, and that route is denied.
