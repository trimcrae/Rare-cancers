#!/usr/bin/env python3
"""Fetch a list of literature URLs from a GitHub-hosted runner (unrestricted egress)
and dump readable text into .cache/literature/ for the publish step.

The dev sandbox egress allowlist only permits github.com, so verbatim-quote
verification of journal/preprint pages has to happen out here. Pure stdlib except
for an optional pypdf import (installed by the workflow) used for PDF targets.
"""
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OUT = os.path.join(".cache", "literature")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

# name -> url. Name becomes the output filename.
TARGETS = {
    # 1. LOMAP origin
    "lomap_escholarship_pdf": "https://escholarship.org/content/qt4ss798kt/qt4ss798kt_noSplash_fa4f02c1a3fd390aee989bdb9f173170.pdf",
    "lomap_springer": "https://link.springer.com/article/10.1007/s10822-013-9678-y",
    "lomap_pmc": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3808540/",

    # 1b. FEP+ / Schrodinger cycle closure
    "wang2015_jacs_landing": "https://pubs.acs.org/doi/10.1021/ja512751q",
    "schrodinger_patent_cycleclosure": "https://patents.google.com/patent/WO2014151310A2/en",
    "schrodinger_patent_us": "https://patents.google.com/patent/US20160055304A1/en",

    # 2/3. precision vs accuracy, hysteresis limitations
    "commschem_maximal_accuracy": "https://www.nature.com/articles/s42004-023-01019-9",
    "scirep_fep_protocol": "https://www.nature.com/articles/s41598-019-53133-1",

    # 4. best-practices documents (the crux: replicates vs cycle closure)
    "livecoms_alchemical_bp": "https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378",
    "livecoms_alchemical_bp_pdf": "https://livecomsjournal.org/index.php/livecoms/article/download/v2i1e18378/pdf",
    "mey_bp_arxiv": "https://arxiv.org/abs/2008.03067",
    "mey_bp_arxiv_pdf": "https://arxiv.org/pdf/2008.03067v3",
    "hahn_benchmarks_arxiv": "https://arxiv.org/abs/2105.06222",
    "hahn_benchmarks_arxiv_pdf": "https://arxiv.org/pdf/2105.06222v4",
    "hahn_benchmarks_livecoms": "https://livecomsjournal.org/index.php/livecoms/article/view/v4i1e1497",

    # 4b. OpenFE / cinnabar
    "cinnabar_docs": "https://cinnabar.readthedocs.io/en/latest/",
    "cinnabar_api": "https://cinnabar.readthedocs.io/en/latest/api.html",
    "openfe_docs_analysis": "https://docs.openfree.energy/en/stable/guide/rbfe/index.html",

    # 5. DiffNet / maximum likelihood network estimation
    "diffnet_arxiv": "https://arxiv.org/abs/1906.08599",
    "diffnet_arxiv_pdf": "https://arxiv.org/pdf/1906.08599v2",
    "diffnet_jcim": "https://pubs.acs.org/doi/10.1021/acs.jcim.9b00528",
    "diffnet_jctc_2021": "https://pubs.acs.org/doi/10.1021/acs.jctc.1c00703",

    # 6. replicates / ensemble sampling / reproducibility (the counter-position)
    "coveney_ties_jctc2017": "https://pubs.acs.org/doi/10.1021/acs.jctc.6b00979",
    "loeffler_reproducibility": "https://pubs.acs.org/doi/10.1021/acs.jctc.8b00544",
    "weighted_cycle_closure": "https://pubs.acs.org/doi/10.1021/acs.jcim.2c01076",
}


def _looks_structured(ctype: str, data: bytes) -> bool:
    """Is this a JSON/XML payload that must reach disk byte-for-byte?

    ⚠ CONTENT-TYPE IS CHECKED FIRST BUT IS NOT TRUSTED ALONE. Several of the endpoints this repo
    fetches serve JSON under `text/plain`, and one serves it with no Content-Type at all, so a
    header-only test would send exactly those through the stripper — the case it exists to prevent.
    The sniff is a first-non-space-byte check, which is what actually decides whether `json.loads`
    will be run on the other end.
    """
    c = (ctype or "").lower()
    if "json" in c or "xml" in c:
        return True
    if "html" in c:
        return False
    head = data[:512].lstrip()[:1]
    return head in (b"{", b"[", b"<") and not data[:512].lstrip().lower().startswith(b"<!doctype html")


def strip_html(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?is)</(p|div|h[1-6]|li|tr|section)>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t\xa0]+", " ", raw)
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)
    return raw.strip()


def pdf_to_text(data: bytes) -> str:
    try:
        import pypdf
    except ImportError:
        return "[pypdf not available]"
    try:
        reader = pypdf.PdfReader(io.BytesIO(data))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:  # noqa: BLE001
        return f"[pdf parse failed: {exc}]"


def fetch(name: str, url: str) -> dict:
    rec = {"name": name, "url": url}
    # Request() is built INSIDE the try: a value that is not a URL raises ValueError
    # from the constructor, and building it outside let ONE bad entry abort the whole
    # corpus run (measured 2026-08-03: a "_readme" prose key in a targets file killed
    # a 14-target fetch before a single request went out). One bad target is now one
    # bad row in the manifest.
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
            rec["status"] = resp.status
            rec["final_url"] = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
            rec["content_type"] = ctype
    except urllib.error.HTTPError as exc:
        rec["status"] = exc.code
        rec["error"] = f"HTTPError {exc.code}"
        try:
            data = exc.read()
            ctype = exc.headers.get("Content-Type", "")
        except Exception:  # noqa: BLE001
            return rec
    except Exception as exc:  # noqa: BLE001
        rec["status"] = None
        rec["error"] = repr(exc)
        return rec

    # ⛔ AN IMAGE MUST NOT BE PUT THROUGH A UTF-8 TEXT WRITER. Every branch below ends at
    # `open(..., "w", encoding="utf-8")`, and `data.decode("utf-8", errors="replace")` on a JPEG
    # replaces most of the file with U+FFFD -- so the run reports success, the manifest records a
    # plausible `chars` count, and the artifact is destroyed. That is the populated-field-is-not-a-
    # measured-field shape this repo already has two incidents for, so images get their own path
    # and are written in BINARY, with the .txt kept as a provenance stub pointing at them.
    #
    # Added 2026-08-12 for the EMC IPD admissibility pass: a Kaplan-Meier figure's
    # numbers-at-risk row is rendered INSIDE THE FIGURE IMAGE, so it is invisible to full-text
    # search and the only way to answer "is the curve admissible?" is to look at the graphic.
    # ⚠ THE DISCRIMINATOR IS THE CONTENT TYPE, NOT THE URL, AND THAT IS LOAD-BEARING. Measured
    # 2026-08-12: pmc.ncbi.nlm.nih.gov answered a request for a `.jpg` with HTTP 200 and
    # `text/html` -- a reCAPTCHA interstitial. Keying off the ".jpg" in the URL would have written
    # a captcha page into a file named like an image and called the step a success. Keying off the
    # declared type sends it down the text path, where it is legible as the refusal it is.
    # ⛔ AND AN OFFICE DOCUMENT IS THE SAME BUG WITH A DIFFERENT EXTENSION (measured 2026-08-23).
    # A .docx/.xlsx/.pptx is a ZIP, so it is as binary as a JPEG -- and none of its content types
    # was listed here, so three Supplemental Digital Content tables from a CORR paper
    # (links.lww.com serving `application/vnd.openxmlformats-...wordprocessingml.document`) went
    # down the TEXT path, were replacement-charactered, and were recorded in the manifest with a
    # plausible five-figure `chars` count and no `binary_path`. The run reported success; the
    # tables were destroyed; and the record looked like a retrieval. That is precisely the
    # populated-field-is-not-a-measured-field shape the comment above already exists for, which is
    # why the fix is a WIDER SNIFF rather than three more content types: the ZIP magic catches
    # every OOXML container whatever the server declares, and the OLE2 magic catches the legacy
    # .doc/.xls/.ppt binaries that a 2015-era archive still serves.
    _ct = ctype.split(";")[0].strip().lower()
    _binary_ext = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif",
                   "image/tiff": "tif", "application/x-tar": "tar", "application/gzip": "gz",
                   "application/x-gzip": "gz", "application/zip": "zip",
                   "application/msword": "doc",
                   "application/vnd.ms-excel": "xls",
                   "application/msexcel": "xls",
                   "application/vnd.ms-powerpoint": "ppt",
                   "application/vnd.openxmlformats-officedocument."
                   "wordprocessingml.document": "docx",
                   "application/vnd.openxmlformats-officedocument."
                   "spreadsheetml.sheet": "xlsx",
                   "application/vnd.openxmlformats-officedocument."
                   "presentationml.presentation": "pptx",
                   "application/vnd.oasis.opendocument.text": "odt",
                   "application/vnd.oasis.opendocument.spreadsheet": "ods"}
    _ooxml_by_ct = {"docx": "docx", "xlsx": "xlsx", "pptx": "pptx"}
    if (_ct in _binary_ext or _ct.startswith("image/")
            or data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"
            or data[:2] == b"\x1f\x8b" or data[:4] == b"PK\x03\x04"
            or data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        ext = _binary_ext.get(_ct)
        if ext is None:
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                ext = "png"
            elif data[:2] == b"\x1f\x8b":
                ext = "gz"
            elif data[:4] == b"PK\x03\x04":
                # An OOXML container declared as something else. `zip` is the honest fallback:
                # it is what the bytes are, and it opens with the same reader.
                ext = _ooxml_by_ct.get(_ct.rsplit(".", 1)[-1], "zip")
            elif data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                ext = "bin"       # OLE2 compound file: .doc/.xls/.ppt, undeclared
            else:
                ext = "jpg"
        binpath = os.path.join(OUT, f"{name}.{ext}")
        with open(binpath, "wb") as fh:
            fh.write(data)
        rec["binary_path"] = os.path.basename(binpath)
        rec["bytes"] = len(data)
        rec["chars"] = 0
        with open(os.path.join(OUT, f"{name}.txt"), "w", encoding="utf-8") as fh:
            fh.write(f"SOURCE URL: {url}\nFINAL URL: {rec.get('final_url')}\n"
                     f"HTTP: {rec.get('status')}\nCONTENT-TYPE: {ctype}\n"
                     f"BINARY: {os.path.basename(binpath)} ({len(data)} bytes)\n"
                     + "=" * 70 + "\nBinary payload saved alongside this stub; not text.\n")
        return rec

    if "pdf" in ctype.lower() or data[:5] == b"%PDF-":
        text = pdf_to_text(data)
    elif _looks_structured(ctype, data):
        # ⛔ NEVER RUN THE HTML STRIPPER OVER JSON/XML. `strip_html` deletes everything from a `<`
        # to the next `>`, and ClinicalTrials.gov emits LITERAL angle brackets inside free-text
        # eligibility criteria — "PLT < 100,000/mcL", "prednisone > 10 mg daily". Each `<` opens a
        # span that closes at the next `>`, wherever that is, so the stripper swallows every
        # structural key in between.
        #
        # ⚠ SUPERSEDED, RETAINED: this comment first said the trigger was HTML-ESCAPED brackets
        # (`&lt;`/`&gt;`). That was wrong and the synthetic written from it did not reproduce the
        # defect — modules survived. The real record settles it: 0 literal `<` and 13 orphaned
        # literal `>` remain in the damaged file, which is the stripper's own footprint. The story
        # was corrected against the artifact rather than kept because it sounded right.
        #
        # Measured 2026-08-07 on the 13-study fetch this repo used to verify trial status. One mode
        # is LOUD (10 records simply stopped parsing). The other is SILENT: NCT05836571 came back as
        # well-formed JSON keeping `statusModule`, `descriptionModule` and `contactsLocationsModule`
        # while `conditionsModule`, `designModule` and `eligibilityModule` VANISHED — and the
        # eligibility *content* survived, orphaned, because only the key fell inside an eaten span.
        # Nothing errored. A reader gets a clean parse of a document missing exactly the fields it
        # was fetched for, with fragments of them still present.
        #
        # ⚠ THAT IS THE WORST FAILURE SHAPE THIS REPO HAS A RULE FOR: a populated field is not a
        # measured one, and here the damage removes fields rather than corrupting them, so every
        # `in` check silently answers "absent" instead of raising. Detection alone is not enough —
        # a lane that fetches eligibility text and is told "undamaged sentences only" still cannot
        # read the sentence. The transport must stop destroying it.
        #
        # The corpora this repo fetches are DELIBERATELY API endpoints returning JSON/XML rather
        # than article pages, so this path is the common case, not the exception.
        text = data.decode("utf-8", errors="replace")
    else:
        text = strip_html(data.decode("utf-8", errors="replace"))

    rec["chars"] = len(text)
    path = os.path.join(OUT, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"SOURCE URL: {url}\nFINAL URL: {rec.get('final_url')}\n"
                 f"HTTP: {rec.get('status')}\nCONTENT-TYPE: {ctype}\n"
                 + "=" * 70 + "\n" + text)
    return rec


def resolve_targets() -> dict:
    """TARGETS, optionally REPLACED by a JSON {name: url} map named in LIT_TARGETS_FILE.

    Additive by design: the built-in TARGETS list is a fixed corpus tied to specific verification
    tasks, so a new corpus gets its own file rather than editing that dict (which would silently
    change what every future run fetches). LIT_TARGETS_MODE=extend appends instead of replacing.
    """
    path = os.environ.get("LIT_TARGETS_FILE", "").strip()
    inline = os.environ.get("LIT_TARGETS_JSON", "").strip()
    if not path and not inline:
        return TARGETS

    extra: dict = {}
    if path:
        with open(path, "r", encoding="utf-8") as fh:
            extra.update(json.load(fh))
    if inline:
        # ⛔ WHY AN INLINE CORPUS EXISTS AT ALL (added 2026-08-07, from a measured cap).
        # `LIT_TARGETS_FILE` names a path INSIDE THE CHECKED-OUT REF, so fetching a URL that is
        # not already committed requires committing and pushing a corpus file first. An agent
        # working in an isolated worktree under a no-push constraint therefore could not verify
        # ANY arbitrary URL, and the consequence was not hypothetical: the FAP lane had to file
        # every one of its clinicaltrials.gov facts as `[search]` rather than `[API]`, because
        # the proxy denies that host locally and no CI path could reach it either. That caps
        # every trial claim in the portfolio at unverified — including the trial-eligibility
        # lane, which is the one item on the board with a direct patient consequence.
        # ⚠ A registry status is exactly the class of fact that must never be quoted from a
        # search snippet: it changes without notice, and a stale "recruiting" is the one error
        # here that could actually mislead someone about their own options.
        parsed = json.loads(inline)
        if not isinstance(parsed, dict):
            raise SystemExit("LIT_TARGETS_JSON: expected a flat JSON object of name -> url")
        # Inline layers OVER a file when both are given, so a dispatch can override one entry of
        # a committed corpus without forking the whole file. Stated because a silent precedence
        # rule between two sources of the same thing is how a run fetches something nobody meant.
        extra.update(parsed)

    if not all(isinstance(v, str) for v in extra.values()):
        raise SystemExit("targets: expected a flat JSON object of name -> url")
    # Underscore-prefixed keys are documentation, not targets. Corpus files in this repo
    # carry a "_readme" line saying what the corpus is for and under what constraints it
    # was fetched; that is worth keeping, so the convention is honoured rather than banned.
    extra = {k: v for k, v in extra.items() if not k.startswith("_")}
    if os.environ.get("LIT_TARGETS_MODE", "replace").strip() == "extend":
        return {**TARGETS, **extra}
    return extra


#: ⛔ PER-HOST PACING, AND IT IS NOT A NICETY — IT SILENTLY LOST 19 OF 50 FETCHES (2026-08-15).
#: Two NR4A3 deposit sweeps dispatched 31 and 19 targets through this module. NCBI answered HTTP 429
#: to 11 and then 8 of them, this module recorded the 429 as an ordinary row, and BOTH RUNS REPORTED
#: SUCCESS. The nine questions behind those rows — including the broad nuccore EWS x NR4A3 alias
#: search, the one most likely to hold another fusion deposit — read afterwards as though they had
#: been asked and had returned nothing. ⚠ THAT IS THE ABSENT-READING-IS-NOT-A-READING-OF-ABSENCE
#: FAILURE ARRIVING THROUGH THE TRANSPORT: a rate-limited query and a genuinely empty one are
#: indistinguishable downstream unless the transport refuses to let it happen.
#: NCBI permits ~3 requests/second without an API key; the gap below is per HOST, so unrelated hosts
#: in the same corpus are not slowed by it.
HOST_MIN_INTERVAL_S = {"eutils.ncbi.nlm.nih.gov": 0.40, "www.ncbi.nlm.nih.gov": 0.40,
                       "pmc.ncbi.nlm.nih.gov": 0.40, "www.ebi.ac.uk": 0.20}
DEFAULT_MIN_INTERVAL_S = 0.10
RETRY_STATUSES = (429, 500, 502, 503, 504)
MAX_RETRIES = 4

_last_hit: dict = {}


def _pace(url: str) -> None:
    host = urllib.parse.urlsplit(url).netloc.lower()
    gap = HOST_MIN_INTERVAL_S.get(host, DEFAULT_MIN_INTERVAL_S)
    prev = _last_hit.get(host)
    if prev is not None:
        wait = gap - (time.monotonic() - prev)
        if wait > 0:
            time.sleep(wait)
    _last_hit[host] = time.monotonic()


def fetch_paced(name: str, url: str) -> dict:
    """`fetch` plus per-host pacing and a backoff retry on the statuses that mean 'ask again'.

    ⛔ A ROW THAT EXHAUSTS ITS RETRIES IS MARKED `unanswered: True`, so a reader can tell a question
    that was ASKED AND ANSWERED EMPTY from one that never got through. Nothing downstream should
    have to infer that from an HTTP code buried in a manifest.
    """
    rec = None
    for attempt in range(1, MAX_RETRIES + 1):
        _pace(url)
        rec = fetch(name, url)
        if rec.get("status") not in RETRY_STATUSES:
            if attempt > 1:
                rec["n_attempts"] = attempt
            return rec
        if attempt < MAX_RETRIES:
            back = 1.5 * (2 ** (attempt - 1))
            print(f"  ⏳ {rec.get('status')} on {name}; retry {attempt}/{MAX_RETRIES - 1} "
                  f"in {back:.1f}s", flush=True)
            time.sleep(back)
    rec["n_attempts"] = MAX_RETRIES
    rec["unanswered"] = True
    rec["⛔ why"] = (f"HTTP {rec.get('status')} after {MAX_RETRIES} paced attempts. THIS QUESTION "
                    "WAS NOT ANSWERED — it must not be read as an empty result.")
    return rec


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for name, url in resolve_targets().items():
        rec = fetch_paced(name, url)
        manifest.append(rec)
        print(f"{rec.get('status')}\t{rec.get('chars', 0)}\t{name}\t{url}"
              f"\t{rec.get('error', '')}", flush=True)
    with open(os.path.join(OUT, "_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    # ⛔ AN UNANSWERED FETCH IS A LOUD FAILURE, NOT A MANIFEST ROW. Both 2026-08-15 sweeps went
    # green with a third of their questions never asked; a reader of the run conclusion alone would
    # have concluded the searches came back empty.
    unanswered = [r["name"] for r in manifest if r.get("unanswered")]
    if unanswered:
        print(f"::error::{len(unanswered)} of {len(manifest)} targets were NEVER ANSWERED after "
              f"paced retries: {', '.join(unanswered)}. These are unanswered questions, NOT empty "
              "results, and nothing may be recorded as absent on their basis.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
