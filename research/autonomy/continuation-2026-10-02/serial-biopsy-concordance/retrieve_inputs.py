import hashlib,json,urllib.request
from pathlib import Path
FOLDER=Path(__file__).parent
SOURCES={
 'SampleSourceData.txt':'https://raw.githubusercontent.com/mskcc/ImmunoSarc/b71c3373bc182f9c647a6f7bc1fbd641d24db917/Figures/data/SampleSourceData.txt',
 'numeric-ihc.json':'https://raw.githubusercontent.com/trimcrae/Rare-cancers/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/ImmunoSarc-measured-numeric-IHC-actual.json',
 'FigureS2.R':'https://raw.githubusercontent.com/mskcc/ImmunoSarc/b71c3373bc182f9c647a6f7bc1fbd641d24db917/Figures/FigureS2.R',
 'SetUpData.R':'https://raw.githubusercontent.com/mskcc/ImmunoSarc/b71c3373bc182f9c647a6f7bc1fbd641d24db917/GeneralProcessing/SetUpData.R'}
receipt=[]
for name,url in SOURCES.items():
    with urllib.request.urlopen(url,timeout=45) as response: data=response.read(600001)
    assert len(data)<=600000,'Scoped input cap exceeded'
    digest=hashlib.sha256(data).hexdigest()
    if name=='SampleSourceData.txt': assert digest=='66d1f6bf39becc76f82d194ef2bf7b1784689c6d01177a319c717e208427e625'
    (FOLDER/name).write_bytes(data)
    receipt.append(dict(name=name,url=url,bytes=len(data),sha256=digest))
(FOLDER/'sources.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
