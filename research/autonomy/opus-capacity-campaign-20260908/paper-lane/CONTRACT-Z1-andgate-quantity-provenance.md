# CONTRACT Z1 — AND-gate degrader paper: quantity provenance verification

Opened 2026-09-08 by the campaign parent, immediately after the ATR integration commit
`1891cd31ff2d58c2e048b4c4ccc3225dffbb78c9`, under the standing instruction to start the next
eligible unfinished paper in the same cycle.

**Paper:** `research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md` (PUB-ANDGATE,
`drafted`, aimed at `preprint`). Unpublished, drafted, and untouched by every prior lane of this
campaign — no CONTRACT in this directory names it.

**Question, single and bounded.** Does every numeric quantity asserted in the manuscript's main text
resolve to a committed artifact leaf in this repository that actually carries that value, and is each
one labelled at the right epistemic level (computed prediction, published measurement, or assumption)?

**Method.** Read-only. Extract each quantity from the manuscript with its sentence. For each, locate
the artifact and the exact key path that should hold it, read that leaf, and record MATCH,
MISMATCH with both values, or NO SOURCE LOCATED. Report the epistemic label the sentence gives and
whether the source supports it. Propose exact single-occurrence replacement text for any defect
found; apply nothing.

**Prohibitions.** Write nothing under `/home/user/Rare-cancers`; no git write operation; no edit to
any manuscript, artifact, graph file or view. Run no producer, no figure generator and no
`scripts/preflight.sh`. Invent no value, source or measurement. Make no EMC efficacy, safety,
selectivity or clinical-readiness claim; there is no wet lab. Do not touch `reports/W25-*` or any W25
continuation. No network retrieval, no paid API, no GPU. If a claim's source cannot be located, say
NO SOURCE LOCATED — absence of a located source is not evidence the claim is false.

**Stop condition.** Return when every main-text quantity has a verdict, or at ~45 tool calls,
whichever comes first. Returning early with fewer quantities and firm verdicts is a success; padding
is not.

**Deliverable.** The entire report in the final message text. Headings: Worker / Question /
Method and inputs / Quantity table with verdicts / Defects found, with exact proposed replacements /
Limitations / Stop condition / Tool-call count actually used.
