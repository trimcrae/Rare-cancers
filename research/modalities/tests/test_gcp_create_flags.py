"""The GCP create command and the messages describing it, checked against the YAML itself.

Two facts about a GCP GPU VM have each cost this repo real GPU-days, and both live in
`.github/workflows/gpu-ternary-fep-gcp.yml`:

1. **`--max-run-duration` REQUIRES `--instance-termination-action`** — for standard as well as spot
   (gcp-gpu-facts.md §3). The standard branch once omitted it, so every on-demand create failed
   request-validation and the failure was mislabelled "stocked out" for months.

2. **The cap the operator is TOLD about must be the cap the instance CARRIES.** Every detach/teardown
   message hardcoded "7h max-run backstop", which is the spot value; the on-demand branch has been
   259200s (72 h) since 2026-07-26. On 2026-07-26 the launcher therefore told the operator that
   gcp-ternary-30215419909 would self-destruct within 7 h while its real cap was 72 h. When that VM's
   in-VM self-delete was refused (`Required 'compute.instances.delete' permission`, measured
   2026-07-27), the exposure everyone believed was bounded at 7 h ran to ~2 h of the project's ONLY
   GPU held idle before a human looked — and would have run to 72 h unattended.

WHY THIS TEST PARSES THE YAML. A test that restated "both branches must pass
--instance-termination-action" would only prove the copy agrees with itself. This one EXTRACTS the
actual `gcloud compute instances create` invocation and the actual `MAXRUN=` assignments out of the
workflow and checks the real text, so it fails when the workflow changes and the rule does not.
"""

from __future__ import annotations

import pathlib
import re

import pytest

WF = pathlib.Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-gcp.yml"


def _text() -> str:
    assert WF.is_file(), f"missing {WF}"
    return WF.read_text()


def _create_invocation(text: str) -> str:
    """The `gcloud compute instances create ...` command, line-continuations joined.

    Extraction, not transcription: if the launcher is rewritten, this either finds the new command or
    fails loudly. It must never silently match nothing.
    """
    i = text.index("gcloud compute instances create")
    out: list[str] = []
    for line in text[i:].splitlines():
        out.append(line)
        if not line.rstrip().endswith("\\"):
            break
    joined = " ".join(ln.rstrip().rstrip("\\").strip() for ln in out)
    assert len(out) > 1, "create invocation collapsed to one line — extraction is probably wrong"
    return joined


def _prov_branches(text: str) -> dict[str, str]:
    """Each provisioning branch's flag string, keyed by its MAXRUN value."""
    branches = {}
    for m in re.finditer(r'PROV_FLAGS="([^"]+)".*?MAXRUN=(\S+)', text):
        branches[m.group(2)] = m.group(1)
    assert branches, "found no PROV_FLAGS/MAXRUN branches — extraction is wrong, not the workflow"
    return branches


def test_create_passes_max_run_duration_and_termination_action_together():
    """gcp-gpu-facts.md §3: GCP rejects --max-run-duration without --instance-termination-action."""
    cmd = _create_invocation(_text())
    assert "--max-run-duration=" in cmd, cmd
    # the termination action may sit in the command or in the per-branch $PROV_FLAGS it interpolates
    branches = _prov_branches(_text())
    for maxrun, flags in branches.items():
        combined = cmd + " " + flags
        assert "--instance-termination-action=" in combined, (
            f"branch MAXRUN={maxrun} sets --max-run-duration but no --instance-termination-action; "
            "GCP fails request-validation and the launcher reports it as 'stocked out'"
        )


def test_both_provisioning_branches_are_covered():
    """Spot and standard must BOTH carry the termination action — 'spot-only' was the original bug."""
    branches = _prov_branches(_text())
    assert len(branches) >= 2, f"expected a spot and a standard branch, got {branches}"
    models = {f for flags in branches.values() for f in flags.split() if "provisioning-model" in f}
    assert models == {"--provisioning-model=SPOT", "--provisioning-model=STANDARD"}, models


def test_operator_messages_do_not_hardcode_a_max_run_cap():
    """No EMITTED line may state a cap in hours; it must interpolate $MAXRUN.

    This is the exact defect that made a 72 h VM read as a 7 h one. Scoped to text the workflow
    actually prints (`echo`, `::notice`, `::error`) rather than to comments: the sizing rationale and
    the retraction of the old "7h backstop" wording are HISTORY, which rule 1.2 says must stay
    quotable, while an operator-facing message is a live claim about a running VM.
    """
    text = _text()
    offenders = []
    for n, ln in enumerate(text.splitlines(), 1):
        stripped = ln.strip()
        if stripped.startswith("#") or "MAXRUN" in ln:
            continue
        if not re.search(r"\becho\b|::notice|::error|::warning", ln):
            continue
        if re.search(r"\b\d+\s*h\b[^\n]{0,24}(max-run|backstop)", ln, re.I) or re.search(
            r"(max-run|backstop)[^\n]{0,24}\b\d+\s*h\b", ln, re.I
        ):
            offenders.append((n, stripped))
    assert not offenders, (
        "these EMITTED lines state a max-run cap as a literal instead of reading $MAXRUN:\n"
        + "\n".join(f"  line {n}: {ln}" for n, ln in offenders)
    )


def test_maxrun_is_exported_so_later_steps_read_it():
    """The teardown/summary steps are separate steps; without this they can only remember."""
    assert re.search(r'echo "MAXRUN=\$MAXRUN" >> "\$GITHUB_ENV"', _text()), (
        "MAXRUN is not published to GITHUB_ENV, so a later step cannot print the real cap"
    )


def test_standard_branch_cap_spans_a_full_leg():
    """A full leg is 800 warmup + 2000 production iterations at ~56.5 s/iter ≈ 44 h of MD.

    An on-demand cap shorter than that buys a VM boundary at create time, and GCP refuses to raise
    max-run-duration on a running instance (gcp-gpu-facts.md §3b) — so it cannot be fixed later.
    """
    branches = _prov_branches(_text())
    standard = [mr for mr, fl in branches.items() if "STANDARD" in fl]
    assert len(standard) == 1, standard
    seconds = int(standard[0].rstrip("s"))
    assert seconds >= 44 * 3600, f"on-demand cap {seconds}s is shorter than a ~44 h leg"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
