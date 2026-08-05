---
id: DOC-ARCHIVE
title: Archive — nothing here is live
kind: index
status: historical
canonical_for: []
purpose: Say plainly that nothing in this directory is current, and where to find what replaced it.
scope: The archive directory. It owns no fact and asserts no status about the live program.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-05
last_verified: 2026-08-05
---

# Archive

⛔ **NOTHING IN THIS DIRECTORY IS LIVE.** Every file here is kept for provenance — so that a claim,
a number or a decision can be traced back to what was believed at the time — and for no other reason.

**Do not cite anything here as current.** Every file has a forwarding row in
[`systems/MIGRATION.md`](../systems/MIGRATION.md) §3 naming what replaced it and where the information
now lives.

## What qualifies

A document is archived only when **all** of these hold:

1. Its own frontmatter says `status: historical` or `superseded`, or its content is a one-off record of
   a moment that has passed.
2. **It has zero inbound references**, verified across every file type in the repository — not just
   Markdown links. Anything with a referrer is repointed in the same commit or is not moved at all.
3. It is **not** a preregistration. A preregistration's entire value is that it was written before the
   result; it stays where it is, permanently, as `status: immutable`.
4. It is **not** read at runtime by any module or workflow, and **not** named in
   `pinned-figures.json` `targets`.
5. Its own banner does not say its results are still pending.

⚠ **Rules 4 and 5 exist because both nearly caught something.** A link sweep found three references
that break at *runtime or in CI* rather than as dead links — a script that `open()`s a file, a lint
target whose absence is an ERROR, and a workflow that `awk`s a table out of one. And one document that
looked stale by every other measure still carries fifteen pending-result markers, so it is live.

⚠ **A date in a filename is a hint, not a verdict.** Two documents here looked like one-off reports and
are not archived at all: both are two days old and are cited by the systems model itself. `kind` and
`status` decide.

## Layout

The path shape mirrors where each file used to live, so an old path is easy to translate:

```
archive/manuscripts/   ← research/manuscripts/
archive/modalities/    ← research/modalities/
archive/research/      ← research/
```
