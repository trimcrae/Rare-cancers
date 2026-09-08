# Leaf-by-leaf JSON invariance across this correction's propagation

Compared: `BEFORE/emc-fusion-partner-pooling.json` (e99df639…, 130554 B) against the delivered
`research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` (bf2b8091…, 133116 B), i.e. across BOTH producer runs recorded in CHECK-RUN-RECORD.txt.
Method: every scalar leaf addressed by its full JSON path (dict keys and list indices), compared by path and
by value. Raw comparator output: `INVARIANCE-raw.txt`.

| quantity | before | after |
|---|---|---|
| total scalar leaves | 924 | 924 |
| leaves ADDED | — | 0 |
| leaves REMOVED | — | 0 |
| leaves CHANGED | — | 5 |
| **NON-STRING leaves changed** | — | **0** |
| numeric leaves (int/float, bool excluded) | 331 | 331 |
| numeric added / removed / changed | — | **0 / 0 / 0** |
| boolean leaves | 52 | 52 |
| boolean changed | — | 0 |
| list nodes | 20 | 20 |
| list nodes whose length changed | — | 0 |
| list nodes added | — | 0 |

**Zero numeric change, as expected. Nothing numeric moved, so nothing had to be stopped and reported.**
Membership is unchanged: no list gained, lost or reordered an element, and no cohort, analysis or citation
key appeared or disappeared.

The five changed leaves, all strings:

1. `$._generated_utc` — the producer's own regeneration timestamp.
2. `$.cohorts[5].context_note` — Suemitsu 2025 (correction 2).
3. `$.cohorts[13].context_note` — Sjögren 2003 (correction 1).
4. `$.analyses.C_partner_prevalence.question` — display label (correction 3).
5. `$.analyses.C_partner_prevalence.cohorts_excluded.sjogren-2003-prevalence` — the second live site of the
   same withdrawn recruitment-rule assertion (correction 1b; see CORRECTION-MAP.md, which flags it as an
   author-initiated extension of correction 1 for the parent to accept or revert).

Nothing else in the artifact moved.
