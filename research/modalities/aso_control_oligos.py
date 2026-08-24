#!/usr/bin/env python3
"""The two control oligonucleotides the falsification experiment requires, as SEQUENCES.

⭐ WHY THIS EXISTS. External review of the condensed article, 2026-08-24: the paper described its
controls as a CLASS — "a dinucleotide-preserving scramble that must itself pass the mature-parent
screen" — and named no sequence. Nucleic Acid Therapeutics returns without review any manuscript
claiming antisense efficacy that does not carry at least two control oligodeoxynucleotides. This
paper claims no efficacy, so the rule is out of scope on its face; but a submission that describes
controls without naming them invites the screener to decide that question the other way, and the
pipeline already generates and screens exactly these molecules. So they are emitted, screened and
named.

⛔ A SCRAMBLE IS NOT A CONTROL UNTIL IT HAS PASSED THE SAME SCREEN AS THE REAGENT. Section 5 of the
manuscript makes that a condition of ordering, for a measured reason: 10.0% of dinucleotide-
preserving scrambles pair a wild-type parent's whole catalytic gap at the ten-base-pair criterion
and 3.9% do so against wild-type NR4A3. A scramble drawn without screening is therefore a one-in-ten
chance of shipping a second active molecule as a negative control, which would not read as a failed
control — it would read as the reagent not working.

★ WHAT IS PRESERVED, AND WHY IT IS THE RIGHT NULL. The Altschul-Erikson Eulerian shuffle holds the
first base, the last base and every dinucleotide count. So the control matches the reagent in
length, base composition, GC content and nearest-neighbour composition — the properties that drive
duplex stability and much of the chemistry — while destroying the junction it was designed against.
A mononucleotide scramble would not hold the dinucleotide composition, which is why the manuscript
prescribes this one.

⚠ WHAT THIS IS NOT. Not a claim that either control is inert: it is a sequence that fails the same
specificity screen the reagent passes, which is what a negative control has to be. Nothing here has
been synthesised, and the same handling rule applies as to every other sequence in this deposit.

⛔ DETERMINISTIC. One recorded seed, `random.Random` via the same `Rng` the null ensembles use, so
the committed sequences are bit-stable and reproducible from this file alone. The draw index that
survived the screen is recorded, so a reader can see how many candidates were refused.

Run:
    python3 research/modalities/aso_control_oligos.py           # write the artifact
    python3 research/modalities/aso_control_oligos.py --check   # verify the committed sequences
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_parent_gap_pairing as pgp      # noqa: E402 — screen 4, the mature-parent screen
import aso_parent_null as apn             # noqa: E402 — the scramble and the indexed screen
import junction_aso as ja                 # noqa: E402 — ONE home for reverse-complement

OUT = os.path.join(HERE, "aso-control-oligos.json")

#: The reagents each control is drawn against. Named here so a control can never drift from the
#: molecule it is a control FOR.
REAGENTS = (
    {"label": "control-1", "for_reagent": "GGGCATATCATCAAAC", "seam": "EWSR1 e12 :: NR4A3 e3"},
    {"label": "control-2", "for_reagent": "GGGCATATCTTGTGTG", "seam": "TAF15 e6 :: NR4A3 e3"},
)

#: Its own seed, so drawing controls cannot perturb the null ensembles' seed lineage.
SEED = 20260824

#: How many draws to attempt before giving up. At a measured ~10% liability rate a clean draw
#: arrives almost immediately; a run that exhausts this is a finding, not something to retry around.
MAX_DRAWS = 500


def _screen(antisense, parents, idx):
    """(longest parent duplex through the gap, gene) for the TARGET this oligo would engage.

    ⛔ THE SCREEN IS RUN ON THE TARGET, NOT ON THE OLIGO. Screen 4 asks whether a wild-type parent
    transcript pairs the catalytic gap, which is a question about the window the oligo hybridises
    to. Passing the antisense strand here would screen the reverse complement of the real question
    — the orientation defect this lane has already paid for once.
    """
    target = ja.revcomp(antisense)
    return apn._best_run(target, parents, idx)


def build() -> dict:
    parents = pgp.mature_parents()
    idx = apn._gap_index(parents)
    out = []
    for spec in REAGENTS:
        reagent = spec["for_reagent"]
        rng = apn.Rng(SEED ^ sum((i + 1) * ord(c) for i, c in enumerate(spec["label"])))
        reagent_run, reagent_gene = _screen(reagent, parents, idx)
        chosen, refused = None, []
        for draw in range(1, MAX_DRAWS + 1):
            cand, fell_back = apn.scramble_dinucleotide(reagent, rng)
            if fell_back:
                #: A silent mononucleotide fallback would make this a weaker null than the paper
                #: prescribes. Record and skip rather than accept.
                refused.append({"draw": draw, "sequence": cand, "reason": "eulerian fallback"})
                continue
            if cand == reagent:
                refused.append({"draw": draw, "sequence": cand, "reason": "identical to the reagent"})
                continue
            run, gene = _screen(cand, parents, idx)
            if run >= pgp.MIN_DUPLEX_BP:
                refused.append({"draw": draw, "sequence": cand, "reason":
                                f"pairs wild-type {gene} through the whole gap over {run} bp"})
                continue
            chosen = {"draw": draw, "sequence": cand,
                      "longest_parent_duplex_through_gap_bp": run,
                      "longest_parent_duplex_gene": gene}
            break
        if chosen is None:
            raise SystemExit(f"{spec['label']}: no dinucleotide-preserving scramble cleared the "
                             f"mature-parent screen in {MAX_DRAWS} draws")
        out.append({
            **spec,
            "control_5to3": chosen["sequence"],
            "geometry": "5-6-5",
            "draws_until_clean": chosen["draw"],
            "n_draws_refused": len(refused),
            "refused": refused,
            "control_longest_parent_duplex_through_gap_bp":
                chosen["longest_parent_duplex_through_gap_bp"],
            "control_longest_parent_duplex_gene": chosen["longest_parent_duplex_gene"],
            "reagent_longest_parent_duplex_through_gap_bp": reagent_run,
            "reagent_longest_parent_duplex_gene": reagent_gene,
            "preserves": ["length", "first base", "last base", "dinucleotide counts"],
        })
    return {
        "_what": ("Two dinucleotide-preserving scramble controls, one per named reagent, each "
                  "screened against the same mature wild-type parent transcripts as the reagent "
                  "and emitted only if it clears the ten-base-pair criterion."),
        "_why": ("The manuscript prescribed these as a class and named no sequence. External "
                 "review, 2026-08-24."),
        "⛔_not_a_claim_of_inertness": (
            "A control here is a sequence that FAILS the specificity screen the reagent passes, "
            "matched on length, base and dinucleotide composition. Nothing establishes that it has "
            "no biological activity, and nothing here has been synthesised or tested."),
        "_method": ("Altschul-Erikson Eulerian dinucleotide shuffle (aso_parent_null."
                    "scramble_dinucleotide), screened by aso_parent_null._best_run over "
                    "aso_parent_gap_pairing.mature_parents(). Deterministic: one recorded seed."),
        "seed": SEED,
        "min_duplex_bp": pgp.MIN_DUPLEX_BP,
        "n_controls": len(out),
        "controls": out,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-control-oligos.json is stale; re-run without --check", file=sys.stderr)
            return 1
        print("control oligos artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    for c in art["controls"]:
        print(f"  {c['label']}  5'-{c['control_5to3']}-3'  for 5'-{c['for_reagent']}-3'  "
              f"(clean at draw {c['draws_until_clean']}; longest parent duplex "
              f"{c['control_longest_parent_duplex_through_gap_bp']} bp)", file=sys.stderr)
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
