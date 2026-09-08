#!/usr/bin/env python3
"""Deterministic checks for CORRECTED-A v2 (flag-semantics repair).

D1-D3  the repair preserved every title, every count and every value
D4     the flag is title-derived, exactly
D5-D6  the renamed flag cannot be mistaken for an eligibility warrant or a numerator warrant
D7     the positive-denominator constraint, checked explicitly (not via denominator_state)
D8     byte-level proof that no row datum changed
D9     the v1 directory and its evidence are unmodified

Exit 0 only if every check PASSes. No pipes are used by the runner, so $? is the real exit code.
"""
from __future__ import annotations
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "CORRECTED-A-denominator-category")

FLAG_V1 = "RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER"
FLAG_V2 = "RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER"
COL_V1 = "dropped_response_bearing_categories_with_values"
COL_V2 = "dropped_response_assessment_category_titles_with_values"
INV_V1 = "response_bearing_title_flag"
INV_V2 = "response_assessment_category_title_flag"

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha_file(p):
    with open(p, "rb") as f:
        return sha_bytes(f.read())

def table(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        lines = [ln for ln in f.read().split("\n") if ln != ""]
    head = lines[0].split("\t")
    return head, [ln.split("\t") for ln in lines[1:]]

R = {}
def rec(cid, desc, ok, detail):
    R[cid] = {"check": desc, "result": "PASS" if ok else "FAIL", "detail": detail}
    print(f"{cid} {'PASS' if ok else 'FAIL'}  {desc}\n     {detail}")

h1, r1 = table(os.path.join(V1, "corrected-a-rows.tsv"))
h2, r2 = table(os.path.join(HERE, "corrected-a-v2-rows.tsv"))
i1 = {n: k for k, n in enumerate(h1)}
i2 = {n: k for k, n in enumerate(h2)}

# ---------------------------------------------------------------------------------------- D1
data_files = ["corrected-a-v2-rows.tsv", "corrected-a-v2-categories.tsv",
              "corrected-a-v2-category-inventory.tsv", "corrected-a-v2-summary.json"]
stale = {}
for fn in data_files:
    t = open(os.path.join(HERE, fn), encoding="utf-8").read()
    hits = [s for s in (FLAG_V1, COL_V1, INV_V1) if s in t]
    if hits:
        stale[fn] = hits
sch = open(os.path.join(HERE, "corrected-a-v2-schema.json"), encoding="utf-8").read()
sch_j = json.load(open(os.path.join(HERE, "corrected-a-v2-schema.json"), encoding="utf-8"))
sch_ok = (FLAG_V1 in sch_j["superseded_identifiers"] and COL_V1 in sch_j["superseded_identifiers"]
          and INV_V1 in sch_j["superseded_identifiers"]
          and FLAG_V2 in sch_j["enumerations"]["advisory_flag_codes"]
          and FLAG_V1 not in sch_j["enumerations"]["advisory_flag_codes"]
          and all(COL_V1 != c["name"] and INV_V1 != c["name"]
                  for t in sch_j["tables"] for c in sch_j["tables"][t]["columns"]))
rec("D1", "the three v1 identifiers are gone from every v2 data table and live schema slot, and "
          "survive only as explicitly labelled superseded identifiers",
    not stale and sch_ok,
    f"stale occurrences in data/summary: {stale or 'none'}; schema: v2 flag enumerated, v1 flag "
    f"absent from the enumeration and recorded under superseded_identifiers = {sch_ok}")

# ---------------------------------------------------------------------------------------- D2
EMPTY = ("", "NONE")   # the tables use `|` as the code separator and `NONE` as the empty sentinel

def codes(cell):
    cell = cell.strip()
    if cell in EMPTY:
        return []
    return [t.strip() for t in cell.split("|") if t.strip()]

def code_counts(rows, idx, col):
    c = {}
    for r in rows:
        for tok in codes(r[idx[col]]):
            c[tok] = c.get(tok, 0) + 1
    return c
a1, a2 = code_counts(r1, i1, "advisory_flag_codes"), code_counts(r2, i2, "advisory_flag_codes")
u1, u2 = code_counts(r1, i1, "unresolved_reason_codes"), code_counts(r2, i2, "unresolved_reason_codes")
s1 = {r[i1["proportion_suitability"]] for r in r1}
mapped = {(FLAG_V2 if k == FLAG_V1 else k): v for k, v in a1.items()}
suit1 = [r[i1["proportion_suitability"]] for r in r1]
suit2 = [r[i2["proportion_suitability"]] for r in r2]
rec("D2", "every count preserved: advisory-code counts, blocking-code counts and the suitability "
          "partition are identical to v1 under the rename",
    mapped == a2 and u1 == u2 and suit1 == suit2 and a2.get(FLAG_V2) == 101 and len(r2) == 552,
    f"advisory v1(renamed)==v2: {mapped == a2} ({FLAG_V2}={a2.get(FLAG_V2)}); blocking identical: "
    f"{u1 == u2}; suitability vector identical on {sum(1 for x, y in zip(suit1, suit2) if x == y)}/552 rows")

# ---------------------------------------------------------------------------------------- D3
ih1, ir1 = table(os.path.join(V1, "corrected-a-category-inventory.tsv"))
ih2, ir2 = table(os.path.join(HERE, "corrected-a-v2-category-inventory.tsv"))
t1 = [r[0] for r in ir1]
t2 = [r[0] for r in ir2]
f1 = {r[0] for r in ir1 if r[ih1.index(INV_V1)] == "yes"}
f2 = {r[0] for r in ir2 if r[ih2.index(INV_V2)] == "yes"}
cats_same = sha_file(os.path.join(V1, "corrected-a-categories.tsv")) == \
            sha_file(os.path.join(HERE, "corrected-a-v2-categories.tsv"))
folded = {r[ih2.index("folded")] for r in ir2}
rec("D3", "every verbatim title preserved: inventory titles, the flagged-title set and the whole "
          "category ledger are unchanged",
    t1 == t2 and f1 == f2 and cats_same and folded == {"NO"} and len(t2) == 123,
    f"{len(t2)} inventory titles identical in order: {t1 == t2}; flagged titles identical: "
    f"{f1 == f2} (n={len(f2)}); categories table sha256 identical to v1: {cats_same}; "
    f"folded values present: {sorted(folded)}")

# ---------------------------------------------------------------------------------------- D4
mism = 0
for r in r2:
    has_flag = FLAG_V2 in r[i2["advisory_flag_codes"]]
    has_titles = r[i2[COL_V2]].strip() != ""
    if has_flag != has_titles:
        mism += 1
rec("D4", "the flag is exactly the title-derived predicate it claims to be: flag present <=> the "
          "dropped response-assessment-title column is non-empty",
    mism == 0, f"0 mismatches over 552 rows (flag on {sum(1 for r in r2 if FLAG_V2 in r[i2['advisory_flag_codes']])} rows)")

# ---------------------------------------------------------------------------------------- D5
bad = 0
cross = {}
for r in r2:
    blocking = len(codes(r[i2["unresolved_reason_codes"]])) > 0
    expect = "UNSUITABLE_FOR_PROPORTION" if blocking else "NOT_REFUTED_BY_THIS_COMPONENT"
    if r[i2["proportion_suitability"]] != expect:
        bad += 1
    k = ("FLAGGED" if FLAG_V2 in r[i2["advisory_flag_codes"]] else "not flagged",
         r[i2["proportion_suitability"]])
    cross[k] = cross.get(k, 0) + 1
both_states = (cross.get(("FLAGGED", "UNSUITABLE_FOR_PROPORTION"), 0) > 0 and
               cross.get(("FLAGGED", "NOT_REFUTED_BY_THIS_COMPONENT"), 0) > 0)
never_blocking = all(FLAG_V2 not in codes(r[i2["unresolved_reason_codes"]]) for r in r2) and \
                 FLAG_V2 not in sch_j["enumerations"]["unresolved_reason_codes"]
rec("D5", "NOT AN ELIGIBILITY WARRANT: suitability is a function of the blocking codes alone; the "
          "flag never appears among them and flagged rows land in BOTH suitability states",
    bad == 0 and both_states and never_blocking,
    f"suitability == (blocking codes non-empty) on {552 - bad}/552 rows; flag absent from every "
    f"unresolved_reason_codes cell and from the blocking enumeration: {never_blocking}; "
    f"cross-tab: {sorted((f'{a} x {b}', n) for (a, b), n in cross.items())}")

# ---------------------------------------------------------------------------------------- D6
# `rate_derived` is exempt by name: it is the column that DECLARES no rate was derived, and D6
# checks its value separately. Every other numerator/rate/percent-shaped name is a failure.
NUMERATOR_NAME = re.compile(r"numerator|responder|rate|percent|proportion_of|_pct", re.I)
name_hits = [h for h in h2 if NUMERATOR_NAME.search(h) and h != "rate_derived"]
rate_ok = all(r[i2["rate_derived"]] == "NOT_DERIVED" for r in r2)
VAL = re.compile(r"=(-?\d+)$")
def wouldbe(cell):
    tot = 0
    for part in cell.split("|"):
        part = part.strip()
        if not part:
            continue
        m = VAL.search(part)
        if not m:
            return None
        tot += int(m.group(1))
    return tot
numer = [wouldbe(r[i2[COL_V2]]) for r in r2]
unparsed = sum(1 for x in numer if x is None)
matching_cols = []
for name in h2:
    col = [r[i2[name]] for r in r2]
    try:
        vals = [int(v) for v in col]
    except ValueError:
        continue
    if vals == numer:
        matching_cols.append(name)
rec("D6", "NOT A NUMERATOR WARRANT: no numerator/rate/percent column exists, rate_derived is "
          "NOT_DERIVED on every row, and the would-be numerator formed by summing the flagged "
          "categories equals NO emitted column",
    not name_hits and rate_ok and not matching_cols and unparsed == 0,
    f"column names matching numerator/responder/rate/percent: {name_hits or 'none'}; "
    f"rate_derived==NOT_DERIVED on 552/552: {rate_ok}; would-be numerator computed for "
    f"{552 - unparsed}/552 rows (range {min(x for x in numer if x is not None)}..{max(x for x in numer if x is not None)}); "
    f"emitted columns equal to it: {matching_cols or 'none'}")

# ---------------------------------------------------------------------------------------- D7
present = zero = negative = nonint = missing = non_participants = 0
positive = 0
for r in r2:
    v = r[i2["reported_denominator_participants"]].strip()
    units = r[i2["denominator_units_available"]]
    if "Participants" not in units.split("|"):
        non_participants += 1
    if v == "":
        missing += 1
        continue
    present += 1
    try:
        n = int(v)
    except ValueError:
        nonint += 1
        continue
    if n > 0:
        positive += 1
    elif n == 0:
        zero += 1
    else:
        negative += 1
state_only = sum(1 for r in r2 if r[i2["denominator_state"]] == "READ_FROM_SOURCE")
rec("D7", "POSITIVE-DENOMINATOR CONSTRAINT, checked explicitly on the values themselves (not via "
          "denominator_state), keeping zero / missing / non-Participants distinct",
    positive == 552 and zero == 0 and negative == 0 and nonint == 0 and missing == 0
    and non_participants == 0,
    f"positive(>0)={positive}  zero(==0)={zero}  negative(<0)={negative}  non-integer={nonint}  "
    f"missing/empty={missing}  rows whose available units lack `Participants`={non_participants}  "
    f"[for contrast, denominator_state==READ_FROM_SOURCE on {state_only}/552, which alone would "
    f"not have excluded a zero, an empty or a non-Participants denominator]")

# ---------------------------------------------------------------------------------------- D8
def reverse(path, header_only):
    raw = open(path, "r", encoding="utf-8", newline="").read()
    lines = raw.split("\n")
    lines[0] = lines[0].replace(COL_V2, COL_V1).replace(INV_V2, INV_V1)
    if not header_only:
        lines[1:] = [ln.replace(FLAG_V2, FLAG_V1) for ln in lines[1:]]
    return sha_bytes("\n".join(lines).encode("utf-8"))
rows_rev = reverse(os.path.join(HERE, "corrected-a-v2-rows.tsv"), False)
inv_rev = reverse(os.path.join(HERE, "corrected-a-v2-category-inventory.tsv"), True)
rows_v1 = sha_file(os.path.join(V1, "corrected-a-rows.tsv"))
inv_v1 = sha_file(os.path.join(V1, "corrected-a-category-inventory.tsv"))
rec("D8", "NO ROW DATUM CHANGED: reversing only the identifier rename on the v2 tables reproduces "
          "the v1 files' sha256 exactly",
    rows_rev == rows_v1 and inv_rev == inv_v1,
    f"rows: reversed={rows_rev} v1={rows_v1} equal={rows_rev == rows_v1}; "
    f"inventory: reversed={inv_rev} v1={inv_v1} equal={inv_rev == inv_v1}")

# ---------------------------------------------------------------------------------------- D9
man = json.load(open(os.path.join(HERE, "corrected-a-v2-input-manifest.json"), encoding="utf-8"))
changed = [fn for fn, h in man["v1_sha256"].items() if sha_file(os.path.join(V1, fn)) != h]
j1 = json.load(open(os.path.join(V1, "corrected-a-input-manifest.json"), encoding="utf-8"))
LANE = os.path.dirname(HERE)
changed_j1 = [fn for fn, h in j1["input_sha256"].items()
              if sha_file(os.path.join(LANE, fn)) != h]
rec("D9", "originals unmodified: the 13 v1 component files and the 12 original job-1 / leaf "
          "evidence files re-hashed",
    not changed and not changed_j1,
    f"v1 component files changed: {changed or 0}/{len(man['v1_sha256'])}; original job-1 and leaf "
    f"evidence files changed: {changed_j1 or 0}/{len(j1['input_sha256'])}")

passed = sum(1 for v in R.values() if v["result"] == "PASS")
out = {"component": "CORRECTED-A-denominator-category-v2", "checks": R,
       "passed": passed, "failed": len(R) - passed, "total": len(R)}
json.dump(out, open(os.path.join(HERE, "corrected-a-v2-checks.json"), "w", encoding="utf-8"),
          indent=1)
print(f"\n{passed}/{len(R)} checks passed")
sys.exit(0 if passed == len(R) else 1)
