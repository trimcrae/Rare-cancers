---
id: DOC-RELEASE-DOI
title: Citable snapshots with a Zenodo DOI (Tier-B low-latency dissemination)
level: —
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under deploy/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Citable snapshots with a Zenodo DOI (Tier-B low-latency dissemination)

The journal paper is slow; the roadmap moves weekly. This is the **middle tier** from
`research/manuscripts/program/emc-treatment-strategy.md` (Q4): a way to mint a **citable, versioned DOI** for
the current state of the roadmap in minutes, so collaborators/reviewers can cite "the roadmap as of
2026-06-24" while the formal paper is in review.

## How it works
1. **GitHub Release → Zenodo → versioned DOI.** Once the repo is connected to Zenodo, every published
   GitHub Release is automatically archived and assigned a DOI. Zenodo also mints a *concept DOI* that
   always resolves to the latest version.
2. **Metadata is pre-filled** from `CITATION.cff` and `.zenodo.json` in the repo root (title, author =
   Tristan D. McRae, license, keywords, abstract). Zenodo reads these at archive time.
3. **Release notes = the roadmap changelog.** `.github/workflows/release.yml` auto-extracts the
   changelog block from `emc-treatment-roadmap.md` into the release body.

## Two tiers, and this file is tier 1

⛔ **A GitHub Release archives the WHOLE REPOSITORY.** That is the right shape for citing a living
project and the wrong shape for citing a paper: a reader following a paper's archive DOI would land
on a record spanning forty routes, and a concept DOI *moves*, so a published paper whose
availability statement names it would point at an archive that changes whenever an unrelated route
cuts a release.

- **Tier 1 — the repository record.** This file. One record, concept DOI resolves to the newest
  release. Cite it for the project as a living document.
- **Tier 2 — one deposit per paper.** [`.github/workflows/deposit-zenodo.yml`](../.github/workflows/deposit-zenodo.yml)
  and [`scripts/zenodo_deposit.py`](../scripts/zenodo_deposit.py). Each paper's archive manifest
  already names its own file set — the ASO manifest names 473 of the repository's 3,453 tracked
  files, each with the role it plays — and the deposit carries exactly those. Corrections become new
  versions of *that paper's* record, so a reader arriving from the published paper lands on the
  version it was written against. **This is what a manuscript's `[ARCHIVE DOI]` placeholder wants.**

## One-time setup (manual — needs your accounts; I can't do these)
1. Sign in at https://zenodo.org with GitHub.
2. Zenodo → **profile → GitHub** → flip the toggle **ON** for `trimcrae/Rare-cancers`.
   (Only releases created *after* the toggle get DOIs.)
3. ~~Before the first release, finish the metadata: add your **ORCID**~~ ✅ **done 2026-08-20** —
   `CITATION.cff` and `.zenodo.json` both carry `0000-0002-1823-1451`. The title and description in
   both files were also broadened from the roadmap to the repository; see the tier note above.
4. *(Optional)* add the Zenodo DOI badge to `README.md` after the first release.

## Cutting a release (repeatable, ~minutes)
1. Add a dated entry to the **Changelog** at the top of `emc-treatment-roadmap.md`.
2. From **`main`**, run the **Release** workflow (Actions → "Release — citable roadmap snapshot") with
   a date-based `version`, e.g. `v2026.06.24`. It tags the commit and creates the GitHub Release;
   Zenodo mints the DOI automatically.
3. **Cadence:** cut a release on any **Tier-1/2 route change** (or monthly if anything changed).

> **Note — this is permanent and outward-facing.** A published release + DOI cannot be un-minted.
> The workflow is dispatch-only and is never run automatically. Don't dispatch it until the Zenodo
> toggle and author metadata (ORCID) are set.

## License note
Code is **Apache-2.0** (repo `LICENSE`) — a fine, permissive start: it allows reuse with attribution,
which is all "publish-to-convince" needs. If you later want the *manuscript text* to match the
academic-preprint norm, the common choice is **CC-BY-4.0** for the prose while code stays Apache-2.0;
that is an optional refinement, not a blocker. The current metadata declares Apache-2.0.
