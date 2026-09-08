> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: tree unchanged (HEAD still `92abbcb…`, only the pre-existing untracked campaign dir), ingester exits 0 on real committed inputs, 17/17 tests pass at exit 0, and a deliberate mutation makes them fail at exit 1.

---

## Worker

**W15**, Lane 15 — data-ingestion / normalisation / evidence-retention.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), per my own system context. This is not an observed fact; the coordinator must extract the actual served model from the transcript. No environment variable names a model.

`date -u` at start: `Tue Sep  8 01:55:31 UTC 2026`. At end: `Tue Sep  8 02:01:17 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start, verbatim; long proxy/no_proxy lines elided only where marked):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
JAVA_TOOL_OPTIONS=... (proxy/truststore only, no model)
no_proxy / NO_PROXY / GLOBAL_AGENT_NO_PROXY / npm_config_noproxy=... (host lists only)
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
```

At end the same grep returns the same set; the model-relevant subset re-checked verbatim: `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_CODE_VERSION=2.1.42`.

Read commit `92abbcb905cacf07f14b238db50d1b98f6590374`, unchanged at end. Only untracked path is the pre-existing campaign directory. No repository file created or modified; all execution under `/tmp/claude-0/w15/`.

## Question

**Does this repository have any single normalised structure into which its scattered retained literature facts can be ingested, so that "what do we actually retain about drug X" is a query rather than a re-read of prose — and how large is the retention gap when measured?**

It is open because the lane's premise turned out to be right in a sharper way than stated: the repository has excellent *identifier* hygiene and essentially no *retained-fact* structure. The initial hypothesis I could have tested — "identifiers appear in prose but not in structure" — is **false**, and I report that as a negative result below before pivoting to the real gap.

## Prior-work check

```
$ rg -l -i "retained.fact|retained_fact|denominator_status|denominator-status" --glob '!.git'
(no output)

$ git ls-files | rg -i "retain|normali[sz]|ingest"
(no output)
```

Nothing in the tracked corpus defines a retained-fact record, a denominator-status vocabulary, or an ingestion/normalisation module. To find the nearest existing thing I searched by field rather than by name:

```
$ for f in $(git ls-files '*.json'); do python3 - "$f" <<'EOF'
... prints the path if the parsed JSON contains both '"denominator"' and '"quote"'
EOF
done
research/modalities/emc-care-delivery-evidence.json
```

Exactly one file. I also read `scripts/lit_probe_common.py`, `research/manuscripts/lint_citations.py`, `research/manuscripts/citation-provenance-ledger.json`, `research/literature/emc-trabectedin-denominator-2026-09-01.json` and `systems/schema/document.schema.json`.

**CLOSED-WORK items I confirmed I am not replaying.** I performed **zero** network retrieval — no probe, no fetch, no route replay, changed or unchanged. The Pazopanib, Sunitinib 2014, Trabectedin/RT 2018, Wagner 2020 and CTARC 2022 unrecovered sources are *read as committed records*, never re-requested. The anthracycline retention limit (median 4 cycles, range 1–8, denominator unknown) is the design case for the UNKNOWN-denominator invariant, not a fact I extended. I am not touching lane 11's source-index, the frozen external-validation comment, or the registry. I hit **no content-policy refusal** in this lane.

## Method / inputs

All read-only, at commit `92abbcb`. Python `3.11.15`, standard library only, no network.

| Input | Role |
|---|---|
| `research/manuscripts/lint_citations.py` | Reused as a library for `PATTERNS`, `extract()`, `TRAILING` — the repository's own definition of "an identifier", so the measurement cannot drift from the gate |
| `research/manuscripts/citation-provenance-ledger.json` | 237 entries; fields `{files, id, key, kind, note, status}` |
| `research/modalities/emc-care-delivery-evidence.json` | `findings[]` (4) and `corpus_quotes[]` (1) |
| `research/literature/emc-trabectedin-denominator-2026-09-01.json` | `series[]` (2) with integer `emc_n` / `emc_objective_responses` |
| `research/literature/arxiv-aso-route.json`, `research/literature/venue-fee-pages-2026-08-24.json` | `{url, attempts[], status}` fetch records, incl. real 403s |
| `systems/schema/*.schema.json` | Convention source: `$schema`/`$id`/`title`/`_role`/`_why`, the `_superseded_role` retention habit, and the practice of documenting *why* a value like `unverified` is legitimate rather than a hole |

Scratch: `/tmp/claude-0/w15/measure_gap.py`, `/tmp/claude-0/w15/pkg/retained_facts.py`, `/tmp/claude-0/w15/pkg/test_retained_facts.py`.

## Result

### R1 — What the existing machinery ingests, and what it drops

| Component | Ingests | Schema | Drops / does not hold | Row type |
|---|---|---|---|---|
| `lit_probe_common.py` | Europe PMC search hits | `{pmid, pmcid, doi, title, journal, year, citedBy, isOpenAccess}` | **Every claim, number, quote and denominator.** Bibliographic only. Correctly keeps `hitCount is None` (API failure) distinct from `0` | PRIMARY (code read) |
| `citation-provenance-ledger.json` | Identifiers in prose with no corroborating artifact | `{files, id, key, kind, status}`, 4 statuses | Any content. By design it asserts *nothing about the source* — only that nothing corroborates it | PRIMARY |
| `lint_citations.py` | Prose ↔ artifact anchoring | n/a (a gate) | Not a store; correctly redacts failed fetches so a 403 body cannot anchor a citation | PRIMARY |
| `emc-care-delivery-evidence.json` | 4 findings + 1 quote | Bespoke: `what_it_says`, `design`, `provenance` | Numbers live **inside prose sentences**; denominator inside `design` as `"n=439"` | PRIMARY |
| `emc-trabectedin-denominator-2026-09-01.json` | 2 series | Bespoke: `emc_n`, `emc_objective_responses` | Different key names for the same concepts as the file above | PRIMARY |

Four committed retention artifacts, four mutually incompatible schemas, none queryable across sources.

### R2 — The measured gap

```
$ cd /tmp/claude-0/w15 && python3 measure_gap.py
kind  prose_md  any_tracked_json  ledger_rows  prose_only(no json)  prose_not_in_ledger
PMID        362              2210           75                    0                  287
DOI         368              4854          112                    0                  256
PMCID       178              3944           27                    0                  151
TOTAL       908             11008          214                    0
tracked .json files carrying both a "denominator" and a "quote" field: 1
EXIT=0
```

| Quantity | Value | Row type |
|---|---|---|
| Distinct PMID/DOI/PMCID in `research/**/*.md` prose | **908** | PRIMARY |
| Prose identifiers absent from every tracked `.json` | **0** | PRIMARY (negative) |
| Ledger rows (identifier + status, no content) | **214** distinct ids / 237 rows | PRIMARY |
| Tracked `.json` files pairing a `quote` with a `denominator` | **1** | PRIMARY |
| Sources with any retained *content* after normalisation | **7** | PRIMARY |

**The negative result first, because it kills the obvious framing.** `prose_only = 0`. Every identifier in prose already appears in some tracked JSON — `lint_citations`' anchor gate works, and "identifiers are being lost" is **false**. I am not claiming a gap that does not exist.

**The real gap.** The 11,008 structured identifier occurrences are overwhelmingly *search-hit rows*: title, journal, year. An identifier being "anchored" means a probe once saw it in a result list, not that anything was read. After normalising every retention artifact in the tree, **7 sources out of 908** carry a retained fact with a claim attached — 1 at full-text-quote tier, 6 at abstract tier. That is the measured friction: **≈0.8% of the identifiers this repository cites have any machine-readable statement of what it knows about them.** The other ~901 require re-reading prose, or have nothing to re-read.

### R3 — The normalised structure, run on real inputs

```
$ cd /tmp/claude-0/w15/pkg && python3 retained_facts.py --root /home/user/Rare-cancers \
    --fetch-file research/literature/arxiv-aso-route.json \
    --fetch-file research/literature/venue-fee-pages-2026-08-24.json
{
 "n_records": 277,
 "n_distinct_sources": 274,
 "by_provenance_tier": {"FT_QUOTE": 1, "ABSTRACT": 6, "METADATA": 33, "UNCORROBORATED": 237},
 "by_denominator_status": {"STATED": 6, "UNKNOWN": 1, "NOT_APPLICABLE": 270},
 "by_access_status": {"FULL_TEXT": 18, "ABSTRACT_ONLY": 6, "METADATA_ONLY": 237,
                      "UNRECOVERED_403": 5, "UNRECOVERED_OTHER": 11},
 "n_with_computable_rate": 2
}
EXIT=0
```

All rows PRIMARY (re-expression of committed artifacts; no fact added). Note `UNRECOVERED_403: 5` and `UNRECOVERED_OTHER: 11` — sixteen refused routes retained as first-class rows rather than dropped, and `n_with_computable_rate: 2` out of 277, which is the honest shape of the evidence base.

The lane's motivating query now answers itself:

```
$ python3 retained_facts.py --root /home/user/Rare-cancers --subject trabectedin --json | ...
ABSTRACT | 27418251 | num 0.0 | den 2.0 STATED | 0 objective response(s) among 2 located EMC patients...
ABSTRACT | 36568164 | num 0.0 | den 3.0 STATED | 0 objective response(s) among 3 located EMC patients...
n = 2
EXIT=0
```

Two rows, separately, unpooled, with denominators 2 and 3 — matching the source artifact's own `pooled: false`. No prose was re-read.

### R4 — The code

Proposed path `research/manuscripts/retained_facts.py` (**the coordinator writes it; I did not**).

```python
#!/usr/bin/env python3
"""One normalised structure for every literature fact this repository has RETAINED.

WHY THIS EXISTS. Measured 2026-09-08 against commit 92abbcb: 908 distinct PMID/DOI/PMCID
identifiers appear in prose under `research/`; 214 of them have a row in
`citation-provenance-ledger.json` (which records ONLY that an identifier is uncorroborated,
never what was read); and exactly ONE tracked .json file in the whole tree carries both a
`quote` and a `denominator` field. Everything else that was actually read -- the anthracycline
median of 4 cycles, the located trabectedin responder count, the metastasectomy 8/29 -- lives
in a free-text field whose key differs in every file that has one (`what_it_says`,
`emc_best_response`, `text`, `answer`). A later analysis asking "what do we retain about
drug X" has to re-read prose, which is how a retained fact gets silently re-derived or lost.

⛔ THIS DOES NOT RETRIEVE ANYTHING AND DOES NOT JUDGE ANYTHING. It reads committed artifacts
and re-expresses what they already say in one shape. It adds no fact, upgrades no provenance
tier, and combines nothing across rows -- `POLICY-evidence` §2.6 forbids pooling and this
module has no pooling operation to forbid.

⚠ SCOPE, STATED HONESTLY. Five adapters cover FOUR committed files and one generic record
shape. They are NOT a corpus-wide reader; the remaining ~700 prose identifiers have no
retained fact anywhere to ingest, which is the finding, not a gap in this module.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import sys
from typing import Any, Iterable, Optional

ROOT = os.environ.get("RARE_CANCERS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Same strip set as research/manuscripts/lint_citations.py. Duplicated deliberately: importing a
#: gate that shells out to `git ls-files` would make this module refuse to run outside a checkout.
TRAILING = ".,;:)]}\"'`*_"

# --------------------------------------------------------------------------------------
# Controlled vocabularies. Each value answers ONE question and none of them is a default.
# --------------------------------------------------------------------------------------

#: What is known about the denominator a numerator is counted out of.
#: ⛔ THERE IS NO ZERO HERE. A denominator that was never printed is UNKNOWN. Coercing it to 0
#: turns "8 patients, out of we-do-not-know-how-many" into a division by zero or, worse, into a
#: rate of 100%. CLOSED-WORK records exactly this hazard for the anthracycline series (median 4
#: cycles, range 1-8, "a separate non-missing denominator is unknown").
DENOMINATOR_STATUSES = ("STATED", "UNKNOWN", "NOT_APPLICABLE")

#: How much of the source this repository actually holds.
#: UNRECOVERED_* rows are FIRST-CLASS. A 403 is an honest unrecovered source and dropping it
#: is how a repository comes to believe it never looked.
ACCESS_STATUSES = (
    "FULL_TEXT",        # retrieved text is held in the tree or the literature cache
    "ABSTRACT_ONLY",    # structured record / abstract retrieved; the paper was not
    "METADATA_ONLY",    # bibliographic identifiers only
    "UNRECOVERED_403",  # a route returned 403 / a bot challenge; access control respected
    "UNRECOVERED_OTHER",
)

#: How strong the evidence behind a claim is. Strictly ordered, weakest last.
PROVENANCE_TIERS = ("FT_QUOTE", "ABSTRACT", "METADATA", "UNCORROBORATED")
_TIER_RANK = {t: i for i, t in enumerate(PROVENANCE_TIERS)}

ID_KINDS = ("PMID", "PMCID", "DOI", "OTHER")


class RetentionError(ValueError):
    """A record that would misstate what is retained. Raised, never silently repaired."""


def _norm_id(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip().rstrip(TRAILING)
    return s or None


def _kind_of(ident: str) -> str:
    if re.fullmatch(r"\d{5,9}", ident):
        return "PMID"
    if ident.upper().startswith("PMC"):
        return "PMCID"
    if ident.startswith("10."):
        return "DOI"
    return "OTHER"


@dataclasses.dataclass(frozen=True)
class RetainedFact:
    """One thing this repository retains about one source. Immutable once built.

    `claim` is what the source says, in this repository's words. `quote` is the source's own
    words and is REQUIRED at tier FT_QUOTE -- a tier that means "we read it" cannot be claimed
    without the text that was read.
    """

    record_id: str
    source_id: str                 # normalised identifier, e.g. "32856598" or "10.1186/s12885-016-2511-y"
    source_id_kind: str
    subject: str                   # what the fact is ABOUT: a drug, a modality, a population
    claim: str
    quote: Optional[str]
    numerator: Optional[float]
    denominator: Optional[float]
    denominator_status: str
    denominator_means: Optional[str]
    access_status: str
    retrieval_date: Optional[str]  # ISO date, or None -- never today's date as a stand-in
    provenance_tier: str
    ingested_from: str             # repository-relative path of the artifact this came from
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if self.denominator_status not in DENOMINATOR_STATUSES:
            raise RetentionError(f"denominator_status {self.denominator_status!r} not in {DENOMINATOR_STATUSES}")
        if self.access_status not in ACCESS_STATUSES:
            raise RetentionError(f"access_status {self.access_status!r} not in {ACCESS_STATUSES}")
        if self.provenance_tier not in PROVENANCE_TIERS:
            raise RetentionError(f"provenance_tier {self.provenance_tier!r} not in {PROVENANCE_TIERS}")
        if self.source_id_kind not in ID_KINDS:
            raise RetentionError(f"source_id_kind {self.source_id_kind!r} not in {ID_KINDS}")

        # ⛔ The invariant this whole module exists for.
        if self.denominator_status == "STATED" and self.denominator is None:
            raise RetentionError("denominator_status STATED with no denominator")
        if self.denominator_status != "STATED" and self.denominator is not None:
            raise RetentionError(
                f"denominator {self.denominator!r} carried under status {self.denominator_status}; "
                "a number that is present is STATED or it is not present")
        if self.provenance_tier == "FT_QUOTE" and not (self.quote or "").strip():
            raise RetentionError("tier FT_QUOTE requires the quoted text it claims to rest on")
        if self.numerator is not None and self.numerator < 0:
            raise RetentionError("negative numerator")

    @property
    def rate(self) -> Optional[float]:
        """numerator/denominator, or None when that division is not licensed.

        ⛔ RETURNS None, NOT 0.0, WHEN THE DENOMINATOR IS UNKNOWN. The caller must handle the
        None; a 0.0 here reads as a measured zero rate and is the exact fabrication this
        repository has already had to correct once.
        """
        if self.denominator_status != "STATED" or self.denominator in (None, 0):
            return None
        if self.numerator is None:
            return None
        return self.numerator / self.denominator

    def to_json(self) -> dict:
        return dataclasses.asdict(self)


# --------------------------------------------------------------------------------------
# Adapters. One per committed shape that actually exists. Each returns RetainedFact rows and
# NEVER drops an input row: an input it cannot express becomes a METADATA/UNKNOWN row with a
# note, because a silently skipped source is indistinguishable from a source nobody had.
# --------------------------------------------------------------------------------------

CARE_DELIVERY = "research/modalities/emc-care-delivery-evidence.json"
TRABECTEDIN = "research/literature/emc-trabectedin-denominator-2026-09-01.json"
LEDGER = "research/manuscripts/citation-provenance-ledger.json"


def _load(root: str, rel: str) -> Any:
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return json.load(fh)


def from_corpus_quotes(doc: dict, rel: str = CARE_DELIVERY) -> list[RetainedFact]:
    """`corpus_quotes[]` -- the only shape in the tree that already pairs a quote with a
    denominator. This adapter is a rename, not an interpretation."""
    out = []
    for i, q in enumerate(doc.get("corpus_quotes") or []):
        ident = _norm_id(q.get("pmid") or q.get("pmcid") or q.get("doi") or q.get("source_id"))
        if ident is None:
            raise RetentionError(f"corpus_quotes[{i}] has no identifier of any kind")
        den = q.get("denominator")
        out.append(RetainedFact(
            record_id=f"CQ-{q.get('source_id') or ident}-{i}",
            source_id=ident, source_id_kind=_kind_of(ident),
            subject=q.get("section") or q.get("corpus") or "unspecified",
            claim=q.get("text", ""),
            quote=q.get("text"),
            numerator=None,
            denominator=float(den) if isinstance(den, (int, float)) else None,
            denominator_status="STATED" if isinstance(den, (int, float)) else "UNKNOWN",
            denominator_means=q.get("denominator_means"),
            access_status="FULL_TEXT",
            retrieval_date=(q.get("read_utc") or "")[:10] or None,
            provenance_tier="FT_QUOTE",
            ingested_from=rel,
            notes=q.get("read_via"),
        ))
    return out


def from_care_delivery_findings(doc: dict, rel: str = CARE_DELIVERY) -> list[RetainedFact]:
    """`findings[]` -- prose `what_it_says` plus a `[API]`/`[FT]` provenance marker.

    ⚠ The numbers inside `what_it_says` (hazard ratios, intervals) are NOT parsed out. Parsing a
    hazard ratio out of a sentence with a regex is how a transcription error enters a structure
    that then looks authoritative. The sentence is retained verbatim as the claim; the tier says
    it came from an abstract."""
    out = []
    for f in doc.get("findings") or []:
        ident = _norm_id(f.get("pmid") or f.get("doi"))
        if ident is None:
            continue
        prov = (f.get("provenance") or "").upper()
        tier = "FT_QUOTE" if "[FT]" in prov else "ABSTRACT"
        access = "FULL_TEXT" if tier == "FT_QUOTE" else "ABSTRACT_ONLY"
        # design carries the series size in prose, e.g. "SEER 1973-2016, n=439 (373 locoregional)".
        # Only a bare, unambiguous `n=<int>` is lifted; anything else stays UNKNOWN.
        m = re.search(r"\bn\s*=\s*(\d+)\b", f.get("design") or "")
        den = float(m.group(1)) if m else None
        out.append(RetainedFact(
            record_id=f"FIND-{f.get('id') or ident}",
            source_id=ident, source_id_kind=_kind_of(ident),
            subject=f.get("route") or "unspecified",
            claim=f.get("what_it_says", ""),
            quote=f.get("what_it_says") if tier == "FT_QUOTE" else None,
            numerator=None,
            denominator=den,
            denominator_status="STATED" if den is not None else "UNKNOWN",
            denominator_means=f.get("design"),
            access_status=access,
            retrieval_date=None,
            provenance_tier=tier,
            ingested_from=rel,
            notes=f.get("why_it_matters"),
        ))
    return out


def from_trabectedin_series(doc: dict, rel: str = TRABECTEDIN) -> list[RetainedFact]:
    """`series[]` -- the one place a numerator and its denominator are BOTH already integers.

    ⛔ EACH SERIES STAYS ITS OWN ROW. The source artifact records `pooled: false` and its reason;
    this adapter has no operation that could pool them."""
    out = []
    for s in doc.get("series") or []:
        ident = _norm_id(s.get("pmid") or s.get("doi") or s.get("pmcid"))
        if ident is None:
            continue
        num = s.get("emc_objective_responses")
        den = s.get("emc_n")
        has_den = isinstance(den, (int, float))
        out.append(RetainedFact(
            record_id=f"TRAB-{s.get('key') or ident}",
            source_id=ident, source_id_kind=_kind_of(ident),
            subject="trabectedin",
            claim=(f"{num} objective response(s) among {den if has_den else 'an unstated number of'} "
                   f"located EMC patients. Best response: {s.get('emc_best_response') or 'not stated'}."),
            quote=None,
            numerator=float(num) if isinstance(num, (int, float)) else None,
            denominator=float(den) if has_den else None,
            denominator_status="STATED" if has_den else "UNKNOWN",
            denominator_means=s.get("arm_composition") or s.get("design"),
            access_status="ABSTRACT_ONLY",
            retrieval_date=(doc.get("date_utc") or "")[:10] or None,
            provenance_tier="ABSTRACT",
            ingested_from=rel,
            notes=s.get("design"),
        ))
    return out


def from_ledger(doc: dict, rel: str = LEDGER) -> list[RetainedFact]:
    """`entries[]` -- an identifier that NOTHING in this repository corroborates.

    These are the honest floor of the structure: a row here asserts no fact at all. It exists so
    that "we retain nothing about X" is a queryable answer rather than an absence of rows."""
    out = []
    for e in doc.get("entries") or []:
        ident = _norm_id(e.get("id"))
        if ident is None:
            continue
        out.append(RetainedFact(
            record_id=f"LEDGER-{e.get('key') or ident}",
            source_id=ident, source_id_kind=e.get("kind") if e.get("kind") in ID_KINDS else _kind_of(ident),
            subject="unassigned",
            claim="No retained content. This identifier appears in prose and no fetch, curation or "
                  "graph record in this repository corroborates it.",
            quote=None, numerator=None, denominator=None,
            denominator_status="NOT_APPLICABLE", denominator_means=None,
            access_status="METADATA_ONLY",
            retrieval_date=None,
            provenance_tier="UNCORROBORATED",
            ingested_from=rel,
            notes=f"ledger status: {e.get('status')}",
        ))
    return out


def from_fetch_records(doc: Any, rel: str) -> list[RetainedFact]:
    """Any `{url, attempts[], status}` fetch record, wherever it is nested.

    ⛔ A FAILED FETCH PRODUCES A ROW. That is the entire point of this adapter: a 403 is a
    retained fact -- "this route was tried on this date and refused" -- and CLOSED-WORK depends
    on it to stop unchanged denied-route replays."""
    out = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            if "url" in node and "status" in node and isinstance(node.get("attempts"), list):
                st = node.get("status")
                ok = isinstance(st, int) and 200 <= st < 300
                access = ("FULL_TEXT" if ok else
                          "UNRECOVERED_403" if st == 403 else "UNRECOVERED_OTHER")
                out.append(RetainedFact(
                    record_id=f"FETCH-{rel}:{path}",
                    source_id=str(node["url"]), source_id_kind="OTHER",
                    subject="route access",
                    claim=f"HTTP {st if st is not None else 'no status (every attempt errored)'} "
                          f"after {len(node['attempts'])} attempt(s).",
                    quote=None, numerator=None, denominator=None,
                    denominator_status="NOT_APPLICABLE", denominator_means=None,
                    access_status=access, retrieval_date=None,
                    provenance_tier="METADATA", ingested_from=rel,
                    notes=node.get("note"),
                ))
                return
            for k, v in node.items():
                walk(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(doc, "")
    return out


ADAPTERS = (
    (CARE_DELIVERY, from_corpus_quotes),
    (CARE_DELIVERY, from_care_delivery_findings),
    (TRABECTEDIN, from_trabectedin_series),
    (LEDGER, from_ledger),
)


def ingest(root: str = ROOT, extra_fetch_files: Iterable[str] = ()) -> list[RetainedFact]:
    facts: list[RetainedFact] = []
    for rel, fn in ADAPTERS:
        facts.extend(fn(_load(root, rel), rel))
    for rel in extra_fetch_files:
        facts.extend(from_fetch_records(_load(root, rel), rel))
    return facts


def by_subject(facts: Iterable[RetainedFact], subject: str) -> list[RetainedFact]:
    """"What do we actually retain about X" -- substring, case-insensitive, over subject+claim.

    Returns strongest tier first so a reader sees the quoted evidence before the uncorroborated
    identifier, and never has to infer which is which."""
    q = subject.lower()
    hits = [f for f in facts if q in f.subject.lower() or q in f.claim.lower()]
    return sorted(hits, key=lambda f: (_TIER_RANK[f.provenance_tier], f.source_id))


def summarise(facts: Iterable[RetainedFact]) -> dict:
    facts = list(facts)
    def count(attr, vocab):
        return {v: sum(1 for f in facts if getattr(f, attr) == v) for v in vocab}
    return {
        "n_records": len(facts),
        "n_distinct_sources": len({f.source_id for f in facts}),
        "by_provenance_tier": count("provenance_tier", PROVENANCE_TIERS),
        "by_denominator_status": count("denominator_status", DENOMINATOR_STATUSES),
        "by_access_status": count("access_status", ACCESS_STATUSES),
        "n_with_computable_rate": sum(1 for f in facts if f.rate is not None),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--fetch-file", action="append", default=[],
                    help="extra repository-relative .json to scan for {url,attempts,status} records")
    ap.add_argument("--subject", help='query: "what do we retain about X"')
    ap.add_argument("--json", action="store_true", help="emit the normalised records")
    a = ap.parse_args(argv)
    facts = ingest(a.root, a.fetch_file)
    if a.subject:
        facts = by_subject(facts, a.subject)
    if a.json:
        json.dump([f.to_json() for f in facts], sys.stdout, indent=1)
        print()
    else:
        json.dump(summarise(facts), sys.stdout, indent=1)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Proposed path `research/manuscripts/tests/test_retained_facts.py`:

```python
#!/usr/bin/env python3
"""Behaviour tests for retained_facts.

Each test names a way this module could silently misstate what the repository retains, and
fails if it does. None of them pins a sentence, a file length or a count that a legitimate
edit would move.
"""
import json
import os
import unittest

import retained_facts as rf

ROOT = os.environ.get("RARE_CANCERS_ROOT", "/home/user/Rare-cancers")


def _fact(**kw):
    base = dict(record_id="R", source_id="1", source_id_kind="PMID", subject="s", claim="c",
                quote=None, numerator=None, denominator=None, denominator_status="NOT_APPLICABLE",
                denominator_means=None, access_status="METADATA_ONLY", retrieval_date=None,
                provenance_tier="METADATA", ingested_from="x.json")
    base.update(kw)
    return rf.RetainedFact(**base)


class MissingDenominatorIsNeverZero(unittest.TestCase):
    """The anthracycline hazard: median 4 cycles, range 1-8, denominator unknown."""

    def test_unknown_denominator_stays_None(self):
        f = _fact(numerator=1.0, denominator=None, denominator_status="UNKNOWN")
        self.assertIsNone(f.denominator)
        self.assertNotEqual(f.denominator, 0)

    def test_rate_is_None_not_zero_when_denominator_unknown(self):
        f = _fact(numerator=1.0, denominator=None, denominator_status="UNKNOWN")
        self.assertIsNone(f.rate, "an unknown denominator must not yield a numeric rate")

    def test_STATED_without_a_number_is_rejected(self):
        with self.assertRaises(rf.RetentionError):
            _fact(denominator=None, denominator_status="STATED")

    def test_a_number_cannot_hide_under_UNKNOWN(self):
        with self.assertRaises(rf.RetentionError):
            _fact(denominator=29.0, denominator_status="UNKNOWN")

    def test_zero_denominator_does_not_divide(self):
        f = _fact(numerator=3.0, denominator=0.0, denominator_status="STATED")
        self.assertIsNone(f.rate)

    def test_stated_denominator_does_divide(self):
        f = _fact(numerator=8.0, denominator=29.0, denominator_status="STATED")
        self.assertAlmostEqual(f.rate, 8 / 29)


class UnrecoveredSourcesAreRetained(unittest.TestCase):
    """A 403 is an honest unrecovered source, not a row to drop."""

    DOC = {"a": {"url": "https://example.org/x", "attempts": [{"n": 1, "status": 403}],
                 "status": 403, "note": "bot challenge"},
           "b": {"url": "https://example.org/y", "attempts": [{"n": 1, "status": 200}],
                 "status": 200},
           "c": {"url": "https://example.org/z", "attempts": [{"n": 1}], "status": None}}

    def test_403_produces_a_record(self):
        got = rf.from_fetch_records(self.DOC, "t.json")
        self.assertEqual(len(got), 3, "no fetch record may be dropped, whatever its status")
        by_url = {f.source_id: f for f in got}
        self.assertEqual(by_url["https://example.org/x"].access_status, "UNRECOVERED_403")

    def test_success_and_failure_are_distinguishable(self):
        by_url = {f.source_id: f for f in rf.from_fetch_records(self.DOC, "t.json")}
        self.assertEqual(by_url["https://example.org/y"].access_status, "FULL_TEXT")
        self.assertEqual(by_url["https://example.org/z"].access_status, "UNRECOVERED_OTHER")

    def test_a_null_status_is_not_read_as_a_success(self):
        by_url = {f.source_id: f for f in rf.from_fetch_records(self.DOC, "t.json")}
        self.assertNotEqual(by_url["https://example.org/z"].access_status, "FULL_TEXT")


class TierDisciplineHolds(unittest.TestCase):
    def test_FT_QUOTE_requires_a_quote(self):
        with self.assertRaises(rf.RetentionError):
            _fact(provenance_tier="FT_QUOTE", quote=None)
        with self.assertRaises(rf.RetentionError):
            _fact(provenance_tier="FT_QUOTE", quote="   ")

    def test_bad_vocabulary_is_rejected_not_defaulted(self):
        for kw in ({"denominator_status": "MISSING"}, {"access_status": "OK"},
                   {"provenance_tier": "GOOD"}):
            with self.assertRaises(rf.RetentionError):
                _fact(**kw)

    def test_query_orders_evidence_before_assertion(self):
        facts = [_fact(record_id="w", provenance_tier="UNCORROBORATED", subject="drugX"),
                 _fact(record_id="s", provenance_tier="FT_QUOTE", quote="q", subject="drugX")]
        self.assertEqual([f.record_id for f in rf.by_subject(facts, "drugx")], ["s", "w"])


class AdaptersReadTheRealCommittedFiles(unittest.TestCase):
    """Runs against the tree, not fixtures. Fails if an artifact's shape changes underneath."""

    @classmethod
    def setUpClass(cls):
        if not os.path.isdir(ROOT):
            raise unittest.SkipTest(f"repository not present at {ROOT}")
        cls.facts = rf.ingest(ROOT)

    def test_every_ingested_row_satisfies_the_invariants(self):
        # Construction validates; reaching here at all means no row violated them.
        self.assertGreater(len(self.facts), 0)

    def test_the_two_trabectedin_series_stay_two_rows(self):
        trab = [f for f in self.facts if f.record_id.startswith("TRAB-")]
        self.assertEqual(len(trab), 2)
        self.assertEqual({f.numerator for f in trab}, {0.0},
                         "0 located objective responses, per the source artifact")
        self.assertEqual(sorted(f.denominator for f in trab), [2.0, 3.0],
                         "denominators stay separate; POLICY-evidence forbids pooling")

    def test_ledger_rows_assert_no_fact(self):
        led = [f for f in self.facts if f.record_id.startswith("LEDGER-")]
        self.assertGreater(len(led), 100)
        self.assertTrue(all(f.provenance_tier == "UNCORROBORATED" for f in led))
        self.assertTrue(all(f.numerator is None and f.denominator is None for f in led))

    def test_the_one_full_text_quote_carries_its_denominator(self):
        cq = [f for f in self.facts if f.record_id.startswith("CQ-")]
        self.assertEqual(len(cq), 1, "if this changes, a second quote was retained -- good, update me")
        self.assertEqual(cq[0].provenance_tier, "FT_QUOTE")
        self.assertTrue(cq[0].quote)
        self.assertEqual(cq[0].denominator_status, "STATED")

    def test_records_round_trip_through_json(self):
        blob = json.dumps([f.to_json() for f in self.facts])
        back = json.loads(blob)
        self.assertEqual(len(back), len(self.facts))
        rebuilt = rf.RetainedFact(**back[0])
        self.assertEqual(rebuilt, self.facts[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## Validation evidence

**RUN.** Environment: `Python 3.11.15`, Linux, no network, cwd `/tmp/claude-0/w15/pkg`, repository read-only at `92abbcb`.

1. Gap measurement — output in R2. `EXIT=0`.
2. Ingester on real committed inputs — output in R3. `EXIT=0`.
3. Subject query — output in R3. `EXIT=0`.
4. Test suite:
```
$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 -m unittest test_retained_facts -v
... 17 tests, all ok ...
Ran 17 tests in 0.008s
OK
EXIT=0
```
5. **Mutation check — proof the tests are not vacuous.** I copied the module to `/tmp/claude-0/w15/mut/`, injected two defects (`rate` coerces an unknown denominator to `0.0` and returns `0.0`; `from_fetch_records` drops every non-2xx record), and re-ran the unchanged suite:
```
$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 -m unittest test_retained_facts
FAIL: test_403_produces_a_record ... AssertionError: 1 != 3 : no fetch record may be dropped, whatever its status
Ran 17 tests in 0.007s
FAILED (failures=3, errors=2)
EXIT=1
```
Both target defects are caught. The mutated copy was discarded; the clean module is what is returned above.

6. Tree unchanged: `git status --porcelain` → only the pre-existing untracked campaign directory; `HEAD=92abbcb905cacf07f14b238db50d1b98f6590374`.

**PROPOSED (NOT RUN).** `scripts/preflight.sh` — the brief forbids running it. A JSON Schema file (`systems/schema/retained-fact.schema.json`) mirroring the vocabularies. Adapters for the remaining literature artifacts. Integration into an existing test tier.

## Limitations

- **Coverage, stated exactly.** The ingester reads **three committed files by name** (`emc-care-delivery-evidence.json`, `emc-trabectedin-denominator-2026-09-01.json`, `citation-provenance-ledger.json`) plus any file passed with `--fetch-file` for the generic `{url, attempts, status}` shape. It is **not** a corpus-wide reader. Of 908 prose identifiers it produces content-bearing rows for **7**. The other ~901 are not a defect in the module — for most of them there is no retained fact anywhere to ingest.
- **Re-expression, not retrieval.** Every row restates a committed artifact. No fact, number, quote or provenance tier is created, upgraded, or inferred. I retrieved nothing over the network.
- **Numbers inside prose are deliberately not parsed.** `what_it_says` sentences retain hazard ratios and intervals as text. Only a bare unambiguous `n=<int>` in `design` is lifted. Regex-extracting a hazard ratio from a sentence would manufacture false precision.
- **The 6 "STATED" denominators are small and source-specific** (2, 3, 29, and `n=` values from SEER-based abstracts). They license no rate beyond their own row. `n_with_computable_rate: 2`, both zero-numerator.
- **This establishes nothing clinical.** It is a data-structure change. It cannot bear on EMC efficacy, safety, selectivity or readiness, and it does not create a cohort, a patient or a denominator that did not already exist in a committed artifact.
- **Two structural risks I did not close.** `TRAILING` is duplicated from `lint_citations.py` rather than imported (importing pulls in a `git ls-files` subprocess); if that set changes, the two can drift. And `record_id` uniqueness is not enforced — two adapters could in principle collide.
- The single `CQ-` count-of-1 assertion is the one test that a legitimate future edit will trip; its failure message says so and says the correct response is to update it, not to weaken it.

## Stop condition

**Set:** a measured retention gap, plus scoped ingestion code with executed tests and real exit evidence.

**MET.** Gap measured (908 prose identifiers vs 7 with retained content; the "identifiers are lost" hypothesis measured **false** and reported as such). Module written, run against real committed inputs at exit 0. 17 tests run at exit 0, and shown non-vacuous by a mutation run at exit 1.

## Tool-call and wall-clock count actually used

18 tool calls (target ~40). Wall clock 01:55:31Z → 02:01:17Z ≈ **6 minutes** (target ~40). No padding; returning on the stop condition.

## Next concrete action

**Write the JSON Schema `systems/schema/retained-fact.schema.json` mirroring the three vocabularies, and add a fifth adapter for `research/literature/emc-clinical-sweep-fulltext.json`** — chosen because "fulltext" in the name means it is the highest-probability source of a *second* `FT_QUOTE`-tier record, and the corpus currently has exactly one. That single number (does a second full-text quote exist in the tree?) is the cheapest measurement of whether the retention gap is a tooling gap or a genuine evidence gap, and it needs no network access.

result: Measured the EMC repository's retention gap at commit 92abbcb — 908 distinct PMID/DOI/PMCID in prose, 0 missing from structure (the obvious hypothesis is false), but only 7 with any machine-readable retained fact and exactly 1 tracked JSON file pairing a quote with a denominator — and delivered a scoped normalisation module (RetainedFact schema + 5 adapters + subject query) that ran on real committed inputs at exit 0 with 17/17 tests passing at exit 0 and a mutation run failing at exit 1.
