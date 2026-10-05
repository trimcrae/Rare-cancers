import pathlib,json,hashlib,csv,zipfile,openpyxl,re
P=pathlib.Path(__file__).resolve().parent
hdoc=json.loads((P/'HOFVANDER13-SOURCE-METADATA.json').read_text());h=hdoc['native_specimens'];checks={}
checks['S1hash']=hashlib.sha256(pathlib.Path(hdoc['source_s1']).read_bytes()).hexdigest()==hdoc['sha256']
checks['all13S1']=len(h)==13 and len({r['source_label'] for r in h})==13
checks['all13gradeNA']=all(r['grade']=='NA' for r in h)
checks['all13FusionYes']=all(r['fusion_positive_source']=='Yes' for r in h)
checks['oneLR']=sum(not r['primary_lesion'] for r in h)==1
checks['threeKnownOverlap']=sum(bool(r['known_overlap_comment']) for r in h)==3
checks['nineSubsetNotIndependence']=sum(r['previous_primary_nonoverlap_eligibility'] for r in h)==9
checks['sex9M2F2NA']=[sum(r['sex']==x for r in h) for x in ['M','F','NA']]==[9,2,2]
s=openpyxl.load_workbook(hdoc['source_s1'],read_only=True,data_only=True)['Sheet1'];sr={r[0]:r for r in s.iter_rows(min_row=3,values_only=True) if len(r)>1 and r[1]=='Extraskeletal myxoid chondrosarcoma'}
checks['clinicalFieldsExact']=all((r['age'],r['sex'],r['site'],r['grade'],r['fusion_positive_source'])==(sr[r['source_label']][5],sr[r['source_label']][6],sr[r['source_label']][7],sr[r['source_label']][10],sr[r['source_label']][13]) for r in h)
a=json.loads((P/'AUTHOR-METADATA-INDEPENDENT-REPLAY.json').read_text());checks['authorHash']=hashlib.sha256(pathlib.Path(a['path']).read_bytes()).hexdigest()==a['sha256'];raw=list(csv.DictReader(pathlib.Path(a['path']).open(),delimiter='\t'));raw=[r for r in raw if r['Diagnosis']=='Extraskeletal myxoid chondrosarcoma'];checks['author13IDs']=len(raw)==13 and {r['lab_no'].removesuffix('_ESMCS') for r in raw}=={r['sample_id'] for r in h}
checks['authorGradeYear']=all(next(x for x in h if x['sample_id']==r['lab_no'].removesuffix('_ESMCS'))['sequencing_year']==r['sequencing_year'] and r['Grade']=='NA' for r in raw)
checks['noDriverNamedGeneTokens']=not any(re.findall(r'\b(?:EWSR1|TAF15|FUS|TFG|TCF12|HSPA8|PGR|LMNB2|NR4A3)\b',r['Driver'],re.I) for r in raw)
ad=json.loads((P/'ARRAY16-SOURCE-METADATA.json').read_text());checks['arrayCounts6and10']=[len(r['conditions']) for r in ad['sources']]==[6,10]
for ss in ad['sources']:
 z=zipfile.ZipFile(ss['source_zip']);checks[ss['member']+'_hash']=hashlib.sha256(z.read(ss['member'])).hexdigest()==ss['member_sha256'];orig={r['gsm']:r['fields'] for r in json.loads(z.read(ss['member']))}
 checks[ss['member']+'_metadataProjection']=all(all(v==orig[r['gsm']][k] for k,v in r['fields'].items() if k!='!Sample_description') for r in ss['conditions'])
checks['noExpressionMatrixValuesExported']=all(not any(k in r for k in ['TPM','expression','values','counts','effect','pvalue']) for r in h+a['all13'])
g=json.loads((P/'GSE28866-FOUR-NATIVE-CONDITIONS.json').read_text());checks['GSE4headerLabels']=len(g['conditions'])==4 and {r['released_header'] for r in g['conditions']}=={'EMC_STT5525','EMC_STT5526','EMC_STT5527','EMC_STT5592'}
checks['33sourceConditionsNot33donors']=len(h)+sum(len(s['conditions']) for s in ad['sources'])+len(g['conditions'])==33
checks['numericalStageOff']=a['numerical_stage'] is False
assert all(checks.values()),checks
print(json.dumps({'pass':True,'checks':len(checks),'details':checks,'new_subgroup_values':0,'new_raw_bytes':0,'network_requests':0}))
