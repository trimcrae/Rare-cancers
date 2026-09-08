> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**Worker ID:** W19e · **lane 19, slot refill** · campaign OPUS-CAPACITY-CAMPAIGN-20260908. Executes the successor W19d named for itself.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. This is a self-report from my own system context, **not an observed fact**; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:35:36 UTC 2026` · `date -u` at end: `Tue Sep  8 02:42:19 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the proxy-plumbing lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` also match the grep and are verbatim in the tool log; elided here for length, they contain nothing model-relevant):

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

**HEAD actually read — and it moved under me, which I record rather than paper over.** At start `git rev-parse HEAD` = `7d081218f107363573573e6d102e4334567adf77`; at end = `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4` (the coordinator committed during my run; working tree clean, `git status --porcelain` = 0 lines at both ends). Neither is the `92abbcb9…` named in `COMMON-BRIEF.md` §1 — that string is stale relative to this live checkout. I verified my four input files are byte-identical across the two HEADs, so the HEAD move does not affect any number below:

```
$ git diff --stat 7d08121 d3e9c4d -- research/modalities/gse243553-eno3-overlap.json \
    research/modalities/gse243553-eno3-overlap-supplement.json \
    research/manuscripts/program/emc-post-degrader-options.md \
    research/modalities/emc_fet_construct_designs.py
EXIT=0   (empty diff = inputs identical across both HEADs)
```

I made **no** write to the Git working tree and **no** git write operation of any kind. All execution was under `/tmp/claude-0/w19e/`.

---

## Question

**Does sharing a 3′ DNA-binding-domain (DBD) family predict peak location, as a properly prespecified test over the full 376-pair non-degenerate panel?**

It is open because W19d's DBD-family observation was explicitly **post-hoc**: W19d noticed after inspecting the within-EWSR1 top-J list that 7 pairs whose 3′ partners are family-related carry the block's entire positive residual (+0.2043 vs −0.0141 for the other 56), computed no p-value — correctly — and named exactly this successor. Two things had to change before it could become a result: the family assignment had to come from a **retrievable, citable source** rather than W19d's own symbol-reading, and the class had to be **declared before any Jaccard was inspected** and tested over the whole panel rather than inside one 5′ block.

---

## Prior-work check

Commands run and what they showed:

- `rg -n -i -l "DNA-binding domain|DNA binding domain|bZIP|ETS family|homeodomain" --glob '!.git'` → 40+ hits, but **no per-gene DBD-family table anywhere in the tracked tree**. The hits are prose (`STRATEGY.md`, `emc-post-degrader-options.md`, `emc-atri-prereg.md`), conda lockfiles matching on the substring `bzip2`, and generated views.
- `git ls-files | rg -i "domain|dbd|tf|annot"` → no annotation table; matches are workflow/test/figure paths.
- `rg -n -i -l "bZIP|ETS family|forkhead|homeodomain|nuclear receptor family" corpus/` inside the **frozen corpus** at `/tmp/claude-0/frozen-corpus/extracted/` → 20 files, all prose. Targeted read of `corpus/research/modalities/emc_fet_construct_designs.py` and `corpus/research/modalities/emc-atri-prereg.md` gave family statements for **three** genes only (see S3 below), not a table.
- Structural check of both input JSONs (`gse243553-eno3-overlap.json`, `…-supplement.json`): **no family or partner-class field exists** in the deposit-derived data.

**Conclusion of the prior-work check, stated as a finding:** no DBD-family assignment for this panel exists in the tracked corpus or the frozen corpus. That is why step 1 had to be done from external citable sources, and it is why W19d's annotation could not simply be looked up and confirmed. Per `CORPUS-CONTEXT.md`, local absence is **UNKNOWN**, not proof of repository-wide absence.

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`): lane 19's closed Q-NR4A2-COVERAGE (untouched); PUB-EMC-CLASSIFICATION and every Brenca route (untouched — no case-identity work here); the restricted NR4A Perspective review (not recreated under any label); `GSE4303`/`GSE28866` (not re-read — this is GSE243553); the registry ICD-O paper (rejected, untouched). **I did not probe, retry, or seek another host for the GSE243553 genome-wide `MOESM3_ESM.zip`** — it stands as a recorded 403 CONNECT policy denial. My only network use was PubMed MCP metadata, which is the one permitted route.

---

## Method / inputs

### Order of operations — this is the point of the task, so it is stated explicitly and is asserted in the script itself

1. **First**, I fixed the DBD-family assignment for all 32 peaksets (25 distinct 3′ genes) from citable sources and **wrote the table into the script**, together with its per-gene source. At that moment I had computed **no Jaccard of any kind** — the only quantities I had touched were file names, `n_intervals`, and one 400-character BED prefix inspected to confirm the field format.
2. **Then** I wrote the null, the decision rule and the minimum-class-size floor into the script docstring.
3. **Only then** was the script run for the first time (it failed on an `IndentationError` on the very first invocation, exit 1, before executing a single line of analysis — that is in the evidence below; the fix touched a print-formatting ternary and nothing else).

The file is timestamped `2026-09-08 02:40:16 UTC`; the first successful analysis run began `02:40:30 UTC`. The script carries `ORDER_OF_OPERATIONS = "family table sourced and written -> docstring prereg written -> first run"`.

### STEP 1 — the sourced 32-peakset 3′ DBD-family table, written before any Jaccard

Assignment is taken **only** from a retrievable citable statement. **W19d's annotation is not inherited as fact.** A partner with no sourced statement is **UNKNOWN**, never a guess, and an UNKNOWN never matches another UNKNOWN.

According to PubMed, the two external sources are:

- **S1** — PMID `30257034`, Renzi et al., *J Cell Physiol* 2018, [DOI](https://doi.org/10.1002/jcp.27558). Abstract, verbatim: *"a gene of the ETS-transcription family ( FLI1, ERG, ETV1, ETV4, or FEV)"*.
- **S2** — PMID `38460673`, Zhao et al., *Mod Pathol* 2024, [DOI](https://doi.org/10.1016/j.modpat.2024.100468). Abstract, verbatim: *"genes encoding CREB transcription factors family (ATF1, CREB1, and CREM)"*. Corroborated by PMID `28009602`, Kao et al., *Am J Surg Pathol* 2017, [DOI](https://doi.org/10.1097/PAS.0000000000000788): *"members of the cAMP response element binding protein (CREB) family (ATF1 and CREB1)"*.
- **S4 (a sourced NEGATIVE only)** — PMID `29480450`, Specht & Hartmann, *Pathologe* 2018, [DOI](https://doi.org/10.1007/s00292-018-0421-2). Abstract, verbatim: *"rearrangements between EWSR1 and non-ETS genes (NFATC2, POU5F1, SMARCA5, PATZ, ZSG, SP3)"*. This **excludes** NFATC2, POU5F1 and SP3 from ETS but names no family for them, so all three stay UNKNOWN.

And one in-repository source:

- **S3** — tracked corpus at the HEADs above: `research/manuscripts/program/emc-post-degrader-options.md` L108–109 (*"EMC's NR4A3 is a nuclear receptor"*) and `research/modalities/emc_fet_construct_designs.py` L13 (*"the first zinc finger of its C4 DBD"*).

| # | Peakset (fusion) | 3′ partner | **Sourced DBD family** | Source | Row type |
|---|---|---|---|---|---|
| 1 | EWSR1-ETV1 | ETV1 | ETS | S1 | PRIMARY |
| 2 | EWSR1-ETV4 | ETV4 | ETS | S1 | PRIMARY |
| 3 | EWSR1-FEV | FEV | ETS | S1 | PRIMARY |
| 4 | EWSR1-FLI1 | FLI1 | ETS | S1 | PRIMARY |
| 5 | FUS-FEV | FEV | ETS | S1 | PRIMARY |
| 6 | TMPRSS2-ERG | ERG | ETS | S1 | PRIMARY |
| 7 | EWSR1-ATF1 | ATF1 | CREB | S2 | PRIMARY |
| 8 | EWSR1-CREB1 | CREB1 | CREB | S2 | PRIMARY |
| 9 | FUS-ATF1 | ATF1 | CREB | S2 | PRIMARY |
| 10 | EWSR1-NR4A3 | NR4A3 | NUCLEAR_RECEPTOR_C4 | S3 | PRIMARY |
| 11 | TAF15-NR4A3 | NR4A3 | NUCLEAR_RECEPTOR_C4 | S3 | PRIMARY |
| 12 | TCF12-NR4A3 | NR4A3 | NUCLEAR_RECEPTOR_C4 | S3 | PRIMARY |
| 13 | TFG-NR4A3 | NR4A3 | NUCLEAR_RECEPTOR_C4 | S3 | PRIMARY |
| 14 | ACTB-GLI1 | GLI1 | **UNKNOWN** | — | UNKNOWN |
| 15 | ARFGEF2-HNF4A | HNF4A | **UNKNOWN** | — | UNKNOWN |
| 16 | CCDC6-RET | RET | **UNKNOWN** | — | UNKNOWN |
| 17 | EPC1-PHF1 | PHF1 | **UNKNOWN** | — | UNKNOWN |
| 18 | MEAF6-PHF1 | PHF1 | **UNKNOWN** | — | UNKNOWN |
| 19 | ETV6-NTRK3 | NTRK3 | **UNKNOWN** | — | UNKNOWN |
| 20 | TPR-NTRK1 | NTRK1 | **UNKNOWN** | — | UNKNOWN |
| 21 | EWSR1-DDIT3 | DDIT3 | **UNKNOWN** | — | UNKNOWN |
| 22 | FUS-DDIT3 | DDIT3 | **UNKNOWN** | — | UNKNOWN |
| 23 | EWSR1-NFATC2 | NFATC2 | **UNKNOWN** (sourced non-ETS, S4) | S4 (negative only) | UNKNOWN |
| 24 | EWSR1-POU5F1 | POU5F1 | **UNKNOWN** (sourced non-ETS, S4) | S4 (negative only) | UNKNOWN |
| 25 | EWSR1-SP3 | SP3 | **UNKNOWN** (sourced non-ETS, S4) | S4 (negative only) | UNKNOWN |
| 26 | EWSR1-PBX1 | PBX1 | **UNKNOWN** | — | UNKNOWN |
| 27 | EWSR1-YY1 | YY1 | **UNKNOWN** | — | UNKNOWN |
| 28 | FGFR3-TACC3 | TACC3 | **UNKNOWN** | — | UNKNOWN |
| 29 | HEY1-NCOA2 | NCOA2 | **UNKNOWN** | — | UNKNOWN |
| 30 | IRF2BP2-CDX1 | CDX1 | **UNKNOWN** | — | UNKNOWN |
| 31 | PAX7-FOXO1 | FOXO1 | **UNKNOWN** | — | UNKNOWN |
| 32 | SS18L1-SSX1 | SSX1 | **UNKNOWN** | — | UNKNOWN |

**8 of 25 distinct 3′ genes are sourced; 17 are UNKNOWN.** Two departures from W19d's symbol-reading are deliberate and material:

- **DDIT3 is UNKNOWN, not bZIP.** W19d's post-hoc group was *"CREB-bZIP: ATF1/CREB1"*. The sourced statement S2 defines the **CREB family** as ATF1/CREB1/CREM and does not include DDIT3; I retrieved no source placing DDIT3 in it, and I did not guess one. This is exactly the substitution the dispatch forbade.
- **"Has no DBD" is not a family.** RET, NTRK1, NTRK3, TACC3, PHF1, NCOA2 and SSX1 are not lumped into a shared class. Doing so would have manufactured pairs (e.g. `ETV6-NTRK3 · TPR-NTRK1`) out of an absence.
- One search that returned zero results (`NR4A3 NOR-1 HNF4A members of the nuclear receptor superfamily`, `total_count: 0`) left **HNF4A UNKNOWN**. It would otherwise have joined NR4A3. This costs the test nothing, because all four NR4A3 fusions share the same 3′ gene and so contribute **zero** different-gene pairs regardless.

### STEP 2 — preregistration, written into the docstring before the first run

- **Substrate, pair statistic and density residualisation are W19c/W19d's, unchanged.** 32 real `Supp_Data_1_new/*_markers.bed` prefixes from the committed supplement JSON; trailing partial line discarded; `chr1` records only. `W(A,B) = min(last retained chr1 end of A, of B)`; restrict both to `chr1:0–W`; Jaccard over exact interval identity; non-degenerate iff both sides hold ≥1 interval in the window. `d(A,B) = |Δlog₁₀ n_intervals|`; quintile-bin the non-degenerate pairs; `r = J − mean(J in that quintile)`. Binning uses interval counts only, never gene labels, so residuals are invariant under every label permutation.
- **GATE 0** — reproduce W19c/W19d ARM 1 before extending, against their published targets. Verbatim from the docstring: *"A DISCREPANCY IS THE MOST IMPORTANT FINDING AND IS REPORTED AS SUCH; the run does not stop, it reports both numbers side by side."*
- **Pre-declared classes over the full 376-pair non-degenerate panel:**
  - **SAMEFAM-DIFFGENE (PRIMARY)** — both 3′ partners have a **sourced** family, families equal, **and the two 3′ genes differ**. Verbatim rationale from the docstring: *"a same-gene pair is already SHARES-3, so including it would merely re-detect the known 3′ effect instead of testing family."*
  - **SAMEFAM-ANY (SECONDARY)** — families equal, identical 3′ genes allowed.
- **Nulls, both of W19d's.** **NULL A** = whole-name shuffle of the 32 fusion names across peaksets (W19c's null). W19d's other null, the 5′-fixed 3′-only shuffle, was declared in advance to be run in its form that **has power for a 3′-defined class** — **NULL B′**, permuting the 32 three-prime labels while each peakset keeps its 5′ label (W19d's TEST 2b null). 50,000 draws, seed 20260908, one-sided high, `p = (1 + #{perm ≥ obs}) / (1 + n_perm)`; MC resolution 1/50001 = 2.0e-5.
- **DECISION RULE, verbatim:** *"SHARING A 3′ DBD FAMILY PREDICTS PEAK LOCATION iff the SAMEFAM-DIFFGENE mean residual is significant at one-sided p ≤ 0.05 under BOTH NULL A and NULL B′. If it clears one null but not the other, that is reported as EQUIVOCAL, not as a positive. If it clears neither, the result is a NULL and is reported as a null with the same willingness as a positive."*
- **MINIMUM-CLASS-SIZE FLOOR, verbatim:** *"any class with fewer than 4 non-degenerate pairs is TOO SMALL TO TEST, is reported descriptively only, and NO p-value is computed for it and none may be quoted."*

**Inputs and tools.** `research/modalities/gse243553-eno3-overlap-supplement.json` (field `contents['SPRINGER::3::zip']['first_bytes']`, ≤600-byte verbatim BED prefix per peakset) and `research/modalities/gse243553-eno3-overlap.json` (field `peakset_inventory[*].n_intervals`), both committed and read-only. Deposit **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`, assembly **hg38** per the deposit's own `!Sample_data_processing`. Python 3.11.15, standard library only (`json`, `itertools`, `math`, `random`, `statistics`). No third-party package, no GPU, no network beyond the five PubMed MCP metadata calls listed above.

---

## Result

### 0. Substrate — every deterministic W19c/W19d quantity reproduced exactly

| Quantity | W19e (this run) | W19c / W19d | Row type |
|---|---|---|---|
| `peakset_inventory` entries | 128 | 128 | PRIMARY |
| Real `Supp_Data_1_new/*.bed` peaksets | 32 | 32 | PRIMARY |
| Prefixes ascending-sorted | `True` | True | PRIMARY |
| Distinct interval widths | `[500]` | [500] | PRIMARY |
| Retained chr1 intervals / peakset | min 4, median 26, max 28 | 4 / 26 / 28 | PRIMARY |
| All pairs / non-degenerate | 496 / **376** | 496 / 376 | PRIMARY |
| Density quintile mean J | 0.0387 / 0.0163 / 0.0126 / 0.0110 / 0.0014 | identical | PRIMARY |
| Class counts (non-deg) | SHARES-3 10, SHARES-5 66, NEITHER 300 | identical | PRIMARY |
| **SHARES-5 mean residual** | **+0.0094** | +0.0094 | PRIMARY |
| **SHARES-3 mean residual · p** | **+0.1513 · 0.00008** | +0.1513 · 0.00008 | PRIMARY |
| **SHARES-5 permutation p** | **0.09200** | **0.09782** | **DISCREPANCY** |

### 1. GATE 0 — the one discrepancy, and its diagnosis

The script emitted `GATE 0: DISCREPANCY -- THIS IS THE MOST IMPORTANT FINDING, REPORT BOTH NUMBERS`, on a ±5e-5 tolerance. **Every deterministic quantity matched, including both point estimates to four decimals and the SHARES-3 p exactly. The single mismatch is the SHARES-5 permutation p: 0.09200 (mine) vs 0.09782 (W19c, reproduced by W19d).**

I diagnosed it rather than waving it away. If the difference were method, it would persist across seeds; if it is Monte-Carlo permutation-stream noise, 0.09782 will sit inside the seed-to-seed spread. Re-running the identical SHARES-5 statistic under 8 independent seeds:

| Seed | SHARES-5 p | Row type |
|---|---|---|
| 20260908 | 0.09200 | PRIMARY |
| 1 | 0.09440 | PRIMARY |
| 2 | 0.09376 | PRIMARY |
| 3 | 0.09760 | PRIMARY |
| 4 | 0.09778 | PRIMARY |
| 5 | 0.09554 | PRIMARY |
| 6 | 0.09804 | PRIMARY |
| 7 | 0.09418 | PRIMARY |
| **spread** | min 0.09200, max 0.09804, mean 0.09541, sd 0.00221 | PRIMARY |

`W19c/W19d target 0.09782 inside [min,max]: True`.

**Diagnosis.** The discrepancy is **Monte-Carlo permutation-stream noise, not a substrate or method difference**. The observed statistic is identical (+0.0094); only the order in which the RNG is consumed differs between my implementation and theirs. Both estimates land in the same place scientifically — SHARES-5 does not clear 0.05 either way. **A secondary, honest correction to W19d follows from this:** W19d reported W19c's ARM 1 as reproducing *"digit-for-digit"* including `p = 0.09782`. That agreement reflects an **identical RNG consumption order inherited from the same implementation lineage**, not an independent re-estimate of the p-value. An independent rebuild — mine — recovers every deterministic quantity exactly but lands at 0.09200. The correct statement of that figure is **p ≈ 0.095 ± 0.002 (MC)**, and quoting five significant digits for it overstates its precision. The GATE 0 reproduction is therefore **passed on all deterministic quantities, with a diagnosed and benign Monte-Carlo difference on the one stochastic one.**

### 2. The pre-declared test — same 3′ DBD family over the full 376-pair panel

| Class | n (non-deg) | mean J | **mean residual** | Row type |
|---|---|---|---|---|
| SHARES-3 | 10 | 0.1715 | +0.1513 | PRIMARY |
| SHARES-5 | 66 | 0.0300 | +0.0094 | PRIMARY |
| NEITHER | 300 | 0.0077 | −0.0071 | PRIMARY |
| **SAMEFAM-DIFFGENE (PRIMARY class)** | **15** | **0.1887** | **+0.1607** | PRIMARY |
| SAMEFAM-ANY (secondary) | 23 | 0.1904 | +0.1644 | PRIMARY |

Both classes clear the n ≥ 4 floor. Permutation results, 50,000 draws, seed 20260908, one-sided high:

| Class | n | observed | Null | null mean | null sd | **p** | Row type |
|---|---|---|---|---|---|---|---|
| **SAMEFAM-DIFFGENE** | 15 | **+0.1607** | NULL A whole-name shuffle | −0.0003 | 0.0154 | **0.00002** | PRIMARY |
| **SAMEFAM-DIFFGENE** | 15 | **+0.1607** | NULL B′ 3′-only shuffle, 5′ fixed | −0.0003 | 0.0154 | **0.00002** | PRIMARY |
| SAMEFAM-ANY | 23 | +0.1644 | NULL A | −0.0002 | 0.0123 | 0.00002 | PRIMARY |
| SAMEFAM-ANY | 23 | +0.1644 | NULL B′ | −0.0002 | 0.0123 | 0.00002 | PRIMARY |

**Script-emitted decision, under the rule fixed before running:** `SAME 3' DBD FAMILY PREDICTS PEAK LOCATION (clears BOTH nulls)`. Both p-values are **at the Monte-Carlo floor** (1/50001 = 0.00002); the correct reading is `p < 2.1e-5`, not a precise value. The observed +0.1607 sits ~10.4 null sd above a null centred on zero.

The 15 member pairs of the primary class, listed from the run (units: J is dimensionless; residual is J minus its density-quintile mean; W in bp on chr1):

| Pair | family | J | residual | Window W | \|A\| | \|B\| | shared |
|---|---|---|---|---|---|---|---|
| EWSR1-FEV · EWSR1-FLI1 | ETS | 0.4118 | +0.3731 | 30,259,296 | 21 | 27 | 14 |
| EWSR1-ETV1 · EWSR1-ETV4 | ETS | 0.3590 | +0.3203 | 15,761,103 | 26 | 27 | 14 |
| EWSR1-FLI1 · FUS-FEV | ETS | 0.2973 | +0.2586 | 24,295,259 | 21 | 27 | 11 |
| EWSR1-ATF1 · EWSR1-CREB1 | CREB | 0.2857 | +0.2731 | 14,540,695 | 9 | 27 | 8 |
| EWSR1-ETV1 · FUS-FEV | ETS | 0.2571 | +0.2185 | 15,833,768 | 27 | 17 | 9 |
| EWSR1-ETV1 · EWSR1-FLI1 | ETS | 0.2424 | +0.2261 | 15,833,768 | 27 | 14 | 8 |
| EWSR1-ETV4 · FUS-FEV | ETS | 0.1892 | +0.1505 | 15,761,103 | 27 | 17 | 7 |
| FUS-FEV · TMPRSS2-ERG | ETS | 0.1463 | +0.1077 | 24,295,259 | 27 | 20 | 6 |
| EWSR1-ETV1 · EWSR1-FEV | ETS | 0.1212 | +0.1049 | 15,833,768 | 27 | 10 | 4 |
| EWSR1-ETV1 · TMPRSS2-ERG | ETS | 0.1081 | +0.0918 | 15,833,768 | 27 | 14 | 4 |
| EWSR1-ETV4 · EWSR1-FLI1 | ETS | 0.1081 | +0.0918 | 15,761,103 | 27 | 14 | 4 |
| EWSR1-FLI1 · TMPRSS2-ERG | ETS | 0.0930 | +0.0544 | 26,744,528 | 21 | 26 | 4 |
| EWSR1-ETV4 · TMPRSS2-ERG | ETS | 0.0789 | +0.0627 | 15,761,103 | 27 | 14 | 3 |
| EWSR1-FEV · TMPRSS2-ERG | ETS | 0.0750 | +0.0363 | 26,744,528 | 17 | 26 | 3 |
| EWSR1-ETV4 · EWSR1-FEV | ETS | 0.0571 | +0.0409 | 15,761,103 | 27 | 10 | 2 |

**All 15 residuals are positive.** Every pair shares at least 2 intervals; the class does not rest on one lucky overlap.

Per-family descriptive split (declared in advance as descriptive, not as the primary decision):

| Family split | n | mean residual | Row type |
|---|---|---|---|
| SAMEFAM-DIFFGENE : ETS | 14 | +0.1527 | PRIMARY (descriptive split, no p-value quoted) |
| SAMEFAM-DIFFGENE : CREB | 1 | +0.2731 | **TOO SMALL TO TEST (n < 4 floor); no p-value computed** |

The script printed the floor verdict for CREB and computed no p-value for it.

### 3. The methodological finding that qualifies my own decision rule

**My "clears BOTH nulls" rule is weaker than it looks, and I say so rather than banking the stronger-sounding claim.** For a class defined **purely by 3′ labels**, NULL A (permute whole names) and NULL B′ (permute 3′ labels, 5′ fixed) both induce a **uniform random permutation of the 3′ label vector**, so they are the **same null in different clothing** — which is visible in the output, where the two rows agree on null mean and null sd to four decimals. Clearing both is therefore **one** test passed twice, not two independent tests. This is a property of the design, and it is the mirror image of the degeneracy W19d demonstrated in the other direction (a 3′-only shuffle has exactly zero power for a 5′ statistic). The honest statement is: **the family effect survives the whole-name shuffle, and the 5′-fixed null adds no independent evidence for a 3′-defined class.**

### 4. POST-HOC descriptive note — NOT pre-declared, NOT tested, NO p-value

Computed after seeing the member table, so it carries no test. Splitting the 15 primary-class pairs by whether the two fusions share a 5′ partner:

| Post-hoc split of SAMEFAM-DIFFGENE | n | mean residual | Row type |
|---|---|---|---|
| same 5′ (both EWSR1) | 7 | +0.2043 | POST-HOC DESCRIPTIVE |
| **different 5′** (spans EWSR1/FUS/TMPRSS2) | **8** | **+0.1226** | POST-HOC DESCRIPTIVE |
| all | 15 | +0.1607 | PRIMARY |

The 7 same-5′ pairs are numerically W19d's post-hoc 7 (its mean, +0.2043, matches exactly). Descriptively, the effect does **not** vanish when the 5′ partner differs — 8 cross-5′ pairs still average +0.1226, an order of magnitude above the SHARES-5 residual (+0.0094) and above the NEITHER residual (−0.0071). **This was chosen after looking at the data, so no p-value is computed and none may be quoted.** It is hypothesis-generating for a successor with an independent panel, not a result.

### 5. What this answers

**ASSOCIATION.**

> Over the full 376-pair non-degenerate panel, with 3′ DBD families fixed in advance from citable sources (ETS from [DOI](https://doi.org/10.1002/jcp.27558); CREB from [DOI](https://doi.org/10.1016/j.modpat.2024.100468)), **pairs of fusions whose 3′ partners belong to the same DBD family but are different genes are markedly more similar in peak location than density predicts** — mean density residual **+0.1607**, n = 15, whole-name permutation **p < 2.1e-5** (at the 50,000-draw Monte-Carlo floor); all 15 residuals positive. The effect sits close to the same-3′-gene effect (SHARES-3, +0.1513) and roughly 17× the shared-5′ effect (SHARES-5, +0.0094, p ≈ 0.095, not significant).

**W19d's post-hoc observation therefore survives conversion into a prespecified test, on a differently and more conservatively sourced family table than the one W19d used**, and on the whole panel rather than inside one 5′ block. The direction of W19c/W19d's overall reading is reinforced: what predicts where these fusion proteins put their differential accessibility calls, on this substrate, is the **3′ DNA-binding module** — and the resolution is finer than "same gene", extending to "same DBD family, different gene". W19d's suggestion that its mild SHARES-5 positive is *"a 3′ effect leaking into the 5′ class"* is consistent with this, though nothing here tests that decomposition directly.

**PREDICTION rows: none.** No model output, extrapolation or projection appears in this report.

**UNKNOWN, preserved from the source.** Wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` have **no marker BED in the supplement at all**. Per `controls.⚠_how_to_read_a_missing_file`, the correct reading is *"the fusion arms have interval sets and the two controls have none"* — **not** that they were tested and came back empty. Likewise, 17 of 25 3′ partners have **UNKNOWN** family here: that is a limit of what I sourced in this run, not a claim that they have no DBD family.

---

## Validation evidence

Environment for every `RUN` below: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux, `cwd=/tmp/claude-0/w19e`, Python `3.11.15` (`python3 -V`), stdlib only, no network during execution, no GPU. Repository read-only; HEAD `7d081218…` → `d3e9c4d8…` (inputs byte-identical across both, diff shown above).

**RUN 1 — first invocation of the preregistered script, FAILED, exit 1.** Kept because it timestamps the order of operations.

```
$ stat -c '%n mtime=%y' dbd_family_test.py && python3 -V && date -u && time python3 dbd_family_test.py; echo "EXIT=$?"
dbd_family_test.py mtime=2026-09-08 02:40:16.343180468 +0000
Python 3.11.15
Tue Sep  8 02:40:22 UTC 2026
  File "/tmp/claude-0/w19e/dbd_family_test.py", line 310
    "pre-declared primary decision)"
IndentationError: unexpected indent
real	0m0.013s
EXIT=1
```

The repair was a print-formatting ternary rewritten as an `if/else` (a `note` string used only in a descriptive print). **No null, no decision rule, no floor, no family assignment and no statistic was touched**, and no analysis line had executed.

**RUN 2 — the preregistered analysis. `EXIT=0`.** Verbatim:

```
$ date -u && time python3 dbd_family_test.py 2>&1 | tee run1.log; echo "EXIT=${PIPESTATUS[0]}"
Tue Sep  8 02:40:30 UTC 2026
peakset_inventory entries: 128
real Supp_Data_1_new peaksets: 32
prefixes ascending-sorted: True
distinct interval widths: [500]
retained chr1 intervals/peakset: min 4 median 26 max 28
distinct 3' partners: 25
FAMILY table covers every 3' partner: True
sourced 3' genes: ['ATF1', 'CREB1', 'ERG', 'ETV1', 'ETV4', 'FEV', 'FLI1', 'NR4A3']
all pairs / non-degenerate: 496 / 376
density quintile mean J: 0.0387 / 0.0163 / 0.0126 / 0.0110 / 0.0014
class SHARES-3           n= 10  mean J 0.1715  mean residual +0.1513
class SHARES-5           n= 66  mean J 0.0300  mean residual +0.0094
class NEITHER            n=300  mean J 0.0077  mean residual -0.0071
class SAMEFAM-ANY        n= 23  mean J 0.1904  mean residual +0.1644
class SAMEFAM-DIFFGENE   n= 15  mean J 0.1887  mean residual +0.1607

[... 15-pair member table, reproduced in Result §2 ...]

=== GATE 0: reproduce W19c/W19d ARM 1 (NULL A, whole-name shuffle) ===
SHARES-5 mean residual +0.0094  p=0.09200   (targets +0.0094 / 0.09782)
SHARES-3 mean residual +0.1513  p=0.00008   (targets +0.1513 / 0.00008)
GATE 0: DISCREPANCY -- THIS IS THE MOST IMPORTANT FINDING, REPORT BOTH NUMBERS

=== PRE-DECLARED TEST: same 3' DBD family, full 376-pair panel ===
SAMEFAM-DIFFGENE   n= 15  obs +0.1607 | NULL A whole-name shuffle          null mean -0.0003 sd 0.0154  p=0.00002
SAMEFAM-DIFFGENE   n= 15  obs +0.1607 | NULL B' 3'-only shuffle, 5' fixed  null mean -0.0003 sd 0.0154  p=0.00002
SAMEFAM-ANY        n= 23  obs +0.1644 | NULL A whole-name shuffle          null mean -0.0002 sd 0.0123  p=0.00002
SAMEFAM-ANY        n= 23  obs +0.1644 | NULL B' 3'-only shuffle, 5' fixed  null mean -0.0002 sd 0.0123  p=0.00002
SAMEFAM-DIFFGENE:ETS     n= 14  mean residual +0.1527  -- n >= floor (descriptive split, not the pre-declared primary decision)
SAMEFAM-DIFFGENE:CREB    n=  1  mean residual +0.2731  -- TOO SMALL TO TEST (n < 4 floor); descriptive only, no p-value

DECISION (rule fixed before running): SAME 3' DBD FAMILY PREDICTS PEAK LOCATION (clears BOTH nulls)

real	0m23.971s
EXIT=0
```

**RUN 3 — GATE 0 discrepancy diagnostic, 8 seeds × 50,000 draws. `EXIT=0`.** Verbatim:

```
$ date -u && time python3 gate0_diag.py; echo "EXIT=$?"
Tue Sep  8 02:41:21 UTC 2026
SHARES-5 observed mean residual: +0.0094
seed 20260908 -> p = 0.09200
seed        1 -> p = 0.09440
seed        2 -> p = 0.09376
seed        3 -> p = 0.09760
seed        4 -> p = 0.09778
seed        5 -> p = 0.09554
seed        6 -> p = 0.09804
seed        7 -> p = 0.09418
min 0.09200  max 0.09804  mean 0.09541  sd 0.00221
W19c/W19d target 0.09782 inside [min,max]: True
real	0m24.162s
EXIT=0
```

Scripts (`dbd_family_test.py`, `gate0_diag.py`) and `run1.log` are under `/tmp/claude-0/w19e/`, outside the repository. Per the corrected write-isolation rule I wrote nothing into the tree; the coordinator may collect the two scripts from that path or ask me to inline them.

**PROPOSED (NOT RUN).** Sourcing the remaining 17 UNKNOWN 3′ partners against a structured DBD-family authority (e.g. the human-TF census, or per-gene primary literature) — attempted only for HNF4A/NR4A3 in one search that returned `total_count: 0`. Any within-family test restricted to non-EWSR1 5′ partners with a preregistered null. A repeat on the genome-wide peak sets — **blocked**: `MOESM3_ESM.zip` is a recorded 403 CONNECT policy denial, not probed, not retried, no alternative host sought.

**Content-policy refusals encountered: none.**

---

## Limitations

Carried forward from W19c and W19d **without softening**, plus this run's own:

- **The window is ~0.4% of the genome at the median.** Every Jaccard is computed inside `chr1:0–W`, where W is the smaller of two prefix-limited chr1 extents — median ≈ 15.8 Mb of a ~3.1 Gb genome. Nothing here describes genome-wide similarity.
- **Depths are 4–27 retained intervals per peakset.** These are 500 bp intervals read from ≤600-byte BED prefixes, not full peak catalogues. A Jaccard of 0.41 rests on 14 shared intervals.
- **Windows are pair-dependent.** W differs across pairs, so the Jaccards are not all computed on the same interval and are not strictly commensurable across the table. The density residualisation controls for interval count, not for window length.
- **HEK293T is not EMC.** These are fusion oncoproteins expressed in one HEK293T background. No statement here transfers to any tumour, tissue, patient or disease.
- **These are the authors' own marker calls** (GSE243553 supplement, doi `10.1038/s41587-024-02347-4`). **This repository called no peak** and did not reprocess any read.
- **The primary class is n = 15 pairs drawn from only 8 peaksets** (6 ETS + 2 CREB after the different-gene rule). It is not 15 independent observations: `EWSR1-ETV1` appears in 5 of the 15 pairs, `TMPRSS2-ERG` in 5. The permutation null does hold the panel composition fixed, but the effective information content is well below n = 15, and no correction for that overlap was applied.
- **14 of 15 primary-class pairs are ETS.** The test is, in practice, largely a test of the ETS family; the CREB contribution is a single pair and is below the floor. "Same DBD family" as a general rule is **not** established by this panel — one family carries it.
- **My own "both nulls" rule is one test, not two** (Result §3). I report the stronger-sounding phrasing only alongside this correction.
- **Both primary p-values are at the Monte-Carlo floor.** `p = 0.00002` means `p < 2.1e-5`; it is not a measured value and must not be quoted as one.
- **17 of 25 3′ partners are UNKNOWN.** Their pairs could not enter any family class, so the test is under-powered by construction and its coverage of the panel is partial. This is a limit of sourcing in a ~40-minute run, not evidence that those genes lack families.
- **The family definitions come from sarcoma-pathology literature, not a systematic DBD taxonomy.** S1 and S2 enumerate family members incidentally, in the course of describing fusion-driven tumours. A different authority might draw the ETS or CREB boundary differently (S2's CREB family is narrower than "bZIP"), and the result's dependence on that boundary was not tested.
- **SHARES-5's p is imprecise at the reported precision** — the five-digit figure `0.09782` is one draw from a distribution with sd ≈ 0.0022 (Result §1).
- The frozen corpus is a **selected snapshot**, not a `93b` checkout; absence within it is UNKNOWN, and my prior-work check inherits that limit.
- **No clinical or disease-identity claim is made.** This is an association between a gene-family label and interval overlap in one cell background. It establishes no efficacy, safety, selectivity, therapeutic window or clinical readiness for any agent, target or gene, and there is no wet lab.

---

## Stop condition

Set by the dispatch, and **met in full**:

1. **A sourced 32-partner family table written before any Jaccard was inspected** — met. The table (Method, STEP 1) with per-gene sources S1–S4 was written into `dbd_family_test.py` (mtime `02:40:16Z`) before the first run (`02:40:22Z`); 8 genes sourced, 17 recorded UNKNOWN rather than guessed; DDIT3 deliberately **not** inherited from W19d's symbol-reading.
2. **A preregistered test executed under both nulls with a real exit code** — met. `EXIT=0`, 50,000 draws each, seed 20260908; null, decision rule and n ≥ 4 floor fixed in the docstring beforehand; the floor was actually enforced (CREB split, n = 1, no p-value computed).
3. **The ARM 1 reproduction gate passed or a discrepancy diagnosed** — met by **diagnosis**. Every deterministic quantity reproduced exactly; the one stochastic quantity (SHARES-5 p) differed and was diagnosed as Monte-Carlo permutation-stream noise by an 8-seed re-run, with W19c/W19d's value inside the observed spread.

Returning now, as instructed.

---

## Tool-call and wall-clock count actually used

**26 tool calls.** Wall clock **02:35:36Z → 02:42:19Z = 6 min 43 s**, plus this report. Well inside the ~40-call / ~40-minute target. Compute: ~72 s of CPU across three Python runs; no GPU, no paid API, no spend.

---

## Next concrete action

**One successor, inside lane 19, and it is a falsification test rather than another confirmation:** *does the same-DBD-family effect survive when the shared-5′ pairs are removed in advance?* The pre-declared class is **SAMEFAM-DIFFGENE-DIFF5′** — same sourced 3′ family, different 3′ gene, **and different 5′ partner** — which on this panel is exactly the 8 pairs whose post-hoc mean is +0.1226 (Result §4). n = 8 clears the n ≥ 4 floor, so it is testable under the whole-name shuffle with the same substrate and residualisation, and the class is fully specified **now, before that worker sees its Jaccards** — this paragraph is its preregistration. It is the sharpest available discriminator between "the 3′ DBD family predicts location" and "EWSR1 fusions resemble each other", and it costs one 25-second run. The successor should also spend part of its budget closing the 17 UNKNOWN family assignments from a systematic DBD authority, since every one of them is currently excluded from the test by construction, and should not treat a larger sourced table as license to re-test the same hypothesis without re-declaring it.

I record honestly that this successor is **incremental**: it reuses one small frozen substrate whose limits (0.4% of the genome, 4–27 intervals, HEK293T, the authors' own calls) are not repairable by any further analysis of this file. Progress beyond it requires the genome-wide peak sets, and that route is a recorded 403 CONNECT policy denial that I did not probe, retry, or attempt to route around.
