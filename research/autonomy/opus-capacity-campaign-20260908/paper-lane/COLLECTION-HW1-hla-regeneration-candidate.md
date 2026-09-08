# COLLECTION HW1 — HLA coverage regeneration candidate, FOR OWNER ADJUDICATION

Collected 2026-09-08 by the campaign parent. **Nothing from this lane has been applied to
`research/manuscripts/neoantigen/hla-coverage-emc.md`.** HW1 is a writer, its output is a candidate,
and the scientific owner adjudicates it during ordinary integration.

## Execution

`HW1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a38c690cad98b857f.jsonl`, `cmp`-verified.
`claude-opus-5` throughout. **27 / 27** tool pairs observed, spanning
2026-09-08T13:15:32.763Z to 13:24:31.754Z. HW1 self-reports 18 calls; the observed count governs.

HW1's own lane is retained verbatim: `AFTER-block.md` (35,722 B), `BEFORE-block.md` (26,078 B),
`block.diff` (50,262 B), `HISTORY-superseded.md` (14,335 B), `SOURCE-KEY-MAP.md` (19,127 B),
`NOTES.md`, `MODEL-ENV.txt`, the narrow pre-refinement before-block, and start/end state files.

## Why this lane exists

N2's audit found roughly 140 superseded coverage numbers in the Abstract, §3.1 and §3.2, and the
parent recorded a blocker rather than patching them, because the document's own line 47 says to
regenerate from `hla-coverage.json` and a per-value patch reintroduces the drift the banner records.

The coordinator then widened the brief **in flight, to the same worker**, after reading the applied
diff and finding that a narrow replacement leaves the document incoherent: the banner still said the
both-arms figure was NOT COMPUTED directly after the corrected text reported 1.78% and one strong
class-II binder; Methods still named DRB1\*03:01 and DRB1\*07:01 as the strong helpers; Limitations
still carried "two strong helpers", 16.5% and 28.4%; and the Abstract put 8.51% next to the old 29.7%
interval. HW1's call and time bounds were **not** reset, and it delivered the wider scope inside them.

## What the candidate does

Whole-document projection rather than piecemeal substitution: 362 before-lines to 479 after-lines.
The supersession banner and every superseded block move verbatim into `HISTORY-superseded.md`, so the
live body carries **no** "everything below is superseded" banner over current values. Tables were
generated programmatically from the JSON rather than transcribed. `SOURCE-KEY-MAP.md` carries 242
rows — 52 prose values, 3 retained-unverified, 164 auto-generated cells — each naming its artifact and
exact key path.

The three requirements the coordinator singled out are addressed in the candidate's structure: the
three allele populations (the base coverage set, the 34-allele expanded scan, the 23-allele class-II
panel) are named as separate denominators and never cross-quoted; a standing header separates a
predicted binding score, a modelled carrier coverage and a measured presentation or immunogenicity
result, of which there are none; and `null` regions render as **UNKNOWN with the reason**, never 0,
with a new column reproducing `coverage_all_alleles_used` so Polynesia's one-allele and Melanesia's
two-allele rows cannot be read against the twelve three-allele rows. Upstream provenance is pinned by
name — the AFND `slowkow/allelefrequencies` mirror labelled SECONDARY, ISO 3166 / UN M49 for the
region mapping, and the corrected-seam lineage **reused** from `⛔_class_ii_provenance` rather than
re-established.

## What HW1 refused to write, and that is the right behaviour

- `coverage_cd8_and_cd4_combined` has **no interval key and no regional counterpart**. HW1 printed
  1.78% without an interval rather than fabricating one, stopped that branch, and recorded the exact
  condition that would supply it: the producer emitting the key.
- §3.4's construct numbers live in `vaccine-construct.json`, outside its two scoped artifacts —
  retained verbatim and flagged **NOT RE-VERIFIED**. §1's 0.495 likewise.
- The retained note's "44 binders / 66.1 nM" has no leaf in its two artifacts and stays only in the
  history file.
- **It corrected the parent's own brief.** My dispatch told it the artifacts carry `⛔` warning fields
  it could source the prediction-only framing to. `⛔_class_ii_provenance.⛔` is literally `null` and
  `coverage-curve.json` has no `⛔` field at all, so HW1 sourced that framing to `_note` and
  `_class_ii_note` instead and **invented no `⛔` string**. That is the correct response to a brief
  that asserts something the data does not carry.

## Qualitative claims the candidate drops, with the artifact reading

The CD8/CD4 anti-correlation (Eastern Asia is now highest on e7::e3 at 15.40% and second on CD4 at
9.84%; Northern Africa is lowest on both); "Melanesia is CD8-best" and its A\*11:01 explanation
(A\*11:01 is in no current set); the 78.9%/35.9% range; the derived "~40% uncovered", "~70% missed"
and "~90% of Sub-Saharan African patients" complements, restated in words so no unsourced number
appears; and Micronesia CD4 "0.0%", whose leaf is 6.86%.

## Open for the owner, not decided here

1. **Where the history record lands** — a sibling file, an appendix, or the decision record.
2. **Whether other documents quoting 29.7% / 58.0% / 28.4% / 16.5% need the same projection.** HW1 did
   not survey them and neither did the parent. This is not a claim that they do or do not.
3. **The candidate has passed no repository check.** HW1 ran no gate, no producer and no preflight,
   as instructed. If it is adopted, `lint_consistency`, `lint_style` and the pinned-figure rules must
   be run against it as part of integration — several pinned figures name this file.

## One disclosure HW1 made unprompted

`NOTES.md` §8 records that six intermediate build fragments in its own `/tmp` lane were removed after
assembly. Their content is verbatim contained in the delivered files, and no campaign evidence
directory or collected set was touched. Recorded because HW1 recorded it, not because anything was
lost.

Nothing here is measured. Every binding value is a model prediction and every coverage figure is
arithmetic over pooled secondary-source allele frequencies.
