---
id: DOC-CHECKPOINT04-FOUNDATION-PRIMARY-ROUTE
title: Evidenced PMC cloud route for the pinned Foundation workbook
kind: memo
status: live
level: cross-cutting
purpose: Reopen the bounded independent primary extraction using a newly evidenced public source route.
scope: Metadata, HEAD and sixteen-byte range observations only; full workbook retrieval and extraction remain cloud work.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

## New route and actual observations

The official [PMC OA service notice](https://pmc.ncbi.nlm.nih.gov/tools/oa-service/) states that the legacy API is no longer available, dated August 25, 2026. Its old oa.fcgi endpoint returned HTTP404 in this check. The official [PMC AWS documentation](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/) instead documents anonymous HTTPS access, including supplementary materials, through the world-readable PMC bucket. This is a documented replacement service, not a challenge workaround. The older Europe PMC supplementaryFiles route was not retried.

The documented version-prefix listing returned only `PMC9200814.1/`. Its captured `article-metadata.json` explicitly names the target workbook in media_urls, identifies DOI10.1038/s41467-022-30496-0, and reports the published version, CC BY and not retracted. The metadata gives workbook MD5 `88366e3facf6d7c61fb660566ea7af3e`.

Exact public object: https://pmc-oa-opendata.s3.amazonaws.com/PMC9200814.1/41467_2022_30496_MOESM2_ESM.xls

At HTTP Date 2 October 2026 16:26:13 GMT, HEAD returned200, length4,812,800 and the same ETag. A separate Range bytes=0-15 request returned206, Content-Range bytes0-15/4812800 and `d0cf11e0a1b11ae10000000000000000`. Only16 workbook bytes were read locally. Full SHA256 is NOT verified by these observations. Exact captured metadata and scoped header receipts are adjacent; the existing successful historical workbook SHA remains the required acceptance pin.

## Cloud execution

`fetch_primary_aws.py` performs one GET, strict byte cap, historical SHA256 plus metadata MD5 checks, no overwrite, 90-second watchdog and >10GiB plus twice workbook size disk headroom. It has not been executed. No new dependency is needed for retrieval; the existing checker needs cloud xlrd. Retain the raw XLS explicitly in the cloud artifact to prevent repeating the historical XLS upload omission.

```sh
timeout 100s python fetch_primary_aws.py --out primary.xls > primary-byte-receipt.json
timeout 180s python foundation_primary_workbook_check.py --workbook primary.xls --mapping mapping.json --export data_sv.txt --corrected data_sv.identity_corrected.tsv > primary-independent-check.json
```

Stage the checker from branch commit `52d63c2352d51181453049246ca306e9815f6e74`, path `research/autonomy/continuation-2026-10-02/foundation/foundation_primary_workbook_check.py`, Git blob `a169d329c80852be10174893af9f54334a2c018d`. Do not use its --fetch-primary option. Its source and frozen input plan were inspected through GitHub. Read its JSON status and exit code; mere output existence is not a pass.

Input bindings:

| Input | Frozen source | Bytes / SHA256 |
|---|---|---|
| mapping.json | https://raw.githubusercontent.com/trimcrae/Rare-cancers/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-rearrangement-source-mapping.json | 1679613 / 341f64562039230c581aefb7f03d7da4769969a79290217962216f3d7e567a5e |
| data_sv.txt | https://media.githubusercontent.com/media/cBioPortal/datahub/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022/data_sv.txt | 180393 / d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701 |
| data_sv.identity_corrected.tsv | Previously verified small artifact, run37009409052, member outputs-small/foundation/data_sv.identity_corrected.tsv | 180952 / 2c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184 |
| primary.xls | New evidenced PMC object above | 4812800 / 88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475 |

The corrected TSV is not listed in the branch's foundation or results directory. Reuse the earlier staged verified artifact, rather than invent a committed path. Fresh API metadata confirms artifact11227172202, `emc-continuation-small-reanalyses-37009409052`,145313 compressed bytes, unexpired. The member path is from the earlier accepted artifact staging, not a new ZIP inspection in this checkpoint. Enforce its byte count and SHA after staging.

No new synthetic biological fixture is needed for source access. Required retrieval checks are byte count, full SHA, MD5 and successful independent checker output; the existing correction negative controls remain separate evidence. Compare returned primary counts with the existing source-plan acceptance expectations, including3771 direct matches,3770 original ID discordances and source49/245 multiplicities. Do not replace returned counts with expectations. No live-portal or diagnosis validity follows.

Stop on download, hash, schema or extraction failure. The earlier run37011070408 timeout remains a failed attempt; this metadata discovery does not retroactively make it pass. A fresh successful extraction would need its own run/code/artifact receipt. No empirical workbook download or extraction was performed locally.
