"""Reproducible selected-list prior-art search and source identity audit."""
from pathlib import Path
import json,re,sys,hashlib,collections,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;sys.path.insert(0,str(next(D.glob('xlrd*.whl'))));import xlrd
pat=re.compile(r'\bDLK.?1\b|preadipocyte|fetal antigen|\bPREF.?1\b|delta.like.?(?:protein.)?1|\b8788\b|003836',re.I)
w=xlrd.open_workbook(D/'subramanian2005-suppletable4.xls');hits=[]
for sh in w.sheets():
    for i in range(sh.nrows):
        row=sh.row_values(i)
        if any(pat.search(str(x))for x in row):hits.append({'sheet':sh.name,'row':i+1,'values':row})
fil=E.parse(D/'filion2009.xml');fp=[p for p in fil.iter('p') if pat.search(' '.join(p.itertext()))]
gene=E.parse(D/'dlk1-gene.xml');assert [e.text for e in gene.iter('Gene-ref_locus')]==['DLK1']
bridge=[E.tostring(e,encoding='unicode')for e in gene.iter('Gene-commentary')if e.findtext('Gene-commentary_accession')=='U15981'];assert len(bridge)==1
text=(D/'GSE71119-all-sample-metadata.txt').read_text(encoding='utf8');cases=[]
for b in text.split('^SAMPLE = ')[1:]:
    lines=b.splitlines();fields=collections.defaultdict(list)
    for line in lines:
        if ' = 'in line:
            k,v=line.split(' = ',1);fields[k].append(v)
    cases.append({'gsm':lines[0],'title':fields['!Sample_title'],'source_histology':fields['!Sample_source_name_ch1'],'characteristics':fields['!Sample_characteristics_ch1']})
hist=collections.Counter(x for c in cases for x in c['source_histology']);amb=[c for c in cases if any(h in ['Other','Undifferentiated sarcoma']for h in c['source_histology'])]
out={'Subramanian2005':{'input_sha256':hashlib.sha256((D/'subramanian2005-suppletable4.xls').read_bytes()).hexdigest(),'sheets':[(s.name,s.nrows,s.ncols)for s in w.sheets()],'pattern':pat.pattern,'hits':hits,'limits':'Published selected SAM list only; no-hit is neither absent assay coverage nor low expression. GSE4303 actual mapped measurements evaluated separately.'},'Filion2009':{'DLK1_alias_main_text_matches':[' '.join(p.itertext()) for p in fp],'supplements':'S1/S2 failed retrieval from observed archive paths; remains a source completeness gap, not negative expression.'},'GSE4303_gene_bridge':{'NCBI_gene':8788,'official_symbol':'DLK1','current_gene_U15981_commentary':bridge,'ESTs':'W01204.1 andAA701996.1 each originally described homologous toU15981; clone IDs match originalGPL3290. Not a whole-genome sequence specificity validation.'},'GSE71119':{'n_samples':len(cases),'source_histology_counts':dict(hist),'all_sample_metadata':cases,'unresolved_count':len(amb),'unresolved_ids':[c['gsm']for c in amb],'decision':'No explicit EMC label. Other/undifferentiated records lack precise histology; source identity is unresolved and blocks using this collection as negative EMC evidence.'},'Sjogren2003':{'source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC1868116/','access':'Primary search-index methods accessible, but direct main retrieval andBioC failed; retainedsjogren2003.txt is anerrorpayload.','observations':'10tumors from9patients,2EMCcDNAarrays againstmyxoidliposarcoma; selected original gene table not fully recovered forDLK1. No cohort-wide DLK1 absence or novelty claim.'}}
(D/'identity-priorart-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'SAM_alias_hits':len(hits),'Filion_main_matches':len(fp),'U15981_bridge':len(bridge),'GSE71119_samples':len(cases),'source_histology_counts':dict(hist),'unresolved':len(amb)}))
