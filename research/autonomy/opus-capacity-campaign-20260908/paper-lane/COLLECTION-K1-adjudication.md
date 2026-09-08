# K1 — collection and adjudication against `CONTRACT-K1-figure1-marker-in-empty-quadrant.md`

Collected 2026-09-08 10:26–10:32 UTC from retained originals. No re-run of K1's work, no restart.

## Child identity — from the transcript, including full lifetime

| item | measured |
|---|---|
| child | `af7ad52123f8eeccd` |
| original JSONL | `K1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-af7ad52123f8eeccd.jsonl`, **575,192 B**, `cmp`-identical |
| model strings | **51 × `claude-opus-5`, 0 others** |
| tool pairs | **30** (self-reported 18 — a **sixth** consecutive undercount) |
| **full lifetime** | **10:19:54.163Z → 10:25:50.927Z** (~5 m 57 s), not the narrower tool window |

## Scope — exactly three paths, verified

`git status --porcelain` shows only `emc_surface_figure.py`, `emc-surface-target-landscape.md` and the
regenerated `emc-surface-prioritization.png`. **Isolation held**: no file was copied *into* the
repository for a baseline or test — the rule tightened after J1 was obeyed. No git write by the child.

## Acceptance, adjudicated

1. **No marker in a region captioned empty — MET.** Value-less antigens are moved out of the plotted
   area into a physically separate right-hand panel with no x-axis, no ticks and **no selectivity
   scale**, grey hatched, headed "NOT EVALUATED / no selectivity value / **(not a measured zero)**".
   The quadrant text changed from "— EMPTY" to "no EVALUATED antigen here".
2. **Caption and drawing agree — MET.** Both the code title/docstring and the manuscript's Figure 1
   caption now describe the band and name its occupants.
3. **⭐ No measured value moved — MET, and I verified this independently rather than accepting it.**
   - From the committed artifact `emc-surfaceome-scan.json`, walked myself: of the 13 `SHOW` genes,
     **exactly two have `enrichment_vs_rest = None` — `SSTR2` and `B4GALNT1`**. Every other gene has a
     value (e.g. ALCAM −1.45). So only value-less genes were diverted.
   - The diff's removed numeric literals are only `0.0` (the fabricated x-position), `2.0` and `3.35`
     (the old caption's coordinates). **No enrichment value, `SHOW`, `LABEL` or tier mapping changed.**
   - Autoscale could have shifted the survivors when two points left the panel, so K1 **pinned**
     `ax.set_xlim(-2.5205, 4.3105)` — the exact limits it measured from the **unmodified HEAD script**.
     Every evaluated antigen keeps its position.
4. **Figure regenerated — MET.** `emc-surface-prioritization.png` **91,013 B `30b1c25b…`** →
   **126,861 B `e3805cf1…`**, hashes matching the child's report. Run offline from the uv wheel cache;
   matplotlib is absent from the sandbox and **no network and no spend** were used. The repo script's
   own network fetch path was **not modified**, so CI behaviour is unchanged.
5. **No overclaim — MET.** The band asserts no selectivity, consistent with Table 1's "not in the scan
   output / not evaluated / RESTRICTED".
6. **Gates — MET, and NOT all green.** My own run: `lint_consistency`, `submission_metrics`,
   `lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry` all **exit 0**;
   `submission_metrics` reports the paper unchanged at main 4,994 / abstract 200 / 6 items / 18 refs.
   **`lint_citations` exits 1** — pre-existing, and its output names K1's two edited files **0 times**.
   ⚠ **One correction to the child's report:** it called its citation stdout byte-identical to J1's.
   At my collection time it is **not** — the summary line reads **299 unanchored** where J1's read
   **302**, a two-line difference. That delta arises **outside K1's paths**, from files committed to
   the tree between the two runs; it is not caused by K1, but "byte-identical" is no longer accurate
   and is corrected here rather than repeated.

## Findings K1 raised, routed not fixed

- **⚠ Pre-existing figure nondeterminism.** `jitter = 0.12 * (hash(g) % 5 - 2)` uses Python's salted
  string hash, so **any** regeneration reshuffles within-tier vertical decoration. K1 demonstrated it
  by running the **unmodified HEAD script twice**, producing two different PNGs (`b2a78474…` /
  90,465 B and `e9b3dc4d…` / 90,234 B), both differing from the committed `30b1c25b…` / 91,013 B.
  This is the review's **Minor 16/17** ("replace the salted-hash jitter with a deterministic offset"),
  explicitly outside K1's contract. **Left untouched and recorded as open.** No *measured* quantity
  (enrichment x, window tier y) is affected — only decorative jitter.
- **SSTR2 had the identical defect and the review named only B4GALNT1.** K1 fixed both under the same
  rule. That is correct generalisation of a stated principle, not scope creep: the acceptance term was
  "a gene with no selectivity value", not "this gene".

## Standing

**Not publication acceptance.** `lint_citations` is red, the jitter nondeterminism is open, the
abstract's n = 4 / n = 6 residue is open, the DFSP-only sensitivity analysis remains undone and out of
scope, and the F1 publisher/cross-version/Appendix A blockers are untouched.

## Retention

`/tmp/claude-0/k1-lane/` **intact, nothing deleted**, pending an exact-directory receipt. In-repo copy
`K1-executed-artifacts/` with a self-exclusive manifest.


---

# Three corrections and one QA result, appended 2026-09-08 10:44 UTC — originals preserved

## 1 · My citation-lint "correction" of K1 was wrong, and is withdrawn

Above I wrote that K1's byte-identical claim was "no longer accurate" because my run reported **299
unanchored** where J1 read **302**. **I compared the wrong file.** K1 claimed identity for **its own
retained output**, and that claim is **true**:

```
K1-executed-artifacts/logs/lint_citations.out   167,870 B
J1-executed-artifacts/lint_citations.AFTER.out  167,870 B
cmp -> BYTE-IDENTICAL
```

**The child's result stands as stated.** My 299-vs-302 reading is a **separate observation at a
different tree state and with a different capture method** (I merged stderr on the first attempt),
taken minutes later after further commits. It does **not** refute K1.

⚠ **And the cause of that later delta is NOT established.** I wrote that it "arises outside K1's
paths, from files committed between the runs". The only evidence I actually have is that
`lint_citations` output names K1's two edited files **zero times** — which is **not** by itself causal
attribution to any particular outside commit. **The cause of the 302 -> 299 change is unproven and is
left unproven**; no rerun or attribution hunt was performed for it. Both records are preserved with
their own timestamps and commands.

## 2 · "Every evaluated antigen keeps its position" was too strong

That phrasing is qualified: it holds for **measured coordinates and tier values** — the x value
(`enrichment_vs_rest`) and the integer window tier — which are provably unchanged. It does **not**
hold for **full plotted pixel positions**: at K1's revision the vertical decoration still came from
the salted-hash jitter K1 itself recorded as nondeterministic, so the rendered offsets varied between
runs. **The distinct PNGs are preserved** (`fig/after.png`, `fig/head_rerun_A.png`,
`fig/head_rerun_B.png`) rather than treated as interchangeable.

## 3 · Visual QA: K1's rendering had a label collision; L1's fix resolved it

The intake's visual finding is **confirmed by my own inspection of the retained images**:

- **`K1-executed-artifacts/fig/after.png`** — `NCAM1/CD56` and `KIT` sit at the same vertical offset
  in the VITAL/IMMUNE tier and their labels **overlap**, rendering as `NCAM1/CD5` `KIT` run together.
- **The committed figure after L1** (`research/modalities/emc-surface-prioritization.png`,
  `130042b6...`, 128,250 B) — `KIT` now sits a step lower than `NCAM1/CD56` and **both labels read
  cleanly and separately**.

So the collision was an artifact of the salted-hash offset that happened to give those two the same
jitter in that one render. **L1's deterministic offset resolved it, and no cosmetic label-offset
treatment is needed.** No measured value was involved at any point, and no further figure task is
opened. Had the collision survived, L1's contract term 4 (legibility must not regress) would have
required a scheme adjustment, never a data change.

## 4 · The missing bytecode file is delivered

`pre/__pycache__/emc_surface_figure.cpython-311.pyc` (**7,418 B**, sha256 `391b57e2...`) was named by
the manifest but excluded from Git delivery by `.gitignore` line 9. The **exact already-created bytes**
are now force-added — **not regenerated**. This is the second instance of the same finite retention
issue, after the three I1 bytecode files.
