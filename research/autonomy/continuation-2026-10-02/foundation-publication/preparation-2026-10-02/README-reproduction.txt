Foundation source-identity correction — offline reproducibility

This package reuses fixed evidence from trimcrae/Rare-cancers revision
5d2f2e2116f43c0bb56a46120902a1332f27720b. No primary extraction was repeated
for publication preparation. Original primary confirmation: run37035103326,
revision83e0fb5348fe41b1747970d6346c6f3b19a3b5ea, passed.

Start in the extracted package directory, using Python3.9 or newer:
    python verify_package.py

This checks the outer package manifest and all original archive members. It
does not run a scientific computation. Original inputs remain nested in the
unchanged primary-inputs.zip; source-archive.json records their exact hashes.

OPTIONAL READER REPRODUCTION
Use a new scratch directory; these commands must not overwrite previous output.
    python -m zipfile -e primary-inputs.zip inputs
    python foundation_identity_recovery.py --export inputs/data_sv.txt --mapping inputs/mapping.json --out-dir recovered

Expected recovered TSV SHA-256:
2c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184
The recovery uses Python's standard library. Non-ID fields and all564 literal
N/A tokens must be preserved. The mapping assumes retained event order.

An optional independent workbook check requires xlrd==2.0.2, in addition to Python:
    python foundation_primary_workbook_check.py --workbook inputs/primary.xls --mapping inputs/mapping.json --export inputs/data_sv.txt --corrected recovered/data_sv.identity_corrected.tsv

The workbook command uses archived bytes, not --fetch-primary. Expected saved
output is primary-independent-check.stdout; see primary-execution.json for the
actual historical run. Both extractors use the xlrd family. Do not interpret
their agreement as independent parser validation.

ANNOTATION EVIDENCE
annotation.json and the exact HGNC response ZIP/manifest preserve the fifteen
literal gene-pair differences: twelve currently alias-supported events, two
unresolved date-cell cases, one unresolved AKAP2/PALM2AKAP2 distinction.
cell-probe.stdout preserves the date-cell inspection. No intended gene is
inferred from a date and no gene annotation is changed by identity recovery.

INTERPRETATION
This is a proposed fixed-file identity-only derivative. Source diagnoses,
functional fusions, somatic status, assays and live portal deployment are not
validated. Event counts are not independently verified patient counts.
LICENSES.txt identifies ODbL, primary-source and HGNC terms separately.
No global CC BY/CC0 relicensing, journal submission or data deposit is claimed.
