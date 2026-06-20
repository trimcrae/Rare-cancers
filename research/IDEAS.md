# Parked ideas / future-work backlog

Ideas worth doing later but deliberately *not* started yet. Each entry: the idea, why
it matters, rough effort/risk, open questions, and what to check before committing.
Add to this rather than losing ideas in chat. Newest at top.

---

## Modernize & help maintain the TxGNN repo (upstream contribution)

**Status:** parked / idea only (filed 2026-06-20).
**Origin:** while running the real TxGNN model for EMC predictions (roadmap #3, see
`hypotheses/METHODOLOGY.md §7` and `txgnn_predict.py` / `.github/workflows/txgnn-run.yml`)
we hit the exact dependency-rot wall that limits TxGNN's reach.

### The idea
Contribute to [`mims-harvard/TxGNN`](https://github.com/mims-harvard/TxGNN): port the
2023-era stack to a modern one and/or refresh the knowledge graph, so the model is
runnable out-of-the-box in 2026+.

### Why it could be high-value
- **The dependency rot is a real, shared barrier.** TxGNN pins **DGL 0.5.2** + an old
  PyTorch; its `model.py` uses DGL 0.5.2 heterograph/message-passing APIs that broke in
  DGL 0.6→0.7→1.0→2.x. Anyone trying to run it today hits this (we did). A clean
  torch-2.x / DGL-2.x port would unblock many rare-disease researchers — high leverage
  for a small, well-scoped repo.
- **Public good aligned with this project's mission** (lower the information cost of
  repurposing for neglected diseases; see METHODOLOGY §7.4 economics).
- Candidate contributions, roughly in increasing effort:
  1. A **CPU-friendly, pinned, reproducible "run inference for one disease" recipe**
     (basically what we built in `txgnn_predict.py` + the workflow) — could be a docs PR
     or an `examples/` script. Lowest effort, immediately useful.
  2. **Dependency modernization** (torch 2.x + DGL 2.x) — non-trivial: rewrite the
     heterograph layers; the released weights are tied to the old DGL, so behavior must
     be re-validated (likely a retrain or careful weight port).
  3. **Refreshed knowledge graph** (newer PrimeKG / MONDO / DrugBank) — bigger, would
     change predictions, needs re-training and re-benchmarking.

### Effort / risk
- (1) is small and self-contained. (2) and (3) are real research-engineering projects
  (weeks), and a faithful port must preserve or transparently re-validate model behavior,
  or it's no longer "the published TxGNN."

### Open questions — check these BEFORE investing
- **Does the maintainer accept/merge PRs?** Check recent commit date, open/merged PR
  activity, issue responsiveness, and whether a `CONTRIBUTING` exists. As of this note the
  repo looks publication-frozen (README still pins DGL 0.5.2; PyPI `TxGNN` at 0.0.3), so
  confirm it isn't effectively archived before sinking effort. (Our GitHub tooling is
  scoped to `trimcrae/rare-cancers`, so this needs a manual look or a widened scope.)
- Is there an **official successor / maintained fork** already (e.g., a newer Zitnik-lab
  release, or PrimeKG v2 tooling) that's the better contribution target?
- Would a **lightweight standalone "txgnn-runner"** (our pinned wrapper, published
  separately) deliver most of the value (1) without needing upstream buy-in?

### Pointers
- Repo: https://github.com/mims-harvard/TxGNN · Explorer: http://txgnn.org
- Paper: Huang et al., *A foundation model for clinician-centered drug repurposing*,
  Nat Med 2024 (doi:10.1038/s41591-024-03233-x).
- KG on Harvard Dataverse: doi:10.7910/DVN/IXA7BM.
- Our working runner: `research/hypotheses/txgnn_predict.py` + `txgnn-run.yml`.
