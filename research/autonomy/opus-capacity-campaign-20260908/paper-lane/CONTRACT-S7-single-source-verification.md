# S7 — bounded single-source verification, recorded BEFORE dispatch

Recorded `date -u` = **Tue Sep  8 06:53:29 UTC 2026**. Same session, `claude-opus-5` medium, saved
subscription, no overage, deadline 2026-09-09T02:37:19Z, sole parent collector.

## Why this and not something else

S6 returned **0 matched pairs** and named exactly one decisive open candidate whose verdict turns on a single
observation it could not make: its admitted tool returns narrative text with tables and figures stripped. **A
restriction of one tool is not proof of global source absence** and is not a reason to abandon the question —
so the correct next step is the same question through a capability that can actually render the source.

## Closed/held check, performed by the parent BEFORE dispatch — required and passed

Target: **Fice 2022, PMID 35251555 / PMC8891938**, an EMC case series. Checked against
`CLOSED-WORK.md`: **no match** — the identifier appears nowhere in that file. It is **not** on the denied list
(Pazopanib, Sunitinib 2014, Wagner, CTARC, Trabectedin/RT), is not GSE4303/GSE28866, is not PMID 22592656, and
is not part of the W25 / primary-article / Results / novelty hold, the NR4A Perspective, or any P1–P6 closure.
It is already cited in this repository's own committed literature records (`emc-mortality-probe.json`,
`emc-attribution-probe.json`, `emc-terminal-events.json`), i.e. an ordinary, already-used open-access source.

## Capability

**`WebFetch`, an already-available first-party capability in this session** — used to read an **open-access PMC
article**. This is ordinary public-source reading, **not** an access-control or refusal workaround: no paywall
is circumvented, no authentication is attempted, no denied route is retried. If the fetch fails or is refused,
that is a **result** — recorded verbatim, branch stopped, **no alternative route sought**.

## The one question

Does PMC8891938 print (a) a survival figure, and (b) a per-patient table carrying **follow-up time and vital
status for the same cohort and endpoint**? That decides **MATCHED** or **NOT A PAIR**, applying S6's
matched-versus-adjacent definition with the weaker reading as default.

## Bounds and prohibitions

**Bounded source verification only.** No digitization, no reconstruction, no inversion, no pooling, no
patient-level dataset, no extraction of the data even if a matched table is found — record **that it exists and
what form it takes**, nothing more. No clinical claim. No manuscript, no publication, no paper admission in
either direction — a MATCHED verdict admits no paper, and a NOT A PAIR verdict is not a publishable negative.
One source only; no crawling to siblings, no second candidate, no query re-run. Durable artifacts (raw fetched
content, the exact URL, the verdict record, any failure) to `/tmp/claude-0/s7-retained/`, **verified before any
cleanup and not deleted**; parent copies and commits. ≥10 GiB free. No repository write, no git operation.

## Acceptance and stop

Accepted on a recorded verdict with the observation that produced it — **or** a recorded fetch failure/refusal
with the branch stopped. Either outcome is a complete result. Stop at acceptance or ~15 tool calls.

## What it changes if it lands

A MATCHED verdict supplies **one** figure–truth pair — which, per the standing narrowing, would let the method
be tested **on that pair only** and would validate nothing in general. A NOT A PAIR verdict closes the last
open candidate in S6's scope and leaves the synthetic line blocked with its reopening input still unmet.
