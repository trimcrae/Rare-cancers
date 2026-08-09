---
id: DOC-EPMC-QUERY-CRAFT
title: What separates a Europe PMC query that finds the class-defining paper from one that returns junk
level: L1
kind: method-note
status: live
canonical_for: ["Europe PMC query construction for this repository's literature lanes"]
purpose: >
  Record, from measurement rather than intuition, the one property that decided whether a retrieval
  in this repository returned the paper it was looking for — so a lane does not re-learn it by
  spending a CI run and, worse, does not cite from a payload that only looks populated.
scope: >
  L1. Nine dispatched Europe PMC searches on 2026-08-09, their hit counts and their top records.
  A note about retrieval mechanics; it makes no scientific claim.
audience: [maintainers, autonomous research agents]
date: 2026-08-09
last_verified: 2026-08-09
---

# Europe PMC query craft, measured

⭐ **THE RULE: put the DISCRIMINATING TERM inside `TITLE:()`.** Every query that landed on the
class-defining paper did. Every query that returned junk relied on unfielded multi-term `OR`s.

| hits | outcome | query shape |
|---:|---|---|
| 0 | ⛔ **zero, and not a negative** | `(POLQ OR "polymerase theta") AND ("homologous recombination deficien")` — truncated phrase |
| 3 | ⭐ bullseye | `TITLE:(tazemetostat) AND TITLE:("epithelioid sarcoma")` |
| 11 | ⭐ bullseye | `TITLE:(hyperthermia) AND TITLE:(sarcoma) AND (randomised OR …)` |
| 33 | ✅ clean | `TITLE:("BH3 profiling")` |
| 934 | ⛔ junk | `("expanded access" OR …) AND ("rare cancer" OR sarcoma) AND (outcome OR registry)` |
| 1537 | ⛔ junk | `("myxoid liposarcoma" OR …) AND (radiotherapy OR radiosensitiv) AND (response OR outcome)` |
| 3565 | ⛔ junk | `(HSP90) AND ("fusion oncoprotein" OR "fusion protein") AND (client OR degradation)` |
| 3957 | ⛔ junk | `("carbon ion" OR "particle therapy" OR proton) AND (sarcoma) AND (registry OR …)` |

## Why the junk looks the way it does

⛔ **A broad unfielded query ranks review articles and guidelines to the top**, because they mention
everything. The autophagy-assay guidelines have thousands of authors and surfaced as the top hit for
an HSP90-and-fusion-protein query; a cardiovascular burden study and *Cancer statistics* topped an
expanded-access query. Neither payload is empty, and **that is the danger** — the run is green, the
file has content, and citing from it would attribute a claim to a paper nobody read.

## Two failure modes that do not announce themselves

- ⚠ **A ZERO IS NOT A NEGATIVE.** The `POLQ` query returned `hitCount: 0` because the phrase was
  truncated mid-word, not because the literature is absent — the same search, re-fielded, returns the
  class-defining papers immediately. **Re-run before reporting an absence**; an absent reading is not
  a reading of absence (CLAUDE.md §4).
- ⚠ **`sort=CITED desc` IS WHAT SURFACES THE CLASS-DEFINING PAPER**, and its omission is why the
  first dispatch of this session returned recent reviews rather than the landmark results. Relevance
  order answers "what mentions this", citation order answers "what established this". They are
  different questions and the second is usually the one a class definition needs.

## The check to run before citing anything

⛔ **Read the top three titles.** If they are reviews, guidelines, or obviously off-topic, the query
failed regardless of hit count, and nothing from that payload may be cited. This costs one glance and
is the only step that separates a retrieval from a citation.
