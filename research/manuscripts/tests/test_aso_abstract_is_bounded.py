"""The ASO abstract has a length bound of its own, and it is this paper's rather than another's.

⛔ WHY THIS EXISTS. Until 2026-08-19 the ASO abstract had NO word guard. Its length was twice
"verified" against `ABSTRACT_WORD_LIMIT = 305` in `test_endpoint_manuscript_figures.py` — a constant
that is JNCI's structured-abstract limit, applied to a DIFFERENT manuscript
(`endpoint/response-endpoint-indolent-tumours.md`). That test reads its own `PAPER` and never opens
this one, so it passed no matter what this abstract did, and prose was trimmed out of this paper to
satisfy a constraint borrowed from another. A green test that does not read the file it is believed
to guard is worse than no test: it converts an unchecked property into a checked-looking one.

★ THE BOUND HERE IS THE DEPOSIT TARGET'S. bioRxiv sets no abstract word limit, so this is not a venue
constraint and must not be described as one. It is a drift bound: an abstract is the only part of the
paper most readers will read, and it has grown every time a reviewer asked for a qualification to be
carried into it. 380 leaves room for the qualifications this paper genuinely owes a reader — the
adopted-not-measured criterion, the by-construction share of the gap-length result, the unusable
candidate set — while failing if the abstract starts absorbing the Results.

⚠ IF A JOURNAL IS EVER TARGETED, replace this with that venue's limit and say which venue in the
constant's name. Do not silently raise this number to make an edit fit.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
#: ⛔ BOTH ABSTRACTS (round 14 seat 2). `PAPER` named the extended report alone, so the journal
#: article's abstract — the one a NAT reviewer reads first — had no length bound and no scope
#: needle of any kind. That is the ninth instrument this review has found bound to one of a pair
#: while reporting on both, and the shape is always the same: the second document was added to the
#: repository and the guard was not widened with it.
PAPERS = {
    "extended-report": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-research-article.md"),
    "journal-article": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-journal-article.md"),
}
PAPER = PAPERS["extended-report"]
NULL = os.path.join(REPO, "research", "modalities", "aso-parent-null.json")

#: Not a venue limit — bioRxiv has none. A drift bound; see the module docstring.
#:
#: ⚠ RAISED 380 → 400 ON 2026-08-19, DELIBERATELY AND WITH THE REASON, WHICH IS WHAT THE DOCSTRING
#: ABOVE ASKS FOR. Four separate readers, working from four different briefs, each found the
#: abstract stating something the body qualifies, and each qualification was owed:
#:   · search depth moves the headline — six of nine "clean" designs are not clean at ten times
#:     the default ceiling, and the abstract said nothing about depth at all;
#:   · 87 of 190 is a rate over DESIGNS, while a laboratory picks one register at its own junction,
#:     where 35 of 38 junctions have a design that clears the screen;
#:   · every null rate quoted is computed at the ten-base-pair cut only, so the seven-base-pair
#:     reading printed beside them has no chance baseline;
#:   · the three condemned designs sit OUTSIDE the 38-junction panel and are passed by the
#:     mature-parent screen, which is what makes them interesting and was not said.
#: The abstract was trimmed by 25 words first — the pipeline sentence, the lead-reagent tail, the
#: chimera gloss and the depth clause all shortened — and 386 is what remains after that. This is
#: the bound doing its job (it forced the trim) rather than being loosened to avoid one. 400 is not
#: an invitation: the next reader asking for a fifth qualification should be answered by cutting
#: something, and if the abstract reaches 400 the question is which Result it has absorbed.
ABSTRACT_DRIFT_BOUND = 400

#: The condensed submission's own bound.
#:
#: ⚠ ALSO NOT A VENUE LIMIT, AND THE DOCSTRING'S INSTRUCTION CANNOT BE FOLLOWED YET. The module
#: docstring says to replace the bound with the venue's own once a journal is targeted. NAT is the
#: targeted venue, and its author instructions could not be read: every Sage-hosted NAT page in
#: `research/literature/venue-policy-browser-fetch.json` — `author-instructions/NAT`,
#: `aims-scope/NAT`, `home/nat` — returned **403** to the fetcher. So this stays a drift bound, and
#: it is NOT to be described as NAT's limit until someone has read NAT's limit.
#:
#: 250 rather than 400 because this paper is on a six-page budget: a word in its abstract is a word
#: not available to its Results. The abstract stands at 227, so the bound buys one qualification
#: and no more.
JOURNAL_ABSTRACT_DRIFT_BOUND = 250

#: Which needles apply to a paper that reports fewer results. The two below are SCOPE bounds — they
#: say what the work is and what the criterion is — and every abstract of this work owes both. The
#: rest of `_needles()` names results the condensed paper deliberately does not carry, and
#: demanding them there would push its Results into its abstract to satisfy a guard.
UNIVERSAL_NEEDLES = ("the criterion is adopted rather than measured",
                     "that the work is computational and nothing was made")


def _abstract(paper=None):
    paper = paper or PAPER
    if not os.path.exists(paper):
        pytest.fail(f"the manuscript is missing: {paper}")
    text = open(paper, encoding="utf-8").read()
    assert "## Abstract" in text, (
        f"the abstract heading has moved in {os.path.basename(paper)}; re-anchor this guard")
    body = text.split("## Abstract", 1)[1].split("\n---\n", 1)[0]
    return [w for w in re.sub(r"\*", "", body).split() if w.strip()]


def _null():
    """`aso-parent-null.json`, the artifact every rate the abstract prints is measured in."""
    if not os.path.exists(NULL):
        pytest.fail(f"the null artifact is missing: {NULL} — every figure below is derived from it")
    return json.load(open(NULL, encoding="utf-8"))


def _figures():
    """Every number this guard requires the abstract to carry, READ rather than typed.

    ⛔ WHY DERIVED. The needles this replaced were literal strings — "175 of 190",
    "adopted, not measured", "partly by", "survive every screen". Two of the four are numbers, and
    a number typed into a test is a second copy of a figure whose only home should be the artifact:
    when the ladder was measured on 2026-08-19 and the counts at seven and ten moved into the
    abstract together, nothing would have noticed a stale copy here. Everything numeric now comes
    out of `aso-parent-null.json` at run time, so re-running the generator re-aims the guard.
    """
    art = _null()
    observed, cuts = art["observed"], art["cut_sensitivity"]
    ladder = {name: ens["cut_ladder"] for name, ens in art["null_ensembles"].items()}
    strict, loose = max(cuts["cuts_bp"]), min(cuts["cuts_bp"])

    def strongest(cut):
        return max(100 * v[str(cut)]["rate_liable"] for v in ladder.values())

    return {
        "n_designs": observed["n_designs"],
        "n_liable_strict": observed["n_liable"],
        "n_liable_loose": cuts["observed_n_liable"][str(loose)],
        "n_junctions": cuts["n_junctions"],
        "n_junctions_clearing": cuts["n_junctions_with_a_clearing_design"][str(strict)],
        "observed_pct_loose": 100 * cuts["observed_rate_liable"][str(loose)],
        "null_pct_strict": strongest(strict),
        "null_pct_loose": strongest(loose),
        "strict": strict,
        "loose": loose,
    }


#: The clause that names the fully screened set. Used as a SCOPE, not as a needle in its own
#: right — see `_scoped` and the entry that depends on it.
_SURVIVES_EVERY_SCREEN = re.compile(
    r"surviv\w+ every screen|clear\w* every screen|pass\w* every screen", re.I)


def _scoped(body, scope):
    """The sentence that `scope` matches, or "" if it matches nothing.

    ⛔ WHY A SCOPE AT ALL. The no-reported-patient qualifier was first written as a free search over
    the whole abstract, and it passed while the clause it guards was deleted — because an earlier,
    unrelated sentence ("chimeras at real exon termini … which no patient is reported to carry")
    contains the same words about a different set. A property asserted anywhere in a paragraph is
    not the property that a particular claim carries its qualifier.
    """
    match = scope.search(body)
    if not match:
        return ""
    end = re.search(r"(?<=[.])\s", body[match.end():])
    return body[match.start(): match.end() + (end.end() if end else len(body))]


def _needles():
    """(name, compiled pattern, why it is owed, scope) — properties, not sentences.

    ⚠ TOLERANT OF WORDING, INTOLERANT ON SUBSTANCE. The abstract is rewritten every
    round; four of these clauses have already been reworded once while meaning the same thing, and
    a guard that goes red on a synonym trains its reader to edit the guard. Each pattern below
    admits any phrasing that still says the thing, and none admits its absence.
    """
    f = _figures()
    near = "[^.]{0,140}"
    return [
        ("the criterion is adopted rather than measured",
         re.compile(r"adopted[^.]{0,60}not measured|not measured[^.]{0,60}adopted"
                    r"|adopted rather than measured|is a choice"
                    #: ⚠ THE JOURNAL ARTICLE SAYS IT AS "a convention rather than a measurement",
                    #: which is the same property in different words. This file's own rule is
                    #: tolerant of wording, intolerant on substance.
                    r"|convention rather than a measurement"
                    r"|a convention[^.]{0,60}not a measurement", re.I),
         f"{f['strict']} base pairs is a convention this work took from the literature, not a "
         "value it derived; an abstract that states the count without it reads as a measurement",
         None),
        (f"the count at the {f['strict']}-base-pair cut ({f['n_liable_strict']} of "
         f"{f['n_designs']})",
         re.compile(rf"\b{f['n_liable_strict']}\b{near}\b{f['n_designs']}\b"
                    rf"|\b{f['n_designs']}\b{near}\b{f['n_liable_strict']}\b"),
         "the headline count, with its denominator in the same breath",
         None),
        (f"the count at the {f['loose']}-base-pair cut ({f['n_liable_loose']} of "
         f"{f['n_designs']})",
         re.compile(rf"\b{f['n_liable_loose']}\b[^.]{{0,40}}\b{f['n_designs']}\b"),
         "the other end of the cited range, which is why 'nearly half' is the conservative "
         "reading rather than the finding",
         None),
        (f"a chance baseline at the {f['strict']}-base-pair cut "
         f"({f['null_pct_strict']:.1f}%)",
         re.compile(rf"\b{f['null_pct_strict']:.1f}\s*%"),
         "a count with no null cannot be large or small",
         None),
        (f"a chance baseline at the {f['loose']}-base-pair cut ({f['null_pct_loose']:.1f}%)",
         re.compile(rf"\b{f['null_pct_loose']:.1f}\s*%"),
         "⛔ THE NULL MOVES WITH THE CUT. Printing the loose reading beside a null computed only at "
         f"the strict cut leaves {f['n_liable_loose']}/{f['n_designs']} with no chance baseline at "
         "all, which is how a reader concludes the loose reading is the alarming one",
         None),
        (f"the observed rate at the {f['loose']}-base-pair cut "
         f"({f['observed_pct_loose']:.1f}%)",
         re.compile(rf"\b{f['observed_pct_loose']:.1f}\s*%"),
         "the null at that cut is only readable beside the observed rate at that cut",
         None),
        ("the by-construction share of the gap-length result",
         re.compile(r"by construction|by necessity of the (?:design|budget)"
                    r"|guaranteed by[^.]{0,60}budget", re.I),
         "part of the quieting a longer gap buys is fixed by the mismatch budget rather than "
         "measured, and an abstract that reports only the movement claims the whole of it",
         None),
        ("designs clearing the screen per junction, not per design",
         re.compile(rf"\b{f['n_junctions_clearing']}\b[^.]{{0,80}}\b{f['n_junctions']}\b"),
         f"{f['n_liable_strict']} of {f['n_designs']} is a rate over DESIGNS, and a laboratory "
         f"picks one register at its own junction, where {f['n_junctions_clearing']} of "
         f"{f['n_junctions']} junctions have a design that clears",
         None),
        ("the designs that survive every screen",
         _SURVIVES_EVERY_SCREEN,
         "the abstract names leads, so it has to say what the fully screened set is",
         None),
        ("and that THOSE designs sit at no reported patient breakpoint",
         re.compile(r"(?:no|none|not)\b[^.;]{0,90}(?:patient|breakpoint)"
                    r"[^.;]{0,90}(?:report|carr|observ)"
                    r"|no reported[^.;]{0,40}breakpoint", re.I),
         "the designs that survive every screen sit at junctions no patient is reported to carry, "
         "so the named leads carry off-target loads by necessity — an abstract naming only the "
         "leads misleads about that. ⚠ SCOPED to the sentence naming that set: the abstract says "
         "the same words about the exon-terminus chimeras two sentences earlier, and an unscoped "
         "search passed on a deleted clause",
         _SURVIVES_EVERY_SCREEN),
        ("that the work is computational and nothing was made",
         re.compile(r"nothing (?:has been|was) synthesi[sz]ed|no wet-lab"
                    #: ⚠ "This work is computational" is the condensed abstract's wording and was
                    #: not admitted by `the work is computational`. Substance, not article.
                    r"|th(?:e|is) work is computational", re.I),
         "the abstract is the part of the paper that travels alone, and the repository "
         "frontmatter that says this is stripped from both rendered PDFs",
         None),
    ]


@pytest.mark.parametrize("key,bound", [("extended-report", ABSTRACT_DRIFT_BOUND),
                                       ("journal-article", JOURNAL_ABSTRACT_DRIFT_BOUND)])
def test_the_abstract_reads_this_paper_and_is_bounded(key, bound):
    """⚠ The first assertion is the one that failed to exist before: that we opened THIS file."""
    words = _abstract(PAPERS[key])
    assert 150 < len(words), (
        f"{key}'s abstract is only {len(words)} words — either it has been gutted or this guard is "
        "reading the wrong file, which is the exact defect it was written for")
    assert len(words) <= bound, (
        f"{key}'s abstract is {len(words)} words against a drift bound of {bound}. This is not a "
        "venue limit — bioRxiv sets none and NAT's author instructions return 403 to the fetcher — "
        "so the question is whether the abstract is absorbing the Results. Trim it, or raise the "
        "bound deliberately and say why beside the constant.")


def test_the_abstract_carries_the_qualifications_the_results_attach():
    """The front matter must not state the headline more flatly than the Results support.

    Each clause below was added because a reader found the abstract stating a result the body
    qualifies. They are asserted so a later trim for length cannot quietly drop the qualification
    and keep the number.

    ⛔ AND THE BOUND WAS RAISED FROM 380 TO 400 TO BUY FOUR OF THEM WHILE PINNING NONE. The four
    qualifications the raise paid for — search depth moving the headline, the per-junction reading,
    every null being computed at one cut, and the condemned designs sitting outside the panel —
    were argued for in a comment on the constant and then left unasserted, so the next trim for
    length could have taken the words back and kept the bound. The bound stays; the clauses it
    bought are now assertions.
    """
    body = " ".join(_abstract())
    missing = [(name, why) for name, pattern, why, scope in _needles()
               if not pattern.search(_scoped(body, scope) if scope is not None else body)]
    assert not missing, (
        "the abstract no longer carries "
        + f"{len(missing)} qualification(s) the Results attach:\n  "
        + "\n  ".join(f"{name} — {why}" for name, why in missing)
        + "\n\nEvery number above is read from research/modalities/aso-parent-null.json at run "
          "time, so if a figure genuinely moved, regenerate the artifact and restate the abstract; "
          "do not retype the number here.")


def test_the_condensed_abstract_carries_the_two_scope_bounds_every_abstract_of_this_work_owes():
    """⛔ THE SHORT PAPER'S ABSTRACT IS THE ONE THAT TRAVELS ALONE THE FURTHEST.

    It is what a NAT editor reads first and the only part of this work most readers will ever see,
    and until 2026-08-22 no guard opened it. It does not owe the extended report's result needles —
    it deliberately reports fewer results, and demanding them here would push its Results into its
    abstract to satisfy a test. It does owe both SCOPE bounds, because those are not results: they
    say what the work is and what the criterion is, and dropping either is the R1-R5 defect the
    language discipline exists to prevent.
    """
    body = " ".join(_abstract(PAPERS["journal-article"]))
    needles = {name: pattern for name, pattern, _why, _scope in _needles()}
    for name in UNIVERSAL_NEEDLES:
        assert name in needles, (
            f"{name!r} is no longer a needle in _needles(), so this test is silently checking "
            "nothing — re-anchor it to the needle that replaced it")
    missing = [name for name in UNIVERSAL_NEEDLES if not needles[name].search(body)]
    assert not missing, (
        "the journal article's abstract no longer states "
        + f"{len(missing)} scope bound(s) it owes:\n  " + "\n  ".join(missing)
        + "\n\nThese are not results and cannot be traded for length: an abstract that states the "
          "count without saying the criterion was adopted reads as a measurement, and one that "
          "does not say the work is computational travels without the frontmatter that says so.")
