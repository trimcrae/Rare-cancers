#!/usr/bin/env python3
"""Replay primary method/source fields; no ADC/IVIM values or graphical outcomes."""
import argparse, hashlib, json, re, shutil
from pathlib import Path
import xml.etree.ElementTree as E
OWN=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    a=json.loads((OWN/'PRIMARY-TEXT-GATE.json').read_text());p=args.source or Path(a['source']['runtime_path']);r=E.parse(p).getroot()
    def t(e):return ' '.join(''.join(e.itertext()).split())
    checks=[]
    def c(k,v):
        assert v,k
        checks.append({'check':k,'pass':bool(v)})
    c('Prospective own pre-field PLAN unchanged',hashlib.sha256((OWN/'PLAN.json').read_bytes()).hexdigest()=='bdfcb3320d8f164f46d985f1e344305ec3fa8fedae10172debdec61239dd7455')
    c('Original cached primary XML hash and size',hashlib.sha256(p.read_bytes()).hexdigest()==a['source']['sha256'] and p.stat().st_size==56009)
    for s in a['selected_physical_methods']:
        z=r.find(".//sec[@id='%s']"%s['section_id'])
        c('Selected original physical-method section '+s['section_id'],s['physical_method_paragraphs']==[t(x) for x in z.findall('./p')])
    pt=a['selected_physical_methods'][0]['physical_method_paragraphs'][0]
    c('Enrollment/exclusions31 minus4 minus1 minus3 equals23',31-4-1-3==23 and all(q in pt for q in ['Thirty-one consecutive','4 patients did not receive surgery','1 tumor in the upper limb','other 3 patients','only 23 STTs']))
    ivim=a['selected_physical_methods'][2]['physical_method_paragraphs'][0];b=re.search(r'10 b values \[([^\]]+)\]',ivim)
    acquisition_values=[int(s) for s in re.findall(r'\d+',b.group(1).split('s/mm')[0])] if b else []
    c('Exactly10 source acquisition b-values, not endpoint values',acquisition_values==[0,10,20,30,50,100,200,300,500,800])
    roi=a['selected_physical_methods'][4]['physical_method_paragraphs'][0]
    c('Nine repeated ROIs; excluded cysts/necrosis/vessels',all(s in roi for s in ['totally 9 ROIs in 3 consecutive images','Large cystic or necrotic areas and large vessels were not included']))
    t1=r.find(".//table-wrap[@id='T1']")
    c('T1 authenticated graphic filename; no HTML measurement table',t1.find('.//graphic').get('{http://www.w3.org/1999/xlink}href')=='medi-94-e1028-g001.jpg' and t1.find('.//table') is None)
    free=shutil.disk_usage(OWN).free;c('At least10GiB free',free>=10737418240)
    x={'status':'PASS','checks':checks,'source_sha256':a['source']['sha256'],'scope':'Primary physical method/field provenance only. No roster image or any endpoint extracted; actual EMC eligibility remains pending at this stage. Not all-public-source coverage or publication certification.','new_originals_retained_bytes':0,'free_bytes':free,'initial_parser_failure':'Inline initial acquisition parser did not handle the printed conjunction and unit; no scientific output written. Fixed parser extracts digits only before s/mm unit. Source definitions unchanged.'}
    args.output.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'free_bytes':free}))

if __name__=='__main__':main()
