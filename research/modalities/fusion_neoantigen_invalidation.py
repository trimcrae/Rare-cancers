#!/usr/bin/env python3
"""Grade the committed EWSR1::NR4A3 neoantigen artifacts against the CORRECTED junction, and banner them. ($0)

★★ WHY THIS EXISTS.
`fusion_breakpoints.py` addressed NR4A3's exon window by CODING-exon index while labelling it with TRANSCRIPT
exon numbers. NR4A3's canonical transcript `ENST00000395097` has **8 transcript exons of which the first two
carry no coding sequence**, so the two numberings differ by two and every junction the module emitted resumed
NR4A3 two coding exons late. The helpers were fixed at source on 2026-08-02 (`resume_offset` / `cut_offset`,
which now REFUSE a non-coding exon instead of sliding onto its neighbour) and the corrected junction was
reproduced independently from live Ensembl exon structure by rung `R13-a`
(`fusion-object-inventory.json` -> `gate.status == "REPRODUCED"`, junction `EWSR1(1-264)::NR4A3(1-626)`).

⛔ **THE COMMITTED ARTIFACTS PREDATE THE FIX AND WERE NEVER REGENERATED.** Regenerating them needs MHCflurry,
which is that lane's call and is not this module's to make. So this module does the one thing that IS free and
IS owed: it establishes exactly how many predictions are affected, and makes the artifacts SAY SO. A wrong
artifact with a banner is honest; a wrong artifact without one is a landmine.

⛔ NOTHING HERE PREDICTS, RE-PREDICTS, EDITS OR INVENTS A PEPTIDE, A BINDER OR AN AFFINITY. Every peptide and
every number in the banner is COUNTED from what is already committed. The classification is computed by
running the FIXED helpers over the committed exon map (`nr4a3-exon-audit.json`), never from memory and never
from a remembered figure.

WHAT "AFFECTED" MEANS, PRECISELY — and it is not one bucket
----------------------------------------------------------
A committed junction is graded on its NR4A3 CDS resume OFFSET, not on its label, because the label is the
thing that was wrong:
  · `SEAM_NOT_PRODUCED`   — no entry in the declared NR4A3 window produces this offset under the fixed
                            helpers. The seam does not exist. Every peptide crossing it is a sequence no
                            corrected breakpoint yields.
  · `SEAM_RELABELLED`     — the fixed helpers DO produce this offset, but from a different transcript exon
                            than the artifact's label. The peptides are real sequences of that other
                            junction; the label on them is wrong, and R13-a's DBD filter excludes that
                            junction anyway (it deletes AF1 and the whole C4 zinc-finger DBD, which opens at
                            NR4A3 C292 — incompatible with the fusion transactivating the PPARG response
                            element it is reported to act through, Filion 2009 / PMC4429309).
Collapsing the two would be the same class of error as the off-by-two itself, so they are counted separately
and both are reported.
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

#: The artifact this module grades and banners.
BREAKPOINT_ARTIFACT = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
#: The OTHER committed neoantigen artifact, from `fusion_neoantigen.py`'s single modelled breakpoint.
SINGLE_BREAKPOINT_ARTIFACT = os.path.join(HERE, "fusion-neoantigen-predictions.json")
#: The committed exon map, which is where the corrected numbering has its one home.
EXON_AUDIT = os.path.join(HERE, "nr4a3-exon-audit.json")
#: R13-a's inventory, which owns the corrected junction string and the DBD filter.
INVENTORY = os.path.join(HERE, "fusion-object-inventory.json")
#: Committed UniProt sequences, used only to CHECK a seam, never to build one.
SEQ_CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")

BANNER_KEY = "⛔_RETRACTED_SEAMS"


def _model(audit, symbol):
    """A `fusion_breakpoints`-shaped gene model built from the COMMITTED exon audit — no network."""
    g = audit[symbol]
    return {"symbol": symbol,
            "coding_ranks": [e["transcript_exon_rank"] for e in g["exons"] if e["is_coding"]],
            "offsets": g["coding_offsets"]}


def corrected_windows(audit=None):
    """`(nr4a3_resumes, ewsr1_cuts, skipped)` under the FIXED helpers over the DECLARED windows.

    ⛔ The helpers are IMPORTED, not reimplemented: this has to fail if the fix is ever reverted, and a
    private copy of the arithmetic could not.
    """
    import fusion_breakpoints as FB
    audit = audit or json.load(open(EXON_AUDIT, encoding="utf-8"))
    nr4, ews = _model(audit, "NR4A3"), _model(audit, "EWSR1")
    resumes, skipped = {}, []
    for n in FB.NR4A3_EXON_WINDOW:
        try:
            resumes[n] = FB.resume_offset(nr4, n)
        except ValueError as exc:
            skipped.append({"transcript_exon": n, "why": str(exc)})
    cuts = {}
    for e in FB.EWSR1_EXON_WINDOW:
        try:
            cuts[e] = FB.cut_offset(ews, e)
        except ValueError as exc:                                # pragma: no cover - EWSR1 is fully coding
            skipped.append({"transcript_exon": e, "why": str(exc)})
    return resumes, cuts, skipped


def residue_of(cds_nt_offset):
    """The 1-based protein residue a CDS nt OFFSET resumes at — `fusion_breakpoints`' own `q // 3 + 1`."""
    return cds_nt_offset // 3 + 1


def classify(artifact=None, audit=None):
    """The complete count. Pure over committed inputs; returns the banner body."""
    art = artifact or json.load(open(BREAKPOINT_ARTIFACT, encoding="utf-8"))
    resumes, cuts, skipped = corrected_windows(audit)
    produced = set(resumes.values())

    rows, dead_keys, relabelled_keys = [], set(), set()
    for j in art["junctions"]:
        q, p = j["nr4_cds_nt"], j["ews_cds_nt"]
        key = (j["EWSR1_exon_end"], j["NR4A3_exon_start"], q)
        label_exon = j["NR4A3_exon_start"]
        produced_by = sorted(n for n, off in resumes.items() if off == q)
        status = "SEAM_RELABELLED" if produced_by else "SEAM_NOT_PRODUCED"
        (relabelled_keys if produced_by else dead_keys).add(key)
        rows.append({
            "committed_label": "EWSR1 exon %s :: NR4A3 exon %s" % (j["EWSR1_exon_end"], label_exon),
            "ews_cds_nt": p,
            "nr4_cds_nt": q,
            "nr4a3_resumes_at_residue": residue_of(q),
            "junction_context": j["junction_context"],
            "status": status,
            "ewsr1_cut_reproduced": cuts.get(j["EWSR1_exon_end"]) == p,
            "nr4a3_label_reproduced": resumes.get(label_exon) == q,
            "corrected_transcript_exon_that_produces_this_offset": produced_by or None,
            "n_novel_peptides": j["n_novel_peptides"],
            "n_binders": j["n_binders"],
        })

    pep_at, bind_at = {}, {}
    for j in art["junctions"]:
        key = (j["EWSR1_exon_end"], j["NR4A3_exon_start"], j["nr4_cds_nt"])
        for pep in j["novel_peptides"]:
            pep_at.setdefault(pep, set()).add(key)
        for b in j["binders"]:
            bind_at.setdefault(b["peptide"], set()).add(key)

    ranked = [b["peptide"] for b in art.get("predicted_binders_ranked") or []]
    counts = {
        "n_junctions_committed": len(art["junctions"]),
        "n_junctions_seam_not_produced": sum(1 for r in rows if r["status"] == "SEAM_NOT_PRODUCED"),
        "n_junctions_seam_relabelled": sum(1 for r in rows if r["status"] == "SEAM_RELABELLED"),
        "n_junctions_with_a_reproduced_nr4a3_label": sum(1 for r in rows if r["nr4a3_label_reproduced"]),
        "n_junctions_with_a_reproduced_ewsr1_cut": sum(1 for r in rows if r["ewsr1_cut_reproduced"]),
        "n_distinct_novel_peptides": len(pep_at),
        "n_distinct_novel_peptides_only_at_seams_not_produced":
            sum(1 for s in pep_at.values() if s <= dead_keys),
        "n_distinct_novel_peptides_at_a_relabelled_seam":
            sum(1 for s in pep_at.values() if s & relabelled_keys),
        "n_junction_level_peptide_rows": sum(j["n_novel_peptides"] for j in art["junctions"]),
        "n_distinct_predicted_binders": len(ranked),
        "n_distinct_predicted_binders_only_at_seams_not_produced":
            sum(1 for s in bind_at.values() if s <= dead_keys),
        "n_distinct_predicted_binders_at_a_relabelled_seam":
            sum(1 for s in bind_at.values() if s & relabelled_keys),
        "n_junction_level_binder_rows": sum(j["n_binders"] for j in art["junctions"]),
    }
    # ⛔ The two artifact-level totals must agree with what the rows actually contain, or the count is not a
    # count. `n_distinct_binders` is the artifact's own field and is checked, never trusted.
    counts["_selfcheck_ranked_equals_junction_level_binders"] = set(ranked) == set(bind_at)
    counts["_selfcheck_artifact_n_distinct_binders"] = art.get("n_distinct_binders") == len(ranked)
    counts["binders_at_a_relabelled_seam"] = sorted(p for p, s in bind_at.items() if s & relabelled_keys)

    return {"rows": rows, "counts": counts,
            "corrected_nr4a3_resumes": {str(n): {"cds_nt": off, "residue": residue_of(off)}
                                        for n, off in sorted(resumes.items())},
            "corrected_nr4a3_window_entries_skipped_as_non_coding": skipped}


# ---------------------------------------------------------------------------------------------------------
# Who still quotes them
# ---------------------------------------------------------------------------------------------------------

#: Directories scanned for citations. Worktrees and VCS internals are excluded — a stale checkout is not a
#: citation, and counting one would inflate the blast radius.
_SCAN_ROOTS = ("research",)
_SCAN_EXTS = (".md", ".json", ".py", ".txt", ".html")
_EXCLUDE = ("/mainwt2/", "/.git/", "/.claude/", "/__pycache__/", "/node_modules/",
            "/fusion_neoantigen_invalidation.py", "/fusion-neoantigen-retraction.json")


def _excluded(path):
    """Is `path` inside an excluded directory OF THIS REPO?

    ⛔ MATCHED RELATIVE TO `REPO`, AND THAT IS THE WHOLE FIX (2026-08-07). `glob.glob` yields ABSOLUTE
    paths, and the previous test was `x in <absolute path>`. The harness places agent worktrees at
    `<repo>/.claude/worktrees/<id>/`, so when the checkout being scanned IS a worktree, every absolute
    path under it contains `/.claude/` — every file matched the exclusion, `consumers()` returned an
    empty list, and this guard reported that NOTHING consumes a retracted artifact.

    ⚠ THAT IS FAIL-QUIET IN A MEDICAL-INTEGRITY GUARD. It does not error, it does not warn: it answers
    the question it was asked with a clean, confident, wrong "none". An absent reading read as a reading
    of absence, in the one check whose job is to find every file still quoting withdrawn peptides.
    Proven by copying an identical tree to a path without `/.claude/`, where the same file's 13 tests
    pass. CI checks out to `/home/runner/work/...`, so `main` never saw it — only every agent did.

    ⚠ NOTHING IS LOOSENED. The same directory names are excluded; they are now anchored to the repo
    root instead of matching anywhere in an absolute path, which is what the comment above always said
    they meant. `/mainwt2/` is retained for the same reason it was added — it is another checkout name.
    """
    rel = "/" + os.path.relpath(path, REPO).replace(os.sep, "/")
    return any(x in rel for x in _EXCLUDE)


def peptides_of(art):
    """Every peptide string the artifact asserts, junction-level and ranked."""
    peps = {p for j in art.get("junctions") or [] for p in j.get("novel_peptides") or []}
    peps |= {b["peptide"] for j in art.get("junctions") or [] for b in j.get("binders") or []}
    peps |= {b["peptide"] for b in art.get("predicted_binders_ranked") or []}
    peps |= set(art.get("novel_peptides") or [])
    for k in ("binders", "top_predictions"):
        peps |= {r["peptide"] for r in (art.get(k) or []) if isinstance(r, dict) and "peptide" in r}
    return {p for p in peps if p}


def consumers(artifact_basename, self_paths=()):
    """`[{path, kind}]` — every committed file that READS or NAMES the artifact by filename.

    ⛔ A DIFFERENT AND MORE SERIOUS CLASS THAN A QUOTED PEPTIDE. A prose file quoting a peptide is one wrong
    sentence; a module that LOADS this artifact recomputes its own numbers from it, so its outputs inherit
    the defect whether or not they ever print a peptide. `hla_coverage.py` and `vaccine_construct.py` are
    both in this class, and neither would have appeared in a peptide-string scan of their outputs alone.
    """
    selves = {os.path.abspath(p) for p in self_paths}
    out = []
    for root in _SCAN_ROOTS:
        for path in sorted(glob.glob(os.path.join(REPO, root, "**", "*"), recursive=True)):
            if not os.path.isfile(path) or os.path.splitext(path)[1] not in _SCAN_EXTS:
                continue
            if _excluded(path) or os.path.abspath(path) in selves:
                continue
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:                                       # pragma: no cover
                continue
            if artifact_basename not in text:
                continue
            out.append({"path": os.path.relpath(path, REPO),
                        "kind": _reference_kind(path, text, artifact_basename)})
    return sorted(out, key=lambda r: (r["kind"], r["path"]))


#: Names a Python binding that a later `open(...)`/`json.load(...)` uses. Kept deliberately narrow — a broad
#: "the file mentions `open(` somewhere" test put SIX modules in the CODE class that only NAME the artifact
#: in a comment, which would have overstated the blast radius. Overstating it is not the safe direction:
#: it is what makes a list nobody trusts, and an untrusted list is not acted on.
_BINDING = ("=", ":")


def _reference_kind(path, text, basename):
    """How `path` refers to the artifact — WRITES / LOADS / names it. Conservative by construction."""
    if not path.endswith(".py"):
        return "names the artifact (prose or data)"
    lines = text.split("\n")
    hit_lines = [l for l in lines if basename in l]
    # bound to a module constant, then that constant is opened/loaded elsewhere
    consts = set()
    for l in hit_lines:
        head = l.split("=")[0].strip()
        if "=" in l and head.isidentifier():
            consts.add(head)
    _READS = ("open(", "json.load", "_load(", "read_text(", "loads(")
    opens_const = any(c in l and any(r in l for r in _READS) for c in consts for l in lines)
    writes = any(('"w"' in l or "'w'" in l) and any(c in l for c in consts) for l in lines) or \
        any(c in ("OUT", "OUTPUT", "DEST") for c in consts)
    # ⚠ ALSO the literal-argument shape — `_load("fusion-breakpoint-neoantigens.json")`. Missing it left
    # `fusion_object_inventory.py`, which is the module that FLAGGED this defect, off its own consumer list.
    direct = any(any(r in l for r in _READS) for l in hit_lines)
    if writes:
        return "CODE — WRITES this artifact (its producer)"
    if opens_const or direct:
        # ⛔ A GUARD IS NOT A CONSUMER. A test that opens the artifact to assert the banner is there does not
        # inherit the defect, and counting it would inflate the blast radius — which is the fastest way to
        # make this list untrusted, and an untrusted list is not acted on.
        if "/tests/" in path.replace(os.sep, "/") or os.path.basename(path).startswith("test_"):
            return "TEST — loads it as a guard (does not inherit the defect)"
        return "CODE — LOADS this artifact and recomputes from it"
    return "code comment / docstring reference only"


def citations(peps, self_paths=()):
    """`[{path, n_peptides_quoted, examples}]` — every committed file quoting one of `peps`.

    ⛔ EXACT SUBSTRING, never fuzzy. A peptide is a literal string; a near-match is not a citation, and
    pretending it is would put files on this list that do not belong there.
    """
    selves = {os.path.abspath(p) for p in self_paths}
    out = []
    for root in _SCAN_ROOTS:
        for path in sorted(glob.glob(os.path.join(REPO, root, "**", "*"), recursive=True)):
            if not os.path.isfile(path) or os.path.splitext(path)[1] not in _SCAN_EXTS:
                continue
            if _excluded(path) or os.path.abspath(path) in selves:
                continue
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:                                       # pragma: no cover
                continue
            hits = sorted(p for p in peps if p in text)
            if hits:
                out.append({"path": os.path.relpath(path, REPO),
                            "n_peptides_quoted": len(hits),
                            "examples": hits[:6]})
    return sorted(out, key=lambda r: (-r["n_peptides_quoted"], r["path"]))


# ---------------------------------------------------------------------------------------------------------
# The banners
# ---------------------------------------------------------------------------------------------------------


def _corrected_junction():
    """The corrected junction string, READ from the artifact that reproduced it (rule 1: one home)."""
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    gate = inv["gate"]
    if gate.get("status") != "REPRODUCED":
        raise SystemExit("REFUSED: %s's gate is %r, not REPRODUCED — nothing may be graded against it"
                         % (os.path.basename(INVENTORY), gate.get("status")))
    return gate["junction"], gate


def _rederive_breakpoint_panel():
    """The panel the CORRECTED transcript model produces, re-derived here from committed inputs.

    ⛔ THIS IS THE GATE'S EVIDENCE AND IT NEVER READS THE ARTIFACT. It rebuilds the graded window
    from `emc-construct-inputs.json` (pinned to `TRANSCRIPT_SOURCE=cache`, so $0 and no network)
    and returns `{junction_label: expected_row}` for every pair graded EMITTABLE. The banner may
    only be lifted when the committed artifact MATCHES this — a file that was merely rewritten is
    not a file that was verified. Returns None if the re-derivation cannot be done at all, in
    which case the caller must NOT claim the artifact is cleared.
    """
    os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")
    sys.path.insert(0, HERE)
    try:
        import junction_aso as ja                                  # type: ignore
        import fusion_breakpoints as fb                            # type: ignore
        ews, nr4 = ja.transcript_model("EWSR1"), ja.transcript_model("NR4A3")
        graded = ja.graded_window(ews, nr4, keep_sequences=True)
        return {r["junction_label"]: fb.emit_junction(ews, nr4, r)
                for r in graded if r["grade"] == ja.EMITTABLE}, ews, nr4
    except Exception:                                              # noqa: BLE001
        return None


def _retracted_resume_residues():
    """The NR4A3 resume residues the RETRACTED artifact carried — RE-DERIVED, never typed.

    ⛔ Reproduces the pre-2026-08-02 indexing (`offsets[n - 2]`, a CODING-exon table addressed with
    TRANSCRIPT exon numbers) over the declared window, from the committed exon audit, and returns
    the residues it yields. This is deliberately NOT read from
    `fusion-object-inventory.json -> neoantigen_lane_flag.stale_resume_residues`: that field is
    computed BY READING THE ARTIFACT, so the moment the artifact is regenerated the field empties
    and a check sourced from it would silently pass on anything. A guard whose reference drains
    when the thing it guards changes is not a guard.
    """
    audit = json.load(open(EXON_AUDIT, encoding="utf-8"))
    offsets = audit["NR4A3"]["coding_offsets"]
    import fusion_breakpoints as FB
    return sorted({offsets[n - 2] // 3 + 1 for n in FB.NR4A3_EXON_WINDOW
                   if 0 <= n - 2 < len(offsets)})


def _breakpoint_panel_clearance(art):
    """`(cleared: bool, checks: list)` — can the retraction banner be LIFTED from this artifact?

    Every check is a comparison against `_rederive_breakpoint_panel()`, which never reads the
    artifact. A single failure withholds the clearance; the checks are all reported either way,
    because a refusal that cannot say what it refused is the failure mode this module exists for.
    """
    red = _rederive_breakpoint_panel()
    if red is None:
        return False, [{"check": "the corrected panel can be re-derived from committed inputs",
                        "got": "re-derivation failed", "want": "a graded window", "ok": False}]
    expected, ews, nr4 = red
    ews_prot = ews["protein"].replace("*", "").rstrip("X")
    nr4_prot = nr4["protein"].replace("*", "").rstrip("X")
    got_rows = {j.get("junction_label"): j for j in art.get("junctions") or []}
    checks = []

    def add(name, got, want, ok=None):
        checks.append({"check": name, "got": got, "want": want,
                       "ok": bool(got == want) if ok is None else bool(ok)})

    # 1. the junction SET, exactly — no padding back to a remembered denominator, no omissions
    add("the artifact's junction set is exactly the set graded EMITTABLE by the transcript model",
        sorted(got_rows), sorted(expected))
    # 2/3/4. per junction: seam, frame, resume residue — all re-derived, none read from the file
    seam_bad, frame_bad, resume_bad, pep_bad = [], [], [], []
    for label, exp in expected.items():
        got = got_rows.get(label)
        if not got:
            continue
        if got.get("junction_context_protein_seam") != exp["junction_context_protein_seam"] or \
                got.get("seam_codon_residue") != exp["seam_codon_residue"]:
            seam_bad.append(label)
        if not got.get("in_frame") or got.get("frame_sum_mod3") != 0:
            frame_bad.append(label)
        if got.get("nr4a3_first_residue") != 1:
            resume_bad.append(label)
        if sorted(got.get("novel_peptides") or []) != exp["novel_peptides"]:
            pep_bad.append(label)
    add("every junction's seam reproduces the re-derived seam (context AND novel codon residue)",
        seam_bad, [])
    add("every junction is in frame at the mRNA level ((cut + acceptor 5'UTR) mod 3 == 0)",
        frame_bad, [])
    add("every junction retains NR4A3 from residue 1 (Met1 survives as an internal residue)",
        resume_bad, [])
    add("every junction's novel-peptide set reproduces the re-derived set",
        pep_bad, [])
    # 5. none of the retracted resume residues survives anywhere in the file
    stale = _retracted_resume_residues()
    add("no junction resumes at a retracted residue %s" % stale,
        sorted({j.get("nr4a3_first_residue") for j in got_rows.values()} & set(stale)), [])
    # 6. every quoted peptide is genuinely absent from both parents — the novelty claim, rechecked
    quoted = peptides_of(art)
    add("every peptide the artifact asserts is absent from BOTH parent proteins",
        sorted(p for p in quoted if p in ews_prot or p in nr4_prot), [])
    # 7. refusals are RECORDED, not omitted: a row for every declared exon pair
    e_win, n_win = (art.get("windows") or {}).get("EWSR1_exons") or [], \
        (art.get("windows") or {}).get("NR4A3_exons") or []
    add("every declared exon pair carries a graded row, refusals included",
        len(art.get("junctions_graded") or []), len(e_win) * len(n_win))
    return all(c["ok"] for c in checks), checks


def breakpoint_banner(stamp_utc, stamp_et):
    art = json.load(open(BREAKPOINT_ARTIFACT, encoding="utf-8"))
    art.pop(BANNER_KEY, None)                                     # idempotent: regrade, never stack banners
    junction, gate = _corrected_junction()

    # ⭐ THE CLEARED OUTCOME COMES FIRST, AND IT IS A RE-DERIVATION (2026-08-07). A grader that can
    # only ever write a retraction is a ratchet: once the artifact is regenerated correctly,
    # `--write` would stamp the same banner back onto a CORRECT file — and `classify()` would raise
    # on the way, because it reads `nr4_cds_nt`, a CDS-space key the corrected artifact does not
    # and must not carry. Same ruling as `single_breakpoint_banner`: the state a grader cannot
    # express is the state it will get wrong.
    cleared, cl_checks = _breakpoint_panel_clearance(art)
    if cleared:
        cits = citations(peptides_of(art), self_paths=(BREAKPOINT_ARTIFACT,))
        cons = consumers(os.path.basename(BREAKPOINT_ARTIFACT), self_paths=(BREAKPOINT_ARTIFACT,))
        strong = [b for b in art.get("predicted_binders_ranked") or []
                  if b.get("class") == "strong"]
        return {
            STAMP_KEY: False,
            "status": "CLEARED — regenerated on the corrected transcript model and it re-derives",
            "one_line": (
                "%d of %d declared exon pairs are EMITTABLE (in frame at the mRNA level AND "
                "resuming NR4A3 at residue 1); each carries %d junction-spanning peptides absent "
                "from both parents, and the screen returns %d distinct predicted binders, %d of "
                "them strong. The retracted 7-junction set is not recovered and was not padded "
                "back to: the corrected denominator is %d."
                % (art.get("n_inframe_junctions"), art.get("n_candidate_exon_pairs"),
                   (art.get("junctions") or [{}])[0].get("n_novel_peptides"),
                   art.get("n_distinct_binders"), len(strong), art.get("n_inframe_junctions"))),
            "corrected_junction": junction,
            "what_was_checked": cl_checks,
            "⭐_how_the_junction_set_changed": (
                "the retracted artifact carried 7 junctions built in CDS coordinates from a "
                "CODING-exon index. The corrected set is %s. e11 drops (its cut is codon-aligned, "
                "so with the acceptor's 2 retained 5'UTR nt the register no longer composes), the "
                "NR4A3 exon-4 acceptors drop as SEAM_NOT_PRODUCED, and the NR4A3 exon-2 acceptors "
                "are now EXPLICIT refusals with their 176 retained 5'UTR nt recorded rather than "
                "silent stderr omissions. Full per-pair grading: `junctions_graded`; the "
                "disjointness of the two models: `_superseded_cds_model_comparison`."
                % sorted(j["junction_label"] for j in art["junctions"])),
            "⛔_what_this_does_NOT_establish": (
                "predicted MHC-I binding is a SCREEN, not presentation and not immunogenicity. No "
                "efficacy, safety, tolerability or clinical claim is made or implied. Which exon "
                "pair a given patient carries is not decidable from exon structure and is not "
                "decided here."),
            "⛔_scope": "sequence composition and predicted binding only.",
            "downstream_citations": cits,
            "downstream_consumers": cons,
            "⚠_downstream_outputs_are_not_regenerated_by_this": (
                "`hla_coverage.py`, `vaccine_construct.py` and `coverage_scan.py` LOAD this "
                "artifact and recompute from it. Their committed outputs were built on the "
                "RETRACTED junction set and are not repaired by this clearance — each must be "
                "re-run before any of its numbers is quoted."),
            "graded_utc": stamp_utc,
            "graded_et": stamp_et,
            "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
        }, art

    # ⚠ A REGENERATED-BUT-UNVERIFIED ARTIFACT IS ITS OWN STATE AND MUST NOT CRASH THE GRADER.
    # `classify()` needs the CDS-space keys, so an artifact in the corrected shape that FAILS the
    # clearance would raise KeyError — and a traceback is not a verdict.
    if not all("nr4_cds_nt" in j for j in art.get("junctions") or [{}]):
        return {
            STAMP_KEY: True,
            "status": "RETRACTED — regenerated in the corrected shape but it did NOT re-derive",
            "one_line": ("this artifact is no longer in the CDS-coordinate shape the original "
                         "retraction graded, but it does not reproduce the panel re-derived from "
                         "committed inputs. Quote nothing until the failing checks below pass."),
            "corrected_junction": junction,
            "what_was_checked": cl_checks,
            "⛔_scope": "sequence composition only. No affinity, immunogenicity or clinical claim.",
            "graded_utc": stamp_utc, "graded_et": stamp_et,
            "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
        }, art

    graded = classify(art)
    c = graded["counts"]
    cits = citations(peptides_of(art), self_paths=(BREAKPOINT_ARTIFACT,))
    cons = consumers(os.path.basename(BREAKPOINT_ARTIFACT), self_paths=(BREAKPOINT_ARTIFACT,))
    banner = {
        "status": "RETRACTED — DO NOT QUOTE ANY PEPTIDE, BINDER OR AFFINITY IN THIS FILE",
        "one_line": ("all %d junctions carry an NR4A3 exon label the corrected exon map does not reproduce; "
                     "%d of them resume at an offset no corrected window entry produces at all, and %d of "
                     "the %d distinct predicted binders exist only at those non-existent seams."
                     % (c["n_junctions_committed"], c["n_junctions_seam_not_produced"],
                        c["n_distinct_predicted_binders_only_at_seams_not_produced"],
                        c["n_distinct_predicted_binders"])),
        "corrected_junction": junction,
        "corrected_junction_source": {
            "artifact": "fusion-object-inventory.json",
            "gate_status": gate.get("status"),
            "checks": gate.get("checks"),
            "_phase_caveat_has_one_home_there": gate.get("_phase_note"),
        },
        "the_defect": (
            "`fusion_breakpoints.py` indexed NR4A3's `offsets` array (CODING exons) with numbers from a "
            "window written in TRANSCRIPT exon numbers. NR4A3 ENST00000395097 has 8 transcript exons of "
            "which exons 1 and 2 carry no coding sequence, so the label \"NR4A3 exon 3\" addressed the "
            "THIRD CODING exon (transcript exon 5, residue 361) instead of transcript exon 3 (residue 1). "
            "Every junction in this file therefore deleted NR4A3's AF1 and the first zinc finger of the C4 "
            "DBD, which opens at C292."),
        "fixed_at_source": "fusion_breakpoints.resume_offset / cut_offset (2026-08-02) — they now RAISE on a "
                           "non-coding exon rather than sliding onto its neighbour",
        "⛔_not_regenerated": ("regenerating this artifact requires MHCflurry-2.0, which is the neoantigen "
                              "lane's call and not this module's. NOTHING here was re-predicted: every "
                              "number in this banner is COUNTED from the committed content below."),
        "counts": c,
        "junctions_graded": graded["rows"],
        "corrected_nr4a3_resumes_over_the_declared_window": graded["corrected_nr4a3_resumes"],
        "corrected_nr4a3_window_entries_skipped_as_non_coding":
            graded["corrected_nr4a3_window_entries_skipped_as_non_coding"],
        "⚠_how_this_reconciles_with_R13a": (
            "`fusion-object-inventory.json` -> `neoantigen_lane_flag` reports `all_seams_stale: true` and "
            "`stale_resume_residues: [318, 361, 419]`. That is CORRECT as written and this grading does not "
            "contradict it — the two use different reference sets ON PURPOSE. R13-a compares against the "
            "PLAUSIBLE corrected breakpoints, i.e. after its DBD filter, which leaves only NR4A3 residue 1; "
            "this module compares against every offset the corrected windows ARITHMETICALLY produce, which "
            "is residues 1 and 318. Residue 318 is therefore stale to R13-a (implausible) and produced to "
            "this module (arithmetic), and BOTH conclusions are the same: none of these binders may be "
            "quoted. Recording the split rather than collapsing it is what stops the next reader deciding "
            "the two artifacts disagree."),
        "⚠_the_one_relabelled_seam": (
            "one committed junction (EWSR1 exon 11 :: NR4A3 CDS nt 951, residue 318) resumes at an offset "
            "the corrected helpers DO produce — but from transcript exon 4, not the \"exon 2\" this file "
            "labels it. Its %d peptides and %d binders are real sequences of THAT junction under a wrong "
            "label, and that junction is itself excluded by R13-a's DBD filter (residue 318 deletes AF1 and "
            "the whole C4 zinc-finger DBD). It is counted separately above and is still not quotable here."
            % (c["n_distinct_novel_peptides_at_a_relabelled_seam"],
               c["n_distinct_predicted_binders_at_a_relabelled_seam"])),
        "downstream_citations": cits,
        "downstream_consumers": cons,
        "⛔_downstream_note": ("`downstream_citations` are files quoting peptide STRINGS from this artifact; "
                              "`downstream_consumers` are files that LOAD it and recompute — the more "
                              "serious class, because their numbers inherit the defect without ever "
                              "printing a peptide. A retracted input still quoted downstream is the more "
                              "serious half of the defect: each needs its own correction, and NONE of them "
                              "is fixed by this banner. ⚠ Two of the loaders — `nr4a3_exon_audit.py` and "
                              "`fusion_object_inventory.py` — read it in order to AUDIT it and are the "
                              "modules that diagnosed the defect; they are listed because they load it, not "
                              "because they inherit it. Test files that load it as a guard are classed "
                              "separately for the same reason."),
        "⛔_scope": ("exon arithmetic and sequence composition only. No affinity, presentation, "
                    "immunogenicity, efficacy, safety or clinical claim is made, repaired or implied here, "
                    "and none was ever established by this artifact."),
        "graded_utc": stamp_utc,
        "graded_et": stamp_et,
        "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
    }
    return banner, art


#: A grade that says "this artifact is now correct" must be as unmistakable as one that says it is not, and
#: it must be the thing that STOPS the banner being written. Two states, one key, checked by main().
STAMP_KEY = "⛔_stamp_this_banner_into_the_artifact"


def _expected_corrected_seam():
    """The corrected 10-residue right context, DERIVED — never typed here.

    Committed inputs only: `junction_aso` is pinned to `TRANSCRIPT_SOURCE=cache` so this module keeps its
    "$0, no network, no prediction" contract, and the transcript model it returns is gated against
    `nr4a3-exon-audit.json` on the way through. Returns (right10, novel_residue_aa, grading) or None if the
    junction cannot be built here — in which case the caller must NOT claim the artifact is cleared.
    """
    os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")
    sys.path.insert(0, HERE)
    try:
        import junction_aso as ja                                  # type: ignore
        import fusion_breakpoints as fb                            # type: ignore
        ews, nr4 = ja.transcript_model("EWSR1"), ja.transcript_model("NR4A3")
        j = ja.mrna_junction(ews, nr4, 7, 3)
        prot = fb.translate(j["_fusion"][ews["utr5_len"]:])
        j0 = j["ewsr1_last_whole_residue"]
        novel = prot[j0] if j["ewsr1_coding_phase"] else None
        return prot[j0:j0 + 10], novel, {k: v for k, v in j.items() if not k.startswith("_")}
    except Exception:                                              # noqa: BLE001
        return None


def single_breakpoint_banner(stamp_utc, stamp_et):
    """The OTHER artifact. A weaker, accurate label — it is not the off-by-two, and must not be called it.

    ⭐ AND IT IS NOW ALSO THE THING THAT LIFTS THAT LABEL (2026-08-06). A grader that can only ever write a
    retraction is a ratchet: once the artifact is regenerated correctly, re-running this module would stamp
    the SAME banner back onto a CORRECT file — and `kept_from` would compute to `None`, so the banner would
    have read "resumes at residue None". The state a grader cannot express is the state it will get wrong,
    so `CLEARED` is a first-class outcome here and it is what withholds the banner.
    """
    art = json.load(open(SINGLE_BREAKPOINT_ARTIFACT, encoding="utf-8"))
    art.pop(BANNER_KEY, None)
    junction, _gate = _corrected_junction()
    seqs = json.load(open(SEQ_CACHE, encoding="utf-8"))
    nr4 = seqs["NR4A3"]
    model = art["_breakpoint_model"]
    right10 = model["junction_context_right10"]
    kept_from = 2 if right10 == nr4[1:11] else (1 if right10 == nr4[0:10] else None)
    cits = citations(peptides_of(art), self_paths=(SINGLE_BREAKPOINT_ARTIFACT, BREAKPOINT_ARTIFACT))

    expected = _expected_corrected_seam()
    if expected and right10 == expected[0]:
        exp_right10, novel_aa, grading = expected
        return {
            STAMP_KEY: False,
            "status": "CLEARED — regenerated against the corrected junction and it reproduces",
            "corrected_junction": junction,
            "modelled_junction": "EWSR1(1-%d)::[%s]::NR4A3(%d-%d)" % (
                grading["ewsr1_last_whole_residue"], novel_aa or "no novel residue",
                grading["nr4a3_first_residue"], len(nr4)),
            "what_was_checked": [
                {"check": "the artifact's junction_context_right10 equals the seam derived from the "
                          "transcript model at EWSR1 e7 :: NR4A3 e3",
                 "got": right10, "want": exp_right10, "ok": True},
                {"check": "NR4A3 is retained from residue 1 (Met1 survives as an internal residue)",
                 "got": grading["nr4a3_first_residue"], "want": 1, "ok": True},
                {"check": "NR4A3 Met1 is where the committed UniProt cache says it is",
                 "got": nr4[0], "want": "M", "ok": nr4[0] == "M"},
                {"check": "the chimeric ORF is in frame ((cut + acceptor 5'UTR) mod 3 == 0)",
                 "got": grading["frame_sum_mod3"], "want": 0, "ok": grading["frame_sum_mod3"] == 0},
                {"check": "no peptide from the superseded seam survives in the artifact",
                 "got": sorted(p for p in peptides_of(art) if p in nr4 or "PCVQAQY" == p[:7]),
                 "want": [], "ok": not any(p in nr4 for p in peptides_of(art))},
            ],
            "⭐_what_the_earlier_banner_left_open_and_this_settles": (
                "the earlier grade called the difference ONE residue (NR4A3 Met1) and left the splice-PHASE "
                "question open. It is TWO residues: EWSR1 exon 7 ends 1 nt past a codon boundary and NR4A3's "
                "acceptor exon retains %d 5'UTR nt, which compose into a NOVEL codon (%s) belonging to "
                "neither parent, and Met1 then follows. The resolution has its one home in "
                "fusion-object-inventory.json -> gate._phase_note_resolution."
                % (grading["nr4a3_acceptor_exon_5utr_nt_retained"], novel_aa)),
            "n_spanning_peptides": art.get("n_spanning_peptides"),
            "n_predicted_binders": art.get("n_predicted_binders_by_percentile"),
            "downstream_citations": cits,
            "⛔_what_this_does_NOT_establish": (
                "predicted MHC-I binding is a screen, not presentation and not immunogenicity. Which exon "
                "pair a given patient carries is not decidable from exon structure and is not decided here. "
                "No efficacy, safety, tolerability or clinical claim is made or implied."),
            "⛔_scope": "sequence composition and predicted binding only.",
            "graded_utc": stamp_utc,
            "graded_et": stamp_et,
            "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
        }, art

    return {
        STAMP_KEY: True,
        "status": "NOT VERIFIED AGAINST THE CORRECTED JUNCTION — its seam is one residue off",
        "⛔_this_is_a_different_defect_from_the_off_by_two": (
            "this artifact was NOT built by `fusion_breakpoints.py` and does not carry the coding/transcript "
            "exon slip. It models ONE declared breakpoint, and its EWSR1 half (kept to residue 264) matches "
            "the corrected junction exactly."),
        "corrected_junction": junction,
        "modelled_junction": "EWSR1(1-%s)::NR4A3(%s-%s)" % (len(seqs["EWSR1"][:264]), kept_from, len(nr4)),
        "the_difference": (
            "the corrected junction retains NR4A3 from residue 1; this artifact resumes at residue %s, "
            "dropping NR4A3 Met1 (the initiator methionine, which is an INTERNAL residue in a fusion). "
            "Measured against the committed UniProt cache: NR4A3[1:11] == %r, and this artifact's own "
            "`junction_context_right10` is %r. Every junction-SPANNING peptide therefore differs from the "
            "corrected-junction peptide of the same length." % (kept_from, nr4[1:11], right10)),
        "⚠_what_this_does_NOT_settle": (
            "whether Met1 survives is a splice-PHASE question, not an arithmetic one: EWSR1 exon 7 ends at "
            "coding phase 1, so residue 265 is split across the junction and how it completes depends on the "
            "acceptor exon's 5' phase. That caveat has its one home in fusion-object-inventory.json -> "
            "gate._phase_note and is NOT resolved here. So this artifact is flagged UNVERIFIED, not "
            "retracted — the honest state, and the two must not be conflated."),
        "⚠_superseded_retained": (
            "the sentence above says the phase question is not resolved. It was RESOLVED on 2026-08-06 from "
            "committed data at $0 — the acceptor exon retains 2 5'UTR nt, so the register composes AND a "
            "novel junction codon exists, making the difference TWO residues rather than one. One home: "
            "fusion-object-inventory.json -> gate._phase_note_resolution. This branch is reached only if an "
            "artifact carrying the superseded seam is committed again, which is why its text is kept."),
        "n_spanning_peptides_affected": art.get("n_spanning_peptides"),
        "n_predicted_binders_affected": art.get("n_predicted_binders_by_percentile"),
        "downstream_citations": cits,
        "⛔_scope": "sequence composition only. No affinity, immunogenicity, efficacy or clinical claim.",
        "graded_utc": stamp_utc,
        "graded_et": stamp_et,
        "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
    }, art


#: The one predicate for "this file LOADS the artifact and its numbers inherit the defect". Used by the
#: banner text, the routed map edit AND the console readout — a second copy is how they disagreed once.
def _n_loaded(banner):
    return sum(1 for r in banner["downstream_consumers"] if r["kind"].startswith("CODE — LOADS"))


def map_edits(banner, banner2=None):
    """The roadmap edits this grading requires.

    ⛔ EVERY EDIT POINTS AND RESTATES NOTHING (rule 1). The map already carries finding 23's consequence —
    "26 predicted binders span seams that do not exist" — so repeating the count here would give one fact a
    second home. What the map does NOT carry is (a) that the artifact is now BANNERED IN PLACE, so a reader
    who opens it is stopped rather than trusted to remember, and (b) that the retraction has a measured
    DOWNSTREAM BLAST RADIUS. Both are pointers.
    """
    n_cited = len(banner["downstream_citations"])
    n_loaded = _n_loaded(banner)
    # ⭐ THE CLEARED STATE NEEDS ITS OWN EDIT, and the retraction edit must not be emitted beside it.
    # The first version of this read `banner["counts"]` unconditionally — a key the CLEARED banner
    # does not carry — so the module would have crashed on exactly the run that reports success.
    if not banner.get(STAMP_KEY, True):
        return [
            {"section": "§9 finding 23 → the neoantigen lane's owed consequence",
             "anchor": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
             "current_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
             "proposed_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane). "
                              "✅ **REGENERATED AND CLEARED 2026-08-07 on the corrected TRANSCRIPT "
                              "model, and the junction set changed:** %s The banner is withheld by "
                              "a RE-DERIVATION gate, not by the file having been rewritten "
                              "(`fusion_neoantigen_invalidation._breakpoint_panel_clearance`). "
                              "⚠ **%d modules LOAD this artifact and recompute from it** — their "
                              "committed outputs were built on the RETRACTED junction set and are "
                              "NOT repaired by this clearance; each must be re-run before any of "
                              "its numbers is quoted."
                              % (banner["one_line"], n_loaded),
             "why": "the map records the artifact as retracted and un-regenerated; it now has a "
                    "corrected, smaller junction set, and the downstream outputs are still stale",
             "artifact": "fusion-breakpoint-neoantigens.json"},
        ]
    c = banner["counts"]
    edits = [
        {"section": "§9 finding 23 → the neoantigen lane's owed consequence",
         "anchor": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
         "current_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
         "proposed_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane). "
                          "✅ **BANNERED IN PLACE 2026-08-03, since regeneration is still not this lane's "
                          "to do:** the artifact now leads with a `%s` block that refuses quotation, grades "
                          "every junction against the corrected windows, and — the part nothing carried "
                          "before — names its **downstream blast radius**: **%d committed files quote its "
                          "peptide strings and %d modules LOAD it and recompute from it**, so `hla-coverage`, "
                          "`vaccine-construct` and the two patient demos all inherit the defect without ever "
                          "printing a seam. Per-file list and per-junction grading: "
                          "[`fusion-breakpoint-neoantigens.json`](../modalities/fusion-breakpoint-neoantigens.json) "
                          "→ `%s`, mirrored in "
                          "[`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json)."
                          % (BANNER_KEY, n_cited, n_loaded, BANNER_KEY),
         "why": "the defect was diagnosed and then unowned; a known defect that is not visible AT THE "
                "ARTIFACT reads as a handled one, and the downstream consumers were never enumerated at all",
         "artifact": "fusion-breakpoint-neoantigens.json:%s" % BANNER_KEY},
    ]
    if banner2:
        edits.append(
            # ⚠ APPENDED AT THE END OF THE BULLET, NOT SPLICED INTO ITS OPENING SENTENCE. A first attempt
            # anchored on "`fusion_cofold.py` resumed NR4A3 at residue 2;" and REPLACED it, which dropped a
            # long clause into the middle of a sentence whose second half then read as a non-sequitur. An
            # edit that applies cleanly and reads badly is still a defect in the map.
            {"section": "§9 finding 23 → the OTHER neoantigen artifact",
             "anchor": "because C166 would not have been in the fusion at all.",
             "current_text": "because C166 would not have been in the fusion at all.",
             "proposed_text": "because C166 would not have been in the fusion at all. ⚠ **But "
                              "\"residue 2 is the exon-correct one\" holds for a FOLD model and not for a "
                              "PEPTIDE one, and this page did not draw that distinction:** the corrected "
                              "junction retains NR4A3 from residue **1**, so "
                              "`fusion-neoantigen-predictions.json` — which uses the same residue-2 seam — "
                              "has all %s of its junction-spanning peptides differing from the corrected "
                              "junction's by NR4A3 **Met1**, and its lead epitope is quoted in "
                              "`research/README.md` and three manuscripts. It is flagged **UNVERIFIED, not "
                              "retracted**, because whether Met1 survives is a splice-PHASE question that "
                              "[`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json) "
                              "→ `gate._phase_note` explicitly leaves open."
                              % banner2.get("n_spanning_peptides_affected"),
             "why": "the page treats the residue-2 model as simply vindicated; that holds for the co-fold "
                    "lane and does not hold for the peptide lane, where one residue at the seam changes "
                    "every spanning peptide",
             "artifact": "fusion-neoantigen-predictions.json:%s" % BANNER_KEY})
    return edits


def _already_clear(path, target):
    """True when `path` on disk already parses to exactly `target` — nothing to strip, nothing to write."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh) == target
    except (OSError, ValueError):                                 # pragma: no cover - unreadable => rewrite
        return False


def main(argv=None):
    import argparse
    import datetime
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="stamp the banners into the artifacts")
    ap.add_argument("--edits-out", default=os.path.join(HERE, "fusion-neoantigen-retraction.json"))
    a = ap.parse_args(argv)

    utc = datetime.datetime.now(datetime.timezone.utc)
    stamp_utc = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    et = utc - datetime.timedelta(hours=4)                        # EDT; CLAUDE.md §1 reports in ET
    stamp_et = et.strftime("%Y-%m-%d %-I:%M %p ET")

    banner, art = breakpoint_banner(stamp_utc, stamp_et)
    banner2, art2 = single_breakpoint_banner(stamp_utc, stamp_et)
    print(banner["one_line"])
    print("  downstream files quoting it: %d" % len(banner["downstream_citations"]))
    for row in banner["downstream_citations"]:
        print("    %-58s %3d peptides" % (row["path"], row["n_peptides_quoted"]))
    # ⛔ THE SAME PREDICATE THE BANNER AND THE MAP EDIT USE. This read `startswith("CODE")`, which swept in
    # the artifact's own PRODUCER and printed 7 where the committed data said 6 — a console line disagreeing
    # with the artifact beside it, which is the exact defect class this module exists to close.
    print("  files that LOAD it and recompute: %d" % _n_loaded(banner))
    for row in banner["downstream_consumers"]:
        print("    %-58s %s" % (row["path"], row["kind"]))
    print(banner2["status"])
    for row in banner2["downstream_citations"]:
        print("    %-58s %3d peptides" % (row["path"], row["n_peptides_quoted"]))

    doc = {"_title": "EWSR1::NR4A3 neoantigen artifacts graded against the corrected junction",
           "_cost": "$0 — committed inputs only, no network, no model, no prediction",
           "_utc": stamp_utc, "_et": stamp_et,
           "breakpoint_artifact": banner, "single_breakpoint_artifact": banner2,
           "map_edits_required": map_edits(banner, banner2)}
    with open(a.edits_out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("wrote", os.path.relpath(a.edits_out, REPO))

    if a.write:
        for path, b, target in ((BREAKPOINT_ARTIFACT, banner, art),
                                (SINGLE_BREAKPOINT_ARTIFACT, banner2, art2)):
            # ⛔ A GRADE OF "CLEARED" MUST BE ABLE TO WITHHOLD THE BANNER, or `--write` is a ratchet that
            # re-retracts a corrected artifact on its next run. Default-True so an older banner shape with
            # no such key keeps stamping — a missing flag is not permission to skip.
            if not b.get(STAMP_KEY, True):
                # ⚠ A CLEARANCE THAT REWRITES AN ALREADY-CLEAR FILE IS CHURN, NOT WORK. This module writes
                # `indent=1` and the producers write `indent=2`, so re-running it over an artifact that has
                # no banner reformatted every line of a file whose CONTENT was byte-for-byte unchanged (448
                # lines on `fusion-neoantigen-predictions.json`, 2026-08-07). A diff that large hides a real
                # one. Compare the parsed content and leave the file alone when there is nothing to remove.
                if _already_clear(path, target):
                    print("already clear (unchanged)", os.path.relpath(path, REPO))
                    continue
                # `art.pop(BANNER_KEY)` already stripped any stale banner; write the artifact back clean so
                # a file bannered by an earlier run is un-bannered by the run that clears it.
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(json.dumps(target, indent=1, ensure_ascii=False) + "\n")
                print("cleared (no banner)", os.path.relpath(path, REPO))
                continue
            out = {BANNER_KEY: b}
            out.update(target)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
            print("bannered", os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
