#!/usr/bin/env python3
"""Does the census's word "covered" survive being TESTED? Ablation, not inspection.

⛔⛔ WHY THIS EXISTS — THE ROUND-16 DIAGNOSIS, WHICH IS ONE LEVEL ABOVE ROUND 15'S.

`claim_coverage.py` was written because fifteen review rounds would not converge: every blocker was
a surface with zero instruments, so the blocker rate tracked how many new LENSES a round introduced,
not how many defects the paper held. The fix was to stop sampling surfaces and enumerate them.

Round 16 pointed three seats at the enumerator and found the SAME defect one level up:

  seats 1/4/5  the census credited a guard's regexes to documents that guard never opens
               — 22 of 27 "covered" cover-letter sentences were false positives
  seat 5       `MAX_MATCH_SHARE = 0.10` on a 9-sentence document: the smallest representable
               non-zero share is 1/9 = 0.111 > 0.10, so EVERY pattern was discarded before the
               coverage loop ran. `journal-tables: 0 of 9` was integer arithmetic, not a reading
  seat 5       "matches few sentences" was implemented where "distinguishes this sentence" was
               meant, so bold spans, code spans and an ISO date all counted as coverage

★★ THE STRUCTURAL FINDING, AND IT IS WHY ITERATION ALONE CANNOT CONVERGE. Every fix ships a NEW
INSTRUMENT, and every new instrument is a new claim asserted in prose and measured nowhere. So each
round's fix REFILLS the pool the next round drains. Reviewing instruments by READING them can never
catch up with writing them — which is the same shape as CLAUDE.md's "a property asserted in prose
about a value passed by a caller is not a property; it is a hope."

★ WHAT CHANGES THE SHAPE: the census makes a per-sentence claim that is FALSIFIABLE IN ONE
OPERATION. "Sentence S is covered by witness W" predicts that if S changed, W would go red. So
change it and look. This module does that, and it is different in kind from every previous fix:

  · it adds NO new hand-written constant, so there is no new number to get wrong;
  · it derives its expectation from the census's OWN output, so it cannot drift from what the
    census claims;
  · it catches document-blindness, non-selective patterns AND the threshold bug with ONE
    mechanism, because all three make the census credit coverage that is not there.

TWO ERROR DIRECTIONS, BOTH FATAL, AND THE SECOND IS THE ONE INSPECTION NEVER FINDS:

  FALSE POSITIVE   census says COVERED, the named witness stays green when the sentence changes
                   -> the census is crediting a guard that binds nothing. Inflates `covered`,
                      shrinks the UNCOVERED list, and HIDES surfaces. The comfortable direction.
  FALSE NEGATIVE   census says UNCOVERED, some guard goes red when the sentence changes
                   -> the census under-reports. Wastes review budget, and (round 16) is what a
                      threshold that cannot represent a short document looks like from outside.

⚠ SCOPE, STATED HONESTLY, AND THE FIRST VERSION OF THIS PARAGRAPH WAS NOT (round 17 seat A). It
said the perturbation changes "the first digit-run", while `ablate`'s own docstring said EVERY digit
run is tried — the module documented two different behaviours, and the function implementing the one
described here had ZERO callers. It also disposed of predicate sentences as "out of scope", which is
false: 9 of the 44 covered numbered article sentences carry no claim number at all, only digits
inside identifiers ("RNase-H1", "5-6-5", "three of three"), so they are perturbed on something that
is not their claim and pass for the wrong reason.

WHAT IS ACTUALLY TRUE: every digit run in the sentence is tried and the FIRST one that trips any
guard wins. That answers "would anything notice a change here?", which is the question the census is
a proxy for. It does NOT answer "is this sentence's own claim watched?" — a sentence can pass on an
exon number while its rate goes unread. Reported, not hidden: `claim_coverage.json` records the
per-sentence witness list, and the gap between the two questions is the honest residue.
"""
from __future__ import annotations

import atexit
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

sys.path.insert(0, HERE)
import claim_coverage as cc  # noqa: E402
import claim_ablation_cache as _cache  # noqa: E402
from claim_quantity_identifiers import orcid_spans  # noqa: E402

#: The witness kinds the census emits, and the command that re-runs each one.
_LINT_CONSISTENCY = [sys.executable, os.path.join(HERE, "lint_consistency.py")]


def _locate(text, sentence):
    r"""Find a censused sentence in the RAW file, tolerating the line wrapping the flattener removed.

    ⛔⛔ THE FIRST VERSION USED `sentence in text`, AND IT MATCHED NOTHING — NOT ONCE IN SEVEN TRIES
    (2026-08-22, caught by a positive control, not by a red run). `claim_coverage._prose` joins lines
    and collapses whitespace, so a censused sentence is the file's text with its LINE BREAKS REMOVED
    and almost never appears verbatim. Every ablation silently did nothing, reported "no witness went
    red", and would have been read as "these guards are blind" — a fabricated measurement about to be
    used to justify narrowing the census.
    ★ Matching with `\s+` between tokens is what makes the mutation actually land.

    ⛔⛔ AND WHITESPACE WAS NOT THE ONLY THING REMOVED (AUT-PD-132, 2026-08-28). `_prose` also strips
    `<!--…-->`, `<sup>…</sup>` and whole heading/table/quote lines, so every sentence carrying a
    citation marker — 15 across the two censused papers, one of them a pinned figure — was
    unlocatable and scored NOT-APPLIED: counted as covered and perturbed by nothing. The locator now
    lives next to the flattener it inverts, is derived from the same regexes, and verifies its match
    by re-flattening it. See `claim_coverage.locate`.
    """
    return cc.locate(text, sentence)


def _witness_cmd(witness):
    """The command that re-runs one witness, or None if this witness is not runnable.

    The census emits two witness kinds: `test:<file>.py`, re-run as that pytest module, and
    `pin:<id>`, whose enforcement lives in `lint_consistency.py`.
    """
    if witness.startswith("test:"):
        return [sys.executable, "-m", "pytest", os.path.join(cc.TESTS, witness[len("test:"):]),
                "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:randomly"]
    if witness.startswith("pin:"):
        return list(_LINT_CONSISTENCY)
    if witness.startswith("generator:"):
        # A generated document's binding is REPRODUCTION: `--check` exits non-zero when the committed
        # file no longer matches what its generator produces.
        return [sys.executable, os.path.join(REPO, witness[len("generator:"):]), "--check"]
    return None


def _run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).returncode != 0


#: The distinct outcomes of one ablation. ⛔ `NOT_APPLIED` MUST NEVER BE COLLAPSED INTO "no witness
#: went red": that conflation is what produced the fabricated reading above, and it is the same
#: early-exit-reports-a-pass defect this module exists to detect in other guards.
APPLIED, NOT_APPLIED = "applied", "not-applied"

#: One hard-linked clone of the repository, made once per process and reused.
_WORKSPACE = None


def _workspace():
    """A disposable clone of the repo that mutations happen in, so the REAL tree is never touched.

    ⛔⛔ THE FIRST VERSION MUTATED THE REAL MANUSCRIPT IN PLACE, AND IT CORRUPTED A PREFLIGHT RUN
    (measured 2026-08-22). A `finally` plus a digest check makes the mutation window SHORT; it does
    not make it SAFE, because safety here is about everything ELSE reading the repo during that
    window. Proven, not inferred: perturbing a pinned figure and running
    `research/modalities/tests/test_lint_consistency.py::test_the_real_repo_is_consistent`
    concurrently reproduces exactly the failure a preflight reported —
    `lint_consistency` reads the same file and sees a pin that disagrees with its artifact.
    ⚠ AND THE `finally` IS NOT EVEN RELIABLE: a process killed with SIGTERM (or its orphaned
    grandchild, which `pkill -P` does not reach) skips it and leaves a DEPOSIT ARTIFACT corrupted on
    disk. A gate that can lose a manuscript is not a gate.

    ★ `cp -al` COSTS 0.03 s FOR 3,326 FILES, so there was never a reason to accept the risk. The
    clone shares inodes, which means an IN-PLACE write would still reach the original — measured, it
    does — so every mutation is written to a new file and `os.replace`d into position, which breaks
    the link instead of following it.
    """
    global _WORKSPACE
    if _WORKSPACE and os.path.isdir(_WORKSPACE):
        return _WORKSPACE
    root = tempfile.mkdtemp(prefix="claim-ablation-")
    for entry in os.listdir(REPO):
        if entry == ".git":
            continue  # nothing under test reads it, and it is the bulk of the tree
        subprocess.run(["cp", "-al", os.path.join(REPO, entry), os.path.join(root, entry)],
                       check=True, capture_output=True)
    _WORKSPACE = root
    atexit.register(shutil.rmtree, root, True)
    return root


def _mirror(path, workspace):
    """The clone's copy of a repo path."""
    return os.path.join(workspace, os.path.relpath(path, REPO))


def _write_without_following_the_link(path, text):
    """⛔ `open(path, "w")` TRUNCATES THE SHARED INODE and reaches the original. Replace, never write."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    with io.open(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def guards_reading(document_basename):
    """Every guard that OPENS this document, whether or not the census could credit it.

    ⛔⛔ THE CENSUS CAN ONLY CREDIT A GUARD WHOSE LOGIC IS A HARVESTED STRING LITERAL, AND THE BEST
    GUARDS IN THIS SUITE ARE NOT (2026-08-22). `claim_coverage._test_patterns` scrapes regex-shaped
    literals out of test source; a guard that COMPUTES — the gene-identifier attestation set, the
    polarity table's span/require/forbid rows, seat 1's artifact bindings — exposes no such literal
    and is therefore invisible to it. Ablating only the census's `read_by` then reports those
    sentences BLIND when the paper is in fact well guarded: a false negative manufactured by the
    proxy rather than by the guards.
    ★ THE QUESTION THE GATE IS ACTUALLY ASKING IS "would anything notice?", so it runs everything
    that opens the file. The census stays a cheap SCREEN; this is the ASSAY.
    """
    out = []
    for name in sorted(os.listdir(cc.TESTS)):
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        try:
            if document_basename in io.open(os.path.join(cc.TESTS, name), encoding="utf-8").read():
                out.append(f"test:{name}")
        except OSError:
            continue

    # ⛔⛔ THE PINS ARE THE PRIMARY BINDING MECHANISM AND THE FIRST VERSION OF THIS FUNCTION DROPPED
    # THEM (2026-08-22). Scanning only `tests/` fixed the computed-guard blind spot and opened a new
    # one in the same edit: `lint_consistency.py` is what enforces every `must_appear_in` pin, and it
    # lives outside `tests/`, so three pins added to the cover letter minutes earlier changed nothing
    # and the sentence still read BLIND. ⚠ A fix that swaps one blind spot for another looks like
    # progress in the report and is not.
    out.append("pin:*")
    for key, path in cc.PAPERS.items():
        if os.path.basename(path) == document_basename:
            gen = cc._generator(path)
            if gen:
                out.append(f"generator:{gen}")
    return out


def _witness_cmds(witnesses, workspace):
    """One command per TOOL, not per witness — every pytest module in a single invocation.

    A sentence can carry a dozen witnesses; starting a dozen interpreters to ask one question is the
    difference between a gate that runs per commit and one that gets disabled.
    """
    manuscripts = _mirror(HERE, workspace)
    modules = [os.path.join(manuscripts, "tests", w[len("test:"):])
               for w in witnesses if w.startswith("test:")]
    cmds = []
    if modules:
        cmds.append([sys.executable, "-m", "pytest", *modules,
                     "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:randomly"])
    if any(w.startswith("pin:") for w in witnesses):
        cmds.append([sys.executable, os.path.join(manuscripts, "lint_consistency.py")])
    for w in witnesses:
        if w.startswith("generator:"):
            cmds.append([sys.executable, os.path.join(workspace, w[len("generator:"):]), "--check"])
    return cmds


def _run(cmd, workspace):
    return subprocess.run(cmd, cwd=workspace, capture_output=True, text=True).returncode != 0


#: ⛔⛔ A QUANTITY WRITTEN IN WORDS WAS UNFALSIFIABLE BY CONSTRUCTION UNTIL 2026-09-01 (AUT-PD-148,
#: filed 2026-08-28 by CYC-0070 while READING a BLIND verdict rather than trusting it). `ablate`
#: perturbed digit runs and nothing else, so a sentence stating "two of five variant cases … eight of
#: the junctions" reached the caller as `not-applied — the sentence states no number`. Measured on
#: this tree before the fix: **157 covered sentences across the censused documents carry a number
#: word, and 29 of them contain NO digit at all**, so the harness answered "there is nothing here to
#: perturb" about sentences stating three quantities each. The gate above them was blind twice over —
#: `_sample` in `test_the_census_word_covered_survives_ablation.py` also required a digit, so those
#: 29 were never even offered.
#: ★ ROUND 15 ALREADY FOUND THIS ONE LEVEL UP AND IT IS RECORDED IN `claim_coverage`'s OWN DOCSTRING:
#: *"'ten' is a WORD, so no numeric instrument read it"*. The census was widened; the harness that
#: falsifies the census was not.
#:
#: ⚠ WHAT THE REPLACEMENT TABLE IS FOR, AND WHY IT PREFERS THE SAME LENGTH. The perturbation must
#: change the QUANTITY and as little else as possible: a swap that also changes the character count
#: can redden a page-budget, justification or word-count guard, and a red from THAT is a false RED —
#: the sentence would be reported bound while its quantity stayed unwatched. Same-length swaps
#: ("three" -> "seven", "one" -> "two") remove that channel wherever English allows it. Where it does
#: not (`hundred` -> `thousand`), the swap is still the honest one and the residue is stated below.
#: ⛔ THE RESIDUE, STATED RATHER THAN GLOSSED — what this perturbation CANNOT reach:
#:   · a quantity carried by a word this table does not list (`several`, `most`, `a majority`,
#:     `dozens`, `an order of magnitude`) — those are not numbers and no single-site swap makes them
#:     falsifiable;
#:   · a compound written across words (`twenty-seven`, `two hundred`) is perturbed at ONE of its
#:     parts, which is a real change of the quantity but not the change a reader would make;
#:   · `one` and `second` also occur as a pronoun and as a unit of time. Both are perturbed. A guard
#:     reddening on "one might expect" -> "two might expect" is answering this module's actual
#:     question — *would anything notice if this text changed* — and the docstring is explicit that
#:     that is NOT the same question as *is this sentence's own claim watched*. The gap is reported,
#:     never hidden: `quantity_kind` below lets a caller count word-only sentences separately.
_NUMBER_WORD_SWAP = {
    # cardinals
    "zero": "four", "one": "two", "two": "six", "three": "seven", "four": "nine",
    "five": "nine", "six": "ten", "seven": "three", "eight": "seven", "nine": "four",
    "ten": "six", "eleven": "twelve", "twelve": "eleven", "thirteen": "fourteen",
    "fourteen": "thirteen", "fifteen": "sixteen", "sixteen": "fifteen",
    "seventeen": "nineteen", "eighteen": "fourteen", "nineteen": "eighteen",
    "twenty": "thirty", "thirty": "twenty", "forty": "fifty", "fifty": "forty",
    "sixty": "forty", "seventy": "sixty", "eighty": "sixty", "ninety": "eighty",
    "hundred": "thousand", "thousand": "hundred",
    # ordinals
    "first": "third", "second": "fourth", "third": "fifth", "fourth": "eighth",
    "fifth": "sixth", "sixth": "ninth", "seventh": "fourth", "eighth": "fourth",
    "ninth": "sixth", "tenth": "sixth",
    # multiplicatives and the two fractions that carry counts in these papers
    #: ⛔ THE MULTIPLICATIVE SET IS CLOSED UNDER ITS OWN SWAPS. A target that is not itself a key
    #: is a word this module can produce and cannot perturb, so a paper that already said
    #: "sevenfold" would have been unfalsifiable at exactly the site the swap invented.
    "twofold": "tenfold", "threefold": "sevenfold", "fourfold": "fivefold",
    "fivefold": "ninefold", "sixfold": "ninefold", "sevenfold": "threefold",
    "eightfold": "threefold", "ninefold": "fivefold", "tenfold": "twofold",
    "half": "third", "quarter": "third",
}

#: ⚠ THE SORT IS DEFENSIVE, NOT LOAD-BEARING, AND THAT IS A CORRECTION A MUTATION MADE (2026-09-01).
#: This comment first claimed longest-alternative-first was what stops `seventeen` being matched as
#: `seven` with a stray `teen` left behind. Reversing the sort in a scratch copy left all 16 tests
#: GREEN: the `\b` on BOTH sides is what does the work, because `seven` inside `seventeen` fails the
#: trailing word boundary. Python's `|` is indeed first-match rather than longest-match, so the sort
#: is kept as protection against a future entry the anchors cannot separate — but the property the
#: tests actually hold is the ANCHORING, and saying otherwise would have credited the wrong line.
_NUMBER_WORD = re.compile(
    r"\b(?:%s)\b" % "|".join(sorted(_NUMBER_WORD_SWAP, key=len, reverse=True)), re.I)

#: What kind of quantity a sentence states, so a caller can COUNT the word-only ones rather than
#: folding them into a single verdict. AUT-PD-148 asked for this before it asked for the mutation:
#: "a status the reader can count is worth more than a mutation that might rewrite prose into
#: nonsense". Both are here; this is the half that costs nothing and can never lie.
DIGITS, WORDS, BOTH, NONE = "digits", "words", "both", "none"


def _match_case(original, replacement):
    """`Three` -> `Seven`, `THREE` -> `SEVEN`, `three` -> `seven`. Nothing else is preserved."""
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def perturbations(span, skip):
    """Every single-site change this module knows how to make to `span`, digits before words.

    Each entry is `(start, end, before, after)` with offsets into `span`.

    ⛔ DIGITS COME FIRST AND THAT ORDER IS LOAD-BEARING, not cosmetic. `ablate` stops at the first
    perturbation that trips a guard, so putting digits first leaves every verdict this harness
    reached before 2026-09-01 exactly where it was: a sentence that was red on a digit is still red
    on the same digit, with the same `reason` string. The word swaps can only ever convert a BLIND or
    a NOT_APPLIED into a red, which is the direction that removes a false negative.
    ⛔ AND NOTHING INSIDE A STRIPPED SPAN IS EVER PERTURBED (`skip`), for either kind — a number word
    inside a dropped heading or a fenced block is not part of the flattened claim.
    """
    # Author identifiers can share a census span with an abstract quantity.
    # Their digits are not quantities; retain every actual numerical site.
    skip = list(skip) + orcid_spans(span)
    out = []
    for m in re.finditer(r"\d+", span):
        if any(s <= m.start() < e for s, e in skip):
            continue
        run = m.group(0)
        out.append((m.start(), m.end(), run, run[:-1] + ("7" if run[-1] != "7" else "4")))
    for m in _NUMBER_WORD.finditer(span):
        if any(s <= m.start() < e for s, e in skip):
            continue
        word = m.group(0)
        out.append((m.start(), m.end(), word,
                    _match_case(word, _NUMBER_WORD_SWAP[word.lower()])))
    return out


def states_a_quantity(sentence):
    """Does this censused sentence state a quantity at all — in digits OR in number words?

    ⛔ THE POPULATION PREDICATE FOR THE GATE ABOVE THIS MODULE, AND IT LIVES HERE SO THERE IS ONE
    COPY. Before AUT-PD-148 the rule existed twice — `re.finditer(r"\\d+")` here and
    `re.search(r"\\d", …)` in `_sample` — and BOTH had to be widened for a word quantity to become
    testable. A sentence the gate never offers is as unfalsifiable as one the harness cannot
    perturb, and the second copy is the one that gets forgotten.
    ⚠ Takes the FLATTENED census sentence, which by construction contains only text that survived
    `_prose`, so there is no stripped span to exclude here.
    """
    return bool(perturbations(sentence, []))


def quantity_kind(span, skip):
    """`digits` | `words` | `both` | `none` — what the perturbable part of this span states.

    ⚠ A COUNT, NOT A VERDICT. It says what a reader would have to check, not whether anything checks
    it. `words` is the population AUT-PD-148 is about; before the fix every one of them scored
    `not-applied` and was invisible in the gate's own accounting.
    """
    kinds = {"digits" if before[:1].isdigit() else "words" for _s, _e, before, _a
             in perturbations(span, skip)}
    if kinds == {"digits"}:
        return DIGITS
    if kinds == {"words"}:
        return WORDS
    return BOTH if kinds else NONE


#: Witness-set signature -> (commands, indices already red BEFORE any mutation). Once per set.
_BASELINE_CACHE = {}


def _is_pytest_batch(cmd):
    return "pytest" in cmd and sum(1 for a in cmd if a.endswith(".py")) > 1


def _split_pytest(cmd):
    """One command per test module, preserving the flags."""
    modules = [a for a in cmd if a.endswith(".py")]
    flags = [a for a in cmd if not a.endswith(".py")]
    return [flags + [m] for m in modules]


def _baseline_reds(witnesses, workspace):
    """The commands to run and which are ALREADY red on the unmutated clone.

    ⛔⛔ WITHOUT A BASELINE THE WHOLE GATE PASSES VACUOUSLY ON ANY RED TREE (round 17 seat B,
    2026-08-23). `ablate` declared a sentence bound when a witness went red AFTER the mutation, and
    never asked whether it was red BEFORE. Measured: one unrelated wrong integer in
    `claim-coverage.json` turns 1 of 2 witness commands red on the UNMUTATED clone, after which
    every sentence in the document reports "a witness noticed" and
    `test_a_covered_sentence_has_a_witness_that_actually_goes_red` passes without measuring
    anything.
    ★ That is the exact defect this module was built to detect — a reading taken without
    establishing its own precondition — committed inside the instrument that detects it. A red
    baseline is subtracted, and a baseline with NOTHING green is reported as unmeasurable rather
    than as a pass.

    ⛔⛔ AND SUBTRACTING THE BATCH SUBTRACTED THIRTEEN INNOCENT GUARDS WITH IT (measured 2026-08-23,
    the same day, one layer down). `_witness_cmds` packs every pytest witness into ONE invocation
    for speed, so "the command is already red" and "this witness is already red" stopped being the
    same statement. With `claim-coverage.json` stale, `test_the_paper_states_what_its_own_claims_
    depend_on.py` failed, the single batched command was red at baseline, and the subtraction
    excluded ALL FOURTEEN modules from ever firing. The gate then reported three sentences BLIND —
    including `NR4A3` -> `NR4A7`, which
    `test_the_manuscripts_gene_identifiers_are_ones_an_artifact_names.py` exists specifically to
    catch and was sitting inside that batch. A blindness verdict manufactured by the harness reads
    exactly like a real one, and it points the reader at the paper instead of at the instrument.
    ★ THE UNIT OF EXCLUSION MUST BE THE FAILING WITNESS, NEVER THE BATCH THAT CONTAINS IT. A red
    batch is therefore decomposed into one command per module and re-measured, so only the module
    that is actually red is subtracted. The cost is paid ONLY when something is already red, which
    is the case that was silently wrong; a green tree still runs one invocation.
    """
    key = (workspace, tuple(sorted(witnesses)))
    if key in _BASELINE_CACHE:
        return _BASELINE_CACHE[key]
    cmds, final, red = _witness_cmds(witnesses, workspace), [], []
    for cmd in cmds:
        if not _run(cmd, workspace):
            final.append(cmd)
            continue
        for sub in (_split_pytest(cmd) if _is_pytest_batch(cmd) else [cmd]):
            final.append(sub)
            if _run(sub, workspace):
                red.append(len(final) - 1)
    _BASELINE_CACHE[key] = (final, red)
    return _BASELINE_CACHE[key]


def _mutation_is_detected(commands, already_red, workspace):
    """Ask whether any baseline-green witness detects this mutation.

    Run the inexpensive standalone tools before pytest and stop once the answer
    is known. Pytest stops after its first failure only for this mutation probe.
    The unmutated baseline and the enclosing scientific suite still run every
    test; a blind mutation still runs every eligible witness. No verdict is
    inferred from an unrun witness.
    """
    ordered = sorted(enumerate(commands), key=lambda item: "pytest" in item[1])
    for index, command in ordered:
        if index in already_red:
            continue
        probe = command + ["--maxfail=1"] if "pytest" in command else command
        if _run(probe, workspace):
            return True
    return False


def subtraction_note(commands, already_red):
    """The clause a BLIND verdict carries when part of its witness set could not run.

    ⛔ A PURE FUNCTION SO IT CAN BE TESTED WITHOUT AN ABLATION. The clause is the only place a
    reader learns that "no guard noticed" was computed from a fraction of the guards, and a message
    nothing asserts is a message that quietly disappears in the next edit.
    """
    if not already_red:
        return ""
    return (f" \u26a0 {already_red} of {commands} guard command(s) were ALREADY red on the unmutated "
            f"clone and were subtracted, so this verdict rests on {commands - already_red} of them")


def ablate(paper_key, row, witnesses=None):
    """Perturb the sentence IN A CLONE, run its guards there, and report whether anything noticed.

    Returns `{"status", "red", "witnesses", "reason"}`. A caller reading `red` without first checking
    `status == APPLIED` is reading absence as evidence.

    ⛔⛔ EVERY DIGIT RUN IS TRIED, NOT JUST THE FIRST (2026-08-22). Perturbing only the first one
    manufactured false BLIND verdicts wherever a sentence opens with an incidental number — a
    `5-6-5` gapmer motif, a "Table 1" cross-reference, a figure number. Those are not the claim, so
    nothing SHOULD go red for them, and scoring the sentence unwatched on that basis is the same
    "absent reading read as a reading of absence" this module was written to stop.
    ★ A sentence is bound if ANY perturbation of it trips a guard, which is what "would anything
    notice if this changed?" actually means. The first trip wins and the rest are not run.

    ⛔⛔ AND SINCE 2026-09-01 A QUANTITY WRITTEN IN WORDS IS A PERTURBATION TOO (AUT-PD-148). Every
    result carries `quantity_kind` — `digits`, `words`, `both` or `none` — so a caller can count the
    word-only sentences instead of reading their old `not-applied` as "there is nothing here".
    """
    path = cc.PAPERS[paper_key]
    original = io.open(path, encoding="utf-8").read()
    ws = list(witnesses) if witnesses is not None else guards_reading(os.path.basename(path))

    # ⛔⛔ THE CACHE, AND WHY THE EXPENSIVE PART IS THE PART WORTH SKIPPING. Measured 2026-09-02:
    # this function's real work — a guard's assertions — is 0.037 s, one pytest subprocess to run
    # them is 0.43 s, and one ablation with its clone and every witness is 17.4 s. Over the 184 covered
    # sentences of the floored documents that is 53 minutes, and it was paid on every publication run whether or not anything
    # had moved. The night that produced this edited three sentences and re-verified all of them.
    # ★ A HIT IS RETURNED ONLY WHEN THE SENTENCE, THE WITNESS SET AND EVERY WITNESS'S SOURCE ARE
    # BYTE-IDENTICAL to when the verdict was recorded — the three things this function's answer is a
    # function of. Everything else is a miss and re-runs. See `claim_ablation_cache` for why the
    # artifact corpus is deliberately not in the key, and for the eleven ways it fails closed.
    # ⛔ IT CANNOT LAUNDER A RED INTO A GREEN: a hit returns the recorded verdict either way, and
    # `status` is recorded with it, so a NOT_APPLIED stays not-applied rather than reading as bound.
    _key = _cache.key_for(paper_key, row["sentence"], ws)
    _entries = _cache.load()
    _hit = _cache.lookup(_entries, _key)
    if _hit is not None and _hit.get("status") in (APPLIED, NOT_APPLIED):
        out = {"status": _hit["status"], "red": ws if _hit["red"] else [], "witnesses": ws,
               "quantity_kind": _hit.get("quantity_kind", NONE),
               "reason": _hit.get("reason", ""), "cached": True}
        # ⛔ AND THE BASELINE COMES BACK WITH IT WHERE THE ENTRY HAS ONE. A BLIND verdict is only
        # readable beside how many of its witnesses could actually run; dropping that on the way
        # through a cache would recreate the false-BLIND `_baseline_reds` exists to prevent.
        if _hit.get("baseline") is not None:
            out["baseline"] = _hit["baseline"]
        return out

    hit = _locate(original, row["sentence"])
    if hit is None:
        return {"status": NOT_APPLIED, "red": [], "witnesses": ws, "quantity_kind": NONE,
                "reason": "the censused sentence has no home in the raw file even allowing for line "
                          "wrapping — the flattener and the file have diverged"}
    span = original[hit.start():hit.end()]
    # ⛔⛔ ONLY THE DIGITS THAT SURVIVE FLATTENING (AUT-PD-132, 2026-08-28). The span may now cross a
    # citation marker or a dropped heading, and perturbing a `<sup>16</sup>` would turn a citation
    # guard red and report the SENTENCE bound while its own number stayed unwatched — a false RED,
    # which is the direction that lies in the reassuring direction. See `claim_coverage.stripped_spans`.
    _skip = cc.stripped_spans(span)
    sites = perturbations(span, _skip)
    kind = quantity_kind(span, _skip)
    if not sites:
        return {"status": NOT_APPLIED, "red": [], "witnesses": ws, "quantity_kind": kind,
                "reason": "the sentence states no quantity, in digits or in number words, so this "
                          "module defines no perturbation"}

    workspace = _workspace()
    mirror = _mirror(path, workspace)
    before = hashlib.sha256(original.encode()).hexdigest()

    # ⛔ ESTABLISH THE BASELINE BEFORE TRUSTING A RED. A guard already failing for an unrelated
    # reason reds on every mutation and on none of them equally.
    # ⚠ `cmds and` IS LOAD-BEARING: an EMPTY witness set has zero commands, and `0 == 0` would read
    # as "everything is already red". The byte-identity test passes `witnesses=[]` deliberately —
    # it is measuring the file, not the guards — and caught this the moment it was introduced.
    cmds, already_red = _baseline_reds(ws, workspace)
    if cmds and len(already_red) == len(cmds):
        return {"status": NOT_APPLIED, "red": [], "witnesses": ws, "quantity_kind": kind,
                "reason": f"all {len(cmds)} guard(s) reading this document are ALREADY red on the "
                          "unmutated tree, so nothing here can be measured. Fix the tree first — a "
                          "red baseline makes every sentence look bound."}
    # ⛔⛔ A BLIND VERDICT MUST STATE HOW MUCH OF ITS WITNESS SET COULD ACTUALLY RUN, AND UNTIL
    # 2026-09-01 IT DID NOT (measured this session, and it nearly cost a false finding). The bailout
    # above fires only when EVERY command is red at baseline; at 25 red of 26 it does not fire, and
    # the module returns a full APPLIED/BLIND verdict computed from the one surviving command — a
    # sentence "no guard noticed" when twenty-five of its guards were never in a position to notice.
    # ⚠ MEASURED, NOT HYPOTHETICAL: `_witness_cmds` runs `sys.executable -m pytest`, so a driver
    # interpreter without pytest reddens every pytest witness at baseline. Running this harness under
    # the sandbox's `/usr/local/bin/python3` gave `26 commands, 25 already red` and reported the
    # journal article's FUS sentence BLIND. Re-run under the interpreter that HAS pytest: 1 red
    # (a stale census artifact), and the same sentence goes RED on `two -> six`.
    # ★ The number is now carried in every result and printed in the blind reason, so the reader of a
    # BLIND cannot mistake "the guards could not run" for "the guards did not care" — the same
    # false-BLIND direction `_baseline_reds` was written for, one level up.
    baseline = {"commands": len(cmds), "already_red": len(already_red)}
    subtracted = subtraction_note(len(cmds), len(already_red))
    tried = []
    try:
        for start, end, was, now in sites:
            tried.append(f"{was}->{now}")
            _write_without_following_the_link(
                mirror,
                original[:hit.start() + start] + now + original[hit.start() + end:])
            if _mutation_is_detected(cmds, already_red, workspace):
                _cache.record(_entries, _key, True, f"{was} -> {now}", ws,
                              status=APPLIED, quantity_kind=kind, baseline=baseline)
                _cache.save(_entries)
                return {"status": APPLIED, "red": ws, "witnesses": ws, "quantity_kind": kind,
                        "baseline": baseline, "reason": f"{was} -> {now}"}
    finally:
        _write_without_following_the_link(mirror, original)
        after = hashlib.sha256(io.open(path, encoding="utf-8").read().encode()).hexdigest()
        if after != before:
            raise SystemExit(
                f"FATAL: the REAL {os.path.basename(path)} changed during an ablation "
                f"({before[:12]} -> {after[:12]}). Recover it from git before doing anything else.")
    _cache.record(_entries, _key, False,
                  "no guard reading this file noticed any of: " + ", ".join(tried) + subtracted,
                  ws, status=APPLIED, quantity_kind=kind, baseline=baseline)
    _cache.save(_entries)
    return {"status": APPLIED, "red": [], "witnesses": ws, "quantity_kind": kind,
            "baseline": baseline,
            "reason": "no guard reading this file noticed any of: " + ", ".join(tried) + subtracted}
