import pathlib,json,hashlib,datetime,xml.etree.ElementTree as E,zipfile
D=pathlib.Path(__file__).resolve().parent

def tables(n):
 r=E.parse(D/n).getroot()
 return [[[' '.join(c.itertext()) for c in row] for row in t.findall('.//tr')] for t in r.findall('.//table-wrap')]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(D/'ferdinandus2022-ts1.docx') as z:r=E.fromstring(z.read('word/document.xml'))
fr=[[' '.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in row.findall('w:tc',ns)] for row in r.findall('.//w:tr',ns)][1:]
assert [x[0] for x in fr]==[str(x) for x in range(1,22)]
assert sum(x[3]=='Sarcoma' for x in fr)==16
assert fr[9][4]=='Chondrosarcoma (femur/pelvic)'
main=' '.join(E.parse(D/'ferdinandus2022.xml').getroot().itertext())
assert 'conventional chondrosarcoma' in main
nr=tables('novruzov2026.xml')[0][1:];assert len(nr)==19
sts=[x for x in nr if x[0].startswith('STS-')];assert [x[0] for x in sts]==['STS-'+str(i) for i in range(1,7)]
kr=tables('koerber2021.xml')[1];categoryrows=kr[1:10]
# The third data row inherits the Liposarcoma label via original XML rowspan.
kcounts=[int(x[0]) if x[0].isdigit() else int(x[1]) for x in categoryrows];assert sum(kcounts)==15
wr=tables('dynamic2021.xml')[0][1:];assert len(wr)==6
assert [x[-1] for x in wr].count('Lung Ca.')==3 and [x[-1] for x in wr].count('No tumor')==3
ex=tables('experience2024.xml')[0];cats=ex[15:27];assert len(cats)==12
assert sum(int(x[1].split(',')[0]) for x in cats)==48
aliases=['extraskeletal','nr4a3','myxoid chondrosarcoma','chondrosarcome myxoide']
labelstrings=[x[4] for x in fr]+[x[0] for x in nr]+[x[0] for x in categoryrows]+[x[-1] for x in wr]+[x[0] for x in cats]
assert not any(a in s.lower() for a in aliases for s in labelstrings)
o={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS source identity extraction; not proof all labels exclude EMC','counts':{'Ferdinandus_rows':21,'Ferdinandus_sarcoma':16,'Novruzov_rows':19,'Novruzov_generic_STS':6,'Koerber_category_n':15,'Wang_rows':6,'Diagnostics2025_categories':12,'Diagnostics2025_n':48},'authentic_EMC_paired_measurements_analyzed':0,'inferential_tests_run':0,'unresolved_explicit':['Koerber sarcomaNOS','Ferdinandus cases2 and11','Novruzov STS1..6','all separatelylisted inaccessible/unexaminedcoverage'], 'source_hashes':{n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['ferdinandus2022-ts1.docx','ferdinandus2022.xml','novruzov2026.xml','koerber2021.xml','dynamic2021.xml','experience2024.xml']}}
(D/'eligibility-validation.json').write_text(json.dumps(o,indent=2),encoding='utf-8');print(json.dumps({k:o[k] for k in ['status','counts','authentic_EMC_paired_measurements_analyzed']},indent=2))
