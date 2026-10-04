import csv,hashlib,json,pathlib,re,xml.etree.ElementTree as E
import openpyxl
D=pathlib.Path(__file__).resolve().parent
out={'scope':'Metadata/assay eligibility, not peptide abundance or absence. No authenticated EMC HLA-bound measurement identified in these inspected sources. Broad atlas independent review remains separate.'}
queries={};unique={}
for p in sorted(list(D.glob('pride-search-*.json'))+list(D.glob('pride-alias-*.json'))):
 a=json.loads(p.read_text());queries[p.name]={'n_returned':len(a),'accessions':[x['accession'] for x in a]}
 for x in a:unique[x['accession']]=x
out['queries']=queries;out['unique_projects']=len(unique)
index=[]
for accession,x in sorted(unique.items()):
 fields={k:x.get(k) for k in ['title','projectDescription','sampleProcessingProtocol','dataProcessingProtocol','sampleAttributes','keywords','organismsPart','diseases','references']}
 text=json.dumps(fields,ensure_ascii=False)
 index.append({'accession':accession,'title':x['title'],'assay_identity_flags':sorted(set(re.findall(r'HLA|immunopeptid\w*|ligandome|extraskeletal|myxoid',text,re.I))),
 'screen_status':'retrieved project metadata screened; source-level eligibility disposition in COVERAGE.txt; not a peptide evaluation',
 'metadata_sha256':hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()})
out['project_screen']=index
w=openpyxl.load_workbook(D/'pediatric-tableS4.xlsx',read_only=True,data_only=True)
out['pediatric_all_ligand_tables']=[{'sheet':s.title,'description':s.cell(1,1).value} for s in w]
assert len(out['pediatric_all_ligand_tables'])==8
assert all(any(n in x['description'] for n in ['HOS','U2OS','SAOS2','A673']) for x in out['pediatric_all_ligand_tables'])
r=E.parse(D/'pleural2022.xml').getroot();tab=r.findall('.//table-wrap')[0]
rows=[]
for row in tab.findall('.//tbody/tr'):
 cells=[' '.join(''.join(c.itertext()).split()) for c in row]
 if cells and re.fullmatch('P[0-9]+',cells[0]):rows.append({'id':cells[0],'age_sex':cells[1],'disease':cells[2],'raw_cells':cells})
out['pleural_patient_rows']=rows
assert len(rows)==14
assert not any(re.search('sarcoma|myxoid',x['disease'],re.I) for x in rows)
pages=json.loads((D/'jci2023-supp-pages.json').read_text('utf-8'))
out['jci101']={'diagnostic_label':'Extraskeletal myxoid chondrosarcoma - Inguinal region','mainTable1':'male, 74 years, primary, grouped as Chondrosarcoma',
 'prior_chemotherapy':False,'prior_radiation_days':862,
 'HLA_S2_source_labels':{'A':['A*29:01/02','A*01:22N'],'B':['B*38:01/02','am'],'C':['C*16:01','am']},
 'HLA_caution':'Author-inferred genotype; / denotes protein ambiguity, am fully ambiguous. Not measured peptide ligands or established allele-specific presentation.',
 'individual_flow_CD91_TCR_numeric_crosswalk':'not located in main text, main Tables1-3 or full15-page supplement; group plots lack case labels; underlying numerical data request-only',
 'WES_public_project':'PRJNA987736','WES_access_gap':'initial ENA filereport HTTP500; no WES sequence analyzed here',
 'molecular_EMC_confirmation':'not reported in inspected case row; no NR4A3 defining fusion documented',
 'independence':'one source-labelled clinical case, no second sample identified; cross-cohort overlap unverified; no pooling',
 'presentation_eligibility':'unsuitable: study human epitope analysis uses NetMHC predictions from WES, not HLA-eluted MS'}
(D/'metadata-evaluation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'queries':{k:v['n_returned'] for k,v in queries.items()},'unique':len(unique),'pediatric_ligand_tables':len(out['pediatric_all_ligand_tables']),'pleural_patients':len(rows),'JCI101_source_row_verified':True},indent=2))
