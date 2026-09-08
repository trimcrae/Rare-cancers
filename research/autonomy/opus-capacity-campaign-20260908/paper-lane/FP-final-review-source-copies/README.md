# FP final review — byte-exact source copies

**2026-09-08, parent. Ordinary existing-byte intake for the FP final reviewer, whose local repository
does not hold these objects.** A locator alone cannot let that reviewer read them; these are the
bytes.

⛔ **Nothing was fetched.** No network access, no new source request, no literature search, no
workflow, no alternate access route, no denied-route retry, and no reconstruction of any human
original. Every file here came from an object **already present** in this session's Git store.

## Method
`GIT_NO_LAZY_FETCH=1 git cat-file blob <id>` for each of the twelve, so a locally absent object would
have failed loudly rather than silently triggering a fetch. Each extracted byte stream was then
re-hashed with `git hash-object --stdin` and **asserted equal to its own blob id** before being
written, and re-verified on disk against its recorded byte count and sha256 afterwards.

**Result: 12 of 12 copied, 209,455 bytes total, 0 missing, 0 mismatches.** Wrapper bytes are
preserved exactly — these are the objects, not re-renderings of them.

`MANIFEST.json` maps, for every copy: source commit `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`, the
original path, the Git blob id, the byte count and the sha256.

⚠ Four of these (`PMC7563993`, `PMC7999686`, `PMC5400622`, `PMC3534218`) are blobs that also appear
under other named slugs. One blob id is one object; no duplicate copy was made for the alternate
slugs and none is needed.

## ⛔ The Huang Table 1 original is still missing, and this package does not change that

`emc-partner-events-r2/_manifest.json` is **retrieval and identity evidence documenting earlier 403
attempts. It is NOT a delivered Table 1 PDF.** `huang2023_epmc_core.txt` is the Europa PMC core text,
a different object from a publisher table.

**No previously retained human PDF or human extraction original with a known locator exists for Huang
Table 1.** Artifact prose asserting that a human read that table is not such an original. ⛔ No hunt
and no reconstruction was attempted, and none should be inferred from the presence of this directory.

## Scope
Bytes only. No scientific claim, nothing revalidated, no FP edit — the FP paper's independent final
review is running on immutable `f44b75588`.
