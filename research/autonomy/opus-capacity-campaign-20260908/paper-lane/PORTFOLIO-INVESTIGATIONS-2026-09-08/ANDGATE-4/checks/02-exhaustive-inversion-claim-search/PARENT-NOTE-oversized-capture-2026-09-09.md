# ⛔ This check's `stdout.txt` was 11,874,455,552 bytes, and it is the cause of the campaign-wide ENOSPC

## What the object actually was

`stdout.txt` here was **11.87 GB**. The lane's own `NOTE.md` (retained above, unedited) describes it
as "1450+ lines" — **that description does not match the object**, and the lane never learned
otherwise, because the failure that stopped it from measuring the file is the same failure the file
caused.

The lane's own `stderr.txt` shows the mechanism, in its last lines:

```
grep: ./research/autonomy/.../collected/s3-repair-originals-20260908.tar.gz: binary file matches
grep: ./research/autonomy/.../collected/campaign-b2-promotion-originals-20260908.tar.gz: binary file matches
grep: write error: No space left on device
head: error writing 'standard output': No space left on device
```

A repository-wide sweep matched **inside committed `.tar.gz` archives** and streamed their
decompressed bytes to stdout until the volume filled. That single capture is what exhausted the
session's writable space at about 01:38Z, and it is what broke DISCOVERY-2 (which then could not
`mkdir` its own lane at all), ENDPOINT-2 (which lost its `FINDING.md` and regeneration check),
MODALITY-CENSUS-2's run 04, ASSESS-EMC-PROGRAM-1's Bash tool, and this lane's own
`exit_code.txt` write.

⚠ `command.txt` in this directory is **0 bytes** — the command was never recorded — and
`exit_code.txt` reads `UNKNOWN — NOT RECORDED, NOT FABRICATED`. So the object had **neither a
recorded invocation nor a recorded exit code**.

## What the parent did, and did not do

The 11.87 GB body was **removed by the parent**, not by the lane. GitHub refuses any file over
100 MB (`GH001`), so it could not be pushed and was blocking every subsequent checkpoint.

**Preserved instead**, all in this directory: the first **200,000 bytes** as
`stdout.FIRST-200KB-EXCERPT.txt`, showing the target-set header and the beginning of the real
grep output; the complete 13,055-byte `stderr.txt`, which is where the diagnosis lives; the empty
`command.txt` and the honest `exit_code.txt`, both unchanged; and the lane's own `NOTE.md`.

**Nothing was fabricated and nothing was re-run over the top.** No sha256 of the 11.87 GB body was
computed — reading 11.87 GB to hash a file that is mostly accidental binary spill is itself the
resource cost this note exists to stop.

## Why this is not a loss of evidence

The lane's finding does not rest on this capture. `checks/03-targeted-inversion-site-scan` re-ran
the same search as a targeted per-target scan **with real per-block exit codes**, including the
load-bearing `exit 1` on `pinned-figures.json`, and that directory is retained in full. The
substantive result — that the inversion claim did not propagate to any shared surface — is carried
by `FINDING.md`, `SITE-LIST.md` and `checks/03`.

## The rule this produces

A repository-wide `grep` must exclude binary files and archives, or bound its own output. An
unbounded capture is not more evidence; here it was 11.87 GB of decompressed tarball that cost five
other lanes their work.
