"""Losslessly compress generated registry payloads; preserve original-byte hashes.
Each source path is checked beneath this round's sources directory before replacement.
"""
import gzip
import retrieve as r
before=after=0
for mp in r.SOURCES.glob('*/manifest.json'):
 m=r.read(mp)
 for page in m['pages']:
  p=(r.ROOT/page['file']).resolve()
  assert p.is_relative_to(r.SOURCES.resolve())
  if p.suffix=='.gz': continue
  b=p.read_bytes();assert r.sha(b)==page['sha256']
  zipped=gzip.compress(b,compresslevel=6,mtime=0);dest=p.with_suffix(p.suffix+'.gz');dest.write_bytes(zipped)
  assert gzip.decompress(dest.read_bytes())==b
  page.update(original_file=page['file'],file=dest.relative_to(r.ROOT).as_posix(),storage_encoding='gzip',stored_sha256=r.sha(zipped),stored_bytes=len(zipped))
  r.save(mp,m)
  p.unlink()
  before+=len(b);after+=len(zipped)
print('Lossless registry compression:',before,'to',after,'bytes')
