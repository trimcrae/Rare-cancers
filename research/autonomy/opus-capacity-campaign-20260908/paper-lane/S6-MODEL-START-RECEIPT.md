# S6 — compact model / start receipt, verified from the child transcript

| field | value |
|---|---|
| child id | `aadf26ebcbd3d3230` |
| status at this reading | **running** (started ~06:30 UTC; `ListAgents` row confirms live) |
| contract recorded | `Tue Sep  8 06:29:42 UTC 2026` (`date -u`) |
| narrowing delivered in flight | `Tue Sep  8 06:34 UTC 2026` — queued to the running child; **no replacement worker** |
| verification read | `Tue Sep  8 06:34:41 UTC 2026` (`date -u`) |
| **observed model set in transcript** | **`['claude-opus-5']`** — one value only, by regex over `"model":"…"` across the raw child transcript; not inferred from the dispatch parameter |
| effort / route | medium, existing first-party subscription — no paid fallback, no overage |
| session | `session_01Eui7FVgatEXAwt2N35yHH6` (unchanged) |
| deadline | `2026-09-09T02:37:19Z` (unchanged) |

**Fresh running counts, helpers separate:** research children running **1** (S6). Helper / wrapper / collector
rows **0** — a collector or wrapper is not research and is not counted here. Disk 20 GiB free (floor 10 GiB).

Prior receipts (S5, S4) and all raw bytes remain intact; nothing was overwritten to produce this one.
