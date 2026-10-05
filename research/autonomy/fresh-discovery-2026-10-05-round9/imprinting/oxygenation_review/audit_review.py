#!/usr/bin/env python3
"""Verify frozen selected exports and source identity/method evidence only; no endpoint extraction."""
import argparse, hashlib, json, re, shutil
from pathlib import Path
import xml.etree.ElementTree as ET

DEFAULT_OWNER = Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/oxygenation_measurement_gate')
OWN = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def text(e):
    return ' '.join(''.join(e.itertext()).split())

def check(conditions, label, good, detail=None):
    conditions.append({'check': label, 'pass': bool(good), 'detail': detail})
    if not good:
        raise AssertionError(label)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--owner', type=Path, default=DEFAULT_OWNER)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    o = args.owner
    checks = []
    check(checks, 'Exact owner scientific freeze', sha(o/'SCIENCE-FREEZE.json') == '8a29bbd0e8b6c16b7d54cf5160f8de5f033498fe13877cef888c055e05c55225')
    check(checks, 'Exact owner selected-export manifest', sha(o/'MANIFEST.json') == '35431e2c18a499da8c2254b005ca700b32058e4322bf43196078242a39a6e2bb')
    m = json.loads((o/'MANIFEST.json').read_text())
    bindings = []
    for f in m['files']:
        p = o/f['path']
        check(checks, 'Owner frozen export '+f['path'], sha(p)==f['sha256'] and p.stat().st_size==f['bytes'])
        bindings.append({'path': f['path'], 'bytes': f['bytes'], 'sha256': f['sha256'], 'status': 'committed derived/source-gate export, not raw primary'})
    check(checks, 'Owner all37 selected files100646B', len(bindings)==37 and sum(f['bytes'] for f in bindings)==100646)
    audit = json.loads((OWN/'PRIMARY-METHOD-IDENTITY-AUDIT.json').read_text())
    originals=[]
    for s in audit['sources']:
        p=o/'raw'/(s['source']+'.xml')
        check(checks, 'Matching original '+s['source'], sha(p)==s['sha256'] and p.stat().st_size==s['bytes'])
        root=ET.parse(p).getroot()
        paragraphs=[text(e) for e in root.findall('.//body//p')]
        check(checks, 'Primary selected physical-method quotes '+s['source'], all(' '.join(q.split()) in paragraphs for q in s['selected_methods']))
        if s['source']=='PMC13536671':
            tab1=root.find(".//table-wrap[@id='Tab1']")
            diag=[r for r in tab1.findall('.//tbody/tr') if any('Extraskeletal myxoid chondrosarcoma' in text(c) for c in list(r))]
            check(checks,'FMISO one diagnostic aggregate row / five histotype counts', len(diag)==1 and [text(c) for c in list(diag[0])][-1].count('1 (20%)')==5)
            tab2=root.find(".//table-wrap[@id='Tab2']")
            headers=[text(c) for c in tab2.findall('.//thead//th')]
            subjects=[text(list(r)[0]) for r in tab2.findall('.//tbody/tr') if len(list(r))]
            check(checks,'Allfive subjectIDs only extracted from endpoint table', subjects==['Subject 1','Subject 2','Subject 3','Subject 4','Subject 5'])
            check(checks,'Subject table headers lack histology column', not any(re.search('histol|diagnos',h,re.I) for h in headers))
        elif s['source']=='PMC5846059':
            tab1=root.find(".//table-wrap[@id='tbl1']")
            diag=[r for r in tab1.findall('.//tbody/tr') if any('Extraskeletal myxoid chrondrosarcoma' in text(c) for c in list(r))]
            check(checks,'VorteX source labelled4 baselineEMC', len(diag)==1 and [text(c) for c in list(diag[0])][1]=='4')
            check(checks,'VorteX source averaging-unit wording preserved', any('for each tumour type' in q for q in s['selected_methods']))
        originals.append({'path': str(p), 'source': s['source'], 'bytes': s['bytes'], 'sha256': s['sha256'], 'status':'ignored owner cache-only original, no copy retained here'})
    g=json.loads((o/'PMC5117798-OXYGEN-IDENTITY-GATE.json').read_text())
    p=o/g['source']['path']
    check(checks,'Matching original electrode-linked primary', sha(p)==g['source']['sha256'])
    root=ET.parse(p).getroot()
    paragraphs=[text(e) for e in root.findall('.//body//p')]
    check(checks,'Electrode cohort selected source-method quotes match', all(' '.join(q.split()) in paragraphs for q in g['oxygenation_source_methods'] if not q.startswith('Diagram of patient selection')))
    check(checks,'Nine explicit gene-cohort histotypes132; not directoxygen roster', len(g['histology_roster'])==9 and sum(x['n'] for x in g['histology_roster'])==132 and all('myxoid chondro' not in x['histologic_label'].lower() for x in g['histology_roster']))
    originals.append({'path':str(p),'source':'PMC5117798','bytes':p.stat().st_size,'sha256':g['source']['sha256'],'status':'ignored owner cache-only original; selectedmethods/roster only'})
    d=json.loads((o/'DECISION.json').read_text())
    check(checks,'Owner no finding / no numerical-stage decision', d['findings_surviving']==0 and 'SHELVE' in d['decision'])
    close=json.loads((o/'SOURCE-GATE-CLOSED.json').read_text())
    check(checks,'Owner no newly inspected numerical endpoints', close['new_EMC_endpoint_values_inspected']==0 and close['numerical_stage_authorized'] is False)
    free=shutil.disk_usage(OWN).free
    check(checks,'Free space at least10GiB', free>=10737418240, free)
    out={'schema':'source-bound-before-values-oxygenation-review-validation/1','status':'PASS','checks':checks,'owner_selected_exports':bindings,'primary_bindings':originals,'new_raw_bytes_retained_by_reviewer':0,'free_bytes':free,'scope':'Export hashes plus independent selected physical methods/cohort identity/table headers/subjectIDs only. No per-case uptake, staining, oxygen, gene or prognostic values extracted. Does not certify global clinical source coverage, raw portability, numerical validity or publication clearance.'}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'PASS','checks':len(checks),'owner_exports':len(bindings),'original_bindings':len(originals),'free_bytes':free}))

if __name__=='__main__': main()
