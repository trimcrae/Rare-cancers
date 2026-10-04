import pathlib,json,hashlib,re,csv,collections,datetime
R=pathlib.Path(__file__).resolve().parent
M=pathlib.Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round3/small_rna')
G=pathlib.Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round3/mirna_deposition')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert h(M/'MANIFEST.json')=='bdb199852f941d4a6ace55c61f74ec4a53177234b6d557334c08c37e83a1b20d'
assert h(G/'file-manifest.json')=='e17b1efbd2d4c8e2597cd981f559b3ebf96ff709565f74663946c71e325f67ac'
paths=[M/n for n in ['MANIFEST.json','RESULTS.txt','COVERAGE.txt','PUBLICATION-TRAIL.txt','HANDOFF.txt','emsos2014-evaluation.json','deposition-review-reuse.json','GSE69470-samples.txt','H-EMC-SS.txt','GSM827448-metadata.txt','GSM1669877-metadata.txt']]+[G/n for n in ['file-manifest.json','RESULTS.txt','HANDOFF.txt','trace-evaluation.json','linked-project-evaluation.json','E-MTAB-7265.sdrf.txt']]
t=(M/'GSE69470-samples.txt').read_text(encoding='utf-8')
blocks=re.split(r'^\^SAMPLE = ',t,flags=re.M)[1:]
title=[re.search(r'^!Sample_title = (.+)$',b,re.M).group(1).strip() for b in blocks]
labels=[re.sub(r'-rep\d*$', '',re.sub(r'\s*\[miRNA\]$','',x)) for x in title]
assert len(blocks)==77 and len(set(labels))==73
with (G/'E-MTAB-7265.sdrf.txt').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
# Read identity metadata only; do not calculate domain-group outcomes from published subtype fields.
identity=[{k:row[k] for k in ['Source Name','Characteristics[disease]','Characteristics[patientid]','Characteristics[tumor grading]']} for row in rows]
assert len(identity)==102
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':str(p),'sha256':h(p),'bytes':p.stat().st_size} for p in paths],
 'independent_NCI_metadata_check':{'sample_records':len(blocks),'unique_normalized_labels':len(set(labels)),'explicit_replicate_labels':[x for x in title if re.search(r'-rep\d*\s',x)],'H_EMC_SS_hits':[x for x in labels if re.search(r'H.?EMC.?SS',x,re.I)]},
 'independent_French_metadata_check':{'rows':len(identity),'disease_counts':dict(collections.Counter(x['Characteristics[disease]'] for x in identity)),'unique_source_names':len(set(x['Source Name'] for x in identity)),'interpretation':'Rows and labels are not evidence of authenticated EMC identity or independent donors.'},
 'decision':'Agree scoped shelving; no biological negative, no final claim of exhaustive public-evidence closure.'}
(R/'source-crosscheck.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2))
