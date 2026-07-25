#!/usr/bin/env python3
"""Backtest the adaptive reservation-price policy against its alternatives on a SYNTHETIC market.

WHAT THIS DOES AND DOES NOT SHOW. The price process here is INVENTED (diurnal + weekly + noise), because no real
Vast price history exists yet — the sampler that will produce one only starts when it reaches main. So this
validates the ALGORITHM — does it cold-start from zero knowledge, converge as it observes, respect the deadline,
and beat the alternatives on the same path? — and NOT the size of any saving on the real market. Re-run it
against `vast-price-history.jsonl` once that series exists; the numbers below are not a forecast.

Benchmarks, in increasing order of information:
  * ADAPTIVE            — starts knowing nothing; only sees prices as they arrive.
  * best FIXED threshold — knows the true price distribution F perfectly, but must use ONE threshold for all time.
  * incumbent x1.9      — the current policy, anchored on the last observed floor.
  * always on-demand    — buy immediately, every time.
  * CLAIRVOYANT         — the true lower bound: knows the whole realised path and buys the W cheapest hours.

Deterministic (seeded). Pure stdlib. Runs anywhere, spends nothing.
"""
import math, random, sys
sys.path.insert(0, ".")
import vast_bid_optimizer as vbo

random.seed(7)
HOURS, OD = 24*21, 0.60          # 3 weeks, on-demand ceiling
def price(t):                     # diurnal + weekly + noise, bounded (0, OD]
    diurnal = 0.5 + 0.5*math.sin(2*math.pi*(t % 24)/24 - 1.2)
    weekly  = 0.85 + 0.15*math.sin(2*math.pi*(t % (24*7))/(24*7))
    p = 0.10 + 0.42*diurnal*weekly + random.gauss(0, 0.03)
    return max(0.05, min(OD, p))
PATH = [price(t) for t in range(HOURS)]

def run(policy, W=60.0, deadline=HOURS):
    """Buy 1 GPU-h per accepted hour until W done. Returns (spend, hours_waited, finished)."""
    spend, done, obs = 0.0, 0.0, []
    for t in range(deadline):
        p = PATH[t]
        obs.append(p)                                  # observation is FREE and non-committal
        if done >= W: break
        P = policy(obs[:-1], W-done, deadline-t)       # decide BEFORE seeing today's price
        if P is not None and p <= P:
            spend += p; done += 1.0
    return spend, t, done >= W

adaptive = lambda o, w, T: vbo.adaptive_reservation_price(o, OD, w, T)["reservation_price"]
fixed19  = lambda o, w, T: min(o[-1]*1.9, OD) if o else OD      # incumbent, anchored on last seen floor
ondemand = lambda o, w, T: OD                                    # always buy
oracle_q = sorted(PATH)[int(0.25*len(PATH))]
best_fixed = lambda o, w, T: oracle_q            # BEST FIXED THRESHOLD given perfect knowledge of F
CLAIRVOYANT = sum(sorted(PATH)[:60])             # true lower bound: buy the 60 cheapest hours of the path

print(f"synthetic market: min ${min(PATH):.3f}  median ${sorted(PATH)[len(PATH)//2]:.3f}  max ${max(PATH):.3f}  on-demand ${OD}")
print(f"work = 60 GPU-h, horizon = {HOURS} h (slack: duty cycle {60/HOURS:.2f})\n")
print(f"CLAIRVOYANT lower bound (60 cheapest hours of the realised path): ${CLAIRVOYANT:.2f} "
      f"(${CLAIRVOYANT/60:.4f}/GPU-h)\n")
print(f"{'policy':<30} {'spend':>8} {'$/GPU-h':>9} {'done':>6} {'vs clairvoyant':>15}")
for name, pol in (("ADAPTIVE (cold start)", adaptive),
                  ("best FIXED threshold (knows F)", best_fixed),
                  ("incumbent min_bid x1.9", fixed19),
                  ("always on-demand", ondemand)):
    sp, t, ok = run(pol)
    print(f"{name:<30} ${sp:>7.2f} {sp/60:>9.4f} {str(ok):>6} {sp/CLAIRVOYANT:>14.2f}x")

print("\nadaptive threshold as it learns (first 10 decisions, then every 48 h):")
obs=[]
for t in range(0, HOURS):
    obs.append(PATH[t])
    if t < 10 or t % 48 == 0:
        o = vbo.adaptive_reservation_price(obs[:-1], OD, 60.0, HOURS-t)
        print(f"  t={t:>4}h n={o['n_observations']:>4}  P*=${str(o['reservation_price']):<7} phase={o['phase']}")
