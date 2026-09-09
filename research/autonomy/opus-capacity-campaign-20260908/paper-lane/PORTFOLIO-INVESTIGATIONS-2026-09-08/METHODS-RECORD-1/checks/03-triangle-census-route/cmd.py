import json,hashlib
def L(p):
    b=open(p,'rb').read(); return json.loads(b), hashlib.sha256(b).hexdigest()
def flat(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+"."+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from flat(v,p+"[%d]"%i)
    else: yield p,o
print("=== triangle")
d,h=L("research/modalities/valb-triangle-reduction.json"); print("sha",h)
for k,v in flat(d):
    if isinstance(v,(int,float)) and not isinstance(v,bool): print(k,"=",v)
    elif isinstance(v,str) and ("NONE QUOTED" in v or "n=1" in v): print(k,"=",v[:120])
print("=== census")
d,h=L("research/modalities/instrument-census.json"); print("sha",h,"type",type(d))
ids=[]
def each(o):
    if isinstance(o,list):
        for e in o: each(e)
    elif isinstance(o,dict):
        if 'id' in o and isinstance(o.get('id'),str) and o['id'].startswith('V'): ids.append(o)
        else:
            for v in o.values(): each(v)
each(d)
print("n instruments:",len(ids),[i['id'] for i in ids])
for i in ids:
    if i['id'] in ('V5','V6','V7','V8','V10'):
        print(i['id'],"| KAT:",repr(i.get('known_answer_test'))[:200])
        print("    result:",repr(i.get('result'))[:250])
print("=== routes RT-METHODS-PAPER")
d,h=L("systems/graph/routes.json"); print("sha",h)
def findroute(o):
    if isinstance(o,list):
        for e in o: yield from findroute(e)
    elif isinstance(o,dict):
        if o.get('id')=='RT-METHODS-PAPER': yield o
        else:
            for v in o.values(): yield from findroute(v)
for r in findroute(d):
    ins=r.get('instruments')
    print("keys",list(r.keys()))
    print(json.dumps(ins,indent=1)[:2000])
