#!/usr/bin/env python3
"""Physical-region/methylation methods only; no array overlay or beta input."""
import argparse, hashlib, json
from pathlib import Path
from xml.etree import ElementTree as ET

OWNER=Path('/workspace/emc-r6-challenge/research/autonomy/fresh-discovery-2026-10-05-round9/imprinting')
EXPECTED={
 'PMC2887472.xml':'60d8c04e5915852231de92a88da0cef8030d7e58c74d9f7e33cf763abe5d8596',
 'PMC6407230.xml':'b4a07b03c8246d3b860db50d37d57b64e2bccb108668dd8f21008ea5f2fc255c',
 'PMC4101709.xml':'721b4f6eb27db8dc67f8624cf71a3505516d3a3ee9c99f3d6eaab8895c5dcbe6'
}
SECTIONS={
 'PMC2887472.xml':"./body/sec[@id='s4']/sec[@id='s4e']",
 'PMC6407230.xml':"./body/sec[@id='Sec2']/sec[@id='Sec6']",
 'PMC4101709.xml':"./body/sec[@id='sec6']/sec[@id='sec13']"
}

def binding(path):
 b=path.read_bytes();return {'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
 plan=OWNER/'functional_region_gate/PLAN.json';assert binding(plan)['sha256']=='e9cc292acf8292eea587cc5f58663ed6b41e392477c49e3d386fad0976cfed13'
 sources={};methods={}
 for name,want in EXPECTED.items():
  path=OWNER/'sources'/name;meta=binding(path);assert meta['sha256']==want;sources[name]=meta
  root=ET.parse(path).getroot();section=root.find(SECTIONS[name]);assert section is not None
  paragraphs=[' '.join(''.join(p.itertext()).split()) for p in section.findall('p')]
  methods[name]={'section_id':section.get('id'),'paragraphs':paragraphs}
 assert 'lack of CpG dinucleotides within the primer sequences' in ' '.join(methods['PMC2887472.xml']['paragraphs'])
 assert 'but not the MEG3/DLK1:IG-DMR' in ' '.join(methods['PMC6407230.xml']['paragraphs'])
 assert 'NT_026437.12' in ' '.join(methods['PMC4101709.xml']['paragraphs'])
 assert '909 bp' in ' '.join(methods['PMC4101709.xml']['paragraphs'])
 # Verify the named physical components without reading patient/structural analyses.
 p2010=ET.parse(OWNER/'sources/PMC2887472.xml').getroot()
 component_definition='the IG-DMR (CG4 and CG6) and the MEG3-DMR (CG7)'
 assert any(component_definition in ''.join(p.itertext()) for p in p2010.findall('.//p'))
 receiptfiles=['PRIMARY-FUNCTIONAL-REGION-RECEIPTS.json','ORIGINAL-2007-RECEIPT.json','HUMAN-ORIGINAL-2000-RECEIPT.json','HUMAN-ORIGINAL-2000-FULL-RECEIPT.json','HUMAN-ORIGINAL-2000-PDF-RECEIPT.json']
 receipts={n:binding(OWNER/'functional_region_gate'/n) for n in receiptfiles if (OWNER/'functional_region_gate'/n).exists()}
 failed=OWNER/'sources/human_IG_2007.pdf';failed_binding=None
 if failed.exists():
  failed_binding=binding(failed);assert not failed.read_bytes().startswith(b'%PDF-');failed_binding['is_pdf']=False
 oldreview=Path(__file__).resolve().parents[1]/'broader_imprinting_review/FREEZE.json'
 assert binding(oldreview)['sha256']=='fbc833c2a85b147a5dc7f4b9e85ec7e5462a3166de744e7d456b06e19b47954d'
 coverage=OWNER/'COVERAGE.json';cov=json.loads(coverage.read_text())
 assert len(cov['all_GSE140686_EMC'])==10 and len(cov['all_fixed_primary_FFPE_control_inventory'])==62
 region=OWNER/'functional_region_gate/REGION-FROZEN.json';assert binding(region)['sha256']=='6f24b4b21b1fc61888adba2b1d5dd5332cbbf6103be91392ab5c6f73bb7ea38f'
 reg=json.loads(region.read_text());assert all(reg[k] is None for k in ['chosen_region','assembly','source_boundaries','probe_count_whole_region']);assert not reg['fresh_probe_overlay_performed']
 nc=OWNER/'functional_region_gate/COVERAGE.json';newcov=json.loads(nc.read_text())
 for newkey,oldkey in [('all_GSE140686_EMC','all_GSE140686_EMC'),('all_fixed_primary_FFPE_controls','all_fixed_primary_FFPE_control_inventory')]:
  assert len(newcov[newkey])==len(cov[oldkey]);assert [v['ID'] for v in newcov[newkey]]==[v['ID'] for v in cov[oldkey]]
  for new,old in zip(newcov[newkey],cov[oldkey]):
   for k in ['GSM','diagnosis','material','manifestation','platform','IDAT','slide','supplier','batch']:
    assert new.get(k)==old.get(k),(new['ID'],k)
 assert newcov['Case21']==cov['Case21']
 assert newcov['validation54']==cov['validation54']
 newmeta=OWNER/'sources/human_IG_original_2000.json';metadata_binding=binding(newmeta) if newmeta.exists() else None
 final_bindings={n:binding(OWNER/'functional_region_gate'/n) for n in ['REGION-FROZEN.json','PRIMARY-DEFINITION-EVIDENCE.json','DECISION.json','COVERAGE.json']}
 wrapper=OWNER/'functional_region_gate/FREEZE.json';assert binding(wrapper)['sha256']=='508bb49850ebbf2f268406197f794aef99b785f0a59fc157c6c333388d441f70'
 wf=json.loads(wrapper.read_text());checked_exports=[]
 for f in wf['files']:
  actual=binding(OWNER/'functional_region_gate'/f['path']);assert actual['sha256']==f['sha256'] and actual['bytes']==f['bytes'];checked_exports.append(f)
 raw=[]
 for item in json.loads((OWNER/'functional_region_gate/PRIMARY-DEFINITION-EVIDENCE.json').read_text())['sources']:
  f=item['binding'];actual=binding(OWNER/f['path']);assert actual['sha256']==f['sha256'] and actual['bytes']==f['bytes'];raw.append(actual)
 output={'schema':'emc-r9-independent-human-whole-region-primary-method-audit/1','owner_plan':binding(plan),'retained_primary_cache_inputs':sources,'methylation_methods_only':methods,'physical_components_2010':component_definition,'primary_whole_interval_authenticated_by_this_audit':None,'failed_2007_pdf_original':failed_binding,'original_2000_metadata_binding':metadata_binding,'owner_access_receipt_bindings':receipts,'prior_exact_envelope_review_reused':binding(oldreview),'native_condition_inventory_binding':binding(coverage),'new_region_science_bindings':final_bindings,'new_region_disposition_null_bounds_not_zero_coverage':True,'owner_final_freeze':binding(wrapper),'checked_frozen_owner_exports':checked_exports,'checked_final_raw_source_bindings':raw,'metadata_field_correspondence_checks':648,'all10_native_conditions':[{'ID':v['ID'],'GSM':v['GSM'],'platform':v['platform'],'joint_assay_status':v['joint_assay_status'],'methylation_values_status':v['methylation_values']} for v in cov['all_GSE140686_EMC']],'potential_fixed_controls':62,'new_native_inventory_and_Case21_matches':True,'Case21_source_independence_limits':cov['Case21'],'fresh_probe_overlays_read_or_computed':False,'methylation_values_read':False,'structural_sections_in_script':'Explicitly excluded; only selected methylation sections are traversed for source text. No patient-genomic mechanism calculation or interpretation.','errors':[]}
 Path(a.output).write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'primary_sources':3,'native_conditions':10,'controls':62,'whole_boundary':None,'overlay':False,'values':False,'errors':[]}))

if __name__=='__main__':main()
