#!/usr/bin/env python3
"""Is there EMC-bearing public molecular data that a DEPOSITOR-PROSE search cannot see?

⭐ WHY THIS EXISTS, AND WHY IT IS NOT A RE-RUN OF `emc_cohort_search.py`.

That module asked GEO for a fourth EMC expression cohort and returned a bounded negative. Its own
header states the bound, and the bound is the opening this module walks through, verbatim:

    "GEO's `esearch` matches depositor prose. A series whose title and summary never say
    'extraskeletal myxoid chondrosarcoma' is invisible to every query below however many EMC
    samples it contains, and EMC samples sitting inside a pan-sarcoma deposit under a generic
    title are exactly the case that would be missed."

⛔ THAT CASE IS NOT HYPOTHETICAL AND THIS REPOSITORY HAS ALREADY BEEN BITTEN BY IT. The docstring of
`atr_hrd_sarcoma_series.py` records that **GSE24369 is titled "low-grade fibromyxoid sarcoma" and
silently contains six EMC tumours** — a third of the EMC samples the transcriptional-output
manuscript reads, sitting in a deposit whose title names a different disease. Every EMC count this
repository holds came from a prose search that could only have found that series by accident.

So the question here is the complement of the cohort search's, and no query in this repository has
ever asked it: **what carries EMC that a prose search structurally cannot reach?** Two arms, chosen
because each searches something other than what a depositor wrote:

  ARM 1 · SNAPTRON / recount3 — search the DATA, not the description.
      Snaptron indexes exon-exon junctions from uniformly reprocessed public RNA-seq (the `srav3h`
      compilation is drawn from the SRA arm of recount3). A junction is a property of the reads. A
      sample whose depositor never typed "EMC" still contributes its junctions, so a query over the
      junction index is blind to the prose and therefore reaches exactly the population the cohort
      search could not. This module does NOT claim a fusion is detectable this way — that is the
      thing it is measuring, and §PROBE below says what would have to be true.

  ARM 2 · A PAN-SARCOMA METHYLATION DEPOSIT — a named deposit in the blind spot.
      GSE140686 is the reference set of Koelsche et al., Nat Commun 2021;12:498, "Sarcoma
      classification by DNA methylation profiling". Its title names no disease, and extraskeletal
      myxoid chondrosarcoma is one of the tumour methylation classes the classifier was trained on.
      It is therefore the textbook instance of the missed case: a pan-sarcoma deposit under a
      generic title. This repository holds ZERO methylation data of any kind for this disease.

⛔ WHAT THIS MODULE MAY AND MAY NOT CONCLUDE.

  * It reports what each endpoint SERVED and what the served record CONTAINS. It grades nothing
    biological. No expression, methylation, fusion, efficacy, selectivity, safety, therapeutic-window
    or clinical-readiness claim is made or implied, and none is derivable from this artifact.
  * A sample counted here is a METADATA MATCH, never a diagnosis. `n_samples_naming_emc` counts
    records whose own text names the disease; it is a claim by the depositor exactly as a series
    title is, and it is reported as such.
  * ⛔ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). Every fetch records its HTTP
    outcome. An arm whose endpoint did not answer is `UNREACHABLE`, never `NOTHING_THERE`, and
    `derive()` refuses to emit a verdict for an arm whose inputs did not arrive.
  * ⛔ AND A ZERO IS NOT A RESULT UNTIL THE TRANSPORT IS PROVEN. Each arm carries a KNOWN-ANSWER
    TRANSPORT CONTROL that must return records, and an ABSENT CONTROL that must return none. If the
    known control comes back empty the arm is `TRANSPORT_FAILED` and its zero is withheld, because a
    null from an instrument that recovers no known positive is a broken search, not a negative.

★ PROBE FIRST, INSTRUMENT SECOND — deliberately, and this is the whole scope of the first run.
  Arm 1's design question is not answerable from documentation and must not be answered from
  recollection: does this junction index carry the junction classes a fusion transcript would
  produce, and in what fields. A chimeric junction joining two chromosomes and an intragenic
  junction inside NR4A3 are different objects, and only one of them is certain to be in a splice
  index at all. So this run MEASURES the served columns, the record counts and the coordinate span,
  and emits `arm_state: PROBED_NOT_SEARCHED` for arm 1. The searchable design is written against
  that measurement, never ahead of it.

REPRODUCTION
    python3 emc_data_level_sweep.py --selftest   # offline arithmetic + guard assertions, no network
    python3 emc_data_level_sweep.py --fetch      # CI only (the dev sandbox egress proxy 403s both hosts)
    python3 emc_data_level_sweep.py              # re-derive the verdict from the cached inputs, offline
    python3 emc_data_level_sweep.py --check      # re-derive and diff against the committed artifact
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-data-level-sweep.json")
INPUTS = os.path.join(HERE, "emc-data-level-sweep-inputs.json")

UA = "rare-cancers-emc-data-level-sweep/1.0 (research; contact via repository)"

# ── ARM 1 · Snaptron ────────────────────────────────────────────────────────────────────────────
# Compilations are TRIED, never assumed. A name that 404s is recorded as such; this repository does
# not get to decide what the service hosts.
SNAPTRON_HOST = "https://snaptron.cs.jhu.edu"
SNAPTRON_COMPILATIONS = ["srav3h", "gtexv2", "tcgav2"]

# The gene the disease is defined by, and — as CONTEXT, not as controls — its two commonest 5'
# partners plus the third partner that is NOT a FET protein. Partner frequencies are the Mod Pathol
# 2023 (PMID 36948401) distribution the roadmap already carries; they are not restated as numbers
# here (CLAUDE.md §1). ⚠ The three partners are the 5' HALF of the chimera, so the fusion gives them
# no 5'-depletion signature at all; they are read to show what an ordinary gene's rate looks like at
# each grid cell, never as a control that gates anything.
SNAPTRON_TARGETS = ["NR4A3"]
SNAPTRON_CONTEXT = ["EWSR1", "TAF15", "TCF12"]

# ⛔ THE TWO TRANSPORT CONTROLS. Neither is optional and neither is decoration.
#   transport — a ubiquitously expressed gene with a dense, well-known junction structure. If this
#               returns nothing the endpoint is not answering and every zero below is meaningless.
#   absent    — a symbol that is not an HGNC gene. If this returns records the service is matching
#               something other than what we asked for, and the target reads cannot be trusted.
SNAPTRON_TRANSPORT_CONTROL = "GAPDH"
SNAPTRON_ABSENT_CONTROL = "ZZZNOTAGENE9"

# ⛔ THE SEARCH CONTROLS, AND WITHOUT THEM THE SEARCH MAY NOT REPORT.
# The signature this instrument looks for is 5' DEPLETION: in a sample where a gene's 3' half is
# transcribed from a partner's promoter, the gene's own 5'-most junctions carry ~no coverage while
# its downstream junctions carry plenty. That is a property of the ARCHITECTURE, not of EMC, so it
# is testable on diseases whose samples are certainly in this compilation.
#
# ⭐ TWO POSITIVES, NOT ONE, added after run 32672524143. A single positive control tells you the
# score CAN fire; it cannot tell you whether the rate it fires at is typical of the signature or a
# peculiarity of that one locus. Both of these are 3' partners — the half driven from a foreign
# promoter — which is the same architecture NR4A3 has in this disease:
#   FLI1 — in Ewing sarcoma the FLI1 3' half is driven from the EWSR1 promoter.
#   ERG  — the 3' partner of the commonest prostate-cancer rearrangement, and public prostate
#          RNA-seq is abundant. It is also a 3' partner in a minority of Ewing tumours; both
#          roles point the same way, so neither confounds the other.
# ⚠ THE ARM REQUIRES AT LEAST ONE OF THEM TO FIRE, NOT BOTH. A positive control that comes back
# silent is a measurement about that locus, and it is reported; it does not get to veto a search
# the other one demonstrably detects.
SNAPTRON_SIGNATURE_POSITIVES = ["FLI1", "ERG"]
# Retained under its old name so the cross-run comparison has one fixed anchor: this is the gene
# whose rate the first search run reported as the negative control (CLAUDE.md §1 — one fact, one
# place; the number itself lives in the artifact, not here).
SNAPTRON_SIGNATURE_NEGATIVE = "GAPDH"

# ⛔ A NEGATIVE PANEL, NOT A NEGATIVE CONTROL — THIS IS THE SINGLE BIGGEST CHANGE OF THIS REVISION.
# The first search run compared the target against GAPDH alone and got ~1.9x, which is not a
# candidate list. One negative gene gives you one number and no idea of its spread: the context
# genes in that same run ranged over a factor of five between them, so "above GAPDH" and "above
# what an ordinary gene does" are different claims and only the second one is worth anything.
# This panel spans a wide range of expression depth on purpose, because depth is the confound the
# score is most likely to be tracking, and the envelope it defines is the MAXIMUM over the panel —
# the target has to clear the hottest ordinary gene, not the average one.
# ⚠ ITS ONE ASSUMPTION, STATED: that none of these is a recurrent 3' fusion partner driven from a
# foreign promoter in some tumour type. That is a design assumption, not a cited fact. Note which
# way it can be wrong: a panel gene that IS such a partner fires MORE, raises the envelope, and
# makes the target harder to call specific. The error is therefore conservative by construction.
SNAPTRON_SIGNATURE_NEGATIVE_PANEL = ["GAPDH", "ACTB", "RPL13A", "PGK1", "POLR2A", "SDHA", "TBP"]

# The 5' fraction of the gene's annotated junctions treated as the "5' end" for the ratio.
FIVE_PRIME_FRACTION = 0.34

# ── THE SPECIFICITY GRID ─────────────────────────────────────────────────────────────────────────
# ⭐ WHY A GRID AND NOT A THRESHOLD, AND WHY IT IS SWEPT INSIDE THE FETCH.
# The first search run fixed one operating point a priori and reported one number per gene. When
# that number turned out not to separate, there was no way to ask "what would a tighter one have
# done" without another fetch — and a rate is only interpretable against the negative rate ON THE
# SAME DAY'S DATA, so a second fetch cannot answer it either. The fix is structural: every cell of
# the grid is scored for every gene inside ONE fetch, from ONE parse, and the whole surface is
# cached. Every tightening is therefore re-scored on the positives, the negative panel and the
# target together by construction, not by remembering to.
#
# The four axes are the three levers §5.2 of `new-evidence-routes.md` names, plus the track below.
GRID_MIN_DOWNSTREAM_COVERAGE = [20, 100, 500, 2000]
# ⭐ LEVER 1, and the one most likely to be doing real work. A 5' junction that is ITSELF rare
# across the compilation carries no information when it is absent: "this sample does not use that
# first exon" and "this sample's 5' end was replaced" are indistinguishable. Requiring the 5'
# junctions used in the ratio to be carried by at least this fraction of the gene's own expressing
# samples separates a real absence from a sparsely annotated 5' end.
GRID_FIVE_PRIME_MIN_SUPPORT = [0.0, 0.10, 0.50, 0.90]
GRID_MAX_FIVE_PRIME_SHARE = [0.02, 0.005, 0.0]
# ⭐ LEVER 3 — the independent discriminator. In this disease NR4A3's 3' half is driven from a
# partner promoter, so the transcript should be ABUNDANT, not merely present. Expressed as a
# WITHIN-GENE percentile of downstream coverage rather than an absolute floor, because GAPDH's
# median and NR4A3's median are orders of magnitude apart and an absolute floor would compare the
# top of one distribution with the middle of another.
GRID_MIN_EXPRESSION_PERCENTILE = [0.0, 0.50, 0.90, 0.99]
# ⭐ LEVER 4 — the track, added here and not named in §5.2. A sample whose libraries are 3'-biased
# looks 5'-depleted at EVERY gene at once, so being a candidate at an ordinary gene is evidence
# that a hit is technical. The `promiscuity_filtered` track removes, from every gene's candidate
# list at every cell, the samples that are also candidates at a NEGATIVE-PANEL gene in the same
# cell. ⛔ Leave-one-out for the panel genes themselves: a panel gene is never filtered against its
# own candidate set, which would zero it by construction and manufacture a separation.
GRID_TRACKS = ["raw", "promiscuity_filtered"]

# ⚠ THE GRID IS DELIBERATELY WIDER THAN THE REGIME WE EXPECT TO NEED, and the reason is that the
# expensive resource here is not CPU — it is a CI ROUND TRIP, because the controls and the target
# have to be scored on the same day's compilation and a cell nobody swept cannot be recovered
# without re-fetching everything. Scoring a cell costs a scan over an in-memory list; not having
# scored it costs the run. The harshest corner (a 5' junction used by nine samples in ten, exactly
# zero coverage on it, the top percentile of expression) is almost certainly too tight to keep the
# positive controls alive — and finding out WHERE it dies is the shape of the limit, which is the
# publishable part if the target never separates.

# The cell that reproduces the first search run's operating point exactly, so the two runs are
# comparable and a change in the underlying compilation shows up as a moved number rather than as
# an unexplained one.
REFERENCE_CELL = (20, 0.0, 0.02, 0.0)

# ⛔ A 5' SET THAT SHRINKS TO NOTHING SILENTLY CALLS EVERY SAMPLE DEPLETED. If the support filter
# leaves fewer than this many 5' junctions the gene is UNSCOREABLE at that cell and says so; it
# never reports zero candidates, which would read as "clean" when it means "not measured".
MIN_FIVE_PRIME_JUNCTIONS_REQUIRED = 2
# A junction carrying at least this much coverage in a sample counts as "covered" for the
# breakpoint-rank statistic below. Absolute, so it needs no second pass over the gene.
BREAKPOINT_MIN_COVERAGE = 5

# ── THE PRE-REGISTERED READ-OUT ──────────────────────────────────────────────────────────────────
# ⛔⛔ THE OPERATING POINT IS CHOSEN ON THE CONTROLS ALONE, AND THE TARGET IS READ AT IT AFTERWARDS.
# Sweeping a grid and then picking the cell where the target looks best is how a null becomes a
# finding. The selection rule below reads ONLY the positive controls and the negative panel; the
# target's numbers are not an input to it, and `selftest` asserts that mutating the target's counts
# to anything at all leaves the selected cell unchanged.
#
# ⭐ WHY THE RULE IS "DRIVE THE BACKGROUND TO A CEILING, THEN KEEP THE POSITIVE" AND NOT "MAXIMISE
# A RATIO". Extraskeletal myxoid chondrosarcoma is vanishingly rare, and public RNA-seq is
# overwhelmingly not sarcoma; whatever the true number of EMC samples in this compilation is, it is
# a number of samples, not a percentage of them. So a background that calls even one sample in two
# hundred swamps the signal no matter how favourable the ratio looks. A regime in which the
# negative panel is at or near zero while a real 5'-truncated population is still recovered is the
# ONLY regime in which a target hit list means anything, and if the grid contains no such cell that
# is itself the finding.
NEG_PANEL_RATE_CEILING = 0.005
MIN_POSITIVE_CONTROL_CANDIDATES = 30
# An envelope taken over one or two surviving genes is not an envelope. If fewer than this many
# panel genes are scoreable at a cell, the cell cannot be an operating point.
MIN_NEG_PANEL_GENES_SCOREABLE = 4
# The 95% lower bound on the target's enrichment over the negative-panel envelope must exceed this
# for the target to be called separated. Pre-registered here, before the fetch, and deliberately
# well above 1: with tens of thousands of samples in the denominator a lower bound above 1 is
# reachable on an effect far too small to be a candidate list.
TARGET_MIN_ENRICHMENT = 3.0
# ⛔⛔ A ZERO IN A POOL OF TWO HUNDRED EXCLUDES NOTHING, AND THE FIRST GRID RUN LANDED EXACTLY THERE.
# The control-selected regime is tight by construction, and tight thresholds shrink the TARGET's pool
# as well as the background: run 32676239799 chose a cell where NR4A3 held 219 samples and an
# envelope of 0.0011, so even a real threefold enrichment would have been expected to produce 0.73
# candidates. It produced none — and that zero is an absent reading, not a reading of absence
# (CLAUDE.md §4). A cell may only return a verdict on the target if, WERE the target enriched by the
# pre-registered factor, at least this many candidates would be expected. Below it the read says
# UNDERPOWERED and says what pool it would have needed.
# ⚠ This criterion was added AFTER seeing that the first grid run's operating point was underpowered.
# It reads only the target's POOL SIZE and the envelope rate — never whether the target fired — so it
# cannot select a cell for looking good, and `selftest` asserts the operating point is unmoved by it.
MIN_EXPECTED_UNDER_ALTERNATIVE = 5.0
# Above this many ids in one cell's negative union the promiscuity track stops being tracked for
# that cell and says so. A cap that silently truncated would understate every overlap.
OVERLAP_MAX_IDS = 400_000
# Reserved key under which the scorer hands back a gene's expressing-sample id set alongside the
# per-cell candidate sets. It is not a grid cell and never reaches the artifact.
EXPRESSING_KEY = "__expressing__"

# ── ARM 2 · the pan-sarcoma methylation deposit ─────────────────────────────────────────────────
GEO_SERIES = "GSE140686"
GEO_ACC_CGI = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

# ⛔⛔ THE ACCESSION BELOW IS NOT WHAT THIS MODULE ONCE SAID IT WAS, AND THE SERVED RECORD IS THE
# PROOF. It was carried here as "the EBI mirror of the same study", which is an identifier written
# from recollection — exactly what CLAUDE.md §7 forbids — and it is WRONG. The record E-MTAB-9875
# actually serves is a DIFFERENT study: "Methylation profiling (450K and EPIC array) for sarcoma
# classification", submitted from UCL by Lyskjær and Flanagan, n=986, whose own Description names
# its paper as a VALIDATION study of the DKFZ sarcoma classifier. Koelsche et al. is the classifier
# it validates, not the study it mirrors. The strings "Koelsche" and "GSE140686" appear zero times
# in the served record. So it is retained here as a SECOND, INDEPENDENT DEPOSIT — which is a better
# thing than a mirror, because two deposits are two chances — and never as a route to GSE140686's
# labels. Whether a real EBI mirror of GSE140686 exists is DISCOVERED below, not assumed.
BIOSTUDIES_KNOWN = ["E-MTAB-9875"]
BIOSTUDIES_API = "https://www.ebi.ac.uk/biostudies/api/v1/studies/"
BIOSTUDIES_SEARCH = "https://www.ebi.ac.uk/biostudies/api/v1/search"
# ⛔ The record is stored WHOLE or the truncation is reported. The previous cap silently kept the
# first 400,000 bytes of a 665,144-byte body and nothing said so, which is the shape of error that
# turns "the second half of the census was never read" into "the census contains no EMC".
MAX_BIOSTUDIES_BYTES = 24_000_000

# ⛔ ARM 2's TWO CONTROLS, and they are the same contract arm 1 carries. A search endpoint that
# answers nothing and a search endpoint that answers everything are both broken, and a zero from
# either is not a negative.
#   transport — a query that MUST return at least one hit: the accession we already hold a served
#               record for. If this returns nothing, the search endpoint is not answering.
#   absent    — a syntactically valid accession that does not exist. If this returns hits, the
#               endpoint is matching something other than what we asked for.
BIOSTUDIES_TRANSPORT_CONTROL = "E-MTAB-9875"
BIOSTUDIES_ABSENT_CONTROL = "E-MTAB-99999999"

# ── the per-case diagnosis table, which is the only thing that can label GSE140686 ──────────────
# ⚠ EVERY IDENTIFIER ON THIS LADDER IS DISCOVERED FROM THE PREVIOUS RUNG, NEVER TYPED.
#   the GEO series header declares  !Series_pubmed_id  ->  the PMID
#   elink (pubmed -> pmc)                              ->  the PMCID
#   the PMC article page / Europe PMC                  ->  the supplementary file URLs
# A guessed MOESM number that 404s and a supplement that does not exist are the same length, so
# nothing here is written from recollection (CLAUDE.md §7).
EUTILS_ELINK = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
NCBI_IDCONV = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
PMC_ARTICLE_FMT = "https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
# ⛔ THE HTML ARTICLE PAGE IS NOT A ROUTE TO THE SUPPLEMENT AND THE FIRST RUN PROVED IT. It answered
# HTTP 200 in 21,246 bytes and the body was a **Google reCAPTCHA challenge page** — `<base
# href="https://www.google.com/recaptcha/challengepage/">` — not the article. A byte-size stub test
# passes that happily, which is exactly the "a plausible-looking record is more dangerous than an
# empty one" failure: 21 KB of the wrong page reads as a healthy fetch. It is kept as a rung, but it
# is graded on CONTENT and the two endpoints below are the ones expected to answer.
INTERSTITIAL_MARKERS = [
    "recaptcha", "challengepage", "enable javascript and cookies",
    "unusual traffic", "are you a robot", "cf-browser-verification", "access denied",
]
# Europe PMC serves the article XML and its supplement listing from EBI, which has been measured on
# this study to serve real records rather than interstitials.
EPMC_REST = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
# ⚠ CANDIDATE SHAPES, TRIED AND RECORDED — NOT ASSERTED. The single shape this module used first
# returned HTTP 404, and "the endpoint 404s" and "we wrote the path wrong" are the same length. Each
# candidate's status is stored so the artifact says which one answered rather than implying the
# supplement does not exist.
EPMC_SUPPL_SHAPES = ["{pmcid}/supplementaryFiles", "PMC/{pmcid}/supplementaryFiles"]
# The NCBI Open Access service. It is a DISCOVERY endpoint: it is asked for the article's package
# and it returns the location, so no archive path is ever typed here.
NCBI_OA_FCGI = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"

# ⛔ WHY THE PUBLISHER PAGE IS STILL FETCHED, AND WHAT IT MEASURED. nature.com answered HTTP 200 in
# 3,038 bytes — a stub, not a paper — so zero supplementary links were discoverable from it. That is
# a TRANSPORT failure and it was correctly reported as one. It is kept as a rung because it is free
# and because a stub is a measurement; a bounded slice of the body is now STORED, so "we were served
# an interstitial" is provable from the artifact rather than asserted in prose.
GEO_ARTICLE_URL = "https://www.nature.com/articles/s41467-020-20603-4"
SUPPL_HOST_HINT = "static-content.springer.com"
MAX_SUPPL_FILES = 12
MAX_SUPPL_BYTES = 40_000_000
STUB_BYTES = 20_000          # a "paper" smaller than this was not a paper

# ⭐⭐ THE JOIN KEY, AND IT IS DECLARED BY BOTH SIDES RATHER THAN INFERRED BY US.
# GSE140686's sample records name no disease, but each one carries
#     !Sample_description = REFERENCE_SAMPLE 259
# and the paper's supplementary tables key their per-case rows on exactly that string. So the
# deposit and the paper share an explicit identifier, and joining them is a lookup rather than an
# alignment. ⚠ THAT DISTINCTION IS THE WHOLE VALUE OF THIS ROUTE: matching the two by ORDINAL
# POSITION would be an inference this module is not entitled to make, and it would be invisible if
# wrong -- every case would still get a plausible-looking partner. Nothing here matches on order.
CASE_ID_RE = re.compile(r"\b(REFERENCE|VALIDATION)_SAMPLE\s+(\d+)", re.I)

# Disease name and the abbreviations a per-sample characteristics field actually uses. Matched
# case-insensitively against sample text; every hit is reported with the sample it came from.
EMC_TERMS = [
    "extraskeletal myxoid chondrosarcoma",
    "extra-skeletal myxoid chondrosarcoma",
    "extraskeletal myxoid chondros",
    "myxoid chondrosarcoma",
    "NR4A3",
    "EWSR1-NR4A3",
    "EWSR1::NR4A3",
    "EWS-NOR1",
    "CHON, EXTRASKEL",
]
# ⛔ DELIBERATELY SEPARATE, NEVER SUMMED. The skeletal tumours are DIFFERENT diseases with different
# drivers, and a substring search cannot tell them apart from the extraskeletal one. `chondrosarcoma`
# is on this list bare because a pan-sarcoma bone-tumour deposit labels its skeletal cases exactly
# that way — E-MTAB-9875 carries 112 of them — and counting those as EMC would manufacture a cohort
# out of a different disease. ⚠ The buckets are EXCLUSIVE: `_bucket()` assigns a row to `emc` if any
# EMC term matches, and only otherwise considers it confusable, so "extraskeletal myxoid
# chondrosarcoma" can never be demoted by the bare `chondrosarcoma` entry below.
EMC_CONFUSABLE_TERMS = [
    "skeletal myxoid chondrosarcoma",
    "chondrosarcoma, skeletal",
    "chondrosarcoma",
    "chondroblastoma",
    "chondromyxoid fibroma",
]


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(url, timeout=120, tries=3, note=""):
    """One fetch. Returns (body_or_None, record). The record is the evidence, not a log line."""
    rec = {"url": url, "note": note, "http": None, "error": None, "bytes": 0, "elapsed_s": None}
    t0 = time.time()
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                rec["http"] = r.status
                rec["bytes"] = len(body)
                rec["elapsed_s"] = round(time.time() - t0, 2)
                return body.decode("utf-8", "replace"), rec
        except urllib.error.HTTPError as e:
            rec["http"] = e.code
            rec["error"] = f"HTTPError {e.code}"
            if e.code in (400, 404, 410):
                break          # a real answer: the resource is not there. Do not retry it.
        except Exception as e:                                     # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"
        if attempt < tries:
            time.sleep(2 * attempt)
    rec["elapsed_s"] = round(time.time() - t0, 2)
    return None, rec


def _get_bytes(url, timeout=300, tries=3, note=""):
    """One fetch, RAW. Identical contract to `_get`, but the body is never decoded.

    ⛔ A SUPPLEMENT IS A BINARY UNTIL PROVEN OTHERWISE. Decoding a .xlsx or a .zip as UTF-8 and
    re-encoding it corrupts it, and a corrupted archive raises inside the parser — which this module
    would then record as `readable: false`, i.e. as a fact about the FILE rather than about our own
    handling of it. Bytes in, bytes out.
    """
    rec = {"url": url, "note": note, "http": None, "error": None, "bytes": 0, "elapsed_s": None}
    t0 = time.time()
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                rec["http"] = r.status
                rec["bytes"] = len(body)
                rec["elapsed_s"] = round(time.time() - t0, 2)
                return body, rec
        except urllib.error.HTTPError as e:
            rec["http"] = e.code
            rec["error"] = f"HTTPError {e.code}"
            if e.code in (400, 404, 410):
                break
        except Exception as e:                                     # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"
        if attempt < tries:
            time.sleep(2 * attempt)
    rec["elapsed_s"] = round(time.time() - t0, 2)
    return None, rec


# ────────────────────────────────────────────────────────────────────────────────────────────────
# ARM 1 — the junction index
# ────────────────────────────────────────────────────────────────────────────────────────────────

def _snaptron_url(compilation, region):
    return f"{SNAPTRON_HOST}/{compilation}/snaptron?regions={urllib.parse.quote(region)}"


def parse_snaptron(body):
    """Parse a Snaptron TSV stream into a SHAPE description. No biology, only structure.

    Snaptron returns a TAB-delimited stream whose first line is a header. We do not assume any
    column name: the header we were SERVED is recorded verbatim and every derived field says which
    served column it came from, so a service-side rename shows up as a missing column rather than as
    a silently wrong number.
    """
    lines = [ln for ln in body.split("\n") if ln.strip()]
    if not lines:
        return {"n_lines": 0, "header": None, "columns": [], "n_records": 0,
                "records_sample": [], "chromosomes": {}, "note": "empty body"}
    header = lines[0]
    cols = header.lstrip("#").split("\t")
    recs = [ln.split("\t") for ln in lines[1:]]
    idx = {c: i for i, c in enumerate(cols)}

    def col(r, name):
        i = idx.get(name)
        if i is None or i >= len(r):
            return None
        return r[i]

    chrom_counts = {}
    for r in recs:
        c = col(r, "chromosome")
        if c is not None:
            chrom_counts[c] = chrom_counts.get(c, 0) + 1

    n_annot = sum(1 for r in recs if col(r, "annotated") == "1")
    return {
        "n_lines": len(lines),
        "header": header[:2000],
        "columns": cols,
        "n_records": len(recs),
        "n_annotated": n_annot,
        # A bounded verbatim sample. Enough to see the shape, never enough to be a dataset.
        "records_sample": ["\t".join(r)[:600] for r in recs[:5]],
        "chromosomes": chrom_counts,
        "has_chromosome_column": "chromosome" in idx,
        "has_samples_count_column": "samples_count" in idx,
        "has_annotated_column": "annotated" in idx,
    }


def cell_key(min_cov, support, max_share, pct):
    """One stable, sortable name for a grid cell. Formatting is fixed so a key written by the
    fetch and a key rebuilt by `derive` can never disagree on trailing zeros."""
    return f"mc{int(min_cov)}|sup{float(support):.2f}|sh{float(max_share):.4f}|pct{float(pct):.2f}"


def grid_cells():
    """The cartesian grid, in one deterministic order, so two runs list cells identically."""
    for mc in GRID_MIN_DOWNSTREAM_COVERAGE:
        for sup in GRID_FIVE_PRIME_MIN_SUPPORT:
            for sh in GRID_MAX_FIVE_PRIME_SHARE:
                for pct in GRID_MIN_EXPRESSION_PERCENTILE:
                    yield (mc, sup, sh, pct)


def five_prime_depletion(body):
    """Per-sample 5'-depletion profile over ONE gene's annotated junctions, swept over the GRID.

    ⛔ WHAT THIS MEASURES, STATED BEFORE THE ARITHMETIC. A junction record carries the samples it
    was seen in and the coverage in each. So for one gene we can rebuild, per sample, how its
    junction coverage is distributed along the gene. A sample whose coverage sits entirely on the
    DOWNSTREAM junctions and not at all on the 5'-most ones is a sample in which that gene's 3' half
    is being transcribed while its own 5' end is not.

    ⛔ WHAT IT IS NOT. That pattern is CONSISTENT WITH a 5'-truncating rearrangement; it does not
    identify one, does not name a partner, and is not a diagnosis. An alternative promoter, 3' bias
    in a degraded library, or a poorly-annotated 5' end all produce it too. The output is a
    CANDIDATE LIST for orthogonal checking, and it is labelled that way in the artifact.

    ⚠ STRAND IS DERIVED, NEVER ASSUMED. "5'-most" is the lowest coordinate on the plus strand and
    the highest on the minus strand, and getting it backwards silently inverts the whole result. The
    strand is taken as the majority strand of the gene's ANNOTATED junctions and is reported.

    Returns `(summary, candidate_ids)`. `summary` is JSON-serialisable and is what gets cached;
    `candidate_ids` maps a cell key to the SET of rail ids called at it and is held only in memory,
    because the cross-gene overlap that feeds the promiscuity track needs the ids and the artifact
    does not.
    """
    lines = [ln for ln in body.split("\n") if ln.strip()]
    if len(lines) < 2:
        return {"usable": False, "why": "no records"}, {}
    cols = lines[0].lstrip("#").split("\t")
    idx = {c: i for i, c in enumerate(cols)}
    need = ("chromosome", "start", "end", "strand", "annotated", "samples")
    missing = [c for c in need if c not in idx]
    if missing:
        return {"usable": False, "why": f"served columns lack {missing}"}, {}

    annotated = []
    for ln in lines[1:]:
        r = ln.split("\t")
        if len(r) <= max(idx.values()):
            continue
        if r[idx["annotated"]] != "1":
            continue
        annotated.append(r)
    if len(annotated) < 6:
        return ({"usable": False,
                 "why": f"only {len(annotated)} annotated junctions; too few to split"}, {})

    strands = {}
    for r in annotated:
        s = r[idx["strand"]]
        strands[s] = strands.get(s, 0) + 1
    strand = max(strands, key=strands.get)
    annotated = [r for r in annotated if r[idx["strand"]] == strand]

    # Order along the transcript: ascending coordinate on +, descending on -.
    annotated.sort(key=lambda r: int(r[idx["start"]]), reverse=(strand == "-"))
    n_j = len(annotated)
    k = max(1, int(n_j * FIVE_PRIME_FRACTION))
    si = idx["samples"]

    def tokens(row):
        for tok in row[si].split(","):
            if not tok or ":" not in tok:
                continue
            sid, _, cov = tok.partition(":")
            try:
                yield sid, float(cov)
            except ValueError:
                continue

    # ── PASS 1 · downstream coverage, 5'-junction support counts, breakpoint rank ────────────────
    # One walk in transcript order. `breakpoint_rank` is the 5'-most annotated junction at which the
    # sample carries non-trivial coverage — where, in this sample, the transcript effectively
    # starts. It needs no per-sample maximum, hence no extra pass.
    cov3, bp_rank = {}, {}
    for rank, row in enumerate(annotated):
        downstream = rank >= k
        for sid, cov in tokens(row):
            if downstream:
                cov3[sid] = cov3.get(sid, 0.0) + cov
            if cov >= BREAKPOINT_MIN_COVERAGE and rank < bp_rank.get(sid, n_j):
                bp_rank[sid] = rank

    base_floor = min(GRID_MIN_DOWNSTREAM_COVERAGE)
    expressing_base = {s for s, d in cov3.items() if d >= base_floor}
    n_base = len(expressing_base)
    if not n_base:
        return ({"usable": False,
                 "why": f"no sample carries {base_floor}+ downstream coverage"}, {})

    # ── PASS 2 · 5'-junction SUPPORT, then 5' coverage per distinct support level ────────────────
    # ⚠ Support is counted over the gene's OWN EXPRESSING SAMPLES, which is the only denominator
    # that makes the fraction mean "how often, when this gene is on, is this junction used". Using
    # every sample in the compilation would let a fraction exceed 1 and would quietly rescale the
    # lever. The 5' region is a handful of rows, so walking it twice costs nothing.
    five_support = [0] * k
    for rank in range(k):
        for sid, cov in tokens(annotated[rank]):
            if cov > 0 and sid in expressing_base:
                five_support[rank] += 1
    support_frac = [round(c / n_base, 5) for c in five_support]

    five_sets = {sup: [r for r in range(k) if support_frac[r] >= sup]
                 for sup in GRID_FIVE_PRIME_MIN_SUPPORT}
    cov5 = {sup: {} for sup in GRID_FIVE_PRIME_MIN_SUPPORT}
    for rank in range(k):
        active = [sup for sup in GRID_FIVE_PRIME_MIN_SUPPORT if rank in five_sets[sup]]
        if not active:
            continue
        for sid, cov in tokens(annotated[rank]):
            for sup in active:
                cov5[sup][sid] = cov5[sup].get(sid, 0.0) + cov

    # ── SCORE THE GRID ──────────────────────────────────────────────────────────────────────────
    # Both coverage thresholds reduce to a floor on downstream coverage, so sorting once turns
    # every (min_cov, percentile) pair into a prefix of one list.
    cells, ids = {}, {}
    shares_desc = sorted(GRID_MAX_FIVE_PRIME_SHARE, reverse=True)
    for sup in GRID_FIVE_PRIME_MIN_SUPPORT:
        n_five_used = len(five_sets[sup])
        prof = None
        if n_five_used >= MIN_FIVE_PRIME_JUNCTIONS_REQUIRED:
            up = cov5[sup]
            prof = [(d, (up.get(s, 0.0) / (up.get(s, 0.0) + d)), s)
                    for s, d in cov3.items() if d >= base_floor]
            prof.sort(key=lambda t: -t[0])
        for mc in GRID_MIN_DOWNSTREAM_COVERAGE:
            # `prof` is sorted by downstream coverage descending, so the expressing set at any
            # floor is a PREFIX of it and is found once per floor rather than once per cell.
            expressing = [t for t in prof if t[0] >= mc] if prof is not None else None
            for pct in GRID_MIN_EXPRESSION_PERCENTILE:
                if prof is None:
                    for sh in GRID_MAX_FIVE_PRIME_SHARE:
                        cells[cell_key(mc, sup, sh, pct)] = {
                            "scoreable": False,
                            "why": (f"the 5'-support filter leaves {n_five_used} of {k} 5' "
                                    f"junctions, below the {MIN_FIVE_PRIME_JUNCTIONS_REQUIRED} "
                                    "this ratio needs; an empty 5' set would call every sample "
                                    "depleted, so this cell is NOT MEASURED rather than zero"),
                            "n_five_prime_junctions_used": n_five_used}
                    continue
                n_expr = len(expressing)
                # ⚠ `int(n * (1 - pct))` is NOT this expression: 1 - 0.9 is 0.09999999...,
                # which silently loses one sample off every top-decile pool.
                n_pool = n_expr - int(n_expr * pct)
                pool = expressing[:n_pool]
                hit = {sh: [] for sh in GRID_MAX_FIVE_PRIME_SHARE}
                for d, share, sid in pool:
                    for sh in shares_desc:
                        if share <= sh:
                            hit[sh].append(sid)
                        else:
                            break
                for sh in GRID_MAX_FIVE_PRIME_SHARE:
                    key = cell_key(mc, sup, sh, pct)
                    got = hit[sh]
                    hist, unassigned = {}, 0
                    for sid in got:
                        r = bp_rank.get(sid)
                        if r is None:
                            unassigned += 1
                        else:
                            hist[str(r)] = hist.get(str(r), 0) + 1
                    cells[key] = {
                        "scoreable": True,
                        "n_five_prime_junctions_used": n_five_used,
                        "n_samples_expressing_downstream": n_expr,
                        "n_pool": n_pool,
                        "n_candidates": len(got),
                        "candidate_rate": round(len(got) / n_pool, 6) if n_pool else None,
                        "breakpoint_rank_hist": hist,
                        # ⚠ Reported so the histogram can never read as complete when it is not: a
                        # candidate whose every junction sits under the coverage floor has no
                        # breakpoint rank, and the concentration is over what WAS assigned.
                        "breakpoint_rank_unassigned": unassigned,
                        "breakpoint_rank_concentration": _concentration(hist),
                    }
                    ids[key] = set(got)

    ids[EXPRESSING_KEY] = expressing_base
    ref = cell_key(*REFERENCE_CELL)
    ref_cell = cells.get(ref, {})
    ref_ids = sorted(ids.get(ref, ()), key=lambda s: -cov3.get(s, 0.0))[:40]
    return {
        "usable": True,
        "strand_derived": strand,
        "strand_vote": strands,
        "n_annotated_junctions": n_j,
        "n_five_prime_region_junctions": k,
        "five_prime_support_fraction": support_frac,
        "n_samples_expressing_at_base_floor": n_base,
        "reference_cell": ref,
        "cells": cells,
        # Bounded and for eyeballing only. The reference cell is the FIRST run's operating point,
        # which is the one that did not separate — these are shown so the shape of the background
        # is visible, and they are not a candidate list (CLAUDE.md §4).
        "reference_cell_examples": [
            {"rail_id": s, "downstream_cov": round(cov3.get(s, 0.0), 1),
             "breakpoint_rank": bp_rank.get(s)} for s in ref_ids],
        "reference_cell_n_candidates": ref_cell.get("n_candidates"),
        "reference_cell_rate": ref_cell.get("candidate_rate"),
        "grid": {"min_downstream_coverage": GRID_MIN_DOWNSTREAM_COVERAGE,
                 "five_prime_min_support": GRID_FIVE_PRIME_MIN_SUPPORT,
                 "max_five_prime_share": GRID_MAX_FIVE_PRIME_SHARE,
                 "min_expression_percentile": GRID_MIN_EXPRESSION_PERCENTILE,
                 "five_prime_fraction": FIVE_PRIME_FRACTION},
    }, ids


def _concentration(hist):
    """How concentrated a breakpoint-rank histogram is: the share held by its commonest rank.

    ⭐ WHY IT IS HERE. A recurrent rearrangement joins the partner to the SAME place in the gene in
    most tumours carrying it, so its samples pile up at one rank. A 3'-biased or degraded library
    has no reason to start anywhere in particular, so its samples scatter. The statistic is
    reported for every gene at every cell — including both positive controls and the whole negative
    panel — so it is read as a contrast and never on its own.
    """
    tot = sum(hist.values())
    if not tot:
        return None
    return round(max(hist.values()) / tot, 4)


def fetch_snaptron():
    out = {"host": SNAPTRON_HOST, "compilations_tried": SNAPTRON_COMPILATIONS,
           "reachability": {}, "queries": {}, "controls": {}}

    # Reachability is asked ONCE per compilation with the transport control, so a compilation that
    # does not exist is separated from a target that has no records in one that does.
    live = []
    for comp in SNAPTRON_COMPILATIONS:
        body, rec = _get(_snaptron_url(comp, SNAPTRON_TRANSPORT_CONTROL), timeout=180,
                         note=f"transport control in {comp}")
        shape = parse_snaptron(body) if body is not None else None
        out["reachability"][comp] = {"fetch": rec,
                                     "shape": shape,
                                     "answers": bool(body is not None and shape
                                                     and shape["n_records"] > 0)}
        if out["reachability"][comp]["answers"]:
            live.append(comp)
    out["compilations_that_answered"] = live

    if not live:
        out["arm_state"] = "UNREACHABLE"
        return out

    comp = live[0]
    out["compilation_used"] = comp

    body, rec = _get(_snaptron_url(comp, SNAPTRON_ABSENT_CONTROL), timeout=120,
                     note="absent control — must return no records")
    out["controls"]["absent"] = {"fetch": rec,
                                 "shape": parse_snaptron(body) if body is not None else None}
    out["controls"]["transport"] = {"compilation": comp,
                                    "shape": out["reachability"][comp]["shape"]}

    def fetch_one(gene):
        return _get(_snaptron_url(comp, gene), timeout=600, note=f"gene {gene}")

    return score_snaptron_bodies(out, fetch_one)


def score_snaptron_bodies(out, fetch_one, pause=1.0):
    """Score every gene of the panel over the whole grid and fill `out` in place.

    ⛔ EVERY GENE IS SCORED IN THE SAME RUN, FROM THE SAME PARSE, OVER THE SAME GRID. A candidate
    rate means nothing except against the negative panel's rate on the same day's compilation, so
    the controls and the target are never in different runs and never on different code paths.

    ⭐ IT IS A SEPARATE FUNCTION FROM `fetch_snaptron` FOR ONE REASON: so `selftest` can drive the
    whole chain — scorer, promiscuity track, `derive` — over synthetic bodies with no network. A
    structural mismatch between what the fetch writes and what `derive` reads is exactly the class
    of bug that would otherwise be discovered only after a CI run had spent its time.

    `fetch_one(gene)` returns `(body_or_None, fetch_record)`. It is called ONCE per gene and its
    body is released as soon as the gene is scored, because these bodies are tens of megabytes
    each and holding thirteen of them at once is a CI runner's memory spent on nothing.
    """
    # ⚠ THE ORDER IS LOAD-BEARING: the negative panel is scored FIRST because the promiscuity track
    # needs the union of its candidate ids before any other gene can be filtered against it.
    negatives = list(dict.fromkeys(SNAPTRON_SIGNATURE_NEGATIVE_PANEL))
    others = [g for g in dict.fromkeys(
        SNAPTRON_SIGNATURE_POSITIVES + SNAPTRON_TARGETS + SNAPTRON_CONTEXT) if g not in negatives]
    out.setdefault("queries", {})
    out["search_genes"] = negatives + others
    out["signature_positives"] = SNAPTRON_SIGNATURE_POSITIVES
    out["signature_negative_panel"] = negatives
    out["signature_negative"] = SNAPTRON_SIGNATURE_NEGATIVE
    out["targets"] = SNAPTRON_TARGETS
    out["context_genes"] = SNAPTRON_CONTEXT
    out["grid_tracks"] = GRID_TRACKS
    out["thresholds"] = {
        "neg_panel_rate_ceiling": NEG_PANEL_RATE_CEILING,
        "min_positive_control_candidates": MIN_POSITIVE_CONTROL_CANDIDATES,
        "min_neg_panel_genes_scoreable": MIN_NEG_PANEL_GENES_SCOREABLE,
        "target_min_enrichment": TARGET_MIN_ENRICHMENT,
        "min_expected_under_alternative": MIN_EXPECTED_UNDER_ALTERNATIVE,
        "min_five_prime_junctions_required": MIN_FIVE_PRIME_JUNCTIONS_REQUIRED,
        "breakpoint_min_coverage": BREAKPOINT_MIN_COVERAGE,
        "reference_cell": cell_key(*REFERENCE_CELL),
    }

    # ⚠ Only TWO expressing-sample sets are kept, and the rest are dropped the moment the gene is
    # scored: thirteen sets of a quarter-million ids each, held to the end of the run, is a few
    # hundred megabytes of a CI runner spent on nothing.
    keep_expressing = {SNAPTRON_TRANSPORT_CONTROL} | set(SNAPTRON_TARGETS)
    expressing = {}

    def one(gene):
        body, rec = fetch_one(gene)
        shape = parse_snaptron(body) if body is not None else None
        dep, ids = (five_prime_depletion(body) if body is not None
                    else ({"usable": False, "why": "no body"}, {}))
        # The scorer hands back the gene's expressing-sample id set under a reserved key. It is not
        # a grid cell and must reach neither the promiscuity arithmetic nor the artifact.
        expr = ids.pop(EXPRESSING_KEY, set())
        if gene in keep_expressing:
            expressing[gene] = expr
        out["queries"][gene] = {"fetch": rec, "shape": shape, "depletion": dep}
        if pause:
            time.sleep(pause)
        return ids

    ids_by_gene = {g: one(g) for g in negatives + others}

    # ⛔ THE ID SPACES MUST BE THE SAME ONE, AND THIS IS MEASURED RATHER THAN ASSUMED. Every
    # cross-gene statement here — the promiscuity track most of all — is nonsense if two gene
    # queries name their samples differently. The check is the overlap between the transport
    # control's expressing samples and the TARGET's: two loci sampled across one compilation must
    # share most of the rarer one's samples, and a near-empty intersection would mean the ids are
    # not comparable and nothing cross-gene may be read.
    tc = expressing.get(SNAPTRON_TRANSPORT_CONTROL, set())
    tn = next((g for g in SNAPTRON_TARGETS if g in expressing), None)
    tg = expressing.get(tn, set()) if tn else set()
    out["id_space_check"] = {
        "transport_control": SNAPTRON_TRANSPORT_CONTROL,
        "transport_control_expressing": len(tc),
        "target": tn,
        "target_expressing": len(tg),
        "shared_with_transport_control": len(tc & tg),
        "shared_fraction_of_target": round(len(tc & tg) / len(tg), 4) if tg else None,
        "_what": ("a floor-level check that the rail ids one gene query returns are the same "
                  "identifiers another one returns. It is not a biological reading."),
    }
    expressing.clear()
    del tc, tg

    out["promiscuity_cells_not_tracked"] = apply_promiscuity_track(
        out["queries"], ids_by_gene, negatives)
    out["arm_state"] = "FETCHED"
    return out


def apply_promiscuity_track(queries, ids_by_gene, negatives, max_ids=OVERLAP_MAX_IDS):
    """LEVER 4, applied in place to every gene's cells. Pure arithmetic over candidate id sets.

    ⭐ WHAT IT REMOVES AND WHY. A 3'-biased library looks 5'-depleted at every gene at once, so a
    sample that is a candidate at an ORDINARY gene is evidence that its hit anywhere else is
    technical. This drops, from each gene's candidate list at each cell, the samples that are also
    candidates at a negative-panel gene at the SAME cell. The denominator is left alone, so the
    filtered rate is a rate over the same pool and stays comparable across genes.

    ⛔ LEAVE-ONE-OUT FOR THE PANEL ITSELF, AND IT IS NOT A DETAIL. Filtering GAPDH against a union
    that contains GAPDH's own candidates zeroes it by construction, and a negative control forced
    to zero manufactures exactly the separation this revision exists to avoid claiming. Every panel
    gene is filtered against the union of the OTHERS, and `selftest` asserts it.

    ⚠ IT IS A LEVER, NOT A TRUTH: an EMC sample really can be a degraded library, and this filter
    would drop it. That is why it is a TRACK the control-selection may or may not pick, scored
    beside the raw one, rather than a filter applied unconditionally.

    Returns the sorted cell keys where the union grew past `max_ids` and the track was therefore
    NOT tracked — recorded, because a silently truncated union understates every overlap.
    """
    def cell_of(gene, key):
        c = ((queries.get(gene) or {}).get("depletion") or {}).get("cells", {}).get(key)
        return c if (c and c.get("scoreable")) else None

    keys = sorted({k for g in negatives for k in ids_by_gene.get(g, {})})
    untracked = []
    for key in keys:
        per_gene = {g: ids_by_gene.get(g, {}).get(key, frozenset()) for g in negatives}
        if sum(len(v) for v in per_gene.values()) > max_ids:
            untracked.append(key)
            for gene in ids_by_gene:
                cell = cell_of(gene, key)
                if cell:
                    cell["promiscuity_tracked"] = False
            continue
        # ⛔ THE LEAVE-ONE-OUT IS A COUNT, NOT A SUBTRACTION. `union_of_everything - own` is NOT
        # `union of the others`: an id that two panel genes both carry survives the subtraction and
        # the gene is wrongly exempted from its own promiscuous candidates — which, since shared
        # background is the exact thing this lever hunts, is the case that matters most. Counting
        # carriers gets it right: an id is in the union of the others iff some OTHER gene carries
        # it, i.e. iff its carrier count exceeds this gene's own contribution of one.
        carriers = {}
        for own_set in per_gene.values():
            for i in own_set:
                carriers[i] = carriers.get(i, 0) + 1
        for gene, ids in ids_by_gene.items():
            cell = cell_of(gene, key)
            if cell is None:
                continue
            own = per_gene.get(gene)
            got = ids.get(key, frozenset())
            if own is None:
                kept = sum(1 for i in got if i not in carriers)
            else:
                kept = sum(1 for i in got
                           if carriers.get(i, 0) - (1 if i in own else 0) <= 0)
            cell["promiscuity_tracked"] = True
            cell["n_candidates_promiscuity_filtered"] = kept
            cell["candidate_rate_promiscuity_filtered"] = (
                round(kept / cell["n_pool"], 6) if cell.get("n_pool") else None)
    return untracked


# ────────────────────────────────────────────────────────────────────────────────────────────────
# ARM 2 — the pan-sarcoma methylation deposit
#
# ★ IT IS A LADDER OF LABEL SOURCES, AND EVERY RUNG IS RECORDED SEPARATELY. GSE140686 is fully
# readable and states no diagnoses at all: all 1,505 sample records are titled "sarcoma classifier
# reference case N" with characteristics "tissue: sarcoma", and EMC / chondrosarcoma / myxoid /
# NR4A3 appear zero times across the whole stream. That is a fact about the LABELS, not about the
# samples, so the question becomes "where else are the per-case diagnoses published", and each
# candidate answer is its own rung with its own HTTP outcome:
#
#   1 · GEO             the deposit itself                      -> measured: carries no diagnoses
#   2 · BioStudies      does a real EBI mirror exist?            -> SEARCHED, never assumed
#   3 · BioStudies      full records for every candidate accno   -> per-sample `disease` census
#   4 · PMC             PMID (from GEO) -> PMCID -> supplements  -> the published per-case table
#
# ⛔ A RUNG THAT DID NOT ANSWER IS RECORDED AS UNREAD, WITH THE REASON. None of them may render as
# "this deposit has no EMC".
# ────────────────────────────────────────────────────────────────────────────────────────────────

def _interstitial_markers(body):
    """Which bot-wall markers does this body carry? Empty list = it looks like real content.

    ⛔ GRADE A PAGE ON WHAT IS IN IT, NEVER ON HOW BIG IT IS. Measured 2026-08-24: PMC answered
    HTTP 200 in 21,246 bytes and the body was a Google reCAPTCHA challenge page. A size threshold
    calls that healthy and hands the link parser a wall, which then finds zero supplementary links
    — and "zero links found" reads exactly like "this paper has no supplement". Presence is never
    evidence of provenance (CLAUDE.md §4).
    """
    if not body:
        return []
    low = body[:20000].lower()
    return [k for k in INTERSTITIAL_MARKERS if k in low]


def _fetch_geo(out):
    """Rung 1 — the deposit itself, header then every sample record."""
    q_self = f"{GEO_ACC_CGI}?acc={GEO_SERIES}&targ=self&form=text&view=brief"
    body, rec = _get(q_self, timeout=180, note="GEO series header")
    out["fetches"]["geo_self"] = rec
    out["geo_self_text"] = body[:200000] if body else None

    q_all = f"{GEO_ACC_CGI}?acc={GEO_SERIES}&targ=all&form=text&view=brief"
    body_all, rec_all = _get(q_all, timeout=600, note="GEO series + every sample record")
    out["fetches"]["geo_all"] = rec_all
    # Bounded: 1,500 brief sample records is a few MB. The cap is recorded so a truncation can never
    # read as a short deposit.
    CAP = 12_000_000
    if body_all is not None:
        out["geo_all_truncated"] = len(body_all) > CAP
        out["geo_all_text"] = body_all[:CAP]
    else:
        out["geo_all_truncated"] = None
        out["geo_all_text"] = None

    # ⚠ DISCOVERED, NOT TYPED. The series header declares its own publication; that declaration is
    # the only reason this module knows which paper to go and read.
    out["pubmed_id"] = None
    if body:
        m = re.search(r"!Series_pubmed_id\s*=\s*(\d+)", body)
        if m:
            out["pubmed_id"] = m.group(1)
    return body is not None or body_all is not None


def _fetch_biostudies(out):
    """Rungs 2 and 3 — is there a real EBI mirror, and what do the EBI records actually label?"""
    # ── rung 2 · the controls first, then the discovery ─────────────────────────────────────────
    controls = {}
    for role, q in (("transport", BIOSTUDIES_TRANSPORT_CONTROL), ("absent", BIOSTUDIES_ABSENT_CONTROL)):
        url = f"{BIOSTUDIES_SEARCH}?query={urllib.parse.quote(q)}&pageSize=5"
        body, rec = _get(url, timeout=120, note=f"BioStudies search control ({role})")
        controls[role] = {"query": q, "fetch": rec, "n_hits": _biostudies_hit_count(body),
                          "accessions": _biostudies_hit_accessions(body)}
    out["biostudies_controls"] = controls

    searches, discovered = {}, []
    series_title = None
    head = out.get("geo_self_text") or ""
    m = re.search(r"!Series_title\s*=\s*(.+)", head)
    if m:
        series_title = m.group(1).strip()
    queries = [("geo_accession", GEO_SERIES)]
    if series_title:
        queries.append(("series_title", series_title))
    for label, q in queries:
        url = f"{BIOSTUDIES_SEARCH}?query={urllib.parse.quote(q)}&pageSize=25"
        body, rec = _get(url, timeout=120, note=f"BioStudies search ({label})")
        accs = _biostudies_hit_accessions(body)
        searches[label] = {"query": q, "fetch": rec, "n_hits": _biostudies_hit_count(body),
                           "accessions": accs}
        for a in accs:
            if a not in discovered:
                discovered.append(a)
    out["biostudies_searches"] = searches
    out["biostudies_discovered"] = discovered

    # ── rung 3 · the full record for every accession, discovered ones and the pinned one ────────
    # ⚠ PROVENANCE IS CARRIED PER ACCESSION. "we searched and found it" and "a previous session
    # typed it into this file" are different epistemic states and the artifact must not blur them.
    # ⛔ THE ORDER IS A FIX, NOT A PREFERENCE, AND THE FIRST RUN IS WHY. The search returned 36
    # accessions and this took the first ten. Thirty-one of them were Europe PMC LITERATURE records
    # — papers citing the deposit — so ten fetches were spent on abstracts, while the two records
    # that could actually carry labels sat further down the list and were never fetched at all:
    # the ArrayExpress-style `E-` data records, and `S-EPMC<n>` for THIS article, which is the
    # paper's own record. Data records first, then this paper's own, then the rest.
    own = f"S-EPMC{(out.get('pmc') or {}).get('pmcid', '')[3:]}" if (
        out.get("pmc") or {}).get("pmcid") else None
    data_first = [a for a in discovered if a.startswith("E-")]
    mine = [a for a in discovered if own and a == own]
    rest = [a for a in discovered if a not in data_first and a not in mine]
    ordered = data_first + mine + rest

    targets = []
    for a in ordered[:10]:
        targets.append((a, "discovered_by_search"))
    if own and own not in [t[0] for t in targets]:
        # Discovered from the PMID the GEO header declared -> the PMCID -> this record. Not typed.
        targets.append((own, "derived_from_the_discovered_pmcid"))
    for a in BIOSTUDIES_KNOWN:
        if a not in [t[0] for t in targets]:
            targets.append((a, "pinned_in_module_NOT_a_mirror"))

    records = {}
    for acc, prov in targets:
        body, rec = _get(BIOSTUDIES_API + acc, timeout=240, note=f"BioStudies record {acc}")
        entry = {"accession": acc, "provenance": prov, "fetch": rec,
                 "served_bytes": rec.get("bytes"), "truncated": None, "parsed": None}
        if body is not None:
            kept = body[:MAX_BIOSTUDIES_BYTES]
            # ⛔ Truncation is a MEASUREMENT, not a silence. `bytes` is what the server sent.
            entry["truncated"] = len(kept) < len(body)
            entry["text"] = kept
            entry["parsed"] = _parse_biostudies(acc, kept, entry["truncated"])
        records[acc] = entry
        time.sleep(1)
    out["biostudies_records"] = records


def _biostudies_hit_count(body):
    if not body:
        return None
    try:
        d = json.loads(body)
    except Exception:                                                  # noqa: BLE001
        return None
    for k in ("totalHits", "hits_total", "total"):
        if isinstance(d.get(k), int):
            return d[k]
    hits = d.get("hits")
    return len(hits) if isinstance(hits, list) else None


def _biostudies_hit_accessions(body):
    if not body:
        return []
    try:
        d = json.loads(body)
    except Exception:                                                  # noqa: BLE001
        return []
    out = []
    for h in (d.get("hits") or []):
        if isinstance(h, dict):
            a = h.get("accession") or h.get("accno")
            if a and a not in out:
                out.append(a)
    return out


def _walk_subsections(node):
    """Yield every subsection dict in a BioStudies section tree.

    ⚠ `subsections` is a list whose members are EITHER a subsection dict OR a nested list of them —
    that is what the served record does, and a walker that assumes only dicts silently skips whole
    branches. Measured against the served E-MTAB-9875 record, not assumed from documentation.
    """
    subs = node.get("subsections") if isinstance(node, dict) else None
    if not isinstance(subs, list):
        return
    for s in subs:
        if isinstance(s, list):
            for t in s:
                if isinstance(t, dict):
                    yield t
                    yield from _walk_subsections(t)
        elif isinstance(s, dict):
            yield s
            yield from _walk_subsections(s)


def _attrs(node):
    """{name: [values]} for one subsection's attributes, preserving repeats."""
    out = {}
    for a in (node.get("attributes") or []):
        if isinstance(a, dict) and a.get("name") is not None:
            out.setdefault(str(a["name"]), []).append(a.get("value"))
    return out


def _parse_biostudies(acc, body, truncated):
    """What does ONE EBI record actually say, and is its own census complete?

    ⛔ THE COMPLETENESS TEST IS THE WHOLE POINT, AND IT IS WHAT MAKES A ZERO ADMISSIBLE. A record's
    per-disease `Factors Table` rows each carry a `No. of Samples`. If those counts SUM TO the
    record's own declared `Sample count`, then every sample in the deposit has been accounted for by
    name and "no EMC row" is a real negative over a complete enumeration. If they do not sum, some
    of the deposit is unaccounted for and the same zero means only "not in the part we read".
    `census_complete` carries that distinction and `derive()` refuses to call it a negative without it.
    """
    res = {"accession": acc, "readable": False, "why": None, "truncated": truncated,
           "title": None, "description": None, "release_date": None, "data_source": None,
           "is_a_data_record": False,
           "declared_sample_count": None, "disease_census": {}, "census_sum": 0,
           "census_complete": False, "n_categories": 0,
           "emc_categories": {}, "confusable_categories": {},
           "n_emc_samples": 0, "n_confusable_samples": 0,
           "emc_idat_files": [], "n_emc_idat_files": 0,
           "mentions_geo_series": False, "characteristics_rows": 0}
    try:
        d = json.loads(body)
    except Exception as exc:                                           # noqa: BLE001
        res["why"] = (f"{type(exc).__name__}: {exc} — the record could not be parsed"
                      + (" (it was TRUNCATED, so this is a cap problem, not a server problem)"
                         if truncated else "")
                      + ". NOT a statement about its contents.")
        return res
    res["readable"] = True
    res["mentions_geo_series"] = GEO_SERIES.lower() in body.lower()

    top = {}
    for a in (d.get("attributes") or []):
        if isinstance(a, dict):
            top.setdefault(str(a.get("name")), a.get("value"))
    res["release_date"] = top.get("ReleaseDate")
    # ⛔ WHAT KIND OF RECORD IS THIS? BioStudies serves two very different things under one API and
    # conflating them is how the first run reported ten "mirrors" that were nothing of the kind:
    #   DataSource "Europe PMC" / AttachTo "EuropePMC" -> a LITERATURE record. A paper, with an
    #       abstract. It mentions GSE140686 because it CITES it. It has no samples and no IDATs.
    #   AttachTo "ArrayExpress"                        -> a DATA record, with samples and files.
    # A mirror of a GEO series is necessarily the second kind, so `is_a_data_record` gates it.
    res["data_source"] = top.get("DataSource") or top.get("AttachTo")
    src = str(res["data_source"] or "").lower()
    res["is_a_data_record"] = "europepmc" not in src.replace(" ", "")

    section = d.get("section") or {}
    sat = _attrs(section)
    res["title"] = (sat.get("Title") or [top.get("Title")])[0]
    res["description"] = (sat.get("Description") or [None])[0]
    if res["description"]:
        res["description"] = res["description"][:1200]

    for node in _walk_subsections(section):
        typ = str(node.get("type") or "")
        at = _attrs(node)
        if typ == "Samples":
            sc = (at.get("Sample count") or [None])[0]
            try:
                res["declared_sample_count"] = int(str(sc))
            except (TypeError, ValueError):
                pass
        elif typ == "Factors Table":
            disease = (at.get("disease") or at.get("Disease") or [None])[0]
            n = (at.get("No. of Samples") or [None])[0]
            if disease is None:
                continue
            try:
                n = int(str(n))
            except (TypeError, ValueError):
                n = 0
            res["disease_census"][str(disease)] = res["disease_census"].get(str(disease), 0) + n
            # The IDAT filenames ride along in the `search` valqual of the count attribute.
            for a in (node.get("attributes") or []):
                if not isinstance(a, dict) or a.get("name") != "No. of Samples":
                    continue
                for vq in (a.get("valqual") or []):
                    if isinstance(vq, dict) and vq.get("name") == "search" and vq.get("value"):
                        if _bucket(str(disease)) == "emc":
                            files = re.findall(r'"([^"]+\.idat)"', str(vq["value"]))
                            res["emc_idat_files"].extend(files[:400])
        elif typ == "Characteristics Table":
            res["characteristics_rows"] += 1

    res["n_categories"] = len(res["disease_census"])
    res["census_sum"] = sum(res["disease_census"].values())
    res["census_complete"] = bool(
        res["declared_sample_count"] and res["census_sum"] == res["declared_sample_count"])
    for disease, n in res["disease_census"].items():
        b = _bucket(disease)
        if b == "emc":
            res["emc_categories"][disease] = n
            res["n_emc_samples"] += n
        elif b == "confusable":
            res["confusable_categories"][disease] = n
            res["n_confusable_samples"] += n
    res["emc_idat_files"] = res["emc_idat_files"][:200]
    res["n_emc_idat_files"] = len(res["emc_idat_files"])
    return res


def _fetch_pmc(out):
    """Rung 4 — the published per-case diagnosis table, reached only through discovered identifiers."""
    pmid = out.get("pubmed_id")
    # ⛔ `pubmed_url` IS NOT DECORATION — it is what makes the identifier ANCHORED. `lint_citations`
    # deliberately does not recognise a lowercase `"pmid"` JSON key: the `": "` between key and
    # digits breaks the adjacency it requires, and loosening that would weaken the guarantee the
    # gate exists for (an identifier must appear in a context only a retrieval could produce). The
    # gate's own header records that the fix belongs in the ARTIFACT, not in the linter, and this is
    # that fix. This PMID was read out of GSE140686's `!Series_pubmed_id` and then actually fetched,
    # so the URL form is the honest record of a retrieval rather than a workaround for a red gate.
    pmc = {"pmid": pmid, "pubmed_url": (f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None),
           "pmcid": None, "pmcid_source": None, "fetches": {},
           "supplementary_links_found": [], "supplementary": {}}
    if not pmid:
        pmc["why"] = ("the GEO series header declared no !Series_pubmed_id, so there is no "
                      "discovered identifier to follow and this module will not type one")
        out["pmc"] = pmc
        return

    # elink first: it is the primary NCBI linkage and it answers from the PMID alone.
    url = (f"{EUTILS_ELINK}?dbfrom=pubmed&db=pmc&id={pmid}&retmode=json"
           f"&tool=rare-cancers-emc-data-level-sweep&email=trimcrae@gmail.com")
    body, rec = _get(url, timeout=120, note="elink pubmed->pmc, to DISCOVER the PMCID")
    pmc["fetches"]["elink"] = rec
    if body:
        try:
            d = json.loads(body)
            for ls in (d.get("linksets") or []):
                for db in (ls.get("linksetdbs") or []):
                    for lid in (db.get("links") or []):
                        pmc["pmcid"] = f"PMC{lid}"
                        pmc["pmcid_source"] = "elink"
                        break
                    if pmc["pmcid"]:
                        break
        except Exception as exc:                                       # noqa: BLE001
            pmc["elink_parse_error"] = f"{type(exc).__name__}: {exc}"

    if not pmc["pmcid"]:
        url = (f"{NCBI_IDCONV}?ids={pmid}&format=json"
               f"&tool=rare-cancers-emc-data-level-sweep&email=trimcrae@gmail.com")
        body, rec = _get(url, timeout=120, note="NCBI ID converter fallback, to DISCOVER the PMCID")
        pmc["fetches"]["idconv"] = rec
        if body:
            try:
                d = json.loads(body)
                for r in (d.get("records") or []):
                    if r.get("pmcid"):
                        pmc["pmcid"] = r["pmcid"]
                        pmc["pmcid_source"] = "idconv"
                        break
            except Exception as exc:                                   # noqa: BLE001
                pmc["idconv_parse_error"] = f"{type(exc).__name__}: {exc}"

    if not pmc["pmcid"]:
        pmc["why"] = ("neither elink nor the ID converter returned a PMCID for the discovered "
                      "PMID. That is a statement about these two fetches, not about the article.")
        out["pmc"] = pmc
        return

    links = []
    # 4a · the PMC article page. ⛔ MEASURED TO BE A CAPTCHA, KEPT AS A CONTROL. It is graded on
    # CONTENT, not length: the first run's 21,246-byte "200" was a reCAPTCHA challenge page, and a
    # size threshold called that healthy.
    art_url = PMC_ARTICLE_FMT.format(pmcid=pmc["pmcid"])
    body, rec = _get(art_url, timeout=240, note="PMC article page, for its supplementary links")
    pmc["fetches"]["pmc_article"] = rec
    pmc["pmc_article_bytes"] = rec.get("bytes")
    pmc["pmc_article_interstitial_markers"] = _interstitial_markers(body)
    pmc["pmc_article_was_served"] = bool(body) and not pmc["pmc_article_interstitial_markers"]
    if body:
        pmc["pmc_article_head"] = body[:1500]
        if pmc["pmc_article_was_served"]:
            for m in re.finditer(r'href="([^"]+)"', body):
                u = m.group(1).replace("&amp;", "&")
                if re.search(r"\.(xlsx?|csv|tsv|txt|zip|pdf|docx?)(\?|$)", u, re.I) and "/bin/" in u:
                    full = urllib.parse.urljoin(art_url, u)
                    if full not in links:
                        links.append(full)

    # 4b · Europe PMC full text XML — EBI, no interstitial, and <supplementary-material> is where an
    # article DECLARES its own supplementary files. The names come from the article, never from us.
    fx_url = f"{EPMC_REST}{pmc['pmcid']}/fullTextXML"
    xml, rec = _get(fx_url, timeout=300, note="Europe PMC full text XML, for its declared supplements")
    pmc["fetches"]["europepmc_fulltext"] = rec
    pmc["fulltext_interstitial_markers"] = _interstitial_markers(xml)
    if xml:
        pmc["fulltext_bytes"] = len(xml)
        decl = []
        for m in re.finditer(r"<supplementary-material\b[^>]*>(.*?)</supplementary-material>",
                             xml, re.S | re.I):
            blk = m.group(1)
            for h in re.finditer(r'xlink:href="([^"]+)"', blk):
                if h.group(1) not in decl:
                    decl.append(h.group(1))
        for h in re.finditer(r'<media\b[^>]*xlink:href="([^"]+)"', xml, re.I):
            if h.group(1) not in decl:
                decl.append(h.group(1))
        pmc["supplements_declared_by_the_article"] = decl[:40]
        # A declared name resolves against the article's own /bin/ path on PMC.
        for nm in decl[:MAX_SUPPL_FILES]:
            if nm.startswith("http"):
                full = nm
            else:
                full = f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{pmc['pmcid'][3:]}/bin/{nm}"
            if full not in links:
                links.append(full)

    # 4c · Europe PMC's supplementaryFiles zip. Candidate URL shapes are TRIED and each status
    # recorded — the previous single guess 404'd, and a wrong path must never read as no supplement.
    pmc["supplementary_endpoint_attempts"] = []
    for shape in EPMC_SUPPL_SHAPES:
        epmc_url = EPMC_REST + shape.format(pmcid=pmc["pmcid"])
        raw, rec = _get_bytes(epmc_url, timeout=600, tries=2,
                              note="Europe PMC supplementaryFiles (zip)")
        pmc["supplementary_endpoint_attempts"].append(
            {"url": epmc_url, "http": rec.get("http"), "bytes": rec.get("bytes")})
        if raw is None:
            continue
        if len(raw) <= MAX_SUPPL_BYTES:
            pmc["supplementary"][epmc_url] = {
                "fetch": rec, "parsed": _parse_supplementary(epmc_url, raw), "parse_error": None}
        else:
            pmc["supplementary"][epmc_url] = {
                "fetch": rec, "parsed": None,
                "parse_error": f"over the {MAX_SUPPL_BYTES}-byte cap; not parsed"}
        break

    # 4d · the NCBI Open Access package — the canonical programmatic route to an OA article's whole
    # supplement bundle. The archive LOCATION is discovered from the service, never constructed.
    oa_body, rec = _get(f"{NCBI_OA_FCGI}?id={pmc['pmcid']}", timeout=180,
                        note="NCBI OA service, to DISCOVER the article's package location")
    pmc["fetches"]["ncbi_oa"] = rec
    pkg = None
    if oa_body:
        pmc["oa_response_head"] = oa_body[:800]
        mm = re.search(r'<error[^>]*code="([^"]*)"[^>]*>([^<]*)', oa_body)
        if mm:
            pmc["oa_error"] = f"{mm.group(1)}: {mm.group(2)}"
        cands = re.findall(r'<link[^>]*format="(tgz|pdf)"[^>]*href="([^"]+)"', oa_body)
        for fmt, href in cands:
            if fmt == "tgz":
                # ftp:// is not fetchable here; the same path is served over https.
                pkg = href.replace("ftp://ftp.ncbi.nlm.nih.gov/", "https://ftp.ncbi.nlm.nih.gov/")
                break
    pmc["oa_package_url"] = pkg
    if pkg:
        raw, rec = _get_bytes(pkg, timeout=900, note="NCBI OA package (tar.gz) for this article")
        pmc["fetches"]["ncbi_oa_package"] = rec
        if raw is not None and len(raw) <= MAX_SUPPL_BYTES:
            pmc["supplementary"][pkg] = {
                "fetch": rec, "parsed": _parse_supplementary(pkg, raw), "parse_error": None}
        elif raw is not None:
            pmc["supplementary"][pkg] = {
                "fetch": rec, "parsed": None,
                "parse_error": f"over the {MAX_SUPPL_BYTES}-byte cap; not parsed"}

    pmc["supplementary_links_found"] = links[:40]
    for u in links[:MAX_SUPPL_FILES]:
        raw, rec_s = _get_bytes(u, timeout=300, note="PMC supplementary file")
        entry = {"fetch": rec_s, "parsed": None, "parse_error": None}
        if raw is not None and rec_s.get("bytes", 0) <= MAX_SUPPL_BYTES:
            entry["parsed"] = _parse_supplementary(u, raw)
        elif raw is not None:
            entry["parse_error"] = f"over the {MAX_SUPPL_BYTES}-byte cap; not parsed"
        pmc["supplementary"][u] = entry
        time.sleep(1)
    out["pmc"] = pmc


def _fetch_publisher(out):
    """The publisher page. Kept because it is free, and because a stub is a measurement."""
    art, rec_art = _get(GEO_ARTICLE_URL, timeout=180, note="article page, for its supplementary links")
    out["fetches"]["article"] = rec_art
    # ⛔ STORED, so "nature.com served an interstitial" is provable from the artifact rather than
    # asserted. A 200 that is 3 KB long is not a paper and the body is the evidence of which it is.
    out["article_head"] = art[:1500] if art else None
    out["article_interstitial_markers"] = _interstitial_markers(art)
    # Two independent reasons a publisher page is not a paper, reported separately: it was too short
    # to be one, or it carried a bot wall. Either means zero links is a TRANSPORT result.
    out["article_looks_like_a_stub"] = (
        rec_art.get("bytes") is not None and rec_art.get("bytes") < STUB_BYTES)
    out["article_was_served"] = bool(art) and not (
        out["article_looks_like_a_stub"] or out["article_interstitial_markers"])
    links = []
    if art:
        for m in re.finditer(r'href="(https?://[^"]*%s[^"]*)"' % re.escape(SUPPL_HOST_HINT), art):
            u = m.group(1).replace("&amp;", "&")
            if u not in links:
                links.append(u)
    out["supplementary_links_found"] = links[:40]
    suppl = {}
    for u in links[:MAX_SUPPL_FILES]:
        raw, rec_s = _get_bytes(u, timeout=300, note="supplementary file")
        entry = {"fetch": rec_s, "parsed": None, "parse_error": None}
        if raw is not None and rec_s.get("bytes", 0) <= MAX_SUPPL_BYTES:
            entry["parsed"] = _parse_supplementary(u, raw)
        elif raw is not None:
            entry["parse_error"] = f"over the {MAX_SUPPL_BYTES}-byte cap; not parsed"
        suppl[u] = entry
        time.sleep(1)
    out["supplementary"] = suppl


def fetch_methylation():
    out = {"series": GEO_SERIES, "fetches": {}}
    # ⚠ ORDER MATTERS AND IT IS A DEPENDENCY, NOT A STYLE. GEO declares the PMID; the PMC rung turns
    # that into a PMCID; and the BioStudies rung uses the PMCID to fetch the paper's OWN record.
    # Run BioStudies first and that record is unreachable, because nothing has discovered its name
    # yet — and the alternative is typing it, which is the thing this module exists not to do.
    reached = _fetch_geo(out)
    _fetch_publisher(out)
    _fetch_pmc(out)
    _fetch_biostudies(out)
    out["arm_state"] = "FETCHED" if reached else "UNREACHABLE"
    return out


def _bucket(text):
    """Which bucket does this label fall in? EXCLUSIVE, and the MOST SPECIFIC match decides.

    ⛔⛔ THE SUBSTRING TRAP RUNS IN BOTH DIRECTIONS, AND EITHER ORDERING ALONE IS WRONG. This is a
    one-of-a-pair defect and both halves are live:

        "extraskeletal myxoid chondrosarcoma"  CONTAINS the confusable "chondrosarcoma"
        "skeletal myxoid chondrosarcoma"       CONTAINS the EMC term  "myxoid chondrosarcoma"

    So "EMC first" files the SKELETAL tumour as EMC — manufacturing a cohort out of a different
    disease — and "confusable first" files real EMC as skeletal and reports zero. Each ordering
    fails exactly the case the other one passes, which is why testing only one direction proves
    nothing. What resolves it is that the LONGEST matching term wins: a label matching both lists
    is decided by specificity rather than by the order the lists happen to be tested in.
    "extraskeletal myxoid chondrosarcoma" (35 chars) beats "chondrosarcoma" (14), and "skeletal
    myxoid chondrosarcoma" (30) beats "myxoid chondrosarcoma" (21). ⛔ That tie-break is the
    load-bearing property and reversing it flips BOTH cases at once.

    ⚠ THE LEFT WORD-BOUNDARY ANCHOR IN `_term_hits` DOES SOMETHING NARROWER THAN IT LOOKS, AND THE
    DIFFERENCE WAS MEASURED RATHER THAN ASSUMED. Across all 54 disease labels the E-MTAB-9875
    census actually carries plus eleven constructed extraskeletal/skeletal edge cases, anchored and
    unanchored matching disagree on exactly ONE label: `osteochondrosarcoma`, which unanchored
    matching sweeps into the confusable bucket on a mid-word hit. So the anchor is what stops an
    unrelated compound word being counted at all; it is NOT what separates the extraskeletal tumour
    from the skeletal one. An earlier version of this docstring claimed both properties carried the
    extraskeletal/skeletal split, and a mutation test disproved it: deleting the anchor left every
    extraskeletal/skeletal assertion passing.
    """
    e = _term_hits(text, EMC_TERMS)
    c = _term_hits(text, EMC_CONFUSABLE_TERMS)
    if not e and not c:
        return None
    longest_e = max((len(t) for t in e), default=-1)
    longest_c = max((len(t) for t in c), default=-1)
    return "emc" if longest_e >= longest_c else "confusable"


def _parse_supplementary(url, raw):
    """Pull disease-term evidence out of one supplementary file, whatever format it arrived in.

    ⛔ REPORTS WHAT IT COULD READ, SEPARATELY FROM WHAT IT FOUND. A binary this parser cannot open
    is `readable: false` with the reason, never "contains no EMC" -- that distinction is the whole
    reason the first run's zero did not close this route.
    """
    low = url.lower()
    res = {"url": url, "kind": None, "readable": False, "why": None,
           "n_rows_scanned": 0, "emc_rows": [], "n_emc_rows": 0, "confusable_rows": 0,
           "emc_case_ids": [], "members": []}
    blob = raw if isinstance(raw, bytes) else (raw or "").encode("utf-8", "surrogateescape")
    try:
        # A zip is a CONTAINER, not a format: Europe PMC returns every supplement in one, so it is
        # unpacked and each member parsed by the same rules. A member this parser cannot open is
        # listed as unreadable with its reason, exactly as a standalone file would be.
        if blob[:2] == b"\x1f\x8b" or low.endswith((".tar.gz", ".tgz")):
            # The NCBI OA package is a gzipped tar of the article's whole file set. Same contract as
            # the zip branch: every member is parsed, and a member this parser cannot open is listed
            # with its reason rather than counted as empty.
            import io, tarfile                                         # noqa: PLC0415
            res["kind"] = "tar.gz"
            with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
                for mem in tf.getmembers()[:80]:
                    if not mem.isfile():
                        continue
                    fh = tf.extractfile(mem)
                    if fh is None:
                        continue
                    inner = _parse_supplementary(mem.name, fh.read())
                    res["members"].append({"name": mem.name, "readable": inner["readable"],
                                           "why": inner["why"], "size": mem.size,
                                           "n_emc_rows": inner["n_emc_rows"],
                                           "confusable_rows": inner["confusable_rows"]})
                    res["n_rows_scanned"] += inner["n_rows_scanned"]
                    res["n_emc_rows"] += inner["n_emc_rows"]
                    res["confusable_rows"] += inner["confusable_rows"]
                    for r in inner["emc_rows"]:
                        if len(res["emc_rows"]) < 25:
                            res["emc_rows"].append(f"[{mem.name}] {r}")
                    for cid in inner["emc_case_ids"]:
                        if cid not in res["emc_case_ids"]:
                            res["emc_case_ids"].append(cid)
            res["readable"] = any(m["readable"] for m in res["members"])
            if not res["readable"]:
                res["why"] = "no member of the archive could be opened by this parser"
            return res

        if blob[:2] == b"PK" and not low.endswith((".xlsx", ".xls", ".docx")):
            import io, zipfile                                         # noqa: PLC0415
            res["kind"] = "zip"
            rows = []
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                for nm in z.namelist()[:60]:
                    inner = _parse_supplementary(nm, z.read(nm))
                    res["members"].append({"name": nm, "readable": inner["readable"],
                                           "why": inner["why"],
                                           "n_emc_rows": inner["n_emc_rows"],
                                           "confusable_rows": inner["confusable_rows"]})
                    res["n_rows_scanned"] += inner["n_rows_scanned"]
                    res["n_emc_rows"] += inner["n_emc_rows"]
                    res["confusable_rows"] += inner["confusable_rows"]
                    for r in inner["emc_rows"]:
                        if len(res["emc_rows"]) < 25:
                            res["emc_rows"].append(f"[{nm}] {r}")
                    for cid in inner["emc_case_ids"]:
                        if cid not in res["emc_case_ids"]:
                            res["emc_case_ids"].append(cid)
            res["readable"] = any(m["readable"] for m in res["members"])
            if not res["readable"]:
                res["why"] = "no member of the archive could be opened by this parser"
            return res

        if low.endswith((".xlsx", ".xls")) or blob[:2] == b"PK":
            res["kind"] = "spreadsheet"
            try:
                import openpyxl                                        # noqa: PLC0415
            except ImportError as exc:                                 # pragma: no cover
                res["why"] = f"openpyxl unavailable ({exc}); NOT a statement about the file"
                return res
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as fh:
                fh.write(blob)
                tmp = fh.name
            wb = openpyxl.load_workbook(tmp, read_only=True, data_only=True)
            rows = []
            for ws in wb.worksheets:
                for r in ws.iter_rows(values_only=True):
                    rows.append(" | ".join("" if c is None else str(c) for c in r))
                    if len(rows) > 40000:
                        break
            res["readable"] = True
            res["n_rows_scanned"] = len(rows)
        elif low.endswith(".pdf") or blob[:5] == b"%PDF-":
            # ⛔ NOT READ, AND SAID SO. Extracting text from a PDF needs a dependency this module
            # does not carry; recording it as unreadable keeps it distinguishable from a file that
            # was read and held nothing.
            res["kind"] = "pdf"
            res["why"] = "PDF text extraction is not implemented here; NOT a statement about its contents"
            return res
        else:
            res["kind"] = "text"
            rows = blob.decode("utf-8", "replace").split("\n")
            res["readable"] = True
            res["n_rows_scanned"] = len(rows)
    except Exception as exc:                                           # noqa: BLE001
        res["why"] = f"{type(exc).__name__}: {exc} -- NOT a statement about the file's contents"
        return res

    for line in rows:
        b = _bucket(line)
        if b == "confusable":
            res["confusable_rows"] += 1
        elif b == "emc":
            res["n_emc_rows"] += 1
            if len(res["emc_rows"]) < 25:
                res["emc_rows"].append(line[:300])
            # ⭐ THE JOIN KEY, EXTRACTED SEPARATELY FROM THE DISPLAY ROW. `emc_rows` is a bounded
            # sample for a human to read; the join must not depend on how many rows we happened to
            # keep for display, so the case identifiers are collected in their own field.
            for cid in CASE_ID_RE.findall(line):
                norm = f"{cid[0].upper()}_SAMPLE {int(cid[1])}"
                if norm not in res["emc_case_ids"]:
                    res["emc_case_ids"].append(norm)
    return res


def _index_geo_cases(txt):
    """GSM -> {case_id, platform, idat_urls} from the deposit's own per-sample records.

    ⛔ KEYED ON THE DECLARED IDENTIFIER, NEVER ON ORDER. See CASE_ID_RE. A sample that declares no
    case id is simply absent from the index rather than being matched to a neighbouring position.
    """
    out = {}
    for gsm, blob in _split_geo_samples(txt).items():
        cid = None
        for line in blob.split("\n"):
            if line.startswith("!Sample_description"):
                mm = CASE_ID_RE.search(line)
                if mm:
                    cid = f"{mm.group(1).upper()}_SAMPLE {int(mm.group(2))}"
                    break
        if not cid:
            continue
        plat = re.findall(r"!Sample_platform_id\s*=\s*(\S+)", blob)
        files = re.findall(r"!Sample_supplementary_file[^=]*=\s*(\S+)", blob)
        out[cid] = {"gsm": gsm, "platform": plat[0] if plat else None,
                    "files": files,
                    "idat_urls": [f for f in files if ".idat" in f.lower()]}
    return out


def _split_geo_samples(txt):
    """Split a GEO `targ=all&view=brief` stream into per-sample blobs keyed by GSM."""
    if not txt:
        return {}
    blobs, cur, key = {}, [], None
    for line in txt.split("\n"):
        if line.startswith("^SAMPLE"):
            if key:
                blobs[key] = "\n".join(cur)
            key = line.split("=", 1)[-1].strip()
            cur = [line]
        elif key:
            cur.append(line)
    if key:
        blobs[key] = "\n".join(cur)
    return blobs


def _term_hits(text, terms):
    """Which of `terms` occur in `text`, anchored at a word boundary on the LEFT.

    ⛔ THE LEFT ANCHOR IS THE WHOLE POINT — see `_bucket`. A plain `in` test matches "skeletal
    myxoid chondrosarcoma" inside "extraskeletal myxoid chondrosarcoma", which is how the skeletal
    tumour and the extraskeletal one become indistinguishable. The right-hand side is intentionally
    open so prefix terms still fire on truncated labels.
    """
    low = (text or "").lower()
    return [t for t in terms
            if re.search(r"(?<![0-9a-z])" + re.escape(t.lower()), low)]


# ────────────────────────────────────────────────────────────────────────────────────────────────
# DERIVE
# ────────────────────────────────────────────────────────────────────────────────────────────────

def derive(inp):
    res = {
        "_generated_utc": _now(),
        "_inputs_generated_utc": inp.get("_generated_utc"),
        "_question": ("Is there EMC-bearing public molecular data that a depositor-prose search "
                      "cannot see? `emc_cohort_search.py` bounded its own negative to prose; this "
                      "asks what lies outside that bound."),
        "_language_discipline": ("Nothing here is an efficacy, selectivity, safety, "
                                 "therapeutic-window or clinical-readiness claim. A sample counted "
                                 "here is a metadata match, never a diagnosis."),
        "arms": {},
    }

    # ── ARM 1 ───────────────────────────────────────────────────────────────────────────────────
    s = inp.get("snaptron") or {}
    arm1 = {"_what": ("Does the public splice-junction index answer at all, and does what it serves "
                      "carry the fields a fusion-junction search would need?"),
            "state": s.get("arm_state", "NOT_RUN")}
    if s.get("arm_state") == "FETCHED":
        transport = ((s.get("controls", {}).get("transport") or {}).get("shape") or {})
        absent = ((s.get("controls", {}).get("absent") or {}).get("shape") or {})
        t_n = transport.get("n_records", 0)
        a_n = absent.get("n_records", 0)
        arm1["transport_control_records"] = t_n
        arm1["absent_control_records"] = a_n
        arm1["controls_pass"] = bool(t_n > 0 and a_n == 0)
        arm1["compilation_used"] = s.get("compilation_used")
        arm1["compilations_that_answered"] = s.get("compilations_that_answered", [])
        arm1["served_columns"] = transport.get("columns", [])
        per = {}
        for g, q in (s.get("queries") or {}).items():
            shape = q.get("shape") or {}
            per[g] = {
                "http": (q.get("fetch") or {}).get("http"),
                "n_records": shape.get("n_records") if q.get("shape") else None,
                "chromosomes": shape.get("chromosomes") if q.get("shape") else None,
                "readable": q.get("shape") is not None,
            }
        arm1["per_gene"] = per
        if not arm1["controls_pass"]:
            arm1["verdict"] = "TRANSPORT_FAILED"
            arm1["⛔"] = ("The known-answer control did not behave. Every count in `per_gene` is "
                          "withheld from interpretation: a null from an instrument that recovers no "
                          "known positive is a broken search, not a negative.")
        else:
            arm1.update(_depletion_verdict(s))
    elif s.get("arm_state") == "UNREACHABLE":
        arm1["verdict"] = "UNREACHABLE"
        arm1["⛔"] = ("No compilation answered. That is a statement about this fetch, not about the "
                      "service and not about the data (CLAUDE.md §4).")
    else:
        arm1["verdict"] = "NOT_RUN"
    res["arms"]["snaptron_junction_index"] = arm1

    # ── ARM 2 ───────────────────────────────────────────────────────────────────────────────────
    m = inp.get("methylation") or {}
    arm2 = {"_what": (f"Does {GEO_SERIES} — a pan-sarcoma deposit whose title names no disease — "
                      "carry EMC samples, and are they open? And where are its per-case diagnoses "
                      "actually published?"),
            "state": m.get("arm_state", "NOT_RUN"),
            "series": GEO_SERIES,
            "stages": {}}
    if m.get("arm_state") == "FETCHED":
        head = m.get("geo_self_text") or ""
        allt = m.get("geo_all_text") or ""
        arm2["series_title"] = next(
            (ln.split("=", 1)[-1].strip() for ln in head.split("\n")
             if ln.startswith("!Series_title")), None)
        arm2["platforms"] = sorted(set(
            re.findall(r"!Series_platform_id\s*=\s*(GPL\d+)", head)
            or re.findall(r"(GPL\d+)", head)))
        blobs = _split_geo_samples(allt)
        arm2["n_samples_read"] = len(blobs)
        arm2["n_samples_declared_by_series"] = len(
            re.findall(r"!Series_sample_id\s*=\s*GSM\d+", head)) or None

        emc, confusable = {}, {}
        for gsm, txt in blobs.items():
            b = _bucket(txt)
            if b == "emc":
                emc[gsm] = _term_hits(txt, EMC_TERMS)
            elif b == "confusable":
                confusable[gsm] = _term_hits(txt, EMC_CONFUSABLE_TERMS)
        arm2["n_samples_naming_emc"] = len(emc)
        arm2["n_samples_naming_a_confusable"] = len(confusable)
        arm2["emc_samples_sample"] = dict(list(emc.items())[:15])
        arm2["⚠ counting_rule"] = ("`n_samples_naming_emc` counts per-sample records whose OWN text "
                                    "matches a disease term. It is a depositor claim exactly as a "
                                    "series title is, and the confusable count is reported "
                                    "separately because a substring search for 'myxoid "
                                    "chondrosarcoma' also hits the skeletal tumour, which is a "
                                    "different disease with a different driver.")
        arm2["stages"]["1_geo_deposit"] = {
            "read": len(blobs) > 0,
            "n_samples_read": len(blobs),
            "n_samples_naming_emc": len(emc),
            "verdict": ("SAMPLES_CARRY_NO_DIAGNOSIS" if blobs and not emc
                        else "EMC_NAMED_IN_SAMPLE_RECORDS" if emc else "NOT_READ")}

        # ── stage 2/3 · the EBI records ─────────────────────────────────────────────────────────
        ctrl = m.get("biostudies_controls") or {}
        t_hits = (ctrl.get("transport") or {}).get("n_hits")
        a_hits = (ctrl.get("absent") or {}).get("n_hits")
        search_ok = bool(t_hits) and a_hits == 0
        recs = m.get("biostudies_records") or {}
        parsed = {a: (e.get("parsed") or {}) for a, e in recs.items()}
        # ⛔ A MIRROR IS A DATA RECORD THAT NAMES THE SERIES — not any record that mentions it.
        # The first run flagged ten "mirrors" which were all Europe PMC LITERATURE records: papers
        # that cite GSE140686 in their text. They carry an abstract and no samples, so treating a
        # string match as a mirror would have reported the deposit as mirrored at EBI when it is
        # not, and pointed the next session at ten papers as though they were cohorts.
        mirror_found = [a for a, p in parsed.items()
                        if p.get("readable") and p.get("mentions_geo_series")
                        and p.get("is_a_data_record")]
        citing_papers = [a for a, p in parsed.items()
                         if p.get("readable") and p.get("mentions_geo_series")
                         and not p.get("is_a_data_record")]
        deposits = []
        for a, e in recs.items():
            p = parsed.get(a) or {}
            deposits.append({
                "accession": a,
                "provenance": e.get("provenance"),
                "http": (e.get("fetch") or {}).get("http"),
                "served_bytes": e.get("served_bytes"),
                "truncated": e.get("truncated"),
                "readable": p.get("readable"),
                "why_unreadable": p.get("why"),
                "title": p.get("title"),
                "description": p.get("description"),
                "data_source": p.get("data_source"),
                "is_a_data_record": p.get("is_a_data_record"),
                "mentions_the_geo_series": p.get("mentions_geo_series"),
                "is_a_mirror_of_the_geo_series": bool(p.get("mentions_geo_series")
                                                      and p.get("is_a_data_record")),
                "declared_sample_count": p.get("declared_sample_count"),
                "n_disease_categories": p.get("n_categories"),
                "census_sum": p.get("census_sum"),
                "census_complete": p.get("census_complete"),
                "disease_census": p.get("disease_census"),
                "emc_categories": p.get("emc_categories"),
                "n_emc_samples": p.get("n_emc_samples"),
                "n_emc_idat_files": p.get("n_emc_idat_files"),
                "emc_idat_files_sample": (p.get("emc_idat_files") or [])[:20],
                "confusable_categories": p.get("confusable_categories"),
                "n_confusable_samples": p.get("n_confusable_samples"),
            })
        arm2["ebi_deposits"] = deposits
        labelled_complete = [d for d in deposits if d.get("census_complete")]
        ebi_emc = sum(d.get("n_emc_samples") or 0 for d in labelled_complete)
        arm2["stages"]["2_ebi_mirror_search"] = {
            "controls_passed": search_ok,
            "transport_hits": t_hits,
            "absent_hits": a_hits,
            "discovered": m.get("biostudies_discovered") or [],
            "a_real_mirror_of_the_geo_series_was_found": bool(mirror_found),
            "mirrors": mirror_found,
            "literature_records_citing_the_series": citing_papers,
            "⚠ mirror_rule": (
                "A mirror must be a DATA record (samples, files) that names the series. A Europe "
                "PMC literature record that mentions the accession is a paper CITING the deposit "
                "and is listed separately — it is not a second copy of the data."),
            "verdict": ("SEARCH_CONTROLS_FAILED" if not search_ok
                        else "MIRROR_FOUND" if mirror_found else "NO_EBI_MIRROR_OF_THIS_SERIES"),
            "⛔": ("A search whose transport control returns nothing, or whose absent control "
                   "returns hits, cannot support 'no mirror exists' — that would be a broken "
                   "search reported as a negative."),
        }
        arm2["stages"]["3_ebi_records"] = {
            "n_records_fetched": len(recs),
            "n_with_a_complete_census": len(labelled_complete),
            "n_emc_samples_in_complete_censuses": ebi_emc,
            "⭐ completeness_rule": (
                "A per-disease census counts as COMPLETE only when its own category counts sum to "
                "the record's declared `Sample count`. Only then does a zero mean 'no EMC anywhere "
                "in this deposit' rather than 'no EMC in the part that was read'."),
        }

        # ── stage 4 · the published table ───────────────────────────────────────────────────────
        def _harvest(sup):
            p = [(u, e.get("parsed")) for u, e in (sup or {}).items() if e.get("parsed")]
            rd = [(u, d) for u, d in p if d.get("readable")]
            return p, rd

        pub_parsed, pub_readable = _harvest(m.get("supplementary"))
        pmc = m.get("pmc") or {}
        pmc_parsed, pmc_readable = _harvest(pmc.get("supplementary"))
        all_parsed, all_readable = pub_parsed + pmc_parsed, pub_readable + pmc_readable
        sup_emc = sum(d.get("n_emc_rows", 0) for _, d in all_readable)
        arm2["supplementary_files_fetched"] = len(all_parsed)
        arm2["supplementary_files_readable"] = len(all_readable)
        arm2["supplementary_unreadable"] = [
            {"url": u, "why": d.get("why")} for u, d in all_parsed if not d.get("readable")][:25]
        arm2["supplementary_emc_rows"] = sup_emc
        arm2["supplementary_confusable_rows"] = sum(
            d.get("confusable_rows", 0) for _, d in all_readable)
        arm2["supplementary_emc_rows_sample"] = [
            r for _, d in all_readable for r in d.get("emc_rows", [])][:20]
        # ── the join · published labels -> deposited samples -> IDATs ───────────────────────────
        case_ids, from_display_rows = [], False
        for _, dd in all_readable:
            ids = dd.get("emc_case_ids")
            if ids is None:
                # ⚠ AN OLDER CACHE, PARSED BEFORE `emc_case_ids` EXISTED. Fall back to scraping the
                # display rows so the join still runs — and FLAG it, because `emc_rows` is capped
                # for display at 25 entries. A cache with more EMC rows than that would join a
                # SUBSET and look complete, which is the exact shape of error this module exists to
                # refuse. The flag is what stops a bounded join being read as a full one.
                from_display_rows = True
                ids = []
                for line in (dd.get("emc_rows") or []):
                    for cid in CASE_ID_RE.findall(line):
                        norm = f"{cid[0].upper()}_SAMPLE {int(cid[1])}"
                        if norm not in ids:
                            ids.append(norm)
            for cid in ids:
                if cid not in case_ids:
                    case_ids.append(cid)
        geo_idx = _index_geo_cases(allt)
        cohort, unjoined = [], []
        for cid in case_ids:
            hit = geo_idx.get(cid)
            if not hit:
                unjoined.append(cid)
                continue
            cohort.append({"case_id": cid, "gsm": hit["gsm"], "platform": hit["platform"],
                           "set": cid.split("_")[0].lower(),
                           "n_idat_files": len(hit["idat_urls"]),
                           "idat_urls": hit["idat_urls"]})
        cohort.sort(key=lambda c: (c["set"], c["gsm"]))
        n_ref = sum(1 for c in cohort if c["set"] == "reference")
        n_val = sum(1 for c in cohort if c["set"] == "validation")
        with_idats = [c for c in cohort if c["n_idat_files"] > 0]
        arm2["emc_cohort"] = {
            "n_cases_named_by_the_paper": len(case_ids),
            "n_joined_to_a_deposited_sample": len(cohort),
            "n_not_joined": len(unjoined),
            "case_ids_not_joined": unjoined[:20],
            "n_in_the_reference_set": n_ref,
            "n_in_the_validation_set": n_val,
            "n_with_downloadable_idats": len(with_idats),
            "n_idat_files_total": sum(c["n_idat_files"] for c in cohort),
            "platforms": sorted({c["platform"] for c in cohort if c["platform"]}),
            "case_ids_came_from_capped_display_rows": from_display_rows,
            "cases": cohort,
            "⛔ what_this_count_is": (
                "A count of samples the PAPER'S OWN supplementary table labels with this disease, "
                "joined to the deposit by an identifier BOTH sides declare (GEO's "
                "`!Sample_description = REFERENCE_SAMPLE n` and the table's row key). It is an "
                "author claim carried across a declared join — it is NOT a diagnosis, not a "
                "re-review of any case, and not a patient count. The reference and validation sets "
                "are reported separately because they are different things: the reference set is "
                "the class the classifier was TRAINED on, the validation set is held out."),
            "⚠ what_would_break_it": (
                "The join is a lookup on a declared string. If a future deposit stops carrying the "
                "case id in `!Sample_description`, cases appear in `case_ids_not_joined` rather "
                "than being matched by position — an unjoined case is reported, never guessed."),
        }
        arm2["stages"]["4_published_table"] = {
            "pmid_discovered_from_geo": m.get("pubmed_id"),
            # ⚠ DERIVED from the PMID rather than read back out of the fetch record, so it is
            # present for any cache — including one written before the field existed. A derived
            # value has one source of truth; reading it back would give it two.
            "pubmed_url": (f"https://pubmed.ncbi.nlm.nih.gov/{m['pubmed_id']}/"
                           if m.get("pubmed_id") else None),
            "pmc_url": (f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc['pmcid']}/"
                        if pmc.get("pmcid") else None),
            "pmcid": pmc.get("pmcid"),
            "pmcid_source": pmc.get("pmcid_source"),
            "why_no_pmcid": pmc.get("why"),
            "publisher_page_bytes": ((m.get("fetches") or {}).get("article") or {}).get("bytes"),
            "publisher_page_was_a_stub": m.get("article_looks_like_a_stub"),
            "pmc_page_bytes": pmc.get("pmc_article_bytes"),
            "pmc_page_was_a_stub": pmc.get("pmc_article_looks_like_a_stub"),
            "n_supplementary_files_readable": len(all_readable),
            "n_emc_rows": sup_emc,
            "n_emc_cases_joined_to_deposited_samples": len(cohort),
            "n_emc_cases_with_downloadable_idats": len(with_idats),
            "⚠": ("A publisher page served as a short interstitial yields zero discoverable "
                   "links. That is a transport failure and is recorded as one; it is never a "
                   "statement that the paper has no supplement."),
        }

        # ── the arm's verdict, in the order that keeps a zero honest ────────────────────────────
        if not blobs:
            arm2["verdict"] = "SAMPLE_LEVEL_NOT_READ"
            arm2["⛔"] = ("The series header arrived but no per-sample record did, so the EMC count "
                          "is unmeasured. Absent reading, not a reading of absence.")
        elif len(emc) > 0:
            arm2["verdict"] = "EMC_SAMPLES_PRESENT_IN_A_PROSE_INVISIBLE_DEPOSIT"
        elif sup_emc > 0:
            arm2["verdict"] = "EMC_IN_THE_PUBLISHED_TABLE_NOT_IN_THE_DEPOSIT_LABELS"
            arm2["⭐"] = ("The deposit's own sample records name no disease, and the published "
                          "supplementary table does. The samples are therefore labelled — just not "
                          "in the repository — and the join is what makes this cohort usable. "
                          "⚠ A row naming the disease is not yet a sample count: mapping rows to "
                          "the deposit's cases is the step after this one.")
        elif ebi_emc > 0:
            arm2["verdict"] = "EMC_LABELLED_IN_AN_EBI_DEPOSIT"
            arm2["⭐"] = ("An EBI record carries per-sample disease labels and names this disease "
                          "among them. ⚠ It is a DEPOSITOR CLAIM, never a diagnosis.")
        elif all_readable:
            arm2["verdict"] = "NO_EMC_ROW_IN_A_READABLE_SUPPLEMENT"
            arm2["⚠"] = ("Sample records name no disease AND the supplementary files that could be "
                          "read carry no row naming it. That is a real negative for what was read "
                          "— it is not a claim about files that could not be parsed, which are "
                          "listed in `supplementary_unreadable`.")
        elif labelled_complete:
            # ⛔ THE ONE PLACE A ZERO IS ADMISSIBLE WITHOUT THE PAPER. It is scoped to the deposits
            # whose OWN census is complete, and it says nothing whatever about GSE140686, whose
            # labels are still unlocated.
            arm2["verdict"] = "NO_EMC_IN_A_COMPLETE_EBI_CENSUS_LABELS_FOR_THE_GEO_SERIES_STILL_UNLOCATED"
            arm2["⚠"] = (
                "Two different findings, and they must not be merged. (a) Every EBI deposit whose "
                "per-disease census SUMS TO its own declared sample count was enumerated, and none "
                "names this disease — a real, bounded negative over those deposits. (b) "
                f"{GEO_SERIES}'s own per-case diagnoses were still not located, so nothing here is "
                "a statement about that deposit's contents.")
        else:
            arm2["verdict"] = "LABELS_NOT_LOCATED"
            arm2["⛔"] = ("Every one of the deposit's sample records is present and none names a "
                          "disease, and no supplementary file could be read. Where the per-case "
                          "diagnoses live is therefore still unmeasured. This is the state in which "
                          "reporting 'no EMC samples' would close a live route on a label that was "
                          "never read.")
    elif m.get("arm_state") == "UNREACHABLE":
        arm2["verdict"] = "UNREACHABLE"
    else:
        arm2["verdict"] = "NOT_RUN"
    res["arms"]["pan_sarcoma_methylation_deposit"] = arm2

    res["headline"] = _headline(arm1, arm2)
    return res


def _rate_ratio_ci(c1, n1, c0, n0, z=1.96):
    """95% interval on a ratio of two candidate rates (Katz log method), or an honest refusal.

    ⚠ WHAT IT IS AN INTERVAL ON. Sampling variability, and nothing else. It says how much of the
    gap between two rates could be counting noise. It says NOTHING about whether the two genes are
    comparable — different expression depths, different annotation densities and different tissue
    mixes in the samples that express them are all confounds this interval cannot see, and none of
    them shrinks as n grows. With tens of thousands of samples in each denominator a lower bound
    above 1 is reachable on an effect far too small to be a candidate list, which is exactly why
    the pre-registered bar is an EFFECT SIZE and not a p-value.
    """
    if n1 <= 0 or n0 <= 0 or c1 <= 0:
        return {"ratio": None, "why": "a zero numerator or an empty denominator; ratio undefined"}
    p1 = c1 / n1
    if c0 == 0:
        # The negative side is empty. A ratio against zero is unbounded, so report the CONSERVATIVE
        # side of it: the rule of three puts a 95% upper bound of 3/n on a rate that produced no
        # events, and dividing by that upper bound gives a lower bound on the ratio.
        return {"ratio": None, "ci_low": round(p1 / (3.0 / n0), 4), "ci_high": None,
                "method": "rule-of-three lower bound (the negative side produced no candidates)"}
    p0 = c0 / n0
    rr = p1 / p0
    se = math.sqrt(1.0 / c1 - 1.0 / n1 + 1.0 / c0 - 1.0 / n0)
    return {"ratio": round(rr, 4), "ci_low": round(math.exp(math.log(rr) - z * se), 4),
            "ci_high": round(math.exp(math.log(rr) + z * se), 4), "se_log": round(se, 5),
            "method": "Katz log method, 95%"}


def _cell_view(dep, key, track):
    """One gene's numbers at one cell on one track, or why they are not there."""
    if not dep.get("usable"):
        return {"scoreable": False, "why": dep.get("why", "gene not scoreable")}
    cell = (dep.get("cells") or {}).get(key)
    if cell is None:
        return {"scoreable": False, "why": "cell absent from this gene's grid"}
    if not cell.get("scoreable"):
        return {"scoreable": False, "why": cell.get("why"),
                "n_five_prime_junctions_used": cell.get("n_five_prime_junctions_used")}
    if track == "promiscuity_filtered":
        if not cell.get("promiscuity_tracked"):
            return {"scoreable": False,
                    "why": "the promiscuity track was not tracked at this cell"}
        c, r = (cell.get("n_candidates_promiscuity_filtered"),
                cell.get("candidate_rate_promiscuity_filtered"))
    else:
        c, r = cell.get("n_candidates"), cell.get("candidate_rate")
    return {"scoreable": True, "n_candidates": c, "n_pool": cell.get("n_pool"), "rate": r,
            "n_samples_expressing_downstream": cell.get("n_samples_expressing_downstream"),
            "breakpoint_rank_concentration": cell.get("breakpoint_rank_concentration"),
            "n_five_prime_junctions_used": cell.get("n_five_prime_junctions_used")}


def _depletion_verdict(s):
    """Grade the 5'-depletion search over the whole grid, and REFUSE to report the target unless a
    regime exists in which the controls behave.

    ⛔⛔ THE ONE RULE THIS FUNCTION EXISTS TO ENFORCE: THE OPERATING POINT IS CHOSEN ON THE CONTROLS
    ALONE. `_select_operating_point` below is handed the positive controls and the negative panel
    and is not handed the target at all. Sweeping a grid and then reading off the cell where the
    target looks best is how a null becomes a finding, and `selftest` asserts that replacing every
    target number with anything whatsoever leaves the selected cell where it was.
    """
    q = s.get("queries") or {}
    th = s.get("thresholds") or {}
    ceiling = th.get("neg_panel_rate_ceiling", NEG_PANEL_RATE_CEILING)
    min_pos = th.get("min_positive_control_candidates", MIN_POSITIVE_CONTROL_CANDIDATES)
    min_neg_genes = th.get("min_neg_panel_genes_scoreable", MIN_NEG_PANEL_GENES_SCOREABLE)
    min_enrich = th.get("target_min_enrichment", TARGET_MIN_ENRICHMENT)
    ref_key = th.get("reference_cell", cell_key(*REFERENCE_CELL))

    def present(names):
        return [g for g in names if g in q]

    positives = present(s.get("signature_positives") or SNAPTRON_SIGNATURE_POSITIVES)
    negatives = present(s.get("signature_negative_panel") or SNAPTRON_SIGNATURE_NEGATIVE_PANEL)
    targets = present(s.get("targets") or SNAPTRON_TARGETS)
    context = present(s.get("context_genes") or SNAPTRON_CONTEXT)
    tracks = s.get("grid_tracks") or GRID_TRACKS

    def dep(g):
        return ((q.get(g) or {}).get("depletion") or {})

    out = {"signature_positives": positives, "signature_negative_panel": negatives,
           "targets": targets, "context_genes": context, "tracks": tracks,
           "reference_cell": ref_key,
           "thresholds_applied": {"neg_panel_rate_ceiling": ceiling,
                                  "min_positive_control_candidates": min_pos,
                                  "min_neg_panel_genes_scoreable": min_neg_genes,
                                  "target_min_enrichment": min_enrich},
           "id_space_check": s.get("id_space_check"),
           "search": {}}

    # The reference cell reproduces the FIRST search run's operating point, so the two runs are
    # directly comparable and a moved compilation shows up as a moved number rather than a mystery.
    for g in q:
        d = dep(g)
        v = _cell_view(d, ref_key, "raw")
        out["search"][g] = {
            "role": ("positive_control" if g in positives else
                     "negative_panel" if g in negatives else
                     "target" if g in targets else "context"),
            "usable": d.get("usable", False),
            "why_unusable": d.get("why"),
            "strand_derived": d.get("strand_derived"),
            "n_annotated_junctions": d.get("n_annotated_junctions"),
            "five_prime_support_fraction": d.get("five_prime_support_fraction"),
            "at_reference_cell": v,
        }

    # ── GATE 0 · the cache must have been written by THIS scorer ─────────────────────────────────
    # ⛔ A cache from before the grid carries a `depletion` block with no `cells`, and every cell
    # lookup below would come back empty — which would render as SIGNATURE_NOT_DEMONSTRATED, i.e.
    # as a dead positive control. That is an absent reading dressed as a reading of absence
    # (CLAUDE.md §4), so it gets its own verdict and its own words.
    stale = [g for g in q if (dep(g).get("usable") and "cells" not in dep(g))]
    if stale:
        out["verdict"] = "CACHE_PREDATES_THE_GRID_SCORER"
        out["⛔"] = (
            f"The cached retrieval for {', '.join(sorted(stale))} was written by the single-"
            "threshold scorer that came before the specificity grid, so it carries no cells to "
            "read. NOTHING here is a statement about the controls or the target — it is a "
            "statement about the cache. Re-run `--fetch` in CI.")
        return out

    # ── GATE 1 · a positive control must have fired somewhere ────────────────────────────────────
    live_pos = [g for g in positives
                if any((c or {}).get("n_candidates", 0) > 0
                       for c in (dep(g).get("cells") or {}).values())]
    out["positive_controls_that_fired"] = live_pos
    if not live_pos:
        out["verdict"] = "SIGNATURE_NOT_DEMONSTRATED"
        out["⛔"] = (
            f"No positive control ({', '.join(positives) or 'none configured'}) produced a single "
            "candidate at any cell of the grid. Every target count is WITHHELD from "
            "interpretation: a search that cannot be shown to detect a signature where it is known "
            "to exist reports nothing about a gene where the answer is unknown.")
        return out

    # ── THE GRID, SCORED ON THE CONTROLS ────────────────────────────────────────────────────────
    keys = sorted({k for g in q for k in (dep(g).get("cells") or {})})
    rows = []
    for key in keys:
        for track in tracks:
            neg = {g: _cell_view(dep(g), key, track) for g in negatives}
            scoreable_neg = {g: v for g, v in neg.items() if v.get("scoreable")
                             and v.get("rate") is not None}
            row = {"cell": key, "track": track, "n_neg_panel_scoreable": len(scoreable_neg)}
            if len(scoreable_neg) < min_neg_genes:
                row["admissible"] = False
                row["why_not"] = (f"only {len(scoreable_neg)} negative-panel genes are scoreable "
                                  f"here; an envelope over fewer than {min_neg_genes} is not an "
                                  "envelope")
                rows.append(row)
                continue
            env_gene = max(scoreable_neg, key=lambda g: (scoreable_neg[g]["rate"], g))
            env = scoreable_neg[env_gene]
            row.update({"neg_envelope_gene": env_gene, "neg_envelope_rate": env["rate"],
                        "neg_envelope_candidates": env["n_candidates"],
                        "neg_envelope_pool": env["n_pool"],
                        "neg_panel_rates": {g: v["rate"] for g, v in scoreable_neg.items()}})
            # A zero envelope is the regime we want and an infinite ratio is not a number, so the
            # RANKING uses a conservative stand-in rate. It is recorded, never hidden.
            env_for_ratio = env["rate"] or (0.5 / env["n_pool"] if env.get("n_pool") else None)
            row["neg_envelope_is_zero"] = not env["rate"]
            best = None
            for g in positives:
                v = _cell_view(dep(g), key, track)
                if not v.get("scoreable") or v.get("rate") is None:
                    continue
                enr = (v["rate"] / env_for_ratio) if env_for_ratio else None
                cand = {"gene": g, "rate": v["rate"], "n_candidates": v["n_candidates"],
                        "n_pool": v["n_pool"], "enrichment": round(enr, 3) if enr else None}
                if best is None or (cand["enrichment"] or 0) > (best["enrichment"] or 0):
                    best = cand
            row["positive_best"] = best
            if best is None:
                row["admissible"] = False
                row["why_not"] = "no positive control is scoreable at this cell"
            elif env["rate"] is not None and env["rate"] > ceiling:
                row["admissible"] = False
                row["why_not"] = (f"negative-panel envelope {env['rate']} exceeds the "
                                  f"{ceiling} ceiling")
            elif (best["n_candidates"] or 0) < min_pos:
                row["admissible"] = False
                row["why_not"] = (f"the best positive control retains {best['n_candidates']} "
                                  f"candidates, below the {min_pos} floor")
            elif env["rate"] is not None and best["rate"] <= env["rate"]:
                # ⛔ The first search run's SPECIFICITY_NOT_DEMONSTRATED check, now applied per
                # cell: where an ordinary gene fires at least as often as a known 5'-truncated
                # one, the score is tracking depth or annotation sparsity, not truncation.
                row["admissible"] = False
                row["why_not"] = (f"the negative envelope ({env['rate']}) is at least the best "
                                  f"positive control's rate ({best['rate']}); the score is not "
                                  "measuring truncation here")
            else:
                row["admissible"] = True
            rows.append(row)
    out["grid"] = rows

    # ⭐ ASKED OF EVERY CELL, AND ASKED WHETHER OR NOT A SPECIFIC REGIME EXISTS. The operating
    # point can be too tight to answer; this cannot, because it keeps the loose cells where the
    # target still holds all its samples. It is computed before the admissibility branch precisely
    # so that a NO_SPECIFIC_REGIME run still carries a statement someone can read.
    if targets:
        out["envelope_comparison"] = _envelope_comparison(
            rows, dep(targets[0]), targets[0],
            th.get("min_expected_under_alternative", MIN_EXPECTED_UNDER_ALTERNATIVE))

    admissible = [r for r in rows if r.get("admissible")]
    out["n_cells_scored"] = len(rows)
    out["n_cells_admissible"] = len(admissible)

    if not admissible:
        out["verdict"] = "NO_SPECIFIC_REGIME"
        out["⛔"] = (
            "No cell of the grid drives the negative panel to the pre-registered ceiling while a "
            "positive control still recovers a population. Target counts are WITHHELD, and this "
            "is a result rather than a failure: it says the 5'-depletion signature, as scored "
            "here over this index, cannot be made specific enough for a candidate list at any "
            "combination of these thresholds. The whole trade-off surface is in `grid` so the "
            "shape of that limit is readable rather than asserted.")
        # The nearest misses, so the limit can be described rather than merely stated.
        near = [r for r in rows if r.get("neg_envelope_rate") is not None
                and (r.get("positive_best") or {}).get("n_candidates")]
        near.sort(key=lambda r: (r["neg_envelope_rate"], -(r["positive_best"]["n_candidates"])))
        out["closest_cells"] = near[:5]
        return out

    # ── SELECT, ON THE CONTROLS ALONE ───────────────────────────────────────────────────────────
    op = _select_operating_point(admissible)
    out["operating_point"] = op
    out["⭐ how_the_operating_point_was_chosen"] = (
        "Only the positive controls and the negative panel were read. Among cells where the "
        "negative-panel envelope is at or under the ceiling and a positive control still retains "
        "the minimum number of candidates, the cell with the largest positive-control enrichment "
        "wins; ties break on more positive-control candidates, then on the cell key, then on "
        "track order. The target's numbers are not an input to this choice.")

    key, track = op["cell"], op["track"]
    env_gene = op["neg_envelope_gene"]
    env = _cell_view(dep(env_gene), key, track)

    def read(g):
        v = _cell_view(dep(g), key, track)
        if not v.get("scoreable") or v.get("rate") is None:
            return {"scoreable": False, "why": v.get("why")}
        ci = _rate_ratio_ci(v["n_candidates"], v["n_pool"], env["n_candidates"], env["n_pool"])
        expected = env["rate"] * v["n_pool"] if env["rate"] is not None else None
        return {"scoreable": True, "n_candidates": v["n_candidates"], "n_pool": v["n_pool"],
                "rate": v["rate"], "enrichment_over_negative_envelope": ci,
                "expected_from_background": round(expected, 1) if expected is not None else None,
                "excess_over_background": (round(v["n_candidates"] - expected, 1)
                                           if expected is not None else None),
                "breakpoint_rank_concentration": v.get("breakpoint_rank_concentration")}

    out["at_operating_point"] = {g: read(g) for g in q}
    out["verdict"] = "SEARCHED"

    tgt_name = targets[0] if targets else None
    tgt = out["at_operating_point"].get(tgt_name) if tgt_name else None
    out["target"] = tgt_name
    if not tgt or not tgt.get("scoreable"):
        out["target_verdict"] = "TARGET_NOT_SCOREABLE_AT_THE_OPERATING_POINT"
        out["⛔"] = ("A specific regime exists on the controls, but the target could not be scored "
                     "in it: " + ((tgt or {}).get("why") or "no reason recorded") + ". That is an "
                     "absent reading, not a reading of absence.")
        return out

    # ⛔ CAN THIS CELL ANSWER AT ALL? Asked before the answer is read, and of the POOL, not the count.
    min_expected = th.get("min_expected_under_alternative", MIN_EXPECTED_UNDER_ALTERNATIVE)
    env_rate = env.get("rate")
    expected_if_enriched = ((tgt["n_pool"] * env_rate * min_enrich)
                            if (env_rate is not None and tgt.get("n_pool")) else None)
    out["target_power_at_operating_point"] = {
        "n_pool": tgt.get("n_pool"),
        "negative_envelope_rate": env_rate,
        "expected_candidates_if_enriched_at_the_bar": (round(expected_if_enriched, 2)
                                                       if expected_if_enriched is not None else None),
        "minimum_required": min_expected,
        "powered": bool(expected_if_enriched is not None and expected_if_enriched >= min_expected),
        "pool_that_would_be_needed": (int(math.ceil(min_expected / (env_rate * min_enrich)))
                                      if env_rate else None),
        "_what": ("whether a cell tight enough to hold the background down still leaves the target "
                  "enough samples to show an enrichment at the pre-registered bar. It reads the "
                  "pool size and the background rate, never the target's own count."),
    }

    ci_low = (tgt["enrichment_over_negative_envelope"] or {}).get("ci_low")
    out["target_enrichment_ci_low"] = ci_low
    if not out["target_power_at_operating_point"]["powered"]:
        out["target_verdict"] = "TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT"
        need = out["target_power_at_operating_point"]["pool_that_would_be_needed"]
        out["⛔"] = (
            "The regime the controls select is tight enough to hold the background down and, in "
            f"doing so, leaves the target only {tgt['n_pool']} samples. Against an envelope of "
            f"{env_rate}, a target enriched at the pre-registered {min_enrich}x would be expected "
            f"to yield {out['target_power_at_operating_point']['expected_candidates_if_enriched_at_the_bar']} "
            f"candidates here — so whatever the target returned, this cell cannot answer. It is an "
            f"ABSENT READING, NOT A READING OF ABSENCE (CLAUDE.md §4), and it is reported as one. "
            f"A pool of about {need} would have been needed. ⭐ The statement that IS powered is in "
            "`envelope_comparison`, which asks a different and weaker question of every cell at "
            "once and answers it where the target has all its samples.")
    elif ci_low is not None and ci_low > min_enrich:
        out["target_verdict"] = "TARGET_SEPARATES"
        out["⭐"] = (
            f"At the control-selected operating point the target's candidate rate clears the "
            f"negative-panel envelope with a 95% lower bound of {ci_low} on the ratio, above the "
            f"pre-registered {min_enrich}. ⛔ THAT IS AN ENRICHMENT, NOT A DETECTION: the excess "
            "over background is an estimate of how many candidates are not explained by what an "
            "ordinary gene does, and no individual sample in the list is thereby a fusion, a "
            "tumour, or a diagnosis.")
        if tgt_name == "NR4A3":
            out["nr4a3_candidates"] = tgt["n_candidates"]
    else:
        out["target_verdict"] = "TARGET_DOES_NOT_SEPARATE"
        out["⛔"] = (
            "At the control-selected operating point the target does NOT clear the negative-panel "
            f"envelope by the pre-registered margin (95% lower bound {ci_low} against a bar of "
            f"{min_enrich}). No candidate list is emitted and no count here is a finding. This is "
            "the honest reading and it is publishable as it stands: every public human RNA-seq "
            "sample in this compilation was scored for the intragenic signature a 5'-truncating "
            "rearrangement leaves, on an instrument whose positive controls fire and whose "
            "negative panel is held at the ceiling, and the target does not rise above what an "
            "ordinary gene does.")
    out["⚠ what_a_candidate_is"] = (
        "a public sample in which this gene's downstream junction coverage is substantial while its "
        "5'-most junctions carry essentially none. That is CONSISTENT WITH a 5'-truncating "
        "rearrangement and is not one: an alternative promoter, 3' bias in a degraded library, or a "
        "poorly annotated 5' end produce the same pattern. It is a candidate list for orthogonal "
        "checking, never a detection and never a diagnosis.")
    return out


def _envelope_comparison(rows, dep, target, min_expected):
    """⭐ THE WEAKER QUESTION, ASKED OF EVERY CELL — AND THE ONE THE DATA CAN ACTUALLY ANSWER.

    The operating point asks whether the target clears the ordinary-gene envelope by a
    pre-registered margin, and pays for that sharpness with a pool small enough that a zero means
    nothing. This asks only whether the target's rate EXCEEDS the envelope at all — a question that
    stays answerable at the loose cells, where the target still has every sample it has.

    ⚠ It is not a substitute for the operating point and it is not a detection test. A target that
    never exceeds what an ordinary gene does has produced no signal ABOVE BACKGROUND; that bounds
    the signature's reach over this index, and it bounds nothing about the disease.
    """
    out = {"target": target, "n_cells_compared": 0, "n_cells_target_exceeds_envelope": 0,
           "exceedances": [],
           "_what": ("does the target's candidate rate EXCEED the ordinary-gene envelope at any "
                     "cell at all — a weaker question than the operating point's, and one that "
                     "stays answerable at the loose cells where the target still has every sample "
                     "it has. It is not a detection test: a target that never exceeds what an "
                     "ordinary gene does has produced no signal above background, which bounds "
                     "this signature's reach over this index and bounds nothing about the disease.")}
    best = None
    for r in rows:
        if r.get("neg_envelope_rate") is None:
            continue
        v = _cell_view(dep, r["cell"], r["track"])
        if not v.get("scoreable") or v.get("rate") is None or not v.get("n_pool"):
            continue
        out["n_cells_compared"] += 1
        if v["rate"] > r["neg_envelope_rate"]:
            out["n_cells_target_exceeds_envelope"] += 1
            out["exceedances"].append(
                {"cell": r["cell"], "track": r["track"], "target_rate": v["rate"],
                 "envelope_rate": r["neg_envelope_rate"], "envelope_gene": r["neg_envelope_gene"],
                 # ⚠ An envelope of exactly zero is a real exceedance with no finite ratio. It is
                 # recorded as one rather than divided into a crash or a fabricated number.
                 "ratio": (round(v["rate"] / r["neg_envelope_rate"], 4)
                           if r["neg_envelope_rate"] else None),
                 "envelope_is_zero": not r["neg_envelope_rate"],
                 "admissible": bool(r.get("admissible"))})
        # ⛔ THE BEST COMPARISON IS THE BEST-POWERED ONE, NOT THE MOST FLATTERING ONE. Ranking by
        # ratio would pick whichever cell happened to look most extreme; ranking by how many
        # background candidates the cell expects picks the one where a real excess would be
        # hardest to miss, and that choice is made without reading the target's count.
        expected = v["n_pool"] * r["neg_envelope_rate"]
        if best is None or expected > best[0]:
            best = (expected, r, v)
    # An exceedance over a zero envelope is the most extreme there is, so it sorts first.
    out["exceedances"] = sorted(
        out["exceedances"], key=lambda e: (0 if e["ratio"] is None else 1, -(e["ratio"] or 0)))[:10]
    if best:
        expected, r, v = best
        ci = _rate_ratio_ci(v["n_candidates"], v["n_pool"],
                            r["neg_envelope_candidates"], r["neg_envelope_pool"])
        # ⛔ WHERE THE TARGET SITS INSIDE THE PANEL, NOT JUST WHETHER IT CLEARS THE TOP OF IT. The
        # envelope is a MAXIMUM over several genes, so "does not exceed the envelope" can be true
        # of a target sitting above most of the panel — and reporting only the envelope would let
        # that read as though the target were quiet. The rank and the median are recorded so the
        # weaker claim cannot be mistaken for the stronger one.
        panel = sorted((r.get("neg_panel_rates") or {}).items(), key=lambda kv: kv[1])
        rates = [x[1] for x in panel]
        med = (rates[len(rates) // 2] if len(rates) % 2
               else (rates[len(rates) // 2 - 1] + rates[len(rates) // 2]) / 2) if rates else None
        out["where_the_target_sits_in_the_panel"] = {
            "panel_rates_ascending": dict(panel),
            "panel_median_rate": med,
            "n_panel_genes_the_target_exceeds": sum(1 for x in rates if v["rate"] > x),
            "n_panel_genes": len(rates),
            "ratio_to_panel_median": (round(v["rate"] / med, 4) if med else None),
            "_what": ("the envelope is a MAXIMUM, so clearing it is a weaker bar than being quiet. "
                      "A target inside the ordinary-gene spread has produced no excess; a target "
                      "above most of the panel but under its top is inside that spread, not below "
                      "it, and this row is here so the two cannot be confused."),
        }
        out["most_powered_comparison"] = {
            "cell": r["cell"], "track": r["track"], "n_pool": v["n_pool"],
            "n_candidates": v["n_candidates"], "rate": v["rate"],
            "envelope_gene": r["neg_envelope_gene"], "envelope_rate": r["neg_envelope_rate"],
            "expected_from_background": round(expected, 1),
            "ratio_to_envelope": (round(v["rate"] / r["neg_envelope_rate"], 4)
                                  if r["neg_envelope_rate"] else None),
            "enrichment_ci": ci,
            "powered": bool(expected >= min_expected),
        }
    if not out["n_cells_compared"]:
        out["verdict"] = "NOT_COMPARABLE"
    elif out["n_cells_target_exceeds_envelope"]:
        out["verdict"] = "TARGET_EXCEEDS_THE_ORDINARY_GENE_ENVELOPE_SOMEWHERE"
    else:
        out["verdict"] = "TARGET_NEVER_EXCEEDS_THE_ORDINARY_GENE_ENVELOPE"
    return out


def _select_operating_point(admissible):
    """⛔ CONTROLS ONLY. This function never sees a target gene: it is handed rows that already
    carry the positive-control and negative-panel numbers and nothing else, and it returns one of
    them. Keeping the selection in its own function with its own inputs is what makes the
    "the target did not choose its own threshold" claim checkable rather than asserted."""
    def rank(r):
        best = r.get("positive_best") or {}
        return (-(best.get("enrichment") or 0.0), -(best.get("n_candidates") or 0),
                r["cell"], GRID_TRACKS.index(r["track"]) if r["track"] in GRID_TRACKS else 99)
    return sorted(admissible, key=rank)[0]


def _target_headline(arm1):
    """⛔ THE HEADLINE LEADS WITH WHATEVER THE RUN CAN ACTUALLY SUPPORT, and never carries a
    candidate count a verdict withheld. The first search run's number went straight into a memo as
    though it were a finding; a headline that prints a count beside a verdict saying the count is
    background is how that happens."""
    tv = arm1.get("target_verdict")
    op = arm1.get("operating_point") or {}
    where = f"{op.get('cell')} [{op.get('track')}]" if op else "no operating point"
    tgt = arm1.get("target")
    if tv == "TARGET_SEPARATES":
        return (f"junction search: {tgt} SEPARATES at {where} (95% lower bound "
                f"{arm1.get('target_enrichment_ci_low')}x over the ordinary-gene envelope)")
    if tv == "TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT":
        pw = arm1.get("target_power_at_operating_point") or {}
        return (f"junction search ran; the specific regime leaves {tgt} only {pw.get('n_pool')} "
                f"samples, too few to answer at {where} — " + _envelope_headline(arm1))
    return (f"junction search ran and {tgt} does not separate from the ordinary-gene envelope at "
            f"{where}; no candidate list")


def _envelope_headline(arm1):
    ec = arm1.get("envelope_comparison") or {}
    if not ec:
        return "target counts withheld"
    mp = ec.get("most_powered_comparison") or {}
    if ec.get("verdict") == "TARGET_NEVER_EXCEEDS_THE_ORDINARY_GENE_ENVELOPE":
        return (f"{ec.get('target')} does not exceed the ordinary-gene envelope at any of "
                f"{ec.get('n_cells_compared')} comparable cells (best-powered: "
                f"{mp.get('ratio_to_envelope')}x on {mp.get('n_pool')} samples)")
    return (f"{ec.get('target')} exceeds the ordinary-gene envelope at "
            f"{ec.get('n_cells_target_exceeds_envelope')} of {ec.get('n_cells_compared')} cells")


def _headline(arm1, arm2):
    bits = []
    v1 = arm1.get("verdict")
    if v1 == "SEARCHED":
        # ⛔ THE HEADLINE NEVER CARRIES A CANDIDATE COUNT THE TARGET VERDICT WITHHELD. The first
        # search run's number went straight into a memo as though it were a finding; a headline
        # that prints a count next to a verdict saying the count is background is how that happens.
        bits.append(_target_headline(arm1))
    elif v1 == "NO_SPECIFIC_REGIME":
        bits.append("junction search: no grid cell holds the negative panel at the ceiling while a "
                    "positive control survives; " + _envelope_headline(arm1))
    elif v1 == "PROBED_NOT_SEARCHED":
        bits.append(f"junction index answers ({arm1.get('compilation_used')}); no fusion search run yet")
    elif v1:
        bits.append(f"junction index: {v1}")
    v2 = arm2.get("verdict")
    if v2 == "EMC_SAMPLES_PRESENT_IN_A_PROSE_INVISIBLE_DEPOSIT":
        bits.append(f"{arm2.get('n_samples_naming_emc')} EMC-naming samples in {arm2.get('series')}")
    elif v2 == "EMC_IN_THE_PUBLISHED_TABLE_NOT_IN_THE_DEPOSIT_LABELS":
        bits.append(f"{arm2.get('series')}: labels are in the paper, not the deposit — "
                    f"{arm2.get('supplementary_emc_rows')} EMC row(s) found")
    elif v2 == "EMC_LABELLED_IN_AN_EBI_DEPOSIT":
        hits = [f"{d['accession']} n={d['n_emc_samples']}"
                for d in (arm2.get("ebi_deposits") or []) if d.get("n_emc_samples")]
        bits.append("EMC named in a labelled EBI deposit: " + ", ".join(hits))
    elif v2 == "NO_EMC_IN_A_COMPLETE_EBI_CENSUS_LABELS_FOR_THE_GEO_SERIES_STILL_UNLOCATED":
        n = sum(1 for d in (arm2.get("ebi_deposits") or []) if d.get("census_complete"))
        bits.append(f"{n} EBI deposit(s) enumerated completely, none names EMC; "
                    f"{arm2.get('series')} labels still unlocated")
    elif v2:
        bits.append(f"{arm2.get('series')}: {v2}")
    return "; ".join(bits) if bits else "nothing run"


# ────────────────────────────────────────────────────────────────────────────────────────────────
# SELFTEST — the guards, asserted offline, BEFORE one byte is fetched
# ────────────────────────────────────────────────────────────────────────────────────────────────

def selftest():
    fails = []

    def ck(cond, msg):
        if not cond:
            fails.append(msg)

    # 1 · An empty cache may never emit a biological verdict.
    empty = derive({})
    ck(empty["arms"]["snaptron_junction_index"]["verdict"] == "NOT_RUN",
       "an empty cache produced a snaptron verdict other than NOT_RUN")
    ck(empty["arms"]["pan_sarcoma_methylation_deposit"]["verdict"] == "NOT_RUN",
       "an empty cache produced a methylation verdict other than NOT_RUN")

    # 2 · A failed transport control WITHHOLDS the target counts rather than reporting them.
    broken = {"snaptron": {"arm_state": "FETCHED", "compilation_used": "srav3h",
                           "compilations_that_answered": ["srav3h"],
                           "controls": {"transport": {"shape": {"n_records": 0, "columns": []}},
                                        "absent": {"shape": {"n_records": 0}}},
                           "queries": {"NR4A3": {"fetch": {"http": 200},
                                                 "shape": {"n_records": 999,
                                                           "chromosomes": {"chr9": 999}}}}}}
    d = derive(broken)["arms"]["snaptron_junction_index"]
    ck(d["verdict"] == "TRANSPORT_FAILED",
       "a dead transport control did not produce TRANSPORT_FAILED")
    ck(d["controls_pass"] is False, "controls_pass was true with zero transport records")

    # 3 · An absent control that RETURNS records also fails the arm.
    leaky = json.loads(json.dumps(broken))
    leaky["snaptron"]["controls"]["transport"]["shape"]["n_records"] = 500
    leaky["snaptron"]["controls"]["absent"]["shape"]["n_records"] = 7
    ck(derive(leaky)["arms"]["snaptron_junction_index"]["verdict"] == "TRANSPORT_FAILED",
       "an absent control returning records did not fail the arm")

    # 4 · ⛔ CLEAN TRANSPORT CONTROLS ARE NOT ENOUGH TO REPORT A TARGET, and this is the guard that
    #     stops the two control layers being confused. The transport pair only proves the ENDPOINT
    #     answers. Whether the SEARCH can see the signature is a separate question with its own
    #     control, so a fetch that answered cleanly but carries no depletion payload must still
    #     withhold every target count.
    clean = json.loads(json.dumps(broken))
    clean["snaptron"]["controls"]["transport"]["shape"]["n_records"] = 500
    clean["snaptron"]["controls"]["absent"]["shape"]["n_records"] = 0
    a4 = derive(clean)["arms"]["snaptron_junction_index"]
    ck(a4["verdict"] == "SIGNATURE_NOT_DEMONSTRATED",
       f"clean transport controls alone gave {a4['verdict']}; the search control must still gate")
    ck("nr4a3_candidates" not in a4,
       "a target count was reported on transport controls alone")

    # 5 · A series header with NO sample records is SAMPLE_LEVEL_NOT_READ, never "no EMC".
    hdr_only = {"methylation": {"arm_state": "FETCHED",
                                "geo_self_text": "!Series_title = Sarcoma classification\n",
                                "geo_all_text": "", "fetches": {}}}
    ck(derive(hdr_only)["arms"]["pan_sarcoma_methylation_deposit"]["verdict"]
       == "SAMPLE_LEVEL_NOT_READ",
       "a header-only read reported a sample-level answer")

    # 6 · The confusable term must NOT be counted as EMC.
    only_skeletal = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                                     "geo_all_text": ("^SAMPLE = GSM1\n!Sample_title = "
                                                      "skeletal myxoid chondrosarcoma case 1\n"),
                                     "fetches": {}}}
    a = derive(only_skeletal)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a["n_samples_naming_a_confusable"] == 1,
       "the skeletal confusable was not counted in its own bucket")
    # ⚠ STRENGTHENED (see `_bucket`). This used to assert that the skeletal sample ALSO appeared in
    # the EMC bucket — the two buckets overlapped and were reported side by side so a reader could
    # see the collision. That was the honest treatment while the matcher could not tell the two
    # tumours apart. It now can, so the stronger property is asserted instead: the skeletal tumour
    # is counted in its own bucket and is NOT counted as EMC. A deposit of skeletal cases must
    # never contribute one sample to an EMC count.
    ck(a["n_samples_naming_emc"] == 0,
       "the SKELETAL tumour was counted as extraskeletal myxoid chondrosarcoma")
    ck(a["emc_samples_sample"] == {},
       "a skeletal-only deposit still listed an EMC sample")

    # 7 · The sample splitter must key on GSM and not merge records.
    two = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                           "geo_all_text": ("^SAMPLE = GSM1\n!Sample_title = extraskeletal myxoid "
                                            "chondrosarcoma\n^SAMPLE = GSM2\n!Sample_title = "
                                            "leiomyosarcoma\n"),
                           "fetches": {}}}
    a2 = derive(two)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a2["n_samples_read"] == 2, f"splitter read {a2['n_samples_read']} samples, expected 2")
    ck(a2["n_samples_naming_emc"] == 1,
       f"EMC count was {a2['n_samples_naming_emc']}, expected 1")

    # 8 · The Snaptron TSV parser must not invent columns it was not served.
    shape = parse_snaptron("DataSource:Type\tsnaptron_id\tchromosome\tstart\tend\n"
                           "srav3h:I\t1\tchr9\t100\t200\n"
                           "srav3h:I\t2\tchr9\t300\t400\n")
    ck(shape["n_records"] == 2, "parser miscounted records")
    ck(shape["has_chromosome_column"] is True, "parser lost a served column")
    ck(shape["has_samples_count_column"] is False,
       "parser reported a column it was never served")
    ck(shape["chromosomes"] == {"chr9": 2}, f"chromosome tally wrong: {shape['chromosomes']}")

    # 9 · THE CONTROL LADDER OVER THE GRID. Each rung withholds the target for a different reason.
    REF = cell_key(*REFERENCE_CELL)
    TIGHT = cell_key(500, 0.50, 0.0, 0.90)
    PANEL = ["GAPDH", "ACTB", "RPL13A", "PGK1"]

    def _gene(cells):
        """One gene's cached depletion block. `cells` maps a cell key to (n_candidates, n_pool),
        or to None for a cell the 5'-support filter left unscoreable."""
        d = {"usable": True, "why": None, "strand_derived": "+", "n_annotated_junctions": 40,
             "five_prime_support_fraction": [0.9, 0.8, 0.05], "reference_cell": REF, "cells": {}}
        for k, v in cells.items():
            if v is None:
                d["cells"][k] = {"scoreable": False, "n_five_prime_junctions_used": 1,
                                 "why": "the 5'-support filter leaves 1 of 3 5' junctions"}
                continue
            c, n = v
            rate = round(c / n, 6) if n else None
            d["cells"][k] = {
                "scoreable": True, "n_five_prime_junctions_used": 3,
                "n_samples_expressing_downstream": n, "n_pool": n, "n_candidates": c,
                "candidate_rate": rate, "breakpoint_rank_hist": {},
                "breakpoint_rank_concentration": None, "promiscuity_tracked": True,
                "n_candidates_promiscuity_filtered": c,
                "candidate_rate_promiscuity_filtered": rate}
        return d

    def _snap(genes, panel=PANEL, tracks=("raw",)):
        return {"snaptron": {
            "arm_state": "FETCHED", "compilation_used": "srav3h",
            "compilations_that_answered": ["srav3h"],
            "signature_positives": ["FLI1", "ERG"], "signature_negative_panel": list(panel),
            "signature_negative": "GAPDH", "targets": ["NR4A3"], "context_genes": [],
            "grid_tracks": list(tracks),
            "thresholds": {"neg_panel_rate_ceiling": 0.005,
                           "min_positive_control_candidates": 30,
                           "min_neg_panel_genes_scoreable": 4,
                           "target_min_enrichment": 3.0, "reference_cell": REF},
            "controls": {"transport": {"shape": {"n_records": 500, "columns": []}},
                         "absent": {"shape": {"n_records": 0}}},
            "queries": {g: {"fetch": {"http": 200}, "shape": {"n_records": 9}, "depletion": d}
                        for g, d in genes.items()}}}

    def _scene(pos=(400, 200), tgt=(12, 2000), panel_tight=20, panel=PANEL, pos_pool=4000,
               **extra):
        """The standard fixture: at REF the panel is hot (0.025, over the ceiling) and at TIGHT it
        is quiet (0.002, under it). Only TIGHT can therefore ever be an operating point."""
        genes = {g: _gene({REF: (250, 10000), TIGHT: (panel_tight, 10000)}) for g in panel}
        genes["FLI1"] = _gene({REF: (1200, 10000), TIGHT: (pos[0], pos_pool)})
        genes["ERG"] = _gene({REF: (900, 10000), TIGHT: (pos[1], pos_pool)})
        genes["NR4A3"] = _gene({REF: (480, 10000), TIGHT: tgt})
        genes.update(extra)
        return _snap(genes, panel=panel)

    def arm1(inp):
        return derive(inp)["arms"]["snaptron_junction_index"]

    dead = _scene()
    for g in ("FLI1", "ERG"):
        for c in dead["snaptron"]["queries"][g]["depletion"]["cells"].values():
            c["n_candidates"], c["candidate_rate"] = 0, 0.0
            c["n_candidates_promiscuity_filtered"] = 0
            c["candidate_rate_promiscuity_filtered"] = 0.0
    a = arm1(dead)
    ck(a["verdict"] == "SIGNATURE_NOT_DEMONSTRATED",
       f"positive controls with zero candidates everywhere gave {a['verdict']}")
    ck("nr4a3_candidates" not in a, "target counts were reported despite dead positive controls")

    unusable = _scene()
    for g in ("FLI1", "ERG"):
        unusable["snaptron"]["queries"][g]["depletion"] = {
            "usable": False, "why": "too few annotated junctions"}
    a = arm1(unusable)
    ck(a["verdict"] == "SIGNATURE_NOT_DEMONSTRATED",
       "unscoreable positive controls did not withhold the target")

    # The first run's SPECIFICITY_NOT_DEMONSTRATED, now per cell: an ordinary gene firing as often
    # as a known 5'-truncated one means the score is measuring depth, not truncation.
    hot = _scene(panel_tight=2000)          # panel at 0.20 everywhere, far over the ceiling
    a = arm1(hot)
    ck(a["verdict"] == "NO_SPECIFIC_REGIME",
       f"a negative panel firing above the positives gave {a['verdict']}")
    ck("nr4a3_candidates" not in a, "target counts survived a failed specificity check")
    ck(bool(a.get("closest_cells")), "NO_SPECIFIC_REGIME reported no nearest misses to read")

    # Under the ceiling but the positive control does not clear the envelope: still no regime.
    # 45/10000 = 0.0045 is under the 0.005 ceiling, and 30/20000 = 0.0015 puts both positive
    # controls BELOW that envelope while still clearing the 30-candidate floor.
    a = arm1(_scene(pos=(30, 30), pos_pool=20000, panel_tight=45))
    ck(a["verdict"] == "NO_SPECIFIC_REGIME",
       f"a positive control below the negative envelope gave {a['verdict']}")

    # Too few panel genes scoreable at the only quiet cell -> that cell cannot be an operating point.
    thin = _scene()
    for g in PANEL[:2]:
        thin["snaptron"]["queries"][g]["depletion"]["cells"][TIGHT] = {
            "scoreable": False, "why": "unscoreable in this fixture"}
    a = arm1(thin)
    ck(a["verdict"] == "NO_SPECIFIC_REGIME",
       f"an envelope over 2 panel genes was accepted; got {a['verdict']}")

    # A quiet panel is not enough: a cell where the positive control has been tightened down to
    # almost nothing proves nothing about specificity, because a handful of survivors is consistent
    # with a threshold that has stopped detecting the signature at all.
    # ⚠ The positive control here still fires at FIVE TIMES the envelope (0.01 against 0.002), so
    # the per-cell specificity check passes and the candidate floor is the only thing left to
    # refuse the cell. A fixture where the rate also failed would not test this rung at all.
    a = arm1(_scene(pos=(5, 5), pos_pool=500))
    ck(a["verdict"] == "NO_SPECIFIC_REGIME",
       f"a cell keeping 5 positive-control candidates was accepted as an operating point; "
       f"got {a['verdict']}")
    tightest = [r for r in a["grid"] if r["cell"] == TIGHT and r["track"] == "raw"][0]
    ck("below the 30 floor" in (tightest.get("why_not") or ""),
       f"the cell was refused for the wrong reason: {tightest.get('why_not')}")

    weak = arm1(_scene(tgt=(12, 2000)))      # 0.006 against an envelope of 0.002 -> ratio 3.0
    ck(weak["verdict"] == "SEARCHED", f"clean controls gave {weak['verdict']}")
    ck(weak["target_verdict"] == "TARGET_DOES_NOT_SEPARATE",
       f"a target at ~3x the envelope was called {weak['target_verdict']}")
    ck("nr4a3_candidates" not in weak,
       "a candidate count was published under TARGET_DOES_NOT_SEPARATE")

    strong = arm1(_scene(tgt=(200, 2000)))   # 0.10 against 0.002 -> ratio 50
    ck(strong["target_verdict"] == "TARGET_SEPARATES",
       f"a target at 50x the envelope was called {strong['target_verdict']}")
    ck(strong["nr4a3_candidates"] == 200,
       f"target count was {strong.get('nr4a3_candidates')}, expected 200")
    ck(strong["at_operating_point"]["NR4A3"]["excess_over_background"] == 196.0,
       "the background-subtracted excess was lost or miscomputed")

    # ⛔ A cache from before the grid must say so, not impersonate a dead positive control.
    old_cache = _scene()
    old_cache["snaptron"]["queries"]["FLI1"]["depletion"] = {
        "usable": True, "n_candidates": 11973, "candidate_rate": 0.11539}
    a = arm1(old_cache)
    ck(a["verdict"] == "CACHE_PREDATES_THE_GRID_SCORER",
       f"a pre-grid cache gave {a['verdict']}, which reads as a biological result")
    ck("nr4a3_candidates" not in a, "a pre-grid cache still reported a target count")

    # 10 · ⛔⛔ THE OPERATING POINT IS CHOSEN ON THE CONTROLS ALONE. This is the guard that stops a
    #      swept grid from becoming a fishing expedition: the same controls must select the same
    #      cell whatever the target does, including a target rigged to look perfect somewhere else.
    rigged = _scene(tgt=(0, 2000))
    rigged["snaptron"]["queries"]["NR4A3"]["depletion"]["cells"][REF] = {
        "scoreable": True, "n_five_prime_junctions_used": 3,
        "n_samples_expressing_downstream": 10000, "n_pool": 10000, "n_candidates": 9999,
        "candidate_rate": 0.9999, "breakpoint_rank_hist": {}, "promiscuity_tracked": True,
        "breakpoint_rank_concentration": None, "n_candidates_promiscuity_filtered": 9999,
        "candidate_rate_promiscuity_filtered": 0.9999}
    a = arm1(rigged)
    ck(a["operating_point"]["cell"] == weak["operating_point"]["cell"]
       and a["operating_point"]["track"] == weak["operating_point"]["track"],
       "the target's own numbers moved the operating point — the selection is not control-only")
    ck(a["operating_point"]["cell"] == TIGHT,
       f"the operating point was {a['operating_point']['cell']}, expected the quiet cell")
    ck(a["target_verdict"] == "TARGET_DOES_NOT_SEPARATE",
       "a target rigged to look perfect at an inadmissible cell was still reported")

    # 11 · THE ENVELOPE IS THE MAX OVER THE PANEL, NOT THE NAMED NEGATIVE CONTROL. One negative gene
    #      gives one number and no idea of its spread, which is how ~1.9x over GAPDH got mistaken
    #      for a signal in the first place.
    spread = _scene(tgt=(200, 2000))
    spread["snaptron"]["queries"]["RPL13A"]["depletion"]["cells"][TIGHT].update(
        {"n_candidates": 45, "candidate_rate": 0.0045,
         "n_candidates_promiscuity_filtered": 45, "candidate_rate_promiscuity_filtered": 0.0045})
    a = arm1(spread)
    ck(a["operating_point"]["neg_envelope_gene"] == "RPL13A",
       f"the envelope was taken from {a['operating_point'].get('neg_envelope_gene')}, not the "
       "hottest panel gene")
    ck(a["at_operating_point"]["NR4A3"]["enrichment_over_negative_envelope"]["ratio"]
       < strong["at_operating_point"]["NR4A3"]["enrichment_over_negative_envelope"]["ratio"],
       "a hotter panel gene did not lower the target's enrichment")

    # 12 · The rate-ratio interval, including the branch where the negative side produced nothing.
    ci = _rate_ratio_ci(200, 2000, 20, 10000)
    ck(abs(ci["ratio"] - 50.0) < 1e-9, f"rate ratio was {ci['ratio']}, expected 50")
    ck(ci["ci_low"] < 50.0 < ci["ci_high"], "the interval does not contain its own point estimate")
    z = _rate_ratio_ci(200, 2000, 0, 10000)
    ck(z["ratio"] is None and z["ci_low"] is not None,
       "a zero negative side did not fall back to a rule-of-three lower bound")
    ck(abs(z["ci_low"] - (0.1 / 0.0003)) < 1e-3,
       f"rule-of-three lower bound was {z['ci_low']}, expected 0.1/(3/10000)")
    ck(_rate_ratio_ci(0, 2000, 20, 10000)["ratio"] is None,
       "a zero numerator produced a ratio instead of a refusal")

    # 13 · GRID GEOMETRY. Keys must be stable under equivalent numeric spellings, or a cell written
    #      by the fetch and looked up by derive silently misses.
    ck(cell_key(20, 0.0, 0.02, 0.0) == cell_key(20.0, 0, 0.0200, 0),
       "cell keys disagree on equivalent numeric spellings")
    ck(len(list(grid_cells())) ==
       len(GRID_MIN_DOWNSTREAM_COVERAGE) * len(GRID_FIVE_PRIME_MIN_SUPPORT)
       * len(GRID_MAX_FIVE_PRIME_SHARE) * len(GRID_MIN_EXPRESSION_PERCENTILE),
       "the grid enumerator does not cover the cartesian product")

    # 14 · 5'-depletion arithmetic, including the strand inversion that would silently flip it.
    hdr = ("DataSource:Type\tsnaptron_id\tchromosome\tstart\tend\tlength\tstrand\tannotated"
           "\tleft_motif\tright_motif\tleft_annotated\tright_annotated\tsamples\tsamples_count"
           "\tcoverage_sum\tcoverage_avg\tcoverage_median\tsource_dataset_id")

    def jrow(i, start, strand, samples):
        return (f"srav3h:I\t{i}\tchr9\t{start}\t{start+100}\t100\t{strand}\t1\tGT\tAG\t1\t1"
                f"\t{samples}\t1\t0\t0.0\t0\t0")

    def build(rows):
        return five_prime_depletion(hdr + "\n" + "\n".join(rows))

    # Nine annotated junctions on +. TRUNC carries coverage only on the three DOWNSTREAM-most.
    rows = [jrow(i, 1000 + 100 * i, "+",
                 ",NORMAL:50" + (",TRUNC:200" if i >= 6 else "")) for i in range(9)]
    d, ids = build(rows)
    ck(d["usable"] is True, f"depletion unusable: {d.get('why')}")
    ck(d["strand_derived"] == "+", "strand vote did not return +")
    ck(sorted(ids[REF]) == ["TRUNC"], f"expected only TRUNC as a candidate, got {sorted(ids[REF])}")

    # Same coverage pattern, minus strand: the "5' end" is now the OTHER end, so TRUNC — which
    # carries the HIGH coordinates — is no longer 5'-depleted. A strand bug would keep calling it.
    dm, idm = build([r.replace("\t+\t", "\t-\t") for r in rows])
    ck(dm["strand_derived"] == "-", "strand vote did not return -")
    ck(sorted(idm[REF]) == [],
       "a minus-strand gene still called the high-coordinate sample 5'-depleted — strand inverted")

    # A sample below the downstream-coverage floor must not be called: "no 5' coverage" and "barely
    # expressed" are the confound this floor exists to separate.
    faint = [jrow(i, 1000 + 100 * i, "+",
                  ",NORMAL:50" + (",FAINT:1" if i >= 6 else "")) for i in range(9)]
    df, idf = build(faint)
    ck(df["usable"] is True, f"the faint fixture was not scoreable: {df.get('why')}")
    ck(sorted(idf[REF]) == [], "a barely-expressed sample was called 5'-depleted")

    # Unannotated junctions must not enter the profile at all.
    du, _ = build([r.replace("\t1\tGT", "\t0\tGT") for r in rows])
    ck(du["usable"] is False, "unannotated junctions were admitted to the profile")

    # 15 · ⭐ LEVER 1 — the 5'-support filter, and the failure it must never produce. A 5' set the
    #      filter empties would give every sample a 5' share of zero and call the whole compilation
    #      depleted. The cell must come back NOT MEASURED, with a reason, never as zero candidates.
    many = [f"S{i}" for i in range(20)]
    sup_rows = []
    for i in range(9):
        toks = []
        if i >= 2:                                   # ranks 2..8 carried by everyone
            toks += [f"{s}:50" for s in many]
        if i < 2:                                    # ranks 0,1 carried by ONE sample only
            toks.append("S0:50")
        if i >= 6:                                   # a truly 5'-truncated sample
            toks.append("TRUNC:200")
        sup_rows.append(jrow(i, 1000 + 100 * i, "+", "," + ",".join(toks)))
    ds, idsup = build(sup_rows)
    ck(ds["usable"] is True, f"support fixture unusable: {ds.get('why')}")
    ck(sorted(idsup[REF]) == ["TRUNC"],
       f"at zero support the truncated sample was not recovered: {sorted(idsup[REF])}")
    tight_sup = ds["cells"][cell_key(20, 0.50, 0.02, 0.0)]
    ck(tight_sup["scoreable"] is False,
       "a 5' set emptied by the support filter was scored instead of refused")
    ck("n_candidates" not in tight_sup,
       "an unscoreable cell still reported a candidate count, which reads as a clean zero")
    ck(tight_sup["n_five_prime_junctions_used"] < MIN_FIVE_PRIME_JUNCTIONS_REQUIRED,
       "the unscoreable cell did not record how few 5' junctions survived")
    ck(ds["five_prime_support_fraction"][0] < 0.1 <= ds["five_prime_support_fraction"][2],
       f"5' support fractions look wrong: {ds['five_prime_support_fraction']}")

    # ⚠ SUPPORT IS COUNTED OVER THE GENE'S OWN EXPRESSING SAMPLES. Here a 5' junction is carried by
    # a hundred samples that have NO downstream coverage at all — they do not express the gene, so
    # that junction's support among expressing samples is zero and the lever must drop it. Counting
    # over every sample in the compilation instead gives a "fraction" of ten, and a junction nobody
    # who expresses the gene actually uses would sail through the filter as its best-supported one.
    ghost_rows = []
    for i in range(9):
        toks = []
        if i == 0:
            toks += [f"G{j}:50" for j in range(100)]      # carried ONLY by non-expressers
        if 1 <= i <= 2:
            toks += [f"E{j}:50" for j in range(10)]
        if i >= 3:
            toks += [f"E{j}:50" for j in range(10)]
        ghost_rows.append(jrow(i, 1000 + 100 * i, "+", "," + ",".join(toks)))
    dg, _ = build(ghost_rows)
    ck(dg["n_samples_expressing_at_base_floor"] == 10,
       f"the ghost fixture should have 10 expressing samples, got "
       f"{dg['n_samples_expressing_at_base_floor']}")
    ck(dg["five_prime_support_fraction"][0] == 0.0,
       f"a 5' junction carried only by NON-expressing samples reported support "
       f"{dg['five_prime_support_fraction'][0]}; the denominator is not the expressing set")
    ck(dg["cells"][cell_key(20, 0.10, 0.02, 0.0)]["n_five_prime_junctions_used"] == 2,
       "the unsupported 5' junction survived the support filter")

    # 16 · ⭐ LEVER 3 — the absolute-expression discriminator. A truncated but barely-expressed
    #      sample must fall out of the pool at a high percentile while a strongly-expressed one
    #      survives; that asymmetry is the whole point of the lever.
    pct_rows = []
    for i in range(9):
        toks = [f"N{j}:50" for j in range(18)]
        if i >= 3:
            toks += ["HI:500", "LO:5"]
        pct_rows.append(jrow(i, 1000 + 100 * i, "+", "," + ",".join(toks)))
    dp, idp = build(pct_rows)
    ck(sorted(idp[cell_key(20, 0.0, 0.02, 0.0)]) == ["HI", "LO"],
       f"at no percentile floor both truncated samples should be called: "
       f"{sorted(idp[cell_key(20, 0.0, 0.02, 0.0)])}")
    top = dp["cells"][cell_key(20, 0.0, 0.02, 0.90)]
    n_expr = top["n_samples_expressing_downstream"]
    ck(top["n_pool"] == n_expr - int(n_expr * 0.90) == 2,
       f"the top-decile pool was {top['n_pool']} of {n_expr}, expected 2")
    ck(sorted(idp[cell_key(20, 0.0, 0.02, 0.90)]) == ["HI"],
       "the weakly-expressed truncated sample survived the top-decile expression floor")

    # 17 · LEVER 2 and the grid's monotonicity. Tightening any axis may only ever remove candidates;
    #      a prefix bug in the sorted scan would show up here as a count that went UP.
    for sup in GRID_FIVE_PRIME_MIN_SUPPORT:
        for pct in GRID_MIN_EXPRESSION_PERCENTILE:
            got = []
            for mc in GRID_MIN_DOWNSTREAM_COVERAGE:
                row = [dp["cells"][cell_key(mc, sup, sh, pct)] for sh in (0.02, 0.005, 0.0)]
                if not all(c.get("scoreable") for c in row):
                    continue
                ns = [c["n_candidates"] for c in row]
                ck(ns[0] >= ns[1] >= ns[2],
                   f"tightening the 5' share raised the count at sup={sup} pct={pct}: {ns}")
                got.append(ns[0])
            ck(got == sorted(got, reverse=True),
               f"raising the downstream-coverage floor raised the count at sup={sup}: {got}")

    # 18 · ⭐ LEVER 4 — the promiscuity track, and the leave-one-out that keeps it honest.
    q4 = {"GAPDH": {"depletion": _gene({REF: (3, 100)})},
          "ACTB": {"depletion": _gene({REF: (3, 100)})},
          "NR4A3": {"depletion": _gene({REF: (4, 100)})}}
    ids4 = {"GAPDH": {REF: {"s1", "s2", "s3"}},
            "ACTB": {REF: {"s4", "s5", "s6"}},
            "NR4A3": {REF: {"s1", "s2", "s9", "s10"}}}
    untracked = apply_promiscuity_track(q4, ids4, ["GAPDH", "ACTB"])
    ck(untracked == [], f"nothing should have exceeded the id cap; got {untracked}")
    ck(q4["GAPDH"]["depletion"]["cells"][REF]["n_candidates_promiscuity_filtered"] == 3,
       "a panel gene was filtered against its OWN candidates and zeroed by construction")
    ck(q4["NR4A3"]["depletion"]["cells"][REF]["n_candidates_promiscuity_filtered"] == 2,
       "the target kept candidates that are also candidates at an ordinary gene")
    ck(q4["NR4A3"]["depletion"]["cells"][REF]["candidate_rate_promiscuity_filtered"] == 0.02,
       "the filtered rate did not keep the same denominator")
    # ⛔ THE MUTATION THAT `union - own` SURVIVES: every panel gene carrying the SAME candidates.
    #    Subtracting a gene's own set from the union empties it and exempts everybody; counting
    #    carriers correctly removes candidates that another panel gene also carries.
    q4b = {"GAPDH": {"depletion": _gene({REF: (3, 100)})},
           "ACTB": {"depletion": _gene({REF: (3, 100)})},
           "NR4A3": {"depletion": _gene({REF: (3, 100)})}}
    same = {"GAPDH": {REF: {"s1", "s2", "s3"}}, "ACTB": {REF: {"s1", "s2", "s3"}},
            "NR4A3": {REF: {"s1", "s2", "s3"}}}
    apply_promiscuity_track(q4b, same, ["GAPDH", "ACTB"])
    ck(q4b["GAPDH"]["depletion"]["cells"][REF]["n_candidates_promiscuity_filtered"] == 0,
       "a panel gene kept candidates that ANOTHER panel gene also carries — the leave-one-out is "
       "a subtraction from the union rather than a carrier count")
    ck(q4b["NR4A3"]["depletion"]["cells"][REF]["n_candidates_promiscuity_filtered"] == 0,
       "the target kept candidates every panel gene also carries")

    q5 = {"GAPDH": {"depletion": _gene({REF: (3, 100)})},
          "ACTB": {"depletion": _gene({REF: (3, 100)})}}
    ck(apply_promiscuity_track(q5, {"GAPDH": {REF: {"a"}}, "ACTB": {REF: {"b"}}},
                               ["GAPDH", "ACTB"], max_ids=1) == [REF],
       "a union past the id cap was not recorded as untracked")
    ck(q5["GAPDH"]["depletion"]["cells"][REF]["promiscuity_tracked"] is False,
       "an untracked cell was left looking tracked")

    # 19 · The breakpoint-rank concentration, which is a contrast statistic and must be None rather
    #      than a number when there is nothing to concentrate.
    ck(_concentration({"3": 8, "5": 2}) == 0.8, "concentration arithmetic is wrong")
    ck(_concentration({}) is None, "an empty histogram produced a concentration")
    ck(ds["cells"][REF]["breakpoint_rank_hist"] == {"6": 1},
       f"breakpoint rank was not read off the fixture: {ds['cells'][REF]['breakpoint_rank_hist']}")

    # 20 · The promiscuity TRACK must be selectable and must withhold where it was not tracked.
    tracked = _scene(tgt=(200, 2000))
    tracked["snaptron"]["grid_tracks"] = ["raw", "promiscuity_filtered"]
    for g in tracked["snaptron"]["queries"]:
        tracked["snaptron"]["queries"][g]["depletion"]["cells"][TIGHT]["promiscuity_tracked"] = False
    a = arm1(tracked)
    rows_f = [r for r in a["grid"] if r["track"] == "promiscuity_filtered" and r["cell"] == TIGHT]
    ck(rows_f and rows_f[0]["admissible"] is False,
       "an untracked promiscuity cell was still offered as an operating point")
    ck(a["operating_point"]["track"] == "raw",
       f"the selection fell to an untracked track: {a['operating_point']['track']}")

    # 21 · An unreadable supplement is never "no EMC".
    unread = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                              "geo_all_text": "^SAMPLE = GSM1\n!Sample_title = case 1\n",
                              "fetches": {},
                              "supplementary": {"u": {"parsed": {"readable": False,
                                                                 "why": "openpyxl unavailable"}}}}}
    a2 = derive(unread)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a2["verdict"] == "LABELS_NOT_LOCATED",
       f"an unreadable supplement gave {a2['verdict']}, expected LABELS_NOT_LOCATED")

    found = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                             "geo_all_text": "^SAMPLE = GSM1\n!Sample_title = case 1\n",
                             "fetches": {},
                             "supplementary": {"u": {"parsed": {
                                 "readable": True, "n_emc_rows": 3, "confusable_rows": 0,
                                 "emc_rows": ["case 12 | extraskeletal myxoid chondrosarcoma"]}}}}}
    a3 = derive(found)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a3["verdict"] == "EMC_IN_THE_PUBLISHED_TABLE_NOT_IN_THE_DEPOSIT_LABELS",
       f"a supplement naming EMC gave {a3['verdict']}")
    ck(a3["supplementary_emc_rows"] == 3, "supplementary EMC row count was lost")

    # 22 · ⭐ END TO END, WITH NO NETWORK. Synthetic Snaptron bodies driven through the REAL scorer,
    #      the REAL promiscuity track and the REAL `derive`. Every guard above tests one piece
    #      against a hand-built fixture; this one is the only thing that proves the pieces still
    #      fit together — a field the fetch writes and `derive` no longer reads is invisible to all
    #      of them and costs a whole CI run to discover.
    def synth(n_clean, truncated, shared):
        """One gene: `n_clean` ordinary samples, plus gene-specific and shared truncated ones."""
        rows = []
        for i in range(9):
            toks = [f"C{j}:50" for j in range(n_clean)]
            if i >= 6:
                toks += [f"{t}:200" for t in truncated] + [f"{b}:200" for b in shared]
            rows.append(jrow(i, 1000 + 100 * i, "+", "," + ",".join(toks)))
        return hdr + "\n" + "\n".join(rows)

    # `B*` are the same ids in every gene: the 3'-biased libraries lever 4 exists to notice.
    shared_bg = [f"B{i}" for i in range(5)]
    bodies = {g: synth(1000, [], shared_bg) for g in SNAPTRON_SIGNATURE_NEGATIVE_PANEL}
    for g in SNAPTRON_SIGNATURE_POSITIVES:
        bodies[g] = synth(1000, [f"{g}T{i}" for i in range(50)], shared_bg)
    for g in SNAPTRON_TARGETS + SNAPTRON_CONTEXT:
        bodies[g] = synth(1000, [f"{g}T{i}" for i in range(3)], shared_bg)

    e2e = {"queries": {},
           "controls": {"transport": {"shape": {"n_records": 500, "columns": []}},
                        "absent": {"shape": {"n_records": 0}}}}
    score_snaptron_bodies(e2e, lambda g: (bodies[g], {"http": 200}), pause=0)
    a = derive({"snaptron": e2e})["arms"]["snaptron_junction_index"]
    ck(a["verdict"] == "SEARCHED",
       f"the end-to-end chain gave {a['verdict']}: the fetch and derive halves disagree")
    ck(a["target_verdict"] in ("TARGET_SEPARATES", "TARGET_DOES_NOT_SEPARATE",
                               "TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT"),
       f"end-to-end target verdict was {a.get('target_verdict')}")
    ck(bool(a.get("envelope_comparison", {}).get("verdict")),
       "the end-to-end run carried no envelope comparison, so an underpowered operating point "
       "would leave nothing readable at all")
    ck(set(a["at_operating_point"]) == set(bodies),
       "a gene the fetch scored did not survive into the operating-point read")
    tcell = e2e["queries"][SNAPTRON_TARGETS[0]]["depletion"]["cells"][REF]
    ck(tcell["n_candidates"] == 8,
       f"the target should carry 3 own + 5 shared truncated samples, got {tcell['n_candidates']}")
    ck(tcell["n_candidates_promiscuity_filtered"] == 3,
       f"lever 4 did not remove the shared background: "
       f"{tcell['n_candidates_promiscuity_filtered']}")
    ncell = e2e["queries"][SNAPTRON_SIGNATURE_NEGATIVE_PANEL[0]]["depletion"]["cells"][REF]
    ck(ncell["n_candidates_promiscuity_filtered"] == 0,
       "a panel gene whose every candidate is shared with the rest of the panel kept them; the "
       "leave-one-out is exempting genes from background they demonstrably share")
    ck(a["id_space_check"]["shared_with_transport_control"] > 0,
       "the id-space check found no shared samples in a fixture that is entirely shared")

    # 23 · ⛔⛔ A ZERO IN A SMALL POOL IS AN ABSENT READING, NOT A READING OF ABSENCE. The tighter
    #      the regime the controls choose, the smaller the TARGET's pool gets too — and run
    #      32676239799 landed on a cell holding 219 target samples against an envelope of 0.0011,
    #      where even a real threefold enrichment expects under one candidate. Whatever the target
    #      returned there, that cell could not answer, and the verdict has to say so.
    # ⚠ ONE candidate, not zero — so this also shows the verdict turns on the POOL and not on the
    #   count: a rate of 1-in-60 is eight times the envelope here and still cannot be believed.
    thin_pool = _scene(tgt=(1, 60))          # 60 x 0.002 x 3 = 0.36 expected at the bar
    a = arm1(thin_pool)
    ck(a["target_verdict"] == "TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT",
       f"a target pool of 60 gave {a['target_verdict']}; nothing there excludes anything")
    ck("nr4a3_candidates" not in a, "a candidate count was published from an unanswerable cell")
    pw = a["target_power_at_operating_point"]
    ck(pw["powered"] is False and pw["pool_that_would_be_needed"] > 60,
       f"the power block did not say what pool was needed: {pw}")

    # ⛔ AND THE POWER CHECK READS THE POOL, NEVER THE COUNT. If it looked at what the target
    #    returned it would be one more way to let the answer choose its own threshold.
    b = arm1(_scene(tgt=(60, 60)))           # same pool, every sample a candidate
    ck(b["target_power_at_operating_point"]["powered"] is False,
       "the power verdict moved when only the target's COUNT changed")
    ck(b["operating_point"]["cell"] == a["operating_point"]["cell"],
       "the operating point moved when only the target's count changed")

    # A pool that IS big enough must go back to answering.
    ck(arm1(_scene(tgt=(12, 2000)))["target_verdict"] == "TARGET_DOES_NOT_SEPARATE",
       "an adequately powered cell was called underpowered")
    ck(arm1(_scene(tgt=(200, 2000)))["target_verdict"] == "TARGET_SEPARATES",
       "an adequately powered cell with a real effect stopped separating")

    # 24 · ⭐ THE WEAKER QUESTION, WHICH IS THE ONE THE DATA CAN ANSWER WHEN THE SHARP ONE CANNOT.
    ec = a["envelope_comparison"]
    ck(ec["verdict"] == "TARGET_EXCEEDS_THE_ORDINARY_GENE_ENVELOPE_SOMEWHERE",
       f"a target above the envelope at the loose cell gave {ec['verdict']}")
    # ⛔ THE BEST COMPARISON IS THE BEST-POWERED ONE, NOT THE MOST EXTREME ONE. In this fixture the
    #    tight cell carries the LARGER ratio (3.0 against 1.92) and the loose cell carries fifty
    #    times the expected background; ranking on ratio would report the flattering cell.
    mp = ec["most_powered_comparison"]
    ck(mp["cell"] == REF,
       f"the most-powered comparison was {mp['cell']}, not the cell with the most background to "
       "see an excess against")
    ck(mp["powered"] is True, "the loose cell was called underpowered")
    ck(mp["ratio_to_envelope"] < max(e["ratio"] for e in ec["exceedances"]),
       "the best-powered cell happens to also be the most extreme; the fixture is not testing "
       "what it claims to test")

    # ⛔ "DOES NOT EXCEED THE ENVELOPE" IS NOT "IS QUIET". The envelope is a maximum, so a target
    #    sitting above most of the panel still clears the test — and the artifact has to say so, or
    #    the weaker claim reads as the stronger one.
    where = ec["where_the_target_sits_in_the_panel"]
    ck(where["n_panel_genes"] == len(PANEL),
       f"the panel-position row saw {where['n_panel_genes']} genes, expected {len(PANEL)}")
    ck(where["n_panel_genes_the_target_exceeds"] == len(PANEL),
       "a target above every panel gene was not recorded as such")
    ck(where["ratio_to_panel_median"] > 1.0,
       f"ratio to the panel median came back {where['ratio_to_panel_median']} for a target above "
       "every panel gene")

    quiet = _scene(tgt=(1, 10000))
    quiet["snaptron"]["queries"]["NR4A3"]["depletion"]["cells"][REF].update(
        {"n_candidates": 1, "candidate_rate": 0.0001,
         "n_candidates_promiscuity_filtered": 1, "candidate_rate_promiscuity_filtered": 0.0001})
    ec2 = arm1(quiet)["envelope_comparison"]
    ck(ec2["verdict"] == "TARGET_NEVER_EXCEEDS_THE_ORDINARY_GENE_ENVELOPE",
       f"a target below the envelope everywhere gave {ec2['verdict']}")
    ck(ec2["n_cells_target_exceeds_envelope"] == 0 and ec2["n_cells_compared"] > 0,
       f"exceedance tally wrong: {ec2['n_cells_compared']} compared, "
       f"{ec2['n_cells_target_exceeds_envelope']} exceeding")

    # ⛔ AND IT MUST SURVIVE A RUN WITH NO ADMISSIBLE CELL AT ALL, which is exactly when a reader
    #    would otherwise be left with nothing but "no regime".
    a = arm1(_scene(panel_tight=2000))
    ck(a["verdict"] == "NO_SPECIFIC_REGIME" and a.get("envelope_comparison"),
       "a run with no specific regime carried no envelope comparison to read")

    # 25 · ⛔ THE BUCKETS ARE EXCLUSIVE AND EMC WINS, because `chondrosarcoma` is a SUBSTRING of
    # `extraskeletal myxoid chondrosarcoma`. Order the test the other way round and every real EMC
    # label is filed under the skeletal tumour and the deposit reports zero — the single mutation
    # that would turn a positive cohort into a negative without any other symptom.
    ck(_bucket("Extraskeletal myxoid chondrosarcoma") == "emc",
       "the disease itself was not bucketed as EMC")
    ck(_bucket("extraskeletal myxoid chondrosarcoma (EMC)") == "emc",
       "a parenthesised EMC label was misbucketed")
    ck(_bucket("Chondrosarcoma") == "confusable",
       "a bare skeletal chondrosarcoma label was not bucketed as confusable")
    ck(_bucket("Chondroblastoma") == "confusable", "chondroblastoma was not bucketed as confusable")
    ck(_bucket("Osteosarcoma") is None, "an unrelated sarcoma was bucketed as something")
    ck(_bucket("EWSR1::NR4A3 fusion positive") == "emc", "a fusion label was not bucketed as EMC")

    # ⛔ THE PAIR, ASSERTED TOGETHER. These two lines fail under OPPOSITE single mutations of
    # `_bucket`: drop the left word-boundary anchor and the first one flips to "confusable";
    # reverse the longest-match tie-break and the second flips to "emc". Testing either alone
    # leaves the other defect free to ship, which is the whole reason they are adjacent here.
    ck(_bucket("extraskeletal myxoid chondrosarcoma, grade 2") == "emc",
       "a real EMC label was demoted to the skeletal bucket")
    ck(_bucket("skeletal myxoid chondrosarcoma of the femur") == "confusable",
       "a SKELETAL label was promoted into the EMC bucket")
    # ⚠ And the LEFT ANCHOR, guarded for what it actually does rather than what it looked like it
    # did: it stops a term matching mid-word. `osteochondrosarcoma` is the one label out of 65
    # tested on which anchored and unanchored matching disagree.
    ck(_bucket("osteochondrosarcoma") is None,
       "a mid-word substring hit swept an unrelated compound into a disease bucket")

    # 26 · ⛔ A CENSUS THAT DOES NOT SUM TO ITS OWN DECLARED SAMPLE COUNT MAY NOT PRODUCE A
    # NEGATIVE. This is the guard that decides whether a zero is "no EMC in this deposit" or "no EMC
    # in the part we happened to read", and it is pure offline arithmetic.
    def _ebi(cats, declared, truncated=False):
        body = {"attributes": [{"name": "ReleaseDate", "value": "2021-05-01"}],
                "section": {"attributes": [{"name": "Title", "value": "sarcoma methylation"}],
                            "subsections": [[{"type": "Samples",
                                              "attributes": [{"name": "Sample count",
                                                              "value": str(declared)}],
                                              "subsections": [
                                                  {"accno": f"factors_{i}", "type": "Factors Table",
                                                   "attributes": [
                                                       {"name": "disease", "value": dz},
                                                       {"name": "No. of Samples", "value": str(n),
                                                        "valqual": [{"name": "search",
                                                                     "value": '"A_Grn.idat" OR "A_Red.idat"'}]}]}
                                                  for i, (dz, n) in enumerate(cats)]}]]}}
        return _parse_biostudies("E-TEST-1", json.dumps(body), truncated)

    complete = _ebi([("Osteosarcoma", 60), ("Chondrosarcoma", 40)], 100)
    ck(complete["census_complete"] is True,
       f"a census summing to its declared count was not complete: {complete['census_sum']}/100")
    ck(complete["n_emc_samples"] == 0, "an all-confusable census reported EMC samples")
    ck(complete["n_confusable_samples"] == 40,
       f"skeletal chondrosarcoma was not counted as confusable ({complete['n_confusable_samples']})")

    short = _ebi([("Osteosarcoma", 60), ("Chondrosarcoma", 30)], 100)
    ck(short["census_complete"] is False, "a census 10 samples short of its own count read complete")

    # ⛔ AND THE VERDICT MUST FOLLOW IT. Same zero, two different meanings.
    def _meth(parsed_rec):
        return {"methylation": {
            "arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
            "geo_all_text": "^SAMPLE = GSM1\n!Sample_title = sarcoma classifier reference case 1\n",
            "fetches": {}, "pubmed_id": "1",
            "biostudies_controls": {"transport": {"n_hits": 1}, "absent": {"n_hits": 0}},
            "biostudies_records": {"E-TEST-1": {"provenance": "discovered_by_search",
                                                "fetch": {"http": 200}, "served_bytes": 10,
                                                "truncated": False, "parsed": parsed_rec}}}}

    v_complete = derive(_meth(complete))["arms"]["pan_sarcoma_methylation_deposit"]
    ck(v_complete["verdict"]
       == "NO_EMC_IN_A_COMPLETE_EBI_CENSUS_LABELS_FOR_THE_GEO_SERIES_STILL_UNLOCATED",
       f"a complete EBI census with no EMC gave {v_complete['verdict']}")
    v_short = derive(_meth(short))["arms"]["pan_sarcoma_methylation_deposit"]
    ck(v_short["verdict"] == "LABELS_NOT_LOCATED",
       f"an INCOMPLETE census produced {v_short['verdict']} — a partial read became a negative")

    emc_cat = _ebi([("Osteosarcoma", 60), ("Extraskeletal myxoid chondrosarcoma", 40)], 100)
    ck(emc_cat["n_emc_samples"] == 40,
       f"an EMC category counted {emc_cat['n_emc_samples']} samples, expected 40")
    ck(emc_cat["n_emc_idat_files"] == 2,
       f"EMC IDAT filenames were not harvested ({emc_cat['n_emc_idat_files']})")
    v_emc = derive(_meth(emc_cat))["arms"]["pan_sarcoma_methylation_deposit"]
    ck(v_emc["verdict"] == "EMC_LABELLED_IN_AN_EBI_DEPOSIT",
       f"an EBI deposit naming EMC gave {v_emc['verdict']}")

    # 27 · ⛔ A BROKEN SEARCH MAY NOT REPORT "NO MIRROR EXISTS". Same contract as arm 1's controls.
    for ctrl, why in (({"transport": {"n_hits": 0}, "absent": {"n_hits": 0}}, "dead transport"),
                      ({"transport": {"n_hits": 3}, "absent": {"n_hits": 2}}, "leaky absent")):
        inp = _meth(complete)
        inp["methylation"]["biostudies_controls"] = ctrl
        st = derive(inp)["arms"]["pan_sarcoma_methylation_deposit"]["stages"]["2_ebi_mirror_search"]
        ck(st["verdict"] == "SEARCH_CONTROLS_FAILED",
           f"a {why} search reported {st['verdict']} instead of SEARCH_CONTROLS_FAILED")

    # 28 · ⛔ AN UNPARSEABLE EBI RECORD IS UNREADABLE, NEVER EMPTY — and a truncation says so.
    bad = _parse_biostudies("E-TEST-2", '{"section": {"attributes": [', True)
    ck(bad["readable"] is False, "a truncated record parsed as readable")
    ck("TRUNCATED" in (bad["why"] or ""), f"a truncated record did not name truncation: {bad['why']}")
    ck(bad["census_complete"] is False, "an unreadable record claimed a complete census")

    # ⚠ AND THE WALKER MUST DESCEND BOTH SHAPES. `subsections` holds dicts AND nested lists of
    # dicts in the served record; a walker that handles only dicts silently drops whole branches,
    # which would render as "this deposit declares no samples".
    ck(complete["declared_sample_count"] == 100,
       "the walker did not reach a Samples node nested inside a list-of-lists")

    # 29 · ⛔ A BOT WALL IS NOT A PAPER, AND A CITING PAPER IS NOT A MIRROR. Both were measured on
    # 2026-08-24 and both had already produced a wrong reading before these guards existed.
    ck(_interstitial_markers('<base href="https://www.google.com/recaptcha/challengepage/">') != [],
       "a reCAPTCHA challenge page was graded as real content")
    ck(_interstitial_markers("Please enable JavaScript and cookies to continue") != [],
       "a JS/cookie bot wall was graded as real content")
    ck(_interstitial_markers("<article><p>Sarcoma classification by DNA methylation</p></article>")
       == [], "a real article body was graded as an interstitial")
    ck(_interstitial_markers(None) == [], "a missing body invented interstitial markers")

    # ⚠ The 21,246-byte reCAPTCHA page is the case a SIZE test cannot see. Asserted with a body big
    # enough to pass any length threshold, so the guard fails if the content test is ever swapped
    # back for a byte count.
    # A real bot wall declares itself in the <head> and pads afterwards, which is exactly the shape
    # that defeats a size test: 21,246 bytes of "200" that contain no article.
    big_wall = ('<html><head><base href="https://www.google.com/recaptcha/challengepage/">'
                "</head><body>" + ("padding " * 4000) + "</body></html>")
    ck(len(big_wall) > STUB_BYTES, "the fixture is too small to exercise the size-test failure mode")
    ck(_interstitial_markers(big_wall) != [],
       "a bot wall LARGER than the stub threshold was graded as real content")

    def _rec(source, mentions):
        # ⚠ The accession goes INSIDE the JSON. Appending it after the closing brace makes the body
        # unparseable, which the module correctly reports as `readable: false` — so the fixture
        # would exercise the parse-failure path instead of the classification path it is aiming at.
        abstract = ("we reanalysed " + GEO_SERIES) if mentions else "no accession here"
        body = {"attributes": [{"name": "DataSource", "value": source},
                               {"name": "Title", "value": "t"}],
                "section": {"attributes": [{"name": "Title", "value": "t"},
                                           {"name": "Abstract", "value": abstract}],
                            "subsections": []}}
        return _parse_biostudies("S-TEST", json.dumps(body), False)

    lit = _rec("Europe PMC", True)
    ck(lit["is_a_data_record"] is False,
       "a Europe PMC literature record was classified as a data record")
    ck(lit["mentions_geo_series"] is True, "the citation match itself was lost")
    dat = _rec("ArrayExpress", True)
    ck(dat["is_a_data_record"] is True, "an ArrayExpress data record was classified as literature")

    def _mirror_stage(rec_parsed, acc):
        inp = {"methylation": {
            "arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
            "geo_all_text": "^SAMPLE = GSM1\n!Sample_title = case 1\n", "fetches": {},
            "biostudies_controls": {"transport": {"n_hits": 1}, "absent": {"n_hits": 0}},
            "biostudies_records": {acc: {"provenance": "discovered_by_search",
                                         "fetch": {"http": 200}, "served_bytes": 10,
                                         "truncated": False, "parsed": rec_parsed}}}}
        return derive(inp)["arms"]["pan_sarcoma_methylation_deposit"]["stages"]["2_ebi_mirror_search"]

    st_lit = _mirror_stage(lit, "S-EPMC1")
    ck(st_lit["mirrors"] == [],
       f"a paper CITING the deposit was reported as a mirror of it: {st_lit['mirrors']}")
    ck(st_lit["literature_records_citing_the_series"] == ["S-EPMC1"],
       "a citing paper was dropped instead of being reported in its own list")
    ck(st_lit["verdict"] == "NO_EBI_MIRROR_OF_THIS_SERIES",
       f"citations alone produced {st_lit['verdict']}")
    st_dat = _mirror_stage(dat, "E-MTAB-1")
    ck(st_dat["mirrors"] == ["E-MTAB-1"], "a genuine data mirror was not reported")

    # 30 · ⛔ THE JOIN IS A LOOKUP ON A DECLARED KEY, AND AN UNJOINED CASE IS REPORTED, NEVER GUESSED.
    # This is the arm's payoff and also its most dangerous arithmetic: matching published labels to
    # deposited samples BY POSITION would give every case a plausible-looking partner and be
    # invisible when wrong. Every assertion below is offline.
    geo = "\n".join([
        "^SAMPLE = GSM1", "!Sample_title = sarcoma classifier reference case 259",
        "!Sample_description = REFERENCE_SAMPLE 259", "!Sample_platform_id = GPL13534",
        "!Sample_supplementary_file_1 = ftp://x/GSM1_A_Grn.idat.gz",
        "!Sample_supplementary_file_2 = ftp://x/GSM1_A_Red.idat.gz",
        "^SAMPLE = GSM2", "!Sample_title = sarcoma classifier validation case 54",
        "!Sample_description = VALIDATION_SAMPLE 54", "!Sample_platform_id = GPL21145",
        "!Sample_supplementary_file_1 = ftp://x/GSM2_B_Grn.idat.gz",
        "!Sample_supplementary_file_2 = ftp://x/GSM2_B_Red.idat.gz",
        # A sample that declares NO case id. It must never be used to absorb an unmatched label.
        "^SAMPLE = GSM3", "!Sample_title = sarcoma classifier reference case 999",
        "!Sample_description = Methylation data from sarcoma sample",
        "!Sample_platform_id = GPL13534",
    ])
    idx = _index_geo_cases(geo)
    ck(set(idx) == {"REFERENCE_SAMPLE 259", "VALIDATION_SAMPLE 54"},
       f"the case index keyed on the wrong thing: {sorted(idx)}")
    ck(idx["REFERENCE_SAMPLE 259"]["idat_urls"] == ["ftp://x/GSM1_A_Grn.idat.gz",
                                                    "ftp://x/GSM1_A_Red.idat.gz"],
       "IDAT urls were not carried through the case index")

    def _joined(case_ids, geo_text=geo):
        return derive({"methylation": {
            "arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
            "geo_all_text": geo_text, "fetches": {},
            "supplementary": {"u": {"parsed": {
                "readable": True, "n_emc_rows": len(case_ids), "confusable_rows": 0,
                "emc_rows": [], "emc_case_ids": case_ids}}}}}
        )["arms"]["pan_sarcoma_methylation_deposit"]["emc_cohort"]

    j = _joined(["REFERENCE_SAMPLE 259", "VALIDATION_SAMPLE 54"])
    ck(j["n_joined_to_a_deposited_sample"] == 2, f"join found {j['n_joined_to_a_deposited_sample']}")
    ck(j["n_in_the_reference_set"] == 1 and j["n_in_the_validation_set"] == 1,
       "the reference and validation sets were not separated")
    ck(j["n_with_downloadable_idats"] == 2 and j["n_idat_files_total"] == 4,
       f"IDAT accounting wrong: {j['n_with_downloadable_idats']}, {j['n_idat_files_total']}")
    ck(sorted(j["platforms"]) == ["GPL13534", "GPL21145"], "platforms were lost in the join")

    # ⛔ A LABEL WITH NO DEPOSITED COUNTERPART IS REPORTED UNJOINED. GSM3 exists, is a reference
    # case, and has no declared id — so it must NOT be handed this label.
    j2 = _joined(["REFERENCE_SAMPLE 259", "REFERENCE_SAMPLE 999"])
    ck(j2["n_joined_to_a_deposited_sample"] == 1,
       f"an unmatched label was joined anyway ({j2['n_joined_to_a_deposited_sample']})")
    ck(j2["case_ids_not_joined"] == ["REFERENCE_SAMPLE 999"],
       f"the unjoined case was not reported: {j2['case_ids_not_joined']}")
    ck(j2["n_cases_named_by_the_paper"] == 2,
       "the paper's own count was quietly reduced to the joinable subset")
    ck("GSM3" not in json.dumps(j2["cases"]),
       "a sample declaring NO case id was matched to a label by position")

    # ⚠ The older-cache fallback must FLAG itself: `emc_rows` is capped at 25 for display, so a
    # join built from it can be a subset that looks complete.
    legacy = derive({"methylation": {
        "arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n", "geo_all_text": geo,
        "fetches": {}, "supplementary": {"u": {"parsed": {
            "readable": True, "n_emc_rows": 1, "confusable_rows": 0,
            "emc_rows": ["REFERENCE_SAMPLE 259 | Extraskeletal myxoid chondrosarcoma"]}}}}}
    )["arms"]["pan_sarcoma_methylation_deposit"]["emc_cohort"]
    ck(legacy["n_joined_to_a_deposited_sample"] == 1, "the legacy-cache fallback did not join")
    ck(legacy["case_ids_came_from_capped_display_rows"] is True,
       "a join built from CAPPED display rows did not flag itself as bounded")
    ck(j["case_ids_came_from_capped_display_rows"] is False,
       "a join built from the full field wrongly flagged itself as bounded")

    if fails:
        print("SELFTEST FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print("selftest ok (30 guard groups)")
    return 0


# ────────────────────────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="retrieve both arms and write the inputs cache (needs network; CI)")
    ap.add_argument("--check", action="store_true",
                    help="re-derive from the cached inputs and diff against the committed artifact")
    ap.add_argument("--selftest", action="store_true",
                    help="offline guard assertions; runs before any fetch")
    # ⭐ WHY A PER-ARM FETCH EXISTS. The two arms hit different hosts, fail for unrelated reasons and
    # answer different questions. Re-running the junction search to re-read a methylation deposit
    # spends ~15 minutes of a runner AND rewrites arm 1's measured numbers for no reason — and if
    # the service happened to be degraded that day, it would silently replace a good measurement
    # with a worse one. `--only` MERGES into the existing cache: the arm named is refetched, every
    # other arm is carried through from the cache verbatim, and refusing to fetch an arm is never
    # the same as that arm returning nothing.
    ap.add_argument("--only", choices=["snaptron", "methylation"], default=None,
                    help="--fetch only this arm; the other arms are carried through from the cache")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.fetch:
        inp = {"_generated_utc": _now(),
               "_what": "raw retrieval only; every verdict is computed in derive()"}
        if args.only:
            if not os.path.exists(INPUTS):
                print(f"--only needs an existing cache at {INPUTS}; run a full --fetch first",
                      file=sys.stderr)
                return 2
            with open(INPUTS) as fh:
                prev = json.load(fh)
            inp = dict(prev)
            inp["_generated_utc"] = _now()
            inp["_partial_refetch"] = {"arm": args.only, "at": _now(),
                                       "carried_over_from": prev.get("_generated_utc")}
        if args.only in (None, "snaptron"):
            inp["snaptron"] = fetch_snaptron()
        if args.only in (None, "methylation"):
            inp["methylation"] = fetch_methylation()
        with open(INPUTS, "w") as fh:
            json.dump(inp, fh, indent=1, sort_keys=True)
        print(f"wrote {INPUTS}" + (f" (only the {args.only} arm was refetched)" if args.only else ""))
    else:
        if not os.path.exists(INPUTS):
            print(f"no inputs cache at {INPUTS}; run --fetch (CI) first", file=sys.stderr)
            return 2
        with open(INPUTS) as fh:
            inp = json.load(fh)

    res = derive(inp)

    if args.check:
        if not os.path.exists(OUT):
            print(f"no committed artifact at {OUT} to check against", file=sys.stderr)
            return 2
        with open(OUT) as fh:
            old = json.load(fh)
        a = json.dumps({k: v for k, v in old.items() if not k.startswith("_generated")},
                       sort_keys=True)
        b = json.dumps({k: v for k, v in res.items() if not k.startswith("_generated")},
                       sort_keys=True)
        if a != b:
            print("DRIFT: the committed artifact does not re-derive from its own inputs cache")
            return 1
        print("check ok: artifact re-derives from its inputs")
        return 0

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(f"wrote {OUT}")
    print(json.dumps({"headline": res["headline"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
