> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W20f** · lane 20 refill · OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 02:46:06 UTC 2026` · `date -u` **end**: `Tue Sep  8 02:48:37 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start run; the four long proxy lines — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are retained verbatim in the transcript and contain no model information; they are elided here as `...`):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=... (proxy list, no model information)
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
GLOBAL_AGENT_NO_PROXY=... (proxy list, no model information)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=... (truststore + proxy settings, no model information)
NO_PROXY=... (proxy list, no model information)
npm_config_noproxy=... (proxy list, no model information)
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

**HEAD actually read: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`** at start and unchanged at end. This is not the brief's frozen `92abbcb90…` nor W20e's `d3e9c4d8…`; the checkout keeps moving under the coordinator's own report-collection commits. **`git status --porcelain` returned 0 lines at start and 0 lines at end — the working tree was never written.** All execution under `/tmp/claude-0/w20f/`. **No network request of any kind was made**; the Ensembl fetch was not attempted, probed, or routed around.

---

## Question

**How many distinct sequences does the probe→gene matcher's intersection filter exclude, at every candidate threshold — and what is the smallest correct change to that filter?**

Open because W20e closed the EWSR1 endpoint (NULL under all three zero-handlings) and named this as the successor: the size of the loss was never measured, and the repair was described but never written. W20d diagnosed the mechanism by hand on three genes; nobody counted it.

---

## Prior-work check

| Command | What it showed |
|---|---|
| `grep -n "common_to_every\|intersection\|set.intersection\|n_probes_offered\|gene_of\|probes_common" research/modalities/emc_fourth_cohort_quant.py` | The filter is at **718–724**, not 583. Nine hit lines, all read. |
| `grep -n "save_inputs(" …quant.py` and `grep -n "gene_of\|GENE_TSV" …quant.py` | Traced the full consumer chain from the filter to both committed TSVs. |
| Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W20e-ewsr1-probe-endpoint.md`, `reports/W20d-probe-power-audit.md` §Question–§Result-4 | W20e's §Next-concrete-action specifies exactly this task and forbids two things I did not do. |

**Confirmed not replayed.** I did **not** re-run W20e's EWSR1 endpoint, and I computed **no** δ, p-value or panel percentile on any re-derived panel — that is the post-hoc iteration W20d refused. No PUB-EMC-CLASSIFICATION, no Brenca, no Hofvander/EGA, no GSE4303/GSE28866, no NR4A Perspective. No reagent designed. **No network request**; the vendor TempO-Seq manifest and the Ensembl FASTA both remain honest unrecovered sources. I hit no content-policy refusal.

---

## Method / inputs

| Input | Path (repo HEAD `3f5fc95d`) | Use |
|---|---|---|
| Sequence × run counts | `research/modalities/emc-fourth-cohort-probe-counts.tsv` | 213,007 rows × 12 run columns — the entire persistence histogram |
| Transcript models | `research/modalities/emc-construct-inputs.json` → `genes.{EWSR1,TAF15,FUS,TCF12,TFG,NR4A3,PGR}.{cdna,cds}` | offline identification, 7 genes × 2 fields |
| The filter and its consumers | `research/modalities/emc_fourth_cohort_quant.py:367–391, 394–459, 462–502, 570–589, 711–733, 739–840` | code reading; memory model re-implemented from `_core_sets` verbatim |

**Tools:** Python 3.11.15, standard library only. No third-party package, no network, no GPU, no paid API. Scripts at `/tmp/claude-0/w20f/{hist.py,genes.py,singletons.py,mem.py}`.

**Operational definition used throughout, stated because it is load-bearing:** "present in run *r*" = a **non-zero** count in that run's column. This is exactly the code's own definition — `_read_probe_tsv` (`:558–566`) only inserts a key `if n:`, so a zero cell is a *missing key*, and the intersection at `:723` operates on those key sets. A zero therefore means **"not among the counts persisted for that run"**, which the module itself (`:821–823`) says "**is not a measurement of zero reads**". Every count below is a count of persistence, not of biological presence.

---

## Result

### 1. The filter, its variables, and its consumers — exact `file:line`

All in `research/modalities/emc_fourth_cohort_quant.py`.

**Correction to the dispatch, stated up front.** The dispatch (inheriting W20d and W20e) cites `:583` as the filter. At this HEAD `:583` is the **opposite** operation — the *union* in `_write_probe_tsv`:

```python
583:    probes = sorted(set().union(*[set(runs[a]["counts"]) for a in accs]))
```

That union is why the committed TSV has all 213,007 rows and why this measurement was possible at all. **The actual filter is `phase_map`, lines 718–724:**

```python
711: def phase_map(budget_s: float, min_runs: int = 2) -> dict:
712:     """Probe -> gene, from the probes the runs actually carry."""
713:     cache = load_inputs()
714:     runs = {k: v for k, v in cache.get("runs", {}).items() if v.get("counts")}
...
718:     # a probe is a sequence retained in EVERY run that was read — the intersection is the
719:     # conservative set, and its size is reported beside the per-run counts.
720:     seqs = None
721:     for v in runs.values():
722:         s = set(v["counts"])
723:         seqs = s if seqs is None else (seqs & s)
724:     probes = sorted(seqs or [])
725:     read_len = max((v.get("modal_read_length_nt") or 0) for v in runs.values())
726:     res = map_probes_to_genes(probes, read_len, budget_s=budget_s)
727:     res["n_probes_in_every_read_run"] = len(probes)
```

What each variable holds, precisely:

| Variable | Line | Set it holds | Measured size |
|---|---|---|---|
| `runs` | 713 | the read runs — cache entries carrying a `counts` dict | **12** (SRR35940646–657) |
| `s` | 722 | one run's **persisted** sequences (non-zero cells only) | per-run, 12 sets |
| `seqs` | 723 | **∩ of all twelve** — sequences persisted in *every* run | **1,645** |
| `probes` | 724 | `sorted(seqs)`; **the only list ever offered to the matcher** | **1,645** |

**Consumers of `probes`, i.e. everything the filter silently controls:**

- `:726` `map_probes_to_genes(probes, …)` — the matcher. `:447` records `"n_probes_offered": len(probes)`; `:450` computes `n_probes_unassigned = len(probes) − unique − multi` **over the offered set only**.
- `:456` `"probe_to_gene": unique` → `:729` `cache["probe_map"]` → `:745` `p2g` in `derive()`.
- `:817` `_write_probe_tsv(cache, p2g)` → `:586` `g = (gene_of or {}).get(pr) or "unassigned"`. **This is the conflation.** The TSV is written over the 213,007-row *union*, but labelled from a map built over the 1,645-row *intersection*, so one string `unassigned` covers two disjoint populations: **662 offered-and-unmatched** and **211,362 never-offered**.
- `:767–773` `gene_counts` — sums per-run counts only where `p2g.get(seq)` is not None. A never-offered sequence contributes **nothing** to `emc-fourth-cohort-gene-counts.tsv`, which is why 862 genes appear and EWSR1 does not.
- `:775, :802` `n_probes_common_to_every_read_run` in the published JSON; `:940` treats it as a drift key.

### 2. The persistence histogram — a real count over all 213,007 committed rows

`PRIMARY` (a computation over committed data; RUN, exit 0). "Excluded" = 213,007 − (number present in ≥ k runs), i.e. the sequences the filter withholds from the matcher at that threshold.

| k | present in **exactly** k runs | present in **≥ k** runs (= offered) | **excluded** at ≥ k | % of table excluded | rows carrying a real `assigned_gene` |
|---|---|---|---|---|---|
| 1 | 162,981 | **213,007** | **0** | 0.00 % | 0 |
| 2 | 17,404 | 50,026 | 162,981 | 76.51 % | 0 |
| 3 | 8,246 | 32,622 | 180,385 | 84.69 % | 0 |
| 4 | 4,103 | 24,376 | 188,631 | 88.56 % | 0 |
| 5 | 4,051 | 20,273 | 192,734 | 90.48 % | 0 |
| 6 | 2,668 | 16,222 | 196,785 | 92.38 % | 0 |
| 7 | 2,644 | 13,554 | 199,453 | 93.64 % | 0 |
| 8 | 2,561 | 10,910 | 202,097 | 94.88 % | 0 |
| 9 | 2,493 | 8,349 | 204,658 | 96.08 % | 0 |
| 10 | 2,217 | 5,856 | 207,151 | 97.25 % | 0 |
| 11 | 1,994 | 3,639 | 209,368 | 98.29 % | 0 |
| **12 (current)** | **1,645** | **1,645** | **211,362** | **99.23 %** | **906** |

**The current "every run" set is 1,645**, reproducing the committed `n_probes_common_to_every_read_run: 1645` exactly. **The filter excludes 211,362 of 213,007 distinct sequences — 99.23 % of the table — from ever being shown to the matcher.** Every one of the 906 rows in the TSV that carries a gene label sits in the k = 12 bucket, and none sits anywhere else: independent confirmation that the map covers the intersection and nothing else.

The single largest step is between k = 12 and k = 11: **1,994 sequences** are excluded solely for failing to persist in one run out of twelve. The two runs doing most of that work are the two smallest libraries, SRR35940651 and SRR35940652 (164,967 and 140,423 panel reads — W20e).

### 3. The seven named genes — which the filter excludes, and at what k each is admitted

Method: every 50-mer of each committed `cdna` and `cds` field, both strands, tested for exact membership in the 213,007-sequence set. `PRIMARY` for presence, span and run count; **`UNVERIFIED` for probe identity** (§Limitations).

| Gene | Candidate sequence | Locus (1-based, antisense) | `assigned_gene` in TSV | **k = runs persisted** | Admitted at threshold ≥ k | Excluded by the current filter? |
|---|---|---|---|---|---|---|
| **TAF15** | `CTTCTGTCTCC…CCTCCTCGATC` | cDNA 1617–1666 / CDS 1531–1580 | **TAF15** | **12** | any | **no** |
| **FUS** | `CCGATTAAAGT…GATAGGATTTC` | cDNA 1158–1207 / CDS 1082–1131 | **FUS** | **12** | any | **no** |
| FUS (+1 frame shift) | `CGATTAAAGTC…ATAGGATTTCC` | cDNA 1157–1206 | unassigned | **1** | ≥ 1 only | yes |
| **TCF12** | `CTCACACATCA…ACACTGAAATG` | cDNA 4128–4177 | unassigned | **11** | ≥ 11 | **yes** |
| **TFG** | `GGTGTAGAGGA…GGGTATAGCC` | cDNA 1442–1491 | unassigned | **11** | ≥ 11 | **yes** |
| **EWSR1** | `GCTTGTTTCCA…GCTGCTGCTGC` | cDNA 453–502 / CDS 384–433 | unassigned | **10** | ≥ 10 | **yes** |
| **TCF12** (2nd) | `CCTTCATGGGC…CTGTAATGAGG` | cDNA 523–572 / CDS 238–287 | unassigned | **10** | ≥ 10 | **yes** |
| **NR4A3** | `GGTACACGCAG…GCCCTCCACG` | cDNA 882–931 / CDS 183–232 | unassigned | **9** | ≥ 9 | **yes** |
| **PGR** | — none — | — | — | — | — | **not present at any k** |

`UNKNOWN` for PGR: no 50-mer of the committed PGR cDNA or CDS appears anywhere in the 213,007 sequences. Under this deposit's persistence cap that is **UNKNOWN, not absence** — a PGR probe present below the cap in all twelve runs would look identical.

**The headline of this section is new and it is the driver gene. `NR4A3` — the fusion's 3′ partner in every EMC chimera this repository studies — has a candidate sequence persisting in 9 of 12 runs (counts 65, 141, 0, 144, 87, 0, 209, 161, 108, 396, 0, 417) and is excluded by the current filter.** W20d recovered EWSR1, TCF12 and TFG by hand; NR4A3 was not on that list. It is on this one. Both W20's Limitations ("NR4A3 … absent from this panel") and the mechanism W20d diagnosed extend to it. **This is not an endpoint and I ran no test on it.**

**The minimum threshold that admits all six genes with a candidate sequence is k = 9** (offering 8,349 sequences, 5.1× the current 1,645).

### 4. Is the singleton bulk just sequencing error? Measured, and the answer is "not mostly"

I checked this because the obvious argument for a floor above k = 1 is that the 162,981 singletons are read errors of real probes. `PRIMARY`, RUN, exit 0:

- singletons that are an exact **1-nt frame shift** of a k ≥ 2 sequence: **2,092 / 162,981 (1.3 %)**
- singletons that are an exact 1-nt frame shift of a k = 12 sequence: **300 / 162,981 (0.2 %)**

So frame-shifted duplicates of persisted probes (the FUS +1 row above is one) account for **about one percent** of the singletons. The remaining ~98.7 % are of **UNKNOWN** origin offline — substitution errors, off-panel reads, and genuine low-abundance probes are not separable without the matcher. I report the measurement rather than the assumption I started with.

### 5. What raising k actually costs — measured, not asserted

`_core_sets` (`:367–391`) is where probe count turns into memory: 3 trim lengths × both strands. Re-implemented verbatim and measured with `tracemalloc`. `PRIMARY`, RUN, exit 0:

| threshold | probes offered | core-dict entries | 16-mer prefix-set entries | peak traced memory |
|---|---|---|---|---|
| ≥ 12 (current) | 1,645 | 9,194 | 8,463 | **1.9 MB** |
| ≥ 9 | 8,349 | 46,329 | 41,596 | **8.9 MB** |
| ≥ 2 | 50,026 | 260,701 | 174,908 | **44.3 MB** |
| ≥ 1 (everything) | 213,007 | 1,172,458 | 618,191 | **197.7 MB** |

**Wall time is essentially unaffected by k.** `_scan_seq` (`:491–502`) tests one 16-mer set membership per base per core length; that is O(1) regardless of set size. The only k-dependent work is the full-core slice taken on a prefix hit, whose rate rises from 8,463/4^16 ≈ 2 × 10⁻⁶ to 618,191/4^16 ≈ 1.4 × 10⁻⁴ — a few tens of thousands of extra slices over the whole cDNA+ncRNA set. **The conservative filter was never buying compute. It cost 99.23 % of the table to save under 200 MB.**

### 6. The smallest correct change

The correct repair is **not** simply lowering the constant, because `probes` feeds two jobs with opposite requirements, and the current code conflates them:

- **Identification** (`map_probes_to_genes`, `:726`) asks *which gene is this sequence?* That is a property of the sequence, not of the sample. Cross-run persistence is **irrelevant** to it, and filtering on it is what lost EWSR1 and NR4A3.
- **Quantification** (`gene_counts`, `:767–773`) asks *how many reads?* Conservatism there is legitimate, and lowering the identification threshold silently changes it: any newly-assigned sequence — including the 1-nt-shifted FUS duplicate at k = 1, which would add its 32 reads to FUS in SRR35940648 — starts contributing to `emc-fourth-cohort-gene-counts.tsv`. That would move every committed gene count, and with it the TAF15/FUS values W20 published and W20e gated against.

So the smallest change that is also **correct** decouples the two thresholds and makes the persistence count a recorded datum rather than a discarded one. Returned inline per the write-isolation rule; **not written into the repository.**

```python
# research/modalities/emc_fourth_cohort_quant.py

# --- near the other module constants (with GATE / KEEP_COVERAGE) ------------------
MIN_RUNS_TO_OFFER = 2      # identification: a sequence is OFFERED to the matcher if it persisted
                           # in at least this many read runs. 12 (the old intersection) withheld
                           # 211,362 of 213,007 sequences, including EWSR1, NR4A3, TCF12 and TFG.
MIN_RUNS_TO_QUANTIFY = 12  # quantification: unchanged, so no committed gene count moves.


# --- phase_map, replacing lines 718-733 ------------------------------------------
    # PERSISTENCE, NOT MEMBERSHIP. Cross-run persistence is a property of the SAMPLES, not of the
    # sequence's identity, so it must not gate identification. It is counted, recorded, and then
    # applied where it belongs — at quantification.
    persisted_in = collections.Counter()
    for v in runs.values():
        persisted_in.update(v["counts"])          # a zero cell is an ABSENT KEY, not a zero read
    probes = sorted(s for s, n in persisted_in.items() if n >= MIN_RUNS_TO_OFFER)
    read_len = max((v.get("modal_read_length_nt") or 0) for v in runs.values())
    res = map_probes_to_genes(probes, read_len, budget_s=budget_s)
    res["n_runs_persisted"] = dict(persisted_in)          # ⛔ THE RECORD. Every downstream cut,
                                                          # including the old k=12 set, is
                                                          # reconstructible from this alone.
    res["min_runs_to_offer"] = MIN_RUNS_TO_OFFER
    res["n_probes_in_every_read_run"] = sum(1 for n in persisted_in.values()
                                            if n == len(runs))   # 1645, key preserved for :940
    res["n_runs_intersected"] = len(runs)
    res["⚠ offered_is_not_every_run"] = (
        "n_probes_offered is now the >= MIN_RUNS_TO_OFFER set, not the intersection. "
        "'unassigned' in the probe table still covers sequences BELOW that threshold, which were "
        "never offered and carry no evidence either way.")
    cache["probe_map"] = res
    save_inputs(cache)
    return {"state": res.get("state"), "n_probes": len(probes),
            "assigned": res.get("n_probes_assigned_to_one_gene"),
            "best_core_length_nt": res.get("best_core_length_nt")}


# --- derive(), replacing lines 767-773 -------------------------------------------
    npr = (pmap.get("n_runs_persisted") or {})
    gene_counts: dict[str, dict[str, int]] = {}
    for acc, v in read_runs.items():
        for seq, n in v["counts"].items():
            g = p2g.get(seq)
            if g is None or npr.get(seq, 0) < MIN_RUNS_TO_QUANTIFY:
                continue        # identification is permissive; quantification stays conservative
            gene_counts.setdefault(g, {})[acc] = gene_counts.setdefault(g, {}).get(acc, 0) + n


# --- _write_probe_tsv, replacing lines 584-588 -----------------------------------
    # The TSV now says WHICH KIND of 'unassigned' each row is. One string covered two disjoint
    # populations: 662 offered-and-unmatched, and 211,362 never-offered.
    lines = ["probe_sequence\tassigned_gene\tn_runs_persisted\t"
             + "\t".join(f"{a}:{alias[a]}" for a in accs)]
    for pr in probes:
        g = (gene_of or {}).get(pr) or "unassigned"
        lines.append(pr + "\t" + g + "\t" + str(npr.get(pr, 0)) + "\t"
                     + "\t".join(str(runs[a]["counts"].get(pr, 0)) for a in accs))
```
(`_write_probe_tsv` takes `npr` as a third argument, passed through `save_inputs`/`derive:817`; `import collections` is already available at module scope via `from collections import Counter` or is added.)

**Recommended k = 2, and here is why — including why it is not 12, 9 or 1.**

- **Not 12.** Measured: it withholds 99.23 % of the table and, by construction, cannot recover *any* sequence that dipped below the persistence cap in even one of the two ~150k-read libraries. It excludes EWSR1, NR4A3, TCF12 and TFG.
- **Not 9**, even though 9 is the minimum that admits all six genes I checked. Choosing the threshold *because* it admits the genes I went looking for is threshold-tuning to a target, and the seven genes are not the panel. k = 9 would be a number fitted to this report.
- **Not 1**, though it is affordable (197.7 MB, no time penalty). k = 1 offers 162,981 sequences seen in exactly one run, of which only 1.3 % are identifiable as frame-shift duplicates and the rest are of unknown origin; assigning genes to sequences with no cross-run reproducibility at all puts a large, uncharacterised population into `probe_to_gene`, and the matcher's own `n_probes_unassigned` denominator becomes uninterpretable.
- **k = 2 is the only threshold with a reason that is not the data in front of me.** It is the weakest possible non-trivial claim — *this sequence was seen in more than one library* — and it is exactly the condition `phase_map`'s own `min_runs: int = 2` guard already treats as the minimum for calling something a panel ("a probe set defined by one run is not a panel", `:717`). It admits all six recovered genes with 3–10 runs to spare, offers 50,026 sequences at 44.3 MB, and it draws the line at the single sharpest discontinuity in the histogram: 162,981 singletons collapsing to 17,404 doubletons, a 9.4× drop, with the decay from k = 2 to k = 12 smooth by comparison. It is a principled floor, not a fitted one.

**Executing the matcher here is impossible.** `map_probes_to_genes` reaches the network at `:410` (`_ensembl_fasta_url` → `http_get` on the Ensembl FASTA directory listing) and `:469` (`urllib.request.urlopen` on the `.fa.gz`). This worker has no network of any kind and did not attempt, probe, or route around it. **Therefore: the number of genes actually recovered at k = 2 is `PROPOSED (NOT RUN)` and remains `UNKNOWN`.** It is ≥ 4 more than the current 862 if the four candidate sequences above are what they appear to be, and could be substantially larger — the offered set grows 30×. I am not estimating it.

---

## Validation evidence

**RUN.** Environment: Python 3.11.15, stdlib only; container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`; repo HEAD `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`; `git status --porcelain` → 0 lines at start and end.

```
$ python3 /tmp/claude-0/w20f/hist.py; echo "EXIT=$?"
total distinct sequences: 213007
rows with a non-'unassigned' assigned_gene: 906
 k   n_seq_with_exactly_k   n_seq_present_in_>=k   excluded_by_>=k(vs union)  assigned_exactly_k
 1      162,981                213,007                        0                  0
 2       17,404                 50,026                  162,981                  0
 ...
12        1,645                  1,645                  211,362                906
k=12 ('present in EVERY run') = 1645
EXIT=0

$ python3 /tmp/claude-0/w20f/genes.py; echo "EXIT=$?"
seq length 50 n rows 213007
EWSR1.cdna antisense 453-502/2400; EWSR1.cds antisense 384-433/1971  assigned=unassigned  k=10
FUS.cdna antisense 1157-1206/1824                                    assigned=unassigned  k=1
FUS.cdna antisense 1158-1207/1824                                    assigned=FUS         k=12
NR4A3.cdna antisense 882-931/5604; NR4A3.cds antisense 183-232/1881  assigned=unassigned  k=9
TAF15.cdna antisense 1617-1666/2162                                  assigned=TAF15       k=12
TCF12.cdna antisense 523-572/6114                                    assigned=unassigned  k=10
TCF12.cdna antisense 4128-4177/6114                                  assigned=unassigned  k=11
TFG.cdna antisense 1442-1491/1907                                    assigned=unassigned  k=11
genes with ZERO: ['PGR']
EXIT=0

$ python3 /tmp/claude-0/w20f/singletons.py; echo "EXIT=$?"
singletons that are an exact 1-nt frame shift of a k>=2 sequence: 2,092 / 162,981 (1.3%)
singletons that are an exact 1-nt frame shift of a k==12 sequence: 300 / 162,981 (0.2%)
EXIT=0

$ python3 /tmp/claude-0/w20f/mem.py; echo "EXIT=$?"
k>=12  probes=  1,645  core-dict entries=    9,194  prefix-set entries=  8,463  peak_traced=   1.9 MB
k>= 9  probes=  8,349  core-dict entries=   46,329  prefix-set entries= 41,596  peak_traced=   8.9 MB
k>= 2  probes= 50,026  core-dict entries=  260,701  prefix-set entries=174,908  peak_traced=  44.3 MB
k>= 1  probes=213,007  core-dict entries=1,172,458  prefix-set entries=618,191  peak_traced= 197.7 MB
EXIT=0
```

Two independent cross-checks passed: the k = 12 bucket size **1,645** equals the committed `n_probes_common_to_every_read_run`, and W20d/W20e's EWSR1, TCF12 and TFG spans and counts reproduce exactly from an independently written script.

**PROPOSED (NOT RUN):** executing `phase_map` with the patch (needs the Ensembl fetch — not attempted); the resulting count of genes recovered at k = 2; `scripts/preflight.sh` (nothing in the tree was changed and the dispatch did not authorise it); any statistical endpoint on a re-derived panel (explicitly out of scope and refused).

---

## Limitations

- **Nothing was executed against the matcher.** The central deliverable of a filter repair — how many genes come back — is `UNKNOWN`. This report measures the *loss*, not the *recovery*.
- **UNVERIFIED probe identity, carried forward from W20d and W20e unchanged.** An exact unique match to a committed cDNA with real counts is *consistent with* a probe and is *not proof* of one. The vendor manifest is behind a recorded egress denial and was not probed. This applies to the NR4A3 row exactly as it applies to EWSR1.
- **Offline uniqueness could not be checked, exactly as W20e stated. Seven genes is not a transcriptome.** These candidates were tested against 14 committed sequences from 7 genes. The matcher scans the Ensembl cDNA + ncRNA set, which is not in the repository, not in the frozen corpus, and not reachable here. A second genomic locus carrying any of these 50-mers would not have been detected and would break the gene attribution.
- **"Present" means "persisted", never "expressed".** Every k in this report counts runs where the sequence survived the lossy-counting persistence cap. A zero is missing data. The histogram is therefore a property of the deposit's *counting*, jointly with library size, not of the tumours.
- **k = 2 is a judgement, argued from a histogram discontinuity and the code's own `min_runs=2` precedent. It is not a validated optimum**, and no threshold was validated by any measurement of matcher output.
- **The patch is unrun code.** It typechecks by eye only; it has not been executed, linted, or put through any test tier. It requires `import collections` and a signature change to `_write_probe_tsv`/`save_inputs` that a real integration must complete.
- **Changing `MIN_RUNS_TO_OFFER` changes `n_probes_offered` and `n_probes_unassigned`**, both of which are published in `emc-fourth-cohort-quant.json` and one of which (`:940`) is a drift key. Any integration must record that the denominators moved.
- **NO CLINICAL CLAIM.** This is a defect measurement in a counting script. It establishes nothing about EMC efficacy, safety, selectivity, therapeutic window, dosing or clinical readiness. No reagent was designed. **Runs are not samples and samples are not people.**

---

## Stop condition

Set up front: *return the moment all four dispatch items are answered from committed data with real exit codes, or as soon as any item is shown to require the network.* **MET in full.**

1. Filter and consumers quoted with exact `file:line`, every variable's set stated — and the dispatch's `:583` citation corrected to `:718–724`. ✓
2. Persistence histogram for k = 1…12 over all 213,007 rows; 1,645 at k = 12 reproduces the committed value; 211,362 excluded (99.23 %). ✓
3. All seven named genes resolved: EWSR1 k = 10, TCF12 k = 10 and 11, TFG k = 11, **NR4A3 k = 9 (new)**, TAF15 and FUS k = 12 (not excluded), PGR absent at every k (UNKNOWN, not absence). Same offline-uniqueness limitation stated as W20e's. ✓
4. Patch returned inline with k = 2 recommended and argued, plus measured memory/time costs; matcher execution marked **PROPOSED (NOT RUN)** because it requires the forbidden Ensembl fetch. ✓

Returning immediately, as instructed. W20e's endpoint was not re-run and no statistic was recomputed on any re-derived panel.

---

## Tool-call and wall-clock count actually used

**14 tool calls** (all `Bash`; 4 of them heredocs that wrote scripts under `/tmp/claude-0/w20f/`). **Wall clock: 2 min 31 s** (02:46:06Z → 02:48:37Z). Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**One successor: run the patched `phase_map` at k = 2 on a GitHub Actions runner and report the count of genes recovered — the one number this report could not produce.**

The repair is now specified, costed (44.3 MB, no measurable time penalty) and non-destructive (`MIN_RUNS_TO_QUANTIFY = 12` leaves every committed gene count byte-identical, so W20's TAF15/FUS values and W20e's gate survive untouched). The only missing ingredient is the Ensembl cDNA + ncRNA fetch, which is a plain unauthenticated HTTP GET of a public FASTA — precisely the class of work the repository's `ci-escape-hatches` skill routes to an Actions runner, and it needs no paid API, no GPU and no new external act. The deliverable is a single figure — genes with ≥ 1 assigned probe at k = 2 versus the current 862 — plus the corrected `n_probes_offered` / `n_probes_unassigned` denominators, and a `n_runs_persisted` column in the probe TSV that makes every future threshold reconstructible without re-running anything.

Two constraints that successor must carry. It must **not** run any statistical endpoint on the re-derived panel — the EWSR1 question is closed at NULL and re-testing it on a panel rebuilt after the fact is the post-hoc iteration W20d refused and W20e forbade. And it must keep the NR4A3 candidate labelled **UNVERIFIED as to probe identity**; recovering a sequence into the map is an identification by the matcher, not a confirmation that the vendor panel contains an NR4A3 probe, and the vendor manifest remains an honest unrecovered source behind a recorded egress denial.

A smaller item for whoever owns the report files: W20's Limitations sentence listing NR4A3 among genes "absent from this panel" should join EWSR1, TCF12 and TFG in W20d's correction — the committed data contain a candidate NR4A3 sequence persisting in 9 of 12 runs, and the absence is attributable to the filter, not to the panel.
