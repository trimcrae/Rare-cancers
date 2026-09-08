> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Tree restored: my report file and the empty `reports/` directory I created are both removed; `git status` shows only the coordinator's own untracked campaign directory. Sanity check done — every claim below traces to a PubMed record I retrieved or a command I ran, and the two blocked routes are recorded rather than worked around. Full report follows as my response body, per the corrected brief.

---

# W02 — Public EMC single-cell / spatial / tumour-microenvironment resources, and transfer limits

## Worker

- **Worker ID:** W02, OPUS-CAPACITY-CAMPAIGN-20260908
- **Lane:** Lane 2 — Public EMC single-cell / spatial / tumour-microenvironment resources, with explicit transfer limits if EMC is absent.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`) running as Claude Code in the Anthropic Cloud remote environment. **This is a self-report and must not be treated as an observed fact.** There is **no `ANTHROPIC_MODEL` variable set in this environment** (see env dump below), so the served model is not confirmable from within this session. The coordinator should extract the actual per-child runtime model from the transcript.
- **Frozen read commit:** `92abbcb905cacf07f14b238db50d1b98f6590374`
- **Write isolation:** I initially wrote my report to the dispatched repository path before the coordinator's correction arrived. On receiving it I deleted that file and the empty `reports/` directory I had created (`rm -f` exit 0, `rmdir` exit 0). `git status --porcelain` now shows only `?? research/autonomy/opus-capacity-campaign-20260908/` — the coordinator's own untracked directory. **I made no other write anywhere in the tree, and no git operation of any kind.**

`date -u` at start: `Tue Sep  8 01:39 UTC 2026` (first tool call). At end: `Tue Sep  8 01:56:02 UTC 2026`.

Literal output of the required env command (proxy/`no_proxy`/`JAVA_TOOL_OPTIONS` noise elided — the elision is declared here rather than made silently):

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
SESSION_INGRESS_URL=https://api.anthropic.com
```

**No `ANTHROPIC_MODEL` key is present.** Model identity is therefore UNKNOWN from the environment.

---

## Question

**Does any public single-cell, single-nucleus, or spatial-transcriptomic dataset contain extraskeletal myxoid chondrosarcoma (EMC) tissue? If none does, which sarcoma single-cell/spatial atlases exist, and what are the precise limits of transferring anything from them to EMC?**

This is open rather than closed because the repository repeatedly *requests* a compartment-resolved EMC measurement as the thing that would unblock several lanes, but no tracked file records a systematic search for whether one exists. The requests are stated as needs; the presence/absence question behind them has never been answered in the corpus.

---

## Prior-work check

Commands run, verbatim:

```
rg -n -i "single.cell|scRNA|snRNA|spatial|microenvironment|deconvolution" research/ --glob '!.git' | head -60
git ls-files | rg -i "single|spatial"
rg -n -i "single.cell|scRNA|snRNA|spatial transcriptom|Visium|deconvolution" research/ systems/graph/ --glob '!.git' -C0
```

What they showed:

- `git ls-files | rg -i "single|spatial"` returned only **three** files, none of them single-cell data or analysis: `research/modalities/single_slot_identity.py`, `research/modalities/tests/test_single_slot_identity.py`, `systems/tests/test_convergence_is_a_repeated_look_not_a_single_test.py`. All three are lexical collisions on the word "single". **The repository holds no single-cell or spatial dataset, loader, or analysis of any kind.**
- The corpus contains the *ask*, repeatedly, in four independent places:
  - `research/manuscripts/surface-targets/surface-targets-graph-records.json` — requires "a compartment-resolved (single-cell or spatial) or protein-level measurement in EMC", and states: *"Bulk archival tissue cannot separate the tumour compartment from the stroma, so neither the negative nor a positive would attribute the signal. A single-cell or spatial EMC dataset is what would."*
  - `research/manuscripts/surface-targets/emc-surface-target-landscape.md:413,506` — same ask.
  - `research/manuscripts/nr4a3-program-map.md:3708,3778` (Q16 / row 26) — the NR4A2-sparing question is closed on bulk and reopenable only by "single-cell or region-resolved expression", because "bulk averages dilute a small nucleus".
  - `research/manuscripts/surface-targets/ofcs-var2csa-lane.md:304` — the retained EMC series are "**bulk tumour-tissue expression arrays** — neither is sorted or single-cell".
- `systems/views/L1-st-microenv.md` (`DOC-VIEW-ST-MICROENV`) records the matching negative from the other direction: the surface-address screen "ranks tumour-cell monoculture transcripts, so it has no stromal compartment in it … its silence about a matrix target is an absent reading rather than a reading of absence."

**Closed items confirmed and not replayed.** From `CLOSED-WORK.md`: I did not re-derive `GSE4303` or `GSE28866` (heavily retained; rediscovery is not new data), did not touch the ASO/NAT or tissue-RNA deliverables, did not recreate the restricted NR4A Perspective review, did not substitute sources for the unrecovered Pazopanib/Sunitinib/Wagner/CTARC records, and did not replay any route recorded as denied. `GSE243553` was already retained and is used here only as a *limit* on transfer, never presented as new.

**Verdict on novelty:** genuinely open. The corpus states the need four times and never tests whether the resource exists.

---

## Method / inputs

| Tool | Version / route | Use |
|---|---|---|
| `rg`, `git ls-files` | repo checkout at frozen commit | prior-work check |
| PubMed MCP (`search_articles`, `get_article_metadata`) | NCBI E-utilities via MCP server | literature census |
| `WebSearch` | US index, Sept 2026 | portal/GEO discovery (secondary route) |
| `WebFetch` | agent egress proxy | full-text attempt — **blocked**, see Validation |
| `curl` → NCBI E-utilities `db=gds` | direct HTTPS via proxy | GEO DataSets query — **blocked**, see Validation |

All literature records were retrieved from **PubMed**; DOIs are given as links per the PubMed MCP attribution requirement. No code was authored, so no `/tmp/claude-0/` execution was required.

---

## Result

### 5.1 — Does any public single-cell / single-nucleus / spatial dataset contain EMC tissue?

**Verdict: NO EMC-containing single-cell, single-nucleus, or spatial-transcriptomic dataset was retrieved.** Scope bounded precisely in Limitations.

The PubMed query `extraskeletal myxoid chondrosarcoma AND (single-cell OR single cell RNA OR spatial transcriptomics OR scRNA-seq)` returned **46 records**. The returned `query_translation` shows why that count is misleading: PubMed expanded "single cell RNA" into the independent terms `"single"[All Fields] AND "cell"[All Fields] AND "rna"[All Fields]`, so any EMC paper containing the ordinary words "single", "cell" and "RNA" matches. I inspected the **7 most recent / highest-relevance records** in full metadata. **Zero use single-cell, single-nucleus, or spatial transcriptomics.**

| PMID | Modality actually used | EMC present? | Row |
|---|---|---|---|
| 41644428 | IHC + FISH + NGS, 16 EMC cases | yes, but **not** sc/spatial | PRIMARY |
| 38678326 | FISH break-apart + NGS, 5 EMC among 205 | yes, but **not** sc/spatial | PRIMARY |
| 38557577 | FDG PET/CT + MRI + FISH, 1 case | yes, but **not** sc/spatial | PRIMARY |
| 38447752 | bulk expression **microarray** + RNA **chromogenic ISH**, 25 EMC | yes, but **not** sc/spatial | PRIMARY |
| 37705036 | IHC + FISH, 1 gingival case | yes, but **not** sc/spatial | PRIMARY |
| 36948401 | RNA exome sequencing (bulk) + FISH, 58 EMC | yes, but **not** sc/spatial | PRIMARY |
| 35650682 | GRM1 IHC, EMC as negative comparator only | EMC only as mimic control | PRIMARY |

Note on 38447752 (Dulken/Charville, *Mod Pathol*, [DOI](https://doi.org/10.1016/j.modpat.2024.100464)) — the CHRNA6 paper, the closest thing to a compartment-resolved EMC measurement that exists. It is **RNA chromogenic ISH on tissue sections**: genuinely spatial in the microscopy sense, single-gene, and **not** a spatial-transcriptomic assay. It resolves *one* transcript in space, not a transcriptome. Row **PRIMARY**; correct citation for "CHRNA6 is expressed in EMC tumour cells in situ", not a substitute for spatial transcriptomics.

**The decisive negative.** The most recent EMC tumour-microenvironment study in existence — Chaiboonchoe *et al.*, *PeerJ* 2026, PMID 42465974, [DOI](https://doi.org/10.7717/peerj.21497) — had to work entirely without single-cell data:

- n = **12** molecularly confirmed EMC, **archival FFPE**, assayed by **TempO-Seq** (targeted whole-transcriptome, **bulk**).
- Cross-validation used **31 external EMC cases across public microarray and NGS datasets** — again all bulk. This is an independent, published census of what public EMC transcriptomic data exists, and it contains **no single-cell or spatial entry**.
- Immune infiltration was "estimated **computationally**" (bulk deconvolution), "spatially validated *via* **multiplex immunofluorescence (mIF) on two representative specimens**".
- Authors' own stated limits: *"All mIF comparisons are within-specimen region of interest (ROI) analyses and should be interpreted as hypothesis-generating"*; *"Given the small cohort and model overfitting, these findings are exploratory."*

That a 2026 paper whose explicit subject is the EMC immune microenvironment reached for bulk deconvolution plus n=2 mIF is the strongest available evidence that no EMC single-cell or spatial dataset was available to them. Row: **PRIMARY**.

### 5.2 — Sarcoma single-cell / spatial atlases that do exist, with exact histology

Histologies quoted as the source states them.

| Resource | Modality / platform | n samples | Exact histologies as stated | EMC? | Row |
|---|---|---|---|---|---|
| Su 2024, *Commun Biol*, PMID 38267611, [DOI](https://doi.org/10.1038/s42003-024-05790-w) | scRNA-seq | "11 primary cartilage tumours and controls" | "conventional central chondrosarcoma (CCCS)"; benign chondroid lesions; controls | **ABSENT** | PRIMARY |
| DeMartino 2023, *Nat Commun*, PMID 37244912, [DOI](https://doi.org/10.1038/s41467-023-38886-8) | single-cell mRNA-seq | UNKNOWN (not in abstract) | "paediatric rhabdomyosarcoma (RMS)", fusion-positive/negative | **ABSENT** | PRIMARY |
| Ge 2023, *Cancer Immunol Immunother*, PMID 37938367, [DOI](https://doi.org/10.1007/s00262-023-03577-2) | scRNA-seq | primary + satellite + LN met (exact n UNKNOWN) | "dermatofibrosarcoma protuberans (DFSP)", metastatic | **ABSENT** | PRIMARY |
| Li 2024, *Transl Pediatr*, PMID 38715675, [DOI](https://doi.org/10.21037/tp-24-66) | scRNA-seq, fresh tissue | 4 patients | "infantile fibrosarcoma (IFS)" | **ABSENT** | PRIMARY |
| Feng 2024, *Oral Dis*, PMID 39639424, [DOI](https://doi.org/10.1111/odi.15214) | single-cell transcriptomics + CIBERSORT + flow + IHC | UNKNOWN | "head and neck rhabdomyosarcoma" | **ABSENT** | PRIMARY |
| Lou 2025, *Front Oncol*, PMID 40963856, [DOI](https://doi.org/10.3389/fonc.2025.1604413) | **reuses** public GEO scRNA-seq + TCGA bulk | UNKNOWN (re-analysis) | "leiomyosarcoma (LMS)" | **ABSENT** | SECONDARY |
| Bergsma 2025, *Eur J Cancer*, PMID 40857838, [DOI](https://doi.org/10.1016/j.ejca.2025.115708) | systematic review integrating IHC + sc/snRNA-seq | 26 sc/snSeq studies, **272 tumour samples**; 47 IHC studies, 2,187 samples | "35 unique pediatric tumor types"; soft-tissue sarcomas as a group | **ABSENT** (no EMC named; EMC is not paediatric) | SECONDARY |
| Subramanian 2024, *Nat Cancer*, PMID 38429415, [DOI](https://doi.org/10.1038/s43018-024-00743-y) | **EcoTyper on BULK transcriptomes** — *not* single-cell | large, exact n UNKNOWN | "soft tissue sarcomas"; 23 cell states, 3 ecotypes | **ABSENT / UNKNOWN** | PRIMARY |
| Menyailo 2024, *Cancer Gene Ther*, PMID 39582085, [DOI](https://doi.org/10.1038/s41417-024-00856-7) | review of STS sc + spatial | n/a | "different types of STS" — subtype list is in full text, **EGRESS_BLOCKED** | **UNKNOWN** | UNKNOWN |
| ScPCA Portal (`SCPCP000017`) | 10x droplet sc/snRNA-seq | ">700 samples, 55 pediatric cancer types" | paediatric sarcoma; aim stated as "pediatric osteosarcoma" | **ABSENT** (paediatric scope) | SECONDARY — web search, portal metadata not directly verified |
| GEO `GSE243553` (already retained; PMID 39048711) | Spear-ATAC, pooled single-cell **ATAC**, HEK293T | 116-member variant library | HEK293T carrying EWSR1-, TAF15-, TCF12-, TFG-NR4A3 | **fusion present, tissue ABSENT** | PRIMARY (retained) |

Access status and licence were **not** individually verified — the confirming routes were blocked (see Validation). Recorded **UNKNOWN** rather than asserted. Histology columns are quoted from abstracts, not per-sample metadata tables.

**Note on Subramanian 2024, because it is the resource most likely to be misused here.** Its "23 sarcoma-specific cell states" look attractive as a transfer source, but the abstract is explicit that they were identified "on a large scale **using bulk transcriptomes** with clinical annotations", precisely because "characterization … has proven difficult using fixed clinical specimens". These are deconvolution-derived states, not observed single cells. Transferring them to EMC would be a deconvolution of a deconvolution.

### 5.3 — CORE DELIVERABLE: itemised transfer-limit statement

EMC is absent from every retrieved single-cell and spatial resource. The following inferences **cannot** be transferred to EMC. Each names the specific biological or sampling reason, and what would remove it.

**(T1) Myxoid stromal composition — NOT transferable. Two independent reasons.**
*Biological:* the abundant chondromyxoid matrix is EMC's defining phenotype (PMID 41644428: "pale-blue myxoid or chondromyxoid matrix", 14/16 cases). No donor atlas contains it. The nearest myxoid tumour, myxoid liposarcoma, is driven by **FUS::DDIT3** in an **adipocytic** lineage — different fusion, different cell of origin, and a matrix that is a different product. Naming both "myxoid" is a histological descriptor, not evidence of a shared stromal program.
*Sampling:* matrix abundance is not neutral background, it is a **dissociation bias**. A sulfated-proteoglycan-rich ECM changes which cells survive enzymatic dissociation, so cell-type proportions recovered from EMC would differ systematically from those recovered from the low-matrix tumours (RMS, DFSP, IFS, CCCS) supplying the donor atlases. No shared protocol arm exists to calibrate that difference.
*What removes it:* EMC specimens processed by **single-nucleus** RNA-seq (far less sensitive to ECM-driven dissociation bias, and compatible with the frozen/archival reality of a tumour this rare) on the same platform and protocol as the comparator.

**(T2) Immune infiltration fraction — NOT transferable, and EMC has no valid target value either.**
The three variables setting an infiltration fraction — anatomic site, prior treatment, specimen processing (fresh dissociation vs. single-nucleus vs. FFPE) — differ across every donor atlas and are unmatched to EMC. Bergsma 2025 makes the error's direction concrete: soft-tissue sarcomas are "relatively immune-infiltrated, T cell-rich" **within paediatric tumours**, while "compared to adult tumours, (CD8) T cell infiltration and macrophage infiltration was **low** for all pediatric tumor types." A fraction imported from a paediatric sarcoma atlas therefore carries a known, signed, uncalibrated offset. Separately, EMC's own only measurement cannot serve as a validation target: bulk deconvolution on n=12 plus mIF on **n=2**, within-specimen ROI, author-labelled hypothesis-generating.
*What removes it:* ≥1 EMC cohort with the same assay and processing arm as its comparator, treatment status and site recorded per specimen.

**(T3) NR4A3-target cell states — NOT transferable. The hardest of the four.**
A "cell state" is a transcriptional program. Transferring an *NR4A3-driven* state requires a donor that **expresses an NR4A3 fusion**. **No donor atlas in §5.2 does.** The one public resource carrying NR4A3 fusions, `GSE243553`, cannot supply one for three stacked reasons: it measures **accessibility, not expression**; it is **HEK293T**, not EMC; and — decisive for this lane — a transfected cell line has **no microenvironment at all**, containing zero stromal and zero immune compartment, so it is structurally incapable of yielding a TME cell state. This compounds a limit the repository already holds: no experiment has measured where an NR4A3 fusion binds in EMC chromatin, so the target set that would *define* the state is itself unmeasured.
*What removes it:* fusion occupancy measured in EMC chromatin, plus EMC expression at single-cell resolution. Neither exists.

**(T4) Malignant-vs-stroma cell assignment in EMC — NOT reliably transferable.**
Reference-based label transfer needs a lineage anchor, and EMC's cell of origin is unresolved: despite the name it is not a cartilaginous tumour, and its marker profile leans neuroendocrine (PMID 41644428: positive for Syn, INSM-1, CD117, NSE, **negative for S-100** in that series; PMID 38447752 describes "features of both cartilaginous and neuroendocrine differentiation"). Mapping EMC malignant cells onto a chondrosarcoma reference (Su 2024) would be anchored on the tumour's *name*, not its lineage. The standard fallback — inferCNV, used by Ge 2023 and Li 2024 — is expected to be weak in EMC, because EMC is driven by a **balanced translocation** with a comparatively quiet copy-number genome, and inferCNV separates malignant from stromal cells *by* copy-number burden. Row: **PREDICTION**, on the stated basis (balanced-translocation biology + how inferCNV works); I did not measure EMC copy-number burden, and it should be checked before being relied on.
*What removes it:* a genotype-anchored malignant-cell call — the EWSR1::NR4A3 junction read directly per cell — which does not depend on CNV at all.

**(T5) Why a generic caveat is not enough.** "Findings from other sarcomas may not generalise to EMC" is true and useless. The four items are not interchangeable: T1, T2 and T4 would be fixed by *sampling* EMC (a cohort and a matched protocol), whereas **T3 would not** — T3 needs a chromatin experiment never performed in any laboratory on any EMC material. Anyone funding EMC single-cell generation should understand it resolves T1, T2, T4 and leaves T3 standing.

**Missing evidence, itemised:** (i) any EMC specimen assayed by sc/snRNA-seq; (ii) any EMC specimen assayed by spatial transcriptomics (Visium/Xenium/CosMx or equivalent); (iii) NR4A3-fusion occupancy in EMC chromatin; (iv) an EMC cell-of-origin anchor; (v) per-sample processing metadata for donor atlases sufficient to model the batch/protocol offset.

---

## Validation evidence

### RUN

| # | Command | Environment | Exit | Key output |
|---|---|---|---|---|
| 1 | `git ls-files \| rg -i "single\|spatial"` | repo @ `92abbcb` | 0 | 3 files, all lexical collisions; **no single-cell/spatial data or code** |
| 2 | `rg -n -i "single.cell\|scRNA\|...\|deconvolution" research/ --glob '!.git'` | same | 0 | 55.9 KB; EMC-relevant hits are all *requests* for such data |
| 3 | PubMed `search_articles`: EMC ∩ (sc/spatial) | MCP | ok | `total_count: 46`; `query_translation` reveals `"single" AND "cell" AND "rna"` expansion |
| 4 | PubMed `get_article_metadata` ×7 (EMC hits) | MCP | ok | 0/7 single-cell or spatial |
| 5 | PubMed `search_articles`: sarcoma sc atlas TME | MCP | ok | `total_count: 11` |
| 6 | PubMed `get_article_metadata` ×8 (atlases) | MCP | ok | histologies tabulated §5.2 |
| 7 | PubMed: `(myxoid liposarcoma OR chondrosarcoma OR synovial sarcoma) AND (scRNA OR spatial) AND atlas` | MCP | ok | `total_count: **1**` — only PMID 38267611 (CCCS) |
| 8 | PubMed: myxoid liposarcoma scRNA-seq TME FUS-DDIT3 | MCP | ok | `total_count: **0**` |
| 9 | PubMed `get_article_metadata` (42465974, 38267611) | MCP | ok | Chaiboonchoe modality + author limits quoted §5.1 |
| 10 | `WebSearch` ×3 (GEO, CELLxGENE/SCP, STS review) | US index | ok | surfaced PMID 42465974, ScPCA; no EMC sc/spatial resource |
| 11 | `rm -f <my report>`; `rmdir reports` | repo | 0; 0 | write isolation restored; `git status` clean of my writes |

Item 8 is a genuine and useful negative: the tumour most often invoked as EMC's myxoid analogue has **no** retrieved single-cell microenvironment study of its own, so it could not serve as a transfer donor even if T1's lineage objection were waived.

### BLOCKED (recorded, not routed around)

| Route | Outcome, verbatim |
|---|---|
| `WebFetch https://www.nature.com/articles/s41417-024-00856-7` | `{"error_type":"EGRESS_BLOCKED","domain":"www.nature.com","message":"Access to www.nature.com is blocked by the network egress proxy."}` |
| `curl .../eutils/esearch.fcgi?db=gds&term="extraskeletal+myxoid+chondrosarcoma"` | `curl: (56) CONNECT tunnel failed, response 403` |

Both are **ordinary proxy egress blocks** — not content-policy refusals, not publisher authentication. Neither was retried unchanged; the STS review was approached instead through the search index (a genuinely different route), which returned its abstract but not its subtype list. **Consequence, stated plainly:** the GEO DataSets registry was **not** queried directly, so §5.1's verdict rests on the literature census plus Chaiboonchoe 2026's independent 31-case public-dataset census, not on direct archive enumeration.

**No content-policy refusal was encountered in this run.**

### PROPOSED (NOT RUN)

- Direct GEO/SRA/ArrayExpress/ENA enumeration for EMC under sc/sn/spatial library strategies via the Actions-runner escape hatch (unblocked egress). **NOT RUN** — outside this worker's bounded scope.
- CELLxGENE Discover and HCA per-sample metadata download, filtering `tissue`/`disease` for EMC or `NR4A3`. **NOT RUN** — same reason.

---

## Limitations

1. **The absence verdict is bounded and is not proof of absence.** It covers PubMed as indexed 2026-09-08, a US web index, and one independent published census (Chaiboonchoe 2026's 31 external EMC cases). It does **not** cover direct queries of GEO, SRA, ArrayExpress, ENA, CELLxGENE, HCA, or Zenodo — blocked or not run. An unindexed, unpublished, controlled-access, or consortium-internal EMC single-cell dataset is **UNKNOWN**, not excluded. Same distinction the repository already enforces for the NR4A3 cistrome negative.
2. I inspected 7 of 46 EMC∩sc/spatial hits. The other 39 are **UNKNOWN** individually; the `query_translation` gives a mechanistic reason to expect the same false-positive class, but that is inference, not a check.
3. Sample counts, access status and licence for §5.2 atlases came from abstracts; per-sample histology tables were not retrieved. Any row could contain a single unnamed EMC specimen — the most likely way this verdict is overturned, and exactly what a direct portal metadata query would settle.
4. **T4 is a PREDICTION, not a measurement.** EMC copy-number burden was not computed.
5. Nothing here is a clinical, efficacy, safety or selectivity claim. No EMC patient data was accessed, and none was created.
6. This report adds **no new EMC data**. Its product is a bounded negative plus a transfer-limit statement — the honest output when the sought resource does not exist.

---

## Stop condition

**Condition set:** an evidence-backed presence/absence verdict for EMC in public single-cell and spatial resources, plus **either** a computable EMC question those resources genuinely support **or** an explicit itemised transfer-limit statement explaining why not.

**Status: MET**, on the second branch.

- Verdict delivered (§5.1): EMC **absent**, bounded per Limitation 1.
- The second branch is correct here as a finding, not a fallback. I examined whether existing resources support a computable EMC question and concluded they do **not** support the obvious candidate. Deconvolving retained EMC bulk arrays with a sarcoma-derived signature matrix fails for a specific, non-generic reason: **a missing-cell-type reference is not a neutral omission.** If the reference lacks the EMC malignant state — and by T3/T4 every available reference does — the deconvolution does not report "unknown"; it redistributes that variance onto whichever included cell type is nearest in expression space, returning a confident, precise, wrong stromal and immune fraction. That failure mode is silent and would produce exactly the kind of number this repository forbids. Hence §5.3 is the deliverable.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 28** (2 brief reads, 4 prior-work/env, 1 ToolSearch, 11 PubMed MCP, 4 WebSearch, 1 WebFetch (blocked), 1 curl (blocked), 1 Write (since deleted), 3 cleanup/env).
- **Wall clock: ~17 minutes** (01:39 → 01:56 UTC, 2026-09-08).
- Both within the ~40/~40 self-observed targets. Returning now that the stop condition is met.

---

## Next concrete action

**One successor, and it is a falsification test rather than a data-generation wish.**

*Before* anyone deconvolves EMC bulk data with a sarcoma reference, run the cheap check that decides whether T3/T4 actually bite: test whether the retained EMC bulk profiles (`GSE4303`, `GSE28866` — already in the repository, no new data, no spend) fall **inside or outside** the span of the donor-derived cell-state signatures from Subramanian 2024's 23 sarcoma cell states. Concretely: fit the non-negative least-squares deconvolution, then examine the **residual** — the fraction of EMC expression variance no combination of donor states can explain — against the same residual computed for the sarcoma histologies the reference was built from, as the null.

This is decisive in both directions, which is why it is worth running. A residual comparable to the reference histologies would mean the EMC malignant state *is* approximately representable in the existing basis, partially lifting T4. A residual well outside that null would be a **measured, quantitative** demonstration that EMC is not representable — converting §5.3's reasoned transfer limit into a number, and giving the outreach in `surface-targets-graph-records.json` a concrete figure for why an EMC single-cell dataset is needed, rather than a qualitative appeal.

It needs no new data, no network, no spend, no wet lab. It needs one thing this worker lacked: the Subramanian signature matrix, whose download sits behind the same egress block recorded above and should be routed through the Actions-runner escape hatch.

Secondary, independent action: re-run §5.1 against the primary sequence archives directly (GEO/SRA/ArrayExpress/ENA/CELLxGENE/HCA) from an unblocked runner, to close Limitation 1. That is the single change that could overturn this verdict, and it should be done before the verdict is cited anywhere outward-facing.

---

**Sources:** [10.3760/cma.j.cn112151-20251129-00787](https://doi.org/10.3760/cma.j.cn112151-20251129-00787) · [10.3760/cma.j.cn112151-20231025-00308](https://doi.org/10.3760/cma.j.cn112151-20231025-00308) · [10.1097/RLU.0000000000005146](https://doi.org/10.1097/RLU.0000000000005146) · [10.1016/j.modpat.2024.100464](https://doi.org/10.1016/j.modpat.2024.100464) · [10.1186/s13000-023-01390-0](https://doi.org/10.1186/s13000-023-01390-0) · [10.1016/j.modpat.2023.100161](https://doi.org/10.1016/j.modpat.2023.100161) · [10.1097/PAS.0000000000001921](https://doi.org/10.1097/PAS.0000000000001921) · [10.7717/peerj.21497](https://doi.org/10.7717/peerj.21497) · [10.1038/s42003-024-05790-w](https://doi.org/10.1038/s42003-024-05790-w) · [10.1038/s41467-023-38886-8](https://doi.org/10.1038/s41467-023-38886-8) · [10.1007/s00262-023-03577-2](https://doi.org/10.1007/s00262-023-03577-2) · [10.21037/tp-24-66](https://doi.org/10.21037/tp-24-66) · [10.1111/odi.15214](https://doi.org/10.1111/odi.15214) · [10.3389/fonc.2025.1604413](https://doi.org/10.3389/fonc.2025.1604413) · [10.1016/j.ejca.2025.115708](https://doi.org/10.1016/j.ejca.2025.115708) · [10.1038/s43018-024-00743-y](https://doi.org/10.1038/s43018-024-00743-y) · [10.1038/s41417-024-00856-7](https://doi.org/10.1038/s41417-024-00856-7) · [ScPCA SCPCP000017](https://scpca.alexslemonade.org/projects/SCPCP000017). Literature records retrieved from PubMed.

---

**Summary (<400 words).** I complied with the coordinator's correction: deleted the report file I had written into the repo and the empty `reports/` dir I created, verified the tree is clean of my writes, re-read the updated brief, and returned the report inline above. Model identity is stated as self-report only — there is no `ANTHROPIC_MODEL` in this environment.

Prior-work check found the repository holds **zero** single-cell or spatial data or code (`git ls-files` returned only three lexical "single" collisions), while four separate tracked files *request* a compartment-resolved EMC measurement as the missing evidence. So the lane question was genuinely open, not a replay.

**Verdict: no public single-cell, single-nucleus, or spatial-transcriptomic dataset containing EMC tissue was retrieved.** The 46 PubMed hits are a term-expansion artefact (`"single" AND "cell" AND "rna"`); the seven I inspected are FISH, IHC, PET/CT, bulk microarray, and RNA chromogenic ISH — none is single-cell or spatial. The strongest evidence is Chaiboonchoe 2026 (*PeerJ*), the most recent EMC microenvironment study, which used bulk TempO-Seq on 12 FFPE cases, computational deconvolution, and mIF on **two** specimens, with 31 external EMC cases all bulk — an independent published census containing no sc/spatial entry.

Sarcoma atlases that do exist (CCCS, RMS ×2, DFSP, IFS, LMS, paediatric ScPCA) each state histologies excluding EMC. Two traps worth flagging: Subramanian 2024's "23 sarcoma cell states" are derived from **bulk**, not single cells; and a PubMed search for myxoid liposarcoma scRNA-seq TME returned **zero** — EMC's usual myxoid analogue has no such study either.

Core deliverable is a four-part transfer-limit statement (T1 myxoid stroma: different driver/lineage *plus* an ECM-driven dissociation bias; T2 immune fraction: Bergsma's paediatric-vs-adult offset is signed and uncalibrated; T3 NR4A3 cell states: no donor expresses an NR4A3 fusion, and GSE243553 is accessibility, HEK293T, and has no microenvironment at all; T4 malignant-cell calling: no lineage anchor, and inferCNV is predicted weak because EMC is balanced-translocation-driven). Critically, T1/T2/T4 are fixed by sampling EMC; **T3 is not**.

Two routes were blocked and recorded, not circumvented: nature.com `EGRESS_BLOCKED`, NCBI eutils `403 CONNECT`. So the verdict is bounded — direct archive enumeration is UNKNOWN, not excluded.

Successor proposed: an NNLS residual test of retained EMC bulk arrays against the Subramanian basis, which would convert this reasoned transfer limit into a measured number at zero spend.

result: EMC is absent from all retrieved public single-cell/spatial resources (verdict bounded to PubMed + web index + one independent published census; direct archive query blocked), delivered with a four-item transfer-limit statement naming why myxoid-stroma, immune-fraction, NR4A3-cell-state and malignant-cell-calling inferences cannot move from sarcoma atlases to EMC — report returned inline, no repository files written.
