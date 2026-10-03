---
id: "DOC-CONTINUATION-2026-10-02-FOUNDATION-FOUNDATION-PRIMARY-SOURCE-PLAN"
title: "Independent primary workbook re-extraction plan"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for Independent primary workbook re-extraction plan."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Independent primary workbook re-extraction plan

Prepared 2 October 2026. NOT EXECUTED by this seat. No workbook downloaded locally.
This closes the remaining dependency on a previously derived source mapping,
rather than repeating the original proof without a new purpose.

## Source identified from pinned historical evidence

Public source container:
https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9200814/supplementaryFiles

Unique basename: 41467_2022_30496_MOESM2_ESM.xls
Workbook bytes: 4812800
Workbook SHA256: 88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475
First16hex: d0cf11e0a1b11ae10000000000000000

This is legacy OLE/BIFF XLS, not XLSX or XML. A ZIP/XML XLSX reader and openpyxl
are inappropriate. Use cloud xlrd; script records its actual version. Reuse an
installed cloud xlrd where available. No local dependency installation is needed.
The supplementary ZIP container hash varied across previous requests; enforce the
extracted workbook hash, record the archive hash, and do not pin the transport
container to one historical hash.

Evidence:
https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/foundation-primary-workbook-actual.json
https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/foundation_legacy_workbook_analysis.py
https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/foundation_identity_and_partner_sensitivity.py

Confirmed variant sheet: variants_table_final_for_supple;28547 physical rows.
Confirmed clinical sheet: samples_table_final_for_supplem;7495 physical rows.
Headers are first physical rows, hard-coded verbatim from the frozen primary
receipt; script refuses unexpected schema/dimensions. Physical XLS row indices
are taken directly from xlrd, not inferred from filtered event order.

## Checker scope

foundation_primary_workbook_check.py is a new independent extraction implementation.
It does not import the prior helper, correction utility, proof summaries, or
mapping perEMC objects. It reads only concrete mapping records after hash check.

For every primary alteration_type exactly RE, compare event ordinal, physical
worksheet row, source ID and gene pair against the complete mapping. Compare
each corrected Sample_Id directly to primary workbook IDs; verify every other
TSV field remains identical to original export. Preserve full event multiplicity.
Extract EMC IDs directly from the primary clinical worksheet and repeat the
specific join consequence. Report numeric gene cells and all symbol differences.

Explicit comparison representation follows the frozen map: whitespace stripped;
empty/NA/N/A/NAN treated as missing. Numeric BIFF genes remain numeric-string
values (for example44621.0), not guessed symbols. Output CSV/TSV is never changed.

Known hashes:
- Mapping:341f64562039230c581aefb7f03d7da4769969a79290217962216f3d7e567a5e
- Original export:d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701
- Corrected export:2c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184

Root reports prior correction replay run37009409052/job110845272744,
codeb066a7e7bcffe4892c78f2d9462cc70b4d14945b. This new primary check has not yet run;
do not treat the prior replay as verification of this new extraction.

## Bounded cloud execution

Prefer existing primary.xls capture if its hash matches. Otherwise one public
GET is permitted with --fetch-primary,90second socket timeout and20MiB cap.
ZIP extraction is in memory and member size/hash are mandatory. Stop on access
error or hash/schema mismatch; do not search authenticated alternatives.
Script writes nothing itself; redirect its small JSON receipt in cloud output.

Example:

python foundation_primary_workbook_check.py --fetch-primary \
  --mapping Foundation-complete-rearrangement-source-mapping.json \
  --export data_sv.txt --corrected data_sv.identity_corrected.tsv \
  > foundation-primary-independent-check.json

Use --workbook primary.xls or --archive supplementary.zip instead to reuse captures.
Set a finite outer process timeout (suggest180seconds). Archive is about4.9MB
historically; no new full checkout or large runtime is warranted.

Acceptance: status passed,3771directprimarymappingmatches,
3771directprimarycorrectedIDmatches,3770originalIDdiscordances,
3182distinctsourceIDs,3756geneagreements/15differences,
75EMCprofiles/76events/28selected/0originatingEMC/47outofrange,
and source49oneevent/source245twoevents. Any discrepancy is a named blocker
requiring source inspection, not a reason to relax hashes or infer missing IDs.
Check independent primary conclusions against accepted receipt, not via script
assertions that simply force those numbers.

Limits: independent code path, but same xlrd reader family; no independent
laboratory/diagnostic validation, new patient data, or portal deployment check.
