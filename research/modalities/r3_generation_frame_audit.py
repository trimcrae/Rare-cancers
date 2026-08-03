#!/usr/bin/env python3
"""R3 — the FRAME-LEVEL generation-receptor dependency audit (Gate A / the paper's open submission gate).

THE QUESTION, in the paper's own words (nr4a3-degrader-paper.md, the "Dependency audit — still open"
paragraph): the harmonized pocket rerun *"must additionally confirm that the exact release-derived frame used
to generate `denovo_401` still qualifies as the same mapped orthosteric site and still exceeds D*"*, and *"if
the generation frame does not qualify, the generation receptor — not merely a reported frame-fraction — is
affected."*

WHY THIS MODULE EXISTS RATHER THAN A READ OF THE HARMONIZED SUMMARY. The paper says the committed artifact
`nr4a3-pocket-reharmonize-summary.json` *"reports ensemble-level fractions only and does not identify which
individual frames cleared D*"*. That is true but it is the WEAKER of the two statements available, and the
stronger one is checkable from committed code: the generation frame was **never an entry in the rerun at
all**. `sagemaker_src/entry_pocket_reharmonize.py` re-scores exactly five things — the AFDB AF-Q92570 model,
the NR-panel calibration structures, the 20 8XTT NMR conformers, the metadynamics frames, and release_rep0..2
— and builds no entry for the release-druggable receptor sub-ensemble, even though `nr4a3_pocket_reharmonize.
detection_from_result` carries a `release_druggable` kind for precisely that input and the redesign brief's
own rerun list ends with *"exact generation receptor frame"*. So the gap is not a reporting granularity
problem that a per-frame dump would close; it is a missing ensemble.

WHAT THE GENERATION RECEPTOR IS. The generator's own receptor loader decides this, not a prose summary:
`nr4a3_denovo.py` loads `nr4a3-release-druggable.pdb` from the Step-0 receptor directory (its module docstring:
*"the thermally-real, breathing, induced-fit pocket — NOT the biased-metad frame"*), and the red-team's F16
quotes the same lines. That PDB is the `role="primary"` entry of `nr4a3_release_druggable.py`'s manifest,
`nr4a3-release-druggable.json`, whose `receptors[]` rows carry `rep`, `frame`, `selection_rg`,
`selection_druggability` and `confirmed_druggability` — i.e. the exact frame identity the audit needs. That
manifest is a SageMaker output under the `nr4a3-release-druggable` S3 prefix and is **not committed to this
repo**, which is why this audit is an S3 read rather than a file read.

⚠ AND THE MANIFEST'S OWN SCORE MAY NOT BE THE HARMONIZED ONE. `pocket_tracking.match_mode` defaults to
LEGACY, and `.github/workflows/release-druggable-aws.yml` sets no `POCKET_MATCH`. So a manifest written by
that workflow records `pocket_match.mode = "legacy"` — the outcome-selected classifier the harmonized rerun
exists to replace. Reading a legacy `confirmed_druggability` and calling the gate discharged would be the
"a populated field is not a measured one" failure (CLAUDE.md §4). This module therefore reports the mode
alongside the number and refuses the verdict when the mode is not harmonized.

VERDICTS THIS CAN RETURN — all four are real results, and three of them are refusals:
  DISCHARGED_PASS      the manifest names the frame AND records a harmonized match >= D*.
  DISCHARGED_FAIL      the manifest names the frame AND records a harmonized match <  D*  (or no match).
                       ⚠ This one reaches the generation receptor itself — see the paper sentence above.
  FRAME_NAMED_UNSCORED the frame identity is recovered but its recorded score is LEGACY-mode, so the
                       frame-level D* question is open on the harmonized criteria. Unblocker: re-score that
                       one PDB with POCKET_MATCH=harmonized and the pinned fpocket build.
  FRAME_NOT_RECOVERABLE no manifest under the prefix. The frame identity is not in any committed artifact
                       and not in the object store; state that, and name what would recover it.

Pure functions (`classify`, `pick_primary`, `reharmonize_covers_generation_frame`) are unit-testable with no
boto3/S3/fpocket stack; `main()` is the thin I/O wrapper the CI job runs.
"""
import json
import os
import sys

D_STAR = 0.53
HARMONIZED = "harmonized"

DEFAULT_BUCKET = os.environ.get("R3_BUCKET") or "sagemaker-us-east-2-646605541856"
DEFAULT_PREFIX = os.environ.get("R3_PREFIX") or "nr4a3-release-druggable"
MANIFEST_NAME = "nr4a3-release-druggable.json"

#: The ensembles the committed harmonized rerun actually scored. Read off
#: `sagemaker_src/entry_pocket_reharmonize.py`'s `aggregate()` entry list — the one home is that file, and
#: this tuple exists only so the audit can SAY which set it checked against.
REHARMONIZED_ENSEMBLES = ("af2_static", "calibration_nr4a3", "8xtt_20conformers", "metad_frames",
                          "release_rep0", "release_rep1", "release_rep2", "release_unbiased_pooled")

#: The ensemble kind that WOULD carry the generation receptor. `nr4a3_pocket_reharmonize.
#: detection_from_result` implements it; no entry in the rerun ever used it.
GENERATION_KIND = "release_druggable"


def reharmonize_covers_generation_frame(summary):
    """Does the committed harmonized summary contain a row that scores the generation receptor? PURE.

    Returns {"covered": bool, "rows": [...], "missing_kind": str, "why": str}.

    ⚠ The answer is NOT "the rows are ensemble-level, so we cannot tell". `release_rep0..2` are the raw
    release TRAJECTORY frames as propagated by `nr4a3_mdpocket.py`; the generation receptor is a frame
    RE-EXTRACTED and re-boxed by `nr4a3_release_druggable.py` into its own PDB, scored by its own fpocket
    call, and it is that PDB the generator was conditioned on. Even a per-frame dump of `release_rep*` would
    not be the same measurement — `nr4a3_release_druggable.py`'s own `confirm_filter` note says the reused
    per-frame summary and the fresh confirmation run "can disagree" and that "the *confirmed* score ...
    governs". So the covering row would have to be a `release_druggable` row, and there is none.
    """
    rows = [r.get("ensemble") for r in (summary or {}).get("rows", [])]
    return {
        "covered": GENERATION_KIND in rows,
        "rows": rows,
        "missing_kind": GENERATION_KIND,
        "why": ("the generation receptor is a RE-EXTRACTED, re-boxed PDB scored by its own fpocket call "
                "(nr4a3_release_druggable.py -> confirm_filter: the reused per-frame summary and the fresh "
                "confirmation 'can disagree' and the confirmed score governs), so a release_rep* trajectory "
                "row is not a measurement of it even at per-frame granularity"),
    }


def pick_primary(manifest):
    """The generation receptor's row out of a release-druggable manifest. PURE. None if absent.

    Prefers the row whose `pdb` is the manifest's own `selection_primary_receptor`, because that is the file
    name `nr4a3_denovo.py` loads. Falls back to `role == "primary"`.

    ⚠ `docking_primary_receptor` is deliberately NOT used as the selector. It can be an ALTERNATE — the
    manifest promotes one when the selection primary fails confirmation — and the molecule was generated
    against `nr4a3-release-druggable.pdb`, so an audit that followed the docking pointer could score a frame
    the generator never saw. Both are reported.
    """
    if not manifest:
        return None
    want = manifest.get("selection_primary_receptor")
    recs = manifest.get("receptors") or []
    for r in recs:
        if want and r.get("pdb") == want:
            return r
    for r in recs:
        if r.get("role") == "primary":
            return r
    return None


def classify(manifest, primary, d_star=D_STAR):
    """The audit verdict. PURE. Returns {"verdict", "reason", "frame_id", "score", "mode", ...}.

    Never guesses: a missing manifest, a missing primary row, a legacy-mode score and a harmonized score are
    four distinguishable states and each gets its own verdict string.
    """
    if manifest is None:
        return {"verdict": "FRAME_NOT_RECOVERABLE", "frame_id": None, "score": None, "mode": None,
                "reason": (f"no {MANIFEST_NAME} was readable under the release-druggable prefix, and no "
                           "committed artifact in this repo records the generation frame's (rep, frame) "
                           "index"),
                "unblocker": ("re-run `nr4a3_release_druggable.py` (release-druggable-aws.yml) with "
                              "POCKET_MATCH=harmonized and the pinned fpocket build; it re-derives the "
                              "selection deterministically from `release_frame_select.select_receptor_"
                              "ensemble`, so the primary is reproducible rather than lost — provided the "
                              "release DCDs are still in S3")}
    if primary is None:
        return {"verdict": "FRAME_NOT_RECOVERABLE", "frame_id": None, "score": None, "mode": None,
                "reason": ("the manifest exists but carries no primary receptor row "
                           "(receptors[] empty or no selection_primary_receptor match)"),
                "unblocker": "same re-run as above; inspect the manifest's `_status` for why it aborted"}

    mode = ((manifest.get("pocket_match") or {}).get("mode") or "").strip().lower()
    frame_id = {"rep": primary.get("rep"), "frame": primary.get("frame"),
                "pdb": primary.get("pdb"), "role": primary.get("role"),
                "selection_rg": primary.get("selection_rg")}
    score = primary.get("confirmed_druggability")
    sel_score = primary.get("selection_druggability")

    if mode != HARMONIZED:
        return {"verdict": "FRAME_NAMED_UNSCORED", "frame_id": frame_id, "score": score,
                "selection_druggability": sel_score, "mode": mode or "(absent)",
                "reason": (f"the generation frame is NAMED, but its recorded pocket match ran in "
                           f"'{mode or 'absent'}' mode, not '{HARMONIZED}'. `pocket_tracking.match_mode` "
                           "defaults to LEGACY and release-druggable-aws.yml sets no POCKET_MATCH, so this "
                           "score is the outcome-selected classifier the harmonized rerun exists to "
                           "replace. A legacy score cannot discharge a harmonized gate"),
                "unblocker": ("score THIS ONE PDB under POCKET_MATCH=harmonized with the pinned fpocket "
                              "build — one structure, CPU, no trajectory reload")}

    if score is None:
        return {"verdict": "DISCHARGED_FAIL", "frame_id": frame_id, "score": None, "mode": mode,
                "reason": ("harmonized mode, but the matcher returned NO matched orthosteric cavity for the "
                           "generation frame — under the composite Jaccard/recovery/centroid gate it is not "
                           "the same mapped site"),
                "reaches": "the generation receptor itself (paper: 'not merely a reported frame-fraction')"}

    if float(score) >= d_star:
        return {"verdict": "DISCHARGED_PASS", "frame_id": frame_id, "score": float(score), "mode": mode,
                "d_star": d_star,
                "reason": (f"harmonized match, confirmed druggability {score} >= D* {d_star}; the exact "
                           "generation frame survives the score-independent site definition")}
    return {"verdict": "DISCHARGED_FAIL", "frame_id": frame_id, "score": float(score), "mode": mode,
            "d_star": d_star,
            "reason": (f"harmonized match, confirmed druggability {score} < D* {d_star}"),
            "reaches": "the generation receptor itself (paper: 'not merely a reported frame-fraction')"}


# ---- thin I/O wrapper (not unit-tested) ------------------------------------------------------------

def _s3():
    import boto3
    return boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"))


def _fetch_manifest(bucket, prefix):
    """(manifest_or_None, listing) — LIST FIRST, so 'the collector could not read it' is distinguishable
    from 'it is not there' (CLAUDE.md §4: an absent reading is not a reading of absence)."""
    s3 = _s3()
    root = prefix.rstrip("/") + "/"
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": root}
        if token:
            kw["ContinuationToken"] = token
        try:
            page = s3.list_objects_v2(**kw)
        except Exception as e:  # noqa: BLE001
            return None, {"error": f"{type(e).__name__}: {e}", "keys": []}
        keys.extend({"key": o["Key"], "size": o["Size"],
                     "last_modified": o["LastModified"].isoformat()} for o in page.get("Contents", []) or [])
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    listing = {"error": None, "n_keys": len(keys), "keys": keys[:200]}
    hit = next((k for k in keys if k["key"].endswith("/" + MANIFEST_NAME)
                or k["key"].endswith(MANIFEST_NAME)), None)
    if not hit:
        return None, listing
    try:
        body = s3.get_object(Bucket=bucket, Key=hit["key"])["Body"].read()
        return json.loads(body), {**listing, "manifest_key": hit["key"],
                                  "manifest_last_modified": hit["last_modified"]}
    except Exception as e:  # noqa: BLE001
        return None, {**listing, "manifest_key": hit["key"], "read_error": f"{type(e).__name__}: {e}"}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "r3-generation-frame-audit.json")
    bucket = DEFAULT_BUCKET
    prefix = DEFAULT_PREFIX
    for i, a in enumerate(argv):
        if a == "--out" and i + 1 < len(argv):
            out_path = argv[i + 1]
        if a == "--bucket" and i + 1 < len(argv):
            bucket = argv[i + 1]
        if a == "--prefix" and i + 1 < len(argv):
            prefix = argv[i + 1]

    summary_path = os.path.join(here, "nr4a3-pocket-reharmonize-summary.json")
    summary = None
    if os.path.exists(summary_path):
        with open(summary_path) as fh:
            summary = json.load(fh)
    coverage = reharmonize_covers_generation_frame(summary)

    manifest, listing = _fetch_manifest(bucket, prefix)
    primary = pick_primary(manifest)
    verdict = classify(manifest, primary)

    out = {
        "_what": ("R3 — the frame-level generation-receptor dependency audit (Gate A). Does the EXACT "
                  "release-derived frame `denovo_401` was generated into still qualify under the "
                  "harmonized, score-independent orthosteric-site definition?"),
        "_gate": ("open SUBMISSION gate, nr4a3-degrader-paper.md 'Dependency audit — still open'; "
                  "nr4a3-ensemble-redesign-brief.md Gate A"),
        "d_star": D_STAR,
        "generation_receptor_identity_chain": [
            {"file": "research/modalities/nr4a3_denovo.py",
             "says": "loads nr4a3-release-druggable.pdb from the Step-0 receptor dir; docstring: the "
                     "DRUGGABLE UNBIASED RELEASE conformation, NOT the biased-metad frame"},
            {"file": "research/manuscripts/nr4a3-degrader-paper-redteam.md (F16.1)",
             "says": "denovo_401 is pocket-conditioned on the NR4A3 release-druggable frame, quoting the "
                     "same nr4a3_denovo.py lines"},
            {"file": "research/manuscripts/nr4a3-degrader-paper.md",
             "says": "all downstream design is anchored to a druggable release-derived frame "
                     "(Rg ~ 0.737, fpocket >= 0.5; nr4a3_release_druggable.py)"},
            {"file": "research/modalities/nr4a3_release_druggable.py",
             "says": "writes nr4a3-release-druggable.pdb = the role='primary' row of "
                     "nr4a3-release-druggable.json, which carries rep/frame/selection_rg/"
                     "selection_druggability/confirmed_druggability"},
        ],
        "reharmonize_coverage": coverage,
        "s3_listing": listing,
        "bucket": bucket,
        "prefix": prefix,
        "primary_row": primary,
        "docking_primary_receptor": (manifest or {}).get("docking_primary_receptor"),
        "manifest_pocket_match": (manifest or {}).get("pocket_match"),
        "manifest_status": (manifest or {}).get("_status"),
        # ⚠ ADDED 2026-08-03, AND IT IS THE DISCRIMINATING OBSERVATION FOR AN OPEN ERRATUM. The manifest
        # records `selection_rg: 0.7367` for a frame whose CV Rg, recomputed from its own coordinates,
        # is 0.7612 (`r3-site-choice-audit.json` -> cv_rg_check). Rg is not a label — it is the SELECTION
        # CRITERION (`release_frame_select` minimises |Rg - target_rg|) — so the mismatch is either a
        # mislabelled frame or a mis-selected one, and the two call for different responses.
        # `candidate_source` names the trajectory the pool was read from and `params` names the
        # target_rg/D* actually used, which is exactly what tells those apart. ⛔ They were being thrown
        # away by a collector that had already downloaded them: `nr4a3_release_druggable._load_summary_
        # records` labels EVERY record `rep: 0` regardless of which trajectory's summary is mounted, so
        # "which trajectory" is a real question about this manifest and not a pedantic one.
        "manifest_candidate_source": (manifest or {}).get("candidate_source"),
        "manifest_candidate_pool": (manifest or {}).get("candidate_pool"),
        "manifest_params": (manifest or {}).get("params"),
        "manifest_selection": (manifest or {}).get("selection"),
        "manifest_confirm_filter": (manifest or {}).get("confirm_filter"),
        "verdict": verdict,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({"verdict": verdict, "reharmonize_covered": coverage["covered"],
                      "n_keys": listing.get("n_keys"), "listing_error": listing.get("error")}, indent=2))
    print(f"[r3-audit] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
