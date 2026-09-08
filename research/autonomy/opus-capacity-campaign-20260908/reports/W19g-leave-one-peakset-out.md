> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**Worker ID:** W19g · lane 19 refill · OPUS-CAPACITY-CAMPAIGN-20260908. Executes the successor W19f named for itself.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:57:56 UTC 2026` · at end: `Tue Sep  8 03:00:32 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the proxy-plumbing lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` also matched the grep, are verbatim in the tool log, and are elided here for length — they contain nothing model-relevant):

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

**Repository state — HEAD MOVED DURING MY RUN, and I checked what moved.** `git rev-parse HEAD` = `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8` at start, `fc6ed92999c26f52c47668d1c126321a5f51d1b5` at end. `git status --porcelain` was **empty at start and empty at end**. The move was not mine — the coordinator committed four sibling reports. I verified my two inputs are byte-identical across the move:

```
git diff --stat ce743d6…fc6ed92 -- research/modalities/gse243553-eno3-overlap.json \
                                   research/modalities/gse243553-eno3-overlap-supplement.json
```
→ **empty output, exit 0** (no change to either input). The full range diff is `4 files changed, 1104 insertions(+)`, all of them `.../reports/W01f-…`, `W05f-…`, `W07e-…`, `W10f-…`. **My substrate is therefore unaffected by the HEAD move.** Neither HEAD equals the brief's frozen commit `92abbcb…`; I read the live checkout, not the frozen corpus.

Every file I created lives under `/tmp/claude-0/w19g/` (`substrate.py`, `gate.py`, `lopo.py`). **I wrote nothing into `/home/user/Rare-cancers` and performed no git write of any kind.**

**Network.** **Zero network calls.** I did not probe, retry, or seek another host for the GSE243553 genome-wide `MOESM3_ESM.zip`; it stands as a recorded 403 CONNECT policy denial. **I hit no content-policy refusal.**

---

## Question

**Does any single peakset carry W19f's `SAMEFAM-DIFFGENE-DIFF5′` effect of +0.1226?**

It is open because W19f flagged it as its own remaining soft spot: the class's eight pairs are drawn from only six peaksets, with `FUS-FEV` and `TMPRSS2-ERG` each appearing in several of them. Leave-one-*pair*-out (which W19f did compute, +0.1031 to +0.1349) cannot detect a single dominating peakset, because dropping one pair leaves the dominating peakset in three or four others. Leave-one-*peakset*-out can. This is a robustness arm on an existing class, not a new hypothesis.

### Framing correction I am carrying forward, from the scientific owner

W19e fixed the DBD-family rule **after** W19d had already viewed the same within-EWSR1 residuals that motivated it. That makes the W19e/W19f/W19g line a **reproducible EXPLORATORY successor** — a post-hoc observation converted into a rule that is stated in advance *of each subsequent run*, on an independently sourced family table, and honestly reported. It is **not prespecified validation and not held-out validation**; the data are the same 32 peaksets throughout, so nothing here is held out. I flag two wordings in the predecessor record that should be read with this correction:

- W19e's report is filed under the name `W19e-dbd-family-prespecified-test.md` and its §Question asks whether the effect holds *"as a properly prespecified test"*. **The class was pre-declared relative to W19e's own execution, not relative to the data.** The filename and that phrasing overstate it; the finding itself stands, its evidential status does not.
- W19f §Result calls its arm a *"falsification test"* that *"falsifies the 'EWSR1 fusions simply resemble each other' reading"*. The internal logic is sound (the shared-5′ confound really is removed by construction), but it is a falsification **within** the exploratory line, on recycled data — not independent confirmation of W19e.

**Unsourced-claim check.** My dispatch warned against repeating a claim that clinical practice assumes fusion-partner interchangeability. I grepped the reports directory for it and **found no such claim in the W19 chain** — the only "interchangeab" hits are (a) the correct methodological caveat that pair-dependent windows are not interchangeable estimates, and (b) the hypothesis label *"FET 5′ partners are interchangeable"*, which is a candidate reading of the data, not a claim about clinicians. `W20-computational-hypothesis.md:308` asks *"whether EMC's non-EWSR1 variants are one disease"* — an open question, correctly posed as one. **I make no claim about clinical practice, and I found none needing correction.** Had one been present it would have been unsourced.

---

## Prior-work check

```
grep -n -i -E "prespecif|pre-specif|held.out|independent confirm|independent valid|interchange" \
     W19c*.md W19d*.md W19e*.md W19f*.md
grep -rn -i -E "partner.{0,30}interchangeab|interchangeab.{0,30}partner" --include='*.md' --include='*.json' .
grep -n -i -E "clinical practice|clinicians|diagnostic practice|assumes.*partner" W19c*.md W19d*.md W19e*.md W19f*.md
```
Results are quoted in the framing block above. No leave-one-peakset-out analysis exists anywhere in the reports directory; W19f's §Limitations states plainly that *"leave-one-peakset-out was not computed"* and its §Next concrete action specifies exactly this arm, including the n ≥ 4 floor. I am executing that named successor, unchanged.

**Closed items confirmed not replayed** (`CLOSED-WORK.md`, item by item): no clinical, registry, methylation, promoter-transfer, inverse-bound, Hofvander/EGA, Brenca, GSE4303/GSE28866, pazopanib/anthracycline/sunitinib/trabectedin/Wagner/CTARC or SEER material is touched; no cohort is invented; lane 11 source-index work is untouched; the restricted NR4A Perspective review is not recreated under any label. I did not re-run W19e's own `SAMEFAM-DIFFGENE` class, did not introduce a third DBD family, and added no post-hoc split.

---

## Method / inputs

**Inputs — both committed, both read-only, read from the live checkout, verified unchanged across the HEAD move:**

| Input | Path | Field used |
|---|---|---|
| Coordinate prefixes | `research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` |
| Peak counts | `research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory[*].n_intervals` |

Deposit **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`; 128 fusion oncoproteins in one HEK293T background; assembly hg38. **These are the authors' own marker calls — this repository called no peak.**

**Tools:** Python 3.11.15, standard library only (`json`, `itertools`, `math`, `random`, `statistics`). No third-party package, no GPU, no paid API, **$0 spend**.

**Substrate rebuilt independently** in `/tmp/claude-0/w19g/substrate.py` — I re-parsed both JSONs from scratch and imported no object from W19c/W19d/W19e/W19f. 32 real `Supp_Data_1_new/*_markers.bed` prefixes, trailing partial line discarded, `chr1` records only, `W(A,B) = min(last retained chr1 end)`, Jaccard on exact interval identity inside `chr1:0–W`, pair non-degenerate iff both sides hold ≥ 1 interval in the window. Density residual `r = J − mean(J in the pair's |Δlog₁₀ n_intervals| quintile)`, quintiles over the 376 full-panel non-degenerate pairs.

**Class — inherited verbatim, not redefined.** `SAMEFAM-DIFFGENE-DIFF5′`; families sourced only, ETS = {ERG, FLI1, FEV, ETV1, ETV4}, CREB = {ATF1, CREB1}, everything else UNKNOWN and never matching another UNKNOWN. **No third family introduced.**

**LOPO design, fixed in the script docstring before execution.** Dropping peakset `D` removes `D` from the *panel*: every pair containing `D` leaves the universe, the class is rebuilt on the remaining 31 peaksets, and the null is **re-permuted** by shuffling the 31 `(5′,3′)` labels across the 31 remaining peaksets. Density residuals `R` are held at their full-panel values, because a residual is a property of a pair — re-binning per arm would change the substrate rather than the arm. Null: 50,000 draws, seed `20260908`, one-sided high, `p = (1 + #{perm ≥ obs}) / (1 + n_perm)`. **Floor: n < 4 ⇒ descriptive, no p-value.**

**Independence reckonings, both declared in the docstring before execution:**
- **(A) Vertex bound.** The pairs are edges of a graph whose vertices are peaksets; independent observations cannot exceed the number of vertices carrying them.
- **(B) Matching bound.** The largest set of class pairs sharing no peakset is a maximum matching of that graph — the largest strictly independent subsample the class contains. Computed exactly by brute force over all subsets.

---

## Result

### Gate — ARM 1 reproduced digit-for-digit, no discrepancy (PRIMARY)

| Quantity | W19g (this run) | Published ARM 1 | Match |
|---|---|---|---|
| Real BED peaksets | 32 | 32 | ✔ |
| All pairs / non-degenerate | 496 / **376** | 496 / 376 | ✔ |
| Density quintile mean J | 0.0387 / 0.0163 / 0.0126 / 0.0110 / 0.0014 | same | ✔ |
| SHARES-3 n · mean residual · p | 10 · **+0.1513** · 0.00008 | 10 · +0.1513 · 0.00008 | ✔ |
| SHARES-5 n · mean residual · p | 66 · **+0.0094** · 0.09782 | 66 · +0.0094 · 0.09782 | ✔ |
| SHARES-NEITHER n · mean residual | 300 · −0.0071 | 300 · −0.0071 | ✔ |

**No discrepancy on any deterministic quantity.** The two p-values matching exactly reflects the same seed and draw order, not evidence about Monte-Carlo stability.

The full class reproduces as well: **n = 8, mean J 0.1556, mean residual +0.1226, p = 0.00084** (baseline arm, re-permuted with the identical LOPO machinery). All eight member pairs and residuals matched W19f's table exactly.

### 4. Dependence, quantified directly (PRIMARY)

| Peakset | pairs it appears in, of 8 |
|---|---|
| **`TMPRSS2-ERG`** | **5** |
| **`FUS-FEV`** | **4** |
| `EWSR1-ETV1` | 2 |
| `EWSR1-ETV4` | 2 |
| `EWSR1-FLI1` | 2 |
| `EWSR1-FEV` | 1 |

Six distinct peaksets carry eight pairs; the two hubs together touch **all eight**.

| Reckoning (declared in advance) | Value | Row type |
|---|---|---|
| **(A) Vertex bound** — effective independent observations ≤ distinct peaksets | **≤ 6** | PRIMARY |
| **(B) Matching bound** — largest peakset-disjoint subset of class pairs | **2 pairs** | PRIMARY |

The matching bound of 2 is not an artefact of the search — it is **structurally forced**. No two `EWSR1-*` peaksets can pair with each other (they share a 5′ partner, which the class excludes), so the graph is bipartite between the four `EWSR1-*` peaksets and the two non-EWSR1 peaksets, plus the single `FUS-FEV · TMPRSS2-ERG` edge. A matching cannot exceed the size of the smaller side, which is **2**. The exact disjoint subset found is `EWSR1-ETV1 · FUS-FEV` (r = +0.2185) and `EWSR1-ETV4 · TMPRSS2-ERG` (r = +0.0627), mean residual **+0.1406** — n = 2 supports no inference and I draw none.

**So the honest statement is: eight pairs, at most six independent observations by the loosest defensible reckoning, and at most two strictly independent ones.** The p-value of 0.00084 is computed against a null that shuffles labels across the whole panel and so does account for hub structure in expectation, but its three-significant-figure precision far exceeds the precision the evidence carries.

### 2. and 3. The six leave-one-peakset-out arms (PRIMARY)

| Arm — peakset dropped | n | mean J | **mean residual** | null mean ± sd | **p** |
|---|---|---|---|---|---|
| *(baseline, none dropped)* | 8 | 0.1556 | **+0.1226** | −0.0004 ± 0.0206 | 0.00084 |
| drop `EWSR1-FEV` | 7 | 0.1671 | **+0.1349** | −0.0016 ± 0.0210 | 0.00070 |
| drop `EWSR1-ETV4` | 6 | 0.1628 | **+0.1279** | −0.0011 ± 0.0223 | 0.00148 |
| drop `EWSR1-ETV1` | 6 | 0.1466 | **+0.1117** | −0.0021 ± 0.0211 | 0.00250 |
| drop `EWSR1-FLI1` | 6 | 0.1425 | **+0.1113** | −0.0022 ± 0.0209 | 0.00202 |
| **drop `FUS-FEV`** | **4** | 0.0888 | **+0.0613** | −0.0020 ± 0.0257 | **0.04074** |
| **drop `TMPRSS2-ERG`** | **3** | 0.2479 | **+0.2092** | — | **DESCRIPTIVE — n < 4, NO p-VALUE** |

Units: Jaccard dimensionless over the pair-specific `chr1:0–W` window. Uncertainty is the 50,000-draw whole-name permutation distribution over the 31 retained peaksets in each arm and extends no further. One arm hit the n < 4 floor, as W19f predicted; it gets no p-value and none may be quoted for it.

### Answer to the question the arm exists for

**No single peakset carries the whole +0.1226 — but one of them carries about half of it, and that is a real weakening of W19f that I state plainly.**

- **Every one of the six arms keeps a positive mean residual**, ranging +0.0613 to +0.2092, all above the SHARES-NEITHER reference of −0.0071. The effect does not vanish on the removal of any single peakset. That is the sense in which W19f survives.
- **But `FUS-FEV` is a dominant contributor.** Dropping it halves the residual (+0.1226 → **+0.0613**, a 50 % reduction) and moves p from 0.00084 to **0.04074** — roughly a 48-fold increase, from comfortably significant to barely inside a 0.05 threshold at n = 4, the smallest testable arm. **W19f's headline effect size is therefore not robust to the loss of one peakset; its significance is only marginally so.** Anyone quoting +0.1226 should quote +0.0613 alongside it.
- **The `TMPRSS2-ERG` arm points the other way and cannot be tested.** Removing it *raises* the residual to +0.2092 — but n falls to 3, below the floor, so this is **descriptive only**. What it shows is structural, not statistical: the residual is concentrated in the `EWSR1-* × FUS-FEV` pairs, the three highest residuals in the whole class (+0.2586, +0.2185, +0.1505). The five `TMPRSS2-ERG` pairs are the four lowest plus one middling one.
- **The most accurate summary of the class is not "the ETS family clusters" but "four `EWSR1-*` ETS peaksets resemble `FUS-FEV` strongly and `TMPRSS2-ERG` weakly."** Both readings are consistent with a 3′-family effect; the data cannot separate a family effect from a `FUS-FEV`-specific one, because `FUS-FEV` is the only non-EWSR1, non-TMPRSS2 peakset in the class.

**PREDICTION rows: none.** No model output, extrapolation or projection appears in this report. **UNKNOWN rows:** the CREB arm (W19f's one CREB candidate was lost to prefix geometry and remains untested here — I did not revisit it), and anything genome-wide.

---

## Validation evidence

All **RUN**. Nothing here is `PROPOSED (NOT RUN)`.

**RUN — command 1** (start state)
```
date -u; git rev-parse HEAD; git status --porcelain;
env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I';
mkdir -p /tmp/claude-0/w19g
```
→ `Tue Sep  8 02:57:56 UTC 2026`, HEAD `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`, `git status --porcelain` **empty**. **Exit 0.**

**RUN — command 2** (substrate rebuild + ARM 1 gate)
```
cd /tmp/claude-0/w19g && python3 --version && time python3 gate.py; echo "EXIT=$?"
```
Environment: Python 3.11.15, stdlib only. Wall `real 0m8.348s`. **`EXIT=0`.** Verbatim:
```
real BED peaksets: 32
all pairs: 496  non-degenerate: 376
density quintiles: Q1=0.0387(n=75) Q2=0.0163(n=75) Q3=0.0126(n=75) Q4=0.0110(n=75) Q5=0.0014(n=76)
  SHARES-3       n= 10 mean J 0.1715 mean residual +0.1513
  SHARES-5       n= 66 mean J 0.0300 mean residual +0.0094
  SHARES-NEITHER n=300 mean J 0.0077 mean residual -0.0071
GATE SHARES-3  n=10 obs residual +0.1513 p=0.00008
GATE SHARES-5  n=66 obs residual +0.0094 p=0.09782
```

**RUN — command 3** (the LOPO arm; docstring written before execution)
```
cd /tmp/claude-0/w19g && time python3 lopo.py; echo "EXIT=$?"
```
Wall `real 0m41.501s`. **`EXIT=0`.** Verbatim:
```
FULL CLASS n=8  mean J 0.1556  mean residual +0.1226
   EWSR1-ETV1       x FUS-FEV           J=0.2571  r=+0.2185
   EWSR1-ETV1       x TMPRSS2-ERG       J=0.1081  r=+0.0918
   EWSR1-ETV4       x FUS-FEV           J=0.1892  r=+0.1505
   EWSR1-ETV4       x TMPRSS2-ERG       J=0.0789  r=+0.0627
   EWSR1-FEV        x TMPRSS2-ERG       J=0.0750  r=+0.0363
   EWSR1-FLI1       x FUS-FEV           J=0.2973  r=+0.2586
   EWSR1-FLI1       x TMPRSS2-ERG       J=0.0930  r=+0.0544
   FUS-FEV          x TMPRSS2-ERG       J=0.1463  r=+0.1077

DEPENDENCE CENSUS: 6 distinct peaksets carry 8 pairs
   TMPRSS2-ERG      appears in 5 of the 8 pairs
   FUS-FEV          appears in 4 of the 8 pairs
   EWSR1-ETV1       appears in 2 of the 8 pairs
   EWSR1-ETV4       appears in 2 of the 8 pairs
   EWSR1-FLI1       appears in 2 of the 8 pairs
   EWSR1-FEV        appears in 1 of the 8 pairs
RECKONING A (vertex bound): effective independent observations <= 6
RECKONING B (maximum matching): largest peakset-disjoint subset = 2 pairs
     disjoint member: EWSR1-ETV1       x FUS-FEV           r=+0.2185
     disjoint member: EWSR1-ETV4       x TMPRSS2-ERG       r=+0.0627
     mean residual of that disjoint subset: +0.1406

=== BASELINE (nothing dropped), re-permuted with identical machinery ===
  ARM drop None             n=8  mean J 0.1556  mean residual +0.1226  null -0.0004+-0.0206  p=0.00084

=== LEAVE-ONE-PEAKSET-OUT: six arms ===
  ARM drop EWSR1-ETV1       n=6  mean J 0.1466  mean residual +0.1117  null -0.0021+-0.0211  p=0.00250
  ARM drop EWSR1-ETV4       n=6  mean J 0.1628  mean residual +0.1279  null -0.0011+-0.0223  p=0.00148
  ARM drop EWSR1-FEV        n=7  mean J 0.1671  mean residual +0.1349  null -0.0016+-0.0210  p=0.00070
  ARM drop EWSR1-FLI1       n=6  mean J 0.1425  mean residual +0.1113  null -0.0022+-0.0209  p=0.00202
  ARM drop FUS-FEV          n=4  mean J 0.0888  mean residual +0.0613  null -0.0020+-0.0257  p=0.04074
  ARM drop TMPRSS2-ERG      n=3  mean J 0.2479  mean residual +0.2092   *** n<4: DESCRIPTIVE ONLY, NO p-VALUE ***
```

**RUN — command 4** (end state)
```
date -u && git rev-parse HEAD && echo "STATUS:[$(git status --porcelain)]" && ls -1 /tmp/claude-0/w19g/
```
→ `Tue Sep  8 03:00:32 UTC 2026`; HEAD **`fc6ed92999c26f52c47668d1c126321a5f51d1b5`**; `STATUS:[]` (**empty**); three `.py` files, all under `/tmp/claude-0/w19g/`. **Exit 0. No repository file created, modified or deleted.**

**RUN — command 5** (HEAD-move impact check)
```
git diff --stat ce743d6…fc6ed92 -- research/modalities/gse243553-eno3-overlap.json \
                                   research/modalities/gse243553-eno3-overlap-supplement.json
```
→ **empty**, `INPUTS_DIFF_EXIT=0`. Range diff is 4 sibling report files, `1104 insertions(+)`, no input touched.

### Code (returned inline, not written into the tree)

`substrate.py` is byte-equivalent in behaviour to W19f's, re-typed rather than imported, with one added assertion (`assert set(nint)==set(names)`); it is reproduced in W19f's report and I do not duplicate it here. The new file is `/tmp/claude-0/w19g/lopo.py`:

```python
"""
W19g - LEAVE-ONE-PEAKSET-OUT robustness arm on W19f's class.

CLASS (unchanged, inherited verbatim from W19f/W19e, NOT redefined here):
  SAMEFAM-DIFFGENE-DIFF5' = same sourced 3' DBD family AND different 3' gene
                            AND different 5' partner.
  Families sourced only: ETS = {ERG, FLI1, FEV, ETV1, ETV4}; CREB = {ATF1, CREB1}.
  Every other 3' partner is UNKNOWN and NEVER matches another UNKNOWN.
  NO THIRD FAMILY IS INTRODUCED. NO NEW SPLIT IS TESTED.

ARMS: six, dropping in turn each peakset that appears in the n=8 class.
  Dropping peakset D means: D is removed from the PANEL entirely (all pairs
  containing D leave the universe), the class is rebuilt on the remaining 31
  peaksets, and the null is RE-PERMUTED by shuffling the 31 (5',3') labels
  across the 31 remaining peaksets. Density residuals R are held at the values
  computed once on the full 376-pair panel (a residual is a property of a pair;
  re-binning per arm would change the substrate, not the arm).

NULL: 50,000 draws, seed 20260908, one-sided high,
      p = (1 + #{perm >= obs}) / (1 + n_perm).
FLOOR (NOT NEGOTIABLE): an arm with n < 4 is DESCRIPTIVE and gets NO p-value.

INDEPENDENCE RECKONINGS, DECLARED BEFORE EXECUTION (both reported):
 (A) VERTEX BOUND. The 8 pairs are edges of a graph whose vertices are peaksets.
     The number of independent observations cannot exceed the number of vertices
     that carry them. Effective n <= (number of distinct peaksets in the class).
 (B) MATCHING BOUND. The largest set of class pairs that share NO peakset with
     each other is a maximum matching of that graph. That is the largest strictly
     independent subsample the class contains. Computed exactly by brute force.
Both are reported as bounds on independence, not as corrected p-values.
"""
exec(open('/tmp/claude-0/w19g/substrate.py').read())
import statistics, random, itertools

FAM={"FLI1":"ETS","ERG":"ETS","FEV":"ETS","ETV1":"ETS","ETV4":"ETS",
     "ATF1":"CREB","CREB1":"CREB"}
def fam(g): return FAM.get(g)

def in_class(a,b,Gmap):
    a5,a3=Gmap[a]; b5,b3=Gmap[b]
    fa,fb=fam(a3),fam(b3)
    if fa is None or fb is None: return False
    if fa!=fb: return False
    if a3==b3: return False
    if a5==b5: return False
    return True

full=[p for p in good if in_class(p[0],p[1],G)]

# ---- dependence census -------------------------------------------------
deg={}
for a,b in full:
    deg[a]=deg.get(a,0)+1; deg[b]=deg.get(b,0)+1
verts=sorted(deg)
print("RECKONING A (vertex bound): effective independent observations <= %d"%len(verts))
best=[]
for k in range(len(full),0,-1):                 # exact maximum matching
    found=None
    for combo in itertools.combinations(full,k):
        used=set(); ok=True
        for a,b in combo:
            if a in used or b in used: ok=False; break
            used.add(a); used.add(b)
        if ok: found=combo; break
    if found: best=found; break
print("RECKONING B (maximum matching): largest peakset-disjoint subset = %d pairs"%len(best))

# ---- LOPO arms ---------------------------------------------------------
def arm(drop,nperm=50000,seed=20260908):
    keep=[n for n in names if n!=drop] if drop else list(names)
    kset=set(keep)
    uni=[p for p in good if p[0] in kset and p[1] in kset]
    members=[p for p in uni if in_class(p[0],p[1],G)]
    n=len(members)
    if n==0:
        print("  ARM drop %-16s n=0  (no members) DESCRIPTIVE"%drop); return
    obs=statistics.mean([R[p] for p in members]); mj=statistics.mean([J[p] for p in members])
    if n<4:
        print("  ARM drop %-16s n=%d  mean J %.4f  mean residual %+.4f   "
              "*** n<4: DESCRIPTIVE ONLY, NO p-VALUE ***"%(drop,n,mj,obs)); return
    idx={nm:i for i,nm in enumerate(keep)}
    gi=[(idx[a],idx[b],R[(a,b)]) for a,b in uni]
    rng=random.Random(seed); labels=list(keep); ge=0; nulls=[]
    for _ in range(nperm):
        rng.shuffle(labels); s=0.0;c=0
        for i,j,r in gi:
            if in_class(labels[i],labels[j],G): s+=r;c+=1
        v=s/c if c else 0.0
        nulls.append(v)
        if v>=obs: ge+=1
    p=(1+ge)/(1+nperm)
    ps="< 2.1e-5 (MC floor)" if ge==0 else "%.5f"%p
    print("  ARM drop %-16s n=%d  mean J %.4f  mean residual %+.4f  null %+.4f+-%.4f  p=%s"
          %(drop,n,mj,obs,statistics.mean(nulls),statistics.pstdev(nulls),ps))

arm(None)
for v in verts: arm(v)
```
(Census-printing lines elided from the excerpt for length; they are verbatim in the tool log and their output is quoted above in full.)

---

## Limitations

**Carried forward without softening from W19c / W19d / W19e / W19f:**

- **The window is a sliver of one chromosome.** Every comparison happens inside `chr1:0` to a pair-specific ceiling; effective comparison depth is 24–28 intervals per side. The retained data is a **byte-truncated prefix**, so the tested region is the proximal end of chr1 selected by nothing but sort order. Whether any of this holds genome-wide is **UNKNOWN**.
- **Windows are pair-dependent**, so the Jaccards are not interchangeable estimates of one quantity. The null was computed the same way, which keeps the comparison fair without making the windows comparable.
- **HEK293T is not EMC.** All fusions were expressed in one embryonic-kidney background. **Nothing here transfers to any tumour or any patient**, to chondroid tissue, or to disease behaviour.
- **These are the authors' marker calls** at a threshold this repository did not set and cannot re-tune.
- **The genome-wide interval sets remain unrecovered** behind a 403 CONNECT policy denial I did not test or route around.
- The class is **ETS-only in practice**; the single CREB candidate was lost to prefix geometry. **No statement about CREB or any non-ETS family is supported** — that arm is UNKNOWN, not null.

**New to this arm, and these are the ones that matter:**

- **This whole line is a reproducible EXPLORATORY successor, not validation.** The DBD-family rule was fixed after the same residuals had been viewed, and every arm since has re-used the same 32 peaksets. There is no held-out data anywhere in W19d→W19e→W19f→W19g. The rule being written down before each run makes the line *reproducible and honest*; it does not make it *confirmatory*. Predecessor wording that reads as prespecified or as independent confirmation is corrected in §Question above.
- **Eight pairs, ≤ 6 independent observations, and only 2 strictly independent ones.** The matching bound of 2 is structurally forced by the class definition itself, not by sampling luck. Any p-value quoted from this class should be read against that.
- **The effect is not robust in magnitude to the loss of `FUS-FEV`** (+0.1226 → +0.0613, p 0.00084 → 0.04074). It survives in *sign* under every single-peakset deletion, which is the weaker of the two claims one might have hoped for.
- **The `TMPRSS2-ERG` arm is uninterpretable statistically** (n = 3, below the floor). Its high descriptive residual is reported and must not be quoted as evidence for the class; it is equally consistent with the class being driven by `FUS-FEV`'s resemblance to the EWSR1 peaksets.
- **LOPO does not repair the dependence, it measures it.** Six arms drawn from the same eight pairs are themselves highly correlated; they are not six independent replications and no multiplicity correction across them would be meaningful.
- **Residuals were held fixed across arms** rather than re-binned. That is a deliberate, stated choice; a re-binned variant was not run and its result is **UNKNOWN**.
- **This is an ASSOCIATION in a heterologous cell line.** Nothing here bears on efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness of any agent, target or gene; no such quantity was computed. No reagent was designed. There is no wet lab. **No clinical claim.**

---

## Stop condition

**Set in advance:** reproduce the ARM 1 gate figures exactly (or report the discrepancy loudly), then run all six leave-one-peakset-out arms with re-permutation, apply the n ≥ 4 floor without exception, answer whether a single peakset carries the effect, and quantify the dependence under reckonings declared before execution — **reporting a weakening of W19f with the same willingness as a confirmation.**

**MET.** The gate reproduced digit-for-digit with **no discrepancy**. All six arms ran; one hit the n < 4 floor and was declared descriptive with no p-value. The question is answered: no single peakset carries the whole effect, but `FUS-FEV` carries about half of it, and I have said plainly that this weakens W19f's effect-size claim. Dependence is quantified two ways, both declared in the script docstring before execution. The predecessor framing error was corrected. I stopped on meeting the condition and added no work.

---

## Tool-call and wall-clock count actually used

**8 tool calls. Wall clock 02:57:56Z → 03:00:32Z ≈ 2.6 minutes** — well inside the ~40 call / ~40 min target. Three scripts written and run under `/tmp/claude-0/w19g/`; **zero repository writes; zero git writes; zero network calls; no denied route probed; $0 spend.**

---

## Next concrete action

**One successor, runnable on retained data with no new access — and it is a scoping arm, not another significance test.** The three highest residuals in the class are all `EWSR1-* × FUS-FEV`, and `FUS-FEV` is the only peakset whose removal halves the effect. Ask whether that is *family* signal or *`FUS-FEV`* signal by measuring `FUS-FEV`'s residual against **every** peakset in the panel, not just its ETS partners: compute the 31 `FUS-FEV × *` residuals, rank them, and report where the four in-class pairs fall in that ranking, alongside the same ranking for `TMPRSS2-ERG`. If `FUS-FEV` is simply a globally high-similarity peakset — an artefact of its prefix geometry or interval density — its in-class pairs will not stand out in its own ranking, and the class effect is partly a property of one peakset rather than of the ETS family. That is a descriptive, distribution-free scoping arm on the existing substrate; it needs no new family assignment, no new class, and no p-value.

**Not a successor, explicitly:** sourcing a third DBD family to enlarge the class (post-hoc redefinition after seeing these results); any leave-*two*-peaksets-out arm (every such arm falls below the n ≥ 4 floor by construction, given six peaksets and two hubs); and anything needing the genome-wide BEDs — that is one recorded 403 away and must not be re-probed. **The honest ceiling of this line is that no amount of re-analysis of 32 truncated chr1 prefixes in HEK293T can raise it above an exploratory association, and the next real advance requires the genome-wide data or a different substrate.**
