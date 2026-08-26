---
id: DOC-KM-FIGURE-ATTRIBUTION
title: Published figures reproduced here, and under what licence
level: L5
kind: register
status: live
canonical_for: [km_figure_provenance]
purpose: Name the source, licence and attribution of every third-party figure image committed under this directory, and state why any is committed at all.
scope: Image files in research/modalities/figures/ only.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-25
last_verified: 2026-08-25
---

# Published figures reproduced here

⛔ **WHY A THIRD-PARTY IMAGE IS IN THIS REPOSITORY AT ALL.** A reconstructed patient-level dataset
is a **clinical datum derived from pixels**. If the pixels are not in the repository, the derivation
cannot be checked, re-run, or refuted by anyone reading it — the coordinates become numbers on
trust, which is the exact failure `emc_ipd_survival.py` refuses to allow when it keeps its own
`CURVES` table empty. Committing the figure is what makes the reading falsifiable.

⛔ **ONLY UNDER A LICENCE THAT PERMITS IT, AND ONLY WITH THE ATTRIBUTION THE LICENCE REQUIRES.** A
figure whose licence does not permit redistribution is NOT committed; its reading is then
conditional on a cache the reader may not have, and that limitation is recorded rather than worked
around.

⛔⛔ **AND THE BAR IS NOT "REDISTRIBUTABLE", IT IS "REDISTRIBUTABLE ON THIS REPOSITORY'S OWN
TERMS".** This repository is **Apache-2.0**, which promises everyone who reads it that they may
reuse what is here, including commercially. A **non-commercial** asset silently breaks that promise
for anyone who forks the repo — the licence in `LICENSE` would say one thing and a file inside would
say another. So the rule is narrower than "the licence allows sharing":

> **A figure may be committed only under a licence that permits commercial reuse with attribution
> (CC BY, CC0, public domain). CC BY-NC and anything more restrictive stays out, and its reading is
> recorded as a RECIPE — the URL, page, dpi and crop that reproduce the exact raster — with the
> reading flagged as not re-runnable from a bare checkout.**

⚠ **The number derived from a figure is not the figure.** Reading a published plot and reporting
what it says is ordinary scholarship and no licence restricts it; copying the plot into a
permissively-licensed repository is a redistribution and does. That is why a reading can be
committed when its image cannot.

**Recorded as a recipe rather than an image, for that reason:**

| reading | source | licence | where the recipe lives |
|---|---|---|---|
| `martinbroto2020_immunosarc_phase2_pfs` | Martín-Broto J, et al. *J Immunother Cancer* 2020;**8**:e001561, Figure 3 (swimmer plot) | **CC BY-NC 4.0 — non-commercial** | `km_digitize.SWIMMER_RECIPES` → `regenerate` |

| file | source | DOI | licence | what it shows |
|---|---|---|---|---|
| `stacchiotti2013-csr-3-16-fig2.png` | Stacchiotti S, et al. *Clinical Sarcoma Research* 2013;**3**:16, Figure 2 | [10.1186/2045-3329-3-16](https://doi.org/10.1186/2045-3329-3-16) | CC BY 2.0 — © 2013 Stacchiotti et al.; licensee BioMed Central Ltd. | Overall progression-free survival of NR4A3-confirmed extraskeletal myxoid chondrosarcoma patients treated with anthracycline-based chemotherapy, with its numbers-at-risk row |

**How this crop was produced, so it can be re-produced:** the article PDF was retrieved by
`scripts/emc_km_figure_fetch.py` via `europepmc.org/articles/PMC3879193?pdf=render`, page 5 was
rasterised with `pdftoppm -r 600 -png`, and the figure region was cropped. Nothing in the pixels was
edited, enhanced or redrawn — a retouched figure would be a fabricated source.
