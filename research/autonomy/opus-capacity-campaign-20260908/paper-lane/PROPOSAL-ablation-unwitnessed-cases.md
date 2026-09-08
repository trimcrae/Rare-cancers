---
id: DOC-OPUS-CAMPAIGN-PROPOSAL-ABLATION-CASES
title: "Proposal — the unwitnessed ablation cases, one identified and two not"
level: L4
kind: memo
status: live
purpose: >
  Record the identified endpoint ablation case, the ghost-witness mechanism behind it, the proposed
  strengthening, and exactly why the two ASO cases could not be identified.
scope: >
  L4. A diagnosis and a proposal. No manuscript edited, no guard applied, no census regenerated.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# The three unwitnessed ablation cases — one solved, two named as a gap

## ⚠ A correction to my own earlier reading

I reported that the interrupted partial run found "0 blinds" for the endpoint paper and suggested
local and CI might disagree. **That was wrong, and the lane corrected it.** The endpoint run
completed all four rows and row `i=1` is `status: applied, red: false` — **exactly the CI failure,
1 of 4, reproduced**. I have re-read the retained JSON and confirmed it: rows 0, 2 and 3 red, row 1
not. There is no CI/local disagreement to explain, and no one should go looking for one. The ASO file
is the genuine partial, 8 of 91, all red.

## Case 1 — endpoint, IDENTIFIED, reproduced, and repairable

**Sentence** (`endpoint/response-endpoint-indolent-tumours.md`, line 514): the two desmoid records
"not established as being on disjoint patients", where the pooled analysis "draws on three
prospective observational studies" and "whether its 282 patients overlap the 100 below … is unknown
here."

**The census's only named witness is `test_aso_abstract_is_bounded.py`** — and ⭐ **that guard never
opens this file.** Two independent defects stack, and I verified both myself:

1. **A GHOST WITNESS through the docstring channel.** `claim_coverage._test_patterns` scopes a test's
   harvested literals with a plain substring test — `if document and document not in src` at
   `claim_coverage.py:544`. `test_aso_abstract_is_bounded.py` mentions
   `endpoint/response-endpoint-indolent-tumours.md` **only at line 6, inside its module docstring**,
   where it narrates the historical mistake of having borrowed that paper's abstract limit. I read
   both sites. The guard reads the ASO article and nothing else. ⚠ This is the round-16 defect —
   "the census credited a guard's regexes to documents that guard never opens" — recurring through a
   channel the earlier fix did not cover.
2. **The crediting pattern binds WORDS, not numbers.** The literal that matched keys on
   "not … patients … report"; every digit and number word in the sentence sits outside it, so no
   perturbation of 282, 100, two, three or one can change whether it matches.

So `covered` here is false twice over. ⛔ It is a **false coverage assertion**, not stale bookkeeping,
and regenerating the census cannot cure it.

**Proposed repair: STRENGTHEN, with no new science and no manuscript edit.** Both counts already sit
in a committed fetch record — `endpoint/natural-history-inputs.json` holds the verbatim abstracts,
with "(n = 282)" and "Three prospective observational studies" under PMID 39620931 and "100 patients
were enrolled" under PMID 37777684. The proposed test goes into
`test_endpoint_manuscript_figures.py`, which **does** read that paper, so the credit becomes real,
and it binds the manuscript's numbers by equality against what the API actually returned. It adds
three equalities and loosens nothing. ⛔ Not applied here.

## ⚠ A systemic repair that is raised, deliberately not taken

The root cause is the scope test. Making it code-only — stripping docstrings and comments before
`document in src` — is a genuine strengthening. **Measured**, it drops the endpoint census from 9/5
to 6/4, **below the committed floor of 7**. The gate's own rule is that a floor is not lowered to
match, so ⛔ **that change cannot land alone**: the per-sentence guard above must land first and
restore real coverage before the scope fix is affordable. It also touches every censused document and
every floor, so it is the class of change that is raised rather than absorbed. It is raised here.

## Cases 2 and 3 — the ASO sentences: NOT ESTABLISHED, and why

⛔ **The identities are not in the retained CI evidence.** The published log carries only pytest's
short summary, which truncates each assertion at its first line; there is no failures section and
zero occurrences of the per-sentence clauses. They were printed into a body that capture did not
retain.

What would supply them, cheapest first: **(a)** the same job's full pytest output without `-q`
truncation — the assertion prints the sentence, its census credits and the perturbations tried, which
is everything needed; **(b)** the ablation cache from that run — but the committed cache holds 184
entries and **none** with `red: false`, so it cannot supply them; **(c)** a re-run of that single
parametrisation, which is the sweep that was ruled out.

⭐ **Eight of the ninety-one are excluded on measurement**: ASO rows 0–7 all went red before the
sweep was stopped, so none of them is one of the two. A static screen leaves roughly 50 candidates —
too coarse to name two, because the ablation runs every guard that opens the file, not only the
census's named witness. The lane offered five most-suspicious rows explicitly as a **ranked
hypothesis with no measurement behind it**, and I am recording it as that and nothing more.

⛔ **No diff is proposed for a sentence nobody can name.** If the two prove to be the same species as
the endpoint case — a harvested literal binding words while the number sits outside the pattern —
the repair is to strengthen a guard that already reads the ASO article, **not** an exemption. An
exemption is honest only for the residue class the module already names (a number word used as a
noun), and it would have to carry the crediting pattern and the exact perturbations. Which applies is
decidable only from the actual sentences.

**Missing exact cases is a precise diagnosis gap, and it is reported as one.** It is not permission to
re-run all 95 cases.

## What was not done

⛔ No manuscript edited — neither the public ASO article nor the parked endpoint paper; `git status`
showed neither modified. No guard applied, no exemption added, no floor moved, no claim-coverage
regeneration, no source gate reopened. The ASO reproduction was terminated by me at 8 of 91 and was
not restarted.
