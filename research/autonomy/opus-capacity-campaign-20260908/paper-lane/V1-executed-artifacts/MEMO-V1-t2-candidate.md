# MEMO — V1: a NEW working revision of the repurposing manuscript on the committed baseline

⛔ **PROPOSED. Nothing is applied.** No shared repository path was written, no git write, no network,
no figure regeneration, no registry or patient-facing change, nothing deleted. This is **not** a
recovered original: it is an explicitly new working revision built on the current committed file.

## Provenance

| item | value |
|---|---|
| start `date -u` | 2026-09-08 11:46:25 UTC |
| start `git rev-parse HEAD` | `0330edbef9e85276ec518dbf2c445bf1d026fd26` |
| start `git status --porcelain` | empty (clean tree) |
| baseline file | `research/manuscripts/repurposing/repurposing-hypotheses.md`, 711 lines |
| baseline check | byte-identical to R2's `BASELINE-repurposing-hypotheses.md` (verified by `diff`, exit 0) |
| candidate | `V1-CANDIDATE-repurposing-hypotheses.md`, 736 lines |

Note: the contract names input revision `cc75a486…` and R2's memo names `cc23cd1d…`; the working tree
HEAD is `0330edbe…`. The **file content** of the baseline is identical to R2's captured baseline, so
the manuscript baseline is unambiguous regardless of which revision label is used. Recorded, not
resolved — no history hunt was run.

## The premise applied (coordinator's decision, not reopened)

T2 adopted on the assembled record's **case-level signal**; **four tiers retained**, T3 **defined but
unoccupied**; baseline = the committed manuscript; **no clinical efficacy finding follows**.

## What changed — eight edits, four target locations plus the tier definition

1. **§2.2 tier definitions** — R2's occupancy sentence retained verbatim; the definitions themselves,
   the T3 threshold and the tier wording are **untouched**.
2. **§2.6 firewall prose** — rule text preserved; recast as the *stated and intended* criterion, with
   the registry mismatch and its unresolved status disclosed in the body.
3. **Figure 1 alt text** — rule preserved, recast as "stated admission criterion", mismatch disclosed.
4. **Figure 1 printed caption** — same recast and disclosure, pointing to §4 and §5.
5. **§4 Tranche 1, grade sentence** — T3 → T2, with the **narrow** rationale.
6. **§4 Tranche 1, registry sentence** — mismatch disclosed at the point where the listing is described.
7. **§5 first limitation** — "only imatinib reaching T3" → "no candidate reaches T3 … graded T2".
8. **§5 ethics firewall** — threshold and clinician-review requirement **verbatim unchanged**; the
   *enforcement* claim recast; mismatch disclosed; conformance marked unresolved.

## The rationale, narrowed

R2's overgeneralised sentence — *"A single case report is neither prospective nor substantial, so it
does not meet this paper's definition of T3."* — is **removed and not used anywhere**. The replacement:

> The assembled record supplies a case-level signal and does not establish the prospective or
> substantial EMC clinical evidence that this paper's definitions require for T3.

Nothing here implies that the case report [7] was newly read. Reference [7] is assessed **as the
committed manuscript characterises it**, exactly as in R2's memo.

## The firewall — description corrected, rule intact

**Unchanged, verbatim, in §5:** "only a candidate reaching direct EMC clinical evidence at T3 may
migrate into the project's cited clinical registry, and then only after clinician review." The T0–T2
exclusion sentence is likewise preserved in substance ("are kept out of all patient-facing material").

**Corrected:** the implicit claim of full enforcement. **Disclosed in the body** (§2.6, §4 and §5, not
in an editorial comment): under the adopted T2 grade the existing imatinib registry listing falls
below the stated criterion, and **registry conformance is unresolved**.

**Explicitly NOT done:** no clinician approval, authorised exception, prospective-only scope, or any
other resolution of clinical governance is asserted; the registry, the patient-facing artifacts, the
tier definitions and the admission threshold are untouched.

## Invariants verified (measured, not asserted)

- **Reference list byte-identical**: `sha256` of everything from `## 9. References` to EOF is
  `6d5f11139792bca06a4905e4a87dd66c98ba7759a40ee0229f168b29ac4f009a` in **both** files.
- **Citation tokens identical**: per-reference `[n]` counts match exactly across baseline and
  candidate ([1]×6, [2]×2, [3]×1, [4]×1, [5]×2, [6]×1, [7]×4, [9]×3, [10]×1, [11]×1, [12]×4, [13]×6,
  [14]×3, [15]×2, [16]×4, [17]×1, [18]×1, [19]×1, [20]×1, [21]×2, [22]×2). No addition, removal or
  renumbering.
- **Counts preserved**: "14" ×6 in both; "3 years of disease stabilisation" preserved; "seven" ×3;
  abstract "tier from T0 to T3" retained (four tiers).
- **Removals are exactly the seven intended sentences** (whitespace-normalised sentence-set diff): the
  §2.6 firewall sentence, the alt-text firewall clause, the printed-caption firewall sentence, the
  §4 grade sentence, the §4 "what remains open" sentence, the §5 first-limitation sentence, and the
  §5 firewall sentence. **No scientific negative, limitation, hedge or uncertainty statement was
  removed** — "Target-level plausibility does not guarantee clinical activity" and every §5/§6
  limitation survive intact.

## The figure — NO change needed, and none made

U2's terminal result is reused and **was not re-inspected**: `repurposing-fig1-design.png`,
177,415 B, sha256 `f711ea7f2c4fd3e4c3d26cfacc61519db5018fb40dcf87c208e1b45ac3ca2075`, rendering
`14 existing drugs, tiers T0–T3` and `T3 plus clinician review only`.

Under the adopted decision **neither label needs to change**:

- `14 existing drugs, tiers T0–T3` states the **range of the scale**, not which tiers are occupied.
  Four tiers are retained, so the range is still T0–T3 and the label is still true.
- `T3 plus clinician review only` states the **admission rule**, which is deliberately unchanged. The
  correction is to the claim that the rule is fully enforced — a claim the figure does not make, and
  which is a property of the registry rather than of the diagram.
- The caption already says "after clinician review", so the caption/figure agreement U2 settled is
  preserved; the caption gains only the stated-criterion recast and the unresolved-conformance note.

Therefore: **the generator was not copied, not modified and not run; no figure was regenerated; the
committed PNG is untouched.** Relabelling would in any case validate nothing about clinical
governance or treatment evidence.

## Validation scope — what was verified vs what is asserted

**Verified by execution in this lane:**
- baseline file byte-identity against R2's captured baseline (`diff`, exit 0);
- all eight edit anchors matched **exactly once** each (the apply script exits non-zero otherwise);
- reference-section sha256 identity; per-reference citation-token counts; key count tokens;
- the whitespace-normalised sentence-set diff (7 removed, 19 added).

**Asserted, not verified here:**
- editorial and scientific adequacy of the new wording — the coordinator's call;
- that the T2 grade is correct (that is the adopted premise, from R2's analysis of the committed text);
- anything about the case report [7] beyond how the committed manuscript describes it;
- anything about the rendered figure beyond U2's terminal measurement.

**Not run:** `scripts/preflight.sh`, any repository gate, any link/citation-integrity checker, any
build of the manuscript, any figure generator. No network, no paid API, no GPU.

## Exact remaining dependencies

1. **Registry conformance is unresolved** — a clinical-governance decision for the responsible
   clinician/owner. The candidate discloses it and resolves nothing.
2. **`research/data/emc-clinical-registry.json`** still lists imatinib; unchanged by this lane, and
   whether it should stay, move or be annotated is dependency 1.
3. **Whether the four-tier / three-tier arity decision stays settled** — the coordinator adopted four
   tiers; R2's Option B fragments remain unused and unapplied.
4. **Integration** — applying this candidate to the shared path, and any gate run, is the scientific
   coordinator's decision. Nothing here is committed.
5. **The revision-label discrepancy** (`cc75a486` / `cc23cd1d` / HEAD `0330edbe`) is recorded, not
   resolved; the file content baseline is unambiguous.
6. **R2's memo item 6** (reference-count mismatch 25 vs 22) remains untouched and out of scope.
7. **Figure**: no dependency remains under four tiers retained. If the arity decision were ever
   reopened to three tiers, both labels and the alt text would need to change together.

## Retained artifacts

All in `/tmp/claude-0/v1-lane/` — nothing deleted:

- `BASELINE-committed-repurposing-hypotheses.md` — the committed baseline as read
- `V1-CANDIDATE-repurposing-hypotheses.md` — the new proposed manuscript
- `V1-CANDIDATE-vs-committed.diff` — its diff against the baseline
- `apply_v1_edits.py` — the exact, re-runnable edit script
- `MEMO-V1-t2-candidate.md` — this memo
- `VALIDATION-LOG.md` — commands, exits and hashes
- `R2-original-proposal/` — R2's separate, unmodified proposal (memo, candidate, diff)

## End-state record

| item | value |
|---|---|
| end `date -u` | 2026-09-08 11:49:55 UTC |
| end `git rev-parse HEAD` | `3be62db0eb09fe0c918cd72d4cad406fc7be6c6e` |
| end `git status --porcelain` | empty (clean tree) |

HEAD advanced during this lane (other campaign lanes committed their collections). Verified by
`git diff --stat` that the move touched **no** manuscript, figure or registry path used here, and the
committed `repurposing-hypotheses.md` is **still byte-identical** to the baseline captured at start.
V1 wrote nothing to the repository; the tree is clean at both ends.

Caveat on `VALIDATION-LOG.md`: its own sha256 in that file was computed while the file was still being
written, so that one line is stale by construction; every other hash in it is final.
