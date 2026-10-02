from pathlib import Path
import gzip,hashlib,xml.etree.ElementTree as E,json
p=Path(__file__).parent
b=(p/'sample-run.mzid.gz').read_bytes()
x=gzip.decompress(b)
r=E.fromstring(x)
ns={'m':r.tag.split('}')[0].strip('{')}
wanted=['AnalysisSoftwareList','AnalysisProtocolCollection','SearchDatabase','SourceFile']
parts=[e for e in r.iter() if e.tag.split('}')[-1] in wanted]
text='\n'.join(E.tostring(e,encoding='unicode') for e in parts)
(p/'sample-run-parameters.xml').write_text(text,encoding='utf-8')
print(json.dumps({'bytes':len(b),'sha1':hashlib.sha1(b).hexdigest(),'uncompressed_bytes':len(x),'uncompressed_sha1':hashlib.sha1(x).hexdigest(),'parameters_sha256':hashlib.sha256(text.encode()).hexdigest()}))
print(text[:24000])
