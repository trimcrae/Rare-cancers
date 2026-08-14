#!/usr/bin/env python3
"""The ONE home for loading fusion-junction ASO screen artifacts, keyed by MEASURED geometry.

⛔⛔ WHY THIS EXISTS. Screens of different gapmer geometries live under the same filename patterns.
`junction-aso-offtarget-*deep500*.json` matches a 16-mer 5-6-5 screen, an 18-mer 5-8-5 screen and a
20-mer 5-10-5 screen; `aso-insilico-evaluation-*` matches all three too. Consumers globbed those
patterns and then applied a gap span — `junction_aso_offtarget.GAP_REGION_1BASED`, which is 5-6-5's
(6, 11) — to whatever came back.

⛔ IT PRODUCED A WRONG NUMBER, NOT A CRASH (2026-08-13). `aso_per_junction_table` globbed the 18-mer
and 20-mer screens, counted an 18-mer's gap-paired hits over SIX of its EIGHT catalytic bases, and
moved `best_available` at the EWSR1 e12, FUS e10 and TAF15 e11 seams — the three clinically central
rows, the ones the manuscript recommends — onto an 18-mer graded against the wrong window. A human
caught it. A guard was then written into that one consumer, which protected that one call site and
left the defect latent in every other module and in the next module anyone writes.

⭐ SO THE FIX IS STRUCTURAL, NOT ANOTHER GUARD. Three properties, and the third is the one that
makes the first two hold tomorrow:

  1. **No API returns a mixed set.** `load_screens()` returns exactly one geometry; `load_by_geometry()`
     returns a MAPPING keyed by geometry. There is no call that hands back one bag of several
     geometries, so pooling cannot be an accident — it requires a caller to iterate the mapping and
     concatenate, which is visible in a diff.
  2. **The caller states the geometry, and there is no default.** A default is how this happens
     again: the module that forgets to think about geometry is exactly the module that would take
     the default, and the default would be right until the day it was not.
  3. **A repo-wide scanner** (`tests/test_one_geometry_screen_loading.py`) fails the build when any
     python module discovers these artifacts by pattern instead of coming through here.

⛔ GEOMETRY IS MEASURED, NEVER READ OFF A FILENAME. Filenames carry `-18mer-`/`-20mer-` markers
today; nothing enforces that, the pre-2026-08-13 screens carry no geometry block at all, and a
naming convention is not a guarantee. The length of the oligonucleotide a screen actually searched
is IN the file — it is the thing that ran — so it is read from the designs.

⛔ AND WHERE AN ARTIFACT STATES ITS OWN GEOMETRY, THE TWO MUST AGREE OR THE LOAD IS REFUSED. A
screen graded against one window and counted against another is the SILENT version of the bug
above: nothing crashes, and every gap-paired count is measured over the wrong columns. Measured
across the 132 committed screen artifacts in this tree, the stated `gap_region_1based` agrees with
the measured length in every single one ([6, 11]↔16, [6, 13]↔18, [6, 15]↔20), so this assertion
costs nothing today and is the only thing standing between a future divergence and a wrong number.

⚠ WHAT THIS IS NOT. It reads committed artifacts and partitions them. It re-screens nothing,
re-grades nothing, and computes no off-target, cleavage, potency, efficacy, safety or
clinical-readiness quantity.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


# ═════════════════════════════════════════════════════════════════════════════════════════════
# GEOMETRY — a value, not a string, so two geometries cannot compare equal by accident
# ═════════════════════════════════════════════════════════════════════════════════════════════
class Geometry:
    """One LNA/DNA/LNA gapmer geometry: total length and wing length, everything else derived.

    ⛔ THE GAP SPAN IS DERIVED HERE AND NOWHERE ELSE. `junction_aso_offtarget.GAP_REGION_1BASED` is
    the span of the geometry that module's ENVIRONMENT built, which is the manuscript's 5-6-5 unless
    a dispatch overrode it. Reading that constant while holding an 18-mer is the original bug, so a
    consumer takes the span from the screen's OWN geometry — `screens.geometry.gap_region_1based` —
    and the two can no longer be different things wearing the same name.
    """

    __slots__ = ("oligo_len", "wing")

    def __init__(self, oligo_len: int, wing: int):
        if not (isinstance(oligo_len, int) and isinstance(wing, int)):
            raise TypeError("a geometry is two integers (oligo_len, wing)")
        if oligo_len <= 2 * wing:
            raise ValueError(f"{oligo_len}-mer with {wing}-nt wings leaves no catalytic gap")
        self.oligo_len = oligo_len
        self.wing = wing

    # -- derived ------------------------------------------------------------------------------
    @property
    def gap_nt(self) -> int:
        return self.oligo_len - 2 * self.wing

    @property
    def gap_region_1based(self) -> tuple[int, int]:
        """1-based inclusive span of the DNA gap — the window a gap-paired hit must cover."""
        return (self.wing + 1, self.oligo_len - self.wing)

    @property
    def architecture(self) -> str:
        return f"{self.wing}-{self.gap_nt}-{self.wing}"

    #: How many junction-spanning registers a seam admits at this geometry. Named because it is
    #: what makes two panels comparable or not: five at the 5-6-5, seven at 5-8-5, nine at 5-10-5.
    @property
    def n_junction_spanning_registers(self) -> int:
        return self.gap_nt - 1

    # -- value semantics ----------------------------------------------------------------------
    def __eq__(self, other):
        return (isinstance(other, Geometry)
                and (self.oligo_len, self.wing) == (other.oligo_len, other.wing))

    def __hash__(self):
        return hash((self.oligo_len, self.wing))

    def __lt__(self, other):
        return (self.oligo_len, self.wing) < (other.oligo_len, other.wing)

    def __repr__(self):
        return f"Geometry({self.oligo_len}-mer {self.architecture})"

    def as_dict(self) -> dict:
        return {"oligo_len": self.oligo_len, "wing": self.wing, "gap_nt": self.gap_nt,
                "architecture": f"{self.architecture} (LNA-DNA-LNA)",
                "gap_region_1based": list(self.gap_region_1based)}


#: The geometry every published number in this lane is derived from, and the one the manuscript
#: reports. ⚠ IT IS A NAME, NOT A DEFAULT — no function in this module falls back to it. Naming it
#: lets a consumer say *which* panel it is about in one legible token instead of typing `16, 5`.
MANUSCRIPT_GEOMETRY = Geometry(16, 5)
GEOMETRY_18MER_585 = Geometry(18, 5)
GEOMETRY_20MER_5_10_5 = Geometry(20, 5)


# ═════════════════════════════════════════════════════════════════════════════════════════════
# ARTIFACT FAMILIES — the patterns, named ONCE
# ═════════════════════════════════════════════════════════════════════════════════════════════
class Family:
    """One artifact family: how to find its files, and how to read designs and stated geometry.

    ⚠ `exclude` IS PART OF THE FAMILY, NOT A CALLER'S BUSINESS. `junction-aso-offtarget-*.json`
    also matches the graded re-scores and the derived locus-collapse artifact, and every consumer
    that globbed it re-typed the same two exclusions — five copies of one rule, which is how one of
    them ends up missing a third file nobody anticipated.
    """

    __slots__ = ("name", "pattern", "exclude", "_designs", "_stated", "_what")

    def __init__(self, name, pattern, exclude, designs, stated, what):
        self.name = name
        self.pattern = pattern
        self.exclude = tuple(exclude)
        self._designs = designs
        self._stated = stated
        self._what = what

    def matches(self, basename: str) -> bool:
        if not fnmatch.fnmatch(basename, self.pattern):
            return False
        return not any(fnmatch.fnmatch(basename, x) for x in self.exclude)

    def designs(self, artifact) -> list[str]:
        """Every antisense design sequence the artifact holds, in no particular order."""
        return [s for s in self._designs(artifact) if isinstance(s, str) and s]

    def stated_geometry(self, artifact) -> dict:
        """{field: value} for every geometry fact the artifact states about ITSELF.

        Absent is absent — a family that records nothing returns `{}`, and an EMPTY dict is never
        treated as agreement. A reading of absence is not a reading, which is why
        `_check_agreement` reports which fields were checkable rather than returning a bare bool.
        """
        return {k: v for k, v in self._stated(artifact).items() if v is not None}

    def __repr__(self):
        return f"Family({self.name})"


def _blast_designs(art):
    return [o.get("antisense_5to3") for o in (art.get("oligos") or []) if isinstance(o, dict)]


def _blast_stated(art):
    method = art.get("method") or {}
    params = method.get("parameters") or {}
    return {"gap_region_1based": method.get("gap_region_1based"),
            "oligo_len": params.get("oligo_len"),
            "wing": params.get("wing")}


def _graded_designs(art):
    per = art.get("per_oligo") or {}
    return [seq for rows in per.values() if isinstance(rows, dict) for seq in rows]


def _graded_stated(art):
    return {"gap_region_1based": art.get("gap_region_1based"),
            "oligo_len": art.get("oligo_len")}


def _eval_designs(art):
    return [d.get("antisense_5to3") for d in (art.get("top_designs") or []) if isinstance(d, dict)]


def _eval_stated(art):
    """The `architecture` string each design carries, e.g. `5-6-5 (LNA-DNA-LNA)`.

    ⚠ ONE VALUE OR NONE. Designs of two architectures in one panel is itself the corruption this
    module refuses, so a disagreement is surfaced as an unusable stated value rather than resolved.
    """
    arch = {d.get("architecture") for d in (art.get("top_designs") or [])
            if isinstance(d, dict) and d.get("architecture")}
    return {"architecture": (arch.pop() if len(arch) == 1 else
                             ("⛔ DISAGREEING: " + ", ".join(sorted(arch))) if arch else None)}


#: ⛔ EVERY PATTERN THAT CAN MATCH MORE THAN ONE GEOMETRY, NAMED ONCE AND HERE.
#: The scanner in `tests/test_one_geometry_screen_loading.py` derives its detector from these
#: prefixes, so a fourth family added here is guarded from the moment it is added — there is no
#: second list to remember.
#:
#: ⚠ THE HYPHEN IN `junction-aso-offtarget-*.json` IS LOAD-BEARING AND IS NOT A TYPO. It excludes
#: the un-suffixed `junction-aso-offtarget.json`, the legacy pre-panel screen at a modelled seam,
#: which every consumer of this family has always excluded — the collapse artifact's committed
#: population is 78 screens and includes it nowhere. Widening the pattern would enlarge that
#: population, which is a data decision with manuscript consequences and not a side effect of
#: tidying a glob. ⛔ AND THE EXCLUSION IS CHECKED RATHER THAN TRUSTED: `unclaimed_files()` below
#: returns every file matching a family prefix that NO family claims, and the scanner test pins
#: that set — so a NEW artifact falling through the gap fails the build instead of being silently
#: invisible to every consumer, which is the fail-quiet direction this rule could otherwise take.
BLAST_SCREEN = Family(
    "blast_screen", "junction-aso-offtarget-*.json",
    ("*-graded.json", "*locus-collapse*"), _blast_designs, _blast_stated,
    "transcriptome-wide near-match screens (the gap-resolved BLAST arm)")
GRADED_RESCORE = Family(
    "graded_rescore", "junction-aso-offtarget-*-graded.json", (),
    _graded_designs, _graded_stated,
    "graded re-scores of a committed screen under the two literature fold-discrimination models")
DESIGN_EVALUATION = Family(
    "design_evaluation", "aso-insilico-evaluation*.json", (),
    _eval_designs, _eval_stated,
    "per-seam design panels with the exhaustive <=1-mismatch local scan")

FAMILIES = (BLAST_SCREEN, GRADED_RESCORE, DESIGN_EVALUATION)

#: The bare prefixes a discovery pattern is built from. The scanner treats a string literal
#: CONTAINING one of these, whose tail is not a complete concrete filename, as artifact discovery.
#: ⚠ NO TRAILING HYPHEN, deliberately: `junction-aso-offtarget` also catches
#: `junction-aso-offtarget*.json`, the spelling a consumer reaches for when it wants "the family
#: and the un-suffixed original too" — which is a discovery pattern like any other.
FAMILY_PREFIXES = ("junction-aso-offtarget", "aso-insilico-evaluation")


def unclaimed_files(root: str | None = None) -> list[str]:
    """Files whose name starts with a family prefix that NO family claims.

    ⛔ THE FAIL-QUIET DIRECTION, MADE LOUD. A consumer that goes through this loader sees exactly
    what the families match; anything else on disk is invisible to it, and invisible is how a
    screen stops being counted without anyone noticing. Two files are legitimately here (the
    un-suffixed legacy screen and the derived locus-collapse artifact) and the scanner test pins
    the set, so a THIRD one — a new campaign's output under a name no family matches — turns the
    build red rather than quietly reaching nobody.
    """
    root = HERE if root is None else root
    out = []
    for name in sorted(os.listdir(root)):
        if not name.endswith(".json"):
            continue
        if not any(name.startswith(p) for p in FAMILY_PREFIXES):
            continue
        if not any(f.matches(name) for f in FAMILIES):
            out.append(name)
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════
# MEASUREMENT
# ═════════════════════════════════════════════════════════════════════════════════════════════
class GeometryError(ValueError):
    """A screen whose geometry cannot be measured, or which disagrees with what it states."""


def measure_oligo_len(family: Family, artifact) -> int | None:
    """The oligonucleotide length this artifact's designs ACTUALLY have, or None if it has none.

    RAISES if one file holds designs of more than one length. That file is internally inconsistent
    — no single dispatch tiles two geometries — and picking one would be choosing which half of a
    corrupt record to believe.
    """
    lens = {len(s) for s in family.designs(artifact)}
    if not lens:
        return None
    if len(lens) > 1:
        raise GeometryError(
            f"one {family.name} artifact holds designs of {sorted(lens)} nucleotides. No single "
            f"screen tiles two geometries, so this file is internally inconsistent and no geometry "
            f"can be assigned to it.")
    return lens.pop()


def _check_agreement(family: Family, artifact, measured_len: int, where: str) -> dict:
    """Refuse if what the artifact SAYS about its geometry disagrees with what it HOLDS.

    Returns the fields that were checkable, so a caller can tell "agrees" from "said nothing".
    ⛔ THE DANGEROUS CASE IS `gap_region_1based`, NOT `oligo_len`. A length mismatch would be caught
    downstream the first time an index ran off the end; a gap span mismatch would not be caught at
    all — every gap-paired count would simply be measured over the wrong columns and the artifact
    would look complete.
    """
    stated = family.stated_geometry(artifact)
    checked = {}
    for field, value in sorted(stated.items()):
        if field == "oligo_len":
            if int(value) != measured_len:
                raise GeometryError(
                    f"{where}: states oligo_len {value} and holds {measured_len}-mer designs")
            checked[field] = value
        elif field == "gap_region_1based":
            lo, hi = (list(value) + [None, None])[:2]
            if lo is None or hi is None:
                continue
            wing = int(lo) - 1
            if wing < 0 or measured_len - wing != int(hi):
                raise GeometryError(
                    f"{where}: states gap_region_1based {list(value)}, which is not the gap of any "
                    f"{measured_len}-mer with equal wings. A screen graded against one window and "
                    f"counted against another is the silent form of the geometry-mixing bug.")
            checked[field] = list(value)
        elif field == "architecture":
            if str(value).startswith("⛔"):
                raise GeometryError(f"{where}: designs disagree about architecture — {value}")
            head = str(value).split()[0]
            try:
                parts = [int(x) for x in head.split("-")]
            except ValueError:
                continue
            if len(parts) == 3 and sum(parts) != measured_len:
                raise GeometryError(
                    f"{where}: states architecture {value!r} ({sum(parts)} nt) and holds "
                    f"{measured_len}-mer designs")
            checked[field] = value
    return checked


def geometry_of(family: Family, artifact, where: str = "<artifact>") -> Geometry | None:
    """The geometry this artifact was produced at, MEASURED and then checked against its own claims.

    ⚠ THE WING IS TAKEN FROM THE STATED GAP SPAN WHERE THERE IS ONE, AND ASSUMED 5 OTHERWISE, WHICH
    IS SAID RATHER THAN HIDDEN. Length alone does not determine the wing: a 20-mer could be 5-10-5
    or 6-8-6. Every screen in this lane states `gap_region_1based`, so the wing is read in practice;
    the fallback exists only for a family that records nothing, and `wing_is_measured` on the
    returned set says which happened, so a consumer is never left inferring it.
    """
    measured_len = measure_oligo_len(family, artifact)
    if measured_len is None:
        return None
    checked = _check_agreement(family, artifact, measured_len, where)
    span = checked.get("gap_region_1based")
    wing = (int(span[0]) - 1) if span else int(checked.get("wing") or 5)
    return Geometry(measured_len, wing)


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE LOADER
# ═════════════════════════════════════════════════════════════════════════════════════════════
class Screen:
    """One committed artifact, with the geometry it was measured at."""

    __slots__ = ("path", "artifact", "geometry", "family", "stated_fields")

    def __init__(self, path, artifact, geometry, family, stated_fields):
        self.path = path
        self.artifact = artifact
        self.geometry = geometry
        self.family = family
        self.stated_fields = stated_fields

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def junction_label(self):
        return self.artifact.get("junction_label")

    def __repr__(self):
        return f"Screen({self.name}, {self.geometry!r})"


class ScreenSet:
    """Every screen of ONE geometry from ONE family. Iterating it cannot yield a second geometry.

    ⛔ THERE IS NO `+`, NO `extend` AND NO `update`. Two ScreenSets of different geometries have no
    operation that merges them, because there is no legitimate reason to hold a mixed bag and every
    illegitimate one starts with a convenience method.
    """

    __slots__ = ("geometry", "family", "_screens", "root")

    def __init__(self, geometry, family, screens, root):
        self.geometry = geometry
        self.family = family
        self._screens = list(screens)
        self.root = root
        bad = {s.geometry for s in self._screens if s.geometry != geometry}
        if bad:
            raise GeometryError(f"ScreenSet({geometry!r}) was handed {sorted(bad)} — refusing")

    def __iter__(self):
        return iter(self._screens)

    def __len__(self):
        return len(self._screens)

    def __bool__(self):
        return bool(self._screens)

    def __getitem__(self, i):
        return self._screens[i]

    @property
    def names(self) -> list[str]:
        return [s.name for s in self._screens]

    @property
    def gap_region_1based(self) -> tuple[int, int]:
        """The window a gap-paired hit must cover, FOR THESE SCREENS. Never a module constant."""
        return self.geometry.gap_region_1based

    @property
    def artifacts(self):
        return [s.artifact for s in self._screens]

    def provenance(self) -> dict:
        """What an artifact derived from this set should record about where it came from."""
        return {"geometry": self.geometry.as_dict(),
                "family": self.family.name,
                "n_screens": len(self._screens),
                "screens": sorted(self.names),
                "_geometry_is_measured": ("from the designs in each artifact, then checked against "
                                          "whatever geometry the artifact states about itself; "
                                          "never read off a filename")}

    def __repr__(self):
        return f"ScreenSet({self.family.name}, {self.geometry!r}, n={len(self._screens)})"


_MISSING = object()


def _iter_family_files(family: Family, root: str):
    for name in sorted(os.listdir(root)):
        if family.matches(name):
            yield os.path.join(root, name)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_by_geometry(family: Family, *, root: str | None = None,
                     select=None) -> dict[Geometry, ScreenSet]:
    """{geometry: ScreenSet} over every artifact of `family`. NEVER one pooled set.

    This is the only way to reach more than one geometry, and it hands back a mapping rather than a
    list precisely so that a consumer which wants them all must decide, in code a reviewer can see,
    what it does with each.

    `select(screen) -> bool` filters on the artifact's own content (depth, junction label,
    orientation status). It is deliberately NOT a filename filter: a filename is a convention, and
    the whole failure this module exists for was a convention treated as a discriminator.
    """
    root = HERE if root is None else root
    out: dict[Geometry, list[Screen]] = {}
    for path in _iter_family_files(family, root):
        try:
            art = _read(path)
        except (OSError, ValueError) as exc:
            raise GeometryError(f"{os.path.basename(path)}: unreadable ({exc})") from exc
        if not isinstance(art, dict):
            continue
        geom = geometry_of(family, art, where=os.path.basename(path))
        if geom is None:
            continue                      # holds no design — nothing to assign a geometry to
        screen = Screen(path, art, geom, family,
                        _check_agreement(family, art, geom.oligo_len, os.path.basename(path)))
        if select is not None and not select(screen):
            continue
        out.setdefault(geom, []).append(screen)
    return {g: ScreenSet(g, family, s, root) for g, s in sorted(out.items())}


def iter_geometries(family: Family, *, root: str | None = None, select=None):
    """`(geometry, ScreenSet)` pairs — ONE GEOMETRY AT A TIME, as a first-class pattern.

    ⭐ THIS IS THE SHAPE A CONSUMER THAT SERVES SEVERAL GEOMETRIES SHOULD WRITE, and it is
    deliberately not the same call as `load_screens`. `offtarget_chance_baseline`'s grouping key is
    `(seam, geometry)`, `aso_gap_length_tradeoff` compares geometries side by side, and
    `submission_tables` emits one column per geometry — none of those wants "geometry X" and none of
    them wants one pooled bag either. Iterating pairs makes the per-geometry loop the natural thing
    to write, and makes any concatenation across the loop visible in the diff that adds it.

    ⚠ THE VALUE IS STILL A `ScreenSet`, so a body that accidentally accumulates into one list still
    cannot produce a set that claims to be one geometry while holding two.
    """
    yield from sorted(load_by_geometry(family, root=root, select=select).items())


def group_by_geometry_and(family: Family, key, *, root: str | None = None, select=None):
    """`{(key(screen), geometry): [Screen, ...]}` — the compound key, built once and here.

    ⛔ WHY THIS IS A LOADER FUNCTION AND NOT A THREE-LINE DICT AT EACH CALL SITE. Two artifacts are
    re-emissions of each other only if they measured the same thing WITH THE SAME REAGENT, and the
    seam is only half of that. `offtarget_chance_baseline` learned this by raising its "two
    different evaluations" refusal on every build once the 18-mer panels landed: the refusal was
    right about the fact and wrong about the remedy — they must not be compared, rather than one
    being chosen over the other. The compound key is the remedy, and it belongs next to the geometry
    measurement so the second module that needs it does not re-derive the length inline.
    """
    out: dict[tuple, list[Screen]] = {}
    for geom, screens in iter_geometries(family, root=root, select=select):
        for s in screens:
            out.setdefault((key(s), geom), []).append(s)
    return out


def load_screens(geometry: Geometry, family: Family = _MISSING, *, root: str | None = None,
                 select=None, allow_empty: bool = False) -> ScreenSet:
    """Every artifact of `family` produced at EXACTLY `geometry`. The one call consumers make.

    ⛔ `geometry` IS POSITIONAL AND REQUIRED, AND THAT IS THE POINT OF THE SIGNATURE. A default
    would be taken by exactly the module that has not thought about geometry, and would be correct
    until the day it was not — which is the day this whole file exists to describe. Passing `None`
    is refused rather than treated as "any".

    ⚠ AND AN EMPTY RESULT RAISES BY DEFAULT. A consumer that silently measures nothing is the
    failure this repository keeps paying for; a consumer that legitimately tolerates absence
    (a geometry that has not been screened yet) says so with `allow_empty=True`.
    """
    if family is _MISSING:
        raise TypeError("load_screens(geometry, family) — name the artifact family explicitly; "
                        "the families are aso_screen_sets.FAMILIES")
    if geometry is None:
        raise GeometryError(
            "load_screens() was given geometry=None. There is no 'any geometry' load: applying one "
            "geometry's gap span to another's designs is the exact defect this loader exists to "
            "make unrepresentable. Name a Geometry, or use load_by_geometry() and handle each.")
    if not isinstance(geometry, Geometry):
        raise TypeError(f"geometry must be a Geometry, got {type(geometry).__name__}")
    by_geom = load_by_geometry(family, root=root, select=select)
    got = by_geom.get(geometry)
    if got is None:
        got = ScreenSet(geometry, family, [], HERE if root is None else root)
    if not got and not allow_empty:
        raise GeometryError(
            f"no {family.name} artifact in {os.path.basename(got.root)} was produced at {geometry!r} "
            f"(present: {sorted(by_geom) or 'none'}). Loading nothing and reporting a result over it "
            f"is worse than failing here; pass allow_empty=True if absence is a legitimate answer.")
    return got


# ═════════════════════════════════════════════════════════════════════════════════════════════
# Selectors — content predicates, offered here so five consumers do not write five copies
# ═════════════════════════════════════════════════════════════════════════════════════════════
def is_deep(screen: Screen) -> bool:
    """A screen run at a deeper alignment ceiling than the default, judged on CONTENT.

    ⚠ NOT `"deep500" in the filename`. Three spellings are already on disk (`-deep500`,
    `-clean9-deep500`, `-deep500-b2`) and the next campaign will choose a fourth. The evidence a
    pre-2026-08-13 screen carries is that retention EXCEEDED the default 15 on some design, which a
    default run cannot produce; a screen with a `parameters` block says so outright.
    """
    art = screen.artifact
    params = (art.get("method") or {}).get("parameters") or {}
    ceiling = params.get("blast_hitlist_size")
    if ceiling is not None:
        return int(ceiling) > _default_hitlist_size()
    stored = max((len(o.get("offtargets") or []) for o in (art.get("oligos") or [])), default=0)
    return stored > _default_saved_hits()


def is_default_depth(screen: Screen) -> bool:
    return not is_deep(screen)


#: A PRIMARY panel's name ends at the junction tag — `aso-insilico-evaluation-<tag>n3.json`.
#: ⛔ THIS ONE IS A FILENAME RULE AND SAYS SO, because the thing it selects has no other tell. A
#: re-screen at a deeper ceiling and the primary panel of the same seam are value-for-value
#: identical in every field this repository reads, so no content predicate can separate them; what
#: separates them is that one was emitted under a further suffix. It lives here, once, beside the
#: geometry measurement that makes it safe — a filename rule applied to a set already narrowed to
#: one measured geometry cannot do the damage the original glob did.
_PRIMARY_PANEL = re.compile(r"aso-insilico-evaluation-[a-z0-9]+n3\.json$")


def is_primary_panel(screen: Screen) -> bool:
    """The primary evaluation panel of a seam, not a re-emission of it under a further suffix."""
    return bool(_PRIMARY_PANEL.match(screen.name))


def _default_hitlist_size():
    try:
        import junction_aso_offtarget as jo   # noqa: PLC0415
        return int(jo.DEFAULT_BLAST_HITLIST_SIZE)
    except Exception:                         # noqa: BLE001
        return 50


def _default_saved_hits():
    try:
        import junction_aso_offtarget as jo   # noqa: PLC0415
        return int(jo.DEFAULT_SAVED_HITS_PER_DESIGN)
    except Exception:                         # noqa: BLE001
        return 15


def main(argv=None):
    """Print what is on disk, partitioned by family and MEASURED geometry. `python3 aso_screen_sets.py`"""
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    root = argv[0] if argv else HERE
    for family in FAMILIES:
        by = load_by_geometry(family, root=root)
        print(f"\n{family.name}  ({family._what})")
        if not by:
            print("    (none)")
        for geom, screens in sorted(by.items()):
            deep = sum(1 for s in screens if is_deep(s))
            print(f"    {geom!r:<34} n={len(screens):<4} deep={deep:<4} "
                  f"gap_region_1based={list(geom.gap_region_1based)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
