---
id: DOC-MF1-HANDOFF-METHODS-RECORD
title: "MF1 · frozen handoff for independent final scientific review of the degrader methods-record"
level: L4
kind: handoff
status: live
purpose: >
  Freeze one handoff for the required independent final scientific review of
  research/manuscripts/methods-record/degrader-methods-failure-record.md — naming the concrete main,
  the dependencies that actually exist, their per-file hashes, the checks actually run with their real
  exit codes, and the limitations that are still unresolved.
scope: >
  L4. Reader-facing presentation only. NO new science was performed, no claim was broadened, no
  threshold was changed, and no unrun or failed evidence was removed. There is no wet lab; degradation
  is experimentally unvalidated and nothing here asserts efficacy, safety, selectivity, a therapeutic
  window or clinical readiness.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# MF1 · frozen handoff for independent final scientific review

Frozen 2026-09-08 by the MF1 existing-paper preparation owner. **One handoff, one main.**

## 1 · The main

`research/manuscripts/methods-record/degrader-methods-failure-record.md`

| | |
|---|---|
| intake, as received | 56,401 bytes · `fb3eb862a81af9aadff59a9ab68d8d4272422a7657816cf483fbf663828a5d3e` |
| intake, as measured 2026-09-08 | 56,401 bytes · `fb3eb862a81af9aadff59a9ab68d8d4272422a7657816cf483fbf663828a5d3e` — **agrees** |
| frozen for review | 46,172 bytes · `a9058b6c40e32549f878347b2d4f8c0ed3f8593320ce417ef29367179a7d0fe2` |

⛔ The manuscript is **uncommitted in the working tree**. This lane does not commit or push; the
parent integrates, and the frozen hash above is the byte state a reviewer must be handed.

## 2 · What this pass did, and did not do

**Removed from the reader-facing manuscript** (internal scaffolding, all preserved verbatim in
[`SETTLED-figure-and-text-presentation.md`](SETTLED-figure-and-text-presentation.md)):

1. The header blockquote's **roadmap-subordination** paragraph, its **§9 figure-bill pointer**, and
   the **"THE FRAMING IS NOT DECIDED HERE"** permission paragraph. Replaced by a four-line
   reader-facing note that keeps the no-typed-figure rule and nothing else.
2. Old **§0 "Status of this document"** — endpoint, route, strategy, registry-blocker and
   cost-to-finish rows. Internal, and stale on its own account.
3. Old **§9 "The figure bill"** — the field-by-field typesetting pull-list.
4. Old **§11 "Venue, and what is explicitly not decided here"** — venue selection, the `P1`/`P6`
   framing question and the submission gate.
5. Two residual internal clauses inside the limitations: the "`RT-METHODS-PAPER.readiness.missing`
   is stale / left for the register's owner" sentence in §9.3 item 1, and "A typesetting pass reads
   each count from its own home" in §9.3 item 2. **The limitations they sat inside are unchanged** —
   see §5 items 6 and 7 below, where the two facts are carried forward rather than dropped.

**Renumbered** so the public text has no gaps: old §10 → §9, old §12 → §10, old §13 → §11. Every
in-document anchor was re-pointed and re-checked (§4).

**Added**: eleven artifacts and one script that the figure bill named but no prose sentence did were
added to the manuscript's provenance list, so removing the bill did not orphan them.

**Preserved exactly as accepted**: the D3 correction (§6(b) — the second method's known-answer arm
returned zero gradeable pairs, with the four recorded dispositions of the twelve listed pairs) and the
D4 correction (§4.3 opening — `selcal-verdict.json`'s own tier word is `NULL`, and the paper reports
that this is a FAILED calibration and not an absent one, without relabelling the artifact). Neither
was touched.

⛔ **Not done, on purpose:** no new science, no V4, no claim broadened, no threshold changed, no
figure created, no evidence hidden.

## 3 · Dependencies that actually exist, with per-file hashes

Every path the frozen manuscript links to, measured on this branch 2026-09-08. All exist; there are
no broken links.

| file | bytes | sha256 |
|---|---:|---|
| `research/manuscripts/methods-record/degrader-methods-failure-record.md` **(main)** | 46172 | `a9058b6c40e32549f878347b2d4f8c0ed3f8593320ce417ef29367179a7d0fe2` |
| `CLAUDE-history.md` | 16024 | `0314e347ae78fe2891e44d33ffbda91df1b23e6d3fa1f2580adb39e4e0a1c405` |
| `research/manuscripts/nr4a3-program-map.md` | 616465 | `e33db25530872819117e1c7281404c7341a3f9570ed05a3536efb1a8324625b8` |
| `research/manuscripts/program/paper-framing-options.md` | 60281 | `3154bdd9facdb93a5a84b53dbff847021380f4320fe9848bb9e2bb28dd017b79` |
| `research/modalities/antitarget-selfcontrol.json` | 81221 | `74c36ff5385706ba549a39bd66a2004d25a30b4d302584384c7fa75035d8899c` |
| `research/modalities/apo-pose-recovery.json` | 382759 | `6f60c5f37949dbf89d6d709656d33b6113519e48802fa335c88a7782b9cfa4dd` |
| `research/modalities/apo-pose-site-in-regime.json` | 377767 | `97cb06e63a4f8709bae1f2f4e731d9106a4fa988e56c285a55ddbecc0f31d372` |
| `research/modalities/categorical-decoy-null-lbd.json` | 154730 | `29c234062776e45cb729b6f6206e28a4a52dd11d30d15b237a40559177cc6b1b` |
| `research/modalities/categorical-decoy-null.json` | 55925 | `e7aa7b9c598d2129cb0f2fe160316d01730e7fd650c5e2779510e3ac5f1c80be` |
| `research/modalities/decoy-null-provenance.json` | 5170 | `3bd0c10cebf42bc248744c30de6a56a7dc3d6b69a610f9cd9f6063a5e5649bb4` |
| `research/modalities/decoy_null_provenance.py` | 7279 | `318ba3b7ef7caed3f1037c6ccf0394a3e7e2f6c84f191913569dded5191a0e1f` |
| `research/modalities/instrument-census.json` | 30336 | `c9eb3bd57b7a13b582ee7ee9a05c55c711ff1fa2a697e58fd764187d4aac08bf` |
| `research/modalities/instrument-census.md` | 21475 | `350b328516e697e1344619c10233c38a0577125162da6c167593f2515252854e` |
| `research/modalities/instrument_census.py` | 17914 | `f3c3bb603dea6e53e858b8828e92662dc34c53dd5c634794e89c14a986a2996b` |
| `research/modalities/nr4a-safety-genetics.json` | 3970 | `9acc806b8bd94f612a983c3819dce721a4d82246076f2f2206656625bdb1c75c` |
| `research/modalities/nr4a2-sparing-bound.json` | 75050 | `c5e732e658200e5732bebb8e89e778016e3daa58826e3749e41cea0efeea8c58` |
| `research/modalities/nr4a3-5aks-reduction.json` | 1696 | `63736eda6ac0c05ea97ad240d9f16388aa9cfffa15484382d6e455fa5babc4a6` |
| `research/modalities/nr4a3-5bt-gate.json` | 48431 | `f4dbee00f2f0f7e903de60446bc4f5d07b2e01bc7cbe30c6e23226fcbf5478ee` |
| `research/modalities/nr4a3-5bt-signature.json` | 73145 | `474f366968b77b30670345694ea46e52a78a585c688b8b6aae0483ba28a20784` |
| `research/modalities/nrv04-cys-conservation.json` | 892 | `ae579ee1d7fec65ed3d572589cdec95becd3f454aaa0fb10ddf40ba8af3df326` |
| `research/modalities/nrv04-retro-secondaries.json` | 76668 | `9a8288ba5122b8ac523b4720bbc816c1d16db83b9a9467bb1e49e4a80f1ce228` |
| `research/modalities/nrv04-retro-verdict.json` | 7797 | `f39714dcea6a9d42e8aab52f75e3c7a16e93d4309cc8c44ad9377c21aa42346c` |
| `research/modalities/pose-conditionality-census.json` | 39770 | `b164fd14404241430f7a87fffdb787c4de5e519ca1f88f83acf41ec43262fbba` |
| `research/modalities/pose-second-method.json` | 92755 | `0e1019ce9a91f061358419bc734bdac62d8b652617fbbdb1a1ea3b8210d09a81` |
| `research/modalities/r3-generation-frame-harmonized.json` | 16921 | `65a08298be77ec09b833e2766d1cd0b5afe70b745733b0c84c5e462c26c29fba` |
| `research/modalities/selcal-cofold-dockq.json` | 25028 | `563940a2cd8d510519cf647b5c69dabc990fcde783cc178a306363a18780f10c` |
| `research/modalities/selcal-cofold-vs-crystal.json` | 41796 | `815614755c549fafa6ad8d38a86ce746856f58e685878adfca8c42fded6c5ad5` |
| `research/modalities/selcal-deepternary-poscontrol.json` | 4874 | `77a641be493be2c2d488b46c796f033cd7b4e94b7e6112d15c99b8509f75d229` |
| `research/modalities/selcal-dockq-decoy-scale.json` | 6935 | `2c4942e049e33a95195e001eca7c246e772e1d3b5fa0802a26f5dde689a2f21c` |
| `research/modalities/selcal-interface-signature.json` | 22259 | `278e0d836f3d4e576e818a5e3e508cb70773886d65033111e475b36181433a65` |
| `research/modalities/selcal-verdict.json` | 8145 | `0faae150a91ba727764971802516e7189137d39dc82168b02b36b93b3da8f92c` |
| `research/modalities/selectivity-resolution-options.md` | 34653 | `619fdd924a1a13771f1ecbdda2750481b746910f2dc2d6f0a0fc50a82a3197fd` |
| `research/modalities/selectivity_calibration.py` | 3893 | `946029ffeadd0098d1b650a75c9cd78c14c9c1f94bf121ed8b2eca625e43ac7f` |
| `research/modalities/step1-fanout-map.json` | 74817 | `6052d5754bad5672e910d6612fb2d883802e705f35c449f2922d713c50096220` |
| `research/modalities/ternary-env-parity.json` | 1002 | `daea6c4fdec8d44a17feee0504b232454637bdae1bdc83e185a9de810b55c0a4` |
| `research/modalities/valb-triangle-closure.json` | 18343 | `8c8782f965b9c19a33e6836f73f42946e599d2c4760540d778d93e5a7d0cba8e` |
| `research/modalities/valb-triangle-reduction.json` | 15576 | `8174ccd0f62d6ec00a385d3f6255cce3366098bc89eb1b37c7e549a80543eadf` |
| `systems/graph/publications.json` | 63611 | `0023e64c82fef653ec1a2eda9bc99db17ff632a812cde9e115672785b95e32a2` |
| `systems/graph/routes.json` | 617198 | `17d208e48c7901eeb01c64a16a415bb1f56a6ce729dfd05846c3b5e0e25f3d3b` |
| `systems/views/registers/instruments.md` | 12319 | `d5f539de36e16a49a22a232b703abb49501fd8016aa69da33223c6f35bcac3cc` |
| `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-preparation/SETTLED-figure-and-text-presentation.md` | 15290 | `cc78e4b28ce1b557c451f211e16d51ea3da7c440e55e984a2c5bcda3c8f25f57` |

⚠ `research/manuscripts/methods-record/degrader-methods-failure-record.md` also links the directory
`results/nr4a3-decoy/`, which exists and is not hashed here.

## 4 · Checks actually run, with real exit codes

Scoped to the one file. No preflight, no repository manuscript suite, no CI.

| check | command | EXIT | result |
|---|---|---:|---|
| style | `python3 research/manuscripts/lint_style.py <main>` | **1** | 197 ERROR. ⛔ **Pre-existing and NOT fixed here**: the same linter on the pre-edit copy returns **220 ERROR**, also EXIT=1. Every error is house-style density (bold runs, em-dash density, decorative glyphs), none is a scientific finding |
| claims | `python3 research/manuscripts/lint_claims.py <main>` | **0** | `OK - 1 file(s) clean` |
| readability | `python3 research/manuscripts/lint_readability.py <main>` | **0** | reports long sentences as a SCREEN; no gate, no action taken |
| presentation metrics | `submission_metrics.measure(<main>)` | **0** | before 6154 main_words → after 5665; figures 0, tables 0, display_items 0, references 0 both times |
| anchors and paths | in-file scan of every `](…)` target against the file's own headings and the working tree | **0** | 23 headings, **0** broken anchors, **0** broken relative paths |

⛔ **Not run, and not claimed as passing:** `lint_consistency.py`, `lint_asymmetry.py` and
`lint_submission_residue.py` are repo-wide interfaces that reject a per-file argument — each returned
**EXIT=2, an argparse usage error, not a pass**. Running them means running them repo-wide, which is
outside this lane's scope. `lint_citations` is known to fail repo-wide, pre-existing and untouched
here. No test was deselected or skipped to produce any row above.

## 5 · Unresolved limitations, current and concise

Scientific, and unchanged by this pass:

1. **There is no working positive control for paralogue-selectivity detection.** Three preregistered
   attempts failed differently (wrong-sign cooperativity calibrator; adequately-powered endpoint-MD
   null; covalency-confounded retrospective). The fourth candidate `V4` is **built and staged with no
   result key, never completed and not authorised**. Every paralogue-selectivity statement the program
   can make is therefore an **unvalidated prediction**.
2. **`V16` has no known-answer calibrator at all**, so `S ≈ 0` is reportable as a bound and may not be
   reported as calibrated.
3. **The anti-target panel is unreadable** — `antitarget-selfcontrol.json` grades
   `panel_readable: false`, the attempted repair did not restore it, and the affected clauses are in
   published SI.
4. **The pose comparison grades neither method.** The second method's known-answer arm returned **0 of
   12 gradeable**, in four recorded dispositions (2 excluded by preregistered rule R2b, 6 `UNRUN` on
   an unreadable `dock.prm`, 1 fetch 404, 3 alignment refusals). Nothing was re-run to establish this.
5. **n = 1** — one pipeline, one target family, one author; the audit generalises no further.
6. **The two instrument registers do not share a denominator and must not be summed.** The census
   counts the roadmap's tables; the paper's four/sixteen split counts only what `RT-METHODS-PAPER`
   cites, and the generated register a reader can check holds a larger set again.
7. ⚠ **`RT-METHODS-PAPER.readiness.missing` still names an item that was closed on 2026-08-07** by
   `decoy-null-provenance.json`. The registry field is stale against the artifact. This lane does not
   edit `systems/graph/`, so the correction is **open and owned by the register's owner** — it is
   recorded here rather than inside the public manuscript.
8. ⛔ **No wet lab exists.** Degradation is experimentally unvalidated; nothing in the manuscript or in
   this handoff asserts efficacy, safety, selectivity, a therapeutic window or clinical readiness for
   any molecule or disease.

Process, outside this lane's authority:

9. **The framing choice (`P1` against `P6`) and submission itself are the user's**, not settled here.
   The paragraphs that said so were removed from the public text as internal, and are preserved intact
   in the settled-presentation record. `systems/graph/publications.json` records `PUB-METHODS` as
   aiming at `journal_submission`; the manuscript's own line reads **"Preprint draft — not submitted,
   not posted"**, and no submission is authorised by anything in this handoff.
10. **Nothing is committed.** The main and both records in this directory are working-tree files for
    the parent to integrate.

## 6 · No blocker was hit

No central scientific blocker arose in this pass. The work was reader-facing presentation over
already-accepted records; every scientific limitation above was already in the manuscript or in the
registry and is carried forward visible rather than resolved. **If a reviewer finds that any removal
in §2 took a scientific statement out of the public text, the reopening condition is exactly that:
name the removed sentence, and it is restorable verbatim from §3–§6 of the settled-presentation
record.**
