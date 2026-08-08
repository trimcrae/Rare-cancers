#!/usr/bin/env python3
"""
Fusion-junction antisense oligonucleotide (gapmer) design for EWSR1::NR4A3 EMC.

Rationale. The chimeric mRNA's junction is a tumour-specific sequence: no normal
transcript contains the EWSR1-exon -> NR4A3-exon seam. A gapmer ASO whose central
DNA window straddles that seam can direct RNase-H1 cleavage of the fusion transcript
while sparing wild-type EWSR1 and NR4A3 mRNAs (each of which matches only one half of
the oligo). This is a transcript-level modality that needs no druggable protein pocket.

What this does (real, reproducible; sequences fetched from NCBI, nothing invented):
  1. Fetches the RefSeq mRNAs for EWSR1 (NM_005243) and NR4A3 (NM_006981) from NCBI
     E-utilities and extracts their CDS.
  2. Builds the modelled fusion mRNA at the same canonical breakpoint used by
     fusion_neoantigen.py (EWSR1 N-terminal coding fragment :: retained NR4A3 CDS),
     keeping the junction in-frame and FLAGGING the breakpoint as a model assumption.
  3. Tiles candidate gapmers (default 16-mer, 5-6-5 LNA/DNA/LNA architecture; 5-10-5 is the
     common 20-mer template) whose
     central DNA gap spans the junction, i.e. each oligo must draw bases from BOTH
     sides of the seam (that is what makes it fusion-specific).
  4. Filters/annotates each candidate by standard design heuristics: %GC window,
     absence of >=4 consecutive G (G-quadruplex / tox motif), and the count of
     contiguous bases on the shorter side of the junction (specificity margin: the
     more unique bases on each side, the less either parent transcript is engaged).
  5. Verifies the full antisense oligo is NOT a perfect complement to either parent
     mRNA (true junction specificity).

This is a DESIGN tool, not a validated drug. Output oligos are hypotheses to be tested
(knockdown + parental-sparing controls) in EMC cell models. Delivery to tumour is the
unsolved, separate problem and is out of scope.

⛔ REAL-EXON MODE IS mRNA-LEVEL, AND THAT IS NOT A DETAIL. `FUSION_JUNCTION_MODE=real` builds the
chimera from the spliced TRANSCRIPTS (cDNA + exon boundaries in transcript coordinates), not from
the CDSs, because a fusion transcript retains the acceptor exon whole — 5'UTR included — and those
retained bases sit immediately 3' of the seam that the oligo hybridises to. Building this from CDS
concatenation produced two separate wrong answers in one day (see the two-defect block below).

Outputs:
  junction-aso-designs[SUFFIX].json  — the design panel for ONE graded junction
  junction-mrna-frame-audit.json     — `--audit`: every declared breakpoint graded, designing
                                       nothing. Run this FIRST; a panel may only be emitted for a
                                       row this table grades EMITTABLE.
"""

import json
import os
import re
import sys
import time
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "junction-aso-designs.json")

EWSR1_MRNA = "NM_005243"
NR4A3_MRNA = "NM_006981"

# Same modelled breakpoint convention as fusion_neoantigen.py (protein-level):
# EWSR1 kept to residue 264; NR4A3 kept from residue 2. We translate that to mRNA by
# locating the CDS and taking codons. Flagged as an assumption.
EWSR1_KEEP_AA = 264
NR4A3_KEEP_AA_FROM = 2

# Oligo geometry is env-configurable so the SAME tiler runs the 16-mer 5-6-5 (default) OR the common
# 20-mer 5-10-5 layout (OLIGO_LEN=20, WING=5) — the longer gap is the paper's lever to convert
# residual-off-target junctions into clean designs.

# ⛔ AN ENV VAR SET TO THE EMPTY STRING IS SET, AND `os.environ.get(k, default)` WILL NOT SAVE YOU
# (measured 2026-08-06, run 31130625823). `aso-offtarget.yml` passes `OLIGO_LEN: ${{ inputs.oligo_len }}`
# and `WING: ${{ inputs.wing }}`; an unsupplied optional input renders as "", so the var exists and
# `int("")` raised `ValueError: invalid literal for int() with base 10: ''` before a single line of
# design ran. The workflow swallows each command with `|| echo "... failed"`, so the step exited 0
# after ONE SECOND and the run was reported `success` — and then the publish step copied the
# still-on-disk RETRACTED artifacts to `modalities-cache` under a commit message announcing a fresh
# screen. A defaulting bug, a fail-quiet wrapper and a publish step that cannot tell a fresh artifact
# from a stale one compose into a green run that republishes exactly what was retracted.
# `_env_int` treats "" as absent, which is what every caller already meant.
def _env_int(name, default):
    raw = os.environ.get(name)
    return default if raw is None or not raw.strip() else int(raw.strip())


OLIGO_LEN = _env_int("OLIGO_LEN", 16)                # total gapmer length
WING = _env_int("WING", 5)                           # 5-6-5 at len 16; set OLIGO_LEN=20 for 5-10-5
GAP = OLIGO_LEN - 2 * WING

EUTILS = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
          "?db=nuccore&id={acc}&rettype=fasta_cds_na&retmode=text")

COMP = str.maketrans("ACGTacgt", "TGCAtgca")


def revcomp(s):
    return s.translate(COMP)[::-1]


def fetch_cds(acc, retries=4):
    url = EUTILS.format(acc=acc)
    for i in range(retries):
        try:
            print(f"  fetching CDS {acc}", file=sys.stderr)
            with urllib.request.urlopen(url, timeout=60) as r:
                text = r.read().decode()
            # fasta_cds_na returns the CDS nucleotide sequence(s); take the first record
            blocks = [b for b in text.split(">") if b.strip()]
            seq = "".join(l.strip() for l in blocks[0].splitlines()[1:])
            seq = re.sub(r"[^ACGTacgt]", "", seq).upper()
            if seq:
                return seq
        except Exception as e:  # noqa
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"could not fetch {acc}")


def build_fusion_cds(ews_cds, nr4_cds):
    left = ews_cds[: EWSR1_KEEP_AA * 3]              # EWSR1 coding fragment (in-frame)
    right = nr4_cds[(NR4A3_KEEP_AA_FROM - 1) * 3:]   # retained NR4A3 CDS (in-frame)
    return left, right, left + right


def junction_label():
    """Human-readable label + provenance dict for the active breakpoint mode."""
    if os.environ.get("FUSION_JUNCTION_MODE") == "real":
        e = _env_int("EWSR1_EXON_END", 12)
        n = _env_int("NR4A3_EXON_START", 3)
        return f"EWSR1_e{e}__NR4A3_e{n}", {
            "mode": "real_exon_junction_mRNA",
            "source": ("Ensembl MANE/canonical TRANSCRIPT structure (junction_aso.transcript_model): "
                       "spliced cDNA, exon boundaries in transcript coordinates, CDS located inside "
                       "the cDNA. Cross-checked exon-for-exon against the committed "
                       "nr4a3-exon-audit.json before anything is emitted."),
            "EWSR1_exon_end": e, "NR4A3_exon_start": n,
            "note": ("Real in-frame EWSR1::NR4A3 exon junction built at the mRNA level — the acceptor "
                     "exon is taken WHOLE, including any 5'UTR it carries, because that is what a "
                     "fusion transcript contains and what an ASO hybridises to. Self-checked: exon "
                     "lengths sum to the cDNA, the CDS is a unique substring of the cDNA, "
                     "translate(CDS)==Ensembl protein, and the chimeric ORF retains the NR4A3 "
                     "C-terminus. NOT the codon-space modelled reference."),
        }
    return "reference_codon264_from2", {
        "mode": "modelled_reference_codon_space",
        "EWSR1_coding_kept": f"codons 1-{EWSR1_KEEP_AA} (in-frame)",
        "NR4A3_coding_kept": f"from codon {NR4A3_KEEP_AA_FROM} (in-frame)",
        "note": ("Codon-space modelled reference breakpoint (junction_aso.py default; a label of "
                 "convenience, NOT a validated clinical breakpoint)."),
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# ⛔⛔ TWO DEFECTS, ONE SEAM. Read both before touching the real-mode builder below.
#
# DEFECT 1 (found 2026-08-06 by the route framing audit; fixed the same day).
#   The old code did `fb.gene_model(...)["offsets"][n - 2]` — it indexed a table keyed by CODING
#   exon with a TRANSCRIPT exon number. NR4A3 ENST00000395097 has 8 transcript exons of which 1
#   and 2 carry no coding sequence, so the label "NR4A3 exon 3" addressed the THIRD CODING exon
#   (transcript exon 5) instead. MEASURED: the committed seam `TTGTCCGTACAG` sits at NR4A3 CDS
#   nt 1081 = residue 361 — bit-for-bit the `nr4_cds_nt: 1081` / `nr4a3_resumes_at_residue: 361`
#   that `fusion-neoantigen-retraction.json` grades SEAM_NOT_PRODUCED, against a corrected
#   `nr4a3_resume_range_across_plausible_breakpoints` of [1, 1] in `fusion-object-inventory.json`.
#   The EWSR1 side reproduced correctly throughout (EWSR1 exon 1 IS coding, so rank == coding
#   index), which is why nothing caught it: the e7n3 and e12n3 panels agreed with each other and
#   the paper read that agreement as confirmation. Two artifacts agreeing is not evidence when
#   one defect produces both.
#
# DEFECT 2 (found 2026-08-06 in this task, from the SAME committed exon audit, $0, no network).
#   ⚠ THE FIX FOR DEFECT 1 WAS ARITHMETICALLY RIGHT AND STILL COULD NOT REGENERATE THE PANEL.
#   It concatenated CDS to CDS: `nr4_cds[resume_offset(nr4, n)]`, i.e. it resumed NR4A3 at its
#   ATG and DISCARDED the 5'UTR that transcript exon 3 carries ahead of that ATG. A real fusion
#   transcript retains the acceptor exon WHOLE, UTR included — those bases are physically in the
#   mRNA, are read in the donor's frame, and are the bases immediately 3' of the seam that an ASO
#   actually hybridises to. Dropping them is wrong twice over:
#     (a) the reported seam context is wrong for an mRNA-level modality, and
#     (b) the in-frame self-check then fails for every donor whose cut is not a multiple of 3.
#   MEASURED from `nr4a3-exon-audit.json` (committed; no network needed to see this):
#     EWSR1 cut offsets mod 3 — e6 581→2 · e7 793→1 · e8 974→2 · e9 1012→1 · e10 1045→1 ·
#     e11 1164→0 · e12 1294→1 · e13 1417→1 · e14 1580→2.
#   With NR4A3 resuming at CDS nt 0, ONLY e11 is a multiple of 3. So the Defect-1 fix would have
#   RAISED "not in-frame" on **e7n3 and e12n3 — the two junctions the manuscript leads with** —
#   and silently admitted only e11n3, a junction the manuscript does not use. A regeneration run
#   before this was found would have reported the lane as broken for the wrong reason.
#   ⭐ The frame is closed by the acceptor exon's own 5' phase, not by the donor alone. Let U be
#   the number of NR4A3 transcript-exon-3 bases 5' of the ATG; the chimeric ORF is in frame iff
#   (cut + U) % 3 == 0. e7 and e12 are both ≡1, so BOTH are in frame for the same U ≡ 2 (mod 3),
#   which is a PREDICTION this module tests against Ensembl rather than an assumption it makes.
#   U is not knowable from any artifact in this repo — `nr4a3-exon-audit.json` records coding nt
#   per exon only — so it is UNKNOWN here and is measured by the CI fetch.
#
# THE RULE THAT FALLS OUT: a nucleotide-level fusion model for an RNA-targeting modality must be
# built from the TRANSCRIPT (cDNA + exon boundaries in transcript coordinates), never from the
# CDS. `fusion_breakpoints.gene_model` is a CDS/protein instrument and is correct for the
# neoantigen lane, which asks a protein question. It is the wrong instrument for this one.
# ─────────────────────────────────────────────────────────────────────────────────────────────

ENS = "https://rest.ensembl.org"
_TX_CACHE = {}

# ⭐ THE TRANSCRIPT MODEL IS AVAILABLE OFFLINE, AND THAT IS WHY THIS LANE NO LONGER NEEDS THE
# NETWORK TO SAY WHAT ITS SEAM IS (measured 2026-08-06). The two-defect block above states that
# U — the number of NR4A3 transcript-exon-3 bases 5' of the ATG — "is not knowable from any
# artifact in this repo". That was true of `nr4a3-exon-audit.json`, which records coding nt per
# exon only; it was NOT true of the repo. `emc-construct-inputs.json` (fetched 2026-08-03 from
# the same Ensembl REST endpoint, same transcripts, with its own four self-checks recorded and
# all true) carries the spliced cDNA, the CDS, the protein, per-exon lengths and cDNA offsets,
# and `utr5_len` for both genes. From it U is a subtraction, and the frame audit and the design
# panel are a $0 CPU run. What still needs the network is the BLAST/RefSeq screen downstream —
# not the junction.
# ⛔ A CACHE IS NOT A MEASUREMENT OF TODAY. So the source is never silent: it is chosen by
# `TRANSCRIPT_SOURCE` (auto|ensembl|cache), recorded in every artifact this module emits, and
# when a live Ensembl read IS available it is diffed against the committed cache field-for-field
# and RAISES on any disagreement — the cache can therefore only ever agree with the network or
# stop the run, never quietly replace it.
CONSTRUCT_INPUTS = os.path.join(os.path.dirname(__file__), "emc-construct-inputs.json")
TRANSCRIPT_SOURCE = os.environ.get("TRANSCRIPT_SOURCE", "auto").strip().lower() or "auto"
# {symbol: "ensembl" | "ensembl+cache_agreed" | "committed_cache"} — populated as models are built.
TRANSCRIPT_SOURCE_USED = {}


def _self_check_model(model):
    """The three sequence self-checks + the exon-audit provenance gate. All RAISE.

    1. exon lengths sum to len(cdna)          — the exon list really is this transcript's
    2. the CDS occurs EXACTLY ONCE in the cdna — so utr5_len is unambiguous
    3. translate(cds) == the annotated protein — the reading frame is the annotated one
    4. per-exon coding nt reproduce the committed `nr4a3-exon-audit.json` exon-for-exon
    Check 4 is the provenance gate: if the model in hand does not reproduce the exon index this
    repo's corrections were derived from, NOTHING downstream may be emitted, because a design
    panel built on an exon map nobody has graded is worse than no panel. Applied identically to
    a live read and to the committed cache — a cache that skipped the gate would be a second
    source of truth, which is the failure this module exists to correct.
    """
    import fusion_breakpoints as fb
    symbol, cdna, cds = model["symbol"], model["cdna"], model["cds"]
    if sum(model["exon_lens"]) != len(cdna):
        raise RuntimeError(f"{symbol}: exon lengths sum to {sum(model['exon_lens'])} != cdna "
                           f"length {len(cdna)}")
    if cdna.count(cds) != 1:
        raise RuntimeError(f"{symbol}: CDS occurs {cdna.count(cds)} times in the cdna — the 5'UTR "
                           "length would be ambiguous, so no seam may be emitted")
    if cdna.index(cds) != model["utr5_len"]:
        raise RuntimeError(f"{symbol}: utr5_len {model['utr5_len']} != the cdna offset of the CDS "
                           f"{cdna.index(cds)}")
    if fb.translate(cds) != model["protein"].replace("*", "").rstrip("X"):
        raise RuntimeError(f"{symbol}: translate(CDS) != annotated protein")
    _cross_check_against_committed_exon_audit(model)
    return model


def _model_from_committed_cache(symbol):
    """Build the transcript model from `emc-construct-inputs.json` — no network, no assumption.

    Every field returned is a value that file MEASURED from Ensembl on its recorded `_fetched_utc`
    and self-checked at the time; nothing here is defaulted or inferred. Raises if the file, the
    gene, or any needed field is absent — an absent reading is not a reading of absence.
    """
    if not os.path.exists(CONSTRUCT_INPUTS):
        raise RuntimeError("emc-construct-inputs.json is missing — no offline transcript model")
    with open(CONSTRUCT_INPUTS) as fh:
        blob = json.load(fh)
    g = (blob.get("genes") or {}).get(symbol)
    if not g:
        raise RuntimeError(f"{symbol} absent from emc-construct-inputs.json")
    for field in ("transcript", "cdna", "cds", "protein", "utr5_len", "exons"):
        if field not in g:
            raise RuntimeError(f"{symbol}: emc-construct-inputs.json carries no {field!r}")
    # ⚠ NAME THE ASSERTIONS; DO NOT SWEEP EVERY FALSE BOOLEAN. `self_checks` mixes four ASSERTIONS
    # with descriptive facts, and `first_transcript_exon_is_coding: false` is the single most
    # important FACT about NR4A3 in this whole lane — it is the off-by-two's root cause, not a
    # failure. A blanket "any false is a failure" sweep refused the correct record on the strength of
    # the very fact the correction rests on (caught the first time this ran, 2026-08-06).
    required = ("exon_lengths_sum_equals_cdna", "coding_nt_sum_equals_cds",
                "cdna_slice_at_utr5_equals_cds", "cds_translation_equals_protein")
    checks = g.get("self_checks") or {}
    missing = [k for k in required if k not in checks]
    if missing:
        raise RuntimeError(f"{symbol}: emc-construct-inputs.json records no {missing} — an absent "
                           "check is not a passed check")
    bad = [k for k in required if checks[k] is not True]
    if bad:
        raise RuntimeError(f"{symbol}: emc-construct-inputs.json records FAILED self-checks {bad}")
    exon_lens = [e["exon_length_nt"] for e in g["exons"]]
    tx_ends, cum = [], 0
    for L in exon_lens:
        cum += L
        tx_ends.append(cum)
    return {"symbol": symbol, "transcript": g["transcript"], "strand": g.get("strand"),
            "cdna": g["cdna"].upper(), "cds": g["cds"].upper(), "protein": g["protein"],
            "exon_lens": exon_lens, "tx_ends": tx_ends, "utr5_len": g["utr5_len"],
            "n_transcript_exons": len(exon_lens),
            "_fetched_utc": blob.get("_fetched_utc"), "_source_file": os.path.basename(CONSTRUCT_INPUTS)}


def _model_from_ensembl(symbol):
    """Build the transcript model from a live Ensembl REST read. Needs the network."""
    import fusion_breakpoints as fb
    look = fb.get(f"{ENS}/lookup/symbol/homo_sapiens/{symbol}?expand=1")
    tr = next((t for t in look["Transcript"] if t.get("is_canonical") == 1), look["Transcript"][0])
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    exon_lens = [e["end"] - e["start"] + 1 for e in exons]
    tx_ends, cum = [], 0
    for L in exon_lens:
        cum += L
        tx_ends.append(cum)
    cdna = fb.get_text(f"{ENS}/sequence/id/{tr['id']}?type=cdna").replace("\n", "").upper()
    cds = fb.get_text(f"{ENS}/sequence/id/{tr['id']}?type=cds").replace("\n", "").upper()
    protein = fb.get_text(f"{ENS}/sequence/id/{tr['Translation']['id']}?type=protein").replace("\n", "")
    if cdna.count(cds) != 1:                      # utr5 must be unambiguous before we can set it
        raise RuntimeError(f"{symbol}: CDS occurs {cdna.count(cds)} times in the cdna — the 5'UTR "
                           "length would be ambiguous, so no seam may be emitted")
    return {"symbol": symbol, "transcript": tr["id"], "strand": strand, "cdna": cdna, "cds": cds,
            "protein": protein, "exon_lens": exon_lens, "tx_ends": tx_ends,
            "utr5_len": cdna.index(cds), "n_transcript_exons": len(exons)}


def _diff_live_against_cache(live):
    """RAISE if a live Ensembl read disagrees with the committed cache on anything load-bearing.

    This is what keeps the offline path honest: the cache may only ever AGREE with the network or
    stop the run. Ensembl moving under us is a real event (a transcript re-annotation would change
    every seam in this lane), and it must surface as a refusal, never as a silent new number.
    """
    try:
        cached = _model_from_committed_cache(live["symbol"])
    except RuntimeError:
        return "ensembl"                          # nothing committed to compare against
    for field in ("transcript", "cdna", "cds", "exon_lens", "utr5_len"):
        if cached[field] != live[field]:
            a, b = cached[field], live[field]
            raise RuntimeError(
                f"{live['symbol']}: live Ensembl {field!r} disagrees with the committed "
                f"emc-construct-inputs.json (fetched {cached.get('_fetched_utc')}). "
                f"cache={str(a)[:80]!r} live={str(b)[:80]!r}. Every seam this lane has emitted "
                "was derived from the cached value, so a disagreement is a re-annotation, not a "
                "detail — refusing to emit until it is graded.")
    if cached["protein"].replace("*", "").rstrip("X") != live["protein"].replace("*", "").rstrip("X"):
        raise RuntimeError(f"{live['symbol']}: live Ensembl protein disagrees with the committed cache")
    return "ensembl+cache_agreed"


def transcript_model(symbol):
    """mRNA-level model of `symbol`'s canonical transcript — the instrument this module needs.

    Returns cdna (spliced transcript), cds, protein, exon lengths and cumulative exon ends in
    TRANSCRIPT coordinates, and utr5_len (transcript nt 5' of the ATG). Every field is measured;
    nothing is assumed. Source is `TRANSCRIPT_SOURCE`:
      ensembl — live REST read only (raises without network)
      cache   — the committed `emc-construct-inputs.json` only (no network, $0)
      auto    — live read if the network answers, else the committed cache (the default)
    Whichever is used, `_self_check_model` runs on it, so the exon-audit provenance gate is not
    bypassable by choosing a source. A live read is additionally diffed against the cache.
    """
    if symbol in _TX_CACHE:
        return _TX_CACHE[symbol]
    # ⚠ READ THE ENV AT CALL TIME, not only at import. A test or a caller that sets TRANSCRIPT_SOURCE
    # after this module has already been imported by some other test in the same process would
    # otherwise get the import-time value and silently go to the network — which is exactly how the
    # first version of this failed only when run alongside other test modules and passed alone.
    src = (os.environ.get("TRANSCRIPT_SOURCE") or TRANSCRIPT_SOURCE).strip().lower() or "auto"
    if src not in ("auto", "ensembl", "cache"):
        raise RuntimeError(f"TRANSCRIPT_SOURCE={src!r} is not one of auto|ensembl|cache")
    if src == "cache":
        model, used = _model_from_committed_cache(symbol), "committed_cache"
    else:
        # ⛔ THE FALLBACK IS SCOPED TO THE FETCH, AND THE DIFF IS DELIBERATELY OUTSIDE IT. A network
        # failure is not a verdict and may fall back; a live-vs-cache DISAGREEMENT is a verdict and
        # must never be masked by falling back to the very cache it disagrees with. The first version
        # of this put both inside one `try` and re-raised every RuntimeError — which `fusion_breakpoints.get`
        # also raises on a plain 403, so `auto` never fell back at all.
        try:
            model = _model_from_ensembl(symbol)
        except Exception as exc:                  # noqa: BLE001
            if src == "ensembl":
                raise
            print(f"  Ensembl unreachable for {symbol} ({exc}); using the committed cache",
                  file=sys.stderr)
            model, used = _model_from_committed_cache(symbol), "committed_cache"
        else:
            used = _diff_live_against_cache(model)
    _self_check_model(model)
    TRANSCRIPT_SOURCE_USED[symbol] = used
    _TX_CACHE[symbol] = model
    return model


def transcript_source_provenance():
    """What every emitted artifact must carry: which source produced the seam, and when it was read."""
    prov = {"requested": TRANSCRIPT_SOURCE, "used_per_gene": dict(TRANSCRIPT_SOURCE_USED)}
    if any(v == "committed_cache" for v in TRANSCRIPT_SOURCE_USED.values()):
        try:
            with open(CONSTRUCT_INPUTS) as fh:
                prov["committed_cache_fetched_utc"] = json.load(fh).get("_fetched_utc")
        except Exception:                          # noqa: BLE001
            prov["committed_cache_fetched_utc"] = None
        prov["_caveat"] = ("At least one gene was read from the committed cache "
                           "(emc-construct-inputs.json), not from Ensembl today. The cache is a "
                           "dated measurement that passed this module's four self-checks; it is "
                           "not a statement about Ensembl's current annotation.")
    return prov


def coding_nt_per_exon(model):
    """Coding nt contributed by each TRANSCRIPT exon, derived from the transcript model alone."""
    lo, hi = model["utr5_len"], model["utr5_len"] + len(model["cds"])   # [lo, hi) in tx coords
    out, start = [], 0
    for end in model["tx_ends"]:
        out.append(max(0, min(end, hi) - max(start, lo)))
        start = end
    return out


def _cross_check_against_committed_exon_audit(model):
    """Check 4 — the provenance gate. Refuses on ANY disagreement with `nr4a3-exon-audit.json`."""
    path = os.path.join(os.path.dirname(__file__), "nr4a3-exon-audit.json")
    if not os.path.exists(path):                     # the gate cannot run; say so, do not pass
        raise RuntimeError("nr4a3-exon-audit.json is missing — the exon-index provenance gate "
                           "cannot run, so no seam may be emitted")
    with open(path) as fh:
        audit = json.load(fh)
    ref = audit.get(model["symbol"])
    if not ref:
        raise RuntimeError(f"{model['symbol']} absent from nr4a3-exon-audit.json")
    if ref["transcript"] != model["transcript"]:
        raise RuntimeError(f"{model['symbol']}: Ensembl canonical is {model['transcript']} but the "
                           f"committed audit graded {ref['transcript']} — different exon maps")
    got = coding_nt_per_exon(model)
    want = [e["coding_nt_in_exon"] for e in ref["exons"]]
    if got != want:
        raise RuntimeError(f"{model['symbol']}: per-exon coding nt {got} != committed audit {want}")
    if len(model["protein"].replace("*", "").rstrip("X")) != ref["protein_length"]:
        raise RuntimeError(f"{model['symbol']}: protein length disagrees with the committed audit")


def exon_tx_end(model, rank):
    """Transcript nt through the END of transcript exon `rank` (1-based)."""
    if not 1 <= rank <= len(model["tx_ends"]):
        raise ValueError(f"{model['symbol']}: no transcript exon {rank} "
                         f"(has {len(model['tx_ends'])})")
    return model["tx_ends"][rank - 1]


def exon_tx_start(model, rank):
    """0-based transcript index at which transcript exon `rank` BEGINS."""
    if not 1 <= rank <= len(model["tx_ends"]):
        raise ValueError(f"{model['symbol']}: no transcript exon {rank} "
                         f"(has {len(model['tx_ends'])})")
    return 0 if rank == 1 else model["tx_ends"][rank - 2]


def mrna_junction(ews, nr4, e_end, n_start):
    """Build the chimeric mRNA for EWSR1 exon `e_end` :: NR4A3 exon `n_start` and grade it.

    Returns a dict that is a READING, never an assertion: `in_frame` may be False and
    `nr4a3_first_residue` may be a value no plausible breakpoint produces. `main()` refuses to
    emit designs on either — but the grading itself is always reported, because a refusal that
    cannot say what it refused is the failure mode this whole module is a correction for.
    """
    import fusion_breakpoints as fb
    left = ews["cdna"][:exon_tx_end(ews, e_end)]
    right = nr4["cdna"][exon_tx_start(nr4, n_start):]
    fusion = left + right
    orf = fusion[ews["utr5_len"]:]                 # the chimeric ORF starts at EWSR1's own ATG
    prot = fb.translate(orf)
    in_frame = prot.endswith(nr4["protein"][-100:])
    # where the acceptor exon's coding actually starts, in that exon's own transcript coordinates
    coding = coding_nt_per_exon(nr4)
    acceptor_utr = max(0, nr4["utr5_len"] - exon_tx_start(nr4, n_start))
    nr4_cds_nt = max(0, exon_tx_start(nr4, n_start) - nr4["utr5_len"])
    first_res = (nr4_cds_nt // 3) + 1 if coding[n_start - 1] else None
    ews_coding_nt = sum(coding_nt_per_exon(ews)[:e_end])
    return {
        "junction_label": f"EWSR1_e{e_end}__NR4A3_e{n_start}",
        "EWSR1_exon_end": e_end, "NR4A3_exon_start": n_start,
        "ewsr1_coding_nt_through_cut": ews_coding_nt,
        "ewsr1_last_whole_residue": ews_coding_nt // 3,
        "ewsr1_coding_phase": ews_coding_nt % 3,
        "nr4a3_acceptor_exon_is_coding": bool(coding[n_start - 1]),
        "nr4a3_acceptor_exon_5utr_nt_retained": acceptor_utr,
        "nr4a3_cds_nt_at_resume": nr4_cds_nt,
        "nr4a3_first_residue": first_res,
        "frame_sum_mod3": (ews_coding_nt + acceptor_utr) % 3,
        "in_frame": bool(in_frame),
        "chimeric_protein_length": len(prot),
        "junction_context_mRNA": left[-12:] + "|" + right[:12],
        "_left": left, "_right": right, "_fusion": fusion,
    }


# The corrected resume residues a plausible breakpoint can produce. ONE HOME: read out of
# `fusion-object-inventory.json` at run time, never typed here — that file is the graded record and
# a copy of its numbers in this module is exactly how the retracted seam survived.
def plausible_nr4a3_resume_residues():
    path = os.path.join(os.path.dirname(__file__), "fusion-object-inventory.json")
    with open(path) as fh:
        inv = json.load(fh)
    lo, hi = inv["inventory"]["excluded_span"][
        "nr4a3_resume_range_across_plausible_breakpoints"]
    return lo, hi


def build_parents_and_fusion():
    """Return (ews_parent, nr4_parent, left, right, fusion) for either the codon-space modelled
    reference breakpoint (default) or a REAL exon-level junction (env-selected), and set the
    module parent globals used by design()'s specificity check.

    Real mode (FUSION_JUNCTION_MODE=real) is built at the mRNA level — see the two-defect block
    above. The parents used for the specificity substring test become the full cDNAs rather than
    the CDSs, which is both more correct (an ASO meets the whole transcript, UTRs included) and
    strictly stricter (a superset)."""
    global EWSR1_full, NR4A3_full
    if os.environ.get("FUSION_JUNCTION_MODE") == "real":
        e_end = _env_int("EWSR1_EXON_END", 12)
        n_start = _env_int("NR4A3_EXON_START", 3)
        ews = transcript_model("EWSR1")
        nr4 = transcript_model("NR4A3")
        j = mrna_junction(ews, nr4, e_end, n_start)
        if not j["nr4a3_acceptor_exon_is_coding"]:
            raise RuntimeError(
                f"NR4A3 transcript exon {n_start} carries no coding sequence — refusing to slide "
                "onto a neighbour (this is Defect 1, and it is what produced the retracted seam)")
        lo, hi = plausible_nr4a3_resume_residues()
        if not (lo <= j["nr4a3_first_residue"] <= hi):
            raise RuntimeError(
                f"EWSR1 e{e_end} :: NR4A3 e{n_start} resumes NR4A3 at residue "
                f"{j['nr4a3_first_residue']}, outside the corrected plausible range [{lo}, {hi}] "
                "in fusion-object-inventory.json — this is the exact grade "
                "fusion-neoantigen-retraction.json calls SEAM_NOT_PRODUCED. Refusing to emit.")
        if not j["in_frame"]:
            raise RuntimeError(
                f"EWSR1 e{e_end} :: NR4A3 e{n_start} is not in-frame at the mRNA level "
                f"(EWSR1 coding nt {j['ewsr1_coding_nt_through_cut']} phase "
                f"{j['ewsr1_coding_phase']} + acceptor 5'UTR "
                f"{j['nr4a3_acceptor_exon_5utr_nt_retained']} nt => "
                f"(cut+UTR) mod 3 = {j['frame_sum_mod3']}, must be 0); NR4A3 C-terminus not "
                "retained. This is a READING about that exon pair, not a code failure.")
        globals()["LAST_JUNCTION"] = j
        EWSR1_full, NR4A3_full = ews["cdna"], nr4["cdna"]
        return ews["cdna"], nr4["cdna"], j["_left"], j["_right"], j["_fusion"]
    # default: codon-space modelled reference breakpoint (NCBI RefSeq CDS)
    ews_cds = fetch_cds(EWSR1_MRNA)
    nr4_cds = fetch_cds(NR4A3_MRNA)
    EWSR1_full, NR4A3_full = ews_cds, nr4_cds
    left, right, fusion = build_fusion_cds(ews_cds, nr4_cds)
    return ews_cds, nr4_cds, left, right, fusion


def gc(s):
    return round(100 * (s.count("G") + s.count("C")) / len(s), 1) if s else 0


def design(left, right, fusion):
    j = len(left)  # first index of NR4A3 base in the fused string
    oligos = []
    for start in range(0, len(fusion) - OLIGO_LEN + 1):
        end = start + OLIGO_LEN
        gap_start, gap_end = start + WING, end - WING  # central DNA gap [gap_start, gap_end)
        # the junction must fall inside the DNA gap (RNase-H cleaves there)
        if not (gap_start < j < gap_end):
            continue
        target = fusion[start:end]            # sense (mRNA) window
        oligo = revcomp(target)               # antisense oligo, 5'->3'
        left_bases = j - start                # mRNA bases from EWSR1 side
        right_bases = end - j                 # mRNA bases from NR4A3 side
        # GAP-LEVEL discrimination (red-team F3): RNase-H1 cleaves only where the central DNA
        # gap [gap_start, gap_end) is base-paired, so fusion-vs-parent discrimination is set by
        # junction-unique bases INSIDE the gap on each side, not across the whole 16-mer. The
        # oligo-wide specificity_margin (min(left_bases, right_bases)) OVERSTATES true discrimination
        # (a parent can share up to WING wing bases plus part of the gap). Report the gap-level
        # margin as the honest operative metric.
        gap_left = j - gap_start              # junction-unique EWSR1 bases within the gap
        gap_right = gap_end - j               # junction-unique NR4A3 bases within the gap
        gap_margin = min(gap_left, gap_right)
        # specificity: oligo must not perfectly complement either parent transcript
        spec_ok = (target not in EWSR1_full) and (target not in NR4A3_full)
        oligos.append({
            "antisense_5to3": oligo,
            "target_mRNA_5to3": target,
            "architecture": f"{WING}-{GAP}-{WING} (LNA-DNA-LNA)",
            "junction_offset_in_oligo": OLIGO_LEN - (j - start),  # from 5' of antisense
            "bases_from_EWSR1": left_bases,
            "bases_from_NR4A3": right_bases,
            "specificity_margin": min(left_bases, right_bases),
            "gap_bases_from_EWSR1": gap_left,
            "gap_bases_from_NR4A3": gap_right,
            "gap_specificity_margin": gap_margin,          # operative metric (junction-unique bases in the gap)
            "gap_centered": gap_margin >= 2,               # >=2 junction-unique gap bases each side
            "gc_percent": gc(target),
            "has_G4_motif": bool(re.search("G{4,}", target)),
            "fusion_specific": spec_ok,
        })
    # rank: gap-centred discrimination first (the operative metric), then oligo-wide margin,
    # then mid GC (40-60), then no G4. Prefers designs whose junction-unique bases fall inside
    # the catalytic gap on both sides (red-team F3 gap-centred design rule).
    def score(o):
        gc_pen = abs(o["gc_percent"] - 50)
        return (o["gap_specificity_margin"], o["specificity_margin"], -gc_pen,
                0 if not o["has_G4_motif"] else -1)
    oligos.sort(key=score, reverse=True)
    return oligos


# module-level full mRNAs for the specificity check (populated in main)
EWSR1_full = ""
NR4A3_full = ""
# The measured grading of the junction the last real-mode build accepted. None in default mode.
LAST_JUNCTION = None


# Declared breakpoint windows. ONE HOME: read out of `fusion_breakpoints`, never re-typed here.
def declared_windows():
    import fusion_breakpoints as fb
    return list(fb.EWSR1_EXON_WINDOW), list(fb.NR4A3_EXON_WINDOW)


#: The grade that means "a panel may be built on this row". Named once so no consumer types it.
EMITTABLE = "EMITTABLE"


def grade_junction(j, lo, hi):
    """`(grade, why)` for ONE `mrna_junction` reading, against the plausible resume range.

    ⛔ EXTRACTED SO THERE IS EXACTLY ONE GRADER (rule 1). It was inline in `audit_window` while the
    neoantigen lane was being rebuilt on the same transcript model, and a second copy of these four
    branches in `fusion_breakpoints.py` would have been a second definition of "in frame" — which
    is the shape of the defect both lanes are a correction for. The ORDER matters and is part of
    the contract: a non-coding acceptor has no resume residue to range-check, and a row outside the
    plausible range must not be re-explained as a frame problem.
    """
    if not j["nr4a3_acceptor_exon_is_coding"]:
        return "NON_CODING_ACCEPTOR", "acceptor exon carries no CDS"
    if not (lo <= j["nr4a3_first_residue"] <= hi):
        return "SEAM_NOT_PRODUCED", (
            f"NR4A3 resumes at residue {j['nr4a3_first_residue']}, outside the "
            f"corrected plausible range [{lo}, {hi}]")
    if not j["in_frame"]:
        # ⚠ TWO DIFFERENT FAILURES WEAR THIS GRADE AND THEY MUST NOT RENDER ALIKE.
        # frame_sum_mod3 != 0 is a REGISTER mismatch: the donor cut and the acceptor exon's
        # 5' phase do not compose. frame_sum_mod3 == 0 with the C-terminus still missing is
        # a PREMATURE STOP — the register is right and something in the read-through
        # terminates translation before NR4A3's own C-terminus. The second is a biological
        # statement about that exon pair; the first is arithmetic. Collapsing them would
        # reproduce, in the replacement, the exact ambiguity that let the e11 self-check be
        # written off as an exon-boundary to-verify.
        return "OUT_OF_FRAME", (
            (f"frame register mismatch: (EWSR1 coding nt "
             f"{j['ewsr1_coding_nt_through_cut']} + acceptor 5'UTR "
             f"{j['nr4a3_acceptor_exon_5utr_nt_retained']}) mod 3 = {j['frame_sum_mod3']}, "
             "must be 0")
            if j["frame_sum_mod3"] else
            (f"frame register is correct (mod 3 = 0) but the NR4A3 C-terminus is not "
             f"reached — a stop codon terminates the chimeric ORF after "
             f"{j['chimeric_protein_length']} aa"))
    return EMITTABLE, "in frame, resume residue inside the corrected range"


def graded_window(ews=None, nr4=None, keep_sequences=False):
    """Grade EVERY declared breakpoint at the mRNA level. One row per exon pair, no omissions.

    ⛔ EVERY PAIR GETS A ROW, INCLUDING THE REFUSALS. The CDS-coordinate predecessor
    (`fusion_breakpoints.main` before 2026-08-07) skipped a non-coding acceptor to STDERR and left
    no row at all, so "NR4A3 exon 2 was considered and refused" and "NR4A3 exon 2 was never
    considered" rendered identically in the artifact — which is an absent reading masquerading as a
    reading of absence (CLAUDE.md §4).

    `keep_sequences=True` retains the `_left`/`_right`/`_fusion` strings a caller needs to build a
    chimeric protein; the audit table drops them because a table is not a sequence store.
    """
    ews = ews or transcript_model("EWSR1")
    nr4 = nr4 or transcript_model("NR4A3")
    lo, hi = plausible_nr4a3_resume_residues()
    e_win, n_win = declared_windows()
    rows = []
    for e in e_win:
        for n in n_win:
            try:
                j = mrna_junction(ews, nr4, e, n)
            except Exception as exc:                      # noqa — a refusal is a reading
                rows.append({"junction_label": f"EWSR1_e{e}__NR4A3_e{n}",
                             "EWSR1_exon_end": e, "NR4A3_exon_start": n,
                             "grade": "UNREADABLE", "why": str(exc)})
                continue
            if not keep_sequences:
                j = {k: v for k, v in j.items() if not k.startswith("_")}
            j["grade"], j["why"] = grade_junction(j, lo, hi)
            rows.append(j)
    return rows


def audit_window():
    """Grade EVERY declared breakpoint at the mRNA level and emit the table, designing nothing.

    This is the diagnostic the lane did not have. It answers, per exon pair and from measured
    Ensembl sequence: is the acceptor exon coding, where does NR4A3 resume, how many acceptor
    5'UTR bases the fusion retains, whether the chimeric ORF is in frame, and what the real mRNA
    seam is. A design panel may be emitted only for a row this table grades EMITTABLE.
    """
    ews = transcript_model("EWSR1")
    nr4 = transcript_model("NR4A3")
    lo, hi = plausible_nr4a3_resume_residues()
    rows = graded_window(ews, nr4)
    out = os.path.join(os.path.dirname(__file__), "junction-mrna-frame-audit.json")
    res = {
        "_title": "EWSR1::NR4A3 chimeric-mRNA junction audit at the CORRECTED exon index",
        # ⚠ The cost line must describe THIS run, not the run the author had in mind. It read
        # "a GitHub-hosted CPU runner and two Ensembl reads" on an audit that made no network call
        # at all (2026-08-06) — a small lie, in the field a reader checks to see what was paid for.
        "_cost": ("$0 — CPU only, no GPU and no rental. Inputs: "
                  + ("the committed emc-construct-inputs.json cache, no network call"
                     if all(v == "committed_cache" for v in TRANSCRIPT_SOURCE_USED.values())
                     else "live Ensembl reads")),
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_what_this_is": (
            "The instrument the ASO lane was missing. `fusion_breakpoints.gene_model` is a "
            "CDS/protein instrument — correct for the neoantigen lane, wrong for an RNA-targeting "
            "modality, because it cannot see the acceptor exon's 5'UTR, which a fusion transcript "
            "retains and an ASO hybridises to. Every row here is measured from the spliced cDNA."),
        "_limits": [
            "Exon arithmetic and sequence composition only. No potency, no knockdown, no delivery, "
            "no tolerability and no clinical claim is made or implied.",
            "Canonical transcripts only. A different transcript gives a different exon map, and EMC "
            "breakpoints are reported against specific transcripts.",
            "Which exon pair a given PATIENT carries is not decidable from exon structure and is "
            "not decided here.",
        ],
        "transcripts": {g["symbol"]: {"transcript": g["transcript"], "cdna_nt": len(g["cdna"]),
                                      "cds_nt": len(g["cds"]), "utr5_nt": g["utr5_len"],
                                      "protein_aa": len(g["protein"].replace("*", "").rstrip("X")),
                                      "n_transcript_exons": g["n_transcript_exons"]}
                        for g in (ews, nr4)},
        "_transcript_source": transcript_source_provenance(),
        "plausible_nr4a3_resume_range": [lo, hi],
        "_plausible_range_source": ("fusion-object-inventory.json -> reactive_residue_inventory."
                                    "excluded_span.nr4a3_resume_range_across_plausible_breakpoints"),
        "n_rows": len(rows),
        "grade_counts": {g: sum(1 for r in rows if r.get("grade") == g)
                         for g in sorted({r.get("grade") for r in rows})},
        "rows": rows,
    }
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", out, file=sys.stderr)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))
    for r in rows:
        print(f"  {r['junction_label']:<24} {r.get('grade'):<19} "
              f"resume_res={r.get('nr4a3_first_residue')} "
              f"utr={r.get('nr4a3_acceptor_exon_5utr_nt_retained')} "
              f"in_frame={r.get('in_frame')} seam={r.get('junction_context_mRNA')}")
    return res


def main():
    if "--audit" in sys.argv:
        audit_window()
        return
    ews, nr4, left, right, fusion = build_parents_and_fusion()
    oligos = design(left, right, fusion)
    label, prov = junction_label()
    suffix = os.environ.get("OUT_SUFFIX", "")
    out = os.path.join(os.path.dirname(__file__), f"junction-aso-designs{suffix}.json")

    result = {
        "_note": "Fusion-junction gapmer ASO designs (RNase-H1 mechanism). DESIGN ONLY "
                 "— hypotheses for wet-lab knockdown testing; not a validated drug.",
        "_breakpoint_model": {
            # ⛔ THIS FLAG WAS INVERTED BY THE DEFECT-1 FIX AND NOBODY NOTICED (found 2026-08-08).
            # It was written as `prov["mode"] != "real_exon_junction"`. When the corrected builder
            # renamed its mode to `real_exon_junction_mRNA` -- because the junction moved from CDS
            # to mRNA coordinates -- the comparison stopped matching, so `assumption` became True
            # for the CORRECTED artifacts and had been False for the RETRACTED ones. The flag whose
            # job is to say "this breakpoint is a model, not a measurement" was therefore claiming
            # LESS confidence in the re-derived panels than in the withdrawn ones, and 7 of the 13
            # unbannered retracted artifacts on `modalities-cache` carry `"assumption": false` on
            # exactly this arithmetic. A string equality against a name that later changed: the
            # rename was correct, the comparison was not updated with it, and nothing compared the
            # flag to anything. Anchored to the family prefix so the next rename cannot re-invert it.
            "assumption": not prov["mode"].startswith("real_exon_junction"),
            "junction_label": label,
            "EWSR1_mRNA": EWSR1_MRNA, "NR4A3_mRNA": NR4A3_MRNA,
            "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
            "caveat": "Re-run with a patient's sequenced fusion transcript for clinical design.",
            "_transcript_source": transcript_source_provenance(),
            **prov,
            # The measured grading of the accepted junction — present ONLY in real mode, and only
            # because every gate in `build_parents_and_fusion` passed. A reader must be able to see
            # WHICH seam these designs are for without re-deriving it, which is the whole lesson of
            # the retraction: the old artifacts carried a junction LABEL and no graded offsets, so
            # the wrong seam was invisible in the file that depended on it.
            **({"measured_junction": {k: v for k, v in LAST_JUNCTION.items()
                                      if not k.startswith("_")}} if LAST_JUNCTION else {}),
        },
        "oligo_length": OLIGO_LEN,
        "architecture": f"{WING}-{GAP}-{WING}",
        "n_candidates": len(oligos),
        "n_fusion_specific": sum(1 for o in oligos if o["fusion_specific"]),
        "n_gap_centered": sum(1 for o in oligos if o["fusion_specific"] and o["gap_centered"]),
        "_gap_margin_note": ("gap_specificity_margin = junction-unique bases INSIDE the 6-nt "
                             "catalytic gap on the shorter side; it is the operative "
                             "fusion-vs-parent discriminator (RNase-H cleaves only across the "
                             "gap). The oligo-wide specificity_margin overstates discrimination "
                             "(red-team F3). gap_centered = >=2 unique gap bases each side."),
        "top_designs": oligos[:12],
    }
    with open(out, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", out, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "top_designs"}, indent=2))


if __name__ == "__main__":
    main()
