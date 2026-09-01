---
id: DOC-SPRINT-S27-RETRACTIONS
title: "S27-RETRACTIONS — the retraction check covered 1% of the citations; it now covers all of them"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S27-RETRACTIONS — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S27-RETRACTIONS — the retraction check covered 1% of the citations; it now covers all of them

**Item(s):** driver-raised (retraction advisory on `nr4a3-druggability-reconciliation.md:69`)
**Owned paths:** `research/manuscripts/lint_citations.py` (retraction/type half),
`research/manuscripts/lint_citation_types.py`, `research/manuscripts/citation-retraction-sweep.json`
(new), `research/manuscripts/citation-retraction-notices.json` (new),
`research/manuscripts/tests/test_the_retraction_sweep_covers_every_identifier.py` (new), this file
**Started/Finished (UTC):** 2026-09-01T15:44 / 2026-09-01T16:35

> **Attribution.** According to PubMed. Every publication type, title, journal, year and DOI below
> was fetched from PubMed through the PubMed MCP connector on 2026-09-01; PubMed's terms require its
> metadata to travel with a resolvable DOI link, so each retracted paper is given with one.

## Verdict

**FIXED (tooling) + NO-CHANGE-NEEDED (prose).** The sweep found **two** retracted papers cited in
this repository, not one — and **both citing passages are already correct as written**, so no
manuscript edit is required. What was broken was the *check*: retraction detection rode on the
type-claim scanner and therefore looked at **23 of the repository's ~1,080** prose identifiers. It now looks at all of
them, still as an advisory, and the argument for *not* making it an error tonight is in §5.

## What I measured

### 1 · The known case is real, and the retraction notice exists

PubMed `get_article_metadata(["40646688"])`, 2026-09-01:

| field | value |
|---|---|
| PMID | 40646688 · PMC12263127 |
| title | *Orphan nuclear receptor transcription factors as drug targets.* |
| authors | Safe S, Oany AR, Tsui WN, Lee M, Srivastava V, Upadhyay S, et al. |
| journal | *Transcription* 16(2-3):224–260 (2025) |
| DOI | [10.1080/21541264.2025.2521766](https://doi.org/10.1080/21541264.2025.2521766) |
| `article_types` | `Journal Article`, `Review`, `Research Support, N.I.H., Extramural`, **`Retracted Publication`** |

★ **The retraction notice is a separate record and nothing in this repository names it.** Found by
title search, then `get_article_metadata(["42622620"])`:

> PMID **42622620** — *"Statement of Retraction: Orphan nuclear receptor transcription factors as
> drug targets."* *Transcription*, published **2026-08-20**, DOI
> [10.1080/21541264.2026.2714669](https://doi.org/10.1080/21541264.2026.2714669),
> `article_types = ['Journal Article', 'Retraction Notice']`.

⛔ **The GROUNDS for the retraction are UNKNOWN from here, and that is a reading I could not take
rather than a reading of absence.** PubMed carries `[Abstract not available]` for the notice; the
notice text sits behind `doi.org` and `tandfonline.com`, and both are refused by this sandbox's
egress proxy (`curl: (56) CONNECT tunnel failed, response 403`, measured today, same as
`eutils.ncbi.nlm.nih.gov`). A WebSearch for the statement returned the *article* and no notice text.
**Do not write a reason for this retraction until somebody has fetched the notice** — §7 of the
driver list below is how.

### 2 · What the sentence at `nr4a3-druggability-reconciliation.md:69` rests on

Read verbatim. The sentence is inside a `**[CORRECTED 2026-07-12, primary-source verified: ...]**`
block. It cites the Safe 2025 review **only as the secondary source whose loose paraphrase it is
correcting**, it already prints "PMC12263127 — **RETRACTED**; PubMed records the type 'Retracted
Publication' for this article, read 2026-08-27", and the substance — Compounds 1 and 19, IC₅₀ ≈ 8–47
µM, MYC de-repression, and the absence of any NR4A1/NR4A2 counter-screen — is taken from **Zaienne
2022 (PMC9542104, *ChemMedChem*, [10.1002/cmdc.202200259](https://doi.org/10.1002/cmdc.202200259)),
the primary**, quoted verbatim from its full text.

★ **So the retraction strengthens the correction rather than undermining it**, exactly as the prose
already says. **Nothing rests on the retracted paper. No prose change is warranted here.** This is
the situation the brief asked me to separate from its opposite, and it is the benign one.

### 3 · ⭐ THE SWEEP — every prose identifier, not 23

Method (all through the PubMed MCP connector, because direct NCBI/EuropePMC/Crossref/OpenAlex are
all 403 at the egress proxy — four hosts tested, all refused):

1. `lint_citations.survey()` for every prose identifier in tracked `.md`.
2. `convert_article_ids` to map PMCIDs (168/168 resolved) and DOIs (230 resolved) onto PMIDs.
   ⚠ **The NCBI ID Converter only covers PMC-backed records**, so a DOI it cannot resolve is *not*
   thereby absent from PubMed — the residue needed a second pass.
3. `search_articles` with `(<ids>) AND ("Retracted Publication"[Publication Type] OR "Expression of
   Concern"[Publication Type])` over the union of 447 PMIDs plus the DOI residue by `[doi]`.
   ⚠ **The connector refuses more than 20 boolean operators** (`Query too complex: too many boolean
   operators (max: 20)`), so the ceiling is 17 identifiers per filtered query — 35 queries.
4. `search_articles` without the filter, to establish which identifiers PubMed resolves at all.

| | count |
|---|---|
| prose identifiers | **1,086** |
| checked against PubMed | **848** |
| **retracted** | **6 rows = 2 distinct papers** (each cited by PMID, PMCID and DOI) |
| **could NOT be checked — UNKNOWN, not clean** | **238** |
| not swept | **0** |

⛔ **Read the last two rows together or the first one lies.** 848 + 238 = 1,086: **22% of the
identifiers in this repository's prose have no PubMed retraction status and cannot be given one from
PubMed at all.** The linter prints that count on its own summary line, beside the hits, for exactly
the reason the brief gives — a sweep that quietly counts what it could not read as fine is the
defect, not the finding. The counts move as other seats edit prose; they are derived by the
generator and printed live by the gate, never typed twice.

⛔ **The 238 broken out, because "unchecked" is the number this repository keeps losing:** 82
ClinicalTrials.gov NCT ids, 69 arXiv ids, 59 GEO accessions — none of which are PubMed records at
all — plus **27 DOIs PubMed's own query translator silently DROPPED from the query**, meaning they
are not in its Publisher-ID index: 7 Zenodo deposits (mostly ours), 2 bioRxiv preprints, 1 ChemRxiv,
1 Qeios, 1 PDB entry, 1 Harvard Dataverse dataset, 3 meeting abstracts (ASCO ×2, AACR ×1), 2
malformed DOIs written in prose with a trailing `.full.pdf` and `v1`, and 9 journal DOIs outside
PubMed's scope (*J Chem Phys*, *J Phys Chem*, *Comput Phys Commun*, *JOSA A*, *J Am Stat Assoc*
1927, …). **Plus 1 PMID that does not resolve: `99999999`, the known-negative control
`lint_citations.py` documents in its own header.** Every one of those is `unknown` in the artifact
with its reason, and the linter prints them as "outside PubMed's reach — UNKNOWN, not clean".

### 4 · ⭐ THE SECOND RETRACTED PAPER, WHICH THE OLD CHECK COULD NOT SEE

`get_article_metadata(["36062197"])`:

> PMID **36062197** · PMC9428684 — *"Network Pharmacology, Molecular Docking, and Experimental
> Validation to Unveil the Molecular Targets and Mechanisms of Compound Fuling Granule to Treat
> Ovarian Cancer."* *Oxid Med Cell Longev* 2022, DOI
> [10.1155/2022/2896049](https://doi.org/10.1155/2022/2896049),
> `article_types = ['Journal Article', 'Retracted Publication']`.

It is cited in `research/manuscripts/no-wet-lab-publication-archetypes.md` and
`research/literature/no-wet-lab-archetypes-2026-08-12.json` **because it is retracted** — it is the
worked example of the network-pharmacology paper-mill failure mode that archetype is designed
against. **Correct as written; removing the citation would destroy the passage.**

★ **And the wide pass found a third location for the FIRST paper: the retracted Safe 2025 review is
also cited in `research/manuscripts/degrader/nr4a3-degrader-paper.md` — a submission manuscript**
(reference 6, and the sentence at :112). That passage, too, already labels it RETRACTED and already
says the claim rests on Zaienne 2022. **But the old advisory never mentioned it**, because that file
does not put the identifier in an attributive slot after a type word. A retracted citation was
sitting in a paper we intend to submit, and the guard was structurally incapable of naming it.

## What I changed

| path | change |
|---|---|
| `research/manuscripts/citation-retraction-sweep.json` | **NEW.** 846 checked rows + 238 `unknown` rows with reasons, both retracted papers in full with their notices, and an `acknowledged` list. Counts are DERIVED by a generator, never typed. |
| `research/manuscripts/lint_citation_types.py` | **NEW `retraction_sweep()`** — reads that artifact and reports retraction status for **every** prose identifier, plus a coverage line naming the unchecked count. Wired into `check()`. Missing artifact ⇒ rc 2, never a pass. Exit code otherwise **unchanged: still ADVISORY** (see §5). |
| `research/manuscripts/lint_citations.py` | **Two lines**, and they are defensive, not a change to the anchoring logic: `SWEEP_ARTIFACT_REL` added to `survey()`'s anchor-scan exclusion beside the ledger and the type cache. |
| `research/manuscripts/citation-retraction-notices.json` | **NEW.** The two retraction NOTICES as fetched records, so a document may cite a notice without the citation looking typed-from-memory. Deliberately NOT excluded from the anchor scan — see below. |
| `research/manuscripts/tests/test_the_retraction_sweep_covers_every_identifier.py` | **NEW**, 9 tests, all mutation-driven, all on tmp_path copies. `9 passed`; the whole pair with `test_citation_type_guard.py` is `40 passed` + 1 pre-existing failure that is not mine (below). |

⛔⛔ **THE `lint_citations.py` EDIT IS NOT COSMETIC AND I MEASURED WHAT HAPPENS WITHOUT IT.** The
sweep artifact is a tracked `.json` whose `records` map is keyed by every prose identifier in the
repository — so left inside the anchor scan it ANCHORS ALL OF THEM. Measured both ways today:

```
without the artifact   PMID 30  PMCID 17  DOI 38  NCT 7  GEO 3  arXiv 11   (106 unanchored)
with it, unexcluded    PMID  0  PMCID  0  DOI  0  NCT 0  GEO 0  arXiv  0   (0 unanchored)
```

That is the **2026-08-07 self-anchoring incident** — the one `survey()`'s own comment block records
for the ledger and again for the type cache — reproduced on a wider blast radius, and it would have
handed the next reader a perfect green bought by adding a file. Pinned by
`test_the_sweep_artifact_does_not_anchor_the_provenance_ledger`.

## ⭐ 5 · ADVISORY or ERROR? — the argument, and it says NOT TONIGHT

**Recommendation: keep it ADVISORY now; make it an ERROR in step 3 of the sequence below.** The
reasoning, not the assertion:

**(a) What breaks if it fails the gate, measured rather than guessed.** Flipping it to an
unconditional error today reds the trunk on **four documents**:
`research/manuscripts/no-wet-lab-publication-archetypes.md`,
`research/literature/no-wet-lab-archetypes-2026-08-12.json`,
`research/modalities/nr4a3-druggability-reconciliation.md` and
`research/manuscripts/degrader/nr4a3-degrader-paper.md`. **Every one of them is right as written.**
The first two cite a retracted paper *because* it is retracted; the second two cite one as the
secondary source a correction overrides, and say so in the prose.

**(b) So the naive bar punishes exactly the behaviour it wants.** A gate that goes red on honest work
gets switched off — that is CLAUDE.md §7's warning and it is the governing risk here, the same one
`lint_citation_types`' own header cites for its false-positive budget. A repository whose defence
against paper-mill work is a documented worked example of a retraction cannot have a rule that says
"never name a retracted paper".

**(c) But ADVISORY-and-uncounted is not the honest alternative either.** The advisory that prompted
this seat was true, and its neighbouring summary line — "23 type claim(s) checked against 13 cached
record(s)" — was a step that reported while measuring 2% of the corpus. That is fixed above, at zero
risk to the exit code.

**(d) The mechanism that makes the error version reachable is the repository's own idiom.** This is
`lint_citations`' *"a ledger, not a wall"* again: enumerate the existing cases, require each to carry
a written reason, then fail on anything NOT enumerated. The `acknowledged` list in the sweep artifact
is that ledger, and it is already populated for all four documents with a per-file `why`.

**Proposed sequence for the driver:**

1. **Tonight (done, in this seat).** Wide pass + artifact + tests. Exit code untouched, trunk green.
2. **Next.** Let the acknowledgements sit through one hardening round so a blind seat can dispute a
   `why` it disagrees with. Sequence the two small prose additions in §6 — they are the substantive
   improvements the sweep found.
3. **Then.** Flip **unacknowledged** retracted citations to an ERROR (acknowledged ones stay
   advisory). By construction that cannot red the trunk on today's tree, and it does catch the case
   the bar exists for: a NEW citation to a retracted paper, added by a session that did not notice.
   ⛔ **Do not flip step 3 in the same cycle that writes an acknowledgement** — `research-loop`'s
   anti-gaming invariant: a bar may not be changed by the cycle it would have blocked.

## What I could not do, and what it is actually waiting on

- **The GROUNDS of the Safe 2025 retraction — genuinely blocked on network, not on effort.**
  `doi.org` and `tandfonline.com` are 403 at the egress proxy; PubMed holds no abstract for the
  notice. **It is a $0 CI fetch**: `.github/workflows/verify-refs.yml` already curls Crossref and
  Europe PMC from a runner with full internet. Adding
  `10.1080/21541264.2026.2714669` to its `FIXED_DOIS` list and dispatching it would return the
  notice's title and abstract. **That is a workflow edit, which is not my path** — driver item below.
- **Retraction status for the 238 unreachable identifiers.** Not a PubMed question. NCT records have
  a withdrawal/termination status in ClinicalTrials.gov, GEO has withdrawn accessions, arXiv has
  withdrawn versions, Zenodo has tombstones — four different sources, none of them PubMed. **Left
  honestly UNKNOWN rather than assumed clean.** Sizing that is its own seat.
- **`lint_citations`' DOI pattern truncates at `(`** — `10.1016/S1470-2045(19` is what the scanner
  stores for `10.1016/S1470-2045(19)30319-5`. Seven identifiers, all Elsevier legacy DOIs. I
  recovered the full forms **by grepping the prose** and checked them (none retracted), but the
  pattern lives in `PATTERNS`, which is the anchoring half — **not my path**. Driver item.
- **A pre-existing red I did not cause and did not fix, and it is the ONLY thing red here:**
  `lint_citations` exits 1 on
  `::error::UNANCHORED PMCID PMC9825574 — appears only in prose
  (research/autonomy/sprint-2026-09-01/S25-P1-ANCHOR.md)`. **That is seat S25's findings file**, and
  I confirmed the error is independent of everything I touched by removing my artifact and re-running
  (the error persists). It needs a ledger row or an artifact anchor from whoever owns that file.

### ⭐ Why the notices are a SECOND file, and not a section of the sweep

The sweep artifact must be anchor-excluded (above). But a retraction notice's record is an ordinary
fetch product of four identifiers, and it *should* anchor them — otherwise citing PMID 42622620 in
prose is indistinguishable from inventing it. **Measured:** with the notices inside the sweep file,
`lint_citations` errored `UNANCHORED PMID 42622620 — appears only in prose`. Splitting them fixed the
DOI immediately and **left the PMID still unanchored**, because `PATTERNS["PMID"]` needs the literal
token `PMID`, a `pubmed.ncbi.nlm.nih.gov` URL or an `EXT_ID` — *a lowercase `"pmid"` JSON key anchors
nothing*, which is the hole `lint_citations.py`'s own header records costing a drafting agent a red
gate. Adding the `pubmed_url` field that header prescribes cleared it. Both facts are written into
the new file so the next reader does not rediscover them.

## ⚠ Three defects I caught in my own work, recorded because each nearly shipped

Reconstructing the seven truncated DOIs, I **typed four of the seven suffixes from inference**
(`0022-2836(73)90388-4`, `S1093-3263(98)00003-3`, `s0300-9084(97)86730-6`,
`s1470-2045(11)70097-8`) and queried PubMed with them. Three returned records — **for the wrong
papers**. `grep`-ing the actual strings out of the prose gave `…(73)90011-9`, `…(98)00002-3`,
`…(97)86731-4`, `…(11)70057-2`: **four of seven wrong**, and the wrong ones *resolved*, which is the
dangerous direction. The committed artifact uses only the grepped forms. This is §7's rule —
*never write an identifier from recollection* — failing in the sub-case that feels like arithmetic
rather than memory, and the only thing that caught it was going back to the file.

**Second: I marked identifiers clean that no fetch had ever seen.** The first generator classified
any DOI not on a known-bad list as checked — so four identifiers other seats added to prose *while
this seat was running* came out `clean` without a single PubMed call touching them. Fixed by pinning
the swept universe to the snapshot the fetches actually ran against; anything outside it is
`NOT SWEPT`. The four are now genuinely swept, and the mechanism that caught them is the one the
brief asked for.

**Third: my one-token edit to `lint_citations.py` reddened a guard whose property was untouched.**
`test_citation_type_guard.py::test_the_cache_is_not_an_anchor_for_the_provenance_gate` asserts the
literal string `TYPE_CACHE_REL)` appears in the source; appending to that tuple broke the spelling
while preserving the behaviour. **Repaired by inserting rather than appending** — no edit outside my
owned paths — and my own test was rewritten to assert the behaviour (run `survey()`, check the
unanchored set is non-empty and overlaps the sweep's keys) instead of grepping for a tuple.

## Ledger rows the driver should write

| `what` | `kind` | `state` |
|---|---|---|
| Fetch the grounds of the Safe 2025 retraction (notice PMID 42622620, DOI 10.1080/21541264.2026.2714669) via `verify-refs.yml`; record them in the sweep artifact's `retracted_detail` | `fetch` | `ready` — $0 CI, needs a one-line `FIXED_DOIS` addition |
| Add the retraction-notice identifier (PMID 42622620, 2026-08-20) to the two passages that already say the Safe 2025 review is retracted — `nr4a3-druggability-reconciliation.md` and `degrader/nr4a3-degrader-paper.md` ref 6. A reader who follows the citation should land on the notice, not infer it | `prose` | `ready` — driver sequences; both are one clause, replacing not appending |
| Flip **unacknowledged** retracted citations from ADVISORY to ERROR in `lint_citation_types.check()` (step 3 of §5) | `gate` | `blocked` on one hardening round over the `acknowledged` reasons; must not be the cycle that wrote them |
| `lint_citations.PATTERNS["DOI"]` truncates Elsevier legacy DOIs at `(` — 7 identifiers stored truncated, and they anchor and ledger under the truncated form | `tooling` | `ready` — anchoring half, needs the owner of that pattern |
| Size a non-PubMed withdrawal sweep: 82 NCT, 69 arXiv, 59 GEO, 27 non-PubMed DOIs currently UNKNOWN for withdrawal/retraction | `scoping` | `ready` |
| `PMC9825574` unanchored + not in ledger, from `S25-P1-ANCHOR.md` — reds `lint_citations` today | `gate` | `ready` — belongs to the seat that wrote the file |
