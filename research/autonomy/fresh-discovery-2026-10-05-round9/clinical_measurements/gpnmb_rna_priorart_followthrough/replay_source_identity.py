"""Offline clinical/source replay. Never reads expression table cells or mechanisms."""
import pathlib,json,hashlib,re,collections,datetime,shutil,lxml.etree as E
P=pathlib.Path(__file__).resolve().parent;checks=[];deviations=[]
def ck(name,ok):checks.append({'name':name,'pass':bool(ok)})
plan=json.loads((P/'PLAN-FROZEN.json').read_text());deadline=datetime.datetime.fromisoformat(plan['scientific_deadline_utc'])
raw=0
for n in range(1,5):
 a=json.loads((P/f'ACCESS-{n:02}.json').read_text());r=json.loads((P/f'ROUTE-{n:02}-FROZEN.json').read_text());start=datetime.datetime.fromisoformat(a['utc']);end=datetime.datetime.fromisoformat(a['completed_utc'])
 ck(f'route{n} before request',datetime.datetime.fromisoformat(r['frozen_at_utc'])<start)
 ck(f'call{n} before deadline',end<deadline)
 ck(f'call{n} anonymous nominal10second timeout',a['anonymous'] and a['timeout_seconds']==10 and not a['redirects'])
 if a['complete_response']:
  f=pathlib.Path(a['path']);b=f.read_bytes();raw+=len(b);ck(f'original{n} exact hash',hashlib.sha256(b).hexdigest()==a['sha256']);ck(f'original{n} size/cap',len(b)==a['bytes'] and len(b)<=a['cap_bytes'])
 else:ck(f'call{n} failure retained no accepted file',n==3 and a.get('error')=='The read operation timed out' and not (P/f'raw-cache/stage-{n:02}.source').exists())
 if (end-start).total_seconds()>10:deviations.append({'call':n,'wall_elapsed_seconds':(end-start).total_seconds(),'scope':'Nominal socket timeout plus overhead exceeded strict wall cap; record retained, no retry/acceptedbytes; overallalarm added beforecall4.'})
ck('four bounded calls no retry',len(list(P.glob('ACCESS-*.json')))==4)
ck('raw cap',raw<plan['caps']['raw_bytes'])
ck('free storage',shutil.disk_usage(P).free>=plan['caps']['free_bytes'])
for s in json.loads((P/'SOURCE-PORTABILITY.json').read_text())['reused_bindings']:
 f=pathlib.Path(s['path']);ck('prior hash '+f.name,hashlib.sha256(f.read_bytes()).hexdigest()==s['sha256'])
meta=json.loads((P/'REUSED-PRIMARY-METADATA.json').read_text());ck('original metadata unchanged',hashlib.sha256(pathlib.Path(meta['source_path']).read_bytes()).hexdigest()==meta['source_sha256'])
for n,pmid,doi in [(1,'18447899','10.1186/1471-2164-9-201'),(2,'32596059','10.7717/peerj.9394')]:
 x=E.fromstring((P/f'raw-cache/stage-{n:02}.source').read_bytes());ids={a.get('pub-id-type'):''.join(a.itertext()) for a in x.xpath('./front/article-meta/article-id')};ck(f'primary{n} exact PMID/DOI',ids['pmid']==pmid and ids['doi']==doi)
 # Only source annotation cells (not expression outcomes) at the fixed target row.
 if n==1:
  target=[]
  for row in x.xpath('.//table-wrap[@id="T3"]//tr'):
   c=row.xpath('./td|./th')
   if len(c)>=3 and 'GPNMB' in ''.join(c[1].itertext()):target.append({'Unigene_cluster':''.join(c[0].itertext()).strip(),'Symbol':''.join(c[1].itertext()).strip(),'Gene_Name':''.join(c[2].itertext()).strip()})
  ck('fixed target source annotation unique',len(target)==1 and target[0]['Symbol']=='GPNMB')
  (P/'TARGET-GENE-ANNOTATION-ONLY.json').write_text(json.dumps({'rows':target,'scope':'Only firstthree sourceannotation columns; no outcome cells.'},indent=2)+'\n')
  cap=' '.join(x.xpath('.//fig[@id="F4"]/caption')[0].itertext());ck('different-probe case pairing explicitly recorded','medulloblastoma (A)' in cap and 'adenocarcinoma (B)' in cap and 'Ewing sarcoma (C)' in cap and 'ADAM12, GPNMB and PRSS3, respectively' in cap)
# Re-extract only all75 sourceidentity/type fields from retained GEO brief, not sample data.
original={}
for ch in re.split(r'(?m)^\^SAMPLE = ',(P/'raw-cache/stage-04.source').read_text())[1:]:
 lines=ch.splitlines();gsm=lines[0].strip();types=[s.split(' = ',1)[1] for s in lines if s.startswith('!Sample_characteristics_ch1 = type: ')];titles=[s.split(' = ',1)[1] for s in lines if s.startswith('!Sample_title = ')];original[gsm]={'type':types,'title':titles}
rows=json.loads((P/'GSE68591-ALL-SOURCE-CONDITIONS.json').read_text())['records'];ck('all75 unique conditions',len(rows)==len(original)==75 and len(set(r['GSM'] for r in rows))==75)
ck('all type fields source-replayed',all(original[r['GSM']]['type']==r['RNA_characteristics'] and original[r['GSM']]['title']==r['title'] for r in rows))
ck('all75 type fields present',all(len(r['RNA_characteristics'])==1 for r in rows))
ck('70 model/5 normal source conditions',collections.Counter(';'.join(r['source_name']) for r in rows)=={'human cell line':70,'normal human cell':5})
d=json.loads((P/'GSE68591-SOURCE-UNIT-AND-IDENTITY-DISPOSITION.json').read_text());ck('all75 dispositions',len(d['all75_source_dispositions'])==75)
ck('all15 generic identities retained',len(d['generic_identity_pending_GSMs'])==15)
ck('duplicate source models retained',d['repeated_exact_model_labels']=={'A-204':2,'ES-4':2})
q=json.loads((P/'ALL-SOURCE-CONDITION-AND-PRIORART-DISPOSITIONS.json').read_text());ck('Pestana full7/206 originalscope',len(q['Pestana2021']['native_cohort'])==7 and sum(x['n_source_specimens'] for x in q['Pestana2021']['native_cohort'])==206)
ck('Stockwin four native/control-source roles',len(q['Stockwin2020']['native_conditions'])==4)
ck('no numerical stage',not json.loads((P/'DECISION.json').read_text())['numeric_stage'])
ck('compact cap',sum(f.stat().st_size for f in P.iterdir() if f.is_file())<plan['caps']['derived_bytes'])
out={'scope':'Offline sourceidentity/coverage/provenance verification; no network or expression values. Not a whole-study absence or publication approval.','checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks),'transport_deviations':deviations,'new_raw_bytes':raw,'status':'PASS for source scope with recorded transport deviation' if all(x['pass'] for x in checks) else 'FAIL'}
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['passed'],out['total'])
if not all(x['pass'] for x in checks):raise SystemExit(1)
