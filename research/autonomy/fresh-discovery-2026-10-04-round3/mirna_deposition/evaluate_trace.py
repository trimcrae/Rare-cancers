"""Audit all retrieved metadata, keeping quantitative miRNA data unopened."""
from pathlib import Path
import json,csv,re,collections,xml.etree.ElementTree as E,hashlib
D=Path(__file__).resolve().parent
entrez=json.loads((D/'entrez-search-receipts.json').read_text())
queries=[]
for r in entrez:
    x=r['result'];assert int(x['count'])==len(x['idlist']);queries.append({'db':r['db'],'query':r['query'],'count':int(x['count']),'translation':x.get('querytranslation'),'warnings':x.get('warninglist')})
gds={};sra={};bp={}
for pattern,out in [('gds-*summaries-*.json',gds),('sra-*summaries-*.json',sra),('bioproject-summaries-*.json',bp)]:
    for p in D.glob(pattern):
        x=json.loads(p.read_text())['result']
        for u in x['uids']:out[u]=x[u]
groups=collections.defaultdict(list)
for u,r in sra.items():
    x=E.fromstring('<root>'+r['expxml']+'</root>');study=x.find('.//Study');st=x.find('.//LIBRARY_STRATEGY');sample=x.find('.//Sample');exp=x.find('.//Experiment')
    groups[study.get('acc')].append({'uid':u,'title':x.findtext('.//Title'),'study_name':study.get('name'),'strategy':st.text if st is not None else None,'sample':sample.get('acc')if sample is not None else None,'experiment':exp.get('acc')if exp is not None else None,'submitter':x.find('.//Submitter').attrib if x.find('.//Submitter')is not None else{}})
# Restrict output to identity/design metadata. Do not interpret or select molecular subtypes.
sdrf=list(csv.DictReader((D/'E-MTAB-7265.sdrf.txt').open(encoding='utf8'),delimiter='\t'))
keys=['Source Name','Comment[ENA_SAMPLE]','Characteristics[disease]','Characteristics[patientid]','Characteristics[tumor grading]','Material Type','Comment[ENA_EXPERIMENT]','Comment[ENA_RUN]','Comment[LIBRARY_STRATEGY]']
french=[{k:r[k]for k in keys}for r in sdrf]
sx=E.parse(D/'SRP223204-all8-experiments.xml');swiss=[]
for p in sx.findall('.//EXPERIMENT_PACKAGE'):
    s=p.find('SAMPLE');swiss.append({'sample':s.attrib,'experiment':p.find('EXPERIMENT').attrib,'attributes':{a.findtext('TAG'):a.findtext('VALUE')for a in s.findall('.//SAMPLE_ATTRIBUTE')},'study_title':p.findtext('.//STUDY_TITLE')})
english=[]
for b in (D/'GSE87054-samples.txt').read_text(encoding='utf8').split('^SAMPLE = ')[1:]:
    ll=b.splitlines();d=collections.defaultdict(list)
    for line in ll:
        if ' = 'in line:
            k,v=line.split(' = ',1)
            if k in ['!Sample_title','!Sample_source_name_ch1','!Sample_characteristics_ch1','!Sample_library_strategy']:d[k].append(v)
    english.append({'gsm':ll[0],'metadata':dict(d)})
bio={}
for p in D.glob('biostudies-search-*.json'):
    o=json.loads(p.read_text());assert len(o['hits'])==o['totalHits']
    for r in o['hits']:bio[r['accession']]={'title':r.get('title'),'from_search':p.name}
author_queries=[]
for p in D.glob('*author-alias-search.json'):
    r=json.loads(p.read_text())['esearchresult'];assert len(r['idlist'])==int(r['count']);author_queries.append({'file':p.name,'count':int(r['count']),'translation':r.get('querytranslation'),'warnings':r.get('warninglist')})
out={'date':'2026-10-04','quantitative_miRNA_payloads_opened':False,'MSTS16_authenticated_public_deposit':None,'search_queries':queries,'author_alias_queries':author_queries,'unique_metadata_counts':{'GDS_records':len(gds),'SRA_experiments':len(sra),'BioProject_records':len(bp),'BioStudies_records':len(bio)},'GDS_all_records':[{'uid':u,'accession':r.get('accession'),'title':r.get('title'),'summary':r.get('summary'),'assay':r.get('gdstype'),'n_source_samples':r.get('n_samples'),'pubmedids':r.get('pubmedids')}for u,r in gds.items()],'SRA_all_study_groups':dict(groups),'BioProject_all_records':bp,'BioStudies_all_hits':bio,'complete_candidate_identity':{'E-MTAB-7265':{'n':len(french),'sample_rows':french,'source':'French multicenter frozen cartilage tumors; no MSTS author/cohort link','grading_counts':dict(collections.Counter(r['Characteristics[tumor grading]']for r in french)),'limits':'Generic chondrosarcoma labels do not independently exclude EMC. Original study metadata is an unrelated cartilage-tumor cohort, not authenticated as MSTS2013 or EMC.'},'SRP223204':{'n':len(swiss),'sample_rows':swiss,'limits':'Eight Balgrist Swiss biopsy samples, three benign/twoGradeI/threeGradeII; no explicit EMC label or MSTS cohort crosswalk.'},'GSE87054':{'n':len(english),'sample_rows':english,'limits':'All27 fingerstick blood spots, not16FFPE tumor profiles. Gradedchondrosarcoma identities do not establish EMC eligibility.'}},'decision':'Bounded trace complete without authenticating a numerical public deposit for the conference cohort. No biological result; do not infer no deposit exists. All16 reported EMC profiles remain unavailable for individual mature-miRNA analysis pending accession/sample mapping. Broad candidate histologies remain unresolved where not explicit.'}
(D/'trace-evaluation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'unique_metadata_counts':out['unique_metadata_counts'],'candidate_counts':{k:v['n']for k,v in out['complete_candidate_identity'].items()},'authenticated_MSTS_deposit':None}))
