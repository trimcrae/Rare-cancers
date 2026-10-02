import csv,gzip,hashlib,json,xml.etree.ElementTree as E
from pathlib import Path
p=Path(__file__).parent
old=p.parent/'checkpoint05-hla'
sha=lambda b:hashlib.sha256(b).hexdigest()
files=json.loads((old/'pride-files.json').read_text())
results=sorted((r for r in files if r['fileCategory']['value']=='RESULT'),key=lambda r:(r['fileSizeBytes'],r['fileName']))
selected=results[0]
b=(p/'sample-run.mzid.gz').read_bytes(); x=gzip.decompress(b)
assert hashlib.sha1(b).hexdigest()==selected['checksum']
assert len(x)==selected['fileSizeBytes']
r=E.fromstring(x)
local=lambda e:e.tag.split('}')[-1]
wanted=['AnalysisSoftwareList','AnalysisProtocolCollection','SearchDatabase','SourceFile']
parts=[e for e in r.iter() if local(e) in wanted]
parameters='\n'.join(E.tostring(e,encoding='unicode') for e in parts)
(p/'sample-run-parameters.xml').write_text(parameters,encoding='utf-8')
rows=list(csv.DictReader((old/'archive-readme.txt').open(encoding='utf-8'),delimiter='\t'))
counts={t:sum(r['TYPE']==t for r in rows) for t in sorted(set(r['TYPE'] for r in rows))}
xml=E.parse(old/'primary.xml')
context=[{'section':'/'.join([]),'text':''.join(e.itertext())} for e in xml.iter('p') if 'Identification of cryptic HLA-I peptides from HLA-I LC-MS/MS data' in ''.join(e.itertext())]
# Keep this source-context extract small. It does not add a historical database identity.
(p/'primary-cryptic-context.json').write_text(json.dumps(context,indent=2),encoding='utf-8')
report={'selection':{'rule':'Minimum fileSizeBytes among RESULT entries in the reused first-100-row PRIDE API response; filename breaks ties. This is not the minimum across all 483 outputs. No biological selection and no prior output fetched.','api_rows':len(files),'result_candidates':len(results),'selected':selected},'compressed':{'bytes':len(b),'sha1':hashlib.sha1(b).hexdigest(),'sha256':sha(b)},'uncompressed':{'bytes':len(x),'sha256':sha(x)},'size_interpretation':'The API fileSizeBytes equals the observed uncompressed XML byte length, whereas its checksum agrees with SHA1 of the compressed response. Metadata does not name checksum algorithm.','readme':{'rows':len(rows),'type_counts':counts,'cryptic_name_hits':[r for r in rows if any(k in r['NAME'].lower() for k in ['cryptic','prism','denovo','parameter'])]},'source_hashes':{name:sha((old/name).read_bytes()) for name in ['primary.xml','pride-files.json','archive-readme.txt','archive-index.html']},'query_representation':{q:'UNKNOWN in historical cryptic search space; no scan performed' for q in ['NMPCVQAQY','QQNMPCVQAQY','SYGQQNMPCVQAQYS','DMPCVQAQY']}}
(p/'audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'selection':report['selection']['rule'],'api_rows':len(files),'candidate_count':len(results),'compressed':report['compressed'],'uncompressed':report['uncompressed'],'readme_counts':counts,'source_hashes':report['source_hashes']},indent=2))
