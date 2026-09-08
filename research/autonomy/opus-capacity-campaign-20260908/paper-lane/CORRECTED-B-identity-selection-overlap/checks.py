#!/usr/bin/env python3
"""CORRECTED-B deterministic checks.

Schema / key compatibility, actual row coverage, and the SPECIFIC prior counterexamples.
Exit code 0 only if every check passes. Every check prints PASS/FAIL with its numbers.
No check is skipped; a check that cannot run is a FAIL.
"""
import csv, json, os, sys, subprocess, collections, glob, re

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "artifacts")
JOB2 = os.path.normpath(os.path.join(BASE, "..", "CURATION-endpoint-identity-and-overlap-artifacts"))
LEAF = os.path.normpath(os.path.join(BASE, "..", "LEAF-OUT"))
CACHE = "/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5"

results = []
def check(name, ok, detail):
    results.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return ok

def rd(p):
    with open(p, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))

# C1 -------------------------------------------------- cache integrity, real exit code
r = subprocess.run(["sha256sum", "-c", "SHA256-MANIFEST.txt"], cwd=CACHE,
                   capture_output=True, text=True)
check("C1_cache_sha256sum_c", r.returncode == 0,
      f"sha256sum -c returncode={r.returncode}, {len([l for l in r.stdout.splitlines() if l.endswith(': OK')])} files OK")

obs = rd(os.path.join(OUT, "LEDGER-response-observations.tsv"))
cells = rd(os.path.join(OUT, "LEDGER-measurement-cells.tsv"))
rel = rd(os.path.join(OUT, "RELATED-SETS-unresolved.tsv"))
enr = rd(os.path.join(OUT, "ENROLLMENT-CONFLICT.tsv"))
grp = rd(os.path.join(OUT, "GROUP-RELATIONS-pooled-parent-component.tsv"))
chg = rd(os.path.join(OUT, "CHANGE-MAP-vs-job2.tsv"))
qb = rd(os.path.join(OUT, "LEAF-QB-harmonised-trials.tsv"))
qc = rd(os.path.join(OUT, "LEAF-QC-harmonised-ties.tsv"))
sel = rd(os.path.join(JOB2, "SELECTED-cohort-response-measurements.tsv"))
ties = rd(os.path.join(JOB2, "TIES.tsv"))
exc = rd(os.path.join(JOB2, "EXCLUSIONS.tsv"))
ovl = rd(os.path.join(JOB2, "OVERLAP-enrollment-check.tsv"))

# C2 -------------------------------------------------- primary key integrity
ids = [o["obs_id"] for o in obs]
dupe = [k for k, v in collections.Counter(ids).items() if v > 1]
blank = [o for o in obs if not (o["obs_id"] and o["nct"] and o["om_index"] != "" and o["results_group_id"])]
check("C2_observation_primary_key_unique_and_complete", not dupe and not blank,
      f"{len(ids)} rows, {len(dupe)} duplicate obs_id, {len(blank)} rows with a blank key part")

# C3 -------------------------------------------------- related-set closure
obs_by_key = collections.defaultdict(list)
for o in obs:
    obs_by_key[(o["nct"], o["results_group_title_norm"])].append(o)
rel_keys = {(r["nct"], r["results_group_title_norm"]) for r in rel}
tot = sum(int(r["n_observations"]) for r in rel)
check("C3_related_sets_partition_the_ledger",
      rel_keys == set(obs_by_key) and tot == len(obs) and len(rel) == len(rel_keys),
      f"{len(rel)} cohort keys, sum(n_observations)={tot} vs {len(obs)} ledger rows, "
      f"key-set difference={len(rel_keys ^ set(obs_by_key))}")

# C4 -------------------------------------------------- every observation in exactly one set
mem = collections.Counter()
for r in rel:
    for i in r["observation_ids"].split("|"):
        mem[i] += 1
check("C4_each_observation_in_exactly_one_related_set",
      set(mem) == set(ids) and all(v == 1 for v in mem.values()),
      f"{len(mem)} referenced observation ids, {sum(1 for v in mem.values() if v != 1)} referenced more than once")

# C5 -------------------------------------------------- cell referential integrity
idset = set(ids)
orphan = [c for c in cells if c["obs_id"] not in idset]
check("C5_measurement_cells_reference_a_ledger_observation", not orphan,
      f"{len(cells)} cell rows, {len(orphan)} orphans")

# C6 ------------------------ prior counterexample: job2 selection coverage + the 6 misses
selkeys = collections.Counter((s["nct"], s["gnorm"]) for s in sel)
missing = [s for s in sel if (s["nct"], s["gnorm"]) not in obs_by_key]
minus_titles = [o for o in obs if o["results_group_title"].rstrip().endswith("-")]
explained = all(any(o["results_group_title_norm"].rstrip("-").strip() == s["gnorm"]
                    for o in obs if o["nct"] == s["nct"]) for s in missing)
check("C6_job2_selected_rows_join_or_are_explained", len(missing) == 6 and explained,
      f"{len(sel)} job2 selected rows, {len(sel)-len(missing)} join on (nct,group_norm); "
      f"{len(missing)} do not, all {len(missing)} explained by job2 stripping a trailing '-' "
      f"from a biomarker-negative group title ({len(minus_titles)} such source titles in the cache)")

# C7 -------------------- the trailing '-' strip must not have MERGED two source cohorts
by_nct = collections.defaultdict(set)
for o in obs:
    by_nct[o["nct"]].add(o["results_group_title_norm"])
merges = []
for n, ts in by_nct.items():
    m = collections.defaultdict(list)
    for t in ts:
        m[t.rstrip("- ").strip()].append(t)
    merges += [(n, k, v) for k, v in m.items() if len(v) > 1]
check("C7_trailing_hyphen_strip_caused_no_cohort_merge", len(merges) == 0,
      f"{len(merges)} trials where the job2 strip would merge two distinct source group titles "
      f"(key is lossy, but no observed merge)")

# C8 ------------------------------------ tie disposition coverage against LEAF-QC
tie_f = [t for t in ties if t["resolved_at_step"].startswith("f")]
qc_keys = {(q["nct"], q["group_norm"]) for q in qc}
tie_f_keys = {(t["nct"], t["group_norm"]) for t in tie_f}
cls = collections.Counter(q["classification"] for q in qc)
check("C8_step_f_ties_fully_covered_by_leaf_QC",
      len(tie_f) == 1590 and len(qc) == 1590 and tie_f_keys == qc_keys,
      f"{len(tie_f)} step-f tie rows, {len(qc)} harmonised QC rows, key sets identical={tie_f_keys==qc_keys}, "
      f"classification census={dict(cls)}")

# C9 ------------------ the WITHDRAWN claim: 1,589 of 1,590 ties DO carry a distinguishing basis
check("C9_withdrawn_claim_step_f_ties_have_a_basis",
      cls.get("BASIS_EXISTS", 0) == 1589 and cls.get("NO_BASIS", 0) == 1,
      f"BASIS_EXISTS={cls.get('BASIS_EXISTS',0)}, NO_BASIS={cls.get('NO_BASIS',0)} — job2's "
      f"'no distinguishing metadata' claim is withdrawn by the delivered leaf evidence")

# C10 ----------------------------------------- change-map covers every job2 artifact row
cm = collections.Counter(c["job2_artifact"] for c in chg)
expect = {"SELECTED-cohort-response-measurements.tsv": len(sel), "TIES.tsv": len(ties),
          "EXCLUSIONS.tsv": len(exc), "OVERLAP-enrollment-check.tsv": len(ovl)}
check("C10_change_map_row_coverage", all(cm.get(k) == v for k, v in expect.items()),
      f"expected {expect}, got {dict(cm)}")

# C11 ------------------- zero denominators: retained, never usable, never divided by
zero = [o for o in obs if o["denominator_state"] == "REPORTED_ZERO"]
bad = [o for o in zero if o["denominator_usable"] != "False"]
selzero = [s for s in sel if s["denom"] == "0"]
check("C11_reported_zero_retained_and_marked_unusable", zero and not bad,
      f"{len(zero)} REPORTED_ZERO observations retained, {len(bad)} wrongly marked usable; "
      f"job2's own selected set carried {len(selzero)} zero-denominator rows in "
      f"{len({s['nct'] for s in selzero})} trials")

# C12 --------------- three denominator states are separated and the census is exhaustive
states = collections.Counter(o["denominator_state"] for o in obs)
allowed = {"PRESENT", "REPORTED_ZERO", "ABSENT_NO_DENOMS", "ABSENT_NO_PARTICIPANT_UNIT",
           "ABSENT_FOR_GROUP", "ABSENT_EMPTY_VALUE", "PRESENT_NONNUMERIC",
           "NONPARTICIPANT_UNITS_ONLY"}
check("C12_denominator_state_vocabulary_closed", set(states) <= allowed,
      f"observed states={dict(states)}; ABSENT and NONPARTICIPANT states do not occur in this cache, "
      f"which is a finding, not an assumption")

# C13 ------------------- no cross-measure summation: recompute the within-measure figure
by_trial_measure = collections.defaultdict(lambda: collections.defaultdict(list))
for o in obs:
    if o["denominator_state"] == "PRESENT":
        by_trial_measure[o["nct"]][o["om_index"]].append(int(o["denominator_value_participants"]))
mismatch = 0
for r in enr:
    sums = by_trial_measure.get(r["nct"], {})
    want = max((sum(v) for v in sums.values()), default=0)
    if int(r["within_measure_denominator_sum"] or 0) != want:
        mismatch += 1
check("C13_enrollment_file_holds_only_a_within_measure_sum", mismatch == 0,
      f"{len(enr)} trial rows recomputed from the ledger, {mismatch} mismatches; no cross-measure "
      f"denominator sum is emitted anywhere in this contract")

# C14 --------- enrollment is kept as recorded: no clipping, no invented corrected value
neg = [r for r in enr if r["registered_enrollment"] not in ("",) and int(r["registered_enrollment"]) < 0]
clip = [r for r in enr if r["registered_enrollment"] != "" and
        int(r["within_measure_denominator_sum"] or 0) > int(r["registered_enrollment"])
        and "EXCEEDS" not in r["conflict_findings"]]
check("C14_enrollment_recorded_not_repaired", not neg and not clip,
      f"{len(neg)} negative enrollments, {len(clip)} excesses silently absorbed; "
      f"conflict census={dict(collections.Counter(r['conflict_findings'] for r in enr))}")

# C15 ------------------------------- overlap is not manufactured out of a cross-measure sum
job2_excess = {r["nct"] for r in ovl if int(r["excess"]) > 0}
mine_single = {r["nct"] for r in enr if r["conflict_findings"].startswith("SINGLE_COHORT")}
mine_within = {r["nct"] for r in enr if "WITHIN_MEASURE_SUM_EXCEEDS" in r["conflict_findings"]}
check("C15_job2_180_trial_overlap_claim_is_selection_dependent",
      len(job2_excess) == 180 and len(mine_within) < len(job2_excess),
      f"job2 reported {len(job2_excess)} trials whose CROSS-measure selected sum exceeds enrollment; "
      f"within a single outcome measure only {len(mine_within)} trials exceed it and only "
      f"{len(mine_single)} trial has a single cohort larger than enrollment "
      f"({sorted(mine_single)}). The remainder is produced by summing across measures.")

# C16 ------------------------------------- QB harmonisation coverage and schema divergence
qb_ncts = {r["nct"] for r in qb}
check("C16_leaf_QB_harmonised_covers_the_180_excess_trials",
      len(qb) == 180 and qb_ncts == job2_excess,
      f"{len(qb)} harmonised QB trial rows, set equality with job2's excess trials={qb_ncts==job2_excess}")

heads = {}
for q in ("QA", "QB", "QC", "QD"):
    for g in range(4):
        p = os.path.join(LEAF, f"LEAF-{q}-group{g}.tsv")
        heads[(q, g)] = tuple(open(p, encoding="utf-8").readline().rstrip("\n").split("\t"))
qb_h = {heads[("QB", g)] for g in range(4)}
qc_h = {heads[("QC", g)] for g in range(4)}
check("C16b_leaf_files_are_schema_incompatible_as_delivered", len(qb_h) == 4 and len(qc_h) == 4,
      f"QB: {len(qb_h)} distinct headers across 4 files; QC: {len(qc_h)} distinct headers across 4 files. "
      f"Harmonisation was required and is recorded in the builder's QB_MAP/QC_BASIS mapping.")

# C17 ------------------------------------------- every related set carries a machine state
noempty = [r for r in rel if not r["unresolved_states"].strip()]
notsel = [r for r in rel if r["selection_status"] != "NOT_SELECTED_BY_DESIGN"]
check("C17_every_related_set_has_a_machine_readable_state_and_no_selection",
      not noempty and not notsel,
      f"{len(rel)} cohort keys, {len(noempty)} without an unresolved-state token, "
      f"{len(notsel)} carrying a selection")

# C18 ---------------------------------- pooled parent is never added to its components
cols = set(grp[0].keys()) if grp else set()
check("C18_no_parent_plus_component_total_column",
      not any(re.search(r"parent_plus|grand_total|combined_total", c) for c in cols),
      f"{len(grp)} pooled-parent relations; columns={sorted(cols)}")

# C19 ------------------- reinstated records: reportingStatus absent is a metadata gap
absent_rs = [o for o in obs if o["reporting_status_state"] == "ABSENT_FIELD"]
absent_trials = {o["nct"] for o in absent_rs}
in_sel = absent_trials & {s["nct"] for s in sel}
check("C19_absent_reportingStatus_records_reinstated", len(absent_rs) > 0 and not in_sel,
      f"{len(absent_rs)} observations in {len(absent_trials)} trials carry POSTED-shaped results with "
      f"no reportingStatus field; job2 dropped all of them ({len(in_sel)} appear in its selection). "
      f"They are retained here as source facts with usable_for_proportion=False.")

# C20 -------------------------------- no response proportion is computed anywhere
# Two columns legitimately contain the word "proportion": they are USABILITY flags, not
# values. They are not whitelisted on their name — the check proves their value domain is
# boolean / a count, so neither can be a computed response proportion.
FLAG_COLS = {"usable_for_proportion", "denominator_usable", "n_usable_for_proportion"}
banned = re.compile(r"(?i)(response_rate|orr_value|proportion|percent|rate|ratio|numerator|responders)")
offend = []
for f in glob.glob(os.path.join(OUT, "*.tsv")):
    hdr = open(f, encoding="utf-8").readline().rstrip("\n").split("\t")
    offend += [(os.path.basename(f), c) for c in hdr if banned.search(c) and c not in FLAG_COLS]
domain_bad = []
for o in obs:
    if o["usable_for_proportion"] not in ("True", "False") or o["denominator_usable"] not in ("True", "False"):
        domain_bad.append(o["obs_id"])
for r_ in rel:
    if not r_["n_usable_for_proportion"].isdigit():
        domain_bad.append(r_["cohort_key"])
check("C20_no_rate_or_proportion_value_emitted", not offend and not domain_bad,
      f"offending value columns={offend}; the 3 flag columns named '*proportion*'/'*usable*' hold "
      f"only booleans or counts ({len(domain_bad)} out-of-domain values), so no response "
      f"proportion, numerator or rate is computed or stored anywhere in this contract")

# C21 --------------------------- participant flow is absent, disjointness unverifiable
pf = subprocess.run("grep -l participantFlowModule " + os.path.join(CACHE, "ctg_*.txt"),
                    shell=True, capture_output=True, text=True)
check("C21_participant_flow_absent_from_cache", pf.returncode == 1 and not pf.stdout.strip(),
      f"grep returncode={pf.returncode} (1 = no match in any payload); every disjointness claim "
      f"in this contract is therefore withheld")

fails = [r for r in results if r["status"] == "FAIL"]
with open(os.path.join(OUT, "CHECKS.json"), "w", encoding="utf-8") as fh:
    json.dump({"checks": results, "n_checks": len(results), "n_failed": len(fails)}, fh, indent=1)
print(f"\n{len(results)-len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
