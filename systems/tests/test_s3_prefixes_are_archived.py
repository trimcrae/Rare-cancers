"""Every S3 prefix on the expiring bucket must be covered by the archiver.

⛔⛔ THIS GUARD EXISTS BECAUSE THE FAILURE IT PREVENTS HAS NOW HAPPENED TWICE.

`archive-results-aws.yml`'s own header records the first time, in its own words: *"old outputs were
lost to S3 lifecycle expiration"*. That workflow was built to stop it recurring — it mirrors durable
result artifacts out of the ephemeral SageMaker default bucket and into git.

It did not stop it recurring. On 2026-08-26 the step-1 fan-out results prefix was read at **10
objects**, against **8,510** on 2026-08-06 — both readings printed verbatim at the top of
`research/modalities/step1-terminus-evidence.txt`, which regenerates from a live S3 list every run.
Roughly 8,500 raw result objects expired, and **nothing had been mirrored**, because
`nr4a3-step1-fanout` was never added to `DEFAULT_PREFIXES`.

⭐ AND IT WAS NOT ALONE — WHICH IS THE REASON THIS IS A TEST AND NOT A ONE-LINE FIX. When the check
below was first written, the archiver's nineteen-entry default list covered **none** of the six
prefixes the repository actually writes to today. Every lane added since the list was authored had
drifted out of coverage silently. `paper-hardening` names this defect class exactly: a fix scoped to
a LIST regresses at a sibling; a fix scoped to a PREDICATE does not. The predicate is below.

⚠ WHAT THIS CANNOT DO: it cannot tell you an object still exists. It checks that a lane writing to
the expiring bucket is *claimed* by the archiver — which is evidence of intent, not of a mirror. The
archiver actually running is what makes the mirror, and that is why it now carries a `schedule:`.
"""

from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
ARCHIVER = REPO / ".github" / "workflows" / "archive-results-aws.yml"

# The bucket that expires things. Prefixes elsewhere (Vast, GCS) are out of scope for this guard.
EXPIRING_BUCKET = "sagemaker-us-east-2-646605541856"

SEARCH_ROOTS = (REPO / ".github" / "workflows", REPO / "research" / "modalities")
S3_URI = re.compile(r"s3://([a-z0-9.\-]+)/([A-Za-z0-9_\-]+)")

# Prefixes that are scratch or caches by design and are NOT a durable result. Each needs a REASON,
# because "it does not matter" is how the fan-out prefix stayed uncovered.
EXEMPT = {
    "nrv04-ffcache": "a force-field parameter CACHE — regenerable from the ligand definitions at "
                     "no cost, so expiry loses time rather than evidence.",
}


def _declared_prefixes() -> set[str]:
    text = ARCHIVER.read_text()
    match = re.search(r'DEFAULT_PREFIXES:\s*"([^"]+)"', text)
    assert match, "archive-results-aws.yml no longer declares DEFAULT_PREFIXES — this guard is blind"
    return {p.strip() for p in match.group(1).split(",") if p.strip()}


def _referenced_prefixes() -> dict[str, set[str]]:
    """prefix -> the files that write to it on the expiring bucket."""
    found: dict[str, set[str]] = {}
    for root in SEARCH_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".yml", ".yaml", ".py"}:
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            for bucket, prefix in S3_URI.findall(text):
                if bucket == EXPIRING_BUCKET:
                    found.setdefault(prefix, set()).add(str(path.relative_to(REPO)))
    return found


def test_the_archiver_still_declares_a_prefix_list():
    assert _declared_prefixes(), "DEFAULT_PREFIXES is empty — the archiver would mirror nothing"


def test_the_archiver_runs_without_a_human():
    """⛔ A PREVENTIVE CONTROL NOBODY RUNS IS NOT A CONTROL. This workflow sat dispatch-only while the
    very loss it was built to prevent happened a second time."""
    assert "schedule:" in ARCHIVER.read_text(), (
        "archive-results-aws.yml has no schedule. It exists to stop S3 lifecycle expiry destroying "
        "results, and dispatch-only means it protects nothing unless somebody remembers."
    )


def test_every_lane_writing_to_the_expiring_bucket_is_claimed_by_the_archiver():
    """★ THE PREDICATE. Scoped to 'any prefix on the expiring bucket', not to a list of known lanes,
    because a list is what drifted."""
    declared, referenced = _declared_prefixes(), _referenced_prefixes()
    assert referenced, "found no S3 references at all — the scanner is broken, not the repo clean"

    uncovered = {p: files for p, files in referenced.items()
                 if p not in declared and p not in EXEMPT}
    assert not uncovered, (
        "these lanes write to the expiring bucket and the archiver does not claim them, so their "
        "results can expire with no git mirror — exactly what cost ~8,500 objects on 2026-08-26:\n"
        + "\n".join(f"  {p}  written by {sorted(f)}" for p, f in sorted(uncovered.items()))
        + "\nAdd each to DEFAULT_PREFIXES in .github/workflows/archive-results-aws.yml, or add it to "
          "EXEMPT in this file WITH A REASON."
    )


def test_every_exemption_carries_a_reason():
    """An exemption without a reason is a silent hole with extra steps."""
    for prefix, reason in EXEMPT.items():
        assert len(reason.strip()) > 30, f"{prefix} is exempt with no real reason given"


def test_the_guard_is_load_bearing_and_not_decorative(monkeypatch):
    """Mutation test: drop a real lane from the declared list and the check must actually fail.

    Without this, every assertion above could pass against a scanner that finds nothing.
    """
    referenced = _referenced_prefixes()
    victim = sorted(p for p in referenced if p not in EXEMPT)[0]
    module = __import__(__name__)
    # ⚠ Bind the ORIGINAL first. Patching to a lambda that calls the patched name recurses forever —
    # which is what the first version of this test did, and pytest caught it rather than a reviewer.
    original = module._declared_prefixes
    monkeypatch.setattr(module, "_declared_prefixes", lambda: original() - {victim})
    with pytest.raises(AssertionError):
        test_every_lane_writing_to_the_expiring_bucket_is_claimed_by_the_archiver()
