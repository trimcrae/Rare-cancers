# PR1 scratch: deliberately NOT retained in the repository

PR1 built its repair in a write-isolated sandbox at `/tmp/claude-0/pr1-lane/sandbox/`, which is a
**symlink farm** — 114 symlinks pointing into the live tree, alongside 258 real files — so that no
execution path could write into the repository.

The parent's first attempt copied that sandbox in here verbatim. `research/autonomy/push_guard.py`
(AUT-PD-144) refused the push, correctly: the copy dereferenced into files that do not parse as the
JSON their names claim, and the guard's own message is the right reading — loop state only a machine
reads, where a half-applied tree is invisible until something crashes on it. The copy was removed
rather than forced through.

**What is retained here instead**, and it is the whole of the meaningful evidence:

| file | what it is |
|---|---|
| `BEFORE-endpoint_regime_map.py` | the producer as committed before the repair |
| `AFTER-endpoint_regime_map.py` | the producer as committed after it |
| `producer.diff` | the three-hunk unified diff between them |
| `ORIGINAL-CHILD-TRANSCRIPT-ae8e3b030e7297293.jsonl` | PR1's full transcript, carrying every command it ran, its outputs and its exit codes verbatim |

The artifact's own before/after is recoverable from Git history at the landing commit. The sandbox
itself was a build directory, not evidence: everything it demonstrated is in the transcript and the
diff. Nothing was recreated to write this note, and the original `/tmp/claude-0/pr1-lane/` is
untouched.
