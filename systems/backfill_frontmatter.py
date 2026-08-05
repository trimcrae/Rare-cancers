#!/usr/bin/env python3
"""Add YAML frontmatter to every Markdown file that has none. ($0, pure stdlib)

    python3 systems/backfill_frontmatter.py --dry-run
    python3 systems/backfill_frontmatter.py

⛔ WHY THIS IS MECHANICAL AND WHY IT STOPS SHORT.

The repository already wrote all of this — role banners, status lines, supersession markers,
generated-file banners — in four incompatible informal conventions, none of them machine-readable.
This does not invent metadata; it reads what is already there and puts it in one shape.

⚠ WHAT IT REFUSES TO INVENT:

  `last_verified`  is set to the literal `unverified`, NEVER to today's date. This script has not
                   read 185 documents. Stamping them would claim a verification nobody performed —
                   the "a populated field is not a measured one" failure, in the single field whose
                   entire job is to say how stale something is. The checker counts the unverified,
                   and that count is meant to fall as people read them.

  `canonical_for`  is left empty. Deciding that a document OWNS a concept is a judgement, and a
                   wrong one creates a second home for a fact — the exact bug the model removes.

  `purpose`/`scope` are taken from an existing role banner where one exists; otherwise they are
                   derived from the path and marked so a reader knows they were not authored.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "systems/views"}

# Path prefix -> (kind, level, audience). First match wins; order matters.
BY_PATH = [
    ("research/manuscripts/", "manuscript", "L3"),
    ("research/modalities/", "memo", "L4"),
    ("research/compute/", "runbook", "—"),
    ("research/hypotheses/", "memo", "L5"),
    ("archive/", "historical", "—"),
    ("systems/", "policy", "L0"),
    ("research/", "index", "—"),
]

# In-document signals. Order matters: the first hit wins.
#
# ⚠ THESE ARE CHECKED ONLY IN THE FIRST 12 LINES, AND ONLY ON LINES THAT DO NOT LINK ELSEWHERE.
# The first version scanned 40 lines and matched anywhere, which classified CLAUDE.md — the most
# important file in the repository — as `historical`/`superseded`, because line 24 says
# "STRATEGY.md is now history only". It was describing ANOTHER document. A banner about a
# different file is not this file's status, and reading it as one is the same mistake as treating
# a populated field as a measured one.
STATUS_SIGNALS = [
    (r"\bPREREGISTRATION\b|^#.*\bprereg", "immutable", "prereg"),
    (r"⛔?\s*SUPERSEDED|^\s*>?\s*#*\s*RETIRED\b|\bhas been retired\b", "superseded", "historical"),
    (r"\bHISTORY ONLY\b|\bTHIS FILE OWNS NOTHING\b", "historical", "historical"),
]

#: A generated file is rendered by a checker that compares its whole content against a fresh render.
#: Adding frontmatter to one makes it differ from what its generator produces and turns that check
#: red — measured on the first run. Generated files are SKIPPED; their generator owns their header.
# ⚠ CASE-INSENSITIVE, AND OVER THE FIRST 20 LINES. The first version required upper-case "DO NOT EDIT"
#: within 8 lines and missed a file whose banner reads "⛔ **GENERATED FILE — do not edit.**" on line 3
#: of its body. A near-miss detector is worse than none: it reports success while letting exactly the
#: file it exists to protect through.
GENERATED_BANNER = re.compile(r"GENERATED FILE\s*[—-]?\s*do not edit|^<!--\s*GENERATED", re.M | re.I)

#: A line that links to another document is talking ABOUT that document, not declaring its own status.
LINKS_ELSEWHERE = re.compile(r"\]\(|\.md\b")

#: ⭐ EXPLICIT OVERRIDES for the root canonical set. A heuristic reading prose cannot classify a RULES
#: file that talks about supersession in every other paragraph: CLAUDE.md was twice classified
#: `superseded` because its own text explains how to retire a value. These seven are known, so they are
#: stated rather than guessed — and stating what you know beats a cleverer guess every time.
OVERRIDE = {
    "CLAUDE.md":            ("convention", "live", "—"),
    "AGENTS.md":            ("runbook", "live", "—"),
    "README.md":            ("index", "—", "—"),
    "CONTRIBUTING.md":      ("runbook", "live", "—"),
    "systems/POLICY-evidence.md": ("policy", "live", "L0"),
    "MEDICAL_DISCLAIMER.md": ("policy", "live", "—"),
    "STRATEGY.md":          ("historical", "historical", "—"),
}

ROLE_BANNER = re.compile(r"^>\s*\*\*Role:\s*(.+?)\.?\*\*", re.M)
H1 = re.compile(r"^#\s+(.+)$", re.M)


def _slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").upper()


def slug(rel: str, all_rels=None) -> str:
    """A document id, unique across the repository.

    ⛔ THE FIRST VERSION DERIVED IT FROM THE BASENAME ALONE, AND SEVEN FILES ENDED UP SHARING TWO IDS:
    `DOC-METHODOLOGY` on both `METHODOLOGY.md` and `research/hypotheses/METHODOLOGY.md` — two documents
    that are not the same contract and are cited for different things — and `DOC-README` on five
    READMEs. That contradicts the one thing CONVENTIONS.md exists to guarantee, that a name always
    resolves to exactly one thing, and it did so in the namespace the whole document layer is keyed on.

    ⭐ THE TIE-BREAK IS DETERMINISTIC, NOT ALPHABETICAL: **a root-level file keeps the bare id; a nested
    duplicate is path-qualified.** The root file is the one CLAUDE.md and AGENTS.md point at, so it is
    the one whose id a reader will guess. Basenames that do not clash are untouched, so this renames
    only what is actually ambiguous rather than churning 244 ids to fix 7.

    `all_rels` is every relative path in the sweep. Without it there is no way to know a basename is
    shared, so a bare call returns the un-qualified form — correct for a single-file lookup, and the
    reason `[D6]` in `systems_check.py` checks the RESULT rather than trusting this function.
    """
    base = f"DOC-{_slugify(os.path.splitext(os.path.basename(rel))[0])}"
    if not all_rels:
        return base
    shared = sum(1 for r in all_rels
                 if os.path.splitext(os.path.basename(r))[0] == os.path.splitext(os.path.basename(rel))[0])
    if shared < 2 or "/" not in rel:
        return base
    return f"DOC-{_slugify(os.path.splitext(rel)[0])}"


def classify(rel: str, head: str):
    if rel in OVERRIDE:
        k, st, lv = OVERRIDE[rel]
        return (k, st, lv) if st != "—" else (k, "live", lv)
    kind, level = "memo", "—"
    for prefix, k, lv in BY_PATH:
        if rel.startswith(prefix):
            kind, level = k, lv
            break
    status = "live"
    # Only a line in the document's own banner region that is NOT about another file can set status.
    # A marker only counts as a BANNER: a heading, a blockquote, or bold at the start of a line.
    # Prose that merely uses the word "superseded" is not a status declaration — that is how a rules
    # file explaining how to retire a value got itself retired.
    own = [ln for ln in head.splitlines()[:12]
           if not LINKS_ELSEWHERE.search(ln) and re.match(r"^\s*(#{1,3}\s|>|\*\*)", ln)]
    own_text = "\n".join(own)
    for pat, st, kd in STATUS_SIGNALS:
        if re.search(pat, own_text, re.M | re.I):
            status, kind = st, kd
            break
    if "prereg" in os.path.basename(rel).lower():
        status, kind = "immutable", "prereg"
    return kind, status, level


def build(rel: str, text: str, all_rels=None) -> str:
    head = "\n".join(text.splitlines()[:40])
    kind, status, level = classify(rel, head)

    m = H1.search(text)
    title = (m.group(1) if m else os.path.basename(rel)).strip()
    title = re.sub(r"[`*⛔⚠★⭐🗺📊✅❌⏱️🔄]", "", title).strip()[:120] or os.path.basename(rel)

    rb = ROLE_BANNER.search(text)
    if rb:
        purpose = re.sub(r"\s+", " ", rb.group(1)).strip()[:300]
        scope = "As stated in the document's own role banner."
    else:
        purpose = f"See the document body; purpose was not stated separately when frontmatter was backfilled."
        scope = f"Scope not separately declared. Inferred kind `{kind}` from its location under {os.path.dirname(rel) or '.'}/."

    aud = ["maintainers", "autonomous research agents"]
    if kind == "manuscript":
        aud = ["maintainers", "external reviewers", "autonomous research agents"]

    lines = ["---",
             f"id: {slug(rel, all_rels)}",
             f"title: {title}",
             f"level: {level}",
             f"kind: {kind}",
             f"status: {status}",
             "canonical_for: []",
             f"purpose: {purpose}",
             f"scope: {scope}",
             f"audience: [{', '.join(aud)}]",
             "date: 2026-08-05",
             "last_verified: unverified",
             "_backfilled: true",
             "---",
             ""]
    return "\n".join(lines) + text


def targets():
    """Returns (needs_backfill, every_id_bearing_path).

    ⚠ THE SECOND LIST IS WIDER THAN THE FIRST ON PURPOSE. `slug()` decides whether to path-qualify by
    asking whether a basename is shared, and a new document can clash with one that ALREADY carries
    frontmatter — which is invisible if the comparison set is only the files being written. Narrowing
    it to the backfill set would reintroduce the collision on the very next document added.
    """
    out, seen = [], []
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO)
        if any(part in SKIP_DIRS for part in rel_root.split(os.sep)):
            dirs[:] = []
            continue
        if rel_root.replace(os.sep, "/").startswith("systems/views"):
            dirs[:] = []
            continue
        for fn in files:
            if not fn.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, fn), REPO).replace(os.sep, "/")
            if rel.startswith(".git/"):
                continue
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            if GENERATED_BANNER.search("\n".join(text.splitlines()[:20])):
                continue  # its generator owns its header; frontmatter here would fail the drift check
            seen.append(rel)
            if text.startswith("---\n"):
                continue
            out.append((rel, text))
    return sorted(out), sorted(seen)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    todo, all_rels = targets()
    from collections import Counter
    kinds, statuses = Counter(), Counter()
    for rel, text in todo:
        head = "\n".join(text.splitlines()[:40])
        k, s, _ = classify(rel, head)
        kinds[k] += 1
        statuses[s] += 1
        if not a.dry_run:
            with open(os.path.join(REPO, rel), "w", encoding="utf-8") as fh:
                fh.write(build(rel, text, all_rels))

    verb = "would backfill" if a.dry_run else "backfilled"
    print(f"{verb} {len(todo)} document(s)")
    print(f"  kind:   {dict(kinds)}")
    print(f"  status: {dict(statuses)}")
    print("  last_verified: unverified on every one — this script has read none of them, and a "
          "date here would claim a verification nobody performed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
