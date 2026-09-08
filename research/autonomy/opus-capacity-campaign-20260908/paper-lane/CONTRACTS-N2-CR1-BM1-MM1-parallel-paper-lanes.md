# CONTRACTS — four parallel paper lanes, opened 2026-09-08

Opened by the campaign parent immediately on the throughput correction, and dispatched together
rather than sequentially. Each worker is `claude-opus-5`, read-only, on a **distinct** manuscript that
no prior contract in this directory names. None of them may produce a selection, census, contract or
review-seat artifact: each must return a paper-specific verdict grounded in inputs it actually read,
or a concrete source-grounded improvement.

Recorded here as one file rather than four, to keep the administrative footprint proportionate to the
work.

| worker | paper | the question, and the failure mode it hunts |
|---|---|---|
| **N2** | `research/manuscripts/neoantigen/hla-coverage-emc.md` | Every main-text quantity against the committed artifact leaf that should hold it, plus the epistemic level of each. A predicted peptide-MHC binding score is a prediction, never a measured immunogenicity result. Second part: dispose of the two `bracket-placeholder` submission-residue findings at line 58 (`[Name]`, `[City, Country]`) — fill from repository content or say precisely why not. No institution or city may be invented. |
| **CR1** | `research/manuscripts/methods-record/closed-routes-negative-record.md` | For each route reported closed: quote the stated reason, read the retained closure record it cites, and return SUPPORTED / OVERSTATED / MISATTRIBUTED / NO SOURCE LOCATED. Hunts the three collapses this genre makes — closed on argument stated as closed on experiment, a blocked retrieval stated as failed biology, and one silent inspected source stated as no evidence existing. Explicitly forbidden from reopening or retrying any closed route. |
| **BM1** | `research/manuscripts/dependency/emc-biomarker-selected-classes.md` | For each therapeutic class: what the paper claims, what the cited source actually supports, and at which level. Hunts class inheritance stated as an EMC result. There is no wet lab and no EMC clinical evidence for these classes; a result measured in another disease or a computed prediction must be labelled in the prose, not only in a caveat section. Quantities checked against artifact leaves as well. |
| **MM1** | `research/manuscripts/emc-mortality-mechanisms-paper.md` | Every mortality quantity against `emc-mortality-decomposition.json`, `-inputs.json`, `emc-relative-survival.json`, `emc-terminal-events.json` and `-classified.json`. Hunts a model output presented as observed, a projection presented as a measurement, a decomposition share presented as if its assumptions were established, a denominator whose population differs from the sentence's, and a missing measurement reported as zero. A missing measurement is UNKNOWN, never zero. |

Common to all four: write nothing under `/home/user/Rare-cancers`, no git write, no producer, no
figure generator, no `scripts/preflight.sh`, no gate authored or weakened, no network, no paid API, no
GPU, no publication, no human contact. `reports/W25-*` and every W25 continuation are held and
excluded. Preregistrations are immutable. Absence of a located source is not evidence a claim is
false. Each verdict is specific to its own paper and may not be generalised into a readiness claim
about the repository. Scratch stays under `/tmp/claude-0/<worker>-lane/` and is **not** deleted, so
the parent can retain it. Each records `date -u`, HEAD and `git status --porcelain` at start and end,
and verifies rather than assumes that nothing it measured moved as the parent commits.

Defects are returned as exact single-occurrence string replacements. The parent applies, after
independently re-deriving each claim it acts on. Writers stay isolated; the parent remains the sole
integration owner.
