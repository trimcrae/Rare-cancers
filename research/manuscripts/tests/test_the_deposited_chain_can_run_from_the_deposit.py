#!/usr/bin/env python3
"""⛔⛔ EVERY MODULE THE DEPOSITED REGENERATION CHAIN INVOKES MUST BE IN THE DEPOSIT.

The Availability statement names `./scripts/regenerate_aso_chain.sh` as the command a reader runs to
establish that the archive is current, and the archive's own manifest row for it promises "The script
AND every step it invokes that no other row here already carries". Both are statements about a set
difference, and until 2026-08-30 nothing computed it.

⚠ WHAT IT COST, MEASURED. Round 23's citations seat found `aso_offtarget_duplex_energy.py` and its
output absent from a 484-path archive that had been PUBLISHED, while the manuscript promised "All
code … every screen's parameters and the complete bounds on each claim are deposited" and printed
four numbers — 8 fully paired off-target duplexes, 45 within 2 kcal/mol, and the 3.2 and 3.0 kcal/mol
margins the two named reagents rest on — that come from nowhere else. It had been missing from every
published version: 482, 483 and 484 paths. Four packaging modules were missing beside it.

⛔ AND THE ARCHIVE WAS INTERNALLY BROKEN, WHICH IS THE PART A COMPLETENESS ARGUMENT MISSES: the
deposited `test_aso_submission_numbers.py` loads the missing JSON and the deposited chain script
invokes the missing module, so the command the paper tells a reader to run died on a clean download.

★ WHY THE EXISTING BACKSTOP COULD NOT SEE IT. The manifest's `gaps.import_closure` is computed from
PYTHON IMPORTS. The chain invokes its steps as SUBPROCESSES by path, which no import graph traverses,
so `promises_resolving_to_no_file` stayed `[]` however many steps were absent. A guard has to read the
script the way the reader runs it — by parsing its invocations — and that is what this file does.

⛔ IT PARSES THE COMMITTED SCRIPT RATHER THAN A LIST. A hand-list of steps is a thing somebody must
remember to extend, and this defect IS that failure: the 2026-08-19 sweep enumerated the steps that
existed then, and every step added afterwards arrived outside every promise glob.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))

CHAIN = os.path.join(REPO, "scripts", "regenerate_aso_chain.sh")
MANIFEST = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-archive-manifest.json")

#: The shell variables the chain resolves its step paths through, read off the script itself below
#: and asserted rather than assumed — a renamed variable must fail loudly, not silently match zero
#: invocations and report a complete archive.
_EXPECTED_VARS = {"MOD", "MAN", "FIG"}

#: ⛔⛔ THE VERB LIST IS PART OF THE MEASUREMENT, AND MATCHING ONLY `python3` MADE THIS GUARD MISS A
#: STEP ON ITS FIRST DAY. Round 24's statistics seat found `test_the_word_manuscript_is_current_and
#: _whole.py` absent from the archive: the chain invokes it with a BARE `pytest`, deliberately and
#: with a comment saying why, so a `python3`-only pattern could not see it — the guard written to
#: enforce "every step the script invokes is deposited" was itself blind to a whole class of step.
#: ★ THE GENERAL LESSON, WHICH OUTLIVES THE FIX: a guard that parses a script must enumerate the
#: INVOCATION VERBS that script actually uses, and `test_the_parser_actually_finds_the_chains_steps`
#: below asserts the count so a new verb fails loudly instead of shrinking the measured set.
_INVOCATION = re.compile(
    r"(?:python3|python|pytest|bash|sh)\s+(?:-m\s+\S+\s+)?"
    r"(?:\$\{?(?P<var>\w+)\}?/)?(?P<rel>[\w/][\w/.-]*\.py)")


def _manifest():
    with io.open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def _script():
    with io.open(CHAIN, encoding="utf-8") as fh:
        return fh.read()


def _var_map(src):
    """`{name: path}` for each `NAME="…"` assignment the chain uses in a step path."""
    #: ⚠ RESOLVE NESTED REFERENCES RATHER THAN SKIP THEM. The first draft dropped any assignment
    #: containing a `$`, which silently dropped `FIG=$MAN/figures` — one of the three step
    #: directories — and would have reported a complete archive while never looking at the figure
    #: steps. That is the fail-quiet shape this whole file replaces, reproduced inside it.
    out = {}
    for m in re.finditer(r'^(?P<name>\w+)="?(?P<val>[^"\n]+)"?\s*$', src, re.M):
        name, val = m.group("name"), m.group("val").strip()
        if not val:
            continue
        for _ in range(4):
            expanded = re.sub(r"\$\{?(\w+)\}?",
                              lambda mm: out.get(mm.group(1), mm.group(0)), val)
            if expanded == val:
                break
            val = expanded
        if "$" in val:
            continue
        out[name] = val.lstrip("./")
    return out


def _invoked(src):
    """Every `.py` the chain runs as a subprocess, as a repo-relative path."""
    variables = _var_map(src)
    out = set()
    for m in _INVOCATION.finditer(src):
        var, rel = m.group("var"), m.group("rel")
        if var:
            base = variables.get(var)
            if base is None:
                continue
            out.add(os.path.normpath(os.path.join(base, rel)).replace(os.sep, "/"))
        elif rel.startswith(("research/", "scripts/")):
            out.add(rel)
    return out


def test_the_parser_actually_finds_the_chains_steps():
    """⛔ THE PRECONDITION, AND IT IS THE ONE THAT FAILS SILENTLY. A parser that matches nothing
    reports a complete archive for any archive at all — the same fail-quiet shape as the
    import-closure backstop it replaces. So assert the chain's own variables are the ones this file
    resolves, and that a real number of steps came back."""
    src = _script()
    variables = _var_map(src)
    assert _EXPECTED_VARS <= set(variables), (
        f"the chain no longer defines {sorted(_EXPECTED_VARS - set(variables))}; this guard resolves "
        "step paths through those variables and would silently match fewer steps")
    invoked = _invoked(src)
    assert len(invoked) >= 25, (
        f"only {len(invoked)} step module(s) parsed out of {os.path.relpath(CHAIN, REPO)}. The chain "
        "runs far more than that, so the invocation pattern has stopped matching and this guard is "
        "measuring nothing")


def test_every_module_the_chain_invokes_is_in_the_archive():
    """⛔⛔ THE PROPERTY ITSELF. A reader who downloads the DOI and runs the named command must have
    every file that command executes."""
    src = _script()
    manifest = _manifest()
    deposited = {f["path"] for f in manifest["files"]}
    missing = sorted(rel for rel in _invoked(src)
                     if rel not in deposited and os.path.exists(os.path.join(REPO, rel)))
    assert not missing, (
        f"{len(missing)} module(s) that scripts/regenerate_aso_chain.sh invokes are NOT in the "
        f"archive, so the command the Availability statement names dies on a clean download:\n  "
        + "\n  ".join(missing)
        + "\n\nAdd them to a `patterns` list in research/manuscripts/aso_archive_manifest.py and "
        "re-derive the manifest. ⛔ Do NOT weaken the manifest's promise instead — the paper says "
        "all code is deposited, and the code exists.")


def test_the_deposited_chain_does_not_read_an_undeposited_artifact():
    """★ THE OTHER HALF OF 'IT CAN RUN'. A step present in the archive whose INPUT is not is the
    same failure one level in — and it is the shape that actually shipped: the deposited
    `test_aso_submission_numbers.py` loaded `aso-offtarget-duplex-energy.json`, which was not
    deposited.

    Scoped to the artifacts a deposited test opens by name, because that is the set a reader
    exercises by running the archive's own tests.
    """
    manifest = _manifest()
    deposited = {f["path"] for f in manifest["files"]}
    tests = sorted(p for p in deposited
                   if "/tests/" in p and p.endswith(".py") and os.path.exists(os.path.join(REPO, p)))
    assert tests, "no deposited test files; this guard would pass vacuously"
    referenced = re.compile(r'"(research/modalities/[\w./-]+\.json)"')
    missing = {}
    for rel in tests:
        with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
            body = fh.read()
        for name in re.findall(r'"([\w-]+\.json)"', body):
            cand = "research/modalities/" + name
            if os.path.exists(os.path.join(REPO, cand)) and cand not in deposited:
                missing.setdefault(cand, []).append(rel)
        for cand in referenced.findall(body):
            if os.path.exists(os.path.join(REPO, cand)) and cand not in deposited:
                missing.setdefault(cand, []).append(rel)
    assert not missing, (
        "a deposited test opens an artifact the archive does not carry, so the archive's own tests "
        "cannot run from the archive:\n  "
        + "\n  ".join(f"{k} — opened by {sorted(set(v))[0]}" for k, v in sorted(missing.items())))


# ══════════════════════════════════════════════════════════════════════════════════════════
# ⛔⛔ THE THIRD ITERATION OF ONE BLINDNESS: a deposited STEP whose INPUTS are not deposited
# ══════════════════════════════════════════════════════════════════════════════════════════
#: ⚠ THE GUARD ABOVE HAS NOW MISSED THE SAME CLASS THREE TIMES, EACH TIME ONE LEVEL FURTHER IN, and
#: each time it passed while the archive was broken:
#:   · round 23 — the chain invoked `python3 -m pytest`, matched; a BARE `pytest` did not (verb).
#:   · round 24 — `FIG=$MAN/figures` was dropped as "contains a $", so the figure steps were unseen.
#:   · round 26 — every MODULE the chain invokes was deposited, and three artifacts one of them
#:     opens by name were not. `test_the_deposited_chain_does_not_read_an_undeposited_artifact`
#:     could not see it either: that one is scoped to deposited TEST files, and this is a producer.
#:
#: ⛔ WHAT THE THIRD ONE COST, MEASURED. `aso_noncoding_acceptor_screened_table.py` and its output
#: were both in the 496-path archive; its `ATLAS`, `PARENT_SCREEN` and `PREMRNA_SCREEN` were not, and
#: neither was any file of the `noncoding-acceptor/` directory its rows are built from. A reader
#: running the Availability statement's own command therefore got a clean exit and a table with NO
#: junction rows written over the one holding the exon-2 reagents' 8 and 9 bp parent duplexes.
#:
#: ★ SO THIS READS THE MODULE THE WAY THE INTERPRETER DOES — module-level assignments, resolved by
#: AST — rather than the way a reviewer reads a filename. `HERE = os.path.dirname(os.path.abspath(
#: __file__))` and `os.path.join(HERE, "x.json")` are the two idioms every module in this lane uses,
#: and both are evaluated here. A constant that resolves to no file on disk is not a finding: the
#: question is only ever "this file exists in the tree and the archive does not carry it".
_DATA_SUFFIXES = (".json", ".jsonl", ".csv", ".tsv", ".txt", ".fasta", ".fa")


def _module_level_paths(full):
    """Every filesystem path a module names at module level, as absolute paths.

    Returned as `{constant name: absolute path}` — the NAME is what tells an input from an output.
    Evaluates the two idioms this lane actually uses — `os.path.dirname(os.path.abspath(__file__))`
    and `os.path.join(...)` over already-known names — and returns `None` for anything else rather
    than guessing. A bare filename constant is resolved against the module's own directory and
    against any module-level constant that names a real directory, because `SCREEN_DIR` plus a bare
    `ATLAS` is precisely the shape that shipped broken.
    """
    tree = ast.parse(io.open(full, encoding="utf-8").read())
    home = os.path.dirname(full)
    env = {}

    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            return env.get(node.id)
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if name == "join":
                parts = [ev(a) for a in node.args]
                if parts and all(isinstance(x, str) for x in parts):
                    return os.path.join(*parts)
            #: `dirname(abspath(__file__))` and its variants all denote the module's directory.
            if name in ("dirname", "abspath", "realpath"):
                return home
        return None

    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        value = ev(node.value)
        if isinstance(value, str):
            env[node.targets[0].id] = value

    dirs = [home] + [v for v in env.values() if os.path.isdir(v)]
    out = {}
    for name, value in env.items():
        if not value.endswith(_DATA_SUFFIXES):
            continue
        if os.path.isabs(value):
            out[name] = os.path.normpath(value)
            continue
        for base in dirs:
            cand = os.path.join(base, value)
            if os.path.exists(cand):
                out[name] = os.path.normpath(cand)
                break
    return out


def _names_opened_for_writing(full):
    """The module-level constant NAMES this module opens for writing — those are outputs.

    ⛔ WITHOUT THIS THE GUARD REDS ON HONEST INPUT, which is how a gate gets loosened until it
    measures nothing. Three chain steps name a path they PRODUCE: `aso_archive_manifest.py` writes
    the manifest (which structurally cannot list itself), `svg_to_print_formats.py` writes
    `print-formats-manifest.json` and re-reads the previous copy only to diff against it, and
    `lint_citations.py --baseline` writes the provenance ledger. A reader missing an OUTPUT is not
    missing anything.

    ⭐ MATCHED BY AST ON THE CALL, NOT BY A TEXT SEARCH FOR THE FILENAME. A regex that asks
    "does this file mention `open(..., 'w')` anywhere AND mention this basename anywhere" answers
    yes for every producer that also reads something, which would excuse the exact omission this
    file exists to catch.
    """
    tree = ast.parse(io.open(full, encoding="utf-8").read())
    written = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "open" or not node.args:
            continue
        mode = node.args[1] if len(node.args) > 1 else next(
            (k.value for k in node.keywords if k.arg == "mode"), None)
        literal = isinstance(mode, ast.Constant) and isinstance(mode.value, str)
        if not literal or not any(c in mode.value for c in "wax"):
            continue
        if isinstance(node.args[0], ast.Name):
            written.add(node.args[0].id)
    return written


def test_every_input_an_invoked_module_names_is_in_the_archive():
    """⛔⛔ THE PROPERTY, ONE LEVEL IN FROM THE STEP LIST. A deposited step whose input is absent
    fails as surely as an absent step — and worse, because it can succeed."""
    manifest = _manifest()
    deposited = {f["path"] for f in manifest["files"]}
    #: ⚠ THE MANIFEST IS IN THE ARCHIVE AND CANNOT BE IN ITS OWN FILE LIST — a file cannot carry its
    #: own hash. `zenodo_deposit.build_zip` writes it into the zip as an extra member beside the
    #: listed files, and the deposition description records its digest separately for that reason.
    #: So a step that reads it is reading something the reader HAS; excluding it here is the one
    #: place this guard trusts a fact it cannot see in `files[]`, and it is asserted below rather
    #: than assumed.
    shipped_beside_the_list = {os.path.relpath(MANIFEST, REPO).replace(os.sep, "/")}
    deposited |= shipped_beside_the_list
    missing = {}
    for rel in sorted(_invoked(_script())):
        full = os.path.join(REPO, rel)
        if not os.path.exists(full) or rel not in deposited:
            continue
        outputs = _names_opened_for_writing(full)
        for name, path in sorted(_module_level_paths(full).items()):
            if name in outputs:
                continue
            cand = os.path.relpath(path, REPO).replace(os.sep, "/")
            if cand.startswith("..") or cand in deposited or not os.path.exists(path):
                continue
            missing.setdefault(cand, []).append(rel)
    assert not missing, (
        f"{len(missing)} artifact(s) a DEPOSITED chain step opens by name are not in the archive, "
        "so the command the Availability statement names runs against inputs a reader does not "
        "have:\n  "
        + "\n  ".join(f"{k} — named by {sorted(set(v))[0]}" for k, v in sorted(missing.items()))
        + "\n\n⛔ A step that reads a missing input may SUCCEED and write an empty artifact over a "
        "populated one. Add the inputs to a `patterns` list in "
        "research/manuscripts/aso_archive_manifest.py and re-derive the manifest.")


def test_the_input_reader_actually_resolves_this_lanes_two_idioms():
    """⛔ THE PRECONDITION, and the one that fails silently: a resolver that evaluates nothing
    reports a complete archive for every archive. Driven against the module whose inputs were the
    measured omission, so a refactor that renames `HERE` or moves the constants fails loudly."""
    full = os.path.join(REPO, "research", "modalities",
                        "aso_noncoding_acceptor_screened_table.py")
    assert os.path.exists(full), "the module the third iteration was measured on has moved"
    found = {os.path.relpath(p, REPO).replace(os.sep, "/")
             for p in _module_level_paths(full).values()}
    for rel in ["research/modalities/nr4a3-fusion-junction-atlas-noncoding-acceptor.json",
                "research/modalities/aso-parent-gap-pairing-noncoding-acceptor.json",
                "research/modalities/aso-premrna-offtarget-noncoding-acceptor.json",
                "research/modalities/aso-genome-offtarget-noncoding-acceptor.json"]:
        assert rel in found, (
            f"the module-level path resolver no longer finds {rel}, which this module names as a "
            "bare filename joined to HERE. It resolved all four when the guard was written, and a "
            "resolver that finds nothing passes every archive")


def test_the_table_module_refuses_to_overwrite_its_own_answer_with_an_empty_one():
    """★ THE OTHER HALF OF THE FIX, ASSERTED RATHER THAN DESCRIBED. Depositing the inputs makes the
    chain run TODAY; it does not stop a partial download, a dropped pattern or a run from the wrong
    directory reproducing the destruction. `_refuse_to_replace_a_populated_table` is the standing
    guard, and a guard nothing imports is this repository's own recorded failure mode."""
    full = os.path.join(REPO, "research", "modalities",
                        "aso_noncoding_acceptor_screened_table.py")
    body = io.open(full, encoding="utf-8").read()
    assert "_refuse_to_replace_a_populated_table(out)" in body, (
        "the non-canonical table module no longer refuses to replace a populated table with an "
        "empty one. That write is silent, exits 0, and destroys the only committed record of the "
        "non-canonical junctions' screened numbers")


def test_the_manifest_really_is_shipped_beside_its_own_file_list():
    """⛔ THE ONE EXEMPTION ABOVE, DRIVEN AGAINST THE PACKAGER RATHER THAN BELIEVED. If the zip
    builder ever stops adding the manifest itself, a chain step that reads it becomes a real
    omission and the exemption would hide it — which is how an exemption written for a true reason
    outlives the reason."""
    body = io.open(os.path.join(REPO, "scripts", "zenodo_deposit.py"), encoding="utf-8").read()
    assert "z.write(os.path.join(REPO, manifest_rel), manifest_rel)" in body, (
        "scripts/zenodo_deposit.build_zip no longer writes the manifest into the archive, so the "
        "manifest is NOT shipped beside its file list and the exemption in "
        "test_every_input_an_invoked_module_names_is_in_the_archive is now hiding a real gap")


def test_the_manifest_promise_row_for_the_chain_still_claims_completeness():
    """⚠ THE ROW'S SENTENCE IS WHAT MAKES THIS A BLOCKER RATHER THAN AN OMISSION, so it is asserted
    rather than trusted. If a future session weakens the promise instead of fixing the archive, the
    guards above stop meaning what they mean, and this fails to say so."""
    manifest = _manifest()
    rows = [p for p in manifest.get("promises", [])
            if "scripts/regenerate_aso_chain.sh" in (p.get("files") or [])]
    assert len(rows) == 1, f"expected exactly one promise row carrying the chain, found {len(rows)}"
    #: ⚠ THE SENTENCE IS SERIALISED ONTO THE FILE ENTRIES, NOT ONTO THE PROMISE ROW. The row carries
    #: only `promise_text`, `n_files` and `files`; each entry in `files[]` carries the `contributes`
    #: prose. Looking for it on the row found nothing and would have passed the day it was deleted.
    contributes = " ".join(f.get("contributes", "") for f in manifest["files"]
                           if f["path"] == "scripts/regenerate_aso_chain.sh")
    assert contributes, "the chain has no file entry in the manifest, so it is not deposited at all"
    assert "every step it invokes" in contributes, (
        "the chain's promise row no longer claims to carry every step it invokes. If that promise "
        "was deliberately narrowed, the manuscript's Availability statement has to narrow with it — "
        "and it says all code is deposited.")


@pytest.mark.parametrize("rel", ["research/modalities/aso_offtarget_duplex_energy.py",
                                 "research/modalities/aso-offtarget-duplex-energy.json"])
def test_the_screen_behind_the_printed_kcal_margins_is_deposited(rel):
    """⛔ THE SPECIFIC OMISSION, NAMED, because a general guard that regresses on one artifact is
    how a fixed defect comes back unnoticed. These two are the sole source of four numbers the
    manuscript prints: 8 designs with a fully paired 16 bp off-target duplex, 45 within 2 kcal/mol,
    and the named reagents' 3.2 and 3.0 kcal/mol separations."""
    deposited = {f["path"] for f in _manifest()["files"]}
    assert rel in deposited, (
        f"{rel} is not in the archive, and the manuscript prints numbers that come from nowhere "
        "else. This was missing from three published versions before round 23 found it.")
