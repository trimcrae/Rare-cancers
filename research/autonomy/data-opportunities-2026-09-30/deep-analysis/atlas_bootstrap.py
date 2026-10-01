import urllib.request,hashlib,json
from pathlib import Path
base=Path('research/autonomy/atlas-hofvander-source-2026-09-06');base.mkdir(parents=True,exist_ok=True)
urlbase='https://raw.githubusercontent.com/JakobHofvander/Transcriptomic_subgroups_in_soft_tissue_tumors_correlate_with_morphologic_subtype_genomic_features/984a5eddeb3d616dea2f404ed4032c8f78fba60e/source_data/'
records=[]
for name,sha,size in [('tpm_matrix.tsv','b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3',65407718),('meta_data.txt','e0bbc6f2e8c062cb6733e68e1c148248775f2e53c6bce7c61b70bb79c89777bf',90300)]:
    with urllib.request.urlopen(urlbase+name,timeout=120) as r:b=r.read(size+1);status=r.status
    assert status==200 and len(b)==size and hashlib.sha256(b).hexdigest()==sha,name
    (base/name).write_bytes(b);records.append({'file':name,'url':urlbase+name,'bytes':len(b),'sha256':sha,'http_status':status})
    if name=='tpm_matrix.tsv':
        hdr=b.split(b'\n',1)[0].decode().rstrip('\r').split('\t')
        m=json.loads(Path('research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())
        print(json.dumps({'first_column':hdr[0],'first10_sample_columns':hdr[1:11],'short_id_matches':sum(r['sample_id'] in hdr[1:] for r in m['samples']),'label_matches':sum(r['source_label'] in hdr[1:] for r in m['samples'])}))
        assert hdr[0]=='symbol' and all(r['sample_id'] in hdr[1:] for r in m['samples'])
out=Path('campaign-output/atlas-bootstrap.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(records,indent=2)+'\n')
print('EMC_ATLAS_BOOTSTRAP_BEGIN');print(json.dumps(records));print('EMC_ATLAS_BOOTSTRAP_END')
