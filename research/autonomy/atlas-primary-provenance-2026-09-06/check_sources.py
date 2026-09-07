"""Reproduce metadata-only counts and verify downloaded source hashes; no expression analysis."""
from pathlib import Path
import gzip, hashlib, json, re, datetime, csv, argparse
P = Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-dir',type=Path,help='External directory for raw archives; explicit files here take precedence over bundled sources.')
parser.add_argument('--output-dir',type=Path,help='New output directory only. Omit for read-only comparison against saved evidence.')
args=parser.parse_args()
if args.output_dir:
    args.output_dir=args.output_dir.resolve()
    args.output_dir.mkdir(parents=True,exist_ok=False)
def source(name):
    if args.source_dir and (args.source_dir/name).is_file(): return args.source_dir/name
    f=P/name
    if not f.is_file(): raise FileNotFoundError(f'Missing {name}; supply --source-dir with hash-verified raw archives (see excluded-raw-manifest.json)')
    return f
def dump(name,obj):
    if args.output_dir: (args.output_dir/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
records=json.loads((P/'retrievals.json').read_text())
checks=[]
for r in records:
    if 'sha256' in r:
        actual=hashlib.sha256(source(r['file']).read_bytes()).hexdigest()
        checks.append({'check':'retrieval_sha256','file':r['file'],'pass':actual==r['sha256']})
        if actual != r['sha256']: raise ValueError(f"Source hash mismatch: {r['file']}")
samples=[]; platforms=[]
for accession in ['GSE4303','GSE24369']:
    lines=[]
    with gzip.open(source(accession+'.soft.gz'),'rt',encoding='utf-8') as f:
        for line in f:
            if line.startswith(('^','!','#')): lines.append(line)
    metadata=''.join(lines)
    checks.append({'check':'saved_metadata_agrees','file':accession+'-metadata.txt','pass':(P/(accession+'-metadata.txt')).read_text(encoding='utf-8')==metadata})
    if args.output_dir: (args.output_dir/(accession+'-metadata.txt')).write_text(metadata,encoding='utf-8')
    for block in re.split(r'(?=\^SAMPLE = )',metadata)[1:]:
        attrs={}
        for l in block.splitlines():
            if ' = ' in l:
                k,v=l.split(' = ',1);attrs.setdefault(k,[]).append(v)
        attrs['source_series']=[accession]
        samples.append(attrs)
    if accession=='GSE4303':
        for block in re.split(r'(?=\^PLATFORM = )',metadata)[1:]:
            block=block.split('^SAMPLE')[0];attrs={}
            for l in block.splitlines():
                if l.startswith(('^PLATFORM','!Platform_')) and ' = ' in l:
                    k,v=l.split(' = ',1);attrs.setdefault(k,[]).append(v)
            platforms.append(attrs)
s4303=[s for s in samples if s['source_series']==['GSE4303']]
gpl=[s for s in s4303 if s['!Sample_platform_id']==['GPL3290']]
emc=[s for s in gpl if 'myxoid' in s['!Sample_title'][0].lower()]
dfsp=[s for s in gpl if 'DFSP' in s['!Sample_title'][0]]
gist=[s for s in gpl if 'GIST' in s['!Sample_title'][0]]
with gzip.open(P/'E-GEOD-4303-GPL3290.matrix.gz','rt') as f:
    matrix_ids=[]
    for line in f:
        if line.startswith('!Sample_geo_accession'):
            matrix_ids=next(csv.reader([line],delimiter='\t'))[1:];break
checks += [
 {'check':'GSE4303_36_records','pass':len(s4303)==36},
 {'check':'GPL3290_10EMC_3DFSP_3GIST','pass':(len(emc),len(dfsp),len(gist))==(10,3,3)},
 {'check':'all36_RNA_Cy3ref_Cy5tumor','pass':all(s['!Sample_type']==['RNA'] and s['!Sample_label_ch1']==['Cy3'] and s['!Sample_label_ch2']==['Cy5'] for s in s4303)},
 {'check':'matrix_family_accessions_agree','pass':set(matrix_ids)=={s['^SAMPLE'][0] for s in gpl}},
 {'check':'2017_table_figshare_md5','pass':hashlib.md5((P/'2017-controls-table.xlsx').read_bytes()).hexdigest()=='a66aa9434f28386115d819ddf5f4a142'},
 {'check':'2011_supplement_figshare_md5','pass':hashlib.md5((P/'ccr-supplement.pdf').read_bytes()).hexdigest()=='da9aa69b8fdffd13d02838538232085c'}]
generated={'samples':samples,'platforms':platforms,'candidate_emc':[s['^SAMPLE'][0] for s in emc],'candidate_dfsp':[s['^SAMPLE'][0] for s in dfsp]}
checks.append({'check':'saved_gsm_platform_evidence_agrees','pass':generated==json.loads((P/'gsm-platform-evidence.json').read_text(encoding='utf-8'))})
dump('gsm-platform-evidence.json',generated)
dump('source-checks.json',{'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_pass':all(x['pass'] for x in checks),'scope':'hashes, metadata counts, channel fields, accession agreement; no expression values analyzed'})
assert all(x['pass'] for x in checks), checks
print(json.dumps({'checks':len(checks),'all_pass':all(x['pass'] for x in checks),'mode':'read_only_compare' if not args.output_dir else 'compare_and_write_new_directory','samples':len(s4303),'candidate_emc':len(emc),'candidate_dfsp':len(dfsp)}))
