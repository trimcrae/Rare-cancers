"""Replay source-identity/approval and current transcript-association checks.

Read-only. Manual primary-study interpretation remains in the hashed review;
this script does not label diagnoses or clinical benefit automatically.
"""
import argparse,hashlib,json,pathlib
from lxml import etree
HERE=pathlib.Path(__file__).resolve().parent
IDS={'ERBB2':'2064','TACSTD2':'4070','NECTIN4':'81607','FOLR1':'2348','F3':'2152','MET':'4233'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--peer',type=pathlib.Path,required=True);ar=ap.parse_args();peer=ar.peer
 universe=json.loads((peer/'FDA-UNIVERSE-FROZEN.json').read_text());ind=json.loads((HERE/'FDA-UNIVERSE-INDEPENDENT-REVIEW.json').read_text());assert sha(peer/'FDA-UNIVERSE-FROZEN.json')==ind['owner_universe_sha256']
 for n,h in universe['source_hashes'].items():assert sha(peer/'source-cache'/n)==h,n
 raw=json.loads((peer/'source-cache/OpenFDA-conjugate-labels.json').read_text())['results'];assert len(raw)==len(universe['all_label_roster'])==31
 for r in universe['all_label_roster']:
  s=raw[r['source_row']];assert (s['id'],s['set_id'],s['effective_time'])==(r['label_id'],r['set_id'],r['effective_time']);assert s['effective_time']<='20261005'
 for app,date in ind['eligible_original_approvals_independently_matched'].items():
  api=json.loads((HERE/'source-cache'/f'FDA-{app}.json').read_text());subs=[s for r in api['results'] for s in r['submissions'] if s.get('submission_type')=='ORIG' and s.get('submission_status')=='AP'];assert min(s['submission_status_date'] for s in subs)==date<='20261005'
 gate=json.loads((HERE/'MODEL-ANNOTATION-GATE.json').read_text())
 for p,h in gate['owner_source_bindings'].items():assert sha(pathlib.Path(p))==h
 el=json.loads((peer/'source-cache/ADC-gene-RefSeqRNA-elink.json').read_text())['linksets'];es=json.loads((peer/'source-cache/ADC-RefSeqRNA-summaries.json').read_text())['result'];rows=[];uids=[]
 for g,gid in IDS.items():
  links=[r for r in el if r['ids']==[gid]];assert len(links)==1 and links[0]['dbfrom']=='gene'
  linked=[r for r in links[0]['linksetdbs'] if r['dbto']=='nuccore' and r['linkname']=='gene_nuccore_refseqrna'];assert len(linked)==1
  for uid in linked[0]['links']:
   r=es[uid];assert int(r['taxid'])==9606 and r['sourcedb']=='refseq' and '('+g+')' in r['title'];a=r['accessionversion'];accepted=r['biomol']=='mRNA' and a.startswith(('NM_','XM_'));assert accepted or (g=='ERBB2' and a.startswith('NR_'))
   rows.append((g,gid,uid,a,accepted));uids.append(uid)
 assert len(uids)==len(set(uids))==58 and set(uids)==set(es['uids'])
 assert set(rows)=={(r['gene'],r['gene_id'],r['UID'],r['RefSeq_accessionversion'],r['accepted_mRNA']) for r in gate['rows']}
 primary=json.loads((HERE/'PRIMARY-OMISSION-REVIEW.json').read_text())
 for r in primary['sources']:
  if r.get('raw_path'):assert sha(HERE/r['raw_path'])==r['sha256']
 xml=etree.parse(str(HERE/'source-cache/PMC9248243.xml'));review_rows=[]
 for t in xml.xpath('//table-wrap/table'):
  for r in t.xpath('.//tbody/tr'):
   cells=[' '.join(' '.join(c.itertext()).split()) for c in r.xpath('td')]
   if len(cells)==10 and cells[0].isdigit():review_rows.append(cells)
 assert len(review_rows)==21;negative=sum('HER2' in r[-1] for r in review_rows);assert negative==6
 out={'schema':'emc-ADC-independent-source-replay/1','status':'passed','FDA_returned_labels':31,'FDA_original_AP_dates':8,'six_Gene_RefSeqRNA_associations':6,'linked_unique_human_RefSeq_UIDs':58,'accepted_mRNAs':57,'breast_review_rows':21,'breast_review_explicit_HER2_negative_rows':6,'limits':'Source identity/numerical roster replay only. Breast rows include molecularly unresolved cases and a confirmed metaplastic carcinoma; six reported negatives are not an authenticated EMC denominator. Manual primary interpretation/eligibility remains in primary review and dated amendment.'}
 (HERE/'SOURCE-REPLAY-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
