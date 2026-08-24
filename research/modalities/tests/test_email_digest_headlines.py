"""The newsletter's treatment headlines must not depend on the filter prompts.

WHY THIS TEST EXISTS. On 2026-08-19 the Merck/Moderna Phase 3 INTerpath-001 readout did not
reach the 2026-08-21 newsletter. Two causes: the generator had no source that could carry it,
and every prompt that filters the digest was scoped to methods. The generator is fixed, but the
prompt that usually wins lives in the claude.ai Routines UI, OUTSIDE this repository — no commit
here can guarantee it. So the headline block is read off the digest deterministically, and these
tests hold that path shut: they must fail if it stops surfacing news, silently dedupes a real
story away, or starts asserting a quiet week it did not observe.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from email_digest import headlines_html, headlines_md, treatment_headlines  # noqa: E402

DIGEST = """# Method-watch digest — 2026-08-24

## Clinical / treatment-news watch

### Trial registry — ClinicalTrials.gov (records updated within 60 days)

#### individualized neoantigen therapy
- 🆕 **2026-08-21** — A Study of Pembrolizumab With or Without Intismeran Autogene (PHASE3) — https://clinicaltrials.gov/study/NCT06623422

### News feeds (items from the last 14 days)

#### cancer vaccines / individualized neoantigen therapy
- 🆕 **2026-08-19** — Moderna and Merck say mRNA cancer vaccine succeeded in late-stage melanoma trial - STAT — https://news.google.com/x1
- 🆕 **2026-08-19** — Moderna and Merck say mRNA cancer vaccine succeeded in late-stage melanoma trial - CNBC — https://news.google.com/x2
- 🆕 **2026-08-21** — INTerpath-001 Trial Meets Primary and Key Secondary Endpoints - The ASCO Post — https://news.google.com/x3
- **2026-06-01** — An old item outside the window - Somewhere — https://news.google.com/x4

#### sarcoma treatment news
- ⚠ _feed returned no items at all — treat as UNREAD, not as quiet; check the feed URL._

## Literature watch

### virtual-cell / perturbation prediction
- 🆕 **2026-08-21** — A methods paper that must never appear as a treatment headline. (MED:MED/1)
"""


BREADTH_DIGEST = """# d

### News feeds (items from the last 14 days)

#### row one
- 🆕 **2026-08-24** — Row one, first item - A — https://n/1
- 🆕 **2026-08-23** — Row one, second item - B — https://n/2

#### row two
- 🆕 **2026-08-19** — Row two, first item - C — https://n/3
"""


def test_it_surfaces_the_readout_that_was_missed():
    titles = " | ".join(h["title"] for h in treatment_headlines(DIGEST))
    assert "INTerpath-001" in titles
    assert "mRNA cancer vaccine" in titles


def test_it_stops_at_the_news_section_and_never_promotes_a_literature_hit():
    # The literature watch is a separate '## ' section. A headline block that swallowed it would
    # put keyword-collision noise at the top of the email, above the summary.
    titles = " ".join(h["title"] for h in treatment_headlines(DIGEST))
    assert "methods paper" not in titles
    # ...and the registry subsection sits ABOVE the news heading, so it is not a headline either.
    assert "Intismeran Autogene" not in titles


def test_the_same_story_from_two_outlets_collapses_to_one_headline():
    same = [h for h in treatment_headlines(DIGEST) if "mRNA cancer vaccine" in h["title"]]
    assert len(same) == 1, f"expected one deduped headline, got {len(same)}"


def test_items_outside_the_window_are_excluded():
    # Only '🆕' lines are fresh; the generator owns that judgement, and this must not re-derive it.
    assert all("old item" not in h["title"] for h in treatment_headlines(DIGEST))


def test_capped():
    assert len(treatment_headlines(DIGEST, cap=1)) == 1


def test_breadth_first_gives_every_priority_row_a_voice_before_any_row_gets_two():
    # The digest orders its news rows by OUR priority. A straight date sort discards that: the
    # first render of this block put a generic same-day round-up above the Phase 3 readout.
    items = treatment_headlines(BREADTH_DIGEST, cap=2)
    assert [h["title"] for h in items] == ["Row one, first item - A", "Row two, first item - C"], items


def test_the_text_block_carries_no_urls():
    # Google News redirect links run to hundreds of base64 characters; six of them make the
    # plain-text alternative unreadable. Links belong on the titles in the HTML part.
    assert "http" not in headlines_md(treatment_headlines(DIGEST))


def test_the_html_block_links_the_title_and_escapes_it():
    html = headlines_html([{"date": "2026-08-19", "title": "A <b>headline</b> & more", "link": "https://x/y"}])
    assert '<a href="https://x/y"' in html
    assert "&lt;b&gt;headline&lt;/b&gt; &amp; more" in html
    assert headlines_html([]) == ""


def test_a_digest_with_no_news_section_renders_nothing_rather_than_claiming_quiet():
    # An older digest, or a generator that failed before the news section, must produce an EMPTY
    # block — never a line implying the week was quiet. Absence of a reading is not a reading.
    assert treatment_headlines("# Method-watch digest\n\n## Literature watch\n- 🆕 **2026-08-21** — x") == []
    assert headlines_md([]) == ""


def test_the_block_marks_its_own_evidential_weight():
    # Press sources are leads, not evidence (CLAUDE.md §7). The block must say so on its face —
    # it sits at the top of the email, where it is most likely to be read as established fact.
    block = headlines_md(treatment_headlines(DIGEST))
    assert "read the source before citing" in block
