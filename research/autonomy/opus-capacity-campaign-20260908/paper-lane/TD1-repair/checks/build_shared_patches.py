#!/usr/bin/env python3
"""TD1 F10 — build bounded ANNOTATION-ONLY patches for parent-owned shared files.

JSON files are edited STRUCTURALLY: the file is parsed, the named string field is replaced by
path, and the object is re-serialised with the settings that reproduce the original file
byte-for-byte (verified per file before any edit). That makes it provable that nothing but the
named annotation strings changed. Generator sources are edited by replacing the exact wrapped
literal block that produces the corresponding annotation, so the generating text AGREES with the
corrected displayed value.

⛔ No producer is executed, no artifact regenerated, no numeric value, cohort member, membership
list, measured state or original source byte altered. The working tree is left UNCHANGED; only
patches and patched copies are written under <repair>/patches/.
"""
import ast
import datetime
import difflib
import hashlib
import json
import os
import sys

REPAIR = "research/autonomy/opus-capacity-campaign-20260908/paper-lane/TD1-repair"
OUT = os.path.join(REPAIR, "patches")
DATE = "2026-09-08"
CORR = f"⚠ Corrected {DATE} (TD1 final review, root adjudication)"

# ----------------------------------------------------------------- new annotation text
G_OBSERVED = ("The CDK7 initiation module and the general transcriptional-output group both read "
              "HIGHER in EMC on both platform records, at nominal uncorrected significance. The CDK9 "
              "elongation module is higher on both but weakly. MYC is up on both. "
              f"{CORR} F7: \"both with the largest t-statistics in this pass\" is withdrawn — no "
              "reproducible, scientifically meaningful census-wide ranking criterion was defined for "
              "it. ⚠ F2: the GPL3290 record is under an interpretation hold, its deposited reference "
              "labels differing by group (CRH-mRNA for the EMC arm, CRH for DFSP, UHR for GIST) with "
              "comparability across them not established.")

G_VERDICT = ("SUPPORTED ON ABUNDANCE, EXPLORATORY — elevated on both platform records, uncorrected "
             f"for multiple testing. {CORR} F7: the superlative \"the most concordant elevation in "
             "the census\" is withdrawn as an undefined rank; F2: the GPL3290 record is under an "
             "interpretation hold.")

G_CLOSED = (f"{CORR} F1/F3: THE DEPENDENCY SCREEN DID NOT CLOSE THIS WINDOW, and the earlier text "
            "under this field name is superseded (the key itself is retained unchanged for consumer "
            "stability). What is measured: across the 91 screened sarcoma-lineage lines (of 176 "
            "catalogued Soft Tissue/Bone models) in DepMap 24Q4, CDK7 and CDK9 have Chronos gene "
            "effects below the -0.5 dependency threshold in 100% of them, with mean gene effects of "
            "-1.85 and -1.46 and cancer-line mean differences (non-sarcoma minus sarcoma) of +0.085 "
            "and +0.017 reported without a precision estimate. ⛔ That is a broad binary dependency in "
            "NON-EMC cancer lines. It does not establish equal continuous effects, absence of subgroup "
            "heterogeneity, absence of a graded response to partial inhibition, absence of a "
            "selectable phenotype, or a tumour-versus-normal window — a cancer-versus-cancer "
            "comparison cannot supply one. No line here contributes a CRISPR observation for EMC, so "
            "nothing in it decides an EMC-specific dependency, and the expression and dependency "
            "readings are UNPAIRED: no relationship between them is estimated.")

G_ACTION = ("hold: elevated on abundance in archival EMC-labelled specimens; broad non-selective "
            "dependency in non-EMC cancer lines; unpaired, and unmeasured in EMC. "
            f"{CORR} F1/F3: \"closed on the axis that matters\" is withdrawn.")

G_CHAP_OBSERVED = ("The HSP90 machine reads HIGHER in EMC on both platform records and the "
                   "co-chaperones follow it in direction, the co-chaperone contrasts not reaching "
                   "nominal significance. ⚠ The HSP70-arm-and-heat-shock group gives negative point "
                   "estimates on both, NEITHER distinguishable from zero and both with approximate "
                   f"intervals that include positive differences. {CORR} F4: \"go the OTHER way on "
                   "both, which is not what a general stress response looks like\" is withdrawn. This "
                   "is no clear evidence of a positive contrast for this curated list — not absence "
                   "of elevation, not an equivalence result, and not contradictory biology.")

G_CHAP_VERDICT = ("PARTLY SUPPORTED, EXPLORATORY — the HSP90 arm only; the stress-response arm gives "
                  f"no clear evidence in either direction. {CORR} F4: \"the stress-response arm "
                  "contradicts it\" is withdrawn.")

E_QUESTION = ("Is the transcriptional CDK machinery elevated in EMC — the dependency a fusion "
              "oncoprotein whose described mechanism is transactivation might be expected to impose? "
              f"{CORR} F8: the earlier clause \"and the class the census found no prior search had "
              "ever named\" is withdrawn, because this programme's dated searches bound what was "
              "inspected, not what exists.")

E_CANNOT = ("⛔ DEPENDENCY IS NOT ABUNDANCE, AND HERE THE GAP IS UNUSUALLY WIDE. Every cell "
            "transcribes, so these genes are expressed everywhere, and a tumour can be exquisitely "
            "dependent on a module it expresses at ordinary levels. A flat read therefore does NOT "
            f"exclude the class. {CORR} F1/F3: \"only a dependency screen would\" is withdrawn — a "
            "dependency screen in NON-EMC lines does not exclude the class for EMC either. The two "
            "readings are unpaired, and only a perturbation observation in a fusion-positive EMC "
            "model bears on an EMC-specific dependency. This read can raise the hypothesis and cannot "
            "lower it much.")

C_ANSWER = ("NOT IDENTIFIED IN THE ITEMS INSPECTED BY THIS DATED SEARCH — with a real positive "
            "underneath it that must not be inflated into a yes, and a bound that must not be "
            f"inflated into a proof of absence. {CORR} F8.")

C_ONE = ("We did not identify a qualifying direct BINDING result for any FET-family fusion protein "
         "among the items inspected in this dated PubMed search. What those items contain is three "
         "independent demonstrations that EWS::FLI1 protein levels FALL when the HSP90 machine is "
         "perturbed — one of them a genetic knockdown of the HSP90 co-chaperone SGT1/SUGT1 rather "
         "than a drug — which is chaperone-machine DEPENDENCE and not client status; for "
         "EWSR1::NR4A3, this programme's own fusion, no chaperone record was retrieved by these "
         "queries. ⚠ 25 hits of Q15 were not individually screened, the Q13 client-screen supplement "
         "was not retrieved, several records were abstract-only or full-text inaccessible, and "
         "preprint and non-PubMed sources were not searched — so this is a bounded search finding, "
         "not a statement about the whole literature and not evidence that the experiment has never "
         f"been attempted. {CORR} F8.")

C_B = ("NOT ESTABLISHED BY THE ITEMS INSPECTED. Three papers show EWS::FLI1 protein DEPLETION on "
       "HSP90-machine perturbation (PMID 24388362, PMID 36495678, PMID 25985210). No "
       "co-immunoprecipitation, pull-down, chemical-affinity capture or client-screen appearance for "
       "any FET fusion was found among the records inspected in this dated search; that is not a "
       "demonstration that none exists, and unscreened hits, unretrieved supplements and inaccessible "
       f"full texts remain. {CORR} F8. ⚠ And the co-chaperone result is weaker than it first reads: "
       "the systematic human client screen assigns SGT1 a preference for leucine-rich-repeat folds "
       "(PMID 25036637), which neither EWSR1 nor FLI1 has — a preference, which does not exclude "
       "other interactions.")

C_C = ("NOT FOUND BY THESE QUERIES. FLI1, DDIT3 and NR4A3 each return no record of HSP90 clientship "
       "in a title/abstract co-occurrence search (queries Q5 and Q6 below). No chaperone record for "
       "the 3' partner NR4A3 was retrieved by these queries; a title/abstract co-occurrence search "
       f"cannot establish that none exists. {CORR} F8.")

C_WHY = ("The assay exists and has been run on other fusion oncoproteins. AML1-ETO was shown to bind "
         "the chaperonin TRiC/CCT directly, by immunoprecipitation, mass spectrometry and cryo-EM, "
         "with HSP70 assistance and through its DNA-BINDING DOMAIN (PMID 26706127, PMID 27276256). So "
         "the fact that this search did not locate such a demonstration for a FET fusion is not "
         "explained by the instrument being unavailable. ⚠ It remains a gap in what this search "
         "retrieved, which is not the same as a gap in the literature: a negative or unpublished "
         f"experiment would not appear here either. {CORR} F8.")

C_Q15 = ("A substantial WILD-TYPE FUS aggregation literature — category (a), and about condensates "
         "rather than HSP90 clientship, on the evidence of the result titles. ⚠ Not individually "
         "screened. ⛔ The earlier claim that these hits \"cannot contain a fusion-clientship result "
         f"that Q1, Q2, Q7, Q8 and Q12 all missed\" is withdrawn. {CORR} F8: 25 unscreened hits are "
         "an open gap in this search, not evidence about their contents.")

C_Q3 = ("THE MOST DIRECT NULL RETRIEVED FOR THIS PROGRAMME. The single hit is PMID 28383167 — HSPA8 "
        "as a fusion PARTNER. This query retrieved no chaperone-dependence, chaperone-binding or "
        "HSP90-inhibitor study of EWSR1::NR4A3 or TAF15::NR4A3. ⚠ That is the result of one query "
        "string on one date, not a demonstration that PubMed contains no such record. "
        f"{CORR} F8.")

C_RTCHAP = ("The route's own required_validation item — 'A literature assessment of chaperone "
            "clientship across FET-family fusion proteins' — has been carried out to the bounded "
            "scope recorded here, and it returned no qualifying binding result among the items "
            "inspected. The route's remaining_unknown 'whether the chimera is a chaperone CLIENT' "
            f"stays open. {CORR} F8: 'it comes back NEGATIVE ON THE PREMISE' and 'the literature now "
            "says it is open for EVERY FET fusion' are withdrawn — this search does not speak for the "
            "literature, and unscreened hits, unretrieved supplements, inaccessible full texts and "
            "unsearched non-PubMed sources all remain. That is a weaker position than the 2026-08-09 "
            "record implied and a better-evidenced one.")

C_DEF = (f"{CORR} F5, so that this definition and this record's verdict use one consistent category "
         "scheme. CLIENTSHIP, as used in the verdict, requires a BINDING observation naming the "
         "chaperone, the protein and the assay: co-immunoprecipitation or pull-down with a chaperone, "
         "or appearance in a chaperone client screen or affinity-capture proteomic. Loss of the "
         "protein on chaperone inhibition or co-chaperone depletion is DEPENDENCE evidence and is NOT "
         "counted as clientship here, because a transcription factor can fall for reasons that never "
         "touch the chaperone — including loss of its own autoregulated transcription. ⚠ Binding, "
         "stability/folding dependence, fusion-specific dependence and selective vulnerability are "
         "four different claims; no single assay settles all of them, and evidence for one is not "
         "evidence for another.")

PUB_CLAIM = ("Two UNPAIRED descriptive evidence streams for an NR4A3-fusion sarcoma: relative "
             "transcript scores for seven repository-curated gene lists in 16 archival EMC-labelled "
             "specimen records, and single-gene CRISPR knockout effects for five of the same genes in "
             "non-EMC cancer lines (DepMap 24Q4). The paper reports each stream at its own scope, "
             "estimates NO relationship between them, and decides no EMC-specific dependency. "
             f"{CORR} F1: the earlier central claim that abundance and dependency disagree in "
             "opposite directions is PARKED — these unpaired data do not measure such a relationship "
             "— together with the census superlative, the 'closes completely on dependency' and 'no "
             "selectivity' readings, and the 'internally contradictory' chaperone reading.")

PUB_WHY = ("Two unpaired evidence streams, both unresolved for this disease and resolvable only by a "
           "perturbation observation in a fusion-positive EMC model. "
           f"{CORR} F1: the 'disagree in opposite directions' framing is withdrawn.")

# ----------------------------------------------------------------- JSON edit plan
# (path tuple into the parsed object, new value, finding, human label)
JSON_EDITS = {
    "research/modalities/census-route-expression-grading.json": [
        (("routes", "RT-TXN-CDK", "observed"), G_OBSERVED, "F7/F2"),
        (("routes", "RT-TXN-CDK", "verdict"), G_VERDICT, "F7/F2"),
        (("routes", "RT-TXN-CDK", "the_dependency_screen_ran_and_it_closed_the_window"),
         G_CLOSED, "F1/F3"),
        (("routes", "RT-TXN-CDK", "route_action"), G_ACTION, "F1/F3"),
        (("routes", "RT-CHAPERONE", "observed"), G_CHAP_OBSERVED, "F4"),
        (("routes", "RT-CHAPERONE", "verdict"), G_CHAP_VERDICT, "F4"),
    ],
    "research/literature/fet-fusion-chaperone-clientship-2026-08-27.json": [
        (("verdict", "answer"), C_ANSWER, "F8"),
        (("verdict", "one_sentence"), C_ONE, "F8"),
        (("verdict", "by_category", "b_the_FUSION_as_client"), C_B, "F8"),
        (("verdict", "by_category", "c_the_PARTNER_as_client"), C_C, "F8"),
        (("verdict", "why_this_is_not_a_null_result_about_the_assay"), C_WHY, "F8"),
        (("definitions", "documented_chaperone_client"), C_DEF, "F5"),
        (("what_this_changes", "for_RT_CHAPERONE"), C_RTCHAP, "F8"),
    ],
    "systems/graph/publications.json": [],  # filled in below (list index resolved at run time)
    # E carries the same two annotation strings in three/two places; all copies move together.
    "research/modalities/emc-expression-panels.json": [
        (("panels", "transcriptional_cdk", "question"), E_QUESTION, "F8"),
        (("panels", "transcriptional_cdk", "what_it_cannot_settle"), E_CANNOT, "F1/F3"),
        (("reads", "read_13_TXN_CDK", "question"), E_QUESTION, "F8"),
        (("reads", "read_13_TXN_CDK", "what_it_cannot_settle"), E_CANNOT, "F1/F3"),
        (("reads", "read_13_TXN_CDK", "panels", "transcriptional_cdk", "question"),
         E_QUESTION, "F8"),
    ],
}

# C's Q3/Q15 live in a list; resolved by id below.
C_QUERY_EDITS = {"Q3": C_Q3, "Q15": C_Q15}


def dig(obj, path):
    for k in path:
        obj = obj[k]
    return obj


def setpath(obj, path, value):
    for k in path[:-1]:
        obj = obj[k]
    old = obj[path[-1]]
    obj[path[-1]] = value
    return old


def roundtrip_settings(raw, obj):
    for kw in (dict(indent=2, ensure_ascii=False), dict(indent=2, ensure_ascii=True),
               dict(indent=1, ensure_ascii=False), dict(indent=1, ensure_ascii=True)):
        out = json.dumps(obj, **kw)
        if out == raw or out + "\n" == raw:
            return kw, (out + "\n" == raw)
    return None, None


os.makedirs(OUT, exist_ok=True)
ledger = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "date": DATE,
          "rule": ("annotation/prose only. JSON edits are structural, by field path, re-serialised "
                   "with settings verified to reproduce the original file byte-for-byte before the "
                   "edit; generator-source edits replace the exact literal block producing the same "
                   "annotation. No numeric value, cohort member, membership list, measured state or "
                   "original source byte is changed."),
          "files": {}}
problems = []


def emit(path, original, text, recs):
    ledger["files"][path] = {
        "original_bytes": len(original.encode()), "patched_bytes": len(text.encode()),
        "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
        "patched_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "edits": recs}
    if text == original:
        problems.append(f"{path}: no change produced")
        return
    diff = list(difflib.unified_diff(original.splitlines(keepends=True), text.splitlines(keepends=True),
                                     fromfile="a/" + path, tofile="b/" + path, n=3))
    name = path.replace("/", "__")
    with open(os.path.join(OUT, name + ".patch"), "w", encoding="utf-8") as fh:
        fh.writelines(diff)
    ledger["files"][path]["patch"] = name + ".patch"


for path, edits in JSON_EDITS.items():
    raw = open(path, encoding="utf-8").read()
    obj = json.loads(raw)
    kw, trailing_nl = roundtrip_settings(raw, obj)
    if kw is None:
        problems.append(f"{path}: no serialisation reproduces the original bytes; refusing to patch")
        continue
    recs = []
    for pth, new, finding in edits:
        old = setpath(obj, pth, new)
        recs.append({"field": ".".join(str(x) for x in pth), "finding": finding,
                     "old_len": len(old), "new_len": len(new),
                     "old_sha256_16": hashlib.sha256(old.encode()).hexdigest()[:16],
                     "new_sha256_16": hashlib.sha256(new.encode()).hexdigest()[:16]})
    if path.endswith("fet-fusion-chaperone-clientship-2026-08-27.json"):
        for i, q in enumerate(obj["searches_that_returned_nothing_relevant"]["queries"]):
            if q["id"] in C_QUERY_EDITS:
                old = q["outcome"]
                q["outcome"] = C_QUERY_EDITS[q["id"]]
                recs.append({"field": f"searches_that_returned_nothing_relevant.queries[{i}]"
                                      f"({q['id']}).outcome", "finding": "F8",
                             "old_len": len(old), "new_len": len(q["outcome"]),
                             "old_sha256_16": hashlib.sha256(old.encode()).hexdigest()[:16],
                             "new_sha256_16": hashlib.sha256(q["outcome"].encode()).hexdigest()[:16]})
    if path.endswith("systems/graph/publications.json"):
        hit = None
        for i, ent in enumerate(obj):
            if isinstance(ent, dict) and ent.get("id") == "PUB-TXN-DEPENDENCY":
                hit = i
        if hit is None:
            problems.append(f"{path}: PUB-TXN-DEPENDENCY not found")
            continue
        for key, new in (("what_it_would_claim", PUB_CLAIM), ("outcome_potential_why", PUB_WHY)):
            old = obj[hit][key]
            obj[hit][key] = new
            recs.append({"field": f"[{hit}](PUB-TXN-DEPENDENCY).{key}", "finding": "F1",
                         "old_len": len(old), "new_len": len(new),
                         "old_sha256_16": hashlib.sha256(old.encode()).hexdigest()[:16],
                         "new_sha256_16": hashlib.sha256(new.encode()).hexdigest()[:16]})
    text = json.dumps(obj, **kw) + ("\n" if trailing_nl else "")
    ledger.setdefault("serialisation", {})[path] = {**{k: str(v) for k, v in kw.items()},
                                                    "trailing_newline": bool(trailing_nl)}
    emit(path, raw, text, recs)

# ----------------------------------------------------------------- generator sources
def py_literal(indent, key, value, width=100):
    """Render `"key": ("..." "...")` as adjacent literals whose concatenation IS `value`."""
    segs, cur = [], ""
    for w in value.split(" "):
        if cur and len(cur) + len(w) + 1 > width - len(indent) - 8:
            segs.append(cur + " ")
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    segs.append(cur)
    lines = ['"' + seg.replace("\\", "\\\\").replace('"', '\\"') + '"' for seg in segs]
    assert "".join(seg for seg in segs) == value, "py_literal changed the value"
    pad = " " * (len(indent) + len(key) + 5)
    body = f'{indent}"{key}": ({lines[0]}\n'
    body += "".join(f"{pad}{l}\n" for l in lines[1:])
    return body.rstrip("\n") + "),\n"


def block_bounds(src, start_marker, end_marker, label):
    i = src.find(start_marker)
    if i < 0:
        problems.append(f"{label}: start marker not found")
        return None
    j = src.find(end_marker, i + len(start_marker))
    if j < 0:
        problems.append(f"{label}: end marker not found")
        return None
    if src.find(start_marker, i + 1) != -1 and label.endswith("!unique"):
        problems.append(f"{label}: start marker is not unique")
        return None
    return i, j


def replace_entry(src, lo, hi, key, new_value, label, indent="        "):
    """Replace exactly one `"key": <literal>,` entry inside src[lo:hi]."""
    anchor = f'\n{indent}"{key}": '
    i = src.find(anchor, lo, hi)
    if i < 0:
        problems.append(f"{label}: entry {key!r} not found in block")
        return src, hi, False
    # the entry ends at the next sibling key at the same indent, or -- if this is the last
    # entry -- at the first following line that is dedented out of the entry list.
    j = src.find(f'\n{indent}"', i + 1)
    if j < 0 or j > hi:
        j, k = hi, i + 1
        while True:
            nl = src.find("\n", k)
            if nl < 0 or nl >= hi:
                break
            line = src[nl + 1:src.find("\n", nl + 1)]
            if line.strip() and (len(line) - len(line.lstrip(" "))) < len(indent):
                j = nl
                break
            k = nl + 1
    rendered = "\n" + py_literal(indent, key, new_value).rstrip("\n")
    out = src[:i] + rendered + src[j:]
    return out, hi + (len(rendered) - (j - i)), True


GP = "research/modalities/census_route_expression_grading.py"
gp_raw = open(GP, encoding="utf-8").read()
gp = gp_raw
recs = []
G_FIELDS = [("RT-TXN-CDK", "observed", G_OBSERVED, "F7/F2"),
            ("RT-TXN-CDK", "verdict", G_VERDICT, "F7/F2"),
            ("RT-TXN-CDK", "the_dependency_screen_ran_and_it_closed_the_window", G_CLOSED, "F1/F3"),
            ("RT-TXN-CDK", "route_action", G_ACTION, "F1/F3"),
            ("RT-CHAPERONE", "observed", G_CHAP_OBSERVED, "F4"),
            ("RT-CHAPERONE", "verdict", G_CHAP_VERDICT, "F4")]
ROUTE_END = {"RT-TXN-CDK": '\n    routes["RT-CHAPERONE"]',
             "RT-CHAPERONE": '\n    routes["RT-APOPTOSIS-DEP"]'}
for route, key, new, finding in G_FIELDS:
    b = block_bounds(gp, f'routes["{route}"] = {{', ROUTE_END[route], f"GP {route}!unique")
    if b is None:
        recs.append({"field": f"{route}.{key}", "finding": finding, "status": "FAILED (block)"})
        continue
    lo, hi = b
    gp, hi, good = replace_entry(gp, lo, hi, key, new, f"GP {route}.{key}")
    recs.append({"field": f"routes[{route}].{key}", "finding": finding,
                 "status": "replaced" if good else "FAILED"})
emit(GP, gp_raw, gp, recs)

EP = "research/modalities/emc_expression_panels.py"
ep_raw = open(EP, encoding="utf-8").read()
ep = ep_raw
recs = []
b = block_bounds(ep, '    "transcriptional_cdk": {', '\n    "chaperone_dependency": {',
                 "EP transcriptional_cdk!unique")
if b is None:
    recs.append({"field": "PANELS.transcriptional_cdk", "finding": "F8/F1/F3", "status": "FAILED (block)"})
else:
    lo, hi = b
    for key, new, finding in (("question", E_QUESTION, "F8"),
                              ("what_it_cannot_settle", E_CANNOT, "F1/F3")):
        ep, hi, good = replace_entry(ep, lo, hi, key, new, f"EP transcriptional_cdk.{key}")
        recs.append({"field": f"PANELS.transcriptional_cdk.{key}", "finding": finding,
                     "status": "replaced" if good else "FAILED"})
emit(EP, ep_raw, ep, recs)

# ---- generator-source equivalence guard: only the named string constants may differ ----
def const_multiset(src):
    tree = ast.parse(src)
    strs, others = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            (strs if isinstance(node.value, str) else others).append(node.value)
    return strs, others


for src_path, expected_new in ((GP, [G_OBSERVED, G_VERDICT, G_CLOSED, G_ACTION,
                                     G_CHAP_OBSERVED, G_CHAP_VERDICT]),
                               (EP, [E_QUESTION, E_CANNOT])):
    a = open(src_path, encoding="utf-8").read()
    bsrc = gp if src_path == GP else ep
    try:
        sa, oa = const_multiset(a)
        sb, ob = const_multiset(bsrc)
    except SyntaxError as exc:
        problems.append(f"{src_path}: patched source does not parse: {exc}")
        continue
    if sorted(map(repr, oa)) != sorted(map(repr, ob)):
        problems.append(f"{src_path}: a NON-STRING constant changed")
    added = sorted(set(sb) - set(sa))
    removed = sorted(set(sa) - set(sb))
    if sorted(added) != sorted(set(expected_new)):
        problems.append(f"{src_path}: unexpected added string constants: "
                        f"{[x[:60] for x in set(added) - set(expected_new)]}")
    if len(removed) != len(expected_new):
        problems.append(f"{src_path}: {len(removed)} string constants removed, expected "
                        f"{len(expected_new)}: {[x[:60] for x in removed]}")
    ledger["files"][src_path]["constant_delta"] = {
        "n_string_constants_added": len(added), "n_string_constants_removed": len(removed),
        "non_string_constants_unchanged": sorted(map(repr, oa)) == sorted(map(repr, ob)),
        "removed_preview": [x[:90] for x in removed]}

ledger["problems"] = problems
json.dump(ledger, open(os.path.join(OUT, "EDIT-LEDGER.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(json.dumps({"patched": sorted(ledger["files"]), "problems": problems}, indent=1))
sys.exit(1 if problems else 0)
