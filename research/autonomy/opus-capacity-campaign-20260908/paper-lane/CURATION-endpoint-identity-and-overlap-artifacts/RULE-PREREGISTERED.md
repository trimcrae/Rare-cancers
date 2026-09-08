# Pre-registered deterministic selection rule (JOB 2) — recorded BEFORE application

Recorded 2026-09-08, before any response value was read. Everything below was derived from
**record structure only** (key stability, field presence, title/qualifier vocabulary, denominator
placement). No numerator, percentage or effect was inspected when this rule was written; the
structural census that motivated it counted keys, groups, time frames and denominators only.

## Unit of analysis

**One reported response measurement per (trial, results-group cohort).**
Key = `(nctId, normalised results outcome-group title)`, normalisation = Unicode NFKC, casefold,
whitespace collapsed, leading/trailing punctuation stripped.

Rationale from structure, not from results:
- `nctId` is the only stable study identifier in the payloads.
- Outcome-measure group **ids** (`OG000`, …) are scoped to a single outcome measure and are NOT a
  study-level cohort key: measured on this cache, 1,425 of 4,235 result-bearing studies reuse one id
  for more than one group title. Identity across outcome measures must therefore go by title.
- Protocol `armGroups.label` cannot serve as the unit: only 4,227 of 17,124 distinct results-group
  titles match a protocol arm label exactly, so most results groups are not resolvable to a
  registered arm without inference the source does not license.

## R0 — Record canonicalisation (applied first)

One canonical study record per `nctId`: among the copies returned by different payloads, take the
copy with the most populated fields; ties broken by payload name ascending. Justified because every
cross-payload duplicate differs only by **field set** (the accrual queries request fewer fields),
never by conflicting content.

## R1 — Candidate outcome measures

An outcome measure is a candidate for a cohort iff **all** hold:
1. `title` matches the fixed response regex
   `\b(overall response|objective response|best overall response|response rate|orr\b|disease control rate|clinical benefit rate)` (case-insensitive);
2. `reportingStatus == "POSTED"`;
3. it contains a group whose normalised title equals the cohort key's group title;
4. it carries a `denoms` entry with `units == "Participants"` holding a count for that group id.

## R2 — Priority ladder, applied in order, to pick exactly ONE outcome measure per cohort

a. **Type**: `PRIMARY` > `SECONDARY` > `OTHER_PRE_SPECIFIED` > `POST_HOC`.
b. **Population**: ITT / full-analysis-set flagged > unflagged > per-protocol / evaluable flagged.
c. **Confirmation**: `confirmed` flagged > unflagged > `unconfirmed` flagged.
d. **Assessment**: independent / central / BICR flagged > unflagged > investigator flagged.
e. **Cohort completeness**: largest reported `Participants` denominator for that group.
   (Denominator only — never a numerator, rate or effect.)
f. **Registration order**: smallest outcome-measure index within the study's results section.

Flags b–d are set from the fixed regexes over `title + description + populationDescription`:
ITT `\b(intent[- ]to[- ]treat|intention[- ]to[- ]treat|itt|full analysis set|fas)\b`;
PP `\b(per[- ]protocol|pp population|evaluable|efficacy[- ]evaluable|response[- ]evaluable)\b`;
confirmed `\bconfirmed\b` (and not `\bunconfirmed\b`); unconfirmed `\bunconfirmed\b`;
central `\b(independent|central|blinded independent|bicr|irc|iac)\b`; investigator `\binvestigator\b`.

## Ties and exclusions — both recorded, exhaustively

- Every cohort resolved at step **e** or **f** is recorded as a TIE with the step that resolved it
  and the number of candidates still competing at that step.
- Every excluded record is recorded with its exclusion reason: no results section; no
  response-titled outcome measure; `reportingStatus != POSTED`; no `Participants` denominator;
  non-`Participants` denominator unit.
- Cohorts whose group title is a **pooled/total** label (`total`, `overall`, `all participants`,
  `all patients`, `combined`) are **flagged, not dropped**: they overlap the other cohorts of the
  same trial and must never be counted alongside them.

## What this rule explicitly does NOT claim

It does not claim a selected cohort is a randomised arm, an independent trial, or a distinct patient
group from any other cohort in the same trial. It selects one measurement per named results cohort;
that is all the source supports.
