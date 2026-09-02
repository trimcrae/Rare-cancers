# Round 33 seat records, held outside `review-seats/` on purpose

⛔⛔ **THESE ARE NOT YET CLAUSE-1 EVIDENCE, AND FILING THEM AS SUCH WOULD BE A FALSE RECORD.**
`publish_bar.clause_1_hardening_converged` counts blind seats that reviewed **the commit being
posted**, and a round must field at least as many as the widest earlier round on record — six, from
`_look_history('PUB-ASO')`. This directory holds the seats completed so far, at the pin each names
in its own `reviewed_commit`. They live here rather than in `research/autonomy/review-seats/`
because that directory is what the bar globs, and a partial round sitting in it would be counted.

★ **WHY THEY ARE COMMITTED AT ALL:** a seat record written only to a session scratchpad dies with
the container. CLAUDE.md §7 calls work that exists only in `/tmp` a data-loss bug, and this session
has already lost one background job to a restart.

⚠ **AND THE PAPER HAS NOT MOVED THROUGHOUT.** The journal article's sha256 is
`afd60b9ef7f3c1eead4927b8f812136ba4c9db8601df0898d4d94dabd3117377` and the deliverable digest is
`a6f7158552096aea` at round 32's pin and at every commit since; the intervening commits are
tooling. So a seat's findings are about the same text regardless of which sha it names — which is
exactly the observation `AUT-PD-205-d7df5340` is filed on, and exactly what the bar cannot currently
see.

★ **WHAT A SUCCESSOR SHOULD DO WITH THEM.** Do not move them into `review-seats/` and do not
re-point their `reviewed_commit` by hand — a seat record is a claim about what a reviewer read, and
editing the sha to fit a bar is falsifying it. Freeze the tree at one commit, run the round's seats
against **that** pin, and file the round there. These records are useful as evidence that the round
was under way and as a list of what has already been examined; they are not a substitute for seats
at the posted commit.
