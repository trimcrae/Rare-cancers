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

⛔⛔ `is_public: 0` DOES NOT MAKE A SUBMISSION PRIVATE. MEASURED 2026-08-22, AND IT IS NOT A GUESS.
`aixiv.260822.000005` was submitted with `--public 0`; the stored record reads `is_public: 0`, and
**the paper is world-readable anyway** — `/abs/aixiv.260822.000005` returns 200 and renders the full
title, author name, correspondence e-mail and abstract, and `/api/pdf/aixiv.260822.000005` returns
200 and serves the file. Verified from a runner with no credentials at all.
⚠ *Superseded, retained — this docstring previously offered a "PRIVATE-FIRST" shape: "a submission
can in principle be created non-public, reviewed, and made public later … Treat `--public 0` as an
untested claim about aiXiv's behaviour, not a guarantee of privacy."* It was tested. It is false.
**THERE IS NO REHEARSAL MODE. Every `submit` is a publication**, so treat the flag as metadata about
intent and never as access control, and never tell anyone a paper posted this way is unpublished.

⭐ AND THE REVIEW ARRIVES WITHOUT ASKING. A new submission lands at `status: "Under Review"`, which is
exactly what `GET /api/get_pending-review-submissions` describes itself as serving to aiXiv's own
review scheduler. Measured on the same paper: `POST /api/start_attack_review` answered **HTTP 500**,
while a review by "Official Agent" appeared on its own and came back from `POST /api/get-review`
about three minutes after submission. **So `fetch` is the normal path and `review` is the manual
override**; a 500 from the override does not mean no review is coming.

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

#: Same string `lit_fetch_urls.py` uses, and for the same reason — see the note in `_request`.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

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
    # ⛔ DO NOT REMOVE THE USER-AGENT. aixiv.science sits behind Cloudflare, which refuses
    # urllib's default `Python-urllib/3.x` signature with **HTTP 403, "error code: 1010"** — an
    # EDGE verdict on the client's browser signature, not an API verdict on the token. Measured
    # 2026-08-22 in run 32579611578: /api/profile/me/status AND /api/agents both returned 1010
    # with a valid token, while `lit_fetch_urls.py` — same runner infrastructure, same host, same
    # morning — got 200 from /api/archive-stats because it sends a browser UA.
    # ⚠ THE FAILURE MODE THIS GUARDS IS A MISDIAGNOSIS, NOT AN OUTAGE: a 403 on an authenticated
    # endpoint reads as "the token is wrong", and the next hour goes into re-minting a credential
    # that was fine.
    for k, v in {"User-Agent": UA, "Accept": "application/json"}.items():
        req.add_header(k, v)
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


def cmd_verify(args):
    """Read-only proof that the token works, and a report of what it can actually do.

    ⛔ THIS REPOSITORY'S ACTIONS LOGS ARE WORLD-READABLE, AND `/api/profile/me` RETURNS THE
    ACCOUNT'S OWN DETAILS — including the corresponding e-mail. So this prints an explicit
    ALLOWLIST of fields and never the response body. A `json.dumps(profile)` here would publish
    trimcrae's address to a public log, which no later commit can retract.

    ⭐ IT CHECKS THE SCOPE, NOT JUST THE 200. `start_attack_review` is documented as requiring the
    'review' scope, so a token that authenticates perfectly and lacks it will fail at exactly the
    step this integration exists for — and it will fail LATER, on a real paper, rather than here.
    """
    tok = _token()
    hdr = {"Authorization": f"Bearer {tok}"}
    ok = True

    # ⚠ INFORMATIONAL ONLY, AND ITS FAILURE IS THE EXPECTED CASE. `/api/profile/me/*` authenticates
    # a USER session (a Clerk JWT); an agent token is an opaque bearer, so it answers
    # 401 "Malformed JWT: cannot parse header - Not enough segments" — measured 2026-08-22, run
    # 32579709445. That is the API telling us the two credentials are different, which is correct
    # and says nothing about the agent token.
    # ⛔ SO IT MUST NOT SET `ok`. A verify that fails on a check which CANNOT pass trains the reader
    # to ignore its verdict, which costs the verdict exactly when it matters.
    try:
        _request("/api/profile/me/status", method="GET", headers=hdr)
        print("profile/me/status: reachable (this token also carries a user session)")
    except AixivError as e:
        print(f"profile/me/status: not a user session — expected for an agent token ({e})")

    try:
        agents = _request("/api/agents", method="GET", headers=hdr)
        rows = agents if isinstance(agents, list) else agents.get("agents", [])
        print(f"agents: {len(rows)} registered")
        review_capable = 0
        for a in rows:
            scopes = a.get("scopes") or []
            if "review" in scopes:
                review_capable += 1
            # name + scopes only. No ids, no tokens, no owner fields.
            print(f"  - {a.get('name')!r} scopes={sorted(scopes)}")
        if not rows:
            print("  ⚠ NO AGENTS REGISTERED. Create one with POST /api/agents before submitting; "
                  "the agent lane needs an agent identity, not just a signed-in user.")
        elif not review_capable:
            ok = False
            print("  ⛔ NO AGENT CARRIES THE 'review' SCOPE. Submission would work and "
                  "start_attack_review would NOT — which is the whole point of this integration.")
    except AixivError as e:
        ok = False
        print(f"agents: FAILED — {e}")

    print("VERIFY OK" if ok else "VERIFY INCOMPLETE — see the lines above")
    return 0 if ok else 1


def cmd_submit(args):
    meta = load_meta(args.meta, args.public)
    if args.dry_run:
        print(f"DRY RUN — would POST {BASE}{EP_SUBMIT}")
        print(f"  file:     {args.pdf} ({os.path.getsize(args.pdf)} bytes)")
        # ⛔ BOTH VALUES ARE A PUBLICATION. Measured 2026-08-22: is_public=0 still served the paper
        # at /abs/ and /api/pdf/ to an unauthenticated reader. Saying "non-public" here would be
        # the single most misleading line this tool could print.
        print(f"  is_public: {meta['is_public']}  (EITHER VALUE IS A PUBLICATION — "
              "is_public=0 does NOT restrict access; see the module docstring)")
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


def cmd_calibrate(args):
    """What does a Rating of N actually mean here? Measure it against the public corpus.

    ⛔ WHY THIS IS NOT OPTIONAL. `review_results.Rating` arrives as a bare integer with **no scale,
    no minimum and no maximum anywhere in the payload or the OpenAPI schema**. "Rating 6" was
    reported up the chain three times in one session as though it carried meaning; it does not,
    until the distribution it sits in is known. A goal phrased as "a good rating" is unmeasurable
    until this runs.

    ⚠ AND THE TWO OTHER CANDIDATE SIGNALS WERE BOTH CHECKED AND BOTH FAILED (2026-08-22):
      * `status` is "official review completed" for **100 of 100** public submissions, so it
        separates nothing.
      * `doi` is populated on only 4 of 100 — and every one of those four is the record's own
        `aixiv_id` with no `10.xxxx/` registrant prefix, so it is not a registered DOI and not
        evidence of acceptance. Crossref returns 0 results for aiXiv as a container title.
    So the rating is the only graded signal, which is exactly why it must be calibrated rather than
    quoted.
    """
    subs = _request("/api/submissions/public", method="GET",
                    headers={"Accept": "application/json"})
    if isinstance(subs, dict):
        subs = subs.get("submissions") or subs.get("data") or []
    papers = [s for s in subs if s.get("doc_type") == args.doc_type][:args.limit]
    print(f"calibrating against {len(papers)} public {args.doc_type}(s)")

    ratings = []
    keys_seen = set()
    for s in papers:
        aid, ver = s.get("aixiv_id"), str(s.get("version") or "1.0")
        try:
            out = _request(EP_GET_REVIEW,
                           data=json.dumps({"aixiv_id": aid, "version": ver}).encode(),
                           method="POST", headers={"Content-Type": "application/json"})
        except AixivError as e:
            print(f"  {aid} v{ver}: unreadable ({e})")
            continue
        for r in (out.get("review_list") or []):
            try:
                rr = json.loads(r["review_results"])
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
            keys_seen.update(rr.keys())
            v = rr.get("Rating")
            if isinstance(v, (int, float)):
                ratings.append((float(v), aid, ver, s.get("title", "")[:70],
                                str(rr.get("Summary", ""))[:400]))

    if not ratings:
        # ⛔ An empty sample is an unanswered question, not a verdict about our own rating.
        print("NO RATINGS READ. This is an absent reading, NOT evidence that 6 is good or bad.")
        return 1

    # ⭐ IS THERE ANY QUALITATIVE LABEL AT ALL? A percentile over a corpus of unknown quality
    # persuades nobody, so print the UNION of every field the reviews carry. A decision,
    # recommendation, meta-review or accept/reject verdict would show up here if one existed.
    print("\nreview_results fields present anywhere in the corpus:")
    for k in sorted(keys_seen):
        print(f"  - {k}")
    decisionish = sorted(k for k in keys_seen
                         if any(w in k.lower() for w in
                                ("decis", "recommend", "accept", "reject", "verdict", "meta",
                                 "confidence", "vote")))
    print("  -> decision-like fields:", decisionish or "NONE — no accept/reject verdict is emitted")

    vals = sorted(v for v, _, _, _, _ in ratings)
    n = len(vals)
    mean = sum(vals) / n
    median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
    print(f"\nn={n}  min={vals[0]:g}  max={vals[-1]:g}  mean={mean:.2f}  median={median:g}")
    hist = {}
    for v in vals:
        hist[v] = hist.get(v, 0) + 1
    for v in sorted(hist):
        print(f"  {v:5g} | {'#' * hist[v]} ({hist[v]})")
    if args.mine is not None:
        below = sum(1 for v in vals if v < args.mine)
        equal = sum(1 for v in vals if v == args.mine)
        pct = 100.0 * (below + 0.5 * equal) / n
        print(f"\nours = {args.mine:g} -> percentile {pct:.0f} of this corpus "
              f"({below} below, {equal} equal, {n - below - equal} above)")
        print("⚠ Observed range only. The scale's true maximum is still UNKNOWN — a corpus that "
              "never scores above its own max cannot reveal one.")

    # ⛔ A PERCENTILE IS ONLY AS GOOD AS THE CORPUS IT RANKS AGAINST. If the bottom of this
    # distribution is slop, standing above it means nothing — so print the actual titles and
    # verdict text at both ends and let a human judge the corpus rather than take the rank.
    ranked = sorted(ratings, key=lambda t: t[0])
    print("\n=== LOWEST RATED (is the floor slop?) ===")
    for v, aid, ver, title, summary in ranked[:3]:
        print(f"[{v:g}] {aid} — {title}\n      {summary[:260]}\n")
    print("=== HIGHEST RATED (what does a 7-8 look like?) ===")
    for v, aid, ver, title, summary in ranked[-3:]:
        print(f"[{v:g}] {aid} — {title}\n      {summary[:260]}\n")
    return 0


def cmd_new_version(args):
    """Post a revised version of a paper already on aiXiv.

    ⛔ THIS IS A PUBLICATION TOO, and it carries the same acknowledgement gate as `submit`. A new
    version does not replace the old one — aiXiv keeps both (`/list` shows v1.0 and v1.1 rows for
    the same id) — so nothing here retracts what the previous version said.
    """
    meta = load_meta(args.meta, args.public)
    path = f"{EP_SUBMIT}/{args.aixiv_id}/versions"
    if args.dry_run:
        print(f"DRY RUN — would POST {BASE}{path}")
        print(f"  file: {args.pdf} ({os.path.getsize(args.pdf)} bytes)")
        print(f"  is_public: {meta['is_public']}  (EITHER VALUE IS A PUBLICATION)")
        print("  metadata:")
        print("    " + json.dumps(meta, indent=2, sort_keys=True).replace("\n", "\n    "))
        return 0
    if not args.i_understand_this_is_outward_facing:
        raise AixivError(
            "refusing to post a new version: this publishes revised text to a third party and the "
            "previous version is not withdrawn by it. Re-run with --dry-run, or pass "
            "--i-understand-this-is-outward-facing once trimcrae has authorised it.")
    body, ctype = _multipart({"metadata": json.dumps(meta)}, {"file": args.pdf})
    out = _request(path, data=body, method="POST", headers={
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

    v = sub.add_parser("verify", help="read-only: does the token work, and does it carry 'review'?")
    v.set_defaults(fn=cmd_verify)

    s = sub.add_parser("submit", help="create a submission (outward-facing; gated)")
    s.add_argument("--pdf", required=True)
    s.add_argument("--meta", required=True, help="JSON file of SubmissionCreate metadata")
    s.add_argument("--public", type=int, default=0, choices=(0, 1))
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--i-understand-this-is-outward-facing", action="store_true")
    s.set_defaults(fn=cmd_submit)

    c = sub.add_parser("calibrate", help="what a Rating means, measured against the public corpus")
    c.add_argument("--limit", type=int, default=40)
    c.add_argument("--doc-type", dest="doc_type", default="paper")
    c.add_argument("--mine", type=float, default=None, help="our rating, to place as a percentile")
    c.set_defaults(fn=cmd_calibrate)

    nv = sub.add_parser("new-version", help="post a revised version of an existing paper (gated)")
    nv.add_argument("--aixiv-id", required=True)
    nv.add_argument("--pdf", required=True)
    nv.add_argument("--meta", required=True)
    nv.add_argument("--public", type=int, default=0, choices=(0, 1))
    nv.add_argument("--dry-run", action="store_true")
    nv.add_argument("--i-understand-this-is-outward-facing", action="store_true")
    nv.set_defaults(fn=cmd_new_version)

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
