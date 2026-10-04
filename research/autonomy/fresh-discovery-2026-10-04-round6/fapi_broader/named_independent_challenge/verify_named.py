#!/usr/bin/env python3
"""Independent read-only source/accountability check against exact named packet."""
import argparse,collections,datetime,hashlib,json,pathlib,re,subprocess,zipfile
from lxml import html,etree
ROOT=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'\s+',' ',s).strip()
parser=argparse.ArgumentParser();parser.add_argument('--named-packet',type=pathlib.Path,required=True);args=parser.parse_args();P=args.named_packet
freeze=P/'EVIDENCE-FREEZE-02.json'
assert sha(freeze)=='89af5884b7b861d828aaa985dfd0d8e28c210b5c45ad8985f779be6d243051da'
bound=json.loads(freeze.read_text())
for x in bound['files']:assert sha(P/x['path'])==x['sha256'],x['path']
source_pins=[]
for name in ['kessler-supp.pdf','lanzafame-supp.pdf','pabst-appendix.pdf','lanzafame-table1.html']+[f'kessler-reading-{i}.xlsx' for i in range(1,5)]:source_pins.append({'path':'raw-cache/'+name,'sha256':sha(P/'raw-cache'/name)})
texts={n:subprocess.check_output(['pdftotext','-layout',str(P/'raw-cache'/n),'-'],text=True) for n in ['kessler-supp.pdf','lanzafame-supp.pdf','pabst-appendix.pdf']}
# Independently account printed Kessler counts, not the analysis script constants.
ks=texts['kessler-supp.pdf'];ks=ks[:ks.index('Supplemental Table 2.')]
krows=[]
for line in ks.splitlines():
 m=re.fullmatch(r'\s+(.+?)\s{2,}(\d+)\s*\([0-9.]+%\)\s*',line)
 if m:krows.append({'label':norm(m.group(1)),'n':int(m.group(2))})
assert len(krows)==18 and sum(r['n'] for r in krows)==47
t=html.fromstring((P/'raw-cache/lanzafame-table1.html').read_bytes(),parser=html.HTMLParser(encoding='utf-8'))
rows=[[norm(c.text_content()) for c in tr.xpath('./th|./td')] for tr in t.xpath('//table//tr')]
group=None;lg=collections.defaultdict(list)
for row in rows:
 if row[0] in ['BS','STS']:group=row[0];continue
 if row[0]=='Grading':group=None
 if group:lg[group].append({'label':row[0],'n':int(re.match(r'\d+',row[1]).group())})
assert sum(x['n'] for x in lg['BS'])==65 and sum(x['n'] for x in lg['STS'])==135
hist=json.loads((P/'HISTOLOGY-COVERAGE.json').read_text());sums=collections.defaultdict(int)
for row in hist:sums[(row['source'],row['location'])]+=row['reported_donors']
assert sums[('Lanzafame2024','SupplementalTable3 otherSTS41')]==41
assert sums[('Lanzafame2024','SupplementalTable3 otherbone15')]==15
assert sum(v for (s,l),v in sums.items() if s=='Lanzafame2024')==200
ps=texts['pabst-appendix.pdf'];s3=ps[ps.index('Table S3.'):ps.index('Table S4.')]
pco=json.loads((P/'PABST-COHORT-COVERAGE.json').read_text());macros=pco['complete_macro155']
for row in macros:
 pattern=norm(row['source_label'])+' '+str(row['donors'])+' '
 assert any(norm(line).startswith(pattern) for line in s3.splitlines()),row
assert sum(row['donors'] for row in macros)==155
assert sum(v for (s,l),v in sums.items() if s=='Pabst2025')==28
assert not re.search(r'extraskeletal|NR4A3|\bEMC\b',s3,re.I)
s8=ps[ps.index('Table S8.'):ps.index('Table S9.')]
assert 'No 7 and 8, and no 21 and 22 were each from the same participant' in s8
assert len([line for line in s8.splitlines() if re.match(r'^\s*\d+\s{2,}',line)])==24
obs=json.loads((P/'OBSERVATION-COVERAGE.json').read_text());pobs={r['id']:r for r in obs if r['source']=='Pabst2025'}
for i in [7,8,9,23]:
 row=pobs[f'TableS8 row{i}'];assert row['source_FAPI_PET_SUVpeak']=='No uptake' and not row['authenticated_EMC']
 assert row['source_FDG'].startswith('not supplied')
assert 'Known sameparticipant' in pobs['TableS8 row7']['donor_overlap']
assert 'Known sameparticipant' in pobs['TableS8 row8']['donor_overlap']
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};wbs=[]
for i in range(1,5):
 with zipfile.ZipFile(P/'raw-cache'/f'kessler-reading-{i}.xlsx') as z:
  strings=[''.join(x.itertext()) for x in etree.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
  ids=set(x for x in strings if re.fullmatch(r'FAPI_STS_\d+',x))
  assert not any(re.search(r'extraskeletal|chondrosarcoma|NR4A3|histolog|diagnos|scan.*date|date.*scan',x,re.I) for x in strings)
  wb=etree.fromstring(z.read('xl/workbook.xml'));sheets=[x.attrib for x in wb.findall('.//s:sheet',ns)]
  assert len(sheets)==1 and not any('external' in n.lower() for n in z.namelist())
  wbs.append({'file':f'kessler-reading-{i}.xlsx','n_donor_IDs':len(ids),'sheet_names':[x['name'] for x in sheets],'no_public_identity_date_crosswalk':True})
assert [x['n_donor_IDs'] for x in wbs]==[47,43,47,43]
results=json.loads((P/'RESULTS.json').read_text());assert results['authenticated_EMC_donors']==0 and results['computed_EMC_ratios']==0
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewed_freeze_sha256':sha(freeze),'reviewed_files':bound['files'],'source_pins':source_pins,'independent_Kessler_printed_roster':krows,'independent_Lanzafame_main_groups':dict(lg),'independent_Kessler_workbook_checks':wbs,'source_accountability':'47 Kessler; 200 Lanzafame (144 main leaves plus 41+15 expanded Others); 155 Pabst macros including nested 28sarcoma and Other11; no double counting','Pabst_adverse_conditions':'All relevant rows7/8/9/23 retained as FAPI No uptake, no imputed numeric0 and no FDG value;7/8 knownsame donor by sourcefootnote','source_retrievals':0,'checks_passed':True,'meaning':'Supports bounded source eligibility and decision, not EMC biological absence or efficacy. Generic diagnoses and unavailable crosswalks remain explicit.'}
(ROOT/'REVIEW-CHECKS.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('PASS: exact final bindings and independent source accountability/identity/condition checks.')
