#!/usr/bin/env python3
"""Cross-document numeric-consistency linter for the research plan and its companion docs.

WHY THIS EXISTS
---------------
`lint_claims.py` guards what the manuscript may *assert*. This file guards something the
2026-07-25 STRATEGY.md cleanup showed is just as damaging and much harder to spot by
reading: the same quantity stated at **different values in different places**.

That cleanup found, in one pass:

  * the gated-ladder total written as ~$194 twice and ~$128 once, in the same file;
  * a high band of ~$544 whose own per-rung rows summed to ~$561;
  * a dependency spine carrying cumulative $15/$97/$273/$252 against the ladder's
    $13/$48/$104/$194 -- the spine summarised a table it disagreed with;
  * a rung recorded as UNPRICED/BLOCKED in five places and QUALIFIED/PRICED in a sixth;
  * a superseded single-replicate result (-0.552) restated four lines under the table
    that had replaced it (-0.370);
  * a withdrawn per-arm figure cited as justification in a preregistration, and cited
    again in the manuscript paragraph immediately below its own DO-NOT-CITE banner.

Every one is the same failure: a number lived in several places and a correction reached
one of them. The repo had already tried to fix this with prose ("keep the two in sync"),
and prose had already lost -- exactly as it lost for language discipline before
`lint_claims.py` was written. So the rule is mechanised here.

WHAT IT CHECKS
--------------
  D  derivations       -- a total must EQUAL its parts, recomputed from the machine JSON
                          the cost model emits. Catches a wrong CURRENT value.
  A  artifact figures  -- a doc that quotes a machine-written number must quote THAT
                          number. Catches a hand-typed figure with no machine behind it:
                          the scoreboard's "$0.74 spent" beside a $20.11 rental ledger.
  T  table completeness -- a repriced-ladder table must carry EVERY stage the cost model
                          prices, its printed rows must sum to its printed total, and that
                          total must match the tool. The exact shape of the $128 bug: one
                          missing row, a total nobody re-added.
  X  subset             -- a SUMMARY must not carry a value absent from what it summarises.
                          The dependency spine restating the ladder's cumulative chain.
  S  superseded         -- a replaced value may still appear (this repo never silently
                          drops a correction) but ONLY on a line marked as superseded.
                          Catches an OLD value surviving where the fix did not reach.

DESIGN CONSTRAINT (inherited from lint_claims.py's founding lesson)
-------------------------------------------------------------------
    A linter that flags true statements gets ignored, and an ignored linter is worse
    than no linter.

So a superseded value is CLEARED by a supersession marker on its line or in a small
window around it -- markdown prose wraps mid-sentence, so a strict single-line check
would fire on correctly-worded retractions. Patterns are multi-token by policy; a bare
number is not a pattern.

Registry: `pinned-figures.json` beside this file. Adding an entry is part of making a
correction, not extra work after it.

EXIT CODE
---------
  0  consistent
  1  one or more inconsistencies

Stdlib only, no pip. Runs in CI on every push (.github/workflows/tests.yml).

Usage:
    python3 research/manuscripts/lint_consistency.py           # check the repo
    python3 research/manuscripts/lint_consistency.py --json    # machine-readable
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(_HERE))
REGISTRY = os.path.join(_HERE, "pinned-figures.json")

# Markdown prose wraps mid-sentence, so a supersession marker routinely lands on a
# neighbouring line from the number it disclaims. Two lines back covers a wrapped
# lead-in ("... this row previously carried / ~$0.26"); one forward covers a trailing
# "(superseded)". Widening this further starts clearing real violations.
_WINDOW_BACK = 2
_WINDOW_FWD = 1

# ★★ AND THE WINDOW IS BOUNDED IN CHARACTERS, NOT ONLY IN LINES — measured 2026-07-31, from a false clear
# that had already happened.
#
# `degrader-paper-schedule.json` stores each entry as ONE ENORMOUS SINGLE LINE. A line-scoped window is
# therefore the whole entry, thousands of characters wide, so an unrelated `"Superseded framing:"` written
# about a different figure CLEARED three genuinely stale panel counts ("R1, 18 legs" after prereg
# AMENDMENT 4 made it 16). The linter reported success while vouching for stale numbers — the exact class
# CLAUDE.md §1 built it to catch, found only because the counts were read by hand.
#
# ⚠ SCOPING TO "THE ENCLOSING JSON VALUE" WOULD NOT HAVE FIXED IT, which is why this is a proximity bound
# rather than a structural one: the false clear happened INSIDE a single string value. The unit that
# actually means "this retraction covers this text" is ADJACENCY — a disclaimer belongs beside the figure
# it disclaims — so proximity is measured from the match position outward.
#
# 400 chars each way is ~4-5 wrapped prose lines: comfortably more than any real markdown retraction needs
# (the widest in this repo is a two-line wrapped lead-in, well under 200), and far below the multi-thousand
# character entries that caused the false clear. Both directions are pinned by
# tests/test_lint_consistency.py — one test that a distant marker does NOT clear, one that a nearby marker
# on an equally long line still DOES, because over-tightening is how a linter gets switched off.
_WINDOW_CHARS = 400


def load_registry(path=REGISTRY):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _read_lines(repo, rel):
    p = os.path.join(repo, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read().splitlines()


# A contrastive statement of the old value -- "2.10x, **not** 2.42x" -- is the CORRECT
# way to write a correction, so it must pass. Same idea as lint_claims._locally_negated.
_NEGATORS = ("not ", "never ", "no longer ", "rather than ", "instead of ", "isn't ", "≠")
_NEG_LOOKBACK = 28


def _locally_negated(line, start):
    """True if the match is immediately preceded by a negator, i.e. it is a contrast."""
    before = line[max(0, start - _NEG_LOOKBACK):start].lower()
    return any(n in before for n in _NEGATORS)


def _enclosing_heading(lines, idx):
    """The nearest markdown heading at or above idx, or ''."""
    for j in range(idx, -1, -1):
        if lines[j].startswith("#"):
            return lines[j]
    return ""


def is_cleared(lines, idx, markers, line=None, start=None):
    """True if this occurrence is a correctly-marked reference to a superseded value.

    Three ways to clear, each answering a real writing pattern:
      1. a marker NEAR the match -- "was ~$0.26 ... (superseded)". Near means within
         `_WINDOW_BACK`/`_WINDOW_FWD` LINES *and* `_WINDOW_CHARS` CHARACTERS of the match
         itself. The character bound is not decoration: without it, a file that stores an
         entry as one very long line (`degrader-paper-schedule.json`) lets a marker about
         some other figure clear every stale number in the entry. See `_WINDOW_CHARS`.
      2. a negator immediately before the match       -- "2.10x, not 2.42x"
      3. a marker in the ENCLOSING HEADING            -- a whole section of retractions,
         e.g. "## 7. WHAT WAS BELIEVED BEFORE, AND WHICH MEASUREMENT RETIRED IT", or
         STRATEGY.md's "## Appendix A -- superseded numbers and retracted claims",
         whose rows should not each have to repeat the disclaimer. This one stays
         structural on purpose: a heading genuinely scopes everything beneath it.
    """
    if line is not None and start is not None and _locally_negated(line, start):
        return True
    lo = max(0, idx - _WINDOW_BACK)
    hi = min(len(lines), idx + _WINDOW_FWD + 1)
    window = lines[lo:hi]
    # Where the match sits inside the joined window, so proximity is measured from the
    # FIGURE and not from the start of whatever line happens to contain it.
    offset = sum(len(l) + 1 for l in lines[lo:idx]) + (start or 0)
    blob = "\n".join(window)
    near = blob[max(0, offset - _WINDOW_CHARS):offset + _WINDOW_CHARS].lower()
    if any(m.lower() in near for m in markers):
        return True
    heading = _enclosing_heading(lines, idx).lower()
    return any(m.lower() in heading for m in markers)


def _finding(rule, severity, path, line, message, detail=""):
    return {
        "rule": rule,
        "severity": severity,
        "file": path,
        "line": line,
        "message": message,
        "detail": detail,
    }


def _nums(text):
    """Every number in a string, as floats. Handles $1,234.56 and unicode minus."""
    text = text.replace("−", "-").replace(",", "")
    return [float(m) for m in re.findall(r"-?\d+(?:\.\d+)?", text)]


# ---------------------------------------------------------------------------
# D: derivations -- a total must equal its parts
# ---------------------------------------------------------------------------
def check_derivations(reg, repo=REPO):
    out = []
    for d in reg.get("derivations", []):
        tool_path = os.path.join(repo, d["tool_json"])
        if not os.path.exists(tool_path):
            out.append(_finding("D-tool-json-missing", "ERROR", d["tool_json"], 0,
                                "the cost model's output JSON is missing, so no total can be derived"))
            continue
        with open(tool_path, encoding="utf-8") as fh:
            tool = json.load(fh)

        ladder = tool.get("ladder", {})
        rows_mid = sum(v["plan_usd"] for v in ladder.values())
        rows_lo = sum(v["range_usd"][0] for v in ladder.values())
        rows_hi = sum(v["range_usd"][1] for v in ladder.values())
        tol = d.get("tolerance_usd", 1.0)

        # D1 -- the tool's own reported total must equal its own rows. A tool whose
        # total drifts from its rows would poison every doc downstream of it.
        for label, rows, total in (
            ("total_plan_usd", rows_mid, tool.get("total_plan_usd")),
            ("total_range_usd[0]", rows_lo, (tool.get("total_range_usd") or [None, None])[0]),
            ("total_range_usd[1]", rows_hi, (tool.get("total_range_usd") or [None, None])[1]),
        ):
            if total is None or abs(total - rows) > tol:
                out.append(_finding(
                    "D-tool-total-mismatch", "ERROR", d["tool_json"], 0,
                    f"{label} is {total}, but its own ladder rows sum to {rows:.2f}",
                    "regenerate with research/modalities/vast_cost_model.py"))

        # D2 -- the pinned ladder total must equal tool + the stages the tool omits.
        nts = d["non_tool_stages"]
        want_lo = rows_lo + sum(v[0] for v in nts.values())
        want_mid = rows_mid + sum(v[1] for v in nts.values())
        want_hi = rows_hi + sum(v[2] for v in nts.values())
        for label, want, declared in (
            ("mid", want_mid, d["expect_mid"]),
            ("low", want_lo, d["expect_low"]),
            ("high", want_hi, d["expect_high"]),
        ):
            if abs(want - declared) > tol:
                out.append(_finding(
                    "D-ladder-total", "ERROR", "pinned-figures.json", 0,
                    f"{d['id']} {label}: registry says {declared}, "
                    f"but {d['tool_json']} + the declared non-tool stages give {want:.1f}",
                    "either the tool was regenerated (update expect_*) or a non-tool stage changed"))

        # D3 -- every doc that quotes the total must quote the SAME one. This is the
        # check that would have caught $194-vs-$128 sitting in one file.
        pat = re.compile(
            r"\$" + str(d["expect_mid"]) + r"\b[^\n]{0,40}?\$" + str(d["expect_low"]) +
            r"\s*[–—-]\s*" + str(d["expect_high"]) + r"\b")
        for rel in d.get("must_appear_in", []):
            lines = _read_lines(repo, rel)
            if lines is None:
                out.append(_finding("D-target-missing", "ERROR", rel, 0, "declared target file not found"))
                continue
            if not any(pat.search(ln) for ln in lines):
                out.append(_finding(
                    "D-total-not-stated", "ERROR", rel, 0,
                    f"does not state the pinned ladder total as "
                    f"${d['expect_mid']} (${d['expect_low']}–{d['expect_high']})",
                    "every doc that carries the total must carry the same one, verbatim"))
    return out


# ---------------------------------------------------------------------------
# A: artifact figures -- a doc quoting a machine-written number must quote THAT number
#
# WHY THIS RULE WAS ADDED (2026-07-27). The scoreboard headline read "$0.74 spent" while
# the step 1 fan-out's own ledger stood at $20.11 -- a hand-typed realised total, ~27x
# low, understating spend while three lanes were billing. D/T/X/S could not see it: it
# was not a ladder total, not a table row, not a summary of another table, and not a
# superseded value. It was simply a number in prose with no machine behind it.
#
# The fix is the same shape as D: name the artifact, name the key, and require every doc
# that quotes it to quote the artifact's value.
#
# ★ IT CHECKS THE COMMITTED SNAPSHOT, NOT A LIVE RECOMPUTATION, and that is deliberate.
# The lanes bill continuously, so a live figure moves several times an hour; a rule
# demanding the doc track that would be red almost always, and an always-red linter is
# the failure lint_claims.py's founding lesson warns about. The snapshot moves only when
# someone runs `realised_spend.py --write` -- so this fires exactly when a refresh
# happened and the doc was not updated in the same commit, which is the real failure mode.
# ---------------------------------------------------------------------------
def check_artifact_figures(reg, repo=REPO):
    out = []
    for a in reg.get("artifact_figures", []):
        path = os.path.join(repo, a["artifact"])
        if not os.path.exists(path):
            out.append(_finding("A-artifact-missing", "ERROR", a["artifact"], 0,
                                f"{a['id']}: the artifact this figure is derived from is missing",
                                a.get("regenerate", "")))
            continue
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        try:
            value = float(_dig_json(doc, a["key"]))
        except Exception as e:  # noqa: BLE001
            out.append(_finding("A-key-missing", "ERROR", a["artifact"], 0,
                                f"{a['id']}: cannot read key {a['key']!r} ({type(e).__name__})",
                                a.get("regenerate", "")))
            continue
        shown = a.get("format", "${:.2f}").format(value)
        tol = a.get("tolerance", 0.005)
        for rel in a.get("must_appear_in", []):
            lines = _read_lines(repo, rel)
            if lines is None:
                out.append(_finding("A-target-missing", "ERROR", rel, 0, "declared target file not found"))
                continue
            hits = [(i, ln) for i, ln in enumerate(lines, 1) if re.search(a["context"], ln)]
            if not hits:
                out.append(_finding(
                    "A-figure-not-stated", "ERROR", rel, 0,
                    f"{a['id']}: no line matches the declared context /{a['context']}/, so the "
                    f"figure this doc is supposed to carry ({shown}) is not there at all",
                    a.get("regenerate", "")))
                continue
            for ln_no, ln in hits:
                quoted = _nums(ln)
                if not any(abs(q - value) <= tol for q in quoted):
                    out.append(_finding(
                        "A-figure-mismatch", "ERROR", rel, ln_no,
                        f"{a['id']}: this line quotes {quoted} but {a['artifact']}:{a['key']} "
                        f"is {shown}",
                        a.get("regenerate", "")))
    return out


def _dig_json(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        cur = cur[part]
    return cur


# ---------------------------------------------------------------------------
# T: table completeness -- a subset total masquerading as a whole
# ---------------------------------------------------------------------------
def _section_lines(lines, header):
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip().startswith(header))
    except StopIteration:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## ") and not lines[i].strip().startswith(header):
            end = i
            break
    return lines[start:end]


def check_table_completeness(reg, repo=REPO):
    out = []
    for t in reg.get("table_completeness", []):
        lines = _read_lines(repo, t["file"])
        if lines is None:
            out.append(_finding("T-file-missing", "ERROR", t["file"], 0, "declared target file not found"))
            continue
        sec = _section_lines(lines, t["section"])
        if sec is None:
            out.append(_finding("T-section-missing", "ERROR", t["file"], 0,
                                f"section {t['section']!r} not found"))
            continue

        # Search the TABLE ROWS ONLY, never the surrounding prose. Adversarial test,
        # 2026-07-25: with the 5c row deleted this check still passed, because the
        # section's own explanatory note happens to contain the string "5c" -- so the
        # linter cleared the very deletion it exists to catch.
        rows = [ln for ln in sec if ln.lstrip().startswith("|")
                and not re.match(r"^\s*\|[\s:|-]*\|?\s*$", ln)
                and not re.search(r"\*\*TOTAL", ln)]
        row_blob = "\n".join(rows).lower()

        with open(os.path.join(repo, t["tool_json"]), encoding="utf-8") as fh:
            tool = json.load(fh)
        hints = t.get("row_key_hints", {})

        missing = []
        for key in tool.get("ladder", {}):
            hint = hints.get(key, key)
            if hint.lower() not in row_blob:
                missing.append(key)
        if missing:
            out.append(_finding(
                "T-missing-row", "ERROR", t["file"], 0,
                f"the repriced-ladder table omits {len(missing)} stage(s) the cost model prices: "
                + "; ".join(missing),
                "a table missing a row still prints a plausible total -- that is exactly how "
                "$128 escaped into nr4a3-program-map.md as a whole-ladder figure"))

        # TWO independent total checks. The row-sum one is the load-bearing one: deleting a
        # row leaves a total that still matches the tool if nobody re-added the column, which
        # is precisely how a subset total ($128) came to be quoted as the whole ladder.
        tot_line = next((ln for ln in sec if re.search(r"\*\*TOTAL", ln)), None)
        if tot_line is None:
            out.append(_finding("T-no-total-row", "ERROR", t["file"], 0,
                                "the table has no **TOTAL** row to check"))
        else:
            tol = max(t.get("tolerance_usd", 1.0), 1.0)
            got = _nums(tot_line.replace("$", " ").replace("~", " "))
            want = tool.get("total_plan_usd")
            if want is not None and not any(abs(g - want) <= tol for g in got):
                out.append(_finding(
                    "T-total-mismatch", "ERROR", t["file"], sec.index(tot_line) + 1,
                    f"printed TOTAL {got} does not include the cost model's {want:.2f}",
                    tot_line.strip()[:160]))

            # The table must be internally consistent: its own printed rows must sum to its
            # own printed total. Column = the bolded plan-$ cell, e.g. "| ... | **21.21** |".
            row_vals = []
            for ln in rows:
                bolded = re.findall(r"\*\*\s*\$?\s*([\d.,]+)\s*\*\*", ln)
                if bolded:
                    row_vals.append(_nums(bolded[-1])[0])
            if row_vals and want is not None:
                s = sum(row_vals)
                if not any(abs(g - s) <= tol for g in got):
                    out.append(_finding(
                        "T-rows-do-not-sum", "ERROR", t["file"], sec.index(tot_line) + 1,
                        f"the table's {len(row_vals)} printed rows sum to {s:.2f}, "
                        f"but its TOTAL row reads {got}",
                        "a deleted row leaves a plausible-looking total — re-add the column"))
    return out


# ---------------------------------------------------------------------------
# X: a summary must not contradict the thing it summarises
# ---------------------------------------------------------------------------
def check_subsets(reg, repo=REPO):
    """Every value in the SUMMARY must also appear in the SOURCE it summarises.

    The dependency spine restates the ladder's cumulative chain. On 2026-07-25 it was
    carrying $15/$97/$273/$252 against the ladder's $13/$48/$104/$194 -- a summary that
    silently disagreed with its own source for long enough that both looked authoritative.
    Subset, not equality: a spine legitimately skips rungs it does not draw.
    """
    out = []
    for c in reg.get("subset_checks", []):
        lines = _read_lines(repo, c["file"])
        if lines is None:
            out.append(_finding("X-file-missing", "ERROR", c["file"], 0, "declared target file not found"))
            continue
        text = "\n".join(lines)
        sup = set(re.findall(c["superset_pattern"], text))
        sub = set(re.findall(c["subset_pattern"], text))
        if not sup or not sub:
            out.append(_finding(
                "X-pattern-found-nothing", "ERROR", c["file"], 0,
                f"{c['id']}: superset matched {len(sup)}, subset matched {len(sub)} — "
                "a check that matches nothing silently passes forever",
                "the document was probably reformatted; update the patterns"))
            continue
        stray = sorted(sub - sup, key=lambda v: (len(v), v))
        if stray:
            out.append(_finding(
                "X-summary-contradicts-source", "ERROR", c["file"], 0,
                f"{c['id']}: {c['subset_name']} carries value(s) absent from {c['superset_name']}: "
                + ", ".join(stray),
                c.get("description", "")))
    return out


# ---------------------------------------------------------------------------
# S: superseded values must carry a supersession marker
# ---------------------------------------------------------------------------
def check_superseded(reg, repo=REPO, targets=None):
    out = []
    markers = reg["supersession_markers"]
    for rel in (targets if targets is not None else reg["targets"]):
        lines = _read_lines(repo, rel)
        if lines is None:
            out.append(_finding("S-target-missing", "ERROR", rel, 0, "declared target file not found"))
            continue
        for entry in reg["superseded"]:
            rx = re.compile(entry["pattern"])
            for i, ln in enumerate(lines):
                m = rx.search(ln)
                if not m:
                    continue
                if is_cleared(lines, i, markers, line=ln, start=m.start()):
                    continue
                out.append(_finding(
                    "S-" + entry["id"], "ERROR", rel, i + 1,
                    f"superseded value {m.group(0)!r} stated without marking it superseded",
                    f"current: {entry['current']} | retired by: {entry['retired_by']}"))
    return out


# ---------------------------------------------------------------------------
def check_in_page_anchors(reg, repo=REPO):
    """Every `](#slug)` in a target document must resolve to a heading IN THAT DOCUMENT.

    ★ WHY THIS IS A CONSISTENCY RULE AND NOT A STYLE ONE (added 2026-08-03). The roadmap is now the single
    steering document, and CLAUDE.md rule 1 is *one fact, one place — everywhere else POINTS AT IT*. A
    pointer that resolves to nothing does not fail loudly: GitHub renders the link, the reader clicks, the
    page does not move, and the fact stays un-found. So the rule that makes the map navigable is exactly
    the rule nothing was checking.

    ⛔ TWO WERE ALREADY BROKEN WHEN THIS WAS WRITTEN, both from the same cause — an anchor typed from what
    the author *meant* the heading to say rather than from the heading:
      `#gpu-economics-full-provenance-in-pricingmd`  (the real heading carries the whole markdown link,
                                                     so the slug swallows `computepricingmd` too)
      `#in-flight-superseded`                        (the heading says no such thing; "superseded" is the
                                                     ref's editorial gloss, not the heading's text)
    Both had survived every doc pass because a dead in-page anchor is silent. Fixed in the same commit.

    The slug rule is GitHub's: lowercase, drop everything that is not word/space/hyphen, spaces to hyphens.
    ⚠ It is applied to the heading TEXT AS WRITTEN, punctuation and emoji included — which is precisely why
    a hand-typed anchor drifts from a heading that later gains a `·`, an emoji or an inline link.
    """
    out = []
    for rel in reg["targets"]:
        path = os.path.join(repo, rel)
        if not os.path.exists(path) or not rel.endswith(".md"):
            continue
        text = open(path, encoding="utf-8").read()
        heads = {_gh_slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.*)$", text, re.M)}
        for m in re.finditer(r"\]\(#([^)]+)\)", text):
            if m.group(1) in heads:
                continue
            line = text.count("\n", 0, m.start()) + 1
            out.append(_finding(
                "N-dead-in-page-anchor", "ERROR", rel, line,
                "in-page anchor #%s resolves to no heading in this file" % m.group(1),
                "a pointer that goes nowhere fails SILENTLY — the link renders, the page does not move, "
                "and the fact it points at stays un-found. Derive the slug from the heading text as "
                "written (lowercase, drop non-word/space/hyphen, spaces -> hyphens); do not type it."))
    return out


def _gh_slug(heading):
    """GitHub's heading -> anchor rule, applied to the heading text exactly as written."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s", "-", s)


# ---------------------------------------------------------------------------
def lint(repo=REPO, registry_path=REGISTRY):
    reg = load_registry(registry_path)
    return (check_derivations(reg, repo) + check_artifact_figures(reg, repo)
            + check_table_completeness(reg, repo)
            + check_subsets(reg, repo) + check_superseded(reg, repo)
            + check_in_page_anchors(reg, repo))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--repo", default=REPO, help="repo root to check")
    args = ap.parse_args(argv)

    findings = lint(args.repo)
    errors = [f for f in findings if f["severity"] == "ERROR"]

    if args.json:
        print(json.dumps({"findings": findings, "n_error": len(errors)}, indent=2))
    else:
        for f in findings:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"{loc}: {f['severity']} [{f['rule']}] {f['message']}")
            if f["detail"]:
                print(f"    {f['detail']}")
            print()
        n_targets = len(load_registry()["targets"])
        print(f"lint_consistency: {len(errors)} ERROR across {n_targets} target file(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
