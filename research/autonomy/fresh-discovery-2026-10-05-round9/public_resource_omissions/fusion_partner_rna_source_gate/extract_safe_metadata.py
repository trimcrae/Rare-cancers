"""Extract identity/confounder fields only; never open expression matrices."""
import csv, hashlib, json, pathlib, re, collections
ROOT=pathlib.Path('/workspace/Rare-cancers/research/autonomy')
HERE=pathlib.Path(__file__).resolve().parent
import openpyxl

def bind(p):
 b=pathlib.Path(p).read_bytes()
 return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def emit(n,d): (HERE/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
manifest_path=ROOT/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
s1_path=ROOT/'atlas-hofvander-source-2026-09-06/ccr-25-3740_supplementary_table_s1_suppts1.xlsx'
m=json.loads(manifest_path.read_text());samples=[r for r in m['samples'] if r['diagnosis']=='Extraskeletal myxoid chondrosarcoma']
wb=openpyxl.load_workbook(s1_path,read_only=True,data_only=True);ws=wb.worksheets[0]
rows=[]
for r in samples:
 cells=next(ws.iter_rows(min_row=r['s1_row'],max_row=r['s1_row'],values_only=True))
 # Explicit whitelist: identity, age, sex, site, size, depth, grade, lesion, binary fusion.
 d={k:r.get(k) for k in ['sample_id','source_label','s1_row','sequencing_year','specimen_exception','known_overlap','primary_lesion','role','exclusion_reason']}
 d.update(author_diagnosis=cells[1],age=cells[5],sex=cells[6],site=cells[7],size=cells[8],depth=cells[9],grade=cells[10],lesion=cells[12],fusion_present=cells[13],direct_partner_in_s1=None,patient_independence='Not established from lab identifier or analysis patient_group')
 assert str(cells[0])==r['source_label'];rows.append(d)
wb.close()
author_path=HERE/'raw-cache'/'author-meta-data.txt'
author=list(csv.DictReader(author_path.open(),delimiter='\t'))
sel=[r for r in author if r['Diagnosis']=='Extraskeletal myxoid chondrosarcoma']
# Examine only diagnostic partner-pair strings in the author Driver label field.
# Do not project Driver contents, coordinates, chromosome descriptions or mechanisms.
pattern=re.compile(r'\b(EWSR1|TAF15|TCF12|FUS|TFG)\s*(?:::|[-_/])\s*NR4A3\b',re.I)
projection=[]
for r in sel:
 matches=pattern.findall(r.get('Driver',''))
 projection.append({'sample_id':r['lab_no'],'author_diagnosis':r['Diagnosis'],'grade':r['Grade'],'sequencing_year':r['sequencing_year'],'explicit_partner_pair_tokens':matches})
assert {r['sample_id'] for r in rows}=={r['sample_id'] for r in projection}
assert len(rows)==len(sel)==13
assert all(r['fusion_present']=='Yes' for r in rows)
assert all(r['grade']=='NA' for r in rows+projection)
assert all(not r['explicit_partner_pair_tokens'] for r in projection)
emit('ALL13-HOFVANDER-SAFE-ROSTER.json',{'source_bindings':[bind(manifest_path),bind(s1_path),bind(author_path)],'source_cases':13,'sex_counts':dict(collections.Counter(r['sex'] for r in rows)),'primary_conditions':12,'local_recurrence_conditions':1,'known_cross_study_overlap_conditions':3,'primary_after_known_exclusions':9,'nine_independent_donors_proven':False,'rows':rows,'author_release_projection':projection,'partner_resolution':'S1 and v1.0.1 release do not supply directly usable partner labels; this is not proof labels are unavailable elsewhere.','historical_partial_link':'R7 complete16 diagnostic source table contains author EMC168/97 EWSR1-NR4A3. Normalized168-97 is a candidate historical identity link, with known MDB9736:4 reuse. No opposite-partner comparator exists from this singleton and no independent donor is added.'})
emit('METADATA-CHECK.json',{'all13_s1_and_release_ids_match':True,'source_fusion_present_13_yes':True,'grade_unknown_13':True,'source_partner_pair_tokens_found':0,'expression_files_opened':0,'new_subgroup_outputs':0,'denied_mechanistic_fields_used':False,'unit_rule':'Conditions are retained separately; missing partner never equals EWSR1.'})
