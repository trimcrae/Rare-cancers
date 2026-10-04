"""Published USZ23_EMC3 selected transcript estimates and versioned models."""
import csv, gzip, hashlib, io, json, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE=Path(__file__).resolve().parent
IDS={'NM_152335','XM_005254160','XM_017021915','XM_047432151',
     'XM_054377283','XM_054377284','XM_054377285'}
URL='https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM9037nnn/GSM9037837/suppl/GSM9037837_USZ23_EMC3.RefSeq.quant.sf.gz'
REF='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_152335.3,XM_005254160.3,XM_017021915.1&rettype=gb&retmode=xml'
TEMPO='GTGGTGACCATACACACAGCTGGCTCTGGGACACCGCTGTCACTGCTGGG'

def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (compatible; EMCResearch/1.0)','Accept-Encoding':'identity'})
    parts=[]; n=0
    with urllib.request.urlopen(req,timeout=45) as r:
        while True:
            b=r.read(65536)
            if not b:break
            parts.append(b);n+=len(b);assert n<=15000000
    return b''.join(parts)

def rc(s):return s.translate(str.maketrans('ACGT','TGCA'))[::-1]

def main():
    b=fetch(URL)
    assert len(b)==1821812 and hashlib.sha256(b).hexdigest()=='d49822e6ca79a18c186b00c4faa4087b8582bbb72c0be218fcea2e997565507f'
    t=gzip.decompress(b); reader=csv.DictReader(io.StringIO(t.decode()),delimiter='\t')
    assert reader.fieldnames==['Name','Length','EffectiveLength','TPM','NumReads']
    rows=list(reader); selected=[r for r in rows if r['Name'].split('.')[0] in IDS]
    raw=fetch(REF); models=[]
    with (BASE.parent/'tmem266-prepublication-2026-10-03/probe-map.csv').open() as f: probes=list(csv.DictReader(f))
    for g in ET.fromstring(raw).findall('GBSeq'):
        s=g.findtext('GBSeq_sequence').upper(); cds=[]
        for f in g.findall('.//GBFeature'):
            if f.findtext('GBFeature_key')=='CDS':
                quals={q.findtext('GBQualifier_name'):q.findtext('GBQualifier_value') for q in f.findall('.//GBQualifier')}
                cds.append({'location':f.findtext('GBFeature_location'),'translation_length':len(quals.get('translation','')),'protein_id':quals.get('protein_id')})
        mapped=[]
        for p in probes:
            for strand,q in [('direct',p['sequence']),('reverse_complement',rc(p['sequence']))]:
                at=s.find(q)
                if at>=0:mapped.append({'probe_id':p['physical_probe_id'],'start0':at,'end0':at+len(q),'orientation':strand})
        tempo=[{'orientation':strand,'start0':s.find(q),'end0':s.find(q)+len(q)} for strand,q in [('direct',TEMPO),('reverse_complement',rc(TEMPO))] if s.find(q)>=0]
        models.append({'accession':g.findtext('GBSeq_accession-version'),'length':len(s),'CDS':cds,'array_probe_matches':mapped,'tempo_matches':tempo})
    out={'url':URL,'file_bytes':len(b),'file_sha256':hashlib.sha256(b).hexdigest(),
         'text_sha256':hashlib.sha256(t).hexdigest(),'n_rows':len(rows),'fixed_ids':sorted(IDS),'target_rows':selected,
         'missing_from_index':sorted(IDS-{r['Name'].split('.')[0] for r in selected}),
         'summed_TPM':sum(float(r['TPM']) for r in selected),
         'summed_estimated_NumReads':sum(float(r['NumReads']) for r in selected),
         'reference_receipt':{'url':REF,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'models':models,
         'limits':'Single cultured model; transcript allocation estimates with no equivalence-class uncertainty. No full-length molecule, isoform predominance, translation, tissue localization or cross-platform abundance conclusion.'}
    (BASE/'usz-quant.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'selected':selected,'TPM_sum':out['summed_TPM'],'models':[{k:v for k,v in m.items() if k not in ['array_probe_matches']} for m in models]},indent=2))

if __name__=='__main__':main()
