import json,collections
from fetch_pilot import OUT
load=lambda n:json.loads((OUT/n).read_text())
mut=load('emc_and_nr4a3_mutations.json');cn=load('emc_and_nr4a3_cna.json');cl=load('emc_and_nr4a3_sample_clinical.json');sv=load('emc_and_nr4a3_sv.json')
print('MUTATIONS');print(json.dumps([{k:r.get(k) for k in ('sampleId','patientId','entrezGeneId','proteinChange','mutationType')}|{'gene':r['gene']['hugoGeneSymbol']} for r in mut],indent=2))
print('NONZERO CNA');print(json.dumps([{k:r.get(k) for k in ('sampleId','patientId','entrezGeneId','value')}|{'gene':r['gene']['hugoGeneSymbol']} for r in cn if abs(r['value'])==2],indent=2))
print('SV');print(json.dumps([{k:r.get(k) for k in ('sampleId','patientId','site1HugoSymbol','site2HugoSymbol','eventInfo')} for r in sv],indent=2))
want=['GENE_PANEL','FACETS_WGD','FACETS_QC','FACETS_PURITY','FRACTION_GENOME_ALTERED','SAMPLE_TYPE','PRIMARY_SITE','METASTATIC_SITE','TUMOR_PURITY','TMB_SCORE','MSI_SCORE']
by=collections.defaultdict(dict)
for r in cl:
 if r['clinicalAttributeId'] in want:by[r['sampleId']][r['clinicalAttributeId']]=r['value']
print('CLINICAL');print(json.dumps(by,indent=2))
