#!/usr/bin/env python3
"""Fetch the PGR canonical transcript model and merge it into `emc-construct-inputs.json`.

⛔ WHY A SEPARATE SCRIPT RATHER THAN ADDING "PGR" TO `emc_fet_construct_designs.GENES`.
That module's `--refresh` re-fetches EVERY gene and rewrites the whole file with a new
`_fetched_utc`. Six committed gene models — and every seam, every design panel and every screen
this repository has emitted — are derived from the values in that file, and
`junction_aso._diff_live_against_cache` exists precisely so a live Ensembl read that DISAGREES with
those cached values stops the run rather than silently replacing them. A blanket re-fetch would
overwrite the very record that guard compares against, which converts a detectable re-annotation
into an invisible one. So this script is ADDITIVE by construction: it fetches ONE symbol, refuses to
touch any gene already present, and leaves the file's `_fetched_utc` and every other byte alone.

⭐ WHY PGR AT ALL. PMID 36103645 (PMC9489176, JCO Precis Oncol 2022) reports an EMC whose fusion is
"gene fusion of progesterone receptor, PGR (exon2) to the 5' untranslated region (UTR) of NR4A3
(exon2)" — a 5' partner no other EMC report names, in a tumour whose "Fluorescent in situ
hybridization was negative for EWSR1 rearrangement". This repository holds transcript models for
five NR4A3 partners (EWSR1, TAF15, TCF12, FUS, TFG) and PGR is not among them, so the junction
cannot be built at all without this fetch. ⛔ It is ONE reported EMC patient — see
`hormone-partner-lane.json`, which owns that count — and nothing here changes that.

NETWORK. Ensembl REST. The dev sandbox 403s it at CONNECT (CLAUDE.md §6), so this runs on a
GitHub Actions runner and publishes back to the triggering branch.

⚠ NOTHING IS TYPED. Every field written is a value `emc_fet_construct_designs.gene_model` READ from
Ensembl on this run — the same function, not a copy of it, so PGR's record is built by exactly the
code that built the other six. The four self-checks that function computes are written with it and
are what `junction_aso._model_from_committed_cache` refuses on.

Run:
    python3 research/modalities/pgr_transcript_fetch.py            # fetch + merge (CI)
    python3 research/modalities/pgr_transcript_fetch.py --check    # offline: is PGR present and sound?
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import emc_fet_construct_designs as efc   # noqa: E402  — ONE home for the Ensembl gene model

INPUTS = os.path.join(HERE, "emc-construct-inputs.json")

#: The symbol to add. Named once; the script refuses to run on anything already in the file.
SYMBOL = "PGR"

#: The four `self_checks` keys `junction_aso._model_from_committed_cache` REQUIRES to be True before
#: it will build a transcript model from this file. Read from there in spirit; asserted here so a
#: record that could never be loaded is never written.
REQUIRED_CHECKS = ("exon_lengths_sum_equals_cdna", "coding_nt_sum_equals_cds",
                   "cdna_slice_at_utr5_equals_cds", "cds_translation_equals_protein")


#: Outer retries around the WHOLE gene model, and the spacing that made the difference.
#: ⛔ MEASURED, NOT GUESSED (Actions run 31887415414, 2026-08-15). That run resolved PGR's canonical
#: transcript, its exon list, its cDNA and its CDS from Ensembl without a hiccup and then died on the
#: LAST of the five calls — `/sequence/id/ENSP00000325120?type=protein` — with, in order, a read
#: timeout, `HTTP 503`, `HTTP 500`, `HTTP 500`. Four different failures on one URL while every other
#: request to the same host in the same job succeeded: that is Ensembl-side transience on one
#: endpoint, not a wrong identifier and not a code fault. `emc_fet_construct_designs._fetch` already
#: retries four times at 1/2/4/8 s — about fifteen seconds of patience — and the outage outlasted it.
#: A longer backoff INSIDE `_fetch` would change the retry behaviour of every lane that shares it, so
#: the extra patience is added out here where its blast radius is this fetch.
#: ⚠ A retry loop must not turn a REAL refusal into a slow one. `gene_model` raises `RuntimeError`
#: only from `_fetch`'s exhausted-retries path; the self-check failures that mean "this model is
#: wrong" are raised by `main()` below, after this returns, and are never retried.
OUTER_TRIES = 5
OUTER_SLEEP_S = 45


def _gene_model_with_outer_retry(symbol: str):
    last = None
    for attempt in range(1, OUTER_TRIES + 1):
        try:
            return efc.gene_model(symbol)
        except RuntimeError as exc:
            last = exc
            print(f"  Ensembl attempt {attempt}/{OUTER_TRIES} failed: {exc}", file=sys.stderr)
            if attempt < OUTER_TRIES:
                time.sleep(OUTER_SLEEP_S)
    raise RuntimeError(
        f"{symbol}: Ensembl did not serve a complete transcript model in {OUTER_TRIES} attempts "
        f"spaced {OUTER_SLEEP_S}s apart. Last error: {last}. Nothing was written — an incomplete "
        "model is not merged, so emc-construct-inputs.json is byte-for-byte unchanged.")


def _load():
    with open(INPUTS, encoding="utf-8") as fh:
        return json.load(fh)


def check(symbol: str = SYMBOL) -> int:
    """Offline: is `symbol` present in the committed cache, and does it pass the four checks?"""
    blob = _load()
    g = (blob.get("genes") or {}).get(symbol)
    if not g:
        print(f"{symbol} is NOT in emc-construct-inputs.json", file=sys.stderr)
        return 1
    checks = g.get("self_checks") or {}
    bad = [k for k in REQUIRED_CHECKS if checks.get(k) is not True]
    if bad:
        print(f"{symbol} is present but records FAILED/absent self-checks {bad}", file=sys.stderr)
        return 1
    print(f"{symbol}: {g['transcript']} — {len(g['cdna'])} nt cDNA, {len(g['cds'])} nt CDS, "
          f"{len(g['protein'])} aa, utr5={g['utr5_len']} nt, {len(g['exons'])} transcript exons, "
          f"fetched {g.get('_fetched_utc')}")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--check" in argv:
        return check()

    blob = _load()
    genes = blob.setdefault("genes", {})
    if SYMBOL in genes:
        # ⛔ REFUSE RATHER THAN OVERWRITE. A second fetch that silently replaced the record would
        # make a re-annotation invisible, which is the whole reason this script is additive.
        print(f"{SYMBOL} is already in emc-construct-inputs.json — refusing to overwrite. "
              "Delete the entry deliberately if a re-fetch is genuinely wanted.", file=sys.stderr)
        return check()

    model = _gene_model_with_outer_retry(SYMBOL)

    # ⭐ RECORD THE GENE'S OWN NAMES, MEASURED. The off-target screens exclude a hit by matching a
    # transcript's DESCRIPTION against a list of parent-gene names (`junction_aso_offtarget.
    # _DONOR_ALIASES`), and every alias in that list has to come from somewhere. Typing PGR's
    # synonyms from recollection is exactly the failure CLAUDE.md §7 forbids, so they are READ from
    # the same Ensembl lookup that produced the transcript and written beside it. A screen that then
    # excludes wild-type PGR hits is excluding them on a fetched name, not a remembered one.
    look = efc._fetch(f"{efc.ENS}/lookup/symbol/homo_sapiens/{SYMBOL}", "application/json")
    model["_ensembl_gene_id"] = look.get("id")
    model["_ensembl_display_name"] = look.get("display_name")
    model["_ensembl_description"] = look.get("description")

    checks = model["self_checks"]
    bad = [k for k in REQUIRED_CHECKS if checks.get(k) is not True]
    if bad:
        # ⛔ A model that fails its own checks is not written at all. `junction_aso` would refuse to
        # load it anyway; writing it would leave a plausible-looking record in the cache that no
        # consumer can use, which is worse than an absent one.
        raise RuntimeError(f"{SYMBOL}: Ensembl model FAILED self-checks {bad} — refusing to write. "
                           f"checks={checks}")

    # ⚠ A PER-GENE FETCH STAMP, because the file-level `_fetched_utc` describes the 2026-08-12
    # six-gene fetch and this record is not part of it. Stamping the file-level field would date
    # six untouched models to today, which is a false provenance for all six.
    model["_fetched_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    model["_added_by"] = "research/modalities/pgr_transcript_fetch.py"
    model["_why"] = ("5' partner of the PGR::NR4A3 fusion reported in PMID 36103645 — the only "
                     "reported EMC case with this partner. Fetched because no transcript model for "
                     "PGR existed in this repository, so the junction could not be built at all.")
    genes[SYMBOL] = model

    # ⚠ `indent=1`, no trailing newline — byte-for-byte the serialisation
    # `emc_fet_construct_designs.py` writes this file with. A reformat would present six untouched
    # gene models as changed in the diff, which is how a real change hides inside a cosmetic one.
    with open(INPUTS, "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=1)
    print(f"merged {SYMBOL} into {os.path.basename(INPUTS)}", file=sys.stderr)
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
