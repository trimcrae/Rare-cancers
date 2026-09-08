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

---

# S7 RESULT — **UNKNOWN**, on a transport failure. Appended 2026-09-08 06:56 UTC.

Child `a5b01f4c2c97e9e8a`, ran 06:54:37 → 06:55:31 UTC (~54 s, 8 tool calls). Repository untouched: HEAD
identical at its start and end, `git status --porcelain` empty both times, 20 GiB free. Model self-reported
`claude-opus-5`; parent verifies the observed transcript model set below.

## What happened

**No rendering occurred.** Both permitted URL forms for the same open-access record returned zero bytes:

```
{"error_type":"EGRESS_BLOCKED","domain":"pmc.ncbi.nlm.nih.gov","message":"Access to pmc.ncbi.nlm.nih.gov is blocked by the network egress proxy."}
{"error_type":"EGRESS_BLOCKED","domain":"www.ncbi.nlm.nih.gov","message":"Access to www.ncbi.nlm.nih.gov is blocked by the network egress proxy."}
```

The child stopped after the second form: no third attempt, no mirror, no DOI or publisher route, no
authentication, no denied-route retry, no sibling article. **That is the contracted behaviour and it was
followed exactly** — a blocked route is a result, not a problem to route around.

## Verdict: **UNKNOWN**, and the reasoning is the right way round

An unobserved source cannot be MATCHED; and **a transport failure is not evidence that no matched pair
exists**, so it cannot be NOT A PAIR either. The candidate's S6 status is **unchanged** — still the single
UNKNOWN. The child explicitly recorded that S6's second-hand report about this article's Methods contributed
**nothing** to the verdict, which is the correct discipline: expectation is not observation.

⚠ **Missing bytes, labelled:** there is no raw-content artifact because zero bytes were ever returned;
`fetch-attempts.md` records that in place of content. Retained and parent-verified at
`paper-lane/S7-executed-artifacts/` — `fetch-attempts.md` `685ee905…`, `VERDICT.md` `e69af2ab…`,
`sha256sum -c` **OK/OK** in both the source directory and after copying. `/tmp/claude-0/s7-retained/` not deleted.

## ⚠ One claim in the child's report the parent could not corroborate

Its "Next concrete action" asserts the repository "already documents" an Actions-runner escape hatch "for
exactly this NCBI/PMC block." **A parent grep does not support that**: `research/autonomy/OPERATING_PROTOCOL.md`
contains no such documentation (its only "egress"-adjacent line is unrelated), and the sole `EGRESS_BLOCKED`
references in `CLOSED-WORK.md` are the historical trabectedin-PDF note recording that an old proxy outcome is
**not** a publisher refusal or a global absence. Treat the escape-hatch claim as **UNVERIFIED**. It is not
acted on here.

## Disposition

**The synthetic instrument line remains BLOCKED with its reopening input unmet**, exactly as before S7. Nothing
is validated, refuted, admitted or rejected; no paper consequence in either direction; no clinical claim.

**Exact unmet dependency, now sharper than before:** one rendering of PMC8891938's **figures and tables** from a
network path not subject to this session's NCBI egress block. This is a **transport** dependency — the article
is open access and on no closed or held list; nothing here is a paywall, an authentication demand or a
content-policy refusal.

**Not taken, deliberately:** routing the fetch through CI or any runner. That is a new external act, its
documented basis in this repository is unverified (above), and the parent will not manufacture an authorization
for it. It is named as a dependency for whoever holds that authority, not executed.

## Next-candidate assessment — candidate-by-candidate, no global exhaustion claimed

A one-route block is not source absence and not workstream exhaustion. Assessed now, concretely:

| candidate | status | reason |
|---|---|---|
| PMC8891938 figure/table verification | **BLOCKED** | transport only; needs a non-egress-blocked path (above) |
| S6's 13–15 unscreened PMC candidates | **available but low value** | screenable only through a route that strips tables and figures, so every verdict would be UNKNOWN by construction — the same wall S7 just hit, reached more slowly |
| S6's structural observation (per-patient rows only in very small reports) | **not selected** | testing it is another literature census, and its answer changes no decision now open |
| Further synthetic sweeps | **NO-GO, standing** | S5 resolved the merit question against the density finding; transfer is the limit and no sweep touches it |
| S4/S5 successor (point count vs row count) | **NO-GO, standing** | refines a cohort-and-render artifact |
| P1/P2/P3, P4–P6, S1/S3, NR4A/P6, W25 | **closed or held** | unchanged, not revisited |

**No further child is dispatched on this pass.** Every candidate with available inputs is either blocked on
transport or has no useful yield, and the standing instruction forbids filling slots with record audits or new
sweeps. This is a **candidate-specific block with a named dependency**, not a claim that public-data,
clinical-evidence or study-development work is exhausted.

Session, model, subscription, collector, deadline and every hold unchanged; no manuscript, publication,
controller, session or billing change.
