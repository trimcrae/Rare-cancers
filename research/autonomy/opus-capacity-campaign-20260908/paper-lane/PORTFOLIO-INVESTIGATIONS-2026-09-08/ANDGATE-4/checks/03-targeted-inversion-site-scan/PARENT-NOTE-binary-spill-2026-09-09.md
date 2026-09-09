# This check's `stdout.txt` was 86,447,935 bytes and contained NO readable line at all

Unlike `checks/02`, this directory has a **real recorded command** and a **real recorded exit code
(0)**. But its `stdout.txt` was 86 MB in which **1,669 of 1,669 lines contained NUL bytes** — the
same `.tar.gz` spill described in
`../02-exhaustive-inversion-claim-search/PARENT-NOTE-oversized-capture-2026-09-09.md`: the
`grep -rn` matched inside committed archives and streamed their decompressed bytes.

⛔ **I extracted every NUL-free line and got ZERO BYTES.** There were no human-readable grep hits in
this capture — not a reduced set, none. So the correction I first wrote here, that the text hits
were retained, was wrong, and I am not letting it stand: **this capture never held the site-list
evidence.**

**What that means for the lane's finding.** ANDGATE-4's conclusion — that the inversion claim did
not propagate to any shared surface — is carried by `FINDING.md` and `SITE-LIST.md`, which name
each site with file and line. It is **not** carried by this capture, and the `exit 0` recorded here
attaches to a command whose entire output was binary spill. Anyone re-verifying the site list must
re-run the scan with binary files excluded, not read this directory.

**Removed**: the 86 MB binary body, which is decompressed archive content that the archives
themselves already hold byte-for-byte in git. **Retained unchanged**: `command.txt`,
`exit_code.txt` (0) and `stderr.txt`. Nothing was fabricated, no exit code was invented, and the
check was not re-run to manufacture a replacement.
