# P3 read-only verification — neoantigen seam claim
Verdict: ALREADY CORRECTED (in the committed manuscript and its artifacts).
Key evidence:
- manuscript L194-198: 27 pairs, 5 in frame, 174 peptides, 11 binders (4 strong)
- manuscript L1508-1529 Appendix A: superseded 7 junctions / 26 binders -> current 5 / 11,
  attributed to the 2026-08-07 coordinate-system correction
- fusion-breakpoint-neoantigens.json _utc 2026-08-19T16:26:49Z, no RETRACTED banner,
  plausible_nr4a3_resume_range [1,1], all 5 EMITTABLE junctions nr4a3_first_residue=1,
  nr4a3_cds_nt_at_resume=0, n_distinct_binders=11, distinct peptides recomputed = 174
- fusion-neoantigen-retraction.json: breakpoint_artifact status "CLEARED", stamp banner = false
- fusion-neoantigen-predictions.json: transcript model, NR4A3 kept residues 1-, _supersedes the
  residue-2 protein concatenation model
- no downstream banner in hla-coverage.json, vaccine-construct.json, epitope-allele-matrix.json,
  junction-proteome-novelty.json
Residual: nr4a3-program-map.md L4388 still carries the 2026-08-03 "26 predicted binders span seams
that do not exist" sentence with no closure marker on that bullet (stale prose, not a paper defect).
