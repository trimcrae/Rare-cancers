"""Replay the prospective all-11 origin/event-type gate; no efficacy estimate.
Only native source identity/PFS fields and clinical endpoint definitions are read.
No external cohort, image or genomic mechanism is used.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
SOURCE_SHA='390e456b36664c767f2b06d5bc6c5ffc2afcf5f2d1074727dd5c06fc248bf8c7'
def txt(e):
 return ' '.join(''.join(e.itertext()).split()) if e is not None else ''
def run(source):
 b=source.read_bytes();assert hashlib.sha256(b).hexdigest()==SOURCE_SHA
 r=E.fromstring(b);table=next(t for t in r.findall('.//table-wrap') if t.get('id')=='T2')
 tr=table.findall('.//tr');headers=[txt(x) for x in tr[0]];foot=txt(table.find('table-wrap-foot'))
 assert '*Patient treated with surgery after chemotherapy, censored at the time of surgical resection' in foot
 rows=[]
 for x in tr[1:]:
  values=[txt(c) for c in x]
  if len(values)!=len(headers):continue
  q=dict(zip(headers,values));assert q['NR4A3 rearrangement']=='yes'
  pfs=q['PFS'];m=re.fullmatch(r'(\d+(?:\.\d+)?)(\*)?',pfs);assert m,pfs
  surgery=bool(m[2])
  rows.append({'source_case_id':q['Patient ID'],'identity':'Native author-EMC; source NR4A3 rearrangement yes','source_pfs_literal':pfs,'source_elapsed_value':float(m[1]),'column_unit_literal':None,'context_units':'months in published cohort PFS statement; column itself has no unit','common_treatment_origin':None,'terminal_type':'complete surgery (source footnote)' if surgery else None,'terminal_type_limit':None if surgery else 'Plain PFS duration; individual progression/death versus last-contact censor state not explicitly coded','source_recist_accessed_by_this_script':False})
 assert len(rows)==11 and {x['source_case_id'] for x in rows}=={str(i) for i in range(1,12)}
 assert [x['source_case_id'] for x in rows if x['terminal_type']]==['1','7','10']
 clinical=[]
 for s in r.findall('./body/sec'):
  if txt(s.find('title')).lower() in ['methods','materials and methods','results','discussion','conclusions','conclusion']:
   for p in s.findall('.//p'):
    text=txt(p)
    # Restrict to clinical definition/context; exclude diagnostic mechanism fields.
    if re.search(r'fusion|rearrang|FISH|\bHLA\b|\bFAP\b|glycan|\bRET\b',text,re.I):continue
    if re.search(r'PFS|censor|survival|surgical resection|external controls',text,re.I):clinical.append(text)
 origin=[x for x in clinical if re.search(r'(?:PFS|progression.free survival).{0,160}(?:from|since).{0,30}(?:start|initiat|first dose|chemotherap)|(?:from|since).{0,30}(?:start|initiat|first dose).{0,80}(?:PFS|progression.free survival)',x,re.I)]
 assert not origin,'New explicit origin requires independent source inspection, not automatic repair.'
 postop=next(x for x in clinical if 'patient 1/7/10' in x and '24/12/24 months from surgery' in x)
 inputs={'postoperative_published_conditions':[{'source_case_id':i,'origin':'complete surgery, explicitly stated in Results','later_event':'new distant relapse','source_elapsed_months':v,'novelty':'Published authors observation; no new effect estimate'} for i,v in [('1',24),('7',12),('10',24)]],'postoperative_source_quote':postop,'source':{'path':str(source),'bytes':len(b),'sha256':SOURCE_SHA},'all11_source_rows':rows,'surgery_definition_footnote':foot,'scope':'Exact source PFS/identity projection after prospective analysis freeze; no assumed terminal events, common origin or calendar dates.'}
 result={'analyzed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_native_source_rows':len(rows),'explicit_surgery_case_ids':['1','7','10'],'explicit_surgery_count':3,'individual_terminal_event_or_ordinary_censor_unknown_count':8,'common_origin_explicit':False,'origin_search_scope':'Clinical METHODS/RESULTS/DISCUSSION/CONCLUSION paragraphs, not denied mechanism fields; exact permitted definition pattern plus manual source inspection','six_month_cif':None,'six_month_bounds':None,'bootstrap_run':False,'survival_curve_reconstruction_performed':False,'clinical_failure_count':None,'decision':'STOP event-time numerical estimation: explicit common origin and eight final event/censor states missing. Complete surgery is not progression.','published_context':'Original authors explicitly map later distant relapse in patients1/7/10 after surgery and already discuss its interpretation; do not recast that published follow-up as a new finding.','scope_limits':'Counts are source schema observations, not survival probabilities, absence of failure or an efficacy result. Non-identifiability does not demonstrate the published KM estimate was biased or that surgery worsens outcome.','all11_source_inputs_retained':True,'independence':'One selected institutional/rare-cancer-network series, not all EMC. No pooling or donor independence across reports assumed.'}
 return inputs,result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=D/'raw-cache/PMC3879193.xml');ap.add_argument('--write',action='store_true');a=ap.parse_args()
 inp,res=run(a.source)
 if a.write:
  (D/'ALL11-SOURCE-INPUTS.json').write_text(json.dumps(inp,indent=2)+'\n')
  (D/'MEASUREMENT-GATE-RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
 print(json.dumps({k:res[k] for k in ['all_native_source_rows','explicit_surgery_count','individual_terminal_event_or_ordinary_censor_unknown_count','common_origin_explicit','six_month_cif','six_month_bounds','decision']},indent=2))
