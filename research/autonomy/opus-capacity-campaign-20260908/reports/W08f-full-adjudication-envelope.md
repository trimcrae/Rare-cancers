> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

# W08f — Full-surface adjudication envelope for the EMC interval census

## Worker

Worker ID **W08f**, lane 8 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT ONLY, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). I did not and cannot observe the served model; no environment variable in this container names a model at all. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:39:03 UTC 2026`
`date -u` at end: `Tue Sep  8 02:41:32 UTC 2026`

**Actual HEAD read: `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`** (`/home/user/Rare-cancers`, `git status --porcelain` empty — clean tree). This is **not** the `92abbcb905cacf07f14b238db50d1b98f6590374` named in `COMMON-BRIEF.md`, nor W08d's `b9a0257e` nor W08e's `47aac85f`; the checkout has moved again. **No writes of any kind to the Git working tree; no git write operations; no network; no retrieval.** All execution in `/tmp/claude-0/w08f/`. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` was consulted read-only for the novelty check (not copied, not overlaid).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; re-run at end, md5 `d34e5ad074f671b813c93e14de5df58c`, byte-identical — the same hash W08d recorded):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...,*.svc.cluster.local
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=... -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=localhost,127.0.0.1,::1,...,*.svc.cluster.local
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...,*.svc.cluster.local
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(Four long proxy/no-proxy values elided mid-value with `...` for readability only; the full 51-line dump was printed in-session and hashes as above.)

## Question

**How wide can the EMC interval census be made without violating any single stated rule?** Concretely: extend W08e's three-variant sensitivity frame to **all twelve** of W08c's documented borderline calls, and produce (1) a leave-one-decision-out table over every *testable* call, (2) the two extreme envelopes bounding the census under defensible rules, and (3) a ranking of the calls by how much each moves the census — plus, as a prerequisite named in my dispatch, **verification of W08d's 108-month value against W08d's own report**, which W08e could not read.

It is open because W08e demonstrated adjudication-dependence on three calls only and explicitly named this extension as its successor, and because W08e's stability conclusions rested on a value it had taken from a dispatch prompt rather than from source.

## Prior-work check

```
$ git rev-parse HEAD
d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4
$ git status --porcelain | wc -l
0
$ rg -l -i "leave-one-decision-out|leave-one-out.*census|extreme envelope" --glob '!.git' | head -10
research/autonomy/opus-capacity-campaign-20260908/reports/W08e-adjudication-sensitivity.md
$ rg -l -i "most-inclusive rule set" --glob '!.git' /home/user/Rare-cancers /tmp/claude-0/frozen-corpus/extracted
/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports/W08e-adjudication-sensitivity.md
$ git ls-files | grep -i -E "W08|sensitivity"
.../reports/W06b-misclassification-sensitivity.md
.../reports/W08-disease-course-surveillance-question.md
.../reports/W08b-interval-census-adjudication.md
.../reports/W08c-blinded-third-adjudication.md
.../reports/W08d-unavailable-record-recovery.md
.../reports/W08e-adjudication-sensitivity.md
research/modalities/junction-anchor-convention-sensitivity.json
research/modalities/junction-transcript-sensitivity.json
research/modalities/junction_anchor_convention_sensitivity.py
research/modalities/junction_transcript_sensitivity.py
```

The only occurrences of "leave-one-decision-out", "extreme envelope" and "most-inclusive rule set" anywhere in the live tree **or the frozen corpus** are inside W08e's own *Next concrete action*, i.e. the task description, not a result. **No prior worker has computed this.** The `junction-*-sensitivity` artefacts are fusion-junction analyses, unrelated to the interval census. Note also that **W08d and W08e are now both tracked in Git** at this HEAD — W08e's stated transfer gap ("`W08d-*.md` does not exist on disk") has been closed by the coordinator, exactly as W08e requested.

Closed items confirmed **not** replayed (`CLOSED-WORK.md`): no publisher route of any kind, no Sunitinib 2014, Wagner 2020, CTARC 2022, Trabectedin/RT 2018, pazopanib or anthracycline route; **no retrieval or network at all** this pass. I did not touch PUB-EMC-CLASSIFICATION (user-rejected, closed) or any Brenca route. I did not open `emc-km-reachability-census-2026-08-25.json` or any cohort-level median, and **nothing here is pooled with one**. No content-policy refusal was encountered on any branch.

## Method / inputs

- **Inputs read in full:** `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W08c-blinded-third-adjudication.md`, `reports/W08d-unavailable-record-recovery.md`; `reports/W08e-adjudication-sensitivity.md` read for its worker block, its full sensitivity tables and its raw script output. All at HEAD `d3e9c4d8`.
- **No retrieval, no network, no new sources.** Every value used is already written down in W08c's report (the twelve borderline calls, with verbatim sentences and PMIDs) or in W08d's report (the one converted record).
- **Quartile estimator: W08c's, reproduced verbatim** — `def q(x,p): x=sorted(x); n=len(x); h=(n-1)*p; lo=int(h); hi=min(lo+1,n-1); return x[lo]+(h-lo)*(x[hi]-x[lo])` — linear interpolation on order statistics, `h=(n-1)p`. Median via `statistics.median`. Same as W08c and W08e.
- **Baseline (never replaced, always shown alongside):** Column A = W08c's blinded A1–A8 plus W08d's converted PMID 36097623 @ 108 mo → `[10,16,24,26,34,48,60,74,108]`, n=9. Column B = W08c's B1–B5 unchanged → `[16,29,36,42,168]`, n=5. **W08c's, W08d's and W08e's sets are not revised by this report.**
- Script `/tmp/claude-0/w08f/envelope.py`, run in `/tmp/claude-0/w08f` (outside the Git tree).

### Verification of W08d's 108-month value — the dispatch's priority item

**VERIFIED. The value matches; W08e's transferred grading was correct.** W08d's own report states, in its per-record outcome table and in a dedicated "The one admitted event" block: PMID **36097623**, PMCID **PMC9463557**, DOI 10.1016/j.jdcr.2022.08.012, **Months = 108**, anchor "initial diagnosis / primary surgery (left below-knee amputation)", admitted as a Column A event and labelled `PRIMARY`, with the verbatim admitting sentence *"…was considered disease-free for 9 years before presenting to the dermatology clinic for a forehead mass presumed to be a lipoma."* W08d's own union table gives Column A n=9, median 34, max 108, `>120 mo: 0 of 9` — **identical to the baseline W08e reconstructed from its prompt.** So no correction to W08e is required on the value.

**Two things W08e could not have known, which I record as focused additions rather than corrections:**

1. **W08d flags a real 108-vs-96-month ambiguity in the same source** — the article also states the mass *"was noted 1 year before presentation after a minor forehead trauma"*; an adjudicator dating the metastasis to first notice rather than diagnosis would enter **96**, not 108. W08d chose 108 because that is the value the source states with an explicit anchor, and flagged the alternative. **This does not disturb W08e's conclusion**: 96 and 108 both lie strictly between 74 and 120, so "Column A max = 108" becomes "max = 96 or 108" while "no Column A event beyond 120 months" survives either way. This is a **thirteenth** borderline call, contributed by W08d, and I test it below as C13.
2. W08d **upgrades** W08c's evidence grade for that event: it is `PRIMARY` (full text retrieved from PMC, PMID verified against the request under W10c's tool-defect guard), not the `SECONDARY (TRANSFERRED)` that W08e was obliged to use. Every row W08e marked "PRIMARY + 1 SECONDARY(transferred)" may now be read as **PRIMARY throughout**.

### Which of the twelve are testable

A call is **testable** only if W08c recorded a determinate numeric value that flipping would move into or out of a column. Where the *value* is unknown rather than merely the admissibility, the call is **not flippable** and is excluded from the envelopes rather than given an invented number.

| # | W08c borderline call | Testable? | Flip and value | Direction / kind |
|---|---|---|---|---|
| 1 | PMID 10469211 unanchored "12 weeks / 10 months", excluded from A | **YES** (`C1`) | ADMIT 2.8 and 10 to A | incl / judgement |
| 2 | PMID 18308379 A6 @48, included despite possible unreported earlier distant event | **YES** (`C2`) | WITHDRAW 48 from A | excl / judgement |
| 3 | PMID 30534357 A3 @24: year-granular "after 2 years"; pelvic disease not counted as local | **YES, two sub-flips** (`C3a`,`C3b`) | (a) WITHDRAW 24 from A; (b) ADMIT pelvic disease @24 to B | (a) excl/judgement; (b) incl/redefinition |
| 4 | PMID 15810095 pancreatic met @240, excluded as not the *first* distant met | **YES** (`C4`) | ADMIT 240 to A | incl / redefinition |
| 5 | PMID 3731040, metastases *preceding* the primary by 10 y and 2 y | **NO** | No interval from primary to metastasis exists; the recorded values run the wrong way. Flipping requires violating Rule A's explicit exclusion, not loosening a judgement | — |
| 6 | PMID 21547635 "died 16 months after surgery owing to abdominal wall recurrence" | **NO** | 16 months is an interval to **death**; the recurrence's own date is not stated. Entering 16 would impute a value | — |
| 7 | PMID 1531226 "recurred 14 years after the first resection" — the *second* recurrence | **YES** (`C7`) | ADMIT 168 to B | incl / redefinition |
| 8 | PMID 22743288 combined SS+EMC @84, excluded on histology | **YES** (`C8`) | ADMIT 84 to B | incl / judgement |
| 9 | PMID 22446404 canine EMC, excluded as non-human | **NO** | W08c recorded no interval for it at all | — |
| 10 | PMID 38111543 excluded from A because pulmonary mets were synchronous | **NO** | "Synchronous" is categorical; **no elapsed value is recorded**. Entering 0 would be my assumption, not W08c's record. (Flagged: under an assumed 0 it would be the single largest downward mover in the table — an adjudicator wanting the widest census should note this, but I will not manufacture the number) | — |
| 11 | Non-EMC histologies excluded on sight (9 PMIDs) | **NO** | W08c recorded no interval for any of them | — |
| 12 | Osseous-primary EMC treated as EMC (23588370, 28249774, 9149016) | **YES** (`C12`) | WITHDRAW 26, 74 from A and 36 from B (28249774 and 9149016 contribute no values) | excl / judgement |
| **13** | *(from W08d, not W08c)* 36097623 at 108 vs 96 months | **YES** (`C13`, reported separately) | SUBSTITUTE 96 for 108 in A | value-choice / judgement |

**Testable: 7 of the 12 calls** (calls 1, 2, 3, 4, 7, 8, 12), yielding **8 single flips** because call 3 has two independently flippable components. **Not testable: 5 of the 12** (calls 5, 6, 9, 10, 11) — in every one of those five the *value* is missing, not merely the admissibility, so they are excluded from the envelopes as the dispatch requires.

I additionally classify each testable flip as an **admissibility judgement** (the wording of Rule A/B is unchanged; only how strictly it is applied moves) or an **endpoint redefinition** (the flip changes what "first" or "local" means). The question asked — how wide the census can be made *without violating any single stated rule* — is answered by the **judgement-only** envelope; the redefinition envelope is reported as a strictly wider bound that does change a rule, so it is labelled and kept separate.

## Result

Units are **months**. Every `n` and every `>t` figure is a **count of published case-report events** — never a rate, risk, incidence, cumulative incidence, hazard or probability. **The frame has no denominator.** UNKNOWN records (the 3 of 84 W08d fixed as permanently unretrievable, plus the canine exclusion) remain **excluded, never imputed**. **Anchors are heterogeneous and unharmonised** — Column A mixes primary surgery, initial diagnosis, primary detection and "definitive therapy"; Column B mixes initial surgery, primary resection, initial diagnosis and "definitive therapy" — so these are descriptive summaries of a mixed-anchor list, not estimates of one clock. Every variant is shown **alongside** the baseline, never in place of it, and the variants must **not** be combined into a single "corrected" census.

### Baseline (`PRIMARY` throughout, per W08d's verification above)

| Column | n | values | min | Q1 | median | Q3 | max | >24 mo | >60 mo | >120 mo |
|---|---|---|---|---|---|---|---|---|---|---|
| A — first distant/regional metastasis | 9 | 10,16,24,26,34,48,60,74,108 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| B — first local recurrence | 5 | 16,29,36,42,168 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |

### 1. Leave-one-decision-out — each testable call flipped alone

Column A (`PRIMARY`; for C1 the anchor of the two added events is UNKNOWN):

| Flip | n | min | Q1 | median | Q3 | max | >24 | >60 | >120 |
|---|---|---|---|---|---|---|---|---|---|
| *baseline* | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| `C1` admit 10469211 (2.8, 10) | 11 | **2.8** | **13.00** | **26.00** | 54.00 | 108 | 6 of 11 | 2 of 11 | 0 of 11 |
| `C2` withdraw 18308379 @48 | 8 | 10 | 22.00 | 30.00 | 63.50 | 108 | 5 of 8 | 2 of 8 | 0 of 8 |
| `C3a` withdraw 30534357 @24 | 8 | 10 | 23.50 | **41.00** | 63.50 | 108 | 6 of 8 | 2 of 8 | 0 of 8 |
| `C3b` admit pelvic @24 to B | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| `C4` admit 15810095 @240 | 10 | 10 | 24.50 | **41.00** | 70.50 | **240** | 7 of 10 | 3 of 10 | **1 of 10** |
| `C7` admit 1531226 @168 to B | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| `C8` admit 22743288 @84 to B | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| `C12` withdraw osseous EMC | 7 | 10 | 20.00 | 34.00 | 54.00 | 108 | 4 of 7 | 1 of 7 | 0 of 7 |

Column B (`PRIMARY`; C8's row is histologically mixed by construction):

| Flip | n | min | Q1 | median | Q3 | max | >24 | >60 | >120 |
|---|---|---|---|---|---|---|---|---|---|
| *baseline* | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| `C1` | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| `C2` | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| `C3a` | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| `C3b` admit pelvic @24 | 6 | 16 | 25.25 | **32.50** | 40.50 | 168 | 4 of 6 | 1 of 6 | 1 of 6 |
| `C4` | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| `C7` admit 1531226 @168 | 6 | 16 | 30.75 | 39.00 | **136.50** | 168 | 5 of 6 | 2 of 6 | **2 of 6** |
| `C8` admit 22743288 @84 | 6 | 16 | 30.75 | 39.00 | 73.50 | 168 | 5 of 6 | 2 of 6 | 1 of 6 |
| `C12` withdraw osseous EMC | 4 | 16 | 25.75 | 35.50 | 73.50 | 168 | 3 of 4 | 1 of 4 | 1 of 4 |

**Estimator-agreement check (RUN):** `C1` reproduces W08e's V1 row exactly, `C12` reproduces its V2 rows exactly (A: n=7, Q1 20.00, median 34.00, Q3 54.00; B: n=4, Q1 25.75, median 35.50, Q3 73.50), and `C8` reproduces its V3 Column B row exactly (n=6, Q1 30.75, median 39.00, Q3 73.50). W08c's estimator was carried across three independent workers without drift.

### `C13` — W08d's 108-vs-96 value choice, tested separately

Substituting 96 for 108 in Column A gives `[10,16,24,26,34,48,60,74,96]`: n=9, min 10, Q1 24.00, median 34.00, Q3 60.00, **max 96**, `>24` 6 of 9, `>60` 2 of 9, **`>120` 0 of 9**. Only the maximum moves. **W08e's "no Column A event beyond 120 months" conclusion is robust to this ambiguity**, and its "maximum is 108" should be stated as "maximum is 96 or 108, depending on how the source's two dates are read".

### 2. The two extreme envelopes

| Envelope | Flips applied | Col | n | min | Q1 | median | Q3 | max | >24 | >60 | >120 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *baseline* | — | A | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| *baseline* | — | B | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| **MOST-INCLUSIVE, no rule violated** (judgement flips only) | C1, C8 | A | **11** | **2.8** | **13.00** | **26.00** | 54.00 | 108 | 6 of 11 | 2 of 11 | 0 of 11 |
| | | B | **6** | 16 | 30.75 | 39.00 | 73.50 | 168 | 5 of 6 | 2 of 6 | 1 of 6 |
| **MOST-EXCLUSIVE, no rule violated** (all exclusion flips; all judgement-type) | C2, C3a, C12 | A | **5** | 10 | **16.00** | 34.00 | 60.00 | 108 | 3 of 5 | 1 of 5 | 0 of 5 |
| | | B | **4** | 16 | 25.75 | 35.50 | 73.50 | 168 | 3 of 4 | 1 of 4 | 1 of 4 |
| *(wider bound, but a rule is redefined)* MOST-INCLUSIVE incl. endpoint redefinitions | C1, C3b, C4, C7, C8 | A | 12 | 2.8 | 14.50 | 30.00 | 63.50 | **240** | 7 of 12 | 3 of 12 | **1 of 12** |
| | | B | 8 | 16 | 27.75 | 39.00 | 105.00 | 168 | 6 of 8 | 3 of 8 | 2 of 8 |

**The answer to the question, stated plainly.** Holding every stated rule intact and moving only how strictly each borderline call is applied, the census spans:

- **Column A: n between 5 and 11 events** (baseline 9) — a factor of 2.2 in event count. Median **34.00 → between 26.00 and 34.00**. Q1 **13.00 → 24.00**, an 11-month spread. Minimum **2.8 → 10**, a factor of 3.6. Maximum is **108 in every rule-preserving variant**, and **no Column A event exceeds 120 months under any rule-preserving variant**.
- **Column B: n between 4 and 6 events** (baseline 5). Median **35.50 → 39.00**, a 3.5-month band — the most stable quantity in the whole exercise. Minimum 16 and maximum 168 are **invariant**, and **exactly one** Column B event exceeds 120 months under every rule-preserving variant.
- **Only if a stated endpoint definition is redefined** does anything qualitative change: dropping "first" from Rule A admits PMID 15810095's 240-month pancreatic deposit, which is the **only** way in the entire testable surface to place a Column A event beyond 120 months, and dropping "first" from Rule B puts a second event beyond 120 months in Column B.

### 3. Ranking by movement — which judgements are load-bearing

Ranked by composite `|ΔmedianA| + |ΔmedianB|` (months), tie-broken by `|Δmax|` then `|Δn|`; `|ΔQ1|` and `|ΔQ3|` shown because the median is not the only thing an owner cares about.

| Rank | Call | \|Δmedian\| | \|Δmax\| | \|Δn\| | \|ΔQ1\| | \|ΔQ3\| | Direction / kind | What it decides |
|---|---|---|---|---|---|---|---|---|
| 1 | `C1` 10469211 unanchored | **8.00** | 0.0 | 2 | **11.00** | 6.00 | incl / judgement | **Load-bearing.** Owns the shortest documented Column A interval and the whole lower tail |
| 2 | `C4` 15810095 @240 | 7.00 | **132.0** | 1 | 0.50 | 10.50 | incl / **redefinition** | **Load-bearing.** The sole route to any Column A event beyond 120 months |
| 3 | `C3a` 30534357 @24 | 7.00 | 0.0 | 1 | 0.50 | 3.50 | excl / judgement | **Load-bearing.** Moves Column A's median from 34 to 41 on its own |
| 4 | `C2` 18308379 @48 | 4.00 | 0.0 | 1 | 2.00 | 3.50 | excl / judgement | Moderate. Median 34 → 30 |
| 5 | `C3b` pelvic @24 to B | 3.50 | 0.0 | 1 | 3.75 | 1.50 | incl / redefinition | Moderate. The only flip that lowers Column B's median |
| 6 | `C7` 1531226 @168 to B | 3.00 | 0.0 | 1 | 1.75 | **94.50** | incl / redefinition | **Load-bearing on the upper tail only** — the median barely moves while Q3 moves 94.5 months |
| 7 | `C8` 22743288 @84 to B | 3.00 | 0.0 | 1 | 1.75 | 31.50 | incl / judgement | Moderate; Q3 +31.5 |
| 8 | `C12` osseous EMC | 0.50 | 0.0 | **3** | 7.25 | 37.50 | excl / judgement | **Cosmetic on the medians, decisive on the counts** — removes 3 of 14 events while moving both medians by ≤0.5 mo |

**The ranking metric matters and I state its limits.** By median movement the osseous-EMC call (`C12`) looks cosmetic — yet it is the single largest change in *event count* in the table (3 of 14 events, a 21% reduction) and moves Column A's Q1 by 7.25 and Column B's Q3 by 37.5 months. Likewise `C7` ranks 6th on median but 1st on Q3. **An owner reading only the median column would draw the wrong conclusion about which judgements matter.** The honest summary is: `C1` and `C3a` dominate the medians; `C4` alone controls whether anything sits beyond 120 months; `C12` alone controls the census's size; `C7` and `C8` control the Column B upper tail.

**Everything that survives the whole rule-preserving surface (STABLE):** Column A's maximum (108, or 96 under `C13`); no Column A event beyond 120 months; Column B's minimum (16) and maximum (168); exactly one Column B event beyond 120 months; Column B's median inside 35.5–39.0; both columns remaining small (A: 5–11 events; B: 4–6). **Everything that does not (UNSTABLE):** Column A's minimum, Q1 and event count; whether a majority of Column A events exceeded 24 months (6 of 9 at baseline, but 3 of 5 and 6 of 11 at the envelopes — a bare majority either way, and it must never be asserted without naming the rule set).

## Validation evidence

**RUN.** Environment: `Linux 6.18.44-fc-v24 x86_64`, `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, cwd `/tmp/claude-0/w08f` (outside the Git tree). Repository HEAD read `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`, `git status --porcelain` empty.

Command: `$ cd /tmp/claude-0/w08f && python3 envelope.py; echo "EXIT=$?"` → **`EXIT=0`**.

Script `/tmp/claude-0/w08f/envelope.py`, reproduced in full:

```python
import statistics as st

# ---- W08c's exact quartile estimator, reproduced verbatim (linear interpolation, h=(n-1)p)
def q(x,p):
    x=sorted(x); n=len(x); h=(n-1)*p; lo=int(h); hi=min(lo+1,n-1)
    return x[lo]+(h-lo)*(x[hi]-x[lo])

# ---- BASELINE: W08c Column A (n=8) + W08d's converted PMID 36097623 @ 108 mo ; W08c Column B (n=5)
A_BASE=[10,16,24,26,34,48,60,74,108]
B_BASE=[16,29,36,42,168]

# ---- Flips. add_A/add_B = values admitted; rm_A/rm_B = values withdrawn. Months.
# dir: 'incl' (admits events) / 'excl' (withdraws events). kind: 'judgement' / 'redefinition'.
FLIPS=[
 ("C1","10469211 unanchored 12wk+10mo -> ADMIT to A","incl","judgement",[2.8,10],[],[],[]),
 ("C2","18308379 A6@48 -> WITHDRAW (may not be first distant)","excl","judgement",[],[],[48],[]),
 ("C3a","30534357 A3@24 -> WITHDRAW (year-granular 'after 2 years')","excl","judgement",[],[],[24],[]),
 ("C3b","30534357 pelvic disease @24 -> ADMIT to B as locoregional","incl","redefinition",[],[24],[],[]),
 ("C4","15810095 pancreatic met @240 -> ADMIT to A (not the first distant)","incl","redefinition",[240],[],[],[]),
 ("C7","1531226 recurrence @168 -> ADMIT to B (second, not first)","incl","redefinition",[],[168],[],[]),
 ("C8","22743288 combined SS+EMC @84 -> ADMIT to B","incl","judgement",[],[84],[],[]),
 ("C12","osseous-primary EMC (23588370) -> WITHDRAW","excl","judgement",[],[],[26,74],[36]),
]

def apply(flips):
    A=list(A_BASE); B=list(B_BASE)
    for f in flips:
        _,_,_,_,aA,aB,rA,rB=f
        A+=aA; B+=aB
        for v in rA: A.remove(v)
        for v in rB: B.remove(v)
    return sorted(A), sorted(B)

def row(label,v):
    if not v: return f"{label:<58}| n=0 | EMPTY SET"
    s=(f"{label:<58}| n={len(v):<2}| min={min(v):<6} Q1={q(v,.25):<7.2f} median={st.median(v):<7.2f} "
       f"Q3={q(v,.75):<7.2f} max={max(v):<5}| >24:{sum(1 for x in v if x>24)} of {len(v)}"
       f"  >60:{sum(1 for x in v if x>60)} of {len(v)}  >120:{sum(1 for x in v if x>120)} of {len(v)}")
    return s

def stats(v):
    if not v: return None
    return dict(n=len(v),mn=min(v),q1=q(v,.25),md=st.median(v),q3=q(v,.75),mx=max(v),
                t24=sum(1 for x in v if x>24),t60=sum(1 for x in v if x>60),t120=sum(1 for x in v if x>120))

print("="*150)
print("EVERY n AND EVERY '>t months' FIGURE IS A COUNT OF PUBLISHED CASE-REPORT EVENTS.")
print("NOT a rate, risk, incidence or probability. THE FRAME HAS NO DENOMINATOR.")
print("Anchors heterogeneous and unharmonised. UNKNOWN records excluded, never imputed.")
print("Quartile estimator: W08c's, linear interpolation on order statistics, h=(n-1)p.")
print("="*150)
print()
print("--- BASELINE (W08c blinded sets + W08d PMID 36097623 @ 108 mo) ---")
print(row("BASELINE A: first distant/regional metastasis",A_BASE))
print(row("BASELINE B: first local recurrence",B_BASE))
print("  A values:",A_BASE)
print("  B values:",B_BASE)
print()
print("--- 1. LEAVE-ONE-DECISION-OUT: each borderline call flipped ALONE against the baseline ---")
loo={}
for f in FLIPS:
    cid,desc,d,k,_,_,_,_=f
    A,B=apply([f])
    loo[cid]=(stats(A),stats(B),desc,d,k)
    print(f"[{cid}] {desc}   ({d}/{k})")
    print("   "+row("  A",A))
    print("   "+row("  B",B))
    print(f"     A values: {A}")
    print(f"     B values: {B}")
print()
print("--- 2. EXTREME ENVELOPES ---")
strict_in=[f for f in FLIPS if f[2]=="incl" and f[3]=="judgement"]
broad_in=[f for f in FLIPS if f[2]=="incl"]
excl=[f for f in FLIPS if f[2]=="excl"]
for lbl,fl in (("MOST-INCLUSIVE (strict: rule-consistent judgement flips only)",strict_in),
               ("MOST-INCLUSIVE (broad: also endpoint redefinitions)",broad_in),
               ("MOST-EXCLUSIVE (all exclusion flips; all are judgement-type)",excl)):
    A,B=apply(fl)
    print(f"{lbl}  [{', '.join(f[0] for f in fl)}]")
    print("   "+row("  A",A)); print(f"     A values: {A}")
    print("   "+row("  B",B)); print(f"     B values: {B}")
    print()
print("--- 3. RANKING BY MOVEMENT (composite = |dMedianA|+|dMedianB|, tiebreak |dMax|, then |dn|) ---")
b=(stats(A_BASE),stats(B_BASE))
rank=[]
for cid,(sa,sb,desc,d,k) in loo.items():
    dmd=abs(sa['md']-b[0]['md'])+abs(sb['md']-b[1]['md'])
    dmx=abs(sa['mx']-b[0]['mx'])+abs(sb['mx']-b[1]['mx'])
    dn=abs(sa['n']-b[0]['n'])+abs(sb['n']-b[1]['n'])
    dq1=abs(sa['q1']-b[0]['q1'])+abs(sb['q1']-b[1]['q1'])
    dq3=abs(sa['q3']-b[0]['q3'])+abs(sb['q3']-b[1]['q3'])
    rank.append((dmd,dmx,dn,dq1,dq3,cid,desc,d,k))
rank.sort(key=lambda r:(-r[0],-r[1],-r[2]))
print(f"{'rk':<3}{'call':<5}{'|dMedian|':>10}{'|dMax|':>8}{'|dn|':>6}{'|dQ1|':>8}{'|dQ3|':>8}  direction/kind")
for i,(dmd,dmx,dn,dq1,dq3,cid,desc,d,k) in enumerate(rank,1):
    print(f"{i:<3}{cid:<5}{dmd:>10.2f}{dmx:>8.1f}{dn:>6}{dq1:>8.2f}{dq3:>8.2f}  {d}/{k}  {desc}")
```

Verbatim output (complete):

```
======================================================================================================================================================
EVERY n AND EVERY '>t months' FIGURE IS A COUNT OF PUBLISHED CASE-REPORT EVENTS.
NOT a rate, risk, incidence or probability. THE FRAME HAS NO DENOMINATOR.
Anchors heterogeneous and unharmonised. UNKNOWN records excluded, never imputed.
Quartile estimator: W08c's, linear interpolation on order statistics, h=(n-1)p.
======================================================================================================================================================

--- BASELINE (W08c blinded sets + W08d PMID 36097623 @ 108 mo) ---
BASELINE A: first distant/regional metastasis             | n=9 | min=10     Q1=24.00   median=34.00   Q3=60.00   max=108  | >24:6 of 9  >60:2 of 9  >120:0 of 9
BASELINE B: first local recurrence                        | n=5 | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168  | >24:4 of 5  >60:1 of 5  >120:1 of 5
  A values: [10, 16, 24, 26, 34, 48, 60, 74, 108]
  B values: [16, 29, 36, 42, 168]

--- 1. LEAVE-ONE-DECISION-OUT: each borderline call flipped ALONE against the baseline ---
[C1] 10469211 unanchored 12wk+10mo -> ADMIT to A   (incl/judgement)
     A                                                       | n=11| min=2.8    Q1=13.00   median=26.00   Q3=54.00   max=108  | >24:6 of 11  >60:2 of 11  >120:0 of 11
     B                                                       | n=5 | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168  | >24:4 of 5  >60:1 of 5  >120:1 of 5
     A values: [2.8, 10, 10, 16, 24, 26, 34, 48, 60, 74, 108]
     B values: [16, 29, 36, 42, 168]
[C2] 18308379 A6@48 -> WITHDRAW (may not be first distant)   (excl/judgement)
     A                                                       | n=8 | min=10     Q1=22.00   median=30.00   Q3=63.50   max=108  | >24:5 of 8  >60:2 of 8  >120:0 of 8
     B                                                       | n=5 | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168  | >24:4 of 5  >60:1 of 5  >120:1 of 5
     A values: [10, 16, 24, 26, 34, 60, 74, 108]
     B values: [16, 29, 36, 42, 168]
[C3a] 30534357 A3@24 -> WITHDRAW (year-granular 'after 2 years')   (excl/judgement)
     A                                                       | n=8 | min=10     Q1=23.50   median=41.00   Q3=63.50   max=108  | >24:6 of 8  >60:2 of 8  >120:0 of 8
     B                                                       | n=5 | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168  | >24:4 of 5  >60:1 of 5  >120:1 of 5
     A values: [10, 16, 26, 34, 48, 60, 74, 108]
     B values: [16, 29, 36, 42, 168]
[C3b] 30534357 pelvic disease @24 -> ADMIT to B as locoregional   (incl/redefinition)
     A                                                       | n=9 | min=10     Q1=24.00   median=34.00   Q3=60.00   max=108  | >24:6 of 9  >60:2 of 9  >120:0 of 9
     B                                                       | n=6 | min=16     Q1=25.25   median=32.50   Q3=40.50   max=168  | >24:4 of 6  >60:1 of 6  >120:1 of 6
     A values: [10, 16, 24, 26, 34, 48, 60, 74, 108]
     B values: [16, 24, 29, 36, 42, 168]
[C4] 15810095 pancreatic met @240 -> ADMIT to A (not the first distant)   (incl/redefinition)
     A                                                       | n=10| min=10     Q1=24.50   median=41.00   Q3=70.50   max=240  | >24:7 of 10  >60:3 of 10  >120:1 of 10
     B                                                       | n=5 | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168  | >24:4 of 5  >60:1 of 5  >120:1 of 5
     A values: [10, 16, 24, 26, 34, 48, 60, 74, 108, 240]
     B values: [16, 29, 36, 42, 168]
[C7] 1531226 recurrence @168 -> ADMIT to B (second, not first)   (incl/redefinition)
     A                                                       | n=9 | min=10     Q1=24.00   median=34.00   Q3=60.00   max=108  | >24:6 of 9  >60:2 of 9  >120:0 of 9
     B                                                       | n=6 | min=16     Q1=30.75   median=39.00   Q3=136.50  max=168  | >24:5 of 6  >60:2 of 6  >120:2 of 6
     A values: [10, 16, 24, 26, 34, 48, 60, 74, 108]
     B values: [16, 29, 36, 42, 168, 168]
[C8] 22743288 combined SS+EMC @84 -> ADMIT to B   (incl/judgement)
     A                                                       | n=9 | min=10     Q1=24.00   median=34.00   Q3=60.00   max=108  | >24:6 of 9  >60:2 of 9  >120:0 of 9
     B                                                       | n=6 | min=16     Q1=30.75   median=39.00   Q3=73.50   max=168  | >24:5 of 6  >60:2 of 6  >120:1 of 6
     A values: [10, 16, 24, 26, 34, 48, 60, 74, 108]
     B values: [16, 29, 36, 42, 84, 168]
[C12] osseous-primary EMC (23588370) -> WITHDRAW   (excl/judgement)
     A                                                       | n=7 | min=10     Q1=20.00   median=34.00   Q3=54.00   max=108  | >24:4 of 7  >60:1 of 7  >120:0 of 7
     B                                                       | n=4 | min=16     Q1=25.75   median=35.50   Q3=73.50   max=168  | >24:3 of 4  >60:1 of 4  >120:1 of 4
     A values: [10, 16, 24, 34, 48, 60, 108]
     B values: [16, 29, 42, 168]

--- 2. EXTREME ENVELOPES ---
MOST-INCLUSIVE (strict: rule-consistent judgement flips only)  [C1, C8]
     A                                                       | n=11| min=2.8    Q1=13.00   median=26.00   Q3=54.00   max=108  | >24:6 of 11  >60:2 of 11  >120:0 of 11
     A values: [2.8, 10, 10, 16, 24, 26, 34, 48, 60, 74, 108]
     B                                                       | n=6 | min=16     Q1=30.75   median=39.00   Q3=73.50   max=168  | >24:5 of 6  >60:2 of 6  >120:1 of 6
     B values: [16, 29, 36, 42, 84, 168]

MOST-INCLUSIVE (broad: also endpoint redefinitions)  [C1, C3b, C4, C7, C8]
     A                                                       | n=12| min=2.8    Q1=14.50   median=30.00   Q3=63.50   max=240  | >24:7 of 12  >60:3 of 12  >120:1 of 12
     A values: [2.8, 10, 10, 16, 24, 26, 34, 48, 60, 74, 108, 240]
     B                                                       | n=8 | min=16     Q1=27.75   median=39.00   Q3=105.00  max=168  | >24:6 of 8  >60:3 of 8  >120:2 of 8
     B values: [16, 24, 29, 36, 42, 84, 168, 168]

MOST-EXCLUSIVE (all exclusion flips; all are judgement-type)  [C2, C3a, C12]
     A                                                       | n=5 | min=10     Q1=16.00   median=34.00   Q3=60.00   max=108  | >24:3 of 5  >60:1 of 5  >120:0 of 5
     A values: [10, 16, 34, 60, 108]
     B                                                       | n=4 | min=16     Q1=25.75   median=35.50   Q3=73.50   max=168  | >24:3 of 4  >60:1 of 4  >120:1 of 4
     B values: [16, 29, 42, 168]

--- 3. RANKING BY MOVEMENT (composite = |dMedianA|+|dMedianB|, tiebreak |dMax|, then |dn|) ---
rk call  |dMedian|  |dMax|  |dn|   |dQ1|   |dQ3|  direction/kind
1  C1         8.00     0.0     2   11.00    6.00  incl/judgement  10469211 unanchored 12wk+10mo -> ADMIT to A
2  C4         7.00   132.0     1    0.50   10.50  incl/redefinition  15810095 pancreatic met @240 -> ADMIT to A (not the first distant)
3  C3a        7.00     0.0     1    0.50    3.50  excl/judgement  30534357 A3@24 -> WITHDRAW (year-granular 'after 2 years')
4  C2         4.00     0.0     1    2.00    3.50  excl/judgement  18308379 A6@48 -> WITHDRAW (may not be first distant)
5  C3b        3.50     0.0     1    3.75    1.50  incl/redefinition  30534357 pelvic disease @24 -> ADMIT to B as locoregional
6  C7         3.00     0.0     1    1.75   94.50  incl/redefinition  1531226 recurrence @168 -> ADMIT to B (second, not first)
7  C8         3.00     0.0     1    1.75   31.50  incl/judgement  22743288 combined SS+EMC @84 -> ADMIT to B
8  C12        0.50     0.0     3    7.25   37.50  excl/judgement  osseous-primary EMC (23588370) -> WITHDRAW
EXIT=0
Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]
Linux 6.18.44-fc-v24 x86_64
```

The `C13` figures quoted above were obtained by the same estimator on `[10,16,24,26,34,48,60,74,96]`; only `max` differs from the baseline row (96 vs 108), every other statistic being identical because 96 and 108 occupy the same order-statistic position.

**PROPOSED (NOT RUN):** none. No repository test suite, no `scripts/preflight.sh`, no lint — this worker is read-only on the tree and its dispatch did not call for them. No content-policy refusal was encountered on any branch.

## Limitations

- **Every number in this report is a count of published case-report events. None is a rate, risk, incidence, cumulative incidence, hazard or probability. The frame has no denominator**, there is no cohort at risk, and nothing here supports a survival or hazard estimate.
- **No surveillance interval, imaging schedule, follow-up duration or clinical recommendation is stated or implied anywhere in this report, and none may be derived from it.** The envelopes exist to show that the census's summary statistics are adjudication-dependent, which is a reason for *more* caution about any downstream use, not less.
- **The envelopes are bounds on rule-choice, not on truth.** They quantify how much the *adjudicator's* discretion can move the census. They say nothing about publication bias, which is severe and one-directional in a case-report frame, nor about the 3 of 84 records W08d fixed as permanently unretrievable — those remain UNKNOWN, excluded and never imputed, and both columns remain undercounts of unquantified size on top of everything shown here.
- **Anchors are heterogeneous and unharmonised** across and within every variant. Do not average across anchors as if they were one clock.
- **5 of the 12 borderline calls were not testable** (calls 5, 6, 9, 10, 11) because the *value* is missing, not merely the admissibility. The envelopes are therefore bounds over a **7-of-12 subset**, and the true rule-surface may be wider than reported. Call 10 (PMID 38111543, synchronous pulmonary metastases) is the one I would most expect to widen it further: under an assumed 0-month value it would be the largest single downward mover in the table, and I declined to enter that number because W08c recorded no elapsed value.
- **`C12` withdraws only 23588370's values.** W08c's osseous-EMC call also names 28249774 and 9149016, but neither contributes an admitted value, so the flip's numeric effect is entirely 23588370's — an owner should not read `C12` as "the full cost of excluding osseous EMC" across the wider literature.
- **The ranking depends on the metric chosen** and I have shown the disagreement explicitly (`C12` is 8th by median and 1st by event count; `C7` is 6th by median and 1st by Q3). There is no single correct ordering.
- **The 108-vs-96 ambiguity is real and unresolved by the source.** I verified W08d's value and its reasoning; I did not adjudicate between them, and I did not retrieve the source.
- **W08c's, W08d's and W08e's sets are not revised.** Every variant is presented alongside the baseline, never in place of it, and the variants must not be combined into a single "corrected" census. Nothing here is pooled with any cohort-level median in this repository.
- **Model identity is self-reported and unverified.** The read HEAD (`d3e9c4d8`) differs from the brief's frozen commit and from both predecessors' HEADs, as recorded above.

## Stop condition

**MET**, all four components:

1. **W08d's 108-month value verified against W08d's own report** — matches exactly (PMID 36097623, PMC9463557, 108 months, Column A, `PRIMARY`), so W08e's transferred grading was correct and its "no Column A event beyond 120 months" conclusion stands. Two additions W08e could not see are recorded: the 96-month alternative W08d flagged (tested as `C13`; conclusion robust) and the upgrade of that row from `SECONDARY (TRANSFERRED)` to `PRIMARY`.
2. **Leave-one-decision-out table over every testable borderline call** — 8 single flips covering 7 of the 12 calls, both columns, with n / min / Q1 / median / Q3 / max and counts beyond 24/60/120 months; 5 calls documented as not testable with the reason.
3. **Both extreme envelopes computed** — most-inclusive and most-exclusive under rule-preserving judgement flips, plus a separately labelled wider bound that requires redefining an endpoint.
4. **Ranking by movement produced**, with the metric's limits stated.

All computed with a real command (`python3 envelope.py`) in a stated environment, **exit code 0**. Three independent cross-checks against W08e's published rows (`C1`≡V1, `C12`≡V2, `C8`≡V3-B) confirm W08c's estimator was carried across without drift. I returned as soon as the condition was met.

## Tool-call and wall-clock count actually used

**7 tool calls**, all Bash (1 env/HEAD probe + scratch dir, 1 brief read, 1 W08c read, 1 W08d read, 1 W08e read, 1 combined W08e-table read + prior-work check, 1 script write-and-run; plus 1 closing probe = 8 including the end-timestamp call). No MCP calls, no ToolSearch, no network, no retrieval. Wall clock `02:39:03` → `02:41:32` UTC, approximately **2.5 minutes** — well inside the ~40 minute / ~40 call target.

## Next concrete action

The rule-sensitivity axis in this lane is now **closed to the limit of what W08c recorded**: all twelve calls are classified, the seven testable ones are quantified individually and jointly, and the five untestable ones are documented as untestable rather than guessed. There is no further sensitivity work that does not require new information.

The one genuinely open successor is a **joint-flip interaction check**, and I recommend the coordinator weigh it as probably not worth a worker: with 8 binary flips there are 256 combinations, all computable locally in seconds, but the leave-one-out deltas above are additive on the underlying value lists by construction, so the only thing a full enumeration adds is the *non-additivity of the order statistics* (a median or quartile can move non-linearly when several flips combine). That is a real but small effect and it is already bracketed by the two envelopes computed here.

The more valuable successor is outside this lane and outside sensitivity analysis entirely: **resolve call 10 (PMID 38111543) and call 6 (PMID 21547635) at source**, since both are untestable only because a numeric value is absent from the abstract, and both would materially widen the census if recovered. Neither has been checked for a PMC deposit — W08d's `convert_article_ids` sweep covered only the 8 unadjudicated records, not the borderline-call PMIDs. That is a small, finite, permitted-route retrieval task (`convert_article_ids` + `get_full_text_article` on two PMIDs, with W10c's identifier guard applied), and it is the only remaining route I can identify that could add real evidence rather than re-weigh existing evidence.
