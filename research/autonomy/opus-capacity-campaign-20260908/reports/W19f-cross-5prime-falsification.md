> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Report follows.

---

## Worker

**Worker ID:** W19f · lane 19 refill · OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (proxy-plumbing lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` matched the grep, are verbatim in the tool log, and are elided here for length — they contain nothing model-relevant):

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

`date -u` at start: `Tue Sep  8 02:47:51 UTC 2026` · at end: `Tue Sep  8 02:51:29 UTC 2026`.

**Repository state.** `git rev-parse HEAD` = `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` at start **and** at end (unchanged during my run; this is not the frozen campaign commit `92abbcb…` — the coordinator has been committing sibling reports, which I did not do). `git status --porcelain` was **empty at start and empty at end**. Every file I created lives under `/tmp/claude-0/w19f/` (`substrate.py`, `gate0.py`, `samefam.py`, `diag.py`). **I wrote nothing into `/home/user/Rare-cancers` and performed no git write of any kind.**

**Network.** The only network calls were PubMed MCP metadata lookups (permitted by my dispatch). **I did not probe, retry, or seek another host for the GSE243553 genome-wide `MOESM3_ESM.zip`** — that route stands as a recorded 403 CONNECT policy denial. **I hit no content-policy refusal.**

---

## Question

**W19e pre-declared this class before seeing my Jaccards, and I ran it:**

> Do fusion pairs whose 3′ partners belong to the **same sourced DNA-binding-domain family**, are **different genes**, and whose **5′ partners also differ** (`SAMEFAM-DIFFGENE-DIFF5′`) still show elevated peak-location similarity?

It is open because W19e's own same-family result (n = 15, mean residual +0.1607, p at the 50,000-draw floor) is confounded twice over: 14/15 of its pairs are ETS, and 7/15 share EWSR1 as their 5′ partner. If the effect is really "EWSR1 fusions resemble each other", deleting every shared-5′ pair should destroy it. This is the sharpest discriminator the panel affords between *"the 3′ DBD family predicts location"* and *"EWSR1 fusions simply resemble each other"*.

---

## Prior-work check

```
rg -n -i "SAMEFAM|DIFF5|same.{0,3}family|DBD family" --glob '!.git' -l
```
→ 20 files. The **only** one that is about 3′-partner DBD families in this panel is
`research/autonomy/opus-capacity-campaign-20260908/reports/W19d-within-ewsr1-permutation.md`; every other hit is degrader/route/manuscript text using "family" in an unrelated sense.

```
git ls-files | rg -i "dbd|domain.family|ets.family"
```
→ 1 path, `systems/views/L2-rt-dbd.md` — a generated RT view, not a peakset analysis.

```
rg -n -i "ETS family|winged.helix.turn.helix|bZIP" --glob '!.git' -l
```
→ `STRATEGY.md` and MM-GBSA lock files under `results/nr4a3-*`. Nothing peakset-related.

Reading W19d's §"post-hoc" block confirms the boundary: W19d observed that the five highest within-EWSR1 Jaccards all pair same-DBD-family 3′ partners, computed a **descriptive** n = 7 mean residual (+0.2043), and explicitly stated *"this was chosen after looking at the data, so no p-value is computed and none may be quoted."* **No DBD-family class has ever been tested anywhere in this repository.** My class is additionally distinct from W19d's: W19d's n = 7 block is entirely *within*-EWSR1, i.e. exactly the shared-5′ pairs my class **excludes**.

**Closed items confirmed not replayed** (`CLOSED-WORK.md`, item by item): no clinical, registry, methylation, promoter-transfer, inverse-bound, Hofvander/EGA, Brenca, GSE4303/GSE28866, pazopanib/anthracycline/sunitinib/trabectedin/Wagner/CTARC or SEER material is touched; no cohort is invented; lane 11 source-index work is untouched; the restricted NR4A Perspective review is not recreated under any label. **I did not re-run W19e's own `SAMEFAM-DIFFGENE` class** — I report its census counts only, as a reconciliation check, and label it as not re-tested.

---

## Method / inputs

**Inputs — both committed, both read-only, read from the live checkout at HEAD `3f5fc95d`:**

| Input | Path | Field used |
|---|---|---|
| Coordinate prefixes | `research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` |
| Peak counts | `research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory[*].n_intervals` |

Deposit **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`; 128 fusion oncoproteins in one HEK293T background; assembly hg38. **These are the authors' own marker calls — this repository called no peak.**

**Tools:** Python 3.11.15, standard library only (`json`, `itertools`, `math`, `random`, `statistics`). No third-party package, no GPU, no paid API, $0 spend.

**Substrate rebuilt independently** (I re-parsed both JSONs from scratch in `/tmp/claude-0/w19f/substrate.py`; I did not import W19c's or W19d's objects): 32 real `Supp_Data_1_new/*_markers.bed` prefixes, trailing partial line discarded, `chr1` records only, `W(A,B) = min(last retained chr1 end)`, Jaccard on **exact interval identity** inside `chr1:0–W`, pair **non-degenerate** iff both sides hold ≥ 1 interval in the window. Density residual `r = J − mean(J in the pair's |Δlog₁₀ n_intervals| quintile)`, quintiles formed over the **376 full-panel non-degenerate pairs**.

**3′ DBD family assignments — sourced by me, not inherited.** According to PubMed:

| Family | Genes assigned | Sourcing statement | Citation |
|---|---|---|---|
| **ETS** | ERG, FLI1, FEV | verbatim: *"ERG family proteins (ERG, FLI1 and FEV) are a subfamily of ETS transcription factors"* | Saulnier et al., *Nucleic Acids Res* 2021, PMID 34009296, [DOI](https://doi.org/10.1093/nar/gkab305) |
| **ETS** | ETV1, ETV4 | verbatim: *"The PEA3 subfamily is a subgroup of the E26 transformation-specific (ETS) family. Its members, ETV1, ETV4, and ETV5…"* | Qi et al., *Am J Cancer Res* 2020, PMID 33163259 (PMC7642666); no DOI in the record |
| **CREB** | ATF1, CREB1 | verbatim: *"members of the cAMP response element binding protein (CREB) family (ATF1 and CREB1)"*; also lists CREM | Kao et al., *Am J Surg Pathol* 2017, PMID 28009602, [DOI](https://doi.org/10.1097/PAS.0000000000000788) |
| **CREB** | corroboration | AMPK *"phosphorylated CREB1… ATF1… CREM"* as "transcription factors of the CREB family" | Thomson et al., *J Appl Physiol* 2007, PMID 18063805, [DOI](https://doi.org/10.1152/japplphysiol.00900.2007) |

**Every other 3′ partner in the panel is UNKNOWN and never matches another UNKNOWN** — GLI1, HNF4A, RET, PHF1, NTRK3, DDIT3, NFATC2, NR4A3, PBX1, POU5F1, SP3, YY1, TACC3, NCOA2, CDX1, FOXO1, SSX1, NTRK1. **DDIT3 is not inherited into any family.** "Has no DBD" was never used as a family.

**Pre-declared class (from W19e's preregistration, encoded in my script docstring before execution):**
`SAMEFAM-DIFFGENE-DIFF5′` = same sourced 3′ family ∧ different 3′ **gene** ∧ different 5′ **partner**.

**Null (fixed before running):** whole-name shuffle of the 32 `(5′, 3′)` labels across the 32 fixed peaksets, 50,000 draws, seed `20260908`, one-sided high, `p = (1 + #{perm ≥ obs}) / (1 + n_perm)`. Floor `n ≥ 4` to test. Floor p reported as `< 2.1e-5`, never as a value.

---

## Result

### Gate 0 — ARM 1 reproduced digit-for-digit, no discrepancy (PRIMARY)

| Quantity | W19f (this run) | Published ARM 1 | Match |
|---|---|---|---|
| Real BED peaksets | 32 | 32 | ✔ |
| All pairs / non-degenerate | 496 / **376** | 496 / 376 | ✔ |
| Density quintile mean J | 0.0387 / 0.0163 / 0.0126 / 0.0110 / 0.0014 | same | ✔ |
| SHARES-3 n · mean J · **mean residual** | 10 · 0.1715 · **+0.1513** | 10 · 0.1715 · +0.1513 | ✔ |
| SHARES-3 permutation p | **0.00008** | 0.00008 | ✔ |
| SHARES-5 n · **mean residual** | 66 · **+0.0094** | 66 · +0.0094 | ✔ |
| SHARES-5 permutation p | **0.09782** | 0.09782 | ✔ |
| SHARES-NEITHER n · mean residual | 300 · −0.0071 | 300 · −0.0071 | ✔ |

**No discrepancy on any deterministic quantity.** Both p-values also landed identically, which is expected here because I used the same seed and the same draw order, not evidence about Monte-Carlo stability; W19e's diagnosis that the SHARES-5 p carries seed spread ≈ 0.095 ± 0.002 is untouched by this and I did not treat it as a defect.

### Census — W19e's transferred counts reproduce exactly (SECONDARY figures, PRIMARY reproduction)

| Quantity | W19f | Transferred from W19e |
|---|---|---|
| `SAMEFAM-DIFFGENE` non-degenerate pairs | **15** | 15 |
| … of which ETS | **14** | 14 |
| … of which share EWSR1 as 5′ | **7** | 7 |

I did **not** re-run W19e's test statistic on this class; this is a membership census only.

### The pre-declared class — SAMEFAM-DIFFGENE-DIFF5′, n = 8 (PRIMARY)

Member pairs, all eight, with the residual actually used:

| Pair | Family | J | **residual r** | n_intervals |
|---|---|---|---|---|
| EWSR1-FLI1 · FUS-FEV | ETS | 0.2973 | **+0.2586** | 2676 / 3728 |
| EWSR1-ETV1 · FUS-FEV | ETS | 0.2571 | **+0.2185** | 5121 / 3728 |
| EWSR1-ETV4 · FUS-FEV | ETS | 0.1892 | **+0.1505** | 5805 / 3728 |
| FUS-FEV · TMPRSS2-ERG | ETS | 0.1463 | **+0.1077** | 3728 / 2527 |
| EWSR1-ETV1 · TMPRSS2-ERG | ETS | 0.1081 | **+0.0918** | 5121 / 2527 |
| EWSR1-FLI1 · TMPRSS2-ERG | ETS | 0.0930 | **+0.0544** | 2676 / 2527 |
| EWSR1-ETV4 · TMPRSS2-ERG | ETS | 0.0789 | **+0.0627** | 5805 / 2527 |
| EWSR1-FEV · TMPRSS2-ERG | ETS | 0.0750 | **+0.0363** | 2658 / 2527 |

| Statistic | Value | Row type |
|---|---|---|
| n (non-degenerate) | **8** — clears the n ≥ 4 floor | PRIMARY |
| mean J | 0.1556 | PRIMARY |
| **mean density residual** | **+0.1226** | PRIMARY |
| whole-name permutation null mean · sd | −0.0004 · 0.0206 | PRIMARY |
| **one-sided high p (50,000 draws, seed 20260908)** | **0.00084** | PRIMARY |
| Verdict (script-emitted) | **PREDICTS LOCATION** | PRIMARY |
| SHARES-NEITHER reference mean residual | −0.0071 | PRIMARY |
| All eight residuals positive | **True** (min +0.0363, max +0.2586) | PRIMARY |
| Leave-one-out means | +0.1031 … +0.1349 (all eight) | PRIMARY |

Units: Jaccard is dimensionless over the pair-specific `chr1:0–W` window. Uncertainty is the 50,000-draw whole-name permutation distribution over these same 32 peaksets and extends no further. The p did **not** land at the Monte-Carlo floor (42 of 50,000 draws ≥ observed), so it is quoted as a value, not as `< 2.1e-5`.

### Why the class is 8 and not 9 — the one point where I had to check the transferred figure

By the class definition plus my sourced families, **nine** candidate pairs exist: the eight ETS pairs above, plus one CREB pair, `EWSR1-CREB1 · FUS-ATF1` (different family gene, different 5′). That pair is **excluded by the non-degeneracy rule, not by family assignment**, and the reason is purely geometric:

```
last retained chr1 end: EWSR1-CREB1 = 14,540,695   FUS-ATF1 = 225,243,066  -> W = 14,540,695
intervals with end <= W: EWSR1-CREB1 = 27          FUS-ATF1 = 0
first interval of FUS-ATF1 = (17,536,323, 17,536,823)
```
`FUS-ATF1`'s truncated prefix does not begin until 17.5 Mb, past the 14.5 Mb window ceiling, so it contributes zero intervals. **This is an artefact of the byte-truncated prefix, not biology.** With that pair correctly dropped, my independent count is **exactly the pre-declared 8**, and the ETS-only reconciliation arm returns the identical member set (p = 0.00156 under its own narrower null, same 8 pairs, same +0.1226). **No count discrepancy against the transferred figures survives.**

### 4. Does the effect survive removing shared-5′ pairs? — stated plainly

**Yes.** Every pair sharing a 5′ partner is gone from this class by construction; the class spans three distinct 5′ partners (EWSR1, FUS, TMPRSS2) and five distinct 3′ genes (ERG, ETV1, ETV4, FEV, FLI1). The residual falls from W19e's transferred +0.1607 (n = 15, floor p) to **+0.1226 (n = 8, p = 0.00084)** — a **24 % attenuation**, not a collapse. For scale, the same-3′-gene effect is +0.1513 and the shared-5′ effect is +0.0094 (p ≈ 0.098, not significant); the shared-5′-free family effect sits at **~13× the shared-5′ effect** and at **81 % of the same-3′-gene effect**.

**This is a positive result, and it falsifies the "EWSR1 fusions simply resemble each other" reading of W19e's class** — that reading predicts the effect should vanish once shared-5′ pairs are deleted, and it does not. The association is with the **3′ DBD family**, not with a shared 5′ partner.

**PREDICTION rows: none.** No model output, extrapolation or projection appears in this report.

---

## Validation evidence

All **RUN**. Nothing here is `PROPOSED (NOT RUN)`.

**RUN — command 1** (environment / git / scratch)
```
date -u; env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'
git rev-parse HEAD; git status --porcelain; mkdir -p /tmp/claude-0/w19f
```
→ HEAD `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`, `git status --porcelain` **empty**. **Exit 0.**

**RUN — command 2** (Gate 0)
```
cd /tmp/claude-0/w19f && python3 --version && time python3 gate0.py; echo "EXIT=$?"
```
Environment: Python 3.11.15, stdlib only. Wall `real 0m8.371s`. **`EXIT=0`.** Verbatim tail:
```
all pairs: 496  non-degenerate: 376
density quintiles: Q1=0.0387(n=75) Q2=0.0163(n=75) Q3=0.0126(n=75) Q4=0.0110(n=75) Q5=0.0014(n=76)
  SHARES-3        n= 10 mean J 0.1715 mean residual +0.1513
  SHARES-5        n= 66 mean J 0.0300 mean residual +0.0094
  SHARES-NEITHER  n=300 mean J 0.0077 mean residual -0.0071
GATE0 SHARES-3  n=10 obs residual +0.1513 null mean +0.0000 p=0.00008
GATE0 SHARES-5  n=66 obs residual +0.0094 null mean -0.0000 p=0.09782
```

**RUN — command 3** (the pre-declared test; docstring written before execution)
```
cd /tmp/claude-0/w19f && time python3 samefam.py; echo "EXIT=$?"
```
Wall `real 0m10.818s`. **`EXIT=0`.** Verbatim key lines:
```
CENSUS: SAMEFAM-DIFFGENE (W19e's class, NOT re-tested here) n=15
  of which ETS: 14  CREB: 1
  of which share EWSR1 as 5': 7
=== PRE-DECLARED CLASS: SAMEFAM-DIFFGENE-DIFF5' (ETS+CREB, as sourced) ===
member pairs (non-degenerate): n=8
member pairs excluded as DEGENERATE: 1 [('EWSR1-CREB1', 'FUS-ATF1')]
obs mean J 0.1556   obs mean residual +0.1226   null mean -0.0004   null sd 0.0206
one-sided high p = 0.00084   -> PREDICTS LOCATION
=== RECONCILIATION ARM: same class restricted to ETS only (to match the transferred n=8) ===
member pairs (non-degenerate): n=8
obs mean J 0.1556   obs mean residual +0.1226   null mean -0.0005   null sd 0.0221
one-sided high p = 0.00156   -> PREDICTS LOCATION
```

**RUN — command 4** (degenerate-pair diagnosis and leave-one-out)
```
cd /tmp/claude-0/w19f && python3 diag.py; echo "EXIT=$?"; date -u; git rev-parse HEAD && git status --porcelain | wc -l
```
`diag.py` printed **`EXIT=0`**; the trailing `git rev-parse` in the *same* compound command failed with **exit 128 — `fatal: not a git repository`** because the shell was still in `/tmp/claude-0/w19f`. That is a cwd error in my one-liner, not a repository problem; I re-ran it correctly in command 5. I record the real 128 rather than hiding it. Verbatim `diag.py` output is quoted in §"Why the class is 8" and the leave-one-out row above.

**RUN — command 5** (end state, from the repository root)
```
date -u && git rev-parse HEAD && git status --porcelain && ls /tmp/claude-0/w19f
```
→ `Tue Sep  8 02:51:29 UTC 2026`; HEAD **`3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`** (unchanged); `git status --porcelain` **empty**; four `.py` files, all under `/tmp/claude-0/w19f/`. **Exit 0. No repository file created, modified or deleted.**

### Code (returned inline, not written into the tree)

`/tmp/claude-0/w19f/substrate.py` — independent substrate rebuild:

```python
"""W19f substrate rebuild - independent re-parse. Gate 0 = reproduce ARM 1 published figures."""
import json, itertools, math, random, statistics

REPO="/home/user/Rare-cancers"
sup=json.load(open(REPO+"/research/modalities/gse243553-eno3-overlap-supplement.json"))
fb=sup["contents"]["SPRINGER::3::zip"]["first_bytes"]
inv=json.load(open(REPO+"/research/modalities/gse243553-eno3-overlap.json"))["peakset_inventory"]

real={k:v for k,v in inv.items() if "__MACOSX" not in k and "Supp_Data_1_new/" in k and k.endswith(".bed")}

def parse_prefix(s):
    lines=s.split("\n")
    if not s.endswith("\n"): lines=lines[:-1]   # discard trailing partial line
    out=[]
    for ln in lines:
        p=ln.split("\t")
        if len(p)<3 or p[0]!="chr1": continue   # chr1 only
        try: out.append((int(p[1]),int(p[2])))
        except ValueError: continue
    return out

peaks={}; names=[]
for k,s in fb.items():
    if "__MACOSX" in k or not k.endswith("_markers.bed"): continue
    nm=k.split("/")[-1][:-len("_markers.bed")]
    peaks[nm]=parse_prefix(s); names.append(nm)
names.sort()
nint={k.split("/")[-1][:-len("_markers.bed")]:v["n_intervals"] for k,v in real.items()}
assert set(nint)==set(names)

def jac(a,b):
    A,B=peaks[a],peaks[b]
    if not A or not B: return None
    W=min(A[-1][1],B[-1][1])
    SA={iv for iv in A if iv[1]<=W}; SB={iv for iv in B if iv[1]<=W}
    if not SA or not SB: return None            # non-degenerate iff both hold >=1
    return len(SA&SB)/len(SA|SB)

J={}
for a,b in itertools.combinations(names,2): J[(a,b)]=jac(a,b)
def key(a,b): return (a,b) if (a,b) in J else (b,a)
good=[p for p in J if J[p] is not None]

d={p:abs(math.log10(nint[p[0]])-math.log10(nint[p[1]])) for p in good}
order=sorted(good,key=lambda p:d[p]); q=max(1,len(order)//5); bin_of={}
for i,p in enumerate(order): bin_of[p]=min(4,i//q)
bmean={b:statistics.mean([J[p] for p in good if bin_of[p]==b]) for b in range(5)}
R={p:J[p]-bmean[bin_of[p]] for p in good}

def split(nm):
    i=nm.index("-"); return nm[:i],nm[i+1:]
G={n:split(n) for n in names}
```

`/tmp/claude-0/w19f/samefam.py` — the pre-declared test; its docstring is the preregistration and was written before execution:

```python
"""
W19f - falsification test of the class PRE-DECLARED BY W19e:
  SAMEFAM-DIFFGENE-DIFF5' = pairs whose 3' partners belong to the SAME sourced
  DNA-binding-domain family, are DIFFERENT genes, AND whose 5' partners differ.
Substrate/residual identical to W19c ARM 1 (reproduced as Gate 0, exit 0).
NULL: whole-name shuffle of the 32 (5',3') labels, 50,000 draws, seed 20260908,
  one-sided high, p = (1 + #{perm >= obs}) / (1 + n_perm).
  Report p as "< 2.1e-5" if it lands at the 1/50001 floor.
FLOOR: n >= 4 non-degenerate pairs to test.
FAMILIES: sourced only (ETS, CREB). Any 3' partner with no sourced statement is
  UNKNOWN and NEVER matches another UNKNOWN.
"""
exec(open('/tmp/claude-0/w19f/substrate.py').read())
import statistics, random, itertools

FAM = {"FLI1":"ETS","ERG":"ETS","FEV":"ETS","ETV1":"ETS","ETV4":"ETS",
       "ATF1":"CREB","CREB1":"CREB"}
def fam(g): return FAM.get(g)          # None == UNKNOWN

def samefam_diffgene_diff5(a,b, allowed=("ETS","CREB")):
    a5,a3=G[a]; b5,b3=G[b]
    fa,fb=fam(a3),fam(b3)
    if fa is None or fb is None: return False   # UNKNOWN never matches
    if fa!=fb: return False
    if fa not in allowed: return False
    if a3==b3: return False                     # different 3' GENE
    if a5==b5: return False                     # different 5' PARTNER
    return True

def run(pred, tag, nperm=50000, seed=20260908):
    idx={n:i for i,n in enumerate(names)}
    members=[p for p in good if pred(*p)]
    n=len(members)
    print("\n=== %s ===" % tag)
    print("member pairs (non-degenerate): n=%d" % n)
    for a,b in sorted(members):
        print("   %-16s x %-16s  fam=%-5s  J=%.4f  r=%+.4f  n_int %d/%d"
              %(a,b,fam(G[a][1]),J[(a,b)],R[(a,b)],nint[a],nint[b]))
    deg=[p for p in J if J[p] is None and pred(*p)]
    print("member pairs excluded as DEGENERATE: %d %s" % (len(deg), sorted(deg)))
    if n<4:
        print("TOO SMALL TO TEST (n<4) - descriptive only"); return
    obs=statistics.mean([R[p] for p in members])
    meanJ=statistics.mean([J[p] for p in members])
    gi=[(idx[a],idx[b],R[(a,b)]) for a,b in good]
    rng=random.Random(seed); labels=list(names); ge=0; nulls=[]
    for _ in range(nperm):
        rng.shuffle(labels)
        s=0.0;c=0
        for i,j,r in gi:
            if pred(labels[i],labels[j]): s+=r; c+=1
        v=s/c if c else 0.0
        nulls.append(v)
        if v>=obs: ge+=1
    p=(1+ge)/(1+nperm)
    pstr="< 2.1e-5 (Monte-Carlo floor, 1/50001)" if ge==0 else "%.5f"%p
    print("obs mean J %.4f   obs mean residual %+.4f   null mean %+.4f   null sd %.4f"
          %(meanJ,obs,statistics.mean(nulls),statistics.pstdev(nulls)))
    print("one-sided high p = %s   -> %s"
          % (pstr, "PREDICTS LOCATION" if p<=0.05 else "does NOT predict location"))
```
(`gate0.py` and `diag.py` re-use the same `substrate.py` and add no new statistic beyond the ARM-1 census, the degenerate-pair geometry and the leave-one-out means.)

---

## Limitations

**Carried forward without softening from W19c / W20b:**

- **The window is a sliver of one chromosome.** Every comparison happens inside `chr1:0` to a pair-specific ceiling — for this class, 14.5–225 Mb, but the *effective* comparison depth is 24–28 intervals per side. The retained data is a byte-truncated prefix, so the tested region is the proximal end of chr1 selected by nothing but sort order. Whether this holds genome-wide is **UNKNOWN**.
- **Windows are pair-dependent**, so the eight Jaccards are not interchangeable estimates of one quantity. The null was computed the same way, which keeps the comparison fair without making the windows comparable.
- **HEK293T is not EMC.** All fusions were expressed in one embryonic-kidney background. **Nothing here transfers to any tumour or patient**, to chondroid tissue, or to disease behaviour. A fusion's accessible chromatin in HEK293T is not its cistrome in EMC.
- **These are the authors' marker calls** at a threshold this repository did not set and cannot re-tune.
- **The genome-wide interval sets remain unrecovered** behind a 403 CONNECT policy denial I did not test or route around.

**New to this arm:**

- **n = 8, and the class is ETS-only in practice.** The one CREB candidate was lost to prefix geometry, so this is a test of *the ETS family*, not of "DBD families" in general. **No statement about CREB, or about any family other than ETS, is supported by this result** — the CREB arm is UNKNOWN, not null.
- **Five 3′ genes but only three 5′ partners.** Seven of the eight pairs contain EWSR1 on one side (never on both — no pair shares a 5′ partner). The class removes the *shared-5′* confound cleanly, but it does not remove EWSR1 from the panel; a design in which EWSR1 appeared on neither side is not available here. The single such pair, `FUS-FEV · TMPRSS2-ERG`, is positive (r = +0.1077, above the class median) — **n = 1 supports no inference** and I make no claim from it.
- **Three of the eight pairs involve `FUS-FEV` and five involve `TMPRSS2-ERG`**, so the eight pairs are far from independent — every peakset appears in up to four of them. Leave-one-out is stable (+0.1031 to +0.1349) but leave-one-*peakset*-out was not computed and the p-value's precision exceeds the evidence's precision, as with every small class on this panel.
- **Two families were sourced; others were not attempted.** In particular I noticed that PBX1 and CDX1 are both commonly described as homeodomain proteins, which if sourced and admitted would add a ninth pair and change the class. **I did not source it and did not test it** — introducing a third family after seeing the data would be exactly the post-hoc split my dispatch forbids. It is flagged as a limitation, not a result.
- **This is an ASSOCIATION in a heterologous cell line.** Nothing here bears on efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness of any agent, target or gene; no such quantity was computed. No reagent was designed. There is no wet lab. **No clinical claim.**
- **W19e's own +0.1607 / floor-p figures are SECONDARY (transferred through my dispatch prompt), not read.** I reproduced its *membership counts* (15 / 14 ETS / 7 EWSR1-shared) exactly, which is corroborating but not a verification of its test statistic.

---

## Stop condition

**Set in advance:** run the pre-declared `SAMEFAM-DIFFGENE-DIFF5′` class exactly as W19e specified it — after Gate 0 reproduces ARM 1, with families sourced by me from citable statements — under the whole-name shuffle at 50,000 draws, and **report a null with the same willingness as a positive**.

**MET.** Gate 0 reproduced ARM 1 digit-for-digit with no discrepancy. Families were sourced independently from four PubMed records. The class cleared its n ≥ 4 floor at n = 8, and the one apparent count difference against the transferred figure was traced to a definite, non-biological cause (prefix geometry) rather than smoothed over. The test returned a **positive** (p = 0.00084) — the pre-declared falsification did **not** falsify. Every member pair is listed. I stopped on meeting the condition and did not add work.

---

## Tool-call and wall-clock count actually used

**11 tool calls. Wall clock 02:47:51Z → 02:51:29Z ≈ 3.6 minutes** — well inside the ~40 call / ~40 min target. Four scripts written and run under `/tmp/claude-0/w19f/`; **zero repository writes; zero git writes; no denied route probed; $0 spend.**

---

## Next concrete action

**One successor, runnable on retained data with no new access:** the ETS block's internal dependence is the remaining soft spot — eight pairs drawn from six peaksets, with `FUS-FEV` and `TMPRSS2-ERG` each appearing in three-to-five of them. Run a **leave-one-peakset-out** version of this exact class (six arms, dropping each of `EWSR1-ETV1/ETV4/FEV/FLI1`, `FUS-FEV`, `TMPRSS2-ERG` in turn and re-permuting), reporting each arm's n and residual. That directly measures whether any single peakset carries the +0.1226, which leave-one-*pair*-out cannot. It is the same class, the same preregistration, and the same machinery — a robustness arm, not a new split — and each arm's n (3–5) must be reported against the n ≥ 4 floor, with the arms falling below it declared descriptive rather than tested.

**Not a successor:** sourcing a third DBD family to enlarge the class (that would be a post-hoc redefinition after seeing this result), and anything needing the genome-wide BEDs — that is one recorded 403 away and must not be re-probed.
