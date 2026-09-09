---
id: DOC-PUBLIC-PREPRINT-SITE
title: Public preprint landing page
level: —
kind: runbook
status: live
purpose: Build and maintain the public catalogue of posted EMC research preprints.
scope: Curated public metadata, the five-file static build, and GitHub Pages deployment.
audience: [maintainers, autonomous research agents]
date: 2026-09-09
last_verified: 2026-09-09
---

# Public preprint landing page

GitHub Pages publishes only the five public files generated in `site/_site/`. It never uploads the repository, manuscripts, private correspondence, operational state, evidence memos or working drafts.

Build with the installed Python standard library:

```sh
python3 site/build.py
python3 -m http.server 8080 --directory site/_site --bind 127.0.0.1
```

`publications.json` is the explicitly verified public catalogue. Keep one record per paper, using the newest actually posted version, its public title/byline, version date and canonical article link. The repository's general publication graph also tracks unfinished revisions and must not be exported as a list of public papers.

When a new preprint or revision is confirmed public by the research coordinator, update its record and `updated_date` together. Check the public venue page and saved posting receipt. Do not advance a version for a local commit, an upload receipt without public posting, prescreening, or a pending submission. Describe the posted paper's scope; newer working results do not belong in an older public version's summary. The GitHub workflow rebuilds and deploys on changes to this directory. Dates are explicit verification dates, never refreshed merely because CI runs.

The workflow uses `main`, the `github-pages` environment and GitHub's Pages artifact deployment. Repository Settings → Pages must use **GitHub Actions** as its publishing source. Keep repository visibility unchanged. Pages requires an eligible repository/account; do not enable paid services as a fallback.

The local build validates dates, unique paper IDs/URLs, public article destinations and DOI consistency. An output directory containing files outside its public allowlist causes a failure. All assets are local and all paper links point to the original venue; no unpublished PDFs or third-party scripts/fonts are served.

Each record includes live venue `availability`: `available` or `unverified`. If a previously posted paper's public page becomes unavailable or its version cannot be reconciled, retain its documented last confirmed posting with a concise `availability_note`, use the "Check venue" link, and exclude it from current-version structured data. Do not label that version as verified current, infer withdrawal, substitute a working draft, or remove the availability note until a public readback resolves it.
