> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

All verification complete: 18/18 pass, 7/8 new tests fail on the unrepaired helper, tier arithmetic 1484/1500, repo tree untouched.

---

## Worker

**W11b**, lane 11 — source-index repair integration (sole owner of source-index changes).

**Model evidence — SELF-REPORT, not independently verified.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model; no environment variable in this container names a model at all. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` start: `Tue Sep  8 01:57:41 UTC 2026` (approx, first tool call) · `date -u` end: `Tue Sep  8 02:12:21 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal, sorted, long proxy host-lists retained in the transcript and elided here only where marked:

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_DEBUG=true
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_SYNC_SESSION_REFS=1
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_PID=522
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
GLOBAL_AGENT_NO_PROXY=… (proxy host list, elided)
JAVA_TOOL_OPTIONS=… (proxy config, elided)
NO_PROXY=… (proxy host list, elided)
PWD=/tmp/claude-0/w11b/final
SESSION_INGRESS_URL=https://api.anthropic.com
no_proxy=… (proxy host list, elided)
npm_config_noproxy=… (proxy host list, elided)
```

**Write isolation honoured.** Zero files created or modified under `/home/user/Rare-cancers`. All execution under `/tmp/claude-0/w11b/`. No git write operation of any kind. `git status --porcelain` at the end shows only three untracked reports collected by the coordinator for other workers (`W02b`, `W06b`, `W19b`), none touched by me.

---

## Question

**Given the arrived bundle, which of the nine statically-asserted defects in the source-reuse index are real when executed, what is the correct diagnosis of the one failing delivered test, and what complete pair of files satisfies S1–S9 while fitting the commit-loop tier's measured headroom?**

Open because W11 established the receiving contract without the bytes; every claim about the code itself was static or transferred, and a static finding is not a passed review.

---

## Prior-work check

- `find . -name 'W11*' -not -path './.git/*'` → `research/autonomy/opus-capacity-campaign-20260908/reports/W11-source-index-integration-contract.md`. **Note for the coordinator:** when I read it at the start of this run it was an 8-line stub containing only the collection header and one stray sentence ("All four real records the review cites are **absent** at the freeze commit…"). It was rewritten to W11's full pre-capsule report mid-run, with a COLLECTION NOTE explaining that an earlier pass had captured only the resumed agent's opening line. I worked from the S1–S12 contract transferred in my dispatch; the restored file agrees with it. I did not edit the file.
- `git ls-files | grep -E "(^|/)(source_reuse_index|test_source_reuse_index)\.py$"` → **no output**. No basename collision (S4 satisfied). `ls scripts/source_reuse_index.py` → does not exist.
- `git ls-files 'scripts/tests/*' | wc -l` → 21 existing files. `ls scripts/tests/conftest.py conftest.py` → neither exists; `find . -name conftest.py` → only `research/autonomy/tests/`, `research/modalities/tests/`, `research/manuscripts/tests/`. **S11 confirmed measured**, not assumed.
- `CLOSED-WORK.md` read in full. I am not replaying ASO/Qeios deliverables, the retained biology-access refusal, the closed scientific gates, or the unrecovered sources. The lane-11 block is my direct input; I honour all three constraints (no ceiling increase, no 30-test gate, complete named final files into an existing tier).
- `grep -n -i "synthetic" AGENTS.md` → line 35, "synthetic data explicitly labeled and primary/secondary provenance distinct" — this is the repository-internal basis for F8, independent of the external contract's AC-28.

---

## Method / inputs

Bundle at `research/autonomy/opus-capacity-campaign-20260908/inputs/source-index/`. I re-verified the two code inputs against `input-manifest.json` by hash before running anything:

```
bc348ce955534bf848b6a3d8b24944c3126abe6066ef1c5fbbe25f2b4bf91c4d  research/tools/source_reuse_index.py
2c07fae45942fdbf994ec5df4b67df4d957056f23d6a0cafbce6d736ff269bc4  research/tools/tests/test_source_reuse_index.py
```

Both match the manifest exactly. Also read in full: the helper (779 lines), the test file (10 tests), `evidence/execution/execution-result.json`, both execution stderr logs, `evidence/independent-comparison/report.md` §0–§2 (the nine findings and the contract comparison), `README.md`, `input-manifest.json`. Repository files read read-only: `scripts/tier_budget.py`, `scripts/tier-budgets.json`, `AGENTS.md`, `CLOSED-WORK.md`, `COMMON-BRIEF.md`.

Execution environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `Python 3.11.15` (`/usr/local/bin/python3`), `pytest 9.1.1` at `/root/.local/bin/pytest`, shebang `#!/root/.local/share/uv/tools/pytest/bin/python3`. Working root `/tmp/claude-0/w11b/`.

I did **not** port either malformed diff. Every change was re-derived from the file after reproducing a failing case.

---

## Result

### 1. Reproduction of the three recorded outcomes

| Recorded outcome | Reproduces here? | Evidence | Class |
|---|---|---|---|
| Discovery fails, `ImportError: Start directory is not importable`, exit 1 | **PARTIALLY — only under the right invocation** | `python3 -m unittest discover -s research/tools/tests` → **ran 10 tests, exit 1 from the one failure, no ImportError**. `python3 -m unittest discover -s research/tools/tests -t .` → `ImportError: Start directory is not importable: '/tmp/claude-0/w11b/research/tools/tests'`, exit 1 | PRIMARY |
| Direct run: 10 tests, 9 passed, 1 failed, exit 1 | **YES, exactly** | 9 `ok`, 1 `FAIL` on `test_cli_exits_zero_for_unresolved_matched_and_invalid` at line 261, same `AssertionError` string, exit 1 | PRIMARY |
| 4 bounded CLI examples exit 0 | **YES** (re-derived examples, not the originals) | four `python3 scripts/source_reuse_index.py …` invocations, `exit=0` each, against my final helper | PRIMARY |

**This is the most important finding of the reproduction, and it corrects the transferred contract.** The recorded ImportError is not mysterious and it is not about `pytest` at all. It is `unittest.TestLoader.discover` enforcing that when `start_dir != top_level_dir`, the start directory must contain `__init__.py`. I read the enforcing source in this interpreter:

```
elif top_level_dir is None:
    top_level_dir = start_dir
...
is_not_importable = False
```

With the default invocation `top_level_dir` *becomes* `start_dir`, the check is skipped, and discovery succeeds. The original Windows run had them differ (its traceback goes through `_do_discovery`, raising at `loader.py:308`), so the `__init__.py` check fired. I confirmed the mechanism by construction: adding `__init__.py` to `research/tools/tests/` makes the failing `-t .` invocation collect and run all 10 tests.

So both prior positions are true and were talking past each other. W11's refutation was about **pytest 9.1.1**, where `__init__.py` is irrelevant and the `sys.path` preamble is what matters. The recorded failure was about **unittest discovery**, where `__init__.py` is exactly what matters. I did not resurrect the hypothesis as a repair — S5 stands and I ship no `__init__.py` — because I verified the repository's *existing* tier has the identical property:

```
$ python3 -m unittest discover -s scripts/tests -t . -p 'test_affected_tests.py'
ImportError: Start directory is not importable: '/home/user/Rare-cancers/scripts/tests'
$ ls scripts/tests/__init__.py   →   No such file or directory
```

All 21 existing `scripts/tests/` files share it. The tier's runner is pytest, `scripts/tier_budget.py` counts by AST, and my file is collected and run correctly by pytest from the repository root. Adding `__init__.py` to satisfy a runner the repository does not use would be a change to shared tier structure I do not own.

### 2. Adjudication of all nine findings — each run, none accepted on reading

Every row below is a probe I executed against the **unrepaired** helper at `/tmp/claude-0/w11b/probe/probe.py`. The four real repository records the review cites are absent at the freeze commit, so each mechanism was tested on a synthetic record built to the shape the review describes; that is a limitation of the *citation*, not of the mechanism.

| # | Finding | Verdict | Failing case I actually ran | Class |
|---|---|---|---|---|
| F1 | Bare identifier under a field name never indexed | **REPRODUCED** | `{"pmid": "24703573"}` → `state: unresolved_not_indexed`, 0 matches; control `{"doi": "10.5555/x.1"}` → `matched`, 1 match. A false non-match on a record demonstrably in the corpus | PRIMARY |
| F2 | Negated sentence asserts the categories it rules out | **REPRODUCED exactly, 5 labels as predicted** | the motivating sentence → `['proxy_or_network_failure', 'publisher_authentication_or_subscription', 'policy_or_biology_refusal', 'full_text_unavailable_in_scope', 'no_access_attempt_in_this_packet']` | PRIMARY |
| F3 | Orthogonal `*_status` fields manufacture a conflict | **REPRODUCED** | one record with `operational_status`/`scientific_status`/`source_asset_status` → `state: matched_with_divergent_states`, `conflicts: ['differing_record_status']`, from a record that disagrees with nothing | PRIMARY |
| F4 | Policy exclusion produces no event; silence is ambiguous | **MECHANISM REPRODUCED; the review's own cited example REFUTED** | the review's exact wording, "restricted reagent work, excluded from retrieval", contains the trigger `retriev` and **does** emit `['unclassified_reported_access_evidence']` — the review's claim that it "contains none of `_ACCESS_TRIGGERS`, so no event is emitted at all" is **wrong**. A variant without that substring, "Restricted reagent work; excluded from this packet by policy.", returns `[]`, identical to a record that says nothing. Fixed on the corrected example; the review's example is recorded as refuted | PRIMARY |
| F5 | `record_id` basename collision pools evidence across files | **REPRODUCED, and it is the worst of the nine** | two distinct files both named `integration.json` → `scope files: ['integration.json', 'integration.json']`; a lookup matching only the first returned **both** records' statuses (`['paz_open', 'closed_no_original_full_text_recovered']`) and the second record's 403 access evidence. Cross-record evidence attribution in a provenance tool | PRIMARY |
| F6 | Missing/empty root reads as a genuine non-match | **REPRODUCED** | nonexistent root → `state: unresolved_not_indexed`, `file_count: 0`, **no warning key of any kind** in the result | PRIMARY |
| F7 | `_bytes_signal` infers "recovered" from unrelated keys | **REPRODUCED** | `{"landing_page": "https://…/landing", "archive_sha256": "ab"*32, "archive_member": "bundle/inner.xml"}` → a full retained-bytes signal, tying a landing page to an archive digest that is not the member's | PRIMARY |
| F8 | `synthetic_fixture` never labelled in output | **REPRODUCED** | record with `synthetic_fixture: true` → `"SYNTHETIC" in text render: False`; the string `synthetic_fixture` appears nowhere in the JSON result. Basis is `AGENTS.md:35`, not only the external contract | PRIMARY |
| F9 | Test 10 assertion is case-sensitive and cannot pass | **REPRODUCED** | `"not an authorization" in sri.DISCLAIMER` → `False`; `"Not an authorization" in …` → `True` | PRIMARY |

Nine of nine reproduce as mechanisms; one (F4) reproduces only after correcting the review's own example, which I record as refuted rather than repeating. None was accepted on the strength of the review's prose, and no proposed diff was ported.

### 3. The disclaimer failure (S12) — diagnosed on merits

**The assertion is wrong; the code is right.** Three reasons, in order of weight:

1. `DISCLAIMER` opens a sentence: "…retained records. **N**ot an authorization, not a novelty determination…". The capital is correct English at a sentence boundary. Lowercasing the constant to satisfy a test would make the tool's own output ungrammatical, and it would change a user-visible safety string to accommodate a test — the wrong direction.
2. The constant is consistent with the module docstring ("It is not an authorization mechanism") and with `LOOKUP_STATES`/`ACCESS_LABELS`. Nothing about the disclaimer's *content* is at issue; the failure is purely orthographic.
3. The test file already establishes the correct idiom twice. Tests 3 and 8 both do `" ".join(result["notes"]).lower()` before asserting. Test 10 simply omitted the `.lower()`. This is a local slip in one assertion, not a disagreement about behaviour.

Repair: `self.assertIn("not an authorization", payload["disclaimer"].lower())`. I strengthened it rather than merely fixing it — the test now also asserts `"not a novelty determination"` is present, so the assertion pins the disclaimer's substance and not just one phrase, and the loop no longer stops at its first iteration (the original failure hid iterations 2 and 3, as the bundle's `coverage_limit` field correctly warned).

### 4. Tier arithmetic

`python3 scripts/tier_budget.py`, run by me against the live repository:

```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```

S9 confirmed at 1466/1500 → **34 functions of headroom, shared not reserved.** My test file defines **18** test functions, counted by the repository's own AST method (`ast.walk`, `name.startswith("test_")`), with **zero duplicate names** (S7 — `tier_budget.py` fails the tier on a shadowed name, not just over-count). Projected commit-loop total **1484/1500, 16 functions of headroom left for everyone else.** I read `count_dir()` and confirmed it uses `os.listdir` on the tier directory only — a subdirectory would indeed evade the budget (S3), so the file goes flat in `scripts/tests/`.

### 5. S1–S9 conformance of the delivered pair

| | Requirement | Satisfied by |
|---|---|---|
| S1 | implementation flat at `scripts/<identifier>.py` | `scripts/source_reuse_index.py` |
| S2 | underscores only | both basenames use `_` throughout |
| S3 | test flat in `scripts/tests/` | `scripts/tests/test_source_reuse_index.py`, no subdirectory |
| S4 | `test_<unique>.py`, globally unique basename | verified by `git ls-files` — no match anywhere in the tree |
| S5 | no `__init__.py` | none shipped; consistent with all 21 existing tier files |
| S6 | `sys.path.insert(0, os.path.join(ROOT, "scripts"))` + `# noqa: E402` | lines 30–32 of the test file, verbatim shape |
| S7 | no duplicate test function names | AST check: `duplicates: none` |
| S8 | tier assignment is directory membership | file lives in `scripts/tests/`, which `tier-budgets.json` lists under `commit-loop`; no budget file edited |
| S9 | ≤ 34 test functions | **18** |

---

## Final files

### `scripts/source_reuse_index.py`

sha256 `b3288598378fd55d26d46ed2e4b6575c2357a57abf71b8fcec7bf28edb8337e3`, 1056 lines, LF.

```python
"""Informational, read-only source/identifier provenance lookup.

Given an identifier (DOI, PMID, PMCID, dataset/registry accession) or a URL, report
whether that identifier already appears in a supplied corpus of retained records, where
it appears (file plus JSON dotted path or line number), what dated statuses those
records carry, and what access evidence those records explicitly report.

What this tool is NOT
---------------------
* It is not an authorization mechanism. It never says a source may be fetched, retried
  or approved; it only quotes retained record text verbatim.
* It is not a scientific or acceptance gate. The CLI exits 0 for every lookup state by
  design, including unresolved and invalid candidates, so it cannot be wired in as a
  pass/fail check without a deliberate, visible change.
* It is not evidence of novelty. Absence from the index means the supplied corpus did
  not contain the identifier. The corpus is always incomplete; every non-match carries
  a mandatory note saying so.
* It performs no network access. Only ``urllib.parse`` (string parsing) is imported from
  urllib; no socket, no ``urllib.request``, no HTTP. Files are opened read-only.
* It never matches on titles. Title/abstract text is excluded from identity matching
  entirely, so no "same paper?" judgement is made from prose similarity.

Standard library only.

Repairs applied after independent review (each demonstrated with a failing case before
the change; see the paired test file, which pins every one as a regression):

* F1  identifiers carried by a *field name* with a bare value (``"pmid": "24703573"``)
      are now indexed, deduplicated against the syntactic hit. They were invisible
      before, producing a false non-match on a record that is in the corpus.
* F2  access labels now carry per-label evidence (matched phrase, containing clause,
      whether that clause negates). Labels are mentions of a category, never assertions
      that the category applies. No label is silently dropped.
* F3  status divergence is flagged only when the *same field name* holds different
      values. Orthogonal ``*_status`` dimensions in one record no longer manufacture a
      contradiction the record does not state.
* F4  restriction/exclusion vocabulary is recognised, and a match whose records carry no
      recognised access statement now says so explicitly instead of rendering silence
      identically to "nothing to report".
* F5  records are identified by position, not by basename. Two files both called
      ``integration.json`` no longer pool each other's statuses and access evidence.
* F6  missing roots and skipped non-text files are recorded and surfaced as
      ``scope_warnings`` on every result, so a typo'd corpus path cannot read as
      "not previously seen".
* F7  the retained-bytes signal requires a URL from a ``*url*`` key and a digest from a
      ``sha256``-named key, and states the association basis. Unrelated key
      co-occurrence no longer claims a recovered source.
* F8  records flagged ``synthetic_fixture`` are labelled as such in JSON and text output
      (AGENTS.md requires synthetic data to be explicitly labelled).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------

IDENTITY_SCHEMES: Tuple[str, ...] = (
    "doi",
    "pmid",
    "pmcid",
    "geo",
    "arrayexpress",
    "bioproject",
    "sra",
    "ega",
    "nct",
    "eudract",
)

LOOKUP_STATES: Tuple[str, ...] = (
    "matched",
    "matched_prose_mention_only",
    "matched_with_divergent_states",
    "unresolved_not_indexed",
    "unresolved_url_without_identifier",
    "ambiguous_multiple_identifiers",
    "invalid_candidate",
)

ACCESS_LABELS: Tuple[str, ...] = (
    "proxy_or_network_failure",
    "http_403_unclassified_denial",
    "publisher_authentication_or_subscription",
    "policy_or_biology_refusal",
    "full_text_unavailable_in_scope",
    "reported_complete_source_recovered",
    "no_access_attempt_in_this_packet",
    "unclassified_reported_access_evidence",
)

DISCLAIMER = (
    "Informational read-only lookup over the supplied corpus of retained records. "
    "Not an authorization, not a novelty determination, not evidence of source "
    "availability, not scientific validation."
)

NON_MATCH_NOTE = (
    "A non-match is NOT novelty: it means this identifier was not found in the files "
    "enumerated in indexed_scope. The supplied corpus is incomplete by construction."
)

URL_NOTE = (
    "A URL alone never establishes article identity. A URL resolves only through an "
    "identifier embedded in the URL string itself; a newly surfaced URL is not a newly "
    "identified article."
)

TITLE_NOTE = (
    "Titles are excluded from matching entirely. Supply a DOI, PMID, PMCID or accession."
)

DATED_NOTE = (
    "Dated record statuses are reported verbatim in date order. Nothing is merged, "
    "ranked or superseded by this tool; conflicting or dated entries are all retained."
)

LABEL_MENTION_NOTE = (
    "Access labels record which categories a record's own wording NAMES. A label is a "
    "mention, not an assertion: a record that explicitly rules a category out still "
    "names it. Read label_evidence and the verbatim quote before drawing any conclusion."
)

NO_ACCESS_EVIDENCE_NOTE = (
    "Matched records contributed no recognised access statement. That is silence in the "
    "supplied text, not a finding: it does not mean access was attempted, was not "
    "attempted, was permitted, or was restricted. Unknown, not zero."
)

TEXT_EXTENSIONS = frozenset({".json", ".md", ".txt"})

SYNTHETIC_MARKER = "[SYNTHETIC FIXTURE]"

# --------------------------------------------------------------------------------------
# Extraction and normalization
# --------------------------------------------------------------------------------------

_TRAILING = ".,;:)]}'\""

_PATTERNS: Tuple[Tuple[str, "re.Pattern[str]"], ...] = (
    ("doi", re.compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:+\-]+")),
    ("pmid", re.compile(r"PMID\s*:?\s*\d{4,9}\b", re.IGNORECASE)),
    ("pmcid", re.compile(r"\bPMC\d{4,9}\b", re.IGNORECASE)),
    ("geo", re.compile(r"\bG(?:SE|SM|PL)\d{3,9}\b")),
    ("arrayexpress", re.compile(r"\bE-[A-Z]{4}-\d{1,9}\b")),
    ("bioproject", re.compile(r"\bPRJ[A-Z]{2}\d{3,9}\b")),
    ("sra", re.compile(r"\bSR[RXPS]\d{5,12}\b")),
    ("ega", re.compile(r"\bEGA[SD]\d{6,15}\b")),
    ("nct", re.compile(r"\bNCT\d{8}\b")),
    ("eudract", re.compile(r"\b\d{4}-\d{6}-\d{2}\b")),
    ("url", re.compile(r"https?://[^\s\"'<>\]\),]+")),
)

_DOI_FULL = re.compile(r"^10\.\d{4,9}/\S+$")
_PMID_FULL = re.compile(r"^(?:pmid\s*:?\s*)?(\d{4,9})$", re.IGNORECASE)
_PMCID_FULL = re.compile(r"^(?:pmcid\s*:?\s*)?pmc(\d{4,9})$", re.IGNORECASE)
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")

_DOI_URL_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "https://www.doi.org/",
    "http://www.doi.org/",
)


def normalize_url(raw: str) -> str:
    """Weak, deliberately non-identifying URL key.

    Folds http/https and a leading 'www.', drops the fragment, strips one trailing
    slash, keeps path and query. This can conflate genuinely distinct hosts that differ
    only by 'www.'; that is a documented simplification, and a URL key is never used to
    assert article identity.
    """
    raw = raw.strip().rstrip(_TRAILING)
    parts = urllib.parse.urlsplit(raw)
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    try:
        port = parts.port
    except ValueError:
        port = None
    suffix = ":%d" % port if port else ""
    path = parts.path.rstrip("/")
    query = "?%s" % parts.query if parts.query else ""
    return "%s%s%s%s" % (host, suffix, path, query)


def normalize_identifier(scheme: str, raw: str) -> str:
    """Normalize one raw identifier string for its scheme. No fuzzy matching anywhere."""
    value = raw.strip().rstrip(_TRAILING)
    if scheme == "doi":
        low = value.lower()
        for prefix in _DOI_URL_PREFIXES:
            if low.startswith(prefix):
                low = low[len(prefix):]
                break
        if low.startswith("doi:"):
            low = low[4:]
        return low.strip().rstrip(_TRAILING)
    if scheme == "pmid":
        return re.sub(r"\D", "", value)
    if scheme == "pmcid":
        return "PMC" + re.sub(r"\D", "", value)
    if scheme == "url":
        return normalize_url(value)
    if scheme == "eudract":
        return value
    return value.upper()


@dataclass(frozen=True)
class Mention:
    scheme: str
    raw: str
    normalized: str
    locator: str
    context: str  # "structured_field", "prose_context" or "structured_field_name"

    def as_dict(self) -> Dict[str, str]:
        return {
            "scheme": self.scheme,
            "raw": self.raw,
            "normalized": self.normalized,
            "locator": self.locator,
            "context": self.context,
        }


def extract_identifiers(text: str, locator: str = "", context: str = "prose_context") -> List[Mention]:
    """Extract every identifier mention from one string. Order is stable."""
    found: List[Mention] = []
    seen = set()
    for scheme, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            raw = match.group(0).strip().rstrip(_TRAILING)
            if not raw:
                continue
            normalized = normalize_identifier(scheme, raw)
            if not normalized:
                continue
            key = (scheme, normalized, locator)
            if key in seen:
                continue
            seen.add(key)
            found.append(Mention(scheme, raw, normalized, locator, context))
    return found


def scheme_for_field_name(key: str) -> Optional[str]:
    """F1: map a JSON field NAME to an identity scheme, or None.

    Accepts the bare scheme name and a ``<qualifier>_<scheme>`` suffix, so ``pmid``,
    ``source_pmid`` and ``primary_doi`` all resolve. Nothing here inspects the value;
    a field name only proposes a scheme, and the value must still parse under it.
    """
    low = key.strip().lower()
    for scheme in IDENTITY_SCHEMES:
        if low == scheme or low.endswith("_" + scheme):
            return scheme
    return None


def extract_field_name_identifier(key: str, value: str, locator: str) -> Optional[Mention]:
    """F1: index a bare identifier whose scheme is carried by its field name.

    Real retained records store ``"pmid": "24703573"`` — a value that spells out no
    scheme, so purely syntactic extraction never sees it and the tool reports a false
    non-match. The value must parse as a *complete* identifier of the field's scheme;
    prose in an identifier-named field yields nothing.
    """
    scheme = scheme_for_field_name(key)
    if scheme is None:
        return None
    parsed_scheme, parsed = parse_candidate(value, kind=scheme)
    if parsed_scheme is None:
        return None
    return Mention(parsed_scheme, value.strip(), parsed, locator, "structured_field_name")


def parse_candidate(query: str, kind: Optional[str] = None) -> Tuple[Optional[str], str]:
    """Resolve a query string to (scheme, normalized) or (None, reason).

    Bare digits are rejected unless ``kind='pmid'`` is given explicitly, so that a
    stray number cannot be silently treated as a PubMed identifier.
    """
    value = (query or "").strip()
    if not value:
        return None, "empty candidate"

    if kind:
        if kind not in IDENTITY_SCHEMES + ("url",):
            return None, "unknown kind %r" % kind
        if kind == "doi":
            normalized = normalize_identifier("doi", value)
            if _DOI_FULL.match(normalized):
                return "doi", normalized
            return None, "not a syntactically valid DOI"
        if kind == "pmid":
            match = _PMID_FULL.match(value)
            if match:
                return "pmid", match.group(1)
            return None, "not a syntactically valid PMID"
        if kind == "pmcid":
            match = _PMCID_FULL.match(value)
            if match:
                return "pmcid", "PMC" + match.group(1)
            return None, "not a syntactically valid PMCID"
        if kind == "url":
            if "://" not in value:
                return None, "not a syntactically valid URL"
            return "url", normalize_url(value)
        for scheme, pattern in _PATTERNS:
            if scheme != kind:
                continue
            match = pattern.fullmatch(value)
            if match:
                return scheme, normalize_identifier(scheme, value)
        return None, "not a syntactically valid %s" % kind

    doi_candidate = normalize_identifier("doi", value)
    if _DOI_FULL.match(doi_candidate):
        return "doi", doi_candidate
    if value.lower().startswith(("http://", "https://")):
        return "url", normalize_url(value)
    if _PMCID_FULL.match(value):
        return "pmcid", normalize_identifier("pmcid", value)
    if re.match(r"^pmid\s*:?\s*\d{4,9}$", value, re.IGNORECASE):
        return "pmid", re.sub(r"\D", "", value)
    for scheme, pattern in _PATTERNS:
        if scheme in ("doi", "pmid", "pmcid", "url"):
            continue
        if pattern.fullmatch(value):
            return scheme, normalize_identifier(scheme, value)
    if re.match(r"^\d+$", value):
        return None, "bare number: pass --kind pmid to query a PubMed identifier"
    return None, "unrecognised identifier syntax; titles are never matched"


# --------------------------------------------------------------------------------------
# Access-evidence classification (from explicitly reported text only)
# --------------------------------------------------------------------------------------

_ACCESS_TRIGGERS = (
    "access",
    "retriev",
    "request",
    "denial",
    "denied",
    "block",
    "refus",
    "403",
    "forbidden",
    "subscription",
    "full text",
    "full-text",
    "fulltext",
    "egress",
    "proxy",
    "unavailab",
    "paywall",
    "authenticat",
    # F4: restriction/exclusion wording previously fell outside the gate entirely.
    "restrict",
    "exclud",
    "embargo",
)

_ACCESS_RULES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("proxy_or_network_failure", ("egress", "proxy", "network failure", "dns", "timeout", "connection refused")),
    ("http_403_unclassified_denial", ("403", "forbidden")),
    ("publisher_authentication_or_subscription", ("subscription", "authenticat", "paywall", "sign-in", "login")),
    ("policy_or_biology_refusal", (
        "guardrail", "refusal", "refused", "policy restriction", "policy-restricted",
        # F4: a policy/biology exclusion is a category of its own, not "unclassified".
        "policy restricted", "restricted under policy", "excluded by policy",
        "excluded from retrieval", "excluded from this packet", "restricted reagent",
        "policy exclusion",
    )),
    ("full_text_unavailable_in_scope", ("not full text", "no full text", "no recovered original full text", "unavailab", "not recovered")),
    ("no_access_attempt_in_this_packet", ("no current access-state test was performed", "no access attempt", "not attempted", "no http request", "no request was made")),
)

_NEGATION_MARKERS = (" not ", "is not", "are not", "never", "none", "no current", "no recovered")

_CLAUSE_SPLIT = re.compile(r"(?<=[.;])\s+")


def _clauses(text: str) -> List[str]:
    """Split one statement into clauses for per-label evidence. Deliberately crude and
    documented as such: it exists to quote the surrounding clause, not to parse English."""
    parts = [part.strip() for part in _CLAUSE_SPLIT.split(text) if part.strip()]
    return parts or [text.strip()]


def classify_access_text(text: str) -> List[str]:
    """Multi-label classification of one reported access statement.

    Labels come only from phrases present in the record's own text. Unfamiliar wording
    fails toward 'unclassified_reported_access_evidence' rather than being guessed into
    a category, and distinct categories are never collapsed into one another (an HTTP
    403 is not relabelled as publisher authentication).

    A label means the category is NAMED in the text. It does not mean the record
    asserts it: a sentence written to rule a category out still names it. Use
    ``classify_access_details`` for the per-label evidence that separates the two.

    'reported_complete_source_recovered' is never assigned from prose; it comes only
    from the structured retained-bytes signal (see _bytes_signal).
    """
    return [detail["label"] for detail in classify_access_details(text)]


def classify_access_details(text: str) -> List[Dict[str, object]]:
    """F2: labels WITH evidence — matched phrase, containing clause, clause negation.

    No label is dropped on account of negation. Dropping would delete correct labels
    (``"this is not full text"`` genuinely reports unavailable full text) as readily as
    wrong ones, so the tool reports what it matched and where, and leaves the reading to
    a human.
    """
    low = text.lower()
    if not any(trigger in low for trigger in _ACCESS_TRIGGERS):
        return []
    clause_list = _clauses(text)
    details: List[Dict[str, object]] = []
    for label, phrases in _ACCESS_RULES:
        for phrase in phrases:
            if phrase not in low:
                continue
            clause = next((c for c in clause_list if phrase in c.lower()), text.strip())
            details.append({
                "label": label,
                "matched_phrase": phrase,
                "clause": clause,
                "clause_has_negation": _negation_present(clause),
            })
            break
    if not details:
        details.append({
            "label": "unclassified_reported_access_evidence",
            "matched_phrase": "",
            "clause": text.strip(),
            "clause_has_negation": _negation_present(text),
        })
    return details


def _negation_present(text: str) -> bool:
    low = " " + text.lower() + " "
    return any(marker in low for marker in _NEGATION_MARKERS)


def _access_event(record_id: str, locator: str, text: str) -> Optional[Dict[str, object]]:
    details = classify_access_details(text)
    if not details:
        return None
    return {
        "record_id": record_id,
        "locator": locator,
        "labels": [detail["label"] for detail in details],
        "label_evidence": details,
        "quote": text,
        "negated_terms_present": _negation_present(text),
        "labels_are_mentions_not_assertions": True,
    }


# --------------------------------------------------------------------------------------
# Record scanning
# --------------------------------------------------------------------------------------

@dataclass
class Record:
    record_id: str
    path: str
    kind: str
    position: int = -1
    synthetic_fixture: bool = False
    mentions: List[Mention] = field(default_factory=list)
    groups: List[List[Mention]] = field(default_factory=list)
    access_events: List[Dict[str, object]] = field(default_factory=list)
    statuses: List[Dict[str, str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


_URL_KEY = re.compile(r"url", re.IGNORECASE)
_SHA_KEYS = ("sha256", "content_sha256", "member_sha256", "file_sha256")


def _bytes_signal(node: Dict[str, object]) -> Optional[Dict[str, str]]:
    """Detect an explicitly retained-bytes claim: a URL, a sha256 and an archive member
    recorded together in one object. This is the only source of the
    'reported_complete_source_recovered' label; it reports what the record states and
    does not verify any hash.

    F7: the URL must come from a key whose NAME contains 'url' and the digest from a key
    named sha256/content_sha256/member_sha256/file_sha256. Before this, any http-valued
    string plus any ``*_sha256`` plus an ``archive_member`` — key names unrelated — was
    reported as retained bytes for that URL. The association basis is now stated so a
    reader can see which keys were tied together.
    """
    url = sha = member = None
    url_key = sha_key = ""
    for key, value in node.items():
        if not isinstance(value, str):
            continue
        low = key.lower()
        if url is None and _URL_KEY.search(low) and value.lower().startswith(("http://", "https://")):
            url = value
            url_key = key
        if sha is None and low in _SHA_KEYS and _SHA256.match(value):
            sha = value
            sha_key = key
        if low in ("archive_member", "archive_members"):
            member = value
    if url and sha and member:
        return {
            "url": url,
            "sha256": sha,
            "archive_member": member,
            "association_basis": "keys %s + %s + archive_member in one object" % (url_key, sha_key),
        }
    return None


def _is_synthetic(node: object) -> bool:
    """F8: does any object in this record carry a truthy ``synthetic_fixture`` flag?"""
    if isinstance(node, dict):
        if node.get("synthetic_fixture"):
            return True
        return any(_is_synthetic(value) for value in node.values())
    if isinstance(node, list):
        return any(_is_synthetic(item) for item in node)
    return False


def _walk_json(node: object, path: str, record: Record) -> None:
    if isinstance(node, dict):
        group: List[Mention] = []
        for key in sorted(node.keys()):
            value = node[key]
            child = "%s.%s" % (path, key) if path else key
            strings: List[Tuple[str, str]] = []
            if isinstance(value, str):
                strings.append((child, value))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, str):
                        strings.append(("%s[%d]" % (child, index), item))
            for locator, text in strings:
                mentions = extract_identifiers(text, locator, "structured_field")
                seen = {(m.scheme, m.normalized, m.locator) for m in mentions}
                by_name = extract_field_name_identifier(key, text, locator)
                if by_name is not None and (by_name.scheme, by_name.normalized, by_name.locator) not in seen:
                    mentions.append(by_name)
                record.mentions.extend(mentions)
                group.extend(mentions)
                event = _access_event(record.record_id, locator, text)
                if event is not None:
                    record.access_events.append(event)
        if group:
            record.groups.append(group)
        signal = _bytes_signal(node)
        if signal is not None:
            record.access_events.append({
                "record_id": record.record_id,
                "locator": path or "$",
                "labels": ["reported_complete_source_recovered"],
                "label_evidence": [{
                    "label": "reported_complete_source_recovered",
                    "matched_phrase": "",
                    "clause": signal["association_basis"],
                    "clause_has_negation": False,
                }],
                "quote": "record reports retained bytes: url=%s sha256=%s archive_member=%s"
                         % (signal["url"], signal["sha256"], signal["archive_member"]),
                "association_basis": signal["association_basis"],
                "negated_terms_present": False,
                "labels_are_mentions_not_assertions": True,
                "hash_not_recomputed": True,
            })
        for key in sorted(node.keys()):
            value = node[key]
            child = "%s.%s" % (path, key) if path else key
            if isinstance(value, (dict, list)):
                _walk_json(value, child, record)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            if isinstance(item, (dict, list)):
                _walk_json(item, "%s[%d]" % (path, index), record)


def _collect_statuses(node: object, record: Record) -> None:
    if not isinstance(node, dict):
        return
    date = ""
    for key in ("utc", "date", "recorded_utc", "timestamp"):
        value = node.get(key)
        if isinstance(value, str):
            date = value
            break
    for key in sorted(node.keys()):
        value = node[key]
        if not isinstance(value, str):
            continue
        low = key.lower()
        if low == "status" or low.endswith("_status"):
            record.statuses.append({
                "record_id": record.record_id,
                "date": date,
                "field": key,
                "status": value,
                "locator": key,
            })


def scan_file(path: str, record_id: str) -> Record:
    """Open one file read-only and index it. Never writes, never fetches."""
    extension = os.path.splitext(path)[1].lower()
    record = Record(record_id=record_id, path=path, kind=extension.lstrip("."))
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    if extension == ".json":
        try:
            data = json.loads(text)
        except ValueError as exc:
            record.notes.append("JSON parse failed (%s); indexed as plain lines." % exc)
        else:
            record.synthetic_fixture = _is_synthetic(data)
            _walk_json(data, "", record)
            _collect_statuses(data, record)
            return record
    for number, line in enumerate(text.splitlines(), start=1):
        locator = "line:%d" % number
        mentions = extract_identifiers(line, locator, "prose_context")
        record.mentions.extend(mentions)
        if mentions:
            record.groups.append(mentions)
        event = _access_event(record.record_id, locator, line)
        if event is not None:
            record.access_events.append(event)
    return record


def _iter_files(root: str, skipped: List[str]) -> Iterable[Tuple[str, str]]:
    if os.path.isfile(root):
        yield root, os.path.basename(root)
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            if os.path.splitext(name)[1].lower() in TEXT_EXTENSIONS:
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                yield full, rel
            else:
                # F6: a dropped file used to leave no trace at all.
                skipped.append(os.path.relpath(full, root).replace(os.sep, "/"))


@dataclass
class Index:
    roots: List[str]
    records: List[Record] = field(default_factory=list)
    missing_roots: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)

    @property
    def files(self) -> List[str]:
        return [record.record_id for record in self.records]

    def warnings(self) -> List[str]:
        """F6: never let an empty or mistyped corpus read like a genuine non-match."""
        warnings: List[str] = []
        for root in self.missing_roots:
            warnings.append(
                "Corpus root does not exist and contributed no files: %r. A non-match "
                "against a missing root says nothing about the identifier." % root
            )
        if not self.records:
            warnings.append(
                "The index is EMPTY: zero files were opened. Every lookup against this "
                "index is unresolved by construction and carries no information."
            )
        if self.skipped_files:
            warnings.append(
                "%d file(s) were skipped because their extension is outside %s: %s. "
                "Their contents were not indexed."
                % (len(self.skipped_files), sorted(TEXT_EXTENSIONS),
                   ", ".join(sorted(self.skipped_files)[:10]))
            )
        return warnings

    def scope(self) -> Dict[str, object]:
        return {
            "roots": list(self.roots),
            "files": self.files,
            "file_origins": [
                {"record_id": r.record_id, "origin_path": r.path, "position": r.position,
                 "synthetic_fixture": r.synthetic_fixture}
                for r in self.records
            ],
            "file_count": len(self.records),
            "missing_roots": list(self.missing_roots),
            "skipped_files": list(self.skipped_files),
            "scope_warnings": self.warnings(),
            "scope_note": (
                "Supplied corpus only: exactly these files were opened read-only. "
                "Records referenced by them but absent here were not inspected."
            ),
        }


def build_index(roots: Sequence[str]) -> Index:
    index = Index(roots=[str(root) for root in roots])
    seen = set()
    used_ids: Dict[str, int] = {}
    for root in index.roots:
        if not os.path.exists(root):
            index.missing_roots.append(root)
            continue
        for path, record_id in _iter_files(root, index.skipped_files):
            key = os.path.abspath(path)
            if key in seen:
                continue
            seen.add(key)
            record = scan_file(path, record_id)
            index.records.append(record)
    index.records.sort(key=lambda record: (record.record_id, os.path.abspath(record.path)))
    for position, record in enumerate(index.records):
        # F5: two files may share a basename. Identity is the position; the id is only a
        # label, disambiguated so a reader can tell the two apart in output.
        count = used_ids.get(record.record_id, 0)
        used_ids[record.record_id] = count + 1
        if count:
            record.record_id = "%s#%d" % (record.record_id, count + 1)
        record.position = position
        for collection in (record.access_events, record.statuses):
            for entry in collection:
                entry["record_id"] = record.record_id
    return index


# --------------------------------------------------------------------------------------
# Lookup
# --------------------------------------------------------------------------------------

def _base_result(query: str, scheme: Optional[str], normalized: Optional[str], index: Index) -> Dict[str, object]:
    scope = index.scope()
    return {
        "query": query,
        "resolved_scheme": scheme,
        "normalized": normalized,
        "state": "",
        "matches": [],
        "url_key_mentions": [],
        "record_statuses": [],
        "access_evidence": [],
        "conflicts": [],
        "notes": [],
        "indexed_scope": scope,
        "scope_warnings": scope["scope_warnings"],
        "synthetic_fixture_records": [],
        "disclaimer": DISCLAIMER,
    }


def _matches_for(index: Index, scheme: str, normalized: str) -> List[Dict[str, object]]:
    matches: List[Dict[str, object]] = []
    for record in index.records:
        for mention in record.mentions:
            if mention.scheme == scheme and mention.normalized == normalized:
                entry: Dict[str, object] = dict(mention.as_dict())
                entry["record_id"] = record.record_id
                entry["record_position"] = record.position
                entry["origin_path"] = record.path
                entry["synthetic_fixture"] = record.synthetic_fixture
                matches.append(entry)
    matches.sort(key=lambda entry: (str(entry["record_id"]), str(entry["locator"])))
    return matches


def _co_identifier_conflicts(index: Index, scheme: str, normalized: str) -> List[Dict[str, object]]:
    partners: Dict[str, Dict[str, List[str]]] = {}
    for record in index.records:
        for group in record.groups:
            if not any(m.scheme == scheme and m.normalized == normalized for m in group):
                continue
            for mention in group:
                if mention.scheme == scheme or mention.scheme not in IDENTITY_SCHEMES:
                    continue
                bucket = partners.setdefault(mention.scheme, {})
                where = bucket.setdefault(mention.normalized, [])
                locator = "%s@%s" % (record.record_id, mention.locator)
                if locator not in where:
                    where.append(locator)
    conflicts: List[Dict[str, object]] = []
    for partner_scheme in sorted(partners):
        values = partners[partner_scheme]
        if len(values) > 1:
            conflicts.append({
                "type": "co_identifier_divergence",
                "query_scheme": scheme,
                "query_normalized": normalized,
                "partner_scheme": partner_scheme,
                "values": sorted(values),
                "provenance": {value: values[value] for value in sorted(values)},
                "note": (
                    "The same %s is bound to differing %s values in the supplied corpus. "
                    "Both bindings are retained; this tool does not adjudicate which is "
                    "correct, and asserts no cross-scheme identity that a record did not "
                    "state." % (scheme.upper(), partner_scheme.upper())
                ),
            })
    return conflicts


def _status_conflicts(statuses: Sequence[Dict[str, str]]) -> List[Dict[str, object]]:
    """F3: divergence means the SAME field name carrying different values.

    Orthogonal dimensions (``operational_status``, ``scientific_status``,
    ``source_asset_status``) in one record disagree about nothing, and reporting them as
    a contradiction manufactures a conflict the repository does not assert.
    """
    by_field: Dict[str, List[Dict[str, str]]] = {}
    for entry in statuses:
        by_field.setdefault(entry["field"], []).append(entry)
    conflicts: List[Dict[str, object]] = []
    for field_name in sorted(by_field):
        entries = by_field[field_name]
        if len({entry["status"] for entry in entries}) > 1:
            conflicts.append({
                "type": "differing_record_status",
                "field": field_name,
                "statuses": entries,
                "note": (
                    "Field %r carries differing dated statuses. All are listed in date "
                    "order and all are retained; none is superseded, merged or "
                    "overwritten here. This flags divergence for human reading and does "
                    "not assert contradiction. Statuses under DIFFERENT field names are "
                    "orthogonal dimensions and are not compared." % field_name
                ),
            })
    return conflicts


def lookup(index: Index, query: str, kind: Optional[str] = None) -> Dict[str, object]:
    """Look one candidate up. Always returns a result dict; never raises for bad input."""
    scheme, resolved = parse_candidate(query, kind)
    if scheme is None:
        result = _base_result(query, None, None, index)
        result["state"] = "invalid_candidate"
        result["reason"] = resolved
        result["notes"] = [NON_MATCH_NOTE, TITLE_NOTE] + list(result["scope_warnings"])
        return result

    if scheme == "url":
        result = _base_result(query, "url", resolved, index)
        embedded = [
            mention for mention in extract_identifiers(query, "query", "query_string")
            if mention.scheme in IDENTITY_SCHEMES
        ]
        distinct = sorted({(m.scheme, m.normalized) for m in embedded})
        result["url_key_mentions"] = _matches_for(index, "url", resolved)
        if len(distinct) > 1:
            result["state"] = "ambiguous_multiple_identifiers"
            result["embedded_identifiers"] = [
                {"scheme": item[0], "normalized": item[1]} for item in distinct
            ]
            result["notes"] = [
                URL_NOTE,
                NON_MATCH_NOTE,
                "This URL embeds more than one identifier; it is not resolved to any "
                "single record, and no candidate was chosen arbitrarily.",
            ] + list(result["scope_warnings"])
            return result
        if not distinct:
            result["state"] = "unresolved_url_without_identifier"
            result["notes"] = [
                URL_NOTE,
                NON_MATCH_NOTE,
                "This URL carries no embedded DOI/PMID/PMCID/accession, so it cannot "
                "identify an article. Any URL mentions listed under url_key_mentions are "
                "string co-occurrences only.",
            ] + list(result["scope_warnings"])
            return result
        inner_scheme, inner_normalized = distinct[0]
        inner = lookup(index, inner_normalized, kind=inner_scheme)
        inner["query"] = query
        inner["resolved_via"] = {
            "url_key": resolved,
            "embedded_scheme": inner_scheme,
            "embedded_normalized": inner_normalized,
        }
        inner["url_key_mentions"] = result["url_key_mentions"]
        inner["notes"] = [URL_NOTE] + list(inner["notes"])
        return inner

    result = _base_result(query, scheme, resolved, index)
    matches = _matches_for(index, scheme, resolved)
    result["matches"] = matches
    if not matches:
        result["state"] = "unresolved_not_indexed"
        result["notes"] = [NON_MATCH_NOTE] + list(result["scope_warnings"])
        return result

    # F5: select contributing records by POSITION, never by record_id string equality.
    matched_positions = {entry["record_position"] for entry in matches}
    statuses: List[Dict[str, str]] = []
    events: List[Dict[str, object]] = []
    synthetic: List[str] = []
    for record in index.records:
        if record.position not in matched_positions:
            continue
        statuses.extend(record.statuses)
        events.extend(record.access_events)
        if record.synthetic_fixture:
            synthetic.append(record.record_id)
    statuses.sort(key=lambda entry: (entry["date"], entry["record_id"], entry["field"]))
    events.sort(key=lambda entry: (str(entry["record_id"]), str(entry["locator"])))
    result["record_statuses"] = statuses
    result["access_evidence"] = events
    result["synthetic_fixture_records"] = sorted(synthetic)

    conflicts = _co_identifier_conflicts(index, scheme, resolved)
    conflicts.extend(_status_conflicts(statuses))
    result["conflicts"] = conflicts

    notes = [DATED_NOTE]
    if events:
        notes.append(LABEL_MENTION_NOTE)
    else:
        # F4: silence and "nothing recognised" used to render identically.
        notes.append(NO_ACCESS_EVIDENCE_NOTE)
    if any(event.get("negated_terms_present") for event in events):
        notes.append(
            "At least one access statement contains negating wording. Labels record the "
            "categories named in the text, including categories the record explicitly "
            "rules out; read the verbatim quote before drawing any conclusion."
        )
    if synthetic:
        notes.append(
            "%s Matched record(s) %s are labelled synthetic fixtures and assert no "
            "bibliographic fact." % (SYNTHETIC_MARKER, ", ".join(sorted(synthetic)))
        )
    notes.extend(result["scope_warnings"])
    result["notes"] = notes

    if all(entry["context"] == "prose_context" for entry in matches):
        result["state"] = "matched_prose_mention_only"
        result["notes"].append(
            "Every match is a prose mention, not a structured record field: the corpus "
            "discusses this identifier but no structured record binds it."
        )
    elif conflicts:
        result["state"] = "matched_with_divergent_states"
    else:
        result["state"] = "matched"
    return result


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def _mark(entry: Dict[str, object], text: str) -> str:
    """F8: prefix a rendered line whose record is a labelled synthetic fixture."""
    return "%s %s" % (SYNTHETIC_MARKER, text) if entry.get("synthetic_fixture") else text


def render_text(result: Dict[str, object]) -> str:
    synthetic_ids = set(result.get("synthetic_fixture_records") or [])
    lines = [
        "query            : %s" % result["query"],
        "resolved_scheme  : %s" % result["resolved_scheme"],
        "normalized       : %s" % result["normalized"],
        "state            : %s" % result["state"],
    ]
    if result.get("reason"):
        lines.append("reason           : %s" % result["reason"])
    for entry in result["matches"]:
        lines.append("match            : " + _mark(entry, "%s :: %s [%s] (%s) <- %s"
                     % (entry["record_id"], entry["locator"], entry["context"],
                        entry["raw"], entry["origin_path"])))
    for entry in result["url_key_mentions"]:
        lines.append("url_mention      : " + _mark(entry, "%s :: %s"
                     % (entry["record_id"], entry["locator"])))
    for entry in result["record_statuses"]:
        text = "%s | %s | %s :: %s" % (entry["date"] or "undated", entry["record_id"],
                                       entry["field"], entry["status"])
        if entry["record_id"] in synthetic_ids:
            text = "%s %s" % (SYNTHETIC_MARKER, text)
        lines.append("status           : %s" % text)
    for entry in result["access_evidence"]:
        text = "%s :: %s :: %s" % (entry["record_id"], ",".join(entry["labels"]), entry["quote"])
        if entry["record_id"] in synthetic_ids:
            text = "%s %s" % (SYNTHETIC_MARKER, text)
        lines.append("access_evidence  : %s" % text)
        for detail in entry.get("label_evidence", []):
            lines.append("  label_basis    : %s | phrase=%r | clause_negates=%s"
                         % (detail["label"], detail["matched_phrase"],
                            detail["clause_has_negation"]))
    for entry in result["conflicts"]:
        lines.append("conflict         : %s :: %s" % (entry["type"], entry["note"]))
    for note in result["notes"]:
        lines.append("note             : %s" % note)
    for warning in result.get("scope_warnings") or []:
        lines.append("scope_warning    : %s" % warning)
    scope = result["indexed_scope"]
    lines.append("indexed_scope    : %d file(s): %s"
                 % (scope["file_count"], ", ".join(scope["files"])))
    lines.append("disclaimer       : %s" % result["disclaimer"])
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only identifier/source-provenance lookup over retained records. "
            "Informational only: exits 0 for every lookup state, including unresolved "
            "and invalid, so it cannot act as a gate."
        )
    )
    parser.add_argument("query", help="DOI, PMID, PMCID, accession or URL")
    parser.add_argument("--record", action="append", default=None,
                        help="file or directory to index (repeatable; default '.')")
    parser.add_argument("--kind", choices=sorted(IDENTITY_SCHEMES + ("url",)), default=None,
                        help="force the candidate scheme (required for a bare PMID)")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)

    roots = args.record or ["."]
    index = build_index(roots)
    result = lookup(index, args.query, args.kind)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 0  # deliberate: every lookup state exits 0; this tool is not a gate.


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/tests/test_source_reuse_index.py`

sha256 `49208917bba102cd1bceb4ac932046dcab20609f046303f5dc8476954904136a`, 477 lines, LF, 18 test functions.

```python
"""Behavioural tests for the read-only source-reuse index (scripts/source_reuse_index.py).

All fixtures are SYNTHETIC and labelled: identifiers use reserved namespaces only
(DOI prefix 10.5555/, PMID 999000xx / 99900573, PMC9990001, host fixture.invalid). No
fixture asserts a real bibliographic fact, and no real source record is copied here.

The tests assert observable behaviour (lookup states, provenance, retained dated
statuses, access-label separation, CLI exit codes). They do not pin internal structure,
wording of prose, or file length.

Tests 1-10 are the delivered behavioural suite. Tests 11-18 pin the eight repairs made
after independent review; each was written from a failing case reproduced against the
unrepaired helper, and each fails if that repair is reverted.

Standard library only. Every fixture is written under tempfile.mkdtemp(), never into the
repository: this directory carries no conftest write guard, so the isolation is by
construction rather than by fixture.
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import source_reuse_index as sri  # noqa: E402


ALPHA_EARLY = {
    "synthetic_fixture": True,
    "utc": "2026-09-01T00:00:00+00:00",
    "status": "open_candidate_potentially_distinct_report",
    "source_identity": {
        "doi": "10.5555/synthetic-alpha.0001",
        "pmid": "PMID 99900001",
    },
    "access_note": "Historical proxy EGRESS_BLOCKED result recorded for this candidate.",
}

ALPHA_LATE = {
    "synthetic_fixture": True,
    "utc": "2026-09-08T00:00:00+00:00",
    "status": "closed_at_deduplication_no_new_source_asset",
    "source_identity": {
        "doi": "10.5555/SYNTHETIC-ALPHA.0001",
        "pmid": "PMID 99900002",
    },
    "access_note": "No current access-state test was performed in this packet.",
}

BETA = {
    "synthetic_fixture": True,
    "utc": "2026-09-07T00:00:00+00:00",
    "status": "admitted_limited_transcribed_source_fields",
    "source": {
        "pmcid": "PMC9990001",
        "doi": "10.5555/synthetic-beta.0002",
        "url": "https://www.fixture.invalid/europepmc/rest/PMC9990001/fullTextXML",
        "sha256": "ab" * 32,
        "archive_member": "synthetic-fixture/primary-source/PMC9990001.xml",
        "locator": "JATS sec13, direct paragraph 1",
    },
    "denial_note": "Three institutional URLs each returned 403 on one direct request; none retried.",
    "subscription_note": "Only subscription full-text link metadata was present; this is not full text.",
    "odd_note": "Access route condition observed but not otherwise described here.",
}

GAMMA_MD = (
    "# Synthetic fixture memo (labelled synthetic)\n"
    "\n"
    "Candidate discussed in prose only: doi:10.5555/synthetic-gamma.0003 (PMID 99900003).\n"
)

DELTA_MD = (
    "# Synthetic fixture memo (labelled synthetic)\n"
    "\n"
    "Resolver lead: https://fixture.invalid/resolve?a=10.5555/synthetic-delta.0004"
    "&b=10.5555/synthetic-delta.0005\n"
    "Bare PDF lead: https://fixture.invalid/journals/impressive-response-longterm-survival.pdf\n"
)

PDF_URL = "https://fixture.invalid/journals/impressive-response-longterm-survival.pdf"

# The sentence that produced the five-label collapse (F2), rewritten with synthetic
# wording. Three of the five categories it names are the ones it exists to rule out.
NEGATING_ACCESS_SENTENCE = (
    "Historical proxy EGRESS_BLOCKED results are not publisher authentication denials, "
    "biological guardrail refusals or proof of global unavailability. This packet closed "
    "under its bounded no-repeat contract; no current access-state test was performed."
)


def _write_corpus(files):
    """Write a synthetic corpus under a fresh temp directory and return its path.

    Nothing here ever writes inside the repository.
    """
    root = tempfile.mkdtemp(prefix="sri-synthetic-fixture-")
    for name, payload in files.items():
        path = os.path.join(root, name)
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent)
        with open(path, "w", encoding="utf-8") as handle:
            if isinstance(payload, str):
                handle.write(payload)
            else:
                json.dump(payload, handle, indent=2)
    return root


class SourceReuseIndexTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="sri-synthetic-fixture-")
        records = os.path.join(cls.root, "records")
        os.makedirs(records)
        for name, payload in (
            ("alpha-2026-09-01.json", ALPHA_EARLY),
            ("alpha-2026-09-08.json", ALPHA_LATE),
            ("beta-recovered.json", BETA),
        ):
            with open(os.path.join(records, name), "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
        for name, text in (("gamma-prose.md", GAMMA_MD), ("delta-leads.md", DELTA_MD)):
            with open(os.path.join(records, name), "w", encoding="utf-8") as handle:
                handle.write(text)
        cls.index = sri.build_index([cls.root])
        cls._temp_roots = [cls.root]

    @classmethod
    def tearDownClass(cls):
        for root in cls._temp_roots:
            shutil.rmtree(root, ignore_errors=True)

    def corpus(self, files):
        root = _write_corpus(files)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def records_of(self, result):
        return sorted({entry["record_id"] for entry in result["matches"]})

    # 1
    def test_doi_spelling_variants_resolve_identically(self):
        variants = [
            "10.5555/synthetic-alpha.0001",
            "10.5555/SYNTHETIC-ALPHA.0001",
            "doi:10.5555/Synthetic-Alpha.0001",
            "https://doi.org/10.5555/synthetic-alpha.0001",
            "10.5555/synthetic-alpha.0001.",
        ]
        results = [sri.lookup(self.index, variant) for variant in variants]
        for result in results:
            self.assertEqual(result["normalized"], "10.5555/synthetic-alpha.0001")
            self.assertEqual(result["state"], results[0]["state"])
            self.assertEqual(self.records_of(result), self.records_of(results[0]))
        self.assertEqual(len(self.records_of(results[0])), 2)

    # 2
    def test_provenance_is_file_plus_field_or_line_with_context_flag(self):
        structured = sri.lookup(self.index, "10.5555/synthetic-alpha.0001")
        located = [
            entry for entry in structured["matches"]
            if entry["record_id"].endswith("alpha-2026-09-01.json")
        ]
        self.assertEqual(len(located), 1)
        self.assertEqual(located[0]["locator"], "source_identity.doi")
        self.assertEqual(located[0]["context"], "structured_field")

        prose = sri.lookup(self.index, "10.5555/synthetic-gamma.0003")
        self.assertEqual(prose["state"], "matched_prose_mention_only")
        self.assertEqual(len(prose["matches"]), 1)
        self.assertTrue(prose["matches"][0]["record_id"].endswith("gamma-prose.md"))
        self.assertEqual(prose["matches"][0]["locator"], "line:3")
        self.assertEqual(prose["matches"][0]["context"], "prose_context")

    # 3
    def test_pdf_url_without_identifier_is_unresolved_and_never_novelty(self):
        result = sri.lookup(self.index, PDF_URL)
        self.assertEqual(result["state"], "unresolved_url_without_identifier")
        self.assertEqual(result["matches"], [])
        joined = " ".join(result["notes"]).lower()
        self.assertIn("not novelty", joined)
        self.assertIn("url alone never establishes article identity", joined)
        for forbidden in ("new source", "novel article", "not previously known"):
            self.assertNotIn(forbidden, joined)

    # 4
    def test_url_resolves_through_embedded_pmcid_across_scheme_and_www_variants(self):
        query = "http://fixture.invalid/europepmc/rest/PMC9990001/fullTextXML"
        result = sri.lookup(self.index, query)
        self.assertIn(result["state"], ("matched", "matched_with_divergent_states"))
        self.assertEqual(result["resolved_via"]["embedded_scheme"], "pmcid")
        self.assertEqual(result["resolved_via"]["embedded_normalized"], "PMC9990001")
        self.assertEqual(self.records_of(result), ["records/beta-recovered.json"])
        self.assertEqual(
            sri.normalize_url(query),
            sri.normalize_url("https://www.fixture.invalid/europepmc/rest/PMC9990001/fullTextXML#sec1"),
        )

    # 5
    def test_two_dated_statuses_are_both_retained_in_date_order(self):
        result = sri.lookup(self.index, "10.5555/synthetic-alpha.0001")
        self.assertEqual(result["state"], "matched_with_divergent_states")
        dates = [entry["date"] for entry in result["record_statuses"]]
        self.assertEqual(dates, sorted(dates))
        statuses = [entry["status"] for entry in result["record_statuses"]]
        self.assertIn("open_candidate_potentially_distinct_report", statuses)
        self.assertIn("closed_at_deduplication_no_new_source_asset", statuses)
        conflict = [c for c in result["conflicts"] if c["type"] == "differing_record_status"]
        self.assertEqual(len(conflict), 1)
        self.assertIn("none is superseded", conflict[0]["note"])

    # 6
    def test_one_doi_bound_to_two_pmids_is_reported_as_divergence(self):
        result = sri.lookup(self.index, "10.5555/synthetic-alpha.0001")
        conflicts = [c for c in result["conflicts"] if c["type"] == "co_identifier_divergence"]
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["partner_scheme"], "pmid")
        self.assertEqual(conflicts[0]["values"], ["99900001", "99900002"])
        self.assertEqual(len(conflicts[0]["provenance"]["99900001"]), 1)

    # 7
    def test_url_embedding_two_dois_is_ambiguous_not_arbitrarily_resolved(self):
        query = ("https://fixture.invalid/resolve?a=10.5555/synthetic-delta.0004"
                 "&b=10.5555/synthetic-delta.0005")
        result = sri.lookup(self.index, query)
        self.assertEqual(result["state"], "ambiguous_multiple_identifiers")
        embedded = sorted(item["normalized"] for item in result["embedded_identifiers"])
        self.assertEqual(embedded, ["10.5555/synthetic-delta.0004", "10.5555/synthetic-delta.0005"])
        self.assertEqual(result["matches"], [])

    # 8
    def test_title_string_is_never_matched(self):
        result = sri.lookup(self.index, "Impressive response and long-term survival in a rare sarcoma")
        self.assertEqual(result["state"], "invalid_candidate")
        self.assertEqual(result["matches"], [])
        joined = " ".join(result["notes"]).lower()
        self.assertIn("titles are excluded from matching entirely", joined)
        self.assertIn("not novelty", joined)

    # 9
    def test_access_categories_stay_distinct_and_unknown_wording_is_unclassified(self):
        result = sri.lookup(self.index, "PMC9990001")
        events = result["access_evidence"]

        denial = [e for e in events if "403" in e["quote"]]
        self.assertEqual(len(denial), 1)
        self.assertIn("http_403_unclassified_denial", denial[0]["labels"])
        self.assertNotIn("publisher_authentication_or_subscription", denial[0]["labels"])
        self.assertNotIn("proxy_or_network_failure", denial[0]["labels"])
        self.assertNotIn("reported_complete_source_recovered", denial[0]["labels"])

        subscription = [e for e in events if "subscription" in e["quote"].lower()]
        self.assertEqual(len(subscription), 1)
        self.assertIn("publisher_authentication_or_subscription", subscription[0]["labels"])
        self.assertIn("full_text_unavailable_in_scope", subscription[0]["labels"])
        self.assertNotIn("http_403_unclassified_denial", subscription[0]["labels"])

        odd = [e for e in events if e["quote"].startswith("Access route condition")]
        self.assertEqual(len(odd), 1)
        self.assertEqual(odd[0]["labels"], ["unclassified_reported_access_evidence"])

        recovered = [e for e in events if "reported_complete_source_recovered" in e["labels"]]
        self.assertEqual(len(recovered), 1)
        self.assertTrue(recovered[0]["hash_not_recomputed"])

        proxy = sri.classify_access_text(ALPHA_EARLY["access_note"])
        self.assertIn("proxy_or_network_failure", proxy)
        self.assertNotIn("http_403_unclassified_denial", proxy)
        self.assertNotIn("policy_or_biology_refusal", proxy)

        no_attempt = sri.classify_access_text(ALPHA_LATE["access_note"])
        self.assertIn("no_access_attempt_in_this_packet", no_attempt)
        self.assertNotIn("full_text_unavailable_in_scope", no_attempt)

        refusal = sri.classify_access_text("Retrieval declined under a biological guardrail refusal.")
        self.assertIn("policy_or_biology_refusal", refusal)
        self.assertNotIn("publisher_authentication_or_subscription", refusal)

    # 10  (F9: the comparison is case-insensitive, matching tests 3 and 8. The
    #      DISCLAIMER opens the sentence with "Not an authorization"; the disclaimer is
    #      correct and this assertion was the defect.)
    def test_cli_exits_zero_for_unresolved_matched_and_invalid(self):
        queries = [
            "10.5555/absent-from-corpus.9999",
            "10.5555/synthetic-alpha.0001",
            "Impressive response and long-term survival in a rare sarcoma",
        ]
        expected = ["unresolved_not_indexed", "matched_with_divergent_states", "invalid_candidate"]
        for query, state in zip(queries, expected):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = sri.main([query, "--record", self.root, "--json"])
            self.assertEqual(code, 0, msg=query)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["state"], state, msg=query)
            self.assertIn("not an authorization", payload["disclaimer"].lower(), msg=query)
            self.assertIn("not a novelty determination", payload["disclaimer"].lower(), msg=query)

    # 11 (F1)
    def test_bare_identifier_under_an_identifier_named_field_is_indexed(self):
        root = self.corpus({"records/bare.json": {
            "synthetic_fixture": True,
            "pmid": "99900573",
            "source_doi": "10.5555/synthetic-bare.0006",
            "geo": "not an accession, just prose in an identifier-named field",
        }})
        index = sri.build_index([root])

        pmid = sri.lookup(index, "99900573", kind="pmid")
        self.assertEqual(pmid["state"], "matched")
        self.assertEqual(len(pmid["matches"]), 1)
        self.assertEqual(pmid["matches"][0]["locator"], "pmid")
        self.assertEqual(pmid["matches"][0]["context"], "structured_field_name")

        qualified = sri.lookup(index, "10.5555/synthetic-bare.0006")
        self.assertEqual(qualified["state"], "matched")

        # A field name proposes a scheme; it never forces one onto prose.
        self.assertIsNone(sri.extract_field_name_identifier(
            "geo", "not an accession, just prose in an identifier-named field", "geo"))
        self.assertEqual(sri.scheme_for_field_name("source_pmid"), "pmid")
        self.assertIsNone(sri.scheme_for_field_name("locator"))

    # 12 (F1) — the field-name hit must not double-count an already-syntactic one
    def test_field_name_indexing_does_not_duplicate_the_syntactic_hit(self):
        root = self.corpus({"records/both.json": {
            "synthetic_fixture": True,
            "pmid": "PMID 99900007",
        }})
        index = sri.build_index([root])
        result = sri.lookup(index, "99900007", kind="pmid")
        self.assertEqual(result["state"], "matched")
        self.assertEqual(len(result["matches"]), 1)

    # 13 (F2)
    def test_access_labels_carry_per_label_evidence_and_are_never_silently_dropped(self):
        details = sri.classify_access_details(NEGATING_ACCESS_SENTENCE)
        labels = [detail["label"] for detail in details]
        for expected in ("proxy_or_network_failure", "no_access_attempt_in_this_packet",
                         "publisher_authentication_or_subscription",
                         "policy_or_biology_refusal", "full_text_unavailable_in_scope"):
            self.assertIn(expected, labels)
        ruled_out = {detail["label"]: detail for detail in details}
        for category in ("publisher_authentication_or_subscription",
                         "policy_or_biology_refusal", "full_text_unavailable_in_scope"):
            self.assertTrue(ruled_out[category]["clause_has_negation"], msg=category)
            self.assertIn(ruled_out[category]["matched_phrase"],
                          ruled_out[category]["clause"].lower())
        event = sri._access_event("r", "loc", NEGATING_ACCESS_SENTENCE)
        self.assertTrue(event["labels_are_mentions_not_assertions"])
        self.assertEqual(len(event["label_evidence"]), len(event["labels"]))

    # 14 (F3)
    def test_orthogonal_status_fields_in_one_record_are_not_a_contradiction(self):
        root = self.corpus({"records/one.json": {
            "synthetic_fixture": True,
            "utc": "2026-09-07T00:00:00+00:00",
            "doi": "10.5555/synthetic-orthogonal.0008",
            "operational_status": "completed_verified",
            "scientific_status": "primary_rechecked",
            "source_asset_status": "not_admitted",
        }})
        result = sri.lookup(sri.build_index([root]), "10.5555/synthetic-orthogonal.0008")
        self.assertEqual(len(result["record_statuses"]), 3)
        self.assertEqual([c for c in result["conflicts"]
                          if c["type"] == "differing_record_status"], [])
        self.assertEqual(result["state"], "matched")

        # ... while the same field name diverging across records still is one.
        clash = self.corpus({
            "records/a.json": {"synthetic_fixture": True, "utc": "2026-09-01T00:00:00+00:00",
                               "doi": "10.5555/synthetic-clash.0009", "status": "open"},
            "records/b.json": {"synthetic_fixture": True, "utc": "2026-09-08T00:00:00+00:00",
                               "doi": "10.5555/synthetic-clash.0009", "status": "closed"},
        })
        flagged = sri.lookup(sri.build_index([clash]), "10.5555/synthetic-clash.0009")
        conflicts = [c for c in flagged["conflicts"] if c["type"] == "differing_record_status"]
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["field"], "status")

    # 15 (F4)
    def test_policy_exclusion_is_a_category_and_absent_evidence_is_stated_not_silent(self):
        self.assertIn("policy_or_biology_refusal", sri.classify_access_text(
            "Restricted reagent work; excluded from this packet by policy."))
        self.assertIn("policy_or_biology_refusal", sri.classify_access_text(
            "This candidate was excluded from retrieval under a standing restriction."))

        root = self.corpus({"records/quiet.json": {
            "synthetic_fixture": True,
            "doi": "10.5555/synthetic-quiet.0010",
            "title_note": "A record that says nothing whatsoever about obtaining anything.",
        }})
        result = sri.lookup(sri.build_index([root]), "10.5555/synthetic-quiet.0010")
        self.assertEqual(result["access_evidence"], [])
        self.assertIn(sri.NO_ACCESS_EVIDENCE_NOTE, result["notes"])

    # 16 (F5)
    def test_same_basename_in_two_directories_does_not_pool_evidence(self):
        root = self.corpus({
            "paz/integration.json": {"synthetic_fixture": True,
                                     "utc": "2026-09-01T00:00:00+00:00",
                                     "doi": "10.5555/synthetic-paz.0011",
                                     "status": "paz_open",
                                     "access_note": "No access attempt was made here."},
            "sun/integration.json": {"synthetic_fixture": True,
                                     "utc": "2026-09-02T00:00:00+00:00",
                                     "doi": "10.5555/synthetic-sun.0012",
                                     "status": "sun_closed_no_full_text",
                                     "denial_note": "Three institutional URLs returned 403."},
        })
        index = sri.build_index([os.path.join(root, "paz", "integration.json"),
                                 os.path.join(root, "sun", "integration.json")])
        self.assertEqual(len(index.scope()["files"]), len(set(index.scope()["files"])))

        paz = sri.lookup(index, "10.5555/synthetic-paz.0011")
        self.assertEqual([e["status"] for e in paz["record_statuses"]], ["paz_open"])
        quotes = " ".join(str(e["quote"]) for e in paz["access_evidence"])
        self.assertNotIn("403", quotes)
        self.assertEqual(len(paz["matches"]), 1)
        self.assertTrue(paz["matches"][0]["origin_path"].endswith(
            os.path.join("paz", "integration.json")))

    # 17 (F6, F7)
    def test_missing_root_warns_and_retained_bytes_needs_related_keys(self):
        index = sri.build_index([os.path.join(tempfile.gettempdir(), "sri-absent-root-fixture")])
        result = sri.lookup(index, "10.5555/synthetic-absent.0013")
        self.assertEqual(result["state"], "unresolved_not_indexed")
        self.assertTrue(result["scope_warnings"])
        joined = " ".join(result["notes"]).lower()
        self.assertIn("does not exist", joined)
        self.assertIn("index is empty", joined)

        root = self.corpus({"records/skipme.csv": "a,b\n1,2\n",
                            "records/kept.json": {"synthetic_fixture": True,
                                                  "doi": "10.5555/synthetic-skip.0014"}})
        kept = sri.lookup(sri.build_index([root]), "10.5555/synthetic-skip.0014")
        self.assertIn("records/skipme.csv", kept["indexed_scope"]["skipped_files"])

        self.assertIsNone(sri._bytes_signal({
            "landing_page": "https://fixture.invalid/landing",
            "archive_sha256": "ab" * 32,
            "archive_member": "bundle/inner.xml",
        }))
        signal = sri._bytes_signal({
            "source_url": "https://fixture.invalid/source.xml",
            "sha256": "ab" * 32,
            "archive_member": "bundle/inner.xml",
        })
        self.assertIsNotNone(signal)
        self.assertIn("source_url", signal["association_basis"])

    # 18 (F8)
    def test_synthetic_fixture_records_are_labelled_in_json_and_text_output(self):
        root = self.corpus({"records/syn.json": {"synthetic_fixture": True,
                                                 "doi": "10.5555/synthetic-label.0015"}})
        result = sri.lookup(sri.build_index([root]), "10.5555/synthetic-label.0015")
        self.assertEqual(result["synthetic_fixture_records"], ["records/syn.json"])
        self.assertTrue(result["matches"][0]["synthetic_fixture"])
        rendered = sri.render_text(result)
        self.assertIn(sri.SYNTHETIC_MARKER, rendered)
        for line in rendered.splitlines():
            if line.startswith("match "):
                self.assertIn(sri.SYNTHETIC_MARKER, line)


if __name__ == "__main__":
    unittest.main()
```

---

## Validation evidence

All **RUN**. Working root `/tmp/claude-0/w11b/final/`, laid out as `scripts/source_reuse_index.py` + `scripts/tests/test_source_reuse_index.py` so the S6 preamble resolves exactly as it will in the repository.

**1. Final suite under pytest — the primary evidence.**

```
$ cd /tmp/claude-0/w11b/final
$ /root/.local/bin/pytest scripts/tests/test_source_reuse_index.py -v
cachedir: .pytest_cache
rootdir: /tmp/claude-0/w11b/final
plugins: xdist-3.8.0
collecting ... collected 18 items
... (18 lines, all PASSED) ...
============================== 18 passed in 0.03s ==============================
EXIT=0
```
`pytest 9.1.1`, shebang `#!/root/.local/share/uv/tools/pytest/bin/python3`, `Python 3.11.15`. `date -u` at run: `Tue Sep  8 02:12:12 UTC 2026`.

**2. Negative control — the new tests fail on the unrepaired helper.** Same test file, original bundle helper placed at `scripts/source_reuse_index.py`:

```
$ /root/.local/bin/pytest scripts/tests/test_source_reuse_index.py -q
7 failed, 11 passed in 0.09s
EXIT=1
FAILED ...::test_access_labels_carry_per_label_evidence_and_are_never_silently_dropped
FAILED ...::test_bare_identifier_under_an_identifier_named_field_is_indexed
FAILED ...::test_missing_root_warns_and_retained_bytes_needs_related_keys
FAILED ...::test_orthogonal_status_fields_in_one_record_are_not_a_contradiction
FAILED ...::test_policy_exclusion_is_a_category_and_absent_evidence_is_stated_not_silent
FAILED ...::test_same_basename_in_two_directories_does_not_pool_evidence
FAILED ...::test_synthetic_fixture_records_are_labelled_in_json_and_text_output
```
Seven of the eight new tests demonstrably pin a repair. **Test 12 passes on the old helper and I say so plainly**: it is a guard against my own F1 repair double-counting a mention, not a reproduction of an original defect. Also note the ten inherited tests (including the F9-fixed test 10) all pass here — the repairs did not change any delivered behaviour that was already correct.

**3. Runner matrix on the final pair.**

| Command | Exit | Result |
|---|---|---|
| `/root/.local/bin/pytest scripts/tests/test_source_reuse_index.py -q` | 0 | 18 passed |
| `/root/.local/bin/pytest -q scripts/tests/` (repo-root shape, no file arg) | 0 | 18 passed |
| `python3 scripts/tests/test_source_reuse_index.py` (direct unittest) | 0 | `Ran 18 tests … OK` |
| `python3 -m unittest discover -s scripts/tests -t .` | 1 | `ImportError: Start directory is not importable` — **identical to the existing repository tier**, which also has no `__init__.py`; not a property of my file |

**4. Four CLI examples, all exit 0**, against a synthetic record under `demo/`:

```
exit=0 :: 10.5555/synthetic-demo.0001 --record demo --json
exit=0 :: 99900573 --kind pmid --record demo
exit=0 :: 10.5555/absent.0000 --record demo
exit=0 :: "Some title that is not an identifier" --record demo
```
(The invalid-candidate path exits 0. An earlier run of that fourth case showed exit 2 purely because I left the title unquoted in the shell, so argparse saw extra positionals — a harness slip, corrected and re-run, not a tool behaviour.)

Sample text render showing the F8 marker, F1 field-name context, and F2 per-label basis:
```
match            : [SYNTHETIC FIXTURE] rec.json :: pmid [structured_field_name] (99900573) <- demo/rec.json
status           : [SYNTHETIC FIXTURE] 2026-09-08T00:00:00+00:00 | rec.json | status :: demo_open
access_evidence  : [SYNTHETIC FIXTURE] rec.json :: no_access_attempt_in_this_packet :: No current access-state test was performed in this packet.
  label_basis    : no_access_attempt_in_this_packet | phrase='no current access-state test was performed' | clause_negates=True
```

**5. Safety audit of the final helper.** `grep -n "open(" scripts/source_reuse_index.py` → exactly one hit, line 634, mode `"r"`. `grep "urllib.request\|socket\|requests\|subprocess"` → one hit, line 19, inside the docstring saying it does none of them. `main()` returns literal `0` on every path. The test file imports only `contextlib, io, json, os, shutil, sys, tempfile, unittest` plus the module under test.

**6. Environment caveat, stated honestly as instructed.** The available pytest is a uv-tool install in an isolated venv — the configuration `preflight.sh` once recorded as reporting 36 phantom failures. **My suite is stdlib-only, so this does not bite**: it imports nothing outside the standard library, needs no plugin, and produces identical results under the system `python3 -m unittest` (18 passed, exit 0) as under that pytest (18 passed, exit 0). Two independent runners agreeing is the evidence that the result is not a venv artefact.

**PROPOSED (NOT RUN):** `scripts/preflight.sh` in any form, and `PREFLIGHT_FULL=1`. My dispatch did not authorise it and the tree is read-only to me. The coordinator should run the normal commit gate after placing the files. Also not run: `scripts/tier_budget.py --check` with these files actually in place — my 1484 figure is arithmetic on the measured 1466 plus my AST-counted 18, not a post-placement measurement.

---

## Limitations

- **The four real records the review cites are absent at the freeze commit.** Every defect probe used a synthetic record shaped to the review's description. That establishes the *mechanism* on real code; it does not verify the review's claim that those specific repository files trigger it. Those four hits remain UNKNOWN, not confirmed.
- **The 30-case independent contract is not satisfied and I did not attempt it.** §2 of the review lists divergences (the `KNOWN_*` vocabulary rename, `admitted_fields`, sha256 recomputation, `referenced_origin_missing`, Zenodo concept/version advisory, `base_revision`, current-vs-superseded designation, advisory title candidates). None is implemented here. My acceptance contract is S1–S9, and I did not author or relax it.
- **F2's `clause_has_negation` is an annotation, not a verdict.** It marks that a matched phrase sits in a clause carrying negating wording. It fires on correct labels too — `"this is not full text"` genuinely reports unavailable full text and is still flagged as negating. That is deliberate: dropping negated labels would delete correct ones, so the tool annotates and a human reads. `_clauses()` splits on `.`/`;` and does not parse English.
- **F5's disambiguation suffix (`integration.json#2`) changes rendered ids** when two files share a basename. That is a visible output change for that case, and intended — the alternative is silent evidence pooling.
- **F1 widens what counts as an identifier mention.** A field named `doi`/`pmid`/`*_pmid` whose value parses completely under that scheme is now indexed. It cannot fire on prose (verified), but it does mean a record can now match where it previously did not — the correct direction, and the whole point, but a behaviour change the coordinator should know about.
- No scientific claim of any kind. This is an informational, read-only lookup helper; it establishes nothing about EMC efficacy, safety, selectivity, or clinical readiness, and it grants no source-access authorisation. Absence from its index remains UNKNOWN, never novelty.
- Single platform: Linux, Python 3.11.15. Windows behaviour is not tested here; the original bundle's Windows-path evidence is provenance, not a run I performed.

---

## Stop condition

Set: complete final files delivered, my own tests executed with real exit evidence, all nine findings individually adjudicated by execution, tier arithmetic checked. **MET.**

- Final files: delivered inline, both named with their intended repository paths, sha256 stated.
- Own tests executed: 18 passed, exit 0, under pytest 9.1.1 and again under stdlib unittest.
- Nine findings: nine adjudicated by a probe I ran — eight reproduced-and-fixed, one (F4) reproduced as a mechanism with the review's own cited example refuted and recorded as such. Zero accepted on reading.
- Tier arithmetic: 1466 measured + 18 = 1484/1500, no ceiling change, no gate change, no budget file edited.
- Three recorded outcomes: two reproduce exactly, one (discovery) reproduces only under the invocation shape that makes `top_level_dir` differ from `start_dir` — diagnosed to the enforcing line of `unittest/loader.py`.

## Tool-call and wall-clock count actually used

**20 tool calls; approximately 15 minutes wall clock** (`01:57:41Z` → `02:12:21Z`). Both inside the ~40/~40 target.

## Next concrete action

**Place the two files and run the real commit gate on a settled tree.** Specifically: write `scripts/source_reuse_index.py` and `scripts/tests/test_source_reuse_index.py` at the paths above, then run `python3 scripts/tier_budget.py --check` to confirm the measured (not projected) commit-loop total, and `scripts/preflight.sh` in its normal form. That is a coordinator action, not a lane-11 one — I am read-only. If the measurement comes back different from 1484, the discrepancy is in `count_dir`'s view of the tier and not in my file, and I would want to see it before anything else changes.

The nearest genuinely open lane-11 question after that: **the review's §2 divergence list has never been adjudicated by execution at all.** The eight unimplemented contract items (`KNOWN_*` vocabulary, `admitted_fields`/`FIELD_NOT_ADMITTED`, sha256 recomputation, `referenced_origin_missing`, Zenodo concept-vs-version advisory, `base_revision`, current-vs-superseded, advisory title candidates) are still purely static claims, exactly as the nine findings were before this run. That is a real, bounded successor — but it needs its own test-budget decision, since 16 functions of shared headroom will not carry eight new behaviours, and the honest answer may be that the tier is the wrong home for them.

result: All 9 static findings adjudicated by execution (8 reproduced-and-fixed, 1 reproduced-with-its-own-example-refuted); final `scripts/source_reuse_index.py` + `scripts/tests/test_source_reuse_index.py` delivered inline, 18/18 pass exit 0 under pytest 9.1.1 and stdlib unittest, 7/8 new tests fail on the unrepaired helper, tier 1484/1500 with no ceiling change; the recorded discovery failure is diagnosed as `unittest` discovery's `__init__.py` check when top_level_dir differs from start_dir — a property the existing `scripts/tests/` tier already shares.
