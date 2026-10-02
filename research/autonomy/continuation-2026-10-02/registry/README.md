# Registry response extraction conformance cases

This package demonstrates literal extraction behavior using known ClinicalTrials.gov
examples. It supplements the frozen oncology corpus correction. It does not establish
a new general extraction method, estimate registry error prevalence, harmonize clinical
response estimands, or provide independent held-out validation.

The extractor retains complete outcome objects and full literal measurement objects.
Each output identity includes the input SHA256, source study index, NCT identifier,
outcome index and outcome-content digest. Class index and outcome-local group ID identify
rows. Identical OG identifiers in different outcomes are never joined.

Normalized aliases are deliberately conservative and versioned. Qualifications,
combined categories and unfamiliar labels remain literal. Duplicate aliases, missing
cells and noninteger values do not become zero. `normalizedIntegerCells` means exact
label/integer recognition only. `explicitParticipantCountSemantics` separately reports
whether the source explicitly uses COUNT_OF_PARTICIPANTS with Participants units.
Neither field establishes clinical endpoint equivalence.

All denominator entries remain available. Class-specific entries take precedence.
Overall denominators are eligible only when the complete parent outcome has one class
and the class has no denominator declarations. Duplicate participant-denominator
entries remain ambiguous even when values agree. Selected-category sums remain
separate from posted denominators. The utility does not calculate response rates.

The source outcome object preserves empty classes, unmeasured categories, analysis
metadata, descriptions and measurement limits/comments. Row expansion includes declared
groups with no measurements; this represents missing data, not zero observations.

The API schema already distinguishes outcomes, classes, categories, measurements,
parameter types, units and denominator scopes:
https://clinicaltrials.gov/api/v2/studies/metadata

The reporting template distinguishes measurement type, unit and analyzed population:
https://cdn.clinicaltrials.gov/documents/results_table_layout/DataEntryTable_OMForm.pdf

## Inputs and provenance

Frozen inputs must match the complete original-byte SHA256 in sources.json, including
the archived text preamble. The immutable revision is recorded separately. Filters
apply after verification and preserve original source study indices.

Use source kind archived for pinned corpus inputs, live-capture for separately
captured live API responses, and synthetic only for explicitly synthetic fixtures.
A digest records identity, not authenticity: use the reviewed manifest for archived
expected hashes, rather than calculating an expected hash from an untrusted download.

Current API responses may change. Live capture must record retrieval time, URL, exact
response-byte SHA256 and source last-update date. Never substitute live captures into
the frozen audit or change its 552/575 counts.

The original-byte receipts in sources.json are distinct from earlier exploratory
PowerShell receipts that hashed UTF-8 re-encoded response text. Those earlier hashes
are not expected raw-byte hashes and are not used by this package. Live response
bodies were consumed in memory and were not persisted.

Frozen manifest receipts were recovered from reconciliation-result Git blob
fa160178f6c6dd706d94000ce81e2341a6792fa5 at repository revision
da49c4e836533253825587f83656675dac4c913b. No large frozen inputs were downloaded locally.

## Checks

conformance_checks.synthetic_checks() exercises duplicate aliases, invalid counts,
conflicting denominators, an unmeasured second class, non-count measurement metadata,
checksum rejection and preservation of source indices after filtering.

conformance_checks.real_checks(document, receipt, fixtures) exercises the four named
real-source cases in cases.json and returns the case IDs actually checked.
The caller must require that the union of returned IDs equals every expected case ID.
An empty or partial set is not successful validation.

Initial execution: seven synthetic checks passed; four real case groups passed using
three live API responses on 2026-10-02. Frozen-input validation was not executed locally.
The seven synthetic checks passed after the output filter was added; live checks ran
before that small filter addition. Dedicated frozen CI must cover the final package.
