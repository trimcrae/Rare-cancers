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


# `<<PY`, `<<'PY'`, `<<"PY"`, `<<-PY` — the shell heredoc forms BuildKit's dockerfile:1.4+ frontend accepts.
# Anchored to a `<<` that is not `<<<` (a here-STRING, which consumes no following lines).
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1(?!<)")


def _heredoc_terminator(line):
    """The terminator word a heredoc on this line opens, or None. Ignores `<<<` here-strings."""
    body = line.split("#", 1)[0]
    if "<<<" in body:
        body = body.replace("<<<", "")
    m = _HEREDOC.search(body)
    return m.group(2) if m else None


def _orphan_lines(text, name="<text>"):
    """Lines a Dockerfile frontend would read as instructions but that are not. Heredoc bodies excluded.

    Extracted from the test that uses it so the guarantee can be asserted against synthetic input — a
    heredoc-aware parser that had gone blind to the multi-line `python -c` bug would still pass against
    every real file in the repo, which is the failure this split exists to make impossible.
    """
    offenders, cont, terminator = [], False, None
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if terminator is not None:
            # Inside a heredoc body: consumed by the process on stdin, never by the Dockerfile parser.
            if stripped == terminator:
                terminator = None
            continue
        if cont:
            cont = line.rstrip().endswith("\\")
            terminator = _heredoc_terminator(line) or terminator
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.split(" ", 1)[0].upper() not in INSTRUCTIONS:
            offenders.append(f"{name}:{i}: {stripped[:80]}")
        cont = line.rstrip().endswith("\\")
        terminator = _heredoc_terminator(line)
    return offenders


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


@pytest.mark.parametrize("path", DOCKERFILES, ids=lambda p: p.name)
def test_every_line_is_an_instruction_or_a_continuation(path):
    """Catches a multi-line `python -c` payload, which Dockerfile parses as stray instructions.

    ⚠ A HEREDOC BODY IS NOT THAT BUG, and this test used to say it was (measured 2026-08-06, on
    `Dockerfile.boltz`, which had landed the day before). `RUN python - <<'PY' … PY` hands its body to the
    process on stdin; the frontend never parses it as instructions, so flagging those lines condemned valid
    syntax. The distinction is the whole point of the check — an unquoted multi-line `python -c` really does
    break the build, and a heredoc really does not — so the parser learns heredocs rather than the file
    getting an exemption. **The heredoc is only legal under the dockerfile:1.4+ frontend**, which is what
    `test_a_heredoc_file_pins_the_frontend_that_can_parse_it` below now requires.
    """
    offenders = _orphan_lines(path.read_text(), path.name)
    assert not offenders, "orphan lines (a quoted payload broken across lines?):\n" + "\n".join(offenders)


@pytest.mark.parametrize("path", DOCKERFILES, ids=lambda p: p.name)
def test_a_heredoc_file_pins_the_frontend_that_can_parse_it(path):
    """A heredoc needs `# syntax=docker/dockerfile:1` (1.4+), and it must be the FIRST line to be honoured.

    Without it the parse depends on whichever frontend the builder happens to bundle, and the failure mode
    is `unknown instruction: IMPORT` three layers in — the same class of misleading late error this module's
    docstring was written for. Every heredoc-using image in this repo is built by a plain `docker build`.
    """
    text = path.read_text()
    if not any(_heredoc_terminator(line) for line in text.splitlines()):
        pytest.skip("no heredoc in this file")
    first = text.splitlines()[0].strip()
    assert re.match(r"#\s*syntax\s*=\s*docker/dockerfile:1", first), (
        f"{path.name} uses a heredoc but its first line is {first[:60]!r} — a `# syntax=docker/dockerfile:1` "
        "directive must come first, or the heredoc body is parsed as instructions")


def test_the_orphan_parser_still_catches_the_bug_it_exists_for():
    """Teaching it heredocs must not have taught it to ignore the multi-line `python -c` payload."""
    bad = 'FROM x\nRUN python -c "import os\nprint(os.getcwd())\nos.exit(0)"\n'
    assert len(_orphan_lines(bad)) == 2, _orphan_lines(bad)


@pytest.mark.parametrize("text", [
    "FROM x\nRUN python - <<'PY'\nimport os\nPY\nRUN echo done\n",   # quoted terminator
    "FROM x\nRUN python - <<PY\nimport os\nPY\nRUN echo done\n",     # unquoted
    "FROM x\nRUN cat <<-EOF\nimport os\nEOF\nRUN echo done\n",       # tab-stripping form
    'FROM x\nRUN grep a <<< "b"\nRUN echo done\n',                   # here-STRING consumes no lines
])
def test_valid_heredoc_forms_are_not_condemned(text):
    assert _orphan_lines(text) == []


def test_the_pmx_image_gates_its_engine_install():
    """The pmx layer must prove the import, not merely run pip."""
    pmx = next((p for p in DOCKERFILES if p.name == "Dockerfile.pmxfep"), None)
    assert pmx is not None
    text = pmx.read_text()
    assert "import pmx" in text, "the image must verify pmx imports at BAKE time, on free CI"
    assert "GPU support" in text, "the image must refuse a CPU-only GROMACS at bake time"
