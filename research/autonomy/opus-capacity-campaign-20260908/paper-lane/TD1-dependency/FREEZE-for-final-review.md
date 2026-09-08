# TD1 — dependency candidate frozen for ONE final scientific review

**Lane:** TD1, paper lane, OPUS-CAPACITY-CAMPAIGN-20260908. Sole exclusive owner; disjoint from
P-ST, P-CI, P-AB and the two frozen reviews (FP `f44b75588`, MF1 `0b965a127`), neither of which was
touched.
**Frozen:** 2026-09-08T20:22Z (see `checks/00-start-state.txt` and the check files for exact stamps).
**Tree at freeze:** HEAD `2fe53eb679c11b3bc2a398ca80fecbf621c1090f`, working tree dirty with other
lanes' files (listed verbatim in `checks/00-start-state.txt`); none of them is mine. **No commit, no
push, no producer run, no new data, no source retrieval, no network, no shared-graph edit, no
subagent.**

## Main

`research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md`
(PUB-TXN-DEPENDENCY, `DOC-EMC-TXN-PROTEOSTATIC`), edited in place.

| | bytes | sha256 |
|---|---|---|
| intake (as briefed, confirmed) | 17,716 | `4e906de80ae8a807c507882d9c3983f083749d5490da5b1689b1ae0a14bcebbf` |
| frozen for review | 20,924 | `fe316b44d44b7f16cbb62ea7451dd4c3acff1a8cc2edc0dd73932e98649c9398` |

Intake bytes were confirmed as ordinary intake, not as a separate audit. The intake copy is kept at
`BEFORE-emc-transcriptional-proteostatic-dependency.md` (byte-identical to intake) and the whole
change is in `DIFF-TD1-scope-repair.patch`. Per-file hashes: `frozen/HASHES.sha256`.

## What the review is being asked to judge

Whether the paper's reader-facing claims are now coherent across purpose, summary, body, table,
conclusion, falsifiers and limits, **given that no EMC CRISPR observation exists**.

### The contradiction that was resolved

The paper measured expression in 16 EMC tumours and dependency in a sarcoma-line CRISPR panel that
contains **no EMC line** — while its purpose, summary, §2 heading, §4 table and §5 asserted that the
dependency axis *decides* each class, that the transcriptional route *closes completely*, and that an
expression-only reading would have been *wrong*. Cross-sarcoma evidence cannot decide an unmeasured
EMC-specific dependency, so the categorical half was withdrawn.

**Kept, unchanged in substance**
- Every descriptive expression measurement in EMC tumours (all *t*, coverage, significance criterion,
  the repo-curated-list caveat).
- Every non-EMC dependency measurement with its exact panel and uncertainty: 91 screened lines of 176
  catalogued models; CDK7/CDK9 100 % dependent, means −1.85/−1.46, selectivity 0.085/0.017;
  HSP90AA1/HSP90AB1 5.5 %/18.7 %; CDC37 97.8 %; no sarcoma selectivity; the paralogue-redundancy
  caution and the unanswered dual-knockout question.
- The transfer inference — now stated explicitly *as* a conditional wherever it bears on EMC.

**Withdrawn**
- "the dependency axis decid[es] each time" (front-matter purpose).
- "closes completely on dependency" and "the second axis is the one that decides … a confident and
  wrong answer in both cases" (Summary).
- "closed on dependency" (§2 heading), "The route closes here, and it closes on the axis that decides"
  (§2).
- outcome **closed** (§4 table) and "been wrong in both" (§4).
- "The class is closed on selectivity, and no expression or dependency reading can reopen it" (§5).

**Added**
- A Summary paragraph stating that the two axes are not measured in the same place, that no EMC
  dependency was observed, and that nothing here decides, closes or reopens an EMC-specific
  vulnerability.
- §2: the panel-scoped measured statement, then the explicit conditional and "cross-sarcoma evidence
  cannot decide an unmeasured EMC-specific dependency".
- §4 table columns naming where each axis was measured, and an outcome column that is conditional.
- Falsifier F8 (an EMC CRISPR screen departing from the sarcoma panel), F2 rescoped from "this tissue
  class" to "the 91 screened lines".
- Limits: "No claim here decides a dependency in this disease."

### Accepted corrections preserved exactly (not re-litigated)

176 catalogue / 91 scored / repo-curated memberships; no observed EMC CRISPR data; the disputed
identity of the one EMC-labelled line kept separate from the dependency argument (§1 still rests on
`has_crispr_gene_effect = false`, not on the fusion-negative call); the fifteen-query source bound
scoped to what was searched; non-significant readings never converted into decreases (§2 processivity
kinases, §3 HSP70/heat-shock arm both still read as absence of elevation).

### The central contribution that survives, on the actual records

A HOLD was considered and is **not** returned. Removing the disease-specific decision language leaves
a contribution that is scientifically useful and fully supported: (i) the first reported reading of
the transcriptional-CDK and chaperone panels in 16 EMC tumours, with per-platform coverage and the
curated-list caveat; (ii) the measured cross-sarcoma dependency structure of those same genes with the
correct 91-line denominator; (iii) the methodological result — abundance alone would have produced
confidence in both directions, the dependency axis removes that confidence without replacing it with a
decision, and the disease-specific question therefore remains open; and (iv) the named measurement
that would settle each class. The paper's own title — *what a no-wet-lab program can and cannot
establish* — is now what the paper actually does.

## Necessary existing dependencies (read-only, unchanged)

| supplies | file | sha256 |
|---|---|---|
| scored expression panels, *t*, Welch df, per-gene readability | `research/modalities/emc-expression-panels.json` | `123bd05a…f336bd9` |
| per-route grading | `research/modalities/census-route-expression-grading.json` | `5bc3c80c…5e4f07a8` |
| sarcoma CRISPR panel: means, dependent fractions, selectivity, `n_sarcoma`, catalogued models | `research/modalities/depmap-sarcoma-dependency.json` | `d88bed62…8dd27546` |
| the EMC-labelled line carries no CRISPR gene effect | `research/modalities/fet-ddr-axis-scan.json` | `0737bdef…f8079b012` |
| the identity call graded suggestive, not definitive (kept separate) | `research/modalities/hemcss-label-priorart.json` | `fcc3d828…5486a5d7` |
| class definitions and background PMIDs | `research/literature/txn-dependency-class-definitions-2026-08-09.json` | `7b9944c7…c215e389628` |
| clientship search, its fifteen dated queries, §5 PMIDs | `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json` | `4603641f…9bdbbebe` |

Full-length hashes in `frozen/HASHES.sha256`. The prior TD1 claim-by-claim review (D1–D14 verdicts,
already applied to the manuscript before this lane opened) is in
`../TD1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a3ea9067b5836bf10.jsonl`.

## Check ORIGINALS — every attempt retained, real exit codes

Nothing was overwritten; a failed attempt keeps its own file.

| file | what ran | exit |
|---|---|---|
| `checks/00-start-state.txt` | date, HEAD, `git status --porcelain`, intake hash | — |
| `checks/01-preflight-default.txt` | `./scripts/preflight.sh` (normal commit gate) | **1 — FAILED** |
| `checks/02-baseline-producers-without-TD1-edit.txt` | the three failing producers with this manuscript reverted to its committed bytes | **1, 1, 1** |
| `checks/03-producers-after-TD1-edit.txt` | the same three after the edit | **1, 1, 1** |
| `checks/04-lint_claims.txt` | `lint_claims.py <paper>` | 0 |
| `checks/04-lint_changed_prose.txt` | `lint_changed_prose.py <paper>` | 0 |
| `checks/04-lint_consistency.txt` | wrong invocation (takes no path) — **retained as the failure it was** | 2 |
| `checks/04-lint_citations.txt` | wrong invocation — retained | 2 |
| `checks/04-lint_asymmetry.txt` | wrong invocation — retained | 2 |
| `checks/04-lint_style.txt` | `lint_style.py <paper>` | 1 |
| `checks/05-lint_consistency-repo.txt` | correct repo-mode rerun: 0 ERROR across 29 targets | 0 |
| `checks/06-lint_readability.txt` | `lint_readability.py <paper>` (a screen, not a gate) | 0 |
| `checks/07-lint_style-before-after.txt` | style findings by rule, committed bytes vs edited bytes | — |

**Preflight failed, and the failure is not this lane's.** Three generated-file rows are stale —
claim-coverage census, submission packet, archive manifest. `checks/02` shows all three already
failing with this manuscript reverted to its committed bytes, and the claim-coverage drift spans
manuscripts TD1 never touched (care-delivery, degrader, ATR); another lane's modified
`research/manuscripts/claim_coverage.py` and other lanes' in-flight edits are in the same working
tree. TD1's own contribution to that drift is bounded and visible: this paper's census row moves from
51 to 58 sentences and 21 to 22 numeric sentences relative to the committed 30/17 (`checks/02` vs
`checks/03`). **Regenerating `claim-coverage.json`, `SUBMISSION-PACKET.md` and the archive manifest is
the integrator's step once the lanes land — TD1 deliberately did not run those producers**, because
regenerating against this dirty tree would sweep other lanes' unlanded work into a shared artifact.

`lint_style` exits 1 on this paper before and after the edit; the findings are the house glyph/bold
conventions used throughout the document (16→19 glyph, 16→17 bold-midsentence, 3→4 heading-style, all
of the same kinds already present). It is not a preflight gate and the default preflight's style gates
passed.

## Limits of this lane

- No new data, no source retrieval, no CRISPR/model/source retry, no producer, no statistics, no test
  suite, no network. Nothing was re-derived; printed values were left exactly as the prior review had
  verified them against the committed leaves.
- Only prose scope was changed. Every number, PMID, artifact link and falsifier F1–F7 is unchanged
  except F2's panel wording.
- **Nothing in this lane bears on efficacy, safety, selectivity, therapeutic window or clinical
  readiness in EMC or any disease.** There is no wet lab.
- The paper remains untested in any EMC cell; the EMC-specific dependency stays unmeasured and is
  reported as unknown, not as absent.
- No commit, no push. The parent integrates.
