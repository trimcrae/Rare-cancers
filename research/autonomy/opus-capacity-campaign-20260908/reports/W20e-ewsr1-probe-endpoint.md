> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W20e** · lane 20 refill · OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 02:38:05 UTC 2026` · `date -u` **end**: `Tue Sep  8 02:40:40 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start run; identical at end. The four long proxy lines — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are retained verbatim in the transcript and contain no model information):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...(truncated proxy list)
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

**HEAD actually read:** `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4` — this is **not** the brief's frozen commit `92abbcb905cacf07f14b238db50d1b98f6590374`; the checkout has moved past it, as the dispatch warned. `git status --porcelain` = 0 lines at start and at end: **the working tree was never written.** All execution was under `/tmp/claude-0/w20e/`. **No network request of any kind was made.**

---

## Question

**Does EWSR1 expression differ between the EWSR1-FISH-positive and FISH-negative arms of PRJNA1357027, measured on the one sequence in the deposit that has power against the partner-readthrough hypothesis?**

Open because W20's primary TAF15 endpoint was shown by W20c and independently by W20d to have **no power by construction** (its probe lies 1,047 nt 3′ of the exon-6 breakpoint), and W20d then found — but deliberately did **not** test — a 50-nt sequence matching EWSR1 cDNA 453–502, i.e. *inside* the portion retained in every EMC-reported EWSR1::NR4A3 chimera. W20d declined to run it because no rule had been pre-specified before the sequence was found. Pre-specifying the rule and running it is this task.

---

## Prior-work check

| Command | What it showed |
|---|---|
| `ls .../reports \| grep -i w20` | The four transferred reports exist: `W20-computational-hypothesis.md`, `W20b-partner-chromatin-interchange.md`, `W20c-temposeq-probe-position.md`, `W20d-probe-power-audit.md`. Read W20d in full; read W20's Method/Result/Limitations sections directly. |
| `grep -n -i -E "EWSR1\|453\|502\|persistence cap\|a_zero_in_the_probe\|uniq\|matcher\|cdna" W20d-probe-power-audit.md` | Confirmed W20d's §Result 4 finding, its explicit statement "**I did not test it**", and its §Next-action specification of exactly the four steps this dispatch assigns. |
| `find . -not -path "./.git/*" \( -iname "*.fa" -o -iname "*.fasta" -o -iname "*cdna*" \)` | One FASTA in the tree (`research/manuscripts/aso/fusion-junction-aso-sequences.fasta`) — an ASO design file, **not** a human cDNA set. |
| `find /tmp/claude-0/frozen-corpus/extracted -iname "*.fa" -o -iname "*.fasta*" -o -iname "*cdna*"` | **Zero hits.** The frozen corpus contains no human cDNA/ncRNA FASTA either. |
| `sed -n '380,470p' research/modalities/emc_fourth_cohort_quant.py` | The matcher's sequence set is the **Ensembl cDNA + ncRNA FASTA fetched over the network** (`_ensembl_fasta_url` → `urllib.request.urlopen`). Not committed. |

**Closed items confirmed not replayed.** No PUB-EMC-CLASSIFICATION content (user-rejected, closed). No Brenca route. No GSE4303/GSE28866 rediscovery. No NR4A Perspective. **No network request** — the vendor TempO-Seq probe manifest sits behind a recorded egress denial and was not probed, retried, or sought on another host. This is not a re-run of W20's TAF15 test: the direction is the **opposite arm** and the endpoint is a different sequence.

---

## Method / inputs

**Order of operations — and I state it explicitly, because it is the whole point of this task.** (1) Uniqueness check, (2) direction + null + decision rule + tolerance frozen in the script docstring, (3) gate against W20's committed values, (4) endpoint. The script was written **in one `Write`, then executed unmodified**: `md5sum` was `b6600fa2461013dd865bbedc18b825f2` before the run and `b6600fa2461013dd865bbedc18b825f2` after. The docstring was not edited afterwards.

**One honesty caveat on the blinding, stated up front.** I was instructed to read `W20d-probe-power-audit.md`, and that report prints the twelve raw counts of the candidate sequence in its §Result 4 table. So I had seen the raw counts before writing the docstring; I was **not** blind to them. What I was blind to — and what the preregistration genuinely fixes — is every derived quantity: the CPM normalisation, the log2 transform, δ, the 495/210-split enumeration, and the panel percentile. The **direction** is not data-derived at all: it follows from the biological model (retained 5′ portion present in both alleles of a FISH-positive tumour ⇒ higher in FISH-positive), was specified by W20d's successor note before any test, and points at the opposite arm from W20's TAF15 test. I did not compute anything before freezing the rule. I record the imperfection rather than claiming a blinding I did not have.

| Input | Path (repo `/home/user/Rare-cancers`, HEAD `d3e9c4d`) | Use |
|---|---|---|
| Candidate sequence counts | `research/modalities/emc-fourth-cohort-probe-counts.tsv` (line 129487) | endpoint counts, 12 columns |
| Panel gene counts | `research/modalities/emc-fourth-cohort-gene-counts.tsv` | 862 genes; per-column sum = library size; TAF15/FUS gate; panel calibration |
| FISH labels, persistence caps | `research/modalities/emc-fourth-cohort-quant.json` → `per_run.*.ewsr1_break_apart_fish`, `.support_floor_reads`; `⛔ a_zero_in_the_probe_table` caveat | arm assignment; Analysis C imputation |
| Transcript models | `research/modalities/emc-construct-inputs.json` → `genes.*.cdna` / `.cds` | offline uniqueness check (7 genes × 2 fields = 14 sequences) |
| Matcher provenance | `research/modalities/emc_fourth_cohort_quant.py:394–460, 583` | established that the matcher's sequence set is network-fetched Ensembl, not committed |
| Prior reports | campaign `reports/W20-*.md`, `W20c-*.md`, `W20d-*.md` | expected gate values; sequence provenance |

**Tools:** Python 3.11.15, standard library only (`json`, `math`, `itertools`, `sys`, `statistics`). No third-party package, no network, no GPU, no paid API. Script at `/tmp/claude-0/w20e/ewsr1_endpoint.py`, returned inline below.

**Pipeline (W20's own, re-implemented independently):** counts → CPM against the per-run panel library size → log2(CPM+1) → δ = mean(log2CPM, FISH-neg) − mean(log2CPM, FISH-pos) → complete enumeration of every label split at the observed group sizes. Panel percentile reported at both rank conventions (`i/n`, W20's; `(i+0.5)/n`, W20d's).

---

## Result

### Step 1 — uniqueness: **partially checked; the check the question requires COULD NOT BE MADE OFFLINE**

`RUN`, exit 0. Against the committed transcript models the sequence has **exactly one** occurrence, antisense, at **EWSR1 cDNA 453–502** (and the corresponding CDS 384–433 — the same locus, not a second site). Zero occurrences in TAF15, FUS, TCF12, TFG, NR4A3 or PGR cDNA/CDS.

That is a check over **14 sequences from 7 genes**, not over a human transcriptome. The matcher whose `unassigned` label is at issue scanned the **Ensembl cDNA + ncRNA FASTA over the network**; that file is not in the repository and not in the frozen corpus, and network access is forbidden here. **Uniqueness across the matcher's own human sequence set could not be checked offline.** I state this plainly rather than passing off the 7-gene check as the answer. Consequence: a second genomic locus carrying this 50-mer would not have been detected, and would break the attribution of these counts to EWSR1.

### Step 2 — preregistration (frozen before execution, verbatim from the docstring)

- **Direction:** EWSR1 higher in the EWSR1-FISH-**POSITIVE** arm ⇒ in W20's sign convention, **δ < 0**.
- **Null H0:** δ = 0; labels exchangeable.
- **Decision rule:** SUPPORTED if δ<0 **and** one-sided p₁ ≤ 0.05; REFUTED if δ>0 **and** two-sided p ≤ 0.05; NULL otherwise.
- **Power floor stated before the result:** smallest attainable one-sided p is 1/495 = 0.00202 (n=4 vs 8) and 1/210 = 0.00476 (n=4 vs 6). Both clear 0.05, so the test is **not powerless by construction**.
- **Gate tolerance:** |δ| and |p| to 5e-4; panel percentile to 0.10 absolute (absorbing the documented `i/n` vs `(i+0.5)/n` convention gap, and nothing larger).
- **Zero handling** (three analyses, primary named in advance): A = drop, B = literal zeros, C = impute at the run's persistence cap.

### Step 3 — GATE: **PASS, exact to every reported digit**

| Gene | δ observed | δ expected (W20) | p₁(δ>0) obs / exp | p₂ obs / exp | pct `i/n` | pct `(i+0.5)/n` | expected pct |
|---|---|---|---|---|---|---|---|
| **TAF15** `PRIMARY` | −0.8347 | −0.8347 ✓ | 0.9899 / 0.9899 ✓ | 0.0182 / 0.0182 ✓ | **9.05** | 9.11 | 9.05 ✓ |
| **FUS** `PRIMARY` | +0.0789 | +0.0789 ✓ | 0.4808 / 0.4808 ✓ | 0.9131 / 0.9131 ✓ | **62.06** | 62.12 | 62.06 ✓ |

495 splits enumerated in each case; 8/4 FISH split reproduces (`EWSR1−` = SRR35940648, 654, 656, 657). **No discrepancy to report** — which is the outcome the dispatch flagged as most important if it had gone the other way. Note this also **resolves W20d's open +0.06 percentile question**: W20 used the `i/n` convention (9.05, 62.06 reproduce exactly at `i/n`), W20d used midpoint. A convention difference, confirmed, not an error in either.

### Step 4 — ENDPOINT: **NULL under all three zero-handlings**

Raw counts of `GCTTGTTTCCATCC…GCTGCTGC`, `assigned_gene` = `unassigned` in the TSV:

| Run | 646 | 647 | **648** | 649 | 650 | 651 | 652 | 653 | **654** | 655 | **656** | **657** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| count | 337 | 521 | 423 | 459 | 807 | **0** | **0** | 735 | 791 | 999 | 281 | 183 |
| FISH | + | + | **−** | + | + | + | + | + | **−** | + | **−** | **−** |

Both zero runs (SRR35940651, SRR35940652 — the two smallest libraries, 164,967 and 140,423 panel reads) are in the **FISH-positive** arm.

| Analysis | Zero handling | n neg/tot | δ (log2CPM) | p₁ (δ<0, declared direction) | p₂ | splits | panel pct `i/n` | Verdict | Row type |
|---|---|---|---|---|---|---|---|---|---|
| **A (PRIMARY)** | dropped as *below persistence cap* | 4/10 | **−0.4766** | **0.1476** | 0.3476 | 210 | 22.62 | **NULL** | `PRIMARY` |
| B (secondary) | literal zeros (W20's pipeline as written) | 4/12 | +1.9651 | 0.6384 | 0.4545 | 495 | 100.00 | **NULL** | `SECONDARY` |
| C (sensitivity) | imputed at each run's `support_floor_reads` (13.4, 13.0) | 4/12 | +0.3514 | 0.6303 | 0.7677 | 495 | 80.05 | **NULL** | `SECONDARY` |

Uncertainty definitions: p-values are **exact**, from complete enumeration of every label split at the observed group sizes — no asymptotics, no resampling error, no seed. Panel percentile is the rank of δ among all 862 panel genes' δ computed on the same runs.

**Answer to the question, stated with the same willingness as a positive would be: NO detectable difference.** On the one sequence in this deposit that has power against the partner-readthrough hypothesis, EWSR1 abundance does **not** differ between the EWSR1-FISH-positive and FISH-negative arms of PRJNA1357027. This is `UNVERIFIED` as to probe identity (below) but the statistical verdict itself is definite.

**The zero handling IS load-bearing — for the sign, not for the verdict.** Because both zeros sit in the FISH-positive arm, treating them as real zeros (B) drags the positive-arm mean down and **flips δ from −0.48 to +1.97**, i.e. from the H1 direction to the anti-H1 direction, and pushes the gene from the 23rd to the **100th** panel percentile. That is a large artefact manufactured entirely by a value the source module itself says is not a measurement. Had W20's pipeline been applied literally and unexamined, this endpoint would have read as a dramatic reversal. The three verdicts nonetheless agree: **NULL**. So the pre-specified handling changed the story but not the conclusion — and reporting all three is what makes that visible.

**What the null does and does not mean.** A one-sided p of 0.1476 on n=4 vs 6 is *not* evidence of no effect; with 210 splits and this dispersion the test can only detect a fairly large shift. The point estimate (δ = −0.48, EWSR1 nominally higher in the FISH-positive arm) is *consistent* with H1 in direction and gives no support to it in magnitude. This is an underpowered null, and I label it as such rather than as absence of an effect.

---

## Validation evidence

**RUN.** Environment: Python 3.11.15, stdlib only; container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`; repo HEAD `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`; working tree unmodified (`git status --porcelain` → 0 lines, start and end).

```
$ python3 --version && python3 /tmp/claude-0/w20e/ewsr1_endpoint.py; echo "EXIT=$?"
Python 3.11.15
```

Verbatim key output (full output in the transcript):

```
STEP 1 - UNIQUENESS CHECK (offline, bounded)
  HIT EWSR1.cdna antisense: n=1 at 1-based 453..502 (len 2400)
  HIT EWSR1.cds  antisense: n=1 at 1-based 384..433 (len 1971)
  transcripts searched offline: 14 fields over 7 genes; total exact occurrences of S (either strand) = 2
  ⛔ ... uniqueness across the matcher's own human sequence set COULD NOT BE CHECKED OFFLINE.

runs=12  panel genes=862  EWSR1-=['SRR35940648','SRR35940654','SRR35940656','SRR35940657']  n_pos=8
library sizes (panel reads): [375572, 1174158, 907268, 588992, 1066043, 164967, 140423, 292897,
                              994241, 1356848, 406135, 307583]

GATE - reproduce W20's committed TAF15 / FUS values
  TAF15  delta=-0.8347 (exp -0.8347 OK)  p1(d>0)=0.9899 (exp 0.9899 OK)  p2=0.0182 (exp 0.0182 OK)
         pct i/n=9.05  (i+.5)/n=9.11  (exp 9.05 OK)   splits enumerated=495
  FUS    delta=+0.0789 (exp +0.0789 OK)  p1(d>0)=0.4808 (exp 0.4808 OK)  p2=0.9131 (exp 0.9131 OK)
         pct i/n=62.06  (i+.5)/n=62.12  (exp 62.06 OK)   splits enumerated=495
  GATE: PASS

ENDPOINT - candidate EWSR1 sequence S
  assigned_gene in TSV = 'unassigned'
  runs reading 0 (treated as BELOW PERSISTENCE CAP, not zero):
      [('SRR35940651','EWSR1+'), ('SRR35940652','EWSR1+')]
  persistence caps used in C: {'SRR35940651': 13.4, 'SRR35940652': 13.0}

  analysis    n(neg/tot)     delta   p1(d<0)       p2  splits  pct i/n  pct mid  verdict
  A_drop     4/10          -0.4766    0.1476   0.3476     210    22.62    22.68  NULL
  B_zeros    4/12          +1.9651    0.6384   0.4545     495   100.00   100.06  NULL
  C_cap      4/12          +0.3514    0.6303   0.7677     495    80.05    80.10  NULL

  GATE=PASS
EXIT=0
```

**Exit code: 0** (the script exits 0 only on `GATE=PASS`; a gate failure would have exited 4, a missing sequence 3).

**Preregistration integrity:** `md5sum /tmp/claude-0/w20e/ewsr1_endpoint.py` = `b6600fa2461013dd865bbedc18b825f2` **before** execution and `b6600fa2461013dd865bbedc18b825f2` **after**. The docstring containing direction, null, decision rule, tolerance and zero-handling plan is byte-identical pre- and post-run.

**PROPOSED (NOT RUN):** confirmation of the sequence's identity as the vendor's EWSR1 TempO-Seq probe (requires the vendor manifest — recorded egress denial, not attempted); uniqueness across the Ensembl cDNA+ncRNA set (requires the network fetch the matcher performs — not attempted); `scripts/preflight.sh` (dispatch did not authorise it and nothing in the tree was changed).

Script, returned inline per the write-isolation rule (not written into the repository) — the full text is the file quoted above at `/tmp/claude-0/w20e/ewsr1_endpoint.py`; its docstring is reproduced verbatim in §Result Step 2 and its computational body is the six functions `rc`, `l2cpm`, `enumerate_delta`, `test`, `panel_deltas`, `pct` plus the three-analysis driver. The coordinator can reproduce it byte-for-byte from that path while the container lives.

---

## Limitations

- **UNVERIFIED probe identity — this is the governing limitation.** I have not established that this 50-mer *is* the vendor's EWSR1 probe. An exact unique cDNA match with real counts in 10 of 12 runs is **consistent with** a probe and is **not proof** of one. The vendor manifest is behind a recorded egress denial and was not probed. Every number above is therefore a measurement on *a sequence that matches EWSR1 cDNA*, not certifiably on *the EWSR1 probe*.
- **The uniqueness check the question asked for was not achievable offline.** 7 genes ≠ a transcriptome. A second locus carrying this 50-mer is UNKNOWN, not excluded.
- **Underpowered null.** n = 4 vs 6 (primary) or 4 vs 8. p₁ = 0.1476 is not evidence of no effect; only a large shift was detectable.
- **The endpoint sequence was never offered to the matcher**, so it carries no independent gene assignment in the committed table — the `unassigned` label reflects the intersection-across-runs filter W20d diagnosed, not a failed match.
- **Zeros remain missing data.** Analyses A and C are both principled guesses about a value the deposit does not contain. C's imputation at `support_floor_reads` is the *most H1-favourable* value consistent with the caveat and still yields NULL, which bounds the direction of that uncertainty but does not remove it.
- **FFPE, 23 collection years, one deposit.** Specimen degradation and biology are not separable in this metadata. `Prognosis` B/G remains undefined by the deposit and was not used.
- **No transfer.** This is an association within one deposit, not a validated finding, and not transferable to any other cohort.
- **NO CLINICAL CLAIM.** 12 FFPE tumour BioSamples establish nothing about EMC efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness. Nothing here bears on any agent or target. No reagent was designed. **Runs are not samples and samples are not people.**

---

## Stop condition

Set by the dispatch; **MET in full**:

1. Uniqueness — checked as far as offline permits, and its **impossibility across the matcher's own set stated plainly**, not skipped. ✓
2. Direction, null, decision rule and tolerance **preregistered in the script docstring before execution**, md5-verified unchanged after. ✓
3. W20's TAF15 and FUS values **reproduced exactly as a gate** (PASS; no discrepancy; the `i/n` vs `(i+0.5)/n` convention question left open by W20d is resolved in W20's favour). ✓
4. EWSR1 endpoint run to a **definite verdict — NULL under all three zero-handlings** — with a **real exit code, 0**. ✓

Returning immediately, as instructed.

---

## Tool-call and wall-clock count actually used

**10 tool calls** (all `Bash`, one of which was the heredoc that wrote the script). **Wall clock: 2 min 35 s** (02:38:05Z → 02:40:40Z). Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**One successor for this lane: fix the `n_probes_common_to_every_read_run` intersection filter that caused this, and re-derive the panel — a defect repair with a measurable size, not another endpoint.**

`emc_fourth_cohort_quant.py:583` offers the matcher only the 1,645 sequences present in *every* run, so any sequence falling below the persistence cap in even one small-library run is silently excluded from the probe→gene map and lands in the 212,101-strong `unassigned` bucket. That single line is why EWSR1 — the cohort's defining gene — was reported as "absent from this panel". The repair is to offer the matcher the union of sequences present in ≥ k runs (or all 213,007, if the matcher's budget allows) and record, per sequence, in how many runs it was persisted. The concrete deliverable is the **count of genes recovered** by that change: W20d already found EWSR1, TCF12 and TFG by hand, and the true number is unknown and probably larger. That is bounded, offline-checkable in its logic, and it converts a hand-diagnosed defect into a committed, reproducible correction.

Two things this successor must **not** do. It must not re-run the EWSR1 endpoint — that is now answered, and repeating it on a re-derived panel would be exactly the post-hoc iteration W20d refused. And it cannot execute the matcher itself, because that requires the Ensembl network fetch; the repair is therefore a **code-and-logic** deliverable plus a `PROPOSED (NOT RUN)` note on the fetch, unless a CI escape hatch is separately authorised.

A second, smaller item worth routing to whoever owns the report files: **W20's Limitations sentence "the fusion-transcript question cannot be asked of this cohort at all" is now doubly wrong** — W20d showed the sequence exists, and this worker showed the question can be *asked and answered*. The answer is a null, and W20d's proposed replacement wording should be updated to say so rather than leaving the question "open pending a pre-specified test".
