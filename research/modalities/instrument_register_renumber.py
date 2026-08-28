#!/usr/bin/env python3
"""GIVE THE INSTRUMENT REGISTER A NON-COLLIDING ID PREFIX: `C01`..`C16` -> `IC01`..`IC16`. ($0, stdlib)

⛔ WHY (roadmap §10.1a `Q22`, §0.6). Two independent registers in this program are written `C`-and-a-number:

    C1 .. C25    a CONFIGURATION ITEM on the roadmap -- a frozen definitional choice a number is
                 conditional on (roadmap §3b). UNPADDED.
    C01 .. C16   an INSTRUMENT-REGISTER CANDIDATE (research/modalities/instrument-options.json). PADDED.

§0.6 registered the zero padding as the tell -- and then recorded that **the tell runs out at ten**: the
instrument register reaches `C16` and the configuration register reaches `C25`, so `C10` `C11` `C12` `C13`
`C14` `C15` `C16` are spelled IDENTICALLY in both and no padding distinguishes them.

⛔ `C14` IS THE DANGEROUS ONE, AND IT IS WHY THIS IS NOT COSMETIC. As a configuration item it is the
**pose-recovery criterion** that decides `panel_readable` and adjudicates all four SI §S1 anti-target
clauses; as an instrument-register id it is a **priced GPU benchmark**. A sentence reading *"C14 refuses
it"* is ambiguous between a criterion and a purchase.

§0.6's mitigation was a WRITING RULE (*above `C09`, write an instrument id in words*). A rule that depends
on every future author remembering it manages the hazard; a prefix removes it. This does the removal.

★ WHAT MAKES THIS SAFE, BECAUSE A BLANKET `sed` WOULD BE A DISASTER HERE. `C10`..`C16` also occur ~9,600
times under `results/` as ATOM NAMES in MM-GBSA system caches, and far more often as configuration items
than as register ids in the research documents. So every occurrence is CLASSIFIED before anything is
rewritten, by a rule that is stated, auditable and deliberately conservative:

    PADDED  `C01`..`C09`   -> REGISTER, always. §0.6: "a configuration id is `C` + an UNPADDED number and
                              nothing else", so a padded id cannot be a configuration item.
    `C10`..`C16`           -> REGISTER **only** inside `REGISTER_FILES` (the register's own two files,
                              whose JSON says in its own words "IDs ARE THIS FILE'S NAMESPACE ONLY",
                              plus any file listed there on evidence -- see the constant's comment),
                              or where the occurrence is preceded by an explicit instrument-candidate
                              marker within `MARKER_WINDOW` characters.
                           -> CONFIGURATION otherwise, and left alone. ⛔ THIS IS THE CONSERVATIVE
                              DIRECTION ON PURPOSE: a missed rename leaves a citation that still reads
                              correctly under the §0.6 writing rule, while a wrong rename silently
                              re-points a criterion at a GPU purchase.

⚠ THE ROADMAP IS NOT REWRITTEN BY THIS SCRIPT. `nr4a3-program-map.md` is edited only through routed
`map_edits_required` blocks; `--emit-map-edits` writes one, anchor-verified with
`map_edit_anchors.verify()`, and `--apply` skips the file.

Usage:
    python3 research/modalities/instrument_register_renumber.py --audit
    python3 research/modalities/instrument_register_renumber.py --apply
    python3 research/modalities/instrument_register_renumber.py --emit-map-edits
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

OLD_PREFIX, NEW_PREFIX = "C", "IC-"
N_IDS = 16
#: ⭐ THE TARGET SPELLING IS NOT INVENTED HERE. `systems/CONVENTIONS.md` §1 already REGISTERS it --
#: "| `C01`…`C16` (zero-padded) | **`IC-1`…`IC-16`** | an instrument-options candidate |" -- and
#: `systems/schema/research-object.schema.json` repeats it in its namespace description. That is exactly
#: what §10.1a `Q22` records: *the disambiguation rule is registered, the renumbering is not*. This script
#: performs the renumbering the convention already mandates; it does not choose a prefix.
#: ⚠ THE NUMBER IS UNPADDED AFTER `IC-`. `IC-4`, never `IC-04` -- the padding was the failed tell and
#: carrying it into the new scheme would preserve the thing being removed.
MAP = {"C%02d" % i: "IC-%d" % i for i in range(1, N_IDS + 1)}

ROADMAP = "research/manuscripts/nr4a3-program-map.md"
MAP_EDITS_OUT = os.path.join(ROOT, "research", "manuscripts", "program", "instrument-register-prefix-map-edits.json")

#: The register's own files. Every `C\d\d` in these is a register id -- the JSON says so itself:
#: "IDs ARE THIS FILE'S NAMESPACE ONLY. `C01`..`C16` are CANDIDATE instruments."
REGISTER_FILES = (
    "research/modalities/instrument-options.json",
    "research/modalities/instrument-options.md",
    # ⭐ ADDED 2026-08-08, ON EVIDENCE RATHER THAN ON READING. This workflow runs three instruments and
    # cites them by bare id, but it carries none of the MARKERS within MARKER_WINDOW, so the ambiguous
    # band fell to CONFIGURATION and `C10`/`C12` were left behind while `C03` renamed around them —
    # leaving a file whose own title read "IC-3 + C12".
    # ⛔ THAT IS WORSE THAN AN UNMIGRATED FILE, AND IT IS WHY THE CONSERVATIVE DEFAULT NEEDED AN
    # EXCEPTION HERE. The conservative direction is justified by §0.6's writing rule — a missed rename
    # "leaves a citation that still reads correctly". That justification EXPIRED the moment the register
    # itself finished migrating: `instrument-options.json` now holds `IC-1`..`IC-16` and ZERO `C0x`, so a
    # bare `C12` no longer resolves to anything at all. A dangling citation is not a citation that reads
    # correctly.
    # The evidence that these are register ids, not configuration items, is that the register's own
    # descriptions match the workflow's steps verbatim: IC-10 is "Symmetric reciprocal-uniqueness + indel
    # census across all residue classes" and the step is named exactly that; IC-12 is "Thiol pKa /
    # intrinsic nucleophilicity for C397" and the step is the measured-pKa precheck for that thiol.
    # ⚠ `C397` is untouched by construction — it is a residue, and ANY_ID is bounded to a two-digit id.
    ".github/workflows/covalent-axis-prechecks.yml",
)

#: An explicit instrument-candidate marker in the preceding text promotes an occurrence to REGISTER.
#: These are the forms §0.6's writing rule mandates, so text that OBEYED the rule is machine-resolvable.
MARKERS = ("instrument candidate", "Instrument candidate", "instrument-register", "instrument register",
           "instrument-options", "candidate instrument")
MARKER_WINDOW = 120

#: ⛔⛔ FILES THAT DOCUMENT THE MIGRATION AND MUST KEEP THE OLD SPELLINGS THEY QUOTE AS EVIDENCE.
#: `CONVENTIONS.md` carries the `| C01…C16 | IC-1…IC-16 |` mapping row itself, and the schema's namespace
#: description says "an instrument-options candidate is IC-4 and never C04 (which collided outright with
#: C10-C16)". Rewriting those turns the record of the rename into a sentence that renames nothing. This is
#: the same exemption `lint_optional_input_guards` needs for incident write-ups that quote broken forms.
NEVER_REWRITE = (
    "systems/CONVENTIONS.md",
    "systems/MIGRATION.md",
    "systems/schema/research-object.schema.json",
    "research/modalities/instrument_register_renumber.py",
    "research/modalities/tests/test_instrument_register_prefix.py",
    "research/manuscripts/program/instrument-register-prefix-map-edits.json",
)

#: ⛔⛔ A `map_edits_required` BLOCK IS A VERBATIM QUOTATION OF THE ROADMAP, AND THE ROADMAP IS THE ONE
#: FILE THIS SCRIPT REFUSES TO REWRITE. Its `current_text` is required by contract to be a byte-exact
#: substring of the live map, and `map_edit_anchors.verify()` fails when it is not — so renaming an id
#: inside a quotation does not update a reference, it BREAKS THE ANCHOR, and the routed edit can never
#: be applied again.
#: ⚠ Measured 2026-08-08, after `--apply` did exactly this. Restored from git, and the damage is the
#: argument for the rule: in `q-queue-2026-08-07-map-edits.json` the run rewrote the sentence
#: *"PDB atom names are spelled exactly `C01`, `C02`, `C07`"* into *"`IC-1`, `IC-2`, `IC-7`"* — a
#: statement that is now simply false, since a PDB atom name IS `C01` — and turned §0.6's own writing
#: rule *"above `C09`, write an instrument id in words"* into *"above `IC-9`"*, which renames the rule
#: that exists because the rename had not happened. Those lines ARE the evidence for the migration,
#: which is precisely the category `NEVER_REWRITE` already protects; they were missed only because the
#: list is exact paths and these files are generated under many names.
#: ⭐ SO THE RULE IS BY SHAPE, NOT BY PATH: anything whose job is to quote the map is quoted, not
#: rewritten. When the roadmap's own routed rename lands, these files' quotations move with it, in that
#: same commit, because that is when what they quote actually changes.
QUOTATION_MARKERS = ("map-edits", "map_edits")


def _is_a_quotation_of_the_roadmap(path: str, text: str = "") -> bool:
    base = os.path.basename(path)
    if any(m in base for m in QUOTATION_MARKERS):
        return True
    # ⭐ BY CONTENT, NOT ONLY BY NAME. `sufex-second-handle.json` carries a `map_edits_required` block
    # and is named nothing like a map-edits file, so a filename rule alone would have left exactly the
    # artifact whose anchors broke. Any file that CARRIES the block is quoting the map.
    if "map_edits_required" in text:
        return True
    # A generator that hardcodes a map anchor is quoting just as much as the JSON it emits.
    return path in QUOTATION_GENERATORS


#: Modules that hold a roadmap anchor as a literal. Kept explicit rather than sniffed: a module is only
#: listed here once its anchors have been read and confirmed to be quotations.
QUOTATION_GENERATORS = (
    "research/modalities/sufex_second_handle.py",
)

PADDED = re.compile(r"\bC0[1-9]\b")
AMBIGUOUS = re.compile(r"\bC1[0-6]\b")
ANY_ID = re.compile(r"\bC(?:0[1-9]|1[0-6])\b")

TEXT_EXT = (".md", ".json", ".py", ".yml", ".yaml", ".mjs", ".sh")
#: `results/` is archived SageMaker output -- atom names, not ids. Never rewritten, never audited.
SKIP_PREFIXES = ("results/", ".claude/")


def tracked_files():
    """⛔ AUT-PD-036, 2026-08-28. A bare `git ls-files` misses a brand-new, not-yet-committed
    document, so `test_the_migration_is_idempotent_over_the_repo` could pass over a fresh draft that
    reintroduces the exact `C10`-`C16` ambiguity this migration exists to remove, and only catch it
    the run AFTER it was committed. `--cached --others --exclude-standard` (the convention proven in
    `research/autonomy/tests/test_the_clause_count_is_never_typed.py`) adds untracked-but-not-
    ignored files so the convergence check sees a draft before it is committed, not after.
    """
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"],
                        capture_output=True, text=True).stdout.split("\n")
    for f in out:
        f = f.strip()
        if not f or f.startswith(SKIP_PREFIXES) or not f.endswith(TEXT_EXT):
            continue
        yield f


ATOM_CONTEXT = ("\"elem\"", "\"xyz\"", "atom_name", "\"element\"")
ATOM_WINDOW = 220
#: ⚠ AND A COORDINATE RECORD IS NOT ALWAYS JSON. `nr4a3-e3-arm-registry-lane1.json` carries staging LOG
#: LINES -- "ligand F4E n_heavy=12 exit atom C07 exposure 3.98 A" -- with no `elem`/`xyz` key anywhere
#: near, so the structural window above misses them. Caught by --audit, not by reasoning.
ATOM_PHRASES = ("exit atom ", "atom name ", "atom_name", "exit_atom")
ATOM_PHRASE_WINDOW = 24


def _looks_like_atom_name(text, match):
    """⛔ THE ONE FALSE POSITIVE A PADDED ID CAN HAVE, AND IT IS A COORDINATE RECORD.

    PDB atom names are spelled exactly `C01`, `C02`, `C07`. `nr4a3-e3-arm-registry-lane1.json` holds
    eight as `{"name": "C01", "elem": "C", "xyz": [...]}` and `transfer-anchor-diagnostic.json` carries
    `"exit_atom_name": "C07"`. The FIRST version of this classifier said "PADDED => REGISTER, always" on
    §0.6's own authority, and would have rewritten those. §0.6 was not wrong -- it was scoped to the
    roadmap's PROSE and read here as a repo-wide fact. This is why `--audit` runs before `--apply`.
    """
    lo = max(0, match.start() - ATOM_WINDOW)
    if any(k in text[lo:match.end() + ATOM_WINDOW] for k in ATOM_CONTEXT):
        return True
    near = text[max(0, match.start() - ATOM_PHRASE_WINDOW):match.start()]
    return any(p in near for p in ATOM_PHRASES)


def classify(path, text, match):
    """REGISTER | CONFIGURATION | QUOTED for one occurrence. PURE given (path, text, match).

    Two different discriminators, because the two halves of the id space are not equally ambiguous:

      `C01`..`C09`  PADDED, and §0.6 is right that a configuration id is never padded. So these are
                    REGISTER unless they sit in a coordinate record (see `_looks_like_atom_name`).

      `C10`..`C16`  ⛔ GENUINELY AMBIGUOUS, AND BACKTICKS DO NOT HELP. Both registers are backticked in
                    the roadmap -- `C14` the pose-recovery criterion and `C14` the priced GPU benchmark
                    are byte-identical there, which is the entire defect `Q22` names. So the ONLY thing
                    that promotes one is an explicit instrument-candidate marker in the preceding text,
                    which is the form §0.6's writing rule already mandates. Everything else stays a
                    configuration item and is left alone.

    ⛔ CONSERVATIVE IN THE RIGHT DIRECTION. A missed rename leaves a citation that still reads correctly
    under §0.6's writing rule; a wrong rename silently re-points a criterion at a GPU purchase, or
    corrupts an atom record.
    """
    if path in NEVER_REWRITE or _is_a_quotation_of_the_roadmap(path, text):
        return "QUOTED"
    if path in REGISTER_FILES:
        return "REGISTER"
    tok = match.group(0)
    before = text[max(0, match.start() - MARKER_WINDOW):match.start()]
    marked = any(m in before for m in MARKERS)
    if PADDED.fullmatch(tok):
        if _looks_like_atom_name(text, match) and not marked:
            return "CONFIGURATION"
        return "REGISTER"
    return "REGISTER" if marked else "CONFIGURATION"


def rewrite(path, text):
    """The file's text with every REGISTER occurrence renamed, plus the count. PURE."""
    out, last, n = [], 0, 0
    for m in ANY_ID.finditer(text):
        if classify(path, text, m) != "REGISTER":
            continue
        out.append(text[last:m.start()])
        out.append(MAP[m.group(0)])
        last = m.end()
        n += 1
    out.append(text[last:])
    return "".join(out), n


def scan():
    rows = []
    for f in tracked_files():
        p = os.path.join(ROOT, f)
        try:
            t = open(p, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        reg = sum(1 for m in ANY_ID.finditer(t) if classify(f, t, m) == "REGISTER")
        cfg = sum(1 for m in ANY_ID.finditer(t) if classify(f, t, m) == "CONFIGURATION")
        if reg or cfg:
            rows.append((f, reg, cfg, t))
    return rows


def audit():
    rows = scan()
    print("%-72s %8s %8s" % ("file", "REGISTER", "CONFIG"))
    treg = tcfg = 0
    for f, reg, cfg, _t in sorted(rows, key=lambda r: -r[1]):
        if reg:
            print("%-72s %8d %8d%s" % (f, reg, cfg, "   <- ROADMAP: routed, not rewritten"
                                       if f == ROADMAP else ""))
        treg += reg
        tcfg += cfg
    print()
    print("REGISTER occurrences to rename: %d   CONFIGURATION occurrences left alone: %d" % (treg, tcfg))
    print("files touched by --apply: %d (the roadmap is excluded and routed instead)"
          % sum(1 for f, reg, _c, _t in rows if reg and f != ROADMAP))
    return 0


def apply(dry=False):
    changed = []
    for f, reg, _cfg, t in scan():
        if not reg or f == ROADMAP:
            continue
        new, n = rewrite(f, t)
        if new != t:
            changed.append((f, n))
            if not dry:
                open(os.path.join(ROOT, f), "w", encoding="utf-8").write(new)
    for f, n in changed:
        print("%-72s %d" % (f, n))
    print("\n%d file(s), %d occurrence(s) renamed %s* -> %s*"
          % (len(changed), sum(n for _f, n in changed), OLD_PREFIX, NEW_PREFIX))
    return 0


#: ⛔⛔ §0.6 IS THE RECORD OF THE COLLISION AND MUST KEEP THE OLD SPELLINGS IT QUOTES. Its table row
#: "| **`C10`** | the pendant reach the gate is read at | the symmetric ... census |" exists precisely to
#: show that `C10` meant two things; renaming the left-hand column would turn the evidence into a sentence
#: that documents nothing. Same for "the instrument register runs to **`C16`**" and "**`C10` `C12` `C14`
#: `C16` are spelled IDENTICALLY in both**". So the emitter SKIPS the section wholesale and the routed
#: block instead carries ONE editorial edit recording that the renumbering happened. That edit is
#: hand-authored on purpose: a migration note is a judgement, not a substitution.
#: ⚠ AND THE COLLISION IS DOCUMENTED OUTSIDE §0.6 TOO -- §3b carries "**`C` collides**: the options
#: registers already use `C01`…`C09` and the covalent artifacts use `C397`-style residue ids". A
#: section-range skip misses it, and the emitter proposed rewriting it on the first pass (caught by
#: reading the emitted block, which is the reason routed edits are read before they are applied). Any line
#: that TALKS ABOUT the collision keeps its spellings, wherever it lives.
QUOTED_LINE_MARKERS = ("collides", "collision", "spelled IDENTICALLY", "zero-padded", "zero padding",
                       "the tell", "padding is the tell", "is ambiguous between")
QUOTED_SECTION_START = "### 0.6 · ⚠ Five different things in this program are called `R`"
QUOTED_SECTION_END = "### 0.7 · "


def _quoted_line_range(lines):
    try:
        a = next(i for i, l in enumerate(lines) if l.startswith(QUOTED_SECTION_START))
    except StopIteration:
        raise SystemExit("instrument_register_renumber: §0.6's heading moved. Relocate "
                         "QUOTED_SECTION_START rather than letting the emitter propose rewriting the "
                         "record of the collision it is fixing.")
    b = next((i for i in range(a + 1, len(lines)) if lines[i].startswith(QUOTED_SECTION_END)), len(lines))
    return a, b


def emit_map_edits():
    """One routed edit per roadmap LINE that carries a register id, anchor-verified.

    ⚠ PER LINE, NOT PER OCCURRENCE. A line carrying four ids would otherwise produce four edits whose
    `current_text` all overlap, and applying the first would kill the other three's anchors -- the exact
    dead-anchor failure `map_edit_anchors` exists to diagnose."""
    sys.path.insert(0, HERE)
    import map_edit_anchors as mea

    path = os.path.join(ROOT, ROADMAP)
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    q_a, q_b = _quoted_line_range(lines)
    edits, skipped = [], 0
    offset = 0
    for i, line in enumerate(lines):
        start = offset
        offset += len(line) + 1
        hits = [m for m in ANY_ID.finditer(text[start:start + len(line)])]
        hits = [m for m in hits
                if classify(ROADMAP, text, re.compile(re.escape(m.group(0))).search(text, start + m.start()))
                == "REGISTER"]
        if not hits:
            continue
        if q_a <= i < q_b or any(k in line for k in QUOTED_LINE_MARKERS):
            skipped += len(hits)
            continue
        new_line = line
        for tok in sorted({m.group(0) for m in hits}, reverse=True):
            new_line = re.sub(r"\b%s\b" % tok, MAP[tok], new_line)
        if new_line == line:
            continue
        e = {
            "id": "IRP-L%d" % (i + 1),
            "section": "line %d" % (i + 1),
            "anchor": line[:80],
            "current_text": line,
            "proposed_text": new_line,
            "why": ("instrument-register prefix migration: the register's ids are renamed `C01`..`C16` -> "
                    "`IC-1`..`IC-16`, the spelling `systems/CONVENTIONS.md` §1 already registers, so they "
                    "can never again be spelled identically to a §3b configuration item (roadmap §0.6 / "
                    "§10.1a `Q22`). Configuration ids on this line are untouched."),
            "artifact": "research/modalities/instrument_register_renumber.py",
        }
        if text.count(line) != 1:
            # ⛔ AMBIGUOUS ANCHOR IS A DEFECT IN THE EDIT, NOT A WARNING. Reported, never applied blind.
            e["⛔"] = "this line is not unique in the file -- lengthen the anchor before applying"
        edits.append(e)

    edits.append({
        "id": "IRP-S06",
        "section": "§0.6 — the collision register",
        "anchor": "**So above `C09`, an instrument-register id must be written in words**",
        "current_text": None,
        "where_it_goes": ("§0.6, at the end of the `C` collision discussion, immediately after the "
                          "writing-rule sentence the anchor names."),
        "proposed_text": ("⛔ EDITORIAL, NOT MECHANICAL — apply by hand. Record that the renumbering is "
                          "DONE: the instrument register now uses `IC-1`..`IC-16` (the spelling "
                          "`systems/CONVENTIONS.md` §1 registers), so `C10`-`C16` no longer exist in two "
                          "schemes and the writing rule above is retained as history rather than as a "
                          "live instruction. ⚠ Every old spelling in THIS SECTION must stay as written — "
                          "it is the record of the collision, and rewriting it would document nothing. "
                          "Migration: `research/modalities/instrument_register_renumber.py`; the "
                          "reintroduction guard is `tests/test_instrument_register_prefix.py`."),
        "why": ("§0.6's mitigation was a writing rule that depends on every future author remembering it. "
                "The prefix removes the hazard, so the section must say so or it will keep instructing "
                "readers to manage a collision that no longer exists."),
        "artifact": "research/modalities/instrument_register_renumber.py",
        "_hand_authored": True,
    })

    verified, summary = mea.verify(edits, path)
    doc = {
        "_what": ("Routed roadmap edits for the instrument-register prefix migration (`C01`..`C16` -> "
                  "`IC-1`..`IC-16`). The roadmap is never rewritten mechanically; these are applied by "
                  "whoever owns that document."),
        "_generated_by": "research/modalities/instrument_register_renumber.py --emit-map-edits",
        "_rule": ("One edit per LINE, not per occurrence -- overlapping `current_text` values would kill "
                  "each other's anchors as the first landed. Configuration ids (`C1`..`C25`, unpadded, and "
                  "any `C10`..`C16` without an instrument-candidate marker) are NOT touched."),
        "_section_0_6_is_excluded": (
            "%d register occurrences are deliberately NOT proposed for renaming: everything inside §0.6, "
            "plus any line anywhere that DOCUMENTS the collision (§3b's \"`C` collides\" bullet). Those "
            "lines ARE the evidence -- §0.6's table shows `C10` meaning two different things -- so "
            "rewriting them would destroy the record of the defect being fixed. One hand-authored "
            "editorial edit (IRP-S06) states the migration in §0.6 instead." % skipped),
        "n_edits": len(verified),
        "anchor_summary": summary,
        "map_edits_required": verified,
    }
    open(MAP_EDITS_OUT, "w", encoding="utf-8").write(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s: %d edit(s), %d §0.6 occurrence(s) deliberately skipped; anchors %s"
          % (os.path.relpath(MAP_EDITS_OUT, ROOT), len(verified), skipped,
             {k: summary[k] for k in ("n_ok", "n_applied", "not_found", "ambiguous")}))
    return 0


def main(argv):
    if "--audit" in argv:
        return audit()
    if "--apply" in argv:
        return apply()
    if "--dry-run" in argv:
        return apply(dry=True)
    if "--emit-map-edits" in argv:
        return emit_map_edits()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
