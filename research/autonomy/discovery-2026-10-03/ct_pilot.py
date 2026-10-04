"""Independent replay of exploratory within-patient metastatic CT comparison."""
import urllib.request,xml.etree.ElementTree as E,json,hashlib,statistics,math
from pathlib import Path
u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4110079/fullTextXML'
b=urllib.request.urlopen(u,timeout=45).read();root=E.fromstring(b)
tab=next(t for t in root.iter('table-wrap') if t.find('caption') is not None and ''.join(t.find('caption').itertext()).startswith('Hounsfield units'))
headers=['case','primary','recurrence','mediastinal_nodes','abdominal_nodes','retroperitoneum','lung','soft_tissue','bone']
rows=[[(''.join(c.itertext()).strip() or None) for c in tr.findall('td')] for tr in tab.findall('./table/tbody/tr')]
assert all(len(r)==len(headers) for r in rows)
pairs=[]
for row in rows:
    extra=[float(row[i]) for i in [3,4,5,7,8] if row[i] is not None]
    if extra and row[6] is not None:
        lung=float(row[6]);m=statistics.median(extra)
        pairs.append(dict(case=row[0],lung_HU=lung,extrapulmonary_site_values_HU=extra,median_extra_HU=m,delta_HU=m-lung))
d=[r['delta_HU'] for r in pairs];n=len(d);k=sum(v>0 for v in d)
nonzero=[v for v in d if v!=0];nn=len(nonzero);kk=sum(v>0 for v in nonzero)
p=min(1,2*sum(math.comb(nn,j) for j in range(min(kk,nn-kk)+1))/2**nn)
result=dict(source=u,raw_xml_sha256=hashlib.sha256(b).hexdigest(),headers=headers,printed_rows=rows,pairs=pairs,n=n,positive=k,median_delta_HU=statistics.median(d),range_delta_HU=[min(d),max(d)],sign_test_two_sided_p=p,
    disposition='Rejected: five selected paired patients; weak direction; protocol/timing/site confounding, no independent replication',
    design='Exploratory after table inspection; exclude primary/local recurrence, patient-level unit; site values reflect source selection at largest burden and include averages of multiple lung/nodal metastases')
(Path(__file__).parent/'ct-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['headers','printed_rows']},indent=2))
