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

GitHub Pages publishes only the eight allowlisted public files generated in `site/_site/`. It never uploads the repository, manuscripts, private correspondence, operational state, evidence memos or working drafts.

Build with the installed Python standard library:

```sh
python3 site/build.py
python3 -m unittest discover -s site -p 'test_*.py'
python3 -m http.server 8080 --directory site/_site --bind 127.0.0.1
```

`publications.json` is the explicitly verified public catalogue. Keep one record per paper, using the newest actually posted version, its public title/byline, version date and canonical article link. The repository's general publication graph also tracks unfinished revisions and must not be exported as a list of public papers.

When a new preprint or revision is confirmed public by the research coordinator, update its record and `updated_date` together. Check the public venue page and saved posting receipt. Do not advance a version for a local commit, an upload receipt without public posting, prescreening, or a pending submission. Describe the posted paper's scope; newer working results do not belong in an older public version's summary. The GitHub workflow rebuilds and deploys on changes to this directory. Dates are explicit verification dates, never refreshed merely because CI runs. When a paper is posted at more than one venue, keep one paper card with the newest confirmed posting as its main link and retain the other verified venue links in `other_postings`. Each additional posting records its venue, version, posting date and canonical public URL.

The workflow uses `main`, the `github-pages` environment and GitHub's Pages artifact deployment. Repository Settings → Pages must use **GitHub Actions** as its publishing source. Keep repository visibility unchanged. Pages requires an eligible repository/account; do not enable paid services as a fallback.

The local build validates dates, unique paper IDs/URLs, public article destinations and DOI consistency. An output directory containing files outside its public allowlist causes a failure. All assets are local and all paper links point to the original venue; no unpublished PDFs or third-party scripts/fonts are served.

Each record includes live venue `availability`: `available` or `unverified`. If a previously posted paper's public page becomes unavailable or its version cannot be reconciled, retain its documented last confirmed posting with a concise `availability_note`, use the "Check venue" link, and exclude it from current-version structured data. Do not label that version as verified current, infer withdrawal, substitute a working draft, or remove the availability note until a public readback resolves it.

## Literature discovery catalogue

`literature.json` is a separate discovery index, not the project's verified preprint list. Build it from the compressed bibliographic search snapshots with `python scripts/emc_literature_census.py` followed by `python scripts/emc_literature_enrich.py`. The first command intentionally regenerates the base index; the second reapplies the reviewed `literature-overrides.json` annotations. Network refresh is explicit for the census. Preserve snapshot dates and query limits. The Crossref title search inspects its first 1,000 relevance-ranked records, not its fuzzy total-results count.

`literature_page.py` generates a static fallback with every record. `literature.js` adds search, scope/access/type/year filters and pagination. Public metadata contains no article abstracts or full-text copies. Indexed free links are not proof of current reachability; unresolved access is not evidence of a paywall-only work. Study-level duplicates, incomplete conference coverage and incidental mentions remain openly labeled. Only `build.py`'s output allowlist is deployable. Full-text recovery writes to `.cache/`, not the public site. The research census report records outstanding screening and reading work.
