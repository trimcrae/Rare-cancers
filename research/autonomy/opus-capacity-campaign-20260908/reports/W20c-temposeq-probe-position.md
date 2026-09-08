> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

> **COORDINATOR COLLECTION NOTE.** This report changes the inferential label attached to W20's
> primary endpoint: the correct label for that null is **UNDECIDED, not REFUTED**, because the
> TempO-Seq TAF15 probe lies 3' of the breakpoint and the null had no power by construction.
> W20's computed values, its FUS control and its other findings stand unchanged.

Sanity check: the verdict string is printed by the script, not typed by me; the exon-6 endpoint is confirmed twice by independent routes (cumulative exon lengths, and the fusion atlas seam 12-mer); the nucleotide match is unique in the TAF15 cDNA; nothing was written into the repository.

---

## Worker

**Worker ID:** W20c · **Lane 20 refill** — settle the probe-position premise that W20 named as its own dominant limitation.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). This is a self-report from my own system context, not an observed fact. No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (run at end of work; the long `no_proxy` / `JAVA_TOOL_OPTIONS` / `npm_config_noproxy` lines are retained verbatim in the transcript and contain no model information):

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

`date -u` at end: `Tue Sep  8 02:14:57 UTC 2026`.
**Honest reporting gap:** I did **not** capture `date -u` at the start of my run, so I cannot state my own start time as a measurement. My elapsed wall clock is therefore reported below as a bounded estimate, not an observation.

Repository HEAD read: `103ff76f1d66426420c56a4d49752eb84f5f5c39`. This is **not** the frozen campaign commit `92abbcb90...` named in `COMMON-BRIEF.md`; the difference is the coordinator's own collection commits of earlier workers' reports (`git status --porcelain` shows further worker reports still untracked). **Every file I read is committed at this HEAD and none of them is a campaign report**, so the drift does not affect this result. **No file under `/home/user/Rare-cancers` was created, modified or staged; no git write of any kind was performed.** All execution was under `/tmp/claude-0/w20c/`.

---

## Question

**Where does the TempO-Seq *TAF15* probe used in W20's test sit relative to the TAF15 breakpoint of TAF15::NR4A3 — 5′ of it (the test had power) or 3′ of it (the test had none)?**

This is open because W20 named it open. W20's own Limitations section states:

> "The prediction depends on an unverified premise I could not check: that the TempO-Seq *TAF15* probe lies **5′ of the fusion breakpoint**. If it lies 3′, the fusion allele contributes nothing to the probe and the test had **no power by construction**. The probe-to-transcript map in `emc-fourth-cohort-quant.json` assigns probes to genes by verbatim cDNA matching; it records no breakpoint-relative position."

The premise is decisive in both directions, which is why it is worth one worker: W20's REFUTED verdict is a real negative only if the probe could ever have seen the fusion allele.

---

## Prior-work check

Commands actually run and what they showed.

```
git ls-files | grep -i -E "probe|tempo|temposeq"
   -> research/modalities/emc-fourth-cohort-probe-counts.tsv   (probe-level counts, 213,008 rows)
      ... plus ~30 unrelated files where "probe" means a literature/API probe

git ls-files | grep -i -E "\.(fa|fasta|fa\.gz|seq)$"
   -> research/manuscripts/aso/fusion-junction-aso-sequences.fasta   (ASO oligos only)

grep -rl -E "[ACGT]{200,}" --include="*.json" --include="*.txt" --include="*.tsv" research/
   -> research/modalities/{nr4a3-intron2-cryptic-exon,emc-construct-inputs,
      nr4a3-nuccore-sweep,emc-ret-target-scan-inputs,aso-premrna-sequences}.json

grep -rl -E "MSDSGSYGQ|QGSYG|RGGYGG|DRGGYGG" research/
   -> research/modalities/{emc-construct-inputs,emc-fet-construct-designs,
      emc-condensate-constructs,fet-sequences-cache}.json

grep -n "TAF15_e6" research/modalities/aso-per-junction-table.json \
                   research/modalities/nr4a3-fusion-junction-atlas.json
grep -rn "TAF15_e6__NR4A3_e3\|TAF15 exon 6" --include="*.md" --include="*.json" research/
```

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`, read in full):

- **W20's own test** — not re-run. I executed no differential-expression test, no permutation, and no label split. I read the probe *sequence*, not the counts as an outcome.
- **Hofvander (one TAF15 case, EGA controlled-access)** — no Hofvander material used, no EGA request made. The shared word "TAF15" is coincidental; this is a probe-annotation question about a commercial panel.
- **GSE4303 / GSE28866, "rediscovery is not new data"** — neither used.
- **The 403-denied archive routes** — **not attempted at all.** I downloaded nothing, made no network request of any kind, and did not replay the routes W20 and W01b recorded as blanket-blocked. Everything below is committed data.
- **Promoter transfer, inverse bounds, Davis, Brenca, methylation, registry ICD-O, the clinical checkpoints** — none touched.
- **The restricted NR4A Perspective refusal** — not touched, not recreated, not relabelled. I hit **no** content-policy refusal in this run.

I found no prior repository artifact that places any TempO-Seq probe relative to any fusion breakpoint. `emc-fourth-cohort-quant.json`'s `probe_map` is the only probe-annotation record and, as W20 said, it carries no positional field.

---

## Method / inputs

All inputs are committed at HEAD `103ff76f...`. Nothing was downloaded; no network call was made.

| Input | Path | What I used |
|---|---|---|
| Probe-level counts | `research/modalities/emc-fourth-cohort-probe-counts.tsv` | the one row whose `assigned_gene` is `TAF15`; its `probe_sequence` field |
| Probe-map provenance | `research/modalities/emc-fourth-cohort-quant.json` | `probe_map` block, quoted below |
| TAF15 transcript record | `research/modalities/emc-construct-inputs.json` | `genes.TAF15`: `cdna`, `cds`, `protein`, `exons[]` with per-exon cDNA spans |
| TAF15 pre-mRNA | `research/modalities/aso-premrna-sequences.json` | `genes.TAF15.sequence` (37,759 nt unspliced), independent second coordinate system |
| Breakpoint record | `research/modalities/nr4a3-fusion-junction-atlas.json` | `TAF15_e6__NR4A3_e3` record: `donor_exon_end`, `seam_mRNA`, `chimeric_protein_length` |
| Breakpoint corroboration | `research/modalities/aso-per-junction-table.json`, `emc-fet-construct-designs.json`, review-seat records | that TAF15 exon 6 is the reported donor exon |

**Tools:** Python 3.11.15, standard library only (`json`, `re`). No third-party package, no network, no GPU, no paid API. `df -h /` before and after: `/dev/vda 252G, 24G avail, 36% used` — the ≥10 GiB budget is satisfied and nothing was downloaded, so no disk was consumed beyond two small scripts.

**Decision rule, fixed in the script docstring before execution and printed by the script, not typed by me:**

- (a) probe END ≤ exon-6 end → probe is 5′ of the breakpoint → W20's test **had** power
- (b) probe START > exon-6 end → probe is 3′ of the breakpoint → W20's test had **no** power
- (s) probe straddles the exon-6/7 boundary → partial power
- (c) probe not locatable in committed data → **undeterminable offline**

---

## Result

### 1. What the probe map actually records for TAF15 — quoted

`research/modalities/emc-fourth-cohort-quant.json`, `probe_map` block, verbatim:

```json
"probe_map": {
  "state": "read",
  "sources": [
   { "kind": "cdna",
     "url": "https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz",
     "state": "read", "n_transcripts": 465769, "n_bases_scanned": 1276790359 },
   { "kind": "ncrna",
     "url": "https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/ncrna/Homo_sapiens.GRCh38.ncrna.fa.gz",
     "state": "read", "n_transcripts": 203778, "n_bases_scanned": 201604096 }
  ],
  "read_length_nt": 50,
  "best_core_length_nt": 34,
  "n_probes_offered": 1645,
  "n_probes_assigned_to_one_gene": 906,
  "n_probes_matching_several_genes": 77,
  "n_probes_unassigned": 662,
  "⚠ unassigned_means": "no verbatim match to a human cDNA or ncRNA transcript at any core length tried. That is a statement about this matcher, NOT about the probe: a probe spanning a junction the sequence set does not contain, or carrying non-target bases, is unassigned here and is still a real probe.",
  ...
}
```

W20's characterisation is exactly right: the matching method is **verbatim cDNA/ncRNA substring matching at a core length**, the assignment is **gene-level only**, and **no breakpoint-relative or transcript-coordinate position is stored**. The module's own caveat is honest about the same gap.

**But the probe *sequence itself* is committed**, in the companion table the same module wrote (`"probe_counts_written_to": "emc-fourth-cohort-probe-counts.tsv"`, `probe_counts_sha256: c689e0fd…`, 213,007 data rows). Exactly **one** of those rows is assigned to `TAF15`:

```
probe_sequence	assigned_gene	SRR35940646 …
CTTCTGTCTCCTCCATAGCCTCCTCGATCTCCTCCATAACCTCCTCGATC	TAF15	1298	3585	1489	1563	2603	276	204	785	701	3028	783	429
```

Those twelve values are, run-for-run, the raw *TAF15* counts W20 reported (`TAF15 raw counts pos: [1298, 3585, 1563, 2603, 276, 204, 785, 3028]`, `neg: [1489, 701, 783, 429]`). **So this single 50-nt oligonucleotide is the entire basis of W20's primary endpoint** — there is no second probe to average over.

### 2. The TAF15 breakpoint from committed evidence

`research/modalities/nr4a3-fusion-junction-atlas.json`, verbatim:

```json
{
  "junction_label": "TAF15_e6__NR4A3_e3",
  "donor_symbol": "TAF15",
  "donor_exon_end": 6,
  "acceptor_exon_start": 3,
  "seam_mRNA": "ACCACACACAAG|ATATGCCCTGCG",
  "nr4a3_first_residue": 1,
  "chimeric_protein_length": 788,
  ...
}
```

Corroborated independently in `research/modalities/emc-fet-construct-designs.json`, quoted from a review-seat record that reproduces it verbatim: `constructs[3] = 'TAF15::NR4A3 — TAF15 exon 6 :: NR4A3 exon 3'`, with `five_prime_FET_half` retaining **`TAF15(1-161)`**. And on why exon 6 is the reported donor at all, from `PUB-ASO-6127da1ac1a2d912b4a9a5f93de6d0f0e98d372c-seat-citations-and-instruments.json`, quoting the primary source: *"For USZ22-EMC2; TAF15 … exon 6 for TAF15 on chr17 and exon 2 from NR4A3 on chr9 involved (D)"*, and from another seat, `PMID 12378528` contributing *"3/3 TAF15 exon 6"*. TAF15 exon 6 is the repository's recorded donor exon, and the ASO manuscript names it as one of the two most frequently reported EMC breakpoints.

### 3. The join — the probe placed against the breakpoint

| Quantity | Value | Row type |
|---|---|---|
| TAF15 transcript used | `ENST00000605844` / `ENSP00000474096`, 2,162 nt cDNA, 1,779 nt CDS, 592 aa, 16 exons, + strand | PRIMARY (committed) |
| Probe located in TAF15 cDNA | **as the reverse complement**, 0-based 1616–1665 → **1-based 1617–1666** | PRIMARY (computed) |
| Occurrences of that 50-mer in the TAF15 cDNA | **1** (unique) | PRIMARY (computed) |
| Same probe in the committed pre-mRNA | 0-based 35346–35395 of 37,759 nt (independent coordinate system, same answer) | PRIMARY (computed) |
| Exon containing the probe | **exon 15** (`ENSE00003641314`, cDNA 1264–1825) | PRIMARY (computed) |
| **TAF15 exon 6 end, cDNA 1-based** | **570** | PRIMARY (computed, two independent routes) |
| Distance from breakpoint to probe start | **+1,047 nt, 3′** | PRIMARY (computed) |

The exon-6 endpoint is confirmed twice, by routes that do not share an assumption:

1. **Cumulative exon lengths** from the committed exon record: `[93, 40, 52, 85, 106, 194, …]` → cumulative cDNA ends `[93, 133, 185, 270, 376, **570**, 691, …]`. The exon lengths sum to 2,162, exactly `len(cdna)` — an internal consistency check that passed.
2. **The fusion atlas seam.** The retained-donor half of `seam_mRNA` is `ACCACACACAAG`. Searching that 12-mer in the committed TAF15 cDNA places its last base at 1-based position **570** — identical. The atlas's breakpoint and the transcript's exon table agree to the nucleotide.

A third, protein-level check also agrees: cumulative coding nt through exon 6 = 484, i.e. 161.33 codons; exon 7's `first_protein_residue` is 162; `chimeric_protein_length` 788 minus NR4A3's committed 626 aa = **162** TAF15 residues; and `emc-fet-construct-designs.json` independently records the retained half as **`TAF15(1-161)`**. Four records, one number.

### 4. Robustness of the verdict

- **The verdict does not depend on which TAF15 donor exon is used.** The probe starts at 1617. Exon 14 — the most 3′ TAF15 donor exon appearing in any committed junction label — ends at cDNA 1263. The probe is 3′ of **every** TAF15 donor exon end recorded anywhere in the committed junction files (exons 1–14; the atlas's combinatorial enumeration also emits e15/e16 labels, which are downstream of the probe but are not reported breakpoints).
- **No part of the probe cross-matches the retained 5′ region.** No 12-, 15-, 20-, 25- or 30-mer of the probe target occurs anywhere in TAF15 cDNA 1–570. There is no partial-signal leak route.
- **Sequence identity of the probe.** Its reverse complement is `GATCGAGGAGGTTATGGAGGAGATCGAGGAGGCTATGGAGGAGACAGAAG`, translating in frame to `DRGGYGGDRGGYGGDR` — an RGG/GY-repeat block in the C-terminal half of TAF15. (I note honestly that `protein.find()` returns residue 497 while the CDS arithmetic gives 511: the peptide occurs three times, at 497, 504 and 511, because the region is a tandem repeat. The **nucleotide** match is unique at 1617, so the placement is unaffected — but this is exactly the kind of repeat region where a protein-level argument alone would have been unsafe, and I am recording that the nucleotide route is the load-bearing one.)

### 5. Consequence for W20's result — **form (b)**

**The TempO-Seq *TAF15* probe lies 3′ of the TAF15::NR4A3 breakpoint, by 1,047 nucleotides, in exon 15 of a 16-exon transcript whose fusion retains only exons 1–6.**

The `TAF15::NR4A3` chimeric mRNA contains **none** of the sequence this probe targets. W20's primary endpoint therefore could not, by construction, have detected the fusion allele's transcript at any expression level. **W20's test of "is *TAF15* elevated in EWSR1-FISH-negative EMC because the fusion allele adds partner-side transcript?" had no power.**

Per W20's own pre-stated conditional — *"If it lies 3′, the fusion allele contributes nothing to the probe and the test had no power by construction"* — **the correct label for that null is UNDECIDED, not REFUTED.** I am changing W20's verdict label, and under my instruction to preserve it "unless your evidence changes it, in which case say so precisely", I say so here precisely: the δ, the p-values, the permutation enumeration, the panel percentiles, the *FUS* control and the arithmetic are all **unchanged and correct as computed**; what changes is only the inferential label attached to the primary endpoint, from REFUTED to **UNDECIDED — no power by construction**.

Everything else in W20's report stands, including its two independent PRIMARY findings (the first expression reading of PRJNA1357027 against its per-sample FISH labels was performed; the *FUS* negative control behaved correctly), its global-shift robustness result, and its GSE243553 inaccessibility statement.

### 6. One consequence I will not overstate

A 3′ probe is not merely blind to the fusion — it has a **prediction of its own, and it points the other way**. In a fusion-positive tumour, one *TAF15* allele's transcription is diverted into a chimeric mRNA that stops at exon 6, so a 3′ probe should read **less** full-length *TAF15* from that allele, not more. W20 observed δ = −0.83 (lower in the EWSR1-negative, TAF15::NR4A3-enriched arm), which is **directionally consistent** with that.

I am **not** converting this into a finding. It is post-hoc, it was not pre-specified by anyone, it rests on n = 4 vs 8 in FFPE material spanning 23 collection years, W20 already documented a mild global negative arm shift (panel-wide δ mean −0.097) against which *TAF15* sits at only z = −1.28, the negative arm is a **mixture of unknown composition** (EWSR1-FISH-negative ≠ TAF15-fusion-positive), and one allele of two remains intact so the maximum expected effect is bounded well below 1 log2 unit. Classify it strictly as **ASSOCIATION, hypothesis-generating, not validated** — and note that it is now a *pre-specifiable* hypothesis for a future test, which is the useful part.

The single route by which a 3′ TAF15 probe could carry any fusion-related signal is a **reciprocal `NR4A3::TAF15` transcript** from the derivative chromosome. Nothing in this cohort measures that, no committed artifact establishes it is expressed in EMC, and I make no claim about it; I name it only to bound the "no power" statement honestly rather than absolutely.

**PREDICTION rows: none.** This report contains no model output and no extrapolation.

---

## Validation evidence

**RUN — command 1** (budget gate, before and after):
```
df -h /
```
→ `/dev/vda  252G  14G used  24G avail  36%` — exit 0. ≥10 GiB satisfied. **Nothing was downloaded at any point; no network request was made.**

**RUN — command 2** (the decisive join): `/tmp/claude-0/w20c/probe_position.py`
```
cd /tmp/claude-0/w20c && python3 --version && python3 probe_position.py; echo "EXIT=$?"
```
Environment: `Python 3.11.15`, stdlib only. Verbatim output (abridged only by eliding the 16-line exon dump, reproduced in the Result table):
```
TAF15-assigned probe rows: 1
probe sequence used: CTTCTGTCTCCTCCATAGCCTCCTCGATCTCCTCCATAACCTCCTCGATC len=50
reverse complement  : GATCGAGGAGGTTATGGAGGAGATCGAGGAGGCTATGGAGGAGACAGAAG

TAF15 transcript: ENST00000605844 translation: ENSP00000474096 strand: 1 utr5_len: 86
cdna_nt: 2162  cds_nt: 1779  protein_aa: 592  n_exons: 16
pre-mRNA record: ENST00000605844 premrna_nt: 37759 n_exons: 16 exonic_nt: 2162 strand: 1
  MATCH  cdna     antisense(rc)  at 0-based 1616 .. 1665
  MATCH  cds      antisense(rc)  at 0-based 1530 .. 1579
  MATCH  premrna  antisense(rc)  at 0-based 35346 .. 35395
...
exon lengths (nt): [93, 40, 52, 85, 106, 194, 121, 35, 33, 110, 130, 93, 82, 89, 562, 337]
cumulative cDNA end of each exon (1-based): [93, 133, 185, 270, 376, 570, 691, 726, 759, 869, 999, 1092, 1174, 1263, 1825, 2162]
sum of exon lengths: 2162  vs len(cdna): 2162  EQUAL
TAF15 exon 6 ends at cDNA 1-based position: 570

seam_mRNA for TAF15_e6__NR4A3_e3: ACCACACACAAG|ATATGCCCTGCG
last 12 nt of the retained TAF15 donor: ACCACACACAAG
  found in committed TAF15 cDNA at 1-based end position: 570
  agrees with exon-6 cumulative end? True

---- PRE-SPECIFIED VERDICT ----
probe occupies TAF15 cDNA 1-based 1617..1666; exon-6 end = 570
VERDICT: (b) PROBE IS 3' OF THE BREAKPOINT -> W20's test had NO POWER
EXIT=0
```

(An earlier invocation of the same script exited 1 on a `KeyError: 'end'` — my fallback branch guessed exon-record field names before I had read them. I fixed the parse to use the record's real fields (`exon_length_nt`, `cdna_start_0based`, `cdna_end_exclusive`) and re-ran. No decision logic was touched between the two runs; I am recording the failed exit rather than presenting only the clean one.)

**RUN — command 3** (confirmations): `/tmp/claude-0/w20c/confirm.py` — `EXIT=0`
```
probe overlaps exon 15 (ENSE00003641314) cDNA 1264..1825
probe in CDS 0-based: 1530 -> codons 511 .. 527
in-frame translation of probe target: DRGGYGGDRGGYGGDR
cumulative coding nt through exon 6: 484 => TAF15 residues retained ~ 161.33
exon 7 first_protein_residue: 162

TAF15 donor exons recorded in committed junction files: [1..16]
  TAF15 exon 6 ends at cDNA 570; probe starts at 1617 -> probe is 3' of breakpoint
  TAF15 exon 14 ends at cDNA 1263; probe starts at 1617 -> probe is 3' of breakpoint
  any 12/15/20/25/30-mer of probe target present in retained TAF15 cDNA 1..570? False (all)
```
plus, run inline:
```
occurrences of probe target in TAF15 cDNA: [1617]        # unique
occurrences of peptide in TAF15 protein (1-based): [497, 504, 511]   # repeat-degenerate
```

**RUN — command 4** (write-isolation check):
```
git rev-parse HEAD ; git status --porcelain
```
→ HEAD `103ff76f1d66426420c56a4d49752eb84f5f5c39`; the only untracked paths are other workers' collected reports. **No path authored by me appears anywhere in the tree.** My two scripts are at `/tmp/claude-0/w20c/probe_position.py` and `/tmp/claude-0/w20c/confirm.py`.

**PROPOSED (NOT RUN):**
- Any confirmation against the vendor's own published TempO-Seq probe manifest — the authoritative annotation. **Not run:** it is behind the same egress denial, and I did not attempt any archive route.
- Any measurement of reciprocal `NR4A3::TAF15` transcript. **Not run**, no data.
- `scripts/preflight.sh` — **not run**, per COMMON-BRIEF §1; my dispatch did not instruct it and I wrote nothing to the tree for it to gate.
- **No reagent of any kind was designed, proposed or scored.** This was probe-position bookkeeping on an existing commercial panel.

---

## Limitations

- **This places the probe on one transcript, `ENST00000605844`.** That is the transcript the repository's own fusion atlas and construct inputs use for TAF15, and both the exon table and the atlas seam agree on it, so the join is internally coherent. It is not a check against the vendor's manifest, and a probe designed against a different TAF15 isoform's numbering would still land at the same *sequence*, which is what I matched — but I did not verify isoform choice independently.
- **The probe assignment is the parent module's, not mine.** I inherited `assigned_gene = TAF15` from `emc-fourth-cohort-quant.json`. My finding is conditional on that assignment being right; I did confirm the sequence is a unique exact match inside the TAF15 cDNA, which is consistent with it, but I did not re-screen it against the whole transcriptome for a better match elsewhere.
- **"No power" is a construction argument, not a measurement of zero.** It states that the chimeric mRNA contains none of the probe's target sequence. It does not exclude a reciprocal-transcript route, which is unmeasured here.
- **Nothing in this report bears on** efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness of any agent, target or gene, and no such quantity was computed. Runs are not samples and samples are not people.
- **What this does not rescue.** Relabelling W20's endpoint UNDECIDED does not make the fusion-partner model supported. It restores it to untested by this instrument. The panel also lacks `NR4A3`, `EWSR1`, `TCF12`, `TFG` entirely (W20's finding), so this cohort cannot ask the fusion question in any form with the probes it has.

---

## Stop condition

**Condition set:** a documented probe-position verdict in form (a), (b) or (c), with quoted committed evidence.

**MET, in form (b).** The probe lies **3′** of the TAF15 breakpoint — cDNA 1617–1666 against an exon-6 end at 570, a 1,047-nt gap, in exon 15 of a fusion that retains exons 1–6. The verdict was emitted by a script whose decision rule was fixed before execution, the exon-6 endpoint is confirmed by two independent committed routes that agree to the nucleotide, and the placement is invariant across every TAF15 donor exon recorded in the repository. **W20's null must be relabelled UNDECIDED (no power by construction), not REFUTED.** Its computed values, its *FUS* control, its robustness analysis and its GSE243553 statement are unaffected and stand as written.

---

## Tool-call and wall-clock count actually used

**Tool calls: 13.** **Wall clock: approximately 15 minutes**, ending 02:14:57 UTC. This is an estimate, not a measurement — I failed to run `date -u` at the start of the run and I am not going to reconstruct a start time I did not record. Both counts are inside the ~40-call / ~40-minute self-observed target. No compute was left running; nothing is in flight.

---

## Next concrete action

**One successor task for this lane:** re-ask W20's question with an instrument that can answer it. The `TAF15::NR4A3` chimeric mRNA is detectable in this panel only by a probe whose target lies within TAF15 cDNA 1–570 (exons 1–6). The concrete first step is a **probe-inventory check that needs no network at all**: take the 1,645 probe sequences already committed in `emc-fourth-cohort-probe-counts.tsv` — including the **662 currently `unassigned`**, which the module's own caveat says may be real junction-spanning probes the cDNA matcher could not place — and search each against TAF15 cDNA 1–570 and against the six committed fusion-partner transcripts' retained 5′ regions. If any probe lands 5′ of a recorded breakpoint, W20's test becomes answerable on retained data with a properly powered endpoint; if none does, that is a clean, bounded statement that **this panel cannot address fusion-partner readthrough for any EMC fusion**, which closes the question honestly and saves the next worker the attempt. Either outcome is a finite result reachable with committed files and stdlib Python, and it is the natural continuation of the bookkeeping I did for one probe.

*Secondary:* W20's own handover (resolve the actual fusion partner in the four EWSR1-FISH-negative specimens by a fusion caller over the public FASTQs) remains the right eventual move, but it is now **strictly downstream** of the above — with a 3′-only TAF15 probe, better labels would still be joined to an endpoint that cannot see the fusion.

result: The TempO-Seq TAF15 probe lies 3′ of the TAF15::NR4A3 breakpoint (TAF15 cDNA 1617–1666, exon 15; exon-6 end at 570, confirmed independently by the exon table and the fusion atlas seam 12-mer, gap 1,047 nt), so W20's primary endpoint could not detect the chimeric transcript — verdict form (b): W20's null had no power by construction and must be relabelled UNDECIDED rather than REFUTED, with all of its computed values, its FUS control and its other findings unchanged.
