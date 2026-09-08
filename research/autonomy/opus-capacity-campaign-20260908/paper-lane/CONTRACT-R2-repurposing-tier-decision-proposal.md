# R2 — repurposing tier decision proposal (isolated lane, no shared writes)

## Why this exists

`BLOCKER-repurposing-canonical-draft-identity.md` records that the committed manuscript carries a
**four-valued T0-T3 scale with imatinib at T3** (lines 416, 523), while the 2026-08-10 response
describes a **three-valued scale, imatinib regraded T2, "nothing reaches T3"**, propagated to the
abstract, Table 1, §5, §6 and §2.7. The regrade was **not applied** and must not be applied
unilaterally.

## The question — scientific, not clerical

**Which grading is scientifically justified for imatinib in EMC, on the evidence the paper actually
cites?** The evidence is **one published case report**: a *KIT* exon-11-mutant patient with 3 years of
stable disease, reference [7]. The committed scale defines **T3** as *"prospective or substantial
clinical evidence in EMC"* and **T2** as *"a case-level signal in EMC or in a very"*-close setting
(read the full definitions yourself at lines ~209-212).

⭐ **Assess whether a single case report meets the paper's own T3 definition.** That is a question the
committed text can answer, and it is the heart of the decision.

## Also required — the consequences, made concrete

If the grade changes, what else must change for the paper to stay coherent? Work out and **draft**:
the tier-scale definition, the abstract, Table 1, §5, §6, §2.7, and the firewall rule that admits only
**T3** to the cited clinical registry. ⚠ **Note the interaction:** imatinib is **already in** that
registry (O1 established this, and the manuscript now says so). If imatinib becomes T2, the paper
would assert a rule its own registry entry violates — **surface that tension precisely; do not resolve
it**, and do not touch the registry or the rule.

## Deliverable

Under `/tmp/claude-0/r2-lane/`: a **candidate revision or diff** showing the coherent T2 version, and
a memo giving the **scientifically justified choice with its support** — or, if the evidence does not
settle it, **the exact missing evidence**, stated so someone else can recognise it.

## Acceptance

- A reasoned recommendation: **keep T3**, **regrade to T2**, or **undecidable on committed evidence** —
  with the paper's own definitions quoted as the test.
- A concrete candidate revision in your lane covering every dependent location.
- The registry-rule tension stated and **left unresolved**.
- ⛔ **No unilateral grade change to the shared manuscript, no registry edit, no added reference, and
  no assumption that an external canonical draft exists.**
- This is **not** a repeat of E1, N1 or O1, and **not** a history hunt.

## Bounds — binding

Input revision **fb6f7028a420a7bf383e2974bebf9a18f38f4b6d**. `claude-opus-5` **medium**, saved first-party subscription — **no paid
fallback, no overage, no credits, no GPU**. Deadline **2026-09-09T02:37:19Z**.

⛔ **Do NOT edit the shared manuscript, any clinical or patient-facing artifact, the registry, any
gate, or any committed scientific artifact.** Your proposal lives **entirely in your own lane**.
⛔ You may **not** write, copy, move or restore any file over a shared repository path, for any reason.
Baselines go **out** via `git show HEAD:<path> >`. **No git write** — read-only git only.
⛔ **Do not rerun unchanged gates.** ⛔ No network, source retrieval, denied-route retry, or
`scripts/preflight.sh`. ⛔ No history hunt, no census, no whole-paper re-review, no reopening of a
closed contract.
⛔ **Distinguish a PROPOSED RECONSTRUCTION from a RECOVERED ORIGINAL.** You are not recovering a lost
draft and must never imply you have. Say "proposed" everywhere.
⛔ Leave anything you cannot support **explicitly UNRESOLVED**. An honest unresolved list is part of
the deliverable, not a failure.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, patient datum or measurement. If a request of yours is refused by content policy, stop that
branch, record the refusal verbatim, never route around it.
⛔ **DELETE NOTHING**, including your lane. Record `date -u`, `git rev-parse HEAD`,
`git status --porcelain` at start and end, and confirm you changed nothing shared.

Stop at ~40 tool calls / ~40 minutes.
