# Rename note — `BEFORE-ghost-witness-patterns` suffix corrected

**2026-09-08, parent. Rename ONLY. The bytes are unchanged and were verified identical by sha256
before and after.**

`BEFORE-ghost-witness-patterns.json` was rejected by the repository's pre-push integrity guard, which
parses every `.json` path as a single JSON document. The file is **not** one: it is two concatenated
pretty-printed JSON objects — a JSON *stream* — so the `.json` suffix described it inaccurately and
the guard was right to refuse it.

Renamed to **`BEFORE-ghost-witness-patterns.jsonstream.txt`**, which states what the file actually is.

⛔ **The guard was not weakened, disabled or exempted**, and no content was edited, reformatted,
split or deleted. This is the correct direction: the guard found a real mislabel, and the mislabel was
fixed rather than the check.
