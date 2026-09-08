---
id: DOC-EMC-CLOUD-SELECTED-CORPUS-20260908
title: Selected EMC source snapshot for the cloud campaign
level: —
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

This directory transports 5,996 selected files (236,150,544 uncompressed source bytes) from frozen local source 93b75888e31976195145e2404373b2d7a512f6d1. Every selected file matched its recorded Git blob and size before packaging. This is a selected-file snapshot, not a complete repository or that commit's Git ancestry. The supporting branch is based on actual remote main; do not label the cloud checkout 93b.

The six numbered parts are raw pieces of one ZIP. Verify the external reassembly manifest (SHA256 a9fa1ff6639dec434d60e0b1b7b3954c41f4f73a72160fe422e42cab673d37f7), each part's byte count and SHA256, then concatenate in numeric order. The resulting ZIP must be 45,840,377 bytes with SHA256 b474cd2f8a0e3fa3a253f5b3135379cb26c15222a94698fc411fd781f6346808. CRC-check all 6,002 members before extracting into a fresh, separate context directory.

The archive contains source files under corpus/ and these six metadata/README members:
- README.md
- metadata/closed-source-and-ownership-map.md
- metadata/corpus-manifest.json
- metadata/member-manifest.json
- metadata/snapshot-provenance.json
- metadata/tracked-file-map.txt

Use corpus/ beside the actual cloud checkout; do not overlay it. The complete tracked-file map is discovery metadata and includes files not supplied here. Missing files remain unprovided/unknown, not evidence of repository-wide absence. The compact source/ownership map is a point-in-time record; its historical worker-status wording does not describe current workers. The sole campaign launcher maintains live status. Inclusion of material does not reopen a closed source or authorize work on the separately closed NR4A Perspective.

The adjacent earlier source-index capsule and evidence-4878-exact-files.zip retain later code, execution and source-disposition records. Original tests, static findings and malformed proposed diffs keep their original status; this transport applies no implementation or scientific acceptance.
