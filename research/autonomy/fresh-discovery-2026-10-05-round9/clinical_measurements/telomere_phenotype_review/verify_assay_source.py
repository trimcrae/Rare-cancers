#!/usr/bin/env python3
"""Check source bindings and exact published EMC assay denominators, not images."""
from pathlib import Path
import json,hashlib,re
b=Path(__file__).resolve().parent
s=(b/'source-cache/liau2015-text.txt').read_text()
match=re.search(r'Extraskeletal myxoid chondrosarcoma\s+3\s+0/3 \(0%\)\s+0/2 \(0%\)\s+N/A\s+2/2 \(100%\)\s+0/2 \(0%\)',s)
assert match,'Source Table2 EMC row must match all columns'
assert 'ATRX' in s and 'DAXX' in s and '1:500' in s
assert 'criteria used for interpretation of the FISH' in s
assert 'results were the same as previously defined.24' in s
assert not re.search(r'\bTRAP\b|telomeric repeat amplification protocol',s,re.I)
for x in json.loads((b/'PORTABILITY.json').read_text())['local_cache']:
 p=b/x['path'];assert p.stat().st_size==x['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print(json.dumps({'status':'PASS','EMC_source_row':'3 ATRXassayed;2 ALT-FISHtested;0/2 sourceALTpositive;not0/3','local_cache':'all locked hashes matched','scope':'Text-only published assay/method/eligibility check; no images, DNA/topology, new activity inference or efficacy'}))
