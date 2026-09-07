---
id: DOC-ATLAS-OFFLINE-REPLAY-20260906
title: Portable offline source replay
level: cross-cutting
kind: runbook
status: live
canonical_for: []
purpose: Reproduce the historical frozen analysis using relocated exact source bytes.
scope: One tested clean-directory replay on this host, without changing scientific kernels.
audience: [external reviewers, autonomous research agents]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-HOFVANDER-VALIDATION-20260906]
---

Use Python3.12.14 with the three packages pinned in requirements.txt. Installation into a suitable environment is `python -m pip install -r requirements.txt`; the replay itself uses only local files and never installs or downloads anything. A configured environment suffices; this release does not claim to bundle Python/wheels or to have been tested on every OS.

Run `python -B -X utf8 replay.py --bundle /path/to/EMC-Research --frozen-packet /path/to/unchanged/atlas-hofvander-validation-2026-09-06 --run-dir /path/to/NEW-directory`. The bundle root must contain the four source locations recorded in input-lock.json: compressed Hofvander source/provenance, original-array source/provenance, the existing GSE24369 family gzip and the normal-context roster. No user-specific original absolute source path is used to find replay inputs. The default frozen packet is this directory's parent; use the option if inputs have been separately packaged.

The wrapper refuses an existing run directory, links/junctions, unsafe archive member paths, changed hashes or wrong runtime versions. It copies exact frozen code, extracts only11 needed source files from pinned archives/gzip, checks each source member, and changes only the top-level source_location key in two **derived staging copies** of the manifests. It records old/new hashes and JSON-pointer edits and checks that all other decoded content is identical. Original files are never edited.

Historical coordinator approval remains byte-identical under the staging frozen/ directory. A separately named replay-compatibility.json retains its historical coordinator fields because the unchanged entry points require them, replaces only relocated-manifest hashes and adds explicit replay provenance. It is not presented as a newly issued approval. standing-authorization.json records the coordinator's actual current instruction permitting this mechanical replay; the receipt identifies the present initiator/time separately.

Both unchanged synthetic fixture entry points run first, followed sequentially by the unchanged Hofvander and array kernels. Replication consumes the newly replayed original-cohort results, never the historical expected result. report.py is a separate presentation adapter derived from the original CSV-export operations; its normal-context path is explicit and it does not alter summarize.py. It exports the same five tables plus a verbatim normal-context roster and provenance, without recomputing tissue hypotheses or normal-sparing labels. It does not attempt byte-identical narrative prose or rerun the historical3SEQ analysis.

Comparison is strict decoded type/value equality, including array order and nulls, with no floating tolerance. The only exclusions are **top-level** result.authorization (separately checked against compatibility) and replication result.original_result_sha256 (checked against the actual replay result bytes). Original_values_sha256 remains exact. Execution status/final stage must agree; times differ and are retained. All five CSV tables require exact parsed column strings and row order, a stronger check than numeric semantic equivalence. Every mismatch and compared scalar/file count is saved. Biological labels, gates, source values, singleton states, bootstrap seed/order and all sensitivities are equality targets.

code-freeze.json pins the adapter/input-lock/authorization/requirements bytes before the single empirical replay. receipt.json and comparison.json preserve commands, logs, runtime/OS, input/archive/member/output hashes, elapsed time and comparison results. The actual test is one newly created directory on this existing Windows host using the pinned runtime; it is not a second-machine or second-OS validation, a new cohort, an additional scientific experiment or publication approval. The frozen empirical and draft packets remain unchanged.
