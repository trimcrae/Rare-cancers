"""Exploratory, multiplicity-aware partner comparison frozen in AMENDMENT01."""
import json,re,hashlib,collections,math
from pathlib import Path
from scipy.stats import fisher_exact
D=Path(__file__).resolve().parent
r=json.loads((D/'foundation-emc-all-values.json').read_text());cases=[x for x in r['source_labeled_cases']if x['source_final_emc']]
def group(x):
 partners={str(e[k])for e in x['NR4A3_support']for k in ['gene','partner_gene']if str(e[k])!='NR4A3'}
 known=partners&{'TAF15','EWSR1'}
 return next(iter(known))if len(known)==1 else 'other_or_ambiguous'
groups=collections.Counter(group(x)for x in cases)
gene_sets={}
for p in [D/'kegg-mtor.txt',D/'kegg-pi3k-akt.txt']:
 active=False;genes={}
 for line in p.read_text().splitlines():
  tag=line[:12].strip()
  if tag:active=tag=='GENE'
  if active:
   m=re.match(r'\s*(\d+)\s+([^;]+);',line[12:])
   if m:genes[m[2]]=m[1]
 assert len(genes)>100
 gene_sets[p.name]=genes
pathway=set().union(*(set(v)for v in gene_sets.values()))
secondary={g:set(v['source_ids'])for g,v in r['gene_source_id_counts'].items()}
T={x['source_id']for x in cases if group(x)=='TAF15'};E={x['source_id']for x in cases if group(x)=='EWSR1'}
tests=[]
for gene,ids in sorted(secondary.items()):
 a=len(ids&T);b=len(T)-a;c=len(ids&E);d=len(E)-c
 or_,p=fisher_exact([[a,b],[c,d]],alternative='two-sided')
 tests.append({'gene':gene,'TAF15_altered':a,'TAF15_total':len(T),'EWSR1_altered':c,'EWSR1_total':len(E),'fisher_OR':str(or_)if not math.isfinite(or_)else or_,'two_sided_p_exploratory':p,'bonferroni_observed_secondary_genes':min(1,p*len(secondary)),'bonferroni_reported465_exonic_panel_genes':min(1,p*465)})
pathway_cases=[]
for x in cases:
 ev=[e for e in x['secondary_events']if str(e['gene'])in pathway]
 if ev:pathway_cases.append({'source_id':x['source_id'],'fusion_group':group(x),'events':ev})
tsc2=[x for x in cases if x['source_id']in secondary['TSC2']]
source_files=['foundation-emc-all-values.json','kegg-mtor.txt','kegg-pi3k-akt.txt','AMENDMENT-01-TSC2.txt']
out={'date':'2026-10-04','status':'Exploratory follow-up; no confirmed association or efficacy inference','inputs':{f:hashlib.sha256((D/f).read_bytes()).hexdigest()for f in source_files},'fusion_groups':dict(groups),'all_secondary_gene_count':len(secondary),'all_gene_tests':tests,'kegg_memberships':gene_sets,'kegg_union_genes':len(pathway),'all_pathway_event_cases':pathway_cases,'TSC2_complete_cases':tsc2,'limits':['Exploratory selection and broad gene search; no unadjusted p-value is confirmatory.','Source methods report465 coding genes overall but specimen-specific panel assignment is absent; no per-case coverage verification is implied.','The original article describes7494patients; distinct source IDs are treated as distinct reported patients, with no cross-cohort identity or normal-tissue validation.','A truncating TSC2 variant in tumor-only data does not establish somatic/biallelic loss; CN0 is a source copy-number call, not independently measured protein loss.','Pathway membership alone does not establish oncogenicity or mTOR activation.']}
(D/'tsc2-followup-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'fusion_groups':dict(groups),'secondary_genes':len(secondary),'TSC2':next(x for x in tests if x['gene']=='TSC2'),'pathway_genes':len(pathway),'pathway_cases':[{'id':x['source_id'],'fusion':x['fusion_group'],'genes':[e['gene']for e in x['events']]}for x in pathway_cases]},indent=2))
