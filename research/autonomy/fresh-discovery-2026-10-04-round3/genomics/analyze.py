"""Reproduce scoped primary-table evaluation; never infer absent measurements.
Run with the bundled Python and openpyxl/pypdf dependencies, PYTHONUTF8=1.
No network, no writes outside this packet. Source labels remain explicit.
"""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET,zipfile
from openpyxl import load_workbook
from scipy.stats import beta

D=Path(__file__).resolve().parent
R=D.parents[1]/'fresh-discovery-2026-10-04-round2'/'genomics'
def save(name,obj): (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
tables={}
for p in sorted(D.glob('CAM4*')):
    if p.suffix=='.docx':
        with zipfile.ZipFile(p) as z: root=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tables[p.name]={'text':[e.text or '' for e in root.findall('.//w:t',ns)],'rows':[
            [' '.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in row.findall('w:tc',ns)]
            for row in root.findall('.//w:tr',ns)]}
    elif p.suffix=='.xlsx':
        w=load_workbook(p,read_only=True,data_only=True)
        tables[p.name]={s.title:[list(row) for row in s.values] for s in w}
save('japan-all-tables.json',tables)
rows=tables['CAM4-14-e71098-s002.xlsx']['Sheet1']
emc=[]
for n,row in enumerate(rows,1):
    if len(row)>2 and row[2]=='EMC':
        small=[{'gene':row[i],'aa_change_a':row[i+1],'aa_change_b':row[i+2]} for i in range(3,27,3) if row[i]]
        emc.append({'excel_row':n,'patient':row[0],'age':row[1],'small_variants':small,
                    'reported_amplifications':[x for x in row[27:38] if x],
                    'reported_losses':[x for x in row[38:42] if x],
                    'literal_row':row})
assert [(x['patient'],x['age']) for x in emc]==[(26,40),(109,59),(126,56)]
assert sum(len(x['small_variants']) for x in emc)==5
assert not any(x['reported_losses'] or x['reported_amplifications'] for x in emc)
germline=tables['CAM4-14-e71098-s004.xlsx']['Sheet1']
assert not any(str(c).strip()=='EMC' or 'Q160' in str(c) for row in germline for c in row)
root=ET.parse(D/'japan2025.xml')
contexts=[]
for tag in ['p','table-wrap']:
    for node in root.iter(tag):
        s=' '.join(node.itertext())
        if any(k.casefold() in s.casefold() for k in ['PMS2','MSI','TMB','allele','germline','pazopanib']):
            contexts.append({'tag':tag,'text':s})
save('japan-pms2-context.json',contexts)

# Manually transcribed from the retained, visually inspected primary figure/table.
# No numerical fold changes are inferred from a colour scale.
shared='ANO5 ASB2 CA3 CACNA2D1 CASQ1 CCN1 CDH5 CDKN1A CLEC3B CLIC5 COL4A3 CRK DES DMD DUSP1 DYSF FILIP1 FLNC FLT1 HBA2 HBB JPH1 KLF6 MDM2 MYH2 MYO18B MYOM3 NR4A2 PADI2 PAPPA PDK4 PER1 PLA2G4B PRSS12 PTGDS RYR3 S100A1 SCN4A SNRPD1 SOX18 STAC3 SURF4 TAGLN TYRP1'.split()
assert len(shared)==len(set(shared))==44
thesis={'source':str(R/'nottley2025-thesis.pdf'),'sha256':digest(R/'nottley2025-thesis.pdf'),
    'source_url':'https://discovery.ucl.ac.uk/id/eprint/10214596/7/Nottley_10214596_Thesis.pdf',
    'patients':[
      {'id':9,'fusion':'EWSR1::NR4A3','DNA_WES':['pre_RT'],'RNA':['pre_RT','post_RT'],'DNA_WGS':[],'NanoSeq':[],
       'sex':'male','site':'leg','outcome_label':'responder'},
      {'id':29,'fusion':'TCF12::NR4A3','DNA_WES':['pre_RT'],'RNA':['pre_RT','post_RT'],'DNA_WGS':[],'NanoSeq':[],
       'sex':'male','site':'leg','outcome_label':'responder'}],
    'assay_map_source':'Figure2.2 p72; fusions p106; demographics Tables4.1/4.2 pp166-167',
    'outcome_definition':'p71: no local recurrence or disease-related death during followup; not measured RT shrinkage',
    'RT_dose_all_patients':'50Gy IMRT in25fractions; sourcep70',
    'RT_to_surgery_days_all_cohort':{'median':46,'range':[13,84],'EMC_individual_values':None},
    'baseline_signatures':{'source':'Figures3.14p136 and3.17p142, visually inspected','EMC_WES_sample_labels':['RT10','RT30'],'crosswalk_to_patient9_29':'not explicitly released; do not silently equate aliases','SBS_signatures_displayed':['SBS1','SBS5'],'ID_EMC_display':'RT10 has oneindel attributedtoID10; RT30notinindelpanel','limitation':'Singleindel andverylowSNVcounts cannot establish a mutational process; no postRTDNA. These are published author assignments, not a new discovery.'},
    'age_range': [56,63], 'age_to_ID_crosswalk':None,
    'reported_cancer_gene_variants':{'ETV6':1,'FBXW7':1},
    'cancer_gene_variant_source':'Table3.4 p105; alleles, patient and condition crosswalk not supplied here',
    'high_or_moderate_REVEL_tables_contain_EMC':False,
    'REVEL_caveat':'Absence from Tables3.1/3.2 does not establish all variants benign or all mutation types evaluated.',
    'reported_median_TMB_mut_per_Mb':0.5,
    'RNA_EMC_DE_genes':94,'RNA_EMC_unique_DE_genes':50,'RNA_EMC_shared_DE_genes':44,
    'shared_genes_table4_4':shared,
    'Figure4_9_EMC_direction':{
      'up':['CRK','CCN1','PDK4'],
      'down':['CASQ1','PRSS12','ANO5','JPH1','MYOM3','TAGLN','DMD','SOX18','HBA2','HBB'],
      'white_near_zero_or_below_display_threshold':['SERPINE1','RGS1','MT1X','FGF7','IFIT3','F13A1','LOXHD1','NOTCH4','WDR62','ZBTB16','HBA1']},
    'figure_caveat':'These are already-published subtype contrasts from two paired donors, not individual donor changes. White denotes |log2FC|<1 per caption, not biological absence; no exact effect/uncertainty extracted from colours.',
    'RNA_readout_limits':'No individual9/29 count or fold-change matrix/accession identified in full thesis or landing page. All-histology GSEA/xCell/PROGENy cannot be assigned to EMC. Biopsy versus postRT resection composition confounds interpretation.',
    'gene_note':'Table4.4 includes CACNA2D1 in EMC; CACNA1E is SS/MLS there, so do not carry over discussion as an EMC differential gene.'}
assert len(sum(thesis['Figure4_9_EMC_direction'].values(),[]))==24
thesis['paired_DNA_donors']=sum('pre_RT' in p['DNA_WES'] and 'post_RT'in p['DNA_WES'] for p in thesis['patients'])
thesis['paired_RNA_donors']=sum('pre_RT'in p['RNA'] and 'post_RT'in p['RNA'] for p in thesis['patients'])
assert thesis['paired_DNA_donors']==0 and thesis['paired_RNA_donors']==2
save('thesis-evaluation.json',thesis)

guo={'source_url':'https://link.springer.com/content/pdf/10.1007/s12672-026-05818-z_reference.pdf',
 'version':'accepted manuscript; published2026-08-24','sha256':digest(D/'guo2026.pdf'),
 'cases':[
  {'id':1,'sex':'female','age':72,'site':'right thigh','specimen_size_cm':[17,14,5],
   'morphology':'conventional with about30% hypercellular solid/epithelioid','NR4A3_FISH_percent':25,
   'fusion_partner':None,'secondary_genotype':None,'margins':'negative after wide excision',
   'conditions':[{'time':'initial','treatment':'wide excision'},{'time':'one month after surgery','treatment':'RT60Gy/30fractions'},
                 {'time':'15months after surgery','assessment':'no recurrence/metastasis'}]},
  {'id':2,'sex':'male','age':38,'site':'right popliteal fossa','specimen_size_cm':[11,6,5],
   'morphology':'classic','NR4A3_FISH_percent':30,'fusion_partner':None,'secondary_genotype':None,
   'margins':'unknown because not anatomically oriented after simple excision',
   'conditions':[{'time':'initial','treatment':'simple excision, no adjuvant therapy'},
                 {'time':'6months after initial surgery','assessment':'local recurrence plus separate noncontiguous ipsilateral thigh soft-tissue metastasis, both resected and histologically confirmed'},
                 {'time':'after repeat surgery','treatment':'no RT, chemotherapy or targeted therapy'},
                 {'time':'27months after repeat surgery to2025-04-01','assessment':'generally well; later telephone assessment lacks detailed imaging, not proven disease-free'}]}],
 'assay':'NR4A3 break-apart FISH,200evaluable tumor nuclei each; threshold15%; no partner-specific FISH/RT-PCR/RNAseq',
 'decision':'No measurable genotype variation or causal RT comparison; tumor, margins, surgery and followup differ.'}
save('guo-evaluation.json',guo)
save('analysis-results.json',{
 'japan_EMC':emc,'japan_count':len(emc),'reported_secondary_variant_rows':5,
 'japan_treatment_aggregate':{'pazopanib_n':3,'PR':1,'SD':2,'time_to_progression_months':[43.3,None,None],
  'None_definition':'not reached, not zero; patient/response mapping unavailable',
  'PR_fraction':1/3,'descriptive_exact_binomial_95CI':[beta.ppf(.025,1,3),beta.ppf(.975,2,2)],
  'CI_caveat':'Describes sample proportion uncertainty only; selection and no untreated/other-genotype comparator prevent population or predictive inference.'},
 'PMS2_followup':{'case':26,'age':40,'variant':'Q160*','TMB':None,'MSI':None,'MMR_IHC':None,'VAF':None,'purity':None,
  'germline_or_somatic':None,'biallelic':None,'individual_panel':None,'individual_response':None,
  'cohort_context':'127/136 had MSI calls, none MSI-high. TMB for132/136, high cases described onlyLMS/ULMS/IMT. Missing-case crosswalk prevents assigning results toEMC26. No EMC/Q160* in source germlineTableS15. A different PMS2 germlineI18Sfs*34 belongs to osteosarcoma,female74.',
  'decision':'No demonstrated dMMR, hereditary syndrome or ICI response from this variant.'},
 'thesis_paired_DNA_donors':0,'thesis_paired_RNA_donors':2,
 'claim_decision':'Shelve proposed genotype/RT or secondary-genotype/treatment standalone paper; no new useful disease relation established.',
 'coverage_not_exhaustive':'Qin16 full text inaccessible behind subscription; thesis matrix not located. Broad-public evidence reused fromround2, not claimed exhaustively evaluated here.'})
receipts=[json.loads(x) for x in (D/'receipts.jsonl').read_text().splitlines()]
verified=[]
for r in receipts:
 if 'sha256'in r:
  p=D/r['name'];assert p.stat().st_size==r['bytes'] and digest(p)==r['sha256'];verified.append(r['name'])
save('verification.json',{'downloaded_files_hash_verified':verified,'count':len(verified),
 'assertions':['all3EMCrows and5smallvariants extracted','all44shared EMC RNA genes unique','24heatmap genes classified','0pairedDNA versus2pairedRNA donors','noEMC/Q160* in germline table'],
 'status':'PASS','scripts_run':['fetch.py imported for bounded primary-source retrieval','analyze.py'],
 'manual_verification':'Source Figure2.2 and Table4.4/Figure4.9 visually inspected from saved page renders; manual directional transcription retained explicitly.'})
print(json.dumps({'EMC_rows':len(emc),'secondary_calls':5,'paired_DNA':0,'paired_RNA':2,'source_hashes_verified':len(verified),'status':'PASS'}))
