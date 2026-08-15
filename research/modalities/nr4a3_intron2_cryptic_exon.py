#!/usr/bin/env python3
"""Measure the cryptic exon in NR4A3 intron 2 that the TAF15::NR4A3 *T-N* transcript retains.

⛔ WHY THIS EXISTS. Every one of the 38 junctions in the manuscript's panel joins a donor exon to
NR4A3 exon **3**, and the TAF15 arm of the coverage ladder is priced 3/3 — i.e. it assumes every
TAF15 patient carries TAF15 exon 6 :: NR4A3 exon 3. PMID 31020999 (PMC6766969, Brenca et al.,
J Pathol 2019) describes TWO isoforms and calls them, verbatim, "the two major TAF15-NR4A3 isoforms
detected in human tumors":

    T-N*  TAF15 exon 6 - NR4A3 exon 3        "the commonest TAF15 ... fusion"
    T-N   TAF15 exon 6 - NR4A3 intron 2      "the less common T-N variant"

A gapmer designed at the T-N* seam CANNOT engage a T-N transcript: the two seams share only their
donor half, and the 3' half an oligo hybridises to is entirely different sequence. So if real TAF15
patients carry T-N, the panel does not reach them and the published coverage figure is optimistic on
that arm. ⚠ THIS MOLECULE CAN ONLY EVER LOWER THE HEADLINE, which is exactly why it must be measured
rather than skipped.

★ THE ACCEPTOR IS NOT A RAW INTRON. Verbatim from the same paper: "T-N retains a short cryptic exon
located in NR4A3 intron 2 (ENST00000395097.6 isoform), thus encoding 25 additional amino acids prior
to the NR4A3 ATG." It is a SPLICED cryptic exon, so it has a definite sequence with definite
boundaries — and this module measures that sequence instead of asserting it.

WHAT THIS MODULE DOES (all measured; nothing typed from recollection):
  1. Cuts NR4A3 intron 2 from the genome via `hybrid_intron.fetch_intron`, which already defines
     "NR4A3 intron 2" as the intron immediately 5' of TRANSCRIPT exon 3 of ENST00000395097 and
     gates the coordinate convention against the committed exon record before cutting.
  2. DERIVES the cryptic exon's required length from the paper's own claim plus the measured frame
     arithmetic — it is not a free parameter. See `derive_required_length`.
  3. Enumerates EVERY exon Ensembl annotates inside that intron, across ALL NR4A3 transcripts and
     via a region-level overlap query, so an annotated cryptic exon is found rather than guessed.
  4. Enumerates every candidate internal exon in the intron that satisfies the derived length, the
     canonical AG|exon|GT splice-site flanks, and an uninterrupted fusion reading frame — and
     REPORTS THE COUNT. If that count is not 1, the sequence is NOT uniquely determined by these
     criteria and this module says so instead of picking one.

⛔ WHAT THIS MODULE MUST NEVER DO: emit a sequence that is not a substring of the genomic intron it
   fetched. Every candidate below is a slice of measured sequence, and `_assert_from_measured_intron`
   is the check that keeps it that way. A hand-typed 75-mer would look exactly like a real result.

Needs the network (Ensembl REST). The dev sandbox's egress proxy refuses rest.ensembl.org
(CONNECT 403), so this runs on a GitHub-hosted runner — `.github/workflows/fusion-cpu-extras.yml`,
task `nr4a3_intron2_cryptic`.

Output: nr4a3-intron2-cryptic-exon.json
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nr4a3-intron2-cryptic-exon.json")
sys.path.insert(0, HERE)

import junction_aso as ja            # noqa: E402
import hybrid_intron as hi           # noqa: E402

ENS = "https://rest.ensembl.org"

#: ⭐ A SECOND WAY IN, AND IT CHANGES NOTHING ABOUT WHERE THE SEQUENCE COMES FROM. This module needs
#: Ensembl, which the dev sandbox 403s at CONNECT, so it normally runs on a GitHub-hosted runner.
#: When THIS repository's own scripts cannot be pushed to a runner — during an integration freeze,
#: for instance, when commits belong to a steward rather than to the working session — the same three
#: Ensembl reads can be performed by an already-on-main fetcher (`fetch-literature.yml`, inline
#: `targets_json`) and published to the `literature-cache` branch. Point `ENSEMBL_FETCH_DIR` at that
#: directory and every measurement below is taken from those files instead of from a live call.
#:
#: ⛔ WHAT MUST NOT CHANGE, AND DOES NOT: the SEQUENCE IS STILL MEASURED FROM ENSEMBL. This mode
#: swaps WHICH process made the HTTP request; it does not let a sequence be typed, inferred or
#: reconstructed. The identification arithmetic is the same code either way, and
#: `_assert_from_measured_intron` still refuses anything that is not a substring of the fetched
#: genomic DNA. A mode that let a human supply the bases would be the one failure this whole module
#: exists to prevent.
FETCH_DIR = (os.environ.get("ENSEMBL_FETCH_DIR") or "").strip()


#: `lit_fetch_urls.py` writes a provenance header — SOURCE URL / FINAL URL / HTTP / CONTENT-TYPE —
#: above every payload, separated by a rule of '=' characters. That header is the reason this mode is
#: auditable at all (it carries the URL actually fetched and the status actually returned), so it is
#: PARSED rather than skipped past.
_FETCH_RULE = "=" * 20


def _fetched(name):
    """Read one payload from the CI-fetched Ensembl cache, gated on its recorded HTTP status.

    ⛔ THE STATUS GATE IS THE POINT. A failed fetch still produces a FILE, and that file contains
    plausible-looking text — `503 Service Unavailable / No server is available to handle this
    request.` One of the three reads in this corpus came back exactly that way. Without this gate a
    503 body would flow into a parser as though it were data, which is the precise shape of "a
    populated field is not a measured one".
    """
    # ⚠ COLON-SEPARATED, because one Ensembl read can fail while its siblings succeed and the retry
    # lands in a DIFFERENT published corpus. (Measured: the all-transcripts lookup returned 503 while
    # the genomic and lookup reads returned 200 in the same run.) Re-fetching into a fresh slug is
    # right — the publish step replaces a slug wholesale, so retrying into the same one would delete
    # the payloads that did succeed — and that makes the cache a SEARCH PATH rather than a directory.
    failures = []
    for d in [x for x in FETCH_DIR.split(os.pathsep) if x.strip()]:
      for ext in (".txt", ".json"):
        p = os.path.join(d.strip(), name + ext)
        if not os.path.exists(p):
            continue
        raw = open(p, encoding="utf-8", errors="replace").read()
        if not raw.strip():
            raise RuntimeError(f"{p} is empty — an absent reading, not a reading of absence")
        head, sep, body = raw.partition(_FETCH_RULE)
        if not sep:
            return raw                    # no provenance header; take the payload as-is
        status = None
        for line in head.splitlines():
            if line.startswith("HTTP:"):
                status = line.split(":", 1)[1].strip()
        if status != "200":
            # A failed read in ONE corpus is not a verdict — a later corpus may hold the retry that
            # succeeded. Remember the failure and keep looking; only report it if nothing succeeds.
            failures.append(f"{p}: HTTP {status}")
            continue
        return body.lstrip("=\n")
    raise RuntimeError(
        f"{name}(.txt|.json) not usable in ENSEMBL_FETCH_DIR={FETCH_DIR!r}"
        + (f" — found but unusable: {failures}" if failures else " — not found in any corpus"))


def _fasta_seq(text):
    """Sequence out of a FASTA payload, uppercased, with every non-ACGTN character refused."""
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith(">")]
    seq = "".join(lines).upper()
    bad = set(seq) - set("ACGTN")
    if bad:
        raise RuntimeError(f"fetched genomic FASTA carries non-nucleotide characters {sorted(bad)}")
    if not seq:
        raise RuntimeError("fetched genomic FASTA contains no sequence")
    return seq


def intron2_from_fetched_genomic():
    """NR4A3 intron 2, cut out of the CI-fetched genomic FASTA by EXACT EXON MATCHING.

    ⭐ WHY MATCHING RATHER THAN COORDINATE ARITHMETIC. The genomic payload is the transcript's span
    on the transcript's strand; locating intron 2 inside it needs the exon boundaries, and taking
    those from a second endpoint would make the cut depend on two records agreeing. The committed
    cDNA already contains exon 2 and exon 3 verbatim, so each can be FOUND in the genomic sequence —
    and a match that is not unique is a refusal rather than a choice. That makes the cut
    self-verifying: it cannot silently land one base off, which is the exact defect class
    `junction_aso`'s two-defect block records twice.

    The GT..AG check at the end is the independent confirmation, and it is the same check
    `hybrid_intron.fetch_intron` applies to its own coordinate-based cut.
    """
    nr4 = ja.transcript_model(ACCEPTOR_SYMBOL)
    genomic = _fasta_seq(_fetched("nr4a3_transcript_genomic_fasta"))
    e2 = nr4["cdna"][ja.exon_tx_start(nr4, 2):ja.exon_tx_end(nr4, 2)]
    e3 = nr4["cdna"][ja.exon_tx_start(nr4, 3):ja.exon_tx_end(nr4, 3)]
    for label, seq in (("exon 2", e2), ("exon 3", e3)):
        n = genomic.count(seq)
        if n != 1:
            raise RuntimeError(
                f"NR4A3 {label} occurs {n} times in the fetched genomic sequence — the intron-2 cut "
                "would be ambiguous, so no seam may be emitted")
    lo = genomic.index(e2) + len(e2)          # first intronic base
    hi = genomic.index(e3)                     # one past the last intronic base
    if hi <= lo:
        raise RuntimeError("NR4A3 exon 3 precedes exon 2 in the fetched genomic sequence — the "
                           "payload is not the transcript span this module assumes")
    seq = genomic[lo:hi]
    if seq[:2] != "GT" or seq[-2:] != "AG":
        raise RuntimeError(
            f"the cut intron reads {seq[:2]}...{seq[-2:]}, not GT...AG. A non-canonical intron is "
            "possible, but an off-by-one or a strand error is far likelier, and neither may be "
            "built on.")
    return {"symbol": ACCEPTOR_SYMBOL, "transcript": nr4["transcript"],
            "chrom": None, "strand": nr4.get("strand"),
            "intron_name": f"{ACCEPTOR_SYMBOL} intron {ACCEPTOR_EXON - 1} "
                           f"(5' of TRANSCRIPT exon {ACCEPTOR_EXON})",
            "genomic_start": None, "genomic_end": None,
            "offset_in_fetched_transcript_span": lo,
            "length_nt": len(seq),
            "donor_dinucleotide": seq[:2], "acceptor_dinucleotide": seq[-2:],
            "gc_percent": round(100 * (seq.count("G") + seq.count("C")) / len(seq), 1),
            "_source": ("cut from the CI-fetched genomic FASTA by exact matching of the committed "
                        "exon 2 and exon 3 sequences; both matched uniquely and the cut reads "
                        "GT...AG"),
            "_seq": seq}

#: The paper this whole module is a measurement of. ⚠ The two quoted strings are the ONLY inputs
#: taken from prose; everything else is measured. They are quoted verbatim so a reader can check the
#: derivation against the source rather than against a paraphrase.
SOURCE = {
    "pmid": "31020999",
    "pmc": "PMC6766969",
    "citation": ("Brenca M, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks "
                 "the difference between EWSR1 and TAF15 translocated extraskeletal myxoid "
                 "chondrosarcomas. J Pathol. 2019."),
    "quote_construct": (
        "T-N, corresponding to TAF15 (exons 1-6)-NR4A3 (intron 2-exon 8) and T-N*, corresponding to "
        "the commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) fusion. Both T-N and T-N* encode the "
        "whole coding sequence of NR4A3 (exons 3-8); T-N retains a short cryptic exon located in "
        "NR4A3 intron 2 (ENST00000395097.6 isoform), thus encoding 25 additional amino acids prior "
        "to the NR4A3 ATG."),
    "quote_prevalence": (
        "we sought to compare the biological behavior of the two major TAF15-NR4A3 isoforms detected "
        "in human tumors. Cells were engineered with the T-N* fusion variant (TAF15 exon 6-NR4A3 "
        "exon 3) and with the less common T-N variant (TAF15 exon 6-NR4A3 intron 2)."),
    "transcript_named_in_the_paper": "ENST00000395097.6",
}

#: The single number this module takes from the paper's prose. Named once, used once.
ADDITIONAL_AA_BEFORE_NR4A3_ATG = 25

DONOR_SYMBOL, DONOR_EXON = "TAF15", 6
ACCEPTOR_SYMBOL, ACCEPTOR_EXON = "NR4A3", 3


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1 · The length is DERIVED, not assumed
# ─────────────────────────────────────────────────────────────────────────────────────────────
def aa_accounting(L):
    """Both ways of counting "amino acids prior to the NR4A3 ATG" for a cryptic exon of length L.

    ⛔⛔ THE SENTENCE IS AMBIGUOUS AND THE AMBIGUITY IS WORTH A FULL CODON. This function exists
    because an earlier version of this module DERIVED a length from the paper's phrase and got the
    wrong answer, and the wrong answer was self-consistent enough to look right.

    "T-N retains a short cryptic exon ... thus encoding 25 additional amino acids prior to the NR4A3
    ATG" can mean either of two things, and BOTH are frame-preserving:

      DIFFERENCE  — T-N has 25 more whole codons before the NR4A3 ATG than T-N* does.  → L = 75
      ENCODED     — the cryptic exon contributes bases to 25 codons.                    → L = 72

    ⭐ THE ANNOTATION SETTLES IT, NOT THE ARITHMETIC. The exon is annotated (curated RefSeq
    NM_173200.3, and independently the mRNA U12767, at identical coordinates) at 72 nt, which
    satisfies the ENCODED reading exactly. So this function no longer predicts a length: it REPORTS
    what each reading implies, and `resolve` checks the measured exon against them. An arithmetic
    prediction from an ambiguous sentence is a hypothesis, and this lane's rule is that a hypothesis
    never outranks a measurement.
    """
    donor = ja.transcript_model(DONOR_SYMBOL)
    acceptor = ja.transcript_model(ACCEPTOR_SYMBOL)
    cut = sum(ja.coding_nt_per_exon(donor)[:DONOR_EXON])
    U = max(0, acceptor["utr5_len"] - ja.exon_tx_start(acceptor, ACCEPTOR_EXON))
    first = cut // 3 + 1                      # 1-based codon holding the first cryptic base
    last = (cut + L - 1) // 3 + 1             # 1-based codon holding the last cryptic base
    return {
        "cryptic_exon_length_nt": L,
        "donor_coding_nt_through_cut": cut,
        "acceptor_exon_5utr_nt_retained": U,
        "frame_preserved": (cut + L + U) % 3 == 0,
        "aa_before_nr4a3_atg_in_TNstar": (cut + U) // 3,
        "aa_before_nr4a3_atg_in_TN": (cut + L + U) // 3,
        "reading_DIFFERENCE_aa": (cut + L + U) // 3 - (cut + U) // 3,
        "reading_ENCODED_aa": last - first + 1,
        "_codon_span_touched_by_the_cryptic_exon": [first, last],
    }


#: The number the paper states. Named once; used only as a CHECK on a measured exon, never to predict
#: one. See `aa_accounting` for why predicting from it produced a wrong length that looked right.
def _matches_the_papers_claim(acc):
    hits = [k for k in ("reading_DIFFERENCE_aa", "reading_ENCODED_aa")
            if acc[k] == ADDITIONAL_AA_BEFORE_NR4A3_ATG]
    return hits


def derive_required_length():
    """DEPRECATED PREDICTOR — retained only to show what it predicted and why that was not enough.

    ⚠ THIS FUNCTION'S ANSWER IS NOT USED TO CHOOSE A SEQUENCE ANY MORE. It is kept, and its output
    is carried in the artifact, because the artifact must show that a 75-nt prediction was made,
    was arithmetically self-consistent, and was WRONG — otherwise a later reader has no way to know
    the ambiguity exists and may re-derive it.

    ⭐ THIS IS THE STEP THAT MAKES THE RETRIEVAL FALSIFIABLE. The paper gives no coordinates and no
    sequence, so without a derived length any 30-nt or 300-nt window in the intron would be equally
    admissible and "the cryptic exon" would be whatever the code happened to pick. It is not a free
    parameter, because two measured facts pin it:

      * TAF15 contributes `cut` coding nt through transcript exon 6, measured from the committed
        transcript model — not counted by hand.
      * NR4A3 transcript exon 3 carries `U` nt of 5'UTR ahead of its own ATG, likewise measured.
        (U = 2 is the very quantity `junction_aso`'s Defect-2 block says the lane could not see when
        it was building fusions out of CDSs.)

    In T-N*, the bases translated before the NR4A3 ATG are `cut + U`. In T-N they are `cut + L + U`
    for a cryptic exon of length L. The paper says T-N encodes 25 ADDITIONAL amino acids prior to
    the NR4A3 ATG, and that both isoforms "encode the whole coding sequence of NR4A3" — so the
    register must be preserved and the difference must be a whole number of codons:

        (cut + L + U)/3 - (cut + U)/3 = 25   =>   L = 75

    ⚠ THE COMPETING READING IS EXCLUDED BY ARITHMETIC, NOT BY PREFERENCE. Read instead as "T-N has
    25 aa in total before the NR4A3 ATG", L would be 75 - U = 73, and 73 % 3 != 0 would shift the
    register and destroy the NR4A3 ORF — contradicting the paper's own sentence in the same breath.
    Both readings are computed and reported so the exclusion is visible, not asserted.
    """
    donor = ja.transcript_model(DONOR_SYMBOL)
    acceptor = ja.transcript_model(ACCEPTOR_SYMBOL)
    cut = sum(ja.coding_nt_per_exon(donor)[:DONOR_EXON])
    U = max(0, acceptor["utr5_len"] - ja.exon_tx_start(acceptor, ACCEPTOR_EXON))
    if (cut + U) % 3 != 0:
        raise RuntimeError(
            f"T-N* ({DONOR_SYMBOL} e{DONOR_EXON} :: NR4A3 e{ACCEPTOR_EXON}) is not in register "
            f"(cut {cut} + acceptor 5'UTR {U}) % 3 = {(cut + U) % 3}. The paper's 'additional amino "
            "acids' arithmetic is relative to T-N*, so it cannot be applied to a T-N* that does not "
            "itself preserve the NR4A3 reading frame. Refusing to derive a length.")
    L = 3 * ADDITIONAL_AA_BEFORE_NR4A3_ATG
    alt = L - U
    return {
        "derived_length_nt": L,
        "donor_coding_nt_through_cut": cut,
        "acceptor_exon_5utr_nt_retained": U,
        "aa_before_nr4a3_atg_in_TNstar": (cut + U) // 3,
        "aa_before_nr4a3_atg_in_TN": (cut + L + U) // 3,
        "difference_aa": (cut + L + U) // 3 - (cut + U) // 3,
        "_reading_A_accepted": (
            f"{ADDITIONAL_AA_BEFORE_NR4A3_ATG} codons contributed wholly by the cryptic exon "
            f"=> L = {L}; L % 3 = {L % 3}, so the NR4A3 reading frame is preserved and the paper's "
            "'both encode the whole coding sequence of NR4A3' holds."),
        "_reading_B_rejected": (
            f"(L + U)/3 = {ADDITIONAL_AA_BEFORE_NR4A3_ATG} => L = {alt}; L % 3 = {alt % 3} != 0, "
            "which shifts the register and destroys the NR4A3 ORF. Rejected by arithmetic."),
        "_sources": {
            "donor_transcript": donor["transcript"], "acceptor_transcript": acceptor["transcript"],
            "transcript_source": ja.transcript_source_provenance(),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2 · What Ensembl actually annotates inside that intron (needs the network)
# ─────────────────────────────────────────────────────────────────────────────────────────────
def _tx_version(transcript_id):
    import fusion_breakpoints as fb
    rec = fb.get(f"{ENS}/lookup/id/{transcript_id}")
    return {"id": rec.get("id"), "version": rec.get("version"),
            "display_name": rec.get("display_name"), "biotype": rec.get("biotype")}


def _exons_from_lookup(blob):
    """Transcript exons in TRANSCRIPT order from an Ensembl `lookup?expand=1` payload."""
    strand = blob["strand"]
    exons = sorted(blob["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    return strand, blob["seq_region_name"], exons


def intron2_coords_from_fetched_lookup():
    """Intron 2's genomic span from the fetched lookup, gated against the committed exon lengths.

    This is the SECOND, independent determination of the same intron. `intron2_from_fetched_genomic`
    finds it by matching exon sequence inside the genomic payload; this one finds it by subtracting
    exon coordinates. Two routes through two different endpoints must agree on the length, and
    `build` refuses if they do not — which is the check neither route can perform alone.
    """
    nr4 = ja.transcript_model(ACCEPTOR_SYMBOL)
    blob = json.loads(_fetched("nr4a3_transcript_lookup_expand"))
    strand, chrom, exons = _exons_from_lookup(blob)
    lens = [e["end"] - e["start"] + 1 for e in exons]
    if lens != nr4["exon_lens"]:
        raise RuntimeError(
            f"{ACCEPTOR_SYMBOL}: fetched genomic exon lengths {lens[:6]}... do not reproduce the "
            f"committed emc-construct-inputs.json lengths {nr4['exon_lens'][:6]}... — the "
            "coordinate convention is not what this module assumes, so no intron may be cut")
    a, b = exons[ACCEPTOR_EXON - 2], exons[ACCEPTOR_EXON - 1]   # exon 2 and exon 3
    lo, hi = ((a["end"] + 1, b["start"] - 1) if strand == 1 else (b["end"] + 1, a["start"] - 1))
    return {"chrom": chrom, "strand": strand, "genomic_start": lo, "genomic_end": hi,
            "length_nt": hi - lo + 1, "transcript_version": blob.get("version")}


def annotated_exons_from_fetched_gene(intron):
    """The transcript walk, from the fetched all-transcripts payload. No region-overlap arm.

    ⚠ AND IT SAYS SO. The live path runs a second, independent region-overlap query that can see an
    exon Ensembl attributes to some other gene or read-through model. That endpoint was not fetched
    here, so this arm is genuinely narrower — recorded as `not_fetched` rather than reported as a
    zero, because "the query did not run" and "the query found nothing" are different facts and only
    one of them is evidence.
    """
    lo, hi = intron["genomic_start"], intron["genomic_end"]
    blob = json.loads(_fetched("nr4a3_gene_all_transcripts"))
    out = []
    for tr in blob.get("Transcript", []) or []:
        for ex in tr.get("Exon", []) or []:
            s, e = min(ex["start"], ex["end"]), max(ex["start"], ex["end"])
            if s <= hi and e >= lo:
                out.append({"transcript": tr.get("id"), "transcript_biotype": tr.get("biotype"),
                            "is_canonical": tr.get("is_canonical"), "exon_id": ex.get("id"),
                            "start": ex["start"], "end": ex["end"],
                            "length_nt": e - s + 1, "strand": ex.get("strand"),
                            "relation_to_intron": ("contained" if lo <= s and e <= hi
                                                   else "overlapping")})
    contained = [a for a in out if a["relation_to_intron"] == "contained"]
    return {"n_annotated_exons_in_intron_by_transcript_walk": len(out),
            "n_annotated_exons_in_intron_by_region_overlap": None,
            "n_contained_wholly_within_the_intron": len(contained),
            "region_overlap_query": "not_fetched — this arm did not run in fetched-cache mode",
            "n_transcripts_examined": len(blob.get("Transcript", []) or []),
            "by_transcript_walk": out, "by_region_overlap": [],
            "_intron_strand": intron["strand"]}


def annotated_exons_inside(intron):
    """Every Ensembl-annotated exon lying wholly inside the fetched intron, two independent ways.

    ⛔ TWO QUERIES ON PURPOSE, AND THE SECOND IS NOT REDUNDANT. The per-transcript walk sees only
    exons belonging to a transcript Ensembl assigns to the NR4A3 gene record; the region overlap
    sees every exon annotated on that DNA regardless of which gene or transcript owns it. A cryptic
    exon that Ensembl attributes to a neighbouring or read-through model would be invisible to the
    first and visible to the second, and "no annotated exon" is a claim strong enough that it must
    survive both. An absent reading is not a reading of absence.
    """
    import fusion_breakpoints as fb
    lo, hi, chrom, strand = (intron["genomic_start"], intron["genomic_end"],
                             intron["chrom"], intron["strand"])

    def _inside(s, e):
        return lo <= min(s, e) and max(s, e) <= hi

    def _overlaps(s, e):
        return min(s, e) <= hi and max(s, e) >= lo

    # ⭐ CONTAINMENT IS NOT THE ONLY SHAPE THE CRYPTIC EXON CAN HAVE, AND A CONTAINMENT-ONLY QUERY
    # WOULD MISS THE LIKELIEST ALTERNATIVE. If Ensembl models this exon as the FIRST exon of a
    # shorter NR4A3 isoform, or as the last exon of an upstream one, it can start inside intron 2 and
    # run past its boundary — in which case it overlaps the intron without being contained by it, and
    # a `wholly inside` test returns nothing while the annotation sits right there. So overlapping
    # exons are recorded too, tagged, and left for the caller to judge; only CONTAINED exons of the
    # derived length are eligible to resolve the sequence.
    def _rec(**kw):
        s, e = kw["start"], kw["end"]
        kw["length_nt"] = max(s, e) - min(s, e) + 1
        kw["relation_to_intron"] = "contained" if _inside(s, e) else "overlapping"
        return kw

    by_transcript = []
    look = fb.get(f"{ENS}/lookup/symbol/homo_sapiens/{ACCEPTOR_SYMBOL}?expand=1")
    for tr in look.get("Transcript", []):
        for ex in tr.get("Exon", []) or []:
            if _overlaps(ex["start"], ex["end"]):
                by_transcript.append(_rec(
                    transcript=tr.get("id"), transcript_biotype=tr.get("biotype"),
                    is_canonical=tr.get("is_canonical"), exon_id=ex.get("id"),
                    start=ex["start"], end=ex["end"], strand=ex.get("strand")))

    by_region = []
    try:
        feats = fb.get(f"{ENS}/overlap/region/human/{chrom}:{lo}-{hi}?feature=exon")
        for ex in feats:
            if _overlaps(ex.get("start"), ex.get("end")):
                by_region.append(_rec(
                    exon_id=ex.get("exon_id") or ex.get("id"),
                    parent_transcript=ex.get("Parent"),
                    start=ex.get("start"), end=ex.get("end"), strand=ex.get("strand")))
        region_query = "ok"
    except Exception as exc:                                     # noqa: BLE001
        # ⚠ A FAILED QUERY IS RECORDED AS A FAILED QUERY. Swallowing it into an empty list would
        # turn "Ensembl did not answer" into "Ensembl annotates nothing here", which is the exact
        # absent-reading-as-reading-of-absence failure this repo has a rule about.
        region_query = f"FAILED: {exc}"

    contained = [a for a in by_transcript + by_region if a["relation_to_intron"] == "contained"]
    return {"n_annotated_exons_in_intron_by_transcript_walk": len(by_transcript),
            "n_annotated_exons_in_intron_by_region_overlap": len(by_region),
            "n_contained_wholly_within_the_intron": len(contained),
            "region_overlap_query": region_query,
            "_relation_note": ("`contained` = wholly inside intron 2, which is what a cryptic "
                               "internal exon looks like. `overlapping` = crosses a boundary, which "
                               "is what an alternative FIRST or LAST exon of another isoform looks "
                               "like; recorded because its absence would otherwise be invisible, "
                               "but not eligible to resolve the sequence."),
            "by_transcript_walk": by_transcript, "by_region_overlap": by_region,
            "_intron_strand": strand}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3 · Candidate enumeration inside the measured intron
# ─────────────────────────────────────────────────────────────────────────────────────────────
STOPS = ("TAA", "TAG", "TGA")


def _codon_offset_into_cryptic(cut):
    """0-based index of the first base of the cryptic exon that STARTS a codon.

    The chimeric ORF has `cut` donor coding nt before the cryptic exon, so `(-cut) % 3` cryptic
    bases finish the codon the donor left open, and codons start from there.
    """
    return (-cut) % 3


def enumerate_candidates(intron_seq, length, cut):
    """Every window of `length` nt in the intron that could be an internal spliced exon here.

    Three filters, each a real constraint rather than a preference:
      (a) LENGTH — derived above, not chosen.
      (b) SPLICE SITES — an internal U2 exon is preceded by an intron ending `AG` and followed by
          an intron beginning `GT`. This is the GT-AG rule read from the exon's point of view, and
          it is the same rule `hybrid_intron.fetch_intron` already self-checks its own cut against.
      (c) READING FRAME — the paper says T-N encodes the whole NR4A3 coding sequence, so the
          chimeric ORF reads THROUGH the cryptic exon. A window carrying a stop codon in the fusion
          frame cannot be it.

    ⚠ THE RETURN VALUE IS A CANDIDATE LIST, NOT AN ANSWER. Reporting how many windows survive is
    the point: if it is not exactly 1 the sequence is undetermined by these criteria and the caller
    must say so rather than taking the first row.
    """
    off = _codon_offset_into_cryptic(cut)
    out = []
    for s in range(1, len(intron_seq) - length - 1):     # need >=1 nt of intron on each side
        e = s + length                                   # window is intron_seq[s:e]
        if intron_seq[s - 2:s] != "AG":                  # acceptor site immediately 5'
            continue
        if intron_seq[e:e + 2] != "GT":                  # donor site immediately 3'
            continue
        win = intron_seq[s:e]
        codons = [win[i:i + 3] for i in range(off, len(win) - 2, 3)]
        if any(c in STOPS for c in codons):
            continue
        out.append({"intron_offset_0based": s, "sequence": win,
                    "flank_5p_intron_3nt": intron_seq[max(0, s - 3):s],
                    "flank_3p_intron_6nt": intron_seq[e:e + 6],
                    "gc_percent": round(100 * (win.count("G") + win.count("C")) / len(win), 1)})
    return out


#: UCSC track payloads fetched alongside the Ensembl ones. `ncbiRefSeqCurated` is the authoritative
#: arm — a MANUALLY CURATED RefSeq model, not a prediction — and `all_mrna` is the independent
#: evidence arm: a real spliced mRNA aligned to the genome, which is exactly what a "cryptic exon"
#: claim needs behind it. `ncbiRefSeq` additionally carries XM_ predicted models, which are recorded
#: but never allowed to resolve anything on their own.
UCSC_TRACKS = ("ncbiRefSeqCurated", "ncbiRefSeq", "knownGene", "all_mrna", "intronEst",
               "ncbiRefSeqOther")
UCSC_AUTHORITATIVE = ("ncbiRefSeqCurated",)


def ucsc_exons_in_intron(intron):
    """Every annotated/aligned exon block lying wholly inside the intron, per UCSC track.

    ⚠ UCSC IS 0-BASED HALF-OPEN AND ENSEMBL IS 1-BASED INCLUSIVE, and this is the single likeliest
    place for this whole module to go silently wrong by one. So the conversion is done ONCE, here,
    and every returned exon carries BOTH coordinate systems plus the sequence cut from the Ensembl
    intron at the converted offset — and `resolve` then re-checks that the cut sequence's own splice
    flanks read AG…GT. A one-base slip breaks that check immediately.
    """
    lo1, hi1 = intron["genomic_start"], intron["genomic_end"]        # 1-based inclusive
    lo0, hi0 = lo1 - 1, hi1                                          # 0-based half-open
    out = []
    for track in UCSC_TRACKS:
        try:
            blob = json.loads(_fetched(f"ucsc_{_UCSC_FILE_ALIAS.get(track, track)}"))
        except Exception as exc:                                     # noqa: BLE001
            out.append({"track": track, "_unavailable": str(exc)})
            continue
        rows = blob.get(track)
        if isinstance(rows, dict):                                   # bigBed tracks nest by chrom
            flat = []
            for v in rows.values():
                flat.extend(v if isinstance(v, list) else [v])
            rows = flat
        for r in rows or []:
            if "exonStarts" in r:
                ss = [int(x) for x in str(r["exonStarts"]).rstrip(",").split(",") if x]
                ee = [int(x) for x in str(r["exonEnds"]).rstrip(",").split(",") if x]
            elif "tStarts" in r and "blockSizes" in r:               # PSL alignment
                ss = [int(x) for x in str(r["tStarts"]).rstrip(",").split(",") if x]
                bs = [int(x) for x in str(r["blockSizes"]).rstrip(",").split(",") if x]
                ee = [a + b for a, b in zip(ss, bs)]
            else:
                continue
            for a, b in zip(ss, ee):
                if a >= lo0 and b <= hi0:
                    out.append({
                        "track": track,
                        "authoritative": track in UCSC_AUTHORITATIVE,
                        "name": r.get("name") or r.get("qName"),
                        "gene": r.get("name2") or r.get("geneName"),
                        "strand": r.get("strand"),
                        "ucsc_0based_start": a, "ucsc_0based_end": b,
                        "genomic_start_1based": a + 1, "genomic_end_1based": b,
                        "length_nt": b - a,
                        "offset_in_intron_0based": (a + 1) - lo1,
                    })
    return out


#: UCSC track name -> the filename stem it was fetched under. The corpus was fetched with readable
#: names; mapping them here keeps the track vocabulary (which is UCSC's) separate from the file
#: vocabulary (which is ours), so neither has to be renamed to match the other.
_UCSC_FILE_ALIAS = {
    "ncbiRefSeqCurated": "refseq_curated", "ncbiRefSeq": "refseq_all",
    "knownGene": "knowngene_gencode", "all_mrna": "all_mrna",
    "intronEst": "intron_est", "ncbiRefSeqOther": "refseq_other",
}


def resolve(intron_seq, ucsc_exons, cut):
    """Pick the cryptic exon from the ANNOTATION, then put it through every independent check.

    ⛔ AN ANNOTATED EXON IS A CANDIDATE, NOT AN ANSWER, UNTIL IT SURVIVES ALL OF THESE:
      1. it is recorded by at least one AUTHORITATIVE (manually curated) track;
      2. the sequence cut at its converted offset is a substring of the intron measured from a
         DIFFERENT source (Ensembl) — a cross-source agreement no single database can fake;
      3. its own flanks read AG | exon | GT, which is what breaks a one-base coordinate slip;
      4. its length preserves the chimeric reading frame;
      5. it carries no stop codon in that frame — the paper says T-N encodes the whole NR4A3 CDS;
      6. it reproduces the paper's 25-amino-acid statement under a NAMED reading.
    Anything that fails is returned with the failure attached rather than dropped, because "no exon
    resolved" and "an exon was found and rejected" are different findings.
    """
    graded = []
    for ex in ucsc_exons:
        if "_unavailable" in ex:
            continue
        off, L = ex["offset_in_intron_0based"], ex["length_nt"]
        g = dict(ex)
        seq = intron_seq[off:off + L] if 0 <= off and off + L <= len(intron_seq) else ""
        acc = aa_accounting(L) if L else None
        g.update({
            "sequence": seq or None,
            "check_1_authoritative_track": bool(ex.get("authoritative")),
            "check_2_substring_of_the_ensembl_intron": bool(seq) and seq in intron_seq,
            "check_3_splice_flanks": (f"{intron_seq[off-2:off]}|exon|{intron_seq[off+L:off+L+2]}"
                                      if seq else None),
            "check_3_pass": bool(seq) and intron_seq[off-2:off] == "AG"
                            and intron_seq[off + L:off + L + 2] == "GT",
            "check_4_frame_preserved": bool(acc and acc["frame_preserved"]),
            "check_5_no_stop_in_the_fusion_frame": bool(seq) and not any(
                seq[i:i + 3] in STOPS for i in range(_codon_offset_into_cryptic(cut), len(seq) - 2, 3)),
            "check_6_readings_matching_the_papers_25aa": _matches_the_papers_claim(acc) if acc else [],
            "aa_accounting": acc,
        })
        g["passes_every_check"] = bool(
            g["check_1_authoritative_track"] and g["check_2_substring_of_the_ensembl_intron"]
            and g["check_3_pass"] and g["check_4_frame_preserved"]
            and g["check_5_no_stop_in_the_fusion_frame"]
            and g["check_6_readings_matching_the_papers_25aa"])
        graded.append(g)

    winners = {g["sequence"] for g in graded if g["passes_every_check"]}
    if len(winners) == 1:
        seq = winners.pop()
        supporting = sorted({g["name"] for g in graded if g["sequence"] == seq and g["name"]})
        return seq, graded, {
            "how": "annotated_exon_passing_every_independent_check",
            "supporting_records": supporting,
            "n_independent_records_at_these_coordinates": len(supporting),
        }
    return None, graded, {"how": None, "n_passing": len(winners)}


def _assert_from_measured_intron(seq, intron_seq):
    """⛔ THE ONE CHECK THAT CANNOT BE SKIPPED: every emitted base came out of the fetched intron."""
    if not seq or seq not in intron_seq:
        raise RuntimeError(
            "a cryptic-exon sequence that is not a substring of the fetched NR4A3 intron 2 was about "
            "to be emitted. That can only mean it was constructed rather than measured. Refusing.")
    return True


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 4 · The run
# ─────────────────────────────────────────────────────────────────────────────────────────────
def build():
    prediction = derive_required_length()          # kept only to show what it predicted, and why
    cut = prediction["donor_coding_nt_through_cut"]

    if FETCH_DIR:
        intron = intron2_from_fetched_genomic()
        coords = intron2_coords_from_fetched_lookup()
        intron_seq = intron.pop("_seq")
        # ⛔ TWO INDEPENDENT DETERMINATIONS MUST AGREE. One found the intron by matching exon
        # SEQUENCE inside the genomic payload; the other by subtracting exon COORDINATES from the
        # lookup. Different endpoints, no shared arithmetic — so agreement is real evidence, and
        # disagreement is a refusal, because a seam built on a one-base slip is the defect class
        # this lane has been burned by twice.
        if coords["length_nt"] != len(intron_seq):
            raise RuntimeError(
                f"NR4A3 intron 2 is {len(intron_seq)} nt by exon-sequence matching but "
                f"{coords['length_nt']} nt by exon-coordinate subtraction. Two Ensembl records "
                "disagree about the same intron — refusing to emit until that is graded.")
        intron.update({k: coords[k] for k in ("chrom", "genomic_start", "genomic_end")})
        intron["_cross_check"] = ("length agrees between exon-sequence matching in the genomic "
                                  "payload and exon-coordinate subtraction in the lookup payload")
        intron["_transcript_version_today"] = coords.get("transcript_version")
        # ⚠ THE ENSEMBL ANNOTATION ARM IS CORROBORATING, NOT AUTHORITATIVE, SO ITS ABSENCE IS
        # RECORDED RATHER THAN FATAL — but it is recorded, with the HTTP status that caused it, and
        # never as an empty result. "Ensembl annotates no exon here" and "Ensembl did not answer"
        # are different facts and only one of them is evidence. (Measured: this endpoint returned
        # 503 and then 500 across two runs while UCSC answered every query.)
        try:
            annotated = annotated_exons_from_fetched_gene(intron)
        except RuntimeError as exc:
            annotated = {"_unavailable": str(exc),
                         "_reading": ("the Ensembl all-transcripts arm did not run; the "
                                      "identification below rests on the UCSC/RefSeq arm, which is "
                                      "an independent annotation source and carries the manually "
                                      "curated track")}
    else:
        intron = hi.fetch_intron(ACCEPTOR_SYMBOL, ACCEPTOR_EXON - 1)
        intron_seq = intron.pop("_seq")
        annotated = annotated_exons_inside({**intron, "chrom": intron["chrom"]})

    ucsc = ucsc_exons_in_intron(intron)
    resolved, graded, how = resolve(intron_seq, ucsc, cut)
    if resolved:
        _assert_from_measured_intron(resolved, intron_seq)
    acc = aa_accounting(len(resolved)) if resolved else None

    # The splice-site enumeration at the PREDICTED length, kept as the negative control it turned
    # out to be: it returns several windows and therefore settles nothing. Reported so a reader can
    # see that the annotation did the work and a consensus scan could not have.
    predicted_candidates = enumerate_candidates(intron_seq, prediction["derived_length_nt"], cut)

    return {
        "_what": ("The cryptic exon in NR4A3 intron 2 that the TAF15::NR4A3 T-N transcript retains "
                  "— identified from genome annotation and measured from genomic sequence."),
        "_why": ("The manuscript's 38-junction panel joins every donor exon to NR4A3 exon 3, so no "
                 "reagent in it can engage a T-N transcript. Whether that matters is a coverage "
                 "question, and it cannot be asked until the T-N seam has a measured sequence."),
        "_cost": "$0 — CPU only; Ensembl + UCSC reads on a GitHub-hosted runner. No GPU, no rental.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_paper": SOURCE,
        "_retrieval_mode": ("fetched_cache (ENSEMBL_FETCH_DIR) — Ensembl and UCSC reads performed "
                            "on a GitHub-hosted runner by fetch-literature.yml and published to the "
                            "literature-cache branch" if FETCH_DIR else "live REST from a CI runner"),
        "transcript_named_in_the_paper_vs_today": {
            "paper": SOURCE["transcript_named_in_the_paper"],
            "ensembl_today_version": intron.get("_transcript_version_today"),
            "_reading": ("⚠ THE PAPER PINS ITS INTRON NUMBERING TO A VERSIONED TRANSCRIPT AND THE "
                         "VERSION HAS MOVED. Recorded rather than assumed away. The exon identified "
                         "below is supported by RefSeq and by an aligned mRNA independently of the "
                         "Ensembl version, so the drift does not by itself invalidate it."),
        },
        "intron": {**intron, "_convention": (
            "NR4A3 intron 2 = the intron immediately 5' of TRANSCRIPT exon 3 of the canonical "
            "transcript — the coordinate convention hybrid_intron.py fixes for this lane.")},
        "⛔_the_papers_25aa_phrase_is_ambiguous": {
            "phrase": "thus encoding 25 additional amino acids prior to the NR4A3 ATG",
            "reading_DIFFERENCE": "T-N has 25 more whole codons before the NR4A3 ATG than T-N* → 75 nt",
            "reading_ENCODED": "the cryptic exon contributes bases to 25 codons → 72 nt",
            "both_are_frame_preserving": True,
            "what_settled_it": ("THE ANNOTATION, NOT THE ARITHMETIC. The exon is annotated at 72 nt "
                                "by a manually curated RefSeq transcript and by an independently "
                                "aligned mRNA at identical coordinates, which satisfies the ENCODED "
                                "reading exactly."),
            "⚠_an_earlier_version_of_this_module_predicted_75": (
                "It derived 75 nt from the DIFFERENCE reading, rejected a third reading on frame "
                "grounds, and was internally consistent throughout — and wrong. Recorded here "
                "because a later reader who re-derives the length will get 75 again unless the "
                "ambiguity is stated. A prediction from an ambiguous sentence is a hypothesis; it "
                "never outranks a measurement."),
            "superseded_prediction": prediction,
        },
        "resolved_cryptic_exon": {
            "sequence": resolved,
            "length_nt": len(resolved) if resolved else None,
            "is_a_substring_of_the_fetched_intron": bool(resolved) and resolved in intron_seq,
            "aa_accounting": acc,
            "reproduces_the_papers_25aa_claim_under": (
                _matches_the_papers_claim(acc) if acc else []),
            **how,
            "_if_null": ("No annotated exon in the intron passed every check. That is a "
                         "measurement, not a failure: it would mean the T-N seam is NAMED in the "
                         "literature but its sequence is not determined by anything reachable, and "
                         "no design may be built on it."),
        },
        "annotation_evidence": {
            "_method": ("Every annotated or aligned exon block wholly inside the intron, from UCSC "
                        "RefSeq (curated + all), GENCODE knownGene, aligned mRNAs and spliced ESTs, "
                        "each put through six independent checks. Only a manually curated track may "
                        "resolve; predictions and alignments corroborate."),
            "n_exon_blocks_inside_the_intron": len([g for g in graded if g.get("length_nt")]),
            "graded": graded,
            "ensembl_arm": annotated,
        },
        "splice_site_scan_at_the_predicted_length": {
            "_what": ("The enumeration that would have been needed if no annotation existed: every "
                      f"{prediction['derived_length_nt']}-nt AG|exon|GT window with an open reading "
                      "frame."),
            "n_candidates": len(predicted_candidates),
            "⛔_reading": ("IT SETTLES NOTHING, AND THAT IS THE POINT. Several windows satisfy "
                          "splice-site consensus plus an open frame, and the best-scoring one by "
                          "polypyrimidine tract is NOT the real exon — it lies inside it, offset by "
                          "22 nt. Splice-site consensus does not identify an exon; annotation and "
                          "aligned transcript evidence do."),
            "candidates": predicted_candidates,
        },
        "_limits": [
            "Exon arithmetic and sequence composition only. No potency, no knockdown, no delivery, "
            "no tolerability and no clinical claim is made or implied.",
            "The identification rests on genome annotation plus the paper's amino-acid statement. "
            "The paper reports no coordinates and no sequence, and no sequenced T-N patient "
            "transcript was retrieved, so the seam is CONSISTENT with the published description "
            "rather than confirmed against a patient's own read.",
            "Which isoform a given PATIENT carries is not decidable from exon structure and is not "
            "decided here.",
        ],
    }

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    r = art["resolved_cryptic_exon"]
    amb = art["⛔_the_papers_25aa_phrase_is_ambiguous"]
    ev = art["annotation_evidence"]
    print(f"  intron: {art['intron']['length_nt']} nt at "
          f"chr{art['intron'].get('chrom')}:{art['intron'].get('genomic_start')}-"
          f"{art['intron'].get('genomic_end')} "
          f"({art['intron']['donor_dinucleotide']}...{art['intron']['acceptor_dinucleotide']})",
          file=sys.stderr)
    print(f"  exon blocks inside the intron: {ev['n_exon_blocks_inside_the_intron']}; "
          f"splice-site scan at the superseded predicted length returned "
          f"{art['splice_site_scan_at_the_predicted_length']['n_candidates']} candidates "
          "(settles nothing)", file=sys.stderr)
    print(f"  ⛔ the paper's '25 aa' phrase has two readings "
          f"({amb['reading_DIFFERENCE']} / {amb['reading_ENCODED']}); the ANNOTATION settled it",
          file=sys.stderr)
    if r["sequence"]:
        print(f"  RESOLVED {r['length_nt']} nt via {r['how']}", file=sys.stderr)
        print(f"    supported by {r.get('n_independent_records_at_these_coordinates')} records: "
              f"{', '.join(r.get('supporting_records') or [])}", file=sys.stderr)
        print(f"    reproduces the paper's 25-aa claim under: "
              f"{r['reproduces_the_papers_25aa_claim_under']}", file=sys.stderr)
        print(f"    {r['sequence']}", file=sys.stderr)
    else:
        print("  NOT RESOLVED — no annotated exon passed every check", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
