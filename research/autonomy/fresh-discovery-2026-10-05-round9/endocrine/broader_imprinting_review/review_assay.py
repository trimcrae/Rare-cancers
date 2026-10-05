#!/usr/bin/env python3
"""Independent source-byte/primer/annotation check; never reads DNAm matrices."""
import argparse, csv, gzip, hashlib, itertools, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path('/workspace/emc-r6-challenge/research/autonomy/fresh-discovery-2026-10-05-round9/imprinting')
IUPAC = {'A':'A','C':'C','G':'G','T':'T','R':'AG','Y':'CT'}
COMPLEMENT = str.maketrans('ACGTRY','TGCAYR')
PAIRS = {
 'HCC2012_IG1': ['ATTATTGAATTGGGTTTGTTAGTAG','CAAAACAACTCAAATCCTTTATAAC'],
 'HCC2012_IG2': ['TAGYGATTTGTTAATTGYGAGTG','CRAATCCATTATAACCAATTACAATACCAC'],
 'OS2016_IG1_outer': ['ATGTTAATTATTTTTTGGATAAGAG','AATCAAAACAACTCAAATCCTTTA'],
 'OS2016_IG2_outer': ['GTTAAGAGTTTGTGGATTTGTGAGAAATG','GTAAAAATGAGGAAAAGGGATAAAATGAG'],
 'OS2016_IG2_inner_R_only': ['CATTATAACCAATTACAATACCACA'],
 'iPSC2022_IG_ASMM': ['AGTTTTATGTTAAGATGTTAATTATTTTTTGGA','ACCAAAAAACCTAACAAATCAAAACA']
}

def digest(path):
 return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
 gate=ROOT/'broader_region_gate';sources=ROOT/'sources'
 freeze=json.loads((gate/'FREEZE.json').read_text());decision=json.loads((gate/'SOURCE-ASSAY-VALUE-DECISION.json').read_text())
 exported={}
 for name,want in freeze['files'].items():
  actual=digest(gate/name);assert actual==want,(name,actual,want);exported[name]=actual
 amendment=freeze['scope_amendment'];assert digest(gate/amendment['path'])['sha256']==amendment['sha256']
 caches={}
 for source in decision['sources']:
  actual=digest(Path(source['local_cache']));assert actual=={k:source[k] for k in ('sha256','bytes')},source['path'];caches[source['path']]=actual
 transforms=[]
 for transform in decision['archive_transforms']:
  with zipfile.ZipFile(gate/transform['archive']) as z: body=z.read(transform['member'])
  derived=(gate/transform['derived']).read_bytes();assert body==derived
  transforms.append({'member':transform['member'],'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'exact_member_match':True})
 # Verify actual assay names and F/R sequences from primary supplements.
 hcc=(sources/'HCC_DMR_primers.doc').read_bytes().decode('latin1')
 for label,name in [('IG-DMR (1)','HCC2012_IG1'),('IG-DMR (2)','HCC2012_IG2')]:
  assert label+'\x07'+PAIRS[name][0]+'\x07'+PAIRS[name][1]+'\x07' in hcc
 os=(sources/'OS_DMR_supp.txt').read_text();os=os[os.index('Table S2:'):os.index('Supplementary Table S3:')]
 for sequence in PAIRS['OS2016_IG1_outer']+PAIRS['OS2016_IG2_outer']+PAIRS['OS2016_IG2_inner_R_only']:assert sequence in os
 assert 'Universal–bio' in os and 'GGGACACCGCTGATCGTTTAAGTTGTTAGAGGTTTATAGTTGTTTAT' in os
 ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(sources/'human_iPSC_ASMM_primers.xlsx') as z:
  st=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
  rows=[]
  for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:row',ns):
   cells=[]
   for cell in row.findall('s:c',ns):
    v=cell.find('s:v',ns);v=v.text if v is not None else '';cells.append(st[int(v)] if cell.get('t')=='s' and v else v)
   rows.append(cells)
  ix=next(i for i,row in enumerate(rows) if any('14q32' in c and 'IG-DMR' in c for c in row));ipr=rows[ix:ix+2]
  assert PAIRS['iPSC2022_IG_ASMM'][0] in ipr[0][1] and PAIRS['iPSC2022_IG_ASMM'][1] in ipr[1][1]
  assert 'M' in ipr[0][2] and 'UM' in ipr[1][2]
 reference=json.loads((sources/'chr14_hg38_DMR_reference.json').read_text());dna=reference['dna'].upper();base=reference['start']
 assert reference['genome']=='hg38' and reference['chrom']=='chr14' and len(dna)==75000
 expected=json.loads((gate/'CONVERTED-PRIMER-ASSAY-GEOMETRY.json').read_text());geometry={}
 for name,primers in PAIRS.items():
  obs=[]
  for primer in primers:
   hits=[]
   for orientation,p in [('direct',primer),('reverse_complement',primer.translate(COMPLEMENT)[::-1])]:
    variants=[''.join(v) for v in itertools.product(*(IUPAC[x] for x in p))]
    for mode,from_base,to_base in [('C_to_T','C','T'),('G_to_A','G','A')]:
     query=sorted({v.replace(from_base,to_base) for v in variants});ref=dna.replace(from_base,to_base)
     starts=set()
     for v in query: starts.update(m.start() for m in re.finditer('(?='+v+')',ref))
     for start in sorted(starts):hits.append({'start':base+start,'end':base+start+len(primer),'orientation':orientation,'conversion':mode})
   assert hits==expected['primary_candidates'][name]['primers'][len(obs)]['placements'],name
   obs.append({'primer':primer,'placements':hits})
  interval=None
  if len(obs)==2 and all(len(p['placements'])==1 for p in obs):
   assert obs[0]['placements'][0]['orientation']=='direct' and obs[1]['placements'][0]['orientation']=='reverse_complement'
   interval={'start':min(p['placements'][0]['start'] for p in obs),'end':max(p['placements'][0]['end'] for p in obs)}
  assert interval==expected['primary_candidates'][name]['paired_envelope'];geometry[name]={'primers':obs,'paired_envelope':interval}
 arrays={}
 for platform in ['HM450','EPIC']:
  selected={name:([] if v['paired_envelope'] else None) for name,v in geometry.items()};nearby=[];count=0;ids=set()
  with gzip.open(sources/(platform+'.ordering.tsv.gz'),'rt') as a,gzip.open(sources/(platform+'.hg38.coord.tsv.gz'),'rt') as b:
   aa=csv.DictReader(a,delimiter='\t');bb=csv.DictReader(b,delimiter='\t')
   for order,coordinate in itertools.zip_longest(aa,bb):
    assert order is not None and coordinate is not None;count+=1;assert order['Probe_ID'] not in ids;ids.add(order['Probe_ID'])
    if coordinate['CpG_chrm']!='chr14':continue
    position=int(coordinate['CpG_beg']);item={'Probe_ID':order['Probe_ID'],'start':position,'mapQ':int(coordinate['mapQ'])}
    for name,v in geometry.items():
     bounds=v['paired_envelope']
     if bounds and bounds['start']<=position<bounds['end']:selected[name].append(item)
    if order['Probe_ID'] in ['cg27281850','cg06442344']:nearby.append(item)
  assert selected==expected['arrays'][platform]['complete_envelope_probes'] and count==expected['arrays'][platform]['rows']
  arrays[platform]={'rows':count,'unique_ids':len(ids),'exact_envelope_probes':selected,'nearby_unaccepted_EPIC_pair':nearby}
 coverage=json.loads((ROOT/'COVERAGE.json').read_text());emc=coverage['all_GSE140686_EMC'];assert len(emc)==10
 from collections import Counter
 result={'schema':'emc-r9-independent-broader-IG-source-annotation-audit/1','target_freeze':digest(gate/'FREEZE.json'),'verified_exports':exported,'verified_cache_inputs':caches,'archive_members':transforms,'source_named_F_R_matches':True,'iPSC_source_F_R_M_UM_rows':ipr,'geometry':geometry,'arrays':arrays,'all_EMC_conditions':[{'ID':v['ID'],'GSM':v['GSM'],'platform':v['platform'],'methylation_values_status':v['methylation_values']} for v in emc],'reference_EMC_platform_counts':dict(Counter(v['platform'] for v in emc)),'potential_controls':len(coverage['all_fixed_primary_FFPE_control_inventory']),'Case21_source_limits':coverage['Case21'],'values_read':False,'errors':[]}
 Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'exported_files':len(exported),'cache_inputs':len(caches),'complete_pairs':sum(v['paired_envelope'] is not None for v in geometry.values()),'reference_EMC':len(emc),'controls':result['potential_controls'],'errors':[]}))

if __name__=='__main__':main()
