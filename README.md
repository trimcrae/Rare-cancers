# EMC treatment-advancement project

> **Primary focus:** this repo's number-one priority is **computational work that drives forward a treatment for
> extraskeletal myxoid chondrosarcoma (EMC)**, an ultra-rare sarcoma driven by the EWSR1::NR4A3 fusion — with
> **no wet lab** (either a paper convincing enough that others test it, or in-silico evaluation we run ourselves).
>
> ## Start here
>
> - **🗺️ [`research/manuscripts/nr4a3-program-map.md`](./research/manuscripts/nr4a3-program-map.md) — THE
>   ROADMAP. It is the whole plan, and it is the only thing you have to read.** One document, top to bottom:
>   what is done, what is true, what is blocked and what is next. It carries the requirement register (`R*`),
>   the instrument register (`V*`), the dependency graph, the gate scoreboard, the closed-route register,
>   **THE ORDERED PLAN**, the spend ladder and its derivation, the validation architecture, the
>   language-discipline rules, the open decisions and the single ordered list of next steps. The #1 program is
>   the **NR4A3-selective degrader paper**. Read this before proposing a step — a step whose instrument is
>   unvalidated buys nothing.
> - **📋 [`STRATEGY.md`](./STRATEGY.md) — history only: two appendices.** Appendix A (superseded numbers and
>   retracted claims) and Appendix B (retired plan framings). ⛔ **Nothing live is left in it** — every section
>   that said what to do, what a thing costs or what a gate decided was moved into the roadmap on 2026-08-02,
>   under the same headings and slugs. The two appendices stay because their rows are read *as data*
>   (`realised_spend.py` cites "Appendix A row 35") and because `lint_consistency` uses Appendix A's heading as
>   a structural clear. **The roadmap wins on everything; this file wins only on what a superseded value used
>   to be.**
> - **[`research/manuscripts/emc-treatment-strategy.md`](./research/manuscripts/emc-treatment-strategy.md)** —
>   the broader route portfolio (all treatment routes ranked; context beneath the roadmap).
> - **[`research/IDEAS.md`](./research/IDEAS.md)** — live tracker board: every candidate route, status, next step.
>
> Everything clinical must be cited and never fabricated — medical-integrity rules in [AGENTS.md](./AGENTS.md)
> apply to all of it.

## Repo layout

- **`research/manuscripts/nr4a3-program-map.md`** — the roadmap: requirements, instruments, what blocks what,
  the ordered plan, the spend ladder and the one ordered list of what is next (read first). Machine-parsed by
  `work_ledger`, `lint_consistency` and `lint_claims` on exact heading strings — do not rename a heading.
- **`STRATEGY.md`** — history only: Appendix A (superseded numbers, rows cited as data) and Appendix B
  (retired plan framings). Do not restructure it; do not renumber its rows.
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
