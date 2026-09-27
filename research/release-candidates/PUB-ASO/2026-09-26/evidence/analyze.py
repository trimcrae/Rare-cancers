"""Offline, standard-library analysis of pinned primary sources and reused inputs.

Sequences are 5'-3' DNA alphabet representations of RNA. No cleavage inference.
Run: python analyze.py. Inputs are hashed; no network or repository writes.
"""
import csv, hashlib, json, pathlib, re

ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(name,value):(OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def rc(s):return s.translate(str.maketrans('ACGT','TGCA'))[::-1]
def table(name,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader()
        for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})

for row in load(ROOT/'input-manifest.json'):
    assert hashlib.sha256((ROOT/row['copy']).read_bytes()).hexdigest()==row['sha256'],row['copy']

parents=load(ROOT/'inputs/emc-construct-inputs.json')['genes']
premrna=load(ROOT/'inputs/aso-premrna-sequences.json')['genes']
normal={g:''.join(v['sequence'][a:b+1] for a,b in v['exon_spans_0based_inclusive']) for g,v in premrna.items()}
assert len(normal)==6
for g,seq in normal.items():assert seq==parents[g]['cdna']
atlas={}
for suffix in ['', '-noncoding-acceptor','-taf15intron2','-ewsr1intron2']:
    for panel in load(ROOT/f'inputs/nr4a3-fusion-junction-atlas{suffix}.json')['panels']:
        atlas[panel['junction_label']]=panel
cryptic=load(ROOT/'inputs/nr4a3-intron2-cryptic-exon.json')['resolved_cryptic_exon']['sequence']

def junction(label,flank=30):
    panel=atlas[label]; donor=parents[panel['donor_symbol']]
    cut=donor['exons'][panel['donor_exon_end']-1]['cdna_end_exclusive']
    if isinstance(panel['acceptor_exon_start'],int):
        acc=parents['NR4A3']['exons'][panel['acceptor_exon_start']-1]['cdna_start_0based']
        right=parents['NR4A3']['cdna'][acc:acc+flank]
    else:right=cryptic[:flank]
    return donor['cdna'][cut-flank:cut],right

# Resolve the actual proteins shown in Figure 4, without using exon labels alone.
fig=load(ROOT/'figure-observations.json');crosswalk=[];displayed={}
for gene,ensp in [('EWSR1','ENSP00000400142'),('NR4A3','ENSP00000333122'),('TAF15','ENSP00000466950')]:
    protein=load(ROOT/f'sources/{ensp}-lookup.json');enst=protein['Parent']
    model=load(ROOT/f'sources/{enst}-grch37.json');dna=load(ROOT/f'sources/{enst}-grch37-cdna.json')
    assert model['assembly_name']=='GRCh37' and model['strand']==1 and dna['version']==model['version']
    assert model['Translation']['id']==ensp
    assert sum(e['end']-e['start']+1 for e in model['Exon'])==len(dna['seq'])
    displayed[gene]=(model,dna['seq'])
    for rank,e in enumerate(model['Exon'],1):
        crosswalk.append(dict(gene=gene,protein=ensp+'.'+str(protein['version']),transcript=enst+'.'+str(model['version']),assembly='GRCh37',exon_rank_1based=rank,exon_accession=e['id']+'.'+str(e['version']),start_1based=e['start'],end_1based_inclusive=e['end']))
table('displayed-transcript-exons.tsv',crosswalk)
em,es=displayed['EWSR1'];nm,ns=displayed['NR4A3'];tm,ts=displayed['TAF15']
obs=fig['USZ20-EMC1'];e=em['Exon'][obs['first_exon_label']-1];n=nm['Exon'][obs['second_exon_label']-1]
assert e['end']==obs['first_position'] and n['start']==obs['second_position']
ec=sum(x['end']-x['start']+1 for x in em['Exon'][:13]);nc=nm['Exon'][0]['end']-nm['Exon'][0]['start']+1
left,right=es[ec-30:ec],ns[nc:nc+30]
catalogue_matches=[lab for lab in atlas if junction(lab)==(left,right)]
assert catalogue_matches==['EWSR1_e12__NR4A3_e3'],catalogue_matches
# Independent genomic retrieval and RefSeq annotation corroboration.
genome_left=load(ROOT/'sources/hg19-chr22-29692328-29692388.json')['dna'][:30].upper()
genome_right=load(ROOT/'sources/hg19-chr9-102590292-102590417.json')['dna'][30:60].upper()
assert (left,right)==(genome_left,genome_right)
refseq=[]
for gene,acc,rank,boundary in [('EWSR1','NM_005243.4',12,e['end']),('NR4A3','NM_006981.4',3,n['start'])]:
    record=next(r for r in load(ROOT/f'sources/{gene}-hg19-RefSeq.json')['ncbiRefSeqCurated'] if r['name']==acc)
    starts=list(map(int,record['exonStarts'].rstrip(',').split(',')));ends=list(map(int,record['exonEnds'].rstrip(',').split(',')))
    assert (ends[rank-1] if gene=='EWSR1' else starts[rank-1]+1)==boundary
    refseq.append(dict(gene=gene,accession=acc,exon=rank,start_1based=starts[rank-1]+1,end_1based=ends[rank-1]))
usz22=fig['USZ22-EMC2']; intervals=[]
for gene,model,rank,coords in [('NR4A3',nm,2,usz22['first_interval']),('TAF15',tm,6,usz22['second_interval'])]:
    ex=model['Exon'][rank-1];assert ex['start']<coords[0]<=coords[1]<ex['end']
    intervals.append(dict(gene=gene,interval=coords,exon_start=ex['start'],exon_end=ex['end'],inclusive_width=coords[1]-coords[0]+1,offsets_1based_in_exon=[x-ex['start']+1 for x in coords]))
dump('model-crosswalk.json',dict(USZ20=dict(evidence_class='reference_reconstruction_from_reported_coordinates',reference_genome_build_inferred='GRCh37/hg19',coordinate_convention_inferred='1-based terminal exon bases',reference_junction_30_plus_30=left+'|'+right,catalogue_matches=catalogue_matches,refseq_corroboration=refseq,unresolved='patient consensus; variants/insertions; original caller conventions; build not explicitly stated'),USZ22=dict(evidence_class='unresolved_intervals',intervals=intervals,exact_junction=None)))

# Deposits: compare the deposited sequence itself with candidate 16+16 anchors.
records={}
for entry in (ROOT/'sources/documented-deposits.gb').read_text().split('//'):
    acc=re.search(r'^VERSION\s+(\S+)',entry,re.M)
    if not acc:continue
    seq=''.join(re.findall('[acgtun]+',entry.split('ORIGIN',1)[1].lower())).upper().replace('U','T')
    records[acc.group(1)]=(seq,entry)
expected={'AF162670.1':'TAF15_e6__NR4A3_e3','AJ243810.1':'TAF15_e6__NR4A3_e3','AJ245932.1':'TAF15_e6__NR4A3_e3','AY532911.1':'TFG_e7__NR4A3_e3','AF289510.1':'TCF12_e5__NR4A3_e3','AF524261.1':'EWSR1_e10__NR4A3_intron2crypticExon','S81242.1':'EWSR1_e7__NR4A3_e2'}
junction_rows=[]
for acc,label in expected.items():
    seq,entry=records[acc];l,r=junction(label,16);positions=[i for i in range(len(seq)-31) if seq[i:i+32]==l+r]
    assert len(positions)==1,(acc,label,positions)
    seam=positions[0]+16
    pmids=re.findall(r'^\s+PUBMED\s+(\d+)',entry,re.M)
    junction_rows.append(dict(evidence_id=acc,system='deposited EMC-linked fusion mRNA; see original record for specimen provenance',evidence_class='directly_reported_deposit_sequence',source_url=f'https://www.ncbi.nlm.nih.gov/nuccore/{acc}',accession_version=acc,pubmed=pmids,catalogue_junction=label,donor_end_in_deposit_1based=seam,acceptor_start_in_deposit_1based=seam+1,junction_16_plus_16=l+'|'+r,new_in_this_investigation=False,ambiguity='not an independent-patient count; S81242 is GenBank transcription from print' if acc=='S81242.1' else 'deposit metadata does not establish independent patient count'))
junction_rows.extend([
dict(evidence_id='USZ20-EMC1',system='patient-derived EMC model',evidence_class='reference_reconstruction_from_reported_coordinates',source_url='https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/',accession_version='ENST00000414183.2; ENST00000330847.1 (GRCh37 lookup)',catalogue_junction=catalogue_matches[0],junction_16_plus_16=left[-16:]+'|'+right[:16],new_in_this_investigation=True,ambiguity='reference sequence, not deposited patient consensus; genome build and coordinate convention inferred'),
dict(evidence_id='USZ22-EMC2',system='patient-derived EMC model',evidence_class='unresolved_coordinate_intervals',source_url='https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/',accession_version='ENST00000588240.1; ENST00000330847.1 (GRCh37 lookup)',catalogue_junction='',junction_16_plus_16='',new_in_this_investigation=True,ambiguity='internal exon intervals and reversed displayed gene order; no exact RNA junction assigned'),
])
for system,label in [('Brenca E-N','EWSR1_e12__NR4A3_e3'),('Brenca T-N*','TAF15_e6__NR4A3_e3'),('Brenca T-N','TAF15_e6__NR4A3_intron2crypticExon')]:
    l,r=junction(label,16)
    junction_rows.append(dict(evidence_id=system,system='engineered tBJ/ER construct',evidence_class='previous_reference_model_from_construct_description',source_url='https://pmc.ncbi.nlm.nih.gov/articles/PMC6766969/',accession_version='paper names ENST00000395097.6 for intron convention; exact construct sequence not deposited in the paper',catalogue_junction=label,junction_16_plus_16=l+'|'+r,new_in_this_investigation=False,ambiguity='RNA read evidence evaluated separately; do not transfer construct sequence to Zurich model'))
table('junction-evidence.tsv',junction_rows)

# New comparisons are confined to source-corresponding designs and a label-transfer error control.
selected=sorted(set(expected.values())|{catalogue_matches[0],'TAF15_e6__NR4A3_intron2crypticExon','EWSR1_e13__NR4A3_e2'})
accepted={}
for fname in ['aso-parent-gap-pairing.json','aso-parent-gap-pairing-noncoding-acceptor.json']:
    for r in load(ROOT/'inputs'/fname)['per_design']:accepted[(r['junction'],r['antisense_5to3'])]=r
extended=dict(normal)
for g,(model,seq) in displayed.items():extended[g+':'+model['id']+'.'+str(model['version'])]=seq
figure_corpus=dict(extended)
curated={};acc_gene={r['accession']:r['gene'] for r in load(ROOT/'sources/parent-refseq-accessions.json')}
for entry in (ROOT/'sources/six-parents-curated-RefSeq.gb').read_text().split('//'):
    acc=re.search(r'^VERSION\s+(\S+)',entry,re.M)
    if not acc:continue
    acc=acc.group(1);assert acc in acc_gene
    seq=''.join(re.findall('[acgtun]+',entry.split('ORIGIN',1)[1].lower())).upper().replace('U','T')
    expected_length=int(re.search(r'^LOCUS\s+\S+\s+(\d+) bp',entry,re.M).group(1));assert len(seq)==expected_length
    curated[acc_gene[acc]+':'+acc]=seq
assert len(curated)==len(acc_gene)==68
extended.update(curated)
normal_rows=[dict(reference=k,length_nt=len(s),sha256=hashlib.sha256(s.encode()).hexdigest()) for k,s in extended.items()]
table('normal-reference-manifest.tsv',normal_rows)
with (OUT/'normal-reference-transcripts.fasta').open('w') as f:
    for key,seq in extended.items():f.write('>'+key+'\n'+seq+'\n')

def best(target,corpus):
    winners=[];length=0
    # Exact-substring enumeration from 16 down to 6; only intervals covering all gap bases.
    for size in range(16,5,-1):
        for start in range(0,6):
            stop=start+size
            if stop>16 or stop<11:continue
            seed=target[start:stop]
            for gene,seq in corpus.items():
                pos=seq.find(seed)
                while pos>=0:
                    window_start=pos-start
                    if 0<=window_start<=len(seq)-16:
                        window=seq[window_start:window_start+16]
                        winners.append(dict(transcript=gene,parent_window_start_0based=window_start,parent_window_5to3=window,target_match_start_0based=start,match_length=size,whole_window_matches=sum(a==b for a,b in zip(window,target)),mismatch_positions_1based=[i+1 for i,(a,b) in enumerate(zip(window,target)) if a!=b]))
                    pos=seq.find(seed,pos+1)
        if winners:return size,winners
    return 0,[]

def direct_best(target,corpus):
    value=0
    for seq in corpus.values():
        for start in range(len(seq)-15):
            window=seq[start:start+16]
            if window[5:11]!=target[5:11]:continue
            a,b=5,11
            while a>0 and window[a-1]==target[a-1]:a-=1
            while b<16 and window[b]==target[b]:b+=1
            value=max(value,b-a)
    return value

design_rows=[];hit_rows=[];legacy_checked=0
for label in selected:
    l,r=junction(label,30);context=l+r
    for d in atlas[label]['designs']:
        target=d['target_mRNA_5to3'];aso=d['antisense_5to3'];assert rc(aso)==target
        assert target in context and len(target)==16
        start=context.find(target);donor_bases=30-start;assert 6<=donor_bases<=10
        old=accepted.get((label,aso))
        if old:
            six=old['longest_parent_duplex_bp_through_gap'];legacy_checked+=1
        else:six=best(target,normal)[0]
        full,hits=best(target,extended)
        figure_length=best(target,figure_corpus)[0]
        assert full==direct_best(target,extended)
        assert full>=six
        # Reused longest-run values are checked only for this changed source/isoform subset.
        assert six==best(target,normal)[0]
        exact=[g for g,seq in extended.items() if target in seq]
        row=dict(junction=label,antisense_5to3=aso,target_RNA_DNA_alphabet_5to3=target,donor_bases=donor_bases,acceptor_bases=16-donor_bases,architecture='16nt 5-6-5; proposed chemistry only',legacy_six_parent_longest_gap_spanning_match_bp=six,with_figure_isoforms_longest_match_bp=figure_length,expanded_parent_corpus_longest_match_bp=full,exact_16nt_normal_transcript_matches=exact,legacy_metric_reused=bool(old),control_only=(label=='EWSR1_e13__NR4A3_e2'))
        design_rows.append(row)
        hit_rows.extend(dict(junction=label,antisense_5to3=aso,**hit) for hit in hits)
table('design-comparisons.tsv',design_rows);table('longest-normal-match-locations.tsv',hit_rows)

true_label=catalogue_matches[0];wrong_label='EWSR1_e13__NR4A3_e2';error_rows=[]
true={r['donor_bases']:r for r in design_rows if r['junction']==true_label}
for wrong in [r for r in design_rows if r['junction']==wrong_label]:
    correct=true[wrong['donor_bases']];a=wrong['target_RNA_DNA_alphabet_5to3'];b=correct['target_RNA_DNA_alphabet_5to3']
    error_rows.append(dict(donor_bases=wrong['donor_bases'],reference_reconstructed_design=correct['antisense_5to3'],literal_label_design=wrong['antisense_5to3'],aligned_target_hamming_distance=sum(x!=y for x,y in zip(a,b)),gap_positions_mismatched=sum(a[i]!=b[i] for i in range(5,11)),interpretation='same-register sequence comparison; not a binding/cleavage prediction'))
table('literal-label-error-control.tsv',error_rows)
cutoffs=[]
scientific_rows=[r for r in design_rows if not r['control_only']]
for cutoff in range(6,17):
    cutoffs.append(dict(cutoff_bp=cutoff,n_designs=35,six_parent_designs_at_or_above=sum(r['legacy_six_parent_longest_gap_spanning_match_bp']>=cutoff for r in scientific_rows),expanded_designs_at_or_above=sum(r['expanded_parent_corpus_longest_match_bp']>=cutoff for r in scientific_rows),biological_threshold=False))
table('cutoff-sensitivity.tsv',cutoffs)
normal_corroboration=[]
for entry in (ROOT/'sources/NR4A3-normal-isoform.gb').read_text().split('//'):
    acc=re.search(r'^VERSION\s+(\S+)',entry,re.M)
    if not acc:continue
    seq=''.join(re.findall('[acgtun]+',entry.split('ORIGIN',1)[1].lower())).upper()
    motif='AAATGTGGATATGCCC';pos=seq.find(motif);assert pos>=0
    normal_corroboration.append(dict(accession=acc.group(1),motif=motif,start_1based=pos+1,end_1based=pos+len(motif)))
dump('normal-isoform-corroboration.json',normal_corroboration)
dump('summary.json',dict(documented_deposit_records=len(expected),distinct_deposit_junctions=len(set(expected.values())),new_patient_model_reference_correspondence=true_label,direct_patient_consensus_recovered=False,unresolved_model='USZ22-EMC2',design_rows=len(design_rows),legacy_subset_metrics_reused=legacy_checked,normal_reference_sequences_original=len(normal),normal_reference_sequences_extended=len(extended),normal_reference_distinct_sequences=len(set(extended.values())),curated_refseq_accessions=len(curated),normal_match_increases=[r for r in design_rows if r['expanded_parent_corpus_longest_match_bp']>r['legacy_six_parent_longest_gap_spanning_match_bp']],USZ20_registers=[r for r in design_rows if r['junction']==true_label],literal_label_control=error_rows,verification='input hashes, protein/transcript links, genomic/RefSeq corroboration, deposit anchors, antisense orientation, two independent matching implementations; all assertions passed'))
print(json.dumps(load(OUT/'summary.json'),indent=2))
