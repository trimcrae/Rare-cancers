# EMC atlas — collaborator outreach preparation

> **DRAFTS for trimcrae to review, personalise, and send under a named human author. Do NOT auto-send
> — outward-facing contact requires trimcrae sign-off + a real sender identity (repo human-in-the-loop
> rule).** Nothing here impersonates a real person or organisation; recipients are described by role,
> with `[bracketed]` placeholders for the sender's name/affiliation and the specific addressee. Pair
> each email with `collaborator-brief.md` (the 2-page evidence package).

## Target map — who to approach, why, and with which program

| Target (role) | Why them | Lead ask | Primary artifact |
|---|---|---|---|
| **The USZ / NCC EMC-model owners** (the groups that built USZ20-EMC1, USZ22-EMC2, NCC-EMC1-C1) | They hold the only three modern EMC models; the whole proteostasis-chromatin validation runs on them | Run the 12-compound / 6-combination class-vs-compound panel; we do all analysis | Program 1 (proteostasis-chromatin) |
| **The Stacchiotti / European sarcoma network** (pazopanib, sunitinib, IMMUNOSARC II, anthracycline cohorts) | Nearly all EMC systemic evidence + the primary-confirmed EWSR1-vs-TAF15 differential comes from this group | Share de-identified, fusion-annotated, response-linked data for the growth-rate-adjusted biomarker analysis | Program 2 (antiangiogenic biomarker) + the CRF |
| **A sarcoma referral centre / molecular pathology group** | Archival EMC tissue + immunopeptidomics/IHC capacity | Confirm fusion-junction/lineage antigen presentation on real EMC tissue | Antigen axis (junction + lineage) |
| **The SGC (Structural Genomics Consortium) / NR4A chemical-biology groups** | Tool compounds + the orphan-NR4A ligandability problem | Collaborate on NR4A3 ligand discovery to enable the direct-fusion route | Direct-fusion route (long-horizon) |
| **EMC / sarcoma patient foundations** | Funding + tissue-network access + patient-registry reach | Fund the wet-lab validation package; connect models/tissue | Whole program (Phase B) |

## Email drafts

### 1 — To the EMC model-owning group (Program 1: proteostasis-chromatin)

> **Subject:** Ready-to-run validation panel for your EMC models — full computational support, no cost to your lab
>
> Dear [Dr. ___],
>
> I'm an independent computational researcher who has built an open, reproducible **EMC Open Target &
> Drug Atlas** integrating every usable EMC dataset, model, and drug screen with a transparent evidence
> score. Your [USZ / NCC] models are central to its strongest preclinical hypothesis.
>
> Two independent screens (yours included) converge on a **proteostasis–chromatin vulnerability** —
> proteasome (carfilzomib), HSP90 (PU-H71), and HDAC (panobinostat/romidepsin). I've assembled a
> **12-compound / 6-combination, class-vs-compound validation panel** (so effects attribute to the
> target, not one chemical), with pre-registered go/no-go criteria, concentrations chosen against
> achievable human exposure, and mechanistic readouts. A public DepMap analysis I ran shows these
> targets are pan-essential — so the key question is a therapeutic-window/pharmacology one, which the
> panel is designed to answer.
>
> I would provide **all** experimental design, analysis, and manuscript support; I'm asking whether your
> lab would run the panel in the EMC models (plus the controls specified). A 2-page evidence brief,
> plate-map-ready panel, and draft figure set are attached.
>
> [Name, affiliation, links to the atlas repository]

### 2 — To the clinical sarcoma network (Program 2: EWSR1-vs-TAF15 antiangiogenic biomarker)

> **Subject:** Fusion-subtype antiangiogenic biomarker in EMC — a growth-rate-adjusted re-analysis proposal
>
> Dear [Dr. ___],
>
> Your group generated essentially all the systemic-therapy evidence in EMC. Your sunitinib data state
> that responders carried EWSR1::NR4A3 while refractory cases carried TAF15::NR4A3, and the pazopanib
> responders were EWSR1-fused — a fusion-subtype biomarker that could improve treatment selection now.
>
> I've built a reproducible atlas of the EMC evidence and a response-linked common data model with
> **growth-rate-adjusted endpoints** (pre- vs on-treatment growth, growth-modulation index,
> time-to-next-treatment) — because in an indolent disease, stable disease alone overstates activity. I
> propose a re-analysis that tests whether the EWSR1-vs-TAF15 signal predicts *growth-rate-adjusted*
> benefit and survives leave-one-patient-out, plus a kinome-level comparison of the active TKIs.
>
> Your institution would own consent, ethics, and de-identification; I would provide the data model,
> statistical plan, and analysis. Would you be open to discussing a de-identified, fusion-annotated,
> response-linked dataset?
>
> [Name, affiliation, links]

### 3 — To a sarcoma pathology / immunopeptidomics group (antigen axis)

> **Subject:** Testing EMC fusion-junction & lineage antigens on real tissue
>
> Dear [Dr. ___],
>
> EMC's recurrent NR4A3 fusion and lineage program offer tumour-specific antigens. In-silico, the
> EWSR1::NR4A3 junction is modest on MHC-I but carries a **strong predicted CD4 helper epitope**
> (QYSQQSSSYGQQPCV / DRB1*07:01), and fusion-induced lineage markers (CHRNA6, NMB, plus B7-H3/PRAME by
> surrogate) are candidate surface/antigen targets — all of which need confirmation on real EMC tissue,
> since RNA abundance does not equal surface protein.
>
> I have a ranked candidate list, a mass-spec inclusion list, and a validation ladder. Would your group
> consider targeted immunopeptidomics / IHC on archival EMC to test natural presentation? I'd provide
> the full computational package and analysis.
>
> [Name, affiliation, links]

## Pre-send checklist (trimcrae)
- [ ] A named human author (ideally a sarcoma clinician/researcher) is on the correspondence.
- [ ] Sender identity and affiliation are real; no impersonation.
- [ ] The attached brief's `verification_level` caveats are intact (no over-claiming).
- [ ] The atlas repository link is public/shareable as intended.
- [ ] No identifiable patient data is requested directly by an unaffiliated individual (institution owns it).
