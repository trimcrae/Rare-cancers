---
id: DOC-DEGRADER-CITATION-AUDIT-2026-08-08
title: Citation-provenance audit of nr4a3-degrader-paper.md — all 74 unanchored identifiers resolve, six are defective anyway
level: L3
kind: memo
status: live
canonical_for:
  - the resolution status of every citation identifier in nr4a3-degrader-paper.md that no fetch product anchored
  - the enumerated citation defects blocking submission of the degrader paper
purpose: >
  Answer, for each of the 74 citation identifiers that research/manuscripts/nr4a3-degrader-paper.md
  carried with no fetch-product anchor anywhere in this repository, whether it resolves — and, where
  it does, whether it resolves to the work the manuscript says it does. The paper is aimed at journal
  submission, and 74 unchecked identifiers is a publication-blocking defect independent of the science.
scope: >
  Identifier resolution and bibliographic metadata (title, authors, journal, volume, pages, year),
  fetched from Crossref, Europe PMC, data.rcsb.org and the DOI handle system. It deliberately does NOT
  establish that any cited work SUPPORTS the sentence citing it — that requires reading the papers, and
  the two characterization flags below are exactly the cases where the title alone says it may not.
  Covers this paper's unanchored set only; the other 140 unanchored identifiers in the repository, and
  reference entries carrying no identifier at all, are out of scope and named as such.
audience:
  - maintainers
  - autonomous research agents
  - external reviewers
date: 2026-08-08
last_verified: 2026-08-08
related:
  - research/manuscripts/citation-provenance-ledger.json
  - research/manuscripts/lit-targets-degrader-citations.json
  - research/manuscripts/lint_citations.py
  - research/manuscripts/nr4a3-degrader-paper.md
---

# Citation-provenance audit — `nr4a3-degrader-paper.md`, 2026-08-08

**Headline: all 74 unanchored identifiers RESOLVE. None is fabricated. Five are defective anyway, and one of
those is disqualifying on its own — a PMID that resolves cleanly to the wrong paper.**

| | count |
|---|---|
| identifiers audited (the paper's full unanchored set) | **74** |
| **RESOLVES** — registry returned a record | **74** |
| **DOES NOT RESOLVE** — no such identifier | **0** |
| **PAYWALLED** — blocked the check | **0** (see *What "paywalled" means here*) |
| **defective anyway** — resolves, but not to what the manuscript says | **5** across 4 references: 2 citation-integrity failures (D1, D2), 1 wrong year (D3), 2 descriptor flags needing a human read (D4, D5). D6 below is a sixth entry from the same block, checked and **clean**. |

The paper carried **by far the largest unanchored block in the repository**: 74 identifiers, against 22 for the
next file down (`emc-unexplored-treatment-lanes.md`) and 17 for the one after that — more than a third of the
214-identifier baseline the ledger was opened with on 2026-08-07. Under
[`lint_citations.py`](./lint_citations.py) "unanchored" means the identifier appeared in **no tracked
`.json`/`.jsonl` fetch product anywhere in this repository**, i.e. *nobody had ever checked it.* That is now
false: every one of the 74 has a machine-fetched bibliographic record in
[`lit-targets-degrader-citations.json`](./lit-targets-degrader-citations.json), and every one of the 74 ledger
rows in [`citation-provenance-ledger.json`](./citation-provenance-ledger.json) moved from
`unverified_at_baseline` to `verified`, carrying the returned title and year.

⚠ **`verified` means the identifier was fetched and answered. It does NOT mean the citation is right** — that
is the whole point of the list below, and it is why every defective entry also carries a `defect` field in the
ledger. A resolving identifier attached to the wrong claim is, to a reader who pulls it, indistinguishable from
a fabricated one.

---

## 1 · The defects, enumerated

Nothing here is a summary count. Each row names the identifier, what the registry actually returned, and the
manuscript claim that rests on it.

### ⛔ D1 — `PMID 37444483` resolves to a **different paper**. Reference 15. *Must be fixed before submission.*

* **Manuscript claim (References, entry 15, line 2984):** *"Khan J, Ullah A, Goodbee M, Lee KT, Yasinzai AQK,
  Lewis JS Jr, Mesa H. **Acinic Cell Carcinoma in the 21st Century: A Population-Based Study from the SEER
  Database and Review of Recent Molecular Genetic Advances.** Cancers 15(13):3373 (2023). PMID 37444483;
  PMC10340722; doi 10.3390/cancers15133373."* — the paper's only population-level source for acinic cell
  carcinoma, the second NR4A3-driven indication in §1 and SI §S4.
* **What Europe PMC returns for `EXT_ID:37444483`:** *"Post-Surgical Prognosis of Patients with Pineoblastoma:
  A Systematic Review and Individual Patient Data Analysis with Trends over Time"*, Nandoliya KR, Sadagopan NS,
  Thirunavu V, … Magill ST. **Cancers 15:3374, DOI 10.3390/cancers15133374, PMC10340270.** A pineoblastoma
  review. Nothing to do with acinic cell carcinoma or NR4A3.
* **How the true value was established (two independent fetches, not inference):** the *same reference's other
  two identifiers* both return the acinic-cell paper and both report its PMID as **37444484** — Europe PMC
  `PMCID:PMC10340722` → pmid 37444484; Europe PMC `DOI:"10.3390/cancers15133373"` → pmid 37444484; and a
  confirmatory `EXT_ID:37444484` returns the acinic-cell paper. Crossref independently returns
  10.3390/cancers15133373 = *Acinic Cell Carcinoma in the 21st Century*, Cancers 15:3373, Khan J et al.
* **Nature of the error:** one digit. 3373/3374 and 37444483/37444484 are adjacent articles in the same issue,
  which is exactly how this survives proof-reading — and exactly why a reviewer who pulls the PMID lands on a
  pineoblastoma paper.
* **Fix:** `PMID 37444483` → `PMID 37444484` in entry 15. Everything else in entry 15 is correct: author list,
  title, journal, volume 15, page 3373, year 2023, PMCID and DOI all verified against the record.

### ⛔ D2 — Reference 57 is bylined to someone who is **not an author**. `PMID 40454645` / 10.1056/NEJMoa2505725.

* **Manuscript claim (entry 57, line 3108):** *"**Hurvitz SA, et al.** Vepdegestrant, a PROTAC Estrogen
  Receptor Degrader, in Advanced Breast Cancer. N Engl J Med (2025)."* Cited in §1 (lines 150–153) as the
  clinical precedent for targeted protein degradation and, in-text, as *"Hurvitz 2025"*.
* **What both registries return:** 27 authors — **Campone M**, De Laurentiis M, Jhaveri K, Hu X, Ladoire S,
  Patsouris A, Zamagni C, Cui J, Cazzaniga M, Cil T, Jerzak KJ, Fuentes C, Yoshinami T, Rodriguez-Lescure A,
  Sezer A, Fontana A, Guarneri V, Molckovsky A, Mouret-Reynier MA, Demirci U, Zhang Y, Valota O, Lu DR,
  Martignoni M, Parameswaran J, Zhi X, **Hamilton EP**, VERITAC-2 Study Group. N Engl J Med **393:556–568**
  (2025). **`Hurvitz` appears nowhere in the byline** (checked against the full 27-name Crossref list and the
  full Europe PMC `authorString`).
* **Why it is not harmless:** the identifier resolves, so the citation looks sound to every automated check —
  including `lint_claims`, which grades claim strength, not provenance. A reader who follows it finds a real
  paper with a byline that does not match, which reads as invention.
* **Fix:** entry 57 → *"Campone M, De Laurentiis M, Jhaveri K, et al."*, add volume/pages **393:556–568**, and
  change the in-text *"Hurvitz 2025"* at line 153. The §1 efficacy numbers themselves are not in scope of this
  audit — this is a byline defect, not a data defect.

### ⚠ D3 — Reference 33 gives the wrong year. `PMC6926456`.

* **Manuscript claim (entry 33, line 3037):** *"Structural basis of binding of homodimers of the nuclear
  receptor NR4A2 to selective Nur-responsive DNA elements. J Biol Chem **(2020)**. PMC6926456. [NR4A DNA-binding
  grammar; PDB 6L6Q/6L6L.]"*
* **What Europe PMC returns:** title matches exactly; **pubYear 2019**, J Biol Chem, DOI
  10.1074/jbc.ra119.010730, first author **Jiang L**.
* **Fix:** year → 2019. The audit also supplies the author list and DOI the entry is missing — the manuscript
  itself flags entry 33 as one of three deliberately left incomplete "until completed from the publisher record
  before submission", and this fetch completes it.

### ⚠ D4 — Reference 61 is described as PROTAC prior art; the paper is about **molecular glues**.

* **Manuscript claim (entry 61, line 3130), under the heading *"Prior art in alchemical ternary-cooperativity
  free-energy calculation"*:** *"J Chem Theory Comput (2025). doi 10.1021/acs.jctc.5c00064. [**Alchemical
  PROTAC** ternary-cooperativity ΔΔG_coop cycle. Authors/title to be completed at submission.]"*
* **What Crossref returns:** *"Quantifying Cooperativity through Binding Free Energies in **Molecular Glue
  Degraders**"* — Dudas B, Athanasiou C, Mobarec JC, Rosta E. JCTC **21:5712–5723** (2025).
* **Status: flagged, not resolved.** Molecular glue and PROTAC are different modalities, and the manuscript's
  bracket asserts the latter. Title-level evidence only — settle it by reading the paper, not by re-guessing.

### ⚠ D5 — Reference 63 is grouped under *alchemical* prior art; the paper says **end-point**.

* **Manuscript claim (entry 63, line 3134), same heading:** *"J Chem Inf Model (2024). doi
  10.1021/acs.jcim.4c01227. [PROTAC ternary cooperativity / **paralogue selectivity** by free-energy
  calculation. Authors/title to be completed at submission.]"*
* **What Crossref returns:** *"Characterizing the Cooperative Effect of PROTAC Systems with **End-Point**
  Binding Free Energy Calculation"* — Xu K, Wang Z, Xiang S, Tang R, Deng Q, Ge J, Jiang Z, Yang K, Hou T,
  Sun H. JCIM **64:7666–7678** (2024).
* **Status: flagged, not resolved.** End-point (MM/PB(GB)SA-class) is a different method class from alchemical,
  and the section's whole purpose is to position this work against *alchemical* prior art. No
  paralogue-selectivity claim is visible at title level either. Both need a human read of the paper.

### ⚠ D6 — The same title-vs-descriptor question, benign, on reference 62.

Entry 62 (10.1021/acs.jctc.5c00736) resolves to *"Cooperative Free Energy: Induced Protein–Protein
Interactions and Cooperative Solvation in Ternary Complexes"* — Chen S-Y, Solazzo R, Fouché M, Roth H-J,
Dittrich B, Riniker S. JCTC **21:8557–8570** (2025). The subject matches the manuscript's description; recorded
here only because D4 and D5 came from the same three-entry block, so the block should be read as a whole.

---

## 2 · What the audit also fixes for free

The manuscript says in several places that an author list or title *"was not retrievable from a primary source
in this environment"* and is *"deliberately left blank rather than reconstructed, since a plausible-looking but
unverified citation is a fabrication"* — the right call, and it was true when written. For the entries whose
identifiers fall inside this audit it is no longer true, and the registries supply the missing strings:

| entry | now retrievable |
|---|---|
| 33 | Jiang L, Dai S, Li J, Liang X, Qu L, Chen … (Europe PMC `authorString`, via PMCID:PMC6926456). J Biol Chem **2019**, DOI 10.1074/jbc.ra119.010730, PMID 31723028 |
| 34 | Gao Y, He X-Y, Wu XS, Huang Y-H, Toneyan S, et al. Nat Cell Biol 25:298–308 (2023) |
| 61 | Dudas B, Athanasiou C, Mobarec JC, Rosta E. *Quantifying Cooperativity through Binding Free Energies in Molecular Glue Degraders.* JCTC 21:5712–5723 (2025) |
| 62 | Chen S-Y, Solazzo R, Fouché M, Roth H-J, Dittrich B, Riniker S. *Cooperative Free Energy: Induced Protein–Protein Interactions and Cooperative Solvation in Ternary Complexes.* JCTC 21:8557–8570 (2025) |
| 63 | Xu K, Wang Z, Xiang S, Tang R, Deng Q, Ge J, Jiang Z, Yang K, Hou T, Sun H. *Characterizing the Cooperative Effect of PROTAC Systems with End-Point Binding Free Energy Calculation.* JCIM 64:7666–7678 (2024) |
| §2.2 in-text 10.1021/acs.jctc.6c00135 | Zhang S, Miller JJ, Bowman GR. *How Well Can AI and Physics-Based Simulations Predict the Probability a Cryptic Pocket Is Open?* JCTC 22:3839–3850 (2026) — title matches the in-text use exactly |

Two entries stay open and are **outside this audit's scope, because they carry no identifier for it to check**:
entry 60 (*"Chen et al. (2023)"*, no DOI recorded anywhere in the program map) and the worm-like-chain reference
the manuscript deliberately declines to cite in §2.10. `lint_citations` never saw either — a missing identifier
is invisible to a gate that reads identifiers, which is worth stating plainly next to a clean audit result.
Entry 36 (Tumor Biol 33:1599–1607) is likewise out of scope here: its DOI is already anchored by another
artifact, so it was not in this paper's unanchored set, and its blank author list is a separate open item.

**Reference 1 (PDB 8XTT) verified in full**, against `data.rcsb.org` and the DOI handle system: SOLUTION NMR;
`conformers_calculated_total_number` 100, `conformers_submitted_total_number` **20**;
`deposited_polymer_monomer_count` **248**; deposit **2024-01-11**, initial release **2025-01-15**; primary
citation `journal_abbrev: "To Be Published"`, authors Yoo J.Y., Yoon H.S. Every particular the manuscript
asserts about its own experimental starting structure — including *"primary literature citation not yet
published"* — matches the deposition record.

## 3 · Everything else checked and clean

* **Volume, first page, last page, year and first author** were compared against the record for all 28
  references that state them. All 28 agree. (Two Nature-family entries return no volume/page from Crossref
  because the publisher deposits an article number; not a defect.)
* **Full author lists** were compared for all 34 references that give one. All 34 agree, name for name and in
  order — including the seven-name list in the very entry whose PMID is wrong (D1).
* **Internal consistency**: for the 15 references carrying two or three of these identifiers (PMID + PMCID +
  DOI), each identifier was resolved separately and the returned titles compared against each other.
  **Fourteen agree. One does not — reference 15, which is D1**, and it was the disagreement between a
  reference's own identifiers that exposed it.
* **The three in-text MGI-sourced PMIDs in §2.4** — `9520484` (Saucedo-Cardenas O, et al., PNAS 1998,
  *Nurr1 is essential for the induction of the dopaminergic phenotype…*), `9608532` (Castillo SO, et al., Mol
  Cell Neurosci 1998, *Dopamine biosynthesis is selectively abolished in substantia nigra/ventral tegmental
  area…*) and `20016108` (Kadkhodaei B, et al., J Neurosci 2009, *Nurr1 is required for maintenance of maturing
  and adult midbrain dopamine neurons*) — all resolve to real *Nr4a2*/Nurr1 loss-of-function papers consistent
  with the phenotypes the paragraph attributes to them.

## 4 · Method, and what it does and does not establish

$0, entirely through GitHub Actions ([`fetch-literature.yml`](../../.github/workflows/fetch-literature.yml),
`targets_json` path) because this container's egress proxy 403s NCBI, PMC, Europe PMC and Springer on CONNECT.
DOIs → Crossref `api.crossref.org/works/<doi>`; PMIDs and PMCIDs → Europe PMC REST search
(`EXT_ID:` / `PMCID:`, `resultType=lite`); PDB DOI additionally against `data.rcsb.org` and the DOI handle
system. Round 1 = run `31270123183` (corpus at `literature-cache:literature/degrader-citation-anchor/`);
round 2 = run `31270300182`, which re-fetched the 13 DOIs Crossref answered **429** in round 1, half of them
through Europe PMC to sidestep the throttle
(`literature-cache:literature/degrader-citation-anchor-round2/`).

**Every dispatch carried a known-positive and a known-negative on both endpoints**, because a run in which
nothing resolves and a run in which the endpoint is down are otherwise identical: Crossref positive
10.1038/nature14539 → 200 + *"Deep learning"*; Crossref negative (a deliberately nonexistent DOI under the
unassigned 10.9999 prefix, spelled out only in the two Actions runs' inputs so that this note does not put a
known-bad identifier into repository prose) → **404**; Europe
PMC positive `EXT_ID:26017442` → hitCount 1; Europe PMC negative `EXT_ID:99999999` → **hitCount 0**. All four
behaved in round 1, and both Crossref controls were repeated in round 2 and behaved again — so a 404 or an
empty hit list anywhere in this corpus would have been readable as a real absence. Neither occurred.

⚠ **A 429 is not a non-resolution, and treating it as one would have manufactured 13 fabrications.** Thirteen
DOIs came back rate-limited in round 1. Every one resolved on re-fetch. Any audit of this kind that reports a
throttle as a missing record produces exactly the false accusation it exists to prevent.

**What "paywalled" means here, and why the column is zero.** Crossref and Europe PMC serve *metadata* openly, so
a subscription paywall cannot block identifier resolution, and none did. Full-text access is a separate axis and
was not the question: of the 26 identifiers queried through Europe PMC, 11 are flagged `isOpenAccess: Y`, 11 more
have full text in PMC/Europe PMC, and 4 (`34124809`, `35482177`, `40454645`, `9608532`) have neither. **This
audit verifies that each identifier exists and names the work the manuscript says it names. It does not verify
that the work supports the sentence citing it** — that requires reading the papers, and the two
characterization flags (D4, D5) are precisely the cases where the title alone says the descriptor may be wrong.

## 5 · One identifier outside this paper, checked because it was free

While this audit was running, `lint_citations.py` was widened (b1b9f7b65) so the anchor scan recognises the
`{name: url}` form every `lit-targets-*.json` uses, and so `TRAILING` strips backticks and asterisks. Two
consequences landed on the ledger, and both are recorded here because the ledger has one owner and this audit
was it:

* **35 baseline rows were stored under a punctuation-laden key** (`…/anie.201806037` + a stray backtick) and
  were orphaned by the widening — which does not fail safe: an orphaned baseline row reappears as a NEW
  unanchored identifier, i.e. the gate accuses already-triaged citations of being fabrications. The gate now
  normalises stored keys on read; the ledger was additionally re-keyed to the clean form and 13 rows that had
  become exact duplicates of each other were merged, files-lists unioned, statuses preserved. 215 rows → 202.
  No status was changed by that operation and no identifier was added or dropped.
* **`PMID 41712689` became visible for the first time**, in `research/IDEAS.md:412` and
  `research/field-scan-log.md:89`. It is pre-existing prose written as a `pubmed.ncbi.nlm.nih.gov/…` URL, which
  the old pattern could not see, so it is baseline material and not a new citation. ⚠ **The two files describe
  it differently** — IDEAS.md as MOF-nanoparticle ASO delivery, the field-scan log as immunity — and it is a
  *delivery* citation, which is load-bearing for PUB-ASO, so the disagreement mattered. **Fetched, and it is not
  a disagreement:** Europe PMC returns *"Strengthening Antisense Oligonucleotide-Mediated Anti-Tumor Immunity
  via Metal-Organic Framework Nanoparticles"* — Nowak JA, Cho E, Davis MA, … Farha OK, Teplensky MH, Nano Lett,
  doi 10.1021/acs.nanolett.5c05579. A MOF-nanoparticle ASO-delivery paper whose endpoint is anti-tumour
  immunity. Both descriptions are the same paper seen from different ends; **neither file is wrong**.
  ⚠ That settles *which paper it is*. It does not establish that the paper supports the delivery claim built on
  it — that needs the paper read, and this audit did not read it.

## 6 · Verdict

**On citation grounds this paper is not yet submittable, and the blocker is small and specific.** No identifier
in it is invented — the failure mode that produced
[`lint_citations.py`](./lint_citations.py) (a PMID written from recollection that existed in no committed
source, which passed `lint_claims` twice while six invented titles and author-lists went out beside it) **did
not happen here.** What did happen is one transposed digit that points a reader at a pineoblastoma review
(**D1**) and one byline naming a non-author (**D2**). Both are one-line edits. Fix D1 and D2, correct the year
in D3, and read the two papers behind D4 and D5 before their descriptors stand; after that the paper's citation
record is, to the limit an offline check can reach, sound — and it is now the best-anchored manuscript in the
repository rather than the worst.

*Files: evidence in [`lit-targets-degrader-citations.json`](./lit-targets-degrader-citations.json); per-identifier
status and `defect` fields in [`citation-provenance-ledger.json`](./citation-provenance-ledger.json); raw fetched
payloads on the `literature-cache` branch under `literature/degrader-citation-anchor{,-round2}/`. This audit
changed no text in `nr4a3-degrader-paper.md` — the fixes above are unapplied and are the manuscript owner's call.*
