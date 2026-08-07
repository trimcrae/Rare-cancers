#!/usr/bin/env python3
"""The literature fetcher must not run the HTML stripper over JSON/XML. ($0, pure stdlib)

⛔ THE DEFECT THIS PINS, measured 2026-08-07 on a real 13-study ClinicalTrials.gov fetch.
`strip_html` deletes from a `<` to the next `>`. ClinicalTrials.gov puts LITERAL angle brackets in
free-text eligibility criteria ("PLT < 100,000/mcL", "prednisone > 10 mg daily"), so each `<` opened
a span that closed at some later `>` and every structural key in between was swallowed.

⚠ WHY IT IS A TEST AND NOT A COMMENT. One failure mode was loud — 10 records stopped parsing. The
other was SILENT: NCT05836571 came back as well-formed JSON, keeping `statusModule`,
`descriptionModule` and `contactsLocationsModule`, while `conditionsModule`, `designModule` and
`eligibilityModule` vanished — with fragments of the eligibility content still present, orphaned.
Nothing raised. That is the shape this repo's own rule names as the dangerous one: the damage
REMOVES fields rather than corrupting them, so every `in` check answers "absent" instead of failing,
and an absent reading gets read as a reading of absence.

⚠ AND THE FIRST DIAGNOSIS WAS WRONG. It blamed HTML-ESCAPED brackets; the synthetic written from
that story did not reproduce the loss. The real artifact settled it — 0 literal `<` and 13 orphaned
`>` left behind. These cases are built from the mechanism that actually reproduces.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lit_fetch_urls as L  # noqa: E402

REAL_SHAPE = json.dumps({"protocolSection": {
    "statusModule": {"overallStatus": "ACTIVE_NOT_RECRUITING"},
    "descriptionModule": {"detailedDescription": "Patients with PLT < 100,000/mcL are excluded"},
    "conditionsModule": {"conditions": ["Sarcoma"]},
    "designModule": {"phases": ["PHASE2"]},
    "eligibilityModule": {"eligibilityCriteria": "prednisone > 10 mg daily", "minimumAge": "18 Years"},
    "contactsLocationsModule": {"locations": []},
}})

ALL_MODULES = ("statusModule", "descriptionModule", "conditionsModule",
               "designModule", "eligibilityModule", "contactsLocationsModule")


def test_the_stripper_really_does_eat_json_keys():
    """The regression guards a real defect, so the defect must still be demonstrable."""
    damaged = L.strip_html(REAL_SHAPE)
    lost = [m for m in ALL_MODULES if m not in damaged]
    assert set(lost) == {"conditionsModule", "designModule", "eligibilityModule"}, lost
    # ⚠ The silent half: content outlives its key, so the wreck still looks like data.
    assert "minimumAge" in damaged
    assert damaged.count("<") == 0


def test_json_is_routed_away_from_the_stripper_under_any_content_type():
    """Header-only detection would miss it: some endpoints serve JSON as text/plain or unlabelled."""
    for ctype in ("application/json", "text/plain", "", "application/xml"):
        assert L._looks_structured(ctype, REAL_SHAPE.encode()), ctype


def test_real_html_is_still_stripped():
    """The fix must not over-correct into 'never strip anything'."""
    html = b"<!doctype html><html><body><p>hello <b>world</b></p></body></html>"
    for ctype in ("text/html", ""):
        assert not L._looks_structured(ctype, html), ctype


def test_the_structured_path_preserves_every_module_and_the_brackets():
    assert L._looks_structured("application/json", REAL_SHAPE.encode())
    p = json.loads(REAL_SHAPE)["protocolSection"]
    assert set(p) == set(ALL_MODULES)
    assert "> 10 mg" in p["eligibilityModule"]["eligibilityCriteria"]
