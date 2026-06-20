# Rare Cancer Info Hub

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

The site is host-agnostic (all relative URLs). Deploy configs are included for:

- **GitLab Pages** — `.gitlab-ci.yml` (publishes from the default branch)
- **GitHub Pages** — `.github/workflows/pages.yml` (enable Settings → Pages →
  Source: *GitHub Actions*)

## Licence

Code is under the repository's [LICENSE](./LICENSE) (Apache-2.0). Linked medical
content belongs to its original publishers; we link to sources rather than
reproduce them.
