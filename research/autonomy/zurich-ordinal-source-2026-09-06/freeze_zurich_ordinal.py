"""Source transcription only. Reads no NCC results and calculates no concordance."""
from pathlib import Path
import csv,json,hashlib,collections,xml.etree.ElementTree as ET
p=Path(__file__).resolve().parent
chem=[('Carfilzomib','high'),('Doxorubicin HCL','good'),('Etoposide','moderate'),('SN-38','moderate'),('Docetaxel','moderate'),('Gemcitabine HCl','moderate'),('Mitomycin C','moderate'),('Fluorouracil','low'),('Topotecan HCl','low'),('Dacarbazine','none'),('Oxaliplatin','none'),('Pemetrexed Disodium Hydrate','none'),('Bleomycin sulfate','none'),('Vinblastine sulfate','none'),('Fludarabine phosphate','none'),('Paclitaxel','none'),('Vinorelbine tartrate','none')]
target=[('PU-H71','good'),('HDM201','good'),('Venetoclax','moderate'),('Derazantinib','moderate'),('Ceritinib','moderate'),('AZD5153','moderate'),('Encorafenib','low'),('Dabrafenib','low'),('Belinostat','low'),('Crizotinib','low'),('Abmaciclib','low'),('Adavosertib','low'),('Ipatasertib','low'),('Trametinib','low'),('Enasidenib','none'),('Niraparib Tosylate','none'),('Erlotinib HCl','none'),('Sorafenib','none'),('WE-822','none'),('Tazemetostat','none'),('Cabozantinib','none'),('Ponatinib','none'),('Selpercatinib','none')]
rows=[]
for panel,values in [('a',chem),('b',target)]:
 for i,(name,band) in enumerate(values,1):
  flag=''
  if name=='Abmaciclib': flag='Printed spelling; possible Abemaciclib identity requires verification; no silent normalization.'
  if name=='WE-822': flag='Printed first letters appear WE; possible VE-822 identity requires verification; no silent normalization.'
  if name=='AZD5153': flag='Last yellow row adjacent to orange boundary; independent colour check required.'
  rows.append(dict(model='USZ20-EMC1',panel=panel,panel_row=i,source_drug_label=name,ordinal_band=band,ambiguity_flag=flag,source_file='13577_2022_818_Fig5_HTML.jpg'))
assert len(rows)==40 and len(chem)==17 and len(target)==23
assert len(set(x['source_drug_label'] for x in rows))==40
with (p/'zurich2023-fig5-ordinal-roster.csv').open('w',newline='',encoding='utf-8') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
root=ET.fromstring((p/'Zurich2023-fulltext.xml').read_bytes())
sections=[]
for el in root.iter('sec'):
 title=el.find('title')
 if title is not None and ''.join(title.itertext())=='Drug screening':
  sections.append({'section':'Drug screening','text':''.join(el.itertext())})
fig5=root.find(".//fig[@id='Fig5']")
sections.append({'section':'Figure 5 legend','text':''.join(fig5.itertext())})
(p/'zurich2023-assay-source-extract.json').write_text(json.dumps(sections,indent=2,ensure_ascii=True),encoding='utf-8')
meta={'status':'frozen source transcription before NCC matching; single-reader, independent validation pending','n_rows':40,'panel_counts':{'a':17,'b':23},'band_counts':dict(collections.Counter(r['ordinal_band'] for r in rows)),'legend_labels':{'high':'High sensitivity (<10% cell viability)','good':'Good sensitivity (11-20% cell viability)','moderate':'Modern sensitivity (21-40% cell viability) [image wording; main legend says moderate]','low':'Low sensitivity (41-70% cell viability)','none':'No sensitivity (>71% cell viability)'},'scope':'Categories only, no inferred numeric AUC, viability or curve point values. Source threshold gaps preserved; categories do not establish common assay concentration. Figure 6 preserved and visually inspected only. No NCC outcome file read by this transcription script.','source_zip_url':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/supplementaryFiles','source_article':'https://link.springer.com/article/10.1007/s13577-022-00818-x','files':[]}
for name in ['Zurich2023-EuropePMC-supplementaryFiles.zip','13577_2022_818_Fig5_HTML.jpg','13577_2022_818_Fig6_HTML.jpg','Zurich2023-fulltext.xml','zurich2023-fig5-ordinal-roster.csv','zurich2023-assay-source-extract.json']:
 b=(p/name).read_bytes();meta['files'].append({'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(p/'zurich2023-ordinal-freeze.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps(meta,indent=2))
