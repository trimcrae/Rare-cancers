> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Verification complete. Writing the report.

**Verdict: the tension is REAL but PARTIALLY ALREADY-KNOWN** — it is stated in exactly one repository file (a review/observations doc), and absent from all three design documents. Full report follows.

---

## Worker

**W19b**, refill for Lane 19 — testing Q-NR4A2-COVERAGE against the repository's own fusion-partner corpora.

**Model evidence: SELF-REPORT ONLY, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:05:16 UTC 2026`. At end: `Tue Sep  8 02:07:50 UTC 2026` (final env re-check same turn; report drafting followed).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (51 lines; proxy plumbing `no_proxy`/`NO_PROXY`/`npm_config_noproxy`/`GLOBAL_AGENT_NO_PROXY`/`JAVA_TOOL_OPTIONS` matched the grep and are elided for length — they are verbatim in the tool log):

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

---

## Question

**Q-NR4A2-COVERAGE — does this repository's therapeutic architecture structurally fail EMC patients whose tumour is driven by an NR4A2 fusion rather than an NR4A3 fusion?**

Decomposed into the four things the dispatch actually asks: (a) is the tension real against committed text, or already scoped away somewhere; (b) how many such cases does the retained corpus actually attest, with an honest denominator; (c) for each of the three modalities, does an NR4A2 fusion escape it, and by which committed design requirement; (d) what is the smallest scoped correction, and to whom is it routed.

---

## Prior-work check

Commands run and what they showed.

```
rg -n -i "::NR4A2|NR4A2::|NR4A2[ -]fusion|NR4A2 rearrang" --glob '!.git' .
```
→ 24 hits. NR4A2-fusion EMC is retained in the tree in three roles: as a citation record (`fusion-junction-aso-references.json:912`, `.md:90`, `lit-targets-aso-verify.json:675`, `emc-atr-vulnerability-inputs.json:3411`), as a breakpoint-census verbatim (`lit-targets-aso-breakpoint-census.json:409`), and in one hormone-route file (`hspa8-promoter-hormone-grade.json:11,165`).

The decisive search:

```
rg -n -i "NR4A2" --glob '!.git' --glob '!**/opus-capacity-campaign-*/**' \
   --glob '!systems/graph/**' --glob '!**/*.py' . \
 | rg -i "substitut|misses by|miss by|addressable population|coverage gap|not covered|blind to"
```
→ **exactly one repository file states the coverage observation**: `research/manuscripts/program/emc-unexplored-treatment-lanes.md:545-549`.

```
rg -n "NR4A2" research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md \
   research/manuscripts/degrader/nr4a3-degrader-selectivity-architecture.md \
   research/manuscripts/nr4a3-program-map.md
```
→ 40 hits across the three design documents. **Every one treats NR4A2 as a paralogue to be spared** (tox-mitigation, PK/CNS-exclusion, handle counting, ΔΔG margins). **None scopes the requirement to NR4A3-driven EMC.**

New evidence capsule:
```
cd research/autonomy/opus-capacity-campaign-20260908/inputs/evidence-4878 && grep -rn "NR4A2" .
```
→ **zero hits.** The 47-file capsule contains no NR4A2 material at all. Per the dispatch, absence from a file snapshot is **not** proof of absence in the repository's ancestry; it means the capsule contributes nothing here.

Closed items I confirm I am not replaying: the NR4A Perspective content-policy refusal (not recreated, not rerouted, not relabelled); registry ICD-O; methylation; GSE4303/GSE28866 re-read; independent-cohort invention; pazopanib/sunitinib/Wagner/CTARC denied routes (I made **no** network calls this session); source-index (lane 11). I did not redo W19's ranking.

**Novelty verdict: PARTIALLY ALREADY-KNOWN.** W19's statement that the tension is "unstated in the repository" is **refuted**. I report that rather than building on it.

---

## Method / inputs

Repository read-only at frozen HEAD `92abbcb905cacf07f14b238db50d1b98f6590374` (verified at end). No network. No paid API. $0. Python 3.11.15, stdlib only. Script authored and executed at `/tmp/claude-0/w19b/count_nr4a2.py`, outside the tree.

Corpora scanned (all committed):

| file | role |
|---|---|
| `research/manuscripts/aso/lit-targets-aso-breakpoint-census.json` | query corpus + per-record verbatims |
| `research/manuscripts/aso/fusion-junction-aso-references.json` | citation records |
| `research/manuscripts/aso/fusion-junction-aso-submission-references.json` | citation records + abstracts |
| `research/manuscripts/aso/lit-targets-aso-verify.json` | verified abstracts |
| `research/manuscripts/aso/aso-citations-priorart-2026-08-08.md` | prior-art register |
| `research/manuscripts/aso/fusion-junction-aso-working-record.md` | working record |
| `research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md` | retained case-series retrieval record |
| `research/manuscripts/program/emc-unexplored-treatment-lanes.md` | observations register |
| `research/modalities/emc-atr-vulnerability-inputs.json` | citation records |

Design documents read verbatim: `research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md`, `research/manuscripts/degrader/nr4a3-degrader-selectivity-architecture.md`, `research/manuscripts/nr4a3-program-map.md`, `research/manuscripts/aso/fusion-junction-aso-research-article.md`, `systems/views/L2-rt-degrader.md`, `systems/views/L1-st-occupancy.md`.

---

## Result

### R1 · The tension is REAL in the design documents — verified verbatim

`research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md:53-55` (`SECONDARY`, committed text):

> "That LBD sequence is **identical in the fusion and in wild-type NR4A3** — the fusion retains a near-intact LBD — so the agent is NR4A3-selective (it can be tuned to spare the NR4A1/NR4A2 paralogues) but **not fusion-selective**"

Same file, `:322-325`:

> "⛔ **The paralogue layer is not one requirement**: sparing NR4A1 is the hard, mandatory half, and all 7 handles (5 engageable) differ from it; **sparing NR4A2 is best-effort**, and only 6 of 7 differ (4 of the 5 engageable), because I531 is Ile in NR4A3 *and* NR4A2"

`research/manuscripts/degrader/nr4a3-degrader-selectivity-architecture.md:24`:

> "plus pharmacokinetics for NR4A2), and route fusion-vs-wild-type — unobtainable from the degrader — to the ASO."

Same file, `:42-44`, which is the load-bearing framing:

> "- **Axis A — paralogue:** NR4A3 vs NR4A1 (NUR77) and NR4A2 (NURR1). A *tox-mitigation* requirement. … NR4A2 risks dopaminergic/Parkinsonian effects (NR4A2/Nurr1 is a midbrain-DA-neuron gene). So sparing…"

And `:250`:

> "3. **Paralogue safety (NR4A2):** source primarily from **PK / CNS-exclusion** (peripheral restriction),"

**Confirmed: across all three design documents NR4A2 is framed exclusively as an anti-target, on a tox-mitigation rationale, with zero scope qualifier.** The route title itself carries the unqualified form — `systems/views/L2-rt-asymmetric.md:3`: *"Asymmetric selectivity — NR4A1-sparing mandatory, NR4A2-sparing best-effort"*.

### R2 · But it is ALREADY STATED, once, in a review file — this is the correction to W19

`research/manuscripts/program/emc-unexplored-treatment-lanes.md:545-549`, verbatim (`SECONDARY`):

> "7. ⚠ **NR4A2 can substitute for NR4A3 as the driver.** An EMC with no canonical NR4A3 fusion carried **HSPA8::NR4A2**, full neuroendocrine phenotype, **methylation class EMC at 0.99** (*Virchows Arch* 2025, **PMID 41315062** **[API]**); **FUS::NR4A2** is separately reported. `RT-ASYMMETRIC` holds NR4A2-sparing as best-effort — for that subset a strictly NR4A2-sparing agent misses by construction. This bounds the addressable population; it does not contradict the selectivity rule."

That is the substance of Q-NR4A2-COVERAGE, already written, already correctly hedged, and already routed as an observation for "whoever owns" the lane. **W19's novelty claim does not survive.**

What remains genuinely open, and is the residue I contribute:

| # | residue | status |
|---|---|---|
| 1 | The observation lives **only** in an observations register. Not one of the three design documents, nor `RT-ASYMMETRIC`, nor requirement `R7`, carries the scope qualifier. | `PRIMARY` (my grep, above) |
| 2 | The lanes item covers **one** modality — "a strictly NR4A2-sparing agent", i.e. the degrader/binder paralogue axis. It does **not** state that the junction ASO also fails. | `PRIMARY` |
| 3 | No numerator/denominator has been computed anywhere in the tree. | `PRIMARY` |

### R3 · The count — numerator 2, denominator UNKNOWN

**Pass A (mechanical, `PRIMARY`, computed this session).** Fusion-token scan over the nine corpora. **These are string mentions in query corpora, not cases**, per W19's explicit warning, and they are used for nothing downstream:

| fusion token | raw mentions | distinct corpus files |
|---|---|---|
| EWSR1::NR4A3 | 102 | 9 |
| TAF15::NR4A3 | 44 | 9 |
| TCF12::NR4A3 | 18 | 7 |
| TFG::NR4A3 | 13 | 1 |
| HSPA8::NR4A2 | 6 | 4 |
| FUS::NR4A2 | 4 | 4 |
| SMARCA2::NR4A3 | 4 | 2 |
| ACTB::NR4A3 | 3 | 3 |
| FUS::NR4A3 | 3 | 2 |
| `EMC::NR4A3` | 2 | 1 |
| PGR::NR4A3 | 2 | 2 |
| LSM14A::NR4A3 | 1 | 1 |

Raw mention total 202; 12 distinct tokens; 170 distinct (fusion, file, line) triples. **`EMC::NR4A3` is a false positive of my regex** — it matches the prose string "EMC-NR4A3", not a gene fusion. I report it rather than silently filtering it, because a filter tuned after seeing the output is a filter tuned on the outcome. It affects nothing: pass A feeds no count.

**Pass B (curated, provenance-checked, `SECONDARY` — the underlying reports are literature, not my measurement).** Only reports whose retained text states **both** a case count **and** the fusion per case:

| PMID | n cases | ascertainment | selection | fusions | NR4A2-driven |
|---|---|---|---|---|---|
| 41755350 (*Histopathology* 2026, doi 10.1111/his.70131) | 5 | NGS, unbiased fusion detection | **selected variant-morphology series** | EWSR1::NR4A3 ×1, FUS::NR4A3 ×2, ACTB::NR4A3 ×1, **FUS::NR4A2 ×1** | 1 |
| 41315062 (*Virchows Arch* 2025, doi 10.1007/s00428-025-04352-7) | 1 | RNA-seq + methylation classifier (EMC class 0.99) | **single case report** | **HSPA8::NR4A2 ×1** | 1 |

```
NR4A2-driven EMC cases (numerator)           : 2
NR4A3-driven cases in the SAME reports       : 4
cases in reports stating a fusion per case   : 6
DENOMINATOR FOR PREVALENCE                   : UNKNOWN
```

**Why the denominator is UNKNOWN, and structurally so — this is the methodological point, not an excuse.** A prevalence denominator requires EMC cases *assayed by a method capable of detecting an NR4A2 fusion*. The historical EMC series in this corpus typed tumours by **NR4A3-targeted FISH or RT-PCR**, which cannot detect an NR4A2 fusion by construction; they therefore cannot enter the denominator at all. The two reports that can are both **selected**: a variant-morphology series and a single case report. The repository's own census file states this restriction unprompted, at `lit-targets-aso-breakpoint-census.json` (`what_the_two_sentences_give`):

> "⛔ THE SERIES IS OF VARIANT EMCs BY SELECTION, which is why the paper says 'variant cases' and not 'cases': two of five here is NOT a prevalence estimate for FUS in EMC, and nothing in this repository may read it as one."

So **1 of 5 is not a rate**, and neither is 2 of 6. `partner-event-counts-2026-08-08.md:287` independently records PMID 41755350 as carrying "no EWSR1-vs-TAF15 contrast", and PMID 40885991 (Japanese national registry, n = 171) as "**not stratified by fusion partner at all**" — so the one large registry in the corpus cannot supply a denominator either.

**Numerator 2. Denominator UNKNOWN. Prevalence not estimable from this corpus.**

### R4 · The structural argument, per modality, from committed design requirements

| modality | the committed design requirement that makes it blind | why an NR4A2 fusion escapes |
|---|---|---|
| **Junction ASO** | `fusion-junction-aso-research-article.md:3` (title, i.e. the paper's own scope statement): *"junction-spanning 5-6-5 gapmer designs across 38 modelled **NR4A3** fusion junctions of five extraskeletal myxoid chondrosarcoma partner genes"* | The design space is enumerated as NR4A3 junctions. An ASO is a sequence-complementarity agent; a `FUS::NR4A2` or `HSPA8::NR4A2` junction is a **different sequence** and appears in none of the 38. Not a tuning shortfall — the target is absent from the enumeration. The ASO corpus files PMID 41315062 among "Variant 5′ partners" (`aso-citations-priorart-2026-08-08.md:140`), i.e. **as a further NR4A3 partner**, which is the mis-filing that lets the gap persist. |
| **NR4A3-selective degrader** | `fusion-selective-andgate-degrader-paper.md:54`: the agent *"is NR4A3-selective (it can be tuned to spare the NR4A1/NR4A2 paralogues)"*; `nr4a3-degrader-selectivity-architecture.md:250`: *"**Paralogue safety (NR4A2):** source primarily from **PK / CNS-exclusion** (peripheral restriction)"* | The requirement is to **remove NR4A3 and spare NR4A2**. Applied to an NR4A2-fusion tumour it removes a bystander and spares the driver — the requirement is **inverted**, not merely insufficient. The PK lever makes it worse in a specific way: a **peripherally-restricted** agent is designed to reach peripheral tissue and not the CNS, and EMC is a peripheral soft-tissue sarcoma — so peripheral restriction spares midbrain NR4A2 *and* spares the peripheral tumour's NR4A2 driver by the same mechanism. |
| **NR4A3 binder (R7)** | `nr4a3-program-map.md:1620`, requirement R7: *"**The binder is paralogue-selective over NR4A1/NR4A2**"* | The binder's success criterion is a **negative** margin against NR4A2 — the reported ΔΔG(NR4A3−NR4A2) = **−4.98 ± 0.68** (`nr4a3-program-map.md:2412`, held provisional and parked on defect `V9`). A binder that better satisfies R7 is *by that same measure* less able to engage an NR4A2 fusion. **Optimising the requirement monotonically worsens coverage of this subset.** |

**The compounding fact, which is the part no repository file states:** the architecture routes each modality's weakness to another. `nr4a3-degrader-selectivity-architecture.md:24` — *"route fusion-vs-wild-type — unobtainable from the degrader — to the ASO."* That referral is what makes the portfolio complete for NR4A3-driven EMC. For an NR4A2-driven tumour **all three arms fail simultaneously and the referral has nowhere to point**: the ASO's junction list has no NR4A2 entry, the degrader's requirement is inverted, and the binder's success metric is anti-correlated with coverage. This is a portfolio-level property, and it is not visible from inside any single document — which is exactly why the observation sitting in one review file has not propagated.

Hard limits observed: this is a **design-coverage observation**, not a clinical finding. No efficacy, safety, selectivity or therapeutic-window claim is made or implied for any agent, no reagent is designed, and no NR4A2-directed agent is proposed here.

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24, Python 3.11.15, stdlib only, no network, $0, cwd `/tmp/claude-0/w19b` (outside the repository).

```
$ python3 --version
Python 3.11.15
$ python3 count_nr4a2.py
... (pass A table, pass B table and the denominator statement as reproduced above) ...
EXIT=0
```

Determinism:
```
$ python3 count_nr4a2.py > a.txt 2>&1; python3 count_nr4a2.py > b.txt 2>&1; diff -q a.txt b.txt
DETERMINISTIC exit 0/0
```

**Over-counting / fabrication guards, and a negative control that proves G3 fires.** The guards are G1 (collapse duplicate mentions per fusion), G2 (abort on duplicate PMID in the case table — the same report is reachable through four corpus files and must not add cases four times), G3 (every curated row's fusion token must be literally present in the file it cites), G4 (pass A mention counts may never become a denominator). G3 tested by mutating one attested token to a nonexistent one:

```
$ sed 's/HSPA8::NR4A2"),/HSPA8::NR4A9"),/' count_nr4a2.py > guardtest.py
$ python3 guardtest.py
ABORT G3: HSPA8::NR4A9 not literally present in research/manuscripts/aso/lit-targets-aso-verify.json — row is unattested
guardtest EXIT=3
```
The guard is live, not decorative: an unattested case row aborts the run.

Write isolation:
```
$ git status --porcelain
?? research/autonomy/opus-capacity-campaign-20260908/
$ git rev-parse HEAD
92abbcb905cacf07f14b238db50d1b98f6590374
```
The single untracked path is the campaign directory that pre-existed my session. **I created and modified no file under `/home/user/Rare-cancers` and ran no git write operation.** No manuscript or architecture file was edited.

**PROPOSED (NOT RUN):** any external retrieval of PMID 41755350 or 41315062 full text (I made zero network calls); any denominator from a fusion-agnostic EMC cohort; `scripts/preflight.sh` (dispatch did not direct it).

**No content-policy refusal was encountered in this session.**

### The script

`/tmp/claude-0/w19b/count_nr4a2.py`, returned inline per write isolation:

```python
#!/usr/bin/env python3
"""
W19b — NR4A2-fusion EMC coverage count.

Two independent passes, deliberately kept apart:

  PASS A (mechanical): scan the retained corpora for 5'partner::NR4A{1,2,3} fusion
          tokens. Reports RAW MENTIONS and DISTINCT (source-record, fusion) pairs.
          A mention is NOT a case. This pass produces NO case count.

  PASS B (curated, provenance-checked): a per-report case table built ONLY from
          verbatim sentences that state the number of cases and their fusion.
          Every row is checked back against the file it claims to come from;
          a row whose fusion token is not literally present in its cited file
          is a FABRICATION and aborts the run (exit 3).

Over-counting guards:
  G1 duplicate (pmid, fusion) collapse in pass A
  G2 same report reachable through >1 corpus file must not add cases twice (pass B
     is keyed on PMID, and duplicate PMIDs abort)
  G3 pass B rows must be literally attested in their cited file
  G4 the denominator is NEVER inferred from pass A mention counts
"""
import json, os, re, sys, collections

REPO = "/home/user/Rare-cancers"

CORPORA = [
 "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json",
 "research/manuscripts/aso/fusion-junction-aso-references.json",
 "research/manuscripts/aso/fusion-junction-aso-submission-references.json",
 "research/manuscripts/aso/lit-targets-aso-verify.json",
 "research/manuscripts/aso/aso-citations-priorart-2026-08-08.md",
 "research/manuscripts/aso/fusion-junction-aso-working-record.md",
 "research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md",
 "research/manuscripts/program/emc-unexplored-treatment-lanes.md",
 "research/modalities/emc-atr-vulnerability-inputs.json",
]

# Historical gene aliases used in the pre-2000 EMC literature.
ALIAS = {"CHN": "NR4A3", "TEC": "NR4A3", "NOR1": "NR4A3", "NOR-1": "NR4A3",
         "RBP56": "TAF15", "TAF2N": "TAF15", "EWS": "EWSR1", "NURR1": "NR4A2"}

TOKEN = re.compile(r"\b([A-Z][A-Z0-9]{1,9})\s*(?:::|-|–|/)\s*(NR4A[123]|CHN|TEC|NOR-?1)\b")

def norm(g):
    return ALIAS.get(g.upper(), g.upper())

def pass_a():
    raw = collections.Counter()
    pairs = set()
    per_fusion_files = collections.defaultdict(set)
    for rel in CORPORA:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            print(f"  MISSING (UNKNOWN, not absent): {rel}")
            continue
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            for m in TOKEN.finditer(line):
                five, three = norm(m.group(1)), norm(m.group(2))
                if not three.startswith("NR4A"):
                    continue
                if five.startswith("NR4A"):     # paralogue-pair prose, not a fusion
                    continue
                fus = f"{five}::{three}"
                raw[fus] += 1
                per_fusion_files[fus].add(rel)
                pairs.add((fus, rel, i))
    return raw, per_fusion_files, pairs

# ---- PASS B: per-report case rows, each with the verbatim it rests on -------
# Only reports whose retained text states BOTH a case count and the fusion(s).
CASES = [
 dict(pmid="41755350", n_cases=5, ascertain="NGS (unbiased fusion detection)",
      selection="SELECTED variant-morphology series — NOT a prevalence sample",
      fusions={"EWSR1::NR4A3":1, "FUS::NR4A2":1, "ACTB::NR4A3":1, "FUS::NR4A3":2},
      attest_file="research/manuscripts/aso/lit-targets-aso-breakpoint-census.json",
      attest_token="FUS::NR4A2"),
 dict(pmid="41315062", n_cases=1, ascertain="RNA-seq + methylation classifier",
      selection="single case report — no denominator",
      fusions={"HSPA8::NR4A2":1},
      attest_file="research/manuscripts/aso/lit-targets-aso-verify.json",
      attest_token="HSPA8::NR4A2"),
]

def pass_b():
    seen = set()
    for c in CASES:
        if c["pmid"] in seen:                                   # G2
            print(f"ABORT G2: duplicate PMID {c['pmid']}"); sys.exit(3)
        seen.add(c["pmid"])
        blob = open(os.path.join(REPO, c["attest_file"]), encoding="utf-8",
                    errors="replace").read()
        if c["attest_token"] not in blob:                        # G3
            print(f"ABORT G3: {c['attest_token']} not literally present in "
                  f"{c['attest_file']} — row is unattested"); sys.exit(3)
        if sum(c["fusions"].values()) != c["n_cases"]:
            print(f"ABORT: fusion counts != n_cases for {c['pmid']}"); sys.exit(3)
    return CASES

def main():
    print("=" * 78)
    print("PASS A — mechanical fusion-token scan.  A MENTION IS NOT A CASE.")
    print("=" * 78)
    raw, files, pairs = pass_a()
    for fus, n in sorted(raw.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {fus:<18} raw_mentions={n:<4} distinct_corpus_files={len(files[fus])}")
    print(f"\n  raw mention total          : {sum(raw.values())}")
    print(f"  distinct fusion tokens     : {len(raw)}")
    print(f"  distinct (fusion,file,line): {len(pairs)}")
    print("  G1/G4: these are STRING MENTIONS in a query corpus. They are NOT")
    print("         case frequencies and are NOT used as any denominator.")

    print()
    print("=" * 78)
    print("PASS B — per-report EMC cases with a stated fusion, provenance-checked")
    print("=" * 78)
    cases = pass_b()
    tot = nr4a2 = nr4a3 = 0
    for c in cases:
        print(f"\n  PMID {c['pmid']}  n_cases={c['n_cases']}")
        print(f"    ascertainment : {c['ascertain']}")
        print(f"    selection     : {c['selection']}")
        for f, n in sorted(c["fusions"].items()):
            tag = "NR4A2-DRIVEN" if f.endswith("NR4A2") else "NR4A3-driven"
            print(f"      {f:<16} n={n}   {tag}")
            if f.endswith("NR4A2"): nr4a2 += n
            else: nr4a3 += n
            tot += n
        print(f"    attested in   : {c['attest_file']} (token {c['attest_token']} present)")

    print()
    print("-" * 78)
    print(f"  NR4A2-driven EMC cases (numerator)          : {nr4a2}")
    print(f"  NR4A3-driven EMC cases in the SAME reports  : {nr4a3}")
    print(f"  cases in reports that state a fusion per case: {tot}")
    print("-" * 78)
    print("  DENOMINATOR FOR PREVALENCE : UNKNOWN — and structurally so.")
    print("  A prevalence denominator requires EMC cases ASSAYED BY A METHOD ABLE")
    print("  TO DETECT AN NR4A2 FUSION. Historic EMC series typed tumours by")
    print("  NR4A3-targeted FISH/RT-PCR, which cannot detect an NR4A2 fusion by")
    print("  construction, so they cannot enter the denominator. Both reports above")
    print("  are additionally SELECTED (a variant-morphology series and a single")
    print("  case report), so 1/5 is not a rate. Numerator 2, denominator UNKNOWN.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## The routed correction

**I edited nothing.** This is a proposal routed to the owners, exactly as the dispatch requires.

**Route to: the degrader-selectivity owner (`RT-ASYMMETRIC` / `PUB-DEGRADER`), and separately to the ASO submission owner.** Note the ASO manuscript is under `PUB-ASO`, which `CLAUDE.md` §3 and `CLOSED-WORK.md` place with the submission owner / user — so item C below is a **notification, not a proposed edit**, and must not be actioned by an agent.

**A · The smallest scoped caveat (degrader-selectivity owner).** One clause, wherever the requirement is stated — `fusion-selective-andgate-degrader-paper.md:54` and `:324`, `nr4a3-degrader-selectivity-architecture.md:42-44` and `:250`, `nr4a3-program-map.md` R7 and §2.4, and the `RT-ASYMMETRIC` route title:

> Sparing NR4A2 is the correct requirement **for NR4A3-driven EMC**, which is the population every agent in this program is designed against. It is **inverted for the NR4A2-fusion subset** (`HSPA8::NR4A2`, PMID 41315062; `FUS::NR4A2`, PMID 41755350), where NR4A2 is the driver and sparing it spares the tumour. That subset is **outside the addressable population** of this portfolio; its size is **UNKNOWN** and is not estimable from the retained corpus, because the historical series were typed by NR4A3-targeted assays that cannot detect it.

That is a **scope statement on an existing requirement**, not a change to it. It weakens nothing: the tox-mitigation rationale for NR4A2-sparing stands unchanged within its scope.

**B · The residue W19's target file does not cover (same owner).** `emc-unexplored-treatment-lanes.md:545-549` already states the observation for "a strictly NR4A2-sparing agent". Two things it does not say and that the count above supports: (i) the **binder** case is not merely a miss but **anti-correlated** — R7's success metric ΔΔG(NR4A3−NR4A2) = −4.98 ± 0.68 means a better-satisfied R7 is a worse-covering binder; (ii) the **peripheral-restriction** lever (`architecture.md:250`) fails in the tumour's own compartment, since EMC is a peripheral soft-tissue sarcoma.

**C · Notification only, to the ASO/PUB-ASO owner.** `aso-citations-priorart-2026-08-08.md:140` and `fusion-junction-aso-working-record.md:1782` file PMID 41315062 under **"Variant 5′ partners"** of NR4A3. It is not a variant 5′ partner — it is a **different 3′ gene**, and the ASO's 38-junction enumeration therefore does not and cannot cover it. Whether the ASO manuscript should say anything is the owner's decision; I flag the classification, propose no edit, and take no action on it.

---

## Limitations

1. **W19's novelty claim is refuted, and mine is correspondingly narrow.** The coverage observation exists at `emc-unexplored-treatment-lanes.md:545-549`. What I add is: the propagation gap into the design documents, the third-modality (ASO) leg, the anti-correlation reading of R7, and the first actual count.
2. **Numerator 2 rests on two literature reports I did not retrieve this session.** They are `SECONDARY` — retained abstracts and verbatims, not my measurement. I made zero network calls; nothing was re-fetched or verified against the publishers.
3. **Denominator UNKNOWN, and no prevalence, rate, fraction or percentage is asserted.** "2" is a count of attested cases in a selected corpus, not an incidence.
4. **My corpus list is nine files, not the whole tree.** Additional NR4A2-fusion EMC reports may exist in the repository or the literature outside it. Absence from my scan is UNKNOWN, not proof of absence — as is the capsule's zero NR4A2 hits.
5. **Pass A carries a known false positive** (`EMC::NR4A3`, a prose match). Reported rather than filtered post hoc.
6. **Nothing here is a clinical finding.** No efficacy, safety, selectivity or therapeutic-window claim; no reagent design; there is no wet lab. A coverage gap is a design observation. Whether NR4A2-fusion EMC would respond differently to anything is entirely unaddressed.
7. **I hold no write access and proposed no edit to any owned file.** The correction is routed, not applied.
8. The structural argument in R4 is an argument from committed design documents. It establishes what the *portfolio as specified* does, not what any molecule does.

---

## Stop condition

**Set (from the dispatch):** the tension verified or refuted against committed text; an honest numerator/denominator; a cited structural argument per modality; a routed scoped correction.

**MET, with the first element returning a partly negative result.**

- **Tension: VERIFIED in the design documents** (quoted at four line ranges) — **but the coverage observation is ALREADY-KNOWN**, stated once at `emc-unexplored-treatment-lanes.md:545-549`. Reported as a refutation of W19's novelty claim rather than built on.
- **Count: numerator 2, denominator UNKNOWN and structurally so.** Deterministic, exit 0, with a G3 guard shown firing at exit 3 on a negative control.
- **Structural argument: given for all three modalities**, each citing the committed requirement that makes it blind, quoted not paraphrased.
- **Correction: routed**, in three parts, with nothing edited.

---

## Tool-call and wall-clock count actually used

**16 tool calls** (target ~40). **Wall clock 02:05:16Z → 02:07:50Z of tool time ≈ 2.5 minutes**; total turn duration modestly longer with report drafting. Well under both budgets. $0, no network, no GPU.

---

## Next concrete action

**One task, for the degrader-selectivity owner, not for this lane:** apply caveat **A** at the six named locations and fold residue **B** into `RT-ASYMMETRIC`, then regenerate `systems/views/` so `L2-rt-asymmetric.md:3` and `L2-rt-degrader.md:8` carry the scope rather than the unqualified "NR4A2-sparing best-effort". That is a $0 in-tree edit with a checkable numerator behind it.

**For lane 19 itself: no viable successor, and I recommend closing the lane** rather than refilling it again. The lane's remaining questions are the ones W19's own sensitivity sweep showed are not robustly ordered, and its top question has now resolved to a propagation fix owned by someone else. The one thing that would genuinely advance Q-NR4A2-COVERAGE — a denominator from an EMC cohort typed by fusion-agnostic RNA-seq — is blocked by the gateway 403s W19 recorded, and inventing a cohort is forbidden. Refilling this lane a third time would produce restatement, not evidence.

result: Q-NR4A2-COVERAGE verified but PARTIALLY ALREADY-KNOWN — the NR4A2-driven-EMC coverage observation is already stated at emc-unexplored-treatment-lanes.md:545-549, refuting W19's novelty claim; what is genuinely open is that none of the three design documents carries the scope, and the count returns numerator 2 NR4A2-driven EMC cases (HSPA8::NR4A2 PMID 41315062; FUS::NR4A2 PMID 41755350) against a denominator that is UNKNOWN and structurally unobtainable because historical EMC series were typed by NR4A3-targeted assays blind to NR4A2 — with a three-modality structural argument from quoted committed requirements (the ASO's 38 junctions are all NR4A3; the degrader requirement is inverted; R7's ΔΔG(NR4A3−NR4A2) = −4.98 ± 0.68 makes binder coverage anti-correlated with its own success metric) and a scoped correction routed, unapplied, to the degrader-selectivity owner.
