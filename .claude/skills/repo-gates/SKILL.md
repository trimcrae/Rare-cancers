---
name: repo-gates
description: Run the repository checks appropriate to a code, evidence, or manuscript change and preserve an honest validation result.
---

# Repository checks

Follow `research/autonomy/OPERATING_PROTOCOL.md`. During development use targeted checks for
changed behavior. Batch known fixes and regenerations before running the normal commit gate:

```bash
./scripts/preflight.sh
```

Read the whole failure log and fix related failures together. Preserve exit codes; do not infer
success from a piped tail. A baseline environment failure is not evidence the paper is wrong.
Use the appropriate interpreter/dependencies; `scripts/dev-setup.sh` is the legacy Linux setup,
not a portable Windows installer. Record any checks that could not run.

Use `PREFLIGHT_TESTS=1`, `PREFLIGHT_MODALITIES=1`, or targeted pytest files as the changed behavior
requires. Preserve the actual reported scope. Do not run full science suites for every prose or
coordination edit. A publication candidate requires `PREFLIGHT_FULL=1`, the full log, and the exact
candidate revision, recorded by `research/autonomy/record_bar_evidence.py` and evaluated by
`publish_bar.py`. A scoped/skipped run is not full publication evidence.

One coordinator checks current main and integrates coherent work. Do not merge main after every
individual edit. A test or gate whose only effect is repeated administrative work may be changed
under the user's improvement mandate; document the change and test the meaningful behavior.
Do not weaken scientific checks to hide a defect or announce readiness on unrun checks.

The [legacy reference](references/legacy-2026-09-04.md) contains old environment workarounds and
measured incidents. Consult it only for a matching failure, not as additional routine procedure.
