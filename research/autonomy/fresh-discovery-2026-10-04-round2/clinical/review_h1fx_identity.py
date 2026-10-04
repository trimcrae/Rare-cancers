"""Independent provenance audit; no new expression values examined here."""
from pathlib import Path
import json,hashlib,collections,xml.etree.ElementTree as ET,datetime,re
P=Path(__file__).resolve().parent
R=Path('C:/Projects/EMC-Research/research/autonomy')
L=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-lead/research/autonomy/fresh-discovery-2026-10-04-round2/h1fx')
source=L/'GSE6481-samples.txt';rows=[];current=None
for line in source.read_text(encoding='utf-8').splitlines():
 if line.startswith('^SAMPLE = '):
  current={'GSM':line.split(' = ',1)[1]};rows.append(current)
 elif line.startswith('!Sample_characteristics_ch1 = Histology:'):current['histology']=line.split('Histology:',1)[1]
 elif line.startswith('!Sample_source_name_ch1 = '):current['source']=line.split(' = ',1)[1]
 elif line.startswith('!Sample_title = '):current['title']=line.split(' = ',1)[1]
 elif line.startswith('!Sample_platform_id = '):current['GPL']=line.split(' = ',1)[1]
counts=collections.Counter(row['histology']for row in rows)
assert len(rows)==105 and len({row['GSM']for row in rows})==105
assert counts['Myxoid liposarcoma']==19
assert not any(re.search('chondrosarcoma|extraskeletal|\bEMC\b',r['histology'],re.I)for r in rows)
article=R/'peerj21497-source-2026-09-06/article.xml';x=ET.parse(article)
paragraphs=[' '.join(''.join(e.itertext()).split())for e in x.iter('p')if 'GSE6481'in ''.join(e.itertext())]
supp=[ET.tostring(e,encoding='unicode')for e in x.iter('supplementary-material')if e.get('id')=='supp-8']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_hashes':{str(p):sha(p)for p in [source,P/'gse6481-independent-metadata.txt',article,P/'peerj-14-21497-s008.png']},'GSE6481_all105_sample_histologies':rows,'histology_counts':dict(counts),'eligible_EMC':0,'manuscript_GSE6481_paragraphs':paragraphs,'supplement_caption_xml':supp,'figure_visual_observations':{'source':'peerj-14-21497-s008.png, viewed in full 2026-10-04','panel_B_title':'GSE6481 (n=147)','panel_B_xlabels':['Other Chondrosarcomas (n=59)','EMC (n=19)'],'all_three_genes_same_labels':True,'H1FX_log2FC':0.64,'H1FX_Wilcoxon_p':0.001,'contrast_n_sum':78,'main_text_contrast_n':[19,128],'no_GSM_identifiers_in_figure':True,'panel_A_title':'GSE24369(n=42)','panel_A_xlabels':['Other Sarcomas(n=36)','EMC(n=6)'],'panel_A_control_identity_caveat':'Two pooled normal-muscle samples and six desmoid samples are included in the source non-EMC group; not 36 malignant sarcomas.'},'alternative_source_check':[{'accession':'GSE6461','status':'unsuitable','source':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE6461','reason':'Near-string accession is9murine SYT-SSXsynovial-sarcoma/muscle profiles, not19EMC.'},{'accession':'GSE4303','status':'different authentic EMC dataset; not claimed cohort authenticated','source':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE4303','reason':'Original study10EMC+26other sarcomas, not19EMC+128or59cartilaginous tumors; individual deposit includes platform/technical replication questions.'},{'accession':'unknown','status':'unresolved','reason':'Targeted searches of19EMC,128cartilaginous,147total,59comparators,H1FXcorrection did not identify a corrected accession or GSMcrosswalk. A failure to locate is not proof no such data exist.'}],'conclusion':'The cited accession cannot establish the published EMC-versus-chondrosarcoma H1FX comparison. The origin of the plotted19cases remains unresolved; a citation/label/transcription error is possible. Do not call this fabrication, infer the19plottedcases are definitely myxoid liposarcoma, or infer H1FX is absent or biologically irrelevant in EMC.','decision':'Bounded provenance resolution and carefully specified disease contrasts warranted; standalone value/claim scope belongs to lead and independent scientific reviewer. This identity audit alone is not a new disease mechanism.'}
(P/'h1fx-independent-identity.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'all_samples':len(rows),'histologies':dict(counts),'eligible_EMC':0,'figure_comparison_n':78,'main_comparison_n':147,'decision':'source mismatch verified; plottedcase origin unresolved'}))
