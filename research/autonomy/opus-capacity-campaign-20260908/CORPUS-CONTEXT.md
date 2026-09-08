# Verified frozen source corpus — shared read-only context

**Status: LIVE and fully verified 2026-09-08 ~02:30Z by the campaign coordinator.**

Every worker — active and newly dispatched — may read this corpus. It is **read-only**
(`chmod -R a-w`), it is **one copy**, and it must **not** be overlaid on the Git working tree.

```
/tmp/claude-0/frozen-corpus/extracted/
    README.md
    corpus/          <- 5,996 selected source files (AGENTS.md, CLAUDE.md, README.md,
                        research/, scripts/, systems/)
    metadata/        <- closed-source-and-ownership-map.md, corpus-manifest.json,
                        member-manifest.json, snapshot-provenance.json, tracked-file-map.txt
```

**ROOT CORRECTION (W21b ~02:58Z, restated here by W35 2026-09-08T03:36Z because it previously
lived only in WAVE-LOG.md): repository-relative paths live under
`/tmp/claude-0/frozen-corpus/extracted/corpus/`, NOT under `.../extracted/`.** Searching the outer
directory finds nothing and looks like absence. A path that resolves under `corpus/` is present; a
path that does not is UNKNOWN, never absent.

**The corpus is read-only by mode (`chmod -R a-w`), but workers run as root (`id -u` = 0), so the
mode is a guard-rail, not enforcement (W35, measured: `test -w` on the corpus root returns
writable). Do not write to it.**

## What was verified, with the actual commands

| Check | Result |
|---|---|
| Supporting ref | `codex/opus-cloud-inputs-20260908` @ `ad34f06b53c2fb41f0b3d7949239b8d2951ac61e` — fetched |
| `reassembly-manifest.json` sha256 | `a9fa1ff6639dec434d60e0b1b7b3954c41f4f73a72160fe422e42cab673d37f7` — **matches** |
| 6 part sha256s | all six **match** the manifest, byte counts 5×8388608 + 3897337 |
| Assembled ZIP bytes | **45,840,377** — matches |
| Assembled ZIP sha256 | `b474cd2f8a0e3fa3a253f5b3135379cb26c15222a94698fc411fd781f6346808` — **matches** |
| Members | **6,002** (1 README + 5,996 under `corpus/` + 5 under `metadata/`) |
| CRC of every member | `ZipFile.testzip()` → `None` (**all 6,002 CRC-clean**) |
| Unsafe member paths | **0** (no absolute paths, no `..` traversal) |
| Symlink members | **0** |
| Uncompressed bytes under `corpus/` | **236,150,544** — matches |
| Per-file provenance | **6,001 / 6,001 sha256 verified against `metadata/member-manifest.json`; 0 mismatches** |
| Snapshot base recorded in the manifest | `93b75888e31976195145e2404373b2d7a512f6d1` |
| Free disk after extraction | 23 GiB (10 GiB floor honoured throughout) |

## What this corpus IS and IS NOT — quoted from its own `snapshot-provenance.json`

- `"identity": "SNAPSHOT OF SELECTED FILES"`, `"is_complete_repository": false`,
  `"contains_git_history": false`, `"is_git_commit_materialization": false`.
- **This is NOT a `93b` Git checkout and NOT imported `93b` ancestry.** Do not claim to have
  checked out `93b` or to have inspected all of its files.
- `"absent_files": "Unknown/unprovided in this selected snapshot. Absence is not evidence of
  repository-wide absence, source novelty or access permission."`
- `metadata/tracked-file-map.txt` is the full tracked-file discovery map for base `93b`. **It
  lists more than what is present under `corpus/`.** A listing does not prove local
  availability, inspection, or inclusion; those files' absence remains **UNKNOWN**.
- `"no_new_source_material": true`, `"no_source_fetch": true`, `"no_scientific_acceptance": true`.
- `metadata/closed-source-and-ownership-map.md` retains the original compact map **verbatim**.
  Existing closures and refusal boundaries remain in force. **This packaging does not authorize
  reviewing, recreating or rerouting the blocked NR4A Perspective.**
- **Historical worker-status wording inside the compact map is not current live ownership.**

## How workers must use it

1. **Before any novelty, absence or identifier claim that depends on prior work**, check this
   corpus. "Not found locally" is now a much weaker claim than it was, and a locally absent
   prior report is **not** source novelty.
2. Use it **alongside** the live cloud checkout at `/home/user/Rare-cancers`. Record which of
   the two you read, and record the actual HEAD of the checkout.
3. **Do not copy it.** One shared read-only directory; no per-worker duplicates.
4. Completed outputs are **preserved**. Where newly received retained evidence contradicts a
   completed report, append a **focused correction**, not a new whole-review round.
5. The earlier source-index capsule and the 47-file evidence capsule remain relevant and
   **retain their original failure/review status**.
