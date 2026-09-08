# U1 — What `emc-fusion-frame-fig1` actually renders

Worker U1, EMC capacity campaign, paper lane. Read-only. Nothing shared was written.

## 0 · Image identity and session state

| item | value |
|---|---|
| path | `research/manuscripts/figures/emc-fusion-frame-fig1.png` |
| bytes | 360,656 |
| sha256 | `fa94675f436692344f5514ac1d08f7d448b5ebdbae4ac16fe3a8572597eb07a7` |
| PNG header (read from the file) | 2220 x 2670, 8-bit, colour type 6 (RGBA), non-interlaced |
| companion | `emc-fusion-frame-fig1.pdf`, 83,262 B, sha256 `0d9aff26ec469e669a6ee1a6e310eaf9f3f808b3a8f4f18f9410d39e30148701` |

Start: `date -u` = 2026-09-08T11:38:13Z; `git rev-parse HEAD` = `b4be8881c14553fb8203b698a0defcb5fe291d71`;
`git status --porcelain` = empty.

**Method.** I opened the PNG with the Read tool (full page, downscaled by the tool to 1663x2000), then
decoded the PNG myself in pure Python (zlib only; no PIL, ImageMagick or pdftotext in this
environment) to cut three native-resolution crops and Read each of them at 2x. Every quoted string
below was read from rendered pixels at 2x native scale. The PDF was **not** needed and was not used
for any content claim.

Retained inspection evidence in this lane: `panelA_top.png`, `panelB_zoom.png`, `panelC_top.png`,
`pdf_streams.bin` (an abandoned PDF-text-extraction attempt: the PDF uses subset fonts with `TJ`
glyph arrays and no `ToUnicode`, so it yielded zero readable strings — recorded so nobody repeats it).

## 1 · What is rendered

The figure has **three panels, A / B / C**, stacked vertically, bold single-letter labels at the upper
left of each. No panel is missing and there is no panel D.

### Panel A — protein-scale bar diagram

Two blocks separated by a horizontal dotted rule.

**Upper block: three wild-type proteins.** Horizontal light-grey bars, left-aligned at residue 0,
row labels at left in black, an annotation at the right end of each bar in black:

| row label | right-hand annotation |
|---|---|
| `EWSR1` | `30 RG` |
| `TAF15` | `31 RG` |
| `NR4A3` | `2 RG` |

- Thin vertical black lines are drawn inside the EWSR1 and TAF15 bars at irregular, clustered
  positions. **The figure never says what these ticks are.** Their count and clustering are
  consistent with RG-dipeptide positions, but that is my inference from the `30 RG` / `31 RG`
  annotations, **not** a rendered label. There is **no key or legend anywhere in the figure.**
- Dashed black rectangles overlay parts of the bars: **two** on EWSR1 (one narrow, around residues
  ~295–330; one long, around ~455–640) and **one** on TAF15 (around ~325–570). **These dashed boxes
  are unlabelled.** Nothing in the figure names them (RGG1/RGG2/RGG3, "RGG domain", or otherwise).
  This is the single largest legend gap in the figure.
- The NR4A3 bar is subdivided by shading into a light region, a mid-grey block and a dark-grey block
  (the dark block is itself split by an internal vertical line). Three grey labels sit **below** the
  bar: `AF-1`, `C4 zinc finger`, `ligand-binding domain`. **No numeric domain boundaries are
  printed**; boundary residues can only be estimated off the shared axis and I do not state them as
  read values.
- `C166` is printed in black **above** the NR4A3 bar with a short black tick on the bar at
  approximately residue 166. Read at 2x, the tick is unambiguously on the **NR4A3** bar, not on
  TAF15. So **C166 is an NR4A3 residue annotation**, despite the label sitting in the whitespace
  between the TAF15 and NR4A3 rows.

**Lower block, headed by the italic grey label `retained 5' segment`: seven fusion constructs.**
Each is a bar starting at residue 0 and terminating at a heavy vertical end-cap, with a grey
annotation to the right. Read verbatim:

| row label | grey annotation |
|---|---|
| `EWSR1::NR4A3 type 1` | `EWSR1(1-431), 8 of 30 RG` |
| `EWSR1::NR4A3 type 2` | `EWSR1(1-264), 0 of 30 RG` |
| `EWSR1::NR4A3 type 5` | `EWSR1(1-472), 11 of 30 RG` |
| `TAF15::NR4A3` | `TAF15(1-161), 0 of 31 RG` |
| `EWSR1::ATF1, exon 8` | `EWSR1(1-324), 7 of 30 RG` |
| `EWSR1::ATF1, exon 10` | `EWSR1(1-348), 8 of 30 RG` |
| `EWSR1::FLI1, type 1` | `EWSR1(1-264), 0 of 30 RG` |

**Axis (shared by both blocks):** a single horizontal axis at the bottom of Panel A, ticks and labels
`0 100 200 300 400 500 600 700`, axis title `residue`. Units: amino-acid residues. Note the axis
carries **no** RG-count scale — the RG counts appear only as text annotations.

**Scope of Panel A:** wild-type EWSR1, TAF15 and NR4A3 plus seven fusion 5'-segments. TCF12 does
**not** appear in Panel A.

### Panel B — one-dimensional dose axis, three stacked rows

**Axis:** horizontal, ticks `0.00 0.25 0.50 0.75 1.00`, axis title read verbatim:
`retained RG dipeptides, as a fraction of the 5' partner's wild-type total`. Dimensionless fraction.

Two grey anchor captions sit just above the axis line, at the two ends:
`fusion reference construct` (left) and `native EWSR1 and the three-domain add-back` (right).

Rows, top to bottom, with their grey left-hand labels read verbatim:

1. `measured in reference 1` — a hatched (diagonal-fill) rectangle spanning the **full** axis 0.00 to
   1.00, with a filled black circle at 0.00 and a filled black circle at 1.00. Grey annotation
   centred above it: `one-domain add-back construct: position on this axis not determinable`.
2. `reported EWSR1::ATF1 breakpoints` — a heavy horizontal bar from 0.00 to about 0.27 with terminal
   end-caps and one interior tick at about 0.233. Black annotation to its right:
   `0.000 to 0.267; the breakpoint of the measured construct is not stated`.
3. `computed here, EMC fusions` — three open (unfilled) triangle markers on the axis, each with a
   black label above it: `type 2 and TAF15::NR4A3` at 0.00, `type 1` at about 0.267, `type 5` at
   about 0.367.

**Scope of Panel B:** the recruitment dose axis only. **TCF12 does not appear.** No composition,
prefix-sweep or hydropathy quantity appears.

### Panel C — nucleotide-level seam schematic (no numeric axis)

A single horizontal composite bar, left to right:

- a plain light-grey segment, labelled above:
  `EWSR1 exon 7,` / `coding through nt 793`
- a **dotted-fill** segment (the long middle), labelled above:
  `NR4A3 exon 2, 174 nt,` / `untranslated in NR4A3`
- a very narrow cross-hatched sliver, labelled above with a leader line: `2 nt of exon 3`
- a plain mid-grey segment to the right, labelled above:
  `NR4A3 coding sequence,` / `from its own initiator`

Below the bar, a comb of short vertical ticks (codon boundaries) spans from a leader that starts
**one nucleotide before** the dotted segment to the end of the cross-hatched sliver. Two black
captions under the comb:

- left, with a leader to the comb's start: `one nucleotide donated by EWSR1`
- right: `59 codons, 177 nt, no internal stop codon`

Below that, black text:

`residues 265 to 323 of the chimeric protein, read in the EWSR1 frame:`

then the sequence on two lines, in a monospaced face:

```
KPTAEEGSPASPGPEPGPLAVPGSTAGASP
RRTSAPPTLSASAGETPSPTIQRARYPPD
```

(30 + 29 = 59 residues, consistent with "59 codons" and with 323 − 265 + 1 = 59.)

**Panel C has no axis and no scale bar.** The segment widths are schematic, not proportional — the
"2 nt of exon 3" sliver is drawn far wider than 2/177 of the dotted segment.

**Panel C never names the fusion type.** It says "EWSR1 exon 7", which is the type-2 junction, but
the string "type 2" does not appear in Panel C. This is exactly the scope clause U2 was told the
caption needs, and the pixels confirm it is genuinely absent from the figure.

### Illegible / absent items — stated as such

- **Nothing in this figure is illegible.** At 2x native crop every glyph resolved. I mark no text as
  unreadable.
- What is **absent**, not illegible: any legend/key; any label for the dashed boxes in Panel A; any
  label for the thin vertical ticks in Panel A; numeric domain boundaries for NR4A3; any scale in
  Panel C; any statistical annotation, error bar or n anywhere.
- Panel A domain-boundary residues and the exact Panel B marker positions are **estimated off the
  axis by eye**, not printed. I give them as approximations and flag them as such.

## 2 · Proposed caption and panel map

Written to match the pixels. Bracketed items are the decisions the figure forces on whoever adopts it.

> **Figure 1. Composition of reported EMC fusion proteins and the nucleotide register of the type-2
> junction.**
> **(A)** Domain and RG-dipeptide maps drawn on a shared residue axis (0–700 aa). Top: wild-type
> EWSR1, TAF15 and NR4A3; vertical ticks inside the EWSR1 and TAF15 bars mark RG dipeptides, and the
> total for each protein is given at the right (30, 31 and 2 RG respectively). Dashed outlines mark
> the RGG-rich regions of EWSR1 (two) and TAF15 (one). *[ADOPTER MUST CONFIRM: the figure does not
> label the dashed boxes; whoever inserts it must either state in the caption what they are or add a
> key. Do not assert RGG1/RGG2/RGG3 boundaries the figure does not print.]* NR4A3 shading marks the
> AF-1 region, the C4 zinc finger and the ligand-binding domain, and the tick above the NR4A3 bar
> marks C166. Bottom, below the dotted rule: the 5' segment retained in each of seven fusion
> constructs, each bar ending at its breakpoint, annotated with the retained residue range and the
> retained RG count out of the 5' partner's wild-type total.
> **(B)** The same RG content expressed as a fraction of the 5' partner's wild-type total, the axis
> on which the published recruitment-dose argument is made. Top row, measured in reference 1: the
> two firmly measured positions are the fusion reference construct (0.000) and native EWSR1 together
> with the three-domain add-back (1.000); the one-domain add-back cannot be placed, so it is drawn as
> a hatched band across the whole axis rather than as a point. Middle row: reported EWSR1::ATF1
> breakpoints span 0.000 to 0.267, and the breakpoint of the construct actually measured is not
> stated in the source. Bottom row, open triangles: the EMC fusions computed here — EWSR1::NR4A3
> type 2 and TAF15::NR4A3 at 0.000, type 1 at 0.267, type 5 at 0.367. These are computed positions,
> not measurements.
> **(C)** Nucleotide register of the EWSR1 exon 7 to NR4A3 exon 2 junction, that is the type-2
> fusion; the panel is schematic and not drawn to scale. EWSR1 coding sequence runs through exon 7 to
> nucleotide 793, one base into a codon, so one nucleotide is donated across the seam. The 174 nt of
> NR4A3 exon 2 and the first 2 nt of exon 3, both untranslated in NR4A3, are read in the EWSR1 frame:
> 1 + 174 + 2 = 177 nt = 59 codons, with no internal stop, before NR4A3 coding sequence resumes at its
> own initiator. The inserted 59 residues are residues 265 to 323 of the chimeric protein and their
> sequence is given below the schematic. Panel C shows one junction only; it is not a claim about
> types 1 or 5.

**Panel map for the changelog's cross-references.**

| changelog / R1 reference | resolves to | verdict |
|---|---|---|
| "Figure 1B (the axis)" | Panel B, the fraction-of-wild-type-RG dose axis | **correct** |
| "Figure 1C (the seam)" | Panel C, the EWSR1 e7 / NR4A3 e2 nucleotide seam | **correct** |
| "one scope clause … in the Figure 1 caption naming type 2" | needed for **Panel C**, which renders the type-2 junction without ever printing "type 2" | **required, and the figure confirms the need** |
| no changelog reference at all | **Panel A** | Panel A is uncited by the changelog and needs a caption written from scratch — done above |

## 3 · Check of R1's arithmetic and references against the pixels

**177 nt / 59 codons, or 176, or neither?**

The figure renders **177**, in the string `59 codons, 177 nt, no internal stop codon`. It also renders
`174` (exon 2) and `2 nt of exon 3` and `one nucleotide donated by EWSR1`. It does **not** print the
number 176 anywhere.

R1's package (`PROPOSED-emc-atr-collaborator-package.md` L169–170) says the junction "places 177
nucleotides in the EWSR1 reading frame … one donated by EWSR1 across the seam and 176 supplied by
NR4A3, of which 174 come from exon 2 and 2 from exon 3." Against the pixels: 1 + 174 + 2 = 177, and
174 + 2 = 176. **R1's 177-vs-176 arithmetic agrees with the figure exactly. There is no 177/176
conflict — they are two different quantities (total in-frame insert vs. the NR4A3-supplied part), and
both are correct.** R1's §3.3 statement that the mRNA carries "176 nucleotides of NR4A3 5'
untranslated sequence" is likewise consistent: the figure marks the 2 nt of exon 3 as lying *before*
the NR4A3 initiator.

Two further R1 numbers that the figure independently corroborates: "nucleotide 793 … 264 complete
codons and one base over" (793 = 3x264 + 1; Panel C prints `coding through nt 793`, and Panel A prints
`EWSR1(1-264)` for type 2), and the 59-residue insert (Panel C prints `residues 265 to 323`, and the
printed sequence is 30 + 29 = 59 residues).

**Does the figure depict the frame rule?** **No — only one instance of it.** Panel C shows the single
type-2 junction: the one donated nucleotide and a 174 nt (multiple-of-three) acceptor exon. It never
prints the rule R1 states — "in frame if and only if the donor exon ends one nucleotide into a codon,
that is if its cumulative coding nucleotide count is congruent to 1 modulo 3" — and it shows no other
junction. **MISMATCH, precisely: a caption or text that cites Figure 1 as showing the frame rule
would overclaim. Figure 1C illustrates one case of the rule; it does not establish or display it.**

**Does the figure depict the phase-1 donor set?** **No.** R1 states the set as EWSR1 exons 1, 4, 7, 9,
10, 12, 13 and 15 across seventeen coding exons. **Not one exon number from that set appears in the
figure** except exon 7 (in Panel C) and exon numbers 8 and 10 in the ATF1 row labels of Panel A,
which are ATF1-junction labels, not donor-phase statements. There is no exon-phase panel.
**MISMATCH if cited: the phase-1 donor set is a text/table result with no figure support.**

**Does the figure depict the symmetric prefix sweep, 0.439 vs 0.400?** **No — completely absent.**
Neither `0.439` nor `0.400` nor `0.039` is rendered anywhere. **TCF12 does not appear anywhere in the
figure at all**, in any panel, in any label. The figure contains no composition or hydropathy axis of
any kind; Panel B's axis is retained-RG fraction, a different quantity. **MISMATCH, precisely: R1's
DECISION-MEMO M9 (the symmetric sweep, FET lowest 0.439 vs TCF12 best 0.400, margin 0.039) has no
figure to point at. Any cross-reference from that row to Figure 1 would be false.**

**Does the figure depict the margin of 13?** **No.** R1's P3 states TAF15(1-161) has "13 residues of
headroom below the RG-free ceiling of 174 and TAF15's first RG at 175", and a separate line cites a
fixed window "with 13 residues of margin". Panel A renders `TAF15(1-161), 0 of 31 RG` — the 161 and
the zero count are there — but **174, 175 and 13 are not rendered anywhere**, and no headroom bracket
or ceiling marker is drawn. **MISMATCH if cited: the 13-residue margin is not visible in the figure.**
The TAF15 bar does carry unlabelled RG ticks whose leftmost lies past the 161 end-cap, which is
visually consistent with the claim but is not annotated and cannot be read off as "175".

**What R1's numbers the figure *does* corroborate:** the ATF1 comparator span 0.000 to 0.267 (Panel B,
verbatim); the Table-4 pairs EWSR1::ATF1 e10 = EWSR1(1-348) = 8/30 = 0.267 and type 1 = EWSR1(1-431)
= 8/30 = 0.267 (Panel A annotations and the Panel B triangle position agree); type 5 = EWSR1(1-472) =
11/30 = 0.367 (Panel A text and Panel B triangle agree); type 2 and TAF15::NR4A3 at 0.000; and the
"measured in reference 1" row's two firm anchors at 0.000 and 1.000 with the one-domain add-back
explicitly undeterminable — which matches R1's M6 exactly, including the honesty of the hatched band.

**Summary of the mismatch finding.** R1's arithmetic is sound and agrees with the figure. The
mismatch is one of *coverage, not of numbers*: Figure 1 supports the composition axis and the type-2
seam and nothing else. Three of R1's headline results — the frame rule as a rule, the phase-1 donor
set, and the symmetric prefix sweep with its 0.039 margin — plus the 13-residue TAF15 headroom, have
**no visual representation in this figure**. Inserting Figure 1 (R1's D3) is safe; citing it for those
four things is not.

## 4 · Provenance of each claim

- **Rests on pixels (everything in §1 and §2, and the figure side of every comparison in §3):** all
  quoted labels, ticks, axis titles, annotations, the three-panel division, the presence of the
  dashed boxes and the absence of any key, the absence of TCF12 / 0.439 / 0.400 / 176 / 13 / 174-as-a
  -TAF15-ceiling, and the PNG's own 2220x2670 RGBA header.
- **Rests on the R1 artefacts** (`PROPOSED-emc-atr-collaborator-package.md`, `DECISION-MEMO.md`),
  read only to state what R1 claims so it could be checked: the wording of R1's 177/176 sentence, the
  frame rule as R1 states it, the phase-1 donor set, the 0.439/0.400/0.039 sweep row, and the P3
  13-residue headroom.
- **Rests on the generator or on `emc-fet-frame-and-composition.json`: nothing.** I did not open
  either file. No claim here derives from them.
- **My own inference, flagged as such and not read from the figure:** that the thin vertical ticks in
  Panel A are RG dipeptides; that the dashed boxes are RGG-rich regions; approximate residue
  positions of the dashed boxes and NR4A3 domain boundaries; approximate Panel B marker positions
  (0.267, 0.367, 0.233), which I state as "about" and which agree with the exact fractions printed as
  counts in Panel A.

## 5 · UNKNOWN

- What the dashed boxes in Panel A denote. Unlabelled in the figure. **UNKNOWN from pixels.**
- What the thin vertical ticks denote. Unlabelled. **UNKNOWN from pixels.**
- The NR4A3 domain boundary residues. Not printed. **UNKNOWN from pixels.**
- Which source "reference 1" is. Panel B says "reference 1" without a citation. **UNKNOWN.**
- Whether the figure file on disk is the current output of the current generator. I did not open the
  generator and ran nothing. **UNKNOWN.**
- Whether the manuscript's existing prose already cross-references Figure 1 for the four unsupported
  items. I did not review the manuscript. **UNKNOWN — worth one targeted grep by whoever owns U2.**

## 6 · What I did NOT do

No figure regenerated. No science rerun. No data changed. No edit to the manuscript, registry, tier,
reference list, generator or any gate. No whole-paper review, no census, no source recovery, no
network, no `scripts/preflight.sh`, no paid API, no GPU. No git write — read-only `git rev-parse` and
`git status` only. No write outside `/tmp/claude-0/u1-lane/`. Nothing deleted. No closed contract
reopened. No content-policy refusal was encountered, so there is none to record.

No EMC efficacy, safety, selectivity or clinical-readiness claim is made or implied here; Panel B's
EMC positions are computed, not measured, and the figure itself says so by separating "measured in
reference 1" from "computed here". There is no wet lab.
