# NR4A3-degrader paper → preprint: conversion plan & checklist

> **✅ CLEAN PREPRINT DRAFTED (2026-07-01): [`nr4a3-degrader-preprint.md`](./nr4a3-degrader-preprint.md).**
> The conversion pass below is largely done — scaffolding stripped, front matter added, `denovo_401` stated
> at its frame-dependent weight, ternary omitted (future work). **Remaining before posting:** fill in
> author/affiliation/corresponding-email; render the figures (incl. the release-vs-metad decoy-null contrast
> panel); confirm the target journal's preprint policy; then post to ChemRxiv + send the outreach emails.
> The working doc [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) is kept as the internal red-teamed record.

**Goal:** turn the working manuscript ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)) — which is
currently an *internal, red-teamed working doc* — into a clean, self-contained **preprint** for immediate
posting, with journal submission in parallel. Regime: `emc-treatment-strategy.md → "Operating regime
(2026-07-01)"`. Started 2026-07-01.

## Target venue
> **✅ FEE/POLICY CONFIRMED IN WRITING (2026-07-05).** ChemRxiv posting is **free** (CC-BY option; hosted on
> Cambridge Open Engage; co-owned by ACS/RSC/CCS/CSJ/GDCh — no prejudice to a later ACS submission; no
> embargo/scooping issue). **JCIM (ACS) has a confirmed $0 subscription route** — authors may opt out of open
> access and publish paywalled at no cost (the paid ACS Open Access upgrade, ~$2.5–5k, is optional). JCIM
> **explicitly allows ChemRxiv preprints** (note it in the cover letter; may revise the preprint until final
> acceptance; link the preprint to the published DOI). Scope fits a no-wet-lab computational/generative-design
> paper. **Digital Discovery is OUT as a planned free route** (fully gold OA, mandatory £2,200 APC; waivers are
> discretionary, unsuitable for an unaffiliated solo author). **J. Med. Chem. is OUT on scope** (wants
> synthesized compounds), not fee. → **Plan of record: ChemRxiv (CC-BY) + JCIM subscription route.** Only
> unread live figure: exact JCIM gold-OA APC $ (irrelevant — the $0 route is the plan); eyeball the live JCIM
> cover-letter preprint wording at submission.


> **HARD CONSTRAINT (trimcrae, 2026-07-05): NO pay-to-publish. Author pays $0.** The preprint is free, and the
> journal must have a **free (subscription/hybrid) route** — publish subscription-side and let the free ChemRxiv
> preprint be the open copy. Fully open-access / APC-only journals (IJMS, PLOS, Sci. Rep., Frontiers) are OUT
> unless a **full fee waiver** is secured up front. Do not submit anywhere that can bill the author.

- **Preprint: ChemRxiv** (med-chem / comp-chem home; best fit for a cryptic-pocket + de-novo-design paper).
  **Free ($0).** Post immediately once the two pending results land. bioRxiv is the alternative if we lean the
  framing biological (also free). The preprint does most of the outreach work regardless of the journal.
- **Journal (parallel submission) — fee model matters as much as fit:**
  - **✅ FREE route exists (subscription/hybrid — publish at $0, paper paywalled, preprint stays the open copy):**
    - ***J. Chem. Inf. Model.*** (ACS) — **top pick.** Best audience/credibility fit; publish subscription-side
      for $0 (skip the paid ACS-OA upgrade, ~$2.5–5k, which is optional).
    - ***J. Med. Chem.*** (ACS) — same $0 subscription route, but poor *fit* (wants synthesized compounds +
      wet-lab data; likely desk-reject for a no-wet-lab paper). Fee isn't the blocker here — scope is.
    - ***Digital Discovery*** (RSC) — hybrid; free subscription route. Good if we lean the *method* (generative +
      decoy-null calibration). Confirm no mandatory APC before submitting (RSC is shifting some titles to OA).
  - **❌ APC-only (author pays, NO free route — OUT unless a full waiver is granted):** *IJMS* (~$2,900),
    *PLOS Comput. Biol.* (~$2,300–2,900), *Sci. Rep.* (~$2,700), *Front. Pharmacol.* All are fully OA. Only
    revisit via a documented **fee waiver** (PLOS has a formal no-funding waiver program; MDPI/Frontiers
    sometimes discount) — and only if a $0 subscription venue has already rejected it.
  - All are preprint-friendly (confirm each journal's preprint policy before submitting — nearly all allow
    ChemRxiv). **Confirm the $0 route in writing at submission**, since journal fee policies change.
- **Framing (per the honest-assessment note):** sell it as **first-in-target computational characterization of
  NR4A3 druggability/selectivity + a decoy-null-screened *designed/predicted* candidate (a foothold, not a
  fully control-validated one — the decoy null does not control the generative step; F16 red-team)** — NOT as a
  methods advance, NOT as a validated drug. Every candidate claim reads "predicted / designed," never
  "selective," and never "control-validated" unqualified.
- **Abstract (F20):** the working-doc abstract is ~90 lines and tracks three successive leads through two
  retractions; the preprint abstract must state the honest bottom line cleanly (feasibility druggability +
  one de-noised foothold, no FEP, no wet lab). Keep it tight; do not re-import the retraction history.

## Results status (2026-07-01)
1. **Metad-frame decoy null — DONE (partial-negative, folded in).** `denovo_401` clears the decoy null in its
   release/design frame (+12.83 vs 95th +6.69) but **NOT** in the biased metad-opened frame (+7.44 vs 95th
   +17.70, max decoy +24.74) — a **receptor-frame-dependent** hit. Already in abstract/§2.6/§5-caveat-7/§6/prereg.
   → **State the candidate at this (frame-dependent) weight throughout the preprint; do not upgrade it.**
2. **Ternary control — DONE + VALIDATED (2026-07-01, after 4 infra walls; see next-steps handoff).** Boltz-2
   seats lenalidomide in CRBN's tri-Trp pocket (2.85 Å to W380; ligand-iPTM 0.99), recovering the known IMiD
   mode → the degradation-geometry pipeline is trustworthy. **Folded into §2.7 + Limitations (not a new §2.8;
   no Fig 6)** as a validated-positive-control note. The **NR4A3-specific degradation-geometry prediction
   (Stage 2) is still future work** — needs a warhead PROTAC — stated as such in Discussion/Limitations.

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
      control → 2.6 multi-snapshot + decoy-null → **2.7 selectivity architecture**) · Discussion (incl. the
      ternary/degradation-geometry model as future work) · Limitations · Methods · Data/Code availability ·
      References. *(No §2.8 — the ternary is deferred; see Results status above.)*

## Front matter to add
- [ ] **Title** — current: *"Computational design of a selective NR4A3 degrader: opening a cryptic pocket in
      a 'ligand-independent' nuclear receptor."* **Author decision:** the deliverable is a cryptic-pocket
      druggability case + a selective *warhead* candidate + a *validated ternary pipeline* — not a completed
      degrader. "degrader" describes the program's aim and is defensible (the abstract is explicit about scope),
      but a reviewer-proof alternative leads with the concrete result, e.g. *"Opening a cryptic pocket in the
      'undruggable' nuclear receptor NR4A3: computational druggability and a selective degrader-warhead
      candidate."* Pick one before posting.
- [x] **Authors / affiliations** — **DONE:** sole author **Tristan D. McRae** (Independent researcher;
      correspondence trimcrae@gmail.com), set in both the preprint and the SI. **Claude is NOT a co-author**
      (ACS/JCIM and essentially all venues disallow AI authorship) — it stays as the AI-assistance statement in
      Methods, which is already present.
- [ ] **Abstract** — ready to finalize now (metad-frame decoy null folded in; ternary deferred). Trim its
      internal red-team scaffolding to a clean results paragraph.
- [ ] **Data & Code Availability** — point to the public GitHub repo + note S3 artifacts available on request;
      list the key scripts.
- [ ] **Competing interests / Funding** — "no funding; no competing interests" (accurate at solo scale).
- [ ] **AI-assistance statement** — disclose Claude use in Methods (standard, increasingly required).
- [ ] **License** — CC-BY for the preprint (maximizes reuse / pickup).

## Figures & tables (from `nr4a3-degrader-figures.md`)
- [ ] Finalize Fig 1 (calibration), Fig 2 (cryptic opening + release), Fig 3 (handles), Fig 4 (matrix), Fig 5
      (de-novo + decoy control + multi-snapshot — already reframed around denovo_401; **add the release-vs-metad
      decoy-null contrast panel** showing the frame-dependence). *(No Fig 6 — ternary deferred.)*
- [ ] Render via `render-figures.yml`; ensure each caption states its data weight (model / biased-MD / docking-
      prior / MM-GBSA-direction) and that the candidate is *predicted*.

## Dissemination (do NOT wait for journal acceptance)
- [ ] Post ChemRxiv preprint once the conversion pass is done (results are complete — ternary deferred).
- [ ] **Outreach** — ready-to-send email drafts are in
      **[`nr4a3-degrader-outreach-emails.md`](./nr4a3-degrader-outreach-emails.md)** (5 templates: NR4A/NR
      structural labs, the de Vera / Nurr1-pocket group, the **SGC**, sarcoma/EMC translational labs,
      rare-cancer foundations). Fill in `[PREPRINT_URL]`/`[DOI]`/`[REPO_URL]` + personalise one line each,
      then send the day the preprint posts. Log responses in that file's tracking table.
- [ ] Submit to the chosen journal in parallel.

## Handling new in-silico science that lands *while the paper is in review*
This is a long-lived project on a rising in-silico frontier (`method-watch.md`), and the journal clock is
long (JCIM: ~6 wk to first decision, ~5–9 mo submission→online realistically). So new capability/results
**will** land mid-review. That does **not** mean holding submission indefinitely — "something better lands in
6 months" is always true, so novelty alone is never the trigger. The **preprint decouples dissemination from
the journal clock**: ChemRxiv is *versioned* (post v2/v3 anytime), so new science reaches the outreach
audience immediately regardless of where the journal copy is frozen. Route each new result by a **materiality
test**, not by novelty:

| New science… | Channel | Why |
|---|---|---|
| **changes a conclusion / fixes a load-bearing weakness** (e.g. a structure model that *corroborates the cryptic pose* Boltz couldn't; a converged cheap cryptic-pocket FEP running the SKIP'd `denovo_401` selectivity FEP; better induced-fit docking that resolves the +12.83-release-vs-+7.44-metad frame-dependence) | **Fold into the revision round** (free — reviewers expect the paper to change; add it in the response). If it lands *pre-decision* and is transformative, **withdraw → strengthen → resubmit** (resets the clock; only for standing-changing results). If it *refutes* a claim, it is **mandatory** before publishing (integrity guardrail). | These touch the claims, so they belong *in* the paper. The revision round is the zero-cost injection point. |
| **adds another confirmatory axis** without changing a conclusion (breadth-first "new axis" work) | **Preprint v2 + a follow-up paper.** Do **not** reopen/withdraw the submission for it. | It's a second paper, not a revision. |
| **routine / reviewer-anticipated** (e.g. the FEP replicate + convergence already queued) | Hold as **revision-ready material**; attach when a reviewer asks (they will). | Not new science — expected hardening. |

**Guardrail (from `method-watch.md`):** a coming capability justifies *waiting or re-running* — it never
licenses claiming a result before the method supports it. **Timing tactic:** don't submit the week before a
*known-imminent, conclusion-changing* capability (the monthly digest flags warming triggers); don't hold for
anything merely confirmatory. After **acceptance** the manuscript is frozen (proof corrections are typo-level
only) — all further new science goes to the preprint and/or a follow-up paper.

## Explicitly NOT doing (per regime)
- No FEP (ceiling-bound; least reliable here) beyond an optional ~$100 spot run only if a reviewer demands it.
- No self-funded wet-lab synthesis/assay ($5–25k) — that's a funded collaborator's call, offered *via* the
  outreach, not a to-do here.
