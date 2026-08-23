#!/usr/bin/env python3
"""Does the junction — and the isoform collision — survive a different choice of transcript?

WHAT QUESTION THIS SETTLES. Every peptide in this lane is derived from ONE transcript per gene: the
Ensembl canonical. `fusion_breakpoints.py` picks it, `junction_aso.transcript_model` caches it, and
nothing has ever asked what happens under a different choice. An external reviewer put the objection
directly (aiXiv 1365, W3): the analysis rests on "a curated list of 27 exon pairs" and does not
discuss "how sensitive the isoform-collision finding is to the exact transcript model". That is a
fair reading — a seam defined by exon boundaries is defined by whichever transcript declares them.

⛔ WHAT THIS IS NOT. It is not a claim that any non-canonical transcript is the one a tumour uses.
Which transcript a given patient's fusion transcribes is not decidable from annotation and is not
decided here. What is computed is the SPREAD: across every protein-coding transcript pair, how much
does the seam, the peptide set and the Section B5 isoform collision move? A finding that survives the
spread is a property of the locus; one that does not is a property of a choice nobody defended — the
same distinction Section 2.3 draws for the acceptance threshold.

⚠ AND A TRANSCRIPT THAT CANNOT PRODUCE THE SEAM IS A RESULT, NOT AN ERROR. Most alternative
transcripts will lack the donor or acceptor exon, or place the acceptor's coding start elsewhere.
Each is recorded with the reason it was graded out, because "the finding held on the 3 transcripts
that could express it" and "the finding held on all 40" are different claims and the denominator is
what tells them apart.

Needs Ensembl (CI). Output: junction-transcript-sensitivity.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "junction-transcript-sensitivity.json")
NOVELTY = os.path.join(HERE, "junction-proteome-novelty.json")

#: ⛔ EVERY IN-FRAME DONOR EXON, NOT JUST THE LEAD ONE. The first draft of this file tested EWSR1
#: exon 7 alone, because that is the junction the manuscript leads on — and Section B5's collision is
#: NOT there. `peptides_found_in_proteome` names junctions e9, e10, e12 and e13. Testing e7 would
#: have answered a question nobody asked and reported it as the sensitivity of the collision.
DONOR, ACCEPTOR, ACCEPTOR_EXON = "EWSR1", "NR4A3", 3
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
LENGTHS = [8, 9, 10, 11]


def coding_transcripts(symbol, fb, ens):
    """Every protein-coding transcript of `symbol`, canonical first, as full models.

    ⚠ Built with the SAME construction `_model_from_ensembl` uses, so a difference between two rows
    here is a difference between transcripts and never between two ways of reading one.
    """
    look = fb.get(f"{ens}/lookup/symbol/homo_sapiens/{symbol}?expand=1")
    out = []
    for tr in look["Transcript"]:
        if tr.get("biotype") != "protein_coding" or not tr.get("Translation"):
            continue
        try:
            strand = tr["strand"]
            exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
            exon_lens = [e["end"] - e["start"] + 1 for e in exons]
            tx_ends, cum = [], 0
            for L in exon_lens:
                cum += L
                tx_ends.append(cum)
            cdna = fb.get_text(f"{ens}/sequence/id/{tr['id']}?type=cdna").replace("\n", "").upper()
            cds = fb.get_text(f"{ens}/sequence/id/{tr['id']}?type=cds").replace("\n", "").upper()
            prot = fb.get_text(
                f"{ens}/sequence/id/{tr['Translation']['id']}?type=protein").replace("\n", "")
            if cdna.count(cds) != 1:
                out.append({"transcript": tr["id"], "usable": False,
                            "why": f"CDS occurs {cdna.count(cds)}x in the cdna — 5'UTR ambiguous"})
                continue
            out.append({"transcript": tr["id"], "usable": True,
                        "is_canonical": tr.get("is_canonical") == 1,
                        "model": {"symbol": symbol, "transcript": tr["id"], "strand": strand,
                                  "cdna": cdna, "cds": cds, "protein": prot,
                                  "exon_lens": exon_lens, "tx_ends": tx_ends,
                                  "utr5_len": cdna.index(cds), "n_transcript_exons": len(exons)}})
        except Exception as e:                        # noqa: BLE001 — the reason IS the record
            out.append({"transcript": tr.get("id"), "usable": False,
                        "why": f"{type(e).__name__}: {e}"})
    out.sort(key=lambda r: (not r.get("is_canonical", False), r["transcript"]))
    return out


def main():
    sys.path.insert(0, HERE)
    import fusion_breakpoints as fb
    import junction_aso as ja

    ens = ja.ENS
    try:
        donors = coding_transcripts(DONOR, fb, ens)
        acceptors = coding_transcripts(ACCEPTOR, fb, ens)
    except Exception as e:                            # noqa: BLE001
        json.dump({"⛔_STATUS": "ENSEMBL FETCH FAILED — THIS ARTIFACT CARRIES NO RESULT",
                   "error": f"{type(e).__name__}: {e}"}, open(OUT, "w"), indent=2)
        print(f"  ENSEMBL FETCH FAILED: {e}", file=sys.stderr)
        return 1

    # The Section B5 collision, read from the artifact that owns it rather than retyped.
    collided = []
    if os.path.exists(NOVELTY):
        nov = json.load(open(NOVELTY))
        for r in nov.get("peptides_found_in_proteome", []) or []:
            collided.append(r["peptide"])

    # The in-frame donor exons, read from the artifact that grades them rather than retyped.
    bp = json.load(open(BREAKPOINTS))
    donor_exons = sorted({j["EWSR1_exon_end"] for j in bp.get("junctions", [])})
    if not donor_exons:
        print("  no in-frame junctions in the breakpoint artifact", file=sys.stderr)
        return 1

    rows, seams, peptide_sets = [], {}, {}
    for DONOR_EXON in donor_exons:
      for d in donors:
        for a in acceptors:
            key = f"e{DONOR_EXON}|{d['transcript']}::{a['transcript']}"
            if not d.get("usable") or not a.get("usable"):
                rows.append({"pair": key, "emitted": False,
                             "why": d.get("why") or a.get("why")})
                continue
            try:
                j = ja.mrna_junction_generic(d["model"], a["model"], DONOR_EXON, ACCEPTOR_EXON)
                prot = fb.translate(j["_fusion"][d["model"]["utr5_len"]:])
                j0 = j["donor_last_whole_residue"]
                has_novel = bool(j["donor_coding_phase"])
                peps = sorted(fb.junction_peptides(prot, j0, LENGTHS, novel_residue=has_novel))
                dp = d["model"]["protein"].replace("*", "").rstrip("X")
                ap = a["model"]["protein"].replace("*", "").rstrip("X")
                novel = sorted(p for p in peps if p not in dp and p not in ap)
            except Exception as e:                    # noqa: BLE001 — a refusal is a row
                rows.append({"pair": key, "emitted": False, "why": f"{type(e).__name__}: {e}"})
                continue
            seam = prot[j0] if has_novel else None
            rows.append({
                "pair": key,
                "donor_exon": DONOR_EXON,
                "donor_is_canonical": d.get("is_canonical", False),
                "acceptor_is_canonical": a.get("is_canonical", False),
                "emitted": True,
                "in_frame": j["in_frame"],
                "seam_residue": seam,
                "n_novel_peptides": len(novel),
                "collided_peptides_present": sorted(set(novel) & set(collided)),
            })
            if j["in_frame"]:
                seams.setdefault(str(seam), []).append(key)
                peptide_sets[key] = set(novel)

    emitted = [r for r in rows if r.get("emitted") and r.get("in_frame")]
    canon = [r for r in emitted if r["donor_is_canonical"] and r["acceptor_is_canonical"]]
    shared = set.intersection(*peptide_sets.values()) if peptide_sets else set()
    union = set.union(*peptide_sets.values()) if peptide_sets else set()
    collision_held = [r["pair"] for r in emitted if r["collided_peptides_present"]]

    result = {
        "_what": (f"Sensitivity of every in-frame {DONOR} :: {ACCEPTOR} exon {ACCEPTOR_EXON} "
                  "junction, and of the Section B5 isoform collision, to the "
                  "choice of transcript — every protein-coding transcript pair, not the canonical "
                  "one alone."),
        "_why": ("aiXiv review 1365 (W3): the analysis does not discuss how sensitive the "
                 "isoform-collision finding is to the exact transcript model. A seam defined by "
                 "exon boundaries is defined by whichever transcript declares them."),
        "⛔_what_this_is_not": (
            "NOT a claim that any non-canonical transcript is the one a tumour transcribes. Which "
            "transcript a patient's fusion uses is not decidable from annotation and is not decided "
            "here. This reports the SPREAD across annotated transcripts and nothing else."),
        "_method": ("every protein-coding transcript of each gene built by the same construction "
                    "junction_aso._model_from_ensembl uses, so a difference between rows is a "
                    "difference between transcripts and not between two ways of reading one; the "
                    "junction rebuilt for each pair; peptides filtered against BOTH of that pair's "
                    "own parent proteins."),
        "n_donor_transcripts": len(donors),
        "n_acceptor_transcripts": len(acceptors),
        "n_pairs": len(rows),
        "n_donor_exons": len(donor_exons),
        "n_pairs_emitting_an_in_frame_seam": len(emitted),
        "⚠_denominator": ("pairs that cannot produce the seam are recorded with the reason, not "
                          "dropped: 'held on the pairs that could express it' and 'held on all "
                          "pairs' are different claims."),
        "canonical_pairs": canon,
        "donor_exons_tested": donor_exons,
        "seam_residue_by_pair": seams,
        "n_distinct_seam_residues": len(seams),
        "peptides_shared_by_every_in_frame_pair": sorted(shared),
        "peptides_in_any_in_frame_pair": sorted(union),
        "b5_collided_peptides": sorted(set(collided)),
        "pairs_where_the_b5_collision_still_appears": collision_held,
        "pairs": rows,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"  transcript sensitivity: {len(emitted)}/{len(rows)} pairs emit an in-frame seam; "
          f"{len(seams)} distinct seam residue(s); {len(shared)} peptide(s) common to all; "
          f"B5 collision reappears in {len(collision_held)} pair(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
