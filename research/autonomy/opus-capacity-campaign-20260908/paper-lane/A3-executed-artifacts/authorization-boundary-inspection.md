# A3 — authorization-blocker inspection (read-only; no gate touched, weakened or tested)

Coordinator correction 2: an old graph row recording an AUTHORIZATION blocker is not itself the
current permission boundary. Both `kind: requires_authorization` rows in
`systems/graph/blockers.json` were inspected against their recorded reason and their actual enforcer.

## BLK-SELECTIVITY-CONTROL-UNAUTHORIZED — NOT STALE. The record matches a live, fail-closed enforcer.

* `owner`: `research/manuscripts/nr4a3-program-map.md#31--the-instrument-table` (a document, not a person).
  The retiring act is trimcrae's alone.
* Recorded reason: *"The decision was TAKEN on 2026-09-02 and it was NO"* — a **category** ban on GPU work
  by this automation, explicitly not a budget, so no price and no ceiling clears it.
* Actual enforcer, read: `research/autonomy/autonomy-state.json -> gpu_spend_prohibited` with
  `active: True`, `set_utc: 2026-09-02T16:35:00Z`, `set_by: "trimcrae, 2026-09-02, in session"`,
  `scope: "every GPU rental, fleet, fan-out and dispatch made by this automation, at any price,
  including $0 free-credit lanes and including a resume of a previously started run"`.
* `research/autonomy/gpu_ban.py` is the enforcement half and fails closed on a missing file, an
  unparseable file, a missing block, or a non-boolean `active`; `active: false` read out of a real file
  is the only permitting state.
* **Verdict: the row still describes the standing authorization and names the actual enforcer correctly.**
  It is not a stale record of a boundary that has changed. Its own text also records that the last time
  a cycle re-derived the price and reasoned from the CLAUDE.md dollar ceiling, it reached a buy decision
  that trimcrae interrupted. The recorded correct next action on this row is **NONE**, and A3 takes none.
* Consequence for the ranking: **ST-PROXIMITY's `next` is genuinely unmet and its missing condition is a
  human authorization that has been asked and answered NO.** Named as the missing condition; stopped there.

## BLK-REGISTRY-DUA — NOT STALE, and it is not the binding gate on anything shortlisted.

* `owner`: `systems/graph/blockers.json` itself; retiring act is *"An action only trimcrae can take:
  register for SEER research data and sign the agreement."*
* The row carries its own prior-question warning: whether an ICD-O-3 9231/3 SEER cohort is an EMC cohort
  at all is unsettled (`research/modalities/emc-care-delivery-evidence.json -> icd_o_9231_3`: two
  published SEER studies read that one morphology code as two mutually incompatible diseases), so access
  bought first buys a contaminated denominator.
* It gates `PUB-EMC-CLASSIFICATION` (state `drafted`), and CLOSED-WORK.md records that the user
  **rejected** the registry ICD-O classification paper. So this authorization is not a live route either
  way. No approval is sought and none is needed for anything A3 recommends.

## Nothing was excluded by an NR4A label

Per the correction: no strategy in A3's table is excluded because "NR4A" appears in it. `ST-PROXIMITY`
and `ST-OCCUPANCY` are the two NR4A3-centred families and both were adjudicated on their own recorded
evidence — `ST-OCCUPANCY`'s `next` as **answered** by `selectivity-requirement-sizing.md` (2026-08-07),
`ST-PROXIMITY`'s as **unmet under a live authorization gate** inspected above. Neither was closed on a
name. The only NR4A-specific holds cited anywhere in this work are the two the coordinator names — the
refused NR4A Perspective review and P6's unauthorized proposed manuscript — and A3 proposes neither.
