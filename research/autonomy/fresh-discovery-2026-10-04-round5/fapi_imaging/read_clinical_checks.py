import pathlib,json,xml.etree.ElementTree as E
D=pathlib.Path(__file__).resolve().parent
out={}
for name in ['ferdinandus2022.xml','novruzov2026.xml']:
 r=E.parse(D/name).getroot();pars=[' '.join(x.itertext()) for x in r.findall('.//p')]
 out[name]=[p for p in pars if any(q in p.lower() for q in ['conventional chondro','previously reported','already','nct','inclusion','data availab','surgery','biopsy'])]
 print(name)
 for p in out[name]: print(p[:3000])
p=json.loads((D/'source-evaluation.json').read_text())
for t in p['xmls']['novruzov2026.xml']['tables']:
 if t['id']=='Tab1':print(t['rows'])
for t in p['pdfs']['pabst2025.pdf']['pages']:
 if 'Data sharing' in t: print(t[t.index('Data sharing'):t.index('Data sharing')+1600])
(D/'clinical-context-checks.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
