import io, sys, os
SRC = "/tmp/claude-0/x1-lane/PROPOSED-X1-emc-atr-collaborator-package.md"
DST = "/tmp/claude-0/x1-integrate/INTEGRATED-emc-atr-collaborator-package.md"
t = io.open(SRC, encoding="utf-8").read()
n = 0
def rep(old, new, label):
    global t, n
    c = t.count(old)
    if c != 1:
        sys.exit("FAILED %s: %d occurrences" % (label, c))
    t = t.replace(old, new)
    n += 1
    print("applied", label)

# ---- C1: frontmatter first, provenance comment after it -----------------
head_end = t.index("============================================================================= -->\n---\n")
lead = t[:head_end + len("============================================================================= -->\n")]
assert lead.startswith("<!-- ===")
t = t[len(lead):]
fm_close = t.index("\nrelated: [DOC-EMC-ATR-VULNERABILITY-ASSESSMENT]\n---\n")
insert_at = fm_close + len("\nrelated: [DOC-EMC-ATR-VULNERABILITY-ASSESSMENT]\n---\n")
prov = """
<!-- ============================================================================
REVISION PROVENANCE, EDITORIAL - NOT FOR SUBMISSION.

This file is a NEW working revision, integrated on 2026-09-08. It is not a recovered
original: no file, blob or draft of any lost historical revision was found, and none is
claimed. The wording of the edit that introduced the earlier text was not recovered from
the history examined at its squash and shallow-clone boundary, which is a limit of that
examination and not a finding of global historical absence.

It was built by applying, to the R1 candidate, three required corrections to that
candidate, the qualifications established by U1, and the completed outputs of W1
(Supplementary Table S3), W2 (Panel A key sources) and W3 (Okamoto 2001 metadata). The
scientific coordinator then accepted that reconstruction and title as the new working
manuscript and authorised six further bounded corrections, together with one sentence
replacement opening section 3.5, all of which are applied here. Integration is not
publication acceptance.

The `date` and `last_verified` fields above are the original source dates of the
underlying analysis and are deliberately unchanged: no scientific result was recomputed,
re-derived or re-verified for this revision, and no fresh verification is claimed.

Retained records, unedited: the proposal, its decision record, the verbatim earlier
Appendix A, and the candidate-versus-baseline and candidate-versus-R1 diffs are under
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/X1-executed-artifacts/`.
Figure-QA observations carried out of the Figure 1 caption during this integration are in
[`emc-atr-collaborator-package-integration-qa-2026-09-08.md`](./emc-atr-collaborator-package-integration-qa-2026-09-08.md).
============================================================================= -->
"""
t = t[:insert_at] + prov + t[insert_at:]
n += 1
print("applied C1 frontmatter")

# ---- C2: Figure 1 image + Panel C nucleotide accounting ------------------
rep("""**Figure 1.** Reported EMC junctions on the retained-RG axis, and the type-2 seam. Three panels,""",
    """![Figure 1. Three panels: reported EMC junctions drawn to residue scale with their RG content, the retained-RG fraction axis, and the type-2 seam.](../figures/emc-fusion-frame-fig1.png)

**Figure 1.** Reported EMC junctions on the retained-RG axis, and the type-2 seam. Three panels,""",
    "C2 image")

rep("""**Panel C.** The type-2 seam, drawn as NR4A3 exon 2 (174 nt, untranslated in NR4A3), one nucleotide
donated by EWSR1, and the resulting extension of 59 codons over 177 nt with no internal stop codon.""",
    """**Panel C.** The type-2 seam, drawn as one nucleotide donated by EWSR1 followed by 176 nt of NR4A3
untranslated sequence: 174 nt of NR4A3 exon 2, the block labelled untranslated in NR4A3, and the
first 2 nt of NR4A3 exon 3, annotated separately in the panel. Those 177 nt are the extension of 59
codons carrying no internal stop codon. The earlier caption counted only the exon 2 block and the
donated nucleotide, which does not reach 177.""",
    "C2 panel C")

# ---- C6: figure QA out of the caption ------------------------------------
rep("""*What the figure does not show.* The frame rule as a rule over all donor and acceptor pairs, the
complete phase-1 donor set, the symmetric prefix sweep and its 0.039 margin, and the TAF15 zero-RG
margin are results of sections 3.2, 3.4 and 3.5 and appear in no panel; none of them may be cited to
this figure. The generator draws NR4A3 RG ticks at residues 371 and 508; an independent reading of
the rendered image reported one of them, and whether the 371 tick is occluded by the adjacent
domain-block edge at 373 or is not resolved at print size was not settled and is not asserted here.

*A provenance limitation of the drawing.* The Panel A box spans are hard-coded literals in the
generator and currently match `rgg_boxes_operational` exactly, which was checked. The generator
stamps a hash of each of its listed source files, so a change to that data field would change the
recorded stamp; what the code does not carry is any binding or asserted equality between that field
and the literals, so a later redraw with the literals unchanged could preserve a semantic mismatch
while still producing a fresh source stamp.""",
    """*What the figure shows, and what it does not.* The three panels carry the reported junctions, the
RG content each retains, the retained-RG fraction axis and the type-2 seam. The frame rule as a rule
over all donor and acceptor pairs, the complete phase-1 donor set, the symmetric prefix sweep and its
0.039 margin, and the TAF15 zero-RG margin are results of sections 3.2, 3.4 and 3.5 and appear in no
panel. Two drawing-level observations, on the legibility of the closely spaced NR4A3 ticks and on the
binding between the Panel A box literals and their source data field, are recorded in the integration
QA note cited in the editorial comment above rather than in this caption.""",
    "C6 caption")

# ---- C7: Y1 sentence replacement -----------------------------------------
rep("""Roughly 3 to 4 per cent of EMC carries TCF12::NR4A3, and TCF12 is not a FET-family gene.""",
    """TCF12::NR4A3 was reported in one of 26 cases in one EMC series [6]. TCF12 is not a FET-family gene.""",
    "C7 section 3.5 opening")

# ---- C3a: Methods 2.3 ----------------------------------------------------
rep("""The sweep
computes the [S,Y,G,Q] fraction of every TCF12 N-terminal prefix from 50 residues to full length in
10-residue steps, so the conclusion does not rest on one assumed junction.""",
    """The sweep
computes the [S,Y,G,Q] fraction of every N-terminal prefix from 50 residues to full length in
10-residue steps, on that one evaluated grid, for TCF12 and for each of the three FET proteins rather
than for TCF12 alone. The published version of this test swept TCF12 alone and compared its best
value against the FET proteins at a single fixed 250-residue window, which is asymmetric. No sweep
was run for this revision: the symmetric result, its grid, its per-protein prefixes and the resulting
0.039 gap are read from the retained artifact
[`emc-fet-frame-and-composition.json`](../../modalities/emc-fet-frame-and-composition.json) under
`composition.symmetric_prefix_sweep`. The conclusion therefore rests neither on one assumed junction
nor on one fixed window.""",
    "C3a methods 2.3")

# ---- C3b: Methods 2.5 ----------------------------------------------------
rep("""```
python3 research/modalities/emc_fet_construct_designs.py --check
```

That command re-derives every figure below offline from the committed input cache
([`emc-construct-inputs.json`](../../modalities/emc-construct-inputs.json)) and prints `REPRODUCES`.
The producer emits no output if the inputs have drifted.""",
    """```
python3 research/modalities/emc_fet_construct_designs.py --check
python3 research/modalities/emc_fet_frame_and_composition.py --check
python3 research/manuscripts/figures/emc_fusion_frame_figure.py --check
```

The first command re-derives the per-construct assembly coordinates, the reading frames and the
recruitment-axis rows offline from the committed input cache
([`emc-construct-inputs.json`](../../modalities/emc-construct-inputs.json)) and prints `REPRODUCES`;
it does not produce the frame rule, the type-2 seam arithmetic or the composition results. The second
re-derives those into
[`emc-fet-frame-and-composition.json`](../../modalities/emc-fet-frame-and-composition.json), printing
`REPRODUCES` when a fresh derivation matches the committed artifact and `DRIFT`, with a non-zero
exit, when it does not; its unit tests are
[`test_emc_fet_frame_and_composition.py`](../../modalities/tests/test_emc_fet_frame_and_composition.py).
The third compares the committed provenance stamp
([`emc-atr-figure-provenance.json`](../figures/emc-atr-figure-provenance.json)) against the artifacts
Figure 1 was drawn from, printing `PROVENANCE MATCHES` or `STALE`; run without `--check` it redraws
the figure. These are the declared command signatures, quoted from the three modules; none of them
was run to produce this revision, which recomputes no scientific result.""",
    "C3b methods 2.5")

# ---- C3c: section 7 ------------------------------------------------------
rep("""| Computed artifact, the home of every figure above | [`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json) |""",
    """| Computed artifact holding the per-construct assembly coordinates, reading frames and axis rows | [`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json) |
| Producer of the frame rule, the type-2 seam arithmetic and the composition results | [`emc_fet_frame_and_composition.py`](../../modalities/emc_fet_frame_and_composition.py) |
| Its computed artifact | [`emc-fet-frame-and-composition.json`](../../modalities/emc-fet-frame-and-composition.json) |
| Its unit tests | [`test_emc_fet_frame_and_composition.py`](../../modalities/tests/test_emc_fet_frame_and_composition.py) |
| Figure 1 generator and the provenance stamp it writes | [`emc_fusion_frame_figure.py`](../figures/emc_fusion_frame_figure.py), [`emc-atr-figure-provenance.json`](../figures/emc-atr-figure-provenance.json) |""",
    "C3c section 7 rows")

rep("""The artifact was produced by GitHub Actions run 30857647907 on `depmap-dependency.yml` in the
public repository, and `--check` re-derives it offline. Any figure above that disagrees with the
artifact is an error in this document.""",
    """`emc-fet-construct-designs.json` was produced by GitHub Actions run 30857647907 on
`depmap-dependency.yml` in the public repository, and its producer's `--check` re-derives it offline.
The frame-and-composition artifact and the figure carry their own producers and checks, listed in
section 2.5. Any figure above that disagrees with the artifact it is drawn from is an error in this
document.""",
    "C3c section 7 prose")

# ---- C4: preregistration commentary --------------------------------------
rep("""P4's falsifier, "the pair showing no kinetic
difference", is the same observation as P2's first falsifier, "type 1 recruiting no earlier than
type 2"; one experiment therefore falsifies two entries, and the set counts fewer independent tests
than its five ids suggest. P1 as registered predicts kinetics *indistinguishable* from a comparator,
which is an equivalence: a null result satisfies it and an underpowered experiment satisfies it too,
so P1 is confirmable but not straightforwardly falsifiable in the direction it is written.""",
    """P4's falsifier, "the pair showing no kinetic
difference", overlaps P2's first falsifier, "type 1 recruiting no earlier than type 2", without being
identical to it: the first is a two-sided absence of any difference, while the second is directional
and is also satisfied by type 1 recruiting later. One experiment can therefore satisfy both at once,
so the set counts fewer independent tests than its five ids suggest, but the two entries are not
interchangeable. P1 as registered predicts kinetics *indistinguishable* from a comparator. Failure to
detect a difference does not establish equivalence. The registered wording supplies no equivalence
margin or precision criterion, so a nonsignificant comparison alone cannot confirm P1.""",
    "C4 prereg commentary")

# ---- C5: S3 legacy rank row ----------------------------------------------
rep("""| Reported rank | the commonest reported EWSR1::NR4A3 transcript type |""",
    """| Reported rank — LEGACY SOURCE DESCRIPTION, not a counted frequency (see note) | the commonest reported EWSR1::NR4A3 transcript type |""",
    "C5 S3 row label")

rep("""Genomic breakpoint coordinates are `UNRESOLVED` for all four junctions because the input carries""",
    """*Note on the "Reported rank" row.* Its four cells are verbatim leaves of the artifact and are
retained unchanged, with their provenance, but they are a legacy source description of how each
junction was characterised, not a frequency counted in this work. Table 1 carries the corrected
frequency evidence, with each count attached to the series it comes from; where the two differ,
Table 1 governs. No artifact value was modified to add this label.

Genomic breakpoint coordinates are `UNRESOLVED` for all four junctions because the input carries""",
    "C5 S3 footnote")

io.open(DST, "w", encoding="utf-8").write(t)
print("wrote", DST, "replacements:", n)
