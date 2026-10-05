#!/usr/bin/env python3
"""Reproduce the scoped measurement/eligibility gate from preserved primary bytes.
No read quantification, variant calling, image digitization or effect inference.
Cache-only primary sources must be restored to rerun; portability is explicit.
"""
import argparse,datetime,hashlib,json,pathlib,re,subprocess,xml.etree.ElementTree as E
P=pathlib.Path(__file__).resolve().parent;C=P/'.cache'
expected={x['path']:x['sha256'] for x in json.load(open(P/'SOURCE-HASHES.json'))['raw_records']} if (P/'SOURCE-HASHES.json').is_file() else {}
def sha(f):
 actual=hashlib.sha256(f.read_bytes()).hexdigest();rel=str(f.relative_to(P))
 if rel in expected:assert actual==expected[rel],('Cache input changed',rel)
 return actual
def source(name):
 f=next((x for x in C.glob(name+'-*.xml') if 'bioc_xml' in x.name),None)
 if f is None:f=C/(name+'-epmc_xml.xml')
 root=E.fromstring(f.read_bytes())
 ps=[e.findtext('text','') for e in root.findall('.//passage')] if root.tag=='collection' else [' '.join(e.itertext()) for e in root.findall('.//body//p')+root.findall('.//table-wrap')+root.findall('.//fig')]
 return f,root,list(dict.fromkeys(ps))
def expanded_table(table):
 # Resolve original rowspans without moving reported values to another sample.
 carry={};out=[]
 for tr in table.findall('.//tr'):
  row={};nxt={}
  for col,(val,left) in carry.items():
   row[col]=val
   if left>1:nxt[col]=(val,left-1)
  col=0
  for cell in list(tr):
   while col in row:col+=1
   val=' '.join(' '.join(cell.itertext()).split());span=int(cell.get('colspan','1'));rs=int(cell.get('rowspan','1'))
   for j in range(span):
    row[col+j]=val
    if rs>1:nxt[col+j]=(val,rs-1)
   col+=span
  out.append([row.get(i,'') for i in range(max(row,default=-1)+1)]);carry=nxt
 return out
sources={};obs={}
for name in ['heterogeneity2022','pgr2022','kit2018','imatinib2021','pleural2022','regression2025','cabozantinib2021','trough2022','sorafenib2011','bez2352016','collateral2025']:
 f,r,ps=source(name);sources[name]={'cache_path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f)};obs[name]={'selected_primary_passages':[]}
 if name=='heterogeneity2022':
  rows=expanded_table(r.find('.//table-wrap'));assert len(rows)==9;assert all(len(x)==13 for x in rows)
  data=[dict(zip(rows[0],x)) for x in rows[1:]];assert len({x['Source'] for x in data})==4
  pre=[x for x in data if 'pre-treatment' in x['Source'] and x['Gene']=='EGFR'][0];post=[x for x in data if 'post-treatment' in x['Source'] and x['Gene']=='EGFR'][0];assert pre['Amplification']=='3.00' and post['Amplification']=='4.13'
  obs[name].update(all_printed_table_rows=data,donors=1,conditions=4,identity='NR4A3 break-apart positive; partner unreported',exposure='Five doxorubicin/ifosfamide cycles between pre/post recurrence samples; no reported antiangiogenic treatment',descriptive_EGFR_copy_number_change={'pre':3.00,'post':4.13,'post_minus_pre':round(4.13-3.00,2),'relative_percent_change':round((4.13/3.00-1)*100,6),'meaning':'Arithmetic on published panel copy-number values, not adaptive kinase activity or a new finding'},paired_RET_activity_available=False,source_limits=['Primary lesion unavailable for NGS; four dependent samples from one donor.','Axillary lymph-node label in Table1 differs from narrative inguinal-node pathology; no invented correspondence.','Bulk copy-number/purity and different lesions cannot establish clonal selection or kinase activation.','Original FBXW7 c.585-2A>T/exon4 and c.1637C>A/p.S546* rows are labelled missense by authors; preserve labels without recoding them.','Supplement Table2.XLSX has Gene List and an NGS-panel sheet containing FASTQ-like text; no donor/condition crosswalk was recovered. No read analysis performed.'])
  needles=['somatic tumor testing','First, patients are treated','genetic analysis of the primary','After five cycles']
 elif name=='kit2018':
  pdf=C/'kit2018_supp/ijms-19-01855-s001.pdf';text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True);rows=[]
  for line in text.splitlines():
   if line.strip().startswith('#'):
    x=re.split(r'\s{2,}',line.strip());assert len(x)==6,x
    num=int(re.search(r'#(\d+)',x[0]).group(1));rows.append({'sample':num,'Sanger_only':'*' in x[0],'NR4A3_fusion':x[1],'sex':x[2],'age_at_primary':int(x[3]),'primary_site':x[4],'distant_relapse_printed':x[5]})
  assert [x['sample'] for x in rows]==list(range(1,21));assert sum(x['Sanger_only'] for x in rows)==15
  obs[name].update(all20_clinical_rows=rows,supplement_sha256=sha(pdf),WTS_cases=[1,2,3,4,5],WTS_partner='EWSR1-NR4A3 for all five',hotspot_cases=20,reported_KIT_exon11_mutant_cases=1,reported_other_KIT_PDGFRA_hotspot_mutants=0,western_blot_cases=3,western_result='KIT in all three tested; mild phospho-KIT only mutant case1',sample1_KIT_RNA_published_relative_value=9.8,sample1_treatment='Published prolonged sunitinib response; never received imatinib',paired_RET_activity_available=False,source_limits=['Single specimens, no case-linked pre/on/progression assay comparison.','No treatment dates/assay-condition crosswalk in complete TableS1.','Potential Italian sunitinib2012/2014 and RNA-cohort donor overlap not resolved; do not pool.'])
  needles=['WTS was performed','Pathogenic single nucleotide','additional cohort of 15','never received imatinib','KIT protein expression']
 elif name=='pgr2022':
  fig=C/'pgr2022-supp/po-6-e2200039-g003.jpg';table=C/'pgr2022-supp/po-6-e2200039-g004.jpg'
  obs[name].update(donors=1,donor_label='TP_2274 (Fig2C)',demographics='35F, pregnancy-associated cellular EMC',assay_condition='Recurrent resection after pregnancy/delivery and initial surgery; MI-ONCOSEQ exome-capture RNA sequencing before tamoxifen',fusion='PGR exon2–NR4A3 exon2 5′UTR',Table1_exact_transcription=[['Somatic point mutations (1)','No informative, actionable, recurrent mutations'],['Copy number aberrations','NR4A3, focal gain (four copies); Copy gain (three copies): chr11 (PGR,AIP)'],['Gene fusions','PGR(exon2)-NR4A3(exon2,5′UTR)'],['Outlier gene expression','NR4A3,PGR,ESR1'],['Germline variants for disclosure','No cancer-associated pathogenic germline variants']],Table1_image_sha256=sha(table),Figure2_image_sha256=sha(fig),gene_expression='Fig2C ESR1/NR4A3/PGR TPM versus >3000 MI-ONCOSEQ samples; no exact index values tabulated or digitized',narrative_outlier_genes=['ESR1','PGR','GREB1'],table_narrative_limit='Narrative additionally names GREB1; Table1 instead lists NR4A3 with ESR1/PGR. Preserve both.',clinical_conditions=['20weeks pregnancy groinmass/aspiration presumedhematoma','23weeks surgery/biopsy cellularEMC, EWSR1FISHnegative','25weeks MRI bilateral4cm inguinal lesions, continued growth during pregnancy','34weeks planneddelivery, cellulitis/wounddehiscence delayedresection','40days postpartum primarywideexcision10.5/8.2cm cellulargrade2/3, negative margins','2months postoperative localrecurrence; repeat7.3cm cellularEMCresection, positive lateral margin; sequenced recurrenttumor','1month later new bilateral lungnodules up to7mm and1.8cm mons pubis nodule; no further surgery','Tamoxifen thereafter; reported lungnodule decrease andnoPD for>5years; dose not specified'],paired_post_tamoxifen_molecular_assay=False,paired_RET_activity_available=False,source_limits=['Published baseline expression/clinical interpretation is prior art, no independent hormone-benefit result.','Bulk gene reads not assigned to native versus fusion transcripts.','Single pregnancy-associated donor; normal/hormonal/tumor compartment alternatives require controls.','MI-ONCOSEQ and Michigan clinical cohort donor overlap unresolved.'])
  needles=['A 35-year-old','Forty days after delivery','One month later','The results of next-generation sequencing','Genomic analysis.']
 elif name=='cabozantinib2021':
  trial=json.load(open(C/'caboz_trial.json'));assert trial['protocolSection']['identificationModule']['nctId']=='NCT01755195'
  obs[name].update(author_labelled_EMC_donors=3,EMC_patient_records=[{'id':'1010003','condition':'Prior primary9×6cm thighresection+RT; lungnodules observed2years; cabozantinibPR after10cycles, imagingafter98cycles/onstudy99cycles','serial_kinase_assay_crosswalk':None},{'id':None,'condition':'Second Table1EMC; individual identity/assaycondition/response not exposed','serial_kinase_assay_crosswalk':None},{'id':None,'condition':'Third Table1EMC; individual identity/assaycondition/response not exposed','serial_kinase_assay_crosswalk':None}],prior_TKI_record='One EMC among six who received TKI as sole initial therapy; no casecrosswalk to1010003 or others',serial_plasma_scope={'all_histology_donors':42,'markers':['sMET','HGF','VEGF-A','sVEGFR2'],'conditions':['baseline','cycle1day1 3–6hours postdose','cycle2day1 3–6hours postdose'],'EMC_donor_assay_crosswalk':None,'measurement':'MSD electrochemiluminescent/immunoassays, calibrated proteins'},supplementS3='Visually inspected: pooled scatter/boxplots and PR/SD6+cycles/SD<6cycles/PD-or-NA groups; no subtype labels or caseIDs. No plotdigitization.',trial_record='Read-only API results retain aggregate outcomes, no released specimen-level EMC plasma crosswalk.',paired_RET_activity_available=False,source_limits=['Three EMC enrolments do not prove that all three had plasma collected.','Two EMC responses remain unknown; only one reported PR is not imputed across cohort.','Early soluble plasma targets are not tumor RET phosphorylation or acquired-resistance samples.','Different selected outcome/missing-C2D1 groups confound even pooled temporal interpretation.'])
  needles=['Blood samples (mandatory','Blood sampling for evaluation','Patient 1010003, with an EMC','1010003, EMC','single-agent TKI as initial']
 elif name=='imatinib2021':
  obs[name].update(donors=1,demographics='55F',identity='NR4A3 gene-region rearrangement',assay='Pretreatment partial groinexcision KITexon11c.1669T>G; germlinebloodnegative',conditions=['Baseline6.8×4.3×2cm abdominalwall/2.3×2.2cm groin masses, bilateral lungmetastases','Baselinegroinbiopsy NR4A3 andsomaticKIT variant','Zoledronicacid before mutationresult; thenimatinib','Published stable disease3years, no postdrugmolecular assay'],paired_RET_activity_available=False,source_limits=['Baseline genotype and clinical course are published, not serial resistance.'])
  needles=['A partial excisional biopsy','The patient was initially treated','Her disease has been stable']
 elif name=='pleural2022':
  obs[name].update(donors=1,demographics='34F',conditions=['PrimarykneeEMC surgery+RT3years earlier','Pleuralmetastasis thoracoscopicbiopsy before subsequentanthracycline; NR4A3-EWSR1, TMB4mut/Mb, microsatellitestable; VEGF/TGFbeta1IHCpositive','Subsequentanthracycline, publishedSD'],paired_RET_activity_available=False,source_limits=['Only metastasis assayed; no primary or postdrug paired expression/protein specimen.','Assay/compartment context differs from RET kinase activity.'])
  needles=['A 34‐year‐old woman','On immunohistological examination']
 elif name=='regression2025':
  obs[name].update(donors=1,identity='NR4A3FISH',conditions=['2015initial6cm lowgradeprimaryR1, <1mitosis/10HPF; noadjuvant','2016sunitinib:2.5cm→4.1cm after6months, progression','2017atezolizumab5cycles, localprogression11.9cm','2018trabectedin5cycles, newlungnodules/localPD15.8cm','2019ONCOmine noactionablealterations, nofurther systemictherapy; RTdeclined','2019October18cm debulkinggrade2, necrosis/hemorrhage/vascularinvasion/R1','2020Janlungnodulesdecreased; Mayresolution; Nov2024noevidencedisease'],paired_RET_activity_available=False,source_limits=['One genomic profile, no serial phospho/kinase assay.','Histology at baseline and heavily pretreated debulking differs, with treatment/selection/composition confounding.','Published regression narrative is not new immune or resistance mechanism.'])
  needles=['first-line sunitinib','next-generation sequencing (NGS)','Four and a half years','After his surgery']
 elif name=='trough2022':
  obs[name].update(EMC_scope='Included in unnumbered other*category13 of95; no individual EMC count/ID',assay='Serial plasma pazopanib concentration; HPLC-UV; steady state>=15days; first3months every2weeks thenmonthly',paired_RET_activity_available=False,source_limits=['No EMC case-level exposure/outcome crosswalk in mainTables1–4; generic plasma drug concentration is not tumor pathway activity.'])
  needles=['Blood samples were drawn','Including:','Data available within']
 elif name=='sorafenib2011':
  rows=expanded_table(r.findall('.//table-wrap')[0]);h=rows.index(['Histology','']);hist=rows[h+1:rows.index(['Primary site',''])];assert sum(int(x[1].split(' ')[0]) for x in hist)==15
  obs[name].update(complete_histology_counts=hist,EMC_donors=0,paired_RET_activity_available=False,source_limits=['All15histologyroster counts examined; no EMC. Threepaired biopsies and plasma observations belong to other sarcomas.'])
  needles=['Biopsies were available from 3']
 elif name=='bez2352016':
  obs[name].update(mechanistic_donor='Published UPS donor-derived model, not EMC',paired_RET_activity_available=False,source_limits=['Explicit sourceidentity UPS; cannot substitute another sarcoma resistance result for EMC.'])
  needles=['Herein we report the case']
 elif name=='collateral2025':
  obs[name].update(mechanistic_models=['A204','G402'],identity='Malignant rhabdoid tumour models, not EMC',primary_roster=['A204','G402','SAOS2','U2OS','HT1080','MESSA','SW684','SW872','Hs729T','RUCH3','T91-95','SW982','HEK293T','SJSA1','RMS-YM'],paired_RET_activity_available=False,source_limits=['Primary acquired-resistance experiments use rhabdoid models.','Complete supplemental identity of otherscreenedlabels not reevaluated; any unclear model remains pending, not certified EMCabsence.'])
  needles=['Using malignant rhabdoid tumour','A204 and G402 cell lines were obtained']
 for needle in needles:
  found=[t for t in ps if needle in t];assert found,(name,needle);obs[name]['selected_primary_passages']+=found[:1]
output={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_question':'Within-donor preantiangiogenic versus acquiredresistance RET/linked kinase activity','scope':'All relevant measured EMC conditions in inspected sources above; reused evidence and broader pending sources are in coverage. Published contrasts are not new discoveries.','sources':sources,'observations':obs,'eligible_new_paired_RET_activity_comparisons_in_evaluated_sources':sum(x.get('paired_RET_activity_available',False) for x in obs.values()),'decision':'SHELVE standalone RET adaptation claim; measurements/value gate fails, no absence/resistance/efficacy inference.','raw_reanalysis':False,'raw_public_reads_in_heterogeneity_supplement':'Preserved without sequencing analysis or caseassignment.'}
parser=argparse.ArgumentParser();parser.add_argument('--output',type=pathlib.Path,default=P/'MEASUREMENTS.json');args=parser.parse_args()
args.output.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'sources':len(sources),'Wang_conditions':obs['heterogeneity2022']['conditions'],'KIT_allcases':len(obs['kit2018']['all20_clinical_rows']),'caboz_EMC':len(obs['cabozantinib2021']['EMC_patient_records']),'eligible_comparisons':output['eligible_new_paired_RET_activity_comparisons_in_evaluated_sources']},indent=2))
