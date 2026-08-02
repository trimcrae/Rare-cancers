"""A supervision loop that reaps without re-placing is a slow leak, not supervision.

★★ MEASURED 2026-08-01. The sensitivity-control watch collected, reaped and published every 3 minutes and
never dispatched `launch`. Because the reaper destroys a host as soon as its leg banks, every landed leg
removes a host and nothing puts one back — so the panel could only ever converge if all 24 units banked on
their first attempt. They do not.

    6:13 PM  24 of 24 units covered — 5 landed, 19 live
    6:26 PM   8 landed, 11 live, 3 reaped  ->  **5 units with neither a result nor a host**

The watch was green throughout. An agent noticed and hand-dispatched `launch` three times, which is exactly
the dependency CLAUDE.md §6 forbids: "while any fleet is billing, YOU are the supervisor" is a statement of
what went wrong, not a design.

⚠ THE OPPOSITE FAILURE IS THE EXPENSIVE ONE and is why `_REPLACE_MIN_S` exists. A host rented seconds ago is
not yet on the account, so the next tick's `need` computation still counts its unit as bare. Without the
interval the loop would re-rent the same units every 3 minutes — paying repeatedly for one leg. Both
directions are pinned here.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
if MOD not in sys.path:
    sys.path.insert(0, MOD)

import selcal_vast_launch as L  # noqa: E402

SRC = open(os.path.join(MOD, "selcal_vast_launch.py")).read()


def _watch_body():
    body = SRC[SRC.index("def mode_watch("):]
    return body[:body.index("\ndef ", 10)]


def test_the_watch_dispatches_launch_for_units_with_no_result_and_no_host():
    """THE REGRESSION. Without this the panel stalls with a green watch running over the hole."""
    body = _watch_body()
    assert 'self_dispatch("launch")' in body, (
        "the watch reaps hosts but never re-places the units it emptied — the panel cannot converge")


def test_the_gap_is_computed_against_BOTH_done_and_live():
    """A unit is bare only when it has neither. Missing either term double-buys or never buys."""
    body = _watch_body()
    seg = body[body.index("need = ["):body.index("if need and")]
    assert "not in done" in seg and "not in live" in seg


def test_the_replacement_is_rate_limited_so_a_leg_is_not_bought_twice():
    """⚠ THE EXPENSIVE DIRECTION. Ticks are 3 min; a rental takes ~1-2 min to appear on the account."""
    body = _watch_body()
    assert "_REPLACE_MIN_S" in body
    assert L._REPLACE_MIN_S >= 300, (
        "the re-placement interval must exceed the time a fresh rental takes to register, or the next tick "
        "buys a second host for the same leg")
    interval = float(os.environ.get("SELCAL_WATCH_INTERVAL_S", "180"))
    assert L._REPLACE_MIN_S > interval, "a per-tick dispatch would race its own rentals"


def test_the_interval_is_far_below_a_leg_runtime():
    """A gap must not be allowed to stand for a meaningful fraction of the work. Legs run ~45 min."""
    assert L._REPLACE_MIN_S <= 15 * 60


def test_a_failed_dispatch_is_surfaced_not_swallowed():
    """A gap we could not re-place stalls the panel; it must not read like a healthy tick."""
    body = _watch_body()
    assert "SELCAL GAP NOT RE-PLACED" in body
    assert "::error" in body[body.index('self_dispatch("launch")'):]


def test_a_held_replacement_still_says_so():
    """Silence during the rate-limit window is indistinguishable from a loop that stopped checking."""
    body = _watch_body()
    assert "awaiting re-placement" in body


def test_the_completion_path_still_exits_without_dispatching():
    """When every unit has landed there is nothing to re-place — the loop must reap and return, not dispatch
    a launch that would find nothing to buy and rent a gate record for no reason."""
    body = _watch_body()
    complete = body[body.index("panel complete"):body.index("mode_reap(bucket)\n        # ★★")]
    assert 'self_dispatch("launch")' not in complete


def test_the_dispatch_cannot_pass_a_price_or_a_ceiling():
    """`self_dispatch` DISPATCHES, IT DOES NOT DECIDE. The re-placement must hand `launch` no knobs at all —
    every rental it causes has to face the lane's own market gate and per-offer buy line unmodified."""
    body = _watch_body()
    call = body[body.index('self_dispatch("launch")'):][:80]
    assert call.startswith('self_dispatch("launch")'), call
    assert "usd" not in call.lower() and "bid" not in call.lower() and "price" not in call.lower()


# =============================================================================================================
# the window ending is not the work ending
# =============================================================================================================
def test_the_watch_re_arms_when_its_window_closes_on_unfinished_work():
    """★★ MEASURED 2026-08-01. `mode_cofold_watch` re-arms itself in four places; `mode_watch` — the loop
    supervising the legs that cost LADDER DOLLARS — just `return 0`-ed when its 55-minute clock expired.

    `self_dispatch`'s own docstring states the rule it was breaking: "a watch that simply exits converts a
    supervised fleet into an unsupervised one at a predictable moment". The hosts do not stop when the job
    does; only the control plane can end billing (CLAUDE.md §6)."""
    body = _watch_body()
    tail = body[body.index("SELCAL_WATCH_INTERVAL_S"):]
    assert 'self_dispatch("watch")' in tail, (
        "the watch window closes and nothing re-arms it — the fleet becomes unsupervised on a timer")


def test_the_re_arm_is_keyed_on_UNFINISHED_UNITS_not_on_live_hosts():
    """⚠ They differ exactly when the panel has a gap and NO host in it — a stalled lane, which is the state
    that most needs a next tick and the one that looks identical to a finished lane from outside."""
    body = _watch_body()
    tail = body[body.index("SELCAL_WATCH_INTERVAL_S"):]
    assert "left = [" in tail and "not in done" in tail
    guard = tail[tail.index("if not left:"):tail.index('self_dispatch("watch")')]
    assert "return 0" in guard, "a complete panel must NOT re-arm"


def test_a_completed_panel_does_not_re_arm():
    """The early return on completion is a terminus; only the clock expiring is a re-arm."""
    body = _watch_body()
    tail = body[body.index("SELCAL_WATCH_INTERVAL_S"):]
    assert "nothing left to supervise" in tail


def test_a_failed_re_arm_is_an_error_naming_the_billing_risk():
    body = _watch_body()
    assert "SELCAL SUPERVISION ENDED" in body
    assert "cannot stop its own billing" in body


# =============================================================================================================
# two control paths must agree on what "alive" means
# =============================================================================================================
def test_a_host_whose_cur_state_is_terminal_does_not_cover_its_unit(monkeypatch):
    """★★ MEASURED 2026-08-01, and it stalled the panel for 32 minutes.

        rented 6:05-6:07 PM   actual_status='loading'/'created'   cur_state='stopped'   x7
        6:39 PM               the ACCOUNT REAPER destroyed exactly those seven as TERMINAL

    `_live_labels` read only `actual_status`, so the launcher counted all seven as live and skipped their
    units — while the other control path was destroying the very hosts that made them look covered. One of
    the two was wrong about the same instances at the same moment; that disagreement is the defect."""
    live = [{"label": "selcal-smarca2-m1-r1", "actual_status": "loading", "cur_state": "stopped"},
            {"label": "selcal-smarca4-m2-r1", "actual_status": "running", "cur_state": "running"}]
    monkeypatch.setattr(L, "_vast_request", lambda *a, **k: {"instances": live})
    ok, by_label, _mine = L._live_labels_checked(key="t")
    assert ok is True
    assert "selcal-smarca4-m2-r1" in by_label
    assert "selcal-smarca2-m1-r1" not in by_label, (
        "a host the account reaper calls TERMINAL still counted as covering its unit")


def test_created_still_counts_as_alive_when_cur_state_is_healthy():
    """⚠ `created` is an EARLY lifecycle state, not a terminal one — `vast_account_reaper` writes this down
    because an early draft of it had `created` in the terminal set and would have shredded fresh rentals."""
    assert "created" not in L._terminal_cur_states()


def test_the_terminal_set_is_not_re_typed_here():
    """§1. It is derived by `vast_account_reaper` from the lanes that define it, and that module is the one
    that ACTS on it. A second copy here is exactly how the two definitions drifted apart."""
    # THE DOCSTRING IS EXCLUDED — it NAMES `cur_state='stopped'` because that is the measurement this
    # function exists for, and a naive substring check would forbid writing down the evidence for the rule.
    # AST rather than string surgery: the question is "is this a literal the CODE uses", and only a parse
    # can answer that.
    import ast
    fn = next(n for n in ast.walk(ast.parse(SRC))
              if isinstance(n, ast.FunctionDef) and n.name == "_terminal_cur_states")
    stmts = fn.body[1:] if ast.get_docstring(fn) else fn.body
    code = "\n".join(ast.unparse(st) for st in stmts)
    assert "terminal_states_from_source" in code
    for typed in ("stopped", "exited", "offline", "error'"):
        assert typed not in code, f"{typed!r} must not be typed here — import the set"


def test_it_fails_OPEN_so_a_derivation_fault_cannot_double_rent(monkeypatch):
    """⚠ THE OPPOSITE DIRECTION FROM THE REAPER, DELIBERATELY. The reaper fails closed because its error is
    destructive; this predicate's error would be a DUPLICATE RENTAL, so it must under-demote, never over."""
    import builtins
    real = builtins.__import__

    def boom(name, *a, **k):
        if name == "vast_account_reaper":
            raise ImportError("simulated")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", boom)
    assert L._terminal_cur_states() == frozenset()


# =============================================================================================================
# the terminus is a VERDICT, not an empty host list
# =============================================================================================================
def test_a_complete_panel_is_SCORED_not_just_reaped():
    """★★ The completion branch used to reap and `return 0`, so the moment the 24th leg landed the lane went
    quiet with its frozen criterion UNSCORED — the panel sitting in S3 waiting for somebody to notice and
    dispatch `collect` by hand. That is the "needs an agent awake" dependency CLAUDE.md §6 removes, at the one
    place where noticing matters most: the terminus of the whole calibration."""
    body = _watch_body()
    comp = body[body.index("panel complete"):body.index("mode_reap(bucket)\n        # ★★")]
    assert "mode_collect(" in comp, "a complete panel must be scored, not merely reaped"
    assert comp.index("mode_reap(") < comp.index("mode_collect("), (
        "reap first: only the control plane can stop the meter, and scoring is a pure S3 read")


def test_the_scored_verdict_is_published():
    """A verdict that never leaves the runner is not a result."""
    body = _watch_body()
    comp = body[body.index("panel complete"):body.index("mode_reap(bucket)\n        # ★★")]
    assert "VERDICT_READOUT" in comp and "COLLECT_READOUT" in comp


def test_a_scoring_fault_does_not_lose_the_reap():
    """The reap stops billing; the score is analysis. A fault in the second must never undo the first."""
    body = _watch_body()
    comp = body[body.index("panel complete"):body.index("mode_reap(bucket)\n        # ★★")]
    assert "except Exception" in comp and "SELCAL PANEL UNSCORED" in comp


def test_scoring_at_the_terminus_is_not_an_interim_analysis():
    """⛔ The prereg forbids peeking at a partial panel. This branch is reached only when every unit has a
    production-checked leg, and `mode_collect` suppresses the tier unless `panel_complete` — so the criterion
    fires exactly when it said it would. The reasoning must stay written down next to the call."""
    import selcal_panel as SP
    assert "no_interim_analysis" in SP.PASS_CRITERION
    body = _watch_body()
    # …from the `if`, not from the print: the reasoning lives in the COMMENT above the branch, which is
    # where it has to be for the next reader deciding whether this is a peek.
    comp = body[body.index("if len(done) >= len(SP.enumerate_units())"):
                body.index("mode_reap(bucket)\n        # ★★")]
    assert "NOT AN INTERIM ANALYSIS" in comp
    # ⚠ RE-POINTED: suppression moved into `selcal_gate.suppress_for_incomplete_panel` so the label and
    # everything disclosing it are withheld ATOMICALLY. Asserting `tier_suppressed` appeared in
    # `mode_collect`'s own source pinned the mechanism, and broke on the refactor that made it safer — the
    # sixth time in this session a test pinned implementation over property. The property is: the scorer
    # suppresses on an incomplete panel, and it does so through the one home.
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    coll = src[src.index("def mode_collect("):]
    coll = coll[:coll.index("\ndef ", 10)]
    assert "suppress_for_incomplete_panel" in coll and "panel_complete" in coll
    import selcal_gate as G
    v = G.suppress_for_incomplete_panel(G.verdict([]), "incomplete")
    assert v["tier"] is None and "tier_suppressed" in v


# =============================================================================================================
# a file you PUBLISH is a file you must PRODUCE
# =============================================================================================================
def test_the_watch_recomputes_the_collect_readout_it_publishes():
    """★★ MEASURED 2026-08-02, and it had already done five hours of damage.

    The loop listed COLLECT_READOUT in its publish set and never called `mode_collect`, so each tick
    re-published whatever copy the checkout held. Harmless until something knocked the artifact backwards —
    and something did: a `status` tick reverted it to `landed: 0` at 22:16:50Z. Nothing here recomputed it,
    so the lane's official "what has landed" readout sat at ZERO while SEVENTEEN legs were banked in S3.

    ⚠ THE UPSTREAM PUBLISH GUARD MAKES THIS WORSE IN THIS ONE SPOT, which is why it needs its own test: an
    unchanged file is now correctly SKIPPED, so a stale copy can never be corrected by ticking. Publishing a
    file you do not produce is a slow corruption, not a no-op.
    """
    body = _watch_body()
    # ⚠ rindex on BOTH sides. There are two of each now — the terminus pair in the completion branch and
    # this per-tick pair — so comparing an index against a rindex compares the wrong two calls entirely.
    pub = body[body.rindex("_tick_publish(["):]
    assert "COLLECT_READOUT" in pub
    # ⚠ `rindex`, NOT `index`: there are TWO mode_collect calls now — the terminus scorer in the completion
    # branch, and this per-tick census. `index` finds the terminus and would pass while the per-tick call
    # was missing, i.e. it would vouch for the very thing this test exists to check.
    assert body.count("mode_collect(") >= 2, "the per-tick census is missing (only the terminus scorer)"
    assert body.rindex("mode_collect(") < body.rindex("_tick_publish(["), \
        "it must be recomputed BEFORE the publish that ships it"


def test_the_per_tick_collect_cannot_leak_an_early_verdict():
    """⛔ Running the scorer every 3 minutes is only safe because `mode_collect` SUPPRESSES the tier unless
    the panel is complete — it writes the evidence and withholds the label. If that ever stopped being true,
    this loop would be emitting interim verdicts on a live panel, which the prereg forbids outright."""
    # Same re-pointing as above: the guarantee is BEHAVIOURAL and lives in the gate, so assert it by
    # running it rather than by grepping for the assignment that used to implement it here.
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    coll = src[src.index("def mode_collect("):]
    coll = coll[:coll.index("\ndef ", 10)]
    assert "suppress_for_incomplete_panel" in coll
    assert "NO INTERIM ANALYSIS" in coll.upper()
    import selcal_gate as G
    v = G.suppress_for_incomplete_panel(G.verdict([]), "incomplete")
    assert v["tier"] is None, "an incomplete panel must publish no tier"
    assert "WITHHELD" in repr(v["next_step"]), "…and nothing that discloses it"
    body = _watch_body()
    assert "NOT AN INTERIM ANALYSIS" in body


def test_a_census_fault_does_not_end_supervision():
    """The reap stops billing; the census is reporting. A fault in the second must not kill the loop."""
    body = _watch_body()
    seg = body[body.rindex("mode_collect(bucket)"):]      # the PER-TICK one; see the rindex note above
    assert "except Exception" in seg[:400]
    assert "not refreshed this tick" in seg[:900]
