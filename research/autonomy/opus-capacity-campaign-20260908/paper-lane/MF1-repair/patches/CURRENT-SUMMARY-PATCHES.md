---
id: DOC-MF1-CURRENT-SUMMARY-PATCHES
title: "MF1 repair — limited current-summary patches for the parent to apply"
level: L4
kind: memo
status: live
canonical_for: []
purpose: Hand the integrator the exact, verified-unique shared-file edits the MF1 correction batch needs, so no current summary contradicts the corrected manuscript.
scope: research/manuscripts/nr4a3-program-map.md and systems/graph/publications.json only. It touches no original execution output, result file or protocol history.
audience: [maintainers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---
# MF1 repair — limited current-summary patches, for the parent to apply

**2026-09-08.** These are the **only** shared-file edits the MF1 correction batch needs. Each one exists
because leaving it would put a current summary in direct contradiction with the corrected manuscript, which
the review's finding F03 names explicitly ("… and any current summary it asks readers to treat as
authoritative"). ⛔ **The MF1 repair owner did not apply them** — `research/manuscripts/nr4a3-program-map.md`
and `systems/graph/publications.json` are parent-owned shared files.

⛔ **None of these touches an original raw execution output, a result file or a protocol history.** All
targets are narrative annotations or endpoint metadata. The primary artifacts they misread
(`nr4a3-5aks-reduction.json`, `valb-triangle-reduction.json`, `valb-triangle-closure.json`,
`r5-cross-method-cavity-attribution.json`, `selcal-deepternary-frame.json`) are unchanged and remain the
evidence.

⚠ **`research/modalities/instrument-census.md` / `.json` are GENERATED from the roadmap** (`§3.1`/`§3.2`) by
`research/modalities/instrument_census.py`. Applying P3, P4 and P5 and regenerating the census carries the
correction into the census rows for `V5` and `V16` automatically; the census must **not** be hand-edited.

Each patch gives an exact unique `OLD` string and its `NEW` replacement. All `OLD` strings were verified
unique in their target file at commit `9716bf3df803ba63728c1c240f994871b479ef58`; re-verify before applying
if the files have moved since.

---

## P1 · `systems/graph/publications.json` → `PUB-METHODS.what_it_would_claim`

*Why:* the field claims "exactly which" and "each with its diagnosed mechanism". F03 establishes that the
wrong-sign calibration failure's mechanism is **not** uniquely diagnosed, and F05 establishes that the
register is route-selected rather than a complete ascertainment. The corrected manuscript states its claim
in §2 and discloses this divergence rather than silently restating the field.

**OLD**

```
"A computation-only program can state, with its instruments' known-answer controls attached, exactly which of its selectivity claims its methods were able to support and which they were not — and the disclosed failures, each with its diagnosed mechanism, are the transferable result."
```

**NEW**

```
"From one computation-only program's retained instrument records, it is possible to state which of its paralogue-selectivity statements its methods were graded as supporting and which they were not, with each instrument's control type, execution state, inferential outcome and claim scope reported separately — and the enumerated failures, with the evidence retained for each, are the transferable result."
```

## P2 · `systems/graph/publications.json` → `PUB-METHODS.outcome_potential_why`

*Why:* same finding; "each disclosed failure carries a diagnosed mechanism" is not supportable.

**OLD**

```
"A failure record. Valuable because each disclosed failure carries a diagnosed mechanism another group can act on, and by construction not a treatment lead."
```

**NEW**

```
"A retrospective audit of one program's instrument records. Valuable because each enumerated failure carries the evidence that is actually retained for it — including where the cause is not identified — and by construction not a treatment lead."
```

---

## P3 · `research/manuscripts/nr4a3-program-map.md` — the 5a-KS "bound" (F02)

*Why:* `nr4a3-5aks-reduction.json` records a two-seed `replicate_sd`. The reducer computes a difference of
species means and `sqrt(sd_A² + sd_B²)`; it constructs no confidence interval, equivalence test or
calibrated physical-effect bound. The 0.65 kcal/mol "2σ" exclusion is not in the artifact.

**P3a — §2.10e narrative (one occurrence, line ~691)**

**OLD**

```
> as likely to be unresolvable. It came back as a **BOUND** — excluding ≳ 0.65 kcal/mol at 2σ — because its
> design condition (two seeds per arm) was met.
```

**NEW**

```
> as likely to be unresolvable. ⛔ **Corrected 2026-09-08 (MF1 final review, F02):** it came back as an
> **EXPLORATORY CONDITIONAL ESTIMATE with a two-seed between-seed dispersion**, compatible with zero at the
> observed precision, because its design's operational completion condition (two seeds per arm) was met. It
> is **not** a confidence interval, an equivalence result or a calibrated effect bound, and it does not show
> the marginal wedge is absent.
```

**P3b — the §2.10e result table row (one occurrence, line ~984)**

**OLD**

```
| what it bounds | the design could only resolve **\|S\| ≳ 0.65 kcal/mol** (2σ); it did not |
```

**NEW**

```
| what it does NOT bound | ⛔ **corrected 2026-09-08 (F02): no bound is established.** The recorded uncertainty is a two-seed `replicate_sd`, not a confidence, equivalence or effect bound, and the earlier "\|S\| ≳ 0.65 kcal/mol (2σ)" exclusion is withdrawn |
```

**P3c — the `V16` census-source row (one occurrence, line ~1770)**

**OLD**

```
It is a **BOUND**: the design could only have resolved *"a wedge contribution of roughly \|S\| ≳ 0.65 kcal/mol (2σ)"*
```

**NEW**

```
⛔ **Corrected 2026-09-08 (F02): it is NOT a bound** — an exploratory conditional estimate with a two-seed between-seed dispersion, compatible with zero at the observed precision
```

⚠ Two further repetitions of the withdrawn bound sit at lines ~2416 (`R11` row) and ~3238 (dependency
row). They carry the same wording and should be corrected in the same pass; they are listed here rather
than transcribed because their surrounding text differs and the parent owns the merge.

---

## P4 · `research/manuscripts/nr4a3-program-map.md` — closure does not localise the miss (F03)

*Why:* `valb-triangle-closure.json` itself records that endpoint-state errors are **invisible** to closure,
which makes the statistic blind to that class rather than diagnostic of it. The residual is one linear
contrast of six edge errors, a conservative shared-sampling bias telescopes the same way, and
`valb-failure-propagation.json` gives power ≈ 0.63 at its own measured upper noise bound.

**P4a — the landed-`R` reading (one occurrence, line ~1287)**

**OLD**

```
(0.216 at `sigma_leg = 0.045`). Read against the mapping below, that says valB_mini's miss is an
**ENDPOINT-STATE error, and more sampling will not fix it.**
```

**NEW**

```
(0.216 at `sigma_leg = 0.045`). ⛔ **Corrected 2026-09-08 (MF1 final review, F03): that does NOT identify the
miss.** A small residual is compatible with several unresolved error sources — the statistic is one linear
contrast of six edge errors, and a conservatively structured bias from shared incomplete sampling telescopes
out of it — so it neither localises the cause to an endpoint state, nor excludes sampling error, nor shows
that more sampling cannot help. The wrong-sign **operational calibration failure** stands on its own.
```

**P4b — the two-branch mapping (one occurrence, line ~1304)**

**OLD**

```
- **`R` ≈ 0 ⇒ an ENDPOINT-STATE error.** The bias is a per-endpoint state function, it telescopes out of any
  cycle, and **more sampling will NOT fix the miss.**
```

**NEW**

```
- **`R` ≈ 0 ⇒ NOTHING IS IDENTIFIED.** ⛔ **Corrected 2026-09-08 (F03).** An endpoint-state bias telescopes
  out of any cycle — so closure is **blind** to that class, not diagnostic of it — and so does a
  conservatively structured shared-sampling bias. A small residual therefore excludes neither, and the
  earlier reading ("more sampling will NOT fix the miss") is withdrawn.
```

**P4c — the `V5` census-source row (one occurrence, line ~1759)**

**OLD**

```
the closure triangle localises the miss to an **endpoint-state** error, so more sampling will NOT fix it
```

**NEW**

```
⛔ **corrected 2026-09-08 (F03): the closure triangle does NOT localise the miss** — it is blind to endpoint-state error rather than diagnostic of it, and does not exclude shared sampling bias
```

---

## P5 · `research/manuscripts/nr4a3-program-map.md` — pose disagreement is not orientation-only (F09a)

*Why:* `r5-cross-method-cavity-attribution.json` → `rollup` measures 6 systems, 5 gradeable, **4
same-cavity and 1 different-cavity**, with the sixth ungradeable and excluded from the denominator, and
states that the cavity call is receptor-conformer dependent.

**OLD**

```
and disagrees in ORIENTATION rather than in location.
```

**NEW**

```
⛔ **corrected 2026-09-08 (F09a): the disagreement is MIXED, not orientation-only** — 4 same-cavity and 1 different-cavity among 5 gradeable systems, with 1 ungradeable excluded from the denominator, so the cavity call is itself receptor-conformer dependent.
```

---

## P6 · `research/manuscripts/nr4a3-program-map.md` — the external 66-atom refutation (F11)

*Why:* the cited file `selcal-deepternary-frame.json` is a single SMARCA2 preparation record with **64**
degrader atoms recording superposition, snapping and readability. It does not contain the asserted 66-atom
equality on a released benchmark case, and this repository does not hold the released-case comparison or the
primary protocol statement that a refutation of an external publication would require.

**OLD**

```
*Premise false.* The generator's own unbound protocol **supplies the native pose**, so there was never a generated conformer for us to constrain. Refuted by its released benchmark data, for $0, before it was built
```

**NEW**

```
*Premise treated as false on this program's own reading of the input protocol.* ⛔ **Corrected 2026-09-08 (MF1 final review, F11): the external refutation is WITHDRAWN.** The cited record is a single SMARCA2 preparation record with **64** degrader atoms — superposition, snapping and file readability — and is not the asserted 66-atom equality on a released benchmark case. What survives is a finding about this program's own assumed input protocol and the consequent relabelling; no defect in the external publication is asserted. Reopening requires the exact already-retained released-case coordinate comparison and the primary protocol statement
```

**OLD (the same row's evidence cell)**

```
shipped `ligand.pdb` ≡ native, **0.000 Å over 66 heavy atoms**
```

**NEW**

```
⛔ **withdrawn 2026-09-08 (F11)** — the cited file records a 64-atom preparation, not a 66-atom equality
```

---

## Application notes

1. Apply P1–P6, then regenerate the census: `python3 research/modalities/instrument_census.py`.
2. `research/manuscripts/methods-record/degrader-methods-failure-record-SI.md` is generated by
   `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/extract_mf1_inventory.py`; it
   does not read the roadmap and does not need regenerating for these patches.
3. ⛔ **Do not** edit `research/modalities/instrument-census.md` or `.json` by hand.
4. ⛔ **Do not** edit `research/modalities/selcal-verdict.json`, `selcal_panel.py`,
   `nr4a3-5aks-reduction.json`, `valb-triangle-reduction.json`, `valb-triangle-closure.json`,
   `valb-failure-propagation.json`, `nrv04-result-forensics.json` or any leg record. The PRT3789/ACBI2
   identity correction (F01) is made in the manuscript's current scientific summary only; the historical
   bytes stand as the record of what was run.
