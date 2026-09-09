#!/usr/bin/env bash
# REAL cumulative apply of MORTALITY-3's section 4.2 diff and this lane's section 6 diff, in both
# orders, on a scratch copy OUTSIDE the repository. `git apply --check` tests each patch against the
# tree independently, so it cannot show that two patches coexist; this does.
# Nothing in /home/user/Rare-cancers is written.
set -u
REPO=/home/user/Rare-cancers
LANE="$REPO/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08"
D3="$LANE/MORTALITY-3/section-4.2-composition-effect.diff"
D6="$LANE/MORTALITY-4/section-6-conclusion-scope.diff"
SCRATCH="${SCRATCH_BASE:?}/cumulative-apply"
rc_all=0
for order in "3-then-6" "6-then-3"; do
  rm -rf "$SCRATCH"; mkdir -p "$SCRATCH/research/manuscripts"
  cp "$REPO/research/manuscripts/emc-mortality-mechanisms-paper.md" "$SCRATCH/research/manuscripts/"
  git -C "$SCRATCH" init -q
  echo "=== order $order ==="
  if [ "$order" = "3-then-6" ]; then set -- "$D3" "$D6"; else set -- "$D6" "$D3"; fi
  for p in "$@"; do
    git -C "$SCRATCH" apply -v "$p"
    rc=$?
    echo "apply $(basename "$p") -> exit $rc"
    [ "$rc" -ne 0 ] && rc_all=1
  done
  echo "--- resulting section 4.2 tail and section 6 ---"
  sed -n '/^For ultra-rare cancers generally/,+3p;/^Whether that record is distinctive/,+40p' "$SCRATCH/research/manuscripts/emc-mortality-mechanisms-paper.md" | head -50
  echo "--- section 6 as it ends up ---"
  sed -n '/^## 6\. Conclusion/,/^## Appendix A/p' "$SCRATCH/research/manuscripts/emc-mortality-mechanisms-paper.md"
  if grep -q "For ultra-rare cancers generally" "$SCRATCH/research/manuscripts/emc-mortality-mechanisms-paper.md"; then
    echo "RESIDUAL GENERALISATION STILL PRESENT"; rc_all=1
  else
    echo "OK: no residual 'For ultra-rare cancers generally'"
  fi
done
rm -rf "$SCRATCH"
exit $rc_all
