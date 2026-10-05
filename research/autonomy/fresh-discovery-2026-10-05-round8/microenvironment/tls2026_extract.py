#!/usr/bin/env python3
"""Extract public grouped observations without accessing private patient data."""
from pathlib import Path
import zipfile,io,subprocess,json,hashlib,datetime,xml.etree.ElementTree as ET,openpyxl
P=Path(__file__).parent;p=P/'raw/TLS2026-supplement.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
z=zipfile.ZipFile(p);nested=z.read('cancers-18-01685-s001.zip');a=zipfile.ZipFile(io.BytesIO(nested))
b=a.read('cancers-4239141-supplementary/Tables.xlsx');w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
tables={s.title:[[c.isoformat() if hasattr(c,'isoformat') else c for c in row] for row in s.iter_rows(values_only=True)] for s in w};w.close()
pdf=a.read('cancers-4239141-supplementary/cancers-4239141-Supplementary figure.pdf')
r=subprocess.run(['pdftotext','-','-'],input=pdf,capture_output=True,check=True);txt=r.stdout.decode()
primary=(P/'raw/TLS2026-PMC13255587.xml').read_bytes();root=ET.fromstring(primary)
pars=[' '.join(' '.join(e.itertext()).split()) for e in root.iter('p')]
selected=[t for t in pars if t.startswith('This retrospective study included') or t.startswith('RNA was extracted from FFPE') or t.startswith('The datasets generated and analyzed') or t.startswith('IHC was performed on')]
assert len(tables)==9 and any('not publicly available' in t for t in selected)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'doi':'10.3390/cancers18111685','primary_source_sha256':sha(primary),
     'public_package_sha256':sha(p.read_bytes()),'nested_package_sha256':sha(nested),'table_workbook_bytes':len(b),'table_workbook_sha256':sha(b),
     'all9_grouped_tables':tables,'primary_eligibility_access_excerpts':selected,'supplement_pdf_sha256':sha(pdf),'supplement_caption_text':txt,
     'source_scope':'219resectedprimarylimb/trunksarcomas1990–2020, no metastaticatdiagnosis/no neoadjuvant;126RNA retainedafter20QCfailed of146extractable. Allpublic9supplementtables+figurePDFtext inspected; no new images/privateclinicaldata accessed. EMC listedonlyamong39Othercombined15subtypes; exactEMCcount/condition/TLSstatus/RNAidentity unresolved.',
     'disposition':'PublicgroupedIHC/RNAclassification priorart evaluated; source individualgenerated/analyzeddatasets explicitlynonpublicprivacy/regulatory. No publicEMCligandexpression orcase-levelTLS/outcome mapping acquired, no EMC-specificprevalence/prognosis inferred. Publication-worthycontrast blocked; no outreach/private request.',
     'all_conditions':'Fourmicrodissectedregions CT/PT/R1/NT described; cannot assignEMC toRNAcohort or transfercombinedcounts. ActualEMC transcript conditions unknown ratherthanexcluded.',
     'compartment':'CD20/CD23/HESwholeblockTLS classification is immune/IHCcontext, not malignantcellprotein/localized ligandRNA or secretion; no EMC-cellresolvedcompartment inferred.'}
(P/'TLS2026-PUBLIC-COVERAGE-OBSERVATIONS.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'tables':len(tables),'private_data_statement':next(t for t in selected if 'not publicly available' in t),'supplement_caption_text':txt,'status':out['disposition']},indent=2))
