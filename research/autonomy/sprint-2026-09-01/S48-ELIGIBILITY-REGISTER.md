---
id: DOC-SPRINT-S48-ELIGIBILITY-REGISTER
title: "S48-ELIGIBILITY-REGISTER — gate 5 had never read the trial-reachability short report; 33 ERROR converted to 0 with no claim changed, and the file is now armed"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Convert research/manuscripts/care-delivery/emc-trial-reachability.md (PUB-STRATEGY-ARCH, drafted,
  target_venue preprint, unit short_report) from repository register to journal register, then add it
  to TARGETS in lint_style.py so gate 5 reads it on every commit. Records the before/after counts, the
  three sentences whose conversion was load-bearing, and the evidence that no claim moved.
scope: >
  Two files: the manuscript body and lint_style.py's TARGETS list, plus this memo. Measures prose
  register only. Adjudicates no science, re-runs no analysis, and changes no number in the paper.
last_verified: 2026-09-02
---

# S48 — the fourteenth submission text, and the first one gate 5 had never seen

**Owned paths:** `research/manuscripts/care-delivery/emc-trial-reachability.md`,
`research/manuscripts/lint_style.py`, this file. Nothing else was written; no git write command was run.
**Baseline:** `git rev-parse HEAD` = `b4cf28c6be8f464fc25e0cee06f6be50eb181138`.
**Pre-edit snapshot** for the claim diff:
`/tmp/.../scratchpad/sprint/ORIGINAL-emc-trial-reachability.md` (session scratchpad, not committed).

## ⭐ THE COUNTS, UP FRONT

| | words | bold /1000 (limit 12.0) | em-dash /1000 (limit 6.0) | ERROR |
|---|---|---|---|---|
| **before** | 1,718 | **31.4** (54 runs) | **12.2** (21) | **33** |
| **after** | 1,686 | 7.7 (13 runs) | 0.0 (0) | **0** |

Before, by kind: `glyph=14`, `bold-midsentence=11`, `heading-style=6`, `bold-density=1`,
`emdash-density=1`. After: `clean`. With the file added to `TARGETS`, the whole gate reads
**`lint_style: 0 ERROR across 15 file(s)`** — 13 manuscripts plus the two figure sources.

⛔ **Clean first, arm second.** The file was taken to 0 ERROR standing alone before the `TARGETS` line
was written, because arming a guard over a dirty file reddens the commit loop for every other seat.

## 1 · Why the gate had never read it

The same absent-guard shape `lint_style.py`'s own 2026-08-09 comment records: gate 5 enforces register
**only on files in `TARGETS`**, and a submission text absent from that list is not checked-and-passing,
it is **unchecked**. This paper has been `state: drafted`, `target_venue: preprint`,
`unit: short_report` since 2026-08-09 — the same day four other endpoints were taken to submission form
and added — and was missed. Measured damage then: 96 findings in the ATR package, 283 in the surface-target
landscape. Measured damage here: 33.

## 2 · The three hardest sentences

⛔ **The binding constraint was not the counts — it was that every `⚠` and `⛔` in this paper carried a
caveat or a refusal.** Deleting a glyph without rewriting its sentence deletes the flag and leaves an
unmarked claim standing where a warned one stood. Each was re-carried in the prose.

**(a) The screens' fields limit — a `⚠` whose whole job was to stop a reader trusting the big screens.**
Before: `⚠ **The large screens are fields-limited and carry no eligibility text**, so they can identify a
candidate and can never confirm one. That is why every claim below rests on a per-trial retrieval, and why
the two refusals in §4 were only detectable that way.`
After: `The large screens are fields-limited and carry no eligibility text, so they can identify a
candidate and can never confirm one. Every claim below therefore rests on a per-trial retrieval, and the
two refusals in §4 were only detectable that way.`
The warning survives because the *proposition* was always the warning: "can identify a candidate and can
never confirm one" is untouched, and "therefore" carries the dependency the glyph was decorating.

**(b) The refusal caveat in §5 — the sentence that stops the geographic scope being over-read.**
Before: `⚠ **A refusal says what an endpoint would answer, never what a registry contains**, so nothing
above may be read as those registries having been searched and found empty. The geographic scope of this
finding is **partly measured, and not shown to generalise**.`
After: identical prose, bold and glyph removed, no word changed. This is the strongest hedge in the paper
and it needed no conversion at all — it was already a complete sentence that states its own limit, which
is what journal register asks for. ⭐ **The tell that a house-register flag is redundant is that the
sentence reads the same without it.**

**(c) `:147`, the attributed weakening — the one sentence where a "tightening" would have been a claim
change.** Before: `⚠ **This is not a criticism of that trial.** Excluding a histology expected to respond
poorly to the agents under test is an ordinary and defensible design.`
After: `This is not a criticism of that trial. Excluding a histology expected to respond poorly to the
agents under test is an ordinary and defensible design.`
⛔ **"expected to respond poorly" is deliberately weaker than the source, which says `known`, and it is
attributed to another trial's design rather than asserted here.** It is byte-identical after the rewrite.
The editorial pull in a register pass is toward the crisper "known to respond poorly"; that would have
promoted somebody else's design rationale into this paper's assertion about EMC drug response, which is
the R2/R3 line `lint_claims` guards.

## 3 · The headings

Six were sentences. Each became a noun phrase; none became a shorter list.

| before | after |
|---|---|
| `2 · What was read, and how` | `2 · Sources and retrieval` |
| `3 · The trials that admit this disease and do not name it` | `3 · Trials admitting this disease without naming it` |
| `4 · The counter-finding: a keyword map would be worse than nothing` | `4 · The counter-finding: the cost of a keyword map` |
| `4.1 · And the one non-US registry that answered names this disease only to refuse it` | `4.1 · Exclusion in the one non-US registry that answered` |
| `5 · What this does not establish` | `5 · Limitations` |
| `6 · What would fix it` | `6 · Remedies` |

⚠ **§5 kept all five of its bullets and every word of their content.** Only the heading moved, to the
noun phrase the reference papers use (`emc-surface-target-landscape.md` heads the same section
`### Limitations`). A limitations section that loses an item to a heading rewrite is the failure this
task existed to avoid.

## 4 · No claim changed — the evidence, not the assertion

Method: both versions normalised (emphasis markers and `⭐⛔⚠` stripped, em-dash and hyphen-bullet mapped
to comma), re-split into sentences, and diffed. **Every hunk is punctuation, a heading, or a connective.**
The complete set of non-punctuation changes:

- `And the sharpest result is an absence:` → `The sharpest result is an absence:` (dropped conjunction)
- `That is why every claim below rests on…` → `Every claim below therefore rests on…`
- `A transport defect in the earlier read is disclosed rather than worked around.` → `The earlier read
  carried a transport defect.` (the disclosure *is* the sentence; the self-describing frame went)
- `The last row is kept separate on purpose.` → `The last row is kept separate from the three above it.`
  (`deliberately`/`on purpose` is a `BANNED` self-defence; the separation and its reason are intact)
- `So the mechanism runs in both directions, and that is the fuller result.` → `The mechanism therefore
  runs in both directions, which is the fuller result.`
- `This is the argument for reading eligibility text one trial at a time, and it is the methodological
  content of this paper.` → `Reading eligibility text one trial at a time is the methodological content
  of this paper.`
- `…a defect here, not a finding about that registry.` → `…a defect here rather than a finding about
  that registry.`
- `§4 is the demonstration of why` → `Section 4 is the demonstration of why`
- `This was drafted the other way…` → `This section was drafted the other way…`

⭐ **Every number, identifier, count, hedge, null and negative is byte-identical**: the two admitting
trials and their listed conditions, "nine further trials", `n = 73`, `n = 5500`, the five non-oncology
studies, "Not one is an oncology study", the observational row's separation, "partly measured, and not
shown to generalise", "Statuses go stale", "no patient was involved". **Zero sentences were left
unconverted**, so there is no reported-error-instead-of-weakened-claim trade to declare.

⛔ **Scope was not widened.** The paper defends **reachability** only, of an endpoint spanning scheduling,
sequencing and reachability, and the rewrite added no sentence and no heading that implies the other two.
`5 · Limitations` is narrower-sounding than `What this does not establish` as a *label*; its five
bullets are unchanged, and the paper's own restriction to findability ("The relevance is entirely about
findability") survives verbatim in §4.1.

## 5 · Every other gate, verbatim

| gate | verdict |
|---|---|
| `lint_style.py` (this file) | `lint_style: 0 ERROR across 1 file(s)` — `clean` |
| `lint_style.py` (armed, whole gate) | `lint_style: 0 ERROR across 15 file(s)` |
| `lint_claims.py` (this file) | `lint_claims: OK - 1 file(s) clean`, exit 0 |
| `lint_claims.py` (repo) | `lint_claims: 0 ERROR, 172 WARN across 129 file(s)` — no WARN in this file |
| `lint_citations.py` | `lint_citation_types: 23 type claim(s) checked against 13 cached record(s), 0 error(s), 1 retraction advisory(ies)` — every advisory is ACKNOWLEDGED and names other files |
| `lint_consistency.py` | `lint_consistency: 0 ERROR across 29 target file(s)` |
| `lint_readability.py` | exit 0; 81 sentences, mean 17.5 w, p90 30, max 43, **0 sentences >60 w**, FKGL 11.4, caution 10.6/1kw |
| `node scripts/validate-research.mjs` | `OK - 14 candidate(s) valid. 1 warning(s)`, exit 0 — the warning is `candidates[0] "imatinib-kit-subset" is T3`, pre-existing and unrelated |

⚠ **`lint_readability` is a screen, not a verdict** (its own closing line says so). Its longest sentence
is 43 words and nothing exceeds 60; no sentence was shortened to move a number.

## 6 · What this memo does not establish

- **Gate 5 checks register, not argument.** A clean run means the known mechanical tells are absent. It
  says nothing about whether this paper's argument holds, and `lint_style.py`'s own docstring says so.
- **The register conversion is not a review.** No hardening seat has read this paper as a reviewer; it
  remains `state: drafted`, and this memo does not move it.
- **Nothing here authorises a post.** `publish_bar.py::CLAUSES` decides that, from committed artifacts.
- ⛔ **The census this memo answers was one file.** Whether any other repository manuscript is a
  submission text absent from `TARGETS` was not tested here and is not claimed either way.

## Appendix A · Superseded values

None. This memo pins no figure that existed before it, and re-pins nothing in
`research/manuscripts/pinned-figures.json` — that file was not touched.
