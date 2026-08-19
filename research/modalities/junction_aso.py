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
        # ⛔ THE LABEL MUST FOLLOW `DONOR_GENE`, AND GETTING THIS WRONG WOULD BE WORSE THAN THE
        # ORIGINAL LIMITATION. A TAF15 screen emitted under an `EWSR1_e…` label is not a missing
        # result, it is a MISATTRIBUTED one — the exact shape of the 2026-08-06 retraction, where a
        # panel carried a junction label its sequence did not match and the mismatch was invisible
        # in the file that depended on it.
        # ⛔⛔ REAL MODE REFUSES TO GUESS A BREAKPOINT (2026-08-19). These three read
        # `EWSR1`, `12` and `3` by default — the lead junction — so `FUSION_JUNCTION_MODE=real`
        # with nothing else set did not fail. It silently emitted a complete, correctly
        # self-labelled panel for `EWSR1_e12__NR4A3_e3`, and all five screens then ran happily on
        # it. A blind order-walkthrough hit this trying to design for a patient's own breakpoint:
        # the paper names only `FUSION_JUNCTION_MODE=real`, so following it hands a laboratory
        # SOMEBODY ELSE'S REAGENT under its own junction's name. The comment above already says a
        # misattributed panel is the exact shape of the 2026-08-06 retraction; the default was the
        # remaining way to produce one. A default is safe only where getting it wrong is cheap.
        donor = (os.environ.get("DONOR_GENE") or "").strip()
        e_raw = os.environ.get("EWSR1_EXON_END") or os.environ.get("DONOR_EXON_END") or ""
        n_raw = os.environ.get("NR4A3_EXON_START") or ""
        missing = [name for name, val in (("DONOR_GENE", donor),
                                          ("DONOR_EXON_END", e_raw.strip()),
                                          ("NR4A3_EXON_START", n_raw.strip())) if not val]
        if missing:
            raise SystemExit(
                "FUSION_JUNCTION_MODE=real needs the breakpoint declared and "
                f"{', '.join(missing)} {'is' if len(missing) == 1 else 'are'} unset. There is no "
                "default breakpoint: one would emit the lead junction's panel under whatever "
                "junction you believe you are designing for. Set all three, e.g.\n"
                "  FUSION_JUNCTION_MODE=real DONOR_GENE=TCF12 DONOR_EXON_END=5 "
                "NR4A3_EXON_START=3 python3 junction_aso.py\n"
                "Run with --audit first: a panel may only be emitted for a pair that grades "
                "EMITTABLE. A non-coding acceptor additionally needs "
                "PUBLISHED_BREAKPOINT_JUNCTION=1 and a whitelist entry.")
        e = int(e_raw.strip())
        n = int(n_raw.strip())
        # ⛔ THE NOTE BELOW SAYS "Real in-frame …", AND FOR A WAIVED PUBLISHED BREAKPOINT THAT WOULD
        # BE FALSE IN THE ONE FIELD A READER USES TO SEE WHAT WAS BUILT. Both whitelisted seams are
        # excluded from the panel precisely BECAUSE the chimeric ORF does not compose (no CDS in the
        # acceptor exon, or an out-of-frame register), so a provenance block asserting the opposite
        # would be the artifact contradicting its own `measured_junction`. Resolved here from the
        # same whitelist the builder's waiver comes from, so the two cannot drift apart.
        pub = (published_noncoding_acceptor_junctions().get((donor, e, "NR4A3", n))
               if published_breakpoint_opt_in() else None)
        return f"{donor}_e{e}__NR4A3_e{n}", {
            "mode": "real_exon_junction_mRNA",
            "source": ("Ensembl MANE/canonical TRANSCRIPT structure (junction_aso.transcript_model): "
                       "spliced cDNA, exon boundaries in transcript coordinates, CDS located inside "
                       "the cDNA. Cross-checked exon-for-exon against the committed "
                       "nr4a3-exon-audit.json before anything is emitted — ⚠ for EWSR1 and NR4A3 "
                       "only; a non-EWSR1 donor rests on the weaker construct-inputs gate, and "
                       "`provenance_gate` below records which one actually ran."),
            "donor_gene": donor,
            "provenance_gate": dict(PROVENANCE_GATE_USED),
            "EWSR1_exon_end": e, "donor_exon_end": e, "NR4A3_exon_start": n,
            **({"published_breakpoint": {
                "transcript_type": pub["transcript_type"],
                "excluded_from_the_manuscript_panel_by": pub["excluded_from_the_panel_by"],
                "n_independent_sources": pub["n_independent_sources"],
                "evidence": list(pub["evidence"]),
                "one_home_for_the_evidence": pub["one_home_for_the_evidence"]}} if pub else {}),
            "note": ((f"Real {donor}::NR4A3 exon junction built at the mRNA level, at a PUBLISHED "
                      f"breakpoint the manuscript's panel excludes by a protein-level filter "
                      f"({pub['excluded_from_the_panel_by']}) — the acceptor exon is taken WHOLE, "
                      "including any 5'UTR it carries, because that is what a fusion transcript "
                      "contains and what an ASO hybridises to. Self-checked: exon lengths sum to "
                      "the cDNA, the CDS is a unique substring of the cDNA, "
                      "translate(CDS)==Ensembl protein. ⛔ THE CHIMERIC ORF IS **NOT** ASSERTED TO "
                      "RETAIN THE NR4A3 C-TERMINUS AND IS NOT ASSERTED TO BE IN FRAME: that is the "
                      "exclusion this junction is admitted in spite of, because an RNase-H1 gapmer "
                      "cleaves the transcript rather than the protein. NOT the codon-space "
                      "modelled reference.")
                     if pub else
                     (f"Real in-frame {donor}::NR4A3 exon junction built at the mRNA level — the acceptor "
                      "exon is taken WHOLE, including any 5'UTR it carries, because that is what a "
                      "fusion transcript contains and what an ASO hybridises to. Self-checked: exon "
                      "lengths sum to the cDNA, the CDS is a unique substring of the cDNA, "
                      "translate(CDS)==Ensembl protein, and the chimeric ORF retains the NR4A3 "
                      "C-terminus. NOT the codon-space modelled reference.")),
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


#: {symbol: "graded_exon_audit" | "construct_inputs_self_checks_only"} — which provenance gate
#: actually ran for each gene. Every artifact that designs on a partner MUST carry this, because
#: the two gates are not equally strong and a reader cannot tell them apart from a seam alone.
PROVENANCE_GATE_USED = {}


def _cross_check_against_committed_exon_audit(model):
    """Check 4 — the provenance gate. Refuses on ANY disagreement with `nr4a3-exon-audit.json`.

    ⛔ THE AUDIT GRADES TWO GENES, AND THE OTHER PARTNERS ARE NOT A LOOPHOLE. `nr4a3-exon-audit.json`
    covers NR4A3 and EWSR1 — the two genes the 2026-08-06 off-by-two correction was derived against.
    TAF15, TCF12 and FUS have no graded exon index in this repository, so for them this gate CANNOT
    RUN. It would be trivial, and wrong, to let an ungraded gene fall through a `.get()` and design
    anyway: that is precisely the shape of the defect this function exists to catch, and it would be
    silent. Instead the weaker gate that IS available runs — `emc-construct-inputs.json`'s own four
    recorded self-checks, already required by `_model_from_committed_cache`, plus the three sequence
    checks in `_self_check_model` — and WHICH gate ran is recorded per gene in `PROVENANCE_GATE_USED`
    and carried into every artifact. An absent reading is never a reading of absence (CLAUDE.md §4);
    it is an absent reading that says its own name.
    """
    path = os.path.join(os.path.dirname(__file__), "nr4a3-exon-audit.json")
    if not os.path.exists(path):                     # the gate cannot run; say so, do not pass
        raise RuntimeError("nr4a3-exon-audit.json is missing — the exon-index provenance gate "
                           "cannot run, so no seam may be emitted")
    with open(path) as fh:
        audit = json.load(fh)
    ref = audit.get(model["symbol"])
    if not ref:
        PROVENANCE_GATE_USED[model["symbol"]] = "construct_inputs_self_checks_only"
        return
    PROVENANCE_GATE_USED[model["symbol"]] = "graded_exon_audit"
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


def mrna_junction_generic(donor, acceptor, d_end, a_start):
    """Build the chimeric mRNA for `donor` exon `d_end` :: `acceptor` exon `a_start` and grade it.

    ⭐ DONOR-GENERIC SINCE 2026-08-12, AND NOTHING ABOUT THE ARITHMETIC CHANGED TO MAKE IT SO.
    Every quantity below was already read out of the two transcript models — `utr5_len`, the exon
    length vector, the CDS, the annotated protein — and the only thing that was ever EWSR1-specific
    was the name typed into the label and the key prefixes. EMC's second-commonest fusion is
    TAF15::NR4A3, and TAF15 patients are the ones with zero reported responses to the only systemic
    therapy with activity in this disease (`emc-fusion-partner-pooling.json`), so a design lane that
    could not address any partner but EWSR1 was excluding, by a hard-coded string, the subgroup with
    the worst options. `mrna_junction` below is the unchanged EWSR1 face of this function.

    Returns a dict that is a READING, never an assertion: `in_frame` may be False and
    `nr4a3_first_residue` may be a value no plausible breakpoint produces. `main()` refuses to
    emit designs on either — but the grading itself is always reported, because a refusal that
    cannot say what it refused is the failure mode this whole module is a correction for.
    """
    import fusion_breakpoints as fb
    left = donor["cdna"][:exon_tx_end(donor, d_end)]
    right = acceptor["cdna"][exon_tx_start(acceptor, a_start):]
    fusion = left + right
    orf = fusion[donor["utr5_len"]:]               # the chimeric ORF starts at the DONOR's own ATG
    prot = fb.translate(orf)
    in_frame = prot.endswith(acceptor["protein"][-100:])
    # where the acceptor exon's coding actually starts, in that exon's own transcript coordinates
    coding = coding_nt_per_exon(acceptor)
    acceptor_utr = max(0, acceptor["utr5_len"] - exon_tx_start(acceptor, a_start))
    acc_cds_nt = max(0, exon_tx_start(acceptor, a_start) - acceptor["utr5_len"])
    first_res = (acc_cds_nt // 3) + 1 if coding[a_start - 1] else None
    donor_coding_nt = sum(coding_nt_per_exon(donor)[:d_end])
    ds, acs = donor["symbol"], acceptor["symbol"]
    return {
        "junction_label": f"{ds}_e{d_end}__{acs}_e{a_start}",
        "donor_symbol": ds, "acceptor_symbol": acs,
        "donor_exon_end": d_end, "acceptor_exon_start": a_start,
        "donor_coding_nt_through_cut": donor_coding_nt,
        "donor_last_whole_residue": donor_coding_nt // 3,
        "donor_coding_phase": donor_coding_nt % 3,
        # ⚠ The acceptor keys keep the `nr4a3_` prefix even though this function is generic. That is
        # deliberate and is not sloppiness: in EMC the acceptor is ALWAYS NR4A3 — the disease is
        # defined by NR4A3 rearrangement, the partner is what varies — and every consumer, grader
        # and committed artifact in this lane keys on these names. Renaming them would fork the
        # grade vocabulary for zero new capability.
        "nr4a3_acceptor_exon_is_coding": bool(coding[a_start - 1]),
        "nr4a3_acceptor_exon_5utr_nt_retained": acceptor_utr,
        "nr4a3_cds_nt_at_resume": acc_cds_nt,
        "nr4a3_first_residue": first_res,
        "frame_sum_mod3": (donor_coding_nt + acceptor_utr) % 3,
        "in_frame": bool(in_frame),
        "chimeric_protein_length": len(prot),
        "junction_context_mRNA": left[-12:] + "|" + right[:12],
        "_left": left, "_right": right, "_fusion": fusion,
    }


def mrna_junction(ews, nr4, e_end, n_start):
    """The EWSR1::NR4A3 face of `mrna_junction_generic` — same reading, legacy key names kept.

    Every existing consumer and test in this lane keys on `EWSR1_exon_end` / `ewsr1_coding_phase`,
    and those artifacts are the ones the 2026-08-06 retraction was resolved against. So the keys
    stay, as ALIASES of the generic ones rather than as a second computation — one builder, one
    grader (rule 1).
    """
    j = mrna_junction_generic(ews, nr4, e_end, n_start)
    j["EWSR1_exon_end"] = j["donor_exon_end"]
    j["NR4A3_exon_start"] = j["acceptor_exon_start"]
    j["ewsr1_coding_nt_through_cut"] = j["donor_coding_nt_through_cut"]
    j["ewsr1_last_whole_residue"] = j["donor_last_whole_residue"]
    j["ewsr1_coding_phase"] = j["donor_coding_phase"]
    return j


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


# ═════════════════════════════════════════════════════════════════════════════════════════════
# ⛔⛔ THE PUBLISHED-BREAKPOINT WHITELIST — the ONLY exception to the acceptor guards below, and it
# lives HERE, beside the guards it excepts, so the two can never be separated.
#
# The guards in `build_parents_and_fusion` exist because code once slid onto a neighbouring exon and
# designed against a seam no patient has ("this is Defect 1, and it is what produced the retracted
# seam"). They see an EXON INDEX and nothing else, so two different things wear the same grade:
#     (a) a coordinate slip onto NR4A3 exon 2 when exon 3 was meant  → still a defect, still raises;
#     (b) a patient whose transcript genuinely joins NR4A3 exon 2    → a target, and the guard
#         cannot tell (a) from (b), because the exon index is identical in both.
# So the exception is not a relaxation. It is a NAMED LIST of seams a published report places in a
# patient, and reaching it needs TWO independent things to be true at once:
#     1. the caller says explicitly that it is building a published non-canonical seam
#        (`PUBLISHED_BREAKPOINT_JUNCTION=1`, or `published_breakpoint=True`), and
#     2. the exact (donor, donor exon, acceptor, acceptor exon) tuple is in this dict.
# A coordinate slip fails (1) — nothing in the ordinary lane sets that flag — and a seam nobody
# sequenced fails (2). ⛔ AND THE GRADE IS ASSERTED, NEVER ASSUMED: an entry claiming the wrong
# exclusion reason RAISES rather than being waived, so this cannot become a general bypass by
# someone adding a tuple with a plausible-sounding reason beside it.
#
# ⚠ THE LIST ITSELF LIVES IN `aso_noncoding_acceptor_designs`, WHICH FIRST CURATED IT, AND IS READ
# FROM THERE RATHER THAN COPIED HERE. One fact, one place: a second copy beside the guard would be
# the more authoritative-looking one and would go stale the first time a case report is added. The
# import is LAZY because that module imports this one — at call time this module is fully loaded, so
# the cycle never forms — and its ABSENCE IS A REFUSAL, never an empty whitelist, because an empty
# whitelist silently turns every waiver request into "not published" and would read as a curation
# verdict rather than a missing file.
def published_noncoding_acceptor_junctions():
    """`{(donor, donor_exon, acceptor, acceptor_exon): meta}` — the curated published-breakpoint list."""
    import aso_noncoding_acceptor_designs as _nca                       # noqa: PLC0415
    return _nca.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS


def published_breakpoint_retraction(donor_sym, d_end, acceptor_sym, a_start):
    """The record of a seam this repository whitelisted and then WITHDREW, or None.

    Same lazy import and the same one-home rule as the whitelist above: the retraction list lives
    beside the whitelist it removes entries from, because a withdrawal stored anywhere else is a
    withdrawal the next curator will not see while editing the list it applies to.
    """
    import aso_noncoding_acceptor_designs as _nca                       # noqa: PLC0415
    return _nca.retraction_for(donor_sym, d_end, acceptor_sym, a_start)

#: ⛔ THE GRADES A PUBLISHED-BREAKPOINT ENTRY MAY WAIVE, AND `SEAM_NOT_PRODUCED` IS DELIBERATELY
#: ABSENT AND MUST STAY ABSENT. Both grades here are PROTEIN-level readings — the acceptor exon
#: carries no CDS, or the chimeric ORF does not compose — and an RNase-H1 gapmer cleaves a
#: transcript whatever protein that transcript makes. `SEAM_NOT_PRODUCED` is the opposite: it says
#: the seam is at a nucleotide offset the corrected transcript model does not produce, i.e. it is
#: the retraction's own grade, and no citation can make a seam exist that the coordinates refuse.
WAIVABLE_PUBLISHED_GRADES = ("NON_CODING_ACCEPTOR", "OUT_OF_FRAME")


def published_breakpoint_opt_in():
    """Has the CALLER explicitly said it is building a published non-canonical seam?

    ⛔ THE FLAG IS HALF THE LOCK. Membership of the whitelist alone would let a coordinate slip onto
    a whitelisted exon through, which is exactly case (a) above; the flag is what makes the waiver
    an INTENTION rather than a coincidence of arithmetic. Nothing in the ordinary design or screen
    lane sets it.
    """
    return (os.environ.get("PUBLISHED_BREAKPOINT_JUNCTION") or "").strip().lower() in (
        "1", "true", "yes", "on")


def published_breakpoint_waiver(donor_sym, d_end, acceptor_sym, a_start, j, opt_in=None):
    """The whitelist entry that excuses `j`'s non-EMITTABLE grade, or None if nothing does.

    RAISES rather than returning None when the caller HAS opted in but the junction does not stand
    up: not on the list, on the list under the wrong exclusion reason, or on the list while grading
    EMITTABLE (in which case it belongs in the ordinary panel and must not be emitted in a lane that
    labels its output unscreened-and-exceptional). A refusal that quietly degrades into the ordinary
    guard's message would send the next reader hunting for a coordinate bug that is not there.
    """
    opt_in = published_breakpoint_opt_in() if opt_in is None else bool(opt_in)
    if not opt_in:
        return None
    key = (donor_sym, d_end, acceptor_sym, a_start)
    meta = published_noncoding_acceptor_junctions().get(key)
    if meta is None:
        # ⛔ A WITHDRAWN SEAM AND AN UNSEQUENCED ONE ARE BOTH "not on the whitelist", AND THEY MUST
        # NOT PRINT THE SAME REFUSAL. The generic message sends the reader looking for a case report
        # to add; for a retracted seam the case report EXISTS, was read, and did not survive. Naming
        # the retraction is what stops the next session re-adding it from the same source.
        retracted = published_breakpoint_retraction(donor_sym, d_end, acceptor_sym, a_start)
        if retracted:
            raise RuntimeError(
                f"PUBLISHED_BREAKPOINT_JUNCTION is set for {donor_sym} e{d_end} :: {acceptor_sym} "
                f"e{a_start}, which this repository RETRACTED on {retracted['retracted_utc']}. "
                f"{retracted['verdict']} Re-adding it to the whitelist is not the fix — see "
                "`what_would_reopen_it` on the retraction record in "
                "aso_noncoding_acceptor_designs.RETRACTED_PUBLISHED_BREAKPOINTS. Refusing to emit.")
        raise RuntimeError(
            f"PUBLISHED_BREAKPOINT_JUNCTION is set for {donor_sym} e{d_end} :: {acceptor_sym} "
            f"e{a_start}, which is NOT on the published-breakpoint whitelist in junction_aso. The "
            "flag does not create an exception; it only lets a NAMED one through, and a seam nobody "
            "has sequenced is exactly what the acceptor guard exists to refuse. Refusing to emit.")
    lo, hi = plausible_nr4a3_resume_residues()
    grade, why = grade_junction(j, lo, hi)
    declared = meta["excluded_from_the_panel_by"]
    if declared not in WAIVABLE_PUBLISHED_GRADES:
        raise RuntimeError(
            f"{j['junction_label']} is whitelisted under exclusion grade {declared!r}, which is not "
            f"one of the waivable protein-level grades {WAIVABLE_PUBLISHED_GRADES}. Refusing.")
    if grade != declared:
        raise RuntimeError(
            f"{j['junction_label']} is whitelisted as {declared} but the committed transcript model "
            f"grades it {grade} ({why}). A whitelist entry whose stated reason does not match the "
            "measured one is a curation error, and waiving a grade nobody checked is how the "
            "retracted seam survived. Refusing to emit.")
    return {"junction": f"{donor_sym}_e{d_end}__{acceptor_sym}_e{a_start}",
            "waived_grade": grade, "why_the_panel_excludes_it": why,
            "transcript_type": meta["transcript_type"],
            "n_independent_sources": meta["n_independent_sources"],
            "evidence": list(meta["evidence"]),
            "one_home_for_the_evidence": meta["one_home_for_the_evidence"],
            "⚠_read_this_before_using_the_sequence":
                meta.get("⚠_read_this_before_using_the_sequence"),
            "_why_this_is_not_a_relaxation": (
                "The grade waived is a PROTEIN-level exclusion and this is an RNase-H1 modality: a "
                "gapmer cleaves the transcript whether or not the chimeric ORF survives. The "
                "coordinate guards are untouched — the acceptor's resume residue is still "
                "range-checked wherever the acceptor exon has a CDS, and SEAM_NOT_PRODUCED is not "
                "waivable at all."),
            "_screens_are_not_implied": (
                "A waiver admits the junction to the design and screen lane. It says nothing about "
                "which screens have actually been run on the designs; read those from the screen "
                "artifacts themselves."),
            }


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
        # ⭐ DONOR_GENE ADDED 2026-08-12. Default EWSR1, so every existing caller, workflow and
        # committed artifact is bit-for-bit unaffected; setting it lets the SCREEN follow the design
        # lane to TAF15/TCF12/FUS. Without this the atlas could design at 32 junctions and the
        # transcriptome screen could only ever run at 8 of them, which would leave the paper naming
        # a next step nothing could execute. `DONOR_EXON_END` is the generic spelling of
        # `EWSR1_EXON_END`; the old name still works and still wins if both are set, because
        # `aso-offtarget.yml` passes it and a silent change of meaning there would re-screen the
        # wrong junction under the right filename.
        donor_sym = (os.environ.get("DONOR_GENE") or "EWSR1").strip() or "EWSR1"
        d_end = _env_int("EWSR1_EXON_END", _env_int("DONOR_EXON_END", 12))
        n_start = _env_int("NR4A3_EXON_START", 3)
        ews = transcript_model(donor_sym)
        nr4 = transcript_model("NR4A3")
        # ⛔ AN EWSR1 RUN MUST EMIT THE KEY SET IT ALWAYS EMITTED. `mrna_junction_generic` alone
        # drops `EWSR1_exon_end` / `ewsr1_coding_nt_through_cut` / `ewsr1_coding_phase` from the
        # `measured_junction` block of every committed panel — and those are exactly the fields the
        # 2026-08-06 retraction narrative cites when it shows WHICH seam a panel is for. Silently
        # renaming them would make the corrected artifacts unreadable against the record that
        # corrected them. So EWSR1 goes through `mrna_junction`, which adds the legacy aliases on
        # top of the generic keys; a new partner gets the generic keys only, because it has no
        # history to preserve and an `ewsr1_`-prefixed field on a TAF15 junction would be a lie.
        j = (mrna_junction(ews, nr4, d_end, n_start) if donor_sym == "EWSR1"
             else mrna_junction_generic(ews, nr4, d_end, n_start))
        # ⛔ THE WAIVER IS RESOLVED BEFORE ANY GUARD RUNS, AND IT IS `None` UNLESS THE CALLER ASKED.
        # See `published_breakpoint_waiver`: no flag, no waiver; flag without a whitelist entry, a
        # refusal; whitelist entry whose stated exclusion reason disagrees with the measured grade,
        # a refusal. So the three guards below are unchanged for every junction any existing caller
        # builds — the ordinary lane cannot reach this object at all.
        waiver = published_breakpoint_waiver(donor_sym, d_end, "NR4A3", n_start, j)
        if not j["nr4a3_acceptor_exon_is_coding"] and waiver is None:
            raise RuntimeError(
                f"NR4A3 transcript exon {n_start} carries no coding sequence — refusing to slide "
                "onto a neighbour (this is Defect 1, and it is what produced the retracted seam)")
        lo, hi = plausible_nr4a3_resume_residues()
        # ⛔ THE RESUME-RESIDUE RANGE CHECK IS *NOT* WAIVABLE, AND ITS CONDITION IS THE ACCEPTOR'S
        # OWN CODING STATE RATHER THAN THE WAIVER. `grade_junction` already fixes this order and
        # says why: "a non-coding acceptor has no resume residue to range-check". Before the waiver
        # existed the guard above raised first, so this line could assume a residue; with a waived
        # non-coding acceptor `nr4a3_first_residue` is None and the comparison would raise a
        # TypeError that reads like a code fault instead of a reading. Where the acceptor DOES carry
        # a CDS this runs exactly as it always did, waiver or no waiver — SEAM_NOT_PRODUCED is the
        # retraction's own grade and no citation can waive it.
        if j["nr4a3_acceptor_exon_is_coding"] and not (lo <= j["nr4a3_first_residue"] <= hi):
            raise RuntimeError(
                f"{donor_sym} e{d_end} :: NR4A3 e{n_start} resumes NR4A3 at residue "
                f"{j['nr4a3_first_residue']}, outside the corrected plausible range [{lo}, {hi}] "
                "in fusion-object-inventory.json — this is the exact grade "
                "fusion-neoantigen-retraction.json calls SEAM_NOT_PRODUCED. Refusing to emit.")
        if not j["in_frame"] and waiver is None:
            raise RuntimeError(
                f"{donor_sym} e{d_end} :: NR4A3 e{n_start} is not in-frame at the mRNA level "
                f"({donor_sym} coding nt {j['donor_coding_nt_through_cut']} phase "
                f"{j['donor_coding_phase']} + acceptor 5'UTR "
                f"{j['nr4a3_acceptor_exon_5utr_nt_retained']} nt => "
                f"(cut+UTR) mod 3 = {j['frame_sum_mod3']}, must be 0); NR4A3 C-terminus not "
                "retained. This is a READING about that exon pair, not a code failure.")
        # ⛔ A WAIVED JUNCTION MUST SAY SO IN EVERY ARTIFACT BUILT ON IT. `measured_junction` copies
        # every non-underscore key of this dict into the designs panel, the BLAST screen and the
        # uncapped evaluation, so the waiver travels with the seam it excuses. An artifact that is
        # exceptional and does not look exceptional is the shape of the retraction: the old panels
        # carried a junction LABEL and no graded offsets, so the wrong seam was invisible in the
        # file that depended on it.
        if waiver is not None:
            j = dict(j, **{"⛔_published_breakpoint_waiver": waiver})
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


def design(left, right, fusion, parents=None):
    """Tile junction-spanning gapmers over `left|right` and annotate each.

    `parents` — an optional {symbol: transcript_sequence} map the fusion-specificity test runs
    against. ⭐ ADDED 2026-08-12 AND IT WIDENS A TEST THAT WAS TOO NARROW BY CONSTRUCTION. The
    default (module globals `EWSR1_full` / `NR4A3_full`) checks a candidate against the two parents
    of ITS OWN fusion only — which cannot see that a design against, say, TAF15::NR4A3 might be a
    perfect complement of wild-type EWSR1, a gene the patient also expresses. The FET-family donors
    (EWSR1, TAF15, FUS) are paralogues with genuinely similar low-complexity N-termini, so this is
    not a theoretical concern about this particular gene set; it is the concern. Passing every
    partner transcript makes the test strictly stricter, and the per-parent detail is reported so a
    refusal names WHICH transcript it hit.
    """
    if parents is None:
        parents = {"EWSR1": EWSR1_full, "NR4A3": NR4A3_full}
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
        # specificity: oligo must not perfectly complement ANY supplied parent transcript
        hit_parents = sorted(sym for sym, seq in parents.items() if seq and target in seq)
        spec_ok = not hit_parents
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
            # WHICH parent an exact hit landed on — a refusal that cannot name what it hit is the
            # failure mode this module is a correction for. Empty list = clean against all of them.
            "exact_parent_hits": hit_parents,
            "parents_screened": sorted(parents),
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
            (f"frame register mismatch: ({j.get('donor_symbol', 'EWSR1')} coding nt "
             f"{j['donor_coding_nt_through_cut']} + acceptor 5'UTR "
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
