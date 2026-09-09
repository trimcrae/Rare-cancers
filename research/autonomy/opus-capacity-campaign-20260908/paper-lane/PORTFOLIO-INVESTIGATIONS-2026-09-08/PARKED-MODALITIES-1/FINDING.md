---
id: DOC-PORTFOLIO-INVESTIGATION-PARKED-MODALITIES-1
title: "PARKED-MODALITIES-1 — the parked register's reasons audited against their own evidence: one stands, three narrow, one has no locator at all"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: PARKED-MODALITIES-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
target_endpoint: PUB-PARKED-MODALITIES
repo_head: 9a0ee12226deef23fabc72011c64bab9fee18763
---

# PARKED-MODALITIES-1

Worker lane under `SHARED-CONTRACT.md`. **Read-only outside this directory** — proved in
`checks/06`, where both graph files hash byte-identical to `checks/01`. No `git add`, commit, push,
`preflight.sh`, subagent, network request, GPU, paid API, worktree or repo copy. The diff is
**unapplied**.

⛔ **This lane does not un-park anything.** Every one of the five modalities is still parked, none is
recommended for pursuit, and no efficacy, safety, selectivity, therapeutic-window or
clinical-readiness property is asserted or implied anywhere in this finding or its artifacts. Where
a reason weakened, the finding says what changed and stops.

## 1 · The question

`PUB-PARKED-MODALITIES` is a register of five modalities set aside. It has no `document.file` and
has never had a lane, so its reasons have never been audited.

> **For each parked modality, is the recorded reason for parking still true, and is it scoped to
> what was actually checked?**

Answered on committed bytes, offline, at $0.

## 2 · Paper-level merit

A parked register is the one place in a portfolio where nobody checks the work. Its rows are not
results, so no review process touches them; but they are load-bearing, because they decide what is
never looked at again. Two specific things can rot in one: a reason overtaken by later evidence, and
a reason stated as a **global absence** ("nobody has", "the field has not solved") when the evidence
supports only a **bounded** one ("not achieved on the inputs held here"). The second is the
characteristic defect, because a global absence is unfalsifiable in practice while a bounded one has
a named thing that could change.

Patient relevance is indirect and stated as such: EMC has no targeted agent, and which modality
classes stay off the board is decided by exactly these five paragraphs. **Grading the wording of a
register is not a therapeutic claim and nothing here becomes one.**

Reconciled against `research/autonomy/portfolio-2026-09-05/recommendation.md`: none of these five
routes appears in its ranked prospects, which is itself consistent — the memo ranks work that could
be done, and these are the rows that cannot be.

## 3 · The exact evidence gap

**All five routes carry `artifacts: []` and `evidence: []`.** That is a mechanical fact of
`systems/graph/routes.json`, reproduced in `checks/02`. So no parking reason in this register is
connected to an artifact by the graph, and the whole question of "is it still true" has never had a
path to an answer. What exists instead is one level down — `blockers.json`, `technologies.json`,
`instruments.json` — and it is **not the same claim**. That mismatch is the gap, and it is
checkable without any new data.

Distinct from prior work: the eight named sibling lanes (`MONOVALENT-2`, `MONOVALENT-3`,
`DEGRADER-2`, `ANDGATE-2`, `SYNLETH-2`, `PUB-MTAP-PRMT5`, `SURFACE-2`, `MATRIX-ADDRESS-3`) were read
in full before any verdict. **None of them audits a parked route**, and none bears on a parked
route's blocker — see §6.

## 4 · The step taken, and the result

`parked_reason_ledger.py` (stdlib only) walks `routes[].publication.endpoint == PUB-PARKED-MODALITIES`,
pulls every parking-reason field, tests each against the record that **owns** the capability it
appeals to, and re-derives the one load-bearing number in the register. Output:
`parked-modality-derived-inputs.json` (machine-derived) and
`parked-modality-reason-ledger.json` (the adjudicated ledger, one row per modality).

| modality | verdict | the exact artifact that establishes it |
|---|---|---|
| **RT-RIPTAC** | **REASON-STANDS** | `blockers.json` — five inherited blockers of four distinct kinds, incl. `BLK-NOT-FUSION-SELECTIVE` (`fundamental_biological_limit`); `routes.json` `timing.two_year_delta` already refuses the one supersession that could apply |
| **RT-AF3-INTERFACE** | **REASON-NARROWED** | `technologies.json` `TECH-COFOLD-ASSEMBLY.current_state = "partially_landed"`, two named arms, 3 ungraded signals (newest `2026-09-04`) |
| **RT-GLUE** | **REASON-NARROWED** | `technologies.json` `TECH-GLUE-DESIGN.current_state = "early_signals"`, `confidence: moderate`, **5** `pending_signals` all `graded: false` |
| **RT-CRISPR-CAS13** | **REASON-NARROWED** | `blockers.json` `BLK-VECTOR-DELIVERY` has **no `evidence` field**; `technologies.json` `TECH-VECTOR-DELIVERY` states the bounded form at `confidence: moderate` |
| **RT-RIBOZYME** | **REASON-UNEVIDENCED** (gate 2) | `routes.json` (`artifacts []`, `evidence []`, `blockers_inherited` = `[BLK-VECTOR-DELIVERY]` only) + owner memo `emc-post-degrader-options.md:959-961`, uncited |
| *endpoint* **PUB-PARKED-MODALITIES** | **REASON-NARROWED** | `technologies.json` — 2 of the 4 owning records are not `absent` |

**REASON-SUPERSEDED is empty.** That is a real negative and is preserved as one (§6).

### 4.1 · The headline

The endpoint says, twice, that every route is parked on **"a technology nobody has"** / **"a
capability nobody has."** By the graph's own owning records that universal is false as written:
`TECH-COFOLD-ASSEMBLY` is `partially_landed` and `TECH-GLUE-DESIGN` is `early_signals`; only
`TECH-VECTOR-DELIVERY` and `TECH-FE-CRYPTIC-POCKET` are `absent`. **The bounded true statement is
that the specific ARM each route needs has not landed** — which is a stronger register, not a weaker
one, because an arm is a thing a scan can watch for.

### 4.2 · The sharpest row — RT-RIBOZYME

The ribozyme route is called, by the endpoint itself, *"the one row gated twice over… and the reason
two gates is a different situation from one."* Gate 1 is vector delivery. **Gate 2 — "a technique
with no modern solid-tumour clinical footing", "largely a 2000s-era approach" — has no locator
anywhere in this repository.** Not in the route (`artifacts []`, `evidence []`), not in a blocker
(only `BLK-VECTOR-DELIVERY` is inherited, and it covers gate 1), not in a technology record, not in
any `TR-`/`TRG-` scan trigger, and not as a citation in the owner memo that first asserted it —
`research/manuscripts/program/emc-post-degrader-options.md:959-961` states it bare, in a paragraph
whose neighbouring route claims (routes 11, 14) *do* carry links. It is also the only clause in the
register with **no watch at all**: if it became false, nothing would notice.

**UNEVIDENCED IS NOT FALSE.** This lane does not claim trans-splicing ribozymes have modern footing,
and gate 1 keeps the route parked on its own. The finding is that the register cannot show its work
for the clause that carries its "twice over" distinction, and so may not lean on it.

### 4.3 · Number re-derivation — the one quantity in the register

`RT-AF3-INTERFACE`'s reason rests on *"the one tested here failed badly."* Its only quantitative
form is `instrument-census.json`: *"DockQ 0.023–0.046 ≈ true structure moved 32 Å."*
Re-derived from `research/modalities/selcal-dockq-decoy-scale.json`:
`cofold_DockQ_range = [0.0228, 0.0459]`; the first ladder rung whose **median** DockQ falls at or
below 0.0459 is **32.0 Å** (median 0.0255). **It reproduces exactly.**

**But the ladder is a doubling series** (0 / 0.5 / 1 / 2 / 4 / 8 / 16 / 32 Å), and the 16 Å rung has
median 0.0848 > 0.0459. So the matching displacement lies in the **open interval (16, 32] Å**.
"32 Å" is the **coarsest matching rung, not an estimated displacement**, and no interpolation or
uncertainty is published beside it. The route's failure claim survives; the bracket is the honest
form of the number and is recorded in the ledger.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `parked-modality-reason-ledger.json` (5 route rows + 1 endpoint row: recorded reason
  verbatim, evidence locator, verdict, establishing artifact, park disposition);
  `parked-modality-derived-inputs.json` (machine-derived, with input SHA-256s);
  `parked_reason_ledger.py`; `UNAPPLIED-parked-reason-scope.patch`.
* **Validation / baseline** — the *baseline* is each capability's **owning record**, not this lane's
  judgement: a route's reason is graded against `technologies.json` / `blockers.json` /
  `instruments.json`, which are the records the graph itself designates as owning those claims. The
  global-absence screen is mechanical (a fixed marker list applied to a fixed set of prose fields)
  and its per-route hit counts are printed in `checks/02` — `RT-RIPTAC` scores 0, which is why it is
  the control that passes. The one number in the register was re-derived from its underlying ladder.
* **Provenance** — repo HEAD `9a0ee12226deef23fabc72011c64bab9fee18763`; input SHA-256s recorded in
  `checks/01` **and independently re-recorded inside** `parked-modality-derived-inputs.json`;
  `checks/06` proves both graph files unchanged after the diff was built. Offline throughout: no
  HTTP request was issued from this lane, no PubMed/PMC MCP call was made, no closed route
  (B1/B2, B4, B8, B9) was touched, retried, proxied around or relabelled, and R1–R4 were not
  restarted.
* **Limitations.**
  1. **This is an audit of RECORDS, not of the world.** It establishes what this repository can and
     cannot show for each parking reason. It does **not** establish whether any capability has in
     fact landed, and no literature retrieval was performed to find out.
  2. The five routes' `artifacts[]`/`evidence[]` being empty means every locator here was
     **reconstructed** by following `blockers_inherited`, `instruments.disclosed_failing` and
     `technologies[].unblocks.routes`. A locator the graph does not encode may exist in prose I did
     not read; absence of a locator is reported as such, not as absence of evidence.
  3. `pending_signals` were counted, **not read or graded**. Grading them is a scan-owner act and is
     not this lane's to do. Five ungraded glue signals and three ungraded co-fold signals are
     **eight UNKNOWNS**, and are recorded as unknowns.
  4. The `(16, 32] Å` bracket is read off a published doubling ladder. No decoy was regenerated, no
     DockQ was recomputed, and no finer ladder was run.
  5. `RT-RIPTAC`'s `readiness.missing[0]` ("paralogue selectivity") is broader than the blocker it
     inherits, and **no diff is proposed for it** — the adjacent field already scopes it correctly.
     That is a judgement call and is flagged rather than acted on.
* **Stop condition — reached.** The ledger covers every route the endpoint reaches (5 of 5, count
  verified mechanically), each row has a verdict and a named establishing artifact, the register's
  single number is re-derived, and the diff proves clean. **Stop here.** The next credible
  independent step is not this lane's: a dated, closed literature retrieval — query, index, date,
  total hits — for the RT-RIBOZYME gate-2 clause, by the admitted PubMed/PMC route, in the
  `ANDGATE-2` provenance form. It was **not** attempted here because a null result without that
  closure discipline would reproduce the exact defect this lane is reporting.

## 6 · The negative that must be preserved: nothing was superseded

The task named eight sibling lanes to read before judging. All were read. **None supersedes a
parking reason, and the REASON-SUPERSEDED column is empty.** Their subjects — the covalent corridor
under experimental NR4A2 chains and a clash sweep (`MONOVALENT-2`, `-3`), per-frame RSA overlap
(`DEGRADER-2`), condensate concentration for `C_E` (`ANDGATE-2`), screen denominators
(`SYNLETH-2`), within-series FET class transfer (`PUB-MTAP-PRMT5`), derived-flag consistency
(`SURFACE-2`), probe-core labelling (`MATRIX-ADDRESS-3`) — all attach to routes that are **not**
parked.

The near miss is worth naming and refusing. `DEGRADER-2` and `MONOVALENT-2/-3` **do** supply
paralogue-discrimination measurements that never pass through a free-energy engine, and
`RT-RIPTAC` is parked partly on "the selectivity the program cannot measure". They are **not** a
supersession: both are covalent/geometric axes belonging to a warhead-bearing architecture, and the
RIPTAC as recorded has no such axis. **Reading them across would be relabelling, which is exactly
what this lane is forbidden to do.** `RT-RIPTAC` is therefore graded REASON-STANDS.

What the campaign *did* contribute is not a result but two rules, and both are used above:

* **A precedent** — `PUB-TCIP` (`publications.json`, corrections dated 2026-09-08 / 2026-09-09):
  *"the two retained literature indexes have no query, page or total-hit closure and cannot
  establish an absence in the field."* That is the same defect as `RT-GLUE`'s "nobody has shown it"
  and `RT-CRISPR-CAS13`'s "the field has not solved", on a different route.
* **A template** — `ANDGATE-2`'s admissible wording for a null: *"not measured anywhere in the
  **retrieved** public record"*, with the retrieval route named and per-source provenance filed
  beside it.

## 7 · The diff — `UNAPPLIED-parked-reason-scope.patch`

**Six string edits across two shared canonical files.** Prepared, proved and **not applied**; the
parent alone records shared state.

| file | field | change |
|---|---|---|
| `publications.json` | `PUB-PARKED-MODALITIES.why_not_written` | narrow "a technology nobody has" to the per-route arm; dated correction |
| `publications.json` | `PUB-PARKED-MODALITIES.outcome_potential_why` | same, short form |
| `routes.json` | `RT-AF3-INTERFACE.readiness.why_not_higher` | narrow "nothing to report until…" to the sequence-and-ligand-only arm |
| `routes.json` | `RT-GLUE.remaining_unknowns[1]` | narrow "nobody has shown it" to this repository's scan record |
| `routes.json` | `RT-CRISPR-CAS13.readiness.why_not_higher` | quote `TECH-VECTOR-DELIVERY`'s bounded form instead of escalating to "the field" |
| `routes.json` | `RT-RIBOZYME.remaining_unknowns[1]` | flag gate 2 UNEVIDENCED; **clause retained verbatim, not withdrawn** |

Every replacement **preserves the superseded wording verbatim** inside a dated
`⚠ NARROWED 2026-09-09 (PARKED-MODALITIES-1) … SUPERSEDED, RETAINED: "…"` correction, in this
repository's established form. Every replacement also **restates that the route stays parked**, so
the correction cannot be read as an un-parking. No guard, floor, gate, matcher, pin or test is
touched; no blocker, trigger, technology state or `blocked_by` edge is changed; both files remain
valid JSON with unchanged element counts (asserted in the build script, `checks/04`).

**Proof:** `git apply --check` → **exit 0** (`checks/05`, real exit code, no pipe).
The build's own `git diff --no-index` exit 1 is preserved in `checks/04` — 1 means *differences
present*, which is the expected value for that command.

## 8 · Checks

| dir | what | exit |
|---|---|---|
| `checks/01-repo-state` | HEAD, clean status, input SHA-256 of all 7 read artifacts | 0 |
| `checks/02-derive-ledger-inputs` | ledger derivation + the (16, 32] Å re-derivation | 0 |
| `checks/03-build-diff-FAILED-relative-path` | **failed attempt, preserved** — a subshell `cd` made the lane-relative redirects unresolvable | 1 |
| `checks/04-build-diff` | patch generated with absolute paths | 1 *(differences present — expected)* |
| `checks/05-normalise-and-apply-check` | header normalisation + `git apply --check --verbose` | **0** |
| `checks/06-tree-untouched` | both graph files hash-identical to `checks/01`; nothing outside the lane modified | 0 |
