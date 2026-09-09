# checks/02 — exit code lost to a harness resource failure; NOT fabricated

The repo-wide sweep in `command.txt` ran and its `stdout.txt` (1450+ lines) and `stderr.txt` were
written. **The `echo $? > exit_code.txt` write then failed**, because the Claude Code harness's own
temp filesystem
(`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/tasks`) hit
**ENOSPC — 0 MB free** mid-command. The Bash tool was fully unavailable for several minutes
afterwards (even `echo probe` returned the ENOSPC error), then recovered on its own.

`exit_code.txt` therefore reads `UNKNOWN — NOT RECORDED, NOT FABRICATED`. A plausible code was
**not** invented, and the check was **not** silently re-run over the top of the surviving evidence.

**Nothing was deleted to free space.** Per CLAUDE.md §8, campaign task evidence is not removed for
disk headroom; the resource problem is reported here and in FINDING.md instead. The full free-space
diagnosis could not be run because `df` itself could not execute during the outage.

**The finding does not depend on this check.** `checks/03` re-ran the same search as a targeted,
per-target scan with real per-block exit codes (including the load-bearing `exit 1` on
`pinned-figures.json`) after Bash recovered, and `stdout.txt` here is preserved as the corroborating
first pass.
