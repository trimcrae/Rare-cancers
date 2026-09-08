#!/usr/bin/env python3
"""CORRECTED-B builder — identity / selection / overlap long-form evidence ledger.

Reads ONLY the frozen ClinicalTrials.gov cache (12 payloads) already delivered to this
session. No network access of any kind. Emits new sibling artifacts; never rewrites
job1/job2/job3 outputs.

Design commitments (from the admitting memo):
  * NO endpoint, RECIST version, time point, population or measure is preferred.
  * NO single-record-per-cohort selection is performed. Competing records are retained
    as an explicitly related set with machine-readable unresolved states.
  * Denominator states are three-way separated: ABSENT / REPORTED_ZERO / NONPARTICIPANT
    (plus ABSENT_FOR_GROUP and PRESENT / PRESENT_NONNUMERIC).
  * Parent(pooled)/component relations are recorded; they are NEVER summed as
    independent people.
  * ACTUAL enrollment is kept as recorded; conflicts are recorded, not repaired.
"""
import json, os, re, sys, glob, csv, hashlib, unicodedata
from collections import defaultdict, Counter

CACHE = "/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "artifacts")
JOB2 = os.path.normpath(os.path.join(BASE, "..", "CURATION-endpoint-identity-and-overlap-artifacts"))
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- source read
def load_payload(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    marker = "=" * 70
    i = raw.index(marker)
    return json.loads(raw[i + len(marker):].lstrip("\n"))

PAYLOADS = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CACHE, "ctg_*.txt")))

# ------------------------------------------------------------- normalisation
_STRIP = ".,;:!?"
def gnorm(s):
    s = unicodedata.normalize("NFKC", s or "").casefold()
    s = re.sub(r"\s+", " ", s).strip()
    return s.strip(_STRIP).strip()

# --------------------------------------------------- vocabularies (source-bound)
# Inclusion boundary retained IDENTICAL to job2 so the change map joins 1:1.
JOB2_RESPONSE_RE = re.compile(
    r"\b(overall response|objective response|best overall response|response rate|orr\b|"
    r"disease control rate|clinical benefit rate)", re.I)
# Boundary-sensitivity probe only. NOT used to include or exclude any ledger row.
WIDER_RESPONSE_RE = re.compile(
    r"\b(complete response|partial response|tumou?r response|response|remission rate|"
    r"disease control|clinical benefit|dcr\b|cbr\b|bor\b|recist)", re.I)

# Endpoint constructs are recorded SEPARATELY and are never merged into one endpoint.
CONSTRUCTS = [
    ("ORR", r"\b(objective response rate|overall response rate|orr)\b"),
    ("OVERALL_RESPONSE", r"\boverall response\b(?! rate)"),
    ("OBJECTIVE_RESPONSE", r"\bobjective response\b(?! rate)"),
    ("BOR", r"\bbest overall response\b|\bbor\b"),
    ("DCR", r"\bdisease control rate\b|\bdcr\b"),
    ("CBR", r"\bclinical benefit rate\b|\bcbr\b"),
    ("RESPONSE_RATE_GENERIC", r"\bresponse rate\b"),
    ("RESPONSE_CATEGORY_DIST", r"\b(complete response|partial response|stable disease|progressive disease|cr\b|pr\b|sd\b|pd\b)"),
    ("DURATION_OF_RESPONSE", r"\bduration of response\b|\bdor\b"),
    ("TIME_TO_RESPONSE", r"\btime to response\b"),
]
CONSTRUCTS = [(k, re.compile(v, re.I)) for k, v in CONSTRUCTS]

CRITERIA = [
    ("iRECIST", r"\birecist\b"),
    ("irRECIST", r"\birrecist\b|\bir-recist\b"),
    ("mRECIST", r"\bmrecist\b|\bmodified recist\b"),
    ("RECIST", r"\brecist\b"),
    ("irRC", r"\birrc\b|\bimmune[- ]related response criteria\b"),
    ("WHO", r"\bwho criteria\b"),
    ("CHESON", r"\bcheson\b"),
    ("IWG", r"\biwg\b|\binternational working group\b"),
    ("IMWG", r"\bimwg\b"),
    ("IWCLL", r"\biwcll\b"),
    ("LUGANO", r"\blugano\b"),
    ("RANO", r"\brano\b"),
    ("PERCIST", r"\bpercist\b"),
    ("EORTC", r"\beortc\b"),
    ("CHOI", r"\bchoi\b"),
    ("MACDONALD", r"\bmacdonald\b"),
    ("EBMT", r"\bebmt\b"),
    ("INRC", r"\binrc\b"),
    ("RECIL", r"\brecil\b"),
    ("PCWG", r"\bpcwg\b|\bprostate cancer working group\b"),
]
CRITERIA = [(k, re.compile(v, re.I)) for k, v in CRITERIA]
VERSION_RE = re.compile(r"\b(?:v(?:ersion)?\.?\s*)?(1\.0|1\.1|1\.2|2\.0|4\.0|5\.0)\b", re.I)

# Text-derived qualifiers. Recorded as DERIVED flags, never as source fields.
FLAG_RES = {
    "itt": re.compile(r"\b(intent[- ]to[- ]treat|intention[- ]to[- ]treat|itt|full analysis set|fas)\b", re.I),
    "pp": re.compile(r"\b(per[- ]protocol|pp population|evaluable|efficacy[- ]evaluable|response[- ]evaluable)\b", re.I),
    "confirmed": re.compile(r"\bconfirmed\b", re.I),
    "unconfirmed": re.compile(r"\bunconfirmed\b", re.I),
    "central": re.compile(r"\b(independent|central|blinded independent|bicr|irc|iac)\b", re.I),
    "investigator": re.compile(r"\binvestigator\b", re.I),
}
POOLED_RE = re.compile(r"^(total|overall|all participants|all patients|all subjects|combined)\b", re.I)
NONCOLLECTION_RE = re.compile(
    r"(not collected|were not collected|no data (were|was)? ?collected|not analy[sz]ed|"
    r"data collection did not|no participants were analy|not performed|was not assessed|"
    r"no results are reported|study was terminated|terminated (early|prior)|"
    r"no participants (were )?enrolled|zero participants)", re.I)

def find_all(pats, text):
    return [k for k, rx in pats if rx.search(text or "")]

def is_int(v):
    try:
        int(str(v).strip()); return True
    except Exception:
        return False

def tsv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        for r in rows:
            w.writerow(["" if x is None else str(x).replace("\t", " ").replace("\n", " ")
                        for x in r])
    return path

# ============================================================ PASS 1 — identity
# Which payload copies carry each nctId, and which copy is canonical (R0').
appearances = defaultdict(list)      # nct -> [payload]
score = {}                            # (nct,payload) -> score tuple
for pname in PAYLOADS:
    data = load_payload(os.path.join(CACHE, pname))
    for st in data.get("studies", []):
        ps = st.get("protocolSection", {}) or {}
        nct = ((ps.get("identificationModule") or {}).get("nctId"))
        if not nct:
            continue
        appearances[nct].append(pname)
        sc = (1 if st.get("resultsSection") else 0, len(ps), len(json.dumps(st, sort_keys=True)))
        score[(nct, pname)] = sc
    del data

canonical = {}
for nct, plist in appearances.items():
    best = sorted(plist, key=lambda p: (tuple(-x for x in score[(nct, p)]), p))[0]
    canonical[nct] = best

dup_ncts = {n: p for n, p in appearances.items() if len(p) > 1}

# ============================================================ PASS 2 — ledger
obs_rows, cell_rows, group_rows, enroll_rows = [], [], [], []
cohort_index = defaultdict(list)     # (nct,gnorm) -> obs dict
stats = Counter()
scope_probe = Counter()
id_reuse_rows = []

OBS_HEADER = [
    "obs_id", "nct", "canonical_payload", "all_payloads", "om_index", "om_type",
    "om_reporting_status", "om_title", "om_description", "om_population_description",
    "om_time_frame", "om_param_type", "om_unit_of_measure", "om_dispersion_type",
    "om_denom_units_all", "om_calculate_pct", "om_denom_units_selected",
    "results_group_id", "results_group_title", "results_group_title_norm",
    "results_group_description", "n_groups_in_om",
    "denominator_state", "denominator_value_participants", "denominator_units_used",
    "nonparticipant_units_present", "class_level_denoms_present",
    "endpoint_constructs", "assessment_criteria", "criteria_version_tokens",
    "derived_flag_itt", "derived_flag_pp", "derived_flag_confirmed",
    "derived_flag_unconfirmed", "derived_flag_central", "derived_flag_investigator",
    "pooled_label_flag", "noncollection_statement", "noncollection_evidence",
    "n_classes", "class_titles", "n_categories_total", "category_titles",
    "reporting_status_state", "denominator_usable", "usable_for_proportion",
    "unusable_reason", "source_pointer",
]

CELL_HEADER = [
    "obs_id", "nct", "canonical_payload", "om_index", "results_group_id",
    "class_index", "class_title", "category_index", "category_title",
    "measurement_value_raw", "measurement_spread", "measurement_lower",
    "measurement_upper", "measurement_comment", "om_param_type", "om_unit_of_measure",
    "class_denom_units", "class_denom_value_for_group", "source_pointer",
]

for pname in PAYLOADS:
    data = load_payload(os.path.join(CACHE, pname))
    for st in data.get("studies", []):
        ps = st.get("protocolSection", {}) or {}
        nct = ((ps.get("identificationModule") or {}).get("nctId"))
        if not nct or canonical.get(nct) != pname:
            continue
        stats["canonical_studies"] += 1
        design = ps.get("designModule", {}) or {}
        einfo = design.get("enrollmentInfo", {}) or {}
        arms = (ps.get("armsInterventionsModule", {}) or {}).get("armGroups", []) or []
        rs = st.get("resultsSection", {}) or {}
        oms = (rs.get("outcomeMeasuresModule", {}) or {}).get("outcomeMeasures", []) or []
        if rs:
            stats["canonical_studies_with_results"] += 1

        # results-group-id reuse across measures inside one study (identity failure)
        id2titles = defaultdict(set)
        trial_obs = []
        for oi, om in enumerate(oms):
            title = om.get("title", "") or ""
            for g in om.get("groups", []) or []:
                id2titles[g.get("id")].add(gnorm(g.get("title", "")))
            if WIDER_RESPONSE_RE.search(title):
                scope_probe["wider_match_measures"] += 1
            if not JOB2_RESPONSE_RE.search(title):
                continue
            scope_probe["job2_scope_measures"] += 1
            desc = om.get("description", "") or ""
            popd = om.get("populationDescription", "") or ""
            blob = " ".join([title, desc, popd])
            constructs = find_all(CONSTRUCTS, title + " " + desc)
            criteria = find_all(CRITERIA, blob)
            versions = sorted(set(m.group(1) for m in VERSION_RE.finditer(blob)))
            flags = {k: bool(rx.search(blob)) for k, rx in FLAG_RES.items()}
            if flags["unconfirmed"]:
                flags["confirmed"] = bool(re.search(r"(?<!un)\bconfirmed\b", blob, re.I))
            nc = NONCOLLECTION_RE.search(blob)

            denoms = om.get("denoms", []) or []
            part_denom = None
            other_units = []
            for d in denoms:
                u = (d.get("units") or "").strip()
                if u.casefold() == "participants":
                    part_denom = {c.get("groupId"): c.get("value") for c in (d.get("counts") or [])}
                else:
                    other_units.append(u)
            classes = om.get("classes", []) or []
            class_denom_map = {}
            for ci, cl in enumerate(classes):
                for d in cl.get("denoms", []) or []:
                    for c in d.get("counts") or []:
                        class_denom_map[(ci, c.get("groupId"))] = ((d.get("units") or ""), c.get("value"))
            groups = om.get("groups", []) or []
            for g in groups:
                gid = g.get("id")
                gt = g.get("title", "") or ""
                gn = gnorm(gt)
                if part_denom is None:
                    dv, state = None, ("NONPARTICIPANT_UNITS_ONLY" if other_units
                                       else ("ABSENT_NO_DENOMS" if not denoms else "ABSENT_NO_PARTICIPANT_UNIT"))
                    units_used = "|".join(sorted(set(other_units)))
                elif gid not in part_denom:
                    dv, state, units_used = None, "ABSENT_FOR_GROUP", "Participants"
                else:
                    raw = part_denom[gid]
                    units_used = "Participants"
                    if raw is None or str(raw).strip() == "":
                        dv, state = None, "ABSENT_EMPTY_VALUE"
                    elif is_int(raw):
                        dv = int(raw)
                        state = "REPORTED_ZERO" if dv == 0 else "PRESENT"
                    else:
                        dv, state = None, "PRESENT_NONNUMERIC"
                den_usable = state == "PRESENT"
                usable = den_usable
                reason = "" if den_usable else state
                rs_raw = om.get("reportingStatus")
                rs_state = ("POSTED" if rs_raw == "POSTED"
                            else ("ABSENT_FIELD" if rs_raw in (None, "") else str(rs_raw)))
                if rs_state != "POSTED":
                    usable = False
                    reason = (reason + "|" if reason else "") + "REPORTING_STATUS_" + rs_state
                if nc:
                    reason = (reason + "|" if reason else "") + "NONCOLLECTION_STATEMENT"
                obs_id = f"{nct}#om{oi}#{gid}"
                ptr = f"{pname}::{nct}::outcomeMeasures[{oi}]::groups[{gid}]"
                cat_titles, n_cat = [], 0
                for ci, cl in enumerate(classes):
                    for cj, cat in enumerate(cl.get("categories", []) or []):
                        n_cat += 1
                        ct = cat.get("title", "")
                        if ct:
                            cat_titles.append(ct)
                        for m in cat.get("measurements", []) or []:
                            if m.get("groupId") != gid:
                                continue
                            cd = class_denom_map.get((ci, gid), ("", ""))
                            cell_rows.append([
                                obs_id, nct, pname, oi, gid, ci, cl.get("title", ""), cj, ct,
                                m.get("value", ""), m.get("spread", ""), m.get("lowerLimit", ""),
                                m.get("upperLimit", ""), m.get("comment", ""),
                                om.get("paramType", ""), om.get("unitOfMeasure", ""),
                                cd[0], cd[1],
                                ptr + f"::classes[{ci}]::categories[{cj}]",
                            ])
                row = [
                    obs_id, nct, pname, "|".join(sorted(appearances[nct])), oi,
                    om.get("type", ""), om.get("reportingStatus", ""), title, desc, popd,
                    om.get("timeFrame", ""), om.get("paramType", ""),
                    om.get("unitOfMeasure", ""), om.get("dispersionType", ""),
                    "|".join(sorted({(d.get("units") or "") for d in denoms})),
                    om.get("calculatePct", ""), om.get("denomUnitsSelected", ""),
                    gid, gt, gn, g.get("description", ""), len(groups),
                    state, "" if dv is None else dv, units_used,
                    bool(other_units), bool(class_denom_map),
                    "|".join(constructs), "|".join(criteria), "|".join(versions),
                    flags["itt"], flags["pp"], flags["confirmed"], flags["unconfirmed"],
                    flags["central"], flags["investigator"],
                    bool(POOLED_RE.match(gn)), bool(nc), (nc.group(0) if nc else ""),
                    len(classes), "|".join(sorted({(c.get("title") or "") for c in classes if c.get("title")})),
                    n_cat, "|".join(sorted(set(cat_titles))[:12]),
                    rs_state, den_usable, usable, reason, ptr,
                ]
                obs_rows.append(row)
                d_obs = dict(zip(OBS_HEADER, row))
                cohort_index[(nct, gn)].append(d_obs)
                trial_obs.append(d_obs)

        for gid, titles in id2titles.items():
            if len(titles) > 1:
                id_reuse_rows.append([nct, pname, gid, len(titles), "|".join(sorted(titles))])

        # ---- enrollment conflict, recorded WITHOUT any cross-measure summation
        if trial_obs:
            enr = einfo.get("count")
            etype = einfo.get("type", "")
            per_measure = defaultdict(list)
            for o in trial_obs:
                if o["denominator_state"] == "PRESENT":
                    per_measure[o["om_index"]].append(o)
            max_single = 0; max_single_ptr = ""
            worst_sum = 0; worst_om = ""; worst_pooled = False; worst_n = 0
            for oi, lst in per_measure.items():
                s = sum(int(o["denominator_value_participants"]) for o in lst)
                pooled = any(o["pooled_label_flag"] in (True, "True") for o in lst)
                if s > worst_sum:
                    worst_sum, worst_om, worst_pooled, worst_n = s, oi, pooled, len(lst)
                for o in lst:
                    v = int(o["denominator_value_participants"])
                    if v > max_single:
                        max_single, max_single_ptr = v, o["source_pointer"]
            enr_i = enr if isinstance(enr, int) else None
            findings = []
            if enr_i is None:
                findings.append("ENROLLMENT_ABSENT")
            else:
                if max_single > enr_i:
                    findings.append("SINGLE_COHORT_EXCEEDS_ENROLLMENT__INTERNAL_INCONSISTENCY__INFERENCE_STOPPED")
                if worst_sum > enr_i:
                    findings.append("WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT" +
                                    ("__POOLED_LABEL_IN_MEASURE" if worst_pooled else ""))
            enroll_rows.append([
                nct, pname, enr_i if enr_i is not None else "", etype,
                len(arms), len({o["results_group_title_norm"] for o in trial_obs}),
                len(trial_obs), max_single, max_single_ptr,
                worst_om, worst_n, worst_sum, worst_pooled,
                "|".join(findings) if findings else "NO_CONFLICT_DETECTED",
                "NOT_A_PATIENT_COUNT__NO_CROSS_MEASURE_SUM_EMITTED",
                "DISJOINTNESS_UNVERIFIABLE__NO_participantFlowModule_IN_CACHE",
            ])
    del data

# ============================================ related sets + unresolved states
REL_HEADER = [
    "cohort_key", "nct", "results_group_title_norm", "n_observations",
    "observation_ids", "om_indices", "distinct_om_types", "distinct_titles",
    "distinct_time_frames", "distinct_constructs", "distinct_criteria",
    "distinct_criteria_versions", "distinct_population_descriptions",
    "distinct_param_types", "distinct_units", "distinct_denominator_values",
    "distinct_denominator_states", "n_usable_for_proportion",
    "duplicate_encoding_candidate", "unresolved_states", "selection_status",
    "resolution_note",
]
rel_rows = []
def uniq(vals):
    out = []
    for v in vals:
        if v not in out:
            out.append(v)
    return out

for (nct, gn), obs in sorted(cohort_index.items()):
    titles = uniq([o["om_title"] for o in obs])
    tfs = uniq([o["om_time_frame"] for o in obs])
    cons = uniq([o["endpoint_constructs"] for o in obs])
    crit = uniq([o["assessment_criteria"] for o in obs])
    vers = uniq([o["criteria_version_tokens"] for o in obs])
    pops = uniq([o["om_population_description"] for o in obs])
    pts = uniq([o["om_param_type"] for o in obs])
    units = uniq([o["om_unit_of_measure"] for o in obs])
    dens = uniq([str(o["denominator_value_participants"]) for o in obs])
    dsts = uniq([o["denominator_state"] for o in obs])
    types = uniq([o["om_type"] for o in obs])
    n_usable = sum(1 for o in obs if str(o["usable_for_proportion"]) == "True")
    unresolved = []
    if len(obs) > 1:
        if len(titles) > 1: unresolved.append("UNRESOLVED_MULTIPLE_MEASURE_TITLES")
        if len(cons) > 1: unresolved.append("UNRESOLVED_MULTIPLE_ENDPOINT_CONSTRUCTS")
        if len(tfs) > 1: unresolved.append("UNRESOLVED_MULTIPLE_TIME_FRAMES")
        if len(crit) > 1 or len(vers) > 1: unresolved.append("UNRESOLVED_MULTIPLE_ASSESSMENT_CRITERIA")
        if len(pops) > 1: unresolved.append("UNRESOLVED_MULTIPLE_POPULATION_DESCRIPTIONS")
        if len(dens) > 1: unresolved.append("UNRESOLVED_MULTIPLE_DENOMINATORS")
        if len(pts) > 1 or len(units) > 1: unresolved.append("UNRESOLVED_MULTIPLE_PARAMTYPE_OR_UNIT")
        if len(types) > 1: unresolved.append("UNRESOLVED_MULTIPLE_OUTCOME_TYPES")
    dup = (len(obs) > 1 and len(titles) == 1 and len(tfs) == 1 and len(cons) == 1
           and len(crit) == 1 and len(vers) == 1 and len(pops) == 1 and len(dens) == 1
           and len(pts) == 1 and len(units) == 1)
    if dup:
        unresolved.append("DUPLICATE_ENCODING_CANDIDATE")
    if n_usable == 0:
        unresolved.append("NO_OBSERVATION_USABLE_FOR_A_PROPORTION")
    if len(obs) == 1 and not unresolved:
        unresolved.append("SINGLE_OBSERVATION")
    if len(obs) > 1 and not unresolved:
        unresolved.append("UNRESOLVED_NO_DISTINGUISHING_FIELD_FOUND")
    rel_rows.append([
        f"{nct}||{gn}", nct, gn, len(obs), "|".join(o["obs_id"] for o in obs),
        "|".join(str(o["om_index"]) for o in obs), "|".join(types), len(titles),
        len(tfs), len(cons), len(crit), len(vers), len(pops), len(pts), len(units),
        "|".join(dens), "|".join(dsts), n_usable, dup, "|".join(unresolved),
        "NOT_SELECTED_BY_DESIGN",
        "This contract approves no preferred endpoint, criteria version, time point, "
        "population or single-record-per-cohort rule. The set is retained whole.",
    ])

# ============================================ pooled parent / component relations
GRP_HEADER = [
    "nct", "relation_type", "parent_cohort_key", "parent_denominator",
    "component_cohort_keys", "component_denominators", "component_sum",
    "registered_enrollment", "enrollment_type", "arithmetic_note", "source_pointer",
]
grp_rows = []
by_trial = defaultdict(list)
for (nct, gn), obs in cohort_index.items():
    by_trial[nct].append((gn, obs))
enroll_by_nct = {r[0]: (r[2], r[3]) for r in enroll_rows}
for nct, cohorts in sorted(by_trial.items()):
    pooled = [(gn, obs) for gn, obs in cohorts if POOLED_RE.match(gn)]
    if not pooled:
        continue
    comps = [(gn, obs) for gn, obs in cohorts if not POOLED_RE.match(gn)]
    if not comps:
        continue
    enr, etype = enroll_by_nct.get(nct, ("", ""))
    for gn, obs in pooled:
        pv = uniq([str(o["denominator_value_participants"]) for o in obs
                   if o["denominator_state"] == "PRESENT"])
        cdv, cks = [], []
        for cgn, cobs in comps:
            vals = uniq([str(o["denominator_value_participants"]) for o in cobs
                         if o["denominator_state"] == "PRESENT"])
            cks.append(f"{nct}||{cgn}")
            cdv.append("/".join(vals) if vals else "NA")
        csum = sum(int(v.split("/")[0]) for v in cdv if v != "NA" and v.split("/")[0].isdigit())
        grp_rows.append([
            nct, "POOLED_PARENT_WITH_COMPONENTS", f"{nct}||{gn}", "/".join(pv) or "NA",
            "|".join(cks), "|".join(cdv), csum, enr, etype,
            "component_sum is shown ONLY to expose double counting against the parent; "
            "parent and components are the SAME people and are never added together.",
            f"{canonical[nct]}::{nct}",
        ])

# ============================================ change / disposition map vs job2
CHG_HEADER = ["job2_artifact", "job2_key", "job2_value_summary", "corrected_b_disposition",
              "corrected_b_key", "reason"]
chg_rows = []
sel_path = os.path.join(JOB2, "SELECTED-cohort-response-measurements.tsv")
sel = list(csv.DictReader(open(sel_path, encoding="utf-8"), delimiter="\t"))
obs_by_key = defaultdict(list)
for r in obs_rows:
    d = dict(zip(OBS_HEADER, r))
    obs_by_key[(d["nct"], d["results_group_title_norm"])].append(d)
sel_join_hit = sel_join_miss = 0
sel_obs_present = sel_obs_absent = 0
for r in sel:
    key = (r["nct"], r["gnorm"])
    hit = obs_by_key.get(key)
    if hit:
        sel_join_hit += 1
    else:
        sel_join_miss += 1
    exact = [o for o in (hit or []) if str(o["om_index"]) == r["om"]]
    if exact:
        sel_obs_present += 1
    else:
        sel_obs_absent += 1
    chg_rows.append([
        "SELECTED-cohort-response-measurements.tsv", f"{r['nct']}||{r['gnorm']}||om{r['om']}",
        f"type={r['type']};denom={r['denom']};resolved_by={r['resolved_by']}",
        ("RETAINED_AS_ONE_MEMBER_OF_A_RELATED_SET__SELECTION_WITHDRAWN" if exact
         else ("COHORT_RETAINED__SELECTED_OM_NOT_MATCHED" if hit else "NOT_JOINED")),
        f"{r['nct']}||{r['gnorm']}",
        "job2's single selected record per cohort is not adopted; all competing records "
        "are retained and the choice is left unresolved.",
    ])
ties = list(csv.DictReader(open(os.path.join(JOB2, "TIES.tsv"), encoding="utf-8"), delimiter="\t"))
qc = {}
for g in range(4):
    p = os.path.normpath(os.path.join(BASE, "..", "LEAF-OUT", f"LEAF-QC-group{g}.tsv"))
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
        qc[(r["nct"], r["group_norm"])] = (g, r.get("classification", ""))
tie_f = [t for t in ties if t["resolved_at_step"].startswith("f")]
for t in ties:
    step = t["resolved_at_step"]
    k = (t["nct"], t["group_norm"])
    if step.startswith("f"):
        g, cls = qc.get(k, ("", "NOT_IN_QC"))
        disp = ("WITHDRAWN__LEAF_QC_FOUND_A_DISTINGUISHING_BASIS" if cls == "BASIS_EXISTS"
                else "WITHDRAWN__NO_BASIS_FOUND_BUT_TIE_BREAK_STILL_NOT_EVIDENCE"
                if cls == "NO_BASIS" else "WITHDRAWN__NOT_COVERED_BY_QC")
        reason = ("job2's claim that step-f ties carry no distinguishing metadata is "
                  f"withdrawn; LEAF-QC-group{g} classification={cls}. The tie-break is "
                  "not adopted and no replacement selection is made.")
    else:
        disp = "SELECTION_WITHDRAWN__COMPETING_RECORDS_RETAINED"
        reason = "ladder steps a-e are not adopted as an endpoint/population preference."
    chg_rows.append(["TIES.tsv", f"{t['nct']}||{t['group_norm']}",
                     f"step={step};competing={t['candidates_still_competing']}",
                     disp, f"{t['nct']}||{t['group_norm']}", reason])
exc = list(csv.DictReader(open(os.path.join(JOB2, "EXCLUSIONS.tsv"), encoding="utf-8"), delimiter="\t"))
exc_reinstated = 0
for r in exc:
    reason = r["reason"]
    if reason.startswith("reportingStatus"):
        disp = "REINSTATED_AS_SOURCE_FACT__RETAINED_UNUSABLE"
        exc_reinstated += 1
        why = ("a non-POSTED response measure is retained in the ledger as a source record "
               "with usable_for_proportion=False, not deleted.")
    elif reason == "no response-titled outcome":
        disp = "UPHELD__OUTSIDE_THE_JOB2_TITLE_BOUNDARY"
        why = "retained as an explicit inclusion-boundary limitation, not as an absence of data."
    else:
        disp = "UPHELD__NO_RESULTS_SECTION_IN_CACHE"
        why = "the cached record carries no resultsSection; nothing was re-fetched."
    chg_rows.append(["EXCLUSIONS.tsv", f"{r['nct']}||om{r['outcome_index']}", reason,
                     disp, "", why])
ovl = list(csv.DictReader(open(os.path.join(JOB2, "OVERLAP-enrollment-check.tsv"), encoding="utf-8"), delimiter="\t"))
for r in ovl:
    chg_rows.append(["OVERLAP-enrollment-check.tsv", r["nct"],
                     f"sum={r['sum_selected_denominators']};enrollment={r['registered_enrollment']};excess={r['excess']}",
                     "NOT_ADOPTED__CROSS_MEASURE_SUM_IS_NOT_A_PATIENT_COUNT",
                     r["nct"],
                     "the excess is recorded as a conflict between fields, not as proof of "
                     "overlap; no corrected enrollment and no clipping is produced."])

# ============================================ harmonised leaf tables (QB, QC)
QB_MAP = {
 0: {"nct":"nct","mechanism":"mechanism","reducible":"reducible","enrollment":"registered_enrollment",
     "enrollment_type":"enrollment_type","cohorts":"selected_cohorts","sum":"sum_selected_denominators",
     "excess":"excess","row_type":"row_type","trial_tag":"TRIAL"},
 1: {"nct":"nct","mechanism":"mechanism","reducible":"reducible","enrollment":"registered_enrollment",
     "enrollment_type":"enrollment_type","cohorts":"selected_cohorts","sum":"sum_selected_denominators",
     "excess":"excess","row_type":"row_type","trial_tag":"TRIAL"},
 2: {"nct":"nct","mechanism":"mechanism","reducible":"reducible_to_nonoverlapping","enrollment":"registered_enrollment",
     "enrollment_type":"enrollment_type","cohorts":"selected_cohorts","sum":"sum_selected_denominators",
     "excess":"excess","row_type":"row_type","trial_tag":"TRIAL"},
 3: {"nct":"nct","mechanism":"mechanism","reducible":"reducible_to_non_overlapping_set","enrollment":"enrollment",
     "enrollment_type":"enrollment_type","cohorts":"selected_cohorts","sum":"sum_selected_denominators",
     "excess":"excess","row_type":"level","trial_tag":"TRIAL"},
}
qb_rows = []
qb_seen = set()
for g in range(4):
    p = os.path.normpath(os.path.join(BASE, "..", "LEAF-OUT", f"LEAF-QB-group{g}.tsv"))
    m = QB_MAP[g]
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
        rt = (r.get(m["row_type"]) or "").strip().upper()
        if rt not in ("TRIAL", "T", "TRIAL_SUMMARY"):
            continue
        nct = r[m["nct"]]
        qb_seen.add(nct)
        qb_rows.append([nct, g, r.get(m["mechanism"], ""), r.get(m["reducible"], ""),
                        r.get(m["enrollment"], ""), r.get(m["enrollment_type"], ""),
                        r.get(m["cohorts"], ""), r.get(m["sum"], ""), r.get(m["excess"], ""),
                        f"LEAF-QB-group{g}.tsv"])
qc_rows = []
QC_BASIS = {0: "distinguishing_fields", 1: "basis_fields", 2: "distinguishing_field", 3: "distinguishing_fields"}
QC_CHANGE = {0: "would_change_selection", 1: "selection_effect", 2: "would_change_selection", 3: "would_change_selection"}
for g in range(4):
    p = os.path.normpath(os.path.join(BASE, "..", "LEAF-OUT", f"LEAF-QC-group{g}.tsv"))
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
        qc_rows.append([r["nct"], r["group_norm"], g, r.get("classification", ""),
                        r.get(QC_BASIS[g], ""), r.get(QC_CHANGE[g], ""),
                        f"LEAF-QC-group{g}.tsv"])

# ============================================ write
tsv(os.path.join(OUT, "LEDGER-response-observations.tsv"), OBS_HEADER, obs_rows)
tsv(os.path.join(OUT, "LEDGER-measurement-cells.tsv"), CELL_HEADER, cell_rows)
tsv(os.path.join(OUT, "RELATED-SETS-unresolved.tsv"), REL_HEADER, rel_rows)
tsv(os.path.join(OUT, "GROUP-RELATIONS-pooled-parent-component.tsv"), GRP_HEADER, grp_rows)
tsv(os.path.join(OUT, "RESULTS-GROUP-ID-REUSE.tsv"),
    ["nct", "canonical_payload", "results_group_id", "n_distinct_titles", "titles"], id_reuse_rows)
tsv(os.path.join(OUT, "ENROLLMENT-CONFLICT.tsv"),
    ["nct", "canonical_payload", "registered_enrollment", "enrollment_type",
     "n_registered_arms", "n_distinct_response_cohorts", "n_response_observations",
     "max_single_cohort_denominator", "max_single_cohort_pointer",
     "largest_within_measure_om_index", "groups_in_that_measure",
     "within_measure_denominator_sum", "pooled_label_in_that_measure",
     "conflict_findings", "summation_policy", "disjointness_status"], enroll_rows)
tsv(os.path.join(OUT, "CHANGE-MAP-vs-job2.tsv"), CHG_HEADER, chg_rows)
tsv(os.path.join(OUT, "LEAF-QB-harmonised-trials.tsv"),
    ["nct", "leaf_group", "mechanism", "reducible_to_non_overlapping_set",
     "registered_enrollment", "enrollment_type", "selected_cohorts_job2",
     "sum_selected_denominators_job2", "excess_job2", "source_file"], qb_rows)
tsv(os.path.join(OUT, "LEAF-QC-harmonised-ties.tsv"),
    ["nct", "group_norm", "leaf_group", "classification", "distinguishing_basis",
     "would_change_selection", "source_file"], qc_rows)

summary = {
    "cache_dir": CACHE,
    "payloads": PAYLOADS,
    "canonical_studies": stats["canonical_studies"],
    "canonical_studies_with_results": stats["canonical_studies_with_results"],
    "ncts_appearing_in_more_than_one_payload": len(dup_ncts),
    "job2_scope_response_measures": scope_probe["job2_scope_measures"],
    "wider_response_pattern_measures_probe_only": scope_probe["wider_match_measures"],
    "ledger_observation_rows": len(obs_rows),
    "ledger_measurement_cell_rows": len(cell_rows),
    "related_set_cohort_keys": len(rel_rows),
    "pooled_parent_relations": len(grp_rows),
    "results_group_id_reuse_rows": len(id_reuse_rows),
    "enrollment_conflict_rows": len(enroll_rows),
    "change_map_rows": len(chg_rows),
    "qb_harmonised_trials": len(qb_rows),
    "qc_harmonised_tie_rows": len(qc_rows),
    "job2_selected_rows_joined_on_cohort_key": sel_join_hit,
    "job2_selected_rows_not_joined": sel_join_miss,
    "job2_selected_rows_with_exact_om_in_ledger": sel_obs_present,
    "job2_selected_rows_without_exact_om_in_ledger": sel_obs_absent,
    "job2_exclusions_reinstated_as_unusable_source_records": exc_reinstated,
    "denominator_state_census": dict(Counter(dict(zip(OBS_HEADER, r))["denominator_state"] for r in obs_rows)),
    "reporting_status_census": dict(Counter(dict(zip(OBS_HEADER, r))["reporting_status_state"] for r in obs_rows)),
    "noncollection_statement_rows": sum(1 for r in obs_rows if dict(zip(OBS_HEADER, r))["noncollection_statement"] is True),
    "denominator_usable_rows": sum(1 for r in obs_rows if dict(zip(OBS_HEADER, r))["denominator_usable"] is True),
    "unresolved_state_census": dict(Counter(s for r in rel_rows for s in r[19].split("|") if s)),
    "participant_flow_module_present_in_cache": False,
}
with open(os.path.join(OUT, "BUILD-SUMMARY.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=1, sort_keys=True)
print(json.dumps(summary, indent=1, sort_keys=True))
