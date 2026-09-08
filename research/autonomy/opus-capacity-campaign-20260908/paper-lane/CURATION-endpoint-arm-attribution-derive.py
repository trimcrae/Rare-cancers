"""JOB 3 - arm-level disease, phase and control attribution.

Reads ONLY the delivered immutable cache copy. Re-derives, for each of the 552 included
group records, four things kept strictly separate:
  (1) whole-trial condition list   (2) trial phase label
  (3) arm/registry description     (4) group-specific evidence in the posted results
No effect estimate is computed anywhere in this file.
"""
import collections, json, os, re, sys

CACHE = "/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5"
BOR = [f"ctg_results_bor_{e}" for e in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
PLA = [f"ctg_placebo_onc_{e}" for e in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
FILES = BOR + PLA

CATEGORY = {
    "CR": re.compile(r"^\s*(complete response|complete remission|CR)\b", re.I),
    "PR": re.compile(r"^\s*(partial response|partial remission|PR)\b", re.I),
    "SD": re.compile(r"^\s*(stable disease|SD)\b", re.I),
    "PD": re.compile(r"^\s*(progressive disease|disease progression|PD)\b", re.I),
}

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()

def payload(name):
    p = os.path.join(CACHE, name + ".txt")
    with open(p, encoding="utf-8") as fh:
        raw = fh.read()
    body = raw.split("=" * 70, 1)[1]
    return json.loads(body)

def cells_for_groups(om):
    per = collections.defaultdict(dict)
    for cl in om.get("classes") or []:
        for cat in cl.get("categories") or []:
            title = cat.get("title") or ""
            label = next((k for k, rx in CATEGORY.items() if rx.match(title)), None)
            if not label:
                continue
            for meas in cat.get("measurements") or []:
                gid, val = meas.get("groupId"), meas.get("value")
                if gid is None or val is None:
                    continue
                try:
                    f = float(val)
                except (TypeError, ValueError):
                    continue
                if f.is_integer():
                    per[gid][label] = int(f)
    return per

# ---- condition normalisation (conservative; every collapse is reported) ------------
STAGE = re.compile(r"\bstages?\s+[0-9ivx]+[ab]?\b")
QUALIFIER = re.compile(
    r"\b(recurrent|refractory|relapsed|relapse|metastatic|advanced|unresectable|locally|"
    r"progressive|previously|treated|untreated|newly|diagnosed|adult|pediatric|childhood|"
    r"high|low|grade|risk|malignant|primary|resected|early|late|extensive|limited)\b")
HEAD = re.compile(r"\b(cancer|cancers|carcinoma|carcinomas|neoplasm|neoplasms|neoplasia|"
                  r"tumor|tumors|tumour|tumours|malignancy|malignancies|disease|diseases)\b")

def cond_key(c):
    """STRICT disease key. Deliberately conservative: it strips stage and status qualifiers and the
    generic head noun, and NOTHING else. It does not strip 'non' (that would collapse NSCLC into
    SCLC) and it does not reorder tokens, so two orderings of the same words stay DISTINCT and the
    record stays MIXED. Under-collapsing is the safe direction here."""
    t = norm(c)
    t = STAGE.sub(" ", t)
    t = QUALIFIER.sub(" ", t)
    t = HEAD.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t or norm(c)

def cond_key_lenient(c):
    """SENSITIVITY key only -- token-sorted, so 'squamous cell carcinoma of head and neck' and
    'head and neck squamous cell carcinoma' collapse. Reported as a sensitivity count; it is never
    the headline attribution."""
    return " ".join(sorted(set(cond_key(c).split())))

# ---- control vocabulary -----------------------------------------------------------
PLACEBO_TXT = re.compile(r"\bplacebo|\bsham\b|\bvehicle control\b", re.I)
NOINT_TXT = re.compile(r"\bno intervention\b|\bobservation only\b|\bbest supportive care\b|\bbsc\b|\bwatchful waiting\b|\buntreated control\b", re.I)
CONTROL_TXT = re.compile(r"\bcontrol\b|\bcomparator\b|\bactive control\b", re.I)
#: The ONLY description phrases allowed to establish control status. "standard of care" on its own is
#: refused: in these records it overwhelmingly describes PRIOR therapy in an eligibility narrative,
#: not this group's assignment (measured on NCT03854227 Parts 2B/2C, both EXPERIMENTAL arms).
CONTROL_DESC = re.compile(r"\bcontrol (arm|group|drug)\b|\brandomi[sz]ed to (the )?(control|placebo)\b", re.I)
#: "Demcizumab/Placebo Arm (Arm 2)" names a TREATMENT SEQUENCE, not a placebo control arm. A title
#: that puts a non-placebo token immediately before "/placebo" is not evidence of control status.
PLACEBO_SEQUENCE = re.compile(r"[A-Za-z0-9]\s*/\s*placebo", re.I)
# producer's own rule, for the divergence count
PRODUCER_CONTROL_TITLE = re.compile(
    r"\b(placebo|best supportive care|BSC|observation|no (treatment|intervention)|"
    r"supportive care alone|watchful waiting)\b", re.I)
CONTROL_TYPES = {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION", "ACTIVE_COMPARATOR"}

#: Condition strings that pass the "one condition" test but name NO tumour type. A group under one
#: of these has a trial-level condition list that is specific-looking and diagnostically empty.
UMBRELLA_KEYS = {"solid", "solid tumors", "malignant solid tumor", "advanced malignancies",
                 "cancer", "neoplasms", "advanced", "metastatic"}
#: One level above a tumour type: an organ system, a lineage or a biomarker. Real, but it cannot
#: carry a disease-specific subgroup on its own.
BROAD_KEYS = {"central nervous system", "leukemia", "lung", "lymphoma",
              "isocitrate dehydrogenase gene mutation", "sarcoma", "carcinoma"}

PHASE_TXT = re.compile(r"\bphase\s*(i{1,3}|1|2|3|4)\b|\bdose escalation\b|\bdose expansion\b|\bexpansion (cohort|phase|part)\b|\bpart\s+[ab12]\b", re.I)

def arm_match(gtitle, armgroups):
    """Resolve an outcome-measure group title to a registered arm group.
    Returns (quality, armgroup|None). Quality is EXACT / NORMALIZED / CONTAINMENT /
    AMBIGUOUS_MULTI / NONE.  CONTAINMENT is explicitly recorded as weak."""
    if not armgroups:
        return "NONE", None
    for g in armgroups:
        if (g.get("label") or "") == gtitle:
            return "EXACT", g
    gt = norm(gtitle)
    if not gt:
        return "NONE", None
    nm = [(norm(g.get("label")), g) for g in armgroups]
    hits = [g for k, g in nm if k and k == gt]
    if len(hits) == 1:
        return "NORMALIZED", hits[0]
    if len(hits) > 1:
        return "AMBIGUOUS_MULTI", None
    cont = [g for k, g in nm if k and (k in gt or gt in k)]
    if len(cont) == 1:
        return "CONTAINMENT", cont[0]
    if len(cont) > 1:
        return "AMBIGUOUS_MULTI", None
    return "NONE", None

def main():
    rows = []
    seen = set()
    for name in FILES:
        era = name.rsplit("_", 2)[-2] + "_" + name.rsplit("_", 1)[-1]
        family = "bor" if name in BOR else "placebo"
        doc = payload(name)
        for s in doc.get("studies") or []:
            ps = s.get("protocolSection") or {}
            rs = s.get("resultsSection") or {}
            nct = (ps.get("identificationModule") or {}).get("nctId")
            conds = (ps.get("conditionsModule") or {}).get("conditions") or []
            dm = ps.get("designModule") or {}
            phases = dm.get("phases") or []
            ai = (ps.get("armsInterventionsModule") or {}).get("armGroups") or []
            n_arms_registered = len(ai)
            registry_has_control = any((g.get("type") or "") in CONTROL_TYPES for g in ai)
            registry_has_placebo = any((g.get("type") or "") in {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION"} for g in ai)
            for om in (rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []:
                gmeta = {g.get("id"): g for g in om.get("groups") or []}
                for gid, cells in cells_for_groups(om).items():
                    if len(cells) < 4:
                        continue
                    n = sum(cells.values())
                    if n <= 0:
                        continue
                    g = gmeta.get(gid) or {}
                    gtitle = g.get("title") or ""
                    key = (nct, om.get("title"), gtitle, n)
                    if key in seen:
                        continue
                    seen.add(key)
                    gdesc = g.get("description") or ""
                    omtitle = om.get("title") or ""
                    omdesc = (om.get("description") or "") + " " + (om.get("populationDescription") or "")
                    q, ag = arm_match(gtitle, ai)
                    ag_label = (ag or {}).get("label") or ""
                    ag_type = (ag or {}).get("type") or ("" if ag is None else "NOT_STATED_IN_REGISTRY")
                    ag_desc = (ag or {}).get("description") or ""

                    # ---------- (A) DISEASE ----------
                    raw_conds = list(conds)
                    keys, lkeys = [], []
                    for c in raw_conds:
                        k = cond_key(c)
                        if k not in keys:
                            keys.append(k)
                        lk = cond_key_lenient(c)
                        if lk not in lkeys:
                            lkeys.append(lk)
                    group_text = " || ".join([gtitle, gdesc, ag_label, ag_desc, omtitle, omdesc])
                    gnorm = norm(group_text)
                    named = [c for c in raw_conds if cond_key(c) and cond_key(c) in gnorm]
                    named_keys = []
                    for c in named:
                        k = cond_key(c)
                        if k not in named_keys:
                            named_keys.append(k)
                    if not raw_conds:
                        disease_status, disease_value, disease_basis = "UNKNOWN", "", "no condition list in record"
                    elif len(named_keys) == 1 and len(keys) > 1:
                        disease_status, disease_value = "GROUP_SPECIFIC", named[0]
                        disease_basis = "group/arm/outcome text names exactly one of the trial conditions"
                    elif len(keys) == 1 and len(raw_conds) == 1:
                        disease_status, disease_value = "TRIAL_SINGLE", raw_conds[0]
                        disease_basis = "trial lists exactly one condition"
                    elif len(keys) == 1:
                        disease_status, disease_value = "TRIAL_SINGLE_AFTER_COLLAPSE", raw_conds[0]
                        disease_basis = "trial conditions collapse to one disease key: " + " ; ".join(raw_conds)
                    else:
                        disease_status, disease_value = "MIXED", ""
                        disease_basis = f"{len(keys)} distinct disease keys at trial level, no single-disease group evidence"

                    attributed_key = (cond_key(disease_value) if disease_value else "")

                    # ---------- (B) PHASE ----------
                    ptxt = PHASE_TXT.search(group_text)
                    if not phases:
                        phase_status, phase_value = "UNKNOWN", ""
                    elif phases == ["NA"]:
                        phase_status, phase_value = "NOT_APPLICABLE", "NA"
                    elif len(phases) == 1:
                        phase_status, phase_value = "TRIAL_SINGLE", phases[0]
                    else:
                        phase_status, phase_value = "MIXED", "/".join(phases)
                    phase_group_hint = ptxt.group(0) if ptxt else ""

                    # ---------- (C) CONTROL ----------
                    strong = q in ("EXACT", "NORMALIZED")
                    seq = bool(PLACEBO_SEQUENCE.search(gtitle))
                    ctl_txt_p = bool(PLACEBO_TXT.search(gtitle)) and not seq
                    ctl_txt_n = bool(NOINT_TXT.search(gtitle))
                    ctl_txt_c = bool(CONTROL_TXT.search(gtitle) or CONTROL_DESC.search(gdesc))
                    if strong and ag_type in {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR"}:
                        ctl, ctl_basis = "CONTROL_PLACEBO", f"registry arm '{ag_label}' type={ag_type} ({q} match)"
                    elif strong and ag_type == "NO_INTERVENTION":
                        ctl, ctl_basis = "CONTROL_NO_INTERVENTION", f"registry arm '{ag_label}' type={ag_type} ({q} match)"
                    elif strong and ag_type == "ACTIVE_COMPARATOR":
                        ctl, ctl_basis = "CONTROL_ACTIVE_COMPARATOR", f"registry arm '{ag_label}' type={ag_type} ({q} match)"
                    elif strong and ag_type in ("EXPERIMENTAL", "OTHER"):
                        ctl, ctl_basis = "NOT_CONTROL", f"registry arm '{ag_label}' type={ag_type} ({q} match)"
                    elif ctl_txt_p:
                        ctl, ctl_basis = "CONTROL_PLACEBO_BY_GROUP_TEXT", "results group title/description states placebo or sham; registry arm not strongly matched"
                    elif ctl_txt_n:
                        ctl, ctl_basis = "CONTROL_NO_INTERVENTION_BY_GROUP_TEXT", "results group title/description states no-intervention/BSC; registry arm not strongly matched"
                    elif ctl_txt_c:
                        ctl, ctl_basis = "CONTROL_UNSPECIFIED_BY_GROUP_TEXT", "results group text says control/comparator/standard of care without naming placebo"
                    elif strong and ag_type == "NOT_STATED_IN_REGISTRY":
                        ctl, ctl_basis = "UNKNOWN", f"registry arm '{ag_label}' carries no type field ({q} match)"
                    elif seq:
                        ctl, ctl_basis = "UNKNOWN_AMBIGUOUS_SEQUENCE_LABEL", (
                            "group title names a treatment sequence ending in placebo; it is not "
                            "evidence that this group is the placebo control arm")
                    elif q == "CONTAINMENT":
                        ctl, ctl_basis = "UNKNOWN_WEAK_MATCH_ONLY", f"only a substring match to registry arm '{ag_label}' (type={ag_type}); not group-supported"
                    elif n_arms_registered <= 1:
                        ctl, ctl_basis = "NOT_CONTROL_SINGLE_ARM_TRIAL", f"trial registers {n_arms_registered} arm group(s)"
                    else:
                        ctl, ctl_basis = "UNKNOWN", f"no strong arm match ({q}) and no control language in the group record"
                    # a placebo claim with no placebo arm anywhere in the registry is a contradiction
                    ctl_flag = ""
                    if ctl.startswith("CONTROL_PLACEBO") and not registry_has_placebo:
                        ctl_flag = "PLACEBO_CLAIM_WITHOUT_PLACEBO_ARM_IN_REGISTRY"
                    producer_ctl = bool(PRODUCER_CONTROL_TITLE.search(gtitle))

                    rows.append(dict(
                        era=era, family=family, nct=nct, om_title=omtitle, group_title=gtitle,
                        evaluable_n=n,
                        trial_conditions=" ; ".join(raw_conds),
                        n_trial_conditions=len(raw_conds), n_disease_keys=len(keys),
                        n_disease_keys_lenient=len(lkeys), disease_key=keys[0] if len(keys)==1 else '',
                        attributed_key=attributed_key,
                        disease_specificity=(
                            "UNASSIGNABLE" if disease_status in ("MIXED", "UNKNOWN")
                            else "NOT_A_DISEASE_UMBRELLA" if attributed_key in UMBRELLA_KEYS
                            else "BROAD_CATEGORY_ONLY" if attributed_key in BROAD_KEYS
                            else "NAMES_A_TUMOUR_TYPE"),
                        disease_status=disease_status, disease_value=disease_value,
                        disease_basis=disease_basis,
                        trial_phases="/".join(phases) if phases else "",
                        phase_status=phase_status, phase_value=phase_value,
                        phase_group_hint=phase_group_hint,
                        registry_arm_label=ag_label, registry_arm_type=ag_type,
                        arm_match_quality=q, n_arms_registered=n_arms_registered,
                        registry_has_control_arm=registry_has_control,
                        control_status=ctl, control_basis=ctl_basis, control_flag=ctl_flag,
                        producer_control_arm_candidate=producer_ctl,
                        group_description=gdesc.replace("\n", " ")[:400],
                        registry_arm_description=ag_desc.replace("\n", " ")[:400],
                    ))
    return rows

if __name__ == "__main__":
    rows = main()
    out = sys.argv[1]
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1)
    print("records:", len(rows))
