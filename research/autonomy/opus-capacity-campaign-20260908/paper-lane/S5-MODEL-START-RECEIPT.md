# S5 — model and start receipt (verified from the child transcript, not from the dispatch)

| field | value |
|---|---|
| child id | `a53b0d25fa5e70b56` |
| dispatched | `Tue Sep  8 06:18:xx UTC 2026` (contract recorded `06:17:40 UTC`, `date -u`) |
| verification read | `Tue Sep  8 06:19:38 UTC 2026`, `date -u` |
| transcript at verification | `/tmp/claude-0/.../tasks/a53b0d25fa5e70b56.output`, 141,257 bytes |
| **observed model set in transcript** | **`['claude-opus-5']`** — exactly one value, no other model appears |
| effort / route | medium, existing first-party subscription; no paid fallback, no overage |
| session | `session_01Eui7FVgatEXAwt2N35yHH6` (unchanged) |
| verification method | regex over `"model":"…"` across the raw child transcript; the set is asserted to equal `["claude-opus-5"]`, not inferred from the dispatch parameter |

Running counts at this reading, helpers counted separately:
**research children running: 1** (S5). **Helper/wrapper rows: 0.** A collector or wrapper is not research and is
not counted here.
