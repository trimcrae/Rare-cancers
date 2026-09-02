#!/usr/bin/env python3
"""The `$/ns` gate at the moment of RENTING ONE HOST — a relaunch, a resume, or a cold single unit.

⛔ WHY THIS EXISTS (trimcrae, 2026-07-27: *"Why are there so many high $/ns rows that are flagged but you're
still paying for them? The whole point is to pause the test if it gets that expensive."*).

CLAUDE.md §6 gated the **fan-out** on `$/ns` and exempted "a single unit already running". That exemption was
cut on the wrong axis and the incoherence was visible on the board the same night: a fan-out at 2.05× basis
was correctly HELD while a shakeout resume ran at **1.76×** and a 5a-KS leg at **1.51×**, both printing
`⚠ DRIFT`, both untouched. Overnight those two lanes were relaunched repeatedly through spot churn, host
deaths and capacity reclaims — and **every one of those relaunches was a fresh decision to rent a host at
whatever the market was charging that minute.** Classifying them as "already running" let each one past a
gate that would have refused the identical purchase made nineteen at a time.

★ THE RIGHT AXIS IS NOT FAN-OUT-VS-SINGLE. IT IS *"WOULD WAITING ACTUALLY LOSE WORK?"*
At the moment a relaunch is considered, the host is **already gone**. The only state that still exists is the
state that was durable enough to survive it — the S3 commit store. Waiting cannot destroy that; it is not a
lease, it is an object. So for a checkpointed leg the answer is essentially always **no**, and a relaunch must
face the same ceiling as a fan-out. `EXEMPTIONS` below is the complete list of the cases where the answer is
genuinely *yes*, each with its reason; anything not on that list is gated.

**And that premise is measured, not assumed** (`--durability-probe`, 2026-07-27). The direct read is refused —
the CI identity has no `s3:GetLifecycleConfiguration` — so the probe asks the data instead and the argument
closes on a property of S3 rather than on the sample: **lifecycle expiration is expressed in DAYS with a
minimum of 1**, so the shortest possible rule is 24 h, while a hold becomes trimcrae's decision at
`RELAUNCH_ESCALATE_H`. A hold therefore cannot straddle an expiry boundary. The listing separately excludes any
1–2 day rule and any storage-class transition.

★ THE CEILING IS A RATIO, NOT A DOLLAR BAND — and that is a deliberate difference from the fan-out gate.
  1. **A dollar band is a TRANCHE authorisation.** `congeneric_fanout.market_ceiling_usd` scales the rung's
     approved band by unit count, which is the right test for a tranche you are about to buy whole. A resume
     is not that: it re-enters a leg at an unknown fraction of its work, so any per-unit dollar projection is
     the FULL unit cost and therefore an over-estimate of what the rental will actually consume. A ceiling
     built on an over-estimate is not conservative — it is just wrong in a direction nobody can reason about.
  2. **A rate needs no estimate of remaining work.** `$/ns` is what you are being charged per unit of science
     regardless of how much science is left, which is exactly the quantity a resume can be graded on.
  3. **1.5× is the repo's OWN number, not one invented here.** CLAUDE.md §1 already defines ≳1.5× basis as
     drift and requires every in-flight row to say so; `inflight_usd_per_ns.DRIFT_MULTIPLE` is its code home
     and `ternary_vast_launch.MARKET_MAX_RATIO_VS_BASIS` already points at it. Per rule 1, a fourth number
     would be the bug. It also makes the board self-consistent for the first time: **a row that prints
     `⚠ DRIFT` is now exactly a row this gate would have refused to buy.**

★ WHAT IS IMPORTED RATHER THAN REIMPLEMENTED (rule 1 — LANE 20 and LANE 21 both got this right):
  * `gpu_backend.rank_offers_by_usd_per_ns` — the qualify+score filter the RENTING path itself uses, so the
    gate can never price a host the launcher would not actually buy;
  * `congeneric_fanout.basis_usd_per_ns` — the ladder basis (a property of the market, not of a rung), and
    deliberately the ladder's rather than a recent night's: anchoring to observations is self-ratcheting, so
    a bad night would raise the ceiling until the guard permitted the market it exists to refuse;
  * `inflight_usd_per_ns.DRIFT_MULTIPLE` — the drift line the reporting rules already publish.
Nothing in this file computes a price, a throughput or a basis of its own.

★ THE TWO FAILURE MODES CLAUDE.md §6 NAMES APPLY HERE TOO, and are answered the same way LANE 21 answered
them for the fan-out — the mechanism is reused, not re-invented:
  * **A silent hold is indistinguishable from a finished unit.** Every pass writes its snapshot to the
    committed `relaunch-market-hold.json` AND to `<state_prefix>/relaunch-market-hold.json` in S3, and every
    hold prints a `::notice::` annotation naming the unit, the ratio and the board depth. A held relaunch is
    never "nothing to do".
  * **A ceiling nobody can clear turns into an idle night.** The first hold per unit records `first_held_utc`;
    once a unit has been held past `RELAUNCH_ESCALATE_H` the annotation becomes a `::error::`, which fails the
    job and fires GitHub's own workflow-failure notification — the session-independent alert path the
    watchdogs already rely on. The gate never buys in on its own; the escalation hands the decision over.
"""
import calendar
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "autonomy"))
import gpu_ban as _gpu_ban  # noqa: E402

from inflight_usd_per_ns import DRIFT_MULTIPLE    # noqa: E402  the drift line's ONE home (CLAUDE.md §1)

# The ceiling. Overridable by env for a deliberate, recorded exception; never edited to fit a bad market.
RELAUNCH_MAX_RATIO_VS_BASIS = float(os.environ.get("RELAUNCH_MAX_RATIO_VS_BASIS") or DRIFT_MULTIPLE)

# ★ ELAPSED TIME, NOT A TICK COUNT, for the reason LANE 21 recorded on the fan-out gate: this repo's crons are
# throttled to roughly one run per workflow per hour whatever they ask for (measured 56-97 min for a */15), so
# "3 ticks" is not a knowable duration and a tick-based escalation would fire anywhere between 30 min and 5 h.
RELAUNCH_ESCALATE_H = float(os.environ.get("RELAUNCH_MARKET_ESCALATE_H") or "6")

STATE_BASENAME = "relaunch-market-hold.json"
READOUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), STATE_BASENAME)


# =============================================================================================================
# the exemptions — narrow, enumerated, each with the reason it is real
# =============================================================================================================
# ⚠ THE BOUNDARY THIS GATE MUST NEVER CROSS: **it applies at the moment of RENTING, never to work in progress.**
# A unit already executing on a host is untouched — the gate is not consulted for it, has no way to stop it and
# must never be given one. Killing a running leg to save $/ns would throw away paid-for work to avoid paying
# for work, which is the opposite of the rule. `tests/test_relaunch_market_gate.py` pins this.
#
# Everything below is a case where the premise "waiting loses nothing" genuinely fails. The list is short
# because the premise is strong: at relaunch time the host is already dead and the surviving state is an S3
# object, which does not expire while you think about it.
EXEMPTIONS = {
    # 1. YOU ALREADY OWN THIS RENTAL. Re-issuing `PUT /instances/<id>/ {"state": "running"}` on a box you are
    #    still holding is NOT a purchase: the price was agreed when the instance was created, the rate cannot
    #    change under you, and a `stopped` Vast box is billing for its disk in the meantime. Holding would cost
    #    money and buy nothing. This is a real path in the code — `ternary_vast_launch.collect` nudges stopped
    #    boxes exactly this way — and it is the one place where "relaunch" does not mean "rent".
    "already_held_instance": "restarting an instance this account already holds — the rate was fixed at "
                             "rental time and the stopped box is billing disk, so waiting costs money and "
                             "saves none",
    # 2. A CHECKPOINT WITH A HARD EXPIRY. This is the only way waiting can actually destroy durable state, so
    #    it is parameterised rather than assumed away: an entry may carry `checkpoint_expires_utc` and the gate
    #    will let its relaunch through once the deadline is inside `RELAUNCH_ESCALATE_H`.
    #    ⚠ NO LANE SETS IT TODAY, and that is an evidence-backed statement rather than an assumption — see
    #    `--durability-probe`, which reads the checkpoint bucket's real lifecycle configuration. Keep the hook
    #    anyway: the day a lane checkpoints somewhere with a TTL, the exemption must already exist, because
    #    the alternative is discovering it by losing a leg.
    "checkpoint_expiring": "this unit's durable state has a hard expiry inside the escalation window, so "
                           "waiting would destroy work rather than defer it",
}


def exemption(*, already_held_instance=False, checkpoint_expires_utc=None, now=None,
              window_h=None):
    """(key, reason) if this rental is genuinely exempt from the gate, else (None, "").  PURE.

    Both arguments default to the non-exempt answer, so a caller that does not know is gated — the safe
    direction, and the one that makes a forgotten call site visible as a hold rather than as a silent bypass.
    """
    if already_held_instance:
        return "already_held_instance", EXEMPTIONS["already_held_instance"]
    if checkpoint_expires_utc:
        try:
            t = time.strptime(str(checkpoint_expires_utc), "%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            return None, ""      # an unparseable expiry is not an expiry; gate it and let the readout say so
        left_h = (calendar.timegm(t) - (now if now is not None else time.time())) / 3600.0
        win = RELAUNCH_ESCALATE_H if window_h is None else float(window_h)
        if left_h <= win:
            return ("checkpoint_expiring",
                    f"{EXEMPTIONS['checkpoint_expiring']} ({left_h:.1f} h left, window {win:.1f} h)")
    return None, ""


# =============================================================================================================
# pricing — PURE, so the verdict is unit-testable without a board
# =============================================================================================================
def price_offers(offers, res, n_hosts=1):
    """(best_usd_per_ns, depth, rows) for renting `n_hosts` from an already-fetched offer list. PURE.

    Delegates the filter and the score to `gpu_backend.rank_offers_by_usd_per_ns` — the same call the renting
    path makes — so a host this gate prices is a host the launcher would actually take. `best` is the mean
    over the `n_hosts` cheapest qualifying offers; for the single-host case this file exists for that is
    simply the best offer on the board.
    """
    from gpu_backend import rank_offers_by_usd_per_ns
    measured, capable = rank_offers_by_usd_per_ns(offers or [], res)
    take = measured[:max(1, int(n_hosts))]
    rows = [{"gpu": o.get("gpu_name"), "machine_id": o.get("machine_id"),
             "min_bid_usd_h": p, "usd_per_ns": round(u, 6)} for u, p, o in take]
    depth = {"offers_returned": len(offers or []), "qualifying": len(capable),
             "priceable": len(measured), "needed": int(n_hosts), "used_for_mean": len(take)}
    best = (sum(r["usd_per_ns"] for r in rows) / len(rows)) if rows else None
    return best, depth, rows


def verdict(best_usd_per_ns, max_ratio=None):
    """(hold, ratio, basis, reason) for one rental at an achievable `$/ns`. PURE.

    `best_usd_per_ns is None` means the board offered nothing this gate can price — no benched card, or no
    qualifying offer at all. That is a HOLD, not a launch: an unpriceable market is the one case where
    guessing is worst, and it is exactly the case where nobody is awake to check.
    """
    from congeneric_fanout import basis_usd_per_ns
    basis = basis_usd_per_ns()
    cap = RELAUNCH_MAX_RATIO_VS_BASIS if max_ratio is None else float(max_ratio)
    if best_usd_per_ns is None:
        return True, None, basis, ("the board offered nothing priceable (no benched card, or no qualifying "
                                   "offer) — an unpriceable market is not a cheap one")
    ratio = float(best_usd_per_ns) / basis if basis > 0 else None
    if ratio is None:
        return True, None, basis, "the ladder basis is not positive, so no ratio can be formed"
    # ⚠ RELATIVE EPSILON, NOT A BARE `>` (2026-07-27). `ratio` is a DIVISION, so a rental priced exactly at
    # the line — `best = cap * basis`, which is precisely how the boundary test constructs it — can land at
    # 1.5000000000000002 and be refused. Whether a spend gate admits the boundary case must not depend on the
    # bit pattern of the current basis: with the retired basis `(1.5*b)/b` was exactly 1.5 and this passed by
    # luck; the re-anchored basis exposed it. The documented rule is "at the line it CLEARS".
    if ratio > cap * (1.0 + 1e-9):
        return True, round(ratio, 3), basis, (
            f"{ratio:.2f}x the ladder basis exceeds the {cap:.2f}x drift line (CLAUDE.md §1). A relaunch is a "
            f"NEW PURCHASE, not a continuation: the host is already gone and the checkpoint is a durable S3 "
            f"object, so waiting defers this rental without losing any work. Need <= ${cap * basis:.6f}/ns")
    return False, round(ratio, 3), basis, (
        f"{ratio:.2f}x the ladder basis is within the {cap:.2f}x drift line — this host is buyable at a sane "
        f"rate per nanosecond")


# =============================================================================================================
# the gate — the one call every single-host rental makes
# =============================================================================================================
def _utcnow(now=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))


def _held_hours(first_held_utc, now=None):
    if not first_held_utc:
        return 0.0
    try:
        t0 = calendar.timegm(time.strptime(str(first_held_utc), "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError):
        return 0.0
    return max(0.0, ((now if now is not None else time.time()) - t0) / 3600.0)


def _load_state(s3, bucket, key):
    if s3 is None or not bucket:
        return {}
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception:  # noqa: BLE001 — no state yet, or unreadable; an empty clock is the safe default
        return {}


def _save_state(s3, bucket, key, doc):
    if s3 is None or not bucket:
        return False
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(doc, indent=2).encode())
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[relaunch-gate] state not persisted ({type(e).__name__}: {e}) — the escalation clock cannot "
              f"run without it, and the readout says so", flush=True)
        return False


def _write_readout(doc, path=None):
    """Best-effort committed readout. A hold that only exists in a job log is a silent hold: GitHub truncates
    a log from the tail and the tail is always runner boilerplate."""
    p = path or READOUT_PATH
    try:
        with open(p, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
        return True
    except OSError as e:
        print(f"[relaunch-gate] readout not written to {p}: {e}", flush=True)
        return False


def gate(lane, unit_id, res, *, key=None, excluded=(), max_ratio=None, s3=None,
         state_bucket=None, state_prefix=None, readout_path=None,
         already_held_instance=False, checkpoint_expires_utc=None, offers=None, now=None):
    """(hold, doc) for renting ONE host for `unit_id` right now. Reads the LIVE board unless `offers` is given.

    `hold=True` means DO NOT RENT. Nothing is destroyed, nothing is dropped, and the next scheduled tick
    re-checks — the unit's checkpoint is untouched in S3 and the leg resumes exactly where it stopped.

    `res` is the LANE'S OWN `ResourceSpec`, never a shared default: a ternary leg needs 32 GB RAM / 8 vCPU /
    24 GB VRAM and a paralogue MD leg does not, so pricing one against the other's filter would grade a market
    the lane cannot buy from.
    """
    import dataclasses
    doc = {"_what": "Whether a SINGLE-HOST rental (relaunch / resume / cold unit) may proceed, priced in "
                    "$/ns. Written on EVERY pass, because a silent hold is indistinguishable from a "
                    "finished unit.",
           "_rule": "CLAUDE.md §6 — a thin, expensive market is a reason to PAUSE, not to pay. A relaunch is "
                    "a NEW PURCHASE, not a continuation.",
           "lane": lane, "unit_id": unit_id, "utc": _utcnow(now),
           "max_ratio_vs_basis": (RELAUNCH_MAX_RATIO_VS_BASIS if max_ratio is None else float(max_ratio))}

    # ⛔⛔ THE NO-GPU BAN IS ASKED FIRST — BEFORE THE EXEMPTIONS, BEFORE THE BOARD, BEFORE ANY PRICE.
    # ★★ THE ORDERING IS THE POINT, AND IT IS WRITTEN IN CODE BECAUSE PROSE DID NOT HOLD. On 2026-09-02 a
    # cycle read the selectivity control's committed price ($25.45), compared it against CLAUDE.md §2's
    # ≲$50 self-doable ceiling, and concluded the standing autonomy rule already authorised the buy. Every
    # written rule it applied was applied correctly. trimcrae interrupted. This gate answers "is this RATE
    # acceptable?"; he had already answered a different question with "no GPU at all", so a `CLEARS` here
    # is not permission and never was.
    # ⛔ AND IT IS AHEAD OF `EXEMPTIONS` DELIBERATELY. Those exempt the cases where waiting would genuinely
    # lose work — a real and correct reason to bypass a PRICE ceiling, and no reason at all to bypass a
    # category ban. An exemption that could out-rank the ban would make "we would lose work" into a
    # self-issued purchase permission, which is the exact shape §3 refuses.
    _banned = _gpu_ban.refusal(f"relaunch_market_gate.gate({lane}/{unit_id}) — renting one host")
    if _banned:
        doc.update({"hold": True, "hold_cause": "gpu_spend_prohibited", "ratio_vs_basis": None,
                    "reason": _banned,
                    "_ordering": "The ban is read BEFORE the exemptions, the board and the price. No $/ns "
                                 "verdict was computed, because none of them could change this answer."})
        print(f"[relaunch-gate] {lane}/{unit_id}: \u26d4 REFUSED BY STANDING INSTRUCTION (not by price)\n{_banned}",
              flush=True)
        _write_readout(doc, readout_path)
        return True, doc

    ex_key, ex_why = exemption(already_held_instance=already_held_instance,
                               checkpoint_expires_utc=checkpoint_expires_utc, now=now)
    if ex_key:
        doc.update({"hold": False, "exempt": ex_key, "reason": f"EXEMPT ({ex_key}): {ex_why}"})
        print(f"[relaunch-gate] {lane}/{unit_id}: ✅ EXEMPT — {ex_why}", flush=True)
        return False, doc

    if excluded:
        res = dataclasses.replace(res, exclude_machine_ids=tuple(str(m) for m in excluded))
    if offers is None:
        try:
            from gpu_backend import _vast_offer_query, _vast_request
            api = key or os.environ.get("VAST_API_KEY")
            if not api:
                raise RuntimeError("no VAST_API_KEY — the board cannot be read")
            offers = (_vast_request("GET", "/search/asks/", api,
                                    params={"q": json.dumps(_vast_offer_query(res))}) or {}).get("offers", [])
        except Exception as e:  # noqa: BLE001
            # Same discipline as the fan-out guard's "unreadable is not zero": refuse, and say the refusal was
            # for lack of evidence rather than for a price.
            offers, doc["board_error"] = None, f"{type(e).__name__}: {e}"

    if offers is None:
        best, depth, rows = None, {"offers_returned": 0, "qualifying": 0, "priceable": 0,
                                   "needed": 1, "used_for_mean": 0}, []
    else:
        best, depth, rows = price_offers(offers, res, n_hosts=1)
    hold, ratio, basis, reason = verdict(best, max_ratio)
    if doc.get("board_error"):
        reason = (f"could not read the board ({doc['board_error']}) — an unreadable market is not a cheap "
                  f"one, and this gate exists precisely for the case where nobody is awake to check")
    elif hold and best is None and depth["offers_returned"] and not depth["qualifying"] and excluded:
        # ⚠ NOT A PRICE PROBLEM, AND IT MUST NOT BE REPORTED AS ONE. The shared host blacklist is permanent
        # by design (a host that refuses starts keeps refusing), so it only ever grows — and a set large
        # enough to disqualify the whole board would make this gate hold forever while the readout blamed the
        # market. That misdiagnosis would cost a night, so the two causes are separated here by the one
        # observation that discriminates: the board RETURNED offers and NONE survived the filter.
        reason = (f"NOT A PRICE HOLD — the board returned {depth['offers_returned']} offer(s) and none "
                  f"survived the host filter while {len(excluded)} machine(s) are excluded "
                  f"({sorted(excluded)[:12]}). Either the exclusion set has outgrown the market or the "
                  f"ResourceSpec is unsatisfiable; re-pricing will not fix either. Review the exclusions "
                  f"(vast_machine_blacklist) before touching the ceiling.")
        doc["hold_cause"] = "exclusions_or_spec_not_price"
    doc.update({"hold": hold, "reason": reason, "best_usd_per_ns": (round(best, 6) if best else None),
                "basis_usd_per_ns": round(basis, 6), "ratio_vs_basis": ratio,
                "usd_per_ns_at_max_ratio": round(doc["max_ratio_vs_basis"] * basis, 6),
                "board_depth": depth, "offers_priced": rows})

    # ---- the escalation clock, per unit ---------------------------------------------------------------
    skey = f"{str(state_prefix).rstrip('/')}/{STATE_BASENAME}" if state_prefix else None
    state = _load_state(s3, state_bucket, skey) if skey else {}
    units = state.get("units") or {}
    prev = units.get(unit_id) or {}
    first = (prev.get("first_held_utc") if (hold and prev.get("held")) else (doc["utc"] if hold else None))
    doc["first_held_utc"] = first
    doc["held_hours"] = round(_held_hours(first, now), 2)
    units[unit_id] = {"held": hold, "first_held_utc": first, "held_hours": doc["held_hours"],
                      "utc": doc["utc"], "ratio_vs_basis": ratio, "reason": reason}
    state.update({"_what": doc["_what"], "_rule": doc["_rule"], "lane": lane, "utc": doc["utc"],
                  "units": units})
    persisted = _save_state(s3, state_bucket, skey, state) if skey else False
    if not persisted:
        doc["escalation_clock"] = ("UNAVAILABLE — the hold state could not be persisted, so `held_hours` "
                                   "restarts every pass and this unit cannot escalate on its own")
    doc["state_key"] = skey
    _write_readout(state, readout_path)

    if not hold:
        print(f"[relaunch-gate] {lane}/{unit_id}: ✅ CLEAR — {reason}", flush=True)
        return False, doc

    print(f"[relaunch-gate] {lane}/{unit_id}: ⛔ HELD ON PRICE — {reason}. Nothing was rented; the checkpoint "
          f"is untouched in S3 and the next tick re-checks. Board: {json.dumps(depth)}; "
          f"priced: {json.dumps(rows)}", flush=True)
    # `escalated` is RETURNED rather than acted on here, because only the caller knows how its job signals a
    # decision: the watchdogs count alerts and exit non-zero, the fan-out tick sets its own escalation flag.
    # Printing `::error::` annotates; FAILING THE JOB is what actually reaches a phone, and that is the
    # caller's exit code to own.
    doc["escalated"] = bool(doc["held_hours"] >= RELAUNCH_ESCALATE_H and persisted)
    if doc["escalated"]:
        # Not a decision the gate is allowed to make for him — a notification that one is now needed.
        # `::error::` also fails the job, which is what actually reaches a phone with no agent awake.
        print(f"::error title=RELAUNCH HELD {doc['held_hours']:.1f} H ON A BAD MARKET::{lane}/{unit_id} has "
              f"been refused a host for {doc['held_hours']:.1f} h (since {first}). Best achievable is "
              f"{ratio}x the ladder basis against a {doc['max_ratio_vs_basis']}x drift line. The gate will "
              f"NOT buy in on its own — this needs a decision: wait longer, re-price the ladder against a "
              f"changed market, or authorise the higher rate. Snapshot: {STATE_BASENAME}.", flush=True)
    else:
        # Visible but not alarming, per CLAUDE.md §6: a routine pause on a thin market is expected behaviour.
        print(f"::notice title=RELAUNCH HELD ON PRICE::{lane}/{unit_id} — {ratio}x the ladder basis exceeds "
              f"the {doc['max_ratio_vs_basis']}x drift line. Held {doc['held_hours']:.1f} h; escalates at "
              f"{RELAUNCH_ESCALATE_H:.0f} h. Nothing rented, nothing lost.", flush=True)
    return True, doc


# =============================================================================================================
# the durability probe — the evidence behind "waiting cannot lose work"
# =============================================================================================================
def checkpoint_prefixes():
    """The prefixes whose durability the gate's premise rests on — DERIVED from each lane's own module rather
    than typed here, so a lane that repoints its prefix cannot leave this probe measuring the old one."""
    import congeneric_fanout_vast as cfv
    import nr4a_paralogue_md_vast_launch as pdyn
    import ternary_vast_launch as tv
    return tuple(p for p in (f"{cfv.RESULT_PREFIX.rstrip('/')}/",
                             f"{tv.RESULT_PREFIX.rstrip('/')}/commits/",
                             f"{pdyn.RESULT_PREFIX.rstrip('/')}/") if p.strip("/"))


def observed_object_ages(bucket, prefixes=None, s3=None, sample=400):
    """(oldest_age_days, storage_classes, per-prefix rows) for the CHECKPOINT data itself.

    ★ THE FALLBACK DIAGNOSTIC, AND IT IS NOT A CONSOLATION PRIZE (CLAUDE.md §4). `GetBucketLifecycleConfiguration`
    is the direct read, and the CI identity is not authorised for it — measured, not assumed:
    `AccessDenied … user/nr4a3-ci-submitter … s3:GetLifecycleConfiguration` (run 30261651754, 2026-07-27
    7:22 AM ET). "I couldn't run it here" is never the stopping point, so the question is asked of the DATA
    instead, using `ListObjectsV2`, which the same identity uses on every tick.

    The observation discriminates: an EXPIRATION rule deletes objects past its age, so the survival of objects
    materially older than any plausible TTL is direct evidence none is acting on this prefix. A TRANSITION rule
    changes `StorageClass`, so an all-`STANDARD` listing is direct evidence none is acting either — which
    matters separately, because a checkpoint transitioned to GLACIER is still *there* but no longer resumable
    on demand, and that would be an expiry in every sense that counts for a held relaunch.

    This is weaker than reading the policy and says so: it proves no rule is BITING today, not that the bucket
    carries no rule at all. A rule added tomorrow with a TTL longer than the oldest object would be invisible
    here — which is exactly why `EXEMPTIONS["checkpoint_expiring"]` exists as a parameter rather than as an
    assumption this probe retires.
    """
    if s3 is None:
        import boto3
        s3 = boto3.client("s3")
    rows, classes, oldest = [], set(), None
    for pfx in (prefixes or checkpoint_prefixes()):
        try:
            page = s3.list_objects_v2(Bucket=bucket, Prefix=pfx, MaxKeys=sample)
        except Exception as e:  # noqa: BLE001
            rows.append({"prefix": pfx, "error": f"{type(e).__name__}: {e}"[:200]})
            continue
        objs = page.get("Contents") or []
        if not objs:
            rows.append({"prefix": pfx, "n_objects": 0})
            continue
        ages = []
        for o in objs:
            classes.add(o.get("StorageClass") or "STANDARD")
            try:
                ages.append((time.time() - o["LastModified"].timestamp()) / 86400.0)
            except Exception:  # noqa: BLE001
                continue
        if ages:
            rows.append({"prefix": pfx, "n_objects": len(objs), "oldest_age_days": round(max(ages), 1),
                         "newest_age_days": round(min(ages), 2)})
            oldest = max(ages) if oldest is None else max(oldest, max(ages))
    return (round(oldest, 1) if oldest is not None else None), sorted(classes), rows


def durability_probe(bucket=None, s3=None):
    """Is a checkpoint destroyed by waiting? Returns a dict; prints it.

    ★ WHY THIS IS A PROBE AND NOT A SENTENCE IN A DOCSTRING (CLAUDE.md §4). The entire case for holding a
    relaunch is "the checkpoint is a durable object and waiting cannot destroy it". That claim has exactly one
    way to be false — an S3 lifecycle rule that expires or transitions the checkpoint prefixes. `probably no
    lifecycle rule` is a hypothesis; a real read is a diagnosis. Two reads are attempted, in order of strength:
    the bucket's lifecycle configuration, and — when the identity is not authorised for it, which is the
    measured case here — the observed age and storage class of the checkpoint objects themselves.
    """
    b = bucket or os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
    if s3 is None:
        import boto3
        s3 = boto3.client("s3")
    out = {"bucket": b, "utc": _utcnow()}
    try:
        cfg = s3.get_bucket_lifecycle_configuration(Bucket=b)
        out["rules"] = cfg.get("Rules") or []
        out["has_expiry_rule"] = any(("Expiration" in r or "NoncurrentVersionExpiration" in r)
                                     and r.get("Status") == "Enabled" for r in out["rules"])
    except Exception as e:  # noqa: BLE001 — NoSuchLifecycleConfiguration is the ANSWER, not an error
        out["rules"] = []
        out["error"] = f"{type(e).__name__}: {e}"
        # `NoSuchLifecycleConfiguration` is a definitive NO. Anything else (AccessDenied, a network failure)
        # is UNKNOWN, and an unknown must not be reported as a clean bill of health — that is how a claim
        # gets made on the absence of evidence rather than on evidence of absence.
        out["has_expiry_rule"] = False if "NoSuchLifecycleConfiguration" in str(e) else None
    if out["has_expiry_rule"] is None:
        # The policy is unreadable, so ask the DATA. `oldest_age_days` far past any plausible TTL, with every
        # object still in STANDARD, is direct evidence that nothing is expiring or tiering these prefixes.
        oldest, classes, rows = observed_object_ages(b, s3=s3)
        out.update({"fallback": "observed object ages + storage classes (ListObjectsV2), because "
                                "GetBucketLifecycleConfiguration is not permitted to this identity",
                    "oldest_checkpoint_age_days": oldest, "storage_classes": classes, "prefixes": rows})
        if oldest is None:
            out["verdict"] = ("UNKNOWN — neither the lifecycle configuration nor the checkpoint objects could "
                              "be read, so the premise 'waiting cannot destroy a checkpoint' is UNVERIFIED.")
        else:
            # ★ THE ARGUMENT THAT ACTUALLY CLOSES, and it is NOT "the objects look old enough".
            # Measured 2026-07-27: the oldest checkpoint object is only ~2.6 days old, which on its own would
            # NOT exclude a 7- or 30-day TTL — these lanes are young. What closes the question is the
            # combination with a fact about S3 itself: **lifecycle expiration is expressed in DAYS, with a
            # minimum of 1**, so the shortest rule that can exist is 24 h. A hold here is bounded by
            # RELAUNCH_ESCALATE_H before it stops being the gate's decision and becomes trimcrae's, and that
            # window is a small fraction of the shortest possible TTL. So a hold cannot straddle an expiry
            # boundary that this listing does not already exclude — and any rule long enough to be invisible
            # here is far longer than any hold the gate is allowed to sustain unattended.
            out["escalation_window_h"] = RELAUNCH_ESCALATE_H
            out["verdict"] = (
                f"HOLDING IS SAFE, and not because {oldest} days looks old — these lanes are young enough "
                f"that {oldest} days alone would not exclude a 7- or 30-day TTL. It is safe because S3 "
                f"lifecycle expiration is expressed in DAYS with a MINIMUM OF 1, so the shortest rule that "
                f"can exist is 24 h, while a hold escalates to a human at {RELAUNCH_ESCALATE_H:.0f} h — a "
                f"fraction of that floor. The listing independently excludes any 1- or 2-day rule (objects "
                f"{oldest} days old survive) and any transition rule (every listed object is in {classes}; a "
                f"checkpoint tiered to GLACIER is still there but no longer resumable on demand, which would "
                f"be an expiry in every sense that counts here). WEAKER THAN READING THE POLICY and stated "
                f"as such: this shows no rule acting today. `EXEMPTIONS['checkpoint_expiring']` stays a "
                f"parameter for exactly that residual.")
    elif out["has_expiry_rule"]:
        out["verdict"] = ("A checkpoint on this bucket has a hard expiry — the `checkpoint_expiring` "
                          "exemption is LIVE and every lane must set `checkpoint_expires_utc`.")
    else:
        out["verdict"] = ("No enabled expiration rule on this bucket: a checkpoint does not expire while a "
                          "relaunch waits, so holding defers the rental without losing work. This is the "
                          "evidence behind the gate's premise.")
    print(json.dumps(out, indent=2, default=str))
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--durability-probe" in argv:
        i = argv.index("--durability-probe")
        bucket = argv[i + 1] if len(argv) > i + 1 and not argv[i + 1].startswith("-") else None
        return 0 if durability_probe(bucket) else 0
    if "--price" in argv:
        # Ad-hoc: what would a single-host rental cost right now against the drift line? Rents nothing.
        from ternary_vast_launch import resource_spec
        hold, doc = gate("adhoc", "adhoc", resource_spec())
        print(json.dumps(doc, indent=2))
        return 1 if hold else 0
    print(__doc__)
    print("usage: relaunch_market_gate.py [--price | --durability-probe [BUCKET]]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
