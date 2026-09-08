# Worker role definitions — OPUS-CAPACITY-CAMPAIGN-20260908

These are the intended custom agent definitions. Because no `.claude/agents/` directory exists in
this repository and the subagent registry is fixed at session start, they are **enforced through
the dispatch prompt** rather than through definition files (see MANIFEST deviation 3). The
documented supported control actually exercised is the Agent tool's per-call `model` override.

Common to all twenty:
- `model: opus` (session-configured `claude-opus-5`); effort inherited from session (`medium`).
  Explicitly never Explore / Haiku / Sonnet / Fable, and never a fallback alias.
- `maxTurns` intent: ~40 tool calls, ~40 minutes wall clock, return on stop condition.
- Tools: read/search/compute/web-research. **No git write operations. No publication tools.
  No network egress that circumvents an access control.**
- Write scope: exactly one report path and at most one `code/W##/` directory per worker.

| ID | Lane | Role |
|---|---|---|
| W01 | 1 | EMC expression / multiomics resource + accession-overlap evidence analyst |
| W02 | 2 | Single-cell / spatial / microenvironment resource analyst (transfer-limit discipline) |
| W03 | 3 | Genomic / structural-variant natural-history analyst |
| W04 | 4 | Digital pathology / imaging resource + licence analyst |
| W05 | 5 | Cross-study patient-independence auditor |
| W06 | 6 | Diagnostic delay / referral / molecular-confirmation evidence analyst |
| W07 | 7 | Patient-reported outcome + denominator analyst |
| W08 | 8 | Disease-course / surveillance question designer |
| W09 | 9 | Care-access / referral data analyst |
| W10 | 10 | New primary clinical evidence + supplementary data scout |
| W11 | 11 | Source-index integration engineer (sole owner of source-index changes) |
| W12 | 12 | Windows portability / reproducibility defect engineer |
| W13 | 13 | Provenance / specimen-identity data-contract engineer |
| W14 | 14 | Computation / reproduction bottleneck engineer |
| W15 | 15 | Ingestion / normalisation / evidence-retention engineer |
| W16 | 16 | New clinically important computation author |
| W17 | 17 | Held-out / orthogonal validation analyst |
| W18 | 18 | Statistical methods author (estimand → diagnostics → falsification) |
| W19 | 19 | Computable evidence-synthesis author |
| W20 | 20 | Computational hypothesis author with decisive stop condition |
