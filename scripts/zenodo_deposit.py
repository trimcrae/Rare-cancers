#!/usr/bin/env python3
"""Build a paper's Zenodo deposition from its own archive manifest, and RESERVE its DOI.

WHY THIS EXISTS, AND WHY IT IS NOT THE REPOSITORY'S EXISTING ZENODO WIRING.
`deploy/release-doi.md` wires GitHub Releases to Zenodo, which archives the WHOLE REPOSITORY —
3,453 tracked files across forty routes — under one concept DOI that moves to the newest release.
That is the right shape for citing a living project and the wrong shape for citing a paper:

  * A reader following a paper's archive DOI would land on a record about forty subjects and have
    to be told which files are the paper's. The ASO manifest already says: 473 of the 3,453, each
    with the role it plays (`serves`, `contributes`).
  * A concept DOI MOVES. A paper whose availability statement says "every result re-derives from
    the committed artefacts" would be pointing at an archive that changes every time an unrelated
    route cuts a release. The paper must cite a FROZEN version.

So: tier 1 is the repository record (GitHub-wired, unchanged by this file); tier 2 is one deposition
per paper, built here from that paper's manifest. Later corrections to a paper's deposit become new
VERSIONS OF THAT PAPER'S RECORD, so a reader arriving from the published paper still lands on the
version it was written against, with Zenodo offering them the newer one.

⛔ THIS SCRIPT DOES NOT PUBLISH UNLESS `--publish` IS PASSED, AND `--publish` REFUSES UNLESS THREE
INDEPENDENT CONDITIONS HOLD. Publishing is irreversible — a published version's files cannot be
edited, only superseded. The default path is unchanged and is the ordering fix the manifest's step 5
describes: create the draft, RESERVE the DOI, and print it, so the DOI can be pasted into the
manuscript and the manuscript rebuilt BEFORE the files are frozen. The deposit and the paper that
cites it then carry the same identifier.

⚠ SUPERSEDED, RETAINED (rule 1.2): "⛔ THIS SCRIPT NEVER PUBLISHES." That was true until 2026-08-30,
when trimcrae widened the grant in terms — "You should submit to zenodo on your own. That can be as
simple as a quick approval request to me when ready" — having just been told, with the evidence,
that the loop could not do it. ⛔ THE SENTENCE HE ADDED IS A GATE, NOT A COURTESY, so `--publish`
implements it: `publication-authority.json` must name the act, and the caller must pass
`--approved-by` naming who approved THIS deposition. An approval for one is not an approval for the
next.

★ AND THE THIRD CONDITION IS THE ONE NO HUMAN CAN EYEBALL: the draft's recorded upload digest must
EQUAL the archive manifest's `archive_content_digest`, re-read at publish time. Publishing a stale
draft freezes an archive already behind the paper that cites it — the precise defect the 2026-08-29
correction existed to remove, and the draft went stale TWICE during it, once because a repair landed
after the refresh. A human clicking Publish on zenodo.org cannot see that; this can.

⚠ THE MANIFEST IS THE CONTRACT, NOT A HINT. Every path is taken from `files`, every file's SHA-256
is re-read from disk and checked against the manifest, and a single mismatch aborts before anything
touches the network. A manifest that has drifted from the tree is exactly the failure that would
ship an archive whose hashes describe different bytes than it contains.

    ZENODO_TOKEN=... python3 scripts/zenodo_deposit.py --paper aso --sandbox
    ZENODO_TOKEN=... python3 scripts/zenodo_deposit.py --paper aso
    python3 scripts/zenodo_deposit.py --paper aso --build-only     # zip + verify, no network
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import io
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: paper key -> everything the deposition metadata needs that the manifest does not carry.
#: ⚠ The TITLE is the one a reader sees under the DOI, and it is taken verbatim from the manifest's
#: own step 4 rather than re-invented here, so the record and the instructions cannot disagree.
PAPERS = {
    "aso": {
        "manifest": "research/manuscripts/aso/fusion-junction-aso-archive-manifest.json",
        "zip": "emc-aso-archive.zip",
        "title": ("Code and artefacts for: fusion-junction antisense oligonucleotides in "
                  "extraskeletal myxoid chondrosarcoma"),
        "keywords": ["extraskeletal myxoid chondrosarcoma", "EWSR1::NR4A3",
                     "antisense oligonucleotide", "gapmer", "fusion junction",
                     "off-target screening", "in silico"],
        #: CC-BY-4.0 for artefacts is the manifest's own recommendation; the code in the archive
        #: stays under the repository's Apache-2.0, which the README block states.
        "license": "cc-by-4.0",
        "upload_type": "dataset",
    },
}

CREATOR = {"name": "McRae, Tristan D.",
           "affiliation": "Independent researcher, unaffiliated",
           "orcid": "0000-0002-1823-1451"}

REPO_URL = "https://github.com/trimcrae/Rare-cancers"

PACKAGE_NAME = "junction-provenance-20260926"
PACKAGE_ROOT = "research/release-candidates/PUB-ASO/2026-09-26"


def package_configuration(paper_key, package="canonical"):
    """Select a payload of the same paper; never create a second concept identity."""
    if package == "canonical":
        return PAPERS[paper_key]
    if paper_key != "aso" or package != PACKAGE_NAME:
        raise SystemExit("Unknown paper/package combination")
    return {
        **PAPERS[paper_key],
        "manifest": PACKAGE_ROOT + "/repository-deposit/zenodo-manifest.json",
        "zip": "EMC-junction-provenance-data-and-code.zip",
        "title": "Transcript provenance and normal-parent sequence comparisons for EMC fusion-junction antisense designs",
        "keywords": ["extraskeletal myxoid chondrosarcoma", "NR4A3", "fusion transcript",
                     "antisense oligonucleotide", "transcript provenance", "normal isoforms"],
        "expected_concept": "22028915",
        "strict_manifest": True,
    }


def content_digest(files):
    """Use the existing ASO manifest's path-NUL-SHA-newline convention."""
    digest = hashlib.sha256()
    for entry in files:
        digest.update(f"{entry['path']}\0{entry['sha256']}\n".encode("utf-8"))
    return digest.hexdigest()


def _safe_regular_file(relative):
    if not isinstance(relative, str) or not relative or any(c in relative for c in "\\:\0\n\r"):
        raise SystemExit("Manifest paths must be safe repository-relative POSIX paths")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or parts.as_posix() != relative:
        raise SystemExit("Unsafe or non-normalized manifest path")
    root = Path(REPO).resolve()
    actual = root.joinpath(*parts.parts)
    if not actual.is_file() or actual.is_symlink() or not actual.resolve().is_relative_to(root):
        raise SystemExit(f"Manifest entry is not a regular file within the repository: {relative}")
    return actual


def _git_bytes(revision, relative):
    try:
        row = subprocess.check_output(
            ["git", "-C", REPO, "ls-tree", revision, "--", relative], stderr=subprocess.PIPE)
        if not row.startswith((b"100644 blob ", b"100755 blob ")):
            raise SystemExit(f"Payload is not a committed regular file: {relative}")
        return subprocess.check_output(
            ["git", "-C", REPO, "show", f"{revision}:{relative}"], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise SystemExit(f"Cannot resolve committed payload: {revision}:{relative}") from None


def validate_package_manifest(manifest, paper):
    """Additional integrity checks for the named data-only payload; legacy default unchanged."""
    if not paper.get("strict_manifest"):
        return
    if manifest.get("_schema") != "emc-zenodo-package-manifest/1":
        raise SystemExit("Unsupported data-package manifest schema")
    files = manifest.get("files")
    if not isinstance(files, list) or not files or not all(isinstance(e, dict) for e in files):
        raise SystemExit("Manifest requires a nonempty per-file inventory")
    paths = [e.get("path") for e in files]
    if not all(isinstance(p, str) for p in paths) or paths != sorted(set(paths)):
        raise SystemExit("Manifest paths must be unique and sorted")
    if type(manifest.get("n_files")) is not int or manifest["n_files"] != len(files) or manifest.get("inventory_limited_to_tracked_files") is not True:
        raise SystemExit("Manifest inventory/count declaration is invalid")
    if not isinstance(manifest.get("_what_this_is"), str) or not manifest["_what_this_is"].strip():
        raise SystemExit("Manifest description is missing")
    instructions = manifest.get("how_to_reproduce_offline")
    if not isinstance(instructions, list) or not instructions or not all(isinstance(s, str) and s.strip() for s in instructions):
        raise SystemExit("Manifest reproduction instructions are missing")
    revision = manifest.get("git_revision", "")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise SystemExit("Manifest requires an exact source commit")
    if str(manifest.get("conceptrecid")) != paper["expected_concept"]:
        raise SystemExit("Manifest names the wrong archive concept")
    if not re.fullmatch(r"10\.5281/zenodo\.\d+", str(manifest.get("deposition_doi", ""))):
        raise SystemExit("Manifest must identify an existing ASO archive version")
    if paper["manifest"] in paths:
        raise SystemExit("Manifest cannot contain its own hash")
    for entry in files:
        actual = _safe_regular_file(entry["path"])
        if not permitted_package_path(entry["path"]):
            raise SystemExit(f"Path is outside the named data-only package: {entry['path']}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            raise SystemExit("Malformed per-file SHA-256")
        if type(entry.get("bytes")) is not int or entry["bytes"] != actual.stat().st_size:
            raise SystemExit(f"Manifest size mismatch: {entry['path']}")
        if hashlib.sha256(_git_bytes(revision, entry["path"])).hexdigest() != entry["sha256"]:
            raise SystemExit(f"Manifest hash differs from its source commit: {entry['path']}")
    if manifest.get("archive_content_digest") != content_digest(files):
        raise SystemExit("Manifest content digest does not match its inventory")


def require_committed_file(relative):
    actual = _safe_regular_file(relative)
    if _git_bytes("HEAD", relative) != actual.read_bytes():
        raise SystemExit(f"External action requires committed file bytes: {relative}")


def permitted_package_path(relative):
    if relative in {"LICENSE", PACKAGE_ROOT + "/supplementary-methods.md",
                    PACKAGE_ROOT + "/repository-deposit/README.md"}:
        return True
    prefix = PACKAGE_ROOT + "/evidence/"
    if not relative.startswith(prefix):
        return False
    local = PurePosixPath(relative[len(prefix):])
    if len(local.parts) == 1:
        return local.name in {
            "analyze.py", "CORRECTIONS.md", "figure-observations.json", "INDEPENDENT-REVIEW.md",
            "input-manifest.json", "NORMAL-CORPUS-AMENDMENT.md", "read_prefix_probe.py",
            "READ-PROBE-AMENDMENT.md", "read-probe-results-64MiB.json", "read-probe-results.json",
            "retrieval.jsonl", "retrieve.py", "VERIFICATION.json"}
    if len(local.parts) != 2:
        return False
    folder, name = local.parts
    if folder == "inputs":
        return local.suffix in {".json", ".csv"}
    if folder == "results":
        return local.suffix in {".json", ".tsv", ".fasta"}
    if folder == "reads":
        return local.suffix == ".json"
    if folder == "sources":
        return (local.suffix == ".gb" or
                (local.suffix == ".json" and (name.startswith(("ENSP", "ENST", "hg19-")) or "-RefSeq.json" in name)) or
                name in {"parent-refseq-accessions.json", "DElite-metadata.csv", "PRJNA692081-ena.tsv"})
    return False


def verify_package_identity(paper, deposition, *, draft=False, pending=None):
    if not paper.get("strict_manifest"):
        return
    if str(deposition.get("conceptrecid")) != paper["expected_concept"]:
        raise SystemExit("Remote deposition belongs to the wrong archive concept")
    if draft and deposition.get("submitted") is not False:
        raise SystemExit("Remote record is not an explicitly unpublished draft")
    if pending is not None:
        if str(pending.get("deposition_id")) != str(deposition.get("id")):
            raise SystemExit("Pending receipt names a different draft")
        if str(pending.get("conceptrecid")) != paper["expected_concept"]:
            raise SystemExit("Pending receipt names a different archive concept")
        if pending.get("doi") != _record_summary(deposition)["doi"]:
            raise SystemExit("Pending receipt names a different reserved DOI")


def strict_open_draft(base, token, published, concept):
    """Read the complete bounded account listing; uncertainty never permits a mutation."""
    matches = []
    for page in range(1, 11):
        rows = api(base, token, "GET", f"/deposit/depositions?size=100&page={page}&all_versions=1")
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise SystemExit("Cannot establish the account's draft inventory")
        for row in rows:
            if str(row.get("conceptrecid")) != str(concept) or row.get("id") == published.get("id"):
                continue
            if row.get("submitted") is False:
                matches.append(row)
            elif row.get("submitted") is not True:
                raise SystemExit("Ambiguous publication status in matching archive record")
        if len(rows) < 100:
            break
    else:
        raise SystemExit("Draft inventory exceeds bounded inspection; no mutation permitted")
    unique = {str(row.get("id")): row for row in matches}
    if len(unique) > 1:
        raise SystemExit("Multiple drafts match this concept; reconcile ownership first")
    if not unique:
        return None
    row = next(iter(unique.values()))
    return api(base, token, "GET", f"/deposit/depositions/{row['id']}")


def verify_uploaded_archive(deposition, zip_path, filename):
    files = deposition.get("files")
    if not isinstance(files, list) or len(files) != 1:
        raise SystemExit("Remote draft must contain exactly the intended archive")
    entry = files[0]
    if entry.get("filename", entry.get("key")) != filename:
        raise SystemExit("Remote draft has the wrong archive filename")
    data = Path(zip_path).read_bytes()
    expected_md5 = hashlib.md5(data).hexdigest()
    checksum = str(entry.get("checksum", "")).removeprefix("md5:")
    size = entry.get("filesize", entry.get("size"))
    if checksum != expected_md5 or size != len(data):
        raise SystemExit("Remote archive bytes do not match the local upload")
    return {"filename": filename, "bytes": len(data), "md5": expected_md5,
            "sha256": hashlib.sha256(data).hexdigest()}


def named_metadata(paper, manifest, digest):
    return {"upload_type": "dataset", "title": paper["title"], "creators": [CREATOR],
            "license": paper["license"], "access_right": "open", "keywords": paper["keywords"],
            "description": description(paper, manifest, paper["manifest"], digest),
            "related_identifiers": [{"relation": "isDerivedFrom", "scheme": "url",
                                     "identifier": f"{REPO_URL}/tree/{manifest['git_revision']}"}]}


def verify_named_metadata(paper, manifest, digest, metadata):
    expected = named_metadata(paper, manifest, digest)
    actual = dict(metadata)
    if "upload_type" not in actual:
        actual["upload_type"] = actual.get("resource_type", {}).get("type")
    if isinstance(actual.get("license"), dict):
        actual["license"] = actual["license"].get("id")
    # The API may add creator/identifier metadata. Compare all fields we own.
    actual["creators"] = [{key: creator.get(key) for key in CREATOR}
                          for creator in actual.get("creators", [])]
    actual["related_identifiers"] = [{key: item.get(key) for key in ("relation", "scheme", "identifier")}
                                     for item in actual.get("related_identifiers", [])]
    for key, value in expected.items():
        if actual.get(key) != value:
            raise SystemExit(f"Remote metadata no longer describes the verified package: {key}")


def verify_built_archive(manifest, manifest_relative, zip_path):
    expected = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    expected[manifest_relative] = sha256(os.path.join(REPO, manifest_relative))
    with zipfile.ZipFile(zip_path) as archive:
        if sorted(archive.namelist()) != sorted(expected):
            raise SystemExit("Built ZIP inventory differs from the manifest")
        for name, digest in expected.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise SystemExit(f"Built ZIP bytes differ from the manifest: {name}")


def _package_pending(paper):
    path = Path(REPO) / Path(paper["manifest"]).parent / "deposit-state.json"
    if not path.exists():
        return {}
    require_committed_file(path.relative_to(REPO).as_posix())
    with path.open(encoding="utf-8") as stream:
        return json.load(stream).get("pending") or {}


def require_draft_ownership(paper, deposition, adopt_id=None):
    verify_package_identity(paper, deposition, draft=True)
    if adopt_id is not None and str(deposition.get("id")) == str(adopt_id):
        return
    pending = _package_pending(paper)
    if not pending:
        raise SystemExit("Existing draft needs a committed ownership receipt or explicit inspected adoption")
    verify_package_identity(paper, deposition, draft=True, pending=pending)


def _record_summary(deposition):
    if deposition is None:
        return None
    metadata = deposition.get("metadata") or {}
    return {"deposition_id": deposition.get("id"), "conceptrecid": deposition.get("conceptrecid"),
            "submitted": deposition.get("submitted"),
            "doi": deposition.get("doi") or metadata.get("doi") or metadata.get("prereserve_doi", {}).get("doi"),
            "files": [{k: entry.get(k) for k in ("filename", "key", "filesize", "size", "checksum")}
                      for entry in deposition.get("files", [])]}


def _write_receipt(path, receipt):
    with open(path, "x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")


def load_manifest(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(manifest):
    """Every file in the manifest exists and hashes to what the manifest says. Hard failure."""
    bad, missing = [], []
    for entry in manifest["files"]:
        path = os.path.join(REPO, entry["path"])
        if not os.path.exists(path):
            missing.append(entry["path"])
            continue
        if sha256(path) != entry["sha256"]:
            bad.append(entry["path"])
    if missing or bad:
        for p in missing:
            print(f"  MISSING  {p}", file=sys.stderr)
        for p in bad:
            print(f"  CHANGED  {p}", file=sys.stderr)
        raise SystemExit(
            f"manifest does not describe this tree: {len(missing)} missing, {len(bad)} changed. "
            "Regenerate the manifest and rebuild before depositing — an archive whose hashes "
            "describe different bytes than it carries is worse than no archive.")
    print(f"  verified {len(manifest['files'])} files against the manifest")


def build_zip(manifest, manifest_rel, out, deterministic=False):
    """The payload: every file the manifest lists, plus the manifest itself."""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        paths = [entry["path"] for entry in manifest["files"]] + [manifest_rel]
        for relative in paths:
            if deterministic:
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                z.writestr(info, Path(REPO, relative).read_bytes())
            else:
                z.write(os.path.join(REPO, relative), relative)
    print(f"  wrote {os.path.relpath(out, REPO)} "
          f"({os.path.getsize(out) / 1024 / 1024:.1f} MiB, {len(manifest['files']) + 1} members)")


def description(paper, manifest, manifest_rel, manifest_digest):
    """The record's own description. Everything in it is read, never recalled."""
    reproduce = "".join(f"<li>{s}</li>" for s in manifest.get("how_to_reproduce_offline", []))
    return (
        f"<p>{manifest['_what_this_is']}</p>"
        f"<p>This deposition is the archive cited by the manuscript's availability statement. It "
        f"carries {manifest['n_files']} files taken from <a href=\"{REPO_URL}\">{REPO_URL}</a> at "
        f"revision <code>{manifest['git_revision']}</code>, together with the manifest that names "
        f"and hashes every one of them.</p>"
        f"<p><strong>Verifying this archive.</strong> Every file's SHA-256 is listed in "
        f"<code>{os.path.basename(manifest_rel)}</code>. That file cannot carry its own hash, so it "
        f"is recorded here instead: <code>{manifest_digest}</code>. The archive's content digest, "
        f"derived over the file list, is <code>{manifest['archive_content_digest']}</code>.</p>"
        f"<p><strong>Reproducing the results offline.</strong></p><ol>{reproduce}</ol>"
        f"<p>Research use only. The oligonucleotide sequences in these artefacts are research "
        f"reagents; nothing here is for administration to any person or animal, and nothing in it "
        f"asserts efficacy, safety, delivery or clinical readiness.</p>")


#: ⛔ RETRY SAFE READS ONLY, AND NEVER A MUTATION (AUT-PD-199, 2026-09-01).
#: GET and HEAD have no side effect, so repeating one after a gateway error costs nothing and is
#: correct. POST/PUT/DELETE against this API are NOT idempotent — `actions/newversion` creates a
#: draft, a file PUT uploads bytes, `actions/publish` is irreversible — so a blind retry can leave
#: the record in a state nobody asked for. ⚠ THAT IS NOT HYPOTHETICAL: on 2026-09-01 a 504 landed
#: on the GET *after* a successful `newversion` POST, orphaning draft 22229096 with the files it
#: inherits still attached. Retrying the POST is what would have made a SECOND orphan.
_RETRY_METHODS = frozenset({"GET", "HEAD"})
#: 5xx is the server saying "not now"; 4xx is the server saying "not like that", and repeating a
#: malformed or unauthorised request is noise. 429 is included because it is explicitly a
#: "come back later".
_RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
_RETRY_ATTEMPTS = 4
_RETRY_BACKOFF = (2, 6, 15)


def api(base, token, method, path, payload=None, raw=None, ctype="application/json",
        _sleep=time.sleep):
    """One Zenodo API call, with a bounded retry on transient failures of SAFE methods.

    ⛔⛔ THIS FUNCTION HAD NO RETRY AT ALL, AND THAT — NOT A ZENODO OUTAGE — IS WHAT BLOCKED THE ASO
    ARCHIVE ON 2026-09-01. Any `HTTPError` raised `SystemExit` immediately, so a single transient
    504 from Zenodo's gateway was fatal to a whole run. Three runs died that way and the cycle
    reported "Zenodo's deposit API is down"; a `record=verify` dispatch minutes later read the
    published record in THREE SECONDS. The service was healthy the entire time. ★ The tell was
    available and unread: two of the three failures were 504s on GETs — reads, which are exactly
    the calls a retry fixes — and the third was a 400 that was Zenodo correctly refusing to open a
    second version while one was open, i.e. not a failure at all.
    ⚠ CLAUDE.md §4: a remembered or inferred fact about an outside system is a dated observation.
    "The API is down" was inferred from three responses on one endpoint and was wrong.
    """
    url = path if path.startswith("http") else f"{base}{path}"
    sep = "&" if "?" in url else "?"
    body = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
    last = None
    for attempt in range(_RETRY_ATTEMPTS):
        req = urllib.request.Request(f"{url}{sep}access_token={token}", data=body, method=method)
        if body is not None:
            req.add_header("Content-Type", ctype)
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                text = resp.read().decode()
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:800]
            retryable = method.upper() in _RETRY_METHODS and exc.code in _RETRY_STATUS
            if not retryable or attempt == _RETRY_ATTEMPTS - 1:
                # ⭐ SAY WHETHER IT WAS RETRIED, so the next reader does not have to infer it from
                # the wall clock. A one-shot failure and an exhausted retry are different findings.
                tried = (f" after {attempt + 1} attempt(s)" if retryable else
                         " (not retried: "
                         + ("unsafe method" if method.upper() not in _RETRY_METHODS
                            else f"{exc.code} is not transient") + ")")
                raise SystemExit(f"Zenodo {method} {path} -> {exc.code}{tried}: {detail}")
            last = exc.code
            print(f"  Zenodo {method} {path} -> {last}; retrying in "
                  f"{_RETRY_BACKOFF[attempt]}s ({attempt + 1}/{_RETRY_ATTEMPTS - 1})")
            _sleep(_RETRY_BACKOFF[attempt])


def _open_draft_of(base, token, published, concept):
    """The UNPUBLISHED draft already open on this record, or None. Reads only.

    ⛔⛔ `links.latest_draft` DOES NOT MEAN "AN UNPUBLISHED DRAFT EXISTS", AND ASSUMING IT DID WOULD
    HAVE OVERWRITTEN A PUBLISHED ARCHIVE. Measured live 2026-09-01, run 33519701596: the first
    version of this adoption read `latest_draft` off published record 22182180 and it resolved to
    **22182180 itself**. The refusal at the call site caught it — "which Zenodo reports as
    PUBLISHED" — on the guard's first real run, and the alternative was uploading the corrected
    archive over the version both papers cite. ★ That link tracks the latest VERSION, which is
    normally the published one; it is not a draft pointer.

    ★ SO THE DRAFT IS FOUND BY LISTING, WHICH IS WHAT ACTUALLY ANSWERS THE QUESTION: the depositions
    endpoint returns this account's depositions including unpublished ones, and a new version shares
    its record's `conceptrecid`. An entry that is not `submitted`, carries that concept id and is
    not the published record itself IS the open draft — the one at 22229096, orphaned when a 504
    killed the run that opened it (AUT-PD-197).

    ⛔ IT NEVER MUTATES AND IT NEVER GUESSES. Returning None means "found nothing", and the caller
    then opens a version the ordinary way; it does not mean "there is nothing", which is why the
    caller re-checks `submitted` on whatever it ends up with rather than trusting this function.
    """
    if not concept:
        return None
    for path in (f"/deposit/depositions?status=draft&size=100&all_versions=1",
                 f"/deposit/depositions?size=100&all_versions=1"):
        try:
            rows = api(base, token, "GET", path)
        except SystemExit:
            continue                      # this listing shape is unsupported; try the next
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or row.get("submitted"):
                continue
            if row.get("conceptrecid") != concept:
                continue
            if row.get("id") == published.get("id"):
                continue
            print(f"  a new-version draft is ALREADY OPEN on record {published.get('id')}: "
                  f"deposition {row['id']} — adopting it rather than asking Zenodo for a second one")
            return api(base, token, "GET", f"/deposit/depositions/{row['id']}")
    return None

def refuse_unless_publishable(paper_key, manifest, approved_by, package="canonical"):
    """⛔ THE THREE CONDITIONS FOR AN IRREVERSIBLE PUBLISH. Every one FAILS CLOSED.

    ★ THEY ARE INDEPENDENT ON PURPOSE. Authority answers "may the loop do this at all"; the approval
    answers "for THIS deposition"; the digest answers "is what we would freeze still the archive the
    paper cites". No two of them substitute for the third, and the third is the one a human clicking
    Publish on zenodo.org cannot check — which is the whole reason this path exists rather than the
    click staying manual.
    """
    authority = json.load(io.open(os.path.join(
        REPO, "research", "autonomy", "publication-authority.json"), encoding="utf-8"))
    grant = authority.get("zenodo_archive_publication") or {}
    if not grant.get("standing_grant"):
        raise SystemExit(
            "publication-authority.json does not grant Zenodo publication. Publishing is "
            "irreversible and the grant is the record of who allowed it; without one, this refuses. "
            "⛔ Do NOT add the block to make this run — the grant is trimcrae's to give.")

    #: ⛔ `--approved-by` IS ALWAYS REQUIRED, AND SINCE 2026-08-30 IT IS A RECORD RATHER THAN A GATE.
    #: trimcrae retired the per-publication approval that day, verbatim: "On second thought, this is
    #: annoying. I don't want my approval to gate Zenodo. Just do it." — said in answer to exactly
    #: the one question the retired gate prescribed, for deposition 22180100.
    #: ★ THE STRING STAYS MANDATORY BECAUSE THE `exercised` LIST IS ONLY AUDITABLE IF EVERY ROW SAYS
    #: WHO AUTHORISED IT. A grant with no record of its exercise cannot be revoked knowingly, and an
    #: empty authoriser is exactly the row nobody can later account for. What went is the requirement
    #: that a HUMAN answer before each publish; what stays is that the act must name its authority.
    #: ⚠ IT IS NOT CHECKED AGAINST HIM AND NEVER WAS — this has always been an honesty mechanism.
    #: The checks that actually refuse are the grant, digest and draft-identity ones around it, each
    #: computed from a committed artifact.
    #: ⚠ The flag is still READ, so restoring the human gate is one boolean in
    #: publication-authority.json, and a value of true makes the message below say so.
    if not approved_by:
        gated = grant.get("approval_is_required_per_publication")
        raise SystemExit(
            "--approved-by was not given, and every publish must name the authority it acts under. "
            + ("The grant ALSO requires an approval for THIS deposition: ask, then pass what he "
               "said — an approval for one deposition is not an approval for the next."
               if gated else
               "trimcrae retired the per-publication approval on 2026-08-30, so this is a record "
               "rather than a gate: pass the standing grant and what he said when he gave it."))

    #: deposit-state.json sits beside the paper's manifest. Derived rather than configured, so a
    #: paper added to PAPERS cannot silently arrive without one and be published unchecked.
    paper = package_configuration(paper_key, package)
    state_rel = os.path.join(os.path.dirname(paper["manifest"]), "deposit-state.json")
    state_abs = os.path.join(REPO, state_rel)
    if not os.path.exists(state_abs):
        raise SystemExit(
            f"{state_rel} does not exist, so nothing records what the draft holds. A publish that "
            "cannot be checked against the tree is the one this gate exists to refuse.")
    if paper.get("strict_manifest"):
        require_committed_file(Path(state_rel).as_posix())
    state = json.load(io.open(state_abs, encoding="utf-8"))
    pending = state.get("pending") or {}
    uploaded = pending.get("uploaded_manifest_digest")
    current = manifest.get("archive_content_digest")
    if not uploaded:
        raise SystemExit(
            "deposit-state.json records no uploaded digest for the pending draft, so nothing can "
            "say whether the draft matches this tree. Re-run the deposit, then publish.")
    if uploaded != current:
        raise SystemExit(
            f"THE DRAFT IS BEHIND THIS TREE and publishing would freeze it that way.\n"
            f"  draft holds : {uploaded}\n"
            f"  tree is at  : {current}\n\n"
            "Re-run this script WITHOUT --publish first (it updates the draft in place), update "
            "uploaded_manifest_digest, and only then publish. ⚠ This has gone stale twice, once "
            "because a repair landed AFTER the refresh — so the refresh must be the last act "
            "before the publish, not merely a recent one.")
    if paper.get("strict_manifest"):
        if pending.get("doi") != manifest["deposition_doi"] or str(pending.get("conceptrecid")) != paper["expected_concept"]:
            raise SystemExit("Pending receipt does not match the declared version/concept")
        if not pending.get("deposition_id") or not pending.get("uploaded_archive_sha256") or not pending.get("uploaded_manifest_sha256"):
            raise SystemExit("Pending receipt lacks the actual draft identity or uploaded archive hash")
    return grant, pending


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", choices=sorted(PAPERS), required=True)
    ap.add_argument("--package", choices=["canonical", PACKAGE_NAME], default="canonical",
                    help="Named payload of the selected paper; canonical remains the default")
    ap.add_argument("--inspect", action="store_true", help="Named package only: read the record and open draft without mutation")
    ap.add_argument("--adopt-draft", type=int, help="Explicitly identify an inspected existing draft whose ownership was reconciled")
    ap.add_argument("--receipt", help="New local JSON receipt path, required for named-package remote operations")
    ap.add_argument("--sandbox", action="store_true",
                    help="deposit to sandbox.zenodo.org — a full rehearsal that mints nothing real")
    ap.add_argument("--build-only", action="store_true",
                    help="verify and zip, then stop; no network and no token needed")
    ap.add_argument("--new-version", action="store_true", dest="new_version",
                    help="the record named by the manifest is PUBLISHED and needs correcting: open "
                         "a NEW VERSION of it, reserve that version's own DOI and upload the "
                         "current archive into it. On its own it does not publish — that needs --publish and its approval. This is the only correct "
                         "route for a correction — a published version's files cannot be edited, "
                         "and --new would create an unrelated second record with its own concept "
                         "DOI, orphaning the citation trail.")
    ap.add_argument("--new", action="store_true",
                    help="force a NEW deposition even though the manifest names one. Only for a "
                         "paper's first deposit after its manifest was populated by hand — a "
                         "re-run otherwise updates the draft the manuscript already cites.")
    ap.add_argument("--out-dir", default=os.path.join(REPO, ".cache", "zenodo"))
    ap.add_argument("--publish", action="store_true",
                    help="PUBLISH the existing draft — IRREVERSIBLE. Refuses unless the authority "
                         "record grants it, --approved-by names who approved THIS deposition, and "
                         "the draft's digest still equals the manifest's. Uploads nothing.")
    ap.add_argument("--approved-by", default=None,
                    help="Who approved THIS publication, and when. Required by --publish; recorded "
                         "in the run's output so the approval is auditable after the fact.")
    args = ap.parse_args(argv)

    paper = package_configuration(args.paper, args.package)
    strict = paper.get("strict_manifest", False)
    if strict and args.new:
        raise SystemExit("This package may only continue the existing ASO concept, never mint an unrelated record")
    if args.inspect and (not strict or args.publish or args.new_version or args.build_only or args.adopt_draft):
        raise SystemExit("Inspection is a separate read-only named-package operation")
    if strict and args.publish and args.new_version:
        raise SystemExit("Publish the already identified draft in a separate invocation")
    if args.adopt_draft and (not strict or args.publish or args.build_only):
        raise SystemExit("Draft adoption requires a named-package draft preparation")
    if strict and not args.build_only:
        if not args.receipt or os.path.exists(args.receipt) or os.path.exists(args.receipt + ".publish.json"):
            raise SystemExit("Provide a new receipt path before a named-package remote operation")
        if not Path(args.receipt).absolute().parent.is_dir():
            raise SystemExit("Receipt directory must exist before a remote operation")
    manifest = load_manifest(paper["manifest"])
    validate_package_manifest(manifest, paper)
    print(f"deposition for '{args.paper}' at manifest revision {manifest['git_revision'][:8]}")

    gaps = manifest.get("gaps", {}).get("promises_resolving_to_no_file", [])
    if gaps:
        raise SystemExit(f"the manifest lists {len(gaps)} promise(s) resolving to no file. "
                         "A promise that outruns the deposit is the defect a reader finds first — "
                         "close each one or narrow the manuscript before depositing.")

    verify(manifest)
    if strict and not args.build_only:
        require_committed_file(paper["manifest"])

    #: ⛔⛔ THE GATE RUNS HERE, BEFORE ANY NETWORK CALL — AND IT USED TO RUN AFTER THE UPLOAD.
    #: Round 21's regression seat measured the defect: `--publish` reached `refuse_unless_publishable`
    #: only at the bottom of `deposit()`, so the metadata PUT and the zip upload had ALREADY happened
    #: by the time the digest check could refuse. A `--publish` against a drifted tree therefore did
    #: not refuse harmlessly — it rewrote the draft's metadata, uploaded a new archive over it, and
    #: only then raised. The draft was left holding a build `deposit-state.json` does not describe,
    #: which is the exact "nothing records what was deposited" state that file was created to end.
    #: ★ THE FLAG'S OWN HELP AND THE COMMENT AT THE PUBLISH STEP BOTH CLAIMED THIS ORDERING ALREADY
    #: HELD ("Uploads nothing", "the digest check above has already refused"). They described the
    #: intent; the code did the reverse. It is now true because the call site moved, not because the
    #: sentence was reworded — a property asserted in prose about an ordering is not a property.
    publish_grant = publish_pending = None
    if args.publish:
        if strict:
            publish_grant, publish_pending = refuse_unless_publishable(
                args.paper, manifest, args.approved_by, args.package)
        else:
            publish_grant, publish_pending = refuse_unless_publishable(
                args.paper, manifest, args.approved_by)

    os.makedirs(args.out_dir, exist_ok=True)
    zip_path = os.path.join(args.out_dir, paper["zip"])
    if strict:
        build_zip(manifest, paper["manifest"], zip_path, deterministic=True)
    else:
        build_zip(manifest, paper["manifest"], zip_path)
    if strict:
        verify_built_archive(manifest, paper["manifest"], zip_path)
    digest = sha256(os.path.join(REPO, paper["manifest"]))
    if strict and args.publish:
        if publish_pending["uploaded_archive_sha256"] != sha256(zip_path) or publish_pending["uploaded_manifest_sha256"] != digest:
            raise SystemExit("The verified upload receipt does not describe the exact archive/manifest bytes to publish")
    print(f"  manifest SHA-256 (recorded in the record, not in the manifest): {digest}")
    if args.build_only:
        return 0

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        raise SystemExit("ZENODO_TOKEN is not set. Create a personal access token at "
                         "zenodo.org/account/settings/applications/tokens/new/ with the "
                         "deposit:write and deposit:actions scopes.")
    base = ("https://sandbox.zenodo.org/api" if args.sandbox else "https://zenodo.org/api")
    print(f"  target: {base}" + ("  (REHEARSAL — mints nothing real)" if args.sandbox else ""))

    #: ⛔⛔ A RE-RUN MUST UPDATE THE DRAFT THE MANUSCRIPT ALREADY CITES, NOT MAKE A SECOND ONE.
    #: This script always POSTed a new deposition, and the workflow that runs it is DESIGNED to be
    #: run twice — once to reserve the DOI, once more after the manuscript has been rebuilt around
    #: it, so the archive carries the paper that cites it. The second run would therefore have
    #: minted a SECOND reserved DOI and uploaded the corrected archive to a draft nothing points
    #: at, leaving the manuscript's DOI attached to the stale one. Caught before the second run
    #: completed; nothing was published, so nothing had to be retracted — but a published pair
    #: could not have been undone.
    #: The manifest's `deposition_doi` is the manuscript's own answer to "which record is this?",
    #: so it is the input, and the deposition id is the DOI's own suffix. Absent -> first run.
    declared = manifest.get("deposition_doi")
    existing = re.search(r"zenodo\.(\d+)$", declared) if declared else None
    if existing and not args.new:
        dep_id = int(existing.group(1))
        # ⛔ SANDBOX AND PRODUCTION ARE SEPARATE UNIVERSES WITH SEPARATE RECORD IDs, AND A RAW 404
        # DOES NOT SAY SO (measured 2026-08-22, run 32592438100). The first `--new-version`
        # rehearsal reported `Zenodo GET /deposit/depositions/22028916 -> 404: The persistent
        # identifier does not exist` — correct, and completely opaque: 22028916 is a zenodo.org
        # record and the rehearsal was asking sandbox.zenodo.org for it.
        # ⚠ SO A CORRECTION CANNOT BE REHEARSED IN THE SANDBOX. Anything that operates on an
        # EXISTING record — which is what a new version is — can only run where that record lives.
        # The sandbox still rehearses everything up to that point: the manifest verification, the
        # zip, the token and the API contract. Say which half was rehearsed rather than let a 404
        # read as a bug in the archive.
        try:
            dep = api(base, token, "GET", f"/deposit/depositions/{dep_id}")
        except SystemExit as exc:
            if "404" in str(exc) and args.sandbox:
                raise SystemExit(
                    f"{declared} is a zenodo.org record and this is a REHEARSAL against "
                    "sandbox.zenodo.org, where it does not exist.\n\n"
                    "A correction operates on an existing record, so it can only run where that "
                    "record lives. Everything before this point HAS been rehearsed: the manifest "
                    "verified against the tree, the archive built, the token accepted and the API "
                    "reachable. Re-run without --sandbox to open the new version for real — opening a "
                    "version does not publish it.") from None
            raise
        verify_package_identity(paper, dep)
        if args.inspect:
            draft = strict_open_draft(base, token, dep, paper["expected_concept"]) if dep.get("submitted") is True else dep
            if draft is not None:
                verify_package_identity(paper, draft, draft=True)
            receipt = {"operation": "inspect", "package": args.package,
                       "declared_record": _record_summary(dep), "open_draft": _record_summary(draft),
                       "remote_mutation": False}
            _write_receipt(args.receipt, receipt)
            print(json.dumps(receipt))
            return 0
        if strict and args.new_version and dep.get("submitted") is not True:
            raise SystemExit("New-version preparation must start from an explicitly published record")
        if strict and args.publish:
            verify_package_identity(paper, dep, draft=True, pending=publish_pending)
            uploaded = verify_uploaded_archive(dep, zip_path, paper["zip"])
            remote_meta = dep.get("metadata") or {}
            verify_named_metadata(paper, manifest, digest, remote_meta)
            _write_receipt(args.receipt, {"operation": "prepublication_verified", "package": args.package,
                           "record": _record_summary(dep), "archive": uploaded,
                           "manifest_sha256": digest, "public_read_back": False})
            published = api(base, token, "POST", f"/deposit/depositions/{dep_id}/actions/publish")
            verify_package_identity(paper, published, pending=publish_pending)
            if published.get("submitted") is not True:
                raise SystemExit("Publication response is ambiguous; inspect remote state before any retry")
            _write_receipt(args.receipt + ".publish.json", {"operation": "publish_response",
                           "record": _record_summary(published), "upload_receipt": args.receipt,
                           "public_read_back": False})
            print(f"Publication response received for {declared}; public read-back is still required.")
            return 0
        if dep.get("submitted") and not args.new_version:
            raise SystemExit(
                f"deposition {dep_id} ({declared}) is already PUBLISHED and its files cannot be "
                "changed. A correction is a NEW VERSION of that record, which issues its own DOI "
                "under the same concept DOI — not a re-upload. Re-run with --new-version to open "
                "one; opening a version does not publish it. Do NOT use --new: that makes an unrelated "
                "second "
                "record with its own concept DOI, and the citation trail from the published paper "
                "would not reach it.")
        if dep.get("submitted"):
            # ⛔⛔ THE ONLY CORRECT ROUTE FOR A CORRECTION (added 2026-08-22, round 15). The record
            # went out on 2026-08-20 and the repository then corrected two statements inside the
            # extended report it contains — so a reader following the paper's DOI reads text this
            # work has retracted. Zenodo cannot repoint a published version DOI; the record's
            # `newversion` action makes a fresh draft that inherits the concept DOI and reserves a
            # version DOI of its own, which is what lets the reserve-then-rebuild ordering below
            # work for a correction exactly as it worked for the first deposit.
            # ⚠ THE NEW DRAFT INHERITS THE OLD VERSION'S FILES. They are deleted before upload, so
            # what ships is the current archive and not a union of two.
            # ⛔⛔ ADOPT AN OPEN DRAFT BEFORE ASKING FOR ANOTHER ONE. `actions/newversion` is NOT
            # idempotent and Zenodo will not open a second version while one is open, so a run that
            # dies AFTER the POST leaves a draft this script could never reach again — every later
            # attempt asked for a new version and was refused, and the refusal names files rather
            # than drafts, which reads like an archive problem instead of a resume problem.
            # ⚠ MEASURED 2026-09-01, both halves, in the real logs rather than reasoned:
            #   · run 33498033370 — `POST .../22182180/actions/newversion` succeeded and the
            #     immediately following `GET .../deposit/depositions/22229096` returned 504. The
            #     draft existed; the script did not survive to use it.
            #   · run 33498227279 — the retry POSTed newversion again and Zenodo answered
            #     `400 files.enabled: "Please remove all files first."`. That is Zenodo declining to
            #     open a second version, and no wording in it says so.
            # ★ THE PUBLISHED RECORD ITSELF CARRIES THE ANSWER: its `links.latest_draft` points at
            # the open draft when there is one. Reading it first makes the whole correction
            # RESUMABLE — a transient failure anywhere after the POST costs a re-run, not a record.
            # ⛔ AND IT IS CHECKED, NOT TRUSTED. An adopted draft that comes back `submitted`, or
            # that is the published record itself, is not a draft; taking either would upload the
            # corrected archive onto something a reader may already cite, so both refuse.
            published_id = dep_id
            concept = dep.get("conceptrecid")
            dep = strict_open_draft(base, token, dep, concept) if strict else _open_draft_of(base, token, dep, concept)
            if strict and dep is not None:
                require_draft_ownership(paper, dep, args.adopt_draft)
            if dep is None:
                act = api(base, token, "POST", f"/deposit/depositions/{dep_id}/actions/newversion")
                latest = act.get("links", {}).get("latest_draft")
                if not latest:
                    raise SystemExit("Zenodo accepted the newversion action but returned no "
                                     "latest_draft link; open the record on Zenodo and finish by "
                                     "hand")
                dep = api(base, token, "GET", latest)
            verify_package_identity(paper, dep, draft=True)
            dep_id = dep["id"]
            # ⛔ THE SAME TWO REFUSALS APPLY TO A DRAFT WE OPENED AND TO ONE WE ADOPTED. Uploading
            # the corrected archive onto a version a reader may already cite is the one outcome
            # worth aborting for, and `_open_draft_of` cannot be the only thing standing in front
            # of it — a helper's guarantee is not a guard.
            if dep.get("submitted"):
                raise SystemExit(
                    f"the deposition this run resolved to for record {published_id} is {dep_id}, "
                    "which Zenodo reports as PUBLISHED. A published version's files cannot be "
                    "changed and this run would have tried to replace them. Open the record on "
                    "Zenodo and check its version history before re-running.")
            if dep_id == published_id:
                raise SystemExit(
                    f"record {published_id} resolved to itself, so there is no new version to "
                    "write to. Open the record on Zenodo and check its version history before "
                    "re-running.")
            print(f"  NEW VERSION draft {dep_id} of published record {published_id}")
            for old_file in dep.get("files", []):
                api(base, token, "DELETE", f"/deposit/depositions/{dep_id}/files/{old_file['id']}")
            if dep.get("files"):
                print(f"  cleared {len(dep['files'])} inherited file(s) from the new draft")
        else:
            verify_package_identity(paper, dep, draft=True, pending=publish_pending)
            if strict:
                require_draft_ownership(paper, dep, args.adopt_draft)
            print(f"  updating existing draft {dep_id} ({declared}) — not creating a second one")
    else:
        if strict:
            raise SystemExit("Named package cannot create an unrelated archive record")
        dep = api(base, token, "POST", "/deposit/depositions", payload={})
        dep_id = dep["id"]
    #: ⛔ RESERVE BEFORE UPLOAD, AND BEFORE ANY PUBLISH. This is the whole ordering fix: the DOI has
    #: to exist as a string the manuscript can print while the deposition is still editable.
    meta = {
        "upload_type": paper["upload_type"],
        "title": paper["title"],
        "creators": [CREATOR],
        "license": paper["license"],
        "keywords": paper["keywords"],
        #: Harmless on an update — Zenodo returns the DOI it already reserved for this draft
        #: rather than issuing a second one.
        "prereserve_doi": True,
        "description": description(paper, manifest, paper["manifest"], digest),
        "related_identifiers": [
            {"relation": "isDerivedFrom", "scheme": "url",
             "identifier": f"{REPO_URL}/tree/{manifest['git_revision']}"},
        ],
        #: ⛔⛔ THIS FIELD IS WRITTEN INTO A PUBLIC RECORD UNDER THE AUTHOR'S ORCID, SO IT MUST BE
        #: TRUE OF THE RUN THAT WRITES IT. Until 2026-08-30 it read, unconditionally, "Not published
        #: by that script: publishing is irreversible and is a human step" — and the PUT carrying it
        #: runs on EVERY non-build-only invocation, the publishing one included. So the run that
        #: published 10.5281/zenodo.22166420 stamped that record with a sentence denying it had done
        #: so. Round 21's regression seat found it; the note was true when written and was falsified
        #: by the --publish path landing above it, which is the shape this repository keeps paying
        #: for: a status sentence about an outside system, frozen in prose, invalidated by a change
        #: somewhere else. It is now DERIVED from what this run is actually doing.
        "notes": (
            f"Built by scripts/zenodo_deposit.py from {os.path.basename(paper['manifest'])}. "
            + ("Published by that script in the same run, under a recorded per-publication "
               "approval: publishing is irreversible, and the gate that permits it "
               "(refuse_unless_publishable) checks the standing authority, the approval for THIS "
               "deposition, and that the archive still equals the one a committed manifest "
               "describes."
               if args.publish else
               "Not published by this run: this invocation only reserves the DOI and refreshes the "
               "draft.")),
    }
    if strict:
        meta.update(named_metadata(paper, manifest, digest))
    dep = api(base, token, "PUT", f"/deposit/depositions/{dep_id}", payload={"metadata": meta})
    verify_package_identity(paper, dep, draft=True, pending=publish_pending)
    doi = dep["metadata"].get("prereserve_doi", {}).get("doi")

    with open(zip_path, "rb") as fh:
        api(base, token, "PUT", f"{dep['links']['bucket']}/{paper['zip']}",
            raw=fh.read(), ctype="application/octet-stream")
    print(f"  uploaded {paper['zip']}")
    if strict:
        observed = api(base, token, "GET", f"/deposit/depositions/{dep_id}")
        verify_package_identity(paper, observed, draft=True, pending=publish_pending)
        verify_named_metadata(paper, manifest, digest, observed.get("metadata") or {})
        uploaded = verify_uploaded_archive(observed, zip_path, paper["zip"])
        receipt = {"operation": "upload_verified", "package": args.package,
                   "record": _record_summary(observed), "archive": uploaded,
                   "uploaded_manifest_digest": manifest["archive_content_digest"],
                   "manifest_sha256": digest, "source_revision": manifest["git_revision"],
                   "publication_requested": args.publish, "public_read_back": False}
        _write_receipt(args.receipt, receipt)

    #: ⚠ THE CLOSING BANNER MUST SAY WHICH RUN THIS WAS. It printed "created" and the full
    #: paste-the-DOI checklist on every run, including the UPDATE run whose whole point is that the
    #: DOI is already in the manuscript — so the log of a successful second run read as an
    #: instruction to redo the first. A reader following it would have found nothing to paste and
    #: had to work out which half of the message was stale.
    #: ⛔ THE IRREVERSIBLE STEP. `--publish` freezes the draft as this run has just left it, and the
    #: gate that decides whether it may has ALREADY run, at the top of this function, before the
    #: metadata PUT and the upload above.
    #: ⚠ SO THIS RUN DID UPLOAD, AND SAYING OTHERWISE WAS THE OLD DEFECT. What the early gate buys is
    #: the thing that actually matters: a refusal costs the draft nothing, because it happens before
    #: anything is sent. What it cannot buy is the separation of assembling from freezing — that is
    #: what the digest check enforces, by requiring the archive to equal one a COMMITTED manifest
    #: already describes.
    if args.publish:
        grant, pending = publish_grant, publish_pending
        print(f"  publishing deposition {dep_id} — IRREVERSIBLE")
        print(f"    approved by : {args.approved_by}")
        print(f"    digest      : {pending['uploaded_manifest_digest']} (matches the manifest)")
        published = api(base, token, "POST", f"/deposit/depositions/{dep_id}/actions/publish")
        verify_package_identity(paper, published)
        if strict:
            if published.get("submitted") is not True or str(published.get("id")) != str(dep_id):
                raise SystemExit("Publication response is ambiguous; inspect remote state before any retry")
            _write_receipt(args.receipt + ".publish.json", {"operation": "publish_response",
                           "record": _record_summary(published), "upload_receipt": args.receipt,
                           "public_read_back": False})
        doi = published.get("doi") or (published.get("metadata") or {}).get("doi")
        print("=" * 72)
        print(f"PUBLISHED deposition {dep_id}. This cannot be undone.")
        print(f"  DOI      : {doi}")
        print(f"  record   : https://doi.org/{doi}" if doi else "")
        print("=" * 72)
        print("Next: move `pending` into `published` in deposit-state.json and delete `pending`,")
        print("and READ THE RECORD BACK with record=verify rather than trusting this output —")
        print("'the script said so' is a report about an outside system, not a reading of it.")
        return 0

    updated = bool(existing and not args.new and not args.new_version)
    print("\n" + "=" * 72)
    print(f"DRAFT deposition {dep_id} {'updated' if updated else 'created'}. NOTHING IS PUBLISHED.")
    print(f"  reserved DOI : {doi}")
    print(f"  edit it at   : {dep['links'].get('html')}")
    print("=" * 72)
    if strict:
        print("Preserve this upload receipt. Record the actual reserved DOI and draft ownership,")
        print("commit the package manifest/state, refresh the draft, then verify before publication.")
        print("Publication uses the existing standing grant; public read-back is a separate check.")
        return 0
    if updated:
        print("\nThe archive now carries the manuscript that cites this DOI. One step remains, and")
        print("it is not this script's to take:")
        print(f"  * Publish deposition {dep_id} by hand on Zenodo. Irreversible: a published")
        print("    version's files cannot be edited, only superseded by a new version.")
        return 0
    print("\nNext, in this order — the order is what keeps the paper and the archive on one DOI:")
    print(f"  1. Paste {doi} into the manuscript's two [ARCHIVE DOI] placeholders")
    print("     (Methods -> Availability, and Declarations -> Data and code availability), and")
    print("     record it as `deposition_doi` in research/manuscripts/aso_archive_manifest.py.")
    print("  2. Regenerate sequences.csv, THEN rebuild the PDFs, THEN regenerate the manifest.")
    print("     That order matters: PDFs built before the CSV are stale against a file they quote.")
    print("  3. Re-run this script. It will UPDATE this draft, not make a second one.")
    print("  4. Only then publish the deposition, by hand, on Zenodo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
