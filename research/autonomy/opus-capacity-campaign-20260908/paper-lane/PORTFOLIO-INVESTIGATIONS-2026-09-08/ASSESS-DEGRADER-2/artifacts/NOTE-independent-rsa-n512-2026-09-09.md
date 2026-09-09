# Why `independent-rsa-n512` is zero bytes and no longer ends in `.json`

`independent-rsa-n512.json` was **0 bytes**, sha256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` — which is the sha256 of the
empty string. Its write was killed mid-flight by the session-wide `ENOSPC` recorded in
`../../../RESOURCE-INCIDENT-2026-09-09.md`; the n=512 quadrature run produced no output file.

`research/autonomy/push_guard.py` (AUT-PD-144) parses every `.json` path at the pushed commit as a
single JSON document, and a zero-byte file cannot parse, so the push was refused. **The file was
renamed, not filled.** Its bytes are unchanged — still zero, still that hash. Nothing was written
into it, and `push_guard.py` was not touched.

⚠ The n=512 quadrature RESULT is not lost: `ASSESS-DEGRADER-2/FINDING.md` reports it — refining
n_points from 96 to 512 moves frame `fp_99_az0_ci9r` from 0.1870 to 0.2180 while the ceiling moves
only 0.2126 to 0.2142, so the headline becomes 73/75 rather than 72/75. What is lost is the
machine-readable artifact backing that number. It is therefore **reported, not independently
re-checkable from this lane**, and should be regenerated before anyone relies on the integer.
`independent-rsa-n96.json` (12,422 B, `9908e98c…`) survived intact.
