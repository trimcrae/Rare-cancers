---
id: DOC-PORTFOLIO-INVESTIGATION-METHODS-RECORD-1
title: "METHODS-RECORD-1 — do PUB-METHODS's recorded failures still hold, and is each one scoped to what was actually checked?"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: METHODS-RECORD-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
target: PUB-METHODS
---

# METHODS-RECORD-1 — the failure record, re-derived and scope-checked

Worker lane under `SHARED-CONTRACT.md`. **Read-only outside this directory.** No `git add`, commit, push,
`scripts/preflight.sh`, subagent, network, GPU, paid compute, worktree or repo copy. No wet lab.
Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.**

Locators re-hashed at use. `research/manuscripts/methods-record/degrader-methods-failure-record.md`
= `6b38ac4e545c990c0317a52154e8c1e4cebfc4013b6a22ec0e4411faf69f530f` at both read and patch-build;
SI = `2f39caf7ea31179c8120fe243dd428c9ee35398147470161f00dc03f9f4079d6`; repo HEAD at execution
`9a0ee12226deef23fabc72011c64bab9fee18763`, `research/manuscripts/methods-record/` clean.

## 1 · The question

> PUB-METHODS is a **failure record**, so its value is that its negatives are checkable and its scope is
> honest. **Does every recorded failure still hold; is each one scoped to what was actually checked; and
> has any been superseded by later campaign evidence?**

## 2 · Paper-level merit

A negative record's characteristic defect is not a wrong number — it is a **global absence asserted from a
bounded search** ("X does not exist" from "X was not found in the N sources examined"). That defect is
invisible to a normal review, because the sentence reads as modest. It is also the one defect that
silently converts a useful, transferable audit into an unsupportable claim about a field. Checking it costs
nothing, cannot manufacture a positive, and can only sharpen the paper. Patient relevance is **indirect and
stated as such**: this grades the evidentiary standing of a computational program's own record. **No
efficacy, potency, selectivity, safety, therapeutic-window or clinical-readiness claim is made or follows
from anything here**, and none could — this lane is a document and artifact audit.

## 3 · The evidence gap, and how it differs from prior work

PUB-METHODS has **never had a lane**. It has had two rounds of *review* (the accepted MF1 correction batch
and its five R1–R5 residuals), and those rounds already caught the over-scoping defect class in several
places — §9.5's repository-wide absence was narrowed to inspected evidence, §7.3's universal reading was
withdrawn, §8.1's "excludes a design class" was withdrawn. ⛔ **Those batches are CLOSED and were not
reopened here.** What had *not* been done is the complementary check from the other side: take the numbers
the paper prints and **recompute them from the committed artifacts**, and take the paper's absence
sentences and ask which reach further than the evidence behind them. That is this lane, and nothing else.

## 4 · The step taken

Fourteen quantities re-derived from their named committed artifacts before being relied on, five sibling
campaign lanes read for supersession, and every absence sentence in §1, §5.1, §7, §8.2, §9.4, §9.5 and
§10.5–10.6 read against the evidence it cites. Machine-readable output:
**`failure-rederivation-ledger.json`**. Every execution attempt is in `checks/`.

### 4a · Re-derivation — everything checked reproduces, digit for digit

**No discrepancy was found in any quantity re-derived.** The load-bearing case is `V11`: the full
`C(11,6) = 462` permutation was re-enumerated from the stored model means, returning
**mean_A 4.968417, mean_B 4.531100, statistic +0.437317, p = 0.746753, mirror p = 0.255411, floor
1/462 = 0.0021645** — every figure the manuscript prints, recomputed rather than copied
(`checks/01-selcal-rederive`, exit 0). `S = −0.1297` recomputes from the two per-species means and its
`0.3264` from the two replicate SDs; `R = +0.2128` recomputes from `R_ternary − R_binary`; the decoy
**22 of 38** is confirmed by counting positive margins in `margins_desc` (indices 0–21 positive, index 22
= −0.75) in the one archived arm that reproduces the committed constant; the census/route
**22 / 4 + 16 = 20** partition and the `{V2, V18}` difference reproduce exactly; the §9.4 erratum is itself
correct (**17 + 1 = 18**, `trajectory_objects_found = 0` in **both** surveys). Per-quantity detail,
including two checks that were **not** completed (Q10 partial, Q14 unrun), is in the ledger.

### 4b · Scope — one over-scoped consequence found, in the abstract

The absence claims are, with one exception, **already bounded** — and bounded in place, not in a distant
caveat. The exception is §1:

> "A retained object census over two named storage prefixes finds no multi-frame coordinate file, **so the
> corrected-interface readouts cannot be recomputed.**"

The *absence* is scoped ("over two named storage prefixes"); the *consequence* is not. The body scopes the
same conclusion twice — §9.4: "a retrospective one about the surveyed prefixes, not a proof about every
possible external copy of the data", and §10.5 item 4: "from what was retained under the surveyed
prefixes". The abstract is the single place the qualifier is dropped, and the abstract is what gets quoted.

**`scope-abstract-recompute.patch`** brings the abstract to the body's own scope. ⛔ **It is UNAPPLIED**,
proved by `git apply --check` returning **exit code 0** (`checks/07-git-apply-check`,
`checks/08-manuscript-hash-recheck`). ⛔ **It is not a softening.** The negative is untouched: no
trajectory exists in either surveyed prefix, the readouts remain non-recomputable from retained data, and
the two legs that simulated the wrong tether remain unrepairable by any retained data. Only the sentence's
reach is returned to its evidence.

One further sentence is recorded as **borderline with no edit proposed** (§8.2 item 1, "a bench
measurement is the only answer"): read alone it is a claim about all computation, but the same item bounds
it two sentences later and §10.6 restates it scoped. It is listed in the ledger rather than silently
dropped, for the parent to judge.

### 4c · Supersession — nothing is overturned; one failure is strengthened

⛔ **No recorded failure of PUB-METHODS is overturned by DEGRADER-2, PUB-DEGRADER, MONOVALENT-2,
MONOVALENT-3 or ANDGATE-2, and none is overturned on this lane's authority.**

* **PUB-DEGRADER and DEGRADER-2 STRENGTHEN `V17`'s failure.** They report the NR4A1 C551 positive control
  failing in every replica (max RSA 0.091 / 0.133 / 0.120) and, per frame, in every frame
  (0.0907 / 0.1333 / 0.1201) — where the SI records only "demonstrated false negative". A sharper failure
  is the useful direction for a failure record. ⚠ Those figures are **that lane's**, not re-derived here.
* **MONOVALENT-2 and MONOVALENT-3 are orthogonal.** PUB-METHODS cites neither the corridor tally nor
  `C534` anywhere in the main text or SI (verified by grep). Their narrowing of the "34 of 60" attribution
  to a per-chain 20–36 range, and of the cutoff robustness to the two loosest cutoffs, moves no sentence
  in this paper.
* **ANDGATE-2 is orthogonal in content and corroborating in form** — its "`C_E` is not measured anywhere
  in the **retrieved public record**" is exactly the scoping discipline §1 is asked to keep.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `failure-rederivation-ledger.json` (14 re-derivations with recomputed values, 5 scope
  verdicts, 5 supersession verdicts, an explicit unfinished list) and the unapplied
  `scope-abstract-recompute.patch`.
* **Validation.** Independent recomputation, not transcription: the 462-arrangement permutation was
  re-enumerated; `S`, its dispersion, `R` and the 22/38 count were recomputed from primary fields; the
  census, route partition and object counts were recounted from the JSON. `git apply --check` exit 0 on
  the unapplied patch, re-run after re-hashing the target.
* **Provenance.** Every artifact SHA-256 is in the ledger and in `checks/*/stdout.txt`. Manuscript hash
  identical at read and at patch build; tracked tree clean for that directory.
* **Failed attempts, preserved.** The patch took three tries to build: an off-by-one line index
  (`AssertionError`, exit 1, never reached `git`); a hand-written hunk header (`git apply --check`
  exit **128**, "corrupt patch at line 13"); and a difflib call that emitted a multi-line
  replacement as one list element (exit **128**, "corrupt patch at line 9"). ⚠ The first two
  `git` attempts reused `checks/07-git-apply-check/`, so their original bytes were **overwritten**
  by the successful run; they are reconstructed from the session transcript in
  `checks/07-git-apply-check-FAILED-attempt1/` and `-attempt2/`, and each says so in its own
  `command.txt` rather than presenting itself as an original capture.
  `checks/01-rederive-numbers/` is a stub in which nothing was ever run, labelled `NO EXECUTION`.
* **Limitations.** (1) Q14 — the §7.2 6/5/4/1 partition, the 9.853 Å separation and the twelve-pair
  2/6/1/3 disposition tally were **not** recounted; the artifacts are present and committed, so this is an
  **unrun check, not a missing input**, and must not be read as a re-derivation. (2) Q10 — the 7-of-10
  anti-target count was confirmed from the artifact's own text and from `panel_readable = false` on all
  three blocks, not by recounting per-receptor RMSD rows. (3) The 22-row supplementary inventory was read
  only for `V17`. (4) The sibling lanes' numbers are reported as theirs and were not re-derived. (5) This
  is an audit of a document against committed artifacts — it establishes nothing about EMC, degradation,
  binding, safety or any therapeutic window, and computation could not establish those in any case.
* **Stop condition.** Met and stopped: every quantity checked reproduced (so the "report the discrepancy
  and stop" branch did not fire), the scope review reached a single actionable sentence, and the
  supersession question was answered for all five named lanes. The next credible independent work is
  Q14's recount and the remaining 21 supplementary inventory rows — **not** any new measurement, source
  retrieval or re-run, none of which is authorised or needed here.

⛔ **Every failure this lane examined still holds.** That is the expected and useful result, and no
positive outcome was manufactured from any of it.
