---
id: DOC-EMC-RET-LANE
title: RET in EMC — is it a fusion target gene, and does it clear the activation bar?
level: L3
kind: memo
status: live
canonical_for: ["the 2026-08-07 RET-lane instrument build and its reading of the primary sources"]
purpose: >
  Work the lane emc-unexplored-treatment-lanes.md §3.1 ranks first of twelve: test whether RET is a
  target GENE of EWSR1::NR4A3, read RET across the public EMC expression series, and carry the
  methodological guard the memo supplies (clear cell sarcoma's MET). Report at true strength.
scope: >
  L3. Grades ONE lane. It does not re-grade any route, and every roadmap or graph change it implies
  is emitted as a routed map-edits file rather than applied.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
---

# RET in EMC — is it a fusion target gene, and does it clear the activation bar?

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC,
> AND NOTHING HERE RECOMMENDS GIVING ANY AGENT TO ANY PATIENT.** No EMC patient has received a
> selective RET inhibitor. Every clinical and biological statement below carries a PMID or PMCID
> and a verification level.

## 0 · The one-paragraph answer

**The lane survives, and its headline sentence does not.**
[`emc-unexplored-treatment-lanes.md` §3.1](../manuscripts/program/emc-unexplored-treatment-lanes.md#31--ret)
says *"RET in EMC passes the test MET in CCS failed."* Read against the primary sources, that is not
supported: **the only report of RET *activation* in EMC is one sentence in one paywalled 2014
abstract, over "a limited set of samples" of an n = 10 series, with no stated numerator and no
stated denominator** (PMID 24703573 **[API]**). The only independent EMC dataset measures **mRNA
abundance in six patients** and performs no phosphorylation assay at all (PMID 28423517, PMC5400622
**[FT]**). *Expression common, activation of unknown frequency* **is** the MET-in-clear-cell-sarcoma
failure mode — and the CCS study is specific about the instrument that decided it (a blinded 32-case
TMA: MET protein 82 %, phospho-MET Tyr1234–35 **4 %**, PMID 34885165 **[FT]**). **RET in EMC has
never been measured that way**, so the honest verdict on the guard is **NOT PASSED AND NOT FAILED —
the test was never administered.** Two further things the memo does not say: the lane's named free
next step is **mis-specified** (the ENO3 precedent was EMSA/ChIP/luciferase, not a motif scan, and
was **TFG::NR4A3**, not the EMC-canonical fusion); and **EMC's RET is over-expressed wild type**,
which sits outside the enrolment criterion of every trial behind the two approvals the lane leans
on. The falsifier has **not** fired; the two clauses that would fire it were not measurable at $0
this session, and the reasons are recorded rather than hand-waved.

---

## 1 · What was run

| # | thing | route | state |
|---|---|---|---|
| 1 | **Egress diagnosis** — is the sandbox actually blocked, and by what? | proxy status endpoint | ✓ **measured, not assumed.** `recentRelayFailures` shows `403 to CONNECT` for `rest.ensembl.org`, `ftp.ncbi.nlm.nih.gov`, `www.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `files.rcsb.org`, `data.rcsb.org`. `api.github.com`, `raw.githubusercontent.com` and `pypi.org` return 200 |
| 2 | **The instrument** — NBRE/NurRE scan + two nulls + the EMC expression read | [`emc_ret_target_scan.py`](./emc_ret_target_scan.py) | ✓ **built, self-tested, 42 tests green.** Its fetch half has **not** run — see §5. ⛔ Two real defects were found in it by running it against committed data before trusting it (§5) |
| 3 | **The activation-bar audit** — what the primary sources actually MEASURED | Europe PMC via `fetch-literature.yml` @ `main` (**no push needed** — the `query` path takes no repo file) + the committed `literature-cache` corpora | ✓ **run.** One home: [`emc-ret-activation-bar.json`](./emc-ret-activation-bar.json) |
| 4 | Five Europe PMC corpora dispatched | same | ✓ **4 landed and read** — `ret-emc-lane` (272 records / 214 full texts), `ret-regulation-and-ccs-met-guard` (4,599 / 2,851), `selective-ret-inhibitor-eligibility` (2,077 / 1,608), `nr4a3-cistrome-tight` (792 / 461). One over-broad query is still running and is superseded by the tight one |
| 5 | **A full-text scan of every EMC paper in the RET corpus** for a phospho-RET / RET-IHC measurement with a denominator | local, over the retrieved corpus | ✓ **run — and it found none.** §3 |

**$0 throughout. No GPU, no rental, nothing billed.**

---

## 2 · Four corrections to §3.1, each with the sentence that produces it

### 2a · ⛔ The ENO3 precedent is not what the memo says it is — twice over

§3.1: *"an NBRE-motif scan of its regulatory region, **the same bioinformatic approach that
established PPARG and ENO3 as direct targets**"*.

The ENO3 source is **PMID 26310886** **[API]**, and its own abstract says:

> *"**EMSAs, ChIP assays, and luciferase reporter assays** revealed that TFG-TEC upregulates
> β-enolase transcription by binding to two NGFI-B response element motifs located upstream of the
> putative transcription start site."*

Two things follow, and both matter for what this lane can deliver:

1. **The instrument was wet-lab, not bioinformatic.** The NBRE motifs were the *hypothesis*; EMSA,
   ChIP and luciferase were the *evidence*. **A motif scan alone did not establish ENO3 and cannot
   establish RET.**
2. **The fusion is `TFG::NR4A3`, not `EWSR1::NR4A3`.** `TEC` is an alias of `NR4A3`, which is why the
   result reads as an NR4A3 result — but the 5′ partner is a different one, and **this repository's
   own §3.2 evidence is that the 5′ partner changes what the chimera binds.**

### 2b · ⭐ The precedent the memo *should* have named exists, and it is in the repository's own corpus

**PMID 31020999 / PMC6766969** **[FT]** — already cited in §3.2 for axon guidance, never for method —
did exactly the study §3.1 describes:

> *"The **MatInspector** software was employed to identify putative NR4A3 consensus sites (**NBRE**)."*
> … *"**ChAP-qPCR** experiments confirmed the ability of NR4A3 to bind the predicted target on
> SEMA3C. More interestingly, the ability of NR4A3 to recognize the SEMA3C target region was
> **retained by the EWSR1-NR4A3 chimera but was impaired by TAF15-NR4A3**."*

⭐ **A bridge between §3.1 and §3.2 that neither section currently states.** §3.1's sunitinib
responders all carried EWSR1::NR4A3 and its refractory cases all carried TAF15::NR4A3
(PMID 24703573). Here the two chimeras are **measured** to differ in DNA binding at a validated NBRE
target. That is a mechanism for the fusion-variant split — ⚠ **a bridge, not a demonstration:
nothing shows the difference runs through RET**, and saying otherwise would be exactly the
over-reading this memo is correcting.

**And it sets the ceiling on part 1 of the instrument.** In the one EMC study that ran this method,
in-silico generated the candidate and a chromatin assay decided it. **This program has no wet lab.**
So an NBRE scan here can produce a *prioritisation*; it can never produce a target-gene claim.

### 2c · ⛔ The translational bar the memo does not state: EMC's RET is over-expressed wild type

PMID 28423517 **[FT]** is explicit that beyond the fusion, *"other recurring genomic abnormalities
were not detected"*. **EMC has no reported RET fusion, mutation or amplification.**

Against 2,077 Europe PMC records (1,608 with full text):

- the tumour-agnostic arm a rare sarcoma would enter through is *"selpercatinib in patients with RET
  **fusion-positive** solid tumours other than lung or thyroid"* — **PMID 36108661** **[API]**;
- the pan-tumour companion diagnostic behind the 2023 FDA and 2024 MHLW approvals identifies **RET
  fusions** — **PMID 42211499** **[API]**. A tumour with over-expressed wild-type RET and no fusion
  is **CDx-negative by construction**;
- over-expression *is* a recognised RET aberration class (**PMID 34402300** **[API]**) — but
  recognition of a class is not an evidence base for treating it, and **no record in the corpus
  reports a selective RET inhibitor active against over-expressed wild-type RET in any tumour type.**

⚠ **That last line is a searched-and-did-not-find, not a proof of absence**, and it is written that
way in the artifact. What it establishes is narrower and still decision-relevant: *"two approved
selective inhibitors exist"* does not currently name a label, a companion diagnostic, or an open
basket that EMC could enter.

### 2d · ⭐ The cistrome question, asked and answered — and it opens a better instrument than the one this lane was given

The highest-value version of *"is RET a fusion target gene"* is not a motif scan; it is *"has anyone
already ChIP'd NR4A3?"* Asked of 792 Europe PMC records (461 full texts):

**⛔ No `EWSR1::NR4A3` cistrome exists.** The only chromatin experiments on any NR4A3 fusion are
single-locus: the SEMA3C ChAP-qPCR (PMID 31020999) and the ENO3 EMSA/ChIP (PMID 26310886, and on
`TFG::NR4A3`). ⚠ This repository already records that no modern IP-MS/BioID **interactome** of the
fusion exists; **the same hole runs through its chromatin.** Nothing genome-wide has ever been done
on the object the whole programme is about.

**⭐ But wild-type NR4A3 cistromes do exist, and one of them is human and paralogue-matched.**

| study | system | what it is | data |
|---|---|---|---|
| **PMID 36482877** / PMC10108054 **[FT]** | human primary CD1c⁺ cDC2s, resting + stimulated | *"we performed **ChIP sequencing for NR4A1, NR4A2, and NR4A3** in resting and stimulated cDC2s"* | ⛔ **no accession in the PMC rendering** — searched for GSE/E-MTAB/PRJNA/PRJEB/EGAS/SRP/CRA across all 23,670 characters, none present, no data-availability section; supplements are on the Wiley site. ⚠ Absent reading, not proof of non-deposition |
| **PMID 42028030** / PMC13099357 **[FT]** | Schwann cells | *"Integrated ChIP-seq and mRNA-seq profiling identified GLS2 as a direct transcriptional target of NR4A3"* | ✓ **in hand** — *"The mRNA-seq and ChIP-seq data … are available in GSA under accession numbers **CRA032321** and **CRA032324**"* |

**Two free things this makes possible, and both are stronger than the motif scan:**

1. **Ask the peak sets whether NR4A3 binds RET's regulatory region.** A peak is measured occupancy in
   real chromatin; an NBRE octamer is a string that occurs about once per 33 kb of random sequence.
   ⛔ **The caveat travels with it, in both directions:** these are wild-type NR4A3 in dendritic and
   Schwann cells, not the chimera in EMC. A peak at *RET* would be a strong **prior**, not a
   demonstration; **no** peak would be weak evidence, because the locus may simply be closed in those
   cell types. Saying both up front is what stops this becoming the next over-read.
2. ⭐ **The paralogue read comes free.** The cDC2 dataset carries **NR4A1, NR4A2 and NR4A3 in the same
   cells**. This programme's paralogue-selectivity problem has been argued from *domain sequence
   identity*; a matched three-paralogue peak-set overlap is a **direct empirical** measure of how much
   the three actually share at DNA level, and no identity calculation can produce it. That is worth
   more to the repository than this lane is.

---

## 3 · The methodological guard, answered at its true strength

**The guard (from §3.1):** clear cell sarcoma's EWSR1::ATF1 transactivates MET, which motivated
crizotinib trials that produced only sporadic responses, attributed to infrequent actual MET
*activation*. **Expression is not a target; measured activation is.**

**Does RET in EMC clear it? NO — AND IT DOES NOT FAIL IT EITHER. THE DENOMINATOR IS UNKNOWN.**

| what | source | what it actually is |
|---|---|---|
| the comparator study that DID pass/fail this test | PMID 34885165 **[FT]**, n = 32 | a blinded TMA measuring ligand, receptor, both phospho-sites and three downstream nodes. **This is the instrument.** MET 82 %, pMET-Tyr1234–35 **4 %** |
| *"Among putative sunitinib targets, only RET was **expressed and activated** in analysed samples"* | PMID 24703573 **[API]**, n = 10 series | the **only** activation report in existence. Its own methods sentence reads *"transcriptome, immunohistochemical and biochemical analyses of **a limited set of samples**"* — ⛔ **the subset size, the positive fraction, and which assay produced the word "activated" are all absent from the abstract, and the full text is paywalled** |
| *"Only RET expression was significantly greater in patients with EMC relative to other types of sarcomas excluding liposarcoma (p<0.0002)"* | PMID 28423517 **[FT]**, n = 6 | **transcriptome sequencing** — mRNA abundance. This paper measures **no phosphorylation of anything** |
| *"analysis of receptor tyrosine kinase (RTK) activity demonstrated elevated expression and activation of RET"* | PMID 28423517 **[FT]** | ⚠ **SECONDARY** — this is the 2017 paper *citing* the 2014 one. It is not a second observation and must not be counted as one |
| authors' own conclusions | both | *"Involvement of RET deserves further investigation"* (2014); *"The clinical significance of RET expression in EMC should be explored"* (2017) |

**⭐ The guard's own source is sharper than the memo, and it names the instrument.** **PMID 34885165**
/ PMC8657105 **[FT]** is the EORTC 90101 correlative study, and it did not merely *attribute* the
sporadic responses — it measured them out:

> *"The histopathological analysis showed the **absence of a MET ligand and MET activation**, with
> the presence of MET itself in most of cases."*

The measurement: a **blinded 32-case tissue microarray**, stained for MITF, HGF, (p)MET, (p)GAB1,
(p)MAPK, (p)AKT and (p)S6, evaluable in 88–100 % per stain. **MET protein in 82 %. HGF ligand in
16 %. Phospho-MET at Tyr1234–35 — the kinase-domain activation loop — in 4 %.** *That* 82 %-vs-4 %
gap is what closed crizotinib in CCS.

⛔ **So the bar is not an abstract distinction. It is a specific study, and RET in EMC has never had
one.** No EMC phospho-RET microarray, no denominator, no GDNF/GFRA ligand co-stain, no downstream
node panel exists in anything retrieved. **RET in EMC did not pass the test MET failed; it has not
taken it** — and a full-text scan of every EMC paper in a 272-record RET-focused corpus found the
only substantive RET passages to be about **mRNA abundance**. ⚠ That scan cannot see PMID 24703573,
which is paywalled — an instrument limit, recorded as one.

⭐ **And the tumour's own histology keeps the confound live.** PMC6766969 **[FT]**: *"Most EMC are
hypocellular and classified as low-grade neoplasms."* A hypocellular, matrix-rich tumour is
precisely the setting in which a **bulk** RTK-activity read is most exposed to stromal contribution
— which is the memo's own falsifier, arriving from the histology rather than from any new
measurement.

⭐ **And the same group said so first.** In the two-patient precursor (**PMID 23058004**, PMC3534218
**[FT]**): *"Unfortunately, due to absence of untreated frozen material, we could not assess the RTK
activation profile."* The activation assay needs **untreated frozen tissue**, which in a rare sarcoma
treated on a named-patient basis exists for only some patients — so 2014's *"a limited set of
samples"* is a **structural property of the series**, not an oversight. ⚠ That explains why the
denominator is small; it does not recover it.

⚠ **The competing explanation is also theirs.** The same paper: *"In the absence of selective targets
and known mechanisms of action, sunitinib antiangiogenic activity as well as an effect on the
autocrine-paracrine PDGFR/VEGFR activation-loop have been advocated as possible explanations."*
§3.1 frames the VEGFR attribution as the *conventional* reading that RET displaces. It is the
**originating authors' own** reading, from the same series.

---

## 4 · The falsifier: did it fire?

§3.1's falsifier is a conjunction — ***no NBRE at RET*, PLUS *evidence that RET phosphorylation
tracks stromal rather than tumour content*.**

**It did not fire.** Neither clause was measured this session, and neither was measured against.

| clause | state | what it is waiting on |
|---|---|---|
| no NBRE at *RET* | **NOT MEASURED** | RET's regulatory sequence. Ensembl REST answers `403` to CONNECT from this sandbox — measured, not assumed. The scanner, the window, the two nulls and the background panel are built and green; only the fetch is missing |
| phosphorylation tracks stroma | **NOT MEASURABLE AT $0, AND NOT ONLY HERE** | no phospho-RET dataset for EMC exists in any source reached. The expression-level shadow of it — does RET covary with a stromal panel more than with an EMC tumour panel — **is** implemented and reportable from GSE24369, and is honestly labelled as a shadow rather than the thing |

⛔ **An absent reading is not a reading of absence.** `part_1_nbre_scan._status` and
`part_2_expression._status` both read `NOT_RUN` with `verdict: null` in
[`emc-ret-target-scan.json`](./emc-ret-target-scan.json), and
`test_an_empty_inputs_cache_never_produces_a_biological_verdict` fails the build if any future
change lets an empty cache emit a biological call.

---

## 5 · The instrument, and the one thing blocking it

[`emc_ret_target_scan.py`](./emc_ret_target_scan.py) — pure stdlib, no numpy, three parts:

**Part 1 — the motif scan, built so that a hit can *mean* something.** A raw NBRE count is not a
result: `AAAGGTCA` is an 8-mer — 4⁸ = 65,536 — so even the widened 25 kb window read on both
strands is expected to carry **under one** by chance, and **one hit is what the genome does
anyway**. So the module never reports a count alone.
It reports it against **two independent nulls**:

- a **dinucleotide-preserving (Altschul–Erikson / Euler-path) shuffle** of the *same* window, 2,000
  replicates — this holds GC *and CpG* exactly, which a mononucleotide shuffle does not, and CpG
  depletion is the strongest compositional feature of mammalian promoters. Verified across 300
  randomised cases plus 8 parameterised tests: length, first base, last base and **every
  dinucleotide count** are preserved exactly, and the output is never the input;
- the **rank of RET's window among a 200-gene background panel** fetched identically, reported both
  raw and **GC-matched** (±0.05). ⭐ **The panel is not chosen by me**: it is a fixed-seed sample of
  the 1,299 symbols this repository already committed for the ATR/DDR concept universe in
  `emc-atr-vulnerability-inputs.json`, so it cannot have been picked to flatter or damage RET.

⛔ **AND THE WINDOW HAD TO BE RE-FROZEN — a symmetric ±5 kb would have excluded the one
experimentally validated distal element *RET* has.** HOXB5 binds a multi-species conserved sequence
at **MCS+9.7, in RET's first intron**, and deleting that site abolishes HOXB5 trans-activation of
the RET promoter (**PMID 24794774**); ETV5 ChIP-seq separately identifies binding at the promoter
**and an enhancer upstream of it** (**PMID 29321660**). The window is now **−10 kb / +15 kb**, which
contains MCS+9.7. ⚠ **The timing is what makes this a re-scope and not tuning:** no RET sequence had
been fetched, `part_1_nbre_scan` still reads `NOT_RUN`, and the change is driven by two published
facts *about the gene* rather than by any count the module produced. Superseded, retained:
`WINDOW_UPSTREAM = WINDOW_DOWNSTREAM = 5000`. ⚠ It is still a scope: a null inside this window is a
null **within this window**, and the artifact says so in `_window.⚠_still_bounded`.

Positive controls (`ENO3`, `PPARG`, `NR4A3`, `NR4A1`) and the **alternative hypothesis** (`VEGFA`,
`KDR` — the conventional VEGFR attribution for EMC's TKI activity) are scanned in the same pass, so
the answer is comparative rather than absolute. Both consensus sequences carry the PMID that defines
them (NBRE: 1902986; NurRE: 9315667). The empirical p is `(ge+1)/(n+1)`, never `ge/n`, so it can
never print a 0 the permutation count does not support — asserted by a test.

**Part 2 — the expression read**, on **GSE24369/GPL6244** (42 samples → **6 EMC, 29 comparators**,
7 unclassified; single-channel, so *absolute* expression) and **GSE4303/GPL3290** (16 samples →
**10 EMC, 6 comparators**; two-colour, so *relative*). Welch t reused from the module that owns it
(`fet_ddr_axis_scan._welch`), and the stroma-vs-tumour Spearman contrast that shadows the falsifier.

⛔ **The sample classifier was re-implemented here once and was wrong in two ways, and running it
over the real committed annotations before trusting it is the only reason that is known.**

1. It required the phrase *"**extraskeletal** myxoid chondrosarcoma"*. GSE4303 — the original EMC
   series — titles its samples `STT3697-Myxoid Chondrosarcoma`, with no "extraskeletal". **Ten of
   its sixteen samples classified as comparators**, so the contrast would have been EMC against EMC
   and would have reported `n_EMC = 0, underpowered` — an **instrument failure wearing the costume
   of a data limitation**, which is precisely the shape CLAUDE.md §4 exists to catch.
2. It ended with a catch-all: any unrecognised non-empty annotation became a comparator. GSE24369's
   two `Skeletal muscle` samples are **normal tissue** and were being fed into the comparator arm of
   a tumour contrast.

Both had one root cause — a second copy of a classification this repository already owns. The
patterns are now **read from `emc_atr_vulnerability`** (`ast.literal_eval` over its source, so no
pandas/numpy import is needed and a moved constant **raises** rather than silently falling back to a
private copy), and an unrecognised label is now `unclassified` and excluded from **both** arms. Six
tests hold it, one of which runs the classifier over the **real committed GEO annotations** — every
version of this bug was invisible to a hand-written fixture and obvious against the actual data.

⭐ **The fix also gains a contrast the lane did not have.** GSE4303/GPL3290 was previously readable
as *"0 EMC"*; it is **10 EMC vs 6 comparators (3 GIST, 3 DFSP)**. It is two-colour and therefore
relative, so it corroborates rather than measures — but a second independent series is exactly what
an n = 6 primary contrast needs.

⭐ **A probe-mapping improvement that is not incidental.** `emc_atr_vulnerability._gpl_symbols`
records `symbol_column: null` for GPL6244 and falls back to an EST accession bridge with a
wall-clock budget. For a handful of *named* genes that is unnecessary: GPL6244's platform table
carries `seqname` / `RANGE_START` / `RANGE_STOP`, so **a probe whose genomic range lies inside a
gene's span is that gene's probe**. This module resolves probes by curated symbol **and** by
coordinate and **records whether the two agree**, rather than trusting either. ⚠ This is also why
the committed cache cannot answer the RET question by itself: its `geneset_gene_values` covers only
the 1,299 ATR-concept genes, and **RET is not among them** — checked, not assumed.

**Part 3 — the activation-bar audit**, §3 above, one home in
[`emc-ret-activation-bar.json`](./emc-ret-activation-bar.json).

### ⛔ What blocks parts 1 and 2, precisely

**One `git push` of this worktree branch, plus one `workflow_dispatch`.** Nothing else. Not money,
not a GPU, not a capability that does not exist, not data only a human holds. The chain is:

1. Ensembl REST and GEO FTP are `403`-on-CONNECT from this sandbox (measured).
2. CLAUDE.md §6's remedy is a GitHub Actions runner, and a `workflow_dispatch` runs **the code on
   the ref it is dispatched against**.
3. This agent was instructed **not to push**, so no ref carries `emc_ret_target_scan.py`.
4. The literature half was still reachable, because `fetch-literature.yml`'s `query` path needs no
   new file — which is why part 3 ran and parts 1 and 2 did not.

The dispatch, once the branch exists on the remote, is a mode of `emc-expression-datasets.yml` (the
lane that already owns "the sandbox cannot reach GEO/Ensembl" work) running
`emc_ret_target_scan.py --fetch`, ~10 minutes on a free CPU runner.

---

## 6 · The grade

| axis | reading |
|---|---|
| **Is the lane real?** | **Yes.** Two independent cohorts, RET the only sunitinib target with an EMC-enriched expression signal, two approved selective agents in the world, and no RET route among the 40 |
| **Can those agents reach EMC today?** | **Not on their evidence base.** EMC's RET is over-expressed wild type; every approval enrolled RET-**altered** disease (§2c). This does not close the lane — it says the lane's translational step is a research question, not a referral |
| **Is it #1 of twelve?** | **Not on this evidence.** Its rank rested on *"passes the test MET in CCS failed"*, and that sentence does not survive contact with the sources. It should be re-ranked against §3.2 (fusion-variant stratification), which is cheaper, has more data, and — per §2b — is now **mechanistically linked to §3.1** |
| **Has the falsifier fired?** | **No.** Neither clause was measured. Recorded as `NOT_RUN`, not as a negative |
| **Is it publishable?** | **Yes, and the paper is already better specified than it was.** *"RET in extraskeletal myxoid chondrosarcoma: what the record actually shows, and the one measurement nobody has published."* Its one sentence for the field's record: **the sole basis for calling RET an activated target in EMC is an unquantified subset of a ten-patient series, and the fraction has never been reported** |
| **What it is NOT** | not a demonstration that RET is a fusion target gene; not evidence of RET occupancy anywhere; not a statement about selectivity, efficacy, safety, a therapeutic window or clinical readiness; not a recommendation |

### The ordered next steps, cheapest first

1. **$0 — pull the published wild-type NR4A3 ChIP-seq peak sets and intersect them with *RET*
   (§2d).** This now outranks the motif scan, because it substitutes measured occupancy for a
   sequence string, and it carries the paralogue-overlap read for free. **The Schwann-cell dataset
   can be pulled today — GSA `CRA032324` — and needs nothing further.** The cDC2 three-paralogue
   dataset, which is the more valuable of the two, needs **one prior $0 retrieval**: its accession
   is absent from the PMC rendering, so it has to come from a GEO/ArrayExpress search or the Wiley
   supplement.
2. **$0 — push the branch and dispatch the fetch.** Parts 1 and 2 both land in one ~10-minute CPU
   run. Still worth doing — the motif scan is the *prioritisation* layer under the ChIP read, and
   the expression half answers the falsifier's reachable clause. This is the only item blocked on
   something this repository controls.
3. **⛔ Outside-world — the full text of Eur J Cancer 2014;50:1657-64 (PMID 24703573).** Its methods
   and the figure behind *"only RET was expressed and activated"* are the single highest-value
   unread page in this lane, and everything §3 says is provisional on them. Paywalled; this is a
   genuine external dependency, not a sandbox limitation.

---

## 7 · Files

| file | what it is |
|---|---|
| [`emc_ret_target_scan.py`](./emc_ret_target_scan.py) | the instrument: motif engine, two nulls, background panel, expression read, `--selftest` / `--fetch` / `--check` |
| [`emc-ret-target-scan.json`](./emc-ret-target-scan.json) | the derived artifact. Parts 1 and 2 read `NOT_RUN` with `verdict: null` — deliberately |
| [`emc-ret-activation-bar.json`](./emc-ret-activation-bar.json) | part 3: every primary source with its verbatim sentences, PMID and verification level |
| [`tests/test_emc_ret_target_scan.py`](./tests/test_emc_ret_target_scan.py) | 42 tests. The first asserts that no reading ⇒ no verdict; six hold the sample classifier, one of them against the real committed GEO annotations |
| [`emc-ret-map-edits.json`](./emc-ret-map-edits.json) | the routed roadmap/graph proposal, including the candidate `RT-RET` route record. **Not applied** |

**Both halves of the map-edits file were checked rather than asserted**, because a routed edit that
does not apply is the failure `route_map_edits.py` exists to prevent:

- every `anchor` and `current_text` was matched against `git show origin/main:<file>` and occurs
  **exactly once** — 4 of 4;
- the proposed `RT-RET` record **validates against `systems/schema/route.schema.json`** (with its
  `research-object.schema.json` `$ref` resolved), and the validator was negative-controlled by
  removing `remaining_unknowns` and lower-casing the id, which produced 3 errors.

⚠ **That is a SHAPE check only.** It does not exercise `systems_check.py`'s cross-file invariants
(`[H2]` in particular: the family must list the route and the route must claim the family), because
running those needs a write into `systems/graph/`, which this agent was told not to make. The
applier's checklist is in the file.
