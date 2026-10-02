"""Verify packaged file and nested archive hashes without rerunning the analysis."""
import hashlib,io,json,pathlib,zipfile
HERE=pathlib.Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    manifest=json.loads((HERE/'package-manifest.json').read_text())
    for item in manifest['files']:
        p=HERE/item['path'];data=p.read_bytes()
        if len(data)!=item['bytes'] or sha(data)!=item['sha256']:raise ValueError('Package mismatch: '+item['path'])
    spec=json.loads((HERE/'source-archive.json').read_text())
    data=(HERE/'primary-inputs.zip').read_bytes()
    if sha(data)!=spec['sha256']:raise ValueError('Primary archive mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if set(z.namelist())!={x['name'] for x in spec['members']}:raise ValueError('Unexpected archive members')
        for member in spec['members']:
            data=z.read(member['name'])
            if len(data)!=member['bytes'] or sha(data)!=member['sha256']:raise ValueError('Member mismatch: '+member['name'])
    hgnc=json.loads((HERE/'hgnc-source-records-manifest.json').read_text())
    data=(HERE/'hgnc-source-records.zip').read_bytes()
    if sha(data)!=hgnc['sha256']:raise ValueError('HGNC archive mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in hgnc['entries']:
            data=z.read(member['name'])
            if len(data)!=member['bytes'] or sha(data)!=member['sha256']:raise ValueError('HGNC member mismatch')
    print(json.dumps({'status':'passed','package_files':len(manifest['files']),'primary_members':len(spec['members']),'hgnc_members':len(hgnc['entries']),'scope':'Byte integrity only; no scientific rerun'}))
if __name__=='__main__':main()
