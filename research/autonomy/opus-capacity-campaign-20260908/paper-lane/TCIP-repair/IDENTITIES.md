---
id: DOC-OPUS-CAMPAIGN-TCIP-IDENTITIES
title: "TCIP F01–F13 repair — file, source and dependency identities"
level: L4
kind: record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Identities for the TCIP F01–F13 author repair

All hashes are SHA256 of the actual local bytes, measured 2026-09-08 in worktree
`/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`.

## Files changed by this lane

| file | bytes before | SHA256 before | bytes after | SHA256 after |
|---|---:|---|---:|---|
| `research/manuscripts/tcip/tcip-induced-interface-preprint.md` | 28,068 | `2e2b7862c3c6412ff4ae9086fd2acca799ae8999511ca607d1a49e416e82d9a9` | 51,625 | `d211e11afe565a734282d3830e5223efaf79590add7de36769eb2eac361f0e20` |
| `research/manuscripts/tcip/tcip-induced-interface-preprint-si.md` | 16,663 | `3483c0bbcbd94e4faa5b3de38da8010130b189336b79ac27cd08101c56748ba3` | 35,997 | `72d21e7f4893f3a9103400a64d05304236707aa2e8f27d2057348ea03de2a19e` |

The "before" bytes are retained verbatim in this directory as
`BEFORE-tcip-induced-interface-preprint.md` and `BEFORE-tcip-induced-interface-preprint-si.md`, whose
hashes equal the "before" column above. They are byte-identical to the frozen capsule copies under
`inputs/frozen/research/manuscripts/tcip/` and to the values recorded in the final review, so the
working tree was at the frozen pin `f43f1495f40d8aff7b4f34bd385d55aac521a500` for both files when
this lane began.

## Files inspected and deliberately NOT changed

| file | bytes | SHA256 | why |
|---|---:|---|---|
| `research/manuscripts/tcip/tcip-interface-floor-sizing.md` | 21,346 | `f865a51c85a01ad6392d7951492acd48fd8e2a151122063fa6987bf6057ba707` | outside named scope; still carries withdrawn claims — see `SIZING-MEMO-CARRYOVER.md` |
| `systems/graph/publications.json` | 63,825 | `11b8a785ac95809d844f46f6427601c67f73f9137a063f6d91b4b93ba0d5bf53` | parent-owned shared file; unapplied patch prepared under `patches/` |

## Artifacts produced by this lane

| artifact | SHA256 |
|---|---|
| `DIFFS/tcip-induced-interface-preprint.md.diff` | `f45a0ed499a171efe12155ccaa2f5607414c841792db5e76e88b0ad98c228823` |
| `DIFFS/tcip-induced-interface-preprint-si.md.diff` | `f47b86975d0dd266ae9f4cac33863e936ca7d59f6e5e1754d8e398190dad88ac` |
| `patches/0001-systems-graph-publications-PUB-TCIP-narrowed.patch` | `f573ed19ffd9a735c95c8742963ea4bf6d30205b04e1b10a2345fba5fb2b7832` |

## Review capsule relied on (verified by the parent before dispatch; spot-checked here)

Extracted read-only at
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/tcip/x/`.

| document | bytes | SHA256 |
|---|---:|---|
| `TCIP-final-review-root-adjudication-20260908.md` | 5,859 | `131a610dcf3b76afad00f53a0aca47020f44864edc56a84174b724c05bb9e13c` |
| `tcip-final-review-20260908/FINAL-SCIENTIFIC-REVIEW-TCIP.md` | 52,425 | `a00bec7213282192725722bb84736470868523acaa13766c2dac44ea4da82101` |
| `tcip-final-review-20260908/SOURCE-INTAKE-ADDENDUM-20260908.md` | 19,411 | `7d2941dbbd64c080b37ac619ff4532b66134d7eb782b9fdb3377c0c101ff77f6` |

Both review documents and the root memo were read in full as originals. The whole archive was **not**
re-hashed as a task, per the dispatch instruction.

## Dependencies read for specific numbers, from the capsule's read-only frozen copies

Under `.../tcip-final-review-20260908/inputs/frozen/research/modalities/`:

| file | what was read from it |
|---|---|
| `nr4a3-induced-interface-census.json` | 9MZA entry: entity/chain descriptions, both `A1BUC` copies with `n_heavy_atoms` 81 and their `chains_touched`, the five `ligand_bridged_chain_pairs`, and the three retained `chain_pairs` (A/C 71/66; A/D 6/7; B/C 7/6, all with 4 residues per side and the recorded `n_query_points`). 7LWG A/B 67/64. |
| `nr4a3_induced_interface_census.py` | `contact_profile` exact-distance banding; `protein_chains` eligibility (≥50 % amino-acid atoms and ≥40 of them); `bridging_ligands` (`MIN_BRIDGING_LIGAND_ATOMS = 12`, `LIGAND_CONTACT_A = 4.5`, `spans` at ≥3 heavy atoms); the zero-contact-band `continue` applied to both directions before induced-pair selection; `main()` requiring `<corpus-dir>` and returning 2 otherwise. |
| `nr4a3_basin_search.py` | `PARAMS` (`hard_clash_A` 3.0, `soft_clash_A` 3.6, `max_soft_clashes` 6, `contact_A` 6.0, `min_contact_residues` 12); the radial draw `L_min + (L_max-L_min)*U**(1/3)` and its "uniform in the shell VOLUME" comment; the placement loop scoring `md(tp) - slack` and rejecting on hard clash, soft budget or contact floor; anchor clearance on `md(ae) - slack`. |
| `nr4a3_tcip_reach.py` | the `--refresh-derived` branch calling `verdict(...)` without the named-effector argument; the CLI options quoted in the corrected reproduction section. |
| `basin_geom.py` (referenced) | cell-centre distance lookup and half-cell-diagonal slack, `sqrt(3)*0.9/2 = 0.7794228634 Å`. |

Reviewer calculation records read for retained arithmetic (`reviewer-calculations.json`,
`reviewer-calculations-stdout.txt`, `reviewer-calculations-exit.txt`, exit **0**): the ablation
counts and stored Wilson intervals, the enumeration inventory (576 cells, 172,800,000 draws), the
seed definitions and the 56 `bcl6`/`vhl` stream collisions, the two omitted 9MZA candidate pairs, the
shell-proposal quantiles (0.125 against 0.232142857), the predicate non-identity example (3.2206 Å),
the points-versus-residues arithmetic, the additive-offset algebra (0.90 → 0.91) and the ternary odds
counterexample. These are the reviewer's calculations, not new measurements by this lane.

## Original source identities relied on (from `source-intake/inputs/`, read-only)

Seven original retained source files, 1,340,205 bytes total, delivery revision
`c6d97dcc2043bd2a21c749339637286915a29a82`. Used here:

| source file | what this paper cites it for |
|---|---|
| `tcip-9mza-2026-08-07__cif_9MZA.txt` (SHA256 `b81668a1eaeb1eb40e74c99b65f093f647fd78eec30cecf201aa83006bc75780`) | entry 9MZA, title, X-ray, 2.1 Å, primary citation DOI `10.1101/2025.03.14.643404` / PubMed `40166243`, BCL6 and p300 entities, chain assignments, `A1BUC`, A2B2 assembly, UniProt ranges and sequence conflicts |
| `tcip-9mza-2026-08-07__rcsb_entry_9MZA.txt` | independent entry payload: title, primary citation, accession info (deposited 2025-01-22, released 2025-04-16), resolution |
| `tcip-9mza-2026-08-07__rcsb_assembly_9MZA.txt` | hetero 4-mer A2B2 symmetry record; author-provided FRET assembly evidence field; modeled/unmodeled monomer totals |
| `tcip-kat-structure-2026-08-07__epmc_kat_tcip_record.txt` | `hitCount: 2`; Cell article PMID 42476129 / DOI `10.1016/j.cell.2026.06.037`; preprint record; `commentCorrectionList` update relation; `isOpenAccess: N`, `inEPMC: N`, free DOI link, `cc by` field; both abstracts |
| `tcip-kat-structure-2026-08-07__rcsb_cite_pubmed_42476129.txt` | **HTTP 400, invalid search attribute** `rcsb_primary_citation.pdbx_database_id_PubMed` — cited only as an invalid-request outcome, never as a negative search or an access denial |
| `induced-proximity-transcription-2026-08-07___index.json` | 100 records, 20 with a full-text pointer; no query/date/total-hit/limit/pagination closure |
| `induced-interface-vs-output-2026-08-07___index.json` | 300 records, 51 with a full-text pointer; same absent closure |

`SHA256SUMS.txt` in that delivery carries a stale self-entry (declares the empty-file digest for
itself); its actual 1,602-byte SHA256 is
`de6eb0e6a8ab04bd83ac7b2b2a85b7693b2b762b2d3f5878d4f96a4ee7ea5610`. All seven source entries match
their actual bytes. This is recorded in SI §S8 without rewriting any source evidence.

**No source was queried, fetched, retried or acquired by this lane.** All source reading was of the
read-only local copies above.
