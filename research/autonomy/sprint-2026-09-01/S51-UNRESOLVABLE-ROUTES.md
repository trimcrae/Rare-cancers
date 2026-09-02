---
id: DOC-SPRINT-S51-UNRESOLVABLE-ROUTES
title: "S51-UNRESOLVABLE-ROUTES — 208 `serves` join keys point at ids no graph holds, the repair is `null` for 177 of them, and the guard is the durable half"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Verify the unresolvable-`serves.route` census independently, establish what `RT-AUTONOMY` was
  evidently meant to denote and what the honest attribution is, build a guard that refuses a
  dangling join key at both the write path and the commit gate, and mutation-test it. Writes no
  ledger row and adds nothing to `systems/graph`.
scope: >
  research/autonomy/{research-ledger.json (READ ONLY), ledger_schema.py, ledger_io.py, priority.py,
  health.py, out_of_ideas.py} and systems/graph/*.json. Baseline `git rev-parse HEAD` =
  b4cf28c6be8f464fc25e0cee06f6be50eb181138. ⚠ `research-ledger.json` is NOT at HEAD — the driver is writing it — so every
  ledger count below is from the WORKING TREE and is labelled as such; `systems/graph` and
  `priority.py` are byte-identical to HEAD. Every count is reproduced by a command printed beside
  it. The ledger was never written by this seat; the repair is a script the driver runs.
last_verified: 2026-09-02
---

# S51 — a field declared as a join key, joining to nothing, on 208 rows

**Item:** `AUT-094-e71cf460-f664c8c1` (the only ledger row on this defect — see §6).
**Owned paths:** `research/autonomy/ledger_schema.py`,
`research/autonomy/tests/test_a_serves_route_the_graph_lacks_cannot_enter_the_ledger.py`, this file,
and scratch under the session scratchpad. ⛔ `research-ledger.json` was READ and never written.
**Guard ships green?** ⛔ **Not until the driver runs one script.** See §5 — this is the one thing
that must happen outside this seat.

## ⭐ THE CENSUS, REPRODUCED RATHER THAN INHERITED

```
python3 - <<'PY'
import json, collections
routes = {r['id'] for r in json.load(open('systems/graph/routes.json'))}
led = json.load(open('research/autonomy/research-ledger.json'))['entries']
c = collections.Counter(e['serves']['route'] for e in led
                        if isinstance(e.get('serves'), dict) and e['serves'].get('route'))
print(len(led), len(routes), sum(c.values()), len(c),
      {k: v for k, v in c.items() if k not in routes})
PY
```

| quantity | dispatch said | measured | agrees |
|---|---|---|---|
| ledger rows | 361 | **361** | ✅ |
| routes in `systems/graph/routes.json` | 77 | **77** (77 unique ids) | ✅ |
| rows carrying a `serves.route` | — | **336**, 80 distinct ids | — |
| unresolvable route rows | 178 | **178** | ✅ |
| `RT-AUTONOMY` / `RT-LOOP` / `RT-DEGRADER-TERNARY` | 176 / 1 / 1 | **176 / 1 / 1** | ✅ |

**No disagreement.** The dispatch's numbers are exactly right.

## ⛔ AND THE SAME DEFECT IS ON A SECOND FIELD, WHICH THE DISPATCH DID NOT COVER

The identical query against `systems/graph/strategies.json` (**13** strategies):

| `serves.strategy` | rows | resolves? |
|---|---|---|
| `ST-RNA` | **26** | no |
| `ST-DEGRADER` | **2** | no |
| `ST-PROCESS` | **1** | no |
| `ST-EVIDENCE` | **1** | no |

**30 of the 155 rows that name a strategy name one the graph does not hold.** ⭐ The third join,
`serves.publication` — 170 rows, 32 distinct ids against `systems/graph/publications.json` — is
**clean, 0 unresolvable**, which is what makes it safe to put under the same guard today.

**Total: 208 dangling join keys across 206 rows** (two rows carry both).

## ★ WHAT THE 176 ROWS ARE, AND WHAT `RT-AUTONOMY` WAS MEANT TO DENOTE

Characterised over all 178 (not a sample of three):

| field | distribution |
|---|---|
| `kind` | `process_defect` **142**, `proposal` 16, `fix` 8, `harden` 6, `process` 2, `fetch` 2, `analysis` 1, `regrade` 1 |
| `_derived` | **0 of 178** — every one is hand-filed |
| id namespace | `AUT-PD` **156**, `AUT-PROP` 19, `AUT-BIX` 2, `AUT-080` 1 |
| `serves.publication` | absent on **157**; `PUB-ASO` 13, `PUB-STRATEGY-ARCH` 7, `PUB-DEGRADER` 1 |
| `state` | `done` 92, `queued` 78, `in_progress` 6, `parked` 1, `blocked` 1 |
| `score` | 157 carry a number, **21 carry none — every one of them closed** (open unscored: 0) |

Reading them (18 sampled in full, plus every row that names a publication): they are **the loop's own
machinery**. A fan-out governance row that read a key the receipts stopped writing; a seat that died
on its first message and was reported working for 2 h 36 m; the commit loop's cost; the reaper
refusing to archive a receiptless successor; `continuity.py` and `priority.py` reading different
fields for the same question. Not one of them moves EMC evidence.

⭐ **`RT-AUTONOMY` IS NOT A MISSPELLING OF ANYTHING. It is a filer saying "no route".** That reading
is not inferred from the prose — it is corroborated in three independent places already in the tree:

1. `priority.route_score_floor`'s own docstring: *"RT-AUTONOMY is not a route in systems/graph, so
   its rows can never inherit"*.
2. `health.py`'s `scores_are_reachable`: *"DO NOT expect this to reach zero soon — most of the
   residue serves RT-AUTONOMY, which is not a route in the graph."*
3. The receipt vocabulary, where the honest value for a loop-upkeep cycle is `route_advanced: "none"`
   and several receipts write `RT-AUTONOMY` in the same slot with a `_route_advanced_why` that says
   *"⛔ HONEST. This is RT-AUTONOMY: it lands a bar on the loop's own queue hygiene and moves no EMC
   evidence."*

**So the honest attribution is `null`, and there is no strategy row it should point at instead.**
`systems/graph/strategies.json` holds 13 strategies, all of them treatment- or dissemination-shaped;
the closest, `ST-DISSEMINATION` ("Methods and publication as an outcome in itself"), carries four
routes — `RT-METHODS-PAPER`, `RT-ENDPOINT-CHOICE`, `RT-FUSION-OUTPUT`, `RT-MODALITY-CENSUS` — and
none of them is the loop's own upkeep. ⛔ Proposing a new `ST-*` row for "the loop maintaining
itself" would be the same manufactured pointer one level up, so it is **not** proposed here.

⭐ **NOTHING IS LOST BY NULLING IT**, and that is checkable rather than asserted: `kind`
(`process_defect` on 142) and the `AUT-PD` / `AUT-PROP` namespaces — documented in
`ledger_schema.ID_PREFIXES` as *"process defects"* and *"proposals"* — already carry everything the
label carried, and the string itself is preserved verbatim in `serves._route_was`.

### ⛔ THE ONE JUDGEMENT THIS SEAT REFUSED TO MAKE

21 of the 178 name a publication. Applying AUT-PD-177's rule mechanically — *remap to the `primary`
route of the publication the row names* — would move 13 `PUB-ASO` rows to `RT-ASO` and 1
`PUB-DEGRADER` row to `RT-DEGRADER`. **That is a judgement, not a determination, and the two id
classes differ in intent:** `RT-ASO-JUNCTION` was a filer *trying to name the ASO route and getting
the id wrong*; `RT-AUTONOMY` is a filer *deliberately saying "not a route"*. Re-pointing the second
at `RT-ASO` changes what the filer said rather than repairing a broken pointer — and six of those
rows are unscored, so it would hand them a route floor on this seat's judgement. **Left open and
named**, not decided silently. (`PUB-STRATEGY-ARCH`, on 7 more, has **no `primary` route at all**, so
the rule yields nothing for it either way.)

## ⛔ THE OTHER TWO IDS, AND THE PROOF THAT REPAIRING WITHOUT GUARDING DOES NOT HOLD

`RT-LOOP` (1 row, `AUT-PROP-027`, the worktree-in/branch-out contract) is the same shape as
`RT-AUTONOMY` → `null`.

`RT-DEGRADER-TERNARY` (1 row, `AUT-PD-179`) **is** a misspelling of a real route, and its target was
already adjudicated and committed. `AUT-PD-005` carries, in its own `serves._route_remap_note`:

> AUT-PD-177: `RT-DEGRADER-TERNARY` appears in no route of systems/graph/routes.json (77 routes) …
> Remapped to `RT-DEGRADER`, which the graph determines rather than this cycle choosing: it is the
> `primary` route for the publication these rows name.

★★ **AND THIS IS THE EVIDENCE THAT MAKES THE GUARD THE POINT OF THIS MEMO RATHER THAN THE FIX.**
Read at the repair's own commit:

```
git show 6e093294b:research/autonomy/research-ledger.json | python3 -c "…"
  -> bad at that commit: {'RT-AUTONOMY': 162, 'RT-LOOP': 1}
  -> AUT-PD-179 present at 6e093294b: False
```

**AUT-PD-177 drove `RT-DEGRADER-TERNARY` to ZERO on 2026-08-29. It is back today**, on a row that did
not exist when the repair landed, filed by `INTERACTIVE-2026-08-29-budget` — and `RT-AUTONOMY` grew
**162 → 176 in four days**. Nothing refused either, because nothing was watching. Separately, the
sprint driver wrote `RT-TXN-DEPENDENCY` — a route existing nowhere — into a `serves` block from
memory the same night, and `priority.py` stored it silently. **Three re-introductions of the same
defect after it was fixed once is not a coincidence; it is what an unguarded repair looks like.**

## ★ WHICH READERS ACTUALLY MISBEHAVE — MEASURED, NOT LISTED

S44 established that the route half of these rows' *score* is vestigial. That is correct and it is
**not** the same claim as "harmless everywhere". Each named reader was run against the unrepaired
ledger:

| reader | behaviour on an unresolvable id | verdict |
|---|---|---|
| `priority.route_score_floor(E)` | returns a **77-key** dict built from `_derived` rows; `RT-AUTONOMY` is simply **absent** (`RT-ASO -> 70.0`). No error. | silent no-op — **S44 confirmed** |
| `priority.apply_route_inheritance` | no floor exists, so the row never inherits | silent no-op — **S44 confirmed** |
| `priority.merge`'s `by_route` | `_derived`-filtered; no entry, so no id donation | silent no-op |
| `priority.py` default table | **renders all 176 rows under a column reading `RT-AUTONOMY`** | ⛔ **misleads** — it prints an id that names no route, beside 77 that do |
| `health.py` `by_route` | buckets on `str(route)`, so a bucket labelled `RT-AUTONOMY` appears; the row's VERDICT depends only on the unscored count and is unaffected | payload misleads, verdict fine |
| `priority.py --explain <anything>` | **crashes `KeyError: 'serves'`** — including on `RT-ASO` | ⛔ **broken, and NOT by this defect** (see below) |
| `out_of_ideas.compute_histories` | crashes on this tree at `versions[0].sha` (a dict where an object is expected) before any route is read | **UNMEASURED** |

⛔ **TWO SEPARATE LIVE DEFECTS FOUND WHILE CHECKING, NEITHER FIXED HERE AND NEITHER MINE TO FIX:**

- `priority.py:1636` — `[e for e in entries if e["serves"]["route"] == args.explain]` raises
  `KeyError: 'serves'` for **every** `--explain` invocation, because **2 committed rows carry no
  `serves` key at all**. `priority.py:1591` already predicted this in a comment — *"`serves.route` IS
  THE SAME LINE'S THIRD BARE INDEX … each would have been the NEXT crash the moment the score one was
  fixed alone"* — and the prediction has come true at a different line than the one it guarded.
  ⚠ **This seat's repair does not fix it and must not be read as doing so:** the repair writes
  `route: null` inside an existing `serves` dict; a row with no `serves` key is a different
  population. (`research/autonomy/priority.py` is held by another seat this sprint.)
- `health.py`'s `scores_are_reachable` tells the reader, in its docstring **and** in its red message,
  to *"give its route a row in systems/graph so priority.apply_route_inheritance has a floor to
  inherit"* — **the exact remedy this task refuses.** Proposed correction, not applied (health.py is
  outside this seat's paths): name `null` + `_route_was` as the remedy for a loop-upkeep row, and
  keep "give it a graph row" for a row that really does serve a route the graph has not enumerated.

## ★★ THE GUARD — WHERE IT LIVES AND WHY NOT `systems_check.py`

**`research/autonomy/ledger_schema.py`**, in a new `reference_problems(entry, row_id=None,
graph_dir=None)`, wired into `problems()` (the ledger-wide `--check`) and into `check_write()` (the
write path).

⛔ **`systems/systems_check.py` was read and rejected.** It builds `systems/views/` from
`systems/graph/*.json` and **does not read `research-ledger.json` at all** — `grep -n
"research-ledger" systems/systems_check.py` is empty. Putting a ledger assertion there would create a
second home for a ledger concern (CLAUDE.md §1) and couple the view builder to `research/autonomy/`.

★ **`ledger_schema.py` is where this belongs, and it says so itself.** It is *"THE ONE PLACE THAT
NAMES WHAT A LEDGER ENTRY MAY CALL ITS FIELDS"*; its `GOVERNED_SUBFIELDS` already **documents**
`serves.route` as *"priority.py's join to systems/graph/routes.json"*; and its own "WHAT THIS CANNOT
CATCH" §4 already **named this exact gap** — *"A WRONG VALUE UNDER A RIGHT NAME, in general"*. This
change turns that documented join into a checked one, which is the difference CLAUDE.md §6 records as
**"RECORDED IS NOT ENFORCED"**. It is also the only module bound at **both** ends: `ledger_io.write_ledger`
calls `check_write` (*"the one place a programmatic writer cannot get past"* — the door
`RT-TXN-DEPENDENCY` walked through), and `research/autonomy/tests/` is in the **default preflight
tier (gate 13)**, so a hand edit is caught at the commit.

**What it asserts, per row:** each of `serves.route`, `serves.publication`, `serves.strategy`, when
present and non-empty, is a string naming an `id` in `systems/graph/{routes,publications,strategies}.json`.

**What it deliberately does not assert:** that any particular row *has* a route. `None` and `""` pass
— 25 committed rows serve no route and "this row serves no route" is an honest statement, which is
also exactly what the repair writes. Flagging absence would make the guard's own remedy inadmissible.

**Fails closed.** An unreadable or malformed graph file is reported as a problem, never treated as
"no constraint" (CLAUDE.md §4: an absent reading is not a reading of absence). Cached on
`(mtime_ns, size)` because `check_write` runs on every ledger write, and keyed on the stat rather
than the path so a rewritten graph is re-read — a cache in a gate that goes stale is a gate that has
stopped measuring the tree it judges.

## ⛔⛔ (a) OR (b): THE 178 ROWS ARE FIXED, THERE IS NO GRANDFATHER LIST

**Option (a), and the argument is that the honest attribution really is `null`.** A grandfather list
of 178 ids would be a permanent tripwire that has to be maintained, read and eventually trusted —
and it would encode, forever, that `RT-AUTONOMY` is an acceptable value of a field whose declared
meaning is "a key into routes.json". A dated list is still a list; the same is true of a "sentinel"
registered in the schema, which is only a 3-entry grandfather list wearing a better name.

**And the decisive evidence is that the repair costs nothing measurable.** On a full scratch copy,
`priority.py --write` was run on the unrepaired ledger and on the repaired one and every row compared:

| | before | after |
|---|---|---|
| rows | 361 | 361 (same ids) |
| **rows whose `score` changed** | — | **0** |
| `n_unscored` | 23 | **23** |
| `n_unscored_open` | 0 | **0** |
| `n_clamped` | 12 | **12** |
| `n_by_state` | — | identical |
| fields that differ | — | **`serves` on 206 rows, and nothing else** |
| unresolvable route / strategy refs | 178 / 30 | **0 / 0** |

**Zero score changes, zero ratchet movement.** `MAX_UNSCORED_OPEN` and
`test_the_ratchet_is_not_vacuous` are untouched, so — unlike AUT-PD-177, which had to re-pin a
ceiling downward in the same commit — this repair needs no bar moved in either direction. That is a
measurement, not a prediction: all 21 unscored rows in the population are closed, and
`apply_route_inheritance` could never have fired on them anyway because `RT-AUTONOMY` has no floor.

## ★ THE MUTATION TABLE — 13 TRIED, 13 BEHAVED

Each mutation is applied to a fresh copy of the **repaired** (green) tree; the suite is then run.

| # | mutation | expected | result |
|---|---|---|---|
| M1 | checker: `if value not in known:` → `if False:` | caught | ✅ 6 failed |
| M2 | wiring: `reference_problems` dropped from `problems()` | caught | ✅ 1 failed |
| M3 | wiring: `reference_problems` dropped from `check_write()` | caught | ✅ 1 failed |
| M4 | fail-open: unreadable graph skipped instead of reported | caught | ✅ 1 failed |
| M5 | cache: a rewritten graph file served stale | caught | ✅ 1 failed |
| M6 | type check: a non-string join key falls through | caught | ✅ 1 failed |
| M7 | scope: the `strategy` join quietly dropped from `SERVES_JOINS` | caught | ✅ 2 failed |
| M8 | message: the refused remedy no longer named | caught | ✅ 3 failed |
| M9 | ledger: a NEW invented route id (`RT-TXN-DEPENDENCY`, the incident replayed) | caught | ✅ 1 failed |
| M10 | ledger: a NEW invented strategy id (`ST-BOGUS`) | caught | ✅ 1 failed |
| M11 | ledger: a NEW invented publication id (`PUB-BOGUS`) | caught | ✅ 1 failed |
| **M12** | **CONTROL — a different REAL route id (`RT-METHODS-PAPER`)** | **not caught** | ✅ 16 passed |
| **M13** | **CONTROL — `serves.route` set to `null` (the repair's own shape)** | **not caught** | ✅ 16 passed |

⭐ **M2–M8 are the ones that matter.** A suite whose only assertion is "the committed file is clean"
passes equally well for a checker that has been switched off — the vacuous-guard failure
`ledger_schema`'s own suite already names. M12 and M13 are the false-positive controls: the guard
must stay silent on a good id and on the value the repair writes, or it would refuse its own fix.
Harness: `…/scratchpad/sprint/mutate.py`.

## ⛔ WHAT THE DRIVER MUST RUN — THE GUARD IS RED UNTIL THIS HAPPENS

`research-ledger.json` is being written continuously by the driver, so this seat did not touch it.

```
python3 /tmp/claude-0/-home-user-Rare-cancers/e71cf460-51bb-5657-a314-50a7b993acba/scratchpad/sprint/fix_serves_route.py \
        --repo /home/user/Rare-cancers --write
python3 research/autonomy/priority.py --write        # same edit, before committing
```

Dry run first without `--write` (it reports and changes nothing). Measured output:

```
   176 row(s)  serves.route: RT-AUTONOMY -> None
    26 row(s)  serves.strategy: ST-RNA -> ST-NUCLEIC-ACID
     2 row(s)  serves.strategy: ST-DEGRADER -> ST-PROXIMITY
     1 row(s)  serves.route: RT-LOOP -> None
     1 row(s)  serves.strategy: ST-PROCESS -> None
     1 row(s)  serves.route: RT-DEGRADER-TERNARY -> RT-DEGRADER
     1 row(s)  serves.strategy: ST-EVIDENCE -> ST-REPURPOSING
   208 change(s), 0 refusal(s)
```

★ **Every target is READ FROM THE GRAPH, never typed.** The strategy targets are each the `strategy`
field of the row's own route (`RT-ASO -> ST-NUCLEIC-ACID`, `RT-DEGRADER -> ST-PROXIMITY`,
`RT-PARTNER-STRAT -> ST-REPURPOSING`); `RT-DEGRADER` is recomputed as the unique `role: primary`
route for the row's own `serves.publication` and the script **refuses** rather than guessing if no
such route exists. The shape written is AUT-PD-177's committed convention — `serves.<field>: null`
or the real id, plus `serves._<field>_was` and `serves._<field>_remap_note`; `_strategy_was` and
`_strategy_remap_note` are registered in `ledger_schema.DESCRIPTIVE_SUBFIELDS` in the same change.

⚠ **ORDERING MATTERS AND IT IS A REAL TRAP.** Once `ledger_schema.py` lands, `check_write` refuses
any write while the 208 rows are unrepaired — so **the fix script must run before the next
`priority.py --write`, in the same edit as the guard.** The script itself calls
`ledger_schema.check_write` explicitly on the repaired document before writing, so it proves the
repair is complete or it writes nothing.

**Verified on a copy:** with the repair applied, `ledger_schema.py --check` prints
`361 row(s), 44 governed field name(s), 3 graph join(s), 0 problem(s)` and the new suite is
**16 passed**. Against the live unrepaired ledger it is **15 passed, 1 failed** — the one failure
being `test_every_serves_join_in_the_committed_ledger_resolves`, by design.

## ⛔⛔ A CORRECTION TO THE MID-TASK BRIEF, AND IT IS THE SAME CLASS OF ERROR IT WARNED ABOUT

The coordinator sent a mid-task message quoting `AUT-PD-194` as a pre-existing ledger row describing
this defect, asking that it be read before designing anything. **It is not one, and the quoted text
is this seat's own guard output.**

- **`AUT-PD-194`'s actual subject** (read from the committed ledger, `state: done`, filed by
  `CYC-0090-d7df5340`): *"⛔ `dev-setup.sh` INSTALLS `libreoffice-writer` WITHOUT AN `apt-get update`
  FIRST, SO A STALE CONTAINER INDEX MAKES THE .docx CHAIN FAIL"*. Nothing to do with routes. It
  appears here only because it is one of the 176 rows carrying `serves.route: RT-AUTONOMY`.
- **The quoted paragraph is `ledger_schema.reference_problems`' refusal message**, written by this
  seat roughly fifteen minutes before the brief arrived, prefixed with `AUT-PD-194:` because that is
  the `rid` the checker names. Proof: `git grep "health.by_route, out_of_ideas" HEAD` returns
  **nothing**, the string exists only in the working tree's `ledger_schema.py:495`, and
  `git diff --stat HEAD -- research/autonomy/ledger_schema.py` shows it among 133 uncommitted
  insertions.
- **`continuity.py` cannot have printed it**: `grep -n "ledger_schema" research/autonomy/continuity.py`
  is empty.
- **The remap convention in the brief is nonetheless real and was already in use here** — it comes
  from `AUT-PD-177`'s 18 committed `_route_was` / `_route_remap_note` blocks, which this seat read
  before writing the script and which the script follows. The brief was right about the convention
  and wrong about where it was quoted from.

★ **Which row survives:** `AUT-094-e71cf460-f664c8c1`, and it is not a duplicate of anything —
it is the **only** ledger row on this defect. `AUT-PD-194` must keep its own `dev-setup.sh` subject.
**Nothing to merge.** What `AUT-094` should gain: the strategy half (30 rows, 4 ids), the
zero-score-change measurement, the AUT-PD-177 re-introduction evidence, and the two live defects in
§4 that belong to other rows.

⚠ **This is worth recording rather than smoothing over**, because it is the fourth instance tonight
of the same failure and this memo exists because of the first three: an identifier read from a
display surface instead of from the file it names. CLAUDE.md §7 — *never write an identifier from
recollection* — extends to **never read one from a rendered message without opening the file behind
it**. A checker's output is prefixed with the id it is complaining about, which makes it look exactly
like that row's content.

## UNMEASURED

- **Whether the 13 `PUB-ASO` and 1 `PUB-DEGRADER` rows should be re-attributed to `RT-ASO` /
  `RT-DEGRADER` rather than nulled.** Deliberately not decided (§2). Six are unscored, so the answer
  moves real numbers; it needs a reader of the rows' content, not a rule.
- **`out_of_ideas`' behaviour on an unresolvable id.** `compute_histories` crashes on this tree at
  `out_of_ideas.py:334` (`versions[0].sha` against a dict) before reaching the route, so the reader
  could not be exercised. Not diagnosed — it is a different defect and a different owner.
- **Whether `priority.py --explain` has ever worked since the two `serves`-less rows landed.** The
  crash is reproduced; its introduction commit is not bisected.
- **Whether any other `systems/graph` file is joined to from the ledger under a key not in
  `SERVES_JOINS`.** Only the three `serves` sub-keys were surveyed.

## Reproduction

- Guard: `research/autonomy/ledger_schema.py` — `reference_problems`, `graph_ids`, `SERVES_JOINS`,
  `WHY_GREEN`.
- Suite: `research/autonomy/tests/test_a_serves_route_the_graph_lacks_cannot_enter_the_ledger.py`
  (16 tests; gate 13 runs it in the default preflight tier).
- Repair script (**the driver runs it**):
  `…/scratchpad/sprint/fix_serves_route.py`.
- Mutation harness: `…/scratchpad/sprint/mutate.py`; before/after trees under
  `…/scratchpad/sprint/{base,before,after}`. The live tree was never mutated and
  `research-ledger.json` was never written by this seat.
