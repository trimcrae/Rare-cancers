# Blocker record — surface-targets, peer review item 44 (surfaceome overlap)

Recorded 2026-09-08 10:32 UTC by the parent, under the work-selection amendment in
`CROSS-PAPER-ADVANCE-2026-09-08.md`. Three required elements: the paper and item, the **measured**
evidence, and the **exact reopening condition**.

## 1 · Paper and item

`research/manuscripts/surface-targets/emc-surface-target-landscape.md`, `PUB-SURFACE-TARGETS`,
drafted and unpublished. **Peer review item 44 (Minor 19)** asks the paper to quantify its overlap
with the published machine-learning surfaceome. The 2026-08-10 review response **declined** it, on the
ground that the resource's membership table "is not committed anywhere in this repository".

## 2 · Evidence — measured now, not inherited

- **The bibliographic record is committed; the membership table is not.**
  `research/literature/remaining-reference-metadata-2026-08-09.json` holds only the citation for
  Bausch-Fluck et al., *"The in silico human surfaceome"*, PNAS 2018 — PMID 30373828, PMC6243280,
  DOI 10.1073/pnas.1808790115. It contains **no gene membership data**.
- **No membership table exists anywhere under `research/`.** A filename search for `*surfy*` and
  `*surfaceome*membership*` returns **nothing**; a content search for `SURFY` returns **nothing**.
- **The manuscript's current form is already honest.** Line 154 states that the resource exists and
  that it **was not used**, with the reason — the surfaceome here is built from UniProt annotation.
  The correction register (line 741) records that this wording was chosen deliberately, because
  citing the resource at the construction step would have implied it was the source.

So the paper does not misstate anything. What it cannot do is **quantify** a difference against data
it does not hold.

## 3 · Exact reopening condition

**Item 44 reopens when the Bausch-Fluck surfaceome membership table is committed to this repository
as data** — a gene-level list obtained through an authorised route — after which the overlap becomes
a local computation over committed inputs and needs no further permission.

⚠ **Stated precisely, because "blocked" is a claim that needs evidence:** what is established is that
the table **is not committed**. It is **not** established that it is unreachable. PMC6243280 exists,
so the article is open access, and whether that record's **supplementary material** is retrievable
through this campaign's admitted PubMed route **has not been tested**. Testing it would be a **new
source-retrieval task**, outside every current contract and requiring its own authorisation — so item
44 is blocked **for the contracts in force**, not proven unreachable in principle.

**The cheap first test, if this is ever authorised:** ask the admitted PubMed route for PMC6243280's
supplementary files, and record the exact result. That is a $0 reading; a negative result would be a
bounded reachability finding, not a global absence claim.

## Not admitted by this record

No network call, no denied-route retry, no paid access, and no change to the manuscript's current
wording — which stands as accurate. This record does not reopen F1, G1, H1, I1, J1 or K1, and does not
admit the DFSP-only sensitivity analysis.

## Consequence for work selection

Item 44 does **not** stall the paper. Surface-targets continues through its remaining **ready** work —
`L1` (`a050ed6a7259902e8`) is executing on peer review Minor 16/17, the figure's nondeterministic
jitter, which needs no network and was measured by K1. When surface-targets' ready work is exhausted,
the next eligible unfinished paper starts in the same cycle.
