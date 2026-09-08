# MTAP/PRMT5 — exact publication-readiness blockers, as at `91974780`

Recorded 2026-09-08 09:08 UTC. `PUB-MTAP-PRMT5`, `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md`.
**The F1 contract is CLOSED.** These blockers are delivered to the scientific orchestrator for
distinct owner decisions and are **not** to be repaired under F1, nor repeatedly re-opened while other
unfinished papers can advance.

## Blocker 1 — live commit-gate failure

`lint_consistency` **exit 1**, current and reproducible:

```
research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md:673: ERROR
[S-card_ratio_4090_over_3090_2_10] superseded value '2.102' stated without marking it superseded
```

The matched string `2.102` lies inside the index-reported DOI `10.1016/j.jbc.2022.102434`
(…202**2.102**434).

⚠ **Withdrawal of my own framing.** I previously called this "a naive-substring false positive". That
was **a reported interpretation, not a passed guard** — I am withdrawing it as a disposition. What is
measured is only this: the gate **fails**, and the matched substring lies inside that DOI. Whether the
rule is mis-scoped is a question for the owner, not a finding I have established.

**Reopening condition.** A separately justified, correctly scoped consistency-rule resolution with
meaningful verification. Explicitly **not** admissible: weakening the rule, adding an exclusion to
duck the match, or labelling a correct DOI "superseded" (which would be a false statement). Until
such a resolution exists, the manuscript **does not pass its commit gate**.

## Blocker 2 — publisher-level confirmation outstanding

The apparent peer-reviewed counterpart (JBC 2022;298(10):102434, PMC9513783) is **search-index-only**.
Publisher-level confirmation, and **cross-version identity and content**, are **UNCONFIRMED at the
level actually observed**. The manuscript now says exactly this, and that grade must be preserved:
existence is **indicated, not confirmed**, qualified together with the metadata; repeated index hits
are not publisher verification and are not verification that peer review occurred.

**Reopening condition.** Actual permitted evidence at publisher level. ⛔ **The four routes
(jbc.org, PMC, bioRxiv, ohsu.elsevierpure.com) are blocked and are not to be retried, reworded or
rerouted**, and no paid access or credential may be used. **Preprint-read findings stay attributed to
the preprint.**

## Blocker 3 — Appendix A attribution, unresolved

The corrections register attributes "a peer-reviewed fusion-dependent PRMT5 requirement in a second
EWSR1-fusion sarcoma **[2]**". That is the Ewing result, reference **[3]**; **[2]** is the
non-peer-reviewed preprint. F1 flagged rather than edited it — correctly, being outside its named
passages and inside a preserved register. **Reopening condition:** an accurate citation treatment
decided by the register's owner.

## Related, separately owned

**Repurposing canonical-draft identity** (the committed text is not the 2026-08-10 revised version its
review-response describes) is a **distinct unresolved integration/publication dependency** of
`PUB-REPURPOSING`, not of this paper.

## Status

**MTAP/PRMT5 is BLOCKED for publication readiness on all three counts.** The manuscript's scientific
content stands as corrected and qualified; nothing above is a reason to edit it further under a closed
contract. Work has advanced to the next eligible unfinished draft (G1, surface-targets).
