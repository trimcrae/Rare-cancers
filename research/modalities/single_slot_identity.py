#!/usr/bin/env python3
"""SINGLE-SLOT ARTIFACT IDENTITY — bind a fixed output path to the thing it is supposed to hold.

⛔⛔ THE DEFECT CLASS, NOT THE INSTANCE. A "single-slot artifact" is a generator that writes ONE
fixed path whose CONTENT identity — which GEO series, which cohort, which accession — is decided by
a runtime argument. The path never varies, so the identity of what is in the slot is implied by
nothing except whichever run wrote it last. Every downstream reader cites the PATH; none of them can
see that the path changed meaning. Nothing in a `--check` that re-derives an artifact from its own
inputs cache can notice, because a cache for the wrong subject re-derives an artifact for the wrong
subject perfectly.

⚠ MEASURED, AND THIS MODULE EXISTS BECAUSE OF IT (AUT-PROP-009, filed by CYC-0016).
`research/modalities/atr-hrd-sarcoma-series.json` is the slot for GSE299349 and is cited as the
producer of §8 of `emc-atr-vulnerability-assessment.md`, the whole competing-biomarker section.

  * 2026-08-07, 325258cb8 "GEO series GSE28866: sample-level characterisation (CI)" — a dispatch of
    `emc-expression-datasets.yml mode=gse-series` with `series=GSE28866` wrote GSE28866's inputs
    cache, quant cache and artifact into the slot. Verified here by `git show`: the artifact's
    `series` field reads `GSE28866` at that commit and at every commit after it until the repair,
    while the module constant `SERIES` reads `GSE299349` at 325258cb8, at 4a7030e and at a8caba9 —
    it never moved.
  * The wrong series then sat in the slot for twenty days, under a green `--check` the whole time,
    and was found by a blind arithmetic seat reading the manuscript, not by any instrument.
  * 2026-08-27, a8caba9 re-fetched GSE299349 and restored the slot. That was the DATA fix. This
    module is the guard, and the guard is the half that has to outlive the instance.

★ SO THE THING TO BIND IS THE IDENTITY, NOT THE SERIES PAIR. Four independent records claim to know
what is in the slot — the producer's own constant, the artifact, the inputs caches it re-derives
from, and the prose that cites the artifact as its producer — and before this module NOTHING
compared any two of them. A slot registered below is checked on all four.

WHAT EACH CHECK IS, AND WHAT MAKES IT FAIL CLOSED
  A/declared     the producer's identity constant exists, parses and matches the slot's pattern.
                 Read with `ast` from source, never imported: a guard that executes the thing it is
                 auditing inherits its import-time behaviour.
  B/artifact     the committed artifact's identity field equals the declared identity. THIS IS THE
                 CHECK THAT WOULD HAVE CAUGHT THE INCIDENT ON 2026-08-07.
  C/cache        every declared inputs cache's identity field equals it too. `--check` re-derives
                 the artifact FROM these, so a cache with the wrong identity is the upstream half of
                 the same defect and is invisible to a byte-comparison.
  D/members      a cache that carries NO identity field is bound structurally instead: its member
                 ids must be a non-empty subset of the artifact's. An empty intersection is exactly
                 what a cache fetched for another subject looks like.
  E/systems-map  the machine-readable systems map's entry for this path names the declared identity
                 and no other identifier of the same family. The map is what `systems/` reads.
  F/producer     every manuscript that declares this artifact as its producer — the repository's
                 `**Producer:** <script> -> <artifact>` block — must name the declared identity in
                 the section that makes the declaration, and must name no OTHER identifier of the
                 family there. This is the half that makes the guard worth more than the instance:
                 it binds the slot to the claims made from it, which is where the harm lands.

⛔ WHAT THIS DELIBERATELY DOES NOT BIND, EACH FOR A MEASURED REASON.
  1. It does not check "every file that mentions the artifact". Measured over the whole repository
     on 2026-08-27: 26 lines name the artifact or its producer AND another `GSE` accession on the
     same line, and EVERY ONE of them is legitimate — the ledger, the CYC-0016/0018 receipts and a
     review seat recording this very incident verbatim, plus `new-evidence-routes.md` citing the
     producer's docstring about a DIFFERENT series (GSE24369) as a cautionary precedent, plus a
     provenance note in `emc-expression-panels.json` recording the historical wrong run. A rule that
     is red on twenty-six true sentences gets switched off, so the scope is the DECLARING relation
     (F) and the structured map (E), both of which were green on the unmutated tree.
  2. It does not check that the artifact's CONTENT is about the declared identity — sample counts,
     titles, accession prefixes inside the payload. That is a different guard and a bigger one; the
     honest statement is that identity here means the identity fields and the declaring prose, and
     a payload deliberately mislabelled with the right `series` string would pass.
  3. It does not read the network. Everything is offline and pure stdlib, so it can run in the
     default commit loop.

WHERE IT RUNS. `scripts/preflight.sh`, the "generated deposit artifacts reproduce from their
generators" gate, in the DEFAULT commit loop — before the mistake is shared, which is the whole
point (the modalities suite is opt-in behind `PREFLIGHT_MODALITIES=1` and CI's copy runs on push,
i.e. after the commit that ships the wrong artifact). The mutation tests live in
`tests/test_single_slot_identity.py` because a gate must never mutate the tree it is checking.

    python3 research/modalities/single_slot_identity.py --check
"""

import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


# =============================================================================================
# THE REGISTRY. One entry per single-slot artifact. Adding a slot is a dict, not a code change,
# and the gate below picks it up with no further wiring.
# =============================================================================================
SLOTS = [
    {
        "id": "ART-ATR-HRD-SERIES",
        "producer": "research/modalities/atr_hrd_sarcoma_series.py",
        "identity_attr": "SERIES",
        # The family the identity belongs to. Anything matching this pattern in a place bound below
        # is an identity CLAIM, so a second one there is a contradiction rather than a mention.
        "identity_pattern": r"GSE\d+",
        "artifact": "research/modalities/atr-hrd-sarcoma-series.json",
        "artifact_identity": ("series",),
        # ⚠ THE CACHES ARE NOT A DETAIL. `--check` re-derives the artifact from exactly these, so a
        # cache for the wrong series makes the artifact for the wrong series reproduce perfectly.
        "caches": [
            {"path": "research/modalities/atr-hrd-sarcoma-series-inputs.json",
             "identity": ("series",)},
            # The quant cache carries no accession of its own — it is keyed by GSM — so it is bound
            # by MEMBERSHIP instead. A quant cache fetched for another series shares no sample id
            # with this artifact, which is a total mismatch rather than a subtle one.
            {"path": "research/modalities/atr-hrd-sarcoma-series-quant-inputs.json",
             "members": ("per_sample", "[]"),
             "artifact_members": ("samples", "[]", "accession")},
        ],
        # The one machine-readable map `systems/` and the manuscripts both read.
        "systems_map": "research/manuscripts/emc-systems-map.json",
        "systems_map_collection": "artifacts",
        "systems_map_key": "path",
        # ⛔ NON-VACUITY. A guard over "every declaring document" is silently satisfied by zero
        # documents, and zero is exactly what a renamed link or a deleted section produces. These
        # files MUST still declare this artifact as their producer; losing the declaration is a
        # finding, not a pass.
        "declared_by": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
    },
]


# =============================================================================================
# small readers
# =============================================================================================
def _dig(obj, path):
    """Follow `path` through nested JSON. `"[]"` means 'iterate this list'.

    Returns a LIST of leaves, so ("samples", "[]", "accession") over a list of sample records is a
    list of accessions and ("series",) is a one-element list. A path that does not resolve returns
    [] rather than raising, because 'the field is not there' is a finding this module must be able
    to REPORT — an exception here would abort the other checks (CLAUDE.md §4: an absent reading is
    not a reading of absence).
    """
    cur = [obj]
    for step in path:
        nxt = []
        for c in cur:
            if step == "[]":
                if isinstance(c, list):
                    nxt.extend(c)
                elif isinstance(c, dict):
                    nxt.extend(c.keys())
            elif isinstance(c, dict) and step in c:
                nxt.append(c[step])
        cur = nxt
    return cur


def _load_json(root, rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None, f"missing file: {rel}"
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as e:                                        # noqa: BLE001
        return None, f"unreadable JSON in {rel}: {type(e).__name__}: {e}"


def declared_identity(root, slot):
    """The producer's identity constant, read from SOURCE with `ast`.

    ⛔ NOT `import`. The producer is a fetch-capable module and this guard must be safe to run over
    a tree it does not trust; parsing cannot execute a module-level side effect, and it also means
    a producer whose imports are broken still gets its identity read rather than silently skipped.
    """
    p = os.path.join(root, slot["producer"])
    if not os.path.exists(p):
        return None, f"A/declared: producer is missing: {slot['producer']}"
    try:
        with open(p, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=p)
    except SyntaxError as e:
        return None, f"A/declared: {slot['producer']} does not parse: {e}"
    attr = slot["identity_attr"]
    found = None
    for node in tree.body:                      # module level only: a constant, not a computed value
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == attr and isinstance(node.value, ast.Constant):
                    found = node.value.value
    if not isinstance(found, str):
        return None, (f"A/declared: {slot['producer']} defines no module-level string `{attr}` — "
                      f"the slot's identity is declared nowhere, so nothing below can be bound "
                      f"to it")
    if not re.fullmatch(slot["identity_pattern"], found):
        return None, (f"A/declared: `{attr} = {found!r}` in {slot['producer']} does not match the "
                      f"slot's identity pattern {slot['identity_pattern']!r}")
    return found, None


# ---------------------------------------------------------------------------------------------
# markdown: sections and producer declarations
# ---------------------------------------------------------------------------------------------
_HEADING = re.compile(r"^#{1,6}\s")
_PRODUCER = re.compile(r"\bProducer:")


def _sections(lines):
    """[(start, end)] half-open line-index spans, split on ATX headings, ignoring fenced code."""
    fenced, heads = False, []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and _HEADING.match(line):
            heads.append(i)
    if not heads or heads[0] != 0:
        heads.insert(0, 0)
    return [(h, heads[k + 1] if k + 1 < len(heads) else len(lines)) for k, h in enumerate(heads)]


def _declaration_blocks(lines):
    """Line spans of every `Producer:` declaration — the line plus its non-blank continuation.

    The repository writes these as a blockquote whose link to the artifact is on the NEXT line
    (`> **Producer:** [x.py](...) ->\\n> [x.json](...)`), so a one-line window would miss the half
    that names the artifact. The block ends at the first blank line, which is where the declaration
    ends and the prose begins.
    """
    out = []
    for i, line in enumerate(lines):
        if _PRODUCER.search(line):
            j = i
            while j + 1 < len(lines) and lines[j + 1].strip():
                j += 1
            out.append((i, j + 1))
    return out


def _check_declaring_doc(root, rel, slot, ident, must_declare):
    """F/producer for ONE document. Returns (failures, n_declarations_found)."""
    fails, n = [], 0
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        if must_declare:
            fails.append(f"F/producer: {rel} is declared_by for {slot['id']} but does not exist")
        return fails, 0
    with open(p, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    art_base = os.path.basename(slot["artifact"])
    prod_base = os.path.basename(slot["producer"])
    pat = re.compile(slot["identity_pattern"])
    sections = _sections(lines)
    for a, b in _declaration_blocks(lines):
        block = "\n".join(lines[a:b])
        if art_base not in block and prod_base not in block:
            continue                                   # somebody else's Producer block
        n += 1
        sec = next(((s, e) for s, e in sections if s <= a < e), (a, b))
        body = "\n".join(lines[sec[0]:sec[1]])
        seen = set(pat.findall(body))
        if ident not in seen:
            fails.append(
                f"F/producer: {rel}:{a + 1} declares {art_base} as the producer of the section "
                f"'{lines[sec[0]].strip()[:70]}', but that section never names {ident} — the "
                f"prose and the slot are no longer bound to each other")
        for other in sorted(seen - {ident}):
            fails.append(
                f"F/producer: {rel}:{a + 1} declares {art_base} as its producer, and its section "
                f"names {other}, which is not the {ident} that producer declares. The section's "
                f"claims are attributed to a slot holding something else")
    if must_declare and n == 0:
        fails.append(
            f"F/producer: {rel} is registered as declaring {os.path.basename(slot['artifact'])} as "
            f"its producer, and no such declaration is there any more. The binding this guard "
            f"checks has not been satisfied — it has DISAPPEARED, which is the failure that looks "
            f"most like a pass")
    return fails, n


# =============================================================================================
def check_slot(slot, root=REPO):
    """Every failure for one slot, as a list of attributed strings. Empty list = bound."""
    fails = []
    ident, err = declared_identity(root, slot)
    if err:
        return [err]                     # nothing below can be compared to an identity we cannot read

    art, err = _load_json(root, slot["artifact"])
    if err:
        fails.append(f"B/artifact: {err}")
    else:
        got = _dig(art, slot["artifact_identity"])
        key = ".".join(slot["artifact_identity"])
        if not got:
            fails.append(f"B/artifact: {slot['artifact']} has no `{key}` field, so the slot holds "
                         f"no statement of what is in it")
        elif got[0] != ident:
            fails.append(
                f"B/artifact: {slot['artifact']} holds `{key} = {got[0]!r}` but its producer "
                f"declares {slot['identity_attr']} = {ident!r}. ⚠ Which of the two moved is not "
                f"decided here — a run for another subject may have written the slot, or the "
                f"producer may have been re-pointed and the slot left behind. What IS decided: "
                f"every reader citing this path is citing {got[0]}")

    for cache in slot["caches"]:
        cj, err = _load_json(root, cache["path"])
        if err:
            fails.append(f"C/cache: {err}")
            continue
        if "identity" in cache:
            got = _dig(cj, cache["identity"])
            key = ".".join(cache["identity"])
            if not got:
                fails.append(f"C/cache: {cache['path']} has no `{key}` field")
            elif got[0] != ident:
                fails.append(
                    f"C/cache: {cache['path']} holds `{key} = {got[0]!r}` but the producer declares "
                    f"{ident!r}. `--check` re-derives the artifact from this cache, so it would "
                    f"reproduce {got[0]} byte-identically and report OK")
        if "members" in cache:
            if art is None:
                fails.append(f"D/members: cannot bind {cache['path']} by membership — the artifact "
                             f"did not load")
                continue
            cm = set(_dig(cj, cache["members"]))
            am = set(_dig(art, cache["artifact_members"]))
            if not cm:
                fails.append(f"D/members: {cache['path']} lists no members at "
                             f"`{'.'.join(cache['members'])}`, so it binds nothing")
            elif not am:
                fails.append(f"D/members: {slot['artifact']} lists no members at "
                             f"`{'.'.join(cache['artifact_members'])}`")
            elif not cm <= am:
                extra = sorted(cm - am)
                fails.append(
                    f"D/members: {len(extra)} of {len(cm)} members in {cache['path']} are absent "
                    f"from {slot['artifact']} (e.g. {', '.join(extra[:3])}). A cache fetched for a "
                    f"different subject is what a disjoint member set looks like")

    smap, err = _load_json(root, slot["systems_map"])
    if err:
        fails.append(f"E/systems-map: {err}")
    else:
        rows = [r for r in smap.get(slot["systems_map_collection"], [])
                if r.get(slot["systems_map_key"]) == slot["artifact"]]
        if not rows:
            fails.append(
                f"E/systems-map: {slot['systems_map']} has no `{slot['systems_map_collection']}` "
                f"entry for {slot['artifact']}. The map is the source of truth for what an artifact "
                f"is; an unregistered slot is one nothing can contradict")
        for row in rows:
            pat = re.compile(slot["identity_pattern"])
            seen = set(pat.findall(json.dumps(row)))
            if ident not in seen:
                fails.append(
                    f"E/systems-map: the entry for {slot['artifact']} never names {ident}, so the "
                    f"map records no identity for this slot at all")
            for other in sorted(seen - {ident}):
                fails.append(
                    f"E/systems-map: the entry for {slot['artifact']} names {other}, but the "
                    f"producer declares {ident}")

    declared = set(slot.get("declared_by", []))
    for rel in sorted(declared):
        f, _ = _check_declaring_doc(root, rel, slot, ident, must_declare=True)
        fails.extend(f)
    # ⚠ AND EVERY OTHER MANUSCRIPT THAT DECLARES IT, whether or not the registry knew. A new
    # section citing this producer is exactly as exposed as the registered one, and it arrives
    # without anybody editing this file.
    for rel in _scan_declaring(root, slot, skip=declared):
        f, _ = _check_declaring_doc(root, rel, slot, ident, must_declare=False)
        fails.extend(f)
    return fails


def _scan_declaring(root, slot, skip=()):
    """Markdown under research/ and systems/ carrying a `Producer:` line for this slot."""
    art_base = os.path.basename(slot["artifact"])
    prod_base = os.path.basename(slot["producer"])
    out = []
    for sub in ("research", "systems"):
        base = os.path.join(root, sub)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                if rel in skip:
                    continue
                try:
                    with open(os.path.join(dirpath, fn), encoding="utf-8") as fh:
                        text = fh.read()
                except (OSError, UnicodeDecodeError):
                    continue
                if _PRODUCER.search(text) and (art_base in text or prod_base in text):
                    out.append(rel)
    return sorted(out)


def check_all(root=REPO, slots=None):
    return {s["id"]: check_slot(s, root) for s in (slots if slots is not None else SLOTS)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="single-slot artifact identity guard")
    ap.add_argument("--check", action="store_true",
                    help="verify every registered slot holds the identity its producer declares")
    ap.add_argument("--slot", default=None, help="restrict to one slot id")
    args = ap.parse_args(argv)
    slots = [s for s in SLOTS if args.slot in (None, s["id"])]
    if args.slot and not slots:
        print(f"no such slot: {args.slot}", file=sys.stderr)
        return 2
    if not slots:
        # ⛔ AN EMPTY REGISTRY IS NOT A PASS. A gate that reports OK while measuring nothing is the
        # defect this repository keeps paying for; say it, and fail.
        print("REGISTRY EMPTY — this guard measured nothing", file=sys.stderr)
        return 1
    rc = 0
    for slot in slots:
        fails = check_slot(slot)
        if fails:
            rc = 1
            print(f"IDENTITY UNBOUND — {slot['id']} ({slot['artifact']})", file=sys.stderr)
            for f in fails:
                print(f"    {f}", file=sys.stderr)
            print("    ⛔ This is not a staleness failure and rerunning the generator will not fix "
                  "it: the slot holds, or is cited as holding, something other than what its "
                  "producer declares. Re-fetch the DECLARED subject, or give the other subject its "
                  "own module and output path.", file=sys.stderr)
        else:
            ident, _ = declared_identity(REPO, slot)
            print(f"OK   {slot['id']} bound to {ident} "
                  f"(artifact, {len(slot['caches'])} caches, systems map, "
                  f"{len(slot.get('declared_by', []))} declaring document(s))")
    return rc


if __name__ == "__main__":
    sys.exit(main())
