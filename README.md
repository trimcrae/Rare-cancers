# Rare Cancer Info Hub → EMC treatment-advancement project

> **Primary focus (2026-06):** this repo's number-one priority is **publishing work that
> drives forward a treatment for extraskeletal myxoid chondrosarcoma (EMC)**. Its crux is a
> tracked portfolio of candidate treatment ideas — why each is encouraging or unlikely, and how to
> advance it **with no wet lab** (either a paper convincing enough that others test it, or in-silico
> evaluation we run ourselves).
>
> - **Start here:** [`research/manuscripts/emc-treatment-strategy.md`](./research/manuscripts/emc-treatment-strategy.md) — the prioritized portfolio (the crux).
> - **Live tracker board:** [`research/IDEAS.md`](./research/IDEAS.md) — every candidate, status, next step.
> - All other manuscripts/code exist to advance entries in that tracker.
>
> **The patient-facing info-hub site below is SHELVED** (deprioritized, not deleted) — see
> "Patient-facing info hub (shelved)" below. Medical-integrity rules in [AGENTS.md](./AGENTS.md)
> still apply to everything.

---

## Patient-facing info hub (shelved)

Hard-to-find information, gathered in one place — for cancers too rare to
research alone.

This project was started by a patient diagnosed with **extraskeletal myxoid
chondrosarcoma (EMC)** at age 29, who found almost nothing useful online. The
goal is a simple, fast page for each rare cancer that brings together the tools
a newly diagnosed person actually wishes they had.

## What each cancer page gives you

- 🔬 **Every study** we can find, plus live search links for new ones
- 👥 **Pooled patient data** from across published reports
- 📊 **Outcomes** presented like an outcomes study (survival, recurrence, spread)
- 🎛️ **"People like me" filter** — enter your age / grade / stage / size to see
  how similar patients did
- 💬 **Support groups** (Facebook, Reddit, real-life networks)
- 🏥 **Centres of excellence** worldwide + a **find-a-specialist-near-me** tool
- 🩺 **Treatment plans**, filterable by stage
- 💡 **New & promising treatments** under investigation
- 🧪 **Clinical trials** — find actively enrolling/upcoming trials and how to join
- 🔁 **Monitoring plans** for remission
- ❓ **Good questions** to ask your oncologist

> **Not medical advice.** This is patient-built educational information drawn
> from public literature. It cannot replace your own oncology/sarcoma team.
> See [MEDICAL_DISCLAIMER.md](./MEDICAL_DISCLAIMER.md).

## Live pages

- **EMC** — Extraskeletal Myxoid Chondrosarcoma — `cancers/emc/`

## Run it locally

It's a zero-build static site. Serve the folder over HTTP (the pages fetch JSON,
so opening files directly won't work):

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Add or improve a cancer page

A whole cancer page is driven by **one JSON file** — no build step, no framework.

```bash
node scripts/new-cancer.mjs <slug> "Full Name" "ABBR" "Category"
# then edit data/cancers/<slug>.json
node scripts/validate.mjs
```

See **[AGENTS.md](./AGENTS.md)** for the full playbook (and the medical-integrity
rules) and **[CONTRIBUTING.md](./CONTRIBUTING.md)** for how to contribute data.

## Hosting

Deployed via **GitHub Pages** (`.github/workflows/pages.yml`). Every push to
`main` validates the data and publishes the site.

One-time setup by the repo owner: **Settings → Pages → Build and deployment →
Source: _GitHub Actions_**. After that it's automatic.

The site itself is host-agnostic (all relative URLs), so it can also be served
from any other static host or a subpath without changes.

## Licence

Code is under the repository's [LICENSE](./LICENSE) (Apache-2.0). Linked medical
content belongs to its original publishers; we link to sources rather than
reproduce them.
