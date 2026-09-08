# COLLECTION AB1 — ATR collaborator package, shortened abstract

Collected 2026-09-08 by the campaign parent. Applied to
`research/manuscripts/dependency/emc-atr-collaborator-package.md` under ordinary
manuscript-advancement scope, per the coordinator's correction that shortening this abstract is an
authoring task and not an authorization gate.

## Execution, from the original transcript

`AB1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a29679a2457255f71.jsonl`, copied and
`cmp`-verified identical, sha256
`89f11aae6cd42d4b118b0e17fb99cbf60b29e13a74cb068412f206cbb5534d6e`.

| observed | value |
|---|---|
| model, every entry | `claude-opus-5` (53 of 53) |
| tool_use / tool_result | 30 / 30, fully paired |
| span | 2026-09-08T12:43:06.762Z to 12:49:50.814Z |

AB1's report states 19 tool calls; the transcript records **30**. The observed count governs.

AB1's own scratch lane is retained verbatim: `BEFORE-abstract.txt`, `AFTER-abstract.txt`,
`abstract.diff`, `COUNTER-INVOCATION.txt`, `NOTES.md`, `START-STATE.txt`, `END-STATE.txt` and the two
counter wrappers `cand-before.md` / `cand-after.md`.

## Parent's independent verification, before applying

| check | result |
|---|---|
| AB1's `BEFORE-abstract.txt` is the live abstract | Diffed against a fresh extraction from the manuscript. Identical except a trailing blank line and the `---` rule that follows the section, which the counter blanks. Faithful. |
| the declared counter, called directly | `sm.measure()` on the live manuscript returned **341**; on AB1's candidate wrapper, **245**. The parent imported `submission_metrics` and called `measure()` rather than running the script, exactly as AB1 did. |
| the five required preservations | each located in the applied text and checked against the manuscript body: recruitment measured only at 0.000 and 1.000; the EWSR1::ATF1 span named as reported breakpoints with the measured construct's breakpoint unstated; the evaluated grid named as 50 aa upwards in 10-aa steps with no TCF12 prefix reaching the lowest FET value on that grid; the no-experiment and single-annotation-source limitations; the computed contributions. |
| every quantity already in the manuscript at the same value | 177 nt, 59 residues, 8 of 30, 0 of 30, 0.000, 0.267, 1.000, exons 12/7/13 and TAF15 exon 6 — all present unchanged in sections 3.1 to 3.5 and Table 3. Nothing new was introduced. |

AB1 read `submission_metrics.py` in source, established that `measure()` and `prepare()` only read,
that the module's sole write is inside `main()` under a `__main__` guard, and imported rather than
executed it. That is the correct handling of a script whose `--help` is not inert, and the parent
repeated it.

## Applied

The abstract body was replaced in place and rewrapped to the file's 100-column convention. Nothing
else in the manuscript changed; the diff is `manuscript-abstract-swap.diff`.

**Measured after, by the declared counter run as a script once:** abstract **245 w**, main 6,202 w,
1 figure, 5 tables, 6 display items, 10 references — `within believed limits`, and
`submission-metrics.json` now records `0 limit(s) exceeded`. The **BLOCKER recorded earlier is
closed** on its corrected reopening condition: a faithful abstract at or under 250 words, measured by
the actual declared counter.

`lint_style` 0 ERROR on the manuscript, `lint_claims` 0 ERROR with the one pre-existing author-block
WARN, `lint_consistency` 0 ERROR across 29 files.

## Carried forward, honestly

The 250-word limit is `VENUES["GCC-Research-Article"]["limits"]["abstract_words"]` in
`submission_metrics.py`, whose provenance field records it as search-derived because Wiley's guideline
page serves a bot challenge. It is **not publisher-verified**, and 245 is a count under this counter's
tokenisation rules, which a journal's own counter may not share. Neither fact was discovered here and
neither is repaired here.

Three sentences were cut whose content survives elsewhere in the paper: the per-junction pairing
(Table 1), the internal 177-nt accounting (section 3.3 and Figure 1C), and the per-series frequency
attribution (Table 1, which governs). The tag and laser-stripe geometry moved to section 5's
quotation. The axis-position fact was made explicit rather than implicit — the 341-word version stated
the intermediate-position gap only by omission.

Integration is not publication acceptance. The coordinator assesses the wording.
