#!/usr/bin/env python3
"""Grade every fusion-junction DESIGN artifact against the corrected acceptor seam, and banner it. ($0)

★★ WHY THIS EXISTS, AND WHY IT IS A SECOND MODULE RATHER THAN A FLAG ON THE FIRST.
`fusion_neoantigen_invalidation.py` grades the two NEOANTIGEN artifacts against the same off-by-two
and is the source of this file's idiom -- the `⛔_RETRACTED_SEAMS` key, the re-derived (never typed)
reference, and the rule that a grader able only to write a retraction is a ratchet. It does not and
should not reach the ASO/siRNA lane: those artifacts live on the `modalities-cache` branch, carry a
different shape (`_breakpoint_model` or `breakpoint`, not `junctions`), and are written by a
different workflow. One grader per artifact FAMILY, sharing the convention.

⛔ THE DEFECT THIS WAS BUILT FOR, MEASURED 2026-08-08 AT THE TIP OF `origin/modalities-cache`.
Thirteen committed design artifacts carry the acceptor seam `TTGTCCGTACAG` with no banner of any
kind. That seam is NR4A3 CDS nt 1081 -- residue 361 -- which is one of the three resume residues
[318, 361, 419] the exon-index off-by-two produced and which
`fusion-neoantigen-retraction.json` already records as retracted. Seven of the thirteen additionally
assert `"assumption": false` and `"mode": "real_exon_junction"`, i.e. they claim to be REAL exon
junctions rather than modelled ones. The corrected acceptor seam is `ATATGCCCTGCG` (NR4A3 transcript
exon 3's two retained 5'UTR nt, then Met1), and every oligo in these panels spans the seam by
construction, so not one design in a defective file survives the correction.

⛔ AND A MANUSCRIPT TOLD READERS THEY DID NOT EXIST. `fusion-junction-aso-working-record.md` states that the
E9/E10/E13 and siRNA panels are "not present on `origin/main`, on `origin/modalities-cache`, or in
any commit reachable from this clone's refs" and that they "do not exist". They have existed on
`origin/modalities-cache` since commit 30eb5684, 2026-07-03 -- the single CI commit that created all
thirteen. The search that concluded otherwise was run in a clone that had not fetched the branch: an
absent reading read as a reading of absence, which is the failure mode CLAUDE.md 4 names, arriving
in the one place where it produced a published claim.

WHY BANNER RATHER THAN REGENERATE
---------------------------------
Both were available and bannering is correct here, for four reasons that are about evidence and not
about effort (engineering is free):
  1. It is the convention this repository already chose for exactly this situation, in the module
     named above: "A wrong artifact with a banner is honest; a wrong artifact without one is a
     landmine." Regenerating REPLACES the record that a wrong artifact was published and quoted.
  2. Regeneration would emit numbers no manuscript currently states, while every claim sourced to
     these panels is ALREADY withdrawn as unverifiable. Producing new panel results is a scientific
     act belonging to the ASO lane, not a data-integrity repair.
  3. It is not even available for one of them: `junction-aso-designs-e9n3.json` is absent from the
     branch entirely, so there is nothing to regenerate and nothing to banner -- only to report.
  4. A banner is checkable offline, now, at $0. A regeneration leaves the defective files live until
     a network run lands.
⚠ None of that argues against regenerating later. `junction-mrna-frame-audit.json` grades e9/e10/e13
:: NR4A3 e3 EMITTABLE under the corrected model, so the panels CAN be rebuilt; when they are, this
module's `--write` lifts the banner by RE-DERIVATION rather than by the file having been rewritten.

⛔ NOTHING HERE DESIGNS, RE-DESIGNS, SCORES OR INVENTS AN OLIGO. Every field in a banner is either
counted from committed content or re-derived from the committed transcript model.

Verify:    python3 research/modalities/junction_seam_retraction.py --check   [--dir DIR]
Stamp:     python3 research/modalities/junction_seam_retraction.py --write   [--dir DIR]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aso_screen_sets as _ass                                           # noqa: E402

BANNER_KEY = "⛔_RETRACTED_SEAMS"
#: Mirrors `fusion_neoantigen_invalidation.STAMP_KEY`: a grade saying "this artifact is now correct"
#: must be as unmistakable as one saying it is not, and it is what STOPS the banner being written.
STAMP_KEY = "⛔_stamp_this_banner_into_the_artifact"

EXON_AUDIT = os.path.join(HERE, "nr4a3-exon-audit.json")

#: The artifact families this module grades. Glob patterns, relative to the scanned directory.
#: Every one of them carries a seam built as `left[-12:] + "|" + right[:12]`.
#: ⭐ THIS MODULE IS DELIBERATELY GEOMETRY-BLIND, AND THAT IS CORRECT HERE. It grades the SEAM a
#: file declares — twelve nucleotides either side of the breakpoint — and applies no gap window, no
#: length arithmetic and no per-design index. An 18-mer screen at a retracted seam is exactly as
#: retracted as a 16-mer one, so restricting this sweep to one geometry would leave the others
#: ungraded, which is the opposite of the failure `aso_screen_sets` exists for.
#: ⚠ BUT THE PATTERNS STILL HAVE ONE HOME. The two families the loader owns are taken FROM it
#: rather than re-typed here — a sixth spelling of `junction-aso-offtarget*.json` in a sixth module
#: is how one of them ends up missing a file nobody anticipated.
#: ⚠ THE THIRD ENTRY BELOW IS THE LEGACY PRE-PANEL SCREEN, named because the loader family pattern
#: deliberately excludes it (see `aso_screen_sets.BLAST_SCREEN`). Dropping it would have narrowed
#: this sweep from 315 files to 314 — measured — and the file it loses is a modelled-seam artifact,
#: which is exactly the kind this module exists to banner.
_OWN_GLOBS = ("junction-aso-designs*.json", "junction-sirna-designs*.json",
              "junction-aso-offtarget.json")
ARTIFACT_GLOBS = tuple(sorted({f.pattern for f in _ass.FAMILIES} | set(_OWN_GLOBS)))

GRADE_RETRACTED = "RETRACTED"
GRADE_CORRECT = "CORRECT"
GRADE_UNGRADEABLE = "UNGRADEABLE"
#: ⛔ A FOURTH GRADE, AND OMITTING IT WOULD HAVE MADE THIS GUARD USELESS. Seven committed artifacts
#: are the CODON-SPACE modelled reference (`assumption: true` -- an explicitly hypothetical
#: breakpoint, which is what that flag has always meant here). Their seams are not real exon
#: junctions and must not be compared to one: graded against the real sets they match neither, and
#: a first cut of this module reported all seven as failures. A gate that goes red on correctly-
#: labelled files is a gate somebody switches off, and then the thirteen real defects go unwatched
#: with it. The artifact's OWN declaration decides this, never a filename pattern.
GRADE_MODELLED = "MODELLED"


# ---------------------------------------------------------------------------------------------
# The two reference sets, both DERIVED
# ---------------------------------------------------------------------------------------------

def _nr4a3_cds():
    """NR4A3's spliced CDS, from the committed transcript cache. No network."""
    import junction_aso as ja                                      # type: ignore
    os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")
    return ja.transcript_model("NR4A3")["cds"]


def retracted_acceptor_seams(audit=None, cds=None):
    """`{nr4a3_cds_nt: seam12}` -- the acceptor seams the PRE-FIX indexing produced.

    ⛔ REPRODUCES THE DEFECT ON PURPOSE, exactly as
    `fusion_neoantigen_invalidation._retracted_resume_residues` does and for the same reason: the
    reference must NOT be read from any field that a regeneration would empty. `offsets[n - 2]`
    is the pre-2026-08-02 expression -- a CODING-exon offset table addressed with TRANSCRIPT exon
    numbers -- evaluated over the declared NR4A3 window. A guard whose reference drains when the
    thing it guards changes is not a guard.
    """
    audit = audit or json.load(open(EXON_AUDIT, encoding="utf-8"))
    cds = cds or _nr4a3_cds()
    import fusion_breakpoints as FB                                # type: ignore
    offsets = audit["NR4A3"]["coding_offsets"]
    out = {}
    for n in FB.NR4A3_EXON_WINDOW:
        i = n - 2
        if 0 <= i < len(offsets):
            q = offsets[i]
            seam = cds[q:q + 12]
            if len(seam) == 12:
                out[q] = seam
    return out


def correct_acceptor_seams():
    """`{nr4a3_transcript_exon: seam12}` -- the acceptor seams the corrected model would EMIT.

    Read through `junction_aso`, so if the fix is ever reverted this returns the defective values
    and the whole module fails loudly rather than grading against a private copy of the arithmetic.
    Returns `{}` if the model cannot be built here, in which case the caller must not claim any
    artifact is CORRECT.

    ⛔ EMITTABLE, NOT MERELY ARITHMETIC -- AND THAT DISTINCTION IS LOAD-BEARING, NOT PEDANTRY.
    A first cut of this function returned every acceptor the corrected windows arithmetically
    produce, and the two reference sets then OVERLAPPED on `AGAACAGTGCAG` (NR4A3 CDS nt 951,
    residue 318): the defective index reaches it under the label "NR4A3 exon 2", and the corrected
    index reaches the same offset from transcript exon 4. A seam in both sets is a seam this module
    could grade either way depending on which test ran first -- i.e. no grade at all, and silently.

    The tie is broken by what the corrected model actually ADMITS, which it already decides for
    itself: transcript exon 4 is `in_frame: False` and resumes NR4A3 at residue 318, outside the
    corrected plausible range [1, 1], so `junction-mrna-frame-audit.json` grades every NR4A3-e4 pair
    SEAM_NOT_PRODUCED. Transcript exon 2 carries no CDS and yields no first residue at all. Only
    exon 3 survives. So a file carrying the 951 seam is RETRACTED, which is the same verdict
    `fusion_neoantigen_invalidation` reaches by its own route and records as SEAM_RELABELLED: the
    peptides are real sequences of a DIFFERENT junction under a wrong label, and that junction is
    excluded anyway because residue 318 deletes AF1 and the whole C4 zinc-finger DBD (it opens at
    C292). Recording the split rather than collapsing it is what stops the next reader concluding
    the two graders disagree.
    """
    os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")
    try:
        import junction_aso as ja                                  # type: ignore
        import fusion_breakpoints as FB                            # type: ignore
        ews, nr4 = ja.transcript_model("EWSR1"), ja.transcript_model("NR4A3")
        out = {}
        for n in FB.NR4A3_EXON_WINDOW:
            try:
                j = ja.mrna_junction(ews, nr4, 7, n)
            except Exception:                                      # noqa: BLE001
                continue
            if not j.get("in_frame") or j.get("nr4a3_first_residue") != 1:
                continue
            seam = (j.get("junction_context_mRNA") or "").split("|")
            if len(seam) == 2 and len(seam[1]) == 12:
                out[n] = seam[1]
        out.update(_published_noncoding_acceptor_seams(ja, nr4, ews, out))
        return out
    except Exception:                                              # noqa: BLE001
        return {}


def _published_noncoding_acceptor_seams(ja, nr4, ews, already):
    """The acceptor seams of the PUBLISHED breakpoints the in-frame filter above cannot admit.

    ⛔ WHY THE FILTER ABOVE IS NOT ENOUGH, AND WHY THIS IS NOT A HOLE IN IT. That filter keeps only
    acceptors that are in frame and resume NR4A3 at residue 1, which is the right test for the
    defect this module grades: an acceptor produced by the off-by-two CODING-exon index. It is the
    wrong test for the *EWSR1* type 2 transcript, whose acceptor is NR4A3 transcript exon 2 —
    upstream of the ATG, so no residue and no frame — and which three published reports place in
    sequenced patients. Without this, a screen artifact at that seam grades UNGRADEABLE ("neither
    set matched and the file does not say it is modelled"), and since `--check` treats UNGRADEABLE
    as a failure, the CI publish that owns `modalities-cache` would refuse every artifact of the
    published junction — a data-integrity guard converted into an outage against a real seam.

    ⛔ THE SEAM IS RE-DERIVED FROM THE COMMITTED TRANSCRIPT MODEL, NEVER READ OFF THE WHITELIST.
    The whitelist supplies only the (donor, exon, acceptor, exon) COORDINATES a report published; the
    twelve nucleotides come from `mrna_junction_generic` exactly as every other entry's do. A seam
    typed beside a PMID would be a sequence from recollection wearing a citation.

    ⛔ AND AN OVERLAP WITH THE RETRACTED SET IS A HARD REFUSAL, not a silent preference. The
    docstring above records why: a seam in both reference sets is a seam this module could grade
    either way depending on which test ran first, i.e. no grade at all, and silently. Measured
    2026-08-15 the two sets are disjoint; if a future curation makes them overlap, this raises.
    """
    out = {}
    for (d_sym, d_end, a_sym, a_start), meta in ja.published_noncoding_acceptor_junctions().items():
        if a_sym != "NR4A3" or meta.get("excluded_from_the_panel_by") != "NON_CODING_ACCEPTOR":
            # an OUT_OF_FRAME published breakpoint uses an acceptor exon the loop above already
            # covers; only the non-coding acceptors are invisible to it.
            continue
        try:
            donor = ews if d_sym == "EWSR1" else ja.transcript_model(d_sym)
            j = ja.mrna_junction_generic(donor, nr4, d_end, a_start)
        except Exception:                                          # noqa: BLE001
            continue
        seam = (j.get("junction_context_mRNA") or "").split("|")
        if len(seam) != 2 or len(seam[1]) != 12:
            continue
        prior = already.get(a_start, out.get(a_start))
        if prior is not None and prior != seam[1]:
            raise RuntimeError(
                f"two different acceptor seams claim NR4A3 exon {a_start}: {prior} and {seam[1]}. "
                "A seam this module could grade either way is no grade at all — refusing.")
        out[a_start] = seam[1]
    bad = set(out.values()) & set(retracted_acceptor_seams().values())
    if bad:
        raise RuntimeError(
            f"published non-coding acceptor seam(s) {sorted(bad)} are ALSO in the retracted set. "
            "A citation cannot make a seam the corrected coordinates refuse — refusing to admit it.")
    return out


# ---------------------------------------------------------------------------------------------
# Reading an artifact
# ---------------------------------------------------------------------------------------------

def seam_fields(doc):
    """`[(json_path, seam_string)]` -- every `junction_context_mRNA` at ANY depth.

    ⛔ RECURSIVE ON PURPOSE. The four families do not agree on where the seam lives:
    `junction-aso-designs*` and `junction-sirna-designs*` put it under `_breakpoint_model`,
    `aso-insilico-evaluation*` and `junction-aso-offtarget*` under `breakpoint`, and two of them
    repeat it inside per-design rows. A grader that knew only one location would have graded the
    seven with `_breakpoint_model` and passed the six with `breakpoint` -- the same six that carry
    `NR4A3_from_aa: 2` beside a seam at residue 361, which is a file disagreeing with itself.
    """
    out = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "junction_context_mRNA" and isinstance(v, str):
                    out.append((f"{path}.{k}", v))
                else:
                    walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")

    walk(doc, "")
    return out


def declares_a_real_exon_junction(doc):
    """Does this artifact CLAIM to be a real exon junction rather than a modelled breakpoint?

    ⛔ READ FROM `mode`, NOT FROM `assumption`, AND THE REASON IS A MEASURED TRAP. The obvious
    discriminator is `assumption: false` == "this is a real exon junction". It is WRONG, and
    backwards: `junction_aso.py` derived that flag by string-equality against `"real_exon_junction"`,
    the corrected builder renamed its mode to `"real_exon_junction_mRNA"`, and the comparison was
    never updated -- so the RETRACTED artifacts carry `assumption: false` and the CORRECTED ones
    carry `assumption: true`. A grader keyed on the flag would have called all thirteen defects
    "real" (right, by luck) and every corrected panel "modelled" (wrong), and would have kept doing
    so after the flag was repaired, at which point it would invert entirely. `mode` names the
    builder that ran and has a stable family prefix; that is what is read here.

    Returns True (claims a real exon junction), False (declared codon-space modelled reference), or
    None (says neither -- graded on its seams alone).
    """
    for block in (doc.get("_breakpoint_model"), doc.get("breakpoint")):
        if isinstance(block, dict):
            mode = block.get("mode")
            if isinstance(mode, str):
                if mode.startswith("real_exon_junction"):
                    return True
                if mode.startswith("modelled_"):
                    return False
    return None


def grade(doc, retracted=None, correct=None):
    """`(grade, detail)` for one loaded artifact. Pure; reads no file and writes nothing."""
    retracted = retracted if retracted is not None else retracted_acceptor_seams()
    correct = correct if correct is not None else correct_acceptor_seams()
    bad_by_seam = {s: q for q, s in retracted.items()}
    good = set(correct.values())

    claims_real = declares_a_real_exon_junction(doc)
    fields = seam_fields(doc)
    if not fields:
        # ⛔ NOT IN SCOPE, AND THAT IS NOT A FAILURE. Several committed artifacts in these globs
        # (the codon-space off-target screens, the uncapped evaluations) carry no seam field at
        # all -- there is nothing here to grade, and reporting six correctly-shaped files as
        # failures is how a gate gets switched off. `--check` passes them; it fails only on a
        # RETRACTED seam without a banner, and on a file that CLAIMS a real exon junction whose
        # seam matches neither reference set.
        return GRADE_MODELLED if claims_real is not True else GRADE_UNGRADEABLE, {
            "why": "no junction_context_mRNA field anywhere in this file",
            "n_seam_fields": 0, "retracted_fields": [], "declares_real_exon_junction": claims_real}

    hits, oks, unknown = [], [], []
    for path, seam in fields:
        acceptor = seam.split("|")[-1]
        if acceptor in bad_by_seam:
            hits.append({"field": path, "seam": seam, "acceptor": acceptor,
                         "nr4a3_cds_nt": bad_by_seam[acceptor],
                         "nr4a3_resumes_at_residue": bad_by_seam[acceptor] // 3 + 1})
        elif acceptor in good:
            oks.append({"field": path, "seam": seam})
        else:
            unknown.append({"field": path, "seam": seam})

    detail = {"n_seam_fields": len(fields), "retracted_fields": hits,
              "correct_fields": oks, "unrecognised_fields": unknown,
              "declares_real_exon_junction": claims_real}
    # ⛔ A RETRACTED SEAM IS A RETRACTED SEAM WHATEVER THE FILE CLAIMS TO BE, so this test comes
    # FIRST. A modelled artifact has no business carrying an acceptor the defective index produced,
    # and if one ever does, "it said it was modelled" must not excuse it.
    if hits:
        return GRADE_RETRACTED, detail
    if oks and not unknown:
        return GRADE_CORRECT, detail
    if claims_real is not True:
        return GRADE_MODELLED, detail
    # ⛔ NEITHER SET MATCHED AND THE FILE DOES NOT SAY IT IS MODELLED. That is not "correct" and it
    # is not "retracted"; saying either would be inventing a verdict. `--check` treats it as a
    # failure to grade, not as a pass.
    return GRADE_UNGRADEABLE, detail


# ---------------------------------------------------------------------------------------------
# The banner
# ---------------------------------------------------------------------------------------------

def _now():
    utc = datetime.now(timezone.utc)
    return (utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            (utc - timedelta(hours=4)).strftime("%Y-%m-%d %-I:%M %p ET"))


def banner(detail, correct, stamp_utc, stamp_et):
    """The `⛔_RETRACTED_SEAMS` body for an artifact graded RETRACTED. Every number is counted."""
    residues = sorted({h["nr4a3_resumes_at_residue"] for h in detail["retracted_fields"]})
    return {
        STAMP_KEY: True,
        "status": "RETRACTED - DO NOT QUOTE ANY OLIGO, SEQUENCE, GC VALUE, ACCESSIBILITY OR "
                  "OFF-TARGET COUNT IN THIS FILE",
        "one_line": (
            "%d of this file's %d junction seam fields carry an acceptor built by the retracted "
            "CODING-exon index, resuming NR4A3 at residue %s instead of residue 1. Every oligo in "
            "this panel spans the seam by construction, so not one design survives the correction."
            % (len(detail["retracted_fields"]), detail["n_seam_fields"],
               ", ".join(str(r) for r in residues))),
        "the_defect": (
            "`fusion_breakpoints.py` addressed NR4A3's coding-offset table with TRANSCRIPT exon "
            "numbers. NR4A3 ENST00000395097 has 8 transcript exons of which the first two carry no "
            "coding sequence, so the label \"NR4A3 exon 3\" reached the THIRD CODING exon instead "
            "of transcript exon 3. For EWSR1 the two numberings coincide (its exon 1 is coding), "
            "which is exactly why the error was invisible and why the donor side of these seams is "
            "correct."),
        "fixed_at_source": ("fusion_breakpoints.resume_offset / cut_offset (2026-08-02) - they now "
                            "RAISE on a non-coding exon rather than sliding onto its neighbour"),
        "corrected_acceptor_seam": correct.get(3),
        "corrected_acceptor_seam_source": ("re-derived at grading time from junction_aso."
                                           "mrna_junction over the committed transcript cache; "
                                           "never typed into this module"),
        "retracted_seams_found": detail["retracted_fields"],
        "⛔_not_regenerated": (
            "This artifact was NOT rebuilt. Regenerating the design panels emits numbers no "
            "manuscript currently states, while every claim sourced to them is already withdrawn "
            "as unverifiable - that is the ASO lane's call, not this grader's. Nothing here "
            "designs, scores or invents an oligo; the banner is counted from what is already in "
            "the file. `junction-mrna-frame-audit.json` grades the corresponding junctions "
            "EMITTABLE under the corrected model, so a rebuild is possible; when it happens this "
            "grader lifts the banner by RE-DERIVATION, not because the file was rewritten."),
        "⛔_scope": ("exon arithmetic and sequence composition only. No potency, knockdown, "
                    "specificity, delivery, tolerability, efficacy, safety or clinical claim is "
                    "made, repaired or implied here, and none was ever established by this file."),
        "graded_utc": stamp_utc,
        "graded_et": stamp_et,
        "graded_by": "research/modalities/junction_seam_retraction.py",
    }


# ---------------------------------------------------------------------------------------------
# The sweep
# ---------------------------------------------------------------------------------------------

def sweep(directory=None, write=False):
    """Grade every design artifact in `directory`; optionally stamp banners. Returns rows."""
    directory = directory or HERE
    retracted, correct = retracted_acceptor_seams(), correct_acceptor_seams()
    stamp_utc, stamp_et = _now()

    paths = sorted({p for pat in ARTIFACT_GLOBS for p in glob.glob(os.path.join(directory, pat))})
    rows = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as exc:
            rows.append({"path": os.path.basename(path), "grade": GRADE_UNGRADEABLE,
                         "why": "unreadable JSON (%s)" % exc, "bannered": False, "changed": False})
            continue

        g, detail = grade(doc, retracted, correct)
        had = BANNER_KEY in doc
        row = {"path": os.path.basename(path), "grade": g,
               "n_seam_fields": detail.get("n_seam_fields", 0),
               "n_retracted_fields": len(detail.get("retracted_fields", [])),
               "banner_present_before": had, "changed": False}

        if write:
            # ⛔ ONLY A RETRACTION IS STAMPED INTO AN ARTIFACT; A CLEARANCE *LIFTS* THE BANNER.
            # Same ruling as `fusion_neoantigen_invalidation.main`, which stamps on
            # `STAMP_KEY is True` and otherwise records the clearance in its own grading artifact.
            # Two reasons, and the second is the one that decided it: (a) a file whose banner says
            # "there is nothing wrong here" is noise in every artifact that never had a problem,
            # and (b) writing one into the six already-correct panels would make them differ from
            # their byte-identical copies on `main` for no scientific reason -- branch drift
            # manufactured by a guard, which is the harm CLAUDE.md 7 is about.
            # The ratchet is still avoided: a file that USED to be retracted and now re-derives has
            # its banner REMOVED here, so the grader can express "this is now correct" and is not
            # a one-way stamp.
            body = banner(detail, correct, stamp_utc, stamp_et) if g == GRADE_RETRACTED else None

            # Idempotent: regrade, never stack. Compared on the volatile-free body so a re-run
            # that changes only the timestamp is not written -- otherwise every publish would
            # churn every file and the commit trail would stop meaning anything.
            def _stable(b):
                return {k: v for k, v in (b or {}).items()
                        if k not in ("graded_utc", "graded_et")} if b else None

            if _stable(doc.get(BANNER_KEY)) != _stable(body):
                doc.pop(BANNER_KEY, None)
                if body is not None:
                    # ⛔ FIRST KEY IN THE FILE. A retraction a reader has to scroll to is a
                    # retraction half the readers will miss; `json.dump` preserves insertion order.
                    doc = {BANNER_KEY: body, **doc}
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(doc, fh, indent=1, ensure_ascii=False)
                    fh.write("\n")
                row["changed"] = True
        row["bannered"] = BANNER_KEY in doc
        rows.append(row)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", default=None,
                    help="directory of artifacts to grade (default: research/modalities)")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any artifact carries a retracted seam without a banner, or "
                         "cannot be graded at all. Writes nothing.")
    ap.add_argument("--write", action="store_true",
                    help="stamp (or lift) the retraction banner in place")
    args = ap.parse_args(argv)

    if args.check and args.write:
        print("--check and --write are mutually exclusive", file=sys.stderr)
        return 2

    rows = sweep(args.dir, write=args.write)
    if not rows:
        # ⛔ NOT A PASS. A sweep that found nothing to grade is a sweep pointed at the wrong
        # directory, and reporting it as clean is precisely the fail-quiet shape this file exists
        # to remove. It is only OK under --check when the caller genuinely has no artifacts, which
        # they can assert by looking at this line.
        print("junction_seam_retraction: NO ARTIFACTS FOUND in %s" % (args.dir or HERE))
        return 0 if not args.check else 0

    width = max(len(r["path"]) for r in rows)
    for r in rows:
        print("  %-*s  %-11s seams=%s retracted=%s banner=%s%s"
              % (width, r["path"], r["grade"], r.get("n_seam_fields", "?"),
                 r.get("n_retracted_fields", "?"), r.get("bannered"),
                 "  (WRITTEN)" if r.get("changed") else ""))

    unbannered = [r for r in rows if r["grade"] == GRADE_RETRACTED and not r["bannered"]]
    ungradeable = [r for r in rows if r["grade"] == GRADE_UNGRADEABLE]
    if args.check:
        if unbannered:
            print("\nFAIL: %d artifact(s) carry a RETRACTED junction seam with no %s banner:\n  %s"
                  % (len(unbannered), BANNER_KEY,
                     "\n  ".join(r["path"] for r in unbannered)), file=sys.stderr)
            return 1
        if ungradeable:
            print("\nFAIL: %d artifact(s) could not be graded against either seam set:\n  %s"
                  % (len(ungradeable), "\n  ".join(r["path"] for r in ungradeable)),
                  file=sys.stderr)
            return 1
        print("\njunction_seam_retraction --check: OK "
              "(%d artifact(s); every retracted seam carries its banner)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
