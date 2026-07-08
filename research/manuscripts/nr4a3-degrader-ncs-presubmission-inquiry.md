# NCS presubmission inquiry — draft (the free long shot)

> **Purpose.** A *presubmission enquiry* to the Nature Computational Science editor — a short note asking
> whether the work is in scope **before** investing in a full submission. This is a **free long shot**, not
> the plan: the realistic target is **JCIM** (see
> [`nr4a3-degrader-carT-and-family-druggability-framing.md`](./nr4a3-degrader-carT-and-family-druggability-framing.md) §2).
> Send it *because* it costs nothing and the editor's reply (usually within days) settles the question. If the
> reply is anything short of clear interest, submit to JCIM and post the ChemRxiv preprint.
>
> **How to send:** NCS takes presubmission enquiries via the journal's online system / editorial email (check
> nature.com/natcomputsci for the current route). Keep it short. Attach or link the preprint/draft. Fill in
> `[YOUR NAME]`, `[AFFILIATION or "independent researcher"]`, and the preprint link once posted.
>
> **Tone rule:** lead with the *general/methodological* claim (the only thing that gives NCS a reason to
> consider it), and be **candid up front that it is in-silico with no experimental validation** — editors
> value the honesty and it prevents a wasted round. Do not oversell.

---

**Subject:** Presubmission enquiry — a controlled in-silico framework for cryptic-pocket druggability and programmable paralogue-selective degradation of an "undruggable" nuclear-receptor family

Dear Dr. [EDITOR NAME / "Editor"],

I am writing to ask whether the study below is of potential interest to Nature Computational Science before I
prepare a full submission.

**The advance.** The NR4A nuclear receptors (NR4A1/2/3) are textbook "undruggable" orphan transcription
factors. Using an integrated, control-heavy computational workflow, we show that (i) their occluded orthosteric
pocket breathes open into a thermally-populated, druggable cryptic cavity — characterised across **all three
paralogues** with well-tempered metadynamics plus an unbiased release run, calibrated against a
nuclear-receptor panel, and independently corroborated by a cryptic-pocket predictor trained on separate data;
and (ii) because that pocket is the family's most sequence-divergent zone, **one framework is tunable across the
entire selectivity axis**. The methodological core is a **state-matched family selectivity matrix** — running
the same cryptic-pocket dynamics on every paralogue so selectivity is judged opened-vs-opened, removing the
opened-target-vs-static-off-target confound that biases naive selectivity docking — coupled to **built-in null
models** (a decoy-calibrated MM-GBSA selectivity null and multi-snapshot de-noising) that we use to *retract*
our own non-robust calls. From one generative campaign the framework designs both a paralogue-**selective**
NR4A3 degrader (validated to affinity-grade selectivity FEP) for NR4A3-driven cancers and, by re-ranking on the
conserved core, a **pan-NR4A** degrader relevant to reversing CAR-T-cell exhaustion — one computational result
spanning rare oncology and immunotherapy.

**Why I think it may fit NCS.** The contribution is computational and general: a reusable, control-validated
recipe for assessing cryptic-pocket druggability and designing programmable paralogue selectivity against
targets a static structure calls undruggable, with the honest null-model machinery to keep such claims
falsifiable. NR4A is the demonstration.

**Candid scope (so your time isn't wasted).** This is an **entirely in-silico study — no wet-lab validation and
no synthesized molecule**; the load-bearing structural model is a predicted cryptic pocket that an independent
co-folding method could not corroborate, which we report transparently. Every claim is labelled at its
computed weight, and the negative results (a ternary that adds no selectivity; a raw endpoint metric that fails
its decoy control) are reported as such. If NCS would want experimental validation or a broader
multi-target method benchmark for a study of this kind, I would value knowing that now.

The manuscript is complete in draft form and the code/data are openly available. A preprint is at
[PREPRINT_URL] (or available on request). I would be grateful for your view on whether a full submission would
be welcome.

Thank you for your time.

Sincerely,
[YOUR NAME]
[AFFILIATION or "independent researcher"] · [CONTACT]

---

## If the editor declines / is lukewarm
Proceed directly to **JCIM** (cover letter can reuse the "advance" paragraph above, minus the NCS-fit
paragraph), and post the **ChemRxiv preprint** the same day regardless. Optionally send the same enquiry to
**Chemical Science** only if you first build the retrospective known-answer benchmark (§2 of the framing memo)
— without it, Chem Sci is the same stretch as NCS.
