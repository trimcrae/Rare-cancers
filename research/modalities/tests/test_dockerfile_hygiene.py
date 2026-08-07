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


# A BuildKit heredoc opener: `<<PY`, `<<'PY'`, `<<"PY"`, `<<-PY`. Anchored on an identifier so a `<<<`
# here-string does not match (its third `<` is not an identifier character), since a here-string consumes
# no following lines.
_HEREDOC_OPEN = re.compile(r"<<-?\s*(?:'([A-Za-z_]\w*)'|\"([A-Za-z_]\w*)\"|([A-Za-z_]\w*))")


def _orphan_lines(text, name="<text>"):
    """Lines a Dockerfile frontend would read as instructions but that are not. Heredoc bodies excluded.

    A callable seam, so the guarantee can be asserted against SYNTHETIC input: a heredoc-aware parser that
    had gone blind to the multi-line `python -c` bug would still pass against every real file in the repo,
    which is the failure this split exists to make impossible.

    Openers are queued as seen and activated only when the backslash chain ends, because a heredoc opened
    on a continuation line does not begin its body until the whole logical line does -- and one logical
    line may open several.
    """
    offenders, cont = [], False
    pending, active = [], None
    for i, line in enumerate(text.splitlines(), 1):
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
            offenders.append(f"{name}:{i}: {stripped[:80]}")
        pending += [next(g for g in m.groups() if g) for m in _HEREDOC_OPEN.finditer(line)]
        cont = line.rstrip().endswith("\\")
        if not cont and pending:
            active = pending.pop(0)
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

    ⛔ HEREDOC BODIES ARE SKIPPED, AND THAT IS THE POINT RATHER THAN AN EXEMPTION. `RUN python - <<'PY'
    ... PY` is valid BuildKit syntax and is the CORRECT way to embed a multi-line payload -- it is the fix
    for the very defect this test exists to catch. Before this the walker read `Dockerfile.boltz`'s Python
    body as ten stray instructions and went red on a file that is right. A check that fails the correct
    construct while passing the broken one teaches the next author to write the broken one.

    ⚠ The opener can appear on a CONTINUATION line (`RUN a \\` / ` && python - <<'PY'`), and the body does
    not begin until the whole logical line ends. Openers are therefore collected as seen and activated only
    once the backslash chain stops -- tracking them only on non-continuation lines would have missed this
    file's, which is exactly where it occurs. A logical line may open MORE THAN ONE, so `pending` is a queue.

    ⚠ MERGE NOTE (2026-08-07): this walker and a simpler one were written independently on two branches for
    the same `Dockerfile.boltz` failure. THIS one is kept because the other activated a heredoc immediately
    on sight and tracked only one terminator, so a continuation-line opener -- the only kind this repo
    actually has -- would have been mis-parsed. What the other branch contributed and is retained below is
    `_orphan_lines` as a callable seam plus `test_a_heredoc_file_pins_the_frontend_that_can_parse_it`: the
    heredoc is legal ONLY under the dockerfile:1.4+ frontend, and nothing here required the `# syntax=`
    directive that guarantees it.
    """
    offenders = _orphan_lines(path.read_text(), path.name)
    assert not offenders, "orphan lines (a quoted payload broken across lines?):\n" + "\n".join(offenders)


@pytest.mark.parametrize("path", DOCKERFILES, ids=lambda p: p.name)
def test_a_heredoc_file_pins_the_frontend_that_can_parse_it(path):
    """A heredoc needs `# syntax=docker/dockerfile:1` (1.4+), and it must be the FIRST line to be honoured.

    Without it the parse depends on whichever frontend the builder happens to bundle, and the failure mode
    is `unknown instruction: IMPORT` three layers in -- the same class of misleading late error this
    module's docstring was written for. Every heredoc-using image in this repo is built by a plain
    `docker build`, so nothing supplies a newer frontend on its behalf.
    """
    text = path.read_text()
    if not _HEREDOC_OPEN.search(text):
        pytest.skip("no heredoc in this file")
    first = text.splitlines()[0].strip()
    assert re.match(r"#\s*syntax\s*=\s*docker/dockerfile:1", first), (
        f"{path.name} uses a heredoc but its first line is {first[:60]!r} -- a "
        "`# syntax=docker/dockerfile:1` directive must come first, or the body is parsed as instructions")


def test_the_orphan_parser_still_catches_the_bug_it_exists_for():
    """Teaching it heredocs must not have taught it to ignore the multi-line `python -c` payload."""
    bad = 'FROM x\nRUN python -c "import os\nprint(os.getcwd())\nos.exit(0)"\n'
    assert len(_orphan_lines(bad)) == 2, _orphan_lines(bad)


@pytest.mark.parametrize("text", [
    "FROM x\nRUN python - <<'PY'\nimport os\nPY\nRUN echo done\n",        # quoted terminator
    "FROM x\nRUN python - <<PY\nimport os\nPY\nRUN echo done\n",          # unquoted
    "FROM x\nRUN cat <<-EOF\nimport os\nEOF\nRUN echo done\n",            # tab-stripping form
    'FROM x\nRUN grep a <<< "b"\nRUN echo done\n',                        # here-STRING consumes no lines
    "FROM x\nRUN a \\\n && python - <<'PY'\nimport os\nPY\nRUN b\n",       # opener on a CONTINUATION line
])
def test_valid_heredoc_forms_are_not_condemned(text):
    assert _orphan_lines(text) == []


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
