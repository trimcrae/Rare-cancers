# O1 — paper-level contract, recorded BEFORE launch

`date -u` **2026-09-08 ~11:02 UTC**. Input revision **1ddce5f95798e8f9b4357bd150a684451878058b**. Same parent/controller and session,
`claude-opus-5` **medium**, existing first-party saved subscription — no paid fallback, no overage, no
credits, no new controller. Deadline **2026-09-09T02:37:19Z**, never extended.

## Paper

`research/manuscripts/repurposing/repurposing-hypotheses.md`, `PUB-REPURPOSING`, **drafted,
unpublished**. Continuing the same paper's strongest ready issue. Not held, not frozen.

## ⭐ The issue — a live FALSE claim, parent-verified

The manuscript states at **lines 420-421**:

> "It is the only candidate flagged as **eligible to graduate into the cited clinical registry,
> pending clinician review**."

**That is false, and the paper's own review response says so.** The response (item 1, under *"One thing
the review did not catch, and it is the more serious half"*) states the sentence *"was false in fact,
not merely inflated by a tier"*, because imatinib **is already in that registry**, and records that
*"§5 Tranche 1 now states that imatinib is not a hypothesis awaiting promotion, and why."*

**Measured by me at the revision above:**
- The false sentence is **still in the manuscript** at lines 420-421.
- `grep -i "awaiting promotion|not a hypothesis"` returns **nothing** — the correction the response
  describes **was never applied**.
- `research/data/emc-clinical-registry.json` **does** list it: `"Imatinib (KIT inhibitor) — only for
  KIT-mutant EMC"`, `"Off-label; single published case (biomarker-restricted)"`, attributed to the
  case report.

So a drafted manuscript asserts that an agent is *awaiting* admission to a patient-facing registry
that **already contains it**. This is a **scientific-accuracy** defect, not hygiene, and it is the
strongest ready issue on this paper.

## Finite acceptance

1. **Replace the false sentence with what is true**, in place: imatinib is **already in** the project's
   cited clinical registry — quote its actual entry terms from
   `research/data/emc-clinical-registry.json` (name, status, biomarker restriction, single-case
   attribution). It is **not** a hypothesis awaiting promotion.
2. **Check every other statement of the same shape.** Lines **272** and **574** carry related registry
   /migration language (*"may migrate into the project's cited clinical registry, and then only after
   clinician review"*). Read them; correct any that is false for imatinib specifically. If a sentence
   is a **general rule** about tiers rather than a claim about imatinib, **leave it** and say so.
3. **⛔ DO NOT resolve the underlying tension.** The project's rule admits only **T3** to the registry,
   and imatinib is graded **T2** and is in it. The response deliberately recorded that tension at its
   home in `METHODOLOGY.md` §5 *"rather than resolved unilaterally here, because relaxing a
   patient-facing"* rule is not this paper's call. **State the tension plainly if it is needed for
   accuracy; do not adjudicate it, do not change any tier, and do not change the admission rule.**
4. **⛔ DO NOT EDIT THE CLINICAL REGISTRY** — `research/data/emc-clinical-registry.json` is out of
   bounds, as is any patient-facing artifact. `CLAUDE.md` §7 requires reading
   `systems/POLICY-evidence.md` before editing the clinical registry; this contract simply forbids the
   edit. You are correcting a **manuscript sentence** to match the registry, never the reverse.
5. **⛔ No new citation, no new reference, no reference-count change.** A count mismatch elsewhere is
   **not** licence to add citations. Use only sources already cited in this manuscript and the
   committed registry file.
6. **No other claim, number or hedge changes.** The class-evidence disclosure, both in-silico
   negatives, the abstract-level labelling and every qualification stay exactly as they are.
7. Gates run and reported with exit codes. ⛔ A tripped gate is a finding to report, never a reason to
   weaken, relax, reorder or edit a gate. ⚠ **`lint_citations` fails repo-wide at exit 1,
   pre-existing** — attribute it and **do not describe all gates as green**.
8. If correcting the sentence would require resolving the tier tension, editing the registry, or
   adding a source, **STOP and report exactly that**. A supported stop is a successful result.

## ⛔ Isolation

**You may not write, copy, move or restore any file over a shared repository path for a baseline,
comparison or test.** Baselines go **out** to `/tmp/claude-0/o1-lane/` via `git show HEAD:<path> >` or
by copying out — never in. Your only repository write is the repurposing manuscript. **No git write** —
read-only git only.

## Out of scope

⛔ No other manuscript, SI, registry, figure or code edit. ⛔ No network, no source retrieval, no paid
API, no GPU, no `scripts/preflight.sh`. ⛔ No reopening of E1 or N1, no DFSP work, no item 44 work, no
census or review-all sweep, no reference-count reconciliation. There is no wet lab: no EMC efficacy,
safety, selectivity or clinical-readiness claim. Invent no fact, source or measurement.

## Retention

Under `/tmp/claude-0/o1-lane/`: pre-edit manuscript, post-edit manuscript, unified diff, and every
gate's stdout **and** stderr with exit code echoed. ⛔ **DELETE NOTHING**, including your own lane.

## Stop conditions

Acceptance 8; the sentence proving already corrected on reading; any step needing a prohibited action;
or **~40 tool calls / ~40 minutes**. Early with a supported result or block is success.
