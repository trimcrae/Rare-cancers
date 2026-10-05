import json, hashlib, os
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def binding(path, expected=None):
    p=Path(path); actual=sha(p)
    return {"path":str(p),"sha256":actual,"expected":expected,"hash_matches":expected is None or actual == expected,"bytes":p.stat().st_size}

def selected(path):
    p=Path(path)
    x=json.loads(p.read_text())
    return {"binding":binding(p),"data":x}

if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); args=ap.parse_args()
    for path in args.paths:
        print(json.dumps(selected(path),indent=2))
