---
id: DOC-MF1-RESIDUAL2-CLOSURE
title: "MF1 residual-2 — five-item dated closure of the root disposition"
level: L4
kind: memo
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# MF1 residual-2 — five-item dated closure

Scope: the five residues named in the root disposition memo
`MF1-residual-direct-root-disposition-20260908.md` (8,586 B, sha256
`c640196b2bbf726392307295a4232968c3581c1ea78ebec30dc8843d42710656`). **R2, R3, R4 (count 18), R5
and the R1 propagation from the previous batch are accepted and were not redone.** One new
extraction was run, after the display and template changes settled, exactly as admitted.

| # | residue | what was actually changed, dated 2026-09-09 | where | status |
|---|---|---|---|---|
| **1** | The V5 result display still printed the unsupported *"~34× the statistical uncertainty"* beside a statement that it is omitted | The result cell for `V5` is now an **explicitly labelled source excerpt** — `⭐ SOURCE EXCERPT — one fragment omitted, see the header note:` — with that one fragment omitted and disclosed verbatim in the inventory header and SI footer item 6 as a withdrawn quantity. ⛔ **Nothing edited at the source**: `instrument-census.json` keeps the full original string and is hashed into the manifest, so the original is retrievable at a named, bound source. ⛔ **No replacement multiplier computed or adopted.** Reference **+0.944**, result **−0.599**, absolute error **1.543** and **wrong sign in all 3 replicates** are all preserved and displayed. A stdout counter (`result-display omissions applied: 1 of 1 declared (V5)`) records that the fragment was still present in the source and was omitted from the display; it is a disclosure counter, not a guard | `extract_mf1_inventory.py` §2c + inventory header + SI_FOOTER item 6 → `MF1-instrument-inventory.md`, SI S2 | **CLOSED** |
| **2** | Stale "four cells unapplied" labels, after the four source cells were actually applied | The four-cell repair — census `V11.result`, `V16.result`, `V16.scope_limit`, `V20.scope_limit` — **was applied by the parent at `91609d30fdc672f4dbc9eb191e6342a7ddd4f61d`**, with the census regenerated from the corrected roadmap and the roadmap's *"with a quantified bound"* clause removed. The stale labels are updated to that actual dated state in main §2, main §10.5 item 9, main §11's register list, the end of `corrective-interpretations-2026-09-08.md`, the extractor's §2b comment, the `write_inventory` header and `SI_FOOTER` item 5. ⛔ The adjacent column is **no longer** called a *superseded historical annotation*: it is now **the census `scope_limit` at the bound revision**, because an author `CURRENT_SCOPE` override existing for a row does **not** by itself supersede the census cell — at this revision `V16`, `V20` and `V5` carry their own dated corrections at source. Historical records (the filed patch sets, the earlier response/patch notes) are preserved and marked with **additive** dated notes; ⛔ **no P1–P6 or Q patch was reapplied** | main §2, §10.5.9, §11 · `corrective-interpretations-2026-09-08.md` · extractor §2b / header / footer | **CLOSED** |
| **3** | The settled-identity narration was wrong about the outputs and the runs | Stated plainly: **the extractor writes FOUR outputs** — `MF1-quantitative-results.md`, `MF1-instrument-inventory.md`, `MF1-dependency-manifest.json` and the SI at `research/manuscripts/methods-record/degrader-methods-failure-record-SI.md`, all four written by `main()`. **Parent RUN10 changed the inventory AND the SI; parent RUN13 rebound the manifest.** Measured from the retained bytes of the two commits: SI 40,004 B `36fcdc3b…1cbf819` at `f6107376c` → 41,072 B `c4e2f1e9…02de18c` at `806ab2ecd`, differing in **exactly four census-derived cells across three instrument rows** (`V11.result`, `V16.result`, `V16.scope_limit`, `V20.scope_limit`), with the recorded values inside them unchanged (*p* = 0.393 / 0.747; **S = −0.1297 ± 0.3264 kcal/mol**) and dated correction prose added. ⛔ Author **RUN05**, parent **RUN10** and parent **RUN13** are preserved as **three actual original executions**, none relabelled or merged, and **no extraction was rerun to establish this** | extractor docstring **and main §2's extraction-boundary paragraph** (both applied) · ⛔ **UNAPPLIED** parent diff at `patches/UNAPPLIED-0001-parent-settled-identities-four-outputs.diff` | **CLOSED, one part UNAPPLIED by design** |
| **4** | The transposition was still attributed to the root memo | Corrected in both places. The **original 6,819 B root residual memo** (sha256 `ecb01e1c…23d677ce2`) is **CORRECT** — all five pairs in source order. The **derived 9,259 B `CONTRACT-MF1-R1-R5-residual-author.md`** (sha256 `4f93302c…9d37e4`) is what **transposed** them. The `BENCHMARK-FACTS.md` correction (8,278 B, sha256 `5c717270…bbf3bef4d8`) **already landed and is accepted**, and is not redone. Three separate things are now kept separate wherever the count is discussed: **(1)** the original final review **and the first 6,673 B root adjudication** carried the mistaken combined **17**; **(2)** the **focused post-repair verification** originated the correction **17 + 1** and is **not** to be blamed for the error; **(3)** the **later 6,819 B root residual memo** correctly states **18** | `MF1-residual/DENOMINATOR-ERRATUM.md` (table row + new dated section) · `MF1-residual/R1-R5-CLOSURE-MAP.md` R3 **OPEN** row and R4 **ATTRIBUTED** row | **CLOSED** |
| **5** | The extractor's opening generated-versus-authored claim was too broad | Narrowed in the docstring. Most printed numbers are read at runtime from a named field or counted; **three groups are authored constants transcribed from retained evidence and not parsed**: the E1 literals **24** declared and **2** expected-excluded legs from `selectivity-sensitivity-control-prereg.md` AMENDMENT 1 (`:26–31`) — only the admitted **22** is read, from `selcal-verdict.json` `n_legs_admitted`; the benchmark values quoted inside `CURRENT_SCOPE` prose for `V5`; and the `1/462` figure quoted in `CURRENT_SCOPE` for `V11`. ⭐ The **source/manifest binding is retained and not weakened**: every named source is in `INPUTS`, hence hashed with its working-tree SHA-256, git blob id and `bytes_match_head_blob`. ⛔ **No new parser** was written, and the existing author classification table stays labelled an author classification | `extract_mf1_inventory.py` module docstring · main §2 extraction-boundary paragraph | **CLOSED** |

## Limits, stated rather than dissolved

1. ⛔ **A labelled omission is still an omission.** The `V5` result cell is no longer the whole
   field. A reader who wants the field verbatim must go to `instrument-census.json`. That is
   disclosed in two places, but it is a display decision by this author, not a source repair.
2. ⛔ **The source string is unchanged and will regenerate.** `instrument-census.json` is generated
   from `nr4a3-program-map.md` §3.1, which still contains *"~34× the statistical uncertainty"*. Any
   future regeneration reproduces it at the source. Repairing it there is a shared-file change and
   was **not** made here; no patch for it was filed either, because none was authorised.
3. ⚠ **Residue 3's correction is UNAPPLIED.** `SETTLED-IDENTITIES-2026-09-08.md` is parent-owned;
   the exact diff is filed and the parent-owned file is byte-unchanged by this batch.
4. ⛔ **No gate, guard, floor, matcher, pin or test was changed, and none was run.** No preflight,
   no census regeneration, no proof run, no commit, no push. The inherited whole-repository gate
   failures remain failures and remain unadjudicated. **Nothing here is a release, a publication
   clearance or an all-green report.**
5. ⚠ **The stdout omission counter is a disclosure, not an enforcement.** If a future source no
   longer carries the fragment, the run prints `fragment NOT PRESENT in source` and displays the
   field verbatim; it does not fail. No existing check was loosened to make room for it.
6. ⚠ **HEAD moved under this batch.** Other lanes committed while it ran; the extraction bound at
   `b58e0ed897cbc3efc62894518fb7661777c36592`, not at the commit HEAD held when the batch started.
   The manifest records the commit it actually bound to.
7. ⛔ **No new science.** No benchmark, simulation, source retrieval, census regeneration, review or
   measurement was performed. Every number restated above was read from a retained record or from
   the bytes of a named commit.
