#!/usr/bin/env python3
"""Drive aiXiv's automated adversarial review from the hardening loop, as an EXTERNAL seat.

WHY THIS EXISTS. `paper-hardening` runs five blind seats per round, and every seat costs model
spend. aiXiv (https://aixiv.science) runs its own adversarial reviewer and exposes it over HTTP,
so some of that spend can be moved off our own budget. This client is the seam.

⛔ THE CONSTRAINT THAT DECIDES HOW THIS CAN BE USED, READ OFF THE SPEC RATHER THAN ASSUMED.
`POST /api/start_attack_review` requires `aixiv_id` AND `aixiv_url` (openapi.json -> StartReviewIn,
fetched 2026-08-22 to literature/aixiv-api-surface-2026-08-22/), and
`GET /api/get_pending-review-submissions` describes itself as returning "submissions with status
'Under Review'". The reviewer is therefore keyed to a paper that ALREADY EXISTS ON aiXiv. There is
no endpoint that reviews a local file.

⚠ SO THIS CANNOT BE A DROP-IN REPLACEMENT FOR A BLIND SEAT ON A PINNED COMMIT. `paper-hardening` §3
requires every seat to review a pinned SHA of a file in this repository; an aiXiv review requires
the text to be uploaded to a third party first. Those are different acts with different
consequences, and conflating them would turn a review round into a publication.

TWO HONEST SHAPES, and the second is unverified:
  1. POST-POSTING. For a paper we have DECIDED to put on aiXiv, its review is a free extra seat.
  2. PRIVATE-FIRST. `SubmissionCreate` carries `is_public: integer`, so a submission can in
     principle be created non-public, reviewed, and made public later. ⚠ NOTHING HERE VERIFIES THAT
     A NON-PUBLIC SUBMISSION IS REVIEWABLE — no account has been created, so it has never been run.
     Treat `--public 0` as an untested claim about aiXiv's behaviour, not a guarantee of privacy.

⛔ SUBMITTING IS OUTWARD-FACING AND THIS SCRIPT WILL NOT DO IT SILENTLY. `submit` refuses to run
without --i-understand-this-is-outward-facing, in the same spirit as scripts/zenodo_deposit.py
never publishing: uploading a manuscript to a third-party server is not reversible by deleting a
row, because it may have been fetched, cached or indexed in between (CLAUDE.md §3).

    python3 scripts/aixiv_review.py submit   --pdf <path> --meta <path.json> --dry-run
    AIXIV_TOKEN=... python3 scripts/aixiv_review.py submit --pdf <p> --meta <m> \
        --public 0 --i-understand-this-is-outward-facing
    AIXIV_TOKEN=... python3 scripts/aixiv_review.py review --aixiv-id <id> --version v1.0 \
        --pdf <path> --seed 20260822
    python3 scripts/aixiv_review.py fetch    --aixiv-id <id> --version v1.0 --out <dir>

`fetch` needs no token: `POST /api/get-review` carries no security requirement in the spec.
"""
import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("AIXIV_BASE", "https://aixiv.science")

#: Endpoints, each one taken from the fetched openapi.json rather than from documentation prose.
EP_SUBMIT = "/api/agent/submit"
EP_REVIEW = "/api/start_attack_review"
EP_GET_REVIEW = "/api/get-review"

#: Required by SubmissionCreate. Listed here so a missing key fails BEFORE the network call, with a
#: message naming the field, rather than as a 422 whose body we then have to interpret.
REQUIRED_META = (
    "title", "authorship_type", "authors", "corresponding_author",
    "category", "keywords", "license", "doc_type",
)


class AixivError(RuntimeError):
    pass


def _request(path, *, data=None, headers=None, method="POST", timeout=180):
    """One HTTP call. Returns parsed JSON, or raises AixivError carrying the server's own body.

    ⚠ THE ERROR BODY IS THE DIAGNOSTIC. A 422 from this API names the field it rejected; swallowing
    it and raising "submission failed" would cost exactly the observation that fixes the call
    (CLAUDE.md §4).
    """
    url = BASE.rstrip("/") + path
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:2000]
        raise AixivError(f"HTTP {e.code} from {path}: {detail}") from None
    except urllib.error.URLError as e:
        raise AixivError(f"could not reach {url}: {e.reason}") from None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise AixivError(f"{path} returned non-JSON: {body[:500]}") from None


def _multipart(fields, files):
    """Build a multipart/form-data body. Pure stdlib on purpose — this runs on a CI runner too."""
    boundary = "----aixiv" + uuid.uuid4().hex
    out = bytearray()
    for name, value in fields.items():
        out += f"--{boundary}\r\n".encode()
        out += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        out += f"{value}\r\n".encode()
    for name, path in files.items():
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        fname = os.path.basename(path)
        with open(path, "rb") as fh:
            blob = fh.read()
        out += f"--{boundary}\r\n".encode()
        out += (f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{fname}"\r\n').encode()
        out += f"Content-Type: {ctype}\r\n\r\n".encode()
        out += blob + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def _token(required=True):
    tok = os.environ.get("AIXIV_TOKEN", "").strip()
    if not tok and required:
        raise AixivError(
            "AIXIV_TOKEN is not set. Mint one with POST /api/agents/{agent_id}/tokens — the plain "
            "token is shown ONLY ONCE, so store it as a GitHub Actions secret when you create it.")
    return tok


def load_meta(path, public):
    with open(path) as fh:
        meta = json.load(fh)
    missing = [k for k in REQUIRED_META if not meta.get(k)]
    if missing:
        raise AixivError(f"{path} is missing required SubmissionCreate field(s): {', '.join(missing)}")
    meta["is_public"] = int(public)
    meta.setdefault("submitter_type", "agent")
    return meta


def cmd_submit(args):
    meta = load_meta(args.meta, args.public)
    if args.dry_run:
        print(f"DRY RUN — would POST {BASE}{EP_SUBMIT}")
        print(f"  file:     {args.pdf} ({os.path.getsize(args.pdf)} bytes)")
        print(f"  is_public: {meta['is_public']}"
              + ("  (public — this is a PUBLICATION)" if meta["is_public"] else "  (non-public — UNVERIFIED, see module docstring)"))
        print("  metadata:")
        print("    " + json.dumps(meta, indent=2, sort_keys=True).replace("\n", "\n    "))
        return 0
    if not args.i_understand_this_is_outward_facing:
        raise AixivError(
            "refusing to submit: uploading a manuscript to a third party is outward-facing and "
            "irreversible in practice (CLAUDE.md §3). Re-run with --dry-run to see the exact "
            "payload, or pass --i-understand-this-is-outward-facing once trimcrae has authorised it.")
    body, ctype = _multipart({"metadata": json.dumps(meta)}, {"file": args.pdf})
    out = _request(EP_SUBMIT, data=body, method="POST", headers={
        "Content-Type": ctype, "Authorization": f"Bearer {_token()}"})
    print(json.dumps(out, indent=2))
    return 0


def cmd_review(args):
    """Start an attack review on a submission that ALREADY EXISTS on aiXiv."""
    aixiv_url = args.aixiv_url or f"{BASE.rstrip('/')}/abs/{args.aixiv_id}"
    fields = {
        "aixiv_id": args.aixiv_id,
        "aixiv_url": aixiv_url,
        "version": args.version,
        "doc_type": args.doc_type,
    }
    # ⭐ A SEED IS WHAT MAKES A ROUND RE-RUNNABLE. `paper-hardening` §3 reviews a pinned commit so
    # every finding is falsifiable against one text; an unseeded external reviewer would give a
    # different answer on the same pin and there would be no way to tell drift from disagreement.
    if args.seed is not None:
        fields["seed"] = str(args.seed)
    if args.engine:
        fields["engine"] = args.engine
    if args.lit_search:
        fields["enable_lit_search"] = "true"
    if args.dry_run:
        print(f"DRY RUN — would POST {BASE}{EP_REVIEW}")
        print("  " + json.dumps(fields, indent=2, sort_keys=True).replace("\n", "\n  "))
        print(f"  file: {args.pdf}")
        return 0
    body, ctype = _multipart(fields, {"file": args.pdf})
    out = _request(EP_REVIEW, data=body, method="POST", headers={
        "Content-Type": ctype, "Authorization": f"Bearer {_token()}"})
    print(json.dumps(out, indent=2))
    return 0


def cmd_fetch(args):
    """Pull the reviews for one submission version. Needs no token per the spec."""
    payload = json.dumps({"aixiv_id": args.aixiv_id, "version": args.version}).encode()
    out = _request(EP_GET_REVIEW, data=payload, method="POST",
                   headers={"Content-Type": "application/json"})
    reviews = out.get("review_list") or []
    # ⚠ `Review.review_results` IS TYPED `string` IN THE SPEC, NOT AN OBJECT. Anything richer is a
    # convention of whatever wrote it, so it is stored VERBATIM and parsed only best-effort — a
    # structure we assume and do not check is the "populated field is not a measured one" failure.
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        dest = os.path.join(args.out, f"{args.aixiv_id}-{args.version}-reviews.json")
        with open(dest, "w") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
        print(f"wrote {len(reviews)} review(s) -> {dest}")
    for r in reviews:
        print(f"--- review {r.get('id')} by {r.get('reviewer')} at {r.get('create_time')}")
        print(str(r.get("review_results"))[:4000])
    if not reviews:
        # ⛔ AN EMPTY LIST IS NOT A CLEAN BILL OF HEALTH. It means no review is recorded yet —
        # which is an unanswered question, not a pass (CLAUDE.md §4).
        print("NO REVIEWS RECORDED for this id/version. That is an absent reading, NOT a verdict.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("submit", help="create a submission (outward-facing; gated)")
    s.add_argument("--pdf", required=True)
    s.add_argument("--meta", required=True, help="JSON file of SubmissionCreate metadata")
    s.add_argument("--public", type=int, default=0, choices=(0, 1))
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--i-understand-this-is-outward-facing", action="store_true")
    s.set_defaults(fn=cmd_submit)

    r = sub.add_parser("review", help="start an attack review on an EXISTING aiXiv submission")
    r.add_argument("--aixiv-id", required=True)
    r.add_argument("--version", required=True)
    r.add_argument("--pdf", required=True)
    r.add_argument("--aixiv-url", default=None)
    r.add_argument("--doc_type", "--doc-type", dest="doc_type", default="paper")
    r.add_argument("--engine", default=None)
    r.add_argument("--seed", type=int, default=None)
    r.add_argument("--lit-search", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    r.set_defaults(fn=cmd_review)

    f = sub.add_parser("fetch", help="pull recorded reviews for a submission version")
    f.add_argument("--aixiv-id", required=True)
    f.add_argument("--version", required=True)
    f.add_argument("--out", default=None, help="directory to write the raw JSON into")
    f.set_defaults(fn=cmd_fetch)

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except AixivError as e:
        print(f"aixiv_review: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
