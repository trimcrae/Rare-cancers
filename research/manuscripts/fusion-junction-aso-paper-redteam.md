# Red-team of the fusion-junction ASO paper — deficiencies + fixes applied

> **Role:** adversarial review of [`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md) (2026-06-26),
> run as two independent reviewers (computational/methods lens + molecular-biology/clinical lens) plus a
> data-cross-check against every committed JSON. Scope per the standing directive: critique the *manuscript's
> claims, framing, internal consistency, and methods* — **not** the experiments still out of reach (no wet
> lab, delivery unsolved). "Experiment not finished" is never a finding; "the writeup claims more than the
> finished analyses establish" is. Each finding below has a fix that was applied to the paper and/or the
> supporting scripts/JSON in the same change. Findings are ordered by severity. Two reviewer sub-claims that
> turned out to be **wrong on the data** are recorded at the end so they are not re-raised.

## F1 (high) — §3a-ter showcased the *dirtiest* gapmer as its "clean, balanced" favorable example
**Deficiency.** §3a-ter (and the abstract) presented EWSR1 200 / NR4A3 8 with "a fusion-specific 5-6-5
gapmer `5′-GCTATACGGCTGTGTA-3′` … **GC 50.0%** … i.e. a clean, balanced design." But that exact oligo is the
scan's in-band pick, and §3a-quater's own committed gap-resolved screen
([`junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json))
shows it carries **29 true cleavage risks — the worst of the five** gapmers at that breakpoint. A reader of
§3a-ter alone is actively misled, and the example silently contradicts the paper's own thesis that "GC-triage
≠ specificity."

**Why it matters.** This is the single most catch-on-sight inconsistency in the paper: the poster child for
"specificity is achievable at a favorable breakpoint" is, in the paper's own off-target table, the least
specific design at that breakpoint.

**Fix applied.** Rewrote §3a-ter to state explicitly that `GCTATACGGCTGTGTA` passes GC/complexity triage but
**fails** the gap-resolved BLAST screen (29 cleavage risks), and that the actually-clean designs at 200/8 are
the slightly higher-GC `GGGCTATACGGCTGTG` (62.5%) and `AGGGCTATACGGCTGT` (56.2%). Reframed the abstract's
breakpoint-scan sentence so it no longer presents that oligo as clean and instead leads with "triage is
necessary but not sufficient; a per-oligo BLAST screen must follow." Now 200/8 illustrates *both* halves of
the thesis (breakpoint favorability **and** per-oligo selection).

## F2 (high) — "canonical breakpoint" implies a clinical reality it does not have
**Deficiency.** The paper repeatedly called the modelled breakpoint (EWSR1 kept to codon 264, NR4A3 from
codon 2) "the canonical" junction. It is not a validated common patient breakpoint: codon 264 is the EWSR1
1–264 IDR/transactivation *protein-domain* boundary reused across the repo, and the **real** recurrent EMC
junctions are exon-level, joining **predominantly NR4A3 exon 3** (the in-repo companion
[`novel-modalities.md`](./novel-modalities.md) §3.3 resolves EWSR1 exons 7/9/10/11/12/13 → NR4A3 exon 3 from
Ensembl exon structure; the commonly reported junction is EWSR1 exon-7/12 :: NR4A3 exon-3). "NR4A3 from codon
2" retains nearly the entire NR4A3 CDS — a different seam from an exon-3 fusion. The central "the canonical
junction is GC-rich/unfavorable" narrative was thus built on a sequence that may not correspond to any real
breakpoint, and "canonical" overclaimed.

**Why it matters.** The paper's whole feasibility arc (unfavorable reference → favorable elsewhere) hangs on
what "the" junction is. Calling an arbitrary codon-space default "canonical" lets a reader mistake a modelling
convenience for the breakpoint patients carry.

**Fix applied.** Rewrote the §3a integrity flag to define "canonical" explicitly as a *label of convenience*
(the script default, a protein-domain landmark — **not** a validated clinical breakpoint), state that the
real recurrent junctions are exon-3-based, and note that **neither off-target screen has been run on the real
exon-3 junction**. Replaced the most load-bearing "canonical" claims (abstract, §6, the de-risked lines) with
"modelled reference junction." Added a References "to verify" entry for the rank-order of recurrent exon
junctions, and made §3b.2 name "build and screen the real exon-7/12::exon-3 junction" the genuine remaining
step (it previously said the remaining step was a favorable-breakpoint screen, which is now done).

## F3 (high) — RNase-H discrimination logic under-specified; the specificity metric overstates
**Deficiency.** §1/§2a justified fusion-exclusivity with "each wild-type mRNA matches only one half of the
oligo." That is necessary but not sufficient: RNase-H1 cleaves only where the **6-nt DNA gap** is
base-paired, so discrimination is set by junction-unique bases *inside the gap*, not across the whole 16-mer.
The committed `specificity_margin` is computed oligo-wide (`min(bases_from_EWSR1, bases_from_NR4A3)` over all
16 nt, `junction_aso.py`), so it **overstates** true gap-level discrimination, and the tiler only requires the
junction to fall *somewhere* in the gap (`gap_start < j < gap_end`), permitting a 1/5 split where a parent
shares 5 of the 6 gap bases and could be cleaved.

**Why it matters.** The fusion-exclusivity claim is the paper's reason to exist; stating it loosely invites a
reviewer to find the counterexample (a parent matching the full gap plus a flank).

**Fix applied.** Added a precise blockquote in §2a stating the gap-level requirement, flagging that
`specificity_margin` overstates, and pointing to the transcriptome off-target screen (not the margin) as the
operative filter; echoed it in §5. Added a §3b.1 design-rule fix: require the junction near the **gap centre**
with ≥2–3 junction-unique bases each side *inside the gap*, and report a gap-level margin.

## F4 (high) — provenance string bug: favorable-breakpoint JSONs were labelled "assumed canonical breakpoint"
**Deficiency.** `junction_aso_offtarget.py` hard-coded `method.breakpoint_model = "assumed canonical
breakpoint"` regardless of the env-overridden breakpoint, so the committed 200/8 files
([`junction-aso-offtarget-bp200-8.json`](../modalities/junction-aso-offtarget-bp200-8.json) and its
`-gapres` companion) carried a provenance string contradicting their own `breakpoint: {…, is_canonical:
false}` block. For a publish-to-convince artifact whose value is honest provenance, a self-contradictory
provenance label is a real defect.

**Fix applied.** Made the script's `breakpoint_model` string breakpoint-aware (reference vs env-override), and
corrected the field in the two committed JSONs to "modelled non-reference breakpoint (EWSR1 keep 200 / NR4A3
from 8); set via env override" — data values untouched, only the mislabel fixed. Future re-runs now emit the
correct string.

## F5 (medium) — the two off-target screens were said to "agree" when they diverge per-oligo
**Deficiency.** §3a-quater said the gap-resolved BLAST (2/5 clean) and the uncapped full-transcriptome screen
(4/5 clean) "agree." They agree only on the **two BLAST-clean oligos**; for the other three they disagree
sharply — the uncapped scan reports `GCTATACGGCTGTGTA`/`GGCTATACGGCTGTGT` as 0/1 ≤1-mismatch off-target while
the gap-resolved BLAST flags the same two as **29/15** cleavage risks. The cause is stringency: the uncapped
≤1-mismatch (≥15/16) cutoff structurally cannot see the 14/16 (2-mismatch) hits that drive the BLAST numbers.

**Fix applied.** Rewrote the reconciliation to state agreement-on-the-2 / divergence-on-the-rest and the
structural reason, and to make the **2** designs (surviving the wider ≤2-mismatch gap-resolved test) the
*defensible* count, with "4 of 5" holding only if 2-mismatch hits are deemed non-cleaving.

## F6 (medium) — "zero true cleavage risk" / "cannot be cleaved" / "specificity achievable" overclaim a heuristic
**Deficiency.** The "2 of 5 clean" headline rests entirely on the rule "any mismatch in the 6-nt gap ⇒
non-cleavable," stated categorically ("cannot be cleaved," "decisive," "achievable"). RNase-H1 tolerance of a
single central mismatch is reduced but not guaranteed zero and depends on identity/position/flank length; no
citation supports the quantitative rule.

**Fix applied.** Softened throughout to "predicted strongly disfavoured / 0 predicted-cleavable under a
conservative all-gap-mismatch-blocks-cleavage assumption," added an explicit assumption bullet in §3a-quater,
changed "achievable" → "reachable (predicted, not demonstrated)," and added a References "to verify" entry for
the quantitative gap-internal-mismatch tolerance.

## F7 (medium) — the §4 experiment cannot *prove* fusion-exclusivity as designed
**Deficiency.** §4 billed knockdown in EMC lines (USZ-EMC, NCC-EMC) vs a scrambled control as "decisive" for
fusion-vs-wildtype sparing. But EMC cells may express little wild-type *NR4A3*, so "sparing" cannot be shown
where the wild-type transcript is near-absent; and a scrambled control tests sequence-independent toxicity,
not discrimination. The phenotype arm cannot separate fusion-knockdown lethality from generic toxicity without
a fusion-negative line.

**Fix applied.** Strengthened §4 with the missing controls: (a) a fusion-negative cell engineered to express
the fusion (or an isogenic knock-in/parental pair) carrying *both* the chimera and abundant wild-type
NR4A3/EWSR1; (b) single-parent-targeting ASOs as positive controls for wild-type knockdown; (c) a
fusion-negative line for the phenotype arm. Stated that without these the experiment shows knockdown + killing
but cannot prove sparing.

## F8 (medium) — "most mechanistically de-risked" overstates relative to the unsolved delivery gate
**Deficiency.** The paper called the ASO "the most mechanistically de-risked fusion-exclusive option" while
itself conceding delivery is wholly unsolved, specificity is only predicted, and feasibility is
breakpoint-conditional. "De-risked" conflates mechanistic clarity with overall risk; the degrader's dominant
risk (sparing wild-type NR4A3) differs in kind, not strictly worse.

**Fix applied.** Replaced every instance with "most mechanistically *unambiguous* (knockdown of an addicted,
fusion-only transcript), conditional on breakpoint-favorability and gated by delivery," and added an explicit
sentence that neither route is strictly more de-risked overall.

## F9 (medium) — B7-H3 framed as a plausible EMC marker on no EMC-specific evidence
**Deficiency.** §3c named B7-H3 (CD276) as "a candidate worth evaluating as an EMC surface marker." B7-H3 is
broadly over-expressed across sarcomas, but there is no EMC-specific expression study; the `[citation to
verify]` flag was honest but the framing still implied plausibility for the one delivery handle named.

**Fix applied.** Stated plainly that B7-H3 EMC expression is **unknown** and the rationale is extrapolation
from other sarcomas, requiring an EMC IHC/RNA-seq survey first; promoted **intratumoural administration**
(needs no marker) to the top of the delivery hypotheses; updated the References "to verify" entry.

## F10 (medium) — the "62% favorable" headline is a grid/threshold artifact, repeated as reassurance
**Deficiency.** "243/390 (62%) favorable" was repeated four times as a load-bearing reassurance. The 390 are
an arbitrary codon-space grid with hand-chosen GC/entropy thresholds, and "favorable" requires only that a
triage-passing in-band design *exists* (a parent-substring test, not the BLAST screen) — so 62% is an **upper
bound on designable positions, not a real-patient frequency**, and includes positions whose in-band design
fails the off-target screen (exactly 200/8).

**Fix applied.** Reframed every headline use as "62% pass a GC/complexity/parent-substring **triage** — an
upper bound on designable positions, not a real-patient breakpoint frequency," and tied the bound to the
200/8 triage-passes-but-BLAST-fails example and the still-unrun real exon-3 junction.

## F11 (medium) — uncapped-screen method bounds and ViennaRNA accessibility caveats were omitted
**Deficiency.** §3a-bis(iii) called the uncapped counts "true counts" without noting that the seed-and-extend
pigeonhole finds every ≤1-**substitution** off-target but **not** indels/bulges, and counts **sense-strand**
transcript matches only. The accessibility values (0.34–0.42) were read as a potency ranking, though they come
from a truncated **local 180-nt fold** (can over-estimate accessibility), are a weak potency correlate, and
their spread is within method noise.

**Fix applied.** Added a method-bounds sentence (≤1-substitution, sense-strand only) and an accessibility
caveat (local-fold equilibrium proxy; 0.34–0.42 spread is not a meaningful ranking) to §3a-bis(iii).

## F12 (low) — reference-junction BLAST "0 of 5" was capped, coverage-only, and over a failed query
**Deficiency.** The reference-junction BLAST screen ([`junction-aso-offtarget.json`]) was HITLIST-capped at
50, scored **coverage-only** (not gap-mismatch-resolved, unlike the 200/8 run), and one of five queries
failed (`n_screened_ok = 4`) — yet the paper led with "0 of 5 free of gap-spanning near-matches" as a co-equal
headline next to figures it elsewhere disowns.

**Fix applied.** §6 now phrases it as "0 of the 4 successfully screened," flags that it was coverage-only and
not strictly comparable to the gap-resolved 200/8 screen, and rests the reference-junction negative on the
**uncapped true counts (8–95 ≤1-mismatch)** instead.

## F13 (low) — point estimates without version/uncertainty framing; "quiet genome ⇒ no escape" over-extrapolation
**Deficiency.** Seed off-target counts (~21k–119k; 3,366) and accessibility were given as precise quantities;
§1 stated a quiet genome means "no large mutational landscape offering obvious escape" as if fact.

**Fix applied.** Labelled the seed counts "version-dependent point estimates"; qualified §1 to note clonality
lowers *baseline* heterogeneity but does not preclude *acquired* resistance, naming a breakpoint-region point
mutation that abolishes oligo complementarity as a specific ASO escape route.

---

## Reviewer sub-claims that were WRONG on the data (recorded so they are not re-raised)
- **"200/8 is not even a FAVORABLE row in the scan."** False: the committed
  [`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json) row for EWSR1 200 / NR4A3 8
  has `favorable: true`, `best_gapmer_in_band_gc: 50.0`, `best_sirna_in_band_gc: 52.6`. 200/8 *is* favorable;
  the valid core (it was chosen by hand, not by the scan's `most_favorable` rank, which is the GC-extremity
  artifact 204/16 with **no** in-band gapmer) was retained and added to §3a-ter.
- **"The headline numbers don't match the JSONs."** They do: the data cross-check confirmed every gapmer
  sequence/GC/margin (`junction-aso-designs.json`), the ≤1-mismatch counts 8/16/17/58/95
  (`aso-insilico-evaluation.json`), siRNA 0-pass / min-GC 73.7% (`junction-sirna-designs.json`), the 200/8
  uncapped 5/5-zero-exact / 4/5-zero-≤1mm (`aso-insilico-evaluation-bp200-8.json`), the gap-resolved
  0/15/0/29/27 risks and the two clean antisense sequences (`-gapres.json`), and the seed counts. The only
  sequence error (the §3a-quater clean oligos printed as their target-mRNA strings) was fixed in the prior
  change, before this red-team.

**Net.** The paper was already scrupulous about modelled-vs-real, the GC problem, delivery, and `[citation to
verify]` markers. The substantive corrections were: a self-undermining showcase example (F1), an overclaimed
"canonical" label resting on a non-real breakpoint (F2), an under-specified discrimination mechanism and an
overstating specificity metric (F3), a provenance-string bug (F4), and a too-rosy reconciliation of the two
screens (F5/F6). All are fixed in the same change; the genuine open scientific gap the red-team surfaces — run
the full pipeline on the **real exon-7/12 :: NR4A3 exon-3 junction** — is now stated as the lead next step.
