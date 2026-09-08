# Rename note — `01-source-bindings-attempt1.stdout.json` → `.stdout.EMPTY.txt`

**2026-09-08, by the integrating parent. The file's bytes are unchanged; only its name changed.**

`research/autonomy/push_guard.py` (AUT-PD-144) parses every `.json` path at the commit being pushed
as a single JSON document, and refused the push because this file does not parse.

**It does not parse because it is 0 bytes.** TD1's attempt 1 exited 1 on a cp1252 decode of a UTF-8
artifact; the diagnostic went to **stderr** and stdout was genuinely **empty**. The capture is
correct — an empty stdout is exactly what that attempt produced, and it is evidence of the failure,
not a missing file.

| | before | after |
|---|---|---|
| name | `01-source-bindings-attempt1.stdout.json` | `01-source-bindings-attempt1.stdout.EMPTY.txt` |
| bytes | 0 | 0 |
| sha256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

(That hash is the sha256 of the empty string, as it must be.)

⛔ **Nothing was written into the file to make it parse.** Writing `{}` or `null` into an empty
capture would fabricate output that the run never produced. ⛔ **The guard was not changed,
relaxed or bypassed.** It found a real mislabel — a stream named as a document — and the mislabel
was fixed. The failing run, its stderr and its measured exit 1 stay exactly as recorded in
`CHECK-RUN-RECORD.txt` / `checks/README.md`.

This is the same class of defect as the earlier `BEFORE-ghost-witness-patterns.json` rename, and was
resolved the same way: correct the label, never the check.
