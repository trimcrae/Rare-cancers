# CSPG4 author-review reproducibility package — September 21, 2026

This revision retains the accepted September19 primary, historical and external data without changing their measurements or accepted test outputs. See README-september19.md for that original package.

The presubmission-20260921 folder adds a dated plan, a portable standalone two-sample specimen bootstrap, exact results, molecular-support source workbooks and selected rows, and the revised main figures/code. Run `python presubmission-20260921/amended_analysis.py` with Python and NumPy 2.3.5 to reproduce the new estimates and intervals. Its inputs are included. It writes AMENDED-RESULTS.json in that folder; timestamps differ but all result values reproduce. No source download or account is needed. Re-running the original replay.py validates unchanged retained calculations but is not needed to reproduce the added analysis.

The bootstrap uses50,000 draws, seed20260921, PCG64,50blocks of1,000 independent x-then-y multinomial draws and linear quantiles. Intervals are approximate and pointwise, conditional on the observed design, not post-selection corrected. No new pvalue or specimen reclassification was added. The original9EMC/393reference exact test remains unchanged; the broader descriptive reference has489specimens/37source labels.

Source workbooks retain publisher attribution; S3/S4 selected-row exports preserve original headers and Excel row numbers. Source TableS1Fusion=Yes can include previous ancillary testing. Seven retained cases have explicitNR4A3 in filteredS3, oneFUS::NR4A2, and one nofilteredS3row. No missing filtered detail is inferred from the aggregateS4comment.

FILE-MANIFEST.json binds all files except itself. Publication status is author-review draft, not journal submission or acceptance.
