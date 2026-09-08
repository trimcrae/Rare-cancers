# L1 — contract, recorded BEFORE launch

`date -u` **Tue Sep  8 10:29:27 UTC 2026**. Input revision **d78868bed7d32faa49b0f8395d1fb803e0e984a1**. Same parent/controller and session, `claude-opus-5`
**medium**, saved first-party subscription — no overage, no credits, no paid fallback. Deadline
**2026-09-09T02:37:19Z**, never extended.

## The issue — measured, not inferred

Peer review **Minor 16/17** asks to "replace the salted-hash jitter with a deterministic offset".
**K1 measured that this is a live defect** ():

`research/modalities/emc_surface_figure.py` computes
`jitter = 0.12 * (hash(g) % 5 - 2)`. Python's string `hash()` is **salted per process**
(`PYTHONHASHSEED` is random by default), so the vertical offset of every marker changes on every
run. K1 ran the **unmodified script twice** and got two different PNGs — `b2a78474…` / 90,465 B and
`e9b3dc4d…` / 90,234 B — both differing from the committed `30b1c25b…` / 91,013 B.

⭐ **A published figure that cannot be reproduced from its own committed code is a reproducibility
defect**, and it also makes any future figure diff unreadable. Only decorative jitter is affected —
no measured quantity — which is what makes this a safe, bounded fix.

## Finite acceptance

1. **Replace the salted hash with a deterministic offset** that is stable across processes and
   machines. It must depend only on committed inputs (e.g. the gene's index in `SHOW`, or a stable
   digest such as `hashlib` over the gene symbol) — **never** on `hash()`, iteration order of an
   unordered set, wall-clock time, RNG without a fixed seed, or the environment.
2. **Prove determinism**: run the modified script **at least twice in separate processes**, and once
   more with a **different `PYTHONHASHSEED`**, and show the output PNG's **sha256 identical every
   time**. Capture exact commands, stdout, stderr and exit codes.
3. **⛔ No measured quantity may change.** The x position (`enrichment_vs_rest`) and the y tier of
   every antigen stay exactly as they are; the NOT EVALUATED band K1 added stays as it is. You are
   changing only the decorative vertical offset. Do not recompute, re-derive or adjust any number, and
   do not alter `SHOW`, `LABEL`, tier mapping, axis limits or captions.
4. **Legibility must not regress**: markers that the old jitter separated must still be separated. If
   a deterministic scheme collides two labels, adjust the scheme — not the data.
5. **Regenerate the committed figure** and record its path, byte size and sha256 before and after.
6. If a note about determinism belongs in the code docstring, add it. **No manuscript edit is required
   or authorised** unless the caption becomes factually wrong — it should not.
7. Gates run and reported honestly with exit codes. ⛔ A tripped gate is a finding to report, never a
   reason to weaken, relax, reorder or edit a gate. ⚠ **`lint_citations` fails repo-wide at exit 1,
   pre-existing** — attribute it and **do not call all gates green**.
8. If determinism cannot be achieved without changing a measured value or harming legibility, **STOP
   and report exactly that**. A supported stop is a successful result.

## ⛔ Isolation

**You may not write, copy, move or restore any file over a shared repository path for a baseline,
comparison or test.** Baselines go **out** to `/tmp/claude-0/l1-lane/` via `git show HEAD:<path> >`
or by copying out — never in. Your only repository writes are `emc_surface_figure.py` and the
regenerated PNG. **No git write** — read-only git only.

## Out of scope

⛔ No DFSP recomputation or any contrast re-analysis. ⛔ No other manuscript, no SI, no registry, no
linter edits. ⛔ No network, no source retrieval, no paid API, no GPU, no `scripts/preflight.sh`.
matplotlib is absent from the sandbox — use the **offline uv wheel cache** as K1 did; **do not install
anything and do not touch the script's own network fetch path**, so CI behaviour stays unchanged.
Terminal contracts F1, G1, H1, I1, J1, K1 are not reopened. There is no wet lab: no EMC efficacy,
safety, selectivity or clinical-readiness claim. Invent no fact, source or measurement.

## Retention

Under `/tmp/claude-0/l1-lane/`: pre- and post-edit copies of every file touched, unified diffs, every
PNG produced with its hash, and every command's stdout/stderr/exit code. ⛔ **DELETE NOTHING**,
including your own lane.

## Stop conditions

Acceptance 8; the jitter already being deterministic on reading; any step needing a prohibited action;
or **~40 tool calls / ~40 minutes**. Early with a supported result or block is success.
