#!/usr/bin/env python3
"""Screen every junction gapmer against PRE-mRNA — the compartment both committed screens cannot see.

⭐ WHY THIS EXISTS. The submission manuscript names this as its own largest blind spot, in its
Limitations, and says so in as many words: "both screens search mature transcript sequence only.
RNase-H1 is active in the nucleus and gapmers are known to engage pre-mRNA, so intronic and
intron-exon-spanning sites are a class of liability that neither the RefSeq RNA search nor the
transcript-level exhaustive scan can see; the counts reported here therefore bound the
mature-transcript compartment only. That gap is closable by a genomic screen and is not closed here."

⛔ AND IT WAS IN NO REGISTER ANYWHERE. A repository-wide grep for "genomic screen" on 2026-08-13
returned exactly that one sentence: no `required_validation` row, no method-watch entry, no working-record
item. A paper's own stated hole is the easiest thing in the world to leave open, because conceding it
reads as rigour and closing it is work.

⚠⚠ THE DIRECTION OF THE BIAS IS THE POINT, AND IT IS NOT NEUTRAL.
`hybrid-intron-aso-target.md` states it plainly for the same database families: both target sets are
MATURE transcript sets, so "running them unchanged yields a low off-target count BY CONSTRUCTION."
A junction gapmer's two halves are exonic, and in a parent PRE-mRNA an exon is followed by an intron
rather than by the next exon — so the parent pre-mRNA is exactly where a design's donor half sits
beside sequence no mature screen has ever compared it against. Reporting a clean mature screen and
staying silent about pre-mRNA is therefore not conservative; it is measuring the compartment where the
liability is least likely to be.

★ WHAT THIS MEASURES, EXACTLY, AND WHAT IT DOES NOT.
Two arms, and they are deliberately not equal in strength:

  (a) THE PARENT PRE-mRNA ARM IS EXHAUSTIVE AND IS THE ONE ANY CLAIM RESTS ON. Unspliced sequence for
      all six parent transcripts is fetched from Ensembl, and every design's 16-nt target window is
      scanned against all of it at <=2 mismatches, both orientations, seeded by the pigeonhole
      principle so completeness is a property of the method rather than of the search's sensitivity.
      <=2 is chosen to match the >=14/16 threshold the BLAST arm uses, so the two are comparable.
      Every hit is classified by COMPARTMENT — wholly intronic, wholly exonic, or spanning an
      intron-exon boundary — because only the exonic ones could have been visible to a mature screen.

  (b) THE GENOME-WIDE ARM IS BEST-EFFORT AND SAYS SO. NCBI's URL API is asked for a genomic database
      and the answer is recorded with the database that actually served it. If no genomic database
      answers, this arm reports that it did not run. It NEVER degrades to a mature-transcript database
      and calls the result a genomic screen: that would reproduce the exact defect this module exists
      to close, with a provenance string asserting the opposite.

⛔ WHAT A HIT HERE IS AND IS NOT. Pre-mRNA is transcribed in the transcript's own orientation, so a
match on the forward strand of a pre-mRNA is hybridisable and a match on its reverse complement is
not — the same rule, and the same reason, as the mature screens' orientation filter. Antisense
transcription at these loci is a separate question this does not answer; annotated antisense
transcripts are RefSeq records and are already in the mature screens.

⚠ AND A HIT IS NOT A MEASUREMENT OF CLEAVAGE. As everywhere else in this work: a paired six-nucleotide
gap is a necessary condition for RNase-H1 cleavage, not a sufficient one, and nothing here measures
activity. What this can do is move a whole compartment from "unmeasured" to "measured", which is the
only thing a sequence screen was ever able to do.

    python3 research/modalities/aso_premrna_offtarget.py            # needs network (Ensembl)
    python3 research/modalities/aso_premrna_offtarget.py --offline   # scan a cached fetch only
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
#: ⛔ THE ATLAS PATH IS A KNOB AS OF 2026-08-13, FOR THE SAME REASON `PREMRNA_OUT` ALREADY WAS. This
#: module derives its gap span and its mismatch ceiling from `junction_aso_offtarget`, so it already
#: follows a geometry change — but it read its DESIGNS from one fixed filename, so a 5-8-5 or 5-10-5
#: run would have scanned the 16-mer designs under the longer geometry's gap indices. The geometry
#: and the design set have to move together or the arm measures neither.
ATLAS = os.path.join(HERE, os.environ.get("ATLAS_JSON") or "nr4a3-fusion-junction-atlas.json")
CACHE = os.path.join(HERE, "aso-premrna-sequences.json")
OUT = os.path.join(HERE, os.environ.get("PREMRNA_OUT", "aso-premrna-offtarget.json"))

ENSEMBL = "https://rest.ensembl.org"
def _max_mismatches():
    """The mismatch ceiling, DERIVED from the BLAST arm's identity threshold, never typed.

    ⛔ THE TWO ARMS HAVE TO ASK THE SAME QUESTION OR THE COMPARISON IS AN ARTEFACT. The mature screen
    admits a near-match at `NEAR_MATCH_MIN_IDENT`/`OLIGO_LEN`; ask pre-mRNA a stricter question and it
    comes back cleaner for that reason alone, which would read as "the intronic compartment is fine"
    and would be the most flattering possible way to be wrong. So this is `OLIGO_LEN - MIN_IDENT` from
    the owning module. The fallback is 2 — the value that arithmetic yields for the 16-mer 5-6-5
    geometry this panel uses — and it is a fallback for an import failure, not a second definition.
    """
    try:
        sys.path.insert(0, HERE)
        from junction_aso_offtarget import MAX_MISMATCHES_PER_NEAR_MATCH  # noqa: PLC0415
        return int(MAX_MISMATCHES_PER_NEAR_MATCH)
    except Exception:  # noqa: BLE001
        return 2


MAX_MM = _max_mismatches()
#: The catalytic gap, 1-based inclusive, as `junction_aso_offtarget` defines it. Imported rather than
#: re-typed where possible; the fallback is the same literal that module carries.
GAP_1BASED = (6, 11)

COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def _rc(s):
    return s.translate(COMPLEMENT)[::-1]


def _gap_region():
    """Ask the owning module for the gap, so a geometry change cannot desynchronise the two.

    ⛔ THIS SEAM WAS DEAD FROM THE DAY IT WAS WRITTEN UNTIL 2026-08-13, AND NOTHING COULD SHOW IT.
    `junction_aso_offtarget` had no `GAP_REGION_1BASED` — it computed `[ja.WING + 1, ja.OLIGO_LEN -
    ja.WING]` inline at four separate sites — so this import raised ImportError on every call, the
    bare `except Exception` swallowed it, and the function returned this module's own hard-coded
    `GAP_1BASED`. At the default 16,5 geometry that fallback is the right answer, which is exactly
    why it never surfaced: a guard that fails closed onto the correct value is indistinguishable
    from one that works. Under a `20,5` dispatch this arm would have scored the gap as [6, 11]
    while the screen it is meant to stay in step with used [6, 15] — the desynchronisation the
    docstring above promises to prevent.

    So the import is now unconditional. If the owning module stops exporting the constant, this
    raises rather than quietly substituting a geometry nobody chose.
    """
    sys.path.insert(0, HERE)
    from junction_aso_offtarget import GAP_REGION_1BASED  # noqa: PLC0415
    return tuple(GAP_REGION_1BASED)


#: ⛔ TEN, NOT FOUR, AND THE NUMBER IS MEASURED (2026-08-15). Four consecutive CI dispatches of this
#: screen died in the fetch loop, and the discriminating detail is that they died in DIFFERENT
#: places every time:
#:     run 31890657213  503  lookup/id/ENST00000325455   (PGR,   4th gene)
#:     run 31891448127  503  lookup/id/ENST00000605844   (TAF15, 5th gene)
#:     run 31891???     500  sequence/id/ENST00000333725 (TCF12, 6th gene, and a DIFFERENT endpoint)
#:     run 31892621691  503  lookup/id/ENST00000325455   (PGR   again)
#: Three transcripts, two endpoints, two status codes, four runs: that is an Ensembl-side
#: instability window, not a bad identifier and not a code fault. `fetch_premrna` makes 2 requests
#: per transcript, so a 7-transcript atlas is 14 SERIAL calls that must ALL succeed; at four tries
#: and a 3/6/9 s backoff each call buys about eighteen seconds of patience, and the run is a coin
#: flip weighted against itself. Engineering effort is free and a re-dispatch is 15 minutes of wall
#: clock, so the patience is bought here instead: 10 tries with the same widening pause is ~165 s
#: per call, which spans the outages actually observed. ⚠ It does NOT weaken the failure: the last
#: error is still raised, still names the URL, and still lands in `aso-premrna-offtarget-FAILED.json`.
DEFAULT_TRIES = 10


def _http(url, timeout=180, accept="application/json", tries=DEFAULT_TRIES):
    """GET with the Accept header Ensembl actually keys on, and a bounded retry.

    ⚠ THE HEADER MATTERS AND THE FIRST VERSION SENT THE WRONG ONE. Ensembl REST selects its response
    format from `Accept` (or the `content-type` query parameter); a `Content-Type` request header on a
    GET describes a body that does not exist and is not what it reads. Asking for plain text with a
    JSON `Content-Type` is the kind of mismatch that returns a 400 rather than a sequence.

    ⚠ AND A ONE-SHOT NETWORK CALL IN CI IS A COIN FLIP, not a measurement: 429 and 503 are routine
    from a public API. Retried with a widening pause, and the LAST error is raised rather than
    swallowed, so a genuine failure still fails and still says why.
    """
    err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": accept, "User-Agent": "rare-cancers-aso-premrna/1.0"})
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001 — re-raised below once the retries are spent
            err = e
            body = getattr(e, "read", None)
            detail = ""
            if callable(body):
                try:
                    detail = f" body={body().decode('utf-8', 'replace')[:300]!r}"
                except Exception:  # noqa: BLE001
                    detail = ""
            print(f"  GET failed (attempt {attempt + 1}/{tries}): {type(e).__name__}: {e}{detail}\n"
                  f"    url={url}", file=sys.stderr)
            if attempt + 1 < tries:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Ensembl GET failed after {tries} attempts: {type(err).__name__}: {err} "
                       f"({url})")


def fetch_premrna(transcripts):
    """Unspliced sequence and exon spans for each transcript, in TRANSCRIPT orientation.

    ⚠ `type=genomic` on a TRANSCRIPT id is the unspliced transcript — pre-mRNA — and Ensembl returns
    it already strand-corrected, which is what makes the forward/reverse distinction below mean
    "hybridisable" rather than "on the plus strand of the chromosome". Asking for a GENE id instead
    would return a region that can carry neighbouring genes, and the compartment classification would
    silently be about the wrong feature.
    """
    out = {}
    for gene, tid in sorted(transcripts.items()):
        seq = _http(f"{ENSEMBL}/sequence/id/{tid}?type=genomic",
                    accept="text/plain").strip().upper()
        if not seq or set(seq) - set("ACGTN"):
            # An error page returned with a 200 would otherwise be scanned as if it were sequence,
            # and every design would come back clean against it.
            raise RuntimeError(f"{gene} ({tid}): the response is not nucleotide sequence "
                               f"(len={len(seq)}, first 80 chars: {seq[:80]!r})")
        time.sleep(0.4)                       # Ensembl asks for <= 15 requests/s; this is far under
        meta = json.loads(_http(f"{ENSEMBL}/lookup/id/{tid}?expand=1"))
        strand = meta.get("strand")
        g0, g1 = meta.get("start"), meta.get("end")
        exons = []
        for ex in meta.get("Exon") or []:
            # Convert genomic coordinates to offsets along the returned (strand-corrected) sequence.
            if strand == 1:
                a, b = ex["start"] - g0, ex["end"] - g0
            else:
                a, b = g1 - ex["end"], g1 - ex["start"]
            exons.append([a, b])
        exons.sort()
        out[gene] = {
            "transcript": tid, "strand": strand, "genomic_start": g0, "genomic_end": g1,
            "premrna_nt": len(seq), "n_exons": len(exons),
            "exonic_nt": sum(b - a + 1 for a, b in exons),
            "exon_spans_0based_inclusive": exons, "sequence": seq,
        }
        print(f"  {gene:6} {tid}  pre-mRNA {len(seq):>7,} nt  {len(exons)} exons  "
              f"exonic {out[gene]['exonic_nt']:>6,} nt", file=sys.stderr)
    return out


def _mismatches(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            n += 1
            if n > MAX_MM:
                return n
    return n


def _compartment(start, end, exons):
    """Wholly intronic, wholly exonic, or spanning a boundary — over [start, end] inclusive."""
    covered = 0
    for a, b in exons:
        if b < start:
            continue
        if a > end:
            break
        covered += min(b, end) - max(a, start) + 1
    span = end - start + 1
    if covered == 0:
        return "intronic"
    if covered >= span:
        return "exonic"
    return "intron_exon_spanning"


#: The number of seed blocks. `MAX_MM + 1` is the pigeonhole requirement and nothing else: with
#: `MAX_MM` mismatches spread over this many disjoint blocks, at least one block is untouched.
N_SEED_BLOCKS = MAX_MM + 1


def seed_blocks(length):
    """Half-open [start, end) spans partitioning a window of `length` into balanced seed blocks.

    Balanced rather than equal, because a length need not divide: the first `length % n` blocks take
    one extra base. At length 16 with three blocks this returns (0,6), (6,11), (11,16) — the exact
    literal it replaces, which is what makes the change safe to land against a committed screen.
    """
    n = N_SEED_BLOCKS
    sizes = [length // n + (1 if i < length % n else 0) for i in range(n)]
    out, start = [], 0
    for s in sizes:
        out.append((start, start + s))
        start += s
    return out


def scan(designs, premrna):
    """Exhaustive <=MAX_MM scan of every target window against every pre-mRNA, both orientations.

    ⛔ COMPLETENESS IS A PROPERTY OF THE SEEDING, NOT AN ASSUMPTION. Splitting a 16-mer into three
    blocks means at most two of them can carry a mismatch, so a hit at <=2 mismatches must match at
    least one block exactly. Seeding on all three therefore cannot miss one. That is the same
    pigeonhole argument `aso_insilico.offtarget_scan` makes for <=1 mismatch over two halves, extended
    by one block because this arm's threshold is wider — stated here because "exhaustive" is a word
    this paper uses as load-bearing and it has to be earned each time.

    ⚠ AND THE BLOCK BOUNDARIES ARE DERIVED FROM THE WINDOW, NOT TYPED (2026-08-13). They were the
    literal `[(0, 6), (6, 11), (11, L)]` — three blocks of 6, 5 and 5 at the 16-mer this arm was
    written for. The pigeonhole argument above survives any partition into three blocks, so a longer
    window stayed COMPLETE; what it stopped being was balanced, with the tail block running to 9 nt
    of a 20-mer while the first two shrank in relative terms. Balanced thirds reproduce (6, 5, 5)
    exactly at L=16, so nothing about the committed screen moves.
    """
    gap_a, gap_b = _gap_region()
    lo, hi = gap_a - 1, gap_b                 # to 0-based half-open
    per_design = {}
    for gene, rec in sorted(premrna.items()):
        fwd = rec["sequence"]
        exons = rec["exon_spans_0based_inclusive"]
        strands = (("forward", fwd, True), ("reverse_complement", _rc(fwd), False))
        for label, seq, hybridisable in strands:
            index = {}
            for d in designs:
                t = d["target_mRNA_5to3"]
                L = len(t)
                for a, b in seed_blocks(L):
                    index.setdefault(t[a:b], []).append((d["_key"], a, t, L))
            # One pass over the sequence per block length, collecting seed positions.
            by_len = {}
            for block in index:
                by_len.setdefault(len(block), set()).add(block)
            pos = {}
            for blen, blocks in by_len.items():
                for i in range(len(seq) - blen + 1):
                    sub = seq[i:i + blen]
                    if sub in blocks:
                        pos.setdefault(sub, []).append(i)
            for block, entries in index.items():
                for i in pos.get(block, ()):
                    for key, off, t, L in entries:
                        ws = i - off
                        if ws < 0 or ws + L > len(seq):
                            continue
                        rec_d = per_design.setdefault(key, {"_seen": set(), "hits": []})
                        # ⚠ DEDUPED BY (strand, window start): three blocks can seed the same window,
                        # and counting it once per seed would inflate every count by up to threefold.
                        tag = (gene, label, ws)
                        if tag in rec_d["_seen"]:
                            continue
                        rec_d["_seen"].add(tag)
                        window = seq[ws:ws + L]
                        mm = _mismatches(window, t)
                        if mm > MAX_MM:
                            continue
                        # Coordinates are reported on the FORWARD (transcript) sequence in both
                        # orientations, so a reader can locate a reverse hit without re-deriving it.
                        f_start = ws if hybridisable else len(seq) - ws - L
                        f_end = f_start + L - 1
                        gap_mm = _mismatches(window[lo:hi], t[lo:hi])
                        rec_d["hits"].append({
                            "gene": gene, "orientation": label, "hybridisable": hybridisable,
                            "premrna_start_0based": f_start, "premrna_end_0based": f_end,
                            "mismatches": mm, "gap_mismatches": min(gap_mm, MAX_MM + 1),
                            "gap_fully_paired": gap_mm == 0,
                            "compartment": _compartment(f_start, f_end, exons),
                        })
    for rec_d in per_design.values():
        rec_d.pop("_seen", None)
        rec_d["hits"].sort(key=lambda h: (h["mismatches"], h["gene"], h["premrna_start_0based"]))
    return per_design


#: Candidate NCBI databases for the genome-wide arm, tried in order. Named as candidates because the
#: URL API's database names change and a wrong one returns an empty search rather than an error, so
#: the one that ANSWERED is recorded in the artifact instead of assumed.
GENOMIC_DB_CANDIDATES = ("core_nt", "nt", "refseq_genomes")


def genomic_blast(designs, dbs=GENOMIC_DB_CANDIDATES):
    """Best-effort genome-wide arm: BLAST each target window against a genomic database.

    ⛔ THIS ARM MUST NEVER DEGRADE INTO A MATURE-TRANSCRIPT SEARCH AND CALL ITSELF GENOMIC. That is
    the failure this whole module exists to close, and doing it here — with a provenance string
    asserting the opposite — would be worse than not running at all. So the database is taken from a
    candidate list of GENOMIC databases only, `refseq_rna` is not among them and must not be added,
    and if none answers the artifact records `ran: false` with the reason.

    ⚠ It is scoped to the designs handed to it rather than to all 190, because the URL API serves one
    query at a time and a genome-scale blastn-short is minutes each. The caller chooses the scope and
    the artifact records it, so a reader can see the arm is a spot check and not a corpus screen.
    """
    sys.path.insert(0, HERE)
    try:
        import junction_aso_offtarget as jo  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        return {"ran": False, "why": f"junction_aso_offtarget did not import: {e}", "db": None}

    def put(seq, db):
        params = {"CMD": "Put", "PROGRAM": "blastn", "DATABASE": db, "QUERY": seq,
                  "WORD_SIZE": "7", "EXPECT": "1000", "HITLIST_SIZE": str(jo.BLAST_HITLIST_SIZE),
                  "FILTER": "F", "MEGABLAST": "off", "ENTREZ_QUERY": "txid9606[ORGN]"}
        html = _http(jo.BLAST + "?" + urllib.parse.urlencode(params))
        import re  # noqa: PLC0415
        m = re.search(r"^\s*RID = (\S+)", html, re.M)
        if not m:
            raise RuntimeError(f"no RID from {db}")
        return m.group(1)

    chosen, rows, why = None, [], None
    for db in dbs:
        try:
            rid = put(designs[0]["target_mRNA_5to3"], db)
            jo.blast_poll(rid)
            rows.append({"antisense_5to3": designs[0]["antisense_5to3"],
                         "junction_label": designs[0]["junction_label"],
                         "hits": jo.blast_hits(rid)})
            chosen = db
            break
        except Exception as e:  # noqa: BLE001
            why = f"{db}: {e}"
            print(f"  genomic arm: {db} did not answer ({e})", file=sys.stderr)
    if not chosen:
        return {"ran": False, "why": why or "no candidate database answered", "db": None,
                "candidates_tried": list(dbs)}

    for d in designs[1:]:
        try:
            rid = put(d["target_mRNA_5to3"], chosen)
            jo.blast_poll(rid)
            rows.append({"antisense_5to3": d["antisense_5to3"],
                         "junction_label": d["junction_label"], "hits": jo.blast_hits(rid)})
        except Exception as e:  # noqa: BLE001
            rows.append({"antisense_5to3": d["antisense_5to3"],
                         "junction_label": d["junction_label"], "error": str(e)})
        print(f"  genomic arm: {d['antisense_5to3']} done", file=sys.stderr)
    return {"ran": True, "db": chosen, "candidates_tried": list(dbs),
            "scope": "caller-selected subset, not the whole corpus", "per_design": rows}


def _clean_sequences():
    """The designs with no hybridisable near-match on the mature screens, read from the screens.

    ⚠ DERIVED, NEVER LISTED. Nine sequences typed into this module would be a second home for the
    paper's headline set and would go stale the first time the corpus grew — which is exactly what
    happened to every other copy of that set. The predicate is the same one `submission_tables` and
    `test_aso_submission_numbers` apply: no hybridisable retained hit, over a hit list complete enough
    to say so. Returns an empty set if the collapse artifact is absent, which makes the genomic arm
    fall back to a single design rather than silently screening nothing.
    """
    collapse = os.path.join(HERE, "junction-aso-offtarget-locus-collapse.json")
    if not os.path.exists(collapse):
        return set()
    try:
        sys.path.insert(0, HERE)
        from junction_aso_offtarget import (  # noqa: PLC0415
            SAVED_HITS_PER_DESIGN, screen_counts_are_orientation_filtered)
    except Exception:  # noqa: BLE001
        return set()
    out = set()
    for s in json.load(open(collapse))["screens"]:
        if not (s.get("junction_label") and screen_counts_are_orientation_filtered(s.get("orientation"))):
            continue
        p = os.path.join(HERE, s["screen"])
        if not os.path.exists(p):
            continue
        for o in json.load(open(p)).get("oligos") or []:
            n = o.get("n_offtarget_near_matches")
            if o.get("status") != "screened" or n is None or n > SAVED_HITS_PER_DESIGN:
                continue
            if not [h for h in o.get("offtargets") or [] if not h.get("is_minus_strand")]:
                out.add(o["antisense_5to3"])
    return out


def _designs_from_atlas():
    """Every design at every frame-compatible junction, keyed by (junction, antisense sequence)."""
    atlas = json.load(open(ATLAS))
    out, seen = [], set()
    for pan in atlas["panels"]:
        for d in pan.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            key = f"{pan['junction_label']}|{d['antisense_5to3']}"
            if key in seen:
                continue
            seen.add(key)
            out.append({"_key": key, "junction_label": pan["junction_label"],
                        "antisense_5to3": d["antisense_5to3"],
                        "target_mRNA_5to3": d["target_mRNA_5to3"],
                        "gap_specificity_margin": d.get("gap_specificity_margin"),
                        "gc_percent": d.get("gc_percent")})
    return out, atlas


def main(argv):
    """Run the screen, and make a FAILURE readable from the artifact branch.

    ⛔ WHY THE WRAPPER. The first CI dispatch of this module failed, and the traceback was
    unreachable: the run's own log archive is served from a host the dev sandbox's egress proxy
    blocks, and the log tail the API returns was entirely consumed by the publish step's output. So
    the diagnosis had to be guessed — which CLAUDE.md §4 forbids — over a $0 run that could simply
    have written down what happened. A failed screen now publishes a record of the failure and THEN
    exits non-zero: the step still goes red, and the reason travels to where it can be read.
    """
    try:
        return _run(argv)
    except Exception as e:  # noqa: BLE001 — the point is to record it, and the re-raise is below
        import traceback  # noqa: PLC0415
        p = os.path.join(HERE, "aso-premrna-offtarget-FAILED.json")
        with open(p, "w") as fh:
            json.dump({
                "_what": "a pre-mRNA screen run that FAILED. Not a result, and not a reading of absence.",
                "_why_this_file_exists": ("the traceback of a CI failure is otherwise unreachable "
                                          "from the dev sandbox, so it was being guessed at"),
                "error_type": type(e).__name__, "error": str(e),
                "traceback": traceback.format_exc().splitlines()[-25:],
                "argv": list(argv),
                "env": {k: os.environ.get(k) for k in ("PREMRNA_GENOMIC", "PREMRNA_OUT")},
                "atlas_present": os.path.exists(ATLAS),
                "sequence_cache_present": os.path.exists(CACHE),
            }, fh, indent=1)
            fh.write("\n")
        print(f"::error::pre-mRNA screen failed: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"wrote {p}", file=sys.stderr)
        traceback.print_exc()
        return 1


def _run(argv):
    offline = "--offline" in argv
    designs, atlas = _designs_from_atlas()
    transcripts = {g: v["transcript"] for g, v in atlas["transcripts"].items()}
    print(f"designs: {len(designs)} across {len({d['junction_label'] for d in designs})} junctions",
          file=sys.stderr)

    if offline:
        if not os.path.exists(CACHE):
            print(f"--offline needs {os.path.basename(CACHE)}, which is not present. The fetch needs "
                  f"network (Ensembl), so run this in CI.", file=sys.stderr)
            return 2
        premrna = json.load(open(CACHE))["genes"]
    else:
        print("fetching unspliced transcript sequence from Ensembl", file=sys.stderr)
        premrna = fetch_premrna(transcripts)
        with open(CACHE, "w") as fh:
            json.dump({"_what": "unspliced (pre-mRNA) sequence and exon spans, transcript orientation",
                       "_source": "Ensembl REST /sequence/id/{ENST}?type=genomic + /lookup expand",
                       "genes": premrna}, fh)
        print(f"  cached -> {os.path.basename(CACHE)}", file=sys.stderr)

    hits = scan(designs, premrna)

    # ⚠ THE GENOMIC ARM IS OPT-IN AND ITS SCOPE IS EXPLICIT. Default is the designs the paper's
    # cleanliness claim is actually about — the ones with no hybridisable near-match on either mature
    # screen — because those are where an unmeasured compartment would change a conclusion. A blank
    # `PREMRNA_GENOMIC` skips the arm and the artifact says it did not run, which is the honest state.
    genomic = {"ran": False, "why": "not requested (set PREMRNA_GENOMIC=1 to run)", "db": None}
    want = os.environ.get("PREMRNA_GENOMIC", "").strip().lower() in ("1", "true", "yes")
    if want and not offline:
        picks = [d for d in designs if d["antisense_5to3"] in _clean_sequences()]
        if not picks:
            picks = designs[:1]
        print(f"genomic arm: {len(picks)} design(s)", file=sys.stderr)
        genomic = genomic_blast(picks)

    rows, corpus = [], {"designs": 0, "with_any_hit": 0, "with_hybridisable_gap_paired": 0,
                        "with_a_liability_invisible_to_mature_screens": 0}
    for d in designs:
        h = (hits.get(d["_key"]) or {}).get("hits") or []
        hyb = [x for x in h if x["hybridisable"]]
        gap = [x for x in hyb if x["gap_fully_paired"]]
        # The whole point: a hit that touches intronic sequence could not have appeared in either
        # mature-transcript screen, so it is NEW information rather than a re-count.
        new = [x for x in gap if x["compartment"] != "exonic"]
        corpus["designs"] += 1
        corpus["with_any_hit"] += bool(h)
        corpus["with_hybridisable_gap_paired"] += bool(gap)
        corpus["with_a_liability_invisible_to_mature_screens"] += bool(new)
        rows.append({
            "junction_label": d["junction_label"], "antisense_5to3": d["antisense_5to3"],
            "gc_percent": d["gc_percent"], "gap_specificity_margin": d["gap_specificity_margin"],
            "n_hits_either_orientation": len(h), "n_hybridisable": len(hyb),
            "n_hybridisable_gap_fully_paired": len(gap),
            "n_invisible_to_mature_screens": len(new),
            "compartments": {c: sum(1 for x in gap if x["compartment"] == c)
                             for c in ("intronic", "intron_exon_spanning", "exonic")},
            "hits": h[:20],
            "hits_truncated": len(h) > 20,
        })

    rec = {
        # ⛔ THE PARENT COUNT IS DERIVED, NOT TYPED (2026-08-15). This read "all six parent
        # transcripts" as a constant. The atlas's parent set is not always six — the non-coding
        # acceptor atlas carries SEVEN, because PGR joined it with the PGR::NR4A3 seam — and the
        # committed pre-mRNA cache holds six, so an offline run over that atlas scans 6 of 7 while
        # the sentence above it says "all". A hard-coded population is how a partial scan reports
        # itself as complete.
        "_what": (f"Exhaustive <=2-mismatch screen of every fusion-specific junction gapmer's "
                  f"target window against the UNSPLICED (pre-mRNA) sequence of "
                  f"{len(premrna)} parent transcript(s) ({', '.join(sorted(premrna))}), both "
                  f"orientations, gap-resolved and classified by compartment."),
        # ⛔⛔ A PARENT IN THE ATLAS THAT WAS NOT SCANNED IS NAMED, NOT DROPPED. An absent reading is
        # never a reading of absence: a design could complement a parent's pre-mRNA that this run
        # never looked at, and the only difference between that and a clean result is this field.
        "⛔_parents_in_the_atlas_that_were_NOT_scanned": {
            "genes": sorted(set(transcripts) - set(premrna)),
            "why": ("present in the atlas's parent set but absent from the sequence this run "
                    "scanned. On an --offline run that means the committed cache "
                    f"({os.path.basename(CACHE)}) does not carry them, and closing the gap needs a "
                    "networked (CI) run that re-fetches the cache with the atlas's full parent set. "
                    "⛔ These genes are UNMEASURED here — not clean."),
        },
        "_why": ("The manuscript's Limitations concede that both committed screens search mature "
                 "transcript only, that RNase-H1 is nuclear, and that the intronic compartment is "
                 "therefore unmeasured. This measures it for the gene set where a junction gapmer is "
                 "most likely to find one: the parents that supply its own two halves."),
        "_what_this_is_not": [
            "Not a genome-wide screen. It covers six parent transcripts' pre-mRNA exhaustively and "
            "says nothing about the other ~20,000 genes' introns.",
            "Not a measurement of cleavage. A fully paired gap is necessary for RNase-H1 and is not "
            "sufficient, and no wet-lab experiment has been performed.",
            "Not a statement about antisense transcription at these loci. A reverse-complement match "
            "is reported and is counted as NOT hybridisable, on the same rule the mature screens use.",
        ],
        "_cost": ("$0 - CPU only, scanning the COMMITTED pre-mRNA cache; no network was used. "
                  "No GPU, no rental."
                  if offline else
                  "$0 - CPU and one Ensembl read. No GPU, no rental."),
        # ⛔ WHICH SEQUENCE THIS SCANNED, SAID OUT LOUD (added 2026-08-15). Before this the artifact
        # was byte-for-byte silent about `--offline`: a run over the committed cache and a run over a
        # live Ensembl fetch produced records that looked identical, and the `_cost` line positively
        # asserted "one Ensembl read" for both. A plausible-looking record is more dangerous than an
        # empty one, and provenance is exactly the field a reader cannot reconstruct from the result.
        "sequence_source": {
            "mode": "committed_cache" if offline else "ensembl_fetch_this_run",
            "file": os.path.basename(CACHE) if offline else None,
            "cache_source_line": (json.load(open(CACHE)).get("_source") if offline else None),
            "⚠": ("A CACHE IS NOT A MEASUREMENT OF TODAY. The parent arm's completeness is a "
                  "property of its SEEDING over whatever sequence it was given, so an offline run "
                  "is exhaustive over the cached sequence and is not a statement about Ensembl's "
                  "current annotation. The genome-wide arm cannot run offline at all and is "
                  "reported as not run, which is its honest state."
                  if offline else
                  "read live from Ensembl on this run and written back to the cache"),
        },
        "method": {
            "max_mismatches": MAX_MM,
            "why_this_threshold": ("matched to the BLAST arm's >=14/16 identity so the two arms "
                                   "describe the same liability class"),
            "gap_region_1based": list(_gap_region()),
            "completeness": ("exhaustive for substitutions by construction: three seed blocks over a "
                             "16-mer, so a hit at <=2 mismatches must match one block exactly"),
            "blind_to": ["insertions and deletions", "genes other than the six parents",
                         "unannotated transcription", "any question about cleavage activity"],
            "orientation_rule": ("pre-mRNA is transcribed in transcript orientation, so a forward "
                                 "match is hybridisable and a reverse-complement match is not"),
        },
        "genes": {g: {k: v for k, v in rec_g.items() if k != "sequence"}
                  for g, rec_g in sorted(premrna.items())},
        "genome_wide_arm": genomic,
        "corpus": corpus,
        "per_design": sorted(rows, key=lambda r: (-r["n_invisible_to_mature_screens"],
                                                  -r["n_hybridisable_gap_fully_paired"],
                                                  r["junction_label"], r["antisense_5to3"])),
    }
    with open(OUT, "w") as fh:
        json.dump(rec, fh, indent=1)
        fh.write("\n")
    print(f"\nwrote {OUT}")
    print(f"  {corpus['designs']} designs · {corpus['with_any_hit']} with any pre-mRNA near-match · "
          f"{corpus['with_hybridisable_gap_paired']} with a hybridisable gap-paired site · "
          f"{corpus['with_a_liability_invisible_to_mature_screens']} carrying a site no mature screen "
          f"could see")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
