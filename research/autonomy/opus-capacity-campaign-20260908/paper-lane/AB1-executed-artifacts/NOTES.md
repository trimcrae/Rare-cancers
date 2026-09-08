# AB1 — shortened abstract for emc-atr-collaborator-package.md

Source: `research/manuscripts/dependency/emc-atr-collaborator-package.md` (whole manuscript read:
frontmatter, editorial block, sections 1-9).
Declared counter: `research/manuscripts/submission_metrics.py::measure` (see COUNTER-INVOCATION.txt).
BEFORE 341 words. AFTER 245 words. Recorded cap 250 (search-derived, not publisher-verified).

## The five required preservations, each mapped to a sentence in AFTER-abstract.txt

1. **Central contributions of the paper.** Carried by five sentences, matching sections 3.1-3.5 and 4:
   - compilation and transcript-level translation: *"The reported EMC junctions are compiled from
     primary sources, translated at transcript rather than coding-sequence level, and placed on that
     axis."*
   - in-frame result: *"Four sourced junctions (EWSR1 exons 12, 7 and 13; TAF15 exon 6) yield
     in-frame reading frames retaining the complete NR4A3 moiety."*
   - the type-2 insertion (section 3.3): *"The EWSR1 exon 7 to NR4A3 exon 2 junction inserts 177
     nucleotides in the EWSR1 frame, encoding 59 residues absent from this programme's earlier
     protein-level model."*
   - axis placement (section 3.4): *"Retained EWSR1 RG dipeptides place type 1 at 8 of 30 and type 2
     at 0 of 30, within the 0.000 to 0.267 span of the three reported EWSR1::ATF1 breakpoints ..."*
   - TCF12 classification (3.5) and the pre-specified set (section 4): the TCF12 sentence, and
     *"Five predictions with explicit falsifiers, four constructs and four controls are specified in
     advance."*

2. **Honest source and computational limitations.** *"No experiment was performed: sequences come
   from public reference transcripts on one annotation source, and each junction needs verification
   against a sequenced breakpoint."* This carries limitations 1, 3 and 8 and section 2.6's
   single-annotation-source dependency in one sentence.

3. **Recruitment NOT measured at intermediate positions on the retained-RG axis.**
   *"Recruitment was measured only at 0.000 and 1.000, never in between."*

4. **REPORTED breakpoint vs MEASURED construct.** *"... within the 0.000 to 0.267 span of the three
   reported EWSR1::ATF1 breakpoints: reported breakpoints, not the measured construct, whose
   breakpoint is unstated."*

5. **Evaluated-grid qualification on the symmetric prefix sweep.** *"TCF12, a minority non-FET 5'
   partner in EMC, falls outside the FET compositional range at every prefix on the evaluated grid
   (50 aa upwards in 10-aa steps), where no TCF12 prefix reaches the lowest value any FET prefix
   takes."* — "on the evaluated grid" scopes both the range claim and the relative clause, matching
   section 3.5's "no N-terminal prefix on the evaluated grid reaching the lowest value any FET
   prefix takes on that grid".

## What was cut, and why (96 words)

- **The EWSR1::NR4A3 / TAF15::NR4A3 exon pairs spelled out one by one** ("EWSR1 exon 12 to NR4A3
  exon 3, EWSR1 exon 7 to NR4A3 exon 2, ...") — compressed to "(EWSR1 exons 12, 7 and 13; TAF15
  exon 6)". No junction is lost; the acceptor exons are still recoverable from Table 1, and the one
  acceptor that matters for the seam (NR4A3 exon 2) is named in the type-2 sentence.
- **The nucleotide accounting of the 177 nt** ("one donated by EWSR1 across the seam and 176
  supplied by NR4A3, of which 174 come from exon 2 and 2 from exon 3") — section 3.3 and Figure 1C
  carry it; the abstract keeps 177 nt and 59 residues.
- **The frequency sentence** ("Type 1 is the commonest EWSR1::NR4A3 type in both series that typed
  EWSR1 subtypes; type 2 is counted once in those two series, and a third series counts partner
  genes rather than EWSR1 subtypes") — this is a source-counting result, not one of the paper's four
  computed contributions, and its per-series attribution cannot survive compression honestly.
  Table 1 governs it.
- **"A recent report ... using accumulation of a GFP-tagged fusion protein at laser-induced
  double-strand break stripes as the readout"** — shortened to "recruitment to laser-induced
  double-strand breaks"; the GFP tag and stripe geometry are methods detail (section 5).
- **"the measured positions on the axis itself are 0.000 and 1.000"** was kept but rephrased into
  its own short sentence and strengthened with "never in between", which is the point the dispatch
  requires and which the 341-word version stated only implicitly.
- **"Five predictions with explicit falsifiers, four constructs and four wild-type controls"** ->
  "four controls"; Supplementary Table S2 carries that they are wild-type controls.

## Fidelity checks

- Every quantity in AFTER appears in the manuscript with the same value: 177 nt, 59 residues,
  8/30, 0/30, 0.000, 0.267, 1.000, 50 aa, 10-aa steps, five predictions, four constructs, four
  controls, EWSR1 exons 12/7/13, TAF15 exon 6, NR4A3 exon 2.
- No claim was added. No efficacy, safety, selectivity or clinical-readiness claim appears.
- "0.000 to 0.267 span" is stated as a span of REPORTED breakpoints, exactly as Table 3 and the
  Panel B caption require.
- Nothing in the repository was modified; this is an isolated candidate, not an applied edit.
