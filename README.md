# EMC treatment-advancement project

> **Primary focus:** this repo's number-one priority is **computational work that drives forward a treatment for
> extraskeletal myxoid chondrosarcoma (EMC)**, an ultra-rare sarcoma driven by the EWSR1::NR4A3 fusion — with
> **no wet lab** (either a paper convincing enough that others test it, or in-silico evaluation we run ourselves).
>
> ## Start here
>
> - **📋 [`STRATEGY.md`](./STRATEGY.md) — the overarching research strategy and the single source of truth for the
>   plan.** What we run, in what order, why, each step priced, with GO/NO-GO gates. The #1 program is the
>   **NR4A3-selective degrader paper**; its full spend-gated execution ladder is there.
> - **[`research/manuscripts/emc-treatment-strategy.md`](./research/manuscripts/emc-treatment-strategy.md)** —
>   the broader route portfolio (all treatment routes ranked; context beneath `STRATEGY.md`).
> - **[`research/IDEAS.md`](./research/IDEAS.md)** — live tracker board: every candidate route, status, next step.
>
> Everything clinical must be cited and never fabricated — medical-integrity rules in [AGENTS.md](./AGENTS.md)
> apply to all of it.

## Repo layout

- **`STRATEGY.md`** — the plan (read first).
- **`research/`** — the treatment-discovery work: manuscripts, modalities (structure/FEP/ternary pipelines),
  the EMC atlas, and compute infra. `research/manuscripts/` holds the papers; `research/modalities/` holds the
  in-silico pipelines and how-to-run handoffs.
- **`AGENTS.md`** / **`CLAUDE.md`** — the maintenance guide and agent instructions.
- **`METHODOLOGY.md`** — how registry data is cited and pooled (read before touching `registry`).
- **`data/`, `cancers/`, `scripts/`** — the shelved patient-facing static site (see below).

## Patient-facing info hub (shelved)

The repo also contains a zero-build static site of one-page-per-rare-cancer information hubs (first page: EMC).
It is **deprioritized/shelved** — kept working if touched, but not under active development. If you do touch it,
`node scripts/validate.mjs` must pass, and it deploys via GitHub Pages (`.github/workflows/pages.yml`) on push to
`main`. See [AGENTS.md](./AGENTS.md) for the site playbook and the medical-integrity rules.

> **Not medical advice.** Any patient-facing content is educational information drawn from public literature and
> cannot replace an oncology/sarcoma team. See [MEDICAL_DISCLAIMER.md](./MEDICAL_DISCLAIMER.md).

## Licence

Code is under the repository's [LICENSE](./LICENSE) (Apache-2.0). Linked medical content belongs to its original
publishers; we link to sources rather than reproduce them.
