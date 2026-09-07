# Reproduce the GEO metadata checks

This supplement contains verification code and factual audit outputs. It contains no original GEO archive, publisher article, publisher image, expression table, or copied narrative study description. The original files are obtained separately under their original terms. Their rights are not changed by this supplement's license.

Python 3.9 or later is sufficient; only the standard library is used. From this directory:

```text
python -X utf8 -B retrieve_sources.py --plan --sources ../local-original-sources
python -X utf8 -B retrieve_sources.py --sources ../local-original-sources
python -X utf8 -B verify_metadata.py --sources ../local-original-sources --output results
```

The first command prints the four exact original-source retrieval URLs and hashes without connecting or writing files. The second downloads the originals into a separate directory, verifies their frozen hashes, and records actual retrievals there. Figure S6 is obtained as one exact named member of the original supplementary ZIP. Its unchanged file size and SHA256 are mandatory. The containing ZIP is a transport: its actual hash/size are recorded, its earlier hash/size remain reference observations, and downloads are capped at 16 MiB. Exactly one named Figure S6 member is read; other members are not extracted. The transport ZIP is retained outside this supplement in the local `transport/` directory. Existing matching source and transport files are reused. A source-file/member mismatch causes failure without overwriting an existing source. Source servers can change or become unavailable; changed source-file content is not silently accepted. Do not bypass an access challenge. A retained byte-identical original can be placed in the same separate directory and verified offline.

The verifier skips every GEO expression/platform table body. It checks source hashes, complete sample rosters, independent diagnostic fields, platform membership, GSE6481 aggregate counts, and GSE24369 title numbering and sample-type labels. Narrative metadata is read locally when needed for these checks but is not written into the factual outputs.

Expected results are 105 GSE6481 sample records and 42 GSE24369 array records. The latter comprise 40 tumor samples and two skeletal-muscle pooled-RNA controls. Outputs contain GSM accessions, diagnosis labels, platform accessions, source line numbers and audit counts. These are array/sample records, not independently verified unique-patient counts. No expression analysis or patient-identity inference is performed.

## Original sources and rights

`retrieval-sources.json` gives the exact URLs, byte counts, file hashes, the Figure S6 archive member, historical containing-archive observations, the transport size bound, and rights links.

- [GSE6481](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE6481) and [GSE24369](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369) remain original GEO deposits. [NCBI's usage terms](https://www.ncbi.nlm.nih.gov/home/about/policies/) impose no NCBI reuse/distribution restrictions while preserving possible submitter rights; no CC0 grant in those originals is asserted here. Cite the accessions and original studies (PMIDs 17464315 and 21536545).
- The original article and Figure S6 are from Chaiboonchoe et al., *Prognostic biomarkers for enhanced risk stratification in extraskeletal myxoid chondrosarcoma: a retrospective cohort study*, PeerJ 14:e21497 (2026), [DOI 10.7717/peerj.21497](https://doi.org/10.7717/peerj.21497). They retain their [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) terms and original attribution. No copy of either is included here.

## Reproduction record

`results/execution.json` records verification of originals obtained by the successful live reader workflow. `reproduction.json` preserves the earlier offline replay, the first live run's transport-hash failure, the precise repair, the subsequent successful four-source live retrieval and verification, and a local check of matching-transport reuse after interruption. The four original file hashes and all factual rosters/counts match the reviewed source audit; the distributed output schema omits narrative extracts. The final matching-transport reuse change was checked locally after the successful live run; it did not require another network request.

`manifest.json` inventories this supplement, excluding itself. The separate deterministic ZIP is an exact container of those files and that manifest. A local rerun updates only the selected result files; it does not regenerate the packaging manifest. Original-source files are never part of the distribution inventory.
