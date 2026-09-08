# M1 — source-recovery contract, recorded BEFORE launch

`date -u` **2026-09-08 ~10:52 UTC**. Input revision **18c75f63**. Same parent/controller and session,
`claude-opus-5` **medium**, existing first-party saved subscription — **no paid fallback**, no
overage, no credits, no new controller or permission queue. Deadline **2026-09-09T02:37:19Z**.

Authorised under the **standing workstream authority for ordinary public-source recovery**. This is
**not** a retry or reroute of any held or denied source, and **not** a duplicate of any existing
source task.

## Exact source — one, named

| field | value |
|---|---|
| citation | Bausch-Fluck D, Goldmann U, Muller S, van Oostrum M, Muller M, Schubert OT, Wollscheid B. *The in silico human surfaceome.* PNAS 2018 |
| PMID | **30373828** |
| PMCID | **PMC6243280** |
| DOI | **10.1073/pnas.1808790115** |

## The question

Is the **surfaceome membership table** — the gene-level list — obtainable through this campaign's
**existing first-party tools**? Peer review item 44 asks the surface-targets paper to quantify its
overlap with this resource; `BLOCKER-surface-targets-item44-surfaceome-overlap.md` records that the
table is not committed here and that **retrieval has never been tested**.

## Finite acceptance

1. **Use only existing first-party tools** — the admitted PubMed/PMC route already used in this
   campaign. **No paid access, no credentials, no publisher scraping, no alternative host, no
   payment.** If a route returns a block or an error, **record it verbatim and stop that branch** —
   never route around it.
2. **Report exactly what came back**, in these terms: (a) metadata only; (b) abstract; (c) full text;
   (d) supplementary file list; (e) the actual membership table. **State which.**
3. ⛔ **A source observation is NOT a claim of gene-table recovery and NOT scientific validation.**
   Do not assert the overlap, do not compute it, and do not describe the paper's item 44 as resolved.
   If you obtain a table, your job ends at **recording and retaining it with provenance** — the
   analysis is a separate, later decision.
4. **Retain the original returned artifact and its provenance**: the exact tool call and arguments,
   the response as returned, any identifiers, sizes and hashes. **Do not paraphrase an artifact you
   retained** and do not reconstruct anything from memory.
5. **EARLY STOP is a SUCCESSFUL RESULT.** If the supplementary material is not exposed by the
   available tools, or access is refused or blocked, **stop immediately** and report the exact
   observation. A bounded negative — "this route returns X for this identifier" — is a real finding.
   ⛔ It is **not** a global absence claim: say what the tested route returned, nothing wider.
6. **Write nothing into the repository.** Retain under `/tmp/claude-0/m1-lane/` only; the parent
   integrates. **No git write** of any kind — read-only git only.

## Out of scope

⛔ No global repository census or audit — none is a prerequisite. ⛔ No other source, no second
identifier, no "related article" expansion. ⛔ No manuscript, SI, registry, figure or code edit. ⛔ No
GPU, no paid API, no `scripts/preflight.sh`. Terminal contracts F1, G1, H1, I1, J1, K1, L1 are not
reopened, and their no-network terms bound **those** workers, not this independently admitted task.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, identifier or measurement. If any request of yours is refused by content policy, stop that
branch, record the refusal verbatim, and never route around it.

## Retention

Under `/tmp/claude-0/m1-lane/`: every tool call with its exact arguments, every response as returned,
any downloaded artifact with size and sha256, and a short index. ⛔ **DELETE NOTHING**, including your
own lane — cleanup requires an exact-directory receipt that does not exist.

## Stop conditions

Acceptance 5; the table proving already committed on inspection; any step needing a prohibited action;
or **~25 tool calls / ~25 minutes**, deliberately tighter than the usual bound because this is a
narrow retrieval question. Returning early with a supported result or block is success; padding is
not.
