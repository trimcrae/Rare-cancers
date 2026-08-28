#!/usr/bin/env python3
"""The one push channel the autonomy loop has, and the only thing that can report its own death.

⛔⛔ THE FAILURE THIS EXISTS FOR IS THE QUIETEST ONE AVAILABLE. `health.py` grades the loop and
commits the board — but a red board committed to a repository nobody is reading tells nobody. If the
driver Routine stops firing, the loop produces no receipts, no commits, no errors and no alarm. It
looks exactly like a quiet week, indefinitely. That is not hypothetical here: this repository's
field-scan Routine fired every Friday for six weeks delivering nothing, and it was found by a human
happening to look.

★★ THE DESIGN PRINCIPLE IS TWO INDEPENDENT CLOCKS, EACH ABLE TO REPORT THE OTHER'S ABSENCE.
    the Routine clock  — fires the research cycles, and is the thing that dies silently
    the Actions clock  — `autonomy-tick.yml`, every 2 h, and is what runs THIS
A supervisor sharing a clock with the thing it supervises cannot report that the clock stopped. This
is the same reasoning that keeps `fleet-supervision-alarm.yml` sharing no code with the lane it
watches.

⛔ AND IT MUST NOT BECOME NOISE, BECAUSE THIS REPOSITORY HAS ALREADY PAID FOR THAT TOO. Every push
channel was stripped out of `lane-staleness-watch.yml` on 2026-07-31 after a supervisor with nothing
to supervise emitted 1,476 commits in 24 h. So three rules bound it:
  1. Only when a condition is red — never on unmeasured, never on green, never a heartbeat.
  2. Only after the condition has been red for `FIRST_ALARM_RUNS` consecutive runs, so one transient
     red (a mid-cycle read, a half-written ledger) never wakes anybody.
  3. Then at most once a day while it stays red, so a genuine outage nags but does not flood.
A quiet alarm is worth having. An alarm that cries every two hours gets muted, and a muted alarm is
worse than none because it also carries the belief that somebody is watching.

⭐ AND A FOURTH RULE, ADDED 2026-08-28 (AUT-PROP-034), WHICH IS THE ONE THAT SENDS A DIFFERENT MAIL
RATHER THAN A LOUDER ONE. Rules 1-3 answer "the loop is unhealthy, come look". They cannot say the
stronger thing: **automation has run out of ways to respond.** `health.py`'s restart-intensity
counter (OTP `intensity`/`period`, systemd `StartLimitBurst`, ported) marks a condition the loop has
now answered with `RESTART_INTENSITY` consecutive refusals or redirects, and `decide()` turns that
into a CLAUDE.md §3 escalation with its own subject — sent ONCE outside the cadence, on the crossing
run, and governed by rule 3 thereafter. ⛔ It is deliberately not merged into the ordinary mail: an
escalation queued behind an alarm that already went out waits a day, and an escalation that reads
like the daily alarm gets filed like one.

Usage (from the Actions clock; needs MAIL_PASSWORD or SES creds in the environment):
    python3 research/autonomy/stall_alarm.py --health research/autonomy/health.json
    python3 research/autonomy/stall_alarm.py --dry-run     # decide and print, send nothing

Exit 0 always — a mail failure must not fail the tick that also publishes the board.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_HEALTH = HERE / "health.json"

#: Consecutive red runs before the FIRST alarm. At the tick's 2 h cadence this is ~4 h of sustained
#: red — long enough that a transient loses, short enough that a real stall is caught the same day.
FIRST_ALARM_RUNS = 2

#: After the first, re-alarm every this many runs (~24 h at a 2 h cadence). Rule 3 above.
REPEAT_EVERY_RUNS = 12


def decide(board: dict) -> dict:
    """Pure function: given the board, should we send, and what would we say?

    Kept separate from sending so the decision is testable without an SMTP server, and so `--dry-run`
    exercises the REAL logic rather than a parallel copy of it.
    """
    conditions = board.get("conditions") or []
    red = [c for c in conditions if c.get("needs_attention")]
    if not red:
        return {"send": False, "why": "no condition needs attention", "red": [], "escalations": []}

    # ⚠ The alarm ages on the WORST-established red, not the newest. A condition red for a day and a
    # second red for one run must not reset the clock and delay the alarm.
    worst = max(red, key=lambda c: int(c.get("consecutive_bad_runs") or 0))
    runs = int(worst.get("consecutive_bad_runs") or 0)

    # ⛔⛔ THE RESTART-INTENSITY ESCALATION, AND IT IS A DIFFERENT MESSAGE RATHER THAN A LOUDER ONE.
    # `health.py`'s intensity counter (OTP `intensity`/`period` and systemd `StartLimitBurst`,
    # ported) marks a row whose red the loop has now answered with RESTART_INTENSITY consecutive
    # automated refusals or redirects. Everything above this line says "the loop is unhealthy, come
    # look". This says something stronger and far more specific: **automation has stopped being able
    # to fix it, and CLAUDE.md §3 wants a decision.** Sending them under one subject is how the
    # second gets read as the first and waits behind it.
    # ⚠ THE LIMIT IS READ OFF THE BOARD, NEVER RETYPED HERE. `health.py` owns RESTART_INTENSITY; a
    # second copy of it in the alarm is the drift `receipt_schema` was created to end (AUT-PD-013).
    escalating = [c for c in red if (c.get("intensity") or {}).get("exhausted")]
    # ⭐ ONE MAIL OUTSIDE THE CADENCE, AND EXACTLY ONE PER RED EPISODE. The CROSSING run is the run at
    # which `n` first reaches the limit; after it, the ordinary repeat cadence governs again. Weaker,
    # and the escalation waits up to REPEAT_EVERY_RUNS (~a day) behind a mail already sent; stronger,
    # and a sustained escalation mails every tick, which is the 1,476-commits-in-24-h failure the
    # three rules in this module's docstring exist to prevent.
    crossing = [c for c in escalating
                if int((c.get("intensity") or {}).get("n") or 0)
                == int((c.get("intensity") or {}).get("limit") or -1)]

    if not crossing:
        if runs < FIRST_ALARM_RUNS:
            return {"send": False, "red": [c.get("key") for c in red], "escalations": [],
                    "why": f"red for {runs} run(s); first alarm at {FIRST_ALARM_RUNS} "
                           "— one transient red never wakes anybody"}
        if runs > FIRST_ALARM_RUNS and (runs - FIRST_ALARM_RUNS) % REPEAT_EVERY_RUNS != 0:
            return {"send": False, "red": [c.get("key") for c in red], "escalations": [],
                    "why": f"already alarmed; next repeat in "
                           f"{REPEAT_EVERY_RUNS - ((runs - FIRST_ALARM_RUNS) % REPEAT_EVERY_RUNS)} run(s)"}

    if escalating:
        limit = (escalating[0].get("intensity") or {}).get("limit")
        lines = [
            "⛔ CLAUDE.md §3 ESCALATION — the loop's automated response to this is spent.", "",
            "This is NOT the ordinary 'the loop is unhealthy' mail. Each condition below has been RED "
            f"on at least {limit}",
            "consecutive health-board runs while the loop's only response was to refuse to start a "
            "cycle, or to",
            "redirect a cycle at fixing it — and that response has now demonstrably not worked. OTP "
            "calls this bound",
            "`intensity`/`period` and systemd calls it `StartLimitBurst`; neither lets a supervised "
            "thing fail forever",
            "in silence, and until this counter existed, this loop did.", "",
            "⛔ THE CORRECT NEXT ACT IS A DECISION, NOT ANOTHER CYCLE AND NOT ANOTHER REFUSAL.", "",
        ]
        for c in escalating:
            inten = c.get("intensity") or {}
            lines.append(f"  {c.get('key')} [axis={c.get('axis')}, on_red={c.get('on_red')}]: "
                         f"{c.get('verdict')}")
            lines.append(f"      {str(c.get('detail') or '').strip()[:400]}")
            lines.append(f"      red on {inten.get('n')} consecutive {inten.get('unit')} "
                         f"(limit {inten.get('limit')})"
                         + (f", measured age {c.get('bad_for_h')} h" if c.get("bad_for_h") else ""))
            lines.append("")
        lines += [
            "⚠ That count is in BOARD RUNS, not hours. The tick's cron is a request rather than a "
            "cadence, so the",
            "  run count is a LOWER BOUND on elapsed time; the measured age beside it is the real "
            "figure.",
            "",
            "Every red condition, including the ones above:", "",
        ]
    else:
        lines = [f"The EMC research loop has been unhealthy for {runs} consecutive checks.", ""]
    for c in red:
        lines.append(f"  {c.get('key')}: {c.get('verdict')}")
        lines.append(f"      {str(c.get('detail') or '').strip()[:400]}")
        if c.get("bad_since_utc"):
            lines.append(f"      red since {c['bad_since_utc']}")
        lines.append("")
    lines += [
        "This mail comes from the Actions clock, NOT from the research loop — deliberately, because a",
        "loop that has stopped cannot report that it stopped.",
        "",
        "What to look at first:",
        "  research/autonomy/health.json          the full board, with each condition's evidence",
        "  research/autonomy/receipts/            a cycle that ran leaves one here; none means none ran",
        "  the driver Routine in claude.ai        if it stopped firing, nothing in the repo can restart it",
        "",
        "⚠ A red board is not always a dead loop. `gates_green` red means the trunk is red and cycles are",
        "correctly refusing to start; `queue_is_takeable` red means the queue has nothing workable, which",
        "is a stall the loop cannot fix by trying harder.",
    ]
    if escalating:
        keys = ", ".join(c.get("key") for c in escalating)
        return {"send": True, "red": [c.get("key") for c in red], "runs": runs,
                "escalations": [c.get("key") for c in escalating],
                "subject": f"[EMC loop] ⛔ §3 ESCALATION — automation is out of retries on {keys}"[:180],
                "body": "\n".join(lines)}
    return {"send": True, "red": [c.get("key") for c in red], "runs": runs,
            "escalations": [],
            "subject": f"[EMC loop] unhealthy for {runs} checks: "
                       + ", ".join(c.get("key") for c in red)[:80],
            "body": "\n".join(lines)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--health", default=str(DEFAULT_HEALTH))
    ap.add_argument("--dry-run", action="store_true", help="decide and print; send nothing")
    args = ap.parse_args(argv)

    try:
        board = json.loads(pathlib.Path(args.health).read_text())
    except Exception as exc:
        # ⛔ AN UNREADABLE BOARD IS ITSELF A STALL SIGNAL, not a reason to exit quietly — the checker
        # that writes it runs in this same job, so if it is missing, the job before us failed.
        print(f"[stall-alarm] cannot read {args.health}: {type(exc).__name__} — "
              "treat as the tick failing, not as the loop being healthy")
        return 0

    verdict = decide(board)
    print(f"[stall-alarm] send={verdict['send']} — {verdict.get('why', verdict.get('subject'))}")
    if not verdict["send"] or args.dry_run:
        return 0

    sys.path.insert(0, str(REPO / "research" / "modalities"))
    try:
        from mailer import send_email  # the ONE home of "how this repo sends mail"
        result = send_email(verdict["subject"], verdict["body"], None)
        print(f"[stall-alarm] {result}")
    except Exception as exc:
        # Never fail the tick. The board is committed regardless, and a failed send that took the
        # publish step down with it would remove the pull channel as well as the push one.
        print(f"[stall-alarm] send FAILED ({type(exc).__name__}: {exc}) — the board is still committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
