# A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity that the NR4A3 degrader cannot reach

> **In-silico design / feasibility draft (2026-06).** No wet lab; no molecule synthesized; **no new
> GPU run was performed** — the real results cited here are CPU outputs: the committed gapmer designs
> [`../modalities/junction-aso-designs.json`](../modalities/junction-aso-designs.json) (5 fusion-specific
> gapmers), a transcriptome-wide off-target screen
> [`../modalities/junction-aso-offtarget.json`](../modalities/junction-aso-offtarget.json) (0 of 5 free of
> gap-spanning near-matches), and a junction-siRNA design set
> [`../modalities/junction-sirna-designs.json`](../modalities/junction-sirna-designs.json) (0 of 5 pass;
> min GC 73.7%), a full-transcriptome (uncapped, 186,185-transcript) off-target + accessibility + siRNA-seed
> evaluation [`../modalities/aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json) (0 of 5
> canonical gapmers off-target-free; true ≤1-mismatch counts 8–95, not the capped "50"), a per-breakpoint
> feasibility scan
> [`../modalities/junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json) (390 modelled
> breakpoints; 243, or 62%, favorable; the canonical one is not), and a gap-mismatch-resolved off-target
> screen on a favorable breakpoint
> [`../modalities/junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json)
> (2 of 5 gapmers predicted clean — zero true RNase-H cleavage risk), corroborated by an uncapped
> full-transcriptome screen on the same favorable breakpoint
> [`../modalities/aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json)
> (4 of 5 gapmers with zero ≤1-mismatch off-targets; 5 of 5 with zero exact — vs 0 of 5 clean at the
> canonical junction). Together these show feasibility is
> **breakpoint-conditional but breakpoint-selectable**: specificity and chemistry at the *canonical* modelled
> junction are poor, but that is a property of that junction position — a clear majority of modelled
> breakpoints yield clean, in-band, fusion-specific designs — not of the modality. **The fusion-selectivity rationale in one line:** the breakpoint mRNA seam is
> present *only* in the chimera, so an RNase-H gapmer (or siRNA) targeting the junction silences
> EWSR1::NR4A3 while sparing wild-type *EWSR1* and wild-type *NR4A3* — true fusion-exclusivity, which an
> LBD-binding degrader (identical domain in fusion and wild-type) cannot achieve. Every clinical/quantitative
> claim is cited, computed from committed repo output, or flagged as a design hypothesis. Nothing here is a
> validated drug or clinical evidence. **An adversarial self-review of this manuscript — deficiencies and the
> fixes applied — is recorded in [`fusion-junction-aso-paper-redteam.md`](./fusion-junction-aso-paper-redteam.md).**

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in the large majority of cases by an in-frame fusion
of *EWSR1* (less often *TAF15*, and rarely TCF12/TFG/FUS) to the orphan nuclear receptor *NR4A3*, on an
otherwise "quiet" genome with few recurrent secondary mutations [Sjögren; Panagopoulos]. The companion
NR4A3-degrader program in this repo targets the **NR4A3 ligand-binding domain (LBD)** — a domain whose
sequence is *identical* in the fusion and in wild-type NR4A3 — so that agent is NR4A3-selective but **not
fusion-selective**, and it carries the residual liability of also removing tumour-suppressive wild-type
NR4A3 [Mullican; Safe & Karki]. This manuscript pursues the one feature the degrader cannot offer: **true
fusion-exclusivity at the RNA level.** The chimeric mRNA contains a breakpoint *junction sequence* that
exists in no normal transcript; an antisense gapmer whose central DNA window straddles that seam directs
RNase-H1 cleavage of the fusion transcript while sparing both parent mRNAs by sequence, and a
junction-spanning siRNA offers a parallel route. We report the one real, committed computational result —
**5 fusion-specific candidate gapmers** designed against the modelled EWSR1::NR4A3 junction
([`junction-aso-designs.json`](../modalities/junction-aso-designs.json)), each drawing bases from both
sides of the seam and absent as a perfect complement from either parent CDS — together with the honest
caveat that surfaces immediately: this junction is **GC-rich (~75–81% GC)**, outside the usual comfort
zone, and would need chemistry tuning. Two further real, committed CPU results sharpen this caveat: a
transcriptome-wide off-target screen (blastn-short vs human RefSeq RNA) finds **0 of 5** gapmers free of
gap-spanning (RNase-H-cleavable) near-matches, and a GC-tolerant junction siRNA route does **not** rescue
the chemistry — its lowest-GC fusion-specific guide is still **73.7% GC**, so **0 of 5** siRNA guides pass
all filters. The honest synthesis is that this *modelled* breakpoint sequence is intrinsically GC-rich and
low-complexity, hurting gapmer chemistry, siRNA GC, and predicted specificity at once — a property of this
junction, not of the modality. A new per-breakpoint feasibility scan
([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)) confirms this directly:
sweeping **390 modelled breakpoints** (an arbitrary codon-space grid; the 62% is an upper bound on
*designable* positions, not a real-patient breakpoint frequency), the reference position is unfavorable but a
majority pass a GC/complexity/parent-substring triage and yield balanced (~50% GC) in-band gapmer *and* siRNA
designs. Triage-passing is necessary but **not** sufficient: the gapmer the scan picks as in-band-best at the
worked 200/8 example actually carries the most off-target cleavage risks there, so a per-oligo BLAST screen
must follow the triage (§3a-ter/§3a-quater). So feasibility is
**breakpoint-conditional but breakpoint-selectable**: junction sequence-favorability is a tractable
selection step (sequence the patient's breakpoint, triage it, then BLAST-screen a favorable design), not a
roadblock — with the honest bounds that these breakpoints are *modelled, not exon-exact*, that "favorable"
is a GC/complexity triage rather than the full BLAST screen, and that clinical design must still be re-run
on each patient's sequenced breakpoint. We then specify what else is computable *now* without any GPU (extended
tiling and a breakpoint-keyed per-patient panel), and we are explicit that the genuinely unsolved problem is **tumour delivery**, which
we discuss only at the hypothesis level (e.g. a B7-H3-targeted antibody–oligonucleotide conjugate or a
receptor-targeted nanoparticle). We ask others to run one decisive experiment: junction-ASO versus
scrambled-control knockdown in patient-derived EMC lines (USZ-EMC [Bangerter]; NCC-EMC [Iwata]), with
specificity confirmed by sparing of the parental transcripts. The platform generalises to any
recurrent-fusion cancer with a defined breakpoint; EMC is the proof-of-concept entry indication.

---

## 1. Background and the fusion-selectivity rationale

EMC's defining lesion creates a chimeric transcription factor: the N-terminal low-complexity /
transactivation region of EWSR1 (a FET-family protein) fused to most of NR4A3 (NOR-1), an orphan member of
the NR4A nuclear-receptor subfamily [Sjögren; Panagopoulos]. *EWSR1::NR4A3* is the dominant variant;
*TAF15::NR4A3* accounts for a substantial minority, with rarer partners (TCF12, TFG, FUS) [Panagopoulos].
Critically, EMC otherwise carries **few recurrent secondary mutations** — a "quiet genome" — so the fusion
is, to a first approximation, the single clonal driver of the disease [Panagopoulos; and see the
EMC-program roadmap]. A therapy that neutralises the fusion transcript should therefore engage essentially
every tumour cell at baseline. This lowers *baseline* heterogeneity but does **not** guarantee the absence of
*acquired* resistance: downstream-pathway reactivation, delivery-driven heterogeneity of exposure, and — a
risk specific to a junction-targeted oligo — a **point mutation at or near the patient's breakpoint that
abolishes oligo complementarity** are all plausible escape routes. Clonality is an advantage, not a guarantee
of no escape.

**The central differentiator — why this paper exists alongside the degrader.** The repo's lead modality is
a PROTAC/molecular-glue degrader that engages the **NR4A3 ligand-binding domain** and recruits an E3 ligase
to remove the protein (see [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)). That LBD is retained
near-intact in the fusion, and its amino-acid sequence is **identical** to that of wild-type NR4A3. A
ligand that binds the fusion's LBD therefore cannot, in principle, distinguish the fusion from wild-type
NR4A3: the degrader is **NR4A3-selective but not fusion-selective**. The degrader paper handles this
honestly — its selectivity work is *paralogue* selectivity (NR4A3 vs NR4A1/NR4A2), not *fusion-vs-wildtype*
selectivity — and it is bounded by NR4A3's own tumour-suppressor roles (combined NR4A1/NR4A3 loss causes
AML [Mullican]; NR4A3 is tumour-suppressive in HCC/breast/lymphoma [Safe & Karki]). Removing wild-type
NR4A3 systemically is thus a real liability the degrader must manage.

The fusion **mRNA junction** dissolves this problem at the sequence level. The breakpoint seam — the few
nucleotides where the retained EWSR1 exon is spliced to the retained NR4A3 exon — is a contiguous sequence
that appears in **neither** parent transcript. An antisense oligonucleotide complementary to that seam, or
an siRNA spanning it, can engage the chimera while each wild-type mRNA matches only one half of the oligo.
This is the RNA-level expression of "fusion-unique": fusion-exclusivity **by sequence**, achieving exactly
the discrimination the LBD degrader cannot. The two modalities are complementary, not redundant — the
degrader removes the oncoprotein (and, accepting the liability, wild-type NR4A3 too); the junction ASO
removes only the chimeric transcript.

---

## 2. The approach: junction-spanning gapmer or siRNA

Two transcript-level mechanisms can exploit the junction; both require the active sequence to **straddle**
the breakpoint so that fusion-exclusivity is enforced by base-pairing.

**(a) RNase-H1 gapmer (lead).** A gapmer is a short oligo with a central DNA "gap" flanked by modified
"wings" (LNA — locked nucleic acid — or cEt — constrained ethyl). The wings raise affinity and nuclease
resistance; the DNA gap, once hybridised to the target, recruits endogenous RNase-H1 to cleave the RNA
strand [Crooke et al. 2021]. For fusion-exclusivity the central DNA gap must span the junction, because
RNase-H1 cleaves within the DNA:RNA duplex of the gap — so the cleaved bond sits across the tumour-specific
seam.

> **Where the discrimination really lives — a precise (and limiting) statement.** "A parent transcript
> matches only one wing" is *necessary but not sufficient*. RNase-H1 needs a contiguous DNA:RNA duplex of
> roughly ≥5–6 base pairs across the **gap** to cleave; the wings (LNA/cEt) do not support cleavage. So
> fusion-discrimination is set by how many junction-**unique** bases fall *inside the 6-nt catalytic gap on
> each side of the seam*, not by the whole 16-mer. The committed `specificity_margin` is computed oligo-wide
> (`min(bases_from_EWSR1, bases_from_NR4A3)` across all 16 nt), so it **overstates** true gap-level
> discriminating power, and the design only requires the junction to fall *somewhere* in the gap
> (`gap_start < j < gap_end`) — which permits a 1/5 split where one parent shares 5 of the 6 gap bases. The
> defensible design rule (a fix this red-team adopts going forward, see §3b) is to require the junction near
> the **gap centre** with ≥2–3 junction-unique bases on each side *within the gap*, and to treat the
> transcriptome off-target screen (§3a-bis/§3a-quater), not the oligo-wide margin, as the operative
> specificity filter. A parent transcript that happens to match the full gap plus a flank *can* be cleaved —
> which is exactly why the gap-mismatch-resolved off-target screen (§3a-quater) is the load-bearing analysis.

The committed designs (§3) use a 16-mer **5-6-5** LNA/DNA/LNA architecture; the design script's docstring
also references the common **5-10-5** gapmer layout as the standard 20-mer template [`junction_aso.py`].

**(b) Junction-spanning siRNA (parallel route).** An siRNA / shRNA whose guide strand is centred on the
junction loads into RISC and directs Ago2 cleavage of the chimeric mRNA. siRNA chemistry (2′-OMe / 2′-F,
phosphorothioate, and conjugation handles) is mature, and RISC tolerates the GC-rich seam differently from
RNase-H, so the siRNA route is a genuine fallback if gapmer chemistry proves intractable at this GC content
(§6). The selectivity logic is the same: the guide must cover the seam, and a single-nucleotide-resolved
seed mismatch against either parent transcript is what buys fusion-exclusivity. siRNA off-target
(seed-mediated) behaviour differs from ASO off-target behaviour, so the two routes need separate
specificity screens.

**Chemistry options (both routes).** Backbone phosphorothioate for stability/protein binding; sugar
modifications (LNA/cEt for gapmers; 2′-OMe/2′-F for siRNA); and — central to the unsolved delivery problem
(§3c) — conjugation handles (GalNAc is hepatocyte-directed and therefore *not* useful for a soft-tissue
sarcoma; a tumour-receptor-directed conjugate is what EMC would need).

---

## 3. Computational groundwork

### 3a. What already exists (real, committed output)

[`research/modalities/junction_aso.py`](../modalities/junction_aso.py) fetches the RefSeq CDS of *EWSR1*
(NM_005243) and *NR4A3* (NM_006981) from NCBI, builds the **modelled** fusion CDS at the canonical
protein-level breakpoint (EWSR1 kept to codon 264; NR4A3 retained from codon 2 — flagged in the output as
an assumption), and tiles 16-mer 5-6-5 gapmers whose central DNA gap spans the junction. It keeps only
oligos that (i) draw bases from **both** sides of the seam and (ii) are **not** a perfect complement of
either parent CDS. The committed result
([`junction-aso-designs.json`](../modalities/junction-aso-designs.json)) reports **5 fusion-specific
candidate gapmers** (`n_candidates = 5`, `n_fusion_specific = 5`), e.g. the top design antisense
`5′-ACGCAGGGCTGCTGCC-3′` (target mRNA `GGCAGCAGCCCTGCGT`, 8 bases from each side of the seam,
specificity margin 8). The modelled junction context is `…TACGGGCAGCAG|CCCTGCGTCCAA…`.

**The honest design caveat surfaces immediately and is reported as a real finding:** this junction is
**GC-rich**, with the top candidates at **75–81% GC** (75.0% and 81.2% across the five), well outside the
usual 40–60% gapmer comfort zone. None carry a G-quadruplex (≥4 consecutive G) motif (`has_G4_motif:
false` for all five), but the high GC alone implies elevated melting temperature, self-structure and
potential aggregation/tox risk that would require chemistry tuning (wing chemistry, length, or the siRNA
route). This is exactly the kind of constraint a design tool should expose up front; it is recorded here as
a real, committed result, not hidden.

> **Integrity flag (the breakpoint is modelled, and "canonical" is a label of convenience — not a validated
> clinical breakpoint).** The committed designs use a *modelled reference* breakpoint (EWSR1 kept to codon
> 264, NR4A3 from codon 2; the JSON marks `_breakpoint_model.assumption = true`). We call this position
> "canonical" only because it is the script default shared with the companion neoantigen work — **it is not a
> validated common patient junction.** Two honest consequences. (1) The codon-264 cut coincides with the
> EWSR1 1–264 IDR/transactivation boundary used elsewhere in this repo, i.e. it is a *protein-domain*
> landmark, not an observed mRNA breakpoint. (2) The **real** recurrent EMC junctions are exon-level and join
> **predominantly to NR4A3 exon 3** (the companion breakpoint-resolved work resolved EWSR1 exons 7/9/10/11/12/13
> → NR4A3 exon 3; [`novel-modalities.md`](./novel-modalities.md) §3.3), whereas "NR4A3 from codon 2" retains
> almost the entire NR4A3 CDS — so the *modelled* junction seam is not the seam of the commonly reported
> EWSR1 exon-7/12 :: NR4A3 exon-3 fusion ([citation to verify] for the rank-order of recurrent exon
> junctions). Neither off-target screen below has been run on that real exon-3 junction. The practical upshot
> is unchanged — every clinical design must be re-derived from the patient's **sequenced** fusion transcript
> (§3b) — but the reader should not read "canonical" as "the breakpoint patients actually carry." The five
> sequences are design hypotheses on a modelled seam, not a drug.

### 3a-bis. Off-target screen and siRNA route — now done for the modelled breakpoint (real, committed)

Three further CPU jobs were run on the modelled-breakpoint designs and committed as real outputs — a BLAST
gap-spanning off-target screen (i), a GC-tolerant siRNA route (ii), and an uncapped full-transcriptome
evaluation that also scores accessibility and siRNA-seed load (iii). Together they turn the abstract's GC
caveat into a quantified, honest verdict on *this* junction.

**(i) Transcriptome-wide off-target screen
([`junction-aso-offtarget.json`](../modalities/junction-aso-offtarget.json)).**
[`junction_aso_offtarget.py`](../modalities/junction_aso_offtarget.py) BLASTs each gapmer (blastn-short,
filter off) against human RefSeq RNA (`txid9606`) via the NCBI BLAST API and counts near-matches
(≥14/16 identical), flagging those that cover the central DNA gap (positions 6–11) — the
RNase-H-cleavable liability. **Of 5 gapmers, 4 returned** (one BLAST query transiently failed); **every
returned gapmer hit the HITLIST cap of 50 near-matches, and all 50 were classified gap-spanning**, so
`n_oligos_no_gap_spanning_offtarget = 0` of 5. The top candidate (`ACGCAGGGCTGCTGCC`) had 50 gap-spanning
near-matches spread across unrelated genes (e.g. *OTOG*, *SPTBN2*, *MAP3K13*, *SLC2A9*).

> **Over-call caveat (reported as honestly as the result).** The HITLIST was capped at 50 and the
> low-complexity filter was **off**, so on a GC-rich, low-complexity window like this junction the screen
> **over-calls** near-matches: the 50 figure is a floor / over-estimate in character, not an exact
> off-target count. The *qualitative* signal is nonetheless robust — these particular gapmers are
> **specificity-poor**: a GC-rich, low-complexity seam matches many transcripts at ≥14/16 identity, and
> gap-spanning matches are the most concerning class. This is predicted specificity, not validated; only the
> §4 wet-lab parental-/off-target-sparing controls can confirm it.

**(ii) GC-tolerant junction siRNA route
([`junction-sirna-designs.json`](../modalities/junction-sirna-designs.json)).**
[`junction_sirna.py`](../modalities/junction_sirna.py) designs junction-spanning 19-mer siRNA guides
(RISC/Ago2, GC window 30–52%) as the GC-tolerant fallback of §2b. It returns **5 fusion-specific guides,
but 0 pass all filters**, because the **minimum GC among the fusion-specific guides is 73.7%** — far above
the 30–52% target window. So the siRNA route **does not rescue** the GC problem at this breakpoint; the same
GC-rich seam that troubles the gapmer also disqualifies every siRNA guide.

**(iii) Full-transcriptome (uncapped) off-target + accessibility + siRNA-seed evaluation
([`aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json)).**
[`aso_insilico.py`](../modalities/aso_insilico.py) re-screens the same five canonical-breakpoint gapmers
against the **entire human RefSeq RNA transcriptome (GRCh38.p14; 186,185 transcripts)** downloaded in full —
an **uncapped, local** scan that removes the §3a-bis(i) HITLIST-50 over-call and yields true counts. It adds
two axes the BLAST screen does not: ViennaRNA target-site **accessibility** (potency) and an **siRNA
seed-region** off-target module. The picture it draws of the canonical junction is more nuanced than the
capped screen, and still negative on the bottom line:
- **True off-target counts are real, not a floor — and lower than the capped "50" suggested.** All five
  gapmers have **0 exact** transcriptome matches; their **≤1-mismatch** full-length counts are
  **8, 16, 17, 58, 95** (the two 81.2 %-GC designs are by far the worst, at 58 and 95). So the best canonical
  gapmer (`ACGCAGGGCTGCTGCC`) has only 8 near-complementary off-target sites genome-wide — but
  **`n_candidates_zero_offtarget = 0`**: none is clean, consistent with the canonical junction being
  unfavorable. (These are full-16-mer ≤1-mismatch hits, *not* gap-resolved, so like the BLAST screen they
  still over-count true RNase-H cleavage risk — the gap-resolution of §3a-quater is what separates cleavable
  from non-cleavable.)
  Two method bounds on "true counts": the seed-and-extend scan finds every ≤1-**substitution** off-target
  (the pigeonhole guarantee) but **not** 1-nt insertion/deletion (bulged) off-targets, and it counts
  **sense-strand transcript** matches only — the cleavage-relevant orientation — not genomic/antisense
  complementarity. "Uncapped true counts" should be read with those two scoping choices in mind.
- **Target site is moderately accessible** (mean unpaired probability **0.34–0.42** across the five) — i.e.
  potency is not obviously gated by mRNA structure at this junction; specificity, not accessibility, is the
  reference junction's problem. *Caveat:* this is a **local 180-nt fold** equilibrium proxy — it ignores
  long-range pairing that could sequester the site in the full transcript (so it can *over-estimate*
  accessibility) and is only a rough correlate of ASO potency (no kinetics, no in-cell protein occupancy);
  the 0.34–0.42 spread is within method noise and is **not** a meaningful potency ranking among the five.
- **The siRNA seed route carries its own, large liability, reported honestly:** only **2 of 5** designs
  present a guide seed that actually **straddles the junction** (the fusion-unique-seed goal), and the
  seed-match off-target load is enormous (**~21,000–119,000** transcriptome seed sites), because a GC-rich
  seed is intrinsically promiscuous. This is an independent reason the GC-rich canonical seam is hard for
  RISC, complementing the GC-window failure in (ii).

**Synthesis — feasibility is breakpoint-conditional, not modality-limited.** At the canonical *modelled*
breakpoint, the EWSR1::NR4A3 junction sequence is simultaneously **GC-rich and low-complexity**, and this
single property hurts three things at once: (i) gapmer chemistry (75–81% GC), (ii) siRNA GC (min 73.7%),
and (iii) predicted specificity (many gap-spanning off-targets). This is a property of **this junction
sequence**, not of the ASO/siRNA modality. Crucially, real patients carry **≥7 distinct in-frame
breakpoints** (the companion neoantigen work: EWSR1 exons 7/9/10/11/12/13 → predominantly NR4A3 exon 3;
[`novel-modalities.md`](./novel-modalities.md) §3.3), some of which are likely more favorable. The
conclusion is therefore that ASO/siRNA feasibility is **breakpoint-conditional**: designs must be re-run on
the patient's *sequenced* breakpoint, and junction sequence-favorability (GC content, complexity,
off-target load) becomes a **patient/breakpoint selection criterion**. This tempers but does not overturn
the route's standing — the *mechanism* (knockdown of an addicted fusion transcript) remains the most
mechanistically unambiguous of the fusion-exclusive routes (conditional on breakpoint, gated by delivery),
and the per-breakpoint scan below (§3a-ter) shows that a clear
majority of modelled breakpoints *do* yield in-band designs (triage-clean, not yet off-target-screened) — so the reference junction's poor
chemistry/specificity is a property of **that position**, not of the modality.

### 3a-ter. Per-breakpoint feasibility scan — favorability is a tractable selection step (real, committed)

The breakpoint-conditional hypothesis above makes a falsifiable prediction: if the canonical junction's
GC/specificity problem is a property of *that* position rather than of the modality, then sweeping the
breakpoint position should reveal many *other* positions whose junction is favorable. We tested this
directly. [`junction_breakpoint_scan.py`](../modalities/junction_breakpoint_scan.py) sweeps a grid of
**390 modelled in-frame breakpoints** (EWSR1 kept-length 200–300 codons × NR4A3 start 2–30 codons) and
triages each junction by junction-window GC (±10 nt), ±12 nt Shannon entropy, low-complexity repeat, and
whether a *fusion-specific* gapmer or siRNA exists with GC in the 40–60% comfort band. The committed result
([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)) **largely resolves the
breakpoint-conditional concern in the route's favor**:

- **243 of 390 modelled breakpoints (62%) are FAVORABLE** — i.e. a fusion-specific gapmer or siRNA exists
  with GC inside the 40–60% band. A clear majority of positions yield a chemically clean, specific design.
- The **canonical breakpoint (EWSR1 keep 264 / NR4A3 from 2) is NOT favorable**, exactly as the §3a / §3a-bis
  findings predicted: junction GC ±10 nt = **80%**, minimum gapmer GC **75.0%**, minimum siRNA GC **73.7%**,
  and **no in-band design** (`best_oligo: null`). The canonical position is genuinely a hard one.
- A **well-balanced in-band example** (EWSR1 keep 200 / NR4A3 from 8) has junction GC ±10 nt = **50.0%** and
  yields a fusion-specific 5-6-5 gapmer at **GC 50.0%** *together with* an in-band siRNA guide (**GC 52.6%**)
  — i.e. balanced GC/complexity on both routes. **Crucial caveat, and the paper's own thesis in miniature:**
  the gapmer the scan picks as 200/8's in-band best is `5′-GCTATACGGCTGTGTA-3′`, and the §3a-quater
  gap-resolved BLAST screen shows that exact oligo carries **29 true cleavage risks** — the *worst* of the
  five gapmers at this breakpoint. GC/complexity triage passing does **not** mean off-target-clean; the
  actually-clean designs at 200/8 are the slightly higher-GC `GGGCTATACGGCTGTG` (62.5%) and
  `AGGGCTATACGGCTGT` (56.2%) (§3a-quater). So 200/8 illustrates *both* halves of the thesis: breakpoint-level
  favorability (in-band on both routes) **and** the separate, decisive need for per-oligo off-target
  selection on top of it. (200/8 was chosen by hand as an in-band example on both modalities, not by the
  scan's `most_favorable` rank; that rank — EWSR1 204 / NR4A3 16, 35% junction GC — is an artifact of ranking
  by GC-extremity and in fact has **no** in-band gapmer at all (`best_gapmer_in_band_gc: null`), only a 42.1%
  siRNA, so it is less useful than 200/8 despite being the script's top-ranked "favorable.")

**Honest caveats on the scan (stated as plainly as the result):**

1. **These are MODELLED breakpoint positions** — a codon-space sensitivity sweep, not exon-exact clinical
   breakpoints. The 62% is a property of the swept grid, **not** a claim about how often real patients carry
   a favorable breakpoint; the companion exon work (EWSR1 exons 7/9/10/11/12/13 → predominantly NR4A3 exon 3;
   [`novel-modalities.md`](./novel-modalities.md) §3.3) is bracketed in codon space here, not mapped exon-exact.
2. **"Favorable" = passes a GC/complexity/parent-substring TRIAGE**, not the full transcriptome BLAST
   off-target screen of §3a-bis(i). A breakpoint chosen as favorable still owes that BLAST screen before any
   specificity claim.
3. **Real clinical design still needs the patient's actually-sequenced breakpoint** — the scan narrows the
   design space and shows favorable positions exist; it does not substitute for sequencing the patient's
   chimera.

**What the scan changes.** It converts the breakpoint-conditional caveat from a near-fatal-sounding risk
into a **tractable selection step**. The canonical junction is unfavorable, but it is one position out of
many; a clear majority of modelled breakpoints give balanced (~50% GC), fusion-specific designs on both the
gapmer and siRNA routes. The GC/specificity problem documented in §3a/§3a-bis is therefore a property of the
**canonical position**, not of the ASO/siRNA modality. The practical consequence is a concrete workflow:
sequence the patient's breakpoint, triage it with this scan, and — for a favorable hit — run the §3a-bis(i)
BLAST off-target screen on that specific design (triage alone is not enough — §3a-quater). This supports the
route's standing as the most mechanistically *unambiguous* of the fusion-exclusive options (gated by
delivery), with breakpoint-favorability now demonstrated to be selectable rather than a roadblock.

### 3a-quater. Two off-target screens on a favorable breakpoint — gap-resolved BLAST + uncapped full-transcriptome
We ran the full §3a-bis(i) off-target screen *directly on the favorable 200/8 breakpoint* (junction GC
50 %), then **resolved each near-match to the gap-mismatch level** — because RNase-H cleavage requires the
central DNA gap (the 6 nt the gapmer cleaves through) to be base-paired: a near-match whose mismatch falls
*inside* the gap is **predicted strongly disfavoured** for cleavage and is treated here as not a real
liability ([`junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json)).
This is informative, and positive — with one explicit assumption flagged below:
- **GC-triage alone is necessary but not sufficient**, and the coarse "gap-spanning" count *over-states*
  risk. Every near-match at this breakpoint is a weak **14/16** (2-mismatch) hit to a real gene
  (CSMD2, ADAMTSL2, DDR1, SLC66A1…), versus the reference junction's stronger 15/16 hits.
- **Once gap-mismatch position is resolved, 2 of the 5 gapmers carry no predicted cleavable off-target under
  a conservative all-gap-mismatch-blocks-cleavage assumption.** The gapmer (antisense) `5′-GGGCTATACGGCTGTG-3′`
  (62.5 % GC; target mRNA `CACAGCCGTATAGCCC`) has 21 off-target near-matches but **all 21 are gap-disrupted**
  (the mismatch lands in the DNA gap) → 0 predicted-cleavable; `5′-AGGGCTATACGGCTGT-3′` (56.2 % GC; target
  mRNA `ACAGCCGTATAGCCCT`) has a **single** off-target near-match, also gap-disrupted → 0 predicted-cleavable.
  The other three retain 15, 27 and 29 predicted cleavage risks.
- **The cleanliness rests on one assumption, stated plainly.** "Gap mismatch ⇒ no cleavage" is a *conservative
  heuristic*, not a measured fact: RNase-H1 tolerance of a single central mismatch is reduced but not
  guaranteed zero, and depends on mismatch identity/position and on flanking-duplex length [citation to
  verify for the quantitative gap-mismatch tolerance]. So "2 of 5 clean" is *predicted under this heuristic*,
  to be confirmed by the §4 assays — not an established off-target-free claim.
- So **per-oligo selection is as important as breakpoint selection**, and the deciding filter is the
  gap-mismatch-resolved off-target screen, not raw GC or raw near-match count.
- **An orthogonal, uncapped full-transcriptome screen confirms it — and more cleanly.** We re-ran the §3a-bis(iii)
  uncapped evaluation (full RefSeq, 186,185 transcripts; seed-and-extend) *on this same 200/8 favorable
  breakpoint* ([`aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json)).
  The contrast with the canonical junction is stark: **all 5 gapmers have 0 exact off-targets and 4 of 5 have
  0 near-perfect (≤1-mismatch) off-targets** transcriptome-wide (the fifth has just 1), where the *canonical*
  designs had 0 of 5 clean and 8–95 ≤1-mismatch hits. The two predicted-clean designs from the BLAST screen
  The siRNA-seed load also collapses at this breakpoint (the junction-straddling seed of `GCTATACGGCTGTGTA`
  matches **3,366** transcriptome sites, vs ~119,000 for the GC-rich reference seed). **The two screens agree
  where it counts but diverge elsewhere — and the divergence is instructive, not extra reassurance.** They
  agree on the two designs the BLAST screen calls clean (`GGGCTATACGGCTGTG`, `AGGGCTATACGGCTGT`): both also
  have zero ≤1-mismatch off-targets in the uncapped scan. But for the other three they *disagree sharply* —
  the uncapped scan reports `GCTATACGGCTGTGTA` and `GGCTATACGGCTGTGT` as 0 and 1 ≤1-mismatch off-target,
  while the gap-resolved BLAST flags those same two as **29 and 15** predicted cleavage risks. The reason is
  structural: the uncapped scan's ≤1-mismatch (≥15/16) cutoff **cannot see** the 14/16 (2-mismatch) hits that
  drive the BLAST cleavage-risk counts, so its "4 of 5 clean" is cleaner only because it uses a *stricter
  match threshold*, not because those oligos are safer. The defensible count is therefore the **2** designs
  that survive the *wider* ≤2-mismatch, gap-resolved test; the "4 of 5" holds only if 2-mismatch off-targets
  are deemed non-cleaving — the same heuristic flagged above.

**Reading.** At a favorable breakpoint, the full workflow — breakpoint triage → per-oligo BLAST →
gap-mismatch resolution, corroborated by an independent uncapped full-transcriptome screen — **yields gapmers
predicted off-target-clean** (a defensible **2 of 5** under the wider ≤2-mismatch gap-resolved test; up to 4
of 5 if 2-mismatch hits are deemed non-cleaving), a result the GC-rich reference junction could not offer. So
specificity looks **reachable** at the right breakpoint — *predicted*, not demonstrated. Honest bounds remain
and are load-bearing: the "clean" calls rest on the conservative gap-mismatch heuristic ([citation to verify]),
the breakpoint is *modelled* not patient-sequenced, and **delivery (§3c) is the separate, still-unsolved
gate.** We therefore call this route the most mechanistically *unambiguous* fusion-exclusive option —
knockdown of an addicted, fusion-only transcript, with no protein-conformation guesswork — **conditional on
breakpoint-favorability and gated by delivery.** That is a narrower and more defensible claim than "most
de-risked": the degrader's dominant risk (sparing wild-type NR4A3) differs in kind from the ASO's (delivery),
and neither is strictly more de-risked overall.

### 3b. What is specifiable now, without any GPU

All of the following are CPU-only and need no new GPU/compute run; they are specified, not executed, in
this draft:

1. **Expanded tiling, with a gap-centred specificity rule.** Re-run the existing tiler over a wider window
   and multiple oligo lengths (e.g. 14–20-mers) and both 5-6-5 and 5-10-5 architectures, to enumerate the
   full junction-spanning design space rather than the top-5 snapshot, and to find any lower-GC register that
   still straddles the seam. **Adopt the §2a fix:** require the junction near the **gap centre** with ≥2–3
   junction-unique bases on each side *inside the catalytic gap* (not the current "junction anywhere in the
   gap" rule), and report a **gap-level** discriminating margin rather than the oligo-wide
   `specificity_margin`, which overstates true discrimination.
2. **Genome-wide off-target complementarity screen (CPU) — DONE for the modelled breakpoint (§3a-bis i).**
   The current design-time check only confirms an oligo is not a *perfect* complement of the two parent
   CDSs; a real specificity claim requires a transcriptome-wide near-match search with gap-region weighting
   (RNase-H tolerates wing mismatches more than gap mismatches). **This has now been run** (blastn-short vs
   The current design-time check only confirms an oligo is not a *perfect* complement of the two parent
   CDSs; a real specificity claim requires a transcriptome-wide near-match search with gap-region weighting
   (RNase-H tolerates wing mismatches more than gap mismatches). **This has now been run** on both the
   modelled reference junction (poor — §3a-bis) and the favorable 200/8 junction (gap-resolved BLAST +
   uncapped full-transcriptome — §3a-quater). **The genuine remaining gap is the *real* clinical junction:**
   neither screen has been run on the commonly reported **EWSR1 exon-7/12 :: NR4A3 exon-3** fusion, because
   the design scripts model the breakpoint in codon space rather than mapping exons. Building the exon-exact
   real junction (via the companion `fusion_breakpoints.py` Ensembl exon structure) and re-running the full
   design→triage→screen pipeline on it is the most important specifiable next step — the 200/8 result shows
   the pipeline *can* find clean designs, but at a modelled position, not yet at a real one.

   **Per-breakpoint feasibility scan — DONE (§3a-ter), and the favorable-breakpoint screens are now DONE too
   (§3a-quater).** The sensitivity sweep over 390 modelled breakpoints has been run and committed
   ([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)); the reference position is
   unfavorable and in-band designs exist elsewhere. Both the gap-resolved BLAST screen and the uncapped
   full-transcriptome screen have since been run on the favorable 200/8 example (§3a-quater) — so the
   remaining specifiable items are the **real exon-3 junction** designs (above) and the gap-centred re-tiling,
   not "run a screen on a favorable breakpoint."
3. **siRNA alternative (computable) — DONE for the modelled breakpoint (§3a-bis ii).** Junction-spanning
   19-mer siRNA guides have now been generated (asymmetry/end-stability/run filters); at this breakpoint 0
   of 5 pass (min GC 73.7%), so the GC-tolerant route does not rescue this junction. Seed off-target
   counting against the transcriptome remains specifiable for any breakpoint that yields in-window-GC guides.
4. **Breakpoint heterogeneity → a per-patient panel.** Because EMC breakpoints vary by exon usage (the
   companion neoantigen work resolved *7 distinct in-frame junctions* across EWSR1 exons 7/9/10/11/12/13 →
   predominantly NR4A3 exon 3; see [`novel-modalities.md`](./novel-modalities.md) §3.3), the ASO sequence
   is **breakpoint-conditional**. The deployable artifact is therefore not one oligo but a *panel*:
   key each patient's design to their sequenced breakpoint, exactly as the script already supports by
   re-running on the patient transcript. The per-breakpoint scan (§3a-ter) now shows this panel is largely
   tractable — a clear majority of modelled breakpoints yield clean in-band designs — so favorability is a
   selection step, not a roadblock. This is a feature of the modality, not a bug — it mirrors the
   personalised logic the immunotherapy route reached independently.

### 3c. The honest hard part — tumour delivery (unsolved)

Oligonucleotide *design* is tractable; **delivery to an EMC tumour is not**, and this is stated plainly as
the limiting problem. Systemically administered naked gapmers distribute to liver/kidney; GalNAc
conjugation (the one solved targeting handle) is hepatocyte-directed and useless for a soft-tissue sarcoma.
Options below are **hypotheses, explicitly flagged**, not validated approaches — and they are listed in
*increasing* order of how much they depend on an unknown:

- **Local / intratumoural administration** for accessible lesions, sidestepping systemic targeting entirely
  — the only delivery hypothesis here that needs **no** EMC-specific surface marker, and therefore the most
  tractable first-in-human setting. (Promoted to the top because the receptor-targeted routes below all
  depend on an input that does not yet exist.)
- **Receptor-targeted antibody–oligonucleotide conjugate (AOC).** Couple the gapmer/siRNA to an antibody
  against a surface antigen enriched on EMC cells. The honest status of the one antigen we can even name:
  **B7-H3 (CD276)** is broadly over-expressed across *many* sarcoma subtypes, but its expression **in EMC
  specifically is unknown** — there is, to our knowledge, no EMC expression study, so naming it here is an
  *extrapolation from other sarcomas*, not evidence [citation to verify]. An EMC immunohistochemistry / RNA-seq
  survey is a prerequisite before B7-H3 (or any antigen) can be treated as an EMC delivery handle. AOC
  platforms exist in other indications but none is established for EMC.
- **Receptor-/ligand-targeted nanoparticle (LNP or polymer).** Encapsulate the oligo and decorate with a
  ligand for an EMC-enriched receptor. The specific EMC-enriched receptor is, again, the unsolved input
  [citation to verify].
No delivery claim is made; this section exists to mark delivery as the dominant risk, not to assert a
solution.

---

## 4. The decisive experiment we ask others to run

Computation cannot establish that junction silencing kills EMC cells, nor confirm parental sparing in a
living transcriptome. The single decisive, wet-lab-doable experiment is:

**Junction-ASO vs. scrambled-control knockdown in patient-derived EMC lines.** Transfect (or free-uptake /
gymnose) the committed candidate gapmers — and a junction-spanning siRNA — into **USZ-EMC** [Bangerter] and
**NCC-EMC** [Iwata], against a scrambled/mismatch control matched for length and GC. Read out:

1. **On-target knockdown** of the fusion transcript (junction-spanning qPCR / RNA-seq across the breakpoint)
   and of fusion protein.
2. **Specificity — the crux:** wild-type *EWSR1* and wild-type *NR4A3* transcripts must be **spared**
   (allele/exon-resolved or junction-discriminating assays), confirming the oligo silences only the chimera.
3. **Phenotype:** viability/proliferation/apoptosis, to test whether the cells are addicted to the fusion
   transcript.

**The controls matter as much as the readouts — and an EMC line alone cannot prove fusion-exclusivity.** A
scrambled control tests only sequence-independent toxicity; it does *not* test fusion-vs-wildtype
discrimination. Two further controls are required to make the claim. (a) **A setting where wild-type NR4A3 is
abundantly expressed** — in EMC cells wild-type *NR4A3* may be minimally expressed, so "sparing" cannot be
demonstrated where the wild-type transcript is near-absent; the discriminating test is a **fusion-negative
cell engineered to express the fusion** (or an isogenic fusion knock-in/parental pair) carrying *both* the
chimera and abundant wild-type *NR4A3*/*EWSR1*. (b) **Single-parent-targeting positive controls** — ASOs
against wild-type *EWSR1* or *NR4A3* alone — to prove the assays can detect wild-type knockdown when it
occurs, so that "spared" is a real negative and not an insensitive assay. The phenotype arm likewise needs a
**fusion-negative line** to separate fusion-knockdown lethality from generic oligo toxicity. With these
controls the experiment converts five sequences and a mechanism into evidence; without them it can show
on-target knockdown and EMC-cell killing but cannot *prove* the wild-type transcripts are spared. It needs no
new molecule beyond synthesising the listed oligos and the engineered/isogenic models above.

---

## 5. Selectivity and safety

- **Fusion-exclusive by sequence — and the discrimination lives in the catalytic gap.** The active oligo
  spans the breakpoint; selectivity is enforced by base-pairing, not by protein conformation. The precise
  (and limiting) condition is that the **6-nt DNA gap** straddle the junction with junction-unique bases on
  each side: "a parent matches only one wing" is necessary but not sufficient (a parent matching the full gap
  plus a flank could still be cleaved). This is why the gap-mismatch-resolved off-target screen, not the
  oligo-wide specificity margin, is the operative filter (§2a, §3a-quater).
- **Spares wild-type NR4A3 — and therefore avoids the tumour-suppressor liability the degrader carries.**
  This is the key safety advantage over the LBD degrader. Because the junction is absent from wild-type
  *NR4A3*, the oligo does not touch the wild-type transcript, side-stepping the AML risk of combined
  NR4A1/NR4A3 loss [Mullican] and the HCC/breast/lymphoma tumour-suppressor roles of NR4A3 [Safe & Karki].
- **Spares wild-type EWSR1.** EWSR1 is a broadly expressed FET-family gene with essential functions; a
  junction oligo leaves the wild-type *EWSR1* transcript intact, matching only one wing.
- **Residual risks remain and must be tested, not assumed away:** sequence-based off-target hybridisation
  elsewhere in the transcriptome (the §3b CPU screen is the in-silico filter; only the wet-lab experiment
  is proof), and chemistry-class / phosphorothioate effects (hepatotoxicity, complement, platelet effects)
  that are generic to oligonucleotide drugs [Crooke et al. 2021]. Predicted specificity is a screen, not a
  guarantee (§6).

---

## 6. Limitations

- **GC-rich chemistry.** The modelled junction yields 75–81% GC gapmers — outside the comfort zone; high Tm
  and self-structure risk would need chemistry tuning, an alternative register, or the siRNA route (§2b).
  This is a real, committed finding, not a hypothetical.
- **Poor predicted specificity at the modelled reference breakpoint.** The BLAST off-target screen (§3a-bis i)
  found **0 of the 4 successfully screened** gapmers free of gap-spanning near-matches (the 5th BLAST query
  failed), and the GC-tolerant siRNA route did not rescue it (0 of 5 guides pass; min GC 73.7%, §3a-bis ii).
  Two honest qualifiers on the BLAST number: it is over-called (HITLIST capped at 50, low-complexity filter
  off, on a low-complexity GC-rich window), **and** — unlike the favorable-breakpoint run — it was scored
  coverage-only, *not* gap-mismatch-resolved, so its "0 clean" is an upper-bound-on-risk count not strictly
  comparable to the §3a-quater 200/8 BLAST screen. The **load-bearing** negative is therefore the
  **uncapped, true-count** full-transcriptome re-screen (§3a-bis iii): all five gapmers have 0 exact matches
  and **8–95 ≤1-mismatch** off-targets, `n_candidates_zero_offtarget = 0`. On that defensible footing the
  reference junction is specificity-poor. That same evaluation also flags a large siRNA-seed off-target load
  (~21k–119k seed sites; version-dependent point estimates) for the GC-rich seam.
- **Breakpoint-conditional — a tractable selection step, not a roadblock.** Feasibility (chemistry GC,
  siRNA GC, predicted specificity) is a property of the *junction sequence*, not of the modality, and the
  modelled reference junction is genuinely unfavorable. The per-breakpoint scan (§3a-ter) shows
  **243 of 390 modelled breakpoints (62%) pass a GC/complexity/parent-substring triage** and yield in-band
  designs — so junction-favorability is a *selectable* criterion, not a fatal flaw. But the reassurance is
  bounded harder than the bare "62%" implies: (i) the 390 are an **arbitrary codon-space grid** with
  hand-chosen thresholds, so 62% is an **upper bound on *designable* positions, not a real-patient breakpoint
  frequency**; (ii) "favorable" requires only that a triage-passing in-band design *exists* — and triage is
  **not** the off-target screen (the 200/8 worked example shows the scan's own in-band pick failing the BLAST
  screen, §3a-ter/§3a-quater); and (iii) **neither off-target screen has been run on the real, commonly
  reported EWSR1 exon-7/12 :: NR4A3 exon-3 junction** — only on modelled codon-space positions — so the whole
  favorability narrative still owes a run on the real clinical seam (§3b.2). Every clinical design must be
  re-derived from the patient's *sequenced* fusion transcript.
- **Delivery unsolved.** No validated tumour-delivery route for EMC exists; §3c lists hypotheses only. This
  is the dominant risk for the whole modality.
- **Knockdown, not knockout.** ASO/siRNA reduce transcript; they do not eliminate the gene or guarantee
  durable, complete loss of fusion protein. Depth and duration of knockdown are empirical.
- **"Predicted clean" rests on a conservative heuristic, and on a margin metric that overstates.** The
  favorable-breakpoint "clean" calls (§3a-quater) assume any mismatch inside the 6-nt gap abolishes RNase-H
  cleavage — a conservative rule, not a measured fact [citation to verify], and the two screens that
  implement it disagree at the per-oligo level for the non-clean designs (§3a-quater). Separately, the
  committed `specificity_margin` is computed oligo-wide and **overstates** true gap-level discrimination
  (§2a); a gap-centred margin and gap-centred design rule are the fix (§3b.1).
- **Predicted specificity ≠ validated specificity.** The transcriptome-wide near-match screens have been
  **run** (modelled reference junction: poor; favorable 200/8: 2–4 of 5 predicted clean) but remain
  *in-silico* — and the reference-junction BLAST number is over-called and coverage-only (§6, above). Only the
  §4 wet-lab experiment, with the controls specified there, can confirm parental and off-target sparing in
  cells.
- **No molecule, no clinical claim.** This is a computation-only, publish-to-convince draft. Nothing here
  has been tested in a patient.

---

## 7. Broader indications

The junction-ASO concept is a **platform**, not an EMC-only tactic: it applies to **any recurrent-fusion
cancer with a defined, sequenced breakpoint**, because the only requirement is a tumour-specific mRNA seam
absent from both parent transcripts. Natural extensions include other **FET-family / EWSR1-fusion
sarcomas** (the EWSR1-rearranged sarcoma spectrum more broadly), where the same design-and-screen pipeline
([`junction_aso.py`](../modalities/junction_aso.py) plus the §3b CPU off-target screen) applies with only
the breakpoint sequence changed. EMC is the proof-of-concept entry indication precisely because it is the
cleanest case — a quiet genome with a single near-clonal fusion driver — so a positive parental-sparing
knockdown result here is the strongest possible demonstration that the platform discriminates fusion from
wild-type at the RNA level. *(Specific partner cancers beyond the EWSR1/FET family are not enumerated here
to avoid over-claiming; each would need its own breakpoint sourcing — [citation to verify] per indication.)*

---

## 8. Keeping this paper current — method-watch

This route's progress is **method-gated**: specific next steps unlock the moment an enabling technology
becomes usable. Those gates are watched automatically by the repo's **method-watch** (monthly cron +
on-demand: [`scripts/method-watch.mjs`](../../scripts/method-watch.mjs),
[`.github/workflows/method-watch.yml`](../../.github/workflows/method-watch.yml); digest published to the
`method-watch-cache` branch). The capability → action trigger table lives in
[`research/method-watch.md`](../method-watch.md); the rows specific to this paper are:

- **ASO off-target / RNase-H cleavage-activity predictor** → retire the conservative "gap-mismatch ⇒
  non-cleaving" heuristic (§3a-quater) and re-grade predicted specificity with a calibrated model.
- **ASO/siRNA efficacy + target-site-accessibility predictor** → re-rank the junction designs for potency
  and replace the local-fold accessibility proxy (§3a-bis iii).
- **New patient-derived EMC / FET-fusion-sarcoma model** (cell line / organoid / PDX) → unblocks the
  decisive knockdown + parental-sparing experiment (§4) and a fusion-dependence readout.
- **In-silico oligo/nanoparticle tumour-delivery predictor** → score a targeted junction-siRNA/AOC and
  re-grade the route's dominant gate, delivery (§3c).

A digest "🆕" that crosses one of these is a prompt to update the cited section here, not an automatic edit.

---

## References

Verified reference pool (appear verified in the repo):

- **Sjögren H, et al.** *EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma.* (EMC defining fusion.)
- **Panagopoulos I, et al.** *Fusion variants and partners in EMC* (incl. TAF15, TCF12, TFG, FUS).
- **Crooke ST, et al.** *Antisense technology: an overview and prospectus.* **Nat Rev Drug Discov** 2021.
  doi:10.1038/s41573-021-00162-z. (Antisense / gapmer / RNase-H1 mechanism overview.)
- **Bangerter, et al.** USZ-EMC patient-derived EMC model (2023).
- **Iwata S, et al.** NCC-EMC patient-derived EMC cell lines.
- **Mullican SE, et al.** *Abrogation of Nr4a3 and Nr4a1 leads to acute myeloid leukemia.* **Nat Med** 2007.
  (Wild-type NR4A1/NR4A3 loss → AML — the tumour-suppressor liability the junction ASO avoids.)
- **Safe S, Karki K.** *The paradoxical roles of orphan nuclear receptor 4A (NR4A) in cancer.* **Mol Cancer
  Res** 2021. (NR4A3 tumour-suppressor roles in HCC/breast/lymphoma.)
- **Le Guilloux V, Schmidtke P, Tufféry P.** *Fpocket.* **BMC Bioinformatics** 2009. (Referenced for the
  companion structural/degrader work; not used in this RNA-level analysis.)
- **Varadi M, et al.** *AlphaFold Protein Structure Database.* **Nucleic Acids Res** 2022.
  doi:10.1093/nar/gkab1061. (Referenced for the companion structural work; not used here.)

To verify (do **not** treat as established until sourced):

- B7-H3 (CD276) surface expression in EMC specifically — **[citation to verify]** (broadly expressed across
  other sarcomas, but no EMC-specific study is known to us; §3c states this).
- EMC-enriched surface receptor(s) suitable for AOC / targeted-nanoparticle delivery — **[citation to verify]**.
- Rank-order of recurrent EMC exon junctions (the commonly reported **EWSR1 exon-7/12 :: NR4A3 exon-3**
  fusion) — **[citation to verify]**; the in-repo companion ([`novel-modalities.md`](./novel-modalities.md)
  §3.3) resolves EWSR1 exons 7/9/10/11/12/13 → predominantly NR4A3 exon 3 from Ensembl exon structure.
- Quantitative RNase-H1 tolerance of a single **gap-internal** mismatch (the basis of the "gap mismatch ⇒
  non-cleaving" heuristic used in §3a-quater) — **[citation to verify]**.
- Specific non-EWSR1/FET recurrent-fusion cancers as platform extensions — **[citation to verify]** per indication.

**Reproducibility.** The real results cited here are committed CPU outputs (snapshotted on the main branch;
refreshed by GitHub Actions on the `modalities-cache` branch):

- [`junction-aso-designs.json`](../modalities/junction-aso-designs.json) — 5 junction-spanning 5-6-5 gapmer
  designs, from [`junction_aso.py`](../modalities/junction_aso.py).
- [`junction-aso-offtarget.json`](../modalities/junction-aso-offtarget.json) — NCBI BLAST API (blastn-short
  vs RefSeq RNA) gap-spanning off-target screen of the canonical designs, from
  [`junction_aso_offtarget.py`](../modalities/junction_aso_offtarget.py) (HITLIST-capped at 50; over-calls).
- [`aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json) — **uncapped** full-RefSeq
  (186,185-transcript) off-target screen + ViennaRNA accessibility + siRNA-seed module of the canonical
  designs, from [`aso_insilico.py`](../modalities/aso_insilico.py).
- [`junction-sirna-designs.json`](../modalities/junction-sirna-designs.json) — junction siRNA route, from
  [`junction_sirna.py`](../modalities/junction_sirna.py).
- [`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json) — 390-breakpoint GC/
  complexity/parent-specificity triage sweep, from
  [`junction_breakpoint_scan.py`](../modalities/junction_breakpoint_scan.py).
- [`junction-aso-offtarget-bp200-8.json`](../modalities/junction-aso-offtarget-bp200-8.json) and its
  gap-mismatch-resolved companion
  [`junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json) —
  the BLAST off-target screen re-run on the favorable EWSR1-keep-200 / NR4A3-from-8 breakpoint, resolved to
  true RNase-H cleavage risk, from [`junction_aso_offtarget.py`](../modalities/junction_aso_offtarget.py).
- [`aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json) — the
  **uncapped** full-RefSeq off-target + accessibility + siRNA-seed evaluation re-run on the same favorable
  breakpoint (4 of 5 gapmers with zero ≤1-mismatch off-targets), from
  [`aso_insilico.py`](../modalities/aso_insilico.py) (breakpoint-parameterised via env).

No GPU computation was performed for this draft.
