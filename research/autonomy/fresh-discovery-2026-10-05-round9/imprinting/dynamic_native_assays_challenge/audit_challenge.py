#!/usr/bin/env python3
"""Source-only dynamic challenge replay: hashes, identities and all30 conditions. No values."""
import argparse,hashlib,json,re,shutil
from pathlib import Path
import xml.etree.ElementTree as E
OWN=Path(__file__).resolve().parent

def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    checks=[]
    def c(label,good):
        assert good,label
        checks.append({'check':label,'pass':bool(good)})
    c('Prospective pre-source plan exact',sha(OWN/'PLAN.json')=='bc8a04bd714842e40d6528ed04ff50797b851b3ce69ff3fcc3bd97b8e099aaa1')
    close=json.loads((OWN/'SOURCE-GATE-CLOSED.json').read_text())
    for f in close['raw_inventory']:
        q=OWN/f['path'];c('New ignored catalogue/source hash '+q.name,sha(q)==f['sha256'] and q.stat().st_size==f['bytes'])
    c('Raw soft cap8MiB respected including originals',sum(f['bytes'] for f in close['raw_inventory'])<=8388608)
    d=json.loads((OWN/'raw-cache/geo-broader-dynamic-series-metadata.json').read_text())['result']
    c('All53 metadata returned for exactGEOquery',len(d['uids'])==53)
    # No53-source analytical export; only source98824 conditions actually evaluated.
    a=json.loads((OWN/'EVALUATED-BROADER-SOURCE.json').read_text());rows=a['all_condition_rows'];m=a['models']
    c('All30 unique sample conditions, six models not donor count',len(rows)==len(set(x['gsm'] for x in rows))==30 and len(m)==6 and a['independent_donor_count'] is None)
    expected={(2,'Buparlisib treatment'),(50,'Buparlisib treatment'),(50,'washout'),(2,'control'),(50,'control')}
    for model in m:c('Complete five declaredconditions '+model,{(x['declared_hr_label'],x['condition']) for x in rows if x['source_model']==model}==expected)
    source=(OWN/'raw-cache/GSE98824-source-metadata.txt').read_text()
    source_ids=[x.split(' = ',1)[1] for x in source.splitlines() if x.startswith('!Series_sample_id = ')]
    c('Exact officialseries30GSMlist and allcatalogue30titles agree',set(source_ids)==set(x['gsm'] for x in rows)==set(x['accession'] for x in d['200098824']['samples']))
    c('Officialsource defines breastPDXpanel, not title-name inference','panel of triple negative breast cancer patient derived xenograft models' in source and a['source_identity_sentence'] in source)
    z=json.loads((OWN/'PRIMARY-DYNAMIC-METHOD-CHECK.json').read_text());q=Path(z['cached_runtime_path']);c('Zero-copy ownerprimary hash',sha(q)==z['sha256'] and q.stat().st_size==z['bytes'])
    r=E.parse(q).getroot()
    def t(e):return ' '.join(''.join(e.itertext()).split())
    methods=[x for x in r.findall('.//body//sec') if t(x.find('title'))=='Materials and Methods'][0]
    for selected in z['selected_methods']:
        node=[x for x in methods.findall('./sec') if t(x.find('title'))==selected['title']][0]
        c('Exact primary selected method '+selected['title'],selected['source_method_paragraphs']==[t(x) for x in node.findall('./p')])
    culture=[x for x in z['selected_methods'] if x['title']=='Cell Culture'][0]['source_method_paragraphs'][0]
    c('Five explicit source cellmodels, not nativeEMC inferredfromTAF15',all(n in culture for n in ['HCT116','HT29','HeLa','MCF7','MKN45']) and 'All five cell lines' in culture)
    c('No new endpointstage, source gateclosed',close['new_numerical_outcomes_inspected']==0 and close['numerical_or_matrix_stage_authorized'] is False and close['scientific_source_calls_closed'] is True)
    free=shutil.disk_usage(OWN).free;c('Atleast10GiBfree',free>=10737418240)
    out={'status':'PASS','checks':checks,'new_raw_bytes':sum(x['bytes'] for x in close['raw_inventory']),'free_bytes':free,'scope':'Hash/metadata/condition/primarymethod replay only;53catalogue rows are not source evaluations, cellmodels not patient donors. No RNA matrix/response/withdrawal numerical outcome or globalpubliccoverage/publicationcertificate.'}
    args.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'newraw':out['new_raw_bytes'],'free':free}))

if __name__=='__main__':main()
