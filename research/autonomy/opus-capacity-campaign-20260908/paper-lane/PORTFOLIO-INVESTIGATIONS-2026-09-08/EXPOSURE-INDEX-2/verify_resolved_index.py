#!/usr/bin/env python3
"""Verifier for EXPOSURE-INDEX-2. Reads ONLY the emitted v2 JSON and the source index.
Enforces EXPOSURE-INDEX's original invariants, this lane's additional ones, and re-runs
the LOCOREGIONAL-2 control from the v2 rows. Non-zero exit on any failure."""
import json, collections, sys
fail = []
def ck(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond: fail.append(msg)

d = json.load(open("emc-patient-exposure-index-v2.json"))
rows = d["rows"]
byid = {r["row_id"]: r for r in rows}

print("A. inherited invariants (EXPOSURE-INDEX's own)")
ck(len(rows) == 28, "28 rows preserved")
ck(all(r["retrieval_completeness"] in ("complete","partial","unread") for r in rows),
   "retrieval_completeness three-valued on every row")
ck(all("overlap_unknown" in r for r in rows), "overlap_unknown present on every row")
ck(sum(1 for r in rows if r["overlap_unknown"] is True) == 24,
   "overlap_unknown=true still on 24 rows (NO flag changed by this lane)")
ck(all(r["n_emc_quoted_from"] for r in rows if r["n_emc_status"] == "reported"),
   "every reported n_emc names a source")
zeros = [r for r in rows if r["n_emc_patients_as_reported"] == 0]
ck(all("Preclinical" in (r["n_emc_quote"] or "") or "No human patient" in (r["n_emc_quote"] or "")
       for r in zeros), "no zero without a measured-zero justification (zeros: %d)" % len(zeros))

print("B. no total-shaped key anywhere in the file")
BAD = ("total_patients","pooled","portfolio_total","sum_of_n","overall_n","aggregate_n",
       "distinct_patients","grand_total","n_total")
def walk(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items():
            kl = str(k).lower()
            for b in BAD:
                if b in kl: fail.append("total-shaped key %s at %s" % (k, path))
            walk(v, path + "." + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, "%s[%d]" % (path, i))
walk({k: v for k, v in d.items() if k != "control_locoregional2"})
ck(not any("total-shaped" in f for f in fail), "no total-shaped key outside the sanctioned control")

print("C. this lane's own invariants")
unk = [r for r in rows if r["n_emc_status"] == "UNKNOWN"]
ck(all("resolution_2026_09_09" in r for r in unk),
   "every surviving UNKNOWN row records WHY it is still unknown (%d rows)" % len(unk))
ck(all(r["resolution_2026_09_09"]["reason_code"] in
       ("identity_not_established_no_admitted_call_attributable",
        "no_pmc_record_abstract_only","tables_stripped_from_returned_body") for r in unk),
   "every surviving UNKNOWN carries an admitted reason code")
res = [r for r in rows if r.get("resolution_2026_09_09",{}).get("outcome") == "reported"]
ck(len(res) == 5, "exactly 5 rows resolved by this lane")
ck(all(r["resolution_2026_09_09"].get("quote") and r["resolution_2026_09_09"].get("locator")
       for r in res), "every resolved row carries a verbatim quote AND a locator")
ck(all(r["resolution_2026_09_09"]["overlap_unknown_change"].startswith("NONE") for r in res),
   "no resolved row changed an overlap_unknown flag")
ck(byid["chow2007"]["n_emc_status"] == "UNKNOWN",
   "chow2007 refusal UPHELD (not overturned to 0)")
ck(byid["maki2005bortezomib"]["n_emc_status"] == "UNKNOWN",
   "maki2005 protected row UPHELD (UNKNOWN, never zero)")
ck(byid["boklan2025carfilzomib"]["n_emc_status"] == "UNKNOWN",
   "boklan2025 unread-not-absent row UPHELD")
ck(byid["higuchi2023zaltoprofen"]["n_emc_patients_as_reported"] == 0,
   "higuchi2023 remains the only measured zero")

print("D. LOCOREGIONAL-2 control -- re-derived FROM THIS INDEX'S ROWS")
c = d["control_locoregional2"]
led = json.load(open("../LOCOREGIONAL-2/rt-local-control-contrast-ledger-k2.json"))
arms = led["arm_level_event_ledger"]
tot_n = tot_e = 0
for a in arms:
    sid = a["source_id"]
    ck(sid in byid, "ledger arm source %r is a row in this index" % sid)
    for arm, n in a["arm_sizes"].items():
        e = a["arm_events"][arm]
        tot_n += n; tot_e += e
        print("       %-14s %-28s n=%-4d events=%d" % (sid, arm, n, e))
    ck(sum(a["arm_events"].values()) == a["events_total_printed"],
       "%s arm events sum to its printed total" % sid)
ck(tot_n == 175, "control patients = 175 (got %d)" % tot_n)
ck(tot_e == 21, "control local recurrences = 21 (got %d)" % tot_e)
ck(len(set(a["source_id"] for a in arms)) == 2, "the sanctioned sum spans exactly TWO rows")
# CORRECTED after checks/10 (exit 1). The licence for this one sum is NOT the row-level
# overlap_unknown flag -- bishop2019 carries overlap_unknown=true ("may overlap ussc2022").
# It is a PAIRWISE, CONTRAST-SCOPED ruling in a named source file. Test that, not the flag.
lic = d["control_locoregional2"]["\u26d4_why_this_arithmetic_is_permitted_when_the_index_forbids_totals"]
ck("FOR THIS CONTRAST" in lic, "the sum's licence is explicitly contrast-scoped, not row-level")
ck("NEVER be summed into any total" in lic,
   "the licence explicitly forbids widening this sum beyond the pair")
ck(byid["bishop2019"]["overlap_unknown"] is True,
   "bishop2019 KEEPS overlap_unknown=true -- the pairwise licence does not clear the row flag")
ck(byid["masunaga2025"]["overlap_unknown"] is False,
   "masunaga2025 overlap_unknown=false on its own named-source basis")
for other in ("ussc2022","remiszewski2025","seer270_2022","uMich2023"):
    ck(other not in d["control_locoregional2"]["rows_used"],
       "%s is NOT in the sanctioned sum (the licence names it as forbidden)" % other)

print("E. the control's inputs are now primary-verified, not only curated")
for sid in ("bishop2019","masunaga2025"):
    cv = byid[sid]["resolution_2026_09_09"].get("control_verification")
    ck(bool(cv), "%s carries a primary control_verification block" % sid)

print()
if fail:
    print("FAILURES: %d" % len(fail))
    for f in fail: print("  -", f)
    sys.exit(1)
print("ALL CHECKS PASS")
sys.exit(0)
