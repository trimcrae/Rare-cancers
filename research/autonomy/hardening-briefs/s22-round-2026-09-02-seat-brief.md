---
id: DOC-S22-ROUND-2026-09-02-SEAT-BRIEF
title: "Blind adversarial seat brief - the 2026-09-02 hardening round over three papers"
level: L3
kind: memo
status: live
canonical_for: ["the instructions the 2026-09-02 blind seats were dispatched against"]
purpose: >
  The single brief every blind seat of this round read before it opened the paper. Committed rather
  than passed inline so each seat's prompt stays short and so the round's instructions are auditable
  beside the seat records they produced.
scope: >
  L3. One hardening round, pin f78666ce3715775c81c0b0b824a1f5bf3abb200c, three publication
  endpoints. It states what a seat may read, how it must grade, and the standard of evidence; it
  reports no result of its own.
audience: [maintainers, autonomous research agents]
date: 2026-09-02
last_verified: 2026-09-02
---

# Blind adversarial seat brief — hardening round, three papers, one pin

You are ONE blind adversarial review seat. You have one lens. You do not know what any other seat is
doing and you must not go looking; there is no expectation of what you will find.

## The pin — this is the subject of your review

    PIN = f78666ce3715775c81c0b0b824a1f5bf3abb200c

⛔ REVIEW THE PIN, NEVER THE WORKING TREE. Read every file as:

    git show f78666ce3715775c81c0b0b824a1f5bf3abb200c:<path>

run from the root of the repository checkout you were given.

The working tree may drift under you while you read. If the live file and the pinned file disagree,
the PINNED file is the one you are reviewing. Do not reconcile against the live file.

⛔ YOU ARE READ-ONLY IN THE MANUSCRIPTS. Do not edit, stage or commit any manuscript, SI, table or
figure. The ONLY tracked file you may write is your own seat record, and only via the instrument
named in your dispatch message.

## What is in scope — the OUTGOING ARTIFACT SET

Your blockers must be about the paper a reader receives. For your paper that is:

* PUB-FUSION-OUTPUT — `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`
  and its SI `...-SI.md`, its tables and figures, its reference list, and the built PDFs
  `...-manuscript.pdf` / `...pdf`.
* PUB-STRATEGY-ARCH — `research/manuscripts/care-delivery/emc-trial-reachability.md`. That is the
  whole deliverable set; it ships alone.
* PUB-NEOANTIGEN — `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md`. That is
  the whole deliverable set; it ships alone.

⛔ NOT IN SCOPE, and a defect there is real but is NOT a blocker on a paper: this repository's own
tooling, tests, ledgers, receipts, state files and skills. Grade such a thing P2 and say where it
lives.

⛔ YOU MAY NOT READ, AND MUST NOT GRADE:
  * any `*-cover-letter.md` — it is out of the outgoing set by decision, and out of reach
  * anything under `research/autonomy/` — that is the loop's own bookkeeping, not the paper. THE ONE
    EXCEPTION IS THIS BRIEF ITSELF and the `seat_scratch.py` command your dispatch names; read
    neither of them for findings.
  * anything under `.claude/skills/`

You MAY and SHOULD read any committed artifact the paper's numbers come from — JSON, CSV, scripts
under `research/`, `systems/graph/*.json` — to check whether the paper states what they contain.

## Grading — and the grade is the thing under review, not evidence

| grade | the test |
|---|---|
| BLOCKER | the outgoing text AS IT STANDS AT THE PIN is wrong, misleading or unsafe. A reader acting on it would be misled. Quote the wrong text and the record that contradicts it, and NAME the outgoing artifact it is in. A blocker that cannot name one is, by that fact, not a blocker. |
| P1 | the text is CORRECT now, but an ordinary future edit would silently falsify it and nothing would catch that. Every guard-coverage gap belongs here, however central the claim. |
| P2 | anything else worth fixing — a defect in tooling, a stylistic wish, a completeness suggestion. |

★ THE TEST PER FINDING, BEFORE YOU GRADE IT: would a reviewer STOP this paper for it, or SUGGEST it?
A wrong fact, a claim the paper's own text contradicts, and an internal contradiction stop a paper.
A completeness wish, a "you should also measure X", and a caveat the body already carries elsewhere
are suggestions. Grade the second kind P2.

## The standard of evidence

⛔ REFUTE BY DEFAULT. Every finding names the artifact PATH and the FIELD or LINE that confirms it.
Anything you cannot reproduce is dropped, or kept as PLAUSIBLE with the one observation that would
settle it. Re-derive every number you challenge from the file that produces it — do not compare it
to your own recollection.

⛔ NEVER ASSERT A MEDICAL FACT, PMID, NCT ID, HLA ALLELE, GENE SYMBOL OR STATISTIC FROM MEMORY.
If you think an identifier is wrong, the finding is "this identifier appears in no committed
artifact" (which you can check) — not "this identifier is wrong" (which you cannot).

## Language discipline these papers are held to

R1-R5: the paper must never imply proteome-wide selectivity, efficacy, safety, a therapeutic window,
or clinical readiness. A NEGATIVE keeps exactly the weight its evidence supports and no more; a
prediction is a prediction, not a measurement; a trial being REACHABLE is not a trial being
APPROPRIATE. A sentence that quietly upgrades any of those is a BLOCKER.

## Returning no findings

Returning **no findings** is a complete and expected answer. Do not lower your bar to produce one.
If your lens turns up nothing on this commit, say so plainly and stop — that is the round's most
valuable result, not its least.

## What to write

Write ONE JSON object to the findings path in your dispatch message, exactly this shape:

```json
{
  "verdict": "supported" | "supported_with_reservations" | "not_supported",
  "central_claim": "<the paper's central claim in your own words, >=40 chars, as YOU tested it>",
  "what_i_read": ["<path>", "..."],
  "blockers": [{"id":"B1","where":"<outgoing artifact path>","quote":"<the wrong text>",
                "why":"<what contradicts it, with artifact path and field>",
                "fix":"<a REPLACEMENT sentence, not an appended qualifier>"}],
  "p1s": [{"id":"P1-a","where":"...","what":"...","why_not_a_blocker":"..."}],
  "p2s": [{"id":"P2-a","where":"...","what":"..."}]
}
```

`verdict` is about the paper's CENTRAL claim only: is it supported by the committed artifacts?
A paper can carry a blocker and still have a supported central claim; say so if that is what you find.

Then reply with a SHORT summary: verdict, counts by grade, and one line per blocker.
