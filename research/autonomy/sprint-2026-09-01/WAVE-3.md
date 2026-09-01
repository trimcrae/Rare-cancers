# Wave 3 — dispatched 2026-09-02 ~00:15Z (8:15 PM ET)

Seven seats. **Six of the seven exist because of something a wave-1 or wave-2 seat found, not
because of a ledger row** — which is the honest measure of whether the first two waves were worth
running. The ledger had 155 queued rows and none of them named any of this.

## The three that are evidence-integrity work, and they outrank everything else here

| seat | what a seat found | why it is urgent |
|---|---|---|
| **S18-FALSE-ABSENCES** | Two committed artifacts record medical **absences that are false against their own source corpora**, proven by a single blob SHA: the same PMC file sits at two paths, and it contains verbatim the sentences that `"result": "ZERO records."` and `carbon_ion.found_in_this_histology: false` deny. Both values are hard-coded literals in their generators; no gate reads the corpus; a guard now locks the wrong answer in. | CLAUDE.md §7's golden rule is never to fabricate a medical fact. **A recorded absence that is false is the same defect with the opposite sign** — a confident claim about the literature that the literature contradicts. And §4 already names the error: *an absent reading is not a reading of absence.* Two route grades quote these. |
| **S19-TRABECTEDIN** | `routes.json` carries figures the cited registry **withdrew on 2026-08-07** (n=5 where the registry says 2; a median PFS that was withdrawn because it belongs to the mixed arm and lands on an MCS patient), reprinted in a generated view. And `emc-treatment-roadmap.md:213` — a **submission-targeted** manuscript — asserts a "reported EMC responder" **with no identifier**, which that file's own reference list already flags as open. | S16 named the mechanism exactly: *"this is what `lint_claims` cannot catch: the sentence is perfectly hedged; the denominator is wrong."* A third axis beyond strength and provenance — a correctly-hedged sentence resting on a number its own source retracted, in the one kind of document that reaches an outside reader. |
| **S20-VACCINE-RECONCILE** | Two live documents give **opposite answers** to which peptide configuration deletes the repertoire. And S13 measured that §B3's near-self null **turns entirely on position 1**: counting P1, 6 of 11 binders acquire an anchor-only near-self neighbour, all six against an isoform of the acceptor gene. | S13 flagged rather than adjudicated it, correctly — it is an immunological call and neither file was its path. Until it is resolved, **nothing from the new artifact may go into a paper.** The seat is explicitly forbidden from resolving it by weakening both statements until they agree. |

## The rest

| seat | one line |
|---|---|
| **S21-UNSCORED** | `health.py`: **68 of 194 open rows carry no score**, so no cycle can be offered them and no handoff lists them — invisible, not deprioritised, for 88 hours. ⭐ The census is the deliverable: *what has the queue been blind to?* Scores are the follow-on, and a number invented to fill a column is worse than an honest absence. |
| **S22-PROSE-A** | PUB-VACCINE-PATH (18 over-ceiling, longest 108 w) and PUB-FUSION-OUTPUT (15). ⛔ Fenced off from §B3's null, which S20 is adjudicating. |
| **S23-PROSE-B** | PUB-METHODS, PUB-CLOSED-ROUTES, PUB-MODALITY-CENSUS, PUB-HLA-COVERAGE — small counts, and told to expect that two are already clear. ⚠ Two are **negative-result papers**, the most dangerous to shorten: an honest limit of an experiment becomes a claim about the world in one careless join. |
| **S24-CALIBRATION** | S13: the acceptance-threshold calibration is *"the cheapest step that can still close the route"* and needs MHCflurry, which this sandbox lacks. ⛔ *"It needs the driver to dispatch"* is precisely the sentence `ci-escape-hatches` exists to delete — the seat routes it to Actions itself. |

## One instruction every prose seat carries, and why it is repeated verbatim

A hedge quietly dropped to shorten a sentence is the only way these seats can do real damage, and no
guard in the repository can see it: `lint_claims` reads claim STRENGTH, and an inverted claim is
still a grammatical, hedged-looking sentence of the same length. CLAUDE.md §6 records the 13
inverted claims that reached `origin/main` exactly this way. So each seat's deliverable is **a table
of every sentence changed, original beside replacement** — the driver audits the meaning rather than
trusting it.
