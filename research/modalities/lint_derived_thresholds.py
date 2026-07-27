#!/usr/bin/env python3
"""Find gates typed as a MULTIPLE of a moving basis, instead of derived from the approved rate.

THE BUG CLASS (CLAUDE.md §1, ruling of 2026-07-27).

The buy/drift line is an ABSOLUTE rate — `$0.006539/ns` — and the multiple of the ladder basis is
DERIVED from it. It was not always written that way. On 2026-07-27 the throughput table was
re-anchored and widened (the reference card's measured throughput rose; 97 more offers became
gradeable), so the ladder basis fell 22 %, from a now-superseded `$0.004359/ns` to `$0.003412/ns`.
**No price moved. The yardstick did.**

Every guard that had been typed as `>= 1.5 * basis` or `x_basis >= 1.5` then meant a ~22 % STRICTER
rule than the one that was agreed, and boards that had been passing began to fail — a rule change
nobody decided and nothing announced. `1.5 × $0.004359` and `1.92 × $0.003412` are the same dollars
per nanosecond; only the denominator moved.

So the invariant is the absolute rate, and the multiple falls out of it:

    inflight_usd_per_ns.APPROVED_USD_PER_NS      the approved rate — the invariant
    inflight_usd_per_ns.drift_multiple()         that rate ÷ the CURRENT basis
    congeneric_fanout.unit_rate_line_usd_per_ns()  the §1 rate line, absolute
    congeneric_fanout.drift_buy_line_x_basis()     the same line as a multiple
    congeneric_fanout.basis_usd_per_ns()           the current basis itself

A literal typed anywhere in that family is a number that will be wrong the next time the basis is
corrected, and wrong SILENTLY — which is exactly what happened three times in one day.

WHAT THIS FLAGS. Via `ast`, not grep (a docstring quoting `1.5 * basis` as the superseded form is
evidence, and this file's own module docstring would trip a grep):

  * `ast.Compare` with a numeric literal on one side and a cost-basis quantity on the other
    — `if x_basis >= 1.5:`
  * `ast.BinOp` multiplying a numeric literal into such a quantity — `1.5 * basis`
  * `ast.Assign` of a numeric literal to a cost-basis name — `MAX_RATIO_VS_BASIS = 2.25`
  * a keyword argument of a cost-basis name given a numeric literal — `max_usd_per_ns=0.0065`

WHAT IT DELIBERATELY DOES NOT FLAG, and why each exemption exists:

  * `0` and `1` — neutral/identity, never a threshold.
  * TOLERANCES — `abs(a - b) < 1e-12`. The literal is a precision bound, not a rule.
  * ROUND-TRIPS — a literal written INTO a fixture and then asserted back out in the same
    function. `record(gate={"ratio_vs_basis": 1.261}); assert row["gate_ratio_vs_basis"] == 1.261`
    tests plumbing; it has no coupling to the live basis at all.
  * A NARROW vocabulary. An earlier draft matched any name containing `threshold`, `drift`,
    `ceiling` or `per_ns`, and immediately "found" `LOEUF_THRESHOLD = 0.35`, `PS_PER_NS = 1000.0`
    and `ENDPOINT_DRIFT_SIGMA = 4.0` — none of which have anything to do with dollars per
    nanosecond. A checker that cries wolf about genetics constants gets switched off, so the
    vocabulary is restricted to the cost-basis family and listed in `COST_BASIS_TOKENS`.

SEVERITY. Production modules are BUG (they decide real spend). Files under `tests/` are NOTE: a
test literal is usually a PIN, and pins are supposed to be typed — but a pin typed against a
moving basis still needs re-deriving when the basis moves, so it is listed rather than silenced.

USAGE
    python3 research/modalities/lint_derived_thresholds.py [paths...]
    Exit 1 on any un-allowlisted BUG. NOTE never fails the build.
"""

from __future__ import annotations

import ast
import glob
import os
import re
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence

# --------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------

#: Substrings that mark a name as belonging to the $/ns ladder-basis family. Deliberately narrow
#: — see the docstring for the false positives that a loose list produced.
COST_BASIS_TOKENS = (
    "basis",
    "usd_per_ns",
    "buy_line",
    "rate_line",
    "drift_multiple",
    "approved_usd",
    "ceiling_usd",
    "usd_ceiling",
    "market_ceiling",
)

#: The accessors that already do the derivation. A finding's remedy is always "call one of these".
DERIVED_ACCESSORS = (
    "APPROVED_USD_PER_NS",
    "drift_multiple",
    "drift_buy_line_x_basis",
    "unit_rate_line_usd_per_ns",
    "unit_usd_per_ns_ceiling",
    "unit_ceiling_components",
    "basis_usd_per_ns",
    "MAX_RATIO_VS_BASIS",
)

_TOKEN_RE = re.compile("|".join(re.escape(t) for t in COST_BASIS_TOKENS), re.IGNORECASE)
_DERIVED_RE = re.compile("|".join(re.escape(t) for t in DERIVED_ACCESSORS))

#: Literals that are never a threshold: the additive and multiplicative identities.
NEUTRAL_LITERALS = (0, 1, 0.0, 1.0, -1, -1.0)


def mentions_cost_basis(source: str) -> bool:
    return bool(_TOKEN_RE.search(source))


def mentions_derived_accessor(source: str) -> bool:
    return bool(_DERIVED_RE.search(source))


def suggested_accessor(source: str) -> str:
    """The accessor a given site should be calling instead of carrying a literal."""
    low = source.lower()
    if "x_basis" in low or "ratio_vs_basis" in low or "multiple" in low:
        return (
            "congeneric_fanout.drift_buy_line_x_basis() "
            "(= inflight_usd_per_ns.drift_multiple(), derived against the CURRENT basis)"
        )
    if "ceiling" in low:
        return "congeneric_fanout.unit_ceiling_components() / unit_usd_per_ns_ceiling()"
    if "usd_per_ns" in low or "rate_line" in low or "buy_line" in low:
        return (
            "congeneric_fanout.unit_rate_line_usd_per_ns() "
            "(= inflight_usd_per_ns.APPROVED_USD_PER_NS, the invariant)"
        )
    return "congeneric_fanout.basis_usd_per_ns() — derive it, do not type it"


# --------------------------------------------------------------------------------------
# Allowlist
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Allow:
    """One deliberately-typed literal. A REASON is structurally required."""

    path: str  # basename or any path suffix
    expression: str
    reason: str

    def __post_init__(self) -> None:
        if len(self.reason.strip()) < 20:
            raise ValueError(
                f"allowlist entry for {self.path} / {self.expression!r} needs a real REASON "
                "(>= 20 chars). A typed threshold with no stated reason is the bug itself."
            )

    def matches(self, path: str, expression: str) -> bool:
        norm = path.replace(os.sep, "/")
        if not (norm == self.path or norm.endswith("/" + self.path)):
            return False
        return " ".join(expression.split()) == " ".join(self.expression.split())


ALLOWLIST: tuple[Allow, ...] = (
    Allow(
        path="tests/test_buy_line_invariant.py",
        expression="1.5 * old_basis",
        reason=(
            "THE HISTORICAL IDENTITY, and it must stay typed. This test proves that '1.5x' against "
            "the SUPERSEDED basis and '1.92x' against the current one are the same dollars per "
            "nanosecond — the claim CLAUDE.md §1 makes to show the re-expression was not a "
            "loosening. Deriving either side would make the test assert its own premise and prove "
            "nothing. The retired constants are registered in pinned-figures.json."
        ),
    ),
)


# --------------------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------------------

SEVERITY_BUG = "BUG"
SEVERITY_NOTE = "NOTE"


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    shape: str  # COMPARE | MULT | ASSIGN | KWARG
    expression: str
    literal: float
    severity: str
    why: str
    should_be: str
    allowlisted: bool = False
    allow_reason: str = ""

    def render(self) -> str:
        head = f"{self.path}:{self.line}"
        lines = [
            f"{'ALLOWED' if self.allowlisted else self.severity:<7} {head}  [{self.shape}]",
            f"          expression   {self.expression}",
            f"          why wrong    {self.why}",
            f"          should be    {self.should_be}",
        ]
        if self.allowlisted:
            lines.append(f"          allowlisted  {self.allow_reason}")
        return "\n".join(lines)


# --------------------------------------------------------------------------------------
# Structural exemptions
# --------------------------------------------------------------------------------------


def _is_numeric_literal(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    )


def _is_tolerance(compare: ast.Compare, literal: ast.Constant) -> bool:
    """`abs(a - b) < tol` — the literal bounds precision, it does not encode a rule.

    The shape is required to be a DIFFERENCE inside `abs()`, which is what makes it unambiguous:
    `abs(rate) < 0.0065` would be a real threshold wearing a tolerance's clothes, and is not
    exempted. Magnitude is deliberately not part of the test — `abs(a - b) < 0.2` on a
    percentage is as much a tolerance as `< 1e-12` on a rate.
    """
    if not compare.ops or not isinstance(compare.ops[0], (ast.Lt, ast.LtE)):
        return False
    if compare.comparators and compare.comparators[-1] is not literal:
        return False
    left = compare.left
    if not (isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == "abs"):
        return False
    return (
        len(left.args) == 1
        and isinstance(left.args[0], ast.BinOp)
        and isinstance(left.args[0].op, ast.Sub)
    )


def _round_trip_literals(func: ast.AST) -> set[float]:
    """Literals that this function both WRITES and READS BACK.

    `record(gate={"ratio_vs_basis": 1.261}); assert row["gate_ratio_vs_basis"] == 1.261` asserts
    plumbing: the value never touches the live basis, so re-anchoring cannot invalidate it.
    A literal counts as round-tripped when it also appears outside a comparison in the same body.
    """
    written: set[float] = set()
    compared: set[float] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Compare):
            for operand in [node.left] + list(node.comparators):
                if _is_numeric_literal(operand):
                    compared.add(float(operand.value))
    for node in ast.walk(func):
        if isinstance(node, ast.Compare):
            continue
        for child in ast.iter_child_nodes(node):
            if _is_numeric_literal(child) and not isinstance(node, ast.Compare):
                written.add(float(child.value))
    return written & compared


def _enclosing_functions(tree: ast.AST) -> list[ast.AST]:
    return [
        n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


# --------------------------------------------------------------------------------------
# Scan
# --------------------------------------------------------------------------------------


def is_test_file(path: str) -> bool:
    norm = path.replace(os.sep, "/")
    return "/tests/" in norm or os.path.basename(norm).startswith("test_")


def scan_file(path: str, allowlist: Sequence[Allow] = ALLOWLIST) -> list[Finding]:
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [
            Finding(
                path=path,
                line=exc.lineno or 0,
                shape="PARSE",
                expression="",
                literal=0.0,
                severity=SEVERITY_BUG,
                why=f"the file could not be parsed as Python: {exc.msg}",
                should_be="fix the syntax so the threshold sweep can see this file",
            )
        ]

    test_file = is_test_file(path)
    round_trip: set[float] = set()
    for func in _enclosing_functions(tree):
        round_trip |= _round_trip_literals(func)

    raw: list[Finding] = []
    seen: set[tuple[int, str]] = set()

    def add(node: ast.AST, shape: str, expression: str, literal: float, other_src: str) -> None:
        key = (getattr(node, "lineno", 0), expression)
        if key in seen:
            return
        seen.add(key)
        why = (
            f"`{literal:g}` is typed against a cost-basis quantity. The ladder basis is a "
            "CORRECTABLE denominator — it fell 22 % on 2026-07-27 with no price moving — so a "
            "literal here silently becomes a different rule the next time the basis is re-anchored."
        )
        severity = SEVERITY_NOTE if test_file else SEVERITY_BUG
        if test_file:
            why += (
                " It is in a test, where a typed value is usually a deliberate PIN, so this is "
                "listed rather than failed — but it still needs re-deriving when the basis moves."
            )
        raw.append(
            Finding(
                path=path,
                line=getattr(node, "lineno", 0),
                shape=shape,
                expression=expression,
                literal=literal,
                severity=severity,
                why=why,
                should_be=f"call {suggested_accessor(other_src or expression)}",
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            operands = [node.left] + list(node.comparators)
            for index, operand in enumerate(operands):
                if not _is_numeric_literal(operand) or operand.value in NEUTRAL_LITERALS:
                    continue
                if _is_tolerance(node, operand):
                    continue
                if float(operand.value) in round_trip:
                    continue
                others = [
                    ast.unparse(o) for j, o in enumerate(operands) if j != index
                ]
                # ANCHORED TO A DERIVATION is the correct shape, not the bug: `x <= approved *
                # 1.001` and `assert v == pytest.approx(drift_multiple())` both move WITH the
                # basis. Only a literal standing on its own against a raw basis quantity is stale.
                if any(mentions_derived_accessor(o) for o in others):
                    continue
                if any(mentions_cost_basis(o) for o in others):
                    add(node, "COMPARE", ast.unparse(node), float(operand.value), " ".join(others))

        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            for literal, other in ((node.left, node.right), (node.right, node.left)):
                if not _is_numeric_literal(literal) or literal.value in NEUTRAL_LITERALS:
                    continue
                other_src = ast.unparse(other)
                if mentions_derived_accessor(other_src):
                    continue  # a relative perturbation OF the derived rate — moves with it
                if mentions_cost_basis(other_src):
                    add(node, "MULT", ast.unparse(node), float(literal.value), other_src)

        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [ast.unparse(t) for t in targets]
            value = node.value
            if value is not None and _is_numeric_literal(value):
                if value.value in NEUTRAL_LITERALS:
                    continue
                if any(mentions_cost_basis(n) for n in names):
                    add(node, "ASSIGN", ast.unparse(node), float(value.value), " ".join(names))

        elif isinstance(node, ast.keyword):
            if (
                node.arg
                and mentions_cost_basis(node.arg)
                and _is_numeric_literal(node.value)
                and node.value.value not in NEUTRAL_LITERALS
                and float(node.value.value) not in round_trip
            ):
                add(
                    node.value,
                    "KWARG",
                    f"{node.arg}={ast.unparse(node.value)}",
                    float(node.value.value),
                    node.arg,
                )

    resolved: list[Finding] = []
    for finding in raw:
        allow = next((a for a in allowlist if a.matches(path, finding.expression)), None)
        if allow is None:
            resolved.append(finding)
        else:
            resolved.append(
                Finding(**{**finding.__dict__, "allowlisted": True, "allow_reason": allow.reason})
            )
    return resolved


def iter_python_files(targets: Iterable[str]) -> list[str]:
    out: list[str] = []
    for target in targets:
        if os.path.isdir(target):
            out.extend(glob.glob(os.path.join(target, "**", "*.py"), recursive=True))
        else:
            out.append(target)
    return sorted(set(out))


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv: Sequence[str]) -> int:
    targets = list(argv[1:]) or [os.path.join(repo_root(), "research", "modalities")]
    files = iter_python_files(targets)

    findings: list[Finding] = []
    for path in files:
        if os.path.basename(path) == os.path.basename(__file__):
            continue  # this module's own docstring quotes the bad forms as evidence
        findings.extend(scan_file(path))

    bugs = [f for f in findings if f.severity == SEVERITY_BUG and not f.allowlisted]
    notes = [f for f in findings if f.severity == SEVERITY_NOTE and not f.allowlisted]
    allowed = [f for f in findings if f.allowlisted]

    print("=" * 96)
    print("derived-threshold sweep — a multiple of a correctable denominator is not a rule, it is a drift")
    print("=" * 96)
    print(f"python files parsed   {len(files)}")
    print(f"findings              {len(bugs)} BUG · {len(notes)} NOTE · {len(allowed)} allowlisted")
    print()

    for group, title in ((bugs, "BUG"), (notes, "NOTE (tests — pins, listed not failed)"), (allowed, "ALLOWLISTED")):
        if not group:
            continue
        print(f"--- {title} ({len(group)}) " + "-" * max(4, 70 - len(title)))
        for finding in group:
            print(finding.render())
            print()

    if bugs:
        print(f"FAIL — {len(bugs)} typed threshold(s) against a moving basis.")
        return 1
    print("OK — no production module types a multiple of the ladder basis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
