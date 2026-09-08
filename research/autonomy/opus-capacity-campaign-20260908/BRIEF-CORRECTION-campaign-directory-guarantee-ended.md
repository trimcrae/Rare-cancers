# CORRECTION — the campaign-directory commit guarantee has ended

Recorded 2026-09-08 by the campaign parent. **Four independent workers reported this without being
asked to look for it**: CR1, N2, MM1 and BM1 each measured it during their own start/end HEAD
verification and each flagged it as outside their lane.

## What COMMON-BRIEF says

`COMMON-BRIEF.md` §1 tells every worker that each commit since the pin touches **only**
`research/autonomy/opus-capacity-campaign-20260908/`, and warns that if a coordinator commit ever
touches anything outside that directory, the guarantee ends and **39 pin-anchored reports lose it
silently**.

## What actually happened

It ended, and the parent ended it. Between `aa66d1d7` and `4992bca5` these four files changed outside
the campaign directory:

- `research/manuscripts/dependency/emc-atr-collaborator-package.md`
- `research/manuscripts/submission-metrics.json`
- `systems/views/L2-rt-andgate.md`
- `systems/views/L3-publications.md`

Since then the parent has committed changes to eight manuscripts, two generated views,
`submission-metrics.json` and `submission-residue-baseline.json`. The guarantee is comprehensively
gone and will not come back during this campaign, because integrating manuscript corrections is what
this phase of the work is.

## What this does and does not invalidate

It does **not** invalidate any measurement in this campaign's reports. Every worker that flagged it
also verified, file by file, that none of the changed paths was an input to its own audit, and each
recorded the hashes it read. Those verdicts stand on their own evidence.

What it does invalidate is the **shortcut**: a report pinned to a commit may no longer assume that a
later HEAD leaves its inputs untouched. Any worker or reader relying on §1's blanket statement should
instead do what these four did — name the files it measured and check those files specifically across
the HEAD move. That is a stricter discipline than the guarantee, not a weaker one.

`COMMON-BRIEF.md` itself is **not edited here**. It is a frozen brief that 39 reports are pinned to,
and rewriting it would change what those reports were written against. This correction sits beside it
and supersedes its §1 guarantee from `4992bca5` onward.

No report was re-run, no measurement was recomputed, and nothing was deleted to record this.
