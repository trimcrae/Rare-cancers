#!/usr/bin/env python3
"""One bounded public-source cycle for CHRNA6 specimen-overlap evidence.

AI-authored evidence tooling. No patient identity inference or expression analysis.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import signal
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

PMID = "38447752"
DOI = "10.1016/j.modpat.2024.100464"
UA = "EMCResearchSourceAudit/1.0"
METADATA = {
    "europe_pmc": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:38447752%20AND%20SRC:MED&format=json&resultType=core",
    "crossref": "https://api.crossref.org/works/10.1016%2Fj.modpat.2024.100464",
}
ALLOWED = {"www.ebi.ac.uk", "api.crossref.org", "www.modernpathology.org", "www.modpathol.org", "www.modernpathology.com", "www.modpatholjournal.org", "www.sciencedirect.com", "linkinghub.elsevier.com"}
LIMIT = 400_000
ROBOTS_LIMIT = 64_000
DEADLINE = 180
ROOT = Path(__file__).resolve().parent

class CycleDeadline(BaseException):
    """Terminate the finite cycle; ordinary source-error handlers must not swallow it."""


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def ensure_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or p.hostname not in ALLOWED or p.username or p.password or p.port not in (None, 443):
        raise ValueError("Unapproved source URL")
    return p

class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.count = 0
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        ensure_url(newurl)
        self.count += 1
        if self.count > 3 or urllib.parse.urlsplit(newurl).hostname != urllib.parse.urlsplit(req.full_url).hostname:
            raise ValueError("Redirect exceeds same-host source contract")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def request(url, limit):
    ensure_url(url)
    opener = urllib.request.build_opener(Redirects())
    began = time.monotonic()
    with opener.open(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, application/xml, text/html;q=0.8"}), timeout=12) as r:
        if int(r.headers.get("Content-Length", "0")) > limit:
            raise ValueError("Source size exceeds contract")
        parts = []
        n = 0
        while True:
            if time.monotonic() - began > 30:
                raise TimeoutError("Source read deadline exceeded")
            b = r.read(min(65536, limit + 1 - n))
            if not b:
                break
            n += len(b)
            if n > limit:
                raise ValueError("Source size exceeds contract")
            parts.append(b)
        raw = b"".join(parts)
        return {"http_status": r.status, "final_url": r.url, "content_type": r.headers.get("Content-Type", ""), "bytes": len(raw), "sha256": sha(raw), "raw_utf8": raw.decode("utf-8", errors="strict")}

def robots(url):
    p = ensure_url(url)
    robots_url = f"https://{p.hostname}/robots.txt"
    try:
        rec = request(robots_url, ROBOTS_LIMIT)
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return {"url": robots_url, "http_status": e.code, "decision": "allow_missing_robots"}
        return {"url": robots_url, "http_status": e.code, "decision": "refuse"}
    except Exception as e:
        return {"url": robots_url, "decision": "refuse", "error": f"{type(e).__name__}: {e}"}
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(rec["raw_utf8"].splitlines())
    rec["url"] = robots_url
    rec["decision"] = "allow" if parser.can_fetch(UA, url) else "refuse"
    return rec

def acquire_source(key, url):
    started = utc()
    rb = robots(url)
    rec = {"key": key, "requested_url": url, "started_utc": started, "robots": rb}
    if rb["decision"] == "refuse":
        rec["status"] = "robots_or_access_unavailable"
    else:
        try:
            rec.update(request(url, LIMIT))
            rec["status"] = "acquired"
        except urllib.error.HTTPError as e:
            rec.update(status="http_unavailable", http_status=e.code)
        except Exception as e:
            rec.update(status="unavailable", error=f"{type(e).__name__}: {e}")
    rec["completed_utc"] = utc()
    return rec

def metadata_fields(sources):
    out = {}
    for s in sources:
        if s["status"] != "acquired":
            continue
        if s["key"] == "europe_pmc":
            records = json.loads(s["raw_utf8"])["resultList"]["result"]
            matches = [r for r in records if str(r.get("id")) == PMID and r.get("source") == "MED"]
            if len(matches) != 1 or matches[0].get("doi", "").lower() != DOI:
                raise ValueError("Europe PMC PMID/DOI identity mismatch")
            r = matches[0]
            out["europe_pmc"] = {k: r.get(k) for k in ("id", "source", "doi", "title", "authorString", "pmcid", "isOpenAccess", "inPMC", "hasSuppl", "hasData", "abstractText", "fullTextUrlList")}
        elif s["key"] == "crossref":
            m = json.loads(s["raw_utf8"])["message"]
            if m.get("DOI", "").lower() != DOI:
                raise ValueError("Crossref DOI identity mismatch")
            out["crossref"] = {k: m.get(k) for k in ("DOI", "title", "URL", "link", "resource", "relation", "abstract")}
    return out

def validate(record):
    if record.get("schema") != "emc-chrna6-specimen-crosswalk/1" or record.get("pmid") != PMID or record.get("doi") != DOI:
        raise ValueError("Record identity mismatch")
    sources = record["sources"]
    keys = [s["key"] for s in sources]
    if len(keys) != len(set(keys)) or not {"europe_pmc", "crossref"}.issubset(keys) or len(keys) > 4:
        raise ValueError("Source-cycle cardinality mismatch")
    for s in sources:
        ensure_url(s["requested_url"])
        if s["key"] in METADATA and s["requested_url"] != METADATA[s["key"]]:
            raise ValueError("Metadata locator mismatch")
        if s["status"] not in {"acquired", "http_unavailable", "unavailable", "robots_or_access_unavailable"}:
            raise ValueError("Unknown access status")
        rb = s["robots"]
        if rb["decision"] not in {"allow", "allow_missing_robots", "refuse"}:
            raise ValueError("Unknown robots decision")
        origin = urllib.parse.urlsplit(s["requested_url"]).hostname
        if rb.get("url") != f"https://{origin}/robots.txt":
            raise ValueError("Robots locator is not bound to requested source origin")
        if rb.get("http_status") == 200:
            if "raw_utf8" not in rb:
                raise ValueError("200 robots receipt lacks replayable policy")
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(rb["raw_utf8"].splitlines())
            replayed = "allow" if parser.can_fetch(UA, s["requested_url"]) else "refuse"
            if rb["decision"] != replayed:
                raise ValueError("Robots decision disagrees with acquired policy")
        elif rb.get("http_status") in (404, 410):
            if rb["decision"] != "allow_missing_robots" or "raw_utf8" in rb:
                raise ValueError("Missing-robots access policy mismatch")
        elif rb["decision"] != "refuse":
            raise ValueError("Unavailable robots cannot authorize source access")
        if s["status"] == "acquired":
            if rb["decision"] == "refuse" or s["http_status"] != 200:
                raise ValueError("Acquired source conflicts with access receipt")
            ensure_url(s["final_url"])
            b = s["raw_utf8"].encode("utf-8")
            if len(b) != s["bytes"] or len(b) > LIMIT or sha(b) != s["sha256"]:
                raise ValueError("Raw source hash/size mismatch")
        if "raw_utf8" in rb:
            b = rb["raw_utf8"].encode("utf-8")
            if len(b) != rb["bytes"] or len(b) > ROBOTS_LIMIT or sha(b) != rb["sha256"]:
                raise ValueError("Robots hash/size mismatch")
    fields = metadata_fields(sources)
    for s in sources:
        if s["key"] == "pmc_fulltext":
            pmcid = fields.get("europe_pmc", {}).get("pmcid")
            if not pmcid or s["requested_url"] != f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML":
                raise ValueError("Full-text locator is not bound to returned PMCID")
        elif s["key"] == "publisher_landing":
            landing = ((fields.get("crossref", {}).get("resource") or {}).get("primary") or {}).get("URL")
            if not landing or s["requested_url"] != landing:
                raise ValueError("Publisher locator is not bound to returned DOI resource")
        elif s["key"] not in METADATA:
            raise ValueError("Unrecognized source key")
    if fields != record["metadata_projection"]:
        raise ValueError("Metadata projection diverges from raw primary/index bytes")
    gap = record["adjudication"]
    # Source acquisition cannot establish absent/unshared patients. Roster review is human/independent.
    if gap != {"specimen_overlap": "unknown", "patient_overlap": "unknown", "crosswalk_status": "not_established", "independent_validation": "not_established", "reason": "No reviewed specimen/patient crosswalk binds the CHRNA6 discovery/validation study to the existing GEO cohort. Accessible abstract or link metadata alone cannot adjudicate reuse."}:
        raise ValueError("Unsupported specimen/independence conclusion")
    if record["scope"] != "source availability and methods evidence only; no expression analysis, CISH threshold inference or clinical validation":
        raise ValueError("Scope mismatch")
    return fields

def acquire():
    sources = [acquire_source(k, u) for k, u in METADATA.items()]
    fields = metadata_fields(sources)
    # At most one official PMC full text and one DOI-returned publisher landing page.
    pmcid = fields.get("europe_pmc", {}).get("pmcid")
    if pmcid:
        if not str(pmcid).startswith("PMC") or not str(pmcid)[3:].isdigit():
            raise ValueError("Malformed PMCID")
        sources.append(acquire_source("pmc_fulltext", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"))
    publisher = fields.get("crossref", {}).get("resource")
    landing = (publisher or {}).get("primary", {}).get("URL")
    if landing:
        try:
            ensure_url(landing)
        except ValueError:
            pass
        else:
            sources.append(acquire_source("publisher_landing", landing))
    out = {"schema": "emc-chrna6-specimen-crosswalk/1", "ai_authorship": "Codex AI assistant; not human scientific validation", "completed_utc": utc(), "pmid": PMID, "doi": DOI, "scope": "source availability and methods evidence only; no expression analysis, CISH threshold inference or clinical validation", "stop_condition": "one metadata cycle plus at most two returned official text locators; no retries, guessed supplements or access bypass", "sources": sources, "metadata_projection": metadata_fields(sources), "adjudication": {"specimen_overlap": "unknown", "patient_overlap": "unknown", "crosswalk_status": "not_established", "independent_validation": "not_established", "reason": "No reviewed specimen/patient crosswalk binds the CHRNA6 discovery/validation study to the existing GEO cohort. Accessible abstract or link metadata alone cannot adjudicate reuse."}}
    validate(out)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--acquire", action="store_true")
    p.add_argument("--check")
    p.add_argument("--output")
    args = p.parse_args()
    if args.acquire:
        if (ROOT / "evidence.json").exists():
            raise SystemExit("Committed evidence exists; this source cycle is complete and may not reacquire")
        if not args.output:
            p.error("--output required")
        socket.setdefaulttimeout(12)
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(CycleDeadline("Finite source-cycle deadline")))
        signal.alarm(DEADLINE)
        record = acquire()
        signal.alarm(0)
        text = json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="")
        print("SOURCE_EVIDENCE_BEGIN")
        print(text, end="")
        print("SOURCE_EVIDENCE_END")
        print(f"EVIDENCE_SHA256={sha(text.encode('utf-8'))} BYTES={len(text.encode('utf-8'))}")
    elif args.check:
        record = json.loads(Path(args.check).read_text(encoding="utf-8"))
        fields = validate(record)
        print(f"OFFLINE_CHECK_OK sources={len(record['sources'])} metadata_records={len(fields)} overlap=unknown")
    else:
        p.error("choose --acquire or --check")

if __name__ == "__main__":
    main()
