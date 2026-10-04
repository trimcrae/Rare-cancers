"""Complete GSE80126 sample-metadata audit; reuse frozen target measurements."""
import hashlib,json,urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parent
URL='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE80126&targ=gsm&form=text&view=full'
with urllib.request.urlopen(URL,timeout=45) as r:b=r.read(15000001)
assert len(b)<=15000000
samples=[]
for p in b.decode().split('^SAMPLE = ')[1:]:
    fields={}
    for l in p.splitlines():
        if l.startswith('!Sample_') and ' = ' in l:
            key,value=l.split(' = ',1);fields.setdefault(key[8:],[]).append(value)
    samples.append({'GSM':p.splitlines()[0],'fields':fields})
assert len(samples)==29
emc=[s for s in samples if any('extraskeletal myxoid chondrosarcoma' in v.lower() for v in s['fields'].get('characteristics_ch1',[]))]
assert len(emc)==1 and emc[0]['GSM']=='GSM2113301'
old=BASE.parent/'tmem266-tissue-2026-10-03'
data=json.loads((old/'cultured-emc-recount-results.json').read_text())
out={'series':'GSE80126','source':{'url':URL,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},
     'all_sample_metadata':samples,'explicit_EMC_samples':emc,
     'TMEM266_reused':data['genes']['TMEM266'],
     'frozen_source':{'path':'../tmem266-tissue-2026-10-03/cultured-emc-recount-results.json','sha256':hashlib.sha256((old/'cultured-emc-recount-results.json').read_bytes()).hexdigest()},
     'scope':'All29GEOsamples screened by explicit histology; one biological EMC culture, two technical runs. Other samples with fibromyxoid in a different diagnosis are not EMC. GEO processed sample contains fusion calls, not gene abundance; prior recount3 gene/base coverage retained in its own units.'}
(BASE/'davila-census.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'samples':len(samples),'EMC_GSM':[s['GSM'] for s in emc],'target':out['TMEM266_reused']},indent=2))
