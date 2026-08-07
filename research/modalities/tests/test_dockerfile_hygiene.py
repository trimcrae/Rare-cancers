"""Structural checks on the repo's container definitions.

These exist because both failure modes below have actually cost a build (and, in one case, sent the
build on to fail three layers later with a misleading error):

  * A load-bearing `RUN` ending in a chain-wide `|| true`. Written as
    `RUN pip install X && pip cache purge || true`, the `|| true` applies to the WHOLE chain, so a
    FAILED install produces a SUCCESSFUL layer. The pmx image built "fine" and then died on a bare
    "No module named 'pmx'". A tolerant exit belongs on cache cleanup, never on the step that
    installs the engine.
  * A multi-line `python -c` payload inside a `RUN`. Dockerfile has no notion of a continued quoted
    string, so every line after the first is parsed as an instruction: "unknown instruction: import".

Both are cheap to assert and neither is caught by anything else in CI.
"""

import pathlib
import re

import pytest

DOCKERFILES = sorted((pathlib.Path(__file__).resolve().parents[2] / "compute").glob("Dockerfile.*"))

INSTRUCTIONS = {
    "FROM", "RUN", "ENV", "COPY", "ADD", "WORKDIR", "CMD", "ENTRYPOINT", "ARG", "LABEL",
    "EXPOSE", "USER", "VOLUME", "SHELL", "HEALTHCHECK", "ONBUILD", "STOPSIGNAL",
}

# Steps where a tolerant exit is the POINT, not an oversight: cache cleanup and best-effort
# relocation fixups. Anything else that swallows its exit status is a bug.
TOLERANT_OK = ("micromamba clean", "pip cache purge", "rm -rf /opt/mamba/pkgs", "apt-get",
               "du -sh", "conda-unpack")


def _logical_instructions(text):
    """Join backslash continuations into logical instructions. Returns [(line_no, text)]."""
    out, buf, start = [], "", 1
    for i, line in enumerate(text.splitlines(), 1):
        if not buf:
            start = i
        buf += line.rstrip("\\")
        if line.rstrip().endswith("\\"):
            continue
        out.append((start, buf))
        buf = ""
    if buf:
        out.append((start, buf))
    return out


def test_dockerfiles_exist():
    assert DOCKERFILES, "expected at least one Dockerfile under research/compute"


@pytest.mark.parametrize("path", DOCKERFILES, ids=lambda p: p.name)
def test_no_load_bearing_run_swallows_its_exit_status(path):
    offenders = []
    for line_no, instr in _logical_instructions(path.read_text()):
        s = instr.strip()
        if not s.upper().startswith("RUN "):
            continue
        if not re.search(r"\|\|\s*true\s*$", s):
            continue
        if any(ok in s for ok in TOLERANT_OK):
            continue
        offenders.append(f"{path.name}:{line_no}: {s[:100]}")
    assert not offenders, (
        "a RUN that ends in `|| true` cannot fail, so a broken install produces a working layer:\n"
        + "\n".join(offenders))


# A BuildKit heredoc opener: `<<PY`, `<<'PY'`, `<<"PY"`, `<<-PY`. Anchored on an identifier so a
# `<<<` herestring does not match (its third `<` is not an identifier character).
_HEREDOC_OPEN = re.compile(r"<<-?\s*(?:'([A-Za-z_]\w*)'|\"([A-Za-z_]\w*)\"|([A-Za-z_]\w*))")


@pytest.mark.parametrize("path", DOCKERFILES, ids=lambda p: p.name)
def test_every_line_is_an_instruction_or_a_continuation(path):
    """Catches a multi-line `python -c` payload, which Dockerfile parses as stray instructions.

    ⛔ HEREDOC BODIES ARE SKIPPED, AND THAT IS THE POINT RATHER THAN AN EXEMPTION (2026-08-07).
    `RUN python - <<'PY' ... PY` is valid BuildKit syntax and is the CORRECT way to embed a multi-line
    payload -- it is the fix for the very defect this test exists to catch. Before this change the
    walker had no notion of a heredoc, so it read `Dockerfile.boltz`'s Python body as ten stray
    instructions and went red on a file that is right. A check that fails the correct construct while
    passing the broken one teaches the next author to write the broken one, which is worse than not
    checking. The `python -c "..."`-split-across-lines pattern is still caught: those lines are not
    inside a heredoc.

    ⚠ The opener can appear on a CONTINUATION line (`RUN a \\` / ` && python - <<'PY'`), and the body
    does not begin until the whole logical line ends. So openers are collected as they are seen and
    only activated once the backslash chain stops -- tracking them only on non-continuation lines
    would have missed this file's, which is exactly where it occurs.
    """
    offenders, cont = [], False
    pending, active = [], None
    for i, line in enumerate(path.read_text().splitlines(), 1):
        stripped = line.strip()
        if active is not None:                       # inside a heredoc body
            if stripped == active:
                active = pending.pop(0) if pending else None
            continue
        if cont:
            pending += [next(g for g in m.groups() if g) for m in _HEREDOC_OPEN.finditer(line)]
            cont = line.rstrip().endswith("\\")
            if not cont and pending:
                active = pending.pop(0)
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.split(" ", 1)[0].upper() not in INSTRUCTIONS:
            offenders.append(f"{path.name}:{i}: {stripped[:80]}")
        pending += [next(g for g in m.groups() if g) for m in _HEREDOC_OPEN.finditer(line)]
        cont = line.rstrip().endswith("\\")
        if not cont and pending:
            active = pending.pop(0)
    assert not offenders, "orphan lines (a quoted payload broken across lines?):\n" + "\n".join(offenders)


def test_the_heredoc_skip_does_not_swallow_a_genuinely_broken_payload():
    """The heredoc fix must not blunt the check it lives inside.

    Written because the change above makes the walker skip lines, and a skip is exactly how a guard
    silently stops guarding. Two synthetic Dockerfiles: one correct heredoc (must pass), one split
    `python -c` payload of the kind the test was built for (must still be caught).
    """
    import tempfile
    good = 'FROM x\nRUN a \\\n && python - <<\'PY\'\nimport os\nprint(os.sep)\nPY\nRUN b\n'
    bad = 'FROM x\nRUN python -c "import os\nprint(os.sep)"\nRUN b\n'
    with tempfile.TemporaryDirectory() as d:
        for name, text, expect_offenders in (("Dockerfile.good", good, False),
                                             ("Dockerfile.bad", bad, True)):
            p = pathlib.Path(d) / name
            p.write_text(text)
            try:
                test_every_line_is_an_instruction_or_a_continuation(p)
                caught = False
            except AssertionError:
                caught = True
            assert caught is expect_offenders, f"{name}: expected offenders={expect_offenders}"


def test_the_pmx_image_gates_its_engine_install():
    """The pmx layer must prove the import, not merely run pip."""
    pmx = next((p for p in DOCKERFILES if p.name == "Dockerfile.pmxfep"), None)
    assert pmx is not None
    text = pmx.read_text()
    assert "import pmx" in text, "the image must verify pmx imports at BAKE time, on free CI"
    assert "GPU support" in text, "the image must refuse a CPU-only GROMACS at bake time"
