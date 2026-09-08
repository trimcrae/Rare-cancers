# R1 — collection: a reviewable ATR reconciliation PROPOSAL (nothing applied)

Collected 2026-09-08 ~11:33 UTC. ⛔ **Nothing here is applied.** R1's output is a **reviewable
candidate**, explicitly a **proposed reconstruction, not a recovered original** — no draft containing
the 2026-08-10 revision was found, and none is claimed to exist. The **final version and integration
decision belongs to the scientific coordinator** under existing authority; this creates no per-item
approval queue, and publication permissions remain separate.

| item | measured |
|---|---|
| child | `a6a41bcc67e17cc38` |
| model strings | **`claude-opus-5` only** — from transcript model fields |
| tool pairs | **18** (self-reported 20 — the first *over*-report of the campaign) |
| shared writes | **none** — `git status` empty at its start and end, verified |

## ⭐ It decided the arithmetic instead of trusting the response — and I re-derived it

The committed manuscript says **"176 nucleotides … encodes 59 residues"**. From the committed artifact
`emc-fet-frame-and-composition.json`:

```
nr4a3_5utr_nt_retained_total              = 176
nucleotides_spanned_by_the_extra_residues = 177
_the_arithmetic = "1 nt donated by EWSR1 + 176 nt of NR4A3 5'UTR = 177 nt = 59 codons"
```

and the test at line 32 asserts `span % 3 == 0`, with the docstring *"The defect this module was
written for: 176 nt cannot encode 59 residues."* **176/3 = 58.67; 177/3 = 59.** So the committed text
is **arithmetically wrong** and the response's 177 is right — established from committed inputs, not
assumed. The proposed text separates the two quantities the original sentence collapsed: **177 nt
spanned**, **176 nt supplied by NR4A3** (174 from exon 2 + 2 from exon 3).

## What it produced

**15 mechanical corrections**, each traceable to a committed block: the seam arithmetic; Table 1's
inferred "rank" replaced by counted frequencies; Table 4 rebuilt with the two-tier status column, the
restored EWSR1::ATF1 e7 row, the RGG(1) anchor and the ATF1 span; "bracket"/"interpolate between points
already measured" removed; margin 14 → **13** with the convention stated; Table 5 → the symmetric
sweep, **0.439 vs 0.400**, "separates" not "decisive"; "byte-identical" → "identical in sequence";
"the source" → the named authors; §3.2 gains the frame rule with the full phase-1 donor set.

**7 decisions left to a human**, each with a recommendation and its basis — retitle, delete Appendix A,
insert Figure 1 and cut to six tables, reduce P1-P5 to three, move the scope blockquote, renumber into
a Discussion, add §2.3/§4.1 and supplementary tables. ⭐ On the predictions it flagged the right
constraint itself: **that table is preregistration-shaped and this repository preserves
preregistrations**, so a human decides correction versus new registration.

**Coverage stated honestly: 15 corrections, 7 decisions, 8 unresolved — not 41, and not claimed as
41.** The candidate keeps the baseline's shape deliberately, because every shape change is a decision
rather than a correction.

## ⭐ U8 — the finding that changes the blocker

R1 reports that **the changelog's later same-day block corrects sentences present in neither committed
file**: its "before" column quotes a **first revision**, so four of its five rows cannot be applied
against the committed baseline at all. **The ATR package is missing TWO revision passes, not one, and
the second is unreachable without the first.**

**Parent corroboration, stated at its true strength:** I sampled 29 quoted strings from the changelog;
**25 do not appear in the committed manuscript**. That is a crude measure — it includes the changelog's
own headings — so it **corroborates** R1's reading rather than proving it. The precise claim rests on
R1's row-by-row reading, which I have not independently re-derived.

## Explicit UNRESOLVED list, carried forward

U1 the title string · U2 the Figure 1 caption and panel assignments (images **not opened**) · U3 the
§4.1 procedure prose and Supplementary Table S3 · U4 the §2.3 text · U5 the ORCID iD — the paper's own
editorial block says the repository carries none, and it was **not invented** · U6 journal/year/volume
/pages for PMIDs 11679947 and 12598313, **marked rather than written** · U7 the cover letter, not
opened · **U8 the second revision pass**.

## Bounds respected

No shared path written, copied, moved or restored; no git write; **no gate rerun**; no network,
retrieval, history hunt, census or whole-paper re-review; figure images not opened; cover letter,
registry, views and all clinical artifacts untouched; no efficacy, safety, selectivity or
clinical-readiness claim.

Deliverables retained in `R1-executed-artifacts/`: the baseline, the proposed manuscript, a 232-line
diff, `build_candidate.py` (a replayable edit script) and `DECISION-MEMO.md`.
`/tmp/claude-0/r1-lane/` intact, nothing deleted.
