"""Independent narrow audit of the R7 diagnostic-panel EMC row count."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET

root=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round7/fusion_transcripts')
review=json.loads((root/'REVIEW-INPUTS.json').read_text(encoding='utf-8'))
for row in review['files']:
    p=Path(row['path'])
    assert p.is_file() and p.stat().st_size==row['bytes']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],p
source=root/'racanelli2020.xml'
doc=ET.parse(source).getroot()
result=[]
for table in doc.findall('.//table-wrap'):
    emc=[]
    for tr in table.findall('.//tbody/tr'):
        cells=[' '.join(''.join(td.itertext()).split()) for td in tr.findall('./td')]
        if any('Extraskeletal Myxoid Chondrosarcoma' in cell for cell in cells):
            emc.append(cells[0])
    if emc:result.append({'table':table.attrib.get('id'),'ids':emc})
ids=[item for table in result for item in table['ids']]
assert ids==['7','12']+[str(x)for x in range(55,66)]+['100'],ids
print(json.dumps({'reviewed_hashes':len(review['files']),'emc_source_tables':result,'emc_row_count':len(ids)}))
