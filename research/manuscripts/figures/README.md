# Manuscript figures

**Figures are now inline in the manuscripts as Markdown tables and Mermaid diagrams**, not
hand-drawn SVG — see the "Making figures" rules in the repo `AGENTS.md`. Hand-emitted SVG was
removed because it overflowed its boxes and cannot be rasterised/verified in this environment.

- Repurposing paper (`repurposing-hypotheses.md`): the evidence × novelty **map** and the
  candidate detail are Markdown tables; the three-method/firewall diagram is a **Mermaid**
  flowchart; the TxGNN stress-test is a table.
- Treatment roadmap (`emc-treatment-roadmap.md`, Fig 2): the prioritized portfolio is a two-axis
  Markdown table **and** a labelled categorical grid, **`portfolio-quadrant.png`** — readiness ×
  driver-directedness (both axes categorical: 4 readiness bands × 3 defined directedness levels),
  rendered with **matplotlib** via `portfolio_quadrant.py` and viewed before commit (the AGENTS.md
  path for a real plot). Regenerate with `python3 portfolio_quadrant.py`; keep the cell membership in
  the script in sync with the table. *(The old hand-emitted single-tier `portfolio.svg` +
  `portfolio_figure.py` were removed — superseded by this and banned by the "Making figures" rules.)*
- Final journal figures should be produced by the authors with a proper plotting tool.
