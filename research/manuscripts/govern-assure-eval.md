# GOVERN/ASSURE — the Trusted-Evals pillar (over-claim eval)

> Build item #1 from [degrader-startup-plan-exo.md](./degrader-startup-plan-exo.md) §5.
> This is the **Trusted Evals** pillar of GOVERN/ASSURE, made operational. Until it existed,
> the plan capped the Intelligence-Stack (I) score at 2 (I is capped at the lowest of the Four
> Pillars). This eval lifts Trusted Evals to ≥3 and is the **Quiet-Drift guard**: a hedge quietly
> softened across many edits is exactly what a human read misses and an automated eval catches.

## What it guards against

The single existential risk for a solo, integrity-first computational shop (plan §1, "the spark"):
a credibility-destroying **over-claim** drifting into a shipped, outward-facing artifact — an implied
efficacy / safety / clinical-readiness claim, an unconditional-binding claim, a "recovered degradation"
claim, or "a drug." It encodes the **language-discipline rules from [STRATEGY.md](../../STRATEGY.md)**
and the repo's medical-integrity rule as automatic checks.

## Two layers: automatic + human

### Layer 1 — automatic lexical eval (runnable)

`scripts/govern-overclaim-lint.mjs` — scans outward-facing artifacts and fails (exit 1) on any
ERROR-severity over-claim.

```
node scripts/govern-overclaim-lint.mjs           # default outward-facing claim artifacts
node scripts/govern-overclaim-lint.mjs --all      # every research/manuscripts/*.md
node scripts/govern-overclaim-lint.mjs <file>...  # a specific grant draft / client deliverable
```

Severity model:
- **ERROR** — banned language; must be fixed before the artifact ships (fails the run).
- **WARN** — a disciplined-form is preferred; confirm the usage is allowed.
- **INFO** — advisory (e.g. prefer "predicted NR4A-paralogue-selective" over a bare
  "NR4A3-selective" label); never fails.

Rules encoded (from STRATEGY.md "Language discipline" + Mandatory Changes 2–4):
efficacy · therapeutic window · clinical readiness · safety claims · cure · proteome-wide selectivity ·
"binds at all" / "does bind" · "true binding likely stronger" · unconditional affinity ·
"recovered degradation" · unqualified "degrades NR4A3" · "selective hit" · "synthesis-ready" ·
"a/the/our/selective drug" (medchem terms like *drug-like*, *druggable*, *drug repurposing* excluded) ·
the 6–12 vs 24–36 matrix-arithmetic reminder.

It is a **lexical guard, not a semantic one** — a clean lint is *necessary, not sufficient*. It does not
replace Layer 2.

**First run (2026-07-19) surfaced two items for human sign-off** (not auto-edited — manuscript wording
is a human decision; line numbers report the paragraph start):
- `nr4a3-degrader-paper-SI.md:~89` [ERROR] — "it makes the degrader's **efficacy** claim quantitative and
  falsifiable." Intent is that the *degradation-response model* is falsifiable; reword to
  "makes the predicted degradation-response behaviour quantitative and falsifiable" to drop "efficacy."
- `nr4a3-degrader-paper.md:~83` [WARN] — "it degrades NR4A3 whether wild-type or in the EMC fusion" —
  generic mechanism description; consider "a degrader would remove NR4A3."

The `--all` sweep also emits INFO advisories to prefer "predicted NR4A-paralogue-selective" over bare
"NR4A3-selective" labels; these are non-failing and reviewed at fold time.

### Layer 2 — human sign-off checklist (the real gate)

Run before ANY of the three irreversible / outward-facing acts (preprint post, grant submit, client
send). These require explicit sign-off per the repo's outward-facing rule; the Human Review Queue is
exactly these three.

- [ ] `govern-overclaim-lint.mjs` passes on the artifact (0 ERROR), and every WARN/INFO consciously
      accepted with a reason.
- [ ] No statement implies efficacy, safety, therapeutic window, or clinical readiness.
- [ ] Every quantitative result is labelled either **benchmarked** (accuracy vs a public known-answer)
      or **conditional/precision-only** (converged but not accuracy-validated) — never presented as
      unconditional accuracy.
- [ ] Binding/affinity claims are conditional on the modeled open state (ΔG_bind|open), or ΔG_open is
      integrated — no unconditional-affinity claim.
- [ ] Degradation language is **directional concordance / surrogate score**, never "recovered degradation."
- [ ] Candidate language: "predicted selective candidate," "predicted NR4A-paralogue-selective," and
      "computationally prioritized … candidate matrix" — never "selective hit," "synthesis-ready," or "drug."
- [ ] The parent-warhead liability (e.g. MYC induction) is disclosed where relevant, not omitted.
- [ ] Every clinical fact / statistic / citation is real, cited, and verified (medical-integrity rule);
      any synthetic/sample data is bannered.
- [ ] Matrix arithmetic is stated as 24–36 primary before controls, with the preregistered downselection
      to 6–12 made explicit.
- [ ] Source attribution preserved for any republished framework material.

**Pass = automatic eval green AND every checklist box ticked with a named human (the founder) signing off.**
This is the Fiduciary Wedge for outward-facing artifacts: one named human owner per shipped claim.

## CI hook (optional, $0)

The lint can be wired into an existing on-main `workflow_dispatch` CI as a $0 gate before posting, or run
locally. It is intentionally fast and dependency-free (pure Node, no install), matching the repo's
"no build step" convention.
