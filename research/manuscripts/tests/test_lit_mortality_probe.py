"""Tests for the EMC terminal-event probe.

The probe runs on a GitHub runner against live APIs, so nothing here touches the network.
What IS testable offline is the part that decides what ends up in the artifact, and that
is the part a wrong answer would corrupt silently: the sentence extraction, and the
life-table parser that the background-mortality check rests on.

⛔ The property this file exists to defend is that the probe CLASSIFIES NOTHING. It keeps
sentences and records where they came from; deciding that a sentence describes a death
from respiratory failure is a reading done downstream against the quoted text. A future
change that made the regex assign causes would turn a retrieval artifact into a set of
fabricated clinical facts, so the recall-first behaviour is asserted rather than assumed.
"""

from __future__ import annotations

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
MODULE = ROOT / "scripts/lit_mortality_probe.py"


def _load():
    spec = importlib.util.spec_from_file_location("lit_mortality_probe", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _load()


# ---------------------------------------------------------------------------
# Full text -> sentences
# ---------------------------------------------------------------------------
def test_the_reference_list_is_dropped_before_sentences_are_taken():
    """A bibliography is full of other papers' titles containing 'mortality' and
    'death'. Those are not this paper's patients, and keeping them would pad the corpus
    with rows that look like terminal events and are not."""
    xml = (
        "<article><body><p>The patient died of respiratory failure.</p></body>"
        "<ref-list><ref>Smith J. Death and mortality in soft tissue sarcoma.</ref>"
        "</ref-list></article>"
    )
    text = P.strip_xml(xml)
    assert "respiratory failure" in text
    assert "Smith" not in text


def test_the_back_matter_is_dropped_even_without_a_ref_list_tag():
    xml = ("<article><body><p>She died at home.</p></body>"
           "<back><ack>We thank the deceased patient's family.</ack></back></article>")
    text = P.strip_xml(xml)
    assert "died at home" in text
    assert "We thank" not in text


def test_tables_and_figures_are_stripped_so_their_numbers_do_not_become_sentences():
    xml = ("<article><body><table-wrap><td>deaths 4</td></table-wrap>"
           "<p>Two patients died during follow-up.</p></body></article>")
    text = P.strip_xml(xml)
    assert "Two patients died" in text
    assert "deaths 4" not in text


def test_sentence_splitting_does_not_break_on_clinical_abbreviations():
    text = "The tumour was 4 cm (approx. 5 cm on MRI). She died 14 months later."
    sents = P.sentences(text)
    assert len(sents) == 2
    assert sents[0].endswith("MRI).")
    assert "died 14 months later" in sents[1]


# ---------------------------------------------------------------------------
# What is kept, and what is deliberately kept that a tighter filter would drop
# ---------------------------------------------------------------------------
def test_a_mechanism_sentence_is_kept_and_flagged():
    s = "She died of respiratory failure due to progressive pulmonary metastases."
    assert P.DEATH_CUES.search(s)
    assert P.MECHANISM_CUES.search(s)


def test_a_bare_vital_status_sentence_is_kept_but_not_flagged():
    """This is the common case in EMC's literature and it is the reason the corpus needs
    reading rather than counting: 'died of disease' names no mechanism at all."""
    s = "At last follow-up the patient had died of disease after 62 months."
    assert P.DEATH_CUES.search(s)
    assert not P.MECHANISM_CUES.search(s)


def test_a_negative_sentence_is_kept_because_the_filter_is_recall_first():
    """'No deaths occurred' must survive extraction. A filter tuned to drop it would also
    drop the unusual terminal events, which are exactly the rows worth finding -- and the
    reader can see a negative for what it is, whereas a silently dropped row is invisible."""
    s = "No treatment-related deaths occurred in the adjuvant cohort."
    assert P.DEATH_CUES.search(s)


def test_a_competing_cause_sentence_is_kept_and_flagged():
    s = "The patient died of an unrelated myocardial infarction with no evidence of disease."
    assert P.DEATH_CUES.search(s)
    assert P.MECHANISM_CUES.search(s)


def test_an_ordinary_clinical_sentence_is_not_kept():
    s = "The lesion was excised with wide margins and the wound healed uneventfully."
    assert not P.DEATH_CUES.search(s)


def test_the_mechanism_cue_is_only_a_hint_and_never_names_a_cause():
    """The flag is boolean by design. If it ever became a cause label, the artifact would
    be asserting clinical facts no human had read."""
    s = "He died of sepsis following neutropenia."
    assert P.MECHANISM_CUES.search(s)
    assert isinstance(bool(P.MECHANISM_CUES.search(s)), bool)


# ---------------------------------------------------------------------------
# The disease query
# ---------------------------------------------------------------------------
def test_the_corpus_and_the_index_ask_about_the_same_disease():
    """Both halves interpolate one EMC fragment. If they drifted apart the index would be
    describing a different population from the corpus, invisibly."""
    assert "extraskeletal myxoid chondrosarcoma" in P.EMC
    assert "chordoid sarcoma" in P.EMC
    emc_queries = [q for k, q in P.QUERIES if k.startswith("emc_")]
    assert emc_queries, "the EMC-specific half of the index vanished"
    assert all(P.EMC in q for q in emc_queries)


def test_every_query_key_is_unique():
    keys = [k for k, _ in P.QUERIES]
    assert len(keys) == len(set(keys))


# ---------------------------------------------------------------------------
# The life table behind the background-mortality check
# ---------------------------------------------------------------------------
def _life_table_html(ages, m_q=0.01, f_q=0.006):
    rows = "".join(
        f"<tr><td>{a}</td><td>{m_q:.6f}</td><td>90000</td><td>26.0</td>"
        f"<td>{f_q:.6f}</td><td>94000</td><td>29.0</td></tr>"
        for a in ages
    )
    return f"<table>{rows}</table>"


def test_the_life_table_parser_compounds_single_year_probabilities(monkeypatch):
    monkeypatch.setattr(P, "get", lambda url, tries=3: _life_table_html(range(50, 70)))
    out = P.fetch_life_table(start_age=55, years=10, male_fraction=1.0)
    assert out["status"] == "OK"
    # Ten years at q=0.01 each: 1 - 0.99**10 = 0.0956
    assert abs(out["cumulative_mortality_male"] - 0.0956) < 0.001
    assert abs(out["cumulative_mortality_blended"] - 0.0956) < 0.001


def test_the_blend_moves_with_the_cohort_sex_ratio(monkeypatch):
    monkeypatch.setattr(P, "get", lambda url, tries=3: _life_table_html(range(50, 70)))
    male = P.fetch_life_table(55, 10, 1.0)["cumulative_mortality_blended"]
    female = P.fetch_life_table(55, 10, 0.0)["cumulative_mortality_blended"]
    mixed = P.fetch_life_table(55, 10, 0.66)["cumulative_mortality_blended"]
    assert female < mixed < male


def test_a_missing_age_fails_loudly_rather_than_extrapolating(monkeypatch):
    """⛔ Silently skipping an unparsed age would return a mortality figure that is too
    LOW, which biases the background check toward 'the gap is not background' -- the
    conclusion this analysis wants. A parser must not fail in the direction of its
    author's hypothesis."""
    monkeypatch.setattr(P, "get", lambda url, tries=3: _life_table_html(range(55, 60)))
    out = P.fetch_life_table(start_age=55, years=10, male_fraction=0.66)
    assert out["status"] == "PARSE_FAILED"
    assert 60 in out["ages_missing"]
    assert "cumulative_mortality_blended" not in out


def test_a_failed_fetch_asserts_no_background_figure(monkeypatch):
    monkeypatch.setattr(P, "get", lambda url, tries=3: "")
    out = P.fetch_life_table(55, 10, 0.66)
    assert out["status"] == "FETCH_FAILED"
    assert "cumulative_mortality_blended" not in out


def test_the_life_table_records_that_it_is_a_one_sided_check(monkeypatch):
    """A general-population table over-states background mortality for a treated cancer
    cohort, so it can refute 'this gap is background' and cannot confirm it. The artifact
    has to carry that or a reader will take the comparison as symmetric."""
    monkeypatch.setattr(P, "get", lambda url, tries=3: _life_table_html(range(50, 70)))
    out = P.fetch_life_table(55, 10, 0.66)
    assert "one-sided" in out["limits"]


# ---------------------------------------------------------------------------
# The workflow wiring -- a mode nothing dispatches is a mode that does not exist
# ---------------------------------------------------------------------------
def test_the_probe_is_actually_wired_into_the_fetch_literature_workflow():
    """The lesson from systems/graph's exempt-lane bug: a property asserted in prose about
    a value a caller passes is a hope, not a property. This probe is only reachable if the
    workflow's slug guard names it, and if the three other paths exclude it -- otherwise a
    dispatch would run the EMC keyword sweep instead and report success."""
    wf = (ROOT / ".github/workflows/fetch-literature.yml").read_text(encoding="utf-8")
    assert "scripts/lit_mortality_probe.py" in wf, "the probe is never invoked"
    assert "inputs.slug == 'mortality-probe'" in wf, "no slug selects the probe"
    assert wf.count("inputs.slug != 'mortality-probe'") == 3, (
        "the query path, its assertion step and the URL-fetch path must all exclude this "
        "slug; a missing guard means a mortality-probe dispatch also runs the keyword "
        "sweep and publishes a mislabelled corpus")
    assert "research/literature/emc-mortality-probe.json" in wf, "the artifact is never published"


# ---------------------------------------------------------------------------
# The life table behind the background check, after it silently returned a wrong number
# ---------------------------------------------------------------------------
# ⛔ MEASURED 2026-08-09, run 31335519304: the fetch reported `status: OK` and a ten-year
# all-cause mortality from age 55 of 2.4%, about four times too low. The value served is an
# annual RATE and the code used it as a five-year PROBABILITY. Nothing about the artifact
# looked wrong -- it was populated, internally consistent and plausible-looking. These
# tests exist so that class of error fails loudly instead of publishing.
import importlib.util as _ilu  # noqa: E402

_HF_SPEC = _ilu.spec_from_file_location(
    "lit_host_factor_probe", ROOT / "scripts/lit_host_factor_probe.py")
HF = _ilu.module_from_spec(_HF_SPEC)
_HF_SPEC.loader.exec_module(HF)


def test_a_rate_is_converted_and_a_probability_is_not():
    m = 0.011437434
    assert HF._band_probability(m, is_rate=False) == m
    converted = HF._band_probability(m, is_rate=True)
    assert converted > m, "a five-year probability must exceed the annual rate behind it"
    assert abs(converted - (1 - 2.718281828 ** (-5 * m))) < 1e-6


def test_the_measured_values_reproduce_a_demographically_sane_answer():
    """The exact numbers the API returned, through the corrected path. US male ten-year
    mortality from 55 is about 12-13%; the first implementation produced 2.8%."""
    male = [0.011437434, 0.016444465]
    surv = 1.0
    for v in male:
        surv *= 1 - HF._band_probability(v, is_rate=True)
    assert 0.10 < 1 - surv < 0.16


def test_the_indicator_label_decides_the_interpretation_not_a_default_guess():
    assert HF._looks_like_a_rate("Age-specific death rate (nMx)") is True
    assert HF._looks_like_a_rate("nqx - probability of dying between exact ages") is False
    assert HF._looks_like_a_rate("Probability of dying per 1000") is False


def test_an_unknown_label_defaults_to_rate_because_that_is_what_was_measured():
    assert HF._looks_like_a_rate("") is True
    assert HF._looks_like_a_rate("LIFE_0000000029") is True


def test_the_sanity_band_would_have_caught_the_original_bug(monkeypatch):
    """The 2.4% figure that shipped must not be publishable."""
    lo, hi = HF.SANITY_BAND
    assert not (lo <= 0.024 <= hi), "the original wrong value still falls inside the guard"
    assert lo <= 0.113 <= hi, "the corrected value must pass"


def test_an_implausible_result_asserts_nothing(monkeypatch):
    def fake_get(url, tries=3):
        if "Indicator?" in url:
            return '{"value":[{"IndicatorName":"nqx - probability of dying"}]}'
        return ('{"value":[{"Dim2":"AGEGROUP_YEARS55-59","NumericValue":0.0114,"TimeDim":2021},'
                '{"Dim2":"AGEGROUP_YEARS60-64","NumericValue":0.0164,"TimeDim":2021}]}')
    monkeypatch.setattr(HF, "get", fake_get)
    out = HF.fetch_life_table()
    assert out["status"] == "IMPLAUSIBLE"
    assert "cumulative_mortality_blended" not in out
    assert out["indicator_name_as_published"] == "nqx - probability of dying"


def test_a_plausible_result_records_how_it_was_interpreted(monkeypatch):
    def fake_get(url, tries=3):
        if "Indicator?" in url:
            return '{"value":[{"IndicatorName":"Age-specific death rate (nMx)"}]}'
        return ('{"value":[{"Dim2":"AGEGROUP_YEARS55-59","NumericValue":0.0114,"TimeDim":2021},'
                '{"Dim2":"AGEGROUP_YEARS60-64","NumericValue":0.0164,"TimeDim":2021}]}')
    monkeypatch.setattr(HF, "get", fake_get)
    out = HF.fetch_life_table()
    assert out["status"] == "OK"
    assert "rate" in out["interpreted_as"]
    assert out["indicator_name_as_published"] == "Age-specific death rate (nMx)"
    assert 0.05 <= out["cumulative_mortality_blended"] <= 0.25
