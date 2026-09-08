# Root qualifications on the closed source checkpoints — carried, not re-audited

**Date 2026-09-08. Root read and hash-verified the actual reports at `b7fc3e2c6`.**
⛔ No auditor was created, no check was re-run and no healthy worker was interrupted to produce this
record. It carries corrections; it does not re-measure them.

## B1/B2 — CLOSED DENIED in this runtime

⚠ **Request count, corrected.** The original report records **TWO HEAD requests**, to two distinct
cDNA and ncRNA resources on `ftp.ensembl.org:443`, both `CONNECT 403`, at **19:22:04.870** and
**19:22:05.208**. ⛔ My earlier commit message said "one probe". **Two, not one** — the exact count
is preserved here because it is the evidence of what was actually attempted.

**Nothing is admitted onward.** No source was delivered. No dependent B1/B2 analysis, no repeated
host probe, no alternate host, **no CI/Actions source fetch**, and no transcript or sequence update.
⚠ The report's §5, describing an existing workflow as an onward route, is **ONLY A PROPOSAL — not
permission to bypass this recorded denial.** The historical derived mapping, the unknown release and
the missing raw snapshots all remain as they are.

### Narrow B1 qualifications — scope corrections to claims I carried too strongly
1. ⚠ **A `current_fasta` locator without identity does NOT prove its bytes actually changed since
   2 September.** Absence of a pinned release means the identity is unknown, not that it moved.
2. ⚠ **A different release MAY alter the mapping; it does NOT necessarily alter the 906 / 77 / 662
   split.** My commit wrote that a different release "moves probes across" that split. That is
   stronger than the evidence: the correct statement is that it *may*, and that nothing here
   establishes it does.
3. ⚠ **The gzip sizes are ESTIMATES** — not measured lower bounds and not `Content-Length`. They
   refute the proposal's "44.3 MB" as unverified; they are not themselves a measurement.
4. ⚠ **No future fetch has yet established either equality with or difference from the historical
   inputs.** Nothing has been compared, because nothing was retrieved.
5. ⛔ **Keep every source-absence statement scoped to the retained evidence**, never as global
   absence.

## B4 — CLOSED DENIED for the one new publisher route

The single new PNAS publisher route returned `CONNECT 403` at **19:22:18**. Item 44 remains **open**.
No supplement was delivered, and no dependent membership comparison, retry or alternate route is
admitted.

⚠ **Do not describe the earlier PubMed/PMC tool calls as egress denied.** They **succeeded** — they
returned metadata, abstract and full text — and simply **did not expose supplement assets**. That is
a different fact from a blocked route, and conflating them would misstate what the tooling can do.

## FO figure/estimand mismatch — figure identity corrected

⚠ The generator's `fig_matrix` output is **`fig4-instrument-convergence`, NOT `fig2`**. Verified by
the parent at `nr4a3_fusion_targets_figures.py:472`, with `fig2-evidence-classes` being `fig_classes`
at line 470. `ADJUDICATION-FO-figure-estimand-mismatch.md` has been corrected in place with the
correction dated and the earlier wording named. The mismatch itself is unchanged — only the figure it
lands on.

⛔ **The actual rendered label and estimand still need targeted adjudication.** No figure producer
run, no redraw, and **no global plot acceptance follows from a metadata update.**

## Production artifacts — collected, NOT accepted

⚠ The four PDF/stamp pairs, the I1 shim fix, the figure-provenance equivalence entry and the graph
bytes have been **collected**. They are **NOT root-accepted merely because the files exist.**
Acceptance is a separate decision root has not taken.
