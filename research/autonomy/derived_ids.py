#!/usr/bin/env python3
"""THE ROUTE→`AUT-NNN` BINDING, READ FROM A FROZEN FILE RATHER THAN DERIVED FROM A SORT ORDER.

⛔⛔ THE DEFECT (AUT-PD-215, measured 2026-09-03). `priority.build_entries()` minted a derived row's
id as ``AUT-{index + 1:03d}`` over ``sorted(routes, key=id)``. That is not an identity, it is a
POSITION, so adding any route renumbered every route after it. Reproduced against the live graph by
patching `priority._load` (no tracked file touched):

    routes 77 -> 78   derived rows 77 -> 78
    AUT-073: RT-TRIAL-REACH -> RT-TRABECTEDIN-PPARG
    ids whose meaning CHANGED: 76 of 77

⛔ WHAT IT BREAKS IS THE RECORD, NOT A BUILD, WHICH IS WHY IT SCORED ABOVE ORDINARY PROCESS DEFECTS.
`AUT-073` is the escalation trimcrae answered on 2026-09-01 with "This was not a good use of
escalation". After a six-route merge that string names a different route — and so does every other
AUT-NNN in every commit message, receipt, `_stranded_work` note and cross-reference in this
repository, with **nothing red anywhere**. One `systems/tests` module happened to hard-code what
AUT-073 is, and that accident was the entire detection.

⭐ `merge()` WAS NOT THE FIX AND HAD ALREADY CLAIMED TO BE. Its docstring has said "Ids are now
assigned once per route and persisted here" since 2026-08-26, and it is true of anything read
THROUGH `merge()`. But `build_entries()` is where an id is CREATED, three test modules call it raw,
and a fresh ledger has no prior row to donate anything — so the repair was one caller deep and the
mint underneath it was still positional. A repair layered over a broken derivation is a derivation
that is still broken for everyone who does not go through the layer.

★★ SO THE BINDING IS DATA, NOT A DERIVATION, AND AN UNKNOWN ROUTE IS A LOUD FAILURE.
`derived-ledger-ids.json` maps route id → `AUT-NNN` for every route that has ever had one. A route
in it keeps its id forever; a route absent from it makes `build_entries()` RAISE, naming
``--extend`` as the remedy. ⛔ The alternative — mint a plausible id and carry on — is the exact
shape of the original bug: a number that looks right, means something new, and reds nothing.

⚠ WHY NOT A HASH OR A SLUG, WHICH IS WHAT THE LEDGER ROW PROPOSED. `ids.ENTRY_ID` requires a decimal
ordinal, and it is the shared reader for `priority.merge`, `duplicate_ids`, `push_guard` and
`prepush_ledger_guard`. A slug (`AUT-COMPETING-MORTALITY`) does not parse under it, so the grammar
change would land in five readers at once; a hash folded INTO the ordinal space collides, and
resolving a collision by probing makes the id depend on which other routes exist — the same
positional defect with a smaller period. What the row actually asked for is that an id be a function
of the ROUTE rather than of its neighbours, and a frozen lookup table is that function, written down
where a human can read it. ⛔ It is NOT "pinning the route list's order", which the row forbids and
which would leave the next route addition to break everything again.

⚠ AND THE ORDINAL A NEW ROUTE GETS IS STILL ALLOCATED, NOT DERIVED — said plainly rather than
hidden. `--extend` hands out ``max(every ordinal the ledger or the map already uses) + 1``. What
makes that safe is not the allocator, it is that the answer is COMMITTED and never recomputed: an
ordinal moves exactly once, from unassigned to assigned. The old scheme recomputed every id on every
call, which is why it could never be trusted.

⚠ A BINDING WHOSE ROUTE HAS LEFT THE GRAPH IS KEPT, AND `--check` REPORTS IT RATHER THAN FAILING.
Receipts naming that id are immutable history; deleting the binding would make the id unresolvable,
which is the same loss of meaning by a different route. Retiring one is a session's decision with a
reason, never a side effect.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ids as _ids  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
MAP_PATH = HERE / "derived-ledger-ids.json"
LEDGER_PATH = HERE / "research-ledger.json"
ROUTES_PATH = REPO / "systems" / "graph" / "routes.json"

#: The prefix a derived row's id carries. Spelled once, here, and imported by `priority` rather than
#: retyped there — CLAUDE.md rule 1, and the reason `subagents.max_concurrent` cost this loop two
#: separate incidents was a name agreed in prose between two files.
DERIVED_PREFIX = "AUT"


def _load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_map(path: pathlib.Path | None = None) -> dict:
    return _load_json(path or MAP_PATH)


def bindings(path: pathlib.Path | None = None) -> dict[str, str]:
    """`{route_id: "AUT-NNN"}`, frozen."""
    return dict(load_map(path)["bindings"])


def id_for_route(route_id: str, table: dict[str, str] | None = None) -> str:
    """The one id this route has ever had.

    ⛔ RAISES on an unbound route. That is the whole mechanism: the caller cannot invent a number,
    so a new route cannot quietly take one that already means something else.
    """
    table = bindings() if table is None else table
    try:
        return table[route_id]
    except KeyError:
        raise KeyError(
            f"{route_id} has no derived ledger id. ⛔ A derived id is DATA, not a derivation — it "
            f"cannot be minted at read time, because a number invented here is indistinguishable "
            f"from one that already names another route in a receipt. Run\n"
            f"    python3 research/autonomy/derived_ids.py --extend\n"
            f"and COMMIT {MAP_PATH.relative_to(REPO)} with the route that needs it."
        ) from None


def route_for_id(entry_id: str, table: dict[str, str] | None = None) -> str | None:
    """The inverse reading — what does `AUT-073` mean? — which is the one a human wants."""
    table = bindings() if table is None else table
    for route, rid in table.items():
        if rid == entry_id:
            return route
    return None


def _all_used_ordinals(table: dict[str, str], ledger: dict | None) -> set[int]:
    """Every ordinal any ledger id already occupies, across ALL prefixes.

    ⚠ ACROSS ALL PREFIXES ON PURPOSE, AND IT IS THE BEHAVIOUR `merge()` ALREADY HAD. `AUT-PD-215`
    contributes 215, so a new derived route lands above every hand-filed row rather than beside one.
    It wastes ordinals, which cost nothing, and it keeps a grep for a bare number unambiguous.
    """
    used = set()
    for source in (table.values(), [e.get("id", "") for e in (ledger or {}).get("entries", [])]):
        for value in source:
            parsed = _ids.parse_entry_id(str(value or ""))
            if parsed is not None:
                used.add(parsed[1])
    return used


def graph_route_ids(path: pathlib.Path | None = None) -> list[str]:
    doc = _load_json(path or ROUTES_PATH)
    routes = doc["routes"] if isinstance(doc, dict) else doc
    return [r["id"] for r in routes]


def check(map_path: pathlib.Path | None = None,
          ledger_path: pathlib.Path | None = None,
          routes_path: pathlib.Path | None = None) -> tuple[list[str], list[str]]:
    """`(failures, notes)`. Failures fail the commit; notes are reported and do not."""
    failures: list[str] = []
    notes: list[str] = []

    table = bindings(map_path)

    # 1. A binding is a bijection, or an id names two routes and the record is already ambiguous.
    seen: dict[str, list[str]] = {}
    for route, rid in table.items():
        seen.setdefault(rid, []).append(route)
    for rid, routes in sorted(seen.items()):
        if len(routes) > 1:
            failures.append(f"{rid} is bound to {len(routes)} routes: {', '.join(sorted(routes))}")

    # 2. Every id parses under the shared grammar, under the derived prefix.
    for route, rid in sorted(table.items()):
        parsed = _ids.parse_entry_id(rid)
        if parsed is None or parsed[0] != DERIVED_PREFIX:
            failures.append(
                f"{route} -> {rid!r} is not a {DERIVED_PREFIX}-NNN id `ids.parse_entry_id` reads, "
                f"so merge(), duplicate_ids() and the push guards cannot see its ordinal")

    # 3. Every route in the graph is bound. This is the one that fails the commit that adds a route.
    unbound = [r for r in graph_route_ids(routes_path) if r not in table]
    if unbound:
        failures.append(
            f"{len(unbound)} route(s) in systems/graph/routes.json have no derived ledger id: "
            + ", ".join(sorted(unbound))
            + " — run `python3 research/autonomy/derived_ids.py --extend` and commit the result")

    # 4. A binding whose route has left the graph is KEPT and reported. Receipts still name it.
    in_graph = set(graph_route_ids(routes_path))
    retired = sorted(r for r in table if r not in in_graph)
    if retired:
        notes.append(
            f"{len(retired)} binding(s) name a route no longer in the graph, retained so their ids "
            f"stay resolvable: " + ", ".join(retired))

    # 5. ⛔ THE MIGRATION PROOF, OVER THE WHOLE SET RATHER THAN A SPOT CHECK. Every derived row on the
    #    committed ledger must still mean what it meant. This is what makes the change a no-op for
    #    everything already written down, and the ledger row asks for it by name.
    ledger = _load_json(ledger_path or LEDGER_PATH)
    for entry in ledger.get("entries", []):
        if not entry.get("_derived"):
            continue
        route = (entry.get("serves") or {}).get("route")
        if not route:
            failures.append(f"derived ledger row {entry.get('id')} names no route")
            continue
        if route not in table:
            failures.append(
                f"ledger row {entry.get('id')} serves {route}, which the frozen map does not bind")
        elif table[route] != entry.get("id"):
            failures.append(
                f"⛔ MEANING CHANGED: ledger row {entry.get('id')} serves {route}, but the frozen "
                f"map binds {route} to {table[route]}. One of the two is a silent rewrite of what "
                f"an already-written id means — do not 'fix' this by editing whichever is louder")
    return failures, notes


def extend(map_path: pathlib.Path | None = None,
           ledger_path: pathlib.Path | None = None,
           routes_path: pathlib.Path | None = None) -> list[tuple[str, str]]:
    """Bind every graph route that has no id yet. Never renumbers one that has."""
    path = map_path or MAP_PATH
    doc = load_map(path)
    table = dict(doc["bindings"])
    ledger = _load_json(ledger_path or LEDGER_PATH)
    used = _all_used_ordinals(table, ledger)
    nxt = max(used, default=0) + 1

    added: list[tuple[str, str]] = []
    for route in sorted(r for r in graph_route_ids(routes_path) if r not in table):
        while nxt in used:
            nxt += 1
        rid = f"{DERIVED_PREFIX}-{nxt:03d}"
        table[route] = rid
        used.add(nxt)
        added.append((route, rid))
    if added:
        doc["bindings"] = {k: table[k] for k in sorted(table)}
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify the frozen map against the graph "
                                                         "and the committed ledger")
    ap.add_argument("--extend", action="store_true", help="bind graph routes that have no id yet")
    ap.add_argument("--show", metavar="AUT-NNN", help="what route does this id name?")
    args = ap.parse_args(argv)

    if args.show:
        route = route_for_id(args.show)
        print(f"{args.show} -> {route}" if route else f"{args.show} is not a derived ledger id")
        return 0 if route else 1

    if args.extend:
        added = extend()
        if not added:
            print("every graph route already has an id — nothing to bind")
        for route, rid in added:
            print(f"bound {route} -> {rid}")
        return 0

    failures, notes = check()
    table = bindings()
    for note in notes:
        print(f"   note: {note}")
    if failures:
        for f in failures:
            print(f"   {f}")
        return 1
    print(f"{len(table)} route→id bindings, frozen and agreeing with the ledger")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
