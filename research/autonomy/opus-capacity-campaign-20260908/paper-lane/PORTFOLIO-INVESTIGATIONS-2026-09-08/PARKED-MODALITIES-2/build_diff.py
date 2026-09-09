import json,io,os,hashlib,collections
REPO="/home/user/Rare-cancers"
SRC=os.path.join(REPO,"systems/graph/routes.json")
raw=open(SRC,encoding="utf-8").read()
print("input sha256:",hashlib.sha256(raw.encode()).hexdigest())
d=json.loads(raw)
rs=d["routes"] if isinstance(d,dict) and "routes" in d else d
n_before=len(rs)
r=[x for x in rs if x.get("id")=="RT-RIBOZYME"][0]

CIT=('PubMed, retrieved 2026-09-09 via the PubMed MCP route: PMID 30393375, '
     'doi 10.1038/s41417-018-0055-9, "Phase I trial of intravenous Ad5CRT in patients with liver '
     'metastasis of gastrointestinal cancers.", Cancer Gene Ther 2018;26(5-6):174-178, '
     'article types "Clinical Trial, Phase I"/"Journal Article" — a trans-splicing ribozyme '
     'targeting hTERT RNAs, delivered by adenovirus, in a solid-tumour indication')

def corr(new, old, extra=""):
    return (new + "  ⚠ CORRECTED 2026-09-09 (PARKED-MODALITIES-2, dated closed PubMed retrieval; "
            "SUPERSEDED, RETAINED VERBATIM: \"" + old + "\"). "
            "THE ROUTE REMAINS PARKED on BLK-VECTOR-DELIVERY (gate 1), which is untouched by this "
            "correction. No efficacy, safety, selectivity, therapeutic-window or clinical-readiness "
            "claim is made or implied." + (" " + extra if extra else ""))

edits=[]

old=r["remaining_unknowns"][1]
new=("Modern solid-tumour footing: ONE published solid-tumour clinical record was retrieved — "
     + CIT + ". That trial reported the treatment as feasible and well tolerated and reported no "
     "meaningful clinical benefit; this repository asserts nothing beyond quoting it. Under the "
     "closed query \"trans-splicing ribozyme AND Clinical Trial[Publication Type]\" on 2026-09-09 "
     "(total_count=1, fully enumerated) no OTHER clinical record is in the retrieved public record. "
     "The unknown that actually remains is whether any post-2018 solid-tumour clinical work exists "
     "at all: none is in the retrieved public record under these queries, on this date, with this "
     "closure. Publication activity is NOT extinct — anchor query total_count=272 all years, 97 "
     "for 2000-2009, 55 for 2015-2026 — so \"largely a 2000s-era approach\" overstates a "
     "distribution it never cited.")
r["remaining_unknowns"][1]=corr(new,old)
edits.append("remaining_unknowns[1]")

old=r["grade"]["value"]
r["grade"]["value"]=corr("Tier 3 — vector delivery; a technique whose only retrieved solid-tumour "
    "clinical record is a single 2018 phase I trial (PMID 30393375) that reported no meaningful "
    "clinical benefit, with no later clinical record in the retrieved public record", old)
edits.append("grade.value")

old=r["closure_note"]
r["closure_note"]=corr("Vector delivery; and a technique with one retrieved solid-tumour clinical "
    "record (2018 phase I, PMID 30393375) and none later in the retrieved public record.", old)
edits.append("closure_note")

old=r["readiness"]["why_not_higher"]
r["readiness"]["why_not_higher"]=corr("Two independent gates — delivery, and a clinical base "
    "consisting of a single retrieved 2018 phase I solid-tumour trial with no later retrieved "
    "record — and no computation addresses either.", old)
edits.append("readiness.why_not_higher")

old=r["readiness"]["missing"][1]
r["readiness"]["missing"][1]=corr("a solid-tumour clinical demonstration later than the single "
    "retrieved 2018 phase I trial (PMID 30393375)", old)
edits.append("readiness.missing[1]")

assert len(rs)==n_before, "route count changed"
assert len(r["remaining_unknowns"])==2 and len(r["readiness"]["missing"])==2
assert r["blockers_inherited"]==["BLK-VECTOR-DELIVERY"]
assert r["state"]["status"]=="parked"
out=json.dumps(d,indent=2,ensure_ascii=False)
if raw.endswith("\n"): out+="\n"
open("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/routes.modified.json","w",encoding="utf-8").write(out)
print("edited fields:",edits)
print("route count:",n_before,"->",len(rs),"; status:",r["state"]["status"],"; blockers_inherited:",r["blockers_inherited"])
