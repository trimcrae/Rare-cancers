#!/bin/bash
# ⛔⛔ "KEEP EVERYTHING SYNCED TO `main`" WAS A PROSE RULE MEASURED BY NOTHING, AND IT FAILED THE
# WAY EVERY PROSE RULE IN THIS REPOSITORY HAS FAILED.
#
# trimcrae, 2026-08-29: "Makes me think we've once again fallen victim to the issue where rules that
# only exist in prose don't get consistently enforced. Is there an elegant way to make sure sessions
# always get merged to main as a default?"
#
# ★ MEASURED THAT DAY, AND IT IS NOT ONE SESSION'S SLIP. `git for-each-ref` over `origin` found
# TWENTY-PLUS branches carrying unmerged commits, most last touched a month earlier. The session that
# prompted this had eight commits and had never merged once while `main` moved 53 ahead — and the
# cost was not hypothetical: another cycle diagnosed and fixed THE SAME BUG on the trunk within the
# same hour, neither able to see the other, each finding something the other missed.
#
# ⛔⛔ AND THE PROXIMATE CAUSE WAS A MISREADING THIS HOOK EXISTS TO MAKE IMPOSSIBLE. The session
# carried an instruction to develop on a named feature branch and to "NEVER push to a different
# branch without explicit permission", and read that as gating the merge to `main`. IT DOES NOT.
# CLAUDE.md §6: "A MERGE OR PUSH TO `main` IS THE COMMIT LOOP, NOT PUBLICATION" — the same tier as
# an ordinary commit, needing `preflight.sh` and nothing else. CLAUDE.md §7: "merge early and often".
# A branch instruction says where work LANDS; it does not say the trunk goes unsynced. The session
# resolved that tension silently, in the wrong direction, and then escalated the merge as a decision
# for trimcrae — which CLAUDE.md §3 also forbids ("A GATE YOU COULD RESOLVE IS NEVER AN ESCALATION").
#
# ★★ WHY A `Stop` HOOK AND NOT A CHECKER. This repository has now watched two checkers fail at this
# exact class of problem: one printed a green tick over the failure, the other diagnosed it correctly
# and was never consulted, because the moment of stopping is precisely the moment nobody runs one
# more command. `ready-work-at-turn-end.sh` records that argument in full. The harness runs a Stop
# hook whether or not anyone remembers to; that is the entire reason this is one.
#
# ⚠ IT DOES NOT BLOCK. `stop_hook_active` makes it fire ONCE per stop, so it cannot trap a session or
# stop trimcrae reaching the agent. It makes the state unavoidable at the stopping moment. Nothing
# more is needed, and anything more would be a wall.
#
# ⛔ NO GREEN STATE THAT RECORDING CAN BUY. There is no flag, no marker file and no "I intend to merge
# later" — those are self-issued permission slips, the shape of the failure this replaces. The only
# ways past it are the real ones: be on `main`, have nothing ahead of it, or merge.
#
# =====================================================================================================
# ⭐⭐ 2026-09-01 — THE HOOK HAD TWO ALWAYS-GREEN PATHS, AND BOTH FIRED CONSTANTLY WHILE THE
# POPULATION IT GUARDS NEARLY DOUBLED. S31-ORPHANS found them; S35-DRIFTGUARD reproduced both against
# a controlled fixture and rewrote the file. The paragraph above claiming "no green state" was TRUE
# ABOUT RECORDING and FALSE ABOUT EVERYTHING ELSE: two ordinary states bought silence for free.
#
# ⛔ HOLE 1 — IT MEASURED `origin/main...HEAD`, SO IT COULD ONLY EVER SEE THE BRANCH THE STOPPING
# SESSION WAS SITTING ON. A branch pushed by a DIFFERENT session is not `HEAD` anywhere; once that
# session ends there is no stop left for it to fire on. The old file never ran `for-each-ref` and
# never ran `ls-remote` — `for-each-ref` appeared in its comments only. Reproduced in a throwaway
# fixture: with `origin/seat/s3-stranded` pushed and unmerged and the session moved off it, the hook
# printed ZERO mentions of that branch on any HEAD, and exited 0.
#
# ⛔ HOLE 2 — A DIRTY TREE SILENCED THE WHOLE FILE. `git status --porcelain` non-empty exited 0.
# Reproduced with a one-file control: same branch, same 1 unmerged commit, clean tree -> exit 2;
# add ONE untracked file -> exit 0. During a twelve-seat sprint the tree is never clean, so the
# hook was unconditionally off for exactly the window in which the most branches get created.
#
# ⛔ THE COST, MEASURED 2026-09-01: 37 branches on `origin` share this trunk's history and carry
# unmerged commits (152 distinct commits). The 2026-08-29 census said "20+". Seventeen of the 37 were
# pushed on 2026-08-28/29 by one archived seat cohort. Nothing in this repository enumerated `origin`
# at all — the 2026-08-29 number was produced by a human-driven one-off, never by an instrument.
#
# ★★ THE FIX IS TWO HALVES WITH DIFFERENT RULES, BECAUSE THEY ANSWER DIFFERENT QUESTIONS.
#   HALF A — "does THIS session owe a merge?"  `origin/main...HEAD`, as before, dirty-tree exit KEPT.
#   HALF B — "does ANY branch on origin owe a merge?"  `for-each-ref` over already-fetched remote
#            refs. Runs on every branch INCLUDING `main` and a detached HEAD, and is NOT gated on the
#            tree, because a dirty worktree is a fact about this session's uncommitted edits and
#            carries no information whatever about whether somebody else's pushed branch is on the
#            trunk. That asymmetry is the whole of hole 2.
#
# =====================================================================================================
# ⭐⭐ 2026-09-02 — A THIRD HALF, BECAUSE THE RULE GAINED A SECOND OBLIGATION.
# trimcrae: "use branches but have it pull from main whenever there's a change", and "rather than
# merging everything to main willy nilly". CLAUDE.md §7 now runs two lanes: coordination state
# (autonomy-state.json, receipts/, research-ledger.json, claims) goes STRAIGHT to `main` because each
# of those files is inert off the trunk — `claim.py`'s push to `main` IS the lock, `health.py` reads
# the checkout's receipts and a fired cycle checks out `main`, every cycle re-scores the ledger from
# the trunk — while WORK PRODUCT develops on a branch that pulls `main` in on every change.
#
#   HALF A2 — "has this branch pulled `main` in?"  The pull half. Same `origin/main...HEAD` counts
#             this hook already computes, read in the other direction (BEHIND rather than AHEAD).
#
# ⛔⛔ HALF A2 DOES NOT REPLACE HALF B AND MUST NEVER BE ALLOWED TO. They fail in opposite directions:
# a branch can pull `main` in every hour and still be abandoned, and pulling is precisely what makes
# an abandoned branch look healthy. HALF B is the check that costs something — it is the one that
# names 25 refs carrying 111 unmerged commits (live reading 2026-09-02 1:04 PM ET, 174 unmerged refs
# in total) — and dropping it is the only way this rule change does real harm.
#
# ⚠ WHY A2 IS GRADED RATHER THAN BINARY. Any branch is behind `main` within minutes, and a hook that
# printed a block for that at every stop is the wall this file's header refuses to become. So:
#   DIVERGENT (behind AND ahead) — the dangerous state, and the only one that gets a block. Commits
#     were written against a trunk that has since moved; that is the 2026-08-29 shape, where two
#     sessions fixed one bug in one hour because neither branch ever pulled the other's work in.
#   STALE (behind, nothing of its own) — one line. Nothing has been written against the stale trunk
#     yet, so this is a warning before the fact rather than a debt after it.
# ⭐ AND IT USES THE COUNTS ALREADY COMPUTED. No `merge-base`, no extra process: that formulation
# measured 20.0 s over 183 refs against a 15 s timeout and is pinned out by
# `test_the_classification_is_one_process_and_not_a_merge_base_loop`.
# =====================================================================================================
#
# ⭐ WHY HALF A KEEPS THE DIRTY EXIT, STATED SO IT CAN BE ARGUED WITH. Two reasons, both checked
# rather than assumed. (1) `~/.claude/stop-hook-git-check.sh` is wired at the launcher level and was
# run on this tree on 2026-09-01: it exits 2 on uncommitted changes TODAY, so that state is already
# alarmed and a second alarm for one state teaches the reader to skim both. (2) Mid-edit, HALF A's
# instruction — "MERGE IT, not next turn" — is genuinely the wrong advice, and a hook that gives
# wrong advice at every stop of a sprint is the wall this file's header refuses to become.
# ⛔ WHAT IS NOT TRADED AWAY: the suppressed count is still PRINTED, as one line inside HALF B's
# block. A dirty tree now defers the merge ADVICE; it no longer buys silence about the debt.
#
# ⭐ WHY `--contains=<root of main>` AND NOT A `merge-base` LOOP — THIS IS THE PART THAT HAD TO BE
# CHEAP, AND IT WAS MEASURED, NOT ASSUMED. A Stop hook cannot spend seconds per stop; this one has a
# 15 s timeout in `.claude/settings.json`.
#     naive: `for ref in $(for-each-ref --no-merged); do git merge-base origin/main $ref; done`
#            -> 183 candidate refs, 20.0 s. OVER THE TIMEOUT. It is slow for the exact reason it
#            looks cheap: proving NO common ancestor makes git walk both histories to the end.
#     this: one `git for-each-ref --no-merged=origin/main --contains=<root>` -> 0.28 s.
#     whole HALF B, five consecutive runs: 0.451 / 0.452 / 0.457 / 0.460 / 0.462 s.
# The two methods were compared as SETS, not as counts: both return the same 37 refs, `diff` empty.
# ⭐ And root-containment excludes the workflow data refs STRUCTURALLY rather than by name — all 13
# `*-cache` refs plus `email-outbox` and `figure-renders` are orphan refs sharing no root with the
# trunk, so they fall out of the query itself. A name-glob exclusion list would have been one more
# thing to keep in sync, and one more place to quietly widen.
#
# ⚠ NO FETCH, STILL — BUT THE STALENESS IS NOW REPORTED RATHER THAN REASONED AWAY. The old comment
# argued a stale remote ref "cannot produce a false silence". That is true of HALF A (its AHEAD is
# exact) and FALSE of HALF B, which compares other people's refs against a last-known `origin/main`:
# a branch merged since the last fetch reads as stranded, and a branch pushed since the last fetch is
# invisible. Measured 2026-09-01: `git ls-remote` put origin/main at 105df270 while this clone's
# remote-tracking ref sat at 1d01f079, EIGHT MINUTES after the last fetch. So HALF B prints the age of
# the last fetch and calls its own number a reading, not a truth. Fetching from a Stop hook would put
# a network round trip in the stopping path, which is what the original comment correctly refused.
#
# ⚠ AND IN A SHALLOW CLONE THE CENSUS UNDER-REPORTS. This checkout is shallow (`is-shallow-repository`
# = true), grafted at 2026-08-04. `--max-parents=0` therefore returns the GRAFT boundary, not the true
# root, so HALF B really asks "does this ref contain main's earliest LOCALLY KNOWN commit?" — and a
# branch that forked below the graft is invisible to THIS query. Those refs are UNMEASURED BY HALF B,
# not merged, and calling them "pre-rewrite history" is a claim this clone cannot support. The error
# direction is FALSE SILENCE, so the printed count is a LOWER BOUND and says so. Every branch HALF B
# names has a tip well above the graft, so the reading is sound for each one it reports.
#
# ⛔⛔ SUPERSEDED, RETAINED (2026-09-02): this comment used to end "a branch forked below the graft
# CANNOT BE CLASSIFIED AT ALL", and the printed warning told the reader the same thing. That was
# false, and it was the expensive kind of false — it told a reader not to look at 147 refs.
# ★ ANCESTRY IS DEAD FOR THEM; CONTENT IS NOT. A TREE DIFF NEEDS NO MERGE-BASE. `git cat-file -e
# <ref>:<path>` and `git diff <ref> -- <path>` answer "does main have this content" with no common
# ancestor whatsoever, and pre-graft refs share merge-bases with EACH OTHER, so fork points are
# recoverable even where they are unrecoverable against main. A census on that method reached
# UNMEASURED = 0 across all 185 unmerged refs: research/autonomy/sprint-2026-09-01/S38-BRANCH-CENSUS.md.
# ⛔ AND WHAT IT FOUND IS WHY THE SILENCE MATTERED: 40 refs carry live work, among them 39 files of a
# body of work STRATEGY.md still calls a "backup route", and 138 files exist on some branch and on no
# other. It also found 15 refs that are LIVE CI INFRASTRUCTURE rather than debt — main's own
# workflows write to them — so a future tightening here must not treat every unmerged ref as a defect.
# ⚠ HALF B STILL REPORTS ITS OWN 38 AND NOT THE 185. The ancestry reading is the stronger one where
# it applies, and collapsing the two would lose that. The dropped count is now printed BESIDE it.
# =====================================================================================================

set -uo pipefail

input=$(cat 2>/dev/null || echo '{}')

# ⛔ RECURSION GUARD. Without it the hook re-fires on the stop it just caused and the session cannot
# end at all. Copied from the two hooks that already work.
if command -v jq >/dev/null 2>&1; then
  if [[ "$(echo "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" == "true" ]]; then
    exit 0
  fi
fi

# REPO discovery, copied from `escalation-debt-at-turn-end.sh`: CLAUDE_PROJECT_DIR when the harness
# sets it, otherwise the repo this hook file physically lives in. A hook that silently measures the
# wrong tree is worse than one that measures nothing.
_hook_dir=$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd) || _hook_dir=""
REPO=""
for cand in "${CLAUDE_PROJECT_DIR:-}" "${_hook_dir%/.claude/hooks}"; do
  [ -n "$cand" ] || continue
  if git -C "$cand" rev-parse --git-dir >/dev/null 2>&1; then REPO="$cand"; break; fi
done
[ -n "$REPO" ] || exit 0
cd "$REPO" 2>/dev/null || exit 0

HAVE_ORIGIN_REFS=$(git for-each-ref --count=1 --format=x refs/remotes/origin 2>/dev/null)

# ⛔ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). If this is a clone of something —
# it has remote-tracking refs — but `origin/main` will not resolve, the honest report is UNMEASURED,
# and UNMEASURED is not a reason to go quiet. A repo with no origin at all is not this repository and
# is left alone.
if ! git rev-parse --verify -q origin/main >/dev/null 2>&1; then
  if [ -n "$HAVE_ORIGIN_REFS" ]; then
    {
      echo "⛔ merge-debt: \`origin/main\` does not resolve in this checkout, so NOTHING was measured."
      echo "   That is UNMEASURED, not clean. Neither your own merge debt nor the branch census ran."
      echo "   Fix the remote (\`git remote -v\`, \`git fetch origin main\`) and stop again."
    } >&2
    exit 2
  fi
  exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# HALF A — the merge debt of THIS session's own branch.
# ─────────────────────────────────────────────────────────────────────────────────────────────────
A_AHEAD=0; A_BEHIND=0; A_BRANCH=""; A_DIRTY=0
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ] && [ "$BRANCH" != "main" ]; then
  # ⚠ `--left-right --count A...B` prints LEFT then RIGHT: left = on origin/main only (BEHIND),
  # right = on HEAD only (AHEAD). Getting this pair backwards inverts the hook, so it is spelled out.
  read -r A_BEHIND A_AHEAD < <(git rev-list --left-right --count origin/main...HEAD 2>/dev/null | tr '\t' ' ')
  A_BEHIND=${A_BEHIND:-0}; A_AHEAD=${A_AHEAD:-0}
  A_BRANCH="$BRANCH"
  [ -n "$(git status --porcelain 2>/dev/null)" ] && A_DIRTY=1
fi

# HALF A2 — graded from the counts HALF A already has. DIVERGENT is the state that costs something.
A_DIVERGENT=0; A_STALE=0
if [ "$A_BEHIND" -gt 0 ]; then
  if [ "$A_AHEAD" -gt 0 ]; then A_DIVERGENT=1; else A_STALE=1; fi
fi

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# HALF B — every branch on `origin` that carries unmerged commits, whoever pushed it and whenever.
# Not gated on HEAD. Not gated on the worktree. One `for-each-ref`, no network.
# ─────────────────────────────────────────────────────────────────────────────────────────────────
B_REFS=""; B_N=0; B_COMMITS=0
ROOT=$(git rev-list --max-parents=0 origin/main 2>/dev/null | tail -1)
# ⛔ COUNT WHAT THIS QUERY THROWS AWAY. Every unmerged ref, minus the ones HALF B can reach by
# ancestry, is the set the hook used to drop in silence. Printing it is the whole 2026-09-02 fix:
# a number a reader can act on, instead of a sentence saying the refs were beyond reach.
B_ALL=$(git for-each-ref --no-merged=origin/main --format='x' refs/remotes/origin 2>/dev/null | grep -c . || echo 0)
B_DROPPED=0
if [ -n "$ROOT" ]; then
  B_REFS=$(git for-each-ref --no-merged=origin/main --contains="$ROOT" \
             --sort=-committerdate --format='%(refname:short)' refs/remotes/origin 2>/dev/null)
  if [ -n "$B_REFS" ]; then
    B_N=$(printf '%s\n' "$B_REFS" | grep -c .)
    B_DROPPED=$(( B_ALL - B_N ))
    # shellcheck disable=SC2086 — deliberate word splitting: these are ref names, one per line.
    B_COMMITS=$(git rev-list --count $B_REFS --not origin/main 2>/dev/null || echo 0)
  fi
fi

# Nothing to say only when BOTH halves are quiet — and HALF A is quiet on a dirty tree by the trade
# argued in the header.
# ⛔ A2 IS NOT SILENCED BY A DIRTY TREE. HALF A's dirty-tree exit defers an instruction that would be
# wrong mid-edit ("merge it, not next turn"); "you are working against a stale trunk" is not wrong
# mid-edit — it is most useful exactly then, because every further edit compounds it. What the dirty
# tree defers is the `git merge origin/main` INSTRUCTION, not the reading.
if [ "$B_N" -eq 0 ] && [ "$A_DIVERGENT" -eq 0 ] && [ "$A_STALE" -eq 0 ] \
   && { [ "$A_AHEAD" -eq 0 ] || [ "$A_DIRTY" -eq 1 ]; }; then
  exit 0
fi

FETCH_AGE="unknown"
# ⚠ FETCH_HEAD LIVES IN THE COMMON GIT DIR, AND `.git` IS A FILE IN A LINKED WORKTREE. Same class of
# defect as the one fixed in promised-work-at-turn-end.sh on 2026-09-02, and same silent shape: the
# `-f` test simply fails, so the age reads "unknown" forever rather than wrongly — a degraded reading
# that looks exactly like a repository nobody has fetched in. `--git-common-dir` is the right scope
# here, unlike the per-worktree state file: a fetch updates the shared FETCH_HEAD for every worktree.
_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || _COMMON=".git"
[ -n "$_COMMON" ] || _COMMON=".git"
if [ -f "${_COMMON}/FETCH_HEAD" ]; then
  _m=$(date -u -r "${_COMMON}/FETCH_HEAD" +%s 2>/dev/null || echo "")
  if [ -n "$_m" ]; then
    _d=$(( $(date -u +%s) - _m ))
    if [ "$_d" -lt 3600 ]; then FETCH_AGE="$((_d / 60)) min ago"; else FETCH_AGE="$((_d / 3600)) h ago"; fi
  fi
fi

{
  # ── HALF A2 — the PULL half (CLAUDE.md §7 lane 2) ──────────────────────────────────────────────
  if [ "$A_DIVERGENT" -eq 1 ]; then
    echo "⛔ '$A_BRANCH' has NOT pulled main in: $A_AHEAD commit(s) of its own written against a trunk"
    echo "   that has since moved $A_BEHIND commit(s). That is DIVERGENT, not merely behind."
    echo
    echo "★ CLAUDE.md §7: a work branch \"pulls main in on EVERY change\" — not once at the start and not"
    echo "   before the final push. A branch that has not pulled is reasoning from a trunk that no longer"
    echo "   exists, and on 2026-08-29 that produced two sessions diagnosing and fixing the SAME bug"
    echo "   within one hour, neither able to see the other."
    if [ "$A_DIRTY" -eq 0 ]; then
      echo "   ⭑ DO IT NOW: \`git fetch origin main && git merge origin/main\`, then re-run preflight."
    else
      echo "   ⚠ The worktree is dirty, so the merge INSTRUCTION is deferred to the next clean stop."
      echo "     ⛔ The divergence is not deferred: it is printed here every stop, and every further edit"
      echo "     is one more thing written against the stale trunk."
    fi
    echo
  elif [ "$A_STALE" -eq 1 ]; then
    echo "⚠ '$A_BRANCH' is $A_BEHIND commit(s) behind main and carries nothing of its own yet. Pull before"
    echo "   you commit (\`git merge origin/main\`) — CLAUDE.md §7 lane 2. Refs as last fetched."
    echo
  fi

  # ── HALF A ─────────────────────────────────────────────────────────────────────────────────────
  if [ "$A_AHEAD" -gt 0 ] && [ "$A_DIRTY" -eq 0 ]; then
    echo "⛔ $A_AHEAD commit(s) on '$A_BRANCH' are NOT on main. Committed, clean, and off the trunk."
    echo
    git log --oneline --no-decorate origin/main..HEAD 2>/dev/null | head -8 | sed 's/^/   /'
    [ "$A_AHEAD" -gt 8 ] && echo "   … and $((A_AHEAD - 8)) more"
    echo
    # ⚠ The behind-count is HALF A2's, above — one fact, one place (CLAUDE.md rule 1). It used to be
    # restated here as an aside, which is how it stayed advice instead of becoming a check.
    echo "⛔⛔ MERGING TO main NEEDS NO PERMISSION, AND READING A BRANCH INSTRUCTION AS IF IT DID IS"
    echo "   THE MISTAKE THIS HOOK EXISTS FOR. CLAUDE.md §6: \"A MERGE OR PUSH TO \`main\` IS THE COMMIT"
    echo "   LOOP, NOT PUBLICATION\" — ordinary work, gated by ./scripts/preflight.sh and nothing else."
    echo "   An instruction to develop on a named branch says where work LANDS. It does not say the"
    echo "   trunk goes unsynced, and it is not a reason to ask (CLAUDE.md §3: a gate you could resolve"
    echo "   is never an escalation)."
    echo
    echo "★ ONE OF THESE IS TRUE, AND THE REPLY SHOULD SAY WHICH:"
    echo "   1. It is ready. Then MERGE IT — preflight, merge to main, push. Not next turn."
    echo "   2. It is genuinely not ready — a half-finished change a merge would ship broken. Then say"
    echo "      WHAT is unfinished. ⛔ THE BAR IS GREEN AND COHERENT, NOT FINISHED (CLAUDE.md §7): a work"
    echo "      branch merges as soon as preflight passes and the tree makes sense to a reader."
    echo "      \"I'll merge when the feature is done\" is the reasoning that stranded the branch"
    echo "      population — it is not a plan, it is a deferral with no trigger."
    echo "   3. Somebody outside this session must decide — and that is rare enough that it needs a"
    echo "      reason, not a habit."
    echo
  elif [ "$A_AHEAD" -gt 0 ] && [ "$A_DIRTY" -eq 1 ]; then
    echo "⚠ This checkout ('$A_BRANCH') also has $A_AHEAD commit(s) off the trunk. The worktree is dirty,"
    echo "   so the merge instruction is deferred to the next clean stop — \`~/.claude/stop-hook-git-check.sh\`"
    echo "   already owns the uncommitted-changes alarm, and stacking two warnings on one state teaches"
    echo "   skimming. ⛔ The DEBT is not deferred, only the advice: it is printed here every stop."
    echo
  fi

  # ── HALF B ─────────────────────────────────────────────────────────────────────────────────────
  if [ "$B_N" -gt 0 ]; then
    echo "⛔ $B_N branch(es) on origin carry $B_COMMITS unmerged commit(s): finished work nothing will merge."
    echo "   §7 calls this a DATA-LOSS BUG, and it is check (b): PULLING main IN DOES NOT FIX IT."
    echo "   These share this trunk's history and are not ancestors of the last-known origin/main."
    echo "   Newest first (refs as last fetched, $FETCH_AGE — no fetch is run from a Stop hook):"
    echo
    printf '%s\n' "$B_REFS" | head -12 | while read -r _r; do
      [ -n "$_r" ] || continue
      _c=$(git rev-list --count "origin/main..$_r" 2>/dev/null || echo '?')
      _d=$(git log -1 --format=%cs "$_r" 2>/dev/null || echo '????-??-??')
      # ⚠ This checkout's own upstream branch is NOT excluded — it is a branch on origin carrying
      # unmerged commits and that is simply true. It is MARKED instead, so a reader does not mistake
      # HALF A's subject for somebody else's stranded work. Excluding it would be the first of the
      # convenience exclusions that turn a census into a filter.
      if [ -n "$A_BRANCH" ] && [ "$_r" = "origin/$A_BRANCH" ]; then
        printf '   %-4s %s  %s   ← this checkout (HALF A above)\n' "$_c" "$_d" "$_r"
      else
        printf '   %-4s %s  %s\n' "$_c" "$_d" "$_r"
      fi
    done
    [ "$B_N" -gt 12 ] && echo "   … and $((B_N - 12)) more"
    echo
    echo "★ THIS IS NOT YOUR BRANCH AND THAT IS THE POINT. The old hook measured origin/main...HEAD, so"
    echo "   it could only see the branch the stopping session sat on — and a branch pushed by a session"
    echo "   that has ENDED is exactly the case it could not represent. Four seat branches sat unmerged"
    echo "   for four days under a green hook; the census then found 37, not four."
    echo
    echo "★ WHAT TO DO, AND NONE OF IT IS 'note it and move on':"
    echo "   1. Read one. \`git log --oneline origin/main..<ref>\` and \`git diff origin/main...<ref>\` are"
    echo "      free, local and already fetched. Most of these are one commit."
    echo "   2. Worth keeping -> merge it (preflight, merge, push). That is the commit loop, not"
    echo "      publication, and it needs nobody's permission."
    echo "   3. Superseded or empty -> say so IN WRITING with the reading that shows it, and the branch"
    echo "      can be deleted. A branch nobody has read is not 'probably nothing'."
    echo "   4. Cannot be judged from here -> record it on the owning ledger row's \`_stranded_work\`"
    echo "      with the branch name AND its tip sha. That field is the only thing in this repository"
    echo "      that has ever actually recovered a stranded branch (S31: AUT-PD-130 -> seat/s1)."
    echo "      ⛔ It does NOT silence this hook. Only merging or deleting the branch does."
    echo
    echo "⚠ THE NUMBER IS A LOWER BOUND, TWICE OVER, AND NEITHER IS FIXABLE FROM A STOP HOOK:"
    echo "   • refs are as of the last fetch ($FETCH_AGE); anything pushed since is invisible here."
    if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
      echo "   • this clone is SHALLOW and grafted, so ${B_DROPPED:-?} further ref(s) do not contain"
      echo "     main's earliest known commit and are invisible to THIS query — counted as neither"
      echo "     merged nor stranded. UNMEASURED BY ANCESTRY, not clean, and NOT unclassifiable:"
      echo "     a tree diff needs no common ancestor. All of them were read on 2026-09-02 —"
      echo "     research/autonomy/sprint-2026-09-01/S38-BRANCH-CENSUS.md (UNMEASURED = 0 of 185)."
    fi
    echo
  fi
  echo "⚠ Fires once per stop. It will not ask twice — answer it now."
} >&2

exit 2
