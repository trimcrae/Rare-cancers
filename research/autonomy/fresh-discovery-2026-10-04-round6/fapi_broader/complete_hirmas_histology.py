#!/usr/bin/env python3
"""Append all released non-sarcoma histology leaves and unresolved generic labels."""
import datetime,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
rows={
 'Pancreas':[('Acinar cell carcinoma',1),('Ductal adenocarcinoma',62),('Intraductal papillary mucinous neoplasia',1),('Neuroendocrine carcinoma',1),('Signet ring cell carcinoma',1),('Unknown',1)],
 'Brain':[('Astrocytoma',1),('Glioblastoma multiforme',19),('Unknown',2)],
 'Lung':[('Adenocarcinoma',5),('Adenosquamous carcinoma',6),('Squamous cell carcinoma',3)],
 'Pleura':[('Biphasic mesothelioma',1),('Epithelial mesothelioma',10),('Sarcomatoid mesothelioma',1)],
 'Cholangiocellular carcinoma':[('Extrahepatic CCC (Klatskin tumor)',2),('Extrahepatic CCC (non-Klatskin tumor)',2),('Intrahepatic CCC',7)],
 'Colorectal':[('Colon adenocarcinoma',6),('Rectal adenocarcinoma',5)],
 'Prostate':[('Adenocarcinoma',11)],
 'Head and Neck':[('Adenoid cystic carcinoma',5),('Polymorphic adenocarcinoma',1),('Small blue round cell tumor',1),('Squamous cell carcinoma',2)],
 'Bladder':[('Urothelial carcinoma',8)],
 'Lymphoma':[('NHL, diffuse large B-cell lymphoma',1),('NHL, follicular lymphoma',5),('MALT lymphoma',1)],
 'Myeloma':[('IgA kappa',2),('IgG kappa',2),('Light chain kappa',1),('Smouldering myeloma',1)],
 'Ovarian':[('Other',1),('Serous carcinoma',3)],
 'Breast':[('Tripe negative adenocarcinoma',3)],
 'Duodenum':[('Duodenal adenocarcinoma',2)],
 'Other':[('Cervix, squamous cell carcinoma',1),('Knee, myoepithelial carcinoma',1),('Liver, hepatocellular carcinoma',1),('Skin, melanoma',1),('Stomach, gastric adenocarcinoma',1),('Thyroid, papillary carcinoma',1)]}
text=(ROOT/'raw/hirmas2023_supp.txt').read_text();section=text[text.index('Supplemental Table 1.'):text.index('Supplemental Table 2.')]
norm=lambda s:re.sub(r'\s+',' ',s).strip().lower()
for group,labels in rows.items():
 for label,n in labels:assert norm(label) in norm(section),label
sarcoma=json.loads((ROOT/'hirmas2023-roster.json').read_text())
assert sum(n for vals in rows.values() for _,n in vals)==193
assert 193+sarcoma['sarcoma_patients']==324
unresolved=[{'source_group':g,'source_label':label,'patients':n,'status':'unavailable evidence','consequence':'No subtype/genomic crosswalk in inspected release; do not exclude EMC by organ or nonspecific label.'} for g,vals in rows.items() for label,n in vals if (g,label) in {('Pancreas','Unknown'),('Brain','Unknown'),('Ovarian','Other'),('Head and Neck','Small blue round cell tumor')}]
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':'Additive completeness clarification after primary freeze and independent named-source omission challenge; original PLAN/decision unchanged. All TableS1 text was inspected in the original pilot, but initial export focused sarcoma leaves plus324macrocounts. This append preserves every remaining released histology leaf and explicit generic identities.','source_pdf_sha256':hashlib.sha256((ROOT/'raw/hirmas2023_supp.pdf').read_bytes()).hexdigest(),'source_location':'Original SupplementalTable1 PDF pp13–14','non_sarcoma_leaf_rows':[{'group':g,'source_label':label,'patients':n} for g,vals in rows.items() for label,n in vals],'non_sarcoma_count':193,'sarcoma_count':131,'complete_released_count':324,'additional_unresolved_labels':unresolved,'no_individual_ID_crosswalk':'No source ID or patient scan crosswalk for these aggregate labels. Five generic patients are additional unresolved source categories, not authenticatedEMC. Category is not an anatomical exclusion.','decision':'Maintain shelving; no authenticated EMC measurements and no new disease finding. No ratios or inference. Complete relevant accessible sources remains mandatory; search not exhausted.'}
(ROOT/'HIRMAS-HISTOLOGY-COMPLETENESS-AMENDMENT.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('PASS: complete324released histology leaves; five additional generic source-labelled patients retained unresolved.')
