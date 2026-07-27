#!/usr/bin/env python3
"""The VM startup script that `gpu-ternary-fep-gcp.yml` GENERATES must be valid bash, and must carry the
restraint flag through to the engine.

WHY THIS EXISTS. That workflow builds a ~235-line bash script inside an UNQUOTED heredoc and hands it to GCE as
metadata. Nothing on the runner ever parses it: a syntax error in the generated script is discovered by BOOTING
A GPU, waiting out provisioning, and reading a serial console — a ~20-40 minute round trip on the single GPU the
whole project shares (GPUS_ALL_REGIONS=1), for a defect a parser finds in milliseconds. `actionlint` and
`test_workflows_parse.py` both check the YAML; neither looks INSIDE the block scalar, because to them it is a
string.

THE METHOD, and it is the point. This does not restate the script. It EXTRACTS the real heredoc body from the
real workflow, EMULATES the unquoted-heredoc expansion the runner performs (unescaped `$VAR` is substituted by
the runner as the file is written; `\\$VAR` survives into the file for the VM's shell), writes the result, and
runs `bash -n` on it. A test that retyped the script would prove only that the copy parses.

THE EXPANSION RULE IS THE SAME ONE THAT CAUSED THE 2026-07-25 SILENT WRONG ANSWER (audit §H): `DIRSUF` was
assigned in the VM's shell and read in the runner's, so it expanded to empty and a rev leg resumed the forward
trajectory. `test_heredoc_two_shell.py` guards that specific two-shell mistake; this file guards the other half
— that whatever the two shells produce is a script bash will actually accept, and that the values the runner is
supposed to bake in are really baked in.
"""

import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, "..", "..", "..", ".github", "workflows", "gpu-ternary-fep-gcp.yml")

# What the RUNNER has in scope when it writes the heredoc. Values are placeholders; only the substitution
# behaviour is under test. RESTRAIN=1 and a matching _rst prefix, because that is the configuration whose
# plumbing is new and unproven.
RUNNER_ENV = {
    "BUCKET": "bkt", "PROJECT": "proj", "MODE": "run", "LEG_ID": "calib_hi_to_lo__binary_vhl",
    "SEED": "0", "DIRECTION": "fwd", "NWIN": "12", "CHARGE_METHOD": "nagl", "TIMESTEP_FS": "2.0",
    "CONSTRAIN_LIG": "0", "WARMUP_TS": "1.0", "WARMUP_ITERS": "", "PROD_ITERS": "", "REQUIRE_PRIMED": "1",
    "MIN_STEPS": "5000", "AUTOSTOP": "0", "AUTOSTOP_MIN_FRAC": "0.4", "RESTRAIN": "1", "GITREF": "somebranch",
    "IMG_FAMILY": "common-cu123", "RESULTS": "gs://bkt/valB-6hax/results", "TEMPLATE_PDB": "8G1Q",
    "PE_NS": "0.5", "PE_SMOKE": "0", "USE_PE": "0", "FORCE_RERUN": "0", "SPOT_SAFE": "0",
    "COMMIT_PREFIX": "gs://bkt/valB-6hax/commits/calib_hi_to_lo__binary_vhl/0_dt2.0fs_clig0_wu1.0_rst",
}

_ESCAPED = "\x00KEEP_DOLLAR\x00"


def heredoc_body(text):
    """The raw lines between `cat > /tmp/startup.sh <<SS` and its terminator, de-indented by the YAML block
    scalar's indentation. Fails loudly rather than returning something plausible-but-wrong."""
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if "cat > /tmp/startup.sh <<SS" in l), None)
    assert start is not None, "the startup heredoc is gone from the workflow — this test is now blind"
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = next((j for j in range(start + 1, len(lines))
                if lines[j].strip() == "SS" and (len(lines[j]) - len(lines[j].lstrip())) == indent), None)
    assert end is not None, "no `SS` terminator at the heredoc's own indentation"
    body = [l[indent:] if len(l) >= indent else l for l in lines[start + 1:end]]
    assert len(body) > 100, "heredoc body is suspiciously short (%d lines) — extraction is probably wrong" % len(body)
    return "\n".join(body)


def render(body, env):
    """Emulate the runner writing an UNQUOTED heredoc: `\\$VAR` survives to the VM, bare `$VAR` is expanded now.
    An unset runner variable expands to empty, exactly as the shell would — which is precisely how the direction
    suffix silently vanished in §H, so it is emulated rather than corrected."""
    s = body.replace("\\$", _ESCAPED)
    s = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)",
               lambda m: env.get(m.group(1) or m.group(2), ""), s)
    return s.replace(_ESCAPED, "$")


def test_generated_startup_script_is_valid_bash():
    rendered = render(heredoc_body(open(WF).read()), RUNNER_ENV)
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as fh:
        fh.write(rendered)
        path = fh.name
    try:
        r = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        assert r.returncode == 0, (
            "the GENERATED VM startup script is not valid bash — a GPU would have to boot to find this:\n"
            + r.stderr[:2000])
    finally:
        os.unlink(path)


def test_the_restraint_flag_is_baked_in_by_the_runner_not_left_to_the_vm():
    """RBFE_RESTRAIN must arrive at the engine as a LITERAL VALUE. If it were left as `\\$RESTRAIN` it would be
    read in the VM's shell, where nothing ever assigns it — it would expand to empty, the leg would run
    UNRESTRAINED at an `_rst` commit prefix, and every downstream artifact would label it restrained. That is
    the §H failure with the labels swapped, and no particle-count check can see it."""
    rendered = render(heredoc_body(open(WF).read()), RUNNER_ENV)
    assert "RBFE_RESTRAIN=1" in rendered, (
        "RBFE_RESTRAIN did not render to its literal runner-side value; got the surrounding text: "
        + next((l for l in rendered.split("\n") if "RBFE_RESTRAIN" in l), "(no RBFE_RESTRAIN line at all)"))
    assert "RBFE_RESTRAIN=$RESTRAIN" not in rendered, (
        "RBFE_RESTRAIN was deferred to the VM's shell, where RESTRAIN is never assigned — it would expand to "
        "empty and the leg would run unrestrained at a restrained prefix")


def test_the_restraint_report_upload_is_direction_and_seed_keyed():
    """The report names the leg, direction and seed. An unkeyed name would let one leg's restraint geometry
    overwrite another's, which is §L.5/§L.6 for the fifth time — anything keyed on a dimension must be keyed
    everywhere the artifact travels."""
    rendered = render(heredoc_body(open(WF).read()), RUNNER_ENV)
    up = [l for l in rendered.split("\n") if "restraint_" in l and "gcloud storage cp" in l]
    assert up, "no restraint.json upload in the generated script — the report would die with the VM"
    line = up[0]
    for token in ("calib_hi_to_lo__binary_vhl", "fwd", "r0"):
        assert token in line, "the restraint upload path is not keyed on %r: %s" % (token, line.strip())


def _rendered(restrain):
    env = dict(RUNNER_ENV)
    env["RESTRAIN"] = restrain
    env["RSTTAG"] = "_rst" if restrain == "1" else ""
    if restrain != "1":
        env["COMMIT_PREFIX"] = env["COMMIT_PREFIX"][: -len("_rst")]
    return render(heredoc_body(open(WF).read()), env)


def test_the_idempotent_skip_is_restraint_keyed():
    """§L.5/§L.6's transferable rule applied one layer out. The leg RESULT is `leg_<leg>_<dir>_r<seed>.json` and
    carries no restraint component, so the skip would find the UNRESTRAINED r0 binary result already in the
    bucket, print `status=OK (idempotent-skip)`, and exit after ~37 s having computed nothing — reporting
    success for a leg that never ran. That is the §L.6#5 failure verbatim, with `restrain` in place of
    `direction`."""
    on = _rendered("1")
    skip = [l for l in on.split("\n") if "idempotent skip" in l or ("gcloud storage ls" in l and "leg_" in l)]
    assert skip, "no idempotent-skip check found in the generated script"
    ls_line = next((l for l in on.split("\n") if "gcloud storage ls" in l and "leg_" in l), "")
    assert "_rst.json" in ls_line, (
        "the idempotent skip is NOT restraint-keyed — a restrained re-run would find the unrestrained result "
        "and skip: " + ls_line.strip())
    off = _rendered("0")
    ls_off = next((l for l in off.split("\n") if "gcloud storage ls" in l and "leg_" in l), "")
    assert "_rst" not in ls_off, (
        "restrain=0 must keep the historical unsuffixed result name or every existing reader breaks: " + ls_off.strip())


def test_a_restrained_result_cannot_overwrite_the_unrestrained_one():
    """The destructive half. Uploading a restrained ΔG_binary over `leg_<leg>_<dir>_r<seed>.json` would replace
    the number the whole r0 cycle is built on with a DIFFERENT HAMILTONIAN's result, leaving no trace that they
    were ever different calculations."""
    on = _rendered("1")
    ups = [l for l in on.split("\n") if "gcloud storage cp" in l and "leg_" in l and "restraint_" not in l]
    assert ups, "no leg-result upload found in the generated script"
    assert any("_rst.json" in l for l in ups), (
        "the restrained leg result is uploaded under the UNRESTRAINED name and would overwrite it: "
        + " | ".join(l.strip() for l in ups))


# The runner stays LAST: tests defined below a `__main__` block are silently skipped, which has already happened
# twice in this directory. Add new test_* functions ABOVE this line.
if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                print("FAIL", name, "\n      ", e)
                fails += 1
            except Exception as e:  # noqa: BLE001
                print("ERROR", name, "\n      ", type(e).__name__, e)
                fails += 1
    print("\n%d failure(s)" % fails)
    sys.exit(1 if fails else 0)
