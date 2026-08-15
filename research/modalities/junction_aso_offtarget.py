#!/usr/bin/env python3
"""
Transcriptome-wide off-target screen for the fusion-junction gapmer ASOs.

WHY: junction_aso.py only checks that a gapmer's target window is not a *perfect*
substring of the two parent CDSs. A real specificity claim needs a transcriptome-wide
near-match search: could the antisense oligo hybridise (with a few mismatches) to some
OTHER human transcript and trigger RNase-H cleavage there? This script answers that for
the committed fusion-specific designs.

HOW: for each top fusion-specific gapmer, take its 16-mer target_mRNA (sense) window and
BLAST it (blastn-short, low-complexity filter OFF — these SYGQ-derived windows are
GC/repeat-biased) against human RefSeq RNA via the NCBI BLAST URL API. We then flag, per
oligo, any near-complementary off-target transcript that is NOT EWSR1 or NR4A3, and — the
RNase-H-relevant part — whether the match covers the central DNA-gap region (positions
WING..LEN-WING), since RNase-H cleavage needs the DNA:RNA duplex contiguous across the gap;
a match confined to a wing is a weaker (affinity-only) liability than a gap-spanning match.

INTERNET REQUIRED (NCBI). The dev sandbox blocks outbound HTTPS, so this is meant to run on
a GitHub-hosted runner (.github/workflows/aso-offtarget.yml), which publishes the result JSON
to the `modalities-cache` branch — the same pattern as depmap_sarcoma_dependency.py.

Graceful degradation: if a BLAST query fails/times out, that oligo is recorded with
status="screen_failed" rather than crashing the run, so partial results still publish.

Output: junction-aso-offtarget.json
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import junction_aso as ja   # reuse the committed design logic (no duplication)

# Breakpoint is parameterisable (env) so the SAME screen can be run on the canonical breakpoint
# OR on a favorable one identified by the per-breakpoint scan, to test whether the GC/complexity
# "favorable" triage actually yields off-target cleanliness under the full BLAST screen.
if os.environ.get("EWSR1_KEEP_AA"):
    ja.EWSR1_KEEP_AA = int(os.environ["EWSR1_KEEP_AA"])
if os.environ.get("NR4A3_KEEP_AA_FROM"):
    ja.NR4A3_KEEP_AA_FROM = int(os.environ["NR4A3_KEEP_AA_FROM"])
_SUFFIX = os.environ.get("OUT_SUFFIX", "")
OUT = os.path.join(os.path.dirname(__file__), f"junction-aso-offtarget{_SUFFIX}.json")

BLAST = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
PARENT_ACCS = {"NM_005243", "NM_006981"}          # EWSR1, NR4A3 (the intended on-/parent hits)
# ⛔ THE PARENT SET MUST FOLLOW `DONOR_GENE`, OR A NON-EWSR1 SCREEN SILENTLY MISCOUNTS IN BOTH
# DIRECTIONS (2026-08-12). This tuple names the transcripts a hit is NOT counted as an off-target
# against, because each parent matches one wing of a junction oligo by construction. Left EWSR1-only,
# a TAF15::NR4A3 screen would (a) count every wild-type TAF15 wing hit as an off-target, inflating
# that junction's load, and (b) keep EXCLUDING wild-type EWSR1 — a gene that is NOT a parent of that
# fusion and whose engagement is a real specificity finding. Two errors in opposite directions from
# one stale constant.
# ⚠ NOTE WHAT IS AND IS NOT SOLVED HERE. Adding the donor's SYMBOL fixes the name-match arm.
# `PARENT_ACCS` stays EWSR1/NR4A3 because this repository holds no verified RefSeq accession for
# TAF15, TCF12 or FUS, and typing one from memory is exactly the failure gate 4 exists for. So for a
# non-EWSR1 donor the accession arm is INERT and only the name arm fires; every emitted artifact
# records `parent_set` so a reader can see which arms were live rather than inferring it.
_DONOR = (os.environ.get("DONOR_GENE") or "EWSR1").strip() or "EWSR1"
_DONOR_ALIASES = {
    "EWSR1": ("EWSR1", "EWS RNA"),
    "TAF15": ("TAF15", "TATA-box binding protein associated factor 15", "TAF2N", "RBP56"),
    "FUS": ("FUS", "FUS RNA binding protein", "TLS", "fused in sarcoma"),
    "TCF12": ("TCF12", "transcription factor 12", "HEB"),
    # ⭐ PGR ADDED 2026-08-15 for the PGR::NR4A3 seam of PMID 36103645. ⚠ THE PHRASE IS A QUOTE,
    # NOT A RECOLLECTION: that report writes "gene fusion of progesterone receptor, PGR (exon2) to
    # the 5′ untranslated region (UTR) of NR4A3 (exon2)". No further synonym is listed, because this
    # repository holds no fetched record of one and inventing an alias would silently EXPAND what
    # counts as a parent — i.e. silently SHRINK every off-target count this screen reports.
    "PGR": ("PGR", "progesterone receptor"),
}
PARENT_GENES = tuple(_DONOR_ALIASES.get(_DONOR, (_DONOR,))) + (
    "NR4A3", "NOR-1", "nuclear receptor subfamily 4 group A member 3")

# ⛔ SPLIT BY SHAPE, BECAUSE SHAPE IS WHAT DECIDES HOW SAFELY AN ALIAS CAN BE MATCHED. A multi-word
# phrase ("EWS RNA", "fused in sarcoma", "nuclear receptor subfamily 4 group A member 3") is
# distinctive enough that a plain substring test cannot collide. A BARE SYMBOL is three or four
# characters and collides constantly — see `is_parent` below for the three measured cases.
# ⚠ DERIVED from `PARENT_GENES`, never maintained beside it: adding an alias to `_DONOR_ALIASES`
# must not require remembering to update a second list, because that is the stale-constant failure
# the `DONOR_GENE` comment above already records once.
PARENT_SYMBOLS = tuple(g.upper() for g in PARENT_GENES if " " not in g)
PARENT_PHRASES = tuple(g.upper() for g in PARENT_GENES if " " in g)
#: How many of the ranked fusion-specific designs are screened.
#: ⛔ IT HAD TO BECOME A KNOB THE MOMENT A SECOND GEOMETRY EXISTED, AND A FIXED 6 WOULD HAVE MADE THE
#: GAP-LENGTH COMPARISON AN ARTEFACT OF THIS CONSTANT (2026-08-13). The number of junction-spanning
#: registers is `GAP - 1`: five at the 16-mer 5-6-5, seven at 5-8-5, nine at 5-10-5. A cap of 6
#: therefore screens 5 of 5 at the short gap and 6 of 9 at the long one — so a longer-gap panel would
#: come back with fewer counted liabilities partly because a third of its designs were never
#: searched, and the flattering direction is the one that goes unnoticed.
#: ⚠ THE DEFAULT IS UNCHANGED AT 6, so every committed screen and every existing dispatch is
#: bit-for-bit unaffected; only a caller that asks for more gets more.
N_OLIGOS = ja._env_int("SCREEN_TOP_N", 6)          # screen the top N fusion-specific designs
# near match = allow up to 2 mismatches over the oligo length (14/16 at len 16, 18/20 at len 20)
NEAR_MATCH_MIN_IDENT = ja.OLIGO_LEN - 2
SUBMIT_SPACING_S = 3                               # NCBI: at most one request per 3 s
POLL_MAX_S = 600                                   # cap per-query polling at 10 min


def _http(url, data=None, timeout=120):
    req = urllib.request.urlopen(url if data is None else urllib.request.Request(url, data=data),
                                 timeout=timeout)
    return req.read().decode("utf-8", "replace")


def blast_put(seq):
    """Submit a short blastn search restricted to human RefSeq RNA; return the RID."""
    params = {
        "CMD": "Put", "PROGRAM": "blastn", "DATABASE": "refseq_rna",
        "QUERY": seq, "WORD_SIZE": "7", "EXPECT": "1000",
        "HITLIST_SIZE": str(BLAST_HITLIST_SIZE),
        "FILTER": "F", "MEGABLAST": "off", "ENTREZ_QUERY": "txid9606[ORGN]",
    }
    html = _http(BLAST, data=urllib.parse.urlencode(params).encode())
    m = re.search(r"^\s*RID = (\S+)", html, re.M)
    if not m:
        raise RuntimeError("no RID returned from BLAST Put")
    return m.group(1)


def blast_poll(rid):
    """Poll until the search is READY; raise on FAILED/UNKNOWN or timeout."""
    waited = 0
    while waited < POLL_MAX_S:
        html = _http(BLAST + "?" + urllib.parse.urlencode(
            {"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo"}))
        m = re.search(r"Status=(\w+)", html)
        status = m.group(1) if m else "UNKNOWN"
        if status == "READY":
            return
        if status in ("FAILED", "UNKNOWN"):
            raise RuntimeError(f"BLAST status {status} for RID {rid}")
        time.sleep(20)
        waited += 20
    raise RuntimeError(f"BLAST poll timeout for RID {rid}")


def blast_hits(rid):
    """Fetch XML results and return parsed HSPs.

    ⛔⛔ ORIENTATION IS PARSED AS OF 2026-08-12, AND EVERY SCREEN COMMITTED BEFORE THAT DATE
    OVER-COUNTS. This function read six HSP fields and never `Hsp_hit-frame`, and no orientation
    filter existed anywhere downstream. `blastn` searches BOTH strands by default, so a transcript
    carrying the REVERSE COMPLEMENT of the sense target window is returned as a high-identity hit —
    and an antisense oligonucleotide cannot hybridise it, because hybridisation needs the
    complement, not the reverse complement. Such a hit is not a weak liability; it is not a
    liability at all. It was nonetheless admitted by the `identity >= 14` filter and, if its
    alignment spanned query positions 6-11, recorded as a `true_cleavage_risk`.

    ⭐ THE DISCRIMINATING EVIDENCE WAS A CONTRADICTION BETWEEN THIS REPOSITORY'S OWN TWO SCREENS,
    found by adversarial review. At TCF12 e13::NR4A3 e3 the design `GGGCATATCTGTGAGA` returns FIVE
    PERFECT 16/16 matches to C7orf25 here, while `aso_insilico`'s uncapped scan over the same
    186,185-transcript set reports `offtarget_exact: 0` and `offtarget_le1mm: 0` for the identical
    query. Both cannot be true: an exact match lies inside the local scan's <=1-mismatch window, and
    that scan is exhaustive for <=1 mismatch by a pigeonhole argument over both 8-mer halves. The
    local scan searches the STORED (sense) orientation only — stated in the manuscript as a scoping
    choice — so a minus-strand BLAST hit is exactly the class it would miss and this one would keep.
    The published reconciliation ("the <=1-mismatch cutoff cannot see 14/16 hits") cannot explain a
    16/16 hit and therefore cannot be assumed to explain the other divergences either.

    ⚠ WHAT IS FIXED AND WHAT IS NOT. `hit_frame` is now captured and `is_minus_strand` derived, so
    downstream code can exclude or flag them. This does NOT retro-correct the committed artifacts:
    they were produced without the field and cannot be re-derived without re-running the search, so
    every `n_true_cleavage_risk` published before this date is an UPPER BOUND of unknown tightness.
    Re-running is the only fix, and the manuscript must say so until it has.
    """
    xml = _http(BLAST + "?" + urllib.parse.urlencode(
        {"CMD": "Get", "RID": rid, "FORMAT_TYPE": "XML"}), timeout=180)
    root = ET.fromstring(xml)
    hits = []
    for hit in root.iter("Hit"):
        hid = (hit.findtext("Hit_accession") or "")
        hdef = (hit.findtext("Hit_def") or "")
        for hsp in hit.iter("Hsp"):
            ident = int(hsp.findtext("Hsp_identity") or 0)
            alen = int(hsp.findtext("Hsp_align-len") or 0)
            qfrom = int(hsp.findtext("Hsp_query-from") or 0)
            qto = int(hsp.findtext("Hsp_query-to") or 0)
            # ⚠ ABSENT IS NOT PLUS. A missing `Hsp_hit-frame` is recorded as None and treated as
            # UNKNOWN orientation downstream, never silently as the safe case — that substitution
            # is how the original defect would reappear the first time NCBI changed its schema.
            raw_frame = hsp.findtext("Hsp_hit-frame")
            frame = int(raw_frame) if raw_frame not in (None, "") else None
            hits.append({"acc": hid, "defn": hdef, "identity": ident, "align_len": alen,
                         "q_from": qfrom, "q_to": qto,
                         "hit_frame": frame,
                         "is_minus_strand": (frame < 0) if frame is not None else None,
                         "qseq": hsp.findtext("Hsp_qseq") or "",
                         "midline": hsp.findtext("Hsp_midline") or ""})
    return hits


#: Screens produced before orientation was parsed. Their counts are upper bounds, and any artifact
#: whose hits lack `hit_frame` must be reported as such rather than quoted as a measurement.
#: ⛔ BLAST's own ceiling on hits returned per query, and the reason a near-match count of
#: exactly this value is a LOWER BOUND rather than a measurement. It is named because two
#: different caps operate on the same numbers and conflating them misreads both: this one
#: bounds what the search REPORTS, while the 15-hit retention below bounds what we STORE.
#: The manuscript quotes both, and `submission_tables` marks its columns from them.
#: ⭐ OVERRIDABLE SO THE CENSORING CAN BE MEASURED RATHER THAN ONLY DISCLOSED (2026-08-13). 136 of the
#: 183 screened designs carry right-censored counts, and the manuscript can only report that as a
#: bound. A re-screen at a deeper ceiling turns those bounds into measurements — and it can move a
#: RESULT, not just a caveat: a tenth design scores zero residual cleavage load and is refused as
#: clean solely because its unstored hits are unknown. ⛔ A DEEPER RE-SCREEN MUST WRITE TO ITS OWN
#: SUFFIX. Overwriting the committed screens would silently re-base every count the paper quotes,
#: and the two sets are not comparable: a count taken at a deeper ceiling is a different measurement,
#: not a correction of the shallower one.
#: ⭐ THE DEFAULT IS NAMED SEPARATELY FROM THE LIVE VALUE, because they answer different
#: questions. The live constant is what THIS process would search at; the default is the floor a
#: committed screen is graded against when asking "was this run deeper than a normal one?"
#: (`aso_screen_sets.is_deep`). Under a `BLAST_HITLIST_SIZE=500` dispatch the live value is 500,
#: and reading it as the default would make every deep screen on disk look shallow — a depth
#: test that silently answers "no" for every file.
DEFAULT_BLAST_HITLIST_SIZE = 50
BLAST_HITLIST_SIZE = ja._env_int("BLAST_HITLIST_SIZE", DEFAULT_BLAST_HITLIST_SIZE)

#: How many ranked hits are STORED per design, against a hitlist of up to `BLAST_HITLIST_SIZE`.
#: ⛔ NAMED BECAUSE IT WAS A BARE `[:15]` IN ONE PLACE AND A TYPED "15" IN FOUR OTHERS — the
#: manuscript, the tables generator, the pinning test and this module's own comments. It is the
#: number that decides whether a design can be called clean at all: the strand of an unstored hit
#: is unrecoverable, so a design with more near-matches than this carries a strand-blind count no
#: later pass can repair. A fact that decides a headline result does not get to live as a literal.
#: ⚠ RAISING THIS IS NOT COSMETIC EITHER: it is what lets a re-screen decide cleanliness for a design
#: whose current answer is "unknown beyond the stored window".
#: The default, named for the same reason as `DEFAULT_BLAST_HITLIST_SIZE` above.
DEFAULT_SAVED_HITS_PER_DESIGN = 15
SAVED_HITS_PER_DESIGN = ja._env_int("SAVED_HITS_PER_DESIGN", DEFAULT_SAVED_HITS_PER_DESIGN)

# ─────────────────────────────────────────────────────────────────────────────────────────
# WHAT THIS SCREEN RAN UNDER — the four knobs, recorded rather than left to be inferred
# ─────────────────────────────────────────────────────────────────────────────────────────
#: ⛔ AN ARTIFACT MUST STATE THE PARAMETERS IT WAS PRODUCED UNDER, BECAUSE INFERRING THEM FAILED IN
#: PRINT (2026-08-13). Four values here are environment-overridable — `BLAST_HITLIST_SIZE`,
#: `SAVED_HITS_PER_DESIGN`, and `OLIGO_LEN`/`WING` through `junction_aso` — and until this block
#: existed a screen's `method` recorded the database, the program, the near-match threshold, the gap
#: region, the breakpoint model and the parent set, and NOT ONE of the four. Two consequences, both
#: measured in this tree:
#:   * A manuscript sentence described a deeper re-screen as "a tenfold deeper ceiling and retention
#:     depth". The ceiling did go 50 -> 500. The retention did NOT go to 150: `aso-offtarget.yml`
#:     exports `SAVED_HITS_PER_DESIGN=500` alongside it, and the discriminating evidence is that one
#:     `-deep500` design stores **305** hits — a number a retention of 150 cannot produce. Nothing
#:     in any artifact could have told a reader that; it was caught by counting stored hits in a file.
#:   * A `-deep500` screen and the default screen beside it have BYTE-IDENTICAL `method` blocks.
#:     The only things separating a 500/500 run from a 50/15 run were the filename suffix and the
#:     indirect tell that a screen storing more than 15 hits cannot have run at a retention of 15.
#: ⛔ THIS IS FORWARD-ONLY AND CANNOT BE BACKFILLED. The committed screens carry no `parameters`
#: block and none can be added to them: what a past run used is not recoverable from its output
#: (only bounded by it), and an inferred value written into a provenance field is the exact failure
#: this repository keeps paying for — a populated field is not a measured one. The absence stays
#: visible instead.


def _env_was_set(name):
    """Was this knob's environment variable actually PRESENT when the constants were derived?

    ⚠ THE EMPTINESS RULE IS ASKED FOR, NOT RE-IMPLEMENTED. `ja._env_int` treats "" and whitespace as
    ABSENT, and that is not a corner case on this lane: `aso-offtarget.yml` splits its single
    `gapmer_geometry` input into `OLIGO_LEN` and `WING` and then `export`s BOTH, so a dispatch that
    leaves the geometry blank exports them EMPTY and the run uses the defaults. A presence test
    written as `name in os.environ` would report every such screen's geometry as overridden — a
    provenance field that is wrong on precisely the path CI takes, which is worse than no field.
    `_env_int(name, None)` returns None only when the variable is absent by that same rule, and
    `int()` can never return None, so the two cannot drift apart.
    """
    return ja._env_int(name, None) is not None


#: The four variables, named ONCE. Everything that has to enumerate them walks this tuple rather
#: than repeating the list, so a fifth knob cannot be added to the screen and forgotten here.
#: ⭐ `SCREEN_TOP_N` JOINED THE LIST WHEN IT BECAME A KNOB, WHICH IS THE WHOLE POINT OF THE LIST.
#: How many designs a screen searched decides what its counts are counts OF, and a panel of 9
#: registers screened 6 deep is not comparable with one of 5 screened 5 deep. Nothing in an artifact
#: could have said which had happened.
_KNOB_ENV_VARS = ("BLAST_HITLIST_SIZE", "SAVED_HITS_PER_DESIGN", "OLIGO_LEN", "WING",
                  "SCREEN_TOP_N")

#: 1-based inclusive span of the DNA gap, DERIVED from the geometry rather than typed.
#: ⛔ THIS CONSTANT EXISTED IN THREE OTHER MODULES' EXPECTATIONS AND IN NONE OF THIS ONE'S NAMESPACE
#: UNTIL 2026-08-13. `aso_premrna_offtarget._gap_region()` did `from junction_aso_offtarget import
#: GAP_REGION_1BASED` inside a bare `except Exception`, whose docstring says the point is "so a
#: geometry change cannot desynchronise the two" — and the name has never existed, so every call
#: raised ImportError and silently returned that module's own hard-coded `(6, 11)`. At the default
#: 16,5 geometry the fallback is correct, which is why nothing ever showed; under a `20,5` dispatch
#: the pre-mRNA arm would have scored the gap as [6, 11] while the screen used [6, 15]. A seam that
#: fails closed onto a right answer is indistinguishable from one that works, which is why this is
#: defined here and why the importer no longer swallows the failure.
GAP_REGION_1BASED = (ja.WING + 1, ja.OLIGO_LEN - ja.WING)

#: ⚠ WHICH KNOBS THE ENVIRONMENT SET, READ ONCE AT IMPORT — the same instant the constants above
#: were derived from it, and the instant `junction_aso` derived `OLIGO_LEN`/`WING` from it. Read at
#: call time instead, a process that mutated `os.environ` after import could make this block
#: describe an override that produced none of the values beside it. The VALUES are read at call
#: time (see `screen_parameters`) because they are the module constants themselves — if a caller
#: reassigns one, what ran is the new value, and reporting the import-time copy would be the lie.
_ENV_OVERRIDDEN = tuple(n for n in _KNOB_ENV_VARS if _env_was_set(n))


def screen_parameters():
    """The four environment-overridable knobs this screen actually ran under.

    `overridden_from_env` names the variables the environment set; every value NOT listed there came
    from this module's own default, so the two together are unambiguous without re-typing a default
    into the artifact — a default belongs to the code that reads it, and a second copy in every
    screen would be one more number to keep in sync. The VALUE is the load-bearing field either way:
    it is what ran, and it stays correct even if a default later moves.
    """
    return {
        "_what": (
            "The four environment-overridable knobs this screen ran under, recorded because they "
            "were not: before 2026-08-13 a screen's method block named the database, the program, "
            "the near-match threshold, the gap region, the breakpoint model and the parent set, and "
            "none of these — so a re-screen at a deeper BLAST ceiling was distinguishable from a "
            "default one only by its filename suffix, and a description of one such re-screen as a "
            "tenfold deeper ceiling AND retention depth was wrong about the retention with nothing "
            "in any artifact able to show it. Values not named in overridden_from_env are the "
            "module defaults. Screens committed before that date carry no parameters block and it "
            "cannot be added to them after the fact: what a past run used is not recoverable from "
            "its output, and an inferred value in a provenance field is worse than a visible gap."),
        "blast_hitlist_size": BLAST_HITLIST_SIZE,
        "saved_hits_per_design": SAVED_HITS_PER_DESIGN,
        "oligo_len": ja.OLIGO_LEN,
        "wing": ja.WING,
        "screen_top_n": N_OLIGOS,
        "n_junction_spanning_registers": ja.GAP - 1,
        "overridden_from_env": list(_ENV_OVERRIDDEN),
    }


ORIENTATION_PARSED_SINCE = "2026-08-12"

#: The three states a committed screen can be in. They are DISTINCT on purpose: the middle one is
#: the state this function used to report as the good one, and it is the one that cost a paper.
ORIENTATION_FILTERED = "orientation_filtered"
ORIENTATION_LABELS_STRAND_BLIND = "orientation_parsed_but_labels_are_strand_blind_upper_bounds"
ORIENTATION_UNPARSED = "orientation_UNPARSED_counts_are_upper_bounds"
#: ⛔ A FOURTH STATE, BECAUSE "NOTHING TO PARSE" WAS BEING REPORTED AS "NOT PARSED" (2026-08-13).
#: A screen whose designs return NO near-match at all stores no hit, so no hit carries `hit_frame`,
#: so the parsed flag below never went true and the screen was graded an upper bound of unknown
#: tightness. That is an ABSENT READING reported as a READING OF ABSENCE — this module's own §4
#: failure — and it runs in the flattering-to-nobody direction: the cleanest possible screen, the one
#: with zero hits, was the one labelled least trustworthy. Measured when the 5-10-5 screens landed:
#: two of them return zero near-matches across every screened design and both were graded UNPARSED,
#: while the only two committed screens in that state genuinely carry hits and are genuinely
#: unparsed, so no published count moves.
#: ⚠ KEPT DISTINCT FROM `ORIENTATION_FILTERED` rather than folded into it. "No hit existed" and
#: "hits existed and every minus-strand one was diverted" are different facts about a screen, and a
#: reader deciding what a zero means needs to be able to tell them apart.
ORIENTATION_NO_HITS = "no_offtarget_hits_to_orient"


def screen_orientation_status(screen):
    """Whether a committed screen's COUNTS were actually filtered by alignment orientation.

    ⛔⛔ THIS ASKED THE WRONG QUESTION UNTIL 2026-08-12, AND IT ASKED IT ONE LEVEL ABOVE THE BUG IT
    WAS WATCHING FOR. It returned "orientation_parsed" the moment ANY hit carried `hit_frame` —
    that is, it tested whether the FIELD WAS PRESENT, not whether any count had been computed with
    it. `classify()`'s own docstring, thirty lines below, warns in bold that parsing `hit_frame`
    alone fixed nothing because the classifier never read it; this function then made exactly that
    mistake about the classifier.

    ⚠ **A POPULATED FIELD IS NOT A MEASURED ONE.** Measured on the committed corpus the day this
    was rewritten: four screens (TFG e3, e4, e5, e7) carry `hit_frame` on every hit and were
    classified before the strand branch landed, so every one of their minus-strand hits is still
    labelled `true_cleavage_risk` or `gap_disrupted_no_cleavage`. All four were being reported as
    `orientation_parsed`, and 83 non-liabilities were being counted as cleavage risks inside a
    corpus described in a manuscript as orientation-filtered throughout.

    ⛔ **THE AUDIT IS ON THE LABELS, NOT THE FIELD**, because the labels are what every count is
    built from. A screen is FILTERED only if no hit is simultaneously `is_minus_strand: True` and
    labelled anything other than `minus_strand_not_hybridisable`. A screen with no minus-strand
    hits at all is filtered trivially and truthfully — there was nothing to divert.

    ⚠ Recovery is NOT possible for a strand-blind screen, which is why it is demoted rather than
    re-scored: only the top 15 hits are stored against a hitlist of up to 50, so the strand of the
    truncated tail is simply gone. An upper bound is the honest reading and the only available one.

    ⛔⛔ AND A SCREEN WITH NO HITS AT ALL WAS BEING GRADED `ORIENTATION_UNPARSED` UNTIL 2026-08-13,
    WHICH IS A FAIL-TOWARD-DOUBT BUG AND WILL BITE ANY FUTURE CLEAN SCREEN. The parsed flag went
    true only when some STORED HIT carried `hit_frame`. A design that returns no near-match stores
    no hit; a screen whose every design returns none therefore stored nothing, nothing carried the
    field, and the screen was labelled "counts are upper bounds of unknown tightness" — over a set
    of counts that are all ZERO and cannot be an upper bound of anything. **The cleanest possible
    result was graded the least trustworthy**, and the direction is the dangerous one: it does not
    exaggerate a liability, it withholds credit from a design that has none, which is exactly the
    kind of error nobody goes looking for because it reads as caution.
    ⚠ IT IS THE SAME MISTAKE THIS FUNCTION'S OWN HISTORY IS ABOUT, ONE LEVEL FURTHER OUT. The block
    above records that it used to test whether the FIELD WAS PRESENT rather than whether any count
    had been computed with it; this tested whether the field was present rather than whether
    anything EXISTED to carry it. An absent reading is not a reading of absence (CLAUDE.md §4) —
    and "no hits were found" is a reading, not an absence.
    ⛔ THE FIX IS SCOPED TO COMPLETE HIT LISTS AND MUST STAY THAT WAY. Zero STORED hits against a
    NON-ZERO near-match count is a censored screen, not an empty one: its hits exist, their strand
    is unrecoverable, and it keeps the upper-bound label. Admitting that case would hand a clean
    verdict to precisely the screens the orientation retraction was about.
    ⚠ `ORIENTATION_NO_HITS` IS KEPT DISTINCT FROM `ORIENTATION_FILTERED` rather than folded into it,
    because "no hit existed" and "hits existed and every minus-strand one was diverted" are
    different facts about a screen, and a reader deciding what a zero means needs to tell them
    apart. `screen_counts_are_orientation_filtered` accepts both, since a set of zeros is
    orientation-safe either way. Measured before landing: no committed screen is in the new state,
    so nothing published moves; the two committed screens that read UNPARSED genuinely carry hits
    and are genuinely unparsed.
    """
    parsed = False
    saw_minus = False
    n_hits = 0
    for o in screen.get("oligos", []):
        for h in (o.get("offtargets") or []):
            n_hits += 1
            if "hit_frame" in h:
                parsed = True
            if h.get("is_minus_strand") is True:
                saw_minus = True
                if h.get("risk") != "minus_strand_not_hybridisable":
                    return ORIENTATION_LABELS_STRAND_BLIND
    if not parsed:
        # ⛔ ORDER MATTERS: ask "were there hits" BEFORE "were they parsed". A screen that stored no
        # hit has nothing whose orientation could have been read, and calling that UNPARSED grades
        # the cleanest possible result as the least trustworthy one. Scoped to screens whose stored
        # lists are COMPLETE — a truncated list of zero saved hits against a non-zero count is a
        # censored screen, not an empty one, and must keep its upper-bound label.
        if n_hits == 0 and all(
                (o.get("n_offtarget_near_matches") == 0)
                for o in screen.get("oligos", []) if o.get("status") == "screened"):
            return ORIENTATION_NO_HITS
        return ORIENTATION_UNPARSED
    # ⚠ Parsed, and every minus-strand hit was diverted — including the vacuous case of a screen
    # that returned none. `saw_minus` is reported for the reader; it does not change the verdict.
    return ORIENTATION_FILTERED


def screen_counts_are_orientation_filtered(screen_or_status):
    """THE predicate. Accepts a screen dict or an already-computed status string.

    One home, because the previous consumer tested `"UNPARSED" not in status` — a substring sniff
    that silently answers True for any new failure state whose name lacks that word, which is
    precisely what a newly-named state is.
    """
    status = (screen_or_status if isinstance(screen_or_status, str)
              else screen_orientation_status(screen_or_status))
    # ⚠ `ORIENTATION_NO_HITS` PASSES, AND IT IS NOT A LOOSENING. Every count in such a screen is
    # zero, so there is no count an orientation filter could have changed — the predicate asks
    # whether the counts are orientation-safe, and a set of zeros is. Measured before landing: no
    # committed screen is in that state, so nothing published moves.
    return status in (ORIENTATION_FILTERED, ORIENTATION_NO_HITS)


#: RefSeq writes the approved gene symbol in parentheses immediately before a record's qualifiers:
#: "Homo sapiens FUS RNA binding protein (FUS), transcript variant 1, mRNA". That is the ANCHOR —
#: not a hopeful convention but a measured one: over every hit stored in every committed screen in
#: this tree (2026-08-13), **6767 of 6767 definition lines carry this `(SYMBOL),` form**, and none
#: is missing it. Trailing `$` is allowed for a record whose symbol ends the line.
_REFSEQ_SYMBOL = re.compile(r"\(([A-Za-z0-9][A-Za-z0-9._@#/-]*)\)\s*(?=,|$)")


def _symbol_as_a_whole_word(sym, defn_upper):
    """Is `sym` present as a standalone token, rather than buried inside a longer word?

    The lookarounds are the entire fix for the substring collision: they refuse a match whose
    neighbouring character is alphanumeric, so MITOFUSIN, FUSING and FUSION stop containing FUS.
    """
    return re.search(r"(?<![A-Z0-9])" + re.escape(sym) + r"(?![A-Z0-9])", defn_upper) is not None


def is_parent(h):
    """Is this BLAST hit one of the fusion's PARENT transcripts, rather than an off-target?

    A parent hit is dropped before `n_offtarget_near_matches` is computed, because each parent
    matches one wing of a junction oligo by construction. So a FALSE POSITIVE here silently removes
    a real off-target from every count the paper quotes — it does not produce a visible error, it
    produces a smaller number.

    ⛔ AND THE NAME ARM USED TO BE A BARE SUBSTRING OF THE DEFINITION LINE, WHICH FIRES ON WORDS
    THAT MERELY CONTAIN A SYMBOL (2026-08-13). `PARENT_GENES` carries three- and four-character
    symbols, and for donor gene FUS it carries "FUS" and "TLS". `"FUS" in defn.upper()` is
    therefore True of, among others:
        "Homo sapiens mitofusin 1 (MFN1), transcript variant 1, mRNA"        -> MITOFUSIN
        "Homo sapiens N-ethylmaleimide sensitive factor, vesicle fusing ATPase"  -> FUSING
        "PREDICTED: Homo sapiens BCR-ABL fusion transcript, misc_RNA"        -> FUSION
    Every one of those would have been counted as a parent and dropped from the near-match count of
    every FUS-donor screen, with nothing in the artifact to show it had happened.

    ⚠ MEASURED EXPOSURE IS NIL, AND THAT IS WHY THIS IS A CORRECTION TO THE CODE AND NOT TO A
    PUBLISHED NUMBER. Over every hit stored in every committed screen (2026-08-13): **0 of 6767
    definition lines contain "FUS" or "TLS" in any form**, so no committed count moves. It is fixed
    because the next screen at a new donor is the one that pays, and because a filter that has
    never yet been wrong is not thereby right.

    ⛔ THE NEW PREDICATE IS A STRICT SUBSET OF THE OLD ONE, WHICH IS THE PROPERTY THAT MAKES IT SAFE
    TO LAND WITHOUT RE-RUNNING ANYTHING. Each of the three name arms below implies the old
    substring test: a parenthesised `(FUS)` contains "FUS", a phrase match IS a substring match,
    and a whole-word match is a substring match with lookarounds. So no hit that is currently
    STORED can become a parent, and no committed near-match count can silently re-base. The only
    direction that can move is a hit the old code dropped and the new code keeps — which is exactly
    the collision class above.

    Three name arms, loosest last and each one narrower than the arm it replaces:
      1. the RefSeq gene symbol, parenthesised — the arm that actually decides; see
         `_REFSEQ_SYMBOL` above for the corpus measurement that supports it;
      2. a multi-word descriptive alias, as a substring — UNCHANGED, because a phrase that long
         cannot collide the way a symbol does, and changing it could re-base a committed count;
      3. a bare symbol as a WHOLE WORD — kept only so a definition line carrying no parenthesised
         symbol (a `complete cds` GenBank-style record, say) behaves as it always did. The corpus
         contains no such line, so this arm is a guard against re-basing rather than a measured
         need; deleting it would be a second behaviour change with no evidence behind it.
    """
    acc = h["acc"].split(".")[0]
    if acc in PARENT_ACCS:
        return True
    d = h["defn"].upper()
    symbols = {m.group(1).upper() for m in _REFSEQ_SYMBOL.finditer(d)}
    if symbols.intersection(PARENT_SYMBOLS):
        return True
    if any(p in d for p in PARENT_PHRASES):
        return True
    return any(_symbol_as_a_whole_word(s, d) for s in PARENT_SYMBOLS)


def gap_mismatch_profile(h):
    """(reaches_gap, gap_fully_covered, n_gap_mismatches or None) for one BLAST HSP.

    Cleavage needs a contiguous DNA:RNA duplex across the central DNA gap (query positions
    [WING+1 .. LEN-WING]). This walks the alignment, maps each column to a query position and
    counts mismatches inside the gap. `n_gap_mismatches` is None when the alignment strings are
    absent, which is the coverage-only fallback case and must never be read as zero."""
    gap_lo, gap_hi = GAP_REGION_1BASED                         # 1-based inclusive gap span
    if not (h["q_from"] <= gap_lo and h["q_to"] >= gap_hi):
        return False, False, None
    qseq, mid = h.get("qseq", ""), h.get("midline", "")
    if not qseq or not mid or len(qseq) != len(mid):
        return True, False, None                               # reaches it; cannot resolve it
    qpos = h["q_from"]
    gap_mismatches, gap_covered = 0, set()
    for qc, mc in zip(qseq, mid):
        if qc == "-":                                          # insertion in target; query pos unchanged
            continue
        if gap_lo <= qpos <= gap_hi:
            gap_covered.add(qpos)
            if mc != "|":
                gap_mismatches += 1
        qpos += 1
    if len(gap_covered) < (gap_hi - gap_lo + 1):
        return False, False, None
    return True, True, gap_mismatches


def _locus_summary(ranked):
    """Gene-locus counts over the COMPLETE ranked hit list, written into the screen record.

    The arithmetic lives in `junction_aso_locus_collapse` and is imported rather than repeated, so
    a screen produced today and an artifact recounted after the fact cannot disagree about what a
    locus is. Imported lazily: that module reads this one's orientation verdict, and a module-level
    import in both directions would be a cycle.
    """
    try:
        from junction_aso_locus_collapse import accession_class, locus_of  # noqa: PLC0415
    except ImportError:  # pragma: no cover — the screen must not fail over a reporting extra
        return {}
    by_locus = {}
    for h in ranked:
        by_locus.setdefault(locus_of(h), []).append(h)
    predicted_only = [k for k, v in by_locus.items()
                      if {accession_class(h) for h in v} == {"predicted"}]
    risk_loci = sorted(k for k, v in by_locus.items()
                       if any(str(h.get("risk") or "").startswith("true_cleavage") for h in v))
    return {
        "n_distinct_loci": len(by_locus),
        "n_loci_seen_only_as_predicted_models": len(predicted_only),
        "n_loci_with_a_gap_spanning_hit": len(risk_loci),
        "loci_with_a_gap_spanning_hit": risk_loci,
    }


def classify(h):
    """RNase-H cleavage relevance, resolved to the gap-mismatch level.

      - gap not fully covered  -> "wing_only_affinity_risk"  (no gap duplex; weak liability)
      - gap covered, 0 gap mismatches -> "true_cleavage_risk" (the real RNase-H liability)
      - gap covered, >=1 gap mismatch -> "gap_disrupted_no_cleavage" (mismatch falls in the gap)
      - alignment strings absent      -> "gap_spanning_cleavage_risk" (coverage-only fallback)

    ⛔ THESE LABELS ARE A PARTITION, NOT A VERDICT. `gap_disrupted_no_cleavage` says where the
    mismatch fell; it does NOT say the transcript is safe, and reading it as zero risk is the
    defect `grade_panel()` below exists to correct — see DISCRIMINATION_MODELS.

    ⛔⛔ ORIENTATION IS CHECKED FIRST, AND UNTIL 2026-08-12 IT WAS NOT CHECKED AT ALL. `blastn`
    searches both strands. A transcript matching the REVERSE COMPLEMENT of the target window is not
    a liability in any degree: an antisense oligonucleotide cannot hybridise to it, so there is no
    duplex, no RNase-H substrate and nothing to cleave. Those hits were nevertheless passing the
    identity filter and being labelled `true_cleavage_risk`.
    ⚠ AND PARSING `hit_frame` ALONE FIXED NOTHING. The field was captured a week earlier and this
    function never read it, so every reported count still included minus-strand hits — the
    instrumentation was in place and the number it was supposed to correct had not moved. Measured
    once this branch actually diverted them: **55 % of the gap-spanning "risks" on the EWSR1
    junctions are minus-strand**, ranging from 7 % at e13 to 89 % at e7. That spread is why it
    matters beyond a rescale — it reorders the junctions.

    ⛔ `None` IS NOT `False`. A screen produced before the parse carries no `hit_frame`, and an
    absent reading must not be promoted to "plus strand, therefore a real risk" OR demoted to safe.
    Only an explicit `True` diverts, so pre-fix artifacts keep exactly the counts they had and stay
    honestly labelled upper bounds, while re-run artifacts get the measurement."""
    if h.get("is_minus_strand") is True:
        return "minus_strand_not_hybridisable"
    reaches, covered, n_mm = gap_mismatch_profile(h)
    if not reaches:
        return "wing_only_affinity_risk"
    if not covered:
        return "gap_spanning_cleavage_risk"                    # coverage-only fallback
    if n_mm == 0:
        return "true_cleavage_risk"
    if n_mm is None:                                           # unreachable; defensive
        return "gap_spanning_cleavage_risk"
    return "gap_disrupted_no_cleavage"


# ─────────────────────────────────────────────────────────────────────────────────────────
# THE DISCRIMINATION MODEL — why "gap mismatch ⇒ 0 predicted-cleavable" is not a call we may make
# ─────────────────────────────────────────────────────────────────────────────────────────
# ⛔ THE PANEL'S ORIGINAL HEADLINE COUNTED EVERY GAP-DISRUPTED NEAR-MATCH AS ZERO-CLEAVABLE, AND
# THE PRIMARY LITERATURE DOES NOT SUPPORT THAT. Two retrieved sources, both anchored in
# research/manuscripts/aso/lit-targets-aso-verify.json and both re-verified against PubMed, Europe PMC
# and Crossref on 2026-08-08 (Actions run 31276141296):
#
#   * PMID 23963702 (Østergaard ME, Southwell AL, Kordasiewicz H, Watt AT, Skotte NH, Doty CN,
#     Vaid K, Villanueva EB, Swayze EE, Bennett CF, Hayden MR, Seth PP; Nucleic Acids Res
#     41(21):9634-50, 2013; doi 10.1093/nar/gkt725) — "ASOs have been previously shown to
#     discriminate single nucleotide changes in targeted RNAs with ~5-fold selectivity … The
#     resulting oligonucleotides demonstrate >100-fold discrimination …" where "the resulting"
#     means ASOs carrying POSITIONAL CHEMICAL MODIFICATIONS placed to limit RNase H cleavage of
#     the non-targeted transcript. So an UNMODIFIED gapmer — which is all this panel's designs are
#     — buys ~5-fold, and the >100-fold figure requires chemistry these designs do not carry.
#     REDUCTION, NOT ABOLITION.
#
#   * PMID 7567450 (Duroux I, Godard G, Boidot-Forget M, Schwab G, Hélène C, Saison-Behmoaras T;
#     Nucleic Acids Res 23(17):3411-3418, 1995; doi 10.1093/nar/23.17.3411) — "Short
#     oligonucleotides (12- or 13mers) centered on the mutation had a very high discriminatory
#     efficiency. Longer oligonucleotides (16mers) DID NOT DISCRIMINATE EFFICIENTLY between the
#     mutated and the normal mRNA." ⚠ THIS PANEL'S DESIGNS ARE 16-MERS (ja.OLIGO_LEN). The one
#     retrieved result that speaks to this geometry speaks against it, and it is a length effect —
#     so it cannot be argued away by choosing a better mismatch position.
#
# Consequence: there is no defensible fold value, only a RANGE whose two ends are these two papers.
# The panel is therefore scored under BOTH, and neither end is reported alone.
DISCRIMINATION_MODELS = {
    "ostergaard_5fold": {
        "fold_per_gap_mismatch": 5.0,
        "source": "PMID 23963702 (doi 10.1093/nar/gkt725)",
        "what": ("~5-fold discrimination per single-nucleotide change for an UNMODIFIED "
                 "RNase-H-active ASO. The OPTIMISTIC end: it is the figure for a gapmer chosen "
                 "and positioned for allele selectivity, which these designs were not."),
    },
    "duroux_16mer_none": {
        "fold_per_gap_mismatch": 1.0,
        "source": "PMID 7567450 (doi 10.1093/nar/23.17.3411)",
        "what": ("16-mers 'did not discriminate efficiently'; discrimination in that assay was "
                 "confined to 12-13mers centred on the mismatch. The PESSIMISTIC end, and the "
                 "one matching this panel's oligo LENGTH: a gap-internal mismatch buys nothing, "
                 "so every near-match counts at full weight."),
    },
}

# ⛔ RETIRED, KEPT NAMED SO THE OLD FIGURE STAYS TRACEABLE. `fold = inf` is the assumption that
# produced "2 of 5 predicted off-target-clean". It is not in DISCRIMINATION_MODELS because it is
# not a model the literature supports — it is the thing being corrected.
RETIRED_ABOLITION_MODEL = {
    "name": "all_gap_mismatch_blocks_cleavage",
    "fold_per_gap_mismatch": float("inf"),
    "why_retired": ("no retrieved source supports abolition; both sources above measure or imply "
                    "a finite fold, and the one that matches the 16-mer length implies ~none."),
}

# Total mismatches over a near-match are bounded by (OLIGO_LEN - NEAR_MATCH_MIN_IDENT), so a
# gap-disrupted hit carries at least 1 and at most that many gap-internal mismatches. That bound is
# what lets a TRUNCATED off-target list still yield an exact interval rather than a guess.
MAX_MISMATCHES_PER_NEAR_MATCH = ja.OLIGO_LEN - NEAR_MATCH_MIN_IDENT


def cleavage_weight(n_gap_mismatches, fold):
    """Residual predicted cleavage of one off-target, relative to a perfect gap duplex (= 1.0).

    fold**-n. ⚠ Independence across mismatches is an ASSUMPTION — neither source measures two
    gap-internal mismatches — and it is recorded as one in the artifact rather than buried here."""
    if n_gap_mismatches <= 0:
        return 1.0
    if fold == float("inf"):
        return 0.0
    return float(fold) ** (-int(n_gap_mismatches))


def grade_one(oligo, fold):
    """Residual predicted cleavage LOAD for one screened oligo, as a closed interval.

    The interval is not a confidence interval. Its width is TRUNCATION: `screen_one` saves only
    the strongest 15 off-targets, while the per-oligo counters are complete, so hits beyond the
    saved list are known to be gap-disrupted but not to what depth. Each such hit is bounded by
    `cleavage_weight(MAX_MISMATCHES_PER_NEAR_MATCH, fold) .. cleavage_weight(1, fold)`.
    Where the saved list covers every near-match, lo == hi and `exact` is True."""
    n_true = int(oligo.get("n_true_cleavage_risk") or 0)
    n_gapdis = int(oligo.get("n_gap_disrupted_no_cleavage") or 0)
    n_fallback = int(oligo.get("n_coverage_only_fallback") or 0)
    n_wing = int(oligo.get("n_wing_only_affinity") or 0)
    saved = oligo.get("offtargets") or []

    hist = oligo.get("gap_mismatch_histogram")

    # ⛔⛔ THE HISTOGRAM COUNTS HITS AN ANTISENSE OLIGONUCLEOTIDE CANNOT BIND, AND THAT PUT THIS
    # PAPER'S CENTRAL NEGATIVE ON NON-LIABILITIES (2026-08-12). `gap_mismatch_histogram` is written
    # over every ranked hit regardless of strand. `classify()` was fixed to divert minus-strand
    # hits and `n_true_cleavage_risk` fell to 0 for the clean designs — while the histogram beside
    # it still read {"0": 7, "1": 1} for an oligonucleotide whose eight hits are ALL minus-strand.
    # The graded load is then 0.2 rather than 0, and `zero_predicted_cleavage_load` reads False for
    # a design the paper reports as carrying no hybridisable near-match. A reviewer downloading the
    # archive sees the graded artifact contradict the headline, and both are ours.
    #
    # ⚠ REPAIRED ONLY WHERE IT CAN BE, WHICH IS WHERE THE SAVED LIST IS COMPLETE. `screen_one`
    # keeps the strongest 15 of a hitlist up to 50, so for a censored design the strand of the tail
    # is gone and no honest recount exists — those keep the strand-blind histogram and are marked,
    # so the load stays the upper bound it has always been rather than silently improving.
    saved_all = oligo.get("offtargets") or []
    n_near = int(oligo.get("n_offtarget_near_matches") or 0)
    complete = bool(saved_all) and len(saved_all) == n_near
    strand_known = any(h.get("is_minus_strand") is not None for h in saved_all)
    hist_strand_aware = False
    if hist and complete and strand_known:
        rebuilt = {str(n): 0 for n in range(0, MAX_MISMATCHES_PER_NEAR_MATCH + 1)}
        for h in saved_all:
            if h.get("is_minus_strand") is True:
                continue                                   # not hybridisable, not a liability
            n_mm = h.get("gap_mismatches")
            if n_mm is not None and str(n_mm) in rebuilt:
                rebuilt[str(n_mm)] += 1
        hist, hist_strand_aware = rebuilt, True

    if hist:
        # ⭐ COMPLETE histogram over every ranked hit — written by screens run after 2026-08-08.
        # No truncation, so the interval collapses to a point.
        resolved = sum(int(v) for k, v in hist.items() if int(k) > 0)
        resolved_load = sum(int(v) * cleavage_weight(int(k), fold)
                            for k, v in hist.items() if int(k) > 0)
    else:
        # ⚠ PRE-2026-08-08 SCREEN: only the strongest 15 off-targets carry alignments, so the
        # tail is known to be gap-disrupted but not to what depth. Bounded, never guessed.
        resolved, resolved_load = 0, 0.0
        for h in saved:
            _, covered, n_mm = gap_mismatch_profile(h)
            if covered and n_mm and n_mm > 0:
                resolved += 1
                resolved_load += cleavage_weight(n_mm, fold)
    unresolved = max(0, n_gapdis - resolved)
    w_hi = cleavage_weight(1, fold)
    w_lo = cleavage_weight(MAX_MISMATCHES_PER_NEAR_MATCH, fold)

    # a full-gap-duplex hit and a coverage-only fallback both count at full weight
    base = float(n_true + n_fallback)
    lo = base + resolved_load + unresolved * w_lo
    hi = base + resolved_load + unresolved * w_hi
    return {
        "n_offtarget_near_matches": int(oligo.get("n_offtarget_near_matches") or 0),
        "n_full_gap_duplex": n_true,
        "n_gap_disrupted": n_gapdis,
        "n_gap_disrupted_resolved_from_saved_alignments": resolved,
        "n_gap_disrupted_unresolved_by_truncation": unresolved,
        "n_coverage_only_fallback_counted_at_full_weight": n_fallback,
        "n_wing_only_not_counted": n_wing,
        "residual_cleavage_load_lo": round(lo, 4),
        "residual_cleavage_load_hi": round(hi, 4),
        "exact": unresolved == 0,
        "zero_predicted_cleavage_load": hi == 0.0,
        # ⚠ WHICH HISTOGRAM THIS LOAD WAS BUILT ON, stated per oligo rather than per screen,
        # because within one screen some designs are censored and some are not. False means the
        # count still includes minus-strand hits and the load is an upper bound of unknown
        # tightness — not a measurement of hybridisable liability.
        "gap_histogram_orientation_filtered": hist_strand_aware,
    }


def grade_panel(screen):
    """Re-score a committed screen artifact under the graded models. NO NETWORK, NO RE-BLAST.

    ⛔ DELIBERATELY DERIVED FROM THE COMMITTED SCREEN RATHER THAN A FRESH ONE. A new BLAST would
    return a different hit set, and the old and new headline figures would then differ for two
    reasons at once — the model change and the retrieval change — which is exactly the comparison
    a corrected headline must not be muddied by. The hit set is held fixed; only the scoring moves.

    ⛔⛔ THE GEOMETRY IS THE SCREEN'S, NOT THIS MODULE'S — AND WRITING THIS MODULE'S WAS A LIVE
    DEFECT THAT SURVIVED THE GEOMETRY SWEEP OF 2026-08-14 (found and reproduced the same day).
    `oligo_len`, `gap_region_1based` and `near_match_threshold` below were `ja.OLIGO_LEN` /
    `GAP_REGION_1BASED` / `NEAR_MATCH_MIN_IDENT` — the geometry THIS PROCESS'S environment built,
    which is the manuscript's 5-6-5 unless a dispatch overrode it. Step 0 of
    `scripts/regenerate_aso_chain.sh` rescores EVERY `junction-aso-offtarget-*.json` in one sweep,
    so the first chain run after the 18-mer and 20-mer screens landed would have written graded
    artifacts stating `oligo_len: 16`, `gap_region_1based: [6, 11]` and `>= 14/16 identical` over
    18-mer and 20-mer designs — and `submission_tables._graded_loads` globs those into the
    manuscript's residual-load column. Reproduced end to end on
    `junction-aso-offtarget-e12n3-18mer-deep500.json` before this fix: `oligo_len` 16 beside designs
    measured at 18, `>= 14/16` on a screen that ran at 16/18.
    ⚠ NOTHING COMMITTED WAS AFFECTED — the chain had not been re-run since those screens landed, so
    all 39 graded artifacts on disk are 16-mer, and re-grading every committed screen after this fix
    reproduces all 39 byte-for-byte. Latent is what this fix is for.
    ⭐ AND IT IS THE ARGUMENT FOR THE LOADER RATHER THAN FOR ANOTHER PER-CONSUMER GUARD: three
    generators were fixed by hand on 2026-08-14, each after its own symptom was caught by a human,
    and this one — which no symptom had reached yet — was not among them.
    """
    import aso_screen_sets as ass                                             # noqa: PLC0415
    geom = ass.geometry_of(ass.BLAST_SCREEN, screen,
                           where=f"screen for {screen.get('junction_label') or '<unlabelled>'}")
    graded, per_model = {}, {}
    ok = [o for o in screen.get("oligos", []) if o.get("status") == "screened"]
    for name, m in DISCRIMINATION_MODELS.items():
        fold = m["fold_per_gap_mismatch"]
        rows = {o["antisense_5to3"]: grade_one(o, fold) for o in ok}
        graded[name] = rows
        per_model[name] = {
            **m,
            "n_oligos_with_zero_predicted_cleavage_load": sum(
                1 for r in rows.values() if r["zero_predicted_cleavage_load"]),
            "rank_best_first": [k for k, _ in sorted(
                rows.items(), key=lambda kv: (kv[1]["residual_cleavage_load_hi"],
                                              kv[1]["residual_cleavage_load_lo"], kv[0]))],
        }
    retired = sum(1 for o in ok if int(o.get("n_true_cleavage_risk") or 0) == 0)
    return {
        "_what": ("Graded re-score of a committed gap-resolved off-target screen. Replaces the "
                  "binary 'a mismatch in the DNA gap abolishes RNase-H cleavage' assumption with "
                  "the fold-discrimination the primary literature actually reports."),
        "_the_correction": (
            f"Under the retired abolition assumption {retired} of {len(ok)} oligos scored "
            f"'0 predicted-cleavable off-targets' and were called predicted off-target-clean. "
            "Under BOTH literature-supported models that count is 0 of "
            f"{len(ok)}: every design retains a non-zero predicted residual cleavage load, "
            "because every design has at least one gap-disrupted near-match and a gap-disrupted "
            "near-match is reduced, not abolished. What survives is a RANK ORDER, not a "
            "clean/dirty call."),
        "_what_this_is_not": [
            "Not a measurement. No RNase-H1 cleavage was measured here or anywhere in this "
            "repository; this re-weights a BLAST-derived prediction under a literature prior.",
            "Not a safety, efficacy or selectivity claim, and not a therapeutic-window statement.",
            "Wing-only near-matches (alignment does not reach the DNA gap) are scored 0 for "
            "CLEAVAGE and are not thereby harmless — they remain affinity liabilities, counted "
            "separately as n_wing_only_not_counted.",
            "Independence across two gap-internal mismatches is an assumption. Neither source "
            "measures it, which is why the pessimistic model (fold 1.0) is reported alongside.",
            "The interval width is TRUNCATION of the saved off-target list, not statistical "
            "uncertainty. Where `exact` is true there is no truncation.",
        ],
        "retired_model": RETIRED_ABOLITION_MODEL,
        "retired_model_headline": f"{retired} of {len(ok)} predicted off-target-clean",
        # ⛔ Every field below is the SCREEN's geometry, measured from its designs — see the
        # docstring. `geom` is None only for a screen holding no design at all, in which case there
        # is nothing graded and the fields state their own absence rather than this module's values.
        "near_match_threshold": (
            f">= {geom.oligo_len - 2}/{geom.oligo_len} identical" if geom else None),
        "oligo_len": geom.oligo_len if geom else None,
        "gap_region_1based": list(geom.gap_region_1based) if geom else None,
        "max_mismatches_per_near_match": MAX_MISMATCHES_PER_NEAR_MATCH,
        # ⛔ THE SEARCH DEPTH IS THE SCREEN'S TOO, AND IT HAS TO BE CARRIED OR IT IS UNRECOVERABLE
        # (2026-08-14). A re-score holds no hits of its own — only per-design loads — so nothing in
        # this artifact's shape can say whether the search behind it stopped at the default ceiling
        # or ten times deeper. `aso_screen_sets.is_deep` therefore answered False for every graded
        # artifact ever written, and `submission_tables._graded_loads` pooled a default and a deep
        # re-score of the same seam into one Table 3 cell: `31.4 / 101 / 0 / 0` for
        # `GGGCATATCTCTATAA`, in a table whose legend says it reports the default-depth result.
        # ⚠ EVIDENCE, NOT A VERDICT. What is stored is the ceiling the screen recorded and the hits
        # it actually retained; the comparison against the default stays in `is_deep`, so a graded
        # artifact cannot carry a stale "deep" judged against a threshold that has since moved.
        "source_screen_depth": ass.BLAST_SCREEN.depth_evidence(screen),
        "models": per_model,
        "per_oligo": graded,
        "source_screen": screen.get("junction_label"),
        "source_breakpoint": screen.get("breakpoint"),
    }


def screen_is_gap_resolved(screen):
    """Can this screen be graded at all? A COVERAGE-ONLY screen cannot, and must not be zeroed.

    ⛔ ADDED 2026-08-12 AFTER `--rescore` PRODUCED A CLEAN CALL OUT OF MISSING DATA. Rescoring
    every committed screen in one sweep included `junction-aso-offtarget-bp200-8.json`, which is
    the pre-gap-resolution coverage-only screen: its oligos carry `n_true_cleavage_risk: null`,
    no `gap_mismatch_histogram`, and no per-hit gap profile. `grade_one` reads those absent fields
    through `int(... or 0)`, so every term evaluated to zero and the artifact announced
    **"4 of 4 with zero predicted cleavage load"** — the strongest possible claim, manufactured
    entirely from the absence of the data needed to test it. That is an absent reading rendered as
    a reading of absence (CLAUDE.md §4), in the one file a reader would quote to say a design is
    clean, and it is the same shape as the retracted "2 of 5 clean" this whole grading model exists
    to correct. A screen that cannot be graded must REFUSE, not score zero.
    """
    ok = [o for o in screen.get("oligos", []) if o.get("status") == "screened"]
    if not ok:
        return False, "no successfully screened oligos"
    # Gap resolution is present if ANY screened oligo carries a resolved gap reading: either the
    # complete histogram (post-2026-08-08 screens) or a non-null true-cleavage counter.
    resolved = [o for o in ok if o.get("gap_mismatch_histogram")
                or o.get("n_true_cleavage_risk") is not None]
    if not resolved:
        return False, ("coverage-only screen — no gap_mismatch_histogram and no "
                       "n_true_cleavage_risk on any oligo, so cleavage load is UNMEASURED here, "
                       "not zero. Re-run the screen with gap resolution; do not grade this file.")
    return True, ""


def rescore(paths):
    """`--rescore <screen.json> ...` -> writes `<screen>-graded.json` beside each. $0, offline."""
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            screen = json.load(fh)
        gradeable, why = screen_is_gap_resolved(screen)
        if not gradeable:
            print(f"REFUSED {os.path.basename(p)}: {why}", file=sys.stderr)
            continue
        out = p[:-5] + "-graded.json" if p.endswith(".json") else p + "-graded.json"
        art = grade_panel(screen)
        art["_generated_from"] = os.path.basename(p)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(art, fh, indent=2)
        print("wrote", out, file=sys.stderr)
        print(json.dumps({"source": os.path.basename(p),
                          "retired_headline": art["retired_model_headline"],
                          "correction": art["_the_correction"],
                          "models": {k: {"zero_load": v["n_oligos_with_zero_predicted_cleavage_load"],
                                         "rank": v["rank_best_first"]}
                                     for k, v in art["models"].items()}}, indent=2))
    return 0


def screen_one(design, rid=None):
    """Screen one design. `rid` lets a caller submit first and collect later — see `screen_all`."""
    target = design["target_mRNA_5to3"]
    rec = {"antisense_5to3": design["antisense_5to3"], "target_mRNA_5to3": target,
           "gc_percent": design["gc_percent"], "specificity_margin": design["specificity_margin"]}
    try:
        if rid is None:
            rid = blast_put(target)
        blast_poll(rid)
        hits = blast_hits(rid)
        offt = [h for h in hits
                if h["identity"] >= NEAR_MATCH_MIN_IDENT and not is_parent(h)]
        # dedup by accession, keep the strongest HSP
        best = {}
        for h in offt:
            k = h["acc"]
            if k not in best or h["identity"] > best[k]["identity"]:
                h["risk"] = classify(h)
                # ⭐ CARRIED PER HIT so a graded re-score never has to re-walk the alignment, and
                # so the DEPTH of gap disruption survives the `[:15]` truncation for saved hits.
                h["gap_mismatches"] = gap_mismatch_profile(h)[2]
                best[k] = h
        ranked = sorted(best.values(), key=lambda h: (-h["identity"], h["acc"]))
        rec.update({
            "status": "screened",
            "blast_rid": rid,
            "n_parent_or_intended_hits": sum(1 for h in hits if is_parent(h)),
            "n_offtarget_near_matches": len(ranked),
            "n_true_cleavage_risk": sum(1 for h in ranked if h["risk"] == "true_cleavage_risk"),
            "n_gap_disrupted_no_cleavage": sum(1 for h in ranked
                                               if h["risk"] == "gap_disrupted_no_cleavage"),
            "n_wing_only_affinity": sum(1 for h in ranked if h["risk"] == "wing_only_affinity_risk"),
            "n_coverage_only_fallback": sum(1 for h in ranked
                                            if h["risk"] == "gap_spanning_cleavage_risk"),
            # ⛔ COMPLETE HISTOGRAM OVER ALL RANKED HITS, not just the 15 saved below. Without it a
            # graded re-score can only BOUND the truncated tail; with it the bound is exact.
            # ⛔⛔ HYBRIDISABLE HITS ONLY — AND THIS IS THE THIRD PLACE THE SAME OMISSION HID
            # (2026-08-12). `Hsp_hit-frame` was parsed, and no number moved because `classify()`
            # never read it. `classify()` was then fixed, and the GRADED re-score still did not
            # move, because it reads THIS histogram — which was built over every ranked hit
            # regardless of strand. Measured on TCF12 e17: `n_true_cleavage_risk` correctly fell to
            # 0 while the histogram beside it still read `{"0": 7, "1": 1}` for an oligonucleotide
            # whose eight stored hits are ALL minus-strand.
            # The graded re-score under the literature discrimination bounds is what produces this
            # paper's central negative, so a histogram counting non-liabilities put that negative on
            # hits an antisense oligonucleotide cannot bind.
            # ⚠ `is True`, not truthiness: a pre-parse hit carries no `is_minus_strand` and must
            # keep counting, so old artifacts stay the upper bounds they are honestly labelled.
            "gap_mismatch_histogram": {
                str(n): sum(1 for h in ranked
                            if h.get("gap_mismatches") == n
                            and h.get("is_minus_strand") is not True)
                for n in range(0, MAX_MISMATCHES_PER_NEAR_MATCH + 1)},
            "n_minus_strand_not_hybridisable": sum(1 for h in ranked
                                                   if h.get("is_minus_strand") is True),
            "n_gap_mismatch_unresolvable": sum(1 for h in ranked
                                               if h.get("gap_mismatches") is None
                                               and h.get("is_minus_strand") is not True),
            # ⛔ LOCUS COUNTS OVER ALL RANKED HITS, FOR THE SAME REASON AS THE HISTOGRAM ABOVE
            # (2026-08-12). A near-match count is a count of RefSeq VARIANTS, and collapsing it to
            # genes after the fact can only be done over the 15 hits saved below — which for 41 of
            # 67 already-committed oligonucleotides is a truncated sample of a list up to 50 long,
            # so those artifacts can offer a lower bound and nothing better. Computed here, before
            # the truncation, the collapse is exact and stays exact.
            **_locus_summary(ranked),
            "offtargets": ranked[:SAVED_HITS_PER_DESIGN],
        })
    except Exception as e:  # noqa: BLE001 — never crash the whole screen on one query
        rec.update({"status": "screen_failed", "error": str(e)})
    return rec


def screen_all(designs):
    """Submit every design to BLAST first, then collect — instead of one blocking wait each.

    ⛔ WHY: THIS LOOP WAS THE WHOLE COST OF THE SCREEN (measured 2026-08-12). It ran strictly
    serially — submit, poll to READY, fetch, next — so a five-design junction paid five full BLAST
    round-trips back to back and the step measured **27.6 min per junction**. Twelve junctions is
    then ~5.5 h against a 6-hour job ceiling, which is why the paper's screens had been trickling
    out a junction at a time.

    NCBI's URL API is submit-then-poll BY DESIGN: `CMD=Put` returns an RID immediately and the
    search continues server-side whether or not anyone is waiting. Submitting all five and then
    polling them turns five sequential waits into one concurrent one — the searches were always
    running in parallel on NCBI's side; only this client was serialising them.

    ⚠ NCBI'S POSTED USAGE RULES ARE KEPT, NOT BENT. Their guidance is at most one request every
    three seconds and polling no more often than once a minute per RID; submissions stay spaced by
    `SUBMIT_SPACING_S`, and the collect phase polls each RID in turn with the existing 20-second
    sleep inside `blast_poll`, so the request rate against any single search is unchanged. This is
    a change to WHEN we wait, not to how hard we hit the service.

    ⛔ A FAILED SUBMISSION MUST NOT TAKE THE OTHERS DOWN. Each design carries its own RID or its own
    error, exactly as before — the four transport failures already on record are per-oligo, and
    batching must not turn one of them into a lost junction.
    """
    rids = {}
    for i, d in enumerate(designs):
        seq = d["target_mRNA_5to3"]
        try:
            rids[seq] = blast_put(seq)
            print(f"  submitted {i+1}/{len(designs)}: {seq} -> {rids[seq]}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 — recorded per design by screen_one below
            rids[seq] = None
            print(f"  submit failed {i+1}/{len(designs)}: {seq}: {e}", file=sys.stderr)
        time.sleep(SUBMIT_SPACING_S)

    out = []
    for i, d in enumerate(designs):
        seq = d["target_mRNA_5to3"]
        print(f"  collecting {i+1}/{len(designs)}: {seq}", file=sys.stderr)
        out.append(screen_one(d, rid=rids.get(seq)))
    return out


def method_block(prov):
    """The `method` block every screen artifact carries — what a reader needs to know what ran.

    ⭐ A FUNCTION RATHER THAN A DICT LITERAL INSIDE `main()`, so it can be exercised without a
    network. `main()` cannot run in this sandbox and cannot run in a test at all — it BLASTs — so
    while the block was built inline, nothing could assert its contents and no guard on it could
    exist. The thing under test is now the thing `main()` calls, with no mock in between.
    """
    return {
        "db": "refseq_rna (txid9606[ORGN])", "program": "blastn (short, FILTER off)",
        "near_match_threshold": f">= {NEAR_MATCH_MIN_IDENT}/{ja.OLIGO_LEN} identical",
        "gap_region_1based": list(GAP_REGION_1BASED),
        "breakpoint_model": prov["note"],
        # The knobs this run used. `near_match_threshold` and `gap_region_1based` above are DERIVED
        # from two of them, so before this block a reader could recover the geometry from the
        # artifact but had no way at all to recover the search depth or the retention depth.
        "parameters": screen_parameters(),
        # Which transcripts a hit was NOT counted against, and which matching arms were live.
        # Recorded rather than assumed: for a non-EWSR1 donor the accession arm is inert (no
        # verified RefSeq accession is held here), so a reader must be able to see that the
        # parent exclusion rested on name matching alone.
        "parent_set": {
            "donor_gene": _DONOR,
            "names_excluded": list(PARENT_GENES),
            "accessions_excluded": sorted(PARENT_ACCS),
            "accession_arm_live_for_donor": _DONOR == "EWSR1",
        },
    }


def main():
    ews, nr4, left, right, fusion = ja.build_parents_and_fusion()
    label, prov = ja.junction_label()
    designs = [o for o in ja.design(left, right, fusion) if o["fusion_specific"]][:N_OLIGOS]

    screened = screen_all(designs)

    n_ok = sum(1 for r in screened if r["status"] == "screened")
    n_clean = sum(1 for r in screened
                  if r.get("status") == "screened" and r.get("n_true_cleavage_risk", 1) == 0)
    result = {
        "junction_label": label,
        # ⛔ IN REAL MODE, `ja.EWSR1_KEEP_AA` / `ja.NR4A3_KEEP_AA_FROM` ARE NOT WHAT WAS BUILT.
        # They are the codon-space MODELLED-reference constants (264 / from-2) and they are ignored by the
        # real-mode builder — yet the regenerated e12n3/e7n3 panels emitted `NR4A3_from_aa: 2` beside a
        # measured resume residue of 1, i.e. the artifact contradicted itself in adjacent keys and the
        # stale number was the more quotable one (measured 2026-08-06 on the corrected regeneration run).
        # In real mode carry the MEASURED grading; keep the constants only where they are what ran.
        "breakpoint": {**prov,
                       **({"measured_junction": {k: v for k, v in ja.LAST_JUNCTION.items()
                                                 if not k.startswith("_")}}
                          if ja.LAST_JUNCTION else
                          {"EWSR1_keep_aa": ja.EWSR1_KEEP_AA,
                           "NR4A3_from_aa": ja.NR4A3_KEEP_AA_FROM}),
                       "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
                       "_transcript_source": ja.transcript_source_provenance()},
        "_note": ("Transcriptome-wide off-target screen of the fusion-junction gapmer ASOs "
                  "(blastn-short vs human RefSeq RNA, NCBI BLAST URL API), resolved to the "
                  "gap-mismatch level. A TRUE cleavage risk = an off-target near-match whose "
                  "central DNA gap is fully matched (RNase-H can cleave); a gap-disrupted hit "
                  "(mismatch inside the gap) does NOT cleave; wing-only hits are weak affinity "
                  "liabilities. A clean oligo has zero true_cleavage_risk off-targets. Predicted "
                  "specificity, not validated; confirm by the parental-/off-target-sparing assays."),
        "method": method_block(prov),
        "n_oligos_screened": len(screened),
        "n_screened_ok": n_ok,
        "n_oligos_no_true_cleavage_risk": n_clean,
        "oligos": screened,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "oligos"}, indent=2))


if __name__ == "__main__":
    # `--rescore <screen.json> ...` re-grades committed screens offline ($0, no BLAST); bare
    # invocation runs the network screen as before.
    if "--rescore" in sys.argv:
        i = sys.argv.index("--rescore")
        sys.exit(rescore(sys.argv[i + 1:]))
    main()
