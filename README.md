# EMC treatment-advancement project

> **Primary focus:** this repo's number-one priority is **computational work that drives forward a treatment for
> extraskeletal myxoid chondrosarcoma (EMC)**, an ultra-rare sarcoma driven by the EWSR1::NR4A3 fusion — with
> **no wet lab** (either a paper convincing enough that others test it, or in-silico evaluation we run ourselves).
>
> ## Start here
>
> - **🗺️ [`research/manuscripts/nr4a3-program-map.md`](./research/manuscripts/nr4a3-program-map.md) — THE
>   ROADMAP, and where to start.** One document, read top to bottom: what is done, what is true, what is
>   blocked and what is next. It carries the requirement register (`R*`), the instrument register (`V*`), the
>   dependency graph, the closed-route register and the single ordered list of next steps. The #1 program is
>   the **NR4A3-selective degrader paper**. Read this before proposing a step — a step whose instrument is
>   unvalidated buys nothing.
> - **📋 [`STRATEGY.md`](./STRATEGY.md) — the roadmap's APPENDIX SET, and the machine-parsed layer.** The
>   ordered plan, the spend ladder and its derivation, the validation architecture, the language-discipline
>   rules, the gate scoreboard, the open decisions and the history (Appendices A and B). It stays a separate
>   file because seven CI checks parse it by exact heading and format. **For a cost, a gate, a plan marker or a
>   decision number it wins; for what blocks what and what to do next, the roadmap wins.**
> - **[`research/manuscripts/emc-treatment-strategy.md`](./research/manuscripts/emc-treatment-strategy.md)** —
>   the broader route portfolio (all treatment routes ranked; context beneath `STRATEGY.md`).
> - **[`research/IDEAS.md`](./research/IDEAS.md)** — live tracker board: every candidate route, status, next step.
>
> Everything clinical must be cited and never fabricated — medical-integrity rules in [AGENTS.md](./AGENTS.md)
> apply to all of it.

## Repo layout

- **`research/manuscripts/nr4a3-program-map.md`** — the roadmap: requirements, instruments, what blocks what,
  and the one ordered list of what is next (read first).
- **`STRATEGY.md`** — the roadmap's appendix set: the ordered plan, the spend ladder, the validation
  architecture, the open decisions and the history. Machine-parsed; do not restructure it.
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
