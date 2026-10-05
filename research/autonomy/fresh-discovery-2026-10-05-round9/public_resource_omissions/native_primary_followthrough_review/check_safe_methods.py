"""Inspect BioC METHODS text only. Never access TABLE infon XML or endpoint text."""
from pathlib import Path
from lxml import etree
import hashlib,json,re,datetime,sys
P=Path(__file__).resolve().parent
R=Path('/workspace/emc-r6-radiotherapy/research/autonomy/fresh-discovery-2026-10-05-round9/endocrine/native_primary_followthrough/raw-cache')
inputs=[('PMC9481662-bioc.xml','c88103d60bc3fdbd27db5aca58d45915434bd1a69535a1fa7a9edeed26d029d0'),('PMC4847145-bioc.xml','5fe99bec350b655ccfcd021aaca8299004f06d24d077caf8f75cb99a64872d02')]
methods={};bindings=[];passage_counts={}
for name,sha in inputs:
 f=R/name;b=f.read_bytes();assert hashlib.sha256(b).hexdigest()==sha
 bindings.append({'path':str(f),'bytes':len(b),'sha256':sha})
 r=etree.parse(str(f));texts=[];categories={}
 for passage in r.findall('.//passage'):
  safe={i.get('key'):i.text for i in passage.findall('./infon') if i.get('key') in ['type','section_type']}
  key=str((safe.get('section_type'),safe.get('type')));categories[key]=categories.get(key,0)+1
  if safe.get('section_type')=='METHODS' and safe.get('type')=='paragraph':
   text=passage.findtext('./text','')
   for sentence in re.split(r'(?<=[.!?])\s+',text):
    # Exact FAP is excluded; GFAP is a different published diagnostic marker.
    if not re.search(r'promoter|fusion|rearrang|glycosyl|glycan|\bHLA\b|NY.?ESO|\bFAP\b',sentence,re.I):texts.append(sentence)
 methods[name]=' '.join(texts);passage_counts[name]=categories
m=methods['PMC9481662-bioc.xml'];old=methods['PMC4847145-bioc.xml']
assert 'extraskeletal myxoid chondrosarcoma (15 total, 3 TMA)' in m
assert 'single cores' in m and '0.6 to 2.0 mm' in m
assert 'primary tumor and recurrence' in m and 'chondromyxoid fibroma' in m
assert 'three cases each of extraskeletal myxoid chondrosarcoma' in m
assert 'triplicate' in m and 'comparative Ct' in m
assert 'cerebellum' in m and 'negative control' in m
assert '16 extraskeletal myxoid chondrosarcomas' in old
assert '1 representative section per case' in old and '4-mm thick' in old
assert all(x in old for x in ['D2-40','S100','pankeratin','epithelial membrane antigen','brachyury','glial fibrillary acidic protein'])
assert '<5% cells stained' in old and 'mean extent' in old
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bindings':bindings,'safe_reader':'Only infon type/section_type values and METHODS paragraph text. TABLE/RESULTS/FIG/ABSTRACT text and infon XML never accessed by this checker.','method_prerequisite_checks':{'GRM1_IHC_materials':15,'GRM1_TMA_materials':3,'GRM1_whole_section_materials':12,'GRM1_prior_qPCR_EMC_controls':3,'qPCR_technical_triplicates':True,'CMF_only_recurrence_pairs_not_EMC':True,'older_EMC_materials':16,'older_panel_markers':6,'older_one_representative_section_per_case':True,'literal_older_section_unit':'4-mm; unresolved source conversion/unit, not corrected'},'passage_type_counts':passage_counts,'marker_outcome_values_inspected':0,'passed':True,'scope_limit':'Counts are study-material/assay conditions, not distinct donors or same-case pairing. Outcome blindness applies to this independent read only; owner accidental exposure is preserved separately.'}
if '--write' in sys.argv:(P/'SAFE-METHOD-VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'native_assay_cohorts':[15,3,16],'biological_outcomes_read':0}))
