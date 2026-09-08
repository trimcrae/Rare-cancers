# AB1 final edit — already applied, evidence retained here

The coordinator's one-line edit was **applied and pushed before this evidence was written**, in commit
`035e9f69` ("Apply N2 and CR1 fixes; take the ATR abstract to 243 words"), which is an ancestor of
`ebd06673`. The local intake note reporting it absent from `ebd06673` is mistaken; the check is:

```
git show ebd06673:research/manuscripts/dependency/emc-atr-collaborator-package.md \
  | grep -c "establishes measured anchors at 0.000 and 1.000"     ->  1
grep -c "never in between" research/manuscripts/dependency/emc-atr-collaborator-package.md  ->  0
```

Nothing was re-applied. This directory only retains the evidence the coordinator asked for.

| file | what it is |
|---|---|
| `BEFORE-abstract-245w.txt` | the abstract as it stood at `035e9f69^`, extracted by the counter's own regex |
| `AFTER-abstract-243w.txt` | the abstract as committed, same extraction |
| `final-edit.diff` | unified diff of the two: one sentence replaced, the paragraph rewrapped |
| `COUNTER-AFTER-FINAL-EDIT.txt` | the declared counter's output on the live manuscript |

The replacement is exactly as authorised. "Recruitment was measured only at 0.000 and 1.000, never in
between." became "That report establishes measured anchors at 0.000 and 1.000." No other abstract
wording changed; the rest of the diff is line rewrapping at the file's 100-column convention.

The counter was **imported and `measure()` called directly**, not run as a script, because
`submission_metrics.py` does not implement `--help` and executing it rewrites
`submission-metrics.json`. It reports **243** words. AB1's own 245-word originals are retained
unchanged in the parent directory: `AFTER-abstract.txt`, `abstract.diff`, `COUNTER-INVOCATION.txt`,
`NOTES.md` and the two counter wrappers. The derived row in `submission-metrics.json` was updated in
the same commit and records `abstract_words: 243`, `0 limit(s) exceeded`.

No new worker, no science, no source, no figure, no broad gate replay.
