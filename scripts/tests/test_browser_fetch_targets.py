#!/usr/bin/env python3
"""The caller-supplied-target seam in the browser fetcher, asserted rather than described.

⛔ WHY THIS FILE EXISTS. `venue_policy_browser_fetch.py` grew a seam that lets a caller replace its
hardcoded venue corpus via environment variables, and the only thing standing between that seam and
a mislabelled record is prose. This repository has already paid for a property that was documented
and never checked: `fleet_armed.CENSUS_LANE` was described correctly in three places and wired to a
name nothing used, so the design read as safe while the one artifact it protected was dropped.

So the properties that actually matter here are asserted:

  * with no env set, NOTHING changes -- the venue corpus and its output path are what run;
  * a supplied corpus REPLACES the built-in one and redirects the output, and the payload records
    that it did, because a run whose targets were swapped must not read like a venue-corpus run;
  * a malformed corpus FAILS THE RUN rather than silently falling back to the venue corpus, which
    would publish 25 publisher policy pages under whatever slug the caller chose;
  * a non-http target is refused, because `file://` and `data:` are not pages.

⚠ Nothing here launches a browser. The seam is the unit under test.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import venue_policy_browser_fetch as B  # noqa: E402

ENV_VARS = (
    "BROWSER_TARGETS_JSON",
    "BROWSER_OUT",
    "BROWSER_HARVEST_LINKS",
    "BROWSER_HARVEST_ALL_LINKS",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_no_env_leaves_the_venue_corpus_and_its_output_path_untouched():
    targets, out, note = B._targets_from_env()
    assert targets is B.TARGETS
    assert out == B.OUT
    assert note is None, "an unswapped run must not claim its targets were overridden"


def test_a_supplied_corpus_replaces_the_builtin_one_and_says_so(monkeypatch):
    monkeypatch.setenv("BROWSER_TARGETS_JSON", '{"a": "https://example.org/a"}')
    targets, out, note = B._targets_from_env()
    assert targets == {"a": "https://example.org/a"}
    assert not set(targets) & set(B.TARGETS), "the venue corpus must not survive a replace"
    assert out != B.OUT, "a swapped run must not overwrite the venue corpus artifact"
    assert note and "REPLACED" in note


def test_the_output_path_is_redirectable(monkeypatch):
    monkeypatch.setenv("BROWSER_TARGETS_JSON", '{"a": "https://example.org/a"}')
    monkeypatch.setenv("BROWSER_OUT", "research/literature/somewhere-else.json")
    _, out, _ = B._targets_from_env()
    assert out == "research/literature/somewhere-else.json"


@pytest.mark.parametrize(
    "bad",
    [
        "not json at all",
        "[]",           # a list is not a name -> url map
        "{}",           # an empty corpus would silently fetch nothing
        '"a string"',
        '{"a": 7}',                     # not a URL
        '{"a": "file:///etc/passwd"}',  # not a page
        '{"a": "data:text/html,x"}',
        '{"a": "ftp://example.org"}',
    ],
)
def test_a_malformed_corpus_fails_the_run_rather_than_falling_back(monkeypatch, bad):
    """⛔ THE FALLBACK IS THE BUG. Refusing loudly is the only safe direction: a silent fall back
    to TARGETS would publish the venue corpus under the caller's name, which is this workflow's
    documented mislabelled-record failure arriving through a new door."""
    monkeypatch.setenv("BROWSER_TARGETS_JSON", bad)
    with pytest.raises(SystemExit):
        B._targets_from_env()


def test_whitespace_only_env_is_treated_as_unset(monkeypatch):
    monkeypatch.setenv("BROWSER_TARGETS_JSON", "   ")
    targets, out, note = B._targets_from_env()
    assert targets is B.TARGETS and out == B.OUT and note is None


def test_link_harvesting_defaults_to_the_builtin_list_and_extends_from_env(monkeypatch):
    assert B._harvest_names() == set(B.HARVEST_LINKS_FROM)
    monkeypatch.setenv("BROWSER_HARVEST_LINKS", "one, two ,,three")
    assert B._harvest_names() == set(B.HARVEST_LINKS_FROM) | {"one", "two", "three"}


def test_the_link_filter_is_on_by_default_and_can_be_turned_off(monkeypatch):
    """The default filter is tuned to publisher navigation. A caller harvesting a registry archive
    page wants every link -- an errata PDF named by its date matches none of the filter's words."""
    assert B._link_filter() is B.LINK_WORDS
    assert B.LINK_WORDS.search("07/11/2019 Errata") is None, (
        "if this ever matches, the reason the opt-out exists has changed and this test should say so"
    )
    for truthy in ("1", "true", "yes"):
        monkeypatch.setenv("BROWSER_HARVEST_ALL_LINKS", truthy)
        assert B._link_filter() is None
    monkeypatch.setenv("BROWSER_HARVEST_ALL_LINKS", "0")
    assert B._link_filter() is B.LINK_WORDS


def test_the_scope_rule_is_still_stated_in_the_module(monkeypatch):
    """⚠ NOT STYLE POLICING. The seam turns a fixed public-page corpus into an arbitrary one, and
    the only thing that keeps 'public pages only, never a paywall route' attached to it is the
    sentence next to the seam. If someone deletes it, that constraint stops travelling with the
    code that needs it."""
    src = open(os.path.join(ROOT, "scripts", "venue_policy_browser_fetch.py"), encoding="utf-8")
    with src as fh:
        text = fh.read()
    assert "not a paywall route" in text
    assert "UNREACHABLE" in text
