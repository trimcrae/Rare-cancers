import pathlib,re,csv,json,hashlib,datetime
D=pathlib.Path(__file__).parent; S=D.parent/'fusion-partial-benchmark-2026-09-05'
def rc(x): return x.translate(str.maketrans('ACGT','TGCA'))[::-1]
def sites(s,q): return [i+1 for i in range(len(s)-len(q)+1) if s[i:i+len(q)]==q]
def parse(p):
 t=p.read_text(); version=re.search(r'^VERSION\s+(\S+)',t,re.M)[1]; seq=re.sub('[^acgt]','',t.split('ORIGIN')[1].split('//')[0]).upper(); length=int(re.search(r'^LOCUS\s+\S+\s+(\d+)',t,re.M)[1]); assert len(seq)==length; return version,seq
refs=dict(parse(p) for p in (D/'inputs').glob('*.gb'))
junctions={'B4N':{'left':'CTCTGACAGCGAAGACTCCGAAACAG','right':'CATCTGCATTGCCGGGACCGGATATGAG','source':'main Fig.2A'},'SS':{'left':'CCAGCAGAGGCCTTATGGATATGACCAG','right':'ATCATGCCCAAGAAGCCAGCAGAGGAAGGAAA','source':'S6 Fig.A'}}
for j in junctions.values():j['boundary_after_nt']=len(j['left']);j['sequence']=j['left']+j['right'];j['verification']='manual transcription of colored boundary, visually inspected primary figure'
(D/'junctions.json').write_text(json.dumps(junctions,indent=2))
b=refs['NM_058243.2'];n=refs['NM_001284292.2']; left=junctions['B4N']['left'];right=junctions['B4N']['right'];print('boundary flanks',sites(b,left),sites(n,right))
a=sites(b,left);z=sites(n,right); assert len(a)==len(z)==1
cut=a[0]-1+len(left); start=z[0]-1
fusion=b[:cut]+n[start:]; assert fusion[cut-len(left):cut+len(right)]==left+right
seqs={**refs,'B4N_reconstructed':fusion}
(D/'references.fasta').write_text(''.join('>'+k+'\n'+v+'\n' for k,v in seqs.items()))
primers={'wild_BRD4':['AAAAGGGAATAGTGCCGTGGAG','AGGAACTGACTTTGGTTGGTGG'],'wild_NUTM1':['CTTCCAGACAGCCACAGTTAGT','TCAGAAGTTGGTGGGAGAAAGG'],'BRD4_NUTM1':['GACAGCGAAGACTCCGAAAC','GCACTAGGTTTCATGCTCATATCC'],'wild_SS18':['GTAGATGCTTGATTGTTTTGGTCTC','GTGCTTTGTCTTCCCCTCAC'],'SS18_SSX1':['GTCCTCAGTATCCTAACTACCCACA','GGTGCAGTTGTTTCCCATCG']}
assays=[]
for name,(f,r) in primers.items():
 if 'SS' in name:
  assays.append(dict(assay=name,forward_5to3=f,reverse_5to3=r,status='unverified: no SS18/SSX1 transcript version accession in inspected primary material',templates=None));continue
 templates=[]
 for key,seq in seqs.items():
  fs=sites(seq,f);rs=sites(seq,rc(r));amps=[{'start':x,'end':y+len(r)-1,'length_bp':y+len(r)-x,'sequence':seq[x-1:y+len(r)-1]} for x in fs for y in rs if y>=x+len(f)]
  templates.append(dict(template=key,forward_sites_1based=fs,reverse_binding_sites_1based=rs,exact_amplicons=amps))
 assays.append(dict(assay=name,forward_5to3=f,reverse_5to3=r,status='exact sequence prediction only; mismatched priming not excluded',templates=templates))
(D/'primer-mappings.json').write_text(json.dumps(assays,indent=2))
outs=list(csv.DictReader((S/'outcomes.csv').open())); designs=list(csv.DictReader((S/'designs.csv').open()));rows=[]
for d in designs:
 core=d['sense_core_5to3'].replace('U','T');anti=d['antisense_core_5to3'].replace('U','T');assert len(core)==19 and rc(core)==anti
 j=junctions[d['target']]; hits=sites(j['sequence'],core); assert len(hits)==1; p=hits[0]; l=j['boundary_after_nt']-p+1;assert 0<l<19
 row={'design_id':d['design_id'],'target':d['target'],'sense_core_DNA_5to3':core,'antisense_core_DNA_5to3':anti,'sense_position_figure_1based':p,'sense_end_figure_1based':p+18,'left_parent_nt':l,'right_parent_nt':19-l,'crosses_reported_junction':True,'sense_orientation':'plus relative to fusion mRNA','antisense_orientation':'reverse complement, binds plus fusion target','parent_reference_status':'verified article references + S3 version sensitivity' if d['target']=='B4N' else 'unverified: primary reference versions not specified','parent_matches':None,'fusion_full_start':None,'outcomes':[o for o in outs if o['design_id']==d['design_id']]}
 if d['target']=='B4N':
  row['parent_matches']={key:{'sense_exact_sites':sites(seq,core),'antisense_same_string_sites':sites(seq,anti)} for key,seq in refs.items()};row['fusion_full_start']=sites(fusion,core);assert len(row['fusion_full_start'])==1
 rows.append(row)
assert len(rows)==31 and len(outs)==93
(D/'design-mappings-and-outcomes.json').write_text(json.dumps(rows,indent=2))
flat=[{k:r[k] for k in ['design_id','target','sense_core_DNA_5to3','antisense_core_DNA_5to3','sense_position_figure_1based','sense_end_figure_1based','left_parent_nt','right_parent_nt','crosses_reported_junction','parent_reference_status']} for r in rows]
with (D/'design-mappings.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=flat[0]);w.writeheader();w.writerows(flat)
summary={'n_designs':31,'n_cross_junction':31,'n_B4N_full_fusion_matches':15,'B4N_boundary_parent_coordinate':cut,'NUTM1_start_parent_coordinate':start+1,'fusion_reconstruction':'NM_058243.2:1..'+str(cut)+' + NM_001284292.2:'+str(start+1)+'..'+str(len(n)),'parent_full_match_designs':[r['design_id'] for r in rows if r['parent_matches'] and any(v['sense_exact_sites'] or v['antisense_same_string_sites'] for v in r['parent_matches'].values())],'SS_full_reference_status':'unverified; all16 match displayed junction but no full-parent verdict','n_outcome_rows_joined':sum(len(r['outcomes']) for r in rows),'n_uncensored_measured_parent_means':sum(o['endpoint']=='measured_parent' and bool(o['relative_expression_mean']) for o in outs),'inputs':{str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'designs.csv',S/'outcomes.csv',S/'inputs/lee2023.xml',S/'inputs/input-manifest.json']}}
(D/'checks.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print(json.dumps([x for x in assays if x['assay']=='wild_BRD4'],indent=2));print(json.dumps(rows[14],indent=2))

