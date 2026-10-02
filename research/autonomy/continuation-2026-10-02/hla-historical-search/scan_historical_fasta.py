"""Cloud-only full scan of the single deposited historical FASTA; stdlib."""
import argparse,hashlib,json,urllib.request
from collections import Counter
from pathlib import Path
URL='https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/04/PXD019643/sp_21_04_2020_decoy.fasta'
EXPECTED_BYTES=27229450
EXPECTED_CHECKSUM='a8f95d9048d4688a0da109ff01e9d796563dad74'
QUERIES=('NMPCVQAQY','QQNMPCVQAQY','SYGQQNMPCVQAQYS','DMPCVQAQY')

def positions(sequence,query):
    start=0
    while True:
        at=sequence.find(query,start)
        if at<0:return
        yield at
        start=at+1

def scan(handle,queries=QUERIES):
    sha1,sha256=hashlib.sha1(),hashlib.sha256()
    total=0;header=None;parts=[];length=0;seen=set();categories=Counter()
    out={q:{'length':len(q),'class_I_length_eligible':8<=len(q)<=12,'class_II_length_eligible':8<=len(q)<=25,'occurrences':Counter(),'matching_records':Counter(),'witnesses':[]} for q in queries}
    def finish():
        if header is None:return
        if not parts:raise ValueError('Empty FASTA record')
        seq=''.join(parts)
        category='decoy' if header.startswith('DECOY_') else 'swissprot_target' if header.startswith('sp|') else 'other_target_header'
        categories[category]+=1
        for q,row in out.items():
            hits=list(positions(seq,q))
            row['occurrences'][category]+=len(hits)
            row['matching_records'][category]+=bool(hits)
            for at in hits:
                if len(row['witnesses'])<20:row['witnesses'].append(dict(header=header,category=category,start_0based=at,sequence=seq[at:at+len(q)]))
    for raw in handle:
        total+=len(raw)
        if total>EXPECTED_BYTES:raise ValueError('Source exceeds pinned byte cap')
        sha1.update(raw);sha256.update(raw)
        line=raw.decode('ascii').strip()
        if not line:continue
        if line.startswith('>'):
            finish();header=line[1:];parts=[];length=0
            accession=header.split()[0] if header else ''
            if not accession or accession in seen:raise ValueError('Empty or duplicate FASTA identifier')
            seen.add(accession)
        else:
            if header is None:raise ValueError('Sequence before header')
            if any(not ('A'<=c<='Z' or c=='*') for c in line):raise ValueError('Invalid sequence alphabet')
            length+=len(line)
            if length>2000000:raise ValueError('Record exceeds bounded memory cap')
            parts.append(line)
    finish()
    for row in out.values():row['witnesses_capped']=sum(row['occurrences'].values())>len(row['witnesses'])
    return dict(bytes=total,sha1=sha1.hexdigest(),sha256=sha256.hexdigest(),records=sum(categories.values()),record_categories=dict(categories),queries=out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    with urllib.request.urlopen(URL,timeout=60) as response:
        if response.status!=200:raise ValueError('Expected full HTTP200 source')
        result=scan(response)
    if result['bytes']!=EXPECTED_BYTES:raise ValueError('Truncated or changed file size')
    if result['sha1']!=EXPECTED_CHECKSUM:raise ValueError('PRIDE checksum does not match computed SHA1; do not interpret result')
    result.update(url=URL,pride_reported_checksum=EXPECTED_CHECKSUM,checksum_interpretation='Computed SHA1 agrees with the 40-hex PRIDE checksum; retrieved metadata does not explicitly name its algorithm.',scope='Deposited canonical search FASTA exact substrings, target and decoy separated by observed DECOY_ and sp| header prefixes; other headers retained separately. Not proof of per-run settings, cryptic database inclusion, presentation or detection.',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
