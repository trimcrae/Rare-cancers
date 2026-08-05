# A slug asserts a subject. The manifest must be able to show it.

⛔ **2026-08-05 — `literature/bangerter-2023-emc-exvivo/` was published here containing 25 files about
lomap, Schrödinger's cycle-closure patents, cinnabar, diffnet and FEP protocol papers, and NOT ONE about
Bangerter or about EMC.** It has been removed. Every file in it was byte-identical to
`literature/cycle-closure-verification/` apart from session-cookie codes in five refetched pages, so
nothing was lost — which is the only reason deleting it was the right call rather than a second error.

**How it happened, because the trap is still there.** `fetch-literature.yml` takes a `query` AND a
`slug` AND a `targets_file`. `scripts/lit_fetch_urls.py` reads `LIT_TARGETS_FILE` and falls back to its
built-in `TARGETS` list; only a later step consumes `QUERY`. So dispatching with a `query` and a `slug`
but no `targets_file` re-fetches the built-in corpus and files it under whatever name you chose. The run
reported **success**.

⚠ **A MISLABELLED RECORD IS WORSE THAN A MISSING ONE.** A future session greps this branch and finds a
directory whose name promises the one piece of ex-vivo EMC evidence the repository has been unable to
resolve. Nothing inside would have contradicted the name — the name is the only claim being made, and
nothing checked it.

**The rule:** a slug is a claim about contents. If a run cannot show that its fetch targeted the subject
its slug names, it must not publish under that slug.
