---
id: DOC-PPARG-DIRECTION-EMC
title: The direction of the PPARγ effect in EMC — agonism, antagonism, or neither
level: L3
kind: memo
status: live
canonical_for: ["the sign of the PPARγ axis in EMC and the evidence tier it carries"]
purpose: >
  Answer the one literature question that RT-PPARG-DOWNSTREAM and RT-TRABECTEDIN-PPARG have both
  been blocked on since 2026-06 — is the PPARγ axis in EWSR1::NR4A3 EMC to be agonised or
  antagonised — from retrieved primary sources rather than from inference.
scope: >
  The PPARγ axis in extraskeletal myxoid chondrosarcoma only. Says nothing about PPARγ in any other
  disease, and asserts nothing about efficacy, safety or clinical use of any agent it names.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-06
last_verified: 2026-08-06
---

# The direction of the PPARγ effect in EMC — agonism, antagonism, or neither

**One sentence.** The direction is **NOT resolved by the published literature — and the reason is not
that nobody looked.** It was looked at twice, in the two EMC expression studies that report *PPARG*,
and **those two papers read the same observation in opposite therapeutic directions**; the only
functional experiment that has ever tested the direction was run in a cell line this repository had
already recorded, on 2026-08-05, as not carrying the hallmark fusion on the curated record.

**Second sentence, and it is the one that changes a route.** The premise both route records have been
carrying — *"in EMC the fusion turns PPARG on, so an agonist may be redundant"* — **is an inference
the cited source does not make, and the source argues the opposite in its own discussion.**

---

## 1 · What was asked, and what would count as an answer

`RT-PPARG-DOWNSTREAM` and `RT-TRABECTEDIN-PPARG` are both held, in their own records, behind the same
item: *the direction of the PPARγ effect in EMC*. `RT-TRABECTEDIN-PPARG` sits at readiness
`experimental_proposal` with that as its **only** missing item, so the whole all-approved-drug
combination proposal turns on it.

An answer has to distinguish three claims that this repository's prose has been running together:

| # | claim | what would settle it |
|---|---|---|
| **A** | *PPARG is over-expressed in EMC* | an expression measurement in EMC tumours |
| **B** | *the fusion causes A* | a promoter/response-element experiment |
| **C** | *therefore an agonist / an antagonist is the useful direction* | a functional experiment in EMC, or an explicit argument from A+B |

**A and B are settled. C is the question, and A+B do not determine it.** Conflating them is what
produced the redundancy argument in §3.

---

## 2 · What was retrieved, and how

⚠ **Every source below was read from a retrieved document, not from memory.** Provenance:

- **The Europe PMC corpora already committed to the `literature-cache` branch** — `literature/extraskeletal-myxoid-chondrosarcoma/` (694 files, `_index.json` carrying **1,369 catalogued records**) and `literature/emc-post-degrader-options/`. Both were pulled by `.github/workflows/fetch-literature.yml` in earlier sessions and are readable from the sandbox with `git fetch origin literature-cache`, which is why this answer cost **$0 and needed no new run**.
- **A fresh, on-point Europe PMC query** — PPARγ/TZD terms × NR4A3/chondrosarcoma terms — was dispatched to that workflow on 2026-08-06 (run `31126146908`, slug `pparg-direction-emc-2026-08-06`). ⛔ **It has not run, and the reason is not this lane.** GitHub Actions execution for this repository is stalled **repo-wide**. Measured at 2:56 PM ET on 2026-08-06 via the public Actions API: **38 runs queued, 0 in progress**, the oldest queued since 12:49 PM ET, and the newest run to reach any terminal state was created at **12:55 PM ET**. A concurrency cap would show N runs executing; **zero executing with dozens queued is an account-level stop**, not contention, and it is outside this pass's control. **Nothing in this memo depends on that run**; it can only add the chondrosarcoma-TZD reports of §6.

### 2a · The `query` path was verified before anything was trusted, and the check found a second bug

CLAUDE.md §6 records that this workflow's Europe PMC `query` path was **decorative until 2026-08-05**
— the header claimed it, `scripts/fetch-paper.mjs` implemented it, and the workflow never invoked it,
so a dispatch carrying a query searched for nothing and reported success. A memo that leaned on it
without checking would be repeating that failure, so it was checked at $0 against a **committed
output**, not against the code:

✅ **It works.** Run `31051158710` (2026-08-05, 6:03 PM ET — after the wiring fix) published
`literature/bangerter-2023-emc-exvivo/`, which carries a real `_index.json` of **70 Europe PMC
records, 61 with full text on disk**, whose first record is the query's known-positive target
(Bangerter et al. 2023, PMID 36316541). A search that ran and returned the record it was aimed at is
the discriminating observation; the green tick alone was not.

⛔ **And the same artifact shows a second defect, measured rather than argued.** That directory also
holds all **25 built-in FEP-methodology files** — `lomap_*`, `cinnabar_*`, `diffnet_*`, the
Schrödinger cycle-closure patents — plus their `_manifest.json`, because the workflow ran **both**
input paths into the same output directory: `scripts/lit_fetch_urls.py` falls back to its built-in
`TARGETS` when no `targets_file` is given, and the publish step copies the directory wholesale. So a
query-only dispatch published its Europe PMC corpus **interleaved with an unrelated corpus** — the
same mislabelled-record harm the publish step's own slug guard was written to prevent, arriving from
the other direction.

**Fixed this session** (both in `.github/workflows/fetch-literature.yml`, which this pass owns):
the URL-fetch step is now skipped when a query is given with no `targets_file`, and a new
`scripts/lit_query_assert.py` step **fails the run** if the query path produced no index, an empty
index, or an index missing the known-positive PMID(s) named in a new `expect_pmids` input — so the
retrieval is **asserted** rather than described. ⚠ The dispatch above ran against `main`, which does
not yet carry either change; the branch these landed on is not on `origin`, so `ref=<branch>`
dispatch is not available until it is pushed.
- **One source could not be read and is marked as such** — the pioglitazone + trabectedin myxoid-liposarcoma paper (§4, row 4). The literature cache holds a recorded **HTTP 403** for it, so this repository has never retrieved its text.

---

## 3 · Finding 1 — the redundancy premise is not in the source it cites

Both route records, `IDEAS.md` and `emc-post-degrader-options.md` carry a version of:

> *in EMC the fusion turns PPARG **on**, so an agonist may be **redundant***

sourced to `EV-FILION-2009`. **Filion et al. say the opposite, in the same paper, in their discussion**
(*J Pathol* 2009;217(1):83–93, PMID 18855877, PMC4429309 — full text retrieved):

> "PPARG agonists have been reported to have anti-neoplastic effects in a variety of PPARG-expressing
> cancers. **Thus, the direct up-regulation of PPARG by EWSR1/NR4A3 demonstrated here provides a
> rationale for studies of these agents** (several of which are already clinically available) **in
> EMC**, either in vitro if genuine EMC cell lines become available, or in vivo in the context of
> Phase I trials."

So the paper treats fusion-driven PPARG up-regulation as the **reason to try an agonist**, not as a
reason it would be redundant. The redundancy reading was generated inside this repository and
attributed outward.

**Why the inference fails, mechanistically.** PPARγ is a **ligand-activated** nuclear receptor. A
transcription factor that drives the *PPARG gene* produces **more receptor**, which is a statement
about **abundance**, not about **occupancy**. "The receptor is abundant, therefore activating it adds
nothing" only follows if the receptor is already ligand-saturated, and **no published work measures
that in EMC.** ⚠ *This paragraph is reasoning, not a measurement, and is marked as such —* it is
offered to explain why A+B cannot decide C, not as evidence for either sign.

Note also Filion's own conditional — *"if genuine EMC cell lines become available"* — written in 2009.
Finding 3 is that the experiment which eventually ran did not clear that condition.

---

## 4 · Finding 2 — the two EMC expression studies that report *PPARG* point in opposite directions

The observation is concordant. The therapeutic reading is not.

| # | source | what it measured | what it proposed | tier |
|---|---|---|---|---|
| 1 | **Subramanian S, West RB, Marinelli RJ, et al.** *The gene expression profile of extraskeletal myxoid chondrosarcoma.* J Pathol 2005;206:433–444. doi:10.1002/path.1792, PMID 15920699 *(abstract retrieved; not open access. Full citation taken from Filion 2009's reference 31, whose text was read.)* | 10 EMCs vs 26 other sarcomas, 42,000-spot cDNA microarrays | ⛔ **ANTAGONISM.** Verbatim: *"High levels of expression of PPARG and the gene encoding its interacting protein, PPARGC1A, in most EMCs suggest activation of lipid metabolism pathways in this tumour. **Small molecule inhibitors for PPARG exist and PPARG could be a potential therapeutic target for EMC.**"* | **T0** — a proposal in a discussion; no functional experiment |
| 2 | **Filion C, Motoi T, Olshen A, et al.** *The EWSR1/NR4A3 fusion protein of EMC activates the PPARG nuclear receptor gene.* J Pathol 2009;217(1):83–93. doi:10.1002/path.2445, PMID 18855877, PMC4429309 *(full text retrieved)* | 3 fusion-positive EMCs (fusion transcript verified by RT-PCR in the source) vs 137 other sarcomas; PPARγ Western blot / IHC; PPARG-promoter response element by band-shift + transient transfection | ★ **AGONISM.** Verbatim quote in §3 | **T0** for the direction; **T1** for claims A and B, which are experimental |
| 3 | **Higuchi T, Takeuchi A, Munesue S, et al.** *A nonsteroidal anti-inflammatory drug, zaltoprofen, inhibits the growth of extraskeletal chondrosarcoma cells by inducing PPARγ, p21, p27, and p53.* Cell Cycle 2023. doi:10.1080/15384101.2023.2166195, PMID 36636023, PMC10054153 *(abstract retrieved; not open access — full text NOT read)* | zaltoprofen → PPARγ mRNA + protein induction, via Krox20 / C/EBPβ / C/EBPα, in **H-EMC-SS** cells; p21/p27/p53 up; growth inhibition in vitro; *"inhibited tumor growth, induced tumor cell apoptosis … in a mouse model of extraskeletal myxoid chondrosarcoma"* | ★ **AGONISM** — the **only functional test of the direction that exists** | **T1**, and see Finding 3 for why it is T1-with-an-asterisk |
| 4 | pioglitazone + trabectedin in **myxoid liposarcoma**, *Clin Cancer Res* 2019;25:7565 | — | ⚠ **NOT EMC, and NOT RETRIEVED.** The literature cache records **HTTP 403** for this URL, so its text has never been read in this repository. It is a *different fusion* (FUS::DDIT3) in a *different disease*; it is analogy, not EMC evidence | **T0 by analogy**, and unverified at the text level |

★ **This is the actual state of the question: it has been asked twice and answered inconsistently,
from the same underlying observation, by two independent groups.** That is a materially different
finding from "nobody has spent an hour on it", which is how the route board has described it.

⚠ **And the two are not evenly matched, which is what tips the balance rather than settles it.**
Filion et al. criticise the cohort behind the antagonism proposal, by name and in their introduction
— verbatim: the earlier profiling study *"used samples in which the diagnosis of EMC was not
independently confirmed by testing for EWS/NR4A3 or other related but less common EMC-specific gene
fusions"* (their reference 31 **is** Subramanian et al. 2005). Filion's own three cases *were* verified
fusion-positive by RT-PCR. So the antagonism proposal rests on a molecularly-unconfirmed cohort **and** on
no functional experiment, while the agonism proposal rests on a fusion-confirmed cohort **and** has
one functional experiment behind it. ⛔ **That is an asymmetry in evidence quality, not a resolution**
— an over-expression finding can be right in a cohort whose diagnosis was made histologically, and
neither paper tested either drug in EMC.

Two further readings from the retrieved text, both bearing on the sign:

- **Filion et al. state the general ambivalence themselves**, verbatim: PPARG *"is generally believed to act as a tumor suppressor through induction of differentiation or apoptosis, or inhibition of proliferation or angiogenesis. However some studies are not entirely consistent with this view"* — and they go on to note that transgenic over-expression models suggest the receptor *"may be cancer-permissive"*. **The field-level prior is itself two-signed**, so it cannot be used to break the tie.
- **The receptor's level in EMC may be actively buffered.** Filion et al. report that a C-terminally truncated native NR4A3 isoform is *"very highly expressed in tumors positive for EWSR1/NR4A3"* and that co-transfection indicates it *"may negatively regulate the activity of the fusion protein on the PPARG promoter"*. Their reading: *"the amount of PPARG may be an important factor with regards to its tumoral function."* ⚠ A dose-sensitive axis is exactly the kind on which agonism and antagonism can both be wrong, and it is another reason A+B do not settle C.

---

## 5 · Finding 3 — the one functional experiment stands on this repository's own disputed model

⛔ **`H-EMC-SS` is `OBJ-LINE-HEMCSS`.** The Higuchi 2023 abstract names *"human extraskeletal
chondrosarcoma **H-EMC-SS** cells"* — the same line as DepMap `ACH-001519` / Cellosaurus `CVCL_1238`,
which `research/manuscripts/emc-systems-map.json` registers with
`verdict: NOT_FUSION_POSITIVE_PER_CURATED_RECORD`, on Cellosaurus's verbatim caution *"Does not
harbor a gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma
(PubMed=34413129)"* plus a DepMap fusion-caller reading naming no FET gene.

**This link had never been drawn in prose.** It was already sitting in a committed artifact —
`research/modalities/emc-atr-vulnerability.json` carries a Europe PMC `"H-EMC-SS"` search whose first
row **is** PMID 36636023 — and no document connected it to the PPARγ lead that
`repurposing-hypotheses.md` grades as its top novel candidate on **in-vivo EMC evidence**.

Three consequences, and the middle one is the load-bearing one:

1. **The strongest evidence for agonism is weakened, not withdrawn.** A growth-inhibition result in a sarcoma line of contested identity is still a real result about a real cell line; what it may not do is ground a sentence of the form *"in EMC, activating PPARγ inhibits growth."*
2. ⚠ **THE ABSTRACT DOES NOT NAME THE LINE USED IN THE MOUSE EXPERIMENT.** It says *"a mouse model of extraskeletal myxoid chondrosarcoma"* and names H-EMC-SS only for the in-vitro work. The paper is **not open access and its full text was not retrieved**, so whether the xenograft is an H-EMC-SS xenograft is **UNREAD, not unaffected** — an absent reading is not a reading of absence (CLAUDE.md §4). **Do not write either way until the full text is read.**
3. **Filion's 2009 condition was never met.** He wrote that the agonist proposal could be tested *"in vitro if genuine EMC cell lines become available"*. The in-vitro test that eventually ran used the line whose EMC identity the curated record does not support. That is a straight line from a 2009 caveat to a 2026 correction, and it is worth one sentence in the paper.

---

## 6 · The answer

**Direction: UNRESOLVED, leaning AGONISM, at tier T1-with-a-model-caveat.** Stated at full honesty:

- ✅ **Settled (T1):** PPARG is over-expressed in EMC relative to other sarcomas — **two independent cohorts, concordant** (10 EMCs, Subramanian 2005; 3 fusion-positive EMCs, Filion 2009), with protein-level corroboration by Western blot / IHC in the second.
- ✅ **Settled (T1):** the fusion can transactivate through a response element in the *PPARG* promoter — band-shift plus transient transfection (Filion 2009). ⚠ Heterologous reporter in transfected cells, not an endogenous EMC readout.
- ⚠ **Not settled (the question):** which direction of pharmacological intervention follows. **Published proposals exist for both signs**, each in a discussion section with no EMC functional experiment behind it (Subramanian 2005 → inhibitors; Filion 2009 → agonists), and they are not evenly matched on cohort quality (§4).
- ★ **The tie-break, such as it is:** exactly **one** functional experiment has ever tested the direction, and it points to **agonism** (Higuchi 2023) — carrying the model-identity caveat of §5. Nothing anywhere tests the antagonism direction in EMC or an EMC model.
- ⛔ **Never measured, by anyone — ⚠ SUPERSEDED 2026-08-28, SEE §6a; RETAINED VERBATIM:** PPARγ **transcriptional output** in EMC. Every EMC reading is of receptor *abundance* (transcript, protein, IHC). No published work reports a PPARγ target-gene signature, a ligand-occupancy readout, or a receptor-activity assay in EMC tissue. **That, not "an EMC expression dataset", is the measurement the redundancy argument actually turns on** — abundance is already measured, twice, concordantly.

### 6a · ⭐ UPDATE 2026-08-28 — the measurement §6 calls "never measured, by anyone" HAS been made, in this repository, and it does not settle the direction

**What changed.** The bullet above and item 4 of the table below both file PPARγ receptor *activity*
behind `BLK-NO-EMC-DATA` as the one thing still owed. It is no longer owed. Six PPARγ-related gene
sets were scored in EMC tumour tissue on both readable array platforms, each pinned to a verbatim
source term with its species read off the term, each null-calibrated on its own platform, with a
knockout-UP falsifier arm and an adipogenesis process proxy carried alongside. **The analysis, and
every figure in it, lives in
[`nr4a3-fusion-transcriptional-output-SI.md`](../fusion-output/nr4a3-fusion-transcriptional-output-SI.md)
§S4**, computed from
[`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) `reads.read_3_PPARG_ACTIVITY`.
⛔ **No number from it is repeated here** — that section is its one home, and this memo points.

**What it says, and this memo does not soften it.** PPARγ target genes are coordinately higher in
EMC tumour tissue than in comparator sarcomas, beyond a size-matched random set, on two platforms.
And the same data **cannot distinguish that from an adipogenic differentiation programme**: the
adipogenesis proxy is set-specific up on both platforms too, is itself significant under permutation,
and has the table's largest overlap with the occupancy-derived arm. Most arms are mouse-derived, which
is an orthology assumption carried into human tumour transcripts.

⛔ **So the direction verdict of §6 is UNCHANGED — *unresolved, leaning agonism, T1 with a
model-identity caveat*.** This measurement does not move it, and the SI says so in its own words:
it says nothing about the direction of any pharmacological intervention on this axis.

★ **What genuinely changes is what the two routes are waiting FOR, and it is not more data.** Both
`RT-PPARG-DOWNSTREAM` and `RT-TRABECTEDIN-PPARG` filed this behind `BLK-NO-EMC-DATA` and, through it,
behind `TECH-EMC-EXPRESSION-DATA` (forecast 2029). The obstacle turns out not to be data availability
— the data existed and was read — but that **bulk archival tissue cannot separate receptor output
from lineage composition**. A further bulk expression cohort does not lift that; a readout that
resolves cell type does. ⚠ This is a bounded statement about what these two platforms can support,
not a claim that the separation is impossible.

⚠ **Nothing here asserts efficacy, safety or clinical use of pioglitazone, zaltoprofen, any
thiazolidinedione, trabectedin, or any combination.**

**So the honest one-liner for any document that needs one:**

> In EMC the *PPARG* gene is over-expressed and the EWSR1::NR4A3 fusion can drive its promoter, but
> the useful **direction** of pharmacological intervention is unresolved: the two EMC expression
> studies that report *PPARG* proposed opposite directions from the same observation, and the single
> functional experiment favouring agonism was performed in a cell line whose EMC identity the curated
> record does not support.

### What is still owed, in ascending cost

| # | what | cost | who can do it |
|---|---|---|---|
| 1 | Read the **Higuchi 2023 full text** and settle whether the xenograft is an H-EMC-SS xenograft (§5 point 2) | $0 CI, one publisher fetch | this repo, once Actions unblocks |
| 2 | Run the dispatched PPARγ × chondrosarcoma query and read the **chondrosarcoma TZD reports** the Higuchi abstract alludes to (*"PPARγ … has been reported as an antitumor target for chondrosarcomas"*) — none has been retrieved here | $0 CI | this repo, run `31126146908` |
| 3 | Retrieve the **CCR 2019 pioglitazone + trabectedin** text, which this repository cites and has never read (403 on record) | $0 CI | this repo |
| 4 | ~~A **PPARγ target-gene signature** in EMC tissue — the measurement nobody has made~~ **✅ TAKEN 2026-08-28 — see §6a.** It was made, it is null-calibrated, and it does not settle the direction: the adipogenic ceiling in SI §S4 is the reason | done, $0 | ~~`BLK-NO-EMC-DATA`~~ — the residual is a study-design limit, not a data-availability one |

⚠ Items 1–3 are all **$0 CI and none is on any route's blocker list.** Item 4 is the only one that
genuinely waits on data, and it is a **narrower** ask than the "EMC expression readout" the route
records name: abundance is already known, so the question is activity.
⚠ **SUPERSEDED 2026-08-28 for item 4 only** — *"the only one that genuinely waits on data"* was true
when written; the data was read on 2026-08-24 and item 4 is now taken (§6a). Items 1–3 stand.

---

## 7 · What this does to the two routes

**`RT-TRABECTEDIN-PPARG` — LIVE.** Its `readiness` is `experimental_proposal` and its **only** listed
missing item is *"the direction of the PPARγ effect in EMC"*. That item is now answerable as a
stated, cited direction with an explicit tier — *unresolved, leaning agonism, T1 with a named
model-identity caveat* — which is what a proposal needs in order to state its own premise. It does
**not** need to wait on `TECH-EMC-EXPRESSION-DATA` (forecast 2029) to say that much.

⚠ **Two things move in opposite directions and both must be reported.** The route's premise is
*better* than recorded — the redundancy worry (§3) is not sourced and the cited author argues the
other way — while its supporting evidence is *weaker* than recorded, because its one functional leg
stands on a disputed model (§5). The net is a route that can now state its premise honestly, and a
proposal whose evidence paragraph must name a weakness it was not naming before.

**`RT-PPARG-DOWNSTREAM` — its blocker is REFRAMED, not retired.** Its record files the direction
question behind `BLK-NO-EMC-DATA` → `TECH-EMC-EXPRESSION-DATA` (forecast 2029). Two corrections:
the literature half was **answerable today and has now been done**, and the data half is
**mis-specified** — what is missing is a receptor-*activity* readout, not another abundance readout.
The route's `remaining_unknowns` line *"in EMC the fusion appears to turn PPARγ on, so an agonist may
be redundant"* should not survive §3.

⛔ **What this does NOT do.** It does not make either direction certain, does not make PPARγ a
validated target in EMC, and asserts nothing about efficacy, safety or clinical use of pioglitazone,
zaltoprofen, any thiazolidinedione, trabectedin, or any combination of them. A repurposing hypothesis
asserts no efficacy for any agent it names, and this memo keeps that true.

---

## 8 · `map_edits_required` — DESCRIBED, NOT APPLIED

Per the convention in `research/modalities/paralogue_pocket_contrast.py`. These touch files this pass
is not permitted to edit (`systems/graph/*`, `systems/views/*` are generated, and the roadmap is
read-only here). **Nothing below has been applied.**

| # | target | current text | proposed change | basis |
|---|---|---|---|---|
| **1** | `systems/graph/routes.json` → `RT-PPARG-DOWNSTREAM` → `remaining_unknowns[0]` | *"The direction is unresolved rather than refuted: in EMC the fusion appears to turn PPARγ on, so an agonist may be redundant. Nobody has read the direction in EMC tissue."* | Replace with: *"The direction is unresolved rather than refuted, and the reason is not absence of study: the two EMC expression studies that report PPARG proposed OPPOSITE directions from the same observation (Subramanian 2005 → PPARG inhibitors; Filion 2009 → PPARG agonists), and the single functional test favouring agonism was run in H-EMC-SS (`OBJ-LINE-HEMCSS`, identity disputed). ⚠ The redundancy clause is WITHDRAWN — it is not in the source it cited, and Filion et al. argue the opposite in their own discussion."* | this memo §3, §4 |
| **2** | `systems/graph/routes.json` → `RT-PPARG-DOWNSTREAM` → `required_validation` row 1 | *"A literature read of the PPARγ-axis direction in EMC … via the Europe PMC CI lane — feasible today"* | Mark **DONE 2026-08-06**, artifact `research/manuscripts/repurposing/pparg-direction-emc.md`; add a new open row: *"A PPARγ TARGET-GENE (activity) readout in EMC — blocked by `BLK-NO-EMC-DATA`"*, and re-scope the existing expression row from abundance to activity, since abundance is measured | §6 |
| **3** | `systems/graph/routes.json` → `RT-TRABECTEDIN-PPARG` → `readiness.missing` | *["the direction of the PPARγ effect in EMC"]* | Replace with: *["the direction stated at T1 with a model-identity caveat — see `pparg-direction-emc.md`; what remains missing is a PPARγ ACTIVITY readout in EMC, not an abundance one"]*. Consider `timing.recommendation` `wait` → `pursue_now` for the write-up half; the wet-lab ask stays behind `BLK-NO-WET-LAB` | §7 |
| **4** | `systems/graph/routes.json` → both routes → `remaining_unknowns` | — | Add: *"The in-vivo evidence for agonism (Higuchi 2023) uses H-EMC-SS; whether the MOUSE experiment used that line is UNREAD — the paper is not open access and its full text has not been retrieved."* | §5 point 2 |
| **5** | `systems/graph/evidence.json` → `EV-FILION-2009` → `what_it_supports` | *"…the fusion→PPARG axis both PPARG routes rest on…"* | Append: *"⚠ It supports the AXIS, not a DIRECTION. The paper's own discussion proposes PPARγ AGONISTS; it has been cited in this repository for the opposite (a redundancy argument) and must not be again."* Also add `misattributed_as: ["the source of the agonist-redundancy argument"]` | §3 |
| **6** | `systems/graph/evidence.json` | — | Register **two new evidence items**: `EV-SUBRAMANIAN-2005` (PMID 15920699, doi 10.1002/path.1792 — the antagonism proposal and the independent PPARG/PPARGC1A over-expression cohort) and `EV-HIGUCHI-2023` (PMID 36636023, PMCID PMC10054153, doi 10.1080/15384101.2023.2166195 — the only functional test of the direction), the latter cross-linked to `OBJ-LINE-HEMCSS` | §4 |
| **7** | `research/manuscripts/nr4a3-program-map.md` | the PPARγ entries filed behind the 2029 expression-data forecast | Record that the literature half was **never blocked by a 2029 forecast** and is now closed; re-file the residual as an **activity** readout | §6, §7 |
| **8** | `research/manuscripts/program/path-family-synthesis.md` Tier 3 row 13 | *"Stalled on one literature question — agonism vs antagonism — that nobody has spent an hour on"* | Correct: the hour has been spent, and the finding is that the question was answered **inconsistently** by two primary studies rather than left unasked | §4 |

---

## 9 · Files this memo is the one home for

- **The sign of the PPARγ axis in EMC and its tier** — quoted, not restated, everywhere else.
- **The retraction of the agonist-redundancy premise** (§3).
- **The Higuchi 2023 ↔ `OBJ-LINE-HEMCSS` link** (§5).

Anything that needs one of these **points here**; per CLAUDE.md §1 it does not retype it.
