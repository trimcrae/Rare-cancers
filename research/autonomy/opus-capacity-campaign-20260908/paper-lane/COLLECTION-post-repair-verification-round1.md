# COLLECTION — post-repair verification round 1, and the endpoint producer repair

Collected 2026-09-08 by the campaign parent. All workers `claude-opus-5`, all transcripts retained.

## The verifiers

Seven independent readers, one per repair set, each given the frozen AFTER text and diff and told
that **zero findings is a valid result**. None was asked to re-review a paper.

| worker | scope | tool pairs | outcome |
|---|---|---|---|
| VD1 | degrader gate repairs | 28 | 5 of 5 supported; 4 minor repair-induced defects |
| VN1 | neoantigen repairs | 25 | 4 of 4 supported; **zero repair-induced defects** |
| VF1 | fusion-partner repairs | 23 | 4 of 4 supported; 1 defect, 1 guard breakage |
| VM1 | monovalent repairs | 25 | 5 of 5 supported; 1 defect |
| VB1 | mortality + biomarker repairs | 32 | 17 of 17 verdicts; 6 minor defects |
| VT1 | TCIP + synth-lethal + vaccine repairs | 32 | 18 of 18 verdicts; 3 defects |
| PR1 | endpoint producer repair | 23 | fix delivered as a diff |

**Every defect they found is now applied.** The substantive ones:

- **VT1 caught a real integrity error of mine.** I had moved the vaccine paper's `last_verified` to
  2026-09-01 because an artifact it reports carries that stamp. `systems/systems_check.py:1918`
  defines the field as "someone READ it and confirmed it is still true, and a bulk date claims a
  verification nobody performed". An artifact's stamp is not a reading of the document. The date is
  now **2026-09-08**, the day VP1 actually read it end to end.
- **VB1 caught two false statements in my own Table 2 note**: I called the combined row "the
  arithmetic sum of the two strata" when only three of five columns are sums, and attributed the
  unset pooled field to the decomposition artifact when it is `convergence.cause_split_overall_
  competing_share_pct` in `emc-relative-survival.json`. Both corrected. It also caught a direction
  pointer ("the two ratios below" pointing above) and an orphaned referent my §3.6 insert created.
- **VF1 caught that my §3.3 exclusion list under-accounted the Huang gap by five patients** — the
  enumerated TCF12 and unidentified cases explain 24→23 and part of 57→50, but five are lost to
  missing follow-up, which the paragraph did not name. Now named, with a §4.7 pointer.
- **VD1 and VM1** caught pointer and column defects: a forward reference to "item (d)" that lives in
  item 8, a date occupying a Cost column, a provenance row still naming only the superseded source.
- **VN1 found nothing wrong with the repair** and instead flagged a **pre-existing** banner claim, in
  the first paragraph a reviewer reads, asserting the peptide "exists in *no* normal protein" and
  therefore full tumour- and fusion-exclusivity — the same proteome-wide absence claim my §4 repair
  had just removed three sections later. Now qualified to a sequence-level statement checked against
  two parent proteins only.

Two workers **corrected my own briefs**, which is worth recording: PR1 refused the write permission my
dispatch granted, because `COMMON-BRIEF.md` §1 supersedes a dispatch's write path, and returned a diff
instead; and HW1 earlier found that a `⛔` field I told it to cite is literally `null`.

## The endpoint producer repair (PR1), landed

The narrative count in `endpoint_regime_map.py` is now **derived** from the `per_condition` rows the
same producer emits, instead of being hand-written. It said "twelve"; the rows say thirteen.

Landed and verified by the parent: `--check` failed on the committed artifact before regeneration and
passes after; the producer was run **once** on its existing pinned inputs; and the artifact comparison
is exact — **1,132 leaves, key sets identical, exactly one differing leaf** (the narrative string),
with **847 numeric and 58 boolean leaves all equal**. The module's own suite: **70 passed, exit 0**.

## One guard breakage, owned and being repaired

VF1 predicted, and the parent confirmed by running the suite, that the fusion-partner prose repair
breaks bindings in `test_fusion_partner_prose_matches_its_artifact.py`: the generator and its artifact
still carry the wording the prose moved off. Six tests failed; after correcting the prose's own
unbound `n = 73` token, **five remain**, and they are the generator/artifact side. That file's own
docstring says the fix belongs in the prose or the artifact, never in the regex, and the prose is the
correct side — so a bounded producer repair (PR2) is running under the coordinator's separate
authorization for exactly that. **The regexes are not being loosened and no binding is being deleted.**

## Reports retained, findings not yet applied

TD1 (transcriptional/proteostatic dependency), MF1 (degrader methods failure record) and FO1 (fusion
transcriptional output) returned substantial findings that are **not** yet applied. Their transcripts
are retained. Their headline items, for the next pass: TD1 found §1 printing 176 models where every
leaf it reads carries `n_sarcoma = 91`, and no statement anywhere that the scored gene groups are
repo-curated rather than published signatures. MF1 found a stale abstract sentence — "no fourth is
staged" — that the roadmap superseded on 2026-08-07, one day after that draft's `last_verified`, and
which the draft's own §5.1 already contradicts. FO1 found a percentile denominator stated as the
deposit size (14,120) where the artifact's exclusion rule gives 13,708, and a "42–70%" range whose
upper bound rests on a query that returned `null`.

## Gate state

`lint_consistency` 0 ERROR across 29 files throughout. Style: the mortality and vaccine papers are at
0; the neoantigen paper is back at its 108 baseline; the fusion-partner paper is 191 against 189, and
the TCIP and degrader-comparison papers are each one or two above baseline, from glyphs and em-dashes
in the applied text. None of these papers has had a style pass and none passes `lint_style`.

---

## Dated append — VC1, the eighth verifier, and a correction to this record

VC1 verified the closed-routes repairs: **8 verdicts, all CONFIRMED SUPPORTED**, at 15 tool calls.
`claude-opus-5`, 22 tool pairs observed.

It found one repair-induced defect, now applied: my §9 insert ended by calling the RT-SYNPROMOTER
trigger mismatch "exactly the failure mode §3.2 is meant to prevent", but §3.2's rule as the paper
states it admits a trigger naming a capability. `TR-VECTOR-TUMOUR-DELIVERY` names a capability, so
§3.2 is satisfied and the defect §9 found is a different one. The clause now says so.

**A correction to this record.** The append above says all three removed glyphs "came from `⚠` glyphs
my applied text introduced". VC1 measured the frozen copies: on the closed-routes paper the glyph
count went 9 → 8, and one of the two glyphs removed there — the `**yes** ⚠ see §4.1` table cell —
**pre-existed my repair**, visible in the BEFORE copy. That is what makes the lint sequence land at 97
rather than 98. Only one of the three was mine on that paper.

VC1 also checked what the glyph removals cost and found nothing lost: the table row now names what is
contested and whose filing the "yes" belongs to, which the bare glyph did not, and the §9
qualification is carried entirely in plain prose naming the field, its value, and where the real
condition lives. It confirmed independently that no repair reopens or re-litigates a closed route.
