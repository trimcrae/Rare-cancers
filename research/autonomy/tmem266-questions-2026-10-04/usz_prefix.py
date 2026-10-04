"""Frozen 15MB-per-mate exact-anchor pilot; no raw-read persistence."""
import urllib.request,xml.etree.ElementTree as E,zlib,hashlib,json,re,collections
from pathlib import Path
CAP=15000000
url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_152335.3,XM_005254160.3&rettype=gb&retmode=xml'
with urllib.request.urlopen(url,timeout=40) as h:ref=h.read(200001)
assert len(ref)<=200000
root=E.fromstring(ref);seqs={t.findtext('GBSeq_accession-version'):t.findtext('GBSeq_sequence').upper() for t in root.findall('GBSeq')}
rc=lambda s:s.translate(str.maketrans('ACGT','TGCA'))[::-1]
defs=[('alternative_skip106','XM_005254160.3',476),('canonical_inclusion_boundary','NM_152335.3',404),('canonical_exon4_exon5','NM_152335.3',510)]
events=[{'event':name,'reference':acc,'seam0':p,'anchor':seqs[acc][p-20:p+20]} for name,acc,p in defs]
assert all(len(e['anchor'])==40 for e in events)
assert events[0]['anchor'] not in seqs['NM_152335.3'] and all(e['anchor'] not in seqs['XM_005254160.3'] for e in events[1:])
results=[];allhits=[]
for mate,expected_size in [(1,1471025007),(2,1492531906)]:
    u=f'https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR339/095/SRR33903995/SRR33903995_{mate}.fastq.gz'
    req=urllib.request.Request(u,headers={'Range':f'bytes=0-{CAP-1}','Accept-Encoding':'identity','User-Agent':'EMCResearchSequenceAudit/1.0'})
    sha=hashlib.sha256();readn=0;decoded=0;nrec=0;pending=b'';linebuf=[];hist=collections.Counter();de=zlib.decompressobj(31);hits=[]
    with urllib.request.urlopen(req,timeout=60) as h:
        status=h.status;crange=h.headers.get('Content-Range');assert status==206 and crange==f'bytes 0-{CAP-1}/{expected_size}',(status,crange)
        while readn<CAP:
            chunk=h.read(min(65536,CAP-readn))
            if not chunk:break
            sha.update(chunk);readn+=len(chunk);out=de.decompress(chunk);decoded+=len(out);pending+=out
            while de.unused_data:
                tail=de.unused_data;de=zlib.decompressobj(31);out=de.decompress(tail);decoded+=len(out);pending+=out
            lines=pending.split(b'\n');pending=lines.pop();linebuf.extend(lines);stop=(len(linebuf)//4)*4
            for k in range(0,stop,4):
                head,s,plus,q=[x.rstrip(b'\r') for x in linebuf[k:k+4]]
                assert head.startswith(b'@') and plus.startswith(b'+') and len(s)==len(q)
                nrec+=1;hist[len(s)]+=1;ss=s.decode();qq=q.decode();fid=re.sub(r'/[12]$','',head.decode().split()[0][1:])
                for strand,os,oq in [('+',ss,qq),('-',rc(ss),qq[::-1])]:
                    for e in events:
                        pos=os.find(e['anchor'])
                        while pos>=0:
                            quals=[ord(ch)-33 for ch in oq[pos:pos+40]]
                            hits.append({'event':e['event'],'mate':mate,'record_index1':nrec,'read_id':head.decode()[1:],'fragment_id':fid,'orientation':strand,'anchor_start_in_oriented_read0':pos,'oriented_read_start_in_reference0':e['seam0']-20-pos,'minimum_anchor_Phred':min(quals),'qualifies_Q20':min(quals)>=20,'read_sequence':ss,'read_quality':qq})
                            pos=os.find(e['anchor'],pos+1)
            linebuf=linebuf[stop:]
    assert readn==CAP,(mate,readn)
    r={'mate':mate,'url':u,'status':status,'content_range':crange,'compressed_prefix_bytes':readn,'prefix_sha256':sha.hexdigest(),'decompressed_bytes':decoded,'complete_records':nrec,'read_length_counts':dict(hist),'incomplete_tail_lines':len(linebuf),'incomplete_tail_bytes':len(pending),'matches':hits}
    results.append(r);allhits.extend(hits)
summary=[]
for e in events:
    hh=[h for h in allhits if h['event']==e['event']];valid=[h for h in hh if h['qualifies_Q20']]
    summary.append({'event':e['event'],'matched_records':len(hh),'qualifying_Q20_records':len(valid),'fragments':len(set(h['fragment_id'] for h in valid)),'oriented_starts':sorted(set(h['oriented_read_start_in_reference0'] for h in valid))})
out={'reference':{'url':url,'bytes':len(ref),'sha256':hashlib.sha256(ref).hexdigest()},'events':events,'mates':results,'total_complete_records':sum(r['complete_records'] for r in results),'summary':summary,'scope':'fixed compressed prefixes; no absence, isoform ratio or full-length inference'}
Path(__file__).with_name('usz-prefix-replay.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'complete_records':out['total_complete_records'],'summary':summary},indent=2))
