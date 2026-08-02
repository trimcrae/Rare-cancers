# Audit — `nr4a3-program-map.md` against the manuscript it claims to graph

**Scope.** A read-only verification of [`nr4a3-program-map.md`](./nr4a3-program-map.md) against the single
deliverable — [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) (3177 lines) and
[`nr4a3-degrader-paper-SI.md`](./nr4a3-degrader-paper-SI.md) (939 lines). Nothing was edited except this file.
$0: no GPU, no CI, no rental.

⛔ **VERSION PIN — the map is being edited by another session while this audit ran.** Every map line number
below is against **`git HEAD` = `96f5543f9`** (395 lines), which is the version read in full. The working tree
carries **+76 / −25** uncommitted lines. Those edits are confined to **§2** (HEAD lines 97–197) plus two
`classDef` lines in the §1 and §5 mermaid blocks — verified by `git diff -U0` hunk ranges. **§3, §4, §5 branch 1,
§5b and §6 are byte-identical between HEAD and the working tree**, so every finding below except those explicitly
marked stands against both.

⚠ **Excluded by instruction** (other agents own them, state in flux): map §5 branch **1b** /
`nr4a3_linker_covalent_reach`; the pose rows / `apo-pose-recovery.json`; map **§2**'s dead-end register.
Where a §2 row states a claim that is *also* load-bearing elsewhere on the map (§1's note, §4's rows), the claim
is audited **through its in-scope home** and §2 is cited only for context.

---

## Counts

| verdict | n |
|---|---|
| `CONTRADICTS` | 7 |
| `MAP-MISSING-IT` | 6 |
| `PAPER-UNSUPPORTED` | 2 |
| `AGREES` | 8 |
| `UNVERIFIABLE` | 2 |
| **total findings** | **25** |

Confidence-direction tally, for the question that matters most:
**map more confident than the paper: 5** (F2, F7, F13, F14, F21) ·
**paper more confident than the map: 2** (F3, F12) ·
**map asserts a status no document supports: 1** (F4).

---

# SEVERITY 1 — the map and the paper disagree about how confident to be

## F1 · The map's pocket evidence is the superseded count · `CONTRADICTS`

**Claim.** Map §4 row 1: *"4 of 20 conformers of the experimental apo NMR ensemble **8XTT** are cavity-bearing,
no simulation bias applied"*.

**Map location.** `nr4a3-program-map.md:179`.
**Paper location.** `nr4a3-degrader-paper.md:180–186`, restated at `:2513–2514`.

**Paper, verbatim:**
> The original implementation obtained an orthosteric-site score for **all 20** conformers (range 0.000–0.925)
> and placed **4/20** above D\*. The **harmonized rerun** (pinned fpocket build + score-independent matcher …)
> now reports both denominators explicitly: the orthosteric pocket is **matched in 19/20** conformers, of which
> **3** score ≥ D\* — i.e. **3/19 (16 %) among detected pockets and 3/20 (15 %) across all deposited
> conformers** (**one fewer than the original 4/20**, as expected from the pinned build and the stricter
> score-independent matcher).

**Committed artifact** (`nr4a3-pocket-reharmonize-summary.json`, row `8xtt_20conformers`):
`n_propagated: 20`, `n_detected: 19`, `n_ge_dstar: 3`, `frac_ge_among_propagated: 0.15`.

**VERDICT: `CONTRADICTS`.** 4/20 is the value the paper explicitly retires. The map's own opening banner makes
this its own bug: *"⛔ STATUS VALUES ARE READ FROM COMMITTED ARTIFACTS, NEVER TYPED HERE … If this file and an
artifact disagree, the artifact is right and this file is the bug"* (`:11–13`). Partial mitigation, stated so the
fix is not over-applied: the paper does separately use the phrase *"the **four** cavity-bearing 8XTT conformers"*
(`:217`, `:2523`) for the four conformers **prespecified under the original criterion** for the `denovo_401`
robustness transfer. So "four cavity-bearing" is a real phrase — but it names a *downstream input set*, not the
current druggability count, and the map is using it as the latter.

---

## F2 · The map's pocket node is an unqualified ✓; the paper records a FAILED preregistered gate and an open submission gate · `MAP-MISSING-IT` (map more confident)

**Claim.** Map §1 node `PO["✓ Pocket exists and is reachable"]`; §4 row 1 state **✓ complete**, *"settled enough
to build on"*.

**Map location.** `:71`, `:99`, `:179`.
**Paper location.** `:387–394` (Gate 1), `:2745` (gate table), `:2259–2265` (Methods, dependency audit).

**Paper, verbatim — the failed gate:**
> **Gate 1 (a genuine two-state cryptic *opening*) FAILED as pre-registered.** Gate 1 asked for an accessible
> *minimum or shoulder* at an opened Rg "not just biased excursions," but F(Rg) is **monotonic — a single
> resolved minimum and a rising wall, with no separate opened minimum**. By the pre-registered criterion this is
> a fail: there is no distinct opened state.

**Paper, verbatim — the open submission gate:**
> Because the generative campaign was conditioned on a receptor frame selected by the *provisional* classifier,
> the rerun must additionally confirm that the **exact release-derived frame used to generate `denovo_401` still
> qualifies as the same mapped orthosteric site and still exceeds D\***. The committed harmonized artifact
> reports **ensemble-level** fractions only and does **not** identify which individual frames cleared D\*, so
> this frame-level dependency check is **not** discharged by it and remains a submission gate (§4); **if the
> generation frame does not qualify, the generation receptor — not merely a reported frame-fraction — is
> affected.**

**VERDICT: `MAP-MISSING-IT`.** `grep -c "Gate 1" nr4a3-program-map.md` → **0**. The map carries Gate 3A/3B but
not Gate 1's failure, and not the frame-level dependency audit. These are not footnotes: Gate 1 is a
preregistered criterion the program **failed and reformulated**, and the dependency audit is an unresolved
submission gate that, per the paper's own sentence, can invalidate the receptor `denovo_401` was generated
into — i.e. it sits upstream of the map's `L`, `PS` and `B` nodes. A ✓ node labelled "Pocket exists **and is
reachable**" reads as settled; the paper's own §5 says *"We explicitly do **not** claim 'Gates pass' as
unqualified"* (`:2751`).

---

## F3 · The map calls the paralogue ABFE future work; the paper reports it complete at three replicates · `CONTRADICTS` (paper more confident)

**Claim.** Map §4 row 4, *what would settle it*: *"paralogue ABFE with replicate-SD error bars — after
CREBBP/BRD4 shows the method recovers a known ΔΔG"*, state **○ future — gated on ◐**.

**Map location.** `:182`.
**Paper location.** `:1230–1239`, `:2303`, `:2639–2641`.

**Paper, verbatim:**
> **Result (three independent-seed replicates; small-n statistics, n = 3, 2 dof).** Raw-engine per-receptor
> ΔG_bind = **+3.5 ± 1.4 (NR4A3) / +8.3 ± 1.1 (NR4A1) / +8.5 ± 0.7 (NR4A2)** kcal/mol (means ±
> between-replicate SD). … **ΔΔG(NR4A3 − NR4A1):** replicates **−6.90, −2.85, −4.53**; mean **−4.76 ± 2.03** …
> **ΔΔG(NR4A3 − NR4A2):** replicates **−5.48, −4.20, −5.26**; mean **−4.98 ± 0.68** … **resolved below zero**.

Methods `:2303` fixes the error-bar convention the map asks for: *"three independent-seed replicates (r1/r2/r3;
**error bars = between-replicate SD, n = 3**)"*. §4 caveat 7 `:2639`: *"**initial three-replicate ABFE
complete**"*.

**VERDICT: `CONTRADICTS`.** The experiment the map lists as the thing that would settle the binder claim has
been run and is in the paper, with exactly the replicate-SD error bars the map specifies. The paper holds it
**provisional** for a named, different reason — a soft-core-tail λ-overlap defect below 0.03 on *every* leg
(`:1261–1271`) — and holds the repair **deliberately, not for want of capacity**: *"It is not currently running:
the whole ABFE block is deliberately held … so it is not the next thing worth computing"* (`:1277–1280`). The
map's "○ future" collapses *"run, reported, and consciously parked"* into *"not started"*, which is the wrong
instruction to a reader deciding what to do next.

**And the paper's real open item has no row anywhere on the map** (see F5): the **matched experiment-anchored
paralogue legs**, which the paper names twice as the decisive follow-up —
> A *matched* experiment-anchored contrast would require **crystal-seeded paralogue ABFE** (Nurr1 1OVL /
> Nur77 3V3E are collapsed apo crystals, so it additionally needs a pocket-opening MD step), **flagged as the
> decisive follow-up** (§4). (`:1299–1301`)

> the **NR4A3 leg is done** in triplicate (+8.17 ± 0.98, §2.8) but the **matched NR4A1 and NR4A2 legs are
> not**, so the 8XTT-anchored *selectivity* contrast **does not yet exist**. (`:2520–2522`)

`grep -c "8.17" nr4a3-program-map.md` → **0**.

---

## F4 · The map's single highest-leverage item is running an experiment STRATEGY.md says is unauthorised and never run, and that the paper never mentions · `UNVERIFIABLE` against the paper, `CONTRADICTS` STRATEGY.md

**Claim.** Map §3 instrument row: *"Selectivity free energy (ABFE) | CREBBP vs BRD4(1) / SGC-CBP30,
ΔΔG ≈ 2.2 kcal/mol | **solvent leg dispatched; full pass priced** | ◐ in work"*. Map §5b Route A: *"its
selectivity benchmark (CREBBP vs BRD4(1), SGC-CBP30) was built and staged with no `result` key, and **its first
leg is now on spot**. … **This is the single highest-leverage item in the program, and it is the one thing
moving.**"* Map §6 item 5: *"**Run the CREBBP/BRD4 benchmark** … | ◐ in work"*.

**Map location.** `:162`, `:337–341`, `:376`.
**Paper location.** — none. `grep -c "CREBBP" nr4a3-degrader-paper.md nr4a3-degrader-paper-SI.md` → **0 / 0**.
Likewise `SGC-CBP30` → 0 / 0.

**STRATEGY.md, verbatim** (`STRATEGY.md:531–549`) — and per CLAUDE.md §5 STRATEGY.md *"wins over any other doc"*:
> **Two known-answer tests are already built and have never been run:**
> - **CREBBP vs BRD4(1) / SGC-CBP30** — `selectivity-benchmark.json` + `selectivity_benchmark_prep.py` +
>   `stage-selectivity-benchmark-aws.yml`, fully specified with an `abfe_plan` and **no result key**. …
>   ⛔ It is a **binary** selectivity control and would **not** discharge §4's paralogue/ternary statement …
>
> **Neither is authorized here** and neither is a positive control for paralogue *degradation* selectivity.

`selectivity-benchmark.json` confirms the artifact state: top-level keys are
`['_comment','engine','benchmark_type','date_et','ligand','proteins','experimental_selectivity',
'why_this_system','citations','staging','abfe_plan']` — **no `result` key**, consistent with both documents.

**VERDICT: `UNVERIFIABLE` (paper) + `CONTRADICTS` (STRATEGY.md).** Three separate problems, in rising order:

1. **Status conflict.** The map asserts a leg is *dispatched and on spot*; STRATEGY.md says the test *has never
   been run* and is *not authorized*. One of the two is stale. Because this is a GPU rental, the map is the
   document making the riskier assertion, and per CLAUDE.md §3 an unauthorised spend past the >$50 gate is
   trimcrae's alone. **I did not resolve this** — resolving it means reading a live billing/CI record, which
   the audit brief scopes out. Recording the refusal rather than guessing.
2. **The map uses it for something STRATEGY.md says it cannot do.** Map §4 row 4 gates the *paralogue*
   selectivity claim on this benchmark. STRATEGY.md: *"It is a **binary** selectivity control and would **not**
   discharge §4's paralogue/ternary statement."* The map drops that qualifier entirely.
3. **The paper cannot corroborate any of it.** A reader of the deliverable would not learn this benchmark
   exists. That is defensible for genuinely new work — but the map presents it as the gating instrument for a
   claim the paper *already reports a result for* (F3), which makes the omission load-bearing rather than
   incidental.

---

## F5 · The map's instrument table omits the paper's entire ABFE calibration record · `MAP-MISSING-IT`

**Claim.** Map §3's ABFE row lists exactly one known-answer test (the unrun CREBBP/BRD4 one) and nothing else.

**Map location.** `:162`.
**Paper location.** `:1251–1256`, `:2294–2325`, `:2348–2360`, `:1261–1280`.

The paper's actual instrument record, none of which appears on the map:

| what the paper reports | verdict in the paper | on the map? |
|---|---|---|
| **T4-lysozyme L99A + benzene**, ABFE absolute, exp. −5.2 kcal/mol | returns **+1.90 ± 0.09**, *"under-binding by ≈ +7.1 kcal/mol — a failed/strongly-biased absolute benchmark"* (`:1252–1254`) | ✗ |
| **Methane hydration free energy** (FreeSolv), same engine | **+1.60 ± 0.04** vs +2.0, *"approximately reproduced"* (`:2296–2298`) | ✗ |
| **TYK2 `ejm_31→ejm_42`** relative FEP, OpenFE benchmark | **+0.37 vs −0.24**, abs err **0.61** — *"reproduced the experimental relative binding free energy … inside the ~1 kcal/mol chemical-accuracy band"* (`:2354–2356`) | ✗ |
| **λ-overlap defect** — *"**every leg** — the shared solvent leg and all three complex legs — has at least one soft-core-tail window pair below 0.03"* (`:1265–1268`) | holds the whole ABFE block provisional | ✗ |
| CREBBP vs BRD4(1) / SGC-CBP30 | — | ✓ (only row) |

**VERDICT: `MAP-MISSING-IT`.** The map's §3 exists, in its own words, because *"An instrument that has never
recovered a known answer **cannot support a claim**"*. The paper's headline finding about this exact instrument
is that it **fails a textbook absolute benchmark by ≈ 7 kcal/mol** — larger than the entire selectivity margin
it is used to compute — and that the failure is why every ABFE absolute in the paper is uninterpretable. That
belongs in the table. Its absence also makes the map's phrasing *"the ABFE engine has **never recovered a known
ΔΔG**"* (`:339`) read as untested when the paper's position is stronger and more specific: it was tested on an
absolute and **failed**, and the relative path on a *different* quantity **passed**.

---

## F6 · The map's §4 conclusion repeats a framing the paper narrowed, and contradicts the map's own Route B · `CONTRADICTS`

**Claim.** Map §4 row 4: *"predicted margin only; **the paper's own reading is that selectivity, if any, rests
here rather than on the ternary**"*.

**Map location.** `:182`.
**Paper location.** `:729` (the sentence the map is echoing), `:2583–2599` (its withdrawal), `:2600–2601` (the
live replacement), SI `:76–82`, SI `:138–149`.

**What the map is echoing** (`:728–730`, still live in §2.5):
> degradation selectivity, if any, rests on the **binder** margin, with linker/exit-vector design the
> (untested) lever that might introduce it.

**What the paper then does to it** (§4 caveat 5, `:2583–2592`):
> ⚠ **A conclusion previously drawn here is withdrawn as an overclaim in the negative direction.** This caveat
> used to state that sourcing paralogue selectivity from the ternary "**has now been tested and does not
> materialize**" … a method that may not rank ternary selectivity **may not conclude ternary selectivity is
> absent either**. … Accordingly the ternary is **not** written off as a selectivity lever here.

**The paper's live sentence** (`:2600–2601`):
> Degradation selectivity therefore rests, on current evidence, on the **binder** margin **plus those nominated
> categorical handles**.

**SI §S3, verbatim** (`:141–144`):
> So ternary selectivity is **structurally available but not yet realized** … the doubly-selective degrader is a
> **rational goal, not a dead end**.

**VERDICT: `CONTRADICTS`.** Two ways. (a) The map presents as "the paper's own reading" a formulation the paper
has explicitly narrowed; the live version adds the categorical handles and refuses to write the ternary off.
(b) The map contradicts **itself**: §5b Route B is the categorical covalent-handle axis, described as *"◐ in
work"* with its *"chemical basis: ✓ opened 2026-08-02"* (`:343–349`), and §5b closes with *"**Why they
compose**: … two independent mechanisms"* (`:360–362`). §4 row 4 says selectivity rests on the binder *rather
than* elsewhere. Both cannot be the map's position.

---

## F7 · Route A's "✓ strong, and already measured" rests on an uncommitted, superseded-tracker artifact — by the paper's own statement · `AGREES` on the numbers, `CONTRADICTS` on provenance (map more confident)

**Claim.** Map §5b Route A: *"**Chemical basis: ✓ strong, and already measured** ([`nr4a-selectivity.json`],
paper §2.4). Of the **10 Pocket-5 lining residues, 7 are paralogue-divergent** — L406, T407, T410, R412, I484,
I531, L534 — and in the opened druggable ensemble **5 stay pocket-facing** (L406, T410, I484, I531, L534) …
T407 and R412 mostly splay outward."*

**Map location.** `:329–333`.
**Paper location.** `:594–599` (the numbers), `:552–560` + `:561–564` (their status), `:605–611` (the omission).

**The numbers — paper §2.4, verbatim** (`:595–599`):
> Aligning the NR4A3 pocket to NR4A1/NR4A2 … identifies, among the **10 Pocket-5 lining residues**, **7
> divergent** ones — L406, T407, T410, R412, I484, I531, L534 — as selectivity handles. All 7 are within the
> metadynamics CV; of these the opened, druggable ensemble keeps **5 pocket-facing** (L406, T410, I484, I531,
> L534 — §2.3), so those five are the realistically *engageable* handles a warhead can exploit (T407 and R412
> mostly splay outward).

Word-for-word agreement. The ortholog claim also checks out — map: *"all ten are ortholog-invariant across six
species spanning ~300 My"*; paper `:622–626`: *"All ten Pocket-5 lining residues — including all seven
selectivity handles — are **fully conserved across six species spanning ~300 My of amniote evolution**."*

**But the paper says the "5 pocket-facing" half is neither confirmed nor committed** (`:552–554`, `:561–564`):
> *(Registered Gate-2 sub-check — computed under the **pre-harmonized** tracker and **not** re-run under the
> harmonized one, so it is **reported but not treated as confirmed**, since the set of druggable frames it is
> computed over is the superseded one. …
> **Artifact status:** these fractions are recorded in the committed run ledger … but the primary output
> `handle_facing_summary.json` is an **S3-only object that is not committed to this repository**, so the numbers
> are traceable to a run record rather than to a checked-in artifact; they are quoted here at that weight.

And §5 `:2752–2753`: *"Gate 2's frame-fraction clause **passes** under the committed harmonized re-analysis
while its **handles clause is still only at pre-harmonized weight**"*.

**VERDICT: `AGREES` (numbers) / `CONTRADICTS` (provenance and confidence).** The map cites
`nr4a-selectivity.json`, which owns the **7-divergent** half. It does **not** own the **5-pocket-facing** half —
that comes from `handle_facing_summary.json`, which the paper states is not in the repository and was computed
under a tracker the program has since replaced. Calling it *"✓ strong, and already measured"* is exactly the
kind of typed status the map's own banner forbids.

**Route A also drops the paralogue asymmetry, which cuts against it** (`:605–611`):
> Against **NR4A1**, all 7 handles differ (and all 5 engageable ones). Against **NR4A2**, only **6 of 7** differ
> — **I531 is identical (Ile in both NR4A3 and NR4A2)** — so of the 5 engageable handles, only **4** distinguish
> NR4A3 from NR4A2 … **NR4A2 selectivity therefore rests on a *narrower* engageable set**, which matters because
> NR4A2/Nurr1 is the paralogue carrying the dopaminergic-loss liability one most wants to spare.

Route A's chemical basis is 20 % thinner against the paralogue the paper says matters most, and the map does not
say so. The map also omits §2.4's own statistical hedging — *"a two-test Bonferroni correction moves p = 0.028 to
**0.056**, i.e. borderline"*, plus spatial-correlation and selection caveats (`:658–672`).

---

## F8 · "Three separate selectivity results had to be withdrawn" is unenumerated, does not reconcile with the paper, and its causal generalization is refuted by the paper's own record · `CONTRADICTS`

**Claim.** Map §3: *"This table is why three separate selectivity results had to be withdrawn."* and *"Every
claim that later had to be withdrawn came from an instrument that had never been tested. The test costs close to
nothing; **skipping it has cost three retractions**."*

**Map location.** `:156`, `:167–169`.
**Paper location.** full census below.

**Census of withdrawn/retracted *selectivity* results in the paper and SI** (from `grep -niE "retract|withdraw"`
across both files, 32 hits, de-duplicated to distinct results):

| # | result withdrawn | paper location | cause **as the paper states it** | fits "untested instrument"? |
|---|---|---|---|---|
| 1 | the **"MM-GBSA-confirmed selective"** headline and `denovo_15` as lead | `:987`, `:2709–2713`, `:2832`, SI `:501` | failed a **decoy specificity control** — the instrument was later tested and failed | **yes** |
| 2 | **`denovo_111`** as an above-null foothold | `:1007`, `:1109`, `:1215`, `:2717`, `:2833` | its **cationic** microstate reverses selectivity (−15.01 ± 5.14) | partly — a microstate-resolution gap, not a missing known-answer test |
| 3 | the negative conclusion that **the ternary adds no selectivity** | `:2583–2592`, SI `:76–82` | the co-fold classifier **failed its own epimer affinity control** | **yes** |
| 4 | the **NR-V04 covalent-panel per-arm figures** (`recruiter_active` 3/3 vs epimer 1/3; cov 2/3 = noncov 2/3; `cov_c551a` 1/3) — *"retracted and must not be quoted"* | `:808–811`, `:2036`, SI `:816–817` | a **chain-ordering defect** (Elongin C scored as the target), a **nm/Å unit error**, and **contaminated inputs** (14-3-3 ε where Elongin B belongs) | **no** |

The paper additionally names **`denovo_94` and `denovo_57`** alongside `denovo_15` (`:2610`: *"the **retracted**
single-snapshot candidates — denovo_15/94/57 and the protonation-sensitive denovo_111"*), and two further
retractions that are not selectivity results: the **E3-recruiter advanced pair** (*"those numbers are
**retracted**, not merely superseded"*, `:1600` — a biological-assembly frame defect) and the **Gate-3B
accessibility estimate** (*"we **withdraw** that quantitative accessibility interpretation"*, `:403` —
cross-replica divergence).

**VERDICT: `CONTRADICTS`, on both halves.**

*The count.* No enumeration accompanies "three", so it cannot be checked against a stated list — which is itself
the problem in a document whose stated purpose is to stop connections *"being re-derived"* from prose. On the
paper's own naming there are **four** withdrawn selectivity results (rows 1–4), or **six** if `denovo_94`/`57`
are counted separately as the paper counts them, or **two** if rows 1 and 2 are collapsed into "the MM-GBSA
lane". None of those readings is three.

*The generalization.* *"Every claim that later had to be withdrawn came from an instrument that had never been
tested"* is refuted by row 4, the largest single retraction in the paper. Its causes were software and input
defects that **no known-answer test on the instrument would have caught** — the paper says so directly
(`:933–936`):
> **One further limit, learned the expensive way** … the panel persisted no trajectory, so three separate
> analysis defects — the chain split, a chain-blind reactive-cysteine search, and a nanometre/Ångström unit
> error — were each correctable in principle and **none correctable in practice**.

Same for the E3-recruiter retraction (an assembly-frame bug) and the Gate-3B withdrawal (replica divergence).
The map's §3 conclusion is a true and valuable lesson about rows 1 and 3; stated as *"every"*, it is wrong, and
it points the reader at the wrong prophylactic for the failure mode that actually cost the most.

---

## F9 · The map folds two different instruments into one row · `CONTRADICTS`

**Claim.** Map §3 row: *"**Interface-stability endpoint (E1)** | three attempts: cooperativity calibrator,
NR-V04 retrospective, SMARCA2/4 control | wrong sign · p = 0.393 · p = 0.747 | ⏸ parked — **no pass**"*.

**Map location.** `:165` (and the parallel §2b row at `:140`).
**Paper location.** `:1836` (what the calibrator computes), `:1996–1998` (what E1 is), `:2205–2208` (how the
paper groups the three).

**E1, as the paper defines it** (`:1996–1998`):
> The primary endpoint **E1** is the **interface-RMSD plateau (Å)** — the mean RMSD of the E3∩target interface
> heavy atoms over the final 50 % of production frames, against the starting interface, lower being more stable.

**What §2.11's cooperativity calibrator computes** (`:1836`):
> The quantity computed is the thermodynamic cycle `ΔΔG_coop = ΔΔG_alch,ternary − ΔΔG_alch,binary`.

That is an OpenFE alchemical free-energy calculation with MBAR reduction — a different instrument entirely. Only
the NR-V04 retrospective (p = 0.3929, `:2003`) and the SMARCA2/4 control (p = 0.7468, `:2080`) are E1.

**How the paper actually groups them** (`:2205–2208`):
> with §2.11's cooperativity calibrator failed on sign, §2.12's retrospective non-resolved, and this control
> null on an adequately-powered design, **all three attempts to establish a positive control for this program's
> selectivity claims** have now been run and none succeeded.

**VERDICT: `CONTRADICTS`.** The paper's grouping is *"three attempts at a **positive control**"*, spanning **two**
instruments. The map's grouping is *"three attempts at **E1**"*, which mis-attributes the wrong-sign
free-energy failure to an interface-RMSD endpoint. This matters operationally: the map's §2b reopen trigger for
this row — *"a readout with power at achievable sampling"* — is the right trigger for E1 and the **wrong** one for
the calibrator, whose miss the paper proves is systematic and **immune to more sampling** (`:1907–1911`:
*"Because replicates shrink variance and not bias, **more replicates cannot rescue this result**"*).

---

## F10 · A number in the map matches neither statistic in its own cited artifact · `CONTRADICTS`

**Claim.** Map §5 branch 1: *"the thiol's **own HG proton occludes a median 76 %** of the SG surface"*.

**Map location.** `:246–247`.
**Artifact.** `nr4a3-covalent-handle-ensemble.json` → `thiol_hydrogen_occlusion.fraction_occluded`:
```
{"n": 16, "min": 0.21, "q1": 0.643, "median": 0.918, "q3": 1.0, "max": 1.0, "mean": 0.777}
```
Independently recomputed from the 16 per-cysteine entries: **median = 0.918**.

**VERDICT: `CONTRADICTS`.** The artifact's **median is 91.8 %**, not 76 %. The **mean** is 77.7 %, which rounds
to 78 %, not 76 % either. The map labels the figure "median". No other value in that artifact is 0.76. Not in
the paper at all, so the map is the sole home — and the sole home is wrong.

---

# SEVERITY 2 — the map is missing load-bearing paper content

## F11 · Six of the paper's fifteen result sections have no node, row or mention anywhere on the map · `MAP-MISSING-IT`

**Map location.** whole file.
**Method.** `grep -c` over `nr4a3-program-map.md` (HEAD), per topic.

| paper content | what it is | map hits |
|---|---|---|
| **§2.9** congeneric RBFE — 18 of 18 computable edges, **$73.79** realised GPU spend, a 19-edge map | the program's largest completed quantitative lane | `"2.9"` **0** · `"congeneric"` **0** · `"RBFE"` **0** · `"cmpd19"` **0** · `"Zaienne"` **0** |
| **§2.10e** the causal matched-pair test, **S = −0.1297 ± 0.3264 kcal/mol** | *"the **only** test in this program that asks whether a designed element **causes** discrimination"* (`:1782–1783`) | `"2.10e"` **0** · `"0.1297"` **0** |
| **§2.1** BioEmu unbiased ensemble cross-check, 12.5 % druggable | the paper's honest open-state population estimate, an orthogonal evidence axis | `"BioEmu"` **0** |
| **§2.2** PocketMiner + four permutation nulls (p = 0.009 / 0.0001 / 0.036 / **0.74** / 0.014) | the only *independent-method* support for the cryptic site | `"PocketMiner"` **0** |
| **§2.10** the unique-**lysine** categorical axis | *"The program's only insurance against a C397-specific chemical failure is the **unique-lysine** term, not a second cysteine"* (`:1568–1569`) | `"lysine"` **0** |
| **SI §S3** superfamily liability screen — MR/AR named as *"the sole sequence-level non-paralogue follow-ups"* that *"must clear"* before selectivity extends past the paralogues (SI `:213–219`) | a named gate on the scope of every selectivity claim | `"superfamily"` **0** · `"MR/AR"` **0** |

Also absent: `"denovo_401"` **0** — the paper's sole carried candidate, subject of §2.7, §2.8, §3, §5 Gate 4, and
SI §S1/§S2/§S3.

**VERDICT: `MAP-MISSING-IT`.** The map's masthead is *"the dependency graph of **every claim the paper has to
establish**"*. Some of the above are results rather than dependencies and their absence is arguable. Four are
not:

- **§2.10e is a dependency, not a result.** It is the causal test of the `TS` node ("TERNARY adds or preserves
  selectivity") and of Route B's mechanism. The paper's §5 Tier-3 gate is written around it, and it has **run**
  and returned a preregistered null with a quantified bound (*"the design could only have resolved a wedge
  contribution of roughly **|S| ≳ 0.65 kcal/mol** (2σ)"*, `:1798–1800`). A dependency graph with no causal node
  cannot express the paper's own Tier-2/Tier-3 structure.
- **The unique-lysine axis is Route B's only redundancy.** Map §5b Route B presents the covalent cysteine handle
  as the categorical route and states its single point of failure; the paper's stated hedge against exactly that
  failure is the lysine term, which the map does not carry.
- **MR/AR is a live gate on claim scope**, not a result: nothing on the map says the selectivity claim is
  currently bounded to two paralogues by an unrun cross-binding check.
- **§2.9's cycle-closure violation** is the paper's most concrete internal-inconsistency finding and is
  unrepresented — see F12.

---

## F12 · The paper reports a failed cycle closure and a two-run disagreement on one edge; the map has neither · `MAP-MISSING-IT`

**Paper location.** `:1405–1423`, `:1425–1433`.

**Paper, verbatim — the closure violation:**
> `cycle_3carbonyl` — cmpd19 → free acid → primary amide → cmpd19, i.e. `+0.136` and `+2.106` against the direct
> `+0.935` — sums to **R = +1.307 and is a VIOLATION** of that tolerance. … what it does establish is that **at
> least one of them is not converged or not consistently mapped, and all three are therefore quoted here under
> that reservation.**

**Paper, verbatim — the reproducibility gap:**
> **⚠ An independent recomputation of the same edge disagrees with the §2.9 pilot by more than either stated
> uncertainty** … cmpd19 → 5-NH₂ = **+1.84 ± 0.36**; the fan-out's `cw_ev_5nh2` … gives **+1.064 ± 0.118**. The
> gap is **≈0.78 kcal/mol**, against quadrature errors of 0.36 and 0.12.

**VERDICT: `MAP-MISSING-IT`.** Both are direct evidence about the reliability of the free-energy machinery the
map's `V4` node ("Physics recovers a known ddG") and §5b Route A depend on. The map's §3 has an instrument-level
view of this engine that records only an unrun benchmark (F4/F5); the paper has *measured*, on its own system,
that two independent runs of one perturbation differ by several times their own error bars and that one of its
three closed cycles does not close. That is the kind of fact §3 exists to hold.

---

## F13 · `ARCH` is ✓ but nothing it feeds is, and the node it is validated by says the same thing · `CONTRADICTS` (map more confident)

**Claim.** Map §1: `ARCH["✓ Ternary correctly ASSEMBLED"]`, classed `done`, with `ARCH --> T` and
`V2 -.validates.-> ARCH`, where `V2["✓ Generator builds a known ternary"]`.

**Map location.** `:74`, `:81`, `:92`, `:99`.
**Paper location.** `:2152–2169`, `:2163–2165`, `:1183` (map §4 row 5), `:375` (map §6 item 4).

**Paper, verbatim** (`:2152–2157`, `:2163–2165`):
> Run on **9DTY** — the SMARCA2 arm's own deposited ternary … the same generator reaches **DockQ 0.839 (CAPRI
> "High"), interface-RMSD 0.67 Å, fnat 0.83**, **best of 16 seeds, median 0.442** …
> ⚠ Reported as best-of-16 and as **one arm**: the **SMARCA4 arm was refused before any prediction** … and **no
> SMARCA4 number exists**.

**VERDICT: `CONTRADICTS`, internally.** No NR4A3 ternary has been correctly assembled by anyone. The map's own
§4 row 5 has the ternary claim at **○ future** needing *"rebuild by the assembly route"*, and §6 item 4 has that
rebuild at **◐ in work** — so a ✓ node labelled "Ternary correctly **ASSEMBLED**" feeding an ○ claim is a state
the map's §0 rules cannot produce. Read charitably, `ARCH` means *"the assembly route is capable of building a
correct ternary"* — but that is verbatim what `V2` says, which makes the `V2 -.validates.-> ARCH` edge circular:
one node validating a restatement of itself. Either way the ✓ overstates: on the paper's record the capability
is demonstrated **best-of-16, on one arm, on a system that is not NR4A3**.

---

# SEVERITY 3 — provenance and phrasing that will mislead

## F14 · The §3 "PASSES" verdicts drop the paper's own non-generalization caveats · `CONTRADICTS` (map more confident)

**Map location.** `:159–161`.

| map row | map verdict | what the paper says the result cannot do |
|---|---|---|
| Ternary generator, **6HAX** DockQ 0.618 | *"✓ complete — **PASSES**"* | *"That case was deposited in 2018, inside the model's 2023-10-14 data horizon, so it is **memorisation-permitting by construction**: it is a **positive control on the harness and the instruments**, and is **not evidence of generalisation**, of anything about NR4A3, or of anything about degradation or selectivity"* (`:2140–2142`) |
| Ternary generator, **9DTY** DockQ 0.839 / iRMSD 0.67 Å | *"✓ complete — **PASSES**"* | best of 16 seeds, median 0.442; **one arm only**, SMARCA4 refused (`:2155`, `:2163–2165`) |
| Interface-mutation physics (pmx/GROMACS), barnase–barstar **+4.42 ± 1.08 vs +3.4** | *"✓ complete — **PASSES**"* | *"**No benchmark yet probes the regime this cross-check would occupy** — resolving ~1 kcal/mol between two closely related receptor states — so the engine is validated for seeing a large effect and for not inventing one where none exists, but **not demonstrated to resolve a small paralogue-scale difference**"* (`:2409–2412`) |
| Structural selectivity descriptor, **Gln98 Oε1 → Arg12 Nη2 2.88 Å** | *"✓ complete — **PASSES**"* | *"It **validates one contact in one pair**. It does **not** validate E1 … and it makes **no NR4A3 prediction correct**"* (`:2200–2203`) |

The **numbers** in all four rows are correct — verified verbatim against `:2137`, `:2154`, `:2401–2403`, `:2192–2194`
and against `selcal-interface-signature.json`/`nr4a-ternary-signature.json`. **VERDICT on the numbers:
`AGREES`.** **VERDICT on the verdicts: `CONTRADICTS`.** A bare "PASSES" in a table whose stated function is to
decide *"can this instrument support a claim?"* is exactly the reading the paper spends four paragraphs
refusing. The pmx row is the sharpest case: the map's `V4`/Route A pipeline needs it at the ~1 kcal/mol
paralogue scale, and the paper says that regime is the one it has **not** been benchmarked in.

---

## F15 · "Something binds it — evidence today: none" contradicts §1 · `CONTRADICTS`

**Claim.** Map §4 row 2: *"**Something binds it** | **none** — no ligand-bound NR4A3 structure exists, of any
molecule | a thermal shift / SPR / NMR fragment screen …"*.

**Map location.** `:180`.
**Paper location.** `:92–99`, `:335–336`, `:1313–1314`.

**Paper §1, verbatim** (`:92–99`):
> **NR4A3 itself is experimentally ligandable — pharmacologically, though not yet structurally.** **A fragment
> screen against NOR-1/NR4A3 (hit rate <1 %) returned three ligand chemotypes**, one elaborated to a
> **low-micromolar inverse agonist** (compound 19) that shifted NOR-1-regulated gene expression in cells,
> de-repressing the NR4A3 target gene *MYC* (IC₅₀ ≈ 8–47 µM; Zaienne 2022 …).

And `:335–336`: *"Fragment-to-lead campaigns reaching sub-µM NR4A ligands with NOR-1/NR4A3 tested (Stiller &
Merk 2023; Zaienne 2022) keep the *ligandable-not-undruggable* premise on **experimental footing**."*

**VERDICT: `CONTRADICTS` as written.** The map's *evidence today* cell reads "none" and its *what would settle
it* cell proposes a fragment screen — one of which has been run, published, and elaborated to a functional
ligand that the paper's entire §2.9 lane is anchored on (*"the **Zaienne cmpd19** anchor … a ***functional***
NR4A3 ligand"*, `:1313–1314`). The map's node is defensible if scoped to *"binds **the cryptic Pocket-5**"* —
which is the honest question, and which STRATEGY.md scopes correctly (*"whether anything binds **the opened
pocket** at all"*, `STRATEGY.md:513–514`). The map dropped the scoping word, and with it the distinction the
paper's §1 is built on: *"These experimental results establish that NR4A3 *can* be engaged by small molecules,
but leave the binding site **structurally undefined**"* (`:99–101`).

---

## F16 · "Unrecoverable … can never be regenerated by anyone" is stated absolutely; the SI records the construct · `PAPER-UNSUPPORTED`

**Claim.** Map §1 note: *"the ternary claim rests on a molecule that **cannot be recovered**"* (`:105`); §4 row
5: *"the molecule used is **unrecoverable**, so it **cannot be replicated**"* (`:183`); §2a (context only):
*"That specific **result** can never be regenerated by **anyone, including us**"* (`:128`).

**Map location.** `:104–107`, `:183`.
**Paper location.** SI `:70–71`; paper `:719–723`.

**Well-sourced half.** `nr4a-ternary-ligand-provenance.json` confirms the mechanism exactly:
`n_recovered: 0` of 3 arms; per arm *"no `_chem_comp_bond` loop … bond orders would have to be perceived from
coordinates, which for a novel PROTAC is a guess"*; and
`_why_it_is_not_in_the_repo`: *"`nr4a3_ternary_sagemaker.py` forwards the molecule as `$PROTAC_SMILES`; …
`nr4a3-ternary-prep.json` … records a 403 on its sequence fetch and an empty targets map."*
STRATEGY.md `:500–505` states the same. **On the mechanism, the map `AGREES` and is well sourced.**

**But the SI records the construct** (SI `:69–71`):
> **We nonetheless ran that step:** we built a **representative `denovo_401`-PROTAC**
> (**warhead–PEG2–succinyl–lenalidomide**, RDKit-validated **C41H56N4O8**, glutarimide intact) and predicted the
> **NR4A3/NR4A1/NR4A2-LBD + CRBN + PROTAC** ternaries.

C41H56N4O8 → **41 + 4 + 8 = 53 heavy atoms**, which is exactly the `n_heavy: 53` the provenance artifact reports
for `LIG1` in all three models. The warhead's own SMILES is given in full at `:1086`. So the record comprises a
named four-part connectivity scheme, a verified molecular formula, a matching heavy-atom count, and a fully
specified warhead.

**VERDICT: `PAPER-UNSUPPORTED`, on the absoluteness only.** What is genuinely unrecoverable is the **exact
regiochemistry** — which nitrogen of pomalidomide/lenalidomide, which atom of the warhead, the PEG2 attachment
geometry, stereochemistry — and therefore whether a re-fold would be *the same molecule*. That is a real and
sufficient blocker for a replicate comparison, and the paper's own §2.5 caveat (*"one arbitrary linker"*, `:725`)
concedes the construct was never meant to be reproducible. But *"can never be regenerated by anyone"* and
*"cannot be replicated"* are stronger than the record: neither the map nor STRATEGY.md acknowledges the SI's
composition record or explains why formula + scheme + matching heavy-atom count is insufficient. A reader
checking the claim will find the SI paragraph and conclude the map overstated it. **The fix is a sentence, not a
re-run:** say what is missing (connectivity/regiochemistry), not that nothing is known.

---

## F17 · "Built by the failing route" is well-sourced — but the paper contradicts itself about it · `AGREES` (map), paper defect flagged

**Claim.** Map §4 row 5: *"predicted for all three paralogues at comparable confidence, **built by the failing
route**"*.

**Map location.** `:183`.

**Supporting — committed artifact** (`nr4a-ternary-signature.json`, `structure_provenance`):
> "every NR4A ternary this program holds came from the same co-folding route whose output, on the one system
> with a crystal to check against, scores DockQ 0.023-0.046"

**Supporting — paper §4** (`:2501–2503`):
> the single sequence-encoded candidate rests on one model per paralogue against a three-model reproducibility
> bar, **on structures from the route whose assembly fails above**, and with the NR4A3 warhead pose unmeasured

**Contradicting — paper §2.12a** (`:2128–2130`):
> What it does change is where the failure sits — at ternary **generation** rather than at ranking — which is a
> statement about **this co-folding pipeline on a VHL neosubstrate interface and about nothing else**.

**VERDICT: `AGREES` for the map; the defect is the paper's.** The map follows the §4 Limitations reading, which
is backed by a committed artifact. But §2.12a explicitly refuses to extend the DockQ result past a **VHL**
neosubstrate interface, while the §2.5/SI-§S2 ternary is a **CRBN** ternary — so the paper says both "about
nothing else" and "our own structures come from that route". A reader arriving via §2.12a and a reader arriving
via §4 get opposite answers. **This is a paper fix, not a map fix**, and it is worth raising because the map's
ternary node (`T`, `TS`) inherits whichever reading is chosen.

**Also `AGREES`, verified:** the iptm values (`:720`, SI `:75`: *"iptm 0.72/0.83/0.82"*), and map §4 row 6's
ternary-signature counts — `nr4a-ternary-signature.json` `result`: `sequence_encoded: ["GLU208"]`,
`n_sequence_encoded: 1`, `same_residue_placement_artifact: ["ARG174","ARG219","GLU104","LEU234","LYS195"]`
(**five**), matching the map's *"one sequence-encoded candidate (Glu208 …); five further hits were placement
artifacts"* and the paper's `:2499–2504`. ⚠ **Not verified:** the map's *"→ Pro in NR4A1, Tyr in NR4A2"*. The
artifact's `result.detail` and `pairwise` blocks do not carry a paralogue residue identity for position 208 in a
form I could read out. **`UNVERIFIABLE` — recording a refusal rather than assuming.**

---

## F18 · Branch 1's cysteine count disagrees with the paper's, and neither reconciles · `CONTRADICTS`

**Claim.** Map §5 branch 1: *"NR4A3 has **three** cysteines the paralogues lack — C397, C420, C559"*; §1 branch
node: *"3 unique: C397 C420 C559"*.

**Map location.** `:200`, `:229–230`.
**Paper location.** `:1524–1526`.

**Paper, verbatim:**
> Aligning full-length UniProt NR4A3/NR4A1/NR4A2 with two independent aligners and requiring agreement
> (`nr4a_paralogue_unique_residues.py`) identifies **four NR4A3-unique cysteines**, of which **Cys397** — NR4A1
> Asn363, NR4A2 Ser363 — is exposed and sits **10.9 Å** from the cryptic pocket along the exit vector

**Artifact** (`nr4a3-covalent-handle-ensemble.json`): `nr4a3_lbd_cysteines` has **7** entries;
`nr4a3_unique_lbd_cysteines: [397, 420, 559]` — **three**, and `summary.n_nr4a3_lbd_cysteines_unique_vs_both: 3`.

**VERDICT: `CONTRADICTS`.** The reconciliation is almost certainly scope — the paper counts over the
**full-length** protein, the map/artifact over the **LBD** — but **neither document says so**, and the map's
branch-1 text does not qualify "the paralogues lack" with "in the LBD". Two values for one named quantity with no
cross-reference is precisely the rule-1 failure the map exists to prevent. The distance figures do reconcile: the
artifact gives per-cysteine 8XTT ranges C397 10.93–14.06 Å, C420 16.85–18.93 Å, C559 12.22–13.23 Å, so the map's
*"11–19 Å"* is a fair rounding of the pooled band, and the paper's 10.9 Å is C397's single-model value
(`cross_checks`: `committed_dist_A: 10.86`). **`AGREES` on distances.**

---

## F19 · Branch 1 calls all three unique cysteines "exposed"; its own artifact says one is never exposed · `CONTRADICTS`

**Claim.** Map §5 branch 1 table, row *"C397, C420, C559"*, column *NR4A3-unique*: *"**yes**, and **exposed**"*.

**Map location.** `:235`.
**Artifact.** `nr4a3-covalent-handle-ensemble.json` → `summary.per_unique_cysteine_across_8xtt`:

| cysteine | RSA median | `n_flagged` (accessible **and** reachable), of 20 |
|---|---|---|
| C397 | 0.464 | **20** |
| C420 | 0.266 | **16** |
| C559 | **0.205** | **0** |

The exposure criterion is `_criteria.accessible`: *"residue RSA >= EXPOSED_RSA (**0.25**)"*.

**VERDICT: `CONTRADICTS`.** C559's median RSA is **below** the cutoff and it is flagged in **0 of 20** conformers;
C420 clears it in 16 of 20, not uniformly. A blanket "exposed" for all three is not what the cited artifact says.

⚠ **The map's own next paragraph partly defuses this and is worth preserving** — *"⛔ AND THE CRITERIA FAILED
THEIR OWN POSITIVE CONTROL … The rank is the claim; the cutoff is not"* (`:237–243`), verified correct against
`control_recovery` (`n_accessible: 0` of 25, `rsa: 0.165`) and `control_rank` (`rank: 3, of: 18` on all five
observables, with NR4A3 C397 and C420 above it). **`AGREES` on both.** But that makes the "exposed" cell worse,
not better: the map states a cutoff-based verdict two lines above the paragraph explaining why the cutoff means
nothing.

---

## F20 · Branch 1's most important finding is not in the paper — and it undercuts a preregistered gate the paper reports as a pass · `MAP-MISSING-IT` (in the paper's direction)

**Map location.** `:237–243`.
**Paper location.** `:2769` (Tier 0), `:1524–1527`.

**Map, verbatim:**
> ⛔ **AND THE CRITERIA FAILED THEIR OWN POSITIVE CONTROL.** NR4A1 **Cys551** — the site a real degrader is
> believed to use — does not pass the pre-specified exposure cutoff (RSA 0.165 against 0.25) in **0 of 25**
> frames. … **So "C397 is flagged in 20/20 conformers" is worth nothing on its own** — the same criteria miss
> the known site.

**Paper's Tier-0 gate outcome** (`:2769`):
> | 0 | **Categorical-axis screen.** … | $0 CPU | **pass on both axes** — an **exposed** paralogue-unique
> cysteine within exit-vector reach, and three **exposed** paralogue-unique lysines (figures in §2.10) |

**VERDICT: `MAP-MISSING-IT`, inverted — the map found something the paper needs and neither document connects
it.** The paper's Tier-0 **pass** turns on the word *exposed*, adjudicated by the same `EXPOSED_RSA = 0.25`
cutoff that the map's branch-1 artifact shows **fails to recover NR4A1 Cys551**, the one NR4A-family covalent
site with literature support. `grep` finds no mention of Cys551's exposure failure, of the rank-based
replacement, or of `nr4a3-covalent-handle-ensemble.json` anywhere in the paper or SI. This is the single most
consequential thing the map knows that the manuscript does not: a preregistered gate reported as a clean pass
rests on a criterion with a demonstrated false-negative on its own positive control. **It is also a gap in the
map**, which states the finding in branch 1 and then never propagates it — §5b Route B still describes the
categorical basis as *"✓ opened 2026-08-02"* without the caveat, and §6 item 3 records branch 1 as *"✓
complete"* with no note that its criteria are known to be mis-calibrated.

---

## F21 · The map's §6 has no row for the paper's own decisive follow-ups · `MAP-MISSING-IT`

**Map location.** `:370–380`.

Map §6, as committed:

| # | item | map state | in the paper? |
|---|---|---|---|
| 1 | Does anything bind the pocket? — wet lab | ○ future | scoped correctly in STRATEGY.md; see F15 |
| 2 | Known-answer test for pose prediction | ✓ → ○ re-run | *(excluded from this audit)* |
| 3 | Is there a ligandable NR4A3 cysteine? | ✓ complete | branch 1 not in the paper; criteria mis-calibrated (F20) |
| 4 | Rebuild the ternaries by the assembly route | ◐ in work | **not mentioned in the paper** |
| 5 | Run the CREBBP/BRD4 benchmark | ◐ in work | **not mentioned in the paper**; STRATEGY.md says unrun + unauthorised (F4) |
| 6 | ≥3 ternary models per paralogue | ○ future | ✓ `:2501–2502`, and `nr4a-ternary-signature.json` `sentence_replicated` |

Paper items with a stated gating role and **no row**:

1. **Matched 8XTT-anchored / crystal-seeded paralogue ABFE legs** — the paper's twice-named *"decisive
   follow-up"* (`:1299–1301`, `:2520–2522`).
2. **The generation-matched null's paralogue-pocket arm** — *"**The arm that speaks most directly to the
   generative confound** — a fresh generation into a *paralogue* pocket, where any NR4A3-selective survivor is a
   manufactured false positive — **has not been run**"* (`:1196–1199`). This is the outstanding control on
   `denovo_401`'s selectivity, i.e. directly on node `B`.
3. **The frame-level generation-receptor dependency audit** — an explicit *"submission gate"* (`:2259–2265`).
4. **The paralogue-specific pocket-opening free-energy penalty** — *"this term is **potentially decisive** and
   may differ across the three paralogues … paralogue-specific opening penalties could **narrow or even
   reverse** the conditional margin"* (`:2339–2343`). Every ΔΔG on the map's binder path is conditional on it.
5. **AR/MR energetic cross-binding check** (SI `:213–219`).

**VERDICT: `MAP-MISSING-IT`.** The map's §6 closes with *"Four of the six are moving or done; the two ○ rows are
gated on something else … **There is no row here waiting on a decision**"* (`:379–380`). On the paper's record
there are at least five unrun items with stated gating roles, of which items 2–4 are $0-to-cheap and none is
gated on a bench. The reassurance is a consequence of the list being short, not of the backlog being clear.

---

# Language discipline (task item 5)

`python3 research/manuscripts/lint_claims.py` → **0 ERROR, 36 WARN** across 2 files (24 in the paper, 12 in the
SI). By rule family: **R4-confirms 23 · R1-nr4a3-selective 12 · R4-proves 1**. Only two rules fire.

**⛔ None of the 36 touches the five prohibited categories** in CLAUDE.md §1 / STRATEGY.md — proteome-wide
selectivity, EMC efficacy, safety, therapeutic window, clinical readiness. Verified by reading every warning's
context line. The paper is, if anything, over-defended on all five: SI §S1 hedges the anti-target result to *"a
screen-level observation from a 9-target panel, **not a proteome-wide selectivity measurement**"* (SI `:51`);
§4 `:2508` states *"This paper's claimed contribution is the target's **computational
druggability/selectivity, not EMC efficacy**"*; §2.10 closes *"no statement about efficacy, safety, a
therapeutic window, or clinical readiness"* (`:1776–1777`).

**Character of the warnings.** A clear majority are false positives on text that is *denying* validation — the
linter matches the token, not the polarity:

- `:2608` *"remains a docking/endpoint/ABFE-tier prediction … unsynthesized and **un-validated**"*
- `:2533`, `:2707` *"only a **ligand-bound** experimental structure could **validate** the warhead-engaged pose"*
- `:2901` *"[**Validated** direct fusion target.]"* — a bracketed reference-scope tag, not a claim
- `:149` (`R4-proves`) *"nuclear receptors have **proven** a favourable degrader class"* — about the modality's
  clinical record, cited, and immediately followed by *"strong precedent for the *modality* is not precedent for
  the *pocket*"*

**Four are substantive and worth a look, none inherited by the map:**

| location | text | why it is over-strong |
|---|---|---|
| SI `:62` | *"This pipeline **is validated** on a positive control"* (Boltz CRBN/lenalidomide) | the same paragraph then calls it *"memorization-consistent"* and *"a **necessary sanity check, not a demonstration of generalization**"*. The lead clause is the one that gets quoted. |
| SI `:229` | *"**Lead — NR4A3-selective (the validated path):**"* | **the strongest residual over-claim in either file.** It heads the indication table (EMC, AciCC) and pairs the R1 term with "validated" in four words, in the one place a reader skims for the bottom line. `:2478` says the opposite: *"**Every paralogue-selectivity statement in this work is therefore an unvalidated prediction.**"* |
| SI `:285` | *"the endpoint tier **confirms** `denovo_9` binds all three"* | single-snapshot MM-GBSA, the tier the decoy null shows is non-specific |
| SI `:70` | *"RDKit-**validated** C41H56N4O8"* | benign (it means the formula parses) — but note this is the same sentence F16 turns on |

**Does the map inherit or repeat any of it?** **No — not one of the 36 phrases appears on the map.** But two
structural points follow:

1. **The map is not language-linted at all.** `lint_claims.py` `DEFAULT_TARGETS` (line 56) is exactly
   `["research/manuscripts/nr4a3-degrader-paper.md", "research/manuscripts/nr4a3-degrader-paper-SI.md"]`. The
   map **is** in `lint_consistency.py`'s target list (`pinned-figures.json` → `targets`, 12 files) and passes at
   **0 ERROR** — but that linter checks pinned-number consistency, not claim language. So the map's own
   `PASSES` / *"✓ strong, and already measured"* / *"the validated descriptor"* / *"Chemical basis: ✓ strong"*
   phrasing is unchecked by the rule family that would flag it. **F7 and F14 are R4-shaped over-claims that no
   linter currently sees**, in a file CLAUDE.md instructs every session to read first.
2. **`lint_consistency` at 0 ERROR does not cover F1, F10 or F18.** The map's superseded 4/20 (F1), its 76 %
   (F10) and its three-vs-four cysteines (F18) all pass the consistency linter, because none of those three is
   a registered pinned figure. Adding 4/20 → 3/20 and the cysteine count to `pinned-figures.json` would make CI
   catch the first and third.

---

# Verified-correct register (`AGREES`)

Recorded so the report is not read as uniformly negative — these were checked and hold, most of them verbatim.

| map claim | map loc | verified against |
|---|---|---|
| §2.4 handle numbers: 10 lining, 7 divergent (L406/T407/T410/R412/I484/I531/L534), 5 pocket-facing (L406/T410/I484/I531/L534), T407+R412 splay | `:330–333` | paper `:595–599`, word for word (provenance caveat: F7) |
| all ten Pocket-5 residues ortholog-invariant, six species, ~300 My | `:334–336` | paper `:622–626` |
| structural selectivity descriptor: Gln98 Oε1 → Arg12 Nη2 **2.88 Å** vs Leu1545 | `:159` | paper `:2192–2194`; `selcal-interface-signature.json` (`distance_A: 2.88`) |
| ternary generator: 6HAX **0.618**, 9DTY **0.839**, iRMSD **0.67 Å** | `:160` | paper `:2137`, `:2154` |
| pmx/GROMACS barnase–barstar Y29A **+4.42 ± 1.08 vs +3.4** | `:161` | paper `:2401–2403` |
| co-folding **DockQ 0.023–0.046 ≈ true structure moved 32 Å** | `:164`, `:142` | paper `:2119–2121`, `:2145–2149` |
| E1 attempt p-values **0.393 / 0.747** | `:165`, `:142` | paper `:2003` (0.3929), `:2080` (0.7468) |
| ternary predicted for all three paralogues at comparable confidence | `:183` | paper `:720`; SI `:75` (iptm 0.72/0.83/0.82) |
| ternary signature: one sequence-encoded candidate, five placement artifacts, one model per arm vs a three-model bar | `:184` | paper `:2499–2504`; `nr4a-ternary-signature.json` `result` + `sentence_replicated` |
| target row: transfer prior, near-invariant clonal fusion, no LoF experiment, dTAG delegated | `:185` | paper `:2508`, near-verbatim |
| §2.5 ternary molecule has no `_chem_comp_bond` in any of 3 models; entered as an env var | `:105`, `:183` | `nr4a-ternary-ligand-provenance.json` (`n_recovered: 0`); STRATEGY.md `:500–505` (absoluteness caveat: F16) |
| "built by the failing route" | `:183` | `nr4a-ternary-signature.json` `structure_provenance`; paper `:2501–2503` (paper self-conflict: F17) |
| NR4A1 Cys551 fails the 0.25 RSA cutoff in **0 of 25** frames; ranks **3/18** on every observable, C397 and C420 above it | `:237–241` | `nr4a3-covalent-handle-ensemble.json` `control_recovery` + `control_rank` |
| unique cysteines sit **11–19 Å** from the pocket | `:235` | artifact `summary.per_unique_cysteine_across_8xtt`, pooled 10.93–18.93 Å |
| Gate 3A supported / Gate 3B unresolved | `:179` | paper `:2747–2748` |

---

# Two things I did not verify, recorded as refusals

1. **Whether a CREBBP/BRD4 ABFE leg is actually running** (F4). The map says *"solvent leg dispatched"* / *"its
   first leg is now on spot"*; STRATEGY.md says the test *"[has] never been run"* and is *"not authorized"*.
   Settling it requires reading a live billing or CI record, which is outside a read-only $0 document audit.
   Recorded as a conflict, not resolved.
2. **Whether NR4A3 Glu208 aligns to Pro in NR4A1 and Tyr in NR4A2** (F17). `nr4a-ternary-signature.json`'s
   `result.detail` and `result.pairwise` blocks record the discriminating positions and their NR4A3 identities
   but I could not read out a paralogue residue identity for position 208. The map is the only place this
   substitution appears; it is not in the paper. Not asserted either way.

---

# Appendix — audit method

- Map read in full at `git HEAD 96f5543f9` (395 lines); paper (3177) and SI (939) read in full across
  overlapping windows.
- Every map figure traced to its named artifact where one is cited; artifacts re-read and, where the map quotes a
  summary statistic, **recomputed** from the raw entries (F10's median over 16 per-cysteine values).
- Coverage measured by `grep -c` over the map for 20 paper topics rather than by impression.
- `lint_claims.py` and `lint_consistency.py` executed; rule-family counts taken from their output, target lists
  read from source (`lint_claims.py:56`, `pinned-figures.json` → `targets`).
- Retraction census built from `grep -niE "\bretract|\bwithdraw|\bwithdrawn\b"` across paper + SI (32 hits),
  de-duplicated by result.
- Concurrent-edit exposure bounded with `git diff -U0` hunk ranges; §3, §4, §5 branch 1, §5b and §6 confirmed
  untouched.
