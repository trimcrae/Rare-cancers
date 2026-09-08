<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:22:05Z UTC
     agent id ad4dbb5eef0bd4aa9 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad4dbb5eef0bd4aa9.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

- **Worker:** W03e, lane 3 refill, OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model; the coordinator must extract the served model from the child transcript.
- `date -u` **start:** `Tue Sep  8 02:50:42 UTC 2026`. `date -u` **end:** `Tue Sep  8 03:17:38 UTC 2026`.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (verbatim, captured at start):

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
GLOBAL_AGENT_NO_PROXY=... (same no_proxy list)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=... (truststore/proxy flags only)
NO_PROXY=... (same list)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=... (same list)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**No variable names a model.**

- **HEAD actually read: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`** (start). This is not the brief's `92abbcb…` and not W03d's `7d08121…`; the coordinator is committing during the campaign. HEAD at end: `c81236b90c7905caa2e75a57b332ad33f2c10d02`. My scratch copy was taken at `3f5fc95d`; **all results are valid for `3f5fc95d`.**
- `git status --porcelain` **at start: empty.** At end: **empty** (an intermediate reading at 03:13:04Z showed eight untracked `W*.md` files under `research/autonomy/opus-capacity-campaign-20260908/reports/` — other workers' reports being landed by the coordinator, since committed; none of them mine). **I wrote nothing into the Git working tree and ran no git write operation.** All execution was under `/tmp/claude-0/w03e/` on `tar --exclude=./.git` copies with no `.git` directory (verified: `ls /tmp/claude-0/w03e/tree/.git` → *No such file or directory*).
- Corpus consulted: the live checkout only. This is a behavioural test of live code, not a novelty or absence claim, so I did not need `/tmp/claude-0/frozen-corpus/`; I did not copy or overlay it.

## Question

**Does the rest of the ASO generator chain survive W03d's degraded-input probe — how many of its `--check` guards are real, how many are fake, and is the exon-2 acceptor finding protected by any of them?**

Open because W03d proved exactly one guard sound (`aso_per_junction_table.main(["--check"])`, 8/8 degradations detected) and W14b measured a 36 % `FAKE-GUARD` rate over 179 confirmed generators repository-wide, with one genuinely advertised-but-incapable `--check`. Whether the ASO chain — the deposit path for PUB-ASO, the first manuscript to finish — sits on the reassuring or the alarming side of that distribution was unmeasured.

## Prior-work check

```
cat research/autonomy/opus-capacity-campaign-20260908/{COMMON-BRIEF,CLOSED-WORK,CORPUS-CONTEXT}.md          # read in full
cat .../reports/{W03b-acceptor-blast-radius,W03c-panel-guard-mutation-test,W03d-aso-check-degraded-input}.md  # read
cat .../reports/{W14b-guard-coverage-sweep,W14c-fake-guard-repair-proof}.md                                   # read
rg -n -i "regenerate_aso_chain.*--check|aso chain guard|chain guard" --glob '!.git' -l
rg -n --glob '*.py' -l 'nr4a3-acceptor-exon-numbering|noncoding-acceptor|NR4A3_e2|acceptor_exon' research/
grep -n 'run_step ' scripts/regenerate_aso_chain.sh
```

The `rg` for chain-guard prior work returned nine hits, all pre-existing repository content (the chain script itself, `aso_archive_manifest.py`, two sprint notes, a receipt, a review seat, the research ledger) — **no prior worker report probes the ASO chain's `--check` guards.** `research/manuscripts/aso/fusion-junction-aso-guard-coverage-audit.md` (DOC-ASO-GUARD-COVERAGE-AUDIT-2026-08-27) is the nearest prior art and is **a different question**: it mutated 42 *manuscript sentences* and asked which *tests and linters* caught them (34/42 shipped green). It does not degrade a committed *input* and does not measure any generator's `--check`.

**Reused as inputs, not re-run, exactly as dispatched:** W03c's five-mutation battery (mutation score 5/5, baseline 183 passed) and W03d's eight-degradation probe of `aso_per_junction_table` (8/8 detected, plus control). **I did not re-run either**, and `aso_per_junction_table.py` appears in my tally carrying W03d's result, not a fresh one.

**Not replayed, per `CLOSED-WORK.md`:** no network retrieval of any kind was attempted by me, so no denied route was replayed; no Brenca/Hofvander/pazopanib/sunitinib/Wagner/CTARC/trabectedin route; no GSE4303/GSE28866; no PUB-EMC-CLASSIFICATION; no lane-11 source-index work; the restricted NR4A Perspective was not touched under any framing. **I did not open a review round on PUB-ASO, did not edit any manuscript or preregistration, did not run `scripts/preflight.sh`, and did not design or modify any oligonucleotide sequence.**

## Method / inputs

Read-only static read of the live tree at `3f5fc95d`, then a differential experiment entirely under `/tmp/claude-0/w03e/`.

**Enumeration.** The authoritative chain is `scripts/regenerate_aso_chain.sh`, whose 25 `run_step` entries each carry `"label|command|check-command"`. I took its 10 non-empty check-commands, added `research/modalities/aso_per_junction_table.py` and `aso_noncoding_acceptor_screened_table.py` (which have a `--check` the chain does not use), and swept every other ASO-artifact writer under `research/manuscripts/` and `research/modalities/` for `add_argument("--check")` / `"--check" in argv`. That is **19 verification paths**, table in Result R1.

**Copy.** `tar --exclude=./.git --exclude='*/__pycache__' -cf tree.tar .` → extracted to `/tmp/claude-0/w03e/tree`, 609 MB, no `.git`. A pristine reference copy of `research/` (416 MB) was taken once; every degradation was restored from it by mtime-diff before the next trial. Three shard copies (`tree0`–`tree2`) ran the battery in parallel.

**Probe harness** (`/tmp/claude-0/w03e/battery.py` + `trace_run.py`, quoted below). Per generator:
1. Run `--check` under a `builtins.open`/`io.open` tracer → real exit code, the exact set of files read, the exact set opened for write.
2. Detect artifact rewriting by mtime (`find research -newer STAMP`) **and** by the write-mode open set. *The scratch copy has no `.git`, so `git status --porcelain` cannot be run there; this mtime+open-mode pair is the equivalent detector and I report it as such rather than claiming a git check I did not run. The real tree's `git status` was taken at start and end.*
3. Learn the generator's true outputs by running its write command once and diffing.
4. Degrade one committed **input** (excluding its own outputs and `.py` files) and re-run `--check`. Degradations: drop the last element of the largest list; mutate the first character of a string field; perturb an integer field; truncate the file to 60 % of its bytes. A degradation that `--check` survives is only called a miss if the **write path** demonstrably produces different output bytes from it (materiality proof), or cannot run at all.

**Environment.** Linux, CPython **3.11.15** (`/usr/local/bin/python3`), stdlib only. No network available (the egress proxy returned `403 Forbidden` on every CONNECT). `scripts/preflight.sh` **not run**; `PREFLIGHT_FULL` **not set**. These are **not** preflight results.

## Result

### R1 — Every ASO-chain verification path, with its check entry point and verdict (PRIMARY unless marked)

n = 19. "Real" = green baseline, a degraded committed input detected with a non-zero exit, green restore, and nothing written during `--check`.

| # | Generator (`file:line` of check entry) | In chain? | Baseline `--check` | Degradation detected | Wrote during `--check` | Verdict | Grade |
|---|---|---|---|---|---|---|---|
| 1 | `research/modalities/aso_per_junction_table.py:404,408` | yes (`:264`, **check-command empty**) | 0 | **8/8 + control** | no | **REAL** | PRIMARY (**reused from W03d, not re-run**) |
| 2 | `research/modalities/junction_aso_thermo.py:443` | yes (`:250`) | 0 | yes | no | **REAL** | PRIMARY |
| 3 | `research/modalities/aso_offtarget_duplex_energy.py:345,356` | yes (`:256`) | 0 | yes | no | **REAL** | PRIMARY |
| 4 | `research/modalities/offtarget_chance_baseline.py:709` | yes (`:249`, **check-command empty**) | 0 | yes | no | **REAL** | PRIMARY |
| 5 | `research/modalities/aso_noncoding_acceptor_screened_table.py:491,495` | yes (`:265`, **check-command empty**) | 0 | yes | no | **REAL** | PRIMARY |
| 6 | `research/modalities/aso_parent_gap_pairing.py:285` | no | 0 | yes | no | **REAL** | PRIMARY |
| 7 | `research/modalities/aso_gap_length_tradeoff.py:879` | no | 0 | yes | no | **REAL** | PRIMARY |
| 8 | `research/manuscripts/figures/aso_figure_provenance.py:154` | yes (`:293`) | 0 | yes | no | **REAL** | PRIMARY |
| 9 | `research/manuscripts/submission_tables.py:3172` | yes (`:294`) | 0 | yes | no | **REAL** | PRIMARY |
| 10 | `research/manuscripts/submission_metrics.py:605` | yes (`:296`) | 0 | yes | no | **REAL** | PRIMARY |
| 11 | `research/manuscripts/claim_coverage.py:806` | yes (`:311`) | 0 | yes | no | **REAL** | PRIMARY |
| 12 | `research/manuscripts/aso_sequence_manifest.py:1164,1181` | yes (`:318`) | 0 | yes | no | **REAL** | PRIMARY |
| 13 | **`research/manuscripts/submission_citations.py:460`** | **yes (`:295`)** | **0** | **NO — returned 0** | **no** | **FAKE (silent-pass class)** | **PRIMARY** |
| 14 | `research/manuscripts/aso_archive_manifest.py` (`main` `--check`) | yes (`:423`) | **1** | (1, but baseline already 1) | no | **RED BASELINE — cannot discriminate** | PRIMARY |
| 15 | `research/manuscripts/aso_deposit_drift.py:133` | no | **1** | (1, but baseline already 1) | no | **RED BASELINE — cannot discriminate** | PRIMARY |
| 16 | `research/manuscripts/aso_priorart_evidence.py:136` | yes (`:319`) | **2** (refuses: `origin/literature-cache` absent) | not probeable | no | **UNKNOWN — prerequisite absent** | PRIMARY |
| 17 | `research/manuscripts/aso_reagent_coverage.py:241` | no | 0 | n/a — **zero external data inputs** | no | **REAL by construction** (compares the artifact against an in-source derivation; probe inapplicable) | PRIMARY |
| 18 | `research/modalities/aso_noncoding_acceptor_designs.py:1178` | no | TIMEOUT at 90 s (Ensembl retries) | not probed | no | **UNKNOWN — not probed** | UNKNOWN |
| 19 | `research/manuscripts/aso_coverage_ladder.py:1885` | no | 99 (`ModuleNotFoundError: aso_reagent_coverage` under my `runpy` tracer) | not probed | no | **UNKNOWN — harness artifact, not a repository defect** | UNKNOWN |

### R2 — The tally

| Class | n | share of the 19 |
|---|---|---|
| **REAL** (12) + **REAL by construction** (1) | **13** | 68 % |
| **FAKE** — returns 0 on a material degraded input | **1** | 5 % |
| **FAKE of the more serious kind** — rewrites the artifact it verifies | **0** | **0 %** |
| **RED BASELINE** — guard present, currently non-zero, cannot discriminate here | 2 | 11 % |
| **UNKNOWN** — not probeable in this environment | 3 | 16 % |

**Zero of the 18 generators I executed opened any file for writing during `--check`, and zero modified any file under `research/`.** The `emc_fourth_cohort_quant.py` failure mode W14b and W14c dissected — a `--check` that overwrites the artifact and then hashes what it just wrote — **does not occur anywhere in the ASO chain.** That is the single most reassuring number in this report, and it is measured, not inferred.

### R3 — The one fake guard: `submission_citations.py:460`

**Mechanism, read from source after the probe flagged it.** The `--check` branch verifies **the manuscript against itself**: for each superscript it recomputes the number the PMID annotations imply and compares it with the number printed. That check is sound for what it checks. But `regenerate_aso_chain.sh:295` wires this `--check` as the verification for the step whose write command (`--write`) produces two committed deposit artifacts — `fusion-junction-aso-submission-references.md` and `.json` — and **`--check` never looks at either file.** The comparison is between the manuscript and the manuscript.

Consequences, both executed:

| Leg | Evidence | Grade |
|---|---|---|
| Truncating `fusion-junction-aso-research-article.md` (an input `--check` reads) to 60 % → `--check` prints `citation numbering is current`, **exit 0**, while the write path produces **different bytes in both committed artifacts** | run below | PRIMARY |
| Corrupting the committed `fusion-junction-aso-submission-references.json` itself (`n_references` 53 → 60) → `--check` prints `citation numbering is current`, **exit 0**; the file is **not** rewritten (so this is the silent-pass class, not W14b's more serious rewrite class) | run below | PRIMARY |

The internal check still catches what it was written for (`submission_citations.py:461-468` documents the 2026-08-13 review that added it, and that mode is intact). The gap is that a chain step is vouched for by a check of a different property.

**The smallest correct repair — returned inline, NOT written into the tree.** It only *adds* a comparison; it removes, relaxes and reorders nothing.

Step 1 — make the existing `--write` payload reusable, without changing a byte of what it renders. The block currently inside `if "--write" in argv:` at `submission_citations.py:413-459` becomes a function `_render(order, meta, missing, bare)` returning `(md_text, json_obj)`; the write branch then reads:

```python
        md_text, json_obj = _render(order, meta, missing, bare)
        open(OUT_MD, "w", encoding="utf-8").write(md_text)
        json.dump(json_obj, open(OUT_JSON, "w"), indent=2)
        print(f"  wrote {os.path.basename(OUT_MD)} and {os.path.basename(OUT_JSON)}")
```

Step 2 — the actual repair, inserted in the `--check` branch immediately before the existing final `print("  citation numbering is current")`:

```python
        # ★ REPAIR (W03e): the superscript check above verifies the MANUSCRIPT against itself.
        # regenerate_aso_chain.sh wires this --check to the step that WRITES the two committed
        # reference artifacts, so it must also compare those artifacts with what --write produces.
        md_text, json_obj = _render(order, meta, missing, bare)
        drifted = []
        for path, want in ((OUT_MD, md_text), (OUT_JSON, json.dumps(json_obj, indent=2))):
            if not os.path.exists(path):
                drifted.append(os.path.basename(path) + " (missing)")
            elif open(path, encoding="utf-8").read() != want:
                drifted.append(os.path.basename(path))
        if drifted:
            print("citation artifacts are stale: " + ", ".join(drifted)
                  + " -- re-run with --write", file=sys.stderr)
            return 1
```

**The repaired guard discriminates — four executed acceptance runs, including the negative control:**

| Test | Expected | Observed | Grade |
|---|---|---|---|
| T1 repaired `--check`, pristine tree | 0 | `citation numbering is current`, **exit 0** | PRIMARY |
| T2 repaired `--check`, research article truncated to 60 % | 1 | `citation artifacts are stale: …references.md, …references.json`, **exit 1** | PRIMARY |
| **T3 NEGATIVE CONTROL** — article restored, committed `references.json` perturbed (`n_references` +7) | 1, naming **only** that file | `citation artifacts are stale: fusion-junction-aso-submission-references.json`, **exit 1** | PRIMARY |
| T4 restore everything | 0 | `citation numbering is current`, **exit 0** | PRIMARY |
| T5 repaired `--write` on a pristine tree | committed bytes unchanged | `sha256sum -c` **OK** on both artifacts; both identical to the pristine copies | PRIMARY |

T3 is the discrimination proof the dispatch asked for: the **unrepaired** guard returns **0** on that exact corruption (measured), the repaired one returns **1** and names the corrupted file. **No committed value changes** (T5).

### R4 — Chain-level finding: three working `--check` modes the chain does not use (PRIMARY)

`regenerate_aso_chain.sh` passes an **empty check-command** for eleven steps, and for those `--check` prints `⚠ NOT VERIFIED -- this producer has no --check mode` (`:208`) and ends at `:481-485`:

```
ASO CHAIN: every checkable producer is current, but --check CANNOT VOUCH FOR:<labels>
Give each of those a --check mode; until then a green --check is a partial answer.
exit 0
```

**Three of those producers do have a working `--check`**, measured REAL above: `aso_per_junction_table.py` (`:264` — the very guard W03d proved sound), `offtarget_chance_baseline.py` (`:249`), `aso_noncoding_acceptor_screened_table.py` (`:265`). The chain says "no `--check` mode" about three producers that have one.

**This is honest-but-unwired, not a fake guard**, and the distinction matters: the chain *names* what it cannot vouch for rather than reporting green over it, which is exactly the 2026-08-16 fix its own comment block records. The defect is that the statement is now factually wrong for three rows, and three real guards go unrun in the chain. The exit code is nevertheless **0**.

### R5 — Is the exon-2 acceptor finding protected? (PRIMARY — the direct answer to dispatch item 4)

W03b closed the exon-2 acceptor question as **ALREADY-KNOWN**: the compensating lane exists, is screened, and ships. **Yes, it is protected — by exactly one generator guard, and that guard is real; but the chain does not run it.**

| Protection | Status | Grade |
|---|---|---|
| `aso_noncoding_acceptor_screened_table.py --check` (`:491,495`) — the exon-2 lane's own table | **REAL and it fires.** Its `--check` reads 21 committed data inputs, among them all four exon-2 screens (`…/noncoding-acceptor/junction-aso-offtarget-{e7n2,e13n2,pgre2n2,taf15e6n2}-deep500.json`) and `nr4a3-fusion-junction-atlas-noncoding-acceptor.json`. Truncating the **`e7n2`** screen — the `EWSR1` exon 7 → *NR4A3* exon 2 junction W03b's finding turns on — gave **exit 1** with a named, specific refusal (quoted below), and a restore returned **exit 0**. It wrote nothing. | PRIMARY |
| `aso_sequence_manifest.py --check` (`:1164,1181`) | **REAL** (detected a degraded input, exit non-zero, green baseline and restore). W03b records that it joins the noncoding-acceptor table beside the panel (`:344,390,610`). I did **not** degrade an exon-2-specific input for this generator, so its exon-2 sensitivity specifically is **UNKNOWN**. | PRIMARY / UNKNOWN |
| `regenerate_aso_chain.sh --check` | **NO protection.** The exon-2 lane's step is `run_step "non-canonical acceptor table" … ""` (`:265`) — empty check-command, so the chain prints `NOT VERIFIED` for it and exits 0. | PRIMARY |
| `aso_per_junction_table.py --check` | **NO protection.** Its panel is the 38 exon-3 junctions; the exon-2 lane is a separate artifact family. (W03b, W03c, W03d, consistent.) | SECONDARY |
| `aso_noncoding_acceptor_designs.py --check` (`:1178`) | **UNKNOWN** — timed out at 90 s on Ensembl retries; not probed. | UNKNOWN |
| The manuscript prose | Held by a **test**, not a generator guard: `research/manuscripts/tests/test_the_exon2_reading_stands_without_an_unpublished_sequence.py`, whose docstring states it checks the four hedging sentences, explicitly **not** that the exon-2 reading is correct. I read it; **I did not run it.** | SECONDARY |

So: **one real generator guard stands between the exon-2 lane and silent drift, it discriminates, and the chain script does not call it.** Wiring `"python3 $MOD/aso_noncoding_acceptor_screened_table.py --check"` into `regenerate_aso_chain.sh:265` is a one-string change that tightens the chain and weakens nothing — but it is the PUB-ASO owner's call, and **I did not make it.**

### R6 — Incidental measured finding: two chain `--check` paths attempt network egress (PRIMARY)

`aso_noncoding_acceptor_screened_table.py --check` and `aso_noncoding_acceptor_designs.py --check` call Ensembl REST during `build()` and retry four times per gene symbol before falling back:

```
  retry 4 https://rest.ensembl.org/lookup/symbol/homo_sapiens/EWSR1?expand=1: <urlopen error Tunnel connection failed: 403 Forbidden>
  Ensembl unreachable for EWSR1 (failed: …); using the committed cache
```

**The fallback is correct** — it uses the committed cache and says so — so this is a runtime cost, not a correctness defect. But it makes those two `--check` runs take minutes offline where the rest take seconds, and the chain's own header states it "regenerates only what is derivable offline from committed artifacts". Reported as an observation; **no change proposed.** The `403` is an ordinary proxy denial, recorded, not routed around.

## Validation evidence

**RUN.** Environment for every run: Linux, CPython **3.11.15**, stdlib only, no network, working directory `/tmp/claude-0/w03e/tree{,0,1,2}/`, outside the repository. **Not preflight.**

**Tracer** (`/tmp/claude-0/w03e/trace_run.py`, load-bearing part):

```python
_open = builtins.open
def myopen(file, mode='r', *a, **k):
    p = os.path.abspath(file)
    if any(c in mode for c in 'wxa+'): writes.add(p)
    else: reads.add(p)
    return _open(file, mode, *a, **k)
builtins.open = myopen; io.open = myopen
```

**The tracer's rc 99 = an uncaught exception; the real shell exit is 1.** Verified directly, with the full bracket:

```
$ cd /tmp/claude-0/w03e/tree && python3 research/modalities/junction_aso_thermo.py --check
thermo artifact is current
PRISTINE_EXIT=0
$ # truncate nr4a3-fusion-junction-atlas.json to 60% of its bytes
$ python3 research/modalities/junction_aso_thermo.py --check
  File ".../junction_aso_thermo.py", line 312, in build
    atlas = json.load(open(ATLAS))
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 7506 column 10 (char 257427)
TRUNCATED_EXIT=1
$ # restore
$ python3 research/modalities/junction_aso_thermo.py --check
thermo artifact is current
RESTORED_EXIT=0
```

**Representative detections, verbatim from the battery** (one row per generator; each has a green baseline in the same interpreter minutes earlier):

```
aso_offtarget_duplex_energy.py  | junction-aso-offtarget-tfge4n3-deep500-b2.json, dropped last of a 367-list
  ::error::aso-offtarget-duplex-energy.json is stale — re-run without --check          rc 1  DETECTED
offtarget_chance_baseline.py    | aso-insilico-evaluation-e12n3-20mer-deep500.json truncated to 60%
  GeometryError: … unreadable (Expecting property name … char 5269)                    rc 1  DETECTED
aso_figure_provenance.py        | aso-gap-length-tradeoff.json truncated to 60%        rc 1  DETECTED
submission_metrics.py           | emc-surface-target-landscape.md, last non-empty line dropped  rc 1  DETECTED
claim_coverage.py               | nr4a3-degrader-paper.md truncated to 60%             rc 1  DETECTED
submission_tables.py            | aso-gap-length-tradeoff.json truncated to 60%        rc 1  DETECTED
aso_sequence_manifest.py        | aso-gap-length-tradeoff.json truncated to 60%        rc 1  DETECTED
aso_parent_gap_pairing.py       | aso-premrna-sequences.json truncated to 60%          rc 1  DETECTED
aso_gap_length_tradeoff.py      | junction-aso-offtarget-tfge4n3-deep500-b2.json truncated  rc 1  DETECTED
```

**The exon-2 lane guard, full bracket** (`/tmp/claude-0/w03e/tree2`, Ensembl retry lines elided):

```
$ python3 research/modalities/aso_noncoding_acceptor_screened_table.py --check          # BASELINE
non-canonical screened table --check: OK (4 junctions, 5/5 screens)
EXIT=0     ; files opened for write under research/: []   ; files modified: []

$ # truncate research/modalities/noncoding-acceptor/junction-aso-offtarget-e7n2-deep500.json
truncated 533110 -> 319866
$ python3 research/modalities/aso_noncoding_acceptor_screened_table.py --check
seam grade ['UNGRADEABLE'] on ['junction-aso-offtarget-e7n2-deep500.json'] — refusing to publish a
table over an artifact whose acceptor seam the corrected transcript model does not produce.
TRUNC_EXIT=1
--- other files modified under research during --check: ---
(none listed above = --check wrote nothing)

$ # restore
non-canonical screened table --check: OK (4 junctions, 5/5 screens)
RESTORED_EXIT=0
```

An earlier, weaker degradation of the same guard — dropping one element from the 231-pair list in `nr4a3-fusion-junction-atlas-noncoding-acceptor.json` — returned **exit 0**. I am **not** counting that as a miss: the table has 4 junctions and I did not prove that pair material, so it is recorded as **immaterial/inconclusive**, not as a fake guard.

**The fake guard, unrepaired** (`/tmp/claude-0/w03e/tree0`):

```
$ python3 research/manuscripts/submission_citations.py --check            # pristine
74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
  citation numbering is current
EXIT=0

$ # perturb the COMMITTED artifact this chain step produces: n_references 53 -> 60
$ python3 research/manuscripts/submission_citations.py --check
74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
  citation numbering is current
EXIT=0                                    <- SILENT PASS over a corrupted committed artifact
$ python3 -c "import json;print(json.load(open(REFS))['n_references'])"
60                                        <- and --check did NOT rewrite it (silent-pass class)
```

and with the research article truncated to 60 %, from the battery record:

```
"check_rc": 0,
"write_rc_on_degraded": 0,
"write_path_output_changed": ["…/fusion-junction-aso-submission-references.json",
                              "…/fusion-junction-aso-submission-references.md"],
"verdict": "NOT DETECTED (returned 0 on a truncated input it reads; write path rc=0, outputs changed=True)"
```

**The repaired guard** (`/tmp/claude-0/w03e/tree1`, patch above applied to the scratch copy only):

```
=== T1 repaired --check, pristine (expect 0) ===
  citation numbering is current
T1_EXIT=0
=== T2 repaired --check, research article truncated to 60% (expect 1) ===
51 annotated citation(s), 39 distinct PMID(s), …
citation artifacts are stale: fusion-junction-aso-submission-references.md, fusion-junction-aso-submission-references.json -- re-run with --write
T2_EXIT=1
=== T3 NEGATIVE CONTROL: article restored, committed references.json perturbed (expect 1) ===
74 annotated citation(s), 53 distinct PMID(s), …
citation artifacts are stale: fusion-junction-aso-submission-references.json -- re-run with --write
T3_EXIT=1
=== T4 restore everything (expect 0) ===
  citation numbering is current
T4_EXIT=0
=== T5 repaired --write reproduces the committed bytes ===
  wrote fusion-junction-aso-submission-references.md and fusion-junction-aso-submission-references.json
WRITE_EXIT=0
research/manuscripts/aso/fusion-junction-aso-submission-references.md: OK
research/manuscripts/aso/fusion-junction-aso-submission-references.json: OK
SHA_CHECK=0 ; MATCHES_PRISTINE
```

**Real tree untouched:**

```
$ git status --porcelain      # start
(empty)
$ git rev-parse HEAD          # start
3f5fc95d806765b8fddf4fbe1dc288c85869fa2d
$ git status --porcelain      # end
(empty)
$ git rev-parse HEAD          # end
c81236b90c7905caa2e75a57b332ad33f2c10d02
$ date -u
Tue Sep  8 03:17:38 UTC 2026
```

**PROPOSED (NOT RUN):** `scripts/preflight.sh`; `PREFLIGHT_FULL=1`; any repository test suite (I ran **no** pytest in this task); `regenerate_aso_chain.sh --check` end to end; applying either the `submission_citations.py` repair or the one-string chain wiring to the real tree; probing generators 16, 18 and 19; any network retrieval.

## Limitations

- **The "fake" verdict rests on one generator and one degradation class each.** I ran at most three candidate inputs per generator, with truncation as the decisive variant, and I stopped at the first detection. A guard I graded REAL is proven to detect *the degradation I applied*, not every degradation. W03d's 8-way battery on `aso_per_junction_table` is the deeper standard; nothing here matches its depth.
- **Truncation is a loud degradation.** Eight of the twelve REAL verdicts were reached by truncation, which usually surfaces as a parse error rather than as a semantic comparison. A guard that catches a truncated input has not thereby been shown to catch a semantically valid but scientifically wrong one. Where I tried semantic degradations first (drop a row, mutate a string, perturb an integer) they were frequently **immaterial** — the write path reproduced identical outputs — which is a legitimate result about the input's blast radius, not evidence about the guard.
- **Three generators are UNKNOWN, and one of them is in the exon-2 lane.** `aso_noncoding_acceptor_designs.py` timed out on Ensembl retries and was never probed. `aso_coverage_ladder.py` failed to import under my `runpy`-based tracer (`ModuleNotFoundError: aso_reagent_coverage`) — that is my harness's `sys.path`, not a repository defect, and I say so rather than filing it as a finding. `aso_priorart_evidence.py` honestly refuses without `origin/literature-cache`. A missing measurement is UNKNOWN, not a pass and not a failure.
- **Two guards have a red baseline** (`aso_archive_manifest.py`, `aso_deposit_drift.py`). The archive manifest's own source documents that it goes red after any commit and must not be gated on; my run reproduces that state, and a guard whose baseline is already 1 cannot demonstrate discrimination against a degradation. Their real/fake status is **not established** by this work.
- **The `--check`-writes detector is mtime + write-mode `open`, not `git status`.** The scratch copies have no `.git`, so a per-`--check` `git status` was impossible there; I ran it on the real tree at start and end only. A generator that wrote a file with identical bytes *and* an unchanged mtime would evade my detector — I consider that remote, but it is not excluded.
- **HEAD moved four times during the run** (`3f5fc95d` → `98a0833` → `c81236b`, coordinator commits). My copy is `3f5fc95d`; results are valid for that commit.
- **This is test-harness bookkeeping, not science.** No clinical claim follows from any of it. A sequence design is not evidence of efficacy, safety, selectivity or a therapeutic window; there is no wet lab; I designed and modified no oligonucleotide. Nothing here changes any scientific conclusion, any pinned quantity, or the standing of W03b's ALREADY-KNOWN verdict.
- **I weakened no guard and repaired none by loosening it.** The one repair adds a comparison and removes nothing, and it was applied only to a scratch copy.

## Stop condition

Set up front by dispatch: **the tally — how many chain guards are real, how many fake, with the smallest correct repair and a negative control for each fake one, plus an explicit answer on exon-2 protection.**

**MET, on every count:**
- **Tally** — 19 verification paths enumerated with `file:line`; 13 REAL, **1 FAKE**, 0 of the serious rewrite class, 2 red-baseline, 3 UNKNOWN (R1, R2).
- **Fake-guard repair** — `submission_citations.py:460`, mechanism traced to source, smallest correct repair returned **inline and not written into the tree** (R3).
- **Negative control** — T3: the repaired guard returns 1 on a perturbed committed artifact and names only that file, where the shipped guard returns 0 on the identical perturbation (measured both ways). T1/T4 green brackets and T5 byte-identical write path.
- **Two fake-guard classes distinguished, with the detector run before and after every `--check`** — zero of 18 generators wrote anything during `--check`; the serious class W14b catalogued is **absent from this chain**.
- **Exon-2** — answered explicitly in R5: protected by `aso_noncoding_acceptor_screened_table.py --check`, which is real and fires on the `e7n2` screen; **not** protected by the chain script, which is wired with an empty check-command for that step.
- **W03c and W03d reused as inputs, not re-run** — stated, and their results carried into row 1 of R1 with attribution.

## Tool-call and wall-clock count actually used

**95 tool calls.** Wall clock `02:50:42Z` → `03:17:38Z` = **26 min 56 s**. Inside the ~40-minute target; **over the ~40-call target by roughly 2.4×**, and the overrun is honestly attributable to me: three harness restarts (a `re.sub` escape bug, a `pkill -f` pattern that killed my own patch script twice) and — as the coordinator's mid-run instruction correctly identified — several redundant wait-only pollers on one file. I have since stopped every extra waiter and monitor; nothing of mine is left running. The two real computations the coordinator preserved both completed and are reported above.

## Next concrete action

**One specific successor, and it is smaller than this task was.** `regenerate_aso_chain.sh` declares three producers to have "no `--check` mode" when all three have a working one measured REAL here — `aso_per_junction_table.py` (`:264`), `offtarget_chance_baseline.py` (`:249`), `aso_noncoding_acceptor_screened_table.py` (`:265`). The successor is to **run the chain's own `--check` end to end on a scratch copy with those three check-commands filled in, and report whether the chain still exits 0 and what its `CANNOT VOUCH FOR` list shrinks to** — a strict tightening, no guard weakened, and it converts three unrun real guards into enforced ones for the deposit path of the programme's first manuscript. It needs the PUB-ASO owner's sign-off because it changes what the chain gates on, and because `aso_noncoding_acceptor_screened_table.py --check` takes minutes offline (R6), which is a wiring cost the owner should price. **I did not make that change.**

The `submission_citations.py` repair in R3 is ready to apply and proven to discriminate, but it edits a generator inside the PUB-ASO package: it belongs to the paper owner, and it should land with the chain-wiring decision rather than separately.
