"""Outcome-blind catalogue crosswalk: reads MOESM4 columns A:C only."""
from pathlib import Path
import csv, hashlib, json
from collections import Counter
from datetime import datetime, timezone
import openpyxl
p=Path(__file__).parent
wb=openpyxl.load_workbook(p/'NCC-MOESM4.xlsx',read_only=True,data_only=True)
catalog={}
for i,row in enumerate(wb['drug list'].iter_rows(min_row=4,max_col=3,values_only=True),4):
    if row[0]: catalog[str(row[0])]={'catalogue_id':str(row[0]),'cas':str(row[1]),'ncc_name':str(row[2]),'sheet':'drug list','excel_row':i}
assert len(catalog)==221
spec=[
('Carfilzomib','nominal_unique','S2853',''),
('Doxorubicin HCL','nominal_unique','S1208','Exclude E2516 free base: source explicitly HCl.'),
('Etoposide','nominal_unique','S1225',''),
('SN-38','absent','','Do not substitute irinotecan: distinct parent and active metabolite; FDA label.'),
('Docetaxel','nominal_unique','S1148',''),
('Gemcitabine HCl','nominal_unique','S1149','Exclude S1714 free base: source explicitly HCl.'),
('Mitomycin C','absent','','Do not substitute mitoxantrone.'),
('Fluorouracil','nominal_unique','S1209',''),
('Topotecan HCl','nominal_unique','S1231','Exclude S9321 free base: source explicitly HCl.'),
('Dacarbazine','nominal_unique','S1221',''),
('Oxaliplatin','absent','','Do not substitute cisplatin or carboplatin.'),
('Pemetrexed Disodium Hydrate','hydrate_unresolved','S1135','Catalogue CAS150399-23-8 is disodium, no hydrate specified; 2.5 hydrate has CAS357166-30-4. Hydration number unknown. Exclude S5971 free acid.'),
('Bleomycin sulfate','nominal_unique','S1214',''),
('Vinblastine sulfate','nominal_unique','S4505',''),
('Fludarabine phosphate','nominal_unique','S1229','Exclude S1491 nonphosphorylated form.'),
('Paclitaxel','nominal_unique','S1150',''),
('Vinorelbine tartrate','nominal_unique','S4269',''),
('PU-H71','absent','','No matching name or alias in catalogue.'),
('HDM201','absent','','Siremadlin / NVP-HDM201 also absent.'),
('Venetoclax','nominal_unique','S8048',''),
('Derazantinib','absent','','ARQ087 also absent.'),
('Ceritinib','form_unresolved','S7083 S4967','Unsuffixed Zurich label; retain base and dihydrochloride candidates.'),
('AZD5153','absent','','No catalogue match.'),
('Encorafenib','nominal_unique','S7108',''),
('Dabrafenib','form_unresolved','S2807 S5069','Unsuffixed Zurich label; retain base and mesylate candidates.'),
('Belinostat','nominal_unique','S1085','NCC name includes synonym PXD101.'),
('Crizotinib','form_unresolved','S1068 S5190','Retain base and HCl candidates; exclude S7505 (S)-crizotinib, a different enantiomer confirmed by supplier FAQ.'),
('Abmaciclib','label_unresolved','S5716 S7158','Printed label preserved. Abemaciclib is only a candidate correction, not established. Supplier identifies S7158/CAS1231930-82-7 as mesylate despite unsuffixed NCC name.'),
('Adavosertib','absent','','MK1775 / AZD1775 also absent.'),
('Ipatasertib','absent','','GDC0068 also absent.'),
('Trametinib','solvate_unresolved','S4484','NCC CAS1187431-43-1 and supplier S4484 identify DMSO solvate; Zurich unsuffixed label does not establish solvate.'),
('Enasidenib','form_unresolved','S8205 S4929','Unsuffixed Zurich label; retain base and mesylate candidates.'),
('Niraparib Tosylate','nominal_unique','S7625','Exclude S2741 free base: source explicitly tosylate.'),
('Erlotinib HCl','nominal_unique','S1023','Exclude S7786 free base: source explicitly HCl.'),
('Sorafenib','form_unresolved','S7397 S1040','Unsuffixed Zurich label; retain base and tosylate candidates.'),
('WE-822','label_unresolved_absent','','Printed label preserved. VE-822 / berzosertib / VX970 / M6620 are unconfirmed candidate corrections and all absent from catalogue.'),
('Tazemetostat','nominal_unique','S7128',''),
('Cabozantinib','form_unresolved','S1119 S4001','Unsuffixed Zurich label; retain base and malate candidates.'),
('Ponatinib','nominal_unique','S1490',''),
('Selpercatinib','absent','','LOXO292 also absent; do not substitute pralsetinib.'),
]
assert len(spec)==40 and len(set(r[0] for r in spec))==40
rows=[]
for idx,(label,status,ids,note) in enumerate(spec,1):
    rows.append({'roster_index':idx,'zurich_label_verbatim':label,'status':status,'strict_nominal_include':status=='nominal_unique','candidates':[catalog[k] for k in ids.split()],'rationale':note})
assert sum(len(r['candidates']) for r in rows)==36
assert sum(r['strict_nominal_include'] for r in rows)==20
out=p/'zurich-ncc-identity-crosswalk.json'
out.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
with (p/'zurich-ncc-identity-crosswalk.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['roster_index','zurich_label_verbatim','status','strict_nominal_include','candidate_ids','candidate_cas','candidate_names','rationale']); w.writeheader()
    for r in rows:
        w.writerow({**{k:v for k,v in r.items() if k!='candidates'},'candidate_ids':' | '.join(c['catalogue_id'] for c in r['candidates']),'candidate_cas':' | '.join(c['cas'] for c in r['candidates']),'candidate_names':' | '.join(c['ncc_name'] for c in r['candidates'])})
def sha(name): return hashlib.sha256((p/name).read_bytes()).hexdigest()
manifest={'frozen_utc':datetime.now(timezone.utc).isoformat(),'scope':'Source-only identity; no NCC response workbook/CSV or IC50 read by this script. No comparison statistic. Prior source recovery agent had previously inspected NCC workbooks; this is outcome-unconditioned, not a claim of personal blinding.','counts':dict(Counter(r['status'] for r in rows)),'strict_nominal_labels':20,'candidate_ncc_rows':36,'caveat':'Nominal matches are label-based, not assay/formulation certification. Zurich lacks CAS/catalogue IDs. No choice among candidate salts permitted based on outcomes.','sha256':{n:sha(n) for n in ['NCC-MOESM4.xlsx','13577_2022_818_Fig5_HTML.jpg','zurich2023-fig5-ordinal-roster.csv','zurich-ncc-identity-crosswalk.json','zurich-ncc-identity-crosswalk.csv','freeze_identity.py']}}
(p/'zurich-ncc-identity-freeze.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
