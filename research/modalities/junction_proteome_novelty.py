#!/usr/bin/env python3
"""
Proteome-wide novelty test for the EWSR1::NR4A3 junction peptides.

Question this answers: are the junction-spanning peptides absent from the HUMAN
PROTEOME, or only from the two parent proteins? `fusion_breakpoints.py` filters each
candidate against wild-type EWSR1 and wild-type NR4A3 alone (`emit_junction`'s novelty
filter: `k not in ews_prot and k not in nr4_prot`). That is a two-protein test, and the
neoantigen manuscript and `PUB-NEOANTIGEN` both say so explicitly: "absent from the
normal proteome" has never been a claim this repo could make. This script is the test
that would let it be made — or that would find the counterexamples.

⛔ WHAT A PASS DOES AND DOES NOT LICENCE. A peptide absent from every human protein is
NOT self at the sequence level. It is NOT thereby shown to be presented, immunogenic,
safe, or free of TCR cross-reactivity: a T-cell receptor sees a surface, not a string,
and a peptide differing from a self peptide at a non-contact position can still be
cross-recognised. This is an exact-substring test and nothing more. It removes one
specific, previously-unexcluded failure mode (the peptide is simply a normal human
peptide) and leaves every other one standing.

Source (CI-fetchable, citable, reproducible):
  - UniProtKB human reference proteome UP000005640, reviewed (Swiss-Prot) entries,
    WITH isoform sequences, streamed as FASTA from the UniProt REST API. Isoforms are
    included deliberately: a junction peptide that matches no canonical sequence but
    does match an alternatively-spliced isoform is exactly the counterexample this test
    exists to find, and a canonical-only search would miss it.
  - TrEMBL (unreviewed) is NOT searched. It is predicted-and-unreviewed, so a hit there
    is not evidence that a normal protein carries the peptide; a MISS there is also not
    evidence of absence. Including it would trade a clean statement for a noisy one.
    The scope searched is recorded in the output and must be quoted with the result.

Method:
  - Peptides: every distinct `novel_peptides` entry across the in-frame junctions of
    fusion-breakpoint-neoantigens.json (the transcript-model artifact). Each is flagged
    with whether it is also a predicted binder in that artifact's ranked list, so the
    result can be read for the screen's leads specifically as well as in bulk.
  - Search: exact substring, over the concatenated proteome with a sentinel between
    records so no match can straddle two proteins. A hit records every accession whose
    sequence contains it.
  - The two parent proteins are searched like any other. They should not hit (the input
    is already parent-filtered); if one does, the upstream filter is broken and this
    script says so rather than quietly agreeing.

Output: junction-proteome-novelty.json
"""

import bisect
import datetime
import gzip
import io
import json
import os
import sys
import urllib.request


def _utcnow():
    """⚠ Stamped on every write so a stale artifact is DETECTABLE. Its absence was why a
    three-day-old result read as current across two green runs (2026-08-22)."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
OUT = os.path.join(HERE, "junction-proteome-novelty.json")

PROTEOME_URL = (
    "https://rest.uniprot.org/uniprotkb/stream"
    "?query=%28proteome%3AUP000005640%29+AND+%28reviewed%3Atrue%29"
    "&format=fasta&includeIsoform=true&compressed=true"
)
#: ⭐ THE UNREVIEWED PASS, ADDED 2026-08-22 IN ANSWER TO AN EXTERNAL REVIEW.
#: aiXiv review 1363 (W3) held that "a peptide's absence from reviewed proteins does not establish
#: it as novel". The docstring above already argued the other side — a TrEMBL hit is not evidence a
#: normal protein carries the peptide, and a TrEMBL miss is not evidence of absence — and that
#: argument still stands. What it did NOT justify was declining to LOOK.
#: ⛔ SO THIS RUNS AS A SEPARATE, SEPARATELY-REPORTED PASS AND NEVER MERGES INTO THE HEADLINE
#: COUNT. `n_novel_proteome_wide` stays scoped to reviewed entries, because that is the number the
#: manuscript quotes and its meaning must not change silently. A hit here is a LEAD to be named in
#: the paper, not a withdrawal.
UNREVIEWED_URL = (
    "https://rest.uniprot.org/uniprotkb/stream"
    "?query=%28proteome%3AUP000005640%29+AND+%28reviewed%3Afalse%29"
    "&format=fasta&includeIsoform=true&compressed=true"
)
PARENTS = {"P56945": "EWSR1", "Q92570": "NR4A3"}
SENTINEL = "\x00"


def _fetch_paginated(stream_url, tries=3, page=500):
    """Walk UniProt `/search` pages via the Link rel="next" cursor. Returns the joined FASTA text.

    ⚠ EVERY PAGE MUST ARRIVE. A dropped page would silently shorten the proteome and every peptide
    absent from the missing part would score NOVEL, so a page that will not fetch after `tries`
    attempts raises rather than being skipped.
    """
    url = (stream_url.replace("/uniprotkb/stream", "/uniprotkb/search")
                     .replace("&compressed=true", "") + f"&size={page}")
    parts, seen, n = [], 0, 0
    while url:
        last = None
        for attempt in range(tries):
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "Rare-cancers/junction-novelty"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    body = r.read().decode("utf-8", "replace")
                    link = r.headers.get("Link", "") or ""
                break
            except Exception as e:                                # noqa: BLE001
                last = e
                print(f"    page {n} attempt {attempt + 1} failed: {e}", file=sys.stderr)
        else:
            raise RuntimeError(f"proteome page {n} failed after {tries} attempts: {last}")
        parts.append(body)
        seen += body.count(">")
        n += 1
        nxt = ""
        for piece in link.split(","):
            if 'rel="next"' in piece and "<" in piece:
                nxt = piece.split("<", 1)[1].split(">", 1)[0]
        url = nxt
        if n % 20 == 0:
            print(f"    ...{n} pages, {seen} records", file=sys.stderr)
    print(f"  paginated fetch: {n} pages, {seen} records", file=sys.stderr)
    return "".join(parts)


def fetch_proteome(url=PROTEOME_URL, tries=4):
    """Stream the human proteome FASTA. Returns [(accession, name, seq)].

    ⛔ THE FAILURE THIS HANDLES IS `IncompleteRead`, NOT A TIMEOUT. Measured 2026-08-22, run
    32599692787: `IncompleteRead(8760539 bytes read)` — UniProt's `compressed=true` stream drops the
    connection partway, consistently, at a few megabytes. A plain `r.read()` raises, and every retry
    hits the same wall because the request is identical.
    ⛔ AND A PARTIAL BODY MUST NEVER BE USED. `IncompleteRead` carries `e.partial`, and decoding it
    would yield a proteome missing its tail — every peptide absent from the truncated remainder
    would be scored NOVEL. That is a silently wrong headline number, which is worse than no number,
    so a short read is an error here and never a result.
    """
    # ⛔ `/stream` TRUNCATES AND CANNOT BE MADE TO WORK BY RETRYING. Measured 2026-08-22 across two
    # runs: IncompleteRead at 8,760,539 bytes (compressed) and at 769,298 bytes (uncompressed) — a
    # different offset each time, so it is the server dropping a long-lived connection rather than a
    # deterministic size limit or anything our client controls.
    # ⭐ THE FIX IS TO STOP ASKING FOR ONE LONG RESPONSE. `/search` returns bounded pages and a
    # `Link: <...>; rel="next"` cursor, so no single connection has to survive the whole proteome.
    text = _fetch_paginated(url, tries=tries)

    entries, acc, name, chunks = [], None, None, []
    for line in io.StringIO(text):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if acc:
                entries.append((acc, name, "".join(chunks)))
            parts = line[1:].split("|")
            acc = parts[1] if len(parts) > 2 else line[1:].split()[0]
            name = parts[2].split(" OS=")[0] if len(parts) > 2 else ""
            chunks = []
        elif line:
            chunks.append(line.strip())
    if acc:
        entries.append((acc, name, "".join(chunks)))
    return entries


def load_peptides():
    """Distinct novel junction peptides, each tagged with its junctions and binder status."""
    bp = json.load(open(BREAKPOINTS))
    binders = {b["peptide"]: b for b in bp.get("predicted_binders_ranked", [])}
    peps = {}
    for jn in bp.get("junctions", []):
        label = jn.get("junction_label") or jn.get("label") or jn.get("id") or "?"
        for p in jn.get("novel_peptides", []):
            rec = peps.setdefault(p, {"peptide": p, "junctions": [], "predicted_binder": None})
            if label not in rec["junctions"]:
                rec["junctions"].append(label)
    for p, rec in peps.items():
        b = binders.get(p)
        if b:
            rec["predicted_binder"] = {"allele": b.get("allele"), "class": b.get("class"),
                                       "affinity_nM": b.get("affinity_nM")}
    return bp, sorted(peps.values(), key=lambda r: r["peptide"])


def main():
    if not os.path.exists(BREAKPOINTS):
        print("  fusion-breakpoint-neoantigens.json absent; nothing to test", file=sys.stderr)
        return 1
    bp, peptides = load_peptides()
    print(f"  {len(peptides)} distinct novel junction peptides to test", file=sys.stderr)

    # ⛔⛔ A FAILED FETCH MUST NOT LEAVE A STALE ARTIFACT LOOKING CURRENT. MEASURED 2026-08-22:
    # `junction-proteome-novelty.json` on `modalities-cache` was last written 2026-08-19, yet TWO
    # runs that day reported SUCCESS — the step is `continue-on-error: true`, the UniProt fetch hung
    # (tries=4 x timeout=600 is up to 40 minutes), the script raised before writing anything, and
    # the three-day-old file stayed in place still reading "170 of 174". Nothing anywhere said the
    # number was stale, which is this repository's "reports while measuring nothing" defect exactly.
    # ⚠ SO: fail fast, and write a WITHDRAWAL over the artifact rather than leaving the old one.
    try:
        entries = fetch_proteome(tries=3)
    except Exception as e:  # noqa: BLE001 — the failure text IS the record
        json.dump({
            "⛔_STATUS": "FETCH FAILED — THIS ARTIFACT CARRIES NO RESULT",
            "⚠_do_not_quote": ("The previous contents of this file were REPLACED by this notice so "
                               "a stale count could not be read as a current one. Re-run when "
                               "UniProt is reachable."),
            "error": f"{type(e).__name__}: {e}",
            "url": PROTEOME_URL,
            "generated_utc": _utcnow(),
        }, open(OUT, "w"), indent=2)
        print(f"  PROTEOME FETCH FAILED: {e}", file=sys.stderr)
        return 1
    print(f"  proteome: {len(entries)} reviewed sequences (isoforms included)", file=sys.stderr)
    # Sentinel-joined haystack: no match can straddle a record boundary.
    hay = SENTINEL.join(seq for _, _, seq in entries)
    offsets, pos = [], 0
    for acc, name, seq in entries:
        offsets.append((pos, pos + len(seq), acc, name))
        pos += len(seq) + 1

    starts = [o[0] for o in offsets]

    def locate(idx):
        k = bisect.bisect_right(starts, idx) - 1
        if k < 0:
            return None, None
        start, end, acc, name = offsets[k]
        return (acc, name) if start <= idx < end else (None, None)

    found, absent, parent_hits = [], [], []
    for rec in peptides:
        p = rec["peptide"]
        hits, i = [], hay.find(p)
        while i != -1:
            acc, name = locate(i)
            if acc and not any(h["accession"] == acc for h in hits):
                hits.append({"accession": acc, "protein": name})
                if acc.split("-")[0] in PARENTS:
                    parent_hits.append({"peptide": p, "accession": acc,
                                        "parent": PARENTS[acc.split("-")[0]]})
            i = hay.find(p, i + 1)
        out = dict(rec, proteome_hits=hits, novel_proteome_wide=not hits)
        (absent if not hits else found).append(out)

    binder_hits = [r for r in found if r["predicted_binder"]]
    result = {
        "_note": ("Proteome-wide exact-substring novelty test for the EWSR1::NR4A3 junction "
                  "peptides. Closes the gap that fusion_breakpoints.py filters novelty against "
                  "wild-type EWSR1 and NR4A3 ONLY. An exact-match miss is NOT presentation, NOT "
                  "immunogenicity, NOT safety and NOT absence of TCR cross-reactivity."),
        "⛔_what_this_is_not": ("A peptide absent from every reviewed human protein is not thereby "
                               "a safe or usable target. A TCR reads a peptide-MHC surface, so a "
                               "peptide differing from a self peptide at a non-contact position can "
                               "still be cross-recognised. This test excludes exactly one failure "
                               "mode: that the peptide is simply a normal human peptide."),
        "generated_utc": _utcnow(),
        "_input": {"file": "fusion-breakpoint-neoantigens.json",
                   "artifact_utc": bp.get("_utc"),
                   "coordinate_system": "TRANSCRIPT (the corrected model)",
                   "n_inframe_junctions": bp.get("n_inframe_junctions")},
        "_proteome": {"source": "UniProtKB REST stream", "url": PROTEOME_URL,
                      "proteome_id": "UP000005640", "reviewed_only": True,
                      "isoforms_included": True, "trembl_included": False,
                      "n_sequences": len(entries), "n_residues": sum(len(s) for _, _, s in entries)},
        "_method": ("exact substring search of each peptide against the sentinel-joined proteome; "
                    "every containing accession recorded; no mismatch tolerance"),
        "_cost": "$0 — CI only, one public UniProt fetch, no GPU and no rental.",
        "n_peptides_tested": len(peptides),
        "n_novel_proteome_wide": len(absent),
        "n_found_in_proteome": len(found),
        "n_predicted_binders_found_in_proteome": len(binder_hits),
        "⛔_upstream_filter_check": (
            {"parent_protein_hits": parent_hits,
             "verdict": "BROKEN — a parent-filtered peptide matched a parent protein"}
            if parent_hits else
            {"parent_protein_hits": [], "verdict": "consistent — no parent-filtered peptide hit a parent"}),
        "peptides_found_in_proteome": found,
        "peptides_novel_proteome_wide": absent,
    }

    # ⛔⛔ WRITE THE PRIMARY RESULT BEFORE THE OPTIONAL PASS RUNS. MEASURED 2026-08-22, run
    # 32595857959: the unreviewed pass was placed between `result = {...}` and `json.dump`, it did
    # not complete, and `json.dump` was therefore never reached — so a 32-minute step reported
    # SUCCESS (the workflow step is `continue-on-error: true`) while
    # `junction-proteome-novelty.json` kept its PREVIOUS contents. The headline 170/174 looked
    # intact because it was stale, which is worse than an obviously missing file.
    # ⚠ THE RULE: AN OPTIONAL ENHANCEMENT MUST NEVER BE ABLE TO LOSE THE MANDATORY RESULT. This is
    # the same shape as the diagnostics that raised and killed their own runs (CLAUDE-history §4).
    json.dump(result, open(OUT, "w"), indent=2)

    if "--include-unreviewed" in sys.argv:
        # Only the peptides that SURVIVED the reviewed pass are at stake: a peptide already found
        # in a reviewed protein is settled, and re-reporting it here would double-count it.
        try:
            unrev_entries = fetch_proteome(UNREVIEWED_URL)
        except Exception as e:  # noqa: BLE001 — the failure text IS the record
            result["_unreviewed"] = {
                "⛔_status": "FETCH FAILED — this is an absent reading, not a reading of absence",
                "error": f"{type(e).__name__}: {e}", "url": UNREVIEWED_URL,
            }
            json.dump(result, open(OUT, "w"), indent=2)
            print(f"  unreviewed pass FAILED: {e}", file=sys.stderr)
            return 0
        print(f"  unreviewed: {len(unrev_entries)} sequences", file=sys.stderr)
        uhay = SENTINEL.join(seq for _, _, seq in unrev_entries)
        uoff, upos = [], 0
        for acc, name, seq in unrev_entries:
            uoff.append((upos, upos + len(seq), acc, name))
            upos += len(seq) + 1
        ustarts = [o[0] for o in uoff]

        def ulocate(idx):
            k = bisect.bisect_right(ustarts, idx) - 1
            if k < 0:
                return None, None
            start, end, acc, name = uoff[k]
            return (acc, name) if start <= idx < end else (None, None)

        uhits = []
        for rec in absent:
            p = rec["peptide"]
            hits, i = [], uhay.find(p)
            while i != -1:
                acc, name = ulocate(i)
                if acc and not any(h["accession"] == acc for h in hits):
                    hits.append({"accession": acc, "protein": name})
                i = uhay.find(p, i + 1)
            if hits:
                uhits.append({"peptide": p, "predicted_binder": rec.get("predicted_binder"),
                              "unreviewed_hits": hits})
        result["_unreviewed"] = {
            "⚠_scope": ("Searched SEPARATELY and reported separately. A hit among "
                        "predicted-and-unreviewed entries is NOT evidence that a normal protein "
                        "carries the peptide, and a miss is NOT evidence of absence. This does not "
                        "change n_novel_proteome_wide, which remains scoped to reviewed entries."),
            "url": UNREVIEWED_URL,
            "n_sequences": len(unrev_entries),
            "n_residues": sum(len(s) for _, _, s in unrev_entries),
            "n_reviewed_novel_peptides_searched": len(absent),
            "n_with_an_unreviewed_hit": len(uhits),
            "n_predicted_binders_with_an_unreviewed_hit": sum(
                1 for h in uhits if h.get("predicted_binder")),
            "hits": uhits,
        }
        print(f"  unreviewed pass: {len(uhits)}/{len(absent)} reviewed-novel peptides also occur "
              f"in an unreviewed entry", file=sys.stderr)
        # Re-write with the extra block. The primary result is already on disk above, so this
        # rewrite can only ADD; it can no longer be the reason the file is missing or stale.
        json.dump(result, open(OUT, "w"), indent=2)
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"  {len(absent)}/{len(peptides)} novel proteome-wide; "
          f"{len(found)} found in a human protein ({len(binder_hits)} of them predicted binders)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
