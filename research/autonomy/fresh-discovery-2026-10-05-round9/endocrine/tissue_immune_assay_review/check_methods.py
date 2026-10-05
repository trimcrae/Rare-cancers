#!/usr/bin/env python3
"""Validate retained methods and frozen pre-value plan; no results/count tables."""
import argparse, hashlib, json
from pathlib import Path
from xml.etree import ElementTree as ET

OWNER=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/tissue_immune_gate')
OLD=Path('/workspace/Rare-cancers/research/autonomy')

def binding(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
 plan=OWNER/'PLAN.json';assert binding(plan)['sha256']=='c0e82de204a458dffc355d42a423a585b8ec6702cbaafc36c2ca6a980e9e8db1'
 source=OWNER/'raw-cache/umakoshi2023-primary.xml';assert binding(source)['sha256']=='bd02cbff5ebca3fde9e16993d0a4705b3b631e8a95470de255afbab80cf7217a'
 root=ET.parse(source).getroot();methods={}
 for sec in root.findall('./body/sec'):
  title=sec.find('title')
  if title is None or ''.join(title.itertext())!='Materials and methods':continue
  for sub in sec.findall('sec'):
   if sub.get('id') not in ['Sec3','Sec4','Sec5','Sec6']:continue
   methods[sub.get('id')]={'title':''.join(sub.find('title').itertext()),'paragraphs':[' '.join(''.join(p.itertext()).split()) for p in sub.findall('p')]}
 assert set(methods)=={'Sec3','Sec4','Sec5','Sec6'}
 text=' '.join(p for sec in methods.values() for p in sec['paragraphs'])
 assert 'No patients received preoperative chemotherapy or radiotherapy' in text
 assert 'five representative fields (0.2 mm2)' in text and 'counted manually' in text
 assert all(x in text for x in ['Clone PG-M1','Clone EPR19518','Clone SRA-E5'])
 assert 'CD3' not in text and 'CD8' not in text
 assert 'Both cases involved an atypical lipomatous tumor' in text
 smolle=OWNER/'raw-cache/smolle2021-primary.xml';assert binding(smolle)['sha256']=='a56c0b75a7282a9d7fd02befb88fb8a8de590be576ec13d7697d9c93d37937fd'
 smroot=ET.parse(smolle).getroot();smmethods={}
 for sec in smroot.findall("./body/sec[@id='s0002']/sec[@id='s0002-s2001']/sec"):
  if sec.get('id') not in ['s0002-s2001-s3002','s0002-s2001-s3003','s0002-s2001-s3004']:continue
  smmethods[sec.get('id')]={'title':''.join(sec.find('title').itertext()),'paragraphs':[' '.join(''.join(p.itertext()).split()) for p in sec.findall('p')]}
 smtext=' '.join(p for sec in smmethods.values() for p in sec['paragraphs'])
 assert 'CD3+, CD8+' in smtext and 'DAPI nucleus staining' in smtext and 'percentages of the total number of cells' in smtext
 assert 'combined for cores of the same patient' in smtext and 'CD163' not in smtext
 oldsource=OLD/'fresh-discovery-2026-10-04/microenvironment/dancsok-supplement-extracted.json'
 old=json.loads(oldsource.read_text())['Supplemental Material final 2019-12-5.docx']
 paragraphs=old['paragraphs']
 if isinstance(paragraphs,str):paragraphs=paragraphs.splitlines()
 selected=[p for p in paragraphs if 'mean scores of duplicate tissue microarray cores' in p or 'Figure S1.' in p]
 assert len(selected)==2 and any('adding 1 to all values' in p for p in selected)
 tc=Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round9/clinical_measurements/tissue_immune_challenge/source-cache')
 tpdf=tc/'dancsok2019.pdf';ttext=tc/'dancsok2019-text.txt'
 assert binding(tpdf)['sha256']=='5ae254dc77584ba11d265c530b45f610e69dff957d23f67f22de2c2bc97a69b4'
 assert binding(ttext)['sha256']=='1450b4093ef6b3f0c04e1ff3cd269504f6f1caf3f1568a5cdf5daa6b28126396'
 lines=ttext.read_text().splitlines();method_excerpt='\n'.join(lines[141:163])
 assert 'hematoxylin-' in method_excerpt and 'mean score from all replicates' in method_excerpt and 'respective core' in method_excerpt
 reusefiles=[OLD/'fresh-discovery-2026-10-04-round3/immune/RESULTS.md',OLD/'fresh-discovery-2026-10-05-round8/microenvironment/REPORT.txt',OLD/'fresh-discovery-2026-10-05-round8/microenvironment/DECISION.json',OLD/'fresh-discovery-2026-10-05-round8/microenvironment/COVERAGE.json']
 result={'schema':'emc-r9-prevalue-tissue-assay-method-source-audit/1','owner_plan':binding(plan),'retained_new_primary_cache_only':binding(source),'new_primary_methods_only':methods,'new_source_matched_T_cell_assay':False,'retained_multiplex_primary_cache_only':binding(smolle),'multiplex_primary_methods_only':smmethods,'multiplex_source_identity':'Generic other-histotype subset unresolved; no EMC eligibility assigned by this reviewer','multiplex_source_CD68_CD3_assay':'Potentially matched phenotype percentages, not absolute density; source patient-core aggregation rule remains unstated','older_extraction_verified_reuse':binding(oldsource),'older_source_scoring_and_ratio_definitions':selected,'older_full_macrophage2020_primary_cache':'Unavailable in current portable checkout; no new full-primary reproduction claimed','recovered_Tcell2019_primary_bindings':[binding(tpdf),binding(ttext)],'Tcell2019_methods_only_excerpt':method_excerpt,'Tcell2019_marker_identity':'Morphological H&E TIL separate from positive-staining CD8/CD4 lymphocytes; no assayed CD3 in inspected methods; published CD68/TIL index cannot be relabelled CD68/CD3','reuse_scope_bindings':[binding(f) for f in reusefiles],'new_EMC_numeric_cell_count_outcomes_inspected':False,'results_tables_read':False,'images_or_downloads':False,'errors':[]}
 Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'methods':len(methods),'matched_T_assay':False,'count_outcomes':False,'errors':[]}))

if __name__=='__main__':main()
