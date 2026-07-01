# NR4A3-degrader paper → preprint: conversion plan & checklist

**Goal:** turn the working manuscript ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)) — which is
currently an *internal, red-teamed working doc* — into a clean, self-contained **preprint** for immediate
posting, with journal submission in parallel. Regime: `emc-treatment-strategy.md → "Operating regime
(2026-07-01)"`. Started 2026-07-01.

## Target venue
- **Preprint: ChemRxiv** (med-chem / comp-chem home; best fit for a cryptic-pocket + de-novo-design paper).
  Post immediately once the two pending results land. bioRxiv is the alternative if we lean the framing
  biological.
- **Journal (parallel submission):** specialized comp-chem tier — *J. Chem. Inf. Model.*, *IJMS*,
  *J. Med. Chem.* (comp), *PLoS Comput. Biol.*, *Front. Pharmacol.*, or *Sci. Rep.* All are preprint-friendly
  (confirm each journal's preprint policy before submitting — nearly all in this list allow ChemRxiv).
- **Framing (per the honest-assessment note):** sell it as **first-in-target computational characterization of
  NR4A3 druggability/selectivity + a control-validated *designed/predicted* candidate** — NOT as a methods
  advance, NOT as a validated drug. Every candidate claim reads "predicted / designed," never "selective."

## Two pending results to fold in before posting
1. **Metad-frame decoy null** (running; run 28483612927 → `nr4a3-decoy-mmgbsa-metad-ms`) → completes
   denovo_401's control battery; update §2.6.
2. **Ternary** (fires when #1 finishes): CRBN+lenalidomide Boltz-2 control → denovo_401-PROTAC degradation
   geometry → a new short Results subsection (§2.8) on degradation-geometry / paralogue ternary. This is the
   mechanism-relevant add for a *degrader* paper.

## Structural conversion (working doc → preprint)
The manuscript carries a lot of *process scaffolding* that must move out of the main text:
- [ ] **Strip the editorial header** (the "ACTIVE LEAD MANUSCRIPT / split out on 2026-06-25 / adversarial
      self-review" banner, lines ~1–18) → replace with a clean **title + author block + one-paragraph
      abstract**.
- [ ] **Remove internal artifacts from the body:** SageMaker run IDs (`run 284…`), "trimcrae"/decision
      attributions, S3 prefixes, workflow filenames, and repo-relative doc cross-links. These go to SI/Methods
      or are dropped. (Keep the *science*; drop the *lab-notebook*.)
- [ ] **Move to Supplementary Information (SI):** the red-team log (`nr4a3-degrader-paper-redteam.md`), the
      pre-registration + deviation log (`nr4a3-druggability-prereg.md`), the full selectivity-architecture
      analysis, and the per-run control tables. Reference them as "SI §X."
- [ ] **Consolidate the caveats.** The body has caveats inline *and* a §5 Limitations *and* per-section honest
      notes — good for rigor, but for a preprint, keep one clean **Limitations** section + brief inline flags;
      push the exhaustive version to SI.
- [ ] **Clean section arc:** Abstract · Introduction (NR4A3/EMC + "undruggable" reputation) · Results
      (2.1 static pocket → 2.2 cryptic opening + release → 2.3 handles → 2.4 matrix → 2.5 de-novo + decoy
      control → 2.6 multi-snapshot + decoy-null → **2.7 selectivity architecture** → **2.8 ternary/degradation
      geometry (new)**) · Discussion · Limitations · Methods · Data/Code availability · References.

## Front matter to add
- [ ] **Title** (candidate): *"Computational design of a selective NR4A3 degrader: opening a cryptic pocket in
      a 'ligand-independent' nuclear receptor."* (already the working title — keep.)
- [ ] **Authors / affiliations** — trimcrae + "Claude (Anthropic)" acknowledgment per preference (decide author
      vs. acknowledgment; most venues want human authors + an AI-assistance statement in Methods).
- [ ] **Abstract** — finalize *after* the ternary lands (it's results-dependent; don't rewrite twice).
- [ ] **Data & Code Availability** — point to the public GitHub repo + note S3 artifacts available on request;
      list the key scripts.
- [ ] **Competing interests / Funding** — "no funding; no competing interests" (accurate at solo scale).
- [ ] **AI-assistance statement** — disclose Claude use in Methods (standard, increasingly required).
- [ ] **License** — CC-BY for the preprint (maximizes reuse / pickup).

## Figures & tables (from `nr4a3-degrader-figures.md`)
- [ ] Finalize Fig 1 (calibration), Fig 2 (cryptic opening + release), Fig 3 (handles), Fig 4 (matrix), Fig 5
      (de-novo + decoy control + multi-snapshot — already reframed around denovo_401), + a **new Fig 6 (ternary
      / degradation geometry)** once that lands.
- [ ] Render via `render-figures.yml`; ensure each caption states its data weight (model / biased-MD / docking-
      prior / MM-GBSA-direction) and that the candidate is *predicted*.

## Dissemination (do NOT wait for journal acceptance)
- [ ] Post ChemRxiv preprint the day the ternary result is folded in.
- [ ] **Outreach shortlist** (draft emails separately): NR4A/nuclear-receptor structural labs; the **SGC**
      (understudied nuclear receptors); **EMC/sarcoma foundations + patient-advocacy orgs**; the de Vera /
      Nurr1-pocket group (natural reviewers/adopters). One short "here's the preprint + data, happy to
      collaborate / hand off" note each.
- [ ] Submit to the chosen journal in parallel.

## Explicitly NOT doing (per regime)
- No FEP (ceiling-bound; least reliable here) beyond an optional ~$100 spot run only if a reviewer demands it.
- No self-funded wet-lab synthesis/assay ($5–25k) — that's a funded collaborator's call, offered *via* the
  outreach, not a to-do here.
