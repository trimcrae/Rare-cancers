"""One ordinary public supplement request; explicit storage/free-space caps."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import urllib.request

HERE = Path(__file__).resolve().parent
CACHE = HERE / "source-cache"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12055966/supplementaryFiles"
DEST = CACHE / "ORIEN-supplementaryFiles.zip"
TOTAL = 90 * 1024 * 1024
ADDITIONAL = 70 * 1024 * 1024
FLOOR = 10 * 1024**3

def main():
    assert not DEST.exists(), "Preserve existing source; no unchanged retry"
    used = sum(p.stat().st_size for p in CACHE.rglob("*") if p.is_file())
    cap = min(ADDITIONAL, TOTAL - used)
    free = shutil.disk_usage(HERE).free
    assert free - cap >= FLOOR
    record = {"url": URL, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "raw_before_bytes": used, "effective_cap_bytes": cap,
              "free_before_bytes": free, "retained": str(DEST), "status": "pending"}
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "EMC-public-research/1.0"})
        with urllib.request.urlopen(request, timeout=50) as response:
            record.update(http=response.status, content_type=response.headers.get("Content-Type"),
                          declared_length=response.headers.get("Content-Length"))
            if record["declared_length"] and int(record["declared_length"]) > cap:
                raise RuntimeError("Declared size exceeds finite cap; no body downloaded")
            with DEST.open("wb") as handle:
                count = 0
                while True:
                    chunk = response.read(min(1024 * 1024, cap - count + 1))
                    if not chunk:
                        break
                    if count + len(chunk) > cap:
                        handle.write(chunk[:cap - count])
                        raise RuntimeError("Stream exceeds finite cap; retained bounded partial source")
                    handle.write(chunk)
                    count += len(chunk)
        record["status"] = "retrieved; format validation pending"
    except Exception as error:
        record.update(status="source access/finite-stage failure", error=str(error))
    if DEST.exists():
        record.update(bytes=DEST.stat().st_size, sha256=hashlib.sha256(DEST.read_bytes()).hexdigest())
    record["raw_after_bytes"] = sum(p.stat().st_size for p in CACHE.rglob("*") if p.is_file())
    record["free_after_bytes"] = shutil.disk_usage(HERE).free
    assert record["raw_after_bytes"] <= TOTAL
    assert record["free_after_bytes"] >= FLOOR
    (HERE / "ORIEN-STAGE-ACCESS.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))

if __name__ == "__main__":
    main()
