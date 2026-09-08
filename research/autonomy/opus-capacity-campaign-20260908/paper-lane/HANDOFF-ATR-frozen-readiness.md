# FROZEN HANDOFF — ATR collaborator package, publication readiness

Prepared 2026-09-08 by the campaign parent, in the same session, **entirely from evidence already
retained**. No new census, no source or science re-run, no new child, no new approval. This advances
final scientific review and publication readiness; it is not another quantity audit.

## 1 · Exact content identity, as frozen

| item | bytes | sha256 |
|---|---|---|
| `research/manuscripts/dependency/emc-atr-collaborator-package.md` | 61,812 | `75b2189e146647b4d865eee7ffe782723a03fb6b50c502e741dbba1c0f07be5a` |
| `...-cover-letter.md` | 5,310 | `c17b85e179b26e6f54f37763b784a0d84b54d97a5604a875a6b6a609270b8cde` |
| `...-integration-qa-2026-09-08.md` | 3,908 | `b54de5f00912a7de5d8d7dc70d5567affb4cfdee869750d411d1eab53a8c7263` |
| `research/manuscripts/figures/emc-fusion-frame-fig1.png` | 360,656 | `fa94675f436692344f5514ac1d08f7d448b5ebdbae4ac16fe3a8572597eb07a7` |

Title: *Reading-frame constraints and retained RG content in NR4A3 fusion models of extraskeletal
myxoid chondrosarcoma*. Author: Tristan D. McRae, unaffiliated, ORCID 0000-0002-1823-1451.
Declared-counter metrics: **main 6,200 w · abstract 243 w · 1 figure · 5 tables · 6 display items ·
10 references**, `within believed limits`, `0 limit(s) exceeded`. Last commit touching the
manuscript: `035e9f69`.

## 2 · Review provenance, and the actual model and effort

Every review in this package's chain ran as `claude-opus-5`, verified from each child's original
JSONL rather than from any contract text, at `CLAUDE_EFFORT=medium` on the first-party subscription.
No paid API, no GPU, no overage.

| lane | what it produced | observed tool pairs |
|---|---|---|
| R1 | the reconciliation candidate | retained in `X1-executed-artifacts/INPUTS/R1/` |
| U1 | figure map and R1 review | retained in `INPUTS/U1/` |
| W1 / W2 / W3 | Supplementary Table S3, Panel A key sources, Okamoto 2001 metadata | retained in `INPUTS/W1|W2|W3/` |
| X1 | the accepted reconstruction and title | `X1-executed-artifacts/` |
| Y1 | TCF12 frequency provenance | 26 pairs |
| AB1 | the shortened abstract | 30 pairs |

The coordinator accepted X1's reconstruction and title, then authorised six bounded corrections plus
one sentence replacement from Y1's disposition, then one final anchor-sentence edit. All are applied.
**Integration is not publication acceptance.**

## 3 · Paper-specific dependencies that remain

1. **The 250-word abstract limit is search-derived, not publisher-verified.**
   `submission_metrics.py` records its provenance as "search-derived; onlinelibrary.wiley.com serves
   a bot challenge to CI and to a real headless browser alike". 243 is a count under this counter's
   tokenisation; a journal's own counter may differ on tokens like `EWSR1::ATF1`, `10-aa` and
   `0.000`. **Not a defect. A dependency on an unverified constraint.**
2. **Figure 1 legibility at print size is not verified.** The integration QA note records that the
   generator draws NR4A3 RG ticks at residues 371 and 508 and an independent reading of the rendered
   image reported one of them; whether the 371 tick is occluded by the domain-block edge at 373 or is
   not resolved at print size **was not settled and is not asserted**.
3. **The Panel A box spans are literals, not a binding.** They currently match `rgg_boxes_operational`
   exactly, which was checked. The generator's `stamp()` hashes each source file whole, so a data
   change would change the stamp — but no code binds the literals to the field, so a later edit plus
   redraw could produce a fresh correct stamp over a silent mismatch. Anyone editing that field must
   re-check the literals by hand.
4. **The exon-to-nucleotide correspondence rests on one annotation source.** Section 2.6 says so, and
   says no second-source verification was attempted or is claimed.
5. **Y1's denominator distinction.** Total-series and partner-assigned denominators are distinct: the
   pooled Agaram denominator of 24 excludes 2 unassigned cases against a series total of 26; the Huang
   pool of 57 differs from that series' 58. Section 3.5 deliberately reports one of 26 cases in one
   series and no population prevalence.

## 4 · Mandatory publication checks — UNRUN versus FAILED

This distinction matters and is easy to blur, so it is drawn explicitly.

**Run, and passing on this manuscript and its companions:**

| check | result |
|---|---|
| `lint_style.py` | 0 ERROR on the manuscript, the cover letter and the QA note |
| `lint_consistency.py` | 0 ERROR across 29 target files |
| `lint_claims.py` | 0 ERROR (1 pre-existing WARN on an author-block line) |
| `lint_submission_residue.py --report` | exit 0, 0 NEW, 0 stale rows |
| `lint_asymmetry.py --report` | 0 new symmetric restatements |
| `submission_metrics.py` | 0 limits exceeded |

**Run, and FAILING — repo-wide, not this paper:**

- `lint_citations.py` exits **1**. The cause is `lint_citation_types`: type claims disagreeing with
  PubMed and NOT-SWEPT identifiers, in campaign report files under
  `research/autonomy/opus-capacity-campaign-20260908/reports/`. Pre-existing throughout this campaign,
  not introduced by this paper, and not repaired here. **Not all gates are green.**
- `systems_check.py` exits **1** at **907 errors**. ⚠ **907 systems errors on the cloud tree are not
  907 paper defects**, and the assurance here must be no wider than what was actually measured. What
  was measured is one comparison, on one occasion: the ATR integration's **tracked** changes were
  stashed and `systems_check` re-run, giving 907 both ways. That comparison does not cover every
  change this campaign made, and the then-untracked QA note was present in **both** runs, so it bounds
  the tracked ATR changes only. **Error identity was never compared**, so equal totals do not
  establish that the same 907 errors are present in both runs, and no claim is made here about which
  files the 907 name. Separately and narrowly: the two D11 errors that did name a file this
  integration touched were introduced on the new QA note and fixed.

**UNRUN, and explicitly so:**

- **`scripts/preflight.sh` has not been run**, in either normal or `PREFLIGHT_FULL=1` form. The
  campaign's standing instruction reserves the full gate for the publication candidate, and it has not
  been exercised on this one. This is UNRUN, not passed and not failed.
- **No ultra or extended review tier has been run** on this manuscript.
- **No render or typeset QA has been run.** No PDF or DOCX was built, no figure was checked at print
  size, and no proof was read. Publication review and render QA remain a separate step.
- The three reproduction commands in section 2.5 — `emc_fet_construct_designs.py --check`,
  `emc_fet_frame_and_composition.py --check`, `emc_fusion_frame_figure.py --check` — are quoted from
  their modules' declared signatures and **none was executed** for this revision, which recomputes no
  scientific result. The manuscript says so.

## 5 · Applicable submission path, by the existing enforcers

No gate is weakened and no historical record is rewritten to establish this.

- `submission_metrics.py` records the venue as **Genes, Chromosomes and Cancer (Wiley)**, article type
  `GCC-Research-Article`, and the manuscript is `within believed limits` on every recorded dimension.
- `research/autonomy/publication-authority.json` owns the grants; `publish_bar.py` and
  `scripts/zenodo_deposit.py` enforce their respective paths. **aiXiv has a standing scoped grant and
  PUB-ASO is excluded from it; that grant does not cover this paper's journal route.** Journal
  submission is a new external act and requires the applicable user authorization, which has **not**
  been sought or given here.
- The cover letter is prepared and addressed to that venue, with the ORCID supplied and the two
  second-person findings handled as ordinary correspondence formatting.

**What is therefore ready:** a manuscript inside its recorded venue limits, with its companions,
passing the gates listed as run-and-passing above. That is not a statement that the repo-wide
failures are irrelevant or somehow passed: `lint_citations` and `systems_check` both exit 1 on this
tree, and a submission path that runs them will meet those failures whatever this manuscript's own
state.

**Next required steps, and what blocks each:**

1. **An ultra-tier review.** The reviews in this package's chain ran at `CLAUDE_EFFORT=medium`.
   **Medium reviews do not satisfy a required ultra review**, and no ultra review has been run on this
   manuscript. UNRUN.
2. **`scripts/preflight.sh`**, in the form the publication candidate requires. UNRUN.
3. **Render and typeset QA**, including the figure at print size. UNRUN.
4. **The repo-wide gate failures** above, which are pre-existing and not this paper's, but sit on the
   path.

**On submission permission:** it follows the existing grants and enforcers —
`research/autonomy/publication-authority.json`, `publish_bar.py`, `scripts/zenodo_deposit.py` — and
the user's standing authority. This handoff does **not** invent a new approval barrier; it records
that the aiXiv standing grant does not cover a journal route, and leaves the applicable authorization
to those enforcers and to the user.

## 6 · Open items carried, not resolved

- The abstract word-count constraint is unverified at the publisher (item 3.1).
- Figure legibility at print size is unverified (item 3.2).
- `lint_citations` is red repo-wide (section 4).
- The literal-versus-data binding hazard in the figure generator (item 3.3) is a maintenance hazard,
  not a defect in the current figure.

Nothing above was re-derived for this handoff. Every value is read from a retained artifact, a
retained collection record, or the committed file it describes.
