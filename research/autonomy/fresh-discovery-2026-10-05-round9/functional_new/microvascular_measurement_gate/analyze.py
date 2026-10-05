#!/usr/bin/env python3
"""Verify frozen vascular source gate without inspecting outcome values/images."""
from pathlib import Path
import argparse, hashlib, json, re, xml.etree.ElementTree as E

def digest(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def read(f): return json.loads(f.read_text())
def main():
    a=argparse.ArgumentParser();a.add_argument('--packet',type=Path,default=Path(__file__).resolve().parent);opts=a.parse_args();p=opts.packet
    checks=[]
    for row in read(p/'PORTABILITY.json')['local_raw']+read(p/'PORTABILITY.json')['shared_raw']:
        f=Path(row['path']);f=f if f.is_absolute() else p/f
        checks.append({'check':'source hash','file':str(f),'pass':f.is_file() and digest(f)==row['sha256']})
    for z in read(p/'COMPLETE-HISTOLOGY-ROSTERS.json'):
        f=Path('/workspace/emc-r6-radiotherapy/research/autonomy/fresh-discovery-2026-10-05-round9/endocrine/diffusion_mri_gate/raw-cache')/z['source'] if z['source']=='PMC11717864.xml' else p/'raw-cache'/z['source']
        r=E.parse(f).getroot();t=r.find(".//table-wrap[@id='%s']"%z['table']);rows=[]
        for tr in t.findall('.//tbody/tr'):
            cells=[' '.join(''.join(x.itertext()).split()) for x in tr.findall('./td')]
            if cells:rows.append({'cells':cells})
        checks.append({'check':'complete histology rows exactly reproduce','source':z['source'],'pass':rows==z['full_histology_rows']})
        if z['source']=='PMC11717864.xml':
            counts=[int(re.search(r'n\s*=\s*(\d+)',c).group(1)) for row in rows for c in row['cells'] if re.search(r'n\s*=\s*\d+',c)]
            # Three parent categories (LPS15/adipocytic4/vascular5) include separately counted children.
            checks.append({'check':'165macrocount accountability with24nested subtypecounts removed','pass':sum(counts)-24==165,'source_total_with_nested':sum(counts)})
            checks.append({'check':'two explicitly labelled EMC cases only','pass':sum('Extraskeletal myxoid chondrosarcoma (n = 2)' in c for row in rows for c in row['cells'])==1})
        else:
            counts=[]
            for row in rows:
                for c in row['cells'][1:]:counts.extend(int(x) for x in re.findall(r'n\s*=\s*(\d+)',c))
            checks.append({'check':'92full histology counts','pass':sum(counts)==92,'sum':sum(counts)})
    sc=read(p/'EVALUATED-ABSTRACT-ASSAY-GATES.json')
    checks.append({'check':'18scoped metadata-abstract evaluations not whole-catalogue review','pass':len(sc['records'])==18})
    out={'scope':'Source/eligibility/assay prior-value verification only. No ADC/perfusion/MVD biological outcomes inspected or computed.','checks':checks,'passed':all(x['pass'] for x in checks)}
    print(json.dumps(out,indent=2));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
