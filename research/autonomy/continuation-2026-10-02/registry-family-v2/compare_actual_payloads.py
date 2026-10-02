"""Inspect actual v1/v2 exports against frozen source; no classifier execution."""
import argparse, hashlib, json
from pathlib import Path

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode()
def require(ok, msg):
    if not ok: raise ValueError(msg)
def read(p): return json.loads(p.read_bytes())
def digest(x): return hashlib.sha256(canonical(x)).hexdigest()
def verify(source, extraction, companions):
    native={}
    for si,s in enumerate(source["studies"]):
        nct=s["protocolSection"]["identificationModule"]["nctId"]
        for oi,o in enumerate(s.get("resultsSection",{}).get("outcomeMeasuresModule",{}).get("outcomeMeasures",[])):
            native[(si,nct,oi)]=o
    outcomes={}
    for item in extraction["outcomes"]:
        key=item["outcomeKey"]
        coord=tuple(key[1:4])
        require(coord in native and coord not in outcomes,"Unexpected/duplicate outcome")
        require(item["literal"]==native[coord],"Full source outcome differs")
        require(key[4]==digest(native[coord]),"Outcome digest differs")
        outcomes[coord]=item
    require(set(outcomes)==set(native),"Outcome coverage")
    expected_rows=set()
    expected_measurements=set()
    for coord,o in native.items():
        for ci,cls in enumerate(o.get("classes",[])):
            gids={g.get("id") for g in o.get("groups",[])}
            for ki,c in enumerate(cls.get("categories",[])):
                for mi,m in enumerate(c.get("measurements",[])):
                    gids.add(m.get("groupId"))
                    expected_measurements.add(coord+(ci,ki,mi))
            expected_rows.update(coord+(ci,gid) for gid in gids)
    rows={}; seen_measurements=set(); denominator_records=0
    for row in extraction["rows"]:
        key=row["outcomeKey"]; coord=tuple(key[1:4]); ci=row["classIndex"]; gid=row["groupId"]
        rk=coord+(ci,gid)
        require(rk in expected_rows and rk not in rows,"Unexpected/duplicate class/group row")
        o=native[coord];cls=o["classes"][ci]
        require(row["rowKey"]==key+[ci,gid],"Row key differs")
        require(row["parentClassCount"]==len(o["classes"]),"Class count differs")
        require(row["classLiteral"]=={k:v for k,v in cls.items() if k!="categories"},"Class literal differs")
        require(row["groupDefinitions"]==[g for g in o.get("groups",[]) if g.get("id")==gid],"Group definitions differ")
        expected_cells=[]
        for ki,c in enumerate(cls.get("categories",[])):
            for mi,m in enumerate(c.get("measurements",[])):
                if m.get("groupId")==gid: expected_cells.append((ki,mi))
        actual_cells=[]
        for m in row["measurements"]:
            ki,mi=m["categoryIndex"],m["measurementIndex"]
            actual_cells.append((ki,mi));c=cls["categories"][ki];v=c["measurements"][mi]
            require(v.get("groupId")==gid and m["measurementLiteral"]==v,"Measurement differs")
            require(m["categoryLiteral"]=={k:v for k,v in c.items() if k!="measurements"},"Category differs")
            marker=coord+(ci,ki,mi)
            require(marker not in seen_measurements,"Duplicate measurement")
            seen_measurements.add(marker)
        require(actual_cells==expected_cells,"Measurement order/coverage differs")
        for scope,container,field in [("class",cls,"classEntries"),("outcome",o,"outcomeEntries")]:
            actual=row["denominators"][field]
            expected=[]
            for di,d in enumerate(container.get("denoms",[])):
                for vi,count in enumerate(d.get("counts",[])):
                    if count.get("groupId")==gid:
                        expected.append((scope,di,vi,d.get("units"),count))
            got=[(x["scope"],x["denomIndex"],x["countIndex"],x["unitsLiteral"],x["countLiteral"]) for x in actual]
            require(got==expected,"Literal denominator entries differ")
            denominator_records+=len(got)
        rows[rk]=row
    require(set(rows)==expected_rows,"Class/group coverage")
    require(seen_measurements==expected_measurements,"Measurement coverage")
    by_unit={(r["outcomeKey"][2],r["outcomeKey"][4],r["classIndex"],r["groupId"]):r for r in rows.values()}
    require(len(by_unit)==len(rows),"Unit collision")
    seen_units=set()
    for c in companions:
        u=tuple(c["unit"])
        require(u in by_unit and u not in seen_units,"Companion unit mismatch")
        seen_units.add(u);r=by_unit[u]
        require(c["acceptedRowUnchanged"]==r,"Companion accepted payload differs")
        require(c["acceptedRowSHA256"]==digest(r),"Accepted payload digest differs")
    return {"outcomes":len(outcomes),"literalRows":len(rows),"sourceMeasurements":len(seen_measurements),
            "literalDenominatorRecordsIncludingRepeatedScopes":denominator_records,"companionRows":len(seen_units)}

def main():
    p=argparse.ArgumentParser()
    for name in ("source","v1","v2","out"):p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args();raw=a.source.read_bytes()
    require(hashlib.sha256(raw).hexdigest()=="d20367d3d14f99716b20309ee8bed1cebe4b6a1270077fc0ac234a4cc5b91fa6","Source digest")
    source=json.loads(raw); versions={}; loaded={}
    for label,d in [("v1",a.v1),("v2",a.v2)]:
        e=read(d/"literal-extraction.json");c=read(d/"family-companions.json")
        versions[label]=verify(source,e,c);loaded[label]=(e,c)
    require(loaded["v1"][0]==loaded["v2"][0],"Literal extraction changed between versions")
    one={tuple(x["unit"]):x for x in loaded["v1"][1]}
    two={tuple(x["unit"]):x for x in loaded["v2"][1]}
    require(set(one)==set(two),"Companion unit coverage changed")
    require(all(one[k]["acceptedRowUnchanged"]==two[k]["acceptedRowUnchanged"] for k in one),"Accepted rows changed")
    before=read(a.v1/"outcome-comparisons.json");after=read(a.v2/"outcome-comparisons.json")
    b={x["sourcePointer"]:x for x in before};n={x["sourcePointer"]:x for x in after}
    require(set(b)==set(n),"Evaluated outcomes changed")
    changes=[]
    for k,x in n.items():
        require(x["oracle"]==b[k]["oracle"],"Oracle labels changed")
        if x["comparisonPrediction"]!=b[k]["comparisonPrediction"]:
            changes.append({"sourcePointer":k,"nctId":x["outcomeKey"][2],"outcomeIndex":x["outcomeKey"][3],
                            "before":b[k]["comparisonPrediction"],"after":x["comparisonPrediction"],
                            "beforeJointAgreement":b[k]["jointAgreement"],"afterJointAgreement":x["jointAgreement"]})
    result={"schema":"registry-actual-payload-regression-audit/1","status":"passed","versions":versions,
            "fullLiteralExportsUnchanged":True,"acceptedPayloadsUnchanged":True,"frozenOracleUnchanged":True,
            "evaluatedOutcomes":len(n),"changedPredictions":changes,
            "scope":"Actual exported literals, measurements, denominator records and companion accepted payloads checked. Normalized clinical correctness not re-adjudicated. Seen-case regression only, not independent generalization."}
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
