# Anthropic AI for Science — Rare Disease Research Grant (Application Draft)

**Program:** Anthropic AI for Science — rare disease research grants (Track 1).
**Award:** up to **$50,000 in Claude credits** over 6 months (Claude Opus / models approved for biology). *Credits, not cash or GPU compute.*
**Deadline:** **August 2, 2026, 11:59 PM PST.**
**Applicant status:** unaffiliated individual researcher (eligible — no institutional affiliation required; not a resident of any excluded jurisdiction).
**Apply at:** https://www.anthropic.com/news/rare-disease-research-grants

> Framing note: this program targets **rare *genetic* diseases**. Our disease of interest — extraskeletal
> myxoid chondrosarcoma (EMC) — is a rare *cancer* defined by a recurrent genetic driver (the EWSR1::NR4A3
> fusion). We therefore lead with the **genetic mechanism, cross-disease pathway links, and natural-history /
> patient-data** angles, which map directly onto Anthropic's stated example projects, and treat the
> GPU-heavy structural chemistry as translational motivation rather than the core Claude-funded deliverable.

---

## 1. One-paragraph summary

We are building an open, rigorously-cited computational program to accelerate treatment discovery for
**extraskeletal myxoid chondrosarcoma (EMC)** — an ultra-rare sarcoma driven in ~90% of cases by the
**EWSR1::NR4A3** gene fusion — and, through its shared NR4A3/NR4A biology, for a broader family of rare
NR4A-driven conditions. The requested Claude credits would fund three Claude-native workstreams that match
this program's example projects exactly: (1) **proposing and ranking mechanistic links** across rare diseases
that share the NR4A3 gene / nuclear-receptor pathway; (2) **curating and pooling patient-organization and
registry data** into an improved natural-history picture for EMC and related rare sarcomas; and (3)
**building an evaluation suite** that measures how well frontier models handle rare-disease reasoning tasks
(mechanism, literature synthesis, natural-history estimation). All outputs are public and follow strict
medical-integrity rules (every clinical claim cited; synthetic data banner-flagged).

## 2. Why this fits the program's example projects

| Anthropic example project | Our matching workstream |
|---|---|
| *Propose and rank mechanistic links between distinct rare diseases sharing a gene / pathway* | NR4A3/NR4A-family mechanistic map: EMC ↔ other NR4A-driven / nuclear-receptor–pathway rare conditions; ranked, cited hypothesis set. |
| *Curate and summarize patient-organization data to improve natural-history studies* | Structured pooling of rare-cancer registry cohorts (denominator-weighted proportions + Wilson 95% CIs, non-overlapping cohorts only) into a maintained, citation-mapped natural-history resource; patient-facing one-page disease hubs. |
| *Build evaluations that measure how well models handle rare-disease tasks* | An open EMC / rare-cancer eval: mechanism recall, citation-grounded synthesis, natural-history estimation, and refusal-of-fabrication under our medical-integrity standard. |

## 3. What we already have (evidence of a working program)

- An **EMC Open Target & Drug Atlas** (open, cited) assembling target rationale, fusion-vs-wild-type biology,
  anti-target liabilities, and an assay roadmap for future collaborators.
- A **registry-pooling methodology** with a structured citation map (primary vs secondary sources; fixed
  meta-analytic method) — the natural-history backbone.
- An existing, honestly-graded **repurposing / mechanism track** (scored candidate menu, DepMap dependency
  analyses, a graph-foundation-model run, a docking screen) — from which we've *already* identified the
  specific novel, self-executable gaps the credits would fill (a never-published CMap/LINCS analysis;
  fusion-subtype stratification; evidence-class verification of weak expression-only hooks).
- A **computational NR4A3-degrader / method-development program** (structural modeling, RBFE/FEP,
  ternary-complex ensemble modeling, paralogue counter-screening) — the translational driver the above biology
  supports.
- A **zero-dependency public rare-cancer information site** (first page: EMC) for patient/clinician-facing
  natural-history summaries.
- A strict **medical-integrity discipline**: no fabricated facts, stats, or citations; all clinical claims
  sourced; any non-real data flagged `SAMPLE_SYNTHETIC`.

## 4. How the credits would be used (6-month plan)

Full reasoning + empirical grounding: [ai-credits-strategy-deep-dive.md](./ai-credits-strategy-deep-dive.md).
The credits fund the **LLM-bound layer** our existing work demands but cannot scale by hand — exhaustive,
parallel, adversarially-verified reasoning. Six workstreams:

1. **W1 — Complete + re-grade the mechanism/target map (adds novel axes).** We already have a repurposing
   track; rather than re-pitch it, the credits *finish and harden* it: add the **never-published CMap/LINCS
   signature-reversal analysis** for EMC (input transcriptomic datasets already exist), **stratify by fusion
   subtype** (EWSR1 vs TAF15 — a documented biological switch no repurposing effort has used), **resolve the
   PPARG agonist-vs-antagonist direction**, and **verify every druggable hook's evidence class** (promoter-
   level fusion target vs mere overexpression). Output: a cited, subtype-stratified, evidence-graded EMC
   target map. *(Example project #1.)*
2. **W2 — GPU-triage reasoning layer.** Adversarial pre-scoring of which structural/chemistry runs deserve
   scarce GPU — makes our real compute budget go further.
3. **W3 — Continuous adversarial-verification engine.** Scales our red-team + "zero unresolved claims" rule to
   the whole manuscript corpus; nothing clinical enters public material without surviving it. *(Supports #3.)*
4. **W4 — Definitive EMC natural-history meta-analysis.** Exhaustively find/extract/reconcile/pool published
   cohorts (fixed method: denominator-weighted proportions + Wilson 95% CIs, non-overlapping cohorts only);
   extend to 1–2 adjacent rare sarcomas. *(Example project #2.)*
5. **W5 — Patient-hub scale-out.** Extend the cited rare-cancer info hub from EMC to more rare cancers.
6. **W6 — Rare-disease reasoning eval.** Open eval of model performance on mechanism recall, citation-grounded
   synthesis, natural-history estimation, and refusal-of-fabrication. *(Example project #3.)*

*Why credits (not GPU) are the right fit:* every workstream above is Claude-native. Our separate GPU-bound
structural chemistry (the NR4A3 degrader program) is sequenced independently and is **not** what these credits
pay for — the credits instead make that GPU spend *more efficient* via W2. This avoids any mismatch between the
award type (Claude credits) and the spend.

*Integrity guardrails carried from the underlying research (medical-integrity rule):* EMC's active systemic
therapies are antiangiogenic TKIs (pazopanib/sunitinib, prospective phase-2 evidence) — we do **not** overstate
a novel clinical angle; expression-only hooks (RET/KIT/NTRK) are labeled as such, not as validated targets; no
IGF1R / integrated-stress-response involvement is asserted (no primary EMC evidence); all snippet-level
citations are re-verified against full text before any outward-facing use.

## 5. Integrity & scope guardrails (stated up front)

- No wet lab; every deliverable is either publish-to-convince or in-silico evaluation.
- No efficacy/safety/therapeutic-window/clinical-readiness claims — "predicted" language only.
- All clinical facts cited to primary sources; synthetic/sample data always banner-flagged.

---

### Open items before submitting
- [ ] Confirm scope acceptance: is a genetically-driven rare *cancer* (EMC) in-scope for "rare disease"? If
      unclear from the form, lead with the mechanistic-link / natural-history framing (cleanest match).
- [ ] Decide primary framing emphasis (atlas + natural-history vs eval-building) based on the form's fields.
- [ ] Fill any required fields (team, prior work links, budget justification) from the repo.
- [ ] Final medical-integrity read before submission.
