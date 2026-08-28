#!/usr/bin/env python3
"""The RELATION half of the fusion-partner synthesis's claims, bound to the artifact that decides it.

⛔⛔ WHY THIS FILE IS NOT MORE NUMBER CHECKS — THE GAP WAS MEASURED, NOT ARGUED.
Round 6 of this paper's hardening series (2026-08-27, seat records under
`research/autonomy/review-seats/PUB-FUSION-PARTNER-053a821102c352e74c0f3f4c125277e7ff183191*.json`)
ran five blind seats over one pinned commit. The arithmetic seat re-derived **140 printed
quantities** from the artifacts — all 44 arm records, all 13 Fisher p-values, every additive
identity, every Wilson bound — with **ZERO mismatches**, and ran the generator's verify mode, the
122-test prose guard beside this file and its 9-test mutation suite clean. The same tree yielded
**three blockers and not one of them was a number**:

  * a cardinal written as the WORD "two" — §5 asserted that two series ran a multivariable model
    while naming one, and contradicted itself inside the same sentence;
  * a COMPARATIVE — §3.4 opened "Two series, both larger than any cohort that could be pooled here",
    when both named series ARE cohorts this synthesis pools;
  * an unsourced claim about what THE FIELD quotes — "below the ≈27 % the field routinely quotes",
    at four sites, with no source for the quoting practice held anywhere and the two sources in this
    paper's own reference list that state a general TAF15 share both giving about 20 %.

That is `paper-hardening` §8a's diagnosis with a measurement under it: **a claim is a QUANTITY and a
RELATION, and the guard set was built on the quantity half.** Counts-as-words, comparatives,
superlatives and attributions had no instrument at all, so every one of them could drift while the
whole numbers layer stayed green. Filed as ledger item `AUT-PROP-012`.

★ WHAT EACH ASSERTION IS BOUND TO, AND WHY THAT MATTERS MORE THAN THE ASSERTION COUNT.
Every row below computes its expectation from `emc-fusion-partner-pooling.json` — a count from a
PREDICATE over the cohort records (`sum(1 for c in cohorts if "multivariable_result" in c)`), a
maximum from `n_assessable` over a pooled roster, a membership from `analyses.*.pooled_cohorts` /
`cohorts_pooled`, an attribution from `analyses.C_partner_prevalence.external_reported_share`.
⛔ Nothing here compares the prose to a literal typed into this file. A count that changes because a
cohort was added moves the expectation with it, which is exactly what the typed-roster defect of
2026-08-26 did not do.

⛔ AND EVERY ASSERTION BINDS THE SITE, NEVER THE DOCUMENT (`paper-hardening` §6). A guard that asks
"is the right word in here anywhere" cannot see drift: "the one series that ran a multivariable
model" stands at EIGHT sites across the two prose documents, so a corruption at one of them leaves
the other seven and an `in` test passes. Each row therefore captures the word out of the
CONSTRUCTION that states it and checks every match, exactly as the quantity guard beside it does.

⛔ THE FORBIDS ARE SCOPED BY A PROPERTY, NOT BY A FILE LIST (`paper-hardening` §8b.2: six of eleven
list-scoped fixes regressed at a sibling the fix did not name; no predicate-scoped one did). The
scope is *every prose document of this synthesis whose front matter does not call it a register* —
because a correction register's whole job is to hold superseded statements verbatim, so forbidding
the retracted construction there would red on true input, which is worse than not guarding at all
(`paper-hardening` §8b.1). A third manuscript added tomorrow is in scope without anybody remembering
it; `emc-fusion-partner-correction-register.md` is out of scope for as long as it says `kind:
register` and no longer.

⭐⭐ MEASURED, 2026-08-28, BY THE COMMITTED HARNESS: 89 of 89 mutations caught, none survived,
positive control green, every one single-site. `mutate_fusion_partner_guard.py` beside this file
carries all of them; 24 are this module's, and it now runs the two guard modules SEPARATELY so its
output names which one fired. **17 of the 24 are caught by this module ALONE** — the quantity guard
is green on every one of them, which is the evidence that these bindings read a surface nothing else
reaches. Among the 17: the round-6 blocker restored verbatim at its §5 site ("the one series" ->
"either of the two"), the same count drifting at §3.8 four sections away (the one-of-a-pair half),
the retracted §3.4 comparative put back in both of its branches, a uniqueness claim inverted by
naming a real cohort of this synthesis that publishes no time-to-event analysis, "most-quoted" and
"usually attributed to" restored with every digit and every PMID on the page left correct, and the
external share re-attributed from reference [12] to reference [15] — a real reference of this
manuscript, so `lint_citations` stays green and only this file can see it. The other 7 fire both
guards, which is expected where the relation is carried by a digit.
⛔ ONE HALF OF ONE ASSERTION IS NOT EXERCISED AND IS RECORDED RATHER THAN COUNTED:
`test_the_larger_of_the_pooled_outcome_cohorts_is_the_one_that_declines_the_attribution` also
asserts that the LARGER pooled cohort is the one carrying `multivariable_result`, and that half
lives entirely in the artifact — no prose mutation can reach it, because this harness mutates prose.
Making Agaram 2014 the larger cohort would need a generator mutation, which this harness does not
do. The count half of that same test is mutated and caught.

⚠ THE DOCUMENTS THIS MODULE READS ARE NAMED HERE ON PURPOSE, AND THAT IS NOT DECORATION.
It reads `emc-fusion-partner-stratification.md` and `emc-fusion-partner-correction-register.md`,
and it resolves both AT RUNTIME through `quantities.PROSE_DOCUMENTS` — which is the right way to
scope them and is invisible to `research/manuscripts/claim_coverage.py`, because the census decides
which document a guard reads by looking for its BASENAME in the guard's source. Measured on this
file's first run: the census reported the manuscript at 78 of 270 sentences before and after the
module existed, unchanged, because no string in it named the document. That is `paper-hardening`
§8b.1e — a pattern composed at runtime is invisible to anything that reads source — one level up,
with the DOCUMENT rather than the regex as the thing composed. ⛔ Naming them is only honest because
this module genuinely opens them; naming a document a guard does not read is how the fusion-partner
census once credited 82 sentences to a guard that opened none of them.

⚠ WHAT THIS FILE DOES NOT COVER, STATED HERE RATHER THAN LEFT TO BE INFERRED.
`test_no_claim_about_the_fields_practice_goes_unsourced` catches an ASCRIPTION of a quoting habit to
the field. It cannot catch a claim about the field that carries no frequency word and names no
source — "the literature carries point figures" is that shape, and it is true of the two sources the
artifact holds, which is why it stands. The general problem is not mechanisable from anything on
disk: deciding what the field says needs a corpus this repository does not have. The witness that
WOULD settle it is a committed record of retrieved sources stating the claim, of the shape
`analyses.C_partner_prevalence.external_reported_share.sources` — quote, PMCID, DOI, section — and
until a claim has one, the honest form is to name the sources instead of the field.
"""
from __future__ import annotations

import io
import os
import re

import pytest

# ⛔ ONE HOME FOR EACH HELPER. `_word` already exists in the quantity guard beside this file, where
# it renders §8's cache-slug count, and it RAISES on an unmapped integer rather than falling back to
# digits — the property that makes it safe to bind a count that reaches the page as a word. A second
# copy here would be a second thing to extend, and the two would disagree the first time a count
# passed fourteen. Same for the prose loader, the flattener and the published-p renderer: this file
# asserts different things about the SAME text the quantity guard reads, so they must read it
# identically or a site bound here could be a site that guard never sees.
import test_fusion_partner_prose_matches_its_artifact as quantities

_flat = quantities._flat
_word = quantities._word
_pubp = quantities._pubp
_by_id = quantities._by_id
PROSE_DOCUMENTS = quantities.PROSE_DOCUMENTS

pytestmark = pytest.mark.committed_artifact

OUT = "outcome_by_partner"

# =================================================================================================
# The scan domains.
# =================================================================================================

_FRONT_MATTER_KIND = re.compile(r"^---\s*$.*?^kind:\s*(\S+)\s*$.*?^---\s*$",
                                re.MULTILINE | re.DOTALL)


def _kind(path):
    """The `kind:` this document declares in its own front matter.

    ⛔ RAISES RATHER THAN DEFAULTING. The forbid scope below is *documents that are not registers*,
    so a document whose kind cannot be read would silently pick one side or the other — and the side
    a default picks is the one that guards nothing.
    """
    m = _FRONT_MATTER_KIND.search(io.open(path, encoding="utf-8").read())
    if not m:
        raise AssertionError(
            f"{os.path.basename(path)} has no readable `kind:` in its front matter, so this guard "
            "cannot decide whether it is a document that ASSERTS claims or one that RECORDS "
            "corrections. Restore the front matter; do not widen the scope to cover it blind.")
    return m.group(1)


def _asserting_documents():
    """Every prose document of this synthesis that states claims in its own voice.

    ★ THE PREDICATE IS `kind != register`, and the reasoning is the whole reason the forbids can
    exist. `emc-fusion-partner-correction-register.md` is `kind: register`; it quotes twenty
    superseded statements verbatim, including the exact comparative and the exact field-practice
    claim these forbids catch, because a correction that drops the wording it corrects is not a
    correction. A forbid that read it would go red on a correct tree.
    """
    return tuple(p for p in PROSE_DOCUMENTS if _kind(p) != "register")


@pytest.fixture(scope="module")
def flat():
    """Both prose documents, flattened — the domain the REQUIRE rows read."""
    return quantities._flat(quantities._load_prose())


@pytest.fixture(scope="module")
def asserting():
    """The claim-making documents only, flattened one by one — the domain the FORBID rows read.

    Kept per-document rather than concatenated so a failure can name the file.
    """
    return {os.path.basename(p): _flat(io.open(p, encoding="utf-8").read())
            for p in _asserting_documents()}


@pytest.fixture(scope="module")
def art():
    return quantities._load_artifact()


# =================================================================================================
# A · COUNT-WORDS — a cardinal spelled out is still a count, and it is the one round 6 broke.
#
# Each row is (what, pattern, count) where `count` is a PREDICATE over the artifact and `pattern`
# captures the spelled-out cardinal out of the construction that states it. ⛔ The predicate is the
# point: "the two series that ran a multivariable model" was false because one cohort record carries
# `multivariable_result`, and no list typed anywhere would have moved when a second one did.
# =================================================================================================


def _n_multivariable(a):
    """Cohorts whose record carries a published multivariable model. Today: Huang 2023 alone."""
    return sum(1 for c in a["cohorts"] if "multivariable_result" in c)


def _outcome(a):
    return [c for c in a["cohorts"] if c["endpoint"] == OUT]


def _n_outcome(a):
    return len(_outcome(a))


def _n_outcome_with_event_counts(a):
    """Outcome cohorts publishing per-partner event counts, i.e. carrying `strata`.

    ⚠ NOT the same predicate as "pooled". Suemitsu 2025 carries `counts` flagged
    `_counts_are_context_only` and Paioli 2021 publishes p-values alone, so both test the partner
    against outcome and neither supplies an event count — which is exactly what §1.2's sentence
    says, and exactly the distinction a count typed by hand loses.
    """
    return sum(1 for c in _outcome(a) if "strata" in c)


def _n_pooled_outcome(a):
    return len(a["analyses"]["B_outcome_by_partner"]["pooled_cohorts"])


def _n_pooled_prevalence(a):
    return len(a["analyses"]["C_partner_prevalence"]["cohorts_pooled"])


def _n_external_share_sources(a):
    return len(a["analyses"]["C_partner_prevalence"]["external_reported_share"]["sources"])


COUNT_WORDS = [
    # ⭐ THE BLOCKER ITSELF, AT ALL EIGHT OF ITS SITES. §5 read "in either of the two series that ran
    # a multivariable model (Huang 2023)" for three days — a cardinal contradicting the parenthesis
    # beside it — while every number on the page was right and every gate was green.
    ("the number of series that ran a multivariable model",
     r"the ([a-z]+) series that ran (?:a multivariable|that) model",
     _n_multivariable),
    # §1.2's evidence table states the whole outcome roster and then the sub-count that publishes
    # counts. Binding them apart would let the pair drift into a contradiction the way §5's did.
    ("the number of series testing the partner against outcome",
     r"([A-Za-z]+) series test the partner against outcome",
     _n_outcome),
    ("the number of outcome series publishing per-partner event counts",
     r"only ([a-z]+) publish per-partner event counts",
     _n_outcome_with_event_counts),
    ("the number of cohorts publishing EMC outcome event counts by partner",
     r"([A-Za-z]+) cohorts publish EMC outcome event counts",
     _n_outcome_with_event_counts),
    ("the number of cohorts that publish event counts by partner, as §2.3a and §5 state it",
     r"the only ([a-z]+) cohorts that publish event counts by partner",
     _n_outcome_with_event_counts),
    ("the number of cohorts publishing partner-stratified event counts",
     r"the ([a-z]+) cohorts publishing partner-stratified event counts",
     _n_outcome_with_event_counts),
    # ⭐ THE TWO COUNTS §3.4's REPAIRED OPENING RESTS ON. The retracted sentence claimed both series
    # were larger than anything poolable here; the replacement claims the opposite — that each is
    # inside one of this synthesis's own pools — so both roster sizes are now load-bearing prose.
    ("the size of the outcome pool, where §3.4 places Huang 2023 inside it",
     r"one of the ([a-z]+) cohorts pooled in §3\.3",
     _n_pooled_outcome),
    ("the size of the prevalence pool, where §3.4 places Paioli 2021 inside it",
     r"one of the ([a-z]+) pooled in §3\.5",
     _n_pooled_prevalence),
    # ⭐ THE COUNT THAT CARRIES THE REPAIR OF THE FIELD-ATTRIBUTION BLOCKER. §3.5 says how many of
    # this paper's own references state a general TAF15 share; the artifact holds exactly those
    # sources, with their quotes and DOIs. If a third is found the sentence must move with it.
    ("the number of the paper's own references stating a general TAF15 share",
     r"[Tt]he ([a-z]+) sources in the reference list that give a general TAF15 share",
     _n_external_share_sources),
]


@pytest.mark.parametrize("what,pattern,count", COUNT_WORDS, ids=[r[0] for r in COUNT_WORDS])
def test_every_count_the_prose_spells_out_is_the_count_the_artifact_holds(what, pattern, count,
                                                                         flat, art):
    """⛔ EVERY SITE, AND THE COMPARISON IS CASE-FOLDED BECAUSE THE WORD OPENS SENTENCES.

    "Two cohorts publish EMC outcome event counts" opens §3.3 and sits mid-sentence in §2.3a's
    quotation of it. Capitalisation is a typographic fact about position; the count is the claim.

    ⛔ AND A LOST MATCH IS A FAILURE, NOT A PASS. A pattern that stops matching is a guard that has
    silently stopped guarding — which is how §5's cardinal survived a repair that replaced the
    continuation of its own sentence. When this fires, check the MEANING before the regex: re-anchor
    only if the sentence says the same thing in different words.
    """
    expected = _word(count(art))
    found = re.findall(pattern, flat)
    assert found, (
        f"nothing in this synthesis's prose matches the construction that states {what} "
        f"(/{pattern}/). Either the sentence was reworded — check the MEANING before the regex — or "
        "the claim was dropped.")
    wrong = [f for f in found if f.casefold() != expected.casefold()]
    assert not wrong, (
        f"{what}: the artifact gives {expected!r} and the prose spells {wrong!r} at {len(wrong)} of "
        f"its {len(found)} site(s). The count is derived from the cohort records, not typed — fix "
        "the prose, or fix the generator and regenerate. Never edit the predicate to match the "
        "page.")


# =================================================================================================
# B · COMPARATIVES AND SUPERLATIVES over this synthesis's OWN pool.
#
# ⛔ These are decidable and were decided by nothing. §3.4's retracted opening — "Two series, both
# larger than any cohort that could be pooled here" — is false against two lists in the artifact,
# and it survived four rounds because a superlative carries no digit for a numbers guard to read.
# =================================================================================================

_NAMED_SERIES = re.compile(r"\b([A-Z][a-z]+(?:-[A-Z][a-z]+)?)\s+((?:19|20)\d{2})\b")


def _slug(name, year):
    return f"{name.lower()}-{year}"


def _size(c):
    """A cohort's size as the artifact records it, whichever field its endpoint uses.

    ⚠ RAISES rather than returning 0 for a cohort with neither. A missing size silently makes a
    cohort the SMALLEST, so a maximum taken over a roster containing one would be wrong in the
    direction that keeps the guard quiet.
    """
    for field in ("n_assessable", "n_tested"):
        if c.get(field) is not None:
            return int(c[field])
    raise AssertionError(
        f"cohort {c['id']} records neither `n_assessable` nor `n_tested`, so no size comparison "
        "over a roster containing it can be decided. Add the field to the generator.")


def _largest(a, ids):
    """The id of the largest cohort in `ids`, and its size. Ties are an error, not a coin toss."""
    sizes = sorted(((_size(_by_id(a)[i]), i) for i in ids), reverse=True)
    assert len(sizes) < 2 or sizes[0][0] != sizes[1][0], (
        f"two cohorts tie for largest in {sorted(ids)} at n = {sizes[0][0]}, so no sentence calling "
        "one of them 'the largest' is decidable. Say which, or say they are equal.")
    return sizes[0][1], sizes[0][0]


def test_the_largest_series_testing_metastasis_directly_is_the_one_whose_p_the_prose_quotes(flat,
                                                                                            art):
    """★ §3.3 and §5 rest their metastasis negative on a SUPERLATIVE, and the superlative decides
    which p-value belongs on the page.

    "the largest series to test metastasis by partner *directly* reports **P = .728**" is two claims
    welded together: that one of the cohorts publishing a per-partner metastasis count is the
    largest, and that the published p printed beside it is THAT cohort's. Bind only the number and a
    swap to the other cohort's p leaves the sentence false with every digit correct; bind only the
    ranking and the sentence can quote the wrong test. Both halves are asserted here, from the same
    two artifact fields.
    """
    per_cohort = (art["analyses"]["B_outcome_by_partner"]
                     ["distant_metastasis_after_presentation"]["per_cohort"])
    largest, n = _largest(art, list(per_cohort))
    published = _by_id(art)[largest].get("published_p_values", {})
    assert "distant_metastasis_three_way" in published, (
        f"{largest} is the largest cohort testing metastasis by partner directly (n = {n}) but "
        "publishes no `distant_metastasis_three_way` p, so the sentence quoting one has no owner. "
        "The prose, the artifact or both have moved.")
    expected = _pubp(published["distant_metastasis_three_way"])
    found = re.findall(
        r"the largest series to test (?:it|metastasis by partner) directly reports P = (\.\d+)",
        flat)
    assert found, (
        "nothing matches the construction stating the largest metastasis-testing series' published "
        "p. Check the MEANING before the regex — this sentence carries §3.3's and §5's whole "
        "metastasis negative.")
    wrong = [f for f in found if f != expected]
    assert not wrong, (
        f"the largest series testing metastasis directly is {largest} (n = {n}), whose published "
        f"three-way p is {expected}; the prose states {wrong!r} at {len(wrong)} of {len(found)} "
        "site(s). Either the wrong cohort's test is on the page or the ranking moved.")


def test_the_larger_of_the_pooled_outcome_cohorts_is_the_one_that_declines_the_attribution(flat,
                                                                                           art):
    """★ §5's defeater is a COMPARATIVE over the paper's own two-cohort pool, and it is the sentence
    that stops this paper overclaiming.

    "a crude, confounded quantity that the larger of its own two cohorts declines to attribute to
    the partner" says three things at once: the outcome pool has two cohorts, the larger of them is
    the one carrying a multivariable model, and that model declines the attribution. The first two
    are decidable here. ⛔ If Agaram 2014 ever became the larger — a re-read of its follow-up would
    do it — the sentence would be false while every number in §3.3 stayed right.
    """
    pooled = art["analyses"]["B_outcome_by_partner"]["pooled_cohorts"]
    found = re.findall(r"the larger of its own ([a-z]+) cohorts declines to attribute", flat)
    assert found, (
        "nothing matches §5's construction placing the defeater in the larger of the pooled "
        "cohorts. Check the MEANING before the regex — this clause is what keeps the pooled "
        "magnitude from reading as an established effect.")
    expected = _word(len(pooled))
    wrong = [f for f in found if f.casefold() != expected.casefold()]
    assert not wrong, (
        f"the outcome pool holds {len(pooled)} cohorts ({expected!r}); §5 says {wrong!r}.")

    largest, n = _largest(art, pooled)
    assert "multivariable_result" in _by_id(art)[largest], (
        f"§5 says the LARGER of the pooled outcome cohorts declines to attribute the magnitude to "
        f"the partner, but the larger one is {largest} (n = {n}) and its record carries no "
        "`multivariable_result`. The cohort that runs the model and the cohort that is larger have "
        "come apart; the sentence is now false and re-anchoring this test would hide that.")


def test_the_series_section_3_4_calls_internal_are_cohorts_this_synthesis_pools(flat, art):
    """⭐ THE REPAIRED §3.4 OPENING, BOUND TO THE ROSTERS THAT DECIDE IT.

    The retracted sentence said the two size-adjusted series were "both larger than any cohort that
    could be pooled here", which presented them as external corroboration; both are in fact cohorts
    this synthesis pools, so the paper's real and stronger point is that the cohort supplying most of
    the pooled magnitude publishes the analysis calling it confounded. The replacement asserts
    membership, and membership is a lookup.
    """
    m = re.search(
        r"neither is external to this synthesis: ([A-Z][a-z]+ \d{4}) is one of the [a-z]+ cohorts "
        r"pooled in §3\.3 and ([A-Z][a-z]+ \d{4}) one of the [a-z]+ pooled in §3\.5",
        flat)
    assert m, (
        "§3.4's opening no longer states that both size-adjusted series are internal to this "
        "synthesis. Check the MEANING before the regex: this sentence replaced a blocker that "
        "claimed the opposite, and losing it silently restores the claim it corrected.")
    rosters = {"§3.3": art["analyses"]["B_outcome_by_partner"]["pooled_cohorts"],
               "§3.5": art["analyses"]["C_partner_prevalence"]["cohorts_pooled"]}
    for name, (section, roster) in zip(m.groups(), rosters.items()):
        slug = _slug(*name.split())
        assert any(c.startswith(slug) for c in roster), (
            f"§3.4 says {name} is one of the cohorts pooled in {section}, but no id in {roster} "
            f"begins {slug!r}. Either the roster changed or the sentence names the wrong series.")


def test_the_only_cohort_treating_metastasis_as_time_to_event_is_the_one_named(flat, art):
    """★ A UNIQUENESS CLAIM IS A SUPERLATIVE WITH THE COUNT LEFT IMPLICIT.

    §3.3 leans on Paioli 2021 being the ONLY cohort that treats metastasis as a time-to-event
    endpoint — that is what makes its agreement independent corroboration rather than a third
    reading of the same table. The artifact decides it: exactly one cohort publishes a
    metastasis-free-survival p by partner.
    """
    owners = [c["id"] for c in art["cohorts"]
              if "distant_metastasis_free_survival_by_partner" in (c.get("published_p_values") or {})]
    m = re.search(r"([A-Z][a-z]+ \d{4}), the only cohort treating metastasis as a time-to-event",
                  flat)
    assert m, ("nothing matches §3.3's uniqueness claim about the time-to-event metastasis cohort. "
               "Check the MEANING before the regex.")
    assert len(owners) == 1, (
        f"§3.3 calls one cohort the ONLY one treating metastasis as a time-to-event endpoint; the "
        f"artifact records {len(owners)} publishing a partner-stratified metastasis-free-survival "
        f"p ({owners}). The claim is no longer a uniqueness claim.")
    slug = _slug(*m.group(1).split())
    assert owners[0].startswith(slug), (
        f"§3.3 names {m.group(1)} as the only cohort treating metastasis as a time-to-event "
        f"endpoint; the artifact says it is {owners[0]}.")


# ---- B.4 · the forbid: a comparison against this synthesis's own pool must be decidable ----------

#: ⛔ SCOPED BY THE PROPERTY "compares something to the cohorts this synthesis could pool", not by
#: the wording round 6 happened to find. The retracted sentence read "both larger than any cohort
#: that could be pooled here"; a rewrite reaching for "bigger than every series pooled here" is the
#: same claim and the same defect, which is the sibling a list-scoped fix misses
#: (`paper-hardening` §8b.2).
#: ⚠ EVERY ALTERNATION IS BOUNDED, AND BY WHAT IS STATED HERE RATHER THAN ASSUMED: the noun list
#: and the pool list carry explicit `\b`, and the quantifier list is bounded by the `\s+` on either
#: side of it. Without the trailing `\b`, `pool` matches inside "pooling" and `series` inside a
#: hyphenated compound — a substring match inflates coverage in one place and reds on true input in
#: another, and they are the same bug (`paper-hardening` §8b.1d, three instances paid for here).
_POOL_COMPARISON = re.compile(
    r"\b(?:larger|bigger|greater|smaller|longer)\s+than\s+(?:any|every|all)\s+"
    r"(?:cohorts?|series|stud(?:y|ies))\b[^.]{0,80}?\b(?:pooled|poolable|pool)\b")


def _sentence_around(text, start, end):
    """The sentence a match sits in, so a failure quotes what a reader would read.

    ⚠ A MISSING TERMINATOR MUST NOT SILENTLY EMPTY THE QUOTE. `str.find` answers -1 at the end of a
    document, and `text[start:-1 + 1]` is the empty string — a failure message with nothing in it
    reads like an instrument that fired on nothing.
    """
    stop = text.find(".", end)
    return text[text.rfind(".", 0, start) + 1: len(text) if stop < 0 else stop + 1].strip()


def test_no_comparison_places_a_pooled_cohort_outside_this_synthesis_own_pool(asserting, art):
    """⛔⛔ THE BLOCKER'S CLASS, CLOSED AT THE PROPERTY RATHER THAN AT THE SENTENCE.

    A claim that some series is larger than anything this synthesis could pool is decidable — the
    pooled rosters and every cohort's size are in the artifact — and it was decided by nothing for
    four rounds. Three outcomes, and the middle one is the reason this test is not a blanket ban:

      * the sentence names a series this synthesis POOLS -> false by construction, and that is
        exactly the retracted §3.4 opening;
      * the sentence names a series this synthesis does not pool -> decide it against the largest
        pooled cohort and pass if it is genuinely larger;
      * the sentence names no series this artifact holds -> UNDECIDABLE, and undecidable fails.
        A superlative over this repository's own pool with nothing to check it against is the shape
        the blocker had: the retracted sentence named its two series in the NEXT sentence, so no
        reader and no instrument could settle it where it stood.
    """
    pooled = (art["analyses"]["B_outcome_by_partner"]["pooled_cohorts"]
              + art["analyses"]["C_partner_prevalence"]["cohorts_pooled"])
    biggest_id, biggest_n = _largest(art, pooled)
    by_id = _by_id(art)
    bad = []
    for name, text in asserting.items():
        for m in _POOL_COMPARISON.finditer(text):
            sentence = _sentence_around(text, m.start(), m.end())
            named = {_slug(*g) for g in _NAMED_SERIES.findall(sentence)}
            resolved = {cid for cid in by_id if any(cid.startswith(s) for s in named)}
            if not resolved:
                bad.append(f"{name}: {sentence!r} compares something to the cohorts this "
                           "synthesis could pool and names no series the artifact holds, so "
                           "nothing can decide it. Name the series, or state the comparison "
                           "against the pooled roster the artifact computes.")
                continue
            inside = sorted(resolved & set(pooled))
            if inside:
                bad.append(f"{name}: {sentence!r} places {inside} outside the pool this "
                           f"synthesis computes, and they are in it — "
                           f"`analyses.*.pooled_cohorts`/`cohorts_pooled` hold {sorted(set(pooled))}.")
                continue
            outside = sorted(resolved - set(pooled))
            too_small = [i for i in outside if _size(by_id[i]) <= biggest_n]
            if too_small:
                bad.append(f"{name}: {sentence!r} calls {too_small} larger than every "
                           f"poolable cohort; the largest pooled cohort is {biggest_id} at "
                           f"n = {biggest_n}.")
    assert not bad, "\n\n".join(bad)


# =================================================================================================
# C · WHAT THE FIELD SAYS — the attribution surface, and the one the paper had already retracted
# once before round 6 found it again.
#
# ★ THE WITNESS IS `analyses.C_partner_prevalence.external_reported_share`. It records what NAMED
# sources state — citation key, reference number in this manuscript, PMCID, DOI, verbatim quote,
# section — and nothing else. There is no field anywhere in this synthesis recording how OFTEN
# anyone quotes anything, and `outlier_note` says so in as many words: "NO SOURCE FOR THAT QUOTING
# PRACTICE WAS EVER HELD". So a sentence about what the field quotes has no owner, and a sentence
# about what this paper's own cited sources state has exactly one.
# =================================================================================================


def test_the_externally_reported_share_is_the_one_the_artifact_holds_from_named_sources(flat, art):
    """⭐ THE REPAIR OF BLOCKER B3, BOUND BOTH WAYS.

    The retracted claim was "below the ≈27 % the field routinely quotes", at six sites. The
    replacement states the share this document's OWN cited sources give, and says it falls inside
    the pooled interval rather than being corrected by it. Two halves, both from the artifact: the
    percentage, and the reference numbers of the sources that state it. ⛔ Binding the percentage
    alone would let the attribution drift back to the field with the number left correct, which is
    the direction this defect has already travelled twice (Appendix A11, then A30).
    """
    share = art["analyses"]["C_partner_prevalence"]["external_reported_share"]
    expected = str(int(share["percent_approx"]))
    found = re.findall(r"the ≈(\d+) % this (?:document|paper)'s own cited sources state", flat)
    assert found, (
        "nothing matches the construction attributing the externally reported TAF15 share to this "
        "document's own cited sources. Check the MEANING before the regex: the sentence this "
        "replaced attributed the figure to the field at large with no source, which is blocker B3 "
        "of round 6 and Appendix A30.")
    wrong = [f for f in found if f != expected]
    assert not wrong, (
        f"`external_reported_share.percent_approx` is {expected} and the prose states {wrong!r} at "
        f"{len(wrong)} of {len(found)} site(s).")

    refs = tuple(str(s["reference_number_in_manuscript"]) for s in share["sources"])
    cited = re.findall(r"own cited sources state \(\[(\d+)\], \[(\d+)\]\)", flat)
    assert cited, (
        "§5's claims bullet no longer names the reference numbers of the sources stating the "
        "external share. Those numbers are what makes the attribution checkable by a reader; "
        "without them the sentence is back to asserting a share nobody has to source.")
    assert all(c == refs for c in cited), (
        f"the artifact's sources are references {refs} of this manuscript "
        f"({[s['citation'] for s in share['sources']]}); the prose cites {cited!r}.")


#: ⛔ THE PAYLOAD IS THE FREQUENCY WORD, NOT THE NOUN "field" (`paper-hardening` §8b.1b: count the
#: payload, never the pointer to it). §5's "the field should start reporting the partner" and §6's
#: "what the field could do about it" are asks, not attributions, and they must stay green — the
#: defect is asserting how OFTEN or how WIDELY the field quotes, attributes, repeats or cites
#: something, which is a rate over a corpus this repository does not hold.
#: ⚠ Word-bounded throughout: unbounded `cite` matches inside "recite", unbounded `often` is safe
#: but its neighbours are not, and an unbounded alternation is both a false witness somewhere and a
#: false alarm somewhere else (`paper-hardening` §8b.1d).
#: ⛔ WRITTEN OUT IN FULL, NOT ASSEMBLED FROM PARTS (`paper-hardening` §8b.1e): `claim_coverage.py`
#: harvests these patterns by STATICALLY READING THIS SOURCE, so a regex composed at runtime is one
#: it credits in its unbounded form and never in the form that runs.
_FIELD_PRACTICE = re.compile(
    r"\b(?:usually|routinely|commonly|often|widely|generally|typically|conventionally)\s+"
    r"(?:quoted|quotes|attributed|attributes|repeated|repeats|cited|cites|reported|reports)\b"
    r"|\bmost[- ](?:often[- ])?(?:quoted|cited|repeated)\b"
    r"|\bthe\s+(?:field|literature|review literature)\b[^.]{0,40}?"
    r"\b(?:quotes|repeats|attributes)\b")


def test_no_claim_about_the_fields_practice_goes_unsourced(asserting):
    """⛔⛔ A RATE OVER THE FIELD'S HABITS IS A MEASUREMENT, AND THIS SYNTHESIS HOLDS NONE.

    Round 6's blocker B3 was "below the ≈27 % the field routinely quotes", at four sites, with no
    source for the quoting practice held anywhere in the manuscript, its reference list or the
    artifact — and with the two sources in this paper's own reference list that state a general
    TAF15 share both giving about 20 %, inside the paper's own interval. Appendix A11 is the same
    defect retracted a round earlier; Appendix A30 is B3's own retraction.

    ★ THE RULE THIS ENFORCES, AND IT IS THE PAPER'S OWN: name the sources, or drop the frequency
    word. `external_reported_share.sources` is the shape a sourced claim about the outside
    literature takes here — citation key, reference number, PMCID, DOI, verbatim quote, section —
    and any claim that cannot be put in it is a claim this repository cannot support.

    ⚠ THIS CANNOT SEE AN UNSOURCED CLAIM WITH NO FREQUENCY WORD IN IT. "The literature carries point
    figures" names no rate and is true of the two sources the artifact holds; a sentence that
    asserted something false about the field in that register would pass here. Deciding those needs
    a retrieved corpus, which this repository does not have — recorded in the module docstring
    rather than left to be discovered as coverage nobody has.
    """
    bad = []
    for name, text in asserting.items():
        for m in _FIELD_PRACTICE.finditer(text):
            bad.append(f"{name}: {m.group(0)!r} in "
                       f"{_sentence_around(text, m.start(), m.end())!r}")
    assert not bad, (
        "a claim about how often or how widely the field quotes, attributes or repeats something "
        "has no witness in this synthesis — `external_reported_share` records what NAMED sources "
        "state, and `outlier_note` records that no source for a quoting practice was ever held "
        "here:\n  " + "\n  ".join(bad)
        + "\n\nName the sources and state what they say, or drop the frequency word. ⛔ Do not "
          "loosen this pattern to make the sentence pass: this is round 6's blocker B3, and "
          "Appendix A11 is the same defect one round earlier.")
