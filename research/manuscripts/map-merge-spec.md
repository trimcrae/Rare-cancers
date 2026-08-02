# Merge spec — one roadmap, with STRATEGY.md folded in

> ## ⛔ SUPERSEDED IN PART, 2026-08-02 — §1's CENTRAL RULING IS RETIRED. THE MERGE IS PHYSICAL.
> **§1 below says the merge must be "structural, not physical" and that THE ORDERED PLAN, the spend ladder,
> the language-discipline section and the gate scoreboard must stay in STRATEGY.md because seven CI checks
> parse them there. That was implemented, and it produced a RELABELLING, not a merge** — STRATEGY.md stayed
> 3,317 lines against the roadmap's 1,436, with
> [`map-merge-inventory.md`](map-merge-inventory.md) classifying **~2,430** of those lines as live plan
> material. trimcrae: *"Strategy.md and the mapping document are still different files? What is the role of
> strategy anymore?"*
>
> ⛔ **The CI-binding argument was a real constraint but never a reason.** CLAUDE.md §5: engineering effort is
> free, and *"not worth the engineering effort to save X"* is never valid. Every parser was repointed instead.
> **What actually happened:** every live section moved into
> [`nr4a3-program-map.md`](nr4a3-program-map.md) under the heading string and slug it always had;
> `work_ledger.DEFAULT_PLAN_DOC`, `pinned-figures.json`'s `must_appear_in` / `subset_checks.file` /
> `artifact_figures`, and `lint_claims.py`'s 21 provenance strings were repointed in the same commit;
> **Appendix A and Appendix B stayed**, because their rows are read *as data* and Appendix A's heading is a
> structural clear in `lint_consistency.is_cleared`.
>
> **Still live below and unchanged:** §2 (the `R`/`V` id scheme), §3 (the invariants), §4's table of *what*
> each machine parses and how it breaks (only the *file* changed), and §5's list of holes the document must
> render as holes.

★ **trimcrae, 2026-08-02: *"Ideally the map serves as the new source of truth and the strategy.md gets folded
in with it into one document, just adding color. And then it can link to appendices that give more history and
stuff… It's really like a systems engineering task."*** And, on sequencing: *"We shouldn't be executing the
roadmap while we're building it."* Then: *"Build the merged document. Pricing is a nice to have but the
coherent roadmap is the top priority."*

This file is the **contract** for that merge. It is not the merged document; it is what the merged document
must satisfy. It exists because four audits found the map and STRATEGY.md disagreeing in 12 places while
neither could see the other, and because a naive merge breaks CI in seven.

---

## 1 · What goes where — and why NOT "move everything into the map"

**The obvious merge is wrong.** Seven CI checks parse STRATEGY.md **by exact heading string and text format**,
and 100 files carry 358 inbound references to it. Two of its numbering schemes are read *as data*:
`realised_spend.py:167` literally sets `"read_from": "STRATEGY.md Appendix A row 35"`, and Open decision
numbers are cited by 30 files. Nothing resolves either reference, so nothing would fail loudly — the numbers
would just quietly start pointing at the wrong rows.

So the merge is **structural, not physical**:

| layer | owns | lives in | why there |
|---|---|---|---|
| **Requirements** `R*` | what must be TRUE for the paper | the map | new — nothing owns this today |
| **Verification** `V*` | which instrument establishes each `R`, and whether that instrument has itself recovered a known answer | the map | today split between map §3 and STRATEGY.md's five requirements |
| **Dependencies** | the order truths must land in | the map | map §1 |
| **Status** | work-state · authorization · sufficiency (§0/§0b's three axes) | the map | map §0 |
| **Closed routes** | ✕ dead · ⏸ parked · 🔒 held | the map | map §2 |
| **Plan / ladder** | what to DO next, its gate, its price | **STRATEGY.md, unmoved** | `work_ledger.scan_plan_items` parses it |
| **Spend ladder** | what was authorised, cumulative cost | **STRATEGY.md, unmoved** | `lint_consistency.check_subsets` / `check_derivations` |
| **Language discipline** | R1–R5 wording | **STRATEGY.md, unmoved** | 21 `lint_claims.py` provenance strings name it |
| **History** | superseded numbers, retracted claims, dead framings | **STRATEGY.md Appendix A / B, unmoved** | row numbers cited as data by 35 files |

**The map becomes the single thing you read and steer by. STRATEGY.md becomes its appendices** — explicitly
relabelled as such, keeping every heading, slug and row number exactly where CI and 358 references expect
them. That is what "links to appendices that give more history and stuff" means in a repo this wired.

⚠ **This is a real constraint, not conservatism.** A merge that moved the ORDERED PLAN would make
`work_ledger` print *"NOT SCANNED — the plan is invisible this run"* and every open item would vanish from the
work board **silently**.

---

## 2 · The ID scheme — the thing whose absence caused this

Nothing in either document has a stable identifier today, so no one can write "R5 is blocked by V4". That is
**why connections keep being re-derived from prose** and why the same blockers keep being misattributed.

- **`R1…Rn` — requirements.** One per claim the paper must establish. Stable forever; never renumber. A
  retired requirement keeps its number and is marked retired.
- **`V1…Vn` — verification instruments.** One per instrument. Same rule.
- Every plan item, gate, closed-route row and artifact **cites the `R`/`V` it serves.**
- A requirement with **no `V`** is a hole and must render as one — that is the map's main job.
- An instrument that has **not recovered a known answer** cannot raise the confidence of any `R` it serves.
  This is the program's most expensive lesson, stated as a rule the document can enforce rather than as prose.

---

## 3 · The invariants the merged document must hold

1. **A requirement may never be claimed above its instrument's own validation status.** The formal version of
   §3's "instrument layer".
2. **Three axes stay orthogonal** (§0b): **work-state** (✓ ◐ ○ ⏸ ✕), **authorization** (🔓 🔒 —), and
   **sufficiency** (what a pass would and would not license). Collapsing any pair is the error this session
   made four separate times — dead/parked, evidence/status, leverage/authorization, and not-settled/not-started.
3. **✕ means conclusively unworkable**, never "not done yet"; ⏸ names the capability that reopens it; 🔒 names
   the decision it waits on.
4. **A ✓ is a WORK state, never a claim's truth.** The pocket node is the worked example in both directions:
   marked ○ it said nobody had looked, which was false; marked ✓ *"settled enough to build on"* it elided two
   open gates, which was also false. Correct is **✓ work complete · claim supported, not settled.**
5. **Every status cell points at a committed artifact.** A cell with no artifact says so, in those words.
6. **One fact, one place.** Where the map and an appendix both state a number, the map **links** and does not
   restate it.

---

## 4 · Hard bindings — break any of these and CI goes quiet, not red

| binding | what it parses | breakage |
|---|---|---|
| `work_ledger.scan_plan_items` | the `## … THE ORDERED PLAN …` heading, bullet regex ``^(\s*)-\s+\*\*`\[([ x~!–-])\]`\s*(.*)$``, `### <rung>` sub-headings | rename → plan invisible; reformat → open items vanish. ⚠ the skipped marker is an **en dash U+2013**, not a hyphen |
| `lint_consistency.check_subsets` / `check_derivations` | `Cum ~$N` (spine) and `Cum. ~$N` (plan) as **deliberately different** formats | unifying them → `X-pattern-found-nothing` ERROR |
| `lint_claims.py` | 21 provenance strings naming "STRATEGY.md → Honest scope and language discipline" + R1–R5 wording | rename → 21 stale provenance strings |
| `realised_spend.py` | "STRATEGY.md Appendix A row 35" / row 38, read as data | renumber → silently wrong provenance |
| Appendix A row numbers | cited by **35 files**; heading slug used for anchors | freeze numbers AND slug |
| Open decision numbers | cited by **30 files**; nothing resolves them | freeze numbers |
| `pinned-figures.json` | the CI net that catches copied numbers | every changed pinned figure registers its old value **in the same commit** |

**Verification gate for the merge:** `lint_consistency.py` 0 ERROR · `lint_claims.py` 0 ERROR ·
`node scripts/validate.mjs` OK · `pytest research/modalities/tests/ -q` no new failures · `work_ledger`
still scans the plan and reports the **same open-item count as before the merge** — that last one is the
check that catches a silent break, and it must be run and its number quoted.

---

## 5 · Known holes the merged document must render as holes, not smooth over

- **The ternary rebuild has no rung and no price.** STRATEGY.md:500 calls it *"the whole remaining gap"*; it
  appears in no rung, no spine row and no decision-value rank. It was rendered ◐ (in work) when nothing was
  running. It must appear as ○ 🔒 **unpriced**, with "give it a rung and a price" as the named next action.
- **Zero of eleven critical-path rows are moving**, and five wait on a money decision.
- **No claim is ✓-settled**, including the pocket (✓ work, supported-not-settled).
- **`nrv04_feasibility`'s GO is withdrawn**; `dg_open_paralogue` and `abfe_conditional` are 🔒 held;
  **Arm F is unclassified behind a gate that can no longer fire.**
- **Six paper result lanes** had no row until today (§2.9's congeneric RBFE map incl. cycle-closure
  **R = +1.307**, §2.10e's causal matched-pair test, BioEmu, PocketMiner, the unique-lysine axis, MR/AR).
- **Two STALE items inside STRATEGY.md**: `:351`'s header is stamped ~7 h in the future (clock face converted,
  calendar date not), and `:552`'s IN FLIGHT board is 3 days stale and **structurally blind to non-Vast
  rentals** — which is exactly how a SageMaker job launched at 3:16 PM ET, which then failed, appeared on no
  board at all.

⛔ **Do not fix the science while merging.** The merge records what is true today. Where the truth is "this has
no plan", that is the entry.
