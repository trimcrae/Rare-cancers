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

set -uo pipefail

input=$(cat 2>/dev/null || echo '{}')

# ⛔ RECURSION GUARD. Without it the hook re-fires on the stop it just caused and the session cannot
# end at all. Copied from the two hooks that already work.
if command -v jq >/dev/null 2>&1; then
  if [[ "$(echo "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" == "true" ]]; then
    exit 0
  fi
fi

REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"
cd "$REPO" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

BRANCH=$(git branch --show-current 2>/dev/null)
[ -z "$BRANCH" ] && exit 0
[ "$BRANCH" = "main" ] && exit 0

# ⚠ NO FETCH. A Stop hook must be fast and must never fail the turn on a network hiccup, so this
# reads the last-known `origin/main`. That makes BEHIND a lower bound and AHEAD exact — and AHEAD is
# what this hook is about, so reading a stale remote ref cannot produce a false silence.
git rev-parse --verify -q origin/main >/dev/null 2>&1 || exit 0
read -r BEHIND AHEAD < <(git rev-list --left-right --count origin/main...HEAD 2>/dev/null | tr '\t' ' ')
[ "${AHEAD:-0}" -eq 0 ] && exit 0

# ⛔ A DIRTY TREE IS SOMEBODY ELSE'S ALARM. `stop-hook-git-check.sh` already fires on uncommitted
# changes; firing here too would stack two warnings for one state and teach the reader to skim both.
# This hook is about COMMITTED work that is not on the trunk.
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  exit 0
fi

{
  echo "⛔ $AHEAD commit(s) on '$BRANCH' are NOT on main. Committed, clean, and off the trunk."
  echo
  git log --oneline --no-decorate origin/main..HEAD 2>/dev/null | head -8 | sed 's/^/   /'
  [ "$AHEAD" -gt 8 ] && echo "   … and $((AHEAD - 8)) more"
  echo
  if [ "${BEHIND:-0}" -gt 0 ]; then
    echo "⚠ '$BRANCH' is also $BEHIND commit(s) BEHIND main (last-known ref; fetch for the true count)."
    echo "   Merging main IN first is the same rule — CLAUDE.md §7, 'merge early and often'."
    echo
  fi
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
  echo "      WHAT is unfinished. \"I'll merge when the feature is done\" is not that; this repository"
  echo "      merges early and often precisely so that 'done' is never the first merge."
  echo "   3. Somebody outside this session must decide — and that is rare enough that it needs a"
  echo "      reason, not a habit."
  echo
  echo "⚠ WHY THIS IS NOT PEDANTRY. Measured 2026-08-29: 20+ branches on origin carry unmerged"
  echo "   commits, most a month stale, and one bug got diagnosed twice in one hour by two sessions"
  echo "   that could not see each other. §7 calls branch drift a DATA-LOSS BUG for that reason."
  echo
  echo "⚠ Fires once per stop. It will not ask twice — answer it now."
} >&2

exit 2
