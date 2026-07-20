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
- A **computational NR4A3-degrader / method-development program** (structural modeling, RBFE/FEP,
  ternary-complex ensemble modeling, paralogue counter-screening) — the translational driver the above biology
  supports.
- A **zero-dependency public rare-cancer information site** (first page: EMC) for patient/clinician-facing
  natural-history summaries.
- A strict **medical-integrity discipline**: no fabricated facts, stats, or citations; all clinical claims
  sourced; any non-real data flagged `SAMPLE_SYNTHETIC`.

## 4. How the credits would be used (6-month plan)

1. **Months 1–2 — Mechanistic-link map.** Large-scale Claude-driven literature synthesis to enumerate and
   rank NR4A3/NR4A cross-disease mechanistic hypotheses, each with primary-source citations and an explicit
   confidence grade.
2. **Months 2–4 — Natural-history curation.** Agentic curation + pooling of registry / patient-org cohorts
   into an updated, fully-cited EMC natural-history resource; extend the method to 1–2 adjacent rare sarcomas.
3. **Months 3–6 — Rare-disease eval.** Build and release an open eval measuring model performance on the
   rare-disease tasks above, with a leaderboard-style report.
4. **Throughout — Public outputs.** Preprint(s) + open data + open eval; outreach to NR4A/nuclear-receptor
   labs, sarcoma/EMC foundations, and patient organizations.

*Why credits (not GPU) are the right fit:* the workstreams above are Claude-native (synthesis, curation,
reasoning, eval construction). Our separate GPU-bound structural chemistry is funded/sequenced independently
and is **not** what these credits would pay for — avoiding any mismatch between the award type and the spend.

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
