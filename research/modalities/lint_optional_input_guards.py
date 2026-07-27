#!/usr/bin/env python3
"""Find GitHub Actions guards that silently switch themselves off on an unattended trigger.

THE BUG CLASS (measured 2026-07-27, on `.github/workflows/step1-fanout-autoscale.yml`):

    if: ${{ github.event.inputs.release_fanout != '0' }}   # "place unless explicitly disabled"

A `schedule:` event carries NO `inputs` context, so that operand is `null`. GitHub Actions
comparison is LOOSE: when the operand types differ it casts BOTH to a number, and `null` casts
to `0` while `'0'` casts to `0`. The condition is therefore `0 != 0` -> FALSE, and the step is
skipped on exactly the unattended trigger it was written for. That guard disabled the
money-spending step of the step-1 fan-out for 1 h 47 m across seven green ticks; nothing in the
run said so, because a skipped step's only trace is a grey badge.

`||` does not have this problem (`github.event.inputs.x || 'default'` short-circuits on null),
which is why the same file's `fleet_branch` worked while `release_fanout` did not.

WHY THIS PARSES YAML INSTEAD OF GREPPING. A text grep for the expression false-positives on
comments and docstrings — and `step1-fanout-autoscale.yml` deliberately CONTAINS the broken
comparison, both in its incident comment and in an `env:` var (`OLD_EXPRESSION_RESULT`) that
prints the failing expression's real value on every run, as evidence. Comments are invisible to
`yaml.safe_load`, which is the whole reason this checker parses. The `env:` occurrence is
deliberate and lives in the ALLOWLIST below, with its reason.

USAGE
    python3 research/modalities/lint_optional_input_guards.py [paths...]

    Default target is `.github/workflows` relative to the repo root. Exit status is 1 if any
    un-allowlisted BUG-level finding survives, else 0. NOTE-level findings are printed for the
    record and never fail the build.

THE TWO CORRECT FIXES (both are used in the repo; pick by what the step does):

  1. Resolve the flag in bash, where empty is empty, and emit it via `$GITHUB_OUTPUT`:

         env:
           RAW: ${{ github.event.inputs.thing }}
         run: |
           v="${RAW}"; [ -n "$v" ] || v="1"
           echo "thing=${v}" >> "$GITHUB_OUTPUT"

     Use this for anything that spends money or destroys state: it leaves a printed record of
     what the inputs context actually held, which a YAML `if:` cannot do.

  2. Make the null case explicit in the expression itself, fine for cheap/idempotent steps:

         if: ${{ github.event.inputs.thing != '0' || github.event.inputs.thing == '' }}

     (`null == ''` is TRUE — both cast to 0 — so this is the default-ON form. The default-OFF
     form is `${{ ... != '0' && ... != '' }}`. They are not interchangeable; pick the one that
     matches the intent, and say which in a comment.)
"""

from __future__ import annotations

import glob
import math
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - the checker is useless without a parser
    sys.stderr.write(
        "lint_optional_input_guards: pyyaml is required (this checker parses YAML on purpose;\n"
        "a text grep cannot tell a live guard from the incident comment that documents one).\n"
    )
    raise


# --------------------------------------------------------------------------------------
# Allowlist
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Allow:
    """One deliberate, benign occurrence of the bug shape.

    A REASON is structurally required: a bare suppression is not expressible here. The point of
    the allowlist is to record WHY an occurrence is not a bug, so the next reader does not have
    to re-derive it (or, worse, "fix" a piece of evidence).
    """

    path: str  # matched against the workflow's basename or any path suffix
    expression: str  # the expression text, whitespace-normalised
    reason: str

    def __post_init__(self) -> None:
        if len(self.reason.strip()) < 20:
            raise ValueError(
                f"allowlist entry for {self.path} / {self.expression!r} needs a real REASON "
                "(>= 20 chars). A suppression with no reason is exactly the thing this checker "
                "exists to prevent."
            )

    def matches(self, path: str, expression: str) -> bool:
        norm_path = path.replace(os.sep, "/")
        if not (norm_path == self.path or norm_path.endswith("/" + self.path)):
            return False
        return normalise_expression(expression) == normalise_expression(self.expression)


ALLOWLIST: tuple[Allow, ...] = (
    Allow(
        path="step1-fanout-autoscale.yml",
        expression="github.event.inputs.release_fanout != '0'",
        reason=(
            "EVIDENCE, NOT A GUARD. This is the `OLD_EXPRESSION_RESULT` env var in the "
            "'Resolve the placement flag' step: it evaluates the expression that failed and "
            "PRINTS its value on every run, so the 1h47m incident never has to be re-derived "
            "from memory. It gates nothing — the real flag is resolved in bash below it and "
            "passed to the launcher as FANOUT_PLACEMENT_ENABLED. Rewriting it would delete the "
            "evidence. See that file's comment block at the step."
        ),
    ),
)


# --------------------------------------------------------------------------------------
# Expression tokenizer + parser (GitHub Actions expression language)
# --------------------------------------------------------------------------------------


class ExpressionSyntaxError(ValueError):
    """The expression could not be parsed. Reported, never silently swallowed."""


@dataclass(frozen=True)
class Token:
    kind: str  # 'ident' | 'string' | 'number' | 'op' | 'punc'
    text: str
    pos: int


_OPERATORS = ("==", "!=", "<=", ">=", "&&", "||", "<", ">", "!")
_PUNCTUATION = ("(", ")", "[", "]", ",", ".", "*")
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
_NUMBER_RE = re.compile(r"(?:0[xX][0-9a-fA-F]+|[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)")


def tokenize(src: str) -> list[Token]:
    tokens: list[Token] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "'":
            j = i + 1
            buf = []
            while True:
                if j >= n:
                    raise ExpressionSyntaxError(f"unterminated string literal at {i}")
                if src[j] == "'":
                    if j + 1 < n and src[j + 1] == "'":  # '' is an escaped quote
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(src[j])
                j += 1
            tokens.append(Token("string", "".join(buf), i))
            i = j + 1
            continue
        matched_op = next((op for op in _OPERATORS if src.startswith(op, i)), None)
        if matched_op is not None:
            tokens.append(Token("op", matched_op, i))
            i += len(matched_op)
            continue
        if ch in _PUNCTUATION:
            tokens.append(Token("punc", ch, i))
            i += 1
            continue
        m = _NUMBER_RE.match(src, i)
        if m and (ch.isdigit() or ch == "."):
            tokens.append(Token("number", m.group(0), i))
            i = m.end()
            continue
        m = _IDENT_RE.match(src, i)
        if m:
            tokens.append(Token("ident", m.group(0), i))
            i = m.end()
            continue
        raise ExpressionSyntaxError(f"unexpected character {ch!r} at {i} in {src!r}")
    return tokens


# --- AST nodes ------------------------------------------------------------------------


@dataclass(frozen=True)
class Literal:
    kind: str  # 'string' | 'number' | 'bool' | 'null'
    value: Any
    text: str


@dataclass(frozen=True)
class Path:
    """A context reference, e.g. `github.event.inputs.release_fanout`."""

    parts: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class Call:
    name: str
    args: tuple[Any, ...]
    text: str


@dataclass(frozen=True)
class Unary:
    op: str
    operand: Any
    text: str


@dataclass(frozen=True)
class Binary:
    op: str
    left: Any
    right: Any
    text: str


class _Parser:
    def __init__(self, tokens: Sequence[Token], src: str) -> None:
        self.tokens = list(tokens)
        self.src = src
        self.i = 0

    # -- helpers
    def peek(self) -> Token | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def take(self) -> Token:
        if self.i >= len(self.tokens):
            raise ExpressionSyntaxError(f"unexpected end of expression in {self.src!r}")
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def accept(self, kind: str, text: str) -> bool:
        tok = self.peek()
        if tok is not None and tok.kind == kind and tok.text == text:
            self.i += 1
            return True
        return False

    def expect(self, kind: str, text: str) -> Token:
        tok = self.take()
        if tok.kind != kind or tok.text != text:
            raise ExpressionSyntaxError(
                f"expected {text!r}, got {tok.text!r} at {tok.pos} in {self.src!r}"
            )
        return tok

    def _span(self, start: int) -> str:
        lo = self.tokens[start].pos
        end_tok = self.tokens[self.i - 1]
        hi = end_tok.pos + len(end_tok.text) + (2 if end_tok.kind == "string" else 0)
        return self.src[lo:hi].strip()

    # -- grammar
    def parse(self) -> Any:
        node = self.parse_or()
        if self.peek() is not None:
            tok = self.peek()
            raise ExpressionSyntaxError(
                f"trailing {tok.text!r} at {tok.pos} in {self.src!r}"  # type: ignore[union-attr]
            )
        return node

    def parse_or(self) -> Any:
        start = self.i
        node = self.parse_and()
        while self.accept("op", "||"):
            right = self.parse_and()
            node = Binary("||", node, right, self._span(start))
        return node

    def parse_and(self) -> Any:
        start = self.i
        node = self.parse_equality()
        while self.accept("op", "&&"):
            right = self.parse_equality()
            node = Binary("&&", node, right, self._span(start))
        return node

    def parse_equality(self) -> Any:
        start = self.i
        node = self.parse_relational()
        while True:
            tok = self.peek()
            if tok is not None and tok.kind == "op" and tok.text in ("==", "!="):
                self.i += 1
                right = self.parse_relational()
                node = Binary(tok.text, node, right, self._span(start))
                continue
            return node

    def parse_relational(self) -> Any:
        start = self.i
        node = self.parse_unary()
        while True:
            tok = self.peek()
            if tok is not None and tok.kind == "op" and tok.text in ("<", "<=", ">", ">="):
                self.i += 1
                right = self.parse_unary()
                node = Binary(tok.text, node, right, self._span(start))
                continue
            return node

    def parse_unary(self) -> Any:
        start = self.i
        if self.accept("op", "!"):
            operand = self.parse_unary()
            return Unary("!", operand, self._span(start))
        return self.parse_primary()

    def parse_primary(self) -> Any:
        start = self.i
        tok = self.take()
        if tok.kind == "punc" and tok.text == "(":
            node = self.parse_or()
            self.expect("punc", ")")
            return node
        if tok.kind == "string":
            return Literal("string", tok.text, tok.text)
        if tok.kind == "number":
            return Literal("number", _parse_number(tok.text), tok.text)
        if tok.kind == "ident":
            low = tok.text.lower()
            if low in ("true", "false"):
                return Literal("bool", low == "true", tok.text)
            if low == "null":
                return Literal("null", None, tok.text)
            nxt = self.peek()
            if nxt is not None and nxt.kind == "punc" and nxt.text == "(":
                self.take()
                args: list[Any] = []
                if not self.accept("punc", ")"):
                    while True:
                        args.append(self.parse_or())
                        if self.accept("punc", ","):
                            continue
                        self.expect("punc", ")")
                        break
                return Call(tok.text, tuple(args), self._span(start))
            parts = [tok.text]
            while True:
                if self.accept("punc", "."):
                    nxt = self.take()
                    if nxt.kind == "ident":
                        parts.append(nxt.text)
                    elif nxt.kind == "punc" and nxt.text == "*":
                        parts.append("*")
                    else:
                        raise ExpressionSyntaxError(
                            f"bad property name {nxt.text!r} at {nxt.pos} in {self.src!r}"
                        )
                    continue
                if self.accept("punc", "["):
                    index = self.parse_or()
                    self.expect("punc", "]")
                    parts.append(
                        index.value
                        if isinstance(index, Literal)
                        else f"[{getattr(index, 'text', '?')}]"
                    )
                    continue
                break
            return Path(tuple(str(p) for p in parts), self._span(start))
        raise ExpressionSyntaxError(f"unexpected token {tok.text!r} at {tok.pos} in {self.src!r}")


def _parse_number(text: str) -> float:
    if text.lower().startswith("0x"):
        return float(int(text, 16))
    return float(text)


def parse_expression(src: str) -> Any:
    return _Parser(tokenize(src), src).parse()


def walk(node: Any) -> Iterator[Any]:
    yield node
    if isinstance(node, Binary):
        yield from walk(node.left)
        yield from walk(node.right)
    elif isinstance(node, Unary):
        yield from walk(node.operand)
    elif isinstance(node, Call):
        for arg in node.args:
            yield from walk(arg)


# --------------------------------------------------------------------------------------
# Actions coercion semantics
# --------------------------------------------------------------------------------------


def string_to_number(text: str) -> float:
    """GitHub's string -> number cast. Non-numeric strings become NaN; '' becomes 0."""
    if text.strip() == "":
        return 0.0
    try:
        return float(text)
    except ValueError:
        pass
    try:
        return float(int(text, 0))
    except ValueError:
        return math.nan


def literal_to_number(node: "Literal") -> float:
    """The number an `==`/`!=` comparand casts to when the other side is null."""
    if node.kind == "string":
        return string_to_number(node.value)
    if node.kind == "number":
        return float(node.value)
    if node.kind == "bool":
        return 1.0 if node.value else 0.0
    return 0.0  # null == null is an identity comparison; treated as 0 for the report


def compare_null_against_literal(op: str, node: "Literal") -> bool:
    """Evaluate `null <op> <literal>` exactly as the Actions expression evaluator does.

    Types differ, so both sides cast to number: `null` -> 0, the comparand via the rules above.
    `!=` is `not (==)`, which is how the runner implements it, so a NaN comparand makes `==`
    false and `!=` true.
    """
    lit = literal_to_number(node)
    equal = False if math.isnan(lit) else (0.0 == lit)
    return equal if op == "==" else not equal


# --------------------------------------------------------------------------------------
# Workflow model
# --------------------------------------------------------------------------------------

INPUT_PATH_PREFIXES = (
    ("github", "event", "inputs"),
    ("inputs",),
)


def input_name(node: Any) -> str | None:
    """Return the input name if `node` is a reference to a workflow input, else None."""
    if not isinstance(node, Path):
        return None
    for prefix in INPUT_PATH_PREFIXES:
        if node.parts[: len(prefix)] == prefix and len(node.parts) == len(prefix) + 1:
            return node.parts[len(prefix)]
    return None


@dataclass
class WorkflowFacts:
    path: str
    triggers: tuple[str, ...] = ()
    # input name -> (required, has_default)
    inputs: dict[str, tuple[bool, bool]] = field(default_factory=dict)
    parse_error: str | None = None

    @property
    def inputless_triggers(self) -> tuple[str, ...]:
        """Triggers that carry NO `inputs` context at all — where every input reads as null."""
        return tuple(t for t in self.triggers if t not in ("workflow_dispatch", "workflow_call"))

    def can_be_null(self, name: str) -> tuple[bool, str]:
        """Can `inputs.<name>` read as null/empty at evaluation time? Plus the reason why."""
        bare = self.inputless_triggers
        if bare:
            return True, (
                f"the workflow also triggers on {', '.join(sorted(set(bare)))}, which carries no "
                "`inputs` context at all — the operand is null there even though the input "
                "declares a default"
            )
        if name not in self.inputs:
            return True, "the input is not declared in this workflow, so it is always null here"
        required, has_default = self.inputs[name]
        if required:
            return False, "the input is `required: true` on a dispatch-only workflow"
        if has_default:
            return False, "the input has a `default:` and every trigger supplies an inputs context"
        return (
            True,
            "the input is optional with no `default:`, so an omitted dispatch leaves it empty",
        )


def _trigger_names(on_value: Any) -> tuple[str, ...]:
    if isinstance(on_value, str):
        return (on_value,)
    if isinstance(on_value, list):
        return tuple(str(v) for v in on_value)
    if isinstance(on_value, dict):
        return tuple(str(k) for k in on_value)
    return ()


def _collect_inputs(on_value: Any) -> dict[str, tuple[bool, bool]]:
    out: dict[str, tuple[bool, bool]] = {}
    if not isinstance(on_value, dict):
        return out
    for trigger in ("workflow_dispatch", "workflow_call"):
        block = on_value.get(trigger)
        if not isinstance(block, dict):
            continue
        declared = block.get("inputs")
        if not isinstance(declared, dict):
            continue
        for name, spec in declared.items():
            spec = spec if isinstance(spec, dict) else {}
            required = bool(spec.get("required", False))
            has_default = "default" in spec
            prev = out.get(str(name))
            if prev is not None:
                required = required or prev[0]
                has_default = has_default or prev[1]
            out[str(name)] = (required, has_default)
    return out


def read_workflow(path: str) -> tuple[WorkflowFacts, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return WorkflowFacts(path=path, parse_error=str(exc).splitlines()[0]), None
    if not isinstance(doc, dict):
        return WorkflowFacts(path=path, parse_error="top level is not a mapping"), None
    # `on` is YAML 1.1 boolean-ish: pyyaml loads the unquoted key as True.
    on_value = doc.get("on", doc.get(True))
    facts = WorkflowFacts(
        path=path,
        triggers=_trigger_names(on_value),
        inputs=_collect_inputs(on_value),
    )
    return facts, doc


# --------------------------------------------------------------------------------------
# Extraction: every `${{ }}` expression, with the YAML location that carries it
# --------------------------------------------------------------------------------------

_TEMPLATE_RE = re.compile(r"\$\{\{(.*?)\}\}", re.DOTALL)


@dataclass(frozen=True)
class Site:
    """One expression, and where in the parsed YAML it lives."""

    job: str
    step: str
    key: str  # the YAML key holding it, e.g. 'if', 'env.RAW_X', 'with.foo'
    expression: str
    is_condition: bool


def normalise_expression(expr: str) -> str:
    return re.sub(r"\s+", " ", expr).strip()


def extract_expressions(value: str, is_condition: bool) -> list[str]:
    """Pull the expression bodies out of a YAML scalar.

    An `if:` may omit the `${{ }}` wrapper entirely — GitHub allows a bare expression there —
    so a condition with no template markers is taken whole.
    """
    found = [m.group(1) for m in _TEMPLATE_RE.finditer(value)]
    if found:
        return found
    if is_condition and value.strip():
        return [value]
    return []


def _step_label(step: Any, index: int) -> str:
    if isinstance(step, dict):
        name = step.get("name") or step.get("id") or step.get("uses")
        if name:
            return f"step[{index}] {str(name).strip()[:60]}"
    return f"step[{index}]"


def collect_sites(doc: Any) -> list[Site]:
    """Walk the parsed workflow and collect every expression-bearing scalar.

    Comments are already gone — `yaml.safe_load` never saw them — which is the entire reason
    this is a parser and not a grep.
    """
    sites: list[Site] = []

    def scalar(job: str, step: str, key: str, value: Any) -> None:
        if not isinstance(value, str):
            return
        is_condition = key == "if" or key.endswith(".if")
        for expr in extract_expressions(value, is_condition):
            sites.append(Site(job, step, key, expr, is_condition))

    def walk_value(job: str, step: str, key: str, value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                walk_value(job, step, f"{key}.{k}" if key else str(k), v)
        elif isinstance(value, list):
            for idx, v in enumerate(value):
                walk_value(job, step, f"{key}[{idx}]", v)
        else:
            scalar(job, step, key, value)

    if not isinstance(doc, dict):
        return sites

    for key, value in doc.items():
        if key == "jobs":
            continue
        walk_value("<workflow>", "-", str(key), value)

    jobs = doc.get("jobs")
    if isinstance(jobs, dict):
        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                continue
            for key, value in job.items():
                if key == "steps":
                    continue
                walk_value(str(job_id), "-", str(key), value)
            steps = job.get("steps")
            if isinstance(steps, list):
                for idx, step in enumerate(steps):
                    label = _step_label(step, idx)
                    if isinstance(step, dict):
                        for key, value in step.items():
                            walk_value(str(job_id), label, str(key), value)
                    else:
                        walk_value(str(job_id), label, "", step)
    return sites


# --------------------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------------------

SEVERITY_BUG = "BUG"
SEVERITY_NOTE = "NOTE"


@dataclass(frozen=True)
class Finding:
    path: str
    job: str
    step: str
    key: str
    expression: str  # the offending comparison
    full_expression: str  # the whole expression it sits in
    severity: str
    why: str
    should_be: str
    allowlisted: bool = False
    allow_reason: str = ""

    def render(self) -> str:
        head = f"{self.path}:{self.job}:{self.step} [{self.key}]"
        lines = [
            f"{'ALLOWED' if self.allowlisted else self.severity:<7} {head}",
            f"          expression   {self.expression}",
        ]
        if normalise_expression(self.full_expression) != normalise_expression(self.expression):
            lines.append(f"          within       {normalise_expression(self.full_expression)}")
        lines.append(f"          why wrong    {self.why}")
        lines.append(f"          should be    {self.should_be}")
        if self.allowlisted:
            lines.append(f"          allowlisted  {self.allow_reason}")
        return "\n".join(lines)


def _has_explicit_empty_guard(root: Any, name: str, exclude: Any) -> bool:
    """Did the author explicitly compare this same input against '' SOMEWHERE ELSE in the guard?

    That is one of the two sanctioned fixes, so it means the null case was considered. The
    comparison under examination is excluded, or every `X != ''` would vacuously excuse itself.
    """
    for node in walk(root):
        if node is exclude:
            continue
        if isinstance(node, Binary) and node.op in ("==", "!="):
            for a, b in ((node.left, node.right), (node.right, node.left)):
                if input_name(a) == name and isinstance(b, Literal) and b.kind == "string":
                    if b.value == "":
                        return True
    return False


# NOTE: `||` needs no special case. `${{ (github.event.inputs.x || '1') != '0' }}` puts the
# `||` node — not the input path — on the left of the comparison, so `input_name()` returns
# None and the comparison is structurally out of scope. That is the whole reason the defaulted
# form is safe, and encoding it as a suppression list would only risk masking a sibling
# comparison in the same expression that was NOT defaulted.


def analyse_expression(
    facts: WorkflowFacts, site: Site, env_names_used_in_conditions: set[str]
) -> list[Finding]:
    try:
        root = parse_expression(site.expression)
    except ExpressionSyntaxError as exc:
        return [
            Finding(
                path=facts.path,
                job=site.job,
                step=site.step,
                key=site.key,
                expression=normalise_expression(site.expression),
                full_expression=normalise_expression(site.expression),
                severity=SEVERITY_NOTE,
                why=f"could not parse this expression ({exc}); it was NOT analysed",
                should_be="teach the checker this syntax rather than leaving a blind spot",
            )
        ]

    findings: list[Finding] = []

    for node in walk(root):
        if not (isinstance(node, Binary) and node.op in ("==", "!=")):
            continue
        for operand, other in ((node.left, node.right), (node.right, node.left)):
            name = input_name(operand)
            if name is None:
                continue
            # A string is the usual comparand, but `!= 0` and `!= false` coerce identically and
            # are the same trap wearing different clothes.
            if not (isinstance(other, Literal) and other.kind in ("string", "number", "bool")):
                continue
            nullable, null_reason = facts.can_be_null(name)
            if not nullable:
                continue

            lit_num = literal_to_number(other)
            result = compare_null_against_literal(node.op, other)
            casts_to_zero = (not math.isnan(lit_num)) and lit_num == 0.0
            is_empty_string = other.kind == "string" and other.value == ""
            explicit = _has_explicit_empty_guard(root, name, exclude=node)
            shown = f"'{other.value}'" if other.kind == "string" else other.text

            cast_shown = 0 if casts_to_zero else ("NaN" if math.isnan(lit_num) else lit_num)
            why = (
                f"`{operand.text}` is null when absent — {null_reason}. Loose comparison casts "
                f"both operands to a number: null -> 0 and {shown} casts to {cast_shown}, so "
                f"`{normalise_expression(node.text)}` evaluates to {result} on that trigger."
            )

            if is_empty_string:
                # `X != ''` / `X == ''` IS the null test. null and '' both cast to 0, so the
                # comparison means exactly "was a value supplied?" — which is what it reads as.
                why += (
                    " Comparing against '' is the correct idiom for an optional input: null and "
                    "'' cast alike, so the test means exactly \"was a value supplied\"."
                )
                should_be = "no change — this is the null test, not a victim of it"
                severity = SEVERITY_NOTE
            elif casts_to_zero and not explicit:
                # The dangerous shapes. `!= '0'` reads as "unless explicitly disabled" and is
                # FALSE exactly when nobody typed anything; `== '0'` reads as "only when
                # explicitly zero" and is TRUE exactly then.
                if node.op == "!=":
                    why += (
                        " The guard therefore switches OFF on precisely the unattended trigger "
                        "it was written for, leaving only a grey `skipped` badge as its trace."
                    )
                else:
                    why += (
                        " The branch therefore fires on precisely the unattended trigger, even "
                        "though nobody asked for it."
                    )
                should_be = (
                    'resolve the flag in a `run:` bash step (`v="$RAW"; [ -n "$v" ] || '
                    'v="<default>"`) and emit it via $GITHUB_OUTPUT, or make the null case '
                    f"explicit: `{operand.text} {node.op} {shown} "
                    f"{'||' if node.op == '!=' else '&&'} {operand.text} "
                    f"{'==' if node.op == '!=' else '!='} ''`"
                )
                severity = SEVERITY_BUG
            elif casts_to_zero and explicit:
                why += (
                    " The author compared this input against '' in the same expression, so the "
                    "null case is handled deliberately."
                )
                should_be = "no change — the null case is explicit"
                severity = SEVERITY_NOTE
            else:
                why += (
                    " A comparand that does not cast to 0 leaves the guard reading the way it "
                    "looks (absent means 'not this mode'), which is the usual intent, so this is "
                    "reported for the record only."
                )
                should_be = "no change expected — confirm the default matches the intent"
                severity = SEVERITY_NOTE

            if severity == SEVERITY_BUG and not site.is_condition:
                # A data scalar (env:/with:) is only a live guard if something later reads it in
                # a condition. Otherwise it is a value the *program* interprets, where null is
                # visible as an empty string rather than silently coerced.
                env_var = site.key.split(".")[-1]
                if env_var not in env_names_used_in_conditions:
                    severity = SEVERITY_NOTE
                    why += (
                        f" It sits in `{site.key}`, not a condition, and no `if:` in this "
                        f"workflow reads `env.{env_var}`, so nothing is gated on it here — "
                        "the consuming program sees the empty value directly."
                    )

            findings.append(
                Finding(
                    path=facts.path,
                    job=site.job,
                    step=site.step,
                    key=site.key,
                    expression=normalise_expression(node.text),
                    full_expression=site.expression,
                    severity=severity,
                    why=why,
                    should_be=should_be,
                )
            )
    return findings


_ENV_REF_RE = re.compile(r"\benv\.([A-Za-z_][A-Za-z0-9_\-]*)")


def scan_workflow(path: str, allowlist: Sequence[Allow] = ALLOWLIST) -> tuple[list[Finding], int]:
    """Return (findings, number of expressions analysed) for one workflow file."""
    facts, doc = read_workflow(path)
    if facts.parse_error is not None:
        return (
            [
                Finding(
                    path=path,
                    job="-",
                    step="-",
                    key="<file>",
                    expression="",
                    full_expression="",
                    severity=SEVERITY_BUG,
                    why=f"the workflow could not be parsed as YAML: {facts.parse_error}",
                    should_be="fix the YAML so the guard sweep can actually see this file",
                )
            ],
            0,
        )

    sites = collect_sites(doc)
    env_names_used_in_conditions: set[str] = set()
    for site in sites:
        if site.is_condition:
            env_names_used_in_conditions.update(_ENV_REF_RE.findall(site.expression))

    findings: list[Finding] = []
    for site in sites:
        findings.extend(analyse_expression(facts, site, env_names_used_in_conditions))

    resolved: list[Finding] = []
    for finding in findings:
        allow = next((a for a in allowlist if a.matches(path, finding.expression)), None)
        if allow is not None:
            resolved.append(
                Finding(**{**finding.__dict__, "allowlisted": True, "allow_reason": allow.reason})
            )
        else:
            resolved.append(finding)
    return resolved, len(sites)


def iter_workflow_files(targets: Iterable[str]) -> list[str]:
    out: list[str] = []
    for target in targets:
        if os.path.isdir(target):
            out.extend(sorted(glob.glob(os.path.join(target, "*.yml"))))
            out.extend(sorted(glob.glob(os.path.join(target, "*.yaml"))))
        else:
            out.append(target)
    return sorted(set(out))


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv: Sequence[str]) -> int:
    targets = list(argv[1:]) or [os.path.join(repo_root(), ".github", "workflows")]
    files = iter_workflow_files(targets)

    all_findings: list[Finding] = []
    expressions = 0
    for path in files:
        found, count = scan_workflow(path)
        expressions += count
        all_findings.extend(found)

    bugs = [f for f in all_findings if f.severity == SEVERITY_BUG and not f.allowlisted]
    notes = [f for f in all_findings if f.severity == SEVERITY_NOTE and not f.allowlisted]
    allowed = [f for f in all_findings if f.allowlisted]

    print("=" * 96)
    print(
        "optional-input guard sweep — `null != '0'` is FALSE, and that is how a guard turns itself off"
    )
    print("=" * 96)
    print(f"workflows parsed      {len(files)}")
    print(f"expressions analysed  {expressions}")
    print(f"findings              {len(bugs)} BUG · {len(notes)} NOTE · {len(allowed)} allowlisted")
    print()

    for group, title in ((bugs, "BUG"), (notes, "NOTE"), (allowed, "ALLOWLISTED")):
        if not group:
            continue
        print(f"--- {title} ({len(group)}) " + "-" * (80 - len(title)))
        for finding in group:
            print(finding.render())
            print()

    if bugs:
        print(f"FAIL — {len(bugs)} un-allowlisted guard(s) evaluate against a null input.")
        return 1
    print("OK — no un-allowlisted optional-input guard inverts on a null inputs context.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
