---
name: add-cancer
description: Add or substantially update a rare-cancer page in this repo. Use when the user wants to create a new cancer page, research a cancer's studies/outcomes/centres/support groups, or populate a data/cancers/<slug>.json file. Enforces the project's medical-integrity rules.
---

# Add a rare-cancer page

Follow this when creating or filling in a cancer page. The full rationale is in
`/AGENTS.md`; this is the executable checklist.

## Non-negotiable: medical integrity
- Never fabricate facts, statistics, citations, or patient data.
- Every clinical claim and number needs a real, working source link. Use ranges
  across studies, not invented precision.
- Patient registry rows are either real + cited (set `dataStatus` to
  `partial-curated`/`curated`) or clearly `SAMPLE_SYNTHETIC` with a banner. Never
  pass sample data off as real.
- Keep disclaimers; never phrase content as a personal recommendation.
- Set `meta.dataConfidence` honestly (`draft` until a human/clinician reviews).

## Steps

1. **Scaffold** (skip if the data file already exists):
   ```bash
   node scripts/new-cancer.mjs <slug> "Full Name" "ABBR" "Category"
   ```
   Slug = lowercase, hyphens only. This creates the data file, the page shell,
   and the homepage entry (as `draft`).

2. **Research with the web** and fill `data/cancers/<slug>.json`. Use the
   pre-filled live-search links (PubMed, Europe PMC, ClinicalTrials.gov, Scholar).
   Fill these sections (model them on `data/cancers/emc.json`):
   - `overview` — plain language; genetics/biomarkers if any
   - `studies.items` — every paper found, each with a real `url`
   - `outcomes` — cited summary stats, prognostic factors, treatment response
   - `registry` — real per-patient rows w/ `source` if possible, else keep
     sample data flagged + bannered (calibrate to published stats)
   - `treatments` (by stage, with disclaimer), `monitoring` (with disclaimer)
   - `supportGroups`, `centers` (centres need `lat`/`lng`),
     `questionsForOncologist`

3. **Validate**:
   ```bash
   node scripts/validate.mjs
   ```
   Fix all errors and address warnings.

4. **Publish** when the content is solid: set the homepage entry `status` to
   `"published"` in `data/index.json` and bump `meta.dataConfidence`.

5. **Commit** to the active branch with a clear message. Do not open a PR unless
   asked.

## Adding a brand-new section/tool for ALL cancers
Edit `assets/js/cancer.js` (keep it null-safe), then update `data/schema.json`,
`templates/cancer.template.json`, and `scripts/validate.mjs` to match. Maintain
zero dependencies and no build step.
