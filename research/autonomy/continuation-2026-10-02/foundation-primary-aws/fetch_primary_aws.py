"""Cloud-only, one bounded GET of an explicitly listed public PMC object."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import threading
import urllib.request

URL = 'https://pmc-oa-opendata.s3.amazonaws.com/PMC9200814.1/41467_2022_30496_MOESM2_ESM.xls'
SIZE = 4812800
SHA256 = '88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475'
MD5 = '88366e3facf6d7c61fb660566ea7af3e'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise ValueError('Refuse overwrite; use existing workbook only after hash verification')
    if shutil.disk_usage(args.out.parent).free < 10 * 1024**3 + 2 * SIZE:
        raise ValueError('Insufficient cloud headroom')
    part = args.out.with_name(args.out.name + '.part')
    if part.exists():
        raise ValueError('Existing partial file requires explicit recovery')
    sha, md5, count = hashlib.sha256(), hashlib.md5(), 0
    try:
        with urllib.request.urlopen(URL, timeout=30) as response, part.open('xb') as output:
            if response.status != 200 or int(response.headers.get('Content-Length', '-1')) != SIZE:
                raise ValueError('Unexpected HTTP status or size')
            headers = dict(response.headers)
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                count += len(chunk)
                if count > SIZE:
                    raise ValueError('Byte cap exceeded')
                sha.update(chunk); md5.update(chunk); output.write(chunk)
        if count != SIZE or sha.hexdigest() != SHA256 or md5.hexdigest() != MD5:
            raise ValueError('Primary byte identity mismatch')
        part.replace(args.out)
        print(json.dumps({'status': 'primary_bytes_verified', 'url': URL,
                          'bytes': count, 'sha256': sha.hexdigest(), 'md5': md5.hexdigest(),
                          'headers': headers, 'scope': 'Byte retrieval only; independent extraction must run separately'}))
    except Exception:
        part.unlink(missing_ok=True)
        raise

if __name__ == '__main__':
    timer = threading.Timer(90, lambda: os._exit(124))
    timer.daemon = True
    timer.start()
    try:
        main()
    finally:
        timer.cancel()
