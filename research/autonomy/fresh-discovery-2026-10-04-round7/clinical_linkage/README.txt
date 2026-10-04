R7 clinical-linkage source gate, 2026-10-04

Read PLAN.txt, AMENDMENT-01.txt, RESULTS.txt and COVERAGE.json first. This lane produces no new disease finding or treatment guidance. All earlier packets remain frozen.

Reproduction (Python3 standard library only):
python evaluate_linkage.py --inbrx PATH/functional_models/inbrx2023.xml --chiusole PATH/prior-round2/clinical/chiusole2020.xml

The script uses original XMLs in this directory and reused Davis sources at ../../fresh-discovery-2026-10-04-round2/genomics/{davis2017.xml,davis-supplement2.docx}; restore these exact source hashes if running elsewhere. External original sources are read only; no dependency runtime or prior packet is modified. Source receipts and linkage-evaluation.json record actual SHA256 and original paths. The machine-readable result contains all11 anthracycline rows, all6 Davis rows, original supplement excerpts and all relevant EMC cells in the broader treatment source, not only favorable observations. It deliberately does not perform a statistical efficacy test.

fetch_sources.py downloads the original metadata and first XMLs through public EuropePMC APIs, within2MiB perfile and8MiB lane cap. Additional successful original XML URLs and hashes are in followup-source-receipts.json. Fetching again is unnecessary for unchanged verified evidence and may produce updated metadata. Search snapshots are discovery/access receipts; a search hit is not labeled a full evaluation.

Actual executed scripts this round: fetch_sources.py (7 sources); its get() function for sunitinib2012.xml and temozolomide2017.xml (both200); evaluate_linkage.py (all assertions passed). Lightweight read-only source extractions confirmed DOI identifiers and original DOCX timing conflict. No imaging, UI, headless browser, model fitting or clinical-record edits occurred. No owned process remains after freeze.
